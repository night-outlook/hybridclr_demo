from pathlib import Path
import json,hashlib,datetime,subprocess,shutil,os
R=Path('/Users/ah/GitHub/hybridclr_cleanup_receipts/user-retire-runtime17-20261106');B=Path('/Users/ah/GitHub/hybridclr/r03-local-validation');W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';C=D/'Docs/AssemblyShadow/History/M07R/R03/storage-retirement-20261106-runtime17';assert not C.exists();load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
scope=load(R/'APPROVED_SCOPE.json');result=load(R/'RESULT.json');protected=load(R/'PROTECTED_AFTER.json');iv=load(R/'INVENTORY_VERIFICATION.json');expected=load(R/'SOURCE_REMOTE_BEFORE.json')['expected'];H=expected['hybridclr_demo']
assert result['result']=='CompletedExact17RootDeletion' and len(result['deletedRoots'])==17 and result['fortyDuplicateCopiesDeleted'] and not result['recoveryArchiveCreated'];assert protected['independentBeforeAfterComparison']=='Passed' and iv['result']=='PassedMetadataInventoryIntegrity';assert all(not Path(p).exists() and not Path(p).is_symlink() for p in scope['exactRoots'])
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==H and not subprocess.check_output(['git','-C',str(D),'status','--short','--untracked-files=all'],text=True)
C.mkdir();(C/'evidence').mkdir();copies=[]
for source in sorted(R.iterdir()):
 if not source.is_file() or source.name=='TARGET_INVENTORY.jsonl.gz' or source.name.startswith('PUBLICATION_'):continue
 target=C/'evidence'/source.name;shutil.copyfile(source,target);assert sha(source)==sha(target);copies.append({'source':str(source),'checkpoint':str(target.relative_to(C)),'bytes':source.stat().st_size,'sha256':sha(source)})
inventory=R/'TARGET_INVENTORY.jsonl.gz';parts=[]
with inventory.open('rb') as f:
 i=0
 while True:
  block=f.read(16*1024*1024)
  if not block:break
  name=f'TARGET_INVENTORY.jsonl.gz.part{i:04d}';p=C/'inventory'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(block);parts.append({'path':str(p.relative_to(C)),'bytes':len(block),'sha256':sha(p)});i+=1
h=hashlib.sha256();n=0
for part in parts:
 data=(C/part['path']).read_bytes();h.update(data);n+=len(data)
