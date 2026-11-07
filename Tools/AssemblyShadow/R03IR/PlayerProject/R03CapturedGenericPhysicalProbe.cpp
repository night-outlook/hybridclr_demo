// R03 IR-R03-02 A2: additive test-only physical captured-generic witness.
// This is installed ONLY as an extension to a fresh isolated R03 native overlay.
// No general runtime admission changes, no historical S/oneuse07 source edits.
//
// A1 proved only CLR method owner/argument metadata. This code obtains the
// physical original Methods TypeDef handle WITHOUT Class::FromIl2CppType or
// materializing a baseline Il2CppClass. It constructs a genuine inflated AOT
// MethodInfo only AFTER a successful Shadow Commit, then invokes the actual
// AssemblyShadow::AssertMethodIsActive guard (expected error15).
//
// A standalone VM-shaped host driver is NOT real Unity. This source only
// becomes runtime evidence when a freshly built IL2CPP Player executes it.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE && HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#include "il2cpp-class-internals.h"
#include "il2cpp-object-internals.h"
#include "vm/AssemblyShadow.h"
#include "vm/Assembly.h"
#include "vm/MetadataCache.h"
#include "vm/Image.h"
#include "vm/Class.h"
#include "vm/Runtime.h"
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace r03_irg_captured {

static const char* const kOwnerNamespace = "AssemblyShadow.R03.IR";
static const char* const kOwnerType = "R03CapturedGenericAotOwner";
static const char* const kOwnerMethod = "Touch";
static const char* const kBaseline = "Methods";
static const char* const kArgumentNamespace = "R03";
static const char* const kArgumentType = "Node";
static const char* const kCase = "IR-R03-02-captured-generic";
static const size_t kMaxReport = 16384;

struct PhysicalWitness final
{
    std::atomic<int32_t> stage{0}; // 0=unused,1=owner bound,2=guard checked,3=sealed,-1=failed
    int32_t fd = -1;
    char runId[96] = {};
    char fixtureSha256[65] = {};
    const Il2CppAssembly* ownerAssembly = nullptr;
    Il2CppClass* owner = nullptr;
    const FieldInfo* counter = nullptr;
    const MethodInfo* definition = nullptr;
    // Persistent metadata-handle-backed VALUE, not a forged MethodInfo.
    Il2CppType physicalType{};
    Il2CppMetadataTypeHandle physicalHandle = nullptr;
    const MethodInfo* inflated = nullptr;
    uint32_t physicalIndex = 0;
    int32_t ownerIsAot = 0;
    int32_t methodContextPhysical = 0;
    int32_t guardAllowed = -1;
    int32_t beforeState = -1, afterState = -1;
    int32_t beforeCount = -1, afterCount = -1;
    int32_t invoked = 0, invokeSucceeded = 0, invokeThrew = 0;
    int32_t methodInflated = 0;
    int32_t failureCode = 0;
};
static PhysicalWitness witness;

static bool AsciiId(const char* value, size_t minLength, size_t maxLength)
{
    if (!value) return false;
    size_t count = 0;
    while (value[count] && count <= maxLength)
    {
        const char c = value[count];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
              (c >= 'A' && c <= 'F'))) return false;
        ++count;
    }
    return count >= minLength && count <= maxLength && !value[count];
}
static int32_t Fault(int32_t code)
{
    witness.failureCode = code;
    witness.stage.store(-1, std::memory_order_release);
    return code;
}
static bool StaticCounter(int32_t& value)
{
    if (!witness.owner || !witness.owner->static_fields || !witness.counter ||
        witness.counter->parent != witness.owner || !witness.counter->type ||
        witness.counter->type->type != IL2CPP_TYPE_I4 ||
        !(witness.counter->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        witness.counter->offset < 0 ||
        static_cast<uint64_t>(witness.counter->offset) + sizeof(int32_t) >
            witness.owner->static_fields_size) return false;
    std::memcpy(&value, static_cast<const uint8_t*>(witness.owner->static_fields) +
                witness.counter->offset, sizeof value);
    return true;
}
static bool State(int32_t expected, int32_t& code)
{
    il2cpp::vm::AssemblyShadowState state;
    if (il2cpp::vm::AssemblyShadow::GetState(state) !=
        il2cpp::vm::AssemblyShadowError::Success) return false;
    code = static_cast<int32_t>(state);
    return code == expected;
}
static bool WriteAll(int fd, const char* data, size_t bytes)
{
    size_t at = 0;
    while (at < bytes)
    {
        ssize_t written = ::write(fd, data + at, bytes - at);
        if (written > 0) at += static_cast<size_t>(written);
        else if (written < 0 && errno == EINTR) continue;
        else return false;
    }
    return true;
}
} // namespace r03_irg_captured

