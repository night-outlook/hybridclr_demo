# R03 B2-0 — C++11 compatibility, RED→GREEN, and host wire/POSIX tests

Date: 2026-11-10 UTC. Owner: Primary Implementation. **Scope is the B2 inactive component and standalone native host only**; this document is not an installed Unity SDK translation-unit test, Player result, full VM field14/15 producer, or authenticated runtime V2 implementation.

## 1. Source / failure reproduction

The real oneuse-12 Unity Bee native VM source was built with `-std=c++11`. The old isolated bounded V2 code was tested as C++17, not compiled into that Player. A new GitHub Actions [read-only syntax gate](../../../../../../../.github/workflows/r03-ir-b2-compiler-compat-source.yml) checked the actual, unchanged 4 source inputs (`BoundedDiagnosticsV2.h`, `PosixDiagnosticTransaction.h`, `native_driver.cpp`, `transaction_driver.cpp`) on macOS 15 and Ubuntu 24.04.

**RED at commit `f710aea1f97ba43f45b709a462e480f573634ec3`:** [run 42789420796](https://github.com/night-outlook/hybridclr_demo/actions/runs/42789420796), **C++17 2/2 Passed; C++11 0/2 Failed**. Raw Mac and Ubuntu Clang logs independently identified:
- `BoundedDiagnosticsV2.h:89`: a `noexcept` function pointer type alias is not permitted by the C++11 type system (the exception specification participates in function pointer types under C++17).
- `BoundedDiagnosticsV2.h:167`: braced list assignment to a struct with nonstatic data member initializers is not valid C++11 aggregate assignment.
- `native_driver.cpp:76`: braced 2-argument initialization of the test-only `Output` struct is not valid C++11 with member initializers.

The syntax test exited before reaching the second driver after the first failure; it did **not** prove the POSIX header's compatibility.

## 2. Focused Primary-owned remediation

All code changes are in **`night-outlook/hybridclr_demo`**, under `Tools/AssemblyShadow/R03IR/bounded_v2`; no `night-outlook/il2cpp_plus` production native VM, managed fixture, original S or historical evidence was modified.

| File | Exact source correction |
| --- | --- |
| `BoundedDiagnosticsV2.h` | Select the original `noexcept` callback pointer type under C++17 and a plain pointer type under C++11; the sink itself remains `noexcept`. Assign the first `Failure` fields individually under the existing once-only check, retaining the first-writer result |
| `PosixDiagnosticTransaction.h` | Assign `FileFailure` fields explicitly and assemble `FileIdentity` from an initialized local object, retaining original device/inode/owner/mode/bytes/digest values |
| `native_driver.cpp` | Default-initialize the standalone test `Output` and set its buffer pointer/capacity explicitly; no host allocation override enters production libil2cpp |
| `run_tests.py`, `run_transaction_tests.py` | Add optional `--cxx-standard c++11/c++17` with **unchanged default C++17**; preserve strict/sanitized original test cases and record selected standard in the source-bound result |
| `.github/workflows/r03-ir-b2-host-cxx11-cxx17.yml` | New sparse-checkout, exact-source dual-OS job matrix, strict+ASan/UBSan codec and real POSIX host transaction tests in both C++11 and C++17 |

No changes were made to the V2 field14/15 schema, binary frame magic, section/footer layout, SHA256, field bounds, descriptor names, O_EXCL/O_NOFOLLOW, F_FULLFSYNC/fsync or directory identity rules.

## 3. Empirical GREEN evidence (host only)

- [Run 42789933778](https://github.com/night-outlook/hybridclr_demo/actions/runs/42789933778) at source commit `dc611e976721e52a52873b79fdc7b3b35f8ef1d7`: **4/4 completed/success**. macOS 15 and Ubuntu 24.04 independently compile both native drivers with actual `-std=c++11` and `-std=c++17`.
- [Run 42790274635](https://github.com/night-outlook/hybridclr_demo/actions/runs/42790274635) at source commit `94073fe6cf0e70a70c882ea9787de145f5b00c74`: **4/4 completed/success** (macOS/Ubuntu × C++11/C++17), each with two strict/sanitized test profiles per component. Per job `BoundedNativeV2Interop`: **20+20 tests**, 0 Failed/Errors/Skipped. Per job `InactiveNativeFileTransactionTests`: **27+27 tests**, 0 Failed/Errors/Skipped. Total **376 source-bound real host test executions**, including exact binary/reference round trips, failed sink, replay, UTF-8, bytes/bounds, fsync/close, symlink/path swaps, descriptor identity, source mutation, reentrant and other negative cases. Each job independently checked the sources were unchanged and the result explicitly asserted `actualUnity=false` and `productionTransportEnabled=false`.
- Source review of the five code patches found no field/format change or new production allocator driver; the unchanged C++17 path retains `noexcept` pointer type. Evidence is limited to public host compilers and POSIX simulations/real host file operations. No official installed Unity headers, GameAssembly link, actual runtime V2 writer or power-loss durability test was run.

## 4. Scope and remaining blockers

**B2-SRC-02** is **corrected and host-verified in C++11 and C++17**. A future new **actual Unity 2022.3.62f2 SDK** build of the complete B2 Player integration still remains **NotRun**, because B2 Player source integration is not ready and no new Local Validation is authorized.

**B2-SRC-01 (full live source for `finalDiagnostics`/field14 and `finalExecutionDiagnostics`/field15), B2-SRC-03 (metadata/class pointer lifetime and VM-wide epoch not proven), and B2-SRC-04 (external identity/authentic receipt) remain Primary-owned** and prevent activating the binary producer as a semantically complete original V2 snapshot.

Historical oneuse-12 focused B1 PASS and earlier Local outcomes remain immutable. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; wholeVmEpoch=NotProven`. PureInterpreter disabled. [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**.
