# R02 batch I — Primary reconciliation and measured-risk review

Status: **Ready for explicit R02 acceptance and D1/D2 disposition. No human approval is recorded.**

## 1. Authority, review scope and stage boundary

Input Local return: `7a88cfc867d37360a1dc6a06892b3811ec025adf`. The immutable checkpoint is `local-validation-20260929-batch-i-evidence-ready/` in this directory. The independently reviewed pre-review commit is `273f33a324c2262505863fb8a3594f913eb47ebc`.

| Identity | Exact revision |
| --- | --- |
| Candidate demo actually executed | `19b0adcf0a1f376f16eaebf16558d0dcdfdafe6f` |
| Common executable/tool source | `a81bb0d7b886fe941ba4b132296a30dcf4a319cc` |
| Matched control demo | `21c689732cd8087f8ee8fdce4e52a8f2a655f722` |
| HybridCLR, both roles | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Managed package, both roles | `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` |
| Candidate IL2CPP | `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` |
| Control H1 IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` |

The final documentation transport commit is not a new Player execution identity. This reconciliation changes no executable source, source pins, fixture, verifier, runtime, or control branch. `PRIMARY_VALIDATION.md` and `H_PRIMARY_VALIDATION.json` remain the previously selected host/source validation records. `Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and the complete I checkpoint remain unmodified.

Primary read the current Local reports, independent output/receipt, R02 plan, normative review-gate rules and original H1 D1/D2 decision. Primary authenticated the committed checkpoint and independently recomputed its statistical summaries; this is not a second full code review or a rerun of the independent reviewer's live-Mac inspection.

**Gate naming matters:** `Plan/HUMAN_REVIEW_GATES.md` puts the numbered H2 gate after R03. I's local `ReadyForHumanReviewGate` label is a readiness statement, not completion of R03 or H2. This document supplies the requested pre-R03 R02 acceptance/risk decision; it does not add or move a numbered gate. R03 implementation has not started in this cycle, and H2 remains future work.

## 2. Evidence reconciliation

The batch result is `EvidenceReadyForStageReview`: **34 distinct cells, all Passed**, with zero Failed/Blocked. Its result SHA-256 is `5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`.

The independent `code-gate-reviewer` output is **PASS, zero findings**, explicitly without R02 acceptance or R03 authorization. Its exact text hashes to `201ab92298c3ae4f758c9d5a0e464a36eddc117ddcfacf108b27f0404dcd277e` and matches its receipt. The 131 pre-review manifest entries remain byte-identical. The final manifest has 134 entries: it adds the independent output, independent receipt and preserved pre-review manifest, rather than changing the reviewed inputs.

Primary's isolated audit workflow `36659328251` checked out the exact Local return, verified all 134 final manifest entries and exported the checkpoint/planning inputs. Artifact `11073980651` is 751,860 bytes, SHA-256 `a5b50eeefb881b534aff0c2c395490cf362cdad9cae1b1252dc7fe8f50026b76`. Primary rechecked ZIP integrity and all 179 exported file size/SHA-256/Git-blob identities in the current environment. See `I_PRIMARY_AUDIT.json` for precise scope.

Primary also checked aggregate/individual cell equality, 44 pair receipts and schedule identities, non-overlapping intervals, 88 distinct timing IDs plus eight sidecar IDs, ten formal pairs per mode with five AB/five BA orders, all 48 operation-phase summaries, 24 memory phase/metric summaries, eight readiness distributions, and their D1/D2 summary agreement. The 132 count cells and run IDs are distinct. M07's 14-mode strict result and startup's requested 11-mode bounded result plus their R02 schema receipts pass; this does not expand startup coverage to its larger full-mode inventory.

Local and the independent reviewer separately report authentication of **72,826 live locators and 20,111 unique archive members**. The full Mac archive is 736,137,574 bytes, SHA-256 `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`; its 32,975,584-byte index hashes to `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`. Primary verified those committed bindings but did **not** access/re-hash that Mac archive or every full Player raw file in this cycle. The audit export is not a replacement for the full Local seal.

### Previously failing boundaries

