# R03 B2 D5-A — staged Local procedure, DRAFT ONLY

**Authority: `D5A=ApprovedByUser`, `D5B=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.** This document describes *future* Local Validation. It is not an active handoff or a command to start the Local Agent, Unity, IL2CPP, a Player, or a platform SDK. Independent D5-A review and a later explicit user D5-B approval are prerequisites. Do not use this draft to infer missing local tools, paths, platform access, source pins or native fault producers.

## 1. Source authority and new admission profile

The D5-A new implementation is isolated under `Tools/AssemblyShadow/R03IR/D5Admission/`, **without editing the historical** `current_native_candidate.json`, `current_native_source_gate.py`, `run_current_native_validation_cycle.py`, `run_captured_generic_local.py`, oneuse-12 manifests or the immutable original-S checkout.

The new, versioned source manifest `d5a_candidate_v1.json` is the reviewed *source roster* (33 files: 7 demo, 9 hybridclr, 4 hybridclr_unity, 13 il2cpp_plus). It pins exact SHA-1 Git blobs and D4 native commits, including the full `AssemblyShadow.cpp` translation unit, `AssemblyShadowProcessSnapshotOwner.h`, the D1 phase receipt, D2/3 files and actual HybridCLR Runtime/Codec. The **12 native `libil2cpp` files** in its `nativeInstallSources` are expected installation inputs, **not** a receipt proving those bytes were installed/compiled. The standalone `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` has global `operator new/delete` overrides: the source profile explicitly excludes it from installation. The historical B1 installation, 14-source/46-VM admission, and result are read-only comparators.

`d5a_source_gate.py` is a **read-only Git/source verifier**; it accepts exact four sibling physical checkout roots and an externally supplied **actual** demo commit SHA. It authenticates per-repo canonical remotes, clean status, exact HEAD and sources, D4 native ownership/P3–P6 order, D3 terminal-before-UsageUnlock, D2 rollback, and the unchanged historical Unity 2022.3.62f2/macOS/IL2CPP build source. It emits JSON only; it cannot launch Unity or produce a Local execution handoff.

**Source-only reference command, not authorized for Local use today:**

```bash
python3 -B <demo-root>/Tools/AssemblyShadow/R03IR/D5Admission/d5a_source_gate.py \
  --demo-root <absolute-four-repo-workspace>/hybridclr_demo \
  --hybridclr-root <absolute-four-repo-workspace>/hybridclr \
  --package-root <absolute-four-repo-workspace>/hybridclr_unity \
  --native-root <absolute-four-repo-workspace>/il2cpp_plus \
  --expected-demo-head <then-latest-reviewed-40-hex-demo-SHA>
