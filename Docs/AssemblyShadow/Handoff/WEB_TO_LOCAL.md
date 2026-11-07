# Primary Implementation → Local Validation — CONDITIONAL initializer oneuse-07

Date 2026-11-07 UTC. **Only one fresh scoped R03 initializer validation.**
Current Primary source correction resolves the **missing generation input**
for interpreted `Cdecl int32()` ABI `Bi4`. The actual corrected
Unity Player has NOT run; this handoff never grants acceptance.

## Primary source-pin CI repair before this Local cycle

At **prior** demo source `b0469e46c4052ea986d4d92ad501ac020c032d5e`, the mandatory current-native-local-cycle-host run `42336107614` failed on **both** operating systems in read-only source admission, before executing the 8+2 native-host suites. The separate current-native source-only run `42336107652` also failed. Both reported that current `R03Build.cs` did not match its **stale pre-bridge** Git blob in the current-native candidate source gate. These are real failed CI outcomes, not evidence of a passing native-host cycle.

Primary corrected the *current candidate* `R03Build.cs` Git blob from `b993703d918090733a659bd7c3ac883cd5d753e1` to the actual reviewed initializer-only builder `71c685f419d157bf3774996f28f2d075246cf4e4` in `current_native_source_gate.py` and `current_native_candidate.json`, with current-source and stale-pin-negative regression checks in `current_native_source_contracts.py`. The historical R03 pins and native forks are unchanged. Details: `History/M07R/R03/IR_Remediation/INITIALIZER07_BRIDGE_2026-11-07/SOURCE_PIN_CI_REMEDIATION_2026-11-07.md`.

**Do not use the prior failed runs or prior green workflows as final-source evidence.** Require all three workflow names below to complete successfully for macOS15 **and** Ubuntu24.04 at the exact *new final pushed demo SHA*, and inspect their actual job statuses. If the separate current-native source-only workflow fails again, record it as a blocker and return it to Primary. None of these checks authorizes bypassing fresh Mac admission or broadening the single 15-cell run.

## First reads and immutable evidence

Read `Docs/AssemblyShadow/README.md` and THIS canonical
`Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` first, then:
1. `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/INITIALIZER07_BRIDGE_2026-11-07/DESIGN_AND_PLAN.md`
   and `PRIMARY_SOURCE_REVIEW.md`.
2. Actual test-only source and contracts:
   `Tools/AssemblyShadow/R03IR/PlayerProject/R03InitializerBridge.cs`,
   `PlayerProject/R03InitializerPreparedProbe.cpp`,
   `PlayerProject/R03InitializerObservationPlayer.cs`,
   `prepare_initializer_sources.py`,
   `run_initializer_local.py`,
   `verify_initializer_trace.py`,
   `Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs`,
   and `.github/workflows/r03-ir-initializer-bridge-host.yml`.
3. Local-owned `Handoff/RETURN_TO_WEB.md` and
   `Handoff/LOCAL_VALIDATION.md`, and original
   `History/M07R/R03/local-validation-initializer-20261107-oneuse-06/`.
   Read original `RUNTIME_FINDINGS.json` and
   `local-evidence/BRIDGE_FINDING.json`, original
   real Player requests/PIDs and returned exception.
4. The exact user-owned `storage-retirement-20261106-runtime17`
   checkpoint, all previous S/K/initializer01–05 and
   published historical custody restrictions.

Oneuse06 execution demo
`611ad2e45a92ebfbd07cb64238bf2f47b5aff626`,
Local published evidence at demo
`7ada3408a2a5f211a7acfdadd06c36a6c48e274c`.
Both original distinct Players exit2, before callback,
VM first error `NotSupportManaged2NativeFunctionMethod`,
strict raw empty. The captured generated
`MethodBridge.cpp` had only the null stub table.
One real Unity ON/Release build, ten native hosts, 47 tests,
original host custody/product seal passed **only** their
original scopes. No replay, repair, reseal or reinterpretation.

