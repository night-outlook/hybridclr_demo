# Local Validation report

## Current run — 2026-09-28, batch H sealed return after functional and regression failures

**Local Validation → Primary Implementation: ReturnRequired; independent R02 stage review NotEligible/NotRun.** One fresh 34-cell R02LocalBatch-v1 ran once at /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/R02LocalBatch-20260928H/ with TMPDIR=/private/tmp and PYTHONDONTWRITEBYTECODE=1. Entry and final source authority passed. Candidate HEAD bef8249922ce79623f5156cb20c5afc881d4d4c4 and matched control HEAD 2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e matched their pushed remote tips; all eight owning checkouts were clean at entry, and the two demos were clean after the run. HybridCLR remained 1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad, package b936a495ade1691ebb6f3bab8fdff3ef34f6f192, candidate IL2CPP 3981da12f2cd3ee878a04dda6f573d0ad3faeda5, and control IL2CPP 6be7f38bec2fa4677d24efc1a4a1294240789933. Common source anchor af9ba49127a7e852fed504a55c733c5f6ec5e54e has nine candidate metadata transport paths, zero post-anchor non-metadata paths, and 1,666 common candidate/control non-metadata demo blobs.

The runner produced a complete LOCAL_BATCH_RESULT.json: **25 Passed, 5 Failed, 4 Blocked**. Result SHA-256 a1ca2bebd20f8ecf9d7d9328cb72495f4d6a7e5b8235ab26ae4f137811d2ed03. Its mandatory seal passed and was independently reauthenticated member by member, including every live locator: 63,237/63,237 live bindings and 19,346/19,346 archive members. Seal-index SHA-256 8e421d228508e6546f5161876577d867841fe4794f6da369072bd0d6a5b96574; archive SHA-256 c475828ef428b6f77c6fb0695031243cab2e59b5626f2cdec283ce2e58f82f98. The authenticated review checkpoint is Docs/AssemblyShadow/History/M07R/R02/local-validation-20260928-batch-h-return-required/. The full live root and 573,188,976-byte archive remain intact, as do A/B/C/D/E/F/G and H1 evidence.

| Cell or group | Result | Evidence and limit |
| --- | --- | --- |
| Entry/final authority, common sources, host Primary, E forensics, candidate/control builds and frozen map | Passed | All nine Primary subcells passed. Actual macOS native writer/parser used the quoted project-header policy at diagnostics 0/1/2 with 1,310 checks and 12 native plus one legacy fixture. Fresh ON/OFF Unity graphs, M00 inputs, process completion and restoration passed on both roles. |
| Four control sidecars, candidate OFF and candidate ON-NoPatch | Passed | Six functional sidecars have authenticated Player runs and semantic checks. |
| Candidate ON-P01 and ON-P03 | **Failed** | Both raw Players exited successfully, but strict verification rejected the warm 10,000-allocation row. Each mode recorded 10,000 admission misses, proof attempts, unready decisions and baseline-state checks; 20,000 field and 20,000 interface workspace builds; 10,000 layout checks; only two cache hits. Metadata searches stayed at zero. The promised warm certificate reuse did not occur. |
| Four pilot plus forty formal A/B pairs / 88 processes; D1/D2 | Blocked / NotMeasured | Functional P01/P03 failures prevented the paired performance cell. There is no new R02 CPU/RSS acceptance analysis or D1/D2 disposition. |
| Editor, native regressions, generated-native inputs/transaction, negative fixtures and failure/recovery | Passed | EditMode passed 1,119/1,119, including all five exact R02 Editor contracts. Independent native and failure/recovery results passed. |
| M07 | **Failed** | Fourteen Player launches completed; strict verify-m07-results.py rejected the first P01 raw type resolution because the new r02 member is unknown to its historical schema. |
| Startup11 | **Failed** | Eleven launches completed, but the source-bound batch invoked absent Tools/AssemblyShadow/verify-r01-early-results.py. No strict aggregate startup verdict exists. |
| Count132 | Passed | Fresh matrix passed 132/132 launch verifications and verify-h1-count-matrix.py exited 0. |
| Diagnostic build and capacity | **Failed** / Blocked | The diagnostic receipt points to a batch-scoped _temp Player; the strict R01B input verifier requires a distinct Player under Builds/AssemblyShadow/R01B. Retained capacity inputs and overflow fixture passed; lazy/dense, ordinary capacity and mixed capacity were blocked. |
| Seal and independent stage review | Passed / NotEligible | Complete seal and independent authentication passed. ReturnRequired prevents independent R02 stage review. |

The direct warm-path failure is an incomplete admission certificate: pinned AssemblyShadowAllocationProof.h increments AdmissionUnready and returns without publication when certificate.complete is false. Pinned AssemblyShadowTypeResolver.cpp::CheckLayout marks the trace incomplete when a nonstructural source or target class has size_inited false. The evidence proves this path repeated 10,000 times in both modes; it does not identify the exact class or establish whether the workload or runtime readiness invariant needs correction. M07, startup11 and diagnostic-build are separate source/contract integration failures. No Local source, flag, pin, hash, timeout or verifier expectation was changed; no functional or performance Player was rerun as a workaround.

H1 remains PassedWithExplicitDeferredRisk. R02Accepted=false; mayEnterR03=false. Primary must publish a bounded source/control repair and new exact handoff before another unused batch root. Preserve the H archive and earlier evidence; do not begin R03.

## Historical run — 2026-09-28, sealed 34-cell R02LocalBatch-v1 returned at host contract compile

**Local Validation → Primary Implementation: `ReturnRequired`; independent R02 stage review NotEligible/NotRun.** One fresh batch ran once in unused `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/R02LocalBatch-20260928G/` with `TMPDIR=/private/tmp`, `PYTHONDONTWRITEBYTECODE=1`, Unity 2022.3.62f2, Python 3.14.6, PowerShell 7.6.3, .NET SDK 8.0.318 and macOS arm64 C++. Candidate and control demo worktrees fast-forwarded cleanly to exact pushed heads `d807b6e29ad22b15c2c425f78db8e61fbe197faf` and `028ad68fa25a531be07f11f1fdcc417842f98ab4`; both package worktrees already matched `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`. Candidate/control HybridCLR remained `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, with candidate IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` and control IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Eight remote/HEAD/clean source authorities passed. Candidate transport from source anchor `1642392278a97bc9348195e35ec5d1b7fb6fa530` changed nine metadata paths and zero non-metadata paths; candidate/control shared 1,664 non-metadata demo blobs.

`LOCAL_BATCH_RESULT.json` records **34 cells: 9 Passed, 1 Failed, 24 Blocked**, with SHA-256 `4df6eb37397291b10529b97a8e1ecfd14e8885ac1d7c258123acbfb480140772`. The mandatory seal **Passed**: index SHA-256 `8e349af00f80a208258c4fd1ec3e960608f93c8ffe5c31b4f08c1c034e494978`, archive SHA-256 `7356b7816409e142c9055334902551bc119ab08ca5d73485244bb6a3ba4c3678`. Independent member-by-member audit and all 9,031 live bindings passed for 8,662 unique archive blobs. The authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/R02/local-validation-20260928-batch-g-return-required/`; preserve the full G live root, its archive, and all A/B/C/D/E/F/H1 evidence.

| Cell/group | Result | Evidence and limit |
| --- | --- | --- |
| Entry/final authority and common source | `Passed` | Exact eight repository heads/remotes/pins and clean checkouts at both boundaries; no executable-source delta after anchor |
| Host Primary | **`Failed`** | Its source, native, revision, codec, 210/210 Python and managed Baseline/P01/P03 subcells passed. The actual native-writer/package-parser contract failed at `compile-0`: `/usr/bin/c++` with `-I il2cpp_plus/libil2cpp/vm` causes libc++ `<cstring>` to include the project's `vm/string.h`, which then cannot find `il2cpp-config.h`. Command exited 1 with clean process group. No producer/parser contract assertion ran. |
| E DLL forensics | `Passed` | Both missing prior-E live DLLs were recovered only as authenticated exact members of E's Git-bound index/archive, copied to G before builds and included in G's complete seal. They remain historical input bytes, not fresh Player evidence. |
| Independent native regressions, retained capacity input authentication, overflow fixture | `Passed` | These do not establish Unity build, capacity Player, or R02 acceptance. |
| Candidate/control builds, fixed M00 materialization and frozen map | `Blocked/NotRun` | Host Primary failure is a required build prerequisite; no new Unity graph, M00 materialization or valid ON/OFF build was produced. |
| Eight sidecars, four pilot plus forty formal A/B pairs / 88 timing processes | `Blocked/NotRun` | No candidate/control Player launches or CPU/RSS performance analysis; D1/D2 have no R02 measurement or disposition. |
| Five required Editor contracts, M07/startup/failure/count132/diagnostic/lazy-dense/capacity, generated transaction | `Blocked/NotRun` | Actual Unity/IL2CPP and regression repairs are still untested at this final source. The seven host synthetic Editor-coverage tests passed within Python but cannot replace the five real Editor cases. |
| Complete seal and independent stage review | `Passed` / `NotEligible` | Batch result binds a complete independently audited seal; result is `ReturnRequired`, not `EvidenceReadyForStageReview`, so no independent R02 review was commissioned. |

The direct compile error is not evidence of a parser semantic failure; the contract test never produced a native fixture. The contract tool uses `-I` for a directory containing a project `string.h`; the macOS libc++ include chain reaches that file before the intended C header. Primary CI's selected macOS subset did not exercise this actual contract compile, leaving the platform-specific include collision undetected. Exact command, stderr and source bindings are in the checkpoint and `RETURN_TO_WEB.md`. No local source/flag/pin/hash/timeout/verifier change or semantic retry was made.

H1 remains `PassedWithExplicitDeferredRisk`; `R02Accepted=false`; `mayEnterR03=false`. D1/D2 and independent review remain required before H2/R03.

## Historical run — 2026-09-27, 34-cell R02LocalBatch-v1 returned after batch E

**Local Validation → Primary Implementation: `ReturnRequired`; independent R02 stage review NotEligible/NotRun.** One fresh batch ran in `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/R02LocalBatch-20260927F/` with `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`. Candidate exact pushed handoff was `3e9a842b11c7848692728376aa5ab1bf4b20bece`, control exact pushed head `5a931fe86795e8cc192d3df262cdee824b105963`. Candidate source/tool anchor `d4cfbe5da29482a3b307fbec3333821615288129` differs from handoff by nine metadata paths and zero non-metadata paths. Candidate sibling heads were HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and R02 IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`; control used the same HybridCLR/package pins and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Source/remote authority and common source graph passed at entry.

