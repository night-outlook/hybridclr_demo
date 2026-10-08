#include "metadata/CustomAttributeDataWriter.h"
#include "metadata/CustomAttributeTypeIndexBatch.h"
#include "utils/MemoryRead.h"

#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>
#include <vector>

using hybridclr::metadata::CustomAttributeDataWriter;
using hybridclr::metadata::CustomAttributeTypeIndexBatch;

namespace
{
bool failNextAllocation = false;
bool failNextRuntimeAllocation = false;
struct MetadataFailure {};
}

void* operator new(std::size_t size)
{
    if (failNextAllocation)
    {
        failNextAllocation = false;
        throw std::bad_alloc();
    }
    void* result = std::malloc(size == 0 ? 1 : size);
    if (result == nullptr)
        throw std::bad_alloc();
    return result;
}

void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* pointer) noexcept { std::free(pointer); }
void operator delete[](void* pointer) noexcept { std::free(pointer); }
#if __cplusplus >= 201402L
void operator delete(void* pointer, std::size_t) noexcept { std::free(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { std::free(pointer); }
#endif

// Controlled exception adapters preserve production throw/unwind behavior.
// The real Memory.cpp callback route and MemoryRead.cpp remain linked.
namespace il2cpp { namespace vm {
Il2CppException* Exception::GetExecutionEngineException(const char*) { return nullptr; }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw MetadataFailure(); }
void Exception::RaiseOutOfMemoryException() { throw std::bad_alloc(); }
}}

static void* RuntimeMalloc(size_t size)
{
    if (failNextRuntimeAllocation) { failNextRuntimeAllocation = false; return nullptr; }
    return std::malloc(size);
}
static void* RuntimeCalloc(size_t count, size_t size)
{
    if (failNextRuntimeAllocation) { failNextRuntimeAllocation = false; return nullptr; }
    return std::calloc(count, size);
}

namespace
{
size_t checks = 0;

void Check(bool condition, const char* message)
{
    ++checks;
    if (!condition)
    {
        std::fprintf(stderr, "r01b attribute-batch check failed: %s\n", message);
        std::abort();
    }
}

uint32_t ReadFixedFive(const uint8_t* data)
{
    Check(data[0] == 0xF0, "deferred index uses F0 placeholder form");
    return (uint32_t)data[1] | ((uint32_t)data[2] << 8) |
        ((uint32_t)data[3] << 16) | ((uint32_t)data[4] << 24);
}

void TestSignedBoundaries()
{
    CustomAttributeDataWriter writer(16);
    const int32_t values[] = {0, 1, -1, std::numeric_limits<int32_t>::max(),
        std::numeric_limits<int32_t>::min()};
    for (int32_t value : values)
        writer.WriteCompressedInt32(value);
    const char* cursor = reinterpret_cast<const char*>(writer.Data());
    for (int32_t expected : values)
        Check(il2cpp::utils::ReadCompressedInt32(&cursor) == expected,
            "native MemoryRead signed zigzag roundtrip");
}

void TestUnalignedMethodIndex()
{
    CustomAttributeDataWriter writer(8);
    writer.WriteAttributeCount(1);
    const uint32_t offset = writer.Size();
    writer.Skip(sizeof(int32_t));
    writer.WriteMethodIndex(offset, 0x10203040);
    int32_t methodIndex = 0;
    std::memcpy(&methodIndex, writer.Data() + offset, sizeof(methodIndex));
    Check(methodIndex == 0x10203040, "unaligned method index uses byte copy");
}

void TestCombinedBuffersAndCopiedTypes()
{
    CustomAttributeDataWriter writer(8);
    CustomAttributeDataWriter first(8);
    CustomAttributeDataWriter second(8);
    CustomAttributeTypeIndexBatch batch;
    Il2CppType element = {};
    element.type = IL2CPP_TYPE_I4;
    Il2CppType array = {};
    array.type = IL2CPP_TYPE_SZARRAY;
    array.data.type = &element;

    first.WriteByte(0x11);
    batch.WriteTypeIndex(first, &array);
    second.WriteByte(0x22);
    batch.WriteTypeIndex(second, &array);
    Check(batch.Types().size() == 1, "local dedup combines repeated physical type");
    Check(batch.Types()[0] != &array && batch.Types()[0]->data.type != &element,
        "stack root and nested type values are copied");
    Check(batch.Fixups().size() == 2, "combined buffers retain both fixups");
    batch.AppendTo(writer, first);
    batch.AppendTo(writer, second);
    for (const CustomAttributeTypeIndexBatch::Fixup& fixup : batch.Fixups())
        writer.PatchCompressedInt32Placeholder(fixup.outputOffset, 17);
    const uint8_t* bytes = writer.Data();
    Check(bytes[0] == 0x11 && bytes[6] == 0x22, "non-fixup bytes survive relocation");
    Check(ReadFixedFive(bytes + 1) == 34, "first combined fixup is patched");
    Check(ReadFixedFive(bytes + 7) == 34, "second combined fixup is patched");
    const char* firstFixup = reinterpret_cast<const char*>(bytes + 1);
    Check(il2cpp::utils::ReadCompressedInt32(&firstFixup) == 17,
        "native MemoryRead accepts nonminimal F0 fixup");
    batch.DiscardOwnership();
}

void TestGenericAndArrayFixups()
{
    CustomAttributeDataWriter writer(4);
    CustomAttributeTypeIndexBatch batch;
    Il2CppType generic = {};
    generic.type = IL2CPP_TYPE_GENERICINST;
    generic.data.generic_class = reinterpret_cast<Il2CppGenericClass*>(uintptr_t(0x1234));
    Il2CppType element = {};
    element.type = IL2CPP_TYPE_CLASS;
    element.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(uintptr_t(0x5678));
    Il2CppType array = {};
    array.type = IL2CPP_TYPE_SZARRAY;
    array.data.type = &element;
    batch.WriteTypeIndex(writer, &generic);
    batch.WriteTypeIndex(writer, &array);
    Check(batch.Types().size() == 2, "generic and array physical types are retained");
    Check(batch.Fixups()[0].typeIndex == 0 && batch.Fixups()[1].typeIndex == 1,
        "generic and array fixup order is stable");
    for (const CustomAttributeTypeIndexBatch::Fixup& fixup : batch.Fixups())
        writer.PatchCompressedInt32Placeholder(fixup.outputOffset, (int32_t)(100 + fixup.typeIndex));
    Check(ReadFixedFive(writer.Data()) == 200, "generic fixup uses zigzag index");
    batch.DiscardOwnership();
}

void TestFailureBeforeCommitState()
{
    CustomAttributeDataWriter writer(8);
    CustomAttributeTypeIndexBatch batch;
    Il2CppType first = {};
    first.type = IL2CPP_TYPE_CLASS;
    first.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(uintptr_t(0x1));
    batch.WriteTypeIndex(writer, &first);
    const size_t typeCount = batch.Types().size();
    // Simulate a later conversion failure by abandoning the private output.
    Check(typeCount == 1 && batch.Fixups().size() == 1,
        "failed conversion has only private pending state");
    Check(writer.Size() == 5, "failed conversion does not append shared output");
    batch.DiscardOwnership();
}

void TestPrivateBlobAbandonmentAndFreshRetry()
{
    CustomAttributeDataWriter output(8);
    CustomAttributeDataWriter firstBlob(8);
    CustomAttributeDataWriter lastBlob(8);
    CustomAttributeTypeIndexBatch batch;
    Il2CppType first = {};
    first.type = IL2CPP_TYPE_CLASS;
    first.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(uintptr_t(0x101));
    Il2CppType last = {};
    last.type = IL2CPP_TYPE_GENERICINST;
    last.data.generic_class = reinterpret_cast<Il2CppGenericClass*>(uintptr_t(0x202));
    batch.WriteTypeIndex(firstBlob, &first);
    batch.AppendTo(output, firstBlob);
    const uint32_t privateSize = output.Size();
    batch.WriteTypeIndex(lastBlob, &last);
    // A failure in the final blob abandons only private state; the already
    // converted private prefix and its relocated fixup remain intact.
    Check(output.Size() == privateSize, "last-blob failure leaves output prefix unchanged");
    Check(batch.Fixups().size() == 2, "last-blob failure retains private fixup for retry");
    batch.DiscardOwnership();
    Check(batch.Types().empty() && batch.Fixups().empty(),
        "abandoned conversion releases private ownership");

    CustomAttributeDataWriter retry(8);
    CustomAttributeTypeIndexBatch retryBatch;
    retryBatch.WriteTypeIndex(retry, &last);
    retry.PatchCompressedInt32Placeholder(retryBatch.Fixups()[0].outputOffset, 9);
    const char* cursor = reinterpret_cast<const char*>(retry.Data());
    Check(il2cpp::utils::ReadCompressedInt32(&cursor) == 9,
        "fresh conversion retry can patch a fresh private output");
    retryBatch.DiscardOwnership();
}

void TestRuntimeWriterFailures()
{
    failNextRuntimeAllocation = true;
    bool threw = false;
    try { CustomAttributeDataWriter failed(64); }
    catch (const std::bad_alloc&) { threw = true; }
    Check(threw, "runtime calloc failure unwinds constructor");
    CustomAttributeDataWriter writer(64);
    for (unsigned i = 0; i < 64; ++i) writer.WriteByte(static_cast<uint8_t>(i));
    const uint8_t* original = writer.Data();
    failNextRuntimeAllocation = true;
    threw = false;
    try { writer.WriteByte(99); }
    catch (const std::bad_alloc&) { threw = true; }
    Check(threw && writer.Size() == 64 && writer.Data() == original,
        "runtime malloc resize failure preserves pointer and size");
    for (unsigned i = 0; i < 64; ++i)
        Check(writer.Data()[i] == i, "failed resize preserves prior bytes");
    writer.WriteByte(99);
    Check(writer.Size() == 65 && writer.Data()[64] == 99,
        "retry after resize failure grows correctly");
    threw = false;
    try { writer.WriteBytes(nullptr, UINT32_MAX); }
    catch (const MetadataFailure&) { threw = true; }
    Check(threw && writer.Size() == 65, "output overflow rejects without mutation");
    const uint8_t input[] = {7};
    hybridclr::metadata::BlobReader reader(input, sizeof(input));
    threw = false;
    try { writer.Write(reader, 2); }
    catch (const MetadataFailure&) { threw = true; }
    Check(threw && reader.GetReadPosition() == 0 && writer.Size() == 65,
        "truncated copy rejects before reading or writing");
    threw = false;
    try { writer.Skip(-1); }
    catch (const MetadataFailure&) { threw = true; }
    Check(threw && writer.Size() == 65, "negative output skip rejects");
    threw = false;
    try { writer.PatchCompressedInt32Placeholder(UINT32_MAX, 1); }
    catch (const MetadataFailure&) { threw = true; }
    Check(threw && writer.Size() == 65, "overflowing fixup rejects");
}

void TestGeometricBatchGrowth()
{
    CustomAttributeTypeIndexBatch batch;
    size_t growths = 0;
    size_t previousCapacity = 0;
    for (uintptr_t i = 1; i <= 4096; ++i)
    {
        Il2CppType type = {};
        type.type = IL2CPP_TYPE_CLASS;
        type.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(i);
        Check(batch.AddType(&type) == i - 1, "distinct batch types keep stable indices");
        if (batch.Types().capacity() != previousCapacity)
        {
            ++growths;
            previousCapacity = batch.Types().capacity();
        }
    }
    Check(growths < 32, "batch pointer capacity grows geometrically");
}

void TestAllocationFailureOwnership()
{
    CustomAttributeTypeIndexBatch batch;
    Il2CppType first = {};
    first.type = IL2CPP_TYPE_CLASS;
    first.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(uintptr_t(0x303));
    Il2CppType second = {};
    second.type = IL2CPP_TYPE_GENERICINST;
    second.data.generic_class = reinterpret_cast<Il2CppGenericClass*>(uintptr_t(0x404));
    Check(batch.AddType(&first) == 0, "allocation-failure setup type is retained");
    failNextAllocation = true;
    bool threw = false;
    try
    {
        batch.AddType(&second);
    }
    catch (const std::bad_alloc&)
    {
        threw = true;
    }
    Check(threw, "allocation failure is surfaced before batch mutation");
    Check(batch.Types().size() == 1, "allocation failure retains prior type only");
    Check(batch.AddType(&second) == 1 && batch.Types().size() == 2,
        "allocation failure supports a clean retry");
    batch.DiscardOwnership();
}
}

int main()
{
    Il2CppMemoryCallbacks callbacks = {};
    callbacks.malloc_func = RuntimeMalloc;
    callbacks.calloc_func = RuntimeCalloc;
    callbacks.free_func = std::free;
    callbacks.realloc_func = std::realloc;
    il2cpp::utils::Memory::SetMemoryCallbacks(&callbacks);
    TestRuntimeWriterFailures();
    TestGeometricBatchGrowth();
    TestSignedBoundaries();
    TestUnalignedMethodIndex();
    TestCombinedBuffersAndCopiedTypes();
    TestGenericAndArrayFixups();
    TestFailureBeforeCommitState();
    TestPrivateBlobAbandonmentAndFreshRetry();
    TestAllocationFailureOwnership();
    std::printf("r01b_attribute_batch_checks=%zu PASS\n", checks);
    return 0;
}
