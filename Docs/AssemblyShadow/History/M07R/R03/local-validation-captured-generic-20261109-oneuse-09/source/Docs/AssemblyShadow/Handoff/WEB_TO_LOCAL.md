# Primary Implementation → Local Validation — CONDITIONAL A2 oneuse-09

**Why oneuse-09 rather than oneuse-08:** The first oneuse-08 attempt never reached the runner. It remains immutable `PrerequisiteBlocked / NotRun` at candidate source `26843412eda7034cd91c0754bdcde16d5517d814`, published evidence `c9a5cf7a5e9c33a08db0a0f5f9bc1917e8c7ac25`, because Ubuntu Actions job `128946622207` (run `42551093381`) persistently reported `status=in_progress` with `conclusion=success`. No completed-job inference from the parent workflow, timestamp, logs or check-run is allowed. All 19 old cells are NotRun, old runner/build/Player counts zero, and both old `R03IR-CapturedGeneric-20261109-oneuse-08` product/native-host roots remain **absent and not reused**. Read the [exact Primary reconciliation](../History/M07R/R03/IR_Remediation/POST_CAPTURED08_2026-11-09/PRIMARY_CI_ADMISSION_REMEDIATION.md) and the **original** Local prerequisite evidence. The new oneuse-09 is a *fresh* independent authority with distinct unused roots, evidence checkpoint and final-source CI jobs.

Date: 2026-11-09 UTC. Owner: Primary Implementation. **One** fresh, source-pinned, focused R03 IR-R03-02 *physical captured-baseline generic* cycle. This is a new 19-cell, 1-build/3-Player batch — **not** a replay of initializer oneuse-07 or an acceptance of the independent R03 stage. Local may execute only after every gate below passes; otherwise return `BLOCKED/NotRun` without creating/consuming the batch root.

## 1. Required reading and exact source authority

Read in order:

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, this document, then `Handoff/RETURN_TO_WEB.md`.
2. `History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/CAPTURED_GENERIC_A2_PRIMARY_SOURCE_REVIEW.md`, `CAPTURED_GENERIC_A1_OWNER_HOST.md`, and `NEXT_PRIMARY_WORK.md`.
3. `Tools/AssemblyShadow/R03IR/run_captured_generic_local.py`, `prepare_captured_generic_sources.py`, `PlayerProject/R03CapturedGenericPhysicalProbe.cpp`, `R03CapturedGenericPlayer.cs`, `R03CapturedGenericAotOwner.cs`, `verify_captured_generic_native.py` and their actual CI test sources.
4. Published Local oneuse-07 `History/M07R/R03/local-validation-initializer-20261107-oneuse-07/`, original oneuse-06 finding in `local-evidence/FINDING.md` plus `BRIDGE_FINDING.json`, historical original-S custody and owner-retirement disposition.

Common branch `codex/assembly-shadow-r01b-h1`. **The exact execution demo SHA is the FINAL 40-character pushed branch SHA in the accompanying Primary-to-Local continuation prompt; a Git document cannot embed the SHA of its own later publication commit.**

| Repository | Expected local clean checkout | Required source revision |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final Primary demo publication SHA — verify local HEAD, actual live remote and Git source bytes |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

All repos must be independently Git-owned, clean and with the exact canonical origin. Local must not use uncommitted working-tree changes or substitute a newer native/runtime/package revision. Do not mutate original S/K or prior Local checkpoint sources. The new captured target is an independently emitted `Methods.dll` and is checked for repeatable **same-host** bytes twice; A1 demonstrated that equal MVIDs do not guarantee cross-host identical SHA-256. Do not hardcode an unverified A1 Mac/Linux Methods digest as a Player fixture identity.

## 2. Mandatory exact-final-source dual-OS CI

The source-bound `Tools/AssemblyShadow/R03IR/captured_generic_handoff_ci_contracts.py` performs five positive/negative host tests that **all seven** real workflow files self-trigger and include this exact handoff path, plus the pinned public native checkout. This is a *trigger-source* proof only: it does not claim that any actual GitHub Actions job ran. Following this final publication, inspect each workflow's **real** latest run with the exact demo commit in the Primary continuation prompt; even a successful run at the immediately preceding demo commit is insufficient.

Before any run, inspect the **actual workflow jobs**, not just overall status, for exact final pushed demo SHA, **both `macos-15` and `ubuntu-24.04` completed/success with no missing, failed, skipped or cancelled job**:

