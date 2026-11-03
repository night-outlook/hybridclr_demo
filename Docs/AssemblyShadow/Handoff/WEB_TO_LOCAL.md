# Primary Implementation → Local Validation — CONDITIONAL R03 oneuse-H (2026-11-03 UTC)

**Authority / stop:** New single-use **H** R03 current-native validation is authorized **only** after the exact-source CI, Mac read-only admission, disk decision, original-S custody, unused-root, and source/remote identity checks below all pass. Latest G is **consumed / FAIL**: two ON real Unity C++11 builds and three ON sidecar/post-poison Players Passed; OFF compile Failed (incomplete Il2CppException/Il2CppString), engine Player failed with **51,865** reports/500ms and one quit request, OFF Player and official135 installed audit Blocked. G, F, E and all prior historical checkpoints stay immutable. H is not a G retry.

Design and review: [Design](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/DESIGN.md), [Plan](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/PLAN.md), [Primary review](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/PRIMARY_SOURCE_REVIEW.md).

## 1. Exact repositories, paths, commits

All four worktrees must be clean at branch `codex/assembly-shadow-r01b-h1`, canonical `night-outlook` origins and full pushed HEADs matching the closing Primary handoff. These are expected paths, not substitutes for independent Git verification:

| Repository | Local checkout | Required latest pushed branch commit |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final 40-digit demo HEAD in closing Primary prompt (and exact H CI `head_sha`) |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `cdd3f7bc671880052e4f55ae4c1cd75b99a603e1` |

Historical G native `2c899ece8cf241887b14040bab0a73d7c854d2bf`, E `ca0aab8e0abcbcb60a1532223d9e1bdb0aea86c4`, D `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`, original-S native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` and historical R03 native `74dbdbea80d83923863303bd2b2c0a87f36541b1` must never be conflated. `R03/source-pins.json` is immutable. New H source gate checks **11** exact candidate files including `R03EngineFrameDispatcher.cs` and `R03TerminalPlayer.cs`; VM manifest fixes **45** native source paths with actual `AssemblyShadowEngineReportingProbe.cpp` at new H blob, hence **135** installed source pairs required from three *successful* native builds. No old apps, or modified SDK/compiler flags, may stand in for these source pins.

## 2. Mandatory read order, current repair, prior preservation

Read `Docs/AssemblyShadow/README.md`, this `Handoff/WEB_TO_LOCAL.md`, `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, then G `History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-g/{README.md,LOCAL_RESULT.json,RUNTIME_FINDINGS.json}` and relevant original actual build/Player/sidecar logs. Preserve G's two good ON builds/three ON sidecars, raw failed engine 51,865 count, failed OFF compiler log, bound64/500ms and all sealed evidence. Preserve F BLOCKED/root absent, E FAIL/three empty snapshots/51,211 count, all older A–D and independent R03 FAIL outcomes. Do not overwrite/rerun a protected attempt.

Primary H changes: (a) self-contained native object types for probe ON and feature OFF, feature-gated native V2 writer; (b) a real Unity `MonoBehaviour.Update` test-only frame-dispatched unhandled sentinel after original native failure; (c) native normal C-runtime-exit `atexit` witness, strict full V2 raw/status/CRC/schema evidence and failure-only 500-ms watchdog `std::_Exit(71)`; (d) full native-source C++11 OFF/ON mock compilation, old-V1/false-watchdog/phase/source negatives, 11-file/45-VM pinned source gates. No callback sleeps, fabricated JSON, counter caps, relaxed terminal guard or automatic retries. A source-host PASS is not actual SDK/Unity/Player acceptance. A normal process exit is not complete Unity-managed Shutdown.

## 3. Nine mandatory exact-final-commit CI workflows — before Mac H invocation

All **nine** named `.github/workflows/` files must have **fresh `push` runs**, each with `head_sha` equal to the **exact full final demo commit in the closing Primary prompt**; every required **macOS and Ubuntu** job must be `completed/success`. Do not accept ancestor/source-equivalent builds. Names:
`r03-ir-current-native-local-cycle-host.yml`,
`r03-ir-current-native-source-only.yml`,
`r03-ir-current-native-vm-delta-source-only.yml`,
`r03-ir-current-native-oracle-source-only.yml`,
`r03-ir-fixture.yml`,
`r03-ir-host.yml`,
`r03-k-host-contracts.yml`,
`r03-k-sourcecheck.yml`,
`r03-l-contracts.yml`.

All nine watch this `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` in `push.paths`. Inspect *actual run IDs, final head SHAs, trigger path and both job details/logs*, not just YAML trigger assertions. The combined suite must run genuine C++11 full-TU `engine_owner_quit_contracts.py` OFF and ON tests, including wrong-header negative, normal-exit positive and watchdog failure negative, plus source/sidecar and actual checked-out nine-workflow trigger tests. The real `r03-ir-fixture.yml` must compile pinned .NET8 generator and verify original-S versus independent IR target; none of this is Unity Player evidence. Failed/queued/missing/wrong SHA/OS = **NO-GO, coordinator0, no H root; return precise blocker to Primary**.

