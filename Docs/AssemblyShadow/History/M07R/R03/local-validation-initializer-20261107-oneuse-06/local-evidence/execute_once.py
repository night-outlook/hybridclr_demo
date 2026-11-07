from pathlib import Path
import json,hashlib,subprocess,datetime,os,time
R=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-Initializer06');B=R.parent;W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';O=B/'R03IR-Initializer-20261107-oneuse-06';HR=O.with_name(O.name+'-native-host-raw');S=B/'OriginalS-20261026-fc55-oneuse';SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');U=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H='611ad2e45a92ebfbd07cb64238bf2f47b5aff626'
def save(name,obj):
 with (R/name).open('x') as f:json.dump(obj,f,indent=2);f.write('\n')
assert not (R/'runner-INVOCATION.json').exists() and not (R/'runner-COMMAND.json').exists()
ci=load(R/'CI.json')
assert len(ci['runs'])==3
for run in ci['runs']:
 assert run['head_sha']==H and (run['status'],run['conclusion'])==('completed','success')
 jobs=ci['jobs'][str(run['id'])]['jobs']
 assert len(jobs)==2
 for os_name in ('macos-15','ubuntu-24.04'):
  [job]=[j for j in jobs if os_name in j['name']]
  assert (job['status'],job['conclusion'])==('completed','success')
secondary=load(R/'SECONDARY_COMPILE_EQUIVALENCE.json')
assert secondary['freshDemo']==H and len(secondary['verifiedInputs'])==32
assert load(R/'PRESERVATION_BEFORE.json')['result']=='PassedRemainingProtectedInputs_Exact17RetiredRemainUnavailable'
c=load(R/'SCOPED_C_BEFORE.json');assert c['result']=='ScopedHistoricalLossStable' and c['completeScan'] and c['presentVerified']==339367 and c['historicalStillMissing']==77477 and c['originalStrictCustody']=='Blocked'
ad=load(R/'ADMISSION.json');assert ad['capacity']['freeBytes']>=26843545600 and ad['result']=='PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun'
pair=[load(R/f'CAPACITY_{i}.json') for i in [1,3]];assert all(p['capacity']['freeBytes']>=26843545600 and p['bothFreshRootsAbsent'] for p in pair) and pair[0]['device']==pair[1]['device']==B.stat().st_dev and (datetime.datetime.fromisoformat(pair[1]['timeUtc'])-datetime.datetime.fromisoformat(pair[0]['timeUtc'])).total_seconds()>=60
assert not O.exists() and not HR.exists() and not O.is_symlink() and not HR.is_symlink() and O.resolve()==O and HR.resolve()==HR
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==H and not subprocess.check_output(['git','-C',str(D),'status','--short'],text=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1');env['PATH']=str(SDK)+os.pathsep+env['PATH'];env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
net=subprocess.run([str(SDK/'dotnet'),'--version'],capture_output=True,text=True,cwd=B,env=env,timeout=30);assert net.returncode==0 and net.stdout.strip()=='8.0.318';save('DOTNET_SELECTED_VERSION.json',{'command':[str(SDK/'dotnet'),'--version'],'exitCode':net.returncode,'stdout':net.stdout,'stderr':net.stderr,'timeUtc':now(),'processOnlyPATH':env['PATH']})
fs=os.statvfs(B);free=fs.f_bavail*fs.f_frsize;tick=time.monotonic();save('IMMEDIATE_CAPACITY.json',{'timeUtc':now(),'parent':str(B),'device':B.stat().st_dev,'freeBytes':free,'freeGiB':free/1024**3,'mandatoryGiB':25,'hardGiB':20,'advisoryGiB':40,'decision':'GO' if free>=26843545600 else 'NO-GO','twoIndependentSamplesAlsoPassed':True});assert free>=26843545600
a=['python3','-B',str(D/'Tools/AssemblyShadow/R03IR/run_initializer_local.py'),'--workspace',str(W),'--original-s',str(S),'--unity',str(U),'--demo-commit',H,'--output',str(O)];start=now();save('runner-INVOCATION.json',{'command':a,'startUtc':start,'cwd':str(B),'once':True,'productAndHostRootsAbsentAtDispatch':True,'allSixCiJobsPassedAtSource':H,'remainingCustodyPassed':True,'exact17OwnerRetiredUnavailable':True,'completeOriginalCScanPassed':True,'secondsFromImmediateCapacity':time.monotonic()-tick,'processOnlyPATH':env['PATH'],'TMPDIR':env.get('TMPDIR'),'CXX':env.get('CXX')})
with (R/'runner.stdout.log').open('xb') as so,(R/'runner.stderr.log').open('xb') as se:
 p=subprocess.Popen(a,cwd=B,env=env,stdout=so,stderr=se,start_new_session=True);save('runner-PROCESS.json',{'pid':p.pid,'pgid':os.getpgid(p.pid),'startUtc':now(),'command':a});print('Dispatched oneuse06 once;PID',p.pid,flush=True);code=p.wait()
save('runner-COMMAND.json',{'command':a,'cwd':str(B),'startUtc':start,'endUtc':now(),'pid':p.pid,'pgid':p.pid,'exitCode':code,'stdout':str(R/'runner.stdout.log'),'stdoutSha256':sha(R/'runner.stdout.log'),'stderr':str(R/'runner.stderr.log'),'stderrSha256':sha(R/'runner.stderr.log'),'runnerInvocations':1,'retryPerformed':False,'productRootConstructed':O.is_dir()});print('oneuse06 finished;exit',code,flush=True);print((R/'runner.stdout.log').read_text()[-2000:]);print((R/'runner.stderr.log').read_text()[-1500:])