The exact original 17 user-authorized retired roots and 40
duplicate paths remain permanently `Unavailable`. The
historical strict-custody failure remains Blocked; do
not invent missing raw, rebuild old apps, skip unrelated
protected files or claim historical acceptance.

## Four exact source repositories

Common feature branch `codex/assembly-shadow-r01b-h1`.
All local roots are individually owned by Git:

| Repository | Local checkout | Required source commit |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **EXACT 40-char final published demo SHA in the closing Primary continuation prompt.** Verify both local clean HEAD and live remote. The committed document cannot embed its own later Git commit. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

The two original V2 Methods.dll fixtures and all original
S/K/input roles are unchanged:

| Mode | SHA256 | MVID |
| --- | --- | --- |
| `initializer-control` | `d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e` | `5bb6e17a-09b9-5b29-dac2-41d3519f76f4` |
| `initializer-failure` | `6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370` | `f61d7325-6d38-4640-5873-37371f587b16` |

Each is 2560 bytes, interpreted callback import
`__InternalDynamic` /`R03_IRW_OnPrepared`, Cdecl
static noargs int32. AOT managed `__Internal` imports
stay unchanged; the production global bridge generator
and native forks are unchanged.

## Three mandatory exact FINAL demo SHA CI gates

At the SAME pushed final demo SHA require
`completed/success` on **macOS15 and Ubuntu24.04**
for all three workflows below:
- `r03-ir-initializer-bridge-host.yml`: genuine
  .NET8/dnlib Methods fixture source, actual C#
  isolated bridge augmentation, C++11 compiled
  and invoked Bi4 function-pointer wrapper,
  negative reentry/fixture identity, and no
  Unity runtime claim.
- `r03-ir-initializer-local-contracts.yml`:
  15-cell coordinator source, original strict
  admission and V2 fixtures, test-only managed
  prebuild + native probe and writer, strict
  phase103/299/300, negatives and source tests.
- `r03-ir-current-native-local-cycle-host.yml`:
  genuine complete 8+2 current native-host CLI,
  four real adversarial host symlinks, full
  regular bytes and strict generic evidence seal.

