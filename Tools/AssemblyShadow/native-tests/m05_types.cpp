// Focused actual-core checks, not Player acceptance. The production transaction
// core is included only to create its immutable registry/snapshot fixture. The
// TypeKey/resolver/serializer/TLS code is linked unchanged. Explicit adapters
// below model physical metadata tables and upstream class/generic interning;
// they never initialize a class, execute managed code, or reinterpret an object.
#include "vm/AssemblyShadow.cpp"
#include "vm/Class.h"
#include "vm/GlobalMetadata.h"
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <map>

#if !HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
int main()
{
    std::string json = "must-clear";
    if (il2cpp::vm::AssemblyShadow::GetTypeResolutionInfo(nullptr, json) != il2cpp::vm::AssemblyShadowError::FeatureDisabled || !json.empty()) return 1;
    std::puts("m05_disabled_checks=2 PASS");
    return 0;
}
#else
Il2CppDefaults il2cpp_defaults = {};
namespace {
using namespace il2cpp::vm;
size_t checks = 0, inflationCalls = 0, metadataReads = 0;
std::string exceptionMessage;
il2cpp::vm::AssemblyVector assemblies;
std::unordered_map<const Il2CppImage*, std::vector<Il2CppClass*>> imageTypes;
std::unordered_map<const Il2CppClass*, std::vector<Il2CppMetadataFieldInfo>> fields;
std::unordered_map<const Il2CppClass*, std::vector<uint32_t>> offsets;
std::unordered_map<const Il2CppClass*, std::vector<const Il2CppType*>> interfaces;
std::unordered_map<const Il2CppClass*, std::vector<const MethodInfo*>> methods;
std::unordered_map<std::string, Il2CppClass*> interned;
std::map<std::vector<const Il2CppType*>, const Il2CppGenericInst*> genericInstances;
void Check(bool condition, const char* detail)
{
    ++checks;
    if (!condition) throw std::runtime_error(detail);
}
void Failure(const std::function<void()>& action, AssemblyShadowError code, const char* label)
{
    bool failed = false;
    try { action(); }
    catch (const ShadowTypeResolutionFailure& error)
    { failed = error.error == code && std::string(error.what()).find(label) != std::string::npos; }
    Check(failed, label);
}
struct ImageFixture
{
    Il2CppAssembly assembly = {};
    Il2CppImage image = {};
    ImageFixture(const char* name, bool interpreter = false)
    {
        assembly.aname.name = name; assembly.aname.culture = ""; assembly.image = &image; assembly.token = 1;
        image.assembly = &assembly; image.name = image.nameNoExt = name;
        image.token = interpreter ? UINT32_C(1) << 31 : 0;
        assemblies.push_back(&assembly);
    }
    Il2CppClass* Type(const char* name, uint32_t arity = 0, Il2CppClass* parentDeclaration = nullptr, bool value = false, const char* ns = "Tests")
    {
        Il2CppClass* klass = new Il2CppClass();
        klass->image = &image; klass->name = name; klass->namespaze = ns; klass->declaringType = parentDeclaration;
        klass->typeMetadataHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(klass);
        klass->genericContainerHandle = reinterpret_cast<Il2CppMetadataGenericContainerHandle>(static_cast<uintptr_t>(arity));
        klass->byval_arg.type = value ? IL2CPP_TYPE_VALUETYPE : IL2CPP_TYPE_CLASS;
        klass->byval_arg.valuetype = value;
        klass->byval_arg.data.typeHandle = klass->typeMetadataHandle;
        klass->this_arg = klass->byval_arg; klass->this_arg.byref = true;
        klass->instance_size = 32; klass->native_size = -1;
        imageTypes[&image].push_back(klass); image.typeCount++;
        return klass;
    }
};
struct Parameter { Il2CppClass* owner; const MethodInfo* method; uint16_t num; };
Il2CppType ParameterType(Parameter* parameter, bool method = false)
{
    Il2CppType type = {};
    type.type = method ? IL2CPP_TYPE_MVAR : IL2CPP_TYPE_VAR;
    type.data.genericParameterHandle = reinterpret_cast<Il2CppMetadataGenericParameterHandle>(parameter);
    return type;
}
Il2CppClass* Generic(Il2CppClass* definition, std::initializer_list<const Il2CppType*> args)
{
    std::vector<const Il2CppType*> arguments(args);
    return MetadataCache::GetGenericInstanceType(definition, arguments.data(), static_cast<uint32_t>(arguments.size()));
}
const Il2CppAssembly* PrivateLookup(const char*, void* context) { return static_cast<Il2CppAssembly*>(context); }
void AddField(Il2CppClass* klass, const char* name, const Il2CppType* type, uint32_t offset,
    uint16_t attributes = FIELD_ATTRIBUTE_PRIVATE)
{
    Il2CppType* declared = new Il2CppType(*type); declared->attrs = attributes;
    Il2CppMetadataFieldInfo field = {}; field.name = name; field.type = declared;
    fields[klass].push_back(field); offsets[klass].push_back(offset); klass->field_count++;
}
void AddInterface(Il2CppClass* klass, const Il2CppType* type)
{
    interfaces[klass].push_back(type); klass->interfaces_count++;
}
MethodInfo* AddMethod(Il2CppClass* klass, const char* name, const Il2CppType* returnType,
    std::initializer_list<const Il2CppType*> parameterTypes, uint32_t token, uint32_t genericArity = 0)
{
    MethodInfo* method = new MethodInfo();
    method->klass = klass; method->name = name; method->return_type = returnType; method->token = token;
    method->flags = METHOD_ATTRIBUTE_PUBLIC; method->slot = kInvalidIl2CppMethodSlot;
    method->parameters_count = static_cast<uint8_t>(parameterTypes.size());
    if (method->parameters_count)
    {
        const Il2CppType** parameters = new const Il2CppType*[method->parameters_count];
        size_t index = 0;
        for (const Il2CppType* parameter : parameterTypes) parameters[index++] = parameter;
        method->parameters = parameters;
    }
    method->methodMetadataHandle = reinterpret_cast<Il2CppMetadataMethodDefinitionHandle>(method);
    if (genericArity)
    {
        method->is_generic = true;
        method->genericContainerHandle = reinterpret_cast<Il2CppMetadataGenericContainerHandle>(static_cast<uintptr_t>(genericArity));
    }
    methods[klass].push_back(method); klass->method_count++;
    return method;
}
}

