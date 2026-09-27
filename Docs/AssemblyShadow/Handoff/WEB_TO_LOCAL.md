# Primary Implementation -> Local Validation: R02

## Build-boundary repair from Local return 6212167

This handoff supersedes the failed A/B/C build attempts, not their historical evidence. Read `Docs/AssemblyShadow/History/M07R/R02/BUILD_REPAIR_20260927.md` before the batch. Both candidate and control must fast-forward to the new transport commits; both use the common source anchor listed below. No old candidate build is accepted merely because its internal M07 command printed success.

The runner now supervises each Unity/build command and retires only its exact command-owned Roslyn server, then requires the unchanged outer no-survivor check. Unknown children, changed identity, compiler-byte mutation or remaining processes fail. Player/formal timing commands remain unwrapped. Preserve `commands/*-unity-completion.json` along with the original command logs and receipts.

Before M07, each workspace independently generates the fixed M00 ordinary DLL using `R02OrdinaryInput.Prepare`, then authenticates its source/pins/output. Preserve both `<role>-ordinary-input.json` and the retained ordinary-input root with `preparation.json` and compiled bytes. The existing SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27` is not relaxed. A generation mismatch returns to Primary; Local must not rewrite hashes or copy the other workspace’s DLL. Actual Unity byte equality and macOS long-build cleanup remain unverified until this run.

Use `TMPDIR=/private/tmp` and `PYTHONDONTWRITEBYTECODE=1` for the batch entry process. Child commands additionally receive canonical temporary paths and the committed no-server-reuse environment. Keep all A/B/C roots and seals. Use a new unused output root; no resumed or relabeled acceptance.

## Objective and authority

Run `R02LocalBatch-v1` against fresh source-bound H1-runtime control and R02 candidate builds. Collect functional, concurrency, guard/regression, CPU, memory and complete raw/launch evidence in one serial batch. Do not begin R03.

Read `Docs/AssemblyShadow/README.md`, this file, `Docs/AssemblyShadow/History/M07R/R02/DESIGN.md`, `Docs/AssemblyShadow/History/M07R/R02/LOCAL_VALIDATION_TASKS.md`, and `Docs/AssemblyShadow/History/M07R/R02/source-targets.json`.

H1 remains `PassedWithExplicitDeferredRisk` following D1=A and D2=A. R02 is not accepted. The candidate demo **source anchor** is `82d64ce415c062729f0082e81c1808eaac9602e4`. Use the exact **final pushed transport HEAD** supplied by the Primary handoff prompt; do not substitute the source anchor as a complete handoff. The source-to-HEAD executable delta must be empty under the unchanged `shadow_tools.metadata_only` policy.

| Repository | Candidate checkout | Branch | Source commit |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `82d64ce415c062729f0082e81c1808eaac9602e4` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` |

Control demo checkout: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/hybridclr_demo`, branch `codex/r02-h1-runtime-control`, exact published HEAD `6c950eaa98f995084750fe1ea8f80cfe4c59c61b`. Its executable demo source is the same `82d64ce415c062729f0082e81c1808eaac9602e4`. Its three owning sibling checkouts use HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`, package `0ea633a2c5b936b5af69d944593c55bd2783fca9`, and IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`. All three control runtime/package checkouts may be detached at their exact commits; the metadata authority checks their remote branch identities. IL2CPP control remote branch is `codex/assembly-shadow-r01b`. Never install R02 native code into the control workspace or the historical R01 reference.

Canonical remotes are `https://github.com/night-outlook/<repository>.git`. Preserve any existing unrelated worktrees; new control worktrees must use unused absolute paths and the specified owning repositories, not copies of generated outputs.

## Completed implementation

Immutable complete-physical-type admission certificates and absent-baseline counterpart caching; retained mutable-state guards; bounded observation shards and class memo; diagnostics default level 2; explicit disabled/truncated coverage; shared production-header native tests; R02 opt-in allocation/generic/array/boxing/dispatch/1000-type/worker witness; strict raw verifier; controlled paired performance; complete evidence sealing; generated-input recovery; host build/run cleanup repair; codec-owned-storage attribution.

The production native files are already committed, not patches for Local to apply. Local must not run `tools/r02/finalize_sources.py --prepare` or alter source/pins to make a verifier pass. The read-only `--verify` mode is part of Primary checks.

## Single batch

