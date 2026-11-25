# R03 D5-B — Primary R5 creation and response accounting correction

**Date:** 2026-11-25 America/Los_Angeles.
**Primary state:** `D5BDryAdmissionR5Primary=SourceOnlyCIComplete_PendingIndependentR5Review`.
**Independent state:** `D5BDryAdmissionR5IndependentReview=Pending`; the historical R4 `ReturnRequired` is not self-cleared.
**Local state:** `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.

## 1. Outcome and scope

Primary implemented the focused corrections requested by [independent R4 review](D5B_LOCAL_DRY_ADMISSION_R4_INDEPENDENT_REREVIEW_2026-11-25.md), under the [R5 design and verification plan](D5B_LOCAL_DRY_ADMISSION_R5_DESIGN_2026-11-25.md). The exact committed candidate passed **94/94 Python source-host tests** in the focused GitHub Actions job. A [separate independent R5 review](D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md) is the next gate.

| R4 finding | Primary correction | Direct regression evidence |
|---|---|---|
| R4-IR-01: a failed success response reports no created output after a complete seal | Response serialization, write and explicit flush occur outside operation error classification. A completed seal retains `outputCreated=true`, observed visible commit and required reconciliation. Failure diagnostics use stderr once; stdout is not retried. | 82–84 exercise real seals followed by write, flush and both-stream failures. 91–92 preserve partial-output and null-approval denial accounting when reporting fails. |
| R4-IR-02: real mkdir takes effect before `root_created` is recorded | A monotonic attempt flag is armed before mkdir. `CreationFailure` distinguishes unattempted/pre-existing cases from unrecorded attempted creation or a reported collision. Unresolved creation reports `outputCreated=null`, no retry and required reconciliation. It does not open, adopt, remove or write into an unowned candidate. | 85–89 and 93–94 cover after-effect errors, interruption after an unmodified mkdir, pre-existing/racing candidates, pre-effect errors, interruption before the syscall, and relocation/replacement. |
| Adjacent caller-return boundary | The CLI arms writer invocation before calling it. If an unexpected fault arrives before its return is recorded, it reports `IndeterminateWriterOutcome` and unknown output/commit outcome instead of a no-output denial. | 90 completes the real sealer before injecting OSError, RuntimeError or KeyboardInterrupt at the wrapper return boundary. |

The successful on-disk receipt bytes, final-unlink protocol, three final pathname observations, structural verifier, approval pin, versioned plan and public wrapper remain unchanged. Failure diagnostics now have tri-state creation semantics: **false means this invocation did not create the candidate, not that the pathname is absent; null means unresolved.** Future consumers must use exact-boolean checks and reject missing or unknown outcomes.

## 2. Exact repository and source provenance

All four repositories were identified through the GitHub Connector with `pull=true` and `push=true`. The working branch in each is `codex/assembly-shadow-r01b-h1`. Connector Git-data writes and remote readback are the authoritative transport.

| Repository | Bootstrap remote HEAD | Exact R5 source tuple |
|---|---|---|
| [night-outlook/hybridclr_demo](https://github.com/night-outlook/hybridclr_demo) | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | **`eaca19c08f41245c46dfacbf605cd80480bc3a92`** |
| [night-outlook/hybridclr](https://github.com/night-outlook/hybridclr) | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Same, unchanged |
| [night-outlook/hybridclr_unity](https://github.com/night-outlook/hybridclr_unity) | `948c0e3b4f8891481301770115e8ba4945eea6de` | Same, unchanged |
| [night-outlook/il2cpp_plus](https://github.com/night-outlook/il2cpp_plus) | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Same, unchanged |

The [bootstrap → tested-source comparison](https://github.com/night-outlook/hybridclr_demo/compare/83ceb2ba9868d96bd35628908919978e16cc5d2f...eaca19c08f41245c46dfacbf605cd80480bc3a92) contains **one commit and exactly four paths**:

| Path | Exact Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `8c83ab812c64caf0bf7d14bca52b889add784036` |
| This cycle's `D5B_LOCAL_DRY_ADMISSION_R5_DESIGN_2026-11-25.md` | `ac6ffc51fb32b1db2a48061e8368d269826aeab9` |

Every prepared file was fetched back at the exact new commit and matched both its Git blob and complete UTF-8 bytes. The unchanged plan blob is `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9`; wrapper `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39`; imported source-preflight verifier `81e7c3a2eaccb77bff2515c91b173558e4eeba2f`.

Source analysis used isolated Connector-sourced snapshots at `/workspace/scratch/a6fad0908883/r5_source` and exact baseline bytes at `/workspace/scratch/a6fad0908883/r5_baseline`. These are not authoritative Git handoffs or claimed Local Validation checkouts. Actual Local checkout paths, installed SDKs and Unity were not inspected or invoked.

Later report/index publication commits are documentation commits. They must not be substituted for the tested source SHA above.

## 3. Focused raw GitHub Actions evidence

[Run **45609355991**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609355991), [job **139188536483**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609355991/job/139188536483), attempt **1**, event **push**, exact head **`eaca19c08f41245c46dfacbf605cd80480bc3a92`**:

| Observation | Verified result |
|---|---|
| Workflow | `r03-b2-d5b-local-admission-source-host.yml` |
| Run/job conclusion | `completed / success`; **1/1 job** |
| Returned job steps | **8/8 completed/success** |
| Runner / interpreter | Ubuntu 24.04.5 x86_64; CPython 3.11.18 |
| Raw test roster | **94 distinct test lines, IDs 01–94**; all new 82–94 are individually `ok` |
| Actual unittest footer | `Ran 94 tests in 0.191s`, then `OK` |
| Public execute refusal | `NotAuthorized`, `outputCreated=false`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; no unapproved-envelope file created |
| Exit-code evidence | The workflow captures the exit code and successfully asserts `test "$code" -eq 2` with `set -e`; the raw log does not independently print the numeric code |
| Emitted source receipt | `sourceTests:94`, `approvedEnvelope:false`, `localExecution:false`, `unityOrPlayer:false`, `R03Accepted:false` |
| Downloadable run artifacts | Zero; the audited primary evidence is metadata and raw job output |

The raw checkout's `git log -1 --format=%H` equals the tested source SHA. The literal workflow receipt is corroborated by the actual unittest footer and full individual test roster, not used as an independent test counter.

The [preserved raw job log](D5B_LOCAL_DRY_ADMISSION_R5_CI_JOB_139188536483_2026-11-25.log) is byte-equivalent to the Connector's decoded log text, **32,641 UTF-8 bytes**, SHA-256 `fea6866d830090d7717cd221b1a738f336e61454fe1600d6494df18ace1e97c9`. [Machine-readable evidence](D5B_LOCAL_DRY_ADMISSION_R5_EVIDENCE_2026-11-25.json) records the exact source, blobs, roster, authority and transport receipts.

### Other automatically triggered workflows

Their run metadata was inspected separately. They are not promoted to D5-B or full-stage acceptance:

| Run | Workflow | Observed conclusion |
|---|---|---|
| [45609356164](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609356164) | Native B1 source/host qualification | Success; metadata only in this R5 audit |
| [45609356133](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609356133) | K terminal observation host contracts | Cancelled |
| [45609356171](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609356171) | Independent-review terminal host contracts | Cancelled |
| [45609356120](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609356120) | K source-bound contracts | Cancelled |
| [45609355979](https://github.com/night-outlook/hybridclr_demo/actions/runs/45609355979) | L factory and receipt contracts | Cancelled |

No cancelled run is a pass. Primary did not rerun those other workflows or claim their coverage.

## 4. Primary host checks and review

The complete suite passed on Primary's Linux x86_64 host, Python **3.12.14**, **94/94**, in **0.123 seconds**. This is separate from the Actions result. A source-segment comparison verified that all **81 prior test methods and seven prior helper methods are byte-for-byte unchanged**. The workflow now checks the actual 94-test footer and emits the matching count. Changed code/workflow text passed whitespace checks.

Two selected new methods were also run against the exact R4 writer blob `654ced61b75d1d5fca448fce756b9c9bb9ca0799`: test 82 and test 85, the latter with OSError and KeyboardInterrupt subcases. The baseline produced **three expected assertion failures across two test methods, zero test errors**. This confirms that the focused additions detect behavior absent from R4; it is not a failed R5 CI run.

A direct unapproved public-wrapper subprocess returned exit **2**, `NotAuthorized` and `outputCreated=false`, without creating or reading the missing supplied envelope. The retained source tests additionally verify that approval parsing, inspection, writer invocation and mkdir are not called under the null production gate.

A second agent conducted a bounded read-only **Primary internal code review** of creation accounting, collision handling, response flush/failure and the writer-return boundary, including isolated synthetic probes, and reported no blocking finding. This is internal implementation review, **not** the required separate independent source verdict and not a Human Review Gate.

## 5. Connector write smoke tests

The exact Git-data transport used for publication was tested on the uniquely named disposable branch `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0` in each repository. Absence was checked before creation; each branch began at its documented bootstrap feature head. A harmless tree/commit was created, its ref advanced with the expected base SHA, and the exact created remote commit read back.

| Repository | Verified smoke commit |
|---|---|
| hybridclr_demo | `a0c30160de9697d42223310bece86cd96c796d93` |
| hybridclr | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` |
| hybridclr_unity | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` |
| il2cpp_plus | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` |

