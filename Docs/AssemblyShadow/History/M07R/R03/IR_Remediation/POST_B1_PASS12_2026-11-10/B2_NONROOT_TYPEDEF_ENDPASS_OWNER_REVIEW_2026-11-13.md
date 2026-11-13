# R03 B2 — Bounded non-root TypeDef first-owner end-pass audit

**Date:** 2026-11-13 UTC. **Scope:** Primary Implementation, inactive R03 B2 execution diagnostics only. **Branch:** codex/assembly-shadow-r01b-h1 on all four repositories. **Native:** night-outlook/il2cpp_plus@8901942f5d04e97cf8cad59a6dc2922c1d40ceee; **demo source gate/test anchor:** night-outlook/hybridclr_demo@65c69841320fa47b1314128730b7fde4868cd717. Other native/package pins unchanged: hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55, hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de. The enabled original V1 getter's exact 5,222-byte fixture and B1 producer are unchanged. Final demo documentation HEAD should be checked separately.

## Original V1 source gap

The original enabled execution V1 getter constructs the physical token-valid TypeDef handle/image map with first-emplace semantics. The previously published inactive B2 collector authenticated owner for every admitted TypeKey component via resolveOwner, but the end-of-collection check only revisited **registered class root** handles. Nested declaring TypeDefs, constructed generic argument TypeDefs (including cross-image/unobserved owners), and already-existing primitive default TypeDefs could lose an indexed metadata owner or gain an earlier owner **after their owned row was copied**. Class root image, TypeDef handle, class cctor/static fields and image tokens can all remain unchanged in this case.

This is an observed-source divergence, not proof of any real Unity concurrent metadata mutation.

## Source design and exact change

Added a bounded, locally owned NonRootOwnerAudit inside the same native AssemblyShadowBoundedDefinitionExecutionLiveSource.inl. After original physical owner proof in resolveOwner, every distinct **non-root** TypeDef handle is recorded with the independently verified original physical first-owner image. Same handle+owner is deduplicated; conflicting owners reject. Only admitted TypeDef handle values are stored, never TypeDef/name content or class pointers.

- Maximum **128 distinct handle/image pairs** for the full source capture. Overflow revokes the complete capture with SourceOutsideBudget; no partial coverage is accepted.
- Scratch static_assert **<=2,064 bytes** and no heap allocation from the new helper. The destructor and explicit success path scrub all pairs while the initial MetadataLifetimeGate Reader and original g_MetadataLock remain active.
- After existing third physically matched class pass has rechecked root TypeDef owners, and **after the independent second original V1 physical image source visit**, all recorded non-root pairs are independently checked again with the ORIGINAL first-emplace owner policy and MetadataCache::GetAssemblyTypeHandle indexed reads.
- A **separate 65,536 indexed-lookup limit** applies to this non-root audit, independent of the prior row-construction and root-recheck budgets. Owner disappearance returns OriginalV1OwnerMissing, different earlier first owner returns OriginalV1FirstOwnerConflict, and exhaustion returns OriginalV1LookupBudget. No new physical class enumeration, arbitrary metadata dereference or Player entrypoint was introduced.
- Scoped receipt originalV1NonRootTypeDefOwnersRecorded/Rechecked/Lookups/EndPassStable reports only authenticated captured pairs; Reject clears all and revokes owned rows and frozen record. The already existing originalV1FirstEmplaceOwnerMatched receipt now depends on the successful root AND bounded non-root rechecks. A positive zero-entry audit is vacuously stable, not an assertion that non-root handles exist.
- The original enabled V1 getter, B1 native path, R02 and active runtime resolution are unchanged.

**Stack and timing:** the new audit adds <=2,064 bytes of local scratch beyond the previously bounded packed class facts <=53,264 bytes and original-image facts 12,288 bytes. It may perform up to 65,536 additional indexed reads under g_MetadataLock, increasing worst-case source cost. Combined previously separate budgets are not one global single-pass limit, and actual Unity lock hold times, GC and worker stack are **NotRun**.

