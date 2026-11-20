# R03 B2 D5-A — Primary Implementation review, source-only admission

**Disposition: `D5A_Primary=CompleteSourceCI`, `D5A_IndependentReview=Pending`, `D5B=NotAuthorized`.** Date: 2026-11-20 UTC. This is **Primary Implementation evidence, not independent approval**. D5-A was explicitly [approved by the user](D5A_PRIMARY_IMPLEMENTATION_USER_APPROVAL_2026-11-20.md) for source/fixture/CI preparation only, following independent [D4 `PassD4ForNextGate`](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md). It does not begin Local Validation or the Human Review Gate.

## 1. Exact scope, repository authority and connector transport

Branch: `codex/assembly-shadow-r01b-h1`, all four repositories.

| Repository | Implementation source authority | Change scope |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | **CI-tested source commit `6b3990e9bd6c0e7008f987ad93308b7d92d736a8`**; later docs-only HEAD independently rechecked before publication | New versioned D5-A profile, fixture registry, read-only validator, 47 mutation/source tests and CI workflow; new D5-A docs |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | **Unchanged** Runtime/Codec/source |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | **Unchanged** Unity package |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | **Unchanged** D2–D4 native production |

A GitHub Connector read/write smoke test on a **disposable** demo-only branch `codex/smoke-d5a-20261120-gpt6-a01` created commit `b27b03e9a2f339f90a300cc1fcae5c7249a88b3a` and verified exact branch HEAD and content readback. Branch deletion is unavailable in the connector; **the disposable branch remains**, separate from the feature branch and is not an acceptance commit.

The exact GitHub compare from demo bootstrap `a728c869481dd82f12526545749ecda4cfceaf3a` to the last source/plan checkpoint lists **new D5-A files only**. None of the historical B1 runner/source files or original S / oneuse-12 evidence was modified.

## 2. Implemented source-owned deliverables

All new source code under `Tools/AssemblyShadow/R03IR/D5Admission/`:

| File | Purpose / exact Git blob |
| --- | --- |
| `d5a_candidate_v1.json` | **e15bdbff02de2dbb7adef42c39f363fe2d1f3b37** — pinned D4 native/HybridCLR/package commit tuple, **33 exact Git file blobs** (7 demo historical, 9 hybridclr, 4 package, 13 native), 12 `libil2cpp` installation-*intent* paths, explicit exclusion of standalone allocator host code, historic B1 14/46 profile retained |
| `d5a_fixture_registry_v1.json` | **dbdfd51b85b1a8dfc9caedd9916842e1b0d042fc** — all 18 D5-Cxx future Player cases, all labeled `NoCoverage`; `ExistingHistorical` and `ExactSourceHost` are **not** real D5 Player proofs. Six mandatory P3–P6/GC cases listed separately |
| `d5a_source_gate.py` | **8e1fa91c8fe3158c7095dab2116f95af80fd1e00** — read-only Git HEAD/remote/clean-tree + physical sibling roots, exact source blobs and native D2–D4/Runtime phase ordering, legacy B1 candidate consistency, Unity 2022.3.62f2 `BuildPipeline` source check; always emits `UnityOrPlayerExecuted=false` |
| `test_d5a_source_gate.py` | **5fae18301dd96fda27cac9657968659cfd735a12** — 47 unit/source/mutation/path negative tests: wrong pins, Local authorization spoofing, host allocator installation, old B1 14/46 mutation, P3/P4/P5/P6 source alterations, fixture false Player PASS, wrong Unity builder and reused output root |
| `.github/workflows/r03-b2-d5a-source-admission.yml` | **f9f3da46eb37e2179adbe609800fe88e1f9aa8f0** — macOS 15 + Ubuntu 24.04 × Python 3.11, four separate Git checkouts at the exact source tuple and real code HEAD, 47 tests/job and explicit wrong-demo-SHA rejection; **no Unity, native compiler, Local SDK, Player or device execution** |

The profile does **not** hard-code a moving `hybridclr_demo` commit into its own bytes. CI supplies the *actual* triggering demo commit and checks `git rev-parse HEAD` and clean working tree; later D5-B formal handoff must freeze the then-latest pushed 40-hex demo commit. Profile/fixture bytes are independently hard-pinned to their Git blob values in the validator. Paths and remote identities are checked separately for every repository. The Local evidence-root policy is a read-only predicate, not a `mkdir` or reusable output permission.

