# R03 D5-B R4 — independent design, exact-source, regression and raw-CI review

**Review date:** 2026-11-24 America/Los_Angeles (2026-11-25 UTC).  
**Role:** Independent source reviewer, separate from Primary Implementation and Local Validation.  
**Verdict:** **`D5BDryAdmissionR4IndependentReview=ReturnRequired`**.  
**Reviewed implementation:** `night-outlook/hybridclr_demo@55f3eaf5bb87f717d02e2ad81c9ea448397d71ab`.  
**Branch:** `codex/assembly-shadow-r01b-h1`.

## 1. Decision

R4 corrects the two specific counterexamples identified by the preceding R3 review. The final unlink now has an explicit uncertain-outcome state, and the writer rechecks the approved output pathname at the three documented finalization boundaries. The R4 design also correctly limits the meaning of physical receipt structure and explicitly acknowledges that pathname observations are not a cross-process namespace lock.

The complete prospective dry-admission source cannot receive `PassDryAdmissionSourceOnly`, however. Two additional, independently reproduced output-accounting defects remain:

| Finding | Severity and disposition | Actual behavior |
|---|---|---|
| **D5B-DRY-R4-IR-01** | **Medium; blocks source admission** | After the real writer completes a five-file seal, an error while printing the success response reaches the generic no-output handler. The command reports `NotAuthorized` / `outputCreated=false` despite a structurally sealed output. |
| **D5B-DRY-R4-IR-02** | **Medium; blocks source admission** | Directory creation can take effect before `root_created=True` is recorded. An exception at that boundary leaves an existing consumed candidate but reaches the same `outputCreated=false` response. |

These concern the **future approval-enabled source path**. The checked-in production approval constant remains `None` and public execution remains refused. They do not constitute observed Local incidents, real Player passes, or newly granted execution authority.

The genuine result of [GitHub Actions run 45532666894][CI] remains **PASS: 1/1 job and 81/81 source-host tests**. Passing that suite and returning this independent verdict are compatible: the two newly demonstrated boundaries are absent from the suite.

## 2. Scope, method and immutable provenance

The review started with `Docs/AssemblyShadow/README.md` and the [R4 independent review request][Request]. It then read the [R3 independent report][R3], [R4 design][Design], [Primary R4 record][Primary], actual pinned implementation, wrapper, plan, imported source-preflight verifier, test bodies, workflow, remote run/job metadata and raw job output.

Repository and Actions access used the GitHub Connector. Source-host checks used separate reviewer-owned scratch snapshots and temporary fixtures. The downloaded source bytes were verified against Git blob IDs before execution. No implementation, checked-in tests, approval constant, protected historical evidence, Local handoff, or sibling-repository content was changed.

### 2.1 Four-repository tuple

| Repository | Exact source tuple | Observed feature HEAD before review publication |
|---|---|---|
| `night-outlook/hybridclr_demo` | `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab` | `ff8526815f0e756c34f53cb34904890e621eea6d` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Same |

All four named branches resolved through the Connector. The sibling repository refs were checked to establish the unchanged tuple; this review does not claim a new full native implementation audit.

The independently fetched [R3-review-head → R4-code comparison][SourceCompare] contains exactly **two commits and three modified files**:

1. `47b157a5de3cd23e6fd8f604ae776f592ab931f3` — writer changes and tests 77–80.
2. `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab` — test 81 and the corrected 81-test workflow receipt.

Only the D5Local writer, D5Local test suite and its source-host workflow changed. There are no native, package, C10, old B1/D5, or historical-evidence modifications in that comparison.

The [reviewed-code → bootstrap-HEAD comparison][DocsCompare] contains two later, documentation-only commits, `f04287f83479b46d3e030e65fca2fce1a943dd8a` and `ff8526815f0e756c34f53cb34904890e621eea6d`, changing six paths under `Docs/AssemblyShadow`. Neither is the Actions run's tested source SHA.

### 2.2 Verified Git blobs

Paths in this table are relative to `night-outlook/hybridclr_demo`.

