#!/usr/bin/env python3
"""Execute the unchanged actual C# emitter through real host .NET UTF-8 P/Invoke.

The Unity Start method, virtual dispatch guards, GC and real IL2CPP marshaller
are NOT simulated as passing. Report inputs and the native guard producer are
explicit synthetic fixtures. Every subprocess runs once in a fresh process.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from run_cpp import body

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    require(out.is_absolute() and out == out.resolve(strict=False), 'Canonical absolute output required')
    require(not out.exists() and not out.is_symlink() and out.parent.is_dir(), 'Fresh output required')
    require(HERE.parents[3] not in out.parents, 'External output required')
    out.mkdir()
    cpp = ROOT/'R03/PlayerProject/AssemblyShadowR03Probe.cpp'
    cs = ROOT/'R03IR/PlayerProject/R03TerminalPlayer.cs'
    source, managed = cpp.read_text(), cs.read_text()
    fragment = source[source.index('namespace r03_ir_snapshot {'):source.index('extern "C" IL2CPP_EXPORT void R03_IR_Exit')]
    header = '''#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#define IL2CPP_EXPORT
'''
    # Test-only shim; the actual R03_ObserveMethod/AssemblyShadow/Unity are NOT
    # replaced with an assertion that a real guard passed. Only slot ownership
    # and exact native->wire bytes are exercised in this host experiment.
    shim = '''
extern "C" int R03HostWriteGuard()
{
    return R03_IR_ReportText(8, "{\\\"available\\\":true,\\\"activeGuard\\\":1,\\\"baselineGuard\\\":0,\\\"caughtOldGuard\\\":1,\\\"stateCode\\\":9}");
}
'''
    # Match the declaration's UTF-8 string attributes; don't guess ANSI charset.
    declarations = []
    for name in ('R03_IR_ReportOpen', 'R03_IR_ReportInt', 'R03_IR_ReportText', 'R03_IR_ReportSeal'):
        pattern = r'\[DllImport\("__Internal", CallingConvention = CallingConvention\.Cdecl\)\]\s*private static extern int ' + name + r'\([^;]*?\);'
        matches = re.findall(pattern, managed)
        require(len(matches) == 1, 'Exact original P/Invoke declaration missing: '+name)
        declarations.append(matches[0])
    emitter = body(managed, 'private static bool EmitNativeReport')
    report = body(managed, 'public sealed class Report')
    require('return ok && R03_IR_ReportSeal() == 1;' in emitter, 'Unexpected emitter source; review first')
    program = '''using System;
using System.Reflection;
using System.Runtime.InteropServices;
static class Program {
'''+report+'\n'+'\n'.join(declarations)+'\n'+emitter+'''
[DllImport("__Internal", CallingConvention = CallingConvention.Cdecl)]
static extern int R03HostWriteGuard();
static void Check(bool ok) { if (!ok) throw new Exception("Host assertion failed"); }
static int Main(string[] args) {
    string mode=args[0], path=args[1];
    IntPtr library=NativeLibrary.Load(args[2]);
    NativeLibrary.SetDllImportResolver(typeof(Program).Assembly,
        (name, assembly, search) => name=="__Internal" ? library : IntPtr.Zero);
    var r=new Report {
        result="Passed",runId="00112233445566778899aabbccddeeff",caseId="host",
        requestSha256=new string('a',64),stimulus=mode=="baseline"?"baseline-owner":"type-resolution",
        unityVersion="2022.3.62f2",platform="OSXPlayer", initialState=6,poisonedState=9,finalState=9,
        nativeStimulusReturn=1,preActiveReflection=42,preActiveDelegate=42,
        preCanaryCount=1,finalCanaryCount=1,preShadowField=2,finalShadowField=2,
        nativePhase=910,terminalReportingProbeMask=15,reserveGcProbeMask=31,
        shadowFieldReadable=true,prePositive=true,activeReflectionAttempted=true,
        activeDelegateAttempted=true,aotReflectionAttempted=true,recoveryStable=true,fixedDiagnosticsReadable=true,
        activeReflectionException="ManagedExceptionCaught",activeDelegateException="ManagedExceptionCaught",
        aotReflectionException="ManagedExceptionCaught",firstRecovery="{\\\"stateCode\\\":9}",
        finalRecovery="{\\\"stateCode\\\":9}",finalDiagnostics="{\\\"stateCode\\\":9}",
        finalExecutionDiagnostics="{\\\"classes\\\":[]}"
    };
    if(mode=="off") {
        r.stimulus="off";r.initialState=r.poisonedState=r.finalState=0;
        r.reserveGcProbeMask=r.terminalReportingProbeMask=0;r.finalCanaryCount=2;
    }
    if(mode=="at-limit") r.finalExecutionDiagnostics=new string('x',262144);
    if(mode=="over-limit") r.finalExecutionDiagnostics=new string('x',262145);
    if(mode=="supported-producer-size") r.finalExecutionDiagnostics=new string('x',331078);
    if(mode=="unicode") r.error="quotes\\\" backslash\\\\ newline\\n 中文";
    if(mode=="failed-semantic") { r.result="Failed";r.failurePhase=220; }
    Check(R03_IR_ReportOpen(path)==1);
    if(mode=="baseline") Check(R03HostWriteGuard()==1);
    if(mode=="duplicate-native-guard") {Check(R03HostWriteGuard()==1);Check(R03HostWriteGuard()==-1);}
    bool ok=EmitNativeReport(r);
    bool expected=mode!="over-limit" && mode!="supported-producer-size" && mode!="duplicate-native-guard";
    Check(ok==expected);
    Console.WriteLine("HOST_ASSERTIONS_PASSED");
    return 0;
}
}
'''
    (out/'native.cpp').write_text(header+fragment+shim)
    (out/'Program.cs').write_text(program)
    (out/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>\n')
    (out/'Host.csproj').write_text('''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>
<ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable>
<EnableNETAnalyzers>false</EnableNETAnalyzers><UseSharedCompilation>false</UseSharedCompilation>
</PropertyGroup></Project>\n''')
    cc = shutil.which('clang++') or shutil.which('g++')
    dotnet = shutil.which('dotnet')
    require(cc and dotnet, 'C++17 and .NET8 SDK required')
    records=[]
    env=dict(os.environ, DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
    def run(command, tag):
        p=subprocess.run(command,cwd=out,env=env,capture_output=True,timeout=120)
        (out/(tag+'.stdout')).write_bytes(p.stdout)
        (out/(tag+'.stderr')).write_bytes(p.stderr)
        records.append({'argv':command,'cwd':str(out),'exit':p.returncode,
                        'stdoutSha256':hashlib.sha256(p.stdout).hexdigest(),
                        'stderrSha256':hashlib.sha256(p.stderr).hexdigest()})
        require(p.returncode==0, tag+': '+p.stderr.decode(errors='replace')[-4000:])
        return p
    library=out/('libsnapshot.dylib' if os.uname().sysname=='Darwin' else 'libsnapshot.so')
    run([cc,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-fPIC','-shared',
         str(out/'native.cpp'),'-o',str(library)],'native-compile')
    run([dotnet,'restore',str(out/'Host.csproj'),'--configfile',str(out/'NuGet.Config'),
         '--disable-parallel'],'managed-restore')
    run([dotnet,'build',str(out/'Host.csproj'),'-c','Release','--no-restore',
         '--disable-build-servers','-m:1','-p:UseSharedCompilation=false'],'managed-compile')
    dll=out/'bin/Release/net8.0/Host.dll'
    modes=('baseline','type','off','unicode','failed-semantic','at-limit','over-limit',
           'supported-producer-size','duplicate-native-guard')
    for mode in modes:
        raw=out/(mode+'.json')
        p=run([dotnet,str(dll),mode,str(raw),str(library)],mode)
        require(b'HOST_ASSERTIONS_PASSED' in p.stdout,'Host fixture did not complete')
        if mode in ('over-limit','supported-producer-size','duplicate-native-guard'):
            require(raw.stat().st_size==0,'Failed store acquired semantic bytes')
            lines=[x for x in p.stderr.splitlines() if x.startswith(b'[R03SnapshotFailure]')]
            require(len(lines)==1,'Single immutable first-failure required')
            require(b'reason='+ (b'7' if mode=='duplicate-native-guard' else b'9')+b' ' in lines[0], 'Specific first failure')
        else:
            result=json.loads(raw.read_text())
            require(result['result']==('Failed' if mode=='failed-semantic' else 'Passed'),'Result was changed')
            require(result['acceptance'] is False,'Acceptance promoted')
            if mode=='baseline':require(json.loads(result['nativeGuardJson'])['caughtOldGuard']==1,'Guard bytes lost')
            if mode=='at-limit':require(len(result['finalExecutionDiagnostics'])==262144,'Bound changed')
            if mode=='unicode':require('中文' in result['error'],'UTF-8 was corrupted')
    result={'result':'Passed','modeCount':len(modes),'records':records,
            'sourceCppSha256':hashlib.sha256(cpp.read_bytes()).hexdigest(),
            'sourceCsSha256':hashlib.sha256(cs.read_bytes()).hexdigest(),
            'emitter':'Actual unchanged C# method and original DllImport declarations; host .NET8 marshaling',
            'producerAndVm':'Synthetic reports and native guard shim; not actual Unity/IL2CPP guards',
            'UnityLaunched':False,'IL2CPPMarshallerExecuted':False,'NRootCauseProven':False,'runtimeAcceptance':False}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

if __name__=='__main__':
    main()
