# IR-LOCAL-RUNTIME-01 F-COMP — compile-only Local Validation procedure

**Scope: one fresh source-matched official managed + native SDK compile. NO Unity Editor process launch, NO IL2CPP Player build, NO Player execution, NO original 14-cell scheduler, NO E retry.** This task only resolves the current official compilation evidence gap for the Primary-owned terminal-reporting correction. It is not authority to start the separate [inactive F runtime procedure](F_FOCUSED_LOCAL_PROCEDURE.md).

## Read first

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, the **latest source-pinned** `Handoff/WEB_TO_LOCAL.md`.
2. [Primary reconciliation](PRIMARY_RECONCILIATION.md), [immutable E failed checkpoint](../../local-validation-20261010-ir-r03-02-e-native-receipt/README.md), Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`.
3. Existing actual compiler scripts: `Tools/AssemblyShadow/R03/build_api.py`, `Tools/AssemblyShadow/R03/native_validation.py`, `Tools/AssemblyShadow/R03/source-pins.json`; native `libil2cpp/vm/AssemblyShadowTerminalReporting.h`, `Object.h`, `Runtime.cpp`, test-only `AssemblyShadowEngineReportingProbe.cpp` and `tools/r03/runtime01/`.

### Authority and roots

Four actual owning checkouts under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/`, branch `codex/assembly-shadow-r01b-h1`. Use the **final exact four-SHA Primary handoff**; independently verify each `git rev-parse --show-toplevel`, branch, clean `git status --short`, canonical SSH/HTTPS origin, `git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1`, HEAD, submodules/worktrees and demo native source-pins. A dirty/divergent checkout blocks work; no force/reset/stash/clean or wrong worktree.

The retained historical E result **FAIL** is immutable: 11 Passed / 3 Failed of 14 cells; three ON SIGSEGV, OFF Passed, three old native builds Passed; original first failure Unknown. Do not use its app/native installations or retry E. Strict historical S custody remains **Blocked**: frozen 416,844 paths; 339,367 actual survivors / 77,477 Missing as authenticated during E, four historical S native roots missing. No regeneration, cleanup, rebaseline, relocation, native-source replacement, SDK copy into S/R/Q/P/O/N or other protected paths.

Under `/Users/ah/GitHub/hybridclr/r03-local-validation`, verify ALL four candidates are absent, canonical/nonsymlinked, nonoverlapping and outside every source and protected/historic root **before** creating only preflight:

- `Preflight-R03IRCompile-20261010F-runtime01` — source/host/custody/command receipts
- `ManagedAPI-R03IRCompile-20261010F-runtime01` — official managed API compile output
- `NativeSDK-R03IRCompile-20261010F-runtime01` — syntax-only current native compilation output
- `Scratch-R03IRCompile-20261010F-runtime01` — full disposable SDK source copy, retained separate from evidence

Do **not** create `R03IRLocal-20261010F-terminal-report` or its runtime storage roots. Those are reserved for a separately authorized post-compile F runtime attempt.

### Exact host

Unity binary only as a **read-only path to installed SDK files**:
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.
The compiled APIs and SDK must come from this actual installed Unity 2022.3.62f2, not Unity 6000 or a different version. Python 3.14; Apple clang with SDK arm64, .NET compiler resolved by existing pinned scripts. Do not start Unity, install packages, change app bundles or overwrite any source.

The new `native_validation.py` **requires `--sdk-scratch` whenever `--unity` is given** and rejects source/output/Unity-Editor aliases. It never writes the SDK copy beside the installed Unity editor, to the repository, or under its evidence output. All vendor SDK bytes remain only in the new external scratch root; never upload that vendor tree to GitHub. A script failure must retain all raw command receipts; do not delete temp output to "retry".

## Strict conditional sequence

