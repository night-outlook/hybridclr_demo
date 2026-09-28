# Current Status — R02 batch-E repair awaiting Local Validation

Updated after Local return `1d7dc134003206ada8a92b50763ca2da7dc9530d`, Primary code/diagnostic repair, exact source/control pairing and passing final CI.

- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain development-stage deferrals requiring measured R02 disposition before H2.
- Common executable/tool source: `d4cfbe5da29482a3b307fbec3333821615288129`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- CI-tested candidate authority: `69f75b78a0696be8b7da69c1725f07c6e1708c48`. Final transport HEAD is supplied by the verified handoff prompt.
- Control: `codex/r02-h1-runtime-control@5a931fe86795e8cc192d3df262cdee824b105963`.
- Candidate HybridCLR/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP remains `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Final R02 CI 36330847917 (Linux/macOS), legacy CI 36330847766 and M00 origin CI 36330847788: **Passed**.
- R02Accepted=false; mayEnterR03=false.

## Disposition

E correctly returned 9 Passed, 2 Failed and 22 Blocked: process cleanup worked, but new M00 compiler outputs did not match the historical fixed-image hash. The prior helper wrongly equated a new compilation with an immutable input contract.

Primary recovered the exact fixed image from the existing hash-bound H1 archive, committed its compact representation/origin, and implemented independent per-checkout materialization with strict original hash/CLI identity and no overwrite of existing correct bytes. Wrong bytes, source/origin changes and links still fail. The old compiler-and-stage helper is removed; M07's fresh compiler/semantic/fixed-byte validations remain.

The new PE forensic cell diagnoses exact retained E inputs without changing or admitting normalized bytes. Those raw E binaries are unavailable here, so their exact pairwise cause is not established by Primary. All original E evidence keeps its classification.

## Primary evidence

191/191 Python tests Passed both here and Linux CI. macOS passed 60/60 focused tests (subset), both native matrices passed 70/70, managed host assertions passed 102/111/111 with clean groups, scoped legacy tests passed 384/384 plus 6/6 historical positives, and the compact fixed image matches its historical archive/member exactly. All 3,146 inventoried source files and 16 changed source paths/deletions were authenticated. See `History/M07R/R02/PRIMARY_VALIDATION.md` and `E_PRIMARY_VALIDATION.json` for full artifact bindings and scope.

These are host/source results, not Unity Player or performance acceptance.

## Required next action

Follow `Handoff/WEB_TO_LOCAL.md` and `History/M07R/R02/LOCAL_VALIDATION_TASKS.md` for the new **34-cell** batch: fixed-input materializations, fresh candidate/control graphs, independent E forensics, eight functional sidecars, four pilot plus forty formal pairs, generated-native and affected Editor/Player regressions, final authority and complete seals.

Preserve all A/B/C/D/E and H1 inputs/evidence. Return precise classifications and D1/D2 measurements. Independent R02 review is eligible only after complete evidence; H2 and R03 do not open automatically.
