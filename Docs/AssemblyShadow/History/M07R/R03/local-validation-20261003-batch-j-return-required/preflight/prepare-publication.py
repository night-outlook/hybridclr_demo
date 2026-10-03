import pathlib,json,hashlib,subprocess,datetime,shutil
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=W.parent/'r03-local-validation/Preflight-R03LocalBatch-20261003J-contracts';R=P.parent/'R03LocalBatch-20261003J-contracts';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-j-return-required'
sha=lambda q:hashlib.sha256(pathlib.Path(q).read_bytes()).hexdigest();issue=json.loads((P/'PRIMARY_ISSUES.json').read_text());rows=[]
for item in issue['resourceSnapshots']:
 q=C/'preflight'/pathlib.Path(item['snapshot']).relative_to(P);assert sha(q)==item['sha256']==sha(item['live']);lines=[i for i,l in enumerate(q.read_text().splitlines(),1) if l.endswith((' ','\t'))]
 if lines:rows.append({'snapshot':str(q.relative_to(C)),'provenance':'ExactPostExecutionGeneratedSnapshot','livePath':item['live'],'sha256':sha(q),'trailingWhitespaceLines':lines,'limitation':'Runtime configuration bytes; not successful P05 restoration evidence'})
for item in json.loads((P/'pre-install-source-settings.json').read_text()):
 q=C/'preflight'/pathlib.Path(item['snapshot']).relative_to(P);name=pathlib.Path(item['source']).relative_to(D);blob=subprocess.check_output(['git','-C',str(D),'show',item['sourceCommit']+':'+str(name)]);assert q.read_bytes()==blob and sha(q)==item['sha256'];lines=[i for i,l in enumerate(q.read_text().splitlines(),1) if l.endswith((' ','\t'))]
 if lines:rows.append({'snapshot':str(q.relative_to(C)),'provenance':'ExactGitSourceBlob','repositoryPath':str(D),'commit':item['sourceCommit'],'sourcePath':str(name),'sha256':sha(q),'trailingWhitespaceLines':lines})
found=[]
for root in ['preflight','source-snapshot']:
 for q in (C/root).rglob('*'):
  if not q.is_file():continue
  try:s=q.read_text()
  except UnicodeDecodeError:continue
  if any(l.endswith((' ','\t')) for l in s.splitlines()):found.append(str(q.relative_to(C)))
assert set(found)=={x['snapshot'] for x in rows} and len(rows)==4
attrs=C/'.gitattributes';attrs.write_text(attrs.read_text()+'# Preserve only separately authenticated raw snapshot whitespace.\n'+''.join(x['snapshot']+' -whitespace\n' for x in rows));(C/'SOURCE_SNAPSHOT_WHITESPACE.json').write_text(json.dumps({'status':'Passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshots':rows,'ownedProseWhitespaceStillChecked':True,'sourceAndRuntimeBytesUnchanged':True},indent=2)+'\n')
p=P/'check-publication.py';s=p.read_text().replace('The two exact path-specific source/settings exceptions','The four exact path-specific source/settings exceptions');p.write_text(s)
q=D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md';s=q.read_text().replace('ProductName:\t\tmacOS; ProductVersion:\t\t26.5.2; BuildVersion:\t\t25F84; arm64','macOS26.5.2 (25F84) arm64',1);q.write_text(s)
for name in ['prepare-publication.py','check-publication.py','final-publication-audit.py']:shutil.copy2(P/name,C/'preflight'/name)
files=sorted(p for p in C.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256');(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files));print(json.dumps({'authenticatedRawWhitespaceExceptions':len(rows),'manifestFiles':len(files)}))
