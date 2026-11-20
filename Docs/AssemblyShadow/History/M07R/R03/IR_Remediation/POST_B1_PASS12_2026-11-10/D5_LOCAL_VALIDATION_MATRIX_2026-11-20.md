# R03 B2 D5 — proposed source-pinned Local Validation matrix

**Status: PROPOSED; `D5LocalValidation=NotAuthorized`; no Local execution.** This matrix accompanies [D5 preapproval design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md). It is a future validation specification, **not** a command to run a Player or a claim that the listed fault producers already exist. The only approved predecessor is bounded independent [D4 `PassD4ForNextGate`](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md).

## 1. Authority and execution classes

**Planned source tuple:** `hybridclr_demo` current branch `codex/assembly-shadow-r01b-h1`, to be frozen to the **latest pushed HEAD in the future authorized handoff**, while D4 source/host evidence remains at `c3307abacaaaec9db2a0f866b726e2ae5df1108b`. Other fixed reviewed heads:
- `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`
- `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`
- `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`

**Initially proposed target:** Unity 2022.3.62f2, macOS Apple Silicon arm64, actual `StandaloneOSX` IL2CPP Release feature ON, plus a separately rebuilt feature-OFF control. The local runner currently expects this exact Unity version and `R03Build.Build` configuration (`BuildOptions.Development | DetailedBuildReport`; native Release is the C++ compiler configuration, not a non-development Player claim). Avoid pretending the legacy B1 runner accepts the D4 native tuple.

Every cell must be tagged `RealPlayer`, `RealUnityBuild`, `NativeCompilerLink`, `ExactSourceHost`, `SourceOnly`, `HistoricalComparator` or `Synthetic`. Only the first three can close appropriate real-environment integration requirements.

### Gate A — new D5 source admission and environment (before creating any evidence root)

