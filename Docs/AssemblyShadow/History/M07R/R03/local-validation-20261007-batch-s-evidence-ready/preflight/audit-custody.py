"""Read-only compare published S custody and checkpoint; never rebaseline missing files."""
from pathlib import Path
import json,hashlib,datetime,concurrent.futures,time,subprocess
P=Path(__file__).resolve().parent;BASE=P.parent;D=Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-capacity-blocked';OLD=BASE/'Preflight-R03LocalBatch-20261007S-lr-recovery';PUB='29bb3d4a39bf8a2f23be404f77535aaba3485bfc'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):
 with (P/n).open('x') as f:json.dump(v,f,separators=(',',':'));f.write('\n')
start=utc();m=C/'MANIFEST.sha256';blob=subprocess.check_output(['git','-C',str(D),'show',PUB+':'+str(m.relative_to(D))]);assert m.read_bytes()==blob;cm={str(m):hashlib.sha256(blob).hexdigest()}
for line in blob.decode().splitlines():
 h,rel=line.split('  ',1);cm[str(C/rel)]=h
oldmap=C/'preflight/prior-evidence-custody.json';assert sha(oldmap)==cm[str(oldmap)];expected=json.loads(oldmap.read_text());assert len(expected)==290082;expected.update(cm);additional={}
for path in OLD.rglob('*'):
 if path.is_file() and not path.is_symlink() and str(path) not in expected:additional[str(path)]=sha(path)
expected.update(additional);save('prior-evidence-custody.json',expected);errors=[];done=0;last=time.monotonic()
def verify(row):
 path,h=row
 try:
  actual=sha(path);return None if actual==h else {'path':path,'expected':h,'actual':actual}
 except Exception as e:return {'path':path,'expected':h,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for error in pool.map(verify,expected.items(),buffersize=48):
  done+=1
  if error:errors.append(error)
  if time.monotonic()-last>20:print('Custody',done,'/',len(expected),'errors',len(errors),flush=True);last=time.monotonic()
r={'kind':'SContinuationHistoricalCustody','startUtc':start,'endUtc':utc(),'state':'Passed' if not errors else 'Failed','originalPublishedMapFiles':290082,'priorPublishedCheckpointFiles':len(cm),'additionalOriginalPreflightSnapshot':len(additional),'uniqueFiles':len(expected),'oldMapSha256':sha(oldmap),'checkpointManifestSha256':sha(m),'expectedMapSha256':sha(P/'prior-evidence-custody.json'),'errors':errors,'historicalClassificationChanged':False,'noMissingFileRebaselining':True,'priorRCacheSnapshotIsNotAcceptance':True};save('HISTORICAL_CUSTODY_BEFORE.json',r);print('Custody',r['state'],len(expected),'errors',len(errors),flush=True);assert not errors
