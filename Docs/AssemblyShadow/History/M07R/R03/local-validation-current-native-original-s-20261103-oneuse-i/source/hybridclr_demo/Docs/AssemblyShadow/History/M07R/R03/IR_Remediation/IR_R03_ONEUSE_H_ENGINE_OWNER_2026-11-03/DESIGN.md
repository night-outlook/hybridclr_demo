# R03 oneuse-H return: exact native Unity quit owner decisions (oneuse-I design)

Date: 2026-11-03 UTC. Owner: Primary Implementation. Scope: R03 IR-R03-02 **only**. Not a full R03 gate review.

## 1. Immutable empirical baseline

Local H was run exactly once at `hybridclr_demo@3e838edf8995e40058f3bc6c42f071446a0be821` / `il2cpp_plus@cdd3f7bc671880052e4f55ae4c1cd75b99a603e1`. H's three real Unity2022.3.62f2 C++11 IL2CPP builds (ON Release/Debug, OFF Release) Passed. Four Player cases (ON baseline release/debug, ON type-resolution, OFF control) Passed. The real engine Player PID82637 failed: `R03IREngineReportingV2` raw has 55,656 real completed native reports, 514 ms observed versus unchanged 500-ms bound, watchdog exit71, `ownerQuitRequested=true`, `ownerQuitNativeCalls=1`, `ownerQuitReturned=true`, `normalExitHookObserved=false`, `witnessExitMode=WatchdogForcedExit`, terminal code13/RestartRequired. Genuine phase75 Update, native sentinel and initial reporter were observed. Its original verifier is Failed; official installed VM audit was Blocked although independent read-only 135 successful-build-role source comparisons matched. Sealing and preservation passed only their scoped contracts. H is consumed and may NOT be rerun.

Source evidence: `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261102-oneuse-h/{README.md,LOCAL_RESULT.json,RUNTIME_FINDINGS.json}`, committed original `batch/current-native/players/IR-R03-02-release-engine/{raw.json,Player.log.utf8.json,verification.json}`. Local H Player.log:36 exact native sentinel, :37 owner quit request, :56 `[R03TerminalDenied]` for `UnityEngine.Application.Internal_ApplicationWantsToQuit`; many subsequent denied unrelated Unity callbacks. The native request returning is not owner-loop completion.

## 2. Unity 2022.3-specific contract

The **actual UnityCsReference tag `2022.3.62f2`** `Runtime/Export/Application/Application.cs` (blob `5df54a6f3cba20670a68d740d6f1dcddf42e4c1b`) defines private static `bool Internal_ApplicationWantsToQuit()` and `void Internal_ApplicationQuit()` in `UnityEngine.Application`, physical assembly `UnityEngine.CoreModule`. The former returns `true` to continue quitting, or `false` when a subscriber denies; the latter invokes cancellation-token and quitting-event managed work. Official 2022.3 documentation explicitly states that an attempt to quit can be cancelled by a false wants-to-quit decision: https://docs.unity.cn/Documentation/ScriptReference/Application-wantsToQuit.html . The H runtime denial is a *strong causal hypothesis*, not proof of exactly how Unity's closed native owner handles a thrown callback.

A durable FailedAfterCommit execution policy cannot allow managed `wantsToQuit` subscribers, cancellation-token code, or normal `quitting` handlers. Blindly allowing these managed bodies would violate original terminal guards. A single `Application.Quit(0)` native request alone was empirically insufficient in both G and H.

## 3. New test-only native owner decision — selected design

At the existing `Runtime::Invoke` last common boundary, add one **HYBRIDCLR_R03_RUNTIME_PROBE-only** native responder before the usual terminal reporter and ordinary method/class guards. The responder is eligible only when:
- `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1` and `HYBRIDCLR_R03_RUNTIME_PROBE=1` (production/OFF code cannot take this path).
- The exact preallocated H-style unhandled sentinel has already matched, the one native owner `Quit(0)` request was recorded, and the **original immutable terminal recovery was captured** while the witness remains armed and the failure-only writer is still open.
- `AssemblyShadow::GetState` confirms `FailedAfterCommit`.
- Physical MethodInfo is nongeneric, noninflated, static, zero-argument, owned by the stable, noncandidate/nonshadow `UnityEngine.CoreModule` AOT image, and has the exact `UnityEngine.Application` namespace/class.
- Its **exact signature** is either `Internal_ApplicationWantsToQuit(): bool` or `Internal_ApplicationQuit(): void` (no aliases or name-only checks).

The wants-to-quit method returns the existing **pinned, healthy-preallocated physical true Boolean**, as a native owner decision only. The void quit notification returns `nullptr` without invoking managed cancellation-token or user event bodies. No extra class initialization, allocation, reflection resolution, interpreter dispatch, managed callback, general exception conversion, or altered return for any other Unity method. No production recovery path or configuration is changed.

