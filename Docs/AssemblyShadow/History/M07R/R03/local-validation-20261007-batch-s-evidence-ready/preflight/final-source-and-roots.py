from pathlib import Path
import json,subprocess,datetime,sys,hashlib
P=Path(__file__).resolve().parent;B=P.parent/'R03LocalBatch-20261007S-lr-recovery';W=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo'
def save(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert (P/'operations/storage-executing/receipt.json').exists()
a=json.loads((P/'SOURCE_AUTHORITY.json').read_text());rows=[]
for name,pin in a['repositories'].items():
 root=W/name;row={'path':str(root),'expectedCommit':pin,'commands':[]}
 for args in [['rev-parse','--show-toplevel'],['branch','--show-current'],['rev-parse','HEAD'],['status','--short'],['remote','-v'],['worktree','list','--porcelain'],['submodule','status','--recursive'],['ls-remote','origin','refs/heads/codex/assembly-shadow-r01b-h1']]:
  start=utc();r=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=120);row['commands'].append({'argv':['git','-C',str(root),*args],'startUtc':start,'endUtc':utc(),'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
 commands=row['commands'];assert commands[0]['stdout'].strip()==str(root);assert commands[1]['stdout'].strip()=='codex/assembly-shadow-r01b-h1';assert commands[2]['stdout'].strip()==pin;assert not commands[3]['stdout'].strip();assert commands[-1]['stdout'].split()[0]==pin;assert 'git@github.com:night-outlook/'+name+'.git' in commands[4]['stdout'];rows.append(row)
save('FINAL_EXECUTION_SOURCE_AUTHORITY.json',{'state':'Passed','recordedUtc':utc(),'repositories':rows,'freshRemoteObservation':True,'beforeLocalDocumentationChanges':True})
roots=[]
for r in sorted(B.iterdir()):
 if r.is_dir():roots.append({'path':str(r),'exists':r.exists(),'custody':'Retained live; exact selected files bound by evidence-index and producer receipts','classification':'Fresh S output or source-authorized detached reference; never historical runtime-result reuse'})
refs=[]
for r in sorted((B/'reference-worktrees').glob('*')):
 if r.is_dir():
  proc=subprocess.run(['git','-C',str(r),'rev-parse','HEAD'],capture_output=True,text=True,timeout=30)
  if proc.returncode==0:refs.append({'path':str(r),'commit':proc.stdout.strip(),'branch':subprocess.check_output(['git','-C',str(r),'branch','--show-current'],text=True).strip()})
save('RETAINED_LIVE_ROOTS.json',{'recordedUtc':utc(),'batch':str(B),'retainedDirectories':roots,'referenceWorktrees':refs,'scope':'Index-selected evidence is copied; isolated projects, Library/cache/SDK/compiler outputs, complete apps and reference worktrees remain live at original absolute paths. No deletion or relocation. Installed native and Player exact inventories remain in producer receipts.','sameCheckoutSourcePins':a['repositories']})
sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03Storage'));import storage_guard as s
common=Path(subprocess.check_output(['git','-C',str(D),'rev-parse','--git-common-dir'],text=True).strip());common=(D/common).resolve() if not common.is_absolute() else common.resolve()
size=s.footprint(B);required=max(s.FLOOR,size['planningBytes']+s.MARGIN);observation=s.sample({'publicationCheckout':D,'retainedBatch':B,'gitCommon':common});record={'kind':'R03StoragePublicationCheck','requiredBytes':required,'size':size,'observation':observation,'state':'Blocked','recordedUtc':utc()}
try:s.capacity_ok(observation,required);record['state']='Passed'
finally:s.write_new(P/'storage-publication-check.json',record)
print('Final source authority and retained roots Passed; publication capacity',record['state'],required,flush=True)