The runner recorded **34 cells: 22 Passed, 8 Failed, 4 Blocked**. Its full `LOCAL_BATCH_RESULT.json` was **not produced**, because the mandatory seal failed. `SEAL_FAILED.json` names a missing prior-E compiled DLL in the forensic retained-input list; the matching prior-E control compiled DLL is also absent. These historical paths are neither reconstructed nor silently excluded. The Local failure checkpoint is `Docs/AssemblyShadow/History/M07R/R02/local-validation-20260927-batch-f-return-required/`. Its `LIVE_EVIDENCE_INVENTORY.json` hashes 1,984 existing batch and current external-root files, explicitly lists both missing E inputs, and is **not a substitute for the failed complete batch seal**. The live F batch and all A/B/C/D/E/H1 evidence remain preserved.

| Cell/group | Result | Evidence and limit |
| --- | --- | --- |
| Primary, E DLL forensics, candidate/control builds, frozen map | `Passed` | Host Primary's eight cells passed. Both role-specific fixed M00 materializations authenticated the exact 4,608-byte historical SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`. Fresh controlled ON/OFF M07 graphs, Unity Roslyn completion and restoration passed; E forensic analysis passed. |
| Eight functional sidecars | 5 Passed, 3 Failed | All four control and candidate OFF passed. Candidate ON-NoPatch, ON-P01 and ON-P03 produced Player raw `System.FormatException: Unknown type-resolution field: r02`. The pinned R02 native producer appends `r02`; the pinned managed type-resolution parser rejects unknown fields and requires 18 fields. This is a producer/parser schema integration failure. |
| Pilot/formal performance, D1/D2 | `Blocked` | Failed candidate functional sidecars barred the four pilot and forty formal A/B pairs. There are no 88 fresh timing processes, CPU/RSS analysis, or R02 D1/D2 disposition. |
| Editor, native, generated-input/transaction, negative fixtures, failure/recovery | `Passed` | Fresh Editor, independent native scripts, generated-native prerequisite and transaction path passed. Failure/recovery verifier passed. |
| M07 | `Failed` | First T07-01-Prefab-P01 Player exited 1 with startup refusal and no raw result. The retained log does not identify the cause; this is a separate unresolved failure. |
| Startup11 | `Failed` | Three expected-positive modes failed with the same `Unknown type-resolution field: r02` stack; eight expected-negative modes passed. |
| Count132 | `Failed` | The parameter manifest/audit passed, then `run_local.py::counts` invoked `audit-h1-count-fixtures.py` on the nested manifest. It rejected the contract before any of 132 matrix Players ran. The source contains a separate `audit-h1-nested-fixtures.py`. |
| Diagnostic build and capacity | `Failed` / `Blocked` | Diagnostic Unity changed tracked `Assets/HybridCLRGenerate/link.xml`; its cell failed clean-source authority. Final candidate authority also failed for that same generated change, and lazy/dense plus ordinary/mixed capacity were blocked. The changed bytes and diff are preserved in the checkpoint; after the process ended, the tracked file was restored byte-exact to HEAD. Final control authority passed. |
| Complete seal and stage review | `Failed` / `NotEligible` | Seal stopped at a missing batch-E forensic retained-input path, so no runner result or seal-index/archive exists for F. Independent R02 stage review was not commissioned. |

The checkout had no active Unity/batch process when the generated link was restored; its pre-restoration bytes are retained as `generated-link-after-diagnostic.xml`. The 1,984-file live inventory is a diagnostic preservation record, not an acceptance seal. No semantic retry, Player workaround, hash/pin change, M00 compiler helper, check relaxation, or non-trivial Local source repair occurred. The exact Primary return is in `RETURN_TO_WEB.md`.

H1 remains `PassedWithExplicitDeferredRisk`; `R02Accepted=false`; `mayEnterR03=false`. R02 measurement and independent review must precede any H2/R03 decision.

## Historical run — 2026-09-27, 33-cell R02LocalBatch-v1 returned at frozen M00 bytes

**Local Validation → Primary Implementation: `ReturnRequired`; independent R02 stage review NotEligible/NotRun.** One fresh `R02LocalBatch-v1` ran in unused root `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/R02LocalBatch-20260927E/` with `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`. Candidate pushed handoff was `6347b453169fec69a37963f9afc1a603a924cb28` on `codex/assembly-shadow-r01b-h1`; control was `a379f0b809a5d8af967df06fc83271d90fd84f4c` on `codex/r02-h1-runtime-control`. Common executable/tool source anchor `57a9470bf299af60f88112998c8326c4c013204a` differs from candidate handoff by nine metadata paths and zero non-metadata paths under `shadow_tools.metadata_only`. Candidate siblings were HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, R02 IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`; control used the same HybridCLR/package heads and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Entry/final authority, correct remotes, common managed graph and all eight clean checkouts passed.

`LOCAL_BATCH_RESULT.json` contains **33 cells: 9 Passed, 2 Failed, 22 Blocked**. Its SHA-256 is `f81095a7a2561faad6c69ececb8ec17f322c45ba92ae0cbaa633a1af3491d55a`. The bound seal-index SHA-256 is `be5d5dad20052a6244277ab372902274842d0200f86051ab7fe96d240e125cce`; archive SHA-256 is `5ee1e90e131e8a1c19b76b96e506d2be7e30e58888f6c1d3792b3594e0f0d6d2`. Independent member-by-member archive audit passed for 9,203 live locators and 8,763 unique blobs, including both failed compiled M00 DLLs and preparation receipts. The new authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/R02/local-validation-20260927-batch-e-m00-return-required/`. Preserve it, the complete E live batch and external ordinary-input roots, plus historical A/B/C/D and H1 evidence.

| Cell/group | Result | Evidence and limit |
| --- | --- | --- |
| Candidate/control entry and final authority, common source graph, host Primary | `Passed` | Correct eight repository identities, clean workspaces and remote heads; source checks do not establish build acceptance |
| Candidate/control Unity pinned installer completion | `Passed` within failed build cells | `commands/0004` and `0010` each had Unity exit 0, `R02OwnedUnityRoslyn-v2` completion `Passed`, `clean=true`, and outer process group clean. The batch-D installer completion rejection did not recur. |
| Candidate ordinary M00 preparation | **`Failed`** | `commands/0007` Unity `R02OrdinaryInput.Prepare` compiled a 4,608-byte DLL, SHA-256 `9d05065f57806073919b551cb9b23e8f2ef86fab96bb3cb6d8da80f74b82ba99`, instead of frozen `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`. Unity exited 1; process completion was clean. Failed `preparation.json` and compiled bytes are retained. |
| Control ordinary M00 preparation | **`Failed`** | `commands/0013` compiled a separate 4,608-byte DLL, SHA-256 `b6e8b232d1749ed67db7f7bda028522993c7e912a68192c05cad0fe8ef31f5e5`, differing from both frozen and candidate bytes. Unity exited 1; completion was clean. Its independent preparation and compiled bytes are retained. |
| Four independent native regressions, retained capacity inputs, overflow fixture | `Passed` | Budget, recovery, index-runtime and type-cache scripts passed; retained capacity is input authentication only |
| Native-generated prerequisite and transaction regression | `Blocked/NotRun` | Candidate build failed before a controlled graph existed. New dependency ordering worked; it did not yet validate real generated-native execution. |
| Controlled ON/OFF graphs, build map, eight functional sidecars, four pilot plus forty formal A/B pairs/88 processes | `Blocked/NotRun` | Both build cells failed at ordinary input; no valid Player, paired CPU or RSS sample was produced |
| Editor, M07, startup11, failure/recovery, count132, diagnostic, lazy/dense, ordinary/mixed capacity | `Blocked/NotRun` | Failed build and dependent prerequisites prevented these regressions |
| D1/D2 R02 measurement and independent stage review | `Blocked/NotEligible` | No controlled paired series; `LOCAL_BATCH_RESULT.json` is `ReturnRequired`, not `EvidenceReadyForStageReview` |

