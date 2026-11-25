# R03 D5-B prospective dry-admission R4 — final-unlink ambiguity and path identity

**Date:** 2026-11-25 UTC. **Primary design; source-only implementation.** This is a narrowly scoped response to the [R3 independent `ReturnRequired`](D5B_LOCAL_DRY_ADMISSION_R3_INDEPENDENT_REREVIEW_2026-11-24.md) findings R3-IR-01 and R3-IR-02. It does not reopen Local execution, Unity, native VMs, D5-C/D, R03 acceptance, or later milestones.

## Contract A — distinguish physical structure from successful command outcome

R3's durably installed `INCOMPLETE.json` veto remains the precommit barrier; the staging file is written, fsynced, read back, atomically renamed and directory-fsynced *before* removing the veto. However an error or termination at the final unlink boundary can occur after the physical directory has already lost `INCOMPLETE.json`, even though the caller cannot prove successful completion. The process-local `committed` Boolean cannot settle this uncertain outcome.

R4 sets `final_unlink_attempted=True` **before** the final `os.unlink`. If the unlink call does not return normally, the writer must not claim a definite precommit failure; it raises `PartialOutput(commit_uncertain=True)` with `outputCreated=true`, `retryAllowed=false` and an explicit `IndeterminateAfterCommit` / `commitOutcome=UnknownAfterFinalUnlink` / `requiresPhysicalReconciliation=true` CLI result. `commitVisible` stays **false** unless the successful return of unlink was actually observed, avoiding a fabricated positive state. Because the veto may already have been removed, R4 does **not** attempt to write `FAILURE.json` after final unlink has been attempted. An error before that point still retains the incomplete marker and can attempt a separate failure receipt.

A **physically valid five-file structure** is *not* sufficient to establish successful command completion or user-authorized Local evidence. The structural verifier remains labeled `SealedDryReceiptStructureOnly_NotLocalAuthorization`; a later acceptance process must join independent successful command outcome, custody and authorization. It is impossible to make a process-local return value atomic with filesystem visibility across arbitrary crash boundaries; R4 explicitly classifies that boundary as indeterminate rather than promising physically impossible all-or-nothing proof.

## Contract B — approved physical output path must agree with the descriptor-bound directory

After parent descriptor close, directory-descriptor-relative writes can operate on a relocated inode. R4 adds `_assert_final_path_identity` to compare the canonical *approved parent path* against its recorded device/inode and the named output directory's nofollow device/inode against the still-open `root_fd` identity. It executes after parent close but before stage→final rename, again after final directory fsync and **before** veto unlink, and once more **read-only** after successful unlink.

If an identity mismatch is detected before the final unlink, retain the veto and raise `PartialOutput(path_identity_uncertain=True)`. If detected after the final unlink, raise `IndeterminateAfterCommit` (with `commitVisible=true` when unlink returned). In both cases the CLI requires physical reconciliation, disallows retry, and does not report a successful receipt at the approved pathname. The final postcommit identity check is **read-only**; the veto unlink remains the last visibility-changing filesystem operation.

These checks are *point-in-time*, not a namespace lock. A competing process that moves the directory after the final check cannot be excluded by Python pathname checks alone. Future Local approval would require a controlled evidence-parent ownership/namespace policy and independent physical custody checks; no adversarial cross-process atomicity is claimed here.

## Tests, invariants and stop

Existing R3 tests 1–76 remain; new isolated Python host regressions:
- `test_77` — real final unlink followed by synthetic reported error; positive physical structure but `commit_uncertain=True` and no secondary failure marker.
- `test_78` — the corresponding public CLI outputs `IndeterminateAfterCommit`, `UnknownAfterFinalUnlink`, `outputCreated=true`, `retryAllowed=false` and mandatory physical reconciliation.
- `test_79` — output root moved/replaced *after* successful parent close but before rename; not reported as success; relocated root retains veto.
- `test_80` — root moved/replaced immediately *after* successful final unlink; postcommit read-only path check detects it and raises indeterminate.
- `test_81` — public CLI reports the precommit path relocation with `outputPathIdentityUncertain=true` and `requiresPhysicalReconciliation=true`.

Source-only workflow requires **81** tests and its own matching `sourceTests:81` JSON receipt; the public execute without an immutable approval pin remains exit 2 / `NotAuthorized` with no output. No actual macOS, Unity, IL2CPP, Bee, Mach-O, PID, Player or real D5 case runs are involved.

**Hard stop:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; all 18 D5 real Player cases `NoCoverage`. Next only an *independent R4 source/design/raw-CI review*.
