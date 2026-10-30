from pathlib import Path
import os,json,subprocess,hashlib,datetime,plistlib,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261026-oneuse-D';T=D/'Tools/AssemblyShadow/R03IR';U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk')
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((B/'oneuse-D-PRESERVATION_BEFORE-20261029.json').read_text())['protectedOriginalSFiles']==16978 and not O.exists()
assert json.loads((B/'oneuse-D-CI_GENERATOR_GATE-20261029.json').read_text())['actualGeneratorGatePassed'] is True
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1');env['PATH']=str(SDK)+os.pathsep+env['PATH'];records=[]
for argv in [[str(SDK/'dotnet'),'--list-sdks'],[str(SDK/'dotnet'),'--list-runtimes'],[str(SDK/'dotnet'),'--info'],['clang++','--version'],['lipo','-archs',str(U)],['python3','--version']]:
 start=now();r=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=60);assert r.returncode==0;records.append(dict(argv=argv,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
assert records[0]['stdout'].startswith('8.0.318 ') and 'Microsoft.NETCore.App 8.0.21 ' in records[1]['stdout'] and 'osx-arm64' in records[2]['stdout'] and records[4]['stdout'].strip()=='arm64'
assert plistlib.loads((U.parent.parent/'Info.plist').read_bytes())['CFBundleShortVersionString']=='Unity version 2022.3.62f2'
free=shutil.disk_usage(B).free
q=B/'oneuse-D-ENVIRONMENT_BEFORE.json';assert not q.exists();q.write_text(json.dumps(dict(time=now(),PATH=env['PATH'],processOnlyPATH=True,TMPDIR=env.get('TMPDIR'),commands=records,dotnet=str(SDK/'dotnet'),dotnetSha256=sha(SDK/'dotnet'),Unity2022=str(U),unitySha256=sha(U),capacityBytes=free,advisory40GiBAvailable=free>=40*1024**3,installPerformed=False),indent=2)+'\n')
args=['--workspace',str(W),'--original-s',str(S),'--unity',str(U),'--demo-commit','b6076f8d85ba1ac56bfe15656842eb37115d1475','--output',str(O)]
def run(name,script,timeout):
 argv=['python3','-B',str(T/script),*args];so=B/('oneuse-D-'+name+'.stdout.log');se=B/('oneuse-D-'+name+'.stderr.log');start=now()
 marker=B/('oneuse-D-'+name+'-INVOCATION.json')
 with marker.open('x') as f:json.dump(dict(argv=argv,cwd=str(D),start=start,once=True,envPATH=env['PATH']),f,indent=2);f.write('\n')
 with so.open('xb') as f,se.open('xb') as g:
  p=subprocess.Popen(argv,cwd=D,env=env,stdout=f,stderr=g,start_new_session=True);pid=p.pid;code=p.wait(timeout=timeout)
 row=dict(argv=argv,cwd=str(D),start=start,end=now(),pid=pid,exit=code,stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se),capacityAfterBytes=shutil.disk_usage(B).free)
 q=B/('oneuse-D-'+name+'-COMMAND.json');assert not q.exists();q.write_text(json.dumps(row,indent=2)+'\n');print(name,'EXIT',code,flush=True);return row
ad=run('readmission','current_native_environment_admission.py',900)
if ad['exit']!=0:
 print('STOP: readmission failed; coordinator NotRun',flush=True);raise SystemExit(0)
parsed=json.loads(Path(ad['stdout']).read_text());assert parsed['result']=='PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun' and not O.exists()
assert parsed['standaloneCurrentNativeCli']['result']=='PassedFreshPythonProcessHelp_NoUnityOrRuntime' and parsed['standaloneCurrentNativeCli']['pythonPathProvided'] is False
if min(free,parsed['capacity']['freeBytes'],ad['capacityAfterBytes'])<40*1024**3:
 (B/'oneuse-D-ADVISORY_STOP.json').write_text(json.dumps(dict(reason='Below40GiB requires Primary go/no-go',coordinatorInvoked=False),indent=2)+'\n');print('STOP: advisory40GiB gate; request Primary decision',flush=True);raise SystemExit(0)
run('coordinator','run_current_native_validation_cycle.py',43200)
print('Single coordinator invocation completed; no retry',flush=True)
