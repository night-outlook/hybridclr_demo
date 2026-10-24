# Primary source review — R03 IR-R03-01 and IR-R03-02

## Method and independent boundaries

This is a **Primary Implementation** source/provenance review, not a separate independent full-stage review. Real code was inspected at fixed native `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` / interpreter `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` / package `948c0e3b4f8891481301770115e8ba4945eea6de`. Current demo source had README/docs-only changes after the original f51d audit source. No new Unity install/Editor/Player, official managed/native SDK compile, runtime instrumentation, or Local agent invocation occurred.

## IR-R03-02 source chain reviewed

- `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` fixed Git blob `57cf47f964a83973df8296955ccf856b105c595f` contains `TerminalMethodDenied` (state + durable failure), early guard in `AssertMethodIsActive` at line1959, second guard at line2036 and `RequireActiveMethod` terminal refusal at line2072/2093.
- `AssemblyShadowTerminalExecution.h` fixed blob `33258986c31b2e6ae3af17b8553030482a83aef7` implements Disabled/OFF exclusion, Failed/FailedAfterCommit/durable failure and narrowly verified diagnostic constructor exception. The header-only native fixture has **69 actual C++ checks**, not actual production Unity compilation.
- `Runtime.cpp` fixed blob `96b914fbeb31c69d649e4076a802de0b6418daa8` uses `RequireActiveMethod` before actual invoker code in `Invoke` and `InvokeWithThrow`, and exact Unity engine terminal-reporting substitution. `hybridclr/interpreter/Interpreter_Execute.cpp` fixed blob `2dbdb7527afee7f2546e45f20e6ef93e1bca237a` guards entry, nested, delegate/virtual and additional method calls.
- Actual strict `R03TerminalPlayer.cs` includes positive pre-poison method/delegate/native field observation and negative post-poison reflection, delegate, AOT canary and unchanged actual native field/recovery tests. These are **fixture source statements**, not current-source Player receipts.
- **Blocking source mismatch:** demo `Tools/AssemblyShadow/R03/source-pins.json` Git blob `9d72a237fb6ecd3efe3267ca89625aa49c61775d` pins native `74dbdbea80d83923863303bd2b2c0a87f36541b1`, while current native branch is `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. No one-string silent pin overwrite, no source-mismatched build, no assertion relaxation or new Local root is authorized.

**Disposition:** `CurrentSourceCorrectionPresent_ActualSourceMatchedPlayerNotRun`. The source-derived IR-R03-02 failure from the original 2026-10-08 review is materially addressed in the current native code, but empirical terminal reentry/exception/side-effect safety at the current coherent Player tuple remains **unproven**. Do not declare the original High finding fully closed before independent re-review.

## IR-R03-01 evidence chain reviewed

- Original S committed `FILE_TRANSPORT.json` and `batch/seal-receipt.json` agree on original nine-part evidence.tar.gz `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, **587907380 bytes**, **15713** members. Original `S_Reconciliation/EVIDENCE.json` instead contained an incompatible five-part **283728477**-byte family with `f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7`. These are distinct provenance records.
- `IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json` retains exact original S artifact records and read-only proof workflow `37845000985`, 30 host tests, 90 original ledger-cell joins, 15712 index files and 15713 original archive members. `withdrawnHistoricalClaims.status=NotAuthorityForOriginalS`; `observedAudit.independentReviewer=false`, and IR-R03-01 explicitly remains PartiallyRemediatedNotIndependentlyClosed.
- Separate recovered oversized generated-source identities and S original archive bytes are not equivalent to source/build/process semantic review of every generated invoker/physical entry. The October 8 independent reviewer has not yet issued an amended full-stage PASS.

**Disposition:** `OriginalSProvenanceCorrected_AwaitingIndependentRereview`. Preserve the independent **FAIL** verdict, original recorded S 90/90, wrong old family and newly bound correct original S evidence as distinct.

## Actual host-only regression and CI findings

[Final GitHub Actions run 40086902503](https://github.com/night-outlook/hybridclr_demo/actions/runs/40086902503), source commit `f1f6aec7fc4850ce52efffe4a21a7341fa951f9f`, completed **success** on `macos-15` (job `120851589071`) and `ubuntu-24.04` (job `120851589213`). Both hosts independently checked fixed source blobs, ran **20/20** Python adversarial contracts, compiled/executed **69** native terminal-policy header checks, emitted scoped report `PassedSourceOnlyPreflight_PendingRealPlayerAndIndependentReview`, reported `BlockedStaleRunnerNativePin`, and kept R03/H2/runtime flags false.

Initial attempt [40086592790](https://github.com/night-outlook/hybridclr_demo/actions/runs/40086592790) was **FAIL** because unittest parsed custom fixture checkout arguments. Second attempt [40086808626](https://github.com/night-outlook/hybridclr_demo/actions/runs/40086808626) was **FAIL** because the checker raised untyped ValueError on synthetically removed anchors; typed source-failure diagnostics were corrected. Both original red CI results remain genuine historical test-tool failures; neither was a runtime/native product bug. No production code, previous Local artifact, tests from original S, b7e3, c42a or f51d was changed by this Primary source-only cycle.

## Exact remaining decision

Cannot certify IR-R03-02 current Player safety, IR-R03-01 independent full-stage acceptance, RC2–RC4 complete coverage or H2 readiness. Keep source/host code-check outcome separate from compiled product/runtime/Player observations. Next Primary cycle must reconcile the stale native runner pin and transitive Player/build inputs before proposing a separately authorized four-process Local witness. The separate independent reviewer must examine original-S byte/provenance/semantic joins and the full bounded R03 RC1–RC6 matrix. No active Local assignment.

**All flags remain false:** R03Accepted, H2Passed, qualificationApproved, ReadyForHumanReviewGate, runtimeAcceptance, fullLegacyRegressionAcceptance. PureInterpreter disabled; P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. No H2/X02/M08A or SNAP-01 activity.