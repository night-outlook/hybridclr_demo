# R01B execution and entry boundary

Status: **Active / Unaccepted — production integration implemented, fresh Player acceptance pending**. R01 is accepted at demo metadata commit `b89959fcb5b9a3da1dd0e0ffe7874de412472ae8`, after independent review of `7fe868ada1b4eb0b19ebbaa68f00d2611e88b3bf`. Its executable pins and raw evidence remain unchanged in the separate R01 worktrees.

The four new worktrees are `/Users/ah/GitHub/hybridclr/assembly_shadow_r01b/{hybridclr_demo,hybridclr,hybridclr_unity,il2cpp_plus}` on `codex/assembly-shadow-r01b`. Their entry pins are demo metadata `b89959fcb5b9a3da1dd0e0ffe7874de412472ae8` / executable `cc7b17683c2e68a162914c347bb81d765dbc26c0`, HybridCLR `b22fa3d92223645c32663e4a2157eaadf8ea495e`, package `b649c499385ea68490a0f652a98b732e060aeb89`, and il2cpp `7967b8c7043904fcae130b294defd5ce7aa897c4`.

The normative [R01B plan](../../../../Documents/HybridCLR_AssemblyShadow_Design_and_Plans/reviews/M07_SourceReview_2026-09-07/plans/R01B-metadata-index-expansion.md), revised design and Q06–Q08/B05 validation boundaries govern this work. A prototype is not a Player or milestone acceptance result.

## Revised workload contract — 2026-09-08

The user's latest instruction supersedes the earlier 65,536-image target and the proposed 4 MiB / 2 GiB envelope:

- Assembly count: **8,192** (8k).
- Maximum individual DLL: **33,554,432 bytes (32 MiB)**.
- Average DLL: **65,536 bytes (64 KiB)** at the target count.
- Combined DLL bytes: **536,870,912 bytes (512 MiB)** at the target count.
- Spare capacity: **at least 25% of usable encoded index capacity remains free**, after charging all reservations, including retained failed reservations. Reserved but unmapped pages are consumed capacity.

Binary units are used consistently with 8,192 × 64 KiB = 512 MiB. These are user-selected workload requirements. The production candidate implements these admission limits; fresh Player evidence is still required before claiming support. The user selected **process-lifetime total**: ordinary interpreter images, every Shadow version, and retained failed image reservations share the 8,192-image workload budget. A subsequent patch does not reset this count; a process restart starts a new lifetime. Native AOT assemblies are outside this interpreter-image count and retain separate compatibility validation. The 25% free-space requirement applies to usable encoded index capacity after all charged reservations; it is not permission to exclude ordinary or failed allocations from the count.

The 32 MiB maximum is an outlier within the 512 MiB total, not an allowance for every DLL to reach 32 MiB simultaneously. An exact histogram is not prescribed; validation must include a mixed workload reaching the stated count/total and a maximum-size outlier, with independent dense metadata and sparse-offset cases. Padding alone cannot establish metadata capacity. Actual runtime RAM and synthetic/lazy metadata demand must be measured separately.

The current [entry measurement](entry-metadata-measurement.json) retains the original five R00 DLL hashes and historical 65,536-image extrapolation unchanged. Their mean is 27,648 bytes; at the revised 8,192 count that is 226,492,416 bytes (216 MiB), below the required 512 MiB workload. These samples alone do not establish the selected workload. The host has 16 GiB RAM; DLL-byte arithmetic is not a runtime memory result.

R01B remains required: 8,192 exceeds the accepted profile's capacity. Existing prototype runs at the previous scale remain historical diagnostics; new workload acceptance must use the revised requirements and declared counting domain.

## Ordered implementation and verification

1. Complete the index/domain inventory, including encoded arithmetic, sentinels, actual raw heaps/tables, synthetic/lazy growth, fixed tables, private visibility, generated metadata and all managed/tool limits.
2. Compare packed fields, 32-bit sparse pages/intervals and wider fields in an encoding ADR. Run native counterexamples and capacity/arithmetic prototypes. Select a sound admission/growth contract for the user-selected workload envelope before adopting a production profile.
3. Implement one interpreter codec and explicit native-AOT compatibility adapters; migrate every affected arithmetic/lookup/ownership operation. Keep mappings process-lifetime, ordinary/Shadow allocation central, and private data unpublished.
4. Synchronize profile/capability/budget/ABI/manifest/installed-source contracts and old-Player rejection across all four repositories. Freeze new executable pins, install and build a new baseline.
5. Execute 8,191 / 8,192 / 8,193 cumulative-image boundary cases with explicit supported-profile behavior; mix ordinary loads, successive Shadow versions and retained failed reservations in the same process. Verify that Abort does not reset consumption and that 8,192 charged images retain at least 25% usable index capacity. Execute mixed workload, Abort/failure, private/publication, arrays/generics/reflection, large AOT raw indices, affected M03–M07 native/Player/resource and OFF regressions. Measure encoding cost and memory within explicit limits.
6. Package exact evidence, perform independent stage review, then **STOP at H1** for human full review. R02 remains prohibited.

Root owns ADR selection, integration, production allocation/codec ownership, source pins, Unity/install/builds, evidence and final verification. Supporting agents have read-only native/managed inventories or an explicitly isolated standalone prototype; they do not orchestrate other agents. No R02 or later-stage implementation is authorized here.


## Current v6 source entry

The entry pins above are the historical accepted R01 baseline and remain unchanged. The current v6 executable/metadata delivery uses HybridCLR `67f80ac01c15004ed9d2f0c884d0d92141d1019a`, il2cpp_plus `6be7f38bec2fa4677d24efc1a4a1294240789933`, Unity package `c7ed6d244a2c3a8e948f062d5431c289e1369650`, demo executable `9b04fb9f3578a55f50915b914d0071234441289d`, and metadata head `c5a3ac689f1a2c964f98a084f49e97ae3cee4cf2`. This entry records provenance without rewriting the normative historical plan.
