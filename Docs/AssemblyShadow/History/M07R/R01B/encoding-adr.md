# R01B encoding ADR — v6 final draft

Status: **Automated v6 evidence recorded; independent full-stage review and H1 remain pending.**

Source pins for the final evidence package are HybridCLR `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`, hybridclr_unity `c7ed6d244a2c3a8e948f062d5431c289e1369650`, and demo executable `9b04fb9f3578a55f50915b914d0071234441289d` with metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`. Full revisions and hashes belong in the immutable build receipt. The implementation references in this ADR are the pinned v6 files `InterpreterMetadataIndexCodec.h`, `InterpreterMetadataIndexRuntime.h/.cpp`, `InterpreterImageAdmission.h`, `InterpreterImage.h/.cpp`, `InterpreterMetadataRange.h`, `Assembly.cpp`, and `StagedAssembly.cpp`.

## Decision

Use a sparse unique signed 32-bit interpreter codec. Preserve the complete nonnegative int32 AOT/raw domain `[0, 2^31)` and keep `-1` as the invalid/sentinel value. Unknown negative interpreter encodings must fail closed; they must not fall through to AOT decoding.

The 4,096-value page size and the image identity budget are separate concepts. The pinned runtime does not pack a 13-bit image identity into the sparse token. Its runtime adapter keeps a stable record for each reservation, indexed by the monotonic image ID; that record carries the codec reservation, owner token, image pointer, Shadow flag, and publication group. The codec image record separately carries image ID, owner, quota, mapped-page state, low-range finalization state, and lifecycle. The 8,192 image bound is therefore a bound on these records and IDs. A direct unsigned representation of IDs 1 through 8,192 would require 14 bits; the zero-based range 0 through 8,191 fits in 13 bits.

The encoded token is a negative signed 32-bit value formed from a sparse page slot and an in-page offset. Nonnegative values stay in the AOT domain. The all-ones `-1` value is rejected as a sentinel. Decoding checks the token range, bound descriptor, lifecycle, and private caller ownership; it is not an image-ID packing scheme.

## Candidate comparison

| Candidate | Benefit | Required proof or cost |
|---|---|---|
| Reallocated packed image/local bits | Familiar arithmetic and compact decoding. | The image identity and local-index widths compete for 32 bits; sparse token/RVA offsets and the 8,192 lifetime identities do not fit a single fixed local layout without new bounds. It also preserves the old failure mode where encoded addition/subtraction can cross owners. |
| 32-bit contiguous intervals | Keeps field widths and local arithmetic simple within an interval. | Reserving every value through the largest sparse token or offset wastes raw space. Lazy and synthetic growth still need sound fixed ranges, and interval ownership must be checked for every arithmetic operation. |
| 32-bit sparse pages **(selected)** | Preserves AOT values, avoids unused raw gaps, and gives a bounded page-descriptor lookup for sparse interpreter values. | Every encoded addition, subtraction, comparison, and range operation must decode to raw coordinates first. It requires stable owner records, immutable bindings, bounded reservation/growth, and explicit AOT/sentinel protection. |
| Wider stored representation | More numerical address space and simpler large-range arithmetic. | Broad IL2CPP, generated-code, ABI, and metadata-file migration. Native AOT formats still need adapters, while wider values do not solve lifecycle, memory, or publication limits. |

The selected design is a codec and runtime adapter boundary. It does not replace ordinary-construction ownership checks, Shadow staging ownership, or the existing transaction publication protocol.

## Capacity model and worst-case ranges

Each codec page covers 4,096 raw index values; this is an addressability unit, not a 4 KiB memory-allocation claim. The protected raw domain has 2^31 values and therefore 524,288 theoretical pages. The codec reserves the final page for the signed-token boundary, leaving 524,287 usable pages. The charged-page ceiling is 393,215, leaving 131,072 pages uncharged for the required headroom. At 8,192 lifetime image identities this is less than 48 charged pages per identity on average; the addressability budget is approximately 64 pages per identity before the headroom charge. These averages are planning arithmetic, not per-image guarantees.

The per-image worst case is defined by its actual finalized low range plus already mapped sparse pages outside that range. Finalization computes `ceil(lowEnd / 4096)` and unions it with mapped outside-low pages. It can charge additional page credits only before sealing; an attempted demand above the global charged ceiling or usable-page bound fails without changing the reservation. A low range approaching the full raw domain would require more pages than the usable/charged limits and is rejected. No fixed 64-page-per-image promise is made.

The selected workload is 8,192 process-lifetime identities. Ordinary interpreter images, Shadow versions, and retained failed reservations share one monotonic ledger. A rejected batch does not consume an identity or page credit. Once a reservation commits, later construction, metadata initialization, finalization, publication, or abort retains its identity and already charged credits; identities and credits are not reused. Native AOT images remain outside this interpreter-image count.

The input envelope is 32 MiB maximum individual valid DLL, 512 MiB total valid DLL bytes, and a nominal 64 KiB ordinary-valid-image average. These are input constraints, not metadata-RAM, index-density, or performance measurements. A mixed case labeled 8,184 + 5 + 3 must identify the three members' disposition; if three are rejected or excluded, the valid count is 8,189. Its mean is computed over valid members and must not be presented as a 64 KiB mean unless measured bytes support that claim.

## Fragmentation and lookup cost

Page slots and image records are preallocated. A successful reservation appends page credits monotonically; abandoned or aborted credits remain charged and are not compacted or reused. Sparse raw pages can therefore be far apart without consuming the intervening raw pages, but every bound page consumes one credit. The fixed reverse-binding table has its own bounded occupancy and can return `BindingMapFull`; this is a distinct capacity failure and must be reported as such.

Decode is allocation-free, lock-free, and limited to atomic descriptor loads, token arithmetic, and lifecycle/owner checks. Token-to-image filtering is a separate bounded metadata lookup used to select the correct construction or staging scope. Encode and page binding take the codec writer mutex and use bounded hash probing; lazy `TryAddOffset` decodes and validates raw arithmetic before re-entering the writer path. No RAM, RSS, lookup-latency, or perf-stat threshold is claimed without a fresh measurement method and receipt.

## Compatibility and arithmetic rules

The native AOT metadata-usage encoding remains on its existing path. Interpreter sparse-page values must not be routed through the AOT decoder. Raw arithmetic decodes endpoints first, checks the expected owner and range, then performs checked addition, subtraction, count, or offset calculations. Cross-image subtraction and foreign-owner ranges fail closed. The `InterpreterMetadataRange` helpers preserve this boundary for table spans, synthetic offsets, generic constraints, and custom-attribute layouts.

Private ownership authorization is distinct from decoding. A query may use the active construction or staging owner to resolve private metadata, while decode independently validates encoded page, owner, range, and lifecycle. Published images can be decoded by unscoped readers subject to normal public visibility. Global enumeration and ordinary lookup must not gain private access.

The runtime capability handshake uses constant-size live read-only options 7 and 8. The legacy fallback is narrow and authenticated to an old capability shape; it cannot silently admit profile 2. A source or manifest declaration alone is insufficient. R01B retains one Shadow transaction per process. Repeated per-process Shadow transactions are an R03 concern and are not implemented or accepted here.

## Failure and publication strategy

Reservation preflight validates count, owner, nonzero credits, image limit, charged-page limit, and available page slots before the non-throwing commit section. A rejected batch leaves counters, records, and output reservations unchanged. Finalization validates owner, lifecycle, low-range bounds, mapped-page union, and additional-credit availability before changing quota, page charge, or seal state. A finalization failure leaves that image's reservation unchanged. After successful reservation, later construction or metadata initialization failure retains the reservation; abort makes the image unusable without refund. Publication validates every member is finalized before transitioning the batch, so partial visibility is not a capacity success.

After sealing, lazy encoding is restricted to the admitted low range and available quota. Out-of-footprint, unknown, unbound, sentinel, AOT-domain, quota, owner, and lifecycle errors fail explicitly. The existing transaction-wide publication boundary remains authoritative for Shadow visibility.

## Evidence and limits

The finalizer verified the selected v6 startup matrix (11 modes), M07 aggregate (14 modes), R00 strict gate (four modes), ordinary/mixed capacity boundaries and lazy/dense raw result (61 checks). Their exact paths and SHA-256 values are recorded in [runtime-v6-acceptance.json](runtime-v6-acceptance.json). The same record binds 1,021 Editor passes and 492 fresh Python passes from python-v6-sealed-2.log. Native evidence is the v6 reuse audit over retained v5 executions, with the fixed v4 diagnostic fixture limitations preserved. The [workload shape audit](workload-v6-shape-audit.json) records bounded actual-input shapes; the two inherited count-width limitations remain unfixed in [preliminary-v6-code-review.json](preliminary-v6-code-review.json). Independent full-stage review and H1 remain pending. R02 remains prohibited.

The measured receipts establish only the declared workload. Comprehensive arithmetic inventory, fragmentation behavior, and arbitrary metadata/query-cost guarantees are not claimed by these results. Native source reviews and fixed diagnostic fixtures retain their stated scope. Profile acceptance still requires independent full-stage review and H1.

## V6 evidence boundary

The v6 source inventory is sealed against the native commits `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, `6be7f38bec2fa4677d24efc1a4a1294240789933`, the Unity package commit `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable commit `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`. The selected baseline is `M07-Baseline-R01B-20260909-v6`. `native-v6-validation.json` is a reuse audit over unchanged native-v5 executions and no fresh native receipt is required; the v4-fixed header diagnostic limits remain part of the preserved boundary.

V5 exposed an R00 handoff defect: the BCL `ReceiptCodec.Serialize` raw output contained the operations and snapshots, but `JsonUtility` deserialization into the framework-independent `Receipt` lost nested arrays because the nested DTO types lacked Unity `Serializable` attributes. V6 preserves the Serializable DTO projection correction and the finalizer requires its selected fresh v6 R00 strict gate before rendering this document. This historical failure remains diagnostic evidence, not a v6 result.



## Inherited loader limits

The accepted R01 loader contract remains bounded: `parameterCount` narrows before the `>=256` check, and `nested_type_count` increments and casts to `uint16`. Supported ranges are method parameters 0..255 and nested children per declaring type 0..65,535. R01B does not widen these counters or certify arbitrary over-limit or malformed shapes; inherited loader admission debt and runtime counterexamples remain outside this workload and were not run. The current dense fixture has 4,098 types and does not expand the count-width contract. Pre-narrow/increment rejection tests in Debug and Release remain a follow-up outside R01B.
