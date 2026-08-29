// Focused actual-code resolver test, NOT Player/transaction acceptance.
// Includes the production core to construct immutable metadata/snapshot fixtures
// without exposing a test mutation API in the runtime. Assembly enumeration,
// resolver, closure scan, TLS, error seal and diagnostics execute real code.
// Adapters supply physical metadata tables and a managed-exception boundary;
// no managed objects, class materialization or module initializers are modeled.
#include "vm/AssemblyShadow.cpp"
#include <cstdio>
#include <cstdlib>
#include <new>
#include "utils/Memory.h"

static std::atomic<size_t> allocations{0};
void* operator new(size_t size)
{
    ++allocations;
    if (void* p = std::malloc(size ? size : 1)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void* operator new[](size_t size) { return ::operator new(size); }
void operator delete[](void* p) noexcept { ::operator delete(p); }
size_t CheckDeclaredReferenceIdentity(const char* fixture);

namespace {
using namespace il2cpp::vm;
il2cpp::vm::AssemblyVector physicalTables;
std::unordered_map<const Il2CppAssembly*, il2cpp::vm::AssemblyVector> referenceTables;
std::string exceptionMessage;
ActiveSnapshot* pendingPublication = nullptr;
size_t checks = 0;
void Check(bool value, const char* detail)
{
    ++checks;
    if (!value) throw std::runtime_error(detail);
}
struct Fixture
{
    Il2CppAssembly assembly = {};
    Il2CppImage image = {};
    Fixture(const char* name, bool interpreter = false, bool token = true)
    {
        assembly.aname.name = name;
        assembly.aname.culture = "";
        assembly.image = &image;
        assembly.token = token ? 1 : 0;
        image.assembly = &assembly;
        image.name = image.nameNoExt = name;
        image.token = interpreter ? (UINT32_C(1) << 31) : 0;
        physicalTables.push_back(&assembly);
    }
};
const Il2CppAssembly* PrivateLookup(const char* name, void* context)
{
    return assembly_shadow_detail::NameEquals(assembly_shadow_detail::ViewName(name),
        assembly_shadow_detail::ViewName("Tests.Contracts")) ? static_cast<Il2CppAssembly*>(context) : nullptr;
}
}

namespace il2cpp { namespace utils { void Memory::Free(void* p) { std::free(p); } }}
namespace il2cpp { namespace vm {
// M06 Configure indexes physical TypeDefs. This Assembly-only fixture has no
// TypeDefs; any attempted lookup is outside its declared metadata boundary.
Il2CppMetadataTypeHandle MetadataCache::GetAssemblyTypeHandle(const Il2CppImage*, AssemblyTypeIndex)
{ throw std::runtime_error("M04 fixture has no physical type definitions"); }
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(const char* name)
{
    for (const Il2CppAssembly* assembly : physicalTables)
        if (!hybridclr::metadata::IsInterpreterImage(assembly->image) &&
            assembly_shadow_detail::NameEquals(assembly_shadow_detail::ViewName(name),
                assembly_shadow_detail::ViewName(assembly->aname.name))) return assembly;
    return nullptr;
}
const Il2CppAssembly* MetadataCache::GetAssemblyByNameOriginal(const char* name)
{
    const Il2CppAssembly* result = GetAotAssemblyByNamePhysical(name);
    // Model a loader callback that publishes while the ordinary lookup is in
    // progress. The actual Assembly publication lock/version path executes.
    if (pendingPublication)
    {
        ActiveSnapshot* publish = pendingPublication;
        pendingPublication = nullptr;
        Check(Assembly::PublishShadowBatch({publish->byName.Find(name)}, [](void*) { return true; },
            [](void* p) { s_active.store(static_cast<ActiveSnapshot*>(p), std::memory_order_release); }, publish),
            "real locked batch/list invalidation during original lookup");
    }
    return result;
}
const Il2CppAssembly* MetadataCache::GetReferencedAssemblyPhysical(const Il2CppAssembly* requester, int32_t index)
{
    return referenceTables.at(requester).at(index);
}
Il2CppException* Exception::GetInvalidOperationException(const char* detail)
{
    exceptionMessage = detail;
    return reinterpret_cast<Il2CppException*>(1);
}
Il2CppException* Exception::GetBadImageFormatException(const char* detail) { return GetInvalidOperationException(detail); }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::runtime_error(exceptionMessage); }
void AssemblyShadowVisibility::CollectOrdinaryClasses(std::vector<Il2CppClass*>&, uint64_t& generation)
{
    generation = AssemblyShadow::ActiveGeneration();
}
bool AssemblyShadowVisibility::ClassUsesStagedMetadata(const Il2CppClass*) { return false; }
}}

int main(int argc, char** argv)
{
    using namespace il2cpp::vm;
    try
    {
        Check(argc == 2, "one declared-reference DLL fixture is required");
        const size_t referenceChecks = CheckDeclaredReferenceIdentity(argv[1]);
        Fixture baseline("Tests.Contracts"), unchanged("Tests.Unchanged"), stable("mscorlib"), external("Tests.Consumer");
        Fixture shadow("Tests.Contracts", true), dynamic("Tests.Dynamic", true), duplicate("TESTS.DYNAMIC", true);
        Fixture placeholder("Tests.Placeholder", true, false), unapproved("Tests.Unapproved");
        for (Fixture* fixture : { &baseline, &stable, &unchanged, &external, &placeholder })
            Assembly::Register(&fixture->assembly);
        Check(AssemblyShadow::ConfigureCandidates("fixture-baseline", {"Tests.Contracts", "Tests.Unchanged"}, {"mscorlib"}) == AssemblyShadowError::Success,
            "configure actual registry");
        Check(AssemblyShadow::BeginTransaction("fixture-patch", "fixture-baseline", {"Tests.Contracts"}, kAssemblyShadowRuntimeAbiVersion) == AssemblyShadowError::Success,
            "begin actual private closure");
        il2cpp::vm::AssemblyVector before = *Assembly::GetAllAssemblies();
        Check(before.size() == 4 && before.front() == &baseline.assembly, "precommit logical snapshot and placeholder filtering");
        Check(AssemblyShadow::ResolveByName("Tests.Contracts", AssemblyResolveContext::Normal) == nullptr, "normal unresolved before commit");
        std::vector<hybridclr::metadata::StagedAssembly*> privateImages;
        {
            hybridclr::metadata::ScopedStagingResolver scope(privateImages, PrivateLookup, &shadow.assembly);
            Check(AssemblyShadow::CurrentResolveContext() == AssemblyResolveContext::Staging, "explicit private context");
            Check(AssemblyShadow::ResolveByName("Tests.Contracts.dll", AssemblyResolveContext::Staging) == &shadow.assembly, "private pointer");
            Check(AssemblyShadow::ResolveByName("Tests.Contracts", AssemblyResolveContext::Normal) == nullptr, "normal does not inherit TLS");
            Check(Assembly::Load("Tests.Contracts") == &shadow.assembly, "native type-name Load preserves private staging context");
            Check(Assembly::LoadOriginal("Tests.Contracts") == &baseline.assembly, "explicit original Load remains physical inside private scope");
            Check(AssemblyShadow::ResolveByName("Tests.Contracts", AssemblyResolveContext::DiagnosticsPhysical) == &baseline.assembly, "physical ignores TLS");
            bool missing = false;
            try { AssemblyShadow::ResolveReferencedAssembly(&shadow.assembly, &unchanged.assembly, "Tests.Missing", 3, "test.private"); }
            catch (const std::runtime_error& e) { missing = std::string(e.what()).find("ReferenceIndex=3") != std::string::npos; }
            Check(missing, "private missing reference must throw with index and never baseline fallback");
        }
        external.assembly.referencedAssemblyCount = 1;
        referenceTables[&external.assembly] = { &baseline.assembly };
        Check(CheckExternalReferences(Current(), s_candidates.load()) == AssemblyShadowError::ReferenceEscapesClosure, "external AOT static guard");
        Check(Current().detail.find("Path=Tests.Consumer -> Tests.Contracts") != std::string::npos &&
            Current().detail.find("ReferenceIndex=0") != std::string::npos, "static guard path and row evidence");
        external.assembly.referencedAssemblyCount = 0;
        baseline.assembly.referencedAssemblyCount = 1;
        referenceTables[&baseline.assembly] = { &baseline.assembly };
        Check(CheckExternalReferences(Current(), s_candidates.load()) == AssemblyShadowError::Success, "baseline closure requester is semantic closure member");

        ActiveSnapshot active;
        active.byName.Add("Tests.Contracts", &shadow.assembly);
        active.byAssembly.emplace(&baseline.assembly, &shadow.assembly);
        active.byImage.emplace(&baseline.image, &shadow.image);
        active.shadowToBaseline.emplace(&shadow.assembly, &baseline.assembly);
        pendingPublication = &active;
        Check(Assembly::Load("Tests.Contracts") == &shadow.assembly && pendingPublication == nullptr,
            "post-original-load re-resolution observes newly published active pointer");
        s_state.store(AssemblyShadowState::Committing); // Guard is required during initializers too.
        Assembly::Register(&dynamic.assembly);
        Assembly::Register(&duplicate.assembly);
        il2cpp::vm::AssemblyVector logical = *Assembly::GetAllAssemblies();
        Check(logical.size() == 5 && logical[0] == &shadow.assembly && logical[1] == &stable.assembly && logical.back() == &dynamic.assembly,
            "stable baseline slot, canonical dedup and ordinary dynamic order");
        il2cpp::vm::AssemblyVector physical;
        Check(Assembly::CaptureShadowEnumeration(physical) == 1 && physical.size() == 7, "M03 diagnostics retain physical duplicates");
        Check(before.front() == &baseline.assembly, "retained old snapshot is immutable");
        for (const char* name : {"Tests.Contracts", "tests.contracts.dll", "a/b/TESTS.CONTRACTS.DLL", "a\\b\\tests.contracts.exe", "Tests.Contracts, Version=2.3.4.5"})
        {
            Check(AssemblyShadow::ResolveByName(name, AssemblyResolveContext::Normal) == &shadow.assembly, "canonical active resolver");
            Check(Assembly::Load(name) == &shadow.assembly, "public Load active identity");
            Check(Assembly::GetLoadedAssembly(name) == &shadow.assembly, "loaded active identity");
            Check(AssemblyShadow::ResolveByName(name, AssemblyResolveContext::DiagnosticsPhysical) == &baseline.assembly, "physical never redirects");
        }
        Check(Assembly::GetLoadedAssemblyPhysical("tests.contracts", PhysicalAssemblyPreference::AotOnly) == &baseline.assembly, "physical AOT preference");
        Check(Assembly::GetLoadedAssemblyPhysical("tests.contracts", PhysicalAssemblyPreference::InterpreterOnly) == &shadow.assembly, "physical interpreter preference");
        Check(AssemblyShadow::ResolveReferencedAssembly(&baseline.assembly, &baseline.assembly, "Tests.Contracts", 0, "test.baseline") == &shadow.assembly,
            "baseline pointer is semantic closure requester");
        Check(AssemblyShadow::ResolveReferencedAssembly(&shadow.assembly, &stable.assembly, "mscorlib", 1, "test.stable") == &stable.assembly, "approved stable provider");
        Check(AssemblyShadow::ResolveReferencedAssembly(&shadow.assembly, &unchanged.assembly, "Tests.Unchanged", 2, "test.unchanged") == &unchanged.assembly,
            "unchanged registered candidate remains AOT");
        Check(AssemblyShadow::ResolveReferencedAssembly(&dynamic.assembly, &baseline.assembly, "Tests.Contracts", 0, "test.dynamic") == &shadow.assembly,
            "ordinary interpreter consumer redirects");
        const size_t allocationsBefore = allocations.load();
        auto start = std::chrono::steady_clock::now();
        size_t hits = 0;
        for (size_t i = 0; i < 1000000; ++i)
            hits += AssemblyShadow::ResolveByName("some/path/TESTS.CONTRACTS.dll", AssemblyResolveContext::Normal) == &shadow.assembly;
        auto micros = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - start).count();
        const size_t lookupAllocations = allocations.load() - allocationsBefore;
        Check(hits == 1000000 && lookupAllocations == 0, "million name lookups must not allocate");
        bool escaped = false;
        try { AssemblyShadow::ResolveReferencedAssembly(&external.assembly, &baseline.assembly, "Tests.Contracts", 7, "test.runtime"); }
        catch (const std::runtime_error& e) { escaped = std::string(e.what()).find("ReferenceIndex=7") != std::string::npos; }
        Check(escaped && s_state.load() == AssemblyShadowState::FailedAfterCommit, "external runtime guard seals during initializers");
        std::string diagnostics;
        Check(AssemblyShadow::GetDiagnosticsJson(diagnostics) == AssemblyShadowError::Success, "diagnostics remain available after catch");
        Check(diagnostics.find("\"lastError\":14") != std::string::npos && diagnostics.find("Path=Tests.Consumer -> Tests.Contracts") != std::string::npos,
            "existing diagnostic schema preserves error14 and first failure path");
        bool unapprovedFailed = false;
        try { AssemblyShadow::ResolveReferencedAssembly(&shadow.assembly, &unapproved.assembly, "Tests.Unapproved", 9, "test.unapproved"); }
        catch (const std::runtime_error&) { unapprovedFailed = true; }
        Check(unapprovedFailed, "closed requester cannot widen stable AOT after sealed failure");
        bool unknownFailed = false;
        try { AssemblyShadow::ResolveReferencedAssembly(nullptr, &baseline.assembly, "Tests.Contracts", 4, "test.unknown"); }
        catch (const std::runtime_error&) { unknownFailed = true; }
        Check(unknownFailed, "unknown requester cannot bypass active-closure authorization");
        std::string after;
        AssemblyShadow::GetDiagnosticsJson(after);
        Check(after.find("Path=Tests.Consumer -> Tests.Contracts") != std::string::npos, "bounded first failure is retained");
        std::printf("m04_resolution_checks=%zu lookup_count=%zu lookup_allocations=%zu lookup_microseconds=%lld PASS\n",
            checks, hits, lookupAllocations, static_cast<long long>(micros));
        std::printf("m04_guard_diagnostics=%s\n", after.c_str());
        std::printf("m04_reference_identity_checks=%zu PASS\n", referenceChecks);
        return 0;
    }
    catch (const std::exception& e) { std::fprintf(stderr, "FAIL: %s\n", e.what()); return 1; }
}
