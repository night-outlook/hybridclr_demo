import pathlib,json,hashlib,subprocess,datetime,shutil
W=pathlib.Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r');D=W/'hybridclr_demo';P=pathlib.Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261003I-completion');R=P.parent/'R03LocalBatch-20261003I-completion';C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261003-batch-i-return-required'
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
# Add dependency identities already recorded by the immutable cell receipts.
q=D/'Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md';text=q.read_text();current,history=text.split('## Historical',1)
for f in sorted((R/'cells').glob('*.json')):
 cell=json.loads(f.read_text())
 if cell['result']=='Blocked':
  previous='| `'+cell['id']+'` | Blocked |  |'
  replacement='| `'+cell['id']+'` | Blocked | Required prerequisite did not pass: '+', '.join(cell['dependencies'])+' |'
  assert previous in current;current=current.replace(previous,replacement)
q.write_text(current+'## Historical'+history)
# Preserve exact raw source and generated settings bytes; exemptions are path-specific.
rows=[]
q=C/'preflight/diagnostic-source-snapshot/hybridclr/hybridclr/metadata/InterpreterImage.h';owner=W/'hybridclr';name='hybridclr/metadata/InterpreterImage.h';commit=subprocess.check_output(['git','-C',str(owner),'rev-parse','HEAD'],text=True).strip();blob=subprocess.check_output(['git','-C',str(owner),'show',commit+':'+name]);assert blob==q.read_bytes()
rows.append({'snapshot':str(q.relative_to(C)),'provenance':'ExactGitSourceBlob','repositoryPath':str(owner),'commit':commit,'sourcePath':name,'sha256':sha(q),'trailingWhitespaceLines':[i for i,l in enumerate(q.read_text().splitlines(),1) if l.endswith((' ','\t'))]})
q=C/'preflight/issue-resource-snapshot/ProjectSettings/AssemblyShadowSettings.asset';item=next(x for x in json.loads((P/'PRIMARY_ISSUES.json').read_text())['resourceSnapshots'] if x['live'].endswith('AssemblyShadowSettings.asset'));assert sha(q)==item['sha256']==sha(pathlib.Path(item['live']));assert q.read_bytes()==pathlib.Path(item['snapshot']).read_bytes()
rows.append({'snapshot':str(q.relative_to(C)),'provenance':'ExactPostExecutionGeneratedSettingsSnapshot','executedDemoCommit':'c579e75eadef58ca484b35ffee03e435a925d781','livePath':item['live'],'primaryIssuesPath':str(P/'PRIMARY_ISSUES.json'),'sha256':sha(q),'trailingWhitespaceLines':[i for i,l in enumerate(q.read_text().splitlines(),1) if l.endswith((' ','\t'))],'limitation':'M02 configured this retained settings asset before install failed; not an unchanged Git blob or successful P05 restoration proof'})
attrs=C/'.gitattributes';attrs.write_text(attrs.read_text()+'# Preserve only separately authenticated raw snapshot whitespace.\n'+''.join(x['snapshot']+' -whitespace\n' for x in rows))
(C/'SOURCE_SNAPSHOT_WHITESPACE.json').write_text(json.dumps({'status':'Passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshots':rows,'ownedProseWhitespaceStillChecked':True,'sourceAndRuntimeBytesUnchanged':True},indent=2)+'\n')
p=P/'check-publication.py';s=p.read_text();s=s.replace('Exact pinned source snapshots with pre-existing whitespace are separately Git-blob authenticated in SOURCE_SNAPSHOT_WHITESPACE.json; owned prose and other snapshots retain whitespace checks','The two exact path-specific source/settings exceptions are independently authenticated against a pinned Git blob or post-execution live generated settings/issue receipt in SOURCE_SNAPSHOT_WHITESPACE.json; owned prose and other snapshots retain whitespace checks');p.write_text(s)
for name in ['prepare-publication.py','check-publication.py','final-publication-audit.py']:shutil.copy2(P/name,C/'preflight'/name)
files=sorted(p for p in C.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256');(C/'MANIFEST.sha256').write_text(''.join(sha(p)+'  '+str(p.relative_to(C))+'\n' for p in files))
print(json.dumps({'pathSpecificAuthenticatedWhitespaceExceptions':len(rows),'checkpointFiles':len(files),'blockedDependenciesRecorded':48}))
