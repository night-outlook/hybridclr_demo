from pathlib import Path
import json,hashlib,tarfile,collections,re,os,subprocess,datetime,sys
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-Initializer06');B=P.parent;W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';O=B/'R03IR-Initializer-20261107-oneuse-06';HR=O.with_name(O.name+'-native-host-raw');load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def strict(raw):
 def pairs(rows):
  d={}
  for k,v in rows:assert k not in d;d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
run=load(P/'runner-COMMAND.json');assert run['runnerInvocations']==1 and not run['retryPerformed'] and sha(Path(run['stdout']))==run['stdoutSha256'] and sha(Path(run['stderr']))==run['stderrSha256']
r=load(O/'LOCAL_BATCH_RESULT.json');ledger=load(O/'BATCH_EXECUTION.json');assert sha(O/'BATCH_EXECUTION.json')==r['executionLedgerSha256'] and all(r[k]==v for k,v in ledger.items())
expected=['entry-authority','initializer-host-contracts','original-s-archive','original-s-process-joins','audit_s_generated_material','audit_s_binary_linkage','real-dll-fixtures','ir-generator-build','initializer-native-targets','prepare-release','prepare-initializer','build-initializer','player-initializer-control','player-initializer-failure','final-authority'];assert [c['id'] for c in r['cells']]==expected
for c in r['cells']:assert load(O/'cells'/(c['id']+'.json'))==c
states={c['id']:c['result'] for c in r['cells']};counts=dict(collections.Counter(states.values()))
for k in ['runtimeAcceptance','R03Accepted','H2Passed','ReadyForHumanReviewGate','qualificationApproved','fullLegacyRegressionAcceptance','pureInterpreterExpansionEnabled']:assert r[k] is False
source='611ad2e45a92ebfbd07cb64238bf2f47b5aff626';pins={'hybridclr_demo':source,'hybridclr':'4b2774b066cfc6afd77a8c8aded6bda7ea574f55','hybridclr_unity':'948c0e3b4f8891481301770115e8ba4945eea6de','il2cpp_plus':'41764ae1eeefb33b05966e7f7676e52aae39c340'};assert all(r['repositories'][n]==h for n,h in pins.items())
commands=[]
for p in sorted((O/'commands').glob('*/command.json')):
 c=load(p);assert sha(p.parent/'stdout.log')==c['stdoutSha256'] and sha(p.parent/'stderr.log')==c['stderrSha256'];commands.append({'receipt':str(p),'receiptSha256':sha(p),**c})
assert len({c['pid'] for c in commands})==len(commands)
seal=None;sealMembers=None
if r['sealStatus']=='Passed':
 seal=load(O/'seal-receipt.json');idx=load(O/'evidence-index.json');assert sha(O/'evidence-index.json')==seal['indexSha256'] and sha(O/'evidence.tar.gz')==seal['archiveSha256']
 for row in idx['files']:
  p=O/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256']
 with tarfile.open(O/'evidence.tar.gz','r:gz') as tf:
  members=tf.getmembers();assert len(members)==seal['members']==len(idx['files'])+1 and {m.name for m in members}=={x['path'] for x in idx['files']}|{'evidence-index.json'}
  for m in members:
   assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts;h=hashlib.sha256()
   with tf.extractfile(m) as f:
    for v in iter(lambda:f.read(1048576),b''):h.update(v)
   assert h.hexdigest()==sha(O/m.name)
  sealMembers=len(members)
hostSummary={'result':'UnavailableOrNotRun'}
if (HR/'RESULT.json').exists():
 host=load(HR/'RESULT.json');hostSummary={'result':host['result'],'components':host.get('components'),'sourcePreserved':host.get('sourcePreserved')}
 if states['initializer-host-contracts']=='Passed':
  assert host['result']=='PassedHostOnlyTenComponents' and len(host['components'])==10 and all(c['status']=='Passed' for c in host['components']) and host['sourcePreserved'] and host['originalSourceHashes']==host['finalSourceHashes'];assert host['expectedDemo']==source and host['expectedNative']==pins['il2cpp_plus'];legacy=load(HR/'historical-eight/RESULT.json');assert len(legacy['commands'])==8 and sha(HR/'historical-eight/RESULT.json')==host['historicalEightResultSha256']
  for c in legacy['commands']:
   p=Path(c['resultRoot']);assert p.is_relative_to(HR) and c['status']=='Passed' and load(p/'command.json')==c and sha(p/'stdout.bin')==c['stdoutSha256'] and sha(p/'stderr.bin')==c['stderrSha256']
  for name in ['native-owner-method-classifier','native-owner-full-tu']:
   p=HR/'steps'/name;c=load(p/'RESULT.json');assert c['state']=='Passed' and c['exitCode']==0 and not c['timedOut'] and not c['mayHaveExternalOwnedChildren'] and not c['postCleanupGroupExists'] and sha(p/'stdout.log')==c['stdoutSha256'] and sha(p/'stderr.log')==c['stderrSha256']
