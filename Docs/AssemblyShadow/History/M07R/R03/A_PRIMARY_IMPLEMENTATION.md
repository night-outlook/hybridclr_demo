# R03 A — conservative evolution semantics: Primary Implementation

Date: 2026-09-30. Status: **implemented candidate; awaiting initial Local native evidence, not R03 acceptance**.

The owner explicitly initiated R03 after accepted R02. This cycle implements the conservative V1, graph and method path plus a focused executable validation batch. It does not enable PureInterpreter structural expansion, cross a Human Review Gate, or declare the complete R03 stage finished.

## 1. Authority and scope

Read `../../../Plan/DESIGN.md`, `../../../Plan/stages/R03-evolution-semantics.md`, `../../../Plan/HUMAN_REVIEW_GATES.md`, and the current `../../../Handoff/WEB_TO_LOCAL.md`. The old R03 references to `design.revised.md` and `validation-matrix.md` are historical names; the canonical architecture is `Plan/DESIGN.md`. `A_VALIDATION_MATRIX.md` supplies this cycle's explicit requirements without replacing the H1-oriented canonical matrix or reducing R03 exit conditions.

All repositories use `codex/assembly-shadow-r01b-h1`:

| Repository | Exact source revision |
| --- | --- |
| night-outlook/hybridclr_demo | f5f5712459fdf67e2b748ddeab8e6540bffd3d95 |
| night-outlook/hybridclr | 041c0cbb42d3e64e54fe605673d99799b5d63893 |
| night-outlook/hybridclr_unity | 120bb01be680cec0375002a0823552d66d34b84c |
| night-outlook/il2cpp_plus | 1abb6bcaa85226f08c67f9da65edb3c58e8cb399 |

The demo source anchor above is the executed host CI source, not the later documentation transport commit or an executed Unity Player. The final handoff prompt identifies the latest pushed transport HEAD; Local must require a documentation-only delta after the anchor and execute exactly that transport revision. `source-pins.json` contains the three exact external sources. No Player has executed this candidate yet.

## 2. Implemented design

### Safety closure and target load order

`AssemblyReferenceGraph` now stores target actual AssemblyRefs in `loadForward`. The original forward/reverse graph still includes target, baseline and declared impact edges. ReverseClosure computes reachability and validates execution roles, not topological sortability. LoadOrder sorts only actual target dependencies and still rejects a genuine target cycle with `DependencyCycle` and its closed path. Generation-plan and patch-builder callers share this implementation.

Historical edges remain necessary for closure even when removed in target. They no longer dictate target initializer order. No SCC loader or general initializer ordering facility was introduced. Installation-baseline semantic comparison remains unchanged; v2 still includes changes from v1 even when its network delta omits them. `NormalHotUpdate` cannot be promoted into a baseline-backed Shadow closure, including when an erroneous capability flag is true. Existing ordinary-hot-update bootstrap entry rules remain separate.

### Conservative NativeLayoutAdmissionV1

`NativeLayoutAdmissionValidator` reads independently supplied DLL bytes using dnlib, never Assembly.Load or attribute/cctor execution. It rejects definite incompatibilities in field order/signatures/removal, private-reference append, nonprivate append, value-type growth, open-generic structural change, kind/parent/interface/layout changes and generic constraints. Private primitive append remains conditional on native offsets and size. Unknown effective offsets/packing/size are `NeedsNativeProof`, not compatible.

`NativeLayoutAdmissionSnapshot` binds this screen to the verified **linked Player DLLs** and current compiler snapshot. The pre-strip baseline remains the semantic-root input but is not misrepresented as the physical native layout input. `ShadowPatchManifestBuilder` performs the screen before creating output and writes `native-layout-admission-v1.json`. This is a versioned diagnostic sidecar, not a new unversioned field in the strict legacy manifest and not runtime authority.