| File | Exact verified Git blob |
|---|---|
| [D5Local writer][Writer] | `654ced61b75d1d5fca448fce756b9c9bb9ca0799` |
| [D5Local regression suite][Tests] | `df66cce2fc321fe5deaaa370c138c8c9727e5f7a` |
| [Source-host workflow][Workflow] | `a8362ab889c29fa7befc0b56e03abe3ad53af3d7` |
| [Unchanged versioned admission plan][Plan] | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| [Unchanged public wrapper][Wrapper] | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| [Imported RR5 source-preflight verifier][Preflight] | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| R3 baseline writer at `ee283580c372c45fb67dc85bfa51a7d34251449e` | `3cf4e746bc1cd361d162ab4681af3d6d0281ae37` |
| R3 baseline test suite at that same baseline | `0698cff62f1e8a0437c8f2e808dfa504b36106da` |
| [R4 design][Design], at documentation HEAD `ff852681…` | `03b1772876774680bf2705e6871a7a7fa50b1914` |
| [R4 review request][Request], at that documentation HEAD | `d21cfb9161a3378fc0e16b4a46d54ccf68ceb2c7` |
| [Primary R4 record][Primary], at that documentation HEAD | `5666c6bef2545aa1fd9d6f1a10f38146d7bbf3bf` |
| [Prior independent R3 report][R3] | `cf9ac401518761b689aa5d790a48c937cc7d8f06` |
| [Closed WEB_TO_LOCAL snapshot][Handoff] | `b1e15a42a15f2dacde6cd9dd129a1940872c32ad` |

## 3. Per-finding adjudication of R3

### 3.1 R3-IR-01 — closed for the specified final-unlink ambiguity

[Writer lines 713–714 and 811–870][Finalization] initialize and maintain separate `committed` and `final_unlink_attempted` states. The latter becomes true **before** `os.unlink("INCOMPLETE.json", dir_fd=root_fd)`. `committed=True` is recorded only after normal return.

A catchable exception in the unlink call therefore raises `PartialOutput` with `commit_uncertain=True`. After an unlink attempt, the error path does not attempt `FAILURE.json`. [The CLI mapping][CLI] produces:

```json
{
  "result": "IndeterminateAfterCommit",
  "commitVisible": false,
  "commitOutcome": "UnknownAfterFinalUnlink",
  "finalUnlinkOutcomeUncertain": true,
  "outputCreated": true,
  "retryAllowed": false,
  "requiresPhysicalReconciliation": true
}
```

This is an appropriate conservative result whether the unlink actually happened or not. A false `commitVisible` here means normal return was not observed; it is not proof that the veto remains.

[Tests 77–78][UnlinkTests] genuinely call the saved real unlink **before** raising their synthetic error. Test 77 also counts attempted failure-marker writes and requires zero attempts. It checks that the veto and failure marker are absent while the physical five-file structural verifier succeeds. Test 78 checks the public CLI's exit 2, uncertainty fields, created output, no-retry policy and reconciliation requirement.

Independent additional fixtures established:

| Additional case | Observed outcome |
|---|---|
| Error before real unlink | Uncertain final-unlink outcome; veto remains; structure rejected. |
| Real unlink followed by `KeyboardInterrupt` | `PartialOutput` with unknown commit outcome; no veto/failure marker; structure-only positive. |
| Real unlink followed by `SystemExit` | Same conservative uncertain outcome. |

The design's revised distinction between **physical structure** and **successful command completion** is essential to this closure. It no longer promises that every unsuccessful command must leave an unsealed physical directory. The new R4 findings below concern false accounting elsewhere; they do not negate the specific unlink correction.

### 3.2 R3-IR-02 — closed within the stated point-in-time path contract

[`_assert_final_path_identity`, lines 565–591][PathHelper], checks:

- The approved parent is an exact canonical directory.
- The parent's device/inode matches the recorded parent identity.
- The named child is a directory under no-follow stat.
- The named child's device/inode matches the still-open root descriptor.

The helper translates `Rejected`, `OSError` and `RuntimeError` into `PathIdentityMismatch`. The three calls are correctly located after parent close and before final rename (line 805), after final directory fsync and before unlink (809), and read-only after successful unlink (819).

A precommit mismatch retains the veto and reports `NotCommitted` plus path uncertainty. A postcommit mismatch preserves observed commitment and reports `IndeterminateAfterCommit` / `Visible`. Both require physical reconciliation and prohibit retry through [lines 911–939][CLI].

