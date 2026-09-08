// Q05 native contention test.
//
// This executable links the production InterpreterImage allocator and the
// production il2cpp::vm::g_MetadataLock.  A std::atomic start gate is used
// only to align worker entry; allocator state is synchronized exclusively by
// FastAutoLock around AllocImageIndex and by ReserveImageBudget itself.

#include "hybridclr/metadata/InterpreterImage.h"
#include "vm/MetadataLock.h"
#include "os/Mutex.h"

#include <atomic>
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_set>
#include <vector>

namespace
{
using Budget = hybridclr::metadata::InterpreterImageBudget;
using Image = hybridclr::metadata::InterpreterImage;
using Allocation = Budget::Allocation;
using Evaluation = Budget::Evaluation;
using State = Budget::State;

size_t checks = 0;

void Check(bool condition, const char* detail)
{
    ++checks;
    if (!condition)
        throw std::runtime_error(detail);
}

struct Snapshot
{
    State state;
    uint64_t ordinary;
    uint64_t shadow;
    uint64_t reserved;
};

Snapshot GetSnapshot()
{
    Snapshot snapshot = {};
    snapshot.state = Image::GetImageBudgetState(snapshot.ordinary, snapshot.shadow,
                                                snapshot.reserved);
    return snapshot;
}

void CheckFresh(const Snapshot& snapshot)
{
    const State fresh = Budget::FreshState();
    for (int index = 0; index < 4; ++index)
        Check(snapshot.state.cursors[index] == fresh.cursors[index],
              "process did not start with a fresh allocator state");
    Check(snapshot.ordinary == 0 && snapshot.shadow == 0 && snapshot.reserved == 0,
          "process did not start with zero allocation counters");
}

uint32_t AllocateOrdinary(uint64_t size)
{
    // AllocImageIndex is intentionally a lock-held primitive.  This is the
    // production metadata lock, not a test mutex or a helper-local lock.
    il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
    return Image::AllocImageIndex(size, false);
}

void CheckIndicesUnique(const std::vector<uint32_t>& indices)
{
    std::unordered_set<uint32_t> unique;
    for (uint32_t index : indices)
    {
        Check(index != Budget::kInvalidImageIndex, "successful allocation returned index zero");
        Check(unique.insert(index).second, "committed image indices are not unique");
    }
}

void CheckExpectedFirst(const Evaluation& reservation,
                        const std::vector<uint32_t>& expected)
{
    Check(reservation.IsSuccess(), "serial reservation unexpectedly failed");
    Check(reservation.allocations.size() == expected.size(),
          "reservation allocation count differs");
    for (size_t index = 0; index < expected.size(); ++index)
    {
        Check(reservation.allocations[index].IsSuccess(),
              "reservation contains an unsuccessful allocation");
        Check(reservation.allocations[index].imageIndex == expected[index],
              "reservation first indices differ from the production encoding");
    }
}

void RunSerialReserveFirst()
{
    CheckFresh(GetSnapshot());
    const std::vector<uint64_t> sizes = {1000, 2 * 1024 * 1024, 10 * 1024 * 1024};
    const Evaluation reservation = Image::ReserveImageBudget(sizes);
    CheckExpectedFirst(reservation, {768u, 512u, 256u});

    std::vector<uint32_t> committed;
    for (uint64_t size : sizes)
        committed.push_back(AllocateOrdinary(size));
    CheckIndicesUnique({reservation.allocations[0].imageIndex,
                        reservation.allocations[1].imageIndex,
                        reservation.allocations[2].imageIndex,
                        committed[0], committed[1], committed[2]});
    Check(committed[0] == 769u && committed[1] == 516u && committed[2] == 272u,
          "ordinary allocations did not follow the reserved cursors");

    const Snapshot after = GetSnapshot();
    Check(after.ordinary == 3 && after.shadow == 0 && after.reserved == 3,
          "serial reserve-first counters differ");
    std::cout << "q05_serial_reserve_first=pass lock=production-g_MetadataLock\n";
}

void RunSerialOrdinaryFirst()
{
    CheckFresh(GetSnapshot());
    const std::vector<uint64_t> sizes = {1000, 2 * 1024 * 1024, 10 * 1024 * 1024};
    std::vector<uint32_t> ordinary;
    for (uint64_t size : sizes)
        ordinary.push_back(AllocateOrdinary(size));
    Check(ordinary[0] == 768u && ordinary[1] == 512u && ordinary[2] == 256u,
          "ordinary first indices differ from the production encoding");

    const Evaluation reservation = Image::ReserveImageBudget(sizes);
    CheckExpectedFirst(reservation, {769u, 516u, 272u});
    CheckIndicesUnique({ordinary[0], ordinary[1], ordinary[2],
                        reservation.allocations[0].imageIndex,
                        reservation.allocations[1].imageIndex,
                        reservation.allocations[2].imageIndex});

    const Snapshot after = GetSnapshot();
    Check(after.ordinary == 3 && after.shadow == 0 && after.reserved == 3,
          "serial ordinary-first counters differ");
    std::cout << "q05_serial_ordinary_first=pass lock=production-g_MetadataLock\n";
}

struct StartGate
{
    const size_t expected;
    std::atomic<size_t> arrived;
    std::atomic<bool> open;
    explicit StartGate(size_t workerCount) : expected(workerCount), arrived(0), open(false) {}