`ValidateStagedImage` performs metadata-only comparison while the complete private resolver is active. It is called after interpreter metadata preparation and before image finalization/readiness. Existing declarations are matched physically to the original AOT image. Changed materialized layouts reuse the existing CheckLayout implementation; unavailable changed layouts reject rather than manufacture proof by initializing old types. Open-generic structural changes remain rejected. Unchanged open types still require constructed physical allocation proof later.

The staging pass neither creates business objects nor invokes cctors, publishes a snapshot, changes object klass, nor issues an allocation certificate. Existing allocation caching, baseline-use checks, poison checks and old-AOT execution guards remain in place. Existing numeric error 16 is preserved; diagnostic text identifies V1 and the earlier phase. A metadata-phase error retains the transaction's Failed/RestartRequired policy, not an invented successful Abort.

The screen has a 1,048,576-type-row bound per image and existing signature depth/count limits. This is a work bound, not a capacity promise. Transient indexing and baseline metadata materialization can add startup time and memory; they require measurement. Detailed native diagnostics are bounded to sixteen records at diagnostics level 2.

### Logical method identity and compatibility

Managed logical keys encode declaring type, method name, generic arity, calling shape and complete CLI signature using a bounded length-prefixed encoding. Tokens, virtual slots, addresses and optimization hints are not lookup identity. Compatibility separately checks invocation/dispatch attributes, semantic implementation flags, generic constraints and parameter metadata. Ambiguous or missing matches reject.

The native reflection resolver uses its own equivalent representable-shape key, then separate compatibility checks before caching an actual active MethodInfo. Method generic parameters use owner-local ordinals rather than recursively embedding the old physical method key. The physical execution guard never calls this remapper to approve an old AOT method.

**Native representation limit:** the pinned MethodInfo/Il2CppType ABI does not retain every CLI custom-modifier identity or function-pointer calling convention. Such exposed unsupported shapes are rejected instead of using equal modifier counts as proof. This is not a complete arbitrary-CLI method compatibility claim. The managed encoder has broader descriptive coverage than the native remapper; additional real metadata/native negative cases remain necessary for full R03.

### PureInterpreter boundary

No private-reference layout expansion is enabled. A type is not eligible merely because its file is C# or resource ABI is unchanged. The later eligibility proof must cover old objects, Unity native binding, fixed-AOT concrete consumers, value representation and generic/interop boundaries. The stage places that expansion after predictable V1 behavior. The initial Local batch supplies that missing empirical evidence; it does not authorize Local to design an expansion or globally remove CheckLayout.

## 3. Validation infrastructure

`Tools/AssemblyShadow/R03/` contains source-pinned .NET host projects, actual DLL generators, an isolated Unity project template, native test-only MethodInfo observer, strict Player verifier, filesystem/evidence tests, and one batch runner.

The first corpus has 18 baseline/target/cumulative DLLs. The shared admission/method suite creates 70 independently reopened DLL inputs across 35 cases. A second 15-DLL Player corpus uses **static** reference fields for dependency reversal, avoiding a misleading failure caused by changed instance layout. The original host inputs are retained separately. The native TypeKind test deliberately compares a reference baseline to a value target; it is not relabeled as the separate host value-growth case.

The native probe reads real physical baseline MethodInfo rows, records actual token/slot changes and maps to actual active metadata. Its optional old-method guard check occurs outside the metadata scope and never executes the old body. Its exact additive source is separately hashed in the isolated install/build receipt; it is not part of the production source installation receipt. Reference/candidate Players use identical new test harness and current managed package; reference native cores are the accepted R02 sources, not the historical accepted binary.

The 36-cell runner creates four isolated projects/builds, executes nineteen fresh-process Player cases, runs full package Editor tests with exact mandatory-case matching, reruns host contracts, and verifies source authority before and after. Independent cells continue after unrelated failures; dependent cells become Blocked. There is no semantic retry or expectation relaxation.

