#include "metadata/InterpreterMetadataIndexCodec.h"

#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <limits>
#include <thread>
#include <vector>

using hybridclr::metadata::InterpreterMetadataIndexCodec;

namespace
{

typedef InterpreterMetadataIndexCodec Codec;

void Check(bool condition, const char* name, uint64_t& checks)
{
    ++checks;
    if (!condition)
    {
        std::cerr << "[FAIL] " << name << std::endl;
        std::abort();
    }
}

void CheckError(Codec::Error actual, Codec::Error expected, const char* name,
    uint64_t& checks)
{
    Check(actual == expected, name, checks);
}

void InvalidLimitsAndOwnerZero(uint64_t& checks)
{
    Codec invalidImages(0, 1);
    Codec invalidPages(1, Codec::kMaxChargedPages + 1u);
    Check(!invalidImages.IsValid() &&
        invalidImages.InitializationError() == Codec::Error::InvalidLimits,
        "invalid image limit is explicit", checks);
    Check(!invalidPages.IsValid() &&
        invalidPages.InitializationError() == Codec::Error::InvalidLimits,
        "invalid charged-page limit is explicit", checks);

    Codec injectedOom(8, 8, 0);
    Check(!injectedOom.IsValid() &&
        injectedOom.InitializationError() == Codec::Error::OutOfMemory,
        "constructor allocation failure is explicit", checks);
    Codec injectedSecondOom(8, 8, 1);
    Check(!injectedSecondOom.IsValid() &&
        injectedSecondOom.InitializationError() == Codec::Error::OutOfMemory,
        "second constructor allocation failure is explicit", checks);

    Codec codec(8, 8);
    Check(codec.DecodeIsLockFree(), "descriptor atomics report lock-free decode", checks);
    Codec::Reservation reservation;
    CheckError(codec.Reserve(0, 1, reservation), Codec::Error::OwnerRequired,
        "owner zero cannot reserve private image", checks);
    CheckError(codec.Reserve(1, 0, reservation), Codec::Error::ZeroCredits,
        "zero credits are explicit", checks);
    const Codec::Stats stats = codec.GetStats();
    Check(stats.reservationCount == 0 && stats.reservedPages == 0 &&
        stats.nextImageId == 1 && stats.nextPageSlot == 0,
        "invalid reservation inputs do not mutate ledger", checks);
}

void AtomicBatchAndInternalIds(uint64_t& checks)
{
    Codec codec(8, 4);
    const Codec::BatchRequest tooLarge[] = {{11, 3}, {22, 2}};
    Codec::Reservation failed[2];
    const Codec::Stats before = codec.GetStats();
    CheckError(codec.ReserveBatch(tooLarge, 2, failed), Codec::Error::PageLimit,
        "failed reservation batch is rejected atomically", checks);
    const Codec::Stats after = codec.GetStats();
    Check(after.reservationCount == before.reservationCount &&
        after.reservedPages == before.reservedPages &&
        after.nextImageId == before.nextImageId &&
        after.nextPageSlot == before.nextPageSlot,
        "failed batch leaves IDs/pages unchanged", checks);

    const Codec::BatchRequest requests[] = {{11, 1}, {22, 1}};
    Codec::Reservation reservations[2];
    CheckError(codec.ReserveBatch(requests, 2, reservations), Codec::Error::None,
        "successful reservation batch", checks);
    Check(reservations[0].imageId == 1 && reservations[1].imageId == 2,
        "image IDs are internally monotonic", checks);
    CheckError(codec.GrantPages(reservations[0], 11, 1), Codec::Error::None,
        "ordinary and shadow use one shared page ledger", checks);
    CheckError(codec.GrantPages(reservations[1], 22, 1), Codec::Error::None,
        "interleaved growth grant", checks);
    CheckError(codec.GrantPages(reservations[0], 0, 1), Codec::Error::OwnerRequired,
        "unscoped caller cannot grant private growth", checks);
    CheckError(codec.GrantPages(reservations[0], 11, 0), Codec::Error::ZeroCredits,
        "zero growth credits are explicit", checks);

    Codec small(2, 2);
    Codec::Reservation smallImage;
    CheckError(small.Reserve(33, 1, smallImage), Codec::Error::None,
        "small growth reservation", checks);
    const Codec::Stats beforeGrant = small.GetStats();
    CheckError(small.GrantPages(smallImage, 33, 2), Codec::Error::PageLimit,
        "growth beyond global charge is rejected", checks);
    const Codec::Stats afterGrant = small.GetStats();
    Check(afterGrant.reservedPages == beforeGrant.reservedPages &&
        afterGrant.nextPageSlot == beforeGrant.nextPageSlot,
        "failed growth grant leaves quota ledger unchanged", checks);
}

void ArithmeticAndDomains(uint64_t& checks)
{
    Codec codec(8, 8);
    Codec::Reservation ordinary;
    Codec::Reservation shadow;
    CheckError(codec.Reserve(101, 4, ordinary), Codec::Error::None,
        "ordinary reservation", checks);
    CheckError(codec.Reserve(202, 2, shadow), Codec::Error::None,
        "shadow reservation", checks);

    int32_t ordinaryZero = 0;
    int32_t ordinaryFar = 0;
    int32_t shadowPage = 0;
    int32_t maxToken = 0;
    CheckError(codec.Encode(ordinary, 0, 101, ordinaryZero), Codec::Error::None,
        "raw zero encode", checks);
    CheckError(codec.Encode(ordinary, 65536, 101, ordinaryFar), Codec::Error::None,
        "sparse raw page encode", checks);
    CheckError(codec.Encode(shadow, 4096, 202, shadowPage), Codec::Error::None,
        "interleaved shadow page encode", checks);

    Codec::DecodedData decoded;
    CheckError(codec.Decode(ordinaryZero, 101, decoded), Codec::Error::None,
        "ordinary decode", checks);
    Check(decoded.imageId == ordinary.imageId && decoded.rawIndex == 0,
        "decode includes image ID and raw index", checks);
    CheckError(codec.Decode(ordinaryZero, 202, decoded), Codec::Error::NotOwner,
        "private page rejects foreign owner", checks);
    CheckError(codec.Decode(ordinaryZero, 0, decoded), Codec::Error::OwnerRequired,
        "private page rejects unscoped caller", checks);
    int32_t privateMoved = 0;
    CheckError(codec.TryAddOffset(ordinaryZero, 4096, 101, privateMoved),
        Codec::Error::None, "private TryAddOffset binds a lazy page", checks);
    CheckError(codec.Decode(privateMoved, 101, decoded), Codec::Error::None,
        "private TryAddOffset result decodes", checks);
    Check(decoded.imageId == ordinary.imageId && decoded.rawIndex == 4096,
        "private TryAddOffset preserves owner and raw index", checks);
    CheckError(codec.Decode(123, 101, decoded), Codec::Error::AotDomain,
        "positive AOT-domain value is never an interpreter token", checks);
    CheckError(codec.Decode(-1, 101, decoded), Codec::Error::Sentinel,
        "negative sentinel is rejected", checks);
    CheckError(codec.Decode(-2, 101, decoded), Codec::Error::UnknownToken,
        "unknown negative token fails explicitly", checks);
    CheckError(codec.Encode(ordinary, -1, 101, ordinaryZero), Codec::Error::Sentinel,
        "raw sentinel encode is rejected", checks);
    CheckError(codec.Encode(ordinary, std::numeric_limits<int32_t>::max(), 101,
        maxToken), Codec::Error::None, "INT_MAX raw index encodes", checks);
    CheckError(codec.Encode(ordinary, int64_t(1) << 31, 101, shadowPage),
        Codec::Error::RawOutOfRange, "raw upper bound is checked", checks);

    int32_t moved = 0;
    CheckError(codec.TryAddOffset(maxToken, 1, 101, moved), Codec::Error::RawOutOfRange,
        "INT_MAX offset rejects raw overflow", checks);
    CheckError(codec.TryAddOffset(ordinaryFar, std::numeric_limits<int64_t>::max(),
        101, moved), Codec::Error::ArithmeticOverflow,
        "arbitrary positive int64 offset checks overflow", checks);
    CheckError(codec.TryAddOffset(ordinaryFar, std::numeric_limits<int64_t>::min(),
        101, moved), Codec::Error::RawOutOfRange,
        "arbitrary negative int64 offset checks domain", checks);

    int64_t difference = 0;
    CheckError(codec.RawDifference(ordinaryFar, ordinaryZero, 101, difference),
        Codec::Error::None, "same-image raw difference", checks);
    Check(difference == 65536, "raw difference uses decoded indices", checks);
    CheckError(codec.RawDifference(ordinaryFar, shadowPage, 101, difference),
        Codec::Error::NotOwner, "foreign private page is rejected before subtraction", checks);
}

void TokenImageIdentity(uint64_t& checks)
{
    Codec codec(8, 8);
    Codec::Reservation privateImage;
    CheckError(codec.Reserve(1101, 2, privateImage), Codec::Error::None,
        "token identity private reservation", checks);
    int32_t privateToken = 0;
    CheckError(codec.Encode(privateImage, 0, 1101, privateToken), Codec::Error::None,
        "token identity private binding", checks);

    uint32_t imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(privateToken, imageId), Codec::Error::None,
        "private token identity is available without caller", checks);
    Check(imageId == privateImage.imageId, "private token identity matches reservation", checks);
    Codec::DecodedData decoded;
    decoded.imageId = 77;
    decoded.rawIndex = 88;
    CheckError(codec.Decode(privateToken, 0, decoded), Codec::Error::OwnerRequired,
        "identity lookup does not bypass private Decode authorization", checks);
    Check(decoded.imageId == 77 && decoded.rawIndex == 88,
        "private Decode error leaves output unchanged", checks);

