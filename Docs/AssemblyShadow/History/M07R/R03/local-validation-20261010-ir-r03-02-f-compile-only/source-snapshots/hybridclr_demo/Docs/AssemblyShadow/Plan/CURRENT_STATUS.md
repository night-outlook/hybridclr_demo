# Current Status — R03 IR-LOCAL-RUNTIME-01 F-COMP Local compilation only

## Owner and earliest unfinished work

**Next owner: Local Validation for ONE bounded F-COMP official managed/native SDK compilation, with no Unity Editor launch, no Players and no runtime 14-cell scheduler.** Earliest unfinished gate: source-matched official Unity 2022.3.62f2 native translation-unit compilation of the current exact `il2cpp_plus` / demo tuple, including the test-only engine reporting probe. The separate F runtime phase is still NOT authorized. The prior E local attempt returned FAIL / ReturnRequired (11 Passed, 3 Failed; three ON SIGSEGV; OFF Passed). The E source/return and all C/D/A/S/R/Q/P/O/N evidence remain immutable.

Native source corrections committed after E include exact physical `UnityEngine.Debug.CallOverridenDebugHandler` native diagnostic handling on terminal failure, first-error trace, a narrowly scoped private `Object::NewPtrFree` friendship, bounded native Boolean transport/fatal reentry, native phase and engine-observer instrumentation. The supplementary managed Player retains all business rejection/field/counter/recovery proof conditions and records first failure without managed exception formatting. No actual corrected Player run has been observed; the original E originating failure remains unknown.

## Evidence separated by actual coverage

| Item | Result and coverage |
| --- | --- |
| Original E Local | FAIL / ReturnRequired, 14 cells (11 Passed/3 Failed), 3 native builds Passed, 4 Players; 3 ON SIGSEGV, OFF Passed; bounded seal Passed |
| E prerequisites and scoped historical loss | Source, 15 S fixtures, host 15/64/69, two exact-loss 416,844-entry audits, two storage admissions Passed; strict original S custody still Blocked |
| Reconciled native host CI | [Run 38093122306](https://github.com/night-outlook/il2cpp_plus/actions/runs/38093122306) Passed Ubuntu/macOS; actual Runtime::Invoke body with VM mocks, actual Object.h private access negative tests, observer with VM mocks, normal/sanitizer cases, 69 policy checks |
| Old full official SDK CI | [Run 38052720849](https://github.com/night-outlook/hybridclr_demo/actions/runs/38052720849) Failed due private NewPtrFree; successful official managed Player substep (0 errors / 13 warnings) does not reclassify overall failure |
| Current official SDK compile | [CI 38093176419](https://github.com/night-outlook/hybridclr_demo/actions/runs/38093176419) Failed in official Editor CDN download (curl 18), before compilation; resumed-download CI pending, and bounded F-COMP Local SDK compilation is authorized separately. `native_validation.py` compiles EngineReportingProbe.cpp in five native profiles using explicit external `--sdk-scratch`. |
| Current real Unity terminal/reporting evidence | NotRun since repair; no ON first-failure/root-cause closure |
| Separate true engine-originated unhandled callback | NotRun in Unity; direct native/mock observer does not establish it |
| Independent R03 review / re-review | FAIL / NotRun |
| Acceptance, H2, qualification, Human Review readiness | All false; PureInterpreter expansion disabled |

## Frozen project and source authority

All four source repos on branch `codex/assembly-shadow-r01b-h1` with canonical `night-outlook/` remotes. Actual Local owner workspace is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`. Required native source pin is in `Tools/AssemblyShadow/R03/source-pins.json` and must equal the final native remote commit, not a previous E/native intermediate. The package and HybridCLR baseline remain `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`. This status is not a final 4-SHA Local handoff; the new F procedure stays inactive.

Preserve immutable E source demo `baa9473200e453d1ba1017610e776e6c18c8d7f1`, original E native `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`, original E report source/publication `75500e3916300d1fd5f7774e0f9de33b9ed3e7da`, and all exact failed ON records. Original E facts: E pre/after 339,367 survivors hash-verified; exactly 77,477 original C missing unchanged; historical strict custody Blocked, four installed native roots missing. Historic S 90 Passed and sealed index are bounded historical evidence, not proof of current live native provenance or full-stage approval.

## Next steps

1. Use [current F-COMP compile-only handoff](../Handoff/WEB_TO_LOCAL.md), [exact compile procedure](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/F_COMPILE_ONLY_PROCEDURE.md), and final four-SHA prompt. All commits/remote tips must match; no Local runtime permission.
2. Run actual official managed/current-native SDK compilers using installed Unity 2022.3.62f2 read-only, with unused evidence and SDK scratch directories outside installed Editor and all protected roots. Require 55 native profile/unit compilations, actual source hashes and official managed Unity API result. Preserve all failed logs if any.
3. Local publishes a factual additive F-COMP checkpoint and returns to Primary; Primary independently inspects reports, repairs any compile defects and publishes the next separate runtime handoff if compile gate passes.
4. **Only after a distinct Primary authorization** may one fresh F full scoped custody/storage preflight and one 14-cell/three-build/four-Player runtime batch run. Preserve E, no retries, no Human Review Gate advancement. Real engine-originated Unity exception reporting remains additional required independent evidence.

No E retry, X02, M08A, H2, full release qualification or PureInterpreter expansion. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`.
