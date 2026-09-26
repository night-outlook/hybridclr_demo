# H1 Human Review Decision

Date: 2026-09-25.

Gate: H1 — R01 / R01B capacity and failure-model Human Review Gate.

## Decision authority

The user explicitly responded:

```text
D1=A，D2=A
```

This decision closes the two user-owned risk questions in:

`Docs/AssemblyShadow/History/M07R/H1/human-review-20260925/HUMAN_REVIEW_GATE.md`

The reviewed report was first published at commit:

`9c76243ca8667934855ec52a0431b9e50f5405b4`

The live coordination state immediately before recording this decision was:

`b72b48cf1953aa49df820dc4b63da9c458086b2f`

## Accepted deferred risks

### D1 — warm-operation cost

Decision: **A / Accepted as explicit H1 development-stage deferred risk.**

The user accepts the measured P01/P03 warm-operation regressions recorded by the H1 review:

- allocation: +13.34% / +15.01%;
- reflectionInvoke: +26.57% / +27.59%;
- closedGeneric: +20.42% / +22.09%.

This is not a production performance SLA approval. R02 must investigate, optimize where justified, and perform controlled remeasurement. The disposition and remaining cost must be presented before H2 review.

### D2 — RSS

Decision: **A / Accepted as explicit H1 development-stage deferred risk.**

The user accepts the measured P01/P03 before-benchmark RSS marginal-median increases recorded by the H1 review:

- +18.2109 MiB;
- +19.1563 MiB.

This is not a production RAM-budget approval. R02 must attribute and remeasure the memory cost. Production-device RAM budgets remain subject to later target-platform validation.

## Gate result

The H1 result is therefore:

```text
verdict = PassedWithExplicitDeferredRisk
M08Passed = true
humanGatePassed = true
mayEnterR02 = true
R02Started = false
```

The result preserves all evidence classifications and limitations from the H1 report and Local Validation. It does not relabel historical evidence, rerun Player validation, establish a release verdict, or waive later Human Review Gates.

## Deferred-risk closure obligations

R02 must preserve these obligations:

1. establish a controlled comparison between the current candidate baseline and the R02 candidate;
2. retain the historical R01 performance reference as a separate identity;
3. distinguish definition scans, layout-proof construction/cache hits, temporary native allocation, correctness guards, and observation contention;
4. preserve baseline-use, poison, and execution-context correctness checks;
5. record native/managed memory semantics, RSS, and lifetime peak separately;
6. rerun affected count/capacity/publication/failure/early-use/M07 paths or explicitly authenticate reuse when unaffected;
7. present performance and memory disposition, negative tests, and remaining risk before H2 review.

The user's H1 acceptance is a bounded development-stage risk decision, not a permanent waiver.

## Repository tuple bound by the review

The reviewed source/runtime tuple remains:

- night-outlook/hybridclr_demo source anchor: `0388479f7073289e3505b992956a7cbe78c302ce`;
- night-outlook/hybridclr: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
- night-outlook/hybridclr_unity: `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
- night-outlook/il2cpp_plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Documentation-only commits after the source anchor do not create new runtime or Player evidence identities.

## Stop point

H1 is closed as `PassedWithExplicitDeferredRisk`.

R02 is now eligible to begin in a subsequent explicitly initiated Primary Implementation cycle. No R02 source implementation is part of this decision record.
