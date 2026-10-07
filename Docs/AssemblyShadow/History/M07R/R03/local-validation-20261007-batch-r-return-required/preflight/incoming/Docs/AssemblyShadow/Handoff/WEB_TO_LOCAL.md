# Primary Implementation → Local Validation: storage prerequisite, then batch R

## Conditional objective

Reconcile **R03-LQ-001** as an environmental allocation failure. Establish measured storage headroom with the supplied tools, then execute **exactly one unused complete batch R only if admission passes**. No non-trivial code/design change is assigned to Local. If capacity cannot be established safely, return CapacityBlocked with **batch NotRun**; do not launch Unity or retry Q.

Q remains ReturnRequired: 89 Passed / 1 Failed / 0 Blocked, 90 cells; six fresh builds, all 59 Player checks and 18/754/755 Editor cases Passed, zero skips/inconclusive; seal Passed. The integration cell Failed and its restored-baseline zero-root/zero-closure proof is Unavailable. Preserve Q/P/O/N, contaminated controls' Failed unisolated warm certificates and all historical evidence unchanged.

## Read first

Read `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, then `History/M07R/R03/LQ_Storage_2026-10-07/{DESIGN.md,PRIMARY_REVIEW.md,EVIDENCE.json}` and this complete assignment.

## Exact sources and paths

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Exact Local checkout | Commit authority |
|---|---|---|
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Storage source/CI anchor `357a9024865561362cd2c42fa8f793f56aac1763`; execute the final Docs-only descendant with the exact 40-character SHA supplied in Primary's final prompt |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

Both R03 source-pin manifests, the existing Completion/R03/R02 code, C# helpers, native code, package, fixtures, reference-build pins, build profiles, timeouts, warm-up and leases are unchanged from Q. New files are confined to `Tools/AssemblyShadow/R03Storage/` (entry, guard and two tests), `.github/workflows/r03-storage.yml`, and Primary docs. Later changes after `357a9024...` must be Docs-only. Never execute from or merge a disposable Connector smoke branch, including `codex/connector-smoke-lq-storage-69af19f6`.

## Storage conditions and limits

Admission requires `max(64 GiB, 2*B + 20 GiB)` available at **each** batch/workspace/temp/Git/sidecar location, where `B` is the measured retained Q live-root planning size. The 64 GiB floor and formula are conservative policy choices, not a proven peak or a universal Unity requirement. Small allocation/fsync/readback probes and current filesystem identity must pass. The script does not reserve space and cannot rule out later quota, competing-writer or metadata failures.

Q's 22 GiB entry and about 14 GiB later observations are insufficient for this policy. Review the captured APFS/quota information; do not ignore a known quota/container discrepancy. Unsupported diagnostic commands remain Unavailable, not evidence of no quota. The same-container `/Volumes/Data` is not an independent free-space pool. Do not delete/move Q/P/O/N, `.git`, Libraries or other user data to make the gate pass. Operator-approved capacity remediation is an external prerequisite; report the actual deficit when it is missing. No new external mount/path is implicitly authorized.

During execution, a 20 GiB floor, filesystem change or observation failure is latched. Future nonessential actions are prevented; existing in-flight command handling is unchanged. P05 restore/final authority remain callable and sealing remains the original implementation. A separate probe runs before integration. Retain samples and full Python failure tracebacks; do not weaken the guard or manually retry a phase.

## Environment and unused locations

Unity 2022.3.62f2, StandaloneOSX arm64, at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Python at `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`. SDK-only DOTNET_ROOT `/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk`, SDK 8.0.318; never launch Unity 6000. Child TMPDIR remains `/private/tmp`.

- New batch: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007R-lq-storage`
- Local preflight/publication: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261007R-lq-storage`
- Diagnostic-only check: `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03LocalBatch-20261007R-lq-storage`
- Executing storage sidecar: `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03LocalBatch-20261007R-lq-storage`
- Preserved Q live input: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`

The October 7 name is a new run identifier, not a reinterpretation of Q's October 6 PDT clocks. Missing/dirty/wrong paths, unexpected origin/head, an existing output, or unavailable admission input is a blocker. No reset/stash/force-checkout/cleanup is authorized.

