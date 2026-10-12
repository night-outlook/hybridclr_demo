from h_common import *
import concurrent.futures,tarfile
start=now();assert subprocess.check_output(['git','-C',str(D),'hash-object',str(hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/test_scoped_custody.py')],text=True).strip()=='86f79849f2f4a5771e509815b3a005d3d9f3b0a6';clean_sources();no_unity();rows=[]
checks=[('local-validation-20261009-ir-r03-02-c-custody-blocked','36b9828d62bb81d98e81d055871a9540fe116276','87607f109cf1d50a3fb7bdf1b69789f401734298ca65a11e627d52d52f2b26a1'),('local-validation-20261010-ir-r03-02-e-native-receipt','75500e3916300d1fd5f7774e0f9de33b9ed3e7da','3a84dde9cc7599d9b3a38babee6ad92d347c0ddc365b2dc3b84a5ae5a23ceb0f'),('local-validation-20261010-ir-r03-02-f-compile-only','a9483a6e2212701cfedcf93faeb0e71ce82b73ca','c7fc7664311907feccf88862c2654529774b9da52e873dd96688c7a921e049e0'),('local-validation-h-post-gcomp-7d42','588cafb044e7d5e6da185368c5f69da709903bc4','f705fd9253aab7fdd081dae739600a3b56951996b0662f070380d33ee458c8e5'),('local-validation-i-post-h-custody-7f36','3a3d8f384bd6f02e7a685f2e3aae5758e850d72a','944eac81540a676de3bff07268742de1e19fe54597ae1995946617c14e840ec4'),('local-validation-20261011-ir-r03-02-g-compile-only','4808743fcbbc2075b9be305140bdf5ffa8583b0f','eda067e3a425fab00a1754d1f8dfbc3b444b409e70c7832940bec2609cd37fec')]
for name,commit,mhash in checks:
 C=hist/name;assert sha(C/'MANIFEST.sha256')==mhash;raw=subprocess.check_output(['git','-C',str(D),'ls-tree','-r','-z',commit,'--',str(C.relative_to(D))]);blobs={r.split(b'\t',1)[1].decode():r.split(b'\t',1)[0].split()[2].decode() for r in raw.split(b'\0') if r};declared={n:h for h,n in (l.split('  ',1) for l in (C/'MANIFEST.sha256').read_text().splitlines())};actual={str(f.relative_to(C)) for f in C.rglob('*') if f.is_file()};assert actual==set(declared)|{'MANIFEST.sha256'}
 for n in actual:
  f=C/n;assert not f.is_symlink() and sha(f)==(mhash if n=='MANIFEST.sha256' else declared[n]);blob=hashlib.sha1(('blob '+str(f.stat().st_size)+'\0').encode())
  with f.open('rb') as s:
   while data:=s.read(1024**2):blob.update(data)
  assert blob.hexdigest()==blobs[str(f.relative_to(D))]
 rows.append({'checkpoint':str(C),'publication':commit,'manifestSha256':mhash,'manifestFiles':len(declared),'allFilesAndGitBlobsVerified':True})
G=hist/checks[-1][0];assert subprocess.check_output(['git','-C',str(D),'rev-parse','4808743fcbbc2075b9be305140bdf5ffa8583b0f:'+str((G/'MANIFEST.sha256').relative_to(D))],text=True).strip()=='4dc786b14983cc099e87cbd58189c9816f890de9'
for rel,blob in [('Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs','bbced69dee847a7f6b5b721fd55635976acf42a4'),('Tools/AssemblyShadow/R03IR/run_terminal_local.py','386d47c041cf18a46ce741a269cd1ed1fd959d95'),('Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py','064795791687b50033fd247f28d6ae2ab25a8909'),('Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp','a23f927e28714ae6d4eb62c76e6127f96c9f709f'),('Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py','ccc6af25d5d424b3bffe629ebd609ec5e5beed0a'),('Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/verify_retained_e.py','52d1c177ba216bb0164099c082b1f3e9a2e6b40d')]:assert subprocess.check_output(['git','-C',str(D),'hash-object',str(D/rel)],text=True).strip()==blob
for f in G.glob('managed/commands/*/command.json'):
 r=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==r[n+'Sha256']
for f in G.glob('native/commands/*/command.json'):
 r=load(f)
 for n in ['stdout','stderr']:assert sha(f.parent/(n+'.log'))==r[n+'Sha256']
precommands=list((G/'preflight/commands').glob('*/receipt.json'))
for f in precommands:
 r=load(f)
 for n in ['stdout','stderr']:assert sha(G/'preflight/commands'/f.parent.name/(n+'.log'))==r[n+'Sha256']
assert len(precommands)+len(list(G.glob('managed/commands/*/command.json')))+len(list(G.glob('native/commands/*/command.json')))==77
correction=hist/'IR_Remediation/IR_LOCAL_CUSTODY_03_2026-10-12';ci=load(correction/'EVIDENCE.json');assert sha(hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/test_scoped_custody.py')==ci['fixed']['correctedTestSha256'];assert sha(hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py')==ci['fixed']['productionVerifierSha256Unchanged']
for k in ['macos','ubuntu']:
 r=ci['ci'][k];f=correction/r['retainedLogPath'];assert sha(f)==r['artifactLogSha256'] and f.stat().st_size==r['artifactLogBytes'];assert subprocess.check_output(['git','-C',str(D),'hash-object',str(f)],text=True).strip()==r['retainedGitBlob']
save(P/'PRIMARY_CI_AUTHENTICATION.json',{'state':'Passed','classification':'Published source/log authentication; CI attributed, not fresh Local tests','CIrun':38197141796,'correctedTestBlob':ci['fixed']['correctedTestBlob'],'verifierUnchanged':True,'logsAuthenticated':['macos','ubuntu']})
doc=hist/'IR_Remediation/IR_I_RESPONSE_RESERVE_6f02';j=load(doc/'EVIDENCE.json');ci_audit=load(doc/'OFFICIAL_SDK_CI_AUDIT.json');assert ci_audit['nativeSyntaxConfigurations']==55 and ci_audit['sourcePins']['il2cpp_plus']==pins['il2cpp_plus']
for row in j['retainedNativeLogs']:
 f=doc/row['path'];assert sha(f)==row['sha256'] and f.stat().st_size==row['bytes']
for osname in ['macos','ubuntu']:
 r=j['collectorCI'][osname];assert sha(doc/r['logPath'])==r['logSha256']
for rel,key in [('libil2cpp/vm/AssemblyShadowFixedBoolean.h','reserveHeader'),('libil2cpp/vm/Runtime.cpp','runtime')]:
 f=W/'il2cpp_plus'/rel;assert sha(f)==j['nativeCandidate'][key+'Sha256'];assert subprocess.check_output(['git','-C',str(W/'il2cpp_plus'),'hash-object',str(f)],text=True).strip()==j['nativeCandidate'][key+'Blob']
for rel,key in [('collect_i_debug_cache.py','collector'),('test_debug_collection.py','test')]:
 f=doc/rel;assert sha(f)==j['collectorCI'][key+'Sha256'];assert subprocess.check_output(['git','-C',str(D),'hash-object',str(f)],text=True).strip()==j['collectorCI'][key+'Blob']
for r in ci_audit['changedSourceVerified']:assert sha(W/r['path'])==r['sha256']
assert not subprocess.check_output(['git','-C',str(D),'diff','9683079fb84cc5af5a505dc027f084324380b9a7',pins['hybridclr_demo'],'--','Tools','Assets','Packages','ProjectSettings'],text=True).strip()
# Original I live indexed records and all three installed SDK/native inventories.
I=H;icp=hist/'local-validation-i-post-h-custody-7f36';audit=load(icp/'preflight/FINAL_EVIDENCE_AUDIT.json')
for r in audit['topArtifacts']:assert sha(r['path'])==r['sha256']
index_i=load(I/'evidence-index.json');assert len(index_i['files'])==994
for r in index_i['files']:
 f=I/r['path'];assert f.stat().st_size==r['size'] and sha(f)==r['sha256']
for r in audit['builds']:
 root=Path(r['installedNativeRoot'])
 for x in r['installedFileInventory']:assert (root/x['path']).stat().st_size==x['size'] and sha(root/x['path'])==x['sha256']
# Authenticate the exact collector's original I anchors without collecting Bee yet.
import importlib.util
spec=importlib.util.spec_from_file_location('jcollector',doc/'collect_i_debug_cache.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector);anchors=collector.authenticate_original(D)
save(P/'J_SOURCE_BINDINGS.json',{'state':'Passed','pins':pins,'primaryEvidenceSha256':sha(doc/'EVIDENCE.json'),'officialCiAuditSha256':sha(doc/'OFFICIAL_SDK_CI_AUDIT.json'),'officialCiResult':'Attributed CI compilation Passed; not fresh Local','currentSources':[dict(r,path=str(W/r['path'])) for r in ci_audit['changedSourceVerified']],'collectorBlob':j['collectorCI']['collectorBlob'],'collectorSha256':j['collectorCI']['collectorSha256'],'originalIIndexedFiles':994,'originalINativeInventoryFiles':sum(len(r['installedFileInventory']) for r in audit['builds']),'originalIAnchors':anchors,'IResult':'FAIL unchanged'})
managed=load(G/'managed/build-api/results.json');native=load(G/'native/results.json');assert managed['result']==native['result']=='Passed' and len(native['translationUnits'])==55 and len(managed['commands'])==6
for r in managed['inputs']:assert sha(r['path'])==r['sha256'],r
# Old G native c386 is historical; new0fa requires fresh J matrix.
for r in load(G/'SOURCE_BINDINGS.json'):
 if r['repository'].endswith('/hybridclr_unity') or (r['repository'].endswith('/hybridclr_demo') and not r['path'].startswith('Docs/AssemblyShadow/') and r['path']!='Tools/AssemblyShadow/R03/source-pins.json'):assert sha(Path(r['repository'])/r['path'])==r['sha256']
# Original S indexed/sealed evidence. Historical native roots are NOT restored.
C=hist/checks[0][0];a=load(C/'preflight/CUSTODY_FAILURE_ANALYSIS.json');S=B/'R03LocalBatch-20261007S-lr-recovery';tops={n:sha(S/n) for n in a['sealedS']['topArtifactHashes']};assert tops==a['sealedS']['topArtifactHashes'];index=load(S/'evidence-index.json');assert len(index['files'])==15712
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:assert all(pool.map(lambda r:sha(S/r['path'])==r['sha256'] and (S/r['path']).stat().st_size==r['size'],index['files']))
with tarfile.open(S/'evidence.tar.gz','r:gz') as t:
 members=t.getmembers();assert len(members)==15713 and {r['path'] for r in index['files']}<={r.name for r in members}
assert (S/'evidence.tar.gz').stat().st_size==587907380
sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03'));sys.path.insert(0,str(D/'Tools/AssemblyShadow/R03IR'));from ir_original_fixtures import stage_immutable_original_s
entries,receipt=stage_immutable_original_s(D,P/'original-s-fixtures',sha);assert len(entries)==15
save(P/'ORIGINAL_INPUT_PREFLIGHT.json',{'state':'Passed','startUtc':start,'endUtc':now(),'fixtures':15,'authorityReceipt':str(receipt),'authoritySha256':sha(receipt),'regenerated':False,'sIndexFilesVerified':15712,'sArchiveMembers':15713,'sTopArtifactHashes':tops,'strictCustody':'Blocked','runtimeAcceptance':False})
save(P/'G_EQUIVALENCE.json',{'state':'Passed','classification':'ReusedAuditedManagedCompilation','startUtc':start,'endUtc':now(),'sourcePins':pins,'GExecutionDemo':'d7f46bfd090313b41b38175ce1196f14484a3d1e','GPublication':'4808743fcbbc2075b9be305140bdf5ffa8583b0f','compiledInputsUnchanged':428,'managedProducts':5,'expectedNegativeControls':1,'historicalGNativeConfigurations':55,'currentJNativeConfigurations':'NotRun until shared admission','originalGManifestFiles':544,'GCompilerScriptsReinvoked':False,'originalCheckpoints':rows,'retainedEState':'FAIL','retainedFState':'PrerequisiteBlocked','retainedGState':'Passed compile-only','strictHistoricalCustody':'Blocked'})
print(json.dumps({'state':'Passed','classification':'ReusedAuditedManagedCompilation','originalFixtures':len(entries),'originalSFiles':15712}),flush=True)