Both `preparation.json` receipts recorded the same two ordinary witness source-file hashes, but different source-pins hashes and different compiled DLL bytes. The candidate had an existing ignored M00 staged DLL with the frozen expected hash; the control had no staged DLL. Neither failed preparation staged or accepted its newly compiled output. The observed failure establishes a byte/provenance mismatch, not its precise compiler cause. Local did not copy the historical/candidate DLL into control, change the frozen hash or pins, relax a check, or retry semantic execution. Full command/log paths and Primary repair request are in `RETURN_TO_WEB.md`.

H1 remains `PassedWithExplicitDeferredRisk`; `R02Accepted=false`; `mayEnterR03=false`. D1/D2 need fresh R02 measurement before H2, and R03 must not begin.

## Historical run — 2026-09-27, repaired R02LocalBatch-v1 returned to Primary

**Result: `ReturnRequired`.** The fresh, unused `R02LocalBatch-20260927D` root was executed once from candidate handoff `3bbc2c8dee125ba9db47dcd0584c4a6285abebf8` and matched control `6c950eaa98f995084750fe1ea8f80cfe4c59c61b`. Candidate executable source anchor `82d64ce415c062729f0082e81c1808eaac9602e4` differs from its handoff by ten metadata paths and zero non-metadata paths. Candidate sibling heads were HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and IL2CPP `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`; the matched control used the same HybridCLR/package heads and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Entry and final authority, remotes, clean worktrees, and common managed executable graph passed. All eight worktrees were clean after removing one local audit-generated Python cache file.

The live batch is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/R02LocalBatch-20260927D/`; the authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/R02/local-validation-20260927-repaired-return-required/`. The batch has **31 cells: 8 Passed, 3 Failed, 20 Blocked**. `LOCAL_BATCH_RESULT.json` SHA-256 is `dc3185b3e0697894d19c99d581ab00a7d0f2533cdc8ca69a3b42425342a1b7f3`. Its bound `seal/seal-index.json` SHA-256 is `de3aae97aab1dcf86b6e92ad0e86cb31b83a27eec0726dece9fca431b91de602`; the archive SHA-256 is `5c6e082d58ca38f8a582eb2e746bc78ee565e2ead0b4b92e22b8e68637b106fb`. Independent member-by-member audit passed for 9,037 live locators and 8,657 unique archive blobs.

| Cell | Result | Observed limit |
| --- | --- | --- |
| Candidate/control authority, common graph, host Primary, final authorities | `Passed` | Exact source, remote and clean-worktree checks; host checks do not imply runtime acceptance |
| Candidate/control controlled builds | **`Failed`** | Unity `InstallRepeatability` logged success and exited 0 in both workspaces, but command-owned Roslyn completion returned `clean=false` after signalling `VBCSCompiler.dll`: `New or changed descendant during compiler completion`. The outer receipts `commands/0004` and `0007` correctly failed; neither build was accepted. |
| Native regressions | **`Failed`** | Four of five scripts passed. `run-r01-transaction-native-tests.py` failed its dependency scan on missing `icalls/mscorlib/System/MonoType.h` and the `please run 'HybridCLR/Generate/All'` guard. This cell currently depends only on source authority and executed before a successful generated-header workflow. |
| Retained capacity input authentication and overflow fixture | `Passed` | Inputs and fixture only; no capacity Player result was promoted |
| Ordinary M00 input, frozen build map, eight functional sidecars, 44 A/B pairs / 88 formal processes | `Blocked/NotRun` | Both build cells failed before ordinary-input preparation; no fresh paired CPU or RSS analysis exists |
| Editor, M07, startup11, failure/recovery, count132, diagnostic, lazy/dense, ordinary/mixed capacity | `Blocked/NotRun` | Build and dependent prerequisites failed; no affected regression Player was launched |
| D1/D2 R02 measurement/disposition | `Blocked` | No controlled paired performance or memory series; H1's accepted deferred risks remain open for R02 review |
| Independent R02 stage review | `NotEligible/NotRun` | Batch result is `ReturnRequired`, not `EvidenceReadyForStageReview` |

The first Unity failure is a completion-identity failure, not a Unity install/compiler exit failure. The completion receipts retain the original owned compiler PID, start time, group, DLL hash, TERM action, and exact error, but do not retain the changed post-signal census; therefore the changed process cannot be classified more narrowly from this evidence. The native failure is a separate ordering/prerequisite issue. No source change, assertion relaxation, semantic retry, or relabeling was made locally. Preserve batch D, its archive, prior A/B/C evidence, and both installed-runtime workspace roots while Primary diagnoses and repairs the source-bound runner.

H1 remains `PassedWithExplicitDeferredRisk`; `R02Accepted=false`; `mayEnterR03=false`. R02 stage review and H2 are not eligible. The exact return and proposed bounded Primary corrections are in `RETURN_TO_WEB.md`.

## Historical run — 2026-09-26/27, R02LocalBatch-v1 returned to Primary

### Exit

**Local Validation → Primary Implementation: R02LocalBatch-v1 is `ReturnRequired`; R02 is not accepted and independent R02 stage review is NotEligible/NotRun.** H1 retains `PassedWithExplicitDeferredRisk` from the recorded human D1=A/D2=A decision. `R02Accepted=false`; `mayEnterR03=false`. The batch did not produce a valid candidate/control build map, functional Player result, or controlled D1/D2 performance series.

The designated candidate checkout `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` was fast-forwarded cleanly to pushed handoff `5d163cbcb1b00b764ac0bc6e70a3ee0e1432a378` on `codex/assembly-shadow-r01b-h1`. Its executable source anchor is `06ba01e010c7eac3543dd6f23e083c2716941190`; the eight-path anchor-to-handoff delta contains zero non-metadata paths under `shadow_tools.metadata_only`. Candidate sibling heads matched `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, `il2cpp_plus=3981da12f2cd3ee878a04dda6f573d0ad3faeda5`. Four new registered control worktrees under `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/` matched demo `e6fdd32a6fd661a88ef108f7b055e4f7840e9e43`, HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Both four-repository authorities, their remotes, clean inputs, and the common managed executable graph passed at batch entry and final authority checks. All eight worktrees were clean after C.

The authenticated Local checkpoint is `Docs/AssemblyShadow/History/M07R/R02/local-validation-20260927-return-required/`. Complete live attempts are candidate `_temp/AssemblyShadow/R02LocalBatch-20260926A/`, `R02LocalBatch-20260926B/`, and `R02LocalBatch-20260927C/`; the bounded Unity cleanup probe is `_temp/AssemblyShadow/R02UnityCleanupProbe-20260926C/`. None was overwritten or cleaned. Each batch produced `LOCAL_BATCH_RESULT.json`, command/cell receipts, a `Passed` content-addressed seal, and an archive. All three archives were independently reauthenticated member-by-member: A 8,646 unique members, B 8,655, C 8,664. Archive and index SHA-256 bindings are in the checkpoint.

| Cell | Classification | Evidence and limit |
| --- | --- | --- |
| Candidate/control source authority and common graph | `Passed` | Exact eight repository heads, remotes, clean inputs, source pins, and identical non-metadata demo blobs |
| Host Primary | `Passed` in B and C | Source reconstruction, native and revision matrices, codec storage, 115 Python tests, and managed Baseline/P01/P03 checks all passed; A Python had two macOS `/var` symlink test errors, corrected by `TMPDIR=/private/tmp` without source edits |
| Candidate controlled graph | `Failed` in C | Internal M07 workflow completed and restored tracked inputs, but outer command `commands/0006` exited 0 with `processGroupClean=false`: owned `dotnet` / Unity `VBCSCompiler.dll` survived; strict batch rightly rejected its build evidence |
| Control controlled graph | `Failed` in C | `commands/0011` exited 1 and also had a surviving owned `dotnet`; first compiler error was missing ignored `Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes` in the fresh control worktree |
| Candidate native regressions | `Passed` in C | All five budget, recovery, transaction, index-runtime, and type-cache scripts passed after the candidate's internal build generated its local native header; B transaction test failed earlier with an empty generated Unity-version header |
| Retained capacity input authentication and overflow fixture | `Passed` | Historical capacity bytes were authenticated as inputs only; no historical execution PASS was promoted |
| Frozen build map, eight functional sidecars, 44 A/B pairs/88 timing processes | `Blocked/NotRun` | Both controlled graph prerequisites failed; zero valid paired samples and no CPU/RSS comparison |
| Editor, M07, startup11, failure/recovery, count132, diagnostic, lazy/dense, ordinary/mixed capacity | `Blocked/NotRun` | Candidate build prerequisite failed; no affected regression Player was launched |
| Source final checks and evidence seals | `Passed` | Candidate/control final authority passed; A/B/C `R02EvidenceSeal` archives passed independent full-member authentication, including failure outputs |
| D1/D2 disposition | `Blocked` for R02 comparison | No cold/warm or RSS paired series. Host codec probe measured four unchanged profile-2 allocation requests totaling 29,884,384 bytes plus a 144-byte object on this local ABI; that is not Unity RSS, allocator overhead, or new R02 bytes |
| Independent R02 stage review | `NotEligible/NotRun` | `LOCAL_BATCH_RESULT.json` is `ReturnRequired`, not `EvidenceReadyForStageReview`; H2 human review and R03 are closed |

Attempt A used the default macOS Python temporary path under `/var`, which resolves through a symlink; strict tests rejected two linked-parent paths (115 leaves total). An isolated identical 115-test run with canonical `TMPDIR=/private/tmp` passed, and B then passed all host Primary checks. B's candidate and control Unity installer commands exited zero but failed owned-process cleanup due a surviving `dotnet` child. A bounded separate Unity install probe with `TMPDIR=/private/tmp`, `DOTNET_CLI_DO_NOT_USE_MSBUILD_SERVER=1`, `MSBUILDDISABLENODEREUSE=1`, and `DOTNET_CLI_USE_MSBUILD_SERVER=0` exited zero with `processGroupClean=true`, so C used those exact environment settings. C's longer M07 command still spawned Unity's `VBCSCompiler.dll`; its process outlived the outer PowerShell command. The C candidate workflow's own success line cannot override the failed process-group receipt. Control additionally needs canonical generation of its missing M00 hot-update input before compiler validation; copying the candidate's ignored output into control would break the matched-build provenance contract.

Primary needs a source-bound runner/workflow correction that produces and authenticates the control M00 input from its own source, and that waits for or terminates only the command-owned Unity compiler server before declaring a clean process group. Preserve the existing strict no-survivor criterion, failed attempts, and generated-input restoration checks. After a pushed repair and a new exact handoff, Local can run a new batch root. The present run does not establish a D1/D2 performance improvement or memory budget; the user-accepted H1 deferred risks remain open for R02 measurement before H2.

## Historical run — 2026-09-25, fresh source-038 count closure and independent M08 PASS

### Exit

**Local Validation → Primary Implementation: protocol `H1CountMatrixClosureSource038-v1` passed, the six-suite chain is supported, and genuinely independent read-only M08 returned MILESTONE PASS with no findings.** H1 is `ReadyForHumanReviewGate`; `M08Passed=true`, `humanGatePassed=false`, and `mayEnterR02=false`. R02 remains closed until explicit human H1 approval.

The validation checkout `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` started at pushed handoff `df14afd618edd408356ee9559937ccf9080caef8` on `codex/assembly-shadow-r01b-h1`. Source anchor `0388479f7073289e3505b992956a7cbe78c302ce` had zero non-metadata changes through the handoff and final Local commits. The other three source heads remained `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `il2cpp_plus=6be7f38bec2fa4677d24efc1a4a1294240789933`. The designated protected reproduction behavior and committed tooling were authenticated separately. Both committed candidate and reproduction preflights passed after execution; neither claimed build acceptance by itself.

The authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260925-authority038-fresh-count-m08/`. Its frozen 82-entry `PRE_M08_MANIFEST.sha256` bound the exact C00–C09 evidence reviewed independently. `FINAL_STATUS.md`, C10 review output and receipt, and handoff snapshots are bound by the final `MANIFEST.sha256`. The complete live run is `_temp/AssemblyShadow/H1CountClosure038-20260925B/`, including seven sealed archives; four selected candidate build roots also remain live. Preserve those bytes through human review.

| Cell | Result | Evidence and limit |
| --- | --- | --- |
| C00 source/handoff/reproduction authority | `Passed` | Four exact source heads, source-038 post-anchor metadata-only, both post-execution preflights Passed |
| C01 fresh fixtures | `Passed` | Seed 20260925, 12 parameter and 10 nested cases, both independent audits Passed |
| C02/C03 six builds and selection | `Passed` | Six distinct provenance-bound builds, native `Passed`, managed `SourceGraphBound`, exact restoration; four candidate ON/OFF × Debug/Release receipts selected by tuple |
| C04/C05 fresh count matrix | `Passed / 132` | Timeout 120 seconds per launch; fresh 132-cell Player series and strict aggregate verification exit 0 |
| C06 Launch/Raw audit | `Passed` | Exactly 132 verifier reports, 132 launch receipts, 132 semantic raw outcomes, 132 unique run IDs/PIDs; 118 ordinary Passed and 14 expected validation rejections |
| C07 evidence seal | `Passed` | Seven archives: fixtures, matrix, build batch, four selected candidate build roots; every regular member matches its inventory and live file; zero AppleDouble |
| C08 fresh count closure | `PassedFreshSource038CountMatrix` | Fresh source-038 count proof bound to fixtures, builds, 132-cell audit, and archives |
| C09 whole chain closure v2 | `SixRequiredSuitesSupported` | Count=`FreshCurrentSourceExecution`; startup11, failure/publication/recovery, ordinary capacity, mixed capacity, M07/native=`AcceptedReusedAudited` |
| C10 independent M08 | **`MILESTONE PASS`**, zero findings | Read-only `code-gate-reviewer` authenticated the committed checkpoint and live/archive evidence, revisited all three previous BLOCKED findings, and launched no Player |

The first A build batch stopped before Unity because the candidate installed-runtime receipt still named demo pin `316894a`, not source 038. That failed attempt and its 957-file preinstall native-runtime archive were preserved. Local reran the pinned installer, verified the new installed receipt, regenerated both fixture families in separate B root, and completed the six-build batch. No source file or historical execution evidence was changed to make the preflight pass.

The independent review ran from `2026-09-25T11:41:32Z` to `11:57:00Z`. It found no remaining M08 evidence gap. The former 12cf count matrix stays blocked in its historical record; only the new source-038 series supplies the current count Launch/Raw chain. The other five suites remain audited reuse, not fresh execution. Prior V04/V05 analysis and the source-27df formal 40/40 were not rerun. No performance/formal Player, capacity, startup11, failure, or M07/native rerun occurred.

`ComparabilityPassed` establishes measurement validity, not performance acceptance. The full V04 analysis retains unfavorable ON-P01 and ON-P03 allocation, reflection, closed-generic, and RSS measurements for the human H1 gate. The next action is explicit human H1 review of the sealed evidence and measured performance; independent M08 PASS alone does not permit R02.

## Historical run — 2026-09-25, M08 evidence closure re-review

### Exit

**Local Validation → Primary Implementation: the evidence-closure package authenticates its recovered origins and historical manifest successor claims, but the required count-chain suite is BLOCKED. The independent M08 re-review returned BLOCKED with one high-priority finding.** H1 remains `InProgress`; `M08Passed=false`, `humanGatePassed=false`, and `mayEnterR02=false`. R02 remains closed. No Player or formal runner was rerun.

The clean validation worktree `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` was fast-forwarded to pushed handoff `384662d08482f804bfa9772c4acf38b834c57db1` on `codex/assembly-shadow-r01b-h1`. The source anchor remains `0388479f7073289e3505b992956a7cbe78c302ce`; its delta to the handoff HEAD has 79 metadata paths and zero non-metadata paths under the unchanged `shadow_tools.metadata_only` policy. The other three worktrees were clean and matched their pushed heads: `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `il2cpp_plus=6be7f38bec2fa4677d24efc1a4a1294240789933`. Committed handoff preflight returned `SourceTargetVerifiedNotBuildAccepted`. The existing source-038 V05 SHA-256 `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f` and prior Local checkpoint manifest SHA-256 `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10` were unchanged. In accordance with this metadata-only handoff, V01, V02, V04, and V05 were not rerun.

