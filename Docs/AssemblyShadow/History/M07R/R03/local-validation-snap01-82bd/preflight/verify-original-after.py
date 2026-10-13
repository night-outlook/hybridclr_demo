from h_common import *
start=now();g=load(P/'G_EQUIVALENCE.json');cps=[]
for c in g['originalCheckpoints']:
 root=Path(c['checkpoint']);assert sha(root/'MANIFEST.sha256')==c['manifestSha256'];rows=[l.split('  ',1) for l in (root/'MANIFEST.sha256').read_text().splitlines()];assert {str(f.relative_to(root)) for f in root.rglob('*') if f.is_file()}=={r[1] for r in rows}|{'MANIFEST.sha256'}
 for h,n in rows:assert sha(root/n)==h
 cps.append({'path':str(root),'manifestSha256':c['manifestSha256'],'filesVerified':len(rows),'originalPublication':c['publication']})
# Original K/I live records remain tied to their immutable published audit.
roots=[]
for name,live in [('local-validation-n-after-m-6f28','R03IRLocal-N-after-M-6f28'),('local-validation-m-after-l-73bc','R03IRLocal-M-after-L-73bc'),('local-validation-k-after-j-41bc','R03IRLocal-K-after-J-41bc'),('local-validation-i-post-h-custody-7f36','R03IRLocal-I-post-H-custody-7f36')]:
 cp=hist/name;root=B/live;a=load(cp/'preflight/FINAL_EVIDENCE_AUDIT.json')
 for x in a['topArtifacts']:assert sha(x['path'])==x['sha256']
 index=load(root/'evidence-index.json')
 for x in index['files']:assert (root/x['path']).stat().st_size==x['size'] and sha(root/x['path'])==x['sha256']
 for build in a['builds']:
  native=Path(build['installedNativeRoot'])
  for x in build['installedFileInventory']:assert (native/x['path']).stat().st_size==x['size'] and sha(native/x['path'])==x['sha256']
 roots.append({'root':str(root),'indexFiles':len(index['files']),'nativeInventoryRowsVerified':sum(len(x['installedFileInventory']) for x in a['builds']),'result':'Original failure preserved'})
S=B/'R03LocalBatch-20261007S-lr-recovery';index=load(S/'evidence-index.json')
for x in index['files']:assert (S/x['path']).stat().st_size==x['size'] and sha(S/x['path'])==x['sha256']
for n,h in load(P/'ORIGINAL_INPUT_PREFLIGHT.json')['sTopArtifactHashes'].items():assert sha(S/n)==h
save(P/'ORIGINAL_BINDINGS_AFTER.json',{'state':'PassedOriginalIdentityComparison','startUtc':start,'endUtc':now(),'checkpointManifests':cps,'retainedKI':roots,'sealedSIndexFiles':len(index['files']),'sealedSTopArtifacts':'Original hashes unchanged','runtimeAdmission':False,'historicalStrictCustody':'Blocked','afterOnlyNotBeforeAdmission':True})
print('Original checkpoint, K/I installed-native and S evidence bytes unchanged',flush=True)
