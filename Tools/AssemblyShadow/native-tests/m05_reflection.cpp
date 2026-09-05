// Boundary regression, not a VM/core simulation. Include the actual reflection
// implementation so its real cache maps can be initialized without VM startup.
// Link RuntimeAssembly.cpp, System/Object.cpp, Type.cpp and the runtime adapter;
// do NOT additionally compile Reflection.cpp. Resolver/guard and allocation
// seams below are controlled; cache/key/member/exposure code is production.
#include <cstdlib>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "vm/Reflection.cpp"
#include "vm/Type.h"
#include "icalls/mscorlib/System/Object.h"
#include "icalls/mscorlib/System.Reflection/RuntimeAssembly.h"
#include "hybridclr/AssemblyShadowRuntimeApi.h"

Il2CppDefaults il2cpp_defaults = {};

namespace {
size_t s_checks = 0, s_allocations = 0, s_typeResolves = 0, s_moduleUses = 0, s_guardFailures = 0;
size_t s_queryCalls = 0, s_mutations = 0;
bool s_throwQuery = false, s_throwString = false;
std::vector<void*> s_objects;
std::string s_lastString;
Il2CppAssembly s_baselineAssembly = {}, s_activeAssembly = {}, s_stableAssembly = {};
Il2CppImage s_baselineImage = {}, s_activeImage = {}, s_stableImage = {};
Il2CppClass s_baselineClass = {}, s_activeClass = {}, s_stableClass = {}, s_reflectionClass = {};
MethodInfo s_baselineMethod = {}, s_activeMethod = {}, s_unmappedBaselineMethod = {};
Il2CppException s_exception = {};

void Check(bool condition, const char* detail)
{
    if (!condition) throw std::runtime_error(detail);
    ++s_checks;
}
void Rejected(const std::function<void()>& action, const char* detail)
{
    bool threw = false;
    try { action(); } catch (const std::runtime_error&) { threw = true; }
    Check(threw, detail);
}
void* ManagedAllocation(size_t bytes)
{
    void* value = std::calloc(1, bytes);
    if (!value) throw std::bad_alloc();
    s_objects.push_back(value);
    ++s_allocations;
    return value;
}
}

