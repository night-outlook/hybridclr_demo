# M03 native transaction and staging

Status: source checkpoints and pre-build verification are complete; real Player
acceptance is pending. No M03 milestone tag or permission to enter M04 is claimed
here.

## Source checkpoints

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
- Earlier focused ASan checks passed 23,027 parser assertions and 30 actual VM
  name-folding checks, plus 18,674 private-visibility assertions and five cached
  class-enumeration structural checks. Final pinned receipts remain to be captured.
- The M01 manifest still hashes to
  `e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d`;
  accepted M02 native SHA remains
  `0ac827495f6371c81cfc7d5bce7bf6d84c4cbf2968ca7682c9388c764002375c`.

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
