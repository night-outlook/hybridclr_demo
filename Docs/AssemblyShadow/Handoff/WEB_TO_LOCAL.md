# Primary Implementation -> Local Validation: R02 after batch H

## Read first and scope

Read `Docs/AssemblyShadow/README.md`, this handoff, `History/M07R/R02/H_RUNTIME_REPAIR.md`, `DESIGN.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json` under the canonical Assembly Shadow root. Earlier F/G repairs remain included.

Input Local return: `d33792957303488e03529c945ac01ce0eedd660b`. H remains ReturnRequired: 25 Passed, 5 Failed, 4 Blocked with a complete independently audited seal. Count132 and all 1,119 Editor cases passed in H, but that does not validate the new native runtime. Preserve A/B/C/D/E/F/G/H and H1 evidence, original raw failures and archives. No historical execution is relabeled.

## Exact source and owning workspaces

Common executable/tool source anchor: `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`. Use the final remotely verified candidate transport HEAD in Primary's prompt, not this source or the earlier CI authority. The post-anchor candidate delta must be metadata-only under unchanged `shadow_tools.metadata_only`. Both demo remote tips must match the final prompt exactly; stop on movement rather than selecting another HEAD.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `a81bb0d7b886fe941ba4b132296a30dcf4a319cc` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` |

Control demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact HEAD `21c689732cd8087f8ee8fdce4e52a8f2a655f722`. Its siblings under that workspace use HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`, and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Sibling remote branches are `codex/assembly-shadow-r01b-h1` for HybridCLR/package and `codex/assembly-shadow-r01b` for control IL2CPP; control siblings may remain detached at those exact commits. Both demos must use their specified branches.

Control contains the common source as explicit ancestry and differs only in source pins. All eight owning worktrees must be clean, correctly identified and source-bound; equivalent SSH/HTTPS identities are allowed. **Candidate native runtime has changed; install and build fresh in the candidate. Do not install it into control or the separate historical R01 reference.** Both roles retain the same managed package. No old H build becomes a new-runtime artifact through metadata edits.

## Completed Primary work and safety boundaries

Cold, concrete AOT definitions carry compiled layout size/offset data before lazy `size_inited` setup. The native proof trace now recognizes only that narrowly defined fixed layout as baseline-ready; it never initializes the baseline. Active target readiness, all layout comparisons, composite restrictions, full-class cache keys, baseline-use/cctor/vtable/poison/context guards and incomplete-proof rejection remain. Level-2 `[R02LayoutReadiness]` stderr observations are capped at sixteen cold decisions per process and report exact class/image/token/shape/readiness data. Keep those records; no JSON schema or timing exemption is introduced. The exact class responsible for H's old unready counts is not established by its counters alone.

The existing P01/P03 warm 10,000-allocation sidecar assertions remain unchanged and mandatory. A new production-header regression tests cold fixed-baseline readiness, an initially unready target, later single publication, 10,000 allocation-free cache hits, then baseline-use and poison rejection. Synthetic host class descriptors do not substitute for actual Player proof.

M07 and startup11 now use `R02/verify_regressions.py`. The wrapper checks exact candidate authority, validates every field of the known versioned 33-field R02 extension and delegates an in-memory legacy view to the unchanged strict verifiers. Unknown/missing/duplicate/mistyped fields still fail; original raw JSON and hashes never change. Full fourteen-mode M07 and eleven-mode startup evidence is required, with separate `.r02-schema.json` receipts. Startup dispatch uses existing `r01_early_results.main`, not the previously missing script.

Diagnostic Players are built into a new unique `Builds/AssemblyShadow/R01B/<R02-id>-diagnostic/Player.app`; receipt/recovery files remain in `_temp`. Existing or linked output roots are rejected, the receipt must match the exact planned path, and the entire Player root is sealed. The original diagnostic provenance and scene/linker restoration checks remain unchanged.

The F/G parser, early capsules, auditor dispatch, fixed M00 input, forensic archive recovery, quoted host headers, no-survivor completion and five exact Editor requirements remain included. No non-trivial implementation is assigned to Local.

## One new 34-cell batch

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, C++ compiler and at least 30 GiB free (entry minimum, not total evidence-space guarantee). Close both Unity editors, resolve absolute tool paths, set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`. Do not remove history to satisfy disk checks.

Invoke candidate `Tools/AssemblyShadow/R02/run_local.py` with exact `--candidate`, final prompt `--candidate-head`, `--control`, `--control-head 21c689732cd8087f8ee8fdce4e52a8f2a655f722`, absolute `--unity`/`--pwsh`, and an unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Inspect the dry plan; execute once only after source authority passes. Do not resume or relabel H.

Run all 34 cells: exact source/common graph; full host Primary; E forensics; fixed M00 inputs and fresh controlled ON/OFF graphs; eight functional sidecars; four pilot plus forty formal A/B pairs (88 fresh timing processes); five exact Editor contracts; native/generated-transaction/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity; final authorities and complete sealing. Independent valid cells continue; failed prerequisites block consumers. No semantic retry, timeout increase, source/pin/hash edit, reduced case set or weakened warm assertion is authorized.

All eight sidecars must pass before timing. Preserve P01/P03 cold and warm rows, proof/cache/workspace counter deltas and readiness observations. Do not count faster readiness or host codec bytes as CPU/RSS acceptance. D1/D2 need measured effects and residual-risk disposition before H2. The four pilot pairs are not formal acceptance.

## Evidence and return

Retain source/install receipts, host native/managed/schema checks, cold-readiness logs, raw sidecars and strict verifications, all M07/startup capsules/launch/raw/strict outputs plus `.r02-schema.json` receipts, both count audits, diagnostic output-plan and exact receipt/Player tree, original/generated/restored linker and scene bytes, E input copies/archive provenance, M00 receipts, full build/input maps, failed commands, performance samples/analysis and complete content-addressed seal.

No raw result or historical failure is rewritten. `LOCAL_BATCH_RESULT.json` must bind its full seal/index/archive; `SEAL_FAILED.json` or an inventory alone is not equivalent. Retain indexed external roots and all historical archives. If warm publication still fails, return exact class/readiness records with the first failing row; do not initialize baseline classes or suppress the assertion locally.

Update and push `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications and exact input/build/command identities. Return non-trivial issues to Primary. Commission genuinely independent R02 stage review only after complete eligible evidence and retain the verbatim verdict.

H1 remains PassedWithExplicitDeferredRisk; D1=A/D2=A are development-stage deferrals, not production performance/RAM approval. R02Accepted=false; mayEnterR03=false. Stop and return to Primary before R03.
