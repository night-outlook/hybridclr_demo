# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the M07 fixed-byte/bootstrap-policy blocker returned by Local Validation commit `d8349b3facaa5d420ec41a484854a9bba9e6c1a4`.

Authoritative candidate source / implementation anchor:

`29261690798059077e5263de71526867a32bce30`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

The previous Local cycle empirically passed V00–V03, candidate count 132/132, and captured all eight unfixed reproduction cells. It then failed closed in real Unity M07 policy validation because `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness` was not represented in the global bootstrap-entrypoint policy even though the exact fixed assembly bytes were already authenticated by `h1-count-ordinary-witness-image`.

Primary reconciled the two policy layers without changing the shared package/global rule or adding a broad exception. It also corrected M07 failure recovery to restore the exact scene/settings bytes observed mutated by Local.

Run fresh **V00–V05**. Preserve every historical checkpoint, including the valid empirical evidence from `local-validation-20260916-e96bc07`, but do not relabel old-source evidence as current-anchor acceptance.

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Documents/AgentHandoff/source-targets.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-e96bc07/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/m07-fixed-bootstrap-primary-20260916/`

Git is the authority. Do not apply unpublished patches or mutate protected branches/pins.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `29261690798059077e5263de71526867a32bce30` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Protected reproduction demo | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Unfixed reproduction behavior source | same history | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction validation tooling | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro-tooling` | `ba8fee33753a5ebc215b7a98739e343d8e05572e` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. Candidate `AssemblyShadowSourcePins.json` pins `29261690798059077e5263de71526867a32bce30`. The final branch HEAD is expected to be a later metadata-only handoff successor; record both checkout HEAD and source anchor.

## Implementation

### Fixed-byte acquisition + global bootstrap policy

The existing schema-4 reflection-binding site remains authoritative:

- site: `h1-count-ordinary-witness-image`;
- consumer: `AssemblyShadowDemo.Bootstrap`;
- callsite: `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness`;
- provider: `AssemblyShadowBaseline.HotUpdate`;
- original method hash: `fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e`;
- additional method hash: `4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e`;
- operation index: `25`;
- image path: `Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes`;
- image SHA-256: `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`;
- provider identity remains exact.

The shared `BootstrapIsolationRule` and package pin are unchanged. `AssemblyShadowDependencies.json` declares **exactly two target-qualified entries** for this one callsite:

1. source/precompile evidence target `image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4`;
2. compiled fixed-image target `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`.

No targetless, provider-wide, type-wide, or method-only H1 exemption exists. `M07FixedByteBootstrapPolicyTests` uses the real Unity policy construction/validator, requires the exact binding/entrypoint relationship, and proves another image target remains rejected.

### M07 failure restoration

`Tools/AssemblyShadow/Invoke-M07Build.ps1` is now a narrow outer failure guard. `Tools/AssemblyShadow/Invoke-M07Build.Core.ps1` retains the proven M07 workflow behavior.

Before invoking the core workflow, the wrapper snapshots exact bytes for:

- `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`;
- `ProjectSettings/AssemblyShadowSettings.asset`;
- `ProjectSettings/EditorBuildSettings.asset`.

On **failure only**, after owned Unity processes exit, it preserves the current/pre-restore bytes, restores the exact originals, writes `workflow-inputs-restored.json`, and then rethrows the original failure. Recovery failure is itself surfaced explicitly. Successful M07 workflow semantics are unchanged.

### Primary bounded validation

Candidate source anchor `29261690798059077e5263de71526867a32bce30` passed workflow `35135969629` with **300/300** bounded tests and zero nonpasses.