| ID | Test / activity | Positive proof | Fail-closed or no-coverage behavior |
| --- | --- | --- | --- |
| D5-A01 | Four physical Git roots + canonical remotes and branch | Exact 40-char HEAD in each; `git status --porcelain` clean; absolute, disjoint paths | Any drift, dirty tree, alternate repo ⇒ `BlockedBeforeBuild` |
| D5-A02 | D4 production source inventory | Git blobs for D2 registry, D3 lease, D4 `AssemblyShadow.cpp`, process owner and D1 receipt agree with new D5 profile | Wrong/extra native source, old B1 `CURRENT` or unrecognized generated file ⇒ Blocked |
| D5-A03 | Unity 2022.3.62f2 and native build environment | Executable file/hash, installed IL2CPP module, platform/arch, Xcode/Clang version, SDK and license validated | Missing tools ⇒ `Unavailable`, never a substitute build |
| D5-A04 | Isolated original-S comparator | Separately clean original demo SHA `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, canonical remote | Historical source absent ⇒ Blocked comparator; never fabricate |
| D5-A05 | Fresh output custody | Physically canonical, absent, disjoint evidence roots, no symlinks, enough free space (existing runner threshold: 20 GiB) | Path exists/aliases historical root ⇒ Blocked, zero overwrites |
| D5-A06 | Native source-roster and allocator test isolation | Real libil2cpp build input list excludes `NativeHostTests` global `operator new/delete` overrides | Prior oneuse-11 failure class reappears ⇒ Blocked before Player |
| D5-A07 | D5 profile self-validation | New `D5` manifest and exact local admission contract pass source/negative mutation tests in CI | Stale old fixed **14/46 B1 cardinalities** ⇒ reject, not bypass |
| D5-A08 | Diagnostic fixture capabilities | Exact producer filenames/symbols, fault stage and expected provenance predeclared; checked into Git | Absent/unlinked real fault producer ⇒ `NoCoverage` for its cell |

### Gate B — full native IL2CPP build and artifact identity

| ID | Test / activity | Required observable/evidence | Failure rule |
| --- | --- | --- | --- |
| D5-B01 | Actual C++/native translation unit | Current full `AssemblyShadow.cpp`, `AssemblyShadowProcessSnapshotOwner.h`, D1 receipt, D2/D3/Runtime definitions included/compiled | Compilation not executed ⇒ `NotRun` despite host CI |
| D5-B02 | ON/Release macOS arm64 IL2CPP BuildPipeline | `BuildReport.Succeeded`, error count 0, Editor.log, Bee DAG/source digests and `.app` inventory | Build fail ⇒ no Player launch |
| D5-B03 | OFF/Release macOS arm64 IL2CPP control | Independent fresh build/receipt, flag `HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0`, no shadow behavior | Cannot reuse ON binary to claim OFF |
| D5-B04 | Link symbol and native ABI provenance | GameAssembly/export map, SHA-256, architecture, UUID, source-to-compiled-object join, absence of allocator overrides | Linked image mismatch ⇒ Blocked |
| D5-B05 | Generated HybridCLR output origin | `PrebuildCommand.GenerateAll` inputs, generated `MethodBridge.cpp`/metadata hashes, install root, package commit | Wrong or untracked generated material ⇒ Blocked |
| D5-B06 | Feature/diagnostics/stripping configuration | Native flags and test control values recorded; managed stripping Low as current fixture, relevant compile/runtime defines | Unrecorded feature/diagnostics flags ⇒ Blocked |
| D5-B07 | Full native warning/ASan (where supported) | Compiler/link logs and sanitizer/symbolization policy, no hidden warning promotion | Unsupported sanitizer ⇒ `Unavailable`, not Passed |

### Gate C — fresh Player, phase/fault and terminal behavior

**Each negative case uses a fresh Player process**. Before testing any fault, verify its source-pinned producer exists and is enabled **only** in a test build. A crash/fault is a pass only if its expected terminal/recovery behavior is actually observed; process exit alone is not proof. For post-Codec failures, the snapshot/registry and Codec must not be described as rolled back.

| ID | Test/phase | Required observation | Explicit negative condition |
| --- | --- | --- | --- |
| D5-C01 | Healthy P0→P6→Complete | Native receipt/trace P0,P1,P2,P3,P4,P5,P6 in order; `Committed`; healthy method execution; stable owned snapshot | Wrong/missing phase, unknown class identity, or early method activity |
| D5-C02 | P0 closure validation refusal | No usage acquisition/registry mutation/Codec; correct error; no new public snapshot | Any irreversible store or dirty retry |
| D5-C03 | P0 source-witnessed used-closure | `BaselineAlreadyUsed`, proven preappend registry/usage cleanup; only this class permits `Validated` | Retryable P1+ or incorrect terminal poisoning |
| D5-C04 | P1 admitted/preappend native rejection | Usage released; all mutations accounted for; explicit terminal classification unless independently proven safe | Hidden progress to P3 or deadlock |
| D5-C05 | P2 physical+CLI append then pre-Codec fault | Registry vectors restored/owned in native scopes; correct terminal fallback for unproven cleanup | False claim that Codec/group was reversed |
| D5-C06 | P3 real Codec validation error | Authentic actual Codec entry/error, no silent retry; error/first receipt and terminal guard, lifecycle recorded | Return to Validated after Codec attempted |
| D5-C07 | P3 uncertain/partial Codec fault | Authentic real native fault after first possible lifecycle store; terminal with immutable first-error and no unsafe fallback | Treating a synthetic stub as actual partial-Codec proof |
| D5-C08 | P4 real group active, before native active store | Runtime group release-store observed; `s_active` absent; business denied, restart required | In-process retry, baseline fallback or execution allowed |
| D5-C09 | P5 after `s_active` release-store | Process-owner pointer already retained; post-store exception cannot delete; terminal failure no rollback | Raw pointer dangles or owner missing |
| D5-C10 | P5→P6 concurrent method-entry window | Deterministic independent thread + real VM dispatch/guard; no unauthorized early Shadow business execution | Method admission before initializer policy permits it ⇒ critical `ReturnRequired` |
| D5-C11 | P6 initializer control | One real linked initializer; `Committed` on success; original V1/B1 and native trace consistent | Synthetic initializer called only from host |
| D5-C12 | P6 explicit initializer failure | `FailedAfterCommit`, original initializer error/origin, no overwritten first cause | Generic InternalError incorrectly replacing originating failure |
| D5-C13 | P6 unexpected diagnostic/initializer throw | `ScopedPostActiveExit` terminal, snapshot remains owned, later business denied | Exit leaves Committing/Committed while terminal input exists |
| D5-C14 | P5/P6 first failure preservation | Earlier native producer wins once (B1); later errors cannot replace; V1 compatibility retained | Wrong reason/origin, string truncation without a recorded limit |
| D5-C15 | Terminal method/GC/cctor negative | Repeated real managed/native callbacks cannot mutate AOT canary after terminal failure; no hangs; stderr/Unity exception evidence | Unchecked baseline AOT fallback or changed canary |
| D5-C16 | Separate-process restart behavior | A *new process* may start clean; no claim of in-process rollback/restart | Reusing prior native process/heap |
| D5-C17 | Snapshot reader/shutdown | Concurrent public readers and GC/shutdown/exit do not observe invalid owner; native exit signal/stack retained | UAF, UB, native leaked callback reachability |
| D5-C18 | Prior B1/PureInterpreter feature-OFF control | Previous oneuse-12 three-Player modes as fresh D5 binary observations (not copied), PureInterpreter remains disabled | Historical receipts substituted for new runs |

### Gate D — compatibility, budgets, ABI, evidence sealing

| ID | Requirement | Acceptance evidence / fallback |
| --- | --- | --- |
| D5-D01 | Original V1 diagnostic fields 14/15 | Exact source-defined fields and byte/provenance comparison from fresh real Player; semantic claims limited to source definitions |
| D5-D02 | B1 native origin and first recovery V2 | Real native readback of frozen first event, code/origin/reason and first-recovery; absent V2 transport ⇒ `NoCoverage`, never auto-Pass |
| D5-D03 | R02 baseline/captured generics | Fresh physical owner and generic argument path, exact negative and healthy controls, R02 counters and one-use source identity |
| D5-D04 | B2 sparse budget/owner indexing | Confirm inactive bounds of 128 combined TypeDefs, 64 bytes per name and 65,536 indexed owner lookups; no runtime expansion |
| D5-D05 | ABI platform coverage | On macOS arm64, record `std::atomic<uint32_t>::is_lock_free`, C++ pointer width/alignment and compiled native ABI. **32-bit/Android/iOS/Windows must be separately executed or marked NotRun** |
| D5-D06 | Memory/VM/shutdown | Actual GC and native Player exit logs, owner retention, no premature destructor/use-after-free. CloseAndDrain only if target implementation is present |
| D5-D07 | Immutable raw evidence | Each command's exact argv, cwd, PID, exit, UTC timestamp, stdout/stderr hash, source and binary SHA, fixture SHA, result and attempt number |
| D5-D08 | Product seal and manifest | Regular files only, no unexpected symlinks, complete SHA-256 ledger, local one-use root, original/replay comparison role tags |
| D5-D09 | Final independent review entry | Every required cell has explicit result and evidence; no `Blocked`/`NoCoverage` silently reclassified. Return to Primary for nontrivial fixes |

## 2. Planned commands and read order — **not currently executable D5 authority**

Authoritative Local read order after separate D5 authorization:

1. `Docs/AssemblyShadow/README.md` and `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` at the exact then-pushed demo HEAD.
2. [D5 design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md), this matrix, and [independent D4 review](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md).
3. New **approved** D5 candidate source profile and `run_d5_local.py` (path is **proposed, not present**); then historical B1 fixtures as **read-only comparator**.
4. Only after read-only admission, build once per authorized role and launch Players in fresh, separate processes.

**Existing scripts with grounded command-line interfaces, but stale pins — NEVER run as D5 today:**

```text
# EXISTING historical B1 runner, FOR REFERENCE ONLY, NOT D5 AUTHORIZED:
python3 -B Tools/AssemblyShadow/R03IR/run_captured_generic_local.py \
  --workspace <absolute-four-repo-root> \
  --original-s <clean-original-S-checkout> \
  --output <new-disjoint-output-root> \
  --unity <Unity-2022.3.62f2-executable> \
  --demo-commit <latest-pushed-D5-demo-SHA>
