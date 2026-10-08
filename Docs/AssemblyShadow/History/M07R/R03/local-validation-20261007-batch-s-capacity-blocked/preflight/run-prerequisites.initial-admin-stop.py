"""Prescribed prerequisite sequence only; never launches S or changes retained R."""
from pathlib import Path
import subprocess,json,os,datetime,hashlib,plistlib,re
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');UNITY=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');PIN='e8fda852684f584295fe37830340ab3c9f3fcc4f';auth=json.loads((P/'SOURCE_AUTHORITY.json').read_text());env={**os.environ,'EXPECTED_DEMO_COMMIT':PIN,'DOTNET_ROOT':str(SDK),'DOTNET_ROOT_ARM64':str(SDK),'DOTNET_MULTILEVEL_LOOKUP':'0','PATH':str(SDK)+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp','GIT_SSH_COMMAND':auth['sshCommand'],'GIT_TERMINAL_PROMPT':'0'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[]
def cmd(label,args):
 folder=P/'operations'/label;folder.mkdir(parents=True);beg=utc()
 with (folder/'stdout.log').open('xb') as out,(folder/'stderr.log').open('xb') as err:r=subprocess.run([str(a) for a in args],cwd=D,env=env,stdout=out,stderr=err)
 row={'label':label,'argv':[str(a) for a in args],'cwd':str(D),'startUtc':beg,'endUtc':utc(),'exitCode':r.returncode,'stdoutSha256':sha(folder/'stdout.log'),'stderrSha256':sha(folder/'stderr.log')};(folder/'receipt.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row);print(label,'exit',r.returncode,flush=True);return r.returncode
start=utc();state='PrerequisiteBlocked';error=None
try:
 assert UNITY.is_file() and os.access(UNITY,os.X_OK) and os.access(PY,os.X_OK);plist=UNITY.parents[1]/'Info.plist';u=plistlib.loads(plist.read_bytes());assert u['CFBundleVersion']=='2022.3.62f2';assert cmd('sdk-version',[SDK/'dotnet','--version'])==0;assert (P/'operations/sdk-version/stdout.log').read_text().strip()=='8.0.318'
 versions={}
 for label,args in [('python-version',[PY,'--version']),('macos',['sw_vers']),('architecture',['uname','-m']),('xcode',['xcodebuild','-version']),('platform-sdk',['xcrun','--show-sdk-path']),('platform-sdk-version',['xcrun','--show-sdk-version']),('clang',['xcrun','clang','--version'])]:
  assert cmd(label,args)==0;versions[label]=(P/'operations'/label/'stdout.log').read_text().strip()
 settings=[]
 for rel in ['Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03Completion/source-pins.json','Packages/manifest.json','Packages/packages-lock.json','ProjectSettings/ProjectVersion.txt']:
  src=D/rel;blob=subprocess.check_output(['git','-C',str(D),'show',PIN+':'+rel]);assert src.read_bytes()==blob;copy=P/'source-settings'/rel;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(blob);settings.append({'path':str(src),'sha256':sha(src),'copy':str(copy)})
 ps=subprocess.check_output(['ps','-axo','pid=,ppid=,args='],text=True);active=[line for line in ps.splitlines() if str(UNITY) in line and '-projectPath' in line];assert not any(str(W) in line or 'R03LocalBatch-20261007S-lr-recovery' in line or 'R03LocalBatch-20261007R-lq-storage' in line for line in active)
 (P/'ENVIRONMENT.json').write_text(json.dumps({'recordedUtc':utc(),'unityPath':str(UNITY),'unityVersion':u['CFBundleVersion'],'unityInfoPlistSha256':sha(plist),'sdkRoot':str(SDK),'sdkVersion':'8.0.318','pythonPath':PY,'platform':'StandaloneOSX arm64','versions':versions,'sourceSettings':settings,'activeUnityProjectProcesses':active,'gateState':'Prior unresolved ancillary effective-model observation unchanged; no PASS/Off or independent review claimed','environment':{k:env[k] for k in ['EXPECTED_DEMO_COMMIT','DOTNET_ROOT','DOTNET_ROOT_ARM64','DOTNET_MULTILEVEL_LOOKUP','TMPDIR','PYTHONDONTWRITEBYTECODE']},'unity6000Launched':False},indent=2)+'\n')
 assert cmd('retained-r-readonly',[PY,'-B',D/'Tools/AssemblyShadow/R03Completion/retained_transaction.py','--retained-r',BASE/'R03LocalBatch-20261007R-lq-storage','--output',BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery'])==0
 rv=json.loads((BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery/verification.json').read_text());assert rv['result']=='Passed' and rv['settingsRemainStaged'] and not rv['restorationPerformed']
 transport=cmd('transport-preflight',[PY,'-B',D/'Tools/AssemblyShadow/R03Completion/transport_preflight.py','--workspace',W,'--demo-commit',PIN,'--output',BASE/'Transport-R03LocalBatch-20261007S-lr-recovery']);tv=json.loads((BASE/'Transport-R03LocalBatch-20261007S-lr-recovery/verification.json').read_text());
 if transport!=0:state='TransportBlocked';raise RuntimeError('Four-owner transport prerequisite did not pass')
 assert tv['result']=='TransportReady' and len(tv['repositories'])==4 and all(r['result']=='Passed' for r in tv['repositories'])
 for label,folder,pattern,count in [('lr-tests','R03Completion','test_lr_*.py',45),('storage-tests','R03Storage','test_*.py',48)]:
  assert cmd(label,[PY,'-B','-m','unittest','discover','-s',D/('Tools/AssemblyShadow/'+folder),'-p',pattern,'-v'])==0;log=(P/'operations'/label/'stderr.log').read_text();assert re.search(r'Ran '+str(count)+r' tests? in ',log) and '\nOK\n' in log and 'skipped=' not in log
 code=cmd('storage-diagnostic',[PY,'-B',D/'Tools/AssemblyShadow/R03Storage/run_storage_checked.py','--workspace',W,'--output',BASE/'R03LocalBatch-20261007S-lr-recovery','--unity',UNITY,'--demo-commit',PIN,'--retained-q',BASE/'R03LocalBatch-20261006Q-lp-repair','--storage-evidence',BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery'])
 if code!=0:state='CapacityBlocked';raise RuntimeError('Fresh storage diagnostic did not admit S')
 check=BASE/'StorageCheck-R03LocalBatch-20261007S-lr-recovery';ad=json.loads((check/'admission.json').read_text());session=json.loads((check/'session.json').read_text());assert ad['state']=='Admitted' and session['state']=='Passed';state='PrerequisitesReady'
except Exception as e:error={'type':type(e).__name__,'message':str(e)}
finally:
 record={'kind':'SLocalPrerequisiteSequence','startUtc':start,'endUtc':utc(),'state':state,'error':error,'operations':rows,'batchStarted':False,'batchResult':'NotRun','batchRootExists':(BASE/'R03LocalBatch-20261007S-lr-recovery').exists(),'executingSidecarExists':(BASE/'Storage-R03LocalBatch-20261007S-lr-recovery').exists(),'sourceCommit':PIN,'retainedRModified':False};(P/'PREREQUISITE_SEQUENCE.json').write_text(json.dumps(record,indent=2)+'\n');print('Prerequisite result',state,flush=True)
if state!='PrerequisitesReady':raise SystemExit(2)
