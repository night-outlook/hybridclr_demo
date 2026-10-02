// Test-only additive source installed into an isolated validation Player.
// Its exact committed bytes are recorded separately from the native install
// receipt. It is never installed into the production or historical Player.
#include "il2cpp-config.h"
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowTypeResolver.h"
#include "vm/AssemblyShadowDiagnostics.h"
#include "vm/MetadataCache.h"
#include "vm/MetadataLock.h"
#include <cstring>
#include <sstream>

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
            << ",\"activeGeneration\":" << AssemblyShadow::ActiveGeneration() << "}";
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

extern "C" IL2CPP_EXPORT int32_t R03_BeginWarmProbe(const char* assemblyName)
{
#if R03_HAS_RUNTIME_PROBE
    using namespace il2cpp::vm;
    if (!assemblyName || !AssemblyShadow::ActiveGeneration()) return 0;
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
    (void)assemblyName; return 0;
#endif
}

extern "C" IL2CPP_EXPORT int32_t R03_MarkWarmProbe(int32_t boundary)
{
#if R03_HAS_RUNTIME_PROBE
    return il2cpp::vm::assembly_shadow_r03::RuntimeProbe::Mark(boundary) ? 1 : -1;
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
    using il2cpp::vm::AssemblyShadowDiagnostics;
    out << "{\"physical\":" << AssemblyShadowDiagnostics::Quote(ProbePointer(pointer))
        << ",\"assembly\":" << AssemblyShadowDiagnostics::Quote(klass && klass->image && klass->image->assembly ? klass->image->assembly->aname.name : "")
        << ",\"namespace\":" << AssemblyShadowDiagnostics::Quote(klass ? klass->namespaze : "")
        << ",\"name\":" << AssemblyShadowDiagnostics::Quote(klass ? klass->name : "") << "}";
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
    const auto r = assembly_shadow_r03::RuntimeProbe::Read();
    std::ostringstream out; out << std::boolalpha;
    out << "{\"schemaVersion\":1,\"available\":true,\"policy\":\"R03ExactAllocationWindowV1\",\"used\":" << r.used
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
        ProbeType(out, e.key.physical); out << "}";
    }
    out << "],\"layouts\":[";
    for (size_t i = 0; i < r.layouts; ++i)
    {
        if (i) out << ","; const auto& l = r.layout[i];
        out << "{\"baseline\":"; ProbeType(out, l.baseline); out << ",\"target\":"; ProbeType(out, l.target);
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
    out << "],\"runtimeAcceptance\":false}"; json = out.str();
    }
    catch (...) { return -3; }
#else
    json = "{\"schemaVersion\":1,\"available\":false,\"runtimeAcceptance\":false}";
#endif
    if (json.size() + 1 > static_cast<size_t>(capacity)) return -2;
    std::memcpy(output, json.c_str(), json.size() + 1); return static_cast<int32_t>(json.size());
}
