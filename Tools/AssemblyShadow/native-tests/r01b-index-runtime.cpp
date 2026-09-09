#include "metadata/InterpreterMetadataIndexRuntime.h"
#include "metadata/AssemblyShadowBridge.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <mutex>
#include <new>
#include <set>
#include <thread>
#include <vector>

namespace
{
using Runtime = hybridclr::metadata::InterpreterMetadataIndexRuntime;
using Codec = Runtime::Codec;
using Reservation = Runtime::Reservation;
using InterpreterImage = hybridclr::metadata::InterpreterImage;

thread_local uint32_t membershipId = 0;
thread_local InterpreterImage* membershipImage = nullptr;
std::atomic<uint64_t> allocationCount(0);
std::atomic<bool> shadowPublic(false);
size_t checks = 0;

void* Allocate(std::size_t size)
{
    allocationCount.fetch_add(1, std::memory_order_relaxed);
    void* result = std::malloc(size == 0 ? 1 : size);
    if (result == nullptr)
        throw std::bad_alloc();
    return result;
}
}

void* operator new(std::size_t size) { return Allocate(size); }
void* operator new[](std::size_t size) { return Allocate(size); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
#if __cplusplus >= 201402L
void operator delete(void* pointer, std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { std::free(pointer); }
#endif

namespace hybridclr { namespace metadata {
InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t imageIndex)
{
    return imageIndex == membershipId ? membershipImage : nullptr;
}

bool AssemblyShadowBridge::IsPublicImage(uint32_t, InterpreterImage*)
{
    return shadowPublic.load(std::memory_order_acquire);
}
}}

namespace
{
void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "r01b index-runtime check failed: %s\n", message);
        std::exit(1);
    }
}

void CheckError(Runtime::Error actual, Runtime::Error expected, const char* message)
{
    Check(actual == expected, message);
}

void SetMembership(const Reservation& reservation, InterpreterImage* image)
{
    membershipId = reservation.imageId;
    membershipImage = image;
}

void ClearMembership()
{
    membershipId = 0;
    membershipImage = nullptr;
}

InterpreterImage* FakeImage(uintptr_t value)
{
    return reinterpret_cast<InterpreterImage*>(value);
}

bool SameDecoded(const Codec::DecodedData& value, uint32_t imageId, int64_t rawIndex)
{
    return value.imageId == imageId && value.rawIndex == rawIndex;
}

void TestUninitializedDecode()
{
    Codec::DecodedData output;
    output.imageId = 71;
    output.rawIndex = 72;
    const uint64_t allocations = allocationCount.load(std::memory_order_relaxed);
    CheckError(Runtime::Decode(-2, output), Codec::Error::InvalidState,
        "uninitialized decode reports invalid state");
    Check(SameDecoded(output, 71, 72), "uninitialized decode leaves output unchanged");
    Check(allocationCount.load(std::memory_order_relaxed) == allocations,
        "uninitialized decode performs no allocation");
}

void TestReservationsAndConstruction(Reservation& first, Reservation& second,
    InterpreterImage* firstImage, InterpreterImage* secondImage)
{
    std::vector<Reservation> batch;
    CheckError(Runtime::ReserveImages(2, batch), Codec::Error::None,
        "two-image reservation batch succeeds");
    Check(batch.size() == 2 && batch[0].imageId != batch[1].imageId,
        "batch image IDs are distinct");
    Check(batch[0].owner != 0 && batch[0].owner == batch[1].owner,
        "batch uses one stable common owner");
    first = batch[0];
    second = batch[1];

    Check(Runtime::GetConstructionImage(first.imageId) == nullptr,
        "construction lookup starts empty");
    {
        Runtime::ScopedConstruction outer(first, firstImage);
        Check(Runtime::GetConstructionImage(first.imageId) == firstImage,
            "outer construction image is visible");
        {
            Runtime::ScopedConstruction inner(second, secondImage);
            Check(Runtime::GetConstructionImage(second.imageId) == secondImage,
                "nested construction image is visible");
            Check(Runtime::GetConstructionImage(first.imageId) == firstImage,
                "nested construction preserves ancestor lookup");
        }
        Check(Runtime::GetConstructionImage(second.imageId) == nullptr,
            "nested construction restores after destruction");
        Check(Runtime::GetConstructionImage(first.imageId) == firstImage,
            "ancestor construction is restored");
    }
    Check(Runtime::GetConstructionImage(first.imageId) == nullptr,
        "construction lookup clears after outer destruction");
}

