#!/usr/bin/env python3
"""Host-only actual Player serializer/native writer tests; no Unity execution."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[4]
CS=r'''
using System;
using System.Reflection;
using System.Text.Json;
using AssemblyShadow.R03.IR;
class Check {
 static int Main() {
  var report=new R03TerminalPlayer.Report();
  int count=0;
  foreach(var f in report.GetType().GetFields()) {
   if(f.FieldType==typeof(string)) f.SetValue(report,"quote\" slash\\ newline\n nul\0 unicode\u4e2d\ud83d\ude80");
   else if(f.FieldType==typeof(bool)) f.SetValue(report,true);
   else if(f.FieldType==typeof(int)) f.SetValue(report,++count%2==0?Int32.MinValue:Int32.MaxValue);
   else throw new Exception("Unexpected report type "+f.Name);
  }
  var method=typeof(R03TerminalPlayer).GetMethod("EncodeReport",BindingFlags.Static|BindingFlags.NonPublic);
  string text=(string)method.Invoke(null,new object[]{report});
  using(var parsed=JsonDocument.Parse(text)) {
   int properties=0;foreach(var p in parsed.RootElement.EnumerateObject()) ++properties;
   if(properties!=report.GetType().GetFields().Length) throw new Exception("Missing/duplicate report field");
   foreach(var f in report.GetType().GetFields()) {
    var v=parsed.RootElement.GetProperty(f.Name);
    if(f.FieldType==typeof(string) && v.GetString()!=(string)f.GetValue(report))throw new Exception(f.Name);
    if(f.FieldType==typeof(int) && v.GetInt32()!=(int)f.GetValue(report))throw new Exception(f.Name);
    if(f.FieldType==typeof(bool) && v.GetBoolean()!=(bool)f.GetValue(report))throw new Exception(f.Name);
   }
  }
  report.error=null;
  using(var parsed=JsonDocument.Parse((string)method.Invoke(null,new object[]{report})))
   if(parsed.RootElement.GetProperty("error").ValueKind!=JsonValueKind.Null)throw new Exception("Null lost");
  Console.WriteLine("{\"result\":\"Passed\",\"actualPlayerSerializer\":true,\"extremeIntegersUnicodeControlNull\":true,\"unityRun\":false}");return 0;
 }
}
'''

def run(args,**kwargs):
    return subprocess.run(args,check=True,**kwargs)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--managed-assembly',type=Path,required=True)
    args=parser.parse_args()
    player=(ROOT/'Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs').read_text()
    assert player.count('JsonUtility.FromJson<')==1 and 'FromJson<Request>' in player
    assert 'JsonUtility.ToJson' not in player and 'error.ToString()' not in player
    assert player.count('Debug.LogException(')==1 # pre-poison canary only
    assert 'report.finalShadowField == report.preShadowField' in player
    assert 'report.preShadowField == 2' in player
    assert 'report.postReportingCode == 17' in player
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td)
        (temp/'test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup><ItemGroup><Compile Include="Check.cs"/><Reference Include="PlayerApiCompile"><HintPath>'+str(args.managed_assembly.resolve())+'</HintPath></Reference></ItemGroup></Project>')
        (temp/'Check.cs').write_text(CS)
        run(['dotnet','build',str(temp/'test.csproj'),'-c','Release','-v','minimal'])
        run(['dotnet',str(temp/'bin/Release/net8.0/test.dll')])
        source=(ROOT/'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp').read_text()
        start=source.index('extern "C" IL2CPP_EXPORT int32_t R03_IR_SaveReport(')
        end=source.index('extern "C" IL2CPP_EXPORT int32_t R03_IR_ExerciseReporting()',start)
        writer=source[start:end]
        cc=shutil.which('clang++') or shutil.which('g++');assert cc
        (temp/'native.cpp').write_text('#include <cstdint>\n#include <cstdio>\n#include <cstring>\n#include <cerrno>\n#include <fcntl.h>\n#include <unistd.h>\n#include <cassert>\n#define IL2CPP_EXPORT\n'+writer+'\nint main(int argc,char** argv){assert(argc==2);assert(R03_IR_SaveReport(argv[1],"{\\\"x\\\":1}\\n")==0);assert(R03_IR_SaveReport(argv[1],"changed")==-2);assert(R03_IR_SaveReport("relative","no")==-1);return 0;}\n')
        run([cc,'-std=c++17','-Wall','-Wextra','-Werror','-pedantic',str(temp/'native.cpp'),'-o',str(temp/'writer')])
        target=temp/'raw.json';run([str(temp/'writer'),str(target)])
        assert json.loads(target.read_text())=={'x':1}
        print(json.dumps({'result':'Passed','nativeExclusiveWriter':True,'secondWriteRejected':True,'unityRun':False}))

if __name__=='__main__':main()
