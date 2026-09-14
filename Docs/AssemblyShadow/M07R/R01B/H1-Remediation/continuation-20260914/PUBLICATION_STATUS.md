# H1 continuation publication status

Published 2026-09-14.

## Remote branches

- Candidate demo: `codex/assembly-shadow-r01b-h1`
  - implementation commit: `7fd71816a0f0c7716bfb1ea92c9ef1cf082daf86`
  - includes witness/provenance/successor tooling and the committed local-validation handoff.
- Unfixed reproduction demo: `codex/assembly-shadow-h1-count-repro`
  - provenance tooling commit: `762164cc56c06216d87ded0024ebee9044253e41`
  - repro-specific preservation fix: `c8d2faffe289efff6f347ad7a571a6ce16c3a6d4`
  - the pre-existing broad `H1ManagedSourceProvenance` implementation is preserved; new build-scoped source-to-binary work is isolated in `H1ManagedSourceBuildBinding`.
- Candidate/reproduction `hybridclr`, candidate `hybridclr_unity`, and candidate `il2cpp_plus`: no new source modification was required by this continuation pass, so no commit was added here.

All branch updates were fast-forward only; no force push, reset, merge, or history rewrite was used.

## Validation boundary

Portable Python/helper validation was completed before publication. Unity Editor compilation, fresh IL2CPP Player builds, compiler/source provenance receipts, fresh startup11, affected count/reproduction matrices, successor sealing, and independent M08 review still require the local macOS Unity environment as listed in `LOCAL_VALIDATION_TASKS.md`.

This publication does not change the gate state: H1 remains `InProgress` / technically `Blocked`, the latest independent M08 verdict remains `FAIL`, `humanGatePassed=false`, and `mayEnterR02=false`.
