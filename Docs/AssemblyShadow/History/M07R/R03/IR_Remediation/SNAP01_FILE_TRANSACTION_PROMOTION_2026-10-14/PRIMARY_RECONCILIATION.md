# SNAP-01: native V2 file transaction — Primary source and CI reconciliation

**Owner:** Primary Implementation. **Date:** 2026-10-14. **Disposition:** **Passed within inactive component and filesystem-host-test scope only.** A new Local execution, original Player semantics and full R03 acceptance remain **unauthorized**.

## 1. Authority and immutable failures

Read current `Docs/AssemblyShadow/README.md`, factual Local-owned `Handoff/LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md` and the immutable SNAP-01 checkpoint. SNAP-01 was **18 cells: 14 Passed / four Failed**. The three ON raws were zero-byte/exit2 because the *actual* general diagnostics in text slot **14** exceeded the original **262,144** byte single-slot capacity; reason9, scanned prefix262145, exact actual lengths unavailable. It is *not* the synthetic slot15 experiment. The engine witness completed **51,213 uncapped reports in 500ms** (exit71), exceeding the unmodified 1–64 bound. Diagnostic collection `EvidenceCollected` did **not** improve semantic `ReturnRequired`. The full S historical custody remains **Blocked**, original C 416,844 identities, 339,367 survivors, 77,477 missing and four original installed-native roots unavailable.

No Player, native engine guard, compiled C# emitter, original semantic verifier or Local-owned evidence has been modified by this delivery. SNAP-01/N and earlier consumed runtime attempts are never retried/relabelled.

## 2. Candidate comparison and selection

Prior sessions created multiple **isolated** GitHub branches with distinct POSIX transaction models, as well as a local-only file candidate. Do **not** combine their types, receipt schemas or verification scripts as if interchangeable. This publication selected the exact tested source from `codex/v2-file-transaction-20261014-5a71@0793ecb4c6d42605f7959c6190dd09e866ff54a5`: retained ancestor descriptors, independently expected directory inode/device, exclusive fixed filenames, strict sync/readback, immutable failure receipts, and a strict descriptor-bound read-only V2 decoder. The alternatives remain separate CI explorations, not authorized production variants.

The active feature branch `codex/assembly-shadow-r01b-h1` received **four byte-identical source/test Git blobs** (see EVIDENCE.json) and the same CI steps with only the trigger changed. Code was not recopied from the unpublished tarball or assembled from conflicting candidates. Source integration anchor `f039e0df247ccaec162c405be2120691e2d6b47e`. Other GitHub connector smoke branch `codex/connector-smoke-v2-files-20261014-d7c3` was readback verified and remains disposable because branch deletion is unavailable.

## 3. Implemented and exact limits

`Tools/AssemblyShadow/R03IR/bounded_v2/PosixDiagnosticTransaction.h`, `transaction_driver.cpp`, `transaction_reader.py`, and `run_transaction_tests.py` provide one **inactive** component:

- Before terminal execution, a caller-independent authority must admit a fresh external directory/device/inode and exact run/PID/source/request/build bindings. The native component retains descriptor identities while walking with `O_NOFOLLOW`; it exclusively creates fixed private names and never unlinks/overwrites historical output.
- The existing V2 Encoder writes the complete `diagnostics.v2.bin` artifact through a bounded sink. The native transaction checks its full-wire receipt, filesystem identity, length, readback hash and required sync. It writes the small `envelope.v2.json` **only afterward**, performs complete final readback/identity and directory sync, and issues success only after the required operations. Partial artifacts are retained; there is no claim that two paths become atomically visible in one filesystem operation.
- The read-only `transaction_reader.py` requires an externally authenticated successful receipt, retains ancestor/file descriptors and validates exact file hashes/EOF and complete V2 header/section/frame/footer, strict diagnostics JSON and expected identity before returning complete logical fields. It neither rewrites V2 as V1 nor calls a business semantic predicate or changes a `Failed` result. An untrusted self-consistent rewritten receipt is **not** authenticated by SHA-256 alone.
- Per-frame maximum **65,536** bytes; original V1 per-text-slot maximum **262,144** unchanged; diagnostic artifact maximum **3,932,160**; envelope reserve maximum **262,144**; encoded combination maximum **4,194,304**. Overflow is a failure. These are encoded limits, *not* complete VM capture or Python memory/RSS guarantees.

