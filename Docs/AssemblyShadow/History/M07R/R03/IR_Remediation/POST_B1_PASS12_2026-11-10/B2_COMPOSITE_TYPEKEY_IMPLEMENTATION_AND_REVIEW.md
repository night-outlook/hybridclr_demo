# Unicode source extension to prior composite checkpoint (2026-11-11 UTC)

The earlier 26-native/4-demo composite source report is historical. Current native source db5354a9befd5cfd02f907d3169c8106e0a29305 uses **original VM Unicode UTF-16 casefolding** from AssemblyShadowName.h, a bounded folded UTF-8 assembly TypeKey encoder, and new fail-closed receipts. The exact manifest now contains 38 native files and four demo mirrors. See [new Unicode implementation and independent source review](B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md) for source/test scope and CI status. Full primitive/open field15 semantics, terminal field14/15 lifetime, V2 writer and actual Unity Player remain blocked. WEB_TO_LOCAL CLOSED / NO EXECUTION.

---

# R03 B2 — composite TypeKey implementation and independent source review

Date: 2026-11-11 UTC. Owner: Primary Implementation. Source scope: **inactive native source and host evidence only; NOT full V2**.

## 1. Exact source, historical boundary and intent

| Repository | Working branch | Source revision |
| --- | --- | --- |
| night-outlook/il2cpp_plus | codex/assembly-shadow-r01b-h1 | 272f3077eee50835284e27855352fe300362ad79 |
| night-outlook/hybridclr | same | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | same | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/hybridclr_demo | same | verify current remote HEAD on consumption |

The source manifest at Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json pins **26 native Git blobs and four independently tested demo source mirrors**. Historic B1 oneuse-12 focused real macOS Unity/IL2CPP Player **19/19 PASS** at executed demo 2d690bb2f7234ddcbee339f9da7125d687f5ed45 and native 8aa8d09319a89b55b2496bcc2c69ccc69cb57be9 remains immutable and consumed; it is not B2 evidence.

This increment extends the source-only bounded actual native physical AOT TypeDef capture, which previously authenticated concrete generic argument TypeDefs using the original registered AOT assembly registry and physical class enumerator. It preserves the original V1 getters, first-error producer, R02 serializer, source lifetime Reader, original assembly and metadata locks, registration witnesses and fail-closed admission fences.

## 2. Implementation and exact grammar

- New native libil2cpp/vm/AssemblyShadowOwnedCompositeTypeKey.h: noncopyable/nonmovable C++11 allocation-free fixed 4096-byte owned composer. It accepts previously verified canonical metadata definition keys, constructed generic arguments, pointer, SZARRAY, multidimensional ARRAY (signed sizes and lower bounds) and Il2CppType qualifiers; all failures poison and scrub output.
- Native libil2cpp/vm/AssemblyShadowOwnedExecutionRows.h: adds composite type as an explicit trusted key input; arbitrary raw string keys remain forbidden. Max 1024 rows, 2048 registration slots and 256 KiB owned text.
- Actual inactive libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl: recursive argument walker with eight levels, max 16 arguments per constructed generic, max 32 entries per array dimensions list, and the original 65536 metadata-owner-lookup cap. Every CLASS/VALUETYPE TypeDef argument leaf is matched against the registered physical AOT image inventory before dereference under the initial Reader and original g_MetadataLock. Two physical class enumeration passes, raw assembly table before/after comparisons and R02/registry/B1 source fences remain.
- Native libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLive.h: receipt records specific composite shapes and depth/node counts. A source failure clears all positive receipt flags, owned rows and frozen record.
- New NativeHostTests/AssemblyShadowOwnedCompositeTypeKeyHost.cpp tests original byte spelling, signed dimension lists, nested composition, capacity, missing/aliased children, reuse and allocation exclusion; driver stays outside libil2cpp to avoid global new/delete symbols in GameAssembly.
- Updated NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp compiles the actual inactive native .inl against fake VM ABI; positive recursive generic/PTR/SZARRAY/ARRAY/qualified cases and malformed/over-budget negatives extend all previous ownership/epoch/first-event cases.
- Demo pure source mirrors, exact source-gate, negative tests, machine manifest and cross-fork CI were updated in the same feature branch.

