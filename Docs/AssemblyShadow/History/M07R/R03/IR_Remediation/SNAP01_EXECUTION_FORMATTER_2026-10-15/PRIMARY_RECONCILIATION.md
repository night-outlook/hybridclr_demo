# R03 Primary continuation — execution diagnostic formatter and host-only batch

**Owner:** Primary Implementation. **Date:** 2026-10-15. **Scope:** native JSON formatting, host diagnostics, source-bound preflight preparation; **not** a completed SNAP-01 repair or a runtime handoff.

## 1. Source and evidence authority

The preceding published source state is demo 8c9fade8c2e276b38287e60d39c9d7d68628ddb2, HybridCLR 4b2774b066cfc6afd77a8c8aded6bda7ea574f55, package 948c0e3b4f8891481301770115e8ba4945eea6de, native 87aedc1248141d7438d82d53521aadaac22c45ae. All use codex/assembly-shadow-r01b-h1. The present native source anchor after the formatter/CI publication is **fc0d3565ecc5c9d1a31520a26ff3f9fda25bc98f**; the final demo Docs commit is resolved from the remote branch, not from a self-referential SHA in its own contents.

SNAP-01 remains **FAIL/ReturnRequired**: 18 cells, 14 Passed/4 Failed. Three real ON snapshots failed at original V1 text slot14 finalDiagnostics, with *observed prefix* 262145 above bound262144; the actual complete byte length is **Unavailable**. The engine test remains 51,213 uncapped reports in500ms, exit71. Collected failure diagnostics do not change semantic outcomes. Original strict S historical custody is Blocked (416844 identities /339367 preserved /77477 missing, four original native roots Missing). R03 acceptance and all Human Review Gate flags remain false.

## 2. Implementation in this cycle

Native **libil2cpp/vm/AssemblyShadowExecutionSerializer.h** is a pure, typed, VM-independent formatter with Header, ClassRow, Begin, AppendClass, EndClasses. It reuses AssemblyShadowDiagnosticWriter.h quoted-string formatting so the same field order and control-byte escaping work for legacy std::ostringstream and caller-owned bounded Writer output. It preserves V1 execution JSON schema/key order, boolean and integer representations, including the r02 suffix added by the caller.

The real enabled **AssemblyShadow::GetExecutionDiagnosticsJson** in AssemblyShadow.cpp now uses this shared formatter to write its previously collected header/class observations. The disabled feature path is unchanged. Physical metadata collection, exception reporting, counters, class selection, lock usage, FormatMetadataOnly, the legacy returned std::string and observed result semantics remain unchanged. The r02 producer remains byte-compatible and is still appended by its original call.