Also require exact-source native observer/writer
compilation and managed Player PInvoke API
compilation. These may be from a prior CI
source commit only with independently verified
unchanged relevant source blobs and an actual
successful job. A failed/cancelled/skipped
or wrong-OS mandatory job is **NO-GO**.
CI (including real C++/C# host compiles) is
not an actual Unity/IL2CPP Player run.

The official pinned broader build-helper
CI previously compiled `R03Build.cs` against
official Unity2022.3.62f2 API successfully
but the separate old terminal Player compile
later failed on a missing dispatcher in that
independent test's source list. This is
recorded as a **workflow failure**, not
overridden or called success.

## Mandatory fresh Local admission before any output

~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
OUTPUT_PARENT=/Users/ah/GitHub/hybridclr/r03-local-validation
RUN_ROOT="$OUTPUT_PARENT/R03IR-Initializer-20261107-oneuse-07"
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT = exact FINAL pushed 40-char demo SHA in the Primary prompt.
~~~

Both RUN_ROOT and HOST_RAW must be **absent**, physically canonical
and on the original actual output volume, disjoint from sources,
original S, previous oneuse01–06, all historical evidence and
owner-retired paths. Do not substitute another mount/alias/TMPDIR.
Verify original-S clean separate registered detached Git worktree
at `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`,
four clean canonical Git heads + remote, exact installed
Unity2022.3.62f2 macOS arm64/IL2CPP, SDK/dotnet/compiler,
no competing Unity/Bee/Player, before-preservation of all
surviving source/SDK/custody and precise
owner-authorized retirement status.

Measure free bytes on the **real shared output parent**
twice independently, at separate timestamps at least
one minute apart: BOTH ≥`26,843,545,600 bytes` =
**25.0GiB**. Hard20GiB/advisory40GiB unchanged.
This conditional oneuse-07 25–40GiB allowance
is not an exception to the >=25 minimum and
does not permit other cleanup. Historical
capacity samples are not transferable.

Run strict read-only admission **before** creating either root:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

If ANY Git/CI/machine/preservation/retirement/capacity
or absence gate fails: BLOCKED, STOP, **no runner**.
Do not assume old retired data was rehydrated,
and do not fabricate a product ledger.

## ONE 15-cell execution after actual GO

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Exactly one fresh ON/diagnostics2/Release macOS ARM64
Unity IL2CPP build and two distinct real native Players.
No replay, manual altered bridge, unverified DLL
substitution, extra host stimuli, or Local large fixes.

**Actual BuildReceipt requirements:**
ordinary Prebuild codegen occurs first; only the
source-authenticated isolated helper adds one
`Bi4` entry to the generated
`g_managed2NativeFunctionPointerCallStub` table,
with exact Cdecl noargs int32 wrapper and
null terminator. Source SHA before/after and
after BuildPipeline must match, all source
and fixture SHA/MVIDs bind, no hot-update
role changes. Actual GameAssembly.dylib
must contain the table identity and export
`R03_IRW_BridgeStatus` and
`R03_IRW_OnPrepared`. Native link/export
checks alone are insufficient.

**Actual EACH Player requirement:**
before committing any assembly, real AOT
`R03_IRW_BridgeStatus` inspects the actual
compiled native table: phase103 must
be 1 (exact one Bi4, nonnull function).
Only then can the real interpreted callback
enter phase299 and return phase300.
Healthy control must have Commit0/state6;
failure must have Commit19/state9 only
AFTER authentic callback, with exact
`R03IR.InitializerFailure.AfterPublication.V1`
original native first-recovery reason.
Real native pinned field3, pre-positive
mask15, exactly one callback, pre/post
AOT canary1→1, denied postterminal AOT.
Preserve raw V1 `raw.json` even if zero,
native phase `raw.json.native-trace.jsonl`
and `raw.json.vm-recovery.json`
plus full exact request, OS PID, exit,
stdout/stderr/Player.log, build receipt,
target SHA and MVID. A nonzero exit
remains `NotRun_CommandFailed`; do not
reinterpret diagnostics as semantic success.
New missing entry or later failure
must be preserved and returned to Primary.

Keep all ten host components, full raw sibling
with four adversarial symlinks, exact
literal target/regular byte custody,
strict product index/archive/seal or original
failed seal, original S archived-identity
nine-part/90-cell/59-process/Mach-O audit,
and independently proved before/after
surviving source/SDK/custody.

## Additive checkpoint and stop

After one run (even FAIL), publish
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-07/`,
full original raw/logs/receipts, exact
execution SHA vs evidence-publication SHA,
new live Bi4 phase103, correct field/callback
and terminal outcomes, complete 15-cell status,
strict host custody, product seal,
historical owner-retired Unavailable status,
before/after source/SDK/custody findings.
Update Local-owned `Handoff/LOCAL_VALIDATION.md`
and `Handoff/RETURN_TO_WEB.md`, commit/push
and verify four remote HEADs, then STOP.
No retry, Human Review Gate self-approval,
H2/M08A/X02/SNAP-01 or broader milestone.

## Immutable acceptance boundary

R03 independent High `IR-R03-01/02` remain
open. Captured-generic error15, complete
native V2/general first-recovery, original
S full compiler/object/link/Player evidence,
whole VM epoch, managed shutdown, GC/RSS,
RC/P/E/performance/full legacy regression
are unaccepted. `R03Accepted=false`;
`H2Passed=false`;
`ReadyForHumanReviewGate=false`;
`runtimeAcceptance=false`;
`qualificationApproved=false`;
`fullLegacyRegressionAcceptance=false`.
PureInterpreter disabled.
