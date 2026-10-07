#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <limits>
#include <stdexcept>
#include <string>

#include "metadata/BlobReader.h"
#include "metadata/RawImageBase.h"

namespace il2cpp
{
namespace utils
{
    void* Memory::Malloc(size_t size) { return std::malloc(size); }
    void Memory::Free(void* memory) { std::free(memory); }
    void* Memory::Calloc(size_t count, size_t size) { return std::calloc(count, size); }
}
}

namespace il2cpp
{
namespace vm
{
    Il2CppString* String::Empty() { return nullptr; }
    Il2CppString* String::NewUtf16(const Il2CppChar*, int32_t) { return nullptr; }

    struct ProbeException : std::exception
    {
        const char* what() const noexcept override { return "controlled execution-engine exception"; }
    };

    Il2CppException* Exception::GetExecutionEngineException(const char*) { return nullptr; }
    void Exception::Raise(Il2CppException*, MethodInfo*) { throw ProbeException(); }
}
}

namespace hybridclr
{
    void LogPanic(const char*) { std::abort(); }
}

void il2cpp_assert(const char*, const char*, unsigned int)
{
    std::abort();
}

using hybridclr::byte;
using hybridclr::metadata::BlobReader;
using hybridclr::metadata::RawImageBase;
using hybridclr::metadata::LoadImageErrorCode;

class ProbeRawImage : public RawImageBase
{
public:
    void SetUserStream(const byte* data, uint32_t size)
    {
        _streamUS.data = data;
        _streamUS.size = size;
    }

    void SetBlobStream(const byte* data, uint32_t size)
    {
        _streamBlobHeap.data = data;
        _streamBlobHeap.size = size;
    }

    void SetStringStream(const byte* data, uint32_t size)
    {
        _streamStringHeap.data = data;
        _streamStringHeap.size = size;
    }

protected:
    LoadImageErrorCode LoadCLIHeader(uint32_t&, uint32_t&, uint32_t&) override
    {
        return LoadImageErrorCode::BAD_IMAGE;
    }
};

static void Check(bool condition, const char* detail)
{
    if (!condition)
    {
        std::fprintf(stderr, "blob-reader check failed: %s\n", detail);
        std::abort();
    }
}

static int ValidProbe()
{
    const byte bytes[15] = { 0xf1, 0x80, 0xa5, 0xc3, 0xe7, 0x99, 0xd4, 0xfe,
                             0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77 };
    BlobReader reader(bytes, sizeof(bytes));
    Check(reader.ReadByte() == 0xf1, "ReadByte");
    Check(reader.Read16() == 0xa580u, "Read16");
    Check(reader.Read32() == 0xd499e7c3u, "Read32");
    Check(reader.Read64() == 0x77665544332211feull, "Read64");
    Check(reader.IsEmpty(), "fixed reads consume exact length");

    uint32_t lengthSize = 0;
    const byte one[] = { 0x7f };
    Check(BlobReader::ReadCompressedUint32(one, lengthSize) == 0x7fu && lengthSize == 1, "compressed 1-byte");
    const byte two[] = { 0x80, 0x80 };
    Check(BlobReader::ReadCompressedUint32(two, lengthSize) == 0x80u && lengthSize == 2, "compressed 2-byte");
    const byte four[] = { 0xc0, 0x00, 0x40, 0x00 };
    Check(BlobReader::ReadCompressedUint32(four, lengthSize) == 0x4000u && lengthSize == 4, "compressed 4-byte");

    const byte blob[] = { 0x03, 0xa1, 0xb2, 0xc3 };
    BlobReader decoded = RawImageBase::DecodeBlob(blob, sizeof(blob));
    Check(decoded.GetLength() == 3 && decoded.GetData()[0] == 0xa1 && decoded.GetData()[2] == 0xc3,
          "RawImageBase::DecodeBlob valid prefix");

    const byte userString[] = { 0x01, 0x41 };
    const byte blobStream[] = { 0x02, 0xa1, 0xb2 };
    ProbeRawImage image;
    image.SetUserStream(userString, sizeof(userString));
    Check(image.GetStringHeapSize() == 0, "initial string heap size");
    Check(image.GetUserStringBlogByIndex(0) == nullptr, "valid user string entry");
    image.SetBlobStream(blobStream, sizeof(blobStream));
    Check(image.GetBlobFromRawIndex(0) == blobStream, "valid blob entry");
    BlobReader entryReader = image.GetBlobReaderByRawIndex(0);
    Check(entryReader.GetLength() == 2 && entryReader.GetData()[1] == 0xb2, "valid blob reader entry");
    std::printf("blob_reader_valid=PASS\n");
    return 0;
}

