// Additive isolated Player probe. To be appended to a NEW copy of the existing
// test-only native overlay, never installed into K or used in production builds.
// Called by generated R03.TerminalWitness.Prepare after 3 real body increments,
// before the throwing <Module>.cctor can terminate Commit.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include "il2cpp-class-internals.h"
#include "il2cpp-object-internals.h"
#include "vm/AssemblyShadow.h"
#include "vm/Assembly.h"
#include "vm/Image.h"
#include "vm/Class.h"
#include "gc/GCHandle.h"
#include "hybridclr/interpreter/MethodBridge.h"
#include <atomic>
#include <cstdint>
#include <cstring>

// Real writer is later in the composite overlay. The observer's standalone
// C++11 host driver supplies an explicitly labelled test-only trace stub.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d);

// Genuine linked binary table inspection, before any interpreted Commit.
// A source or nm string alone is NOT evidence of a callable Bi4 stub.
// The exported AOT test function reads the same compiled native table that
// InterpreterModule::InitMethodBridge consumes. Never call user methods here.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_BridgeStatus()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    const hybridclr::interpreter::Managed2NativeFunctionPointerCallData* entries =
        hybridclr::interpreter::g_managed2NativeFunctionPointerCallStub;
    if (!entries) return -1;
    int32_t found = 0;
    for (int32_t i = 0; i < 64; ++i)
    {
        if (entries[i].methodSig == nullptr)
            return (found == 1) ? 1 : -2;
        if (std::strcmp(entries[i].methodSig, "Bi4") == 0)
        {
            if (entries[i].methodPointer == nullptr) return -3;
            ++found;
            if (found != 1) return -4;
        }
    }
    return -5; // Missing bounded sentinel is not an authenticated bridge.
#else
    return 0;
#endif
}

