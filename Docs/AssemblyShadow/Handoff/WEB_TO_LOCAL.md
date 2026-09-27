# Primary Implementation -> Local Validation: R02 after batch E

## Read first and scope

Read `Docs/AssemblyShadow/README.md`, this handoff, `History/M07R/R02/E_M00_REPAIR.md`, `DESIGN.md`, `LOCAL_VALIDATION_TASKS.md`, `PRIMARY_VALIDATION.md` and `source-targets.json` under the canonical Assembly Shadow root.

Input Local return: `1d7dc134003206ada8a92b50763ca2da7dc9530d`. E remains ReturnRequired: 9 Passed, 2 Failed, 22 Blocked. Its Roslyn cleanup succeeded; both M00 compiler outputs failed the unchanged fixed-image hash. Preserve E, earlier A/B/C/D, their raw DLLs/seals and all H1 evidence. No failed execution is relabelled.

H1 remains `PassedWithExplicitDeferredRisk`; D1=A/D2=A remain development-stage deferrals requiring R02 measured disposition before H2. R02Accepted=false; mayEnterR03=false.

## Exact source and workspace authority

Common executable/tool source anchor: `d4cfbe5da29482a3b307fbec3333821615288129`. Use the final pushed candidate transport HEAD from the Primary prompt, not this earlier source anchor. The post-anchor delta must be metadata-only under unchanged `shadow_tools.metadata_only`.

| Repository | Candidate owning checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `d4cfbe5da29482a3b307fbec3333821615288129` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` |

Control demo: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact HEAD `5a931fe86795e8cc192d3df262cdee824b105963`. Its siblings in that workspace use HybridCLR/package commits above and H1 IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933` (remote branch `codex/assembly-shadow-r01b`). Control sibling checkouts may be detached at those exact commits; both demo checkouts must use their specified branches. The control includes the common source as ancestry and differs only in source pins. Canonical remotes are `https://github.com/night-outlook/<repository>.git`.

Check all eight owning worktrees, remote identities and common executable graph. Preserve unrelated worktrees. Never install candidate native code into control or the separate historical R01 reference.

## Primary implementation and M00 contract

The byte-pinned historical witness is now a compact, committed fixture with exact archive/member provenance. Each role independently decodes its own fixture and stages the original 4,608 bytes before M07. Required SHA-256 remains `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`; full CLI identity and origin are checked. Existing matching bytes are not rewritten; wrong bytes, links, altered origin/pins or concurrent writers fail. No role reads the other role's generated DLL.

This replaces the incorrect compiler-and-stage helper, which was removed. Receipts are now schema 2, `FrozenHistoricalInputMaterialization`, not a fresh-compilation claim. Do not run the obsolete `R02OrdinaryInput.Prepare` or fabricate schema-2 receipts for E. The full M07 workflow still freshly compiles and enforces original provider semantic, fixed-image, CodeGen and installed-runtime provenance checks. No accepted hash or semantic variant changed.

The independent `m00-batch-e-forensics` cell reads the exact E receipt blobs and their retained compiled DLLs. It records MVID, embedded PDB paths, all differing spans and conservative PE provenance comparisons. It changes no binary and never authorizes normalized bytes. Missing old bytes or malformed input fail that diagnostic but do not block otherwise valid fresh build cells. All required cells must pass for evidence-ready status.

Roslyn v2 kernel identity, strict no-survivor completion, generated-native prerequisites, runtime/cache/guards, formal timing and recovery policies are unchanged.

## One new 34-cell batch

Use macOS arm64, Unity 2022.3.62f2, Python 3.10+, PowerShell, .NET SDK supporting net8.0, clang++, and at least 30 GiB free (entry minimum, not a total-space guarantee). Resolve absolute tool paths and close both Unity editors. Set `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1` for batch entry.

Run `Tools/AssemblyShadow/R02/run_local.py` from candidate with `--candidate`, final `--candidate-head`, `--control`, `--control-head 5a931fe86795e8cc192d3df262cdee824b105963`, absolute `--unity`/`--pwsh`, and a new unused direct child of candidate `_temp/AssemblyShadow/` as `--output`. Inspect the plan without `--execute`, then add it for the single execution.

Preserve the full prior 33-cell scope plus E forensics: source/common graph; host checks; both fixed-input materializations and new controlled ON/OFF build graphs; eight functional sidecars; four pilot plus forty formal A/B pairs (88 fresh timing processes); Editor/native/M07/startup11/failure/count132/diagnostic/lazy-dense/ordinary-mixed-capacity; final authority and complete sealing. Generated-native inputs still depend on candidate-build and gate the transaction test. No historical generated header or DLL default is permitted.

Independent valid cells continue; invalid dependencies block consumers. No automatic semantic retry, timeout increase, pin/hash change, weakened verifier, production refactor or reduced case set is permitted. D1/D2 need measured effects/distributions and residual-risk disposition, not a PASS label. Do not treat the four pilot pairs as formal acceptance.

## Evidence and return

Retain `m00-batch-e-forensics/analysis.json`, all authenticated E DLL inputs, per-role ordinary-input authentication and materialization roots, unchanged Unity-completion snapshots, actual command exit/signals, generated-native input/integrity receipts, fresh build/input maps, every launch/raw/verifier chain, negative inputs, partial failures, recovery receipts and the complete content-addressed seal. Keep generated roots outside the batch folder and all failed attempts. `LOCAL_BATCH_RESULT.json` must bind its seal/index/archive.

Historical capacity and frozen M00 data are input reuse only. Do not promote historical Player execution or host codec-storage attribution to current runtime/RSS acceptance. The old R01 reference remains a separate comparison identity.

Update `Handoff/LOCAL_VALIDATION.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications. Put non-trivial issues in `RETURN_TO_WEB.md` with first failing command/source/build/input hash, complete rejection diagnostics and retained evidence. Commit and push Local reports and evidence indexes. No non-trivial implementation is assigned to Local.

Commission the genuinely independent R02 stage reviewer only when all required evidence is eligible; preserve its verbatim verdict. This is not the H2 Human Review Gate. Stop and return to Primary; R03 remains closed.
