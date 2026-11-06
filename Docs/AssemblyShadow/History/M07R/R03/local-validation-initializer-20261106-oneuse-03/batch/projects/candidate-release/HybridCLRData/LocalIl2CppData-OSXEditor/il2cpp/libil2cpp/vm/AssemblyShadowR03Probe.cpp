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
#include <limits.h>
#include "gc/GCHandle.h"
#include "gc/GarbageCollector.h"
namespace r03_ir_snapshot {
constexpr size_t TextLimit = 262144;
// Complete general diagnostic JSON is never clipped or admitted as an
// oversized field. A separate already-opened sidecar can hold <=3.75 MiB,
// while field 14 retains the unchanged 256 KiB transport limit.
constexpr size_t GeneralLimit = 3932160;
constexpr const char* GeneralSuffix = ".general.json";
constexpr const char* GeneralDescriptor = "R03FullGeneralSidecarV1:";
constexpr const char* IntNames[] = {"initialState","poisonedState","finalState","nativeStimulusReturn","preActiveReflection","preActiveDelegate","preCanaryCount","finalCanaryCount","preShadowField","finalShadowField","nativePhase","failurePhase","terminalReportingProbeMask","reserveGcProbeMask","shadowFieldReadable","prePositive","activeReflectionAttempted","activeReflectionSucceeded","activeDelegateAttempted","activeDelegateSucceeded","aotReflectionAttempted","aotReflectionSucceeded","recoveryStable","fixedDiagnosticsReadable","acceptance"};
constexpr const char* TextNames[] = {"result","runId","caseId","requestSha256","stimulus","unityVersion","platform","error","nativeGuardJson","activeReflectionException","activeDelegateException","aotReflectionException","firstRecovery","finalRecovery","finalDiagnostics","finalExecutionDiagnostics"};
constexpr int IntCount = 25;
constexpr int FirstBool = 14;
constexpr int TextCount = 16;
static std::atomic<int> state{0}; // 0 unused,1 open,2 sealed,3 sealing,-1 failed
static FILE* stream = nullptr;
static int generalFd = -1;
static char generalPath[PATH_MAX] = {};
static bool generalUsed = false;
static size_t generalBytes = 0;
static uint32_t generalCrc = 0;
static int32_t ints[IntCount] = {};
static bool haveInt[IntCount] = {}, haveText[TextCount] = {}, nullText[TextCount] = {};
static char texts[TextCount][TextLimit + 1] = {};
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
static uint32_t Checksum32(const char* text, size_t length) noexcept
{
    // CRC32 of the COMPLETE already-bounded native input, independently
    // checked by the host along with its SHA256 and parsed schema.
    uint32_t crc = 0xffffffffu;
    for (size_t i = 0; i < length; ++i)
    {
        crc ^= static_cast<unsigned char>(text[i]);
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}
static bool WriteCompleteGeneral(const char* input, size_t n) noexcept
{
    if (generalFd < 0 || generalUsed || !input || !n ||
        n > GeneralLimit || input[0] != '{' || input[n - 1] != '}')
        return false;
    // No managed callback, allocator, open or source-field modification after
    // the terminal state. Short OS writes are completed or fail closed.
    size_t offset = 0;
    while (offset < n)
    {
        const ssize_t step = ::write(generalFd, input + offset, n - offset);
        if (step < 0 && errno == EINTR) continue;
        if (step <= 0) return false;
        offset += static_cast<size_t>(step);
    }
    if (::fsync(generalFd) != 0 || ::close(generalFd) != 0)
    {
        generalFd = -1;
        return false;
    }
    generalFd = -1;
    generalCrc = Checksum32(input, n);
    generalBytes = n;
    generalUsed = true;
    return true;
}
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
    const size_t pathLen = ::strnlen(path, sizeof(generalPath));
    const size_t suffixLen = std::strlen(GeneralSuffix);
    if (pathLen == sizeof(generalPath) || pathLen + suffixLen + 1 > sizeof(generalPath))
        return Reject("general-path", -1, 17, pathLen);
    std::memcpy(generalPath, path, pathLen);
    std::memcpy(generalPath + pathLen, GeneralSuffix, suffixLen + 1);
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
    // All potential report destinations are preopened while healthy and are
    // exclusive. No path construction or file open is allowed after poison.
    errno = 0;
    generalFd = ::open(generalPath, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (generalFd < 0) return Reject("general-open", -1, 18, 0, errno);
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
    if (n > TextLimit && field == 14)
    {
        // 262145 in the previous E log was only a lower-bound sentinel.
        // Inspect the complete source up to the predeclared general budget;
        // reject all larger/invalid inputs, NEVER accept truncated bytes.
        n = ::strnlen(value, GeneralLimit + 1);
        if (n > GeneralLimit) return Reject("general-over-limit", field, 9, n);
        if (!WriteCompleteGeneral(value, n))
            return Reject("general-write", field, 19, n, errno);
        const int count = std::snprintf(texts[field], TextLimit + 1,
            "%s%zu:%08x", GeneralDescriptor, n, generalCrc);
        if (count <= 0 || static_cast<size_t>(count) > TextLimit)
            return Reject("general-descriptor", field, 20, n);
        std::fprintf(stderr, "[R03FullGeneralSidecar] version=1 pid=%d bytes=%zu crc32=%08x\n",
            static_cast<int>(::getpid()), generalBytes, generalCrc);
        std::fflush(stderr);
    }
    else
    {
        if (n > TextLimit) return Reject("text", field, 9, n);
        if (value) std::memcpy(texts[field], value, n + 1);
    }
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
    // The unused preopened sidecar is never kept as a phantom diagnostic
    // file. Failure to close/remove it invalidates the entire snapshot.
    if (!generalUsed)
    {
        if (generalFd < 0) return Reject("general-fd", -1, 21);
        errno = 0;
        if (::close(generalFd) != 0) return Reject("general-close", -1, 22, 0, errno);
        generalFd = -1;
        errno = 0;
        if (::unlink(generalPath) != 0) return Reject("general-unlink", -1, 23, 0, errno);
    }
    else if (generalFd != -1 || generalBytes <= TextLimit || generalBytes > GeneralLimit)
        return Reject("general-invalid", -1, 24, generalBytes);
    for (int i = 0; i < IntCount; ++i)
        if (!haveInt[i]) return Reject("missing-int", i, 11);
    for (int i = 0; i < TextCount; ++i)
        if (!haveText[i]) return Reject("missing-text", i, 12);
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
        Quote(stream, nullText[i] ? nullptr : texts[i]);
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

// Source-bound separate initializer part: R03InitializerPreparedProbe.cpp
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
#include <atomic>
#include <cstdint>
#include <cstring>

// Real writer is later in the composite overlay. The observer's standalone
// C++11 host driver supplies an explicitly labelled test-only trace stub.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d);

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
extern "C" IL2CPP_EXPORT int32_t R03_IRW_OnPrepared() { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(
    int32_t*,int32_t*,int32_t*,int32_t*,int32_t*) { return 0; }
#endif

// Source-bound separate initializer part: R03InitializerObservationWriter.cpp
// Test-only native initializer V1 writer and independent durable diagnostic journal.
// The diagnostic journal is NOT the strict V1 observation and never grants V2
// transport, R03 acceptance, recovery completeness or executable provenance.
// All post-Commit journal operations use preopened fds and native primitives.
#include "il2cpp-config.h"
#if HYBRIDCLR_R03_RUNTIME_PROBE
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

extern "C" IL2CPP_EXPORT int32_t R03_IRW_ReadPrepared(
    int32_t*, int32_t*, int32_t*, int32_t*, int32_t*);

namespace r03_irw_output {
static std::atomic<int32_t> state{0}; // 0 unused, 1 opened, 2 sealed, -1 invalid
static std::atomic<int32_t> nextSequence{0};
static std::atomic_flag journalBusy = ATOMIC_FLAG_INIT;
static std::atomic<bool> journalBroken{false};
static int fd = -1, journal = -1;
static char runId[96]{}, caseId[96]{}, stimulus[32]{}, digest[65]{};
static const int MAX_EVENTS = 128;

static bool Safe(const char* p, size_t cap, bool isDigest) noexcept {
    if (!p) return false;
    const size_t n = ::strnlen(p, cap);
    if (n == 0 || n == cap || (isDigest && n != 64)) return false;
    for (size_t i = 0; i < n; ++i) {
        const char c = p[i];
        const bool ascii = (c >= 'a' && c <= 'z') ||
                           (c >= 'A' && c <= 'Z') ||
                           (c >= '0' && c <= '9') ||
                           c == '-' || c == '_' || c == '.';
        const bool hex = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
        if (!(isDigest ? hex : ascii)) return false;
    }
    return true;
}

static bool WriteAll(int output, const char* data, size_t n) noexcept {
    unsigned retries = 0;
    while (n) {
        const ssize_t wrote = ::write(output, data, n);
        if (wrote < 0) {
            if (errno == EINTR && ++retries <= 8) continue;
            return false;
        }
        if (wrote == 0 || static_cast<size_t>(wrote) > n) return false;
        data += wrote; n -= static_cast<size_t>(wrote); retries = 0;
    }
    return true;
}

static bool ValidFd(int value) noexcept {
    struct stat info{};
    return value >= 0 && ::fstat(value, &info) == 0 && S_ISREG(info.st_mode) &&
           (info.st_mode & 0777) == 0600 && info.st_nlink == 1;
}

static int32_t Event(int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d) noexcept {
    if (journal < 0 || journalBroken.load(std::memory_order_acquire)) return -1;
    if (journalBusy.test_and_set(std::memory_order_acquire)) {
        journalBroken.store(true, std::memory_order_release);
        return -2;
    }
    const int32_t sequence = nextSequence.fetch_add(1, std::memory_order_relaxed) + 1;
    char line[512];
    const int size = std::snprintf(line, sizeof line,
        "{\"kind\":\"R03IRInitializerNativeTraceV1\","
        "\"runId\":\"%s\",\"caseId\":\"%s\",\"stimulus\":\"%s\","
        "\"fixtureSha256\":\"%s\",\"pid\":%ld,\"seq\":%d,"
        "\"phase\":%d,\"a\":%d,\"b\":%d,\"c\":%d,\"d\":%d,"
        "\"runtimeAcceptance\":false,\"R03Accepted\":false,\"H2Passed\":false}\n",
        runId, caseId, stimulus, digest, static_cast<long>(::getpid()),
        sequence, phase, a, b, c, d);
    const bool valid = sequence <= MAX_EVENTS && size > 0 &&
        static_cast<size_t>(size) < sizeof line &&
        WriteAll(journal, line, static_cast<size_t>(size)) && ::fsync(journal) == 0;
    if (!valid) journalBroken.store(true, std::memory_order_release);
    journalBusy.clear(std::memory_order_release);
    return valid ? 1 : -3;
}

static void CloseOutputs() noexcept {
    if (fd >= 0) { ::close(fd); fd = -1; }
    if (journal >= 0) { ::fsync(journal); ::close(journal); journal = -1; }
}
} // namespace r03_irw_output

// 100-299 managed phase transitions; 300-399 actual prepublication native
// callback decisions; 400-499 actual postpublication primitive read;
// 600-699 native seal inputs/reasons; 900-999 managed catch/finally context.
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t phase, int32_t a, int32_t b, int32_t c, int32_t d) {
    return r03_irw_output::Event(phase, a, b, c, d);
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(
    const char* path, const char* run, const char* caseName,
    const char* mode, const char* sha) {
    using namespace r03_irw_output;
    int32_t expected = 0;
    if (!state.compare_exchange_strong(expected, 1)) return -1;
    static const char suffix[] = ".native-trace.jsonl";
    const size_t pathLen = path ? ::strnlen(path, 4096) : 0;
    if (!path || pathLen < 2 || path[0] != '/' ||
        pathLen + sizeof suffix > 4096 ||
        !Safe(run, sizeof(runId), false) || ::strlen(run) < 24 ||
        !Safe(caseName, sizeof(caseId), false) ||
        !Safe(mode, sizeof(stimulus), false) ||
        !(::strcmp(mode, "initializer-control") == 0 ||
          ::strcmp(mode, "initializer-failure") == 0) ||
        !Safe(sha, sizeof(digest), true)) {
        state.store(-1); return -2;
    }
    // These are fixed validated ASCII strings: never escape arbitrary
    // user-controlled text into JSON or format a managed exception.
    ::strcpy(runId, run); ::strcpy(caseId, caseName);
    ::strcpy(stimulus, mode); ::strcpy(digest, sha);
    char tracePath[4096];
    std::memcpy(tracePath, path, pathLen);
    std::memcpy(tracePath + pathLen, suffix, sizeof suffix);
    journal = ::open(tracePath, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (!ValidFd(journal)) {
        CloseOutputs(); state.store(-1); return -3;
    }
    if (Event(100, 1, 0, 0, 0) != 1) {
        CloseOutputs(); state.store(-1); return -4;
    }
    fd = ::open(path, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
    if (!ValidFd(fd)) {
        Event(101, -5, errno, 0, 0);
        CloseOutputs(); state.store(-1); return -5;
    }
    if (Event(101, 1, 0, 0, 0) != 1) {
        CloseOutputs(); state.store(-1); return -6;
    }
    return 1;
}

extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(
    int32_t commit, int32_t finalState, int32_t canaryBefore,
    int32_t canaryAfter, int32_t attempted, int32_t succeeded) {
    using namespace r03_irw_output;
    const int32_t started = Event(600, commit, finalState, attempted, succeeded);
    Event(601, canaryBefore, canaryAfter, 0, 0);
    int32_t expected = 1;
    if (!state.compare_exchange_strong(expected, -1) || fd < 0) {
        Event(610, -1, expected, fd, 0);
        CloseOutputs(); return -1;
    }
    int32_t field = -1, preField = -1, ready = -1, mask = -1, calls = -1;
    const int32_t observed = R03_IRW_ReadPrepared(&field, &preField, &ready, &mask, &calls);
    Event(602, observed, field, preField, ready);
    Event(603, mask, calls, 0, 0);
    const bool control = ::strcmp(stimulus, "initializer-control") == 0;
    int32_t reason = 0;
    if (observed != 1) reason = 1;
    else if (field != 3 || preField != 3 || ready != 1) reason = 2;
    else if (mask != 15 || calls != 1) reason = 3;
    else if (canaryBefore != 1 || canaryAfter != 1 || succeeded != 0) reason = 4;
    else if (control ? (commit != 0 || finalState != 6 || attempted != 0)
                     : (commit != 19 || finalState != 9 || attempted != 1)) reason = 5;
    if (started != 1 || journalBroken.load(std::memory_order_acquire)) reason = 6;
    if (reason) {
        Event(610, -2, reason, observed, 0);
        CloseOutputs(); return -2;
    }
    char raw[2048];
    const int len = std::snprintf(raw, sizeof raw,
        "{\"schemaVersion\":1,\"kind\":\"R03IRInitializerCommitObservationV1\","
        "\"reportTransport\":\"NativePreopenedInitializerObservationV1\","
        "\"result\":\"ObservedNotAccepted\",\"runId\":\"%s\","
        "\"caseId\":\"%s\",\"stimulus\":\"%s\","
        "\"fixtureSha256\":\"%s\",\"processId\":%ld,"
        "\"commitReturn\":%d,\"finalState\":%d,"
        "\"nativeObserverBoundBeforeFailure\":true,\"preparedField\":%d,"
        "\"finalField\":%d,\"positiveMask\":%d,\"initializerCallbackCalls\":%d,"
        "\"postAotAttempted\":%s,\"postAotSucceeded\":false,"
        "\"firstRecoveryAuthenticated\":false,\"completeDiagnosticsAuthenticated\":false,"
        "\"nativeV2TransportImplemented\":false,\"runtimeAcceptance\":false,"
        "\"R03Accepted\":false,\"H2Passed\":false}\n",
        runId, caseId, stimulus, digest, static_cast<long>(::getpid()),
        commit, finalState, preField, field, mask, calls,
        attempted ? "true" : "false");
    if (len <= 0 || static_cast<size_t>(len) >= sizeof raw ||
        !WriteAll(fd, raw, static_cast<size_t>(len)) ||
        ::fsync(fd) != 0 || ::close(fd) != 0) {
        fd = -1;
        Event(610, -3, len, errno, 0);
        CloseOutputs(); return -3;
    }
    fd = -1;
    if (Event(620, 1, commit, finalState, observed) != 1) {
        CloseOutputs(); return -4;
    }
    if (::close(journal) != 0) {
        journal = -1; return -5;
    }
    journal = -1;
    state.store(2, std::memory_order_release);
    return 1;
}
#else
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Open(
    const char*, const char*, const char*, const char*, const char*) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Trace(
    int32_t, int32_t, int32_t, int32_t, int32_t) { return 0; }
extern "C" IL2CPP_EXPORT int32_t R03_IRW_Seal(
    int32_t,int32_t,int32_t,int32_t,int32_t,int32_t) { return 0; }
#endif