    void Wait()
    {
        arrived.fetch_add(1, std::memory_order_release);
        while (!open.load(std::memory_order_acquire))
            std::this_thread::yield();
    }

    void ReleaseAfterAllArrive()
    {
        while (arrived.load(std::memory_order_acquire) != expected)
            std::this_thread::yield();
        open.store(true, std::memory_order_release);
    }
};

struct OrdinaryResult
{
    uint32_t imageIndex;
    uint64_t size;
};

struct ReservationResult
{
    Evaluation evaluation;
};

struct ObservedAllocation
{
    uint32_t imageIndex;
    int32_t kind;
    uint32_t cursor;
    bool succeeded;
};

struct ObservedOperation
{
    std::vector<uint64_t> requestedSizes;
    std::vector<ObservedAllocation> allocations;
    bool succeeded;
};

ObservedAllocation ObserveIndex(uint32_t imageIndex)
{
    const uint32_t kindBitsMask = Budget::kMetadataKindCount - 1u;
    const int32_t kind = static_cast<int32_t>((imageIndex >>
        Budget::kMetadataImageIndexKindShift) & kindBitsMask);
    const uint32_t cursor = imageIndex & (Budget::kMaxMetadataImageIndexWithoutKind - 1u);
    return {imageIndex, kind, cursor, imageIndex != Budget::kInvalidImageIndex};
}

ObservedAllocation ObserveAllocation(const Allocation& allocation)
{
    return {allocation.imageIndex, allocation.kind,
            allocation.imageIndex == Budget::kInvalidImageIndex ? 0u
                : ObserveIndex(allocation.imageIndex).cursor,
            allocation.IsSuccess()};
}

bool HasCycle(const std::vector<std::vector<size_t> >& edges, size_t node,
             std::vector<uint8_t>& colors)
{
    if (colors[node] == 1)
        return true;
    if (colors[node] == 2)
        return false;
    colors[node] = 1;
    for (size_t next : edges[node])
    {
        if (HasCycle(edges, next, colors))
            return true;
    }
    colors[node] = 2;
    return false;
}

// Each operation is one node, including a multi-image reservation.  Cursor
// order in each bucket contributes a directed edge between whole operations;
// a crossed pair therefore forms a cycle instead of being mistaken for a
// valid result merely because every index and aggregate count is unique.
bool IsSerializable(const std::vector<ObservedOperation>& operations)
{
    std::vector<std::vector<size_t> > edges(operations.size());
    for (const ObservedOperation& operation : operations)
    {
        if (!operation.succeeded || operation.requestedSizes.size() != operation.allocations.size())
            return false;
        for (size_t index = 0; index < operation.allocations.size(); ++index)
        {
            const ObservedAllocation& allocation = operation.allocations[index];
            if (!allocation.succeeded || Budget::GetImageKind(operation.requestedSizes[index]) != allocation.kind)
                return false;
        }
        for (int kind = 0; kind < 4; ++kind)
        {
            std::vector<uint32_t> cursors;
            for (const ObservedAllocation& allocation : operation.allocations)
            {
                if (allocation.kind == kind)
                    cursors.push_back(allocation.cursor);
            }
            std::sort(cursors.begin(), cursors.end());
            for (size_t index = 1; index < cursors.size(); ++index)
            {
                if (cursors[index] != cursors[index - 1] + Budget::CursorStride(kind))
                    return false;
            }
        }
    }
    for (size_t left = 0; left < operations.size(); ++left)
    {
        for (size_t right = left + 1; right < operations.size(); ++right)
        {
            for (int kind = 0; kind < 4; ++kind)
            {
                bool hasLeft = false;
                bool hasRight = false;
                uint32_t leftMin = 0;
                uint32_t leftMax = 0;
                uint32_t rightMin = 0;
                uint32_t rightMax = 0;
                for (const ObservedAllocation& allocation : operations[left].allocations)
                {
                    if (allocation.kind == kind)
                    {
                        if (!hasLeft) leftMin = allocation.cursor;
                        leftMax = allocation.cursor;
                        hasLeft = true;
                    }
                }
                for (const ObservedAllocation& allocation : operations[right].allocations)
                {
                    if (allocation.kind == kind)
                    {
                        if (!hasRight) rightMin = allocation.cursor;
                        rightMax = allocation.cursor;
                        hasRight = true;
                    }
                }
                if (!hasLeft || !hasRight)
                    continue;
                if (!(leftMax < rightMin || rightMax < leftMin))
                    return false;
                if (leftMax < rightMin)
                    edges[left].push_back(right);
                else
                    edges[right].push_back(left);
            }
        }
    }
    std::vector<uint8_t> colors(operations.size(), 0);
    for (size_t index = 0; index < operations.size(); ++index)
    {
        if (HasCycle(edges, index, colors))
            return false;
    }
    return true;
}

void CheckOracleRegression()
{
    const ObservedOperation crossedLeft = {
        {1000, 2 * 1024 * 1024},
        {{768u, 3, 0u, true}, {516u, 2, 4u, true}}, true};
    const ObservedOperation crossedRight = {
        {1000, 2 * 1024 * 1024},
        {{769u, 3, 1u, true}, {512u, 2, 0u, true}}, true};
    Check(!IsSerializable({crossedLeft, crossedRight}),
          "serializability oracle accepted a crossed atomic-batch order");
}

void RunContentionAccept()
{
    CheckFresh(GetSnapshot());
    const size_t ordinaryCount = 24;
    const size_t reservationCount = 24;
    StartGate gate(ordinaryCount + reservationCount);
    std::vector<OrdinaryResult> ordinary(ordinaryCount);
    std::vector<ReservationResult> reservations(reservationCount);
    std::vector<std::thread> workers;
    workers.reserve(ordinaryCount + reservationCount);

    for (size_t index = 0; index < ordinaryCount; ++index)
    {
        workers.emplace_back([&, index]() {
            gate.Wait();
            const uint64_t size = (index % 3 == 0) ? 1000
                : ((index % 3 == 1) ? 2 * 1024 * 1024 : 10 * 1024 * 1024);
            ordinary[index] = {AllocateOrdinary(size), size};
        });
    }
    for (size_t index = 0; index < reservationCount; ++index)
    {
        workers.emplace_back([&, index]() {
            gate.Wait();
            reservations[index].evaluation = Image::ReserveImageBudget(
                std::vector<uint64_t>{1000, 2 * 1024 * 1024});
        });
    }
    gate.ReleaseAfterAllArrive();
    for (std::thread& worker : workers)
        worker.join();

    std::vector<uint32_t> committed;
    for (const OrdinaryResult& result : ordinary)
        committed.push_back(result.imageIndex);
    for (const ReservationResult& result : reservations)
    {
        Check(result.evaluation.IsSuccess(), "contention acceptance rejected a fitting batch");
        Check(result.evaluation.allocations.size() == 2,
              "contention acceptance partially committed a fitting batch");
        committed.push_back(result.evaluation.allocations[0].imageIndex);
        committed.push_back(result.evaluation.allocations[1].imageIndex);
    }
    CheckIndicesUnique(committed);
    std::vector<ObservedOperation> observations;
    observations.reserve(ordinaryCount + reservationCount);
    for (const OrdinaryResult& result : ordinary)
    {
        observations.push_back({{result.size}, {ObserveIndex(result.imageIndex)}, true});
    }
    for (const ReservationResult& result : reservations)
    {
        ObservedOperation operation = {{1000, 2 * 1024 * 1024}, {}, result.evaluation.IsSuccess()};
        for (const Allocation& allocation : result.evaluation.allocations)
            operation.allocations.push_back(ObserveAllocation(allocation));
        observations.push_back(operation);
    }
    CheckOracleRegression();
    Check(IsSerializable(observations),
          "contention observations are not serializable as atomic operations");

    uint32_t byKind[4] = {};
    for (const OrdinaryResult& result : ordinary)
        ++byKind[Budget::GetImageKind(result.size)];
    for (size_t index = 0; index < reservations.size(); ++index)
    {
        ++byKind[Budget::GetImageKind(1000)];
        ++byKind[Budget::GetImageKind(2 * 1024 * 1024)];
    }
    const State fresh = Budget::FreshState();
    const Snapshot after = GetSnapshot();
    for (int kind = 0; kind < 4; ++kind)
        Check(after.state.cursors[kind] == fresh.cursors[kind] +
              byKind[kind] * Budget::CursorStride(kind),
              "contention acceptance cursor is not serializable");
    Check(after.ordinary == ordinaryCount && after.reserved == reservationCount * 2,
          "contention acceptance counters differ");
    std::cout << "q05_contention_accept=pass workers=48 lock=production-g_MetadataLock oracle=partial-order-atomic-batches\n";
}

void RunContentionReject()
{
    CheckFresh(GetSnapshot());
    // Leave exactly one kind-3 slot while filling every fallback bucket.  A
    // rejected two-image batch will therefore produce one dry-run prefix
    // allocation but cannot commit any cursor globally.
    std::vector<uint64_t> fill;
    fill.insert(fill.end(), 254, 1000);
    fill.insert(fill.end(), 64, 2 * 1024 * 1024);
    fill.insert(fill.end(), 16, 10 * 1024 * 1024);
    fill.insert(fill.end(), 3, 50 * 1024 * 1024);
    const Evaluation filled = Image::ReserveImageBudget(fill);
    Check(filled.IsSuccess() && filled.allocations.size() == 337,
          "contention rejection prefill did not exhaust every fallback bucket");
    const Snapshot before = GetSnapshot();
    Check(before.state.cursors[3] == 254u && before.state.cursors[2] == 256u &&
          before.state.cursors[1] == 256u && before.state.cursors[0] == 256u,
          "contention rejection prefill cursors differ");

    const size_t workerCount = 128;
    StartGate gate(workerCount + 1);
    std::vector<ReservationResult> reservations(workerCount);
    OrdinaryResult ordinary = {};
    std::vector<std::thread> workers;
    workers.reserve(workerCount);
    for (size_t index = 0; index < workerCount; ++index)
    {
        workers.emplace_back([&, index]() {
            gate.Wait();
            reservations[index].evaluation = Image::ReserveImageBudget(
                std::vector<uint64_t>{1000, 1000});
        });
    }
    workers.emplace_back([&]() {
        gate.Wait();
        ordinary = {AllocateOrdinary(1000), 1000};
    });
    gate.ReleaseAfterAllArrive();
    for (std::thread& worker : workers)
        worker.join();

    size_t successes = 0;
    size_t failures = 0;
    std::vector<uint32_t> committed;
    for (const ReservationResult& result : reservations)
    {
        if (result.evaluation.IsSuccess())
        {
            ++successes;
            Check(result.evaluation.allocations.size() == 2,
                  "accepted contention batch did not commit as a whole");
            committed.push_back(result.evaluation.allocations[0].imageIndex);
            committed.push_back(result.evaluation.allocations[1].imageIndex);
        }
        else
        {
            ++failures;
            Check(result.evaluation.firstFailure == Budget::Error::Exhausted,
                  "rejected contention batch failed for an unexpected reason");
            Check((result.evaluation.firstFailureIndex == 0 && result.evaluation.allocations.empty()) ||
                  (result.evaluation.firstFailureIndex == 1 && result.evaluation.allocations.size() == 1),
                  "rejected contention batch did not expose a valid dry-run prefix");
        }
    }
    Check(ordinary.imageIndex != Budget::kInvalidImageIndex,
          "ordinary contender did not obtain the final available slot");
    Check(successes == 0 && failures == workerCount,
          "contention rejection did not reject every fallback-exhausted batch");
    CheckIndicesUnique(committed);
    const Snapshot after = GetSnapshot();
    for (int kind = 0; kind < 3; ++kind)
        Check(after.state.cursors[kind] == before.state.cursors[kind],
              "failed contention batch changed a fallback cursor");
    Check(after.state.cursors[3] == 255u && after.ordinary == 1 &&
          after.shadow == 0 && after.reserved == 337,
          "ordinary contender and failed reservations changed counters unexpectedly");
    std::cout << "q05_contention_reject=pass workers=129 ordinary=1 successes=0 failures=128 lock=production-g_MetadataLock\n";
}

void RunSerialReject()
{
    CheckFresh(GetSnapshot());
    std::vector<uint64_t> fill;
    fill.insert(fill.end(), 254, 1000);
    fill.insert(fill.end(), 64, 2 * 1024 * 1024);
    fill.insert(fill.end(), 16, 10 * 1024 * 1024);
    fill.insert(fill.end(), 3, 50 * 1024 * 1024);
    const Evaluation filled = Image::ReserveImageBudget(fill);
    Check(filled.IsSuccess() && filled.allocations.size() == 337,
          "serial fill did not consume the expected fallback capacity");
    const Snapshot before = GetSnapshot();
    const Evaluation rejected = Image::ReserveImageBudget({1000, 1000});
    Check(!rejected.IsSuccess() && rejected.firstFailure == Budget::Error::Exhausted,
          "serial rejection did not report exhausted capacity");
    Check(rejected.firstFailureIndex == 1 && rejected.allocations.size() == 1,
          "serial rejection did not preserve the dry-run prefix");
    const Snapshot after = GetSnapshot();
    for (int kind = 0; kind < 4; ++kind)
        Check(before.state.cursors[kind] == after.state.cursors[kind],
              "failed serial reservation changed a cursor");
    Check(before.reserved == after.reserved && after.reserved == 337,
          "failed serial reservation changed reserved count");
    std::cout << "q05_serial_reject=pass retainedFailureConsumption=0 lock=production-g_MetadataLock\n";
}
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "usage: q05_interpreter_image_contention <scenario>");
        const std::string scenario = argv[1];
        if (scenario == "serial-reserve-first")
            RunSerialReserveFirst();
        else if (scenario == "serial-ordinary-first")
            RunSerialOrdinaryFirst();
        else if (scenario == "contention-accept")
            RunContentionAccept();
        else if (scenario == "contention-reject")
            RunContentionReject();
        else if (scenario == "serial-reject")
            RunSerialReject();
        else
            throw std::runtime_error("unknown scenario");
        std::cout << "q05_concurrency_checks=" << checks << " scenario=" << scenario
                  << " PASS\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "q05_concurrency_failure=" << error.what() << " checks=" << checks << "\n";
        return 1;
    }
}
