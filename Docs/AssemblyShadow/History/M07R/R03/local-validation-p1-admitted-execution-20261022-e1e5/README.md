# P1 admitted execution — Local prerequisite Blocked 20261022-e1e5

## Current run — P1 admitted execution 20261022-e1e5 — PrerequisiteBlocked / batch NotRun

[Checkpoint](README.md), [Local outcome](LOCAL_RESULT.json), [finding](FINDING.json), [admission](preflight/ADMISSION_RETAINED_BEFORE.json), [after preservation](preflight/ADMISSION_RETAINED_AFTER.json).

| Actual repository | Branch | Exact source commit |
| --- | --- | --- |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | codex/assembly-shadow-r01b-h1 | 19de9dd4d1040aeb2b72b4e3fe0f89b18df94696 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | codex/assembly-shadow-r01b-h1 | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | codex/assembly-shadow-r01b-h1 | 948c0e3b4f8891481301770115e8ba4945eea6de |
| /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | codex/assembly-shadow-r01b-h1 | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

**BLOCKED / PrerequisiteBlocked. Authorized core batch NotRun; 0/25 components invoked.** The Local-owned independent provenance helper failed before creating INVOCATION.json or launching the prescribed core runner. This is a Local collector prerequisite failure, **not a new failed SDK compilation, failed host test or demonstrated product-native defect**. Initial exact clean local/remote identities, unused/disjoint roots, SDK hashes and retained evidence admission Passed. The preflight root is consumed; raw and SDK scratch roots remain absent. No helper/core retry, changed suffix/source/pins, Unity Editor/Test Runner/Player, product link or milestone advancement occurred.

Actual failed command: python3 -B /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261022-e1e5/run-once.py, exit1. Raw traceback preflight/run-once.log SHA256 c49be929f1ce3d95453a7003cad2c52d3f687ddada3ac52cf0f5f34ecee157b0; failed helper SHA256 73d3a7e1fd1ad9f0d87f584f3c90dab1a3da1000e37db07d5891064eaa850cdd. At line150, original=subprocess.check_output(['git','-C',str(N),'cat-file','blob',blob]);assert data==original.

First failed comparison: reconstructed AssemblyShadow.cpp versus frozen Git blob 53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2. The helper adapted the later owned-name reconstruction but omitted stripping the new source-authenticated admitted wrapper include in its **earlier opaque reconstruction**. That earlier reconstruction retains exactly the new three-line CPP include/comment block and fails historical byte equality. The analogous API reconstruction also needs its exact four-line admitted declaration/comment removal; it was **not reached by the failed helper**, and was diagnosed read-only afterward. Native published run_opaque_execution_inventory.py already contains exact admitted_include/admitted_decl stripping. No production verifier regression or original fingerprint rebaseline is established.

**Read-only diagnosis, not a retry:** extracted published literals using AST and compared actual current CPP/API with immutable native82dd source. Reconstructed the failed comparison as data only. Removing only the published new include/declaration bytes restores **both** current CPP/API to native82dd and then the unchanged frozen CPP/API blobs. No source, failed helper, compiler or SDK was edited. Exact residual diffs/hashes: preflight/AssemblyShadow.cpp.FROZEN_COMPARISON.json, AssemblyShadow.h.FROZEN_COMPARISON.json and FINDING.json. This does not substitute for the scheduled tests, SDK compilation or aggregate.

**Timing/environment:** earliest preflight snapshot 2026-10-23T03:07:15.679246+00:00 UTC; failure-log mtime 2026-10-23T03:07:21.990666+00:00 UTC. Exact failed-helper process start/PID is **Unavailable / not recorded before the core invocation stage**; file times were not used to fabricate it. Diagnostic/preservation collector UTC 2026-10-23T03:10:15.130784+00:00 → 2026-10-23T03:10:37.108787+00:00; America/Los_Angeles 2026-10-22T20:10:15.130784-07:00 → 2026-10-22T20:10:37.108787-07:00. Environment: preflight os.json, kernel.json, clang.json, python.json and sdkpath.json. clang++ --version was a metadata query; **zero translation-unit compilations** ran. Official Unity2022.3.62f2 was read-only and never launched.

