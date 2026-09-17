# R01B profile 2 contract — v6 final draft

Status: **Automated v6 evidence recorded; independent full-stage review and H1 remain pending.**

Source pins: HybridCLR `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`, hybridclr_unity `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`.

## Fixed contract

Profile 2 identifies a sparse signed 32-bit codec with 4,096 values per page. It preserves nonnegative AOT/raw indices and the `-1` sentinel. Image identity is represented by the pinned runtime's stable reservation records and monotonic image IDs, not by a 13-bit field in the sparse token: the runtime record binds the codec reservation to its owner, image pointer, Shadow classification, and publication group, while the codec record carries quota, page bindings, low-range seal, and lifecycle. The 8,192 identity bound applies to those records and IDs; direct unsigned encoding of IDs 1 through 8,192 would require 14 bits, while 0 through 8,191 fits in 13 bits.

The shared process-lifetime ledger covers 8,192 identities across ordinary interpreter loads, every Shadow version, and retained failed reservations. A rejected batch is preflighted atomically and consumes no identity or page credit. Once the codec reservation succeeds, its identity and initial page credits are retained for process lifetime: later skeleton, metadata initialization, finalization, or publication failure transitions the image to an unusable/aborted state without returning credits or reusing the identity.

The input envelope is:

- 32 MiB maximum individual valid DLL.
- 512 MiB total valid DLL bytes.
- Nominal 64 KiB ordinary-valid-image average.
- 524,287 usable pages.
- 393,215 charged-page ceiling.
- 131,072 pages of required uncharged margin.

The 512 MiB value is input bytes. It is not a metadata-memory or encoded-index-capacity claim. The ordinary 64 KiB figure applies to the declared ordinary-valid population and must not be generalized to every valid member.

## Wire and admission semantics

A profile 2 capacity report must identify its profile, page constants, lifetime image ledger, reserved and mapped pages, remaining image count, ordered input count, accepted count, first failure, failure reason, preliminary fit, aggregate input bytes, and whether runtime finalization remains required. Legacy cursor arrays are represented deliberately as empty arrays when the Unity DTO includes them; a parser must reject unknown, mixed, or profile-1 fields in a profile-2 report.

Size-only admission is preliminary. Private native initialization computes actual metadata demand and finalizes each image before publication. A successful transaction cannot publish an image whose private metadata is unfinalized. A rejected whole-batch reservation leaves the committed ledger unchanged because all input, image-limit, and page-limit checks occur before the non-throwing commit section. A finalization error likewise leaves that image's reservation unchanged when additional demand cannot be admitted. If reservation has already succeeded, a later construction or initialization failure retains the reservation and its credits; abort marks the image unusable and does not refund them. A post-stage mismatch does not consume another reservation.

The runtime capability version is obtained from live constant-size options 7 and 8. Profile 2 is admitted only after that live result and its source-bound baseline agree. The old-runtime fallback is narrow and explicit, and cannot turn an absent or contradictory capability into profile 2.

## Ownership and compatibility

Private ownership queries and index decoding are separate operations. Construction or staging scope authorizes private queries; decode validates page ownership, range, and semantic domain. Nonnegative AOT values and `-1` retain their original meaning. Unknown negative values fail closed.

R01B supports one Shadow transaction per process. Multiple successful Shadow transactions in one process belong to R03 and remain out of scope.

## Evidence and limits

The finalizer verified the selected v6 startup matrix (11 modes), M07 aggregate (14 modes), R00 strict gate (four modes), ordinary/mixed capacity boundaries and lazy/dense raw result (61 checks). Their exact paths and SHA-256 values are recorded in [runtime-v6-acceptance.json](runtime-v6-acceptance.json). The same record binds 1,021 Editor passes and 492 fresh Python passes from python-v6-sealed-2.log. Native evidence is the v6 reuse audit over retained v5 executions, with the fixed v4 diagnostic fixture limitations preserved. The [workload shape audit](workload-v6-shape-audit.json) records bounded actual-input shapes; the two inherited count-width limitations remain unfixed in [preliminary-v6-code-review.json](preliminary-v6-code-review.json). Independent full-stage review and H1 remain pending. R02 remains prohibited.

The measured receipts establish only the declared workload. Comprehensive arithmetic inventory, fragmentation behavior, and arbitrary metadata/query-cost guarantees are not claimed by these results. Native source reviews and fixed diagnostic fixtures retain their stated scope. Profile acceptance still requires independent full-stage review and H1.

## V6 evidence boundary

The v6 source inventory is sealed against the native commits `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, `6be7f38bec2fa4677d24efc1a4a1294240789933`, the Unity package commit `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable commit `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`. The selected baseline is `M07-Baseline-R01B-20260909-v6`. `native-v6-validation.json` is a reuse audit over unchanged native-v5 executions and no fresh native receipt is required; the v4-fixed header diagnostic limits remain part of the preserved boundary.

V5 exposed an R00 handoff defect: the BCL `ReceiptCodec.Serialize` raw output contained the operations and snapshots, but `JsonUtility` deserialization into the framework-independent `Receipt` lost nested arrays because the nested DTO types lacked Unity `Serializable` attributes. V6 preserves the Serializable DTO projection correction and the finalizer requires its selected fresh v6 R00 strict gate before rendering this document. This historical failure remains diagnostic evidence, not a v6 result.



## Inherited loader limits

The accepted R01 loader contract remains bounded: `parameterCount` narrows before the `>=256` check, and `nested_type_count` increments and casts to `uint16`. Supported ranges are method parameters 0..255 and nested children per declaring type 0..65,535. R01B does not widen these counters or certify arbitrary over-limit or malformed shapes; inherited loader admission debt and runtime counterexamples remain outside this workload and were not run. The current dense fixture has 4,098 types and does not expand the count-width contract. Pre-narrow/increment rejection tests in Debug and Release remain a follow-up outside R01B.
