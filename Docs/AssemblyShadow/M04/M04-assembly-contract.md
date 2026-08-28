# M04 Assembly and AssemblyRef acceptance contract

Status: planned implementation; no M04 acceptance claimed.

## Entry boundary

M03 passed its complete native/runtime and managed/tooling/evidence reviews.
The four repositories have local tag `assembly-shadow-m03-transaction` and now
use branch `codex/assembly-shadow-m04`.

| Repository | Accepted M03 commit |
| --- | --- |
| hybridclr | `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9` |
| il2cpp_plus | `0486098099e7e80176401267538499e611b181f2` |
| hybridclr_unity | `0c9302ffa2f420b30774423d4da8305214a78784` |
| demo | `a8c15b754fe033cda9a791eb7e5cd6494b30ccfd` |

These are the M04 diff bases, not future M04 build-source pins. Every new Player
must bind a newly committed executable-source pairing and fresh immutable
baseline/fixture/Player-input artifacts. Existing M00-M03 artifacts are retained.
The original demo checkout and its pre-existing Editor are outside write scope.

## Required behavior

1. Name lookup has explicit Normal, transaction-private Staging, and
   DiagnosticsPhysical contexts. Normal uses one committed active snapshot;
   Staging resolves the complete private closure or fails; physical diagnostics
   never redirect. Resolver internals cannot recursively call semantic loaders.
2. A single canonical-name policy handles simple names, `.dll`, path components
   and upstream case behavior. The active-name map is O(1), without repeatedly
   allocating lowercase strings for lookups.
3. `Assembly::Load`, `GetLoadedAssembly`, `MetadataCache::GetAssemblyByName`,
   AssemblyRef paths, AppDomain enumeration and executing-assembly paths agree
   on active native Assembly identity. Ordinary load hooks, placeholders and
   non-shadow HybridCLR loading remain available.
4. `GetAllAssemblies` exposes one logical active Assembly per canonical name.
   Shadows occupy the baseline's logical position; ordinary dynamic assemblies
   follow upstream order and placeholder/token filtering. Commit invalidates the
   list once. Explicit physical diagnostics remain available separately.
5. Resolve the requester and provider at semantic AssemblyRef boundaries, not
   by globally rewriting AOT assembly/image indexes. Fixed metadata tables and
   generated AOT physical-index invariants remain unchanged.
6. Missing closure members never resolve to baseline. A non-closure AOT consumer
   resolving a closure provider is a closure violation, with requester/provider
   and reference-index/path diagnostics. Runtime violations cannot continue with
   a baseline fallback; development and release paths both fail safely.
7. `Assembly.GetReferencedAssemblies` reports the active assembly's declared
   identities, including versions and public-key tokens. Logical compiler
   facades must not be fabricated as physical Assembly objects or broaden the
   verified stable-AOT authorization from M03.
8. Preserve one-transaction atomic publication, delayed initializers, sealed
   post-commit failure, byte ownership, private generic visibility, and the
   minimum baseline-use guard. Observational tests cannot exempt baseline use.
9. With the feature macro disabled, preserve ordinary lookup order, errors,
   enumeration and dynamic loading. All new hooks have an OFF path.

M05 owns complete type/reflection/cache coverage. M04 must establish active
native Assembly pointer identity and record the Assembly reflection-equality
probe; any remaining type/reflection-only gap must be diagnosed explicitly,
not confused with an Assembly resolver failure.

## Declared milestone validation

All runtime acceptance uses the pinned Unity 2022.3.62f2 macOS ARM64 IL2CPP
Player. Editor tests establish tooling behavior only. Windows/Android and the
later production platform matrix are not inferred from this host.

| Required case | Acceptance observation |
| --- | --- |
| T04-01 P01 | Internal resolves to shadow; Contracts remains AOT; one logical entry each |
| T04-02 P03 | Entire closure resolves to active interpreter assemblies; stable Unity/BCL remain AOT |
| T04-03 staged visibility | Normal queries see baseline only; private references see staged images; no published shadow |
| T04-04 missing closure | Validation rejects missing member without baseline fallback |
| T04-05 external AOT consumer | Closure violation fails with complete requester/provider evidence |
| T04-06 name variants | Simple, suffix, path and case variants resolve consistently |
| Assembly identity | Load overloads, enumeration and executing-assembly observations agree; active declared refs retain full identity |
| Ordinary feature OFF | AOT/dynamic load, placeholder, supplementary metadata, enumeration, resolve callback and duplicate-load behavior remain covered |
| Performance | One million controlled lookups in OFF and committed modes, with raw measurements in benchmark JSON |

T04-03 runs in a separate process: creating a managed baseline Assembly handle
is guarded use and must prevent later activation, as accepted in M03. Successful
commit tests may observe the native registry without manufacturing baseline
reflection handles before publication.

Verification must bind actual result files to native compiler mode, native SHA,
Player build GUID, source pins, immutable baseline/patch bytes and Editor replay.
Assertions and synthetic tests alone are not runtime acceptance. Retain raw
results, exact test output and benchmark measurements; do not reconstruct missing
observations from final snapshots or rewrite historical evidence.

The gate also requires focused native ON/OFF checks, adversarial tooling tests,
the preserved M03 transaction guarantees, a separate ordinary HybridCLR OFF
regression, restored settings/source verification, four-repository scope audit,
file/API inventory, documented deviations and independent milestone review.
Only then may M04 be tagged and M05 begin.

## Implementation risks to resolve

- Logical enumeration changes the M03 physical-duplicate diagnostic assumption.
  Keep explicit physical observations distinct from the public logical view;
  any revised regression must preserve the original publication/private-state
  guarantees, not simply accept missing evidence.
- Absent `netstandard` and similar compiler facades have declared identities but
  no linked physical Assembly. Reflection identity reporting and constrained
  type-provider resolution are separate responsibilities.
- Requester authorization must not misclassify a baseline pointer that semantically
  belongs to the active closure, nor silently exempt a genuine external AOT
  consumer. Fixed Bootstrap reflection entrypoints retain their verified policy.
- Snapshot publication, assembly locking and reference diagnostics must not
  introduce lock inversion, partial views or per-lookup unbounded allocation.
- Existing M01 resource bytes and serialized identities must remain frozen even
  when additional patch-only probes are introduced.