unitTests=[]
for c in commands:
 name=next((Path(str(v)).name for v in c['command'] if str(v).startswith('test_initializer_') or '/test_initializer_' in str(v)),None)
 if name:
  log=(Path(c['receipt']).parent/'stderr.log').read_text();m=re.search(r'(?m)^Ran (\d+) tests? in ',log);unitTests.append({'name':name,'count':int(m.group(1)) if m else None,'exitCode':c['exitCode'],'pid':c['pid'],'receipt':c['receipt']})
build=None;bp=O/'builds/candidate-release/build-receipt.json'
if bp.exists():
 br=load(bp);cfg=load(bp.parent/'config.json');build={'receipt':str(bp),'sha256':sha(bp),'result':br['result'],'errors':br.get('errors'),'warnings':br.get('warnings'),'buildPipelineResult':br.get('buildPipelineResult'),'config':cfg}
 if states['build-initializer']=='Passed':
  assert br['result']=='Passed' and br['errors']==0 and br['buildPipelineResult']=='Succeeded' and br['unityVersion']=='2022.3.62f2' and br['architecture']=='arm64' and br['nonGeneratedCorePreserved'] is True
  for key in ['featureEnabled','diagnosticsLevel','cppConfiguration','outputPath','projectPath','sourceManifestSha256']:assert br[key]==cfg[key]
  overlay=Path(cfg['overlayPath']);installed=Path(br['installedNativeRoot'])/'vm/AssemblyShadowR03Probe.cpp';assert sha(overlay)==cfg['overlaySha256']==br['testOverlaySha256']==sha(installed)
  manifest=Path(cfg['projectPath'])/'source-inputs.json';assert sha(manifest)==cfg['sourceManifestSha256']
  for row in load(manifest)['files']:assert sha(Path(cfg['projectPath'])/row['path'])==row['sha256']
  app=Path(cfg['outputPath']);exes=[p for p in (app/'Contents/MacOS').iterdir() if p.is_file()];assert len(exes)==1;exe=exes[0];arch=subprocess.run(['lipo','-archs',str(exe)],capture_output=True,text=True,timeout=30);assert arch.returncode==0 and arch.stdout.strip()=='arm64'
  for row in br['playerFiles']:
   p=app/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row.get('size',row.get('bytes'))
  build.update(executable=str(exe),executableSha256=sha(exe),architecture='arm64',installedOverlay=str(installed),overlaySha256=sha(overlay),sourceManifestSha256=sha(manifest),playerInventoryFiles=len(br['playerFiles']))
original=[]
for name in ['original-s-provenance/audit.json','original-s-process-joins/process-joins.json','original-s-generated_material.json','original-s-binary_linkage.json']:
 p=O/name
 if p.exists():original.append({'path':str(p),'sha256':sha(p),'report':load(p)})
targets=[];tp=O/'host/initializer-native-targets/initializer-native-targets.json'
if tp.exists():
 report=load(tp)
 assert report['expectsNativeModule']=='__InternalDynamic' and report['interpreterImportContract']=='R03IR.InterpreterCurrentProcessImport.V2'
 identities={
  'initializer-control':('d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e','5bb6e17a-09b9-5b29-dac2-41d3519f76f4'),
  'initializer-failure':('6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370','f61d7325-6d38-4640-5873-37371f587b16'),
 }
 assert {row['kind'] for row in report['targets']}==set(identities) and len(report['targets'])==2
 for row in report['targets']:
  assert (row['sha256'],row['mvid'])==identities[row['kind']] and row['size']==2560 and row['expectedNativeModule']=='__InternalDynamic'
  p=tp.parent/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];targets.append(row)
