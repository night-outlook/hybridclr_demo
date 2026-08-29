// Actual AssemblyShadow.cpp/TypeKey code, with the existing M05 physical-table,
// exception and interner adapters reused unchanged. This is not Player proof.
// The additional raw-metadata adapters below never materialize a class.
#define main M05UnusedMain
#define ASSEMBLY_SHADOW_M06_RAW_METADATA_FIXTURE 1
#include "m05_types.cpp"
#undef ASSEMBLY_SHADOW_M06_RAW_METADATA_FIXTURE
#undef main
#include "vm/GlobalMetadataFileInternals.h"
static_assert(static_cast<int32_t>(il2cpp::vm::AssemblyShadowError::BaselineMethodExecution) == 21, "M06 error ABI");

#if !HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
int main()
{
    std::string json = "must-clear";
    if (il2cpp::vm::AssemblyShadow::GetExecutionDiagnosticsJson(json) != il2cpp::vm::AssemblyShadowError::FeatureDisabled || !json.empty()) return 1;
    std::puts("m06_execution_disabled_checks=2 PASS");
    return 0;
}
#else
static_assert(noexcept(il2cpp::vm::AssemblyShadow::AssertMethodIsActive(nullptr, nullptr)), "Native callback boolean guard must be noexcept");
namespace {
std::unordered_map<const Il2CppTypeDefinition*, Il2CppClass*> rawDefinitions;
std::vector<const Il2CppType*> rawTypes;
std::unordered_map<const Il2CppClass*, int32_t> rawTypeIndices;

void RawMetadata(Il2CppClass* klass)
{
    auto definition = new Il2CppTypeDefinition();
    definition->declaringTypeIndex = klass->declaringType ? rawTypeIndices.at(klass->declaringType) : kTypeIndexInvalid;
    definition->genericContainerIndex = klass->genericContainerHandle ?
        static_cast<int32_t>(reinterpret_cast<uintptr_t>(klass->genericContainerHandle)) : kGenericContainerIndexInvalid;
    rawDefinitions[definition] = klass;
    klass->typeMetadataHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(definition);
    klass->byval_arg.data.typeHandle = klass->typeMetadataHandle;
    klass->this_arg = klass->byval_arg; klass->this_arg.byref = true;
    rawTypeIndices[klass] = static_cast<int32_t>(rawTypes.size());
    rawTypes.push_back(&klass->byval_arg);
}

MethodInfo Method(Il2CppClass* klass, const char* name = "Run")
{
    MethodInfo method = {};
    method.klass = klass;
    method.name = name;
    return method;
}

Il2CppClass* ClosedClass(Il2CppClass* definition, const Il2CppType* argument)
{
    auto generic = new Il2CppGenericClass();
    generic->type = &definition->byval_arg;
    auto instance = new Il2CppGenericInst();
    instance->type_argc = 1;
    auto arguments = new const Il2CppType*[1]; arguments[0] = argument;
    instance->type_argv = arguments;
    generic->context.class_inst = instance;
    auto klass = new Il2CppClass(*definition);
    klass->generic_class = generic;
    klass->genericContainerHandle = nullptr;
    klass->byval_arg.type = IL2CPP_TYPE_GENERICINST;
    klass->byval_arg.data.generic_class = generic;
    klass->static_fields = new int(0);
    generic->cached_class = klass;
    return klass;
}

uint64_t Counter(const std::string& json, const char* name)
{
    const std::string prefix = std::string("\"") + name + "\":";
    size_t at = json.find(prefix);
    if (at == std::string::npos) throw std::runtime_error("Missing execution counter");
    return std::stoull(json.substr(at + prefix.size()));
}
}

