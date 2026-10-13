from h_common import *
import importlib.util
phase=sys.argv[1];assert phase in ['before','after'];start=now()
G=hist/'local-validation-20261011-ir-r03-02-g-compile-only';original=load(G/'preflight/INSTALLED_SDK_BEFORE.json');root=Path(original['root']);actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()};assert actual=={r['path'] for r in original['files']}
for r in original['files']:
 f=root/r['path'];assert f.stat().st_size==r['size'] and sha(f)==r['sha256'],f
for r in load(G/'preflight/SOURCE_ENVIRONMENT.json')['tools']:assert sha(r['path'])==r['sha256'] and str(Path(r['path']).resolve())==r['resolved']
current_inputs=[]
for r in load(G/'managed/build-api/inputs.json')['files']:
 f=Path(r['path']);h=sha(f)
 if f.is_relative_to(W):
  repo=next(W/n for n in pins if f.is_relative_to(W/n));rel=str(f.relative_to(repo));raw=subprocess.check_output(['git','-C',str(repo),'show',pins[repo.name]+':'+rel]);assert hashlib.sha256(raw).hexdigest()==h
 else:assert h==r['sha256']
 current_inputs.append({'path':str(f),'sha256':h,'historicalGHash':r['sha256'],'legitimateSourceDelta':h!=r['sha256']})
if phase=='before':save(P/'CURRENT_MANAGED_INPUTS_BEFORE.json',current_inputs)
else:assert load(P/'CURRENT_MANAGED_INPUTS_BEFORE.json')==current_inputs
for r in load(G/'managed/build-api/results.json')['packageAssemblies']:
 x=r['output'];assert sha(x['path'])==x['sha256']
for key in ['completeHelper','terminalPlayerApi']:
 x=load(G/'managed/build-api/results.json')[key];x=x.get('output',x);assert sha(x['path'])==x['sha256']