namespace r03_irw_initializer {
struct Prepared final
{
    std::atomic<int32_t> state{0}; // 0=untouched, 2=entering, 1=pinned, -1=failed
    std::atomic<int32_t> calls{0};
    Il2CppClass* witness = nullptr;
    Il2CppClass* node = nullptr;
    Il2CppObject* instance = nullptr;
    uint32_t pinnedHandle = 0;
    int32_t instanceOffset = -1;
    int32_t stableOffset = -1;
    int32_t preField = -1;
    int32_t ready = -1;
    int32_t direct = -1;
    int32_t delegated = -1;
    int32_t generic = -1;
};
static Prepared prepared;

static int32_t Failed(int32_t reason, int32_t a=0, int32_t b=0, int32_t c=0)
{
    prepared.state.store(-1, std::memory_order_release);
    R03_IRW_Trace(300, reason, a, b, c);
    return reason;
}

static bool StaticInt(Il2CppClass* owner, const char* name, int32_t& value)
{
    if (!owner || !owner->static_fields || !name) return false;
    const FieldInfo* field = il2cpp::vm::Class::GetFieldFromName(owner, name);
    if (!field || field->parent != owner || !field->type ||
        field->type->type != IL2CPP_TYPE_I4 ||
        !(field->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        field->offset < 0 ||
        static_cast<uint64_t>(field->offset) + sizeof(value) > owner->static_fields_size)
        return false;
    std::memcpy(&value, static_cast<const uint8_t*>(owner->static_fields) + field->offset, sizeof value);
    return true;
}
} // namespace r03_irw_initializer

extern "C" IL2CPP_EXPORT int32_t R03_IRW_OnPrepared()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_irw_initializer;
    const int32_t calls = prepared.calls.fetch_add(1, std::memory_order_acq_rel) + 1;
    R03_IRW_Trace(299, calls, 0, 0, 0);
    int32_t expected = 0;
    if (!prepared.state.compare_exchange_strong(expected, 2, std::memory_order_acq_rel)) {
        R03_IRW_Trace(300, -1, expected, 0, 0);
        return -1;
    }
    // The active mapping is published, but Commit is still in Committing=5.
    AssemblyShadowState state = AssemblyShadowState::Committing;
    if (AssemblyShadow::GetState(state) != AssemblyShadowError::Success ||
        state != AssemblyShadowState::Committing)
    { return Failed(-2, static_cast<int32_t>(state)); }
    const Il2CppAssembly* assembly = Assembly::GetLoadedAssembly("Methods");
    if (!assembly || !assembly->image || !AssemblyShadow::IsActiveShadow(assembly))
    { return Failed(-3, assembly != nullptr, assembly && assembly->image != nullptr,
                    assembly && AssemblyShadow::IsActiveShadow(assembly)); }
    Il2CppClass* witness = Image::ClassFromName(assembly->image, "R03", "TerminalWitness");
    Il2CppClass* node = Image::ClassFromName(assembly->image, "R03", "Node");
    if (!witness || !node || !witness->static_fields || node->image != assembly->image)
    { return Failed(-4, witness != nullptr, node != nullptr,
                    witness && witness->static_fields != nullptr); }
    const FieldInfo* instanceField = Class::GetFieldFromName(witness, "Instance");
    const FieldInfo* stable = Class::GetFieldFromName(node, "stable");
    if (!instanceField || instanceField->parent != witness || !instanceField->type ||
        !(instanceField->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        instanceField->offset < 0 ||
        static_cast<uint64_t>(instanceField->offset) + sizeof(void*) > witness->static_fields_size ||
        !stable || stable->parent != node || !stable->type ||
        stable->type->type != IL2CPP_TYPE_I4 ||
        (stable->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        stable->offset < static_cast<int32_t>(sizeof(Il2CppObject)) ||
        static_cast<uint64_t>(stable->offset) + sizeof(int32_t) > node->instance_size)
    { return Failed(-5, instanceField ? instanceField->offset : -1,
                    stable ? stable->offset : -1,
                    node ? static_cast<int32_t>(node->instance_size) : -1); }
    Il2CppObject* object = nullptr;
    std::memcpy(&object,
        static_cast<const uint8_t*>(witness->static_fields) + instanceField->offset, sizeof object);
    if (!object || object->klass != node)
    { return Failed(-6, object != nullptr, object && object->klass == node); }
    int32_t actual = -1, ready = -1, direct = -1, delegated = -1, generic = -1;
    std::memcpy(&actual, reinterpret_cast<const uint8_t*>(object) + stable->offset, sizeof actual);
    if (actual != 3 || !StaticInt(witness, "PreField", actual) || actual != 3 ||
        !StaticInt(witness, "Ready", ready) || ready != 1 ||
        !StaticInt(witness, "PreDirectReturn", direct) || direct != 42 ||
        !StaticInt(witness, "PreDelegateReturn", delegated) || delegated != 42 ||
        !StaticInt(witness, "PreGenericReturn", generic) || generic != 42)
    {
        R03_IRW_Trace(301, actual, ready, direct, delegated);
        R03_IRW_Trace(302, generic, 0, 0, 0);
        return Failed(-7);
    }
    // GC handle creation and metadata discovery occur exclusively before
    // the initializer throws. No GC operation follows the terminal boundary.
    const uint32_t pinned = il2cpp::gc::GCHandle::New(object, true);
    if (!pinned)
    { return Failed(-8); }
    if (il2cpp::gc::GCHandle::GetTarget(pinned) != object)
    {
        il2cpp::gc::GCHandle::Free(pinned);
        return Failed(-9);
    }
    prepared.witness = witness;
    prepared.node = node;
    prepared.instance = object;
    prepared.pinnedHandle = pinned;
    prepared.instanceOffset = instanceField->offset;
    prepared.stableOffset = stable->offset;
    prepared.preField = 3;
    prepared.ready = ready;
    prepared.direct = direct;
    prepared.delegated = delegated;
    prepared.generic = generic;
    prepared.state.store(1, std::memory_order_release);
    R03_IRW_Trace(300, 1, 3, 15, calls);
    return 1;
#else
    return 0;
#endif
}

// Post-failure read: stable primitive memcpy only, using the pre-pinned object
// and pre-checked offsets. No reflection, class-init, allocation or user code.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(
    int32_t* finalField, int32_t* preField, int32_t* ready,
    int32_t* positiveMask, int32_t* calls)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_irw_initializer;
    if (!finalField || !preField || !ready || !positiveMask || !calls ||
        prepared.state.load(std::memory_order_acquire) != 1) {
        R03_IRW_Trace(400, -1, prepared.state.load(std::memory_order_acquire), 0, 0);
        return -1;
    }
    AssemblyShadowState state = AssemblyShadowState::Committing;
    if (AssemblyShadow::GetState(state) != AssemblyShadowError::Success ||
        (state != AssemblyShadowState::Committed &&
         state != AssemblyShadowState::FailedAfterCommit))
    {
        R03_IRW_Trace(400, -2, static_cast<int32_t>(state), 0, 0);
        return -2;
    }
    Il2CppObject* object = prepared.instance;
    if (!object || object->klass != prepared.node || !prepared.witness ||
        !prepared.witness->static_fields || !prepared.pinnedHandle ||
        prepared.stableOffset < static_cast<int32_t>(sizeof(Il2CppObject)))
    {
        R03_IRW_Trace(400, -3, prepared.stableOffset, prepared.instanceOffset,
                      prepared.pinnedHandle != 0);
        return -3;
    }
    Il2CppObject* root = nullptr;
    std::memcpy(&root,
        static_cast<const uint8_t*>(prepared.witness->static_fields) + prepared.instanceOffset,
        sizeof root);
    if (root != object) {
        R03_IRW_Trace(400, -4, root != nullptr, object != nullptr, 0);
        return -4;
    }
    int32_t current = 0;
    std::memcpy(&current, reinterpret_cast<const uint8_t*>(object) + prepared.stableOffset,
                sizeof current);
    *finalField = current;
    *preField = prepared.preField;
    *ready = prepared.ready;
    *positiveMask = (prepared.direct == 42 ? 1 : 0) |
                    (prepared.delegated == 42 ? 2 : 0) |
                    (prepared.generic == 42 ? 4 : 0) |
                    (prepared.preField == 3 ? 8 : 0);
    *calls = prepared.calls.load(std::memory_order_acquire);
    R03_IRW_Trace(400, 1, static_cast<int32_t>(state), current, *calls);
    R03_IRW_Trace(401, *preField, *ready, *positiveMask, prepared.stableOffset);
    return 1;
#else
    (void)finalField; (void)preField; (void)ready; (void)positiveMask; (void)calls;
    return 0;
#endif
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRW_BridgeStatus() { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_OnPrepared() { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(
    int32_t*,int32_t*,int32_t*,int32_t*,int32_t*) { return 0; }
#endif