```

This invocation does **not** accept the current D4 native/HybridCLR pair: it is source-bound to the former B1 `current_native_source_gate.CURRENT`. Do not copy this command to an active Local handoff until a separately versioned and CI-tested D5 runner exists. The actual `R03Build.Build` Unity entry point requires `-r03Config` pointing to a hash-authenticated isolated test project and fresh output; the runner must prepare it. Unity batch/IL2CPP CLI use should match the official **2022.3** manual, not an unverified current-major-version command.

## 3. Evidence schema and custody

Proposed fresh one-use external evidence root (only once separately authorized):

```text
R03-B2-D5-<unique-oneuse-id>/
  ADMISSION.json                 # four repo HEADs, remotes, clean status, machine, toolchain
  SOURCE_ROSTER.json             # native source/file blobs, installed/generator manifests
  BUILD/
    on-release/BUILD_RECEIPT.json
    on-release/Editor.log
    off-release/BUILD_RECEIPT.json
    off-release/Editor.log
    <compiler-Bee-source-and-linked-binary-manifests>
  PLAYER/
    <D5-Cxx>/<case-id>/argv.json
    <D5-Cxx>/<case-id>/process.json
    <D5-Cxx>/<case-id>/raw.stdout
    <D5-Cxx>/<case-id>/raw.stderr
    <D5-Cxx>/<case-id>/Player.log
    <D5-Cxx>/<case-id>/phase.json
    <D5-Cxx>/<case-id>/first-error.json
    <D5-Cxx>/<case-id>/terminal.json
  ABI/target-properties.json
  COMPATIBILITY/v1-b1-r02-b2.json
  CELLS.json
  LOCAL_BATCH_RESULT.json
  MANIFEST.sha256
  POSTFLIGHT.json