static int InvalidPrefixProbe()
{
    const byte invalid[] = { 0xe0 };
    uint32_t lengthSize = 0;
    try
    {
        BlobReader::ReadCompressedUint32(invalid, lengthSize);
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::printf("blob_reader_invalid_prefix=controlled_exception PASS\n");
        return 0;
    }
    std::fprintf(stderr, "invalid compressed prefix escaped without controlled rejection\n");
    return 1;
}

static int SkipOverflowProbe()
{
    const byte byteValue = 0;
    BlobReader reader(&byteValue, 1);
    try
    {
        reader.SkipBytes(std::numeric_limits<uint32_t>::max());
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::printf("blob_reader_skip_overflow=controlled_exception PASS\n");
        return 0;
    }
    return 1;
}

static int SkipWrapProbe()
{
    const byte byteValue = 0;
    BlobReader reader(&byteValue, std::numeric_limits<uint32_t>::max());
    reader.SkipBytes(std::numeric_limits<uint32_t>::max());
    try
    {
        reader.SkipByte();
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::printf("blob_reader_skip_wrap=controlled_exception PASS\n");
        return 0;
    }
    return 1;
}

static int BlobZeroSentinelProbe()
{
    ProbeRawImage image;
    Check(image.GetBlobFromRawIndex(0) == nullptr, "absent #Blob zero sentinel");
    const byte emptyHeapByte = 0xa5;
    image.SetBlobStream(&emptyHeapByte, 0);
    Check(image.GetBlobFromRawIndex(0) == &emptyHeapByte, "empty #Blob zero sentinel");

    const byte malformed[] = { 0x80 };
    image.SetBlobStream(malformed, sizeof(malformed));
    try
    {
        (void)image.GetBlobFromRawIndex(1);
        return 1;
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::printf("blob_reader_zero_sentinel=PASS\n");
        return 0;
    }
}

static int ValidateStreamsProbe()
{
    const byte strings[] = { 0 };
    const byte validUs[] = { 0x01, 0x41 };
    const byte validBlob[] = { 0x02, 0xa1, 0xb2 };
    const byte truncatedPrefix[] = { 0x80 };
    const byte truncatedPayload[] = { 0x02, 0xa1 };
    ProbeRawImage image;
    image.SetStringStream(strings, sizeof(strings));
    Check(image.GetStringHeapSize() == sizeof(strings), "string heap size getter");
    image.SetUserStream(validUs, sizeof(validUs));
    image.SetBlobStream(validBlob, sizeof(validBlob));
    Check(image.ValidateStreams() == LoadImageErrorCode::OK, "valid #US/#Blob streams");

    image.SetUserStream(truncatedPrefix, sizeof(truncatedPrefix));
    image.SetBlobStream(validBlob, sizeof(validBlob));
    Check(image.ValidateStreams() == LoadImageErrorCode::BAD_IMAGE, "truncated #US prefix");
    image.SetUserStream(truncatedPayload, sizeof(truncatedPayload));
    Check(image.ValidateStreams() == LoadImageErrorCode::BAD_IMAGE, "truncated #US payload");

    image.SetUserStream(validUs, sizeof(validUs));
    image.SetBlobStream(truncatedPrefix, sizeof(truncatedPrefix));
    Check(image.ValidateStreams() == LoadImageErrorCode::BAD_IMAGE, "truncated #Blob prefix");
    image.SetBlobStream(truncatedPayload, sizeof(truncatedPayload));
    Check(image.ValidateStreams() == LoadImageErrorCode::BAD_IMAGE, "truncated #Blob payload");
    std::printf("blob_reader_validate_streams=PASS\n");
    return 0;
}

