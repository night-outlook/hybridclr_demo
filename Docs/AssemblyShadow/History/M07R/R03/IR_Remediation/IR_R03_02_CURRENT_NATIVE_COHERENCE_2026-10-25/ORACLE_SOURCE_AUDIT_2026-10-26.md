# IR-R03-02 — Current-native Player verification oracle adversarial source review (2026-10-26)

**Primary Implementation; source/host-only. NO Player run, independent full-stage review, Local handoff or H2 approval.** This report supplements [the current-native source candidate design](DESIGN.md), [Primary source audit](PRIMARY_SOURCE_AUDIT.md) and [independent re-review request addendum](INDEPENDENT_REREVIEW_ADDENDUM.md).

## 1. Why this review exists

The original independent R03 review [2026-10-08](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) is **FAIL**, including High `IR-R03-02`: an otherwise-valid active business method might execute after terminal transaction failure. The existing [erratum](../../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md) corrects a mistaken prior claim: the original S C04 Player receipts did **not** contain explicit affirmative post-poison method-attempt fields. Current terminal native guards and focused real-Player source fixtures have since changed, but **current-source Player execution has not occurred**.

The separate current-native source preparation introduced a parallel runner that keeps the historical R03 native `74dbdbea80d83923863303bd2b2c0a87f36541b1` pin separate from candidate native `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. Initial source-only CI `40264569824` proved exact ten Git blobs and 20 source/pin contracts on Mac/Linux. This is not a real native binary/install/Player observation.

## 2. Additive exact source/test scope

| Path / origin | Git blob at current candidate | Claim checked |
| --- | --- | --- |
| `Tools/AssemblyShadow/R03IR/run_terminal_local.py` | `70b1a27f2dbbcad93f67e8caddcf7282ff3afd73` | Existing **unmodified** `verify_ir` / `verify_engine` functions; five focused case runner |
| `Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs` | `598feeec3231707091699d99fbf4428d50b52024` | Existing **unmodified** C# Player source: pre-poison positive control, actual attempted post-poison reflection/delegate/AOT canary, native field observation, real engine unhandled sentinel |
| `Tools/AssemblyShadow/R03IR/current_native_oracle_contracts.py` | `7b87b599170a2a38bb58f344d18346f38297ba77` | New 27-test synthetic source-bound oracle regression suite, deliberately **not** `test_*.py` to avoid unexpected historical suite discovery |
| `.github/workflows/r03-ir-current-native-oracle-source-only.yml` | `a452f1cb368c45cbf7f0a2b0a2356d5bb1fe45af` | New explicit read-only `macos-15`/`ubuntu-24.04` matrix; no external SDK, Unity or product app |

Existing actual code is imported and its **real** `verify_ir` and `verify_engine` functions are invoked against known synthetic positive/negative records (instead of comparing only source text or executing test substitutes). Both fixture and oracle blobs are independently fixed by Git-object hash checks before executing the tests. No existing native, package, interpreter or Player code, legacy `source-pins.json`, original S fixture or historical test was altered. No test has `runtimeAcceptance=true` as an accepted result.

## 3. Actual Mac/Linux CI result

[Run 40285861973](https://github.com/night-outlook/hybridclr_demo/actions/runs/40285861973), source/CI commit `8d537fcfb65db76a7d34044a847ad2c5d84fea52`: completed **SUCCESS** on **macos-15** (job `121449229355`, `Ran 27 tests` / `OK`) and **ubuntu-24.04** (job `121449229645`, `Ran 27 tests` / `OK`). The raw job logs were independently read. Source-only test execution took under one second per host; **no** compiler, original K/S/R03 Player, Unity installation or external SDK invocation was made by this workflow.

Focused positive oracle cases: baseline-owner terminal failure, independent type-resolution terminal failure, feature-OFF ordinary execution, and native engine-unhandled sentinel. The original runtime runner defines **five** fresh Player cases (release baseline, debug baseline, release type, OFF, release engine); the synthetic baseline-owner oracle is shared by release/debug, **not** proof of either real Player execution.

Adversarial fail-closed checks cover:

1. **Actually attempted business entry after poison:** all three reflection/delegate/AOT attempt booleans required true; an omitted/false field must reject.
2. **No post-poison body execution:** all three success flags must remain false; native/managed active method field must remain exactly `2` and readable; the AOT canary must not increment.
3. **Cause and poison persistence:** source native state 6→9, first/last recovery string equality, original typed failure code/disposition, native baseline guard values, reserve/GC mask and native terminal reporter mask.
4. **Authoritative process/fixture:** nonce/run/case/pid equality, exact Unity version/platform, explicit non-acceptance and a real positive control before poison.
5. **Feature OFF negative control:** ordinary canary does increment without poison; ON probe attempts and terminal reporting must not be fabricated for OFF.
6. **Engine unhandled callback:** exact run-scoped sentinel in native Unity reporter, `managedHandlerExecuted=false`, bounded native completion, healthy pre-poison logger count, no post-poison managed logger body, no fake fatal log.

**Observed test result:** the fixed real verifier rejects the enumerated synthetic forged/malformed records and accepts the deliberately well-formed typed synthetic records. This establishes bounded **oracle behavior**, not authentic production values or Player-process source identity.

## 4. Remaining source/empirical gaps and impact

- **IR-R03-02 remains `CurrentSourceCorrectionPresent_CurrentSourceMatchedPlayerNotRun` / open for independent closure.** No current native `e1e5...` Unity Player build or fresh process currently demonstrates a caught terminal failure followed by a valid attempted active method, absent body side effects and stable original failure/recovery in a real application.
- Five original focused Player cases are **NotRun at the current candidate tuple**; the `run_terminal_current.py` candidate remains separate and no new output roots are allocated. A test oracle PASS is not a build receipt, actual managed exception, native canary or Player observation.
- The candidate's five cases do **not** cover every captured generic terminal path, post-publication module initializer terminal poison, reverse AOT→managed thunks, all virtual/interface bridges or alternate platforms. These still require independent claim-by-claim disposition, targeted fixture preparation and source-matched runtime evidence if asserted within R03 scope.
- **IR-R03-01 remains `PartiallyRemediatedNotIndependentlyClosed`.** The authoritative original-S archive is the nine-part `23aedcaf...` / 587907380 bytes, not the withdrawn five-part `f4c2a...` family. Its separate independent semantic source/build/Player/process re-review and oversized generated source omissions are not resolved by these oracle tests.
- **Owner D1=A/D2=A remain binding.** Conservative NativeLayoutAdmissionV1 only; PureInterpreter structural expansion deferred to X02 (not Passed). Development-profile performance data are observational and four contaminated unisolated warm certificates remain Failed.

## 5. Scope-safe next step

Primary may use these tests when preparing a separately authorized, source-frozen current-native Player witness and independent full-stage R03 re-review. **No Local Validation execution is authorized here**; the canonical `WEB_TO_LOCAL.md` stays CLOSED. A later real Player PASS would be a *new* focused evidence record rather than a replacement of the original S, b7e3, c42a or f51d outcomes. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false, PureInterpreter disabled. Do not start M08A, X02, protected SNAP-01 or H2.
