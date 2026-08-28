// Execute the production metadata::Image -> vm::Image lookup path against
// controlled raw metadata records. These adapters count materialization and
// diagnostic hooks; they do not emulate an AssemblyShadow transaction/state.
#include <stdexcept>
#include <vector>
#include "hybridclr/metadata/Image.h"
#include "vm/AssemblyShadow.h"
#include "vm/Class.h"
#include "vm/Image.h"
#include "vm/MetadataCache.h"

Il2CppDefaults il2cpp_defaults = {};

namespace {
struct TypeRecord
{
    const char* namespaze;
    const char* name;
    Il2CppClass* klass;
    size_t materializations;
};
struct ImageRecord
{
    const Il2CppImage* image;
    std::vector<TypeRecord*> definitions;
    std::vector<TypeRecord*> exports;
};
std::vector<ImageRecord> s_images;
Il2CppClass* s_candidateClass;
size_t s_candidateTraces;
size_t s_approvedTraces;
size_t s_imageRedirects;

void Check(bool condition, const char* message)
{
    if (!condition) throw std::runtime_error(message);
}

const ImageRecord& Record(const Il2CppImage* image)
{
    for (const auto& entry : s_images) if (entry.image == image) return entry;
    throw std::runtime_error("Lookup touched an unknown physical image");
}
TypeRecord& Record(Il2CppMetadataTypeHandle handle)
{
    return *reinterpret_cast<TypeRecord*>(const_cast<void*>(reinterpret_cast<const void*>(handle)));
}
Il2CppMetadataTypeHandle Handle(TypeRecord* record)
{
    return reinterpret_cast<Il2CppMetadataTypeHandle>(record);
}
}

namespace il2cpp { namespace vm {
Il2CppMetadataTypeHandle MetadataCache::GetAssemblyTypeHandle(const Il2CppImage* image, AssemblyTypeIndex index)
{
    return Handle(Record(image).definitions.at(index));
}
Il2CppMetadataTypeHandle MetadataCache::GetAssemblyExportedTypeHandle(const Il2CppImage* image, AssemblyExportedTypeIndex index)
{
    return Handle(Record(image).exports.at(index));
}
std::pair<const char*, const char*> MetadataCache::GetTypeNamespaceAndName(Il2CppMetadataTypeHandle handle)
{
    TypeRecord& record = Record(handle);
    return { record.namespaze, record.name };
}
bool MetadataCache::TypeIsNested(Il2CppMetadataTypeHandle) { return false; }
Il2CppMetadataTypeHandle MetadataCache::GetNestedTypes(Il2CppMetadataTypeHandle, void**) { return nullptr; }
Il2CppClass* MetadataCache::GetTypeInfoFromHandle(Il2CppMetadataTypeHandle handle)
{
    TypeRecord& record = Record(handle);
    ++record.materializations;
    return record.klass;
}
void AssemblyShadow::TraceClass(const char*, const Il2CppClass* klass)
{
    if (klass == s_candidateClass) ++s_candidateTraces;
    else ++s_approvedTraces;
}
void AssemblyShadow::TraceImage(const char*, const Il2CppImage*) {}
const Il2CppImage* AssemblyShadow::ResolveImage(const Il2CppImage* image)
{
    ++s_imageRedirects;
    return image;
}
Il2CppClass* Class::FromName(const Il2CppImage* image, const char* namespaze, const char* name)
{
    return Image::ClassFromName(image, namespaze, name);
}
}}

size_t CheckActualFacadeLookup()
{
    using hybridclr::metadata::AssemblyShadowBridge;
    using hybridclr::metadata::Image;
    Check(!AssemblyShadowBridge::IsStaging(), "Lookup regression must run outside staging TLS");
    Il2CppAssembly forwarderAssembly = {}, approvedAssembly = {}, candidateAssembly = {};
    Il2CppImage forwarderImage = {}, approvedImage = {}, candidateImage = {};
    forwarderAssembly.image = &forwarderImage; forwarderImage.assembly = &forwarderAssembly;
    approvedAssembly.image = &approvedImage; approvedImage.assembly = &approvedAssembly;
    candidateAssembly.image = &candidateImage; candidateImage.assembly = &candidateAssembly;
    Il2CppClass unrelatedClass = {}, approvedClass = {}, candidateClass = {};
    unrelatedClass.image = &forwarderImage;
    approvedClass.image = &approvedImage;
    candidateClass.image = &candidateImage;
    TypeRecord unrelated{ "FacadeFixture", "Other", &unrelatedClass };
    TypeRecord approved{ "FacadeFixture", "Target", &approvedClass };
    TypeRecord candidate{ "FacadeFixture", "Target", &candidateClass };
    forwarderImage.typeCount = 1; forwarderImage.exportedTypeCount = 1;
    approvedImage.typeCount = 1; candidateImage.typeCount = 1;
    s_images = { { &forwarderImage, { &unrelated }, { &candidate } },
                 { &approvedImage, { &approved }, {} }, { &candidateImage, { &candidate }, {} } };
    s_candidateClass = &candidateClass;
    s_candidateTraces = s_approvedTraces = s_imageRedirects = 0;
    // Positive control: the previous general lookup actually traverses the
    // forwarder and reaches both candidate materialization and its usage hook.
    Check(il2cpp::vm::Image::ClassFromName(&forwarderImage, "FacadeFixture", "Target") == &candidateClass,
        "Forwarded fixture does not reproduce the unsafe lookup");
    Check(candidate.materializations == 1 && s_candidateTraces == 1,
        "Unsafe lookup control did not reach the instrumented candidate hooks");
    candidate.materializations = 0;
    s_candidateTraces = s_approvedTraces = s_imageRedirects = 0;
    std::vector<const Il2CppAssembly*> onlyForwarder{ &forwarderAssembly };
    Check(Image::FindApprovedFacadeType(onlyForwarder, "FacadeFixture", "Target") == nullptr,
        "Unauthorized forwarded handle was materialized/accepted");
    Check(candidate.materializations == 0 && s_candidateTraces == 0 && s_approvedTraces == 0,
        "Rejected forwarder reached materialization or diagnostic hooks");
    std::vector<const Il2CppAssembly*> orderedProviders{ &forwarderAssembly, &approvedAssembly };
    Check(Image::FindApprovedFacadeType(orderedProviders, "FacadeFixture", "Target") == &approvedClass,
        "Rejected forwarder prevented later approved provider lookup");
    Check(candidate.materializations == 0 && s_candidateTraces == 0,
        "Later-provider lookup touched candidate baseline hooks");
    Check(approved.materializations == 1 && s_approvedTraces == 1,
        "Approved definition was not materialized/traced exactly once");
    Check(unrelated.materializations == 0, "Ownership scan materialized unrelated definitions");
    Check(s_imageRedirects == 0, "Physical defining-image lookup invoked global image redirection");
    Check(Image::FindApprovedFacadeType(orderedProviders, "FacadeFixture", "Missing") == nullptr,
        "Missing facade type unexpectedly resolved");
    Check(candidate.materializations == 0 && s_candidateTraces == 0 && approved.materializations == 1,
        "Missing type lookup changed materialization/usage-hook counters");
    Check(!AssemblyShadowBridge::IsStaging(), "Lookup test changed staging TLS state");
    s_images.clear();
    s_candidateClass = nullptr;
    return 13;
}
