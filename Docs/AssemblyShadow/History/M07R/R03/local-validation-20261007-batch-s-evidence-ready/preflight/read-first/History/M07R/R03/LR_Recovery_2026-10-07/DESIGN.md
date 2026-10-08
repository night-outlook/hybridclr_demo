# LR-002 — Git observations and P05 recovery ownership

## Evidence and objective

Input authority is Local publication `1fb504b2732c72dd1c403060396276af69d6251a`, executed source `ba57a3391da9627e694ee33f8bfe3cb993e6c56a`, on `codex/assembly-shadow-r01b-h1`. R remains ReturnRequired: 47 Passed, 1 Failed, 42 Blocked. Six builds, 18/754 Editor cases and 23 focused Players completed; 755 resource cases and 36 other Players did not run. Storage and seal Passed. Original failure evidence is in `../local-validation-20261007-batch-r-return-required/`, particularly RETURN_TO_WEB's LR-002 and `preflight/P05_RESTORE_FAILURE_ANALYSIS.json`.

The failed boundary was Python's fresh `git ls-remote` check before launching StructuralRestore. The old helper discarded the repository, argv, exit and streams. Its exact transport cause is Unavailable; later passing Git observations do not retroactively pass that check. This is not an established C#/native runtime defect. The design fixes two harness properties: diagnosability and the ordering of cleanup versus network-dependent acceptance.

## Two authorities, neither interchangeable

Normal source authentication continues to require the exact local repository root, HEAD, branch, clean tree, canonical origin, committed source catalog and bytes, generated four-repository pins, project marker, source verification and executable-input inventory. It also requires a fresh remote response whose complete parsed tuple equals `[expected commit, expected ref]`. Empty, duplicate, wrong-ref or wrong-tip replies fail.

Only the internal P05 cleanup path may omit the network portion. It performs all the same local checks through `authenticate_cleanup_copy`. There is no cached remote-pass fallback, alternate checkout, ambient source authority or general permissive mode. A failed local check denies cleanup before launching Unity. The original C# restore additionally verifies transaction identity, quiescence, original backup, current defines and the allowed settings mutation; its implementation is unchanged.

Recovery of a new batch runs in this order:

1. Create exclusive `transaction-recovery/` evidence; refuse a second invocation.
2. Authenticate the exact local source/project and transaction state. With no recorded state, do not mutate settings; record NoRecordedMutation.
3. For a recorded transaction, authenticate ownership and backup hash, preserve staged settings bytes, and record local authority.
4. Run the existing StructuralRestore command once, with unchanged argv, timeout, producer receipts and validation.
5. Run the existing guarded exact-byte restorer, which requires the production restore receipt before replacing settings with the original backup. Preserve Unity-reserialized bytes and all original receipts.
6. Require fresh normal source/remote authentication after recovery. Only then can the restore cell pass and dependent work proceed.

`cleanupResult` and `remoteAuthority` are separate facts in `transaction-recovery/verification.json`. Successful cleanup followed by a failed remote check yields a Failed cell and Blocked dependents, not acceptance. A malformed producer receipt or changed settings does not trigger a blind byte-copy fallback. The existing ninety-cell scheduler, dependency order, storage essential-cleanup path and final authority check remain in place.

## Git diagnostics contract

`R03/git_diagnostics.py` retains one invocation with the existing 120-second timeout and non-interactive Git setting. Each failure and successful remote observation records repository, complete argv with credential-bearing values redacted, UTC clocks, duration, status, numeric exit when actually available, requested source tuple, phase, and helper SHA-256. Failure categories distinguish nonzero exit, timeout, spawn failure, UTF-8 decoding failure and receipt-write failure.

Streams are represented by original byte length/SHA-256 and at most 16 KiB of redacted UTF-8 excerpt each. URL credentials/query strings, authorization headers and common token/password forms are removed before clipping. Raw streams are not persisted. No environment or credential configuration is dumped. Excerpts are intentionally not a promise of complete raw transport reconstruction or universal secret detection. Local must not enable Git tracing or introduce unusual secret-bearing command arguments; inspect redacted diagnostics before publication.

An active ContextVar scope binds cell observations to `git-observations/`; exclusive files are flushed/fsynced. Context restoration is guaranteed. Successful local `git show`/catalog output is not copied into receipts. Pre-constructor failures carry the bounded observation inline because no batch evidence root exists yet. A successful command with an unwritable required receipt fails closed. The receipt records requested authority, not proof of source acceptance. There are no automatic retries, fetches, remote substitutions, protocol changes or relaxed HEAD checks.

## Retained R is forensic state

Do not restore, finalize, reopen in Unity, relocate, or delete the retained R project or sealed checkpoint. It intentionally remains staged and unused. `retained_transaction.py` authenticates six committed transaction witnesses and the continued absence of five restoration outputs, before/after the read, into a new external report. Its Passed means only a bounded read-only audit; `restorationPerformed=false`, `settingsRemainStaged=true`, original cell Failed. It cannot execute or repair R. It is not a replacement for Local's full historical custody map.

The backup and staged settings hashes remain respectively `2ff53cd79e303df0aadaf95aeb436938d55281246b63ade13464775b66504c26` and `21995344678c113d128439fd983f5a6634e183e31850655ffe6e8e2db9cc3ae6`. A restored historical file is a custody mismatch, not something to silently normalize. Any later physical recovery of R itself needs a separate preservation/recovery authorization; this cycle does not need it because S owns a new isolated project.

## New-cycle prerequisite and scope

`transport_preflight.py` observes all four expected owners once and records each independent result. TransportReady is point-in-time only. Unavailable transport, wrong source, failed retained audit or insufficient storage means prerequisites blocked and new batch NotRun. No blanket permission to repair credentials, switch origins, delete history, lower thresholds or select another disk is granted.

The existing storage-checked entry remains the authorized executor. It obtains its own fresh admission rather than consuming a previous pass. Retain `max(64 GiB, 2*B+20 GiB)` admission, 20 GiB operating floor, probes, five-second samples and publication-capacity check. No allocation reservation or future network/capacity guarantee is claimed.

S must freshly validate all 90 cells, six builds, 59 Players and 18/754/755 Editor cases. In particular collect P05 exact byte restoration/finalization, the full resource roster, graph-before-integration, live policy guards, restored-baseline zero roots/closure, strict R02 bridge/resource aggregate and codec/image-method/PDB checks. Earlier Q/P successes cannot fill S's missing evidence.

## Tests, limits and rollback

Tests use real Python authority/recovery functions and the real Completion constructor/cell scheduler, isolating external Unity execution and controlled Git faults. They cover outage after restoration, failed final authority, wrong local identity/backup/transaction, unbound source, malformed refs, no-state behavior, duplicate invocation, retained byte custody, all four preflight rows, redaction/clipping, timeout/spawn/nonzero/signal/decoding/receipt-write faults and pre-constructor observations. Full Completion, storage and strict-schema suites are run on Linux/macOS by the source-bound CI workflow.

This does not emulate actual Unity restoration, guarantee recovery under disk/power loss or corruption, or identify the lost R transport cause. Original `restore_bytes` and subprocess lifetime semantics are retained rather than advertised as new crash-atomic or process-group guarantees. Filesystem TOCTOU risks are bounded by existing exclusive project ownership, quiescence and hash checks, not eliminated. A restore command or evidence write may still fail; retain the partial state and return without retry.

Rollback is a reviewed Primary forward commit with a new assignment, never resetting history or altering old results. All stage/qualification/human-review flags stay false, PureInterpreter expansion stays disabled, and contaminated unisolated warm certificates remain Failed. This design is not the independent full-stage review.
