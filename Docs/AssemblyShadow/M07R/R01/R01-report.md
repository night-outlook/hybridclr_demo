# R01 Stage Report

Status: **Active / Unaccepted**. This is the current v6 stage report draft. It does not pass R01, R01B, H1, or authorize R02.

The executable pairing under review is Unity 2022.3.62f2, StandaloneOSX arm64:

- `hybridclr`: `b22fa3d92223645c32663e4a2157eaadf8ea495e`
- `hybridclr_unity`: `b649c499385ea68490a0f652a98b732e060aeb89`
- `il2cpp_plus`: `7967b8c7043904fcae130b294defd5ce7aa897c4`
- `hybridclr_demo`: `cc7b17683c2e68a162914c347bb81d765dbc26c0`
- runtime ABI: `46814a65339ab321eb2c35ac2b8edd9ff180ce60039a13d650d4bf3f4f3bcc00`

The cumulative v6 source index is [source-change-index-v6.json](source-change-index-v6.json:1); the v5 index remains retained historical evidence ([source-change-index-v5.json](source-change-index-v5.json:1)). The v6 verifier correction changes only `Tools/AssemblyShadow/r01_early_results.py` and its tests; native and managed runtime source are unchanged ([early-v6-verifier-correction-review.json](early-v6-verifier-correction-review.json:35)). The v6 baseline is `M07-Baseline-R01-early-v6`; fresh installation/build pairing is pending in `_temp/AssemblyShadow/R01/early-v6-build-driver-1.log` and `_temp/AssemblyShadow/R01/early-v6-build-1.log`.

The normative contract requires native budget boundaries, a real multi-assembly Player capacity rejection before publication, shared ordinary/Shadow consumption, strict failure and recovery behavior, version-bound evidence, and explicit NotRun limits ([R01 plan](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01-metadata-budget-and-failure-contract.md:44)). The validation matrix assigns Q01/Q02/Q05 to native boundaries, Q03/Q04 to native plus Player, Q06 to Player and R01B, and S01-S04 to their stated policy/native/Player boundaries ([validation matrix](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/validation-matrix.md:9)).

## Evidence state

The v5 native source-correction review and nine native suites are retained historical evidence for the unchanged native pins. They remain bounded native/adapter results and are not v6 runtime acceptance ([early-v5-native-regressions.json](early-v5-native-regressions.json:1)).

The retained v5 native scope records nine passing suites: M03 `94,707/30/25/15/33`, M04 `53` with one million lookups and zero allocations, M05 `616/35/219/34`, M06 `824/20`, startup `168`, contention `545`, transaction `131`, budget `2,684`, and recovery `498`. These are historical relative to v6; the retained gateway and helper compiler failed attempts remain explicitly labeled. Native and adapter limits still apply.

The v5 ON/OFF pair, fixture lifetime, deterministic replay, and 11-mode result are retained historical evidence. Its strict verdict is `PassedBoundedProfile`, with independent early-runtime review passed; it is diagnostic-only and does not bind the v6 source pin or accept R01 ([early-v5-strict-matrix.json](early-v5-strict-matrix.json:1), [early-v5-stage-source-review.json](early-v5-stage-source-review.json:1)). The v6 strict early matrix and runtime claims remain pending.

The v5 Editor and fixture-lifetime result is retained historical evidence: five-member fixture/replay, 379 sealed files unchanged after subsequent compile, and exact 64 MiB pre-publication rejection. Fresh v6 Editor fixture/replay/lifetime/capacity evidence remains pending; no 65,536-assembly product claim is made.

The retained v5 NativeScript trace passed its bounded witness: PID 47101/TID 15077444, seven ordered events, expected UUID `6F75EA76-5544-4D01-9414-D8004DD46D1B`, non-null `class_from_name` before Configure, and natural exit 1 ([early-v5-native-script-trace.json](early-v5-native-script-trace.json:1)). It is historical relative to v6; a fresh v6 trace and source-pair binding remain pending.

The v6 verifier correction review passed with no findings in its bounded source scope, and the full Python suite passed 443 tests with zero skips in 63.044 seconds ([early-v6-verifier-correction-review.json](early-v6-verifier-correction-review.json:1), [early-v6-python-validation.json](early-v6-python-validation.json:1)). The supplemental v5 P01 Player process (PID 47561) passed its native/managed raw checks and exited 0, but its original strict producer failed because it incorrectly required globally empty candidate first-use history ([early-v5-p01-diagnostic.json](early-v5-p01-diagnostic.json:35)). Native and source experts confirmed the observed selected `Internal` use and unchanged `Extensibility` sequence 1 / `Contracts` sequence 2 are legitimate nonclosure AOT dependency uses, consistent with the M07 boundary ([M07-report.md](../../M07/M07-report.md:78)). The v6 correction changes only verifier/tests; it does not retroactively accept that failed receipt. First-use history is not continuous user-code exclusion evidence; staging guard source and native guard tests establish that separate boundary. Native adapters do not establish full Unity startup, managed publication, or Player acceptance.

