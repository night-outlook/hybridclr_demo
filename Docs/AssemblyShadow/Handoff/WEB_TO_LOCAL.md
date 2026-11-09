# Primary Implementation → Local Validation — CONDITIONAL ONEUSE-11 (native B1, shared admission repaired)

Date: **2026-11-09 UTC**.

**Historical Local return (CONSUMED oneuse-10):** original execution candidate `hybridclr_demo@7c8af27e63038c77c13171c5776760e869e9c09d`, evidence publication `hybridclr_demo@e75cb536626358b69d7bbd90837a2044a2fab86a`. The independently authenticated 14-file source and 47-path native VM gates, all six CI jobs, retained original-S/custody and historical 42.193/42.198-GiB samples passed within original scope. The **shared Mac/runner** consumer still required 11/45 and returned `PrerequisiteBlocked/NotRun` before coordinator (0 calls), build (0), Players (0), all 19 cells NotRun. **Both oneuse-10 reserved output roots remain absent but are retired; NEVER reuse them.** Read [original checkpoint](../History/M07R/R03/local-validation-native-b1-20261109-oneuse-10/README.md), Local-owned [RETURN_TO_WEB](RETURN_TO_WEB.md), and [Primary correction/review](../History/M07R/R03/IR_Remediation/POST_B1_BLOCKED10_2026-11-09/PRIMARY_ADMISSION_REMEDIATION.md). `LOCAL_VALIDATION.md` was empty in the published Git; do not invent contents.

**Primary oneuse-11 correction:** both actual `run_current_native_validation_cycle.validate_sources` (shared by Mac readmission and runner) and `run_current_native_host_preflight.inputs` enforce the **exact selected B1 candidate**: 14 pinned source file identities, 47 native VM file hashes, current pins `il2cpp_plus@a0209bf4285db3f0d0fc66d8817578235438cef4`. Both entry paths have positive and negative CI (real four-repo checkouts; 11/45, wrong pin/blob, mixed profile and wrong branch rejected). Historical oneuse-I source evidence at old native `41764ae...` is retained as historical, not promoted. All native/Player/B1/B2 implementation code, original S archive and historical evidence remain unchanged. The only new execution authority is this **conditional oneuse-11**; no retries.
 This handoff authorizes **one** new focused, source-pinned Local Validation cycle, **only after every admission requirement below passes**. If any prerequisite is false or unavailable, record `PrerequisiteBlocked/NotRun` without invoking the runner. The previous oneuse-09 and oneuse-10 are **CLOSED/CONSUMED**; never rerun them or reuse their output paths.

## 1. Current objective and boundaries

Validate the **actual originating native first-error B1 record** in a single real Unity 2022.3.62f2 macOS ARM64 IL2CPP ON/Release build with three distinct real Players:
- initializer-control: actual linked Bi4 callback, control Commit0/state6 and **B1 Empty (code0/origin0)**;
- initializer-failure: actual Bi4 callback, postprepared Commit19/state9 and **B1 Frozen code19 / InterpreterInitializer origin2**, B1 first reason byte-identical to original native V1;
- physical captured-generic: real `Methods.R03.Node` TypeDef in `Assembly-CSharp` AOT owner `method_inst`, postinflation Committed6 then native guard error15/state9, postterminal denied `Runtime::Invoke` without advancing AOT count1→1, **B1 Frozen code15 / Guard origin1**, B1 reason byte-identical to original native V1.

The same new one-use 19-cell coordinator also runs original-S read-only archive/process/source/binary audits, ten current-native host components and focused managed/fixture host tests, **existing B2 strict/sanitized codec and POSIX descriptor-transaction host suites**, exact source manifests, one actual linked GameAssembly export check, fully sealed local output and postflight four-repo authority.

This cycle **cannot** prove full general NativePreopenedSnapshotV2 transport, B3 coherent whole-VM epoch, actual real V2 descriptor-relative writer/manifest, original S complete object/link/Player provenance, GC/RSS/ShutDown, RC/P/E performance, full legacy regression, or R03 acceptance. All those flags remain false; do not enter H2/M08A/X02/SNAP-01 or self-approve Human Review Gate.

## 2. Read order (Local Validation must use Git, not chat history)

1. `night-outlook/hybridclr_demo/Docs/AssemblyShadow/README.md`
2. `night-outlook/hybridclr_demo/Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`
3. This `Handoff/WEB_TO_LOCAL.md` at the **final exact demo commit in the owner-supplied handoff prompt**.
4. `History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md`
5. `History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B1_NATIVE_ORIGIN_IMPLEMENTATION_AND_REVIEW.md`
   - `History/M07R/R03/IR_Remediation/POST_B1_BLOCKED10_2026-11-09/PRIMARY_ADMISSION_REMEDIATION.md` (new shared-admission return/fix).
