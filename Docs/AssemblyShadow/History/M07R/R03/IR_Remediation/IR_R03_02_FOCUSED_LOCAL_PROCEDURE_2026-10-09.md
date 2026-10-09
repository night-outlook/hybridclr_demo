# IR-R03-02 focused Local procedure — B successor, 2026-10-09 UTC

Execute only under the exact four-head tuple in the current Primary handoff and `Handoff/WEB_TO_LOCAL.md`. This revision supersedes the A launch instructions, not A's evidence. **A remains CapacityBlocked; B capacity is unknown.** Original independent R03 verdict remains FAIL. No S/R/Q/P/O/N replay, cleanup, retries, H2, X02 or M08A.

## Scope and read order

Read README, CURRENT_STATUS, WEB_TO_LOCAL, unchanged Local-owned LOCAL_VALIDATION/RETURN_TO_WEB, then [the current compile correction](IR_LOCAL_API_01_2026-10-09/README.md), [fixture authority](IR_R03_02_FIXTURE_PROVENANCE_2026-10-09.md), [native design](IR_R03_02_NATIVE_DESIGN_2026-10-08.md), and the original independent FAIL review/C04 erratum and D1=A/D2=A disposition.

The focused batch remains 14 cells, 3 macOS arm64 native builds (ON Release, ON Debug, OFF Release), 4 fresh Players: release-baseline, debug-baseline, release-type-resolution and OFF control. Captured-generic, genuine initializer-failure and complete R03 acceptance are outside this witness. All nontrivial source work remains Primary-owned.

## Exact source and tool prerequisites

Workspace `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`; every repository branch `codex/assembly-shadow-r01b-h1`. Use the final Primary prompt's full demo SHA, a Docs-only descendant of `ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b`. The other three must equal HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, IL2CPP+ `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`. `Tools/AssemblyShadow/R03/source-pins.json` must match.

Inspect each nested owning checkout independently: canonical origin, named branch, exact HEAD, clean tracked/untracked state and fresh `git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1`. An authorized fast-forward to the exact prompt pin is permitted only for a clean matching checkout; no reset/stash/clean/forced switch or unrelated worktree change. If remote advanced beyond the prompt or any pin differs, stop rather than infer authorization.

Use Unity `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, StandaloneOSX arm64, net8-capable dotnet, and Python `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`. Never launch Unity 6000. Preserve the established temp and process-ownership policy.

## Fresh paths and custody

Let the existing parent be `/Users/ah/GitHub/hybridclr/r03-local-validation`. Authorize only these candidates, **after Local proves each absent, nonsymlinked and nonoverlapping**:

| Role | Absolute path |
| --- | --- |
| Preflight records | `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009B-api-bound` |
| Batch, initially absent | `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009B-api-bound` |
| Diagnostics-only sidecar | `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009B-api-bound` |
| Separate executing sidecar | `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009B-api-bound` |

The retained Q root remains `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`. None of the new locations may alias, contain or be nested in any historical evidence or owning checkout. A conflict is Blocked/NotRun; do not invent another root, overwrite or resume. Only the preflight directory may be created before storage-wrapper invocation. Keep batch and sidecars absent for their respective wrapper calls.

Reauthenticate the previous 416,161-file custody inventory and its exact S/R/Q/P/O/N/other protected roots, plus the published A checkpoint and A live diagnostic/preflight records. Record before/after evidence; never silently rebaseline missing or modified files. Preserve A's publication receipt, failed admission and zero-launch result. Retained R stays staged; no protected cleanup or relocation is authorized.

## Current compilation evidence check

The replacement [CI 37903041633](https://github.com/night-outlook/hybridclr_demo/actions/runs/37903041633) succeeded at ba47 with current Player blob `adc798c6c299594d496393c6729c4c6087111b31`, 0 errors/13 warnings. Its exact receipts and lossless full log are in `IR_LOCAL_API_01_2026-10-09/`. This replaces current-body coverage only; the earlier 37874183375 remains NoCoverage for this body. It is a net8/C#9 real-package signature check using Unity API stubs, not official Unity managed compilation or Player execution.

Retain actual CI run/job metadata and verify the source/receipt bridge below. Set `EXPECTED_DEMO_COMMIT` only from the final exact Primary prompt. After the exclusive preflight directory is created, run:

```bash
export PYTHONDONTWRITEBYTECODE=1
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
P=/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03IRLocal-20261009B-api-bound
EXPECTED_DEMO_COMMIT="${EXPECTED_DEMO_COMMIT:?Exact final Primary demo SHA required}"
"$PY" -B - "$W" "$P" "$EXPECTED_DEMO_COMMIT" <<'PY'
import base64, gzip, hashlib, json, subprocess, sys
from pathlib import Path
w, p = map(Path, sys.argv[1:3]); expected = sys.argv[3]
demo = w / 'hybridclr_demo'
def require(ok, message):
    if not ok: raise RuntimeError(message)
