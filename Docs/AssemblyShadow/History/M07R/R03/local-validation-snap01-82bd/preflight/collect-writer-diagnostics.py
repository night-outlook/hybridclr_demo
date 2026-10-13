from h_common import *
import re
start=now();R=B/'R03IRLocal-SNAP01-82bd';a=load(P/'FINAL_EVIDENCE_AUDIT.json');core=load(R/'LOCAL_BATCH_RESULT.json');index={x['path']:x for x in load(R/'evidence-index.json')['files']};classifier=hist/'IR_Remediation/N_SNAPSHOT_PUBLICATION_91b7/checks/classify_snapshot_failure.py';rows=[]
for p in a['players']:
 case=p['caseId'];root=R/'players'/case;log=root/'Player.log';assert sha(log)==p['logSha256']==index['players/'+case+'/Player.log']['sha256'];cmd=load(p['commandReceipt']);assert cmd['pid']==p['pid'] and str(root/'request.json') in cmd['command'];out=P/('writer-classification-'+case+'.json');assert not out.exists()
 c=command('classify-'+case,[PY,'-B',classifier,'--log',log,'--pid',p['pid'],'--sha256',p['logSha256'],'--output',out]);row={'caseId':case,'source':pins,'pid':p['pid'],'runId':p['runId'],'commandReceipt':p['commandReceipt'],'commandSha256':p['commandSha256'],'log':str(log),'logSha256':p['logSha256'],'originalCell':p['state'],'processExit':p['exitCode'],'originalRaw':p['raw'],'originalVerification':p['verification'],'classificationExit':c['exitCode'],'expectedSnapshotWriter':case!='IR-R03-02-release-engine','writerEvidence':'Unavailable'}
 if c['exitCode']==0:
  j=load(out);assert j['pid']==p['pid'] and j['logSha256']==p['logSha256'] and j['runtimeAcceptance'] is False;row.update(classification=j,classificationPath=str(out),classificationSha256=sha(out))
  if j['result']=='NativeTransportFailureRecorded':row['writerEvidence']='AuthenticatedFirstNativeFailure'
  else:
   lines=[s for s in log.read_text().splitlines() if s.startswith('[R03SnapshotSealed]')];row['sealLines']=lines
   if row['expectedSnapshotWriter'] and lines and p['raw']=='Recorded' and p['verification']=='Passed' and p['exitCode']==0:
    assert len(lines)==1 and re.fullmatch(r'\[R03SnapshotSealed\] version=1 pid='+str(p['pid'])+r' intMask=01ffffff textMask=0000ffff',lines[0]);raw=load(root/'raw.json');assert raw['processId']==p['pid'] and raw['runId']==p['runId'] and raw['requestSha256']==p['requestSha256'];row['writerEvidence']='AuthenticatedCompleteStrictRawAndNativeSeal'
   elif not row['expectedSnapshotWriter']:
    row['writerEvidence']='SeparateEngineControlPreserved';row['engineRaw']=load(root/'raw.json') if (root/'raw.json').stat().st_size else None
 else:row['classification']='Failed; original log retained; classifier not retried'
 rows.append(row)
writers=[r for r in rows if r['expectedSnapshotWriter']];assert len(writers)==4
passed=sum(r['writerEvidence'] in ['AuthenticatedFirstNativeFailure','AuthenticatedCompleteStrictRawAndNativeSeal'] for r in writers);state='EvidenceCollected' if passed==4 else 'Partial' if passed else 'Unavailable'
save(P/'DIAGNOSTIC_COLLECTION.json',{'kind':'SNAP01DiagnosticCollection','startUtc':start,'endUtc':now(),'source':pins,'semanticBatchResult':core['result'],'semanticCellCounts':a['cellCounts'],'semanticLedgerSha256':sha(R/'BATCH_EXECUTION.json'),'originalCoreResultSha256':sha(R/'LOCAL_BATCH_RESULT.json'),'collectionResult':state,'expectedSnapshotWriterCases':4,'authenticatedWriterCases':passed,'cases':rows,'runtimeAcceptance':False,'semanticVerdictsChanged':False,'sourceChanged':False,'counterCapped':False,'newPlayerLaunches':0,'classifierSha256':sha(classifier),'fullProducerLength':'Unavailable unless independently captured; reason9 prefix262145 is not exact full size','syntheticProducerSubstituted':False});print(json.dumps({'collectionResult':state,'semanticBatchResult':core['result'],'writers':[(r['caseId'],r['writerEvidence'],r.get('classification',{}).get('firstFailure')) for r in writers]}),flush=True)
