# R03 B2 — Actual Runtime publication group: bounded design, plan, evidence, Primary review

**Date:** 2026-11-18 UTC. **Scope:** Primary source-host test only; no native production edits, Local Validation authorization, R03 acceptance, or Human Review Gate.

## Pinned source and design

All repos use branch **codex/assembly-shadow-r01b-h1**. Tested code/workflow: **night-outlook/hybridclr_demo@0b2971c6509451151afb6d5f6e329875b0e417ad**. Host test Git blob **cfb471163f23ddd82da1cbd150c622bb3a912e9b**; workflow Git blob **8dd20b113769212ee36c0846d84c491ef18c155e**.

CI checks out detached **night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55** and authenticates the commit tree and working copy SHA for each source:

| Actual source path under hybridclr | Git blob |
| --- | --- |
| hybridclr/metadata/InterpreterMetadataIndexCodec.h | 2020d4e2da6dea8601525203e7ab307d21c40a73 |
| hybridclr/metadata/InterpreterMetadataIndexRuntime.h | c39ac0f5a0c1ea93c55d51e04d25d31a71775260 |
| hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp | 509e357359a8912c05adac3434a7e71b3fc3f83c |
| hybridclr/metadata/AssemblyShadowBridge.h | 5340c0bf9e4c4c211b4379929f3f79133661505a |

Production pins unchanged: **night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de** and **night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a**.

**Design boundary:** extend the previous actual Codec PublishBatch test to execute the **actual InterpreterMetadataIndexRuntime.cpp**, its unmodified Codec and actual Runtime APIs. Only the two AssemblyShadowBridge private-stage/VM-public predicates and a minimal test il2cpp-config.h are simulated. Images are stable opaque pointer markers; the test never constructs or dereferences an Il2CppClass or real InterpreterImage. The mock VM activation bit is **not** the native AssemblyShadow active snapshot.

## One-cycle implementation plan and delivery

1. Add Tools/AssemblyShadow/R03IR/TypeDefCensus/ActualRuntimePublicationGroupHost.cpp outside production source rosters; test actual Runtime normal-return state.
2. Add .github/workflows/r03-b2-actual-runtime-publication-group-host.yml with four exact upstream source blob checks, macOS 15 / Ubuntu 24.04 × C++11 / C++17, strict optimized and ASan/UBSan profiles.
3. Inspect failed receipts; repair only host test/workflow defects; publish raw distinctions between actual Runtime code, mock Bridge, and unavailable Unity/GC/native evidence.
4. Review and stop. Do not touch native Runtime/VM/locks, physical census bounds, Local handoff authority, or later milestones.

The host exercises **12 ordered cases:** invalid inputs before Initialize; reservation and ScopedConstruction; private visibility; later missing member; later unfinalized member; duplicate ID; successful two-image ordinary group; refusal to abort/republish; published/private mix rejection; later aborted member blocking earlier shadow image; completed codec/group publication while mock VM is inactive; and visible shadow image only after mock VM activation. The actual Runtime's Decode and GetPublishedImage outcomes are checked, including the extra Shadow-public predicate. **No concurrent readers are tested.**

## GitHub CI evidence

- [Initial run 44222851693](https://github.com/night-outlook/hybridclr_demo/actions/runs/44222851693): **FAIL 4/4**. GCC -O2 -Werror reports a possible uninitialized FootprintStats.sealed in the pinned Runtime.cpp line 188; the original Mac test incorrectly captured mapped-page stats before the test's own Encode calls.
- [Intermediate run 44223034388](https://github.com/night-outlook/hybridclr_demo/actions/runs/44223034388): **FAIL** (test counter snapshot corrected; GCC strict still treats diagnostic as fatal).
- [Intermediate run 44223061862](https://github.com/night-outlook/hybridclr_demo/actions/runs/44223061862): **FAIL** (Ubuntu C++17 passed; empty Bash array expansion under macOS Bash 3.2 + set -u aborted the Mac jobs before compilation).
- **Final [run 44223227500](https://github.com/night-outlook/hybridclr_demo/actions/runs/44223227500): PASS 4/4** on macOS/Ubuntu × C++11/C++17. Every job log contains two actual Runtime test JSON receipts (strict and sanitized), **12 cases / 95 assertions per execution**, eight receipts total. All real Unity/native/rollback/approval flags are false.

The final CI retains -Wall -Wextra -Werror -pedantic, while explicitly leaving **only GCC -Wmaybe-uninitialized nonfatal and visible**. The warning occurs at the existing local FootprintStats declaration in the actual Runtime; GetFootprintStats assigns all fields when returning None, but GCC does not prove this across the call. The warning is retained as a source/toolchain limitation, not silently suppressed. No production code was altered.

## Primary code/evidence review findings

**RUNTIME-01 — PASS / limited:** actual pinned Runtime and Codec normal-return paths reject invalid later entries without publishing earlier ones, activate the ordinary two-image group, reject abort/republication of the group, and retain the extra mock VM public predicate for Shadow image resolution. This is direct compiled Runtime evidence, unlike the previous synthetic phase model.

**RUNTIME-02 — OPEN / HIGH:** the native AssemblyShadow::PublishActive, actual VM snapshot, native UsageLock and lock graph, GC/class/metadata lifetime, whole-VM epoch and Unity Player are not compiled or executed. A mock bridge cannot establish real atomic transaction publication or shutdown quiescence.

**RUNTIME-03 — OPEN / HIGH:** only sequential successful/negative normal returns are covered. The irreversible codec lifecycle store followed by Runtime group visibility and native snapshot publication is not proven exception-safe; post-codec unknown failures remain terminal/restart-required absent independent rollback evidence. No concurrent reader or publish/abort race was exercised.

**RUNTIME-04 — TOOLCHAIN:** GCC emits one visible potential-uninitialized diagnostic per Ubuntu optimized strict job. A separate authorized native change may consider value-initializing FootprintStats; this cycle does not alter pinned source or assert a runtime defect.

**RUNTIME-05 — NOT RUN:** authenticated original physical TypeDef/use census, class/GC allocation provenance, original V1 fields 14/15, complete native V2 receipt/readback/first recovery, 32-bit ABI, real Unity Player/resource/lock measurements, Local Validation and independent Human Review.

## Disposition and stop

**PassedActualRuntimeNormalReturnsWithMockBridgeOnly** at exact tested code commit 0b2971c6509451151afb6d5f6e329875b0e417ad. Production B2 remains inactive with **128 combined TypeDefs / 64-byte declaration fields / 65,536 indexed owner lookups**; original V1/B1/R02/resolver, 64-native/eight-demo source roster and PureInterpreter activation unchanged. **WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION; R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false.** Do not replay consumed B1 oneuse-12, attach a native collector, alter native failure policy or locks, begin H2/M08A/X02/SNAP-01, or self-approve a Human Review Gate.

**Next Primary scope:** separate pre-integration source review of the actual VM active-snapshot ordering, native exception/UsageLock custody around irreversible publication and necessary review authorization. This test alone is not approval to change the production transaction.