The new authenticated Local checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260925-authority038-m08-re-review/`. It contains E00–E05 receipts, the initial and corrected E04 dispositions, the independent review verbatim, a machine receipt, and snapshots of this report and the Primary return. The Primary closure bundle remains at `Docs/AssemblyShadow/History/M07R/H1/current-primary/m08-evidence-closure-20260925/`; historical checkpoints and recovered JSON were not modified.

| Cell | Result | Evidence and limit |
| --- | --- | --- |
| E00 source/handoff authority | `Passed` | Exact four pushed heads, zero source-038→HEAD non-metadata paths, committed preflight, existing V05/checkpoint hashes unchanged |
| E01 recovered origins | `Authenticated` | All 11 prior-review/12cf copies byte-equal their immutable Git origins; reconstructed 925e Handoff bytes equal commit `075f8a25...` and expected SHA-256 `cb8f06d7...52a3d54` |
| E02 historical checkpoint successor | `AuthenticatedWithExplicitHistoricalExclusion` | 925e effective 293/293 using the recovered external Handoff member; 6913 has 29 verified plus one unavailable/excluded prelaunch log absent at creation commit; original 6913 manifest is **not** claimed 30/30; source-27df superseding checkpoint 92/92, formal 40/40 |
| E03 prior P1 successor mapping | Authenticated facts for re-review, not acceptance | COUNT 12cf summary says 132/132 and six provenance builds; startup11 has 11 distinct historical PIDs and `ReusedAuditedFrom925e` classification; eight UNFIXED-REPRO cells retain 6 `UnexpectedAccepted`, 2 Debug `AssertAbort`, and `candidateAcceptance=false` |
| E04 whole-chain source/index audit | `Passed` within its measured scope | 925e→038 exact 70 Bootstrap, 16 Runtime, 42 H1 count, three failure-tool and three capacity-tool blobs unchanged; native/package/IL2CPP pins unchanged; all 884 indexed 925e artifacts plus raw archive and 3168 reuse bindings authenticate |
| E04 per-suite disposition | **Five `AcceptedReusedAudited`, one `Blocked`** | Startup11, failure/publication/recovery, ordinary capacity, mixed capacity, and M07/native accepted as reused. Count-chain blocked because the selected 12cf 132/132 reports lack their launch/raw layer. |
| E05 independent `MILESTONE` re-review | **`BLOCKED`**, one high-priority finding | Read-only `code-gate-reviewer` independently confirmed the count evidence gap and revisited all three previous BLOCKED findings. Review retained verbatim. |

The initial E04 suite receipt recorded six accepted suites after checking the 12cf summary, six-build provenance record, and archive Git blob identity. It did **not** inspect the archive member set or resolve the per-cell launch/raw references before accepting count-chain. The initial receipt and its nine-entry pre-review manifest are retained as failed-attempt evidence. The subsequent `E04/count-chain-raw-availability.json` examines all 132 verifier reports in the immutable Git archive: its 133 business members are 132 `verification.json` files plus `result-index.json`; none of the referenced 132 launch receipts or 132 raw results is present in the archive or designated checkout. The archive also contains 133 AppleDouble metadata entries. The corrected E04 receipt classifies count-chain `Blocked`, leaves five suites `AcceptedReusedAudited`, and makes independent M08 eligibility false. E03 remains an authentication of historical summary/provenance facts; it does not promote the count Player execution to an accepted raw-evidence chain.

The independent reviewer ran read-only from `2026-09-25T08:44:08Z` to `08:58:55Z` and returned `BLOCKED`. It confirmed the recovered prior-review provenance, the 925e effective 293/293 and 6913 29+1 dispositions, and the supportable reuse of five suites. It found that the 12cf candidate count archive cannot establish the canonical Launch and Raw semantics layers for the selected 132/132 claim; the later 925e six-build GUIDs differ and cannot replace the missing 12cf launch provenance. Its full reasoning and unfavorable performance observations remain verbatim in `E05/independent-review.md`. The independent review was commissioned from the initial E04 receipt; its finding prompted the corrected Local classification. This re-review does not confer `ReadyForHumanReviewGate`.

Primary must recover and index the exact 132 historical count launch receipts and raw results, together with their referenced build/input bytes and per-cell semantic checks, or arrange a separately authorized new controlled count matrix with a frozen source/build. The current Local handoff does not authorize a Player rerun. After count-chain can genuinely be `AcceptedReusedAudited`, a new independent M08 review is required. `ComparabilityPassed` in the reused source-27df performance analysis remains measurement validity only; P01/P03 slowdowns and higher RSS remain human-review inputs, not accepted performance.

## Historical run — 2026-09-24/25, source 038 V05 and independent M08

### Exit

**Local Validation → Primary Implementation: V00–V05 passed within the analysis-only handoff; genuinely independent M08 returned BLOCKED with three evidence gaps.** The 40/40 formal Player series was not rerun. H1 remains `InProgress`, `M08Passed=false`, `humanGatePassed=false`, and `mayEnterR02=false`; R02 remains closed.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, at pushed handoff HEAD `4b8e8617deee75dbc10241e120ec2e8a3b3cd366` before this metadata-only checkpoint/report commit, with source anchor `0388479f7073289e3505b992956a7cbe78c302ce`. The other clean, remotely verified worktrees matched `hybridclr=1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `hybridclr_unity=0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `il2cpp_plus=6be7f38bec2fa4677d24efc1a4a1294240789933`. `V00/source-authority.json` records exact paths, heads, remote refs, source/package pins, and worktree registrations. The original execution source remains `27df1a3d60811dc121f296ab561ae313a382b363`.

The pre-V05 V04 closure checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-pre-v05-v04/`: all 22 manifest members verify; its manifest SHA-256 is `bd8a7e575503623a0c8bf98739a1a8da3c0cc3bebc44dbdd94075c74e7f92c28`. The final Local checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority038-v05-m08/`: all 28 manifest members verify; its manifest SHA-256 is `71cbe155977a08fadacea92c641203c218d05db242ed301dd5d70bd249d31d10`. The final checkpoint retains the independent review verbatim and a SHA-bound receipt. Command receipts retain the exact commands, cwd, UTC intervals, outputs, and exit codes.

| Cell | Result | Evidence and limit |
| --- | --- | --- |
| V00 source authority and committed preflight | `Passed` | Exact four-repository pins and remote heads; source-anchor→handoff HEAD zero nonmetadata paths; preflight `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | 387/387 Passed, zero Failed/Error/Skipped; six V05 leaves included |
| V01 complete Python discovery | Required zero Failed/Error met; 28 environment skips | 1,071 leaves: 1,043 Passed, 28 Skipped; inventory CLI exit 2 reflects skip policy; full inventory/log and explicit skip reasons retained |
| V01A source audits | `Passed` | Source-27df→038 exact seven analysis/test paths; retained-6913→038 exact 25 paths; d61→038 exact three paths |
| V02 immutable historical reauthentication | `PassedHistoricalIntegrityOnly` | 92/92 source-27df manifest, four fixed live hashes, 33,792/33,792 sealed files totaling 1,606,993,133 bytes; zero missing/content/stable-stat mismatches; 33,981 direct bindings with zero unresolved semantic mismatches |
| V04.AF split-checkout compatibility | `AuthenticatedAnalysisOnlySuccessor` | Current analysis checkout and original historical evidence root remain distinct; exact v2 source policy and live historical authority pass |
| V04.AG strict historical analysis | `Passed` / `ComparabilityPassed` | Fresh analysis of immutable original bytes: 45 attempts, 44 valid, one preserved invalid ON-NoPatch pilot, 40/40 valid formal, ten formal pairs/startup observations per mode, chronology and non-overlap pass |
| V04 closure | `Passed` | 22-entry pre-V05 manifest; full performance JSON, exact assertion receipt, and scoped no-Player command proof |
| V05 successor binding | `SuccessorEvidenceBoundForIndependentM08` | `H1AnalysisOnlySuccessorEvidence-v1`; current tests Fresh, historical execution Reused, historical performance Reanalyzed; complete performance JSON SHA bound; no Player; performance acceptance `NotClaimedNoSLA`; M08/human/R02 flags false |
| Independent M08 `MILESTONE` | **`BLOCKED`**, three findings | Read-only `code-gate-reviewer` examined the complete V05 package and H1 gate; review and machine receipt in `M08/` |

V04.AG ran once and exited 0 after full strict verification. The full paired analysis SHA-256 is `c02c4ffd0ad93759ef4f2ffb3a7482b3c9d5ed96cf4c9a122f35135478323053`. The original failed `R00-ON-NoPatch-pilot-01` still records process-group cleanup failure and skipped B side. In the warm repeat-10,000 phase, median paired B/A ratios for allocation, reflection invoke, and closed generic are 1.133/1.266/1.204 for ON-P01 and 1.150/1.276/1.221 for ON-P03. B median RSS is higher than protected A in every mode at both snapshots; P01/P03 managed-memory medians move downward. `ComparabilityPassed` is measurement validity, not performance acceptance. The full timing, startup, memory, and variance statistics remain visible to M08.

The first V05 invocation failed before analysis because its new output directory had not been created. Its failure receipt is preserved. After creating that empty directory, the identical package command exited 0 and produced V05 SHA-256 `534eba62b817584f1a2d48c2fa1bcfccf498d447351c34f10a412993fff3d73f`; no input or Player evidence changed for the retry. The final checkpoint retains both command receipts and all 15 Local V05 assertions.

The independent M08 review ran read-only from `2026-09-25T06:35:25Z` to `06:48:23Z` and returned **BLOCKED**, not PASS. Its three findings are: (1) the original M08 review/finding-closure records referenced by `History/M07R/R01B/H1-handoff.md` are not available in the designated local paths for finding-by-finding closure; (2) older whole-H1 manifests verify only 292/293 and 29/30 members at their listed paths, respectively, although the reviewer did not infer corruption of the current 40/40 formal raw evidence; and (3) V05 does not provide the required selected suite-by-suite equivalence bridge for older capacity, failure, recovery, count, and startup claims. The complete reviewer wording, evidence paths, performance observations, and closure requests are preserved verbatim in `M08/independent-review.md`. These gaps require Primary evidence disposition and a new independent M08 review. Human H1 approval is still separate even if a future M08 returns PASS.

