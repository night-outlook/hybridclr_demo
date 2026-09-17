# M06 execution, generators and warmup acceptance contract

Status: declared before implementation; M06 is not accepted.

## Entry, ownership and immutable bases

M05 passed both independent full gates and its annotated four-repository tag
`assembly-shadow-m05-types` passed the main exact-delta/artifact audit. All four
working branches are `codex/assembly-shadow-m06` at these accepted bases:

| Repository | M05 base |
| --- | --- |
| hybridclr | `7f0da36e1a978abfd22c2c195ecb2741588a5d69` |
| il2cpp_plus | `50194392f08815354b6f230f6d0ddd3ec5f9b0f3` |
| hybridclr_unity | `b132981fa72f8259efde8e8319029b8812858bcf` |
| demo | `71f35b9cd80f92c52a9c6abc6aa4677ecbea48e3` |

The governing scope is the original milestone-06-execution-semantics plan.
The main agent owns this contract, shared schema decisions, integration,
ProjectSettings/scenes/source pins, Unity/Player execution, final verification,
commits and acceptance. Supporting workers have explicit disjoint ownership;
they do not launch Unity/Players or orchestrate other agents. The original demo
and pre-existing Editor remain read-only/uncontrolled. All M00-M05 artifacts,
resource bundles and recorded failures remain immutable. Local commits/tags
are authorized; no push or PR is included.

This is a gate-qualified multi-phase native/runtime/package/demo task. Generic
gate mode is Off, but the declared M06 native/runtime and managed/tooling/evidence
independent full milestone gates are mandatory. M07 implementation remains
closed until both pass and the M06 tag is audited.

## Execution guards and observations

M05 guards type/class use; it does not supply a complete MethodInfo execution
boundary. Add `AssemblyShadow::AssertMethodIsActive(const MethodInfo*, const char*)`
and a throwing/fail-closed wrapper where needed. Append stable error
`BaselineMethodExecution = 21` to both native and managed enums, preserving all
existing values 0..20. A false assertion never permits the caller to continue
into an invoker or method pointer. Retain the first failure and existing
Failed/FailedAfterCommit sealing; fail in release as well as development.

The exact published physical baseline identity, including inflated method
definitions where applicable, determines a forbidden method. Names alone,
metadata tokens alone, a same-name private image or interpreter physical kind
are not sufficient. Stable AOT providers outside the current closure remain
legal, including P01 Contracts/Extensibility. Do not remap a baseline MethodInfo
and silently execute a different body.

Required seams include Runtime::Invoke, actual interpreter entry and nested
direct-call/newobj opcode families, each interpreter delegate target, generated
virtual/interface (including generic) invoke-data helpers and generated bridge/
reverse-PInvoke wrapper entry. Guard constructor/static-constructor dispatch
before execution. Metadata lookup/bridge selection is not misrepresented as
actual invocation. Instrumentation must not initialize baseline classes merely
to diagnose them, acquire metadata locks recursively, or throw across an unsafe
native callback boundary without the existing exception policy.

Direct ordinary nonvirtual AOT calls have no single VM hook. The architecture
continues to exclude them through the complete reverse closure and fixed-AOT
policy; no per-AOT-method dispatch stub is introduced. Native adversarial tests
exercise retained physical MethodInfo guards. A legitimate postcommit logical
lookup cannot be described as a Player injection of a baseline MethodInfo.

Add exactly one public operation, bringing the public API inventory to eleven:

```csharp
AssemblyShadowErrorCode GetExecutionDiagnosticsJson(out string json)
```

This is a separate schema 1, not an expansion of historical transaction or
M05 type-info JSON. ON null native output is InvalidArgument; OFF returns
FeatureDisabled and null JSON. Editor/Mono throws NotSupportedException, not a
simulation. The preserved managed root is AssemblyShadowExecutionDiagnostics;
class rows use AssemblyShadowExecutionClassInfo.

| Root field | Managed type |
| --- | --- |
| schemaVersion | int |
| enabled | bool |
| stateCode | int |
| state | string |
| generation | ulong |
| methodChecks | ulong |
| shadowMethodChecks | ulong |
| rejectedBaselineMethods | ulong |
| baselineClassCctorStarted | ulong |
| shadowClassCctorStarted | ulong |
| interpreterTransformations | ulong |
| shadowInterpreterTransformations | ulong |
| droppedClassObservations | ulong |
| classes | AssemblyShadowExecutionClassInfo[] |

