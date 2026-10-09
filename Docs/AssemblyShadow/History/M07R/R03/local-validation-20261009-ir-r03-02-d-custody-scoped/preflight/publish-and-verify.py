from pathlib import Path
import subprocess,json,datetime,hashlib,concurrent.futures
W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009D-custody-scoped');branch='codex/assembly-shadow-r01b-h1';source=json.loads((P/'SOURCE_ENVIRONMENT.json').read_text())['pins'];operations=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def command(repo,args):
 start=now();r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=240);row={'argv':['git','-C',str(repo),*args],'startUtc':start,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};operations.append(row);assert r.returncode==0,row;return r.stdout.strip()
assert command(D,['status','--short'])==''
head=command(D,['rev-parse','HEAD']);assert command(D,['rev-parse','HEAD^'])==source['hybridclr_demo'];assert command(D,['ls-remote','origin','refs/heads/'+branch]).split()[0]==source['hybridclr_demo']
command(D,['diff','--exit-code',source['hybridclr_demo'],'HEAD','--','.',':!Docs/AssemblyShadow'])
push=command(D,['push','origin','HEAD:refs/heads/'+branch]);print(json.dumps({'pushedDemoHead':head,'pushState':'Passed'}),flush=True)
def verify(name):
 repo=W/name;start=now();rows=[]
 def read(*args):
  a=now();r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,timeout=180);rows.append({'argv':['git','-C',str(repo),*args],'startUtc':a,'endUtc':now(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0;return r.stdout.strip()
 top=read('rev-parse','--show-toplevel');b=read('branch','--show-current');h=read('rev-parse','HEAD');status=read('status','--short');origin=read('remote','get-url','origin');remote=read('ls-remote','origin','refs/heads/'+branch).split()[0];expected=head if name=='hybridclr_demo' else source[name];assert top==str(repo) and b==branch and h==remote==expected and not status and origin=='git@github.com:night-outlook/'+name+'.git'
 return {'repository':'night-outlook/'+name,'path':str(repo),'branch':b,'latestPushedCommit':h,'remoteHead':remote,'remote':'verified','status':'Clean','startUtc':start,'endUtc':now(),'commands':rows}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(verify,source))
C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-d-custody-scoped';manifest=hashlib.sha256((C/'MANIFEST.sha256').read_bytes()).hexdigest();assert manifest==json.loads((P/'PUBLICATION_VALIDATION.json').read_text())['manifestSha256']
with (P/'PUBLICATION_RECEIPT.json').open('x') as f:json.dump({'state':'PublishedVerified','recordedUtc':now(),'repositories':rows,'operations':operations,'preflightSources':source,'checkpoint':str(C),'manifestSha256':manifest,'validationReceipt':str(P/'PUBLICATION_VALIDATION.json'),'batch':'NotRun','runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'exitState':'Local Validation -> Primary Implementation'},f,indent=2);f.write('\n')
print(json.dumps({'state':'PublishedVerified','repositories':[{k:x[k] for k in ['repository','latestPushedCommit','status','remote']} for x in rows],'publicationReceipt':str(P/'PUBLICATION_RECEIPT.json')}),flush=True)