    CheckError(codec.Finalize(privateImage, 1101, 1), Codec::Error::None,
        "token identity publication finalization", checks);
    CheckError(codec.Publish(privateImage), Codec::Error::None,
        "token identity publication", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(privateToken, imageId), Codec::Error::None,
        "published token identity", checks);
    Check(imageId == privateImage.imageId, "published identity remains stable", checks);

    const int32_t unboundToken = static_cast<int32_t>(Codec::kEncodedBase + Codec::kPageSize);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(unboundToken, imageId), Codec::Error::UnknownToken,
        "well-formed unbound token is unknown", checks);
    Check(imageId == 0xC001D00Du, "unknown token leaves identity unchanged", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(-2, imageId), Codec::Error::UnknownToken,
        "unknown negative token identity fails", checks);
    Check(imageId == 0xC001D00Du, "unknown negative leaves identity unchanged", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(-1, imageId), Codec::Error::Sentinel,
        "sentinel token identity fails", checks);
    Check(imageId == 0xC001D00Du, "sentinel leaves identity unchanged", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(123, imageId), Codec::Error::AotDomain,
        "AOT-domain token identity fails", checks);
    Check(imageId == 0xC001D00Du, "AOT-domain leaves identity unchanged", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(static_cast<int32_t>(Codec::kEncodedLast + 1u), imageId),
        Codec::Error::UnknownToken, "out-of-range encoded token identity fails", checks);
    Check(imageId == 0xC001D00Du, "out-of-range leaves identity unchanged", checks);

    Codec::Reservation aborted;
    CheckError(codec.Reserve(1102, 1, aborted), Codec::Error::None,
        "aborted token identity reservation", checks);
    int32_t abortedToken = 0;
    CheckError(codec.Encode(aborted, 4096, 1102, abortedToken), Codec::Error::None,
        "aborted token identity binding", checks);
    CheckError(codec.Abort(aborted), Codec::Error::None,
        "aborted token identity lifecycle", checks);
    imageId = 0xC001D00Du;
    CheckError(codec.GetTokenImageId(abortedToken, imageId), Codec::Error::InvalidState,
        "aborted token identity follows Decode lifecycle", checks);
    Check(imageId == 0xC001D00Du, "aborted identity leaves output unchanged", checks);
}

