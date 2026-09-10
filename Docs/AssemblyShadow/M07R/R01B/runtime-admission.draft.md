# R01B runtime admission draft

Status: **Native admission path implemented in the pinned R01B candidate; final Player/workload acceptance remains pending.** HybridCLR `7bf9479` contains the codec and runtime adapter, with the paired il2cpp_plus `2109c2c` and hybridclr_unity `e06c293` capability/profile contracts. Scoped native evidence does not establish full-stage capacity or H1.

## Demand and publication

Reserve process-lifetime image identities as a complete batch before skeleton construction. Ordinary loads and Shadow reservations share the ledger. An initial image credit covers its first encoded page; private initialization may request additional credits before binding pages. Every granted credit, including an unused or aborted one, remains charged against the 393,215-page ceiling. A failed private initialization does not recover identities or credits.

Before publication, determine the complete remaining low raw-index range from actual initialized vectors, table counts and the string heap. The type-cache end must include its current eager high-water mark plus all still-permitted constraint, interface and attribute additions. The committed attribute transaction makes failed range conversions append no owner types; once-only successful range publication bounds attribute additions by validated blob bytes per row occurrence. Native scoped tests cover this batching and its arithmetic, while the full runtime nested-reflection and Player bound remain unverified.

Define the future low range as the half-open interval `[0, L)`. Compute L with checked wide arithmetic from each domain's actual indexing convention, including any encoded one-past terminal index (which requires that terminal value itself to be below L). Page rounding must be checked before narrowing. Empty, zero-based and one-based domains must each declare their endpoint explicitly.

Already bound high pages cover actual sparse entry-point/RVA/tagged-constant offsets created during initialization. Final admission must account for the union of those pages and the future low range, rather than adding overlapping raw-domain page counts. It may charge additional *unmapped* credits to cover the missing low pages. Those credits are consumed capacity. Publication is allowed only after the entire remaining demand is covered. The runtime adapter must prevent published encoding outside the declared low range or already admitted sparse pages; there must be no automatic post-publication grant that hides an underestimated bound.

Finalize must atomically seal the allowed low range and already mapped sparse pages while permanently charging enough credits for their union. A failed finalize must leave all state unchanged. Successful sealing cannot be reopened for private growth: GrantPages and out-of-footprint Encode must reject even before publication. Publication requires a sealed image. Sparse page admission establishes capacity only; each runtime accessor must still validate its semantic table, heap or vector offset.

The checked per-image demand/finalization operation is implemented in the codec and called by ordinary and staged runtime metadata initialization before publication. Private growth that exceeds the shared ceiling fails before publication, and post-seal out-of-footprint mappings are rejected. A page reservation or scoped native PASS is not proof that the selected 8,192-image / 512 MiB workload fits; actual initialization, lazy-path, memory and failure tests remain mandatory.

## Ownership and compatibility

Use monotonic internal owner identities shared by ordinary construction and Shadow transactions; do not use reusable stack addresses as lifetime authorization tokens. A thread-local owner scope restores its predecessor on exit. Private batch images share the transaction owner. Per-image lifecycle publication does not replace the existing transaction-wide active-snapshot boundary.

Preserve AOT nonnegative int32 values and the -1 sentinel explicitly. Unknown negative encodings must fail, not fall back to AOT. Decoding remains allocation-free; type-vector synchronization is a separate runtime concern with performance to measure.

A size-only budget report can establish identity/initial reservation admission, not final metadata demand. Profile 2 must distinguish preliminary admission from completed runtime metadata capacity. Managed manifests, diagnostics, native capability/ABI identifiers, installation proof and source pins need the same new contract before building the replacement baseline. No old profile is silently reinterpreted.

## Open proof obligations

- End-to-end Player validation of checked custom-attribute byte consumption, array/count behavior and once-only batch publication.
- Remaining post-initialization encoders and raw domains, including all module/string lookup paths.
- Player validation of per-image finalization accounting, already mapped/unmapped credit union and failure atomicity.
- Player validation of ordinary construction visibility and complete Shadow transaction visibility during finalization.
- Actual 8,191/8,192/8,193 cumulative cases, retained failures, 25% free capacity, memory and performance.

## Resolved runtime adapter sequencing in the native candidate

The ordinary loader now reserves an image, enters its exact construction scope, initializes `InitBasic` privately, builds runtime metadata, calls `FinalizeImage`, and publishes only after finalization. The private construction lookup path preserves self-resolution while registration is withheld. Construction scopes nest and restore, including ordinary loads triggered from metadata callbacks. Decode authority is derived from the current construction scope or exact staging membership rather than being handed to every caller as the reservation owner's token.

Shadow skeleton construction precedes the complete staging resolver scope. Its construction owner authorizes the initial encoded fields, then the complete transaction resolver authorizes cross-member metadata initialization. Each member is finalized before the existing batch publication boundary; a per-image codec state does not expose a partial closure. Pre-publication failures permanently retain reservations and do not make them globally resolvable.

Placeholder ordinary assemblies remain an integration constraint: the loader commits the placeholder through the existing publication transaction only after the private image has completed metadata initialization and finalization. This sequencing is source-reviewed in the pinned candidate; actual placeholder, mixed ordinary/Shadow and failure ordering still require the Player matrix. The implemented sequence is native evidence, not an R01B acceptance result.
