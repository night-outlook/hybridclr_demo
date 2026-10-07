# Primary Implementation → Local Validation: LR recovery, fresh batch S

## Assignment and preserved state

First audit retained R read-only, verify transport readiness and fresh storage admission. Only then execute exactly one new complete batch S. No non-trivial code/design changes, phase retries or old-root recovery are assigned to Local.

R remains ReturnRequired: 90 cells = 47 Passed / 1 Failed / 42 Blocked; six builds, 18/754 Editor cases and 23 focused Players completed. The 755 resource roster and remaining 36 Players are NotRun. Storage/seal Passed. Its failed restore and staged settings are immutable forensic evidence; do not run Unity against, restore, finalize, move or delete that retained project. Preserve Q/P/O/N, the earlier capacity-blocked R record and all historical certificates/results unchanged.

## Read and source authority

Read `README.md`, `Plan/CURRENT_STATUS.md`, Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, then `History/M07R/R03/LR_Recovery_2026-10-07/{DESIGN.md, PRIMARY_REVIEW.md, EVIDENCE.json}` and this assignment. Paths in this paragraph are relative to `Docs/AssemblyShadow/`.

All branches are `codex/assembly-shadow-r01b-h1`.

| Repository | Exact Local checkout | Required authority |
|---|---|---|
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Source/CI anchor `9f27feb647bbf2d2bc82483700fe4f78e5ea60be`; execute the final Docs-only descendant whose exact 40-character SHA is supplied in Primary's final prompt |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

The prior user-authorized agent configuration is retained in the new base; this assignment does not alter agent profiles, gate settings or require an invented effective model identity. Any unresolved ancillary gate observation remains explicit and distinct from runtime validation; do not label it Passed/Off or claim independent review. Both source-pin manifests, all C#/native/package code, fixtures, runtime expectations, timeouts, warm-up, leases and storage thresholds are unchanged. No smoke branch, including `codex/connector-smoke-lr-1fb504b2`, is product authority.

## Required repair checks

The new restore path performs all exact local source/project checks, authenticates captured state/backup, uses the unchanged Unity restore and exact-byte restoration, and only then checks fresh remote authority. The remote check is not bypassed for acceptance. If it fails after successful cleanup, `resource-p05-restore` remains Failed and dependents remain Blocked. Retain both facts, not an invented pass or staged-state inference.

Require `transaction-recovery/verification.json` with `cleanupResult=ExactOriginalBytesRestored`, `remoteAuthority=Passed`, stage Complete, exact before/original/after hashes and unchanged production restore receipts for a fully passing S. Retain `settings-before.bytes` and `local-authority.json`. Wrong local source, unsafe paths, changed backup/settings or malformed production receipts must still fail closed. No missing-state branch can substitute for required P05 coverage.

`git-observations/` records successful remote observations and Git failures with repo/argv/clocks, actual exit or timeout/spawn distinction, requested pins, hashes and bounded redacted excerpts. Do not enable raw Git credential tracing, republish secrets, or claim an unavailable original R transport cause was recovered. Local runtime results, cleanup state and fresh source authority are separate.

## Environment and unused locations

Keep Unity 2022.3.62f2, StandaloneOSX arm64, Python and SDK-only paths below; never launch Unity 6000. All new locations are under `/Users/ah/GitHub/hybridclr/r03-local-validation/`:

- `R03LocalBatch-20261007S-lr-recovery` — new core batch.
- `Preflight-R03LocalBatch-20261007S-lr-recovery` — command/publication evidence.
- `RetainedR-R03LocalBatch-20261007S-lr-recovery` — read-only retained-R audit.
- `Transport-R03LocalBatch-20261007S-lr-recovery` — four-owner readiness.
- `StorageCheck-R03LocalBatch-20261007S-lr-recovery` and `Storage-R03LocalBatch-20261007S-lr-recovery` — separate diagnostic/executing storage evidence.

No reuse of an existing output, reset/stash, unrelated merge, source/pin/protocol substitution, credential repair or capacity reclamation is authorized. A failed prerequisite returns PrerequisiteBlocked/TransportBlocked/CapacityBlocked with batch NotRun, rather than fabricating ninety runtime cells. A new attempt after operator remediation needs separate authorization and unused paths.