void FinalizationAccounting(uint64_t& checks)
{
    Codec empty(8, 8);
    Codec::Reservation emptyImage;
    CheckError(empty.Reserve(250, 1, emptyImage), Codec::Error::None,
        "empty footprint reservation", checks);
    Codec::FootprintStats emptyFootprint = {0, 0, 0, 0, false};
    CheckError(empty.Finalize(emptyImage, 250, std::numeric_limits<uint64_t>::max()),
        Codec::Error::InvalidFootprint, "footprint above raw domain is rejected", checks);
    CheckError(empty.Finalize(emptyImage, 250, 0), Codec::Error::None,
        "empty footprint finalizes", checks);
    CheckError(empty.GetFootprintStats(emptyImage, emptyFootprint), Codec::Error::None,
        "empty footprint stats", checks);
    Check(emptyFootprint.sealed && emptyFootprint.lowEnd == 0 &&
        emptyFootprint.requiredPages == 0 && emptyFootprint.chargedPages == 1,
        "empty footprint has zero future pages and retained charge", checks);
    int32_t emptyToken = 0;
    CheckError(empty.Encode(emptyImage, 0, 250, emptyToken),
        Codec::Error::FootprintViolation, "empty sealed footprint rejects expansion", checks);
    CheckError(empty.Publish(emptyImage), Codec::Error::None,
        "empty sealed image publishes", checks);

    Codec overlap(8, 8);
    Codec::Reservation overlapImage;
    CheckError(overlap.Reserve(251, 2, overlapImage), Codec::Error::None,
        "sparse overlap reservation", checks);
    int32_t highToken = 0;
    CheckError(overlap.Encode(overlapImage, 16 * 4096, 251, highToken), Codec::Error::None,
        "high sparse page binds before finalization", checks);
    int32_t overlappingPage = 0;
    CheckError(overlap.Encode(overlapImage, 4096, 251, overlappingPage), Codec::Error::None,
        "low sparse page binds before finalization", checks);
    const Codec::Stats beforeFinalize = overlap.GetStats();
    Codec::FootprintStats footprint = {0, 0, 0, 0, false};
    CheckError(overlap.Finalize(overlapImage, 251, 8193), Codec::Error::None,
        "low range and high sparse page union finalizes", checks);
    CheckError(overlap.GetFootprintStats(overlapImage, footprint), Codec::Error::None,
        "union footprint stats", checks);
    Check(footprint.lowEnd == 8193 && footprint.requiredPages == 4 &&
        footprint.chargedPages == 4 && footprint.mappedPages == 2,
        "overlap counts pages zero one two and sixteen once", checks);
    Check(overlap.GetStats().reservedPages == beforeFinalize.reservedPages + 2,
        "finalization charges only missing union pages", checks);
    int32_t existingHighOffset = 0;
    CheckError(overlap.Encode(overlapImage, 16 * 4096 + 1, 251, existingHighOffset),
        Codec::Error::None, "sealed image retains existing sparse page access", checks);
    int32_t lowLast = 0;
    CheckError(overlap.Encode(overlapImage, 8192, 251, lowLast), Codec::Error::None,
        "sealed low range admits endpoint below lowEnd", checks);
    int32_t outOfFootprint = 0;
    CheckError(overlap.Encode(overlapImage, 12288, 251, outOfFootprint),
        Codec::Error::FootprintViolation, "sealed footprint rejects new high page", checks);
    CheckError(overlap.GrantPages(overlapImage, 251, 1), Codec::Error::InvalidState,
        "sealed private growth grant is rejected", checks);
    CheckError(overlap.Finalize(overlapImage, 251, 8193), Codec::Error::AlreadyFinalized,
        "sealed footprint cannot be reopened", checks);
    CheckError(overlap.Publish(overlapImage), Codec::Error::None,
        "finalized sparse image publishes", checks);

    Codec endpoint(8, 2);
    Codec::Reservation endpointImage;
    CheckError(endpoint.Reserve(252, 1, endpointImage), Codec::Error::None,
        "endpoint reservation", checks);
    CheckError(endpoint.Finalize(endpointImage, 252, 4096), Codec::Error::None,
        "page-aligned low endpoint finalizes", checks);
    int32_t endpointToken = 0;
    CheckError(endpoint.Encode(endpointImage, 4095, 252, endpointToken), Codec::Error::None,
        "raw value below endpoint is admitted", checks);
    CheckError(endpoint.Encode(endpointImage, 4096, 252, endpointToken),
        Codec::Error::FootprintViolation, "raw endpoint is excluded", checks);

    Codec insufficient(8, 3);
    Codec::Reservation insufficientImage;
    CheckError(insufficient.Reserve(253, 1, insufficientImage), Codec::Error::None,
        "insufficient footprint reservation", checks);
    CheckError(insufficient.Encode(insufficientImage, 16 * 4096, 253, highToken),
        Codec::Error::None, "insufficient footprint sparse page", checks);
    const Codec::Stats beforeFailure = insufficient.GetStats();
    CheckError(insufficient.Finalize(insufficientImage, 253, 8193), Codec::Error::PageLimit,
        "insufficient finalization ceiling rejects", checks);
    CheckError(insufficient.GetFootprintStats(insufficientImage, footprint), Codec::Error::None,
        "failed finalization stats remain readable", checks);
    const Codec::Stats afterFailure = insufficient.GetStats();
    Check(!footprint.sealed && footprint.requiredPages == 0 &&
        afterFailure.reservedPages == beforeFailure.reservedPages &&
        afterFailure.nextPageSlot == beforeFailure.nextPageSlot,
        "failed finalization leaves ledger and seal unchanged", checks);
    CheckError(insufficient.Publish(insufficientImage), Codec::Error::Unfinalized,
        "failed finalization blocks publication", checks);
    CheckError(insufficient.GrantPages(insufficientImage, 253, 1), Codec::Error::None,
        "unsealed image retains private growth after failed finalize", checks);
}