namespace il2cpp { namespace vm {
#if !defined(ASSEMBLY_SHADOW_M06_RAW_METADATA_FIXTURE)
// M05 uses class-shaped synthetic handles, not raw TypeDef rows. Keep the new
// execution-diagnostics-only dependencies explicit and fail closed if reached.
// The M06 fixture supplies its own actual raw-row adapters instead.
baselib::ReentrantLock g_MetadataLock;
std::pair<const char*, const char*> GlobalMetadata::GetTypeNamespaceAndName(Il2CppMetadataTypeHandle)
{ throw std::runtime_error("M05 fixture does not model raw execution TypeDefs"); }
Il2CppMetadataGenericContainerHandle GlobalMetadata::GetGenericContainerFromIndex(GenericContainerIndex)
{ throw std::runtime_error("M05 fixture does not model raw execution generic containers"); }
uint32_t GlobalMetadata::GetGenericContainerCount(Il2CppMetadataGenericContainerHandle)
{ throw std::runtime_error("M05 fixture does not model raw execution generic containers"); }
const Il2CppType* GlobalMetadata::GetIl2CppTypeFromIndex(TypeIndex)
{ throw std::runtime_error("M05 fixture does not model raw execution type indices"); }
#endif
const Il2CppAssembly* MetadataCache::GetAotAssemblyByNamePhysical(const char* name)
{
    for (auto assembly : assemblies)
        if (!hybridclr::metadata::IsInterpreterImage(assembly->image) &&
            assembly_shadow_detail::NameEquals(assembly_shadow_detail::ViewName(name), assembly_shadow_detail::ViewName(assembly->aname.name))) return assembly;
    return nullptr;
}
Il2CppClass* MetadataCache::GetTypeInfoFromHandle(Il2CppMetadataTypeHandle handle)
{ ++metadataReads; return reinterpret_cast<Il2CppClass*>(const_cast<void*>(reinterpret_cast<const void*>(handle))); }
Il2CppMetadataTypeHandle MetadataCache::GetAssemblyTypeHandle(const Il2CppImage* image, AssemblyTypeIndex index)
{ return imageTypes.at(image).at(index)->typeMetadataHandle; }
std::pair<const char*, const char*> MetadataCache::GetTypeNamespaceAndName(Il2CppMetadataTypeHandle handle)
{ auto klass = GetTypeInfoFromHandle(handle); return {klass->namespaze, klass->name}; }
bool MetadataCache::TypeIsNested(Il2CppMetadataTypeHandle handle) { return GetTypeInfoFromHandle(handle)->declaringType != nullptr; }
Il2CppMetadataTypeHandle MetadataCache::GetNestedTypes(Il2CppMetadataTypeHandle handle, void** iterator)
{
    Il2CppClass* owner = GetTypeInfoFromHandle(handle);
    auto& types = imageTypes.at(owner->image);
    size_t at = reinterpret_cast<uintptr_t>(*iterator);
    while (at < types.size())
    {
        Il2CppClass* candidate = types[at++];
        *iterator = reinterpret_cast<void*>(at);
        if (candidate->declaringType == owner) return candidate->typeMetadataHandle;
    }
    return nullptr;
}
uint32_t MetadataCache::GetGenericContainerCount(Il2CppMetadataGenericContainerHandle handle) { return static_cast<uint32_t>(reinterpret_cast<uintptr_t>(handle)); }
Il2CppClass* MetadataCache::GetParameterDeclaringType(Il2CppMetadataGenericParameterHandle handle) { return reinterpret_cast<const Parameter*>(handle)->owner; }
const MethodInfo* MetadataCache::GetParameterDeclaringMethod(Il2CppMetadataGenericParameterHandle handle) { return reinterpret_cast<const Parameter*>(handle)->method; }
Il2CppGenericParameterInfo MetadataCache::GetGenericParameterInfo(Il2CppMetadataGenericParameterHandle handle)
{ Il2CppGenericParameterInfo info = {}; info.num = reinterpret_cast<const Parameter*>(handle)->num; return info; }
Il2CppMetadataFieldInfo MetadataCache::GetFieldInfo(const Il2CppClass* klass, TypeFieldIndex index) { return fields.at(klass).at(index); }
const Il2CppType* MetadataCache::GetInterfaceFromOffset(const Il2CppClass* klass, TypeInterfaceIndex index)
{ return interfaces.at(klass).at(index); }
Il2CppMetadataMethodInfo MetadataCache::GetMethodInfo(const Il2CppClass* klass, TypeMethodIndex index)
{
    const MethodInfo* method = methods.at(klass).at(index);
    return {method->methodMetadataHandle, method->name, method->return_type, method->token,
        method->flags, method->iflags, method->slot, method->parameters_count};
}
const MethodInfo* MetadataCache::GetMethodInfoFromMethodHandle(Il2CppMetadataMethodDefinitionHandle handle)
{ return reinterpret_cast<const MethodInfo*>(handle); }
uint32_t GlobalMetadata::GetFieldOffset(const Il2CppClass* klass, int32_t index, FieldInfo*) { return offsets.at(klass).at(index); }
const Il2CppGenericInst* MetadataCache::GetGenericInst(const Il2CppType* const* types, uint32_t count)
{
    if (count && !types) throw std::runtime_error("Missing generic arguments");
    std::vector<const Il2CppType*> key(types, types + count);
    auto found = genericInstances.find(key);
    if (found != genericInstances.end()) return found->second;
    Il2CppGenericInst* instance = new Il2CppGenericInst();
    instance->type_argc = count;
    if (count)
    {
        const Il2CppType** arguments = new const Il2CppType*[count];
        for (uint32_t index = 0; index < count; ++index) arguments[index] = types[index];
        instance->type_argv = arguments;
    }
    genericInstances.emplace(std::move(key), instance);
    return instance;
}
Il2CppClass* MetadataCache::GetGenericInstanceType(Il2CppClass* definition, const Il2CppType** arguments, uint32_t count)
{
    std::string key = std::to_string(reinterpret_cast<uintptr_t>(definition));
    for (uint32_t i = 0; i < count; ++i) key += ":" + std::to_string(reinterpret_cast<uintptr_t>(arguments[i]));
    auto found = interned.find(key);
    if (found != interned.end()) return found->second;
    ++inflationCalls;
    auto klass = new Il2CppClass(); auto generic = new Il2CppGenericClass(); auto inst = new Il2CppGenericInst();
    auto args = new const Il2CppType*[count];
    for (uint32_t i = 0; i < count; ++i) args[i] = arguments[i];
    inst->type_argc = count; inst->type_argv = args;
    generic->type = &definition->byval_arg; generic->context.class_inst = inst; generic->cached_class = klass;
    klass->image = definition->image; klass->name = definition->name; klass->namespaze = definition->namespaze;
    klass->generic_class = generic; klass->byval_arg.type = IL2CPP_TYPE_GENERICINST;
    klass->byval_arg.valuetype = definition->byval_arg.valuetype; klass->byval_arg.data.generic_class = generic;
    klass->this_arg = klass->byval_arg; klass->this_arg.byref = true;
    klass->instance_size = 40; klass->native_size = -1;
    interned.emplace(key, klass); return klass;
}
Il2CppClass* Class::FromIl2CppTypeEnum(Il2CppTypeEnum type)
{
    if (type == IL2CPP_TYPE_I4) return il2cpp_defaults.int32_class;
    if (type == IL2CPP_TYPE_STRING) return il2cpp_defaults.string_class;
    if (type == IL2CPP_TYPE_VOID) return il2cpp_defaults.void_class;
    return nullptr;
}
Il2CppClass* Class::FromIl2CppType(const Il2CppType* type, bool)
{
    if (type->type == IL2CPP_TYPE_GENERICINST) return type->data.generic_class->cached_class;
    if (type->type == IL2CPP_TYPE_SZARRAY) return GetArrayClass(FromIl2CppType(type->data.type), 1);
    if (type->type == IL2CPP_TYPE_ARRAY) return GetBoundedArrayClass(FromIl2CppType(type->data.array->etype), type->data.array->rank, true);
    if (type->type == IL2CPP_TYPE_PTR) return GetPtrClass(type->data.type);
    if (type->type == IL2CPP_TYPE_CLASS || type->type == IL2CPP_TYPE_VALUETYPE) return MetadataCache::GetTypeInfoFromHandle(type->data.typeHandle);
    return FromIl2CppTypeEnum(static_cast<Il2CppTypeEnum>(type->type));
}
Il2CppClass* Class::GetArrayClass(Il2CppClass* element, uint32_t rank) { return GetBoundedArrayClass(element, rank, false); }
Il2CppClass* Class::GetBoundedArrayClass(Il2CppClass* element, uint32_t rank, bool bounded)
{
    std::string key = std::string(bounded ? "bounded:" : "array:") + std::to_string(reinterpret_cast<uintptr_t>(element)) + ":" + std::to_string(rank);
    auto found = interned.find(key); if (found != interned.end()) return found->second;
    auto klass = new Il2CppClass(); klass->image = element->image; klass->element_class = element; klass->rank = rank;
    klass->instance_size = 32; klass->native_size = -1;
    klass->byval_arg.type = bounded ? IL2CPP_TYPE_ARRAY : IL2CPP_TYPE_SZARRAY;
    if (bounded) { auto array = new Il2CppArrayType(); array->rank = rank; array->etype = &element->byval_arg; klass->byval_arg.data.array = array; }
    else klass->byval_arg.data.type = &element->byval_arg;
    klass->this_arg = klass->byval_arg; klass->this_arg.byref = true;
    interned.emplace(key, klass); return klass;
}
Il2CppClass* Class::GetPtrClass(const Il2CppType* element)
{
    std::string key = "ptr:" + std::to_string(reinterpret_cast<uintptr_t>(element));
    auto found = interned.find(key); if (found != interned.end()) return found->second;
    auto klass = new Il2CppClass(); klass->image = FromIl2CppType(element)->image;
    klass->byval_arg.type = IL2CPP_TYPE_PTR; klass->byval_arg.data.type = element;
    klass->this_arg = klass->byval_arg; klass->this_arg.byref = true;
    interned.emplace(key, klass); return klass;
}
void Class::Init(Il2CppClass*) { throw std::runtime_error("FORBIDDEN baseline Init in raw safety comparison"); }
void Class::SetupFields(Il2CppClass*) { throw std::runtime_error("FORBIDDEN baseline SetupFields in raw safety comparison"); }
Il2CppException* Exception::GetInvalidOperationException(const char* detail) { exceptionMessage = detail; return reinterpret_cast<Il2CppException*>(1); }
void Exception::Raise(Il2CppException*, MethodInfo*) { throw std::runtime_error(exceptionMessage); }
uint64_t Assembly::CaptureShadowEnumeration(AssemblyVector& result) { result = assemblies; return AssemblyShadow::ActiveGeneration(); }
void AssemblyShadowVisibility::CollectOrdinaryClasses(std::vector<Il2CppClass*>&, uint64_t& generation) { generation = AssemblyShadow::ActiveGeneration(); }
bool AssemblyShadowVisibility::ClassUsesStagedMetadata(const Il2CppClass*) { return false; }
}}

