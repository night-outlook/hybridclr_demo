from pathlib import Path
import subprocess,concurrent.futures,json,datetime,os,hashlib
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'73340fc3f2cba0a2920e18f362a59e7a89cce864','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'0f72078711d4786dac2666c9017d952d857dd041'};ops=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(p,*args):
 start=now();r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True,timeout=180);ops.append({'argv':['git','-C',str(p),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
def inspect(n):
 p=W/n;v={k:git(p,*a) for k,a in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('remotes',['remote','-v']),('origin',['remote','get-url','origin']),('worktrees',['worktree','list','--porcelain']),('submodules',['submodule','status','--recursive']),('remoteHead',['ls-remote','origin','refs/heads/'+branch])]};assert v['top']==str(p) and v['branch']==branch and not v['status'] and v['origin']=='git@github.com:night-outlook/'+n+'.git' and v['remoteHead'].split()[0]==pins[n];return {'repository':n,'path':str(p),'values':v}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:before=list(pool.map(inspect,pins))
roots=[B/n for n in ['Preflight-R03N-after-M-6f28','ManagedAPI-R03N-after-M-6f28','NativeSDK-R03N-after-M-6f28','Scratch-R03N-after-M-6f28','R03IRLocal-N-after-M-6f28','StorageCheck-R03IRLocal-N-after-M-6f28','Storage-R03IRLocal-N-after-M-6f28']]
for r in roots:
 assert not os.path.lexists(r) and r.resolve()==r and not any(p.is_symlink() for p in [r,*r.parents]);assert not r.is_relative_to(W) and not W.is_relative_to(r)
for r in before:
 n=r['repository'];p=W/n
 if r['values']['head']!=pins[n]:git(p,'merge-base','--is-ancestor',r['values']['head'],pins[n]);git(p,'merge','--ff-only',pins[n])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:after=list(pool.map(inspect,pins))
assert all(r['values']['head']==pins[r['repository']] for r in after)
D=W/'hybridclr_demo';manifest=json.loads((D/'Tools/AssemblyShadow/R03/source-pins.json').read_text());assert all(manifest[n]==pins[n] for n in pins if n!='hybridclr_demo')
delta=git(D,'diff','--name-only','6684615ef6c86ed29de12fb9218d7e092bedbbfb',pins['hybridclr_demo']).splitlines();allowed={'Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp','Tools/AssemblyShadow/R03/source-pins.json','Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs','Tools/AssemblyShadow/R03IR/test_n_guarded_receipts.py'};assert all(x in allowed or x.startswith('Docs/') for x in delta)
ci=json.loads((D/'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/M_RETURN_N_2026-10-13/EVIDENCE.json').read_text());bindings=[]
for key,repo in [('demoManaged','hybridclr_demo'),('demoOverlay','hybridclr_demo'),('demoTest','hybridclr_demo'),('nativeProduct','il2cpp_plus')]:
 r=ci['sourceChanges'][key];blob=git(W/repo,'rev-parse',pins[repo]+':'+r['path']);assert blob==r['gitBlob'];bindings.append({'repository':repo,'path':r['path'],'gitBlob':blob,'sha256':hashlib.sha256((W/repo/r['path']).read_bytes()).hexdigest()})
nd=git(W/'il2cpp_plus','diff','--name-only','c1a6876a3801a8343123977a0e230558904fd94d',pins['il2cpp_plus']).splitlines();assert set(nd)=={'.github/workflows/r03-terminal-rejection.yml','libil2cpp/vm/AssemblyShadow.cpp','tools/r03/runtime01/test_terminal_denied_trace.py'}
P=roots[0];P.mkdir();record={'state':'Passed','recordedUtc':now(),'pins':pins,'branch':branch,'before':before,'after':after,'commands':ops,'rootsAbsentAndNonaliasingBefore':list(map(str,roots)),'onlyPreflightCreated':str(P),'sourcePinsSha256':hashlib.sha256((D/'Tools/AssemblyShadow/R03/source-pins.json').read_bytes()).hexdigest(),'currentNSourceBindings':bindings,'demoDeltaFromMPublication':delta,'nativeDeltaFromM':nd,'humanPinClarification':'Earlier direct user correction Use the published 40-character pin reapplied to identical shortened HybridCLR SHA; current N handoff/procedure independently bind the same full pin, other three pins unchanged','noResetStashCleanOrProtocolChange':True};(P/'SOURCE_AUTHORITY.json').write_text(json.dumps(record,indent=2)+'\n');(P/'source-authority.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'state':'Passed','pins':pins,'onlyPreflightCreated':str(P)}),flush=True)