assert n==inventory.stat().st_size and h.hexdigest()==sha(inventory)
def write(name,x):(C/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
write('COPY_BINDINGS.json',{'copiedMetadata':copies,'inventoryParts':parts,'inventoryFullBytes':n,'inventorySha256':sha(inventory),'inventoryKind':'Metadata paths, hashes, types and ownership only; no deleted-file payload bytes','recoveryArchiveCreated':False})
fs=os.statvfs(B);currentFree=fs.f_bavail*fs.f_frsize
write('CUSTODY_DISPOSITION.json',{'id':'R03-STORAGE-RETIRE17-20261106','authority':'Explicit user permanent deletion, including unique evidence and all40 specified duplicate paths','scopeSha256':sha(R/'APPROVED_SCOPE.json'),'retiredRoots':[{'path':p,'state':'PermanentlyDeleted_UserAuthorized','currentLiveVerification':'Unavailable_RetiredByOwner'} for p in scope['exactRoots']],'fortyDuplicatePaths':[{'path':r['path'],'sha256BeforeRetirement':r['sha256'],'state':'PermanentlyDeleted_UserAuthorized'} for r in scope['duplicateFiles']],'currentPhysicalRawCustody':'UnavailableForSelected17Roots','historicalVerdicts':'Retained unchanged as historical facts; not reclassified as current physical coverage or fresh acceptance.','publishedGitCheckpoints':'Preserved existing bytes, outside deletion scope. No Git history was purged.','newRecoveryCopy':'None, explicitly declined','primaryAction':'Adopt this owner-approved disposition in a new source-bound handoff before any further Local admission. Existing gates expecting these live roots will fail; do not silently weaken assertions, restore old roots, or reuse consumed batches.','R03Accepted':False,'H2Passed':False,'ReadyForHumanReviewGate':False,'runtimeAcceptance':False,'qualificationApproved':False,'fullLegacyRegressionAcceptance':False,'PureInterpreterExpansion':False})
write('LOCAL_RESULT.json',{'kind':'StorageRetirementNotRuntimeValidation','result':'CompletedOwnerAuthorizedRetirement','timeUtc':now(),'sourcePinsAtAction':expected,'sourcePaths':{k:str(W/k) for k in expected},'branch':'codex/assembly-shadow-r01b-h1','deletedRoots':result['deletedRoots'],'deletedRootCount':17,'regularFilesDeleted':result['deletedRegularFiles'],'symlinksDeleted':result['deletedSymlinks'],'fortySpecifiedDuplicatesDeleted':True,'newRecoveryPayloadCopies':0,'logicalBytesRetired':result['logicalFileBytesRetired'],'availableBytesIncreaseDuringDeletion':result['actualAvailableBytesIncrease'],'freeBytesBeforeDeletion':result['freeBytesBefore'],'freeBytesAfterDeletion':result['freeBytesAfter'],'freeBytesAtPublicationPreparation':currentFree,'scopeReview':'Passed independent boundary-only review','preservation':{'outsideTopLevelEntriesVerified':len(protected['topLevelOutsideEntries']),'originalSFilesVerified':protected['originalSFilesVerified'],'publishedCheckpointCount':len(protected['publishedCheckpointsVerified']),'installedSdkFilesVerified':protected['installedSdkFilesVerified'],'owningReposCleanAndHeadsUnchanged':True,'retainedInitializer05RecoveryArchivePreserved':True,'priorGzipTransitionPreserved':True,'scopeLimitation':protected['outsideDirectoryCheck']},'currentRawEvidenceState':'PermanentlyDeleted_UserAuthorized; Unavailable for current verification','oldRuntimeResults':'Historical Passed/Failed/Blocked/NotRun classifications retained; no semantic reclassification','UnityLaunches':0,'newRuntimeBatchInvocations':0,'initializer05Runtime':'NotRun; prior readiness report remains historical Blocked','allAcceptanceFlagsRemainFalse':True,'exitState':'Local Validation -> Primary Implementation','publicationHeadPolicy':'The final pushed Docs-only child SHA and four remote heads are recorded in external PUBLICATION_RECEIPT after pushing; sourceSHA is not misreported as that future commit.'})
(C/'README.md').write_text(f'''# Owner-authorized permanent retirement of17 runtime evidence roots

The user explicitly selected **永久删除17个完整批次，包括唯一证据** and **全部删除，不保留这40个副本**. This supersedes the earlier keep-live requirement only for the17 exact roots in [scope](evidence/APPROVED_SCOPE.json). All40 specified duplicates are contained in these roots; they are not counted as extra deletion targets. No new payload backup or retained representative copy was created.

Exactly **17 roots /{result['deletedRegularFiles']} regular files /{result['deletedSymlinks']} symlinks** were removed. All17 roots and all40 specified paths are independently confirmed absent. The actor did not follow internal symlinks. Independent scope review confirmed zero registered-worktree/source/OriginalS overlap. [Actual result](evidence/RESULT.json), [absence check](evidence/ABSENCE_VERIFICATION.json), [scope review](evidence/SCOPE_REVIEW.json).

Measured available bytes increased **{result['actualAvailableBytesIncrease']} ({result['actualAvailableBytesIncrease']/1024**3:.6f}GiB)** during deletion, from {result['freeBytesBefore']} to {result['freeBytesAfter']} bytes. Directory/logical totals are not unique APFS physical block ownership; no larger release was inferred from du. No Unity, Player, compiler or runtime validation ran.

[Before](evidence/PROTECTED_BEFORE.json)/[after](evidence/PROTECTED_AFTER.json) preservation verifies **1135 outside top-level entries**, full hashes for **16978 OriginalS files,19 published checkpoints and2405 installed SDK inputs**, four clean unchanged owning sources, the retained initializer05 recovery archive and the previous JSON gzip transition. Unselected raw directory interiors were not fully rehashed; their top-level identity/metadata and operation boundary were checked. Existing Git history/published evidence was outside deletion scope and remains intact.

[Inventory bindings](COPY_BINDINGS.json) reconstruct the gzip JSONL inventory from ordered16MiB parts. It contains metadata and pre-deletion hashes, **not payloads or a recovery archive**. The unique live files selected by the owner are now unavailable; do not claim current live custody or reconstruct acceptance from metadata hashes.

[Custody disposition](CUSTODY_DISPOSITION.json) requires Primary to explicitly adopt the new unavailable/retired raw state before another Local dispatch. Original Passed/Failed/Blocked/NotRun verdicts remain historical facts; none is upgraded. Old gates expecting the deleted live roots will fail. All R03/H2/qualification/Human Review Gate flags remain false. Storage retirement is complete; this is not a new product validation PASS. [Factual Local result](LOCAL_RESULT.json).
''')
cp='../History/M07R/R03/'+C.name
intro=f'''## User-authorized permanent retirement —17 runtime roots /40 duplicate paths

**Deletion completed; no new runtime validation.** The user explicitly approved `永久删除17个完整批次，包括唯一证据` and `全部删除，不保留这40个副本`. These approvals supersede earlier live-retention requirements only for the17 exact roots under `/Users/ah/GitHub/hybridclr/r03-local-validation` in the [scope]({cp}/evidence/APPROVED_SCOPE.json). All40 duplicated paths lie inside these roots. Exactly **{result['deletedRegularFiles']} regular files and{result['deletedSymlinks']} symlinks** were removed; no new recovery payload archive or representative copy was retained. [Result]({cp}/LOCAL_RESULT.json), [permanent custody disposition]({cp}/CUSTODY_DISPOSITION.json), [absence verification]({cp}/evidence/ABSENCE_VERIFICATION.json).

The selected live raw data now has custody state **PermanentlyDeleted_UserAuthorized / UnavailableForCurrentVerification**. Existing published Git checkpoints and all prior Passed/Failed/Blocked/NotRun verdicts remain unchanged as historical records; they do not establish current physical custody of the deleted paths. The 575245-file metadata inventory retains names/types/sizes/pre-deletion hashes only, not recoverable file payloads. [Inventory bindings]({cp}/COPY_BINDINGS.json).

Independent boundary review checked17 real disjoint direct-child roots,40 regular-file duplicate paths,81 registered worktrees and mount boundaries: no source/worktree/OriginalS overlap. Before/after protection verified **1135 outside top-level entries**, full hashes of **16978 OriginalS files,19 published checkpoints,2405 installed SDK inputs**, clean unchanged owning source HEADs, retained recovery archive and prior gzip transition. Unselected raw directory interiors were not fully byte-audited; the precise scope is recorded. [Review]({cp}/evidence/SCOPE_REVIEW.json), [before]({cp}/evidence/PROTECTED_BEFORE.json), [after]({cp}/evidence/PROTECTED_AFTER.json).

Actual statvfs available-byte increase during deletion was **{result['actualAvailableBytesIncrease']} bytes /{result['actualAvailableBytesIncrease']/1024**3:.6f}GiB**, from **{result['freeBytesBefore']}** to **{result['freeBytesAfter']} bytes /{result['freeBytesAfter']/1024**3:.6f}GiB**, device{result['device']}. This measured volume delta is distinct from72.84GiB directory estimates and71.53GiB logical payload. Capacity alone does not authorize a new batch. Unity0, Players0, compiler0 and runtime batch0; initializer05 remains NotRun. Earlier readiness Blocked is historical, not rewritten to Passed.

Action source tuple, all branch `codex/assembly-shadow-r01b-h1`: demo `{H}`; hybridclr `{expected['hybridclr']}`; package `{expected['hybridclr_unity']}`; IL2CPP `{expected['il2cpp_plus']}`. Final Docs-only publication HEAD and four verified remote tips are recorded at `{R}/PUBLICATION_RECEIPT.json` after pushing. **Primary must explicitly reconcile the owner-approved raw retirement with future custody admissions before further Local execution**; do not weaken assertions, restore deleted consumed roots, infer full-stage acceptance or start another milestone. All acceptance flags remain false. Return to Primary Implementation.

---

'''
returned=f'''## R03-STORAGE-RETIRE17-20261106 — owner-approved raw evidence no longer available

The user explicitly authorized permanent deletion of17 complete runtime-related roots, including unique evidence, and all40 specified duplicate paths without preserving a representative copy. The action is complete: **17 roots /{result['deletedRegularFiles']} regular files /{result['deletedSymlinks']} symlinks** removed; all40 paths absent, no new payload recovery archive. [Scope]({cp}/evidence/APPROVED_SCOPE.json), [actual result]({cp}/evidence/RESULT.json), [current custody]({cp}/CUSTODY_DISPOSITION.json).

**Impact and reproduction:** read the exact retired-root list, confirm nonexistence, and compare it with prior raw manifests referenced by current admissions. Direct old-path rehash gates will now fail by design. Metadata hashes are retained for provenance only; selected payloads are unavailable for current verification. This is an explicit owner retention decision, not a newly reproduced VM defect, successful runtime repair, or permission to rewrite historical results. All earlier verdicts and existing Git-published checkpoints remain unchanged. No Unity/Player/compile or new runtime batch occurred.

**Required Primary action:** adopt this precise retirement disposition in a new source-bound handoff/custody plan before dispatch. Preserve all remaining data and distinguish unavailable live artifacts from historical results. Do not silently bypass missing evidence, regenerate consumed roots, reuse old apps or promote prior partial observations to acceptance. Independent High findings and R03 obligations remain open; all acceptance flags are false.

Boundary review and independent before/after protection Passed within declared scope: four owning sources/OriginalS,19 published checkpoints,16978 S files,2405 installed SDK files and1135 outside top-level entries preserved. Unselected raw interiors were not fully rehashed. Actual volume free-space increase **{result['actualAvailableBytesIncrease']/1024**3:.6f}GiB**; final verification is in the publication receipt `{R}/PUBLICATION_RECEIPT.json`. [Local report]({cp}/LOCAL_RESULT.json), [after protection]({cp}/evidence/PROTECTED_AFTER.json). Return to Primary Implementation.

---

'''
for name,section in [('LOCAL_VALIDATION.md',intro),('RETURN_TO_WEB.md',returned)]:
 p=D/'Docs/AssemblyShadow/Handoff'/name;old=p.read_text();title,sep,body=old.partition('\n\n');assert sep;p.write_text(title+'\n\n'+section+body)
files=[]
for p in sorted(C.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(sha(p)+'  '+str(p.relative_to(C)))
(C/'MANIFEST.sha256').write_text('\n'.join(files)+'\n')
plan={'timeUtc':now(),'sourcePins':expected,'checkpoint':str(C),'ownedReports':['Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md','Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md'],'manifestSha256':sha(C/'MANIFEST.sha256'),'checkpointFiles':len(files)+1,'storageRetirementComplete':True,'newRuntimeResult':False};(R/'PUBLICATION_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('prepared metadata-only retirement checkpoint',len(files)+1,'files')
