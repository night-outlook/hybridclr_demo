# Primary Implementation -> Local Validation — oneuse-05 capacity-readiness gate (2026-11-06 UTC)

**CONDITIONAL, NOT YET EXECUTION-READY.** The user's actual macOS volume
has not been remeasured since oneuse-04 returned CapacityBlocked.
No storage has been freed or removed by Primary and no new Unity/Player
execution has occurred. This document authorizes **read-only capacity
readiness first**, followed by **one** fresh initializer oneuse-05
batch only if every fresh source, machine, evidence, CI and free-space
gate below actually passes. Never interpret an inspector's exit 0,
a single sample, a candidate size or a CI PASS as Unity authorization.

## 1. Current finding and immutable historical evidence

`IR-LOCAL-R03-INITIALIZER-04-CAPACITY-01`: exact user Mac
`/Users/ah/GitHub/hybridclr/r03-local-validation` parent,
device16777230, had available `26,557,333,504` then
`26,553,147,392` bytes (24.733444 /24.729546 GiB) at
2026-11-06 07:40:41/07:41:43 UTC. The mandatory minimum is
**26,843,545,600 bytes =25.0GiB**; the latter measured deficit
is **290,398,208 bytes (~277MiB)**.
Both readings failed. The oneuse-04 new roots remain absent,
runner0, Unity0, build0, Players0 and 15/15 cells NotRun.
There is NO observed oneuse-04 VM recovery reason.
Read the immutable [oneuse04 finding](../History/M07R/R03/local-validation-initializer-20261106-oneuse-04/FINDING.json)
and [factual Local result](../History/M07R/R03/local-validation-initializer-20261106-oneuse-04/LOCAL_RESULT.json).
Do not rewrite/reseal/retry the consumed oneuse-04 or any
oneuse-01/02/03, K/I/J, original S or other historical record.

`R03Accepted=false`; `H2Passed=false`;
`ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`;
`qualificationApproved=false`; PureInterpreter disabled.

## 2. Sources and mandatory read order

Feature branch for ALL four repositories:
`codex/assembly-shadow-r01b-h1`.

| Repository | Owning local path | Required pushed source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | The **exact latest final pushed 40-char SHA** from the closing Primary prompt. Confirm clean local HEAD and live remote equality, not an earlier source/evidence commit. A committed Markdown file cannot contain its own future Git SHA. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Read:
1. `Docs/AssemblyShadow/README.md`; this current canonical
   `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`.
2. [Capacity readiness design and plan](../History/M07R/R03/IR_Remediation/INITIALIZER05_CAPACITY_2026-11-06/DESIGN_AND_PLAN.md)
   and associated `PRIMARY_SOURCE_REVIEW.md`.
3. `Tools/AssemblyShadow/R03IR/capacity_readiness.py` and
   `test_capacity_readiness.py` (read-only source-only tools).
4. Previous
   `History/M07R/R03/IR_Remediation/INITIALIZER04_PRECALLBACK_2026-11-06/DESIGN.md`,
   `PLAN.md`, `PRIMARY_SOURCE_REVIEW.md` and the unchanged
   `run_initializer_local.py`, native recovery observer and verifier.
5. `Handoff/RETURN_TO_WEB.md` and `Handoff/LOCAL_VALIDATION.md`,
   consumed oneuse-04 checkpoint, all protected S/K/prior
   runtime/SDK/custody inventory and the original R03 FAIL.

Original S stays a separate immutable clean checkout at
`/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`,
demo commit `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
No production VM/interpreter/Unity package/fixture DLL change.

## 3. Absolute NEXT roots — must remain absent until execution

~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
OUTPUT_PARENT=/Users/ah/GitHub/hybridclr/r03-local-validation
RUN_ROOT="$OUTPUT_PARENT/R03IR-Initializer-20261106-oneuse-05"
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT = final 40-char pushed demo SHA from Primary prompt.
~~~

`RUN_ROOT` and `HOST_RAW` must both be canonical, distinct,
nonexistent and disjoint from all source, original S and historical
evidence. Same actual output-parent volume; never redirect
TMPDIR, mount aliases or symlink a new parent to an alternate
device. Existing `R03IR-Initializer-20261106-oneuse-04`
remains a consumed BLOCKED name even though its root is absent.

## 4. Read-only readiness first — no automatic cleanup

The exact default command reports **ONE** actual fresh
independently timestamped capacity sample; it writes nothing:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/capacity_readiness.py" \
 --output-parent "$OUTPUT_PARENT" --run-root "$RUN_ROOT" \
 --host-raw-root "$HOST_RAW" --workspace "$WORKSPACE" \
 --original-s "$ORIGINAL_S" --unity "$UNITY_EXE"
~~~

Run it a SECOND time after a separate interval (at least one
minute) to obtain the second real sample; do not reuse stdout,
timestamps, OS measurements or earlier oneuse-04 readings.
Verify both `capacity.freeBytes >=26843545600`,
`result=ReadySingleSample_NotBatchAuthorized`,
same canonical output parent and actual st_dev, both roots
absent and independently authenticated current machine state.
**The inspector deliberately sets `eligibleForUnityRun=false`
even when one sample passes. Its process exit0 is NOT a GO.**

Optional `--candidate /absolute/path` performs read-only
aggregated inventory only for that EXPLICITLY selected path,
after protecting source/evidence/output parent, system paths,
Unity and every additional SDK/root passed via
`--protected-root /absolute/protected/path`. Candidate
logical/allocated size cannot prove reclaimable APFS space.
No candidate is identified or approved by Primary from
the existing Local evidence. **No deletion/move/purge/GC,
cache eviction, snapshot thinning, evidence relocation,
automatic clean-up or arbitrary disk repair is authorized.**
If storage is below25GiB, STOP and report the actual sample and
possible **unprotected** per-path options for a separate
explicit user approval. Only the user may independently create
space on the same volume after checking each data owner's intent;
Local must not clear any data without that decision and a
subsequent separately bounded procedure.

A several-GiB additional buffer (ideally >=32GiB) is recommended
for another Unity IL2CPP build; this is NOT a new hard or soft
threshold, not a promise and not authority to bypass:
- hard20GiB (unchanged),
- mandatory **two >=25GiB samples** (unchanged),
- ordinary advisory40GiB (unchanged);
- conditional 25–<40GiB oneuse-05 exception only, once actually
  measured and documented. No old below40 exception is reused.

Readiness-only probes may be repeated without creating or
consuming the oneuse-05 batch. If the first attempt remains
CapacityBlocked, publish only a read-only readiness report
and return; do NOT create either new root or fabricate a batch
ledger/seal. A user-managed real capacity increase or a future
explicit capacity action is required before next Local dispatch.

## 5. Mandatory source/CI/SDK gate before ANY oneuse-05 runner

At the same **final** pushed demo SHA, require completed/success
macOS15 and Ubuntu24.04 jobs for **ALL THREE**:
- `.github/workflows/r03-ir-capacity-readiness.yml`:
  actual read-only CLI on foreign cwd, 25GiB arithmetic, host
  path/symlink/SDK exclusion, negative no-write tests;
- `.github/workflows/r03-ir-initializer-local-contracts.yml`:
  real C++11 test-only native observer/writer and strict
  original VM-recovery parser/CLI source contracts;
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml`:
  real ten-component 8+2 pinned native host components, actual
  negative symlink custody, exact regular bytes and strict
  product-seal integration.

