# R03 B2 — Shared exact root/non-root TypeDef declaration audit

**Date:** 2026-11-13 UTC. **Stage:** Primary Implementation source review, inactive R03 B2 only. **Canonical branch:** `codex/assembly-shadow-r01b-h1` on all four forks.

**Source tuple:** `night-outlook/il2cpp_plus@f89b9e9323df1234bf1bc59ca7f418533c958246`; `night-outlook/hybridclr_demo@0724af796d91c7439946e7ea1e7ee275e3fd25f4` (code/test/source-admission anchor, final docs SHA separately verified); `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.

## Defect and original V1 source boundary

The enabled original GetExecutionDiagnosticsJson V1 uses the token-valid **physical** assembly image set, including interpreter images, with MetadataTypeImages first-emplace owner precedence, and formats class TypeKeys from metadata declaration names. R03 B2's inactive source previously double-checked original V1 image primitives, checked three physical class passes and root first owners, and byte-compared up to 128 distinct **non-root** TypeDef declarations after use. Its root metadata contents were only used when producing the row, not compared against later contents: class root pointers and original physical owner may stay unchanged while root name bytes, namespace, declaring-type index, generic index, or arity visibly change.

This source improvement is observational, not evidence of actual Unity metadata mutation or a coherent VM-wide epoch.

## Design decision

**Reuse** the existing stack-bounded `NonRootOwnerAudit` (historical type name) for **both** admitted root and non-root TypeDef handles; do not add a separate large class/metadata snapshot. It records exact handle/image ownership, two copied declaration byte fields (namespace and simple name, each **up to 64 bytes**), declaring/generic indices, and generic arity. Each pair carries explicit `root` and `nonRoot` role bits. A handle used in both roles retains both flags but occupies **one** record.

The total cap is **128 distinct TypeDef handles PER CAPTURE (root + non-root combined)**. This intentionally narrows the previously provisional B2 subset: captures with more than 128 distinct used handles now fail with SourceOutsideBudget, even though the separate physical membership supports up to 1,024 classes. Names exceeding either 64-byte limit fail without truncation/hashing. This is not a final general-gameplay capacity recommendation; completing V1 class coverage may require different native storage/lifetime/latency architecture.

Existing `static_assert(sizeof(NonRootOwnerAudit)<=24576)` still caps the complete root+non-root audit object to **24,576 bytes**, with no additional large audit object, new heap allocation, physical class traversal or enabled Player entry point. The original enabled 5,222-byte V1 getter, B1, R02 and resolver sources are unchanged.

## Implementation details

1. `resolveOwner` continues to authenticate each used TypeDef through registered physical AOT images (or the restricted plain interpreter original physical source) and then through the ORIGINAL first-emplace owner join. **After** successful owner proof, it notes every handle and expected image, using `handle==klass->typeMetadataHandle` to identify class roots for that row. Duplicate same-handle/same-owner entries merge roles; conflicting owners reject.
2. The existing `buildDefinition` call copies exact declaration data for **every** admitted handle, including roots. A second use with different observed contents rejects; no borrowed source-name pointer is retained.
3. At end of the existing third physically matched class pass and after the second original V1 physical image observation, the same bounded pair array is revisited. Each first owner is revalidated using `MetadataCache::GetAssemblyTypeHandle`, then name bytes, declaring/generic indices and arity are re-read and byte-compared under the original initial metadata Reader and `g_MetadataLock`. Total audited pair lookup budget stays **65,536 indexed metadata reads**, separate from prior source-construction and root third-pass limits.
4. Scoped receipt fields include `originalV1RootTypeDefContentRecorded`, `originalV1RootTypeDefContentMatched`, `originalV1RootTypeDefContentEndPassStable`, and total admitted-pair/lookup counters. Historical non-root receipts now count only records marked `nonRoot`, not all array slots. Failure resets both root and non-root receipts, revokes rows and rejects the frozen record. A positive first-emplace receipt requires both scoped root and non-root content checks.

No claim is made that name bytes, TypeDef contents, metadata indices, classes or GC allocations stay immutable *after* the final sample. The original V1 full MetadataTypeImages table remains uncaptured, and unsupported interpreter nested/constructed/generic/VAR/MVAR cases remain fail-closed.

## Tests and exact CI evidence

[**Native CI 43373757923**](https://github.com/night-outlook/il2cpp_plus/actions/runs/43373757923), native exact SHA `f89b9e9323df1234bf1bc59ca7f418533c958246`: **4/4 PASS**, macOS-15/Ubuntu-24.04 × C++11/C++17, Release/Debug strict and sanitizer (ASan/UBSan) host profiles. Each process reports **133 scenarios and 6,623 assertions**. Seven new regression negatives cover:

- root name bytes changing *behind an unchanged name pointer*;
- root namespace changing;
- root declaring-type index changing;
- root generic-container index changing;
- root generic arity changing;
- 65-byte root name rejecting with the original SourceOutsideBudget classification;
- an **earlier class's root name** changing during a later class's TypeKey construction and then failing the complete end-of-collection audit.

The previous 126 source-mock scenarios remain. The tested source is the actual checked-in **inactive** native `.inl` compiled against a **synthetic VM**, not a real Unity/GameAssembly native translation unit or Player.

[**Demo source CI 43374160198**](https://github.com/night-outlook/hybridclr_demo/actions/runs/43374160198), code anchor `0724af796d91c7439946e7ea1e7ee275e3fd25f4`: **2/2 PASS**, macOS-15/Ubuntu-24.04. It checks 64 independently pinned native Git blobs and eight demo reference blobs, the original V1 getter's exact source, root/non-root shared 128-pair primitive scope, separate receipt revocation, seven added modes, first-error preservation, and explicit false product/VM-epoch/V2 predicates. The final **documentation commit** is checked separately and must not inherit this result without its own CI verdict.

## Scoped source review and remaining blockers

- **ROOT-CONTENT-01 — PASS (source/mock only):** both admitted root and non-root TypeDef declarations now have exact bounded name byte/index/arity comparisons at end-pass. Positive receipts are explicitly scoped by role; negative cases revoke all rows.
- **ROOT-CONTENT-02 — OPEN (capacity regression):** the new shared 128-distinct-**total** cap can reject previously accepted provisional captures with more roots (independent physical membership limit remains 1,024). A larger real-game sample/capacity census, alternate storage design and bounded latency/stack evaluation are required before terminal integration.
- **ROOT-CONTENT-03 — OPEN (metadata contents):** unchanged root/owner/name bytes do not prove nested/generic context contents, TypeDef handle-table stability between samples, metadata allocations, class/GC lifetime, ABA exclusion or one all-VM epoch. The 64-byte name cap is an explicit incomplete subset.
- **ROOT-CONTENT-04 — OPEN (real runtime):** official Unity 2022.3 native full TU/GameAssembly, macOS/Windows/Android Player, actual interpreter metadata parity, worker-thread stack/RSS/GC/profiling and metadata-lock time are **NotRun** at these exact SHAs. Synthetic native tests do not confer Unity acceptance.
- **ROOT-CONTENT-05 — BLOCKED (R03 full stage):** complete original general field14/finalDiagnostics and execution field15/finalExecutionDiagnostics with safe immutable preterminal data, native descriptor-relative one-owner V2 artifact/envelope, externally identity-bound receipt/readback, and authenticated first recovery are outstanding. Historical independent R03 FAIL/High findings remain; B1 oneuse-12 focused real Player 19/19 PASS is consumed, not new B2 evidence.

**Next Primary-owned work:** obtain a source-derived full original execution-class shape/metadata inventory and a defensible class/GC/metadata lifetime/epoch strategy; resolve the 128-handle limit and worker-stack/lock-time tradeoff before any terminal field14/15 and native V2 implementation. Do not begin H2/M08A/X02/SNAP-01 or self-approve Human Review Gate.

**State:** `readyForNativeV2FieldCapture=false`; `nativeV2TransportImplemented=false`; `runtimeAcceptance=false`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `wholeVmEpoch=NotProven`; PureInterpreter disabled; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.