[Tests 79–81][PathTests] actually move and replace the output directory after successful parent close or final unlink. They check the displaced directory, the replacement at the approved pathname, and the appropriate exception or CLI fields. The review reran them as part of the complete exact-source 81-test suite; the separate path reviewer also ran the three assigned cases.

Seventeen additional reviewer checks passed their expected assertions. They covered an unchanged path; absent/replaced parent; the original bound child beneath a replacement parent; parent, ancestor and child symlinks; absent/non-directory child; parent-stat, child-stat, fstat and canonical-resolution failures; relocation at the second pre-unlink guard; descriptor-bound failure cleanup; and postcommit CLI classification. In particular, the **same child inode beneath a different parent inode is rejected**—the parent identity check is materially necessary.

**Explicitly retained limitation:** a seventeenth check moved the root during its successful final close, after the last identity observation. The function returned success while the approved pathname was empty and the valid structure was at the relocated path. That is a counterexample to a stronger “path still matches when return occurs” guarantee. It is **not a new blocker against R4**, because [Contract B][Design] expressly acknowledges moves after the final check and requires a future controlled namespace/custody policy. The separate canonical/stat/fstat reads are also not an atomic snapshot. This review grants no stronger guarantee.

## 4. New blocking findings

### D5B-DRY-R4-IR-01 — success-response output failure falsely reports no created output

**Severity:** Medium. **Disposition:** ReturnRequired.  
**Source:** [writer lines 901, 909–910 and 940–951][CLI].

The sealer returns a completed receipt at line 901. The subsequent `print(json.dumps(result, ...))` remains inside the generic `try`. If response output raises `OSError` or `ValueError`, the generic handler emits `outputCreated=false` and `result=NotAuthorized`, with no candidate, commit state, no-retry flag or reconciliation requirement.

The writer's known completed-output state is lost at the CLI reporting boundary.

#### Independently reproduced state

Using the exact writer and the repository's synthetic fixture, the reviewer allowed the entire seal to run normally. A reviewer-owned stdout stream raised `OSError(5)` on its first write and accepted the following diagnostic write. No writer function was replaced.

Observed command result:

```json
{
  "exitCode": 2,
  "result": "NotAuthorized",
  "outputCreated": false
}
```

Observed physical state was exactly:

```text
ADMISSION.json
CELLS.json
LOCAL_BATCH_RESULT.json
MANIFEST.json
POSTFLIGHT.json
```

The real `inspect_dry_receipt_structure` returned `SealedDryReceiptStructureOnly_NotLocalAuthorization`, `filesChecked=5`, zero Player passes, 18 Player cases without coverage, and `R03Accepted=false`.

The problem is **not** that a physical receipt survives failed command reporting; the R4 design already permits that and requires reconciliation. The defect is the explicit, false claim that no output was created after sealing was observed to complete.

A persistently failed stream may prevent any JSON from being delivered. The reproduced case specifically demonstrates a first-write failure followed by successful diagnostic output. It does not claim that every broken pipe yields the misleading JSON.

#### Reproduction boundary

The fixture reused `D5BLocalSourceOnly.setUp()`, `_synthetic_approved_bytes()` and `fake_admission()` from the pinned test suite. It temporarily mocked only the envelope constant, `inspect` and stdout, then invoked the real `gate.main(["--mode", "execute", "--approved-envelope", ...])`. The stdout fault was equivalent to:

```python
class FailFirstWrite(io.StringIO):
    failed = False

    def write(self, value):
        if not self.failed:
            self.failed = True
            raise OSError(5, "reviewer synthetic first stdout write failure")
        return super().write(value)
```

The temporary fixture was cleaned up and the production approval constant was `None` again after the mock context.

#### Required correction and regression

Preserve output creation and observed commit state through response emission. A failure while reporting a completed seal must not enter the same no-output state used for denial before creation. When diagnostics can be emitted, report truthful consumed-output state, no retry and required physical reconciliation. If output delivery itself is unavailable, the external command-outcome process must treat the missing terminal response as unresolved; it must not infer absence from missing output.

Add a regression that completes the real synthetic seal, fails the first success-response write, permits subsequent diagnostic output and compares the CLI fields with the structural verifier. Cover the reporting boundary without weakening the null-approval denial.

### D5B-DRY-R4-IR-02 — directory-creation interruption is misclassified as no output