## Prepare, authenticate and diagnose

Set EXPECTED_DEMO_COMMIT to the exact final pushed SHA in Primary's prompt, not an inferred latest HEAD or the source anchor. Retain exact command/exit/clocks/streams in the new preflight directory. Never log origin credentials; require the canonical origin before network commands.

```bash
set -euo pipefail
: "${EXPECTED_DEMO_COMMIT:?Set the exact final SHA from Primary handoff}"
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BRANCH=codex/assembly-shadow-r01b-h1
export DEMO="$WORKSPACE/hybridclr_demo"
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
export BATCH="$BASE/R03LocalBatch-20261007S-lr-recovery"
export PREFLIGHT="$BASE/Preflight-R03LocalBatch-20261007S-lr-recovery"
AUDIT="$BASE/RetainedR-R03LocalBatch-20261007S-lr-recovery"
TRANSPORT="$BASE/Transport-R03LocalBatch-20261007S-lr-recovery"
CHECK="$BASE/StorageCheck-R03LocalBatch-20261007S-lr-recovery"
STORAGE="$BASE/Storage-R03LocalBatch-20261007S-lr-recovery"
R="$BASE/R03LocalBatch-20261007R-lq-storage"
Q="$BASE/R03LocalBatch-20261006Q-lp-repair"
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
export DOTNET_ROOT=/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk
export PATH="$DOTNET_ROOT:$PATH" DOTNET_MULTILEVEL_LOOKUP=0 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp
for DEST in "$BATCH" "$PREFLIGHT" "$AUDIT" "$TRANSPORT" "$CHECK" "$STORAGE"; do
  test ! -e "$DEST" && test ! -L "$DEST"
done
mkdir "$PREFLIGHT"
for REPO in hybridclr_demo hybridclr hybridclr_unity il2cpp_plus; do
  ROOT="$WORKSPACE/$REPO"
  test "$(git -C "$ROOT" rev-parse --show-toplevel)" = "$ROOT"
  test -z "$(git -C "$ROOT" status --porcelain=v1 --untracked-files=all)"
  test "$(git -C "$ROOT" branch --show-current)" = "$BRANCH"
  URL="$(git -C "$ROOT" remote get-url origin)"
  case "$URL" in
    "https://github.com/night-outlook/$REPO.git"|"https://github.com/night-outlook/$REPO"|"git@github.com:night-outlook/$REPO.git") ;;
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
git -C "$DEMO" merge-base --is-ancestor 9f27feb647bbf2d2bc82483700fe4f78e5ea60be "$EXPECTED_DEMO_COMMIT"
git -C "$DEMO" diff --exit-code 9f27feb647bbf2d2bc82483700fe4f78e5ea60be "$EXPECTED_DEMO_COMMIT" -- . ':!Docs/AssemblyShadow'
test "$(dotnet --version)" = 8.0.318
test -x "$UNITY" && test -x "$PYTHON"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/retained_transaction.py" --retained-r "$R" --output "$AUDIT"
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Completion/transport_preflight.py" --workspace "$WORKSPACE" --demo-commit "$EXPECTED_DEMO_COMMIT" --output "$TRANSPORT"
"$PYTHON" -B -m unittest discover -s "$DEMO/Tools/AssemblyShadow/R03Completion" -p 'test_lr_*.py' -v > "$PREFLIGHT/lr-tests.log" 2>&1
"$PYTHON" -B -m unittest discover -s "$DEMO/Tools/AssemblyShadow/R03Storage" -p 'test_*.py' -v > "$PREFLIGHT/storage-tests.log" 2>&1
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Storage/run_storage_checked.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$CHECK"
```

Require retained audit Passed/read-only/still staged, all four transport rows Passed, 45 LR and 48 storage tests Passed with zero skips/errors/failures, and diagnostic admission Admitted/session Passed. Retain Local's full historical custody map separately; six-file audit is not the full map. Capacity remains `max(64 GiB, 2*B+20 GiB)` per relevant location, operating floor20 GiB; no shared APFS capacity summing. Known unresolved filesystem/transport constraints must be addressed through operator authorization, not ignored because a probe passed. These are point-in-time observations, not a reservation or durable remote lease.

