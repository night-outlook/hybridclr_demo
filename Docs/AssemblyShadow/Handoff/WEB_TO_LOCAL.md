# Primary Implementation → Local Validation — F-COMP official compilation ONLY

**Authorization: ONE fresh F-COMP managed/native SDK compilation using installed Unity 2022.3.62f2 without launching Unity or any Player. No F runtime batch authorization.** The previous E result is irreversible **FAIL**; no E retry, no existing Player reuse, no original S cache/native restoration.

## Objective and source

Resolve the remaining official SDK C# + C++ translation compilation evidence gap for Primary-owned `IR-LOCAL-RUNTIME-01`: terminal rejection previously caused Unity logging recursion/SIGSEGV; the repaired native code substitutes exactly one physical Unity reporting callback with bounded native diagnostic handling and preserves every other business/reflection/delegate/AOT denial. Compilation cannot establish runtime safety or R03 acceptance.

Read first:
1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, this `Handoff/WEB_TO_LOCAL.md`.
2. [F-COMP exact commands and evidence](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/F_COMPILE_ONLY_PROCEDURE.md), [Primary source/evidence reconciliation](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/PRIMARY_RECONCILIATION.md).
3. Local-owned `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, [immutable E FAIL](../History/M07R/R03/local-validation-20261010-ir-r03-02-e-native-receipt/README.md), original C exact-loss custody policy and retained original S source authorities.
4. Original R03 design/plans, independent full-stage FAIL/C04 erratum and HUMAN_REVIEW_GATES. No later stage.

All repositories branch `codex/assembly-shadow-r01b-h1`. Independently verify the exact **final 40-SHA tuple in the final Primary handoff** against GitHub remote and clean local HEAD, each repo's real top, origin, branch, worktrees and submodule state. Actual source workspace is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; do not use other worktrees or reset/stash/clean unrelated state. The demo's **final documentation-publication SHA is supplied in the final Primary prompt** and must be a source-equivalent descendant of the pinned compiler scripts below; it cannot be inferred from an older execution or CI SHA.

| Canonical repository | Actual owning local checkout | Exact binding |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final Primary pushed 40-SHA; contains current native pin and compile-only procedure |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `c386cdd1e8942561f1d1e1fada52d21ca524f174` |

The `Tools/AssemblyShadow/R03/source-pins.json` file must bind exactly these three non-demo SHA values. Verify current `R03TerminalPlayer.cs` and native source Git blobs/manifest, including `Runtime.cpp`, `Object.cpp`, `Object.h`, `AssemblyShadow.cpp`, `AssemblyShadowEngineReportingProbe.cpp`, `AssemblyShadowTerminalReporting.h`, and the additional R03 C++ overlay. No source edits by Local except a truly bounded compile command/path correction returned with full evidence; all nontrivial source fixes return to Primary.

## Current evidence; what is NOT proven

[Native host CI 38093122306](https://github.com/night-outlook/il2cpp_plus/actions/runs/38093122306) **Passed on macOS and Linux**: normal/sanitized native reporting adapter, real private `Object.h` test, mocked engine-reporting observer, 69 terminal-policy checks. It is NOT official whole native translation compilation or Unity execution. Prior [official build CI 38052720849](https://github.com/night-outlook/hybridclr_demo/actions/runs/38052720849) **Failed native private access** (later fixed narrowly in `Object.h`); its successful official managed compile substep is distinct. Current exact [CI 38093176419](https://github.com/night-outlook/hybridclr_demo/actions/runs/38093176419) **Failed at Unity package download** (`curl 18`, 3,957,229,180 bytes remaining), so managed and native compile stages were **Skipped**, not failed product compilation. The CI downloader now supports bounded resumable retries under unchanged package SHA-256, but pending/failed CI is no substitute for this task.

Original E ran 14 real cells (11 Passed/3 Failed), three builds Passed, OFF Passed, three ON SIGSEGV with missing ON semantic JSON. Original first failure **Unavailable**. Independent E before/after custody `ScopedHistoricalLossStable`: 416,844 original map files, 339,367 survivors byte verified, 77,477 Missing path/hash identities unchanged; historical strict full S custody remains **Blocked**, four original native SDK roots Missing. E and earlier A/B/C/D/S/R/Q/P/O/N stay immutable. The scoped exception never grants new full-custody PASS.

## New single-use external paths and hard source/custody gates

Use these exact four candidate roots under `/Users/ah/GitHub/hybridclr/r03-local-validation/` only after independently proving all absent/nonaliasing/nonsymlinked, disjoint from source, original S/R/Q/P/O/N and every old A/B/C/D/E root:

- `Preflight-R03IRCompile-20261010F-runtime01` — source and actual command/custody preflight
- `ManagedAPI-R03IRCompile-20261010F-runtime01` — official managed assembly compile output
- `NativeSDK-R03IRCompile-20261010F-runtime01` — official native translation-unit compile receipts
- `Scratch-R03IRCompile-20261010F-runtime01` — native SDK copy, **outside** evidence and installed Unity Editor

Absolute Unity binary path (reference-only, **never execute**): `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, target SDK macOS arm64. Python 3.14. No Unity 6000 executable or Unity Editor process. Native script **requires** `--sdk-scratch` with `--unity`, rejects aliases or existing scratch, and copies SDK only into the external new root. This is an intentional modification to prevent modifying the installed Editor.

