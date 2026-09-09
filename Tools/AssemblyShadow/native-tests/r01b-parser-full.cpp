#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <fstream>
#include <limits>
#include <string>
#include <vector>

#include "metadata/MetadataUtil.h"
#include "metadata/RawImage.h"

// Controlled allocator/diagnostic adapters. RawImageBase takes ownership of
// the malloc'd input and releases it through this same adapter in its dtor.
namespace il2cpp
{
namespace utils
{
    void* Memory::Malloc(size_t size) { return std::malloc(size); }
    void Memory::Free(void* memory) { std::free(memory); }
    void* Memory::Calloc(size_t count, size_t size) { return std::calloc(count, size); }
}
}

// These exception/string hooks are only invalid-input or user-string paths;
// strict linking keeps them visible without supplying the complete VM.
namespace il2cpp
{
namespace vm
{
    Il2CppString* String::Empty() { std::abort(); }
    Il2CppString* String::NewUtf16(const Il2CppChar*, int32_t) { std::abort(); }
    Il2CppException* Exception::GetExecutionEngineException(const char*) { std::abort(); }
    void Exception::Raise(Il2CppException*, MethodInfo*) { std::abort(); }
}
}

namespace hybridclr
{
    void LogPanic(const char*) { std::abort(); }
}

void il2cpp_assert(const char* assertion, const char* file, unsigned int line)
{
    std::fprintf(stderr, "il2cpp_assert:%s:%u:%s\n", file, line, assertion);
    std::abort();
}

using hybridclr::byte;
using hybridclr::metadata::GetU2LittleEndian;
using hybridclr::metadata::GetU4LittleEndian;
using hybridclr::metadata::GetU8LittleEndian;
using hybridclr::metadata::LoadImageErrorCode;
using hybridclr::metadata::RawImage;
using hybridclr::metadata::TableType;

static bool IsWorkloadName(const char* name)
{
    return std::strncmp(name, "AssemblyShadow.WorkloadV2.I", 27) == 0 &&
           std::strlen(name) == 35 &&
           name[27] >= '0' && name[27] <= '9' && name[28] >= '0' && name[28] <= '9' &&
           name[29] >= '0' && name[29] <= '9' && name[30] >= '0' && name[30] <= '9';
}

static int ParseId(const std::string& name)
{
    unsigned id = 0;
    if (std::sscanf(name.c_str(), "AssemblyShadow.WorkloadV2.I%4u.dll", &id) != 1 || id > 8191)
        return -1;
    char expected[64];
    std::snprintf(expected, sizeof(expected), "AssemblyShadow.WorkloadV2.I%04u.dll", id);
    return name == expected ? static_cast<int>(id) : -1;
}

static std::vector<std::string> ListAssemblies(const char* root)
{
    std::vector<std::string> result;
    DIR* directory = opendir(root);
    if (!directory)
    {
        std::fprintf(stderr, "cannot open corpus directory: %s\n", root);
        std::abort();
    }
    for (dirent* entry = readdir(directory); entry; entry = readdir(directory))
    {
        if (IsWorkloadName(entry->d_name))
            result.push_back(entry->d_name);
    }
    closedir(directory);
    std::sort(result.begin(), result.end());
    return result;
}

static std::vector<byte> ReadOwned(const std::string& path)
{
    std::ifstream input(path.c_str(), std::ios::binary | std::ios::ate);
    if (!input)
    {
        std::fprintf(stderr, "cannot open input: %s\n", path.c_str());
        std::abort();
    }
    std::streamoff size = input.tellg();
    if (size <= 0 || static_cast<uint64_t>(size) > std::numeric_limits<uint32_t>::max())
    {
        std::fprintf(stderr, "invalid input size: %s (%lld)\n", path.c_str(), static_cast<long long>(size));
        std::abort();
    }
    input.seekg(0);
    std::vector<byte> data(static_cast<size_t>(size));
    if (!input.read(reinterpret_cast<char*>(data.data()), size))
    {
        std::fprintf(stderr, "input read failed: %s\n", path.c_str());
        std::abort();
    }
    return data;
}

static void Check(bool condition, const char* detail, const std::string& path)
{
    if (!condition)
    {
        std::fprintf(stderr, "raw-image check failed: %s: %s\n", path.c_str(), detail);
        std::abort();
    }
}

static uint8_t ExpectedPayload(int id, int fieldIndex, uint32_t at)
{
    return static_cast<uint8_t>((id * 17 + fieldIndex * 29 + at) % 251);
}

