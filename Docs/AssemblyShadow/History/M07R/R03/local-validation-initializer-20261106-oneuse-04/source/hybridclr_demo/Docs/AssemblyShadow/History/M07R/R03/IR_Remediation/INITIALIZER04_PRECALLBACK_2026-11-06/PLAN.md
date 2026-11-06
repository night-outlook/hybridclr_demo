# R03 initializer oneuse-04 — bounded Local Validation execution plan

Read `DESIGN.md` and the current
`Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` first.
Date: 2026-11-06 UTC. Owner: Primary Implementation.
This plan addresses only `IR-LOCAL-R03-INITIALIZER-03-PRECALLBACK-01`,
not H2, a Human Review Gate, or R03 stage acceptance.

## P0 — source and historical custody (no writes)

Verify exact four independent canonical Git repositories, their
`codex/assembly-shadow-r01b-h1` branch and *latest final pushed*
commits in the Primary handoff prompt. All four clean local HEADs
must agree with the live remote and with the current 11+45 strict
source inventories. Do not substitute the earlier execution
`7a3b6c31408d8fd8b9fb5f74d78be4fa65670915` or published
evidence `ec753f2facb4b2645083ed969d40d541c9f03cf4`.

Read exact Local oneuse03 result, native journal raw and rejected
strict V1 observations. Preserve original S worktree and prior
oneuse-01/02/03 archives and host raw siblings, including all
literal symlinks; the existing oneuse03 seal PASS must not be
reclassified or rewritten.

## P1 — mandatory source-only/host CI

Require completed/success macOS15 and Ubuntu24.04 jobs at the
**same final pushed demo SHA** for BOTH:
- `r03-ir-initializer-local-contracts.yml`:
  Python strict recovery, phase journal and native writer host
  code, full source-prep/runner and prior admission negatives;
- `r03-ir-current-native-local-cycle-host.yml`:
  full real ten-component current-native host CLI, exact native
  source/checkout checks, all four adversarial symlink identities,
  full original host-byte custody and strict product evidence seal.

Also demand successful source-bound managed API compilation
`r03-ir-player-api.yml` with current
`R03InitializerObservationPlayer.cs` blob at the final commit
or a demonstrably identical source-bound successful preceding
source commit. The dedicated native writer host workflow
`r03-ir-initializer-writer-host.yml` must be successful for
the identical additive writer/driver/stub sources. Any failed/
cancelled/wrong-SHA or missing required CI result -> NO-GO.

## P2 — oneuse-04 distinct Mac read-only admission

Use these previously documented absolute paths:
~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261106-oneuse-04
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT=<40-char latest final pushed demo HEAD from Primary handoff>
~~~

RUN_ROOT and HOST_RAW must BOTH be absent, canonical, on the
same verified output parent and disjoint from all old roots,
Git repositories and original evidence. Check exact installed
Unity2022.3.62f2 macOS arm64, required compiler/SDK/dotnet,
no competing Unity/Bee/IL2CPP/Player processes and original-S
clean detached Git SHA `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
Take **two genuinely new, independent timestamped available-space
samples** on the exact shared volume, each >=25.0GiB, with
hard20GiB/advisory40GiB limits unchanged. This is a distinct
oneuse-04-only conditional 25-GiB exception, **not**
reapplication of 01/02/03 capacity data.

Run read-only admission **before creating** any root:
~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~
Any failure => BLOCKED and STOP; do not create roots or claim CI
as Unity execution.

## P3 — one run only: source-bound 15-cell initializer suite

After all gates GO, invoke exactly once:
~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Expect the same 15 fixed cells, one real ON/Release native
IL2CPP macOS arm64 Unity build and two separate real Players
from distinct OS PIDs. Preserve distinct deterministic
`initializer-control` and `initializer-failure` original
Methods.dll SHA/MVID; the new native recovery source has
NO fixture or public VM ABI change. Preserve ten native-host
component receipts and external raw negative symlinks, authenticated
regular host-byte custody, original nine-part S archive/90 cells/
59 process joins/generated-source/Mach-O audits and production
source-install/build provenance. All original 01/02/03
executions remain consumed.

## P4 — return all decisive native recovery observations

For **both** distinct Player requests retain:
- Pinned request/case/stimulus/run nonce/fixture SHA, actual full
  owned PID/process-group command receipt/exit/time/argv,
  Player.log and stdout/stderr SHA/size.
- Original strict `raw.json` bytes **even if empty**, with SHA.
  `raw.json.native-trace.jsonl` original full native phase
  journal and its typed verifier. Phase299/300 absence is a
  real negative; do not invent a callback success.
- New `raw.json.vm-recovery.json` full native original recovery
  JSON and SHA/typed producer/request/PID verification, or
  exact missing/partial/rejected receipt. Specifically report
  `nativeRecovery.reason` unmodified, `stateCode`,
  `terminalFailureCode` and `disposition`.
- Phase230 native getter result, phase231 managed return,
  phases190/191/201/205 (Commit/state), 299/300
  (prepublication callback), 400/401 (native pinned read),
  phase600–620 (strict Seal reason) and caught managed
  phase900. Preserve any native interpreter/PInvoke
  diagnostics, VM/native terminal guard and actual canary
  side-effect outcomes.
- If the control exits2 with error19, **do not** classify its
  first-recovery reason as an expected sentinel. If failure
  exits2 without callback or sentinel, classify
  NotRun_CommandFailed and report exact recovery reason.
  If actual callback reaches physical field3/mask15 and
  strict raw seals, validate both V1 and recovery/trace
  consistency; merely returning code19 is not sufficient.

Postflight verify all original/raw/host custody/hash/source
bindings, complete product archive membership and seal or
preserved `SEAL_FAILED.json`. A seal PASS does not prove
initializer/Player success. A failed Player with valid
recovery detail remains Failed. No retries/extra scenarios,
no manual replacement raw or local architecture refactor.

## P5 — factual publication, decisions and stop

Create one **additive** checkpoint under
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-04/`
without modifying consumed oneuse-01, oneuse-02 or oneuse-03.
Record exact execution source tuple versus post-publication SHA,
full immutable original raw/root path and separate host sibling,
source/build/provenance/custody/trace/recovery and seal hashes,
actual 15-cell status, matching successful host CI runs,
fresh capacity/version/preflight/preservation and
first-failure evidence. Local owns
`Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`;
commit/push and verify all four remote heads after publication.

Decision matrix:
- `reason` names a failure in original Prepare direct/delegate/
  generic, metadata or native PInvoke resolution: return
  exact exception + raw to Primary. Primary must implement the
  next source-level correction; do NOT edit runtime locally.
- `reason`/state/terminal inconsistent or unavailable:
  mark FAIL/Unavailable and return raw without assumptions.
- Both Players pass strict original V1 plus complete phase
  and first native recovery/sentinel, same exact build/fixture
  identity, host custody and seal: focused evidence ready
  for independent R03 review, **not** R03 acceptance.

All R03/H2/Human Review Gate, V2/global epoch/managed shutdown/
GC/RSS/captured-generic/RC/P/E/performance and original S
source/object/link/Player acceptance remain open.
`R03Accepted=false`, `H2Passed=false`,
`ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`, PureInterpreter disabled.
Stop after this batch and publication. No H2/M08A/X02/SNAP-01
or Human Review Gate self-approval.
