// Actual exported C API + actual published-snapshot mapping. The physical VM
// getters below are controlled adapters, not a Unity registry/Player substitute.
// Nothing initializes a class, mutates metadata, or runs a transaction here.
#include "vm/AssemblyShadow.cpp"
#include "il2cpp-api.h"
#include "vm/Assembly.h"
#include "vm/Class.h"
#include "vm/Image.h"
#include <cstdio>
#include <stdexcept>

namespace {
using namespace il2cpp::vm;
size_t checks = 0;
void Check(bool condition, const char* detail)
{
    ++checks;
    if (!condition) throw std::runtime_error(detail);
}

struct PhysicalImage
{
    Il2CppAssembly assembly = {};
    Il2CppImage image = {};
    Il2CppClass classes[3] = {};
    PhysicalImage(const char* name, uint32_t count)
    {
        assembly.aname.name = name;
        assembly.image = &image;
        image.name = image.nameNoExt = name;
        image.assembly = &assembly;
        image.typeCount = count;
        image.metadataHandle = reinterpret_cast<Il2CppMetadataImageHandle>(this);
        for (auto& klass : classes)
        {
            klass.image = &image;
            klass.name = "Value";
            klass.namespaze = "Tests";
        }
    }
};

void Unchanged(PhysicalImage& physical)
{
    Check(il2cpp_assembly_get_image(&physical.assembly) == &physical.image, "ordinary assembly image identity");
    Check(il2cpp_class_get_image(&physical.classes[0]) == &physical.image, "ordinary class image identity");
    Check(il2cpp_image_get_assembly(&physical.image) == &physical.assembly, "ordinary image assembly identity");
    Check(il2cpp_image_get_class_count(&physical.image) == physical.image.typeCount, "ordinary physical count");
    for (uint32_t i = 0; i < physical.image.typeCount; ++i)
        Check(il2cpp_image_get_class(&physical.image, i) == &physical.classes[i], "ordinary physical indexed classes");
}
}

// Physical getter adapters intentionally do no shadow resolution. This tests
// normalization in the production exports, not a duplicate modeled facade.
namespace il2cpp { namespace vm {
const Il2CppImage* Class::GetImage(Il2CppClass* klass) { return klass->image; }
Il2CppImage* Assembly::GetImage(const Il2CppAssembly* assembly) { return assembly->image; }
const Il2CppAssembly* Image::GetAssembly(const Il2CppImage* image) { return image->assembly; }
uint32_t Image::GetNumTypes(const Il2CppImage* image) { return image->typeCount; }
const Il2CppClass* Image::GetType(const Il2CppImage* image, AssemblyTypeIndex index)
{
    if (index < 0 || static_cast<uint32_t>(index) >= image->typeCount)
        throw std::runtime_error("physical image class index outside fixture");
    auto physical = reinterpret_cast<const PhysicalImage*>(image->metadataHandle);
    return &physical->classes[index];
}
}}

