# R01B encoding ADR — selected candidate and remaining proof

Status: **Draft / native candidate selected**. The sparse signed-int32 candidate is implemented in the pinned native source and has scoped native evidence; no R01B Player capacity result or H1 acceptance is claimed.

The current source set is HybridCLR `7bf9479`, il2cpp_plus `2109c2c`, and hybridclr_unity `e06c293`. The native codec and runtime adapter are present in `InterpreterMetadataIndexCodec.h`, `InterpreterMetadataIndexRuntime.cpp`, and the `InterpreterImage`/ordinary/Shadow call paths. The il2cpp and managed package counterparts carry the profile-2 capability and preliminary-admission contract. This is implementation and source-level evidence; the fresh pinned Player build, full workload, and H1 review remain pending.

Scoped native evidence is recorded by the [codec finalization re-review](codec-finalize-review-2.json), [attribute-batch remediation](attribute-batch-remediation.json), [integration correction review](integration-correction-review.json), and [post-reader parser regression](raw-parser-post-reader-fix.json). These records establish bounded checks for their named source paths; they do not establish full runtime capacity, full-stage Player behavior, or H1.

The current workload is defined in [the execution plan](R01B-execution-plan.md): 8,192 images, maximum DLL 32 MiB, average 64 KiB, total 512 MiB, and at least 25% usable index capacity free. The user selected the shared process-lifetime total: ordinary interpreter images, successive Shadow versions and retained failed reservations count together. AOT assemblies are separate. This supersedes the previous 65,536-image target without rewriting historical measurements or prototype runs.

## Existing invariants and measured inputs

The accepted profile-1 implementation uses signed 32-bit stored indices, a packed image/kind layout and `-1` sentinels. Its image table has 1,024 addressable entries, while actual fresh homogeneous allocation capacities are **338/83/19/3**, not 1,024 arbitrary DLLs. DLL bytes times four is a conservative allocator heuristic, not a proof of every generated metadata index.

The [retained-input measurement](entry-metadata-measurement.json) records actual CLI heap sizes, all table counts, FieldRVA file offsets, entry-point tokens and native metadata regions. R00 observed heap/row/FieldRVA maxima are 22,760 / 22,912 / 34,968 / 21,968 / 23,672. They explicitly exclude converted constants, resolved interface offsets and lazy type-cache growth and cannot serve as complete reservations.

Native IL2CPP `EncodedMethodIndex` is a separate AOT metadata-usage format: three usage bits and a method-spec bit leave a 28-bit decoded payload. Existing interpreter vtable and RGCTX paths bypass that decoder. Preserve the AOT format and domain adapters; do not impose its payload limit on all interpreter indices or send interpreter encodings through it.

## Candidate comparison

| Candidate | Benefit | Required proof / cost |
|---|---|---|
| Reallocated packed image/local bits | Simple arithmetic and decoding | 8,192 interpreter identities plus AOT need at least 14 identity bits, leaving a small fixed per-image local range; sparse token/RVA and mixed large images remain problematic. |
| 32-bit contiguous intervals | Keeps field widths and existing local arithmetic within an interval | Reserving every value up to the largest sparse token or offset wastes space. Sound fixed ranges for lazy/synthetic indices are still required. |
| 32-bit sparse pages | Keeps field widths and avoids unused raw-index gaps; direct page descriptor lookup can be constant-time | Every encoded addition/subtraction/comparison/range must be migrated or guaranteed contiguous. Requires stable synchronized mappings, sound reservation/growth bounds, private ownership and explicit AOT protection. |
| Wider stored representation | More numerical address space | Broad IL2CPP/generated/ABI migration; native AOT file formats and metadata-usage tags need separate adapters. Does not resolve memory or lifecycle budgets. |

The selected native implementation uses sparse 32-bit pages while protecting the **entire nonnegative signed-32-bit raw/AOT domain** `[0, 2^31)`. The all-ones `-1` sentinel is excluded. At a 4-KiB page size, excluding the final page leaves 524,287 complete interpreter pages. This is only addressability: approximately 64 pages per image at the revised 8,192 target before spare capacity. With the user-selected 25% free-space requirement, the aggregate charged-page ceiling is 393,215 (less than 48 pages per target image on average); a real workload and sound growth bounds must fit it. Reservations, including retained failed reservations and unmapped quota, count against this ceiling.

