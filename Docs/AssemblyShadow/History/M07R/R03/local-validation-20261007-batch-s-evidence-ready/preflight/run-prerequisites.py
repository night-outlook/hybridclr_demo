"""Fresh explicitly authorized S prerequisites after operator storage remediation."""
from pathlib import Path
import subprocess,json,os,datetime,hashlib,re
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');UNITY=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');PIN='29bb3d4a39bf8a2f23be404f77535aaba3485bfc';branch='codex/assembly-shadow-r01b-h1';ssh=json.loads((P/'SSH_POLICY.json').read_text())['sshCommand'];env={**os.environ,'EXPECTED_DEMO_COMMIT':PIN,'DOTNET_ROOT':str(SDK),'DOTNET_ROOT_ARM64':str(SDK),'DOTNET_MULTILEVEL_LOOKUP':'0','PATH':str(SDK)+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp','GIT_SSH_COMMAND':ssh,'GIT_TERMINAL_PROMPT':'0'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,record):
 with (P/name).open('x') as f:json.dump(record,f,indent=2);f.write('\n')
rows=[]
def cmd(label,args,timeout=None):
 folder=P/'operations'/label;folder.mkdir(parents=True);start=utc();argv=list(map(str,args))
 with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:r=subprocess.run(argv,cwd=D,env=env,stdout=out,stderr=err,timeout=timeout)
 row={'label':label,'argv':argv,'cwd':str(D),'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log')};(folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(label,'exit',r.returncode,flush=True);return r.returncode,(folder/'stdout.log').read_text().strip()
start=utc();state='PrerequisiteBlocked';error=None
save('EXECUTION_AUTHORIZATION.json',{'recordedUtc':start,'userResponses':['disk space avaliable, continue LocalValidation','continue'],'pendingQuestion':'Which exact demo commit should bind the fresh S execution? Use pushed 29bb3d4a39bf8a2f23be404f77535aaba3485bfc or wait for updated Primary handoff.','interpretation':'Continue authorizes the proposed current pushed Local documentation descendant; no source or pin substitution.','demoCommit':PIN,'primarySourceCommit':'e8fda852684f584295fe37830340ab3c9f3fcc4f','oldDiagnosticPreserved':True,'newPrerequisiteRoot':str(P),'diagnosticRoot':str(BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery-2'),'executingSidecarRoot':str(BASE/'Storage-R03LocalBatch-20261007S-lr-recovery-2'),'coreRoot':str(BASE/'R03LocalBatch-20261007S-lr-recovery'),'corePreviouslyNotConstructed':True,'maximumExecutingInvocations':1,'noCoreOrPhaseRetry':True})
try:
 assert json.loads((P/'HISTORICAL_CUSTODY_BEFORE.json').read_text())['state']=='Passed';ready=json.loads((P/'READ_ONLY_READINESS.json').read_text());assert not ready['applicableInstructionPaths'] and not ready['activeUnityTargets'];assert ready['versions']['sdk-version']['value']=='8.0.318' and ready['unityVersion']=='2022.3.62f2'
 pins=json.loads((D/'Tools/AssemblyShadow/R03Completion/source-pins.json').read_text());pins={n:pins[n] for n in ['hybridclr','hybridclr_unity','il2cpp_plus']};pins={'hybridclr_demo':PIN,**pins};repos=[]
 for name,pin in pins.items():
  root=W/name
  def git(label,*args):
   code,out=cmd('source-'+name+'-'+label,['git','-C',root,*args],120);assert code==0;return out
  assert git('top','rev-parse','--show-toplevel')==str(root) and git('branch','branch','--show-current')==branch and git('status','status','--short')=='' and git('origin','remote','get-url','origin')=='git@github.com:night-outlook/'+name+'.git' and git('head','rev-parse','HEAD')==pin
  git('fetch','fetch','origin',branch);assert git('fetch-head','rev-parse','FETCH_HEAD')==pin;git('fast-forward','merge','--ff-only','FETCH_HEAD');assert git('final-head','rev-parse','HEAD')==pin and git('final-status','status','--short')=='';repos.append({'path':str(root),'branch':branch,'commit':pin,'remote':'verified'})
 assert cmd('source-anchor',['git','-C',D,'merge-base','--is-ancestor','9f27feb647bbf2d2bc82483700fe4f78e5ea60be',PIN],120)[0]==0;assert cmd('executable-delta',['git','-C',D,'diff','--exit-code','9f27feb647bbf2d2bc82483700fe4f78e5ea60be',PIN,'--','.',':!Docs/AssemblyShadow'],120)[0]==0
 settings=[]
 for rel in ['Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03Completion/source-pins.json','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/ProjectVersion.txt']:
  src=D/rel;blob=subprocess.check_output(['git','-C',str(D),'show',PIN+':'+rel]);assert src.read_bytes()==blob;copy=P/'source-settings'/rel;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(blob);settings.append({'path':str(src),'copy':str(copy),'sha256':sha(src)})
 save('SOURCE_AUTHORITY.json',{'recordedUtc':utc(),'repositories':pins,'repositoryRecords':repos,'branch':branch,'sshCommand':ssh,'sourceSettings':settings,'executableDeltaFromPrimary':'None; only Local docs/checkpoint','authorizationPath':str(P/'EXECUTION_AUTHORIZATION.json')})
 code,_=cmd('transport-preflight',['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','-B',D/'Tools/AssemblyShadow/R03Completion/transport_preflight.py','--workspace',W,'--demo-commit',PIN,'--output',BASE/'Transport-R03LocalBatch-20261007S-lr-recovery-2']);state='TransportBlocked';assert code==0;tv=json.loads((BASE/'Transport-R03LocalBatch-20261007S-lr-recovery-2/verification.json').read_text());assert tv['result']=='TransportReady' and len(tv['repositories'])==4 and all(x['result']=='Passed' for x in tv['repositories']);state='PrerequisiteBlocked'
 for label,folder,pattern,count in [('lr-tests','R03Completion','test_lr_*.py',45),('storage-tests','R03Storage','test_*.py',48)]:
  assert cmd(label,[PY,'-B','-m','unittest','discover','-s',D/('Tools/AssemblyShadow/'+folder),'-p',pattern,'-v'])[0]==0;log=(P/'operations'/label/'stderr.log').read_text();assert re.search(r'Ran '+str(count)+r' tests? in ',log) and '\nOK\n' in log and 'skipped=' not in log
 state='CapacityBlocked';check=BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery-2';code,_=cmd('storage-diagnostic',[PY,'-B',D/'Tools/AssemblyShadow/R03Storage/run_storage_checked.py','--workspace',W,'--output',BASE/'R03LocalBatch-20261007S-lr-recovery','--unity',UNITY,'--demo-commit',PIN,'--retained-q',BASE/'R03LocalBatch-20261006Q-lp-repair','--storage-evidence',check]);assert code==0;ad=json.loads((check/'admission.json').read_text());session=json.loads((check/'session.json').read_text());assert ad['state']=='Admitted' and session['state']=='Passed';state='PrerequisitesReady'
except Exception as e:error={'type':type(e).__name__,'message':str(e)}
finally:
 save('PREREQUISITE_SEQUENCE.json',{'kind':'SContinuationPrerequisiteSequence','startUtc':start,'endUtc':utc(),'state':state,'error':error,'operations':rows,'demoCommit':PIN,'batchStarted':False,'batchResult':'NotRun','oldPrerequisitesPreserved':True,'retainedRModified':False});print('Prerequisites',state,flush=True)
if state!='PrerequisitesReady':raise SystemExit(2)