| Boundary | Fresh I evidence and disposition |
| --- | --- |
| Warm P01/P03 certificate publication | Both 10,000-allocation sidecars Passed: 10,002 hits; zero misses, proof attempts, unready outcomes, field/interface workspaces or layout checks; 10,000 baseline-state checks remain. The extra two hits are observed diagnostic scope, not 10,002 requested allocations. |
| Host writer/parser and controlled builds | Actual host contract Passed; both roles freshly installed/built at their declared pins; fixed M00 materialization and eight sidecars Passed. |
| Editor contracts | 1,119/1,119 reported Passed; all five exact required cases occur once in the bound Editor receipt. Primary checked the receipt, not a fresh Editor invocation. |
| M07/startup verifier integration | Strict 14-mode M07 and requested 11-mode bounded startup results and source-bound schema receipts Passed. |
| Count, native and failure regressions | 132 distinct count chains, independent/generated-native transaction and failure/recovery cells Passed. |
| Diagnostic provenance and capacity | Distinct diagnostic Player, lazy/dense and ordinary/mixed capacity cells Passed. |
| Complete seal | Passed in Local and independent review. Earlier A-H failures retain their original classifications. |

No new blocking implementation finding emerged from this reconciliation. There is no source defect returned to Local for repair. Warm success closes H's demonstrated repeated-proof failure for the tested paths; it is not a claim covering every production type, device or concurrency pattern.

## 3. Measurement definition

Source: checkpoint `D1_D2_MEASUREMENT.json` and `batch/performance-analysis.json` (SHA-256 `e1452cdea1f7cfdc9f86d2875c4c77935e06d150b55076e3f16f2677cf8dd440`). A is a fresh H1-runtime control; B is R02, with matching new managed sources. Scope is Unity 2022.3.62f2, Development Player plus C++ Release, macOS arm64, Low stripping, OptimizeSpeed. Four pilot pairs are excluded from the forty formal pairs; there are ten formal pairs per mode, not forty independent observations per mode.

CPU percentages below are `100 * (median(paired B/A) - 1)`. Positive means slower. Absolute CPU differences are medians of paired B-minus-A seconds per iteration, converted to microseconds. They are not differences of marginal medians and need not equal a ratio formed from marginal medians. Reference totals below ten ticks suppress ratios; absolute values remain. No latency-based sample exclusions, post-hoc timing subtraction, new retry policy or significance threshold is introduced.

Memory differences below are B's marginal median minus A's marginal median, in MiB. Current RSS, `GC.GetTotalMemory(false)` managed bytes and lifetime peak RSS have distinct meanings; a lower managed/peak value does not cancel higher current RSS. Ten paired processes on one development platform do not establish universal production performance. Reported min/max/sign counts are descriptive, not confidence intervals or a new acceptance test.

## 4. D1 — favorable and unfavorable CPU results

| Metric | ON-P01 | ON-P03 | ON-NoPatch |
| --- | ---: | ---: | ---: |
| First allocation | +24.70% / +18.900 us | +23.90% / +17.700 us | -79.84% / -9.250 us |
| Allocation repeat10000 | -91.67% / -5.590995 us | -91.40% / -5.603635 us | +15.85% / +0.014325 us |
| ReflectionInvoke repeat10000 | +4.57% / +0.080295 us | +7.31% / +0.130900 us | +10.10% / +0.097980 us |
| ClosedGeneric repeat10000 | +6.76% / +0.164380 us | +6.71% / +0.170295 us | +7.08% / +0.107650 us |

All ten P01 and all ten P03 formal pairs have slower first allocation and faster repeat10000 allocation. Warm allocation paired ratios range 0.079884–0.087487 for P01 and 0.080864–0.090715 for P03. ON-NoPatch warm allocation is slower in nine of ten pairs. Warm reflection/generic regressions are also retained rather than dismissed as noise. Counter evidence demonstrates removal of repeated proof work, but the data does not isolate the complete cause of every remaining timing change.

The primary allocation objective is achieved on the measured warm paths. It does not mean every operation improved. Cold readiness diagnostics were part of the tested runtime and their cost has not been subtracted or moved outside the reported measurement.

### Complete operation-phase percentage matrix

| Mode | Operation | first | warmup | repeat10 | repeat10000 |
| --- | --- | ---: | ---: | ---: | ---: |
| R00-OFF-NoPatch | allocation | -47.63% | +0.00% | Suppressed | +2.06% |
| R00-OFF-NoPatch | reflectionInvoke | -3.63% | +3.33% | +18.75% | +2.64% |
| R00-OFF-NoPatch | closedGeneric | +0.60% | +1.04% | +0.00% | +1.38% |
| R00-ON-NoPatch | allocation | -79.84% | +9.56% | +2.94% | +15.85% |
| R00-ON-NoPatch | reflectionInvoke | +4.32% | +13.60% | +10.24% | +10.10% |
| R00-ON-NoPatch | closedGeneric | -7.92% | +8.85% | +9.33% | +7.08% |
| R00-ON-P01 | allocation | +24.70% | -91.38% | -88.44% | -91.67% |
| R00-ON-P01 | reflectionInvoke | -45.25% | +7.23% | +3.14% | +4.57% |
| R00-ON-P01 | closedGeneric | -12.15% | +5.49% | +7.24% | +6.76% |
| R00-ON-P03 | allocation | +23.90% | -91.25% | -88.38% | -91.40% |
| R00-ON-P03 | reflectionInvoke | -34.56% | +2.82% | +2.39% | +7.31% |
| R00-ON-P03 | closedGeneric | -14.07% | +10.56% | +5.51% | +6.71% |