**tools/r03/diagnostic_stream/execution_serializer_tests.cpp** includes independent old-format JSON golden bytes, signed/unsigned extremes, quotation/backslash/control and NUL escaping, two classes, exact-capacity byte equality between ostringstream and bounded Writer, one-byte-short failure, and rejected sink handling. The source-bound CI workflow .github/workflows/r03-execution-serializer.yml builds and runs strict C++17 and ASan/UBSan on macOS Apple Clang, Linux Clang and Linux GCC. The corrected source-bound [CI run 38675806461](https://github.com/night-outlook/il2cpp_plus/actions/runs/38675806461) completed **success** on all three matrix jobs at native source commit fc0d3565ecc5c9d1a31520a26ff3f9fda25bc98f. Strict C++17 and ASan/UBSan host cases passed on Apple Clang macOS15, Linux Clang and Linux GCC. The first CI run 38675165150 failed on macOS only due to a host-test include-path collision (libil2cpp/vm/string.h shadowed libc++ string.h under -I); corrected to -iquote, then reran successfully. CI is source-bound host evidence, **not** official installed Unity or Player evidence.

The original native formatter golden-byte/source integration tests and the corrected cross-platform CI run are the authoritative source-bound host evidence. No official installed Unity/IL2CPP compiler matrix or Player runtime execution has been performed for this change.

**Tools/AssemblyShadow/R03IR/run_primary_host_preflight.py** defines one read-only, remote-verified four-repository Local host batch, spanning the original general stream, native V2 codec, the POSIX V2 transaction, the earlier V2 native sink, and the new execution formatting unit under strict/sanitized C++. It writes command receipts, exact stdout/stderr SHA-256, component-specific test evidence, before/after source hashes and a complete result-file inventory to a fresh external directory. Independent component failure does not hide later component outcomes; its aggregate result remains FailedOrIncomplete.

## 3. Explicit negative capability and incomplete Primary work

This cycle **does not** expose a safe native post-terminal VM capture API. The current *general* snapshot still allocates vectors and strings while observing transaction/usage/class registries; the new general writer handles output only. The current *execution* producer still allocates an unordered metadata-handle map, dynamic type keys and debug address strings and uses the heap-backed legacy JSON result. It reads metadata/class state after releasing the observation lock and cannot assert one generation-coherent, lifetime-safe frozen inventory. The new shared formatting body does **not** address either acquisition problem. AssemblyShadowTypeKey::FormatMetadataOnly and its recursive formatting are not bounded by this output serializer.

The preallocated V2 codec and descriptor-bound file transaction remain **inactive** and are not connected to the real Player native/C# emitter, final slot14/15 capture or original semantic verifier. The original V1 per-slot bound262144 is unchanged, as are V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304. No truncation, count caps, filesystem receipt as semantic PASS, synthetic V1 or weakened semantic condition is permitted.

The official Unity2022.3.62f2 StandaloneOSX engine-owner safe-point, in-flight callback drain, required native GC/finalizer/service maintenance, and restart disposition remain unresolved; the E0 capability assessment linked below identifies the exact missing API/proof. The reference native coordinator is not an engine adapter. **Do not delegate** native scheduler invention or nontrivial VM/serializer integration to Local.

## 4. Next Primary stages, strict order

1. **P1 capture:** establish metadata/transaction/usage lock-order and lifetime contract; stage capture buffers/descriptors while healthy; replace general/execution dynamic VM census/type-key production with complete bounded frozen structures. Compare entire original JSON bytes under real source-bound fixtures, including 262145+ diagnostics, errors, metadata/class/cctor values and capture peak memory. Reject capacity failure without presenting incomplete semantic fields.
2. **P2 integration:** wire real native/C# emission to authenticated V2 artifact/envelope in independently approved fresh output root; preserve original V1 historical verification, and explicitly dispatch V2 readback into **every unchanged original semantic predicate**. Negative tests cover missing/duplicate/incorrect identity, file descriptor changes, bytes/UTF-8, short/sync/readback failures and producer lifetime.
3. **E0/E1:** obtain actual supported engine-owner scheduler integration and maintenance contract (or return documented Blocked); implement and test a source-backed adapter, no guessed pointer or model-only ack. Preserve full500ms, uncapped1..64 reports and managed logger1→1.
4. **P3:** only then run official integrated Unity C#/55-native compile and independent terminal-path review, publish fresh four-source runtime handoff and allocate seven previously unused roots.

## 5. Local Validation scope now authorized

**Host-only preflight, no runtime execution:** The only new Local assignment enabled by this publication is the read-only source/host component batch in Handoff/WEB_TO_LOCAL.md. Run the one batch exactly once from clean worktrees at the recorded commits. Retain all failures and files, do not change local code, sources, tests or historical evidence. Source-bound host PASS cannot advance SNAP-01, E0, P2, R03 or the Human Review Gate. No new Player app, Unity build, native SDK-integrated compiler assignment or fresh runtime roots are authorized.

The Local factual report may record an independent HostOnly result without rewriting SNAP-01. Any nontrivial failure returns to Primary; no automatic runtime escalation.
