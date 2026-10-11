from pathlib import Path
import json,hashlib,subprocess,datetime,os,sys,plistlib
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRCompile-20261011G-canonical-temp');BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';UNITY=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');CONTENTS=UNITY.parent.parent;PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';pins=json.loads((P/'SYNC_AUTHORITY.json').read_text())['pins'];stage=sys.argv[1]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with Path(p).open('x') as f:json.dump(j,f,indent=2);f.write('\n')
def load(p):return json.loads(Path(p).read_text())
def command(label,argv,timeout=600,env_extra=None):
 root=P/'commands'/label;root.mkdir(parents=True);start=now();env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1';env.update(env_extra or {})
 with (root/'stdout.log').open('wb') as out,(root/'stderr.log').open('wb') as err:
  r=subprocess.run(list(map(str,argv)),cwd=D,env=env,stdout=out,stderr=err,timeout=timeout)
 row={'argv':list(map(str,argv)),'cwd':str(D),'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdoutPath':str(root/'stdout.log'),'stdoutSha256':sha(root/'stdout.log'),'stderrPath':str(root/'stderr.log'),'stderrSha256':sha(root/'stderr.log'),'environmentOverrides':{'PYTHONDONTWRITEBYTECODE':'1',**(env_extra or {})},'sourcePins':pins,'unityOrPlayerLaunch':False}
 save(root/'receipt.json',row);print(json.dumps({'command':label,'exitCode':r.returncode,'receipt':str(root/'receipt.json')}),flush=True);return row
def sources_clean():
 for name,h in pins.items():
  repo=W/name;assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==h and not subprocess.check_output(['git','-C',str(repo),'status','--short'],text=True).strip()
def stopped_unity():
 text=subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True);rows=[s for s in text.splitlines() if s.strip().endswith('/Unity') or s.strip().endswith('/R03Isolated')];assert not rows,rows;return rows
if stage=='host':
 sources_clean();stopped_unity();assert UNITY.is_file() and not UNITY.is_symlink();info=plistlib.loads((CONTENTS/'Info.plist').read_bytes());assert '2022.3.62f2' in str(info)
 core=CONTENTS/'Managed/UnityEngine/UnityEditor.CoreModule.dll';assert sha(core)=='e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e'
 sdk=CONTENTS/'il2cpp';assert (sdk/'libil2cpp/il2cpp-config.h').is_file() and (sdk/'external/baselib/Include').is_dir();start=now();sdkfiles=[]
 for p in sorted(sdk.rglob('*')):
  if p.is_file():sdkfiles.append({'path':str(p.relative_to(sdk)),'size':p.stat().st_size,'sha256':sha(p)})
 save(P/'INSTALLED_SDK_BEFORE.json',{'startUtc':start,'endUtc':now(),'root':str(sdk),'files':sdkfiles,'bytes':sum(x['size'] for x in sdkfiles),'classification':'Official installed Unity files read-only; vendor contents not uploaded','unityLaunches':0})
 toolpaths=[UNITY,CONTENTS/'Info.plist',core,CONTENTS/'NetCoreRuntime/dotnet',CONTENTS/'DotNetSdkRoslyn/csc.dll',Path('/Library/Developer/CommandLineTools/usr/bin/clang++')];tools=[{'path':str(p),'resolved':str(p.resolve()),'sha256':sha(p),'size':p.stat().st_size} for p in toolpaths]
 sr=[]
 files=[D/'Tools/AssemblyShadow/R03/'+Path(n) for n in []]
 for repo,rel in [('hybridclr_demo','Tools/AssemblyShadow/R03/build_api.py'),('hybridclr_demo','Tools/AssemblyShadow/R03/native_validation.py'),('hybridclr_demo','Tools/AssemblyShadow/R03/test_native_validation_scratch.py'),('hybridclr_demo','Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs'),('hybridclr_demo','Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp')]+[('il2cpp_plus','libil2cpp/vm/'+n) for n in ['Runtime.cpp','Object.cpp','Object.h','AssemblyShadow.cpp','AssemblyShadowEngineReportingProbe.cpp','AssemblyShadowTerminalReporting.h']]:
  p=W/repo/rel;raw=subprocess.check_output(['git','-C',str(W/repo),'show',pins[repo]+':'+rel]);assert raw==p.read_bytes();sr.append({'repository':repo,'commit':pins[repo],'path':rel,'gitBlob':subprocess.check_output(['git','-C',str(W/repo),'rev-parse',pins[repo]+':'+rel],text=True).strip(),'sha256':sha(p)})
 v=os.statvfs(BASE);assert v.f_bavail*v.f_frsize>20*1024**3
 save(P/'SOURCE_ENVIRONMENT.json',{'state':'Passed','recordedUtc':now(),'pins':pins,'branch':'codex/assembly-shadow-r01b-h1','unitySdkVersion':'2022.3.62f2','UnityInfo':info,'tools':tools,'sources':sr,'availableBytes':v.f_bavail*v.f_frsize,'capacityPurpose':'Compile-only scratch/digests; not runtime admission','unityLaunches':0,'playerLaunches':0,'sdkVendorFilesUploaded':False})
 commands=[];commands.append(command('environment-version',[PY,'--version']));commands.append(command('clang-version',['/usr/bin/clang++','--version']));commands.append(command('macOS-version',['/usr/bin/sw_vers']));commands.append(command('sdk-scratch-tests',[PY,'-B','-m','unittest','discover','-s',D/'Tools/AssemblyShadow/R03','-p','test_native_validation_scratch.py','-v']))
 native=W/'il2cpp_plus';tests=[('reporting', 'test_reporting.py',{}),('reporting-sanitized','test_reporting.py',{'R03_SANITIZERS':'1'}),('object-access','test_object_access.py',{}),('engine-observer','test_engine_observer.py',{}),('engine-observer-sanitized','test_engine_observer.py',{'R03_SANITIZERS':'1'})]
 for label,name,extra in tests:
  if any(r['exitCode'] for r in commands):break
  commands.append(command(label,[PY,'-B',native/'tools/r03/runtime01'/name],env_extra=extra))
 if not any(r['exitCode'] for r in commands):
  commands.append(command('policy-compile',['/usr/bin/c++','-std=c++17','-Wall','-Wextra','-Werror','-pedantic','-pthread','-I'+str(native/'libil2cpp'),native/'tools/r03/terminal_execution_tests.cpp','-o',P/'policy']))
  if commands[-1]['exitCode']==0:commands.append(command('policy-checks',[P/'policy']))
 hashes=[{'path':str(p.relative_to(native)),'sha256':sha(p)} for p in sorted((native/'tools/r03/runtime01').rglob('*')) if p.is_file()];sources_clean();stopped_unity();passed=not any(x['exitCode'] for x in commands)
 save(P/'HOST_RESULT.json',{'state':'Passed' if passed else 'Failed','commands':commands,'nativeHostSources':hashes,'policyExecutableSha256':sha(P/'policy') if (P/'policy').exists() else None,'unityExecution':False,'vmForReportingAndObserver':'Mocked; not actual Unity engine','runtimeAcceptance':False});sys.exit(0 if passed else 1)
