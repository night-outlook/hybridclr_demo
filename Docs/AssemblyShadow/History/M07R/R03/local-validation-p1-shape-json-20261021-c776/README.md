# R03 P1 pointer-free shape census JSON — Local 20261021-c776

## Current run — P1 pointer-free type-shape census JSON source/SDK 20261021-c776

[Checkpoint](README.md), [independent audit](preflight/EVIDENCE_AUDIT.json), [live census verification](preflight/LIVE_TYPE_SHAPE_CENSUS_VERIFICATION.json), [exact invocation](preflight/RECEIPT.json), [shape JSON verification](preflight/OBSERVED_TYPE_SHAPE_JSON_VERIFICATION.json).

| Actual repository | Branch | Exact execution commit |
| --- | --- | --- |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `1144284ba3cbc2cdb75b68edf3df26d241860ccc` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `c7762af878f36c102ac7a953035e082b55aebf40` |

Exact command: `python3 -B /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py --workspace /Users/ah/GitHub/hybridclr/assembly_shadow_h1r --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --expected-demo 1144284ba3cbc2cdb75b68edf3df26d241860ccc --expected-native c7762af878f36c102ac7a953035e082b55aebf40 --output /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-SHAPE-JSON-20261021-c776 --sdk-scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-SHAPE-JSON-20261021-c776`.

Read-only official SDK anchor: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Environment versions and compiler paths: checkpoint preflight python.json, clang.json, os.json, kernel.json and sdkpath.json. Actual source, historical pins, package manifest/resolution, source-anchor equivalence and exact remote identities: SOURCE_BINDINGS.json, SOURCE_TRANSPORT_EQUIVALENCE.json, DOCS_ONLY_COMMITS.json, GIT_BEFORE.json and GIT_AFTER.json. Full admission and installed SDK snapshots are retained with all source/command hashes.

**PASS / PassedSourceHostAndSDKOnly: 23/23 components Passed.** Exactly one core invocation, PID 68997, exit 0. America/Los_Angeles 2026-10-21T06:00:01.068403-07:00 → 2026-10-21T06:03:25.475010-07:00; UTC 2026-10-21T13:00:01.068403+00:00 → 2026-10-21T13:03:25.475010+00:00. This is fresh source/host/official installed Unity2022.3.62f2 SDK syntax evidence. Unity Editor, Test Runner, Player, product linking, runtime GC/RSS and Shutdown were **NotRun**.

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
| observed-type-shape-json | Passed | PassedWithinOwnedTypeShapeJsonSourceHostScope |
| bounded-status | Passed | PassedWithinHostScope |
| bounded-inventory | Passed | PassedWithinHostScope |
| frozen-v2 | Passed | PassedWithinInactiveHostScope |
| managed-sdk | Passed | Passed |
| native-sdk | Passed | Passed |

**New inactive pure pointer-free aggregate type-shape JSON:** strict and ASan/UBSan each Passed all **16 new JSON +28 original name +15 shape +16 live census groups**, 75 exact ordered labels/profile. Five direct compiler-version/compile/run receipts, actual two production VM methods and pure JSON header compiled together under explicit VM class/Reader/registry/iterator/lock mocks, fifteen source-before/after SHA/size/Git-blob bindings, immutable CPP/API fingerprint chain and complete direct streams verify. Producer RESULT SHA256 `27eb61ce919456b5906f5deb0e52c5e1928085e2bf6295cd1670f75fce3c3252`; actual header SHA256 `6eb08c239c34eb55a8f7e2f1fc1ca84244fc501131c7564d328018d7f0d756e3`; actual fixture SHA256 `d087b022bee79dbc247640b6194191dce4d8746df2854642feb61d6ef06f6e66`. All six outer case inventory flags independently verify.

