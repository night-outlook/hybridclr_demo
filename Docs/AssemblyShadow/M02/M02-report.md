# M02 dependency, manifest and resource compatibility tooling

Status: implementation and validation in progress. No M02 acceptance or tag is
claimed by this draft. M01 remains an accepted CONDITIONAL-GO PoC.

## Scope and acceptance

M02 implements tasks 02.1–02.12 from the milestone plan. Its acceptance requires
real Unity Editor integration tests T02-01–T02-07, deterministic repeat outputs,
an actual Player-input baseline snapshot, adversarial unit tests, independent
review and a local milestone tag in the four source repositories. Native
transaction/type/execution/Unity integration work remains M03–M07.

| Requirement | Implementation boundary | Required evidence |
| --- | --- | --- |
| 02.1 independent candidate settings | package Settings | candidates retained by actual Player filter capture |
| 02.2 naming/Internal/Extensibility/Bootstrap policy | package Validation | unit tests and precompile illegal asmdef case |
| 02.3 target metadata loading | package Metadata | explicit references, duplicates/unresolved tests |
| 02.4 versioned semantic hashing | package Hashing | metadata/IL/signature/debug-only adversarial tests |
| 02.5 reverse dependency closure | AssemblyReferenceGraph | P01/P02/P03 and non-Shadow consumer rejection |
| 02.6 stable dependency-first order | AssemblyReferenceGraph | cycle and repeatability tests |
| 02.7 declared dependencies | project config and graph | unknown/duplicate/self-edge and frozen-edge tests |
| 02.8 conservative serialized ABI | package Serialization | flags, inherited/DTO/list/managed-reference tests |
| 02.9 precise resource impact index | package Serialization | actual frozen prefab/scene GUIDs, data excluded |
| 02.10 Player baseline manifest | package Build | successful Player, input receipt and native SHA |
| 02.11 unsigned patch manifests | package Build | single compile snapshots, P05 refusal, file/hash verification |
| 02.12 generator input adapter | package Generation | normal hot-update union current closure only |

## Design boundaries

- Source of truth remains the pinned native/runtime/package repositories. This
  milestone adds Editor tooling; it does not claim a new native runtime gate.
- The baseline capture observes `IFilterBuildAssemblies` before and after all
  ordinary build filters, returns both input arrays unchanged, and seals the
  receipt only after a successful Player build. Removed compiler outputs retain
  their bytes and original capability roles as exclusion evidence. Only this
  frozen evidence can classify an assembly as build-filtered; a filename or
  source-policy assertion cannot. Candidate/Bootstrap removal is an error.
  A second, separately hashed receipt records the actual linked DLL/PDB set,
  build GUID and native binary hash. Linker exclusions are derived only from
  that verified output; the pre-strip compiler inputs remain intact.
  No Editor-domain DLL is substituted for a target compiler or Player input.
- Compiler reference DLLs come from the target Player compiler's explicit
  reference paths. Patch closure DLLs are copied from a single captured compile
  snapshot; missing, injected or modified DLLs fail validation.
- The original `M01-Baseline-v1` bundles and assembly snapshots are never
  rebuilt or replaced. M02 gets a separate manifest and Player input snapshot.
- A resource-build receipt binds bundle bytes, compiler inputs, serialized ABI,
  script index, authored asset/meta hashes and dependencies. The generic command
  builds this evidence together with new bundles. The M01 import instead checks
  the accepted frozen source audit and reconstructs both original consumer
  assemblies from those sources and explicit target references. In either path,
  the frozen resource ABI must match the actual captured Player ABI; live asset
  metadata cannot certify independently supplied old bundle bytes.
  Fresh resource metadata contains exactly the declared candidates, byte-matched
  to the same empty-define compiler snapshot. Other compiler inputs remain
  explicit resolver references, not additional resource ABI roots.
- A removed explicit dependency cannot erase a frozen baseline consumer.
  Normal HybridCLR hot-update assemblies remain distinct from AOT candidates.
- Unsigned manifests are explicitly labelled unsigned. P05 can emit a
  resource-rebuild requirement, not a falsely deployable DLL-only package.
  Building and exercising matching replacement bundles is part of M07.
- Same input snapshots must produce byte-identical manifests. Fresh compiles
  may legitimately have different MVIDs/PDBs while preserving semantic hashes.

## Reproduction entrypoints

Use the isolated `hybridclr_demo_shadow` project and shared unity-debug routing;
preserve any pre-existing Editor in the original checkout.

1. `AssemblyShadowDemo.Editor.M02Build.Configure`
2. `Tools/AssemblyShadow/Invoke-ShadowEditorTests.ps1`
3. `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`
4. `AssemblyShadowDemo.Editor.M02Build.BuildPlayerBaseline`
5. `AssemblyShadowDemo.Editor.M02EditorValidation.Validate`
6. `Tools/AssemblyShadow/verify-m02-results.py` with the actual Editor and NUnit
   results, frozen M01 baseline, and a selected evidence output path.

## Evidence, review and limitations

Pending real Unity integration runs and independent review. Static compilation
or a passing synthetic fixture alone is not milestone acceptance. macOS ARM64
is the available validated platform inherited from M00/M01; no Windows or
Android result may be inferred from it.

The current build-source checkpoint passed 146/146 Unity Editor tests with no
skips (`_temp/AssemblyShadow/EditorTests-63a522a02e574405ba48d70c720e3ab7/results.xml`).
This includes real JsonUtility round trips, linked-evidence tampering, exact
snapshot sections, facade resolution and resource/compiler provenance. It is
not yet a successful M02 Player build or a passed milestone. Two URP Core
data-driven reflection sites still require a sound bounded dependency policy.
