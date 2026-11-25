# R03 D5-B prospective dry-admission R5 — creation and response accounting

**Date:** 2026-11-25 America/Los_Angeles.  
**Role and status:** Primary Implementation design; focused source-only remediation. Independent R5 review and exact-source CI evidence are pending and are not supplied by this document.

## 1. Scope and inherited authority

The [R4 independent rereview](D5B_LOCAL_DRY_ADMISSION_R4_INDEPENDENT_REREVIEW_2026-11-25.md) returned `D5BDryAdmissionR4IndependentReview=ReturnRequired` for two additional output-accounting defects. **D5B-DRY-R4-IR-01** lost an observed completed seal when success-response printing failed, then falsely reported `outputCreated=false`. **D5B-DRY-R4-IR-02** left a consumed candidate after real directory creation but before `root_created=True` was recorded, then made the same false claim. R5 addresses those two boundaries in the [prospective writer and CLI](../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py).

The [R4 final-unlink and path-identity design](D5B_LOCAL_DRY_ADMISSION_R4_DESIGN_2026-11-25.md) remains the baseline. R5 adds explicit creation uncertainty and separates operation classification from response delivery. It does not claim an atomic transaction between filesystem changes, Python observations and the caller's eventual process result.

The production `APPROVED_EXECUTION_ENVELOPE_BLOB` remains `None`. The versioned [admission plan](../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json) and public [wrapper](../../../../../../../Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py) remain unchanged. The successful on-disk receipt schema and bytes also remain unchanged; R5 extends CLI failure diagnostics. The execute branch must still reject before reading a supplied envelope or invoking inspection. Synthetic approval fixtures are confined to source-host tests; they confer no Local authority.

## 2. Creation contract — distinguish an attempt from recorded creation

`seal_oneuse_dry_admission` records `creation_attempted=True` **before** calling descriptor-relative `os.mkdir`. It records `root_created=True` only after the call returns and that assignment executes. This closes the false-accounting gap without claiming ownership of a pathname observed after a fault.

The new `CreationFailure` carries the candidate path, the original reason, `attempted`, `preexisting`, `collision_reported` and any descriptor-close errors. It is separate from `PartialOutput`, which remains the path for creation recorded by this invocation. A pre-attempt candidate observation and a collision reported by the attempted call are different observations; neither authorizes adoption or deletion.

| Observation available to the handler | CLI classification | Creation and ownership fields | Required disposition |
|---|---|---|---|
| Failure before the creation attempt is armed, with no recorded pre-existing candidate | `NotAuthorized` | `outputCreated=false`, `creationOutcome=NotAttempted`, `candidateOwnership=NotAcquired` | `retryAllowed=false`; reconciliation is required if cleanup errors exist. |
| Candidate observed to exist before the creation attempt | `NotAuthorized` | `outputCreated=false`, `creationOutcome=PreexistingCandidate`, `candidateOwnership=NotAcquired` | `retryAllowed=false`, `requiresPhysicalReconciliation=true`; preserve the existing candidate. |
| Creation attempt armed, normal creation return not recorded | `IndeterminateOutputCreation` | `outputCreated=null`, `creationOutcome=UnknownAfterMkdirAttempt`, `candidateOwnership=Unproven` | `retryAllowed=false`, `requiresPhysicalReconciliation=true`. |
| Creation attempt armed and `FileExistsError` reported | `IndeterminateOutputCreation` | `outputCreated=null`, `creationOutcome=CollisionReported`, `candidateOwnership=Unproven` | Same no-retry and reconciliation requirements; the collision is not ownership evidence. |
| Creation recorded, followed by an operation or cleanup failure | Existing `PartialOutput` classification | `outputCreated=true`, `creationOutcome=Created` | Preserve the existing commit, path-identity, ledger and cleanup observations; prohibit retry. |

`outputCreated` is now tri-state in failure responses: **`true` means creation was observed; `false` means this invocation is known not to have created the candidate; `null` means the outcome is unresolved.** `false` does not assert that the pathname is absent. In particular, a pre-existing candidate can be reported with `false`, and an attempted creation with `null` may have left an empty directory before any receipt or incomplete marker could be written. Future consumers must compare exact booleans, fail closed on `null` or missing fields, and never coerce `null` to `false` through truthiness or a default value.

