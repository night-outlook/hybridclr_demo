# M02 dependency, manifest and resource compatibility tooling

Status: implementation and required local validation completed; final independent
acceptance review and M02 tags pending. M01 remains an accepted CONDITIONAL-GO PoC.

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

## Source boundary and API inventory

| Repository | Exact Player build source |
| --- | --- |
| demo | `0939b0ed667abd2694e5e7dbab23b6f670a8642f` |
| hybridclr_unity | `6d603459e52027cd31616c71f137d29aadaf4ea2` |
| hybridclr | `1bc69c3acc2434804e71560418df8c728a63360e` |
| il2cpp_plus | `03a450c73b5c5db2ed6f87dc4f194788fd204567` |

The demo pin-only commit is `891650bf8f1495b0f4c5c760e734c92076b8e7a6`.
Runtime and native source are unchanged from M01. Source pins, this report,
inventories and review/evidence closeout do not replace the executable source
boundary above. No M02 tag or remote publication is claimed by this draft.

[The source/API inventory](M02-source-and-api-inventory.md) records all 40 demo
and 153 package changed paths at that boundary, including Unity metas, and the
new tooling APIs, menu commands and batchmode entrypoints.

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
- A compiler AssemblyRef to a linker-excluded provider is not silently erased.
  A separate set-bound proof may exempt only its raw runtime-membership checks
  when the sealed linked consumer contains no such reference. The consumer must
  be an unprotected fixed AOT assembly with the same full identity and complete
  metadata/IL fingerprint as the frozen compiler input; current and frozen bytes
  are independently checked. Harmless MVID differences are allowed, but changed
  IL, attributes, references or identity are not. The provider must retain its
  exact captured compiler bytes and authenticated linker-excluded role. Candidate,
  Bootstrap, normal-hot-update and callback-filtered consumers are ineligible.
  Explicit and reflection dependencies remain subject to all original checks.
  Proof reuse rechecks the loaded set, roles, descriptors and bound files.
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
- Extensibility's asmdef declares Contracts, but its frozen base class uses no
  Contracts type token and therefore emits no compiled `AssemblyRef` to it.
  An explicit `ModuleContract` edge preserves the coordinated module upgrade
  boundary from design section 1.2. This is a declared dependency, not a claimed
  reflection call or a fabricated compiler reference. P03 consequently includes
  all five candidates while the immutable M01 business DLLs remain unchanged.
- Unsigned manifests are explicitly labelled unsigned. P05 can emit a
  resource-rebuild requirement, not a falsely deployable DLL-only package.
  Building and exercising matching replacement bundles is part of M07.
- Same input snapshots must produce byte-identical manifests. Fresh compiles
  may legitimately have different MVIDs/PDBs while preserving semantic hashes.
- The P05 fixture adds a real serialized field. Unity requires its loaded Editor
  layout to match the Player layout, so the validation wrapper compiles P05 in
  a separate Editor process with the P05 scripting define. It records the exact
  original defines before changing them, restores them in a `finally` phase,
  and runs P01/P02/P03 validation in a fresh baseline Editor domain. The P05
  snapshot is bound to this run, source pins and baseline. DLLs left behind by
  a failed `CompilePlayerScripts` result are not accepted as a snapshot.
  After Unity exits, the wrapper also restores the exact original settings-file
  bytes. That write requires a hash-bound receipt proving only the recorded
  target's define entry or empty-map representation changed; unrelated or
  concurrent edits are rejected. The final process verifies this byte roundtrip.

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

The fixed-image probe has an exact Bootstrap entry approval for the ordinary
hot-update entry type and callsite. Its explicit runtime dependency remains in
the graph; the entry approval does not authorize an unguarded managed load.

## Explicit design deviations and extensions

- The available execution platform is Unity 2022.3.62f2 macOS ARM64. This is the
  inherited M00/M01 local-platform deviation, not Windows/Android evidence.
- The finite, hash-bound reflection acquisition contracts extend M02's explicit
  implicit-dependency policy. They are not scanner exemptions or a substitute
  for the M03-M05 general first-use and resolution guarantees. The restrictions
  on enum lookup and the 17-type volume domain are deliberate and recorded above.
