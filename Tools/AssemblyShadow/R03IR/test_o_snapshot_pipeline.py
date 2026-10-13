"""Actual native writer + actual C# emitter interop; VM producer inputs synthetic.
These tests verify transport contracts, not Unity semantic/GC acceptance.
"""
import json,os,re,shutil,subprocess,tempfile,unittest
from pathlib import Path
from test_n_guarded_receipts import STUB
ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
CS=ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs'
def block(text,anchor):
 start=text.index(anchor);i=text.index('{',start);depth=1;j=i+1
 while depth:
  depth += (text[j]=='{')-(text[j]=='}');j+=1
 return text[start:j]
def native_source():
 text=CPP.read_text()
 writer=text[text.index('// K test-only transport:'):text.index('extern "C" IL2CPP_EXPORT int32_t R03_IR_ProbeBooleanReserve()')]+'\n#endif\n'
 helper=text[text.index('// N: test-only native guard receipt'):text.index('// O test-only terminal scheduling disposition')]
 original=STUB[:STUB.index('int R03_IR_ReportText(')]
 return original+'\n'+'\n'.join(x for x in (writer+helper).splitlines() if not x.startswith('#include "'))
class SnapshotPipelineTests(unittest.TestCase):
 def test_native_first_failure_receipt_is_immutable(self):
  main=r'''
int main(int argc,char**argv){assert(argc==3);std::string m=argv[2];assert(R03_IR_ReportOpen(argv[1])==1);
 if(m=="missing"){assert(R03_IR_ReportSeal()==-1);}
 if(m=="bool"){assert(R03_IR_ReportInt(14,31)==-1);}
 if(m=="duplicate"){assert(R03_IR_ReportText(8,"one")==1);assert(R03_IR_ReportText(8,"two")==-1);}
 if(m=="long"){std::string large(262145,'a');assert(R03_IR_ReportText(12,large.c_str())==-1);}
 if(m=="managed"){R03_IR_ReportEmissionException();}
 if(m=="io"){
  for(int i=0;i<25;++i)assert(R03_IR_ReportInt(i,0)==1);
  for(int i=0;i<16;++i)assert(R03_IR_ReportText(i,nullptr)==1);
  ::close(::fileno(r03_ir_snapshot::stream));assert(R03_IR_ReportSeal()==-1);
 }
 assert(R03_IR_ReportInt(0,0)==-1);assert(R03_IR_ReportSeal()==-1);return 0;}
'''
  cc=shutil.which('clang++') or shutil.which('g++');self.assertTrue(cc)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();src=root/'first.cpp';exe=root/'first';src.write_text(native_source()+main)
   flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic']
   if os.getenv('R03_SANITIZERS')=='1':flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
   c=subprocess.run([cc,*flags,str(src),'-o',str(exe)],text=True,capture_output=True);self.assertEqual(c.returncode,0,c.stderr)
   for mode,operation,field in [('missing','IntMissing',0),('bool','BooleanValue',14),('duplicate','TextDuplicate',8),('long','TextLength',12),('managed','ManagedEmissionException',-1),('io','RawFlush',-1)]:
    raw=root/(mode+'.json');r=subprocess.run([str(exe),str(raw),mode],capture_output=True,text=True,timeout=20)
    self.assertEqual(r.returncode,0,(mode,r.stderr));out=json.loads(Path(str(raw)+'.transport.json').read_text())
    self.assertEqual((out['operation'],out['field']),(operation,field));self.assertIs(out['semanticAcceptance'],False)
    self.assertEqual(out['result'],'Failed');self.assertEqual(r.stderr.count('[R03SnapshotFailure] operation='),1)
 def test_actual_managed_emitter_and_native_guard_writer(self):
  dotnet=shutil.which('dotnet');self.assertTrue(dotnet,'Real .NET SDK needed for actual C# emitter interop test')
  cc=shutil.which('clang++') or shutil.which('g++');self.assertTrue(cc)
  cs=CS.read_text();report=block(cs,'[Serializable, Preserve] public sealed class Report')
  emitter=block(cs,'private static bool EmitNativeReport(')
  imports=cs[cs.index('        [DllImport('):cs.index('        [DllImport(',cs.index('private static extern void R03_IR_ReportEmissionException();'))]
  # Include only these actual declarations; no rewritten EmitNativeReport body.
  program='''using System; using System.Runtime.InteropServices; using System.Reflection;
class PreserveAttribute:Attribute {}
static class Host {
'''+report+imports+emitter+r'''
[DllImport("__Internal")]static extern int R03_IR_ObserveOldGuardIntoSnapshot();
static int Main(string[] args){
 NativeLibrary.SetDllImportResolver(typeof(Host).Assembly,(name,asm,path)=>name=="__Internal"?NativeLibrary.Load(args[0]):IntPtr.Zero);
 string mode=args[2];Report r=new Report();
 r.stimulus=mode=="baseline"?"baseline-owner":"type-resolution";
 r.result="Passed";r.runId="host-input";r.caseId="host-case";r.requestSha256=new string('a',64);
 r.unityVersion="not-a-Unity-test";r.platform="HostInteropOnly";
 r.firstRecovery="{\"stateCode\":9}";r.finalRecovery=r.firstRecovery;r.finalDiagnostics="{}";r.finalExecutionDiagnostics="{}";
 r.initialState=6;r.poisonedState=9;r.finalState=9;r.nativeStimulusReturn=1;r.preActiveReflection=42;r.preActiveDelegate=42;
 r.preCanaryCount=r.finalCanaryCount=1;r.preShadowField=r.finalShadowField=2;r.nativePhase=910;
 r.terminalReportingProbeMask=15;r.reserveGcProbeMask=31;r.shadowFieldReadable=true;r.prePositive=true;
 r.activeReflectionAttempted=r.activeDelegateAttempted=r.aotReflectionAttempted=true;
 r.activeReflectionException=r.activeDelegateException=r.aotReflectionException="Synthetic test rejection";
 r.recoveryStable=r.fixedDiagnosticsReadable=true;
 if(R03_IR_ReportOpen(args[1])!=1)return 90;
 if(mode=="baseline"&&R03_IR_ObserveOldGuardIntoSnapshot()!=1)return 91;
 if(mode=="long")r.finalDiagnostics=new string('x',262145);
 bool result=EmitNativeReport(r);return result==(mode!="long")?0:92;
}}
'''
  with tempfile.TemporaryDirectory() as td:
   root=Path(td).resolve();lib=root/('libsnapshot.dylib' if os.uname().sysname=='Darwin' else 'libsnapshot.so');native=root/'native.cpp';native.write_text(native_source())
   c=subprocess.run([cc,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-fPIC','-dynamiclib' if os.uname().sysname=='Darwin' else '-shared',str(native),'-o',str(lib)],capture_output=True,text=True);self.assertEqual(c.returncode,0,c.stderr)
   (root/'Host.cs').write_text(program);(root/'Host.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><UseSharedCompilation>false</UseSharedCompilation></PropertyGroup><ItemGroup><Compile Include="Host.cs" /></ItemGroup></Project>')
   env=dict(os.environ,DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_NOLOGO='1')
   c=subprocess.run([dotnet,'build',str(root/'Host.csproj'),'-o',str(root/'bin'),'--nologo','-v:q','-p:UseSharedCompilation=false'],capture_output=True,text=True,env=env,timeout=90)
   self.assertEqual(c.returncode,0,c.stdout+c.stderr)
   for mode in ('baseline','type','long'):
    target=root/(mode+'.json');r=subprocess.run([dotnet,str(root/'bin/Host.dll'),str(lib),str(target),mode],capture_output=True,text=True,env=env,timeout=20)
    self.assertEqual(r.returncode,0,(mode,r.stderr))
    receipt=json.loads(Path(str(target)+'.transport.json').read_text())
    if mode=='long':
     self.assertEqual(receipt['operation'],'TextLength');self.assertEqual(receipt['field'],14);self.assertEqual(target.stat().st_size,0)
    else:
     raw=json.loads(target.read_text());self.assertEqual(raw['result'],'Passed');self.assertEqual(raw['finalShadowField'],2)
     self.assertEqual(receipt['result'],'Sealed')
     if mode=='baseline':self.assertEqual(json.loads(raw['nativeGuardJson'])['caughtOldGuard'],1)
if __name__=='__main__':unittest.main()