```

Each `CELLS.json` entry must provide `id, status, evidenceClass, sourceCommits, outputHashes, processPids, expected, observed, resultReason, sourceProducer, nativePhase, nativeFirstError, terminalState, scopeLimits`. `status` is one of `Passed`, `Failed`, `Blocked`, `NotRun`, `Unavailable`, `NoCoverage`; zero executions may not be reported as Passed. Distinguish literal file bytes from JSON summaries. Store CLI/Player logs even for failed BuildPipeline / SIGABRT, and always seal negative control receipt without changing historical artifacts.

## 4. Accept/reject rules and stop

**Local Validation is accepted as *evidence-ready for independent review* only if** the required macOS real native/link tests are Passed; the required feature-ON and feature-OFF fresh build receipts are source-authentic; every fresh Player test which is marked Passed actually launched an authenticated binary; phase/failure business gates and GC/shutdown cells are covered or clearly recorded as blockers, with no unreviewed runtime defect; provenance, original S comparators and product seal all pass; and an independent reviewer can reproduce the join from source SHA to compiled GameAssembly to PID/log/first-error and public pointer owner.

**Do not grant D5 Complete or R03 Accepted from a total number of green cells.** A critical failure, unsupported real fault producer, missing V2 first-recovery, untested P5/P6 concurrent method gate, untested 32-bit ABI, or unclear binary provenance must remain separately visible as `ReturnRequired`, `NoCoverage`, or `NotRun` and the next Human Review Gate must not be entered.

D5-C07, D5-C08, D5-C09, D5-C10, D5-C13 and D5-C17 are **new risk-focused mandatory acceptance targets** that source-host CI explicitly does not close. If their real-Player producers are absent, Primary must add source-reviewed test-only instrumentation before Local runs them; never pretend a test-only adapter is a real registered native VM producer without linkage and observed evidence.

**Current disposition:** `D5Matrix=PreparedForApproval`; `D5Execution=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. D4 remains independently `PassD4ForNextGate` for its original narrow scope.