## Prepare and diagnose (no Unity/Player launch)

Set `EXPECTED_DEMO_COMMIT` to the exact latest pushed demo commit in Primary's final prompt; never infer it from HEAD. Retain command output in the new preflight directory. The preparation block verifies origins and exact expected commits before fast-forwarding.

```bash
set -euo pipefail
: "${EXPECTED_DEMO_COMMIT:?Set the exact final SHA from the Primary handoff prompt}"
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
export DEMO="$WORKSPACE/hybridclr_demo"
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
export BATCH="$BASE/R03LocalBatch-20261007R-lq-storage"
export PREFLIGHT="$BASE/Preflight-R03LocalBatch-20261007R-lq-storage"
CHECK="$BASE/StorageCheck-R03LocalBatch-20261007R-lq-storage"
STORAGE="$BASE/Storage-R03LocalBatch-20261007R-lq-storage"
Q="$BASE/R03LocalBatch-20261006Q-lp-repair"
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
export DOTNET_ROOT=/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk
export PATH="$DOTNET_ROOT:$PATH" DOTNET_MULTILEVEL_LOOKUP=0 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp
for PATH_TO_CREATE in "$BATCH" "$PREFLIGHT" "$CHECK" "$STORAGE"; do test ! -e "$PATH_TO_CREATE"; done
mkdir "$PREFLIGHT"
for REPO in hybridclr_demo hybridclr hybridclr_unity il2cpp_plus; do
  ROOT="$WORKSPACE/$REPO"
  test "$(git -C "$ROOT" rev-parse --show-toplevel)" = "$ROOT"
  test -z "$(git -C "$ROOT" status --porcelain=v1 --untracked-files=all)"
  test "$(git -C "$ROOT" branch --show-current)" = "$BRANCH"
  URL="$(git -C "$ROOT" remote get-url origin)"
  case "$URL" in
    "https://github.com/night-outlook/$REPO.git"|"https://github.com/night-outlook/$REPO"|"git@github.com:night-outlook/$REPO.git"|"ssh://git@github.com/night-outlook/$REPO.git") ;;
    *) echo "Noncanonical origin: $REPO" >&2; exit 2 ;;
  esac
  case "$REPO" in
    hybridclr_demo) EXPECTED="$EXPECTED_DEMO_COMMIT" ;;
    hybridclr) EXPECTED=4b2774b066cfc6afd77a8c8aded6bda7ea574f55 ;;
    hybridclr_unity) EXPECTED=948c0e3b4f8891481301770115e8ba4945eea6de ;;
    il2cpp_plus) EXPECTED=1cf87f8209790f9fb2ebec97487dc1990ccd56c5 ;;
  esac
  git -C "$ROOT" fetch origin "$BRANCH"
  test "$(git -C "$ROOT" rev-parse FETCH_HEAD)" = "$EXPECTED"
  git -C "$ROOT" merge --ff-only FETCH_HEAD
  test "$(git -C "$ROOT" rev-parse HEAD)" = "$EXPECTED"
done
git -C "$DEMO" merge-base --is-ancestor 357a9024865561362cd2c42fa8f793f56aac1763 "$EXPECTED_DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 357a9024865561362cd2c42fa8f793f56aac1763 "$EXPECTED_DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY" && test -x "$PYTHON"
"$PYTHON" -B -m unittest discover -s "$DEMO/Tools/AssemblyShadow/R03Storage" -p 'test_*.py' -v > "$PREFLIGHT/storage-tests.log" 2>&1
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Storage/run_storage_checked.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$CHECK"
```

Require the 48 storage tests to pass, with zero failures/errors/skips. Read `CHECK/admission.json`, its sizing formula, probes and filesystem/quota observations. If Blocked, stop before the execution block. Do not reclaim unspecified user data. After separately approved capacity remediation, diagnostics may run again only into a newly numbered unused CHECK directory; these are not batch retries and must remain preserved. If no safe capacity solution is available, return CapacityBlocked with the measured deficit and unresolved condition; no R invocation is authorized.