The POSIX tests use actual files and descriptor operations in Linux and macOS CI. Successful requested `fsync`/Darwin `F_FULLFSYNC` is not a hardware power-loss test. Descriptor and kernel behavior on the specific future Local macOS host remain separate verification. No independent source trust, scheduler owner, native GC/finalizer maintenance or restart guarantee is provided by these file components.

## 4. Independent source-bound evidence

Active-branch [CI **38671600319**](https://github.com/night-outlook/hybridclr_demo/actions/runs/38671600319) **Passed** with three jobs: Apple Clang macOS14, Clang Ubuntu24.04 and GCC Ubuntu24.04. Each ran **27 original unit methods** in strict C++17 and ASan/UBSan configurations: 27/27 per profile, zero final failures/errors/skips. They include exact large-field/reference roundtrip, error and replay controls, ancestor/file replacement, hard-link and occupation rejection, short/I/O failure, close/sync and UTF-8/JSON validation. They do **not** prove full OS failure-space coverage.

The original CI ZIP SHA-256 digests, exact source commit, **3,399 independently SHA-verified manifest regular files**, total 3,405 archive files (two manifest/self-evidence entries beyond each declared set), **516** compiler/process command records and exact result identities were authenticated. Final per-platform breakdown, artifact/job IDs, digests and source blobs are in [EVIDENCE.json](EVIDENCE.json). These are unchanged original artifacts; the GitHub ZIP retention is limited.

This publication **does not** claim a fresh official Unity2022.3.62f2 managed/55-native compiler pass against a Player using the V2 transaction. It has not been linked into current `R03TerminalPlayer.cs`, captured the actual `GetDiagnosticsJson`/execution metadata, been run in a protected Local SDK, or produced a successful ON semantic verifier.

## 5. Unfinished Primary work and exact stopping rule

**P1:** Both general and execution diagnostics require one coherent, lock/lifetime-reviewed **bounded native capture** with byte-for-byte legacy/schema output and no terminal-path managed string marshalling. The native general serializer `il2cpp_plus@87aedc1248141d7438d82d53521aadaac22c45ae` now shares formatting with its bounded sink; **execution** metadata still uses allocation-backed snapshots and `std::ostringstream`. Neither current shared format guarantees an allocation-free or stable VM census.

**P2:** Healthy-time admission of descriptors/buffers, integration into real current native/C# emitter and complete V2 artifact/envelope, strong independent receipt custody, copied-archive verifier and **explicit V2 dispatch through all original unchanged semantic predicates** remain unimplemented. File transport integrity alone may not upgrade any runtime status.

**E0/E1:** Establish an actual supported Unity2022.3.62f2 StandaloneOSX native engine-loop owner safe point, in-flight callback drain, continued native maintenance and restart lifecycle. The reference coordinator is **not** a real engine adapter. No synthetic ready flag, report counter cap, coalescing, callback sleep, suppressed finalizer, broad no-op return or early process exit may satisfy the exact 500ms/1–64 uncapped engine-report condition.

Keep `Handoff/WEB_TO_LOCAL.md` **PAUSED**. Do not delegate any of these nontrivial changes to Local or issue unused-root/Player execution authorization before source-bound integrated compiler and independent terminal-path review. All acceptance flags remain false, strict historical S custody Blocked, independent R03 full-stage review FAIL/re-review NotRun; no H2/X02/M08A or automatic Human Review Gate.
