# R03 D5-B — independent R3 dry-admission design → source → tests → raw-CI rereview

**Date:** 2026-11-24 UTC. **Verdict:** `D5BDryAdmissionR3IndependentReview=ReturnRequired`.

This review independently inspected the exact GitHub R3 source, focused test bodies, design contract, predecessor R2 findings and final raw CI. It did **not** modify implementation, grant Local execution authority, run Unity or claim real macOS fault reproduction. The exact source-only CI result is retained as PASS, separately from this review's source-admission verdict.

## 1. Immutable provenance

All four canonical repositories were accessible through GitHub Connector with pull/push permission; feature branch for each: `codex/assembly-shadow-r01b-h1`.

| Repository | Exact reviewed source | Remote feature HEAD at review bootstrap |
|---|---|---|
| `night-outlook/hybridclr_demo` | `eeba27a51e46dd5304da108e14285a1ad5ccd10d` | `61b4522ac967e6b6707e867bbace4b8463003343` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | same |

The GitHub compare `hybridclr_demo@a909909d724c33515eee41458311f122fc745ce4` → exact R3 code SHA is **six commits / exactly three modified files** (D5Local writer, 76-test suite and CI workflow), with no changes to prior B1/D5-A/D5-B, native, package or other repository sources. Exact R3 code → initial remote feature HEAD is another six commits changing **documentation only**.

| Reviewed exact R3 Git file | Verified Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `3cf4e746bc1cd361d162ab4681af3d6d0281ae37` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `0698cff62f1e8a0437c8f2e808dfa504b36106da` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `ee768deafb7b229d7e0b9b0ef74cf9d04d710095` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` (unchanged) |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` (unchanged) |

References: [R3 design](D5B_LOCAL_DRY_ADMISSION_R3_DESIGN_2026-11-24.md), [Primary evidence](D5B_LOCAL_DRY_ADMISSION_R3_PRIMARY_2026-11-24.md), [independent review request](D5B_LOCAL_DRY_ADMISSION_R3_INDEPENDENT_REVIEW_REQUEST_2026-11-24.md), [prior independent R2 ReturnRequired](D5B_LOCAL_DRY_ADMISSION_R2_INDEPENDENT_REREVIEW_2026-11-24.md).

## 2. Confirmed source-only corrections

- **R2-IR-01, normal precommit write/fsync/rename failure path:** R3 creates and file/directory-fsyncs `INCOMPLETE.json` first (source lines 692–697), writes and verifies a separate `LOCAL_BATCH_STAGING.json` (747–753), atomically renames stage→final and fsyncs the root directory *while veto remains* (764–768). Synthetic tests 67–69 show that staged after-flush failure, post-rename directory fsync failure with unwritable `FAILURE.json`, and rename failure leave the veto and are structurally rejected. **Partially closed**: the final unlink outcome remains ambiguous as finding R3-IR-01 below.
- **R2-IR-02, descriptor-close accounting:** Parent descriptor closure now precedes final publication (759–762), and root/parent cleanup is in the root-created-aware block (777–818). Tests 71–73 inject actual close faults and verify precommit `PartialOutput` or postcommit `IndeterminateAfterCommit` with `outputCreated=true`, `retryAllowed=false`, physical reconciliation, and no false Local pass. **Closed for the specifically tested descriptor-close paths**, but does not address the later physical pathname race (R3-IR-02).
- **Fail-closed structural verifier:** `_committed_receipt_structure` (585–637) requires exactly five canonical files, checks manifest v3 and per-file SHA-256/size, rejects incomplete/staging/failure/other entries, and enforces NoUnity/NoPlayer/R03-false metadata. Tests 66, 74–76 exercise positive and negative cases. It explicitly returns `SealedDryReceiptStructureOnly_NotLocalAuthorization`, **not Local authorization**.
- **Source/approval rechecks:** The writer authenticates the raw immutable envelope via `approved_envelope(approved_raw)` (649–660), reconstructs a request and re-runs source/live-remote/historical/physical inspections before writing and prior to staging/finalization. Production `APPROVED_EXECUTION_ENVELOPE_BLOB=None` (47); synthetic tests temporarily patch this constant only in the test process.