For `CreationFailure`, `commitVisible=false` and `commitOutcome=NotCommitted` describe this writer's lack of progression into its receipt-publication protocol. They say nothing about the contents or provenance of an unrelated pre-existing directory.

After an unresolved creation attempt, the implementation does not inspect, open, enumerate, adopt, remove or rewrite the candidate to infer ownership. It closes the already-held parent descriptor on a best-effort basis and carries any close error into the classified failure. No `FAILURE.json` is written into an unowned candidate. This is a conservative uncertainty contract, not an automatic recovery protocol. It also avoids treating every failed `mkdir` as evidence that this invocation created the directory.

## 3. Response contract — preserve classified state through delivery failure

`main` first builds the operation result and exit code. `_emit_cli_response` serializes, writes and flushes that result **outside** the operation `try`/handlers. A response failure can therefore no longer enter the precreation denial handler and overwrite a known or unresolved filesystem effect with `outputCreated=false`.

The emitter performs one stdout response attempt with explicit `flush=True`. It catches reporting failures, including catchable interruption exceptions. A write or flush may fail after partial or complete bytes have already reached stdout, so the emitter never retries stdout. It attempts one diagnostic response on stderr, also flushed, and returns exit 2. Failure of that stderr attempt is suppressed; response delivery does not trigger another candidate filesystem operation.

When the real writer returned a successful dry receipt and response delivery fails, `_completed_seal_failure` preserves these observations:

```json
{
  "result": "IndeterminateAfterCommit",
  "outputCreated": true,
  "creationOutcome": "Created",
  "commitVisible": true,
  "commitOutcome": "Visible",
  "finalUnlinkOutcomeUncertain": false,
  "writerReturnedSuccessfully": true,
  "retryAllowed": false,
  "requiresPhysicalReconciliation": true,
  "responseDelivery": "Failed"
}
```

The diagnostic also retains the candidate and includes `reportingError`. `Visible` records the writer's observed completed publication; it does not turn failed command reporting into successful command completion or guarantee that the pathname still has the same identity later.

When an already-classified failure cannot be delivered to stdout, the emitter copies its result, retaining creation uncertainty, commit uncertainty, candidate, path-identity observations, ledgers and cleanup errors. It adds response-delivery diagnostics and preserves no retry. Known-created or unknown-created output requires physical reconciliation. A failed read-only preview response remains `BlockedBeforeBuild` with `outputCreated=false`; a failed production null-approval denial remains a denial before creation.

A completely failed stdout/stderr path may leave no usable terminal JSON. A complete-looking success JSON may also have reached stdout before its flush failed. An external outcome process must therefore join terminal response and process outcome, and treat missing, partial or inconsistent delivery as unresolved. Neither missing output nor a parseable success fragment proves that no candidate was consumed or that the command succeeded.

## 4. Writer invocation and unrecorded return

The CLI records the inspected candidate and arms `writer_started=True` before calling the writer. Typed `CreationFailure` and `PartialOutput` observations take precedence. If an unexpected exception reaches the generic operation handler after invocation was armed, the handler must not assume that the writer had no filesystem effect.

If a successful receipt has already been assigned to the CLI's `result`, the handler preserves that observed return through `_completed_seal_failure`. If no successful receipt was recorded, it reports `IndeterminateWriterOutcome`, `outputCreated=null`, `creationOutcome=UnknownAfterWriterInvocation`, `candidateOwnership=Unproven`, `commitVisible=false` and `commitOutcome=UnknownAfterWriterInvocation`, with no retry and required physical reconciliation.

This conservative fallback includes a writer that completed physically but was interrupted before the caller recorded its return. Here `commitVisible=false` means no successful commit observation was retained by the CLI; it is not proof that the incomplete veto remains. The fallback also permits uncertainty when invocation was armed but the call had not yet entered the writer. It performs no candidate probe to strengthen that observation.

## 5. Preserved finalization and physical-evidence limits

R4's `final_unlink_attempted` flag remains armed before removal of `INCOMPLETE.json`. An unlink outcome that was not observed to return normally remains `IndeterminateAfterCommit` / `UnknownAfterFinalUnlink`, with created output, no retry and required reconciliation. The writer must not attempt a failure marker after the final unlink has been attempted. A later stream diagnostic does not authorize another output-root mutation.