Also verify the dedicated native-writer host and source-bound
managed Player API compiles on byte-identical source inputs from
their successful recorded CI, or on the exact final SHA.
A wrong, missing, failed, cancelled, or skipped mandatory job is
NO-GO. No CI is a real Local Unity result.

Before executing the oneuse batch also verify actual
Unity2022.3.62f2 macOS ARM64 and SDK/compiler/.NET, no conflicting
Unity/Bee/Player, four clean live Git roots, immutable original S,
old 17+ historical checkpoints, historical external raw/host
inventories and all protected prior SDK files. Use the existing
actual independent read-only `current_native_environment_admission.py`
with exactly the new RUN_ROOT. Both new roots must STILL be absent.
At/after admission recheck actual available bytes are >=25GiB;
not a substitute for the two earlier distinct independent samples.
Any uncertainty or failure -> Blocked/STOP, no new batch root.

## 6. ONE scoped oneuse-05 execution only after GO

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Exactly the existing 15 cells, one genuine Unity ON/Release
macOS ARM64 IL2CPP build, two real initializer-control/failure
Players from distinct OS PIDs, ten real host components with
four real negative symlinks, complete host byte/link custody,
read-only original-S nine-part archive/90-cell/59-process
source+Mach-O identity audits, strict V1 native observation,
preopened phase journal, native VM `reason` capture,
request/PID/fixture/build/source checks and sealed product
evidence. No fixture, native runtime or acceptance predicate
change. No retry after an error, no reconstruction of a failed
product seal, and no Local nontrivial source changes.

Preserve full actual `raw.json` even if empty, original
`raw.json.native-trace.jsonl` and
`raw.json.vm-recovery.json` including exact VM first reason,
phase230/231 and real callback phase299/300 or absence,
physical field/mask/canary outcomes, native Seal reasons,
actual command PID/exit/Player.log, build/VM provenance and
the original full host custody/seal or explicit failure.
No semantic acceptance on nonzero Player exit; source-only
or host PASS does not upgrade original R03 acceptance.

## 7. Evidence publication and stop

If readiness remains Blocked: return only the actual
readiness samples/candidate inventory in a NEW additive
capacity-readiness checkpoint, without creating RUN_ROOT
or HOST_RAW or reusing oneuse-04; preserve old evidence
and request explicit user capacity action. Do not call it
a failed Unity cycle.

If the oneuse-05 batch actually starts: publish one new
checkpoint under
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-05/`
with exact source-vs-publication SHA, all original raw/logs,
fresh CI/capacity/SDK/custody evidence, 15-cell verdict,
source/build/Player/native recovery/host/seal audit and
independent before/after source/evidence preservation.
Update Local-owned `Handoff/LOCAL_VALIDATION.md` and
`Handoff/RETURN_TO_WEB.md`, commit/push, verify four live
remote HEADs, and return first new non-trivial failure
to Primary. If a gate has already failed after oneuse-05
is invoked, do not replay/reuse its root; mark it consumed.

The original oneuse-03 pre-callback failure is not yet
diagnosed. Independent High `IR-R03-01`/`IR-R03-02`,
captured-generic15, native V2/full first-failure/general
diagnostics, original S complete compiler/object/link/
Player join, managed shutdown, whole-VM epoch, GC/RSS,
RC/P/E, performance and full legacy acceptance remain open.
`R03Accepted=false`; `H2Passed=false`;
`ReadyForHumanReviewGate=false`;
`runtimeAcceptance=false`; `qualificationApproved=false`;
`fullLegacyRegressionAcceptance=false`. PureInterpreter
disabled; no H2/M08A/X02/SNAP-01 or Human Review Gate.
