#include "../Il2CppCompatibleDef.h"
#include <cstdint>

namespace hybridclr
{
	const char* g_placeHolderAssemblies[] =
	{
		//!!!{{PLACE_HOLDER
		"AssemblyShadowBaseline.HotUpdate",

		//!!!}}PLACE_HOLDER
		nullptr,
	};

	extern const uint32_t g_assemblyShadowStartupCandidateSchemaVersion = 1;
	const char* g_assemblyShadowStartupCandidates[] =
	{
		//!!!{{ASSEMBLY_SHADOW_STARTUP_CANDIDATES
		"AssemblyA.Contracts",
		"AssemblyA.Implementation.Extensibility",
		"AssemblyA.Implementation.Internal",
		"AssemblyShadowDemo.ContractsConsumer",
		"AssemblyShadowDemo.ExtensibilityConsumer",

		//!!!}}ASSEMBLY_SHADOW_STARTUP_CANDIDATES
		nullptr,
	};

	extern const uint32_t g_assemblyShadowStartupBootstrapSchemaVersion = 1;
	//!!!{{ASSEMBLY_SHADOW_STARTUP_BOOTSTRAP
	const char* g_assemblyShadowStartupBootstrapAssembly = "AssemblyShadowDemo.Bootstrap";
	const char* g_assemblyShadowStartupBootstrapNamespace = "AssemblyShadowDemo";
	const char* g_assemblyShadowStartupBootstrapType = "R01EarlyStartup";
	const char* g_assemblyShadowStartupBootstrapMethod = "Run";

	//!!!}}ASSEMBLY_SHADOW_STARTUP_BOOTSTRAP
}
