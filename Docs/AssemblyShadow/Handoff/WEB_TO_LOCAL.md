# Primary Implementation -> Local Validation: R02 after batch F

## Authority and read order

Read `Docs/AssemblyShadow/README.md`, this handoff, `Docs/AssemblyShadow/History/M07R/R02/F_INTEGRATION_REPAIR.md`, `DESIGN.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json` in that R02 directory.

Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`. F remains 22 Passed, 8 Failed, 4 Blocked followed by failed complete sealing; its preservation inventory is not a complete seal. Preserve A/B/C/D/E/F, all H1 evidence, old R01 comparison and failed raw results.

Common executable/tool source anchor: `995dbf1003c306a69586f882ff02599db7a9780e`. Use the final pushed candidate transport HEAD from Primary's prompt, not this source anchor. Post-anchor changes must be metadata-only under unchanged `shadow_tools.metadata_only`.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `995dbf1003c306a69586f882ff02599db7a9780e` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `b936a495ade1691ebb6f3bab8fdff3ef34f6f192` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` |

Control demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact HEAD `95b85617c92f8ce806f4652d88077936c76c3b8a`. Its siblings use HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`, H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. Control sibling worktrees may be detached at exact commits; their remote branches are `codex/assembly-shadow-r01b-h1` for HybridCLR/package and `codex/assembly-shadow-r01b` for IL2CPP. Both demo worktrees must use their specified branches. Canonical remotes: `https://github.com/night-outlook/<repository>.git`.

All eight worktrees must be clean and source-bound. The control includes the common source as ancestry and differs only in source pins. **Both roles use the new managed parser package.** Do not reuse the old control package, install R02 native runtime into control, or alter unrelated worktrees.

## Completed Primary repairs

The strict type-resolution parser admits the known 33-field R02 extension and still rejects missing/duplicate/unknown/mistyped fields. It preserves UInt64 values and unavailable coverage. `r02` is a preserved parsed view with non-serialized backing storage; the legacy eighteen public serialized fields stay unchanged. Retain raw native JSON for R02 persistence; legacy DTO serialization intentionally excludes that transient view. The real build proof checks the nested 33-field schema separately. New Editor tests cover stripped/narrowed fields and Unity serialization; the actual native-writer/managed-parser and BCL round trips are required host tests.

M07 now prepares and supplies mode-specific Control early-startup capsules before launching. Counts dispatch parameter and nested manifests to their respective existing auditors. Count and diagnostic build transactions capture linker XML and restore only the exact permitted empty-to-known-netstandard expansion; arbitrary changes still fail.

E forensics copies authenticated raw inputs before builds. Missing live E DLLs may be read only from their original Git-bound, digest-verified E archive and exact indexed members. The archive/index and copies are retained. Corrupt existing live data never falls back to an archive. Missing required inputs still prevent a complete seal. No old path is reconstructed and no failed execution is relabeled.

Fixed M00 materialization, native prerequisite ordering, Roslyn v2 kernel identities, source policies, correctness guards, runtime cache and formal timing are unchanged. No non-trivial implementation is assigned to Local.

## One new 34-cell batch

Protocol: `R02LocalBatch-v1`.

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, clang++, and at least 30 GiB free (entry minimum, not a total archive-space guarantee). Close both Unity editors. Resolve absolute tool paths. Set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

Run candidate `Tools/AssemblyShadow/R02/run_local.py` with `--candidate`, final `--candidate-head`, `--control`, `--control-head 95b85617c92f8ce806f4652d88077936c76c3b8a`, absolute `--unity`/`--pwsh`, and an unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Inspect the plan without `--execute`, then add it for one execution. Do not resume or relabel F.

The 34 cells preserve the full scope: exact source/common graph; expanded host checks; E raw forensics; two fixed M00 materializations and fresh controlled ON/OFF graphs; eight functional sidecars; four pilot plus forty formal A/B pairs (88 fresh timing processes); Editor/native/generated-transaction/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity; final authority and full sealing. Require all three new `R02TypeResolutionSchemaTests` and the existing two `R02ProbeContractTests` to pass in Editor results. Inspect M07 early receipts separately from later runtime parser results.

Independent valid cells continue; failed prerequisites block consumers. No automatic semantic retry, timeout increase, hash/pin changes, verifier relaxation, source refactor or case-set reduction is allowed. A new linker output outside the fixed restoration policy returns to Primary with original/generated bytes, not a Local permission change.

## Evidence, review and return

Preserve type-resolution raw JSON and interoperability results, per-mode M07 capsule files/manifests/early receipts, both count audits, linker original/generated/restored bytes, copied E DLLs and their origin/index/archive, per-role M00 materialization, Unity completion snapshots, generated-native receipts, current build maps, all launch/raw/verifier chains, failed attempts, performance analysis and full content-addressed seal. Keep indexed generated roots outside the batch directory. `LOCAL_BATCH_RESULT.json` must bind the completed seal; `SEAL_FAILED.json` or an inventory is not equivalent.

Do not delete retained history to make disk checks pass. If E source paths are absent, the committed forensic cell handles only the exact archived bytes; Local must not improvise another source. Incomplete forensic acquisition remains a fatal full-seal failure even when independent builds complete.

Update and push `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications, first errors, source/build/input hashes and exact evidence locations. Preserve original negative cases; no summary-only replacement of raw evidence. Commission the genuinely independent R02 stage reviewer only when complete evidence is eligible, and retain its verbatim verdict.

H1 remains `PassedWithExplicitDeferredRisk`. D1=A/D2=A are development-stage deferrals, not performance/RAM acceptance. Report measured allocation/reflection/closed-generic and native/managed/RSS effects before H2; keep historical R01 and new H1-runtime-control comparisons distinct. Stop and return to Primary. R02Accepted=false; mayEnterR03=false.
