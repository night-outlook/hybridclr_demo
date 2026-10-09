from pathlib import Path
import json,subprocess,datetime
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');P=Path(__file__).resolve().parent;branch='codex/assembly-shadow-r01b-h1';pins={'hybridclr_demo':'fca2fdb035512fc739693641a5fa2126e4254258','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'9ce1c1bfec9a21b92ea300acda5f27a3815b2c37'};records=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(name,args):
 start=now();root=W/name;r=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=120);record={'repositoryPath':str(root),'argv':['git','-C',str(root),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};records.append(record);(P/('git-'+str(len(records)).zfill(3)+'.json')).write_text(json.dumps(record,indent=2)+'\n');assert r.returncode==0,r.stderr;return r.stdout.strip()
for name,pin in pins.items():
 assert run(name,['remote','get-url','origin'])=='git@github.com:night-outlook/'+name+'.git';assert not run(name,['status','--porcelain=v1','--untracked-files=all']);assert run(name,['branch','--show-current'])==branch;assert run(name,['ls-remote','origin','refs/heads/'+branch]).split()[0]==pin
 run(name,['fetch','origin',branch]);assert run(name,['rev-parse','FETCH_HEAD'])==pin;run(name,['merge-base','--is-ancestor','HEAD',pin])
for name,pin in pins.items():
 assert not run(name,['status','--porcelain=v1','--untracked-files=all']);run(name,['merge','--ff-only',pin]);assert run(name,['rev-parse','HEAD'])==pin;assert not run(name,['status','--porcelain=v1','--untracked-files=all'])
with (P/'SYNC_AUTHORITY.json').open('x') as f:json.dump({'state':'Passed','recordedUtc':now(),'workspace':str(W),'branch':branch,'repositories':pins,'operations':records,'credentialProtocolConfigurationChanged':False},f,indent=2);f.write('\n')
print('Four exact remote heads and clean fast-forwards verified',json.dumps(pins),flush=True)
