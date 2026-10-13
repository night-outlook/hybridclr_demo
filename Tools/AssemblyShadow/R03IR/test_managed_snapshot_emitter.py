"""Execute the ACTUAL C# Report/EmitNativeReport via real .NET P/Invoke.

No Unity, IL2CPP-generated marshaller, native VM or business semantics are tested.
The original native guard-receipt producer is explicitly mocked. The writer,
slot8 bridge and C# emitter method bodies are taken directly from current files.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from snapshot_test_support import prepare, body

ROOT=Path(__file__).resolve().parents[1]
CPP=ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
CS=ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs'

class ManagedSnapshotEmitter(unittest.TestCase):
    def test_actual_csharp_emitter_and_native_pinvoke_roundtrip(self):
        dotnet=shutil.which('dotnet')
        cc=shutil.which('clang++') or shutil.which('g++')
        self.assertTrue(dotnet and cc, 'Real .NET8 SDK and C++ compiler required; no skipped fixture')
        cs=CS.read_text()
        report=body(cs,'public sealed class Report')
        emitter=body(cs,'private static bool EmitNativeReport')
        declarations=re.findall(r'\[DllImport\("__Internal", CallingConvention = CallingConvention.Cdecl\)\]\s*private static extern int R03_IR_Report(?:Open|Int|Text|Seal)\([^;]*;',cs)
        self.assertEqual(len(declarations),4)
        native=prepare(CPP,CS).split('struct Report {',1)[0]
        program='''using System;
using System.IO;
using System.Runtime.InteropServices;
public static class Program {
'''+report+'\n'+'\n'.join(declarations)+'\n'+emitter+r'''
[DllImport("__Internal", CallingConvention=CallingConvention.Cdecl)]
private static extern int R03_IR_ObserveOldGuardIntoSnapshot();
public static int Main(string[] a) {
 if(a.Length!=4)return 90;
 IntPtr library=NativeLibrary.Load(a[0]);
 NativeLibrary.SetDllImportResolver(typeof(Program).Assembly,(name,asm,path)=>name=="__Internal"?library:IntPtr.Zero);
 string mode=a[3];
 Report r=new Report {
  result=mode=="semantic-failed"?"Failed":"Passed",runId="synthetic-managed-wire-only",
  caseId=mode,requestSha256=new string('a',64),stimulus=mode=="baseline"?"baseline-owner":"type-resolution",
  unityVersion="2022.3.62f2",platform="OSXPlayer",initialState=6,poisonedState=9,finalState=9,
  nativeStimulusReturn=1,preActiveReflection=42,preActiveDelegate=42,preCanaryCount=1,finalCanaryCount=1,
  preShadowField=2,finalShadowField=2,shadowFieldReadable=true,prePositive=true,
  activeReflectionAttempted=true,activeDelegateAttempted=true,aotReflectionAttempted=true,
  activeReflectionException="SyntheticDenied",activeDelegateException="SyntheticDenied",aotReflectionException="SyntheticDenied",
  firstRecovery="{\"stateCode\":9}",finalRecovery="{\"stateCode\":9}",finalDiagnostics="{\"stateCode\":9}",
  finalExecutionDiagnostics=File.ReadAllText(a[2]),recoveryStable=true,fixedDiagnosticsReadable=true,
  nativePhase=910,terminalReportingProbeMask=15,reserveGcProbeMask=31,acceptance=false,
  error="quote\" slash\\ newline\n \u4e2d\u6587"
 };
 if(mode=="off"){
  r.stimulus="off";r.initialState=r.poisonedState=r.finalState=0;
  r.terminalReportingProbeMask=r.reserveGcProbeMask=0;r.finalCanaryCount=2;
 }
 if(R03_IR_ReportOpen(a[1])!=1)return 91;
 if(mode=="baseline"&&R03_IR_ObserveOldGuardIntoSnapshot()!=1)return 92;
 if(mode=="duplicate"&&R03_IR_ReportText(0,"first")!=1)return 93;
 bool ok=EmitNativeReport(r);
 Console.WriteLine(Environment.ProcessId);
 return ok?0:5;
}
}
'''
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve(strict=True)
            lib=root/('libwriter.dylib' if sys.platform=='darwin' else 'libwriter.so')
            src=root/'writer.cpp';src.write_text(native)
            flags=['-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread']
            flags+=['-dynamiclib'] if sys.platform=='darwin' else ['-shared','-fPIC']
            p=subprocess.run([cc,*flags,str(src),'-o',str(lib)],capture_output=True,timeout=45)
            self.assertEqual(p.returncode,0,p.stderr.decode(errors='replace'))
            (root/'Program.cs').write_text(program)
            (root/'Emitter.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems><Nullable>disable</Nullable></PropertyGroup><ItemGroup><Compile Include="Program.cs" /></ItemGroup></Project>')
            p=subprocess.run([dotnet,'build',str(root/'Emitter.csproj'),'--nologo','--disable-build-servers','-p:UseSharedCompilation=false'],capture_output=True,timeout=90)
            self.assertEqual(p.returncode,0,(p.stdout+p.stderr).decode(errors='replace')[-6000:])
            # Explicit synthetic structured input is deliberately larger than
            # one backing slice. This is not N's missing historical diagnostic.
            item={'logicalAssembly':'mscorlib','typeKey':'Synthetic.ShortType','executionModeCode':0,
                  'executionMode':'AotBaseline','physicalImageKind':'Aot','isActive':True,
                  'cctorStarted':False,'cctorFinished':True,'hasInitializationException':False,
                  'staticStoragePointer':'','pointerDetailsAvailable':False,'staticStorageAvailable':False}
            data=json.dumps({'classes':[item]*1024},separators=(',',':'))
            self.assertGreater(len(data),262144)
            inputfile=root/'diagnostic.json';inputfile.write_text(data)
            dll=root/'bin/Debug/net8.0/Emitter.dll'
            for mode in ('baseline','type','off','semantic-failed','duplicate'):
                with self.subTest(mode=mode):
                    output=root/(mode+'.json')
                    p=subprocess.run([dotnet,str(dll),str(lib),str(output),str(inputfile),mode],capture_output=True,timeout=45)
                    self.assertEqual(p.returncode,5 if mode=='duplicate' else 0,p.stderr.decode(errors='replace'))
                    if mode=='duplicate':
                        self.assertEqual(output.stat().st_size,0)
                        self.assertIn(b'reason=7 ',p.stderr)
                        continue
                    raw=json.loads(output.read_bytes())
                    self.assertEqual(raw['finalExecutionDiagnostics'],data)
                    self.assertEqual(raw['processId'],int(p.stdout.strip()))
                    self.assertEqual(raw['error'],'quote" slash\\ newline\n 中文')
                    self.assertEqual(raw['result'],'Failed' if mode=='semantic-failed' else 'Passed')
                    self.assertFalse(raw['acceptance'])
                    if mode=='baseline':self.assertEqual(json.loads(raw['nativeGuardJson'])['caughtOldGuard'],1)
                    else:self.assertIsNone(raw['nativeGuardJson'])

if __name__=='__main__':unittest.main()