def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])
def digest(data): return hashlib.sha256(data).hexdigest()
anchor = 'ba47b41674b83a6f694ac4f8ac1bc8f83a9da24b'
require(git(demo, 'rev-parse', 'HEAD').decode().strip() == expected, 'Wrong demo HEAD')
subprocess.run(['git', '-C', str(demo), 'merge-base', '--is-ancestor', anchor, expected], check=True)
changed = git(demo, 'diff', '--name-only', '-z', anchor, expected).split(b'\0')
require(all(x.startswith(b'Docs/') for x in changed if x), 'Non-Docs delta after compiler source')
e = demo / 'Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_API_01_2026-10-09'
inputs_bytes = (e / 'compile-inputs.json').read_bytes()
result_bytes = (e / 'compile-result.json').read_bytes()
require(digest(inputs_bytes) == 'e905754b191949b61fc552c179df4cbefc05c6f2f25d364291c84aa1041ea243', 'Input receipt changed')
require(digest(result_bytes) == 'f6250ed4ed4bf013fbf5b0857a4dcf38ec977aa2a63d1c0fa95fea5fb5ed1472', 'Result receipt changed')
i, r = json.loads(inputs_bytes), json.loads(result_bytes)
require(r['result'] == 'Passed' and r['demoCommit'] == anchor and r['runId'] == '37903041633', 'Wrong CI result')
require(r['inputsSha256'] == digest(inputs_bytes) and not r['runtimeAcceptance'], 'Wrong result binding')
require(git(w / 'hybridclr_unity', 'rev-parse', 'HEAD').decode().strip() == r['packageCommit'], 'Wrong package HEAD')
for row in i['inputs']:
    name = row['repository'].split('/')[1]
    require(name in ('hybridclr_demo', 'hybridclr_unity'), 'Unexpected input owner')
    root = w / name; f = root / row['path']; data = f.read_bytes()
    require(len(data) == row['bytes'] and digest(data) == row['sha256'], 'Input bytes differ: ' + str(f))
    require(git(root, 'rev-parse', 'HEAD:' + row['path']).decode().strip() == row['gitBlob'], 'Input Git object differs')
encoded = (e / 'build.log.gz.b64').read_bytes()
require(digest(encoded) == 'd4863193f7d3289aab46853513e2d0c17a827bd7aa5a424890ae80f8435953cb', 'Encoded log changed')
log = gzip.decompress(base64.b64decode(encoded.strip(), validate=True))
require(digest(log) == r['buildLogSha256'], 'Compiler log changed')
with (p / 'compiler-build.log').open('xb') as f: f.write(log)
receipt = {'result':'SourceMatchedManagedApiEvidence','demoCommit':expected,'ciSource':anchor,
           'runId':r['runId'],'inputsMatched':len(i['inputs']),'freshLocalCompile':False,
           'unityRun':False,'runtimeAcceptance':False}
