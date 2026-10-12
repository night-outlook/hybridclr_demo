# Primary reconciliation — K failures and L correction

Owner: Primary Implementation. Date: 2026-10-12. Scope: R03 / IR-R03-02. **Source and host/compiler evidence support one separately admitted L Local cycle. No repaired real Player runtime has been observed.**

## Immutable K result

The authoritative Local K publication is `2b5cf60363dc7c895deaad26bdaf7af70cde612a`; execution used demo `e1334d1052dba9ad240a3fa781b751ec5a1d9e9d` and native `0fa7b4fef94062e54f186fda938dd8a3d2304b7e`. [Local report](../../../../../Handoff/LOCAL_VALIDATION.md), [return](../../../../../Handoff/RETURN_TO_WEB.md) and [K checkpoint](../../local-validation-k-after-j-41bc/README.md) retain empirical authority.

K remains **FAIL:18 cells,11 Passed/7 Failed; three builds Passed; five Players launched**. OFF Passed. Three ON semantic snapshots Failed at phase170, before post-poison field/canary/recovery assertions. Healthy controls proved actual42/42,stable2,canary1 and Boolean-reserve/collection mask31. Their snapshot state zeroes are unfilled early-catch defaults, not proof of native state reset. The engine sentinel reached native reporting, but its finalizer-thread unhandled path aborted and raw remained empty. All three Bee observations were Unavailable because two factory lookups returned different processors. Compilers, storage, bounded seal and scoped before/after preservation do not change those failed results. K is consumed and cannot be retried.

## Coordinated implementation reviewed, not overwritten

This continuation found and retained concurrent implementation rather than overlaying another candidate. Native implementation `d6872b25f7208f0f65d33ef6693d985c1cd41074` plus its CI publication is pinned at **`c1a6876a3801a8343123977a0e230558904fd94d`**. The demo helper implementation/pin already existed at `d09c8c23291df10a39308df4fb0563b5b9d579f9`.

### IR-LOCAL-K-SEMANTICS-01: rejection transport

`AssemblyShadowTerminalRejection.h` prepares a physical corlib InvalidOperationException and strong pinned handle while Shadow is Disabled at healthy startup. `RaiseTerminalExecutionRejected` and the outward `FailTypeResolution` path use **Exception::Rethrow** rather than post-terminal exception construction and Raise/PrepareExceptionForThrow. The actual pinned Rethrow body directly throws Il2CppExceptionWrapper. This removes new managed constructor, stack preparation and GC-handle operations from transport; it does not claim that platform C++ exception machinery allocates nothing.

The existing native failure/recovery record remains the first-cause authority. This shared exception does not provide per-throw message/stack provenance. The exact historical exception-construction substep that failed in K is still Unavailable. Actual catchability through the P/Invoke receipt bridge and every original post-poison predicate remain mandatory real L evidence.

### IR-LOCAL-K-ENGINE-02: finalizer/unhandled disposition

`Runtime::UnhandledException` reports **only the exact prepared guard-rejection object** natively in Failed/FailedAfterCommit. Other exceptions, including a different object with the same type/message, retain the original unhandled policy. No arbitrary managed AppDomain handler, finalizer body or business entry is admitted. The existing CallUnhandledExceptionDelegate abort route remains for other exceptions.

The GC/finalizer scheduler and ordinary entry guards are unchanged. A terminally denied finalizer body is still not executed; resource-cleanup effects are not generally qualified by this repair. Reporting is bounded. Actual shared exception lifetime and the engine's prescribed500ms completed report require Local validation. Current disposable Players use native exit, so they do not qualify normal runtime shutdown. Reserve release remains at the existing quiescent shutdown boundary.

### IR-LOCAL-K-BEE-03: actual factory returns

`R03ModuleFactoryLease` temporarily wraps **one original platform-module registry slot** with a forwarding DispatchProxy for the synchronous isolated build. Calls, arguments/ref-out values, returned objects and original exceptions are forwarded. The observer captures the **actual original CreateBuildPostprocessor return**, rather than performing an independent factory lookup. The exact original slot is restored; a concurrent replacement is detected, not overwritten. The unique captured processor carrying the driver must have had no driver when returned.

This is internal Unity-module instrumentation, not a guaranteed public API. It does not replace Bee processors/returned objects, suppress logs or relax `BuildReport.summary.totalErrors == 0`. A .NET8 synthetic internal-interface test is not Unity Mono integration. Actual module/processor assembly identities, counts, unique live driver, bounded nodes and restoration must authenticate on all three Local builds. Missing/unrestored capture remains failed diagnostic evidence independent of product-build status. I's old shared-cache emitter remains Unavailable; K's successful Debug build did not erase I.

