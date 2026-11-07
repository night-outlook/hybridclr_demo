# Primary Implementation -> Local Validation — CONDITIONAL R03 initializer oneuse-06

Date 2026-11-07 UTC. **Fresh authority for import-contract validation only.**
The oneuse-05 input and observed FAIL are consumed; the generated control
and failure DLLs have now changed, with new exact SHA256/MVID pins.
Never retry/reseal/replace oneuse-05 or relabel its actual
`dlopen(__Internal)` failure. No User/Human Review Gate authorization
or R03/H2 acceptance is claimed.

## First reads / scope

Read `Docs/AssemblyShadow/README.md` and this canonical
`Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` first. Then:

- `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/INITIALIZER06_DYNAMIC_IMPORT_2026-11-07/DESIGN_AND_PLAN.md`,
  `PRIMARY_SOURCE_REVIEW.md` and historical consumed oneuse-05 handoff.
- `Tools/AssemblyShadow/R03/PlayerFixtures/InitializerNativeTargetFixtures.cs`,
  `Tools/AssemblyShadow/R03IR/run_initializer_local.py`,
  `current_native_environment_admission.py`,
  `test_initializer_local_orchestration.py` and
  `.github/workflows/r03-ir-initializer-dynamic-targets.yml`.
- Local-owned `Handoff/RETURN_TO_WEB.md`, `Handoff/LOCAL_VALIDATION.md`,
  the original `History/M07R/R03/local-validation-initializer-20261106-oneuse-05/`
  actual native recovery and original Player request/PIDs/seal,
  the owner-authorized retirement record
  `History/M07R/R03/storage-retirement-20261106-runtime17/`
  and the earlier oneuse-01–04 checkpoints.

Prior actual source demo
`db232418adf2fc35c54ed72a8933a174f8218126`,
Local publication demo
`eeeec3ba574047c06b5b853e58a5b594e80c37ae`.
Actual both Players exit2, strict V1 empty, no phase299 native callback,
both VM recovery reasons reported
`Unable to load DLL '__Internal'` with named `dlopen(__Internal)`.
One build, ten native host components, 46 tests and host/product
seal passed within their recorded scopes only.
Previous archived actual results are immutable.

## Exact four source repositories

Feature branch for each: `codex/assembly-shadow-r01b-h1`.
Each root owns its own Git repository. Canonical local workspace:
`/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.

| Repo | Absolute root under workspace | Exact source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `hybridclr_demo` | **The exact final pushed 40-character commit in the closing Primary handoff prompt.** Independently check clean checkout and live remote. The committed document cannot name its own yet-to-be-committed SHA. |
| `night-outlook/hybridclr` | `hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Demo's current opt-in fixture producer Git blob is source-pinned by
`current_native_environment_admission.py`. It emits ONLY two
separate v2 targets, exact interpreted import
`ModuleRef "__InternalDynamic"`, no-arg int32 Cdecl NoMangle
entry `R03_IRW_OnPrepared`, same original ordered initialization.
This does not change production `PlatformInvoke.cpp` or
AOT managed DllImport. The strict generator checks
reject the retired `__Internal` import.

**Authenticated actual .NET8/dnlib V2 target identities:**

| Mode | Exact SHA256 | Exact MVID | Bytes |
| --- | --- | --- | ---: |
| `initializer-control` | `d6e5b66f695498a9ba0806ea81930f03804d98f77382cb851d24c2b24f24202e` | `5bb6e17a-09b9-5b29-dac2-41d3519f76f4` | 2560 |
| `initializer-failure` | `6ad097153da2054579c13ec48d9f81a35d2551b08bf7a77398f13809ef9e5370` | `f61d7325-6d38-4640-5873-37371f587b16` | 2560 |

Both outputs independently generated twice on macOS15 and Ubuntu24.04
and compared to the same pinned native code; future Local generator
must reproduce both exact SHA/MVIDs or STOP. Do not substitute the
consumed v1 targets, old fixture receipts, new project-generated
arbitrary hashes or a source-only positive verdict.

## Mandatory exact-FINAL-source CI before ANY Local run

Require completed SUCCESS macOS15 **and** Ubuntu24.04 jobs, on
the SAME final pushed demo SHA, for **all three**:
- `.github/workflows/r03-ir-initializer-dynamic-targets.yml` —
  actual .NET8 generator, two independent runs per OS, source-pinned
  native `PlatformInvoke/LibraryLoader/TransformContext` authority,
  V2 emitted IL, exact per-mode SHA/MVID and legacy import reject.
