# R01B runtime admission — v6 final draft

Status: **Automated v6 evidence recorded; independent full-stage review and H1 remain pending.**

Source pins: HybridCLR `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`, hybridclr_unity `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`.

## Ledger and publication

Use one monotonic process-lifetime ledger for ordinary interpreter images, Shadow versions, and retained failed reservations. The target is 8,192 identities. The pinned runtime represents each identity with a stable reservation record and a codec image record; ownership is carried by the reservation/record pair rather than by a packed 13-bit token field. A rejected reservation batch leaves the ledger unchanged. After a reservation commits, later construction, metadata initialization, finalization, or publication failure retains its identity and charged credits; abort makes it unusable without refund or reuse.

The codec uses sparse unique signed 32-bit values. Nonnegative AOT values remain AOT values, and `-1` remains the sentinel. Private ownership is an authorization question for metadata queries; decoding independently checks encoded page, owner, range, and semantic domain. No private page may become visible through global enumeration before the existing transaction publication boundary.

A 4,096-value page size gives 524,287 usable pages. Admission charges no more than 393,215 pages, preserving 131,072 uncharged pages. The input envelope is 32 MiB maximum per valid DLL and 512 MiB total valid DLL bytes, with a nominal 64 KiB average over the ordinary-valid population. These byte limits do not establish metadata RAM, metadata density, or a performance threshold.

The candidate supports one Shadow transaction per process. Repeated transaction support is R03 and is not done here.

## Required sequence

1. Negotiate the live capability through constant-size read-only options 7 and 8.
2. Bind the selected profile to the source-pinned baseline, package, native metadata, and executable identity. Use the authenticated narrow legacy fallback only for an explicitly verified old runtime.
3. Preflight and reserve the ordered batch against the shared lifetime ledger. Rejection before the codec commit section is atomic and consumes no identity or page credit; after successful reservation, credits are retained even if later construction fails.
4. Construct each image under its exact private owner scope.
5. Compute actual metadata demand, including initialized vectors, sparse pages, synthetic/lazy additions permitted by the contract, and retained credits.
6. Finalize the image atomically before publication. If the footprint or owner/range checks fail before the finalization commit, that image's reservation remains unchanged; a successful finalization may charge additional admitted credits and seals the footprint.
7. Publish only after all transaction members are finalized and the existing transaction-wide publication boundary permits visibility. A later initialization or publication failure retains already committed reservations and credits.

The final report must distinguish reserved credits from mapped pages, preliminary fit from finalized demand, and ordinary, Shadow, and failed ledger counters. It must include immutable input identities and hashes.

## Evidence and limits

The finalizer verified the selected v6 startup matrix (11 modes), M07 aggregate (14 modes), R00 strict gate (four modes), ordinary/mixed capacity boundaries and lazy/dense raw result (61 checks). Their exact paths and SHA-256 values are recorded in [runtime-v6-acceptance.json](runtime-v6-acceptance.json). The same record binds 1,021 Editor passes and 492 fresh Python passes from python-v6-sealed-2.log. Native evidence is the v6 reuse audit over retained v5 executions, with the fixed v4 diagnostic fixture limitations preserved. The [workload shape audit](workload-v6-shape-audit.json) records bounded actual-input shapes; the two inherited count-width limitations remain unfixed in [preliminary-v6-code-review.json](preliminary-v6-code-review.json). Independent full-stage review and H1 remain pending. R02 remains prohibited.

The measured receipts establish only the declared workload. Comprehensive arithmetic inventory, fragmentation behavior, and arbitrary metadata/query-cost guarantees are not claimed by these results. Native source reviews and fixed diagnostic fixtures retain their stated scope. Profile acceptance still requires independent full-stage review and H1.

## V6 evidence boundary

The v6 source inventory is sealed against the native commits `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, `6be7f38bec2fa4677d24efc1a4a1294240789933`, the Unity package commit `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable commit `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`. The selected baseline is `M07-Baseline-R01B-20260909-v6`. `native-v6-validation.json` is a reuse audit over unchanged native-v5 executions and no fresh native receipt is required; the v4-fixed header diagnostic limits remain part of the preserved boundary.

V5 exposed an R00 handoff defect: the BCL `ReceiptCodec.Serialize` raw output contained the operations and snapshots, but `JsonUtility` deserialization into the framework-independent `Receipt` lost nested arrays because the nested DTO types lacked Unity `Serializable` attributes. V6 preserves the Serializable DTO projection correction and the finalizer requires its selected fresh v6 R00 strict gate before rendering this document. This historical failure remains diagnostic evidence, not a v6 result.



## Inherited loader limits

The accepted R01 loader contract remains bounded: `parameterCount` narrows before the `>=256` check, and `nested_type_count` increments and casts to `uint16`. Supported ranges are method parameters 0..255 and nested children per declaring type 0..65,535. R01B does not widen these counters or certify arbitrary over-limit or malformed shapes; inherited loader admission debt and runtime counterexamples remain outside this workload and were not run. The current dense fixture has 4,098 types and does not expand the count-width contract. Pre-narrow/increment rejection tests in Debug and Release remain a follow-up outside R01B.