Before compilation verify exact source/remote pins; actual SDK version/digest provenance; current repository and fixture/source hashes; fresh source-appropriate host tests (**ten** `test_native_validation_scratch.py` safety cases, `test_reporting.py` normal/sanitized, `test_object_access.py`, `test_engine_observer.py` normal/sanitized, native policy 69). Read-only original C scoped-custody-before audit should retain expected exact missing identities, and after-custody audit should run after compile. Unexpected new/restored/changed paths block; original strict full custody stays Blocked. No protected data cleanup or rebaseline. An environment-specific SDK path failure is recorded factually, not silently fixed with a different Editor or temp directory.

## One managed compile and one native compile, with exact evidence

Run commands **only after** the ordered prerequisites and unused-root checks in [F-COMP procedure](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/F_COMPILE_ONLY_PROCEDURE.md). The two actual compiler invocations are:

~~~bash
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/build_api.py" \
 --workspace "$W" --unity "$UNITY" \
 --output "$BASE/ManagedAPI-R03IRCompile-20261010F-runtime01"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/native_validation.py" \
 --workspace "$W" --unity "$UNITY" \
 --sdk-scratch "$BASE/Scratch-R03IRCompile-20261010F-runtime01" \
 --output "$BASE/NativeSDK-R03IRCompile-20261010F-runtime01"
~~~

Do **not** run if any prerequisite failed. Existing `build_api.py` must genuinely compile the current Player source and pinned HybridCLR package/helper against *official* Unity managed assemblies; preserve its expected historical unsigned-count negative control separately from unexpected compiler errors. Native `native_validation.py` must compile **11 units × 5 profiles = 55** real SDK syntax-only configurations, including the new engine-reporting probe and test-only overlay, without bypassing private C++ access or guards. Its output includes actual compiler command receipts and source/SDK digest inventory. Save exact argv, CWD, start/end, exit, stdout/stderr and SHA for every command; no synthetic results.

**Strict stopping point:** Publish factual compile-only `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` with additive `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261010-ir-r03-02-f-compile-only/` checkpoint. Only permitted upload is source bindings, permitted compiler outputs/logs, inventories and receipts; never SDK vendor files, credentials, or unrelated user data. Commit/push/verify four repository heads; STOP and return to Primary. Failed native compile must include actual first error and subsequent output without workaround/retry; later failures may be unresolved. Do not launch Unity, native Players, native Player builds or the 14-cell F runtime batch. The [F runtime procedure](../History/M07R/R03/IR_Remediation/IR_RUNTIME_01_2026-10-10/F_FOCUSED_LOCAL_PROCEDURE.md) remains inactive until separate Primary approval.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`. Independent R03 full-stage review FAIL, rereview NotRun, PureInterpreter expansion disabled. No H2/X02/M08A.
