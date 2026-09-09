#include "metadata/InterpreterMetadataIndexCodec.h"
#include "metadata/InterpreterMetadataRange.h"

#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <limits>

namespace
{
using Codec = hybridclr::metadata::InterpreterMetadataIndexCodec;
using Range = hybridclr::metadata::InterpreterMetadataRange;

size_t checks = 0;

void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "r01b index range check failed: %s\n", message);
        std::exit(1);
    }
}

struct SparseDecoder
{
    const Codec* codec;
    uint64_t caller;

    Range::DecodedIndex operator()(uint32_t encoded) const
    {
        Codec::DecodedData decoded;
        const Codec::Error error = codec->Decode(static_cast<int32_t>(encoded), caller, decoded);
        if (error != Codec::Error::None)
            return Range::DecodedIndex();
        return Range::DecodedIndex(true, decoded.imageId,
            static_cast<uint64_t>(decoded.rawIndex));
    }
};

void CheckError(Range::Error actual, Range::Error expected, const char* message)
{
    Check(actual == expected, message);
}

void Encode(Codec& codec, const Codec::Reservation& reservation,
    int64_t raw, uint64_t owner, int32_t& token)
{
    Check(codec.Encode(reservation, raw, owner, token) == Codec::Error::None,
        "sparse fixture encoding succeeds");
}

