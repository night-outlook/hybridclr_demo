# R01 Stage Report

Status: **Active / Unaccepted**. This is the current v5 stage report draft. It does not pass R01, R01B, H1, or authorize R02.

The executable pairing under review is Unity 2022.3.62f2, StandaloneOSX arm64:

- `hybridclr`: `b22fa3d92223645c32663e4a2157eaadf8ea495e`
- `hybridclr_unity`: `b649c499385ea68490a0f652a98b732e060aeb89`
- `il2cpp_plus`: `7967b8c7043904fcae130b294defd5ce7aa897c4`
- `hybridclr_demo`: `c2c908c5a11ce65aabb0da75b512923f709277c1`
- runtime ABI: `46814a65339ab321eb2c35ac2b8edd9ff180ce60039a13d650d4bf3f4f3bcc00`

The exhaustive cumulative source list is [source-change-index-v5.json](source-change-index-v5.json:1). It records 143 demo files, 11 HybridCLR files, 31 `hybridclr_unity` files, and 12 `il2cpp_plus` files changed from accepted R00. The current v5 installation check records 945 source files, 947 installed files, `demoSourceVerified=true`, and receipt SHA-256 `32d9d71093c2aeef028bd9fd48088c2bf9b837493eb07453d2d989a5488ee045` (`_temp/AssemblyShadow/R01/early-v5-installed-verification-1.json`). The v5 pair checkpoint records workflow and deterministic replay as Passed for `M07-Baseline-R01-early-v5`, with ON build GUID `a5b484a6772e4c90a24dd29216022630`, OFF build GUID `cdfb323305354110b7f5848524a3a7e2`, and native UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B` ([early-v5-player-build-pair-checkpoint.json](early-v5-player-build-pair-checkpoint.json:1)). The full 11-mode early preflight is running; this report does not treat it as Player acceptance until its strict result is recorded.

The normative contract requires native budget boundaries, a real multi-assembly Player capacity rejection before publication, shared ordinary/Shadow consumption, strict failure and recovery behavior, version-bound evidence, and explicit NotRun limits ([R01 plan](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01-metadata-budget-and-failure-contract.md:44)). The validation matrix assigns Q01/Q02/Q05 to native boundaries, Q03/Q04 to native plus Player, Q06 to Player and R01B, and S01-S04 to their stated policy/native/Player boundaries ([validation matrix](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md:9)).

## Evidence state

The v5 source-correction review is independently bounded and passed. Three native files were corrected for the metadata error-construction guard and inner initializer failure detail. Its native receipt has 131 checks, 22 new checks, 1,069 source inputs, and `inputsUnchanged=true`; its scope is explicitly native staging/error formatting, not R01 acceptance ([early-v5-source-correction-review.json](early-v5-source-correction-review.json:30)).

The authoritative v5 native scope now has nine fresh hash-bound suites: M03 `94,707/30/25/15/33` identity/name/facade/lookup/OFF checks; M04 `53` checks with 15 reference-identity checks, 22 syntax checks, one million lookups, zero lookup allocations, and 373,503 microseconds; M05 `616` core, 35 reflection, 219 identity, and 34 syntax checks; M06 `824` and 20 syntax checks; startup `168`; allocator contention `545`; transaction `131`; budget `2,684`; and recovery `498`. The retained gateway has all nine inputs matching and remains explicitly retained execution. These results pass only their native or adapter boundaries ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)); its helper compiler binder preserves the original missing-compiler-hash and direct-backend-SDK failed attempts rather than treating them as passes.

The v5 ON/OFF pair, fixture lifetime, and deterministic replay passed. The v4 early Player diagnostic matrix passed 9 of 11 strict modes; MetadataFailure returned the wrong terminal result and InitializerFailure lost the expected terminal reason ([early-v4-matrix-diagnostic.json](early-v4-matrix-diagnostic.json:220)). Those are historical v4 observations; the current v5 early Player result remains pending.

The v5 Editor and fixture-lifetime check passed the five-member fixture/replay, retained 379 sealed files unchanged after a real subsequent compile, and rejected an exactly 64 MiB padded assembly with `MetadataCapacityExceeded` before rejected output ([early-v5-editor-validation.json](early-v5-editor-validation.json:1)). This is Editor/capacity evidence, not a 65,536-assembly product claim.

The v4 NativeScript trace is a bounded historical witness: PID 36383 naturally exited, five direct public IL2CPP API events were captured, `class_from_name` returned a non-null class, and the return preceded Configure ([early-v4-native-script-trace.json](early-v4-native-script-trace.json:1)). The fresh v5 ON debug capture is now paired to build GUID `a5b484a6772e4c90a24dd29216022630` and native UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B` (`_temp/AssemblyShadow/R01/early-v5-on-native-wrappers/native-debug-artifacts.json`); its actual trace is pending.