## Host tests and published CI

[Native exact-source CI 43358606294](https://github.com/night-outlook/il2cpp_plus/actions/runs/43358606294) at il2cpp_plus@8901942f5d04e97cf8cad59a6dc2922c1d40ceee: **4/4 PASS** (macOS-15/Ubuntu-24.04 × C++11/C++17; Release/Debug strict/ASan-UBSan). The checked-in inactive VM .inl compiles against the synthetic mock VM. **120 scenarios and 5,221 assertions per host process.** Five new fail-closed mutations: (1) same-image generic argument indexed owner removed at end pass; (2) cross-image **unobserved** argument owner removed; (3) existing primitive default TypeDef owner removed; (4) nested declaring Outer TypeDef owner removed; (5) an earlier interpreter physical image becomes first owner of a generic argument. The class root itself remains constant in each negative. Positive host receipts verify a zero non-root source for root-only cases, >=1 for same/cross image generic, >=2 for nested and primitive cases, and exact unique recorded/rechecked counts.

[Four-fork source audit 43358990655](https://github.com/night-outlook/hybridclr_demo/actions/runs/43358990655) on demo@65c69841320fa47b1314128730b7fde4868cd717: **2/2 PASS** macOS/Ubuntu, verifies **64 native and eight demo reference source Git blobs**, original V1 getter, native restricted producer new pair recording/end-pass check, typed receipt clearing, exact new negative modes and 15 additional manifest overclaim mutations in focused Python source-gate tests. The final documentation commit may trigger a new workflow; its own SHA conclusion must be checked.

**These are synthetic VM and source tests, NOT official Unity native translation-unit, GameAssembly, Player, real HybridCLR interpreter metadata, or class/GC/VM lifetime evidence.**

## Source-review findings and still-blocking work

- **NONROOT-01 / scoped PASS:** the admitted non-root TypeDef handles used in the restricted class TypeKeys are now end-pass first-owner checked in addition to roots; five independent indexed-owner late mutations are rejected without inventing partial rows or reporting full coverage.
- **NONROOT-02 / capacity and time OPEN:** 128 unique non-root handles is intentionally a *narrow upper bound*, not a complete general V1 execution-class inventory. Captures beyond 128 fail closed. Worst-case additional 65,536 metadata reads under g_MetadataLock need real Unity profiling.
- **NONROOT-03 / semantics OPEN:** an unchanged first-owner image may still return the same handle at another index, or TypeDef name/namespace, generic arity, nested declarations, context or metadata bytes may change behind unchanged pointers; this audit does not prove their content. Open VAR/MVAR and unsupported interpreter nested/generic shapes still reject.
- **NONROOT-04 / lifetime and epoch OPEN:** no GC/class allocation lifetime ticket, no ABA-proof immutable whole-VM epoch, no terminal-safe no-allocation source; three class observations and two image observations do not create atomic consistency. This is not original V1 enabled getter-to-Player byte parity.
- **NONROOT-05 / delivery BLOCKED:** complete original general field14 and execution field15 immutable preterminal values, native descriptor-relative V2 artifact/envelope, identity-bound external receipt/readback and independently authenticated first recovery remain unimplemented. The prior independent R03 full-stage FAIL/High findings remain; historical B1 oneuse-12 focused real Player 19/19 PASS is consumed and not evidence for B2.

**Next Primary-owned work:** complete class shape/metadata-content and lifetime/epoch source admission without overstating first-owner equality, then full preterminal field14/15 and V2. Do not begin H2/M08A/X02/SNAP-01 or approve a Human Review Gate.

**Acceptance flags:** readyForNativeV2FieldCapture=false; nativeV2TransportImplemented=false; firstRecoveryAuthenticatedV2=false; runtimeAcceptance=false; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; wholeVmEpoch=NotProven; PureInterpreter disabled. WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION.
