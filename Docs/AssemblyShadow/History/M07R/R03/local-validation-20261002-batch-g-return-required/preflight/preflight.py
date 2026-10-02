import datetime,hashlib,json,os,pathlib,plistlib,subprocess
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261002G-producer');R=P.parent/'R03LocalBatch-20261002G-producer';branch='codex/assembly-shadow-r01b-h1';expected={pathlib.Path(r['path']).name:r['expected'] for r in json.loads((P/'preflight-before-sync.json').read_text())['repositories']};records=[]
def command(cmd,env=None):
 s=datetime.datetime.now(datetime.timezone.utc).isoformat();x=subprocess.run(cmd,capture_output=True,text=True,env=env);records.append({'command':cmd,'startUtc':s,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':x.returncode,'stdout':x.stdout,'stderr':x.stderr});assert x.returncode==0,records[-1];return x.stdout.strip()
def git(p,*args):return command(['git','-C',str(p),*args])
for name,h in expected.items():
 p=W/name;assert git(p,'status','--porcelain=v1','--untracked-files=all')=='';assert git(p,'rev-parse','FETCH_HEAD')==h
 git(p,'merge','--ff-only','FETCH_HEAD');assert git(p,'rev-parse','--show-toplevel')==str(p) and git(p,'branch','--show-current')==branch and git(p,'rev-parse','HEAD')==h and git(p,'status','--short')=='';git(p,'remote','-v');git(p,'worktree','list','--porcelain');assert git(p,'ls-remote','origin','refs/heads/'+branch).split()[0]==h
assert git(D,'log','-1','--format=%H','--','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md')==expected['hybridclr_demo']
git(D,'merge-base','--is-ancestor','53e6e559165344cb98405a7261a988871157a864',expected['hybridclr_demo']);git(D,'diff','--exit-code','53e6e559165344cb98405a7261a988871157a864',expected['hybridclr_demo'],'--','.',':!Docs/AssemblyShadow');delta=git(D,'diff','--name-only','53e6e559165344cb98405a7261a988871157a864',expected['hybridclr_demo']);assert not R.exists()
sdk='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';unity='/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity';assert pathlib.Path(unity).is_file();bcl=pathlib.Path(unity).parents[1]/'MonoBleedingEdge/lib/mono/unityaot-macos/mscorlib.dll';assert hashlib.sha256(bcl.read_bytes()).hexdigest()=='d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83';env=os.environ.copy();env.update({'PATH':sdk+':'+env['PATH'],'DOTNET_ROOT':sdk,'DOTNET_ROOT_ARM64':sdk,'DOTNET_MULTILEVEL_LOOKUP':'0','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp'})
assert command([sdk+'/dotnet','--version'],env)=='8.0.318';dotnetinfo=command([sdk+'/dotnet','--info'],env);version=plistlib.loads(pathlib.Path(unity).parents[1].joinpath('Info.plist').read_bytes());assert version['CFBundleVersion']=='2022.3.62f2',version
versions={'macOS':command(['sw_vers']),'machine':command(['uname','-m']),'python':command(['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','--version']),'clang':command(['clang','--version']),'sdk':command(['xcrun','--sdk','macosx','--show-sdk-version']),'powershell':command(['pwsh','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()']),'dotnetInfo':dotnetinfo,'unityVersion':version['CFBundleVersion'],'unityPath':unity,'dotnetPath':sdk+'/dotnet','disk':command(['df','-h',str(P)]),'memory':command(['vm_stat'])}
ps=command(['ps','-axo','pid=,ppid=,comm=']);(P/'process-state.txt').write_text(ps+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
prior=json.loads((P.parent/'Preflight-R03LocalBatch-20261002F-runtime/prior-evidence-custody.json').read_text())
for name in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','evidence.tar.gz','seal-receipt.json']:
 p=P.parent/'R03LocalBatch-20261002F-runtime'/name;prior[str(p)]=sha(p)
checkpoint=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261002-batch-f-return-required'
for line in (checkpoint/'MANIFEST.sha256').read_text().splitlines():
 h,n=line.split('  ',1);p=checkpoint/n;assert sha(p)==h;prior[str(p)]=h
prior[str(checkpoint/'MANIFEST.sha256')]=sha(checkpoint/'MANIFEST.sha256')
for n,h in prior.items():assert sha(pathlib.Path(n))==h,n
(P/'prior-evidence-custody.json').write_text(json.dumps(prior,indent=2)+'\n');(P/'environment.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':versions,'sourceAnchor':'53e6e559165344cb98405a7261a988871157a864','docsOnlyDelta':delta.splitlines(),'expected':expected,'batchRootUnused':True,'priorCustodyFiles':len(prior)},indent=2)+'\n');(P/'preflight-commands.json').write_text(json.dumps(records,indent=2)+'\n')
for name in ['README.md','Handoff/WEB_TO_LOCAL.md','Plan/CURRENT_STATUS.md']:
 p=D/'Docs/AssemblyShadow'/name;out=p.read_text();(P/('read-'+name.replace('/','-'))).write_text(out);print('Read and retained',name)
print('PREFLIGHT PASSED',len(prior),'preserved evidence bindings')
