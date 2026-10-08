"""Read-only environment, retained transaction and transport inventory; no batch dispatch."""
from pathlib import Path
import subprocess,json,os,datetime,hashlib,plistlib
P=Path(__file__).resolve().parent;BASE=P.parent;W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';PY='/Library/Frameworks/Python.framework/Versions/3.14/bin/python3';SDK=Path('/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk');UNITY=Path('/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity');inv=json.loads((P/'CONTINUATION_INVENTORY.json').read_text());ssh=json.loads((P/'SSH_POLICY.json').read_text())['sshCommand'];env={**os.environ,'GIT_SSH_COMMAND':ssh,'GIT_TERMINAL_PROMPT':'0','DOTNET_ROOT':str(SDK),'DOTNET_ROOT_ARM64':str(SDK),'DOTNET_MULTILEVEL_LOOKUP':'0','PATH':str(SDK)+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp'}
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[]
def command(label,args):
 f=P/'operations'/label;f.mkdir(parents=True);start=utc();argv=list(map(str,args))
 with (f/'stdout.log').open('xb') as out,(f/'stderr.log').open('xb') as err:r=subprocess.run(argv,cwd=D,env=env,stdout=out,stderr=err,timeout=120)
 record={'argv':argv,'cwd':str(D),'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdoutSha256':sha(f/'stdout.log'),'stderrSha256':sha(f/'stderr.log')};(f/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');rows.append(record);return r.returncode,(f/'stdout.log').read_text().strip()
versions={}
for label,args in [('python-version',[PY,'--version']),('sdk-version',[SDK/'dotnet','--version']),('macos',['sw_vers']),('architecture',['uname','-m']),('xcode',['xcodebuild','-version']),('platform-sdk',['xcrun','--show-sdk-path']),('platform-sdk-version',['xcrun','--show-sdk-version']),('clang',['xcrun','clang','--version'])]:
 code,value=command(label,args);assert code==0 or label=='xcode';versions[label]={'state':'Passed' if not code else 'Unavailable','value':value}
assert versions['sdk-version']['value']=='8.0.318';u=plistlib.loads((UNITY.parents[1]/'Info.plist').read_bytes());assert u['CFBundleVersion']=='2022.3.62f2' and os.access(UNITY,os.X_OK)
remotes=[]
for repo in inv['repositories']:
 code,value=command('remote-tip-'+repo['repository'],['git','-C',repo['path'],'ls-remote','origin','refs/heads/'+repo['branch']]);assert code==0 and value.split()==[repo['head'],'refs/heads/'+repo['branch']];remotes.append({'path':repo['path'],'head':repo['head'],'remote':'verified','pointInTimeOnly':True})
code,_=command('retained-r-readonly',[PY,'-B',D/'Tools/AssemblyShadow/R03Completion/retained_transaction.py','--retained-r',BASE/'R03LocalBatch-20261007R-lq-storage','--output',BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery-2']);assert code==0
rv=json.loads((BASE/'RetainedR-R03LocalBatch-20261007S-lr-recovery-2/verification.json').read_text());assert rv['result']=='Passed' and rv['settingsRemainStaged'] and not rv['restorationPerformed']
configs=[]
for root in [W,*[Path(x['path']) for x in inv['repositories']]]:
 for name in ['AGENTS.md','CLAUDE.md']:
  for parent in [root,*root.parents]:
   path=parent/name
   if path.exists() and str(path) not in configs:configs.append(str(path))
ps=subprocess.check_output(['ps','-axo','pid=,args='],text=True);active=[{'pid':line.strip().split()[0],'target':'Owning workspace or retained R/S'} for line in ps.splitlines() if str(UNITY) in line and '-projectPath' in line and (str(W) in line or 'R03LocalBatch-20261007S-lr-recovery' in line or 'R03LocalBatch-20261007R-lq-storage' in line)];assert not active
record={'kind':'ReadOnlyContinuationReadiness','recordedUtc':utc(),'versions':versions,'unityVersion':u['CFBundleVersion'],'unityPath':str(UNITY),'unityInfoPlistSha256':sha(UNITY.parents[1]/'Info.plist'),'unityLaunched':False,'sdkOnlyRoot':str(SDK),'unity6000Launched':False,'remoteTips':remotes,'retainedR':rv,'applicableInstructionPaths':configs,'activeUnityTargets':active,'executionCommitPending':True,'operations':rows}
(P/'READ_ONLY_READINESS.json').write_text(json.dumps(record,indent=2)+'\n');print('Read-only environment, exact current remote tips and retained R Passed; execution commit pending',flush=True)
