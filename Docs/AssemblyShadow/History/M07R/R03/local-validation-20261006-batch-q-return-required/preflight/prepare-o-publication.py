"""Preserve raw whitespace using exact, separately authenticated path exceptions."""
import pathlib,json,hashlib,subprocess,datetime,shutil
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261006Q-lp-repair';R=P.parent/'R03LocalBatch-20261006Q-lp-repair';result=json.loads((R/'LOCAL_BATCH_RESULT.json').read_text());C=D/('Docs/AssemblyShadow/History/M07R/R03/local-validation-20261006-batch-q-'+('evidence-ready' if result['result']=='EvidenceReadyForPrimaryReview' else 'return-required'))
transport=json.loads((C/'LARGE_FILE_TRANSPORT.json').read_text());opaque={item['path']:item for row in transport['files'] for item in row['parts']}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();before=json.loads((P/'pre-install-source-settings.json').read_text())['files'];bycopy={str(pathlib.Path(i['copy']).relative_to(P)):i for i in before};rows=[]
for root in ['preflight','source-snapshot']:
 for q in sorted((C/root).rglob('*')):
  if not q.is_file():continue
  relative=str(q.relative_to(C))
  if relative in opaque:
   item=opaque[relative];assert sha(q)==item['sha256'] and q.stat().st_size==item['size'];continue
  try:text=q.read_text()
  except UnicodeDecodeError:continue
  lines=[i for i,l in enumerate(text.splitlines(),1) if l.endswith((' ','\t'))]
  blankEof=text.endswith('\n\n') or text.endswith('\r\n\r\n')
  if not lines and not blankEof:continue
  relative=str(q.relative_to(C));auth=None
  if root=='source-snapshot':
   name=q.relative_to(C/root);repo=W/'hybridclr_unity' if name.parts[0]=='hybridclr_unity' else D;name=pathlib.Path(*name.parts[1:]) if repo!=D else name;h=result['repositories'][repo.name];blob=subprocess.check_output(['git','-C',str(repo),'show',h+':'+str(name)]);assert q.read_bytes()==blob;auth={'provenance':'ExactExecutedGitSourceBlob','repositoryPath':str(repo),'commit':h,'sourcePath':str(name)}
  else:
   name=str(q.relative_to(C/root))
   if name in bycopy:
    row=bycopy[name];assert sha(q)==row['sha256']==sha(row['copy']);source=pathlib.Path(row['path']);rel=source.relative_to(D);blob=subprocess.check_output(['git','-C',str(D),'show',result['repositories']['hybridclr_demo']+':'+str(rel)]);assert q.read_bytes()==blob;auth={'provenance':'ExactPreflightExecutedGitSourceBlob','repositoryPath':str(D),'commit':result['repositories']['hybridclr_demo'],'sourcePath':str(rel)}
   elif name.startswith(('editor-scope-source/','additional-issue-source/')):
    rest=pathlib.Path(name).relative_to(pathlib.Path(name).parts[0]);repo=W/rest.parts[0];rel=pathlib.Path(*rest.parts[1:]);h=result['repositories'][repo.name];blob=subprocess.check_output(['git','-C',str(repo),'show',h+':'+str(rel)]);assert q.read_bytes()==blob;auth={'provenance':'ExactExecutedGitIssueSourceBlob','repositoryPath':str(repo),'commit':h,'sourcePath':str(rel)}
   elif name.startswith('codec-source/'):
    rel=pathlib.Path(name).relative_to('codec-source');repo=W/'hybridclr';h=result['repositories']['hybridclr'];blob=subprocess.check_output(['git','-C',str(repo),'show',h+':'+str(rel)]);assert q.read_bytes()==blob;auth={'provenance':'ExactExecutedNativeCodecSourceBlob','repositoryPath':str(repo),'commit':h,'sourcePath':str(rel)}
  assert auth is not None,('Raw snapshot needs explicit provenance before publication',relative)
  rows.append(dict(auth,snapshot=relative,sha256=sha(q),trailingWhitespaceLines=lines,blankLineAtEof=blankEof))
attrs=C/'.gitattributes';attrs.write_text(attrs.read_text().split('# Preserve separately authenticated raw snapshot whitespace only.')[0]+'# Preserve separately authenticated raw snapshot whitespace only.\n'+''.join(row['snapshot']+' -whitespace\n' for row in rows)+''.join(name+' binary -whitespace\n' for name in sorted(opaque)));(C/'SOURCE_SNAPSHOT_WHITESPACE.json').write_text(json.dumps({'status':'Passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshots':rows,'opaqueTransportParts':[dict(path=name,**opaque[name]) if 'path' not in opaque[name] else opaque[name] for name in sorted(opaque)],'ownedProseWhitespaceStillChecked':True,'sourceAndRuntimeBytesUnchanged':True},indent=2)+'\n')
for name in ['prepare-o-publication.py','check-publication.py','final-publication-audit.py','write-q-reports.py','describe-q-issues.py','ADMINISTRATIVE_PUBLICATION_CORRECTION.json','transport-large-checkpoint-files.py','adapt-large-file-publication.py','ADMINISTRATIVE_LARGE_FILE_PUBLICATION_ADAPTERS.json','ADMINISTRATIVE_PATH_TYPE_CORRECTION.json']:shutil.copy2(P/name,C/'preflight'/name)
for operation in (P/'local-operations').iterdir():
 if operation.is_dir() and (operation/'receipt.json').is_file():shutil.copytree(operation,C/'preflight/local-operations'/operation.name,dirs_exist_ok=True)
files=sorted(p for p in C.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256');(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files));print(json.dumps({'authenticatedRawWhitespaceExceptions':len(rows),'manifestFiles':len(files)}))
