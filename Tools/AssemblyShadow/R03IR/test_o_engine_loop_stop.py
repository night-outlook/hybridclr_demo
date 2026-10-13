"""Actual test-only native loop preparation/disposition; Unity/metadata/GC mocked.
The mock native setter is not a real PlayerLoop integration or runtime PASS.
"""
import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
STUB=r'''
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <thread>
#define IL2CPP_EXPORT
#define HYBRIDCLR_R03_RUNTIME_PROBE 1
#ifndef HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
#endif
#define METHOD_ATTRIBUTE_STATIC 16
#define METHOD_IMPL_ATTRIBUTE_INTERNAL_CALL 4096
#define IL2CPP_TYPE_VOID 1
#define IL2CPP_TYPE_SZARRAY 29
struct Il2CppAssembly;
struct Il2CppImage { Il2CppAssembly* assembly; };
struct Il2CppAssembly { Il2CppImage* image; };
struct Il2CppType { int type; bool valuetype; };
struct Il2CppClass { Il2CppImage* image; const char* name; const char* namespaze;
 int rank; Il2CppClass* element_class; unsigned element_size; unsigned field_count;
 void* generic_class; Il2CppType byval_arg; };
struct Il2CppObject { Il2CppClass* klass; };
struct Il2CppArray:Il2CppObject { void* bounds; uintptr_t max_length; unsigned char data[40]; };
struct Il2CppString { int length; uint16_t chars[100]; };
struct Il2CppException:Il2CppObject { Il2CppString* message; };
struct MethodInfo { Il2CppClass* klass; int flags,iflags; const Il2CppType* return_type;
 const Il2CppType** parameters; };
using Il2CppMethodPointer=void (*)();
Il2CppImage core{},corlib{};
Il2CppAssembly assembly{&core};
Il2CppClass element{&core,"PlayerLoopSystemInternal","UnityEngine.LowLevel",0,nullptr,40,5,nullptr,{0,true}};
Il2CppClass arrayK{&core,"Array","",1,&element,40,0,nullptr,{0,false}};
Il2CppClass exceptionK{&corlib,"InvalidOperationException","System",0,nullptr,0,0,nullptr,{0,false}};
Il2CppClass loopK{&core,"PlayerLoop","UnityEngine.LowLevel",0,nullptr,0,0,nullptr,{0,false}};
Il2CppArray graph{{&arrayK},nullptr,1,{}};
Il2CppString text{};
Il2CppException exception{{&exceptionK},&text},other{{&exceptionK},&text};
Il2CppType ret{IL2CPP_TYPE_VOID,false},arg{IL2CPP_TYPE_SZARRAY,false};
const Il2CppType* args[1]={&arg};
MethodInfo method{&loopK,METHOD_ATTRIBUTE_STATIC,METHOD_IMPL_ATTRIBUTE_INTERNAL_CALL,&ret,args};
int current=6,pins=0,lookups=0,setters=0;bool throwSetter=false;
void SetLoop(Il2CppArray* arr){assert(current==9&&arr==&graph);++setters;if(throwSetter)throw 1;}
namespace il2cpp { namespace gc {
struct GCHandle {
 static Il2CppObject* GetTarget(uint32_t h){assert(current==6);++lookups;return(h==7||h==11)?static_cast<Il2CppObject*>(&graph):(h==8||h==12)?static_cast<Il2CppObject*>(&exception):nullptr;}
 static uint32_t New(Il2CppObject* p,bool pinned){assert(current==6&&pinned);++pins;return p==&graph?11:12;}
 static void Free(uint32_t){assert(current==6);}
}; } namespace vm {
enum class AssemblyShadowState { Committed=6, FailedAfterCommit=9 };
enum class AssemblyShadowError { Success=0 };
struct AssemblyShadow {
 static AssemblyShadowError GetState(AssemblyShadowState& s){s=static_cast<AssemblyShadowState>(current);return AssemblyShadowError::Success;}
 static bool IsCandidate(const Il2CppAssembly*){return false;}
 static bool IsShadowedBaseline(const Il2CppAssembly*){return false;}
 static bool IsActiveShadow(const Il2CppAssembly*){return false;}
};
struct Array { static char* GetFirstElementAddress(Il2CppArray* p){return reinterpret_cast<char*>(p->data);} };
struct Image { static Il2CppImage* GetCorlib(){return &corlib;} };
struct MetadataCache {static const Il2CppAssembly* GetAotAssemblyByNamePhysical(const char*){return &assembly;} };
struct Class {
 static bool IsValuetype(Il2CppClass* c){return c->byval_arg.valuetype;}
 static Il2CppClass* FromName(Il2CppImage*,const char*,const char*){assert(current==6);return &loopK;}
 static const MethodInfo* GetMethodFromName(Il2CppClass*,const char*,int){assert(current==6);return &method;}
};
struct InternalCalls {static Il2CppMethodPointer Resolve(const char* name){assert(current==6&&std::strstr(name,"SetPlayerLoopInternal"));return reinterpret_cast<Il2CppMethodPointer>(&SetLoop);} };
namespace assembly_shadow_reporting {
using EngineDisposition=void(*)(const Il2CppException*);
std::atomic<EngineDisposition>& EngineDispositionObserver(){static std::atomic<EngineDisposition> f{nullptr};return f;}
}
}}
'''
MAIN=r'''
int main(int argc,char**argv){
 assert(argc==2); const char* mode=argv[1];const char* run="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 const char* sentinel="R03_ENGINE_UNHANDLED_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 text.length=std::strlen(sentinel);for(int i=0;i<text.length;++i)text.chars[i]=sentinel[i];
#if !HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW
 (void)mode; (void)run;
 assert(R03_IR_PrepareEngineLoopStop(nullptr,nullptr,nullptr)==0);return 0;
#else
 if(!std::strcmp(mode,"state")){current=9;assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-1);return 0;}
 if(!std::strcmp(mode,"run")){assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,"short")==-2);return 0;}
 if(!std::strcmp(mode,"array")){arrayK.rank=2;assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-3);return 0;}
 if(!std::strcmp(mode,"identity")){element.name="Other";assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-4);return 0;}
 if(!std::strcmp(mode,"nonzero")){graph.data[4]=1;assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-5);return 0;}
 if(!std::strcmp(mode,"sentinel")){text.chars[3]='x';assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-6);return 0;}
 if(!std::strcmp(mode,"icall")){method.iflags=0;assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==-7);return 0;}
 assert(R03_IR_PrepareEngineLoopStop((void*)7,(void*)8,run)==1);
 assert(setters==0&&pins==2);int saved=lookups;
 auto f=il2cpp::vm::assembly_shadow_reporting::EngineDispositionObserver().load();assert(f);
 f(&other);assert(setters==0); // identical message is not the exact object
 if(!std::strcmp(mode,"healthy")){f(&exception);return 99;}
 current=9;
 if(!std::strcmp(mode,"thread")){std::thread t([&]{f(&exception);});t.join();return 99;}
 if(!std::strcmp(mode,"mutate")){graph.data[0]=1;f(&exception);return 99;}
 if(!std::strcmp(mode,"throws"))throwSetter=true;
 f(&exception);for(int i=0;i<100;++i)f(&exception);
 assert(setters==1&&lookups==saved&&pins==2);
 std::puts("{\"result\":\"Passed\",\"mockSetterCalls\":1,\"managedBodies\":0}");return 0;
#endif
}
'''
class EngineLoopStopTests(unittest.TestCase):
 def test_exact_native_loop_disposition(self):
  source=CPP.read_text();fragment=source[source.index('// O test-only terminal scheduling disposition.'):]
  fragment='\n'.join(x for x in fragment.splitlines() if not x.startswith('#include "'))
  cc=shutil.which('clang++') or shutil.which('g++');self.assertTrue(cc)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();src=root/'loop.cpp';src.write_text(STUB+'\n// O test-only terminal scheduling disposition.\n'+fragment+'\n'+MAIN)
   flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread']
   if os.environ.get('R03_SANITIZERS')=='1':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
   for feature in (1,0):
    exe=root/('loop'+str(feature));c=subprocess.run([cc,*flags,'-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW='+str(feature),str(src),'-o',str(exe)],capture_output=True,text=True)
    self.assertEqual(c.returncode,0,c.stderr)
    cases={'positive':0,'state':0,'run':0,'array':0,'identity':0,'nonzero':0,'sentinel':0,'icall':0,'healthy':73,'thread':73,'mutate':73,'throws':74} if feature else {'off':0}
    for mode,expected in cases.items():
     run=subprocess.run([str(exe),mode],capture_output=True,text=True,timeout=20)
     self.assertEqual(run.returncode,expected,(mode,run.stderr))
     if mode=='positive':self.assertEqual(json.loads(run.stdout)['mockSetterCalls'],1)
 def test_counter_and_business_checks_not_replaced(self):
  overlay=CPP.read_text()
  self.assertNotIn('CompletedCounter().store',overlay)
  self.assertNotIn('CompletedCounter().fetch_add',overlay)
  self.assertIn('prepared.set(prepared.graph);',overlay)
  player=(ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs').read_text()
  self.assertLess(player.index('R03_IR_PrepareEngineLoopStop(GCHandle'),player.index('report.reserveGcProbeMask = R03_IR_ProbeBooleanReserve();'))
  self.assertIn('throw engineSentinel;',player)
  self.assertIn('1 <= raw[\'completedReports\'] <= 64',(ROOT/'R03IR/run_terminal_local.py').read_text())
if __name__=='__main__':unittest.main()
