# SNAP-01 continuation — inactive native bounded V2 codec

**Owner: Primary Implementation. Date: 2026-10-14. Result: P1a codec/capture-sink component implemented and host-tested; full Player and engine integration NOT completed. No Local runtime authorization.**

## 1. Source authority and immutable failure

The latest original Local result is SNAP-01 publication `64da7e51d740d4816907a63864b9c006a9db4b85`. Its collectionResult=EvidenceCollected and semanticBatchResult=ReturnRequired remain unchanged:18 cells14 Passed/4 Failed, three builds and five Players; OFF and all three Bee observations Passed. Three ON first failures are slot14/finalDiagnostics, reason9, limit262144, scanned prefix262145, errno0, empty raw and exit2. Exact full lengths and complete semantics are Unavailable. Engine actually completed51213 uncapped reports in500ms, exit71. No new runtime attempt occurred in this continuation.

Start from [Local report](../../../../../Handoff/LOCAL_VALIDATION.md), [return](../../../../../Handoff/RETURN_TO_WEB.md), the immutable `local-validation-snap01-82bd` checkpoint, and [existing bounded design](../SNAP01_BOUNDED_DESIGN_f8a2/LOSSLESS_DIAGNOSTICS_DESIGN.md). The repository had already advanced to `09720df7692598561d59722753a0e58e08e276ad` with Docs/reference design. That concurrent work was retained. No old unpublished snapshot archive was overlaid on current source.

Other repositories remain exactly HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, native `0f72078711d4786dac2666c9017d952d857dd041`, branch `codex/assembly-shadow-r01b-h1`. Canonical local owners remain `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`. No other repository or original source pin changes are part of this component.

## 2. Concrete implementation, not a new runtime verdict

Three new files under `Tools/AssemblyShadow/R03IR/bounded_v2/` implement and exercise an **inactive, standalone** component:

- `BoundedDiagnosticsV2.h`: allocation-free C++17 framing, incremental SHA-256, UTF-8 checks, single-owner fixed-storage capture sink and one-shot encoder.
- `native_driver.cpp`: host-only native driver, explicit caller buffer preparation, allocation tripwire, injected sink failures and state controls.
- `run_tests.py`: native/Python cross-implementation comparisons, original pinned reference decode, negative controls and complete command/source evidence.

The header is not included by the current Player, native overlay, existing serializer, build scripts or runtime verifier. It cannot yet make SNAP-01 emit a complete record. It does not control any Unity callback, GC/finalizer, engine clock or report counter. The original V1 schema/predicates and all production guards are untouched.

### Wire and resource contract preserved

The native encoder emits the exact existing `R03BoundedDiagnosticsV2` format. It retains <=65536-byte frame payloads, <=3932160-byte complete diagnostic artifact and the existing262144-byte envelope reserve, giving the unchanged4194304-byte total encoded allowance. Original V1 per-text capacity262144 is not increased. Two large logical diagnostic fields may use multiple frames within the shared aggregate; overflow remains a deterministic failure, never truncation, compression or omitted census data.

Identity and canonical-inline digests, ordered slots14/15, null-vs-empty tag, full field lengths/hashes, contextual frame hashes, prefix commit footer and whole-artifact digest match the Python reference **byte-for-byte**. UTF-8 may cross a frame boundary; embedded NUL is preserved. Invalid UTF-8, reordered/duplicate/missing sections, corruption, replayed context, incomplete sink output and extra bytes do not produce an accepted complete stream.

The immutable Python reference remains Git blob `0866b07f758a20284d2a5d5d933b2be577b20b50`. It is an independent format model in these tests, not an installed production consumer or a guarantee of bounded Python object memory. Native hashes provide content integrity and context binding, not signatures. The trusted expected run/PID/request/build/source context and descriptor must still come from authenticated upstream evidence, not from an untrusted artifact's own header.

### Capture and concurrency contracts

`Capture` uses caller-owned, preallocated storage. It permits exactly slot14 then15, checks wire-size and capacity before each append, validates complete UTF-8 at each end, and exposes views only after both sections are frozen. It implements a serializer sink, **not** the actual VM census or a lock-consistent general/execution serializer. The caller must prepare buffers while healthy, keep addresses valid, provide one owner and prevent concurrent mutation. It must not hold metadata/transaction locks across file I/O.

`Encoder` owns fixed-size hash/state only and uses a caller-provided65536-byte scratch buffer. It rejects source/scratch overlap, short scratch, null input with nonzero length, reuse and synchronous sink re-entry. Field views and context digests are copied; copied frame bytes are hashed again to detect a synchronous changed-input fault before emitting a successful footer/receipt. This test is **not a claim to make a C++ concurrent data race safe**. Both Capture and Encoder are noncopyable and single-owner.

On tested64-bit layouts Encoder=144 bytes, Capture=72 and SHA state=112. The capture buffer, frame scratch, caller input, output transaction and parser allocations are separate. The4MiB encoded bound is **not a process-RSS or complete integration memory bound**. Host test vectors/files allocate before the protected codec interval; replacing operator new is an allocation regression tripwire, not proof about every allocator, arbitrary callback or future VM integration.

`Receipt.complete` means all wire bytes were accepted by the provided synchronous sink. It does **not** prove fsync, durable close, envelope publication or semantic success. A sink may retain partial failed bytes, which must remain failed evidence. Exact first error is latched; later calls do not erase it. Production file race/admission/durability handling still belongs to P2.

## 3. Source-bound verification and retained failures