**Severity:** Medium. **Disposition:** ReturnRequired.  
**Source:** [writer lines 712, 725–727, 820–821 and 861–871][Creation], followed by [CLI lines 940–951][CLI].

`root_created` is false until the statement after `os.mkdir`. If creation takes effect and an exception is observed before the assignment, the root-created-aware error branch is skipped. The writer raises ordinary `Rejected` and the CLI reports `outputCreated=false`.

#### Independently reproduced state

Two initial fixtures performed real directory creation, then injected respectively `OSError` and `KeyboardInterrupt` before returning control to the assignment.

A stronger third fixture **left `os.mkdir` unmodified**. A reviewer-owned `sys.settrace` line hook raised `KeyboardInterrupt` on entry to line 726, after the real call at line 725 had returned and before `root_created=True` executed. The hook recorded:

```json
{
  "candidateAlreadyExists": true,
  "line": 726,
  "mkdirUnmodified": true,
  "rootCreatedFlagBeforeAssignment": false
}
```

All three cases produced an existing empty candidate, CLI exit 2 and `NotAuthorized` / `outputCreated=false`. `retryAllowed` and `requiresPhysicalReconciliation` were absent. In the trace case, tracing was restored and `os.mkdir` remained unchanged afterward.

The essential trace boundary, with the existing synthetic fixture and process-local approval/inspection mocks, was:

```python
writer_code = gate.seal_oneuse_dry_admission.__code__

def interrupt_after_mkdir(frame, event, arg):
    if event == "line" and frame.f_code is writer_code and frame.f_lineno == 726:
        assert frame.f_locals["root_created"] is False
        assert root.is_dir()
        raise KeyboardInterrupt("after real mkdir, before recorded creation")
    return interrupt_after_mkdir
```

The candidate is consumed despite the lack of receipt files: the existing-output check will reject a later attempt using the same name. This is a false state report, not an accepted physical receipt.

The OSError fixture does not prove that macOS `mkdir` returns an errno after success. The trace fixture removes that syscall assumption: it demonstrates the Python control-flow gap following a successful, unmodified creation call. It is still deterministic synthetic interruption, not evidence of a naturally occurring macOS signal incident.

#### Required correction and regression

Represent creation-attempt/creation-outcome uncertainty, or reconcile it through the descriptor-bound parent before asserting that no output exists. Any unresolved candidate consumption must prohibit retry and require physical reconciliation. Do not simply treat every failed `mkdir` as proof of ownership: a pre-existing-directory collision must remain distinguishable, and an unrelated directory must not be removed or adopted.

Add focused tests for an interruption after real creation and for a genuine pre-existing candidate. The no-output response must be reserved for states in which it is justified.

## 5. Preserved contracts and regression assessment

### 5.1 Existing tests remain intact

An AST comparison between the exact R3 baseline and exact R4 source found:

- **76 prior test methods, unchanged.**
- All pre-existing test-class helper methods unchanged.
- Exactly five added methods: tests 77–81.

The writer comparison found only three changed existing top-level definitions: `PartialOutput`, `seal_oneuse_dry_admission` and `main`. It added `PathIdentityMismatch` and `_assert_final_path_identity`; 29 other existing top-level definitions were unchanged. This supports preservation of the old code paths; it is not proof that every possible interaction is covered.

The reviewer independently ran the exact downloaded suite on **Linux x86_64, Python 3.12.14**:

```text
Ran 81 tests in 0.096s
OK
```

This reviewer-host rerun is separate from the raw Ubuntu/Python 3.11 Actions evidence. Both use synthetic source-host fixtures and are not Local Validation.

### 5.2 Exact five-file verifier

The unchanged [structural verifier, lines 622–673][Structure] requires exactly the five named files, manifest kind `R03D5BDryAdmissionLedgerV3`, four distinct manifest members excluding the manifest itself, exact per-file SHA-256 and byte count, and final receipt fields that retain `NotRun`, zero Player passes, 18 cases without coverage and false R03 acceptance.

The manifest's own SHA-256 is returned as an observation; it is not an external approval signature. The verifier does not authenticate user approval or successful process completion.

The retained tests reject incomplete and failure markers and a missing final receipt. Seven additional reviewer-owned structural mutations were all rejected:

| Mutation | Observed rejection |
|---|---|
| V2 instead of V3 ledger kind | Wrong seal schema |
| Wrong member SHA-256 | Hash/size/identity mismatch |
| Wrong member byte count | Hash/size/identity mismatch |
| Duplicate manifest member | Duplicate or missing entry |
| Unexpected JSON file | Extra/unsealed output |
| Residual staging file | Extra/unsealed output |
| Symlinked receipt member | Unexpected output entry |

These results independently check the contract rather than relying on the Primary summary.

### 5.3 Approval, source and physical reinspection

The inner writer still authenticates **raw immutable envelope bytes** through `approved_envelope(approved_raw)` at line 697. It reconstructs a request and calls the real inspection path before output creation and repeatedly during finalization. `_same_admission` compares source, live-remote, original-S, historical-root and physical identity facts, plus the stable host/Unity fields.

The [imported preflight][Preflight] still checks the defined 16 native/overlay source files, 14 separately pinned evidence-producer files and five historical comparator blobs. [The enclosing inspection][Inspection] joins the independently reviewed source-preflight result, four exact live remote refs, the original-S source identity, six historical roots and host observations. No such real Mac/source/SDK inspection is claimed to have run in the reviewer fixtures; those fixtures replace inspection with the existing synthetic observation.

The public wrapper and plan are unchanged. `APPROVED_EXECUTION_ENVELOPE_BLOB=None` remains in production source, and the execute branch rejects before reading the supplied envelope or invoking inspection. The test-only approval mocks are process-local and restored. No actual Unity build, native compilation, Player launch or later milestone path was added.

## 6. Raw GitHub Actions audit

The independently fetched [run 45532666894][CI] is a `push` run, **attempt 1**, of the exact reviewed workflow. Run and job both report:

| Field | Verified value |
|---|---|
| Run head SHA | `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab` |
| Branch | `codex/assembly-shadow-r01b-h1` |
| Status / conclusion | `completed / success` |
| Attempt-specific job count | **1** |
| Job | [`138931561379`, `future-admission-source-host`][Job] |
| Job head SHA / attempt | Exact source above / **1** |
| Returned step outcomes | **8/8 completed/success** |
| Runner | Ubuntu 24.04.5 x86_64 |
| Python | CPython 3.11.18 |

The checkout's raw `git log -1 --format=%H` output also equals the reviewed source SHA.

The decoded raw job output contains **81 individually successful test lines**, continuously numbered 01–81. In particular:

| Test | Actual raw outcome |
|---|---|
| `test_77_after_effect_veto_unlink_error_requires_reconciliation` | `ok` |
| `test_78_cli_after_effect_unlink_error_never_claims_precommit` | `ok` |
| `test_79_root_relocated_after_parent_close_is_not_success` | `ok` |
| `test_80_root_relocated_after_final_unlink_is_indeterminate` | `ok` |
| `test_81_cli_relocated_parent_closed_root_requires_reconciliation` | `ok` |

Actual runner output, distinguished from echoed shell commands:

```text
2026-11-25T02:24:21.2825128Z Ran 81 tests in 0.139s
2026-11-25T02:24:21.2825442Z OK
```

The separate execute-refusal step emitted the following actual result:

```json
{
  "D5BLocalExecution": "NotAuthorized",
  "R03Accepted": false,
  "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
  "kind": "R03D5BLocalAdmissionFailureV1",
  "outputCreated": false,
  "reason": "D5-B Local execution is not authorized",
  "result": "NotAuthorized",
  "schemaVersion": 1
}
```

The workflow captures the process exit code and successfully executes `test "$code" -eq 2` with `set -e` active. The raw log does not separately print a numeric exit-code line; successful execution of this assertion is the evidence for exit 2. It also checks that the unapproved-envelope path does not exist.

The final emitted receipt has `sourceTests:81`, `approvedEnvelope:false`, `localExecution:false`, `unityOrPlayer:false` and `R03Accepted:false`. That receipt is a literal workflow echo; the independent raw unittest count and individual test lines substantiate its count. The run has zero downloadable artifacts, so the audited evidence is run/job metadata and raw logs.

### Historically separate evidence

[Earlier run 45532556269][EarlierCI], at `47b157a5de3cd23e6fd8f604ae776f592ab931f3`, passed **80** tests but emitted an obsolete `sourceTests:76` summary. It has no test 81. It is not substituted for the final R4 evidence, and its stale summary is not silently relabeled.