- authenticated Apple Bee fixture SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10463420165`
- artifact SHA-256: `2f1b9707ed745e47461b2f5baa3e8672b4b3d2ecd4ce5380fb085cc125d299e2`

This is bounded Primary/tool evidence only. It is not real Unity M07 acceptance, runtime acceptance, M08 PASS, or human approval.

## Local validation

Follow `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/m07-fixed-bootstrap-primary-20260916/LOCAL_VALIDATION_TASKS.md`.

### V00 — authority

1. Pull candidate branch; record final HEAD, source anchor `29261690798059077e5263de71526867a32bce30`, dirty/untracked state, and sibling protected heads.
2. Run candidate `h1_handoff_preflight.py`; require `SourceTargetVerifiedNotBuildAccepted`.
3. Run split reproduction-tooling preflight against exact `ba8fee33753a5ebc215b7a98739e343d8e05572e`; require protected behavior/runtime pins and tooling authority unchanged.

If either preflight fails, stop before V01–V05.

### V01 — source/tool/Unity regressions

Run full H1 Python inventory and bounded Primary suite. Compile candidate and reproduction-tooling checkout in Unity 2022.3.62f2. Run affected H1 Editor tests, explicitly including `M07FixedByteBootstrapPolicyTests`; both real Unity policy tests must pass.

### V02 — fresh candidate provenance smoke

Run a fresh candidate ON/Debug schema-3 normal-cache proof under source anchor `29261690798059077e5263de71526867a32bce30`. Preserve normal Bee cache and require all strict native/PCH/store/managed/fresh-Player/restoration controls.

### V03 — fresh six-build set

Use `h1_count_build_batch_tooling.py` to produce fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release. Require strict native+managed provenance, tooling bindings, and exact restoration for all six accepted builds. Do not reuse old-source smoke receipts.

### V04 — fresh count + M07 + runtime/performance chain

Re-run the current-source count matrix even though the previous Local cycle captured candidate 132/132 and all eight reproduction cells; preserve those historical results for comparison only.

For M07:

1. use a new baseline ID and new outputs;
2. require real `M07Build.ValidateCompilerInputs` to pass with only the two reviewed target-qualified H1 entries;
3. preserve `M07FixedByteBootstrapPolicyTests` evidence;
4. execute a controlled failing M07 invocation and require exact restoration receipts/evidence for the three wrapper-owned files above;
5. then execute the normal successful M07 baseline/resources/players chain and continue startup11, 8192/8193 capacity boundary, required lazy/dense/generic/array/reflection/FieldRVA/old-Player/M03–M07 coverage;
6. run controlled Development performance only against protected reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` on common supported workloads.

If real Unity requires a third bootstrap target or a broader rule, retain the exact source/precompile/compiled policy evidence and return to Primary. Do not broaden locally.

### V05 — successor + independent whole-chain M08

Build the successor package only from explicit fresh current-anchor evidence. Include both V00 authority outputs, fresh six-build receipts/provenance, fresh count evidence, M07 policy regression, controlled-failure restoration receipt and pre-restore bytes, successful M07/runtime/startup/capacity/performance evidence, and historical checkpoints under their original identities.

Authenticate archive/index bytes and semantic membership. Then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make the package Ready for Human Review Gate. Then stop for explicit human H1 approval.

## Failure evidence

For M07 policy failure retain the exact policy/dependency/reflection-binding bytes and hashes, scanner/compiler snapshot, emitted bootstrap reflection references, fixed-byte site identity, Unity logs and NUnit XML.

For M07 workflow failure retain the outer recovery root, each `.original` backup, each `.before-restore` file, `workflow-inputs-restored.json`, original workflow error, post-recovery Git/source preflight, and exact hashes of scene/settings before invocation and after restoration.

For all V00–V05 failures preserve the existing strict provenance/runtime evidence contracts and distinguish `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun`, and `NoCoverage`.

Do not overwrite, rewrite, or relabel `local-validation-20260916-e96bc07` or older checkpoints.

## Alternatives

Do not modify the shared `BootstrapIsolationRule`, add a generic bootstrap-reflection bypass, admit provider/type/method-wide reflection, weaken `FixedAssemblyBytes`, derive acceptance from only the compiled SHA without the method/provider binding, or locally add another target.

Do not solve failure cleanup by resetting/cleaning the repository. Recovery must use the wrapper's captured exact bytes and retained evidence.

## Risks

The two target forms are based on the actual project policy scanner's source/precompile and compiled representations of the same fixed-byte acquisition. Fresh V01/V04 must verify that real Unity still emits exactly those forms under this source anchor.

The outer restoration wrapper is intentionally failure-only so a successful M07 workflow retains its established behavior. Local must empirically verify both the controlled-failure recovery path and the normal successful path.

Primary's 300/300 result does not establish Unity M07, runtime, performance, M08, or human acceptance.

## Local correction boundary

Local may correct machine-specific absolute paths, executable permissions, invocation syntax, new evidence/output directory choices, and isolated test harness setup.

Local must not change bootstrap targets/entrypoints, fixed-byte binding semantics, recovery file set/logic, protected behavior/runtime/tooling/performance pins, provenance rules, count behavior, ABI/architecture, or performance methodology. Such issues return to Primary regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 remains **InProgress / BlockedPendingFreshV00ToV05**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

Fresh V00–V05 and genuine independent whole-chain M08 PASS are required before Ready for Human Review Gate. Then stop for explicit human H1 approval.

**Do not begin R02.**
