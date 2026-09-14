# H1 Assembly Shadow Transfer Package

This directory is the portable handoff for continuing R01B/H1 assembly-shadow remediation in another environment. Read this package before running Unity, building native code, or interpreting any historical evidence.

Snapshot date: 2026-09-13 local time. The coordination records may contain UTC timestamps on 2026-09-14.

Continuation checkpoint commits created by this handoff are candidate demo `06c2ee6`, candidate native `1d2df7c`, unfixed reproduction demo `c8ced4a`, unfixed reproduction native `99cdb1b`, and performance reference `88508b5`. These are preservation checkpoints, not acceptance commits. The source/evidence pins below intentionally remain the pre-checkpoint provenance identities until a new source freeze and rebuild are completed.

## Current gate state

- H1: `InProgress`, technical readiness `Blocked`.
- Independent M08 whole-chain review: `FAIL`.
- `humanGatePassed=false`.
- `readyForHumanH1=false`.
- `mayEnterR02=false`.
- R02 is closed.

The current state is not an H1 acceptance. Do not promote a focused test, a historical audit, `PassedReusedAudited`, or the v11 package to fresh current-candidate acceptance.

## Read order

1. `new-agent-prompt.md` — copy-paste continuation prompt.
2. `h1-transfer-manifest.json` — machine-readable repository, pin, evidence, and transfer inventory.
3. `coordination-snapshot/` — committed snapshots of the live ledger, reviews, successor binding, and task cards.
4. The live handoff at `../H1-handoff.md`.
5. The planning files under `../Planning/`.
6. The external raw evidence roots listed in the manifest, if detailed receipts or archives are needed.

The planning files retain their original plan-time `Pending`/`ImplementationNotStarted` values. The live coordination ledger is authoritative for execution status.

## Worktree map at transfer

| Role | Directory | Branch | HEAD | State |
|---|---|---|---|---|
| Candidate demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `06c2ee6` (checkpoint; source pin was `9c6b812148f5ec640e57ecbedcf9399ce68e6aaa`) | clean for committed scope; historical v7-v11 evidence remains untracked |
| Candidate native | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c` (checkpoint; active source pin was `67f80ac01c15004ed9d2f0c884d0d92141d1019a`) | clean for committed scope |
| Candidate Unity package | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `c7ed6d244a2c3a8e948f062d5431c289e1369650` | clean |
| Candidate IL2CPP Plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` | clean |
| Frozen build native | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_frozen_h1_v5` | detached/pinned checkout | `db685e44afb5aee440efae2eb7bec4205aac090d` | clean; keep separate from active native work |
| Performance reference demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_reference/hybridclr_demo` | `codex/assembly-shadow-h1-performance-reference` | `88508b5` (checkpoint; reference pin `f1c923cbaa814e1b63f3c5b9f8303c90616de726`) | clean for committed scope |
| Unfixed reproduction demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo` | `codex/assembly-shadow-h1-count-repro` | `c8ced4a` (checkpoint; source pin `3efc756f7c95ef6699fe838ddda3fdfffc856b53`) | clean for committed scope |
| Unfixed reproduction native | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr` | `codex/assembly-shadow-h1-count-repro` | `99cdb1b` (checkpoint; active source pin `6356dac1df87f601b2d7eb44c9c2ce13b06aa19b`) | clean for committed scope |

The original checkout `/Users/ah/GitHub/hybridclr/hybridclr_demo` is on `main` at `73d95b4064ee23143e0722f6eae127fe61df6c9d` and contains three unrelated local changes. Do not stage or clean it.

## Completed evidence

- The underlying count-loader evidence is `Passed` for 132 schema-2 cells, but it is not sealed in the v11 package.
- Capacity evidence is recorded for ordinary and mixed 8,192-image workloads and the 8,193 rejection boundary.
- 61 lazy/dense/FieldRVA checks and old-player identity rejection have recorded passes.
- Forty Development StandaloneOSX arm64 performance pairs are `ComparabilityPassed`; this is not an SLA or H1 acceptance.
- Eight unfixed reproduction cells were executed and independently classified as 6 `UnexpectedAccepted` and 2 `AssertAbort`; managed overlay/compiler provenance remains unverified.
- Focused successor packaging tests passed 5/5, but this is integrity validation only.
- The startup fixture attempt failed because the current witness-bearing Bootstrap and the frozen fixture Bootstrap do not share the required exact-site acquisition contract.

## Required continuation

1. Finish the exact H1 witness acquisition/policy contract, including the `FixedAssemblyBytes` binding.
2. Authenticate managed diagnostic source-to-binary and effective Debug/Release compiler provenance for the reproduction builds.
3. Freeze a matching baseline and rebuild Players, fixtures, replay, and provenance receipts.
4. Run fresh current-candidate `R01EarlyLaunches` evidence for all 11 modes and update M06.
5. Seal the schema-2 successor package with mandatory reproduction membership.
6. Obtain an independent whole-chain M08 `PASS`.
7. Stop for explicit human H1 review. Only human approval can permit R02.

Do not rewrite old receipts, relabel historical evidence, weaken the exact-site policy, or use the dirty active native checkout as the clean frozen build source.

## Validation at transfer

- JSON syntax and Git whitespace checks: passed.
- Python bytecode compilation for the changed scripts: passed.
- `test_h1_compiler_provenance.py`: 3/3 passed.
- `test_h1_count_launcher.py`: 27/27 passed.
- `test_h1_count_matrix.py`: passed.
- `test_h1_count_results.py`: passed.
- `test_m07_results.py`: passed.
- `test_m02_results.py`: not passed in this checkout: 65 tests produced 1 failure and 3 errors. The errors include missing historical `BaselineArtifacts/StandaloneOSX/M01-Baseline-v1` and a schema-4 binding site outside the M02 contract. Treat this as an existing continuation blocker, not acceptance evidence.
- `pytest` is unavailable in the environment (`No module named pytest`).

No Unity Player build or fresh 11-mode startup run was performed as part of this transfer commit.

## Evidence transfer policy

The coordination directory is not a Git repository and is approximately 3.4 GiB. The H1 remediation evidence area is approximately 2.0 GiB. The coordination records needed to understand and resume the task are committed under `coordination-snapshot/`. Large generated archives and `_temp` raw evidence remain external artifacts because they are intentionally not placed in normal Git history.

Only transfer the raw evidence roots separately when the next validation needs their full receipts or archives. Preserve names, hashes, failure attempts, and historical status. Do not edit sealed records to replace absolute paths; use a relocation map when the new environment has a different root.
