from h_common import *
import plistlib,re
clean_sources();no_unity();assert load(P/'G_EQUIVALENCE.json')['state']=='Passed';assert load(P/'ORIGINAL_INPUT_PREFLIGHT.json')['state']=='Passed';assert UNITY.is_file() and os.access(UNITY,os.X_OK) and plistlib.loads((UNITY.parent.parent/'Info.plist').read_bytes())['CFBundleVersion']=='2022.3.62f2';assert SDK.is_dir()
records=[]
try:
 for label,args in [('dotnet-info',[SDK/'dotnet','--info']),('dotnet-version',[SDK/'dotnet','--version']),('python-version',[PY,'--version']),('clang-version',['/usr/bin/c++','--version']),('macos-version',['/usr/bin/sw_vers']),('sdk-path',['/usr/bin/xcrun','--show-sdk-path']),('sdk-version',['/usr/bin/xcrun','--show-sdk-version'])]:
  r=command(label,args);records.append(r);assert r['exitCode']==0
 assert (P/'commands/dotnet-version/stdout.log').read_text().strip()=='8.0.318'
 save(P/'SOURCE_ENVIRONMENT.json',{'state':'Passed','recordedUtc':now(),'pins':pins,'branch':'codex/assembly-shadow-r01b-h1','unityVersion':'2022.3.62f2','unityExecutable':str(UNITY),'unityExecutableSha256':sha(UNITY),'python':PY,'dotnetSdkOnlyRoot':str(SDK),'dotnetVersion':'8.0.318','dotnetExecutableSha256':sha(SDK/'dotnet'),'toolCommands':records.copy(),'globalPathOrTempChanged':False,'unity6000Launched':False,'existingSDKOnlyPolicy':'Same SDK-only .NET8.0.318 documented in E; per-command env only','unityLaunches':0})
 suites=[('scratch-tests',D/'Tools/AssemblyShadow/R03','test_native_validation_scratch.py',20),('ir-host-tests',D/'Tools/AssemblyShadow/R03IR','test_*.py',65),('c-custody-tests',hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09','test_scoped_custody.py',25),('retained-e-tests',hist/'IR_Remediation/IR_RUNTIME_01_2026-10-10','test_retained_e.py',9)]
 counts=[]
 for label,path,pattern,count in suites:
  r=command(label,[PY,'-B','-m','unittest','discover','-s',path,'-p',pattern,'-v']);records.append(r);assert r['exitCode']==0
  text=(P/'commands'/label/'stderr.log').read_text();assert re.search(r'Ran '+str(count)+r' tests?',text) and text.rstrip().endswith('OK') and 'skipped' not in text;counts.append({'suite':label,'Passed':count,'Failed':0,'Errors':0,'Skipped':0,'receipt':str(P/'commands'/label/'receipt.json')})
 native=W/'il2cpp_plus'
 for label,name,extra in [('reporting','test_reporting.py',{}),('reporting-sanitized','test_reporting.py',{'R03_SANITIZERS':'1'}),('object-access','test_object_access.py',{}),('engine-observer','test_engine_observer.py',{}),('engine-observer-sanitized','test_engine_observer.py',{'R03_SANITIZERS':'1'})]:
  r=command(label,[PY,'-B',native/'tools/r03/runtime01'/name],extra=extra);records.append(r);assert r['exitCode']==0
  out=(P/'commands'/label/'stdout.log').read_text();assert json.loads(out.splitlines()[-1])['result']=='Passed'
 r=command('policy-compile',['/usr/bin/c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread','-I'+str(native/'libil2cpp'),native/'tools/r03/terminal_execution_tests.cpp','-o',P/'policy']);records.append(r);assert r['exitCode']==0
 r=command('policy-checks',[P/'policy']);records.append(r);assert r['exitCode']==0 and load(P/'commands/policy-checks/stdout.log')['checks']==69
 clean_sources();no_unity();save(P/'HOST_RESULT.json',{'state':'Passed','recordedUtc':now(),'suites':counts,'nativePolicyChecks':69,'hostCommands':records,'nativeReportingAndObserver':'Actual production sources with mocked VM dependencies; not Unity runtime','ObjectHeader':'Actual Object.h access controls','unityLaunches':0,'runtimeAcceptance':False});print('I host prerequisites Passed',flush=True)
except BaseException as e:
 save(P/'HOST_RESULT.json',{'state':'Failed','recordedUtc':now(),'error':type(e).__name__+': '+str(e),'commands':records,'remainingHostChecks':'NotRun after first failure','unityLaunches':0});raise