namespace il2cpp { namespace gc {
void* GarbageCollector::AllocateFixed(size_t size, void*) { return std::calloc(1, size); }
void GarbageCollector::FreeFixed(void* value) { std::free(value); }
void* GarbageCollector::CallWithAllocLockHeld(GCCallWithAllocLockCallback callback, void* context) { return callback(context); }
}}
namespace il2cpp { namespace os {
// RuntimeAssembly.cpp owns an unrelated resource-file mutex. Its static
// lifetime is adapted, but resource locking remains unresolved/fail-closed.
// Reflection caches still execute their actual baselib reader/writer locks.
Mutex::Mutex(bool) : m_Mutex(nullptr) {}
Mutex::~Mutex() {}
}}
namespace il2cpp { namespace vm {
Il2CppObject* Object::New(Il2CppClass* klass)
{
    Il2CppObject* result = static_cast<Il2CppObject*>(ManagedAllocation(1024));
    result->klass = klass;
    return result;
}
Il2CppString* String::New(const char* value)
{
    if (s_throwString) throw std::runtime_error("Injected String::New failure");
    s_lastString = value;
    Il2CppString* result = static_cast<Il2CppString*>(ManagedAllocation(sizeof(Il2CppString) + (s_lastString.size() + 1) * sizeof(Il2CppChar)));
    result->length = static_cast<int32_t>(s_lastString.size());
    for (size_t index = 0; index < s_lastString.size(); ++index) result->chars[index] = s_lastString[index];
    return result;
}
const char* Field::GetName(const FieldInfo* field) { return field->name; }
Il2CppException* Exception::GetNotSupportedException(const char*) { return &s_exception; }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::runtime_error("Controlled unsupported surface"); }
AssemblyShadowError AssemblyShadow::ReportUnexpectedFailure() { ++s_mutations; return AssemblyShadowError::InternalError; }
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
const Il2CppAssembly* AssemblyShadow::ResolveAssembly(const Il2CppAssembly* assembly)
{
    return assembly == &s_baselineAssembly ? &s_activeAssembly : assembly;
}
const Il2CppImage* AssemblyShadow::ResolveImage(const Il2CppImage* image)
{
    return image == &s_baselineImage ? &s_activeImage : image;
}
bool AssemblyShadow::IsActiveShadow(const Il2CppAssembly* assembly) { return assembly == &s_activeAssembly; }
const Il2CppType* AssemblyShadow::ResolveType(const Il2CppType* type)
{
    ++s_typeResolves;
    if (type == &s_baselineClass.byval_arg) return &s_activeClass.byval_arg;
    if (type == &s_baselineClass.this_arg) return &s_activeClass.this_arg;
    return type;
}
Il2CppClass* AssemblyShadow::ResolveClass(Il2CppClass* klass)
{
    return klass == &s_baselineClass ? &s_activeClass : klass;
}
const MethodInfo* AssemblyShadow::ResolveReflectionMethod(const MethodInfo* method)
{
    return method == &s_baselineMethod ? &s_activeMethod : method;
}
void AssemblyShadow::RequireActiveClass(Il2CppClass* klass, BaselineUseKind, const char*)
{
    if (klass == &s_baselineClass) { ++s_guardFailures; throw std::runtime_error("Rejected actual baseline owner"); }
}
void AssemblyShadow::RecordTypeUse(const Il2CppType*, BaselineUseKind, const char*) {}
void AssemblyShadow::TraceImage(const char*, const Il2CppImage*) {}
void AssemblyShadow::RecordBaselineUse(const Il2CppAssembly*, BaselineUseKind kind, const char*, const Il2CppClass*)
{
    if (kind == BaselineUseKind::ModuleReflection) ++s_moduleUses;
}
void AssemblyShadow::FailTypeResolution(AssemblyShadowError, const std::string& detail) { throw std::runtime_error(detail); }
AssemblyShadowError AssemblyShadow::GetTypeResolutionInfo(const Il2CppType* type, std::string& json)
{
    ++s_queryCalls;
    if (s_throwQuery) throw std::runtime_error("Injected query failure");
    Check(type == &s_activeClass.byval_arg, "Query adapter changed its input type");
    json = "{\"fixtureQuery\":true}";
    return AssemblyShadowError::Success;
}
#endif
}}

int main()
{
    try
    {
        using namespace il2cpp::vm;
        using hybridclr::AssemblyShadowRuntimeApi;
        Il2CppString* output = reinterpret_cast<Il2CppString*>(static_cast<uintptr_t>(1));
#if !HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        const int32_t disabled = static_cast<int32_t>(AssemblyShadowError::FeatureDisabled);
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(nullptr, nullptr) == disabled, "OFF null query must be FeatureDisabled");
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(reinterpret_cast<Il2CppReflectionType*>(static_cast<uintptr_t>(1)), &output) == disabled,
            "OFF query accessed a poisoned type argument");
        Check(!output && s_allocations == 0 && s_queryCalls == 0 && s_mutations == 0, "OFF query mutated/allocated output");