namespace il2cpp { namespace metadata {
const MethodInfo* GenericMethod::GetMethod(const MethodInfo* definition, const Il2CppGenericInst* classInst,
    const Il2CppGenericInst* methodInst)
{
    Il2CppGenericMethod* generic = new Il2CppGenericMethod();
    generic->methodDefinition = definition; generic->context.class_inst = classInst; generic->context.method_inst = methodInst;
    MethodInfo* method = new MethodInfo(*definition);
    method->is_inflated = true; method->is_generic = methodInst == nullptr && definition->is_generic;
    method->genericMethod = generic;
    if (classInst)
        method->klass = il2cpp::vm::MetadataCache::GetGenericInstanceType(definition->klass,
            classInst->type_argv, classInst->type_argc);
    return method;
}
}}

int main(int argc, char** argv)
{
    using namespace il2cpp::vm;
    try
    {
        ImageFixture baseline("Tests.Business"), active("TESTS.BUSINESS", true), stable("mscorlib"), unchanged("Tests.Unchanged");
        auto object = stable.Type("Object", 0, nullptr, false, "System");
        il2cpp_defaults.object_class = object;
        il2cpp_defaults.int32_class = stable.Type("Int32", 0, nullptr, true, "System");
        il2cpp_defaults.string_class = stable.Type("String", 0, nullptr, false, "System");
        il2cpp_defaults.void_class = stable.Type("Void", 0, nullptr, true, "System");
        Il2CppType int32Field = {}; int32Field.type = IL2CPP_TYPE_I4;
        auto oldDto = baseline.Type("Dto"), newDto = active.Type("Dto");
        auto oldGeneric = baseline.Type("Box`1", 1), newGeneric = active.Type("Box`1", 1);
        auto oldOuter = baseline.Type("Outer`1", 1), newOuter = active.Type("Outer`1", 1);
        auto oldNested = baseline.Type("Nested`1", 2, oldOuter), newNested = active.Type("Nested`1", 2, newOuter);
        auto caseType = baseline.Type("dto");
        auto missing = baseline.Type("Removed");
        auto oldKind = baseline.Type("Kind"), newKind = active.Type("Kind", 0, nullptr, true);
        auto oldArity = baseline.Type("Arity`1", 1); active.Type("Arity`1", 2);
        auto newAdded = active.Type("Added");
        auto oldNativeReference = baseline.Type("NativeReference"), newNativeReference = active.Type("NativeReference");
        oldNativeReference->native_size = sizeof(void*);
        auto oldNativeValue = baseline.Type("NativeValue", 0, nullptr, true), newNativeValue = active.Type("NativeValue", 0, nullptr, true);
        oldNativeValue->native_size = sizeof(int32_t); newNativeValue->native_size = sizeof(int64_t);
        auto oldBad = baseline.Type("BadLayout"), newBad = active.Type("BadLayout");
        newBad->instance_size = 40;
        auto oldField = baseline.Type("BadField"), newField = active.Type("BadField");
        AddField(oldField, "Value", &il2cpp_defaults.int32_class->byval_arg, 16);
        AddField(newField, "Value", &il2cpp_defaults.int32_class->byval_arg, 16);
        AddField(newField, "ExtraSerializedField", &il2cpp_defaults.int32_class->byval_arg, 20);
        auto oldNonSerialized = baseline.Type("NonSerializedGrowth"), newNonSerialized = active.Type("NonSerializedGrowth");
        newNonSerialized->instance_size = 40;
        AddField(newNonSerialized, "runtimeOnly", &int32Field, 32,
            FIELD_ATTRIBUTE_PRIVATE | FIELD_ATTRIBUTE_NOT_SERIALIZED);
        baseline.Type("SerializedPrivateGrowth"); auto newSerializedPrivate = active.Type("SerializedPrivateGrowth");
        newSerializedPrivate->instance_size = 40;
        AddField(newSerializedPrivate, "resourceValue", &int32Field, 32, FIELD_ATTRIBUTE_PRIVATE);
        auto oldPublicNonSerialized = baseline.Type("PublicNonSerializedGrowth"), newPublicNonSerialized = active.Type("PublicNonSerializedGrowth");
        newPublicNonSerialized->instance_size = 40;
        AddField(newPublicNonSerialized, "runtimeOnly", &int32Field, 32,
            FIELD_ATTRIBUTE_PUBLIC | FIELD_ATTRIBUTE_NOT_SERIALIZED);
        auto oldReferenceNonSerialized = baseline.Type("ReferenceNonSerializedGrowth"), newReferenceNonSerialized = active.Type("ReferenceNonSerializedGrowth");
        newReferenceNonSerialized->instance_size = 40;
        AddField(newReferenceNonSerialized, "runtimeOnly", &il2cpp_defaults.string_class->byval_arg, 32,
            FIELD_ATTRIBUTE_PRIVATE | FIELD_ATTRIBUTE_NOT_SERIALIZED);
        auto contract = stable.Type("IContract", 0, nullptr, false, "Tests"); contract->flags |= TYPE_ATTRIBUTE_INTERFACE;
        auto oldInterfaceChange = baseline.Type("InterfaceChange"), newInterfaceChange = active.Type("InterfaceChange");
        AddInterface(newInterfaceChange, &contract->byval_arg);
        auto list = stable.Type("List`1", 1, nullptr, false, "System.Collections.Generic");
        auto dictionary = stable.Type("Dictionary`2", 2, nullptr, false, "System.Collections.Generic");
        auto untouched = unchanged.Type("Stable");
        auto oldAmbiguous = baseline.Type("Ambiguous"), newAmbiguous = active.Type("Ambiguous");
        MethodInfo* oldRun = AddMethod(oldDto, "Run", &il2cpp_defaults.int32_class->byval_arg,
            {&oldDto->byval_arg}, 0x06000019);
        MethodInfo* newRun = AddMethod(newDto, "Run", &il2cpp_defaults.int32_class->byval_arg,
            {&newDto->byval_arg}, 0x06000384);
        MethodInfo* oldRemovedMethod = AddMethod(oldDto, "Removed", &il2cpp_defaults.void_class->byval_arg, {}, 0x06000020);
        MethodInfo* oldAmbiguousMethod = AddMethod(oldAmbiguous, "Duplicate", &il2cpp_defaults.void_class->byval_arg, {}, 0x06000021);
        AddMethod(newAmbiguous, "Duplicate", &il2cpp_defaults.void_class->byval_arg, {}, 0x06000400);
        AddMethod(newAmbiguous, "Duplicate", &il2cpp_defaults.void_class->byval_arg, {}, 0x06000401);
        MethodInfo* oldGenericMethod = AddMethod(oldGeneric, "GenericWork", &il2cpp_defaults.int32_class->byval_arg,
            {}, 0x06000022, 1);
        MethodInfo* newGenericMethod = AddMethod(newGeneric, "GenericWork", &il2cpp_defaults.int32_class->byval_arg,
            {}, 0x06000402, 1);
        Check(AssemblyShadowTypeKey::Make(oldDto) == AssemblyShadowTypeKey::Make(newDto), "stable key ignores physical identity and assembly case");
        baseline.assembly.aname.major = 97; active.assembly.aname.major = 1; oldDto->token = 19; newDto->token = 900;
        Check(AssemblyShadowTypeKey::Make(oldDto) == AssemblyShadowTypeKey::Make(newDto), "stable key ignores token/version");
        Check(!(AssemblyShadowTypeKey::Make(oldDto) == AssemblyShadowTypeKey::Make(caseType)), "type name remains case sensitive");
        Check(AssemblyShadowTypeKey::Make(oldNested) == AssemblyShadowTypeKey::Make(newNested), "full nesting and metadata arity");
        Check(AssemblyShadowTypeKey::Make(oldNested).ToString().find("@2") != std::string::npos, "nested arity comes from metadata not backtick");
        auto outerA = baseline.Type("Outer", 0, nullptr, false, "A"), outerB = baseline.Type("Outer", 0, nullptr, false, "B");
        auto innerA = baseline.Type("Inner", 0, outerA, false, ""), innerB = baseline.Type("Inner", 0, outerB, false, "");
        Check(!(AssemblyShadowTypeKey::Make(innerA) == AssemblyShadowTypeKey::Make(innerB)), "empty nested namespace retains distinct outer declaration namespaces");
        Check(AssemblyShadow::ConfigureCandidates("fixture", {"Tests.Business", "Tests.Unchanged"}, {"mscorlib"}) == AssemblyShadowError::Success, "real candidate registry");
        Check(AssemblyShadow::ResolveType(&oldDto->byval_arg) == &oldDto->byval_arg, "precommit no remap");
        std::vector<hybridclr::metadata::StagedAssembly*> privateImages;
        {
            hybridclr::metadata::ScopedStagingResolver scope(privateImages, PrivateLookup, &active.assembly);
            AssemblyShadow::RequireActiveClass(newDto, BaselineUseKind::ClassInit, "private-real-identity");
            Check(!s_candidates.load()->byAssembly.at(&baseline.assembly)->firstUse.present, "private interpreter identity never records baseline use");
            AssemblyShadow::RequireActiveClass(untouched, BaselineUseKind::ClassInit, "staging-stable-aot");
            Check(s_candidates.load()->byAssembly.at(&unchanged.assembly)->firstUse.present, "TLS does not hide AOT baseline class use");
        }
        ActiveSnapshot snapshot;
        snapshot.byName.Add("Tests.Business", &active.assembly);
        snapshot.byAssembly.emplace(&baseline.assembly, &active.assembly);
        snapshot.byImage.emplace(&baseline.image, &active.image);
        snapshot.shadowToBaseline.emplace(&active.assembly, &baseline.assembly);
        s_active.store(&snapshot); s_state.store(AssemblyShadowState::Committing);
        Check(AssemblyShadow::ResolveClassDefinition(oldDto) == newDto, "lazy definition remap");
        Check(AssemblyShadow::ResolveClassDefinition(oldDto) == newDto, "definition cache hit");
        Check(AssemblyShadow::ResolveClassDefinition(oldNested) == newNested, "nested remap");
        Check(AssemblyShadow::ResolveReflectionMethod(oldRun) == newRun, "reflection method remaps by structural signature");
        Check(AssemblyShadow::ResolveReflectionMethod(oldRun) == newRun, "reflection method remap cache stable");
        Check(AssemblyShadow::ResolveReflectionMethod(newRun) == newRun, "active reflection method identity preserved");
        Check(oldRun->token != newRun->token, "reflection method proof uses shifted tokens");
        Failure([&] { AssemblyShadowTypeResolver::ResolveReflectionMethod(oldRemovedMethod); },
            AssemblyShadowError::ReferenceResolutionFailed, "ShadowMethodNotFound");
        Failure([&] { AssemblyShadowTypeResolver::ResolveReflectionMethod(oldAmbiguousMethod); },
            AssemblyShadowError::ReferenceResolutionFailed, "ShadowAmbiguousMethodDefinition");
        const Il2CppType* oldArguments[] = {&oldDto->byval_arg};
        Il2CppGenericInst oldInstance = {1, oldArguments};
        Il2CppGenericMethod oldInflation = {}; oldInflation.methodDefinition = oldGenericMethod;
        oldInflation.context.class_inst = &oldInstance; oldInflation.context.method_inst = &oldInstance;
        MethodInfo oldInflated = *oldGenericMethod; oldInflated.klass = Generic(oldGeneric, {&oldDto->byval_arg});
        oldInflated.is_generic = false; oldInflated.is_inflated = true; oldInflated.genericMethod = &oldInflation;
        const MethodInfo* newInflated = AssemblyShadowTypeResolver::ResolveReflectionMethod(&oldInflated);
        Check(newInflated->genericMethod->methodDefinition == newGenericMethod &&
            newInflated->genericMethod->context.class_inst->type_argv[0] == &newDto->byval_arg &&
            newInflated->genericMethod->context.method_inst->type_argv[0] == &newDto->byval_arg,
            "inflated reflection method rebuilds active generic contexts");
        Check(newInflated->klass == Generic(newGeneric, {&newDto->byval_arg}), "inflated reflection declaring class is active");
        Check(AssemblyShadow::ResolveType(&newDto->byval_arg) == &newDto->byval_arg, "active identity preserved");
        Check(AssemblyShadow::ResolveType(&untouched->byval_arg) == &untouched->byval_arg, "unchanged candidate fast path");
        Failure([&] { AssemblyShadowTypeResolver::ResolveDefinition(missing); }, AssemblyShadowError::ReferenceResolutionFailed, "ShadowTypeNotFound");
        Failure([&] { AssemblyShadowTypeResolver::ResolveDefinition(oldArity); }, AssemblyShadowError::ReferenceResolutionFailed, "ShadowGenericArityMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveDefinition(oldKind); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowTypeKindMismatch");
        auto oldList = Generic(list, {&oldDto->byval_arg}); auto newList = Generic(list, {&newDto->byval_arg});
        Check(AssemblyShadow::ResolveClass(oldList) == newList, "AOT List shadow argument rebuilt");
        Check(AssemblyShadow::ResolveType(&newList->byval_arg) == &newList->byval_arg, "unchanged active generic exact pointer");
        auto oldDict = Generic(dictionary, {&il2cpp_defaults.string_class->byval_arg, &oldDto->byval_arg});
        auto newDict = Generic(dictionary, {&il2cpp_defaults.string_class->byval_arg, &newDto->byval_arg});
        Check(AssemblyShadow::ResolveClass(oldDict) == newDict, "AOT Dictionary string shadow value rebuilt");
        auto oldBoxInt = Generic(oldGeneric, {&il2cpp_defaults.int32_class->byval_arg});
        auto newBoxInt = Generic(newGeneric, {&il2cpp_defaults.int32_class->byval_arg});
        Check(AssemblyShadow::ResolveClass(oldBoxInt) == newBoxInt, "shadow generic definition int rebuilt");
        auto oldBoxDto = Generic(oldGeneric, {&oldDto->byval_arg}); auto newBoxDto = Generic(newGeneric, {&newDto->byval_arg});
        Check(AssemblyShadow::ResolveClass(oldBoxDto) == newBoxDto, "shadow generic definition and argument rebuilt");
        auto malformed = Generic(oldGeneric, {&oldDto->byval_arg, &oldDto->byval_arg});
        Failure([&] { AssemblyShadowTypeResolver::Resolve(&malformed->byval_arg); }, AssemblyShadowError::ReferenceResolutionFailed, "ShadowGenericArityMismatch");
        Il2CppType qualified = oldDto->byval_arg; qualified.byref = true; qualified.pinned = true; qualified.attrs = 17; qualified.num_mods = 2;
        auto mappedQualified = AssemblyShadow::ResolveType(&qualified);
        Check(mappedQualified->byref && mappedQualified->pinned && mappedQualified->attrs == 17 && mappedQualified->num_mods == 2, "represented qualifiers preserved");
        Check(AssemblyShadow::ResolveType(&qualified) == mappedQualified, "qualified composite intern stable");
        Check(AssemblyShadow::ResolveType(mappedQualified) == mappedQualified, "active qualifiers exact pointer");
        Check(AssemblyShadow::ResolveType(&oldDto->this_arg) == &newDto->this_arg, "byref canonical active pointer");
        auto oldArray = Class::GetArrayClass(oldDto, 1), newArray = Class::GetArrayClass(newDto, 1);
        Check(AssemblyShadow::ResolveClass(oldArray) == newArray, "SZ array rebuilt");
        auto oldPtr = Class::GetPtrClass(&oldDto->byval_arg), newPtr = Class::GetPtrClass(&newDto->byval_arg);
        Check(AssemblyShadow::ResolveClass(oldPtr) == newPtr, "pointer rebuilt");
        int sizes[] = {4, 5}, bounds[] = {-2, 3};
        Il2CppArrayType array = {}; array.etype = &oldDto->byval_arg; array.rank = 2; array.numsizes = 2; array.numlobounds = 2; array.sizes = sizes; array.lobounds = bounds;
        Il2CppType multi = {}; multi.type = IL2CPP_TYPE_ARRAY; multi.data.array = &array;
        auto mappedMulti = AssemblyShadow::ResolveType(&multi);
        Check(mappedMulti->data.array->etype == &newDto->byval_arg && mappedMulti->data.array->rank == 2 && mappedMulti->data.array->sizes[1] == 5 && mappedMulti->data.array->lobounds[0] == -2, "array rank sizes lowerbounds preserved");
        Check(mappedMulti->data.array->sizes != sizes && mappedMulti->data.array->lobounds != bounds, "rebuilt array descriptor owns bounds");
        Check(AssemblyShadow::ResolveType(&multi) == mappedMulti, "bounded array repeated pointer stable");
        Parameter var{oldGeneric, nullptr, 0}; auto varType = ParameterType(&var);
        Check(AssemblyShadow::ResolveType(&varType) == &varType, "generic parameter context preserved");
        MethodInfo method = {}; method.klass = oldGeneric; method.name = "Method"; method.genericContainerHandle = reinterpret_cast<Il2CppMetadataGenericContainerHandle>(1);
        Parameter mvar{oldGeneric, &method, 0}; auto mvarType = ParameterType(&mvar, true);
        Il2CppType mvarArray = {}; mvarArray.type = IL2CPP_TYPE_SZARRAY; mvarArray.data.type = &mvarType;
        const Il2CppType* parameters[] = {&mvarArray}; method.parameters = parameters; method.parameters_count = 1; method.return_type = &mvarType;
        Check(AssemblyShadowTypeKey::Format(&mvarType).find("szarray(!!0)") != std::string::npos, "nested MVAR signature avoids owner recursion");
        Check(AssemblyShadow::ResolveType(&mvarType) == &mvarType, "method generic parameter context preserved");
        std::string info;
        Check(AssemblyShadow::GetTypeResolutionInfo(nullptr, info) == AssemblyShadowError::InvalidArgument && info.empty(), "ON null query invalid without JSON");
        auto beforeState = s_state.load();
        Check(AssemblyShadow::GetTypeResolutionInfo(&missing->byval_arg, info) == AssemblyShadowError::ReferenceResolutionFailed && info.empty() && s_state.load() == beforeState && !s_typeFailure.load(), "query failure is observational");
        Check(AssemblyShadow::GetTypeResolutionInfo(&oldList->byval_arg, info) == AssemblyShadowError::Success, "type info baseline composite query");
        Check(info.find("\"isActive\":false") != std::string::npos && info.find("\"containsShadowTypes\":true") != std::string::npos && info.find("\"executionMode\":\"AotBaseline\"") != std::string::npos, "physical root mode differs from component shadow containment");
        std::printf("m05_type_info=%s\n", info.c_str());
        Check(AssemblyShadow::GetTypeResolutionInfo(&newDto->byval_arg, info) == AssemblyShadowError::Success && info.find("\"isActive\":true") != std::string::npos, "active query");
        std::printf("m05_active_type_info=%s\n", info.c_str());
        Check(AssemblyShadow::GetTypeResolutionInfo(&newAdded->byval_arg, info) == AssemblyShadowError::Success && info.find("\"baselinePointerAvailable\":false") != std::string::npos, "new type does not fabricate baseline pointer");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(oldNativeReference, "reference-native-size") == newNativeReference,
            "reference marshaling native size is not managed allocation layout");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(oldNativeValue, "value-native-size"); },
            AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutMismatch");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(oldDto, "old-allocation") == newDto, "compatible baseline allocation remap");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newDto, "active-allocation") == newDto, "compatible active allocation raw counterpart proof");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newAdded, "added-allocation") == newAdded, "patch-added type legal");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newNonSerialized, "nonserialized-growth") == newNonSerialized,
            "private appended nonserialized primitive storage is legal for post-commit allocation");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newSerializedPrivate, "serialized-private-growth") == newSerializedPrivate,
            "private appended serialized primitive storage is physically legal after resource authorization");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newPublicNonSerialized, "public-nonserialized-growth"); },
            AssemblyShadowError::ResourceAbiMismatch, "ShadowFieldLayoutMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newReferenceNonSerialized, "reference-nonserialized-growth"); },
            AssemblyShadowError::ResourceAbiMismatch, "ShadowFieldLayoutMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newInterfaceChange, "interface-change"); },
            AssemblyShadowError::ResourceAbiMismatch, "ShadowInterfaceLayoutMismatch");
        size_t beforeInflation = inflationCalls;
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newBoxDto, "active-generic") == newBoxDto && inflationCalls == beforeInflation, "active generic contract avoids old baseline inflation");
        Check(AssemblyShadowTypeResolver::ResolveAllocation(newList, "active-aot-generic") == newList, "active List argument contract legal");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(oldBoxInt, "unknown-old-generic"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutUnavailable");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newKind, "active-kind"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowTypeKindMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newBad, "active-first-layout"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newField, "active-first-fields"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowFieldLayoutMismatch");
        auto badList = Generic(list, {&newBad->byval_arg});
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(badList, "nested-list-layout"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutMismatch");
        auto badArray = Class::GetArrayClass(newBad, 1), badPtr = Class::GetPtrClass(&newBad->byval_arg);
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(badArray, "nested-array-layout"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutMismatch");
        Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(badPtr, "nested-pointer-layout"); }, AssemblyShadowError::ResourceAbiMismatch, "ShadowLayoutMismatch");
        {
            AssemblyShadowTypeMetadataScope scope;
            Failure([&] { AssemblyShadowTypeResolver::ResolveAllocation(newDto, "adversarial-metadata-allocation"); }, AssemblyShadowError::BaselineAlreadyUsed, "ShadowAllocationDuringMetadataResolution");
        }
        Check(!AssemblyShadow::IsResolvingTypeMetadata(), "RAII metadata scope unwinds");
        // Separate process modes exercise first-failure sealing independently;
        // there is deliberately no production reset/retry path for the cache.
        const std::string mode = argc > 1 ? argv[1] : "layout";
        bool guarded = false;
        try
        {
            if (mode == "metadata")
            {
                AssemblyShadowTypeMetadataScope scope;
                AssemblyShadow::RequireActiveClass(oldList, BaselineUseKind::ClassInit, "adversarial-metadata-init");
            }
            else if (mode == "staging")
            {
                hybridclr::metadata::ScopedStagingResolver scope(privateImages, PrivateLookup, &active.assembly);
                AssemblyShadow::RequireActiveClass(oldDto, BaselineUseKind::ClassInit, "adversarial-staging-init");
            }
            else if (mode == "reference")
                AssemblyShadow::ResolveReferencedAssembly(&unchanged.assembly, &baseline.assembly, "Tests.Business", 7, "reference-first");
            else AssemblyShadow::ResolveAllocationClass(newField, "active-first-runtime-guard");
        }
        catch (const std::runtime_error&) { guarded = true; }
        Check(guarded && s_state.load() == AssemblyShadowState::FailedAfterCommit, "unsafe use seals during initializers");
        std::string diagnostic; AssemblyShadow::GetDiagnosticsJson(diagnostic);
        const std::string first = s_typeFailure.load()->detail;
        Check(diagnostic.find(first) != std::string::npos, "first type failure remains inspectable");
        Check(mode == "reference" ? diagnostic.find("\"lastError\":14") != std::string::npos : mode == "layout" ? diagnostic.find("\"lastError\":16") != std::string::npos :
            diagnostic.find("\"lastError\":15") != std::string::npos && diagnostic.find("FirstUseSequence=") != std::string::npos,
            "existing schema carries precise code and first-use sequence");
        try { AssemblyShadow::ResolveClassDefinition(missing); } catch (const std::runtime_error&) {}
        try { AssemblyShadow::ResolveReferencedAssembly(&unchanged.assembly, &baseline.assembly, "Tests.Business", 8, "later-reference"); } catch (const std::runtime_error&) {}
        std::string after; AssemblyShadow::GetDiagnosticsJson(after);
        Check(after.find(first) != std::string::npos, "type and reference guards share immutable first-failure diagnosis");
        Check(s_typeFailure.load()->detail == first && s_state.load() == AssemblyShadowState::FailedAfterCommit, "subsequent failure cannot overwrite first failure or unseal");
        Check(!oldDto->initialized && !newDto->initialized, "no initialization or baseline object reinterpretation");
        std::printf("m05_guard_diagnostics=%s\n", diagnostic.c_str());
        std::printf("m05_type_checks=%zu mode=%s metadata_reads=%zu inflation_calls=%zu PASS\n", checks, mode.c_str(), metadataReads, inflationCalls);
        return 0;
    }
    catch (const std::exception& error) { std::fprintf(stderr, "FAIL: %s\n", error.what()); return 1; }
}
#endif