- `.github/workflows/r03-ir-captured-generic-owner-host.yml` — real CLR owner/physical argument structural and body/negative tests (host only).
- `.github/workflows/r03-ir-captured-generic-native-host.yml` — real test-only native probe compiled under C++11 with intentionally **VM-shaped mock** APIs, including inflation-poison, silent-null, and side-effect negatives.
- `.github/workflows/r03-ir-captured-generic-batch-host.yml` — real C# source compilation against isolated API host, prepare/coordinator and strict source tests.
- `.github/workflows/r03-ir-captured-generic-real-headers.yml` — real pinned **public fork source ABI** declarations/implementations. This is explicitly **NO official Unity SDK/Baselib compile**.
- `.github/workflows/r03-ir-initializer-bridge-host.yml` — original real Bi4 bridge-host source.
- `.github/workflows/r03-ir-initializer-local-contracts.yml` — original initializer runner/native host regressions.
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml` — actual current 8+2 native host source/execution and custody preflight.

**Strict job-status gate for this new cycle:** `Tools/AssemblyShadow/R03IR/captured_ci_job_admission.py` reads a fresh, exact-new-source `CI.json`-shaped snapshot assembled from **actual GitHub workflow-run and job-list responses**. It must return `PassedSevenWorkflowFourteenJobRecords_NoLocalAuthorization` only if all seven run IDs and all fourteen OS job records are genuine `status=completed` AND `conclusion=success` at the final pushed SHA. Independently confirm each direct job and its attempt-level/check-run status; if any source disagrees, stop as `PrerequisiteBlocked`. The parser deliberately rejects the original oneuse-08 `in_progress/success` sample and cannot overwrite it. A parser PASS is a necessary CI receipt cross-check, **not** permission to skip other admission gates or launch Unity.

The current-native source-only gate should also be green if triggered. Record the actual final-source run IDs/job IDs/conclusions and any red/cancelled ancillary workflows without reclassifying their historical outcomes. A real-fork source audit is NOT a pass for official SDK translation-unit compilation. All new C++ A2 integration and real IL2CPP linking remain genuine Local proof obligations.

## 3. Fresh macOS/SDK/source/custody/capacity admission

On the actual Apple Silicon Mac, verify official Unity **2022.3.62f2** at the pinned executable and real working IL2CPP SDK/compiler, `dotnet` SDK >=8 and actual .NET8 runtime, current process-local PATH, no competing Unity/Bee/Player, four Git commits above, and the retained **clean, registered, detached** original-S `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b` at the exact path below.

The owner explicitly deleted **17 historical runtime-related roots and 40 duplicate paths**. Mark them `Unavailable/PermanentlyDeleted`; do **not** recreate, restore, compare nonexistent payloads as present or silently waive surviving custody. Historical strict custody remains `Blocked`. Preserve source/installed SDK/remaining history with the established before/after tests.

Use these exact existing paths (the NEW output roots must **not** exist):

```bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
OUTPUT_PARENT=/Users/ah/GitHub/hybridclr/r03-local-validation
RUN_ROOT="$OUTPUT_PARENT/R03IR-CapturedGeneric-20261109-oneuse-09"
HOST_RAW="$RUN_ROOT-native-host-raw"
CI_SNAPSHOT="$OUTPUT_PARENT/captured-generic-09-prerequisite-CI.json"
# CI_SNAPSHOT is a NEW, fresh GitHub API snapshot outside both unconsumed roots.
# DEMO_COMMIT = exact FINAL pushed SHA reported in Primary's closing prompt.
```

Require canonical physical paths, no symlink/alias, no overlap with repositories, original-S, previous batch/evidence roots or SDK, and both RUN_ROOT and HOST_RAW absent. Before creating either, sample **actual available bytes via statvfs** on the same `OUTPUT_PARENT` volume in **two fresh measurements at least 60 seconds apart**; preserve timestamps, mount/device and raw values. This cycle grants a **new oneuse-09-only conditional 25GiB minimum**: **BOTH** samples must be >=**26,843,545,600 bytes**. This is a single-use allowance for this one IL2CPP build/three-Player cycle, not transfer of oneuse-07's consumed permission, not a change to the project's 20GiB hard or 40GiB advisory thresholds, not a promise future build disk usage fits. At >=25 but <40GiB, explicitly record advisory risk. **No disk cleanup target is authorized** by this document.

First independently collect and preserve a **new** `CI_SNAPSHOT` from the **latest final-source** GitHub Actions workflow and job endpoints in the same `{"runs":[...],"jobs":{"<runId>":{"jobs":[...]}}}` structure as the prior published `preflight/CI.json`; it must not be an edited copy of oneuse-08. Ensure it is a new regular nonsymlink file outside both product roots, retain the original source bytes and hash, then evaluate the strict job-level predicates:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/captured_ci_job_admission.py" \
 --ci-json "$CI_SNAPSHOT" --demo-commit "$DEMO_COMMIT"
```

Any result other than `PassedSevenWorkflowFourteenJobRecords_NoLocalAuthorization` is **BLOCKED**, no runner. Do not repair or filter a contradictory job status in the JSON. Verify original direct job, attempt jobs and check-run records independently, and retain any contradictory bytes. The other six admission categories remain mandatory even if this script passes.

Run existing read-only environment admission (not the actual coordinator) with the new absent output path:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

If **ANY** gate fails: retain source/CI/capacity/admission logs, return `PrerequisiteBlocked`, runner count 0, builds 0, Players 0; **no** automatic retries or capacity-threshold changes. Obtain human approval for any separate storage operation; do not silently perform cleanup.

## 4. ONE authorized 19-cell Local execution — after GO only

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
 "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_captured_generic_local.py" \
 --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
 --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