// Called BEFORE Configure from an AOT runtime-init method, after WarmShared().
// The owner is an actual stable AOT assembly; no physical Methods type is
// looked up here. Failed/opened outputs are never reopened or reused.
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Open(
    const char* path, const char* runId, const char* caseId,
    const char* fixtureSha256, const char* ownerAssembly)
{
    using namespace il2cpp::vm;
    using namespace r03_irg_captured;
    if (!path || path[0] != '/' || !AsciiId(runId, 24, 64) ||
        !AsciiId(fixtureSha256, 64, 64) ||
        !caseId || std::strcmp(caseId, kCase) ||
        !ownerAssembly || !*ownerAssembly ||
        witness.stage.load(std::memory_order_acquire) != 0 ||
        AssemblyShadow::ActiveGeneration() != 0) return -1;
    // Avoid accepting punctuation/unbounded strings as an assembly identity.
    const size_t assemblyLen = std::strlen(ownerAssembly);
    if (assemblyLen > 100) return -2;
    for (size_t i = 0; i < assemblyLen; ++i)
    {
        char x = ownerAssembly[i];
        if (!((x >= 'a' && x <= 'z') || (x >= 'A' && x <= 'Z') ||
              (x >= '0' && x <= '9') || x == '.' || x == '_' || x == '-')) return -2;
    }
    const Il2CppAssembly* physicalOwner = MetadataCache::GetAotAssemblyByNamePhysical(ownerAssembly);
    if (!physicalOwner || !physicalOwner->image ||
        AssemblyShadow::IsCandidate(physicalOwner) ||
        AssemblyShadow::IsShadowedBaseline(physicalOwner) ||
        AssemblyShadow::IsActiveShadow(physicalOwner)) return -3;
    Il2CppClass* owner = Image::ClassFromName(physicalOwner->image, kOwnerNamespace, kOwnerType);
    if (!owner || owner->image != physicalOwner->image) return -4;
    const MethodInfo* definition = Class::GetMethodFromName(owner, kOwnerMethod, 0);
    const FieldInfo* counter = Class::GetFieldFromName(owner, "s_calls");
    if (!definition || definition->klass != owner || !definition->is_generic ||
        definition->is_inflated || !(definition->flags & METHOD_ATTRIBUTE_STATIC) ||
        !counter || counter->parent != owner) return -5;
    witness.ownerAssembly = physicalOwner;
    witness.owner = owner;
    witness.definition = definition;
    witness.counter = counter;
    if (!StaticCounter(witness.beforeCount) || witness.beforeCount != 1) return -6;
    // Exclusively create a NEW file, never follow an output symlink.
    int fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (fd < 0) return -7;
    witness.fd = fd;
    std::strcpy(witness.runId, runId);
    std::strcpy(witness.fixtureSha256, fixtureSha256);
    witness.ownerIsAot = 1;
    witness.stage.store(1, std::memory_order_release);
    return 1;
}

