# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from Local Validation return commit:

`1d0be06d5dc61eb963a13a72061be82f8fd04bf4`

Authoritative candidate source / implementation anchor:

`f59b0d8d171340951157b01b583df17e380d6f55`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

Local correctly added the bounded direct `Unity.HybridCLR.AssemblyShadow.CodeGen` reference to `AssemblyShadowDemo.EditorTests.asmdef`. Real Unity compilation then passed and `M07FixedByteBootstrapPolicyTests` passed 2/2; the previous source authority rejected the changed bytes exactly as designed.

Primary reviewed and retained that fix, added a regression that locks its Editor/test-only scope, and added a deterministic V04 controlled-failure path that can prove exact restoration **after real M07 configuration mutation**.

Run fresh **V00–V05**. Preserve all historical checkpoints/evidence, including the valid Local correction evidence at `local-validation-20260916-a42b205`, but do not relabel old-source results as current-anchor acceptance.

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Documents/AgentHandoff/source-targets.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-a42b205/`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/m07-codegen-test-reference-primary-20260916/`

Git is the authority. Do not apply unpublished patches or mutate protected branches/pins.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `f59b0d8d171340951157b01b583df17e380d6f55` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction demo | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Unfixed reproduction behavior source | same history | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction validation tooling | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**.

Candidate `ProjectSettings/AssemblyShadowSourcePins.json` pins source anchor `f59b0d8d...`. The final branch HEAD is a later metadata-only successor; record both checkout HEAD and source anchor.

## Implementation

### Retained direct CodeGen test reference

`Assets/AssemblyShadowDemo/Tests/Editor/AssemblyShadowDemo.EditorTests.asmdef` directly references:

`Unity.HybridCLR.AssemblyShadow.CodeGen`

This is required because `M07FixedByteBootstrapPolicyTests.cs` directly imports `HybridCLR.AssemblyShadow.CodeGen`; Unity asmdef references are non-transitive.

The boundary remains test-only:

- platform is exactly `Editor`;
- `autoReferenced=false`;
- `UNITY_INCLUDE_TESTS` remains required;
- exactly one direct CodeGen reference is permitted;
- no Player/runtime assembly reference was added.

Local empirical correction evidence is preserved: after this one-line fix the candidate compiled in real Unity 2022.3.62f2 with zero errors and `M07FixedByteBootstrapPolicyTests` passed **2/2**. That result is correction evidence, not current-anchor V01 acceptance.

### Fixed-byte / bootstrap policy remains unchanged

The exact two-target H1 fixed-byte/bootstrap bridge from the previous Primary repair remains in force. Do not add another target or broaden `BootstrapIsolationRule`, `FixedAssemblyBytes`, provider/type/method admission, or reflection policy.

### Deterministic controlled post-mutation restoration

`Tools/AssemblyShadow/Invoke-M07Build.ps1` now supports the opt-in switch:

`-ControlledFailureAfterValidateCompilerInputs`

Only in this mode it:

1. snapshots the exact three outer-owned files;
2. verifies installed candidate runtime/source pins;
3. executes real Unity `AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs` with the supplied baseline ID;
4. verifies installed pins again;
5. deliberately throws before entering the normal core workflow;
6. restores exact bytes through the existing outer recovery and rethrows.

The three files are:

- `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
- `ProjectSettings/AssemblyShadowSettings.asset`;
- `ProjectSettings/EditorBuildSettings.asset`.

The normal no-switch path continues to delegate unchanged to `Invoke-M07Build.Core.ps1`.

### Primary bounded validation

Final source anchor `f59b0d8d171340951157b01b583df17e380d6f55` passed workflow `35179309998`:

- **302/302 Passed**;
- zero nonpasses;
- authenticated Apple Bee graph SHA-256 `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`;
- artifact ID `10478699390`;
- artifact SHA-256 `28239edbda587ca61f9175ef42b334c588363a28226d955b25198a7219afd258`.

This is bounded Primary/tool evidence only. It is not current-source Unity/Player/M07/runtime/performance acceptance, M08 PASS, or human approval.

## Local validation

Follow `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/m07-codegen-test-reference-primary-20260916/LOCAL_VALIDATION_TASKS.md`.

### V00 — authority

1. Pull the final candidate handoff HEAD; record final checkout HEAD and source anchor `f59b0d8d...` separately.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Run split reproduction-tooling preflight against exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
4. Verify every protected reproduction/native/package/IL2CPP/performance identity remains exact.

Stop before V01–V05 on V00 failure.

### V01 — source / Unity / policy integration

Run the full H1 Python inventory and exact bounded Primary suite. Compile candidate and reproduction-tooling checkout in real Unity 2022.3.62f2.

Candidate must have zero compile errors and `M07FixedByteBootstrapPolicyTests` must pass **2/2** using the real policy construction/validator. Retain exact NUnit XML/logs and asmdef bytes.

### V02 — fresh candidate provenance

Run a fresh candidate ON/Debug schema-3 normal-cache proof under source anchor `f59b0d8d...`. Preserve normal Bee cache and require all strict native compiler/PCH/store/managed/fresh-Player/restoration controls. Do not substitute legacy `--reuse-proof`.

### V03 — fresh six-build set

Use candidate-owned `h1_count_build_batch_tooling.py` and exact reproduction tooling to produce fresh:

- candidate ON/OFF × Debug/Release;
- reproduction ON Debug/Release.

Require strict current native+managed provenance, tooling binding, and exact restoration for every accepted build.

### V04 — fresh count + actual-mutation recovery + successful full chain

Re-run candidate 132/132 count cells and all eight unfixed reproduction observations under the current source anchor. Preserve older count evidence only as historical comparison.

#### A. Controlled restoration after actual mutation

After fresh V03 has installed the exact candidate runtime, choose a **new** baseline ID and run:

```powershell
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 `
  -ProjectPath /ABS/CANDIDATE `
  -BaselineId M07-Baseline-H1-<NEW-ID> `
  -TimeoutSec 28800 `
  -ControlledFailureAfterValidateCompilerInputs
