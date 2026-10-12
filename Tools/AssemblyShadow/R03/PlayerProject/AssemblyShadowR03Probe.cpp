// Test-only additive source installed into an isolated validation Player.
// Its exact committed bytes are recorded separately from the native install
// receipt. It is never installed into the production or historical Player.
#include "il2cpp-config.h"
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowTypeResolver.h"
#include "vm/AssemblyShadowDiagnostics.h"
#include "vm/MetadataCache.h"
#include "vm/MetadataLock.h"
#include "vm/AssemblyShadowTypeKey.h"
#include "os/Thread.h"
#include <cstring>
#include <sstream>
#include <stdexcept>

extern "C" IL2CPP_EXPORT int32_t R03_ObserveMethod(const char* assemblyName,
    const char* typeNamespace, const char* typeName, const char* methodName,
    int32_t testOldExecutionGuard, char* output, int32_t capacity)
{
    if (!assemblyName || !typeNamespace || !typeName || !methodName || !output || capacity < 2)
        return -1;
    std::string json;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    const MethodInfo* baselineMethod = nullptr;
    const MethodInfo* activeMethod = nullptr;
    int32_t mapCode = static_cast<int32_t>(AssemblyShadowError::Success);
    std::string mapDetail;
    uint32_t beforeCctor = 0, afterCctor = 0;
    int32_t activeGuard = -1, baselineGuard = -1;
    int32_t caughtOldGuard = -1;
    bool cacheIdentityStable = false;
    try
    {
        // Read real, physical metadata only. Do not initialize a business type,
        // instantiate a baseline object, call the old method or fabricate rows.
        {
            il2cpp::os::FastAutoLock lock(&g_MetadataLock);
            AssemblyShadowTypeMetadataScope scope;
            const auto* baseline = MetadataCache::GetAotAssemblyByNamePhysical(assemblyName);
            if (!baseline || !baseline->image) throw std::runtime_error("MissingPhysicalBaseline");
            Il2CppClass* owner = nullptr;
            for (uint32_t index = 0; index < baseline->image->typeCount; ++index)
            {
                auto handle = MetadataCache::GetAssemblyTypeHandle(baseline->image, index);
                auto name = MetadataCache::GetTypeNamespaceAndName(handle);
                if (std::strcmp(name.first, typeNamespace) || std::strcmp(name.second, typeName)) continue;
                if (owner) throw std::runtime_error("AmbiguousPhysicalType");
                owner = MetadataCache::GetTypeInfoFromHandle(handle);
            }
            if (!owner || owner->image != baseline->image) throw std::runtime_error("WrongPhysicalTypeOwner");
            beforeCctor = owner->cctor_started;
            for (uint32_t index = 0; index < owner->method_count; ++index)
            {
                auto raw = MetadataCache::GetMethodInfo(owner, index);
                const auto* candidate = MetadataCache::GetMethodInfoFromMethodHandle(raw.handle);
                if (!candidate || candidate->klass != owner) throw std::runtime_error("WrongPhysicalMethodOwner");
                if (std::strcmp(candidate->name, methodName)) continue;
                if (baselineMethod) throw std::runtime_error("AmbiguousPhysicalMethod");
                baselineMethod = candidate;
            }
            if (!baselineMethod) throw std::runtime_error("MissingPhysicalMethod");
        }
        try
        {
            activeMethod = AssemblyShadowTypeResolver::ResolveReflectionMethod(baselineMethod);
            cacheIdentityStable = activeMethod != nullptr;
            for (int i = 0; i < 16 && cacheIdentityStable; ++i)
                cacheIdentityStable = AssemblyShadowTypeResolver::ResolveReflectionMethod(baselineMethod) == activeMethod;
        }
        catch (const ShadowTypeResolutionFailure& failure)
        { mapCode = static_cast<int32_t>(failure.error); mapDetail = failure.what(); }
        afterCctor = baselineMethod->klass->cctor_started;
        // Outside the metadata scope: test the actual production guard. It
        // records/seals the expected old-AOT failure but executes neither body.
        if (testOldExecutionGuard && activeMethod)
        {
            activeGuard = AssemblyShadow::AssertMethodIsActive(activeMethod, "R03Probe:Active") ? 1 : 0;
            baselineGuard = AssemblyShadow::AssertMethodIsActive(baselineMethod, "R03Probe:Baseline") ? 1 : 0;
            if (testOldExecutionGuard & 2)
            {
                // Only the supplementary IR fixture uses bit 2. Verify a real
                // managed exception is caught after the Boolean hook sealed the
                // first failure. Original R03 cases pass 0/1 unchanged.
                try
                {
                    AssemblyShadow::RequireActiveMethod(baselineMethod, "R03IR:CaughtBaselineOwner");
                    caughtOldGuard = 0;
                }
                catch (const Il2CppExceptionWrapper&)
                {
                    caughtOldGuard = 1;
                }
            }
        }
        AssemblyShadowState state;
        AssemblyShadow::GetState(state);
        std::ostringstream text;
        text << "{\"schemaVersion\":1,\"available\":true,\"mappingCode\":" << mapCode
            << ",\"mappingDetail\":" << AssemblyShadowDiagnostics::Quote(mapDetail)
            << ",\"baselineToken\":" << baselineMethod->token
            << ",\"baselineSlot\":" << baselineMethod->slot
            << ",\"activeToken\":" << (activeMethod ? activeMethod->token : 0)
            << ",\"activeSlot\":" << (activeMethod ? activeMethod->slot : 65535)
            << ",\"differentPhysicalMethods\":" << (activeMethod && activeMethod != baselineMethod ? "true" : "false")
            << ",\"activeOwner\":" << (activeMethod && AssemblyShadow::IsActiveShadow(activeMethod->klass->image->assembly) ? "true" : "false")
            << ",\"cacheIdentityStable\":" << (cacheIdentityStable ? "true" : "false")
            << ",\"baselineCctorBefore\":" << beforeCctor << ",\"baselineCctorAfter\":" << afterCctor
            << ",\"activeGuard\":" << activeGuard << ",\"baselineGuard\":" << baselineGuard
            << ",\"stateCode\":" << static_cast<int32_t>(state)
            << ",\"activeGeneration\":" << AssemblyShadow::ActiveGeneration();
        if (testOldExecutionGuard & 2) text << ",\"caughtOldGuard\":" << caughtOldGuard;
        text << "}";
        json = text.str();
    }
    catch (const Il2CppExceptionWrapper&)
    { json = "{\"schemaVersion\":1,\"available\":false,\"error\":\"ManagedMetadataFailure\"}"; }
    catch (const std::exception& error)
    { json = "{\"schemaVersion\":1,\"available\":false,\"error\":" + AssemblyShadowDiagnostics::Quote(error.what()) + "}"; }
    catch (...)
    { json = "{\"schemaVersion\":1,\"available\":false,\"error\":\"UnknownNativeFailure\"}"; }
#else
    json = "{\"schemaVersion\":1,\"available\":false,\"featureOff\":true}";
#endif
    if (json.size() + 1 > static_cast<size_t>(capacity)) return -2;
    std::memcpy(output, json.c_str(), json.size() + 1);
    return static_cast<int32_t>(json.size());
}