scratch=B/'Scratch-R03IRCompile-20261011G-canonical-temp';sdk=load(G/'native/native-sdk-inputs.json');assert {r['path'] for r in sdk['files']}=={str(f.relative_to(scratch)) for f in scratch.rglob('*') if f.is_file()}
for r in sdk['files']:assert sha(scratch/r['path'])==r['sha256']
verifier=hist/'IR_Remediation/IR_RUNTIME_01_2026-10-10/verify_retained_e.py';spec=importlib.util.spec_from_file_location('e_preservation',verifier);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
roots=[B/'R03IRLocal-I-post-H-custody-7f36',B/'Preflight-R03IRLocal-I-post-H-custody-7f36',B/'StorageCheck-R03IRLocal-I-post-H-custody-7f36',B/'Storage-R03IRLocal-I-post-H-custody-7f36',B/'Preflight-R03IRLocal-H-post-GCOMP-7d42',B/'Preflight-R03IRCompile-20261010F-runtime01']+[B/(n+'-R03IRCompile-20261011G-canonical-temp') for n in ['Preflight','ManagedAPI','NativeSDK','Scratch']]
roots += [B/n for n in ['Preflight-R03J-reserve-6f02','NativeSDK-R03J-reserve-6f02','Scratch-R03J-reserve-6f02','DebugBee-R03J-reserve-6f02']]
roots += [B/n for n in ['Preflight-R03K-after-J-41bc','ManagedAPI-R03K-after-J-41bc','NativeSDK-R03K-after-J-41bc','Scratch-R03K-after-J-41bc','R03IRLocal-K-after-J-41bc','StorageCheck-R03IRLocal-K-after-J-41bc','Storage-R03IRLocal-K-after-J-41bc']]
roots += [B/'Preflight-R03L-after-K-52d9']
roots += [B/n for n in ['Preflight-R03M-after-L-73bc','ManagedAPI-R03M-after-L-73bc','NativeSDK-R03M-after-L-73bc','Scratch-R03M-after-L-73bc','R03IRLocal-M-after-L-73bc','StorageCheck-R03IRLocal-M-after-L-73bc','Storage-R03IRLocal-M-after-L-73bc']]
roots += [B/n for n in ['Preflight-R03N-after-M-6f28','ManagedAPI-R03N-after-M-6f28','NativeSDK-R03N-after-M-6f28','Scratch-R03N-after-M-6f28','R03IRLocal-N-after-M-6f28','StorageCheck-R03IRLocal-N-after-M-6f28','Storage-R03IRLocal-N-after-M-6f28']]
mapping=e.snapshot(roots);mapfile=P/'retained-fg-before.inventory.json'
if phase=='before':save(mapfile,mapping)
else:assert load(mapfile)==mapping
historical={}
for name in ['R03LocalBatch-20261007R-lq-storage','R03LocalBatch-20261006Q-lp-repair']:
 p=B/name;assert p.is_dir() and not p.is_symlink();historical[name]={f.name:{'sha256':sha(f),'size':f.stat().st_size} for f in sorted(p.iterdir()) if f.is_file() and f.name in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','seal-receipt.json','evidence.tar.gz']}
if phase=='after':assert historical==load(P/'FG_SDK_PRESERVATION_BEFORE.json')['retainedRQTopIdentities']
doc=hist/'IR_Remediation/IR_I_RESPONSE_RESERVE_6f02';spec=importlib.util.spec_from_file_location('jcollector',doc/'collect_i_debug_cache.py');jc=importlib.util.module_from_spec(spec);spec.loader.exec_module(jc);anchors=jc.authenticate_original(D)
installed_sdk_root=UNITY.parent.parent
for r in load(P/'J_SOURCE_BINDINGS.json')['currentSources']:assert sha(r['path'])==r['sha256']
for n in ['ManagedAPI-R03SNAP01-82bd','NativeSDK-R03SNAP01-82bd','Scratch-R03SNAP01-82bd','R03IRLocal-SNAP01-82bd','StorageCheck-R03IRLocal-SNAP01-82bd','Storage-R03IRLocal-SNAP01-82bd']:
 path=B/n;assert path.resolve()==path and not path.is_symlink()
 if phase=='before':assert not path.exists()
capacity=os.statvfs(B);available=capacity.f_bavail*capacity.f_frsize;assert phase=='after' or available>2*1024**3,'Insufficient bounded SDK/diagnostic capacity'
record={'state':'PassedPreservationOnly','phase':phase,'startUtc':start,'endUtc':now(),'installedSDKFilesVerifiedAgainstG':len(original['files']),'installedSDKBytes':original['bytes'],'currentManagedCompilerInputsPreserved':len(current_inputs),'managedInputsChangedFromHistoricalGBefore':sum(x['legitimateSourceDelta'] for x in current_inputs),'originalGOutputsVerified':5,'originalGScratchInventoryFilesVerified':len(sdk['files']),'retainedFGHIJKLMNCurrentSnapshotRoots':list(map(str,roots)),'snapshotEntries':len(mapping),'snapshotPath':str(mapfile),'snapshotSha256':sha(mapfile),'unindexedSnapshotClassification':'Current before/after preservation only, not retroactive build provenance','retainedRQTopIdentities':historical,'originalStrictCustody':'Blocked','E':'FAIL unchanged','F':'PrerequisiteBlocked unchanged','G':'Passed compile-only unchanged','historicalSourceBuildProcessProvenanceRestored':False,'installedSDKModified':False,'I':'FAIL unchanged','J':'Passed compile/read-only scope unchanged','N':'FAIL unchanged','M':'FAIL unchanged','K':'FAIL unchanged','L':'PrerequisiteBlocked unchanged; after-only custody is not before admission','originalIAnchors':anchors,'availableBytesObservation':available,'capacityAdmission':'Bounded compile/collection observation only; no runtime storage admission','sdkReferenceRoot':str(installed_sdk_root),'runtimeAcceptance':False}
save(P/('FG_SDK_PRESERVATION_'+phase.upper()+'.json'),record);print(json.dumps({k:v for k,v in record.items() if k!='retainedRQTopIdentities'}),flush=True)
