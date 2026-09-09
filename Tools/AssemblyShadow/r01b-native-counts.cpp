// Execute unmodified count-bearing VTableSetUp method bodies extracted by the
// runner, with the production native layout and explicit non-count adapters.
#include <vector>
#include "metadata/Il2CppTypeHash.h"
#include "metadata/Il2CppTypeCompare.h"
#include "CommonDef.h"
#include "metadata/MetadataUtil.h"
#define private public
#include "metadata/VTableSetup.h"
#undef private
#include "metadata/InterpreterMetadataCounts.h"
#include <cstdio>
#include <cstdlib>
#include <stdexcept>

namespace {
bool staging = true;
const hybridclr::metadata::GenericClassMethod* parentOverride = nullptr;
size_t checks = 0;
void Check(bool value, const char* message)
{
    ++checks;
    if (!value) { std::fprintf(stderr, "FAIL: %s\n", message); std::abort(); }
}
template<class Action> void Reject(Action action, const char* message)
{
    bool rejected = false;
    try { action(); } catch (const std::runtime_error&) { rejected = true; }
    Check(rejected, message);
}
}

namespace il2cpp { namespace metadata {
size_t Il2CppTypeHash::operator()(const Il2CppType* type) const { return reinterpret_cast<size_t>(type); }
bool Il2CppTypeEqualityComparer::AreEqual(const Il2CppType* a, const Il2CppType* b) { return a == b; }
}}
namespace il2cpp { namespace vm {
Il2CppException* Exception::GetBadImageFormatException(const char*) { return nullptr; }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::runtime_error("ordinary metadata rejection"); }
}}
namespace hybridclr { namespace metadata {
bool AssemblyShadowBridge::IsStaging() { return staging; }
// Signature resolution and override application are outside this count test.
uint16_t VTableSetUp::FindExplicitOverrideInterfaceSlot(GenericClassMethod&, const Int32ToUin16Map&) { return kInvalidIl2CppMethodSlot; }
uint16_t VTableSetUp::FindDefaultOverrideExplicitInterfaceSlot(GenericClassMethod&, const Uin16Set&, const std::vector<uint16_t>&) { return kInvalidIl2CppMethodSlot; }
const GenericClassMethod* VTableSetUp::FindImplMethod(const Il2CppType*, const Il2CppMethodDefinition*, bool) { return parentOverride; }
void VTableSetUp::ApplyOverrideMethod(const GenericClassMethod*, const Il2CppMethodDefinition*, uint16_t) {}
void VTableSetUp::ComputeExplicitImpls(const std::vector<uint16_t>&, Int32ToUin16Map&) {}
void VTableSetUp::ComputeInterfaceOverrideByParentVirtualMethod(const std::vector<uint16_t>&) {}
}}

#include "r01b-native-counts-production.inc"

using namespace hybridclr::metadata;
struct Fixture
{
    VTableSetUp tree;
    Il2CppType type = {};
    Il2CppTypeDefinition definition = {};
    std::vector<Il2CppMethodDefinition> methods;
    Fixture() { tree._parent = nullptr; tree._type = &type; tree._typeDef = &definition; }
    void Methods(size_t count, uint16_t flags = METHOD_ATTRIBUTE_NEW_SLOT | METHOD_ATTRIBUTE_VIRTUAL)
    {
        methods.resize(count);
        tree._virtualMethods.clear();
        for (auto& method : methods) {
            method.flags = flags;
            method.slot = kInvalidIl2CppMethodSlot;
            tree._virtualMethods.push_back({ &type, &method, "M" });
        }
    }
    void InheritedSlots(size_t count) { tree._methodImpls.resize(count); }
    void Build() { Il2CppType2TypeDeclaringTreeMap cache; tree.ComputeInterpTypeVtables(cache); }
};

void TestListRanges()
{
    uint16_t count = 7;
    Check(InterpreterMetadataCounts::TryListRange(1, 65536, 65535, count) && count == 65535, "property/event count 65535 accepted");
    Reject([&] { if (!InterpreterMetadataCounts::TryListRange(1, 65537, 65536, count)) throw std::runtime_error("range"); }, "property/event count 65536 rejected");
    Check(count == 65535, "failed list count leaves narrow destination unchanged");
    Check(InterpreterMetadataCounts::TryListRange(65536, 131071, 131070, count) && count == 65535, "large raw start with 65535 per-type members accepted");
    Check(!InterpreterMetadataCounts::TryListRange(65536, 131072, 131071, count), "nonzero-start 65536 count rejected");
    Check(!InterpreterMetadataCounts::TryListRange(10, 9, 12, count), "descending lists rejected before subtraction");
    Check(!InterpreterMetadataCounts::TryListRange(0, 1, 12, count), "zero one-based list rejected");
    Check(!InterpreterMetadataCounts::TryListRange(1, 14, 12, count), "list beyond table rejected");
    Check(InterpreterMetadataCounts::TryListRange(13, 13, 12, count) && count == 0, "empty one-past list accepted");
    Check(!InterpreterMetadataCounts::CanAppend(UINT64_MAX, 1), "huge inherited count rejected without overflow");
    Check(!InterpreterMetadataCounts::CanAppend(1, UINT64_MAX), "huge addition rejected without overflow");
    uint16_t interfaces = 0;
    for (uint32_t i = 0; i < 65535; ++i) {
        if (!InterpreterMetadataCounts::CanAppend(interfaces, 1)) std::abort();
        ++interfaces;
    }
    Check(interfaces == 65535 && !InterpreterMetadataCounts::CanAppend(interfaces, 1), "direct interfaces admit 65535 and reject next before wrap");
}