static int RawEntriesTruncatedProbe()
{
    const byte malformed[] = { 0x00, 0x80 };
    ProbeRawImage image;
    image.SetUserStream(malformed + 1, 1);
    try
    {
        (void)image.GetUserStringBlogByIndex(0);
        return 1;
    }
    catch (const il2cpp::vm::ProbeException&)
    {
    }

    image.SetBlobStream(malformed, sizeof(malformed));
    try
    {
        (void)image.GetBlobFromRawIndex(1);
        return 1;
    }
    catch (const il2cpp::vm::ProbeException&)
    {
    }
    try
    {
        (void)image.GetBlobReaderByRawIndex(1);
        return 1;
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::printf("blob_reader_raw_entries=controlled_exception PASS\n");
        return 0;
    }
}

static int RunTruncated(const char* mode)
{
    size_t size = 0;
    if (std::strcmp(mode, "read16-truncated") == 0) size = 1;
    else if (std::strcmp(mode, "read32-truncated") == 0) size = 3;
    else if (std::strcmp(mode, "read64-truncated") == 0) size = 7;
    else if (std::strcmp(mode, "prefix2-truncated") == 0) size = 1;
    else if (std::strcmp(mode, "prefix4-truncated") == 0) size = 1;
    else if (std::strcmp(mode, "raw-decode-truncated") == 0) size = 1;
    else return 2;

    byte* bytes = static_cast<byte*>(std::malloc(size));
    Check(bytes != nullptr, "fixture allocation");
    std::memset(bytes, 0, size);
    if (std::strcmp(mode, "prefix2-truncated") == 0 || std::strcmp(mode, "prefix4-truncated") == 0 ||
        std::strcmp(mode, "raw-decode-truncated") == 0)
        bytes[0] = std::strcmp(mode, "prefix4-truncated") == 0 ? 0xc0 : 0x80;

    try
    {
        if (std::strcmp(mode, "read16-truncated") == 0)
            (void)BlobReader(bytes, static_cast<uint32_t>(size)).Read16();
        else if (std::strcmp(mode, "read32-truncated") == 0)
            (void)BlobReader(bytes, static_cast<uint32_t>(size)).Read32();
        else if (std::strcmp(mode, "read64-truncated") == 0)
            (void)BlobReader(bytes, static_cast<uint32_t>(size)).Read64();
        else if (std::strcmp(mode, "prefix2-truncated") == 0 || std::strcmp(mode, "prefix4-truncated") == 0)
        {
            uint32_t value = 0;
            uint32_t lengthSize = 0;
            if (BlobReader::TryReadCompressedUint32(bytes, static_cast<uint32_t>(size), value, lengthSize))
            {
                std::free(bytes);
                std::printf("blob_reader_truncated_escape=UNEXPECTED\n");
                return 1;
            }
            std::free(bytes);
            std::printf("blob_reader_truncated=bounded_false PASS\n");
            return 0;
        }
        else
            (void)RawImageBase::DecodeBlob(bytes, static_cast<uint32_t>(size));
    }
    catch (const il2cpp::vm::ProbeException&)
    {
        std::free(bytes);
        std::printf("blob_reader_truncated=controlled_exception PASS\n");
        return 0;
    }
    std::free(bytes);
    std::printf("blob_reader_truncated_escape=UNEXPECTED\n");
    return 1;
}

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::fprintf(stderr, "usage: blob-reader-fix-native <valid|invalid-prefix|skip-overflow|skip-wrap|zero-sentinel|validate-streams|raw-entry-truncated|read16-truncated|read32-truncated|read64-truncated|prefix2-truncated|prefix4-truncated|raw-decode-truncated>\n");
        return 2;
    }
    if (std::strcmp(argv[1], "valid") == 0) return ValidProbe();
    if (std::strcmp(argv[1], "invalid-prefix") == 0) return InvalidPrefixProbe();
    if (std::strcmp(argv[1], "skip-overflow") == 0) return SkipOverflowProbe();
    if (std::strcmp(argv[1], "skip-wrap") == 0) return SkipWrapProbe();
    if (std::strcmp(argv[1], "zero-sentinel") == 0) return BlobZeroSentinelProbe();
    if (std::strcmp(argv[1], "validate-streams") == 0) return ValidateStreamsProbe();
    if (std::strcmp(argv[1], "raw-entry-truncated") == 0) return RawEntriesTruncatedProbe();
    return RunTruncated(argv[1]);
}