with (p / 'CI_CURRENT_SOURCE.json').open('x') as f: json.dump(receipt, f, indent=2); f.write('\n')
print(json.dumps(receipt))
PY
```

Any failed comparison blocks execution. Run native/API/fixture CI source-equivalence checks from the prior procedure, using the exact source-bound current records rather than green job names. Native policy run 37872834945 and official Unity native compilation run 37893353097 remain distinct from this C# run; immutable fixture authority run 37894308627 is not a Player run. The previous Local 64/69 results are reusable historical facts, not new execution.

## Local host and fixture preflight

Run the existing host suite and native policy with output recorded in P:

```bash
"$PY" -B -m unittest discover -s "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR" -p 'test_*.py' -v
c++ -std=c++17 -Wall -Wextra -Werror -pedantic -pthread \
  -I"$W/il2cpp_plus/libil2cpp" "$W/il2cpp_plus/tools/r03/terminal_execution_tests.cpp" \
  -o "$P/terminal-policy"
"$P/terminal-policy"
```

Require 64 Python tests and 69 native policy checks Passed, no weakened assertions. Authenticate the 15 original S DLL Git blobs from publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`. Never regenerate S. The distinct IR target must remain SHA-256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`, 2,048 bytes, PE timestamp zero. Its generation belongs to the admitted batch, not an unadmitted Unity launch. Preserve historical regeneration Failed/NotIdentical evidence.

## Storage: one diagnostic, then at most one conditional execution

Primary has not established current free space. The original 430,129,152-byte deficit is not a current measurement. Human/operator storage management is external and must not touch protected evidence under this assignment. Do not delete caches/snapshots, change quotas/temp paths, relocate roots, reduce thresholds or treat purgeable space as admitted capacity.

Require unchanged `R03StorageAdmissionV1`: exact preserved Q failure cell, full Q sizing, `max(64GiB, 2*Q+20GiB)` available at every checked location, allocation/sync/readback probes and 20GiB sampled operating floor. No reservation is claimed. First run **without --execute**:

```bash
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py" \
  --workspace "$W" \
  --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009B-api-bound \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --demo-commit "$EXPECTED_DEMO_COMMIT" \
  --retained-q /Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair \
  --storage-evidence /Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009B-api-bound
```

Retain stdout/stderr/exit, source-authority, admission, capacity samples, session and dispatch. Require Admitted, diagnostic exit 0 and `batchStarted=false`. A rejection is **CapacityBlocked/NotRun**, preserved permanently; return without retry, Unity launch or another invented root.

Only if every preflight and diagnostic passes, invoke the same command **once** with `--storage-evidence /Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009B-api-bound --execute` instead of the diagnostic sidecar. All other arguments remain identical. This starts a new full admission/probe; never reuse the diagnostic session. No continuation or phase retry after any executing failure.

## Required results and stop point

ON Players must actually execute the same retained active Keep reflection/delegate before poison: both return 42 and the real private instance counter reaches 2. After the caught baseline-owner or type-resolution failure, actually attempt retained active reflection, delegate and ordinary AOT canary; all must reject, no side effect may occur, the pre-resolved field must still be readable at 2, and first recovery/state/generation/fixed diagnostics must remain stable. OFF invokes its ordinary canary twice without a shadow transaction. Exceptions alone do not prove nonexecution.

Retain exact four-source/build pins, original-S and distinct-IR receipts, all 14 cell records, 3 actual native build receipts, 4 raw Player JSON/logs, PID/run nonce/request/argv/build bindings, ledger/index/archive/seal, storage records and before/after custody. Missing or unexecuted artifacts stay Failed/Blocked/NotRun/Unavailable, never inferred Passed.

Publish a new additive checkpoint under `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261009-ir-r03-02-b-api-bound/` only if absent, update Local-owned LOCAL_VALIDATION.md and RETURN_TO_WEB.md, commit/push and read back the final four remote pins. Stop after the one B result and return to Primary. No substantive native/design/validation-contract repair by Local. Independent re-review is separate and NotRun; every acceptance flag remains false and PureInterpreter expansion disabled.
