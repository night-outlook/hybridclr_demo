// Current profile-2 integration test. Link the actual InterpreterImage entry
// points, metadata-index runtime, and production g_MetadataLock. Atomics only
// align workers; they do not replace any allocator or accounting lock.
#include "hybridclr/metadata/InterpreterImage.h"
#include "vm/MetadataLock.h"
#include "os/Mutex.h"
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace
{
using Image = hybridclr::metadata::InterpreterImage;
using Admission = hybridclr::metadata::InterpreterImageAdmission;
using Runtime = hybridclr::metadata::InterpreterMetadataIndexRuntime;
using Stats = Runtime::Codec::Stats;
size_t checks = 0;

void Check(bool condition, const char* detail)
{
    ++checks;
    if (!condition) throw std::runtime_error(detail);
}

struct Snapshot
{
    Stats stats;
    uint64_t ordinary, shadow, reserved;
};

Snapshot GetSnapshot()
{
    Snapshot result = {};
    Check(Image::GetMetadataCapacitySnapshot(result.stats, result.ordinary,
        result.shadow, result.reserved) == Runtime::Error::None, "capacity snapshot failed");
    return result;
}

void CheckAccounting(const Snapshot& value, uint32_t ordinary, uint32_t reserved)
{
    Check(value.ordinary == ordinary && value.shadow == 0 && value.reserved == reserved,
        "ordinary/Shadow reservation counters disagree");
    Check(value.stats.reservationCount == ordinary + reserved,
        "shared image ledger differs from entry-point counters");
    Check(value.stats.nextImageId == value.stats.reservationCount + 1,
        "monotonic image ID cursor differs from lifetime reservations");
    Check(value.stats.reservedPages == value.stats.reservationCount && value.stats.mappedPages == 0,
        "preliminary reservations must charge one credit each without mapping metadata");
}

void CheckUnchanged(const Snapshot& before, const Snapshot& after)
{
    Check(before.ordinary == after.ordinary && before.shadow == after.shadow &&
        before.reserved == after.reserved && before.stats.reservationCount == after.stats.reservationCount &&
        before.stats.nextImageId == after.stats.nextImageId &&
        before.stats.reservedPages == after.stats.reservedPages &&
        before.stats.mappedPages == after.stats.mappedPages &&
        before.stats.nextPageSlot == after.stats.nextPageSlot,
        "rejected proposal changed committed ledger or accounting");
}

uint32_t AllocateOrdinary(uint64_t size)
{
    il2cpp::os::FastAutoLock lock(&il2cpp::vm::g_MetadataLock);
    return Image::AllocImageIndex(size, false);
}

struct ReservationResult
{
    Admission::Report report;
    Runtime::Error runtimeError;
    std::vector<uint32_t> imageIndices;
};

ReservationResult Reserve(const std::vector<uint64_t>& sizes)
{
    ReservationResult result = {};
    // A rejection must clear stale caller output; it cannot expose a dry-run
    // prefix as if that prefix had been committed.
    result.imageIndices.push_back(UINT32_MAX);
    result.report = Image::ReserveImageBudget(sizes, result.imageIndices, result.runtimeError);
    return result;
}

void CheckSuccess(const ReservationResult& result, size_t count)
{
    Check(result.report.IsSuccess() && result.runtimeError == Runtime::Error::None,
        "fitting reservation failed preliminary admission or runtime reservation");
    Check(result.imageIndices.size() == count && count != 0, "batch not returned as a complete operation");
    Check(result.report.runtimeFinalizationRequired, "preliminary reservation must still require finalization");
    Check(result.report.reservedImageCountAfter == result.report.reservedImageCountBefore + count,
        "successful admission report has wrong committed count");
    for (size_t i = 0; i < count; ++i)
        Check(result.imageIndices[i] == result.report.reservedImageCountBefore + i + 1,
            "report and reserved batch are not one serialized operation");
}

void CheckCapacityRejection(const ReservationResult& result)
{
    Check(result.report.error == Admission::Error::ImageLimit && result.runtimeError == Runtime::Error::None,
        "batch rejected for unexpected admission/runtime reason");
    Check(result.imageIndices.empty(), "rejected batch exposed a committed prefix or stale output");
    Check(result.report.reservedImageCountBefore == result.report.reservedImageCountAfter,
        "rejected admission report claims a partial commit");
}

// Every batch is an indivisible interval in the shared monotonic ID space.
// Complete intervals, rather than uniqueness alone, prove an operation order.
bool IsSerializable(std::vector<std::vector<uint32_t>> operations, uint32_t total)
{
    for (const auto& operation : operations)
    {
        if (operation.empty()) return false;
        for (size_t i = 1; i < operation.size(); ++i)
            if (operation[i] != operation[i - 1] + 1) return false;
    }
    std::sort(operations.begin(), operations.end(),
        [](const std::vector<uint32_t>& a, const std::vector<uint32_t>& b) { return a.front() < b.front(); });
    uint32_t next = 1;
    for (const auto& operation : operations)
    {
        if (operation.front() != next) return false;
        next = operation.back() + 1;
    }
    return next == total + 1;
}

void CheckOracleRegression()
{
    Check(!IsSerializable({{1, 3}, {2, 4}}, 4), "oracle accepted interleaved atomic batches");
    Check(!IsSerializable({{1, 2}, {2, 3}}, 3), "oracle accepted duplicate identities");
    Check(!IsSerializable({{1}, {3}}, 3), "oracle accepted an unexplained reservation hole");
    Check(IsSerializable({{3, 4}, {1, 2}}, 4), "oracle rejected valid reordered whole batches");
}

void RunSerial(bool reserveFirst)
{
    const std::vector<uint64_t> sizes = {1000, 2 * 1024 * 1024, 10 * 1024 * 1024};
    std::vector<std::vector<uint32_t>> operations;
    if (reserveFirst)
    {
        ReservationResult result = Reserve(sizes);
        CheckSuccess(result, sizes.size());
        operations.push_back(result.imageIndices);
    }
    for (uint64_t size : sizes) operations.push_back({AllocateOrdinary(size)});
    if (!reserveFirst)
    {
        ReservationResult result = Reserve(sizes);
        CheckSuccess(result, sizes.size());
        operations.push_back(result.imageIndices);
    }
    Check(IsSerializable(operations, 6), "serial operations do not occupy disjoint complete ranges");
    CheckAccounting(GetSnapshot(), 3, 3);
}

struct StartGate
{
    const size_t expected;
    std::atomic<size_t> arrived;
    std::atomic<bool> open;
    explicit StartGate(size_t count) : expected(count), arrived(0), open(false) {}
    void Wait()
    {
        arrived.fetch_add(1, std::memory_order_release);
        while (!open.load(std::memory_order_acquire)) std::this_thread::yield();
    }
    void Release()
    {
        while (arrived.load(std::memory_order_acquire) != expected) std::this_thread::yield();
        open.store(true, std::memory_order_release);
    }
};

void RunContentionAccept()
{
    const size_t ordinaryCount = 24, reservationCount = 24;
    StartGate gate(ordinaryCount + reservationCount);
    std::vector<uint32_t> ordinary(ordinaryCount);
    std::vector<ReservationResult> reservations(reservationCount);
    std::vector<std::thread> workers;
    for (size_t i = 0; i < ordinaryCount; ++i)
        workers.emplace_back([&, i] {
            gate.Wait();
            ordinary[i] = AllocateOrdinary(i % 3 == 0 ? 1000 : (i % 3 == 1 ? 2 * 1024 * 1024 : 10 * 1024 * 1024));
        });
    for (size_t i = 0; i < reservationCount; ++i)
        workers.emplace_back([&, i] { gate.Wait(); reservations[i] = Reserve({1000, 2 * 1024 * 1024}); });
    gate.Release();
    for (auto& worker : workers) worker.join();
    std::vector<std::vector<uint32_t>> operations;
    for (uint32_t id : ordinary) operations.push_back({id});
    for (const auto& result : reservations)
    {
        CheckSuccess(result, 2);
        operations.push_back(result.imageIndices);
    }
    CheckOracleRegression();
    Check(IsSerializable(operations, ordinaryCount + reservationCount * 2),
        "concurrent ordinary and reserved batches are not serializable");
    CheckAccounting(GetSnapshot(), ordinaryCount, reservationCount * 2);
    std::cout << "r01b_contention_accept=pass workers=48 ordinary=24 shadowBatches=24 lock=production-g_MetadataLock oracle=shared-id-atomic-intervals\n";
}

void PrefillOneRemaining()
{
    const uint32_t fill = Admission::kMaximumImages - 1;
    ReservationResult result = Reserve(std::vector<uint64_t>(fill, 1000));
    CheckSuccess(result, fill);
    CheckAccounting(GetSnapshot(), 0, fill);
}

void RunContentionReject()
{
    PrefillOneRemaining();
    const Snapshot before = GetSnapshot();
    const size_t workerCount = 128;
    StartGate gate(workerCount + 1);
    std::vector<ReservationResult> reservations(workerCount);
    uint32_t ordinary = 0;
    std::vector<std::thread> workers;
    for (size_t i = 0; i < workerCount; ++i)
        workers.emplace_back([&, i] { gate.Wait(); reservations[i] = Reserve({1000, 1000}); });
    workers.emplace_back([&] { gate.Wait(); ordinary = AllocateOrdinary(1000); });
    gate.Release();
    for (auto& worker : workers) worker.join();
    for (const auto& result : reservations)
    {
        CheckCapacityRejection(result);
        Check(result.report.reservedImageCountBefore == Admission::kMaximumImages - 1 ||
            result.report.reservedImageCountBefore == Admission::kMaximumImages,
            "rejection observed an impossible admission snapshot");
        Check(result.report.firstFailureIndex == Admission::kMaximumImages - result.report.reservedImageCountBefore,
            "rejection did not report the exact remaining shared capacity");
    }
    Check(ordinary == Admission::kMaximumImages, "ordinary contender did not obtain the only remaining identity");
    const Snapshot after = GetSnapshot();
    CheckAccounting(after, 1, Admission::kMaximumImages - 1);
    Check(after.reserved == before.reserved, "failed Shadow batches consumed reservation accounting");
    Check(AllocateOrdinary(1000) == hybridclr::metadata::kInvalidImageIndex,
        "ordinary allocation succeeded beyond shared image capacity");
    CheckUnchanged(after, GetSnapshot());
    std::cout << "r01b_contention_reject=pass workers=129 ordinary=1 rejectedBatches=128 limit="
        << Admission::kMaximumImages << " lock=production-g_MetadataLock\n";
}

void RunSerialReject()
{
    PrefillOneRemaining();
    const Snapshot before = GetSnapshot();
    ReservationResult rejected = Reserve({1000, 1000});
    CheckCapacityRejection(rejected);
    Check(rejected.report.firstFailureIndex == 1, "one remaining slot was not reported");
    CheckUnchanged(before, GetSnapshot());
    ReservationResult final = Reserve({1000});
    CheckSuccess(final, 1);
    Check(final.imageIndices[0] == Admission::kMaximumImages, "failed batch consumed the final identity");
    CheckAccounting(GetSnapshot(), 0, Admission::kMaximumImages);
    const Snapshot full = GetSnapshot();
    CheckCapacityRejection(Reserve({1000}));
    CheckUnchanged(full, GetSnapshot());
}
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "usage: r01b_contention <scenario>");
        Check(Admission::kProfileVersion == 2, "requires current profile-2 admission");
        Image::Initialize();
        CheckAccounting(GetSnapshot(), 0, 0);
        const std::string scenario = argv[1];
        if (scenario == "serial-reserve-first") RunSerial(true);
        else if (scenario == "serial-ordinary-first") RunSerial(false);
        else if (scenario == "contention-accept") RunContentionAccept();
        else if (scenario == "contention-reject") RunContentionReject();
        else if (scenario == "serial-reject") RunSerialReject();
        else throw std::runtime_error("unknown scenario");
        std::cout << "r01b_concurrency_checks=" << checks << " scenario=" << scenario << " PASS\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "r01b_concurrency_failure=" << error.what() << " checks=" << checks << "\n";
        return 1;
    }
}