#else
        s_baselineAssembly.image = &s_baselineImage; s_baselineImage.assembly = &s_baselineAssembly;
        s_activeAssembly.image = &s_activeImage; s_activeImage.assembly = &s_activeAssembly;
        s_stableAssembly.image = &s_stableImage; s_stableImage.assembly = &s_stableAssembly;
        s_activeImage.name = "Candidate.dll"; s_activeImage.nameNoExt = "Candidate";
        s_baselineClass.image = &s_baselineImage; s_activeClass.image = &s_activeImage; s_stableClass.image = &s_stableImage;
        s_baselineClass.byval_arg.type = s_activeClass.byval_arg.type = s_stableClass.byval_arg.type = IL2CPP_TYPE_CLASS;
        // Opaque fixture identities: real cache hashing/comparison never
        // dereferences these handles, and no metadata accessor is substituted.
        s_baselineClass.byval_arg.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(&s_baselineClass);
        s_activeClass.byval_arg.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(&s_activeClass);
        s_stableClass.byval_arg.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(&s_stableClass);
        s_baselineClass.this_arg = s_baselineClass.byval_arg; s_baselineClass.this_arg.byref = 1;
        s_activeClass.this_arg = s_activeClass.byval_arg; s_activeClass.this_arg.byref = 1;
        il2cpp_defaults.runtimetype_class = &s_reflectionClass;
        s_System_Reflection_Assembly = s_System_Reflection_Module = s_System_Reflection_MethodInfo =
            s_System_Reflection_RuntimeFieldInfoKlass = s_System_Reflection_RuntimePropertyInfoKlass =
            s_System_Reflection_RuntimeEventInfoKlass = &s_reflectionClass;
        // Initialize only the production maps used here, without invoking full VM startup.
        s_TypeMap = new TypeMap(); s_AssemblyMap = new AssemblyMap(); s_ModuleMap = new ModuleMap();
        s_FieldMap = new FieldMap(); s_MethodMap = new MethodMap();
        s_PropertyMap = new PropertyMap(); s_EventMap = new EventMap(); s_ParametersMap = new ParametersMap();

        Il2CppReflectionType* first = Reflection::GetTypeObject(&s_baselineClass.byval_arg);
        Check(first->type == &s_activeClass.byval_arg, "Type cache contains a baseline type key");
        const size_t allocationsAfterType = s_allocations;
        Check(Reflection::GetTypeObject(&s_activeClass.byval_arg) == first && Reflection::GetTypeObject(&s_baselineClass.byval_arg) == first,
            "Baseline/active handles do not converge on one managed Type");
        Check(s_allocations == allocationsAfterType && s_typeResolves >= 3, "Cache hit skipped resolution or allocated another Type");
        Il2CppReflectionType* byref = Type::GetTypeFromHandle(reinterpret_cast<intptr_t>(&s_baselineClass.this_arg));
        Check(byref->type == &s_activeClass.this_arg && byref != first, "Type handle conversion lost its byref qualifier");
        Check(Reflection::GetTypeObject(&s_stableClass.byval_arg)->type == &s_stableClass.byval_arg, "Stable type changed");

        Il2CppReflectionAssembly* assembly = Reflection::GetAssemblyObject(&s_baselineAssembly);
        Check(assembly->assembly == &s_activeAssembly && assembly == Reflection::GetAssemblyObject(&s_activeAssembly), "Assembly cache keys were not resolved first");
        Il2CppReflectionModule* module = Reflection::GetModuleObject(&s_baselineImage);
        Check(module->image == &s_activeImage && module->assembly == assembly, "Module/assembly identity split");
        Check(module == Reflection::GetModuleObject(&s_activeImage) && s_moduleUses == 2, "Module cache/use hook did not resolve before key lookup");
        Il2CppReflectionAssembly oldAssemblyObject = {}; oldAssemblyObject.assembly = &s_baselineAssembly;
        Check(il2cpp::icalls::mscorlib::System::Reflection::RuntimeAssembly::GetManifestModuleInternal(reinterpret_cast<Il2CppObject*>(&oldAssemblyObject)) == reinterpret_cast<Il2CppObject*>(module),
            "Active ManifestModule did not use resolved native identity");
        oldAssemblyObject.assembly = &s_stableAssembly;
        Rejected([&] { il2cpp::icalls::mscorlib::System::Reflection::RuntimeAssembly::GetManifestModuleInternal(reinterpret_cast<Il2CppObject*>(&oldAssemblyObject)); }, "Nonshadow ManifestModule unsupported behavior changed");

        Il2CppObject existing = {}; existing.klass = &s_baselineClass;
        const size_t resolvesBeforeObject = s_typeResolves;
        Rejected([&] { il2cpp::icalls::mscorlib::System::Object::GetType(&existing); }, "Existing baseline object was relabeled active");
        Check(s_typeResolves == resolvesBeforeObject && existing.klass == &s_baselineClass, "Object guard ran after type remapping");
        existing.klass = &s_activeClass;
        Check(il2cpp::icalls::mscorlib::System::Object::GetType(&existing) == first, "Active object does not expose its cached Type");

        FieldInfo field = {}; field.parent = &s_activeClass; field.type = &s_stableClass.byval_arg; field.name = "Value";
        Il2CppReflectionField* reflectedField = Reflection::GetFieldObject(&s_activeClass, &field);
        Check(reflectedField == Reflection::GetFieldObject(&s_activeClass, &field), "Active field cache identity changed");
        field.parent = &s_baselineClass;
        Rejected([&] { Reflection::GetFieldObject(&s_activeClass, &field); }, "Field cache bypassed stale owner guard");
        field.parent = &s_activeClass; field.type = &s_baselineClass.byval_arg;
        Rejected([&] { Reflection::GetFieldObject(&s_activeClass, &field); }, "Field cache bypassed stale signature guard");
        field.type = &s_stableClass.byval_arg;
        Rejected([&] { Reflection::GetFieldObject(&s_baselineClass, &field); }, "Field reflected-owner guard missing");
        s_activeMethod.klass = &s_activeClass; s_activeMethod.name = "Invoke"; s_activeMethod.return_type = &s_stableClass.byval_arg;
        s_activeMethod.token = 900;
        s_baselineMethod.klass = &s_baselineClass; s_baselineMethod.name = "Invoke"; s_baselineMethod.return_type = &s_stableClass.byval_arg;
        s_baselineMethod.token = 19;
        Il2CppReflectionMethod* reflectedMethod = Reflection::GetMethodObject(&s_activeMethod, &s_activeClass);
        Check(reflectedMethod == Reflection::GetMethodObject(&s_activeMethod, &s_activeClass), "Active method cache identity changed");
        Check(Reflection::GetMethodObject(&s_baselineMethod, &s_baselineClass) == reflectedMethod && reflectedMethod->method == &s_activeMethod,
            "Baseline stack-frame method did not converge on active reflection identity");
        s_unmappedBaselineMethod.klass = &s_baselineClass; s_unmappedBaselineMethod.name = "Missing";
        s_unmappedBaselineMethod.return_type = &s_stableClass.byval_arg;
        Rejected([&] { Reflection::GetMethodObject(&s_unmappedBaselineMethod, &s_activeClass); }, "Unmapped baseline method owner guard missing");
        Rejected([&] { Reflection::GetParamObjects(&s_unmappedBaselineMethod, &s_activeClass); }, "Zero-parameter path bypassed owner guard");
        PropertyInfo property = {}; property.parent = &s_baselineClass;
        Rejected([&] { Reflection::GetPropertyObject(&s_activeClass, &property); }, "Property owner guard missing");
        EventInfo event = {}; event.parent = &s_baselineClass;
        Rejected([&] { Reflection::GetEventObject(&s_activeClass, &event); }, "Event owner guard missing");
        const int32_t invalid = static_cast<int32_t>(AssemblyShadowError::InvalidArgument);
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(nullptr, &output) == invalid && !output, "Null type query output was not initialized");
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(first, nullptr) == invalid, "Null query output was accepted");
        Il2CppReflectionType missingType = {};
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(&missingType, &output) == invalid, "Null native type was accepted");
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(first, &output) == 0 && output && s_lastString == "{\"fixtureQuery\":true}", "Query adapter changed native JSON/result");
        s_throwQuery = true; output = reinterpret_cast<Il2CppString*>(static_cast<uintptr_t>(1));
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(first, &output) == static_cast<int32_t>(AssemblyShadowError::InternalError) && !output, "Query exception boundary failed");
        s_throwQuery = false; s_throwString = true;
        Check(AssemblyShadowRuntimeApi::GetTypeResolutionInfo(first, &output) == static_cast<int32_t>(AssemblyShadowError::InternalError) && !output, "Query allocation exception boundary failed");
        Check(s_mutations == 0, "Query exception mutated transaction state");
        delete s_TypeMap; delete s_AssemblyMap; delete s_ModuleMap; delete s_FieldMap;
        delete s_MethodMap; delete s_PropertyMap; delete s_EventMap; delete s_ParametersMap;
#endif
        for (void* value : s_objects) std::free(value);
        std::cout << "m05_reflection_checks=" << s_checks << " feature=" << HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW << " PASS\n";
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