Each class row has exactly: logicalAssembly, typeKey, executionModeCode,
executionMode, physicalImageKind, isActive, cctorStarted, cctorFinished,
hasInitializationException, staticStoragePointer, pointerDetailsAvailable,
staticStorageAvailable. The five identity/address fields are strings;
executionModeCode is int; remaining state/availability fields are bool.

Checks count guard observations, not unique executed bodies. Transformation
counters increment at actual successful interpreter transformation, with a
separate active-shadow subset; they are not inferred from elapsed time.
Baseline/shadow cctor counters concern the current replacement closure, not
legitimate unchanged AOT providers. Record actual cctor-start boundaries and
only already-existing class/static state. Keep observation storage bounded,
report overflow, and reject normal acceptance with dropped class observations.
Release pointer details are unavailable/empty; missing storage is never assigned
a synthetic address. Diagnostics must not manufacture baseline classes or
cause a cctor. State the observation lifetime and any pre-Configure limitation;
startup policy/ordering must separately exclude early business execution.

## Business and closure matrix

New baseline-known execution fixture types may be added to the five business
assemblies; their baseline and patch bodies must have distinct computed results.
Existing frozen-resource component fields/layout remain unchanged. Do not claim
whole-DLL semantic equality with M01 once new baseline fixture types exist;
instead retain M01 bytes and apply the real serialized/resource ABI comparison.

- P01: Internal shadow; Contracts/Extensibility and their other consumers AOT.
- P02: Extensibility, Internal and ExtensibilityConsumer shadow.
- P03: all five business assemblies shadow in provider-first order.

Exercise actual constructor/base/field-initializer chains, explicit and
beforefieldinit statics, separate closed-generic statics, multiple types,
virtual/abstract/sealed/base/accessor dispatch, stable and shadow interfaces,
delegates/events/multicast/closures, generic reference/value types, struct
parameter/return/ref/out/in/boxing/nullable/array boundaries, reflection generic
construction, exceptions/filter/finally/reflection wrapping, async/cancellation
and iterator/Unity-coroutine state machines. Do not fake successful interface
casts, counters, Type identities or marker values.

Use a fixed primitive/object/string-array boundary from the AOT Bootstrap;
no compile-time candidate reference or fixed Bootstrap generic<TShadow>. The
Bootstrap's acquisitions remain finite literal/byte-approved operations, including
warmup dispatch. New managed observer/helper classes must not become an escape
from the established callable-selector and raw-type proof rules.

Initializers remain absent during Stage/Validate, run once in provider order
after active publication, and observe the correct active/stable providers.
The throwing-initializer fixture must produce actual ModuleInitializerFailed,
FailedAfterCommit and no business launch. A separately launched baseline recovery
process is bound to the failed result and actual baseline Player; it is not an
in-process transaction retry or an M09 persistent rollback/security claim.

Development exception observations retain actual patch stack/source lines when
PDBs are supplied. A separately built release/no-PDB case must still correlate
actual method tokens/type identity with hash-bound patch metadata. It must not
be a relabeled development binary. Runtime module MVID remains unsupported;
offline byte-derived MVIDs stay explicitly offline evidence.

## Generator plans, provenance and build order

The existing name-only ShadowRuntimeAssemblyInputProvider is not verified
generator provenance. Preserve its compatible callers, but new production
generator entrypoints must consume explicit, byte-bound current-closure inputs
plus ordinary hot-update inputs. Do not change the Player's hot-update filter,
permanently add all candidates or hide search-root/name collisions.

A full baseline manifest requires a final Player snapshot; a patch manifest
requires that baseline. Resolve this build-order cycle explicitly:

1. Compile immutable, target-platform P01/P02/P03 snapshots. Derive each graph,
   reverse closure/load order and exact DLL/PDB identities from those bytes.
2. Create separate non-deployable generation-only plans with source/target/
   architecture/snapshot/roots/closure/path/hash provenance. They are not patch
   manifests, linked-runtime policy acceptance or provisional Player baselines.
3. Run plan-aware Link, AOT strip, MethodBridge/ReversePInvoke and AOT-generic
   collection/generation in an explicit order. Capture ordinary-only and each
   current-closure input and optimized output inventory plus output file hashes.
4. A single test Player may use the explicitly selected P03 generation only
   after actual P01/P02 ABI bridge/reverse/calli inventories are proved covered.
   Otherwise fail and use an explicit supported union or separate builds; never
   assume that all-candidate names imply signature coverage.
