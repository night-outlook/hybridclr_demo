from h_common import *
import collections,shlex,re,importlib.util
O=B/'DebugBee-R03J-reserve-6f02';F=O/'files';start=now();collection=load(O/'collection.json');assert collection['result']=='CollectedForPrimaryAnalysis'
for r in collection['files']:assert (F/r['path']).stat().st_size==r['bytes'] and sha(F/r['path'])==r['sha256']
doc=hist/'IR_Remediation/IR_I_RESPONSE_RESERVE_6f02';spec=importlib.util.spec_from_file_location('jc',doc/'collect_i_debug_cache.py');jc=importlib.util.module_from_spec(spec);spec.loader.exec_module(jc)
rows,excluded=jc.inventory(jc.BEE);assert rows==collection['files'] and excluded==collection['excluded'];anchors=jc.authenticate_original(D)
dag=load(F/'Player8592df48.dag.json');events=[json.loads(s) for s in (F/'tundra.log.json').read_text().splitlines()];assert events[0]['dagFile']=='Library/Bee/Player8592df48.dag'
needle=jc.NEEDLE;literal=[]
for r in collection['files']:
 data=(F/r['path']).read_bytes()
 if needle in data:literal.append(r['path'])
assert not literal
command_i=load(H/'commands/0004/command.json');editor=H/'builds/candidate-debug/Editor.log';lines=editor.read_text().splitlines();editor_findings=[]
for i,line in enumerate(lines):
 if needle.decode() in line:editor_findings.append({'line':i+1,'text':line,'context':'\n'.join(lines[max(0,i-2):i+12])})
assert len(editor_findings)==2
children=[]
for index in [273,12]:
 node=dag['Nodes'][index];result=[r for r in events if r.get('msg')=='noderesult' and r.get('index')==index];assert len(result)==1;nr=result[0];assert node['Annotation']==nr['annotation'] and nr['exitcode']==0
 args=shlex.split(node['Action']);stdout=nr['stdout'];assert needle.decode() not in stdout
 label='clang-object' if index==273 else 'unitylinker'
 save(P/'bee-analysis'/('node-'+label+'.json'),{'classification':'Current-only collected node record; associated task, exact diagnostic emitter Unavailable','dagNodeIndex':index,'dagNode':node,'tundraNodeResult':nr,'actionArgvParsedNotExecuted':args,'outerOriginalICommand':command_i,'nodeSpecificEnvironmentOverrides':node['Env'],'completeInheritedChildEnvironment':'Unavailable; DAG Env is empty, only outer selected policy is recorded'})
 (P/'bee-analysis'/('node-'+label+'-stdout.log')).write_text(stdout)
 children.append({'nodeIndex':index,'label':label,'annotation':node['Annotation'],'executable':args[0],'argv':args,'recordedExitCode':0,'nodeSpecificEnv':node['Env'],'actualChildPid':'Unavailable; trace PID12345 is synthetic and not a launch receipt','stdoutBytesUtf8':len(stdout.encode()),'stdoutSha256':hashlib.sha256(stdout.encode()).hexdigest(),'literalSharedCacheDiagnosticInCapturedStdout':False,'dataPath':str(P/'bee-analysis'/('node-'+label+'.json'))})
# Bounded credential review without executing or decoding through external tools.
patterns={'pem-private-key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','github-token':rb'gh[pousr]_[A-Za-z0-9]{30,}','aws-access-key':rb'AKIA[0-9A-Z]{16}','bearer-token':rb'(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9._/-]{20,}','credential-assignment':rb'(?i)(?:password|access_token|api_key|client_secret)\s*[=:]\s*["\x27]?[A-Za-z0-9_/-]{16,}','authenticated-url':rb'https?://[^\s"\x27/@:]+:[^\s"\x27/@]+@'}
findings=[]
for r in collection['files']:
 data=(F/r['path']).read_bytes()
 for key,pattern in patterns.items():
  for m in re.finditer(pattern,data):findings.append({'path':r['path'],'kind':key,'offset':m.start()})
assert not findings,findings
save(P/'DIAGNOSTIC_PUBLICATION_REVIEW.json',{'state':'ReviewedForScopedPublication','recordedUtc':now(),'filesReviewed':len(collection['files']),'bytesReviewed':sum(r['bytes'] for r in collection['files']),'credentialPatternFindings':findings,'scopeReview':'Build DAG, response files, compiler/linker traces, build report and analytics for the exact retained I Debug project; paths and tool/run analytics are diagnostic context','publicationPolicy':'Preserve selected raw bytes including DAGs; no installed vendor SDK or executable binary content','redactions':[],'limitations':'Bounded pattern/structured review is not a guarantee of universal secret detection'})
save(P/'DEBUG_BEE_DIAGNOSIS.json',{'state':'CollectedAndInvestigatedReadOnly','startUtc':start,'endUtc':now(),'collectionFiles':len(collection['files']),'collectionBytes':sum(r['bytes'] for r in collection['files']),'collectionSha256':sha(O/'collection.json'),'originalIAnchors':anchors,'selectedOriginalInventoryAfterMatches':True,'collectedLiteralDiagnosticOccurrences':0,'editorOriginalOccurrences':editor_findings,'tundraMessages':dict(collections.Counter(r.get('msg') for r in events)),'associatedChildTasks':children,'actualSharedCacheDiagnosticEmitter':'Unavailable','emitterLimitation':'Exact diagnostic exists in Git-bound original Editor.log at DefaultResultProcessor/UnityLinkerResultProcessor. It is absent from all 40 selected Bee files and both associated node stdout records. Associated task actions/exits are retained, but they do not prove which process or task emitted the text or why allocation failed. No actual child PID or full inherited child environment is retained in these records. Binary/tool-based decoding and new execution were not performed.','cause':'Unavailable; no proof of ENOSPC, dyld identity, memory pressure or a bad cache','recommendedPrimaryDirection':'Inspect retained node/Editor reporting discrepancy and original binary BinLog provenance in a separately bounded assignment if available; preserve BuildReport errors and do not accept the debug app or suppress the diagnostic. Publish an exact repair/reproduction direction only when source or child records support it.','originalIDebugResult':'Failed errors2/warnings1; dependent Player Blocked/NotRun unchanged','UnityLaunches':0,'PlayerBuilds':0,'Players':0,'retries':0,'runtimeAcceptance':False})
print(json.dumps({'collectionFiles':len(collection['files']),'bytes':sum(r['bytes'] for r in collection['files']),'associatedNodeExits':[0,0],'actualEmitter':'Unavailable','originalInventoryAfter':'Passed','credentialReviewFindings':0}),flush=True)
