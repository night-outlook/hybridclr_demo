from pathlib import Path
import subprocess,concurrent.futures,json,datetime,os,hashlib
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'e1334d1052dba9ad240a3fa781b751ec5a1d9e9d','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'0fa7b4fef94062e54f186fda938dd8a3d2304b7e'};ops=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(p,*args):
 start=now();r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True,timeout=180);ops.append({'argv':['git','-C',str(p),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
def inspect(n):
 p=W/n;v={k:git(p,*a) for k,a in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('remotes',['remote','-v']),('origin',['remote','get-url','origin']),('worktrees',['worktree','list','--porcelain']),('submodules',['submodule','status','--recursive']),('remoteHead',['ls-remote','origin','refs/heads/'+branch])]};assert v['top']==str(p) and v['branch']==branch and not v['status'] and v['origin']=='git@github.com:night-outlook/'+n+'.git' and v['remoteHead'].split()[0]==pins[n];return {'repository':n,'path':str(p),'values':v}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:before=list(pool.map(inspect,pins))
roots=[B/n for n in ['Preflight-R03K-after-J-41bc','ManagedAPI-R03K-after-J-41bc','NativeSDK-R03K-after-J-41bc','Scratch-R03K-after-J-41bc','R03IRLocal-K-after-J-41bc','StorageCheck-R03IRLocal-K-after-J-41bc','Storage-R03IRLocal-K-after-J-41bc']]
for r in roots:
 assert not r.exists() and r.resolve()==r and not any(p.is_symlink() for p in [r,*r.parents]);assert not r.is_relative_to(W) and not W.is_relative_to(r)
for r in before:
 n=r['repository'];p=W/n
 if r['values']['head']!=pins[n]:
  git(p,'merge-base','--is-ancestor',r['values']['head'],pins[n]);git(p,'merge','--ff-only',pins[n])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:after=list(pool.map(inspect,pins))
assert all(r['values']['head']==pins[r['repository']] for r in after)
D=W/'hybridclr_demo';manifest=json.loads((D/'Tools/AssemblyShadow/R03/source-pins.json').read_text());assert all(manifest[n]==pins[n] for n in pins if n!='hybridclr_demo')
assert git(D,'diff','df88f6dcee93c5caab7ed4fbd040657ddbf10f6f',pins['hybridclr_demo'],'--','Assets','Packages','ProjectSettings','Tools')==''
P=roots[0];P.mkdir();record={'state':'Passed','recordedUtc':now(),'pins':pins,'branch':branch,'before':before,'after':after,'commands':ops,'rootsAbsentAndNonaliasingBefore':list(map(str,roots)),'onlyPreflightCreated':str(P),'sourcePinsSha256':hashlib.sha256((D/'Tools/AssemblyShadow/R03/source-pins.json').read_bytes()).hexdigest(),'userAuthorizedPinCorrection':{'originalDemo':'ae0b8bd0c0896955f861d9753916c94f7f322472','governingDemo':pins['hybridclr_demo'],'directUserReply':'Use e1334d1052dba9ad240a3fa781b751ec5a1d9e9d as the final K demo pin; other pins unchanged','delta':'Documentation only, including official SDK and host CI audit addenda; executable anchor unchanged'},'executableAnchor':'df88f6dcee93c5caab7ed4fbd040657ddbf10f6f','noResetStashCleanOrProtocolChange':True}
(P/'SOURCE_AUTHORITY.json').write_text(json.dumps(record,indent=2)+'\n');(P/'source-authority.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'state':'Passed','pins':pins,'onlyPreflightCreated':str(P)}),flush=True)
