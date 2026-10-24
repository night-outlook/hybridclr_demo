# R03 independent re-review readiness — Primary source and evidence design

**Scope: R03 only; Primary Implementation preparatory work.** Not an independent stage re-review, not a Human Review Gate, and not authorization to run Unity/Player, product compilation, H2/X02/M08A, or a new Local cycle.

## 1. Two HIGH findings from the existing independent full-stage review

The [2026-10-08 independent full-stage review](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) produced an immutable **FAIL** with high-severity **IR-R03-02** (otherwise valid business method could execute after terminal failure) and **IR-R03-01** (original S archive identity mismatch). The [citation erratum](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md) clarified that C04 did NOT record affirmative post-poison new-method attempt fields; absence is not an observed false value.

Owner D1=A and D2=A remain binding: R03 uses conservative NativeLayoutAdmissionV1; broader PureInterpreter structural evolution is deferred to X02. R03 development timing/memory measurements are observational, not production-SLA acceptance. Other resource/runtime/graph/RC6 obligations are not waived.

## 2. IR-R03-02 — current source correction present, runtime proof still missing

At current native il2cpp_plus e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb, AssemblyShadow.cpp guards AssertMethodIsActive with an early TerminalMethodDenied before physical method/class inspection and a second terminal check before success return. TerminalMethodDenied joins failed states and durable failure facts; AssemblyShadowTerminalExecution.h excludes ordinary Disabled/OFF calls and allows only exact fixed diagnostic constructors under the separately guarded scope. RequireActiveMethod rejects terminal entry without overwriting the original failed recovery error. Runtime::Invoke, InvokeWithThrow and actual HybridCLR interpreter entry/nested/delegate/virtual call sites retain RequireActiveMethod.

These are **source contract observations**, not an actual post-poison Player acceptance. The existing R03TerminalPlayer.cs has the relevant pre-poison active reflection/delegate/field increments and post-poison attempted reflection/delegate/AOT canary plus unchanged field/first recovery assertions. **Current R03 runner is blocked** because Tools/AssemblyShadow/R03/source-pins.json binds il2cpp_plus at 74dbdbea80d83923863303bd2b2c0a87f36541b1, not current e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb. Do not quietly rewrite the pin and infer Player coverage. Native terminal header-only policy 69/69 checks have a bounded Mac/Linux CI success and are not a substitute for linking/executing the current Unity runtime.

## 3. IR-R03-01 — correct original S archive authenticated, full independent review missing

The immutable original-S checkpoint FILE_TRANSPORT.json and seal-receipt.json agree on original evidence.tar.gz SHA-256 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6, 587907380 bytes, nine ordered parts and 15713 archive members (15712 indexed input files). Earlier S_Reconciliation/EVIDENCE.json instead named f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7, 283728477 bytes, five parts and 18160 members. The records are not interchangeable and neither may be edited or silently relabeled.

The additive original-S provenance correction records original checkpoint/transport/index/member/90-cell ledger byte audit Passed in CI run 37845000985, while explicitly stating independentReviewer=false and IR-R03-01=PartiallyRemediatedNotIndependentlyClosed. Its withdrawnHistoricalClaims.status=NotAuthorityForOriginalS preserves the earlier incompatible claim. The recovered oversized generated C/C++ blob identities have NOT received exhaustive semantic code review. The complete original S source/build/Player/process authority and semantic graph still require separate independent assessment.

## 4. New bounded verification tooling

review_readiness.py authenticates exact source Git blobs, checks native terminal method denial ordering and supported Runtime/HybridCLR dispatch source, detects stale demo/native runner source pin, checks original-S archive corrective identity and withdrawn contradictory archive, and emits explicit negative scope flags. test_review_readiness.py contains **20 adversarial host-only tests** (terminal checks removed, overbroad corlib diagnostic allowance, missing interpreter or Runtime guard, fake S archive/owner decision, and absent Player post-poison attempt). The Mac/Linux CI also builds and executes only the 69-check standalone native terminal-policy header fixture. No official installed SDK compile, Unity Editor/Player, original R03 runtime batch, old evidence rewrite or independent stage re-review happens here.

## 5. Mandatory disposition

IR-R03-02: CurrentSourceCorrectionPresent_ActualSourceMatchedPlayerNotRun. IR-R03-01: OriginalSProvenanceCorrected_AwaitingIndependentRereview. **Prior independent full-stage verdict FAIL remains FAIL.** f51d audit-only PASS remains bounded to historic source-host/SDK receipts; b7e3 and c42a historical Local FAIL remain immutable. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete; R03Accepted/H2Passed/qualificationApproved/ReadyForHumanReviewGate/runtimeAcceptance false; PureInterpreter disabled. No active Local assignment or H2 initiation.