players=[];traces=[];recovery=[];sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03IR'));import verify_initializer_recovery as recoveryVerifier
expectedTargets={'initializer-control':'d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e','initializer-failure':'6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370'}
for mode,fixture in expectedTargets.items():
 root=O/'players'/('IR-R03-02-'+mode);player={'case':mode,'state':states['player-'+mode],'root':str(root),'rawPresent':(root/'raw.json').exists()}
 if (root/'request.json').exists():
  req=load(root/'request.json');cmds=[c for c in commands if '-r03IrInitializerRunId' in c['command'] and req['runId'] in c['command']];assert len(cmds)==1;c=cmds[0];player.update(request=req,commandPid=c['pid'],commandExit=c['exitCode'],commandReceipt=c['receipt']);assert req['dllSha256']==fixture and sha(Path(req['dllPath']))==fixture
  if (root/'raw.json').exists():player.update(rawBytes=(root/'raw.json').stat().st_size,rawSha256=sha(root/'raw.json'))
  if (root/'verification.json').exists():player['verification']=load(root/'verification.json')
  if player['state']=='Passed':
   data=strict((root/'raw.json').read_bytes());v=player['verification'];assert c['exitCode']==0 and v['result']=='PassedFocusedV1PlayerObservation_NotV2';assert data['runId']==req['runId']==v['runId'] and data['caseId']==req['caseId']==v['caseId'] and data['processId']==c['pid']==v['launchPid'];assert data['fixtureSha256']==fixture and v['rawSha256']==sha(root/'raw.json') and v['requestSha256']==sha(root/'request.json') and v['buildReceiptSha256']==sha(bp) and v['executableSha256']==build['executableSha256'];assert (data['commitReturn'],data['finalState'])==((0,6) if mode=='initializer-control' else (19,9)) and data['preparedField']==data['finalField']==3 and data['positiveMask']==15 and data['initializerCallbackCalls']==1 and data['nativeObserverBoundBeforeFailure'] is True and data['postAotAttempted'] is (mode=='initializer-failure');assert all(data[k] is False for k in ['postAotSucceeded','runtimeAcceptance','R03Accepted','H2Passed']);player['raw']=data
  trace=root/'raw.json.native-trace.jsonl';t={'case':mode,'present':trace.exists()}
  if trace.exists():
   raw=trace.read_bytes();assert 0<len(raw)<=65536 and raw.endswith(b'\n') and b'\r' not in raw;lines=raw.splitlines(keepends=True);assert len(lines)<=128;events=[]
   for seq,line in enumerate(lines,1):
    assert len(line)<=512;v=strict(line);assert set(v)=={'kind','runId','caseId','stimulus','fixtureSha256','pid','seq','phase','a','b','c','d','runtimeAcceptance','R03Accepted','H2Passed'} and v['kind']=='R03IRInitializerNativeTraceV1' and v['runId']==req['runId'] and v['caseId']==req['caseId'] and v['pid']==c['pid'] and v['seq']==seq and v['fixtureSha256']==fixture and v['stimulus']==req['stimulus'];assert all(type(v[k]) is int for k in ['pid','seq','phase','a','b','c','d']) and all(v[k] is False for k in ['runtimeAcceptance','R03Accepted','H2Passed']);events.append(v)
   if player['state']=='Passed':
    phases={phase:[v for v in events if v['phase']==phase] for phase in (299,300,400,401,601,620,211)}
    def values(phase):
     [event]=phases[phase]
     return tuple(event[k] for k in 'abcd')
    assert values(299)[0]==1 and values(300)==(1,3,15,1)
    commit=[v for v in events if v['phase']==191]
    assert len(commit)==1 and phases[299][0]['seq']<phases[300][0]['seq']<commit[0]['seq']
    assert values(400)[0]==1 and values(400)[2:]==(3,1) and values(401)[:3]==(3,1,15)
    assert values(601)[:2]==(1,1) and values(620)[0]==1
    if mode=='initializer-failure':assert values(211)[:2]==(0,1)
    else:assert not phases[211]
   t.update(path=str(trace),sha256=sha(trace),bytes=len(raw),events=events)
  traces.append(t);rec=root/'raw.json.vm-recovery.json';v={'case':mode,'present':rec.exists()}
  if rec.exists():
   v.update(path=str(rec),rawSha256=sha(rec),rawBytes=rec.stat().st_size)
   try:
    raw=rec.read_bytes();data=strict(raw);core=data['nativeRecovery'];assert 0<len(raw)<=20000 and raw.endswith(b'\n') and raw.count(b'\n')==1 and set(data)==set(recoveryVerifier.EXPECTED) and set(core)==set(recoveryVerifier.CORE);assert data['processId']==c['pid'] and data['runId']==req['runId'] and data['caseId']==req['caseId'] and data['fixtureSha256']==fixture and type(data['nativeReturn']) is int and data['nativeReturn']==0 and all(data[k] is False for k in ['runtimeAcceptance','R03Accepted','H2Passed']);v.update(independentEnvelopeJoins='Passed',nativeRecovery=core,productionParserCrossCheck=recoveryVerifier.inspect(rec,req,c['pid'],fixture),diagnosticOnly=True)
   except (ValueError,AssertionError,KeyError,UnicodeError) as e:v.update(independentEnvelopeJoins='Rejected',error=repr(e),diagnosticOnly=True)
  if player['state']=='Passed':
   assert v['independentEnvelopeJoins']=='Passed'
   core=v['nativeRecovery']
   if mode=='initializer-failure':
    assert core['stateCode']==9 and core['terminalFailureCode']==19 and 'R03IR.InitializerFailure.AfterPublication.V1' in core['reason']
   else:
    assert core['stateCode']==6 and core['terminalFailureCode']==0 and core['reason']==''
  recovery.append(v)
 players.append(player)
