# R03 B2 D5-B C10 — RR3 Primary Implementation source/host remediation

**Status: `SourceHostComplete_PendingIndependentRereview`, 2026-11-23 UTC.** This is **Primary Implementation**, not independent review approval, not a Local Validation handoff, not a real Unity/IL2CPP/Player run, not runtime evidence for method/canary safety. It corrects exactly the three blocking source findings in [RR2 independent ReturnRequired](D5B_C10_RR2_INDEPENDENT_REREVIEW_2026-11-23.md) and stops at the independently initiated C10 source/design/CI rereview checkpoint.

**Authority remains binding:** `D5BC10IndependentReview=ReturnRequired` (prior decision, pending independent rereview); `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All **18 D5 real Player cells = NoCoverage**. No D6/H2/M08A/X02/SNAP-01/Human Review Gate or Local execution.

## 1. Source tuple and modification scope

All four source repos use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact tested source revision | Changes since RR2 |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | **`dbb1360c5b68dabab05755a5d39a5cea53270574`** | Three implementation/testing commits, **11 D5Probe/workflow file paths** compared to previous docs HEAD `2a639128d186a1f5584c1dd4cacae817a2e0fe44` |
| `night-outlook/il2cpp_plus` | **`c741fb32a2b770856f211f47305c4f86b51f54ce`** | One commit; only `libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowD5WindowProbe.h` from `87a34bbea39930dab96cf4703756d8da79d54684` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |

Changed demo paths only:
- `Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp` (native test-only writer);
- `D5AutoReceiptHost.cpp`, `D5WindowSourceHost.cpp` (host negative/positive tests);
- `d5_c10_native_receipt.py`, `test_d5_c10_native_receipt.py` (source-material PID/exit join and negatives);
- `d5_window_source_contract.py`, `test_d5_window_source_contract.py` (pinning/source mutations);
- `R03D5Build.cs` (new native pin);
- `d5c10_link_source_pinset_v1.json`, `d5_link_materials.py` (new actual blobs);
- `.github/workflows/r03-b2-d5-c10-window-source-host.yml` (four-OS/compiler matrix).

No changes to the two unchanged source repositories, B1/oneuse-12, historical D5-A/D5-B custody, `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, global allocator override source or any unrelated milestone.

Actual manifest `d5c10_link_source_pinset_v1.json`: **Git blob `cfca8eecb339fdbc16777efee42465c762f0462b`**, **13 pinned native source/header blobs**, **three pinned isolated overlay/managed/builder source blobs**, **five intended C++ TUs**, **nine expected C exports**. GitHub Connector separately read back all **16 of 16** exact blob identities at the two tested source commits. Actual Bee compile/link provenance and symbols remain **NotRun**.

## 2. IR-D5BC10-RR2-01 — early terminal method guard observed with exact TLS identity

