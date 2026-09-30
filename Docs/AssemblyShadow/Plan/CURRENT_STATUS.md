# Current Status — R03 Primary candidate implemented; awaiting Local Validation

## State

- R02 verdict: **`PassedWithExplicitDeferredRisk`**.
- R02Accepted: **true**.
- mayEnterR03: **true**.
- R03Started: **true**.
- R03PrimaryCandidateImplemented: **true**.
- R03LocalValidationRequested: **true**.
- R03LocalValidationCompleted: **false**.
- R03Accepted: **false**.
- H2Passed: **false**.
- PureInterpreter structural expansion: **disabled**.

R03's conservative candidate and validation tooling are documented in:
- `Docs/AssemblyShadow/History/M07R/R03/A_PRIMARY_IMPLEMENTATION.md`
- `Docs/AssemblyShadow/History/M07R/R03/A_VALIDATION_MATRIX.md`
- `Docs/AssemblyShadow/History/M07R/R03/B_PRIMARY_HANDOFF.md`
- `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`

## Exact R03 source authority

All repositories use branch `codex/assembly-shadow-r01b-h1`.

| Repository | Exact implementation/source pin |
| --- | --- |
| `night-outlook/hybridclr` | `041c0cbb42d3e64e54fe605673d99799b5d63893` |
| `night-outlook/hybridclr_unity` | `120bb01be680cec0375002a0823552d66d34b84c` |
| `night-outlook/il2cpp_plus` | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` |

Demo host-CI execution anchor: `f5f5712459fdf67e2b748ddeab8e6540bffd3d95`.

Pre-handoff documentation parent: `a898fbf7f65792f1edabef836c6706b2f27d7f1f`.

The authoritative demo handoff revision is the **current pushed remote HEAD containing this status and `WEB_TO_LOCAL.md`**. Because a Git commit cannot literally contain its own SHA, Local must obtain that exact SHA from `refs/heads/codex/assembly-shadow-r01b-h1`, verify the final Primary prompt reports the same SHA, and pass it unchanged as `--demo-commit`. The runner independently re-verifies local HEAD, branch, clean state and remote HEAD.

## Primary validation already completed

Host CI at demo `f5f5712459fdf67e2b748ddeab8e6540bffd3d95` completed successfully after the Player API compile dependency fix:

- verifier/filesystem contracts: **29/29 passed**;
- production graph contracts using real DLL bytes: **9/9 passed**;
- layout-admission/logical-method host contracts: **35/35 passed**;
- Player fixture generation: **15 exact DLLs**;
- compile against actual managed Runtime API source set: **passed, 0 errors**;
- workflow run: `36706408233`;
- artifact: `11092263069`;
- artifact SHA-256: `c51888ca64f4cbddee69e603a1540d946de36f9c4e12633867c966551b91d897`.

These are host/static/tooling results only. Unity Editor execution, IL2CPP Player execution and integrated native behavior are still Local Validation work.

## R02 evidence retained

The accepted R02 execution remains bound to batch-I and its immutable acceptance records. Preserve all R02 A-I/H1 evidence. In particular:
- batch result SHA-256: `5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`;
- seal-index SHA-256: `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`;
- archive SHA-256: `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`.

R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain deferred through H2.

## Next action

Local Validation runs exactly one unused R03 focused batch from `WEB_TO_LOCAL.md`. It must not redesign the feature, enable PureInterpreter expansion, relax expectations, overwrite prior evidence, or promote the focused batch to R03/H2 acceptance.

A successful focused batch returns `EvidenceReadyForPrimaryReview` with a passed evidence seal and all 36 cells Passed. A failed or blocked batch returns `ReturnRequired`. Either way Local records factual evidence in `LOCAL_VALIDATION.md` and returns control to Primary.

After Primary reconciles the Local evidence, **R03 remains open** for the remaining full-stage regression, startup/capacity/performance work, gated PureInterpreter qualification/experiments, and independent full stage review described by `R03-evolution-semantics.md`. H2 occurs only after those R03 exit conditions are satisfied.