- The frozen M01 resource evidence is imported through source reconstruction and
  byte/hash/ABI proof, not through rebuilding the old bundles. This preserves the
  old-resource acceptance requirement while tying M02's Player and resource
  descriptions to independently checked inputs.
- A declared `ModuleContract` supplies the intended Extensibility-to-Contracts
  upgrade dependency where the C# compiler emits no AssemblyRef. No frozen
  business assembly was edited to force that edge.
- The real P05 layout is compiled in an isolated Editor domain. Exact settings
  restoration and successful target-compiler receipts are required; emitted
  files from a failed compiler invocation are never treated as successful output.
- M02 emits unsigned patch manifests and a generator-input adapter. Signing and
  production startup remain M09; updating the five generators remains M06/M08.

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
6. `Tools/AssemblyShadow/Invoke-M02EditorValidation.ps1` (owns the P05 Editor
   define/domain roundtrip and then calls `M02EditorValidation.Validate`).
7. `Tools/AssemblyShadow/verify-m02-results.py` with the actual Editor and NUnit
   results, `--reflection-result`, frozen M01 baseline, and an evidence output path.
8. Run the M02 Player in separate `Baseline` and `P01` processes with distinct
   `-shadowResultPath` and `-logFile` paths; require exit zero for both.
9. Build the ordinary M00 regression to a distinct output using
   `AssemblyShadowBaseline.Editor.BaselineBuild.Build`; run it with a distinct
   result/log path. This temporarily selects the M00 scene and native OFF.
10. Restore the exact captured fixed-image bytes from the M02 Player snapshot,
    run `M02Build.Configure`, and require the default strict installed-source
    verifier to pass in ON mode with no build-settings diff.

## Evidence, review and limitations

Real T02 integration, Player probes, native-OFF regression and complete artifact
verification have passed. Final immutable acceptance review is pending. macOS
ARM64 is the validated local platform inherited from M00/M01; no Windows or
Android result may be inferred from it. These were automated headless runs;
interactive visual/manual validation is not claimed.

| Check | Actual evidence | Result |
| --- | --- | --- |
| Unity NUnit | `Evidence/editor-tests.xml` | 319/319 passed, zero skipped |
| Target-compiler integration | `Evidence/editor-validation.json` | 13/13 passed: T02-01–T02-07, three linked-evidence cases, structural Editor domain, repeatability, snapshot tamper |
| Artifact verifier | `Evidence/verification.json` | actual Player/native/bundle/manifest/source/compile receipts verified |
| Python verifier regressions | `Evidence/python-tests.log` | 93/93 passed |
| Native-ON reflection probe | `Evidence/m02-reflection.json` | exit 0; 26 allowed, 8 denied, 17 finite discovery types, zero denied-path resolver events; fixed-image load and rejection checks pass |
| Original bundles, Baseline mode | `Evidence/m02-old-bundles-baseline.json` | exit 0, BASELINE-PASS |
| Original bundles, P01 mode | `Evidence/m02-old-bundles-p01.json` | exit 0, retained M01 CONDITIONAL-GO result |
| Repeat installation | `Evidence/installation-repeatability.json` | identical receipts; strict installed-source verification passes |
| Native-OFF ordinary regression | `Evidence/native-off-build.json`, `Evidence/native-off-result.json` | build and Player exit 0; ordinary HybridCLR/AOT/serialization checks pass |
| Restored ON source boundary | `Evidence/installed-source-verification.json` | default strict check passes, demoSourceVerified=true; exact original settings and fixed-image bytes restored |

The final baseline is `M02-Baseline-96de80420a47cfe2`, SHA-256
`f080b8e4eb1b91d055faf2f09ef624f9e649251a691df39fb1e903e91afae0cd`.
Its Player build GUID is `96cf854f12144d04920eb667c3829946`; the captured
snapshot hash is
`dd331b1ac2010b33cdd71119bd7b478b68a241802abf55ff7e383a6d531bb140`.
The actual ARM64 GameAssembly SHA-256 is
`0ac827495f6371c81cfc7d5bce7bf6d84c4cbf2968ca7682c9388c764002375c`.
The new app output is `Builds/AssemblyShadow/M02/Guarded-0939b0e.app`.
Unity reused cached Player asset data during its script-only phase; the
managed input, linked output and native binary receipts were captured from
this successful build. No full clean-asset rebuild is claimed.

