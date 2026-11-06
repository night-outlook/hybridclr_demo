from pathlib import Path
import json,hashlib,subprocess,datetime,re,os,shutil
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';H='7da27a486b529cdebf73100b5ce4c332a1bb7e86';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (B/('initializer-02-'+n)).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
load=lambda n:json.loads((B/('initializer-02-'+n)).read_text())
runs=load('CI_RUNS.json');data=runs['structuredContent']['content'];data=json.loads(data) if isinstance(data,str) else data
if isinstance(data,dict) and 'workflow_runs' not in data:data=data.get('data',data)
run=next(x for x in data['workflow_runs'] if x['id']==42013270614)
assert run['head_sha']==H and run['path']=='.github/workflows/r03-ir-initializer-local-contracts.yml' and run['conclusion']=='success' and run['status']=='completed'
jobs=load('CI_JOBS-42013270614.json')['structuredContent']['jobs'];assert len(jobs)==2 and all(j['conclusion']=='success' and j['status']=='completed' for j in jobs)
bindings=[]
old=json.loads((B/'oneuse-K-CI_GATE.json').read_text())['sourceBindings']
new=['Tools/AssemblyShadow/R03IR/run_initializer_local.py','Tools/AssemblyShadow/R03IR/test_initializer_local_orchestration.py','Tools/AssemblyShadow/R03IR/prepare_initializer_sources.py','Tools/AssemblyShadow/R03IR/verify_initializer_observation.py','Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerPreparedProbe.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerObservationWriter.cpp','Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerObservationPlayer.cs','Tools/AssemblyShadow/R03/PlayerFixtures/InitializerNativeTargetFixtures.cs','Tools/AssemblyShadow/R03/PlayerFixtures/PlayerFixtures.csproj','Tools/AssemblyShadow/R03/PlayerFixtures/Program.cs','Tools/AssemblyShadow/R03IR/current_native_environment_admission.py','.github/workflows/r03-ir-initializer-local-contracts.yml']
new+=['Tools/AssemblyShadow/R03IR/initializer_admission_contracts.py','Tools/AssemblyShadow/R03IR/current_native_environment_contracts.py']
for repo,rel in dict.fromkeys([(x['repository'],x['path']) for x in old]+[('hybridclr_demo',x) for x in new]):
 p=W/repo/rel;blob=subprocess.check_output(['git','-C',str(W/repo),'rev-parse','HEAD:'+rel],text=True).strip();actual=subprocess.check_output(['git','-C',str(W/repo),'hash-object',str(p)],text=True).strip();assert actual==blob
 bindings.append(dict(repository=repo,path=rel,gitBlob=blob,sha256=sha(p)))
shared=next(x for x in data['workflow_runs'] if x['id']==42013270483);sharedJobs=load('CI_JOBS-42013270483.json')['structuredContent']['jobs'];assert shared['head_sha']==H and shared['path']=='.github/workflows/r03-ir-current-native-local-cycle-host.yml' and shared['conclusion']=='success' and len(sharedJobs)==2 and all(x['conclusion']=='success' and x['status']=='completed' for x in sharedJobs)
counts={str(j['id']):[int(x) for x in re.findall(r'Ran (\d+) tests?',load('CI_LOG-'+str(j['id'])+'.json')['structuredContent']['content'])] for j in jobs};assert all(v==[4,12,8,29,10,1,4] for v in counts.values())
save('CI_GATE.json',dict(kind='Initializer01ExactSourceRequiredCIGate',time=now(),head=H,result='PassedTwoExactWorkflows_FourOSJobs',workflow=run,jobs=jobs,sharedWorkflow=shared,sharedJobs=sharedJobs,requiredJobsPassed=4,hostTestCountsByJob=counts,sourceBindings=bindings,sharedWorkflowStatus='PassedBothOS_ActualFixtureAdmissionRegressionIncluded',runtimeAcceptance=False))
O=B/'R03IR-Initializer-20261105-oneuse-02';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261105-oneuse-02';fs=os.statvfs(B)
assert not O.exists() and not O.is_symlink() and O.resolve()==O and not C.exists() and not C.is_symlink() and C.resolve()==C
save('ROOTS_AND_INITIAL_CAPACITY.json',dict(time=now(),root=str(O),checkpoint=str(C),bothAbsent=True,canonicalNonaliasing=True,parent=str(B),device=os.stat(B).st_dev,freeBytes=fs.f_bavail*fs.f_frsize,freeGiB=fs.f_bavail*fs.f_frsize/1024**3,minimumGiB=25,hardGiB=20,advisoryGiB=40,df=subprocess.check_output(['/bin/df','-P',str(B)],text=True),rootCreated=False))
print('CI exact-source passed:4 OS jobs;',len(bindings),'source bindings;root absent;freeGiB',fs.f_bavail*fs.f_frsize/1024**3)
