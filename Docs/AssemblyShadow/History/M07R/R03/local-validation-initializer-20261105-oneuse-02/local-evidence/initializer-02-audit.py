from pathlib import Path
import json,hashlib,subprocess,datetime,tarfile,collections,re,os
B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';O=B/'R03IR-Initializer-20261105-oneuse-02';now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();start=now();load=lambda p:json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for v in iter(lambda:f.read(1048576),b''):h.update(v)
 return h.hexdigest()
def strict(data):
 def pairs(rows):
  d={}
  for k,v in rows:assert k not in d;d[k]=v
  return d
 return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
run=load(B/'initializer-02-runner-COMMAND.json');assert run['initializerRunnerInvocations']==1 and run['retryPerformed'] is False and sha(Path(run['stdout']))==run['stdoutSha256'] and sha(Path(run['stderr']))==run['stderrSha256']
r=load(O/'LOCAL_BATCH_RESULT.json');ledger=load(O/'BATCH_EXECUTION.json');assert r['kind']=='R03IRInitializerOneUseEvidenceBatchV1' and sha(O/'BATCH_EXECUTION.json')==r['executionLedgerSha256'] and all(r[k]==v for k,v in ledger.items())
expected=['entry-authority','initializer-host-contracts','original-s-archive','original-s-process-joins','audit_s_generated_material','audit_s_binary_linkage','real-dll-fixtures','ir-generator-build','initializer-native-targets','prepare-release','prepare-initializer','build-initializer','player-initializer-control','player-initializer-failure','final-authority'];assert [c['id'] for c in r['cells']]==expected
for c in r['cells']:assert load(O/'cells'/f"{c['id']}.json")==c
states={c['id']:c['result'] for c in r['cells']};counts=dict(collections.Counter(states.values()));assert set(counts)<= {'Passed','Failed','Blocked'}
for k in ['runtimeAcceptance','R03Accepted','H2Passed','ReadyForHumanReviewGate','qualificationApproved','fullLegacyRegressionAcceptance','pureInterpreterExpansionEnabled']:assert r[k] is False
idx=None;seal=None;sealFailure=None
if r['sealStatus']=='Passed':
 idx=load(O/'evidence-index.json');seal=load(O/'seal-receipt.json');assert r['sealStatus']=='Passed' and sha(O/'evidence-index.json')==seal['indexSha256'] and sha(O/'evidence.tar.gz')==seal['archiveSha256']
 for row in idx['files']:
  p=O/row['path'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256']
 with tarfile.open(O/'evidence.tar.gz','r:gz') as t:
  members=t.getmembers();assert len(members)==seal['members']==len(idx['files'])+1 and len({m.name for m in members})==len(members)
  assert {m.name for m in members}=={x['path'] for x in idx['files']}|{'evidence-index.json'}
  for m in members:
   assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
   h=hashlib.sha256()
   with t.extractfile(m) as f:
    for v in iter(lambda:f.read(1048576),b''):h.update(v)
   assert h.hexdigest()==sha(O/m.name)
else:
 assert r['sealStatus']=='Failed' and r['result']=='ReturnRequired'
 sealFailure=load(O/'SEAL_FAILED.json');assert sealFailure['error']==r['sealError']
 assert not any((O/n).exists() for n in ['evidence-index.json','evidence.tar.gz','seal-receipt.json'])
 rel=r['sealError'].split('Unexpected directory symlink: ',1)[1];alias=O/rel;assert alias.is_symlink()
 sealFailure.update(aliasPath=str(alias),aliasTarget=os.readlink(alias),noIndexArchiveReceipt=True)
commands=[]
for p in sorted((O/'commands').glob('*/command.json')):
 c=load(p);assert sha(p.parent/'stdout.log')==c['stdoutSha256'] and sha(p.parent/'stderr.log')==c['stderrSha256'];commands.append(dict(receipt=str(p),receiptSha256=sha(p),**c))
assert len({x['pid'] for x in commands})==len(commands)
# Authenticate the ten actual host components and their nested receipts.
hostRoot=O/'native-host-diagnostics';host=load(hostRoot/'RESULT.json');legacy=load(hostRoot/'historical-eight/RESULT.json');assert host['result']=='PassedHostOnlyTenComponents' and len(host['components'])==10 and all(x['status']=='Passed' for x in host['components']) and host['sourcePreserved'] and host['originalSourceHashes']==host['finalSourceHashes'];assert host['expectedDemo']==r['repositories']['hybridclr_demo'] and host['expectedNative']==r['repositories']['il2cpp_plus'];assert len(legacy['commands'])==8 and sha(hostRoot/'historical-eight/RESULT.json')==host['historicalEightResultSha256']
for c in legacy['commands']:
 root=Path(c['resultRoot']);assert root.is_relative_to(hostRoot) and c['status']=='Passed' and load(root/'command.json')==c and sha(root/'stdout.bin')==c['stdoutSha256'] and sha(root/'stderr.bin')==c['stderrSha256']
owner=[]
for name,tests in [('native-owner-method-classifier',2),('native-owner-full-tu',3)]:
 root=hostRoot/'steps'/name;c=load(root/'RESULT.json');assert c['state']=='Passed' and c['exitCode']==0 and not c['timedOut'] and not c['mayHaveExternalOwnedChildren'] and not c['postCleanupGroupExists'];assert sha(root/'stdout.log')==c['stdoutSha256'] and sha(root/'stderr.log')==c['stderrSha256'];assert re.search(r'(?m)^Ran '+str(tests)+r' tests? in ',(root/'stderr.log').read_text());owner.append(dict(name=name,tests=tests,pid=c['processId'],end=c['finishedUtc']))
for path,h in host['originalSourceHashes'].items():assert sha(Path(path))==h
hostTests=[]
for name,n in [('test_initializer_observer_native.py',1),('test_initializer_writer_host.py',4),('test_initializer_observation.py',8),('test_initializer_source_preparation.py',12),('test_initializer_local_orchestration.py',4)]:
 matches=[c for c in commands if name in c['command']];assert len(matches)==1;cmd=matches[0];assert cmd['exitCode']==0;log=Path(cmd['receipt']).parent/'stderr.log';assert re.search(r'(?m)^Ran '+str(n)+r' tests? in ',log.read_text()) and re.search(r'(?m)^OK\s*$',log.read_text());hostTests.append(dict(name=name,tests=n,pid=cmd['pid'],receiptSha256=cmd['receiptSha256']))
# Original S audits authenticate retained historical material, not fresh historical Players.
a=load(O/'original-s-provenance/audit.json');j=load(O/'original-s-process-joins/process-joins.json');assert a['result']=='Passed' and a['archiveMembers']==15713 and a['cells']==90 and j['result']=='Passed' and j['totalPlayerReceipts']==59
original=[]
for name in ['original-s-generated_material.json','original-s-binary_linkage.json']:
 p=O/name;original.append(dict(path=str(p),sha256=sha(p),report=load(p)))
# Record actual target generation, preserving mismatch/failure if encountered.
targets=[];tp=O/'host/initializer-native-targets/initializer-native-targets.json'
if tp.exists():
 for t in load(tp)['targets']:
  p=tp.parent/t['path'];assert sha(p)==t['sha256'] and p.stat().st_size==t['size'];targets.append(t)
# Authenticate the actual build receipt, native overlay and source manifest.
buildPath=O/'builds/candidate-release/build-receipt.json';build=None
if buildPath.exists():
 br=load(buildPath);cfg=load(buildPath.parent/'config.json');build=dict(receipt=str(buildPath),sha256=sha(buildPath),result=br['result'],errors=br.get('errors'),warnings=br.get('warnings'),buildPipelineResult=br.get('buildPipelineResult'),config=cfg)
 if states['build-initializer']=='Passed':
  assert br['result']=='Passed' and br['errors']==0 and br['buildPipelineResult']=='Succeeded' and br['unityVersion']=='2022.3.62f2' and br['architecture']=='arm64' and br['nonGeneratedCorePreserved'] is True
  for k in ['featureEnabled','diagnosticsLevel','cppConfiguration','outputPath','projectPath','sourceManifestSha256']:assert br[k]==cfg[k]
  overlay=Path(cfg['overlayPath']);installed=Path(br['installedNativeRoot'])/'vm/AssemblyShadowR03Probe.cpp';assert sha(overlay)==cfg['overlaySha256']==br['testOverlaySha256']==sha(installed)
  manifest=Path(cfg['projectPath'])/'source-inputs.json';assert sha(manifest)==cfg['sourceManifestSha256']
  for item in load(manifest)['files']:assert sha(Path(cfg['projectPath'])/item['path'])==item['sha256']
  app=Path(cfg['outputPath']);executables=[p for p in (app/'Contents/MacOS').iterdir() if p.is_file()];assert len(executables)==1;exe=executables[0]
  arch=subprocess.run(['lipo','-archs',str(exe)],capture_output=True,text=True,timeout=30);assert arch.returncode==0 and arch.stdout.strip()=='arm64'
  build.update(installedOverlay=str(installed),overlaySha256=sha(overlay),executable=str(exe),executableSha256=sha(exe),sourceManifestSha256=sha(manifest),architecture=arch.stdout.strip(),playerInventoryFiles=len(br['playerFiles']))
  for item in br['playerFiles']:
   p=app/item['path'];assert sha(p)==item['sha256'] and p.stat().st_size==item.get('size',item.get('bytes'))
players=[]
expectedTargets={'initializer-control':'f909d3a4dd2ae3e561f1c0a2e25b50009203e440ce35a743afae937073e294a8','initializer-failure':'1cf13922d9f5798873a2581867f4dc0ea7415bd5ceee815e1b9489d99ce4937d'}
for mode,targetSha in expectedTargets.items():
 root=O/'players'/('IR-R03-02-'+mode);summary=dict(case=mode,state=states['player-'+mode],root=str(root),rawPresent=(root/'raw.json').exists())
 if (root/'request.json').exists():
  req=load(root/'request.json');matches=[c for c in commands if '-r03IrInitializerRunId' in c['command'] and req['runId'] in c['command']];assert len(matches)==1;c=matches[0];summary.update(request=req,commandReceipt=c['receipt'],commandPid=c['pid'],commandExit=c['exitCode'])
  if (root/'raw.json').exists():summary.update(rawBytes=(root/'raw.json').stat().st_size,rawSha256=sha(root/'raw.json'))
  if states['player-'+mode]=='Passed':
   v=load(root/'verification.json');raw=(root/'raw.json').read_bytes();assert 0<len(raw)<=2048;data=strict(raw);assert v['result']=='PassedFocusedV1PlayerObservation_NotV2' and c['exitCode']==0
   assert data['runId']==req['runId']==v['runId'] and data['caseId']==req['caseId']==v['caseId'] and data['processId']==c['pid']==v['launchPid']
   assert req['dllSha256']==targetSha==data['fixtureSha256']==sha(Path(req['dllPath'])) and sha(root/'raw.json')==v['rawSha256'] and sha(root/'request.json')==v['requestSha256'] and sha(buildPath)==v['buildReceiptSha256'] and build['executableSha256']==v['executableSha256'] and c['command'][0]==build['executable']
   assert data['kind']=='R03IRInitializerCommitObservationV1' and data['reportTransport']=='NativePreopenedInitializerObservationV1' and data['result']=='ObservedNotAccepted' and type(data['commitReturn']) is int and type(data['finalState']) is int and (data['commitReturn'],data['finalState'])==((0,6) if mode=='initializer-control' else (19,9))
   assert type(data['preparedField']) is int and type(data['finalField']) is int and data['preparedField']==data['finalField']==3 and data['positiveMask']==15 and data['initializerCallbackCalls']==1 and data['nativeObserverBoundBeforeFailure'] is True and data['postAotAttempted'] is (mode=='initializer-failure')
   for flag in ['postAotSucceeded','firstRecoveryAuthenticated','completeDiagnosticsAuthenticated','nativeV2TransportImplemented','runtimeAcceptance','R03Accepted','H2Passed']:assert data[flag] is False
   summary.update(raw=data,verificationSha256=sha(root/'verification.json'),independentJoin='PassedSourceBuildExecutableRequestRunPidFixtureRawBindings_NotRuntimeAcceptance')
 players.append(summary)
if r['result']=='FocusedInitializerEvidenceReadyForIndependentReview':assert counts=={'Passed':15} and r['verifiedFreshUnityBuilds']==1 and r['verifiedFreshInitializerPlayers']==2 and len({p['commandPid'] for p in players})==2
survivors=[]
for line in subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,pgid=,command='],text=True).splitlines():
 p=line.strip().split(None,3)
 if len(p)==4 and str(O) in p[3] and any(x in p[3].split(' ',1)[0] for x in ['Unity','dotnet','clang','python']):survivors.append(line)
assert not survivors
out=dict(kind='IndependentInitializer02EvidenceAudit',start=start,end=now(),result='PassedReceiptAudit_OriginalFailedProductSealRetained',sourcePins=r['repositories'],producerResult=r['result'],cellCounts=counts,cellStates=states,firstFailedCell=next((c for c in r['cells'] if c['result']=='Failed'),None),sealStatus=r['sealStatus'],archiveSha256=seal['archiveSha256'] if seal else None,indexSha256=seal['indexSha256'] if seal else None,indexedFiles=len(idx['files']) if idx else None,archiveMembers=seal['members'] if seal else None,sealFailure=sealFailure,commands=commands,actualNativeHostComponents=10,freshOwnerHostSuites=owner,initializerHostTests=hostTests,originalSArchiveMembers=15713,originalSHistoricalCells=90,originalSHistoricalPlayerJoins=59,originalSIndependentAdditionalAudits=original,targets=targets,build=build,players=players,ownedSurvivors=survivors,initializerRunnerInvocations=1,sourceChanged=False,retry=False,runtimeAcceptance=False,R03Accepted=False)
with (B/'initializer-02-FINAL_INDEPENDENT_AUDIT.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print('Independent evidence audit passed;actual semantic result',r['result'],counts)
