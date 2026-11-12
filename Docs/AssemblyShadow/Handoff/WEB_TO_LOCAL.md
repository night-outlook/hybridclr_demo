# Primary Implementation → Local Validation — CLOSED / NO EXECUTION

## Current R03 B2 Primary native third-pass checkpoint — CLOSED / NO EXECUTION (2026-11-12 UTC)

**NO EXECUTION AUTHORITY.** An inactive native B2 source-only collector has been updated at il2cpp_plus@04d979fe55cea6b2dee7f5bfc49a71f2f1fb6386 to re-enumerate and check all owned per-class cctor/static values at the end of collection. Late mutation, missing callback or duplicate callback revokes owned rows/receipts. [Source/host review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_END_OF_COLLECTION_CLASS_FACTS_IMPLEMENTATION_REVIEW_2026-11-12.md). Native Ubuntu C++11/C++17 source-host CI success and exact four-fork source audit 2/2 success; macOS native jobs still queued at review checkpoint. No real Unity compilation/Player, GC or terminal V2 validation. **Local must report NoExecutionAuthority without running Unity or tests.**

Four branch pins: codex/assembly-shadow-r01b-h1; demo latest verified remote HEAD, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, il2cpp_plus@04d979fe55cea6b2dee7f5bfc49a71f2f1fb6386. Exact source manifest: 63 native/eight demo. Whole-VM epoch NotProven, nativeV2TransportImplemented=false, R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false. Do not reuse B1 oneuse-12 or begin H2/M08A/X02/SNAP-01.

---

## Current Primary B2 source-inventory checkpoint (2026-11-12 UTC)

**AUTHORITY: CLOSED / NO EXECUTION; Local must return NoExecutionAuthority.** The latest Primary work changed **source-admission infrastructure only**, not Unity/native runtime, Player or native V2. The exact original V1 GetExecutionDiagnosticsJson retains its 5,222-byte frozen body; the source gate now checks the 11 header + 11 class-value mapping expressions/order, original token-valid physical image source, registry, ctor/static/debug pointer and live R02 read boundaries. Four new focused Python tests passed locally; 20 semantic source mutants are rejected. [Review and source inventory](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_FIELD15_SOURCE_INVENTORY_REVIEW_2026-11-12.md). No new native tests or Local tests are authorized. Verify the final exact 4-repository HEADs before using as provenance; earlier static CI is not automatically transferable.

**Pins:** codex/assembly-shadow-r01b-h1 for all four; demo current latest pushed HEAD, hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de, il2cpp_plus@e5f8eebca1263181ed3fca49e84a1cf73f40b90b. Native source manifest remains **63-native/eight-demo**. No full field14/field15/GC/epoch or native descriptor V2 has been implemented or proved. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; nativeV2TransportImplemented=false; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION.

---

## Current Primary R03 B2 — verified original field15 formatter, visible class-fact drift rejection (2026-11-12 UTC)

**AUTHORITY: CLOSED / NO EXECUTION. Local must respond NoExecutionAuthority.** This is a Primary-owned **inactive native source/host** checkpoint. It neither reserves a new one-use batch nor authorizes an official Unity build, Player, GC/profiler run, local implementation, B1 oneuse-12 replay, H2/M08A/X02/SNAP-01 or a Human Review Gate. All nontrivial remaining implementation stays with Primary.

### Canonical repository identities

Branch for all four: `codex/assembly-shadow-r01b-h1`; canonical remote `https://github.com/night-outlook/<repo>.git`. Expected default Local checkout root: `/Users/ah/GitHub/hybridclr`; web did not inspect actual Local worktrees.

| Repository | Expected Local worktree | Exact latest native/other source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | latest verified pushed HEAD, because updating this document advances it |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | e5f8eebca1263181ed3fca49e84a1cf73f40b90b |

