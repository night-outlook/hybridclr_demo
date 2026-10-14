# Native bounded diagnostics V2 — component implementation c271

**Owner: Primary Implementation. Scope: native capture/codec and single-sidecar sink. Not installed in the Unity Player. No Local runtime assignment.** This advances Stage B of SNAP01_BOUNDED_DESIGN_f8a2; it does not claim complete producer/envelope/engine integration.

## Source authority and immutable empirical result

Review baseline is demo `718c43345fc931ffbd07f0a7f9ebd93fd1f6062e`, a descendant of actual SNAP-01 evidence publication `64da7e51d740d4816907a63864b9c006a9db4b85`. All branches are `codex/assembly-shadow-r01b-h1`; fixed other pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, IL2CPP+ `0f72078711d4786dac2666c9017d952d857dd041`.

Read the original Local-owned reports and `local-validation-snap01-82bd` checkpoint. Actual first rejection was slot14/finalDiagnostics, reason9, 262144-byte capacity, scanned prefix262145, in all three ON cases. Exact full actual lengths remain Unavailable. SNAP-01 collection is EvidenceCollected; runtime is FAIL/ReturnRequired, 18 cells14Passed/4Failed, three buildsPassed, five Players, engine51213 actual uncapped reports/500ms and exit71. No historical fact is reclassified, no SNAP-01/N retry is performed, no partial data is accepted.

The preceding 331078-byte synthetic slot15 example is NOT the empirical slot14 content. This component's synthetic large fields are also not actual Player measurements.

## Added native implementation

Files are isolated under `Tools/AssemblyShadow/R03IR/NativeDiagnostics/` and currently have no include or call from production Player/native runtime:

- `BoundedDiagnosticsV2.h`: a single-owner, once-only frozen byte capture; incremental SHA256; UTF-8 validation; exact reference-compatible frame encoder and first-failure record.
- `PosixDiagnosticFile.h`: a descriptor-relative, exclusive, no-follow sidecar sink with original inode/device/owner/size/permissions checks, short-write handling, bounded EINTR retries, file fsync/close and directory fsync. It accepts an already authenticated directory descriptor, not an arbitrary pathname.
- `native_codec_driver.cpp`, `posix_sink_driver.cpp`, `test_native_v2.py`: host-only drivers, syscall fault adapters and Python/native cross-checks. Their file reads/vectors/formatting are NOT terminal production code.

The native codec matches the published Python design reference exactly; reference Git blob `0866b07f758a20284d2a5d5d933b2be577b20b50` is checked before any test. The reference itself is unchanged.

## Resource and state contract

The physical frame maximum stays65536. The original inline-text maximum stays262144; the versioned pooled limit remains4194304 encoded envelope+artifact bytes, with3932160 assigned to artifact and262144 to the envelope reserve. Canonical inline content remains<=258048. The capture accounts for both40-byte section headers,72-byte global header,38-byte frame headers,40-byte footer and every payload byte BEFORE copying. Field14 then15 are required exactly once; null and empty are distinct. A total overflow, invalid UTF8, out-of-order/missing/duplicate section, call after freeze or callback re-entry latches the first error and cannot return a descriptor.

Complete native fields can exceed the old physical text slot only by using the explicit V2 frame format, never by increasing that slot. Tests include600011-byte general JSON plus420012-byte execution JSON and an exact3932160-byte artifact, preserving every input byte. One additional byte beyond the admitted artifact budget fails before output. The implementation cannot make arbitrary-size input fit; resource exhaustion stays failure.

The codec does not allocate during Prepare/Begin/Append/End/Freeze/Encode. The test arms a global C++ new/new[] failure during the complete capture/encoding path. Caller allocation of the Capture object and test-driver input vectors occurs before that interval. This checks C++ heap allocation, not every allocator in an external producer/kernel/library. Native capture size was3932320 bytes on the Linux test ABI. Capture plus reserved inline space and a2048-byte stack reserve is4192416 bytes; the POSIX sink is also included in a compile-time total bound. This is component storage accounting, NOT whole-process RSS or all native producer metadata. Actual call-stack and runtime allocator behavior require later integration measurement.

Capture copies all supplied bytes into its owned arena before Freeze; later source-buffer mutation cannot change output. The caller must obtain a coherent complete general/execution snapshot under the real runtime locks and release those locks before Encode performs I/O. The codec does not invent that snapshot or synchronize arbitrary concurrent producers. A single owner may transfer the frozen object to the I/O owner only after external synchronization. No thread-sanitizer or concurrent-producer proof is claimed.

## Authentication, filesystem and commit boundary

SHA256 binds exact bytes at the field, context-bound frame, prefix/footer and full-artifact levels. The prepared identity digest and inline-envelope digest come from the trusted canonical run/PID/request/build/source owner. The codec does not authenticate self-reported input identity; hashes are not signatures. The existing external source/app/PID/request joins and evidence seal remain mandatory.