// This protocol deliberately captures native boundaries before managed JSON
// conversion. It never returns acceptance, modifies a cache or warms a type.
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW && __has_include("vm/AssemblyShadowRuntimeProbe.h")
#include "vm/AssemblyShadowRuntimeProbe.h"
#define R03_HAS_RUNTIME_PROBE HYBRIDCLR_R03_RUNTIME_PROBE
#else
#define R03_HAS_RUNTIME_PROBE 0
#endif

extern "C" IL2CPP_EXPORT int32_t R03_BeginWarmProbe(const char* assemblyName, int32_t isolateProducer)
{
#if R03_HAS_RUNTIME_PROBE
    using namespace il2cpp::vm;
    if (!assemblyName || !AssemblyShadow::ActiveGeneration()) return 0;
    // No metadata/probe mutex is held while acquiring the producer lease.
    if (isolateProducer != 0 && isolateProducer != 1) return -6;
    if (isolateProducer && !assembly_shadow_r03::ProducerFence::Instance().Acquire(
            static_cast<uint64_t>(il2cpp::os::Thread::CurrentThreadId()))) return -7;
    try
    {
        Il2CppClass* baseline = nullptr;
        {
            il2cpp::os::FastAutoLock lock(&g_MetadataLock);
            AssemblyShadowTypeMetadataScope scope;
            const auto* assembly = MetadataCache::GetAotAssemblyByNamePhysical(assemblyName);
            if (!assembly || !assembly->image) return -1;
            for (uint32_t i = 0; i < assembly->image->typeCount; ++i)
            {
                auto handle = MetadataCache::GetAssemblyTypeHandle(assembly->image, i);
                auto name = MetadataCache::GetTypeNamespaceAndName(handle);
                if (!std::strcmp(name.first, "R03") && !std::strcmp(name.second, "Node"))
                { if (baseline) return -2; baseline = MetadataCache::GetTypeInfoFromHandle(handle); }
            }
        }
        auto* active = baseline ? AssemblyShadowTypeResolver::ResolveClass(baseline) : nullptr;
        if (!active || active == baseline || !AssemblyShadow::IsActiveShadow(active->image->assembly)) return -3;
        return assembly_shadow_r03::RuntimeProbe::Begin(active, AssemblyShadow::ActiveGeneration()) ? 1 : -4;
    }
    catch (...) { return -5; }
#else
    (void)assemblyName; (void)isolateProducer; return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_MarkWarmProbe(int32_t boundary)
{
#if R03_HAS_RUNTIME_PROBE
    const bool marked = il2cpp::vm::assembly_shadow_r03::RuntimeProbe::Mark(boundary);
    const bool released = boundary != 3 || il2cpp::vm::assembly_shadow_r03::ProducerFence::Instance().Release();
    return marked && released ? 1 : -1;
#else
    (void)boundary; return 0;
#endif
}

#if R03_HAS_RUNTIME_PROBE
namespace {
using il2cpp::vm::assembly_shadow_r02::Metric;
const char* MetricName(Metric value)
{
    switch (value)
    {
#define METRIC(id, name) case Metric::id: return name;
        METRIC(AdmissionHits, "admissionCacheHits") METRIC(AdmissionMisses, "admissionCacheMisses")
        METRIC(AdmissionBuilds, "admissionProofAttempts") METRIC(AdmissionRejects, "admissionProofRejections")
        METRIC(AdmissionEntries, "admissionEntries") METRIC(AdmissionRetainedBytes, "admissionRetainedBytes")
        METRIC(AdmissionUnready, "admissionUnready") METRIC(BaselineChecks, "baselineStateChecks")
        METRIC(FieldWorkspaces, "fieldWorkspaceBuilds") METRIC(InterfaceWorkspaces, "interfaceWorkspaceBuilds")
        METRIC(LayoutChecks, "layoutCheckCalls") METRIC(GenericContextChecks, "genericContextChecks")
#undef METRIC
        default: return nullptr;
    }
}
std::string ProbePointer(const void* p)
{ std::ostringstream out; out << "0x" << std::hex << reinterpret_cast<uintptr_t>(p); return out.str(); }
void ProbeType(std::ostream& out, const void* pointer)
{
    const auto* klass = static_cast<const Il2CppClass*>(pointer);
    // This path is for published warm targets/events only. Rejected staged
    // layout identities are owned snapshots and never enter this formatter.
    if (klass && !il2cpp::vm::AssemblyShadow::ActiveGeneration())
        throw std::logic_error("Unpublished live probe identity is forbidden");
    using il2cpp::vm::AssemblyShadowDiagnostics;
    out << "{\"physical\":" << AssemblyShadowDiagnostics::Quote(ProbePointer(pointer))
        << ",\"assembly\":" << AssemblyShadowDiagnostics::Quote(klass && klass->image && klass->image->assembly ? klass->image->assembly->aname.name : "")
        << ",\"namespace\":" << AssemblyShadowDiagnostics::Quote(klass ? klass->namespaze : "")
        << ",\"name\":" << AssemblyShadowDiagnostics::Quote(klass ? klass->name : "")
        << ",\"typeKey\":" << AssemblyShadowDiagnostics::Quote(klass ? il2cpp::vm::AssemblyShadowTypeKey::Format(&klass->byval_arg) : "") << "}";
}
void UIntArray(std::ostream& out, const uint32_t* data, size_t count)
{
    out << "[";
    for (size_t i = 0; i < count && i < 16; ++i) { if (i) out << ","; out << data[i]; }
    out << "]";
}
}
#endif

extern "C" IL2CPP_EXPORT int32_t R03_ReadRuntimeProbe(char* output, int32_t capacity)
{
    if (!output || capacity < 2) return -1;
    std::string json;
#if R03_HAS_RUNTIME_PROBE
    using namespace il2cpp::vm;
    try
    {
    // Also release on exceptional managed paths that did not reach Mark(3).
    // The incomplete original probe remains invalid; cleanup never grants PASS.
    assembly_shadow_r03::ProducerFence::Instance().Release();
    assembly_shadow_r03::ProducerFence::Instance().Drain();
    const auto fence = assembly_shadow_r03::ProducerFence::Instance().Read();
    const auto r = assembly_shadow_r03::RuntimeProbe::Read();
    std::ostringstream out; out << std::boolalpha;
    out << "{\"schemaVersion\":3,\"available\":true,\"policy\":\"R03ExactAllocationWindowV1\",\"used\":" << r.used
        << ",\"sealed\":" << r.sealed << ",\"invalid\":" << r.invalid << ",\"overflow\":" << r.overflow
        << ",\"generation\":" << r.generation << ",\"ownerThread\":" << r.owner << ",\"target\":";
    ProbeType(out, r.target);
    out << ",\"eventCapacity\":" << assembly_shadow_r03::RuntimeProbe::kEvents << ",\"samples\":[";
    for (size_t i = 0; i < r.samples; ++i)
    {
        if (i) out << ","; const auto& s = r.sample[i];
        out << "{\"label\":" << s.label << ",\"eventEnd\":" << s.eventEnd << ",\"thread\":" << s.thread
            << ",\"saturated\":" << s.saturated << ",\"droppedThreads\":" << s.droppedThreads << ",\"counters\":{";
        bool comma = false;
        for (size_t m = 0; m < static_cast<size_t>(Metric::Count); ++m)
            if (const char* name = MetricName(static_cast<Metric>(m)))
            { if (comma) out << ","; comma = true; out << "\"" << name << "\":" << s.values[m]; }
        out << "}}";
    }
    out << "],\"events\":[";
    for (size_t i = 0; i < r.events; ++i)
    {
        if (i) out << ","; const auto& e = r.event[i];
        out << "{\"index\":" << i << ",\"metric\":" << AssemblyShadowDiagnostics::Quote(MetricName(e.metric))
            << ",\"amount\":" << e.amount << ",\"phase\":" << e.phase << ",\"thread\":" << e.thread
            << ",\"generation\":" << e.key.generation << ",\"domain\":" << e.key.domain
            << ",\"context\":" << AssemblyShadowDiagnostics::Quote(ProbePointer(e.key.context))
            << ",\"site\":" << AssemblyShadowDiagnostics::Quote(e.site) << ",\"type\":";
        ProbeType(out, e.key.physical);
        out << ",\"producer\":{\"osThread\":" << e.producer.osThread
            << ",\"recognizedArrayPool\":" << e.producer.recognizedArrayPool
            << ",\"finalizerType\":";
        if (e.producer.finalizerClass) ProbeType(out, e.producer.finalizerClass); else out << "null";
        out << ",\"callback\":";
        const auto* callback = static_cast<const MethodInfo*>(e.producer.callback);
        if (callback)
        {
            out << "{\"name\":" << AssemblyShadowDiagnostics::Quote(callback->name)
                << ",\"token\":" << callback->token << ",\"declaringType\":";
            ProbeType(out, callback->klass); out << "}";
        }
        else out << "null";
        out << "}}";
    }
    out << "],\"layouts\":[";
    for (size_t i = 0; i < r.layouts; ++i)
    {
        if (i) out << ","; const auto& l = r.layout[i];
        // No target pointer dereference or metadata decoding after the private
        // staged owner has ended. These exact bytes were captured by RecordLayout.
        out << "{\"baseline\":"; l.baselineIdentity.WriteJson(out);
        out << ",\"target\":"; l.targetIdentity.WriteJson(out);
        out << ",\"identityPolicy\":" << AssemblyShadowDiagnostics::Quote(assembly_shadow_r03::ProbeTypeSnapshot::Policy())
            << ",\"baselineIdentityStatus\":" << AssemblyShadowDiagnostics::Quote(l.baselineIdentity.StatusName())
            << ",\"targetIdentityStatus\":" << AssemblyShadowDiagnostics::Quote(l.targetIdentity.StatusName());
#define SCALAR(name) out << ",\"" #name "\":" << l.name;
        SCALAR(fieldsChanged) SCALAR(baselineReady) SCALAR(targetReady) SCALAR(targetDefinitionReady)
        SCALAR(physicalProof) SCALAR(sourceSizeInited) SCALAR(targetSizeInited) SCALAR(sourcePending) SCALAR(targetPending)
        SCALAR(baselineInitialized) SCALAR(baselineVtable) SCALAR(baselineCctor) SCALAR(targetInitialized)
        SCALAR(targetVtable) SCALAR(targetCctor) SCALAR(sourceSize) SCALAR(targetSize) SCALAR(sourceNativeSize) SCALAR(targetNativeSize)
        SCALAR(sourceFieldCount) SCALAR(targetFieldCount) SCALAR(truncated) SCALAR(error)
#undef SCALAR
#define ARRAY(name, count) out << ",\"" #name "\":"; UIntArray(out, l.name, l.count);
        ARRAY(sourceOffsets, sourceFieldCount) ARRAY(sourceAttrs, sourceFieldCount)
        ARRAY(targetOffsets, targetFieldCount) ARRAY(targetAttrs, targetFieldCount) ARRAY(targetStorage, targetFieldCount)
#undef ARRAY
        const auto* baseline = static_cast<const Il2CppClass*>(l.baseline);
        out << ",\"baselineInitializedAtRead\":" << bool(baseline && baseline->initialized)
            << ",\"baselineVtableAtRead\":" << bool(baseline && baseline->is_vtable_initialized)
            << ",\"baselineCctorAtRead\":" << (baseline ? baseline->cctor_started : 0) << "}";
    }
    out << "],\"producerFence\":{\"policy\":\"R03ArrayPoolFinalizerFenceV1\"";
#define FENCE(name) out << ",\"" #name "\":" << fence.name;
    FENCE(requested) FENCE(acquired) FENCE(released) FENCE(expired) FENCE(invalid) FENCE(drained)
    FENCE(admitted) FENCE(completed) FENCE(deferred) FENCE(deferredCompleted) FENCE(ownerOsThread) FENCE(elapsedMicros) FENCE(leaseMs)
#undef FENCE
    out << "},\"runtimeAcceptance\":false}"; json = out.str();
    }
    catch (...) { return -3; }
#else
    json = "{\"schemaVersion\":1,\"available\":false,\"runtimeAcceptance\":false}";
#endif
    if (json.size() + 1 > static_cast<size_t>(capacity)) return -2;
    std::memcpy(output, json.c_str(), json.size() + 1); return static_cast<int32_t>(json.size());
}

// IR-only opt-in stimulus: invokes the production type-failure boundary, not
// a fake state write. A separate fresh Player must validate its consequences.
// No production build or original R03 Player imports this exported function.
extern "C" IL2CPP_EXPORT int32_t R03_IR_ForceTypeFailure()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    try
    {
        il2cpp::vm::AssemblyShadow::FailTypeResolution(
            il2cpp::vm::AssemblyShadowError::ReferenceResolutionFailed,
            "R03IR synthetic type-resolution failure (test-only stimulus)");
        return 0; // A failure may never return normally.
    }
    catch (const Il2CppExceptionWrapper&) { return 1; }
    catch (...) { return -1; }
#else
    return -2;
#endif
}