- `.github/workflows/r03-ir-initializer-local-contracts.yml` —
  read-only fixture-source admission, synthetic 15-cell
  orchestrator, C++11 native reader/writer, strict original V1
  and native VM recovery diagnostics/negative mutations.
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml` —
  real 8+2 current native host CLI, four adversarial
  symlink metadata + all regular bytes custody, full
  original product evidence seal.

Also verify the dedicated native writer host and managed Player API
compile on the same source blob inputs (or current final SHA).
No success of an earlier source-only CI overrides a missing,
cancelled, failed, skipped or wrong-OS final-source mandatory job.
**CI is not a real Unity or interpreter Player.**

## Fresh local macOS admission / capacity

Use exact old registered Original S, unmodified:
`/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`,
clean detached `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
The user-approved 17 owner-retired runtime roots and 40 named
duplicate paths remain `Unavailable/PermanentlyDeleted_UserAuthorized`.
Validate the original approved scope metadata and all remaining
protected source/SDK/evidence bytes. **Do not** recreate, rehash as
Present, substitute, or automatically restore deleted artifacts.
Strict historical custody remains Blocked; it is not a new
permission to omit other protected files.

~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
OUTPUT_PARENT=/Users/ah/GitHub/hybridclr/r03-local-validation
RUN_ROOT="$OUTPUT_PARENT/R03IR-Initializer-20261107-oneuse-06"
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT = 40-character FINAL pushed demo SHA from Primary handoff.
~~~

Both roots must be absent, physically canonical, on the exact output
volume, distinct from every prior oneuse root and all sources/evidence.
Require four clean HEADs vs live remotes; actual
Unity2022.3.62f2 arm64/IL2CPP compiler/dotnet/SDK;
no competing Unity/Bee/Players; preservation of all nonretired
historical evidence and original S; **two genuinely fresh**
separately timed available-space measurements BOTH >=25.0GiB
(26,843,545,600 bytes) on the real same-volume parent.
The original hard 20GiB / advisory 40GiB and conditional
25–<40GiB oneuse-specific exception are unchanged.
No reuse of oneuse-05 capacity, other volume, symlink, TMPDIR
workaround, broad cleanup or unauthorized deletion. Stop if
either sample fails. Local may run read-only
`capacity_readiness.py` but a single successful probe is
not a batch authorization.

Run the strict read-only admission before creating either root:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Additionally require HOST_RAW absent and retained owner-retirement
scope / nonretired historical custody independently rechecked.
If any gate fails: BLOCKED/STOP; do not invoke batch or fabricate
a Player, evidence index or seal.

## ONE authorized full initializer batch after GO

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Exactly **one** fresh 15-cell batch, ten native host components,
one macOS ON/Release Unity IL2CPP Player build and two separate
fresh `initializer-control` and `initializer-failure` Players with
different PID/nonces and respective new authenticated V2 targets.
No retry, alternate fixture, extra stimulation or Local non-trivial
source edit after failure. Preserve identical original-S archived
9-part/90-cell/59-join/lexical/Mach-O checks only in their original
archived-identity scope, all surviving source/SDK/custody evidence,
and external host raw four symlinks with authenticated byte/archive
and strict product seal.

Preserve for BOTH Players unmodified:
`request.json`, actual OS PID command/argv/exit/streams/Player.log,
new target DLL raw SHA/MVID/producer receipt/build/overlay/executable
hashes, original strict `raw.json` even if empty, complete
`raw.json.native-trace.jsonl`, and exact
`raw.json.vm-recovery.json` native terminal reason. Authenticate
phase299/300 native callback entry/outcome, pinned field3/mask15
and exactly one invocation, control Commit0/state6,
failure Commit19/state9 **only after** real callback and the
precise sentinel
`R03IR.InitializerFailure.AfterPublication.V1`, canary1→1 and
denied postterminal AOT call. Wrong/missing source, callback,
bridge, symbol or another exception => FAIL with raw detail,
not success. Native V1 strict pass and full provenance required.
Product seal PASS alone does not imply Player PASS.

## Publication and stopping point

Create one additive
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261107-oneuse-06/`
checkpoint on the feature branch after the single run.
Include exact execution-vs-publication source tuple, independent
actual native importer/callback/first-failure evidence,
source/Unity build/Player receipts, 15-cell verdict,
original-S/custody/owner-retirement scope, exact host regular
bytes+4 links, seal and before/after preservation. Update Local-owned
`Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`,
commit/push and verify all four remote HEADs; STOP. Return
any new nontrivial issue to Primary Implementation, do not
self-approve the Human Review Gate or proceed to another milestone.

`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
High `IR-R03-01/02`, native V2/full diagnostics, captured-generic15,
original S source/object/link/Player closure, VM epoch,
managed shutdown, GC/RSS and RC/P/E remain outside this
focused validation and unaccepted.
