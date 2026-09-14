# Prompt for the next agent

Continue the H1 assembly-shadow remediation coordinator task from this Git checkout.

First read:

- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/transfer/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/transfer/h1-transfer-manifest.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-handoff.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/plan.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/Planning/milestone-plan.json`
- the transferred coordination records named in the manifest

Current truth:

- H1 is `InProgress` and technically `Blocked`.
- The independent M08 whole-chain review is `FAIL`.
- `humanGatePassed=false`.
- `readyForHumanH1=false`.
- `mayEnterR02=false`.
- R02 remains closed.

The candidate demo source is on `codex/assembly-shadow-r01b-h1`; the candidate native source is a separate nested repository on the same branch. The clean frozen native build source is `hybridclr_frozen_h1_v5` at `db685e44afb5aee440efae2eb7bec4205aac090d`. Do not interchange active-native and frozen-build provenance.

Continue in this order:

1. Complete the exact witness acquisition/policy contract for the current Bootstrap, including `FixedAssemblyBytes`.
2. Authenticate managed diagnostic source-to-binary and effective Debug/Release compiler provenance in the unfixed reproduction.
3. Freeze a new matching baseline and rebuild its Players, fixtures, replay, and receipts.
4. Run fresh current-candidate `R01EarlyLaunches` for the ordered 11 modes: `Control`, `OrdinaryFirst`, `OrdinaryAfterReserve`, `Oversize`, `Mismatch`, `Type`, `Object`, `Cctor`, `NativeScript`, `MetadataFailure`, `InitializerFailure`.
5. Update the M06 aggregate and seal the schema-2 successor package.
6. Obtain independent whole-chain M08 `PASS`.
7. Stop at the explicit human H1 gate; do not enter R02 automatically.

Preserve `Passed`, `Failed`, `Unavailable`, `NotRun`, `NoCoverage`, `ReusedAudited`, and historical limitations distinctly. Do not clean dirty worktrees, overwrite sealed evidence, rewrite receipts, or claim H1 readiness from focused tests or historical startup evidence.