void TestClassSlots()
{
    Fixture parent, child;
    parent.InheritedSlots(65534);
    child.tree._parent = &parent.tree;
    child.Methods(1);
    child.Build();
    Check(child.tree._methodImpls.size() == 65535 && child.methods[0].slot == 65534, "inherited aggregate 65535 gets last valid slot");
    Fixture overflow;
    overflow.tree._parent = &child.tree;
    overflow.Methods(1);
    Reject([&] { overflow.Build(); }, "inherited aggregate 65536 rejected");
    Check(overflow.methods[0].slot == kInvalidIl2CppMethodSlot && overflow.tree._methodImpls.size() == 65535, "overflow rejected before assigning sentinel or appending method");
    Fixture privateOverflow;
    privateOverflow.tree._parent = &child.tree;
    privateOverflow.Methods(1, METHOD_ATTRIBUTE_PRIVATE | METHOD_ATTRIBUTE_VIRTUAL);
    Reject([&] { privateOverflow.Build(); }, "private virtual fallback also rejects overflow");
    Check(privateOverflow.methods[0].slot == kInvalidIl2CppMethodSlot, "private fallback never writes invalid slot");
    Fixture overrideOnly;
    overrideOnly.tree._parent = &child.tree;
    overrideOnly.Methods(1, METHOD_ATTRIBUTE_PUBLIC | METHOD_ATTRIBUTE_VIRTUAL);
    parentOverride = &child.tree._virtualMethods[0];
    overrideOnly.Build();
    Check(overrideOnly.methods[0].slot == 65534 && overrideOnly.tree._methodImpls.size() == 65535, "override allowed at full inherited count because it adds no slot");
    parentOverride = nullptr;
    Fixture malformedParent, derived;
    malformedParent.InheritedSlots(65536);
    derived.tree._parent = &malformedParent.tree;
    Reject([&] { derived.Build(); }, "oversized inherited vector rejected before narrowing");
    Check(derived.tree._methodImpls.empty(), "oversized inherited vector not copied");
    Fixture raw;
    raw.tree._parent = &parent.tree;
    raw.Methods(2);
    staging = false;
    Reject([&] { raw.Build(); }, "ordinary nonstaging route also rejects 65536");
    staging = true;
}

void TestInterfaceSlotsAndOffsets()
{
    Fixture parent, child, interface;
    parent.InheritedSlots(65534);
    interface.Methods(1);
    child.tree._parent = &parent.tree;
    child.tree._interfaces.push_back(&interface.tree);
    child.Build();
    Check(child.tree._methodImpls.size() == 65535 && child.tree._methodImpls.back().slot == 65534, "interface aggregate admits last valid slot");
    Fixture overflow, other;
    other.Methods(1);
    overflow.tree._parent = &child.tree;
    overflow.tree._interfaces.push_back(&other.tree);
    Reject([&] { overflow.Build(); }, "interface aggregate 65536 rejected");
    Check(overflow.tree._interfaceOffsetInfos.size() == 1 && overflow.tree._methodImpls.size() == 65535, "rejected interface adds neither offset nor method");
    Fixture batch, twoMethods;
    twoMethods.Methods(2);
    batch.tree._parent = &parent.tree;
    batch.tree._interfaces.push_back(&twoMethods.tree);
    Reject([&] { batch.Build(); }, "whole interface range checked before appending its first method");
    Check(batch.tree._methodImpls.size() == 65534 && batch.tree._interfaceOffsetInfos.empty(), "oversized interface block is not partially appended");
    Fixture emptyInterface, full, inheritedOffsets;
    inheritedOffsets.tree._interfaceOffsetInfos.resize(65534, { nullptr, &emptyInterface.tree, 0 });
    full.tree._parent = &inheritedOffsets.tree;
    full.tree._interfaces.push_back(&emptyInterface.tree);
    full.Build();
    Check(full.tree._interfaceOffsetInfos.size() == 65535, "inherited interface offset count 65535 accepted");
    Fixture extra, newEmpty;
    extra.tree._parent = &full.tree;
    extra.tree._interfaces.push_back(&newEmpty.tree);
    Reject([&] { extra.Build(); }, "inherited interface offset count 65536 rejected");
    Check(extra.tree._interfaceOffsetInfos.size() == 65535, "offset count stays representable on rejection");
    Fixture reuse;
    reuse.tree._parent = &full.tree;
    reuse.tree._interfaces.push_back(&emptyInterface.tree);
    reuse.Build();
    Check(reuse.tree._interfaceOffsetInfos.size() == 65535, "existing inherited interface accepted at full offset count");
    Fixture malformed, descendant;
    malformed.tree._interfaceOffsetInfos.resize(65536);
    descendant.tree._parent = &malformed.tree;
    Reject([&] { descendant.Build(); }, "malformed inherited interface offset vector rejected before copy");
    Check(descendant.tree._interfaceOffsetInfos.empty(), "malformed inherited offsets not copied");
}

int main()
{
    static_assert(sizeof(((Il2CppTypeDefinition*)nullptr)->vtable_count) == sizeof(uint16_t), "native count ABI unchanged");
    TestListRanges(); TestClassSlots(); TestInterfaceSlotsAndOffsets();
    std::printf("r01b_native_count_checks=%zu PASS\n", checks);
}
