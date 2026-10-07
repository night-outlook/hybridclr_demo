# R03-LQ-001 — storage admission and observation design

## Decision and scope

Treat Q as **ReturnRequired, 89 Passed / 1 Failed**. The one failure is an observed filesystem allocation exception, not an established HybridCLR product defect. Retain Q's 59 passing Player checks, six passing builds, passing 18/754/755 Editor cases, repaired dependency/bridge and live-policy subproofs as their own empirical results. Q's restored-baseline zero-root/zero-closure result remains **Unavailable**. P's historical success on that subproof cannot replace Q's missing output.

Add an opt-in Primary-owned storage entry point. Do not modify `R03Completion`, `R03`, the R02 bridge, C# producers, native code, manifests, source pins, fixtures, deadlines or acceptance gates. The new entry point subclasses the existing Completion batch solely to observe and enforce an environmental prerequisite. Existing cell execution, dependency handling, commands, process supervision, cleanup and sealing are reused.

## What is known and not known

Local publication `69af19f63ec20b900d28b3fab27c646d47264736` records a single execution from `8f7c245a68bffc1db3ad2fcba829bcc8e71b22c0`. Its command 0126 failed at `Directory.CreateDirectory(Path.Combine(root, DirectoryName))` in `ShadowRawTypeAdmissionEvidence.Capture` after deriving the proof but before writing its capture directory/files. The Unity inner/outer exit was 1; timeout and surviving process group were false. This does not justify removing the evidence capture, accepting a partial snapshot, retrying a phase or changing a policy guard.

At entry, `df` reported 22 GiB available on `/dev/disk3s1`; the later observation reported approximately 14 GiB. The APFS container reported 14,847,991,808 unallocated bytes (about 13.83 GiB), about 97% used. The batch and `/private/tmp` were on the same Data volume. `/Volumes/Data` was another volume in the same APFS container, not evidence of an independent capacity pool. The local Q label uses October 6 PDT; its execution ended October 7, 2026 at 01:12:51 UTC. Keep those original clocks and directory names.

Neither capacity sample occurred at the exact failed allocation. Transient container pressure, another writer, quota/reserve effects, or filesystem metadata/allocation behavior remain hypotheses, not established causes. Reported free file-node counts do not establish or rule out the failed APFS metadata allocation. No fresh inspection of the user's Mac filesystem was possible in Primary.

## Environmental prerequisite

Before constructing a new batch, the new script authenticates the four repository heads through the existing `identity` helper, rejects reused or overlapping output paths, and authenticates Q's preserved failed cell by its pinned SHA-256. It performs a bounded metadata-only scan of the retained Q live root, including caches that the evidence archive excludes. It never follows symlinks. A failed/incomplete scan or nested filesystem requires a separate sizing decision; it cannot silently reduce the estimate.

Define `B = max(Q logical bytes per path, Q allocated bytes counted once per inode)`.

Require **at least `max(64 GiB, 2*B + 20 GiB)` currently available bytes at every inspected location**: new batch, future restored capture, workspace, actual child temp, Python temp, sidecar and all four Git common directories. This is a deliberately conservative initial policy: one new retained batch, one publication copy and additional staging/headroom. It is not a measured high-water bound, filesystem guarantee or a universal Unity disk requirement. APFS clone/compression sharing is not deducted. Capacity from paths/volumes is never added together, including paths that share a container. Requiring the same budget on each location is intentionally conservative when devices differ.

Admission uses unprivileged-available bytes (`f_bavail * f_frsize`, falling back to `f_bsize`), not total free blocks or a GUI purgeable-space estimate. Read-only locations and filesystem-identity changes fail the prerequisite. A 1 MiB random-data mkdir/write/flush/fsync/readback probe runs in a uniquely created private directory at each relevant existing ancestor. Cleanup removes only that file and that directory. Probe or owned-probe cleanup failure blocks admission. No arbitrary file deletion, `rmtree`, cache clearing, snapshot deletion, quota change, reserve change or evidence relocation is implemented.

The script records read-only `df -k`, `diskutil apfs list -plist`, `diskutil info -plist` and `quota -v` results before/after the batch. Unsupported/failed diagnostics are recorded as **Unavailable**, not proof that quotas do not exist. Native capacity observations and probes are mandatory; optional descriptive command failures do not fabricate a filesystem diagnosis. A known unresolved quota/container discrepancy is an operator blocker even if the coarse space check passes.

Default invocation is **diagnostics only**. The executing invocation requires `--execute`, obtains its own fresh admission/probes and checks the full initial budget again immediately before construction. A preflight failure leaves the batch root unused and emits a separate blocked admission record. It is not an execution of 90 cells and must not be described as 90 blocked or passed cells.

## During the single batch

The original ninety cell IDs and their order/dependencies remain unchanged. The wrapper samples before and after each reached cell/action and each external command; the owned background thread also samples every five seconds. Samples include UTC/monotonic clocks, phase, sequence, requested and nearest-existing paths, device/filesystem identity, available/total/free bytes and file-node statistics. The future restored-capture path is observed as it becomes available.

