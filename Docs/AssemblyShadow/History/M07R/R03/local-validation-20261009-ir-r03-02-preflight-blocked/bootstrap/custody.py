from pathlib import Path
import json,hashlib,subprocess,datetime,concurrent.futures,os,sys
D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009A-terminal');BASE=P.parent;C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready';S=BASE/'R03LocalBatch-20261007S-lr-recovery';commit='fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b';phase=sys.argv[1];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def git(*a):return subprocess.check_output(['git','-C',str(D),*a],text=True,timeout=120).strip()
def authenticated(f):
 rel=str(f.relative_to(D));obj=git('rev-parse',commit+':'+rel);assert git('rev-parse','HEAD:'+rel)==obj==git('hash-object','--',str(f));return f
errors=[];links={}
if phase=='before':
 old=authenticated(C/'preflight/prior-evidence-custody.json');expected=json.loads(old.read_text());oldcount=len(expected);top=json.loads(authenticated(C/'preflight/POSTRUN_AUTHENTICATION.json').read_text())['topLevelHashes']
 for name,h in top.items():expected[str(S/name)]=h
 index=json.loads((S/'evidence-index.json').read_text());assert sha(S/'evidence-index.json')==top['evidence-index.json']
 for row in index['files']:
  path=str(S/row['path']);assert path not in expected or expected[path]==row['sha256'];expected[path]=row['sha256']
 for line in authenticated(C/'MANIFEST.sha256').read_text().splitlines():
  h,name=line.split('  ',1);assert '\n' not in name;path=str(C/name);assert path not in expected or expected[path]==h;expected[path]=h
 expected[str(C/'MANIFEST.sha256')]=sha(C/'MANIFEST.sha256')
 for root,dirs,files in os.walk(S,followlinks=False):
  for name in files:
   f=Path(root)/name
   if f.is_symlink():links[str(f)]=os.readlink(f)
   elif str(f) not in expected:expected[str(f)]=sha(f)
  for name in dirs:
   f=Path(root)/name
   if f.is_symlink():links[str(f)]=os.readlink(f)
 save('prior-evidence-custody.json',expected);save('prior-evidence-symlinks.json',links);save('CUSTODY_MAP_BINDING.json',{'sha256':sha(P/'prior-evidence-custody.json'),'symlinkMapSha256':sha(P/'prior-evidence-symlinks.json'),'oldAuthenticatedFiles':oldcount,'uniqueFiles':len(expected),'SSelectedFiles':len(index['files']),'SUnindexedCacheClassification':'Current custody snapshot only, never historical runtime acceptance','originalSPublication':commit,'newMapsAreAdditiveNotMissingFileRebaselining':True})
else:
 binding=json.loads((P/'CUSTODY_MAP_BINDING.json').read_text());assert sha(P/'prior-evidence-custody.json')==binding['sha256'] and sha(P/'prior-evidence-symlinks.json')==binding['symlinkMapSha256'];expected=json.loads((P/'prior-evidence-custody.json').read_text());links=json.loads((P/'prior-evidence-symlinks.json').read_text())
def verify(row):
 f,h=row
 try:
  actual=sha(f);return None if actual==h else {'path':f,'expectedSha256':h,'actualSha256':actual}
 except Exception as e:return {'path':f,'expectedSha256':h,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for error in pool.map(verify,expected.items(),buffersize=48):
  if error:errors.append(error)
for f,t in links.items():
 if not Path(f).is_symlink() or os.readlink(f)!=t:errors.append({'path':f,'expectedSymlink':t,'error':'Symlink identity changed'})
sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03Completion'));import retained_transaction
r=retained_transaction.verify(BASE/'R03LocalBatch-20261007R-lq-storage',retained_transaction.inputs())
record={'state':'Passed' if not errors else 'Blocked','phase':phase,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(expected),'symlinks':len(links),'errors':errors,'retainedR':r,'mapSha256':sha(P/'prior-evidence-custody.json'),'historicalStatesReclassified':False,'historicalRootsModified':False};save('HISTORICAL_CUSTODY_'+phase.upper()+'.json',record);print(json.dumps({k:record[k] for k in ['state','phase','files','symlinks','errors']}),flush=True)
if errors:raise SystemExit(1)