The three final path-identity checks remain at their R4 boundaries: after parent close and before final rename; after final directory fsync and before veto unlink; and read-only after successful unlink. They remain point-in-time observations. They do not prevent concurrent relocation after the final observation, make the separate identity reads atomic, or substitute for a controlled evidence-parent namespace and independent custody checks.

The exact five-file structural verifier retains `SealedDryReceiptStructureOnly_NotLocalAuthorization`. Its positive result is compatible with a failed or unresolved command outcome. It proves neither successful response delivery nor user approval. An empty failure-path ledger means no inventory was recorded, not that the directory was empty.

Catchable source-host fault injection cannot establish behavior under arbitrary hard termination, power loss, APFS faults or real macOS syscall failures. Handlers cannot promise delivery after the process is killed. A later authorized acceptance process would have to reconcile command outcome, immutable authority and physical custody; this remediation neither implements nor authorizes that process.

## 6. Focused source-test, CI and review plan

The existing **81 test bodies and existing helpers must remain intact**. R5 adds tests **82–94**, bringing the source suite to **94**. This section describes their scope; execution evidence belongs in the forthcoming Primary report. Fresh exact-source CI evidence remains pending.

| Tests | Focused regression scope |
|---|---|
| **82–84** | Complete the real synthetic seal, then fail the first stdout write, stdout flush, or both reporting streams. Check preserved creation/commit diagnostics where stderr is available, exit 2, no stdout retry and the physical five-file structure. |
| **85–89, 93–94** | Cover errors and interruptions after real `mkdir`; a trace interruption after the unmodified call returns; a genuine pre-existing candidate; a raced collision; failure before the syscall has an effect; a trace interruption after the attempt is armed but before the call; and creation followed by relocation/replacement before recorded ownership. Check the appropriate known-no-creation or unknown-creation classification and preserve existing, relocated and replacement candidates without adoption, deletion or receipt writes. |
| **90** | Allow the real sealer to return, then interrupt before the CLI records that return. Require `IndeterminateWriterOutcome`, nullable creation state, no retry and reconciliation despite a structurally sealed directory. |
| **91** | Fail delivery of a known partial-output response at first write, flush or both streams. Preserve partial-output and failure-marker accounting where diagnostics can be delivered; retain the incomplete veto and reject the physical structure. |
| **92** | Fail delivery of the production null-approval denial at first write, flush or both streams. Retain the denial before envelope reads, inspection, writer invocation or directory creation, with `outputCreated=false` where a diagnostic is delivered. |

Primary must record comparison of the prior 81 tests and helpers with the R4 baseline and execution of the complete synthetic source-host suite. The [source-host workflow](../../../../../../../.github/workflows/r03-b2-d5b-local-admission-source-host.yml) must require an actual **94-test** count and a matching `sourceTests:94` receipt; a literal echoed count is not test evidence. Preserve the separate public execute check for exit 2, `NotAuthorized`, `outputCreated=false` and no envelope-path creation under the unchanged production gate.

Fresh CI evidence must identify the exact source commit, run attempt, job, raw individual test outcomes, actual total and denial-check result. Later documentation HEADs must remain distinguishable from the tested source SHA. Primary may then request a separate independent source/design/raw-CI rereview. This Primary design supplies neither an independent verdict nor a source-admission pass, and it does not alter the historical R4 `ReturnRequired` finding.

## 7. Hard stop

```text
APPROVED_EXECUTION_ENVELOPE_BLOB=None
APPROVED_LOCAL_HANDOFF_BLOB=None
WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION
D5BLocalExecution=NotAuthorized
D5LocalValidation=NotAuthorized
R03Accepted=false
H2Passed=false
ReadyForHumanReviewGate=false
```

All **18 real D5 Player cases remain `NoCoverage`**. Actual macOS Local admission, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain **`NotRun`** for this candidate. No Local preview/dry admission, D5-C/D, D6, H2, M08A, X02, SNAP-01 or Human Review Gate is authorized. The next work is limited to the focused Primary source regressions, exact-source CI evidence and separate independent rereview described above. This document is not a Local handoff.