The successful integration run directory is
`_temp/AssemblyShadow/M02Validation-374b53367f134d229d8ccb1abb3071eb`.
P01 has one closure member, P02 has three, P03 has all five with Contracts first,
and P05 rejects DLL-only and requires exactly the prefab and business-scene
bundles. The baseline and repeated P01 manifest are byte-identical for the same
snapshots. P05's original scripting defines and complete settings-file bytes
were restored; all three restoration receipts are archived.

The OFF app is `Builds/AssemblyShadow/M02/NativeOff-0939b0e.app`, ARM64 native
SHA-256 `805e43f0020801cab5daaa50c424feb89f7c6a4dfee3f4621259557662dd0dd6`.
It runs the original M00 scene and an ordinary freshly compiled hot-update DLL;
the exact two tracked configuration differences are archived in
`Evidence/native-off-settings.diff`. A strict source check attempted during this
intentional override correctly refused the changed scene setting. It was not
bypassed: after `M02Build.Configure` restored the pinned ON configuration, the
default strict verifier passed with 923 source files, 925 installed files and
receipt SHA-256
`243f9163413f97825d485153b797b13e8f2adfdb80c9e5d61c4920d54fe09999`.
The fixed-image bytes were restored to SHA-256
`9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`.

The current consolidated source passed 319/319 Unity Editor tests with no skips
(`_temp/AssemblyShadow/EditorTests-8da6a38f5fb444f697f49479624ec158/results.xml`).
This includes full-identity/provenance regressions, schema-2 acquisition guards,
fixed-image evidence, unproven callback state, policy-path handling, actual
builtin-resource capture, the real 26-name prefab comparison, linked-reference
proofs, exact ordinary-hot-update entry approvals, unchanged Editor enum
behavior, 22 structural-workflow cases and the two module-dependency regressions.
The Python artifact suite passes 93 tests and requires those new NUnit fixtures.
Earlier diagnostic runs exposed that Unity's
`BuildReport.summary.result` is not final inside `OnPostprocessBuild`; capture now
observes callbacks and seals only after `BuildPipeline.BuildPlayer` returns a
matching successful report. A failed target compile also demonstrated that P05
needs the matching loaded Editor layout; the separate-domain workflow now proves
that requirement with real Unity execution. A subsequent diagnostic reached P03
and exposed the missing explicit module dependency; the current five-member
result uses the truthful `ModuleContract` declaration described above.
Independent review also identified verifier mismatches for captured versus
projected roles, same-type builtin objects and historical source provenance.
The corrected verifier accepts the current full real-artifact set, and adversarial
tests retain rejection of altered identities, roles and rehashed provenance.

The first guarded Player attempt exposed Unity forwarding the same control
define twice. Identical controls are now idempotent; distinct or malformed
controls still fail closed. The real Editor validation additionally requires a
schema-2 snapshot copy/read roundtrip, captured-facade byte tamper rejection,
and a modified semantic proof rejection even after its outer receipt hashes
have been recomputed. These cases operate on a disposable copy and restore it
after each negative test; frozen baseline evidence is never modified.

## Performance observations

The final ON Player-build phase reported 36.980 seconds; the OFF build phase
reported 27.172 seconds. These exclude generator preparation and resource-proof
construction. Unity NUnit reported 25.008 seconds
for 319 tests. The archived 93-test Python run took 17.609 seconds. These are
local build/test observations, not a runtime performance or memory acceptance
claim. M02 changes Editor tooling; runtime lookup benchmarks belong to later
milestones. No new runtime memory benchmark is claimed here.

## Next milestone entry

M03 remains gated on final independent acceptance review and M02 tags. All local
M02 execution checks have passed. M03's scope is the real private staging transaction, atomic
publication, delayed initializers, stable error API and first-use guard; the
M01 prototype is not treated as that implementation.
