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
