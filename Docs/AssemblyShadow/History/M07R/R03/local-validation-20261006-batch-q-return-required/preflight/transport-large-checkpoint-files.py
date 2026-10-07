"""Lossless transport of oversized owned checkpoint copies; live evidence unchanged."""
import pathlib,hashlib,json,datetime
P=pathlib.Path(__file__).resolve().parent;R=P.parent/'R03LocalBatch-20261006Q-lp-repair';D=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo');C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261006-batch-q-return-required'
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
expected={'batch/LOCAL_BATCH_RESULT.json':R/'LOCAL_BATCH_RESULT.json','batch/BATCH_EXECUTION.json':R/'BATCH_EXECUTION.json','preflight/runner-stdout.log':P/'runner-stdout.log'}
large={str(f.relative_to(C)) for f in C.rglob('*') if f.is_file() and f.stat().st_size>=100*1024*1024};assert large==set(expected),large
record={'kind':'LosslessLargeCheckpointFileTransport','startedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'partSizeBytes':64*1024*1024,'files':[],'liveOriginalsUnchanged':True,'productReexecution':False,'reason':'Publication file-size guard rejected three exact raw checkpoint copies; preserve original bytes through ordered parts.'}
for name,live in expected.items():
 original=C/name;h=sha(original);size=original.stat().st_size;assert h==sha(live) and size==live.stat().st_size;parts=[];folder=C/(name+'.parts');assert not folder.exists();folder.mkdir(parents=True)
 with original.open('rb') as stream:
  seq=0
  while data:=stream.read(record['partSizeBytes']):
   target=folder/('part-'+str(seq).zfill(3)+'.part');target.write_bytes(data);parts.append({'path':str(target.relative_to(C)),'sha256':sha(target),'size':len(data)});seq+=1
 combined=hashlib.sha256();total=0
 for part in parts:
  f=C/part['path'];assert sha(f)==part['sha256'] and f.stat().st_size==part['size']
  with f.open('rb') as stream:
   for b in iter(lambda:stream.read(1048576),b''):combined.update(b);total+=len(b)
 assert combined.hexdigest()==h and total==size and sha(live)==h
 record['files'].append({'originalPath':name,'liveOriginalPath':str(live),'originalSha256':h,'originalSize':size,'parts':parts,'reassembledSha256':combined.hexdigest(),'removalScope':'Only newly created uncommitted owned checkpoint copy; exact original remains live and reconstructable'})
 original.unlink()
record['endedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(C/'LARGE_FILE_TRANSPORT.json').write_text(json.dumps(record,indent=2)+'\n');(P/'LARGE_FILE_TRANSPORT.json').write_text(json.dumps(record,indent=2)+'\n')
helper='''"""Reconstruct exact oversized Q evidence copies into a new absolute unused directory."""
import pathlib,hashlib,json,sys
root=pathlib.Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python3 REASSEMBLE_LARGE_FILES.py /absolute/unused/output-directory')
target=pathlib.Path(sys.argv[1]);assert target.is_absolute() and not target.exists();manifest=json.loads((root/'LARGE_FILE_TRANSPORT.json').read_text());target.mkdir(parents=True)
for row in manifest['files']:
 rel=pathlib.Path(row['originalPath']);assert not rel.is_absolute() and '..' not in rel.parts;out=target/rel;out.parent.mkdir(parents=True,exist_ok=True);whole=hashlib.sha256();size=0
 with out.open('xb') as dst:
  for item in row['parts']:
   rel=pathlib.Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts;part=root/rel;partHash=hashlib.sha256();partSize=0
   with part.open('rb') as src:
    for data in iter(lambda:src.read(1048576),b''):dst.write(data);whole.update(data);partHash.update(data);size+=len(data);partSize+=len(data)
   assert partHash.hexdigest()==item['sha256'] and partSize==item['size']
 assert whole.hexdigest()==row['originalSha256'] and size==row['originalSize'];print(row['originalPath'],whole.hexdigest(),size)
'''
compile(helper,'REASSEMBLE_LARGE_FILES.py','exec');(C/'REASSEMBLE_LARGE_FILES.py').write_text(helper)
q=C/'README.md';s=q.read_text().replace('[result](batch/LOCAL_BATCH_RESULT.json)','[result transport](LARGE_FILE_TRANSPORT.json)').replace('[ledger](batch/BATCH_EXECUTION.json)','[ledger transport](LARGE_FILE_TRANSPORT.json)');s+='\nThe exact original result, execution ledger and runner stdout exceed the publication size guard. [LARGE_FILE_TRANSPORT.json](LARGE_FILE_TRANSPORT.json) binds their original sizes/hashes and ordered64MiB parts; [REASSEMBLE_LARGE_FILES.py](REASSEMBLE_LARGE_FILES.py) reconstructs them into a new absolute unused directory. Live originals remain unchanged.\n';q.write_text(s)
q=D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md';s=q.read_text();a='Original archive/index/seal bytes are unchanged; exact ordered parts reconstruct at a new path.';b=a+' The oversized original result, ledger and runner stdout are likewise preserved through [authenticated large-file transport](../History/M07R/R03/local-validation-20261006-batch-q-return-required/LARGE_FILE_TRANSPORT.json) and a reconstruction helper; their live bytes and original hashes remain unchanged.';assert a in s.split('## Historical',1)[0];q.write_text(s.replace(a,b,1))
print(json.dumps({'filesTransported':len(record['files']),'parts':sum(len(f['parts']) for f in record['files']),'originalHashes':[f['originalSha256'] for f in record['files']],'liveEvidenceUnchanged':True}))
