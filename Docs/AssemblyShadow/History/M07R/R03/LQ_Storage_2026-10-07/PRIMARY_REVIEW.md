# R03-LQ-001 — Primary reconciliation and storage-readiness review

## Verdict and scope

**Environmental prerequisite unresolved on the Local Mac; Primary implementation of admission, diagnostics and conditional batch-R dispatch is complete.** This is a bounded Primary review, not an independent full-stage review, a disk-repair claim, or permission to start an unadmitted batch.

Q publication is `69af19f63ec20b900d28b3fab27c646d47264736`; its executed demo was `8f7c245a68bffc1db3ad2fcba829bcc8e71b22c0`. Q retains 90 recorded cells: **89 Passed / 1 Failed / 0 Blocked**. Six fresh builds, all 59 Player checks and 18/754/755 Editor cases Passed with zero skips/inconclusive. Binding order, strict R02 bridge, resource aggregate, five eligibility reports and live policy evidence passed their own checks. The integration failed during restored-baseline output allocation; its zero-root/zero-closure proof is **Unavailable**. Q's seal Passed. None of these facts promotes Q to a green batch. Q/P/O/N and the contaminated controls' Failed unisolated warm certificates remain unchanged.

## Filesystem finding

The retained C# stack identifies `Directory.CreateDirectory` in `ShadowRawTypeAdmissionEvidence.Capture`, after derivation and before its fresh evidence writes. The actual source at package pin `948c0e3b...` matches that path. The direct failure is `IOException: No space left on device`; no product-source defect has been established. Replacing the producer, skipping its evidence, or accepting P's old restored-baseline proof would be unjustified.

The retained entry observation shows 22 GiB available. A later APFS observation reports 14,847,991,808 unallocated container bytes; batch/temp/Volumes observations refer to the same Data filesystem. They do not measure the failure instant or identify a quota, metadata limit, competing writer or transient peak. `/Volumes/Data` is a sibling volume within the same APFS container, not demonstrated independent capacity. The exact allocation cause beyond ENOSPC remains uncertain.

Primary read the published Local reports and filesystem observation through the Connector. It did not inspect the Mac's current free space, change its storage, or repeat the Q invocation. Details and primary API/filesystem references are in DESIGN.md. Current capacity is explicitly NotRun in EVIDENCE.json.

## Source authority and change boundary

All branches are `codex/assembly-shadow-r01b-h1`. The storage source/CI commit is **`357a9024865561362cd2c42fa8f793f56aac1763`**, a direct descendant of Q's publication. Its five additions are:

- `Tools/AssemblyShadow/R03Storage/storage_guard.py`
- `Tools/AssemblyShadow/R03Storage/run_storage_checked.py`
- `Tools/AssemblyShadow/R03Storage/test_storage_guard.py`
- `Tools/AssemblyShadow/R03Storage/test_storage_dispatch.py`
- `.github/workflows/r03-storage.yml`

No existing Completion/R03/R02 code, C#, package/native/IL2CPP source, source-pin manifest, Player fixture, Editor roster, build profile, command lifetime, warm-up, lease or timeout changed. The other three feature heads remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, and IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. Final transport is a Docs-only descendant, supplied as an exact SHA in the final prompt and checked by the handoff shell.

## Reviewed design and implementation

The additive entry point reuses the actual Completion constructor, scheduler and complete execute method. It adds storage checks around actions/commands; it does not duplicate the ninety-cell plan or alter its dependency graph. The direct original entry point is retained for historical reproducibility but is not the authorized R entry.

Before batch construction, admission authenticates the original Q failed cell, measures its retained live-root metadata footprint, checks every relevant filesystem location, and performs bounded real allocation/fsync/readback probes in newly owned temporary directories. It requires `max(64 GiB, 2*B + 20 GiB)` available at every location. This is a conservative planning policy; neither B nor the formula is a known peak, reservation or guarantee. `f_bavail`, not total/free/purgeable space, is used. Shared-volume capacity is never summed. Inode statistics are diagnostic only. Probe cleanup removes only its own two paths; a cleanup failure denies admission. Nothing deletes, moves, purges or reconfigures historical/user storage.

During execution, five-second and action/command-boundary observations record capacity and filesystem identity. A sampled breach of the 20 GiB floor, filesystem switch or observation failure latches the storage prerequisite as lost. New nonessential work then fails through the existing scheduler. P05 restore and final authority retain their original cleanup path even after that loss; no in-flight Unity/Player command is cancelled or retried. A fresh bounded probe before integration tests its new capture ancestor without creating `return-baseline` itself.