## Execute the admitted batch once

Only after the diagnostic prerequisite is satisfied and unresolved known filesystem constraints are addressed, run the following **once**. The wrapper independently repeats admission and immediately rechecks the full budget; it never consumes an old diagnostic pass as launch authority. An executing storage root is never reused. Do not fall back to calling `run_completion.py` directly.

```bash
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Storage/run_storage_checked.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$STORAGE" --execute
```

A blocked preconstruction admission has `batchStarted=false`, no new batch root and no new runtime result. Once construction/execution starts, do not rerun R, even if an early action fails. Preserve the original cell/command results and any partial outputs. All in-flight Unity/Player deadlines and process-lifetime rules remain the existing ones. Local may diagnose filesystem state, not change code, guards, thresholds, scope, timeout, warm-up, lease, quota or archive semantics.

## Required complete scope and evidence

When admitted, retain all **90 cells, six fresh builds, 59 fresh Player checks, 18-method preflight and 754/755 exact Editor rosters with zero skips/inconclusive**. Revalidate binding-before-integration, strict R02 bridge counts/raw custody, resource aggregate, codec context, physical measurement image/method/PDB checks, all five P01–P05 eligibility reports, live source/linked policy guards, and the fresh restored-baseline **zero changed roots/zero closure** proof. A previous Q/P subproof cannot substitute.

Keep the original ledger/result/index/archive/seal. Retain the entire storage sidecar separately: source-authority, admission/sizing/probes, capacity.jsonl, launch-intent, integration-allocation-probe, any failure files, session and dispatch. Preserve original stdout/stderr/Unity logs, the command 0126 equivalent, actual paths/devices, clocks and errno. The sampled minimum is not proof of the exact instantaneous peak. Telemetry overhead does not approve a performance SLA. Failed contaminated/unisolated warm certificates remain Failed.

Before making the publication copy, run the following read-only size/free-space check, retaining its new receipt. This does not alter the sealed core or storage-session results. If inadequate, do not start copying/packing; preserve the live evidence and return a small factual publication-capacity blocker rather than delete history.

```bash
PYTHONPATH="$DEMO/Tools/AssemblyShadow/R03Storage" "$PYTHON" -B - <<'PY'
import os
from pathlib import Path
import storage_guard as s
size = s.footprint(Path(os.environ['BATCH']))
required = max(s.FLOOR, size['planningBytes'] + s.MARGIN)
observation = s.sample({'publicationCheckout': Path(os.environ['DEMO']), 'retainedBatch': Path(os.environ['BATCH'])})
record = {'kind': 'R03StoragePublicationCheck', 'requiredBytes': required, 'size': size, 'observation': observation, 'state': 'Blocked'}
try:
    s.capacity_ok(observation, required)
    record['state'] = 'Passed'
finally:
    s.write_new(Path(os.environ['PREFLIGHT']) / 'storage-publication-check.json', record)
PY
```

Also check the actual Git common directory when it is on another filesystem; the executing admission records its canonical path. Do not add available space from APFS sibling volumes. The initial budget includes publication headroom but is not a guarantee against other writers or a larger R footprint.

## Verdict, publication and stop

Every original cell and seal must Pass; storage admission must be Admitted, storage session Passed, wrapper exit zero, and final source/custody checks Passed for **EvidenceReadyForPrimaryReview**. Otherwise return **ReturnRequired**, or **CapacityBlocked / batch NotRun** if construction never started. Do not rewrite core results to reflect the sidecar. Bind the sidecar hashes and command/source identities in the new Local publication receipt.

Update only Local-owned `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and a new immutable `local-validation-20261007-batch-r-*` checkpoint, including the complete storage sidecar/preflight evidence. Preserve all older checkpoints/reports. Commit/push through Local's normal transport, verify final four-repository heads/cleanliness, return to Primary and stop.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`; PureInterpreter expansion disabled. Independent full-stage review and human approval remain separate pending stages. R02 CPU, H1 RSS and contaminated warm-certificate risks remain visible.