| Obligation | Actual state |
| --- | --- |
| Four exact clean source and remote identities | Passed independently before/after |
| Fresh canonical disjoint roots | Passed before preflight creation |
| Source/package/historical pins preservation | Passed |
| SDK and historical evidence preservation | Passed before/after |
| Local opaque frozen-byte reconstruction | Failed prerequisite in Local helper |
| Original85 failure-contract tests | NotRun |
| New nine strict +nine sanitized cases | NotRun |
| Eight source inventory flags | NotRun |
| Five managed positives plus exact negative | NotRun |
| 100 native SDK syntax configurations | NotRun |
| 20 batch Git postflight commands | NotRun |
| Core manifest lifetime consistency | NotRun; core outputs absent |
| Unity/Player/product linking/runtime | NotRun |

| Component | State | Invoked |
| --- | --- | --- |
| command-failures | NotRun | false |
| legacy-host | NotRun | false |
| metadata-gate | NotRun | false |
| bounded-class | NotRun | false |
| bounded-physical | NotRun | false |
| bounded-first-use | NotRun | false |
| owned-general | NotRun | false |
| live-general | NotRun | false |
| owned-execution | NotRun | false |
| empty-live | NotRun | false |
| opaque-inventory | NotRun | false |
| physical-membership | NotRun | false |
| owned-physical-names | NotRun | false |
| owned-physical-json | NotRun | false |
| live-owned-physical-json | NotRun | false |
| observed-type-shape | NotRun | false |
| live-type-shape-census | NotRun | false |
| observed-type-shape-json | NotRun | false |
| vm-shape-json | NotRun | false |
| admitted-execution | NotRun | false |
| bounded-status | NotRun | false |
| bounded-inventory | NotRun | false |
| frozen-v2 | NotRun | false |
| managed-sdk | NotRun | false |
| native-sdk | NotRun | false |

**After-preservation:** all 2405 installed SDK files / 316062203 bytes match before hashes; full installed input inventory unchanged. All bound source bytes/Git inputs match. All **22 consumed P1 raw/scratch/audit sets, 24 prior checkpoint sets and 88 historical negative symlinks** were verified before/after. Historical audit/checkpoint files have no additions, removals or byte changes. Independent read-only Git checks verify four exact clean source heads; they are **not the core 20-command postflight or aggregate PASS**.

Preserve 7896 PASS / PassedSourceHostAndSDKOnly, 7c2c PASS and 82dd FAIL / FailedOrIncomplete, including its original timeout/sourcePreserved=false/fourRepositoriesAfter=[]. Original IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01 SourceConfirmed_NotFaultInjected and its corrected successor disposition remain unchanged. No old host/SDK result is claimed as fresh.

**IR-LOCAL-P1-ADMITTED-PREFLIGHT-01 / Primary direction:** review the Local collector omission and exact diagnosis. A future independently admitted collector must strip **only** source-authenticated admitted CPP/API literals in **every** affected frozen-byte comparison, retain original blobs and fail-closed gates, and verify its reconstruction before execution. No native/SDK/compiler or test-source change is justified here. The handoff stops on failed prerequisite, so these roots will not resume. Another validation needs a new Primary handoff with unused roots. Still required: the entire 25-component cycle, original85/eight inventories/nine+9/five+negative/100 syntax/20 actual Git joins, fresh preservation and factual publication.

**Exit: Local Validation → Primary Implementation, BLOCKED.** P1 Incomplete; P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Canonical TypeKeys, physical pointer origin/lifetime, coherent VM epoch, complete nonempty V1, genuine getter integration, linked Player and GC/RSS/Shutdown remain unproved. Historical SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent full-stage R03 FAIL/re-review NotRun remain immutable. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; runtimeAcceptance=false. PureInterpreter disabled. No H2/X02/M08A or further cycle authorized.

External evidence: /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-ADMITTED-EXECUTION-20261022-e1e5. Expected raw /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-ADMITTED-EXECUTION-20261022-e1e5 and scratch /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-ADMITTED-EXECUTION-20261022-e1e5 are absent/NotRun. LOCAL_RESULT.json is an independent prerequisite outcome, **not core RESULT.json**. This checkpoint MANIFEST.sha256 authenticates Local documentation/copies only; no constructed batch seal or core RESULT/MANIFEST/compiler output is fabricated. Prepared audit.py was never executed.