// Called only after true Commit=0 / Committed=6. This is the actual native
// method-entry guard, not a synthetic error code or managed exception.
// It does NOT call the body of Touch<Methods.R03.Node>.
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Probe()
{
    using namespace il2cpp::vm;
    using namespace r03_irg_captured;
    if (witness.stage.load(std::memory_order_acquire) != 1 ||
        witness.fd < 0 || !witness.ownerIsAot) return Fault(-10);
    if (!State(6, witness.beforeState) || AssemblyShadow::ActiveGeneration() == 0)
        return Fault(-11);
    const Il2CppAssembly* baseline = MetadataCache::GetAotAssemblyByNamePhysical(kBaseline);
    if (!baseline || !baseline->image || !AssemblyShadow::IsShadowedBaseline(baseline))
        return Fault(-12);
    Il2CppMetadataTypeHandle found = nullptr;
    uint32_t selected = 0;
    for (uint32_t index = 0; index < baseline->image->typeCount; ++index)
    {
        const auto handle = MetadataCache::GetAssemblyTypeHandle(baseline->image, index);
        if (!handle) return Fault(-13);
        const auto name = MetadataCache::GetTypeNamespaceAndName(handle);
        if (name.first && name.second &&
            std::strcmp(name.first, kArgumentNamespace) == 0 &&
            std::strcmp(name.second, kArgumentType) == 0)
        {
            if (found) return Fault(-14); // ambiguous physical identity
            found = handle;
            selected = index;
        }
    }
    if (!found || selected >= baseline->image->typeCount) return Fault(-15);
    witness.physicalHandle = found;
    witness.physicalIndex = selected;
    // IL2CPP runtime owns this raw TypeDef handle. We keep the VALUE stable for
    // the lifetime of the generated method_inst; no Class::FromIl2CppType,
    // GetTypeInfoFromHandle or metadata mutation/materialization is performed.
    witness.physicalType = Il2CppType{};
    witness.physicalType.type = IL2CPP_TYPE_CLASS;
    witness.physicalType.data.typeHandle = found;
    const Il2CppType* arguments[1] = { &witness.physicalType };
    const MethodInfo* method = MetadataCache::GetGenericInstanceMethod(
        witness.definition, arguments, 1);
    if (!method || method == witness.definition || !method->is_inflated ||
        !method->genericMethod || !method->genericMethod->context.method_inst ||
        method->genericMethod->context.method_inst->type_argc != 1 ||
        !method->genericMethod->context.method_inst->type_argv ||
        method->genericMethod->methodDefinition != witness.definition ||
        method->klass != witness.owner)
        return Fault(-16);
    const Il2CppType* captured = method->genericMethod->context.method_inst->type_argv[0];
    if (!captured || captured->type != IL2CPP_TYPE_CLASS ||
        captured->data.typeHandle != found) return Fault(-17);
    witness.methodContextPhysical = 1;
    witness.methodInflated = 1;
    witness.inflated = method;
    if (!StaticCounter(witness.beforeCount) || witness.beforeCount != 1)
        return Fault(-18);
    witness.guardAllowed = AssemblyShadow::AssertMethodIsActive(
        method, "R03IR:PhysicalCapturedAotOwner");
    if (!State(9, witness.afterState) || witness.guardAllowed)
        return Fault(-19);
    if (!StaticCounter(witness.afterCount) || witness.afterCount != witness.beforeCount)
        return Fault(-20);
    witness.stage.store(2, std::memory_order_release);
    return 1;
}

// Optional second real entry attempt, now at terminal state. The first VM
// failure must stay error15. A later terminal guard must not execute AOT body.
// This invokes the *actual runtime* method entry rather than a host fake.
extern "C" IL2CPP_EXPORT int32_t R03_IRG_AttemptRuntimeInvoke()
{
    using namespace il2cpp::vm;
    using namespace r03_irg_captured;
    if (witness.stage.load(std::memory_order_acquire) != 2 ||
        !witness.inflated || witness.invoked) return Fault(-21);
    witness.invoked = 1;
    Il2CppException* exception = nullptr;
    try
    {
        Il2CppObject* result = Runtime::Invoke(witness.inflated, nullptr, nullptr, &exception);
        witness.invokeSucceeded = exception == nullptr && result != nullptr;
    }
    catch (const Il2CppExceptionWrapper&)
    {
        witness.invokeThrew = 1;
    }
    catch (...) { return Fault(-22); }
    if (!StaticCounter(witness.afterCount) ||
        witness.afterCount != witness.beforeCount || witness.invokeSucceeded)
        return Fault(-23);
    return 1;
}