| Source type | Original FormatType grammar | Current bounded native subset |
| --- | --- | --- |
| CLASS/VALUETYPE | type(length:assembly/length:namespace/length:name@arity...) | Authenticated registered AOT TypeDefs only |
| GENERICINST | generic(definition,length:argument,...) | Recursive, max 16 args/instantiation, max 8 levels |
| PTR, SZARRAY | ptr(type), szarray(type) | Recursive wrapper around admitted AOT TypeDef leaves |
| ARRAY | array(rank,length:type,sizes=n,...,bounds=n,...) | Rank nonzero, signed values, max 32 entries/list |
| Qualifiers | qualified(attrs,num_mods,byref,pinned,type) | Exact original order and decimal spelling |
| Primitives, VAR/MVAR | Original primitive/declaring-owner resolution | Rejected; owner and canonical parity not proven |
| Non-ASCII assembly folding | Original Unicode UTF-16 case fold | Rejected; ASCII-only key builder |
| Arbitrary postterminal or unrelated metadata | Original full getters | Rejected; not a terminal/full field source |

The 4096-byte cap is for a complete key, not just one child. Callback ordering does not affect final registration-slot-ordered row output. Nested arguments from registered AOT images without any observed class remain eligible only with independently proven TypeDef handle ownership. Primitive/open/Unicode shapes are *not silently replaced with a surrogate*.

## 3. Verified source/host evidence — NOT official Unity

