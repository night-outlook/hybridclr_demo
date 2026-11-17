# R03 B2 — Pinned native TypeDef source-path boundary review

**Date:** 2026-11-17 UTC. **Scope:** Primary Implementation, one source-anchored, read-only static inspection of the **inactive** R03 B2 TypeDef source. Not a runtime census, production adapter, Unity build, or Local Validation handoff.

## Exact source and design intent

Working branch for all four forks: `codex/assembly-shadow-r01b-h1`.

| Repository | Pinned source commit |
|---|---|
| `night-outlook/hybridclr_demo` | `71de20359761f75eff4a3d61eb9293df5d8caeb3` — exact new code anchor |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` — unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` — unchanged |
| `night-outlook/il2cpp_plus` | `cecf4b859d50b128e5c0fc6c90cd89e3a452b96a` — unchanged |

The previous host-only `TypeDefSourceCoverageReplay` can prove that every *caller-planned* site is replayed, but its caller may omit the same real path in both phases. Before considering a native source adapter, the current native code must be inspected independently for the actual TypeDef use sites and rejection boundaries. This source audit does **not** claim exhaustive control-flow enumeration; it gives a pinned, actionable list of known obligations and makes source drift fail closed.

The new `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_source_path_boundary.py` reads four exact Git blobs from a clean **pinned native checkout** (worktree contents must match the corresponding `HEAD` tree entry):

| Native file | Git blob SHA-1 |
|---|---|
| `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` | `f988e8a3ebaefe13dde80fa2cb784a673326f395` |
| `libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h` | `75fc8717ed3b54b1aeee583e28671e304ab233e0` |
| `libil2cpp/vm/AssemblyShadowMetadataLifetime.h` | `d2fe09dd51debbbbc71d67b21347f5d971a3cafd` |
| `libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h` | `06ce1e0413089e27c555eeb3b6481e03cf560664` |

The verifier masks C++ comments/string literals, extracts the actual `Capture`, `resolveOwner`, `buildDefinition`, `Composer::Format` and `Composer::Raw` lexical bodies, then checks call order, source categories and explicit rejection expressions. This is deliberately a *source contract*, not an AST, compiler-generated control-flow graph, source epoch, or end-to-end closure proof.

## Source-verified use categories

| Static obligation | Inactive B2 source route | Why an independent census needs it |
|---|---|---|
| `ClassRoot` | `buildDefinition(definition,image,...)` | Registered class root use, independent of existing 128-handle audit |
| `DeclaringAncestor` | `handle=declaring->data.typeHandle` inside `buildDefinition` | Nested TypeDef ancestry and cycles |
| `GenericDefinition` | `Composer::Raw` resolves generic class definition | Definition can differ from observed root |
| `GenericArgument` | recursive `Format(args->type_argv[i],child,depth+1)` | Transitive generic argument use, not just top-level generic types |
| `CompositeClassLeaf` | `makeDefinition(value->data.typeHandle,...)` | Class/valuetype leaves inside arrays/pointers/qualified forms |
| `PrimitiveDefault` | `Peek` then `makeDefinition(primitive->typeMetadataHandle,...)` | Existing primitive class may supply another physical TypeDef |

The verified source retains **three physical `il2cpp_class_for_each` passes** and **two original-V1 physical image observations**, an initial MetadataLifetime Reader and `g_MetadataLock`, plus independent `original_join::CheckFirstOwner` **before** `NonRootOwnerAudit::Note`. The owner helper checks images in original token-valid order and accepts the first matching metadata handle. Existing B2 limits remain exactly **128 combined TypeDefs**, **65,536 metadata index lookups**, and **64 bytes per namespace/simple-name field**.

## Explicit rejection and omission boundaries

Seven anchored expressions are checked:

1. `PreOwnerMissingTypeDef` — missing handle before `resolveOwner`.
2. `AncestryCycle` — repeated declaring TypeDef during ancestry expansion.
3. `InterpreterUnsupportedAncestry` — unsupported physical interpreter declaration shape.
4. `MissingCompositeType` — null TypeKey node or composite recursion over bound.
5. `MissingGenericContainer` — malformed or absent generic source/container.
6. `InvalidArrayShape` — absent/invalid array rank/shape.
7. `MissingPrimitiveDefault` — missing or non-admitted default primitive metadata.

These are **known source boundaries**, not a guarantee that the seven labels exhaust all rejected branches. Several checks occur before any TypeDef ownership is established, and the real producer has no proven independently complete root/nonroot observer. Both successful `resolveOwner` instrumentation and a host replay plan remain insufficient to prove complete observed population.

## Implementation and validation

Only `night-outlook/hybridclr_demo` was modified:

- `Tools/AssemblyShadow/R03IR/TypeDefCensus/verify_native_source_path_boundary.py`: exact native commit/tree/file-blob verification, lexical-scoped source-path inspection, bounded UTF-8 input, fail-closed reporting and **always-false** runtime/acceptance flags.
- `Tools/AssemblyShadow/R03IR/TypeDefCensus/test_verify_native_source_path_boundary.py`: scanner/scope tests, source mutation negatives (first-owner path, primitive path, array rejection, owner/audit call order, native 128 limit) plus pinned-source/CLI provenance test.
- `.github/workflows/r03-b2-native-source-path-boundary.yml`: source-only macOS/Ubuntu CI, checking out exact `il2cpp_plus` commit with only the four source files. No Unity build or native source modification.

**Exact new code commit:** `hybridclr_demo@71de20359761f75eff4a3d61eb9293df5d8caeb3`. [GitHub CI 43999273532](https://github.com/night-outlook/hybridclr_demo/actions/runs/43999273532): **2/2 completed/success** on macOS-15 and Ubuntu-24.04, each using the actual pinned native source and verifying `PinnedStaticBoundaryOnly` with no runtime-success booleans. **Both CI jobs ran all 11 unit tests with no skips** (including six exact-native-source tests), and passed. All negative mutation tests ran against that exact checkout, not just a substitute synthetic fixture. Local Primary test-only scanner tests passed with six native-checkout tests skipped (the true pinned source was available in GitHub CI only). This distinction is preserved in evidence.

## Review findings and stopping point

- **SOURCEBOUND-01 — PASS in exact-source static scope.** The six known TypeDef-use categories, seven known early-exit categories, legacy first-owner rule, order of first-owner proof relative to the 128-entry audit, and current budget constants are all tied to specific Git blobs. Unknown/stale blobs are rejected rather than silently accepted as evidence.
- **SOURCEBOUND-02 — OPEN / HIGH.** The scan is source-text/lexical-scoped, not a verified C++ CFG; six/seven categories are *not* exhaustive. It does not enumerate runtime `Il2CppClass` instances or TypeKey arguments, does not authenticate ignored/rejected paths in a source callback, and cannot prove the closed-world population. A future real source observer must explicitly account for otherwise skipped branches and missing classes before claiming a complete trace.
- **SOURCEBOUND-03 — OPEN / HIGH.** `MetadataLifetimeGate.Reader(Epoch=1)` and holding `g_MetadataLock` do not establish metadata allocation provenance, class/GC lifetime, ABA immunity or coherent VM epoch. The source-tuple fence is not a runtime measurement. No player, real owner lookup latency, worker-stack/RSS profiling or 32-bit ABI was run.
- **SOURCEBOUND-04 — OPEN.** Full original V1 fields14/15, native V2 artifact/envelope, independent receipt/readback and first recovery, historical R03 review FAIL/High items and ancillary R02 historical byte-pin check remain unresolved. An exact source-only CI success must not replace Local Validation or Human Review Gate.

**Disposition:** `PinnedStaticBoundaryOnly`. No native production modification, no selection of fixed/arena capacity, no change to the combined 128 limit, no Local execution authorization, no later milestones. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; PureInterpreter disabled. The next practical step is a **source-lifetime/closed-world enumerator design and explicit human review** before any real VM attachment.
