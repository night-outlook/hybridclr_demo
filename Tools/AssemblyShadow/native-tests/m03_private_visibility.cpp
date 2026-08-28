// Actual visibility predicates over synthetic native metadata, NOT a Unity/IL2CPP
// transaction or public-enumeration test. Only the two active-snapshot queries
// are substituted; private-image registration and recursive inspection are real.
#include "vm/AssemblyShadow.h"
#include "vm/AssemblyShadowVisibility.h"
#include "vm/GlobalMetadataFileInternals.h"
#include "il2cpp-class-internals.h"
#include "hybridclr/metadata/MetadataUtil.h"

#include <atomic>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using il2cpp::vm::AssemblyShadowVisibility;
using hybridclr::metadata::EncodeImageAndMetadataIndex;

struct SimulatedActiveSnapshot
{
    uint64_t generation;
    const Il2CppAssembly* assemblies[4];
};

std::atomic<const SimulatedActiveSnapshot*> s_simulatedActive{ nullptr };
size_t s_checks = 0;

void Require(bool condition, const char* detail)
{
    ++s_checks;
    if (!condition) throw std::runtime_error(detail);
}

struct ImageFixture
{
    Il2CppImage image{};
    Il2CppAssembly assembly{};
    Il2CppTypeDefinition definition{};
    Il2CppType type{};
    Il2CppClass klass{};

    void Initialize(uint32_t index, const char* name)
    {
        image.assembly = &assembly;
        image.token = index ? EncodeImageAndMetadataIndex(index, 1) : 1;
        image.name = name;
        assembly.image = &image;
        assembly.aname.name = name;
        definition.byvalTypeIndex = EncodeImageAndMetadataIndex(index, 7);
        type.type = IL2CPP_TYPE_VALUETYPE;
        type.valuetype = true;
        type.data.typeHandle = reinterpret_cast<Il2CppMetadataTypeHandle>(&definition);
        klass.image = &image;
        klass.name = "Fixture";
        klass.byval_arg = type;
        klass.element_class = &klass;
        klass.typeMetadataHandle = type.data.typeHandle;
    }
};

Il2CppClass PublicClass(const ImageFixture& publicImage, const Il2CppType& type)
{
    Il2CppClass klass{};
    klass.image = &publicImage.image;
    klass.name = "CompoundFixture";
    klass.byval_arg = type;
    return klass;
}

Il2CppType Compound(Il2CppTypeEnum kind, const Il2CppType* element)
{
    Il2CppType type{};
    type.type = kind;
    type.data.type = element;
    return type;
}

Il2CppType GenericType(Il2CppGenericClass* genericClass)
{
    Il2CppType type{};
    type.type = IL2CPP_TYPE_GENERICINST;
    type.data.generic_class = genericClass;
    return type;
}

void CheckVisibility(const std::vector<Il2CppClass*>& hidden, const std::vector<Il2CppClass*>& ordinary,
    uint64_t generation, bool activated)
{
    for (const Il2CppClass* klass : hidden)
    {
        Require(AssemblyShadowVisibility::IsClassVisible(klass, generation) == activated,
            "Staged class visibility differs from captured publication");
        Require(AssemblyShadowVisibility::ClassUsesStagedMetadata(klass),
            "Staged origin was lost through a compound identity");
    }
    for (const Il2CppClass* klass : ordinary)
    {
        Require(AssemblyShadowVisibility::IsClassVisible(klass, generation), "Ordinary class was hidden");
        Require(!AssemblyShadowVisibility::ClassUsesStagedMetadata(klass), "Ordinary class acquired staged provenance");
    }
}