void TestPrivateOwnershipAndFootprint(const Reservation& first,
    const Reservation& second, InterpreterImage* firstImage,
    InterpreterImage* secondImage)
{
    int32_t firstToken = 0;
    SetMembership(first, firstImage);
    CheckError(Runtime::Encode(first.imageId, 0, firstToken), Codec::Error::None,
        "exact staging membership permits private encoding");
    ClearMembership();

    Codec::DecodedData output;
    output.imageId = 91;
    output.rawIndex = 92;
    std::thread foreign([&] {
        CheckError(Runtime::Decode(firstToken, output), Codec::Error::OwnerRequired,
            "foreign thread rejects private decode");
    });
    foreign.join();
    Check(SameDecoded(output, 91, 92), "foreign private decode leaves output unchanged");

    int32_t rejected = 0;
    SetMembership(second, secondImage);
    CheckError(Runtime::Encode(first.imageId, 0, rejected), Codec::Error::OwnerRequired,
        "same-batch owner without image membership is rejected");
    SetMembership(first, firstImage);
    CheckError(Runtime::Encode(first.imageId, Codec::kPageSize, rejected), Codec::Error::None,
        "exact membership permits private growth");

    Codec::FootprintStats footprint;
    CheckError(Runtime::GetFootprint(first.imageId, footprint), Codec::Error::None,
        "private footprint is readable before finalization");
    Check(footprint.chargedPages == 2 && footprint.mappedPages == 2 && !footprint.sealed,
        "private growth charges and maps a second page");
    CheckError(Runtime::Finalize(first.imageId, 3u * Codec::kPageSize), Codec::Error::None,
        "final footprint seals successfully");
    CheckError(Runtime::GetFootprint(first.imageId, footprint), Codec::Error::None,
        "sealed footprint is readable");
    Check(footprint.lowEnd == 3u * Codec::kPageSize && footprint.requiredPages == 3 &&
        footprint.chargedPages == 3 && footprint.sealed,
        "final footprint includes low range without undercharging");
    CheckError(Runtime::Publish(first.imageId), Codec::Error::None,
        "sealed image publishes");
    Check(Runtime::GetPublishedImage(first.imageId) == firstImage,
        "published image lookup returns associated opaque image");

    Codec::Stats beforeLazy;
    Codec::Stats afterLazy;
    CheckError(Runtime::GetStats(beforeLazy), Codec::Error::None,
        "stats readable before lazy mapping");
    ClearMembership();
    int32_t lazyToken = 0;
    CheckError(Runtime::Encode(first.imageId, 2u * Codec::kPageSize, lazyToken), Codec::Error::None,
        "precharged low-range lazy page maps after publication");
    CheckError(Runtime::GetStats(afterLazy), Codec::Error::None,
        "stats readable after lazy mapping");
    Check(afterLazy.reservedPages == beforeLazy.reservedPages &&
        afterLazy.mappedPages == beforeLazy.mappedPages + 1,
        "lazy mapping consumes footprint without charge growth");
    CheckError(Runtime::Decode(lazyToken, output), Codec::Error::None,
        "published lazy token decodes without private membership");
    Check(SameDecoded(output, first.imageId, 2u * Codec::kPageSize),
        "published lazy token preserves raw index");

    SetMembership(second, secondImage);
    CheckError(Runtime::Publish(second.imageId), Codec::Error::Unfinalized,
        "publish before sealing is rejected");
    int32_t secondToken = 0;
    CheckError(Runtime::Encode(second.imageId, 0, secondToken), Codec::Error::None,
        "second private image maps initial page");
    const uint64_t oversizedLowEnd = (uint64_t(Codec::kMaxChargedPages) + 1u) * Codec::kPageSize;
    CheckError(Runtime::Finalize(second.imageId, oversizedLowEnd), Codec::Error::PageLimit,
        "partial footprint beyond global page budget is rejected");
    CheckError(Runtime::GetFootprint(second.imageId, footprint), Codec::Error::None,
        "failed finalization leaves footprint readable");
    Check(footprint.chargedPages == 1 && footprint.mappedPages == 1 && !footprint.sealed,
        "failed finalization leaves private footprint unsealed");
    ClearMembership();
}