In [native `AssemblyShadow.cpp`](https://github.com/night-outlook/il2cpp_plus/blob/c741fb32a2b770856f211f47305c4f86b51f54ce/libil2cpp/vm/AssemblyShadow.cpp#L2324-L2355), immediately after `TerminalMethodDenied(method)` returns true, the test-only C10 path invokes `WindowProbe::MethodResult(d5EntryPhase, MatchesTargetOnCurrentThread(method), false)` **before returning false**. No physical owner metadata resolution, lock, GC callback, native allocation, diagnostic replacement or arbitrary method admission is introduced by that early-return instrumentation. A bound constructor/other thread/other method pointer does not match the unique TLS token. Existing terminal policy, first error and production feature-OFF path stay unchanged.

Added an `early_terminal` witness-host case, which simulates the exact early-return `MethodResult` branch, verifies one target denial and one-shot token consumption. The actual full `AssemblyShadow.cpp` translation unit and real terminal/recovery status were not compiled in these host jobs; source contract separately asserts the real early-return call is present. This is a source-host behavioral contract, **not a real Player rejection observation**.

## 3. IR-D5BC10-RR2-02 — worker-completion release/acquire before field observation

The [native `AssemblyShadowD5WindowProbe.h`](https://github.com/night-outlook/il2cpp_plus/blob/c741fb32a2b770856f211f47305c4f86b51f54ce/libil2cpp/vm/AssemblyShadowD5WindowProbe.h#L95-L121) now exposes `HasWorkerCompletedP5Acquire()` which loads the actual `release_` CAS flag with `memory_order_acquire`. The worker calls `ReleaseP5` with a release/acq_rel CAS only **after the admitted `Keep` invocation returns or unwinds**. The collector's allowed-completion condition now uses the **acquired worker flag**, not the relaxed `releaseCount_` metrics. The [overlay `FinishNativeReceipt`](https://github.com/night-outlook/hybridclr_demo/blob/dbb1360c5b68dabab05755a5d39a5cea53270574/Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp#L214-L264) reads `canaryBefore` only after `canaryReady.load(memory_order_acquire)` confirms its earlier release publication and reads the pinned `stable` field only on an already-denied method or a worker-acquire completed admitted method. A P5 race or timeout cannot blindly dereference an unpublished canary. `NoCoverage` remains the fallback for unbound/not-yet-completed snapshots.

Added the `canary_happens_before` native host test: a writer thread assigns an ordinary integer, releases the actual `WindowProbe` flag, a reader thread acquire-loads it before reading that integer. Source mutation tests require the **exact acquire-return statement**, guarding against accidentally mutating only the unrelated P5 wait loop. No actual Unity GC/pinned-instance read or native VM metadata race was exercised.

## 4. IR-D5BC10-RR2-03 — private pending receipt, publish after close, process-join rule, injected faults

[`R03D5WindowOverlay.cpp`](https://github.com/night-outlook/hybridclr_demo/blob/dbb1360c5b68dabab05755a5d39a5cea53270574/Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp#L125-L225) now opens `<final output>.pending` exclusively (`O_EXCL|O_NOFOLLOW`, permission 0600), rejecting a preexisting final path or pending output. It writes the exact original **4,652-byte native fixed-record schema**, including the slot-10 record **only inside that private pending path**. `PublishClosedReceipt` performs file `fsync`, checks actual `close`, then uses an **atomic no-clobber `link(pending,final)` publication**, removes the private pending link, and fsyncs the parent directory. The final path does not exist on failed final-event `pwrite`, file `fsync` or `close`. An `unlink`, link or parent-directory sync failure can occur **after** the final path becomes visible; the native collector then exits status `2`, not accepted `20`/`42`. In failure cases pending evidence can remain for diagnosis. This protocol is a **test-only source/host candidate**; independent real disk durability and macOS Player behavior remain NotRun.

The [`d5_c10_native_receipt.py`](https://github.com/night-outlook/hybridclr_demo/blob/dbb1360c5b68dabab05755a5d39a5cea53270574/Tools/AssemblyShadow/R03IR/D5Probe/d5_c10_native_receipt.py) now requires separately supplied `externally_observed_pid` and `externally_observed_exit_code`. Neither a complete-looking ten-slot file nor an admitted/denied native guard alone is sufficient for candidate classification. Exact PID join and **exit `20` for denied** or **`42` for admitted** are required; an externally observed exit `2`, `0`, wrong PID or missing report yields `NoCoverage`, even if the raw file is structurally complete. The parser explicitly says **`externalProcessProvenanceIndependentlyVerified=false`** and **`actualLinkedBinaryAndPidAuthenticated=false`**, because accepting arguments is **not independent attestation**. A future separately authorized Local process monitor must establish the binary/PID/argv/exit authority; neither source-host synthetic PID copying nor user supplied values prove it.

Host-only `HYBRIDCLR_R03_D5_SOURCE_HOST_AUTO=1` fault injection simulates four I/O failures: final-event `pwrite`, file `fsync`, file `close`, and post-publication directory `fsync`. Real OS I/O failure injection, hardware power-loss durability and Player process-exit provenance remain NotRun. The host tests validate the intended file publication/exposure behavior and source parser rejection, but the simulation uses mock process/first-error/canary inputs; do not describe it as an actual Unity native failure.

## 5. CI source-host evidence and failures preserved

**[GitHub Actions run 45144226643](https://github.com/night-outlook/hybridclr_demo/actions/runs/45144226643)** at **demo `dbb1360c5b68dabab05755a5d39a5cea53270574`**, native `c741fb32a2b770856f211f47305c4f86b51f54ce`, push **attempt 1, completed/success, 4/4 successful jobs**. I separately fetched and counted the four raw logs:

| Runner | Raw job | Source-contract Python | Synthetic link Python | Receipt Python | Strict + ASan/UBSan native ON | OFF | Native synthetic receipt scenario checks |
|---|---|---:|---:|---:|---:|---:|---:|
| Ubuntu 24.04 C++17 | `137589405848` | 59 | 27 | 34 | 22 window + 2 manual writer + 20 auto writer | 1 | 20 |
| macOS 15 C++11 | `137589406538` | 59 | 27 | 34 | 22 window + 2 manual writer + 20 auto writer | 1 | 20 |
| macOS 15 C++17 | `137589406633` | 59 | 27 | 34 | 22 window + 2 manual writer + 20 auto writer | 1 | 20 |
| Ubuntu 24.04 C++11 | `137589406705` | 59 | 27 | 34 | 22 window + 2 manual writer + 20 auto writer | 1 | 20 |
| **Total** | | **236** | **108** | **136** | **176** | **4** | **80** |

**480 passing Python source/synthetic tests; 176 passing strict/sanitized C++ native source-host receipts; four feature-OFF controls; 80 synthetic file-publication/classification scenario checks.** All four complete job logs contain no unexpected ASan/UBSan runtime diagnostics. The ``io_pwrite`, `io_fsync`, `io_close`` cases prove no final publication in their simulated failures; the `io_dirsync` case proves a visible complete-looking file is still `NoCoverage` when its synthetic exit is 2. Every result remains `SourceHostOnly`, never real IL2CPP build/Player.

Intermediate runs **remain failed** and cannot be promoted: `45143818536` failed (stale source contract and mutation), `45144032193` failed (mutation targeted waiter instead of worker-acquire); only **`45144226643`** tests this final source code. Earlier RR2 CI [45132702353](https://github.com/night-outlook/hybridclr_demo/actions/runs/45132702353) remains a valid historical *different source* baseline, not today's source proof.

## 6. Remaining risks and next checkpoint

**NotRun/NoCoverage:** full Unity 2022.3.62f2 C# builder/Player compile, complete native `AssemblyShadow.cpp` IL2CPP translation unit, the `HYBRIDCLR_R03_D5_NATIVE_VM_EVIDENCE=1` branch, actual MethodInfo pointer join/dispatch, native GCHandle/field lifetime, P5/Committing concurrent method admission, actual frozen first-error read, macOS arm64 linked Mach-O/UUID/exports, Bee source→object→link, PID/argv/exit trustworthy process monitor, 32-bit ABI and other platforms, and all **18 D5 real Player test cells**. No actual early unauthorized business execution or correct live denial has been established. The 20–2000-ms test-only P5 window and native test-only `_exit(20/42/2)` remain unchanged; their compatibility is for independent future review. Host/synthetic tests are not empirical real-VM evidence.

The source-only link-material check still deliberately accepts manufactured Mach-O/nm/compile materials only under `SyntheticSourceHost` and keeps all linked proof flags false. The six mandatory historical evidence-root roles and `APPROVED_LOCAL_HANDOFF_BLOB=None` remain unmodified in `D5Admission/d5b_custody_authority.py`; no reviewed immutable executable Local handoff or user authorization exists.

**Next and only permitted activity:** a **new independent C10 source/design/raw-CI rereview** of this exact four-repository tuple and run `45144226643`, with explicit attention to early terminal path, release/acquire synchronization and private-to-final file/external PID/exit failure semantics. Reviewer selects `PassD5BC10ForNextPreparation`, `ReturnRequired` or `Blocked` for **source/test-producer preparation only**. Primary cannot self-approve. Do **not** enter Local Validation, D5 complete, R03 acceptance, H2 or Human Review Gate, even if source-host review passes.
