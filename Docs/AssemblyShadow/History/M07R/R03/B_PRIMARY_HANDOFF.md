# R03 B — Primary Implementation → Local Validation handoff record

Date: 2026-09-30. Status: **handoff prepared; awaiting Local Validation**.

This immutable record closes the Primary preparation cycle for the first focused R03 Local batch. It does not record Local execution, R03 acceptance or H2 approval.

## Repository authority

Feature branch in all repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Bound source revision before final demo transport |
| --- | --- |
| night-outlook/hybridclr_demo | `a898fbf7f65792f1edabef836c6706b2f27d7f1f` (documentation parent; final handoff is its pushed docs-only descendant containing this record) |
| night-outlook/hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` |
| night-outlook/il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Host-CI demo execution anchor: `f5f5712459fdf67e2b748ddeab8e6540bffd3d95`.

The final demo transport commit is the current pushed HEAD containing this record and the live `WEB_TO_LOCAL.md`. Local derives that exact SHA from the remote branch, verifies the final Primary prompt reports the same value, and passes it as `--demo-commit`. The runner then independently verifies local HEAD, branch, clean state and `ls-remote` equality.

## Primary host evidence

Workflow `R03 Primary evolution contracts`:
- run: `36706408233`
- demo SHA actually executed: `f5f5712459fdf67e2b748ddeab8e6540bffd3d95`
- host job: Passed
- verifier/filesystem contracts: 29/29
- graph contracts: 9/9
- admission/method contracts: 35/35
- generated Player fixture DLLs: 15
- actual managed Runtime API compile: Passed
- artifact: `11092263069`
- artifact digest: `sha256:c51888ca64f4cbddee69e603a1540d946de36f9c4e12633867c966551b91d897`

No Unity Editor or IL2CPP Player execution is claimed from this host evidence.

## Connector transport smoke test

A disposable branch `codex/connector-smoke-r03-handoff-20260930-0717` was created from the feature head in each repository, one harmless text commit was written through the GitHub Connector, and the exact branch head/file were read back successfully:

| Repository | Smoke commit |
| --- | --- |
| night-outlook/hybridclr_demo | `53afa819f9814ea6c19b707fc0a90e678590cb62` |
| night-outlook/hybridclr | `2029ae5864ce02ee545ec7d28596f03291998556` |
| night-outlook/hybridclr_unity | `3a5abb722bad571aad0c32c0aa72c862df566eef` |
| night-outlook/il2cpp_plus | `9cc6cdd5ff6f96e4937eb4a37a00997b0656fa5f` |

Connector cleanup/delete-ref capability is not exposed in this environment. The four smoke branches therefore remain explicitly as disposable non-authoritative branches. They must never be used as source or validation authority.

## Local execution binding

Owning workspace:
`/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`

Owning repositories:
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity`
- `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus`

Unused batch root reserved for this handoff:
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930A-a898f`

Unity executable:
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`

Runner:
`Tools/AssemblyShadow/R03/run_local.py`

The runner's complete 36-cell contract and nineteen Player cases are specified in `A_VALIDATION_MATRIX.md` and `Tools/AssemblyShadow/R03/player-cases.json`.

## Return rule

On success, Local returns `EvidenceReadyForPrimaryReview`; on any failure or blocked prerequisite, Local returns `ReturnRequired`. Local writes factual results to `Handoff/LOCAL_VALIDATION.md`, updates `Handoff/RETURN_TO_WEB.md`, creates an immutable R03 evidence checkpoint under `History/M07R/R03/`, commits/pushes the Local-owned evidence/doc changes, and stops.

A successful focused batch still leaves R03 open. Primary must reconcile the evidence and complete the remaining R03 regression/performance/PureInterpreter qualification and independent stage-review work before H2 can be requested.
