# Primary Implementation → Local Validation

## Objective

Validate the R01 failure/publication earliest-admission repair at candidate build-input source anchor:

`39c33e259d1ba893e23e3f1aa22529c87524534f`

Then continue the fresh H1 chain as far as safely possible in **one Local batch**: authority → provenance/builds → controlled/normal M07 → startup/M07 matrix → repaired failure/publication → independent remaining V04 coverage → retention → V05/M08 only if mandatory acceptance evidence is complete.

Local returns addressed by the current Primary state:

- failure/publication implementation return: `af0d345ce3aa7257e301926d0da652709c09cf54`;
- V00 handoff-section-contract return: `f8a2766d4ff8de3c6bb4d0900780ef0eccb48bbf`.

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**

## Source targets

Machine-readable authority: `Docs/AssemblyShadow/Handoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate build-input source | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `50c79913096961636a776ee8254b6631002cdfe5` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction behavior | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | source `4e3d2035991ab5629265ac663e61bcb2ca62828b`; published head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction validation tooling | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Performance reference | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Environment remains:

`Unity 2022.3.62f2 / StandaloneOSX / arm64`.

`ProjectSettings/AssemblyShadowSourcePins.json` and candidate `source-targets.json` now bind demo source to `39c33e25...`.

Checkout HEAD is a later metadata-only documentation/handoff successor. Record checkout HEAD and build-input source anchor separately.

All declared reproduction-tool blobs were rechecked against candidate anchor `50c79913...`; every expected blob still matches and both authenticated deletion paths remain absent.

## Implementation

### V00 handoff section-contract repair

Local correctly blocked before V01 because the committed handoff had drifted from `h1_handoff_preflight.py.REQUIRED_SECTIONS`.

The verifier was **not** changed.

The live handoff now contains these exact headings:

- `## Objective`
- `## Source targets`
- `## Implementation`
- `## Local validation`
- `## Failure evidence`
- `## Alternatives`
- `## Risks`
- `## Local correction boundary`
- `## Human review gate`

`Tools/AssemblyShadow/tests/test_h1_handoff_preflight.py` now runs `h1_handoff_preflight.verify()` against the actual committed repository checkout in addition to its disposable synthetic repositories.

The Primary CI workflow now:

- triggers when `WEB_TO_LOCAL.md`, `source-targets.json`, or `AssemblyShadowSourcePins.json` changes;
- checks out full Git history so the declared build-input anchor is resolvable;
- explicitly executes the committed-live-handoff preflight regression.

The blocked Local attempt at `f8a2766d...` remains `Blocked / V00`. It is not reusable or relabelled.

### Failure/publication implementation

### Failure returned by Local

The fresh `8b1298d...` Local cycle passed:

- candidate/reproduction authority;
- V01 compilation/tests;
- V02/V03 provenance/builds;
- controlled M07;
- normal M07;
- control capsules;
- startup11;
- M07 Player 14/14.

The separate R01 failure/publication matrix then failed **before host continuation** because `run-r01-failure-players.py` omitted the mandatory earliest-startup capsule transport. The Player's refusal was correct.

A second tooling defect existed: direct execution of `r01_failure_results.py` defined `main()` but did not invoke it.

### Repair design: Baseline early admission

The three failure/publication processes now use an early `Baseline` capsule.

This is deliberate:

- early `Control` would consume and commit the Shadow transaction before `R01FailureProbe`;
- early `MetadataFailure` / `InitializerFailure` would intentionally return non-zero and terminate before the host probe;
- early `Baseline` authenticates closure/prerequisite bytes, emits a successful early receipt, and performs no Shadow transaction.

The later `R01FailureProbe` therefore remains the sole owner of:

- P03 Control;
- Q04 metadata failure;
- initializer failure/publication.

No C#/native transaction semantics changed.

### Per-mode anti-substitution binding

Each process receives a deterministic `R01FailureEarlyAdmissionBinding` JSON containing its failure mode plus baseline/runtime/fixture/build/failure/negative-input/source identities.

That binding is a capsule prerequisite. Therefore the three Baseline capsules are byte-distinct and cannot be substituted across modes.

The capsule also binds the complete verified failure-fixture and Q04 negative-input file sets. Extra prerequisites already present as closure DLL/PDB inputs are deduplicated; bytes remain authenticated once, and the existing early callback's unique-path invariant remains intact.

### Launcher schema v2

`run-r01-failure-players.py` now:

1. prepares the verified failure input graph;
2. creates all three binding JSON files and Baseline capsules;
3. only then freezes `inputHashesBefore`;
4. launches each fresh Player with:
   - `-shadowEarlyCapsule`;
   - `-shadowEarlyCapsuleSha256`;
   - `-shadowEarlyResult`;
5. requires early `Passed`, callbackReturnCode 0, same PID, exact capsule path/hash;
6. requires the late failure/publication result from the same PID;
7. records hashes for binding, capsule, early result, late result, Unity log and console log;
8. requires the full immutable input graph unchanged afterward.

### Strict verifier schema v2

`r01_failure_results.verify_suite()` independently:

- reconstructs each expected per-mode binding;
- reconstructs each expected capsule from the verified current source inputs;
- verifies full immutable input before/after hashes;
- runs the existing strict `r01_early_results.verify_early_receipt()` for Baseline mode;
- binds early receipt to exact capsule and launch PID;
- verifies the exact executed command;
- binds the later result to the same PID;
- then runs the pre-existing strict failure/publication raw diagnostics/capacity/recovery/initializer oracle.

Missing, stale, substituted, mode-mismatched, rehashed-but-semantically-tampered inputs remain fail-closed.

`r01_failure_results.py` now also has a real module entrypoint.

## Primary testing

GitHub Actions workflow:

`35330989089`

at exact build-input source anchor:

`50c79913096961636a776ee8254b6631002cdfe5`

passed:

- bounded Primary suite: **311/311**;
- early-capsule suite: **7/7**;
- early-results suite: **19/19**;
- failure-pipeline suite: **16/16**.

CI artifact:

- ID: `10540898558`
- ZIP SHA-256: `52861f7bca634fa007e4e5fba7cd3774ab8f9dfbf1b39de0c6ca80fba047d139`

The failure-pipeline suite is actually executed as a script in this anchor and covers capsule absence/substitution/mode mismatch, same-PID early binding, duplicate prerequisite handling, exact command binding, raw/recovery/publication tampering, and direct verifier execution.

This is source/tool evidence, **not** real Player acceptance.

## Preserved evidence

Do not relabel prior checkpoints.