No Unity Editor, native build, IL2CPP build, Player, profiler, or formal runner was invoked in this analysis-only cycle. `V04/no-player-proof.json` records Local command issuance with its stated scope limit. Historical Unity EditMode and runtime results remain historical/reused where separately supported; this run does not promote them to fresh current-source execution.

## Historical run — 2026-09-24, split-checkout historical analysis

### Exit

**Local Validation → Primary Implementation: V04 closed; V05 is not eligible under the current handoff, so independent M08 was not run.** V04.AF authenticated the separate current analysis checkout and historical evidence root. V04.AG then returned `Passed` / `ComparabilityPassed` for the immutable source-27df 40/40 series. No Player was rerun.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, pushed handoff HEAD `0bed47e981e5b3b4ac8b9ed2b4c423e11aa88b31` before this metadata-only report/checkpoint commit, and source/tool anchor `d61bd9df15268f5b02b6ac7a0ad8a06f9fc54ece`. The other clean, remotely verified worktrees remained `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. The source pins, package reference, remote heads, worktree registrations, and host versions are recorded in `V00/source-authority.json`.

The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd61-split-analysis/`. Its `MANIFEST.sha256` covers 24 evidence/README files, SHA-256 `04ca3e24a1f16f21cbbde7e62493070529ffce4720beebac2c1f1615ab3b3553`; all 24 verified independently. Command receipts retain exact commands, UTC start/end, cwd, exit codes, stdout/stderr and paths. V04.AG ran once from `2026-09-24T06:57:24Z` to `17:08:44Z` and exited 0. Python was 3.14.6 on macOS arm64. Unity 2022.3.62f2 / StandaloneOSX / arm64 is the pinned target, but Unity and Players were not invoked in this analysis-only cycle.

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 four-repository authority and committed preflight | `Passed` | `V00/`; all four pushed worktrees clean at entry; `d61→0bed` zero non-metadata paths; preflight `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | `V01/bounded-primary/`: 381/381 Passed, zero skips/failures/errors; four split-checkout regressions included |
| V01 complete Python discovery | `CompletedWithNonPass` from explicit environment skips; required zero failures/errors met | `V01/python-inventory.json` and full log: 1,065 leaves, 1,037 Passed, 28 Skipped, zero Failed/Error; the inventory CLI exit 2 reflects its skip policy |
| V01 exact source audits | `Passed` | `V00/source-authority.json`: source-27df→d61 exact v2 seven paths; retained-6913→d61 exact v2 25 paths; d239→d61 exact three paths |
| V02 source-27df checkpoint and complete live reauthentication | `PassedHistoricalIntegrityOnly` | `V02/`: 92/92 prior checkpoint manifest; four fixed live hashes; 33,792/33,792 sealed files, 1,606,993,133 bytes, zero missing/content/stable-stat mismatches; 184 additional current-live bindings match and five historical Git-source/tool identities match pinned Git blobs, zero unresolved |
| V04.AF split-checkout compatibility | `Passed` | `V04/historical-compatibility.json`: `AuthenticatedAnalysisOnlySuccessor`, analysis root is the designated worktree, historical root is the unchanged ordinary owner, exact v2 policy and source-27df bridge/seal/formal authority |
| V04.AG strict historical analysis | `Passed` / `ComparabilityPassed` | `V04/historical-performance-analysis.json` and `analysis-validation.json`: 45 retained attempts, 44 valid, exactly one preserved invalid ON-NoPatch pilot, 40/40 valid formal, ten formal pairs and startup observations per mode, one valid pilot per mode, complete chronology and non-overlap |
| V04.AH analysis-only closure | `Passed` | New 24-entry SHA-256 checkpoint manifest verified; full measured statistics, including unfavorable values, retained unchanged in analysis JSON |
| V05 successor | `NotEligible / NotRun` | `V05/eligibility.json`: current handoff names V05 but provides no runnable analysis-only successor criteria; the historical series cannot be relabelled fresh current-source execution and Player reruns are forbidden in this handoff |
| Genuinely independent M08 | `NotEligible / NotRun` | `M08/eligibility.json`; no successor package eligible for a whole-chain review, so historical independent M08 `FAIL` remains the only M08 result |

The original failed `R00-ON-NoPatch-pilot-01` retains its process-group cleanup error and skipped B side. The 40 formal attempts were not replayed. V04.AG authenticated and reanalyzed existing bytes; it did not create current-source Player evidence or change the original live source-27df paths. `V04/no-player-proof.json` records Local command issuance and its scope limit. Earlier runtime evidence remains `ReusedAuditedFromFF3D`, and Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`; neither is fresh current-source execution.

`ComparabilityPassed` establishes that the paired measurements can be analyzed, not that they meet a performance target. In the `repeat10000` phase, the median paired B/A ratios for allocation, reflection invoke, and closed generic are respectively 1.133/1.266/1.204 for ON-P01 and 1.150/1.276/1.221 for ON-P03. The candidate B median current RSS exceeds protected A in every mode at both memory snapshots. The analysis JSON retains every measured value and statistic for independent review.

Primary must state an exact V05 successor-evidence contract that is compatible with this analysis-only, no-Player boundary, or explicitly defer V05 to a separately authorized fresh-execution program. Only after an eligible V05 package should a genuinely independent M08 review be commissioned. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 remains closed.

## Historical run — 2026-09-24, v2 historical compatibility preflight

### Exit

**Local Validation → Primary Implementation: FAIL at V04.AF historical compatibility preflight.** The fail-closed preflight rejected the checkout selected for current analysis authority. Corrected historical analysis, V05, and independent M08 were not run. No Players were rerun.

The validation checkout was `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, pushed HEAD `aedf3c58c3e3f8ab612552563a29c8906b82bea1` before this metadata-only report commit, with demo source/tool pin `d239d9d00784ea2df22133cb8c938ec25035f5a0`. The other clean, remotely verified validation worktrees were `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. Native/package/IL2CPP source pins and the Unity package file reference resolve to these worktrees. `V00/source-authority.json` records exact paths, branches, commits, remote heads, worktree registrations, pins, and host versions before report edits.

The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authorityd239-compatibility-project-blocked/`. Its `MANIFEST.sha256` covers 17 evidence and README files; verification passes. Command receipts contain exact commands, UTC start/end, cwd, exit codes, and output paths. The run used Python 3.14.6 on macOS arm64. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity and Players were not invoked. No local source or test fix was made.

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 four-repository source/native/package authority | `Passed` | `V00/source-authority.json`; all four initial worktrees clean and at pushed commits; anchor `d239d9d0` → handoff HEAD has zero non-metadata paths |
| V00 committed handoff preflight | `Passed` | `V00/handoff-preflight.json`: `SourceTargetVerifiedNotBuildAccepted`, not a build acceptance result |
| V01 bounded Primary | `Passed` | `V01/bounded-primary/results.json` and `tests.log`: 377/377 Passed, zero skips/failures/errors |
| V01 complete Python discovery | `CompletedWithNonPass` from explicit skips; handoff requirements met | `V01/python-inventory.json` and `python-tests.log`: 1,061 leaves, 1,033 Passed, 28 environment Skipped, zero Failed/Error; corrected positive paired-performance leaf Passed. Inventory CLI exit 2 reflects skip policy, not a test failure; 27 skips lack the canonical H1R coordination directory and one lacks real compiler/config paths. |
| V01A exact source audits | `Passed` | `V00/source-authority.json`: `27df1a3d` → `d239d9d0` exact seven-path `H1HistoricalPerformanceReanalysis-v2`; `69130bbb` → `d239d9d0` exact 25-path `H1V04RetainedGraphToolOnlySuccessor-v2`; `27df` → handoff HEAD remains exact seven paths |
| V02 source-27df checkpoint manifest and fixed live inputs | `PassedHistoricalIntegrityOnly` | `V02/historical-checkpoint-manifest.log`: 92/92; `V02/live-evidence-reauthentication.json`: original live bridge `c03665db...`, seal `bdc4062a...`, formal batch `97ddb6c8...`, final sample `a8e519c3...` all SHA-256 exact |
| V02 complete live sealed graph | `PassedReadOnlyReauthentication` | 33,792/33,792 files, 1,606,993,133 bytes, zero missing/content/stable-stat mismatches. 184 additional current-live direct bindings match. The initial generic binding audit marked five historical Git-source/tool identities as live mismatches; `V02/direct-binding-semantics-audit.json` verifies their pinned Git blobs and reports zero unresolved mismatches. Both audit receipts are retained. This does not replace the V04 semantic proof. |
| V04.AF v2 historical compatibility | `Failed` | `V04/historical-compatibility-v2.json`, command receipt and checkout-selection diagnosis: exact v2 policy says the two new test paths are missing from the source delta selected by the tool |
| V04.AG corrected historical strict analysis | `Blocked / NotRun` | Requires V04.AF `AuthenticatedAnalysisOnlySuccessor` |
| V04.AH analysis-only closure, V05, independent M08 | `Blocked / NotRun` | No authenticated compatibility/analysis result; historical M08 `FAIL` is unchanged |
| Current Unity/native/IL2CPP builds, Players, profiler | `NotRun` | Analysis-only handoff; original source-27df 40/40 execution remains historical and unchanged |

The preflight uses the original live source-27df bridge, seal, batch, and final sample paths as required. It checks `bridge.projectRoot` (`/Users/ah/GitHub/hybridclr/hybridclr_demo`) for **current** source pins. That ordinary owner checkout is detached at `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` and pins demo source `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The designated validation checkout pins `d239d9d0`; the audited v2 seven-path delta is there. Thus the preflight returns `H1HistoricalPerformanceReanalysisFailure` with `missing=[Tools/AssemblyShadow/h1_bee_primary_tests.py, Tools/AssemblyShadow/tests/test_h1_paired_performance.py]`. This is a checkout-selection defect in the compatibility tool, not a live evidence hash failure. `RETURN_TO_WEB.md` contains the exact reproduction and Primary implementation direction.

