"""Test dependencies for the exact production serializer; no real VM/GC."""
stub=r'''
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
'''
main=r'''
int main(int argc,char** argv){
 assert(argc==2);Il2CppAssembly assembly{{"mscorlib"},nullptr};Il2CppImage image{&assembly,0};assembly.image=&image;
 std::array<Il2CppClass,1024> classes;
 for(size_t i=0;i<classes.size();++i){classes[i].image=&image;s_executionClasses[i]=&classes[i];}
 std::string result;assert(AssemblyShadow::GetExecutionDiagnosticsJson(result)==AssemblyShadowError::Success);
 std::ofstream out(argv[1],std::ios::binary);out<<result;out.close();
 std::cout<<result.size()<<"\n";
}
'''
