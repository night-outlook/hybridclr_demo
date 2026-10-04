import datetime,hashlib,json,os,pathlib,plistlib,subprocess
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261004L-fixed-image');R=P.parent/'R03LocalBatch-20261004L-fixed-image';branch='codex/assembly-shadow-r01b-h1';expected={pathlib.Path(r['path']).name:r['expected'] for r in json.loads((P/'preflight-before-sync.json').read_text())['repositories']};records=[];os.environ['GIT_SSH_COMMAND']=json.loads((P/'SSH_TRANSPORT.json').read_text())['command']
def command(cmd,env=None):
 s=datetime.datetime.now(datetime.timezone.utc).isoformat();x=subprocess.run(cmd,capture_output=True,text=True,env=env);records.append({'command':cmd,'startUtc':s,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':x.returncode,'stdout':x.stdout,'stderr':x.stderr});assert x.returncode==0,records[-1];return x.stdout.strip()
def git(p,*args):return command(['git','-C',str(p),*args])
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
try:
 for name,h in expected.items():
  p=W/name;assert git(p,'rev-parse','--show-toplevel')==str(p) and git(p,'branch','--show-current')==branch and git(p,'rev-parse','HEAD')==h and git(p,'status','--porcelain=v1','--untracked-files=all')=='';git(p,'remote','-v');git(p,'worktree','list','--porcelain');git(p,'submodule','status','--recursive');assert git(p,'ls-remote','origin','refs/heads/'+branch).split()[0]==h
 assert git(D,'log','-1','--format=%H','--','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md')==expected['hybridclr_demo'];anchor='78ce9f81968a330b2801a93d4a426ffab7565b5f';git(D,'merge-base','--is-ancestor',anchor,expected['hybridclr_demo']);git(D,'diff','--exit-code',anchor,expected['hybridclr_demo'],'--','.',':!Docs/AssemblyShadow');delta=git(D,'diff','--name-only',anchor,expected['hybridclr_demo']);assert not R.exists()
 git(D,'diff','--exit-code','4abd44f1fc6f81a75c76ae4975c28dd06a80b9f8','HEAD','--','Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md')
 packageDelta=git(W/'hybridclr_unity','diff','--name-only','c86cbf665f5fcb2137e5adf2960541ce492467a4','HEAD');assert packageDelta==''
 pins=json.loads((D/'Tools/AssemblyShadow/R03Completion/source-pins.json').read_text());assert pins['branch']==branch and pins['runtimeAcceptance'] is False and pins['expansionAuthorized'] is False
 for name in ['hybridclr','hybridclr_unity','il2cpp_plus']:assert pins[name]==expected[name]
 sdk='/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk';unity='/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity';assert os.access(unity,os.X_OK);bcl=pathlib.Path(unity).parents[1]/'MonoBleedingEdge/lib/mono/unityaot-macos/mscorlib.dll';assert sha(bcl)=='d89d5124cafb873b34c2eac68d2ece41d14fec10999baf0e4620276dff54ab83';env=os.environ.copy();env.update({'PATH':sdk+':'+env['PATH'],'DOTNET_ROOT':sdk,'DOTNET_ROOT_ARM64':sdk,'DOTNET_MULTILEVEL_LOOKUP':'0','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/private/tmp'})
 assert command([sdk+'/dotnet','--version'],env)=='8.0.318';dotnetinfo=command([sdk+'/dotnet','--info'],env);version=plistlib.loads(pathlib.Path(unity).parents[1].joinpath('Info.plist').read_bytes());assert version['CFBundleVersion']=='2022.3.62f2'
 versions={'macOS':command(['sw_vers']),'machine':command(['uname','-m']),'python':command(['/Library/Frameworks/Python.framework/Versions/3.14/bin/python3','--version']),'clang':command(['clang','--version']),'sdk':command(['xcrun','--sdk','macosx','--show-sdk-version']),'powershell':command(['pwsh','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()']),'dotnetInfo':dotnetinfo,'unityVersion':version['CFBundleVersion'],'unityPath':unity,'dotnetPath':sdk+'/dotnet','disk':command(['df','-h',str(P)]),'memory':command(['vm_stat'])}
 ps=command(['ps','-axo','pid=,ppid=,comm=']);(P/'process-state.txt').write_text(ps+'\n');editors=[line for line in ps.splitlines() if 'Unity.app/Contents/MacOS/Unity' in line];assert not editors,editors
 gate=command(['pwsh','-NoProfile','-File','/Users/ah/.codex/worktrees/af52/hybridclr_demo/.agents/skills/agent-collaboration/scripts/Get-GateReviewMode.ps1']);assert gate=='Off';(P/'skill-policy.json').write_text(json.dumps({'gateMode':gate,'effectiveMainModel':'Not exposed by authoritative host; no inferred model metadata','delegation':'None; serial single-run Unity/process/custody ownership','skills':[{'path':str(f),'sha256':sha(f)} for f in [pathlib.Path('/Users/ah/.codex/worktrees/af52/hybridclr_demo/.agents/skills/agent-collaboration/SKILL.md'),pathlib.Path('/Users/ah/.codex/worktrees/af52/hybridclr_demo/.agents/skills/unity-debug/SKILL.md')]]},indent=2)+'\n')
 old=P.parent/'Preflight-R03LocalBatch-20261003K-capabilities';prior=json.loads((old/'prior-evidence-custody.json').read_text());oldR=P.parent/'R03LocalBatch-20261003K-capabilities';index=json.loads((oldR/'evidence-index.json').read_text())
 for f in index['files']:
  p=oldR/f['path'];assert sha(p)==f['sha256'];prior[str(p)]=f['sha256']
 for name,h in json.loads((old/'POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes'].items():
  p=oldR/name;assert sha(p)==h;prior[str(p)]=h
 checkpoint=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-k-return-required'
 for line in (checkpoint/'MANIFEST.sha256').read_text().splitlines():
  h,n=line.split('  ',1);p=checkpoint/n;assert sha(p)==h;prior[str(p)]=h
 prior[str(checkpoint/'MANIFEST.sha256')]=sha(checkpoint/'MANIFEST.sha256')
 for n,h in prior.items():assert sha(n)==h,n
 (P/'prior-evidence-custody.json').write_text(json.dumps(prior,indent=2)+'\n');(P/'environment.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'versions':versions,'sourceAnchor':anchor,'docsOnlyDelta':delta.splitlines(),'expected':expected,'packageChangedOnlyFourTestFiles':packageDelta.splitlines(),'batchRootUnused':True,'existingUnityEditors':editors,'priorCustodyFiles':len(prior)},indent=2)+'\n')
 for name in ['README.md','Handoff/WEB_TO_LOCAL.md','Plan/CURRENT_STATUS.md','History/M07R/R03/N_FIXED_IMAGE_REPAIR.md','History/M07R/R03/N_HOST_EVIDENCE.json','History/M07R/R03/N_VALIDATION_MATRIX.md','History/M07R/R03/K_MEASUREMENT_PROTOCOL.md','Architecture/ADR/ADR-0002-pure-interpreter-qualification-boundary.md','Handoff/LOCAL_VALIDATION.md','Handoff/RETURN_TO_WEB.md']:
  p=D/'Docs/AssemblyShadow'/name;(P/('read-'+name.replace('/','-'))).write_bytes(p.read_bytes())
 print('PREFLIGHT PASSED',len(prior),'preserved evidence bindings; exact source/tool tuple; output unused')
finally:(P/'preflight-commands.json').write_text(json.dumps(records,indent=2)+'\n')
