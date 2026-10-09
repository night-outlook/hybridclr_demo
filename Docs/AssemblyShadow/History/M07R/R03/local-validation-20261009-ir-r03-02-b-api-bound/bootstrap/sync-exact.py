from pathlib import Path
import json,subprocess,datetime
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/IR-R03-02-bootstrap-20261009B-api-bound');branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'434ed7ff92951881fcdc7ebbb046c900e6a1d7d2','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'9ce1c1bfec9a21b92ea300acda5f27a3815b2c37'};operations=[]
def command(r,*a):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(['git','-C',str(r),*a],capture_output=True,text=True,timeout=180);row={'argv':['git','-C',str(r),*a],'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};operations.append(row);(B/f'git-{len(operations):03d}.json').write_text(json.dumps(row,indent=2)+'\n');assert p.returncode==0,row;return p.stdout.strip()
for n,h in pins.items():
 r=W/n;assert command(r,'remote','get-url','origin')=='git@github.com:night-outlook/'+n+'.git';assert command(r,'ls-remote','origin','refs/heads/'+branch).split()[0]==h;command(r,'fetch','--no-tags','origin',branch);assert command(r,'rev-parse','FETCH_HEAD')==h;assert not command(r,'status','--short');assert command(r,'branch','--show-current')==branch;command(r,'merge-base','--is-ancestor','HEAD',h)
for n,h in pins.items():
 r=W/n
 if command(r,'rev-parse','HEAD')!=h:command(r,'merge','--ff-only',h)
 assert command(r,'rev-parse','HEAD')==h and not command(r,'status','--short')
(B/'SYNC_AUTHORITY.json').write_text(json.dumps({'state':'Passed','pins':pins,'operations':operations},indent=2)+'\n');print(json.dumps({'state':'Passed','pins':pins}))