The immutable source-27df execution checkpoint and 40/40 formal series remain historical. Earlier runtime evidence remains `ReusedAuditedFromFF3D`; Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`. Neither is fresh current-source execution. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. After Primary publishes a source-authority-safe repair, Local must restart V00, V01, live reauthentication, V04.AF, V04.AG, checkpoint authentication, V05, and genuinely independent M08 in order. R02 remains closed.

## Historical run — 2026-09-23/24, repaired analysis-source handoff

### Exit

**Local Validation → Primary Implementation: FAIL at complete Python discovery.**

The final pushed Primary handoff was checked out cleanly at `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`, branch `codex/assembly-shadow-r01b-h1`, HEAD `dd3c8988e9136e0c3a8ca965f82067d6b7c83acd`. Its build-input/tool anchor remains `7aa6f61994da354b04464e38ddfc8552cc5c3055`. The other validation worktrees and matching pushed commits are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` at `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` at `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` at `6be7f38bec2fa4677d24efc1a4a1294240789933`. All use the expected branch. Native/package/IL2CPP pins and the Unity package file reference resolve to this validation workspace. Exact repository inventories are in the new checkpoint's `V00/v00r-source-authority.json`.

V00.R passed: all nine restored `.agents`/`.codex` files are byte-identical to their `7aa6f619` Git blobs; the complete 7aa→HEAD non-metadata delta is empty. The 27df→HEAD non-metadata delta is exactly the fixed five analysis-only paths, and the retained 6913→7aa delta is exactly the 24-path allowlist. The committed V00 preflight returned `SourceTargetVerifiedNotBuildAccepted`. This authenticates source identity, not a new Player build or acceptance gate.

Bounded Primary regression passed 376/376. Complete Python discovery then executed 1,061 leaves: 1,032 `Passed`, 28 explicit `Skipped`, and one `Failed`. The failure is `test_h1_paired_performance.H1PairedPerformanceTests.test_analyze_sample_index_complete_positive`. Its synthetic `raw()` fixture stores build GUID, baseline ID, and runtime ABI only inside `playerBuildReceipt`; the corrected analyzer requires those three values at raw-result top level and rejects all 44 synthetic pilot/formal attempts with `R00 raw top-level build field differs: buildGuid`. The focused committed test reproduced this. Adding those top-level fields from the expected receipt **in memory only** made the focused test return `ComparabilityPassed`; no repository test or production source was edited. The bounded suite does not contain this failing positive test.

Changing the test file in this checkout would create a sixth non-metadata path after the fixed `7aa6f619` anchor and invalidate both current source preflight and the exact five-path historical compatibility rule. This is therefore a Primary source-authority decision, even though the test fixture defect itself is narrow. `RETURN_TO_WEB.md` gives the reproduction and corrective direction.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| Four-repository Git/native/package preflight | `Passed` | `V00/v00r-source-authority.json`; exact pushed commits and clean checkouts before report edits |
| V00.R repaired source-authority audit | `Passed` | Nine restored bytes exact; 7aa→HEAD zero non-metadata; 27df→HEAD exact five; 6913→7aa exact 24 |
| V00 committed handoff/source preflight | `Passed` | `V00/handoff-preflight.json`; `SourceTargetVerifiedNotBuildAccepted` |
| V01 bounded Primary | `Passed` | 376/376, full inventory and log in `V01/bounded-primary/` |
| V01 complete Python discovery | `Failed` | 1,032 Passed / 28 Skipped / 1 Failed; `V01/python-inventory.json` and `python-tests.log` |
| V01 focused fixture diagnosis | `FailedAsCommitted`; `PassedWithInMemoryDiagnosticCorrection` | 44 invalid synthetic attempts as committed; no file edit or authoritative PASS claim |
| V02 historical checkpoint and four fixed live hashes | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries and four SHA-256 matches; full live graph not reauthenticated this cycle |
| V04 historical compatibility preflight and corrected analysis | `Blocked / NotRun` | Complete Python prerequisite has one failure |
| Analysis-only closure checkpoint / V05 / independent M08 | `Blocked / NotRun` | V04 remains incomplete |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff is analysis-only; no new build GUID or execution evidence |