The native POSIX sink creates only the fixed leaf `diagnostics.v2` relative to a retained approved directory descriptor, using exclusive/no-follow/close-on-exec flags and0600 permissions. The approved directory must be owned by the current effective UID and have0700 permissions. It refuses existing files/symlinks and never deletes failed artifacts to retry. It checks regular-file identity, original inode/device/UID, one link, expected access permissions and exact counted size. Detected substitution, removal, link creation or permission change fails. A private directory and external ownership gate are prerequisites; this is not a defense against an actor that can rewrite all same-user source/raw/hash receipts.

The sink is not a path walker: opening and authenticating the entire root ancestry, proving its stable pathname/ownership and preserving that root across the run remain the integration caller's job. Metadata checks do not make concurrent malicious same-user writes impossible. Final consumer hashes and original manifest bindings still must be checked. Kernel fsync success requests the relevant persistence barriers; these tests are not power-loss hardware proofs.

An encode result is published only after the complete footer and sink finish succeed. File or directory fsync, close or write failure yields no descriptor even if a complete-looking file remains. Close(EINTR) is not retried because the descriptor may have been released; the result remains failure and cleanup is best-effort, not clean-teardown acceptance. Partial files are retained. A successful sidecar alone does not commit the envelope: the separate small-envelope exclusive creation/fsync and authoritative two-artifact consumer acceptance are still pending.

## Tests and exact scope

The component suite contains32 Python test methods. It runs both strict C++17 and ASan/UBSan native binaries and uses actual filesystem operations for successful writes/identity checks, with explicit injectable syscall errors. The first local Linux run passed32 tests and122 compiler/process records. Inside one test, the native driver covers24 state/I/O/ownership scenarios per profile, including all ten write-fault positions; these are NOT counted as extra unique Python tests.

Coverage includes independent hashlib vectors (including million-a and padding boundaries); exact native/Python wire equality; complete oversized logical fields; exact budget and budget+1; null/empty; UTF8 split across frames and one-byte appends; embedded NUL; invalid/overlong/surrogate UTF8; source mutation after freeze; corruption/truncation/trailing data; PID replay and inline substitution; immutable first error; missing/duplicate slots; sink re-entry; all-or-nothing descriptor; real exclusive output, symlink/occupied preservation, hardlink/replacement/mode/deletion, zero/short writes, bounded EINTR, file/directory sync failure and ambiguous close. Complete Failed semantic views remain Failed; duplicate-key/nonfinite diagnostic JSON remains rejected by the unchanged reference consumer.

Source-bound cross-platform workflow: `.github/workflows/r03-native-bounded-v2.yml`. Current run metadata, audited artifact identities and final results are recorded in `EVIDENCE.json`, not inferred from queued/running jobs. Actual compiled source/header blobs are included in the evidence manifest. This suite does NOT run Unity, the official full IL2CPP translation matrix, the actual diagnostic producers, GC/finalizers, native scheduler or current Local custody checks.

## Remaining Primary implementation, in order

1. Refactor BOTH real serializers around their shared native sink operations, preserving exact original property/escape/value/class inventories. Implement coherent preallocated capture and bind the trusted identity/inline snapshot; compare legacy and streaming producer bytes. Do not marshal giant managed strings and call it bounded capture.
2. Integrate the safely admitted root descriptors, single sidecar and small V2 envelope commit; implement resource-admitted consumer dispatch to the UNCHANGED semantic predicates. Historical V1 remains intact; a V2 view must never impersonate V1 raw. Test both artifact failures, corruption, missing descriptor and full actual producer output, then run official managed/native compilation.
3. Establish the exact Unity2022.3.62f2 StandaloneOSX scheduler/lifecycle-owner adapter before enabling engine terminal containment. The existing reference coordinator has no such owner. Current public PlayerLoopSystem documentation allows native pointers only from the engine's default loop and says not to modify native parameters; this is not permission to install an invented callback pointer. Native rendering/plugin examples are not proof of full scheduler/finalizer ownership. Keep the engine policy unchanged and Unsupported/Unbound where no reviewed interface exists.
4. Only after integration/review/compilation gates can Primary issue a new exact-source Local cycle. No repeated known-failing SNAP-01 or N attempt, no count cap/coalescing/sleep/default return/finalizer disabling, and no relaxation of500ms/1..64 actual report bounds. A separate emergency process shutdown cannot be labeled a passed full-window experiment.

Current owner remains Primary Implementation. No nontrivial repair is assigned to Local, no new runtime roots are allocated, and no acceptance flag changes. Strict historical custody remainsBlocked; independent R03 full-stage FAIL/re-reviewNotRun; all original checkpoint outcomes preserved; no H2/X02/M08A/PureInterpreter expansion/Human Review Gate.