// IR-LOCAL-RUNTIME-01: supplementary fixed native reporting witness.
// This is a direct Runtime::Invoke integration check inside the real Player;
// it must not be mislabeled as an unhandled Unity engine callback experiment.
#include "vm/Class.h"
#include "vm/Image.h"
#include "vm/Object.h"
#include "vm/Runtime.h"
#include "vm/AssemblyShadowTerminalReporting.h"
#include <cstdio>

extern "C" IL2CPP_EXPORT void R03_IR_TracePhase(int32_t phase)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    il2cpp::vm::assembly_shadow_reporting::TracePhase(phase);
#else
    std::fprintf(stderr, "[AssemblyShadowPhase] phase=%d featureOff=1\n", static_cast<int>(phase));
    std::fflush(stderr);
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_ProbeTerminalReporting()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    try
    {
        AssemblyShadowState state;
        if (AssemblyShadow::GetState(state) != AssemblyShadowError::Success ||
            state != AssemblyShadowState::FailedAfterCommit) return -1;
        const Il2CppAssembly* core = MetadataCache::GetAotAssemblyByNamePhysical("UnityEngine.CoreModule");
        if (!core || !core->image) return -2;
        Il2CppClass* debug = Image::ClassFromName(core->image, "UnityEngine", "Debug");
        if (!debug || debug->image != core->image) return -3;
        const MethodInfo* handler = Class::GetMethodFromName(debug, "CallOverridenDebugHandler", 2);
        const MethodInfo* enabled = Class::GetMethodFromName(debug, "IsLoggingEnabled", 0);
        if (!handler || !enabled) return -4;
        const uint64_t before = assembly_shadow_reporting::HandledCounter().load(std::memory_order_relaxed);
        int32_t mask = 0;
        void* args[2] = {nullptr, nullptr}; // No managed body may consume these.
        Il2CppException* error = nullptr;
        Il2CppObject* a = Runtime::Invoke(handler, nullptr, args, &error);
        if (!error && a && a->klass == il2cpp_defaults.boolean_class &&
            *static_cast<bool*>(Object::Unbox(a))) mask |= 1;
        // IsLoggingEnabled is NOT exempted by this one-method native adapter.
        error = nullptr;
        Il2CppObject* b = Runtime::Invoke(enabled, nullptr, nullptr, &error);
        if (!b && error) mask |= 2;
        if (assembly_shadow_reporting::HandledCounter().load(std::memory_order_relaxed) == before + 1) mask |= 4;
        // The ordinary guard still denies both physical methods; the callback
        // was replaced with native data, never admitted as managed execution.
        if (!AssemblyShadow::AssertMethodIsActive(handler, "IR:handler-still-denied") &&
            !AssemblyShadow::AssertMethodIsActive(enabled, "IR:enabled-still-denied")) mask |= 8;
        return mask; // Exactly 15 is required by the current raw verifier.
    }
    catch (...) { R03_IR_TracePhase(980); return -5; }