namespace il2cpp { namespace vm {
baselib::ReentrantLock g_MetadataLock;
std::pair<const char*, const char*> GlobalMetadata::GetTypeNamespaceAndName(Il2CppMetadataTypeHandle handle)
{
    auto klass = rawDefinitions.at(reinterpret_cast<const Il2CppTypeDefinition*>(handle));
    return {klass->namespaze, klass->name};
}
Il2CppMetadataGenericContainerHandle GlobalMetadata::GetGenericContainerFromIndex(GenericContainerIndex index)
{ return index == kGenericContainerIndexInvalid ? nullptr : reinterpret_cast<Il2CppMetadataGenericContainerHandle>(static_cast<uintptr_t>(index)); }
uint32_t GlobalMetadata::GetGenericContainerCount(Il2CppMetadataGenericContainerHandle handle)
{ return static_cast<uint32_t>(reinterpret_cast<uintptr_t>(handle)); }
const Il2CppType* GlobalMetadata::GetIl2CppTypeFromIndex(TypeIndex index) { return rawTypes.at(index); }
}}

int main(int argc, char** argv)
{
    using namespace il2cpp::vm;
    try
    {
        const std::string mode = argc > 1 ? argv[1] : "baseline";
        ImageFixture baseline("Tests.Business"), active("Tests.Business", true), stable("mscorlib"),
            unchanged("Tests.Unchanged"), lookalike("Tests.Business", true), aotLookalike("Tests.Business");
        il2cpp_defaults.object_class = stable.Type("Object", 0, nullptr, false, "System");
        il2cpp_defaults.int32_class = stable.Type("Int32", 0, nullptr, true, "System");
        il2cpp_defaults.string_class = stable.Type("String", 0, nullptr, false, "System");
        auto oldClass = baseline.Type("Business"), newClass = active.Type("Business");
        auto stableClass = unchanged.Type("Business"), privateClass = lookalike.Type("Business");
        auto aotLookalikeClass = aotLookalike.Type("Business");
        auto genericDefinition = active.Type("Statics`1", 1);
        auto outer = active.Type("Outer", 0, nullptr, false, "A");
        auto nested = active.Type("Inner", 0, outer, false, "");
        for (auto assembly : assemblies)
            for (auto klass : imageTypes[assembly->image]) RawMetadata(klass);
        MethodInfo oldMethod = Method(oldClass), activeMethod = Method(newClass), stableMethod = Method(stableClass), privateMethod = Method(privateClass);
        MethodInfo aotLookalikeMethod = Method(aotLookalikeClass);
        Check(AssemblyShadow::AssertMethodIsActive(&oldMethod, "before-configure"), "pre-Configure limitation remains explicit");
        Check(s_executionClassCount == 0, "pre-Configure class observations are absent");
        Check(AssemblyShadow::ConfigureCandidates("m06", {"Tests.Business", "Tests.Unchanged"}, {"mscorlib"}) == AssemblyShadowError::Success, "real registry");
        if (mode.find("args-") == 0)
        {
            const size_t readsBeforeArguments = metadataReads;
            Candidate* candidate = s_candidates.load()->byAssembly.at(&baseline.assembly);
            Check(s_candidates.load()->byTypeHandle.at(oldClass->typeMetadataHandle) == candidate,
                "Configure indexes exact raw candidate definitions");
            const Il2CppType* capturedTypes[] = {&oldClass->byval_arg};
            Il2CppGenericInst instance = {1, capturedTypes};
            Il2CppGenericMethod captured = {}; captured.methodDefinition = &stableMethod;
            captured.context.method_inst = &instance;
            MethodInfo method = stableMethod; method.is_inflated = true; method.genericMethod = &captured;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "early-argument"), "early captured baseline argument records use");
            Check(candidate->firstUse.present && candidate->firstUse.kind == BaselineUseKind::MethodExecution &&
                candidate->firstUse.klass == nullptr && std::string(candidate->firstUse.detail).find("Context=method_inst") != std::string::npos,
                "argument observation does not manufacture a class handle");
            Transaction blocked; blocked.closure.push_back({candidate, nullptr});
            Publication publication; publication.transaction = &blocked;
            Check(!TryBeginPublication(&publication) && publication.used == candidate,
                "prepublication generic argument use prevents publication");
            ActiveSnapshot snapshot;
            snapshot.byName.Add("Tests.Business", &active.assembly);
            snapshot.byAssembly.emplace(&baseline.assembly, &active.assembly);
            snapshot.byImage.emplace(&baseline.image, &active.image);
            snapshot.shadowToBaseline.emplace(&active.assembly, &baseline.assembly);
            s_active.store(&snapshot, std::memory_order_release);
            s_state.store(AssemblyShadowState::Committed);
            capturedTypes[0] = &newClass->byval_arg;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "active-argument"), "stable AOT body with active shadow method argument is legal");
            captured.context.class_inst = &instance;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "active-both-contexts"), "both active contexts remain legal");
            capturedTypes[0] = &stableClass->byval_arg;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "unchanged-argument"), "unchanged candidate AOT argument remains legal");
            Il2CppType primitive = {}; primitive.type = IL2CPP_TYPE_I4;
            capturedTypes[0] = &primitive;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "primitive-argument"), "primitive argument legal without class lookup");
            captured.context = {};
            Check(AssemblyShadow::AssertMethodIsActive(&method, "absent-contexts"), "absent optional contexts stay legal");
            Il2CppType pointer = {}; pointer.type = IL2CPP_TYPE_PTR; pointer.data.type = &newClass->byval_arg;
            Il2CppArrayType array = {}; array.rank = 2; array.etype = &pointer;
            Il2CppType arrayType = {}; arrayType.type = IL2CPP_TYPE_ARRAY; arrayType.data.array = &array;
            Il2CppType vectorType = {}; vectorType.type = IL2CPP_TYPE_SZARRAY; vectorType.data.type = &arrayType; vectorType.byref = true;
            const Il2CppType* nestedTypes[] = {&vectorType};
            Il2CppGenericInst nestedInstance = {1, nestedTypes};
            Il2CppGenericClass generic = {}; generic.type = &stableClass->byval_arg; generic.context.class_inst = &nestedInstance;
            Il2CppType composite = {}; composite.type = IL2CPP_TYPE_GENERICINST; composite.data.generic_class = &generic;
            capturedTypes[0] = &composite; captured.context.method_inst = &instance;
            Check(AssemblyShadow::AssertMethodIsActive(&method, "active-composite"), "active generic-array-pointer-byref components legal");
            AssemblyShadowError expected = AssemblyShadowError::BaselineAlreadyUsed;
            const char* reason = "CapturedBaselineType";
            if (mode == "args-class")
            { capturedTypes[0] = &oldClass->byval_arg; captured.context.method_inst = nullptr; captured.context.class_inst = &instance; }
            else if (mode == "args-method") capturedTypes[0] = &oldClass->byval_arg;
            else if (mode == "args-composite") pointer.data.type = &oldClass->byval_arg;
            else if (mode == "args-declaring")
            {
                auto closed = ClosedClass(stableClass, &oldClass->byval_arg);
                method = Method(closed);
            }
            else
            {
                expected = AssemblyShadowError::InvalidArgument;
                if (mode == "args-null") { capturedTypes[0] = nullptr; reason = "NullType"; }
                else if (mode == "args-empty") { instance.type_argc = 0; reason = "EmptyGenericInstance"; }
                else if (mode == "args-null-vector") { instance.type_argv = nullptr; reason = "EmptyGenericInstance"; }
                else if (mode == "args-open") { primitive.type = IL2CPP_TYPE_MVAR; capturedTypes[0] = &primitive; reason = "OpenGenericArgument"; }
                else if (mode == "args-recursive") { pointer.data.type = &pointer; capturedTypes[0] = &pointer; reason = "PathLimit"; }
                else if (mode == "args-array") { array.rank = 0; reason = "MalformedArray"; }
                else if (mode == "args-generic") { generic.context.method_inst = &instance; reason = "MalformedGenericClass"; }
                else throw std::runtime_error("Unknown argument test mode");
            }
            Check(!AssemblyShadow::AssertMethodIsActive(&method, mode.c_str()), "captured stale or malformed argument fails closed");
            Check(s_typeFailure.load()->error == expected && s_typeFailure.load()->detail.find(reason) != std::string::npos &&
                s_typeFailure.load()->detail.find("TypePath=") != std::string::npos && s_state.load() == AssemblyShadowState::FailedAfterCommit,
                "captured failure has precise detail and seals committed state");
            Check(s_rejectedBaselineMethods.load() == 0, "captured argument failure is not a baseline-body rejection");
            Check(metadataReads == readsBeforeArguments, "all captured-context checks avoid metadata materialization");
            Check(captured.methodDefinition == &stableMethod, "captured MethodInfo never remapped");
            std::printf("m06_argument_failure=%s\n", s_typeFailure.load()->detail.c_str());
            std::printf("m06_execution_checks=%zu mode=%s metadata_reads=%zu PASS\n", checks, mode.c_str(), metadataReads);
            return 0;
        }
        Check(AssemblyShadow::AssertMethodIsActive(&oldMethod, "before-publication"), "prepublication body admitted with use marker");
        Candidate* candidate = s_candidates.load()->byAssembly.at(&baseline.assembly);
        Check(candidate->firstUse.present && candidate->firstUse.kind == BaselineUseKind::MethodExecution, "method first-use kind");
        Transaction blocked; blocked.closure.push_back({candidate, nullptr});
        Check(UsedClosureMember(blocked) == candidate, "actual publication precheck sees early method use");
        Publication blockedPublication; blockedPublication.transaction = &blocked;
        Check(!TryBeginPublication(&blockedPublication) && blockedPublication.used == candidate,
            "actual publication callback refuses prepublication method use");
        // Independent immutable-published fixture. No real transaction bypass is
        // claimed: it deliberately retains physical baseline MethodInfo handles.
        ActiveSnapshot snapshot;
        snapshot.byName.Add("Tests.Business", &active.assembly);
        snapshot.byAssembly.emplace(&baseline.assembly, &active.assembly);
        snapshot.byImage.emplace(&baseline.image, &active.image);
        snapshot.shadowToBaseline.emplace(&active.assembly, &baseline.assembly);
        s_active.store(&snapshot, std::memory_order_release);
        s_state.store(AssemblyShadowState::Committed);
        const size_t readsBefore = metadataReads;
        Check(AssemblyShadow::AssertMethodIsActive(&activeMethod, "active"), "active method legal");
        Check(AssemblyShadow::AssertMethodIsActive(&stableMethod, "stable"), "registered stable AOT outside closure legal");
        Check(AssemblyShadow::AssertMethodIsActive(&privateMethod, "lookalike"), "same-name private interpreter is not baseline identity");
        Check(AssemblyShadow::AssertMethodIsActive(&aotLookalikeMethod, "aot-lookalike"), "same-name AOT image is not the exact published baseline");
        Check(!s_candidates.load()->byAssembly.at(&baseline.assembly)->firstUse.detail[0] ||
            std::string(candidate->firstUse.detail) == "before-publication", "first use remains first");
        Il2CppGenericMethod inflatedDefinition = {}; inflatedDefinition.methodDefinition = &oldMethod;
        MethodInfo inflated = Method(newClass); inflated.is_inflated = true; inflated.genericMethod = &inflatedDefinition;
        if (mode == "prior")
        {
            try { AssemblyShadow::FailTypeResolution(AssemblyShadowError::ResourceAbiMismatch, "first-type-failure"); }
            catch (const std::exception&) {}
        }
        if (mode == "reference")
        {
            try { FailReference(&unchanged.assembly, "Tests.Business", 3, "first-reference-failure"); }
            catch (const std::exception&) {}
        }
        if (mode == "null") Check(!AssemblyShadow::AssertMethodIsActive(nullptr, "null"), "null guard returns false");
        else if (mode == "inflated") Check(!AssemblyShadow::AssertMethodIsActive(&inflated, "inflated"), "baseline definition rejected through active-looking owner");
        else Check(!AssemblyShadow::AssertMethodIsActive(&oldMethod, "retained-baseline"), "retained exact baseline rejected");
        AssemblyShadowError firstError = mode == "reference" ? AssemblyShadowError::ReferenceEscapesClosure :
            mode == "prior" ? AssemblyShadowError::ResourceAbiMismatch :
            mode == "null" ? AssemblyShadowError::InvalidArgument : AssemblyShadowError::BaselineMethodExecution;
        Check(s_typeFailure.load()->error == firstError && s_state.load() == AssemblyShadowState::FailedAfterCommit, "exact first error and sealing");
        Check(!AssemblyShadow::AssertMethodIsActive(&inflated, "later-inflated"), "inflated physical definition rejected");
        Check(oldMethod.klass == oldClass && inflated.klass == newClass && inflated.genericMethod->methodDefinition == &oldMethod,
            "method guards never remap or rewrite physical handles");
        bool threw = false;
        try { AssemblyShadow::RequireActiveMethod(&oldMethod, "wrapper"); }
        catch (const std::exception&) { threw = true; }
        Check(threw && s_typeFailure.load()->error == firstError, "throwing wrapper cannot continue and retains first error");
        {
            AssemblyShadowTypeMetadataScope scope;
            bool rejectedInScope = false;
            try { AssemblyShadow::RequireActiveMethod(&oldMethod, "physical-metadata-boundary"); }
            catch (const ShadowTypeResolutionFailure& failure) { rejectedInScope = failure.error == firstError; }
            Check(rejectedInScope, "physical metadata scope never exempts a baseline method");
            bool executionDenied = false;
            try { AssemblyShadow::RequireActiveMethod(&activeMethod, "physical-metadata-active-body"); }
            catch (const std::runtime_error&) { executionDenied = true; }
            Check(executionDenied, "even active user code cannot run inside metadata-only scope");
        }
        Check(metadataReads == readsBefore, "guards never resolve or materialize metadata");
        auto integers = ClosedClass(genericDefinition, &il2cpp_defaults.int32_class->byval_arg);
        auto strings = ClosedClass(genericDefinition, &il2cpp_defaults.string_class->byval_arg);
        auto integerMethod = Method(integers), stringMethod = Method(strings), nestedMethod = Method(nested);
        AssemblyShadow::AssertMethodIsActive(&integerMethod, "closed-int");
        AssemblyShadow::AssertMethodIsActive(&stringMethod, "closed-string");
        AssemblyShadow::AssertMethodIsActive(&nestedMethod, "nested");
        integers->cctor_started = 1; integers->cctor_finished_or_no_cctor = 1;
        strings->cctor_started = 1; strings->initializationExceptionGCHandle = 1;
        AssemblyShadow::ObserveClassCctorStarted(integers);
        AssemblyShadow::ObserveClassCctorStarted(strings);
        AssemblyShadow::ObserveClassCctorStarted(stableClass);
        Check(s_shadowClassCctorStarted.load() == 2 && s_baselineClassCctorStarted.load() == 0, "cctor counters exclude unchanged providers");
        AssemblyShadow::ObserveInterpreterTransformation(&activeMethod);
        AssemblyShadow::ObserveInterpreterTransformation(&stableMethod);
        Check(s_interpreterTransformations.load() == 2 && s_shadowInterpreterTransformations.load() == 1, "actual transformation hook subset");
        const size_t observed = s_executionClassCount;
        const uint64_t previousChecks = s_methodChecks.load();
        for (size_t index = 0; index < 100000; ++index) AssemblyShadow::AssertMethodIsActive(&activeMethod, "repeat");
        Check(s_methodChecks.load() - previousChecks == 100000, "methodChecks counts observations, not unique bodies");
        Check(s_executionClassCount == observed && s_droppedClassObservations.load() == 0, "repeated checks have bounded deduplicated class storage");
        std::string execution;
        Check(AssemblyShadow::GetExecutionDiagnosticsJson(execution) == AssemblyShadowError::Success, "execution schema serializes");
        Check(metadataReads == readsBefore, "metadata-only diagnostics never materialize classes");
        Check(execution.find("generic(") != std::string::npos && execution.find("/0:/5:Inner@0") != std::string::npos, "closed generic and nested keys are structural");
