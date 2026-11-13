# Current Primary — explicit root/non-root TypeDef use-site roles (2026-11-13 UTC)

Inactive B2 `il2cpp_plus@94e5312b8ee167384820f8ab58ee9661dfc7bfb3` now classifies TypeDef root/non-root roles by actual **call site**, not handle equality. One authenticated handle used both ways has both role bits in one pair. New synthetic regression `GenericRootAlsoArgument`; [Primary review and limits](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_EXPLICIT_ROOT_NONROOT_ROLE_REVIEW_2026-11-13.md).

Combined <=128 handles / <=64-byte names / <=24,576-byte scratch unchanged. New native/demo CI at these exact commits **not yet independently verified**. Not a VM/GC epoch, full field14/15, native V2, Unity Player or R03 acceptance. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — shared exact root/non-root TypeDef audit (2026-11-13 UTC)

Inactive B2 `il2cpp_plus@f89b9e9323df1234bf1bc59ca7f418533c958246` now copies and rechecks exact names (<=64 bytes per namespace/simple-name), declaration/generic indices and arity for **both admitted root and non-root TypeDefs**, using the same <=24,576-byte scratch object. The **128 distinct-handle capacity is now COMBINED** and can reject B2 inputs previously admitted with >128 root TypeDefs; this requires redesign/real source census before any product activation. Per-role positive receipts and fail-closed source error behavior remain. [Scoped design/source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_SHARED_ROOT_NONROOT_TYPEDEF_DECLARATION_REVIEW_2026-11-13.md).