Protecting only `[0, 2^28)` would leave 983,039 four-KiB pages, but requires additional proof/admission for larger AOT and raw indices. A 64-KiB page size with that smaller protected prefix provides only 61,439 pages, sufficient for one page per image at the revised 8,192 count, but not a proof that the required 32 MiB maximum / 64 KiB average / 512 MiB total workload fits. These formulas are not support claims.

## Counterexamples that must be closed

1. **Encoded addition:** `InterpreterImage.cpp` adds to encoded field/interface starts before decoding; `GlobalMetadata.cpp` similarly handles field, method, generic-parameter and constraint offsets. Arbitrary noncontiguous page placement can select a wrong raw page or owner. Use checked owner-preserving arithmetic or prove contiguous spans.
2. **Encoded subtraction:** `InterpreterImage.cpp` computes field/method counts from differences between encoded starts. A migration limited to addition is incomplete; these differences must be computed in the raw domain with owner checks.
3. **Incomplete metadata bound:** heap sizes and table counts omit converted constant writer offsets, synthetic type-cache growth and inherited interface-offset vectors. A declared page quota only prevents overselling; it does not prove supported inputs can finish within it. Post-publication exhaustion is terminal failure, not successful capacity support.
4. **Unassigned pages:** unknown interpreter encodings must fail closed; an empty descriptor cannot turn a negative interpreter value into an AOT raw index.
5. **Publication and enumeration:** page ownership can be reserved before Stage, but global image lookup must not expose private metadata. TLS ownership remains explicit, and GC/enumeration must count logical images rather than duplicate page aliases. Abort/failure cannot recycle IDs or pages.
6. **Contract bounds:** the current pure-BCL capability parser, warmup closure readers, DTOs, manifests and verifiers contain limits below the revised 8,192 target (including 4,096-member readers). Any expansion must remain bounded and bind a new profile/Player identity; increasing a parser limit alone does not expand native capacity.

## Required decision evidence

Before production acceptance: complete the caller/arithmetic inventory; validate the selected process-lifetime workload envelope; establish a sound pre-Stage reservation or bounded-growth proof; run randomized/signed/sentinel and cross-page counterexamples; exercise shared allocation and retained-failure cases; and measure lookup cost and memory. The native codec is already integrated, so the remaining acceptance step is fresh full lifecycle/resource/feature-OFF Player evidence against the three pinned repositories. Prototype descriptor counts cannot be reported as loaded assembly counts. Final R01B acceptance and human H1 remain pending.

## Independent adoption review — 2026-09-08

The bounded independent review returned **FAIL for production adoption of the v1 prototype model**, not a milestone or H1 verdict. Its historical corrections are represented in the current native candidate, with scoped evidence, but the review result does not become a Player or H1 verdict:

- The committed codec uses immutable page bindings, one stable per-image owner record and a Private/Published/Aborted lifecycle. Private resolution is checked through construction or Shadow staging ownership, while the existing transaction publication boundary remains authoritative.
- `BuildCustomAttributesData` now decodes same-owner raw endpoints through checked range arithmetic before batching and publishing type indices. The native attribute-batch review found no remaining bounded-remediation issue, but did not execute full Player concurrency or capacity acceptance.
- The native AOT generic-constraint field remains narrow; interpreter generic constraints use the checked full-width raw-start sidecar. The declaration probe remains a historical verified counterexample for the rejected model, not evidence that the current small-fixture Player fails.

See [semantic index domains](semantic-index-domains.json) for 37 inspected sites, their source hashes, AOT/raw exclusions and the native declaration probe. The inventory remains partial. Native codec, range, generic-constraint and attribute-batch checks are scoped evidence, not a sound synthetic/lazy-growth reservation proof; that proof and the Player/H1 gates remain required before accepting the new production profile.