## 5. D2 — memory and baseline limits

All entries are candidate-minus-control marginal-median MiB; negative is lower.

| Mode | RSS before | RSS after | Managed before | Managed after | Lifetime peak before/after |
| --- | ---: | ---: | ---: | ---: | ---: |
| OFF-NoPatch | -0.328125 | -0.210938 | 0.000000 | +0.001953 | -0.187500 |
| ON-NoPatch | -1.906250 | +0.132813 | -0.001953 | -0.003906 | +0.304688 |
| ON-P01 | +0.429688 | +0.335938 | -0.009766 | +0.007813 | -0.062500 |
| ON-P03 | -0.609375 | +0.382813 | -0.015625 | -0.001953 | -0.835938 |

The largest positive RSS difference among these phase/mode medians is +0.429688 MiB. This is not a maximum per-process observation, a leak bound or a production budget. Full distributions remain in the checkpoint.

The original H1 decision accepted +18.2109/+19.1563 MiB before-benchmark P01/P03 RSS versus its historical R01 reference as development-stage risks. **I's small incremental H1-runtime-control-to-R02 deltas do not establish that the original cost disappeared.** The baselines and executable/measurement identities differ. Do not add/subtract memory medians across the two studies or multiply their CPU ratios into an asserted R01-to-current result.

Earlier source/host attribution identified 29,884,384 bytes of profile-2 constructor allocation requests, shared by H1 control and R02, not measured Unity RSS and not a proof of the entire historical D2 delta. That attribution and I's process measurements are distinct evidence. Target-platform RAM budgets and a source-matched historical comparison remain outside this completion claim.

## 6. Single batched decision request

The original H1 `D1=A, D2=A` is preserved and is not being re-asked or rescinded. The following **R02-specific** choices concern the newly measured tradeoffs and acceptance of this milestone.

| Decision | A — Primary recommendation | B — remediation before acceptance |
| --- | --- | --- |
| R02-D1 | Accept the measured CPU tradeoff for the R02 development milestone, explicitly retaining first-allocation, ON-NoPatch and reflection/generic residuals. Carry their measurements and disposition into H2; this is not a production SLA or all-operations speedup claim. | Keep R02 unaccepted and require a bounded Primary CPU investigation/implementation plus controlled Local revalidation before acceptance. |
| R02-D2 | Accept the measured incremental memory cost for the R02 development milestone, preserving the original H1 RSS risk and future production-platform budgeting. Do not declare the historical RAM cost eliminated. | Keep R02 unaccepted and require a bounded Primary memory investigation/implementation plus controlled Local revalidation before acceptance. |

Reply in one batch, for example `R02-D1=A, R02-D2=A`. Both explicit A choices would permit Primary to append an immutable decision bound to this review and tuple, accept R02 as `PassedWithExplicitDeferredRisk`, and make R03 eligible. They do not run R03, approve H2 or grant release acceptance. Any B or missing choice keeps both current booleans false. If B is selected, Primary—not Local—owns every non-trivial change.

Recommendation rationale: fresh functional/negative/regression evidence and independent stage review are complete; the measured warm allocation benefit is substantial and removes H's correctness-of-caching failure. The remaining observed costs are explicit and bounded to the tested development scope, not hidden behind comparability. No claim is made that later work must or will eliminate them automatically.

## 7. Current stop and successor preparation

`I_NEXT_VALIDATION_PLAN.md` and the updated `Handoff/WEB_TO_LOCAL.md` supersede the instruction to start another R02 batch. No new Unity/Player run, native rebuild, full 34-cell retry or R03 implementation is authorized by this review. The current Local prompt is synchronization/evidence custody only. Preserve I and all earlier successful/failed evidence.

The next execution cycle is conditional on the actual user decision and a new source-bound Primary handoff. H2 still follows R03 under the unchanged 5+1 rule. Current state: `ReadyForHumanReviewGate` at the R02 acceptance/risk checkpoint; `R02Accepted=false`; `mayEnterR03=false`.