5. Build and capture the actual Player using the recorded generated bytes.
   Verify inputs did not get silently regenerated/overwritten during IL2CPP.
6. Freeze its actual baseline and build real normal patch manifests through
   complete existing policy/resource validation using the captured snapshots.
   Compare final closure/order and every DLL/PDB hash back to its generation plan.

Ordinary generator menu defaults remain unchanged. Expose a read-only optimized
generation inventory rather than treating an opaque output filename as proof.
AOT generic C# comments are not executable instantiation evidence: capture actual
collector type/method/signature inventories and the emitted assembly-name list.
Any required supplementary AOT metadata comes from the correct actual Player's
immutable linked/stripped DLLs, is hash-bound and loaded through the existing
API before business use. Do not infer an AOT allowlist from name prefixes.

## Warmup and backward-compatible manifests

Keep schema-1 patch emission/parsing and frozen M02-M05 artifacts unchanged.
Use an explicit schema-2 patch representation when warmup is present, containing
the existing base proof and a warmup object. Do not silently add null fields to
legacy serialization or reinterpret unknown schema versions. The implementation
may share base validation but must preserve each version's exact wire contract.

Warmup type entries identify assembly and type explicitly. Method entries bind
assembly, declaring type, method name, staticness, generic arity/arguments,
return and parameter signatures. This expands the plan's shorthand to remove
cross-assembly/overload ambiguity. Resolve against verified closure bytes and
reject missing, ambiguous, bodyless/unsupported or out-of-closure declarations.
The complete manifest hash binds warmup; no mutable unverified sidecar controls
execution. The demo admits only its finite compiled literal dispatcher.

Order: Commit and module initializers, resolve active warmup targets,
RuntimeApi.PreJitClass/PreJitMethod, explicit module warmup, then business use.
Constructors use PreJitClass because the existing PreJitMethod accepts MethodInfo,
not ConstructorInfo. Preserve ordinary PreJit behavior. Record real return values,
transform deltas and Stage/Validate/Commit/module-init/PreJit/first/second/virtual/
generic timings. Compare warm and cold fresh processes without an arbitrary
absolute millisecond threshold. Explain any transformation remaining on the
declared warmed synchronous path; timing alone is not proof of conversion.

## Forbidden boundaries and required regression proof

Fail closed for Burst concrete candidate use, P/Invoke signatures containing
candidate types without an explicitly supported frozen ABI, fixed Bootstrap
generic candidate arguments, candidate RuntimeInitializeOnLoadMethod startup,
preloaded candidate assets and execution-order dependencies that precede the
Bootstrap. Preserve valid ordinary/noncandidate paths. Use actual emitted IL
and actual Editor inventory where applicable, not only synthetic descriptors.
Initializer thread/network/persistent-write/scene-start risks must be diagnosed;
normal test initializers only publish bounded in-memory evidence.

## Declared Player modes and acceptance

Every listed case is a fresh process with complete pre-API input integrity and
actual native/managed evidence. The exact mode inventory is:

- T06-01-New-P01/P02/P03.
- T06-02-Statics-P01/P02/P03.
- T06-03-P01, T06-04-P02, T06-05-P03.
- T06-06-Delegates-P01/P02/P03.
- T06-07-Generics-P01/P02/P03.
- T06-08-Async-P01/P02/P03.
- T06-09-InitializerFailure and T06-09-BaselineRecovery.
- T06-10-Warmup-P01/P02/P03.
- T06-11-FeatureOff.
- T06-12-NoWarmup-P01/P02/P03.
- T06-13-ReleaseNoPdb.

This is 28 actual cases, plus adversarial native method-guard tests, generator/
warmup/policy/schema tests and preserved earlier milestone regressions appropriate
to changed surfaces. Native-OFF exercises all eleven APIs and ordinary HybridCLR
loading. The release/no-PDB case has its own genuine build/fixture provenance.

Before acceptance: fresh pinned installation and source verification; full
Editor/Python/native suites; all 28 real modes and strict byte-bound offline
verification; native ON restored; exact source/file/API inventory, generator
input/output proofs, timing and disclosed limits; lossless retained raw evidence;
historical/original-checkout/Editor preservation; committed source/evidence; both
independent full PASS verdicts; authorized local annotated M06 tags and main
post-closeout audit. No M07 implementation or overall completion claim precedes
that boundary.