void TestSparseRanges()
{
    Codec codec(8, 16);
    Codec::Reservation first;
    Codec::Reservation second;
    Check(codec.Reserve(101, 5, first) == Codec::Error::None, "first sparse image reserved");
    Check(codec.Reserve(202, 1, second) == Codec::Error::None, "second sparse image reserved");

    int32_t firstBegin = 0;
    int32_t foreign = 0;
    int32_t firstEnd = 0;
    int32_t firstOnePast = 0;
    Encode(codec, first, 0, 101, firstBegin);
    Encode(codec, second, Codec::kPageSize, 202, foreign);
    Encode(codec, first, 3 * Codec::kPageSize, 101, firstEnd);
    Encode(codec, first, 4 * Codec::kPageSize, 101, firstOnePast);
    Check(codec.Finalize(first, 101, 4 * Codec::kPageSize + 1) == Codec::Error::None,
        "first sparse image footprint sealed");
    Check(codec.Finalize(second, 202, Codec::kPageSize + 1) == Codec::Error::None,
        "second sparse image footprint sealed");
    Check(codec.Publish(first) == Codec::Error::None, "first sparse image published");
    Check(codec.Publish(second) == Codec::Error::None, "second sparse image published");

    const SparseDecoder decoder = {&codec, 0};
    const Codec::Stats beforeReads = codec.GetStats();
    uint32_t begin = 0;
    uint32_t end = 0;
    uint32_t count = 0;
    CheckError(Range::DecodeRange(firstBegin, firstEnd, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::None, "noncontiguous sparse pages decode as one raw range");
    Check(begin == 0 && end == 3 * Codec::kPageSize && count == 3 * Codec::kPageSize,
        "sparse range preserves raw endpoints");
    CheckError(Range::DecodeRange(firstBegin, firstOnePast, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::None, "same-image one-past endpoint is allowed");
    Check(end == 4 * Codec::kPageSize && count == 4 * Codec::kPageSize,
        "one-past endpoint remains raw");
    CheckError(Range::DecodeRange(firstEnd, firstBegin, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::Reversed, "reversed endpoints are rejected");
    CheckError(Range::DecodeRange(firstBegin, foreign, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::ForeignOwner, "foreign endpoint is rejected");
    CheckError(Range::DecodeRange(firstBegin, firstBegin, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::None, "empty range is representable");
    Check(count == 0, "empty range has zero count");
    CheckError(Range::DecodeRange(static_cast<uint32_t>(-1), firstEnd, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::InvalidEncoding, "sentinel endpoint is rejected");
    CheckError(Range::DecodeRange(static_cast<uint32_t>(-2), firstEnd, first.imageId,
        4 * Codec::kPageSize, std::numeric_limits<uint16_t>::max(), decoder,
        begin, end, count), Range::Error::InvalidEncoding, "unknown endpoint is rejected");
    const Codec::Stats afterReads = codec.GetStats();
    Check(afterReads.reservedPages == beforeReads.reservedPages &&
        afterReads.mappedPages == beforeReads.mappedPages &&
        afterReads.reservationCount == beforeReads.reservationCount &&
        afterReads.nextImageId == beforeReads.nextImageId &&
        afterReads.nextPageSlot == beforeReads.nextPageSlot,
        "range and lookup reads do not mutate sparse codec counters");
}

void TestOffsetsAndBounds()
{
    Codec codec(4, 4);
    Codec::Reservation reservation;
    Check(codec.Reserve(303, 1, reservation) == Codec::Error::None, "offset image reserved");
    int32_t base = 0;
    int32_t nextPage = 0;
    Encode(codec, reservation, 4095, 303, base);
    Check(codec.GrantPages(reservation, 303, 1) == Codec::Error::None, "offset second page granted");
    Encode(codec, reservation, 4096, 303, nextPage);
    Check(codec.Finalize(reservation, 303, Codec::kPageSize + 1) == Codec::Error::None,
        "offset image footprint sealed");
    Check(codec.Publish(reservation) == Codec::Error::None, "offset image published");
    const SparseDecoder decoder = {&codec, 0};
    uint32_t raw = 0;
    CheckError(Range::ResolveOffset(base, reservation.imageId, 0, 4096, decoder, raw),
        Range::Error::None, "offset base resolves");
    Check(raw == 4095, "offset base is decoded before addition");
    CheckError(Range::ResolveOffset(nextPage, reservation.imageId, 0, 8192, decoder, raw),
        Range::Error::None, "cross-page offset resolves from actual sparse token");
    Check(raw == 4096, "cross-page offset preserves decoded raw index");
    const Codec::Stats beforeCrossing = codec.GetStats();
    CheckError(Range::ResolveOffset(base, reservation.imageId, 1, 8192, decoder, raw),
        Range::Error::None, "nonzero offset crosses raw page boundary");
    Check(raw == 4096, "4095 plus one resolves to 4096");
    const Codec::Stats afterCrossing = codec.GetStats();
    Check(beforeCrossing.reservedPages == afterCrossing.reservedPages &&
        beforeCrossing.mappedPages == afterCrossing.mappedPages,
        "cross-page lookup does not allocate or charge codec pages");
    CheckError(Range::ResolveOffset(base, reservation.imageId, 1, 4096, decoder, raw),
        Range::Error::OutOfRange, "one-past index is rejected for indexing");
    CheckError(Range::ResolveOffset(base, reservation.imageId + 1, 0, 4096, decoder, raw),
        Range::Error::ForeignOwner, "offset foreign owner is rejected");
    CheckError(Range::CountRawRange(10, 10, 100, raw), Range::Error::None,
        "empty raw range is ordered");
    CheckError(Range::CountRawRange(10, 9, 100, raw), Range::Error::Reversed,
        "raw reversed range is rejected");
    CheckError(Range::CountRawRange(0, 100, 99, raw), Range::Error::CountOverflow,
        "retained count width is checked");

    struct InvalidDecoder
    {
        Range::DecodedIndex operator()(uint32_t) const
        {
            return Range::DecodedIndex(true, 303,
                static_cast<uint64_t>(std::numeric_limits<uint32_t>::max()) + 1u);
        }
    } invalidDecoder;
    CheckError(Range::DecodeEndpoint(0, 303, std::numeric_limits<uint32_t>::max(),
        invalidDecoder, raw), Range::Error::OutOfRange, "raw decode overflow is rejected");

    CheckError(Range::ValidateCustomAttributeLayout(0, 0, 0, 0, raw),
        Range::Error::InvalidArgument, "zero custom attribute range is rejected");
    CheckError(Range::ValidateCustomAttributeLayout(0, 1023, 1023, 0, raw),
        Range::Error::None, "1023 custom attributes fit writer arithmetic");
    Check(Range::CompressedUint32Size(1023) == 2, "1023 count uses two-byte prefix");
    Check(raw == 1023u * sizeof(int32_t), "1023 method index area size");
    CheckError(Range::ValidateCustomAttributeLayout(0, 1024, 1024, 0, raw),
        Range::Error::None, "1024 custom attributes remain valid");
    Check(Range::CompressedUint32Size(1024) == 2, "1024 count uses two-byte prefix");
    Check(raw == 1024u * sizeof(int32_t), "1024 method index area size");
    const uint32_t tooMany = static_cast<uint32_t>(std::numeric_limits<int32_t>::max() / sizeof(int32_t)) + 1u;
    CheckError(Range::ValidateCustomAttributeLayout(0, tooMany, tooMany, 0, raw),
        Range::Error::OutOfRange, "method index area signed overflow is rejected");
    const uint32_t prefixOverflow = tooMany - 1u;
    CheckError(Range::ValidateCustomAttributeLayout(0, prefixOverflow, prefixOverflow, 0, raw),
        Range::Error::OutOfRange, "compressed prefix overflows otherwise fitting method index area");
}
}

int main()
{
    TestSparseRanges();
    TestOffsetsAndBounds();
    std::printf("r01b_index_range_checks=%zu PASS\n", checks);
    return 0;
}