```

Require all of the following:

1. real Unity `M07Build.ValidateCompilerInputs` succeeds first;
2. the observed failure is the explicit controlled post-validation failure—not pin/preflight/Unity-policy failure;
3. `workflow-inputs-restored.json` has `status=ExactBytesRestored`;
4. **actual mutation is proved**: the pre-restore hashes for both `M07Bootstrap.unity` and `ProjectSettings/AssemblyShadowSettings.asset` differ from their original hashes; `EditorBuildSettings.asset` may remain unchanged;
5. all three restored hashes exactly equal originals;
6. candidate source authority/preflight passes again after restoration.

A failure before real `ValidateCompilerInputs`, or a restoration receipt without the required scene/settings mutation, is `NoCoverage` for this requirement.

#### B. Normal successful M07/runtime/performance chain

Then use another fresh baseline ID and run normal `Invoke-M07Build.ps1` **without** the controlled switch. Complete and retain:

- successful `ValidateCompilerInputs`;
- baseline resources;
- native ON/OFF Players;
- fixtures and Editor replay;
- startup11;
- 8192/8193 capacity boundary;
- required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage;
- controlled Development performance against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

Do not broaden bootstrap/fixed-byte policy locally if a new issue appears.

### V05 — successor + independent whole-chain M08

Build the successor package only from explicit fresh current-anchor evidence. Include V00 authority, V01 Unity/policy evidence, six-build provenance, fresh count evidence, controlled actual-mutation restoration evidence, successful M07/runtime/startup/capacity/performance evidence, and historical checkpoints under their original identities/dispositions.

Authenticate archive/index bytes and semantic membership. Then commission a genuine independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate. Then stop for explicit human H1 approval.

## Failure evidence

For V00/V01 failures retain exact checkout/source identities, source-target/pin bytes, asmdef bytes, Unity compile logs, NUnit XML, and reproduction-tooling authority outputs.

For controlled M07 recovery retain the complete outer recovery root including original snapshots, `.before-restore` bytes, `workflow-inputs-restored.json`, real ValidateCompilerInputs logs, explicit controlled failure, restored hashes, and post-recovery preflight. Do not call it mutation coverage unless the required scene/settings hashes actually changed before restoration.

For later V04/V05 failure preserve all raw M07/runtime/startup/capacity/performance/provenance evidence and exact stage disposition.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Do not overwrite or relabel historical Local checkpoints.

## Alternatives

Do not remove the direct CodeGen test reference and do not work around it by making references transitively visible or by moving the integration test into a production assembly.

Do not add bootstrap targets, weaken fixed-byte bindings, bypass M07 policy, or accept a pre-mutation recovery attempt as evidence.

Do not reset/clean the repository to recover M07 mutations; use the wrapper's exact captured bytes and preserve recovery evidence.

## Risks

The direct CodeGen reference is deliberately limited to an Editor test asmdef; any future move of the policy integration test or CodeGen API can change that compile-time dependency and must be reviewed rather than silently broadened.

The controlled-failure switch proves recovery only when real `ValidateCompilerInputs` succeeds and changes the intended files. Fresh Local empirical validation is therefore mandatory.

Primary 302/302 does not establish real Unity current-anchor acceptance, successful M07 runtime chain, performance, independent M08, or Human Review Gate readiness.

## Local correction boundary

Local may correct machine-specific absolute paths, executable permissions, invocation syntax, fresh output/evidence roots, and isolated harness setup.

Local must not alter the direct CodeGen dependency boundary, controlled-failure semantics, wrapper recovery file set, bootstrap/fixed-byte policy, protected behavior/runtime/tooling/performance pins, provenance rules, count behavior, ABI/architecture, or performance methodology. Return such issues to Primary regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress / BlockedPendingFreshV00ToV05**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

Fresh V00–V05 and genuine independent whole-chain M08 PASS are required before Ready for Human Review Gate. Then stop for explicit human H1 approval.

**Do not begin R02.**