void SealedFootprintBoundaries(uint64_t& checks)
{
    const uint64_t ends[] = {0, 1, 4095, 4096, 4097};
    for (size_t i = 0; i < sizeof(ends) / sizeof(ends[0]); ++i)
    {
        const uint64_t lowEnd = ends[i];
        Codec codec(4, 4);
        Codec::Reservation image;
        const uint64_t owner = 1300 + i;
        CheckError(codec.Reserve(owner, 2, image), Codec::Error::None,
            "partial footprint reservation", checks);
        CheckError(codec.Finalize(image, owner, lowEnd), Codec::Error::None,
            "partial footprint finalizes", checks);
        int32_t token = 0;
        if (lowEnd == 0)
        {
            CheckError(codec.Encode(image, 0, owner, token),
                Codec::Error::FootprintViolation,
                "empty partial footprint rejects its first value", checks);
        }
        else
        {
            CheckError(codec.Encode(image, static_cast<int64_t>(lowEnd - 1), owner, token),
                Codec::Error::None, "partial footprint admits its final value", checks);
            CheckError(codec.Encode(image, static_cast<int64_t>(lowEnd), owner, token),
                Codec::Error::FootprintViolation,
                "partial footprint rejects its half-open endpoint", checks);
        }
    }

    // A page lazily bound after sealing never widens the exact lowEnd.  This
    // is the call order which previously returned an existing binding before
    // checking the sealed footprint.
    Codec lazy(4, 4);
    Codec::Reservation lazyImage;
    CheckError(lazy.Reserve(1400, 2, lazyImage), Codec::Error::None,
        "lazy partial footprint reservation", checks);
    CheckError(lazy.Finalize(lazyImage, 1400, 1), Codec::Error::None,
        "lazy partial footprint finalizes", checks);
    int32_t lazyToken = 0;
    CheckError(lazy.Encode(lazyImage, 0, 1400, lazyToken), Codec::Error::None,
        "lazy footprint binds its admitted value", checks);
    CheckError(lazy.Encode(lazyImage, 1, 1400, lazyToken),
        Codec::Error::FootprintViolation,
        "lazy binding does not round the sealed endpoint", checks);
    CheckError(lazy.Encode(lazyImage, 4095, 1400, lazyToken),
        Codec::Error::FootprintViolation,
        "same lazy page rejects every value beyond the endpoint", checks);

    // A sparse page mapped before sealing remains admitted as a whole page,
    // regardless of whether the low range is empty or partial.
    Codec sparse(4, 4);
    Codec::Reservation sparseImage;
    CheckError(sparse.Reserve(1401, 2, sparseImage), Codec::Error::None,
        "preseal sparse footprint reservation", checks);
    int32_t sparseToken = 0;
    CheckError(sparse.Encode(sparseImage, 16 * 4096, 1401, sparseToken),
        Codec::Error::None, "preseal sparse page binds", checks);
    CheckError(sparse.Finalize(sparseImage, 1401, 1), Codec::Error::None,
        "preseal sparse footprint finalizes", checks);
    CheckError(sparse.Encode(sparseImage, 16 * 4096 + 4095, 1401, sparseToken),
        Codec::Error::None, "preseal sparse page remains admitted", checks);
    CheckError(sparse.Encode(sparseImage, 1, 1401, sparseToken),
        Codec::Error::FootprintViolation,
        "preseal sparse admission does not widen the low range", checks);
}

