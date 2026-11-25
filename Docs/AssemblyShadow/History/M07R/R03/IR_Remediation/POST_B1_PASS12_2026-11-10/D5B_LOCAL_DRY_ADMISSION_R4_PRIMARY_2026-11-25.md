# R03 D5-B — Primary R4 focused corrections and exact source CI

**Date:** 2026-11-25 UTC. **Primary state:** `D5BDryAdmissionR4Primary=SourceOnlyCIComplete_PendingIndependentR4Review`. This is a source-only Primary record, **not** an independent verdict or authorized Local handoff. Implements the [R3 independent R3-IR-01/02 findings](D5B_LOCAL_DRY_ADMISSION_R3_INDEPENDENT_REREVIEW_2026-11-24.md) under the [R4 design](D5B_LOCAL_DRY_ADMISSION_R4_DESIGN_2026-11-25.md).

## 1. Exact four-repository source custody

All repositories use `codex/assembly-shadow-r01b-h1`. Final **CI-tested source** tuple (not subsequent documentation commits):

| Repository | Exact immutable code |
|---|---|
| `night-outlook/hybridclr_demo` | **`55f3eaf5bb87f717d02e2ad81c9ea448397d71ab`** |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

GitHub compare initial R3 independent-review feature HEAD `ee283580c372c45fb67dc85bfa51a7d34251449e` → final R4 **code** `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab` confirms **two commits; only three modified files**:

| Changed file | Verified exact Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `654ced61b75d1d5fca448fce756b9c9bb9ca0799` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `df66cce2fc321fe5deaaa370c138c8c9727e5f7a` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `a8362ab889c29fa7befc0b56e03abe3ad53af3d7` |

Unchanged plan Git blob `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9`; unchanged production wrapper Git blob `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39`. All earlier C10, B1, native, package, historical evidence and the other three source repositories remain unchanged.

## 2. Focused implementation and test evidence

**R3-IR-01:** The writer now records final-unlink-attempt state before the call; any exception at/after an uncertain unlink yields `commit_uncertain` and a CLI `IndeterminateAfterCommit` with `UnknownAfterFinalUnlink` and physical reconciliation. It no longer attempts a `FAILURE.json` write when veto removal may already have committed. This explicitly preserves the difference between physical receipt structure and an authenticated command completion. Tests 77–78 inject an actual physical unlink *then* an error and assert the consumed, non-retryable indeterminate result.

**R3-IR-02:** New source helper `_assert_final_path_identity` checks approved canonical parent physical identity and the named child inode against `root_fd` after parent-close, before final unlink and after commit. Tests 79–81 relocate/replace the actual output directory on either side of the final publication and verify no incorrect successful result at the approved pathname, including public CLI physical reconciliation. This is a point-in-time host test, not a cross-process filesystem lock or macOS runtime proof.

**Final source-only CI:** [GitHub Actions 45532666894](https://github.com/night-outlook/hybridclr_demo/actions/runs/45532666894), push attempt 1, immutable demo SHA `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab`, job `138931561379`, **completed/success, 1/1 job**. Independently read back full raw job log (**281 lines / 30,028 characters**): `Ran 81 tests in 0.139s`, `OK`, individual `test_77` through `test_81` all `ok`. Workflow JSON correctly reports `sourceTests:81`. Public `run_d5_local.py --mode execute` is still denied with exit 2, `NotAuthorized`, `outputCreated=false`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION` and `R03Accepted=false`.

**Earlier intermediate code/run:** `47b157a5de3cd23e6fd8f604ae776f592ab931f3` passed [CI 45532556269](https://github.com/night-outlook/hybridclr_demo/actions/runs/45532556269) with 80/80 Python tests but had an obsolete emitted `sourceTests:76` summary. That is **not** the final R4 evidence. Final source and summary are solely the pinned 81-test run above; earlier R3 76/76 PASS remains historically valid, not independently approved.

## 3. Connector transport and next gate

Read/write permissions verified on all four canonical repositories. The participating demo repo completed a Git-data **write/commit/push/readback smoke test on a separate disposable branch** `codex/smoke-d5b-r4-primary-20261125-9fc4e7` from base `55f3eaf5bb87f717d02e2ad81c9ea448397d71ab`; remote smoke commit `b614bbc194a0cca090cf718e716efe32bd82ab87` exactly matched. No remote-branch delete is exposed by the Connector, so the disposable branch remains, isolated from the feature.

**Primary assessment only:** focused code, source-host regression and exact CI are complete. **Independent R4 review remains PENDING**; earlier independent `D5BDryAdmissionR3IndependentReview=ReturnRequired` remains binding until another reviewer issues a distinct verdict. No execution approval or Local handoff may be inferred.

**Execution state:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. Actual macOS/Unity/IL2CPP/native VM/Bee/Mach-O/GC/PID/Player `NotRun`; all 18 real D5 Player cases `NoCoverage`. No Local preview or execution, D5-C/D, D6/H2/M08A/X02/SNAP-01, Human Review Gate or R03 acceptance.
