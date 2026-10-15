# E0 engine-owner capability review — Unity2022.3.62f2 StandaloneOSX

**Disposition: Blocked (capability not established).** This is a read-only capability assessment, not a fabricated scheduling adapter, not Human Review Gate approval, and not evidence of a Unity Player run.

## Required native capability

After the real first FailedAfterCommit transition, the existing IR-R03-02 engine witness must observe a full original 500ms window and **1–64 actual, uncapped native completed reports**, unchanged logger count1→1 and recovery/GC/sentinel predicates, while safely preventing arbitrary later managed business dispatch. The integration must continue required native engine/GC/finalizer/service maintenance, account for in-flight and queued callback draining, and provide authenticated owner-thread safe-point and lifecycle/restart receipts. The last SNAP-01 real test instead produced 51,213 completed reports/500ms and exit71, with callbacks including ordinary Unity update/rendering and Gen2GcCallback.Finalize sites. No provenance authorizes treating one callback class as the only source.

## Public API evidence and limits

- Unity2022.3 PlayerLoopSystem documented API: https://docs.unity.cn/ScriptReference/LowLevel.PlayerLoopSystem.html — the public managed loop representation permits custom managed updateDelegate; built-in native updateFunction and loopConditionFunction must be copied from GetDefaultPlayerLoop and **must not be modified**. It provides no documented native engine owner acknowledgement, global callback drain or GC/finalizer maintenance disposition.
- Unity low-level native plugin interface: https://docs.unity.cn/Manual/NativePluginInterface.html — UnityPluginLoad/UnityPluginUnload and IUnityGraphics offer plugin/interface and rendering-device callbacks. These callbacks are **not** a documented general Player scheduler ownership, stop-the-world or all-dispatch drain contract.
- Unity application quit / managed PlayerLoop customization are not equivalent to a verified synchronous native safe point after managed business execution has already become terminal. Neither API can be asserted to satisfy the above unchanged predicate from its public contract alone.

These public descriptions do **not** prove that no Unity internal or licensed source-level interface exists. They prove only that the needed contract is **not established** by the public APIs examined. No unofficial function-address inference, changing built-in native PlayerLoop function pointers, synthetic ReadyForRestart state, broad no-op Runtime::Invoke, report cap/coalescing, finalizer suppression, sleep or early exit is admissible.

## Unproven requirements (source/receipt needed)

| Requirement | Evidence status |
|---|---|
| Unity engine scheduler owner thread, safe-point registration and entry/ack | Unavailable |
| All relevant managed callback queue ownership and in-flight drain | Unavailable |
| Native engine service, GC and finalizer continuity after terminal | Unavailable |
| Idempotent one-shot wakeup without managed callback after terminal | Unavailable |
| Source-linked Unity2022.3.62f2 StandaloneOSX arm64 ABI and SDK overlay | Unavailable |
| Native restart/teardown signal with separately authenticated next-process identity | Unavailable |
| Actual original 500ms/1–64 uncapped witness with full semantic PASS | Failed (51,213 reports) |

## Implementation routes (selection is **not** delegated to Local)

**A. Supported source-level Unity engine integration — preferred prerequisite.** Obtain pinned Unity2022.3.62f2 native engine source/build integration or a vendor-supported explicit scheduler/maintenance API. Independently review declarations, ownership, lock/lifetime and scheduling boundaries. Implement an adapter from a **documented, real** safe point and required maintenance/shutdown path; then compile and measure the original witness unchanged. Native code that only references a symbol or executes a callback without proving ownership/drain is insufficient.

**B. No matching supported engine integration available — explicit Blocked decision.** Preserve the existing FAIL and Human Review Gate stop. A different product/runtime acceptance contract could only be proposed in a *separate* design decision with human approval and new independent evidence; it cannot retroactively convert SNAP-01 or weaken the required 500ms predicates.

## Next admissible verification

Primary Implementation should collect the exact vendor/engine declarations and call-site ownership contract in a separate source-bound document before writing E1. An isolated native host model may test state transitions but never counts as Unity scheduler closure. Only after a reviewed real adapter, coherent diagnostics and authenticated V2 semantic path may a new **fresh, explicitly authorized** Unity/Player batch be published. Seven previously unused test roots must not be named or consumed now.

Current acceptance remains R03Accepted=false, H2Passed=false, qualificationApproved=false and ReadyForHumanReviewGate=false. PureInterpreter expansion and H2/X02/M08A remain prohibited.
