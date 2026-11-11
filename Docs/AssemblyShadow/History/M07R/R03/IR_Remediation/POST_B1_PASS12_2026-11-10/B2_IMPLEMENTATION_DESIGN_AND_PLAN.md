# R03 B2 — integrate native bounded V2 transport in the isolated Player

## Current Primary stage: bounded observed cross-image metadata owner discovery (2026-11-11 UTC)

**Implemented in native, inactive:** [cross-image AOT owner implementation/source review](B2_BOUNDED_CROSS_IMAGE_AOT_OWNER_IMPLEMENTATION.md), `il2cpp_plus@cfb33d58432b05f3d28052dfb88677a0561f6c93`. The matched-observed-class image inventory is built by a first physical iterator pass, then a second pass formats owned rows against that inventory. Both occur under one original `g_MetadataLock` and initial-session metadata Reader. Limits: 64 observed physical images, 8,192 TypeDefs/image, 65,536 aggregate owner lookups, 16 arguments/key and 4,096 bytes/key. A canonical cross-image generic TypeDef argument is admitted only when its owner image also has an independently matched observed class. Duplicates, missing/ambiguous owner, class disappearance, encoded index and exceeded capacity remain typed failures.

**Source/mock tests:** [native 42983247910](https://github.com/night-outlook/il2cpp_plus/actions/runs/42983247910) **4/4 Mac/Linux C++11/17 PASS**, Release/Debug + strict/ASan-UBSan; 16 mock host executions, 592 typed scenarios, 6,336 assertions. [20-native/3-demo source identity 42983166781](https://github.com/night-outlook/hybridclr_demo/actions/runs/42983166781) **2/2 PASS**. No Unity/IL2CPP Player build or file-transport test occurred. All product and Human Review Gate acceptance flags stay false.

**Earliest next uncompleted Primary task:** a truly complete physical AOT image-owner source for otherwise unobserved argument images, without violating the original metadata/assembly lock and lifecycle ordering; then additional composite TypeKey shapes and full original V1 nonempty execution field15 parity. Only after full field14/15 terminal-safe source, native V2 descriptor transport and external receipt authentication may Local be given a new one-use source-pinned batch. The current V2 slot14/15 schema is unchanged and `WEB_TO_LOCAL` remains CLOSED / NO EXECUTION.

---

## Current B2 Primary source step (2026-11-11 UTC)

**Implemented, source/mock verified:** [same-image GENERICINST code and review](B2_SAME_IMAGE_GENERICINST_IMPLEMENTATION_AND_REVIEW.md) at native `20a57e58098e3476dad5459f04f9fc730c3848c1`. The actual inactive VM capture can now format and own simple/nested physical AOT TypeDef keys, generic **definition** arities, and a constructed `GENERICINST` with one or more concrete same-image physical definition arguments (max 16, max 4096 output bytes). It uses the existing metadata admission, authentic physical enumerator, bounded per-image owner proof and original frozen execution/R02 writer. 31 scenarios per mock process with original C++11/C++17 Mac/Linux Release/Debug strict/sanitized coverage passed, plus an independent pure bounded composer and exact source admission gate.

**Not an end-to-end B2:** Cross-image generic arguments, nested constructed generics, arrays, pointers, qualifiers, open VAR/MVAR and Unicode assembly-name folding remain unsupported. The source has no postterminal admission; full original V1 execution JSON equality for arbitrary actual Unity classes is not yet demonstrated. General `finalDiagnostics`/slot14 and full `finalExecutionDiagnostics`/slot15, native V2 descriptor file writer/envelope, externally authentic receipt, coherent VM epoch and R03 qualification remain incomplete. No Local build or new Player candidate is authorized.

**Earliest next Primary-owned source stage:** implement **cross-image physical metadata TypeDef owner inventory under the same metadata lifetime contract** (without introducing unstable class pointer dereference) and expand canonical argument shapes through verified source adapters. Add strict byte-reference tests against the pinned legacy `AssemblyShadowTypeKey.cpp` grammar and adversarial source/index/lifetime checks. Then prove complete nonempty field15 and terminal-safe field14 semantics before B2 writer integration. All old B1 receipts remain immutable; `WEB_TO_LOCAL` is CLOSED / NO EXECUTION.

---

## Current Primary increment: owned nonempty class formatting now host-verified

Source-only implementation through [B2 owned execution review](B2_OWNED_NONEMPTY_EXECUTION_IMPLEMENTATION.md) has provided an allocation-free fixed-size TypeKey formatter for an **explicitly restricted metadata-definition subset**, immutable source-unverified nonempty rows (original registry-slot order, copied flags/bytes), and adapters that feed the **actual** `AssemblyShadowExecutionSerializer` and `AssemblyShadowFrozenExecutionRecord` with a **synthetic** typed R02 snapshot. Four Mac/Linux C++11/C++17 workflows passed strict and ASan/UBSan profiles, **32 real host processes / 2,520 assertions, zero protected allocations**. Code remains isolated in `hybridclr_demo/Tools/AssemblyShadow/R03IR/NativeDiagnostics`; no Unity Player or native fork VM code was changed by this increment.

**Not closed:** This cannot yet read physical classes from the VM, prove class-pointer lifetime or fully represent arbitrary generic/array/qualified/unicode assembly TypeKeys. The original full V2 fields still require complete source semantics: slot14 `finalDiagnostics` and slot15 `finalExecutionDiagnostics`. The new row staging is a *consumer of externally authenticated source*, not itself an authenticator. Real native `GetExecutionDiagnosticsJson` and `TryCaptureBoundedEmptyExecutionLive` remain unchanged. **Never** activate V2 transport using only synthetic rows or reduced B1 first-error facts.

**Next code milestone (Primary only):** implement and source-review a VM-owned, fail-closed class producer that binds process-lifetime registration witness to an actual physical metadata callback and original initial-session metadata Reader, copies each class's original flags, verifies genuine metadata declaration ancestry and full canonical TypeKey parity for each admitted shape, and rejects unsupported/changed source before any frozen record exposure. Only then validate complete nonempty output against original V1 formatting with real R02 counter values; follow with terminal-safe general field14 capture and integrated descriptor writer. No new Local run is authorized.

---

## B2-0 source-admission result and stop boundary (2026-11-10)

The new [B2 exact eight-native-file readiness gate](B2_VM_SOURCE_READINESS_GATE.md) passed its **read-only source verification** and 12 negative regressions on both macOS and Ubuntu at [CI 42793741078](https://github.com/night-outlook/hybridclr_demo/actions/runs/42793741078). The output is explicitly `readyForNativeV2FieldCapture=false`: even with B1 real Player PASS and 376 native V2 host tests, the existing VM cannot safely expose complete `finalExecutionDiagnostics` for nonzero observed classes, nor prove complete postterminal `finalDiagnostics` parity. Therefore B2-1 runtime writer integration must not begin until the real full-field source is available.

**Chosen next bounded Primary task:** complete owned canonical execution TypeKey capture and full nonempty class-row source, with a lifetime proof under the original metadata Reader and class registry ownership. Require a source-exact, byte-equivalent V1 execution JSON comparison in class-empty AND nonempty, generic/non-generic cases; failure must invalidate source and never substitute display names or a B1 summary. Then address general final field parity and terminal semantics before transport. No Local Execution Authority exists yet.

---

## 0. Source-review addendum (2026-11-10)

Read the source-anchored [B2-0 findings](B2_SOURCE_REVIEW.md) **before any integration code**. The normative V2 reference explicitly assigns **slot14 = `finalDiagnostics`** and **slot15 = `finalExecutionDiagnostics`**. These are the original full diagnostics payloads, **not the B1 first-error record**. Current `AssemblyShadow::GetDiagnosticsJson/GetExecutionDiagnosticsJson` are allocationful and contain metadata reads across separate synchronization regimes; the bounded P1 general/empty execution capture APIs are explicitly inactive/incomplete.

**Blocking source order:** first prove byte-equivalent complete bounded sources for both fields under a legitimate metadata/lifetime contract, or explicitly design a separately versioned reduced schema and obtain the appropriate review. Only then may B2-1..B2-3 produce a compatible V2 artifact. Do **not** populate final diagnostics with B1 text, optimistic nulls or partial P1 data under the existing wire schema.

The [host-only C++11/C++17 source gate](../../../../../../../.github/workflows/r03-ir-b2-compiler-compat-source.yml) is now **4/4 passed** after focused source compatibility corrections. The [full dual-OS strict/sanitized wire+POSIX host matrix](../../../../../../../.github/workflows/r03-ir-b2-host-cxx11-cxx17.yml) is also **4/4 passed**, totaling 376 real host tests with no failures/skips. [Exact RED→GREEN commits and raw CI jobs](B2_CPP11_COMPATIBILITY_REMEDIATION.md). These are **not** Unity SDK compile/link or proof of the live VM V2 producer. The original B1 evidence and controls remain immutable. The original B1 oneuse-12 source, local evidence and native V1 controls remain immutable.

---

Date: 2026-11-10 UTC. Owner: Primary Implementation. **Design and executable work plan, not a claim of implemented B2 code.** B1 was authenticated by the consumed oneuse-12 focused Local PASS; see [Primary reconciliation](PRIMARY_EVIDENCE_RECONCILIATION.md). B2 **Player/source-producer integration has not begun**; only bounded host compiler compatibility and its focused test infrastructure have been implemented. Do not run Unity or hand work to Local until the source gates below are satisfied.

## 1. Objective, retained boundary and architecture

Integrate the existing real, fixed-storage native first-error B1 record with the already host-verified `BoundedDiagnosticsV2.h` codec and `PosixDiagnosticTransaction.h` filesystem transaction inside **only** the isolated R03 test Player. Produce genuinely authored, independently authenticated `diagnostics.v2.bin` and `envelope.v2.json` from a real VM B1 event while leaving V1 behavior, normal application builds and Original-S evidence untouched. An emission is *not* `wholeVmEpoch` proof or full R03 acceptance.

Current source at the B1 executed tuple:
- `il2cpp_plus/libil2cpp/vm/AssemblyShadowFirstFailureV2.h`: actual immutable process-lifetime CAS `Empty/Writing/Frozen/Invalid` source (4096 UTF-8 byte limit); `AssemblyShadow::FirstFailureV2Status/TryReadFirstFailureV2` are read-only accessors.
- `hybridclr_demo/Tools/AssemblyShadow/R03IR/PlayerProject/R03FirstErrorB1Probe.cpp`: existing `R03_IRB1_Open/Seal` test-only preopened V1-comparison witness; **keep it independently runnable** as a regression control.
- `Tools/AssemblyShadow/R03IR/bounded_v2/BoundedDiagnosticsV2.h`: fixed-storage `Capture` and `Encoder`, ordered field14/15, bounded SHA256 framing, no owned filesystem or VM source semantics.
- `Tools/AssemblyShadow/R03IR/bounded_v2/PosixDiagnosticTransaction.h`: descriptor-relative `Prepare/AppendArtifact/FinishArtifact/CommitEnvelope`, persistent identity/readback/fsync checks; owner-controlled fresh directory and external proof are required.
- `bounded_v2/transaction_reader.py`: fail-closed native-file reader requiring an **independently authenticated** success receipt, `NativeBoundedSnapshotV2` envelope, exact file identity, source and artifact binding. This is not a runtime acceptance oracle.

**Important integration risk:** The codec is documented and host-tested as a C++17 component, while the real oneuse-12 Unity Bee IL2CPP native lump compiled with `-std=c++11`. **Compatibility is NotProven, not presumed failed.** A C++11 official-SDK-or-equivalent source compatibility gate is required before installing any new source into that lump. If adapting the component is necessary, preserve wire bytes and all existing strict/sanitized host contracts; do not unilaterally change Unity C++ flags or introduce global operator overrides.

## 2. Non-negotiable source, identity and safety invariants

1. **Healthy-time admission:** Independently admit a new absent, canonical, owner-controlled `0700` directory, device/inode and four Git source SHA tuple, actual Unity/SDK and build UUID/hash, request runId/caseId/nonce, DLL SHA/MVID and actual future PID. Prepare all fixed buffers, filesystem descriptors and scratch *before the first possible terminal event*. No reopening old oneuse roots, no arbitrary terminal-path allocation or managed callbacks to construct a reason.
2. **Canonical real first event:** Read only `AssemblyShadow::FirstFailureV2Status/TryReadFirstFailureV2` after the actual VM producer; distinguish healthy `Empty` from terminal `Frozen` and permanently `Invalid`. Frozen error19/origin2 and guard15/origin1 must preserve the exact reason bytes and reason length already proven in oneuse-12. Later failures must not replace the first event. A malformed/too-long first reason is `Invalid`, never truncated, retried or replaced.
3. **Field semantics:** Use **the already specified R03 V2 field14/15 schema** and real authenticated source data. Map each field explicitly to the VM producer/version; document whether it is null/empty/unavailable. Do not silently populate field14/15 with generic B1 text if the source schema means something else. Do not infer complete class/metadata/GC state from one frozen B1 record. The VM-snapshot producer and transport must remain separable and auditable.
4. **Single owner, no reentry:** `Capture`, `Encoder` and `PosixDiagnosticTransaction` are noncopyable, not thread-safe; run them under one test-only owner with a one-way state machine. A concurrent or second attempt must fail closed, preserving the original receipt and V1 record. All scratch and raw views stay valid until `Encoder` finishes; no pointer alias or changing capture.
5. **Exact file publication:** The authentically admitted physical directory is never followed through aliases. Preserve `O_EXCL/O_NOFOLLOW`, device/inode/owner/mode and readback before and after `fsync`, artifact-first then authenticated envelope-last order, exact SHA256/byte counts, no duplicate finalize or conflicting side effects. Treat partial artifacts as **Failed**. No separate file can be accepted without the independently authenticated receipt.
6. **Truthful envelope:** `reportTransport=NativeBoundedSnapshotV2` and `diagnosticArtifact` must bind actual size/hash and complete producer/request/PID/fixture/build/source identity; the reader's `expected_identity` comes from externally authenticated receipts, never only from self-asserted JSON. Encode non-finite/invalid JSON and UTF-8 as explicit failure, not null substitution.
7. **No accidental activation or acceptance:** Keep source under `R03IR` and compile only in the new isolated composite / `HYBRIDCLR_R03_RUNTIME_PROBE` path. Preserve original V1 and focused B1 tests. `runtimeAcceptance/R03Accepted/H2Passed/ReadyForHumanReviewGate/qualificationApproved/nativeV2TransportImplemented` stay false until individually proven. Even a real V2 artifact leaves `wholeVmEpoch=NotProven` absent the separately reviewed B3 barrier.

## 3. Phased implementation (Primary-owned changes)

### B2-0. Source/ABI inventory and detailed review — first unfinished step

Read the four source modules and all direct callers at exact four-repo pinned commits. Produce a table for each existing field14/15 producer and schema, required VM locks/reader lifetime and its meaningful `unavailable` state. Confirm the real compiler mode and overlay installation roster from the published oneuse-12 Bee command. Audit C++11 vs C++17 constructs and POSIX/macOS header semantics; add C++11 compilation negative/positive matrix with the *same* effective build flags, no silent compiler upgrade. Review original SNAP-01 V2 field schema and current `transaction_reader.py` before choosing envelope identities. **Stop if schema or lifetime source cannot be made explicit.**

Deliverable: source-anchored `B2_SOURCE_REVIEW.md`, exact Git blob inventory, selected primary architecture decisions and a minimal compiler/ABI fixture.

### B2-1. Isolated healthy-time native preparation

Add a new test-only native V2 transport unit under `Tools/AssemblyShadow/R03IR/PlayerProject` or a dedicated sibling folder, never under production `libil2cpp/vm` as a host driver. Wire it into **only** the authenticated isolated composite via `prepare_captured_generic_sources.py`. Add explicit `HYBRIDCLR_R03_RUNTIME_PROBE` and Shadow gates. Use a new stateful open/preparation entry before `BeginTransaction` / `CommitTransaction`, admitted root identity and external run/build/fixture metadata, exclusively reserved descriptors, fixed scratch and a fail-closed first-use marker.

Validate normal-build inertness, absence of global `new/delete` and exact installed/linked file roster. Keep `R03_IRB1_*`, `R03_IRW_*` and physical `R03_IRG_*` exports unchanged.

### B2-2. Real frozen source and bounded binary capture

Build a producer adapter that translates **authenticated real** VM field14/15 source snapshots into complete, immutable UTF-8 FieldViews, with exact code/origin/first-reason mappings and a clear empty/invalid/unavailable policy. Feed the existing `Capture/Encoder` into `PosixDiagnosticTransaction::ArtifactSink` through a separate, correctly owned sink adapter; preserve exact frame/inline/text limits and flush semantics. Reject an invalid first error, unexpected source revision, change during capture, buffer overflow, resource limits, alias, reentry and incomplete sink. Do not call the mutable allocationful `GetRecoveryInfoJson` to reconstruct the first event after poison.

### B2-3. Authenticated envelope + independent receipt reader

Compose a bounded canonical JSON envelope **without terminal-path allocations**, independently matched inline digest, source/fixture/PID/nonce/build identity and the artifact size/digest from the completed encoder; `FinishArtifact` then `CommitEnvelope` once. Persist an external immutable transaction receipt with literal admitted directory/file identity, before/after file hash evidence and exact success/failure state. Extend the strict Python consumer by **additive** V2-specific verification; never replace existing V1 or B1 consumer, never let producer-supplied hashes authenticate themselves.

### B2-4. Host tests, native source CI and independent Primary review

Require dual-OS source/C++ compiler jobs (Linux and macOS, strict and sanitizers) with **actual** C++11 coverage matching the Unity compile mode. Tests must exercise healthy Empty + terminal initializer19 + physical guard15 and adversarial changes: invalid/4097-byte reason, embedded bad UTF-8, wrong source/PID/dll/MVID/build identity, wrong field slot or null flag, reused root, file symlink/alias/ancestor swap, wrong device/inode, partial or EINTR write/read, content mutation, fsync/close failure, duplicate commit, reentrant encoder, concurrency, allocation tripwire and wrong first-winner. Ensure positive round-trip byte-for-byte V2 frame and strict `transaction_reader.py` decode *only with externally pinned identity*. Record raw compiler and test commands, generated source hashes, CI exact source HEAD, regression negatives.

Independent reviewer must inspect design → plan → implementation → source/host tests before any Local execution authority is issued. Any unimplemented source/lifetime/receipt field remains a blocker, not a waived test.

### B2-5. New conditional Local Validation (later, not yet authorized)

Only after B2-0 through B2-4 are source-complete and reviewed, publish a **new** `Handoff/WEB_TO_LOCAL.md` with all four exact latest pushed commits; fresh independent macOS/SDK/Original-S/CI/2×>=25GiB >=60s same-volume admission and three or more **never-used** absent roots. Plan one source-authenticated real Unity2022.3.62f2 macOS arm64 IL2CPP ON/Release build with bounded Player scenario roster including control, initializer19 and physical guard15, original V1+B1 comparisons, **new real** V2 artifact/envelope/root/source/PID/fixture/readback joins, native installed/linked roster and B2 strict/sanitized host negative suite, and a regular-only product seal. Preserve all raw outputs and returned failures. Local may make only bounded environmental edits; source/architecture fixes return to Primary.

B2 Local empirical success must be reported as `FocusedNativeV2TransportValidated_NotWholeVmEpochOrR03Acceptance` (or equivalent truthful bounded label), not R03/H2/Human Review Gate acceptance.

## 4. Separate B3 / review boundary

B2 demonstrates an actual bounded per-event native V2 artifact; it does **not** supply an all-VM atomic metadata/class/execution/shutdown epoch, source-complete original S compiler+object+Player join, GC/RSS/managed shutdown proof or RC/P/E qualification. These are separately scoped **B3 and later** tasks under the original B plan. Preserve historical `IR-R03-01/02`, independently reviewed full-stage FAIL and permanently unavailable roots. Do not enter H2, M08A, X02, SNAP-01 or mark a Human Review Gate accepted.

## 5. Current decision/status

**B1 focus accepted as empirical oneuse-12 PASS; B2-0 is the earliest incomplete Primary Implementation step.** This document fixes an executable design path, not a source implementation or a new Local run. Existing `WEB_TO_LOCAL.md` must remain **CLOSED / NO EXECUTION** until the B2 source implementation and pre-handoff gates have actually passed.
