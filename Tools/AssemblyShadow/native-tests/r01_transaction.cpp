// R01 transaction boundary checks.  This executable includes the production
// staging parser and AssemblyShadow state machine; the small physical lookup
// and exception adapters below only supply the startup VM boundary.
#include "vm/Assembly.h"

// Image's inline constructor normally snapshots the global Assembly list.
// Keep this native fixture independent of that process-global registry while
// still compiling the real Image/InterpreterImage implementation.
namespace il2cpp { namespace vm {
struct R01ImageAdapter
{
    static void GetAllAssemblies(AssemblyVector& assemblies) { assemblies.clear(); }
    static AssemblyVector* GetAllAssemblies()
    {
        static AssemblyVector empty;
        return &empty;
    }
};
}}
#define Assembly R01ImageAdapter
#include "hybridclr/metadata/Image.h"
#undef Assembly

#include "hybridclr/metadata/StagedAssembly.cpp"

#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "utils/Memory.h"

// AssemblyShadow.cpp is included after the production staging implementation,
// but its VM-facing aliases are redirected to these explicit test adapters.
// This keeps the identity parser real while making synthetic ownership, metadata and
// initializer outcomes visible in the native receipt.
namespace hybridclr { namespace metadata {
enum class R01BackendMode { Production, MetadataFailure, InitializerFailure, PartialOwner };
static R01BackendMode r01BackendMode = R01BackendMode::Production;
struct R01Adapter
{
    static il2cpp::vm::AssemblyShadowError ReadStagedAssemblyIdentity(const byte* dll, size_t length, std::string& name, std::string& detail)
    { return Assembly::ReadStagedAssemblyIdentity(dll, length, name, detail); }
    static il2cpp::vm::AssemblyShadowError CreateStagedSkeleton(const byte* dll, size_t dllLength, const byte* pdb, size_t pdbLength,
        StagedAssembly*& staged, std::string& detail, uint32_t reservedImageIndex = 0)
    {
        (void)pdb;
        (void)pdbLength;
        (void)reservedImageIndex;
        staged = nullptr;
        std::string name;
        il2cpp::vm::AssemblyShadowError parsed = Assembly::ReadStagedAssemblyIdentity(dll, dllLength, name, detail);
        if (parsed != il2cpp::vm::AssemblyShadowError::Success) return parsed;
        // Synthetic ownership is deliberate: it lets the public transaction
        // retain and report an owner without entering Unity's GC/metadata
        // registries. No real runtime metadata is initialized here.
        staged = new StagedAssembly();
        staged->canonicalName = name;
        staged->mvid = "r01-synthetic-mvid";
        staged->dllBytes = dll;
        staged->dllSize = dllLength;
        staged->assembly = new Il2CppAssembly();
        staged->image = new Il2CppImage();
        staged->assembly->aname.name = staged->canonicalName.c_str();
        staged->assembly->aname.culture = "";
        staged->assembly->image = staged->image;
        staged->assembly->token = 1;
        staged->image->assembly = staged->assembly;
        staged->image->name = staged->canonicalName.c_str();
        staged->image->nameNoExt = staged->canonicalName.c_str();
        staged->image->token = (UINT32_C(1) << 31) | 1;
        staged->skeletonBuilt = true;
        if (r01BackendMode == R01BackendMode::PartialOwner)
        {
            detail = "R01 injected skeleton failure after synthetic owner creation.";
            return il2cpp::vm::AssemblyShadowError::BadImage;
        }
        detail = "R01 synthetic skeleton owner created.";
        return il2cpp::vm::AssemblyShadowError::Success;
    }
    static il2cpp::vm::AssemblyShadowError InitializeStagedRuntimeMetadata(StagedAssembly* staged, std::string& detail)
    {
        if (r01BackendMode == R01BackendMode::MetadataFailure)
        {
            detail = "R01 injected StagedAssembly backend rejected runtime metadata.";
            return il2cpp::vm::AssemblyShadowError::ReferenceResolutionFailed;
        }
        if (!staged || !staged->skeletonBuilt) return il2cpp::vm::AssemblyShadowError::InvalidState;
        staged->runtimeMetadataInitialized = true;
        detail.clear();
        return il2cpp::vm::AssemblyShadowError::Success;
    }
    static void PublishStagedImage(StagedAssembly* staged)
    {
        // Explicit fixture publication: CommitTransaction still owns the
        // production snapshot/callback ordering, while no Unity image table
        // or GC registry is touched by this standalone test.
        if (staged) staged->published = true;
    }
    static il2cpp::vm::AssemblyShadowError RunStagedModuleInitializer(StagedAssembly* staged, std::string& detail)
    {
        if (r01BackendMode == R01BackendMode::InitializerFailure)
        {
            detail = "R01 injected StagedAssembly initializer failure.";
            return il2cpp::vm::AssemblyShadowError::ModuleInitializerFailed;
        }
        return Assembly::RunStagedModuleInitializer(staged, detail);
    }
};
}}

