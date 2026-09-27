# Current Status — R02 repaired and awaiting Local Validation

Updated after Local return `621216751ade64aa39f28ed44a5acdc15c38c6cc`, Primary repair, source re-freeze, control re-pairing, and passing final Primary CI.

- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain explicit deferred risks requiring R02 measured disposition before H2.
- R02 executable/tool source anchor: `82d64ce415c062729f0082e81c1808eaac9602e4`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@6c950eaa98f995084750fe1ea8f80cfe4c59c61b`.
- Candidate runtime pins: HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, HybridCLR Unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`, IL2CPP Plus `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP Plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Final R02 Primary CI: run `36318653155` — **Passed**.
- Final legacy-H1 CI: run `36318659885` — **Passed**.
- R02 acceptance: `false`.
- May enter R03: `false`.

## Local return and Primary repair

Local A/B/C attempts correctly returned `ReturnRequired`: candidate M07 completed internally but failed strict process-group cleanup because Unity Roslyn survived; control additionally lacked its workspace-local ignored M00 ordinary DLL. No valid candidate/control build map, functional Player series, D1/D2 comparison, or independent R02 stage review was produced.

Primary fixed both non-trivial issues:

1. command-owned Unity Roslyn retirement is supervised with exact compiler binding and PID/group/start identity, while the outer no-survivor criterion remains unchanged;
2. candidate and control independently compile and authenticate the fixed M00 ordinary input before M07, retaining the frozen SHA-256 contract and forbidding cross-workspace copies.

The repaired source was frozen at `82d64ce4…`. The control tree has that commit as explicit ancestry and differs from it only by `ProjectSettings/AssemblyShadowSourcePins.json`, which selects the H1 IL2CPP runtime. Candidate transport commits after the source anchor change only metadata documents and the source-pin file allowed by the existing source-authority policy.

## Primary validation

Final R02 CI at `fd59bad0a470b8f70a409fae8ccead9e4046518f` passed:

- 3,103 source/input files authenticated;
- native matrix 70/70 process cases, 1,540 checks;
- native revision matrix 70/70 process cases, 28,294 checks;
- Python R02 suite 145/145;
- managed host Baseline/P01/P03 102/111/111 assertions;
- strict managed process cleanup;
- GCC/Clang codec-storage attribution.

Final legacy-H1 CI at `727b8c39c5f6329d3c94e9a0cf339b8d214e2134` passed:

- current reusable contracts plus explicit R02 rejection tests: 384/384;
- fixed-H1 positive fixture tests: 6/6;
- remaining R01/M07/R01B workflow regressions: Passed.

Primary CI is host/source evidence only. No new Unity Player runtime acceptance is claimed.

## Required next action

Local Validation must run one new unused `R02LocalBatch-v1` root using the exact final candidate transport HEAD from the handoff prompt and control head `6c950eaa98f995084750fe1ea8f80cfe4c59c61b`.

The batch must cover fresh candidate/control builds and ordinary-input receipts, eight functional sidecars, 44 A/B pairs / 88 fresh formal processes, affected Editor/native/M07/startup/failure/count132/lazy/dense/ordinary/mixed-capacity regressions, D1/D2 measurements, complete sealing, and a genuinely independent R02 stage review if the evidence is eligible.

Preserve prior A/B/C failed roots and their seals. Do not begin R03.