void FinalizeEncodeRace(uint64_t& checks)
{
    // Both serializations are legal: Finalize first rejects a new page above
    // lowEnd, while Encode first admits that preseal page and Finalize unions
    // it into the sealed sparse footprint.
    Codec finalizeFirst(4, 4);
    Codec::Reservation finalizeFirstImage;
    CheckError(finalizeFirst.Reserve(1500, 2, finalizeFirstImage), Codec::Error::None,
        "finalize-first ordering reservation", checks);
    CheckError(finalizeFirst.Finalize(finalizeFirstImage, 1500, 1),
        Codec::Error::None, "finalize-first ordering finalizes", checks);
    int32_t orderingToken = 0;
    CheckError(finalizeFirst.Encode(finalizeFirstImage, 4096, 1500, orderingToken),
        Codec::Error::FootprintViolation,
        "finalize-first ordering rejects expansion", checks);

    Codec encodeFirst(4, 4);
    Codec::Reservation encodeFirstImage;
    CheckError(encodeFirst.Reserve(1501, 2, encodeFirstImage), Codec::Error::None,
        "encode-first ordering reservation", checks);
    CheckError(encodeFirst.Encode(encodeFirstImage, 4096, 1501, orderingToken),
        Codec::Error::None, "encode-first ordering binds sparse page", checks);
    CheckError(encodeFirst.Finalize(encodeFirstImage, 1501, 1),
        Codec::Error::None, "encode-first ordering unions sparse page", checks);

    Codec race(4, 4);
    Codec::Reservation raceImage;
    CheckError(race.Reserve(1502, 2, raceImage), Codec::Error::None,
        "finalize-encode race reservation", checks);
    std::atomic<uint8_t> start(0);
    std::atomic<int> finalizeResult(static_cast<int>(Codec::Error::InvalidState));
    std::atomic<int> encodeResult(static_cast<int>(Codec::Error::InvalidState));
    std::thread finalizer([&race, &raceImage, &start, &finalizeResult]() {
        while (start.load(std::memory_order_acquire) == 0)
            std::this_thread::yield();
        finalizeResult.store(static_cast<int>(race.Finalize(raceImage, 1502, 1)),
            std::memory_order_release);
    });
    std::thread encoder([&race, &raceImage, &start, &encodeResult]() {
        while (start.load(std::memory_order_acquire) == 0)
            std::this_thread::yield();
        int32_t token = 0;
        encodeResult.store(static_cast<int>(race.Encode(raceImage, 4096, 1502, token)),
            std::memory_order_release);
    });
    start.store(1, std::memory_order_release);
    finalizer.join();
    encoder.join();
    const Codec::Error finalized = static_cast<Codec::Error>(
        finalizeResult.load(std::memory_order_acquire));
    const Codec::Error encoded = static_cast<Codec::Error>(
        encodeResult.load(std::memory_order_acquire));
    Check(finalized == Codec::Error::None &&
        (encoded == Codec::Error::None || encoded == Codec::Error::FootprintViolation),
        "finalize-encode race has a valid serialized outcome", checks);
    CheckError(race.Publish(raceImage), Codec::Error::None,
        "serialized finalize-encode race publishes", checks);
}

void LifecycleAndGrowth(uint64_t& checks)
{
    Codec codec(8, 16);
    Codec::Reservation privateImage;
    CheckError(codec.Reserve(303, 1, privateImage), Codec::Error::None,
        "private lifecycle reservation", checks);
    int32_t first = 0;
    CheckError(codec.Encode(privateImage, 0, 303, first), Codec::Error::None,
        "private lazy binding", checks);
    Codec::DecodedData decoded;
    CheckError(codec.Decode(first, 303, decoded), Codec::Error::None,
        "private owner reads before publication", checks);
    CheckError(codec.GrantPages(privateImage, 303, 2), Codec::Error::None,
        "private owner reserves lazy growth", checks);
    CheckError(codec.Finalize(privateImage, 303, 12288), Codec::Error::None,
        "private image finalizes complete low footprint", checks);
    CheckError(codec.GrantPages(privateImage, 303, 1), Codec::Error::InvalidState,
        "sealed private growth is rejected", checks);
    CheckError(codec.Publish(privateImage), Codec::Error::None,
        "single image publication transition", checks);
    CheckError(codec.Decode(first, 0, decoded), Codec::Error::None,
        "published image is visible to unscoped caller", checks);
    int32_t publishedMoved = 0;
    CheckError(codec.TryAddOffset(first, 4096, 404, publishedMoved),
        Codec::Error::None, "published TryAddOffset binds a lazy page", checks);
    CheckError(codec.Decode(publishedMoved, 404, decoded), Codec::Error::None,
        "published TryAddOffset result decodes", checks);
    Check(decoded.imageId == privateImage.imageId && decoded.rawIndex == 4096,
        "published TryAddOffset preserves image and raw index", checks);
    int32_t second = 0;
    int32_t third = 0;
    CheckError(codec.Encode(privateImage, 4096, 404, second), Codec::Error::None,
        "published foreign caller binds first growth page", checks);
    CheckError(codec.Encode(privateImage, 8192, 404, third), Codec::Error::None,
        "published foreign caller binds second growth page", checks);
    CheckError(codec.Abort(privateImage), Codec::Error::InvalidState,
        "published image cannot abort", checks);
    CheckError(codec.Decode(second, 404, decoded), Codec::Error::None,
        "published growth remains readable", checks);

    Codec::Reservation aborted;
    CheckError(codec.Reserve(505, 1, aborted), Codec::Error::None,
        "abort reservation", checks);
    int32_t abortedToken = 0;
    CheckError(codec.Encode(aborted, 0, 505, abortedToken), Codec::Error::None,
        "abort page binding", checks);
    CheckError(codec.Finalize(aborted, 505, 1), Codec::Error::None,
        "abort image finalization", checks);
    const Codec::Stats beforeAbort = codec.GetStats();
    CheckError(codec.Abort(aborted), Codec::Error::None, "private abort", checks);
    CheckError(codec.Decode(abortedToken, 505, decoded), Codec::Error::InvalidState,
        "aborted image is unreadable", checks);
    const Codec::Stats afterAbort = codec.GetStats();
    Check(afterAbort.reservedPages == beforeAbort.reservedPages &&
        afterAbort.nextPageSlot == beforeAbort.nextPageSlot,
        "abort retains credits and IDs", checks);

    Codec lazy(4, 4);
    Codec::Reservation lazyImage;
    CheckError(lazy.Reserve(606, 2, lazyImage), Codec::Error::None,
        "known-token lazy binding reservation", checks);
    CheckError(lazy.Finalize(lazyImage, 606, 8192), Codec::Error::None,
        "known-token image finalization", checks);
    CheckError(lazy.Publish(lazyImage), Codec::Error::None,
        "publish before concurrent lazy binding", checks);
    const int32_t knownFirst = static_cast<int32_t>(Codec::kEncodedBase);
    const int32_t knownSecond = static_cast<int32_t>(Codec::kEncodedBase + Codec::kPageSize);
    std::atomic<uint8_t> lazyReaderFailed(0);
    std::thread lazyReader([&lazy, &lazyReaderFailed]() {
        Codec::DecodedData local;
        for (uint32_t i = 0; i < 1000000u &&
            lazy.Decode(knownFirst, 909, local) != Codec::Error::None; ++i)
            std::this_thread::yield();
        if (lazy.Decode(knownFirst, 909, local) != Codec::Error::None)
            lazyReaderFailed.store(1, std::memory_order_release);
        for (uint32_t i = 0; i < 1000000u &&
            lazy.Decode(knownSecond, 909, local) != Codec::Error::None; ++i)
            std::this_thread::yield();
        if (lazy.Decode(knownSecond, 909, local) != Codec::Error::None)
            lazyReaderFailed.store(1, std::memory_order_release);
    });
    std::thread lazyBinder([&lazy, &lazyImage]() {
        int32_t firstToken = 0;
        int32_t secondToken = 0;
        if (lazy.Encode(lazyImage, 0, 606, firstToken) != Codec::Error::None ||
            lazy.Encode(lazyImage, 4096, 606, secondToken) != Codec::Error::None)
            std::abort();
    });
    lazyBinder.join();
    lazyReader.join();
    Check(lazyReaderFailed.load(std::memory_order_acquire) == 0,
        "known tokens observe concurrent lazy bindings", checks);
}