In particular:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authority8b/`

is valid historical evidence for source anchor `8b1298d...`: it passed through startup11 and M07 14/14 and captured the pre-host failure/publication refusal. It does not prove the new `50c79913...` chain.

MethodPtr/dense checkpoints remain under their original source identities and dispositions.

## Local validation

Canonical task list:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

### V00 — authority

Run fresh candidate handoff preflight and require:

- `SourceTargetVerifiedNotBuildAccepted`;
- candidate `codeCommit=50c79913096961636a776ee8254b6631002cdfe5`;
- exact unchanged runtime/package/IL2CPP pins.

Run exact reproduction-tooling preflight at `ba8fee33753a5ebc215b7a98739e343d8e05572e`.

**Hard stop** on authority, source-tree, protected-ref, or provenance mismatch.

### V01–V03 — source/build provenance

Run current H1 Python/source-authority tests and real Unity compilation required by the matrix.

Generate fresh source-pin/provenance/build evidence under `50c79913...`; do not promote `8b1298d...` build receipts to current acceptance.

### V04 — controlled + normal M07

Run a fresh controlled M07 authority/restoration case, then a separate fresh normal M07 baseline.

Keep the complete fresh fixture/build/replay graph live.

### V04 — startup + M07 matrix

Using the same fresh normal M07 graph:

- generate control capsules;
- run startup11;
- run M07 Player 14/14 with the matching early-capsule root.

### V04 — repaired failure/publication matrix

Generate/locate the fresh failure-fixture and Q04 negative-input receipts from that same chain.

Run:

~~~text
python3 Tools/AssemblyShadow/run-r01-failure-players.py   --project-root <candidate-root>   --fixture-manifest <m07-fixtures.json>   --on-build <native-on-m07-player-build.json>   --off-build <native-off-m07-player-build.json>   --replay-receipt <m07-editor-replay.json>   --failure-fixtures <r01-failure-fixtures.json>   --negative-input <q04-negative-input.json>   --output-root <new-direct-child-of-_temp/AssemblyShadow>
~~~

Then invoke the public verifier directly:

~~~text
python3 Tools/AssemblyShadow/verify-r01-failure-results.py   --launch-receipt <failure-output>/r01-failure-launches.json   --output <new-strict-verification.json>
~~~

Expected:

- launch receipt schema v2;
- three distinct per-mode binding files;
- three distinct Baseline admission capsules;
- early result `Passed` / callbackReturnCode 0 / exact same PID;
- late Control/Q04/initializer result from the same PID;
- strict `R01FailureVerification.result=Passed`.

The early Baseline callback must not perform a Shadow transaction.

### V04 — continue independent downstream tests in the same batch

After V00–normal-M07 source/provenance is valid, an isolated fresh-process functional failure does not by itself require abandoning all independent downstream tests.

Preserve the failure, then continue safe independent validations that use the same authenticated inputs, including:

- 8192/8193 capacity and mixed boundary;
- lazy/dense;
- generic/array/reflection/FieldRVA;
- immutable old-Player rejection;
- required retained M03–M07 native/runtime coverage;
- controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.

Do **not** continue when the failure indicates shared source/provenance corruption, unsafe working-tree mutation, wrong runtime installation, or invalid common input identity.

No failed prerequisite may be promoted to acceptance.

## Mandatory evidence retention

Before cleanup or V05, authenticate a new Local checkpoint.

Retain or hash-bind:

- V00 authority outputs;
- current source pin bytes;
- V02/V03 build/provenance receipts;
- controlled M07 mutation + restoration;
- normal `m07-build-workflow.json`;
- `m07-fixtures.json`;
- Native-ON/OFF `m07-player-build.json`;
- `m07-editor-replay.json`;
- control capsules/startup11;
- M07 14-mode results;
- failure fixture + Q04 negative input;
- three failure admission bindings/capsules/early receipts/late results/logs;
- capacity/lazy/dense/retained coverage/performance artifacts.

Do not delete/consolidate the live artifact roots before the checkpoint archive/index is authenticated.

Missing evidence is `Unavailable`; never reconstruct acceptance from summaries.

## V05 / M08

Proceed to V05 only if all mandatory acceptance prerequisites are satisfied.

Build/authenticate the successor package and commission a **genuine independent whole-chain M08** review.

Only M08 PASS may make H1 **Ready for Human Review Gate**. Then stop for explicit human H1 approval.

## Failure evidence

For the repaired failure matrix, retain per mode:

- binding JSON + SHA-256;
- capsule + SHA-256;
- early receipt + SHA-256;
- late result + raw evidence;
- exact command;
- PID/start time;
- Unity log + console log;
- immutable before/after input hashes;
- public strict-verifier result.

For any source/provenance failure, retain the exact first path/hash/commit mismatch and stop.

Keep `Passed`, `PassedFocused`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, `NoCoverage`, and historical/reused-audited evidence distinct.

## Risks

- The repaired failure/publication path is Primary-tested but still requires real Unity/IL2CPP Player validation under source anchor `50c79913096961636a776ee8254b6631002cdfe5`.
- Source-pin advancement means prior `8b1298d...` Player/build evidence remains historical comparison only; it must not be promoted to current-anchor acceptance.
- M07 and downstream outputs remain cleanup-sensitive. Authenticate the Local checkpoint before deleting, consolidating, or regenerating live artifact roots.
- An authority/provenance/shared-input mismatch invalidates downstream reuse and is a hard stop; isolated fresh-process functional failures may be preserved while independent cells continue only when common authenticated inputs remain intact.

## Alternatives

Local must not:

- move the source anchor;
- broaden `metadata_only`;
- weaken `verify_demo` or earliest-startup refusal;
- remove or bypass early capsule validation;
- replace Baseline admission with early Control/MetadataFailure/InitializerFailure;
- weaken exact command/PID/hash verification;
- alter runtime transaction/recovery/capacity semantics;
- change protected reproduction/performance pins;
- relabel historical evidence;
- begin R02.

Machine-specific paths, permissions, invocation syntax, and fresh output directories remain within bounded Local correction scope.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Local correction boundary

Local may correct machine-specific absolute paths, executable permissions, invocation syntax, and fresh output/evidence directories.

Local must not change source authority, required handoff headings, metadata-only classification, protected pins, earliest-startup admission semantics, exact command/PID/hash verification, M07 mutable-path policy, runtime transaction/recovery/capacity semantics, or performance methodology.

If a real run requires a non-trivial source/tool change, preserve evidence and return to Primary rather than widening the contract locally.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Fresh current-anchor mandatory V00–V05 evidence and a genuine independent whole-chain **M08 PASS** are required before **Ready for Human Review Gate**.

Human H1 approval must then be explicit.

**Do not begin R02.**