// Called from AOT after the first failure. The existing native recovery getter
// is authoritative; we include its unmodified JSON as a nested raw object.
// The sink is exclusive, bounded, never reopened, fsynced and closed.
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Seal()
{
    using namespace il2cpp::vm;
    using namespace r03_irg_captured;
    if (witness.fd < 0 || witness.stage.load(std::memory_order_acquire) != 2 ||
        !witness.invoked || witness.invokeSucceeded ||
        !witness.methodContextPhysical || !witness.methodInflated ||
        !State(9, witness.afterState)) return Fault(-24);
    std::string recovery;
    if (AssemblyShadow::GetRecoveryInfoJson(recovery) != AssemblyShadowError::Success ||
        recovery.empty() || recovery.size() > 8192 || recovery.front() != '{' ||
        recovery.back() != '}') return Fault(-25);
    char prefix[2048];
    int written = std::snprintf(prefix, sizeof prefix,
        "{\"schemaVersion\":1,\"kind\":\"R03IRCapturedGenericPhysicalNativeV1\","
        "\"result\":\"ObservedNotAccepted\",\"runId\":\"%s\","
        "\"caseId\":\"%s\",\"fixtureSha256\":\"%s\","
        "\"ownerAssembly\":\"%s\",\"capturedArgumentAssembly\":\"Methods\","
        "\"capturedType\":\"R03.Node\",\"physicalTypeIndex\":%u,"
        "\"methodInflated\":%s,\"methodContextPhysical\":%s,"
        "\"ownerIndependentAot\":%s,\"guardAllowed\":%d,"
        "\"beforeState\":%d,\"afterState\":%d,"
        "\"beforeCount\":%d,\"afterCount\":%d,"
        "\"runtimeInvokeAttempted\":%s,\"runtimeInvokeSucceeded\":%s,"
        "\"runtimeInvokeThrew\":%s,\"nativeRecovery\":",
        witness.runId, kCase, witness.fixtureSha256,
        witness.ownerAssembly->aname.name, witness.physicalIndex,
        witness.methodInflated ? "true":"false",
        witness.methodContextPhysical ? "true":"false",
        witness.ownerIsAot ? "true":"false",
        witness.guardAllowed, witness.beforeState, witness.afterState,
        witness.beforeCount, witness.afterCount,
        witness.invoked ? "true":"false",
        witness.invokeSucceeded ? "true":"false",
        witness.invokeThrew ? "true":"false");
    if (written <= 0 || static_cast<size_t>(written) >= sizeof prefix ||
        static_cast<size_t>(written) + recovery.size() + 110 > kMaxReport)
        return Fault(-26);
    const char* suffix =
        ",\"runtimeAcceptance\":false,\"R03Accepted\":false,\"H2Passed\":false}\n";
    bool ok = WriteAll(witness.fd, prefix, static_cast<size_t>(written)) &&
        WriteAll(witness.fd, recovery.data(), recovery.size()) &&
        WriteAll(witness.fd, suffix, std::strlen(suffix)) &&
        ::fsync(witness.fd) == 0;
    const int closed = ::close(witness.fd);
    witness.fd = -1;
    if (!ok || closed != 0) return Fault(-27);
    witness.stage.store(3, std::memory_order_release);
    return 1;
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Open(
    const char*, const char*, const char*, const char*, const char*) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Probe() { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRG_AttemptRuntimeInvoke() { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRG_Seal() { return 0; }
#endif
