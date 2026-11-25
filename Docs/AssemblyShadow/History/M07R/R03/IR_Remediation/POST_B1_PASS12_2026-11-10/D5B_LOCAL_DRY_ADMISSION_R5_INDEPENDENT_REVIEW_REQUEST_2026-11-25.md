# R03 D5-B R5 — separate independent source review request

**Date:** 2026-11-25 America/Los_Angeles.
**Request owner:** Primary Implementation.
**Requested independent verdict:** `PassDryAdmissionSourceOnly` or `ReturnRequired`.
**Current verdict:** `D5BDryAdmissionR5IndependentReview=Pending`.

## 1. Role and exact scope

Act as an independent source reviewer, separate from Primary Implementation and Local Validation. Review R5's corrections for **D5B-DRY-R4-IR-01** and **D5B-DRY-R4-IR-02**, including additional counterexamples. Read actual source and raw CI; do not adopt the Primary assessment as your verdict.

This request authorizes a source/design/test/raw-evidence review and publication of its report under `Docs/AssemblyShadow`. It is not permission to modify implementation, enable approval constants, issue an executable Local handoff, run real Mac/Unity/IL2CPP/Player validation, approve a Human Review Gate, or begin a later milestone.

## 2. Read order

1. `Docs/AssemblyShadow/README.md`.
2. This request.
3. [Independent R4 ReturnRequired report](D5B_LOCAL_DRY_ADMISSION_R4_INDEPENDENT_REREVIEW_2026-11-25.md).
4. [R5 design and focused plan](D5B_LOCAL_DRY_ADMISSION_R5_DESIGN_2026-11-25.md), retaining the [R4 finalization limits](D5B_LOCAL_DRY_ADMISSION_R4_DESIGN_2026-11-25.md).
5. [Primary R5 source/CI record](D5B_LOCAL_DRY_ADMISSION_R5_PRIMARY_2026-11-25.md) and [machine evidence](D5B_LOCAL_DRY_ADMISSION_R5_EVIDENCE_2026-11-25.json).
6. Exact implementation, regression suite, plan, wrapper and workflow below, followed by actual run/job metadata and raw log.
7. `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, which remains CLOSED.

## 3. Exact source tuple

Every repository uses `codex/assembly-shadow-r01b-h1`.

| Repository | Reviewed source commit |
|---|---|
| night-outlook/hybridclr_demo | **`eaca19c08f41245c46dfacbf605cd80480bc3a92`** |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

Later documentation HEADs carry this request and evidence; they are not the Actions-tested code SHA. Independently verify that distinction and the unchanged sibling tuple. The bootstrap-to-code comparison is [83ceb2ba… → eaca19c0…](https://github.com/night-outlook/hybridclr_demo/compare/83ceb2ba9868d96bd35628908919978e16cc5d2f...eaca19c08f41245c46dfacbf605cd80480bc3a92).

At the exact demo source, read:

- [Writer/CLI](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py): especially `CreationFailure`, `seal_oneuse_dry_admission`, `_failure_record`, `_completed_seal_failure`, `_emit_cli_response` and `main`.
- [Tests](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py): all 81 prior tests and 13 additions numbered 82–94.
- [Source-host workflow](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/.github/workflows/r03-b2-d5b-local-admission-source-host.yml).
- [Unchanged plan](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json), [public wrapper](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py) and [imported source preflight](https://github.com/night-outlook/hybridclr_demo/blob/eaca19c08f41245c46dfacbf605cd80480bc3a92/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py).

## 4. Required questions

1. Does response failure preserve a completed seal's known creation and commit state, including failure after bytes have reached stdout? Are stderr failure and the absence of terminal JSON handled without asserting no output?
2. Is creation-attempt uncertainty armed before real mkdir, including an unmodified-mkdir line-trace interruption before recorded creation? Do pre-existing and racing candidates remain distinct and untouched?
3. Does the uncertainty path avoid recovering ownership through the candidate pathname, opening or writing an unrelated directory, or silently allowing a retry?
4. Does the writer-return fallback remain conservative when the real sealer completed but its return was not recorded? Does `outputCreated=null` remain distinguishable from exact `false`?
5. Are the existing 81 test methods and seven helper bodies unchanged? Do tests 82–94 exercise the real writer's relevant effects rather than merely mocking a successful writer result?
6. Are prior R3/R4 final-unlink, pathname-identity and structure-only limits preserved? Is any newly caught result falsely conclusive?
7. Is the production approval constant still `None`, with execute denied before envelope reads, inspection or output creation?
8. Does raw CI substantiate the exact source and actual 94-test roster, rather than only a literal emitted summary?

Additional isolated reviewer counterexamples are welcome within this source-host scope. Do not infer real macOS syscall, crash, power-loss or namespace-lock guarantees from synthetic tests.

## 5. Raw evidence to inspect

- [Actions run **45609355991**, attempt 1](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609355991).
- [Job **139188536483**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609355991/job/139188536483).
- [Preserved decoded raw log](D5B_LOCAL_DRY_ADMISSION_R5_CI_JOB_139188536483_2026-11-25.log), SHA-256 `fea6866d830090d7717cd221b1a738f336e61454fe1600d6494df18ace1e97c9`.

The focused job reports 94/94, 1/1 job success. The four other cancelled workflow runs listed in the Primary report are not passing evidence; the unrelated B1 success was inspected only at run-metadata level. Earlier R4's 81-test success and ReturnRequired are separate historical observations.

An optional isolated reviewer-host command for the downloaded exact source is:

```text
python -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py -v
```

That command is a synthetic source-host regression suite. It is not an instruction to invoke the actual Local CLI or a Unity/SDK/Player workflow.

## 6. Publication and stop

Publish a complete independent report under this `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10` directory and add the current report/status link to the documentation entry point. Record the exact reviewed source, raw evidence, per-finding adjudication, additional findings and limits. Assign either:

```text
D5BDryAdmissionR5IndependentReview=PassDryAdmissionSourceOnly
```

or:

```text
D5BDryAdmissionR5IndependentReview=ReturnRequired
```

Stop after publication. Preserve:

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

All 18 real D5 Player cases remain NoCoverage; actual Mac/Unity/IL2CPP/Bee/full native VM/Mach-O/GC/PID/Player work remains NotRun. A source-only independent pass, if earned, is not Local execution approval or R03 acceptance.

