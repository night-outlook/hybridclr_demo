# Primary Implementation → Local environment: STOP — remediation not ready

## Current assignment boundary

**No new Local runtime batch is authorized. Current owner remains Primary Implementation.** The earlier S execution assignment was consumed. The independent full-stage R03 review has now returned **FAIL**, with IR-R03-01 and IR-R03-02 still not independently closed. This supersedes the previous current-state text saying the independent review was NotRun; it does not alter the historical Local reports or the original reviewer report.

Primary has published a bounded corrective provenance audit and **implemented native IR-R03-02 terminal entry checks, narrow fixed-diagnostic construction, and a separate four-Player regression harness**. Both native policy header CI platforms passed, and initial Linux/macOS host receipt tests passed. **Full Unity/IL2CPP compilation, fresh Player behavior and genuine captured-generic/initializer post-poison coverage remain outstanding.** This is still a STOP/status boundary; it does not authorize Local execution until a new explicit exact-source handoff and impact/risk checks.

## Read first

All paths below are relative to `Docs/AssemblyShadow/`:

1. `README.md`, `Plan/CURRENT_STATUS.md` and this file.
2. Unchanged Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`.
3. `History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md` **and** `INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md` in the same directory.
4. `History/M07R/R03/IR_Remediation/PRIMARY_REMEDIATION_2026-10-08.md`, `ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json` and `IR_R03_02_NATIVE_DESIGN_2026-10-08.md` in the same directory.
5. Original R03 Design/stages/remaining-completion requirements and HUMAN_REVIEW_GATES; recorded D1=A/D2=A disposition, bounded exit matrix and deferred X02 plan.

The historical `S_Reconciliation/EVIDENCE.json` is preserved, but its incorrect original-archive family and associated unjoined claims are withdrawn by the corrective index. Do not treat the old five-part/18,160-member claim or stale independentReview=NotRun value as current authority.

## Exact source identities — not a runtime assignment

All feature branches: `codex/assembly-shadow-r01b-h1`.

| Repository | Owning Local checkout | Identity and role |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Original S runtime `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`; original evidence publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; new audit/tests/workflow source `38575b165d798defe545f2501f1fc307ccac44a3`; exact current documentation descendant is in final Primary readback |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | Runtime unchanged: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | Runtime unchanged: `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | Historical S runtime `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`; current IR native source candidate `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` (NOT verified by S) |

The post-S history now includes provenance tools and **new test/native source changes**; the former blanket instruction that every descendant after fc55 is Docs-only is no longer true. Distinguish the S executable tuple, evidence publication, audit source and final documentation transport. Do not infer new runtime validation from the latest branch tip or smoke commits. Preserve unrelated/dirty working trees; do not reset, stash, clean or switch an occupied project for convenience.

## Completed Primary evidence work

