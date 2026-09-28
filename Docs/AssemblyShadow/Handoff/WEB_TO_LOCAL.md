# Primary Implementation -> Local Validation: R02 after batch G

## Read first and scope

Read `Docs/AssemblyShadow/README.md`, this handoff, and `History/M07R/R02/G_INCLUDE_REPAIR.md`, `F_INTEGRATION_REPAIR.md`, `F_EDITOR_COVERAGE_FINALIZATION.md`, `DESIGN.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json` under that canonical root.

Input Local return: `4c4f50adfd3a44073d14b107227f399c53ea605c`. G remains ReturnRequired: 9 Passed, 1 Failed, 24 Blocked, with a complete independently audited seal. Its only failed cell was host contract compilation, before producer/parser assertions or Unity builds. Preserve A/B/C/D/E/F/G, raw inputs and all H1 history. No old failure or passed subset is relabeled as a current complete run.

## Exact source and owning workspaces

Common executable/tool source anchor: `af9ba49127a7e852fed504a55c733c5f6ec5e54e`. Use the final pushed candidate transport HEAD in Primary's prompt, not the earlier source/CI commit. The candidate post-anchor executable delta must be empty under unchanged `shadow_tools.metadata_only`. Both demo remote tips must match the final prompt exactly; stop on further movement rather than substituting whatever HEAD is current.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `af9ba49127a7e852fed504a55c733c5f6ec5e54e` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` |

Control demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact HEAD `2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`. Its siblings under that workspace use HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`, and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Sibling remote branches are `codex/assembly-shadow-r01b-h1` for HybridCLR/package and `codex/assembly-shadow-r01b` for control IL2CPP; control siblings may be detached at those exact commits. Both demo worktrees use their specified branches.

Canonical HTTPS remotes are `https://github.com/night-outlook/<repository>.git`; equivalent SSH identity is allowed. Verify all eight owning roots, clean state, exact commits/remotes and common non-metadata demo graph. Control contains the common source as ancestry and differs only in source pins. Preserve unrelated worktrees. Never install candidate runtime into control or the separate historical R01 reference.

## Primary repair and retained contracts

The host compiler now uses `-iquote` for project VM headers instead of `-I`. This prevents project `string.h` from shadowing libc++ system includes while preserving quoted project/sibling resolution. No broad replacement include roots, copied native headers or Local flag workaround are required. The receipt records `R02QuotedProjectHeaders-v1`, compiler version, platform and thirteen emitted fixture bindings. Existing strict completion, twelve native plus one legacy fixture and all 33-field/UInt64/coverage/serialization assertions remain unchanged.

The new macOS CI runs the actual writer/parser contract at levels 0/1/2, not only mocked acceptance or lifecycle tests. `PRIMARY_VALIDATION.md` records selected results and their scope. CI does not replace the Local host check or Unity execution.

All F repairs remain: strict versioned parser and separate linked proof; mode-specific M07 early capsules; parameter/nested-specific auditors; narrowly scoped count/diagnostic linker restoration; forensic raw snapshots with exact original E archive recovery. All five exact Editor contracts remain machine-enforced. Fixed M00 materialization, Roslyn kernel identities, generated-native prerequisites, source checks, runtime guards and formal timing remain unchanged. No non-trivial implementation is assigned to Local.

## Execute one new 34-cell batch

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, host C++ compiler and at least 30 GiB free (entry minimum, not a guarantee of total evidence size). Close both Unity editors, resolve absolute tool paths, set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

Invoke candidate `Tools/AssemblyShadow/R02/run_local.py` with exact `--candidate`, final prompt `--candidate-head`, `--control`, `--control-head 2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`, absolute `--unity` and `--pwsh`, and an unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Inspect the dry plan; add `--execute` only after source-authority checks pass. Use one new run, not resumed or relabeled G.

Run all 34 cells: source/common graph; full host Primary including actual contract; E raw forensics; both fixed M00 inputs and fresh controlled ON/OFF graphs; eight functional sidecars; four pilot plus forty formal A/B pairs (88 fresh timing processes); five exact Editor tests; native/generated-transaction/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity; final authorities and complete sealing. Independent valid cells continue; failed prerequisites block consumers. No semantic retry, timeout increase, hash/pin edit, weakened expectation or case reduction is authorized.

## Evidence and return

First verify `primary/type-resolution-contract/results.json` is Passed with diagnostics levels 0/1/2, twelve native and one legacy fixture, required assertions and clean command groups. Keep all compile/emit/managed command logs, compiler-version receipt, fixture JSON and bound binaries. A compiler or parser failure must retain the first failing command and full stdout/stderr; do not replace it with a successful synthetic regression.

Keep the five XML-bound Editor requiredCases, M07 capsules and early receipts, both count audits, linker original/generated/restored bytes, E snapshot/archive provenance, M00 receipts, Unity completion snapshots, generated-native bindings, build maps, launch/raw/verifier chains, performance data, failures and the full content-addressed seal. Keep indexed roots outside the batch directory. `LOCAL_BATCH_RESULT.json` must bind a complete seal; `SEAL_FAILED.json` or an inventory alone is not equivalent. Do not delete history to satisfy disk checks.

Update and push `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual Passed/Failed/Blocked/NotRun/Unavailable results and precise source/build/input/evidence identities. Return non-trivial problems to Primary rather than changing code. Commission the genuinely independent R02 reviewer only after all required evidence is eligible; preserve its verbatim verdict.

H1 remains PassedWithExplicitDeferredRisk. D1=A/D2=A are development-stage deferrals, not performance/RAM acceptance. Report measured allocation/reflection/closed-generic and native/managed/RSS effects before H2, keeping historical R01 separate from the current H1-runtime control. Stop and return to Primary. R02Accepted=false; mayEnterR03=false.
