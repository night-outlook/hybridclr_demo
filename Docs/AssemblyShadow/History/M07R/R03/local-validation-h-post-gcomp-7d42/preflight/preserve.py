from h_common import *
import importlib.util
phase=sys.argv[1];assert phase in ['before','after'];start=now()
G=hist/'local-validation-20261011-ir-r03-02-g-compile-only';original=load(G/'preflight/INSTALLED_SDK_BEFORE.json');root=Path(original['root']);actual={str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()};assert actual=={r['path'] for r in original['files']}
for r in original['files']:
 f=root/r['path'];assert f.stat().st_size==r['size'] and sha(f)==r['sha256'],f
for r in load(G/'preflight/SOURCE_ENVIRONMENT.json')['tools']:assert sha(r['path'])==r['sha256'] and str(Path(r['path']).resolve())==r['resolved']
for r in load(G/'managed/build-api/inputs.json')['files']:assert sha(r['path'])==r['sha256'],r
for r in load(G/'managed/build-api/results.json')['packageAssemblies']:
 x=r['output'];assert sha(x['path'])==x['sha256']
for key in ['completeHelper','terminalPlayerApi']:
 x=load(G/'managed/build-api/results.json')[key];x=x.get('output',x);assert sha(x['path'])==x['sha256']
scratch=B/'Scratch-R03IRCompile-20261011G-canonical-temp';sdk=load(G/'native/native-sdk-inputs.json');assert {r['path'] for r in sdk['files']}=={str(f.relative_to(scratch)) for f in scratch.rglob('*') if f.is_file()}
for r in sdk['files']:assert sha(scratch/r['path'])==r['sha256']
verifier=hist/'IR_Remediation/IR_RUNTIME_01_2026-10-10/verify_retained_e.py';spec=importlib.util.spec_from_file_location('e_preservation',verifier);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
roots=[B/'Preflight-R03IRCompile-20261010F-runtime01']+[B/(n+'-R03IRCompile-20261011G-canonical-temp') for n in ['Preflight','ManagedAPI','NativeSDK','Scratch']]
mapping=e.snapshot(roots);mapfile=P/'retained-fg-before.inventory.json'
if phase=='before':save(mapfile,mapping)
else:assert load(mapfile)==mapping
historical={}
for name in ['R03LocalBatch-20261007R-lq-storage','R03LocalBatch-20261006Q-lp-repair']:
 p=B/name;assert p.is_dir() and not p.is_symlink();historical[name]={f.name:{'sha256':sha(f),'size':f.stat().st_size} for f in sorted(p.iterdir()) if f.is_file() and f.name in ['LOCAL_BATCH_RESULT.json','BATCH_EXECUTION.json','evidence-index.json','seal-receipt.json','evidence.tar.gz']}
if phase=='after':assert historical==load(P/'FG_SDK_PRESERVATION_BEFORE.json')['retainedRQTopIdentities']
record={'state':'PassedPreservationOnly','phase':phase,'startUtc':start,'endUtc':now(),'installedSDKFilesVerifiedAgainstG':len(original['files']),'installedSDKBytes':original['bytes'],'managedCompilerInputsVerifiedAgainstG':428,'originalGOutputsVerified':5,'originalGScratchInventoryFilesVerified':len(sdk['files']),'retainedFAndGCurrentSnapshotRoots':list(map(str,roots)),'snapshotEntries':len(mapping),'snapshotPath':str(mapfile),'snapshotSha256':sha(mapfile),'unindexedSnapshotClassification':'Current before/after preservation only, not retroactive build provenance','retainedRQTopIdentities':historical,'originalStrictCustody':'Blocked','E':'FAIL unchanged','F':'PrerequisiteBlocked unchanged','G':'Passed compile-only unchanged','historicalSourceBuildProcessProvenanceRestored':False,'installedSDKModified':False,'runtimeAcceptance':False}
save(P/('FG_SDK_PRESERVATION_'+phase.upper()+'.json'),record);print(json.dumps({k:v for k,v in record.items() if k!='retainedRQTopIdentities'}),flush=True)