Python and Editor receipts outside the v5 records remain historical evidence. The v5 M03-M06 suites are fresh native evidence, but their adapters and stated limits remain material. Native adapters, including Q05 production allocator/`g_MetadataLock` contention, do not establish full Unity startup, managed publication, or concurrent Player Configure behavior.

## R01 matrix

| Criterion | Current evidence | Current disposition |
|---|---|---|
| Q01 budget boundaries | Fresh v5 production-header helper passes 2,684 checks; recovery helper passes 498 checks | Native boundary is complete; retain helper compiler binding and its failed-attempt history explicitly |
| Q02 fresh capacity | Fresh v5 budget suite, v5 Editor positive five-member fixture, and exact 64 MiB rejection are recorded | Bind a real current-pair Player rejection before publication; do not infer the product target from the Editor case |
| Q03 ordinary plus Shadow allocation | v4 early Control, OrdinaryFirst, and OrdinaryAfterReserve strict-passed; current v5 Player binding is pending | Complete the v5 strict early evidence and compare ordinary consumption with Shadow reservation |
| Q04 staged metadata failure | v4 MetadataFailure failed strict verification; v5 native error construction is fixed and reviewed | Fresh v5 Player receipt must show the actual failure state, retained budget, no publication, and required recovery disposition |
| Q05 mixed-size/ordinary contention | Fresh v5 production allocator and `g_MetadataLock` contention suite passes 545 checks | Native-only boundary is complete; it is not concurrent Player `Assembly.Load` or Configure evidence |
| Q06 project target | Five-member Editor positive and 64 MiB pre-publication rejection are recorded | User target 65,536 requires R01B. Allocation domain, DLL distribution, and headroom are unresolved; no 64K support claim is made |
| S01 pre-Configure use | v4 early negative modes and bounded NativeScript witness exist; fresh v5 ON debug capture is prepared, actual trace pending | Complete strict current-pair early modes and bind policy, process exit, state assertions, and the v5 NativeScript trace |
| S02 correctable Stage rejection | The v4 R01 Mismatch mode is the actual Player Stage rejection path; its strict contract is in `Tools/AssemblyShadow/r01_early_results.py` | Bind this path in the final v5 aggregate. No additional concurrent Configure matrix is required by S02. Exact-set/duplicate/retry semantics are retained M03 evidence and need current reruns only if the affected-regression gate requires them |
| S03 metadata failure recovery | Fresh v5 transaction suite passes 131 bounded native checks; Player failure/recovery receipt is not yet bound | Capture the real staged failure, state/disposition, and no-false-Abort behavior in a fresh Player |
| S04 publication/failure observation | Fresh v5 startup suite passes 168 bounded checks; Player publication/failure snapshots are not yet bound | Bind complete current-pair before/after publication and failure snapshots, with sampling limits explicit |

The final Player scope is the 11 early modes plus 13 M07 ON resource modes and OFF. A build/replay or source review does not substitute for those strict receipts. M07 modes are not marked Passed in this report until the current v5 aggregate is produced and source-bound.

## Remaining R01 work

1. Finish the v5 build and install/generation provenance, then produce the current-pair strict 11-mode early result and the 14-mode M07 aggregate (13 ON plus OFF).
2. Re-run or bind the corrected MetadataFailure and InitializerFailure Player receipts. The v4 failures cannot be carried forward as acceptance; the v5 native correction alone does not prove the Player boundary.
3. Bind the NativeScript LLDB witness to the v5 executable, native UUID, input capsule, PID/TID, five API events, non-null class return, and ordering before Configure.
4. Record the completed v5 native scope and helper compiler binding in the final evidence index, then complete the post-build installed/generated binding audit. Keep non-v5 Python/Editor results labeled by their historical pairing.
5. Consolidate source, compiler, runtime, input, binary, process, log, and assertion hashes in the final evidence index, then obtain the required independent R01 code review. This review is distinct from the human H1 review after R01B.

R01B is mandatory for the approved 65,536 target after R01. The ordered path is R01, R01B, then stop at H1. H1 remains false and R02 is prohibited ([current status](../current-status.json:14), [approved amendment](approved-early-activation-amendment.md:7), [human gates](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md:33)). An independent R01 code review may be performed by an independent agent reviewer; the human H1 review remains mandatory after R01B and cannot be replaced by agent review.

This report remains incomplete until the current v5 Player receipts, NativeScript binding, affected native evidence, final evidence index, and independent R01 code review are complete. Historical evidence files are preserved and are not rewritten by this report. The human H1 review occurs only after required R01B completion.
