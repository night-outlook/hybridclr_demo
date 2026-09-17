# R01B growth accounting — selected implementation and unresolved proof

This analysis supports the selected 8,192-image process-lifetime workload and the native sparse-page implementation in HybridCLR `7bf9479`, paired with il2cpp_plus `2109c2c` and hybridclr_unity `e06c293`. It records native implementation evidence and remaining proof obligations; it does not accept runtime capacity, full-stage Player support, or H1.

## Separate quantities

1. Image identities: ordinary, Shadow and retained failed reservations share the same lifetime count.
2. Encoded index pages: charge reserved quota, including unmapped and aborted reservations. The candidate protects all nonnegative int32 values, has 524,287 usable 4,096-value pages and must charge at most 393,215 pages to retain at least 25% free.
3. Physical memory: DLL copies, vector capacities, hash maps, classes, attributes and reallocations have a separate RAM cost. A page contains 4,096 **index values**, not necessarily 4,096 resident metadata bytes. Do not equate writer allocation capacity with encoded page demand.

## Fixed-resolver bounds and remaining uncertainties

The type cache appends only on a shallow-key miss. Initialization empties its deduplication map once, but later insertions repopulate it. Therefore repeated equivalent post-initialization calls deduplicate. An initial analysis claiming that all lazy retries duplicate types was rejected on inspection of `AddIl2CppTypeCache`; the committed insertion helper preserves this behavior while preparing capacity and encoding before the final append.

For one successful fixed-resolver pass, a conservative Add-call count is `(2 + byref2019) * T + F + M + P + P_flagged + C + G + I + A`, where T/F/M/C/G/I are type, field, method, constant, generic-constraint and direct-interface rows; P comes from decoded method signatures; A counts attribute-conversion type additions. This is not an exact unique-type count or a DLL-size-only bound. Attribute retries resolving distinct physical types need separate lifecycle accounting; the existing deduplication does not prove an input-byte bound across resolver changes.

Interface-offset output includes inherited AOT interfaces. Measure the resolved vector before publication, rather than treating local INTERFACEIMPL rows as its bound. Preserve and validate native per-type count widths. A tiny DLL can reference a large inherited interface set.

Converted constants record tagged logical writer offsets, not writer allocation capacity. Enumerate actual constant start offsets with checked tagging arithmetic; retain contiguous byte storage for `DataAt(offset)`. Repeated source blobs can produce distinct converted offsets. Physical writer capacity and temporary realloc/copy memory must be measured separately.

Image-local parameter, direct-interface and nested-type starts remain raw. External encoded fields need explicit adapters. Generic constraint starts need the full-width interpreter sidecar because the native AOT field is only 16 bits.

## Adoption decision still required

A per-image arbitrary quota is insufficient. A sound admission plan must cover encoded values created privately and all permitted post-publication growth, or explicitly define and validate resource-exhaustion behavior without calling it successful workload support. Eager attribute conversion is not assumed safe: it can resolve classes and allocate managed strings during the early startup boundary.

Candidate tests should combine actual private-initialization measurements with fixed-input lazy constraint/interface/attribute paths, failure/retry behavior, inherited AOT spans and checked global accounting. The generated corpus is an input fixture; loaded images and runtime metadata demand must be measured in fresh native/Player runs. No unverified suspected risk is classified as an existing production bug in this document.

## Independent follow-up: rejected resolver-epoch bound

A proposed `G + I + E*A` bound with E=1 for Shadow / E<=2 for ordinary images is **not accepted**. Independent source review found that unqualified reflection type lookup searches the executing/caller image before the attribute owner's pushed execution-image scope. A failed attribute conversion can therefore append a constructed type from caller A, remain retryable, then append a different physical type from caller B. One Shadow commit does not limit these caller contexts to two. This is a source-level counterexample; a runtime reproduction has not yet been executed.

Successful generic-constraint and interface row fills are charged to the image that owns the row, including an ordinary parent touched while staging another image. Private TLS alone does not multiply these row counts. However, the public generic-constraint reflection path has no demonstrated enclosing metadata lock; the row check, resolution, append and assignment require serialization before asserting a once-per-row bound. Failure between vector append and deduplication-map insertion also needs an explicit invariant.

These capacity issues are distinct from R03's private-resolution semantic isolation. R01B must not silently implement R03 merely to simplify its proof. The committed attribute path defers owner type-index publication until conversion, relocation and aggregate range validation succeed, preserving successful resolution semantics while preventing a failed batch from appending its owner types. This closes the failed-batch append issue under the scoped native tests; it does not bound repeated physical resolution choices across callers or establish a complete workload capacity guarantee.

A syntactic upper bound on attribute value nodes can sum blob lengths **per attribute row occurrence**, including repeated references to the same blob. That bound still requires checked parsing of lengths/counts/recursion and does not by itself bound repeated physical resolution choices.

## Current committed implementation checkpoint

The root remediation preserves the original recursive metadata lock over complete attribute conversion, including constructor-signature resolution through shared type pools. Invocation-local writers and deferred type fixups remain necessary because same-thread metadata callbacks can re-enter conversion even under that lock. The completed `cai` state is rechecked after conversion; a nested winner causes the outer private batch to be discarded.

Before appending owner types, the code validates the complete aggregate raw-index range, relocates and patches fixups, reserves vector capacity, and allocates the final byte buffer. The append/ownership-transfer/completed-state tail contains no intended allocation or metadata-resolution callback. Failed conversions therefore have no path to append their batch-owned types. Pages bound while preparing an ultimately failed result remain charged; this is different from appending owner type entries and must remain included in final capacity accounting.

Native helper checks now exercise actual runtime malloc/calloc failure callbacks, recoverable resize/retry, distinct-buffer fixup relocation, bounded copies and geometric type-vector growth. The scoped native codec, index-runtime, range, type-cache, attribute-batch and parser checks exercise the committed source paths, while the helper tests do not execute the full InterpreterImage/cai publication or actual nested reflection. Source review and affected translation-unit compilation support the current implementation checkpoint; full lazy-path Player evidence remains required before accepting the bound for R01B.

The implementation boundary is therefore explicit: reservations, owner checks, immutable page bindings, finalization, publication sequencing, checked raw arithmetic, generic-constraint sidecar handling and deferred attribute batches exist in the pinned native candidate. The remaining substantive growth proof is an end-to-end bound for synthetic vectors and permitted post-publication lazy paths, including caller-dependent attribute retries, inherited AOT interface spans, real memory consumption and retained-failure behavior at 8,191/8,192/8,193 cumulative identities. Those cases require the pinned Player and runtime matrix; native scoped PASS results do not replace them.
