# HybridCLR Assembly Shadow

Plan holds normative design/stages/Human Review Gates. Handoff holds the current assignment and separately owned Local factual reports. History preserves original evidence and bounded Primary/independent assessments.

## Current state — F-COMP blocked; fixture repaired; G-COMP compilation only

**Next assignment: one fresh G-COMP official managed/native SDK compilation, conditional on all prerequisites. No Unity process, Player build, Player or runtime batch is authorized.** F-COMP was consumed and returned **PrerequisiteBlocked**; do not retry F-COMP or reuse its roots. E remains **FAIL**, and all acceptance flags remain false.

F-COMP at demo `c5662700452ebc4769b376303e1b812cb42ccc72` ran ten scratch tests once: **3 Passed / 5 failures / 2 errors**. Its test fixture derived noncanonical `/var/folders` paths; the production validator correctly rejected the `/private/var` resolution mismatch. All downstream host/compiler work and all 55 native configurations were **NotRun**. Before-custody admission was NotRun. A separate after audit verified 339,367 survivors and 77,477 unchanged missing identities, zero problems; installed SDK preservation verified 2,113 files unchanged. Strict custody remained Blocked. Zero Unity/Player launches. Local publication `a9483a6e2212701cfedcf93faeb0e71ce82b73ca` is immutable.

Primary fixed only `Tools/AssemblyShadow/R03/test_native_validation_scratch.py`: resolve the owned temporary fixture root before deriving paths, and inherit all ten original controls in a second cohort with a guaranteed symlink-backed temporary parent. No TMPDIR/global-temp workaround, skipped control, production validator change or runtime change. [CI 38123748124](https://github.com/night-outlook/hybridclr_demo/actions/runs/38123748124) passed **20/20 tests on macOS and 20/20 on Ubuntu**, with authentic source/log/archive bindings. This closes the fixture defect at host-test level, not the outstanding Local compiler/runtime evidence.

## Read first

1. [Current status](Plan/CURRENT_STATUS.md), [G-COMP WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md), Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md).
2. [IR-LOCAL-COMPILE-01 correction](History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/README.md), [CI evidence and raw log references](History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/CI_EVIDENCE.json), [G-COMP exact procedure](History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/G_COMPILE_ONLY_PROCEDURE.md).
3. Immutable [F-COMP blocked checkpoint](History/M07R/R03/local-validation-20261010-ir-r03-02-f-compile-only/README.md), [E failed checkpoint](History/M07R/R03/local-validation-20261010-ir-r03-02-e-native-receipt/README.md), [C custody failure](History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked/README.md), [original scoped-loss disposition](History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/README.md).
4. [Runtime correction background](History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/PRIMARY_RECONCILIATION.md), original R03 design/plans/HUMAN_REVIEW_GATES, [independent full-stage FAIL](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) and [C04 erratum](History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md).

## Source and next boundary

All repositories use `codex/assembly-shadow-r01b-h1`. Fixed pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, native `c386cdd1e8942561f1d1e1fada52d21ca524f174`. Demo test source is `e36ab83b969f8ba8f9f4cc21fc8bb6c447d7fa2f`; final publication adds only Docs/AssemblyShadow changes. Use the exact latest pushed demo SHA in the final Primary prompt, not an older source/evidence anchor. Source-pins.json, native_validation.py, build_api.py, Player/native sources, fixtures, custody/storage guards and Local-owned reports were not changed by this repair.

G-COMP uses new `20261011G-canonical-temp` roots, freshly runs 20 scratch tests and prescribed native host checks, authenticates the installed official Unity 2022.3.62f2 SDK and original-C custody, then conditionally invokes the existing managed compiler script and 55-configuration native syntax matrix once. SDK copies remain in the explicit external scratch. Verify custody and installed SDK afterwards, publish actual evidence and return to Primary. No retry or runtime advancement follows compile success.

## Unchanged history and acceptance

E remains 11 Passed / 3 Failed of 14 cells; three native builds Passed, OFF Passed, three ON SIGSEGV. Required ON raw/semantic proofs and original triggering error remain Unavailable. Native reporting remediation remains runtime-unverified. The host fixture pass does not close IR-LOCAL-RUNTIME-01.

Strict historical S custody is **Blocked**: original map 416,844 entries, 339,367 survivors and 77,477 Missing; four historical installed native roots remain Missing. `ScopedHistoricalLossStable` is only a bounded classification for new independent evidence and never restores original source/build/process provenance. No rebaseline, restoration, cleanup or reclassification of S/R/Q/P/O/N/A/B/C/D/E/F.

Historical S remains 90 Passed / EvidenceReadyForPrimaryReview, not full-stage acceptance. Its original nine-part 587,907,380-byte archive SHA-256 is `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, 15,712 indexed files. Original S native revision `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` is not the current candidate. R staged/original restoration Failed; contaminated warm certificates Failed; deferred CPU/RSS risks unaccepted. D1=A/D2=A decisions are unchanged.

Independent full-stage R03 review **FAIL**, re-review **NotRun**. IR-R03-01, captured-generic/initializer and real engine-originated reporting coverage remain outstanding. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2/X02/M08A or automatic Human Review Gate approval.