A 12-file `nativeInstallSources` **expected-source list is not actual installation or linkage evidence**. The standalone `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` contains global `operator new/delete` overrides implicated in historical oneuse-11; it is verified as a *standalone host file* and **excluded** from the intended Unity native source list. No real Unity installation, Bee DAG or GameAssembly link has been audited.

Source-only and Local semantics remain distinct:
- **D5-A passes source authorization only**, not an old B1 coordinator with loosened count checks.
- The prior `current_native_candidate.json` still pins `il2cpp_plus@8aa8d093...` and `hybridclr@4b2774b0...`; old composed admission remains 14 files/46 VM files. They are **not** D5 source pins.
- Existing `R03Build.Build` is still a historical test builder and Unity version guard; no D5 native build-runner has been implemented.
- D5-C fault producers (especially Codec partial/postgroup, post-active concurrency, GC/shutdown) are **not** D5 Player-linked. Fixture registry `NoCoverage` is deliberate, not a test failure disguised as success.

## 3. Actual CI evidence (raw logs independently read)

[**CI run 44701514587**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44701514587) at demo **`6b3990e9bd6c0e7008f987ad93308b7d92d736a8`**: **completed/success, run attempt 1, 2/2 successful jobs**.

| Host | Job ID | Unit/source/mutation tests | Read-only exact source receipt | Negative control |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `136170773950` | **47/47 PASS** | 33 Git blob/head source files authenticated; 18 Player cells `NoCoverage` | Wrong demo SHA correctly exits 2 |
| macOS 15 | `136170774310` | **47/47 PASS** | Same 33-source/18-cell proof | Wrong demo SHA correctly exits 2 |
| **Total** | | **94 passing tests** | **2 source-only receipts** | **2 expected rejections** |

The logs emit `PassedD5ASourceOnly_NoUnityOrLocal`, `UnityOrPlayerExecuted=false`, `installedUnityNativeSourceValidated=false`, `realD5PlayerCellsPassed=0`, `D5B=NotAuthorized`, and `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. Both jobs separately printed `ExpectedWrongDemoPinRejected` and `SourceTestsOnly`; there were no unexpected assertion, import or CLI errors. These values are **not** claimed from a Unity run.

**Historical source/CI attempts remain unaltered:**
- `44701007296`, `44701183171`, `44701193894`: **failure**, during initially incomplete test/tool imports or a missing negative check.
- `44701302399`: **success** at an earlier *10-path* native-roster proposal, not final roster.
- `44701484271`: **failure** while changing immutable manifest to the reviewed 12-path roster.
- `44701514587`: **current completed/success** after synchronizing exact profile blob and native header roster. Never aggregate attempts as if all passed.

## 4. Primary review findings and limitations

| Finding | Status | Required next step |
| --- | --- | --- |
| D5A-PI-01 — four-repo Git source admission replaces stale B1 pins without modifying old code | **PASS — source-only** | Independent review the exact 33-blob roster and static invariants |
| D5A-PI-02 — D4 P5 owner/P6 ordering and D3 terminal guard verified via actual source | **PASS — source-only** | Do not claim full production translation-unit compilation |
| D5A-PI-03 — B1 test allocator file excluded from *proposed* native installation | **PASS — intent only** | Real Bee/compiled source linkage must be audited during authorized Local |
| D5A-PI-04 — all 18 D5 Player case probes have honest `NoCoverage` status | **PASS — provenance/no-coverage honesty** | Source-review test-only real native/managed fault producers before attempting corresponding Player cells |
| D5A-PI-05 — complete Local runner and platform/ABI proof | **NotImplemented / NotRun** | Separately authorized D5-B design/runner and fresh macOS Unity/IL2CPP Player |
| D5A-PI-06 — independent D5-A approval | **Pending** | Separate independent review; Primary must not self-approve |

D5-A is **source-only infrastructure**, not Local Validation or RealPlayer acceptance. A future approval sequence must independently review this exact code/CI, prepare the D5-B harness/producer/source-roster gate, obtain **separate D5-B Local execution approval**, then publish a fresh source-pinned `WEB_TO_LOCAL`. The planned [staged Local draft](D5A_STAGED_LOCAL_PROCEDURE_DRAFT_2026-11-20.md) and [42-cell matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md) are **not executable authority**.

**Current gate:** `D5A=PrimaryImplementationComplete_SourceHost`, `D5AIndependentReview=Pending`, `D5B=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. No H2/M08A/X02/SNAP-01, D6, Human Review Gate, or real Unity/IL2CPP/Player work is authorized by this report.