static void CheckEndianHelpers()
{
    alignas(16) byte storage[16] = {};
    const byte expectedBytes[8] = { 0xf1, 0x80, 0xa5, 0xc3, 0xe7, 0x99, 0xd4, 0xfe };
    for (size_t offset = 0; offset < 8; ++offset)
    {
        std::memcpy(storage + offset, expectedBytes, sizeof(expectedBytes));
        const byte* data = storage + offset;
        Check(GetU2LittleEndian(data) == 0x80f1u, "GetU2LittleEndian offset/value", "<helper-offset-tests>");
        Check(GetU4LittleEndian(data) == 0xc3a580f1u, "GetU4LittleEndian offset/value", "<helper-offset-tests>");
        Check(GetU8LittleEndian(data) == 0xfed499e7c3a580f1ull, "GetU8LittleEndian offset/value", "<helper-offset-tests>");
    }
}

static void CheckOne(const std::string& root, const std::string& file, uint64_t& fieldRows,
                     uint64_t& payloadSamples, uint64_t& largeFiles)
{
    const int id = ParseId(file);
    Check(id >= 0, "unexpected workload filename", file);
    std::string path = root + "/" + file;
    std::vector<byte> input = ReadOwned(path);
    const size_t inputSize = input.size();
    byte* owned = static_cast<byte*>(std::malloc(inputSize));
    Check(owned != nullptr, "malloc failed", path);
    std::memcpy(owned, input.data(), inputSize);

    RawImage image;
    // RawImageBase owns this pointer and frees it when image is destroyed.
    input.clear();
    input.shrink_to_fit();
    LoadImageErrorCode load = image.Load(owned, inputSize);
    Check(load == LoadImageErrorCode::OK, "RawImage::Load failed", path);

    const auto assemblyTable = image.GetTableRowNum(TableType::ASSEMBLY);
    Check(assemblyTable == 1, "assembly row count", path);
    const auto assembly = image.ReadAssembly(1);
    const char* assemblyName = image.GetStringFromRawIndex(assembly.name);
    char expectedName[64];
    std::snprintf(expectedName, sizeof(expectedName), "AssemblyShadow.WorkloadV2.I%04d", id);
    Check(std::strcmp(assemblyName, expectedName) == 0, "assembly name", path);

    Check(image.GetTableRowNum(TableType::TYPEDEF) == 98, "TypeDef row count", path);
    Check(image.GetTableRowNum(TableType::METHOD) == 98, "Method row count", path);
    const uint32_t expectedFields = id == 0 ? 4u : id == 1 ? 2u : 1u;
    Check(image.GetTableRowNum(TableType::FIELD) == expectedFields, "Field row count", path);
    Check(image.GetTableRowNum(TableType::FIELDRVA) == expectedFields, "FieldRVA row count", path);

    const uint32_t expectedPayload = id == 0 ? 7500000u : 45000u;
    for (uint32_t row = 1; row <= expectedFields; ++row)
    {
        auto fieldRva = image.ReadFieldRVA(row);
        Check(fieldRva.field == row, "FieldRVA field RID/order", path);
        uint32_t imageOffset = 0;
        Check(image.TranslateRVAToImageOffset(fieldRva.rva, imageOffset), "FieldRVA RVA mapping", path);
        Check(static_cast<uint64_t>(imageOffset) + expectedPayload <= inputSize, "FieldRVA payload bounds", path);
        const byte* payload = image.GetDataPtrByImageOffset(imageOffset);
        for (uint32_t at : {0u, 1u, 127u, 4095u, expectedPayload - 1u})
        {
            Check(payload[at] == ExpectedPayload(id, static_cast<int>(row - 1), at), "FieldRVA payload sample", path);
            ++payloadSamples;
        }
        ++fieldRows;
    }
    if (id == 0)
    {
        Check(inputSize == 32u * 1024u * 1024u, "large core file envelope", path);
        ++largeFiles;
    }
}

int main(int argc, char** argv)
{
    if (argc < 2 || argc > 3)
    {
        std::fprintf(stderr, "usage: raw-image-native <corpus-dir> [expected-file-count]\n");
        return 2;
    }
    const std::vector<std::string> files = ListAssemblies(argv[1]);
    const uint64_t expectedCount = argc == 3 ? std::strtoull(argv[2], nullptr, 10) : 8192;
    Check(files.size() == expectedCount, "workload file count", argv[1]);
    CheckEndianHelpers();
    std::printf("raw_image_helper_offsets=8 PASS\n");
    uint64_t fieldRows = 0, payloadSamples = 0, largeFiles = 0;
    for (const std::string& file : files)
        CheckOne(argv[1], file, fieldRows, payloadSamples, largeFiles);
    Check(largeFiles == 1, "large core presence", argv[1]);
    std::printf("raw_image_checks=%llu files=%llu field_rva_rows=%llu payload_samples=%llu large_files=%llu PASS\n",
                static_cast<unsigned long long>(files.size()),
                static_cast<unsigned long long>(files.size()),
                static_cast<unsigned long long>(fieldRows),
                static_cast<unsigned long long>(payloadSamples),
                static_cast<unsigned long long>(largeFiles));
    return 0;
}
