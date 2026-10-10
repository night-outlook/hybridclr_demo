# Current Status — R03 IR-LOCAL-RUNTIME-01 Primary correction, F pending compilation

## Owner and earliest unfinished work

**Owner: Primary Implementation. Earliest unfinished gate: source-matched official Unity 2022.3.62f2 native translation-unit compilation of the current exact `il2cpp_plus` / demo tuple, including the test-only engine reporting probe.** No new Local Validation execution is authorized while this gate is outstanding. The prior E local attempt returned FAIL / ReturnRequired (11 Passed, 3 Failed; three ON SIGSEGV; OFF Passed). The E source/return and all C/D/A/S/R/Q/P/O/N evidence remain immutable.

Native source corrections committed after E include exact physical `UnityEngine.Debug.CallOverridenDebugHandler` native diagnostic handling on terminal failure, first-error trace, a narrowly scoped private `Object::NewPtrFree` friendship, bounded native Boolean transport/fatal reentry, native phase and engine-observer instrumentation. The supplementary managed Player retains all business rejection/field/counter/recovery proof conditions and records first failure without managed exception formatting. No actual corrected Player run has been observed; the original E originating failure remains unknown.

## Evidence separated by actual coverage

| Item | Result and coverage |
| --- | --- |
| Original E Local | FAIL / ReturnRequired, 14 cells (11 Passed/3 Failed), 3 native builds Passed, 4 Players; 3 ON SIGSEGV, OFF Passed; bounded seal Passed |
| E prerequisites and scoped historical loss | Source, 15 S fixtures, host 15/64/69, two exact-loss 416,844-entry audits, two storage admissions Passed; strict original S custody still Blocked |
| Reconciled native host CI | [Run 38093122306](https://github.com/night-outlook/il2cpp_plus/actions/runs/38093122306) Passed Ubuntu/macOS; actual Runtime::Invoke body with VM mocks, actual Object.h private access negative tests, observer with VM mocks, normal/sanitizer cases, 69 policy checks |
| Old full official SDK CI | [Run 38052720849](https://github.com/night-outlook/hybridclr_demo/actions/runs/38052720849) Failed due private NewPtrFree; successful official managed Player substep (0 errors / 13 warnings) does not reclassify overall failure |
| Current official SDK compile | **Pending exact new successful run** at current pinned native source; `native_validation.py` includes the new EngineReportingProbe.cpp in native unit matrix |
| Current real Unity terminal/reporting evidence | NotRun since repair; no ON first-failure/root-cause closure |
| Separate true engine-originated unhandled callback | NotRun in Unity; direct native/mock observer does not establish it |
| Independent R03 review / re-review | FAIL / NotRun |
| Acceptance, H2, qualification, Human Review readiness | All false; PureInterpreter expansion disabled |

## Frozen project and source authority

All four source repos on branch `codex/assembly-shadow-r01b-h1` with canonical `night-outlook/` remotes. Actual Local owner workspace is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`. Required native source pin is in `Tools/AssemblyShadow/R03/source-pins.json` and must equal the final native remote commit, not a previous E/native intermediate. The package and HybridCLR baseline remain `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`. This status is not a final 4-SHA Local handoff; the new F procedure stays inactive.

Preserve immutable E source demo `baa9473200e453d1ba1017610e776e6c18c8d7f1`, original E native `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`, original E report source/publication `75500e3916300d1fd5f7774e0f9de33b9ed3e7da`, and all exact failed ON records. Original E facts: E pre/after 339,367 survivors hash-verified; exactly 77,477 original C missing unchanged; historical strict custody Blocked, four installed native roots missing. Historic S 90 Passed and sealed index are bounded historical evidence, not proof of current live native provenance or full-stage approval.

## Next steps

1. Authenticate newly published native and demo commits through Connector, and review any new Source changes before claiming source equivalence. All write/readback smoke tests are operational.
2. Obtain successful **official pinned SDK native translation compile** for candidate/debug/ON/OFF including native observer probe and current Player C# official managed compile (source-matched actual logs, compiler flags, source/output hashes). If Failed, repair through Primary without bypassing checks.
3. Finalize [Primary correction](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/PRIMARY_RECONCILIATION.md) and [conditional F procedure](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/F_FOCUSED_LOCAL_PROCEDURE.md), then publish an exact four-SHA `Handoff/WEB_TO_LOCAL.md` and reverify remote heads.
4. Only then may one fresh **F** scoped local preflight/14-cell/3-build/4-Player run occur under strictly new F roots if full prior-source/fixture/custody/storage admission passes; no retries.
5. Preserve separate first-error/native phase, physical-method/counter, managed ON/OFF raw JSON, actual build/process/nonce and crash evidence. Reconcile failures before independent R03 re-review and human gate.

No E retry, X02, M08A, H2, full release qualification or PureInterpreter expansion. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`.
