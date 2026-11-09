# Primary reconciliation — captured-generic oneuse-08 CI prerequisite blocked

Date: 2026-11-09 UTC. Owner: Primary Implementation. Scope: **CI admission metadata only** for R03 captured-generic A2; not a Unity/IL2CPP runtime change, not an R03 stage acceptance decision.

## 1. Immutable Local return

Candidate demo `26843412eda7034cd91c0754bdcde16d5517d814`, Local publication demo `c9a5cf7a5e9c33a08db0a0f5f9bc1917e8c7ac25`. The original oneuse-08 checkpoint is

`Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-08-prerequisite-blocked/`.

Read actual original `LOCAL_RESULT.json`, `preflight/CI.json`, `preflight/SOURCE_AUDIT_ATTEMPT_JOBS.json`, `preflight/UBUNTU_SOURCE_AUDIT_JOB.json`, `preflight/UBUNTU_SOURCE_AUDIT_CHECK_RUN.json`, `preflight/CI_DECISION_RECHECK.json`, capacity and preservation receipts, and Local-owned `Handoff/RETURN_TO_WEB.md`. `Handoff/LOCAL_VALIDATION.md` is empty at the publication HEAD; Primary does not fabricate its contents.

Result **PrerequisiteBlocked / NotRun**. Exactly **0 runner invocations / 0 Unity builds / 0 Players / 19 planned cells NotRun**. The unconsumed oneuse-08 root `R03IR-CapturedGeneric-20261109-oneuse-08` and separate `-native-host-raw` root remain absent. Old oneuse-08 is not a runtime FAIL.

### Exact job-level contradiction

Original source-audit workflow: `.github/workflows/r03-ir-captured-generic-real-headers.yml`. Original workflow run **42551093381**, attempt1, source SHA as above: **completed/success**. Original Ubuntu job **128946622207**:

```json
{
  "id": 128946622207,
  "run_id": 42551093381,
  "head_sha": "26843412eda7034cd91c0754bdcde16d5517d814",
  "status": "in_progress",
  "conclusion": "success",
  "completed_at": "2026-11-09T02:28:13Z"
}
```

All seven original Ubuntu steps are `completed/success`, and the original log states seven tests Passed. The original direct job, attempt job-list and check-run records **all** show the contradictory job status. Local rechecked at `2026-11-09T03:03:15.025988Z` without change. Primary independently queried GitHub again and saw the same contradiction. Under the governing strict `job.status == completed && job.conclusion == success` predicate, this is **BLOCKED** regardless of the successful workflow run, populated timestamp, conclusion or steps. **Do not change the original record or retroactively call that job Passed.** This is inconsistent provider metadata; no specific GitHub internal failure mechanism can be inferred.

The other **13/14 mandatory jobs** satisfied job-level completed/success; the optional current-native source-only workflow also succeeded. Mac/Unity/SDK/clean four-repo Git, clean registered Original S and surviving custody were locally admitted read-only. Physical output-volume capacity was **45.853474 / 45.851467 GiB**, 77.818 seconds apart. Those were valid observations for the **blocked oneuse-08 only**, *not* admission or permission for a future run. Original S strict historical custody stays `Blocked`; 17 approved retired roots and 40 duplicates remain permanently `Unavailable`.

## 2. Minimal Primary remediation

GitHub's historical job status cannot be repaired by editing test sources. Primary therefore does **not** make an exception to the job predicate or rerun/overwrite oneuse-08. Instead it supplies a fresh exact-source CI admission path:

- `Tools/AssemblyShadow/R03IR/captured_ci_job_admission.py`: a pure, read-only consumer of the established `preflight/CI.json` schema. It requires the seven mandated **distinct exact-source workflow runs**, correct branch, actual `completed/success` run state, exactly two different OS jobs per workflow, actual job-level `completed/success`, real step-level success, unique run/job IDs and exact source SHA. It **never** converts `in_progress` to `completed` from timestamps, parent workflow, check-run, or steps. It does not fetch GitHub data or authorize Unity by itself.
- `Tools/AssemblyShadow/R03IR/test_captured_ci_job_admission.py`: reads the actual immutable oneuse-08 `preflight/CI.json` directly and **requires BLOCKED on the original anomalous Ubuntu job**. The in-memory counterfactual changing only the job status to `completed` proves the parser can recognize a consistent schema; it is **not** actual GitHub evidence, a repair, or admission for old source. Tests reject missing mandatory workflows, skipped/failed jobs, wrong source/branch/attempts, duplicate OS/jobs, missing/wrong steps and boolean/int coercion.
- `.github/workflows/r03-ir-captured-generic-batch-host.yml`: actual Mac/Linux host pipeline now includes the immutable historical file in a bounded sparse checkout and runs the strict CI admission test suite and a separate negative command verifying that the **unmodified** oneuse-08 snapshot remains blocked. The first attempt failed because one mutation removed an optional source-only workflow rather than a mandatory workflow; the test was corrected by selecting the seven required names explicitly. Historical red CI runs remain red; only a new exact-source successful run is accepted.
- `run_captured_generic_local.py` source authority binds the new parser and tests. The fresh batch ledger kind is `R03IRCapturedGenericOneUse09EvidenceBatchV1`, distinguishing the new execution from the immutable oneuse-08 prerequisite-only checkpoint. No original initializer, production native fork, original S, fixture input or prior Player source was rewritten.

### Remaining nontrivial risk

A **new** workflow run can still report contradictory job status. If that happens, even when its conclusions and tests appear green, the next oneuse-09 admission remains **BLOCKED**. A CLI sample returned by the new tool is only a strict source receipt check; Local must independently authenticate actual live workflow and job identities and check-run parity at the exact new demo commit. A successful self-test does not repair GitHub's metadata.

## 3. Next Local cycle and acceptance limits

The new oneuse-09 is a conditional **single use, 19 cells, one actual Unity2022.3.62f2 macOS arm64 ON/Release IL2CPP build, three fresh Players** (initializer-control, initializer-failure, captured-generic). It uses **entirely new absent** product and native-host evidence roots and a different additive checkpoint. The abandoned oneuse-08 roots remain absent and are not reused or republished as runtime evidence.

No batch may execute until **all seven latest exact-demo-SHA dual-OS workflows are independently `completed/success` at workflow AND job level**, the fresh strict CI snapshot passes the new source consumer, and fresh Mac Git/Unity/SDK/original-S/surviving custody, two independent >=25GiB same-volume capacity observations and root-absence gates pass. The original oneuse-08 capacity measurements do not transfer. After passing all gates, Local may invoke the oneuse-09 runner **exactly once**, publish unchanged raw original results and stop. Any issue must return to Primary, never be disguised as test success.

Remaining native V2, whole-VM epoch, GC/RSS, original S full compiler/object/link/Player joins, RC/P/E, terminal direct-AOT breadth and independent R03 High IR-R03-01/02 are outside this narrow cycle. `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`; `qualificationApproved=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic Human Review Gate.
