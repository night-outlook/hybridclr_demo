// R03 B2 SOURCE-HOST ONLY. Compile the exact pinned Runtime.cpp and Codec.h.
// The only surrogate is the two AssemblyShadowBridge visibility callbacks.
// No Unity/IL2CPP binary, metadata allocation, GC, rollback, or VM epoch is tested.
#include "hybridclr/metadata/InterpreterMetadataIndexRuntime.h"
#include "hybridclr/metadata/AssemblyShadowBridge.h"

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

namespace hybridclr { namespace metadata {
namespace {
// A test-only stand-in for the VM active-snapshot and private-stage predicates.
// Neither predicate claims to reproduce the native transaction implementation.
std::atomic<bool> mockVmActive(false);
std::atomic<bool> mockPrivateStage(false);
uint32_t mockShadowId = 0;
InterpreterImage* mockShadowImage = nullptr;
}
InterpreterImage* AssemblyShadowBridge::GetPrivateImage(uint32_t imageId)
{
    return mockPrivateStage.load(std::memory_order_acquire) &&
        imageId == mockShadowId ? mockShadowImage : nullptr;
}
bool AssemblyShadowBridge::IsPublicImage(uint32_t imageId, InterpreterImage* image)
{
    return mockVmActive.load(std::memory_order_acquire) &&
        imageId == mockShadowId && image == mockShadowImage;
}
}}

using Runtime = hybridclr::metadata::InterpreterMetadataIndexRuntime;
using Codec = Runtime::Codec;
using Error = Runtime::Error;
using Image = hybridclr::metadata::InterpreterImage;

static unsigned scenarios = 0;
static unsigned checks = 0;
static void Check(bool condition, const char* expression, int line)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "FAIL line %d: %s\n", line, expression);
        std::abort();
    }
}
#define CHECK(expr) Check(bool(expr), #expr, __LINE__)

// The Runtime implementation only retains/compares these pointers. No fake
// InterpreterImage is constructed or dereferenced by this source-host.
struct Marker { uint32_t tag; };