**4/4 remote write/readback checks passed.** The Connector exposes no branch/ref deletion action, so these four disposable branches remain. Their commits are operational transport evidence only and are never source or acceptance pins. No default, release or other feature branch was used for the smoke commit.

## 6. Preserved limits and next gate

A five-file physical seal can coexist with a failed or unresolved command. A complete stdout JSON can precede a failed flush. Missing terminal output is not evidence of absent output. The pathname checks remain point-in-time observations, not namespace locks; there is no newly claimed APFS, power-loss, hard-kill or cross-process atomicity guarantee.

Next: independently review the R5 design, actual immutable source, old and new tests, and raw CI, including additional counterexamples. The independent reviewer must assign `PassDryAdmissionSourceOnly` or `ReturnRequired`. Primary does not assign that verdict.

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

All **18 real D5 Player cases remain NoCoverage**. Actual macOS Local admission, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain **NotRun** for this candidate. No Local preview/dry admission, D5-C/D, D6/H2/M08A/X02/SNAP-01 or Human Review Gate is opened. The canonical WEB_TO_LOCAL remains closed; Local-owned LOCAL_VALIDATION and RETURN_TO_WEB were read and not modified.

**Current state: source correction and focused CI complete; awaiting separate independent R5 review; blocked for Local execution.**

