#include "AssemblyShadowExecutionSerializer.h"

#include <array>
#include <atomic>
#include <map>
#include <vector>
#include <cstdint>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <cassert>
#define IL2CPP_DEBUG 0
struct Il2CppType{};
struct Il2CppImage;
struct Il2CppAssembly {struct{const char*name;}aname;Il2CppImage*image;};
struct Il2CppImage{Il2CppAssembly*assembly;uint32_t typeCount;};
struct Il2CppClass{Il2CppImage*image;Il2CppType byval_arg;void*static_fields=nullptr;int32_t cctor_started=0,cctor_finished_or_no_cctor=1,initializationExceptionGCHandle=0;};
enum class AssemblyShadowState{FailedAfterCommit=9};
enum class AssemblyShadowError{Success=0};
struct ShadowTypeResolutionFailure{AssemblyShadowError error;};
constexpr size_t kMaximumExecutionClasses=1024;
std::array<Il2CppClass*,kMaximumExecutionClasses*2> s_executionClasses{};
struct ExecutionObservationLock{ExecutionObservationLock(){} ~ExecutionObservationLock(){}};
using AssemblyVector=std::vector<const Il2CppAssembly*>;
struct Assembly{static void CaptureShadowEnumeration(AssemblyVector&) {}};
struct MetadataCache{static const Il2CppType* GetAssemblyTypeHandle(const Il2CppImage*,uint32_t){return nullptr;}};
struct AssemblyShadowTypeKey{
 using MetadataTypeImages=std::map<const Il2CppType*,const Il2CppImage*>;
 static std::string FormatMetadataOnly(const Il2CppType*,const MetadataTypeImages&){return "Synthetic.ShortType";}
};
struct ActiveSnapshot{uint64_t generation=1;std::map<const Il2CppAssembly*,const Il2CppAssembly*> byAssembly,shadowToBaseline;};
ActiveSnapshot active;
std::atomic<const ActiveSnapshot*>s_active{&active};
std::atomic<AssemblyShadowState>s_state{AssemblyShadowState::FailedAfterCommit};
std::atomic<uint64_t> s_shadowMethodChecks{2},s_rejectedBaselineMethods{3},s_methodChecks{6},s_shadowInterpreterTransformations{2},s_interpreterTransformations{2},s_baselineClassCctorStarted{0},s_shadowClassCctorStarted{0},s_droppedClassObservations{0};
struct AssemblyShadowDiagnostics{
 static std::string Quote(const char* s){return std::string("\"")+s+"\"";}
 static std::string Quote(const std::string& s){return Quote(s.c_str());}
 static const char* StateName(AssemblyShadowState){return "FailedAfterCommit";}
};
namespace assembly_shadow_r02{struct ObservationCounters{static constexpr int Level=2;};inline void AppendDiagnostics(std::ostream&) {}}
int g_MetadataLock;
namespace il2cpp{namespace os{struct FastAutoLock{explicit FastAutoLock(int*){}~FastAutoLock(){}};}}
namespace os{struct Atomic{static int32_t LoadRelaxed(const int32_t* p){return *p;}};}
bool Interpreter(const Il2CppAssembly*){return false;}
struct AssemblyShadow{static AssemblyShadowError GetExecutionDiagnosticsJson(std::string&);};

