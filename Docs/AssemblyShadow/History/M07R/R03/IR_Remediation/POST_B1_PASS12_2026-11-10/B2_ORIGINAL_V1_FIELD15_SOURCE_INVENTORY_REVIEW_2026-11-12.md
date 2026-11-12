# R03 B2 — Original V1 field15 source/value inventory contract

**Stage:** Primary Implementation, source-admission only. **Date:** 2026-11-12 UTC. **Working branch:** codex/assembly-shadow-r01b-h1. **Code anchor:** hybridclr_demo@3e8d14f3adae98fc5a1b908f4669e3807dd1dec0. **Unchanged native:** il2cpp_plus@e5f8eebca1263181ed3fca49e84a1cf73f40b90b; hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55; hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Read the latest pushed demo HEAD for this report and status-document changes.

## Objective and engineering boundary

The previous source gate proved that the **original enabled V1** GetExecutionDiagnosticsJson was byte-identical to a frozen 5,222-byte Git-blob-pinned fixture. Actual V1/frozen formatter differential tests passed for caller-owned immutable inputs. Neither proof independently enumerated every original header/class assignment with its exact producing expression and read order. This phase installs a separate **fail-closed mapping contract**, not a new Player collector or an acceptance claim.

The source of truth remains the exact original enabled getter in libil2cpp/vm/AssemblyShadow.cpp and the byte-identical fixture under Tools/AssemblyShadow/R03IR/NativeDiagnostics/OriginalV1ExecutionGetter_2026-11-12.txt (Git blob 7769a1ecde1941d17c055a094dabc5857b2bb163). The original code and its C++ runtime behavior have NOT been modified.

## Source-accurate inventory

**Eleven header assignments, in original construction order:** stateCode, state, generation, methodChecks, shadowMethodChecks, rejectedBaselineMethods, baselineClassCctorStarted, shadowClassCctorStarted, interpreterTransformations, shadowInterpreterTransformations, droppedClassObservations. The contract fixes the source expression for every value: state and generation from state/active, load orders for totals/subsets, and original relaxed-load cctor/counter metrics. The independently appended live R02 suffix is not equivalent to one frozen capture without a temporal proof.

**Eleven per-class assignments, in original construction order:** logicalAssembly, typeKey, interpreterShadow, physicalInterpreter, isActive, cctorStarted, cctorFinished, hasInitializationException, staticStoragePointer, pointerDetailsAvailable, staticStorageAvailable. Original logicalAssembly is the *physical owner name*, interpreterShadow is baseline || shadow, physicalInterpreter evaluates Interpreter(owner), and isActive is !baseline. Preserve the debug-only pointer string policy and the original no-storage empty-string behavior.

**Read sequence and exact limitations:**

1. If R02 diagnostics Level >= 2, snapshot non-null registry pointers in s_executionClasses order under ExecutionObservationLock; release that lock **before** any physical metadata or per-class value read. The registry snapshot is not a class-lifetime ticket.
2. If rows are present, CaptureShadowEnumeration obtains token-valid **physical** assemblies, including interpreter and zero-TypeDef images. MetadataTypeImages uses unordered-map emplace: **first handle owner wins**. The earlier B2 restricted AOT first-owner comparison covers admitted handles only, not the entire image map.
3. Read active/state and independent totals/subsets. For each original registered class, FormatMetadataOnly(&klass->byval_arg, images) may allocate, fail or consult metadata not admitted by the restricted current B2 source. This stage does not authenticate interpreter, open VAR/MVAR or every composite/generic shape.
4. Only static_fields is sampled under a short g_MetadataLock. The three cctor/exception booleans are separate relaxed atomic reads *after* that lock. A pair of observed stable samples cannot rule out ABA, a subsequent mutation, class/GC lifetime changes, or a coherent whole-VM epoch failure.
5. Append each row using the actual serializer, then append the **live** R02 diagnostics separately; neither a consistent cross-field timepoint nor a terminal-safe field15 result follows.

The current inactive source may continue to reject unsupported AOT/interpreter/metadata shapes and must revoke positive receipts on failure. The source contract is not permission to substitute a partial class list for the original field15.

## Implementation and validation

The existing Tools/AssemblyShadow/R03IR/b2_definition_source_gate.py now runs inspect_original_v1_field15_contract **after** exact four-repository Git blob admission and original enabled getter byte-fidelity checks. It matches all 11 heading and 11 class assignments with their original right-hand expressions **and order**; enforces the source-scope milestones for registry capture, first-emplace image map, physical vs logical mapping, metadata type key, per-class static/ctor reads, debug pointer formatting and live R02 append. The emitted JSON adds legacyField15SourceInventory with a truthful source mapping result and explicit false lifetime/full-field/epoch/native-V2/runtime predicates. It does not modify the manifest's 63-native/eight-demo source pins.

The associated test_b2_definition_source_gate.py adds **four** focused unittest methods: one positive exact frozen-source inventory and **20** deliberately mutated semantic inputs (four header, eight class-field, eight source/lifetime/R02 changes) which must be rejected. Primary standalone Python local execution: **4/4 new methods PASS**, all 20 mutations rejected. The pre-existing test suite remains in the existing macOS/Ubuntu exact-four-pin workflow, which checks source identity, branch HEADs and closed handoff. CI for the current docs commit must be independently inspected at the exact final SHA before a new CI verdict is recorded. This is **no Unity build, real class metadata test, or Player execution**.

## Review findings and next task

- **B2-F15-INV-01 / scoped PASS:** exact original V1 field names, producing expressions, field order and independent read sequence are now machine-checked against a frozen authentic original getter. Source-only test mutations reject changed semantics. Structural and literal source checks cannot by themselves prove runtime correctness.
- **B2-F15-INV-02 / OPEN:** original getter's row source can include class types and metadata handles outside the restricted AOT source. Physical matching and owner validation of admitted keys do not prove complete V1 row inclusion, class lifetime, true interpreter/VAR/MVAR support or unchanged metadata during capture.
- **B2-F15-INV-03 / OPEN:** the original getter has independent registry lock, metadata lock, cctor atomics and live R02 reads. Neither its own output nor the present B2 samples prove one coherent whole-VM epoch or terminal-safe no-allocation field15.
- **B2-F15-INV-04 / OPEN:** full original finalDiagnostics field14 and finalExecutionDiagnostics field15 still lack one preterminal owned authoritative snapshot compatible with native V2 descriptor-relative one-owner artifact/envelope and independent identity-bound external receipt/first recovery.

**Next bounded Primary phase:** use this fixed original-source inventory to design and implement the **first independently testable complete-class source capture boundary** (include interpreter/open-generic negative cases, class/GC/metadata lifetime and race/ABA decision) without activating the legacy getter or overclaiming complete V2. Independently verify real original header/row parity from genuine Unity metadata before authorizing the eventual one-use Local build/Player batch. Do not begin H2/M08A/X02/SNAP-01.

**Acceptance and authorization remain false:** readyForNativeV2FieldCapture=false, nativeV2TransportImplemented=false, firstRecoveryAuthenticatedV2=false, runtimeAcceptance=false, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, wholeVmEpoch=NotProven. PureInterpreter remains disabled. Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md remains CLOSED / NO EXECUTION. Historic native B1 oneuse-12 real Player focused 19/19 PASS is consumed and is not B2 acceptance; independent full R03 FAIL/High findings remain open.
