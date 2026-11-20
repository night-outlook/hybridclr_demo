# R03 B2 D5-A — Independent source and CI review

**Independent decision: `PassD5AForD5BPreparation` (STRICTLY SOURCE-ONLY).** Review date: 2026-11-20 UTC. Role: **independent reviewer**, separate from Primary Implementation and Local Validation. This decision passes **only** the versioned D5-A *source-admission preparation* milestone and allows a separately scoped task to prepare stronger D5-B test producers, native installation provenance, and a new reviewable handoff. **It does not approve D5-B Local execution, real Unity/IL2CPP/Player builds, H2, R03 acceptance or a Human Review Gate.**

This is a **bounded pass with explicit follow-up requirements**. It is not an endorsement of unexecuted Player tests or the claim that the current D5-A source gate by itself can safely authorize a Local run. The source-level weaknesses documented in findings IR-D5A-06 and IR-D5A-07 **must be resolved before any D5-B Local admission**. If they cannot be resolved, D5-B remains Blocked.

## 1. Independent evidence and exact revisions

I independently reopened the original [D5-A user authorization](D5A_PRIMARY_IMPLEMENTATION_USER_APPROVAL_2026-11-20.md), [Primary implementation review](D5A_SOURCE_ADMISSION_PRIMARY_IMPLEMENTATION_REVIEW_2026-11-20.md), [review request](D5A_INDEPENDENT_SOURCE_REVIEW_REQUEST_2026-11-20.md), [D5 preapproval design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md), [D5 matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md), canonical `README.md` and `WEB_TO_LOCAL.md`. I treated these as requirements/context rather than substitutes for code and raw evidence. GitHub Connector was used to inspect the *actual* five tested D5-A files, native/HybridCLR source definitions, independently fetch each file Git blob, retrieve run/jobs and both raw logs, and compare exact commits.

**All four repositories have branch `codex/assembly-shadow-r01b-h1`.** Verified remote HEAD at review bootstrap:

| Repository | Review-bootstrapped remote HEAD | Source/test role |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `026f73a07d037b90bfa8e8e2f6881520f004c926` | CI-tested D5-A implementation is **`6b3990e9bd6c0e7008f987ad93308b7d92d736a8`**; later six commits changed docs only |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | P3/P4 actual Runtime/Codec source, unchanged from D4 |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unity package source, unchanged |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | D2–D4 native source, unchanged |

The exact compare `hybridclr_demo@a728c869481dd82f12526545749ecda4cfceaf3a...026f73a07d037b90bfa8e8e2f6881520f004c926` lists **17 commits** affecting only four new D5-A source/profile files, one new CI workflow and D5-A planning/review/README/handoff documentation. The historical B1 `current_native_source_gate.py`, `current_native_candidate.json`, `run_current_native_validation_cycle.py`, `run_captured_generic_local.py`, oneuse-12 evidence and the three production repositories were **not modified**. The compare `6b399...026f...` is **six docs-only commits**; the later README does not count as fresh CI-tested implementation.

The **five exact D5-A tested blob identities**:

| Tested file | Git blob |
| --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json` | `e15bdbff02de2dbb7adef42c39f363fe2d1f3b37` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5a_fixture_registry_v1.json` | `dbdfd51b85b1a8dfc9caedd9916842e1b0d042fc` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5a_source_gate.py` | `8e1fa91c8fe3158c7095dab2116f95af80fd1e00` |
| `Tools/AssemblyShadow/R03IR/D5Admission/test_d5a_source_gate.py` | `5fae18301dd96fda27cac9657968659cfd735a12` |
| `.github/workflows/r03-b2-d5a-source-admission.yml` | `f9f3da46eb37e2179adbe609800fe88e1f9aa8f0` |

**I independently read back all 33 Git file blobs** named by the proposed D5-A profile, using the correct four repository revisions: **7/7 demo, 9/9 hybridclr, 4/4 hybridclr_unity, 13/13 il2cpp_plus** matched the manifest. This corroborates the CI source checks without relying on a Primary-written statement. Manifest and fixture are also hard-pinned by Git blob within the gate code. The moving demo HEAD is *not* embedded within the manifest, preventing an impossible self-referential file hash.

## 2. CI evidence: independently verified

[**GitHub Actions run 44701514587**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44701514587), pushed demo commit `6b3990e9bd6c0e7008f987ad93308b7d92d736a8`, **attempt 1 completed/success, 2/2 jobs success**.

| OS | Actual job ID | Real executed Python cases | Source output | Negative demo-pin case |
| --- | --- | --- | --- | --- |
| Ubuntu 24.04 | `136170773950` | **47/47 PASS** | 33/33 pinned blobs, 18/18 `NoCoverage` | **Expected rejection** |
| macOS 15 | `136170774310` | **47/47 PASS** | 33/33 pinned blobs, 18/18 `NoCoverage` | **Expected rejection** |
| **Total** | | **94 passing source/unit/mutation cases** | **2 source-only receipts** | **2 expected failing controls** |

I fetched both raw job logs and inspected the individual `test_01`–`test_47` results, `Ran 47 tests ... OK`, full source receipt fields, the source gate's actual `github.sha` admission, and both nonzero wrong-demo-SHA rejects (`ExpectedWrongDemoPinRejected`). No unexpected import, assertion, or source-gate failure occurred. The workflow checks exact C++/managed *source files*, **not** a C++ native build, Player, device, GC epoch or native ABI. Result fields correctly report `UnityOrPlayerExecuted=false`, `installedUnityNativeSourceValidated=false`, `realD5PlayerCellsPassed=0`, `D5B=NotAuthorized`, and `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`.

Historical D5-A runs retain their original statuses: `44701007296`, `44701183171`, `44701193894`, `44701484271` **failed**; `44701302399` **passed a superseded 10-native-path roster**. They are **not** interchangeable with the final validated `44701514587` run.

## 3. Independent source and scope findings

### IR-D5A-01 — PASS: pinned source provenance and isolation

`d5a_source_gate.py::inspect` and `validate_git_checkout` require exactly four sibling physical checkout roots; use `git rev-parse HEAD`, `--show-toplevel`, local branch/detached status, canonical configured `origin`, and an empty `git status --porcelain`. `audit_source_bytes` authenticates each of the 33 selected regular non-symlink files against both the reviewed Git blob and `HEAD:path`, rejecting LFS pointer text. `validate_profile` and `validate_fixture` require the expected immutable blob, source roster counts, fixed production pins, D4 predecessor, and explicit No Local authority. The CI also independently uses four pinned checkouts and supplies `github.sha` as the expected demo commit.

**Scope precision:** This is exact *source file and local Git commit* admission, not proof of an installed libil2cpp source roster, remote-ref freshness, full compilation, or readiness to run Unity. It does not verify the entire repository's file inventory, only the 33 files selected in its published manifest.

### IR-D5A-02 — PASS: D2–D4 essential source-order checks and old B1 isolation

The actual HybridCLR Runtime calls `beforeCodec` immediately before real Codec publication and `afterRuntimeGroup` after the real group active store. The unchanged native `ReleasePublicationUsage` seals D3 terminal failure before releasing UsageLock; D4 `ProcessSnapshotOwner` moves ownership into process lifetime before publishing `s_active`; `PublishActive` records P5 after the public store; `CommitTransaction` records P6 before managed initializer entry, with `Complete` on normal successful completion. D2 physical/CLI scoped rollback files are unmodified, and the new D5-A gate crosschecks their source signatures.

The new 12-path `nativeInstallSources` is **an expected installation-intent subset**; it is not a proof that all 12 were actually installed or compiled by Bee. The old B1 current-native source files continue to pin `il2cpp_plus@8aa8d093...`, `hybridclr@4b2774b0...`, 14-file/46-VM inventory, and have not been altered to accept D4. `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` contains actual global `operator new/delete`; the D5-A proposed native install list excludes that standalone host driver, but the actual Unity build/input symbol table has **not** been checked.

### IR-D5A-03 — PASS / future NoCoverage: honest fixture and authority boundaries

I independently inspected all **18** D5-C01–C18 fixture records. Every one has `d5RealPlayerProducerLinked=false`, `d5RealPlayerProof=NoCoverage` and `mayRunLocally=false`. The six critical unproven cases C07/C08/C09/C10/C13/C17 are present. Historical B1 fixture paths are pinned to the source inventory; no old oneuse-12 result was relabeled as a D5 Player success. There is no D5-B runnable coordinator or real D5 native fault-producer proven by these files. The contract preserves `D5A=ApprovedByUser`, `D5B=NotAuthorized`, closed WEB_TO_LOCAL and unaccepted R03.

### IR-D5A-04 — MEDIUM: historical evidence-root protection is not a complete Local admission check

**Exact source:** `Tools/AssemblyShadow/R03IR/D5Admission/d5a_source_gate.py:233–246`, `300–335`, and `test_d5a_source_gate.py:214–233`.

The helper `read_only_output_guard(roots, output, historical=())` takes **an optional historical-roots list defaulting to empty**, and the CLI `inspect` never calls the helper or takes an output path. The current `test_44_existing_historical_root_rejected` constructs an **already existing output path** and correctly fails because `not output.exists()` is false; it does **not** test exclusion of a *new child directory inside an existing historical evidence root*. In a source-derived example (not a claimed locally executed repro), a fresh `.../old-oneuse12/R03-B2-D5-new` could pass when the historical root is omitted and the path is outside the four checkouts.

This finding **does not invalidate the D5-A read-only source receipt**, which makes no output-root acceptance claim and has no authorized Local output. It **does invalidate treating the helper or its current three tests as sufficient evidence-root custody for D5-B**. Before any Local execution candidate: require the full historical and source-root list rather than an optional default; test exact/nested/sibling/alias/symlink/absent/root-consumption cases; ensure a new D5-B admission path actually calls it, and create the root exclusively only after successful read-only admission.

### IR-D5A-05 — MEDIUM: no live-remote/head freshness proof, only caller-supplied exact commit

**Exact source:** `d5a_source_gate.py:248–335`, workflow `.github/workflows/r03-b2-d5a-source-admission.yml` expected `github.sha` argument.

`validate_git_checkout` compares `git rev-parse HEAD` against a **caller-provided** `--expected-demo-head`; a detached checkout is deliberately allowed. The configured `origin` URL is checked for an exact name but the tool does not perform `git ls-remote`, consult a separately reviewed Local handoff pin or compare with GitHub's live branch HEAD. Thus a self-consistent **older demo commit** with the same 33 pinned files could pass if the caller supplies that older hash. The current **CI is still valid**, because GitHub Actions independently supplied the actual triggering `github.sha`; it never claimed to prove future live-head freshness.

Before converting this source gate into a **D5-B Local admission authority**, bind the expected demo SHA to a separately approved, immutable, reviewed four-repo handoff tuple, and verify at handoff creation that the SHA is the intended then-current remote branch HEAD. On the Local machine, verify the configured remotes and fetch/compare the approved source refs without silently accepting a stale or unrelated checkout. Do not simply replace the source-gate input with whatever local HEAD happens to be. Distinguish **reviewed exact commit** from **current live branch HEAD** when the branch later advances.

### IR-D5A-06 — HIGH / deferred integration boundary: no real linked Player or full VM proof

The 47 Python tests exercise source strings, manifest mutations, file identity and path guard predicates; they do **not** build the actual production `AssemblyShadow.cpp` translation unit or produce/execute a real Unity Player. D5-C07/C08/C09/C10/C13/C17 do not yet have authenticated, deterministic real native/Player fault producers. The 12-path proposed native install roster is not a Bee/native source install receipt, and a package file's pinned Git blob is not a proof of actual generated HybridCLR version or binary linkage. Real macOS arm64 Unity 2022.3.62f2 IL2CPP, 32-bit ABI, GC/shutdown, and first-recovery V2 remain **NotRun**.

These are **explicitly declared deferred requirements**, not fictitious passing tests. A new D5-B implementation/review must establish test producers and exact source→installed native files→compiled objects→linked binary→PID/evidence joins before the user separately approves Local execution.

## 4. Final gate decision

**`D5AIndependentReview=PassD5AForD5BPreparation`.** No **current D5-A source-only** critical defect was found in the exact pinned code and raw CI evidence; this pass is limited to evidence for development of the next candidate, **not authorization to run it**. Medium findings IR-D5A-04/05 are mandatory pre-Local corrections and IR-D5A-06 is high pending real Player/VM coverage. The gate **does not certify** full evidence-root admission, live remote freshness, actual Unity native installation or Player acceptance. If the next Primary scope cannot implement these guards and real fixture provenance, return a Blocked D5-B proposal rather than issuing an executable handoff.

Next permissible work: **separately tasked D5-B preparation and independent source/fixture review**, followed by an **explicit user D5-B Local execution decision**. `D1IndependentReview=WaivedByUser` (not passed), `D2IndependentReview=PassD2ForD3`, `D3IndependentReview=PassD3ForD4`, `D4IndependentReview=PassD4ForNextGate`, `D5A=CompleteSourceCI`, `D5B=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. No D6, H2/M08A/X02/SNAP-01, Local Player commands or Human Review Gate.
