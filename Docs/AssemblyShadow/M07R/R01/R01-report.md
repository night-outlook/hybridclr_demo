# R01 Stage Report

Status: **Active / Unaccepted**. This is the current v5 stage report draft. It does not pass R01, R01B, H1, or authorize R02.

The executable pairing under review is Unity 2022.3.62f2, StandaloneOSX arm64:

- `hybridclr`: `b22fa3d92223645c32663e4a2157eaadf8ea495e`
- `hybridclr_unity`: `b649c499385ea68490a0f652a98b732e060aeb89`
- `il2cpp_plus`: `7967b8c7043904fcae130b294defd5ce7aa897c4`
- `hybridclr_demo`: `c2c908c5a11ce65aabb0da75b512923f709277c1`
- runtime ABI: `46814a65339ab321eb2c35ac2b8edd9ff180ce60039a13d650d4bf3f4f3bcc00`

The exhaustive cumulative source list is [source-change-index-v5.json](source-change-index-v5.json:1). It records 143 demo files, 11 HybridCLR files, 31 `hybridclr_unity` files, and 12 `il2cpp_plus` files changed from accepted R00. The current v5 installation check records 945 source files, 947 installed files, `demoSourceVerified=true`, and receipt SHA-256 `32d9d71093c2aeef028bd9fd48088c2bf9b837493eb07453d2d989a5488ee045` (`_temp/AssemblyShadow/R01/early-v5-installed-verification-1.json`). The v5 pair checkpoint records workflow and deterministic replay as Passed for `M07-Baseline-R01-early-v5`, with ON build GUID `a5b484a6772e4c90a24dd29216022630`, OFF build GUID `cdfb323305354110b7f5848524a3a7e2`, and native UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B` ([early-v5-player-build-pair-checkpoint.json](early-v5-player-build-pair-checkpoint.json:1)). All 11 early Player launcher rows now pass; the strict offline verifier is still running, so the runtime aggregate remains pending.

The normative contract requires native budget boundaries, a real multi-assembly Player capacity rejection before publication, shared ordinary/Shadow consumption, strict failure and recovery behavior, version-bound evidence, and explicit NotRun limits ([R01 plan](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01-metadata-budget-and-failure-contract.md:44)). The validation matrix assigns Q01/Q02/Q05 to native boundaries, Q03/Q04 to native plus Player, Q06 to Player and R01B, and S01-S04 to their stated policy/native/Player boundaries ([validation matrix](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md:9)).

## Evidence state

The v5 source-correction review is independently bounded and passed. Three native files were corrected for the metadata error-construction guard and inner initializer failure detail. Its native receipt has 131 checks, 22 new checks, 1,069 source inputs, and `inputsUnchanged=true`; its scope is explicitly native staging/error formatting, not R01 acceptance ([early-v5-source-correction-review.json](early-v5-source-correction-review.json:30)).

The authoritative v5 native scope now has nine fresh hash-bound suites: M03 `94,707/30/25/15/33` identity/name/facade/lookup/OFF checks; M04 `53` checks with 15 reference-identity checks, 22 syntax checks, one million lookups, zero lookup allocations, and 373,503 microseconds; M05 `616` core, 35 reflection, 219 identity, and 34 syntax checks; M06 `824` and 20 syntax checks; startup `168`; allocator contention `545`; transaction `131`; budget `2,684`; and recovery `498`. The retained gateway has all nine inputs matching and remains explicitly retained execution. These results pass only their native or adapter boundaries ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)); its helper compiler binder preserves the original missing-compiler-hash and direct-backend-SDK failed attempts rather than treating them as passes.

The v5 ON/OFF pair, fixture lifetime, and deterministic replay passed. All 11 v5 early Player launcher rows now pass, while the strict offline verifier remains pending. The v5 MetadataFailure receipt (PID 47041) records Validate error 13, `Failed`, unpublished state, `abortAllowed=false`, and `restartRequired`; its terminal reason is `AssemblyA.Contracts: Image::ReadType invalid type`. The v5 InitializerFailure receipt (PID 47045) records Commit error 19, `FailedAfterCommit`, published state, `abortAllowed=false`, and `restartRequired`; its terminal reason retains `R01-INIT-THROW:AssemblyA.Implementation.Extensibility`. The v4 9/11 result and two failures remain historical diagnostic evidence ([early-v4-matrix-diagnostic.json](early-v4-matrix-diagnostic.json:220)); the v5 offline aggregate is not yet accepted.

The v5 Editor and fixture-lifetime check passed the five-member fixture/replay, retained 379 sealed files unchanged after a real subsequent compile, and rejected an exactly 64 MiB padded assembly with `MetadataCapacityExceeded` before rejected output ([early-v5-editor-validation.json](early-v5-editor-validation.json:1)). This is Editor/capacity evidence, not a 65,536-assembly product claim.

The v4 NativeScript trace remains historical. The actual v5 bounded trace passed with PID 47101/TID 15077444, seven ordered events, expected UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B`, non-null `class_from_name` return before Configure, and natural exit 1. The source and pairing review was independently passed ([early-v5-native-script-trace.json](early-v5-native-script-trace.json:1)); this is bounded witness evidence, not whole R01 acceptance.

