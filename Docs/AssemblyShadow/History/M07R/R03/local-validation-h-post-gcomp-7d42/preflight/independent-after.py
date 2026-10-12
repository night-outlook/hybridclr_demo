from h_common import *
import importlib.util
assert load(P/'HOST_RESULT.json')['state']=='Failed';clean_sources();no_unity()
C=hist/'local-validation-20261009-ir-r03-02-c-custody-blocked';ver=hist/'IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/verify_scoped_custody.py'
r=command('custody-after',[PY,'-B',ver,'--checkpoint',C,'--phase','after','--receipt',P/'scoped-custody-after.json']);assert r['exitCode']==0
# No before snapshot existed; authenticate E independently without inventing a join.
ver=hist/'IR_Remediation/IR_RUNTIME_01_2026-10-10/verify_retained_e.py';spec=importlib.util.spec_from_file_location('e_preservation',ver);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
start=now();count=e.authenticate_published(D);mapping=e.snapshot(e.ROOTS);dest=P/'retained-e-post-prerequisite.inventory.json';save(dest,mapping);save(P/'RETAINED_E_INDEPENDENT_AFTER.json',{'state':'PassedPreservationOnly','phase':'independent-post-prerequisite','startUtc':start,'endUtc':now(),'publishedFilesVerified':count,'currentSnapshotEntries':len(mapping),'mapPath':str(dest),'mapSha256':sha(dest),'classification':'Original indexed E bytes authenticated; additional snapshot current-only, not historical build provenance','beforeAudit':'NotRun after failed host prerequisite','beforeAfterJoin':'Unavailable; no before snapshot fabricated','historicalE':'FAIL unchanged','strictHistoricalCustody':'Blocked'})
# Published G bindings can be reverified; unindexed current F/G roster has no H-before baseline.
start=now();G=hist/'local-validation-20261011-ir-r03-02-g-compile-only';installed=load(G/'preflight/INSTALLED_SDK_BEFORE.json');root=Path(installed['root']);assert {str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()}=={r['path'] for r in installed['files']}
for r in installed['files']:assert sha(root/r['path'])==r['sha256'] and (root/r['path']).stat().st_size==r['size']
for r in load(G/'preflight/SOURCE_ENVIRONMENT.json')['tools']:assert sha(r['path'])==r['sha256'] and str(Path(r['path']).resolve())==r['resolved']
for r in load(G/'managed/build-api/inputs.json')['files']:assert sha(r['path'])==r['sha256']
for r in load(G/'managed/build-api/results.json')['packageAssemblies']:
 x=r['output'];assert sha(x['path'])==x['sha256']
for key in ['completeHelper','terminalPlayerApi']:
 x=load(G/'managed/build-api/results.json')[key];x=x.get('output',x);assert sha(x['path'])==x['sha256']
scratch=B/'Scratch-R03IRCompile-20261011G-canonical-temp';sdk=load(G/'native/native-sdk-inputs.json');assert {r['path'] for r in sdk['files']}=={str(f.relative_to(scratch)) for f in scratch.rglob('*') if f.is_file()}
for r in sdk['files']:assert sha(scratch/r['path'])==r['sha256']
roots=[B/'Preflight-R03IRCompile-20261010F-runtime01']+[B/(n+'-R03IRCompile-20261011G-canonical-temp') for n in ['Preflight','ManagedAPI','NativeSDK','Scratch']];current=e.snapshot(roots);dest=P/'retained-fg-post-prerequisite.inventory.json';save(dest,current)
save(P/'FG_SDK_INDEPENDENT_AFTER.json',{'state':'PassedPreservationOnly','phase':'independent-post-prerequisite','startUtc':start,'endUtc':now(),'installedSDKFilesVerifiedAgainstOriginalG':len(installed['files']),'SDKBytes':installed['bytes'],'GManagedInputBindings':428,'GOutputDLLHashesVerified':5,'originalGScratchInventoryFilesVerified':len(sdk['files']),'F_G_roots':list(map(str,roots)),'currentSnapshotEntries':len(current),'currentSnapshotPath':str(dest),'currentSnapshotSha256':sha(dest),'beforeAudit':'NotRun after failed host prerequisite','beforeAfterJoin':'Unavailable for unindexed current roster','historicalInputsClassification':'Byte identities backed by original G records; additional current snapshot is not retroactive provenance','historicalF':'PrerequisiteBlocked unchanged','historicalG':'Passed compile-only unchanged','installedSDKModified':False,'runtimeAcceptance':False})
print('Independent original C/E/G-byte and current F/G after audits completed; no before admission inferred',flush=True)
