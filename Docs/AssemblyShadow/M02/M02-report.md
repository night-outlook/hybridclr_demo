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
  Resolution checks full assembly identity. A framework version exception needs
  an immutable proof matching the captured reference's identity and bytes to the
  pinned installation's active-target compiler framework catalog. Primary inputs,
  incompatible tokens/cultures/content types, recorded source-path labels and
  runtime-facade profiles cannot confer that exception. Validation therefore
  requires the matching Unity installation; offline catalog replay is not claimed.
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
  to the same empty-user-define compiler snapshot. A generated, hash-bound
  reflection control define is included when the finite contracts are enabled.
  Other compiler inputs remain
  explicit resolver references, not additional resource ABI roots.
- A removed explicit dependency cannot erase a frozen baseline consumer.
  Normal HybridCLR hot-update assemblies remain distinct from AOT candidates.
- Unsigned manifests are explicitly labelled unsigned. P05 can emit a
  resource-rebuild requirement, not a falsely deployable DLL-only package.
  Building and exercising matching replacement bundles is part of M07.
- Same input snapshots must produce byte-identical manifests. Fresh compiles
  may legitimately have different MVIDs/PDBs while preserving semantic hashes.

## Finite reflection contracts

Five managed acquisition sites require explicit bounded Player contracts.
`ProjectSettings/AssemblyShadowReflectionBindings.json` therefore defines an
explicit Player-only contract for each exact assembly, type, method fingerprint,
instruction and overload. This is a documented extension of the M02 implicit
dependency policy, not a reflection-scanner exemption:

- `DebugUIHandlerCanvas.Rebuild` permits exactly the 26 assembly-qualified widget
  names in the pinned URP `DebugUICanvas.prefab`. An Editor test compares actual
  `SerializedObject` strings, including Unity's YAML whitespace handling.
- `SerializableEnum.value` has an explicit deny-all Player contract for nonempty
  type strings. Such use is unsupported in this baseline and throws before type
  resolution; no claim of unreachability is made. Its Editor behavior is retained.
- The two `CoreUtils.GetAllAssemblyTypes` discovery sites construct a finite
  assembly list and return finite types without calling `GetAssemblies` or
  `GetTypes`. The sealed target contains exactly 17 concrete transitive
  `VolumeComponent` descendants, all in Universal RP; its only compiled discovery
  caller is `VolumeManager`. The Player probe checks the actual caller and manager
  output and uses a receiver with an observable `GetTypes` override to test denial
  before enumeration. This is a pinned contract, not support for arbitrary future
  volume types or general pre-use protection.
- The ordinary M00 byte loader clones its input and checks a configured SHA-256
  before `Assembly.Load`. Snapshots retain that exact image and verify its full
  assembly identity and complete semantic equality to the current
  `NormalHotUpdate` compiler input. A harmless MVID/raw-hash difference does not
  substitute a different shipped image. Generic call-site prose cannot authorize
  an unguarded byte load or unbounded type enumeration.
- A private same-type guard performs exact ordinal comparisons, then calls the
  original `Type.GetType(string)` overload with a constant allowed target. Other
  strings fail before lookup. The normal scanner still sees those real providers;
  same-assembly targets do not create self-edges and external providers retain
  normal reverse-closure restrictions.
- Unity discovers the Editor-only `Unity.HybridCLR.AssemblyShadow.CodeGen`
  postprocessor by its required naming convention. No package source is rewritten.
  A raw configuration SHA in the compiler define invalidates stale cached outputs.
  The Editor and compilations without that control define are unmodified.
- Compiler snapshots retain strict original-method and full guard verification.
  Linked proof separately accounts for Unity's per-type framework forwarding,
  using captured runtime `netstandard` facade bytes and the actual linked framework
  definitions. It never ignores assembly scopes or rewrites literal AQNs. The
  entire protected method and guard must still match, including branches and EH.
