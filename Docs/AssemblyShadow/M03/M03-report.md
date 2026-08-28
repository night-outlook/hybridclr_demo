# M03 native transaction and staging

Status: the first native-ON baseline and Editor replay passed, but its real
T03-01 transaction failed reference resolution. A bounded facade/compiler-library
repair is being validated for a fresh v2 baseline. No M03 milestone tag or
permission to enter M04 is claimed here.

## V2 build-source pairing

| Repository | Exact source commit |
| --- | --- |
| hybridclr | `fd60cb21a4d0d4c204848c3477d2a30ffd155710` |
| il2cpp_plus | `0486098099e7e80176401267538499e611b181f2` |
| hybridclr_unity | `460eb5d65923e092d3c8acc7eb912c2942aea645` |
| demo | `ea49e1d11e30c65417dadc0f903ef7606b63776e` |

Baseline ID: `M03-Baseline-v2`. Runtime ABI hash:
`c9236ac7b6d2a1b32551ca60266199df3acaf11265b488cb2d7a609f6a2f6bfb`.
This source pairing is ready for installation/build, not accepted runtime evidence.

## First diagnostic build source checkpoints

| Repository | M03 source checkpoint |
| --- | --- |
| hybridclr | `69168bb1f192ef16261a7822de82d52150fb691a` |
| il2cpp_plus | `740912bbfcf3e26155f157e7ba0f36d660546ef3` |
| hybridclr_unity | `460eb5d65923e092d3c8acc7eb912c2942aea645` |
| demo | `a71ce08c561a86781ed4f90b2b7281bc2653a1e8` |

The [transaction contract](M03-transaction-contract.md) describes the API, states,
locking, lifetime, publication, diagnostic schema, build identity and deviations.
The original checkout is not modified by this work. The accepted M01 resources
and M02 Player/evidence remain separate and immutable.

## Implementation and API boundary

The native core replaces the hard-coded `AssemblyShadowPrototype` files with
`AssemblyShadow`, explicit state/error definitions, diagnostics, a canonical-name
index, and private metadata visibility. The removed prototype remains recoverable
from the accepted M01/M02 tags. The runtime adds owned staged images, a private
thread-local metadata/reference resolver, and managed InternalCall adapters.

The nine public managed operations are ConfigureCandidates, BeginTransaction,
StageAssembly, ValidateTransaction, CommitTransaction, AbortTransaction, GetState,
GetAssemblyExecutionMode and GetDiagnosticsJson. Every operation returns an
explicit error code; queries use initialized out values. Native OFF returns
FeatureDisabled before interpreting arguments; Editor/Mono throws NotSupported.

New demo entrypoints are M03Build.Configure, ValidateCompilerInputs,
BuildPlayerBaseline, BuildFixtures, BuildFeatureDisabledPlayer, and
M03EditorValidation.Validate. Compiler-only preflight is not runtime-policy proof.
BuildFixtures must finish a separate actual-byte Editor replay before writing its
immutable validation receipt. `Tools/AssemblyShadow/README.md` records commands.

## Required real Player cases

| Case | Required observation |
| --- | --- |
| T03-01 | P01 commits once and invokes the patched Internal method |
| T03-02 | Randomized five-image staging, full skeletons before metadata |
| T03-03 | Three expected members, two staged, exact missing-closure error |
| T03-04 | Extra candidate refused without retaining an image |
| T03-05 | Duplicate refused without additional retained bytes/images |
| T03-06 | Wrong baseline refused before any image exists |
| T03-07 | Real initializers run once, after publication, in manifest order |
| T03-08 | Throwing initializer seals FailedAfterCommit; business never starts |
| T03-08-Fallback | Separate process invokes baseline with the bound failure marker |
| T03-09 | Separate native-OFF binary returns FeatureDisabled for all nine APIs |
| T03-10 | Acquiring baseline Internal prevents activation |
| T03-11 | Managed enumeration hides private images and records baseline use |
| T03-12 | Concurrent ordinary loads/queries span coherent publication |
| T03-13 | Malformed PDB rejected before allocation; real PDB retry succeeds |
| T03-14 | Invalid states/arguments/ABI remain exact and retry-safe |
| T03-15 | Real private generic metadata remains invisible after Abort |

The verifier must require all modes, bind results to actual Player build GUIDs,
native SHA, fixture/baseline/patch snapshots and Editor replay, and reject
tampering. Passing synthetic verifier tests cannot establish runtime acceptance.
Ordinary HybridCLR OFF regression, restored-ON installation verification, final
paired-source audit and an independent milestone review are also still required.

## Pre-build evidence

- Unity Editor tests: 338/338 passed, none skipped, at
  `_temp/AssemblyShadow/EditorTests-dd3563551b47463db93bb0193856ce20/results.xml`.
- Python tooling: 122/122 passed, including 29 focused M03 tests. Every
  adversarial case starts with a passing complete synthetic 16-mode suite and
  checks the intended rejection reason; CLI testing includes real sidecar names,
  shuffled staging, and case-varied physical assembly names.
- Twenty modified native translation units passed syntax-only checks with the
  feature ON and OFF. This does not establish Unity's full native build/link ABI.