void Run(const std::string& mode)
{
    // Every registered image outlives every predicate call, as in production.
    ImageFixture publicImage, privateImages[4], ordinaryInterpreter, nonMember;
    publicImage.Initialize(0, "mscorlib");
    ordinaryInterpreter.Initialize(771, "OrdinaryInterpreter");
    nonMember.Initialize(772, "RegisteredButNeverActivated");
    std::vector<Il2CppClass*> hidden, ordinary;
    ordinary.push_back(&publicImage.klass);
    ordinary.push_back(&ordinaryInterpreter.klass);

    Require(!AssemblyShadowVisibility::IsClassVisible(nullptr), "Null class was visible");
    Require(!AssemblyShadowVisibility::IsTypeVisible(nullptr, 0), "Null type was visible");
    Require(AssemblyShadowVisibility::IsClassVisible(&publicImage.klass), "Empty registry hid an ordinary class");

    for (uint32_t kind = 0; kind != 4; ++kind)
    {
        const uint32_t offset = 1u << hybridclr::metadata::kMetadataImageIndexExtraShiftBitsArr[kind];
        const uint32_t index = (kind << (hybridclr::metadata::kMetadataImageIndexBits -
            hybridclr::metadata::kMetadataKindBits)) | offset;
        privateImages[kind].Initialize(index, "Private");
        Require(hybridclr::metadata::DecodeImageIndex(privateImages[kind].image.token) == index,
            "Fixture image index failed actual decoder");
        AssemblyShadowVisibility::RegisterPrivateImage(&privateImages[kind].image);
        AssemblyShadowVisibility::RegisterPrivateImage(&privateImages[kind].image); // Idempotent registration.
        hidden.push_back(&privateImages[kind].klass);
        Require(!AssemblyShadowVisibility::IsTypeVisible(&privateImages[kind].type, 0),
            "Unmaterialized type handle escaped one of the four metadata index encodings");
    }
    AssemblyShadowVisibility::RegisterPrivateImage(&nonMember.image);

    // Public image + raw private handle: no Il2CppClass/MetadataModule lookup is
    // available for the argument, so image-only checks cannot pass these tests.
    Il2CppType rawClass = privateImages[0].type;
    rawClass.type = IL2CPP_TYPE_CLASS;
    Il2CppClass rawClassOwner = PublicClass(publicImage, rawClass);
    Il2CppClass rawValueOwner = PublicClass(publicImage, privateImages[0].type);
    hidden.push_back(&rawClassOwner);
    hidden.push_back(&rawValueOwner);

    const Il2CppType* privateArgs[]{ &privateImages[0].type };
    const Il2CppType* publicArgs[]{ &publicImage.type };
    Il2CppGenericInst privateInst{ 1, privateArgs }, publicInst{ 1, publicArgs };
    Il2CppGenericClass nullable{ &publicImage.type, { &privateInst, nullptr }, nullptr };
    Il2CppType nullableType = GenericType(&nullable);
    Il2CppClass nullableClass = PublicClass(publicImage, nullableType);
    nullableClass.generic_class = &nullable;
    nullableClass.name = "Nullable`1";
    hidden.push_back(&nullableClass);
    Require(nullable.cached_class == nullptr && nullableClass.element_class == nullptr,
        "Nullable test accidentally materialized its private argument");

    Il2CppGenericClass publicGeneric{ &publicImage.type, { &publicInst, nullptr }, nullptr };
    Il2CppClass publicGenericClass = PublicClass(publicImage, GenericType(&publicGeneric));
    ordinary.push_back(&publicGenericClass);
    Il2CppGenericClass privateDefinition{ &privateImages[0].type, { &publicInst, nullptr }, nullptr };
    Il2CppClass privateDefinitionClass = PublicClass(publicImage, GenericType(&privateDefinition));
    hidden.push_back(&privateDefinitionClass);

    const Il2CppType* nestedArgs[]{ &nullableType };
    Il2CppGenericInst nestedInst{ 1, nestedArgs };
    Il2CppGenericClass nested{ &publicImage.type, { &nestedInst, nullptr }, nullptr };
    Il2CppClass nestedClass = PublicClass(publicImage, GenericType(&nested));
    hidden.push_back(&nestedClass);
    Il2CppGenericClass methodContext{ &publicImage.type, { &publicInst, &privateInst }, nullptr };
    Il2CppClass methodContextClass = PublicClass(publicImage, GenericType(&methodContext));
    hidden.push_back(&methodContextClass);

    Il2CppGenericParameter parameter{};
    parameter.ownerIndex = EncodeImageAndMetadataIndex(
        hybridclr::metadata::DecodeImageIndex(privateImages[1].image.token), 17);
    Il2CppType var{};
    var.type = IL2CPP_TYPE_VAR;
    var.data.genericParameterHandle = reinterpret_cast<Il2CppMetadataGenericParameterHandle>(&parameter);
    Il2CppType mvar = var;
    mvar.type = IL2CPP_TYPE_MVAR;
    Il2CppClass varClass = PublicClass(publicImage, var), mvarClass = PublicClass(publicImage, mvar);
    hidden.push_back(&varClass);
    hidden.push_back(&mvarClass);

    Il2CppType szArray = Compound(IL2CPP_TYPE_SZARRAY, &nullableType);
    Il2CppType pointer = Compound(IL2CPP_TYPE_PTR, &szArray);
    Il2CppType byref = Compound(IL2CPP_TYPE_BYREF, &pointer);
    Il2CppType byrefFlag = privateImages[0].type;
    byrefFlag.byref = true;
    Il2CppArrayType arrayData{ &nullableType, 2, 0, 0, nullptr, nullptr };
    Il2CppType array{};
    array.type = IL2CPP_TYPE_ARRAY;
    array.data.array = &arrayData;
    Il2CppClass szClass = PublicClass(publicImage, szArray), pointerClass = PublicClass(publicImage, pointer),
        byrefClass = PublicClass(publicImage, byref), flagClass = PublicClass(publicImage, byrefFlag),
        arrayClass = PublicClass(publicImage, array);
    hidden.insert(hidden.end(), { &szClass, &pointerClass, &byrefClass, &flagClass, &arrayClass });
    for (const Il2CppType* type : { &nullableType, &szArray, &pointer, &byref, &byrefFlag, &array, &var, &mvar })
        Require(!AssemblyShadowVisibility::IsTypeVisible(type, 0), "Raw compound type escaped before commit");

    Il2CppClass elementClass = PublicClass(publicImage, publicImage.type);
    elementClass.element_class = &privateImages[0].klass;
    Il2CppClass declaredClass = PublicClass(publicImage, publicImage.type);
    declaredClass.declaringType = &nullableClass;
    hidden.insert(hidden.end(), { &elementClass, &declaredClass });

    // Cycles are not an excuse to miss a later private argument, recurse forever,
    // or hide ordinary self-referential class identities.
    Il2CppType cyclicType{};
    const Il2CppType* cyclicArgs[]{ &cyclicType, &privateImages[0].type };
    Il2CppGenericInst cyclicInst{ 2, cyclicArgs };
    Il2CppGenericClass cyclic{ &publicImage.type, { &cyclicInst, nullptr }, nullptr };
    cyclicType = GenericType(&cyclic);
    Il2CppClass cyclicClass = PublicClass(publicImage, cyclicType);
    hidden.push_back(&cyclicClass);
    Il2CppClass publicCycle = PublicClass(publicImage, publicImage.type);
    publicCycle.element_class = publicCycle.declaringType = &publicCycle;
    ordinary.push_back(&publicCycle);

    CheckVisibility(hidden, ordinary, 0, false); // Staged/pre-Validate.
    CheckVisibility(hidden, ordinary, 0, false); // Validated: still no publication.
    Require(!AssemblyShadowVisibility::IsClassVisible(&nonMember.klass, 0), "Unpublished private member escaped");

    if (mode == "abort")
    {
        // Abort retains the registry and never publishes. There is deliberately
        // no fake Abort implementation or registry clearing in this harness.
        for (int iteration = 0; iteration != 128; ++iteration)
            CheckVisibility(hidden, ordinary, 0, false);
        Require(il2cpp::vm::AssemblyShadow::ActiveGeneration() == 0, "Abort scenario published a snapshot");
    }
    else
    {
        const SimulatedActiveSnapshot snapshot{ 1, { &privateImages[0].assembly, &privateImages[1].assembly,
            &privateImages[2].assembly, &privateImages[3].assembly } };
        s_simulatedActive.store(&snapshot, std::memory_order_release);
        Require(il2cpp::vm::AssemblyShadow::ActiveGeneration() == 1, "Simulated publication was not acquired");
        for (int iteration = 0; iteration != 128; ++iteration)
        {
            CheckVisibility(hidden, ordinary, 0, false); // An older enumeration cannot switch halfway through.
            CheckVisibility(hidden, ordinary, 1, true);
        }
        Require(AssemblyShadowVisibility::IsClassVisible(&nullableClass), "Committed Nullable remained hidden");
        Require(AssemblyShadowVisibility::ClassUsesStagedMetadata(&nullableClass), "Committed Nullable lost provenance");
        Require(AssemblyShadowVisibility::IsTypeVisible(&nullableType, 1), "Committed raw Nullable remained hidden");
        Require(!AssemblyShadowVisibility::IsTypeVisible(&nullableType, 0), "Old raw-type snapshot changed visibility");
        Require(!AssemblyShadowVisibility::IsClassVisible(&nonMember.klass, 1),
            "An image absent from the active snapshot became visible merely because generation is nonzero");
        Require(AssemblyShadowVisibility::ClassUsesStagedMetadata(&nonMember.klass), "Inactive private origin was lost");
    }
    std::cout << "visibility_checks=" << s_checks << " mode=" << mode << " PASS\n";
}
}

namespace il2cpp { namespace vm {
uint64_t AssemblyShadow::ActiveGeneration()
{
    const SimulatedActiveSnapshot* active = s_simulatedActive.load(std::memory_order_acquire);
    return active ? active->generation : 0;
}

bool AssemblyShadow::IsActiveShadow(const Il2CppAssembly* assembly)
{
    const SimulatedActiveSnapshot* active = s_simulatedActive.load(std::memory_order_acquire);
    if (active)
        for (const Il2CppAssembly* member : active->assemblies)
            if (member == assembly) return true;
    return false;
}
}}

int main(int argc, char** argv)
{
    try
    {
        if (argc != 2 || (std::strcmp(argv[1], "commit") != 0 && std::strcmp(argv[1], "abort") != 0))
            throw std::runtime_error("Expected exactly one scenario: commit or abort");
        Run(argv[1]);
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << "\n";
        return 1;
    }
}
