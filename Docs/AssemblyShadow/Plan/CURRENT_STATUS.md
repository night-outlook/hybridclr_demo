# Current Status — R02 awaiting Local Validation

Updated after successful Primary publication and CI.

- H1: `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain explicit deferred risks for R02 disposition.
- R02 executable demo source anchor: `06ba01e010c7eac3543dd6f23e083c2716941190`.
- Candidate source-authority commit: `149a7f33d7bf4c431c2ed7ef3e5f393b47b71817`.
- Matched H1-runtime control demo: branch `codex/r02-h1-runtime-control`, commit `e6fdd32a6fd661a88ef108f7b055e4f7840e9e43`.
- Candidate runtime pins: HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, HybridCLR Unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`, IL2CPP Plus `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP Plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Primary CI: workflow run `36289846827` **Passed** at candidate commit `149a7f33d7bf4c431c2ed7ef3e5f393b47b71817`.
- Primary CI artifact: `10921843892`, 10,428,779 bytes, SHA-256 `23c40013304d56ee545941aee0a174f19f89ae4fe29020c5fc64c4b8720e5f2e`.
- R02 acceptance: `false`.
- May enter R03: `false`.

## Primary completion

The continuation repairs are published: separate .NET build/exec ownership, strict process-group cleanup, per-cell source reauthentication, independent build/recovery receipts, bounded restoration, owned-process survivor diagnostics, codec storage attribution, exact candidate/control source authority, and the batched Local runner.

Fresh Primary CI authenticated 3,082 source/input files and passed:
- exact source verification;
- native matrix: 70/70 cases;
- native revision matrix: 70/70 cases;
- Python: 115/115 tests;
- codec storage attribution on GCC and Clang, both 29,884,384 requested heap bytes plus 120-byte codec object on the CI host ABI;
- managed Baseline/P01/P03: 102/111/111 assertions with strict clean process groups.

These are host/source checks only. `unityPlayerRun=false` and `runtimeAcceptance=false` remain in the Primary receipts.

## Required next action

Local Validation must execute `R02LocalBatch-v1` exactly from `Handoff/WEB_TO_LOCAL.md` and `History/M07R/R02/LOCAL_VALIDATION_TASKS.md`: fresh candidate/control builds, functional witnesses, 44 A/B pairs / 88 fresh timing processes, affected regression suites, D1/D2 measurements, complete sealing, and independent R02 stage review if eligible.

Local must preserve Passed/Failed/Blocked/NotRun/Unavailable distinctions and return non-trivial issues to Primary. No R03 work is authorized.
