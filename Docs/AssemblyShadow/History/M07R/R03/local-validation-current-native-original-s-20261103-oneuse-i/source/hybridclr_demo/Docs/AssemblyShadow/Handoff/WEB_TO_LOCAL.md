# Primary Implementation → Local Validation — CONDITIONAL R03 oneuse-I (2026-11-03 UTC)

**Authority and stop:** One brand-new, source-pinned R03 **I** cycle is permitted **only** after all exact nine-workflow CI, four-repository Git source/branch/head, read-only Mac/SDK/original-S custody, H preservation, two-source-pinned capacity, and absent I root gates below pass. H is **consumed FAIL** and must never be replayed. The exact final demo commit is the 40-character pushed HEAD in the closing Primary handoff prompt, not any intermediate Primary commit or historical H execution SHA.

Design and independent limits: [I Design](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/DESIGN.md), [I Plan](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/PLAN.md), [Primary source review](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/PRIMARY_SOURCE_REVIEW.md).

## 1. Prior evidence and exact Git pins

H Local actual: three fresh Unity2022.3.62f2 C++11 ON Release/ON Debug/OFF Release builds **Passed**; ON baseline release/debug, ON type and OFF Player **Passed**; genuine engine Player **Failed** (55,656 reports/514ms vs 64/500ms, watchdog exit71, owner quit once/request returned, no normal atexit). Original source demo `3e838edf8995e40058f3bc6c42f071446a0be821`, native `cdd3f7bc671880052e4f55ae4c1cd75b99a603e1`. Publication descendant demo `d49ad3e113b67b300381e6af904ed1d343005e7e`. H original official135 installed-source audit was **Blocked** though Local separately authenticated 135 byte comparisons. H raw engine, failed-command receipt, native logs, build output, sealed archive and all prior G/E/F history must remain byte-identical. Never rewrite H, rerun its original coordinator/Player, or infer acceptance.

All four workspaces must be physically clean Git checkouts of the exact canonical `night-outlook` repo, `codex/assembly-shadow-r01b-h1` branch, and **latest pushed HEAD** matching the closing Primary handoff and GitHub remote:

| Repository | Expected Local path | Latest pushed execution commit |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **final 40-digit demo SHA in closing Primary prompt; exact CI head_sha** |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Original historical S native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, original historical R03 native `74dbdbea80d83923863303bd2b2c0a87f36541b1`, D `e1e5...`, E `ca0...`, G `2c899ece...`, H `cdd3...` and current I native **must not be conflated**. Original `Tools/AssemblyShadow/R03/source-pins.json` is immutable; current source overlay pins exactly **11** candidate source files including `run_terminal_local.py`, both Unity Player fixtures and physical `Runtime.cpp`; `current_native_vm_delta.json` pins **45** changed native VM paths, so official current installed-role parity requires **135** source pairs after three successful builds. Use actual remote Git blob identities, not file names/old SDK copies.

## 2. Mandatory read and preservation order

Read:
1. `Docs/AssemblyShadow/README.md`;
2. this canonical `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`;
3. Local-owned `Handoff/LOCAL_VALIDATION.md`, then `Handoff/RETURN_TO_WEB.md`;
4. H `History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-h/{README.md,LOCAL_RESULT.json,RUNTIME_FINDINGS.json}`, especially original exact Player.log line33–56 and raw1004 bytes;
5. I Design/Plan/Primary source review linked above.

Preserve H's actual engine completedReports=55,656, elapsed514ms, watchdog exit71, original failure13/RestartRequired; previous G 51,865 / E 51,211 counts and their separate evidence, F Blocked/NotRun/root absent, all A–D and original S/failed independent source decisions. Preserve original S sparse detached worktree `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`, HEAD `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, protected Git tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`, 16,978 protected files. No re-sparsify/recreate/gc/prune/clean, no source/SDK alteration or history reset.

## 3. Primary I implementation — exact bounded behavior

