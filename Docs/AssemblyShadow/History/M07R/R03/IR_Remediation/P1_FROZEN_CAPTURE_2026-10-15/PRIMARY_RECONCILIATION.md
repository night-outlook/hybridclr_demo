# P1 owned frozen execution capture — Primary reconciliation

**Owner:** Primary Implementation. **Disposition:** PassedWithinInactiveHostComponentScope only. This is substantive P1 source work, not complete P1 or runtime qualification. Local remains PAUSED.

## 1. Exact source authority

All four canonical GitHub remotes use branch codex/assembly-shadow-r01b-h1:

| Repository | Authority |
| --- | --- |
| night-outlook/il2cpp_plus | New native P1 component + host CI source **096ad96168e025a43a8581b3f15b704a66731f29** |
| night-outlook/hybridclr_demo | Last actually validated Local host execution **7b9d1d4e37d1731f9f00042eb04892a8afaf7e80**; newest Primary Docs publication is separately verified |
| night-outlook/hybridclr | Unchanged **4b2774b066cfc6afd77a8c8aded6bda7ea574f55** |
| night-outlook/hybridclr_unity | Unchanged **948c0e3b4f8891481301770115e8ba4945eea6de** |

The demo Tools/AssemblyShadow/R03/source-pins.json retains native 74dbdbea80d83923863303bd2b2c0a87f36541b1 from the preceding Local host execution. It is **not** silently rewritten to make new, uninstalled P1 code look like a previously compiled Unity Player. New native source authority is distinct from older execution/evidence authority.

## 2. Implemented P1 building block

libil2cpp/vm/AssemblyShadowFrozenExecutionCapture.h provides an **owned, bounded, frozen execution-diagnostics representation**, independent of VM, Unity lifecycle or OS files:

- Preallocate the Capture object while healthy; copy all header state and row text into a fixed 2,097,152-byte arena and typed 1024-row table matching the current kMaximumExecutionClasses.
- Reject invalid, null, overlapping, oversized and duplicate inputs; preserve the first failure, reject rows after freeze, reject too many classes, and refuse prefix-based success. An ordinary Freeze requires a nonempty reviewed R02 suffix.
- Preserve exact full QuotedText lengths (including embedded NUL/control bytes), immutable scalar values, original JSON field/key order and escaping. Deep copy makes the frozen representation independent of the original source text lifetime.
- Use existing pure native execution Begin/AppendClass/EndClasses and synchronous bounded Writer in SerializeTo, without VM calls, GC, managed marshalling, std::ostringstream, native file I/O or dynamic allocations. The static C++ object-size guard is <=3MiB; capture is allocated while healthy, not inside terminal failure.
- A separate explicit historicalHostFixtureWithoutR02=true exists ONLY for the immutable N fixture, whose original mock R02 formatter emits no suffix. It is not a production acceptance exemption.

**Host implementation and tests:**
- tools/r03/diagnostic_stream/frozen_execution_capture_tests.cpp exercises zero/one/1024 classes, old full N JSON bytes, source-string lifetime mutation, prepared operator-new accounting, byte/row limits, unavailable R02, partial sink and invalid state. 
- tools/r03/diagnostic_stream/frozen_execution_v2_driver.cpp + run_frozen_v2.py directly pipe complete frozen execution JSON to the **unchanged native V2 Capture/Encoder** alongside a large synthetic general diagnostic. Against the pinned original Python wire reference, they require exact full-wire byte equality, lossless readback and original inline result=Failed (never promoted by transport). Negative scenarios reject insufficient capture, invalid UTF-8, combined artifact overflow and deliberately interrupted output.
- .github/workflows/r03-p1-frozen-execution.yml runs strict C++17 plus ASan/UBSan under Apple Clang/macOS and Clang/GCC/Linux, checked against the original pinned N source fixture. It does not launch Unity.

Actual AssemblyShadow::GetDiagnosticsJson/GetExecutionDiagnosticsJson VM readers, native/C# Player emitter and semantic verifier **are unchanged**. The new capture cannot assert that its caller acquired metadata safely. It is inactive until a separately reviewed live capture ABI exists.