namespace il2cpp { namespace vm {
struct R01Adapter
{
    static void GetAllPhysicalAssemblies(AssemblyVector& assemblies) { assemblies.clear(); }
    static uint64_t CaptureShadowEnumeration(AssemblyVector& assemblies) { assemblies.clear(); return 0; }
    static bool PublishShadowBatch(const AssemblyVector&, bool (*tryBegin)(void*), void (*publish)(void*), void* context)
    {
        if (!tryBegin(context)) return false;
        publish(context);
        return true;
    }
};
}}

#define Assembly R01Adapter
#include "vm/AssemblyShadow.cpp"
#undef Assembly

namespace il2cpp { namespace utils {
void* Memory::Malloc(size_t size) { return std::malloc(size ? size : 1); }
void Memory::Free(void* pointer) { std::free(pointer); }
void* Memory::Calloc(size_t count, size_t size) { return std::calloc(count, size); }
void* Memory::Realloc(void* pointer, size_t size) { return std::realloc(pointer, size ? size : 1); }
}}

namespace {
using il2cpp::vm::AssemblyShadowError;
using il2cpp::vm::AssemblyShadowState;
using il2cpp::vm::kAssemblyShadowRuntimeAbiVersion;
using hybridclr::byte;

size_t checks = 0;
std::vector<const Il2CppAssembly*> physicalAssemblies;
std::unordered_map<const Il2CppAssembly*, il2cpp::vm::AssemblyVector> references;
std::string exceptionMessage;

void Check(bool condition, const char* detail)
{
    ++checks;
    if (!condition) throw std::runtime_error(detail);
}

struct Fixture
{
    Il2CppAssembly assembly = {};
    Il2CppImage image = {};

