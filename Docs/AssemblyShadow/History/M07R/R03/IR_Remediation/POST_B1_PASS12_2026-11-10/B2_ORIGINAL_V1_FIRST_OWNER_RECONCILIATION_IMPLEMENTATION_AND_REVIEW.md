# R03 B2 — original V1 physical image first-owner reconciliation

Date: 2026-11-12 UTC. Owner: Primary Implementation. Stage: **inactive, source-bounded admitted-TypeDef owner reconciliation.** This is not complete original execution field15, an atomic VM epoch, native V2 transport, Unity Player or an executable Local Validation order.

## 1. Independent source correction and fixed identities

All four canonical GitHub repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Reviewed source |
| --- | --- |
| `night-outlook/il2cpp_plus` | `648f3b2c5c0d0b86954c339ac3d75fdb96ce1ba2` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/hybridclr_demo` | Read latest pushed branch HEAD; this report and `WEB_TO_LOCAL.md` advance it |

The exact byte-pinned machine candidate `Tools/AssemblyShadow/R03IR/b2_definition_native_candidate.json` now has **57 native source/ABI/test/CI Git blobs and eight demo pure/reference source blobs**, including the unchanged original V1 `GetExecutionDiagnosticsJson` 5,222-byte source fixture. The demo contains source-identical mirrors of the two new pure V1 metadata visitor/join headers.

**Important correction to prior design terminology:** The original `Assembly::CaptureShadowEnumeration` does **not** use the `CopyLogicalAssemblies` remapping used by `GetAllAssemblies`. Its actual implementation holds `s_assemblyLock` and calls `CopyValidAssemblies(assemblies,s_Assemblies)`: it retains **every registered physical assembly with nonzero `assembly->token` in registration order**, including interpreter images and zero-TypeDef images. Original `AssemblyShadow::GetExecutionDiagnosticsJson` then inserts every physical TypeDef handle/image from those assemblies using `MetadataTypeImages.emplace(handle,image)`; the unordered-map `emplace` gives the **first encountered image** ownership of a duplicate handle. The original `AssemblyShadowTypeKey.cpp::MetadataDefinitionKey` uses that image map to choose both declaring TypeDef owner and assembly name.

The B2 bounded source previously visited only registered physical **AOT** images using `Assembly::TryVisitRegisteredAotImages`. Its owner proof was authentic within the AOT registry but did **not** establish the owner selected by original V1 if a valid earlier interpreter image advertised the same opaque handle. This is a concrete source-proven compatibility gap. The original V1 getter, public APIs, B1 first-error producer and HotUpdate/Shadow execution behavior are **unchanged**.

## 2. Implemented Primary changes

### A. Pure physical original-V1 image visitor and native adapter

- `libil2cpp/vm/AssemblyShadowOriginalV1ImageScan.h`: C++11 no-allocation visitor with the original `CopyValidAssemblies` token-valid physical eligibility/order. It deliberately retains interpreter and zero-TypeDef images, skips token-zero entries, and refuses missing/mismatched image/parent pointers. The new visitor itself retains no pointer.
- `libil2cpp/vm/Assembly.cpp` / `Assembly.h`: new **inactive** `Assembly::TryVisitOriginalV1ExecutionImages` invokes that pure visitor under the **original `s_assemblyLock`**, with a callback borrowing each image. Its caller must already hold the initial metadata Reader and `g_MetadataLock`. This code does not replace `CopyValidAssemblies`, `CaptureShadowEnumeration`, `GetAllAssemblies`, or modify original V1 semantics.
- `libil2cpp/vm/AssemblyShadowOriginalV1OwnerJoin.h`: C++11 pure, fixed-storage, no-alloc first-emplace owner comparison. For an opaque, already AOT-owner-authenticated TypeDef handle, walk the *original V1 image inventory* in original registration order and index each image’s TypeDefs with the original `MetadataCache::GetAssemblyTypeHandle`. The **first** image with the equal handle must be exactly the preauthenticated expected AOT image; a later duplicate cannot override it. No TypeDef is dereferenced until ownership is already established separately. Type counts, images and aggregate lookups are bounded. The helper has explicit negative `entireOriginalV1Field15Proven=false`, `coherentVmEpochProven=false`, `terminalSafe=false`, `runtimeAcceptance=false` flags.

### B. Actual native restricted physical TypeDef source

`AssemblyShadowBoundedDefinitionExecutionLiveSource.inl` still acquires an **initial metadata-lifetime Reader** and `g_MetadataLock`, binds observed classes to physical enumerator and registration witnesses, and first proves registered AOT physical image ownership. It now additionally:
1. Reads the **original token-valid all-image physical inventory** under the same metadata-lock scope via `Assembly::TryVisitOriginalV1ExecutionImages`. The capped inventory includes interpreter and zero-TypeDef images; oversize/malformed/all-images-over-cap fails closed.
2. For **every** admitted base TypeDef, declaring TypeDef, nested generic argument and default-primitive TypeDef handle, calls the pure `CheckFirstOwner` against that original image inventory after the existing AOT owner proof and before metadata TypeDef dereference. An interpreter-first handle conflict fails with `OriginalV1FirstOwnerConflict`; missing original owner with `OriginalV1OwnerMissing`; over-budget lookup with `OriginalV1LookupBudget`; missing or malformed original image source with `OriginalV1ImageSourceUnavailable`.
3. Repeats the original-V1 image visit after class traversal; identical ordered source image identities are mandatory. A changed second source fails `SourceChanged`. The registered AOT image visitor is independently sampled twice as before. The two passes are **observational fences only**, not a VM-wide epoch, metadata-content ABA proof or class static/cctor freeze.
4. Emits only source-subset receipt facts: original V1 token-valid image count, owner-handle match count, bounded original lookup count, original image order double-sample flag, and `originalV1FirstEmplaceOwnerMatched=true` **only after** successful rows/frozen record/registry/R02/B1 fences. Any later failure revokes all positive flags, owned rows and frozen record. `originalV1CompleteField15Parity` is **never set true**.

No borrowed image/class/TypeDef pointer escapes the synchronous metadata scope or is written into the immutable frozen execution JSON. The original Unicode folding, nested GENERICINST/PTR/SZARRAY/ARRAY/qualified TypeKey composer and assert-free 19-entry existing primitive default lookup remain unchanged, as do the original healthy-time V1 observational byte-parity probe and all original V1/B1 getters.

### C. Test, source-gate and docs

- `NativeHostTests/AssemblyShadowOriginalV1OwnerJoinHost.cpp` compiles **the actual two new pure source headers**, verifying interpreter-before-AOT conflict, interpreter-later duplicate first-wins, zero-TypeDef interpreter inclusion, token-zero skip, missing first owner, bounded lookup/typecount, malformed image, repeated image and no protected allocation.
- `NativeHostTests/AssemblyShadowBoundedDefinitionExecutionSourceMock.cpp` compiles the **actual native inactive source .inl** under synthetic VM types and visitor. It now tests six additional cases: interpreter-first conflict, interpreter-late alias success, zero-TypeDef interpreter inclusion, original image snapshot drift, deliberately corrupted synthetic V1 source omitting an AOT owner, and oversized interpreter image rejection.
- Native CI runs Mac/Linux C++11/C++17, Release/Debug and strict/ASan-UBSan. Source/mock results and pure visitor results are **not official Unity native translation unit compilation**.
- The demo source gate now checks the exact `CopyValidAssemblies`/original `CaptureShadowEnumeration` membership tokens, original V1 first-emplace image semantics, new pure headers and mirror equality, all original TypeKey/serializer/metadata/B1 source bytes, final 57+8 Git blobs, and negative flags. Its Python negative tests prohibit promoting admitted-owner subset to full field15, Unity ownership acceptance or a coherent epoch.

## 3. Exact observed host evidence

| Source-bound test | Actual result | Correct evidentiary scope |
| --- | --- | --- |
| [Native real .inl synthetic-VM host 43175217165](https://github.com/night-outlook/il2cpp_plus/actions/runs/43175217165) | **4/4 PASS** Mac/Linux C++11/17; 16 Release/Debug strict/sanitized processes, **73 native source cases × 1,673 assertions per process**, with 3 additional fake-original parity adapter and 20 existing default Peek cases | Real inactive `.inl` with synthetic VM owner/metadata/assembly; not real `Assembly.cpp` full TU or Unity Player |
| [Pure original-V1 first-emplace host 43174989182](https://github.com/night-outlook/il2cpp_plus/actions/runs/43174989182) | **4/4 PASS** Mac/Linux C++11/17; 16 Release/Debug strict/sanitized host executions, **12 cases/41 assertions per process**, zero guarded allocations | Tests the actual pure C++11 original-V1 visitor and owner join under fake images, not original VM registry lifetime |
| Final four-fork exact source gate | The latest green run at the final demo commit must be verified. The earlier [43175578270](https://github.com/night-outlook/hybridclr_demo/actions/runs/43175578270) was **2/2 PASS**, 57 native/8 demo blobs, 27 negative tests/OS | Exact source/manifest and false-acceptance admission only, no native Player or original real getter read |

The intermediate pure-host RED at run 43174875009 was caused by setting an assertion threshold above the host’s measured 41 assertions; the source tests themselves printed 12 passing cases/41 checks. CI was corrected and final 43174989182 passed 4/4. Prior source-gate RED was a stale old 53/6 source-count expectation; corrected to 57/8, with 27 tests/OS green. Preserve RED history, do not treat it as product evidence.

## 4. Independent source review and risks

**B2-V1MAP-01 — corrected original source identity (source PASS):** original V1 `CaptureShadowEnumeration` is token-valid **physical**, not `GetAllAssemblies` logical. It includes interpreter and zero-TypeDef images. The new visitor preserves that membership/order (with additional fail-closed pointer validity) and the first-emplace owner semantics. The original V1 enabled getter is also independently frozen and checked byte-for-byte unchanged. This fixes a prior source-model mismatch in B2 planning.

**B2-V1MAP-02 — admitted TypeDef ownership (host PASS, Unity NotRun):** the new source checks each admitted AOT handle against first owner across **all valid original V1 images**, so it cannot silently report an AOT owner if an earlier interpreter image would win V1. Later duplicates remain admissible under original first-emplace semantics; the two original image snapshots must match. It does not enumerate arbitrary V1 classes or prove every original V1 TypeKey or original getter byte equality.

**B2-V1MAP-03 — bounds and fail-closed compatibility (source PASS):** the existing 1,024 registered AOT images, 8,192 TypeDefs/image, 65,536 physical metadata-handle lookups limits now have a separate **1,024 original V1 physical image** inventory and **65,536 original first-emplace handle lookups** budget. Even a valid original getter may support more images/handles than this restricted source. Budget failure is intentional and does not authorize partial results; true Unity performance and stack usage remain NotRun.

**B2-V1MAP-04 — source timing and lifetime (OPEN, Primary):** original V1 uses independent locks and allocations; the bounded source uses a separate initial metadata Reader and nested original metadata/assembly locks. Equal before/after image lists cannot prove metadata-content stability, absence of ABA, cctor/static values or a coherent VM epoch. First-event B1 and R02/registry counters are independent observational fences. There is no demonstrated postterminal safe full field14/15 owner.

**B2-V1MAP-05 — complete V1 JSON parity (OPEN, Primary):** matching the first image owner for admitted TypeDefs is necessary but insufficient for exact original V1 `GetExecutionDiagnosticsJson` bytes, full original class inventory, non-AOT/VAR/MVAR/unsupported types, allocations, counter snapshots and cctor/static values. The healthy-time observational byte probe is not an atomic full-field source and its fake-original test is not a real V1 getter. Keep `originalV1FullField15ParityProven=false` and `completeExecutionDiagnostics=false`.

**B2-V1MAP-06 — future native V2/acceptance (OPEN, Primary):** original finalDiagnostics (field14) and finalExecutionDiagnostics (field15) require **complete original semantics**. This patch does not supply a terminal-safe snapshot, independent original V2 artifact/envelope/receipt, first external recovery, full-source SDK compilation, real Player, GC/RSS or original-S proof. No approval from source/host CI. Human Review Gate, later milestones and PureInterpreter remain restricted as before.

**B2-V1MAP-07 — standalone host isolation (source checked):** test drivers and fake registration/allocator definitions reside only in NativeHostTests; they must not appear in the official Unity Bee native compilation roster or linked GameAssembly. The earlier oneuse-11 failure demonstrates why final Local symbol/allocator exclusion is mandatory. No new Unity link has run for this source.

## 5. Next Primary and consolidated conditional Local validation

The first remaining Primary-owned stage is complete original nonempty V1 field15 semantics and truthful source coherence: cover the actual class registry and cctor/static/metadata mutations, handle unsupported/removed/renamed TypeDefs, and prove real original enabled getter JSON equality on actual Unity source. Then finish **terminal-safe full field14 and15**, identity-bound one-owner descriptor-relative native V2 artifact/envelope/independent receipt and recovery, add adversarial source/torn-write/duplicate/GC/reentry tests, independently review the final stage, and only then open a **new exact-source one-use Local Validation**.

A future approved one-batch Local cycle should combine: (0) 57+8 exact-source/four-clean-repo/SDK/Original-S/two capacity samples and fresh owner-only output-root admission; (1) one official Unity 2022.3.62f2 Mac ARM64 IL2CPP C++11 full native TU/GameAssembly build with source and symbol/allocator provenance; (2) three independent fresh Players (Empty, initializer19, captured generic15) with actual physical/interpreter image conflicts, primitive, Unicode, generic/array/qualifier owner TypeKeys and complete original V1 byte comparison; (3) full preopened native V2 binary/envelope/readback/externally authenticated receipt; (4) invalid owner/image epochs, class/GC/teardown, B1 race, symlink/partial/replay/duplicate tests; (5) first-call/GC/RSS/crash metrics and independent raw/product custody. These are **not executable yet** and must not be delegated as Primary architecture fixes.

**Product flags remain:** `readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; handoffAuthority=CLOSED_NO_LOCAL_EXECUTION`. Historical consumed B1 oneuse-12 focused real Player 19/19 PASS is preserved; original independent R03 full-stage FAIL and both High IR-R03-01/02 remain open. PureInterpreter disabled. Do not begin H2/M08A/X02/SNAP-01 or self-approve a Human Review Gate.