Prerequisites: macOS arm64, Unity 2022.3.62f2, Python 3.10+ with the existing project tooling, .NET SDK 8 or newer capable of net8.0 host builds, `clang++`, and PowerShell. At least 30 GiB free is an entry check, not a guarantee for every archive. Resolve actual absolute tool paths; do not assume a particular Python installation. Confirm the candidate and control owning checkouts are clean and match the final prompt/source-targets.

Run `Tools/AssemblyShadow/R02/run_local.py` with `--candidate`, the prompt's `--candidate-head`, `--control`, the fixed `--control-head`, absolute `--unity` and `--pwsh`, and an unused `--output` directly under candidate `_temp/AssemblyShadow/`. Without `--execute` it prints the plan; add `--execute` only after checking those inputs. The detailed task sheet gives the complete shell command.

Expected independent cells:

1. Four-repository/source/common-managed-graph authority and host Primary checks.
2. Two new controlled build graphs (candidate/control, ON/OFF), installed-runtime provenance and strict input checks.
3. Eight functional sidecar processes across both roles and four modes: 1/10/10000 operations, 100/1000 physical types, four workers, semantic construction checks, retained correctness diagnostics.
4. Four pilot pairs plus forty formal A/B pairs: 88 fresh processes, frozen balanced schedule, strict R00 verification, no R02 sidecar during formal timing. CPU/RSS statistics are measurements, not SLA approval.
5. Candidate Editor tests, native regressions, M07, startup11, failure/publication/recovery, fresh 132-cell count matrix, lazy/dense, and ordinary/mixed capacity.
6. Final source checks and a complete content-addressed evidence archive. `EvidenceReadyForStageReview` means evidence preparation only; `R02Accepted=false` and `mayEnterR03=false` remain.

Dependencies block on failure; independent valid cells continue. A source-state preflight before each workspace-dependent cell prevents a dirty failed build from contaminating later Players. No automatic semantic retry, source edit, lowered expectation, timeout increase, or historical result substitution is permitted.

## Evidence, failures and recovery

Keep every command JSON/stdout/stderr, partial output, failed attempt, generated-input before/after record, exact build/input binding, launch receipt, raw result, sidecar verifier, paired index, and seal index/archive. Do not retain only PASS summaries. `LOCAL_BATCH_RESULT.json` points to the seal; preserve both. The controlled graphs and count/diagnostic roots outside the batch folder are indexed and retained by the runner.

The retained ordinary capacity corpus is used as authenticated input bytes only, never reused execution. It is found through the fixed historical Git index and exact launch/workload bindings; no basename fallback. Missing external bytes block that capacity path. Preserve the historical seven count archives, source-27df performance bytes, and all H1 evidence.

Record the first actual build/semantic error and every recovery error independently. Do not convert a failed cleanup to Passed because host assertions or Player exit code were zero. If unexpected source mutations remain, preserve them and return the failure; do not reset or clean them automatically.

## D1/D2 and review

Report R02-versus-current-H1-runtime cold/warm allocation, reflection and closed generic results, distributions and sample counts. Retain the older R01 comparison separately; no codec-only causal claim. Report native owned structure bytes, managed bytes, point-in-time RSS and lifetime peak with their different meanings. `codec_memory.py` measures host constructor allocation requests for the unchanged profile-2 storage; it neither measures Unity RSS nor explains the whole historical RSS delta by itself.

After all required evidence succeeds, commission a genuinely independent R02 stage review with the existing reviewer definition and fixed source/evidence inputs. Preserve its verbatim verdict. This is not the later H2 Human Review Gate. Return D1/D2 disposition and remaining risks to Primary before any subsequent stage; no risk is silently waived.

## Local modification boundary and return

Permitted: unused output suffixes, absolute tool resolution, registered worktree setup at the listed commits, normal builds/fixture generation, exact scripted generated-input restoration, command/evidence collection, and bounded environment fixes with receipts.

Forbidden: production or verifier refactors, changing source pins or fixtures after freezing, changing the required case set, hiding failing attempts, relaxing provenance or cleanup, installing candidate runtime into control, cleanup of retained evidence, and beginning R03.

Update `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` with actual Passed/Failed/Blocked/NotRun/Unavailable classifications. Put non-trivial issues in `RETURN_TO_WEB.md` with reproduction command, source/build tuple, first failing path/hash and retained evidence. Commit and push Local's reports and evidence indexes without replacing historical records. No non-trivial implementation is assigned to Local.
