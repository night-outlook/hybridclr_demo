# R03 oneuse-G return — OFF compile and engine-owner lifecycle design (H candidate)

Date: 2026-11-03 UTC. Owner: Primary Implementation. Scope: R03 IR-R03-02 only.

## Immutable G finding and authority

At exact G execution `hybridclr_demo@6364dbc795eabc8cfbb7409fcfe2b64a30c12863` and `il2cpp_plus@2c899ece8cf241887b14040bab0a73d7c854d2bf`, all nine exact-commit CI workflows and prerequisite Mac admission passed. Two ON Unity 2022.3.62f2 C++11 native builds and three ON post-poison Players passed their bounded evidence; the OFF C++11 build failed on incomplete `Il2CppException`/`Il2CppString` in `AssemblyShadowEngineReportingProbe.cpp`; the engine Player returned 71 with 51,865 completed native reports in 500 ms (bound 64) despite one owner quit request. OFF Player and official 135 installed pairs were blocked. No G rerun or modification of G or older checkpoints.

## D1 — repair actual OFF native include boundary

Under `HYBRIDCLR_R03_RUNTIME_PROBE=1`, the reporter translation unit needs complete `Il2CppException`/`Il2CppString` definitions regardless of `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW`. It now directly includes `il2cpp-object-internals.h`; the feature-specific recovery/exit-report writer remains behind `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1`. No change to feature-OFF runtime behavior, reporting guards, compiler standard or Unity SDK.

Regression: compile the *entire* reporter under C++11 with feature-OFF and probe-ON using deliberately incomplete SDK-like types except in `il2cpp-object-internals.h`; removing that include must fail. This is a **host mock** and cannot establish real installed SDK compilation. Local H must compile all three actual roles with Unity's C++11 toolchain, preserve Bee and BuildReport failures, and then launch the OFF control.

## D2 — engine owner lifecycle provenance, not synthetic success

G's native `UnityEngine.Application::Quit(System.Int32)` request occurred within `BeforeSceneLoad`, where Unity had not yet established a running frame loop. An icall entry and a single once-counter did not mean Unity actually terminated: many later guarded engine callbacks produced the recorded cascade. H prepares the exact native sentinel during healthy initialization, installs a test-only `R03EngineFrameDispatcher` and raises it exactly once from a genuine `MonoBehaviour.Update` frame. The same actual production native type-resolution failure is emitted immediately before rethrowing the already-allocated managed sentinel. No callback is admitted after poison, no guard is weakened, no extra stimuli are introduced.

The native test-only observer records the first sentinel timestamp, unbounded real reporting count, original immutable recovery JSON and one owner quit request. It installs a C-runtime `atexit` report callback before the test. A *normal* process exit writes `R03IREngineReportingV2` with `normalExitHookObserved=true` and `witnessExitMode=NativeAtexit`; its durable raw receipt is independently joined with an explicit stderr marker. A watchdog at the original 500-ms observation interval can only write `WatchdogForcedExit` and exit nonzero (71); never synthesize zero or a PASS. Genuine raw report count must remain between 1 and 64, original 500-ms window unchanged. The verifier additionally requires a real phase-75 Update-frame checkpoint, authentic native reporter sentinel and recovery code 13/RestartRequired.

**Interpretation:** `atexit` proves normal C process termination and prevents the former `std::_Exit(0)` test oracle from inventing success. It does **not** prove a complete Unity-managed Shutdown, atomic whole-VM epoch, finalizer/GC/RSS qualification, or wider lifecycle. A normal termination within 500 ms is a strict focused test, not a production guarantee. If Unity still dispatches callbacks after quit or exits only via watchdog, H must fail and preserve raw timing/counters; Primary must use that new evidence to decide an additional lifecycle design. No count caps, callback sleeps, logger or finalizer suppression, bypass or automatic retry.

## D3 — bounded exact-source one-use H

Use the existing unchanged ten-stage R03 combined coordinator on one unused H output only, after all nine exact-final-demo-SHA CI workflows succeed on macOS and Ubuntu and after two fresh Mac read-only capacity samples. R03 source gate now binds **11** exact source files (including the new frame fixture); native source delta remains **45** VM paths; three actual installed source trees must match **135** byte pairs after all three successful builds. The historical original-S 15 fixtures, original nine-part archive/90 historical cells, and 59 process joins retain their original independent provenance, not re-execution claims.

H-only disk decision: unchanged hard **20 GiB**, advisory **40 GiB**. G's 39.606-GiB initial and approx 36.996-GiB post-cycle samples imply about **2.612 GiB observed** consumption, not a guaranteed future bound. Primary grants a narrow **conditional H-only advisory exception** at **>=36.0 GiB** for both fresh read-only admission and immediately pre-dispatch samples on the actual output parent volume, with exact source/CI/SDK/root preservation all passed. Between 36.0 and 40.0 GiB explicitly record the waiver, bytes, timestamps and device; at or above 40.0 GiB normal GO. Below 36.0 GiB NO-GO and no root creation; never lower the hard/advisory policy or clean protected history. This exception is not transferable to later cycles.

## Gate

G remains FAIL, F remains BLOCKED, E remains FAIL, all earlier checkpoints immutable. Even a focused H PASS is only evidence for independent R03 re-review; old High IR-R03-01/02 and wider P1/P2/E0/E1/P3 obligations remain. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`; PureInterpreter disabled. No H2, M08A, X02, SNAP-01, or Human Review Gate automatically.
