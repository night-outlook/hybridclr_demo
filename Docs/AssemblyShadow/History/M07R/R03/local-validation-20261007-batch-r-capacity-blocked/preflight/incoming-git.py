import pathlib,subprocess,json,datetime,os,hashlib,concurrent.futures
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');P=W.parent/'r03-local-validation'/('Incoming-R03R-cbf80474-'+stamp);P.mkdir();os.environ['GIT_SSH_COMMAND']='ssh -i /Users/ah/.ssh/github-night-outlook -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3'
pins={'hybridclr_demo':'cbf80474ebdee125e1d162d9c32a1734ee541720','hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'1cf87f8209790f9fb2ebec97487dc1990ccd56c5'};branch='codex/assembly-shadow-r01b-h1'
def run(repo,args):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True);return {'command':['git','-C',str(repo),*args],'startUtc':t,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
def inspect(name):
 repo=W/name;origin=run(repo,['remote','get-url','origin']);assert origin['exitCode']==0 and origin['stdout'].strip()=='git@github.com:night-outlook/'+name+'.git',('Unexpected origin',name)
 rows=[run(repo,a) for a in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/'+branch]]];(P/(name+'-before.json')).write_text(json.dumps(rows,indent=2)+'\n');assert all(r['exitCode']==0 for r in rows);assert rows[0]['stdout'].strip()==str(repo) and rows[1]['stdout'].strip()==branch and not rows[3]['stdout'].strip() and rows[-1]['stdout'].split()[0]==pins[name]
 if name!='hybridclr_demo':assert rows[2]['stdout'].strip()==pins[name]
 return {'repository':name,'path':str(repo),'beforeHead':rows[2]['stdout'].strip(),'remoteHead':rows[-1]['stdout'].split()[0],'status':'Clean'}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:rows=list(e.map(inspect,pins))
D=W/'hybridclr_demo';fetch=run(D,['fetch','origin',branch]);(P/'fetch-demo.json').write_text(json.dumps(fetch,indent=2)+'\n');assert fetch['exitCode']==0 and run(D,['rev-parse','FETCH_HEAD'])['stdout'].strip()==pins['hybridclr_demo']
for name in ['README.md','Handoff/WEB_TO_LOCAL.md']:
 r=run(D,['show',pins['hybridclr_demo']+':Docs/AssemblyShadow/'+name]);assert r['exitCode']==0;dest=P/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(r['stdout'])
(P/'INITIAL_AUTHORITY.json').write_text(json.dumps({'repositories':rows,'sshCommand':os.environ['GIT_SSH_COMMAND'],'expectedPins':pins,'noValidationLaunched':True},indent=2)+'\n');print('Initial authority verified; fetched handoff preserved at',P)