1. Verify final pinned sources/remote tips/workspace clean, no root aliases, exact Unity executable and read-only SDK headers. Read-only authenticate original C receipt sources and E failure, record disk availability and source SHA / actual compiler binary. Stop on mismatch.
2. Fresh host regressions without Unity execution: **10 native SDK scratch-boundary tests** (`test_native_validation_scratch.py`), native `test_reporting.py` normal/sanitized, real `test_object_access.py`, native `test_engine_observer.py` normal/sanitized, and standalone terminal policy 69 C++17 checks. Record actual command/exit/raw output and source hashes; unrelated R02 historical strict-hash workflow failure must not be silently converted to Passed.
3. Optional but recommended: run original C `verify_scoped_custody.py` before and after compile with new receipts, requiring exact original loss states. If a historical identity has changed, stop, preserve full current Missing/changed rows and return to Primary. This is *not* historical strict custody Passed.
4. Run **one** `build_api.py --workspace --unity --output` on fresh ManagedAPI root. Require actual pinned Unity CoreModule/Editor assembly references, whole current `R03TerminalPlayer.cs` source binding and successful C# compilation. Preserve original negative unsigned-count compile behavior, all source/ref hashes, exact compiler invocations, 0 compiler errors and real result/output hashes. Do not infer a Player build.
5. Run **one** `native_validation.py --workspace --unity --sdk-scratch --output` on fresh disjoint NativeSDK/Scratch roots. Require every ON/OFF/debug profile, `Runtime.cpp`, `Object.cpp`, `AssemblyShadow.cpp`, `AssemblyShadowEngineReportingProbe.cpp`, actual overlay `AssemblyShadowR03Probe.cpp` and all other listed units compiled against the **official pinned** SDK. Expect 11 translation units × 5 configurations = **55** successful syntax-only compilations if no compilation stage aborts. The script separately authenticates all relevant exact source hashes. Collect complete compiler stderr on failure, no bypass of private access or disabled guards.
6. Publish factual compile-only `LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md` update plus additive checkpoint `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261010-ir-r03-02-f-compile-only/` with command receipts, compiler flags/logs/hashes, source/pins, root nonaliasing, input/custody provenance, exact per-unit statuses and failure diagnostics. Keep vendor SDK and binaries out of the repository; publish digest/inventory, permitted log and receipts only. Commit/push/read back all four heads, stop and return to Primary. **Do not start F runtime.**

### Conditional command template — never run past a failure

~~~bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
P="$BASE/Preflight-R03IRCompile-20261010F-runtime01"
MANAGED="$BASE/ManagedAPI-R03IRCompile-20261010F-runtime01"
NATIVE="$BASE/NativeSDK-R03IRCompile-20261010F-runtime01"
SCRATCH="$BASE/Scratch-R03IRCompile-20261010F-runtime01"
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
DOC="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09"
C="$W/hybridclr_demo/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-c-custody-blocked"

# Only after exact four-SHA checkout/root/source checks:
mkdir "$P"
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03" -p 'test_native_validation_scratch.py' -v
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_reporting.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_object_access.py"
"$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
R03_SANITIZERS=1 "$PY" -B "$W/il2cpp_plus/tools/r03/runtime01/test_engine_observer.py"
c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread \
  -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" -o "$P/policy"
"$P/policy"
"$PY" -B "$DOC/verify_scoped_custody.py" --checkpoint "$C" \
  --phase before --receipt "$P/scoped-custody-before.json"

# Only if all above checks pass. Run once; never retry a partial output.
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/build_api.py" \
  --workspace "$W" --unity "$UNITY" --output "$MANAGED"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/native_validation.py" \
  --workspace "$W" --unity "$UNITY" --output "$NATIVE" --sdk-scratch "$SCRATCH"

# After successful or failed compilation when safe (new receipt; not a rerun):
"$PY" -B "$DOC/verify_scoped_custody.py" --checkpoint "$C" \
  --phase after --receipt "$P/scoped-custody-after.json"
~~~

Capture argv/cwd/source, start/end, exit, stdout/stderr SHA-256 for every command. The script may exit early leaving partial compiler evidence; that is **Failed/Blocked**, never Passed. Avoid repeating original commands after failure unless Primary authorizes a *new* diagnostic root/attempt.

**No Unity process, Editor Test Runner, native Player build, Player process, or 14-cell batch may be launched under this task.** The test-only engine reporting observer runs against VM mocks and does not establish actual Unity engine unhandled-exception behavior.

Acceptance remains `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. Independent R03 review FAIL/re-review NotRun. No H2/X02/M08A.