6. `Handoff/RETURN_TO_WEB.md` (historical Local oneuse09 result), plus `History/M07R/R03/local-validation-captured-generic-20261109-oneuse-09/README.md` (read only).
7. `Tools/AssemblyShadow/R03IR/run_captured_generic_local.py`, `current_native_source_gate.py`, `current_native_vm_delta_contracts.py`, `verify_first_error_b1.py`, and `PlayerProject/R03FirstErrorB1Probe.cpp`.

## 3. Canonical repositories, branch, exact candidate pins

Transport: four canonical HTTPS GitHub repositories. No local-only code, smoke branches, or detached unpushed commits may substitute. Repo paths are from the previously validated Local workspace; verify actual existence and clean checkout, do not assume the parent directory itself is a repository.

| Repository | Local absolute checkout | Branch | Remote commit |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | **Use the exact latest pushed full 40-character SHA in the final owner handoff prompt.** The pre-publication audited doc/design base is `de467e1dd31ec557fa61dbc110a5126fef2fda52`; do not substitute this earlier base for final HEAD. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `a0209bf4285db3f0d0fc66d8817578235438cef4` |

Reason demo HEAD is in the final handoff prompt: a Git commit that contains this file cannot self-reference its own SHA. Use that precise pushed SHA for `--demo-commit` and all remote/working tree/CI checks. Independently verify `git -C <repo> remote -v`, `git -C <repo> rev-parse HEAD`, `git -C <repo> status --porcelain`, `git -C <repo> ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1` for **all four**; require clean, correct origin identity, remote HEAD = checked-out HEAD = exact source pin. Stop on mismatch.

**Fixed source pins**: Unity `2022.3.62f2`; macOS arm64; IL2CPP ON; Assembly Shadow ON; diagnosticsLevel2; C++ Release. Use original installed engine/vendor headers and installed SDK **only**, never a guessed `Baselib.h` replacement. Managed target generation must preserve the original fixture SHA/MVID/deterministic double-build and linked Bi4 exact signature. `Tools/AssemblyShadow/R03IR/current_native_candidate.json` is the **new current-only** candidate; original `Tools/AssemblyShadow/R03/source-pins.json` is historical and must not be modified.

## 4. Mandatory independent preflight, before any oneuse-11 runner invocation

1. Four exact checkouts/remotes clean, SHA/branch as above. Verify `current_native_source_gate.py --exact-checkout-heads` passes the full 14-source native/current candidate and `current_native_vm_delta_contracts.py` passes **47 exact native VM source files** at the new native commit; original old 45-file/41764 candidate records remain historical and are not a substitute.
2. **At exact FINAL demo HEAD**, wait until each of the following THREE GitHub Actions workflows has `status=completed`, `conclusion=success` and **both** `macos-15` and `ubuntu-24.04` job-level `completed/success` (no mixed in_progress/success; no skipped/failed/cancelled). Verify workflow, run attempt, HEAD and job records, do not infer job status from run conclusion: 
   - `.github/workflows/r03-ir-native-b1-source-and-host.yml`: 25 strict B1 JSON cases, 15 preparer cases, 15 oneuse source cases, one host C++11 real probe compilation with VM-shaped stub and no Unity.
   - `.github/workflows/r03-ir-native-b1-four-repo-source.yml`: source-pinned four-repo checkout, source gate contracts, native 47-path delta and B1 public source symbol audit.
   - `.github/workflows/r03-ir-b1-shared-mac-runner-admission.yml`: four real clean feature-branch checkouts; the actual composed outer Mac/runner 14/47 validator **and** inner native-host 14/47 source admission, real source/blob/pin/branch negatives and synthetic coordinator/host regressions. Official Mac Unity/OriginalS/capacity/SDK are separately MOCKED in hosted CI and remain mandatory real Local admission.
