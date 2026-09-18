# Primary Implementation → Local Validation

## Objective

Resume H1 from Local return `476925a44613f09774de78f93c017e1a078838b0` after advancing the candidate source authority to the reviewed MethodPtr/dense build-input anchor.

Candidate build-input source anchor:

`8b1298d6a5979928bdfa30446e2d674d63999b76`

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.

## Source targets

Machine-readable authority: `Docs/AssemblyShadow/Handoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate build-input source | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `8b1298d6a5979928bdfa30446e2d674d63999b76` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction demo | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | published `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`; behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction validation tooling | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Performance reference | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains `2022.3.62f2 / StandaloneOSX / arm64`.

`ProjectSettings/AssemblyShadowSourcePins.json` now identifies candidate demo source `8b1298d...`.

Checkout HEAD is expected to be a later metadata-only handoff/evidence successor. Record checkout HEAD and source anchor separately.

## Implementation

### Candidate source-authority repair

The previous candidate source anchor `68df00fe31a199491b313cc17f25575663b7452b` did not include the MethodPtr and deterministic dense-v2 build-input changes.

Primary advanced only the authority metadata:

- `ProjectSettings/AssemblyShadowSourcePins.json` → `8b1298d...`;
- candidate `codeCommit` / `implementationCommit` in `source-targets.json` → `8b1298d...`;
- reproduction `candidateToolSourceAnchor` → `8b1298d...`.

No change was made to:

- `shadow_tools.metadata_only()`;
- `shadow_tools.verify_demo()`;
- `h1_handoff_preflight.py` acceptance semantics;
- M07 three-path workflow authority;
- protected reproduction behavior/tooling/runtime pins;
- performance-reference pin.

Remote structural review confirms that all changes after `8b1298d...` are already-authorized metadata-only paths: the exact live handoff authorities, `ProjectSettings/AssemblyShadowSourcePins.json`, plan/status/history/evidence under `Docs/AssemblyShadow/`.

The declared reproduction-tool files were rechecked at `8b1298d...`; all declared blobs still match their expected Git object IDs and both authenticated deletion paths remain absent.

### Focused findings already closed

Local checkpoint:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260917-methodptr-dense/`

remains valid for these exact focused claims because no build-input file changed after `8b1298d...`:

- M05 focused tests: 113 passed, one explicit environment-path skip;
- real retained Unity Bootstrap: `#-`, 1,675 MethodPtr / 1,675 MethodDef, complete permutation;
- five raw method witnesses passed;
- deterministic dense-v2 generation passed;
- native full corpus 8192, dense 2/2, bounded reader 13/13, sanitizer/provenance stability passed.

These are focused results only. They do not substitute for fresh source-pin/provenance, Unity/Player, capsule/startup, V04/V05, M08, or human approval.

### M07 receipt retention requirement

The previous complete M07 launch contract was removed during workspace consolidation. Do not reconstruct it from summaries.

The next normal M07 run must generate a fresh fixture/build/replay set and use it immediately for capsules/startup/downstream validation.

Before any cleanup or handback, the Local checkpoint must retain or explicitly hash-bind the complete new set, including:

- `m07-build-workflow.json`;
- `m07-fixtures.json`;
- exact Native-ON and Native-OFF `m07-player-build.json`;
- `m07-editor-replay.json`;
- failure/rejected fixture and negative-input receipts referenced by the current chain;
- control capsules and `capsules.json`;
- startup11 launch receipt/results/Unity logs/console logs;
- exact referenced Player/resource/fixture paths and hashes;
- post-run candidate source-authority/preflight result.

Do not remove or consolidate `_temp`, `Builds`, Player outputs, resource roots, fixture roots, replay scratch, capsules, or launch outputs until this checkpoint archive/index has been authenticated.

## Local validation

