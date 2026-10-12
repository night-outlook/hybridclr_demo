"""Compile/run the actual .NET factory lease, not a fake Unity build."""
import hashlib,json,os,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CS=ROOT/'R03/PlayerProject/R03Build.cs'
PROGRAM=r'''
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using AssemblyShadow.R03.Editor;
internal interface IModule {
 object CreateBuildPostprocessor(); string TargetName { get; }
 int RefAction(ref int value); void Fail();
}
internal sealed class MarkerException : Exception { }
internal sealed class Module : IModule {
 public int Factories; public string TargetName { get { return "osx"; } }
 public object CreateBuildPostprocessor(){++Factories;return new object();}
 public int RefAction(ref int value){value+=7;return value;}
 public void Fail(){throw new MarkerException();}
}
internal static class Test {
 static int checks;
 static void Check(bool value){++checks;if(!value)throw new Exception("check "+checks);}
 static void Main(){
  var module=new Module();var map=new Hashtable();map["osx"]=module;
  var captured=new List<object>();string failed=null;
  var lease=new R03ModuleFactoryLease(map,"osx",typeof(IModule),captured.Add,e=>failed=e);
  var proxy=(IModule)map["osx"];Check(!ReferenceEquals(proxy,module));
  var a=proxy.CreateBuildPostprocessor();var b=proxy.CreateBuildPostprocessor();
  Check(module.Factories==2);Check(captured.Count==2);
  Check(ReferenceEquals(a,captured[0])&&ReferenceEquals(b,captured[1]));
  Check(!ReferenceEquals(a,b));Check(proxy.TargetName=="osx");
  int value=3;Check(proxy.RefAction(ref value)==10&&value==10);
  bool threw=false;try{proxy.Fail();}catch(MarkerException){threw=true;}Check(threw);
  Check(failed==null);
  bool nested=false;try{new R03ModuleFactoryLease(map,"osx",typeof(IModule),captured.Add,e=>{});}catch(InvalidOperationException){nested=true;}Check(nested);
  lease.Dispose();Check(lease.Restored&&ReferenceEquals(map["osx"],module));
  lease.Dispose();Check(ReferenceEquals(map["osx"],module));
  var second=new R03ModuleFactoryLease(map,"osx",typeof(IModule),o=>{throw new Exception("capture");},e=>failed=e);
  Check(((IModule)map["osx"]).CreateBuildPostprocessor()!=null&&module.Factories==3);
  Check(failed=="System.Exception");second.Dispose();Check(second.Restored);
  var third=new R03ModuleFactoryLease(map,"osx",typeof(IModule),captured.Add,e=>{});
  object concurrent=new Module();map["osx"]=concurrent;bool conflict=false;
  try{third.Dispose();}catch(InvalidOperationException){conflict=true;}
  Check(conflict&&!third.Restored&&ReferenceEquals(map["osx"],concurrent));
  map["osx"]=module;
  bool bad=false;try{new R03ModuleFactoryLease(map,"bad",typeof(IModule),captured.Add,e=>{});}catch(InvalidOperationException){bad=true;}Check(bad);
  Console.WriteLine("{\"result\":\"Passed\",\"checks\":"+checks+",\"actualFactoryLease\":true,\"UnityBuild\":false}");
 }
}
'''

class FactoryObservationTests(unittest.TestCase):
    def test_exact_factory_forwarder_and_restoration(self):
        dotnet=shutil.which('dotnet');self.assertIsNotNone(dotnet,'dotnet required; no skipped factory test')
        source=CS.read_text();start=source.index('    public class R03ModuleFactoryForwarder')
        end=source.index('    // L observation of actual original factory returns;',start)
        body=source[start:end]
        self.assertNotIn('GetBuildPostProcessor(',source)
        self.assertIn('factoryLease.Restored',source)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td).resolve();(p/'FactoryTests.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework><OutputType>Exe</OutputType><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup></Project>')
            (p/'Factory.cs').write_text('using System;using System.Collections;using System.Reflection;using System.Linq;namespace AssemblyShadow.R03.Editor {\n'+body+'\n}')
            (p/'Program.cs').write_text(PROGRAM)
            r=subprocess.run([dotnet,'run','--project',str(p/'FactoryTests.csproj'),'--configuration','Release'],capture_output=True,text=True,timeout=120)
            self.assertEqual(r.returncode,0,r.stdout+'\n'+r.stderr)
            line=next(s for s in r.stdout.splitlines() if s.startswith('{"result"'))
            data=json.loads(line);self.assertEqual(data['result'],'Passed');self.assertGreaterEqual(data['checks'],17)
            print(json.dumps({'result':'Passed','factorySourceSha256':hashlib.sha256(body.encode()).hexdigest(),'checks':data['checks'],'UnityBuild':False}))
if __name__=='__main__':unittest.main()