3. **At exact native SHA `a0209bf4285db3f0d0fc66d8817578235438cef4`**, the native `.github/workflows/r03-native-b1-first-origin.yml` completed/success with both OS jobs completed/success. Historical reference [42598105952](https://github.com/night-outlook/il2cpp_plus/actions/runs/42598105952) passed. It is C++11/17 host proof, not SDK/Unity build.
4. Confirm historical original S is **present**, clean, identity-verified and read-only at the separately admitted original S root; original archive contents/expected 17 retired roots and 40 duplicates remain unchanged/unavailable. The original S root from oneuse09 was `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`, but independently locate/authenticate instead of trusting a guessed path. Confirm saved original-S index, source/artifact process receipts, remaining custody, immutable previous oneuse07/08/09/**10** evidence and official Unity/SDK path (exact native Mac).
5. Create **two **new** same-volume free-space samples** at least **25 GiB each**, separated by the project-required admission interval (historically >=60 seconds), on the volume hosting new output. No historical root deletion/cleanup, archive regeneration, SDK movement, or reuse for capacity. If insufficient, stop and ask user for a new approved capacity decision.
6. Require the new canonical output root **absent** with no aliased/symlink parent; separately require automatic sibling `<output>-native-host-raw` **absent**. **Mandatory fresh output name for this cycle, independently verify never used or aliased:** `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-NativeB1-20261109-oneuse-11`. Do not use any oneuse07/08/09/**10** output or its reserved, absent roots. All path/permissions/canonicalness checks must pass before invoking the runner.
7. Fresh independent `-B --help` probe for the actual current `run_captured_generic_local.py` from a foreign working directory, with no `PYTHONPATH` or local executable side effect. Confirm installed .NET8/runtime/C++ compilers and required Unity editor/SDK are actual, not stubs. Do not reinterpret host-only CI as Local build evidence.

If any check fails, record **PrerequisiteBlocked/NotRun** with precise source/job/capacity/status receipts and **zero** Unity build/Player/runner invocations.

## 5. Exactly one authorized execution

After successful admission only, invoke **once** (replace placeholders with independently verified actual exact paths and the pushed **final demo HEAD**, no retries):

```bash
python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_captured_generic_local.py \
  --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r \
  --original-s /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse \
  --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-NativeB1-20261109-oneuse-11 \
  --unity <ACTUAL_INSTALLED_UNITY_2022_3_62f2_EDITOR_EXECUTABLE> \
  --demo-commit <EXACT_FINAL_40_CHARACTER_DEMO_HEAD>
```

This is one invocation of `run_captured_generic_local.py` despite historical filename; its result kind is now **`R03IRNativeB1OneUse11EvidenceBatchV1`**. It is NOT the consumed oneuse09. It owns 19 fixed cells (original-S archive/process/compiled-source lexical/binary checks, deterministic fixture generation, ten native-host components plus B2 strict+sanitized codec/descriptor suites, one Unity build, initializer-control/failure/captured-generic three independent Players, postflight authority). No dry-run, mock Unity, automatic retry, mutated fixture, extra Player or substitute engine.

## 6. Mandatory observations and raw evidence

- **Actual linked binary:** BuildReport success with exact Unity 2022.3.62f2 macOS ARM64 IL2CPP Release/Shadow ON and source-input manifest hashes; GameAssembly actual SHA, native `nm -gU` exports `_R03_IRB1_Open`, `_R03_IRB1_Seal`, `_R03_IRG_Open`, `_R03_IRG_Probe`, `_R03_IRG_AttemptRuntimeInvoke`, `_R03_IRG_Seal` once each; preserved linked Bi4/method bridge and original source material, not just source file symbols.
- **Initializer control:** one fresh PID and sealed `raw.json`, `raw.json.vm-recovery.json`, `raw.json.first-error-b1.json`; real linked Bi4 phase103=1; callback299/300 once; physical field3/mask15; Commit0/state6; V1 empty first reason; B1 state0/code0/origin0/reason null.
- **Initializer failure:** one independent fresh PID and all raw files, same linked Bi4/callback/field evidence; Commit19/state9 postprepared V1 exact sentinel. B1 Frozen state2/code19/origin2 and first reason **byte-for-byte equal** to independently authenticated V1. Postterminal canary does not advance.
- **Captured generic:** one third PID and all raw files; real postinflation physical Methods.R03.Node / separate AOT owner method_inst guard, 6→9, code15, V1 full physical guard reason, B1 state2/code15/origin1, exact byte-identical first reason, postterminal Runtime::Invoke reported rejection and 1→1 AOT counter.
- Each B1 record must bind request runId/caseId/dllSha256, actual process PID, exact source build/executable identities; include actual first reason length and no truncated fallback. Empty/Invalid/missing/other-origin or reason mismatch is **Failed**, never a host-only substitute or an accepted V2.
- **Native host B2:** strict/sanitized codec and POSIX descriptor transaction results with immutable source hashes and receipts, `actualUnity=false` and `productionTransportEnabled=false`; do not imply real VM B2 integration.
- **Provenance/custody:** preserve original historical receipts, new exact run commands/logs/PIDs/binary/fixture hashes, native host raw, source manifest, JSON B1/V1 fields, platform compiler/SDK, product seal and four repo postflight heads. Do not rehash old deleted historical roots as if they were available.
- Source-only host statuses must remain explicitly distinct from actual local Unity runtime status.

Required emitted local paths (under the new output root): `LOCAL_BATCH_RESULT.json` or runner's actual sealed aggregate `RESULT.json`, `MANIFEST.json`, `players/*/request.json`, `players/*/verification.json`, `players/*/raw.json`, `players/*/raw.json.first-error-b1.json`, initializer `players/*/raw.json.vm-recovery.json`, `builds/**/build-receipt.json`, `commands/**/command.json`, `host/b2-*/RESULT.json`, native host sibling raw/custody manifests and `Player.log`. Preserve actual filenames as emitted: never invent or rename evidence; record missing paths as `Missing/NotRun`. Publish summarized immutable selected receipts to a new `Docs/AssemblyShadow/History/M07R/R03/local-validation-native-b1-20261109-oneuse-11/` checkpoint, preserving distinction between raw local evidence and uploaded selected metadata.

## 7. Ownership, failure handling and handoff back to Primary

Local may only adjust **non-source** invocation/environment details necessary to locate the actual installed Unity/.NET/SDK or correct command spelling/absolute path before executing the single batch. It may diagnose, collect traces, perform source read-only analysis, and make independently testable tiny local fixes **only if** they are truly bounded and permitted by the established ownership boundary. **Do not edit** `AssemblyShadow.cpp/.h`, new B1 header/host, managed Player, B1 writer/parser/runner, native fixture, source-pins, B2, architecture, or historical evidence in Local. A non-trivial correctness/scope/source issue is **ReturnRequired** to Primary with code lines, raw evidence and proposed focused tests; no second oneuse10 execution.

Record new factual Local result in **`Handoff/LOCAL_VALIDATION.md`**, and any Primary-owned fixes in **`Handoff/RETURN_TO_WEB.md`**; commit and push original immutable source/evidence/receipt records through the assigned Local Git transport. Distinguish `Passed`, `Failed`, `PrerequisiteBlocked/NotRun`, `Unavailable`, `NoCoverage` and audited historical evidence; do not promote partial results. The handoff is **consumed** after exactly one invocation or after a documented prerequisite block; any future run needs a **new Primary Implementation source-pinned WEB_TO_LOCAL** and fresh output roots.

## 8. Current acceptance and subsequent plan

`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; wholeVmEpoch=NotProven`. PureInterpreter disabled; original independent R03 overall FAIL and High IR-R03-01/02 open.

After this focused B1 Local return, Primary owns remaining **B2 actual exclusive descriptor-relative complete V2 writer and B3 coherent VM epoch / lifecycle**, original S full provenance and deferred GC/RSS/RC/P/E. No H2, M08A, X02, SNAP-01 or human review self-approval. Local Validation's role is empirical verification, not new architecture or major code changes.

## 9. Exact-source prepublication CI receipts (not execution authority for a later SHA)

Historical pre-oneuse-10 source checkpoint `c6b7b557078251028ce8f9869e0279b59bb0c4c7`, these **host-only** GitHub Actions workflows completed/success on both macOS15 and Ubuntu24.04:

- [B1 source + host CI 42601246155](https://github.com/night-outlook/hybridclr_demo/actions/runs/42601246155): 55 focused Python source/identity/preparer tests and real test-only native probe C++11 host builds.
- [B1 four-repository exact source CI 42601246125](https://github.com/night-outlook/hybridclr_demo/actions/runs/42601246125): all four actual Git checkouts, exact 14 source files, 47 native VM source paths and negative gates.
- [Captured-generic A2/current source host CI 42601246174](https://github.com/night-outlook/hybridclr_demo/actions/runs/42601246174): source, managed/host and batch controller contracts.

The native fork [B1 host C++11/17 CI 42598105952](https://github.com/night-outlook/il2cpp_plus/actions/runs/42598105952) remains pinned at actual native commit `a0209bf4285db3f0d0fc66d8817578235438cef4`.

These are accurately scoped **historical pre-oneuse-10 source receipts**, never a waiver of the final-demo-SHA job-status predicate above. This handoff/documentation commit advances the demo SHA; Local must require a **fresh successful exact-final-demo-HEAD** run of both B1 primary workflows with job-level status and source identities. Existing c6b7 host outcomes and all historical PASS/FAIL/Blocked snapshots remain immutable. No Unity Player run is claimed by Primary.

## 10. New oneuse-11 source-admission proof required

Before invoking the coordinator, **fresh** GitHub Actions at the final pushed demo SHA must have *three distinct dual-OS workflows / six job-level completed/success*, including the new `r03-ir-b1-shared-mac-runner-admission.yml` actual composed Mac/runner/inner-host path. The separate native B1 C++11/17 workflow must also remain completed/success at its pinned native SHA. Record exact job IDs, attempt numbers, remote SHA and time; a previous green 14/47 constituent source gate is NOT enough. If any workflow is absent, stale, in progress, failed, skipped or job-level inconsistent, stop before the runner, preserve results and return `PrerequisiteBlocked/NotRun`. Recheck both newly named oneuse-11 roots are absent and obtain **new** independent >=25 GiB/60-sec capacity evidence; original oneuse-10 capacity observations do not transfer. Local oneuse-11 must run at most once and stop for Primary fixes on any non-trivial failure.