#else
    return 0;
#endif
}

// K diagnostic transport: bind the test report while healthy, then read only
// its prebound instance fields. No managed serializer or callback after poison.
// This source is installed only as the explicit R03 test overlay, never a
// production exception/serialization permission.
#include "vm/Field.h"
#include "gc/GCHandle.h"
#include <fcntl.h>
#include <unistd.h>
#include <thread>
#include <limits>

namespace r03_ir_evidence {
enum WireKind { WireString, WireInt32, WireBoolean, WireException };
struct BoundField { const char* name; WireKind kind; int32_t offset; };
static BoundField fields[] = {
    {"kind", WireString, 0},
    {"result", WireString, 0},
    {"runId", WireString, 0},
    {"caseId", WireString, 0},
    {"requestSha256", WireString, 0},
    {"stimulus", WireString, 0},
    {"unityVersion", WireString, 0},
    {"platform", WireString, 0},
    {"error", WireString, 0},
    {"nativeGuardJson", WireString, 0},
    {"activeReflectionException", WireString, 0},
    {"activeDelegateException", WireString, 0},
    {"aotReflectionException", WireString, 0},
    {"firstRecovery", WireString, 0},
    {"finalRecovery", WireString, 0},
    {"finalDiagnostics", WireString, 0},
    {"finalExecutionDiagnostics", WireString, 0},
    {"schemaVersion", WireInt32, 0},
    {"processId", WireInt32, 0},
    {"initialState", WireInt32, 0},
    {"poisonedState", WireInt32, 0},
    {"finalState", WireInt32, 0},
    {"nativeStimulusReturn", WireInt32, 0},
    {"preActiveReflection", WireInt32, 0},
    {"preActiveDelegate", WireInt32, 0},
    {"preCanaryCount", WireInt32, 0},
    {"finalCanaryCount", WireInt32, 0},
    {"preShadowField", WireInt32, 0},
    {"finalShadowField", WireInt32, 0},
    {"nativePhase", WireInt32, 0},
    {"failurePhase", WireInt32, 0},
    {"terminalReportingProbeMask", WireInt32, 0},
    {"reserveBeforeMask", WireInt32, 0},
    {"reserveAfterGcMask", WireInt32, 0},
    {"gcCollectionsBefore", WireInt32, 0},
    {"gcCollectionsAfter", WireInt32, 0},
    {"shadowFieldReadable", WireBoolean, 0},
    {"prePositive", WireBoolean, 0},
    {"activeReflectionAttempted", WireBoolean, 0},
    {"activeReflectionSucceeded", WireBoolean, 0},
    {"activeDelegateAttempted", WireBoolean, 0},
    {"activeDelegateSucceeded", WireBoolean, 0},
    {"aotReflectionAttempted", WireBoolean, 0},
    {"aotReflectionSucceeded", WireBoolean, 0},
    {"recoveryStable", WireBoolean, 0},
    {"fixedDiagnosticsReadable", WireBoolean, 0},
    {"acceptance", WireBoolean, 0},
    {"activeReflectionError", WireException, 0},
    {"activeDelegateError", WireException, 0},
    {"aotReflectionError", WireException, 0},
    {"caughtFailure", WireException, 0}
};
static FILE* stream = nullptr;
static Il2CppObject* report = nullptr;
static Il2CppClass* reportClass = nullptr;
static uint32_t reportRoot = 0;
static bool prepared = false;
static std::thread::id writerThread;
static size_t bytesWritten = 0;
static char nativeGuard[16384] = {};
static int nativeGuardLength = 0;
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
static Il2CppObject* reserveBefore = nullptr;
static uint32_t reserveHandleBefore = 0;
#endif
[[noreturn]] void Fatal(const char* reason)
{
    std::fprintf(stderr, "[R03NativeEvidence] failed=%s\n", reason);
    std::fflush(stderr);
    std::_Exit(74); // Failed diagnostic process, never a successful witness.
}
void Put(char c)
{
    if (++bytesWritten > 2u * 1024u * 1024u || std::fputc(c, stream) == EOF)
        Fatal("OutputLimitOrWrite");
}
void Text(const char* value)
{
    for (; *value; ++value) Put(*value);
}
void QuotedUtf16(const Il2CppString* value)
{
    if (!value) { Text("null"); return; }
    if (reinterpret_cast<const Il2CppObject*>(value)->klass != il2cpp_defaults.string_class || value->length < 0 || value->length > 262144)
        Fatal("StringIdentityOrLength");
    Put('"');
    const char* hex = "0123456789abcdef";
    for (int32_t i = 0; i < value->length; ++i)
    {
        const unsigned c = static_cast<uint16_t>(value->chars[i]);
        if (c == '"' || c == '\\') { Put('\\'); Put(static_cast<char>(c)); }
        else if (c >= 32 && c < 127) Put(static_cast<char>(c));
        else { Text("\\u"); Put(hex[(c >> 12) & 15]); Put(hex[(c >> 8) & 15]); Put(hex[(c >> 4) & 15]); Put(hex[c & 15]); }
    }
    Put('"');
}
void QuotedAscii(const char* value, size_t length)
{
    Put('"');
    const char* hex = "0123456789abcdef";
    for (size_t i = 0; i < length; ++i)
    {
        unsigned c = static_cast<unsigned char>(value[i]);
        if (c == '"' || c == '\\') { Put('\\'); Put(static_cast<char>(c)); }
        else if (c >= 32 && c < 127) Put(static_cast<char>(c));
        else { Text("\\u00"); Put(hex[c >> 4]); Put(hex[c & 15]); }
    }
    Put('"');
}
const BoundField* Find(const char* name)
{
    for (const auto& f : fields) if (std::strcmp(f.name, name) == 0) return &f;
    return nullptr;
}
template<typename T> T Read(const BoundField& f)
{
    T value{};
    std::memcpy(&value, reinterpret_cast<const char*>(report) + f.offset, sizeof(T));
    return value;
}
void ExceptionName(const char* fieldName)
{
    const auto* f = Find(fieldName);
    if (!f) Fatal("MissingExceptionBinding");
    Il2CppObject* e = Read<Il2CppObject*>(*f);
    if (!e) { Text("null"); return; }
    const Il2CppClass* type = e->klass;
    const Il2CppClass* ancestor = type;
    for (unsigned depth = 0; ancestor && ancestor != il2cpp_defaults.exception_class && depth < 64; ++depth)
        ancestor = ancestor->parent;
    if (ancestor != il2cpp_defaults.exception_class || !type || !type->name || !type->namespaze)
        Fatal("ExceptionIdentity");
    // Metadata names are not formatted by managed Exception.GetType/ToString.
    char name[512];
    int count = std::snprintf(name, sizeof(name), "%s.%s", type->namespaze, type->name);
    if (count < 0 || static_cast<size_t>(count) >= sizeof(name)) Fatal("ExceptionNameLimit");
    QuotedAscii(name, static_cast<size_t>(count));
}
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_PrepareEvidence(uint32_t managedHandle, const char* output)
{
    using namespace il2cpp::vm;
    using namespace r03_ir_evidence;
    try
    {
        AssemblyShadowState state;
        AssemblyShadow::GetState(state);
        if (state != AssemblyShadowState::Disabled || prepared || !managedHandle || !output ||
            output[0] != '/' || std::strlen(output) > 4095) return -1;
        Il2CppObject* object = il2cpp::gc::GCHandle::GetTarget(managedHandle);
        Il2CppClass* klass = object ? object->klass : nullptr;
        const Il2CppClass* outer = klass ? klass->declaringType : nullptr;
        if (!klass || !outer || !klass->name || std::strcmp(klass->name, "Report") ||
            !outer->name || std::strcmp(outer->name, "R03TerminalPlayer") || !outer->namespaze ||
            std::strcmp(outer->namespaze, "AssemblyShadow.R03.IR") || !klass->image ||
            !klass->image->assembly || !klass->image->assembly->aname.name ||
            std::strcmp(klass->image->assembly->aname.name, "Assembly-CSharp")) return -2;
        Class::Init(klass); // Healthy metadata binding, NEVER done in Finish.
        for (auto& binding : fields)
        {
            FieldInfo* field = Class::GetFieldFromName(klass, binding.name);
            const int type = field && field->type ? field->type->type : -1;
            const int expected = binding.kind == WireInt32 ? IL2CPP_TYPE_I4 :
                binding.kind == WireBoolean ? IL2CPP_TYPE_BOOLEAN :
                binding.kind == WireString ? IL2CPP_TYPE_STRING : IL2CPP_TYPE_CLASS;
            size_t size = binding.kind == WireInt32 ? 4 : binding.kind == WireBoolean ? 1 : sizeof(void*);
            if (!field || !field->type || field->type->byref || type != expected ||
                (field->type->attrs & FIELD_ATTRIBUTE_STATIC) || field->offset < static_cast<int32_t>(sizeof(Il2CppObject)) ||
                static_cast<uint64_t>(field->offset) + size > klass->instance_size) return -3;
            binding.offset = field->offset;
        }
        const uint32_t handle = il2cpp::gc::GCHandle::New(object, true);
        if (!handle || il2cpp::gc::GCHandle::GetTarget(handle) != object) return -4;
        const int fd = ::open(output, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
        if (fd < 0) { il2cpp::gc::GCHandle::Free(handle); return -5; }
        FILE* opened = ::fdopen(fd, "w");
        if (!opened) { ::close(fd); il2cpp::gc::GCHandle::Free(handle); return -6; }
        stream = opened; report = object; reportClass = klass; reportRoot = handle;
        writerThread = std::this_thread::get_id(); prepared = true;
        return 1;
    }
    catch (...) { return -7; }
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_ProbeReserve(int32_t phase)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace assembly_shadow_reporting;
    using namespace r03_ir_evidence;
    try
    {
        AssemblyShadowState state;
        AssemblyShadow::GetState(state);
        if (state != AssemblyShadowState::Disabled || (phase != 0 && phase != 1)) return -1;
        auto& reserve = BooleanReserve();
        Il2CppObject* object = reserve.object.load(std::memory_order_acquire);
        if (phase == 0) { reserveBefore = object; reserveHandleBefore = reserve.pinnedHandle; }
        int mask = 0;
        if (object && object == reserveBefore && reserve.pinnedHandle == reserveHandleBefore) mask |= 1;
        if (object && IsReadyBoolean(object->klass) && HasTruePayload(object)) mask |= 2;
        if (reserve.pinnedHandle && il2cpp::gc::GCHandle::GetHandleType(reserve.pinnedHandle) == il2cpp::gc::HANDLE_PINNED) mask |= 4;
        if (reserve.pinnedHandle && il2cpp::gc::GCHandle::GetTarget(reserve.pinnedHandle) == object) mask |= 8;
        return mask;
    }
    catch (...) { return -2; }
#else
    (void)phase; return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_TriggerAndRecord(int32_t stimulus)
{
    using namespace r03_ir_evidence;
    if (!prepared || std::this_thread::get_id() != writerThread) return -10;
    if (stimulus == 13) return R03_IR_ForceTypeFailure();
    if (stimulus != 21) return -11;
    nativeGuardLength = R03_ObserveMethod("Methods", "R03", "Node", "Keep", 3,
        nativeGuard, sizeof(nativeGuard));
    if (nativeGuardLength <= 0 || nativeGuardLength >= static_cast<int>(sizeof(nativeGuard))) return -12;
    nativeGuard[nativeGuardLength] = 0;
    // The original producer's exact JSON is retained, then independently parsed
    // by the existing host verifier. No managed JSON parsing is needed here.
    if (!std::strstr(nativeGuard, "\"available\":true") ||
        !std::strstr(nativeGuard, "\"activeGuard\":1") ||
        !std::strstr(nativeGuard, "\"baselineGuard\":0") ||
        !std::strstr(nativeGuard, "\"caughtOldGuard\":1") ||
        !std::strstr(nativeGuard, "\"stateCode\":9")) return -13;
    return 1;
}

extern "C" IL2CPP_EXPORT void R03_IR_FinishEvidenceAndExit()
{
    using namespace r03_ir_evidence;
    if (!prepared || !stream || !reportRoot || !report || report->klass != reportClass ||
        std::this_thread::get_id() != writerThread) Fatal("UnpreparedOrWrongWriter");
    Text("{"); bool first = true;
    for (const auto& f : fields)
    {
        if (f.kind == WireException) continue;
        if (!first) Put(',');
        first = false;
        QuotedAscii(f.name, std::strlen(f.name)); Put(':');
        if (std::strcmp(f.name, "nativeGuardJson") == 0 && nativeGuardLength > 0)
            QuotedAscii(nativeGuard, static_cast<size_t>(nativeGuardLength));
        else if (std::strcmp(f.name, "activeReflectionException") == 0) ExceptionName("activeReflectionError");
        else if (std::strcmp(f.name, "activeDelegateException") == 0) ExceptionName("activeDelegateError");
        else if (std::strcmp(f.name, "aotReflectionException") == 0) ExceptionName("aotReflectionError");
        else if (f.kind == WireString) QuotedUtf16(Read<Il2CppString*>(f));
        else if (f.kind == WireBoolean)
        {
            const uint8_t value = Read<uint8_t>(f);
            if (value > 1) Fatal("BooleanRepresentation");
            Text(value ? "true" : "false");
        }
        else
        {
            char number[32]; int count = std::snprintf(number, sizeof(number), "%d", Read<int32_t>(f));
            if (count < 0 || static_cast<size_t>(count) >= sizeof(number)) Fatal("IntegerFormat");
            Text(number);
        }
    }
    Text(",\"nativeCaughtException\":"); ExceptionName("caughtFailure");
    Text(",\"nativeReportTransport\":\"PreboundFieldSnapshotV1\",\"nativeWriterComplete\":true}\n");
    const int fd = ::fileno(stream);
    if (std::fflush(stream) != 0 || ::fsync(fd) != 0 || std::fclose(stream) != 0) Fatal("FlushOrClose");
    stream = nullptr;
    std::_Exit(0); // Host verifies raw facts. This test does NOT exercise shutdown.
}

// A separate engine-only request reaches this without a managed catch/finally.
// The existing native observer writes its own request-bound result.
extern "C" IL2CPP_EXPORT void R03_IR_UncaughtTypeFailure(const char* runId)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    if (!runId || std::strlen(runId) != 32) r03_ir_evidence::Fatal("EngineRunId");
    for (unsigned i = 0; i < 32; ++i)
        if (!((runId[i] >= '0' && runId[i] <= '9') || (runId[i] >= 'a' && runId[i] <= 'f')))
            r03_ir_evidence::Fatal("EngineRunId");
    il2cpp::vm::AssemblyShadow::FailTypeResolution(
        il2cpp::vm::AssemblyShadowError::ReferenceResolutionFailed,
        std::string("R03K engine-originated witness ") + runId);
#else
    (void)runId;
#endif
    r03_ir_evidence::Fatal("EngineFailureReturned");
}
