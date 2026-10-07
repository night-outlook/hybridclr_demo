"""Adapt Local-only publication authentication to exact lossless large-file transport."""
import pathlib,hashlib,json,datetime
P=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();records=[]
fn='''def checkpoint_copy_sha(relative):
 p=C/relative
 if p.is_file():return sha(p)
 rows=json.loads((C/'LARGE_FILE_TRANSPORT.json').read_text())['files'];row=next(r for r in rows if r['originalPath']==relative);whole=hashlib.sha256();size=0
 for item in row['parts']:
  part=C/item['path'];assert sha(part)==item['sha256'] and part.stat().st_size==item['size']
  with part.open('rb') as f:
   for data in iter(lambda:f.read(1048576),b''):whole.update(data);size+=len(data)
 assert whole.hexdigest()==row['originalSha256'] and size==row['originalSize'];return whole.hexdigest()
'''
for name in ['check-publication.py','final-publication-audit.py']:
 p=P/name;s=p.read_text();before=sha(p);marker='projectChecks=[]' if name=='check-publication.py' else 'def verify(name):';assert marker in s;s=s.replace(marker,fn+'\n'+marker,1)
 if name=='check-publication.py':
  a="for f in idx['files']:assert sha(C/'batch'/f['path'])==f['sha256']";b="for f in idx['files']:assert checkpoint_copy_sha('batch/'+f['path'])==f['sha256']";assert a in s;s=s.replace(a,b)
  a="for n in ['LOCAL_BATCH_RESULT.json','evidence-index.json','seal-receipt.json']:assert sha(C/'batch'/n)==sha(R/n)";b="for n in ['LOCAL_BATCH_RESULT.json','evidence-index.json','seal-receipt.json']:assert checkpoint_copy_sha('batch/'+n)==sha(R/n)\nfor row in json.loads((C/'LARGE_FILE_TRANSPORT.json').read_text())['files']:\n assert checkpoint_copy_sha(row['originalPath'])==row['originalSha256']==sha(row['liveOriginalPath'])\n if row['originalPath'].endswith('.json'):json.loads(pathlib.Path(row['liveOriginalPath']).read_text());jsonCount+=1";assert a in s;s=s.replace(a,b)
  a="'rawWhitespaceAudit':";b="'largeFileTransport':'Three oversized exact original files authenticated through six ordered64MiB parts; live originals unchanged; original JSON parsed; publication size guard retained','rawWhitespaceAudit':";assert a in s;s=s.replace(a,b)
 else:
  a="sha(C/'batch'/f['path'])==f['sha256']";b="checkpoint_copy_sha('batch/'+f['path'])==f['sha256']";assert a in s;s=s.replace(a,b)
  a="if n!='evidence.tar.gz':assert sha(C/'batch'/n)==h";b="if n!='evidence.tar.gz':assert checkpoint_copy_sha('batch/'+n)==h\nfor row in json.loads((C/'LARGE_FILE_TRANSPORT.json').read_text())['files']:assert checkpoint_copy_sha(row['originalPath'])==row['originalSha256']==sha(row['liveOriginalPath'])";assert a in s;s=s.replace(a,b)
  a="'batchInvocations':1,";b="'largeFilesTransported':3,'largeFileTransportAuthenticated':True,'qualificationApproved':False,'pureInterpreterExpansionEnabled':False,'ReadyForHumanReviewGate':False,'batchInvocations':1,";assert a in s;s=s.replace(a,b)
 p.write_text(s);compile(s,str(p),'exec');records.append({'script':str(p),'beforeSha256':before,'afterSha256':sha(p),'changes':'Authenticate exact reconstructed original hashes and sizes from ordered parts; retain original index/seal, source/pin/remote, clean-state, Git-byte and100MiB checks.'})
p=P/'prepare-o-publication.py';s=p.read_text();before=sha(p);a="sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();before=";b="transport=json.loads((C/'LARGE_FILE_TRANSPORT.json').read_text());opaque={item['path']:item for row in transport['files'] for item in row['parts']}\nsha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();before=";assert a in s;s=s.replace(a,b)
a="if not q.is_file():continue\n  try:text=q.read_text()";b="if not q.is_file():continue\n  relative=str(q.relative_to(C))\n  if relative in opaque:\n   item=opaque[relative];assert sha(q)==item['sha256'] and q.stat().st_size==item['size'];continue\n  try:text=q.read_text()";assert a in s;s=s.replace(a,b)
a="''.join(row['snapshot']+' -whitespace\\n' for row in rows)";b="''.join(row['snapshot']+' -whitespace\\n' for row in rows)+''.join(name+' binary -whitespace\\n' for name in sorted(opaque))";assert a in s;s=s.replace(a,b)
a="'snapshots':rows,";b="'snapshots':rows,'opaqueTransportParts':[dict(path=name,**opaque[name]) if 'path' not in opaque[name] else opaque[name] for name in sorted(opaque)],";assert a in s;s=s.replace(a,b)
a="'ADMINISTRATIVE_PUBLICATION_CORRECTION.json']";b="'ADMINISTRATIVE_PUBLICATION_CORRECTION.json','transport-large-checkpoint-files.py','adapt-large-file-publication.py','ADMINISTRATIVE_LARGE_FILE_PUBLICATION_ADAPTERS.json']";assert a in s;s=s.replace(a,b)
p.write_text(s);compile(s,str(p),'exec');records.append({'script':str(p),'beforeSha256':before,'afterSha256':sha(p),'changes':'Opaque transported parts independently hash-authenticated and marked binary; separately source-authenticated whitespace exceptions unchanged. Copy current Local transport/authentication scripts and completed receipts.'})
(P/'ADMINISTRATIVE_LARGE_FILE_PUBLICATION_ADAPTERS.json').write_text(json.dumps({'kind':'LocalLargeEvidencePublicationAdapters','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records,'productSourceChanges':[],'productReexecution':False,'originalVerdictsUnchanged':True},indent=2)+'\n');print('Updated3 Local publication helpers; exact raw-byte/index/seal/source/remote/size/whitespace checks retained.')