A **20 GiB operating floor** is checked at each location. A sampled shortage, read-only/identity change or telemetry failure is latched. It is never cleared just because a later sample recovers. Before subsequent nonessential work, the wrapper raises a storage-prerequisite failure into the unchanged scheduler. The original scheduler still records all ninety IDs when it can continue writing evidence; downstream dependencies retain Failed/Blocked distinctions.

`resource-p05-restore` and `final-authority` remain callable under their original dependencies even after a storage failure. The wrapper does not interrupt an in-flight Unity/Player command or change its timeout, environment, process-group cleanup, argv, result or command number. It does not retry. Original sealing/failure behavior remains responsible for the core result. Actual storage exhaustion may still prevent reporting; an absent receipt is Unavailable, not inferred success.

Immediately before the production-integration action, perform another bounded allocation probe at the new restored-capture's existing ancestor and retain its separate receipt. Do not pre-create the producer's `return-baseline` output, change its freshness guard, or write anything under the old Q tree.

Python exceptions retain their type, message, errno/path when present, full traceback, clock and phase/command association in separate files. The original Unity log and command receipts remain authoritative for a managed/native exception. A small probe does not reproduce the full allocation sequence; sampled minima are not the actual failure-instant capacity or a proven peak. No tree scans, diskutil calls or allocation probes run during Player measurements: periodic observation is limited to statvfs and a small JSONL append. Its overhead is not claimed zero, and no performance SLA is approved.

## Evidence separation and verdict

Storage evidence lives outside the core batch root so it does not race or alter the existing seal. The monitor is stopped and joined before the storage session result is written. `dispatch.json` binds the core result, when available, and the storage session hash; the session binds the telemetry hash. Source files are checked after execution. Local must preserve the full storage sidecar in its new checkpoint and bind it into its publication receipt.

A fresh batch is evidence-ready only when its original 90 cells and seal pass, storage admission is Admitted, storage session is Passed, wrapper exit is zero, and final source/custody checks pass. A passing storage session alone is not a passing batch; a non-passing storage session cannot be hidden behind a passing core result. Never rewrite the core result or old Q/P/O/N verdicts to combine these conditions.

Before publication, size the new live root and recheck that the publication checkout/Git storage have at least `max(20 GiB, new planning bytes + 20 GiB)` available. This may conservatively overestimate the selected checkpoint. Do not begin copying or packing into known inadequate space. If insufficient, preserve the live evidence and publish a small factual blocker report rather than delete history or manufacture a complete checkpoint.

## Capacity remediation and alternatives

The preferred bounded route is **operator-provided headroom on the existing approved filesystem**, then fresh admission. Local is authorized to measure and report, not choose and delete unrelated user data. Closing unrelated disk-intensive applications with operator approval may reduce contention but is not evidence of adequate space by itself.

A genuinely separate volume/container is an alternative only after its actual mounted path, workspace/Git/temp allocation and preservation plan are explicitly approved. Creating/moving into another APFS volume in the same container does not manufacture capacity. The existing child command policy still uses `/private/tmp`; moving only the batch does not relocate those allocations. No external volume name/path is invented or silently selected in this handoff.

If headroom cannot be established safely, return **CapacityBlocked; batch NotRun**. If ENOSPC recurs after admission, return the actual failed path, closest samples, probe, diskutil/quota observations and original command/log/partial outputs. Do not simply lower the threshold, extend deadlines or invoke another batch.

## Tests and review

The new tests cover admission limits, the recorded Q capacities, available-versus-free semantics, read-only/device changes, missing data, traversal/aliases, hardlinks/sparse files, special files and scan limits, probe fsync/quota/cleanup failures, untouched sentinels/Q input, exclusive outputs, monitor lifetime and latched breaches. Entry tests cover diagnostic-only mode, blocked preconstruction, exactly one dispatch, failure receipts, and unchanged command lifetime. Real Completion constructor/scheduler tests isolate expensive external actions, assert all ninety cells and the existing graph-before-integration order, and prove cleanup survives a shortage. These are tests, not new Unity/Player results.

Re-run all 48 storage tests plus the retained five LP orchestration and nine strict R02 schema tests. CI is separate from fresh Mac storage admission. Do not claim C#/native revalidation in Primary; those sources did not change. Independent full-stage review and Human Review Gate approval remain pending.

## Rollback

The changes are additive. Rollback is a new Primary-owned forward commit removing/updating the new entry-point assignment and diagnostics after reviewing evidence; do not reset the feature branch or remove history. Bypassing this storage entry point for batch R is not authorized merely because the old entry point still exists.

## Primary references

- Apple, APFS space sharing: https://support.apple.com/en-ng/guide/mac-help/sysp560a2952/mac
- Apple Disk Utility, volume quota/reserve semantics: https://support.apple.com/en-by/guide/disk-utility/dskua9e6a110/mac
- Python, statvfs fields and fsync: https://docs.python.org/3.13/library/os.html
- Apple statfs reference: https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/statfs.2.html

These explain the filesystem model/API choice, not Q's unobserved failure-instant cause. The actual project evidence is `../local-validation-20261006-batch-q-return-required/preflight/FILESYSTEM_FAILURE_OBSERVATION.json` and the Local-owned handoff reports at publication `69af19f6...`.
