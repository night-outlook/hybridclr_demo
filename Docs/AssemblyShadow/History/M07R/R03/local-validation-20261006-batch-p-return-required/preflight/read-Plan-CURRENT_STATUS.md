# Current Status — R03 LO repair candidate ready for Local Validation

## Authoritative Local result

Latest completed Local Validation is batch O, published at demo `7025f1026fd61f101a81fbafafb999095aa8604e`.

- Result: **ReturnRequired**.
- 90 cells: **58 Passed / 30 Failed / 2 Blocked**.
- Six fresh builds Passed.
- 18-method preflight and full 754/755 Editor rosters Passed with zero skips/inconclusive.
- All 59 Players executed: 30 verifications Passed / 29 Failed.
- Seal and final custody Passed.
- R03-LO-001–004 returned to Primary Implementation.

Preserve O, N and all earlier evidence/results unchanged. Adapter replays and CI do not reclassify historical Local outcomes.

## Published source authority

All branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Executable/source pin for next Local cycle | Local Validation path |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `9c4b76a540e74c045cabaf9e700051512a75cead` executable source; `8db761455dfd73ef01eac7d48eb39c69ca253cf8` CI-only timeout transport; final Docs handoff transport supplied in Primary prompt | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| `night-outlook/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

The final Primary prompt supplies the latest pushed demo transport SHA. Local must verify that `9c4b76a…` is its ancestor and that every later demo change is limited to `Docs/AssemblyShadow/**` plus the exact CI-only timeout change in `.github/workflows/r03-completion-api.yml` (`timeout-minutes: 60` → `120`).

## Primary repair state

- **R03-LO-001:** source/compiler policy and linked-Player analysis policy are separated. `9c4b76a…` additionally validates the real live Unity source inventory before restored-baseline compilation and requires all three original filtered-reference diagnostics from the wrong-domain linked policy.
- **R03-LO-002:** authenticated native-codec owner/project context is forwarded through the shared diagnostic path; no ambient-CWD fallback is accepted.
- **R03-LO-003:** linked-DLL lookup is canonical-name aware while physical DLL identity, order, hash and MVID checks remain distinct.
- **R03-LO-004:** measurement consumers receive the complete image record, including methods and PDB availability, rather than a methods list with the wrong schema.

No package/native/IL2CPP source changes were required in this continuation.

## Pre-handoff evidence

- Pre-publication exact-patch selected Python suite: 102 Passed, zero failures/errors/skips.
- Python syntax parse: 43 Completion files Passed.
- `7b148aa…`: R03 host Linux/macOS and pinned API workflows Passed.
- `9c4b76a…`: R03 host and R02/native checks Passed; pinned-API attempt 1 Passed steps 6–12 and timed out during unchanged N reference replay. The timeout was operational, not a failed assertion.
- `8db76145…`: increases only the pinned-API job budget from 60 to 120 minutes; its exact-source rerun status is recorded in `History/M07R/R03/LO_Continuation_2026-10-06/PRIMARY_REVIEW.md`.
- Connector write/readback smoke: Passed in all four repositories. Cleanup is unavailable through the Connector; branch `codex/connector-smoke-20261006-primary-r03` remains and is explicitly non-product state.

These are source/compiler checks, not fresh integrated Editor/Player acceptance.

## Next bounded cycle

Next owner: **Local Validation**. Run exactly one fresh batch P using `Handoff/WEB_TO_LOCAL.md`, a new unused output root, the full 90-cell matrix, six fresh builds, 59 fresh Players, the 18-method preflight, and both 754/755 zero-skip Editor rosters. Validate all four LO repairs together and retain the new `compiler-policy-domains.json` evidence.

If every cell and the seal pass, return `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired`. Do not retry individual phases or make non-trivial Local source changes.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; PureInterpreter expansion disabled. Independent full-stage review remains pending after successful Local evidence.