int main()
{
    using namespace il2cpp::vm;
    try
    {
        PhysicalImage baseline("Tests.Business", 1), active("Tests.Business", 3),
            privateSameName("Tests.Business", 2), ordinary("Tests.Ordinary", 2), stable("mscorlib", 1);
        const Il2CppImage* startupIdentity = il2cpp_assembly_get_image(&baseline.assembly);
        Unchanged(baseline);
        Unchanged(active);
        Unchanged(privateSameName);
        Unchanged(ordinary);
        Unchanged(stable);
#if HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
        Check(AssemblyShadow::ResolvePublicImageIdentity(nullptr) == nullptr, "null public identity before publication");
        Check(AssemblyShadow::ResolvePublicImageIdentity(&active.image) == &active.image, "unpublished image remains physical");
        ActiveSnapshot snapshot;
        snapshot.byAssembly.emplace(&baseline.assembly, &active.assembly);
        snapshot.byImage.emplace(&baseline.image, &active.image);
        snapshot.shadowToBaseline.emplace(&active.assembly, &baseline.assembly);
        Il2CppImage alternatePhysicalImage = active.image;
        const uint64_t usageBefore = s_usageGeneration;
        s_active.store(&snapshot, std::memory_order_release);
        for (auto state : {AssemblyShadowState::Committing, AssemblyShadowState::Committed,
                           AssemblyShadowState::FailedAfterCommit})
        {
            s_state.store(state, std::memory_order_release);
            Check(AssemblyShadow::ResolvePublicImageIdentity(nullptr) == nullptr, "null public identity after publication");
            Check(AssemblyShadow::ResolvePublicImageIdentity(&active.image) == startupIdentity, "active maps to registered public image");
            Check(AssemblyShadow::ResolvePublicImageIdentity(startupIdentity) == startupIdentity, "public identity is idempotent");
            Check(AssemblyShadow::ResolvePublicImageIdentity(&alternatePhysicalImage) == &alternatePhysicalImage,
                  "an unregistered alternate image cannot borrow the published assembly mapping");
            Check(AssemblyShadow::ResolveImage(startupIdentity) == &active.image, "metadata resolver direction remains active");
            Check(AssemblyShadow::ResolveImage(&active.image) == &active.image, "active metadata is idempotent");
            for (auto assembly : {&baseline.assembly, &active.assembly})
                Check(il2cpp_assembly_get_image(assembly) == startupIdentity, "assembly public image remains registered");
            Check(il2cpp_class_get_image(&baseline.classes[0]) == startupIdentity, "old class image identity remains registered");
            Check(il2cpp_class_get_image(&active.classes[0]) == startupIdentity, "new class image identity remains registered");
            for (auto image : {startupIdentity, static_cast<const Il2CppImage*>(&active.image)})
            {
                Check(il2cpp_image_get_assembly(image) == &active.assembly, "public image resolves to active assembly");
                Check(il2cpp_assembly_get_image(il2cpp_image_get_assembly(image)) == startupIdentity, "image assembly image round trip");
                Check(il2cpp_image_get_class_count(image) == 3, "public and physical active images enumerate patch count");
                for (size_t i = 0; i < 3; ++i)
                {
                    const Il2CppClass* klass = il2cpp_image_get_class(image, i);
                    Check(klass == &active.classes[i], "indexed image enumeration selects actual active row including added types");
                    Check(il2cpp_class_get_image(const_cast<Il2CppClass*>(klass)) == startupIdentity, "enumerated active class has stable public image");
                }
            }
            Unchanged(privateSameName);
            Unchanged(ordinary);
            Unchanged(stable);
            Check(s_state.load(std::memory_order_acquire) == state, "public identity never changes transaction state");
            Check(s_usageGeneration == usageBefore, "public identity does not fabricate baseline type use");
            Check(baseline.assembly.image == &baseline.image && active.assembly.image == &active.image,
                  "physical assembly image fields unchanged");
            Check(baseline.classes[0].image == &baseline.image && active.classes[0].image == &active.image,
                  "physical class images unchanged");
            Check(Class::GetImage(&active.classes[0]) == &active.image && Assembly::GetImage(&active.assembly) == &active.image,
                  "raw VM getters remain physical");
            Check(Image::GetNumTypes(&baseline.image) == 1 && Image::GetType(&baseline.image, 0) == &baseline.classes[0],
                  "raw metadata enumeration remains physical");
            Check(!baseline.classes[0].initialized && !active.classes[0].initialized, "no class initialization");
        }
        s_active.store(nullptr, std::memory_order_release); // Fixture lifetime only, not a production reset path.
#else
        Check(il2cpp_assembly_get_image(&active.assembly) != startupIdentity, "OFF keeps distinct physical image identities");
        Check(il2cpp_image_get_class_count(startupIdentity) == 1, "OFF baseline count unchanged");
        Check(il2cpp_image_get_class(startupIdentity, 0) == &baseline.classes[0], "OFF baseline indexed class unchanged");
#endif
        std::printf("m05_image_identity_checks=%zu feature=%d PASS\n", checks, HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW);
        return 0;
    }
    catch (const std::exception& error)
    {
        std::fprintf(stderr, "FAIL: %s\n", error.what());
        return 1;
    }
}
