from h_common import *
import concurrent.futures
clean_sources();no_unity();branch='codex/assembly-shadow-r01b-h1'
def verify(n):
 repo=W/n;ops=[]
 def read(*a):
  start=now();r=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,timeout=180);ops.append({'argv':['git','-C',str(repo),*a],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
 top=read('rev-parse','--show-toplevel');b=read('branch','--show-current');h=read('rev-parse','HEAD');status=read('status','--short');origin=read('remote','get-url','origin');remote=read('ls-remote','origin','refs/heads/'+branch).split()[0]
 assert top==str(repo) and b==branch and h==remote==pins[n] and len(h)==40 and not status and origin=='git@github.com:night-outlook/'+n+'.git'
 return {'repository':n,'path':str(repo),'branch':b,'HEAD':h,'remoteHead':remote,'status':status,'commands':ops}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:repos=list(pool.map(verify,pins))
for f in (P/'commands').glob('*/receipt.json'):
 c=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==c[n+'Sha256']
save(P/'FINAL_SOURCE_AUTHORITY.json',{'state':'Passed','recordedUtc':now(),'repositories':repos,'UnityLaunches':0,'playerLaunches':0,'sourceEdits':[],'retries':0,'scope':'J syntax-only compilation and read-only collection; no runtime batch'})
print('All four final execution-source heads clean and remote verified',flush=True)