## Additional receipt correction authored here

The new Python validator initially accepted a synthetic CapturedForAnalysis receipt without original module/processor types, assembly digests or a captured-processor count. The gap was reproduced synthetically, not asserted as a new Local failure. `bee_observation.py` now requires full manifest/assembly SHA-256 syntax, exact integer schema/counts, nonempty bounded instance types, a captured count consistent with factory calls and no acquisition error, in addition to every prior identity/restoration/bounds check. Local must also match the actual assembly hashes to its SDK inventory; digest syntax alone is not authenticity.

Twelve new controls were added in `test_factory_receipt_binding.py`. The existing positive seed in `test_k_contracts.py` now supplies the required identities, preserving its assertions. These three commits changed no C#, native production source, Player, fixture, compiler, pin or storage rule. **Current Python/test source anchor: `04a3cd93663f9a4e877a5524d9c22ee5a3fe0131`.** Final publication must be source-equivalent to it.

## Verification actually completed

[Completion audit](COMPLETION_AUDIT.json) records exact ZIPs, sources, counts and limits.

The pinned Connector export was downloaded and **2,266 size/SHA-256/Git-blob bindings** authenticated, including selected K raw evidence and complete relevant source. This was not an independent audit of every K archive/seal member.

Official Unity2022.3.62f2 [CI38243672034](https://github.com/night-outlook/hybridclr_demo/actions/runs/38243672034) was independently rechecked: **209 manifest files,56 native command receipts/streams,complete55 syntax configurations,42 owned native source hashes,five successful managed targets and the separate expected-negative control**, plus209 available owned managed input hashes. Unexported vendor-reference bytes remain inventory-bound. Current native/helper/Player compiled bytes are unchanged by our Python addition. **616 repeated vendor Baselib atomic-memory-order warnings remain unsuppressed**, without a harmlessness judgment.

Fresh [CI38262556820](https://github.com/night-outlook/hybridclr_demo/actions/runs/38262556820) at04a3 passed **91 tests on macOS14 and91 on Ubuntu24.04**, including the actual managed factory lease's17 assertions within one synthetic-interface test and12 new receipt cases. The separate sanitized native snapshot also passed. Both original artifact ZIPs, source bindings and log hashes were authenticated. [Lossless log metadata](ci/LOG_STORAGE.json) and [decoder](ci/restore_logs.py) preserve both complete original host logs using one gzip base and an exact one-line delta with independent full-file hashes. Original sanitized logs are retained separately. This is encoding of authenticated raw bytes, not normalization or fabrication.

This Linux container ran seven current native outer invocations successfully: rejection/reporting strict C++17 and ASan/UBSan, actual Object.h access, and engine observer strict/sanitized. The rejection harness uses actual Rethrow/FailTypeResolution/UnhandledException source,4,000 concurrent rejections per configuration and three expected native-abort modes. Reporting retains20,000 stress iterations,18 identity negatives and18 fatal modes per configuration; the unchanged policy passed69 checks. **Metadata/GC/VM dependencies remain mocks**; iteration counts and expected aborts are not thousands of Unity tests. No Unity, real finalizer, Local SDK scan or live Local custody scan ran here.

The concurrent full-host runner corrected its expected count183→203 because twenty scratch tests had been added. It removed no test and reclassified no old failed CI. Local must run current suites without skips, not adjust counts to hide failure.

## Successor and acceptance boundary

The [L procedure](L_BATCH_PROCEDURE.md) combines complete source/host/custody checks, fresh official managed/native compilation and **one18-cell/three-build/five-Player cycle** with actual factory captures. Runtime requires both compiler gates and two independent storage admissions. No sixth Player, retry, cache cleanup, occupied-root reuse, guard waiver or nontrivial Local source change.

K/I/E remain FAIL; F/H prerequisite-blocked; G/J historical compile-only Passed. Strict S custody remains Blocked:416,844 identities,339,367 survivors,77,477 missing and four original native roots. Shared exception/real factory integration, semantic rejection and engine behavior remain candidates until actual L evidence exists. Captured-generic/initializer,IR-R03-01 and broad legacy/performance remain open. Independent full-stageFAIL/re-reviewNotRun; all acceptance flagsfalse; PureInterpreterdisabled; noH2/X02/M08A or Human Review Gate advancement.

Connector smoke readback passed in demo/native on `codex/connector-smoke-l-review-20261012-52d9`, commits `144281010d33365395ec72b67f1e07270786c0d0` / `47ce696d3e2389a3b8576f8b738c404425b2a185`. The demo branch also carries only the pinned source-export workflow. These branches remain because branch deletion is not exposed; neither is a Local execution pin.
