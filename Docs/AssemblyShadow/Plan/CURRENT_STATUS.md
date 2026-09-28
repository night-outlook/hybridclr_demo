# Current Status — batch-F repairs published; awaiting Local Validation

Latest incorporated Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.

- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A require measured R02 disposition before H2.
- Common executable/tool source: `995dbf1003c306a69586f882ff02599db7a9780e`.
- Candidate source-authority commit: `a01ac8169ccdbaacc3eec8ce81009f38eb100d64` on `codex/assembly-shadow-r01b-h1`.
- Matched control: `codex/r02-h1-runtime-control@95b85617c92f8ce806f4652d88077936c76c3b8a`.
- **Package in both roles:** `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- HybridCLR unchanged: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Candidate IL2CPP unchanged: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP unchanged: `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- R02Accepted: `false`; mayEnterR03: `false`.

## Returned state and Primary disposition

F reached controlled builds and Player execution, then recorded 22 Passed, 8 Failed and 4 Blocked cells plus a failed complete seal. Its 1,984-file preservation inventory is not a complete seal. That result is not relabelled or reused as new-package runtime acceptance.

Primary implemented strict R02 extension parsing while preserving legacy eighteen-field serialization, separate exact extension pre/post-link proof, native-writer/managed-parser interoperability tests, three Editor tests, M07 early-capsule preparation, correct count-family auditor dispatch, bounded linker restoration and pre-build forensic snapshots with exact E archive recovery.

Both comparison roles now use the same updated parser package. The control includes the frozen demo source as ancestry and differs only in source pins; candidate post-freeze changes are metadata-only. Old F builds must not be reused as the new tuple.

## Actual selected Primary validation

At `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`, R02 workflow **36372371088**, legacy workflow **36372371077** and M00 origin workflow **36372371129** all passed.

Python: 203/203 in the current environment and Linux CI. macOS: 72/72 repeated-subset tests. Actual native-writer/package-parser/schema/BCL-round-trip contract: 1,310 checks across twelve native extension fixtures plus one legacy fixture. Native matrices: 70/70 each, 1,540 and 28,294 checks. Managed Baseline/P01/P03: 102/111/111 assertions. Legacy scoped cases: 384/384 current and 6/6 historical positives. All 3,276 exported source/input entries, nineteen changed executable paths and 137 nested bindings authenticated.

No Unity Editor or Player was run in Primary. The three new Editor tests, actual linked builds and runtime paths remain Local verification. Read `History/M07R/R02/PRIMARY_VALIDATION.md` for artifact identities and limitations.

## Required next action

Local executes one fresh **34-cell R02LocalBatch-v1** using the final pushed candidate transport HEAD in Primary's prompt, control `95b85617c92f8ce806f4652d88077936c76c3b8a`, and the new package in both workspaces. Read `Handoff/WEB_TO_LOCAL.md` and `History/M07R/R02/LOCAL_VALIDATION_TASKS.md`.

Keep all A/B/C/D/E/F and H1 evidence, run fresh builds, all functional/negative/count/capacity paths, four pilot plus forty formal pairs, exact restoration, final authority and complete sealing. Return non-trivial issues to Primary; obtain independent R02 stage review only when the evidence is eligible. Do not begin R03.
