# Primary Implementation -> Local Validation — CONDITIONAL / initializer oneuse-02 admission recovery (2026-11-05 UTC)

**Replaces only the live one-use authority.** The preceding initializer
**oneuse-01 is BLOCKED / all 15 cells NotRun**, at actual source
`bf1e8283061fe3a94c56ea2ac9ab6445905cf738`; its read-only
Mac admission exited 2 because the reviewed fixture project gained
one initializer source without updating the strict old Git blob pin.
That original evidence and [Local checkpoint](../History/M07R/R03/local-validation-initializer-20261105-oneuse-01/README.md)
remain immutable, even though oneuse-01's runner root was never created.
**Do not retry or reuse the original oneuse-01 path.**

The admission has been corrected by Primary on source commit
`b24e51ec074c7b3f9c7f7d86584c873f38dc2387`: the new exact
`PlayerFixtures.csproj`, initializer fixture producer and generator
entry source are pinned by verified Git blob and exact compile inclusion.
Read [recovery design and plan](../History/M07R/R03/IR_Remediation/INITIALIZER02_ADMISSION_RECOVERY_2026-11-05/DESIGN_AND_PLAN.md)
before any local action. **A current successful admission remains necessary;
do not reuse oneuse-01's 25-GiB capacity receipts or CI from earlier SHAs.**

**One new narrowly bounded authority:** `R03IR-Initializer-20261105-oneuse-02`
is authorized **only after** all gates below pass. It is distinct from the
consumed oneuse-K and earlier I/J/G/H cycles. Do not rerun, modify, delete or
rewrite those executions or historical S evidence. No automatic H2/M08A/X02,
Human Review Gate or production qualification.

## 1. Objective and source authority

Produce one new real Unity 2022.3.62f2 macOS ARM64 IL2CPP
**ON/Release build**, two independent initializer-control/failure
native-Player observations, original-S archive/source/Mach-O read-only audits,
and complete retained host/source/process/build/receipt evidence.

Canonical branch for all four repositories: `codex/assembly-shadow-r01b-h1`.

| Canonical repository | Required branch and commit |
| --- | --- |
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1`, **exact latest pushed remote HEAD from the Primary final copyable handoff prompt**. Resolve and verify the full 40-character SHA against origin before any run. The original initializer implementation was committed at `81597899d1ba0f8d00e3fd5dfd8531f8fab40fe9` and the corrected exact-source admission implementation at `b24e51ec074c7b3f9c7f7d86584c873f38dc2387`; **neither replaces the latest final pushed handoff SHA** if there are later documentation commits. |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` @ `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` @ `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` @ `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Use the final Primary message's **latest pushed demo SHA** for the
`--demo-commit` argument, with clean local HEAD and actual `ls-remote` matching.
A committed Markdown file cannot contain its own future commit hash; do not
treat the earlier source implementation commit as the newly published HEAD.
Do not infer missing SHA from historical K, or run from a smoke branch.

Local repository paths (each an independent Git root):
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus`

Original S must be a distinct clean read-only checkout at demo
`fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.

## 2. Read order and published implementation

1. `Docs/AssemblyShadow/README.md`; this live handoff.
2. `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/INITIALIZER02_ADMISSION_RECOVERY_2026-11-05/DESIGN_AND_PLAN.md`
   for the verified local admission failure and strict source correction.
3. The earlier `PRIMARY_FOLLOWUP_2026-11-05/INITIALIZER_ONEUSE_DESIGN.md`
   and `INITIALIZER_ONEUSE_PLAN.md` for the unchanged 15-cell batch.
3. `Tools/AssemblyShadow/R03IR/run_initializer_local.py` and
   `test_initializer_local_orchestration.py`.
4. Existing `prepare_initializer_sources.py`,
   `verify_initializer_observation.py`, the two
   `PlayerProject/R03Initializer*.cpp` files,
   `PlayerProject/R03InitializerObservationPlayer.cs`,
   the deterministic `R03/PlayerFixtures/InitializerNativeTargetFixtures.cs`,
   and native+managed host tests.
5. Historical `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`,
   consumed K preservation/custody and the independent 2026-10-08 FAIL.
   Do not treat original S/K/J/I documents as current run instructions.

**Two mandatory exact-source CI workflows**, each with **two completed
successful macOS/Ubuntu jobs at the same final pushed demo HEAD**:
- `.github/workflows/r03-ir-initializer-local-contracts.yml` — strict
  initializer `.csproj`/producer/admission and native writer/observer suites.
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml` — full
  shared current-native source/host and actual retained-worktree admission
  contracts, including the new initializer regression.