`AssemblyShadowTerminalReporting.h`, `Runtime.cpp`, `AssemblyShadowEngineReportingProbe.cpp` now have a **test-only** native owner-lifecycle responder, limited to `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1` and `HYBRIDCLR_R03_RUNTIME_PROBE=1`, after a genuine H-style sentinel, one native Unity owner `Application.Quit(0)` request, original durable recovery and actual state9. It matches exact physical nongeneric static no-parameter `UnityEngine.CoreModule:UnityEngine.Application.Internal_ApplicationWantsToQuit():bool` and `Internal_ApplicationQuit():void` only, returning an already-pinned true Boolean or native void without running managed callbacks, cancellation-token code, reflection, interpreter or class initialization. Other `Runtime::Invoke` calls still hit the unchanged original terminal method/class denial. The native responder is **not** a general production recovery or managed shutdown API.

The existing native V2 raw also includes `ownerWantsToQuitNativeResponses` and `ownerApplicationQuitNativeNotifications` (both must equal1 for focused engine PASS), plus separate exact native-decision stderr markers with `managedBodyExecuted=false`. Original reporter count remains **uncapped real 1..64**, observation **<=500ms** unchanged; original failure13/RestartRequired, one quit request, actual `NativeAtexit` and durable original raw/normal-exit log marker are required. Missing markers, `WatchdogForcedExit`, count>64, timeout, wrong source/method, continued denied Unity callbacks preventing exit, corrupted raw/nonce or false first failure = **Failed**. No counter cap, callback sleep, extra stimuli, log/finalizer suppression or bypass of ordinary terminal guards.

Primary also decouples physical installed-source parity from Player semantic PASS. When **all three actual builds** are successful, the child native batch is source-pinned and **sealed**, and its original results/acceptance=false fields remain, the official 45-file×3-role audit runs independently even if one Player fails. It must authenticate original BuildReports, per-role installed before/after file inventories and all135 hashes. Its `siblingPlayerBatchResult` and `siblingPlayerSemanticsAccepted` must reflect the unchanged Player verdict. **Scoped source parity PASS never upgrades a failed Player or full coordinator.** Missing/failed build or invalid seal/source = parity Blocked or Failed; no forged audit PASS.

No Unity local validation or broad full-Shutdown proof is implied by Primary CI. Even native `NativeAtexit` only establishes scoped C-runtime normal exit, not managed Unity teardown, cancellation token completion, GC/RSS or coherent whole-VM epoch.

## 4. Exact final demo commit — nine mandatory CI workflows before Local I

All **nine** paths below must produce a new `push` run with `head_sha` exactly equal to the **full final pushed demo SHA in closing Primary prompt** and both required **macOS/Ubuntu** jobs `completed/success`; record real run IDs, actual jobs/logs/SHA and source/workflow blob hashes. No ancestor-substitution and no relying only on source trigger tests.

- `r03-ir-current-native-local-cycle-host.yml`
- `r03-ir-current-native-source-only.yml`
- `r03-ir-current-native-vm-delta-source-only.yml`
- `r03-ir-current-native-oracle-source-only.yml`
- `r03-ir-fixture.yml`
- `r03-ir-host.yml`
- `r03-k-host-contracts.yml`
- `r03-k-sourcecheck.yml`
- `r03-l-contracts.yml`

The combined host must compile genuine native-code method-classifier extracted from the new physical header (positive exact AOT signature, wrong method/assembly/return/generic/preterminal/unarmed negatives) and full genuine native reporter TU in both C++11 OFF and ON SDK-like tests, with normal-exit and watchdog-negative raw. Synthetic oracle verifies new V2 owner response/notification counters and unchanged original semantic guards. All nine workflows watch this canonical handoff path for final exact-commit triggers. CI proof is **host only**, no Unity SDK/Player acceptance. Any required missing/pending/failed/cancelled/wrong-head OS job = **NO-GO**: no I output root or Local coordinator, return complete blocker.

## 5. Read-only Mac prerequisite and one-use I capacity admission

Check actual Unity **2022.3.62f2 arm64** at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, real SDK8.0.318/runtime8.0.21, Git/Python/clang++/lipo and clean installed source/SDK pins. No extra Unity/IL2CPP active processes, no SDK/toolchain install and no compiler flag override. The previously trusted DotNetSdk may be exposed through child-process PATH only, as recorded in H; do not substitute another Unity Player version.

