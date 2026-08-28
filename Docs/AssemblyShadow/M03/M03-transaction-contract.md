# M03 transaction implementation contract

Status: v4 implementation and required validation complete; independent final
M03 review pending. This contract does not itself claim milestone acceptance.

## Boundary

The M01 prototype is replaced by a process-lifetime, one-transaction system.
The original M01 bundles and accepted M02 evidence remain immutable. M04-M07
still own complete assembly/type/runtime/Unity resolution coverage.

All nine managed operations return `AssemblyShadowErrorCode`, including queries
with `out` values. This makes the native-OFF contract unambiguous: every operation
returns `FeatureDisabled`, before interpreting arguments. Editor/Mono execution
throws `NotSupportedException`; it is not a simulated runtime pass. Explicit enum
values are shared with `vm/AssemblyShadowTypes.h`; runtime ABI version is 1.
Mutations are restricted to the thread that configured the candidates. State,
execution-mode and diagnostic queries are safe on other threads.

`ConfigureCandidates(baselineBuildId, candidateNames, stableAotNames)` extends the
suggested API with an explicit stable-external allowlist. The trusted Bootstrap
derives it from verified target framework references, byte-identical installed
Player compiler libraries and the fixed Bootstrap policy, not arbitrary
assembly-name prefixes. Native registration verifies every
entry against physical AOT metadata, excludes candidates from the external list,
and never accepts an ordinary interpreter assembly as a stable external.
Manifest authenticity is not claimed here; signing remains M09 scope.
The allowlist is intersected with the actual linked Player assembly receipt;
compiler-only facades are not physical AOT providers.

Compiler-library evidence is separate from framework identity-unification
evidence. Its production verifier obtains the active Player compiler reference
list from Unity, rejects links below the installed Editor root, and matches full
assembly identity and SHA-256 against captured input/reference DLLs. A receipt's
sourcePath, an installed file absent from that compiler list, and arbitrary
Bootstrap dependencies grant no authority. The stable-AOT v2 provenance binds
the framework proof, compiler-library proof, linked Player receipt, Bootstrap
policy and final physical names; the independent Editor replay recomputes both
compiler authorities.

An absent logical `netstandard` reference is not fabricated as an assembly.
Private staging binds it to the intersection of the existing finite upstream
framework-provider list and explicitly approved physical stable AOT assemblies.
Candidate and physical-name checks take precedence. Each staged image retains
that provider vector through lazy post-commit resolution. Raw type-handle
ownership is checked before any class materialization or usage trace; a
forwarder cannot touch an unauthorized candidate while being rejected. Optional
missing providers are skipped without widening to the ordinary global registry.
Physical AssemblyRef reflection coverage remains part of M04.
The defining-image ownership check scans at most that provider's typeCount raw
handles; performance optimization is not claimed by these correctness tests.

`BeginTransaction(patchId, expectedBaselineBuildId, closureLoadOrder, abiVersion)`
receives the verified manifest's exact provider-before-consumer order. That order
includes declared ModuleContract edges that need not appear in AssemblyRef.
Native validates exact membership, duplicates, baseline identity and ABI before
allocating any image, and later checks every physical AssemblyRef against it.

## State and lifetime

The states are Disabled, CandidatesRegistered, Staging, Staged, Validated,
Committing, Committed, Aborted, Failed and FailedAfterCommit. Configure is allowed
only from Disabled; Begin only from CandidatesRegistered; Stage from Staging or
Staged (the latter permits precise duplicate/extra diagnostics); Validate from
Staging or Staged; Commit only from Validated. Abort is allowed only before
publication, from Staging, Staged or Validated. Queries do not mutate state.

DLL identity is parsed before reserving a global interpreter-image index. A
rejected duplicate or unexpected member does not allocate another image.
Accepted DLL/PDB bytes are owned by the staged image for process lifetime. All
private skeletons exist before runtime metadata initialization. A thread-local
image-index and AssemblyRef resolver exposes them only to that initialization;
ordinary image/assembly registries cannot see them. Missing closure members never
resolve to a baseline. Staging cannot execute user code or module initializers.

The current interpreter has no complete metadata destructor. Abort therefore
retains bounded private image metadata, never publishes it, and permanently
forbids a second transaction in this process. A fatal metadata failure also seals
the transaction. This is explicit bounded retention, not a claim of rollback or
unload. Pre-allocation argument/identity errors may be corrected in the same
transaction without increasing retained image count.

## Publication and locking

Lock order: transaction, metadata, assembly, short usage/cache locks. Resolver and
usage hooks must not acquire the transaction lock from a VM lock. Diagnostic
state is copied under locks and JSON is formatted afterward. No managed callback
or initializer runs while transaction, metadata or assembly locks are held.

Commit rechecks usage, reserves publication storage, batch-publishes physical
images and assemblies, then swaps one immutable active snapshot and increments
the assembly enumeration version once before readers can observe the batch.
Snapshots are retained for process lifetime, matching existing enumeration
snapshot ownership. Initializers run in manifest dependency order after all locks
are released. Reentrant diagnostic/state calls from them must succeed. Successful
completion freezes the state as Committed. An initializer exception produces
FailedAfterCommit and an error that Bootstrap must treat as fatal for business
startup; it never permits in-process baseline fallback or Abort.

