# M05 literal-bound raw type-query admission

Status: implementation contract; not runtime acceptance.

## Purpose and boundaries

M05 must observe actual `Assembly.GetTypes`, `DefinedTypes`, `ExportedTypes`,
`Module.GetTypes` and `Module.GetType(string,bool,bool)` results. The existing
finite reflection binding transforms a declared operation into a guard and,
for finite enumeration, an explicit type array. That remains a valid older
contract, but cannot be substituted for the raw APIs under test here.

Introduce a separate static admission domain. It proves an exact operation
on a literal-bound provider in actual compiled bytes. It never certifies a
runtime commit, changes an API result, accepts an arbitrary receiver, or
weakens the existing reflection binding, runtime-reference or Bootstrap rules.

## Configuration and compiler binding

`ProjectSettings/AssemblyShadowRawTypeAdmissions.json` has exactly
`schemaVersion` (1), `policy` (`assembly-shadow-raw-type-admission:1`) and
`sites`. Each site has exactly these twelve fields, in this canonical order:

`id`, `consumerAssembly`, `declaringType`, `methodSignature`, `methodHash`,
`operationIndex`, `operationSignature`, `providerAssemblyIdentity`, `typeName`,
`throwOnError`, `ignoreCase`, `reason`.

Method identity, complete normalized IL fingerprint, operation index and
signature come from the actual compiler output, not a source-line guess.
Enumeration has an empty type name and false flags. Module lookup names a
literal baseline-known type with the exact recorded overload and flags.
The reason explains intent; it is not evidence or an override.

The reserved compiler define is
`ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_` followed by the lowercase SHA-256 of the
raw configuration bytes. Callers cannot supply a control define themselves.
Existing snapshot hashing already binds every define and every DLL/PDB, so
this new domain does not reinterpret historical snapshot schemas or hashes.
The canonical configuration hash is separate from the raw byte hash.

## Verification and policy acceptance

The initial operation vocabulary is exactly the five APIs above. Each site
must contain the immediate literal `Assembly.Load(provider)` receiver chain,
optionally followed by `ManifestModule`, then its declared operation. Only
harmless no-ops may intervene. Receiver aliases, helper-returned assemblies,
branch entry into the middle of a chain, untrusted API lookalikes and other
overloads are rejected. The complete method fingerprint binds all branches.

The metadata verifier derives the provider's full assembly identity, DLL hash
and TypeDef inventory digest from actual supplied bytes. It does not infer
assembly roles from a name or from current project settings. The compiled
policy validator separately requires an actual runtime consumer and an actual
non-Bootstrap shadow-capable runtime provider. Reference-only, filtered,
ordinary hot-update and unregistered providers cannot receive this admission.

Only an internally constructed, identity-bound verified site reaches the
scanner. It covers the exact raw operation and its literal receiver load;
there is no public verified flag or method-name waiver. Ordinary dependency
edges still apply to non-Bootstrap consumers. Other acquisitions in the same
method retain their existing checks.

Admission also binds provider selection at the helper boundary. A Bootstrap
helper cannot broker its finite providers to another runtime assembly while
leaving that recipient out of their reverse closure. Exact requirements
propagate through static and Bootstrap forwarding calls and actual finite
reflection/declared paths; each non-Bootstrap selector recipient must have the
truthful provider dependencies required by the normal graph. Callable selector
exposure through method tokens, delegates (including forwarding lambdas), or
virtual/interface registration must be attributed to its recipient or rejected.
Bootstrap itself remains outside the patch closure and receives no manufactured
Bootstrap-to-candidate graph edge.

The static boundary conservatively projects those finite providers across
actual incoming AssemblyRefs to a selector-bearing Bootstrap assembly,
including transitive incoming Bootstrap references. A non-Bootstrap caller
therefore needs truthful direct provider dependencies even when its particular
reference appears unrelated to a selector. This deliberate over-approximation
closes field/signature/composite metadata routes without guessing which
reflection operation will eventually expose the selector. It does not project
providers onto Bootstrap's outgoing diagnostic or framework references.

Return types alone do not define selector outputs. Actual selected-value writes
through caller-owned mutable containers, byrefs/indirect stores or custom
delegate Invoke parameters must be attributed or rejected. Unproved writes to
caller/global/unknown locations fail closed; fresh local materialization and
read-only opaque inputs remain distinct. Composite token checks inspect their
components rather than only a generic outer definition.

This boundary is about selecting a named provider and exporting reflection
handles or a callable selector. It does not reject already-selected `Type`
values passed to pinned diagnostics, scalar/DTO observations, ordinary iterator
scheduling or completion callbacks. Those paths do not gain authority to select
a provider. Proof is derived from actual method bodies and AssemblyRefs; a
declared edge alone cannot invent a selector or a missing compiled dependency.

The demo isolates twenty-five sites in five preserved finite-switch methods
of `M05BoundTypeQueries`. Each method has one arm per candidate. Each returns
the actual raw API result directly. Materialization, inventory comparison and
runtime assertions remain outside those methods. No expected-type array is
generated into the runtime path.

## Immutable evidence and linked bytes

Every controlled snapshot contains `RawTypeAdmissions/configuration.json`
and `RawTypeAdmissions/compiled-evidence.json`. Successful Player snapshots
also contain `RawTypeAdmissions/linked-evidence.json`. Their expected file
inventory is exact. Proof JSON is deterministically regenerated from the
configuration and already hash-bound snapshot inputs, then compared exactly;
it is not trusted as an independent claim.

Linked verification uses the existing separately verified captured IL2CPP
facade and linked framework profile. Both the original compiled method and
the actual linked method must agree under only that profile's proven per-type
retargeting. No broad assembly-name substitution, host-installed fallback or
missing linked method is accepted. A raw-query Player snapshot without the
captured retargeting proof fails closed. The older proof domain and its
schemas are unchanged; the new proof consumes its verified evidence.

Copying a baseline, resource snapshot or patch copies the new domain with
hash checks. Historical snapshots without the control define must not contain
the new evidence. Replay verifies both domains; M05's independent offline
verifier derives the same sites from actual PE/IL bytes, not receipt labels.

## Acceptance tests

Require positive compiled and actual linked cases plus negative tests for
configuration/control mismatch, changed method/operation/provider bytes,
untrusted BCL signatures, receiver aliases and control-flow entry, invalid
provider roles, missing/extra evidence, forged proofs, and unauthorized linked
retargeting. Preserve the full older test suite. Real M05 Player observations
must still prove active inventories and managed identity after commit; static
admission is not a replacement for any runtime case.
