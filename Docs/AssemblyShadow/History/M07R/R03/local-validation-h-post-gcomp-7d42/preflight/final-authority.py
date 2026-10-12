from h_common import *
import concurrent.futures
clean_sources();no_unity();rows=[]
def audit(n):
 p=W/n;vals={};commands=[]
 for key,args in [('top',['rev-parse','--show-toplevel']),('branch',['branch','--show-current']),('head',['rev-parse','HEAD']),('status',['status','--short']),('origin',['remote','get-url','origin']),('remoteHead',['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1'])]:
  start=now();r=subprocess.run(['git','-C',str(p),*args],capture_output=True,text=True,timeout=60);assert r.returncode==0;commands.append({'argv':['git','-C',str(p),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});vals[key]=r.stdout.strip()
 assert vals['top']==str(p) and vals['branch']=='codex/assembly-shadow-r01b-h1' and vals['head']==pins[n]==vals['remoteHead'].split()[0] and not vals['status'] and vals['origin']=='git@github.com:night-outlook/'+n+'.git';return {'repository':n,'path':str(p),'values':vals,'commands':commands}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(audit,pins))
for name in ['R03IRLocal-H-post-GCOMP-7d42','StorageCheck-R03IRLocal-H-post-GCOMP-7d42','Storage-R03IRLocal-H-post-GCOMP-7d42']:assert not os.path.lexists(B/name)
for f in (P/'commands').glob('*/receipt.json'):
 r=load(f)
 for name in ['stdout','stderr']:assert sha(r[name+'Path'])==r[name+'Sha256']
save(P/'FINAL_SOURCE_AUTHORITY.json',{'state':'Passed','recordedUtc':now(),'pins':pins,'repositories':rows,'allCommandStreamsAuthenticated':True,'sourceChanged':False,'diagnosticStorageInvocations':0,'executeInvocations':0,'unityLaunches':0,'playerLaunches':0,'runtimeAndStorageRootsRemainAbsent':True});print('Final H source/remote/stream and zero-launch facts verified')
