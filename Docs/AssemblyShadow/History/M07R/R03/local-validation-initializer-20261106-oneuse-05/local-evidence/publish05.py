from pathlib import Path
import json,hashlib,subprocess,shutil,datetime,os
P=Path('/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-Initializer05-Resume-20261106-after-retirement');B=P.parent;W=B.parent/'assembly_shadow_h1r';D=W/'hybridclr_demo';O=B/'R03IR-Initializer-20261106-oneuse-05';H=O.with_name(O.name+'-native-host-raw');C=D/'Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-05';load=lambda p:json.loads(p.read_text());now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
a=load(P/'FINAL_INDEPENDENT_AUDIT.json');r=load(O/'LOCAL_BATCH_RESULT.json');run=load(P/'runner-COMMAND.json');ci=load(P/'CI_GATE.json');find=load(P/'RUNTIME_FINDINGS.json');raw=load(P/'RAW_MANIFEST.json');hr=load(P/'HOST_RAW_MANIFEST.json');pre=load(P/'PRESERVATION_BEFORE.json');post=load(P/'PRESERVATION_AFTER.json');cb=load(P/'SCOPED_C_BEFORE.json');ca=load(P/'SCOPED_C_AFTER.json');cap=load(P/'IMMEDIATE_CAPACITY.json');seal=load(O/'seal-receipt.json');br=load(O/'builds/candidate-release/build-receipt.json');pins=a['sourcePins'];head=pins['hybridclr_demo']
assert head=='db232418adf2fc35c54ed72a8933a174f8218126' and r['result']=='ReturnRequired' and a['cellCounts']=={'Passed':13,'Failed':2} and r['sealStatus']=='Passed' and run['runnerInvocations']==1 and ci['requiredJobsPassed']==6
assert all(x['result']=='ScopedHistoricalLossStable' and x['presentVerified']==339367 and x['historicalStillMissing']==77477 and x['originalStrictCustody']=='Blocked' for x in [cb,ca])
assert post['independentlyRepeatedBeforeAfterComparison']=='Passed' and len(post['history'])==20 and not C.exists() and not subprocess.check_output(['git','-C',str(D),'status','--porcelain'])
for inv in [raw,hr]:
 root=Path(inv['root'])
 for row in inv['files']:
  f=root/row['path'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==row['bytes'] and sha(f)==row['sha256']
 for row in inv['symlinks']:assert (root/row['path']).is_symlink() and os.readlink(root/row['path'])==row['target']
C.mkdir();copied=[];encoded=[];external=[]
def copy(src,rel,binary=False):
 dst=C/rel;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();data=src.read_bytes();why=[]
 if not binary:
  text=data.decode('utf-8')
  if '\r' in text or text.endswith('\n\n') or any(x.endswith((' ','\t')) for x in text.splitlines()):why.append('Original whitespace preserved losslessly')
  if src.suffix=='.json':
   try:json.loads(text)
   except ValueError:why.append('Original empty/malformed/intentional-negative JSON')
 if why:
  dst=dst.with_name(dst.name+'.utf8.json');save(dst,{'kind':'ExactUtf8TextEvidenceEncoding','sourcePath':str(src),'sourceSha256':sha(src),'bytes':len(data),'reason':why,'text':text});encoded.append({'source':str(src),'checkpoint':str(dst.relative_to(C)),'decodedBytes':len(data),'decodedSha256':sha(src)})
 else:shutil.copyfile(src,dst);copied.append({'source':str(src),'checkpoint':str(dst.relative_to(C)),'bytes':len(data),'sha256':sha(src)})
for f in sorted(P.iterdir()):
 if f.is_file() and f.suffix in ['.json','.log','.py','.txt','.diff']:copy(f,Path('local-evidence')/f.name)
allowed={'.json','.jsonl','.log','.txt','.xml','.rsp','.sha256','.py','.cpp','.h','.inl','.cs','.csproj','.md','.yml','.yaml','.traceevents','.plist','.asset','.unity','.asmdef','.meta'}
for inv,label in [(raw,'batch'),(hr,'host-raw')]:
 root=Path(inv['root'])
 for row in inv['files']:
  rel=Path(row['path']);f=root/rel;parts=rel.parts;skip=parts[0] in ['bin','obj','reference-worktrees']
  if label=='batch' and parts[0]=='projects' and len(parts)>2 and parts[2] in ['Library','Temp','Logs','HybridCLRData','obj']:
   skip=not(f.suffix=='.rsp' or f.name=='AssemblyShadowR03Probe.cpp' or (f.name.startswith('Player') and f.name.endswith('.dag.json')))
  keep=not skip and (f.suffix.lower() in allowed or f.name in ['stdout.bin','stderr.bin','stdout','stderr']) and row['bytes']<20*1024**2
  if keep:
   try:f.read_bytes().decode('utf-8')
   except UnicodeError:keep=False
  if keep:copy(f,Path(label)/rel)
  else:external.append({'source':str(f),'bytes':row['bytes'],'sha256':row['sha256'],'publication':'RetainedExternal_FullRawInventoryBound'})
folder=C/'sealed-product';folder.mkdir();parts=[];offset=0;totalhash=hashlib.sha256()
with (O/'evidence.tar.gz').open('rb') as stream:
 while True:
  data=stream.read(16*1024**2)
  if not data:break
  f=folder/f'evidence.tar.gz.part{len(parts):04}';f.write_bytes(data);totalhash.update(data);parts.append({'path':str(f.relative_to(C)),'offset':offset,'bytes':len(data),'sha256':sha(f)});offset+=len(data)
assert totalhash.hexdigest()==seal['archiveSha256'] and offset==(O/'evidence.tar.gz').stat().st_size
save(folder/'TRANSPORT.json',{'kind':'ExactOriginalInitializerProductSealTransport','sourcePath':str(O/'evidence.tar.gz'),'sourceSha256':seal['archiveSha256'],'bytes':offset,'parts':parts,'reconstruction':'Concatenate parts in listed order and verify original sourceSha256. Original Passed bounded seal and Failed semantics are unchanged.','semanticResult':r['result'],'productSealStatus':r['sealStatus'],'runtimeAcceptance':False})
copy(O/'host-custody/HOST_REGULAR_BYTES.tar.gz',Path('batch/host-custody/HOST_REGULAR_BYTES.tar.gz'),binary=True)
for mode in ['initializer-control','initializer-failure']:copy(O/'host/initializer-native-targets/native'/mode/'Methods.dll',Path('compiled-targets')/mode/'Methods.dll',binary=True)
for row in find['sourceBindings']:copy(W/row['repository']/row['path'],Path('source')/row['repository']/row['path'])
for rel in ['Docs/AssemblyShadow/README.md','Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md','.github/workflows/r03-ir-initializer-local-contracts.yml','.github/workflows/r03-ir-current-native-local-cycle-host.yml','.github/workflows/r03-initializer-capacity-readiness-host.yml']:
 f=D/rel
 if f.exists() and not (C/'source/hybridclr_demo'/rel).exists():copy(f,Path('source/hybridclr_demo')/rel)
copy(P/'RUNTIME_FINDINGS.json',Path('RUNTIME_FINDINGS.json'))
save(C/'COPY_BINDINGS.json',{'kind':'AdditiveInitializer05EvidenceTransport','copied':copied,'encodedTextEvidence':encoded,'retainedExternalFiles':external,'retainedHostSymlinkIdentities':hr['symlinks'],'rawInventories':['local-evidence/RAW_MANIFEST.json','local-evidence/HOST_RAW_MANIFEST.json'],'productArchiveTransport':'sealed-product/TRANSPORT.json','originalSealRewritten':False,'acceptancePromoted':False})
tests=sum(x['count'] for x in a['initializerUnitTests']);assert tests==46
result={'kind':'LocalInitializer05FactualResult','result':'FAIL','classification':'ReturnRequired_BothPlayersFailed_OriginalInternalImportExceptionCaptured','reportedAt':now(),'branch':'codex/assembly-shadow-r01b-h1','executionPins':pins,'executionPaths':{n:str(W/n) for n in pins},'executionSourceDemo':head,'publicationCommitIsDocumentationOnlyDescendant':True,'root':str(O),'hostRoot':str(H),'preflightRoot':str(P),'runner':run,'runnerInvocations':1,'retries':0,'cellCounts':a['cellCounts'],'cellStates':a['cellStates'],'nativeHostComponents':10,'initializerHostTests':tests,'exactSourceCIWorkflowsPassed':3,'exactSourceCIOsJobsPassed':6,'readOnlyMacAdmission':'Passed','capacityImmediate':cap,'freshUnityBuilds':1,'verifiedUnityBuilds':1,'buildErrors':br['errors'],'buildWarnings':br['warnings'],'actualFreshPlayers':2,'verifiedFreshPlayers':0,'strictPlayerVerifiers':'NotRun_CommandFailed','players':find['players'],'nativeRecoveryEvidence':'ParsedNativeVMFirstFailure_NotRuntimeAuthenticated','findings':find['findings'],'hostCustody':a['hostCustody'],'sealStatus':r['sealStatus'],'archiveSha256':seal['archiveSha256'],'indexSha256':seal['indexSha256'],'archiveMembers':seal['members'],'archiveTransportParts':len(parts),'rawFiles':len(raw['files']),'rawBytes':raw['totalBytes'],'hostRawFiles':len(hr['files']),'hostRawBytes':hr['totalBytes'],'hostSymlinks':len(hr['symlinks']),'preservationBefore':pre['result'],'preservationAfter':post['result'],'fullFrozenCBeforeAfter':{'result':'ScopedHistoricalLossStable','survivors':339367,'unchangedMissing':77477,'strictHistoricalCustody':'Blocked'},'ownerRetiredRoots':'Exact17Unavailable_Unchanged','priorPublishedCheckpointsPreserved':20,'originalSFilesPreserved':16978,'installedSdkInputsPreserved':2405,'sourceBindingsPreserved':79,'originalSAudits':'PassedOnlyTheirHistoricalArchivedIdentityProcessLexicalMachOScope','historicalReadiness05':'Blocked_NotRun_Unchanged','historical01_02_03_04':'Unchanged','runtimeAcceptance':False,'R03Accepted':False,'H2Passed':False,'qualificationApproved':False,'ReadyForHumanReviewGate':False,'pureInterpreterExpansionEnabled':False,'nextState':'Primary Implementation','publicationReceipt':str(B/'initializer-05-PUBLICATION_RECEIPT.json')}
save(C/'LOCAL_RESULT.json',result)
(C/'README.md').write_text('''# Initializer oneuse-05 — FAIL / ReturnRequired

One authorized fresh batch: **13 Passed / 2 Failed**. One official Unity2022.3.62f2 arm64 IL2CPP build Passed (0 errors /1 warning). Both real Players exit2 with empty strict V1 raw; semantic verifiers remain NotRun_CommandFailed. Both bounded, source/PID/fixture-bound VM recovery files identify the original module-initializer exception: `Unable to load DLL '__Internal'`. Callback entry is absent. Diagnostics and Passed seals do not replace failed Player semantics.

- [Factual result](LOCAL_RESULT.json)
- [Actionable native import finding](RUNTIME_FINDINGS.json)
- [Original result](batch/LOCAL_BATCH_RESULT.json) and [ledger](batch/BATCH_EXECUTION.json)
- [Independent audit](local-evidence/FINAL_INDEPENDENT_AUDIT.json)
- [After preservation](local-evidence/PRESERVATION_AFTER.json) and [full C audit](local-evidence/SCOPED_C_AFTER.json)
- [Exact original archive transport](sealed-product/TRANSPORT.json)
- [Copy bindings](COPY_BINDINGS.json)

Exactly one runner dispatch, one build and two Players. No runtime/test/compiler changes, retries or cleanup during this execution. The documentation-only db232 execution source was explicitly readmitted by the owner and all three mandatory exact-SHA workflows passed both OSes. The exact17 owner-retired roots remain Unavailable; all other protected inputs passed before/after checks. Frozen-C scoped survivors339367/missing77477 are unchanged; strict historical custody remains Blocked. Earlier initializer and historical PASS/FAIL/Blocked/NotRun outcomes are preserved.

Selected exact raw text, command/compiler streams, traces/recovery, build/Player/host receipts and source bindings are copied. Empty/malformed JSON and whitespace-sensitive logs use reversible .utf8.json encoding. Large/cache/app files remain in the new live roots under complete hash inventories. The original bounded product archive is transported in ordered hash-bound parts; no reseal or semantic rewrite. All3198 raw host regular files and four literal links are authenticated by the host archive and postflight. Seal PASS is scoped evidence custody only.

Closing pushed publication HEAD and all four verified remotes are recorded externally at /Users/ah/GitHub/hybridclr/r03-local-validation/initializer-05-PUBLICATION_RECEIPT.json. That closing Docs-only commit is distinct from db232 execution source. All acceptance flags remain false. Return to Primary Implementation; no runtime acceptance, independent High closure or Human Review Gate approval.
''')
link='../History/M07R/R03/'+C.name
pinrows='\n'.join('| '+str(W/n)+' | `'+h+'` |' for n,h in pins.items())
playerrows='\n'.join('| '+v['case']+' | '+str(v['pid'])+' | 2 | 0 | '+str(v['traceEvents'])+' | `'+v['recoverySha256']+'` |' for v in find['players'])
local=f'''## Initializer oneuse-05 — FAIL / ReturnRequired; original VM exception identified

Exactly **one** fresh batch ran: **13/15 cells Passed, both Player cells Failed**. One real Unity **2022.3.62f2 macOS arm64 ON/diagnostics2/Release IL2CPP** build Passed (**0 errors /1 warning**). Two real Players exited **2**, both strict `raw.json` files are **0 bytes**, and semantic verifiers remain **NotRun_CommandFailed**. New native recovery diagnostics identify **`Methods: The type initializer for '<Module>' threw an exception. ---> Unable to load DLL '__Internal'`**. Host custody and bounded product seal Passed; this does not promote failed semantics. [Factual result]({link}/LOCAL_RESULT.json), [producer result]({link}/batch/LOCAL_BATCH_RESULT.json), [source/PID-bound finding]({link}/RUNTIME_FINDINGS.json).

| Execution repository / branch codex/assembly-shadow-r01b-h1 | Exact source commit |
| --- | --- |
{pinrows}

The owner explicitly approved **documentation-only readmission and conditional run**. Only README and WEB_TO_LOCAL changed in source commit **db232418adf2fc35c54ed72a8933a174f8218126**; executable inputs remain identical to Primary85fb. All three mandatory workflows Passed both OSes at db232: initializer **42225120124** (jobs127916542418/127916542638), capacity **42225120279** (127916543456/127916543681), shared host/custody **42225120809** (127916544799/127916544902). [Approval]({link}/local-evidence/OWNER_READMISSION_APPROVAL.json), [CI]({link}/local-evidence/CI_GATE.json), [source equivalence]({link}/local-evidence/SOURCE_EQUIVALENCE.json). Existing managed API/writer compilation is reused source-audited evidence with32 unchanged input blobs, uses stubs/mocks, and is not new official Unity/runtime acceptance.

Fresh read-only Mac/source/fixture/CLI admission Passed. Existing .NET8.0.318/runtime8.0.21 was selected only in child PATH; installed official Unity2022.3.62f2 SDK and Apple clang remained intact. Fresh same-volume pair: **{json.loads(load(P/'EXEC_CAPACITY_1.json')['stdout'])['capacity']['freeGiB']:.9f} / {load(P/'EXEC_CAPACITY_2.json')['sample']['capacity']['freeGiB']:.9f} GiB**, **111.118523 seconds** apart; independent immediate sample **{cap['freeGiB']:.9f} GiB**, all>=25 and advisory40. O/host roots were unused before dispatch. Runner PID **{run['pid']}**, **{run['startUtc']} → {run['endUtc']}**, exit1. Command and stream hashes preserved in [runner receipt]({link}/local-evidence/runner-COMMAND.json). No TMPDIR override or code workaround.

All **ten native host components** and **46 initializer tests** Passed, including5 native recovery tests. Fixed control/failure target SHAs/MVIDs matched. Original-S archives, process joins, generated lexical identity and archived Mach-O audits Passed only their historical scopes, without rerunning historical59 Players or claiming source/object/link closure. The actual fresh build receipt SHA **{a['build']['sha256']}**, executable SHA **{a['build']['executableSha256']}**, overlay SHA **{a['build']['overlaySha256']}** were independently verified with source manifest, installed overlay and app inventory. [Build]({link}/batch/builds/candidate-release/build-receipt.json), [audit]({link}/local-evidence/FINAL_INDEPENDENT_AUDIT.json).

| Fresh Player | PID | Exit | Strict raw bytes | Native events | VM recovery SHA-256 |
| --- | --- | --- | --- | --- | --- |
{playerrows}

Both recovery files independently pass exact envelope/schema/run/case/stimulus/PID/fixture bindings. Native getter returns0; core reports **state9/FailedAfterCommit, terminalFailureCode19, RestartRequired**, with actual `dlopen(__Internal)` attempts. This is **ParsedNativeVMFirstFailure_NotRuntimeAuthenticated**, not complete nativeV2 or first-recovery acceptance. Both traces have no callback-entry299/return300, ReadPrepared=-1/state0 and Seal=-2/reason1. Control does not satisfy0/6; failure19/9 originates from an import exception and cannot prove the intended post-preparation sentinel. Five native observer/writer symbols exist in GameAssembly; exports do not prove runtime import resolution. [Recovery/trace/command/source joins]({link}/RUNTIME_FINDINGS.json).

**IR-LOCAL-R03-INITIALIZER-05-INTERNAL-IMPORT-01:** fixture ModuleRef is `__Internal`; interpreted PInvoke routes through PlatformInvoke::Resolve, whose current special current-process dynamic-load branch is only `__InternalDynamic`. Actual failure is named-library lookup for `__Internal`. Primary must reconcile this producer/VM import contract and verify a new real build/two Players while retaining strict control, fixture, field/mask/cardinality and terminal expectations. No alternative import or fix was tested here. Further failures may remain after repair.

Current host custody authenticates **3198 files /4 literal links /173485951 bytes**, with3199 host archive members. Product seal Passed **{seal['members']} members**, original archive **{offset} bytes**, SHA **{seal['archiveSha256']}**, index **{seal['indexSha256']}**, transported unchanged in **{len(parts)}** parts. Complete new live inventory: **14588 regular files /0 links /3376929994 bytes**; separate host inventory retained. [Host custody]({link}/batch/host-custody/HOST_CUSTODY_RESULT.json), [archive transport]({link}/sealed-product/TRANSPORT.json), [copy bindings]({link}/COPY_BINDINGS.json).

Independent before/after preservation Passed for **16978 original-S files,20 prior checkpoints,2405 SDK inputs,79 source bindings** and1135 remaining outside entries (the latter is top-level file/metadata scope; not a new full-byte audit of every old raw interior). Full original-C audit scanned **416844 identities** before/after: **339367 survivors /77477 unchanged missing**; original strict custody remains **Blocked**. Exactly17 owner-retired roots remain **Unavailable**, never described as restored or live-preserved. Both retained compressed transitions and recovery backup remain verified. [After]({link}/local-evidence/PRESERVATION_AFTER.json), [C-after]({link}/local-evidence/SCOPED_C_AFTER.json). Historical05 capacity-readiness Blocked/NotRun and01/02/03/04 outcomes remain unchanged.

Return to **Primary Implementation** after factual publication. No retry, extra Player, implementation/test/compiler/SDK change or new cleanup during runtime. Current-source acceptance, independent IR-R03-01/02, captured-generic, complete nativeV2, canonicalTypeKeys, pointer lifetime/VM epoch, GC/RSS and managed Shutdown remain unproved. R03Accepted/H2Passed/qualificationApproved/ReadyForHumanReviewGate/runtimeAcceptance/PureInterpreter expansion remain false. Latest pushed Docs-only publication is recorded at `/Users/ah/GitHub/hybridclr/r03-local-validation/initializer-05-PUBLICATION_RECEIPT.json`; it is a descendant of, and not substituted for, execution source db232.
'''
ret=f'''## Initializer oneuse-05 return — original `__Internal` module import failure

**IR-LOCAL-R03-INITIALIZER-05-INTERNAL-IMPORT-01** requires Primary Implementation. One immutable db232 source batch:13 cells Passed,2 Player cells Failed; fresh Unity build Passed0 errors/1 warning; both Players exit2. Host custody and product seal Passed within their scope. [Actionable finding]({link}/RUNTIME_FINDINGS.json), [result]({link}/LOCAL_RESULT.json), [independent audit]({link}/local-evidence/FINAL_INDEPENDENT_AUDIT.json).

**Reproduction already performed exactly once:** source tuple in LOCAL_RESULT; runner `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py` with workspace `{W}`, originalS `{B}/OriginalS-20261026-fc55-oneuse`, officialUnity2022.3.62f2, demo=db232418adf2fc35c54ed72a8933a174f8218126 and output `{O}`. Actual Player commands **0017 /0018**, PID **23120 /23133**, exit2, were launched from the single retained ON/Release build. Their exact argv/nonces/fixture/request/build/executable hashes are preserved. **Do not replay05.** [Command0017]({link}/batch/commands/0017/command.json), [0018]({link}/batch/commands/0018/command.json).

**Actual original exception:** both `raw.json.vm-recovery.json` files report module initializer failure19/state9 and `Unable to load DLL '__Internal'`, including `dlopen(__Internal, 0x0005)` named-library lookup failures. Recovery envelopes and25/27-event bounded traces match source/request/PID/fixture; no callback entry299/return300 exists. Strict raw is empty and semantic verifiers are NotRun_CommandFailed. Native ReadPrepared=-1/state0, Seal=-2/reason1; no intended prepared-field/mask/callback/sentinel proof. The complete exception bytes and raw log files are retained under the two [Player directories]({link}/batch/players/IR-R03-02-initializer-control/verification.json) and [failure verification]({link}/batch/players/IR-R03-02-initializer-failure/verification.json).

**Most likely root cause and affected boundary:** `InitializerNativeTargetFixtures.cs:80` emits ModuleRef `__Internal`. `hybridclr/transform/TransformContext.cpp` routes interpreted PInvoke into `PlatformInvoke::Resolve`. `il2cpp_plus/libil2cpp/vm/PlatformInvoke.cpp:50–53` special-cases only `__InternalDynamic` to open the current-process handle; `__Internal` takes named-library loading. This matches the actual recovery exception. Static nm confirms OnPrepared and all four other native writer symbols are exported in GameAssembly, so exports alone did not establish interpreted lookup. Healthy control0/6 and intended post-preparation failure19/9 both remain unsatisfied. This narrows the03 unknown pre-callback failure to a concrete import-contract issue; historical03 bytes/result remain unchanged and its live root is owner-retired.

**Recommended implementation direction:** explicitly reconcile the interpreted callback import with the supported current-process symbol-resolution contract. Primary must choose and review fixture import authority versus VM resolver behavior; no Local module-name substitution was attempted. If fixture/native inputs change, publish fresh authenticated pins/hashes/controls rather than rebinding old evidence. Preserve control0/6, intended authenticated failure19/9, callback1, physical field3/mask15 and terminal canary constraints. The source-supported `__InternalDynamic` branch is not a proven runtime fix. Validate a fresh source-matched build/two fresh Players, full strict V1 plus source/PID/fixture/native recovery joins, real callback proof, bounded diagnostics, host custody and seal. Subsequent preparation failures may remain; nativeV2, complete recovery authentication and full R03 remain outside this scope.

No source correction, retry or extra stimulus occurred. Original-C before/after scoped339367/77477 stability, remaining history/SDK/source preservation and current seal Passed. Historical strict custody remainsBlocked;17 owner-retired roots remainUnavailable; previous FAIL/Blocked/NotRun/PASS outcomes are unchanged. Full provenance, CI, capacity, preservation and raw-copy limitations are in LOCAL_VALIDATION and the checkpoint. All acceptance flags remain false. Return to Primary and stop.
'''
owned=[]
for name,section in [('LOCAL_VALIDATION.md',local),('RETURN_TO_WEB.md',ret)]:
 f=D/'Docs/AssemblyShadow/Handoff'/name;old=f.read_text();assert old==subprocess.check_output(['git','-C',str(D),'show',head+':'+str(f.relative_to(D))],text=True);title,sep,body=old.partition('\n\n');assert sep;f.write_text(title+'\n\n'+section+'\n---\n\n'+body);owned.append(str(f.relative_to(D)))
m=C/'MANIFEST.sha256';m.write_text(''.join(sha(f)+'  '+str(f.relative_to(C))+'\n' for f in sorted(C.rglob('*')) if f.is_file() and f!=m))
save(P/'PUBLICATION_PLAN.json',{'result':'FAIL','classification':result['classification'],'executionPins':pins,'checkpoint':str(C),'checkpointManifestSha256':sha(m),'ownedReports':owned,'runnerInvocations':1,'runtimeRootConstructed':True,'archiveParts':len(parts),'checkpointFiles':sum(f.is_file() for f in C.rglob('*'))})
print('Prepared checkpoint',len(parts),'parts',offset,'archive bytes;',sum(f.is_file() for f in C.rglob('*')),'files')
