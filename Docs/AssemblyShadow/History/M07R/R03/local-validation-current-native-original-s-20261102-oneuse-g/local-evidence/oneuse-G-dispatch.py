from pathlib import Path
import os,json,subprocess,hashlib,datetime,plistlib,shutil,time
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-G';T=D/'Tools/AssemblyShadow/R03IR';U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');H='6364dbc795eabc8cfbb7409fcfe2b64a30c12863';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
assert json.loads((B/'oneuse-G-PRESERVATION_BEFORE.json').read_text())['protectedOriginalSFilesVerified']==16978 and not O.exists()
assert json.loads((B/'oneuse-G-CI_GATE.json').read_text())['requiredJobsPassed']==18
assert not (B/'R03IR-CurrentNativeOriginalS-20261102-oneuse-F').exists()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1');env['PATH']=str(SDK)+os.pathsep+env['PATH'];records=[]
commands=[[str(SDK/'dotnet'),'--version'],[str(SDK/'dotnet'),'--list-sdks'],[str(SDK/'dotnet'),'--list-runtimes'],[str(SDK/'dotnet'),'--info'],['clang++','--version'],['lipo','-archs',str(U)],['python3','--version'],['git','--version'],['/bin/df','-P',str(B)]]
for argv in commands:
 start=now();r=subprocess.run(argv,cwd=D,env=env,capture_output=True,text=True,timeout=60);assert r.returncode==0;records.append(dict(argv=argv,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
assert records[0]['stdout'].strip()=='8.0.318' and '8.0.318 ' in records[1]['stdout'] and 'Microsoft.NETCore.App 8.0.21 ' in records[2]['stdout'] and 'osx-arm64' in records[3]['stdout'] and records[5]['stdout'].strip()=='arm64';assert plistlib.loads((U.parent.parent/'Info.plist').read_bytes())['CFBundleShortVersionString']=='Unity version 2022.3.62f2'
volume=dict(parent=str(B),stDev=os.stat(B).st_dev,dfCommand=records[-1],resolvedParent=str(B.resolve()))
processes=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True);conflicts=[]
for line in processes.splitlines():
 p=line.strip().split(None,3)
 if len(p)==4 and any(x in p[3].split(' ',1)[0] for x in ['Unity.app','il2cpp','dotnet','clang++']) and any(str(q) in p[3] for q in [W,S,O]):conflicts.append(line)
assert not conflicts
save(B/'oneuse-G-ENVIRONMENT_BEFORE.json',dict(time=now(),PATH=env['PATH'],processOnlyPATH=True,TMPDIR=env.get('TMPDIR'),CXX=env.get('CXX'),commands=records,dotnet=str(SDK/'dotnet'),dotnetSha256=sha(SDK/'dotnet'),Unity2022=str(U),unitySha256=sha(U),capacityBytes=shutil.disk_usage(B).free,actualVolume=volume,conflictingProcesses=conflicts,installPerformed=False,hardMinimumGiB=20,advisoryGiB=40,primaryOneUseGMinimumGiB=39,capacityDecisionSourceSha256=sha(D/'Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md')))
args=['--workspace',str(W),'--original-s',str(S),'--unity',str(U),'--demo-commit',H,'--output',str(O)]
def run(name,script,timeout):
 argv=['python3','-B',str(T/script),*args];so=B/f'oneuse-G-{name}.stdout.log';se=B/f'oneuse-G-{name}.stderr.log';start=now();save(B/f'oneuse-G-{name}-INVOCATION.json',dict(argv=argv,cwd=str(D),start=start,once=True,envPATH=env['PATH']))
 with so.open('xb') as f,se.open('xb') as g:
  proc=subprocess.Popen(argv,cwd=D,env=env,stdout=f,stderr=g,start_new_session=True);pid=proc.pid;code=proc.wait(timeout=timeout)
 record=dict(argv=argv,cwd=str(D),start=start,end=now(),pid=pid,exit=code,stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se),capacityAfterBytes=shutil.disk_usage(B).free);save(B/f'oneuse-G-{name}-COMMAND.json',record);print(name,'EXIT',code,flush=True);return record
ad=run('readmission','current_native_environment_admission.py',900)
if ad['exit']!=0:
 save(B/'oneuse-G-NO_GO.json',dict(reason='ReadOnlyAdmissionFailed',coordinatorInvocations=0,rootAbsent=not O.exists()));raise SystemExit(0)
parsed=json.loads(Path(ad['stdout']).read_text());assert parsed['result']=='PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun' and not O.exists() and parsed['standaloneCurrentNativeCli']['result']=='PassedFreshPythonProcessHelp_NoUnityOrRuntime' and parsed['standaloneCurrentNativeCli']['pythonPathProvided'] is False
assert parsed['capacity']['hardMinimumGiB']==20 and parsed['capacity']['advisoryHeadroomGiB']==40 and os.stat(B).st_dev==volume['stDev']
# No tools, compilation, source changes or long waits between independent statvfs and dispatch.
fs=os.statvfs(B);free=fs.f_bavail*fs.f_frsize;sampleUtc=now();sampleTick=time.monotonic();minimum=39*1024**3;go=parsed['capacity']['freeBytes']>=minimum and free>=minimum
save(B/'oneuse-G-IMMEDIATE_CAPACITY.json',dict(kind='IndependentImmediatePreCoordinatorStatvfs',time=sampleUtc,parent=str(B),stDev=os.stat(B).st_dev,dfVolumeIdentity=volume['dfCommand']['stdout'],fBavail=fs.f_bavail,fFrsize=fs.f_frsize,freeBytes=free,freeGiB=free/1024**3,admissionBytes=parsed['capacity']['freeBytes'],admissionReceiptSha256=sha(Path(ad['stdout'])),hardMinimumGiB=20,advisoryGiB=40,primaryOneUseGMinimumGiB=39,bothSamplesAtLeast39GiB=go,advisoryExceptionUsed=go and min(free,parsed['capacity']['freeBytes'])<40*1024**3,decision='GO' if go else 'NO-GO',authority='Exact source-pinned WEB_TO_LOCAL section4 and closing Primary handoff; G only',thresholdsChanged=False,cleanupPerformed=False))
if not go:
 save(B/'oneuse-G-NO_GO.json',dict(reason='FreshAdmissionOrImmediateSampleBelow39GiB',coordinatorInvocations=0,rootAbsent=not O.exists()));print('NO-GO: reserved G root remains absent',flush=True);raise SystemExit(0)
save(B/'oneuse-G-DISPATCH_JOIN.json',dict(time=now(),secondsSinceIndependentSample=time.monotonic()-sampleTick,rootAbsent=not O.exists(),sameParentDevice=os.stat(B).st_dev==volume['stDev'],coordinatorInvocationsBeforeDispatch=0,admissionPassed=True,ciNineWorkflowsEighteenJobsPassed=True,primaryConditionalCapacityGo=True))
run('coordinator','run_current_native_validation_cycle.py',43200)
print('One G outcome completed; no retry',flush=True)