## 3. Blocking findings

### D5B-DRY-R3-IR-01 — HIGH: post-effect veto-unlink failure can leave an apparently sealed positive receipt but a noncommitted command outcome

**Source:** [writer lines 764–803](https://github.com/night-outlook/hybridclr_demo/blob/eeba27a51e46dd5304da108e14285a1ad5ccd10d/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L764-L803), [CLI accounting lines 857–875](https://github.com/night-outlook/hybridclr_demo/blob/eeba27a51e46dd5304da108e14285a1ad5ccd10d/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L857-L875), [verifier lines 585–646](https://github.com/night-outlook/hybridclr_demo/blob/eeba27a51e46dd5304da108e14285a1ad5ccd10d/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L585-L646).

`committed=True` is set **only after** `os.unlink("INCOMPLETE.json", dir_fd=root_fd)` returns (lines 771–772). Consider an injected post-effect exception/interruption at that last external operation: removal has taken place, but the caller observes an exception before assigning `committed`. The error handler treats the product as precommit (`committed=False`), and `FAILURE.json` is optional: secondary failure to write it is swallowed (787–798). The resulting **exact five positive files** have no veto/failure file and can pass the independent structural validator, while the writer raises `PartialOutput(commit_visible=False)` and the CLI reports `FailedAfterPartialOutput` and `requiresPhysicalReconciliation=false` (872–873). This contradicts the R3 acceptance statement that failed finalization cannot produce a structurally admitted complete receipt.

**Independent bounded host counterexample:** In a temporary filesystem fixture, create the five structurally valid files, manifest-v3 per-file SHA-256/byte-size joins, and an `INCOMPLETE.json` veto. Perform the real `os.unlink` and then raise an injected `OSError(5)`; model the explicitly permitted unwritable `FAILURE.json`. Observed: five-file structure was rejected before unlink but matched the verifier's schema/hash/no-coverage conditions after the reported failure. **This exercises the source-implied post-effect state, not an actual macOS `unlinkat` errno-after-success or an execution of the complete pinned writer.** Its feasibility on APFS requires separate platform validation; the after-effect/crash boundary must nevertheless be treated as **ambiguous**, not as a proven precommit outcome. A crash after successful unlink and before the `committed` assignment yields the same visible-state ambiguity.

**Coverage gap:** [test 70](https://github.com/night-outlook/hybridclr_demo/blob/eeba27a51e46dd5304da108e14285a1ad5ccd10d/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py#L976-L989) always raises **before** invoking the actual unlink. It cannot detect the post-effect state.

**Required Primary correction:** Define a final-unlink-in-progress/ambiguous state whose errors or interrupted command outcome demand `requiresPhysicalReconciliation=true` and `retryAllowed=false`; do not report a conclusively uncommitted product when the veto may already have disappeared. Clearly separate physical-structure observation from verified successful command outcome. Add a regression that performs the actual unlink and then reports a fault, while suppressing the optional failure marker, and checks the CLI and physical verifier contract. If the stated requirement is literally **no structurally positive physical product after an unsuccessful command outcome**, revise the protocol or acceptance contract explicitly, since the post-unlink crash window cannot be eliminated by a process-local boolean.

### D5B-DRY-R3-IR-02 — MEDIUM: the approved output pathname can diverge from the descriptor-bound receipt after parent close

**Source:** [last path-identity check and finalization lines 753–773](https://github.com/night-outlook/hybridclr_demo/blob/eeba27a51e46dd5304da108e14285a1ad5ccd10d/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L753-L773). The last `_assert_open_path(parent_fd, root_fd, root, expected_parent)` is at line 757. The parent descriptor is then closed at line 762. Staging→final rename, directory fsync and veto unlink all operate through `root_fd`, but the physical path `root=Path(observed["candidate"])` is **never rebound or verified again**. A concurrent local actor able to rename the evidence child can move the open directory and recreate a different child at the approved pathname during the gap. The final operations succeed on the old **descriptor-bound but now moved** root; the sealer can return `DryAdmissionRecorded_NoUnityOrPlayer` even though the approved `candidate` points elsewhere.

**Independent bounded host counterexample:** Use real directory-descriptor-relative `os.open`, `os.rename` and `os.unlink` in a temporary Linux host directory. After closing the parent descriptor, rename the one-use root to another name and recreate its original pathname. The stage→final rename and veto unlink through `root_fd` both succeed, but the original candidate is empty and the positive file is under the moved directory. This is a physical namespace/race demonstration, **not an invocation of the full pinned writer or a proven concurrent macOS occurrence**.

**Coverage gap:** test 64 checks a **precreation parent symlink** race, not a directory rename **between parent close and final publication**. Tests 71–73 cover close errors rather than successful close plus path displacement.

**Required Primary correction:** State and enforce an explicit physical namespace-stability assumption or use an independently verifiable output-location invariant across finalization. At minimum add a deterministic post-parent-close root-relocation test and ensure such a mismatch is never reported as a successful receipt at the approved `candidate`. Avoid introducing a fallible postcommit step that silently reopens the R2 false-output-state bug; use explicit indeterminate/physical-reconciliation accounting where needed.

## 4. Exact raw CI provenance — PASS, but insufficient to close findings

Independently fetched the GitHub Actions run metadata, latest-attempt job roster and **full raw job log** for [run 45375970635](https://github.com/night-outlook/hybridclr_demo/actions/runs/45375970635), **push**, **attempt 1**, exact immutable demo code `eeba27a51e46dd5304da108e14285a1ad5ccd10d`. Job `138382258238` is **completed/success, 1/1**. Raw log is 276 lines / 29,088 characters: `Ran 76 tests in 0.118s`, `OK`, and individual `test_66` through `test_76` all `ok`. Production wrapper `--mode execute` exits 2 with `NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `outputCreated=false` and `R03Accepted=false`. The workflow runs **Ubuntu Python source-host tests**, not macOS/Unity/IL2CPP/Bee/linked native or a Player.

Earlier runs have distinct source identities and remain separate: `45375634381` FAILED, `45375689831` FAILED, `45375806304` SUCCESS at older code (not R3 76-test source), `45375922233` FAILED and `45375960396` FAILED. None is reclassified as final R3 source CI.

**Connector write/readback:** the review's participating demo repository passed an isolated Connector commit/readback smoke test: disposable branch `codex/smoke-d5b-r3-review-20261124-cc64b3` based on demo HEAD `61b4522ac967e6b6707e867bbace4b8463003343`; remote smoke commit `35588bfa100c61bd108952455afc1c84dd9ffd97` was read back exactly. Connector branch deletion is unavailable; this *non-feature* smoke branch remains.

## 5. Scope-limited final decision and stop

**`D5BDryAdmissionR3IndependentReview=ReturnRequired`.** The R3 source/tests close the ordinary stage/fsync/rename and descriptor-close cases, but the two new evidence-boundary counterexamples remain unhandled by the exact 76-test suite. Return the two focused findings to Primary for remediation, source-only regression tests, fresh **exact-source CI** and **another separate independent rereview**. No reviewer implementation, test editing, approval hash change, new Local handoff, or later milestone was performed.

**Hard execution boundary unchanged:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; 18/18 D5 Player cases `NoCoverage`. Real Unity/IL2CPP/full VM/GC/Bee/Mach-O/PID/Player `NotRun`. No Local preview/dry admission, D5-C/D, D6/H2/M08A/X02/SNAP-01, Human Review Gate or implicit user execution approval.