    explicit Fixture(const char* name)
    {
        assembly.aname.name = name;
        assembly.aname.culture = "";
        assembly.image = &image;
        assembly.token = 1;
        image.assembly = &assembly;
        image.name = name;
        image.nameNoExt = name;
        physicalAssemblies.push_back(&assembly);
    }
};

using Bytes = std::vector<byte>;

Bytes ReadBytes(const char* path)
{
    std::ifstream stream(path, std::ios::binary);
    Check(stream.good(), "DLL fixture cannot be opened");
    Bytes bytes((std::istreambuf_iterator<char>(stream)), {});
    Check(bytes.size() >= 64, "DLL fixture is empty or truncated");
    return bytes;
}

bool Has(const std::string& json, const char* text)
{
    return json.find(text) != std::string::npos;
}

bool Has(const std::string& json, const std::string& text)
{
    return json.find(text) != std::string::npos;
}

void CheckRecovery(AssemblyShadowState state, const char* disposition,
    int terminalError, bool published, bool retained)
{
    AssemblyShadowState actual = AssemblyShadowState::Disabled;
    Check(il2cpp::vm::AssemblyShadow::GetState(actual) == AssemblyShadowError::Success,
        "GetState failed");
    Check(actual == state, "state-machine state differs");
    std::string recovery;
    Check(il2cpp::vm::AssemblyShadow::GetRecoveryInfoJson(recovery) == AssemblyShadowError::Success,
        "recovery JSON failed");
    Check(Has(recovery, std::string("\"disposition\":\"") + disposition + "\""),
        "recovery disposition differs");
    Check(Has(recovery, std::string("\"terminalFailureCode\":") + std::to_string(terminalError)),
        "recovery terminal error differs");
    Check(Has(recovery, std::string("\"published\":") + (published ? "true" : "false")),
        "recovery publication state differs");
    if (retained) Check(Has(recovery, "\"retainedBytes\":") && !Has(recovery, "\"retainedBytes\":0"),
        "failed transaction did not retain its private owner");
    else Check(Has(recovery, "\"retainedBytes\":0"), "unexpected retained owner");
    std::cout << "r01_recovery_json=" << recovery << "\n";
}

void ConfigureAndBegin(const std::string& name)
{
    Check(il2cpp::vm::AssemblyShadow::ConfigureCandidates("r01-fixture", {name}, {"mscorlib"}) ==
        AssemblyShadowError::Success, "ConfigureCandidates failed");
    Check(il2cpp::vm::AssemblyShadow::BeginTransaction("r01-patch", "r01-fixture", {name},
        kAssemblyShadowRuntimeAbiVersion) == AssemblyShadowError::Success, "BeginTransaction failed");
}

void CheckPreOwner(const std::string& name)
{
    ConfigureAndBegin(name);
    const byte invalid[] = {0, 1, 2, 3};
    Check(il2cpp::vm::AssemblyShadow::StageAssembly(invalid, sizeof(invalid), nullptr, 0) ==
        AssemblyShadowError::BadImage, "invalid identity was accepted");
    AssemblyShadowState state = AssemblyShadowState::Disabled;
    Check(il2cpp::vm::AssemblyShadow::GetState(state) == AssemblyShadowError::Success &&
        state == AssemblyShadowState::Staging, "pre-owner rejection changed state");
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::Success,
        "pre-owner transaction did not abort");
    CheckRecovery(AssemblyShadowState::Aborted, "BaselineEligibleAfterAbort", 0, false, false);
    std::cout << "r01_preowner=pass injectedBackendOutcome=none publication=none\n";
}

void CheckValidateMetadataFailure(const Bytes& bytes, const std::string& name)
{
    hybridclr::metadata::r01BackendMode = hybridclr::metadata::R01BackendMode::MetadataFailure;
    ConfigureAndBegin(name);
    Check(il2cpp::vm::AssemblyShadow::StageAssembly(bytes.data(), bytes.size(), nullptr, 0) ==
        AssemblyShadowError::Success, "synthetic skeleton was rejected");
    Check(il2cpp::vm::AssemblyShadow::ValidateTransaction() == AssemblyShadowError::ReferenceResolutionFailed,
        "injected metadata failure was not returned through ValidateTransaction");
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::InvalidState,
        "failed metadata transaction unexpectedly allowed Abort");
    CheckRecovery(AssemblyShadowState::Failed, "RestartRequired", 13, false, true);
    std::cout << "r01_validate_failure=pass injectedBackendOutcome=ReferenceResolutionFailed syntheticOwner=1 publication=none\n";
}

void CheckBaselineUse(const Bytes& bytes, const std::string& name, Fixture& baseline)
{
    ConfigureAndBegin(name);
    Check(il2cpp::vm::AssemblyShadow::StageAssembly(bytes.data(), bytes.size(), nullptr, 0) ==
        AssemblyShadowError::Success, "synthetic skeleton was rejected");
    il2cpp::vm::AssemblyShadow::RecordBaselineUse(&baseline.assembly,
        il2cpp::vm::BaselineUseKind::AssemblyReflection, "R01.before-validate");
    std::string diagnostics;
    Check(il2cpp::vm::AssemblyShadow::GetDiagnosticsJson(diagnostics) == AssemblyShadowError::Success &&
        Has(diagnostics, "R01.before-validate"), "baseline use was not retained");
    Check(il2cpp::vm::AssemblyShadow::ValidateTransaction() == AssemblyShadowError::BaselineAlreadyUsed,
        "baseline use was not rejected before injected metadata initialization");
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::Success,
        "baseline-use transaction did not abort");
    CheckRecovery(AssemblyShadowState::Aborted, "BaselineEligibleAfterAbort", 0, false, true);
    std::cout << "r01_baseline_use=pass observation=retained-before-owner-validation syntheticOwner=1 publication=none\n";
}

