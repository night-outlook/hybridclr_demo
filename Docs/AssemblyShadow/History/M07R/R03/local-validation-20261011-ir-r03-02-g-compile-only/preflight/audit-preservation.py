from pathlib import Path
import json,hashlib,subprocess,datetime,concurrent.futures
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRCompile-20261011G-canonical-temp');W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');pins=json.loads((P/'SYNC_AUTHORITY.json').read_text())['pins'];branch='codex/assembly-shadow-r01b-h1'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
start=now();j=json.loads((P/'INSTALLED_SDK_BEFORE.json').read_text());root=Path(j['root']);actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()};assert actual=={r['path'] for r in j['files']}
for r in j['files']:
 p=root/r['path'];assert p.stat().st_size==r['size'] and sha(p)==r['sha256'],p
inputs=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text())['tools']
for r in inputs:assert sha(r['path'])==r['sha256'] and str(Path(r['path']).resolve())==r['resolved']
managed=P.parent/'ManagedAPI-R03IRCompile-20261011G-canonical-temp/build-api/inputs.json';tracked=[]
if managed.exists():
 for r in json.loads(managed.read_text())['files']:
  assert sha(r['path'])==r['sha256'],r;tracked.append(r)
record={'state':'Passed','startUtc':start,'endUtc':now(),'files':len(j['files']),'bytes':j['bytes'],'beforeInventorySha256':sha(P/'INSTALLED_SDK_BEFORE.json'),'exactRosterUnchanged':True,'allCapturedToolsUnchanged':True,'managedCompilerInputsUnchanged':len(tracked),'tools':inputs,'unityLaunches':0,'vendorBytesUploaded':False};(P/'INSTALLED_SDK_AFTER_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
def verify(n):
 repo=W/n;values={};rows=[]
 for key,args in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('origin',['remote','get-url','origin']),('remoteHead',['ls-remote','origin','refs/heads/'+branch])]:
  a=now();x=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=60);assert x.returncode==0;rows.append({'argv':['git','-C',str(repo),*args],'startUtc':a,'endUtc':now(),'exitCode':x.returncode,'stdout':x.stdout,'stderr':x.stderr});values[key]=x.stdout.strip()
 assert values['head']==pins[n]==values['remoteHead'].split()[0] and values['top']==str(repo) and values['branch']==branch and not values['status'] and values['origin']=='git@github.com:night-outlook/'+n+'.git'
 return {'repository':n,'path':str(repo),'values':values,'commands':rows}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(verify,pins))
(P/'FINAL_SOURCE_AUTHORITY.json').write_text(json.dumps({'state':'Passed','recordedUtc':now(),'pins':pins,'repositories':rows,'sourceChanged':False},indent=2)+'\n');print(json.dumps(record))