Each exact native decision increases its own **uncapped** observer counter, logs its initial exact-method native-only evidence, and is preserved in the existing V2 engine raw as `ownerWantsToQuitNativeResponses` and `ownerApplicationQuitNativeNotifications`. The oracle requires exactly one of each and the corresponding two distinct log markers. In the normal Unity exit, actual count must remain 1..64 and actual elapsed <=500ms. The failure-only watchdog still writes an accurate `WatchdogForcedExit` raw, exits nonzero and may never claim success, and the original terminal code13/recovery remains unchanged. No counter limit, sleeps, log suppression or extra Local stimuli are introduced.

**Scope limitation:** This native decision deliberately does not run `Internal_ApplicationQuit`'s managed token-cancellation or quitting callbacks. That is appropriate to the strict terminal no-managed-execution experiment but means *even a normal C `atexit` and real quit decision do not prove full managed Unity shutdown*. Full Unity/VM cleanup, finalizers, GC/RSS qualification and coherent whole-VM epoch remain separate unresolved obligations. Unexpected lifecycle callbacks still hit the original guard and remain observable; they are never reclassified as harmless.

## 4. Verifiable source and host coverage

Primary changed `il2cpp_plus/libil2cpp/vm/{AssemblyShadowTerminalReporting.h,Runtime.cpp,AssemblyShadowEngineReportingProbe.cpp}` only. Exact VM native delta remains 45 changed VM paths vs immutable old R03 `74db...` and must match three actual installed IL2CPP source trees (135 pairs). The existing candidate source gate still pins 11 exact files, including `run_terminal_local.py` at its new blob.

New `native_owner_decision_contracts.py` compiles the **actual extracted classifier/response** in C++11 with adversarial MethodInfo and assembly mocks: positive wants/quit, unarmed and preterminal denial, wrong name/type/signature/owner/assembly/generic/candidate, and no unrelated bypass. Existing `engine_owner_quit_contracts.py` compiles the full probe TU OFF/ON using minimal fake SDK headers and separately executes normal-exit vs watchdog-negative source-host processes with exact counters. These tests do not reproduce Unity's closed native execution, but they fail closed if source contracts regress.

The combined two-OS CI runs both scripts, negative oracles, source/VM gates, and historical tests at the identical final demo SHA. The one-use Local coordinator additionally performs both exact native-owner tests within native host diagnostics before Unity.

## 5. Independent build parity despite Player failure

A second Primary correctness repair separates the **build-source-parity** proposition from **Player semantic success**:
- The coordinator may execute the official installed-source audit after the Player stage returns `ReturnRequired` **only** if an exact pinned, `sealStatus=Passed`, nonaccepting batch has three unique successful build cells and three actual passing BuildReports.
- The installed-source verifier still reopens each canonical build receipt, source pin, complete physical before/after VM inventory and current source to authenticate all 45 per role.
- The new parity report independently records `siblingPlayerBatchResult` and `siblingPlayerSemanticsAccepted`; a 135-pair parity PASS **cannot** turn a failed Player or outer coordinator into PASS.
- Missing/failed builds, invalid seal, wrong repo metadata, reused source, absent signed build receipts or role mismatch block/fail parity rather than fabricate success.
- This repairs a separate latent mismatch where the prior audit compared the full repository record to a reduced map omitting `schemaVersion`, `phase`, `branch` and `runtimeAcceptance`, which would have blocked even a successful sealed batch.

H's original official audit remains Blocked; its independent diagnostic135 pairs do not become official historic acceptance retroactively.

## 6. One-use I storage and stop policy

An entirely new `I` root is allowed only after new exact source pins, nine actual same-final-commit dual-OS CI PASSes, clean four checkouts, read-only Mac/source/SDK/retained original-S custody checks, no conflicting Unity/IL2CPP owners, a physically absent new I root and **two current capacity measurements**. H's immediate admission was 39,287,488,512 bytes (~36.589GiB); H after-preservation was 36,140,306,432 bytes (~33.658GiB), a measured 3,147,182,080-byte (~2.931GiB) delta, *not a guaranteed future usage bound*. The fixed hard20GiB and advisory40GiB policy remains unchanged. Primary grants **I-only conditional advisory exception** for fresh preflight and immediately-pre-coordinator samples **both >=32.0GiB on the actual output-parent volume**, independently logged with bytes, timestamps, identity and explicit discretionary exception. Below32.0GiB = NO-GO, no new root; at/above40GiB ordinary GO. No cache/history cleanup, symlink workaround, APFS sibling-volume assumption, SDK install, altered C++ flags, or old-root reuse. The I exception expires after I; it does not weaken future gates.

Expected I output `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261103-oneuse-I`, always initially absent. Run the existing ten-stage coordinator **once** with a new final 40-character pushed demo SHA. Preserve source/SDK/build/Player/native owner-decision/actual counter/real watchdog/parity/raw outputs for independent after-audit. Even all focused I results passing means only `FocusedEvidenceReadyForIndependentReview`—never independent R03 acceptance, runtime qualification or Human Review Gate approval.

R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; PureInterpreter disabled. Original independent High IR-R03-01/02 and broader P1/P2/E0/E1/P3 remain open. No H2/M08A/X02/SNAP-01.