void PublicationConcurrency(uint64_t& checks)
{
    Codec codec(8, 8);
    Codec::Reservation image;
    CheckError(codec.Reserve(801, 2, image), Codec::Error::None,
        "publication concurrency reservation", checks);
    int32_t first = 0;
    int32_t second = 0;
    CheckError(codec.Encode(image, 0, 801, first), Codec::Error::None,
        "first private page", checks);
    CheckError(codec.Encode(image, 4096, 801, second), Codec::Error::None,
        "second private page", checks);
    CheckError(codec.Finalize(image, 801, 8192), Codec::Error::None,
        "publication image finalization", checks);

    std::atomic<uint8_t> publisherSucceeded(0);
    std::atomic<uint8_t> readerObservedPublished(0);
    std::atomic<uint8_t> impossible(0);
    std::thread publisher([&codec, &image, &publisherSucceeded]() {
        publisherSucceeded.store(codec.Publish(image) == Codec::Error::None ? 1 : 0,
            std::memory_order_release);
    });
    std::thread reader([&codec, first, second, &readerObservedPublished, &impossible]() {
        Codec::DecodedData decoded;
        for (uint32_t attempt = 0; attempt < 1000000u &&
            codec.Decode(first, 0, decoded) != Codec::Error::None; ++attempt)
            std::this_thread::yield();
        if (codec.Decode(first, 0, decoded) != Codec::Error::None)
            impossible.store(1, std::memory_order_release);
        else
        {
            readerObservedPublished.store(1, std::memory_order_release);
            if (codec.Decode(second, 0, decoded) != Codec::Error::None)
                impossible.store(1, std::memory_order_release);
        }
    });
    publisher.join();
    reader.join();
    Check(publisherSucceeded.load(std::memory_order_acquire) != 0,
        "publication succeeds atomically", checks);
    Check(readerObservedPublished.load(std::memory_order_acquire) != 0,
        "reader observes publication through a page decode", checks);
    Check(impossible.load(std::memory_order_acquire) == 0,
        "published image pages are consistently visible", checks);

    Codec race(4, 4);
    Codec::Reservation raceImage;
    CheckError(race.Reserve(803, 1, raceImage), Codec::Error::None,
        "abort race reservation", checks);
    int32_t raceToken = 0;
    CheckError(race.Encode(raceImage, 0, 803, raceToken), Codec::Error::None,
        "abort race page", checks);
    std::atomic<uint8_t> raceStarted(0);
    std::atomic<uint8_t> raceStop(0);
    std::atomic<uint8_t> raceUnexpected(0);
    std::thread raceReader([&race, raceToken, &raceStarted, &raceStop, &raceUnexpected]() {
        raceStarted.store(1, std::memory_order_release);
        Codec::DecodedData local;
        while (raceStop.load(std::memory_order_acquire) == 0)
        {
            const Codec::Error result = race.Decode(raceToken, 803, local);
            if (result != Codec::Error::None && result != Codec::Error::InvalidState)
                raceUnexpected.store(1, std::memory_order_release);
        }
    });
    while (raceStarted.load(std::memory_order_acquire) == 0)
        std::this_thread::yield();
    CheckError(race.Abort(raceImage), Codec::Error::None,
        "abort lifecycle transition", checks);
    raceStop.store(1, std::memory_order_release);
    raceReader.join();
    Check(raceUnexpected.load(std::memory_order_acquire) == 0,
        "abort racing decode has only valid outcomes", checks);
    Codec::DecodedData raceDecoded;
    CheckError(race.Decode(raceToken, 803, raceDecoded), Codec::Error::InvalidState,
        "aborted race token remains unreadable", checks);

    Codec::Reservation other;
    CheckError(codec.Reserve(802, 1, other), Codec::Error::None,
        "second image same caller test reservation", checks);
    int32_t otherToken = 0;
    CheckError(codec.Encode(other, 0, 802, otherToken), Codec::Error::None,
        "second image page", checks);
    CheckError(codec.Finalize(other, 802, 1), Codec::Error::None,
        "second image finalization", checks);
    CheckError(codec.Publish(other), Codec::Error::None,
        "second image publication", checks);
    Codec::DecodedData decoded;
    CheckError(codec.Decode(first, 909, decoded), Codec::Error::None,
        "first published image accessible to same caller", checks);
    CheckError(codec.Decode(otherToken, 909, decoded), Codec::Error::None,
        "second published image accessible to same caller", checks);
    int64_t difference = 0;
    CheckError(codec.RawDifference(first, otherToken, 0, difference),
        Codec::Error::CrossImage, "same caller cannot subtract across images", checks);
}

