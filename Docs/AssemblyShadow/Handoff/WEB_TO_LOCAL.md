# Primary Implementation → Local Validation

> Documentation and handoff paths were consolidated under `Docs/AssemblyShadow/` after the predecessor handoff. The implementation anchor and protected runtime/reproduction/performance pins remain unchanged.

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from Local Validation return commit:

`e053b1803b2dd94fa818714c4b79e53220f246b8`

Authoritative candidate source / implementation anchor:

`21d3d5763ce027185d2e7f777f71545d354d44ec`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

The previous Local cycle empirically passed V00–V03 and candidate count 132/132. It also proved that real `M07Build.ValidateCompilerInputs` succeeds and actually mutates the M07 bootstrap scene and AssemblyShadow settings. Both the controlled and normal M07 flows then failed closed at their next full source verifier because those intentional workflow-owned mutations no longer matched the immutable source-anchor blobs.

Primary repaired that authority conflict without changing M07 policy, native/runtime pins, provenance acceptance, or the three-file exact-restoration contract. The generic source verifier remains strict outside the M07 wrapper. During the wrapper only, repeated post-mutation guards combine exact installed-runtime/native/package verification with a separate exact M07 demo-source authority proof.

Run fresh **V00–V05**. Preserve the complete `local-validation-20260917-12cf9b2` checkpoint and all older evidence under their original source identities/dispositions; do not relabel them as current-anchor acceptance.

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`
- `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md`
- `Docs/AssemblyShadow/Handoff/source-targets.json`
- `Docs/AssemblyShadow/History/M07R/H1/latest-local/`
- `Docs/AssemblyShadow/History/M07R/H1/current-primary/`

Git is the authority. Do not apply unpublished patches or mutate protected branches/pins.

## Source targets

Machine-readable authority: `Docs/AssemblyShadow/Handoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `21d3d5763ce027185d2e7f777f71545d354d44ec` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction demo | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Unfixed reproduction behavior source | same history | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction validation tooling | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**.

`ProjectSettings/AssemblyShadowSourcePins.json` pins source anchor `21d3d576...`. The final branch HEAD is a later metadata-only handoff successor; record both checkout HEAD and source anchor.

## Implementation

### M07 post-validation authority split

The generic `shadow_tools.verify_demo()` contract is unchanged. Outside an M07 wrapper invocation, `verify-installed-runtime.py` still performs the same full demo-source verification as before.

`Invoke-M07Build.ps1` now creates its existing exact recovery root, snapshots the three recovery-owned inputs, then scopes these process variables for the controlled or normal M07 workflow lifetime:

- `H1_M07_WORKFLOW_AUTHORITY_ROOT` = exact recovery root;
- `H1_M07_WORKFLOW_BASELINE_ID` = exact requested fresh `M07-Baseline-*` identity.

The prior environment is restored/unset in the wrapper `finally` path.

When `verify-installed-runtime.py` is called inside this scoped context:

1. it first authenticates the three saved originals against source-anchor Git blobs;
2. before either required baseline-bound file changes, it runs the original full verifier unchanged;
3. after a required M07 mutation appears, it requires both:
   - generic installed-runtime/native/package/source-receipt verification with demo working-tree comparison internally skipped; and
   - `h1_m07_workflow_authority.py` exact demo authority.

The M07 demo authority requires:

- the source-anchor build-input tree still equals the committed current source tree;
- `AssemblyShadowSourcePins.json` working bytes match the final committed HEAD blob;
- every non-mutable demo build input still matches its exact source-anchor blob;
- no untracked build input or unpinned `.cs` / `.asmdef` exists;
- saved originals for exactly the three mutable paths match their source-anchor blobs;
- `M07Bootstrap.unity` and `ProjectSettings/AssemblyShadowSettings.asset` both differ from their originals and contain the exact requested baseline ID;
- `EditorBuildSettings.asset` may change or remain unchanged but is still recovery-owned.

The only mutable paths are:

1. `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`
2. `ProjectSettings/AssemblyShadowSettings.asset`
3. `ProjectSettings/EditorBuildSettings.asset`

There is no wildcard/directory allowance. Partial mutation, wrong baseline, immutable-source drift, backup tamper, extra code input, or caller-provided `--skip-demo-source` fails closed.

### Controlled and normal flow

Controlled flow still executes real Unity `M07Build.ValidateCompilerInputs`, then performs the new post-validation authority recheck. Only after that succeeds may it reach the exact deliberate failure:

`Controlled M07 failure after successful ValidateCompilerInputs for exact-byte restoration verification.`

The existing outer three-file exact restoration remains unchanged.

Normal flow still invokes the existing `Invoke-M07Build.Core.ps1`. The core was not relaxed and retains its repeated `Assert-M07PinnedInputs` checks after `ValidateCompilerInputs`, baseline resources, Native-ON Player, Native-OFF Player and later structural stages. Those calls now understand the exact authenticated M07 workflow state through the scoped wrapper context.

### Primary bounded validation

Source anchor `21d3d5763ce027185d2e7f777f71545d354d44ec` passed workflow `35195186054`:

- **311/311 Passed**;
- zero nonpasses;
- authenticated Apple Bee fixture SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`;
- artifact ID `10485926242`;
- artifact ZIP SHA-256 `d2486ad13ab52d41b5fcd19ce7902863c2ef8b242b1747ec9f9b1284402be9a5`.

This is bounded Primary/tool evidence only. It is not current-source Unity/Player/M07/runtime/performance acceptance, M08 PASS, or human approval.

## Local validation

Follow `Docs/AssemblyShadow/History/M07R/H1/current-primary/LOCAL_VALIDATION_TASKS.md`.

### V00 — authority

1. Pull the final candidate handoff HEAD; record checkout HEAD and source anchor `21d3d576...` separately.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Run split reproduction-tooling preflight at exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. Verify every protected reproduction/native/package/IL2CPP/performance identity remains exact.

Stop before V01–V05 on V00 failure.

### V01 — source / Unity regressions

Run the complete H1 Python inventory and exact bounded Primary suite, then compile candidate and reproduction-tooling checkouts in real Unity 2022.3.62f2. Run affected H1 Editor tests, including the M07 fixed-byte/bootstrap policy integration tests. Retain test inventories, raw logs and NUnit XML.

### V02 — fresh candidate provenance

Run a fresh candidate ON/Debug schema-3 normal-cache proof under source anchor `21d3d576...`. Preserve normal Bee cache and require strict native compiler/PCH/store/managed/fresh-Player/restoration controls. Do not substitute legacy prior-proof reuse.

### V03 — fresh six-build set

Use candidate-owned `h1_count_build_batch_tooling.py` and exact reproduction tooling to produce fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release. Require strict native+managed provenance, tooling bindings and exact restoration for every accepted build.

### V04 — fresh count + repaired M07 authority + complete downstream chain

Re-run current-anchor candidate 132/132 and all eight unfixed reproduction observations. Preserve prior passing results as historical comparison only.

#### Controlled M07

After exact candidate runtime installation from fresh V03, use a new baseline ID and run `Invoke-M07Build.ps1 -ControlledFailureAfterValidateCompilerInputs`.

Require:

1. original full pre-mutation source/runtime verification passes;
2. real Unity `ValidateCompilerInputs` succeeds;
3. both baseline-bound files actually mutate and contain the exact fresh baseline ID;
4. the new post-validation split authority succeeds — retain `M07PostValidationAuthorityVerifiedNotBuildAccepted` output/raw logs;
5. execution reaches the exact explicit controlled failure text above;
6. outer recovery retains pre-restore bytes and restores all three paths exactly;
7. fresh full candidate handoff/source preflight passes after recovery.

Failure before the explicit controlled throw is not acceptance. If another tracked build input is reported as needing mutation, return to Primary; do not widen the mutable set locally.

#### Normal M07

Use a separate fresh baseline ID and run normal `Invoke-M07Build.ps1` without the controlled switch.

It must pass the former post-`ValidateCompilerInputs` authority checkpoint and continue through:

- baseline resources;
- Native-ON Player;
- Native-OFF Player;
- structural resource stages/recovery;
- fixture finalization;
- Editor replay.

Then complete startup11, 8192/8193 capacity boundary, required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage, plus controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

### V05 — successor + independent whole-chain M08

Create the successor package only from explicit fresh current-anchor evidence. Include V00 authority, V01 Unity tests, strict six-build provenance, current count/reproduction evidence, controlled post-validation authority + explicit failure + exact recovery, normal successful M07 resources/Players/fixtures/replay, startup/capacity/retained coverage/performance, and all historical checkpoints under original identities.

Authenticate archive/index bytes and semantic membership, then commission a genuine independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate. Then stop for explicit human H1 approval.

## Failure evidence

For authority failures retain the recovery-root originals, current mutable bytes, exact path/hash mismatch, baseline ID, `verify-installed-runtime.py` stdout/stderr, `h1_m07_workflow_authority` output, Git/source preflight and all relevant Unity logs.

For controlled recovery retain the exact explicit-failure text, every `.before-restore` file, `workflow-inputs-restored.json`, original/restored hashes and post-recovery full preflight.

For normal M07 failures retain the last successful repeated authority check and the exact subsequent method/stage evidence so a verifier problem is not confused with a build/runtime problem.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Do not overwrite or relabel `local-validation-20260917-12cf9b2` or older checkpoints.

## Alternatives

Do not change the global `verify_demo` contract, make the demo source generally skippable, remove the core's repeated pin checks, whitelist an M07 directory, or accept arbitrary dirty tracked files.

Do not add a fourth mutable path locally. If real M07 proves another tracked build input is intentionally mutated, preserve exact evidence and return to Primary for review.

Do not broaden bootstrap/fixed-byte policy, provenance acceptance, reproduction behavior, ABI/count limits, or performance methodology.

## Risks

The M07 split authority deliberately assumes the workflow-owned mutable set is exactly the same three paths protected by outer recovery. Fresh real-Unity validation must confirm that later normal M07 stages do not require another tracked source mutation.

Baseline binding for scene/settings is intentionally strict; if real serialized representation changes while semantics remain valid, retain exact bytes and return to Primary rather than weakening the check locally.

Primary's 311/311 result does not establish real Unity M07 progression, startup/capacity/performance, M08, or human acceptance.

## Local correction boundary

Local may correct machine-specific absolute paths, executable permissions, invocation syntax, fresh evidence/output directories, and isolated harness setup.

Local must not alter the exact three-path mutable set, baseline-binding requirements, saved-original authentication, verifier dispatch semantics, three-file recovery contract, M07/bootstrap/fixed-byte policy, protected pins, provenance rules, count behavior, ABI/architecture, or performance methodology. Return such issues to Primary regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress / BlockedPendingFreshV00ToV05**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

Fresh V00–V05 and genuine independent whole-chain M08 PASS are required before Ready for Human Review Gate. Then stop for explicit human H1 approval.

**Do not begin R02.**
