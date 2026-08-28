# M05 Type, reflection and cache acceptance contract

Status: declared before implementation. M05 is not accepted.

## Entry and ownership boundary

M04 passed both complete independent gates and has local tag
`assembly-shadow-m04-resolution`. M05 uses `codex/assembly-shadow-m05` in all
four repositories. These immutable commits are the M05 diff bases:

| Repository | Accepted M04 base |
| --- | --- |
| hybridclr | `39eca7a2cc9c8e414f29701629da268e4e213e09` |
| il2cpp_plus | `229f9450c0ebe2293da2bffbfc35f160f18c69de` |
| hybridclr_unity | `deee300670730fbc4d864e82fa70e7b022581afe` |
| demo | `3abeb0bd10c26b24a536fd18a25a79d4f97eb30b` |

The governing scope is
`Documents/HybridCLR_AssemblyShadow_Design_and_Plans/plans/milestone-05-type-reflection-resolution.md`
and design sections 13-14, with the recorded M01 Unity resource observations.
The main agent owns integration, ProjectSettings/pins/scenes, Unity and Player
runs, commits, final verification and acceptance. Supporting writers have
disjoint explicit file ownership. Reviewers remain independent and read-only.
The original demo and its pre-existing Editor remain outside write scope.
No historical M00-M04 snapshot, receipt, observation or resource is rewritten.

## Required implementation properties

1. Map type handles, never reinterpret an already-created baseline object.
   Resolve definitions only against the committed snapshot. Staging metadata
   stays private and physical fixed AOT index APIs retain their original meaning.
2. Definition TypeKey uses logical assembly, namespace, declaration/nesting
   chain, case-sensitive metadata name and metadata generic arity. No token,
   version or runtime pointer is a stable logical key. Missing definition,
   kind mismatch and arity mismatch fail explicitly, without baseline fallback.
3. Rebuild composite types from active components: generic definition and every
   argument, arrays/rank, pointers and byrefs. Keep generic-parameter context
   and supported qualifiers; never copy a baseline generic-instance pointer
   onto a shadow definition. Unsupported pinned-runtime forms must be diagnosed.
4. Image/Class/type-name queries and reflection Assembly/Module/Type cache
   access resolve before forming keys. Inflate/type reconstruction must happen
   outside reflection-cache locks and obey existing metadata/transaction order.
   Non-shadow fast paths preserve upstream behavior.
5. Class initialization cannot silently redirect and pretend the original
   pointer was initialized. Resolve at semantic callers first; reject direct
   unsafe baseline initialization after publication. Allocation/boxing/array
   boundaries may remap only a compatible handle before an object exists.
   Validate kind/layout and fail safely on mismatch; do not initialize a
   baseline business class merely to manufacture comparison evidence.
6. Member objects must use active declaring/reflected classes and active
   signature types. Never remap a method/field/property/event by metadata token.
   If a real baseline-member caller requires remapping, use a complete canonical
   member signature; otherwise reject it with a precise diagnostic.
7. Record first baseline use at reflection exposure, class initialization,
   vtable/static storage, allocation and observed Unity binding boundaries.
   Physical inventory alone is not use. Early use prevents commit and retains
   assembly/type/kind/thread/sequence detail. Existing transaction sealing,
   initializer ordering and byte ownership remain intact.
8. P01 keeps stable AOT Contracts while Internal is shadow; P03 uses shadow
   Contracts and every consumer in its reverse closure. Interface, cast,
   assignability and reflection identities must hold in both cases.
9. Active ManifestModule identity, type lookup and enumeration must be proved
   through the pinned managed/native call chain. Current unsupported ordinary
   OFF behavior is not silently changed. M05 does not add module MVID support
   or populate unsupported runtime GUID observations from expected artifacts.
10. Keep exact finite reflection/Bootstrap admission. A new test does not
    authorize arbitrary dynamic names, file/byte loaders, AssemblyName aliases
    or unverified providers. Preserve M03/M04 schema and proof domains.

The separate raw-query admission and its byte-bound compiler/linker proof are
declared in [M05-raw-type-admission.md](M05-raw-type-admission.md). They leave
the observed API calls intact; they do not replace enumeration with expected
type handles or assert that a runtime transaction has committed.

## Type-resolution diagnostic API

Add `AssemblyShadowRuntime.GetTypeResolutionInfo(Type type, out string json)`
returning the existing stable `AssemblyShadowErrorCode`, consistent with the
existing diagnostics API. The preserved `AssemblyShadowTypeResolutionInfo`
DTO parses the separate flat schema below. Editor/Mono execution throws
NotSupportedException, not a simulation. Native OFF returns FeatureDisabled
and null JSON; ON null input/output is InvalidArgument. The query does not
change transaction state. Existing nine public APIs and schema-1 transaction
diagnostics retain their contracts.