The [63-native/eight-demo exact source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins original V1 getter/TypeKey/physical owner/diagnostic code; actual original R02 live and frozen serializers, observation counters, R02 snapshot and diagnostics profile; new field15 serializer differential host and CI; the native ClassFacts source and all class-source host/CI files. Independent original V1 `GetExecutionDiagnosticsJson` body remains byte-identical to its 5,222-byte historical source fixture. Native source/ABI/package SHAs above remain authoritative. A future executable batch MUST additionally pin actual official Unity 2022.3.62f2 macOS arm64 IL2CPP/diagnostics2/Bee C++11 SDK, installed native sources, original-S, BridgeTable, GameAssembly UUID/SHA, fresh Player identities and one-use raw/product custody; none is available as current empirical B2 evidence.

### Primary implementation and exact test results

1. **Full JSON formatter equivalence for immutable inputs.** NativeHostTests/AssemblyShadowExecutionV1SerializerParityHost.cpp compiles the **actual** original V1 execution serializer and live R02 formatter and separately the **actual** bounded frozen Record/Writer and frozen R02 formatter. Exact bytes match for the same caller-owned immutable class rows and R02 counter values, including entire R02 suffix, Unicode/escaping, class cctor/static, 64-bit metrics and empty/nonempty rows. Two cases demonstrate changed cctor input or live R02 counters cause different bytes, not false acceptance. Guarded host allocation remains zero during frozen formatting. [CI 43178421718](https://github.com/night-outlook/il2cpp_plus/actions/runs/43178421718): **4/4 PASS**, Mac/Linux C++11/17 × Release/Debug × strict/ASan-UBSan, **16 host processes × ten cases/91 assertions**, six matching class rows/process. This is real serializer code over synthetic inputs, **not actual Unity class capture or original full field15 semantics**.
2. **Native class-fact drift detection.** The inactive true source `TryCaptureBoundedDefinitionExecutionLive` now records, after each first physically registered AOT class callback, only the displayed cctorStarted/cctorFinished/initializationException booleans and numeric static_fields address, with a **16-byte per-slot exact primitive snapshot for 2,048 registry slots (32 KiB temporary stack)**. On the second existing physically matched callback it compares these before/after TypeKey formatting; a witnessed change yields `ObservedClassFactsChanged` and revokes all owned rows, frozen record, original-V1 owner/class-fact positive receipts. Temporary address-value storage is cleared while `g_MetadataLock` and initial Reader are alive. [CI 43180369312](https://github.com/night-outlook/il2cpp_plus/actions/runs/43180369312): **4/4 PASS**, 16 Mac/Linux C++11/17 Release/Debug strict/sanitized host processes × **76 cases/1,865 assertions**, including three cctor/static drift failures, including a mutation during TypeKey formatting. No global class/GC epoch, terminal safety or official Unity native compilation follows from these mocked source tests.
3. **Four-repository strict source admission.** [CI 43179431213](https://github.com/night-outlook/hybridclr_demo/actions/runs/43179431213): **2/2 PASS** macOS/Ubuntu, 63 native source/ABI/test files and eight demo independent source mirrors/frozen original getter; original live/frozen R02 field and Metric mapping parity, false full-field/product flags. Final demo HEAD CI may rerun on this handoff update; inspect latest actual run before asserting its outcome.

[Detailed design, independent source review and remaining work](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_EXECUTION_FIELD15_SERIALIZER_AND_CLASS_FACTS_REVIEW.md). The previous [original V1 first-owner review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_FIRST_OWNER_RECONCILIATION_IMPLEMENTATION_AND_REVIEW.md) remains valid for only its admitted AOT TypeDef subset. The **original** V1 execution getter, B1 native first-event path and active Player behavior are UNMODIFIED.

**Historical boundary:** B1 oneuse-12 executed against different pinned demo/native SHA (`2d690bb2f7234ddcbee339f9da7125d687f5ed45`, `8aa8d09319a89b55b2496bcc2c69ccc69cb57be9`) and yielded focused real Unity Player **19/19 PASS**. Its source/raw evidence/roots are immutable and consumed; not substitute for any B2 field15, native V2 or Player acceptance. Original independent R03 full-stage FAIL and both High IR-R03-01/02 remain unresolved. PureInterpreter disabled.

### Still Primary-owned blockers, NOT Local implementation

- **Full original V1 nonempty field15 source equivalence:** complete observed class registry, interpreter/VAR/MVAR/unsupported types, TypeKey source and actual class/GC/cctor/static metadata lifetime; identical formatter bytes on synthetic rows do not authenticate real class state or prove all-original V1 JSON bytes. Prior healthy-time original-vs-bounded byte probe has not executed in an actual Unity Player.
- **Complete terminal-safe original field14 and field15:** independent full finalDiagnostics and finalExecutionDiagnostics source values, correct terminal state/counters/class lifetime and one coherent consistency boundary. Two existing physical enumerations and first/final cctor snapshots are observational, allow later mutation/ABA, and cannot be substituted by B1 first-error or partial rows.
- **Native V2 transport and independent recovery:** existing bounded codec + descriptor-relative single-owner, preopened artifact-first/envelope-last native transaction must be integrated with complete field14/15 and source/ABI/SDK/PID/nonce/fixture identity; independently authenticated external receipt and strict readback, symlink/torn-write/replay/reentry/race negative CI.
- **Independent source review and exact handoff:** complete the Primary code/host/static CI and separately review full design→implementation→tests, source/VM lifetime, and four exact clean SHA pins, then explicitly reopen an executable WEB_TO_LOCAL. Local only observes real environment and may apply bounded fixes after an authorized cycle.

### Conditional future single-batch Local Validation — NOT RUNNABLE

Only when Primary explicitly authorizes, use one new immutable four-SHA source tuple and previously absent owner-only 0700 one-use roots. Perform **one** official Unity 2022.3.62f2 macOS arm64 IL2CPP Release/diagnostics2 C++11 Bee build and **three** genuinely fresh Players (Empty, initializer error19, captured generic guard15), jointly validating:

- four Git remotes/branch/SHAs/63-native-eight-demo blobs, original-S identity, clean source and two spaced capacity checks;
- full original Class.cpp/Assembly.cpp/AssemblyShadow.cpp Unity native TUs, 32-KiB temporary class-fact snapshot stack budget, metadata Reader/GC lifecycle, no test-only global allocators in GameAssembly, generated BridgeTable, binary/SDK UUID/SHA;
- complete original and frozen class/TypeKey/R02/field14/15 JSON bytes from real primitive, Unicode, generic and interpreter/AOT owner fixtures, including class cctor/static mutations and R02 counter drift;
- full native V2 terminal envelope+artifact+external identity-bound receipt/strict independent recovery and original native B1 first reason equality;
- negative invalid image/first-owner, missing/changed class source, metadata epoch/ABA, terminal teardown, GC/races, duplicate/partial/symlink/replay, and source/product custody;
- first-call/GC/RSS/stability and independent raw/host/product verification.

None of this future Local work is authorized at present. Local report now: **NoExecutionAuthority**, without a build or Player.

**Current product flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. No new oneuse-13, no H2/M08A/X02/SNAP-01, no Human Review Gate self-approval.

**Local read-only order:** Docs/AssemblyShadow/README.md → Handoff/WEB_TO_LOCAL.md → B2_EXECUTION_FIELD15_SERIALIZER_AND_CLASS_FACTS_REVIEW.md → exact source manifest → historical Local reports as background only. Stop and return NoExecutionAuthority.

---

## Current Primary R03 B2 — original V1 FIRST physical owner reconciliation; NO LOCAL EXECUTION (2026-11-12 UTC)

**Authority: CLOSED / NO EXECUTION. Local Agent response: NoExecutionAuthority.** This is an inactive source/host checkpoint, **not** an executable Local Validation order. Do not create one-use output roots, run Unity, build GameAssembly, launch a Player, replay consumed B1 oneuse-12, modify the native architecture locally or start H2/M08A/X02/SNAP-01. Original independent R03 full-stage FAIL and both High findings remain open; PureInterpreter stays disabled.

### Source identity / canonical paths

All four canonical HTTPS remotes are `https://github.com/night-outlook/<repo>.git` and use branch `codex/assembly-shadow-r01b-h1`. The expected default Local checkout paths below were **not inspected in this web environment**; a future explicitly authorized Local batch must independently verify each actual remote, branch, clean worktree and exact HEAD.

| Repository | Expected default Local checkout | Exact current source pin |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | current pushed GitHub HEAD; this handoff itself advances that SHA |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | 648f3b2c5c0d0b86954c339ac3d75fdb96ce1ba2 |

[Exact 57-native/eight-demo source candidate](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins native C++11 implementation, original V1 enabled getter 5,222-byte independent source fixture, updated Assembly.cpp/Assembly.h, pure original V1 first-owner scan/join and host CI, original metadata ABI/serializer/TypeKey and all six previously reviewed demo sources.

**Historical evidence boundary:** B1 oneuse-12 focused real Unity 2022.3.62f2 macOS ARM64 IL2CPP Player **19/19 PASS** executed against a DIFFERENT demo/native source tuple (demo `2d690bb2f7234ddcbee339f9da7125d687f5ed45`, native `8aa8d09319a89b55b2496bcc2c69ccc69cb57be9`). Its raw roots and source are consumed/immutable. Current B2 changes were NOT tested in a real Unity Player or official C++ native full translation unit.

### Primary implementation, source findings and exact tests

**Critical source correction:** Original V1 `Assembly::CaptureShadowEnumeration` uses the actual `CopyValidAssemblies` physical assembly iterator, **not GetAllAssemblies' logical remapping**. Original V1 includes all token-valid physical assemblies (interpreter and zero-TypeDef images included) and uses the **first** `MetadataTypeImages.emplace` owner for each handle. The previous bounded physical source authenticated against registered AOT images only, which could choose a different owner when an earlier interpreter image contained the same opaque TypeDef handle.

Primary added `AssemblyShadowOriginalV1ImageScan.h`, `AssemblyShadowOriginalV1OwnerJoin.h`, and `Assembly::TryVisitOriginalV1ExecutionImages` under the original s_assemblyLock. The inactive actual physical AOT source now takes an independent, bounded all-original-V1 image inventory under the initial metadata Reader and g_MetadataLock, verifies first-emplace original owner equality for **each** admitted AOT base, ancestor, generic/array/qualified/Unicode and primitive TypeDef handle **after registered-AOT ownership is proven but before metadata dereference**, and rechecks the ordered original V1 inventory. Mismatched interpreter-first ownership, absent original owner, change of original image set, malformed/oversized image or lookup budget refuses the result with typed errors; original rows/record/positive provenance flags are scrubbed on failure. Registered AOT source, physical class witnesses, existing composite/Unicode/default primitive and B1/R02/revision fences remain unchanged. **Original V1 getter, B1 native first-error and all active player logic are untouched.**

- [Final exact native source-mock CI 43175809258](https://github.com/night-outlook/il2cpp_plus/actions/runs/43175809258): **4/4 completed/success**, macOS/Linux × C++11/C++17, 16 Release/Debug strict/ASan-UBSan processes; 73 actual restricted native source scenarios and 1,673 assertions per process, plus three fake-reference parity adapter and 20 primitive lookup cases. This compiles real inactive `.inl` source with **synthetic VM classes**, NOT Unity Assembly.cpp/Player.
- [Pure first-emplace original V1 join CI 43174989182](https://github.com/night-outlook/il2cpp_plus/actions/runs/43174989182): **4/4 completed/success**, 12 cases/41 assertions per host process across Mac/Linux C++11/17 Release/Debug strict/sanitized, zero protected allocations; checks interpreter-first conflict, interpreter-late duplicate first-wins, token-zero skip, zero-TypeDef, missing/invalid image and budgets. No real Unity registration source.
- [Exact four-repo source audit 43176359646](https://github.com/night-outlook/hybridclr_demo/actions/runs/43176359646): **2/2 completed/success**, macOS/Linux, **57 native/eight demo exact Git blobs, 27 negative/admission tests per OS**, original V1 getter unchanged and current field15/full-product flags false. After this document advances the demo branch, a subsequent audit run must be independently checked before claiming final HEAD success.
- [Primary design, independent source review, evidence limitations and future single-batch matrix](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_V1_FIRST_OWNER_RECONCILIATION_IMPLEMENTATION_AND_REVIEW.md).

The bounded receipt's `originalV1FirstEmplaceOwnerMatched=true` applies **only to admitted source TypeDef handles** from the restricted physical class subset. It does NOT prove all original V1 rows, original complete nonempty `finalExecutionDiagnostics` field15 JSON bytes, original class cctor/static values or atomic/source-ABA coherence; the two original V1 snapshots compare image identities/order only. The prior healthy-time observational original V1 byte probe may allocate, reads two separately timed sources and has not run against a real original Unity getter.

### Still Primary-owned blockers — no Local architectural fixes

1. Complete real original V1 **full nonempty field15** class/TypeKey/field/array/order/JSON byte semantics and valid source/class/GC lifetime, including interpreter/VAR/MVAR/unsupported rows and original cctor/static state changes. Current first-owner subset is necessary, not sufficient. Verify actual Unity source and preserve the unchanged original getter.
2. Produce terminal-safe **complete original `finalDiagnostics` field14 and `finalExecutionDiagnostics` field15**, under a defensible class/GC/metadata generation/lifetime contract. Healthy-time metadata admission and double-sampled original/registered image identities are NOT a coherent VM epoch or safe postterminal source. Neither B1 text nor partial bounded physical rows can substitute for required complete fields.
3. Integrate already host-tested native bounded V2 codec, one-owner preopened descriptor-relative artifact-first/envelope-last native transaction, externally authenticated origin/nonce/PID/source/GameAssembly/SDK/fixture receipt and independent recovery reader. Add typed source/identity drift, torn-write/partial/symlink/duplicate/replay/GC/race tests.
4. Independently review complete design→implementation→tests and strict source admission, commit/push final exact four SHA tuple and then explicitly authorize ONE new executable one-use Local cycle with reserved fresh absent owner-only roots and exact native build/Player commands. All nontrivial corrections remain Primary-owned.

### Future one-batch Local Validation — CONDITIONAL, NOT RUNNABLE

After all Primary prerequisites and **new explicit executable** handoff:
| Gate | Consolidated validations | Grounded raw evidence |
| --- | --- | --- |
| 0. Admission | Four correct remotes/clean exact SHAs, 57/8 Git blob manifest and all OS CI, immutable Original S custody, Unity2022.3.62f2 macOS ARM64 SDK/Bee/C++11 verification, two time-separated capacity samples and *fresh previously absent owner-only* output roots | exact source/tree/branch receipts, Unity/SDK/Original-S/host/capacity/root provenance |
| 1. Native build/link | One real IL2CPP Release/diagnostics2 Unity build with original Class.cpp/Assembly.cpp, original-V1 source, AOT/interpreter images and new first-owner source, generated bridges, host-only allocator exclusion | full compiler/link/Bee logs, SDK source hashes, BuildReport, GameAssembly UUID/SHA, linked symbol list |
| 2. Three fresh Players | Empty baseline; initializer error19; captured generic guard15, authentic AOT vs interpreter registration order/handle aliases, primitive/Unicode/constructed/array/qualified keys, complete original V1 field14/15 and B1 first reason | independent PID/run IDs/nonce/fixtures/requests, original/owned JSON full byte parity/first-diff offsets, original V1 owner source observations, B1/AOT canary |
| 3. Authenticated V2 | complete original terminal-safe field14/15, one-use native descriptor-relative binary/envelope, independent external identity-bound receipt/readback | binary/envelope/receipt, file dev/inode/size/SHA, UUID/PID/nonce/source/fixture join |
| 4. Adversarial/GC | original V1 interpreter-first conflict vs later duplicate, missing owners, zero TypeDef, over-budget, modified/reloaded metadata, B1 event during source, class GC/teardown and double finalize, symlink/partial/replay | typed failures, unchanged B1 first event and AOT canary, no false seal, Player/crash/GC logs |
| 5. Stability/custody | GC/RSS/first-call and startup/shutdown stability; separate host/product/raw provenance and independent regular-only product seal | profiler/Player output, GC/RSS metrics, strict independent raw/product verifiers, Local Validation and RETURN_TO_WEB |

**No current execution root, new oneuse-13, local command, Player or approval is authorized.** This document is read-only for Local while closed.

**Product flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

**Local read order:** `Docs/AssemblyShadow/README.md` → `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` → `B2_ORIGINAL_V1_FIRST_OWNER_RECONCILIATION_IMPLEMENTATION_AND_REVIEW.md` → `b2_definition_native_candidate.json` → prior Local-owned reports only for historical context. If invoked now, report **NoExecutionAuthority** without Unity/Player work.

---

## Current Primary R03 B2 — original V1 observational field15 parity probe; NO LOCAL EXECUTION (2026-11-12 UTC)

**AUTHORITY: CLOSED / NO EXECUTION.** Local Agent disposition remains **NoExecutionAuthority**. This is a source/host implementation checkpoint, NOT an executable order to build Unity, start a Player, create one-use roots, replay consumed oneuse-12, start H2/M08A/X02/SNAP-01 or self-approve a Human Review Gate. Nontrivial architecture and implementation remain exclusively with Primary Implementation.

### Exact repository/branch and current source pins

Canonical remotes: https://github.com/night-outlook/<repo>.git; all branches `codex/assembly-shadow-r01b-h1`. The default local paths are reference layout only and were **not inspected** in this web environment. Verify actual remote, branch, clean worktree and SHA in any future authorized Local batch.

| Repository | Expected default Local worktree | Current native/other source SHA |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | latest pushed GitHub branch HEAD; this handoff changes that commit |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | 2670b6cfc7006c9483c4c9322808c152efa16772 |

[Exact 53-native/six-demo source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins all ABI/serializer/source/CI Git blobs, the pure V1 parity header mirror, and the **exact original enabled GetExecutionDiagnosticsJson 5,222-byte reference body** frozen from the prior native 68530d7... source. The current native enabled getter has been byte-compared to that fixture; the separate FeatureDisabled getter definition is not confused with the original enabled implementation. The source audit prohibits silent getter changes.

Future native/SDK build constraints (not yet executed): Unity 2022.3.62f2 macOS ARM64 IL2CPP ON Release/diagnostics2 with verified actual original C++11 Bee/SDK overlay, fixed HybridCLR interpreter and Unity package commits above, generated BridgeTable and GameAssembly UUID/SHA to be measured from a new build. Never substitute the historical B1 oneuse-12 binary/fixture/PID/nonce/roots or a prior CI run for an actual new B2 build.

### Completed Primary implementation and source-only evidence

The new **inactive, healthy-time-only** `AssemblyShadow::TryProbeBoundedExecutionV1ByteParity` calls the unchanged **actual original** `TryGetExecutionDiagnosticsWithMetadataAdmission` wrapper, then separately captures the original physical registered-AOT TypeDef subset into an owned `Record` and compares exact JSON bytes with a C++11 one-shot allocation-free comparator. One outer initial-session metadata Reader covers both calls. On original getter error/exception, missing/over-budget source, failed physical source, different bytes or reused probe, it clears old reference bytes and revokes all positive bounded rows/receipt/record state. On a byte-exact match the result remains `twoIndependentObservationsOnly=true`, with `coherentVmEpochProven=false`, `fullCanonicalTypeKeysProven=false`, `terminalSafeFinalExecutionDiagnostics=false`, `nativeV2TransportImplemented=false`, `runtimeAcceptance=false`. It is **not** a terminal V2 field15 producer and no Player/legacy getter interface was changed.

- [Native actual .inl source + parity wrapper synthetic reference CI 43146481197](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146481197): **4/4 PASS**, Mac/Linux C++11/17, 16 Release/Debug strict/ASan-UBSan processes, each with **67 physical-source cases, three adapter cases and 1,258 assertions**, plus the existing 20 primitive Peek mapping tests. The **fake original** in this host intentionally uses another bounded capture; it cannot prove real V1 parity.
- [Pure observational parity comparator CI 43146317881](https://github.com/night-outlook/il2cpp_plus/actions/runs/43146317881): **4/4 PASS**, Mac/Linux C++11/17, ten deterministic exact byte/mismatch/length/capacity/reused/failed-input cases, 42 assertions/process in Release/Debug strict/sanitized.
- [Exact 53-native/six-demo source CI 43148172788](https://github.com/night-outlook/hybridclr_demo/actions/runs/43148172788): **2/2 PASS**, Mac/Linux, **25 negative/admission tests per OS**, frozen original enabled getter source byte identity, exact whole-source Git blob and four branch source SHA pins, original serializer/metadata Reader/R02/diagnostic formatter sources and all full product flags false.
- [Independent source review, design, evidence, risks and staged one-batch Local matrix](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_OBSERVATIONAL_ORIGINAL_V1_PARITY_PROBE_IMPLEMENTATION_AND_REVIEW.md).

These are verified **host/source** tests. No real official Unity `AssemblyShadow.cpp`/Class.cpp full C++ TU, GameAssembly link, actual original V1 nonempty diagnostics/real-class metadata, Player, postterminal capture, real native V2 binary/envelope/receipt or first independent recovery has executed at the current source revision. Original B1 oneuse-12 focused macOS IL2CPP Player **19/19 PASS** remains immutable, consumed and out of this scope. Original independent R03 full-stage FAIL and High IR-R03-01/IR-R03-02 remain open, PureInterpreter remains disabled.

### Remaining Primary-owned blockers before any executable Local authorization

1. Prove **real original complete nonempty V1 field15 byte/semantic parity** on genuine Unity metadata, including original `Assembly::CaptureShadowEnumeration` **logical image map** versus the new raw registered physical AOT owner map. No source-only mock or dual-read equality can establish a coherent VM epoch or universal TypeKey/class/R02 correctness. Reject unsupported/interpreter/open classes and wrong owner maps rather than constructing a new class or inventing a key.
2. Produce terminal-safe, source-owned **complete** `finalDiagnostics` field14 and `finalExecutionDiagnostics` field15 matching the actual original V1 field contract. Prove physical observed class allocation/GC/teardown/source lifetime, cctor/static and metadata generation. The current healthy-time admitted getter may allocate and is not a postterminal source; complete field15 cannot be replaced by partial physical rows, the B1 first reason or null.
3. Integrate the existing pure bounded native V2 codec, preopened descriptor-relative single-owner transaction, artifact-first/envelope-last envelope, independently authenticated external receipt/strict reader and full first-recovery identity/source/provenance. Add typed failure and negative crash/reentry/symlink/partial/duplicate/race tests.
4. Independently review updated full native design→implementation→tests, source/ABI and four exact pushed Git SHAs; only after all prerequisites pass may Primary write a **new executable** WEB_TO_LOCAL with fresh absent one-use roots, real commands, expected data, exact source, environment and empirical acceptance criteria. Nontrivial fixes never transfer to Local.

### Future consolidated one-batch Local Validation matrix — CONDITIONAL, NOT EXECUTABLE

When a future **explicitly reopened** handoff exists, run **one** exact source-pinned Unity2022.3.62f2 macOS ARM64 IL2CPP build and **three** distinct fresh Players to answer as many independent issues as possible, preserving original-S/host/Player raw custody and not reusing the consumed B1 oneuse-12:

| Batch gate | Proposed combined tests | Required raw evidence |
| --- | --- | --- |
| 0. Git/SDK/custody admission | Four clean exact HEAD/source-blobs and 53/6 source audit; original-S immutable custody, official Unity/IL2CPP/Bee source, two spaced disk-capacity samples and absent owner-only 0700 fresh roots | branch/source hashes, OS/SDK/Bee/Original-S receipts, source CI and capacity/ownership checks |
| 1. Real native compile/link | Full Class.cpp and AssemblyShadow.cpp Unity C++11 TUs, physical AOT/Unicode/primitive ABI, original getter and actual parity wrapper; generated method bridges, no host-only allocator sources in GameAssembly | compiler/link stdout, exact installed native/BridgeTable source roster, BuildReport, GameAssembly UUID/SHA, nm/symbol proof |
| 2. Three positive Players | Empty, initializer error19, captured generic guard15 with real primitive/Unicode/constructed/qualified types and original logical vs physical owner images; full original V1 field14/field15 byte equality and B1 first reason | distinct PID/nonces/request/fixtures, old and owned exact JSON byte/parity offsets, type-owner and cctor/static flags, original first-error and AOT canaries |
| 3. Complete native V2 | Full terminal-safe field14+15, original first event, preopened descriptor-relative artifact/envelope transaction and identity-bound external reader/receipt | raw diagnostics.v2.bin, envelope.v2.json, external receipt, SHA/size/dev/inode/source/PID/fixture/SDK and independent first-recovery match |
| 4. Adversarial/lifetime | Original logical/physical owner discrepancy, malformed Unicode/primitive default, stale metadata epoch or registry revision, B1-during-read, missing/changed/partial/symlink V2, duplicate finalize, GC/teardown | typed rejection, unchanged first-error and AOT canary, no false original/owned equality, GC/crash logs and no false V2 seal |
| 5. Stability/performance/custody | GC/RSS/first-call budgets, crash-free startup/shutdown, exact raw/host/product provenance and two independent auditors | profilers/Player logs, GC/RSS traces, original-S and regular-only immutable product manifests, LOCAL_VALIDATION.md/RETURN_TO_WEB.md |

No new one-use root/number or executable Local command has been authorized or reserved. All future significant implementation remains Primary-owned.

**Flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. No H2/M08A/X02/SNAP-01, and no Human Review Gate self-approval. Local reply while closed: **NoExecutionAuthority**.

**Local read-only order:** Docs/AssemblyShadow/README.md → Handoff/WEB_TO_LOCAL.md → B2_OBSERVATIONAL_ORIGINAL_V1_PARITY_PROBE_IMPLEMENTATION_AND_REVIEW.md → exact source manifest → historical Local reports only as background. No Local build or test execution until reopened by Primary.

---

## Current Primary R03 B2 — assert-free existing primitive default source; NO LOCAL EXECUTION (2026-11-12 UTC)

**AUTHORITY: CLOSED / NO EXECUTION. Local Agent response: NoExecutionAuthority.** This is a Primary-owned **source-only** implementation checkpoint, not a command to run a Player, build Unity, reserve one-use output roots, rerun consumed oneuse-12, approve H2 or begin any later milestone. All nontrivial missing implementations stay with Primary.

### Exact current source identity

Canonical remote for each: https://github.com/night-outlook/<repository>.git; branch codex/assembly-shadow-r01b-h1. Default local checkout paths below are expected layout only, not evidence of actual current Local worktrees; verify git remotes and branch/HEAD independently before any future authorized batch.

| Repository | Default local checkout | Latest remote source pin |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | latest actual pushed branch HEAD; this handoff itself advances the demo commit |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | 68530d7ecb86c9122d9ae5eb20366ccb0ea086b6 |

[Exact 42-native/4-demo Git-source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) includes original Class.cpp/Class.h, Il2CppClass actual metadata fields, the original Unicode sources and all new TypeKey source/mock/workflow files. Required eventual Unity build: official Unity 2022.3.62f2 macOS arm64, IL2CPP ON/Release/diagnostics2, actual C++11 Bee source mode and installed canonical 4-repository native/runtime/package pins. A new official SDK/Original-S inspection, generated bridging/table and GameAssembly file/symbol checksum must be measured in the future approved batch, not inferred from current source/mock CI.

Historical oneuse-12 B1 completed at demo 2d690bb2f7234ddcbee339f9da7125d687f5ed45, native 8aa8d09319a89b55b2496bcc2c69ccc69cb57be9, focused real Player **19/19 PASS**, and is consumed. No historical root, executable, PID, fixture, nonce, Git evidence or CI status may be repurposed as current B2/field15/V2 acceptance.

### Primary code, diagnostic, design and tests completed

**Corrected primitive source risk:** Original Class.cpp::FromIl2CppTypeEnum uses a debug IL2CPP_ASSERT on an unavailable initialized default. The inactive native physical observed-class TypeKey source now calls a separate **null-safe, allocation-free Peek** over existing il2cpp_defaults fields. The exact source gate mechanically compares the **19** original Class.cpp type-code→default-class mappings with those in the new primitive Peek header. A null/unknown/unregistered primitive fails without calling original debug assertion, class constructors or metadata cache creation. A nonnull existing default must independently prove registered physical AOT TypeDef owner/image, metadata namespace/name parity, zero generic arity and no nested/generic class fields inside the original metadata Reader and lock. Missing/mismatched sources revoke all source, class, Unicode, composite and primitive receipts and the frozen record. Existing original V1 getter, native B1, R02 and active runtime behaviors unchanged; original ViewName/NextFolded Unicode, composite generic/array/qualified and first-error/registry fences persist.

- [Final native actual inactive .inl + Peek mock 43141452521](https://github.com/night-outlook/il2cpp_plus/actions/runs/43141452521): **4/4 completed/success** (macOS/Ubuntu × C++11/C++17), 16 Release/Debug strict/ASan-UBSan host executions × **67 source scenarios and 1,236 assertions per execution**; **20** direct primitive Peek missing/present/unknown table cases in each execution. It compiles the production inactive .inl and actual Peek header against fake VM data, NOT Unity's entire Class.cpp, real il2cpp_defaults or GameAssembly.
- [Final exact four-fork source audit 43141581601](https://github.com/night-outlook/hybridclr_demo/actions/runs/43141581601): **2/2 completed/success** macOS/Ubuntu; **42 native/four demo exact Git blobs**, **22 negative/admission Python tests per OS**, actual original Class.cpp switch↔new Peek 19-case bijection and source/no-assert constraints; output PassedInactiveSourceOnly_NotFullV2, Local/full product flags false.
- [Final corrective implementation/design/independent source findings](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md), [staged remaining B2 plan](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md), [original Unicode and composite source history](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md).

**Not performed:** official Unity/IL2CPP native full translation-unit/Class.cpp build or link, actual initialized Unity primitive/default metadata parity, real Player B2, full original nonempty execution field15 byte equivalence, terminal-safe full general field14/execution field15, independently authenticated native V2 binary/envelope/receipt, GC/metadata teardown or coherent whole-VM epoch. Original independent R03 full-stage FAIL, High IR-R03-01/IR-R03-02, strict historical custody Blocked and pure interpreter disablement remain unchanged.

### Earliest unfinished Primary work — NO Local architecture edits

1. Prove original full GetExecutionDiagnosticsJson field15 byte/semantic parity using genuine Unity source classes/metadata (empty/nonempty, Unicode, nested generics/arrays/qualifiers, preinitialized primitive defaults, unsupported VAR/MVAR), preserving exact legacy schema and errors. Host-model exact grammar and original Class.cpp text are necessary but **not sufficient** acceptance.
2. Capture complete finalDiagnostics field14 and finalExecutionDiagnostics field15 under a legitimate terminal-safe class/GC/metadata lifetime. The present healthy-time initial Reader, physical registered AOT roster and independent registry/counter/B1 fences are **observational**, not a coherent VM epoch and not safe postterminal complete sources. Do not place B1 reason, partial class bytes or fabricated null in original full V2 slots.
3. Integrate the existing bounded native V2 wire encoder, descriptor-relative single-owner transaction and independently authenticated native artifact/envelope/receipt/recovery join. Test absent immutable roots, one-use, no reentry, symlink/path alias, duplicate/partial writes, source lifetime, Unicode invalidity and first-error/metadata races with adversarial native/host/static CI.
4. Independent review and exact four-pushed-SHA source gate, then issue a **new explicitly executable** WEB_TO_LOCAL and fresh one-use output roots only after source/readiness prerequisites pass. All nontrivial code corrections remain Primary-owned.

### Consolidated eventual Local Validation matrix — CONDITIONAL, NOT EXECUTABLE

Once Primary explicitly authorizes **one** source-pinned one-use batch, Local should answer multiple independent problems within **one** official Unity 2022.3.62f2 macOS arm64 IL2CPP Release build and **three** genuinely fresh independent Players, keeping host evidence, original-S and Player product separate:

| Checkpoint | Combined tests | Required independently grounded evidence |
| --- | --- | --- |
| 0. Admission | Four clean exact repository pins, source manifest **42 native/4 demo**, 4/4 native and 2/2 source CI; original-S/Unity/SDK and two separated capacity checks; fresh owner-controlled previously absent 0700 output roots | exact remote/branch/HEAD/working tree/blob receipts, OS/SDK source hashes, Original-S custody and capacity/root ownership |
| 1. Native TU/link | Original Class.cpp direct default and new 19-case assert-free Peek compile against true Unity ABI, real primitive il2cpp_defaults availability, generated MethodBridge and composite source install, linked global-new/delete host exclusion | Bee/C++ command and stderr, installed source/Git hash roster, BuildReport, generated table, GameAssembly UUID/SHA, linked nm symbol evidence |
| 2. Three positive Players | Empty baseline, real initializer failure19 and captured generic guard15; authenticated registered AOT TypeDefs, preinitialized Int32/other primitive class and Unicode/nested/qualified canonical TypeKeys; original V1 complete field15/field14 equality and native B1 first reason | three distinct PID/runId/nonce/case/request/build/fixture records, V1 complete fields and class ordering/flags/type-key bytes, native B1/AOT canary and physical owner traces |
| 3. Actual full V2 | Terminal-safe full field14+15, one-owner preopened artifact-first/envelope-last native descriptor transaction, independent identity-bound external receipt and strict reader | original raw binary, envelope, external receipt, PID/fixture/source, inode/device/size/SHA and readback logs |
| 4. Adversarial/GC | Missing preinitialized primitive, wrong generic/type handle, unregistered/ambiguous owner, Unicode malformed, stale metadata generation, B1 race, teardown/GC, duplicate finalize, partial/symlink artifact | typed rejected/invalid states, no first error replacement, unchanged AOT canary, no false V2 seal, OS crash/GC evidence |
| 5. Stability/performance/custody | GC/RSS/first-call deltas, crash-free Player start/stop, source/SDK/native identity consistency, independently verified regular-only product seal | CPU/GC/RSS/Player logs and time series, independent source/product/host signed/hashes, LOCAL_VALIDATION.md and RETURN_TO_WEB.md |

**No new Local execution authority, command, approved one-use number, fresh root, build or Player exists now.** Local may read only; no rerun oneuse-12, no H2/M08A/X02/SNAP-01 and no self-approval of Human Review Gate.

**Flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION. PureInterpreter disabled.

Read order: Docs/AssemblyShadow/README.md → Handoff/WEB_TO_LOCAL.md → B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md → exact source manifest → Local historical reports when necessary. Until formally authorized, Local replies **NoExecutionAuthority**.

---

## Current Primary R03 B2 — existing primitive-default source; NO LOCAL EXECUTION (2026-11-12 UTC)

**CLOSED / NO EXECUTION. Local response: NoExecutionAuthority.** The bounded native source is *inactive* and still cannot produce full terminal field14/15 or authenticated native V2 transport. No new Unity build/Player execution, new one-use label/root, Local architecture change or Local test run is authorized. Do not replay the consumed oneuse-12 or enter H2/M08A/X02/SNAP-01.

### Repository identity and exact remote pins

All four repository remotes are the canonical https://github.com/night-outlook/<name>.git, branch codex/assembly-shadow-r01b-h1. The paths below are expected **default local paths** only; the web agent did not inspect the Local machine and these must be verified before a later authorized batch.

| Repository | Expected default Local checkout | Latest pushed source pin |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | latest actual GitHub branch HEAD; verify before handoff, because this document itself advances that commit |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | f6530b221f0ef98ff38436ca8cd2692304d63265 |

The [exact 41-native/four-demo machine manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins original Class.cpp/Class.h/Il2CppClass metadata ABI, actual inactive source and C++11/17 host workflow. Historical B1 oneuse-12 executed at demo 2d690bb2f7234ddcbee339f9da7125d687f5ed45 and native 8aa8d09319a89b55b2496bcc2c69ccc69cb57be9, with focused **19/19 real macOS IL2CPP Player PASS**; its source, raw evidence and roots are consumed/immutable. It is NOT current B2 primitive/field15 validation.

**Expected eventual native/SDK build pins:** Unity 2022.3.62f2 macOS ARM64 IL2CPP ON, Release/diagnostics2, C++11 Bee; fixed HybridCLR and Unity package commits above, native fork f6530b..., future generated bridge and actual Unity engine/IL2CPP SDK source roster, GameAssembly UUID/sha and Player binary identity to be derived from one future build, never invented or borrowed.

### Primary implementation and test evidence completed

In the inactive physical observed-class source, the original Class::FromIl2CppTypeEnum type-code lookup now supplies only *already initialized il2cpp_defaults* primitive classes. Every returned primitive class must pass registration in original physical AOT assembly inventory, exact type-handle owner image, original TypeDef namespace/name, nongeneric zero arity and no declaring class or class generic container before a canonical owned TypeKey can be emitted. No new class/cache object is created, no original V1 getter/B1 first-event logic changed, and unsupported/absent primitive defaults or open VAR/MVAR fail closed. Added positive-only usedExistingPrimitiveDefault/admittedPrimitiveArguments diagnostic fields which are zeroed on any source rejection; prior Unicode/composite, registered AOT owner, first-error/registry/R02 and initial metadata Reader fences persist.

- [Final actual native .inl source/mock CI 43139433481](https://github.com/night-outlook/il2cpp_plus/actions/runs/43139433481): **4/4 completed/success**, Mac/Linux × C++11/C++17, Release/Debug × strict/ASan-UBSan, 16 mock host executions × **67 scenarios / 1195 assertions per process**, no Unity VM metadata. The real original Class.cpp primitive switch is source-pinned, but the test uses a fake pre-existing class with actual inactive .inl.
- [Final four-repository source/ABI admission 43139844512](https://github.com/night-outlook/hybridclr_demo/actions/runs/43139844512): **2/2 completed/success**, Mac/Linux, 21 negative/admission Python tests per OS and exactly 41 original native + four demo source blobs, with accepted result **PassedInactiveSourceOnly_NotFullV2** and all Local/full product acceptance flags false.
- [Implementation, design and independent source findings](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md), [B2 design/plan](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md). Prior [original Unicode](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md) and composite source paths remain documented with their original evidence attribution and limitations.

**Not performed:** official Unity2022.3 full Class.cpp/AssemblyShadow.cpp compilation, GameAssembly link or new actual Player, native type metadata/GC lifecycle proof, complete field15 parity, terminal-safe full general field14, authenticated binary/envelope/receipt V2, coherent whole-VM epoch or full R03 acceptance. Historic independent R03 **FAIL** and both High IR-R03-01/02 findings remain open; PureInterpreter disabled.

### Remaining Primary-owned work (NOT Local implementation)

1. Prove **complete original V1 nonempty execution field15 byte/semantic parity** with authoritative real TypeDefs/classes and a valid metadata/class source ownership and generation model, covering empty/nonempty, baseline/active/error19/guard15, Unicode nested generic/array/qualified and existing primitive default plus rejected unsupported types. Primitive Class::FromIl2CppTypeEnum can be source-matched without class creation; that does not establish actual Unity instance parity.
2. Prove terminal-safe **full** original finalDiagnostics field14 and finalExecutionDiagnostics field15 with correct cctor/static values, teardown/GC/metadata lifetime, bounded no-new-allocation constraints. Original field14/15 cannot be replaced by a partial primitive/first-error record or fabricated null. Whole VM epoch remains B3/not proven.
3. Integrate original bounded V2 binary codec and descriptor-relative POSIX artifact/envelope transaction into a source/lifetime-authenticated, one-owner, one-use native emission path, plus independent identity/fixture/build/PID/source/receipt/readback and fail-closed torn-write, symlink, duplicate, race and postterminal tests. Preserve original V1/B1 and consumed evidence.
4. Independently review implementation+source+host CI, lock exact four latest pushed Git commits, then issue new **explicit executable** WEB_TO_LOCAL with fresh owner-only absent roots and exact Local command, expected results, evidence and permitted bounded fixes. Never transfer nontrivial Primary architecture changes to Local.

### Future single-batch Local Validation matrix (conditional, NOT runnable)

When Primary explicitly reopens this gate, make **one** immutable four-SHA source batch yield as many independent answers as possible with **one** official Unity 2022.3.62f2 macOS arm64 IL2CPP build and **three** distinct fresh Players:

| Batch step | Combined questions | Expected independent raw evidence |
| --- | --- | --- |
| 0. Admission | Four clean exact SHA local checkouts, 41/4 Git source gate and dual-OS CI completion, official Unity/SDK source and Original S custody, two spaced disk-capacity samples, strictly absent 0700 owner-only roots | Git remotes/branch/commit/blob/clean-tree, external SDK/Unity, environment/capacity, original-S/custody and admitted-root receipts |
| 1. Native build/link | Original Class.cpp default-switch and true Il2CppClass metadata ABI; C++11 Bee compilation of actual installed VM source, generated method bridge, type and symbol roster; no host fake classes/global allocator definitions in GameAssembly | Compiler/Bee logs, installed source and generated code hashes, BuildReport, GameAssembly UUID/SHA, exact nm exported symbols and allocator exclusion |
| 2. Positive controls | No-classes baseline Empty; initializer error19 and captured generic guard15; physical TypeDef owners, nested/qualified/Unicode keys and **real preinitialized primitive default class** metadata, complete original V1 semantics and first-error reason equality | Three fresh PID/nonce/case/request/fixture identities, original full V1 field14/field15 bytes, native B1 reason/canary, physical TypeDef/primitive source tracing |
| 3. Native V2 | Full, terminal-safe native fields14/15 with actual source timing/GC boundaries, descriptor-relative exclusive artifact-first/envelope-last transaction, independent receipt binding | raw diagnostics.v2.bin, envelope.v2.json, external receipt, inode/device/owner/size/SHA, strict decoder/readback/identity join |
| 4. Adversarial | Missing/ambiguous/unregistered primitive, mismatched class names, nonzero primitive generic container, stale class/source/owner, Unicode invalidity, postterminal attempt, duplicate finalize, symlink/partial receipt | Typed fail-closed error, no partial source/false acceptance, unchanged first error and AOT canary, original ownership/counter fences |
| 5. Stability/perf/custody | Real GC/RSS/first-call, replay isolation, crash-free startup/shutdown, source/SDK/ABI and final regular-only raw product seal; two independent verification routes | Player/system logs, GC/RSS/perf traces, product/host provenance receipts and independent signed/hashed source/evidence manifest |

No new oneuse-13 is reserved; no executable Local runner/root/nonce exists; prior oneuse-12 is consumed and cannot be replayed. Local owns real runtime observation only when authorized; any nontrivial issue belongs in RETURN_TO_WEB.md and Primary will implement the change.

**Current flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION. No Human Review Gate approval, H2/M08A/X02/SNAP-01. Local response while closed: **NoExecutionAuthority**.

**Next agent read order:** Docs/AssemblyShadow/README.md, Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md, B2_PREEXISTING_PRIMITIVE_DEFAULT_IMPLEMENTATION_AND_REVIEW.md, exact b2_definition_native_candidate.json, then Local-owned LOCAL_VALIDATION.md and RETURN_TO_WEB.md only for historical context. Stop after read-only inspection; do not start a build/Player.

---

## Current Primary B2 Unicode physical TypeKey checkpoint — NO LOCAL EXECUTION (2026-11-11 UTC)

**Authority: CLOSED / NO EXECUTION. Local response: NoExecutionAuthority.** This is an inactive native-source development checkpoint, not approval of a new Player build, test cycle, root name or Local architecture fix. Do not replay consumed oneuse-12, invent oneuse-13, overwrite raw evidence, start Unity, or enter H2/M08A/X02/SNAP-01.

### Exact current remote source tuples

All repositories: branch codex/assembly-shadow-r01b-h1, canonical HTTPS origin https://github.com/night-outlook/<repo>.git.

| Repository | Expected default local checkout (not inspected here) | Latest source pin |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | latest pushed GitHub branch HEAD, verify; this handoff document changes its commit |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | db5354a9befd5cfd02f907d3169c8106e0a29305 |

[Exact 38-native/4-demo manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) authenticates actual source, ABI, CI and reference Unicode table Git blobs. Four-repository branch/HEAD/state verification is mandatory for any future authorized batch. These listed default paths are not a claim of Local worktree inspection. Native/SDK platform preparation remains Unity 2022.3.62f2 macOS ARM64 IL2CPP ON Release/diagnostics2, C++11 real Bee mode, isolated R03 Player, the original pinned HybridCLR runtime and package source. Actual future generated code, Unity SDK overlay, GameAssembly build UUID/hash, PIDs, requests/fixtures and native symbols must be read from **one new real build**, not reconstructed or reused.

### Primary source, tests, diagnostic and review completed

The inactive observed physical AOT TypeDef producer now computes canonical assembly TypeKey bytes through the **original** AssemblyShadowName::ViewName, NameHash and NextFolded (Unity's UTF16-to-lower table) within its original metadata lock and first-session Reader. C++11 owned builder converts folded UTF16 to fixed-budget UTF8 with byte-length prefix, validates surrogate pairs, rejects malformed/budget-exceeded source, and revokes receipt/rows/record on failure. Prior independently owner-verified registered AOT TypeDef generic argument images, nested GENERICINST/PTR/SZARRAY/ARRAY/qualified keys, registry/R02/first-event fences and original serializer remain. The legacy V1 getter and native B1 first-error producer were not modified. Receipt.usedUnicodeAssemblyFold is positive-only.

- [Native actual .inl source-mock CI 43011988073](https://github.com/night-outlook/il2cpp_plus/actions/runs/43011988073): 55 typed source/mock cases and 924 assertions per host process; Ubuntu C++11/17 strict/sanitized Release/Debug jobs completed/success, macOS queued at initial checkpoint. Recheck job-level final status.
- [Pure Unicode folded key host CI 43011964681](https://github.com/night-outlook/il2cpp_plus/actions/runs/43011964681): owned UTF8/surrogate/no-allocation negatives; Ubuntu C++11/17 success, macOS pending initially.
- [Original Name.h and Unicode tables reference host CI 43012431935](https://github.com/night-outlook/il2cpp_plus/actions/runs/43012431935): actual original Name.h and unchanged char-conversions.cpp data + pinned lower-table lookup, but test-only ABI and no Unity/full original TypeKey TU; Ubuntu C++11/17 PASS, Mac pending initially.
- [Four-fork exact 38-native/four-demo source audit](https://github.com/night-outlook/hybridclr_demo/actions/workflows/r03-ir-b2-definition-four-pin-source.yml): strictly source-only; checks 20 negative/admission tests per OS, exact clean roots, demo/native Git blobs and immutable false acceptance flags; check exact final run and OS job status before any claim.
- [New source design and independent review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md); [prior composite review and eventual single-batch matrix](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md).

**No Unity native full TU/GameAssembly/real Player/GC/metadata teardown source tests or native V2 full-field/file/receipt have executed on this candidate.** Historical B1 oneuse-12 focused real Player 19/19 PASS is not new B2 evidence or reusable authority.

### Remaining nontrivial Primary blockers — NOT Local tasks

1. Original primitive/default-enum execution TypeKeys need source identity proof without making new classes or cache population; original FormatMetadataOnly deliberately rejects VAR/MVAR with image map. Prove real full V1 nonempty field15 byte/semantic equality on official metadata before claiming an unrestricted source.
2. Prove complete, source-owned, terminal-safe original finalDiagnostics (field14) and finalExecutionDiagnostics (field15) under valid VM metadata/class/GC lifetime, including cctor/static-value sampling; retain wholeVmEpoch=NotProven absent B3 proof. B1 first error or partial class rows cannot substitute for these full fields.
3. Integrate already host-tested bounded native V2 serializer plus descriptor-relative POSIX transaction with one owner/preopening, authenticated source + external receipt and independent recovery reader. Add torn-write, symlink, duplicate/replay, source-race, invalid Unicode, postterminal and missing-provenance negative tests.
4. Independent review and exact four-SHA source/CI admission; ONLY THEN issue a new one-use Local batch with verified fresh absent roots, precise commands and expected evidence. No large local fixes.

### Future single-batch Local validation (CONDITIONAL; do not execute now)

After new Primary authorization, group all high-cost questions into a **single** exact-source Unity build and three fresh Player executions, with no mixing of historical roots:

| Checkpoint | Combined tests | Source-bound raw evidence |
| --- | --- | --- |
| 0. Admission | Four clean pinned Git roots; 38/4 source gate, two genuine spaced free-capacity checks, official Unity2022.3.62f2/SDK/original-S archive/owner-only absent roots and CI OS completion | commit and blob manifest, source admission, OS/SDK/Bee, storage/custody receipts |
| 1. Build/link | One real C++11 Unity IL2CPP build; generated bridge table and linked GameAssembly code, no host-only allocator symbols; original actual Unity VmStringUtils casefold and type metadata ABI | BuildReport, Bee command, full source install and symbols roster, GameAssembly UUID/SHA and generated C++ hashes |
| 2. Positive controls | Empty, native initializer error19, captured generic guard15, **Unicode assembly names** (Latin, Greek, supplementary, path/version) and nested/array/qualifier type keys with genuine physical AOT metadata; original full V1 class JSON and B1 first reason equality | three distinct Player PIDs/nonces/requests/fixtures, original V1 full byte fields and native B1, authenticated physical owner/type-key comparison |
| 3. Native V2 | Complete terminal field14/15, preopened and bounded artifact-first/envelope-last binary and external identity receipt; strict independent V2 reader | raw binary/envelope/receipt, source/PID/UUID, device/inode/size/SHA, external verification |
| 4. Negative and lifetime | Invalid Unicode, unowned/ambiguous/stale metadata, B1-first failure during source capture, no postterminal AOT, teardown/GC races, duplicate finalize, symlinks, partial receipt | typed errors, preserved first event, clean AOT canary, no partial success, crash/GC/RSS/symbol traces |
| 5. Integrity/performance | Repeatable baseline GC/RSS/first-call and independent evidence seals, original-S/static provenance preserved, regular-only product archive | immutable product+host raw manifests, two independent auditors, local run result and RETURN_TO_WEB findings |

No fresh one-use labels or executable commands are approved. Local may inspect read-only instructions only; do not invent a locally runnable entry. For future actual execution, Local maintains LOCAL_VALIDATION.md and RETURN_TO_WEB.md; Primary retains all nontrivial fixes and must produce the next committed WEB_TO_LOCAL.md.

**Product flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION. Original R03 independent full-stage FAIL, High IR-R03-01/02 and original strict custody remain unresolved. PureInterpreter disabled.

**Read order:** Docs/AssemblyShadow/README.md → Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md → B2_ORIGINAL_UNICODE_ASSEMBLY_FOLD_IMPLEMENTATION_AND_REVIEW.md → exact candidate manifest → LOCAL_VALIDATION.md and RETURN_TO_WEB.md for historical Local evidence. Until explicit new authority, Local responds NoExecutionAuthority.

---

## Current Primary candidate — composite physical AOT TypeKeys; LOCAL NOT AUTHORIZED (2026-11-11 UTC)

**Authority: CLOSED / NO EXECUTION.** This is a committed Primary-owned implementation checkpoint and a **conditional future single-batch validation design**, not a runnable Local Validation order. Any Local Agent presented with this source must report NoExecutionAuthority, without running Unity, Player, build scripts, native linker or any new one-use cycle. Local must not implement missing field source, build transport, or repair architectural gaps. Do not infer oneuse-13 or reuse the consumed oneuse-12 output roots.

### Identity and exact source/branch pins

All canonical remotes resolve to https://github.com/night-outlook/<repo>.git; use existing verified access through GitHub Connector and verify current branches independently. Worktree paths below are the project **default expected** Mac layout, NOT a claim that this web environment inspected the local machine. Local must check each actual git remote/branch/HEAD and record any different absolute worktree root before use.

| Repository | Default local path | Branch | Current authoritative pin |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/hybridclr_demo | codex/assembly-shadow-r01b-h1 | latest pushed branch HEAD from GitHub, verify before any subsequent authorization |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/il2cpp_plus | codex/assembly-shadow-r01b-h1 | 272f3077eee50835284e27855352fe300362ad79 |

The exact **26 native + four demo** implementation, source ABI and CI Git blobs are in [the source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json). Git branch HEAD at the time of executing is authoritative for hybridclr_demo because this document itself changes that Git SHA; the final chat handoff may supply a fixed four-SHA tuple only after its final remote readback.

**Native/package/build pins:** Unity 2022.3.62f2 macOS ARM64; IL2CPP ON, Release diagnostics2 in isolated R03 Player; C++11 compile environment as evidenced by consumed oneuse-12; HybridCLR interpreter source 4b2774...; HybridCLR Unity package 948c0e...; native IL2CPP fork 272f3077...; generated method bridge and GameAssembly binaries must be hashed from the actual future Unity build and may not be invented or reused. The original immutable B1 oneuse-12 real Player executed against a **different** exact native source at 8aa8d093... and demo 2d690bb2...; do not call its result current B2 verification.

### Primary implementation completed and test receipts

The inactive native source now formats bounded composite original TypeKeys from independently authenticated physical AOT TypeDef leaves: simple/nested definitions, nested constructed GENERICINST, PTR, SZARRAY, ranked ARRAY sizes/bounds and original native qualifiers. It retains original V1 getters and B1 first-error producer, all registered physical AOT image and class-witness provenance, reader/lock/registry/R02/B1 source fences, registry-slot-order output and fail-closed source revocation. Added source receipt flags report supported shape observations but cannot claim a whole-VM epoch. Max 4,096 bytes/key, eight composite levels, 16 args/instantiation, 32 entries/array dimension-list, 65,536 owner lookups, 1,024 registered AOT image owners, 64 observed images, 8,192 TypeDefs/image.

- [Pure C++11/17 composite host CI 42992930075](https://github.com/night-outlook/il2cpp_plus/actions/runs/42992930075): 4/4 completed/success, Mac/Linux release/debug strict/sanitized; standalone allocator exclusion.
- [Actual new native .inl source-mock CI 42993897217](https://github.com/night-outlook/il2cpp_plus/actions/runs/42993897217): 4/4 completed/success, 50 typed mock scenarios per process, Mac/Linux C++11/C++17. This is **mocked VM**, not official Unity compilation.
- [Four-fork 26 native/4 demo source audit 42994963528](https://github.com/night-outlook/hybridclr_demo/actions/runs/42994963528): 2/2 completed/success; 18 source/admission negative tests per OS; all full V2 and human approval flags remain false.
- [Independent source review and conditional matrix](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md). [Current plan](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md).

The only acceptable machine disposition for these tests is PassedInactiveSourceOnly_NotFullV2. Neither Unity GameAssembly, real Player, complete field14/15, source/GC/terminal metadata lifetime, V2 file/envelope or first externally authenticated recovery has been tested for this candidate. The old B1 oneuse-12 19/19 focused PASS is historical and consumed, not an acceptance elevation.

### Remaining Primary-owned blockers; no Local fixes permitted

1. Complete original canonical primitive, generic parameter VAR/MVAR/declaring-method and Unicode assembly folding metadata sources; prove byte/semantic identity against real original V1 execution in class-empty, nonempty, nested, array, generic and pointer/qualifier cases.
2. Complete terminal-safe **full** field14 finalDiagnostics and field15 finalExecutionDiagnostics with approved metadata/class/GC lifetime and source epoch, or formally review a separately versioned reduced schema. The current wire field14/15 contract explicitly forbids substituting a B1 first-error, null, or partial class-only source.
3. Integrate a single-owner no-reentry bounded native V2 encoder and descriptor-relative POSIX artifact/envelope transaction, externally verified identity receipt and independent strict reader; negative symlink/path, torn-write, duplicate, race and end-of-lifetime tests.
4. Complete independent source review and source-pin/CI gate across all four repos, then publish new **fresh exact-four-SHA** authorization and new absent one-use output roots, host/SDK/capacity/custody admission, actual command and expected evidence.

These are nontrivial Primary Implementation changes. Do not hand them to Local Validation. Original independent full R03 review FAIL, High IR-R03-01/02, original-S strict custody Blocked and B3 whole-VM epoch/GC/RSS/RC/P/E remain open.

### Future single-batch Local Validation — run only after reopening this gate

A single eventual locally approved run shall use one exact Git tuple, one official Unity build, three fresh independent Players and separately sealed host/native evidence, with no prior root reuse. Group the following investigations so one run answers as many independent issues as practical:

| Group | Explicit precondition / test | Evidence to retain |
| --- | --- | --- |
| 0. Admission | All four clean exact commits, source manifest negative gate, official Unity2022.3.62f2/SDK, archived Original S, two fresh >=60s capacity samples and approved absent owner-only roots | Branch/sha/clean-tree receipts, environment, source audit, capacity, original-S custody and root provenance |
| 1. Real compiler/link | Exact Unity C++11 Bee build, VM overlay file roster, generated method bridge, source/blob/input hashes, post-link global new/delete exclusion | Compiler/link logs, BuildReport, source hashes, GameAssembly UUID/hash, nm symbol table, generated table |
| 2. Three positive Players | Baseline Empty 0, initializer failure19 native origin2, captured generic guard15 origin1, exact V1 and native B1 reason equality, real TypeDef source and nonempty canonical TypeKeys | Distinct PID/nonce/request, build/fixture identities, literal full V1 field14+field15 before terminal and frozen full V2 after event, strict equality and class/owner traces |
| 3. Native V2 custody | Complete field14+15 immutable sources, artifact-first/envelope-last descriptor relative exclusive writes, independently bound identity and first recovery | binary and JSON artifact raw bytes, source owner/size/SHA, dev/inode/fd, independently authenticated receipt and strict reader result |
| 4. Negative/adversarial | Source epoch/registry/counter drift, ambiguous owner, unsupported class shape, over budget, postterminal, symlink and torn artifact, duplicate finalize or conflicting nonce | Typed fail-closed diagnostics, unchanged first event, rejection receipts, no false product seal |
| 5. Cross checks and stability | metadata Reader teardown, repeated fresh startup/shutdown, GC/RSS/perf/first call, independent product seal and provenance consistency | OS crash/Player logs, GC/RSS/perf samples, unchanged AOT canary, independent product manifest and local report |

No batch runner is currently approved; no exact new output directory or one-use label has been reserved. These requirements are **planning**, not authorization. Fresh resource and source verification must be re-evaluated when Primary issues new authorized handoff. Subsequent unblocked Local Agent must do bounded, locally closed-loop modifications only; substantive findings go into RETURN_TO_WEB.md and are fixed here in Primary.

**Current product flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven. PureInterpreter disabled; no H2/M08A/X02/SNAP-01 or Human Review Gate self-approval.

**Next agent read order (even if only read-only):** Docs/AssemblyShadow/README.md → Handoff/WEB_TO_LOCAL.md → B2_COMPOSITE_TYPEKEY_IMPLEMENTATION_AND_REVIEW.md → candidate manifest → Handoff/LOCAL_VALIDATION.md and RETURN_TO_WEB.md for history. While gate remains closed: Local response exactly NoExecutionAuthority; do not perform any new executable Local Validation action.

---

## Current B2 source — registered AOT images including empty assemblies (2026-11-11 UTC)

**Local Validation is NOT authorized.** The exact native source on `codex/assembly-shadow-r01b-h1` is now `night-outlook/il2cpp_plus@8627a93f4f307c8d2c99e7edada54573a93cc312`, with fixed `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de` and current `hybridclr_demo` branch HEAD to be read from GitHub. The [exact 23-native/3-demo source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) pins all relevant implementation/ABI/CI Git blobs.

The inactive native code can now authenticate concrete TypeDef generic arguments from an originally registered physical AOT assembly even when it has no observed class. The original `Assembly.cpp::s_Assemblies` is visited under `s_assemblyLock` while the caller holds `g_MetadataLock` and initial-session Reader; bounded registry-owner sets are compared before/after the actual observed-class source capture. **Registered AOT assemblies with zero TypeDefs are skipped**, not falsely rejected; invalid source, missing/ambiguous ownership, changing registry and capacity exceedance still fail closed. The producer remains inactive and does not claim a coherent VM epoch or full V1 field15 semantics.

[Final native source-mock CI 42988174617](https://github.com/night-outlook/il2cpp_plus/actions/runs/42988174617) **4/4 PASS**, Mac/Linux C++11/17 × Release/Debug × strict/ASan-UBSan, **16 host processes / 672 scenario executions / 7,776 assertions**, no reported sanitizer errors. [Final exact-source CI 42988434479](https://github.com/night-outlook/hybridclr_demo/actions/runs/42988434479) **2/2 PASS**, 23 native source blobs, three pure demo counterparts, **16 fail-closed contract tests per OS**, exact four-fork pins, and explicit negative readiness. [Source review, legacy evidence, risks and rollback](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_REGISTERED_AOT_OWNER_IMPLEMENTATION.md). These are **mock/source tests, not official Unity/IL2CPP C++ compilation, GameAssembly, Player, runtime shutdown or V2 first recovery**.

**Current product flags:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`. Original consumed oneuse-12 remains focused B1 real Player 19/19 PASS only; PureInterpreter disabled. The next Primary stage is complete canonical type/real V1 field15 parity, terminal-safe complete field14/15 sources, authenticated native V2 descriptor writer and independent evidence. Do not replay oneuse-12, invent oneuse-13, launch a Local build, or begin H2/M08A/X02/SNAP-01. Local must respond `NoExecutionAuthority`.

---

## Current Primary checkpoint — registered AOT images without observed classes (2026-11-11 UTC)

**No Local execution is authorized.** The source-only B2 native candidate on `codex/assembly-shadow-r01b-h1` is `night-outlook/il2cpp_plus@f08cb329fb19eaa47eaa8075e62dbc3f2d42cf8a`, with unchanged `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. Read the current demo remote HEAD, [23-native/3-demo source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) and [Primary implementation review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_REGISTERED_AOT_OWNER_IMPLEMENTATION.md) for the exact content; none is a new executable handoff.

**Implementation:** The inactive `TryCaptureBoundedDefinitionExecutionLive` can resolve a concrete `GENERICINST` TypeDef argument from an **unobserved but originally registered physical AOT assembly**. Its new `Assembly::TryVisitRegisteredAotImages` traverses raw `s_Assemblies` under `s_assemblyLock`; the enclosing capture holds `g_MetadataLock` and the initial metadata Reader. Two bounded AOT registry visits bracket the two physical class enumerations. TypeDef ownership must be proven from the registered AOT inventory **before dereference**. The scanner excludes invalid tokens and interpreter images; 1,024 registered image/64 observed image/65,536 TypeDef handle-lookup limits are enforced, and incorrect/ambiguous/changed inventories invalidate output. No original V1 getter or B1 producer changed. The registry comparison is only observational, not a coherent VM epoch or lifetime guarantee.

**Source tests:** [Exact native host mock run 42986790417](https://github.com/night-outlook/il2cpp_plus/actions/runs/42986790417): **4/4 PASS** on Mac/Linux × C++11/17, Release/Debug × strict/ASan-UBSan, **16 mock processes / 656 scenarios / 7,408 assertions**, no reported sanitizer errors. [Exact 23-native/3-demo source audit 42987239404](https://github.com/night-outlook/hybridclr_demo/actions/runs/42987239404): **2/2 PASS**, including the real Assembly.cpp implementation and original metadata/TypeKey/OS lock sources, 15 contract-test functions per platform, explicit false acceptance flags. The first new CI failed at a C++11 sink initialization, fixed and rerun under the final SHA. **No official Unity 2022.3.62f2 source/full TU, GameAssembly, real Player, GC or postterminal V2 work ran.**

**Still blocked:** complete original V1 `finalExecutionDiagnostics` class/TypeKey byte parity and terminal-safe source lifetime, full `finalDiagnostics`/field14, full execution field15, authenticated descriptor-relative native V2 artifact/envelope/receipt, coherent VM epoch and historic original-S evidence. `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven`. PureInterpreter disabled.

**Local Agent response: `NoExecutionAuthority`.** Do not rerun consumed oneuse-12, infer oneuse-13, start a fresh Player/Unity build, or begin H2/M08A/X02/SNAP-01. Primary owns the remaining code and subsequent independent review; there is no approved command or output root.

---

## Latest Primary source checkpoint — cross-image observed AOT TypeDefs, no execution (2026-11-11 UTC)

**No Local Validation execution authority exists.** The current native fork on `codex/assembly-shadow-r01b-h1` is `night-outlook/il2cpp_plus@cfb33d58432b05f3d28052dfb88677a0561f6c93`; `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de` are unchanged. The current `hybridclr_demo` source and documents are committed on this branch; verify its current HEAD rather than using a chat-derived SHA. [Exact pinned 20-native/3-demo source roster](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) and [Primary cross-image review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_BOUNDED_CROSS_IMAGE_AOT_OWNER_IMPLEMENTATION.md) describe this inactive subset.

The new `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` source performs **two** physical enumeration passes under one metadata lock and initial-session lifetime Reader. Its 64-image inventory admits only images of independently matched observed class identities. Thus it can now format generic arguments from a *different* physical AOT image only if that image also contains a physically matched observed class. Missing/ambiguous owners, interpreter images, lost second-pass identities, unsupported nested/generic shapes or budget exhaustion invalidate the output. This is not an exhaustive image inventory, not postterminal `finalExecutionDiagnostics`, not full `finalDiagnostics`, not a coherent VM snapshot and not V2 file transport.

**Exact scoped evidence:** [Native `.inl` mock CI 42983247910](https://github.com/night-outlook/il2cpp_plus/actions/runs/42983247910) **4/4 completed/success** at the native source `cfb33d...`: Mac/Linux × C++11/17 × Release/Debug × strict/ASan-UBSan, **16 mock processes, 37 scenarios per process, 396 assertions per process** (592 scenario executions and 6,336 assertions), no reported sanitizer errors. [Four-fork exact source-gate CI 42983166781](https://github.com/night-outlook/hybridclr_demo/actions/runs/42983166781) **2/2 completed/success** at that native source with 20 source blobs and three demo mirrors. Tests use **mock metadata/VM classes**, not real Unity 2022.3.62f2 or linked GameAssembly. The only source-admission result is `PassedInactiveSourceOnly_NotFullV2`, with `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false` and all runtime/R03/H2/Human Review Gate flags false.

**Next Primary-owned tasks:** prove full physical AOT ownership of argument images without matched observed classes; complete composite canonical TypeKey coverage and actual V1 field15 byte parity with real metadata lifetime/teardown; build terminal-safe full general field14 and execution field15 sources, then identity-bound descriptor V2 writer/envelope/independent receipt and comprehensive source review. **Do not rerun consumed oneuse-12, fabricate oneuse-13, reuse its roots, or begin H2/M08A/X02/SNAP-01.** The Local response is `NoExecutionAuthority`; there is no executable command, fresh root or approved batch.

---

## Current Primary-only B2 constructed TypeKey checkpoint — NO LOCAL EXECUTION (2026-11-11 UTC)

**Execution authority remains CLOSED.** The new exact native candidate on branch `codex/assembly-shadow-r01b-h1` is `night-outlook/il2cpp_plus@20a57e58098e3476dad5459f04f9fc730c3848c1`. The unchanged interpreter and package are `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The latest `night-outlook/hybridclr_demo` HEAD must be verified from the GitHub Connector; all changes are Git-published, with exact native source and three pure-demo counterparts in [the source manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json).

The inactive `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` now supports **one additional restricted canonical TypeKey case**: `GENERICINST` with a same-image verified physical AOT generic **definition** and 1–16 separately verified physical AOT concrete `CLASS/VALUETYPE` TypeDef arguments, including nested definition ancestry. The source uses original metadata lock and initial-session Reader, copies all class primitives into immutable bounded rows and retains the genuine frozen execution/R02 schema. Cross-image, constructed argument, array/pointer, open variable, qualified, non-ASCII assembly-folding and postterminal cases explicitly fail closed. A native B1 first error still precludes accepting stale source. The existing V1 getters/first-error producers and previous oneuse-12 evidence are unchanged.

[New Primary review and strict source/test limitations](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_SAME_IMAGE_GENERICINST_IMPLEMENTATION_AND_REVIEW.md). [Pure constructed-key CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/42978349307): **4/4 success**, 8 host processes/624 assertions, zero protected allocations. [Exact native `.inl` mock CI](https://github.com/night-outlook/il2cpp_plus/actions/runs/42979860514): **4/4 success**, Mac/Linux C++11/17 × Release/Debug × strict/sanitized, **16 mock processes / 496 scenarios / 3,888 assertions**. [Cross-repository source audit](https://github.com/night-outlook/hybridclr_demo/actions/runs/42980498037): **2/2 success**, exact 15 native file blobs including real generic ABI + unchanged canonical TypeKey grammar, three independent demo pure-source blobs, all four verified branch pins, and false acceptance/handoff flags. These are **source/mock tests, NOT official Unity SDK/Player/GC results**. The only legitimate status is `PassedInactiveSourceOnly_NotFullV2`; `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `wholeVmEpoch=NotProven`.

**Next Primary-owned task:** complete physical cross-image canonical type ownership and remaining generic/array/qualified TypeKey cases, real V1/field15 semantic parity, terminal-safe field14 and full field15 sources, descriptor-relative native V2 writer/receipt and independent source review. Do not infer a Local oneuse-13 or rerun consumed oneuse-12. There is **no runnable Local command, fresh output root, or authorized batch**. A Local Agent must respond `NoExecutionAuthority`, not run Unity.

---

## Latest B2 restricted native source checkpoint — Primary only (2026-11-11 UTC)

**No new Local Validation is authorized.** The next native candidate on branch `codex/assembly-shadow-r01b-h1` is now **`night-outlook/il2cpp_plus@4c900ab22735768f517d81daccfed31a3d9aeb1e`**, with fixed `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. The current demo HEAD must be read from GitHub when a subsequent handoff is authorized. [Exact ten-native-blob candidate manifest](../../Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json) and [latest Primary review](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_PHYSICAL_DEFINITION_LIVE_IMPLEMENTATION.md) are **not** a new oneuse-12 execution source or a real Player acceptance record.

The **inactive** `AssemblyShadow::TryCaptureBoundedDefinitionExecutionLive` source now restricts actual physical metadata capture to admissible AOT TypeDef definitions, including same-image verified nested definitions and generic **definition** arity. It admits the initial-session metadata Reader, uses the original registry/witness and physical first-match enumerator under `g_MetadataLock`, copies source values into owned rows and formats through the unchanged native frozen execution/R02 record. It verifies original registry-slot order even when two physical callbacks arrive reversed; checks originating B1 Empty at entry, after collection, and after formatting; rejects staged declaring and generic-container indices, foreign/recursive ancestry, incomplete membership, changed R02/revision and stale lifetime epochs. It still **cannot** serialize arbitrary constructed generic, qualified, array/pointer or Unicode-folded TypeKeys; it is not terminal-safe complete `finalExecutionDiagnostics`, not full `finalDiagnostics`, and not an integrated V2 writer.

**Prior source-exact evidence:** [native `.inl` mock CI 42974759134](https://github.com/night-outlook/il2cpp_plus/actions/runs/42974759134) **4/4 PASS at predecessor native `fd1bc0...`**, Mac/Linux × C++11/17 × Release/Debug × strict/ASan-UBSan: 16 mock host processes, **320 scenario executions and 2,528 assertions**, with no reported sanitizer errors. It used **mocked VM types**, NOT the official Unity SDK. [Earlier source admission 42975024429](https://github.com/night-outlook/hybridclr_demo/actions/runs/42975024429) **2/2 PASS at predecessor source**, not at current final ten-native-blob manifest.

**Final-source prerequisite status at this checkpoint (2026-11-11 UTC):** The current native `4c900ab...` adds the actual `GlobalMetadataFileInternals.h` include needed to define `Il2CppTypeDefinition` in the production TU and tightens the 20-case Release/Debug test gate. [Native CI 42975604704](https://github.com/night-outlook/il2cpp_plus/actions/runs/42975604704) is now **4/4 completed/success**, including macOS and Ubuntu C++11/17 with Release/Debug strict/sanitized; [ten-native-blob cross-repo CI 42976195767](https://github.com/night-outlook/hybridclr_demo/actions/runs/42976195767) had Ubuntu **Passed**, macOS **Queued**. The native mock-source matrix is fully green; the ten-blob cross-repository final-source matrix has **not yet earned a completed dual-OS verdict**. Re-read their actual statuses; do not inherit earlier successful conclusions across changed Git SHAs. Regardless of future source-gate status, the truthful product result remains `PassedInactiveSourceOnly_NotFullV2`, `readyForNativeV2FieldCapture=false`, `nativeV2TransportImplemented=false`, and all R03/H2/HumanReview flags false.

**Next Primary-owned work:** complete full canonical execution TypeKeys and actual nonempty class source parity against the original V1 output, establish metadata/teardown lifetime and postterminal admission, finish terminal-safe full general field14 capture and the authenticated descriptor-relative native V2 writer, and independently review all design/source/test/provenance. Only after those source gates are complete may Primary authorize a fresh, exact-four-SHA **new one-use** Local Validation run. **Do not replay oneuse-12, infer oneuse-13, or begin H2/M08A/X02/SNAP-01. Local response now is `NoExecutionAuthority`.**

---

Date: 2026-11-10 UTC. **No new Local Validation cycle is authorized by this document.**

## Consumed oneuse-12

The prior source-pinned **oneuse-12** handoff was executed **exactly once** at `night-outlook/hybridclr_demo@2d690bb2f7234ddcbee339f9da7125d687f5ed45`, with `night-outlook/il2cpp_plus@8aa8d09319a89b55b2496bcc2c69ccc69cb57be9` and unchanged `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`. It returned **focused PASS, 19/19**: one real Unity2022.3.62f2 macOS arm64 IL2CPP ON/Release build, three actual Players (PID 8760/8777/8787), native B1 0/0/0, 2/19/2 and 2/15/1 respectively, exact V1 first reason equality, linked allocator exclusion, distinct initializer verification receipts, external B2 host custody and independently checked regular-only **534-member** product seal.

Authoritative Local records:
1. [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) — empirical scope and raw provenance.
2. [RETURN_TO_WEB.md](RETURN_TO_WEB.md) — latest Local-to-Primary return and historical findings.
3. [Immutable oneuse-12 checkpoint](../History/M07R/R03/local-validation-native-b1-20261110-oneuse-12/README.md) — selected Git-published evidence; Local raw roots remain where recorded.
4. [Primary B1 reconciliation](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/PRIMARY_EVIDENCE_RECONCILIATION.md) — what was independently compared and what remains outside the scope.

The full **historical executable oneuse-12 instructions** remain recoverable only from the original immutable Git source commit `2d690bb2...` at this path. That command and its three root names are **consumed/retired**. Do not rerun it, reuse the oneuse-12 root names, delete/fix up historical raw data, or treat the evidence-publication commit as a new execution source.

## B2 exact-source admission (Primary only, NOT a Local handoff)

[Source-authenticated B2-0 audit](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_VM_SOURCE_READINESS_GATE.md) and [CI 42793741078](https://github.com/night-outlook/hybridclr_demo/actions/runs/42793741078) verify eight native VM source blobs and the original two-field V2 schema with 12 regression tests on both operating systems. This is an intentionally **negative readiness verdict**, with `readyForNativeV2FieldCapture=false`, because the bounded execution source rejects observed nonzero class rows and the original final diagnostics full-field lifetime cannot yet be established. **Do not turn a green source-audit job into authorization to build or run a Player.**

The next work remains with Primary Implementation: an actual VM-owned physical class/metadata TypeKey producer and full nonempty execution rows, postterminal full general source parity, exact source/metadata lifetime and authenticated native V2 descriptor writer. Source/CI prerequisites for a new Local batch are **not complete**, and no new output roots or command are authorized.

## B2 native execution-row staging (Primary-only host PASS, no Local execution)

Primary implemented pure bounded owned definition TypeKey bytes, an immutable nonempty class-row store and native bridges to the **unchanged real** `AssemblyShadowExecutionSerializer` and `AssemblyShadowFrozenExecutionRecord` with **synthetic** R02 source counters. The source is new under `Tools/AssemblyShadow/R03IR/NativeDiagnostics/`, NOT installed into the original Unity or libil2cpp VM. All four [native host CI workflows](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_OWNED_NONEMPTY_EXECUTION_IMPLEMENTATION.md) passed on Mac/Linux C++11/17, strict/sanitized: **16/16 jobs, 32 host executions, 2,520 assertions, zero protected allocations**.

This does **not** change the `readyForNativeV2FieldCapture=false` result. Restricted synthetic TypeKeys cannot establish physical Il2CppClass pointer provenance, original generic/array/unicode TypeKey coverage, postterminal metadata lifetime or full original `finalExecutionDiagnostics`/field15; neither have the full final general field14 sources been activated. **No Local Agent may build/run oneuse-12 again, invent a oneuse-13, or interpret host success as native Player V2 success.** The source owner is Primary Implementation; there is no new executable handoff.

## Primary-owned next work: B2 native V2 integration

Read [B2 implementation design/plan](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_IMPLEMENTATION_DESIGN_AND_PLAN.md) and the original [B-stage design](../History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md).

**Earliest incomplete source stage: B2-0 — exact complete `finalDiagnostics` (slot14) and `finalExecutionDiagnostics` (slot15) VM producers, healthy-time identity and metadata/class lifetime review.** The source-host compiler blocker was independently corrected: macOS/Ubuntu C++11/17 actual compiler and strict/sanitized codec/POSIX host tests now PASS 4/4 jobs each, 376 host tests total; see [exact RED→GREEN evidence](../History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/B2_CPP11_COMPATIBILITY_REMEDIATION.md). This is **not** Unity/Player source or full V2 acceptance. B2-1 through B2-4 remain Primary Implementation; complete producer semantics, integration code, strict tests, independent source review and a new final-source CI set must precede any future Local request. There is currently **no integrated B2 Player writer, no fresh output roots, and no authorized runner command**. A Local Agent must **stop with `NoExecutionAuthority`**, not infer or invent a runnable batch.

When B2 source implementation, independent review, diagnostics and final-source dual-OS gates are complete, Primary will replace this CLOSED page with an entirely new conditional handoff containing the current objective, verified four Git repository HEADs/branches, source/build pins, installed SDK, exact test command, new never-used output roots, fresh Mac/Original-S/custody/capacity admission, expected raw evidence, forbidden modifications and stopping point. Until then, no Local Validation action is required.

**Project acceptance remains unchanged:** `R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; wholeVmEpoch=NotProven`. PureInterpreter disabled. Original independent R03 FAIL, High `IR-R03-01/02`, original-S strict custody and missing compiler/object/link/Player provenance, full GC/RSS/RC/P/E remain open. Do not self-approve Human Review Gate or begin H2/M08A/X02/SNAP-01.