The periodic observer does not perform tree scans, diskutil calls or probes during Player measurements. Its small metadata/logging overhead is not claimed zero. It is joined before sidecar completion. Original core results/seal are not rewritten; sidecar session/dispatch hashes are additional conditions, not replacements for the core verdict. Python exception evidence retains type, message, errno/path where available, traceback and phase. Unity exceptions remain anchored to original Unity/command logs.

The handoff additionally rechecks publication capacity before copying/packing a new checkpoint, forbids arbitrary evidence reclamation, and provides a CapacityBlocked/batch-NotRun return path. A different physical storage route requires an explicitly approved mounted path and preservation plan; Local is not assigned a storage-migration design or non-trivial source correction.

## Test and evidence review

At the exact published source commit, **GitHub Actions run 37563039265 Passed on Linux and macOS**. Each platform passed **48 new storage tests, 5 retained LP orchestration tests and 9 retained strict R02 schema tests: 62 total, zero failures/errors/skips**. Both artifact ZIP digests, all four indexed outputs and all **419 source-file hashes per artifact** were authenticated. Exact IDs, sizes, hashes and suite commands are retained in EVIDENCE.json and the source-controlled workflow. CI did not run Unity or a Player, and it does not prove Local Mac capacity.

The same 48/5/9 selections passed in the Primary host workspace. The four new Python files parsed/compiled successfully. All three handoff shell blocks passed `bash -n`; this is syntax validation, not execution on the Mac. Existing source was materialized from authenticated Connector artifacts, not an inferred clone or a Local checkout. No local-only Git state is offered as handoff authority.

Coverage includes Q's recorded low-space conditions, threshold equality/deficit, shared-device non-summing, unprivileged-free semantics, read-only and filesystem changes, traversal/symlinks, hardlink/sparse/special-file sizing, incomplete scans, write/fsync/quota/cleanup failures, unchanged sentinels/Q input, exclusive receipts, admission failure before construction, diagnostic-only no-launch, one dispatch, latched telemetry failure and observer shutdown. Actual constructor/cell/execute tests isolate expensive external actions, assert the ninety IDs and LP ordering, verify cleanup is still reached after storage loss, and preserve original command argv/timeouts/results. These controls are not fresh product results.

## Remaining risks and explicit limitations

Admission has not executed against the user's Mac. Physical capacity remediation remains an operator/environment prerequisite, not a completed fix. Quota/diskutil commands can be unavailable; that state does not establish absence of a quota. A known unresolved filesystem discrepancy must be reported rather than ignored.

A small write probe and periodic samples cannot guarantee a later allocation, expose every metadata limit, or capture a shorter-than-sample transient. The floor is not reserved; another writer can exhaust it. The monitor does not kill an ongoing command, so allocation may fail before the next guard. Severe exhaustion can prevent even diagnostic/seal writes; missing evidence remains Unavailable. Bounded metadata sizing authenticates the failed-cell input but is not a full fresh custody audit or an APFS physical-sharing analysis. Local must retain its ordinary source/custody verification.

A green R requires all original cells and the seal, successful storage admission/session and wrapper exit, plus final source/custody checks. Even then independent full-stage review and human approval remain pending. Deferred R02 CPU/H1 RSS risks and failed contaminated certificates are not accepted by this cycle.

## Connector transport and stopping point

All four feature refs were read through the Connector. The retained initial four-repository write/readback smoke remains recorded. This cycle additionally exercised demo's Git-data tree/commit/expected-head ref path on disposable branch `codex/connector-smoke-lq-storage-69af19f6`, base `69af19f63ec20b900d28b3fab27c646d47264736`, created and read-back commit `3dd66a5580c1ef80568ca788732581c5d815129d`. It Passed. The other repositories received no source writes. Branch deletion is not exposed; all smoke branches remain explicitly disposable and must not be merged.

Next owner is Local Validation for storage diagnostics, then at most one complete R invocation **only after fresh admission passes**. If capacity cannot safely be established, return CapacityBlocked/batch NotRun. If a started R fails, preserve every result and return without a phase/batch retry. Rollback is Primary-owned through a reviewed forward commit, never resetting branches or removing historical evidence.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`; PureInterpreter expansion remains disabled.