JSON is distinct `R03P1ObservedTypeShapeCounts` / `ObservedRegistrySubsetShapeCountsOnly`, integer schemaVersion 1, registry revision, observed/Candidate/ActiveShadow counts and nine named integer category counters, with literal false canonical TypeKey, physical origin, coherent VM epoch, Player and runtime flags. Independent audit parsed the byte-exact empty JSON **source fixture literal** (not a runtime-emitted artifact); actual strict/sanitized assertions compare exact bytes and receipt length. Genuine source fixtures verify value/generic/mixed-role counts, owned output unchanged after source mutation, incomplete or forged authority rejection, role/category partition rejection, missing callback category, saturated revision, small and oversized byte budgets, repeated-success revocation and refused reuse after failure. First Record error remains the initial typed error; the current call Receipt can report ReusedOutput. No per-row or per-case numeric JSON output files were emitted or fabricated.

The pure one-shot Record owns a fixed **4096-byte** array, object ceiling **4224 bytes**. Public Data/Bytes are unavailable before successful complete Writer.Finish plus Record.Seal; failure clears the whole array and count. Source validation verifies all counts/roles/categories and nonauthority predicates before writing. Formatter performs no VM traversal, metadata pointer access, heap/file or lock operation. Output has no raw physical names/generic signatures and is **not canonical execution TypeKeys, execution V1/V2, a source authentication token or runtime qualification**. Native delta from d8d4695 is exactly four additions (pure header, host fixture/runner and CI); all pre-existing production files are byte-identical. Existing official SDK owned-name probe instantiates actual shapeJson::Compose in all five unchanged profiles; 20 TUs×five remains 100 actual syntax configurations. New consumer negatives remain inside the original unchanged 85 discovery leaves; no tests or compiler expectations were weakened.

**Retained inactive VM-source-to-shape census:** strict and ASan/UBSan each executed all **28 original names +15 original shape +16 new live census groups**, exactly 59 ordered PASS labels/profile. Fifteen native source-before/after SHA256/size/Git-blob bindings, five direct compiler-version/compile/run receipts and complete direct streams verify. Both actual production VM .inl methods compile together with the real pointer-free Census, using explicit VM class/metadata Reader/registry/iterator/lock host mocks. New producer RESULT SHA256 `ae49bd0261c9f5a9123bf0a1f6a780931b3d2b190a7b90e4be1281fc6e04a01b`; actual live method SHA256 `0472835c03165278579dc3b332f6ef74eea22fb0d527a337bdb157beb14a79d7`; actual fixture SHA256 `3c6c05d586bf519d9d8352fad1e0f5e9f05b96ad04be2c488f7e32bd64c27e80`.

Independent source review verifies caller namesReceipt is reset **before** Fresh preflight; stale/partial/prior successful census fails before iterator and revokes names/scratch; existing first-matched physical capture returns before pure Build; names are revoked after Build success/failure. Fixtures assert source Reader and locks return to zero, no name rows/text or pointer scratch remain, mixed Candidate/ActiveShadow category/role counts, conservative generic/array/nested/unsupported/missing metadata hints, source failure and post-pass revision rejection, stale source-receipt clearing and unchanged iteratorCalls for rejected reused output. The new wrapper performs no additional metadata traversal, pointer dereference, lock, heap/file operation. Result contains primitive observed-subset category counters, **not canonical execution TypeKeys**. No separate numeric per-case census JSON was emitted; evidence is source-authenticated C++ require assertions and complete ordered PASS groups.

The original CPP/API fingerprint constants are unchanged. Independent Local reconstruction removes only exact reviewed additive CPP Census-header/.inl and API forward/declaration bytes and verifies byte equality to native `9260eceaedb9ad1d06de6a769bd070e9c946cc90`, then retains all earlier immutable fingerprint reconstructions. Actual current CPP/API/.inl bytes remain independently bound and included in official SDK compilation. Existing normal getters/managed transport/registration source is not activated by these mocks. The source delta is preserved as losslessly encoded hashed UTF-8 evidence.