[Run 37845000985](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985), job `113543552737`, actually passed 30 synthetic host tests and the bounded read-only original-S audit. The nine committed archive parts reconstructed 587,907,380 bytes with SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`. All 15,713 archive members and 90 ledger/cell pairs matched. Selected archived P05/integration/C04 receipts were joined to those bytes; original and tools checkouts stayed clean.

This does not prove every source/build/process semantic join, resolve the earlier capture's omissions, reproduce the native defect or replace independent review. The audit explicitly keeps `fullSourceBuildProcessSemanticAudit=false`, `independentReviewer=false`, `unityRun=false` and `runtimeAcceptance=false`. Both disputed C04 attempt/success fields are NotRecorded, not observed false.

The corrective record binds the exact script/test source, original input, inner output hashes, artifact `11579112494` and its separate outer ZIP digest. Preserve the earlier failed/successful audit revisions and historical captures. Do not reseal original S or edit its raw receipts to match a summary.

## Current IR-only committed source, CI and experimental boundary

- Native candidate: `il2cpp_plus@9ce1c1bfec9a21b92ea300acda5f27a3815b2c37`, with terminal policy header, modified `AssemblyShadow.cpp`, host native policy tests, and `.github/workflows/r03-ir-terminal.yml`. [Native CI 37872834945](https://github.com/night-outlook/il2cpp_plus/actions/runs/37872834945) passed **header-policy** tests on Linux and macOS; the full native compilation and Player are distinct.
- Primary demo test sources: `Tools/AssemblyShadow/R03/PlayerProject/AssemblyShadowR03Probe.cpp` (new opt-in native stimuli), `Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs`, `run_terminal_local.py`, `test_terminal_contract.py`; `Tools/AssemblyShadow/R03/source-pins.json` targets the native candidate only. The full original S and R03Completion input proofs remain separately pinned to their historical native revision.
- One pinned host [run 37873542257](https://github.com/night-outlook/hybridclr_demo/actions/runs/37873542257) passed 41 strict Python regression tests on Linux/macOS (later integer-bound negative tests and API checks need their own source-bound proof).
- New workflows `r03-ir-host.yml`, `r03-ir-player-api.yml`, and extended `r03-build-api.yml` check host contracts, compile-only C# IR API and the pinned native SDK profile. Do not infer their verdicts from an earlier commit or a queued run. The original S provenance auditor's narrow sparse-checkout job now discovers only `test_audit_s_provenance.py`, avoiding a false import failure from unrelated IR runner modules.
- **Limit**: release/debug ON caught baseline-owner, release ON test-driven `FailTypeResolution`, and OFF ordinary control are the only four fresh-process cases defined. Genuine captured generic and post-publication module-initializer failure, full interface paths and all affected R03/M00–M07 regressions are **not** silently certified by this subset.

## What must remain with Primary before a new handoff

Primary has **implemented** the native terminal guard and a fresh four-process subset; the remaining Primary work is to reconcile full translation-unit/package/API compilation, source-test shortcomings and genuine captured-generic/initializer/interface paths that the current witness does not cover. The existing focused receipt verifier demands pre-poison positive active reflection/delegate and AOT canary, actual attempted post-poison calls, zero AOT body side effects, unchanged first recovery and fixed diagnostics; the macOS Player checks are **NotRun**. Do not describe host-only policy tests as full runtime success.

Primary must also complete proportionate role-specific evidence joins and material omitted-source inspection. Missing fields or workflow success must not be promoted to evidence of an operation never observed. The withdrawn digest-family origin remains unresolved unless directly established; no invented transformation is permitted.

Only after all reasonable source/test changes, successful pinned native/API compile evidence and pre-handoff checks may Primary replace this stop boundary with exact pushed pins, implemented commands, fresh unused output roots, storage/source prerequisites and a proportionate Local Validation assignment. A future IR batch would use `Tools/AssemblyShadow/R03IR/run_terminal_local.py` with exact `--workspace`, `--output`, `--unity`, `--demo-commit` arguments to run three fresh builds and four fresh Players; **do not execute that command under the present STOP state**. It is not a rerun of S. Genuine generic/initializer coverage must be considered explicitly when deciding whether a single broader Local batch is practical. Local's role then remains compilation/build/test and bounded debugging, not designing the substantive native repair. No such assignment is issued in this checkpoint.

## Evidence preservation and forbidden actions

Original S live root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261007S-lr-recovery`.
Original S publication receipt: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03LocalBatch-20261007S-lr-recovery-2/PUBLICATION_RECEIPT.json`.
Original committed evidence: `History/M07R/R03/local-validation-20261007-batch-s-evidence-ready`.

Preserve S/R/Q/P/O/N, earlier prerequisites and every original verdict. Retained R remains staged: do not open it in Unity, restore/finalize it, move or delete it. Its historical Git cause remains Unavailable. Four contaminated unisolated warm certificates remain Failed. Do not overwrite Local-owned reports with Primary conclusions.

Do not invoke `run_completion.py`, `run_storage_checked.py --execute`, StructuralRestore or any historical batch under this file. Do not change credentials, protocols, storage thresholds, timeouts, warm-up, leases, schemas, source pins, acceptance flags or agent/reviewer configuration to advance a gate. Read-only status/evidence inspection is not authorization to create a new runtime result.

## Review and approval boundary

D1=A/D2=A is already recorded and is not being re-requested. R03 remains bounded to conservative NativeLayoutAdmissionV1; V1-external PureInterpreter expansion is deferred to X02. Performance observations do not approve a production SLA or deferred R02 CPU/H1 RSS risks.

The existing independent FAIL review and its erratum remain authoritative historical review outputs. New Primary code and Local evidence will require separately triggered independent re-review. Main-agent self-review and byte-check scripts are not substitutes. Automatic gate-review settings remain unchanged; no model/helper identity or approval is inferred.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. H2 remains separately human-initiated; no H2, X02 or M08A advancement is authorized. **Local remains stopped. Primary Implementation retains ownership.**