## Single executing invocation

Only after all prerequisites pass, invoke once. The storage wrapper independently rechecks exact source authority and fresh capacity/probes immediately before construction. Do not call the unguarded Completion entry directly.

```bash
"$PYTHON" -B "$DEMO/Tools/AssemblyShadow/R03Storage/run_storage_checked.py" \
  --workspace "$WORKSPACE" --output "$BATCH" --unity "$UNITY" \
  --demo-commit "$EXPECTED_DEMO_COMMIT" --retained-q "$Q" --storage-evidence "$STORAGE" --execute
```

Any failed started S is retained without phase/batch retry, even if cleanup succeeded. A failed local recovery check does not authorize copying a backup by hand. Original R remains unused. No non-trivial Local source edit is permitted.

## Complete evidence, publication and return

Retain all 90 cells, six fresh builds, all 59 Player checks, 18-method preflight and 754/755 exact zero-skip/inconclusive rosters. Required P05 coverage includes preparation/compile, local authenticated restore, unchanged production receipts, exact original byte restoration, fresh remote success and finalization. Require graph-before-integration, all five P01-P05 reports, live source/linked-policy guards, restored-baseline zero-root/zero-closure proof, strict R02 bridge counts/raw custody, resource aggregate, codec owner context and complete physical image/method/PDB measurement evidence. Prior focused or historical subproofs never replace missing S results.

Preserve the core ledger/result/index/archive/seal, new transaction-recovery and git-observations, full separate storage sidecar and preflight outputs. If evidence storage fails, record what is actually available, not a fabricated receipt. Keep cleanup and remote verdicts separate. Retain redacted diagnostics, not raw credentials; record the original transport failure as Unavailable where it remains so. The new tools add metadata/I/O overhead; no zero-cost or production-performance SLA is claimed.

Before copying/packing publication, require the unchanged footprint-plus20 GiB budget at checkout, live batch and actual Git common directory. This read-only check does not alter sealed verdicts:

```bash
PYTHONPATH="$DEMO/Tools/AssemblyShadow/R03Storage" "$PYTHON" -B - <<'PY'
import os, subprocess
from pathlib import Path
import storage_guard as s
batch=Path(os.environ['BATCH']);demo=Path(os.environ['DEMO'])
common=Path(subprocess.check_output(['git','-C',str(demo),'rev-parse','--git-common-dir'],text=True).strip())
common=(demo/common).resolve() if not common.is_absolute() else common.resolve()
size=s.footprint(batch);required=max(s.FLOOR,size['planningBytes']+s.MARGIN)
observation=s.sample({'publicationCheckout':demo,'retainedBatch':batch,'gitCommon':common})
record={'kind':'R03StoragePublicationCheck','requiredBytes':required,'size':size,'observation':observation,'state':'Blocked'}
try:
    s.capacity_ok(observation,required);record['state']='Passed'
finally:
    s.write_new(Path(os.environ['PREFLIGHT'])/'storage-publication-check.json',record)
PY
```

Insufficient publication capacity means preserve live evidence and report the blocker; no historical deletion is authorized. Reauthenticate retained R's six files/read-only state and the full historical custody map after S without rerunning or overwriting the initial audit output. All original90 cells and seal, storage admission/session, wrapper exit and final four-source/custody checks must Pass for EvidenceReadyForPrimaryReview. Otherwise ReturnRequired; before construction use the truthful batch-NotRun prerequisite result. Never promote original R or contaminated Failed unisolated warm certificates.

Update only Local-owned LOCAL_VALIDATION.md, RETURN_TO_WEB.md and a new immutable `local-validation-20261007-batch-s-*` checkpoint. Include exact commands, partial/failure diagnostics, original source versus publication commits and all sidecar bindings. Commit/push, verify four remote heads/cleanliness, return to Primary and stop. No later milestone, acceptance, quota change or independent-review claim is authorized. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Independent full-stage review and human approval, deferred R02 CPU/H1 RSS risks and production performance decisions remain pending.
