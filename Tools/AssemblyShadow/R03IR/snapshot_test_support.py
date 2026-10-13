#!/usr/bin/env python3
"""Source-bound N/O transport integration. Not a C#/IL2CPP marshaller or Unity test."""
import re
from pathlib import Path
HERE=Path(__file__).resolve().parent

def body(s, marker):
 start=s.index(marker); op=s.index('{',start); level=0
 # balanced parser handles strings/comments for C++/C# fragments
 i=op; mode=None; esc=False
 while i<len(s):
  c=s[i]; nxt=s[i:i+2]
  if mode=='line':
   if c=='\n':mode=None
  elif mode=='block':
   if nxt=='*/':mode=None;i+=1
  elif mode in ('"',"'"):
   if esc:esc=False
   elif c=='\\':esc=True
   elif c==mode:mode=None
  elif nxt=='//':mode='line';i+=1
  elif nxt=='/*':mode='block';i+=1
  elif c in ('"',"'"):mode=c
  elif c=='{':level+=1
  elif c=='}':
   level-=1
   if level==0:return s[start:i+1]
  i+=1
 raise ValueError(marker)

def prepare(source, candidate):
 cpp=source.read_text(); cs=candidate.read_text()
 fragment=cpp[cpp.index('namespace r03_ir_snapshot {'):cpp.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit')]
 # Only I/O fault-injection callsites are interposed in this test build.
 for old,new in [('::fdopen(fd, "w")','test_fdopen(fd, "w")'),('std::ferror(stream)','test_ferror(stream)'),('std::fflush(stream)','test_fflush(stream)'),('::fsync(::fileno(stream))','test_fsync(::fileno(stream))'),('std::fclose(stream)','test_fclose(stream)')]:
  assert fragment.count(old)==1,old;fragment=fragment.replace(old,new)
 emitter=body(cs,'private static bool EmitNativeReport')
 emitter=emitter.replace('private static bool EmitNativeReport(Report r)','static bool EmitNativeReport(const Report& r)')
 emitter=emitter.replace('if (r.stimulus != "baseline-owner")','if (std::strcmp(r.stimulus, "baseline-owner") != 0)')
 ints=re.findall(r'R03_IR_ReportInt\((\d+), r\.(\w+)( \? 1 : 0)?\)',emitter)
 texts=re.findall(r'R03_IR_ReportText\((\d+), r\.(\w+)\)',emitter)
 assert [int(x[0]) for x in ints]==list(range(25))
 assert [int(x[0]) for x in texts]==list(range(16))
 # Avoid silently reducing emitted fields if the C# method changes.
 assert len(re.findall('R03_IR_ReportInt\\(',emitter))==25 and len(re.findall('R03_IR_ReportText\\(',emitter))==16
 decl='struct Report {\n'+''.join(' bool '+n+'=false;\n' if b else ' int '+n+'=0;\n' for _,n,b in ints)+''.join(' const char* '+n+'=nullptr;\n' for _,n in texts)+'};\n'
 bridge=body(cpp,'extern "C" IL2CPP_EXPORT int32_t R03_IR_ObserveOldGuardIntoSnapshot')
 unique=body(cpp,'static bool UniqueValue')
 stub=r'''
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <cassert>
#include <string>
#include <thread>
#define IL2CPP_EXPORT
#define HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW 1
static std::string failure;
static FILE* test_fdopen(int fd,const char* mode){if(failure=="fdopen"){errno=ENOMEM;return nullptr;}return ::fdopen(fd,mode);}
static int test_ferror(FILE* f){if(failure=="write"){errno=EIO;return 1;}return std::ferror(f);}
static int test_fflush(FILE* f){int r=std::fflush(f);if(failure=="flush"){errno=ENOSPC;return -1;}return r;}
static int test_fsync(int fd){if(failure=="fsync"){errno=EIO;return -1;}return ::fsync(fd);}
static int test_fclose(FILE* f){int r=std::fclose(f);if(failure=="close"){errno=EIO;return -1;}return r;}
namespace il2cpp {namespace vm {
enum class AssemblyShadowState{FailedAfterCommit=9};
enum class AssemblyShadowError{Success=0};
struct AssemblyShadow{static AssemblyShadowError GetState(AssemblyShadowState& s){s=AssemblyShadowState::FailedAfterCommit;return AssemblyShadowError::Success;}};
}}
static const char* guardJson="{\"available\":true,\"activeGuard\":1,\"baselineGuard\":0,\"caughtOldGuard\":1,\"stateCode\":9,\"extra\":\"entire original producer output retained\"}";
static int R03_ObserveMethod(const char*,const char*,const char*,const char*,int mode,char* out,int capacity){
 assert(mode==3);size_t n=std::strlen(guardJson);assert(n+1<static_cast<size_t>(capacity));std::memcpy(out,guardJson,n+1);return static_cast<int>(n);
}
'''
 tests=r'''
int main(int argc,char** argv){
 assert(argc==3); std::string mode=argv[1]; const char* output=argv[2];
 Report r;
 r.initialState=6;r.poisonedState=9;r.finalState=9;r.nativeStimulusReturn=1;
 r.preActiveReflection=42;r.preActiveDelegate=42;r.preCanaryCount=1;r.finalCanaryCount=1;
 r.preShadowField=2;r.finalShadowField=2;r.nativePhase=910;r.failurePhase=0;
 r.terminalReportingProbeMask=15;r.reserveGcProbeMask=31;
 r.shadowFieldReadable=true;r.prePositive=true;r.activeReflectionAttempted=true;r.activeDelegateAttempted=true;r.aotReflectionAttempted=true;
 r.recoveryStable=true;r.fixedDiagnosticsReadable=true;
 r.result="Passed";r.runId="00112233445566778899aabbccddeeff";r.caseId="case-source";
 r.requestSha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 r.stimulus=mode=="baseline"?"baseline-owner":"type-resolution";
 r.unityVersion="2022.3.62f2";r.platform="OSXPlayer";
 r.activeReflectionException=r.activeDelegateException=r.aotReflectionException="ManagedExceptionCaught";
 r.firstRecovery=r.finalRecovery="{\"stateCode\":9,\"terminalFailureCode\":13}";
 r.finalDiagnostics="{\"stateCode\":9}";r.finalExecutionDiagnostics="{\"classes\":[]}";
 bool expect=true;
 if(mode=="no-open"){assert(R03_IR_ReportInt(0,6)==-1);assert(R03_IR_ReportSeal()==-1);return 0;}
 if(mode=="relative-open"){assert(R03_IR_ReportOpen("relative")==-1);return 0;}
 if(mode=="fdopen") failure=mode;
 int openResult=R03_IR_ReportOpen(output);
 if(mode=="fdopen"||mode=="occupied"||mode=="symlink"){assert(openResult==-1);return 0;}
 assert(openResult==1);
 if(mode=="repeat-open"){assert(R03_IR_ReportOpen(output)==-1);return 0;}
 if(mode=="wrong-thread-reentry"){
  r03_ir_snapshot::writerBusy.test_and_set();assert(R03_IR_ReportInt(0,6)==-1);r03_ir_snapshot::writerBusy.clear();assert(R03_IR_ReportSeal()==-1);return 0;
 }
 if(mode=="invalid-int"){assert(R03_IR_ReportInt(25,0)==-1);return 0;}
 if(mode=="invalid-text"){assert(R03_IR_ReportText(-1,nullptr)==-1);return 0;}
 if(mode=="invalid-bool"){assert(R03_IR_ReportInt(24,2)==-1);return 0;}
 if(mode=="duplicate-int"){assert(R03_IR_ReportInt(3,1)==1);assert(R03_IR_ReportInt(3,1)==-1);expect=false;}
 if(mode=="baseline"){assert(R03_IR_ObserveOldGuardIntoSnapshot()==1);}
 if(mode=="duplicate-text") {assert(R03_IR_ObserveOldGuardIntoSnapshot()==1);assert(R03_IR_ObserveOldGuardIntoSnapshot()==-3);expect=false;}
 if(mode=="missing-int"){assert(R03_IR_ReportSeal()==-1);return 0;}
 if(mode=="missing-text"){for(int i=0;i<25;++i)assert(R03_IR_ReportInt(i,0)==1);assert(R03_IR_ReportSeal()==-1);return 0;}
 std::string text;
 if(mode=="at-limit"||mode=="over-limit") {text.assign(mode=="at-limit"?262144:262145,'x');r.finalExecutionDiagnostics=text.c_str();expect=mode=="at-limit";}
 if(mode=="unicode"){r.error="quotes\" backslash\\ newline\n \xe4\xb8\xad\xe6\x96\x87";}
 if(mode=="failed-semantic"){r.result="Failed";r.failurePhase=170;}
 if(mode=="write"||mode=="flush"||mode=="fsync"||mode=="close"){failure=mode;expect=false;}
 if(mode=="off") {r.stimulus="off";r.initialState=r.poisonedState=r.finalState=0;r.terminalReportingProbeMask=r.reserveGcProbeMask=0;r.finalCanaryCount=2;}
 bool ok=EmitNativeReport(r);
 assert(ok==expect);
 if(expect){assert(r03_ir_snapshot::state.load()==2);assert(r03_ir_snapshot::intMask.load()==((1u<<25)-1));assert(r03_ir_snapshot::textMask.load()==((1u<<16)-1));}
 else {assert(r03_ir_snapshot::state.load()==-1);assert(R03_IR_ReportInt(0,99)==-1);assert(R03_IR_ReportSeal()==-1);}
 if(mode=="repeat-seal"){assert(R03_IR_ReportSeal()==-1);}
 return 0;
}
'''
 return stub+fragment+'\nnamespace r03_ir_observe{'+unique+'}\n'+bridge+'\n'+decl+emitter+'\n'+tests