Warm allocation observations use a fixed preparation sequence, then 10,000 measured allocations. This is certificate-reuse evidence, not a cold-performance comparison. Evidence records real run IDs, PIDs, command timestamps, input/build hashes and raw results. The focused archive excludes rebuildable SDK/caches/worktrees explicitly and retains their live roots and inventories. It must not be called the full R02 evidence seal. Final ready status is written only after successful sealing and member authentication.

## 4. Changed source inventory

Package: `Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs`, `EvolutionSignature.cs`, `LogicalMethodIdentity.cs`, `NativeLayoutAdmissionValidator.cs`; `Build/NativeLayoutAdmissionSnapshot.cs`, `ShadowPatchManifestBuilder.cs`; `Tests/Editor/AssemblyShadow/GraphAndInputTests.cs`, `R03EvolutionContractCases.cs`, `R03EvolutionContractTests.cs`; new Unity meta identities.

Native: `il2cpp_plus/libil2cpp/vm/AssemblyShadowLogicalMethod.h`, `AssemblyShadowTypeResolver.h/.cpp`; `hybridclr/hybridclr/metadata/StagedAssembly.cpp`.

Demo: the complete `Tools/AssemblyShadow/R03/` subtree; `.github/workflows/r03-primary.yml`, `r03-native.yml`; canonical status/handoff/stage links and this R03 history package. No old raw evidence or Local-owned report was rewritten.

## 5. Primary review and issue disposition

This is Primary's design-to-source/test self-review, **not an independent reviewer or a Human Review Gate approval**.

| Finding | Disposition and limit |
| --- | --- |
| ASR-004, resource/native admission mismatch | Implemented conservative Editor screen and native prepublication path; host cases pass. Actual rejection phase and old-resource regression are not yet proven. |
| ASR-005, physical slot in logical method identity | Implemented key/compatibility separation; real DLL managed tests pass. Actual native slot mapping and old-AOT guard remain Local tests. |
| ASR-006, baseline/target pseudo-cycle | Fixed in production graph; actual DLL baseline failure and candidate success observed. Genuine target-cycle host rejection remains. Native reversal/cycle evidence is still required. |
| Ordinary role accidentally promoted by flag | Fixed explicitly, including negative regression. |
| Using pre-strip bytes as native baseline | Corrected to independently verified linked Player inputs. |
| Native graph test conflated with field evolution | Split graph-only static-field Player inputs from the original counterexample corpus. |
| Unbound/fabricated or incomplete evidence | Strict identities/phases, negative verifier tests, immutable ledger and post-seal final status; synthetic tests clearly separated from empirical evidence. |
| Host API compile missing dependencies | Corrected host project to compile actual Runtime root sources, not API stand-ins; final host CI passes. |

## 6. Remaining ownership and stop

The **earliest unfinished step is actual Unity/IL2CPP execution of the three counterexamples and this integrated conservative candidate**, followed by Primary reconciliation. Local receives executable tools, not a request to implement them. Unexpected build/API/runtime failures must return to Primary with exact source and logs; only independently verifiable trivial corrections are within Local's ownership.

Full R03 still needs source-bound production patch-builder/generation integration evidence, complete affected M07 P01/P02/P03 and old-resource P04/P05 regressions, stack-trace/interface/generic/negative-method coverage beyond this focused corpus, affected startup/capacity tests, startup cost/memory measurement, independent full stage review, and the gated PureInterpreter eligibility/expansion work. These remain **Primary-owned**, not waived or assigned to Local to design. H2 follows complete R03, not this batch.

R02's accepted CPU residuals and the original H1 +18–19 MiB RSS risk remain visible through H2. No production SLA, RAM budget, release approval or disappearance of historical cost is claimed.

Rollback: preserve all evidence, restore the coherent original four-source tuple and rebuild a separate Player. Do not mix native/package/source pins, replace retained Players in place, remap existing objects or attempt in-process rollback after publication. A failed/poisoned process must terminate under its recorded recovery disposition.
