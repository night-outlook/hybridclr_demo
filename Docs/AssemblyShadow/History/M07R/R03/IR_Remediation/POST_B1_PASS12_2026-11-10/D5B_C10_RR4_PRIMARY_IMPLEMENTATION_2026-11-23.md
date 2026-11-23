# R03 B2 D5-B C10 — RR4 Primary Implementation: native guard-entry preconditions and truthful release receipt

**Primary status (2026-11-23 UTC): SourceCodeCommitted_UbuntuHostPass_MacOSJobsQueued.** This is a bounded **Primary Implementation**, not independent review approval and not Unity/IL2CPP/Player evidence. Two new source changes correct [RR3 independent ReturnRequired](D5B_C10_RR3_INDEPENDENT_REREVIEW_2026-11-23.md) findings `IR-D5BC10-RR3-01` and `IR-D5BC10-RR3-02`. **Until independently approved: `D5BC10IndependentReview=ReturnRequired`.**

## 1. Exact four-repository source tuple and scoped changes

All four repositories have branch `codex/assembly-shadow-r01b-h1`.

| Repository | Exact source tested/pushed | Scope |
|---|---|---|
| `night-outlook/hybridclr_demo` | **`54cd6c3d6c8cc313d00c542d15f0bb409aafbe09`** | 13 scoped C10 D5Probe/workflow files since previous independent report HEAD `4ec9f2bc8af3a797183d18dd3d8a78ad96eec482` |
| `night-outlook/il2cpp_plus` | **`e9aee83345aa9df90085de50162a7aa9172e8263`** | One commit: only `libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowD5WindowProbe.h` since `c741fb32a2b770856f211f47305c4f86b51f54ce` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |

GitHub Connector readbacks confirmed exact native/demo modifications and **16/16** Git source blob identities recorded by [`d5c10_link_source_pinset_v1.json`](https://github.com/night-outlook/hybridclr_demo/blob/54cd6c3d6c8cc313d00c542d15f0bb409aafbe09/Tools/AssemblyShadow/R03IR/D5Probe/d5c10_link_source_pinset_v1.json), Git blob `b218aa1140432d35230350cb7361a5a5b496c812`: 13 native source/header blobs and three isolated demo overlay/managed/builder blobs. Five intended native translation units and nine expected C exports are unchanged. No B1 historical evidence, D5-B custody, Local-owned `LOCAL_VALIDATION.md` or `RETURN_TO_WEB.md`, unrelated milestone, native allocator override or Unity product code was changed.

## 2. RR3-01: exact native target-method guard-entry snapshot

In [actual native `AssemblyShadow.cpp`](https://github.com/night-outlook/il2cpp_plus/blob/e9aee83345aa9df90085de50162a7aa9172e8263/libil2cpp/vm/AssemblyShadow.cpp#L2324-L2360), the C10-only path now invokes `WindowProbe::TargetGuardEntry` **after sampling entry P5 phase and native `s_state` and `s_firstFailureV2.status()`, and before the first `TerminalMethodDenied(method)` check**. It uses the exact pointer identity previously bound to the one-shot worker TLS token. This path allocates no managed objects, does not do metadata lookup or disk I/O, and does not change the production terminal rejection decision.

[`AssemblyShadowD5WindowProbe.h`](https://github.com/night-outlook/il2cpp_plus/blob/e9aee83345aa9df90085de50162a7aa9172e8263/libil2cpp/vm/AssemblyShadowD5WindowProbe.h#L127-L212) defines the new `TargetGuardEntry` / `TryReadTargetGuardEntry` with release-published atomic `stateAtEntry` and `firstErrorAtEntry` values. A mismatched method, competing thread, missing token, or phase not entered at P5 cannot generate a target-entry witness; the first matching entry is frozen and cannot be overwritten by a later terminal value. The native collector writes **event slot 4 = `(1, 1, stateAtEntry, firstErrorAtEntry)`** *only after a real same-TLS native guard-entry token was published*, rather than falsely promoting mere `BeginKeepAttempt` arming.

A source-only C10 *healthy-P5* candidate now requires actual target entry with **`stateAtEntry == 5` (`Committing`)** and **`firstErrorAtEntry == 0` (`Empty`)**. A preexisting terminal state (8/9), first-error already writing/frozen/invalid (1/2/3), no actual entry or P5→P6 race gets `NoCoverage`, never `CandidateObservedDeniedInP5_RequiresIndependentBinaryProof`. The independent native collector also exits status 2 instead of 20/42 when entry was not healthy, before any external parser can promote a candidate. The post-guard frozen first-error and state are still distinct data, not inferred as the pre-entry state.

**Host coverage:** new exact header scenarios `entry_preterminal`, `entry_prior_error`, `entry_no_token`, `entry_competing_thread`, `entry_wrong_method`, `entry_after_p6`, plus host auto-receipt negatives `entry_preterminal`, `entry_prior_error`, `entry_missing_guard`. Source-contract mutations assert the source order is strictly entry snapshot → first terminal check, that first-error status is read rather than assumed, exact TLS identity is required, and proper release/acquire storage is preserved. The complete Unity VM TU was NOT compiled/executed here; actual method identity/first-error in a Player remain unverified.

## 3. RR3-02: versioned native receipt semantics without fabricated managed completion

The fixed native binary record layout remains **4,652 bytes**, but **`Header.schema=2`** and **`R03_D5_WindowProtocolVersion()==2`**. The isolated C# fixture, native header and Python parser use version 2; v1 receipts must fail before classification, preventing reinterpretation of historical fields. The C10 source manifest now explicitly pins `receiptWireSchemaVersion=2` and `nativeWindowProtocolVersion=2` without renaming the separate manifest's v1 *file-format* kind.

**Wire v2:**
- Event slot 4: actual native same-TLS target guard-entry state and first-error status (not merely a token arm).
- Event slot 5: actual same-token native guard completion (`1` allowed, `2` denied, `3` P6 raced).
- Event slot 6: `(-1, postCollectorState, nativeP5ReleaseObserved, targetArmCount)`. Third field is **1 only if `WindowProbe::HasWorkerCompletedP5Acquire()` returned true**; otherwise **0**. It does **not** assert a managed `Join`, managed final `done` flag, or successful managed completion.
- Event slots 1–3 and 7–10 retain their fixed fields, frozen native first-error, pinned canary, native file synchronization and source-only claim limitations.

[`d5_c10_native_receipt.py`](https://github.com/night-outlook/hybridclr_demo/blob/54cd6c3d6c8cc313d00c542d15f0bb409aafbe09/Tools/AssemblyShadow/R03IR/D5Probe/d5_c10_native_receipt.py) requires all ten v2 event slots, healthy native guard entry, a matching slot-5 decision, actual native release field in {0,1}, a terminal post-state and frozen first-error for a denied candidate, bound/matched canary, source-material-only PID/exit and guard counts. **Denied can be a bounded native guard-completion candidate even with `nativeP5ReleaseObserved=false`**, because terminal poison may prevent post-guard managed finally; the parser explicitly outputs `managedWorkerCompletion=Unknown_NotJoined`. An allowed method decision requires the observed native release to avoid claiming successful body-snapshot completion without an acquire. Neither outcome is a Player PASS: `realPlayerC10Passed=false`, `externalProcessProvenanceIndependentlyVerified=false` and `actualLinkedBinaryAndPidAuthenticated=false`.

Earlier contradictory parser tests are reconciled: old "worker unfinished not denial proof" has become "no managed completion required for immutable native denial", with both native-release status and managed unknown explicitly tested; case 28 also checks the same boundary. Added v1 rejection, preterminal/pre-error/incorrect state, no guard-entry, invalid observed-release value and admitted-without-release negatives. **43 receipt-parser tests** per host job.

## 4. Source-host CI and raw evidence status

**[GitHub Actions run 45166349875](https://github.com/night-outlook/hybridclr_demo/actions/runs/45166349875)**, demo `54cd6c3d6c8cc313d00c542d15f0bb409aafbe09`, native `e9aee83345aa9df90085de50162a7aa9172e8263`, attempt 1. The verified per-job matrix is:

| OS / C++ | Actual raw job ID | Latest known result | Python tests if complete | Native ON host cases if complete |
|---|---|---|---:|---:|
| Ubuntu 24.04 C++11 | `137664181102` | **PASS** | 72 source + 27 link + 43 receipt | 34 window + 2 manual + 26 auto |
| Ubuntu 24.04 C++17 | `137664181290` | **PASS** | 72 source + 27 link + 43 receipt | 34 window + 2 manual + 26 auto |
| macOS 15 C++11 | `137664180859` | **QUEUED as of this report draft** | Pending | Pending |
| macOS 15 C++17 | `137664181683` | **QUEUED as of this report draft** | Pending | Pending |

Both full Ubuntu raw logs were independently fetched: **142/142 Python tests, 62/62 native strict/sanitized ON cases, 1 feature-OFF control and 26 synthetic receipt checks per job**, with no unexpected ASan/UBSan or failures. Each Ubuntu job includes preterminal/prior-error/missing-entry source-host negative receipts classified as `NoCoverage`. **The four-job matrix must not be claimed 4/4 successful until both macOS jobs finish and their raw logs are inspected.**

The initial [run 45166141846](https://github.com/night-outlook/hybridclr_demo/actions/runs/45166141846) failed a source-contract mutation that did not catch removal of the native-release evidence variable. The narrowly repaired source-only checker was committed in demo `54cd6c3d6c8cc313d00c542d15f0bb409aafbe09` and retested. Keep the failed earlier run FAILED, not promoted.

## 5. Explicit unknowns, gates and next stop

These are only C++11/C++17 exact-source/synthetic host tests. **NotRun:** real Unity 2022.3.62f2 C# compiler, full native `AssemblyShadow.cpp` IL2CPP TU, actual `HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1` path, real VM GCHandle/pinned canary/MethodInfo identity, authentic first-error, macOS arm64 Bee/object/link/Mach-O/UUID/symbols, 32-bit/platform ABIs, actual PID/argv/exit monitor, and all **18 D5 real Player cases**. The source-only pinset's five native TU and nine export fields are *intended*, not compiled actual outputs. Synthetic mock Mach-O/nm and historical B1 oneuse-12 cannot replace a real D5 source→binary→PID chain.

**Authority remains:** `D5BC10IndependentReview=ReturnRequired` pending a **separate** independent rereview, `D5BLocalExecution=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `APPROVED_LOCAL_HANDOFF_BLOB=None`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. Six historical custody roots remain mandatory and unbound for D5; no local one-use output or user Local execution permission.

**Next permitted step:** complete/authenticate raw macOS CI job outcomes, then request a separate **independent C10 RR4 source/design/CI rereview** of the fixed exact four-repo tuple, not a Local Validation handoff or a product/Human Review Gate. Stop at that review.