## R01 matrix

| Criterion | Current evidence | Current disposition |
|---|---|---|
| Q01 budget boundaries | v5 helper receipts pass 2,684 budget and 498 recovery checks, retained from unchanged native pins | Historical native boundary is retained; v6 unchanged-input audit and final binding remain pending |
| Q02 fresh capacity | v5 native/Editor capacity evidence is retained; fresh v6 fixture and Player binding are pending | Complete v6 current-pair pre-publication rejection; do not infer the product target from the Editor case |
| Q03 ordinary plus Shadow allocation | v5 bounded profile is historical; v6 source-pair Player evidence is pending | Bind fresh v6 ordinary and Shadow consumption in the strict result |
| Q04 staged metadata failure | v5 PID 47041 is historical evidence of Validate 13 and RestartRequired; v6 failure fixture/Player binding is pending | Capture and bind the v6 failure state and recovery disposition |
| Q05 mixed-size/ordinary contention | Retained v5 production allocator and `g_MetadataLock` contention suite passes 545 checks | Native-only boundary is historical relative to v6; unchanged-native-input audit and final binding remain pending, and it is not concurrent Player `Assembly.Load` or Configure evidence |
| Q06 project target | Retained v5 five-member Editor positive and 64 MiB pre-publication rejection are recorded | User target 65,536 requires R01B. Allocation domain, DLL distribution, and headroom are unresolved; no 64K support claim is made |
| S01 pre-Configure use | v5 launcher and NativeScript evidence are historical; v6 trace and strict runtime evidence are pending | Complete v6 strict early verification and NativeScript binding |
| S02 correctable Stage rejection | The v4 R01 Mismatch mode is the actual Player Stage rejection path; its strict contract is in `Tools/AssemblyShadow/r01_early_results.py` | Bind this path in the final v6 aggregate. No additional concurrent Configure matrix is required by S02. Exact-set/duplicate/retry semantics are retained M03 evidence and need current reruns only if the affected-regression gate requires them |
| S03 metadata failure recovery | v5 receipts capture the required failure dispositions but are historical relative to v6 | Bind fresh v6 failure receipts and preserve separate pre/post-publication boundaries |
| S04 publication/failure observation | Retained v5 startup suite passes 168 bounded checks; Player publication/failure snapshots are not yet bound | Bind complete current-pair before/after publication and failure snapshots, with sampling limits explicit |

The final v6 Player scope is the 11 early modes plus 13 M07 ON resource modes and OFF. The v5 bounded profile is retained historical evidence; v6 strict offline verification and the M07 aggregate remain pending.

## Remaining R01 work

1. Complete the fresh v6 installation/build pairing, strict 11-mode early verifier, and 14-mode M07 aggregate (13 ON plus OFF).
2. Capture and bind fresh v6 MetadataFailure and InitializerFailure receipts; retain v5 receipts as historical evidence with their limits.
3. Capture and bind the fresh v6 NativeScript LLDB witness; the v5 seven-event witness remains historical.
4. Complete the v6 unchanged-native-input audit and final evidence-package binding. Record the v6 verifier correction and 443-test Python review separately from runtime evidence.
5. Consolidate source, compiler, runtime, input, binary, process, log, and assertion hashes in the final evidence index, then obtain the required independent R01 code review. This review is distinct from the human H1 review after R01B.

R01B is mandatory for the approved 65,536 target after R01. The ordered path is R01, R01B, then stop at H1. H1 remains false and R02 is prohibited ([current status](../current-status.json:14), [approved amendment](approved-early-activation-amendment.md:7), [human gates](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/HUMAN_REVIEW_GATES.md:33)). An independent R01 code review may be performed by an independent agent reviewer; the human H1 review remains mandatory after R01B and cannot be replaced by agent review.

This report remains incomplete until fresh v6 installation/build provenance, strict 11-mode verdict, 14-mode M07 aggregate, fresh Editor fixture/replay/lifetime/capacity evidence, NativeScript trace, unchanged-native-input audit, final evidence package/review, and independent R01 code-review decision are complete. v5 evidence is preserved as historical with explicit limits. The human H1 review occurs only after required R01B completion.