The runner itself authenticates the four Git HEADs, actual new Git-source bytes, new unused roots, source preparation receipts, both fixture families, ten original native hosts, original-S **archival-only** S/process/binary audits, and final custody. Its fixed 19 cells include exactly **one actual Unity2022.3.62f2 macOS arm64 IL2CPP ON/diagnostics2/Release BuildPipeline**, exactly **two distinct original initializer regression Players** and exactly **one new physical captured-generic Player**. No additional stimuli, stale app reuse, process replay, manual binary patch, alternative fixture, changed timeout/guard/expected semantics, or Local architectural refactor.

The same new compiled Player must preserve the prior source-bound Bi4 `MethodBridge.cpp` augmentation before/after BuildPipeline and the real linked exports `R03_IRW_BridgeStatus`, `R03_IRW_OnPrepared`, `R03_IRG_Open`, `R03_IRG_Probe`, `R03_IRG_AttemptRuntimeInvoke`, `R03_IRG_Seal`. An actual linked binary is necessary, but is not alone runtime success.

Two **fresh** initializer Players must reproduce oneuse-07 control (Commit0/state6, linked Bi4 phase103=1, one callback299/300, native physical field3/mask15, no reason) and failure (Commit19/state9, same linked callback/field/mask, exact `R03IR.InitializerFailure.AfterPublication.V1` first-recovery, attempted postterminal AOT without side effect). Keep their original strict V1 native raw, phase journals, native recovery, fresh OS commands/PIDs/nonces, logs and byte digests. **Do not substitute old oneuse-07 receipts as new Players.**

The *new captured-generic Player* must first prove successful **real** fresh transaction Commit0/state6 with prewarmed `Touch<object>` counter1, without resolving/using physical `Methods.R03.Node` before Commit. Only afterward, a native test-only observer obtains the physical AOT `Methods` TypeDef handle, constructs an actual inflated `Assembly-CSharp` owner `R03CapturedGenericAotOwner.Touch<Methods.R03.Node>` `MethodInfo`, verifies its `method_inst` physically captures the original baseline type rather than the interpreter replacement, and checks state6 **again after generic inflation**. It then calls the **actual native `AssemblyShadow::AssertMethodIsActive`**, expecting denial, final FailedAfterCommit state9, unmodified native first-error **15** with `ShadowCapturedBaselineType`, `CapturedArgumentAssembly=Methods`, `Context=method_inst`, `TypePath=/arg[0]` and `Reason=CapturedBaselineType`. A separate postterminal actual `Runtime::Invoke` must report a **real exception/rejection** (not merely null return), no AOT method-body execution, preserved counter1→1 and unaltered first failure. The unique bounded native V1 JSON writer must be exclusive, fsynced, strictly request/fixture/PID/executable/overlay/build bound, with native real-source probe flags and all acceptance fields false.

Any early failure (including method inflation poisoning the world **before** the guard), Unity compiler issue, absent specialization, wrong type, missing export, missing method-entry denial, wrong error/state or silent-null must remain a genuine `Failed/ReturnRequired`, with its exact native/Unity/Bee/log/command artifact. **Do not repair nontrivial source locally, rerun or claim the first error15 was the method guard if it was caused earlier.** Native V2 remains NotImplemented/NotRun in this experiment.

## 5. Evidence custody, publication and STOP

Preserve the original oneuse-08 `local-validation-captured-generic-20261109-oneuse-08-prerequisite-blocked` checkpoint, its contradictory job records and the unused old root names unchanged. The new oneuse-09 checkpoint is additive and distinct.

After the single invocation even if a cell fails, authenticate the complete raw new batch and sibling native-host custody (including actual literal symlinks, original byte inventory, source/body/install/Player PIDs), independent bounded seal, and before/after protected source/SDK/surviving historical evidence. Preserve the new product/host roots unchanged. Record BuildReport warning/error **without** suppressing a failed BuildPipeline, full actual Unity Editor.log/Bee diagnostics, `MethodBridge.cpp` source after augmentation and after build, GameAssembly link identity and each unique Player log.

Publish to a **new**, nonoverwriting checkpoint at `Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-09/`, with scoped `LOCAL_RESULT`, original raw receipts, evidence index/seal, strict first-error and Player process joins, exact execution SHA/source vs later evidence publication SHA, original-S archival and retired-source dispositions. Update **Local-owned** `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`. Commit/push via GitHub and verify all four repository remote HEADs. Report the exact result and stop. No retry, unrelated workload, H2/M08A/X02/SNAP-01, Human Review Gate approval or milestone promotion.

## 6. Explicit acceptance boundary

A successful A2 oneuse-09 establishes **only** focused compiled/linked source, genuine physical captured-method native guard error15 and its three Player witnesses. It does **not** prove native complete `NativePreopenedSnapshotV2`, VM-wide epoch, GC/RSS, managed shutdown, complete source/object/link historical original-S joins, production SLA, universal AOT direct-call denial or independent R03 full-stage acceptance.

The independent R03 **FAIL** and High `IR-R03-01/02` remain open. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `qualificationApproved=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No automatic Human Review Gate.