[Native source host CI 43373757923](https://github.com/night-outlook/il2cpp_plus/actions/runs/43373757923) **4/4 PASS** Mac/Linux C++11/17, 133 synthetic-VM cases/6,623 assertions per process. [Four-repository code source CI 43374160198](https://github.com/night-outlook/hybridclr_demo/actions/runs/43374160198) **2/2 PASS** Mac/Linux at code anchor, 64-native/eight-demo exact blobs; final documentation HEAD CI checked separately. This is NOT a coherent VM/GC/class lifetime epoch, official Unity Player, full original field14/15, or native V2. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — bounded non-root TypeDef declaration consistency (2026-11-13 UTC)

**Inactive native implementation:** il2cpp_plus@bf9b17175b56090ad5ac05f699864b79358204a2 now compares exact captured non-root TypeDef declaration namespace/name bytes (<=64 each), declaring/generic indices and arity at final metadata sampling for <=128 authenticated handles. Late changes reject; a second-pass failure now exits before partial metadata audits can overwrite its first error. [Source design and Primary review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_NONROOT_TYPEDEF_DECLARATION_CONTENT_REVIEW_2026-11-13.md).

[Exact native CI 43361925344](https://github.com/night-outlook/il2cpp_plus/actions/runs/43361925344) **4/4 PASS** macOS/Ubuntu C++11/17, 126 scenarios/5,637 assertions per synthetic-VM process. [Demo code-anchor source CI 43362278126](https://github.com/night-outlook/hybridclr_demo/actions/runs/43362278126) checked 64 native/eight demo files; final docs SHA CI must be verified separately. **Not** complete root/full-V1 metadata, coherent class/GC/VM epoch, actual Unity Player, terminal-safe field14/15, or authenticated native V2. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**.

---

# Current Primary — bounded non-root TypeDef end-pass owner audit (2026-11-13 UTC)

Native inactive B2 il2cpp_plus@8901942f5d04e97cf8cad59a6dc2922c1d40ceee now rechecks **up to 128 distinct admitted non-root TypeDef handle/physical owner pairs** (nested declarations, generic arguments, primitive defaults) after three class passes and the second original physical V1 image snapshot. Reuses original first-emplace owner policy with a separate <=65,536 lookup limit; no extra class traversal or full metadata/VM epoch claim. [Detailed Primary source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_NONROOT_TYPEDEF_ENDPASS_OWNER_REVIEW_2026-11-13.md).

[Native exact-source host CI 43358606294](https://github.com/night-outlook/il2cpp_plus/actions/runs/43358606294) **4/4 PASS** Mac/Linux C++11/C++17, 120 scenarios/5,221 assertions per synthetic-VM process. [Four-fork source audit 43358990655](https://github.com/night-outlook/hybridclr_demo/actions/runs/43358990655) **2/2 PASS** Mac/Linux at demo code anchor; final docs SHA CI must be checked separately. This still does **not** prove full TypeDef metadata contents/class/GC lifetime/whole-VM epoch, official Unity Player, complete terminal field14/15 or authenticated native V2. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**.

---

# Current Primary — original V1 root-owner end-pass check (2026-11-13 UTC)

**Inactive B2 source:** il2cpp_plus@2ded6fa7deac7a52890aee917516fe9cdb42b128 now rechecks each authenticated class root TypeDef's first-emplace owner against the ORIGINAL physical token-valid V1 image order during the existing third class pass. Four new indexed-handle-table mutation negatives reject stale root ownership even when class pointers and image tokens remain constant. Uses a separate <=65,536 metadata lookup budget; no new class traversal or extra large stack buffer. [Source review and remaining risks](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ROOT_FIRST_OWNER_ENDPASS_RECHECK_REVIEW_2026-11-13.md).

**Exact source evidence:** [native CI 43351671250](https://github.com/night-outlook/il2cpp_plus/actions/runs/43351671250) **4/4 PASS** macOS/Ubuntu × C++11/C++17 (115 synthetic-VM scenarios, 4,656 assertions per process); [demo code-anchor CI 43352312987](https://github.com/night-outlook/hybridclr_demo/actions/runs/43352312987) **2/2 PASS** 64-native/eight-demo physical source audit. Final documentation commit CI must be checked separately. No complete original V1 metadata table, GC/class lifetime, coherent VM epoch, real Unity Player, terminal-safe full field14/15 or native V2. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — packed B2 class facts reduce stack bound (2026-11-12 UTC)

Native il2cpp_plus@39ac1a66b906da12825e095de010cae7cf5a8161: inactive B2 root/cctor facts use 1024 dense primitive records plus 2048 uint16 registry-slot indices, <=53264 bytes instead of 98304, saving >=45040 bytes on the reviewed ABI. Source exact slot semantics, three-pass comparisons and fail-closed scrub retained. [Source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PACKED_CLASS_FACTS_STACK_REVIEW_2026-11-12.md). [Exact native CI 43346655116](https://github.com/night-outlook/il2cpp_plus/actions/runs/43346655116) 4/4 PASS Mac/Linux C++11/17, 111 cases/4237 assertions per process (synthetic VM). [Demo source anchor CI 43347245365](https://github.com/night-outlook/hybridclr_demo/actions/runs/43347245365) 2/2 PASS 64-native/eight-demo sources; final docs CI separately verified.

Official Unity Player/worker-stack/GC and terminal full field14/15, whole-VM epoch and native V2 remain unproven. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — exact observed class root/source consistency (2026-11-12 UTC)

**Source implementation** at il2cpp_plus@c37adc9f7cb610b524ae32b176cbc3e3f67cd35b: the inactive B2 class capture now checks root image, TypeDef handle, byval type/tag/payload and generic pointer in the same physical observations as cctor/static facts; a witnessed change fails closed and revokes rows/receipts. [Native source mock CI 43218731616](https://github.com/night-outlook/il2cpp_plus/actions/runs/43218731616) Ubuntu C++11/17 Release/Debug strict/sanitized **2/2 PASS**, 106 cases/3194 assertions per execution; macOS native jobs queued at checkpoint. [Detailed review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_CLASS_ROOT_SOURCE_FENCE_REVIEW_2026-11-12.md).

**Limitations:** ClassFacts buffer now max 96KiB at 64-bit (+64KiB), requiring official Unity native worker-stack validation. Pointer equality is neither metadata/GC provenance nor a whole-VM epoch. Full original field14+15, actual Unity Player parity and authenticated native V2 remain blocked. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, PureInterpreter disabled; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — original V1 physical image primitive drift fence (2026-11-12 UTC)

**Native source:** il2cpp_plus@376bcf58bf4728828abab4618f331a9e445450f9 now double-samples token-valid original V1 physical image TypeDef count, image token and assembly token (not just pointer/order); a changed primitive or duplicate registration rejects all owned rows and source receipts. Five new negative cases in checked-in actual native .inl synthetic-VM host [CI 43211384982](https://github.com/night-outlook/il2cpp_plus/actions/runs/43211384982) **Ubuntu C++11/17 2/2 PASS**, 99 cases/2841 assertions per process; macOS jobs queued at review. [Source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_IMAGE_FACTS_FENCE_REVIEW_2026-11-12.md). Native B1/real V1 getter and other forks unchanged.

**Scope:** adds 12KiB bounded thread stack; no full TypeDef handle-map, class/GC/VM epoch, real Unity native TU/Player, complete field14/15 or native V2 acceptance. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION.

---

# Current Primary — interpreter-only physical V1 TypeDef source without AOT requirement (2026-11-12 UTC)

**Native source:** il2cpp_plus@f8bf89b42cfb20ab716b7d55a7ce91d20f1875b3 removes the unrelated global requirement for a nonempty registered-AOT TypeDef inventory while retaining per-AOT owner checks and original V1 physical first-owner for plain interpreter CLASS/VALUETYPE. The inactive source now admits interpreter-only physical image inventories in the bounded supported subset. Six new host scenarios (two positives, four negatives) passed in [Ubuntu native CI 43208481081](https://github.com/night-outlook/il2cpp_plus/actions/runs/43208481081), 94 cases/2553 assertions per process; macOS jobs queued at review. [Implementation/source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_INTERPRETER_ONLY_NO_AOT_SOURCE_REVIEW_2026-11-12.md). All original enabled V1 getter, B1 and active Player code unchanged.

**Still incomplete:** actual Unity/HybridCLR Player metadata, full registered class shape inventory, class/GC/VM epoch, complete terminal field14 and15, native V2 envelope/receipt/recovery. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no Local batch is authorized.

---

# Current Primary — restricted simple interpreter TypeDef source (2026-11-12 UTC)

**Implementation:** native il2cpp_plus@90206c7b4abdbf756c8fb1f2c353fcdf78a792e6 extends the inactive B2 field15 source to plain nongeneric/nonnested interpreter CLASS/VALUETYPE definitions with original V1 physical token-valid image and first-emplace metadata-owner proof. Previous AOT generic/composite paths unchanged; interpreter generic/nested/composite/VAR/MVAR fail closed. [Source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_SIMPLE_INTERPRETER_TYPEDEF_SOURCE_REVIEW_2026-11-12.md). Original enabled V1 getter and native B1 unchanged.

**Host/source evidence:** [native CI 43206145229](https://github.com/night-outlook/il2cpp_plus/actions/runs/43206145229) Ubuntu C++11/17 PASS (88 source cases, 2389 assertions/process); macOS jobs queued at review. [Four-pin source CI 43206474551](https://github.com/night-outlook/hybridclr_demo/actions/runs/43206474551) Ubuntu PASS at demo anchor 46ea3a35c3a89f9c0ab25ef8b7a0d51e575f2833; macOS queued. Full native Unity C++ TU/Player and real interpreter metadata/GC lifetime remain NotRun. R03 B2 not accepted; WEB_TO_LOCAL CLOSED / NO EXECUTION; full field14/15, VM epoch and native V2 remain missing. No Human Review Gate approval.

---

# Current Primary — end-of-collection class facts recheck (2026-11-12 UTC)

**Primary native source implementation:** [B2 end-pass source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_END_OF_COLLECTION_CLASS_FACTS_IMPLEMENTATION_REVIEW_2026-11-12.md). The inactive physical-AOT class capture now adds a **third end-of-collection physical enumeration** under the original metadata lock/initial Reader to compare every previously owned class's cctor/static facts; a later row's TypeKey cannot mutate an earlier row unnoticed at this final sample. Five additional negative cases reject late cctor/static changes, earlier-row mutation during a later TypeKey, missing and duplicate final callbacks, poison all receipts. Native il2cpp_plus@04d979fe55cea6b2dee7f5bfc49a71f2f1fb6386; other native/package forks unchanged. [Native source CI 43199686419](https://github.com/night-outlook/il2cpp_plus/actions/runs/43199686419) at source-review checkpoint **Ubuntu C++11/C++17 PASS**, 81 scenarios/2,126 checks/process; Mac jobs still pending. [Exact four-fork source CI 43200124015](https://github.com/night-outlook/hybridclr_demo/actions/runs/43200124015) **2/2 PASS** at demo code anchor 74891c675ebcb449b0a65721266d7e1559b12a03. Review final CI at final demo HEAD separately.

**Boundary unchanged:** third sampling is NOT a whole-VM epoch, complete original nonempty field15, terminal-safe full field14/15, real Unity C++ TU/Player or authenticated native V2. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**. Next Primary owns class-shape/GC/metadata lifetime and full V2 transport.

---

# Current Primary — exact original execution V1 field15 source inventory (2026-11-12 UTC)

**Current source-only checkpoint:** [Mapping/source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_FIELD15_SOURCE_INVENTORY_REVIEW_2026-11-12.md) records all **11 original V1 field15 header + 11 per-class assignments**, exact producing expressions and ordering; original registry/image/typekey, cctor/static/debug pointer and independent live R02 read boundaries are now fail-closed in b2_definition_source_gate.py. Four new locally run Python tests **PASS** with 20 intentionally divergent source cases rejected; cross-fork CI needs the exact final HEAD result checked separately. The original enabled getter and all three native/package branches are UNCHANGED. This proves source mapping ONLY, not real Unity class capture, lifetime, terminal field14/15, whole-VM epoch or native V2.

**Status:** R03 B2 incomplete; readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**. No Local build/Player or Human Review Gate authority.

---

# Current Primary — actual V1 field15 serializer differential and class-fact drift fencing (2026-11-12 UTC)

**Canonical native source:** il2cpp_plus@e5f8eebca1263181ed3fca49e84a1cf73f40b90b, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, all branch codex/assembly-shadow-r01b-h1; demo SHA is latest pushed branch HEAD. [63-native/eight-demo source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json).

**Implemented and source-tested:** Compile the ACTUAL original execution V1 std::ostream JSON serializer and live R02 suffix against the ACTUAL frozen Record/Writer and frozen R02 suffix. They produce **identical complete JSON bytes for identical immutable host class rows/counters**; differing cctor/R02 inputs correctly produce different bytes. [Differential CI 43178421718](https://github.com/night-outlook/il2cpp_plus/actions/runs/43178421718) **4/4 PASS**, Mac/Linux C++11/17 Release/Debug strict/sanitized, ten cases/91 assertions/process, six matching class rows, zero guarded formatter allocations. The inactive native bounded physical class source now also checks original cctor started/finished/exception and static-storage identity across both existing class enumerations and after TypeKey formatting; witnessed drift produces typed rejection/clears all positive receipts. [Native source CI 43180369312](https://github.com/night-outlook/il2cpp_plus/actions/runs/43180369312) **4/4 PASS**, 75 mock source cases/1,865 assertions/process. [Four-fork source CI 43179431213](https://github.com/night-outlook/hybridclr_demo/actions/runs/43179431213) **2/2 PASS**, new exact R02/formats and 63/8 sources. **No real Unity C++ TU, original live metadata/GC, GameAssembly or Player; byte parity is limited to the same immutable host inputs.** [Design, source review, limits and next Primary stage](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_EXECUTION_FIELD15_SERIALIZER_AND_CLASS_FACTS_REVIEW.md).

**Not completed:** original full field15 source/class inventory and real Unity byte parity, original terminal-safe complete field14/field15 with coherent source lifetime, native descriptor-relative V2 artifact/envelope/independent receipt/recovery. Historical consumed B1 oneuse-12 focused real Player 19/19 PASS is not B2. Independent R03 full-stage FAIL/High findings remain. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no Local execution, H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary — original V1 physical first-emplace owner reconciliation (2026-11-12 UTC)

**Current source:** il2cpp_plus@648f3b2c5c0d0b86954c339ac3d75fdb96ce1ba2, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de on codex/assembly-shadow-r01b-h1; read current pushed hybridclr_demo HEAD from GitHub. [Exact 57-native/8-demo source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) includes the original V1 getter frozen body and two new independent pure original-V1 physical image/first-owner mirrors.

**Source correction and implementation:** Original execution V1 `Assembly::CaptureShadowEnumeration` uses `CopyValidAssemblies` (token-valid **physical** assembly order, interpreter/zero-TypeDef INCLUDED), **not** `GetAllAssemblies` logical mapping. The inactive bounded source previously read only registered AOT images, so it could choose a different metadata TypeDef owner from V1 if an interpreter image earlier advertised the same handle. Primary added a no-allocation original-V1 token-valid image visitor under original assembly lock plus initial metadata Reader, with a bounded **first-emplace owner comparison for every admitted AOT TypeDef/ancestor/composite/primitive leaf** before any TypeDef dereference. It double-samples the original image order and fails closed on first-owner mismatch, absent owner, changed source or budget. Does not modify original V1 getters, B1, or HotUpdate runtime behavior. [Independent design, source review, tests and future Local matrix](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_FIRST_OWNER_RECONCILIATION_IMPLEMENTATION_AND_REVIEW.md).

**Source/host tests:** [actual native .inl mock 43175217165](https://github.com/night-outlook/il2cpp_plus/actions/runs/43175217165) **4/4 PASS** (16 Mac/Linux C++11/17 Release/Debug strict/sanitized processes, 73 actual source scenarios and 1,673 assertions/process); [pure original-V1 first-owner host 43174989182](https://github.com/night-outlook/il2cpp_plus/actions/runs/43174989182) **4/4 PASS** (12 cases/41 assertions/process, no protected allocations); [exact source audit 43175578270](https://github.com/night-outlook/hybridclr_demo/actions/runs/43175578270) **2/2 PASS** (57-native/8-demo Git blobs, 27 negative tests per OS). A newer exact-source run may exist at final demo HEAD; verify separately. **No official Unity native `Assembly.cpp`/GameAssembly or real V1 original getter/Player ran.** This is only admitted-key first-owner subset parity, not complete field15.

**Still Primary-owned:** full original nonempty V1 field15 class/JSON byte/semantics parity with real metadata (and temporal class/GC/ctor/static source), complete terminal-safe full original field14/15, authenticated single-owner descriptor-native V2 envelope/artifact/independent receipt and first recovery. Original independent R03 FAIL and High IR findings remain; historical B1 oneuse-12 focused real Unity Player 19/19 PASS is consumed/immutable. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no new Local execution or H2/M08A/X02/SNAP-01.

---

# Current Primary — original V1 healthy-time observational field15 probe, NO full V2 (2026-11-12 UTC)

**Current source:** night-outlook/il2cpp_plus@2670b6cfc7006c9483c4c9322808c152efa16772, unchanged hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, all on codex/assembly-shadow-r01b-h1; read the latest hybridclr_demo remote HEAD. The [53-native/six-demo exact source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) includes a byte-identical **5,222-byte original enabled V1 GetExecutionDiagnosticsJson source** and all new source/tests.

**New Primary implementation:** Inactive TryProbeBoundedExecutionV1ByteParity holds an initial-session metadata Reader, invokes the unchanged ORIGINAL allocating V1 execution getter, independently acquires the restricted source-owned physical AOT class/TypeKey record, and runs a bounded, one-shot exact JSON byte comparer. Typed mismatch reports lengths/first offset and irrevocably revokes the bounded record/legacy output; even equal bytes are two observations, not a coherent VM epoch/full field15. Original V1 getter was verified unchanged against the frozen predecessor. [Native actual .inl + fake V1 adapter CI 43146481197](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146481197) **4/4 PASS** across Mac/Linux C++11/17, 16 Release/Debug strict/sanitized executions of 67 physical-source + three parity-adapter cases and 1,258 assertions/process. [Pure comparator CI 43146317881](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146317881) **4/4 PASS**, 10 cases/42 assertions per process. [Exact source parity gate 43147578102](https://github.com/night-outlook/hybridclr_demo/actions/runs/43147578102) **2/2 PASS**, 25 negative/admission Python tests per OS, 53 native/six demo source blobs and original getter byte fidelity. **Synthetic reference in host tests is not real legacy V1; no Unity full native TU, GameAssembly or new Player.** [Design, implementation, independent findings, conditional one-batch plan](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_OBSERVATIONAL_ORIGINAL_V1_PARITY_PROBE_IMPLEMENTATION_AND_REVIEW.md).

**Next Primary:** prove real logical-vs-physical metadata owner map and complete original V1 nonempty class/field15 parity under a valid class/GC/metadata source epoch; complete terminal-safe original full field14/15 and authenticated native descriptor-relative V2 binary/envelope/independent receipt. Historic oneuse-12 B1 focused real Mac Player 19/19 PASS is consumed, original independent R03 FAIL and High IR findings remain. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven. PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no new Local or H2/M08A/X02/SNAP-01.

---

# Current Primary — original switch-equivalent null-safe primitive source, full B2 still blocked (2026-11-12 UTC)

**Current canonical source:** native il2cpp_plus@68530d7ecb86c9122d9ae5eb20366ccb0ea086b6; unchanged hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de; latest hybridclr_demo remote HEAD must be read at use time. All four on codex/assembly-shadow-r01b-h1. [42-native/four-demo exact manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json).

**Primary corrective implementation:** Original Class::FromIl2CppTypeEnum uses an IL2CPP_ASSERT on absent defaults. Instead of calling it directly, the inactive physical AOT TypeKey producer now uses the new assert-free existing-default Peek with **all 19 original switch mappings mechanically checked against the exact original Class.cpp** by the cross-fork source audit; null defaults fail closed. Physically registered AOT metadata owner, class/name/arity/generic-container proof, earlier composite/Unicode TypeKeys, original metadata Reader and B1/R02 source fences are retained; the original V1 getter, native B1 and original Class.cpp remain unchanged. [Final native .inl mock CI 43141452521](https://github.com/night-outlook/il2cpp_plus/actions/runs/43141452521) **4/4 PASS**, 16 Mac/Linux C++11/17 Release/Debug strict/sanitized processes, **67 source scenarios, 20 direct primitive-peek cases and 1236 assertions each**. [Final four-fork source CI 43141581601](https://github.com/night-outlook/hybridclr_demo/actions/runs/43141581601) **2/2 PASS**, 42 native Git blobs/four demo source mirrors, **22 negative tests per OS**. Source/mock only; **no official Unity Class.cpp/AssemblyShadow.cpp full TU, GameAssembly or new Player**. [Source review, corrected assertion risk, limits and next plan](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md).

**First incomplete Primary:** real full original V1 nonempty execution field15 byte/semantic parity on live Unity classes/primitive defaults; complete terminal-safe original field14+15 with metadata/class/GC lifecycle; one-owner authenticated descriptor-relative native V2 artifact/envelope/independent receipt. R03 independent FAIL and High IR-R03-01/02 unchanged; old oneuse-12 B1 real Player focused PASS 19/19 is consumed. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven. PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) CLOSED / NO EXECUTION, no H2/M08A/X02/SNAP-01.

---

# Current Primary — bounded primitive defaults source, full field15 still blocked (2026-11-12 UTC)

**Source tuple:** il2cpp_plus@f6530b221f0ef98ff38436ca8cd2692304d63265, unchanged hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, all on codex/assembly-shadow-r01b-h1. Current hybridclr_demo exact HEAD must be read from GitHub. [Exact 41-native/4-demo manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) source-authenticates original Class.cpp/Class.h and Il2CppClass metadata ABI.

**New Primary implementation:** the inactive actual physical-AOT TypeKey source can admit a primitive generic argument **only** when original Class::FromIl2CppTypeEnum returns a previously initialized il2cpp_defaults class whose image, metadata TypeDef handle, namespace/name, nonnested and nongeneric class shape are independently proven from the original registered physical AOT source under the initial-session metadata Reader and lock. No class construction/cache population, surrogate primitive name or original V1 getter change. Composite, Unicode and existing B1/R02 source fencing remain. [Final native host source mock 43139433481](https://github.com/night-outlook/il2cpp_plus/actions/runs/43139433481) **4/4 PASS**, 16 C++11/17 macOS/Ubuntu Release/Debug strict/sanitized host processes, **67 typed scenarios and 1,195 assertions each**. [Exact 41-native/four-demo four-pin CI 43139844512](https://github.com/night-outlook/hybridclr_demo/actions/runs/43139844512) **2/2 PASS**, 21 negative/admission tests per OS. These are source/mock tests, **not a real Unity Class.cpp full TU, GameAssembly or Player**. [Detailed source design, independent review and future consolidated Local matrix](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md).

**First unfinished Primary stage:** original complete nonempty execution field15 byte/semantic parity with real metadata, valid class/GC/terminal lifecycle, full terminal-safe field14+15 native source and independently authenticated descriptor-relative native V2 artifact/envelope/receipt. Source subset completion is not full V2. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven. Historical consumed B1 oneuse-12 focused real Player 19/19 PASS, independent full R03 FAIL and High IR-R03-01/02 unchanged. PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no new one-use Local batch or H2/M08A/X02/SNAP-01.

---

# Current Primary — original Unicode assembly folding source-only (2026-11-11 UTC)

Native fork on codex/assembly-shadow-r01b-h1: night-outlook/il2cpp_plus@db5354a9befd5cfd02f907d3169c8106e0a29305; unchanged hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. The current demo HEAD must be read from GitHub. [38-native/4-demo exact source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins the original Unicode name/table/UTF16->UTF8 references and test-only shim.

**New Primary source:** The inactive actual physical AOT TypeDef capture now calls the original AssemblyShadowName::ViewName/NameHash/NextFolded under original metadata locks and initial-session Reader, using C++11 bounded folded UTF-16->UTF-8 owned TypeKey assembly names. This extends the previous nested GENERICINST/PTR/SZARRAY/ARRAY/qualified TypeDef subset to Unicode assembly names. Original V1 getter and B1 first-error are unchanged. Three separate host source tiers include the actual .inl synthetic VM, a pure partial-fold mock and an **original Name.h plus original Unity Unicode lowercase tables** reference host. At initial checkpoint: Ubuntu C++11/17 strict/sanitized PASS; macOS CI jobs pending; do not infer complete four-OS jobs. [Source, evidence and independent review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md).

**Still Primary-owned blockers:** authenticated primitive TypeKeys; complete V1 nonempty field15 byte parity; terminal-safe full general field14/execution field15 and original class/GC/metadata lifetime; authenticated native descriptor-relative V2 writer/envelope/receipt. No Unity native TU, GameAssembly or new real Player test was run. Historical consumed B1 oneuse-12 19/19 PASS remains focused only; original R03 independent FAIL and High IR findings remain. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**. No H2/M08A/X02/SNAP-01.

---

# Current Primary — bounded composite TypeKeys source-only (2026-11-11 UTC)

**Native branch source:** night-outlook/il2cpp_plus@272f3077eee50835284e27855352fe300362ad79 on codex/assembly-shadow-r01b-h1; interpreter and Unity package remain pinned at hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55 and hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. Read current hybridclr_demo branch HEAD from GitHub. The [26-native/4-demo candidate manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) authenticates source and false product flags.

The **inactive** native physical AOT TypeDef source now supports bounded nested constructed GENERICINST, pointer, SZARRAY, ranked array and qualified argument TypeKeys from registered physical TypeDef owners. The original V1 getter/B1 producer and historical oneuse-12 real Player 19/19 focused PASS remain untouched. [Pure composite CI 42992930075](https://github.com/night-outlook/il2cpp_plus/actions/runs/42992930075) **4/4 PASS**, [actual native .inl mock 42993897217](https://github.com/night-outlook/il2cpp_plus/actions/runs/42993897217) **4/4 PASS**, and [source four-pin CI 42994963528](https://github.com/night-outlook/hybridclr_demo/actions/runs/42994963528) **2/2 PASS** with 18 negative tests/OS. **No official Unity TU/GameAssembly/Player B2 or V2 full field capture has run.** [Primary design, code review, incomplete source gates and eventual one-batch Local matrix](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md).

**Still blocked:** primitive/open/Unicode canonical keys, original nonempty V1 execution field15 parity, terminal-safe complete general field14/execution field15, descriptor-relative authenticated native V2 writer and receipt, whole-VM epoch and R03 original-S acceptance. readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven. PureInterpreter disabled; [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**, with no new Local or H2/M08A/X02/SNAP-01.

---

# Current Primary — bounded registered AOT TypeDef owner and zero-TypeDef regression (2026-11-11 UTC)

**Latest native source:** `night-outlook/il2cpp_plus@8627a93f4f307c8d2c99e7edada54573a93cc312` on `codex/assembly-shadow-r01b-h1`; `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de` unchanged. The *inactive* execution diagnostic source now uses the original `Assembly.cpp` registered physical AOT table to verify concrete generic TypeDef owners, including images with **no observed class**, under original assembly/metadata locks and initial-session Reader. The bounded scanner skips legitimate AOT assemblies containing zero TypeDefs, rejects malformed AOT sources and unregistered/ambiguous owners, and invalidates changed source snapshots. Original first-error and V1 getters remain unchanged. This is not complete V1 execution capture, terminal-safe source custody or a VM epoch.

**Source and host evidence:** [native source mock 42988174617](https://github.com/night-outlook/il2cpp_plus/actions/runs/42988174617) **4/4 PASS** (macOS/Ubuntu × C++11/17 × Release/Debug × strict/sanitized; **16 host processes, 672 typed cases, 7,776 assertions**, no reported sanitizer errors). [Exact source gate 42988434479](https://github.com/night-outlook/hybridclr_demo/actions/runs/42988434479) **2/2 PASS**, 23 native files, 3 independently tested demo source headers, 16 negative/admission test functions per platform, `PassedInactiveSourceOnly_NotFullV2`. [Source implementation/review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_REGISTERED_AOT_OWNER_IMPLEMENTATION.md) and [canonical native candidate roster](Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json). **No official Unity2022/IL2CPP GameAssembly native build or new Player test** has executed for this source.

**Remaining Primary:** complete original canonical composite TypeKeys and actual nonempty V1 execution field15 byte parity, prove metadata/class source lifetime through terminal recovery, complete full `finalDiagnostics` (field14) and `finalExecutionDiagnostics` (field15), integrate and independently authenticate V2 binary/envelope/receipt. R03 original-S/whole-VM epoch and High IR findings remain open. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`, PureInterpreter disabled; the consumed B1 oneuse-12 focused real Player 19/19 PASS is preserved. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**. No new Local or H2/M08A/X02/SNAP-01.

---

# Current Primary — registered AOT generic argument ownership; full B2 blocked (2026-11-11 UTC)

**Current native source:** `il2cpp_plus@f08cb329fb19eaa47eaa8075e62dbc3f2d42cf8a`, branch `codex/assembly-shadow-r01b-h1`, fixed `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The inactive `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` now recognizes generic `CLASS/VALUETYPE` arguments from **registered AOT images without any observed class**: it borrows a bounded raw physical assembly table snapshot under the original assembly lock plus metadata lock and initial-session Reader, proves each TypeDef handle's owning image before dereference, and compares registered image inventories twice. The existing observed-class source matching, original V1 getter/B1 first-error and frozen execution/R02 serializer remain unchanged. This is not a whole-VM epoch, full TypeKey grammar or terminal-safe V2 capture.

**Empirical source/host checks:** [final native source mock 42986790417](https://github.com/night-outlook/il2cpp_plus/actions/runs/42986790417) **4/4 PASS** (Mac/Linux × C++11/17, Release/Debug × strict/sanitized, 16 mock executions, **656 scenarios / 7,408 assertions**, zero reported sanitizer errors). [Final exact four-repository source audit 42987239404](https://github.com/night-outlook/hybridclr_demo/actions/runs/42987239404) **2/2 PASS**, **23 Git-pinned native files plus three independently tested demo header files** including original raw Assembly registry code and pure scanner; output `PassedInactiveSourceOnly_NotFullV2`. [New design, review and source limits](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_REGISTERED_AOT_OWNER_IMPLEMENTATION.md) and [exact-source candidate manifest](Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json). No new actual Unity/IL2CPP/GameAssembly/Player test occurred.

**Next Primary work:** complete canonical composite TypeKey coverage and original V1 nonempty execution field15 parity under authentic metadata lifetime, then terminal-safe full field14/15, descriptor-relative native V2 transaction and independent receipt. Original oneuse-12 B1 19/19 focused real Player PASS remains immutable, independent R03 overall FAIL and both High findings remain open. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**. No Local run or H2/M08A/X02/SNAP-01.

---

# Current Primary — bounded observed cross-image AOT owner source; B2 remains incomplete (2026-11-11 UTC)

**Native candidate:** `night-outlook/il2cpp_plus@cfb33d58432b05f3d28052dfb88677a0561f6c93` on `codex/assembly-shadow-r01b-h1`, with fixed `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The inactive `TryCaptureBoundedDefinitionExecutionLive` now resolves canonical `GENERICINST` TypeDef argument keys across different AOT images **only when another registered observed class has independently matched that physical image** under the first-session metadata Reader. Two physical iterator passes share one `g_MetadataLock`; a fixed 64-image inventory is scrubbed before release. Unobserved/ambiguous/unsupported image owners, lost second-pass classes, over-budget metadata and unsupported type shapes reject. Original legacy getters and B1 first-error producer are unchanged.

**Scope-accurate CI:** [Final native source mock 42983247910](https://github.com/night-outlook/il2cpp_plus/actions/runs/42983247910) **4/4 PASS**, Mac/Linux × C++11/17 × Release/Debug × strict/ASan-UBSan: **16 mock processes / 592 scenario executions / 6,336 assertions**, no reported sanitizer errors. [Final 20-native/3-demo Git-source admission 42983166781](https://github.com/night-outlook/hybridclr_demo/actions/runs/42983166781) **2/2 PASS**, with original physical iterator, actual metadata/TypeKey ABI, OS recursive-lock evidence, exact four branch pins and negative source-gate tests. [Detailed new source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_BOUNDED_CROSS_IMAGE_AOT_OWNER_IMPLEMENTATION.md) and [exact candidate manifest](Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json). This is **real native `.inl` compiled against a mock VM**, NOT an official Unity/IL2CPP GameAssembly build or new Player test.

**Next Primary gap:** full physical image coverage when an argument's image has no observed class; composite/qualified/array/Unicode/open generic TypeKeys; actual V1 field15 byte parity and safe postterminal field14/15 capture; authenticated descriptor-relative native V2 writer and independent receipt, B3 whole-VM epoch and historic original-S gaps. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`. B1 oneuse-12 real Player focused PASS 19/19 remains immutable; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**; no Local authorization or H2/M08A/X02/SNAP-01.

---

# Current Primary — restricted same-image GENERICINST native source validated in mock (2026-11-11 UTC)

The current native fork is `night-outlook/il2cpp_plus@20a57e58098e3476dad5459f04f9fc730c3848c1` on `codex/assembly-shadow-r01b-h1`. An inactive, source-owned physical AOT class-capture path now handles simple/nested metadata TypeDefs, generic **definition** arity, and the additional original canonical `GENERICINST` grammar **only for a same-image generic definition plus 1–16 independently owner-verified concrete AOT TypeDef arguments** (4,096-byte key limit). Typed records are immutable, ordered by original registration slot, and feed the **unchanged** frozen execution/R02 serializer. It rejects foreign/unowned, qualified, open, compound generic argument, array/pointer, Unicode assembly-folding and postterminal cases. It does **not** read real full generic-class state in Unity; original V1 getter and B1 paths remain untouched.

**Test evidence:** [Native `.inl` source mock 42979860514](https://github.com/night-outlook/il2cpp_plus/actions/runs/42979860514): 4/4 Mac/Linux C++11/17 jobs successful, Release/Debug × strict/sanitized: **16 host runs, 496 typed scenarios, 3,888 assertions**, no sanitizer diagnostics reported. [Pure composer 42978349307](https://github.com/night-outlook/il2cpp_plus/actions/runs/42978349307): 4/4 success, **8 native runs / 624 assertions**, zero protected allocations. [15-native/3-demo exact Git source audit 42980498037](https://github.com/night-outlook/hybridclr_demo/actions/runs/42980498037): **2/2 success** including original canonical TypeKey C++ source and actual generic runtime ABI. [Design and source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_SAME_IMAGE_GENERICINST_IMPLEMENTATION_AND_REVIEW.md) records exact limits and residual risk. These are only **host/mock and source-identity** results, not Unity/IL2CPP Player validation.

**Next Primary work:** complete cross-image/compound canonical types and original V1 field15 parity, terminal-safe field14, independently bound native V2 writer/receipt and VM metadata-lifetime proof. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`. Original oneuse-12 B1 focused 19/19 real-Player PASS is preserved. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**, no new Local run. PureInterpreter disabled; no H2/M08A/X02/SNAP-01.

---

# Current Primary — B2 native physical TypeDef source at 4c900; Local CLOSED (2026-11-11 UTC)

**New actual native source (still inactive):** `night-outlook/il2cpp_plus@4c900ab22735768f517d81daccfed31a3d9aeb1e` adds `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` in the VM, separate from the legacy getter. It binds observed registry/witness identities to physical first-match AOT TypeDefs under `g_MetadataLock` and the initial-session metadata Reader, validates same-image nested ancestry and definition arity, copies bounded owned source rows and outputs the original native frozen execution/R02 schema for the **restricted healthy-time subset**. It refuses staged generic/declaring indices, malformed/foreign/cyclic source, reversed-callback ordering mismatches, B1 terminal publication racing source collection, stale metadata admission, and incomplete registry/counter snapshots. It **does not** support full generic/array/qualified/unicode-assembly TypeKeys or complete postterminal V2 field15. No Unity native Player has built this new source yet.

**CI evidence with exact source attribution:** [Native mock 42974759134](https://github.com/night-outlook/il2cpp_plus/actions/runs/42974759134) **4/4 PASS at predecessor `fd1bc0...`**, Mac/Linux C++11/17 × Release/Debug × strict/sanitized, **16 mock processes / 320 scenarios / 2,528 assertions**. [Earlier source admission 42975024429](https://github.com/night-outlook/hybridclr_demo/actions/runs/42975024429) **2/2 PASS at predecessor source**, not the final ten-blob manifest. Current `4c900...` adds the real `Il2CppTypeDefinition` layout include; [native final-source CI 42975604704](https://github.com/night-outlook/il2cpp_plus/actions/runs/42975604704) is now **4/4 completed/success**. [Exact ten-blob source CI 42976195767](https://github.com/night-outlook/hybridclr_demo/actions/runs/42976195767) had Ubuntu Passed and macOS Queued at this checkpoint. No current final-source all-OS acceptance is asserted; `PassedInactiveSourceOnly_NotFullV2` remains the only admissible source-audit result. [Exact candidate manifest](Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json), [detailed design/source/evidence review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PHYSICAL_DEFINITION_LIVE_IMPLEMENTATION.md).

**Acceptance:** B1 oneuse-12 remains focused real-Player **19/19 PASS**, not new B2 validation. `readyForNativeV2FieldCapture=false`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `nativeV2TransportImplemented=false`, `wholeVmEpoch=NotProven`; PureInterpreter disabled. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) **CLOSED / NO EXECUTION**. The next Primary-owned work remains full canonical TypeKey/source semantics and terminal-safe native field14/15 plus authenticated descriptor V2 transport, before any fresh one-use Local batch.

---

# Current Primary — B2 nonempty owned execution bytes / real frozen R02 host PASS (2026-11-10 UTC)

**New Primary-only implementation:** restricted **bounded UTF-8 canonical definition TypeKeys** (ASCII-foldable assembly names, nested metadata definition declarations, no constructed/qualified generic forms), immutable 1024-class/256KiB owned row staging with original slot order and eight class flags, and adapters that use the **real** native `AssemblyShadowExecutionSerializer` and `AssemblyShadowFrozenExecutionRecord` with a synthetic typed R02 snapshot. Every source is test-only under `Tools/AssemblyShadow/R03IR/NativeDiagnostics`; there is no native fork/production VM edit or new Unity build. [Implementation/source review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_OWNED_NONEMPTY_EXECUTION_IMPLEMENTATION.md) covers source shape, exact failures and rollback.

**Empirical host scope:** four successful dual-OS C++11/17 strict/sanitized workflows ([TypeKey](https://github.com/night-outlook/hybridclr_demo/actions/runs/42801925182), [owned rows](https://github.com/night-outlook/hybridclr_demo/actions/runs/42802730095), [real serializer](https://github.com/night-outlook/hybridclr_demo/actions/runs/42803482307), [real frozen record + R02](https://github.com/night-outlook/hybridclr_demo/actions/runs/42804244546)): **16/16 jobs, 32 native host executions, 2,520 passed assertions, zero protected allocations**. All machine results explicitly deny physical VM source and V2 runtime acceptance. One early serializer CI failed because of test-only include shadowing, repaired by the real Unity `vm/...` include root; original RED preserved.

**Remaining first-blocking Primary task:** actual physical `Il2CppClass` registry/witness source with safe metadata lifetime, full canonical constructed/nested/generic/qualified TypeKeys, nonempty execution class semantics and original V1 parity; then terminal-safe full general field14, independent identity-bound V2 file transport. The previous [exact-source readiness gate](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_VM_SOURCE_READINESS_GATE.md) still correctly says `readyForNativeV2FieldCapture=false`. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**. B1 oneuse-12 focused PASS remains historical, R03/H2/Human Review Gate false and PureInterpreter disabled.

---

# Current Primary — B2 full-field source admission remains BLOCKED (2026-11-10 UTC)

**New Primary code/test:** `Tools/AssemblyShadow/R03IR/bounded_v2/b2_source_readiness.py` and 12 source/pin-drift regression tests inspect original V2 slots 14/15 and **eight exact** native fork source blobs. [Final source CI 42793741078](https://github.com/night-outlook/hybridclr_demo/actions/runs/42793741078): macOS and Ubuntu 2/2 PASS; each explicitly returns `sourceAudit=PassedPinnedStructuralInspection` and **`readyForNativeV2FieldCapture=false`**. [Source audit/provenance and next changes](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_VM_SOURCE_READINESS_GATE.md).

**Why blocked:** complete `finalDiagnostics` and `finalExecutionDiagnostics` require original VM fields; B1 native first-error is not a substitute. General bounded source has initial-session Reader/observable fences but lacks accepted terminal/full-VM semantics. Live execution bounded source deliberately rejects nonempty observed classes; physically copied display names are not canonical execution TypeKeys. Completing no-allocation full class rows, metadata lifetime and exact legacy parity is Primary-owned. Previous B2 C++11/17 compiler and 376 native host tests remain PASS **within host-only scope**. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**; B1 oneuse-12 remains focused PASS, R03/H2/Human Review Gate false, PureInterpreter disabled.

---

# Current Primary — B1 oneuse-12 PASS reconciled; B2 host C++11 compatibility fixed (2026-11-10 UTC)

**Current source-only result:** original B2 C++11 codec/host was RED on Mac/Linux at [42789420796](https://github.com/night-outlook/hybridclr_demo/actions/runs/42789420796) while C++17 passed. Primary corrected only the inactive V2 codec/POSIX source and standalone host C++11 syntax/initialization without changing wire/receipt semantics. [C++11/17 source CI 42789933778](https://github.com/night-outlook/hybridclr_demo/actions/runs/42789933778) **4/4 PASS** and [full strict/sanitized dual-OS wire+POSIX 42790274635](https://github.com/night-outlook/hybridclr_demo/actions/runs/42790274635) **4/4 PASS, 376 host tests**. Exact code/receipts and limits: [B2 compatibility remediation](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_CPP11_COMPATIBILITY_REMEDIATION.md).

**B2 remains incomplete:** the canonical V2 slots 14/15 are *full* `finalDiagnostics` and `finalExecutionDiagnostics`, **not** B1 code/reason. Their bounded full VM native sources, metadata lifetime/epoch, real Player transport and independent receipt joins are not yet complete. See [B2 source findings](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_SOURCE_REVIEW.md), [B2 design and plan](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md). [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / NO EXECUTION**, no new Local batch authorized. Original oneuse-12 is consumed and focused B1 PASS (19/19), not R03 acceptance; flags and Human Review Gate remain false.

---

# Current Primary — B1 oneuse-12 focused PASS reconciled; B2 implementation next (2026-11-10 UTC)

**Latest authoritative Local:** oneuse-12 executed **once** at demo `2d690bb2f7234ddcbee339f9da7125d687f5ed45`, and returned **19/19 focused PASS** (Unity2022.3.62f2 macOS arm64 IL2CPP one successful build, zero errors/one warning; three real Players PID 8760/8777/8787, B1 Empty 0/0/0, initializer 2/19/2, captured generic 2/15/1; exact native V1 reason equality, linked allocator exclusion, separate immutable verification receipts, real B2 host-only source tests and regular-only 534-member product seal). Local evidence publication: `hybridclr_demo@9c210801c8da1e8371a09c25e0ef708a6d130fc3`. Read [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) first, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md) and the [oneuse-12 checkpoint](History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/README.md).

**Primary reconciliation:** [B1 source/result/provenance scope](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/PRIMARY_EVIDENCE_RECONCILIATION.md) distinguishes authenticated selected Git receipts from full local raw rehash. The oneuse-11 allocator, product symlink and receipt-collision defects are verified resolved for this focused actual Player path only. Oneuse-12 is **consumed**. [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) is now explicitly **CLOSED / NO EXECUTION**, not a new Local command.

**Earliest incomplete Primary stage:** [B2-0 exact-source schema/ABI/lock/lifetime review](History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md), then isolated real native V2 descriptor writer/source integration, adversarial host CI and independent code review. Existing codec+POSIX tests remain **host-only**; no B2 Player implementation or fresh Local authority is currently published. The Unity Bee lump used C++11 while the V2 codec is documented as C++17 host code; this is a **compatibility verification requirement**, not an observed compilation failure.

**Acceptance boundary:** original independent full R03 FAIL and both High `IR-R03-01/02` open, historical strict custody Blocked, 17 retired roots/40 duplicate paths Unavailable. B2 integrated V2, B3 coherent whole-VM epoch, original S full source/object/link/Player provenance, GC/RSS/RC/P/E and qualification remain unaccepted. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; wholeVmEpoch=NotProven`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic Human Review Gate.

---

# Current Primary — oneuse-11 FAIL repaired in source; new oneuse-12 conditional (2026-11-10 UTC)

**Authoritative latest Local (oneuse-11, consumed): FAIL / ReturnRequired.** At source `hybridclr_demo@3ddbac666caf9b5ec2482467652eefd7c5e7833f`, one real Unity2022.3.62f2 macOS ARM64 IL2CPP ON/Release build succeeded, but all three Players exited -6/SIGABRT before B1/V1 raw evidence: the standalone B1 host driver's global allocator overrides were linked into GameAssembly. An intentional sanitized B2 descriptor negative-case symlink defeated the ordinary strict product seal; the later initializer B1 receipt path also collides with the exclusive V1 `verification.json` writer. Read [Local-owned return](Handoff/RETURN_TO_WEB.md) and [immutable oneuse-11 checkpoint](History/M07R/R03/local-validation-native-b1-20261109-oneuse-11/README.md).

**Current Primary correction**: native `il2cpp_plus@8aa8d09319a89b55b2496bcc2c69ccc69cb57be9` has moved only the standalone host driver to `NativeHostTests/`, outside Unity's production `libil2cpp` installation. Exact current source admission is now **14** pinned source files and **46** production VM-delta files. The batch will require actual installed roster and linked GameAssembly allocator-symbol exclusion; host-only tests cover this. Before any Player, it exclusively persists actual linked `nm -gU` stdout and a SHA-bound pass/fail attestation under `builds/candidate-release/native-b1-linked-symbols.nm` and `native-b1-linked-roster.json`; repeated verifications must be byte-identical. B2 strict/sanitized host data and intentional negative symlinks now live in separate authenticated raw custody, and the product archive remains regular-only with the strict symlink rejection intact. V1 and B1 initializer receipts are now exclusively written to distinct immutable `verification.json` and `verification-b1.json`. Native implementation B1 VM semantics and original historical S/source pins unchanged.

**Next Local:** [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) is one **new conditional oneuse-12**. Mandatory exact-final-demo-SHA dual-OS CI, both OS job-level completed/success, real Mac/SDK/Original S/custody admission, two fresh >=25GiB >=60-sec samples and **three** never-used absent roots precede ONE 19-cell / one Unity build / three fresh Players. Read [Primary remediation and tests](History/M07R/R03/IR_Remediation/POST_B1_FAILED11_2026-11-10/PRIMARY_REMEDIATION_DESIGN_TEST_PLAN.md). Prior oneuse-09 focused pass is historical-only; oneuse-11 is consumed, not retriable. No oneuse-12 runtime evidence exists yet.

**Boundary**: Independent full R03 FAIL, High IR-R03-01/02 open, original strict S custody Blocked, 17 retired roots and 40 copies Unavailable, actual B2 integrated V2 writer/B3 whole-VM epoch/full S/GC-RSS-RC-P-E unaccepted. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary — B1 oneuse-10 source admission BLOCKED, corrected oneuse-11 conditional (2026-11-09 UTC)

**Latest Local, immutable:** oneuse-10 source `7c8af27e63038c77c13171c5776760e869e9c09d` → Local publication `e75cb536626358b69d7bbd90837a2044a2fab86a`: **PrerequisiteBlocked/NotRun**. Six required dual-OS CI jobs passed and standalone source 14/47 passed; the **shared** Mac/runner admission still checked obsolete 11/45. Its actual exit2 said `Eleven-file source proof not passed`. Coordinator 0, builds 0, Players 0, 19/19 cells NotRun. Both reserved oneuse10 output roots absent but consumed and must never be reused. Retained original S/custody remained read-only; historical strict custody Blocked and 17 retired roots/40 duplicates Unavailable. Read [Local report](Handoff/RETURN_TO_WEB.md) and [Primary focused remediation](History/M07R/R03/IR_Remediation/POST_B1_BLOCKED10_2026-11-09/PRIMARY_ADMISSION_REMEDIATION.md).

**Primary-owned correction:** `run_current_native_validation_cycle.validate_sources` (shared Mac and runner), `run_current_native_host_preflight.inputs` (inner host) now enforce reviewed **14** exact current-source files and **47** exact native VM paths at `il2cpp_plus@a0209bf4285db3f0d0fc66d8817578235438cef4`, rejecting old/unknown cardinalities, wrong SHA/Git blob/profile/branch. Host/CI source tests exercise real four sibling Git roots on both Mac/Linux and original source readers, with Mac/SDK/Original-S mocked only in CI. Three active current-native CI workflows now pin the same native B1 SHA; original historical source evidence unchanged. Old oneuse-I receipt remains historical-only, not rebound as new B1 acceptance.

**Next Local:** [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) defines a **new, conditional oneuse-11** with new absent roots, fresh CI at exact final demo SHA, independent real Mac/SDK/custody/Original-S admission and **new** 2×>=25GiB/60-sec capacity checks. Only then one source-pinned batch (19 cells, one real Unity2022.3.62f2 Mac ARM64 IL2CPP ON/Release build, three Players for initializer control/error19 and captured-generic error15, B1/V1 exact reason/PID join and inactive B2 host contracts). No Local execution has yet occurred for oneuse-11.

**Boundary:** Independent full-stage R03 verdict FAIL, High IR-R03-01/02 open; B2 native V2 integrated writer NotImplemented, B3 coherent VM epoch NotProven; original S full compiler/object/link/Player provenance, GC/RSS/RC/P/E and qualification unaccepted. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No Human Review Gate self-approval or H2/M08A/X02/SNAP-01.

---

# Current Primary — R03 Native B1 originating-first-error source prepared; conditional oneuse-10 (2026-11-09 UTC)

**New Primary-owned source:** `night-outlook/il2cpp_plus@a0209bf4285db3f0d0fc66d8817578235438cef4` adds fixed-storage lock-free immutable first-native-error B1 capture at actual guard/initializer/late-use/reference/unexpected origins (no full VM epoch or B2 writer). Source/current candidate manifests now bind 14 exact source files and 47 native VM paths; original historical `R03/source-pins.json` and all prior oneuse07/08/09 evidence remain unchanged. [Full B1 design/implementation/risks](History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B1_NATIVE_ORIGIN_IMPLEMENTATION_AND_REVIEW.md).

**New isolated one-use Local batch:** [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) is now **CONDITIONAL**, not yet executed: one **fresh** Unity2022.3.62f2 macOS ARM64 IL2CPP ON/Release build and **three** actual Players (initializer control0/Empty B1, initializer failure19/origin2, captured physical generic15/origin1), strict byte-identical original native V1 reason/PID/source identity, linked Bi4/AOT physical guard, B2 inactive codec+POSIX host source suites, original S archival/provenance/read-only checks, full output seal and four-repo postflight. **All mandatory final-source dual-OS CI, exact checkout, original S, SDK, custody, capacity and fresh-absent-root admission must pass before the one single invocation.** No historical replays or extra builds.

**Host-only evidence:** native C++11/17 fixed latch dual-OS PASS [42598105952](https://github.com/night-outlook/il2cpp_plus/actions/runs/42598105952); new dual-OS B1 probe C++11 mock-source and strict B1/parsing/preparer/coordinator tests PASS within their independent source-only CI scope. No official Unity SDK production translation unit or real new Player has run from this Primary environment. Local oneuse-10 evidence is NotRun until explicitly admissible.

**Acceptance unchanged:** original independent R03 FAIL, High IR-R03-01/02 open, original S full compiler/object/link/Player proof and strict historical custody Blocked, 17 retired roots/40 copies permanently Unavailable. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false`; PureInterpreter disabled. B2 actual V2 descriptor writer, B3 coherent whole VM epoch and RC/P/E/GC/RSS still Primary-owned. No H2/M08A/X02/SNAP-01/Human Review Gate self-approval.

---

# Current Primary — R03 captured-generic oneuse-09 focused PASS; native V2 B1 next (2026-11-09 UTC)

**Latest Local evidence:** oneuse-09 executed at demo bb5fce9c15450e68c6341d88270fbc30dd7b9738, published at 97cd47e06a837569ff62c4ac7744117d22966126. Exactly one authorized 19-cell run passed, with one genuine Unity2022.3.62f2 macOS ARM64 IL2CPP build and three real Players exit0. Both initializer regression controls reproduced linked Bi4/callback/field/mask and Commit0/state6 versus failure19/state9. The captured-generic Player preserved Committed6 after inflation, used the physical Methods.R03.Node TypeDef in the stable AOT method_inst, and the actual native method guard denied error15/state9. Its postterminal Runtime::Invoke reported an exception without changing the AOT counter1→1; the **exception type is unknown**.

**New bounded Primary verification:** the [Git-published raw/receipt crosscheck](History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/PRIMARY_RECONCILIATION.md) and 22 adversarial host tests passed dual-OS [CI 42570848609](https://github.com/night-outlook/hybridclr_demo/actions/runs/42570848609). It does not independently rehash the original entire 509-member sealed archive or physical GameAssembly/executable. The new [inactive C++ first-error freeze B0 candidate](History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md) passed real host C++11/17 tests [CI 42571591288](https://github.com/night-outlook/hybridclr_demo/actions/runs/42571591288), but **is not linked into the VM or a Player**. Native first-error B1 source integration, actual V2 writer, coherent VM epoch and original S full provenance remain uncompleted.

The consumed oneuse-09 [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) is now **CLOSED**; no new Local run authorized. Oneuse-08 remains PrerequisiteBlocked/NotRun, oneuse-07 focused initializer PASS, 17 owner-retired roots and 40 duplicate paths remain Unavailable/PermanentlyDeleted and historical strict custody Blocked. Original independent R03 overall verdict FAIL and High IR-R03-01/02 stay open. All acceptance/H2/qualification/Human Review Gate flags false; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic review gate.

---
# R03 captured-generic A2 — oneuse-08 CI-only prerequisite BLOCKED, new source verification prepared (2026-11-09 UTC)

Latest Local: candidate demo `26843412eda7034cd91c0754bdcde16d5517d814`, evidence publication demo `c9a5cf7a5e9c33a08db0a0f5f9bc1917e8c7ac25`. **oneuse-08 = PrerequisiteBlocked / NotRun**: 0 runner, 0 builds, 0 Players, 19/19 cells NotRun; both reserved roots absent. The sole failure is original Ubuntu workflow job `128946622207` in run `42551093381`, which still reports **status=in_progress / conclusion=success / completed_at populated**, despite completed successful steps and parent workflow. This inconsistency is not a PASS, does not represent runtime failure and is not waived. Original Mac admission/custody was read-only Passed and two historical capacity samples 45.853/45.851 GiB do **not** transfer to another run.

Primary added a strict [CI job-status admission source](Tools/AssemblyShadow/R03IR/captured_ci_job_admission.py) that rejects the actual immutable oneuse-08 `CI.json`, plus [adversarial regression tests](Tools/AssemblyShadow/R03IR/test_captured_ci_job_admission.py), exact Git source pins and dual-OS CI. Previous failed CI runs remain historical; only new *completed/success* jobs at the next exact final pushed SHA can authorize Local. [Reconciliation](History/M07R/R03/IR_Remediation/POST_CAPTURED08_2026-11-09/PRIMARY_CI_ADMISSION_REMEDIATION.md) describes original evidence and the fix.

A fresh **conditional oneuse-09** will be governed by [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) once published: one new actual Unity 2022.3.62f2 Mac ARM64 IL2CPP build, three fresh independent Players, fixed 19 cells, new disjoint output roots; strict seven-workflow/14-job live status, source/SDK/OriginalS/custody and two new >=25GiB capacity samples are mandatory before the *single* runner invocation. The blocked oneuse08 roots and published evidence remain untouched. No original native runtime/initializer/fixture is modified for this CI repair.

Independent R03 review still **FAIL**, High IR-R03-01/02 remain open, native V2/full VM epoch/original S compiler-link/Player/GC/RSS and qualification remain incomplete. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic Human Review Gate.

---

# Current Primary — R03 captured-generic A2 source implementation; conditional oneuse-08 (2026-11-09 UTC)

**A2 source and host work prepared.** The existing native physical-generic probe and 19-cell single-build/three-Player coordinator have been source-reviewed and corrected: test-only AOT owner no longer eagerly invokes `typeof(T)`; genuine generic inflation must leave the native world Committed=6 before the physical captured-argument method guard is credited; a post-terminal `Runtime::Invoke` must actually report a rejection rather than merely returning null. Host negatives cover an inflation-time failure, silent-null, escaped AOT body and forged native evidence. The new read-only authentic `il2cpp_plus` fork API audit verifies native header/implementation signatures and the `Runtime::Invoke` method-entry call path without using mocks. Seven exact-source dual-OS handoff trigger contracts are also checked. [Primary A2 source review](History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/CAPTURED_GENERIC_A2_PRIMARY_SOURCE_REVIEW.md).

**New Local handoff is CONDITIONAL, not already executed:** [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) defines one *new* oneuse-08, 19-cell, one actual Unity2022.3.62f2 macOS arm64 IL2CPP ON/Release build and three fresh independent Players (two initializer controls plus one physical captured-generic failure15). Exact-final-demo-SHA **seven mandatory dual-OS CI jobs**, fresh Mac source/SDK/capacity >=25GiB samples (new single-use allowance), preservation and original-S custody must all pass before one single invocation. **The public fork alone lacks Unity's vendor `Baselib.h`**: public-header-only compilation attempts remain Failed; a successful source audit is not an official Unity SDK C++ compile. Actual IL2CPP bridge/native/Git/Player evidence is Local Validation's mandate, not a source-level PASS.

Initializer oneuse-07 remains **focused PASS**, immutable. A2 genuine captured-generic error15, native V2 complete diagnostic transport, whole-VM epoch/shutdown, independent original S semantic compiler/link/Player provenance and High IR-R03-01/02 remain **NotAccepted**. Independent R03 overall FAIL unchanged. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`, PureInterpreter disabled. No automatic H2/M08A/X02/SNAP-01 or Human Review Gate approval.

---

# Current Primary — R03 captured-generic A1 host prerequisite passed, A2 pending (2026-11-07 UTC)

**New scoped Primary implementation:** `R03CapturedGenericAotOwner.Touch<T>` (test-only), isolated real .NET8 host, strict source/receipt consumer and negative tests. Actual `macos-15` and `ubuntu-24.04` CI [run 42363760691](https://github.com/night-outlook/hybridclr_demo/actions/runs/42363760691) passed C# compilation (0 errors/0 warnings), genuine CLR closed generic with owner outside `Methods`, three positive body/side-effect calls, eight host tests on each OS and output-reuse rejection. This is **structural host proof, not actual Unity/IL2CPP native error15 or runtime acceptance**. The new host Methods.dll SHA differs between OSes even though its MVID matches; it is never substituted for historical S.

Read [A1 source and empirical scope review](History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/CAPTURED_GENERIC_A1_OWNER_HOST.md) and [next Primary plan](History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/NEXT_PRIMARY_WORK.md). **Earliest incomplete Primary work is A2:** physical baseline argument / actual IL2CPP generic MethodInfo acquisition and native error15; A1 cannot grant a Local run. `WEB_TO_LOCAL.md` remains CLOSED. Original oneuse07 focused PASS remains immutable; independent High IR-R03-01/02 and full R03 FAIL remain open. All R03/H2/qualification/Human Review Gate flags false, PureInterpreter disabled. No Local build, H2/M08A/X02/SNAP-01.

---

# Current Primary — initializer oneuse-07 focused PASS; Local authority CLOSED (2026-11-07 UTC)

The latest Local outcome is **focused initializer PASS**: execution demo `6e1dc7b4349a386dc35c5ed46fca4225db273b18`, evidence-publication demo `66a0218ffb17e363531b7f7bc0f4114787ae0b76`. One authorized 15-cell run passed (one real Unity2022.3.62f2 macOS arm64 IL2CPP build, two distinct Players exit0); actual linked Bi4 phase103 preceded native callback299/300, with field3/mask15 and healthy 0/6 versus postprepared failure19/9, expected first-recovery sentinel. Host suite and bounded custody/product seal passed within declared scopes; old oneuse01–06 remain historical.

The oneuse-07 **WEB_TO_LOCAL is now consumed/CLOSED**. Read [postpass Primary reconciliation](History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/PRIMARY_RECONCILIATION.md), [next Primary work](History/M07R/R03/IR_Remediation/POST_INITIALIZER07_2026-11-07/NEXT_PRIMARY_WORK.md), and [current handoff status](Handoff/WEB_TO_LOCAL.md). The original execution handoff is retained at demo source `6e1dc7...`, not executable authority for another batch.

Both High findings `IR-R03-01/02` and independent full-stage R03 FAIL remain open. Captured-generic15, native V2/full first recovery, coherent VM epoch, original S full source/object/link/Player provenance, managed shutdown/GC/RSS and RC/P/E qualification are not accepted. Historical strict custody is still Blocked; 17 retired runtime roots/40 duplicates stay Unavailable. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`. PureInterpreter disabled. No Local build/Player, H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary — oneuse-07 mandatory CI source-pin reconciliation (2026-11-07 UTC)

The pending oneuse-07 runtime batch is still CONDITIONAL. At the previous demo `b0469e46c405`, the bridge-host and initializer-local-contracts workflows passed both operating systems, but the mandatory full current-native-host workflow failed on both operating systems before native-host execution. The separate current-native source-only workflow also failed. Raw GitHub Actions logs show a stale pre-bridge `R03Build.cs` blob pin, **not** a new Unity/Player outcome.

Primary updated only the *current candidate* source gate and candidate JSON to the exact reviewed conditional initializer builder Git blob `71c685f419d157bf3774996f28f2d075246cf4e4`, plus positive/negative source regression checks. The original `R03/source-pins.json`, all native fork pins, Build.cs implementation, original fixture roles, historical outputs and 15-cell oneuse-07 contract are untouched. Read the [pin remediation report](History/M07R/R03/IR_Remediation/INITIALIZER07_BRIDGE_2026-11-07/SOURCE_PIN_CI_REMEDIATION_2026-11-07.md) and [current WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md).

**Additional CI repair from the next exact source run.** The first follow-up demo commit `bc3a3fe89b8035bb81cc8c79128115bac1b6363a` reached and executed the full 8+2 current-native-host phase on both operating systems, and the previously broken read-only source-only workflow was successful. Nevertheless, mandatory run `42354711808` FAILED on both OS jobs in the next `Actual fresh Python CLI startup without PYTHONPATH or Unity` step: `current_native_cli_contracts.py::test_12_reviewed_current_source_files_are_pinned` had a separate stale copy of the same `R03Build.cs` blob `b993703d918090733a659bd7c3ac883cd5d753e1`. Primary now updates that isolated CLI test source pin to `71c685f419d157bf3774996f28f2d075246cf4e4` and adds explicit source/old-blob regression checks. All prior CI FAIL verdicts remain historical; a **new** commit's both-OS success is required before oneuse-07.

This is a source/CI prerequisite repair only. **Before** Local oneuse-07, all three mandatory workflows must have completed/success macOS15 and Ubuntu24.04 jobs at the exact **final** pushed demo SHA, plus fresh independent Local admission and two >=25 GiB same-volume samples. Any failure/skip/cancellation blocks execution. Oneuse01–06 outcomes and the 17 permanently retired roots/40 duplicates remain immutable/unavailable. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false`. No later milestone or Human Review Gate approval.

---

# Current Primary — R03 initializer oneuse-06 missing native Bi4 bridge; conditional oneuse-07 (2026-11-07 UTC)

**Original oneuse-06 Local Validation remains FAIL/ReturnRequired**, executed
at demo `611ad2e45a92ebfbd07cb64238bf2f47b5aff626`,
Local evidence published at `7ada3408a2a5f211a7acfdadd06c36a6c48e274c`.
One real Unity2022.3.62f2 macOS ARM64 IL2CPP build passed with 0 errors/1 warning,
ten current-native hosts, 47 initializer tests and original host/product
evidence seal passed separately. Both real Players exited2:
control PID30595 and failure PID30603, Commit19/state9,
strict V1 raw empty, native callback phases299/300 absent.
Actual VM recovery was `NotSupportManaged2NativeFunctionMethod`.
The generated native `MethodBridge.cpp` owned by the original build
had a null-only managed-to-native function-pointer table, while the
pinned V2 Cdecl no-arg int32 callback requires signature `Bi4`.
These facts support a missing generated bridge; they did NOT prove
anything about a repaired Player.

**Scoped Primary implementation:** preserve normal HybridCLR prebuild
generation, zero general hot-update analyzer assemblies, and the
original AOT baseline fixture role. In the *new isolated initializer
project only*, source/authenticate both V2 Methods DLLs and inject
exactly one `__M2NF_Bi4` Cdecl int32() stub + table entry into the
fresh normal generated source, rejecting missing/different/duplicate
identities and rechecks after Player build. Add real AOT
`R03_IRW_BridgeStatus` that reads the **actual linked** table
and emits phase103 before Commit. A correct phase103 and all
original native callback/field/Commit/canary/first-error predicates
are required for a focused pass; static source or nm symbols alone
are never enough.

The new [canonical conditional WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md),
[design/plan](History/M07R/R03/IR_Remediation/INITIALIZER07_BRIDGE_2026-11-07/DESIGN_AND_PLAN.md)
and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER07_BRIDGE_2026-11-07/PRIMARY_SOURCE_REVIEW.md)
are the current Primary instructions. Oneuse-07 has **not** run.
Before Local execution require three dual-OS host workflows at the exact
final pushed demo source SHA, independently fresh Mac/Unity/SDK/
surviving historical preservation, and two new >=25 GiB real
same-volume capacity samples. The 17 owner-retired runtime roots
and 40 duplicate paths remain `Unavailable/PermanentlyDeleted`;
strict historical custody remains Blocked, not silently waived.

Original oneuse01–06 checkpoints, the independent R03 FAIL and High
`IR-R03-01/02` remain immutable/open, as do native V2/complete
general diagnostics, captured-generic15, original-S complete
compiler/link/Player join, managed shutdown/VM epoch/GC/RSS,
RC/P/E/performance and qualification.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
No Human Review Gate, H2/M08A/X02/SNAP-01.

---

# Current Primary — oneuse-05 interpreted `__Internal` import failure; conditional oneuse-06 (2026-11-07 UTC)

**Original oneuse-05 FAIL is preserved, not reclassified.** Executed
demo `db232418adf2fc35c54ed72a8933a174f8218126`; Local evidence
publication `eeeec3ba574047c06b5b853e58a5b594e80c37ae`.
One real Unity2022.3.62f2 macOS ARM64 IL2CPP build, ten native hosts,
46 initializer tests, host custody and product seal passed within their
scopes. Two actual Players exited2 with empty strict V1 output and
source/PID-bound VM recovery `Unable to load DLL '__Internal'`:
the interpreted PInvoke attempted `dlopen(__Internal)` and never entered
`R03_IRW_OnPrepared`. The control's code19/state9 did not satisfy
healthy0/6; the failure code19/state9 was **not** the expected
postprepared sentinel. Original oneuse-01–04 records remain immutable.

**Reviewed narrow Primary correction:** the opt-in test-only dnlib
initializer targets now emit `__InternalDynamic`, matching the already
existing `PlatformInvoke::Resolve` current-program-symbol lookup
branch in the fixed native fork. The production resolver, AOT
`__Internal` managed imports, strict V1 callback/field/side-effect
predicates and older fixtures are unchanged. Actual .NET8 generation
on macOS15 and Ubuntu24.04 proved two deterministic new
SHA256/MVID target identities; the runner and strict admission pins
were updated, and a negative mutated legacy import must fail.
No corrected real Unity Player has yet run; current-process export
visibility, any missing PInvoke bridge and subsequent initializer
behavior remain unknown until fresh Local evidence.

Read the [new WEB_TO_LOCAL handoff](Handoff/WEB_TO_LOCAL.md),
[source-level design and execution plan](History/M07R/R03/IR_Remediation/INITIALIZER06_DYNAMIC_IMPORT_2026-11-07/DESIGN_AND_PLAN.md)
and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER06_DYNAMIC_IMPORT_2026-11-07/PRIMARY_SOURCE_REVIEW.md).
The new **oneuse-06** is conditional on three exact-final-demo-SHA
dual-OS CI workflows, fresh Mac original-S/source/SDK/preservation
and two genuinely new >=25GiB capacity samples. The 17
owner-authorized permanently deleted runtime roots/40 duplicate
paths remain `Unavailable`, not recreated or counted as intact
raw evidence; all remaining protected data must be authenticated.
Historical strict custody remains Blocked.

The independent R03 High `IR-R03-01/02` and all whole-VM,
nativeV2/full first-failure, captured-generic, original-S
link/Player, managed shutdown, GC/RSS and RC/P/E obligations
remain open. `R03Accepted=false`,
`H2Passed=false`, `ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`, `qualificationApproved=false`,
`fullLegacyRegressionAcceptance=false`, PureInterpreter disabled.
No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Owner-authorized readmission — initializer oneuse-05 after scoped storage retirement

The user requested resuming Local Validation after the explicitly approved retirement of17 runtime roots and all40 specified duplicate copies. Source/runtime/fixture/test/compiler inputs are unchanged. The prior immutable oneuse05 capacity-readiness report remains historical Blocked/NotRun; the actual oneuse05 batch has never been invoked and both product/host roots remain absent.

The exact retired paths remain Unavailable/PermanentlyDeleted_UserAuthorized. Historical verdicts and published checkpoints remain unchanged. All remaining protected inputs must still be authenticated; no additional missing or modified bytes are excused. No old root/app/SDK copy may be restored or reused.

Follow Handoff/WEB_TO_LOCAL.md. This Docs-only readmission commit must receive successful exact-SHA macOS15 and Ubuntu24.04 jobs in all three prescribed workflows before any runner invocation, followed by fresh source/Unity/SDK/original-S/custody admission and capacity rechecks. One fresh15-cell batch, one Unity2022.3.62f2 ON/Release build and two Players only. No retry, test/guard/timeout change or milestone advancement.

All R03/H2/qualification/runtime/Human Review Gate flags remain false.

---

# Current Primary — initializer oneuse-04 CapacityBlocked; read-only readiness and conditional oneuse-05 (2026-11-06 UTC)

**Published Local outcome remains BLOCKED**, not a runtime failure:
executed-input demo `e0f52c008b6b244e58be135e9bdba46192b76d04`,
Local evidence publication `c55950504e21b1a61044f818e1819946ec2dea7e`.
Original same-volume readings of the actual output parent were
**24.733444 GiB** and **24.729546 GiB**, both under mandatory
**25.0 GiB** (26,843,545,600 bytes). The latter deficit was
**290,398,208 bytes (~277 MiB)**. The reserved oneuse-04 roots
were never created; all15 cells, one build, two Players and native
initializer recovery remain **NotRun**. Source, SDK and historical
evidence preservation passed. Prior oneuse-01 BLOCKED and
oneuse-02/03 FAIL and their original seals remain unchanged.

**Primary remedy:** no deletion target is supported by the
evidence and no cleanup, relocation or threshold change is
authorized. Primary implemented a strictly no-write
`capacity_readiness.py` and 14 safety/negative host tests:
actual output-parent statvfs free bytes, canonical fresh
product/host roots, explicit source/SDK/evidence exclusion and
optional user-specified candidate inventory without following
symlinks. A single read-only sample is NEVER Unity authorization.
Additional capacity on the actual same APFS volume must be
established by the user or other separately approved action,
then **two new independent >=25 GiB samples** must pass.
Fixed20GiB hard/40GiB advisory rules remain unchanged.

Read the [current conditional WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md),
[new capacity readiness design/plan](History/M07R/R03/IR_Remediation/INITIALIZER05_CAPACITY_2026-11-06/DESIGN_AND_PLAN.md)
and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER05_CAPACITY_2026-11-06/PRIMARY_SOURCE_REVIEW.md).
Read-only readiness checks precede any new product root.
**Initializer oneuse-05 is conditional and has not been executed.**
Only after real user Mac capacity, source/CI/Unity/SDK/historical
preservation gates pass can one distinct fresh15-cell batch run
(one real IL2CPP build and two Players). A new native recovery
reason, strict V1 trace/Player and sealed host custody are still
required; the previous oneuse-03 pre-callback exception is unknown.

The independent R03 FAIL and High IR-R03-01/02 remain open.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary — initializer oneuse-03 pre-callback FAIL; conditional diagnostic oneuse-04 (2026-11-06 UTC)

**The genuine oneuse-03 Local Validation outcome remains FAIL / ReturnRequired.**
Executed demo `7a3b6c31408d8fd8b9fb5f74d78be4fa65670915`, evidence
publication demo `ec753f2facb4b2645083ed969d40d541c9f03cf4`:
one real Unity2022.3.62f2 macOS ARM64 ON/Release IL2CPP build, ten native host
components, 41 initializer host tests, original S archival audits, independent
host-custody and the **product evidence seal** Passed within their scopes.
Two actual separate Players exited2: strict V1 raw files remained zero bytes;
the authentic native journals recorded Commit19/state9 even for the control,
no phase299/300 callback, prepared state0, ReadPrepared -1 and Seal reason1.
That does NOT establish the intended initializer failure sentinel or a
postprepared field invariant. Both Players remain Failed; 13/15 cells Passed.
Previous oneuse-01 BLOCKED and oneuse-02 FAIL are unchanged.

**Primary source-side response:** HybridCLR's existing native initializer
catch stores its real exception message in the transaction's first terminal
recovery reason, which can be read with `AssemblyShadow::GetRecoveryInfoJson`
without formatting a managed exception after poison. A test-only preopened
`raw.json.vm-recovery.json` now captures that **existing** native reason,
bound to exact run/case/fixture/PID and strict parser. The original V1
callback/field/mask/Seal, deterministic DLL bytes and product VM are
unchanged; the current underlying precursor to the callback is *not
yet diagnosed as an actual implementation bug*. The next Local evidence
should discriminate pre-callback IL/delegate/generic/PInvoke failures.
The prior separate native journal, successful host custody and product
seal remain in force.

**New oneuse-04 is conditional**, not already executed. Read the
[current canonical WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md),
[design](History/M07R/R03/IR_Remediation/INITIALIZER04_PRECALLBACK_2026-11-06/DESIGN.md),
[execution plan](History/M07R/R03/IR_Remediation/INITIALIZER04_PRECALLBACK_2026-11-06/PLAN.md)
and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER04_PRECALLBACK_2026-11-06/PRIMARY_SOURCE_REVIEW.md).
Before a new Local invocation require dual-OS exact **final pushed demo SHA**
initializer and full current native host CI success, source-bound managed
Player C# and native writer host compiles, four exact clean Git remotes,
pinned macOS/SDK/original S, untouched historical evidence, fresh absent
oneuse-04 and sibling host roots, and **two new >=25.0GiB capacity samples**
(hard20/advisory40 otherwise unchanged). Do not reuse previous runs.

Independent R03 FAIL and High `IR-R03-01/02` remain open. Native V2/complete
general diagnostics, captured-generic error15, original S complete compiler/
link/Player chain, whole-VM epoch, managed shutdown, GC/RSS and RC/P/E
obligations remain unaccepted.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.
No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary — initializer oneuse-02 FAIL remediated in source; conditional oneuse-03 (2026-11-06 UTC)

**Original initializer oneuse-02 remains FAIL / ReturnRequired** at execution demo `7da27a486b529cdebf73100b5ce4c332a1bb7e86`, Local evidence publication `61bf436d65e5909767206d385ecba865e4c7a5ac`. Exactly one actual Unity2022.3.62f2 macOS arm64 ON/Release IL2CPP build Passed (0 errors, 1 warning); 13/15 cells Passed but both initializer Players exited 2 and their strict native `raw.json` files were zero bytes. The original product seal Failed on an intentionally created ten-host negative-test directory symlink. Original evidence remains unmodified; oneuse-01 remains BLOCKED / NotRun. No oneuse-03 Unity/Player execution has occurred.

**Primary implementation source correction:** a separate native preopened `raw.json.native-trace.jsonl` records bounded Open/Configure/Stage/Commit/callback/field-read/Seal primitive phases and failures, even when the strict V1 report fails. Failed Players remain Failed and `NotRun_CommandFailed`; diagnostic traces never prove V1/V2 acceptance. The ten-host raw tree, including all four adversarial symlinks, is retained in an unused sibling output root. Every actual regular byte and literal symlink target is recorded in a separate authenticated, symlink-free custody archive included in the unchanged strict product seal. The original S/K and production VM sources are unchanged.

Read the [new conditional WEB_TO_LOCAL handoff](Handoff/WEB_TO_LOCAL.md), [oneuse-03 design](History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/DESIGN.md), [execution plan](History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/PLAN.md), and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/PRIMARY_SOURCE_REVIEW.md). Local oneuse-03 may execute **only after** both designated GitHub host workflows have macOS and Ubuntu completed/success jobs at the same final published demo SHA, plus fresh read-only Mac Git/Unity/SDK/original-S/custody admission and two fresh >=25.0GiB capacity samples for its unused output roots. No earlier CI/measurements substitute.

The independent October 8 R03 FAIL and High IR-R03-01/02 remain open. Captured-generic error15, complete native V2/first-failure/general diagnostics, original-S compiler/object/link/Player joins, whole-VM epoch, managed shutdown, GC/RSS, RC1–RC6, P1/P2/E0/E1/P3, full legacy regression and performance qualification are still unaccepted. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`. PureInterpreter disabled; no H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

---

# Current Primary state — oneuse-01 admission BLOCKED; oneuse-02 source correction ready (2026-11-05 UTC)

**Oneuse-01 is BLOCKED / 15 cells NotRun** at original executed demo
`bf1e8283061fe3a94c56ea2ac9ab6445905cf738`, Local publication
`fda6c84b8cf1af336c6eedb16343e7ddc0362831`. The mandatory
Mac read-only admission exited2 on a stale strict `PlayerFixtures.csproj`
blob, introduced by the legitimate new initializer fixture source.
**No Unity build, no Player, no Local runner or new batch root.**
The published [Local checkpoint](History/M07R/R03/local-validation-initializer-20261105-oneuse-01/README.md)
and old evidence remain immutable.

Primary corrected the **exact** fixture-project, initializer producer,
and generator-entry Git blob admission (without relaxing source checks).
The host regressions and current-native host workflows passed
on both macOS and Ubuntu at implementation source demo
`b24e51ec074c7b3f9c7f7d86584c873f38dc2387`.
The new conditional **oneuse-02**, at a fresh distinct root and final
pushed SHA, is described in the
[current WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md),
[admission recovery design/plan](History/M07R/R03/IR_Remediation/INITIALIZER02_ADMISSION_RECOVERY_2026-11-05/DESIGN_AND_PLAN.md)
and [Primary source review](History/M07R/R03/IR_Remediation/INITIALIZER02_ADMISSION_RECOVERY_2026-11-05/PRIMARY_SOURCE_REVIEW.md).

**Entry conditions:** both initializer and shared native host workflows
must have completed successful macOS+Ubuntu jobs at the same **final**
pushed demo SHA; a fresh read-only Mac/SDK/Git/original-S admission,
two new capacity measurements each >=25.0 GiB, prior evidence custody
and clean exact remote heads must also pass. Prior oneuse-01 capacity
measurements are not reusable. Even a passing source-level gate is not
a Unity/Player result or independent R03 acceptance.

The independent October 8 R03 FAIL and High IR-R03-01/02 remain open.
Captured-generic, complete native V2/first-failure diagnostics,
original-S full source-to-binary/Player provenance, managed shutdown,
GC/RSS, whole-VM and RC/P/E acceptance remain incomplete:
`R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`;
`runtimeAcceptance=false`; `qualificationApproved=false`;
PureInterpreter disabled. Do not start H2/M08A/X02/SNAP-01 or
self-approve the Human Review Gate.

---

# R03 Primary conditional initializer one-use handoff (2026-11-05 UTC)

**New, narrow Local authority is CONDITIONAL** for one previously unexecuted
initializer-only cycle after all current CI, exact Git HEAD, independent
macOS capacity, original-S preservation and SDK admissions pass. Read the
[current WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md), [new design](History/M07R/R03/IR_Remediation/PRIMARY_FOLLOWUP_2026-11-05/INITIALIZER_ONEUSE_DESIGN.md)
and [execution plan](History/M07R/R03/IR_Remediation/PRIMARY_FOLLOWUP_2026-11-05/INITIALIZER_ONEUSE_PLAN.md).
This authorizes only one new ON/Release native build and two separate
initializer-control/failure Players, plus ten local native host components
and archived original-S provenance/source/Mach-O audits. No new execution has
occurred at the time of publication. The older K `WEB_TO_LOCAL` CLOSED
state remains historically correct for **consumed K**; it is not reused.

Prior source-only initializer CI was successful, but real IL2CPP compilation,
postpublication callback, raw V1 observation and native Player process
identity have not yet been established. The new runner is V1, not complete
native V2/first-failure/general diagnostic or captured-generic error-15 proof.

The independent October 8 R03 FAIL, both open High IR-R03-01/02,
the missing whole-VM/managed shutdown/GC/RSS/RC obligations, and all
historical K/I/J classifications remain unchanged:
`R03Accepted=false`; `H2Passed=false`;
`ReadyForHumanReviewGate=false`; `runtimeAcceptance=false`;
`qualificationApproved=false`; PureInterpreter disabled.
No H2/M08A/X02/SNAP-01 or Human Review Gate automatically.

---

# R03 current Primary — initializer diagnostic source prepared (2026-11-05 UTC)

**No new Unity or Player execution.** The new isolated initializer-control/failure target generator, native prepared-field observer, separate preopened diagnostic writer, managed Player source and project-preparation/verifier contracts are published. Six focused workflows passed in their exact source scopes (dual-OS generator, observer, writer, project preparation, diagnostic schema; pinned managed API compile). [Implementation/evidence record](History/M07R/R03/IR_Remediation/PRIMARY_FOLLOWUP_2026-11-05/INITIALIZER_IMPLEMENTATION_PROGRESS.md).

**IR-R03-02 remains High / NeedsEvidence:** actual IL2CPP native build, full terminal V2 reporter and first-failure diagnostics, fresh Player observation, captured-generic producer and source-bound runtime witness are **NotRun/incomplete**. IR-R03-01 and RC closure remain open. Historical K is consumed; Handoff/WEB_TO_LOCAL.md remains **CLOSED**. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, PureInterpreter disabled.

---

# R03 Primary continuation — original S registration and Mach-O evidence (2026-11-05 UTC)

**Read-only archived evidence advance, not stage acceptance.** [Exact-source macOS run 41965330265](https://github.com/night-outlook/hybridclr_demo/actions/runs/41965330265) **Passed**: 14/14 host checks; authenticated both original S NativeOn/NativeOff GameAssembly.dylib Git/archive identities and found *defined* g_Il2CppGenericMethodPointers and g_Il2CppInvokerPointers symbols in both archived Mach-O binaries. Original source code-registration counts 48,232/10,198 agree with audited generated array rows. [Detailed non-authorizing report](History/M07R/R03/IR_Remediation/PRIMARY_FOLLOWUP_2026-11-05/ORIGINAL_S_BINARY_REGISTRATION_AUDIT.md).

**Still open:** original source-to-object/compiler/link receipt and executable-to-Player join, and the IR-R03-02 real captured-generic/initializer native Player witnesses. Both High IR-R03-01/02 remain NeedsEvidence. K remains consumed and Handoff/WEB_TO_LOCAL.md **CLOSED**. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; PureInterpreter disabled.

---

# R03 Primary source-only continuation — original S table audit and V2 host CI (2026-11-04)

**Latest Primary evidence, no Local handoff:** original-S generated source material read-only audit at demo `e32be835148715db838014c06a645d72b0772614` [Actions 41962491415](https://github.com/night-outlook/hybridclr_demo/actions/runs/41962491415) PASS: 15 host tests, exact original S git/index/file byte identities, 4 generated file occurrences, 48,232 generic method-pointer initializer rows and 10,198 invoker initializer rows in both NativeOn/NativeOff. **Source → compiled object → Player linkage and original capture omissions reconciliation remain NotProven/NotRun.** The remaining-witness V2 *synthetic* semantic verifier [Actions 41962796627](https://github.com/night-outlook/hybridclr_demo/actions/runs/41962796627) passed 8/8 host tests on both Ubuntu 24.04 and macOS 15, **not real Unity/Player**. [Exact run and artifact report](History/M07R/R03/IR_Remediation/PRIMARY_FOLLOWUP_2026-11-04/ORIGINAL_S_GENERATED_MATERIAL_AUDIT.md).

**Open independent High IR-R03-01/02 remain NeedsEvidence.** Captured-generic and module-initializer Player producers, real V2 native snapshot, independently bound original source/build/Player linkage, managed shutdown/GC/RSS/whole-VM and other RC obligations remain unaccepted. K was consumed; the active `Handoff/WEB_TO_LOCAL.md` remains **CLOSED**. `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01.

---

# Current R03 Primary state — K PASS reconciled; independent R03 FAIL remains (2026-11-04)

**Local one-use K completed PASS within focused scope** at executed demo c20da0b261172cbdd188378e24dbe9343a14c6b2 and published evidence demo 14f97f15af6c06afa65957a9b880ccf841069452. Primary verified nine exact-source Actions runs / 18 OS success jobs and inspected the actual K producer, ten host components, three Unity builds, five Players, 135 source-install pairs, original S custody and preservation receipts. This is not a new full-stage review. [Primary K reconciliation](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_K_RECONCILIATION_2026-11-04/PRIMARY_RECONCILIATION.md) and [prepared independent R03 review brief](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_K_RECONCILIATION_2026-11-04/INDEPENDENT_REREVIEW_BRIEF.md).

**Open High findings:** IR-R03-02 has current corrected native source and three real ON post-poison witness cases (pre-positive 42, attempted/denied active reflection/delegate/AOT, canary1→1/field2→2; OFF1→2), but captured-generic and initializer cases remain NotRun and independent closure has not occurred. IR-R03-01 has corrected canonical original S nine-part archive custody and 59 archived historical process joins; complete independent original source/build/Player/generated-code semantic authentication is still open. NativeAtexit/exit0 after 11 reports in103ms is a scoped C-runtime exit, **not** full managed Shutdown, coherent whole-VM epoch or GC/RSS acceptance.

**K is consumed; canonical WEB_TO_LOCAL is CLOSED.** No new Local run, independent review, H2, M08A, X02 or SNAP-01 is automatically authorized. The October 8 independent R03 FAIL remains; R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false and PureInterpreter disabled. The older conditional K instructions below are retained as historical context and superseded by this header and the CLOSED handoff.

---

# Current Primary K response — consumed J FAIL, concrete Path and genuine host CLI correction (2026-11-03 UTC)

**Latest Local J is consumed FAIL/ReturnRequired**, not a product/runtime regression: the first actual `run_current_native_host_preflight.py::inputs` gate rejected an otherwise canonical absolute macOS `PosixPath` because `type(workspace) is Path` is false for the pathlib factory's concrete class. Nine exact-source CI workflows/18 jobs, Mac/SDK/read-only capacity and seven source/archive stages Passed. **J executed 0 of 10 native host subcomponents; no Unity/IL2CPP builds or Players and no official 135 native VM pairs.** Original J coordinator exit1/failure raw and every prior A–J/H/I/G/E/F status remain unchanged; J may never be rerun.

**Primary K source fix:** accept a genuine `isinstance(workspace, Path)` while retaining strict absolute/directory/non-symlink/physical canonical and 4 clean Git HEAD/remote/source/SDK checks. The current-only host wrapper gains explicit `--read-only-admission`, which runs real input/output preflight and returns `PassedReadOnlyNativeHostInputs_NoComponentsOrUnity` with no output or runtime/host acceptance. New dual-OS CI uses four **actual independent clean checkout roots** and executes a fresh real foreign-cwd positive CLI admission, negative relative/symlink CLI calls and then a **complete real 8 historical + 2 current owner C++11 host CLI** (not merely mocked receipt assertions). At pre-doc source `de09b8c87b69eaa1cb91bb9ea5bc2ffb2340d2e0`, combined workflow `41629858510` macOS `125896367873` and Ubuntu `125896368772` both Passed, showing exact `PassedHostOnlyTenComponents` and ten genuine host receipts; this remains **host-only**, not fresh Local/Unity evidence. The CI native checkout contract now requires both literal exact pinned source refs in the combined workflow and one in each other native source workflow.

**Next Local K is conditional and single-use** at a distinct absent K root, only after **all nine** new final-demo-SHA `push` workflows and both macOS+Ubuntu jobs each success, four clean pinned repos/SDK/original-S and A–J preservation, two independent **fresh >=25.0GiB** K-parent capacity measurements under an explicit K-only exception (hard20GiB/advisory40GiB unchanged), and *both* Mac read-only environment admission and newly implemented host CLI read-only admission. After all pass, execute one new complete coordinator with 10 actual Local host components before 3 fresh Unity2022.3.62f2 C++11 builds/5 real Players/official135 source pairs. No earlier I Player substitutes, no J retry or history rewriting. [K Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/DESIGN.md), [K Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/PRIMARY_SOURCE_REVIEW.md), [canonical K handoff](Handoff/WEB_TO_LOCAL.md).

**Gate unchanged:** original Oct8 independent R03 FAIL/High IR-R03-01/02, P1/P2/E0/E1/P3, full Unity-managed Shutdown/GC/RSS and coherent whole-VM epoch are still unresolved. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate automatically.

---

# Current Primary J response — I FAIL consumed; complete batch record + native host roster repair (2026-11-03 UTC)

**Latest Local I is consumed/FAIL / ReturnRequired, not a runtime failure.** The original I coordinator `batch/RESULT.json` exited1 because its `verify_current_batch` compared the valid original complete `repositories` producer record (schemaVersion1/phase/candidate/branch/four SHA pins/runtimeAcceptance=false) against only four SHA keys. The original I *child* in `History/M07R/R03/local-validation-current-native-original-s-20261103-oneuse-i/` was `FocusedEvidenceReadyForPrimaryReview`, 18/18 genuine cells Passed, three real Unity IL2CPP C++11 builds Passed, five actual Players Passed, official135 installed source pairs Passed, engine11 reports/103ms with NativeAtexit/exit0, native wants/quit counts1 each. **No original I outer verdict or raw has been rewritten or promoted.** A second independent issue: Local I native-host diagnostics ran only eight historical tests, while two current C++11 native owner suites were **NotRun** locally (both independently Passed exact-source CI).

**Primary J solution:** `current_native_source_gate.py` now supplies one full typed repository-record contract shared by the coordinator and source-parity audit. `verify_current_batch` requires original schema/kind, 18 uniquely Passed cells, exact three/five typed build/Player counts, complete repository metadata, original-S fixture SHA and every false acceptance flag, rejecting duplicates/extra/missing/typed mismatches. An exact byte copy of I's already published `LOCAL_BATCH_RESULT.json` with Git blob `d7209e...` is used **only as a read-only source/host regression fixture**, not fresh J Unity evidence. New `run_current_native_host_preflight.py` preserves the historic eight-command helper byte-for-byte and adds two fresh Local current owner C++11 suites; the coordinator requires exactly ten native host components and valid receipts before any Unity operation. Shared source and host tests cover missing/failed/faked output, stale source heads and unwanted Player-result promotion. **No production/native changes** to `hybridclr`, `hybridclr_unity`, or `il2cpp_plus`.

**Next Local J is CONDITIONAL and single-use.** Require nine fresh GitHub `push` workflows with two completed successful macOS+Ubuntu jobs **at the same final pushed demo SHA**. Source/host CI is not a new Unity Player run. Before creating an unused J root, independently validate four clean exact canonical repo/branch/remote heads, original S/A–I raw+SDK preservation, installed Unity2022.3.62f2 arm64/SDK, no conflicting processes, a read-only Mac admission and two current capacity samples **both >=28.0GiB on the J output parent** under an explicit J-only advisory exception (hard20/advisory40 unchanged). Below28, no J coordinator/root/Unity. If all prerequisites pass, execute exactly one source-pinned J full ten-stage batch, preserve 8+2 Local owner host receipts before Unity, and independently verify three builds/five Players/135 native source pairs without changing I.

**Unchanged gate:** Independent Oct8 full-stage R03 FAIL/High IR-R03-01/02, P1/P2/E0/E1/P3, managed Shutdown/GC/RSS/whole-VM epoch obligations are unresolved. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate. [J Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_I_CONSUMER_HOST_2026-11-03/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_I_CONSUMER_HOST_2026-11-03/PLAN.md), [Primary review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_I_CONSUMER_HOST_2026-11-03/PRIMARY_SOURCE_REVIEW.md), [canonical J handoff](Handoff/WEB_TO_LOCAL.md).

---

# Current Primary I response — H FAIL, native-only Unity quit decision and independent build parity (2026-11-03 UTC)

**Latest Local H = FAIL / ReturnRequired and consumed.** At actual demo `3e838edf8995e40058f3bc6c42f071446a0be821` / native `cdd3f7bc671880052e4f55ae4c1cd75b99a603e1`, all three real Unity2022.3.62f2 arm64 C++11 builds and four of five focused Players Passed. The engine Player still recorded **55,656 real completed reports in 514ms**, compared with the unmodified **64 reports / 500ms** bound, and exited **71** via the failure-only watchdog, without normal `atexit`. The native owner `Application.Quit(0)` call returned, but real `UnityEngine.Application.Internal_ApplicationWantsToQuit` was subsequently denied by the post-terminal guard. H's official installed 135-pair audit remained Blocked although Local independently compared 135 equal bytes. H original failed raw/evidence, all older checkpoints and unchanged acceptance flags remain immutable; **never retry H**.

**Primary I implementation:** new test-only native handling for exactly two Unity2022.3 physical AOT lifecycle methods: `Internal_ApplicationWantsToQuit():bool` (respond with pre-pinned native `true`) and `Internal_ApplicationQuit():void` (return native void, without executing managed callbacks). Eligibility requires original exact-sentinel native owner request, captured first failure, state `FailedAfterCommit`, physical metadata and source-pinned test configuration; all other post-terminal entry remains denied. The original report counter and timing bounds are unchanged; V2 raw adds separate native lifecycle decision counts and exact log markers. Current source: `night-outlook/il2cpp_plus@41764ae1eeefb33b05966e7f7676e52aae39c340`. A separate correction allows the official installed native **135 physical source pairs** to be independently audited after three real successful Unity builds and sealed source evidence even if a Player fails, without upgrading Player or R03 outcome.

**I is a new conditional one-use Local cycle**, not H replay. Source host tests include C++11 full translation unit ON/OFF, actual extracted native owner-method classifier with adversarial method/assembly/owner-state negatives, strict original Player oracle and three-build source-parity rejection tests. The final **nine** required GitHub workflows must each pass macOS and Ubuntu on the **identical final pushed demo SHA**, without ancestor substitution, before any Local invocation. Actual Unity/Player remains NotRun for I until new read-only Mac/SDK/Git/preservation and I-only disk admission: fixed hard20GiB/advisory40GiB, explicit **I-only conditional >=32GiB** two-sample exception on actual parent volume; below32GiB NO-GO, no I root. A normal native process exit does not prove full Unity-managed shutdown, coherent whole-VM epoch, GC/RSS or full R03 acceptance. See [I Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/DESIGN.md), [I Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_H_ENGINE_OWNER_2026-11-03/PRIMARY_SOURCE_REVIEW.md), and [canonical conditional I handoff](Handoff/WEB_TO_LOCAL.md).

**Gate stays closed:** independent Oct8 full-stage R03 FAIL / High IR-R03-01/02; D1=A/D2=A and original P1/P2/E0/E1/P3 outstanding; `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled. Do not begin H2/M08A/X02/SNAP-01 or Human Review Gate.

---

# Primary H source/CI correction — first candidate CI FAIL (2026-11-03 UTC)

The prior pushed H source `953e8e5e4a7f5a4fd7ea0851726b2be1496c37b0` ran exact-source CI and was **NOT eligible for Local H**: the coordinator still expected ten source files, the K synthetic engine witness was V1 instead of V2, and three mandatory workflows still checked out the consumed G native revision. Primary has prepared corrections, including a new actual-workflow checkout-ref gate and source-pinned K fixture. See the latest [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) for the **final** pushed demo SHA and nine fresh two-OS successful workflow requirements. Earlier CI failures remain visible. All A–G Local evidence and R03 acceptance flags are unchanged. Do not execute H from the earlier SHA.

---

# Current Primary response — oneuse-G FAIL remediated in source; conditional oneuse-H (2026-11-03 UTC)

**Latest Local G is FAIL / ReturnRequired**, not acceptance: two ON actual Unity2022.3.62f2 C++11 builds and three ON post-poison complete sidecar Players Passed; OFF C++11 build failed on incomplete exception/string types; engine observer recorded 51,865 reports in500ms despite a single native owner quit request, exited71; OFF Player/official 135-pair audit Blocked. G is consumed and immutable. F remains BLOCKED and E remains FAIL.

**Primary H candidate:** native probe includes `il2cpp-object-internals.h` independently in feature-OFF and feature-gates its recovery/exit writer; Unity fixture triggers the authentic unhandled sentinel from a running `MonoBehaviour.Update` frame instead of `BeforeSceneLoad`; native V2 observer distinguishes normal `atexit` (durably logged) from failure-only `std::_Exit(71)` watchdog, preserving actual 64-report/500ms bounds and first failure. New source-only C++11 OFF/ON full-translation-unit mock tests, strict host oracle negatives and 11 candidate/45 native-VM source blob pins prepare **one** conditional H combined Local cycle. Normal process exit is not full Unity Shutdown or a coherent VM epoch. [Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_G_OFF_ENGINE_2026-11-03/PRIMARY_SOURCE_REVIEW.md), [canonical H handoff](Handoff/WEB_TO_LOCAL.md).

**Local H strict prerequisites:** nine actual macOS+Ubuntu CI workflows at identical *final* demo SHA, exact four remote/source pins, read-only Mac and unconsumed H root, original-S and all A–G evidence preservation. Hard20GiB/advisory40GiB unchanged; explicit **H-only** conditional admission needs two current >=36GiB samples on actual parent, else NO-GO. No automatic Player run before gates. CI source-host tests are not actual Unity acceptance. All Oct8 independent R03 FAIL/High IR-R03-01/02 and `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, PureInterpreter disabled remain. No H2/M08A/X02/SNAP-01/Human Review Gate.

---

# Current Primary response — oneuse-F CI BLOCKED; exact-source oneuse-G preparation (2026-11-02)

**Latest Local F remains BLOCKED / NotRun**, not a new product/runtime failure: at governing demo `9db3927a9cc899fbe73948e0ff9c586f96efde6d` only the combined host had both OS jobs PASS; eight required workflows had no matching exact-commit run. F coordinator0, Unity0, Players0; its root remained absent. E FAIL and all A–F prior checkpoints stay immutable.

**Primary CI remediation:** all nine mandatory workflows now include `Handoff/WEB_TO_LOCAL.md` in `push.paths`; a new `current_native_handoff_ci_contracts.py` independently checks all nine and six positive/negative trigger cases from the actual checked-out files. A final handoff-only change must trigger nine **fresh runs at identical final demo SHA**; their actual two-OS success must still be verified before any Local execution. Ancestor/source-equivalent CI is not silently accepted. See [Design](Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_F_CI_CAPACITY_2026-11-02/DESIGN.md), [Plan](Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_F_CI_CAPACITY_2026-11-02/PLAN.md), [Primary review and capacity decision](Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_F_CI_CAPACITY_2026-11-02/PRIMARY_REVIEW.md), and [new G handoff](Handoff/WEB_TO_LOCAL.md).

**Primary one-use capacity decision:** F's previously measured 39.5234375 GiB was below advisory40 but above hard20. A narrow **conditional GO** for G is granted only with a new source-pinned read-only Mac admission **and second immediate pre-coordinator sample both at least 39.0 GiB** on the actual output parent, all source/CI checks green. Below39.0 = NO-GO, no root creation; hard20/advisory40 unchanged. E's prior ~2.966-GiB disk reduction is only historical capacity evidence, not guaranteed G usage. No cleanup or APFS volume workaround.

No Unity or Player validation is implied by this CI repair. The independent R03 FAIL/High IR-R03-01/02 remains open; R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false; PureInterpreter disabled. No H2/M08A/X02/SNAP-01/Human Review Gate.

---

# Current R03 Primary response — oneuse-E FAIL, F conditional source/host handoff (2026-11-02)

**Actual oneuse-E is consumed/FAIL:** three native Unity2022.3 C++11 builds Passed; OFF Player Passed; three ON Players failed their original bounded field14 snapshot (empty raw, exit2), and one genuine engine observer recorded **51211** terminal reports in500ms (bound64, exit71). The official installed parity stage remains Blocked, despite independent scoped 129 source-to-installed byte comparisons. No prior A–E result changed.

Current Primary candidate: exact full general diagnostic bytes carried by a source-pinned preopened bounded sidecar, host-side complete strict JSON/CRC/schema verification, one-shot native owner-quit request for the genuine engine sentinel, and strict host-negative and legacy source/runner contracts. The new `il2cpp_plus@2c899ece8cf241887b14040bab0a73d7c854d2bf` manifest has **45 changed VM files** requiring **135 installed source-role pairs** in a future Local cycle. See [Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_E_RUNTIME_REPAIR_2026-11-02/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_E_RUNTIME_REPAIR_2026-11-02/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_E_RUNTIME_REPAIR_2026-11-02/PRIMARY_SOURCE_REVIEW.md), and [conditional oneuse-F WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). All required current-source CI and read-only Mac preflight must pass before F root creation. Neither mock host proofs nor diagnostic byte completeness imply a coherent all-VM epoch, actual Unity quit, Player acceptance or independent re-review.

**Gate remains closed:** Original independent R03 FAIL/High IR-R03-01/02, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false; PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate.

---

# Current Primary repair — oneuse-D local FAIL and conditional oneuse-E (2026-10-30)

**Current Local result is FAIL, not runtime acceptance.** In oneuse-D, three actual Unity2022.3.62f2 IL2CPP builds (ON Release/Debug, OFF Release) failed on C++11 compilation before any current Player launched; combined coordinator 8 scoped Passed / 1 Failed / 1 Blocked, child 10 Passed / 3 Failed / 5 Blocked. The original-S archive and process audits remained historical/source-scope Passed. Absent-app enumeration obscured the original C++ compiler errors, and a newly generated CI comparison JSON had a trailing literal backslash-n. The consumed D source and evidence were not modified.

**Primary correction**: C++11-compatible native source in `il2cpp_plus` (now `ca0aab8e0abcbcb60a1532223d9e1bdb0aea86c4`); native three-compiler/macOS/Ubuntu C++11/C++17 source-host workflow [41043686073](https://github.com/night-outlook/il2cpp_plus/actions/runs/41043686073) **PASS**, but NOT real Unity. The subsequent native ca0 commit changes two host test scripts only; production VM source bytes remain identical to the 6510 tested version. Demo now records genuine BuildReport failure before any absent-app inventory, and emits/strictly reparses valid CI comparison JSON. The new source delta covers **43** changed native VM files, including previously omitted `AssemblyShadowDiagnosticWriter.h`, and requires **129** installed source-role pairs (3 x 43) rather than D's old 126. See [Design](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_D_CXX11_REPAIR_2026-10-30/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_D_CXX11_REPAIR_2026-10-30/PLAN.md), [Primary review](History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_D_CXX11_REPAIR_2026-10-30/PRIMARY_SOURCE_REVIEW.md) and [active conditional oneuse-E WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). Local oneuse-E must not run until the exact final demo source has passing host/source/fixture CI and read-only Mac admission. Its root must be fresh/unused; D and prior A/B/C remain immutable.

**Gate remains closed:** original independent R03 FAIL/High IR-R03-01/02, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false; PureInterpreter disabled. No automatic new milestone or Human Review Gate.

---

# Current R03 Primary preparation — pinned pre-Local generator proof (2026-10-29)

Before consuming the active oneuse-D Local root, verify **new real .NET 8.0 generator CI on both macOS and Ubuntu at the final demo commit**. The existing `r03-ir-fixture.yml` now runs on current-native integration/handoff changes, uses sparse exact source and pinned SDK 8.0.318, enforces the independent IR `Methods.dll` SHA/MVID, generates it in two fresh directories and rejects reuse, and runs 16 adversarial receipt checks. The read-only Local capacity advisory now matches **40 GiB**, with the fixed **20 GiB hard minimum** unchanged. See [Design](History/M07R/R03/IR_Remediation/IR_R03_PRELOCAL_GENERATOR_2026-10-29/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_PRELOCAL_GENERATOR_2026-10-29/PLAN.md), [Primary review](History/M07R/R03/IR_Remediation/IR_R03_PRELOCAL_GENERATOR_2026-10-29/PRIMARY_REVIEW.md) and [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md).

These tests are *host-only* and do not prove actual Unity/IL2CPP, 3 current native builds, 5 Players or 126 installed source pairs. Original oneuse-C FAIL and oneuse-D conditional authority are unchanged. Both CI OS jobs and source/remote pins must be checked at the final handoff commit before Local execution. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false; PureInterpreter disabled.

---

# Current R03 Primary response — oneuse-C CLI import failure repaired; oneuse-D conditional handoff (2026-10-26)

**Authoritative latest Local oneuse-C = FAIL / ReturnRequired, NOT Player failure.** A single original-S fc55 sparse projection and fresh admission passed, 16,978 protected original-S files preserved; measured available space increased from 19.844 to 46.334 GiB. The coordinator ran ONCE, with **eight scoped Passes** (104 source/host tests, original S authentic nine-part archive/90-cell and 59 original archived process joins, native host diagnostics), **one Failed** current-native-players CLI startup at run_terminal_current.py:14 due to missing sibling run_local module, and **one Blocked** native installed-source audit. Actual current native 3 builds, 5 Unity2022.3 Players and 126 physical native source pairs remain NotRun. oneuse-C coordinator/sparse roots are now permanently consumed. Original oneuse-A/B capacity BLOCKED remain immutable.

**Primary correction:** The standalone wrapper now bootstraps the exact adjacent owning R03 Python infrastructure *before* its first import. No PYTHONPATH workaround, historical native source pin mutation or product C++/Player fixture change. Read-only current_native_environment_admission now launches the real corrected CLI in a fresh Python process from an external cwd, **without PYTHONPATH/PYTHONHOME**, and rejects any import failure before the next one-use output root. [Design](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CLI_BOOTSTRAP_2026-10-26/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CLI_BOOTSTRAP_2026-10-26/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CLI_BOOTSTRAP_2026-10-26/PRIMARY_SOURCE_REVIEW.md), [source-only evidence](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CLI_BOOTSTRAP_2026-10-26/EVIDENCE.json), [new oneuse-D WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md).

Mac/Linux CI [40459012594](https://github.com/night-outlook/hybridclr_demo/actions/runs/40459012594) completed **205 source/host tests per OS PASS**, including 23 genuine fresh-interpreter startup/negative cases and new fail-closed readmission checks. This is NOT actual Unity/IL2CPP compilation or Player/terminal safety evidence. Related independent-review **host contracts** [40460340694](https://github.com/night-outlook/hybridclr_demo/actions/runs/40460340694) passed **156/156 on both macos-14 and Ubuntu** after correcting the CI-only sparse checkout scope; previous macOS checkout disk-exhaustion and missing R03Storage input failures remain retained. These are not an independent R03 full-stage reviewer verdict. New Local oneuse-D must preserve the ALREADY SPARSE clean original-S fc55 (do not re-sparsify), verify latest full four Git remote heads and genuine SDK8.0.318/runtime8.0.21 + Unity2022.3 arm64, pass fresh actual standalone CLI/read-only capacity admission (hard >=20 GiB, >=40 GiB advisory), then run the unchanged combined 10-stage coordinator once in a NEW unused root.

Oct 8 independent full-stage R03 **FAIL** with High IR-R03-01/02 remains; D1=A NativeLayoutAdmissionV1 conservative/X02 deferred, D2=A performance observational, previous contaminated Failed certificates, original S bounded90/90, b7e3/c42a overall Local FAIL and f51d historical-audit-only PASS all retained. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false; PureInterpreter disabled. No H2/M08A/X02/SNAP-01/Human Review Gate automatically.

---

## Earlier source/status records — historical, NOT current Local execution authority

# Current Primary response — oneuse-B capacity BLOCKED; bounded fc55 projection and conditional oneuse-C (2026-10-26)

**Newest Local oneuse-B remains BLOCKED before coordinator, and original oneuse-A remains BLOCKED.** All ten empirical R03 stages are NotRun, with zero Unity/IL2CPP builds, zero Players and no original-S archive/process reauthentication. oneuse-B output space was 19.858/19.840 GiB, below the unchanged 20-GiB minimum. A proposed /Volumes/Data was in the same APFS disk3 container, not a separate capacity pool. The originally retained clean fc55 worktree remains at its exact path; it was not recreated. Existing trusted .NET SDK8.0.318/runtime8.0.21 osx-arm64 was discovered and enabled via process-scoped PATH, without installation or build.

**Primary remediation:** GitHub directly verified that the exact original-S checkpoint subtree at fc55 contains **16,978 regular files / 3,882,340,952 logical bytes**, Git tree 2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79. New [bounded sparse projection source](../../Tools/AssemblyShadow/R03IR/original_s_sparse_projection.py) is designed to retain original Git history, original worktree registration and *all* checkpoint bytes while de-materializing unrelated clean tracked files from that auxiliary worktree. This is an explicit controlled working-tree change, not guaranteed physical APFS reclamation; no actual Mac sparse conversion has occurred. It never deletes original Git objects, changes product source pins, prunes worktrees or loosens the 20 GiB floor.

[Design](History/M07R/R03/IR_Remediation/IR_R03_ORIGINAL_S_SPARSE_CAPACITY_2026-10-26/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_ORIGINAL_S_SPARSE_CAPACITY_2026-10-26/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_ORIGINAL_S_SPARSE_CAPACITY_2026-10-26/PRIMARY_SOURCE_AUDIT.md), [source-only evidence](History/M07R/R03/IR_Remediation/IR_R03_ORIGINAL_S_SPARSE_CAPACITY_2026-10-26/EVIDENCE.json), [ACTIVE conditional oneuse-C WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). Mac/Linux current source CI validated **180 host-only tests per platform**, including 31 new tiny-Git sparse-custody tests; neither original-S actual worktree, Unity, archive audit nor Player was run. New oneuse-C capacity remediation has one bounded sparse command and must pass full checkpoint postflight and fresh storage/toolchain admission before any single unchanged 10-stage coordinator invocation. 20 GiB hard minimum preserved; 40 GiB advisory buffer, not proven build budget.

Original October 8 independent full-stage R03 verdict remains FAIL, High IR-R03-01/02 independently open; D1=A conservative NativeLayoutAdmissionV1 / X02 deferred, D2=A observational-only performance, contaminated Failed certificates, original S historical bounded 90/90, b7e3/c42a overall Local FAIL and f51d historical audit-only PASS untouched. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, qualificationApproved=false, PureInterpreter disabled. No H2/M08A/X02/protected SNAP-01/Human Review Gate.

---

## Earlier status records — history only, not active authorization

# Current R03 Primary response — retained original-S fc55 and oneuse-B readmission (2026-10-26)

**Previous oneuse-A was BLOCKED before the coordinator was invoked.** The latest Local checkpoint at [oneuse-A capacity BLOCKED](History/M07R/R03/local-validation-current-native-original-s-20261026-oneuse-a/README.md) confirms 19.63 GiB immediately after fc55 worktree creation versus a fixed 20 GiB admission minimum, later 20.29 GiB passive sample, ten coordinator stages NotRun and 0 Unity/Player/SDK invocations. The clean original S fc55 worktree is retained, but prior oneuse-A authority/root is consumed. Actual dotnet was absent on PATH; the net8.0 fixture runtime is not admitted. The Oct 8 independent R03 **FAIL** and High IR-R03-01/02 remain open.

**New Primary disposition:** Preserve oneuse-A and original S history; authorize **read-only reuse** of the retained clean fc55 after new exact Git registration/source admission. No additional original worktree materialization, deletion, cache pruning, threshold weakening or oneuse-A retry. Prefer a new oneuse-B output root on a verified larger volume with >=30 GiB *advisory* headroom; hard coordinator minimum stays 20 GiB. New read-only [environment admission script](../../Tools/AssemblyShadow/R03IR/current_native_environment_admission.py) requires actual PATH-visible net8-capable dotnet SDK + Microsoft.NETCore.App 8.x runtime as well as the existing Unity and source checks.

[Design](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CAPACITY_READMISSION_2026-10-26/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CAPACITY_READMISSION_2026-10-26/PLAN.md), [Primary reconciliation](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CAPACITY_READMISSION_2026-10-26/PRIMARY_RECONCILIATION.md), [source/CI evidence](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_CAPACITY_READMISSION_2026-10-26/EVIDENCE.json), [new canonical one-use-B WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). GitHub CI [40438909487](https://github.com/night-outlook/hybridclr_demo/actions/runs/40438909487) **PASSED 149 source/host-only tests each on Mac/Linux** including 25 new no-write storage/fc55/net8 admissions. CI did not run the Mac Local environment, Unity or original S archive. All ten original R03 empirical stages still NotRun. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled; no H2/M08A/X02/SNAP-01.

---

## Earlier status records — historical only; not active authorization

# Current Primary handoff — one-use R03 current-native and original-S Local validation (2026-10-26)

**ACTIVE ONCE only under canonical pushed WEB_TO_LOCAL.md and exact final demo remote SHA.** Primary has prepared additive one-use R03 source/host orchestration, physical 42 changed-VM-file × 3 installed-build-role parity checks, and 35 new adversarial coordinator/installed-source tests. See [Design](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/PLAN.md), [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/PRIMARY_SOURCE_REVIEW.md), [machine source/CI evidence](History/M07R/R03/IR_Remediation/IR_R03_CURRENT_NATIVE_LOCAL_CYCLE_2026-10-26/EVIDENCE.json) and the [canonical active WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md).

[GitHub Actions 40317130046](https://github.com/night-outlook/hybridclr_demo/actions/runs/40317130046) passed Mac/Linux with **124 source/host-only tests per platform** (20 coordinator, 15 VM-install synthetic, 20 source, 27 verifier synthetic, 12 VM delta, 30 original S audit host). This does NOT reconstruct original S full archive, compile installed Unity SDK, or run a real Player. The original first Mac fixture FAIL is retained, corrected and verified. No historical product FAIL was promoted.

**Next Local scope:** one fresh original-S nine-part archival/provenance/59-process crosswalk, current-native e1e5 three build roles/five real macOS arm64 Unity Player cases, and physical 126 source-installed byte comparisons; these remain NotRun. October 8 independent full-stage R03 **FAIL** and High IR-R03-01/02 remain unclosed. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, PureInterpreter disabled. No H2/M08A/X02/protected SNAP-01.

---

# HybridCLR Assembly Shadow

## Latest Primary Implementation — current-native R03 source review and independent-gate preparation (2026-10-26)

**Current independent full-stage R03 verdict remains FAIL.** The independent review performed on October 8 recorded High **IR-R03-02** (method entry after terminal transaction failure) and **IR-R03-01** (original S archive identity contradiction). An additive original-S provenance correction authenticates the proper nine-part original archive within byte/index/90-cell scope but is **not a separate full semantic independent review**. The current-native terminal guard source appears corrected, but actual matching Unity 2022.3 Player execution at native `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` is still **NotRun**.

**New Primary source-only evidence (not Player acceptance):** [Mac/Linux CI 40264569824](https://github.com/night-outlook/hybridclr_demo/actions/runs/40264569824) passed the existing **20/20 current-native source/pin tests** per host. [CI 40285861973](https://github.com/night-outlook/hybridclr_demo/actions/runs/40285861973) passed **27/27 actual Player-verifier host oracle tests** per host against synthetic positive and deliberately forged post-poison receipts. [CI 40287146227](https://github.com/night-outlook/hybridclr_demo/actions/runs/40287146227) passed **12/12 full changed native VM source-identity tests** per host, pinning all **42** changed `libil2cpp/vm` files among the native candidate's **147 commits / 125 changed paths** since the old R03 runner native pin. This is source identity, not proof of source inclusion, generated C++, linked Player binaries or runtime outcomes. No previous production code or original Player fixture was edited.

**Next authoritative Primary review package:** [R03 RC1–RC6 closure matrix](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/R03_RC1_RC6_CLOSURE_MATRIX_2026-10-26.md), [source-bound machine evidence](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/R03_RC1_RC6_CLOSURE_EVIDENCE_2026-10-26.json), [IR-R03-02 oracle source review](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/ORACLE_SOURCE_AUDIT_2026-10-26.md), [42-file native VM delta audit](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/NATIVE_42_FILE_SOURCE_DELTA_AUDIT_2026-10-26.md), and [unexecuted independent re-review request addendum](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/INDEPENDENT_REREVIEW_DELTA_2026-10-26.md). Owner **D1=A** retains conservative `NativeLayoutAdmissionV1` and defers structural expansion to X02; **D2=A** regards performance measurements as observational only, preserving four contaminated Failed certificates and deferred R02 CPU/H1 RSS risk.

**Separate historical audit:** `f51d` PASS remains **`PassedHistoricalAuditOnly_UnchangedLocalFail`**; original `b7e3` and `c42a` overall Local FAILs remain unchanged. `S` original 90/90 is historical Local evidence, not an R03 acceptance. **[WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) is CLOSED** and no new Local run is allocated. R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false; PureInterpreter disabled. P1 incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. No H2/M08A/X02/protected SNAP-01.

---

## Earlier status records — retained, not current approval
## Current R03 Primary state — current-native terminal source candidate prepared, Player evidence still NotRun (2026-10-25)

**The independent R03 full-stage review dated 2026-10-08 remains FAIL**, with two high findings: `IR-R03-02` (terminal failure must prevent a later otherwise-valid business method entry) and `IR-R03-01` (incorrect original S archive identity and independent source/build/process authentication). The original S execution remains 90/90 within its tested scope; owner **D1=A** retains conservative NativeLayoutAdmissionV1, deferring extra PureInterpreter layouts to X02; **D2=A** keeps development performance measurements observational-only. No H2 or next milestone is initiated.

**Latest Primary work:** the existing R03 focused Player runner still bound native `il2cpp_plus@74dbdbea80d83923863303bd2b2c0a87f36541b1` while current terminal runtime sources are at `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` (147 commits ahead). Primary published a **parallel coherent candidate**: [source manifest](../../Tools/AssemblyShadow/R03IR/current_native_candidate.json), [ten-blob gate](../../Tools/AssemblyShadow/R03IR/current_native_source_gate.py), [isolated current-native runner](../../Tools/AssemblyShadow/R03IR/run_terminal_current.py), and [20 adversarial host-only checks](../../Tools/AssemblyShadow/R03IR/current_native_source_contracts.py). Historical `R03/source-pins.json`, original `run_terminal_local.py`, original S/Player evidence and actual native implementation are **unchanged**. The new wrapper validates actual source identity *before* any new batch root and inherits all existing real repo/clean/remote/build-source checks.

**Source-only CI:** [GitHub Actions 40264569824](https://github.com/night-outlook/hybridclr_demo/actions/runs/40264569824) **PASS** on macos-15 and ubuntu-24.04 (**20/20 tests per platform**, all ten source blobs). Original broad R03 test discovery briefly failed on the candidate's initial `test_` filename; Primary renamed it to `current_native_source_contracts.py` and deleted the auto-discovered version rather than changing existing test rosters or creating skips. Historic R03 K source, K terminal and L source-contract workflows were successfully rerun. This code/CI establishes source-only candidate coherency, **NOT** real Player execution or a full audit of all 147 native commits. Read [new Design](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/PLAN.md), [Primary Source Review](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/PRIMARY_SOURCE_AUDIT.md) and [machine evidence](History/M07R/R03/IR_Remediation/IR_R03_02_CURRENT_NATIVE_COHERENCE_2026-10-25/EVIDENCE.json).

**f51d remains a COMPLETED historical audit-only PASS** within `PassedHistoricalAuditOnly_UnchangedLocalFail` scope. Original `b7e3` and `c42a` overall Local FAIL remain unchanged, with b7e3's original raw 25/25 scope PASS separately preserved. The f51d record is read-only historical evidence, **not** freshly compiled current-source Player proof. The original R03 independent FAIL also has not been replaced by a separate PASS. IR-R03-01 original-S semantic/provenance re-review and IR-R03-02 source-matched real Player proof are both OPEN.

**Next gate is NOT active:** [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) remains **CLOSED / no Local execution authority**. Do not run the new current-native runner, Unity/IL2CPP compiler/Player, re-execute original S/b7e3/c42a/f51d roots, advance H2/M08A/X02 or initiate Human Review Gate based on green source-only CI. A future fresh Real Local scope requires explicit Primary/human authorization, a new one-use source-pinned handoff and independent review of the complete Player input/install/build boundary.

**Project acceptance unchanged:** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. Original protected SNAP-01 and performance/CPU/RSS risks remain open.

---

## Earlier dated status records — history only, not current handoff

## Current R03 Primary stage — independent FAIL findings IR-R03-01/02 source pre-review (2026-10-24)

**The already completed `f51d` historical audit-only PASS remains valid solely within historical source/host/official SDK syntax receipt scope.** The earlier independent full R03 review dated 2026-10-08 has an immutable **FAIL** verdict for two High findings: `IR-R03-02` terminal method-entry safety after caught poison, and `IR-R03-01` incompatible original S archive identities. No independent *re-review* or H2 Human Review Gate has been initiated. The accepted owner D1=A conservative NativeLayoutAdmissionV1/X02 deferral and D2=A observational-only performance limit remain binding.

**New completed Primary work:** source/CI preflight for the two findings at [IR_R03_REREVIEW_PREP_2026-10-24](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/DESIGN.md). Current native `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` has early **and** success-path terminal guards; Runtime/HybridCLR interpreter common entry source guards are present. The focused Player fixture has a pre/post-poison side-effect witness in source, but demo R03 `source-pins.json` points to older native `74dbdbea80d83923863303bd2b2c0a87f36541b1`; current-source Player validation remains **NotRun/BlockedStaleRunnerNativePin**. Independently compiled full Unity/IL2CPP SDK/Player evidence is NOT supplied by this source-only preflight.

**Original S provenance:** immutable nine-part source archive SHA `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6` is bound by original transport/seal and additive byte/90-cell audit. The earlier contradictory five-part Primary archive `f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7` was expressly withdrawn as original S authority, not deleted or relabeled. IR-R03-01 still **PartiallyRemediatedAwaitingIndependentRereview**; complete source/build/process semantic reauthentication and separate full-stage reviewer decision remain pending.

**Verified source-only CI:** [run 40086902503](https://github.com/night-outlook/hybridclr_demo/actions/runs/40086902503) Passed both macos-15 and ubuntu-24.04, each **20/20 adversarial Python source tests and 69/69 compiled native terminal-policy header checks**. Its explicit result is `PassedSourceOnlyPreflight_PendingRealPlayerAndIndependentReview`, never product approval. Original CI attempts 40086592790 and 40086808626 remain honest test-tool FAILs, followed by Primary corrections. No product source files, original Local outputs or historical evidence were changed in this work.

Read [Primary source review](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/PRIMARY_REVIEW.md), [Design](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/PLAN.md), [machine evidence](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/EVIDENCE.json) and the [uninvoked independent re-review request](History/M07R/R03/IR_Remediation/IR_R03_REREVIEW_PREP_2026-10-24/INDEPENDENT_REREVIEW_REQUEST.md). Current [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md) stays **CLOSED / NO ACTIVE LOCAL RUN**. Do not begin runtime/SDK compiler tests, H2/M08A/X02 or any other milestone on this evidence.

**Unchanged gates:** P1 Incomplete (canonical TypeKeys, physical pointer provenance/lifetime, coherent epoch, full V1 and true Player/GC/RSS/Shutdown), P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. Original b7e3 and c42a Local FAIL remain, f51d historical-only PASS retained; older S 90/90 scope result unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled.

---

## Older history and bounded evidence records — not current execution authorization
## Latest Primary disposition — f51d historical evidence audit completed, runtime gates still OPEN (2026-10-24)

**Authoritative latest Local Validation: `20261024-f51d` PASS only in `PassedHistoricalAuditOnly_UnchangedLocalFail` scope.** The new, isolated historical auditor ran **once**, exited **0**, produced `stage/EVIDENCE_AUDIT.json` with `PassedHistoricalEvidenceAuditOnly`, and completed its previously unreached admitted-execution and captured historical Git-authority checks. Original 51/51 source-only prerequisites, historical 25 component receipts, original 85 test identities, eight inventories, admitted nine strict+nine sanitized cases, five original managed positives + exact expected negative, 100 original native SDK syntax receipts, 515 command streams and original Git20 are confirmed within that *read-only historical-evidence* scope. Supplied and independent original data-preservation reports both Passed. **This is NOT a new Player/Unity/runtime execution.**

**Do not promote or rewrite earlier results.** The original `b7e3` raw batch remains `PassedSourceHostAndSDKOnly` 25/25 **but its original overall Local result remains FAIL** due to its own auditor failure at line190. The later isolated `c42a` audit remains **FAIL** at line1031; `f51d` is a new, separately qualified success, not a replay or retroactive fix to those historical execution records. The `7896`/`7c2c` source-host scope PASS, `82dd` raw FAIL and `e1e5`/`6c72` prerequisite Blocked also remain intact.

**Source and custody authority:** f51d audited source `hybridclr_demo@ea530e59eef38175738e517110c698ebd31bb07f`, published factual Local checkpoint under `hybridclr_demo@ac32d96939147f0309ddd8679e2d0fe8c9986592`; other source repository commits unchanged. The Local after-check reports preservation of original **4269 raw**, **2405 installed SDK**, **1925 SDK scratch**, **104 preflight**, prior **2506 b7e3 checkpoint** and **197 c42a checkpoint** entries plus older historical sets. Primary independently examined source/actual receipts and recomputed **7/7** key f51d published file SHA-256 hashes against its 206-entry manifest; Primary has **not** directly rehashed all external original SDK/raw files.

**Primary reconciliation is complete within the historical evidence-only scope.** Read [current LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md), the [f51d evidence checkpoint](History/M07R/R03/local-audit-only-p1-20261024-f51d/README.md), [Primary reconciliation report](History/M07R/R03/IR_Remediation/P1_F51D_HISTORICAL_AUDIT_RECONCILIATION_2026-10-24/PRIMARY_RECONCILIATION.md) and [machine evidence](History/M07R/R03/IR_Remediation/P1_F51D_HISTORICAL_AUDIT_RECONCILIATION_2026-10-24/EVIDENCE.json). The old one-shot handoff is preserved [for history only](History/M07R/R03/IR_Remediation/P1_F51D_HISTORICAL_AUDIT_RECONCILIATION_2026-10-24/CONSUMED_WEB_TO_LOCAL_F51D.md). **[WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) is now CLOSED / NO ACTIVE LOCAL EXECUTION AUTHORITY.** Do not rerun `f51d` or start another audit, core/SDK compiler/Player cycle without a new explicitly authorized plan.

**Remaining:** P1 Incomplete (canonical TypeKeys, physical `Il2CppClass*` origin/lifetime, coherent VM epoch, original full execution V1/metadata safety, genuine Player/runtime initialization/shutdown, GC/RSS), P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter remains **disabled**. No H2/X02/M08A/protected SNAP-01 or Human Review Gate begins on this evidence alone.

---

## Historical source, audit, and handoff states — not current execution instructions
## Latest P1 Primary state — c42a historical-audit helper identity correction (2026-10-24)

**Authoritative latest Local: `20261023-c42a` isolated historical audit-only overall FAIL**, distinct from the original `b7e3` **overall Local FAIL / raw `PassedSourceHostAndSDKOnly` 25/25**. Its 23/23 host prerequisite and independent original evidence admission/preservation Passed; the one-shot historical auditor exited1 with `StopIteration` at line1031. The original checked-in `test_p1_command_failures.py` defines and calls `verify_admitted_execution_receipt_and_negative_mutations` (lines504/892), while the auditor looked up and asserted the obsolete `verify_admitted_execution_receipt_and_fail_closed_mutations` name (lines1031/1032). All subsequent full auditor checks and `EVIDENCE_AUDIT.json` remained NotRun/Unavailable. Read latest [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) FIRST, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md) and [c42a finding](History/M07R/R03/local-audit-only-p1-20261023-c42a/FINDING.json). Both the c42a and b7e3 roots are consumed.

**Primary source correction published:** new [audit_historical_helper_successor.py](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/audit_historical_helper_successor.py) is derived from the exact c42a auditor Git blob `c451e0cb7794e624eabb9029db0a35ba28d14592` with precisely TWO helper-name replacements on lines1031/1032, yielding blob `220aa2831458b37a81f66555f27d95349ec7013f`; every other source check remains unchanged. New source-bound [stager](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/stage_helper_successor.py) authenticates original `b7e3` raw4269, SDK2405, scratch1925, preflight104 and **the 197-file immutable c42a FAIL checkpoint**, then stages only a fresh isolated audit. New [runner](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/run_helper_audit_once.py) preserves the one-shot/no-retry process contract. The original production/native code, original85, consumed Local/checkpoint bytes and source pins are untouched.

**Source-only validation:** 17 new original-helper AST/identity/negative-mutation tests plus 11 new immutable-c42a source/custody tests, in addition to 23 retained one-shot/host tests and the published source/receipt SHA audit. The first CI run was a real host-only test fixture FAIL (quote-style mismatch, corrected without source-auditor changes). Final [Mac/Linux CI 40076790889](https://github.com/night-outlook/hybridclr_demo/actions/runs/40076790889) is **completed SUCCESS, 51/51 source-only tests per platform** (17 new helper identity, 11 c42a custody, 23 prior host contracts), plus complete 2,506-file published checkpoint SHA check with 1,873 original raw files unavailable in GitHub. Local still needs independent original evidence admission and the real new historical audit; no original product/SDK/compiler has been rerun. No full historical auditor, original SDK compiler, Unity Editor/Player or core25 has run in Primary.

See the new [Design](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/PLAN.md), [Primary Source Audit](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/PRIMARY_SOURCE_AUDIT.md), [Evidence](History/M07R/R03/IR_Remediation/P1_HISTORICAL_AUDIT_HELPER_2026-10-24/EVIDENCE.json) and final [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). Only the latter may authorize ONE new *historical audit-only* `20261024-f51d` Local cycle after all gates; NEVER rerun b7e3 core/compiler/SDK or consumed c42a audit.

**Unchanged acceptance:** P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, P3 Incomplete. Historical `7896`/`7c2c` scoped PASS, `82dd` raw FAIL, `e1e5`/`6c72` Blocked, b7e3 raw scoped PASS versus Local FAIL, and c42a historical audit-only FAIL remain distinct. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No H2/X02/M08A/SNAP-01/Human Review Gate.

---

## Earlier status records (historical; NOT current execution instructions)
## Current Primary state — b7e3 isolated audit-only continuation (2026-10-23)

**Latest factual Local Validation remains `20261023-b7e3` overall `FAIL`:** one raw source/host/official installed Unity2022.3.62f2 SDK syntax-only batch `PassedSourceHostAndSDKOnly` at 25/25, original85, admitted9+9, eight inventories, managed5 positives + exact negative, native100 and Git20, but its required **original independent auditor Failed at line190** and all subsequent assertions were **NotRun**. Do not reclassify the historical Local result, change consumed sources, or infer actual Player/runtime acceptance. Read Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) first and [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md).

**New narrowly scoped audit-only work:** user-requested continuation authorizes preparing ONE independent **historical evidence-only audit**, not rerunning Unity/SDK/core. Source-pinned `verify_published_checkpoint.py` and **23 host-only regression tests** completed [Mac+Linux GitHub CI 40072179278](https://github.com/night-outlook/hybridclr_demo/actions/runs/40072179278) **PASS on both hosts**: verified **2506 published checkpoint file hashes**, **2396 of 4269 raw-manifest files** available in GitHub, and the recorded **1925-file native SDK scratch manifest**; **1873 original raw files remain NOT published** and require original retained Local evidence to close. Two of the 23 tests launch only tiny test-owned Python audit stubs to prove the runner's one-shot/no-retry contract; neither invokes the historical Local audit or any Unity/SDK compiler. This is `PassedPublishedSnapshotScope_ExternalInputsUnavailable`, **not a full independent audit or Local PASS**.

An isolated `audit_historical_only.py` carries the full existing corrected auditor's checks and replaces only its obsolete **present-time** terminal Git-HEAD comparison with strict **captured b7e3 source-authority** checks from `GIT_BEFORE.json` and the already reverified 20 historical postflight receipts. It explicitly outputs a new historical-audit-only result, never a retroactive original Local PASS. `stage_local_audit_only.py` performs full original external raw (4269), installed official SDK (2405), **copied SDK scratch (1925)** and source hash admission before and after the isolated review; it rejects changed, duplicate or symlink-aliased scratch inputs, stages a separate audit copy and preserves all originals read-only; `run_local_audit_once.py` enforces one execution and records exact logs/PID/exit; the stager's after mode rehashes the originals. These scripts have **not** been run in the Local environment in the current Primary cycle.

Read the new [Design](History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/PLAN.md), [Primary source audit](History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/PRIMARY_SOURCE_AUDIT.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_B7E3_AUDIT_ONLY_2026-10-23/EVIDENCE.json), and the current [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). **Only** WEB_TO_LOCAL authorizes the new isolated `c42a` audit-only Local work after the source-only Mac/Linux CI and external evidence admission gates; it never authorizes Unity Editor/Player, SDK compilation, b7e3 core re-execution, or another project milestone.

**Protected outcome stays unchanged:** `b7e3` overall FAIL despite raw scoped PASS; earlier `7896` and `7c2c` scope PASS, `82dd` raw FAIL, `e1e5` and `6c72` prerequisite Blocked. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; P3 Incomplete, R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, fullLegacyRegressionAcceptance=false, PureInterpreter disabled. No H2/X02/M08A/protected SNAP-01/Human Review Gate.

---

## Earlier Primary states (historical, not current execution authority)

## Current authoritative Primary state — b7e3 raw PASS / required auditor FAIL (2026-10-23)

**Latest Local Validation is `20261023-b7e3`: overall `FAIL`, not accepted.** Its single raw source/host/actual Unity2022.3.62f2 installed SDK syntax-only batch is **`PassedSourceHostAndSDKOnly` with 25/25 passed**, original85 tests, eight inventories, admitted9+9, five real managed positives + exact original compiler-negative, 100 native C++17 `-fsyntax-only`, and 20 Git source checks. But the *unchanged required independent auditor* exited1 at line190: the strict 25-count assertion preceded an obsolete **24-name** ordered roster that omitted `admitted-execution`. All original auditor statements after line190 were **NotRun**. Read Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) FIRST, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md) and the [original finding](History/M07R/R03/local-validation-p1-admitted-execution-20261023-b7e3/FINDING.json). No historical result is relabeled.

**Primary correction published, without execution authorization:** a separately source-pinned full [audit_successor.py](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/audit_successor.py) changes **only source line190** (+21 bytes) to insert `admitted-execution` between `vm-shape-json` and `bounded-status`, keeping the exact identity/order requirement, original line189 count25 and all other checks intact. The old audited file, b7e3 RESULT/MANIFEST, failed audit log and Local findings remain untouched. Primary 20/20 direct Connector source/published-evidence checks passed. [Mac/Linux source-only CI](https://github.com/night-outlook/hybridclr_demo/actions/runs/39946839722) Passed 2/2, each running **16/16 roster tests plus 10/10 published-receipt checks**. This does **not** establish that the *full* independent auditor or any missing post-line190 checks passed.

Read [new Design](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/DESIGN.md), [one-cycle Plan](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/PLAN.md), [Independent Primary Evidence Review](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/PRIMARY_INDEPENDENT_EVIDENCE_REVIEW.md), and [machine evidence](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/EVIDENCE.json).

**NO FURTHER LOCAL RUN IS AUTHORIZED.** The canonical [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) is explicitly **CLOSED / NO EXECUTION**, superseding the consumed b7e3 handoff. The old b7e3 instruction is retained only as [immutable historical reference](History/M07R/R03/IR_Remediation/P1_AUDIT_ROSTER_2026-10-23/HISTORICAL_WEB_TO_LOCAL_B7E3.md). A new isolated **audit-only** re-review of the existing consumed evidence requires a **separate explicit human authorization**, with new source/receipt custody and safety constraints. Do not rerun b7e3 core/compiler/SDK/Unity, edit consumed roots, or begin a later milestone.

**Project remains:** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Historical 7896/7c2c scope PASS, 82dd raw FAIL, e1e5 and 6c72 prerequisite BLOCKED, original SNAP-01/N/M/K/I/E/R02 and independent full-stage review negatives remain. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter disabled. No H2/X02/M08A/Human Review Gate.

---

## Previous state records (archived; no operative Local execution instructions)

## Current Primary Implementation — P1 preparer canonical temporary fixture fix (2026-10-23)

**Latest authoritative Local Validation is 20261023-6c72: BLOCKED / PrerequisiteBlocked, 0/25 core components invoked.** Source/remote/SDK/historical and unused-root admission passed. The published Primary test prerequisite ran once: **13 tests; 12 Passed, one ERROR; exit 1** because the test-owned temporary directory inherited macOS `/var -> /private/var` aliasing and the test mistakenly passed its *noncanonical* path as an expected-good input. `pristine_root()` correctly rejected it. Local correctly stopped without invoking the preparer, original 85 tests or SDK compilers. Read the latest [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) **FIRST**, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md), and the frozen [6c72 FINDING](History/M07R/R03/local-validation-p1-admitted-execution-20261023-6c72/FINDING.json). Both `6c72` and earlier `e1e5` root identifiers are consumed, even where absent; do not resume/relabel either attempt.

**Primary fix:** `Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py` now canonicalizes *only the test-owned* temporary parent and adds inherited-alias and deterministic symlink-parent regression leaves. The original `prepare_p1_admitted_local.py` source, native runtime, original frozen source/historical results, local toolchain, and production path guards are unchanged. Exact published test blob `d8838bf0788d41a306f900f70d8052cb2d409803`; unchanged preparer blob `cf2fdf39fe17df076d50dcc33ed72c757eaa3b26`. **15/15 Passed** on Primary Linux Python 3.13.5 and **15/15 Passed** in an independently run, deterministic simulated `/var -> /private/var` temp alias. Actual native macOS 15-test suite and new official installed Unity SDK batch remain **NotRun**. See [new Design](History/M07R/R03/IR_Remediation/P1_PREPARER_TEMP_CANONICAL_2026-10-23/DESIGN.md), [one-cycle Plan](History/M07R/R03/IR_Remediation/P1_PREPARER_TEMP_CANONICAL_2026-10-23/PLAN.md), [Primary source audit and raw host results](History/M07R/R03/IR_Remediation/P1_PREPARER_TEMP_CANONICAL_2026-10-23/PRIMARY_SOURCE_AUDIT.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_PREPARER_TEMP_CANONICAL_2026-10-23/EVIDENCE.json), and updated [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md).

**Next authorized scope:** one fresh, independently admitted `20261023-b7e3` Local cycle: **15/15 prerequisite** and ONE source-pinned **25/25 source/host/official Unity2022.3.62f2 SDK syntax-only batch**, original 85 tests, eight inventories, nine admitted cases per strict/sanitized, five managed positives + original expected compiler-negative, 100 Apple arm64 native `-fsyntax-only` commands, twenty genuine Git postflight authority checks, independent audit and SDK/history preservation. Four new root names in WEB_TO_LOCAL require independent absent/canonical admission. No retry and no Unity Editor/Player/product link.

**Outstanding project gates unchanged:** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; P3 Incomplete. Historical `7896` and `7c2c` host/SDK-only PASS, `82dd` raw FAIL and both `e1e5` and `6c72` prerequisite BLOCKED remain distinct. Original SNAP-01/N/M/K/I/E/R02 and full-stage independent review failures remain. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`; PureInterpreter disabled. No protected SNAP-01, Human Review Gate or H2/X02/M08A.

---

## Earlier snapshots — historical, not current instructions

## Current Primary Implementation — P1 admitted-execution Local collector correction (2026-10-23)

**Latest authoritative Local Validation: 20261022-e1e5 is BLOCKED / PrerequisiteBlocked, core NotRun (0/25).** The independently written Local preflight helper omitted the exact newly admitted CPP/API literals in its *early opaque* frozen-source reconstruction. This is an evidence-collector prerequisite, not an observed production/native or official SDK failure. Read current [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) FIRST, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md), and the immutable [blocked finding](History/M07R/R03/local-validation-p1-admitted-execution-20261022-e1e5/FINDING.json). The old e1e5 preflight/checkpoint is consumed and MUST NOT be resumed or altered.

Primary has now committed a **source-authenticated deterministic corrected Local collector preparer**, with 13/13 local Python synthetic regression tests, dual native source-verifier and old 82dd exact CPP/API byte checks. The tool binds the entire blocked 42-file checkpoint manifest, repairs only two frozen-byte reconstruction expressions, and produces the unchanged previous independent audit.py on **one entirely new preflight root**. No native or demo product/runtime code changed, no prior test acceptance was promoted, and **new installed SDK / 25-component Local validation is NotRun**. See the [Design](History/M07R/R03/IR_Remediation/P1_LOCAL_PREFLIGHT_RECONSTRUCTION_2026-10-23/DESIGN.md), [Plan](History/M07R/R03/IR_Remediation/P1_LOCAL_PREFLIGHT_RECONSTRUCTION_2026-10-23/PLAN.md), [Primary audit](History/M07R/R03/IR_Remediation/P1_LOCAL_PREFLIGHT_RECONSTRUCTION_2026-10-23/PRIMARY_SOURCE_AUDIT.md), [Evidence](History/M07R/R03/IR_Remediation/P1_LOCAL_PREFLIGHT_RECONSTRUCTION_2026-10-23/EVIDENCE.json), and **final** [WEB_TO_LOCAL](Handoff/WEB_TO_LOCAL.md). Source and scripts under [Handoff/Tools](Handoff/Tools/prepare_p1_admitted_local.py).

One new independently admitted Local run may verify **25/25** source/host/actual installed official SDK syntax-only components, original 85 test IDs, eight source inventories, nine strict+sanitized new groups, five real managed positive compiler products + expected negative, 100 native C++17 syntax commands, twenty Git source-authority commands, before/after evidence/SDK/history. **No retries; no Unity Editor/Player/native product link.**

**Outstanding:** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete; historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled. Earlier 7896/7c2c PASS and 82dd raw FAIL are unchanged.

---

## Earlier status snapshots (historical; not current instructions)

## New Primary implementation — inactive metadata-admitted V1 getter (official installed SDK NotRun)

**Latest consumed Local:** [20261021-7896](History/M07R/R03/local-validation-p1-git-lifetime-20261021-7896/README.md) **PASS / PassedSourceHostAndSDKOnly**, executed demo `a5c0a4272efc4eee000220f40b7ca769be277917`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, unchanged other two. **24/24** components, original 85 tests, seven case inventories, five genuine managed positives + original exact expected-negative, **100/100** native official SDK syntax, **20/20** Git source-head checks, independently preserved SDK/source/history. The separate `7c2c` PASS and `82dd` raw aggregate **FAIL** remain unchanged. Read Local-owned [LOCAL_VALIDATION](Handoff/LOCAL_VALIDATION.md) FIRST, then [RETURN_TO_WEB](Handoff/RETURN_TO_WEB.md). No Unity Editor/TestRunner/Player/native product link, real GC/RSS/Shutdown.

**New exact source pins:** native `night-outlook/il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` adds an **INACTIVE** `AssemblyShadow::TryGetExecutionDiagnosticsWithMetadataAdmission`, with a default initial-source-epoch MetadataLifetime Reader around the **unchanged** original V1 diagnostic getter. It clears stale output and rejects unavailable Reader with `InvalidState` before any old getter call, releases Reader after the full synchronous delegate call even on exception, and never opens a new epoch. No existing getter/Player/managed API calls this wrapper. **Do not infer class pointer allocation validity, coherent whole-VM epoch, canonical TypeKeys, complete safe execution V1 or real shutdown/runtime behavior.**

Demo **tested code anchor `117cc6b1c2be8050cd2f433ef17db8b3c5138f93`** adds **25th** independently receipted `admitted-execution` source-host child, **nine** exact groups per strict/sanitized and **eighth** inventory flag. The old 24 children, 85 original discovered IDs, seven old inventories, five actual managed-positive+one negative and 100 native SDK syntax configs remain. Existing official SDK TU binds the inactive native method signature; no new TU/Player caller. Native [final CI 39735806552](https://github.com/night-outlook/il2cpp_plus/actions/runs/39735806552) **PASS 3/3** Mac/Linux compilers; demo [integrated CI 39736751961](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736751961) and [focused 39736752238](https://github.com/night-outlook/hybridclr_demo/actions/runs/39736752238) **PASS 2/2 each**. Initial source-verifier and mock-count CI failures remain recorded in [Primary Source Audit](History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/PRIMARY_SOURCE_AUDIT.md), not reclassified. **New installed Unity SDK execution at this tuple is NotRun** until new Local handoff.

Read the [new Design](History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/DESIGN.md), [one-cycle Plan](History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/PLAN.md), [Primary Source Audit](History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/PRIMARY_SOURCE_AUDIT.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_ADMITTED_EXECUTION_2026-10-22/EVIDENCE.json), and final exact-source [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md).

**One new source/host/official Unity2022.3.62f2 SDK syntax-only 25-component Local batch** may run ONLY after independently verifying four exact pushed heads, all consumed evidence/vendor SDK and four fresh never-used roots specified in final handoff. No retry, original getter activation, Unity Editor/Player, protected SNAP-01, Human Review Gate, H2/X02/M08A. **P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete.** Historical R02 fingerprint FAIL and full-stage independent review restrictions intact; all product/Human Review acceptance booleans false, PureInterpreter disabled.

---


## Latest authoritative Local: 20261021-7896 PASS (source/host/SDK syntax only)

Local-owned [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md) confirm **24/24 components Passed**, 85 original failure tests, seven source inventories, five real managed positives plus exact negative, **100/100** native SDK syntax commands and **20/20** Git postflight checks, with four exact repository heads verified and independent source/SDK/history preservation. The one-shot executed demo was `a5c0a4272efc4eee000220f40b7ca769be277917`, native `82ddcef9417e3d662fdd39916a92124b5c835094`. Both serialized lifetime flags are **false** and the inventory is `CompletedBatchFiles`. **PASS / PassedSourceHostAndSDKOnly**, no retry/Unity Editor/Player. Read [Primary reconciliation](History/M07R/R03/IR_Remediation/P1_GIT_MANIFEST_LIFETIME_2026-10-21/PRIMARY_RECONCILIATION_7896.md) and [raw checkpoint](History/M07R/R03/local-validation-p1-git-lifetime-20261021-7896/README.md).

Finding `IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01` retains its original `SourceConfirmed_NotFaultInjected` status; successor correction `CorrectedAndRegressionValidatedWithinHostScope_NoRealTimeoutInjected` was verified with a separate mocked Git-only timeout test, **not a real Git timeout**. **7c2c PASS** and **82dd raw FAIL** remain separate, unchanged historical outcomes. **P1/runtime/R03 acceptance is not established.** This correction is **closed within source/host/SDK-syntax scope**. The previous [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md) is **consumed/archival; no new Local execution is authorized** by it.

---


## Historical snapshot — pre-7896 Primary handoff

**Authoritative latest Local Validation:** `20261021-7c2c` [LOCAL_VALIDATION.md](Handoff/LOCAL_VALIDATION.md) FIRST, then [RETURN_TO_WEB.md](Handoff/RETURN_TO_WEB.md), [immutable checkpoint](History/M07R/R03/local-validation-p1-git-postflight-20261021-7c2c/README.md) and [finding](History/M07R/R03/local-validation-p1-git-postflight-20261021-7c2c/FINDING.json). Its exact *executed* tuple is demo `c5dde8493504cf69781fb0ab52123f525010a3aa`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`. **PASS / PassedSourceHostAndSDKOnly:** 24/24 independent components; 85 original tests; all seven source inventory flags; five actually compiled managed positives plus exact original negative; 100/100 original installed Unity2022.3.62f2 Apple arm64 C++17 SDK syntax; **20/20** final Git postflight commands exit0 and **all four** final repository heads independently verified; source/SDK/history audit Passed, **no batch retry**. No Unity Editor/Test Runner/Player, product native link, real GC/RSS, metadata Shutdown or complete P1/R03 runtime acceptance. `20261021-7c2c` raw/scratch/audit/checkpoint are consumed and immutable.

**Separate older Local `20261021-82dd` aggregate remains `FAIL / FailedOrIncomplete`**: its 24 child results Passed but final `hybridclr ls-remote` exceeded 120 seconds; original `sourcePreserved=false`, `fourRepositoriesAfter=[]`, exit1. Later independent preservation results do not overwrite `82dd` raw evidence.

### New Primary correction — source-host RED→GREEN, not new SDK evidence

- Latest Primary **demo tested code anchor `789655f19bd54c8abdcda67946a1f8195193176c`** changes only root manifest `commandLifetimeUnverified` to match the pre-existing aggregate `unknown_lifetime=stopped is not None or git_probe.unknown_lifetime`. On a **Git-only final postflight timeout**, both `RESULT.json` and `MANIFEST.json` now say `commandLifetimeUnverified=true`, while manifest `inventoryScope=UnsealedObservedFiles`, `sourcePreserved=false` and aggregate `FailedOrIncomplete` stay fail-closed. On successful Git postflight both remain false and inventory is completed. **The 120-second Git limit, SSH transport, source/remote guards, no-retry policy, 24 child scheduling, seven inventories, original 85 test IDs, five+negative managed contracts and 100 native SDK syntax matrix are unchanged.** No native/Unity production code or historical source pins changed.
- Existing `test_p1_command_failures.py` performs a **synthetic end-to-end** run of the real Python orchestrator with 24 mocked Passed children and a deliberately timed-out second repo `ls-remote`. It parses the separately emitted `RESULT.json` and `MANIFEST.json`, asserts identical true lifetime, failed aggregate, unsealed inventory, one partially verified final repo, and no false quiescence/runtime claim. Existing success and earlier child-timeout cases assert matching flags. No new discovered test IDs.
- **RED:** test-only `b29b6385b428e1cb3fbc5684306f6a754d1f7664` [integrated CI 39710461380](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461380) / [focused CI 39710461363](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710461363), **FAIL 2/2 each Mac/Linux** precisely on original false manifest flag.
- **GREEN:** corrected [integrated 85 CI 39710581913](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581913), [focused failure CI 39710581915](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581915), [managed receipt CI 39710581907](https://github.com/night-outlook/hybridclr_demo/actions/runs/39710581907), all **PASS 2/2 Mac/Linux each**. These check real checked-in Python behavior with **mocked Git/SDK/VM child operations**, not new installed Unity SDK validation or a real Git outage.

**Unchanged:** `night-outlook/il2cpp_plus@82ddcef9417e3d662fdd39916a92124b5c835094`, `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The current code change is **demo validation infrastructure only**, not activation of original getters/TypeKeys/Player.

**Required reading:** [Current status](Plan/CURRENT_STATUS.md), [Design](History/M07R/R03/IR_Remediation/P1_GIT_MANIFEST_LIFETIME_2026-10-21/DESIGN.md), [one-cycle Plan](History/M07R/R03/IR_Remediation/P1_GIT_MANIFEST_LIFETIME_2026-10-21/PLAN.md), [Primary source audit](History/M07R/R03/IR_Remediation/P1_GIT_MANIFEST_LIFETIME_2026-10-21/PRIMARY_SOURCE_AUDIT.md), [machine evidence](History/M07R/R03/IR_Remediation/P1_GIT_MANIFEST_LIFETIME_2026-10-21/EVIDENCE.json), and **final** [WEB_TO_LOCAL.md](Handoff/WEB_TO_LOCAL.md).

One new **24-component source/host/official SDK syntax-only Local batch** requires a fresh source-pinned handoff with four new absent/disjoint raw/scratch/audit/checkpoint roots and independent preservation admission. No retry or replacement of older `82dd` FAIL or `7c2c` PASS. No Unity Editor/Test Runner/Player, product native link, protected SNAP-01, H2/X02/M08A or Human Review Gate.

**P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete**. Original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, independent full-stage R03 FAIL/re-review NotRun, and original reporting 500ms/1..64/GC/logger/recovery/canary/performance constraints remain. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter disabled.