#if IL2CPP_DEBUG
        Check(execution.find("\"staticStoragePointer\":\"0x") != std::string::npos, "development actual storage address");
#else
        Check(execution.find("\"pointerDetailsAvailable\":true") == std::string::npos && execution.find("0x") == std::string::npos, "release addresses hidden");
#endif
        Check(s_typeFailure.load()->error == firstError, "diagnostic query preserves transaction failure");
        std::string transaction;
        Check(AssemblyShadow::GetDiagnosticsJson(transaction) == AssemblyShadowError::Success &&
            transaction.find("\"lastError\":" + std::to_string(static_cast<int>(firstError))) != std::string::npos &&
            transaction.find("\"stateCode\":9") != std::string::npos, "first method/reference/type failure inspectable after catch");
        std::printf("m06_guard_json=%s\n", transaction.c_str());
        std::printf("m06_execution_json=%s\n", execution.c_str());
        if (mode == "concurrent")
        {
            std::thread writer([&] {
                for (size_t index = 0; index < 50000; ++index)
                {
                    AssemblyShadow::AssertMethodIsActive(&activeMethod, "concurrent");
                    AssemblyShadow::ObserveInterpreterTransformation(&activeMethod);
                }
            });
            bool valid = true;
            for (size_t index = 0; index < 50; ++index)
            {
                valid = valid && AssemblyShadow::GetExecutionDiagnosticsJson(execution) == AssemblyShadowError::Success;
                valid = valid && Counter(execution, "shadowMethodChecks") <= Counter(execution, "methodChecks") &&
                    Counter(execution, "rejectedBaselineMethods") <= Counter(execution, "methodChecks") &&
                    Counter(execution, "shadowInterpreterTransformations") <= Counter(execution, "interpreterTransformations");
            }
            writer.join();
            Check(valid, "concurrent execution snapshots preserve subset invariants");
        }
        if (mode == "overflow")
        {
            std::vector<std::string> names;
            names.reserve(kMaximumExecutionClasses + 1);
            for (size_t index = 0; index <= kMaximumExecutionClasses; ++index)
            {
                names.push_back("Observed" + std::to_string(index));
                auto extraClass = active.Type(names.back().c_str()); RawMetadata(extraClass);
                auto extraMethod = Method(extraClass);
                AssemblyShadow::AssertMethodIsActive(&extraMethod, "bounded-overflow");
            }
            Check(s_executionClassCount == kMaximumExecutionClasses && s_droppedClassObservations.load() > 0, "class observation overflow is bounded and counted");
            Check(AssemblyShadow::GetExecutionDiagnosticsJson(execution) == AssemblyShadowError::Success &&
                execution.find("\"droppedClassObservations\":0") == std::string::npos, "dropped observation count appears in actual JSON");
            std::printf("m06_overflow_dropped=%llu\n", static_cast<unsigned long long>(s_droppedClassObservations.load()));
        }
        std::printf("m06_execution_checks=%zu mode=%s metadata_reads=%zu PASS\n", checks, mode.c_str(), metadataReads);
        return 0;
    }
    catch (const std::exception& failure) { std::fprintf(stderr, "M06 FAIL: %s\n", failure.what()); return 1; }
}
#endif