void ConcurrentLedgerWriters(uint64_t& checks)
{
    Codec codec(64, 64);
    const uint32_t workerCount = 8;
    Codec::Reservation reservations[workerCount * 2];
    std::atomic<uint8_t> reserveFailure[workerCount];
    for (uint32_t i = 0; i < workerCount; ++i)
        reserveFailure[i].store(0, std::memory_order_relaxed);
    std::vector<std::thread> workers;
    for (uint32_t worker = 0; worker < workerCount; ++worker)
    {
        workers.emplace_back([&codec, &reservations, &reserveFailure, worker]() {
            Codec::BatchRequest requests[2] = {
                {1000u + worker * 2u, 1u}, {1001u + worker * 2u, 1u}};
            if (codec.ReserveBatch(requests, 2, &reservations[worker * 2]) != Codec::Error::None)
                reserveFailure[worker].store(1, std::memory_order_release);
        });
    }
    for (size_t i = 0; i < workers.size(); ++i)
        workers[i].join();
    for (uint32_t i = 0; i < workerCount; ++i)
        Check(reserveFailure[i].load(std::memory_order_acquire) == 0,
            "concurrent reservation batch succeeds", checks);
    const Codec::Stats reserved = codec.GetStats();
    Check(reserved.reservationCount == workerCount * 2 && reserved.reservedPages == workerCount * 2,
        "concurrent batches charge one shared ledger", checks);
    for (uint32_t i = 0; i < workerCount * 2; ++i)
    {
        Check(reservations[i].imageId != 0, "concurrent batch assigns internal image ID", checks);
        for (uint32_t j = 0; j < i; ++j)
            Check(reservations[i].imageId != reservations[j].imageId,
                "concurrent batches assign distinct image IDs", checks);
    }

    workers.clear();
    std::atomic<uint8_t> grantFailure[workerCount];
    for (uint32_t i = 0; i < workerCount; ++i)
        grantFailure[i].store(0, std::memory_order_relaxed);
    for (uint32_t worker = 0; worker < workerCount; ++worker)
    {
        workers.emplace_back([&codec, &reservations, &grantFailure, worker]() {
            const uint32_t first = worker * 2u;
            if (codec.GrantPages(reservations[first], 1000u + worker * 2u, 1) != Codec::Error::None ||
                codec.GrantPages(reservations[first + 1u], 1001u + worker * 2u, 1) != Codec::Error::None)
                grantFailure[worker].store(1, std::memory_order_release);
        });
    }
    for (size_t i = 0; i < workers.size(); ++i)
        workers[i].join();
    for (uint32_t i = 0; i < workerCount; ++i)
        Check(grantFailure[i].load(std::memory_order_acquire) == 0,
            "concurrent growth grants succeed", checks);
    const Codec::Stats granted = codec.GetStats();
    Check(granted.reservedPages == workerCount * 4,
        "concurrent growth grants charge before binding", checks);

    Codec finalizeCodec(4, 4);
    Codec::Reservation finalizeImage;
    CheckError(finalizeCodec.Reserve(1200, 1, finalizeImage), Codec::Error::None,
        "concurrent finalization reservation", checks);
    std::atomic<uint8_t> finalizeSucceeded(0);
    std::atomic<uint8_t> finalizeAlready(0);
    workers.clear();
    for (uint32_t i = 0; i < 2; ++i)
    {
        workers.emplace_back([&finalizeCodec, &finalizeImage, &finalizeSucceeded,
            &finalizeAlready]() {
            const Codec::Error result = finalizeCodec.Finalize(finalizeImage, 1200, 1);
            if (result == Codec::Error::None)
                finalizeSucceeded.fetch_add(1, std::memory_order_acq_rel);
            else if (result == Codec::Error::AlreadyFinalized)
                finalizeAlready.fetch_add(1, std::memory_order_acq_rel);
            else
                std::abort();
        });
    }
    for (size_t i = 0; i < workers.size(); ++i)
        workers[i].join();
    Check(finalizeSucceeded.load(std::memory_order_acquire) == 1 &&
        finalizeAlready.load(std::memory_order_acquire) == 1,
        "concurrent finalization has one atomic winner", checks);
    CheckError(finalizeCodec.Publish(finalizeImage), Codec::Error::None,
        "concurrently finalized image publishes", checks);
}