| CI run | Results and scope |
| --- | --- |
| [Pure composite 42992930075](https://github.com/night-outlook/il2cpp_plus/actions/runs/42992930075) | 4/4 completed success (Mac/Linux C++11/17; Release/Debug strict/sanitized), no observed protected allocation |
| [Exact native .inl mock 42993897217](https://github.com/night-outlook/il2cpp_plus/actions/runs/42993897217) | 4/4 completed success at native 272f3077; 16 host processes × 50 typed cases, at least 640 assertions/process; actual inactive .inl compiled against mocked VM |
| [Cross-fork exact source 42994963528](https://github.com/night-outlook/hybridclr_demo/actions/runs/42994963528) | 2/2 completed success, 18 admission/negative Python tests on each OS, 26 exact native/4 demo Git source blobs |

Earlier RED source-mock jobs revealed missing fake ABI definitions and C++11 local-constant syntax; Primary corrected the source/mock and reran. Exact source CI 42994432053 initially rejected a stale text-bound assertion after the recursive composer replaced the older direct definition call; the assertion was corrected and the full fail-closed source check passed 2/2 at 42994963528. Preserve RED runs as historical evidence, not acceptance.

No official Unity 2022.3.62f2 AssemblyShadow.cpp TU compilation, generated Bee source installation, GameAssembly link, fresh real Player, GC stress, postterminal source capture or new V2 artifact/receipt was executed. The pure source CI validates *syntax and behavior with mock VM types*, not Unity runtime ABI/lifetime.

## 4. Independent review findings and decisions

**B2-COMP-01 — grammar subset and owned bytes.** The limited C++11 source composer, row ownership, exact grammar and failure scrubbing are covered by pure-host and actual .inl mock tests. The original legacy getter remains unchanged. Outcome: **PassedInactiveSourceOnly_NotFullV2**.

**B2-COMP-02 — full canonical TypeKey coverage.** Primitive/default enum, VAR/MVAR with declaring method signatures, Unicode assembly folding, and full real nonempty class byte/semantic parity remain absent. All unsupported cases must fail closed. **Primary-owned open**; do not delegate implementation to Local.

**B2-COMP-03 — metadata/VM epoch.** Original initial-session Reader and original assembly/metadata locks bind present pointer accesses, but two snapshots and registry/R02 counter equality do not freeze cctor/static storage, terminal class state or all VM metadata. Original V1 getter itself observes disjoint synchronization regimes. **Primary-owned open**.

**B2-COMP-04 — full field14/15 and transport.** Existing original V2 schema requires complete finalDiagnostics and finalExecutionDiagnostics, NOT B1 first-error text or limited class rows. Terminal-safe complete native full-field sources, descriptor-relative writer and independently authenticated envelope/receipt remain unimplemented. **Primary-owned open**; the existing host-tested codec/POSIX components cannot be promoted by themselves.

**B2-COMP-05 — official Unity compiler/link.** Native C++ host and fake VM do not establish official Unity Il2CppType ABI, actual translation unit, GameAssembly symbol roster or process teardown semantics. **NotRun**; a future Local Validation prerequisite once Primary source is complete.

**B2-COMP-06 — provenance and safety of handoff.** All new source parts and boundaries are Git-pinned and CI checks forbid changing false product-acceptance flags. **PassedSourceGateOnly**. Original full R03 independent FAIL and High IR-R03-01/02 still open; PureInterpreter disabled.

## 5. Future single-batch Local Validation design — CONDITIONAL

Only after Primary fully implements and independently reviews B2-COMP-02/03/04 and publishes a new explicit executable WEB_TO_LOCAL may Local perform a **single source-pinned one-use batch**. The current WEB_TO_LOCAL is CLOSED / NO EXECUTION; do not replay consumed oneuse-12, invent oneuse-13 roots or run Unity now.

| One-use checkpoint | Combined questions to answer | Required separate raw evidence |
| --- | --- | --- |
| Admission | Clean exact four Git SHA sources, 26+ pinned blobs, official Unity/SDK/OS, original-S provenance, two capacity samples and fresh owner-only absent roots | Branch/commit/clean-tree/blob gate, environment and custody receipts |
| Build and link | One official Unity2022.3.62f2 macOS ARM64 IL2CPP build; real C++11 ABI, verified full Bee TU/source install and generated bridge roster; no host test allocator symbols in GameAssembly | BuildReport, C++ compiler/link logs, object/source hashes, GameAssembly UUID/hash and native symbol table |
| Positive Players | Three fresh independent baseline Empty, initializer error19 and captured generic guard15 scenarios, exact original B1/V1 reason bytes and physical ownership/class state | PID/runId/nonce, complete V1 fields, B1 error, class/TypeKey evidence, fixture and binary hashes |
| Full V2 | Complete original field14+field15 source parity, fully owned bounded encoder, descriptor-relative artifact/envelope transaction, authenticated external identity/receipt | Native diagnostics.v2.bin, envelope.v2.json, artifact hash/size, inode/device, independent external receipt and strict reader |
| Adversarial | Class registry mutation, duplicate/cross-image TypeDef owner, over-budget composite, metadata/teardown race, duplicate finalize, unexpected symlink/path alias, partial artifacts | Fail-closed typed reason, unchanged first error, negative-case receipts, no false success |
| Stability and custody | GC/RSS/first-call overhead, repeated Player startup/shutdown, source/receipt provenance, no accidental global allocators, product regular-only seal | GC/performance traces, linked-symbol attestations, immutable raw/manifest and separately audited final product |

All runtime tests must use one immutable pin set and segregate raw native host outputs, original-S evidence and Player product. No Local architecture refactors or independent schema changes. Primary owns fixing any non-trivial findings returned via LOCAL_VALIDATION.md and RETURN_TO_WEB.md.

**Still required from Primary before executable Local authorization:** complete primitive/open/Unicode authentic source and exact V1 parity; terminal-safe full native fields14/15; integrated authenticated V2 transport and independent receipt; source/host adversarial CI; independent review; new one-use roots and exact four pushed SHA handoff. Preserve all original historical evidence.

Status: readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION.