## 4. Read-only Mac admission, H-only capacity decision, unused output

Retain original-S sparse detached worktree at `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`, pinned `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, protected tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`, 16,978 protected files; do not re-sparsify/recreate/clean it. Verify real Unity **2022.3.62f2 arm64** `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, .NET SDK8.0.318/runtime8.0.21, Git, Python, clang++, lipo, exact installed SDK and clean source/remote pins; no competing Unity/IL2CPP owned processes. No SDK installation, BuildSettings/compiler switches or old binaries as substitutes.

**Explicit Primary H-only disk GO/NO-GO:** Hard20GiB and advisory40GiB are unchanged. G's immediate pre-dispatch free42,526,572,544 bytes and post-run free39,722,037,248 bytes imply ~2.612GiB *observed* consumption, not an H guarantee. This new and separate H-only exception permits `36.0 <= free < 40.0 GiB` **only if BOTH** a fresh source-pinned read-only Mac admission and a second independent sample *immediately before coordinator* show at least **36.0 GiB** on the *actual H output parent volume*, all exact CI/source/SDK/custody/root gates Passed. Record bytes, GiB, timestamps, device/volume and explicit advisory exception. At >=40GiB normal advisory GO; **below36GiB NO-GO** even if hard20 passes. Do not lower the 20/40 policy, clean caches or protected roots, assume same-APFS sibling adds capacity, or reuse G-only39GiB waiver. If another constraint fails, no root creation. This discretionary H-only exception expires unused or consumed with H; no subsequent cycle inherits it.

Choose **only if physically canonical, disjoint and nonexistent**:
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261102-oneuse-H`.
Never pre-create, auto-suffix or reuse; F root remains absent and G root consumed.

Set:
```bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261102-oneuse-H
DEMO_COMMIT=<the-exact-40-digit-final-pushed-demo-commit-in-closing-handoff>
```

Read-only standalone prerequisite (must return `PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun`, **before** any H root is created):
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```
Retain preflight and independent capacity receipts **outside** the H root and all preserved historical roots; foreign-cwd unassisted standalone Python CLI must import correctly without PYTHONPATH or PYTHONHOME. If any test fails, record PrerequisiteBlocked, no coordinator and no Unity, stop.

## 5. Exactly ONE H ten-stage coordinator

Only after all of section3 and section4 PASS and after the second independent immediately-pre-dispatch capacity check, execute **once** at the new absent H root:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

This existing source-pinned ten-stage coordinator exercises five source/host suites, native host diagnostics, authentic original-S nine-part 15,713-member / 90-cell historical archive and 59 historical process joins, three **fresh** ON release/ON debug/OFF release actual Unity IL2CPP C++11 builds, five real Players (baseline release/debug, type release, OFF control, engine-unhandled), then official **135** installed native VM source pairs **only if all three builds and prerequisite stages pass**. Preserve every first real compiler error, BuildReport, Bee graph, actual SDK installed hashes, each Player's request/run nonce/PID/argv/raw/sidecar/log, original semantic verifiers and failure receipts; no cleanup or forced downstream pass.

Specific checks: OFF must build and preserve ordinary canary1→2; three ON post-poison Players must reject reflection/delegate/AOT method entry and leave canary and private field unchanged with stable original recovery and **complete** general sidecar. Engine must genuinely originate from `Update` phase75 before native failure; exact sentinel reaches native sink; real unbounded `completedReports` 1..64 within max500ms; one owner quit call; authentic original recovery terminal code13; native **normal process exit `atexit` with durable V2 report**, not just ownerQuitRequested, not a watchdog; no managed callback admitted after terminal. Failed/missing raw, nonzero exit, `WatchdogForcedExit`, timeout or count>64 = Failed with unaltered evidence. A normal C exit is NOT proof of a complete Unity-managed shutdown/atomic epoch.

## 6. Evidence, publication, gate

Publish new **additive** H checkpoint under `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-h/`, update **Local-owned** `Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`, preserve G and all earlier evidence unchanged, bind exact command/source/SDK/run/output hashes and true Passed/Failed/Blocked/NotRun classification. Seal/verify source/published evidence and four remote branch heads; commit/push. Any nontrivial native/architecture repair belongs to Primary; no unreviewed Local refactor, no H retry. Return to Primary and STOP.

Even if all ten focused stages pass, state is at most `FocusedEvidenceReadyForIndependentReview`. Original Oct8 independent R03 FAIL/High IR-R03-01/02, D1=A/D2=A, incomplete P1/P2/E0/E1/P3, broader shutdown and whole-VM epoch obligations remain; `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate automatically.