elif stage in ['before','after']:
 if stage=='before':assert load(P/'HOST_RESULT.json')['state']=='Passed';sources_clean();stopped_unity()
 root=D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09';c=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked';row=command('custody-'+stage,[PY,'-B',root/'verify_scoped_custody.py','--checkpoint',c,'--phase',stage,'--receipt',P/('scoped-custody-'+stage+'.json')]);sys.exit(row['exitCode'])
elif stage in ['managed','native']:
 sources_clean();stopped_unity();assert load(P/'HOST_RESULT.json')['state']=='Passed';cust=load(P/'scoped-custody-before.json');assert cust['result']=='ScopedHistoricalLossStable' and cust['completeScan'] and cust['presentVerified']==339367 and cust['historicalStillMissing']==77477 and not cust['problems'];assert load(P/'IMMUTABLE_SOURCE_AUTHENTICATION.json')['state']=='Passed'
 if stage=='managed':
  output=BASE/'ManagedAPI-R03IRCompile-20261011G-canonical-temp';assert not output.exists();argv=[PY,'-B',D/'Tools/AssemblyShadow/R03/build_api.py','--workspace',W,'--unity',UNITY,'--output',output]
 else:
  m=BASE/'ManagedAPI-R03IRCompile-20261011G-canonical-temp';assert load(m/'build-api/results.json')['result']=='Passed' and load(P/'commands/managed-compile/receipt.json')['exitCode']==0
  output=BASE/'NativeSDK-R03IRCompile-20261011G-canonical-temp';scratch=BASE/'Scratch-R03IRCompile-20261011G-canonical-temp';assert not output.exists() and not scratch.exists();argv=[PY,'-B',D/'Tools/AssemblyShadow/R03/native_validation.py','--workspace',W,'--unity',UNITY,'--output',output,'--sdk-scratch',scratch]
 row=command(stage+'-compile',argv,timeout=1200);sys.exit(row['exitCode'])
else:raise ValueError(stage)