At the intermediate corrected-source commit
`b24e51ec074c7b3f9c7f7d86584c873f38dc2387`, **both passed**:
[initializer 42012373589](https://github.com/night-outlook/hybridclr_demo/actions/runs/42012373589)
and [shared 42012373659](https://github.com/night-outlook/hybridclr_demo/actions/runs/42012373659).
**These do not substitute for fresh final-documentation-SHA CI or Local
Unity/IL2CPP/Player execution.** If either final SHA run is not success
on both OSes, STOP before any Local invocation.

Production/native repositories remain unchanged. The new composite observer
and writer are **only test overlay** sources. K's five-Player runner is
unchanged.

## 3. Strict single-use admission (NO-GO does not create root)

Expected actual paths:
~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261105-oneuse-02
# Paste DEMO_COMMIT from the FINAL Primary handoff prompt (not the earlier
# oneuse-01 source commit, and not the intermediate admission source commit).
# This is a new absent root. Never reuse /oneuse-01.
~~~

Require all four clean Git roots, canonical origin/branch/live SHA, original S
unchanged and preserved, installed pinned Unity/IL2CPP/SDK, no conflicting
Unity/Bee/Player processes or active evidence mounts, exact source/fixture
preservation and a genuinely absent external RUN_ROOT. Take two independent
**fresh, separately timed** free-space samples on RUN_ROOT's actual parent; both
must be >=25.0 GiB. The oneuse-01 measurements are consumed historical
evidence and must not be copied into oneuse-02's admission. At 25–<40 GiB record this new-cycle-only advisory
exception. Below 25.0 GiB: **Blocked/STOP**, no runner output root or Unity.
Hard20/advisory40 thresholds are otherwise unchanged.

Mandatory read-only preflight:
~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

If any preflight/CI/authority/capacity/preservation gate is not passed,
report Blocked and stop, without an attempt to "repair" the environment by
mutating protected sources or old evidence. Record original return codes,
measured volume, receipts and reason.

## 4. One execution after GO; no replay

Execute exactly once:
~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

The unchanged runner itself enforces 15 fixed cells and rechecks source
authority; the corrected strict read-only admission runs first. The 01
preflight was BLOCKED, so neither the 01 root nor any 01 Player output
is a substitute for this entirely new source-bound run.
Before Unity it runs ten real K-current-native host components plus the new
C++11 observer/writer and Python negatives. It verifies original nine-part S
archive and its 59 original process joins, original generated tables and the two archived NativeOn/Off Mach-O
symbols; produces separately pinned Methods DLLs; prepares the new source
overlay; performs one actual ON/Release build and two distinct fresh Players.

Expected focused outcomes: control Commit 0/state 6 and failure
Commit 19/state 9, exact callback once, prepared/final native field 3,
positive mask 15, canary stays 1; the failure's postterminal AOT call must
be attempted and denied. Compare raw/request/PID/fixture/BuildReport and
native installed overlay bytes; preserve every exception and command log.
A successful schema-only V1 check is **not** a full native V2 snapshot.

Do not rerun the same root, replace raw output or construct synthetic Unity
evidence. Failures return `ReturnRequired` with any independently completed
cells retained. Avoid unrelated edits. Local may only make a trivially
bounded, immediately closed-loop verifiable local unblocker and must publish
the diff; all non-trivial code/native/build design changes return to Primary.

## 5. Evidence publication and scope boundary

Expected output locations:
- `RUN_ROOT/ADMISSION.json` and the Local Agent's two independent capacity
  samples / SDK / Git / original-S preservation reports.
- `RUN_ROOT/native-host-diagnostics/RESULT.json`, `RUN_ROOT/commands/`,
  `RUN_ROOT/cells/`, `RUN_ROOT/original-s-provenance/`,
  `RUN_ROOT/original-s-generated_material.json` and
  `RUN_ROOT/original-s-binary_linkage.json`.
- `RUN_ROOT/host/initializer-native-targets/`,
  `RUN_ROOT/initializer-source/SOURCE_PREPARATION.json`,
  `RUN_ROOT/builds/candidate-release/build-receipt.json` and Editor/Bee logs.
- `RUN_ROOT/players/IR-R03-02-initializer-{control,failure}/` including
  request.json, raw.json, Player.log, verification.json and command PID.
- `RUN_ROOT/BATCH_EXECUTION.json`, `LOCAL_BATCH_RESULT.json`,
  `evidence-index.json`, `evidence.tar.gz`, `seal-receipt.json`.

Publish one **new** additive checkpoint under
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261105-oneuse-02/`,
preserving `local-validation-initializer-20261105-oneuse-01`
verbatim and separately classifying its prior BLOCKED / NotRun result
and update Local-owned `Handoff/LOCAL_VALIDATION.md` and
`Handoff/RETURN_TO_WEB.md` with **actual** executed source/published evidence
SHAs, command transcripts, full raw evidence and every Pass/Fail/Blocked/
NotRun status. Commit/push, verify its remote head and report back to Primary.
Do not overwrite any historic checkpoint.

Still **NotRun / NotProven** after this narrow batch:
captured-generic error 15, complete V2 native snapshot, full first-failure
and complete general diagnostics, original-S complete compiler/object/link/
Player semantic join, managed Unity shutdown, whole-VM epoch, GC/RSS and
RC1–RC6/P1/P2/E0/E1/P3 closure. Independent High IR-R03-01/02 remain open.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`, `qualificationApproved=false`,
`runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false` and
PureInterpreter disabled. The next Human Review Gate is NOT self-approved.
