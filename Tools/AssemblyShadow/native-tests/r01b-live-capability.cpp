// Actual RuntimeApi -> RuntimeConfig getters/setters and diagnostic serializer.
// The standalone exception adapter supplies only the absent managed exception VM.
#include "hybridclr/RuntimeApi.h"
#include "hybridclr/RuntimeConfig.h"
#include "vm/Exception.h"
#include "vm/AssemblyShadowDiagnostics.h"
#include <cstdio>
#include <fstream>
#include <stdexcept>
#include <string>

namespace {
size_t checks = 0;
std::string exceptionParameter, exceptionMessage;
void Check(bool value, const char* message)
{
    ++checks;
    if (!value) throw std::runtime_error(message);
}
int Read(hybridclr::RuntimeOptionId id)
{
    return hybridclr::RuntimeApi::GetRuntimeOption(static_cast<int32_t>(id));
}
}
namespace il2cpp { namespace vm {
Il2CppException* Exception::GetArgumentException(const char* parameter, const char* message)
{
    exceptionParameter = parameter ? parameter : "";
    exceptionMessage = message ? message : "";
    return reinterpret_cast<Il2CppException*>(1);
}
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::invalid_argument(exceptionMessage); }
}}

int main(int argc, char** argv)
{
    using hybridclr::RuntimeOptionId;
    using il2cpp::vm::AssemblyShadowDiagnostics;
    try
    {
        Check(argc == 2, "diagnostic output path required");
        const int metadata = HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW ?
            il2cpp::vm::kAssemblyShadowMetadataBudgetCapabilityVersion : 0;
        const int recovery = HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW ?
            il2cpp::vm::kAssemblyShadowRecoveryCapabilityVersion : 0;
        // Queries use the actual pre-existing icall adapter, never a snapshot
        // or substituted capacity implementation. Growing observations cannot
        // enter this constant-size production call chain.
        il2cpp::vm::ShadowDiagnosticSnapshot snapshot;
        snapshot.enabled = HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW;
        for (size_t count = 0; count <= 8192; ++count)
        {
            Check(Read(RuntimeOptionId::AssemblyShadowMetadataBudgetCapabilityVersion) == metadata,
                "metadata capability changed with image count");
            Check(Read(RuntimeOptionId::AssemblyShadowRecoveryCapabilityVersion) == recovery,
                "recovery capability changed with image count");
            if (count < 8191)
            {
                il2cpp::vm::ShadowDiagnosticSnapshot::OrdinaryAssembly assembly;
                assembly.name = "Workload." + std::to_string(count);
                assembly.isInterpreter = true;
                snapshot.ordinaryAssemblies.push_back(assembly);
            }
        }
        for (size_t count = 0; count < 10000; ++count)
        {
            il2cpp::vm::ShadowDiagnosticSnapshot::OrdinaryClass klass;
            klass.assemblyName = "Workload." + std::to_string(count % 8191);
            klass.typeName = "Workload.InitializedType";
            klass.isInterpreter = true;
            klass.isConstructedGeneric = false;
            klass.usesStagedMetadata = false;
            snapshot.ordinaryClasses.push_back(klass);
        }
        std::string diagnostic = AssemblyShadowDiagnostics::Serialize(snapshot);
        Check(diagnostic.size() < 4 * 1024 * 1024, "node-bound fixture unexpectedly hit byte bound");
        Check(diagnostic.find("\"metadataBudgetCapabilityVersion\":" + std::to_string(metadata)) != std::string::npos,
            "diagnostics and compact metadata capability disagree");
        Check(diagnostic.find("\"recoveryCapabilityVersion\":" + std::to_string(recovery)) != std::string::npos,
            "diagnostics and compact recovery capability disagree");
        for (RuntimeOptionId option : {RuntimeOptionId::AssemblyShadowMetadataBudgetCapabilityVersion,
            RuntimeOptionId::AssemblyShadowRecoveryCapabilityVersion})
        {
            const int before = Read(option);
            bool rejected = false;
            try { hybridclr::RuntimeApi::SetRuntimeOption(static_cast<int32_t>(option), 99); }
            catch (const std::invalid_argument&)
            {
                rejected = exceptionParameter == std::to_string(static_cast<int32_t>(option)) &&
                    exceptionMessage == "read-only runtime option id";
            }
            Check(rejected, "capability setter did not reject read-only ID");
            Check(Read(option) == before, "capability setter changed live truth");
        }
        bool unknown = false;
        try { hybridclr::RuntimeApi::GetRuntimeOption(999); }
        catch (const std::invalid_argument&)
        {
            unknown = exceptionParameter == "999" && exceptionMessage == "invalid runtime option id";
        }
        Check(unknown, "legacy unknown-option discriminator changed");
        std::ofstream output(argv[1]);
        output << diagnostic;
        Check(output.good(), "diagnostic fixture write failed");
        std::printf("r01b_live_capability_checks=%zu feature=%d diagnostic_bytes=%zu PASS\n",
            checks, HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW, diagnostic.size());
        return 0;
    }
    catch (const std::exception& error) { std::fprintf(stderr, "%s\n", error.what()); return 1; }
}