The run used Python 3.14.6 on macOS arm64; command receipts in the checkpoint record UTC start/end, exact commands, logs, paths, and exit codes. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The authenticated return checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-python-fixture-blocked/`, containing all fresh V00/V01 and independent integrity evidence plus `MANIFEST.sha256`. The immutable source-27df execution checkpoint and 40/40 formal series remain historical; no Player was rerun and no historical receipt was changed. Earlier runtime evidence remains `ReusedAuditedFromFF3D`, earlier Unity EditMode 1,076/1,076 remains `ReusedAuditedFromD18`, and source-27df formal execution remains historical. None is relabelled as fresh current-source execution.

Primary must publish a coherent test-fixture correction and source/compatibility handoff. After it is pushed, Local must restart V00.R/V00, rerun the full Python suite, then perform complete live historical reauthentication, historical compatibility preflight, corrected analysis, checkpoint authentication, V05, and genuinely independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23/24, source-pin mismatch

### Exit

**Local Validation → Primary Implementation: FAIL at V00 source authority.**

The latest pushed handoff was read at demo checkout HEAD `d7854b16c09b02d4494d28c2b0ea015ba83f58a3`, branch `codex/assembly-shadow-r01b-h1`, path `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`. Its declared analysis source/tool anchor is `7aa6f61994da354b04464e38ddfc8552cc5c3055`. All four validation worktrees are on the handoff branch, clean, and match the pushed remote heads. Their exact paths, commits, remotes, worktree registrations, package references, source pins, submodule inventories, and host versions are in the new checkpoint's `V00/repository-preflight.json`.

| Repository | Validation checkout | Pushed commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `d7854b16c09b02d4494d28c2b0ea015ba83f58a3` before this report commit |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

Native, package, and IL2CPP pins equal those three repository commits. `Packages/manifest.json` resolves the HybridCLR Unity package to this validation workspace. No new build GUID or Player artifact was generated. The completed formal evidence remains bound to execution source `27df1a3d60811dc121f296ab561ae313a382b363` and retained graph source `69130bbb3a6df516916dddb5ad263799a7c6e5e3`; its four fixed live evidence hashes are recorded in `V02/historical-live-four-hashes.json`.

The current `h1_handoff_preflight.py --project <candidate> --role candidate --output <new V00 output>` returned exit 1: `Blocked: Demo HEAD contains build-input changes after the source pin`. The exact nine non-metadata changes from `7aa6f619` to `d7854b1` are the three `.agents/skills/agent-collaboration` files and six `.codex/agents` profiles. The source verifier compares the complete non-metadata Git tree at the pin to HEAD, so the migration commit `d7854b1` invalidated the pinned checkout. The source-to-source five-path analysis delta and 24-path retained-graph delta remain exact, but they do not authenticate this later HEAD.

### Results

| Cell | State | Evidence and limit |
| --- | --- | --- |
| V00 repository/branch/remote/native/package pins | `Passed` | `V00/repository-preflight.json`; clean worktrees and exact remote heads before report commit |
| V00 current committed handoff/source preflight | `Failed` | `V00/preflight.json`; source pin rejected before output receipt |
| V01 exact source-to-source audits | `PassedForAnchorsOnly` | `V01A/source-audits.json`: 27df→7aa exact five; 6913→7aa exact 24; 7aa→HEAD has nine non-metadata files |
| V02 historical checkpoint manifest | `PassedHistoricalIntegrityOnly` | 92/92 manifest entries verified in `V02/historical-checkpoint-manifest.log` |
| V02 four fixed live evidence hashes | `PassedHistoricalIntegrityOnly` | Bridge, seal, batch, and final sample hash-identical at original live paths; no full live graph reauthentication this cycle |
| V00 bounded Primary / complete Python discovery | `Blocked / NotRun` | Source preflight prerequisite failed |
| V04 historical compatibility and corrected analysis | `Blocked / NotRun` | Source-authority prerequisite failed; no analysis result claimed |
| V04 new checkpoint / V05 / independent M08 | `Blocked / NotRun` | No authenticated current analysis checkout |
| Unity, IL2CPP, native builds, Players, profiler | `NotRun` | Current handoff specifies analysis-only validation; no new execution evidence |

The fresh run used Python 3.14.6, PowerShell 7.6.3, and Git 2.50.1 on macOS arm64. The handoff specifies Unity 2022.3.62f2 / StandaloneOSX / arm64; Unity was not invoked. The preflight command, UTC start/end, exit code, stdout/stderr, Git inventories, full path lists, hashes, and manifest log are in `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260924-authority7aa6-source-pin-blocked/`. That checkpoint is the evidence for this return and references the immutable 27df execution checkpoint. Historical runtime, EditMode, pilot, and formal results remain historical and are not promoted to current-source PASS.

Primary must restore a coherent pushed handoff source identity while preserving the completed 40/40 formal series and the source verifier's fail-closed guarantee. `RETURN_TO_WEB.md` gives the reproduction and implementation boundary. After a new pushed handoff, Local must restart V00 and run V01, historical compatibility, corrected analysis, checkpoint, V05, and independent M08 in order. H1 remains `InProgress`; historical independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 is closed.

## Historical run — 2026-09-23 authority `27df1a3d`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after 40/40 formal pairs**

Fresh V00 authenticated candidate checkout `f5e34235641c212c715aef3405925ddd4cf28ee6` and exact source/tool anchor `27df1a3d60811dc121f296ab561ae313a382b363`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the protected profile-1 family, and both installed runtimes passed. The candidate installed-runtime receipt was refreshed through the sanctioned `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` path, then passed strict verification.

Fresh bounded Primary validation passed 368/368. The focused suite passed 126/126, both requested PowerShell recovery suites passed, and full Python discovery completed 1,053 leaves: 1,025 Passed, 28 explicit environment-bound Skipped, zero failures, and zero errors. The exact source audits passed: `91ac4db3... → 27df1a3d...` contains the required 3 non-metadata paths and `69130bbb... → 27df1a3d...` contains the required 22 paths, with no forbidden runtime or producer delta. Historical Unity 1,076/1,076 remains only `ReusedAuditedFromD18`, not fresh current-source execution.

The retained V04 manifests, build map, protocol, schedule, pilot index, five pilot attempts, four selected pilots, and eight selected launch receipts reauthenticated. Independent hashing verified 33,792 bound files totaling 1,606,993,133 bytes with zero content mismatches.

A new `H1GraphReuseBridge` passed as `AuthenticatedToolOnlySuccessor` with SHA-256 `c03665dbdba797f5024fa8f376e6ac6aa6edf165c76387ddbf01ee6d3611826c`. It binds the exact retained runner SHA-256 `afc0b649579ebd497be493be9fd39fcfe19e3ba3074d6d6679e009975d21a07c` and current runner SHA-256 `a8de4dc1052306923f7aef529442d4c2012cc959c5dea58da6f15785caacd280`.

The retained-pilot admission preflight passed with five retained attempts, four selected pilots, exact historical runner bindings, and no deep reconstruction. Its SHA-256 is `cbfc6faf8512a214ff97fa939bc6335b05a36362d66b539ff22e954c61529ed1`.

The new guard-v2 strict seal passed with `guardKind=CrossRemountStableStatGuard`, `guardVersion=2`, guard fields exactly `[inode, mode, size, mtimeNs, ctimeNs]`, no device field, `deepLaunchVerificationCount=8`, and 33,792 sealed files. Its SHA-256 is `bdc4062acfc6d208a9be50a142b897a07e7359e5df14ad3d3d8f2805c5179631`.

A wholly new formal series started from the retained pilot index, without chaining either historical failed series. The batch runner automatically used path-hash namespace suffix `7cafb9c53434`, so pair 1 did not collide with preserved project-local outputs. Pair 1 proved protected A had no formal launch authority, while candidate B received and consumed a valid current `H1FormalSideLaunchAuthority`, passed retained graph preparation, launched the Player, and emitted an R00 receipt echoing the same authority, bridge, seal, and build map.

All 40 formal pairs passed on their first protocol attempt: 10/10 OFF-NoPatch, 10/10 ON-NoPatch, 10/10 ON-P01, and 10/10 ON-P03. No whole-pair retry was required. The batch receipt is `PassedAllFormalPairs`, SHA-256 `97ddb6c8c90c3bc6ae15a39813a7fa55d75a0a9c4db089a44ff036018ffd3667`; the final cumulative index SHA-256 is `a8e519c355364e96fa2ed8d808ad54e8053d8479b11bc54c2f8dae603d8cd021`.

The bridge-aware strict analyzer completed after reconstructing the cumulative chain, but returned `Incomplete` / `ComparabilityIncomplete`. Build-map comparability and chronology passed. Of 45 cumulative attempts, 44 were rejected by the same receipt-shape check:

`R00 raw build field differs: baselineBuildId`

The raw R00 top-level `baselineBuildId` and `runtimeAbiHash` are correct and match the frozen build. The nested raw `playerBuildReceipt` correctly binds its path, SHA-256, and build GUID, but omits `baselineBuildId` and `runtimeAbiHash`. The final analyzer requires those fields inside the nested receipt. The omission is identical across protected/candidate and the 44 otherwise analyzable pilot/formal attempts. The remaining cumulative attempt is the already-preserved historical `R00-ON-NoPatch-pilot-01` failure: its A-side runner process group could not be proven gone, so B was skipped. Local reproduced the receipt-shape failure through the analyzer's isolated build-binding check and retained a machine-readable diagnosis. This is a source/tool contract failure, not a formal pair failure; retrying current formal pairs would reproduce the same immutable receipt shape.

Local did not modify the producer, analyzer, `WEB_TO_LOCAL.md`, or any source/tool contract; did not relabel the formal evidence; did not enter V05/M08; and did not begin R02.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Checkout `f5e34235...`; exact `SourceTargetVerifiedNotBuildAccepted` for `27df1a3d...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling on its actual branch worktree; protected profile-1 family exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate receipt SHA `4d8afaea...`; protected receipt SHA `54bfe84c...` |
| V01 bounded Primary | `Passed` | 368/368 |
| V01 focused validation | `Passed` | 126/126 plus both PowerShell recovery suites |
| V01 Python inventory | `CompletedWithExplainedEnvironmentSkips` | 1,053 total; 1,025 Passed; 28 environment Skipped; 0 failures/errors |
| V01 Unity EditMode | `ReusedAuditedFromD18` | Historical 1,076/1,076 only after exact source audit; not fresh execution |
| V01A source audits | `PassedExactSets` | Exact 3-path and 22-path non-metadata sets |
| V02 retained evidence | `PassedRetainedEvidenceReauthentication` | 33,792 files / 1,606,993,133 bytes / zero mismatches |
| V04 graph bridge | `Passed` | New bridge SHA `c03665db...`; retained runner SHA `afc0b649...` exact |
| V04 retained-pilot admission | `Passed` | 5 attempts; 4 selected; exact historical runner; no deep reconstruction |
| V04 guard-v2 pilot seal | `Passed` | Stable stat guard exact; no device; 8/8 deep sides; SHA `bdc4062a...` |
| V04 formal pair 1 authority | `Passed` | A has no authority; current B authority consumed; real Player launch; receipt echo exact |
| V04 formal series | `PassedAllFormalPairs` | 40/40 first-attempt passes; 10 per mode; zero retries |
| V04 final analysis | `Incomplete` | `ComparabilityIncomplete`; 0 valid / 45 invalid: 44 nested-receipt schema mismatches plus 1 preserved historical pilot process-cleanup failure |
| V05 / independent M08 | `Ineligible / NotRun` | Mandatory V04 final analysis did not pass |

### Root cause and required Primary correction

The Player-side R00 producer and strict final analyzer disagree about the nested raw build-receipt schema. The producer places `baselineBuildId` and `runtimeAbiHash` at R00 top level but not inside `playerBuildReceipt`; the analyzer requires the same values inside `playerBuildReceipt`. The design allowed the mismatch because launch-time and cached-admission verification authenticated path/hash/build-GUID and top-level authority, while the final analyzer applied a stricter nested-field contract only after the complete series.

Primary must reconcile this contract and add fail-closed coverage. The durable choices are to make the producer echo both fields into the nested receipt, or to deliberately revise the analyzer to bind the authenticated top-level fields instead. Primary must also decide, based on the corrected contract and immutability rules, whether these 40/40 raw attempts may be reanalyzed or whether a new formal series is required. Local must not make that semantic decision.

### Retention checkpoint

The authenticated checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260923-authority27df-formal-analysis-blocked/`. It contains current authority/tests/audits, retained evidence authentication, the new bridge/admission/guard-v2 seal, all 40 cumulative sample indexes, the batch receipt, strict analyzer output and logs, the contract-failure diagnosis, prior checkpoint manifest links, handoff snapshots, raw evidence, all referenced formal side evidence, and a SHA-256 manifest. The large side-evidence archive is split into ordered parts for Git transport; concatenating the parts reconstructs aggregate SHA-256 `fda8226ee124ecc7d6687e2bbbab30d2166c838fd5fc7225b9972d949982f75f`.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
