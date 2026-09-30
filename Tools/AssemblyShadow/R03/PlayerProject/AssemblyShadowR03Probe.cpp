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