using namespace il2cpp::vm;
AssemblyShadowError AssemblyShadow::GetExecutionDiagnosticsJson(std::string& json)
{
    json.clear();
    std::array<Il2CppClass*, kMaximumExecutionClasses> classes{};
    size_t count = 0;
    if (assembly_shadow_r02::ObservationCounters::Level >= 2)
    {
        ExecutionObservationLock lock;
        for (Il2CppClass* klass : s_executionClasses)
            if (klass) classes[count++] = klass;
    }
    // No observation lock remains held while reading physical metadata. The
    // inventory creates neither classes nor generic instances, including AOT.
    AssemblyVector assemblies;
    if (count) Assembly::CaptureShadowEnumeration(assemblies);
    AssemblyShadowTypeKey::MetadataTypeImages images;
    for (const Il2CppAssembly* assembly : assemblies)
        for (uint32_t index = 0; index < assembly->image->typeCount; ++index)
            images.emplace(MetadataCache::GetAssemblyTypeHandle(assembly->image, index), assembly->image);

    const ActiveSnapshot* active = s_active.load(std::memory_order_acquire);
    const AssemblyShadowState state = s_state.load(std::memory_order_acquire);
    // Subset increments release-publish their preceding total increments. Read
    // them with acquire before totals: no impossible subset > total snapshot.
    const uint64_t shadowChecks = s_shadowMethodChecks.load(std::memory_order_acquire);
    const uint64_t rejectedChecks = s_rejectedBaselineMethods.load(std::memory_order_acquire);
    const uint64_t methodChecks = s_methodChecks.load(std::memory_order_relaxed);
    const uint64_t shadowTransforms = s_shadowInterpreterTransformations.load(std::memory_order_acquire);
    const uint64_t transforms = s_interpreterTransformations.load(std::memory_order_relaxed);
    // Both legacy JSON and a future bounded sink use the same field order,
    // escaping and numeric formatting. This formatter does NOT freeze VM data.
    assembly_shadow_execution_diagnostic::Header heading;
    heading.stateCode = static_cast<int>(state);
    heading.state = AssemblyShadowDiagnostics::StateName(state);
    heading.generation = active ? active->generation : 0;
    heading.methodChecks = methodChecks;
    heading.shadowMethodChecks = shadowChecks;
    heading.rejectedBaselineMethods = rejectedChecks;
    heading.baselineClassCctorStarted = s_baselineClassCctorStarted.load(std::memory_order_relaxed);
    heading.shadowClassCctorStarted = s_shadowClassCctorStarted.load(std::memory_order_relaxed);
    heading.interpreterTransformations = transforms;
    heading.shadowInterpreterTransformations = shadowTransforms;
    heading.droppedClassObservations = s_droppedClassObservations.load(std::memory_order_relaxed);
    std::ostringstream output;
    assembly_shadow_execution_diagnostic::Begin(output, heading);
    for (size_t index = 0; index < count; ++index)
    {
        Il2CppClass* klass = classes[index];
        const Il2CppAssembly* owner = klass->image->assembly;
        const bool baseline = active && active->byAssembly.count(owner);
        const bool shadow = active && active->shadowToBaseline.count(owner);
        std::string typeKey;
        try { typeKey = AssemblyShadowTypeKey::FormatMetadataOnly(&klass->byval_arg, images); }
        catch (const ShadowTypeResolutionFailure& failure) { return failure.error; }
        void* storage;
        {
            il2cpp::os::FastAutoLock metadataLock(&g_MetadataLock);
            storage = klass->static_fields; // Only already-existing storage.
        }
        const bool started = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_started)) != 0;
        const bool finished = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->cctor_finished_or_no_cctor)) != 0;
        const bool exception = os::Atomic::LoadRelaxed(reinterpret_cast<const int32_t*>(&klass->initializationExceptionGCHandle)) != 0;
        std::string pointer;
#if IL2CPP_DEBUG
        const bool details = true;
        if (storage)
        {
            std::ostringstream address;
            address << "0x" << std::hex << reinterpret_cast<uintptr_t>(storage);
            pointer = address.str();
        }
#else
        const bool details = false;
#endif
        assembly_shadow_execution_diagnostic::ClassRow row;
        row.logicalAssembly = assembly_shadow_diagnostic::Quoted(owner->aname.name);
        row.typeKey = assembly_shadow_diagnostic::Quoted(typeKey);
        row.interpreterShadow = baseline || shadow;
        row.physicalInterpreter = Interpreter(owner);
        row.isActive = !baseline;
        row.cctorStarted = started;
        row.cctorFinished = finished;
        row.hasInitializationException = exception;
        row.staticStoragePointer = assembly_shadow_diagnostic::Quoted(pointer);
        row.pointerDetailsAvailable = details;
        row.staticStorageAvailable = storage != nullptr;
        // typeKey/pointer are alive throughout this synchronous append.
        assembly_shadow_execution_diagnostic::AppendClass(output, row, index != 0);
    }
    assembly_shadow_execution_diagnostic::EndClasses(output);
    assembly_shadow_r02::AppendDiagnostics(output);
    output << "}";
    json = output.str();
    return AssemblyShadowError::Success;
}

int main(int argc,char** argv){
 assert(argc==2);Il2CppAssembly assembly{{"mscorlib"},nullptr};Il2CppImage image{&assembly,0};assembly.image=&image;
 std::array<Il2CppClass,1024> classes;
 (void)classes;
 std::string result;assert(AssemblyShadow::GetExecutionDiagnosticsJson(result)==AssemblyShadowError::Success);
 std::ofstream out(argv[1],std::ios::binary);out<<result;out.close();
 std::cout<<result.size()<<"\n";
}