void ImageBoundariesAndCapacity(uint64_t& checks)
{
    Codec codec(Codec::kMaxImageCount, Codec::kMaxImageCount);
    Codec::Reservation reservation;
    Codec::Stats at8191 = {0, 0, 0, 0, 0};
    Codec::Stats at8192 = {0, 0, 0, 0, 0};
    for (uint32_t i = 1; i <= Codec::kMaxImageCount; ++i)
    {
        CheckError(codec.Reserve((i & 1u) == 0 ? 900 : 901, 1, reservation),
            Codec::Error::None, "cumulative image reservation", checks);
        if (i == 8191)
            at8191 = codec.GetStats();
        if (i == 8192)
            at8192 = codec.GetStats();
    }
    Check(at8191.reservationCount == 8191 && at8191.reservedPages == 8191,
        "8191 image boundary", checks);
    Check(at8192.reservationCount == 8192 && at8192.reservedPages == 8192,
        "8192 image boundary", checks);
    const Codec::Stats before = codec.GetStats();
    CheckError(codec.Reserve(900, 1, reservation), Codec::Error::ImageLimit,
        "8193 image boundary rejects", checks);
    const Codec::Stats after = codec.GetStats();
    Check(after.reservationCount == before.reservationCount &&
        after.nextImageId == before.nextImageId &&
        after.nextPageSlot == before.nextPageSlot,
        "8193 rejection is atomic", checks);

    Codec capacity(1, Codec::kMaxChargedPages);
    Check(capacity.IsValid() && capacity.MaxChargedPages() == 393215,
        "25 percent free charged ceiling is fixed", checks);
    CheckError(capacity.Reserve(1, Codec::kMaxChargedPages, reservation),
        Codec::Error::None, "charged ceiling is admitted", checks);
    const Codec::Stats charged = capacity.GetStats();
    Check(charged.reservedPages == Codec::kMaxChargedPages &&
        Codec::kUsablePageCount - charged.reservedPages >= Codec::kUsablePageCount / 4u,
        "charged ceiling retains at least 25 percent free", checks);
}

void DecodePerformance(uint64_t& checks)
{
    Codec codec(1, 1);
    Codec::Reservation reservation;
    CheckError(codec.Reserve(777, 1, reservation), Codec::Error::None,
        "benchmark image reservation", checks);
    int32_t sparseTokens[256];
    uint32_t legacyTokens[256];
    for (uint32_t index = 0; index < 256; ++index)
    {
        CheckError(codec.Encode(reservation, index, 777, sparseTokens[index]),
            Codec::Error::None, "benchmark sparse token", checks);
        // Profile 1's first usable kind-A slot is image index 64. Its hot
        // decode is the retained arithmetic reference, not a compatibility
        // path in the profile-2 runtime.
        legacyTokens[index] = (UINT32_C(64) << 22) | index;
    }
    CheckError(codec.Finalize(reservation, 777, 256), Codec::Error::None,
        "benchmark finalization", checks);
    CheckError(codec.Publish(reservation), Codec::Error::None,
        "benchmark publication", checks);

    const uint32_t iterations = 5000000;
    uint64_t sparseChecksum = 0;
    auto sparseStart = std::chrono::steady_clock::now();
    for (uint32_t iteration = 0; iteration < iterations; ++iteration)
    {
        Codec::DecodedData decoded;
        if (codec.Decode(sparseTokens[iteration & 255u], 777, decoded) != Codec::Error::None)
            std::abort();
        sparseChecksum += decoded.rawIndex;
    }
    const uint64_t sparseNanoseconds = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::steady_clock::now() - sparseStart).count());

    uint64_t legacyChecksum = 0;
    auto legacyStart = std::chrono::steady_clock::now();
    for (uint32_t iteration = 0; iteration < iterations; ++iteration)
    {
        const uint32_t token = legacyTokens[iteration & 255u];
        const uint32_t raw = token & UINT32_C(0x0fffffff);
        legacyChecksum += raw;
    }
    const uint64_t legacyNanoseconds = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::steady_clock::now() - legacyStart).count());
    Check(sparseNanoseconds > 0 && legacyNanoseconds > 0 &&
        sparseChecksum == legacyChecksum, "decode benchmark checksums and timers", checks);
    std::cout << "decode_iterations=" << iterations
              << " sparse_nanoseconds=" << sparseNanoseconds
              << " legacy_profile1_nanoseconds=" << legacyNanoseconds
              << " checksum=" << sparseChecksum << std::endl;
}

} // namespace

int main()
{
    uint64_t checks = 0;
    InvalidLimitsAndOwnerZero(checks);
    AtomicBatchAndInternalIds(checks);
    ArithmeticAndDomains(checks);
    TokenImageIdentity(checks);
    FinalizationAccounting(checks);
    SealedFootprintBoundaries(checks);
    FinalizeEncodeRace(checks);
    LifecycleAndGrowth(checks);
    PublicationConcurrency(checks);
    ConcurrentLedgerWriters(checks);
    ImageBoundariesAndCapacity(checks);
    DecodePerformance(checks);
    std::cout << "checks=" << checks << " failures=0" << std::endl;
    return 0;
}