## Acceptance contract

Native diagnostic schema 1 contains `enabled`, `runtimeAbiVersion`, string `state`,
integer `stateCode`, `lastError`, `detail`, `baselineBuildId`, `patchId`, `generation`,
`expected`, `staged`, `retainedBytes`, `closureLoadOrder`, `stableAotNames`, and
`commitOrder`. `assemblies` contains `name`, `mvid`, `skeletonBuilt`,
`runtimeMetadataInitialized`, `published`, `moduleInitializerAttempted`, and
`moduleInitializerRan`. `events` contains `sequence`, `kind`, `name`, `generation`,
and `stagedCount`; metadata-begin events record the full skeleton count.
`baselineUses` contains `name`, `kind`, `detail`, `type`, `thread`, and `timestamp`.
These counters supplement actual managed observations; they do not replace tests
that enumerate assemblies or observe real module-initializer side effects.
All managed diagnostic DTO fields and their type constructors are explicitly
preserved for Unity's linker. Type-level preservation alone does not preserve
unused fields. M03 build capture and independent Editor replay compare the
complete reachable DTO field schema in the exact prelink and linked DLLs;
missing fields cannot be defaulted or reconstructed from a later snapshot.
Native `uint64_t` and ARM64 `size_t` diagnostic scalars map to managed `ulong`,
not signed `long`: six root counters, three event counters, and baseline-use
thread/timestamp. JsonUtility tests cover exact numeric tokens across the
32-bit, floating-point-exactness, signed-64 and unsigned-64 boundaries. The
native-OFF adapter must forward the complete disabled schema from the native
serializer, including FeatureDisabled and empty transaction arrays; a legacy
`{"enabled":false}` stub is not valid schema-1 evidence.
`ordinaryAssemblies` rows (`name`, `isInterpreter`) are captured through the
ordinary native assembly registry with their own coherent `enumerationGeneration`.
That generation can be newer than the transaction-status snapshot if commit
occurs between the two observations. M03 retains physical duplicates after
commit; M04 owns logical enumeration deduplication.

`ordinaryClasses` rows (`assemblyName`, raw `typeName`, `isInterpreter`,
`isConstructedGeneric`, `usesStagedMetadata`) come from the actual public `il2cpp_class_for_each` boundary,
with a separately coherent `classEnumerationGeneration`. Public class and memory
snapshot enumeration filter private generic arguments, nested contexts, arrays,
pointer/byref and unmaterialized type handles. GC retention/cache walkers stay
unchanged. An aborted private image remains hidden forever, and a generation-zero
walk cannot become visible halfway through publication. Formatting never calls
`Type::GetName`, which could resolve metadata or cause baseline use.
The ON ordinary class walk reads only existing initialized AOT/interpreter class
slots. It does not create otherwise-unreported definitions merely to inspect
their initialized flag. The feature-OFF preprocessed walk remains byte-identical
to the accepted implementation. This observational guarantee applies to the
diagnostic class walk, not the full Unity managed-memory-snapshot operation,
which still resolves field types as part of its normal behavior.

M03 builds use a dedicated bootstrap scene with serialized baseline ID and
runtime-ABI hash; fixtures cannot declare their own accepted Player identity.
`M03Build.BuildPlayerBaseline` captures a new real Player while reusing M01 bundles
and checking frozen business semantics. `BuildFeatureDisabledPlayer` captures a
separate OFF build without replacing that baseline, then restores the ON setting.
Every captured Player snapshot has an additional `m03-player-build.json` receipt
binding native compiler arguments, build GUID, input snapshot and native SHA.
`BuildFixtures` finishes by independently replaying the actual compiler/linker,
reflection policy, dependency closure and resource ABI evidence. Only a successful
replay creates the immutable sibling `m03-editor-replay.json`; existing receipts
are never overwritten. `M03EditorValidation.Validate` can replay an existing
fixture set into a separately named receipt. The result verifier requires this
receipt and binds it to the same fixture, baseline, native image, source pins and
patch snapshots. This is local integrity evidence, not a signed attestation.
M03's full-closure P03 fixtures instrument real module initializers in all five
members, so they truthfully declare all five DLLs as changed roots. They exercise
the full P03 transaction, not a claim that only Contracts changed. The accepted
M02 Contracts-only case separately establishes the single-provider reverse closure.

Creating a managed Assembly handle for a registered baseline is itself a use.
The pre-commit `AppDomain.GetAssemblies` invisibility test therefore runs in its
own process and expects the Usage Guard to block a subsequent commit. Successful
commit tests inspect the non-handle-creating native registry before activation.
There is no test-only exemption from the Usage Guard.

Real IL2CPP T03-01 through T03-09, randomized staging, exact missing/extra/duplicate
errors, private ordinary-enumeration observations, real initializer side effects
and reentrancy, initialization failure plus next-process baseline fallback,
baseline-use rejection, concurrent ordinary loads/queries around commit, and
native-OFF plus ordinary HybridCLR regression. Independent review and paired
source-pin/tag audit are mandatory before this milestone is accepted.
