# R02 acceptance decision — batch I

Date: 2026-09-29

Status: **Accepted as `PassedWithExplicitDeferredRisk`**.

## Explicit owner decision

The user/project owner explicitly chose:

```text
R02-D1=A, R02-D2=A
```

This decision is bound to the completed batch-I evidence and the Primary reconciliation in `I_PRIMARY_REVIEW.md`. It does not modify or backdate any Local execution receipt.

## Bound execution and evidence tuple

- Local return: `7a88cfc867d37360a1dc6a06892b3811ec025adf`
- Candidate demo actually executed: `19b0adcf0a1f376f16eaebf16558d0dcdfdafe6f`
- Common executable/tool source: `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`
- Matched control demo: `21c689732cd8087f8ee8fdce4e52a8f2a655f722`
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- Managed package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`
- Candidate IL2CPP: `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`
- Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`

Protected batch-I evidence:
- result SHA-256: `5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`
- seal-index SHA-256: `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`
- archive SHA-256: `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`
- independent review output SHA-256: `201ab92298c3ae4f758c9d5a0e464a36eddc117ddcfacf108b27f0404dcd277e`

Batch I has 34/34 required cells Passed. The independent R02 stage review returned PASS with zero findings.

## R02-D1 — CPU

Decision: **A / accepted as an explicit development-stage deferred risk**.

Accepted residuals include:
- P01/P03 first allocation approximately +24.70% / +23.90%;
- ON-NoPatch repeat10000 allocation approximately +15.85%;
- repeat10000 reflectionInvoke approximately +4.57% / +7.31% for P01/P03;
- repeat10000 closedGeneric approximately +6.76% / +6.71% for P01/P03.

The measured P01/P03 warm allocation objective is also retained: repeat10000 allocation improved approximately 91%, with the tested warm rows showing cache reuse and zero repeated proof/unready/workspace/layout work.

This decision is not a production SLA, an all-operations speedup claim, or permission to hide these residuals. Their measurement and disposition must remain visible to H2 after R03.

## R02-D2 — memory

Decision: **A / accepted as an explicit development-stage deferred risk**.

The fresh H1-runtime-control-to-R02 marginal-median memory deltas are accepted for R02. The largest positive current-RSS phase/mode median in batch I is approximately +0.430 MiB.

This does **not** establish that the previously accepted H1-versus-R01 +18–19 MiB RSS risk disappeared. The comparison baselines differ. The original H1 D2 decision remains intact, and production-device RAM budgeting remains future validation work.

## Milestone result

```text
R02Verdict = PassedWithExplicitDeferredRisk
R02Accepted = true
mayEnterR03 = true
R03Started = false
H2Passed = false
```

R03 is eligible to begin in a subsequent explicitly initiated Primary Implementation cycle. This decision does not itself start R03, satisfy H2, approve a release, or modify historical evidence.

Normative H2 remains after R03 under `Plan/HUMAN_REVIEW_GATES.md`.
