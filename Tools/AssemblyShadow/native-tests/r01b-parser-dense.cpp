#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <limits>
#include <string>
#include <vector>

#include "metadata/RawImage.h"

// Controlled adapters for the parser-only native harness. RawImage owns the
// malloc'd image bytes and releases them through this same adapter.
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
using hybridclr::metadata::LoadImageErrorCode;
using hybridclr::metadata::RawImage;
using hybridclr::metadata::TableType;

static void Check(bool condition, const char* detail, const std::string& path)
{
    if (!condition)
    {
        std::fprintf(stderr, "raw-image-dense check failed: %s: %s\n", path.c_str(), detail);
        std::abort();
    }
}

static std::vector<byte> ReadOwned(const std::string& path)
{
    std::ifstream input(path.c_str(), std::ios::binary | std::ios::ate);
    Check(static_cast<bool>(input), "cannot open input", path);
    std::streamoff size = input.tellg();
    Check(size > 0 && static_cast<uint64_t>(size) <= std::numeric_limits<uint32_t>::max(), "invalid input size", path);
    input.seekg(0);
    std::vector<byte> data(static_cast<size_t>(size));
    Check(static_cast<bool>(input.read(reinterpret_cast<char*>(data.data()), size)), "input read failed", path);
    return data;
}

static std::string AssemblyName(int id)
{
    char name[64];
    std::snprintf(name, sizeof(name), "AssemblyShadow.Workload.I%04d", id);
    return name;
}

static std::string DenseTypeName(int id, int index)
{
    char name[128];
    std::snprintf(name, sizeof(name), "DenseType_%04d_%04d_MetadataBoundary_0123456789abcdef0123456789abcdef", id, index);
    return name;
}

static void CheckFixture(const std::string& path, int id)
{
    std::vector<byte> input = ReadOwned(path);
    const size_t inputSize = input.size();
    byte* owned = static_cast<byte*>(std::malloc(inputSize));
    Check(owned != nullptr, "malloc failed", path);
    std::memcpy(owned, input.data(), inputSize);

    RawImage image;
    input.clear();
    input.shrink_to_fit();
    Check(image.Load(owned, inputSize) == LoadImageErrorCode::OK, "RawImage::Load failed", path);

    Check(image.GetTableRowNum(TableType::MODULE) == 1, "Module row count", path);
    Check(image.GetTableRowNum(TableType::ASSEMBLY) == 1, "Assembly row count", path);
    Check(image.GetTableRowNum(TableType::TYPEDEF) == 4098, "TypeDef row count", path);
    Check(image.GetTableRowNum(TableType::METHOD) == 4097, "Method row count", path);
    Check(image.GetTable(TableType::TYPEDEF).rowMetaDataSize == 18, "4-byte TypeDef string row width", path);
    Check(image.GetTable(TableType::METHOD).rowMetaDataSize == 16, "4-byte Method string row width", path);

    auto module = image.ReadModule(1);
    Check(std::strcmp(image.GetStringFromRawIndex(module.name), AssemblyName(id).c_str()) == 0, "Module name", path);
    auto assembly = image.ReadAssembly(1);
    Check(std::strcmp(image.GetStringFromRawIndex(assembly.name), AssemblyName(id).c_str()) == 0, "Assembly name", path);

    const uint32_t sampleRows[] = { 1, 2, 4095, 4096, 4097, 4098 };
    const uint32_t expectedNameIndices[] = { 31, 82, 112292, 140992, 169692, 198392 };
    for (size_t i = 0; i < sizeof(sampleRows) / sizeof(sampleRows[0]); ++i)
    {
        const uint32_t rid = sampleRows[i];
        auto type = image.ReadTypeDef(rid);
        Check(type.typeName == expectedNameIndices[i], "TypeDef string index", path);
        Check(std::strcmp(image.GetStringFromRawIndex(type.typeName), rid == 1 ? "<Module>" : DenseTypeName(id, static_cast<int>(rid - 2)).c_str()) == 0,
              "TypeDef name across dense boundary", path);
        Check(type.typeNamespace == (rid == 1 ? 0u : 58u), "TypeDef namespace index", path);
        Check(type.fieldList == 1, "TypeDef field list", path);
        Check(type.methodList == (rid == 1 ? 1u : rid - 1), "TypeDef method list boundary", path);
    }

    const uint32_t methodRows[] = { 1, 4095, 4096, 4097 };
    for (uint32_t rid : methodRows)
    {
        auto method = image.ReadMethod(rid);
        Check(method.rva == 8272, "Method RVA", path);
        Check(method.name == 49, "Method string index", path);
        Check(std::strcmp(image.GetStringFromRawIndex(method.name), "ReturnId") == 0, "Method name", path);
        Check(method.signature == 10 && method.paramList == 1, "Method signature/param index", path);
    }
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::fprintf(stderr, "usage: raw-image-dense-native <I0001.dll> <I0002.dll>\n");
        return 2;
    }
    CheckFixture(argv[1], 1);
    CheckFixture(argv[2], 2);
    std::printf("raw_image_dense_checks=2 typedef_rows=8196 method_rows=8194 boundary_rows=PASS PASS\n");
    return 0;
}
