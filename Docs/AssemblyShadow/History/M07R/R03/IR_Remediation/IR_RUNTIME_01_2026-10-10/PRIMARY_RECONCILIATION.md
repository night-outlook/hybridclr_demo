# IR-LOCAL-RUNTIME-01 — Primary source reconciliation and validation (2026-10-10)

**Status: corrected source/host CI published; official exact SDK native compilation and a fresh Unity Player result remain pending. This is NOT a Local Validation authorization.**

## Immutable preceding result

Local E ran one genuine focused 14-cell batch at demo `baa9473200e453d1ba1017610e776e6c18c8d7f1`, native `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`. **11 Passed, 3 Failed**; three builds succeeded; OFF Player Passed, all three ON Players exited SIGSEGV with no ON raw/verification records. The complete bounded evidence seal Passed; source/fixture/host/custody/storage prerequisites Passed independently. Two authenticated macOS reports locate native terminal rejection recursively reentering Unity `CallOverridenDebugHandler` until stack exhaustion; the *originating* first failure is Unavailable. E and historical S/R/Q/P/O/N/A/B/C/D are immutable. Read `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md` and `History/M07R/R03/local-validation-20261010-ir-r03-02-e-native-receipt/` for factual authority.

## Production source correction and unchanged rules

The current source implements a **single exact physical Unity engine reporting callback substitution** in `il2cpp_plus/libil2cpp/vm/AssemblyShadowTerminalReporting.h` and `vm/Runtime.cpp`. Its managed callback body/custom logging handlers are not invoked after terminal failure. It writes bounded native observations; `FixedHandledResult` uses an explicitly scoped friend in actual `Object.h` for reference-free Boolean allocation instead of ordinary boxing/managed class initialization. Native failures abort rather than recursively ask managed Unity to log again. Guards for all other business/reflection/delegate/AOT method entries remain in effect. Native `RecordFirstGuardFailure` persists first-cause stderr evidence; supplementary C# Player reports native phases and retains field/counter/recovery assertions. Feature-OFF remains an independent control.

The original bound IR output remains 14 scheduler cells, three native builds and four Players. Original pre-poison actual `Methods.R03.Node.Keep` reflection/delegate (42/42) and real private `stable` 0→2, and post-poison rejection without active/AOT side effects plus readable stable field 2, are **not weakened**. Native terminal-report probe mask must be 15 in ON, zero in OFF. The probe is a direct native transport assertion; it is **not** itself an engine-originated Unity exception test. A separate test-only `AssemblyShadowEngineReportingProbe.cpp` and host observer exist, but true engine-originated behavior still requires a dedicated real Player observation and independent review.

Existing original-S strict custody remains `Blocked`: 416,844 frozen entries, 339,367 survivors, 77,477 unchanged missing identities at E before/after, four historical S installed native roots missing; `ScopedHistoricalLossStable` was allowed *only* for fresh independent IR evidence. No historical restoration or reduced inventory.

## Current correction / source pins

Branch everywhere: `codex/assembly-shadow-r01b-h1`. Native feature source includes `AssemblyShadowTerminalReporting.h`, `Runtime.cpp`, `AssemblyShadow.cpp`, exact friend declaration in `Object.h`, `AssemblyShadowEngineReportingProbe.cpp`, and regression programs `test_reporting.py`, `test_object_access.py`, `test_engine_observer.py`.

Current demo `Tools/AssemblyShadow/R03/source-pins.json` binds the native revision with the CI wiring correction and the same fixed `hybridclr`/`hybridclr_unity` pins. `Tools/AssemblyShadow/R03/native_validation.py` now explicitly includes the new engine-reporting probe as a translation unit in the official macOS arm64 ON/Debug/OFF matrix. Final exact commit pins must always come from remote readback, not copied old candidate revs.

## CI and coverage

- [Native reporting CI 38093122306](https://github.com/night-outlook/il2cpp_plus/actions/runs/38093122306) **Passed on Ubuntu 24.04 and macOS 14**. Actual native code fragments with mocked VM dependencies, 20,000 repeated reporting invocations per ON test configuration, source-frozen private-access negative tests, engine observer host tests, sanitizer profiles and 69 unchanged terminal-policy checks passed. Neither actual Unity execution nor full SDK translation compilation.
- The earlier pinned [official Unity build/API CI 38052720849](https://github.com/night-outlook/hybridclr_demo/actions/runs/38052720849) **Failed** at `Object::NewPtrFree` private-member access; its current-Player managed API compilation did succeed with official Unity 2022.3.62f2 managed assemblies (0 errors / 13 warnings). It does not cover the now-corrected native source, and that failed run is not reclassified.
- The unrelated legacy R02 source-verification workflow may still be **Failed** because protected old source hashes do not match later R03 sources. Do not rewrite historic R02 authority or call its failure Passed.
- Full new official native compile and current Player runtime are **NotRun/Unverified until explicit source-matched CI and Local results establish them**. The exact new CI run IDs/results belong in an additive receipt once completed; do not infer them from this document.

## Next Primary gate and Local requirements

First obtain source-matched official macOS Unity 2022.3.62f2 managed/native compile evidence for the entire current source tuple and actual engine-probe translation unit. Repair any remaining compile defects **without weakening terminal business-execution denial**. Then publish a fresh F procedure and `Handoff/WEB_TO_LOCAL.md` pinning the exact final four remote HEADs and four **unused** external F roots. Fresh Local prerequisites: 15 C custody tests, 64 IR Python tests, 69 native policy checks, actual current reporting host regressions, 15 original S Git fixtures, current C# API source equivalence, S seal, retained Q/R, complete 416,844-entry exact-loss before/after audits, and independent storage diagnostic/execution admissions. If fully admitted, one new 14-cell/3-build/4-Player execution only; collect original first failure/phases, ON/OFF JSON, raw logs, actual source/build/PID/request joins and bounded seal. No E retry, no automatic phase resume.

Independent R03 full-stage review remains **FAIL**; independent re-review **NotRun**; captured generic/initializer work and IR-R03-01 closure remain outstanding. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2/X02/M08A or automatic Human Review Gate approval.