Python and Editor receipts outside the v5 records remain historical evidence. The v5 M03-M06 suites are fresh native evidence, but their adapters and stated limits remain material. Native adapters, including Q05 production allocator/`g_MetadataLock` contention, do not establish full Unity startup, managed publication, or concurrent Player Configure behavior.

## R01 matrix

| Criterion | Current evidence | Current disposition |
|---|---|---|
| Q01 budget boundaries | Fresh v5 production-header helper passes 2,684 checks; recovery helper passes 498 checks | Native boundary is complete; retain helper compiler binding and its failed-attempt history explicitly |
| Q02 fresh capacity | Fresh v5 budget suite, v5 Editor positive five-member fixture, and exact 64 MiB rejection are recorded | Bind a real current-pair Player rejection before publication; do not infer the product target from the Editor case |
| Q03 ordinary plus Shadow allocation | All v5 early launcher rows pass; strict offline verification remains pending | Bind the v5 strict result and compare ordinary consumption with Shadow reservation |
| Q04 staged metadata failure | v5 PID 47041 records Validate error 13, Failed/unpublished, Abort disallowed, and RestartRequired with the original parser detail | Bind this receipt in the strict offline result and final evidence package; native and Player evidence remain bounded to the stated failure path |
| Q05 mixed-size/ordinary contention | Fresh v5 production allocator and `g_MetadataLock` contention suite passes 545 checks | Native-only boundary is complete; it is not concurrent Player `Assembly.Load` or Configure evidence |
| Q06 project target | Five-member Editor positive and 64 MiB pre-publication rejection are recorded | User target 65,536 requires R01B. Allocation domain, DLL distribution, and headroom are unresolved; no 64K support claim is made |
| S01 pre-Configure use | All v5 launcher rows pass; the independently reviewed v5 NativeScript trace captures the expected API stack and ordering | Complete strict offline verification and final evidence binding |
| S02 correctable Stage rejection | The v4 R01 Mismatch mode is the actual Player Stage rejection path; its strict contract is in `Tools/AssemblyShadow/r01_early_results.py` | Bind this path in the final v5 aggregate. No additional concurrent Configure matrix is required by S02. Exact-set/duplicate/retry semantics are retained M03 evidence and need current reruns only if the affected-regression gate requires them |
| S03 metadata failure recovery | v5 PID 47041 and PID 47045 capture the real failure dispositions: Validate 13 and Commit 19, both RestartRequired with Abort disallowed | Bind both receipts in the strict offline result and final evidence package; preserve their separate pre/post-publication boundaries |
| S04 publication/failure observation | Fresh v5 startup suite passes 168 bounded checks; Player publication/failure snapshots are not yet bound | Bind complete current-pair before/after publication and failure snapshots, with sampling limits explicit |

The final Player scope is the 11 early modes plus 13 M07 ON resource modes and OFF. A build/replay or source review does not substitute for those strict receipts. M07 modes are not marked Passed in this report until the current v5 aggregate is produced and source-bound.

## Remaining R01 work

1. Complete the strict offline verdict for the 11 passing v5 launcher rows, then produce and verify the 14-mode M07 aggregate (13 ON plus OFF).
2. Bind the completed v5 MetadataFailure and InitializerFailure receipts to the strict offline result and final evidence package. The v4 failures remain historical and the v5 native correction remains supporting evidence.
3. Bind the completed v5 NativeScript LLDB witness to the executable, native UUID, capsule, PID/TID, seven events, non-null class return, natural exit, and ordering before Configure.
4. Record the completed v5 native scope, helper compiler binding, and passed post-build audit in the final evidence index. Keep non-v5 Python/Editor results labeled by their historical pairing.
5. Consolidate source, compiler, runtime, input, binary, process, log, and assertion hashes in the final evidence index, then obtain the required independent R01 code review. This review is distinct from the human H1 review after R01B.

R01B is mandatory for the approved 65,536 target after R01. The ordered path is R01, R01B, then stop at H1. H1 remains false and R02 is prohibited ([current status](../current-status.json:14), [approved amendment](approved-early-activation-amendment.md:7), [human gates](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md:33)). An independent R01 code review may be performed by an independent agent reviewer; the human H1 review remains mandatory after R01B and cannot be replaced by agent review.

This report remains incomplete until the strict offline 11-mode verdict, 14-mode M07 aggregate, final evidence package/review, and independent R01 code-review decision are complete. The v5 NativeScript trace, native scope, Editor validation, and post-build audit are complete within their explicit limits. Historical evidence files are preserved and are not rewritten by this report. The human H1 review occurs only after required R01B completion.