void CheckPartialOwner(const Bytes& bytes, const std::string& name)
{
    hybridclr::metadata::r01BackendMode = hybridclr::metadata::R01BackendMode::PartialOwner;
    ConfigureAndBegin(name);
    Check(il2cpp::vm::AssemblyShadow::StageAssembly(bytes.data(), bytes.size(), nullptr, 0) ==
        AssemblyShadowError::BadImage, "injected skeleton failure was accepted");
    AssemblyShadowState state = AssemblyShadowState::Disabled;
    Check(il2cpp::vm::AssemblyShadow::GetState(state) == AssemblyShadowError::Success &&
        state == AssemblyShadowState::Failed, "partial-owner failure did not seal Failed state");
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::InvalidState,
        "partial-owner failure unexpectedly allowed Abort");
    CheckRecovery(AssemblyShadowState::Failed, "RestartRequired", 9, false, true);
    std::cout << "r01_skeleton_outcome=partial-owner syntheticOwner=1 publication=none\n";
}

void CheckPostPublicationInitializerFailure(const Bytes& bytes, const std::string& name)
{
    hybridclr::metadata::r01BackendMode = hybridclr::metadata::R01BackendMode::InitializerFailure;
    ConfigureAndBegin(name);
    Check(il2cpp::vm::AssemblyShadow::StageAssembly(bytes.data(), bytes.size(), nullptr, 0) ==
        AssemblyShadowError::Success, "synthetic skeleton was rejected");
    Check(il2cpp::vm::AssemblyShadow::ValidateTransaction() == AssemblyShadowError::Success,
        "synthetic metadata validation was rejected");
    Check(il2cpp::vm::AssemblyShadow::CommitTransaction() == AssemblyShadowError::ModuleInitializerFailed,
        "injected initializer failure did not return error 19");
    CheckRecovery(AssemblyShadowState::FailedAfterCommit, "RestartRequired", 19, true, true);
    // The active snapshot makes rejected post-publication mutations return
    // AlreadyCommitted (18), while recovery remains terminal error 19.
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::AlreadyCommitted,
        "post-publication failure unexpectedly allowed Abort");
    AssemblyShadowState state = AssemblyShadowState::Disabled;
    Check(il2cpp::vm::AssemblyShadow::GetState(state) == AssemblyShadowError::Success &&
        state == AssemblyShadowState::FailedAfterCommit, "post-publication terminal state changed");
    Check(il2cpp::vm::AssemblyShadow::CommitTransaction() == AssemblyShadowError::AlreadyCommitted,
        "post-publication Commit did not remain rejected");
    CheckRecovery(AssemblyShadowState::FailedAfterCommit, "RestartRequired", 19, true, true);
    std::cout << "r01_initializer_failure=pass injectedBackendOutcome=ModuleInitializerFailed syntheticPublication=1 publication=production-callbacks abort=AlreadyCommitted\n";
}

void CheckPoison(const std::string& name)
{
    ConfigureAndBegin(name);
    Check(il2cpp::vm::AssemblyShadow::ReportUnexpectedFailure() == AssemblyShadowError::InternalError,
        "unexpected failure was not reported");
    Check(il2cpp::vm::AssemblyShadow::AbortTransaction() == AssemblyShadowError::InvalidState,
        "poisoned transaction allowed Abort");
    std::string diagnostics;
    Check(il2cpp::vm::AssemblyShadow::GetDiagnosticsJson(diagnostics) == AssemblyShadowError::Success,
        "poisoned diagnostics unavailable");
    Check(Has(diagnostics, "Unexpected native failure sealed the transaction"),
        "poison detail was not retained");
    CheckRecovery(AssemblyShadowState::Failed, "RestartRequired", 20, false, false);
    Check(il2cpp::vm::AssemblyShadow::ReportUnexpectedFailure() == AssemblyShadowError::InternalError,
        "second poison call changed terminal error");
    std::cout << "r01_poison=pass sticky=1 injectedBackendOutcome=none publication=none\n";
}


}

