# R03 B2 — execution field15 formatter differential and observed class-fact stability

**Stage:** Primary Implementation. **Reviewed native source:** `night-outlook/il2cpp_plus@74c049a8f9d60465e1d656c36306b0e8cd015608`, branch `codex/assembly-shadow-r01b-h1`. Other runtime/Unity forks unchanged at `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. Demo HEAD changes with this report and related docs; use latest remote SHA at handoff. **Date:** 2026-11-12 UTC.

## Objective and preserved boundaries

Advance B2 toward the **complete original execution V1 JSON semantics (future V2 field15)** in two source-owned, testable steps:

1. Verify that the ORIGINAL V1 execution serializer plus its **live R02 formatter**, and the frozen bounded execution Record plus its **frozen R02 formatter**, produce **exactly identical bytes when supplied identical immutable headers, class rows and counter values**.
2. Detect obvious changes to per-class cctor started/finished/initialization-exception booleans and static storage address **between the two existing authenticated physical class enumerations, and during the second callback's TypeKey formatting**, then reject rather than publish stale immutable class data.

The original enabled `AssemblyShadow::GetExecutionDiagnosticsJson` body remains byte-identical to the 5,222-byte frozen reference in `Tools/AssemblyShadow/R03IR/NativeDiagnostics/OriginalV1ExecutionGetter_2026-11-12.txt`. No existing original V1 getter, B1 native first-failure source, shadow selection, interpreter execution or public Player invocation was modified. The prior first-emplace owner reconciliation still applies only to admitted AOT TypeDef handles, not every possible original V1 execution row. The authoritative [current source manifest](../../../../../../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins **63 native source/ABI/host/CI Git blobs and eight demo pure/reference files**.

## Implemented native changes

### Actual original execution field15 serializer differential

New host-only `NativeHostTests/AssemblyShadowExecutionV1SerializerParityHost.cpp` compiles the ACTUAL source for:

- `AssemblyShadowExecutionSerializer.h`: original V1 `Begin`, `AppendClass`, `EndClasses`, JSON escapes/booleans/order;
- `AssemblyShadowR02Diagnostics.h` and `AssemblyShadowObservationCounters.h`: original live R02 formatter/counters;
- `AssemblyShadowFrozenExecutionRecord.h`, `AssemblyShadowFrozenR02Serializer.h`, `AssemblyShadowR02Snapshot.h`: independently frozen owned record and R02 suffix;
- `AssemblyShadowDiagnosticWriter.h`: actual bounded writer.

The host creates one valid live R02 counter snapshot and a caller-owned set of class-row primitives, constructs the legacy text using **the same calls as the original getter**, and separately freezes the owned record. It compares every byte, not a parsed or normalized JSON object. Cases cover zero, one, two and three class rows, AOT/shadow/interpreter flags, cctor/exception/static fields, UTF-8, escaping, pointer details, large 64-bit counters and the **entire original R02 suffix**. Malformed UTF-8, aliased memory and incorrect row counts fail closed. A guarded host allocator confirms **zero new calls during frozen formatting**; no host allocation override is included in libil2cpp. Two explicitly divergent cases demonstrate a changed cctorStarted bit or an R02 live counter increment produces unequal valid JSON; this difference must not be promoted to field15 acceptance.

No mock serializer or handwritten JSON grammar replaces the original source in this test. However, every test row is **synthetic caller-owned data**, not a genuine Unity `Il2CppClass` read or a globally coherent VM snapshot.

### Native observed class-fact consistency

`libil2cpp/vm/AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` now uses an exact 16-byte `ClassFacts` primitive per original registry slot (up to the existing 2,048-slot table; **32 KiB of temporary bounded stack storage**). After the **first** physically matched, independently AOT-registration-proven source callback, it records only three original V1 displayed cctor/exception booleans and the numeric `static_fields` pointer value. On the **second** authenticated physical callback it compares these facts before TypeKey processing and re-reads them after TypeKey processing, before copying a row to the owned buffer.

A visible change yields new `ObservedClassFactsChanged`, rejects the whole capture, revokes source receipts/rows/frozen record and clears all positive `observedClassFactsTwoPassStable`/match counters. A successful source can report `observedClassFactsMatched == registered` and `observedClassFactsTwoPassStable=true` only after the existing original first-owner/source-inventory, physical membership, R02, native B1 and active-state fences finish successfully. All temporary address-value snapshots are reset within the original `g_MetadataLock` scope and initial metadata Reader. No class pointer or metadata handle is retained in the frozen record.

Existing physical class enumeration count remains **two**; no new allocator, managed invocation, original getter mutation or interpreter path is introduced. These checks detect **observed** changes, not ABA or changes after the final read. The 32-KiB thread-stack impact requires real Unity validation; no live `Class::Init`/GC object lifetime provenance is claimed.

## Tests and evidence

| Actual test | Verified result | Claim allowed |
| --- | --- | --- |
| [Actual original-vs-frozen field15 serializer host CI 43178421718](https://github.com/night-outlook/il2cpp_plus/actions/runs/43178421718) | **4/4 PASS**, macOS/Ubuntu × C++11/C++17. 16 Release/Debug strict/ASan-UBSan processes, **10 cases/91 assertions and six matching class rows per process**, zero guarded allocation | Exact legacy/frozen **JSON formatter** byte identity for identical immutable host inputs; plus independent counter/ctor divergence behavior |
| [Final actual inactive class-source .inl host CI 43179088289](https://github.com/night-outlook/il2cpp_plus/actions/runs/43179088289) | **4/4 PASS** at final native source HEAD; 16 Mac/Linux C++11/17 Release/Debug strict/sanitized processes, **75 physical source scenarios/1,849 assertions per process**, two new cctor/static drift negatives | Existing real source .inl compiled against synthetic VM; detects field changes between its two mocked physical class iterations |
| [Exact 63-native/eight-demo four-repo source CI 43179431213](https://github.com/night-outlook/hybridclr_demo/actions/runs/43179431213) | **2/2 PASS**, macOS/Ubuntu, exact Git blobs, pinned original V1 enabled getter, source-matched live/frozen R02 field/Metric order, manifest false-full-field flags | Static source identity/admission, not official Unity native TUs or real Player |
| Earlier original owner and Unicode source CI | Prior independently attributed results remain in historical source reports | Necessary bounded source assumptions; no promotion to full field15/VM epoch |

The initial differential workflow failed because its assertion threshold was set above 75 checks, although its compiled host printed successful byte equality. After correcting that test threshold and adding two meaningful drift cases, final CI passed (91 checks). Do not misinterpret intermediate CI REDs as a native implementation defect or infer real Unity acceptance from green host tests.

## Independent source review findings

- **F15-FMT-01 — actual serializer parity, scoped PASS.** The source uses original execution `Begin/AppendClass/EndClasses` and original live R02 `AppendDiagnostics`; the other path uses actual `FrozenExecutionRecord`, frozen R02 and bounded Writer. Byte equality for identical immutable fields is demonstrated in compiled C++11/17 both platforms. The cross-fork source gate checks the live/frozen R02 field/Metric sequence. **Not genuine runtime source capture.**
- **F15-FMT-02 — class/owner provenance, NOT PROVEN.** Validity of complete class inventory, all interpreter/VAR/MVAR/unsupported TypeKeys and metadata class lifetime remain outside restricted AOT source coverage. Real `AssemblyShadow.cpp`, `Class.cpp`, `Assembly.cpp` full Unity native TU and GameAssembly are **NotRun**.
- **F15-FMT-03 — class-fact read fence, scoped PASS.** New two-pass checked facts reject witnessed cctor/static changes in mock CI and clear receipt flags on failure. It does **not** make class facts, metadata, GC, or global counters atomic or postterminal-safe. Mutations after the final read, ABA and independent R02/metadata activity remain unresolved.
- **F15-FMT-04 — resource impact, requires real validation.** Frozen record capacity remains 3,932,160 bytes; physical owner scan unchanged except the new temporary per-slot 16-byte facts, bounded **32 KiB** on the native call stack. Unity IL2CPP worker/thread stack safety and actual GC/RSS/profiling are **NotRun**.
- **F15-FMT-05 — live/frozen divergence is meaningful.** Changing a class fact or R02 counter between the two samples yields different valid JSON. This demonstrates why the earlier healthy-time original-vs-bounded byte probe is only observational; a failed comparison may be a timing difference, not a serializer defect. There is no license to substitute an old partial field15.
- **F15-FMT-06 — full terminal V2 remains blocked.** Original full `finalDiagnostics` field14 and `finalExecutionDiagnostics` field15 require a defensible terminal/source/lifetime boundary. Neither original V1 allocating getters nor these host serializer tests produce it. Native preopened descriptor-relative V2 artifact/envelope/external receipt, independent recovery, whole-VM epoch, GC and original-S identity/Player acceptance remain missing. Original R03 full-stage FAIL and High IR findings remain open.

## Earliest next Primary work and conditional Local matrix

**Primary next:** establish a source-accurate, fail-closed **complete original nonempty execution V1 field15 class inventory and value-capture plan**, including real class/GC/metadata lifetime and the unavoidable race/ABA model. Decide and implement a terminal-safe full snapshot boundary (or explicitly document why original full field15 cannot be captured under terminal no-allocation/no-lock constraints); include original full general field14. Then implement complete native V2 binary/descriptor-relative one-owner artifact/envelope transaction, external identity-bound receipt/readback and negative replay/symlink/torn-write tests. Independently review and push exact four-SHA source; only then open one fresh executable WEB_TO_LOCAL.

**Future single-batch Local Validation, NOT currently authorized:** verify four clean exact repositories, **63 native/eight demo source** admission, Unity 2022.3.62f2 Mac ARM64 IL2CPP C++11 Bee/SDK/Original-S and fresh owner-only absent roots; run **one** full real native build with three distinct Players (Empty/initializer19/generic guard15), complete original field14/field15 byte comparisons with real class cctor/static/GC mutations, physically registered AOT/interpreter owners, Unicode/composite/primitive keys, B1 reason preservation, full native V2 and external receipt identity/provenance/readback, crash/GC/RSS/first-call/performance and independent immutable host/product/raw custody. Historical B1 oneuse-12 focused 19/19 PASS is consumed and cannot be reused.

**Current flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. PureInterpreter disabled. Do not start H2/M08A/X02/SNAP-01 or self-approve the Human Review Gate.
