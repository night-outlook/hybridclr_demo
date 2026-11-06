from pathlib import Path
import os,json,subprocess,hashlib,datetime,plistlib,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-Initializer-20261105-oneuse-02';T=D/'Tools/AssemblyShadow/R03IR';U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');H='7da27a486b529cdebf73100b5ce4c332a1bb7e86';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (B/('initializer-02-'+n)).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
assert not O.exists() and not O.is_symlink() and O.resolve()==O
assert json.loads((B/'initializer-02-CI_GATE.json').read_text())['requiredJobsPassed']==4
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1');env['PATH']=str(SDK)+os.pathsep+env['PATH'];env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None);records=[]
commands=[[str(SDK/'dotnet'),'--version'],[str(SDK/'dotnet'),'--list-sdks'],[str(SDK/'dotnet'),'--list-runtimes'],[str(SDK/'dotnet'),'--info'],['clang++','--version'],['lipo','-archs',str(U)],['python3','--version'],['git','--version'],['/bin/df','-P',str(B)]]
for argv in commands:
 start=now();r=subprocess.run(argv,cwd=B,env=env,capture_output=True,text=True,timeout=60);records.append(dict(argv=argv,start=start,end=now(),exit=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
assert records[0]['stdout'].strip()=='8.0.318' and 'Microsoft.NETCore.App 8.0.21 ' in records[2]['stdout'] and 'osx-arm64' in records[3]['stdout'] and records[5]['stdout'].strip()=='arm64';assert plistlib.loads((U.parent.parent/'Info.plist').read_bytes())['CFBundleShortVersionString']=='Unity version 2022.3.62f2'
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True);processes=[]
for line in ps.splitlines():
 p=line.strip().split(None,3)
 if len(p)==4 and any(x in p[3].split(' ',1)[0] for x in ['Unity.app','il2cpp','dotnet','clang++','bee_backend']) and any(str(q) in p[3] for q in [W,S,O]):processes.append(line)
mount=subprocess.run(['/sbin/mount'],capture_output=True,text=True,timeout=20)
volume=dict(parent=str(B),resolvedParent=str(B.resolve()),device=os.stat(B).st_dev,df=records[-1]);fs=os.statvfs(B)
save('ENVIRONMENT_BEFORE.json',dict(time=now(),commands=records,PATH=env['PATH'],processOnlyPATH=True,TMPDIR=env.get('TMPDIR'),CXX=env.get('CXX'),dotnet=str(SDK/'dotnet'),dotnetSha256=sha(SDK/'dotnet'),Unity2022=str(U),unitySha256=sha(U),volume=volume,freeBytes=fs.f_bavail*fs.f_frsize,conflictingProcesses=processes,mountCommand=dict(argv=['/sbin/mount'],exit=mount.returncode,stdout=mount.stdout,stderr=mount.stderr),UnityLaunches=0,PlayersLaunched=0,installationOrSourceChanges=False))
assert not processes and mount.returncode==0
save('CAPACITY_SECOND.json',dict(time=now(),kind='IndependentReadOnlyStatvfs_NoDispatch',parent=str(B),device=os.stat(B).st_dev,freeBytes=fs.f_bavail*fs.f_frsize,freeGiB=fs.f_bavail*fs.f_frsize/1024**3,fBavail=fs.f_bavail,fFrsize=fs.f_frsize,minimumGiB=25,hardGiB=20,advisoryGiB=40,above25GiB=fs.f_bavail*fs.f_frsize>=25*1024**3,advisoryExceptionForInitializer02Only=True,coordinatorDispatched=False))
assert fs.f_bavail*fs.f_frsize>=25*1024**3
argv=['python3','-B',str(T/'current_native_environment_admission.py'),'--workspace',str(W),'--original-s',str(S),'--unity',str(U),'--demo-commit',H,'--output',str(O)];start=now()
save('readmission-INVOCATION.json',dict(argv=argv,cwd=str(B),start=start,once=True,processOnlyPATH=env['PATH'],TMPDIR=env.get('TMPDIR'),CXX=env.get('CXX'),outputAbsentBefore=True))
so=B/'initializer-02-readmission.stdout.log';se=B/'initializer-02-readmission.stderr.log'
with so.open('xb') as f,se.open('xb') as g:
 proc=subprocess.Popen(argv,cwd=B,env=env,stdout=f,stderr=g,start_new_session=True);code=proc.wait(timeout=900)
save('readmission-COMMAND.json',dict(argv=argv,cwd=str(B),start=start,end=now(),pid=proc.pid,exit=code,stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se),rootAbsentAfter=not O.exists(),UnityLaunches=0,PlayersLaunched=0))
report=json.loads(so.read_text());print(code,report,flush=True)
if code:
 save('NO_GO.json',dict(time=now(),result='PrerequisiteBlocked',batch='NotRun',reason=report['reason'],prerequisiteExit=code,initializerRunnerInvocations=0,rootAbsent=not O.exists(),UnityLaunches=0,PlayersLaunched=0,productResult='NotRun',retryPerformed=False))
else:save('READMISSION_PASSED_PENDING_PRESERVATION.json',dict(time=now(),result=report['result'],runnerInvocations=0))