namespace il2cpp { namespace vm {
void AssemblyShadowVisibility::RegisterPrivateImage(const Il2CppImage*) {}
bool MetadataCache::PublishInterpreterAssembliesBatch(const std::vector<Il2CppAssembly*>& assemblies,
    bool (*tryBegin)(void*), void (*publishActive)(void*), void* context)
{
    // Controlled logical publication adapter. The production transaction
    // supplies both callbacks; this boundary executes them in order without
    // touching Unity's global assembly registry.
    (void)assemblies;
    if (!tryBegin(context)) return false;
    publishActive(context);
    return true;
}
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(const char* name)
{
    for (const Il2CppAssembly* assembly : physicalAssemblies)
        if (!hybridclr::metadata::IsInterpreterImage(assembly->image) &&
            assembly_shadow_detail::NameEquals(assembly_shadow_detail::ViewName(name),
                assembly_shadow_detail::ViewName(assembly->aname.name))) return assembly;
    return nullptr;
}

Il2CppMetadataTypeHandle MetadataCache::GetAssemblyTypeHandle(const Il2CppImage*, AssemblyTypeIndex)
{
    throw std::runtime_error("R01 physical fixture intentionally has no TypeDef rows");
}

const Il2CppAssembly* MetadataCache::GetReferencedAssemblyPhysical(const Il2CppAssembly* requester, int32_t index)
{
    auto found = references.find(requester);
    if (found == references.end() || index < 0 || static_cast<size_t>(index) >= found->second.size()) return nullptr;
    return found->second[static_cast<size_t>(index)];
}

Il2CppException* Exception::GetInvalidOperationException(const char* detail)
{
    exceptionMessage = detail ? detail : "invalid operation";
    return reinterpret_cast<Il2CppException*>(1);
}
Il2CppException* Exception::GetBadImageFormatException(const char* detail)
{ return GetInvalidOperationException(detail); }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::runtime_error(exceptionMessage); }
void AssemblyShadowVisibility::CollectOrdinaryClasses(std::vector<Il2CppClass*>&, uint64_t& generation)
{ generation = AssemblyShadow::ActiveGeneration(); }
bool AssemblyShadowVisibility::ClassUsesStagedMetadata(const Il2CppClass*) { return false; }
}}

int main(int argc, char** argv)
{
    try
    {
        Check(argc >= 3, "usage: r01_transaction <scenario> <dll>");
        const std::string scenario = argv[1];
        const Bytes bytes = ReadBytes(argv[2]);
        std::string name, detail;
        Check(hybridclr::metadata::Assembly::ReadStagedAssemblyIdentity(bytes.data(), bytes.size(), name, detail) ==
            AssemblyShadowError::Success, "fixture identity is not parseable");
        Fixture baseline(name.c_str());
        Fixture stable("mscorlib");
        if (scenario == "preowner") CheckPreOwner(name);
        else if (scenario == "validate-failure")
        {
            hybridclr::metadata::r01BackendMode = hybridclr::metadata::R01BackendMode::MetadataFailure;
            CheckValidateMetadataFailure(bytes, name);
        }
        else if (scenario == "baseline-use") CheckBaselineUse(bytes, name, baseline);
        else if (scenario == "poison") CheckPoison(name);
        else if (scenario == "skeleton") CheckPartialOwner(bytes, name);
        else if (scenario == "initializer") CheckPostPublicationInitializerFailure(bytes, name);
        else throw std::runtime_error("unknown R01 transaction scenario");
        std::cout << "r01_transaction_checks=" << checks << " scenario=" << scenario << " PASS\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "FAIL: " << error.what() << "\n";
        return 1;
    }
}
