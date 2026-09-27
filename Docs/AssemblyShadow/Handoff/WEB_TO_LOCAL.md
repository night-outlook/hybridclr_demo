# Primary Implementation -> Local Validation — R02 publication blocked

**This is a prepared successor document, not a published or runnable handoff. Do not start Local Validation from the currently published demo HEAD.**

## Objective

Validate R02 admission caching, retained correctness guards, bounded diagnostics, functional witnesses, controlled CPU/memory measurements, and affected regressions in one `R02LocalBatch-v1` batch.

## Publication state

Current verified remote inputs are:

| Repository | Branch | Remote HEAD |
| --- | --- | --- |
| night-outlook/hybridclr_demo | codex/assembly-shadow-r01b-h1 | 44a115cdeb4b5ba4d75552ec7864d20d5d5ddb25 |
| night-outlook/hybridclr | codex/assembly-shadow-r01b-h1 | 1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad |
| night-outlook/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 0ea633a2c5b936b5af69d944593c55bd2783fca9 |
| night-outlook/il2cpp_plus | codex/assembly-shadow-r01b-h1 | 3981da12f2cd3ee878a04dda6f573d0ad3faeda5 |

The published demo still pins H1 demo source `0388479f7073289e3505b992956a7cbe78c302ce` and IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Those pins are **not** a valid pairing for the R02 executable changes. The matched control branch and R02 source-target metadata have not been published. This continuation contains unpublished fixes to managed-host process ownership, cell-boundary source checks, recovery receipts, codec memory attribution and metadata preparation.

The current GitHub interface provides read and artifact-download operations but no commit, file-update or branch-write operations. Direct Git transport in this environment also fails DNS resolution. Repository `push` metadata does not create a usable write operation. No remote write or final CI rerun is claimed.

## Required Primary publication, before any Local handoff

Follow `Docs/AssemblyShadow/History/M07R/R02/PUBLICATION_PLAN.md`. Primary must publish the executable repair, create the matched H1-runtime control pairing, freeze the two exact source identities, regenerate this document with `Tools/AssemblyShadow/R02/prepare_metadata.py candidate`, and commit/push the resulting metadata. The prompt generator verifies live refs before emitting a complete handoff.

Primary must also verify a new passing `r02-primary.yml` run. The existing run `36286602193` is failed: its managed assertions passed, but owned process-group cleanup did not. It cannot be relabeled as a passing run of these new fixes.

## Local plan, after publication only

Candidate owning workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`.
Matched control owning workspace: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control` (new planned workspace; not verified as existing).
Each contains its own `hybridclr_demo`, `hybridclr`, `hybridclr_unity` and `il2cpp_plus` checkout. Do not alter unrelated existing worktrees.

Read `Docs/AssemblyShadow/README.md`, the final published replacement of this file, `History/M07R/R02/DESIGN.md`, `History/M07R/R02/LOCAL_VALIDATION_TASKS.md` and the final `History/M07R/R02/source-targets.json`.

The implemented runner covers exact source authority; host tests; two controlled ON/OFF graphs; eight functional sidecars; 44 A/B pairs (88 fresh performance processes); Editor tests; native regressions; M07; startup11; failure/publication/recovery; count132; lazy/dense; ordinary/mixed capacity; final authority and complete sealing. Independent valid cells continue; invalid dependencies or dirty source state block consumers.

All non-trivial code changes belong to Primary. Local may resolve tool paths, create clean registered worktrees at the published commits, build/run the supplied batch, collect evidence, and perform documented bounded environmental fixes. Local must not repair source algorithms, alter pins, weaken verifiers, suppress failed attempts, or start R03.

Preserve all H1 historical evidence, the source-27df performance execution, the historical R01 reference, and raw/build/launch/seal bytes produced by R02. Record actual results in `LOCAL_VALIDATION.md`; non-trivial issues return in `RETURN_TO_WEB.md`. Do not rewrite either Local-owned file merely to match this planned state.

## Gate

H1 remains `PassedWithExplicitDeferredRisk`; D1=A and D2=A remain accepted only as H1 development-stage deferrals. R02 must report their measured disposition before H2. R02 acceptance and R03 entry remain false.

**Stop at Primary publication. No valid Local Validation handoff exists for this repair until the required commits and remote verification are complete.**
