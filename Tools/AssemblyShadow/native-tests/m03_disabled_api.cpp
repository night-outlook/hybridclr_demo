// Link the actual OFF adapter, native core, and diagnostic serializer. Only
// managed string allocation is substituted; no JSON or native API is mocked.
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include "hybridclr/AssemblyShadowRuntimeApi.h"
#include "vm/AssemblyShadow.h"
#include "vm/String.h"

#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#error This executable verifies the feature-disabled runtime boundary.
#endif

namespace {
size_t s_checks = 0;
size_t s_stringCalls = 0;
int s_throwMode = 0;
Il2CppString s_string = {};
Il2CppString** s_observedOutput = nullptr;
std::string s_receivedJson;

void Check(bool condition, const char* detail)
{
    if (!condition) throw std::runtime_error(detail);
    ++s_checks;
}
}

namespace il2cpp { namespace vm {
Il2CppString* String::New(const char* value)
{
    ++s_stringCalls;
    Check(s_observedOutput && !*s_observedOutput, "Diagnostic output was not initialized before allocation");
    if (s_throwMode == 1) throw std::runtime_error("Injected managed-string allocation failure");
    if (s_throwMode == 2) throw 42;
    s_receivedJson = value;
    return &s_string;
}
}}

int main()
{
    try
    {
        using hybridclr::AssemblyShadowRuntimeApi;
        using il2cpp::vm::AssemblyShadow;
        using il2cpp::vm::AssemblyShadowError;
        const int32_t disabled = static_cast<int32_t>(AssemblyShadowError::FeatureDisabled);
        const int32_t internalError = static_cast<int32_t>(AssemblyShadowError::InternalError);
        // Poison inputs make any accidental argument access fail under ASan.
        Il2CppString* invalidString = reinterpret_cast<Il2CppString*>(static_cast<uintptr_t>(1));
        Il2CppArray* invalidArray = reinterpret_cast<Il2CppArray*>(static_cast<uintptr_t>(1));
        Check(AssemblyShadowRuntimeApi::ConfigureCandidates(invalidString, invalidArray, invalidArray) == disabled,
            "OFF ConfigureCandidates did not precede argument validation");
        Check(AssemblyShadowRuntimeApi::BeginTransaction(invalidString, invalidString, invalidArray, -1) == disabled,
            "OFF BeginTransaction did not precede argument validation");
        Check(AssemblyShadowRuntimeApi::StageAssembly(invalidArray, invalidArray) == disabled,
            "OFF StageAssembly did not precede argument validation");
        Check(AssemblyShadowRuntimeApi::ValidateTransaction() == disabled, "OFF ValidateTransaction result changed");
        Check(AssemblyShadowRuntimeApi::CommitTransaction() == disabled, "OFF CommitTransaction result changed");
        Check(AssemblyShadowRuntimeApi::AbortTransaction() == disabled, "OFF AbortTransaction result changed");
        int32_t state = -1;
        Check(AssemblyShadowRuntimeApi::GetState(&state) == disabled &&
            state == static_cast<int32_t>(il2cpp::vm::AssemblyShadowState::Disabled), "OFF state output changed");
        Check(AssemblyShadowRuntimeApi::GetState(nullptr) == disabled, "OFF null state output was validated");
        int32_t mode = -1;
        Check(AssemblyShadowRuntimeApi::GetAssemblyExecutionMode(invalidString, &mode) == disabled &&
            mode == static_cast<int32_t>(il2cpp::vm::AssemblyExecutionMode::AotBaseline), "OFF mode output changed");
        Check(AssemblyShadowRuntimeApi::GetAssemblyExecutionMode(invalidString, nullptr) == disabled,
            "OFF null execution-mode output was validated");
        Check(AssemblyShadowRuntimeApi::GetDiagnosticsJson(nullptr) == disabled, "OFF null diagnostics output was validated");
        Check(s_stringCalls == 0, "Null diagnostics output attempted managed allocation");

        std::string nativeJson;
        Check(AssemblyShadow::GetDiagnosticsJson(nativeJson) == AssemblyShadowError::FeatureDisabled,
            "OFF native diagnostic result changed");
        Il2CppString* output = invalidString;
        s_observedOutput = &output;
        Check(AssemblyShadowRuntimeApi::GetDiagnosticsJson(&output) == disabled, "OFF diagnostic adapter result changed");
        Check(output == &s_string && s_stringCalls == 1, "OFF diagnostics were not returned exactly once");
        Check(s_receivedJson == nativeJson, "Adapter changed or truncated the native diagnostic JSON");
        Check(s_receivedJson.find("\"schemaVersion\":1") != std::string::npos &&
            s_receivedJson.find("\"state\":\"Disabled\"") != std::string::npos,
            "Native OFF diagnostics are not a full schema-1 snapshot");
        // Check both exception handlers and safe output on allocation failure.
        for (int throwMode = 1; throwMode <= 2; ++throwMode)
        {
            s_throwMode = throwMode;
            output = invalidString;
            Check(AssemblyShadowRuntimeApi::GetDiagnosticsJson(&output) == internalError,
                "Diagnostic allocation exception escaped or returned the wrong error");
            Check(!output, "Failed diagnostic allocation exposed an uninitialized output");
        }
        s_throwMode = 0;
        output = invalidString;
        Check(AssemblyShadowRuntimeApi::GetDiagnosticsJson(&output) == disabled && output == &s_string,
            "Diagnostics did not recover after allocation exceptions");
        Check(s_receivedJson == nativeJson, "Diagnostic exception changed the native disabled snapshot");
        std::cout << "native_disabled_api_json=" << s_receivedJson << '\n';
        std::cout << "native_disabled_api_checks=" << s_checks << " PASS\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
