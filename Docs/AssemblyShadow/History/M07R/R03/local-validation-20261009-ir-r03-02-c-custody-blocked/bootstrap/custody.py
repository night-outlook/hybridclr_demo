from pathlib import Path
import json,hashlib,subprocess,datetime,concurrent.futures,os,sys
D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');BASE=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');P=BASE/'Preflight-R03IRLocal-20261009C-capacity-retry';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-b-api-bound';commit='e6f918bf6c756251982eef47f255eaa71b11e1d4';phase=sys.argv[1];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(f):
 with Path(f).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(n,v):
 with (P/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def git(*a):return subprocess.check_output(['git','-C',str(D),*a],timeout=120).decode().strip()
def authenticated(f):
 rel=str(f.relative_to(D));obj=git('rev-parse',commit+':'+rel);assert git('rev-parse','HEAD:'+rel)==obj==git('hash-object','--',str(f));return f
errors=[];links={}
if phase=='before':
 manifest=authenticated(C/'MANIFEST.sha256');transport=json.loads(authenticated(C/'FILE_TRANSPORT.json').read_text());large=next(x for x in transport['files'] if x['logicalCheckpointPath']=='preflight/prior-evidence-custody.json');h=hashlib.sha256();parts=[]
 for row in large['parts']:
  f=authenticated(C/row['path']);assert sha(f)==row['sha256'];data=f.read_bytes();h.update(data);parts.append(data)
 assert h.hexdigest()==large['sha256']==json.loads(authenticated(C/'preflight/CUSTODY_MAP_BINDING.json').read_text())['sha256'];expected=json.loads(b''.join(parts));del parts;oldcount=len(expected);assert oldcount==416515
 for line in manifest.read_text().splitlines():
  h,name=line.split('  ',1);expected[str(C/name)]=h
 expected[str(manifest)]=sha(manifest)
 for row in json.loads(authenticated(C/'COPY_BINDINGS.json').read_text()):
  f=row['originalPath'];assert f not in expected or expected[f]==row['sha256'];expected[f]=row['sha256']
 current=[]
 for root in [BASE/'Preflight-R03IRLocal-20261009A-terminal',BASE/'IR-R03-02-bootstrap-20261009A',BASE/'StorageCheck-R03IRLocal-20261009A-terminal',BASE/'Preflight-R03IRLocal-20261009B-api-bound',BASE/'IR-R03-02-bootstrap-20261009B-api-bound',BASE/'StorageCheck-R03IRLocal-20261009B-api-bound']:
  assert root.is_dir() and not root.is_symlink()
  for base,dirs,files in os.walk(root,followlinks=False):
   for n in dirs+files:
    f=Path(base)/n
    if f.is_symlink():links[str(f)]=os.readlink(f)
    elif f.is_file() and str(f) not in expected:expected[str(f)]=sha(f);current.append(str(f))
 save('prior-evidence-custody.json',expected);save('prior-evidence-symlinks.json',links);save('CUSTODY_MAP_BINDING.json',{'sha256':sha(P/'prior-evidence-custody.json'),'symlinkMapSha256':sha(P/'prior-evidence-symlinks.json'),'oldAuthenticatedFiles':oldcount,'uniqueFiles':len(expected),'originalBPublication':commit,'authenticatedPreviousMapSha256':large['sha256'],'ABAdditionalCurrentSnapshotFiles':current,'currentSnapshotClassification':'Postpublication external administrative/publication files, not retrospective runtime acceptance','missingFileRebaselining':False})
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
record={'state':'Passed' if not errors else 'Blocked','phase':phase,'startUtc':start,'endUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':len(expected),'symlinks':len(links),'errors':errors,'retainedR':r,'mapSha256':sha(P/'prior-evidence-custody.json'),'historicalStatesReclassified':False,'historicalRootsModified':False};save('HISTORICAL_CUSTODY_'+phase.upper()+'.json',record);print(json.dumps({'state':record['state'],'phase':phase,'files':len(expected),'symlinks':len(links),'errorCount':len(errors),'errorPreview':errors[:2]}),flush=True)
if errors:raise SystemExit(1)