Final tested component source is `8120ca91c0c762b8b29f703f087ab1bfdaf0f532` on `codex/snap-v2-native-20261014-c2e8`. Header blob `174766c40235216d8c954107dd5e026116a510fa`; driver `66d799bc6f21f9219d388c2b945a9eea388c1dae`; test runner `7ba066393f5b9a608155902ef600f6575f78f79d`. Final publication may add only documentation/evidence beyond that exact tested component. The branch is a development/CI source, not a Local execution assignment.

[CI38529319047](https://github.com/night-outlook/hybridclr_demo/actions/runs/38529319047) passed all **20 unique cases in each strict and ASan/UBSan profile** on Linux Clang, Linux GCC and macOS Apple Clang. This is the same20 cases repeated across6 profiles, not120 independent cases. Each compiler/OS combination produced164 compiler/process records,492 in total. The tests include three independent SHA vectors, exact aggregate limit and one-byte overflow, two full JSON fields each above262144, multiple UTF-8/hash/frame boundaries, deterministic random vectors, every sink-failure position, scratch alias/null/short inputs, capture state, reuse, input mutation, replay, footer/corruption/trailing data and preservation of a synthetic Failed report through reference hydration.

All three original artifact ZIP digests, **2445 declared manifest files**,492 command stdout/stderr pairs, current source hashes and complete test logs were independently authenticated. [EVIDENCE.json](EVIDENCE.json) records exact identities. [RETAINED_LOGS.json](RETAINED_LOGS.json) preserves all six original test logs losslessly; [restore_logs.py](restore_logs.py) verifies and restores them into a new external directory. Binary artifacts are retention-limited and are not copied into Git. A native negative outcome is asserted in the host driver/receipt; successful host process exit must not be presented as a successful Unity failure case.

Earlier [CI38528871444](https://github.com/night-outlook/hybridclr_demo/actions/runs/38528871444) passed both Linux jobs and macOS strict cases, but macOS sanitized processes refused `detect_leaks=1` before executing code: `AddressSanitizer: detect_leaks is not supported on this platform.` This failure remains recorded. The correction changes **only test subprocess sanitizer options**: Apple LeakSanitizer is explicitly Unavailable, ASan/UBSan remain enabled, and Linux LeakSanitizer remains enabled. No tests are skipped and no production flags are altered. Final artifacts record actual options per command. An earlier local GCC indentation diagnostic was fixed without weakening `-Werror`; it preceded the published code.

## 4. Remaining Primary implementation gates

This delivers **P1a: native codec/capture-sink component**, not all of P1/P2 in the [implementation plan](../SNAP01_BOUNDED_DESIGN_f8a2/IMPLEMENTATION_PLAN.md).

1. **Actual producers and coherent capture:** refactor the existing general/execution serializers through one common sink without changing field/order/escaping/census; preserve byte equivalence to legacy output. Bind synchronization, exact class/name lifetime, preallocated capture and separately measured peak memory. The component's synthetic large documents are not SNAP-01's missing actual bytes.
2. **Prearmed durable file transaction:** directory-descriptor/no-follow identity, exclusive deterministic sidecar, bounded writes, fsync/close failure handling, exact envelope/sidecar commit relationship and retained partial failure records. A codec receipt is not a durable file receipt.
3. **Current transport/consumer integration:** integrate actual native producers and C# declarations with explicit V2 selection; validate authenticated envelope/identity/artifact before exposing a tagged semantic view to unchanged original predicates. Preserve V1 historical verification, whole diagnostic bytes and all failed statuses. Hard parser memory/time and hostile-schema controls require separate implementation.
4. **E0/E1 engine ownership:** obtain and review a legitimate native scheduler owner safe point, queue-drain and required maintenance contract for Unity2022.3.62f2 StandaloneOSX. The inspected public PlayerLoopSystem documentation requires native values copied from the default loop, while the standard native plugin interface documents rendering callbacks; those facts do not establish the necessary terminal scheduler/lifecycle contract. Do not fabricate such capability from a nonzero pointer or a managed callback. Implement only a source/vendor-supported adapter with truthful acknowledgement and maintenance/restart evidence. No broad no-op returns, sleeps, caps/coalescing, finalizer suppression or changed500ms/1..64 acceptance.
5. **Integrated compilation/review and eventual Local cycle:** coherent four-source tuple, all original host/official managed55-native SDK checks and terminal/file-path review, then a separately pinned Local handoff. There is no runtime root or new Local attempt designation from this delivery.

Relevant official capability references: https://docs.unity3d.com/2022.3/Documentation/ScriptReference/LowLevel.PlayerLoopSystem.html and https://docs.unity3d.com/2022.3/Documentation/Manual/NativePluginInterface.html . These are capability boundaries, not evidence of a tested scheduler adapter.

## 5. Publication and safety boundary

Connector bootstrap verified all four canonical repositories and expected refs. Disposable demo smoke branch `codex/connector-smoke-bounded-native-20261014-c2e8`, commit `09cb670fd2cf8b01edf1986f39bcf71d7acd1070`, passed write/readback; it is not product evidence. The branch is retained, not merged. The component branch contains no smoke file. Authoritative publication is a non-forced expected-HEAD update; inspect concurrent changes before any retry.

SNAP-01/N/M/K/I/E remain FAIL, F/H/L blocked, G/J historically scoped Passed. Strict historical S custody remains Blocked:416844 original entries,339367 survivors,77477 missing identities and4 original native roots. No live Local custody or installed SDK scan was done here. Local-owned reports and old checkpoints are unchanged. All acceptance flags false; independent full-stage R03 FAIL/re-review NotRun. No H2/X02/M08A/PureInterpreter expansion or Human Review Gate approval.