## 3. Verified source-bound evidence

[Native CI 38698299448](https://github.com/night-outlook/il2cpp_plus/actions/runs/38698299448) **completed SUCCESS on all 3 jobs**, source native 096ad96168e025a43a8581b3f15b704a66731f29. Both strict and ASan/UBSan profiles passed on macOS Apple Clang and Ubuntu Clang/GCC.

- Complete 1024-class owned fixture exactly matches original historical N function output: **331,078 bytes**, SHA-256 3d68d22ef23e09b677c06e44f44acac5042b819987719c6cc2937f830f05785a.
- Synthetic general JSON: **300,032 bytes**; synthetic execution JSON: **331,078 bytes**. Native encoded V2 wire: **631,720 bytes**, SHA-256 f1e193ee55e34bcf051f6835949c1889deeec019064fcfc9604fd1264891038e, byte-identical to the unchanged Python reference on all six compiler/profile combinations.
- Each job completed **12 V2 compiler/process receipts**, with all invalid source UTF-8, aggregate-overflow, capture-short and partial encoded sink failure controls rejected. The strict reference decoder rejects incomplete wire; inline semantic Failed remains Failed.
- Original three CI ZIPs downloaded via GitHub Connector and separately audited. All **150** declared V2 manifest regular files (52 macOS, 49 GCC, 49 Clang) were independently SHA-256 matched, with no missing/mismatched or unlisted V2 files. ZIP hashes, artifact IDs, original source pins and limits are in [EVIDENCE.json](EVIDENCE.json). A preceding exploratory host compile failure was in a newly written test-only C-string argument and was corrected before this final CI; no product runtime failure is inferred.

Operator-new accounting observes no new calls during the prepared memory-only capture/format/encode test. **This is not proof** of no malloc, metadata map/type-key allocation, live VM GC/RSS peak, or power-loss durability. The host deliberately holds both an unencoded and encoded V2 buffer at once; that is **not** the proposed 4MiB production memory plan.

## 4. Earliest incomplete P1 source work

Read [SOURCE_LIFETIME_AUDIT.md](SOURCE_LIFETIME_AUDIT.md). The general producer constructs dynamic snapshots under separate transaction/usage/assembly/metadata lifetimes. The execution producer copies class pointers under its observation lock but later allocates a metadata-owner map and recursive type-key strings after releasing that lock; it separately samples metadata/ctor flags and R02 counters. No source-backed all-class lifetime ticket or coherent post-terminal epoch is established.

**Remaining mandatory Primary stages:**
1. P1 VM ownership/lifetime capture contract; bounded metadata/type-key acquisition; complete frozen general/typed execution/R02 snapshots; real peak memory and fail-closed resource disposition.
2. P2 real native+C# V2 file transaction/semantic verifier integration preserving original V1 historical proof and **every unchanged semantic predicate**.
3. E0 vendor/source-proven Unity2022.3.62f2 StandaloneOSX engine-owner safe point, callback drain, native GC/finalizer/service/restart; E1 implemented only if this capability is proven. A mocked coordinator cannot establish engine ownership.
4. P3 full official source-pinned managed/55-native SDK compiler matrix, terminal-path independent review and fresh runtime plan.

The current WEB_TO_LOCAL remains **PAUSED**, with no new Local task or Player root. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled. No H2/X02/M08A or automatic Human Review Gate.

SNAP-01 remains **FAIL/ReturnRequired**: 18 cells (14 Passed/4 Failed), three ON raw zero bytes/exit2 after original V1 field14 scanned prefix262145 over bound262144 (actual full length Unavailable), engine 51213 uncapped reports in500ms/exit71. Strict S historical custody is Blocked (416844 expected,339367 surviving,77477 missing and four original native roots absent); N/M/K/I/E FAIL; independent R03 full-stage review FAIL/re-review NotRun. Nothing in these host tests reclassifies them.