- The linked proof records the target-aware IL2CPP profile, facade SHA, complete
  forwarder map, runtime module SHA/MVIDs, consumer input/linked SHA, and per-site
  method/guard hashes. Its file SHA is bound by linked receipt schema 2 and then
  the Player snapshot hash. Schema 1 remains the no-binding receipt format.
  Binding configuration/transformer version 2 adds acquisition kinds and fixed
  image identities; version-1 canonical hash encoding remains unchanged.

The fixed Bootstrap probe uses framework and ordinary M00 AOT type tokens, never
Shadow candidate tokens. Its dedicated
`M02ReflectionBindings` mode exercises all 26 permitted names, six denied strings,
an actual mutated canvas prefab field through `Rebuild`, and the real deny-all enum
getter. Zero resolver events are supporting observations; the linked IL template
is the proof that rejection precedes lookup. This is not a substitute for the
M03–M05 transaction and first-use guards.

The schema-2 probe also checks the complete volume-discovery domain, a rejected
receiver before its enumeration override runs, and normal hot-update execution
after fixed-image verification. Tampered/null images must fail before loading and
caller-owned bytes must remain unchanged. The Shadow-OFF ordinary M00 regression
continues to use its unmodified upstream load path.

## Reproduction entrypoints

Use the isolated `hybridclr_demo_shadow` project and shared unity-debug routing;
preserve any pre-existing Editor in the original checkout.

1. `AssemblyShadowDemo.Editor.M02Build.Configure`
2. `Tools/AssemblyShadow/Invoke-ShadowEditorTests.ps1 -TestFilter 'HybridCLR.Editor.AssemblyShadow.Tests;AssemblyShadowDemo.EditorTests'`
3. `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`
4. `AssemblyShadowDemo.Editor.M02Build.BuildPlayerBaseline`
5. Run the resulting Player with `-batchmode -nographics -shadowMode M02ReflectionBindings`,
   a distinct absolute `-shadowBindingResult` path and `-logFile` path. Require
   process exit zero and `result=Passed`.
6. `AssemblyShadowDemo.Editor.M02EditorValidation.Validate`
7. `Tools/AssemblyShadow/verify-m02-results.py` with the actual Editor and NUnit
   results, `--reflection-result`, frozen M01 baseline, and an evidence output path.

## Evidence, review and limitations

Pending real Unity integration runs and independent review. Static compilation
or a passing synthetic fixture alone is not milestone acceptance. macOS ARM64
is the available validated platform inherited from M00/M01; no Windows or
Android result may be inferred from it.

The current consolidated source passed 260/260 Unity Editor tests with no skips
(`_temp/AssemblyShadow/EditorTests-42d7408422d34cfa8d83d635ea39411e/results.xml`).
This includes full-identity/provenance regressions, schema-2 acquisition guards,
fixed-image evidence, unproven callback state, policy-path handling, actual
builtin-resource capture, the real 26-name prefab comparison, and unchanged
Editor enum behavior. These results do not establish the new native Player or
complete T02 integration. The initial diagnostic build also exposed that Unity's
`BuildReport.summary.result` is not final inside `OnPostprocessBuild`; capture now
observes callbacks and seals only after `BuildPipeline.BuildPlayer` returns a
matching successful report. The last guarded Player at package `9ef3c4e` sealed
its Player inputs and passed reflection, old-bundle Baseline, and old-bundle P01
probes, but its resource import then failed on the engine-owned GUISkin. The
subsequent repair captures builtin backing bytes, defining installed modules and
every object identity; that repair is covered by the current Unity suite but still
requires the complete import/build run. No earlier binary proves the current
schema-2 guards. The updated Python artifact suite passes 77 tests, including
schema-2 projection and nested builtin-proof tamper cases.

The first guarded Player attempt exposed Unity forwarding the same control
define twice. Identical controls are now idempotent; distinct or malformed
controls still fail closed. The real Editor validation additionally requires a
schema-2 snapshot copy/read roundtrip, captured-facade byte tamper rejection,
and a modified semantic proof rejection even after its outer receipt hashes
have been recomputed. These cases operate on a disposable copy and restore it
after each negative test; frozen baseline evidence is never modified.
