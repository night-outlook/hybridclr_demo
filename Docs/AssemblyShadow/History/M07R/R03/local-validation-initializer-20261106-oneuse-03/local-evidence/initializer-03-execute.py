from pathlib import Path
import os,json,hashlib,subprocess,datetime,time
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';S=B/'OriginalS-20261026-fc55-oneuse';O=B/'R03IR-Initializer-20261106-oneuse-03';T=D/'Tools/AssemblyShadow/R03IR';U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');H='7a3b6c31408d8fd8b9fb5f74d78be4fa65670915';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
def save(n,v):
 with (B/('initializer-03-'+n)).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
pre=load(B/'initializer-03-PRESERVATION_BEFORE.json');ad=load(B/'initializer-03-readmission.stdout.log');rc=load(B/'initializer-03-readmission-COMMAND.json');ci=load(B/'initializer-03-CI_GATE.json')
assert len(pre['history'])==16 and pre['protectedOriginalSFilesVerified']==16978 and pre['installedSdkFilesVerified']==2405 and rc['exit']==0 and ad['result']=='PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun' and ci['requiredJobsPassed']==4 and ci['head']==H
HR=O.with_name(O.name+'-native-host-raw');assert not HR.exists() and not HR.is_symlink() and HR.resolve()==HR
assert not O.exists() and not O.is_symlink() and O.resolve()==O and not (B/'R03IR-Initializer-20261105-oneuse-01').exists()
assert all(r['commit']==pre['sourcePins'][Path(r['path']).name] and r['remoteHeadVerified'] is True for r in ad['currentSource']['repositories'])
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1');env['PATH']=str(SDK)+os.pathsep+env['PATH'];env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
fs=os.statvfs(B);tick=time.monotonic();free=fs.f_bavail*fs.f_frsize;sample=now();first=ad['capacity']['freeBytes'];go=min(first,free)>=25*1024**3;rootcheck=load(B/'initializer-03-ROOTS_AND_INITIAL_CAPACITY.json');assert os.stat(B).st_dev==rootcheck['device']
save('IMMEDIATE_CAPACITY.json',dict(kind='IndependentImmediatePreInitializerStatvfs',time=sample,parent=str(B),device=os.stat(B).st_dev,freeBytes=free,freeGiB=free/1024**3,firstAdmissionFreeBytes=first,admissionCommandSha256=sha(B/'initializer-03-readmission-COMMAND.json'),fBavail=fs.f_bavail,fFrsize=fs.f_frsize,hardMinimumGiB=20,advisoryGiB=40,initializer03MinimumGiB=25,decision='GO' if go else 'NO-GO',bothSamplesAbove25GiB=go,initializerOnlyAdvisoryExceptionUsed=go and min(first,free)<40*1024**3,thresholdsChanged=False,cleanupPerformed=False))
if not go:
 save('NO_GO.json',dict(time=now(),result='CapacityBlocked',batch='NotRun',runnerInvocations=0,rootAbsent=not O.exists()));raise SystemExit(0)
argv=['python3','-B',str(T/'run_initializer_local.py'),'--workspace',str(W),'--original-s',str(S),'--unity',str(U),'--demo-commit',H,'--output',str(O)];so=B/'initializer-03-runner.stdout.log';se=B/'initializer-03-runner.stderr.log';start=now()
save('runner-INVOCATION.json',dict(argv=argv,cwd=str(B),start=start,once=True,rootAbsentAtDispatch=True,sourceAdmissionPassed=True,preservationPassed=True,ciFourJobsPassed=True,immediateCapacitySha256=sha(B/'initializer-03-IMMEDIATE_CAPACITY.json'),secondsFromCapacitySample=time.monotonic()-tick,processOnlyPATH=env['PATH'],TMPDIR=env.get('TMPDIR'),CXX=env.get('CXX')))
with so.open('xb') as f,se.open('xb') as g:
 proc=subprocess.Popen(argv,cwd=B,env=env,stdout=f,stderr=g,start_new_session=True)
 save('runner-PROCESS.json',dict(pid=proc.pid,pgid=os.getpgid(proc.pid),start=now(),argv=argv))
 code=proc.wait()
save('runner-COMMAND.json',dict(argv=argv,cwd=str(B),start=start,end=now(),pid=proc.pid,pgid=proc.pid,exit=code,stdout=str(so),stdoutSha256=sha(so),stderr=str(se),stderrSha256=sha(se),initializerRunnerInvocations=1,retryPerformed=False,rootConstructed=O.is_dir()))
print('Initializer oneuse-03 completed once;exit',code,flush=True);print(so.read_text()[-3500:]);print(se.read_text()[-1500:])