**Primary explicit I-only capacity GO/NO-GO:** Fixed minimum20GiB and advisory40GiB are unchanged. H observed immediate 39,287,488,512 bytes (36.589GiB), final 36,140,306,432 bytes (~33.658GiB), difference3,147,182,080 bytes (~2.931GiB), *historical* evidence only. A new one-time I advisory exception is granted **only if BOTH** fresh source-pinned read-only Mac admission and a second *independent immediate pre-coordinator* sample show **>=32.0GiB free on the actual I output-parent volume**, with full CI/source/SDK/original-S/custody and root admission Passed. At32.0..under40GiB explicitly record the exceptional GO, exact bytes/timestamps, device and volume; at>=40GiB ordinary advisory GO. **Below32.0GiB NO-GO** even if hard20 passed, no I root creation. I waiver expires with this one-use cycle; never reinterpret H's prior capacity as fresh admission. No cache/history cleanup/APFS sibling-volume workaround.

Required I root only if canonical, disjoint and absent:
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261103-oneuse-I`.
Never precreate/auto-suffix/reuse. Keep F unused, H consumed and all earlier roots untouched. Preflight stdout/stderr and independent capacity receipts belong **outside** I and historical roots.

Set exactly:
```bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261103-oneuse-I
DEMO_COMMIT=<exact-40-character-final-pushed-demo-commit-in-closing-Primary-prompt>
```

Run only the read-only original source-pinned admission **before I root creation**, require `PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun` and the independent immediate I volume check:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```
If any prerequisite fails, report `PrerequisiteBlocked`, I root absent, coordinator0, Unity0, stop. No Local source edit or "test" root creation.

## 6. Exactly ONE I combined ten-stage coordinator

**Only after all CI, Git and two read-only Mac/capacity gates passed**, invoke the exact existing coordinator ONCE with the **latest final pushed** demo commit:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

Ten stages: source/oracle/VM source/installed-source host, real native host diagnostics, original-S nine-part archive 15,713 members/90 **historical** cells and 59 original process joins (archival scope), three actual new Unity2022 arm64 IL2CPP C++11 builds, five real fresh Players (release/debug baseline, type, OFF, engine), plus source-verified official **135** installed VM pairs when all three real builds and sealed batch exist. Keep actual process/command/PID/run nonce/request hash/source/SDK/build/Editor Bee/Player.log/raw/sidecar/semantic-verifier/normal-exit/wants-quit log/counter evidence and first real errors, including after-effects if engine fails. If any other prerequisite prevents genuine source audit, mark separate audit Blocked instead of running a synthetic pass.

Engine expected: real frame75 and original synthetic type failure13, exact terminal sentinel handled without invoking managed logger/body, single owner native quit, native wants-to-quit true **once**, native quit notification void **once**, unchanged true total report count 1..64 within <=500ms, true normal C runtime `atexit` durable raw and original recovery, 0 exit. Post-poison ordinary method guard and field/canary/first failure witnesses must remain intact; OFF control must work. Any failed Player must retain Failed/NotRun original verifier, regardless independent installed parity outcome.

## 7. Required evidence, publication, review gate and stop

Publish a **new, additive I checkpoint** at `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261103-oneuse-i/`, update Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`. Record all CLI/Unity/SDK/CI/repo/head and output identities, 3 builds, 5 Players, engine counters/flags, separately labeled installed parity 135-pair status, source/old-S archival audits, original exact raw failure if any, scoped seal and independent post-preservation. Commit/push and verify four remote HEADs, preserve original S and A–H exactly, and return to Primary Implementation. Local may apply only bounded immediately verifiable fixes, no architecture/SDK/native refactor. Never retry consumed I or start another milestone automatically.

**Gate remains closed** even if focused I passes: original Oct 8 independent R03 FAIL/High IR-R03-01/02, D1=A/D2=A, incomplete P1/P2/E0/E1/P3 and whole-VM epoch/full managed Shutdown obligations are still open; `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate approval.
