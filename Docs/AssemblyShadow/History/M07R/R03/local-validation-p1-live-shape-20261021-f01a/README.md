# R03 P1 inactive VM-to-shape census — Local 20261021-f01a

## Current run — P1 inactive VM-to-type-shape census source/SDK 20261021-f01a

[Checkpoint](README.md), [independent audit](preflight/EVIDENCE_AUDIT.json), [live census verification](preflight/LIVE_TYPE_SHAPE_CENSUS_VERIFICATION.json), [exact invocation](preflight/RECEIPT.json), [collector correction](preflight/LOCAL_PROVENANCE_HELPER_CORRECTION.json).

| Actual repository | Branch | Exact execution commit |
| --- | --- | --- |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `2f72fcb6df30890962bc6415325d3f0830ef376f` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `d8d4695c2d3da0e541f9e1a525cfffbcc3b1c230` |

Exact command: `python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --expected-demo 2f72fcb6df30890962bc6415325d3f0830ef376f --expected-native d8d4695c2d3da0e541f9e1a525cfffbcc3b1c230 --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-LIVE-SHAPE-20261021-f01a --sdk-scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-LIVE-SHAPE-20261021-f01a`.

Read-only official SDK anchor: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Environment versions and compiler paths: checkpoint preflight python.json, clang.json, os.json, kernel.json and sdkpath.json. Actual source, historical pins, package manifest/resolution, source-anchor equivalence and exact remote identities: SOURCE_BINDINGS.json, SOURCE_TRANSPORT_EQUIVALENCE.json, DOCS_ONLY_COMMITS.json, GIT_BEFORE.json and GIT_AFTER.json. Full admission and installed SDK snapshots are retained with all source/command hashes.

**PASS / PassedSourceHostAndSDKOnly: 22/22 components Passed.** Exactly one core invocation, PID 65671, exit 0. America/Los_Angeles 2026-10-21T03:05:19.579829-07:00 → 2026-10-21T03:08:35.074029-07:00; UTC 2026-10-21T10:05:19.579829+00:00 → 2026-10-21T10:08:35.074029+00:00. This is fresh source/host/official installed Unity2022.3.62f2 SDK syntax evidence. Unity Editor, Test Runner, Player, product linking, runtime GC/RSS and Shutdown were **NotRun**.

| Component | Status | Actual inner result |
| --- | --- | --- |
| command-failures | Passed | PassedWithinHostScope |
| legacy-host | Passed | PassedHostOnly |
| metadata-gate | Passed | PassedWithinHostScope |
| bounded-class | Passed | PassedWithinHostScope |
| bounded-physical | Passed | PassedWithinHostScope |
| bounded-first-use | Passed | PassedWithinHostScope |
| owned-general | Passed | PassedWithinOwnedHostScope |
| live-general | Passed | PassedWithinInactiveSourceHostScope |
| owned-execution | Passed | PassedWithinOwnedExecutionHostScope |
| empty-live | Passed | PassedWithinInactiveZeroClassHostScope |
| opaque-inventory | Passed | PassedWithinInactiveOpaqueHostScope |
| physical-membership | Passed | PassedWithinInactivePhysicalEnumerationHostScope |
| owned-physical-names | Passed | PassedWithinInactiveOwnedPhysicalNamesHostScope |
| owned-physical-json | Passed | PassedWithinOwnedPhysicalNamesJsonHostScope |
| live-owned-physical-json | Passed | PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope |
| observed-type-shape | Passed | PassedWithinObservedTypeShapeSourceHostScope |
| live-type-shape-census | Passed | PassedWithinInactiveLiveTypeShapeCensusHostScope |
| bounded-status | Passed | PassedWithinHostScope |
| bounded-inventory | Passed | PassedWithinHostScope |
| frozen-v2 | Passed | PassedWithinInactiveHostScope |
| managed-sdk | Passed | Passed |
| native-sdk | Passed | Passed |

**New inactive VM-source-to-shape census:** strict and ASan/UBSan each executed all **28 original names +15 original shape +16 new live census groups**, exactly 59 ordered PASS labels/profile. Fifteen native source-before/after SHA256/size/Git-blob bindings, five direct compiler-version/compile/run receipts and complete direct streams verify. Both actual production VM .inl methods compile together with the real pointer-free Census, using explicit VM class/metadata Reader/registry/iterator/lock host mocks. New producer RESULT SHA256 `2798d1b72f86e13770b6a6a3a59decb980e1afeae516a210e11d860bf012e618`; actual live method SHA256 `0472835c03165278579dc3b332f6ef74eea22fb0d527a337bdb157beb14a79d7`; actual fixture SHA256 `3c6c05d586bf519d9d8352fad1e0f5e9f05b96ad04be2c488f7e32bd64c27e80`.

Independent source review verifies caller namesReceipt is reset **before** Fresh preflight; stale/partial/prior successful census fails before iterator and revokes names/scratch; existing first-matched physical capture returns before pure Build; names are revoked after Build success/failure. Fixtures assert source Reader and locks return to zero, no name rows/text or pointer scratch remain, mixed Candidate/ActiveShadow category/role counts, conservative generic/array/nested/unsupported/missing metadata hints, source failure and post-pass revision rejection, stale source-receipt clearing and unchanged iteratorCalls for rejected reused output. The new wrapper performs no additional metadata traversal, pointer dereference, lock, heap/file operation. Result contains primitive observed-subset category counters, **not canonical execution TypeKeys**. No separate numeric per-case census JSON was emitted; evidence is source-authenticated C++ require assertions and complete ordered PASS groups.

