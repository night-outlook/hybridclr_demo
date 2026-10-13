from pathlib import Path
import subprocess,concurrent.futures,json,datetime,os,hashlib
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'34727adcd4296fefb0d814d2030fbd1cfb581cfe','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'c1a6876a3801a8343123977a0e230558904fd94d'};ops=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(p,*args):
 start=now();r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True,timeout=180);ops.append({'argv':['git','-C',str(p),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
def inspect(n):
 p=W/n;v={k:git(p,*a) for k,a in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('remotes',['remote','-v']),('origin',['remote','get-url','origin']),('worktrees',['worktree','list','--porcelain']),('submodules',['submodule','status','--recursive']),('remoteHead',['ls-remote','origin','refs/heads/'+branch])]};assert v['top']==str(p) and v['branch']==branch and not v['status'] and v['origin']=='git@github.com:night-outlook/'+n+'.git' and v['remoteHead'].split()[0]==pins[n];return {'repository':n,'path':str(p),'values':v}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:before=list(pool.map(inspect,pins))
roots=[B/n for n in ['Preflight-R03M-after-L-73bc','ManagedAPI-R03M-after-L-73bc','NativeSDK-R03M-after-L-73bc','Scratch-R03M-after-L-73bc','R03IRLocal-M-after-L-73bc','StorageCheck-R03IRLocal-M-after-L-73bc','Storage-R03IRLocal-M-after-L-73bc']]
for r in roots:
 assert not r.exists() and r.resolve()==r and not any(p.is_symlink() for p in [r,*r.parents]);assert not r.is_relative_to(W) and not W.is_relative_to(r)
for r in before:
 n=r['repository'];p=W/n
 if r['values']['head']!=pins[n]:
  git(p,'merge-base','--is-ancestor',r['values']['head'],pins[n]);git(p,'merge','--ff-only',pins[n])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:after=list(pool.map(inspect,pins))
assert all(r['values']['head']==pins[r['repository']] for r in after)
D=W/'hybridclr_demo';manifest=json.loads((D/'Tools/AssemblyShadow/R03/source-pins.json').read_text());assert all(manifest[n]==pins[n] for n in pins if n!='hybridclr_demo')
assert git(D,'diff','04a3cd93663f9a4e877a5524d9c22ee5a3fe0131',pins['hybridclr_demo'],'--','Assets','Packages','ProjectSettings','Tools',':(exclude)Tools/AssemblyShadow/R03/test_batch_contract.py')==''
assert git(D,'rev-parse',pins['hybridclr_demo']+':Tools/AssemblyShadow/R03/test_batch_contract.py')=='dc58b0ab95e1f3f5b595abfbbd04e100a41047e1'
assert git(D,'rev-parse',pins['hybridclr_demo']+':Tools/AssemblyShadow/R03/build_provenance.py')=='4a9ba7240ded6ad81bcc29ada489ed26cbc2ae50'
delta=git(D,'diff','--name-only','329040279d18aa053e3af23b962e608b34c6b01f',pins['hybridclr_demo']).splitlines()
assert all(x.startswith('Docs/') or x=='Tools/AssemblyShadow/R03/test_batch_contract.py' or (x.startswith('.github/workflows/') and 'inventory' in x.lower()) for x in delta),delta
P=roots[0];P.mkdir();record={'state':'Passed','recordedUtc':now(),'pins':pins,'branch':branch,'before':before,'after':after,'commands':ops,'rootsAbsentAndNonaliasingBefore':list(map(str,roots)),'onlyPreflightCreated':str(P),'sourcePinsSha256':hashlib.sha256((D/'Tools/AssemblyShadow/R03/source-pins.json').read_bytes()).hexdigest(),'executableAnchor':'04a3cd93663f9a4e877a5524d9c22ee5a3fe0131','noResetStashCleanOrProtocolChange':True}
(P/'SOURCE_AUTHORITY.json').write_text(json.dumps(record,indent=2)+'\n');(P/'source-authority.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'state':'Passed','pins':pins,'onlyPreflightCreated':str(P)}),flush=True)
