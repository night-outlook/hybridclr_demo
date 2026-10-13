from pathlib import Path
import subprocess,concurrent.futures,json,datetime,os,hashlib
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'daf5fab66aa17a9127e6aa09cbf788ec4bdf5a36','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'0f72078711d4786dac2666c9017d952d857dd041'};ops=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(p,*args):
 start=now();r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True,timeout=180);ops.append({'argv':['git','-C',str(p),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
def inspect(n):
 p=W/n;v={k:git(p,*a) for k,a in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('remotes',['remote','-v']),('origin',['remote','get-url','origin']),('worktrees',['worktree','list','--porcelain']),('submodules',['submodule','status','--recursive']),('remoteHead',['ls-remote','origin','refs/heads/'+branch])]};assert v['top']==str(p) and v['branch']==branch and not v['status'] and v['origin']=='git@github.com:night-outlook/'+n+'.git' and v['remoteHead'].split()[0]==pins[n];return {'repository':n,'path':str(p),'values':v}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:before=list(pool.map(inspect,pins))
roots=[B/n for n in ['Preflight-R03SNAP01-82bd','ManagedAPI-R03SNAP01-82bd','NativeSDK-R03SNAP01-82bd','Scratch-R03SNAP01-82bd','R03IRLocal-SNAP01-82bd','StorageCheck-R03IRLocal-SNAP01-82bd','Storage-R03IRLocal-SNAP01-82bd']]
for r in roots:
 assert not os.path.lexists(r) and r.resolve()==r and not any(p.is_symlink() for p in [r,*r.parents]);assert not r.is_relative_to(W) and not W.is_relative_to(r)
for row in before:
 n=row['repository'];p=W/n
 if row['values']['head']!=pins[n]:git(p,'merge-base','--is-ancestor',row['values']['head'],pins[n]);git(p,'merge','--ff-only',pins[n])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:after=list(pool.map(inspect,pins))
assert all(r['values']['head']==pins[r['repository']] for r in after)
D=W/'hybridclr_demo';manifest=json.loads((D/'Tools/AssemblyShadow/R03/source-pins.json').read_text());assert all(manifest[n]==pins[n] for n in pins if n!='hybridclr_demo')
assert git(D,'diff','126626c71f1571ae9a0de9f95a56b485ae9a5267',pins['hybridclr_demo'],'--','.',':(exclude)Docs')==''
assert git(D,'diff','c5b69990d650293ff2faa6ef7ba712ba2a5147a1',pins['hybridclr_demo'],'--','Tools','Assets','Packages','ProjectSettings')==''
bindings=[]
for path,blob in [('Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp','2f13925190a1576738457d8d43f3646a4c7c095f'),('Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs','598feeec3231707091699d99fbf4428d50b52024')]:
 assert git(D,'rev-parse',pins['hybridclr_demo']+':'+path)==blob;bindings.append({'path':path,'gitBlob':blob,'sha256':hashlib.sha256((D/path).read_bytes()).hexdigest()})
delta=git(D,'diff','--name-only','3138ce154b8ad1cbe7fc925522bdfec82a386dd5',pins['hybridclr_demo']).splitlines()
P=roots[0];P.mkdir();record={'state':'Passed','recordedUtc':now(),'pins':pins,'branch':branch,'before':before,'after':after,'commands':ops,'rootsAbsentAndNonaliasingBefore':list(map(str,roots)),'onlyPreflightCreated':str(P),'sourcePinsSha256':hashlib.sha256((D/'Tools/AssemblyShadow/R03/source-pins.json').read_bytes()).hexdigest(),'compiledImplementationAnchor':'c5b69990d650293ff2faa6ef7ba712ba2a5147a1','hostTestAnchor':'126626c71f1571ae9a0de9f95a56b485ae9a5267','compiledInputsByteIdentical':True,'diagnosticSourceBindings':bindings,'demoDeltaFromNPublication':delta,'nativeRuntimeUnchangedFromN':True,'noResetStashCleanOrProtocolChange':True};(P/'SOURCE_AUTHORITY.json').write_text(json.dumps(record,indent=2)+'\n');(P/'source-authority.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'state':'Passed','pins':pins,'onlyPreflightCreated':str(P)}),flush=True)