hostCustody={'result':'UnavailableOrNotRun'}
if (O/'host-custody/HOST_CUSTODY_RESULT.json').exists():
 hc=O/'host-custody';hcResult=load(hc/'HOST_CUSTODY_RESULT.json');hm=load(hc/'HOST_MANIFEST.json');assert hcResult['result']=='PassedFullRegularBytesAndLiteralSymlinkTargets' and hcResult['symlinkCount']==4 and hm['rawHostPath']==str(HR);assert sha(hc/'HOST_MANIFEST.json')==hcResult['manifestSha256'] and sha(hc/'HOST_REGULAR_BYTES.tar.gz')==hcResult['archiveSha256'];entries={}
 for row in hm['entries']:
  p=HR/row['path']
  if row['kind']=='file':assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256'];entries[row['path']]=row
  elif row['kind']=='symlink':assert p.is_symlink() and os.readlink(p)==row['target']
  else:assert p.is_dir() and not p.is_symlink()
 entries['HOST_MANIFEST.json']={'size':(hc/'HOST_MANIFEST.json').stat().st_size,'sha256':sha(hc/'HOST_MANIFEST.json')}
 with tarfile.open(hc/'HOST_REGULAR_BYTES.tar.gz') as tf:
  members=tf.getmembers();assert len(members)==len(entries) and {m.name for m in members}==set(entries)
  for m in members:
   assert m.isfile() and m.size==entries[m.name]['size'];h=hashlib.sha256()
   with tf.extractfile(m) as f:
    for v in iter(lambda:f.read(1048576),b''):h.update(v)
   assert h.hexdigest()==entries[m.name]['sha256']
 assert r['actualNativeHostCustodyPostflight']['result']=='PassedFullRawHostAndArchiveBinding_NoRuntimeAcceptance';hostCustody=hcResult
if r['result']=='FocusedInitializerEvidenceReadyForIndependentReview':assert counts=={'Passed':15} and r['verifiedFreshUnityBuilds']==1 and r['verifiedFreshInitializerPlayers']==2 and len({p['commandPid'] for p in players})==2
x={'kind':'IndependentInitializer06ReceiptCustodyAndDiagnosticsAudit','startUtc':start,'endUtc':now(),'result':'PassedReceiptAndCustodyAudit_ProducerSemanticResultRetained','sourcePins':pins,'producerRepositoryRecord':r['repositories'],'producerResult':r['result'],'runnerExit':run['exitCode'],'runnerInvocations':1,'cellCounts':counts,'cellStates':states,'firstFailedCell':next((c for c in r['cells'] if c['result']=='Failed'),None),'sealStatus':r['sealStatus'],'seal':seal,'archiveMembers':sealMembers,'commands':commands,'nativeHost':hostSummary,'initializerUnitTests':unitTests,'originalSAudits':original,'targets':targets,'build':build,'players':players,'nativeTraceChecks':traces,'nativeRecoveryChecks':recovery,'hostCustody':hostCustody,'runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False}
p=P/'FINAL_INDEPENDENT_AUDIT.json';assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n');print('Independent audit complete:',r['result'],counts,'seal',r['sealStatus']);print('VM reasons',[(v['case'],v.get('nativeRecovery',{}).get('reason'),v.get('independentEnvelopeJoins')) for v in recovery])