void TestAbortAndUnknownTokens(Reservation& aborted, InterpreterImage* image)
{
    std::vector<Reservation> batch;
    CheckError(Runtime::ReserveImages(1, batch), Codec::Error::None,
        "abort reservation succeeds");
    aborted = batch[0];
    Runtime::ScopedConstruction construction(aborted, image);
    SetMembership(aborted, image);
    int32_t token = 0;
    CheckError(Runtime::Encode(aborted.imageId, 0, token), Codec::Error::None,
        "aborted image maps a page before abort");
    ClearMembership();
    Codec::Stats before;
    CheckError(Runtime::GetStats(before), Codec::Error::None, "stats readable before abort");
    CheckError(Runtime::Abort(aborted.imageId), Codec::Error::None, "private image aborts by retained identity");
    Codec::Stats after;
    CheckError(Runtime::GetStats(after), Codec::Error::None, "stats readable after abort");
    Check(after.reservedPages == before.reservedPages &&
        after.reservationCount == before.reservationCount,
        "abort retains charged credits and reservation identity");

    Codec::DecodedData output;
    output.imageId = 111;
    output.rawIndex = 112;
    CheckError(Runtime::Decode(token, output), Codec::Error::InvalidState,
        "aborted token reports invalid state");
    Check(SameDecoded(output, 111, 112), "aborted decode leaves output unchanged");
    CheckError(Runtime::Decode(-1, output), Codec::Error::Sentinel,
        "sentinel negative token is rejected");
    CheckError(Runtime::Decode(-2, output), Codec::Error::UnknownToken,
        "unknown negative token is rejected");
    Check(SameDecoded(output, 111, 112), "unknown token decode leaves output unchanged");
}

void TestShadowBatchVisibility()
{
    std::vector<Reservation> batch;
    CheckError(Runtime::ReserveImages(2, batch), Codec::Error::None,
        "Shadow publication batch reserves two images");
    InterpreterImage* firstImage = FakeImage(0x4000);
    InterpreterImage* secondImage = FakeImage(0x5000);
    {
        Runtime::ScopedConstruction construction(batch[0].imageId, firstImage, true);
        int32_t token = 0;
        CheckError(Runtime::Encode(batch[0].imageId, 17, token), Codec::Error::None,
            "first Shadow image encodes in construction scope");
    }
    {
        Runtime::ScopedConstruction construction(batch[1].imageId, secondImage, true);
        int32_t token = 0;
        CheckError(Runtime::Encode(batch[1].imageId, 29, token), Codec::Error::None,
            "second Shadow image encodes in construction scope");
    }
    SetMembership(batch[0], firstImage);
    CheckError(Runtime::Finalize(batch[0].imageId, 18), Codec::Error::None,
        "first Shadow footprint seals through private membership");
    SetMembership(batch[1], secondImage);
    CheckError(Runtime::Finalize(batch[1].imageId, 30), Codec::Error::None,
        "second Shadow footprint seals through private membership");
    ClearMembership();

    const uint32_t duplicate[] = { batch[0].imageId, batch[0].imageId };
    CheckError(Runtime::PublishBatch(duplicate, 2), Codec::Error::InvalidArgument,
        "duplicate publication batch rejects before any transition");
    const uint32_t ids[] = { batch[0].imageId, batch[1].imageId };
    shadowPublic.store(false, std::memory_order_release);
    CheckError(Runtime::PublishBatch(ids, 2), Codec::Error::None,
        "complete Shadow codec batch publishes behind VM gate");
    Check(Runtime::GetPublishedImage(ids[0]) == nullptr &&
        Runtime::GetPublishedImage(ids[1]) == nullptr,
        "inactive VM snapshot hides the complete Shadow batch");
    Codec::DecodedData output;
    int32_t firstToken = 0;
    SetMembership(batch[0], firstImage);
    CheckError(Runtime::Encode(batch[0].imageId, 17, firstToken), Codec::Error::None,
        "private membership retains access behind inactive VM gate");
    ClearMembership();
    CheckError(Runtime::Decode(firstToken, output), Codec::Error::OwnerRequired,
        "foreign decode remains hidden before VM snapshot publication");
    shadowPublic.store(true, std::memory_order_release);
    Check(Runtime::GetPublishedImage(ids[0]) == firstImage &&
        Runtime::GetPublishedImage(ids[1]) == secondImage,
        "one VM snapshot transition exposes the complete Shadow batch");
    CheckError(Runtime::Decode(firstToken, output), Codec::Error::None,
        "Shadow token decodes after VM snapshot publication");
}