| Field | Managed type | Meaning |
| --- | --- | --- |
| schemaVersion | int | Exactly 1 for this separate schema |
| logicalAssembly | string | Actual logical owner of the queried type |
| executionModeCode | int | Existing registry mode, 0 or 1 |
| executionMode | string | AotBaseline or InterpreterShadow |
| isActive | bool | Input and all relevant components belong to the active view |
| physicalImageKind | string | Actual input image kind, Aot or Interpreter |
| typeKey | string | Stable definition key or canonical composite representation |
| inputTypePointer | string | Actual input type address when development details are available |
| activeTypePointer | string | Actual resolved type address when available |
| baselineTypePointer | string | Actual known baseline type address, never synthesized |
| pointerDetailsAvailable | bool | False requires empty address strings |
| baselinePointerAvailable | bool | False requires an empty baseline address |
| containsShadowTypes | bool | Definition or recursively contained component is shadow |
| definitionCacheHits | ulong | Bounded native resolver counter |
| definitionCacheMisses | ulong | Bounded native resolver counter |
| compositeRebuilds | ulong | Bounded native resolver counter |
| allocationRemaps | ulong | Bounded native resolver counter |
| guardFailures | ulong | Bounded native guard counter |

Addresses are transient diagnostic evidence, not stable identities or cache
keys in persisted manifests. Do not materialize a baseline class to fill an
optional address. Registry execution mode is separate from physical interpreter
kind, including ordinary non-shadow interpreter types. Counters must not require
an unbounded event allocation for each lookup. Native, DTO, linked-schema and
offline-verifier field inventories must agree, including zero/false values and
the full unsigned range. Raw JSON is retained with the typed observation.

## Declared validation matrix

All runtime acceptance uses newly pinned Unity 2022.3.62f2 macOS ARM64 IL2CPP
Players and fresh M05-only baseline, fixture, snapshot and result roots. Editor
tests validate tools; they do not replace Player observations. Split logical
cases into fresh P01/P03 or negative processes where needed.

| Case | Required acceptance |
| --- | --- |
| T05-01 | Literal type-name, nested/generic syntax and supported resolver-overload paths return active types in P01 and P03 |
| T05-02 | Assembly.GetTypes/DefinedTypes/ExportedTypes expose patch-added types and exactly the patch type inventory |
| T05-03 | Repeated Assembly/Module/Type/member queries preserve managed identity after resolve-before-key |
| T05-04 | Early baseline Type exposure prevents commit with BaselineAlreadyUsed and actual first-use evidence |
| T05-05 | Nested, generic, generic-argument, array/rank, byref and supported pointer reconstruction retain active components |
| T05-06 | P01 Internal instance implements and casts to stable AOT Contracts; assignability agrees |
| T05-07 | P03 instance and consumers use shadow Contracts; no baseline interface leaks |
| T05-08 | Frozen M01 prefab and scene load after commit with active runtime types, unchanged serialized values and exact old resource hashes |
| T05-09 | Deliberate incompatible layout is rejected by DLL-only resource tooling and independently by the runtime guard without fallback |
| T05-10 | Load, Type.Assembly, AppDomain, ManifestModule.Assembly and Module type queries agree on the active objects |

Add explicit native-OFF/ordinary loading regression, diagnostic API invalid/OFF
cases, adversarial tooling/schema/type-inventory tests, and preserved M03/M04
native and Player invariants as appropriate to changed surfaces. Capture raw
timing/memory counters for affected resolver/cache paths; do not turn a focused
benchmark into a production-performance claim.

An intentionally rejected layout fixture is test-only defense-in-depth evidence,
not an admitted deployment patch or a waiver of resource ABI validation. Normal
fixtures must pass the complete build policy before activation. Verify the
guard against actual bad bytes, not only a label or synthetic result.

## Unity evidence and integration risks

M01 proves selected native symbols and actual asset/object identities, but does
not prove a universal MonoScript-to-Object::New call chain. MonoScript.GetClass
is Editor-only in this pinned setup. Player acceptance must use actual frozen
Prefab/Scene binding, component.GetType and supported native diagnostics; no
invented direct Player MonoScript invocation or unobserved allocation hook.

Module.GetType's concrete RuntimeModule override and native entrypoint must be
verified from linked managed IL before implementing the missing ManifestModule
surface. Native MVID remains unsupported. Resource layout and class-init checks
must distinguish safe metadata inspection from business use; private staging,
lazy cache creation and lock ordering must not leak or deadlock.

## Acceptance and continuation gate

Before M05 is tagged: commit the complete source pairing; install/build fresh;
run the complete matrix and strict byte-bound replay; retain raw outputs,
source/file/API inventories, old-resource audits, performance and limitations;
restore native ON; audit all four repositories and the original checkout; and
obtain independent native/runtime plus managed/tooling/evidence PASS verdicts.
The declared milestone gate remains required even while generic skill gate
mode is Off. No M06 implementation starts before M05 is accepted and tagged.