The earlier R3 76-test PASS and its independent `ReturnRequired` remain historical records. This review does not rewrite them. Later documentation commits are also not presented as CI-tested source.

## 7. Limits, closure requirements and hard stop

### 7.1 Crash and observation limits

A process-local flag and a filesystem visibility change cannot make the caller's eventual return value atomic across arbitrary process termination. A hard-killed process cannot be expected to run a Python handler or deliver a terminal JSON response. Likewise, a final path check cannot prevent a different process from moving the directory after the observation.

The explicit R4 limits are accepted: physical structure alone is not successful command evidence, and point-in-time identity is not namespace locking. No APFS fault behavior, hard-kill recovery, power-loss durability, real macOS syscall result or external custody protocol was validated here.

The new findings are narrower and actionable: when the running program **does catch a fault and emits a result**, it must not falsely state that no output exists. A future acceptance process must join successful command outcome, authorization and physical custody; a structure-only receipt cannot supply those missing facts.

A diagnostic limitation remains: uncertain-unlink and postcommit error paths can expose an empty `observedLedger` because the ledger collection is in the pre-unlink failure branch. This is not an independently blocking finding, but an empty ledger there means no recorded inventory, not proof that the directory is empty.

### 7.2 Requirements for a future source-only pass

Primary Implementation would need to correct the two output-accounting boundaries, add focused regressions, retain the existing 81 test bodies and null-approval denial, obtain fresh exact-source CI, and request a separate independent rereview. Any new design must preserve the distinction between known creation, uncertain creation, known commit visibility, missing command completion and uncertain pathname identity.

These are remediation requirements for a future review. This reviewer did not implement them or open a new execution phase.

### 7.3 Final verdict and authority

**`D5BDryAdmissionR4IndependentReview=ReturnRequired`.**

R3-IR-01 and R3-IR-02 are closed only for their stated R4 source/design counterexamples and documented limits. The new R4-IR-01 and R4-IR-02 prevent overall dry-admission source approval.

The execution state remains:

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

All **18 real D5 Player cases remain NoCoverage**. Actual macOS Local admission, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain **NotRun** for this reviewed candidate. No Local preview/dry admission, D5-C/D, D6, H2, M08A, X02, SNAP-01 or Human Review Gate is authorized.

Publication consists only of this independent report and a README link/status entry under `Docs/AssemblyShadow`. Stop after publication.

[Writer]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py
[Tests]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py
[Workflow]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
[Plan]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json
[Wrapper]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py
[Preflight]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py
[Design]: https://github.com/night-outlook/hybridclr_demo/blob/ff8526815f0e756c34f53cb34904890e621eea6d/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R4_DESIGN_2026-11-25.md
[Request]: https://github.com/night-outlook/hybridclr_demo/blob/ff8526815f0e756c34f53cb34904890e621eea6d/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R4_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md
[Primary]: https://github.com/night-outlook/hybridclr_demo/blob/ff8526815f0e756c34f53cb34904890e621eea6d/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R4_PRIMARY_2026-11-25.md
[R3]: https://github.com/night-outlook/hybridclr_demo/blob/ff8526815f0e756c34f53cb34904890e621eea6d/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R3_INDEPENDENT_REREVIEW_2026-11-24.md
[Handoff]: https://github.com/night-outlook/hybridclr_demo/blob/ff8526815f0e756c34f53cb34904890e621eea6d/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md
[SourceCompare]: https://github.com/night-outlook/hybridclr_demo/compare/ee283580c372c45fb67dc85bfa51a7d34251449e...55f3eaf5bb87f717d02e2ad81c9ea448397d71ab
[DocsCompare]: https://github.com/night-outlook/hybridclr_demo/compare/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab...ff8526815f0e756c34f53cb34904890e621eea6d
[Finalization]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L711-L870
[CLI]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L876-L951
[Creation]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L711-L871
[PathHelper]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L565-L591
[UnlinkTests]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py#L1093-L1145
[PathTests]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py#L1147-L1231
[Structure]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L622-L673
[Inspection]: https://github.com/night-outlook/hybridclr_demo/blob/55f3eaf5bb87f717d02e2ad81c9ea448397d71ab/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L334-L431
[CI]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45532666894
[Job]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45532666894/job/138931561379
[EarlierCI]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45532556269