```

This command is valid only **after replacing the placeholders with verified physical roots/HEAD**; a D5-B reviewer must separately authorize when Local may run read-only admission. The current D5-A CI already runs the exact command in disposable GitHub Actions source checkouts using the pushed job commit. It does **not** run on a Local Unity machine.

## 2. Prerequisite planning required before a real Local handoff

1. Obtain independent D5-A source/CI decision. Preserve all failed/superseded CI attempts; source-host success is not a Player proof.
2. Produce a D5-B-specific, source-reviewed **real Unity test coordinator** and complete source-native installation proof. It must not call the old B1 coordinator with changed pins. **There is no D5-B runner yet**, and no executable Local command is supplied for it in this draft.
3. Implement/approve test-only real-Player fault producers and deterministic concurrency barriers for the mandatory gaps. The `d5a_fixture_registry_v1.json` lists **18 D5-Cxx Player cells, all `NoCoverage`** under D5-A. Historical controls and D4 host cases are labeled honestly; none are bound to a D5 binary or PID.
4. Require an exact new four-repo source tuple from GitHub, machine/Unity 2022.3.62f2/macOS arm64 toolchain and license proof, and a newly absent output root disjoint from **all four worktrees and previous evidence**.
5. Obtain **separate explicit user D5-B Local approval**. Only then publish the new `WEB_TO_LOCAL.md` with the exact latest pushed demo commit and other three pins, acceptable commands, resource budget, fresh output paths, one-use limit and return-to-Primary evidence rules. Without that approval the Local Agent must reply `NoExecutionAuthority`.

## 3. Proposed D5-B execution protocol, not started

| Stage | Authorized future behavior and required evidence | Stop rule |
| --- | --- | --- |
| Preflight A01–A08 | Audit physically canonical four nested Git roots, clean HEAD/remotes, original S `fc55d8...`, D5 source and install manifests, Unity executable hash/version, Xcode SDK, disk, source-host fixture linkage, fresh one-use output root | Any mismatch ⇒ `BlockedBeforeBuild`; create no batch root |
| Native build B01–B07 | Actual full `AssemblyShadow.cpp` IL2CPP compilation and GameAssembly link, fresh ON/Release and OFF/Release macOS-arm64 Unity 2022.3.62f2 `BuildPipeline` builds, Editor/Bee logs, native symbol map, source→generated/install→binary SHA joins | No successful exact source build ⇒ no Player |
| Player C01–C18 | Fresh separate Player processes for healthy and negative P0–P6, owner lifetime, initializer, first failure, false-return/exception, GC/shutdown and guarded method-entry concurrency; collect PID, linked executable SHA, raw logs and native/managed phase traces | Missing *real* producer ⇒ `NoCoverage`, not `Passed`; terminal execution or UAF ⇒ `ReturnRequired` |
| Compatibility D01–D09 | Original V1 fields14/15, B1 origin, V2 first recovery (if implemented), R02 counters/generics, B2 sparse capacity, target ABI, source/Player/fixture provenance and immutable evidence seal | 32-bit/other platform unsupported ⇒ `NotRun`; never treat historical S as fresh D5 |
| Evidence/return | Sealed `LOCAL_BATCH_RESULT.json`, per-cell receipt and product hash ledger, `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` on issues, exact source/compiled object/binary/PID joins | Do not initiate D6/Human Review Gate or declare R03 accepted without independent Local evidence review |

The [42-cell D5 validation matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md) defines exact cell IDs, gates and statuses. Historical native oneuse-12 had a different, focused B1 source tuple and passed 19 cells; **none of those Player results is D5 product evidence**.

## 4. Evidence and machine-provenance contract

Every real D5 Player case must bind: `sourceTuple`, `sourceFileBlobs`, `unityVersion`, `compilerToolchain`, `nativeInstalledManifest`, `nativeBuildReport`, `linkedBinarySha256`, `fixtureSha256`, `caseId`, `pid`, `exitStatus`, `actualNativePhase`, `snapshotOwnershipState`, `firstError`, `terminalGuardOutcome`, `rawOutputFiles`, `evidenceClass`, `status`, and `reason`. Evidence classes must distinguish real linked Player vs exact source-host, synthetic and historical comparator. Status is `Passed/Failed/Blocked/NotRun/Unavailable/NoCoverage`. Provenance is immutable, no overwritten receipts or unexpected symlinks. No fake baseline fallback or in-process post-P3 rollback.

**Critical unproven cells explicitly retained:** D5-C07 (Codec partial uncertainty), C08 (published group then failure), C09 (post-active owner lifetime), C10 (P5/P6 real concurrent method admission), C13 (unexpected post-active initializer), C17 (GC/shutdown readers). Additional unproven cells in the fixture registry remain `NoCoverage` until real linked producers exist.

## 5. Approval handoff and current gate

Stop D5-A after: a separately audited new source inventory, 47 positive/negative tests per OS in new CI, full new source-only gate receipt, an updated Primary Implementation report and independent D5-A review request. This draft may be amended under Primary ownership after review; it is not the final Local prompt.

**Current:** `D5A=ApprovedByUser`, `D5AIndependentReview=Pending`, `D5B=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