int main()
{
    using namespace hybridclr::metadata;
    Codec::DecodedData data;
    Codec::Stats before{}, after{};
    std::vector<Runtime::Reservation> reservations;
    std::vector<Runtime::Reservation> empty;
    Marker markers[4] = {{101}, {102}, {103}, {104}};
    Image* images[4] = {
        reinterpret_cast<Image*>(&markers[0]),
        reinterpret_cast<Image*>(&markers[1]),
        reinterpret_cast<Image*>(&markers[2]),
        reinterpret_cast<Image*>(&markers[3])
    };
    int32_t tokens[4] = {};

    // Scenario 1: no implicit publication or initialized runtime on bad input.
    ++scenarios;
    const uint32_t unopened = 1;
    CHECK(Runtime::GetStats(before) == Error::InvalidState);
    CHECK(Runtime::PublishBatch(nullptr, 1) == Error::InvalidArgument);
    CHECK(Runtime::PublishBatch(&unopened, 1) == Error::InvalidState);
    CHECK(Runtime::ReserveImages(0, empty) == Error::InvalidArgument);
    CHECK(empty.empty());

    // Scenario 2: real Runtime reservations and construction associations.
    ++scenarios;
    CHECK(Runtime::ReserveImages(4, reservations) == Error::None);
    CHECK(reservations.size() == 4);
    CHECK(Runtime::GetStats(before) == Error::None);
    CHECK(before.reservationCount == 4);
    for (unsigned i = 0; i < 4; ++i)
    {
        CHECK(reservations[i].imageId != 0);
        CHECK(Runtime::GetPublishedImage(reservations[i].imageId) == nullptr);
        {
            const bool shadow = (i == 2);
            Runtime::ScopedConstruction scope(reservations[i].imageId, images[i], shadow);
            CHECK(Runtime::GetConstructionImage(reservations[i].imageId) == images[i]);
            CHECK(Runtime::Encode(reservations[i].imageId, 0, tokens[i]) == Error::None);
            CHECK(Runtime::Decode(tokens[i], data) == Error::None);
            CHECK(data.imageId == reservations[i].imageId && data.rawIndex == 0);
            // Leave the second member unfinalized to test batch atomicity.
            if (i != 1)
                CHECK(Runtime::Finalize(reservations[i].imageId, 1) == Error::None);
        }
        CHECK(Runtime::GetConstructionImage(reservations[i].imageId) == nullptr);
    }
    mockShadowId = reservations[2].imageId;
    mockShadowImage = images[2];
    // Snapshot the ledger AFTER test construction/Encode, before publication.
    CHECK(Runtime::GetStats(before) == Error::None);

    // Scenario 3: association, even when finalized, is not public admission.
    ++scenarios;
    for (unsigned i = 0; i < 4; ++i)
    {
        CHECK(Runtime::GetPublishedImage(reservations[i].imageId) == nullptr);
        CHECK(Runtime::Decode(tokens[i], data) == Error::OwnerRequired);
        CHECK(Runtime::TokenBelongsToImageForVisibility(tokens[i],
            reservations[i].imageId));
    }

    // Scenario 4: a later missing record must not publish an earlier one.
    ++scenarios;
    const uint32_t missingSecond[2] = {reservations[0].imageId, 0};
    CHECK(Runtime::PublishBatch(missingSecond, 2) == Error::InvalidImage);
    CHECK(Runtime::GetPublishedImage(reservations[0].imageId) == nullptr);
    CHECK(Runtime::Decode(tokens[0], data) == Error::OwnerRequired);

    // Scenario 5: a later unfinalized record rejects the complete batch.
    ++scenarios;
    const uint32_t ordinaryPair[2] = {
        reservations[0].imageId, reservations[1].imageId
    };
    CHECK(Runtime::PublishBatch(ordinaryPair, 2) == Error::Unfinalized);
    CHECK(Runtime::GetPublishedImage(ordinaryPair[0]) == nullptr);
    CHECK(Runtime::GetPublishedImage(ordinaryPair[1]) == nullptr);
    CHECK(Runtime::Decode(tokens[0], data) == Error::OwnerRequired);

    // Scenario 6: duplicate IDs cannot produce partial group publication.
    ++scenarios;
    const uint32_t duplicatePair[2] = {
        reservations[0].imageId, reservations[0].imageId
    };
    CHECK(Runtime::PublishBatch(duplicatePair, 2) == Error::InvalidArgument);
    CHECK(Runtime::GetPublishedImage(reservations[0].imageId) == nullptr);
    CHECK(Runtime::Decode(tokens[0], data) == Error::OwnerRequired);
    {
        Runtime::ScopedConstruction scope(reservations[1].imageId, images[1], false);
        CHECK(Runtime::Finalize(reservations[1].imageId, 1) == Error::None);
    }

    // Scenario 7: the actual Runtime activates a complete ordinary group.
    ++scenarios;
    CHECK(Runtime::PublishBatch(ordinaryPair, 2) == Error::None);
    for (unsigned i = 0; i < 2; ++i)
    {
        CHECK(Runtime::GetPublishedImage(reservations[i].imageId) == images[i]);
        CHECK(Runtime::Decode(tokens[i], data) == Error::None);
        CHECK(data.imageId == reservations[i].imageId && data.rawIndex == 0);
    }
    CHECK(Runtime::GetStats(after) == Error::None);
    CHECK(after.reservationCount == before.reservationCount);
    CHECK(after.reservedPages == before.reservedPages);
    CHECK(after.mappedPages == before.mappedPages);

    // Scenario 8: a published group is irreversible at this API boundary.
    ++scenarios;
    CHECK(Runtime::PublishBatch(ordinaryPair, 2) == Error::InvalidState);
    CHECK(Runtime::Abort(reservations[0]) == Error::InvalidState);
    CHECK(Runtime::Abort(reservations[0].imageId) == Error::InvalidState);
    CHECK(Runtime::GetPublishedImage(reservations[0].imageId) == images[0]);

    // Scenario 9: the Runtime rejects mixing published and private records.
    ++scenarios;
    const uint32_t mixed[2] = {
        reservations[0].imageId, reservations[3].imageId
    };
    CHECK(Runtime::PublishBatch(mixed, 2) == Error::InvalidState);
    CHECK(Runtime::GetPublishedImage(reservations[3].imageId) == nullptr);
    CHECK(Runtime::Decode(tokens[3], data) == Error::OwnerRequired);

    // Scenario 10: a later aborted image cannot publish a valid shadow image.
    ++scenarios;
    CHECK(Runtime::Abort(reservations[3].imageId) == Error::None);
    const uint32_t shadowAndAborted[2] = {
        reservations[2].imageId, reservations[3].imageId
    };
    CHECK(Runtime::PublishBatch(shadowAndAborted, 2) == Error::InvalidState);
    CHECK(Runtime::GetPublishedImage(reservations[2].imageId) == nullptr);
    CHECK(Runtime::Decode(tokens[3], data) == Error::InvalidState);

    // Scenario 11: codec/group publication does not open the VM shadow gate.
    ++scenarios;
    CHECK(!mockVmActive.load(std::memory_order_acquire));
    CHECK(Runtime::Publish(reservations[2].imageId) == Error::None);
    CHECK(Runtime::GetPublishedImage(reservations[2].imageId) == nullptr);
    CHECK(Runtime::Decode(tokens[2], data) == Error::OwnerRequired);

    // Scenario 12: only the MOCK VM activation makes the published image visible.
    ++scenarios;
    mockVmActive.store(true, std::memory_order_release);
    CHECK(Runtime::GetPublishedImage(reservations[2].imageId) == images[2]);
    CHECK(Runtime::Decode(tokens[2], data) == Error::None);
    CHECK(data.imageId == reservations[2].imageId && data.rawIndex == 0);
    CHECK(Runtime::Abort(reservations[2].imageId) == Error::InvalidState);
    CHECK(Runtime::GetPublishedImage(reservations[3].imageId) == nullptr);

    std::printf("{\"kind\":\"R03B2ActualRuntimePublicationGroup\","
        "\"result\":\"PassedActualRuntimeHostWithMockBridge\","
        "\"scenarios\":%u,\"checks\":%u,"
        "\"exactRuntimeSourceRequired\":true,"
        "\"bridgeIsMock\":true,"
        "\"actualCodecUsed\":true,"
        "\"runtimeGroupNormalReturnsTested\":true,"
        "\"vmSnapshotReal\":false,"
        "\"concurrentReadersTested\":false,"
        "\"exceptionFreedomProven\":false,"
        "\"rollbackAfterPublicationPossible\":false,"
        "\"nativeProductionChanged\":false,"
        "\"realUnity\":false,\"R03Accepted\":false,"
        "\"H2Passed\":false,\"ReadyForHumanReviewGate\":false}\n",
        scenarios, checks);
    return 0;
}