**Required retained inventories:** 85 distinct failure-contract tests in modules 5+14+44+10+12, zero failures/errors/skips/expected failures/unexpected successes. The new live-census adversarial consumer cases execute inside those unchanged 85 discovery leaves. Names 28+28, pure owned JSON 21+21, live VM-to-JSON 12+12 plus original 28/profile, original observed shapes 15+15 plus original 28/profile, and all earlier legacy/metadata/general/first-use/empty/opaque/execution/status/inventory/frozen suites Passed. Physical membership remains 21/profile; opaque/publisher 34/profile; owned execution six×35; all six old/current V1 byte pairs match. All **six** independently authenticated outer booleans are true: ownedBindingCaseInventoryVerified, ownedPhysicalJsonCaseInventoryVerified, liveOwnedPhysicalJsonCaseInventoryVerified, observedTypeShapeCaseInventoryVerified, liveTypeShapeCensusCaseInventoryVerified, observedTypeShapeJsonCaseInventoryVerified. These host fixtures do not prove real VM pointer validity or process behavior.

**Official managed compilation:** five actual managed positive products, 428 source inputs. Returned binding is the canonical nested `managed-sdk/build-api/results.json`, SHA256 `dd9b3590550084a823c492c7cb5be8c4e27ac34a16f410dc5f43ea43a422f6b6`; stdout path/hash and outer innerResultPath/innerResultSha256/returnedBindingVerified agree, root decoy absent. OriginalUnsignedCounts is a distinct expected-negative compiler exit1, exactly two CS0266, no DLL. This expected-negative is not a successful product build. Retained managed warning occurrences: 68.

**Official native compilation:** 100/100 actual Apple arm64 C++17 `-fsyntax-only` commands, 20 translation units×five candidate/debug/probe-off/diagnostics-off/feature-off profiles, no native product linking. Complete AssemblyShadow.cpp includes the new .inl, and the existing owned-name syntax probe references the new actual VM method signature. 1923 SDK/overlay inputs rehashed. Retained native warning occurrences: 742. Raw compiler commands, response files, logs and input hashes are retained.

**Preservation and audit:** installed official SDK 2405 files/316062203 bytes unchanged. Eighteen consumed P1 raw/scratch/audit sets, 72 deliberate historical negative symlinks, twenty prior checkpoint sets and both original host-only FAIL/PASS evidence were verified before and after, with no outcome reclassification. Raw current manifest has 4139 regular entries and four deliberate negative symlinks authenticated separately through legacy manifest. 490 localized command-stream receipt pairs verified. sourcePreserved=true; postflightError=null; stoppedAfter=null; commandLifetimeUnverified=false; managed/native SDK attempted and passed. descendantQuiescenceProven=false remains unchanged.

**Historical Local collector diagnostics:** original f01a read-only provenance-helper versions, initial logs and correction receipt remain byte-preserved in their consumed raw/audit/checkpoint sets. No predecessor result was rewritten or rerun. This cycle uses the current source anchor and performs one core invocation.

**Limits and exit:** no new nontrivial product finding in this source/host/SDK scope. Physical class allocation/pointer origin and lifetime, canonical generic-aware execution TypeKeys, VM-wide epoch/coherence/general ABA freedom, complete nonempty execution V1 JSON, process GC/RSS/latency, actual metadata Shutdown and linked Player acceptance remain unproved. P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain unchanged. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; runtimeAcceptance=false; PureInterpreter expansion disabled. No H2/X02/M08A or milestone progression. Exit: **Local Validation → Primary Implementation**. This root set is consumed; further execution requires a new handoff.

Raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-SHAPE-JSON-20261021-c776`. SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-SHAPE-JSON-20261021-c776`. Independent audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-SHAPE-JSON-20261021-c776`.

Raw RESULT SHA256 `bfb1bae44bd5b6a3ba2f90cccbcc30fe3af316250d9b0d3b7a09aa7558f9375c`; raw MANIFEST SHA256 `3e5a03eb7c00aa2a00c377a2ef3b88aef24cc9d2291a3d1b79e5f16e56a3770c`. Every checkpoint regular file is listed in MANIFEST.sha256; COPY_BINDINGS.json joins copied bytes and losslessly encoded raw diffs to retained originals. SDK/vendor/product binaries are externally retained and were not uploaded. Local source binding is the execution tuple above; subsequent publication is documentation only.
