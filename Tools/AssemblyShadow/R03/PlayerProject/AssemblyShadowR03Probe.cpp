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

// K test-only transport: preopen once while healthy; persist the actual C#
// observation fields without managed reflection/formatting/file virtual calls.
// Not a production logging, allocation, recovery, or acceptance API.
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include <atomic>
#include <cstdint>
#include <cstdlib>
#include <fcntl.h>
#include <cerrno>
#include <unistd.h>
#include "gc/GCHandle.h"
#include "gc/GarbageCollector.h"
namespace r03_ir_snapshot {
constexpr size_t TextLimit = 262144;
constexpr const char* IntNames[] = {"initialState","poisonedState","finalState","nativeStimulusReturn","preActiveReflection","preActiveDelegate","preCanaryCount","finalCanaryCount","preShadowField","finalShadowField","nativePhase","failurePhase","terminalReportingProbeMask","reserveGcProbeMask","shadowFieldReadable","prePositive","activeReflectionAttempted","activeReflectionSucceeded","activeDelegateAttempted","activeDelegateSucceeded","aotReflectionAttempted","aotReflectionSucceeded","recoveryStable","fixedDiagnosticsReadable","acceptance"};
constexpr const char* TextNames[] = {"result","runId","caseId","requestSha256","stimulus","unityVersion","platform","error","nativeGuardJson","activeReflectionException","activeDelegateException","aotReflectionException","firstRecovery","finalRecovery","finalDiagnostics","finalExecutionDiagnostics"};
constexpr int IntCount = 25;
constexpr int FirstBool = 14;
constexpr int TextCount = 16;
static std::atomic<int> state{0}; // 0 unused,1 open,2 sealed,3 sealing,-1 failed
static FILE* stream = nullptr;
static int32_t ints[IntCount] = {};
static bool haveInt[IntCount] = {}, haveText[TextCount] = {}, nullText[TextCount] = {};
static char texts[TextCount][TextLimit + 1] = {};

// The 262144-byte backing slice and whole-report text budget are unchanged.
// Slot 15 alone may store losslessly packed bytes instead of verbatim bytes.
// It fits that same byte allocation and never changes the emitted JSON schema.
// A report's total unescaped text budget is the original 16 * TextLimit.
constexpr size_t OriginalReportTextBudget = TextCount * TextLimit;
static size_t decodedTextBytes = 0;
static bool packedExecution = false;
static size_t packedBytes = 0, executionDecodedBytes = 0;
static uint64_t executionByteCheck = 0;
constexpr uint64_t ByteCheckSeed = 14695981039346656037ULL;
static uint64_t ByteCheck(uint64_t value, unsigned char byte) noexcept
{ return (value ^ byte) * 1099511628211ULL; }
constexpr const char* DiagnosticTokens[] = {
    "\"logicalAssembly\":", "\"typeKey\":", "\"executionModeCode\":",
    "\"executionMode\":", "\"physicalImageKind\":", "\"isActive\":",
    "\"cctorStarted\":", "\"cctorFinished\":", "\"hasInitializationException\":",
    "\"staticStoragePointer\":", "\"pointerDetailsAvailable\":", "\"staticStorageAvailable\":",
    "\"schemaVersion\":", "\"stateCode\":", "\"generation\":", "\"AotBaseline\"",
    "\"InterpreterShadow\"", "\"Interpreter\"", "\"Aot\"", ":false", ":true"
};
constexpr size_t DiagnosticTokenCount = sizeof(DiagnosticTokens) / sizeof(DiagnosticTokens[0]);
static_assert(DiagnosticTokenCount < 255, "Byte token codes required");
// 0xff,0 encodes a literal 0xff. Other second bytes are 1-based dictionary
// indices. Ordinary bytes are literal. Expansion is validated before sealing.
static bool PackExecution(const char* value, size_t bytes) noexcept
{
    size_t input = 0, written = 0;
    while (input < bytes)
    {
        size_t token = 0, matched = 0;
        for (size_t i = 0; i < DiagnosticTokenCount; ++i)
        {
            const size_t n = std::strlen(DiagnosticTokens[i]);
            if (n <= bytes - input && std::memcmp(value + input, DiagnosticTokens[i], n) == 0)
            { token = i + 1; matched = n; break; }
        }
        const unsigned char c = static_cast<unsigned char>(value[input]);
        const size_t needed = matched || c == 255 ? 2 : 1;
        if (needed > TextLimit - written) return false;
        if (matched || c == 255)
        {
            texts[15][written++] = static_cast<char>(255);
            texts[15][written++] = static_cast<char>(token);
            input += matched ? matched : 1;
        }
        else { texts[15][written++] = value[input++]; }
    }
    uint64_t check = ByteCheckSeed;
    for (size_t i = 0; i < bytes; ++i) check = ByteCheck(check, static_cast<unsigned char>(value[i]));
    executionByteCheck = check; // Internal corruption check, not a cryptographic source proof.
    packedBytes = written;
    executionDecodedBytes = bytes;
    packedExecution = true;
    return true;
}
static bool CheckPackedExecution() noexcept
{
    size_t input = 0, decoded = 0;
    uint64_t check = ByteCheckSeed;
    if (!packedExecution || packedBytes > TextLimit || executionDecodedBytes > OriginalReportTextBudget)
        return false;
    while (input < packedBytes)
    {
        const unsigned char c = static_cast<unsigned char>(texts[15][input++]);
        size_t n = 1;
        if (c == 255)
        {
            if (input == packedBytes) return false;
            const unsigned char code = static_cast<unsigned char>(texts[15][input++]);
            if (code > DiagnosticTokenCount) return false;
            if (code)
            {
                const char* token = DiagnosticTokens[code - 1];
                n = std::strlen(token);
                for (size_t i = 0; i < n; ++i) check = ByteCheck(check, static_cast<unsigned char>(token[i]));
            }
            else check = ByteCheck(check, 255);
        }
        else check = ByteCheck(check, c);
        if (n > executionDecodedBytes - decoded) return false;
        decoded += n;
    }
    return decoded == executionDecodedBytes && check == executionByteCheck;
}
static void QuotedByte(FILE* f, unsigned char c)
{
    if (c == '"' || c == '\\') { std::fputc('\\', f); std::fputc(c, f); }
    else if (c < 32) std::fprintf(f, "\\u%04x", static_cast<unsigned>(c));
    else std::fputc(c, f);
}
static void QuotePackedExecution(FILE* f)
{
    // The complete compressed stream and expansion length were checked before
    // any raw output began; output reconstructs every original byte.
    std::fputc('"', f);
    for (size_t i = 0; i < packedBytes;)
    {
        const unsigned char c = static_cast<unsigned char>(texts[15][i++]);
        if (c != 255) { QuotedByte(f, c); continue; }
        const unsigned char code = static_cast<unsigned char>(texts[15][i++]);
        if (!code) { QuotedByte(f, 255); continue; }
        for (const unsigned char* p = reinterpret_cast<const unsigned char*>(DiagnosticTokens[code-1]); *p; ++p)
            QuotedByte(f, *p);
    }
    std::fputc('"', f);
}

static std::atomic<uint32_t> intMask{0}, textMask{0};
static std::atomic<int> firstFailure{0};
static std::atomic_flag writerBusy = ATOMIC_FLAG_INIT;
// First native failure is supplemental evidence, never a replacement for raw.
// No managed method, dynamic string, new report path or larger limit is used.
static int Reject(const char* operation, int field, int reason, size_t length = 0,
                  int errorNumber = 0) noexcept
{
    const int previous = state.exchange(-1, std::memory_order_acq_rel);
    int expected = 0;
    if (firstFailure.compare_exchange_strong(expected, reason, std::memory_order_acq_rel))
    {
        std::fprintf(stderr,
            "[R03SnapshotFailure] version=1 pid=%d operation=%s field=%d reason=%d previousState=%d length=%zu limit=%zu errno=%d intMask=%08x textMask=%08x\n",
            static_cast<int>(::getpid()), operation, field, reason, previous,
            length, TextLimit, errorNumber, intMask.load(std::memory_order_acquire),
            textMask.load(std::memory_order_acquire));
        std::fflush(stderr);
    }
    return -1;
}
struct WriterCall
{
    bool owns;
    WriterCall() noexcept : owns(!writerBusy.test_and_set(std::memory_order_acquire)) {}
    ~WriterCall() { if (owns) writerBusy.clear(std::memory_order_release); }
};
static void Quote(FILE* f, const char* text)
{
    if (!text) { std::fputs("null", f); return; }
    std::fputc('"', f);
    for (const unsigned char* p = reinterpret_cast<const unsigned char*>(text); *p; ++p)
    {
        if (*p == '"' || *p == '\\') { std::fputc('\\', f); std::fputc(*p, f); }
        else if (*p < 32) std::fprintf(f, "\\u%04x", static_cast<unsigned>(*p));
        else std::fputc(*p, f);
    }
    std::fputc('"', f);
}
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportOpen(const char* path)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("open", -1, 1);
    int expected = 0;
    if (!state.compare_exchange_strong(expected, 1)) return Reject("open", -1, 2);
    if (!path || path[0] != '/') return Reject("open", -1, 3);
    errno = 0;
    int fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (fd < 0) return Reject("open", -1, 4, 0, errno);
    errno = 0;
    stream = ::fdopen(fd, "w");
    if (!stream)
    {
        const int saved = errno;
        ::close(fd);
        return Reject("fdopen", -1, 5, 0, saved);
    }
    return 1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportInt(int32_t field, int32_t value)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("int", field, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("int", field, 2);
    if (field < 0 || field >= IntCount) return Reject("int", field, 6);
    if (haveInt[field]) return Reject("int", field, 7);
    if (field >= FirstBool && value != 0 && value != 1) return Reject("int", field, 8);
    ints[field] = value; haveInt[field] = true;
    intMask.fetch_or(uint32_t(1) << field, std::memory_order_release);
    return state.load(std::memory_order_acquire) == 1 ? 1 : -1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportText(int32_t field, const char* value)
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("text", field, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("text", field, 2);
    if (field < 0 || field >= TextCount) return Reject("text", field, 6);
    if (haveText[field]) return Reject("text", field, 7);
    size_t n = value ? ::strnlen(value, TextLimit + 1) : 0;
    if (n > TextLimit)
    {
        // No unbounded scan, allocation, truncated record or new file path.
        // Other text fields retain their original direct representation.
        if (field != 15) return Reject("text", field, 9, n);
        n = ::strnlen(value, OriginalReportTextBudget + 1);
        if (n > OriginalReportTextBudget) return Reject("text-budget", field, 18, n);
        if (!PackExecution(value, n)) return Reject("text", field, 9, n);
    }
    else if (value) std::memcpy(texts[field], value, n + 1);
    if (n > OriginalReportTextBudget - decodedTextBytes)
        return Reject("text-budget", field, 18, n);
    decodedTextBytes += n;
    nullText[field] = value == nullptr; haveText[field] = true;
    textMask.fetch_or(uint32_t(1) << field, std::memory_order_release);
    return state.load(std::memory_order_acquire) == 1 ? 1 : -1;
}
extern "C" IL2CPP_EXPORT int32_t R03_IR_ReportSeal()
{
    using namespace r03_ir_snapshot;
    WriterCall call;
    if (!call.owns) return Reject("seal", -1, 1);
    if (state.load(std::memory_order_acquire) != 1) return Reject("seal", -1, 2);
    if (!stream) return Reject("seal", -1, 10);
    for (int i = 0; i < IntCount; ++i)
        if (!haveInt[i]) return Reject("missing-int", i, 11);
    for (int i = 0; i < TextCount; ++i)
        if (!haveText[i]) return Reject("missing-text", i, 12);
    if (packedExecution && !CheckPackedExecution()) return Reject("packed-text", 15, 17);
    int expected = 1;
    if (!state.compare_exchange_strong(expected, 3)) return Reject("seal", -1, 2);
    errno = 0;
    std::fprintf(stream, "{\"schemaVersion\":1,\"kind\":\"R03IRPostPoisonEntryV1\","
        "\"reportTransport\":\"NativePreopenedSnapshotV1\",\"processId\":%d", static_cast<int>(::getpid()));
    for (int i = 0; i < IntCount; ++i)
    {
        std::fputc(',', stream); Quote(stream, IntNames[i]); std::fputc(':', stream);
        if (i < FirstBool) std::fprintf(stream, "%d", ints[i]);
        else std::fputs(ints[i] ? "true" : "false", stream);
    }
    for (int i = 0; i < TextCount; ++i)
    {
        std::fputc(',', stream); Quote(stream, TextNames[i]); std::fputc(':', stream);
        if (i == 15 && packedExecution) QuotePackedExecution(stream);
        else Quote(stream, nullText[i] ? nullptr : texts[i]);
    }
    std::fputs("}\n", stream);
    bool ok = true;
    if (std::ferror(stream)) { Reject("write", -1, 13, 0, errno); ok = false; }
    errno = 0;
    if (std::fflush(stream) != 0) { Reject("flush", -1, 14, 0, errno); ok = false; }
    errno = 0;
    if (::fsync(::fileno(stream)) != 0) { Reject("fsync", -1, 15, 0, errno); ok = false; }
    errno = 0;
    if (std::fclose(stream) != 0) { Reject("close", -1, 16, 0, errno); ok = false; }
    stream = nullptr;
    expected = 3;
    if (!ok || !state.compare_exchange_strong(expected, 2)) return -1;
    if (packedExecution)
    {
        std::fprintf(stderr, "[R03SnapshotPacked] version=1 pid=%d field=15 inputBytes=%zu storedBytes=%zu totalTextBytes=%zu totalTextLimit=%zu\n",
            static_cast<int>(::getpid()), executionDecodedBytes, packedBytes, decodedTextBytes, OriginalReportTextBudget);
        std::fflush(stderr);
    }
    std::fprintf(stderr,
        "[R03SnapshotSealed] version=1 pid=%d intMask=%08x textMask=%08x\n",
        static_cast<int>(::getpid()), intMask.load(), textMask.load());
    std::fflush(stderr);
    return 1;
}
extern "C" IL2CPP_EXPORT void R03_IR_Exit(int32_t code) { std::_Exit(code); }

extern "C" IL2CPP_EXPORT int32_t R03_IR_ProbeBooleanReserve()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace il2cpp::vm::assembly_shadow_reporting;
    try
    {
        AssemblyShadowState before;
        if (AssemblyShadow::GetState(before) != AssemblyShadowError::Success ||
            before != AssemblyShadowState::Committed) return -1;
        auto& reserve = BooleanReserve();
        Il2CppObject* saved = reserve.object.load(std::memory_order_acquire);
        int32_t mask = saved && IsReadyBoolean(reserve.physicalClass) &&
            saved->klass == reserve.physicalClass ? 1 : 0;
        if (saved && reserve.pinnedHandle &&
            il2cpp::gc::GCHandle::GetTarget(reserve.pinnedHandle) == saved) mask |= 2;
        const int generation = il2cpp::gc::GarbageCollector::GetMaxGeneration();
        const int count = il2cpp::gc::GarbageCollector::GetCollectionCount(generation);
        il2cpp::gc::GarbageCollector::Collect(generation); // healthy, never after poison
        const int afterCount = il2cpp::gc::GarbageCollector::GetCollectionCount(generation);
        if (saved && reserve.object.load(std::memory_order_acquire) == saved && afterCount > count) mask |= 4;
        if (saved && HasTruePayload(saved)) mask |= 8;
        AssemblyShadowState after;
        if (AssemblyShadow::GetState(after) == AssemblyShadowError::Success && after == before) mask |= 16;
        std::fprintf(stderr, "[R03ReserveGcProbe] mask=%d collectionsBefore=%d collectionsAfter=%d\n", mask, count, afterCount);
        std::fflush(stderr);
        return mask;
    }
    catch (...) { return -2; }
#else
    return 0;
#endif
}
#endif // HYBRIDCLR_R03_RUNTIME_PROBE

// N: test-only native guard receipt and pre-bound primitive field observation.
// The production class/method execution guards are never modified here.
// A separate strong pinned root is created while healthy and retained until
// this disposable Player exits natively; no GCHandle work follows poison.
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include "il2cpp-class-internals.h"
#include "il2cpp-object-internals.h"
#include "vm/Class.h"
#include "vm/Field.h"
#include "gc/GCHandle.h"
#include <atomic>
#include <cstdint>
#include <cstring>
namespace r03_ir_observe {
struct BoundField
{
    std::atomic<int32_t> state{0};
    Il2CppObject* object = nullptr;
    Il2CppClass* owner = nullptr;
    FieldInfo* field = nullptr;
    uint32_t pinnedHandle = 0;
    uint32_t offset = 0;
};
static BoundField witness;

static bool UniqueValue(const char* json, const char* key, const char* value) noexcept
{
    if (!json || !key || !value) return false;
    const char* pos = std::strstr(json, key);
    if (!pos || std::strstr(pos + 1, key) != nullptr) return false;
    pos += std::strlen(key);
    const size_t n = std::strlen(value);
    return std::strncmp(pos, value, n) == 0 && (pos[n] == ',' || pos[n] == '}');
}
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_BindActiveField(void* managedObjectHandle)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_ir_observe;
    if (!managedObjectHandle || witness.state.load(std::memory_order_acquire) != 0) return -1;
    AssemblyShadowState current;
    if (AssemblyShadow::GetState(current) != AssemblyShadowError::Success ||
        current != AssemblyShadowState::Committed) return -2;
    const uintptr_t raw = reinterpret_cast<uintptr_t>(managedObjectHandle);
    if (!raw || raw > static_cast<uintptr_t>(UINT32_MAX)) return -3;
    Il2CppObject* object = il2cpp::gc::GCHandle::GetTarget(static_cast<uint32_t>(raw));
    if (!object || !object->klass) return -4;
    Il2CppClass* owner = object->klass;
    if (!owner->image || !owner->image->assembly ||
        !AssemblyShadow::IsActiveShadow(owner->image->assembly) ||
        !owner->namespaze || std::strcmp(owner->namespaze, "R03") ||
        !owner->name || std::strcmp(owner->name, "Node") ||
        !owner->image->assembly->aname.name ||
        std::strcmp(owner->image->assembly->aname.name, "Methods")) return -5;
    // Only this real active instance and its nonstatic primitive stable field
    // can be observed. Class::GetFieldFromName is invoked only when healthy.
    FieldInfo* field = Class::GetFieldFromName(owner, "stable");
    if (!field || field->parent != owner || !field->name ||
        std::strcmp(field->name, "stable") || !field->type ||
        field->type->type != IL2CPP_TYPE_I4 ||
        (field->type->attrs & FIELD_ATTRIBUTE_STATIC) ||
        field->offset < sizeof(Il2CppObject) ||
        static_cast<uint64_t>(field->offset) + sizeof(int32_t) > owner->instance_size)
        return -6;
    int32_t initial = 0;
    std::memcpy(&initial, reinterpret_cast<const uint8_t*>(object) + field->offset, sizeof initial);
    if (initial != 2) return -7;
    const uint32_t pinned = il2cpp::gc::GCHandle::New(object, true);
    if (!pinned) return -8;
    if (il2cpp::gc::GCHandle::GetTarget(pinned) != object)
    { il2cpp::gc::GCHandle::Free(pinned); return -9; }
    witness.object = object;
    witness.owner = owner;
    witness.field = field;
    witness.offset = field->offset;
    witness.pinnedHandle = pinned;
    witness.state.store(1, std::memory_order_release);
    return 1;
#else
    (void)managedObjectHandle; return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_ReadActiveField(int32_t* output)
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_ir_observe;
    if (!output || witness.state.load(std::memory_order_acquire) != 1) return -1;
    AssemblyShadowState current;
    if (AssemblyShadow::GetState(current) != AssemblyShadowError::Success ||
        current != AssemblyShadowState::FailedAfterCommit) return -2;
    Il2CppObject* object = witness.object;
    if (!object || object->klass != witness.owner || !witness.field ||
        witness.field->parent != witness.owner || witness.field->offset != witness.offset)
        return -3;
    // No managed virtual dispatch, class init, boxing, field writing,
    // allocation or GCHandle target lookup after terminal failure.
    int32_t observed = 0;
    std::memcpy(&observed, reinterpret_cast<const uint8_t*>(object) + witness.offset, sizeof observed);
    *output = observed;
    return 1;
#else
    (void)output; return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_IR_ObserveOldGuardIntoSnapshot()
{
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
    using namespace il2cpp::vm;
    using namespace r03_ir_observe;
    char buffer[16384] = {};
    const int32_t count = R03_ObserveMethod("Methods", "R03", "Node", "Keep", 3,
        buffer, static_cast<int32_t>(sizeof buffer));
    if (count <= 0 || count >= static_cast<int32_t>(sizeof buffer) || buffer[count] != '\0')
        return -1;
    AssemblyShadowState state;
    if (AssemblyShadow::GetState(state) != AssemblyShadowError::Success ||
        state != AssemblyShadowState::FailedAfterCommit ||
        !UniqueValue(buffer, "\"available\":", "true") ||
        !UniqueValue(buffer, "\"activeGuard\":", "1") ||
        !UniqueValue(buffer, "\"baselineGuard\":", "0") ||
        !UniqueValue(buffer, "\"caughtOldGuard\":", "1") ||
        !UniqueValue(buffer, "\"stateCode\":", "9"))
        return -2;
    // Preserve complete original native producer JSON directly into the
    // once-only preopened snapshot. Host independently parses exact fields.
    return R03_IR_ReportText(8, buffer) == 1 ? 1 : -3;
#else
    return 0;
#endif
}
#endif // HYBRIDCLR_R03_RUNTIME_PROBE