Use:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`

as the detailed run order.

### V00 — fresh authority

Run candidate preflight from the final handoff checkout:

`python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project <candidate-root> --role candidate --output <new-v00-output>`

Require `SourceTargetVerifiedNotBuildAccepted` and `codeCommit=8b1298d6a5979928bdfa30446e2d674d63999b76`.

Run the exact reproduction-tooling preflight at `ba8fee33753a5ebc215b7a98739e343d8e05572e` and verify protected refs.

Stop on V00 failure.

### V01–V03 — provenance

Do not rerun the closed MethodPtr/dense focused work solely for repetition. Reuse that checkpoint only for its exact focused claims.

Fresh source-pin/provenance evidence is still required because `AssemblyShadowSourcePins.json` changed. Execute the current H1 V01–V03 requirements and regenerate the required candidate/reproduction build set under the new source pin.

### V04 — controlled M07

Run a fresh controlled M07 baseline under the existing exact workflow-authority contract.

Require the expected explicit controlled failure only after the post-validation authority proof succeeds, then require exact restoration and a fresh candidate preflight.

### V04 — normal M07 + immediate downstream continuation

Use a separate new baseline ID and run normal M07:

`pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 -ProjectPath <candidate-root> -BaselineId <new-M07-baseline-id> -TimeoutSec 28800`

Require a successful `m07-build-workflow.json` with fresh fixture manifest, ON/OFF Player receipts and Editor replay.

Using those exact files, generate fresh control capsules:

`python3 Tools/AssemblyShadow/prepare-h1-m07-control-capsules.py --fixture-manifest <m07-fixtures.json> --on-build <NativeOn/m07-player-build.json> --off-build <NativeOff/m07-player-build.json> --replay-receipt <m07-editor-replay.json> --output-root <new-capsule-root>`

Then run startup11 via the existing `run-r01-early-players.py` contract using the fresh fixture/build/replay/capsule/failure/negative inputs. Do this before any cleanup.

If startup11 succeeds, continue the remaining blocked V04 chain: M07 Player matrix, capacity 8192/8193, lazy/dense/generic/array/reflection/FieldRVA/old-Player, retained M03–M07 coverage, and controlled Development performance as required.

### Retention checkpoint

Before V05 or any workspace cleanup, create the new Local checkpoint under `Docs/AssemblyShadow/History/M07R/H1/`, authenticate its `raw-evidence.tar.gz`/index/manifest, and confirm the complete current M07 fixture/build/replay/capsule/startup receipt set is present or explicitly hash-bound.

A missing required artifact is `Unavailable`, not reconstructed acceptance.

### V05

Proceed only from explicit fresh current-anchor evidence. Build/authenticate the successor evidence package and commission a genuine independent whole-chain M08 review.

## Failure evidence

For source-authority failure retain:

- final checkout HEAD;
- `source-targets.json` hash;
- `AssemblyShadowSourcePins.json` hash;
- exact preflight stdout/stderr;
- the first build-input path/blob difference;
- Git status and branch/remote state.

For M07 regeneration failure retain the last successful authority guard plus the exact workflow/run directory and stage logs.

For capsule/startup failure retain the exact fixture/build/replay/capsule hashes, failure/negative-input hashes, launch command, PID/start identity, Player result, console and Unity logs.

Keep `Passed`, `PassedFocused`, `Failed`, `Blocked`, `Unavailable`, `NotRun`, `NoCoverage`, and historical evidence identities distinct.

## Alternatives

Do not:

- move the candidate source anchor past `8b1298d...` locally;
- broaden `metadata_only`;
- weaken `verify_demo`;
- add source-path exceptions;
- reconstruct removed M07 receipts from summaries;
- relabel retained MethodPtr/dense focused evidence as fresh Player acceptance;
- relabel dense-v1 evidence;
- move protected reproduction/performance refs;
- begin R02.

If a real fresh run requires a new build-input change, preserve the evidence and return to Primary.

## Risks

The source-authority repair has been structurally verified against remote Git state but has not been executed by Primary in the real local checkout. Fresh V00 is therefore mandatory.

The normal M07 chain can again produce cleanup-prone outputs under `_temp` and `Builds`. The retention checkpoint is mandatory before cleanup.

Focused MethodPtr proof used a retained real Bootstrap DLL; full provenance-bound acceptance still requires the freshly regenerated current-anchor M07 chain.

## Local correction boundary

Local may correct machine-specific absolute paths, executable permissions, invocation syntax, and new evidence/output directories.

Local must not change architecture, source authority semantics, the source anchor, protected pins, M07 mutable-path policy, MethodPtr acceptance semantics, dense-v2 evidence identity, capacity/count behavior, or performance methodology.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress**.

Fresh current-anchor V00–V05 plus a genuine independent whole-chain **M08 PASS** are required before the state may become **Ready for Human Review Gate**.

Human H1 approval must then be explicit.

**Do not begin R02.**