void TestConcurrentAndCumulativeReservations(uint32_t retainedCount)
{
    const uint32_t threadCount = 8;
    const uint32_t perThread = 4;
    std::vector<std::vector<Reservation>> results(threadCount);
    std::vector<Runtime::Error> errors(threadCount, Codec::Error::None);
    std::vector<std::thread> workers;
    for (uint32_t worker = 0; worker < threadCount; ++worker)
    {
        workers.emplace_back([&, worker] {
            errors[worker] = Runtime::ReserveImages(perThread, results[worker]);
        });
    }
    for (std::thread& worker : workers)
        worker.join();
    std::set<uint32_t> imageIds;
    std::set<uint64_t> owners;
    for (uint32_t worker = 0; worker < threadCount; ++worker)
    {
        CheckError(errors[worker], Codec::Error::None,
            "concurrent reservation batch succeeds");
        Check(results[worker].size() == perThread,
            "concurrent batch retains every reservation");
        Check(results[worker][0].owner != 0,
            "concurrent batch owner is nonzero");
        for (const Reservation& reservation : results[worker])
        {
            Check(reservation.owner == results[worker][0].owner,
                "concurrent batch uses one common owner");
            Check(imageIds.insert(reservation.imageId).second,
                "concurrent reservations have unique image IDs");
            owners.insert(reservation.owner);
        }
    }
    Check(imageIds.size() == threadCount * perThread && owners.size() == threadCount,
        "concurrent reservations have unique IDs and owners");

    Codec::Stats stats;
    CheckError(Runtime::GetStats(stats), Codec::Error::None,
        "stats readable before cumulative reservation fill");
    const uint32_t remaining = Codec::kMaxImageCount - stats.reservationCount;
    std::vector<Reservation> finalBatch;
    CheckError(Runtime::ReserveImages(remaining, finalBatch), Codec::Error::None,
        "cumulative reservation reaches image limit");
    Check(finalBatch.size() == remaining, "cumulative final batch is retained");
    CheckError(Runtime::GetStats(stats), Codec::Error::None,
        "stats readable at image limit");
    Check(stats.reservationCount == Codec::kMaxImageCount && stats.nextImageId == Codec::kMaxImageCount + 1u,
        "8192 reservations retain IDs and credits");
    std::vector<Reservation> rejected;
    CheckError(Runtime::ReserveImages(1, rejected), Codec::Error::ImageLimit,
        "8193rd cumulative reservation is rejected");
    Check(retainedCount + threadCount * perThread + remaining == stats.reservationCount,
        "cumulative reservation arithmetic is stable");
}
}

int main()
{
    TestUninitializedDecode();
    CheckError(Runtime::Initialize(), Codec::Error::None, "runtime initializes");
    CheckError(Runtime::Initialize(), Codec::Error::None, "runtime initialization is idempotent");

    Reservation first;
    Reservation second;
    TestReservationsAndConstruction(first, second, FakeImage(0x1000), FakeImage(0x2000));
    TestPrivateOwnershipAndFootprint(first, second, FakeImage(0x1000), FakeImage(0x2000));

    Reservation aborted;
    TestAbortAndUnknownTokens(aborted, FakeImage(0x3000));
    TestShadowBatchVisibility();
    const uint32_t retained = 5;
    TestConcurrentAndCumulativeReservations(retained);
    std::printf("r01b_index_runtime_checks=%zu PASS\n", checks);
    return 0;
}