- Final pinned ASan checks passed 23,027 parser assertions and 30 actual VM
  name-folding checks, plus 18,674 private-visibility assertions and five cached
  class-enumeration structural checks. Receipts are
  `_temp/AssemblyShadow/m03-native-regression-a71ce08.json` (974 dependencies) and
  `_temp/AssemblyShadow/m03-visibility-regression-a71ce08.json` (985 dependencies).
- The M01 manifest still hashes to
  `e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d`;
  accepted M02 native SHA remains
  `0ac827495f6371c81cfc7d5bce7bf6d84c4cbf2968ca7682c9388c764002375c`.

## Native-ON baseline build

The two pinned installations produced identical receipt SHA
`d1622f5d82e3d22c18dcd258cfeee510264147afe401792c4469266a60bc0469`.
Strict installed-runtime verification passed with 935 source and 937 installed
files, including the complete pinned demo build source. The real Unity method
then completed successfully in `_temp/UnityExec_20260827_170727.log`, including
the fresh baseline manifest, frozen M01 business semantics and resource reuse.

- Player: `Builds/AssemblyShadow/M03/M03-Baseline-v1.app`.
- Build GUID: `e454ba32269e424bbf25bc254b06968d`.
- Native SHA: `64759be6983519da9fbda314484b9e592b845b6d508e2ede9f9bd07bc3506204`.
- Input snapshot: `_temp/AssemblyShadow/M03PlayerInputs-ba6d2672d8ec4704b3a206b058431597`.
- Snapshot hash: `e7d450626c1e5bfe50eefe99eb05a194e485de36dbe8dfabfdd6576f6b82b32b`.
- Baseline manifest: `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M03-Baseline-v1/baseline-manifest.json`.
- Manifest SHA: `341e29a964f4d5a68bfa09fc0d9b8c7232222b05a99a29153f94bb9a06b22237`.

An independent bounded source/integrity review of demo `a71ce08c` returned PASS
after inspecting the compiler/replay/build bindings and adversarial tests. This
is not the final M03 milestone review; no runtime cases are accepted by that
source-only verdict.

## First live transaction and integration repair

The three v1 patch fixtures and independent Editor replay completed successfully
in `_temp/UnityExec_20260827_171123.log`. The fixture root is
`_temp/AssemblyShadow/M03Fixtures-00bbe514eecb43f1b5821e55df7805c8`;
its replay receipt SHA is
`eb528fc89f693125667e82084aab39200f1a34ded874ad1c01769dcac9ca03cf`.
The actual native-ON Player then failed T03-01 at Validate with
`ReferenceResolutionFailed`, after successful Configure/Begin/Stage. The result
is `_temp/AssemblyShadow/M03PlayerResults-a71ce08-Nc8p4u/m03-T03-01.json`
(SHA `e1cc81fbb0b2aa6fbb94b7db78c5ff917e6e9f7a6af84958f97dc5ee057ace85`).
This failed run is retained, not counted as an accepted runtime case.

The source assumed every AssemblyRef required a physical assembly, while Unity's
compiled patch references the absent logical `netstandard` facade. The stable
allowlist also omitted linked `UnityEngine.CoreModule` because framework proof
deliberately covers only installed system-reference directories. The repair
retains that framework boundary, adds separately byte/identity-bound installed
compiler-library proof, and provides a constrained private facade resolver.
It also captures native diagnostics after a failed assertion instead of leaving
the prior successful Stage snapshot as the apparent final state.

The v2 verifier has 40 passing focused tests and 133 passing tooling tests,
including eight new proof-format/binding regressions. Native facade checks pass
25 policy/TLS assertions and 13 actual-lookup checks in addition to 23,027 parser
and 30 name checks under ASan. Fresh real Player acceptance and the final
independent gate remain pending.

Fresh Editor verification passed 346/346 tests with zero skips at
`_temp/AssemblyShadow/EditorTests-c28758696cc54f9cbdb60362441dad2b/results.xml`,
including eight executable compiler-library provenance tests. The independent
demo source re-review passed this corrected diff; the first compile's dnlib/
System.IO `FileAttributes` ambiguity was corrected before that test run. Native
re-review identified a preauthorization lookup side effect. It was corrected by
checking raw defining-image ownership before materialization/tracing, and the
independent native re-review then passed. The executable lookup regression
includes an unsafe control, zero candidate hooks on the corrected path, and a
later approved provider outside staging TLS. It uses documented metadata/counter
adapters, not a simulated claim of transaction-state correctness.

The corrected native source commits are `fd60cb21a4d0d4c204848c3477d2a30ffd155710`
(HybridCLR) and `0486098099e7e80176401267538499e611b181f2` (IL2CPP). The managed
package remains `460eb5d65923e092d3c8acc7eb912c2942aea645`. These bounded source
reviews permit a fresh v2 build, not milestone acceptance.

## Limits and next gate

Only the transaction foundation is in scope. Full logical assembly enumeration,
all type/reflection/cache routes, execution semantics and Unity resources are
M04-M07. Abort retains private metadata for process lifetime and permanently seals
the transaction. Full memory snapshots are not claimed to be side-effect-free.
The parser is not a complete hostile metadata/IL verifier, and runtime PDB/DLL
debug-identity matching is not established by the envelope tests. Signing and
production next-launch rollback remain M09; current receipts are local integrity
evidence. No Windows or Android result is inferred from macOS ARM64.

Performance/memory acceptance measurements and an independent full M03 verdict
remain pending real Player execution. M04 entry is not yet approved.