The original CPP/API fingerprint constants are unchanged. Independent Local reconstruction removes only exact reviewed additive CPP Census-header/.inl and API forward/declaration bytes and verifies byte equality to native `9260eceaedb9ad1d06de6a769bd070e9c946cc90`, then retains all earlier immutable fingerprint reconstructions. Actual current CPP/API/.inl bytes remain independently bound and included in official SDK compilation. Existing normal getters/managed transport/registration source is not activated by these mocks. The source delta is preserved as losslessly encoded hashed UTF-8 evidence.

**Required retained inventories:** 85 distinct failure-contract tests in modules 5+14+44+10+12, zero failures/errors/skips/expected failures/unexpected successes. The new live-census adversarial consumer cases execute inside those unchanged 85 discovery leaves. Names 28+28, pure owned JSON 21+21, live VM-to-JSON 12+12 plus original 28/profile, original observed shapes 15+15 plus original 28/profile, and all earlier legacy/metadata/general/first-use/empty/opaque/execution/status/inventory/frozen suites Passed. Physical membership remains 21/profile; opaque/publisher 34/profile; owned execution six×35; all six old/current V1 byte pairs match. All **five** independently authenticated outer booleans are true: ownedBindingCaseInventoryVerified, ownedPhysicalJsonCaseInventoryVerified, liveOwnedPhysicalJsonCaseInventoryVerified, observedTypeShapeCaseInventoryVerified, liveTypeShapeCensusCaseInventoryVerified. These host fixtures do not prove real VM pointer validity or process behavior.

**Official managed compilation:** five actual managed positive products, 428 source inputs. Returned binding is the canonical nested `managed-sdk/build-api/results.json`, SHA256 `aeca51b1b0367858bf8e13927f2829d8181ae6428cd926290daceee96eb7ad5a`; stdout path/hash and outer innerResultPath/innerResultSha256/returnedBindingVerified agree, root decoy absent. OriginalUnsignedCounts is a distinct expected-negative compiler exit1, exactly two CS0266, no DLL. This expected-negative is not a successful product build. Retained managed warning occurrences: 68.

**Official native compilation:** 100/100 actual Apple arm64 C++17 `-fsyntax-only` commands, 20 translation units×five candidate/debug/probe-off/diagnostics-off/feature-off profiles, no native product linking. Complete AssemblyShadow.cpp includes the new .inl, and the existing owned-name syntax probe references the new actual VM method signature. 1922 SDK/overlay inputs rehashed. Retained native warning occurrences: 742. Raw compiler commands, response files, logs and input hashes are retained.

**Preservation and audit:** installed official SDK 2405 files/316062203 bytes unchanged. Seventeen consumed P1 raw/scratch/audit sets, 68 deliberate historical negative symlinks, nineteen prior checkpoint sets and both original host-only FAIL/PASS evidence were verified before and after, with no outcome reclassification. Raw current manifest has 4114 regular entries and four deliberate negative symlinks authenticated separately through legacy manifest. 485 localized command-stream receipt pairs verified. sourcePreserved=true; postflightError=null; stoppedAfter=null; commandLifetimeUnverified=false; managed/native SDK attempted and passed. descendantQuiescenceProven=false remains unchanged.

**Local collector diagnostics (preserved):** before any core invocation, the reused read-only Local helper twice stopped because it retained predecessor reconstruction rules/Docs descent anchor. Exact newly published additive CPP/API literals were independently authenticated to restore predecessor bytes, and the Docs-only descent anchor was corrected to the current handoff's `01b093fd1f450c7dc69d0395de237590ddcf6b5f`. Both original helper versions/logs and the correction receipt are retained. No production, test, compiler procedure or expectation changed; no core/host/compiler batch was retried. Full prerequisites then passed before the sole core invocation. This is a Local collector correction, not a new product defect.

**Limits and exit:** no new nontrivial product finding in this source/host/SDK scope. Physical class allocation/pointer origin and lifetime, canonical generic-aware execution TypeKeys, VM-wide epoch/coherence/general ABA freedom, complete nonempty execution V1 JSON, process GC/RSS/latency, actual metadata Shutdown and linked Player acceptance remain unproved. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; runtimeAcceptance=false; PureInterpreter expansion disabled. No H2/X02/M08A or milestone progression. Exit: **Local Validation → Primary Implementation**. This root set is consumed; further execution requires a new handoff.

Raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-LIVE-SHAPE-20261021-f01a`. SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-LIVE-SHAPE-20261021-f01a`. Independent audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-LIVE-SHAPE-20261021-f01a`.

Raw RESULT SHA256 `634e2cde556f477092d6243100859fc0f2bb3672f9ea477ecb853a167235604d`; raw MANIFEST SHA256 `40cd91f146366fef8d3d079bb6cfeaa94cfd530985660aef0f2fe7769834cdc7`. Every checkpoint regular file is listed in MANIFEST.sha256; COPY_BINDINGS.json joins copied bytes and losslessly encoded raw diffs to retained originals. SDK/vendor/product binaries are externally retained and were not uploaded. Local source binding is the execution tuple above; subsequent publication is documentation only.
