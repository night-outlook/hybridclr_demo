# R03 B2 D5-B — Independent review: source-custody preparation

**Decision: `PassD5BCustodyForProducerPreparation` — STRICTLY source-only / synthetic custody scope.** Review date: 2026-11-20. Reviewer role: independent of Primary Implementation and Local Validation. This report independently examines actual source and raw CI evidence at fixed revisions, not merely the [Primary report](D5B_SOURCE_CUSTODY_PRIMARY_REVIEW_2026-11-20.md).

**Authorization boundary:** This decision permits a **separately tasked Primary Implementation phase for D5-B real-Player test-producer/native-link preparation**, not execution of D5-B Local Validation. It does **not** approve Unity/IL2CPP compilation, Player launches, SDK execution, source installation, actual remote/local handoff authentication, H2, R03 acceptance, D6 or the Human Review Gate. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `D5BLocalExecution=NotAuthorized`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.

## 1. Independently inspected source authority

All four repos use `codex/assembly-shadow-r01b-h1`. Remote branch HEADs were independently retrieved through the GitHub Connector before the review publication:

| Repository | Remote HEAD at review bootstrap | Review role |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `3d824e1b6fc7a25f73cb9a1feb6b26bb65efc1ae` | **Actual source tested at `2843c545ef1597f866ebd329ff27d4f73d58ba90`**, followed by exactly five documentation-only commits |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Unchanged D3 Runtime/Codec |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged HybridCLR Unity package |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` | Unchanged D2–D4 native implementation |

GitHub compare `hybridclr_demo@b9776f7dc87170ba08bfed9021c0ee8546bceccf...3d824e1b6fc7a25f73cb9a1feb6b26bb65efc1ae`: **15 commits**; new D5-B source-custody manifest/script/tests and one source-only workflow, plus README/handoff/review/plan documents. **Zero modifications** to older B1 `current_native_candidate.json`, `current_native_source_gate.py`, `run_current_native_validation_cycle.py`, `run_captured_generic_local.py`, oneuse-12 evidence, D5-A source files, and the three production repos. Compare of CI-tested `2843c...3d824...` is five **documentation-only** commits; no undocumented post-CI code drift.

Actual four new tested files and reviewed Git blobs:

| File | Actual Git blob |
| --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_preparation_v1.json` | `202c7847e4ae741902162391a4e4bd7a66e33c2c` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `Tools/AssemblyShadow/R03IR/D5Admission/test_d5b_custody_authority.py` | `d89da965d336ddc50e906036deecc5d8a18f5e46` |
| `.github/workflows/r03-b2-d5b-custody-preparation.yml` | `5c988dbd880797b2b6841874b3ac2767fb4a164a` |

The previously recorded disposable connector write/readback branch `codex/smoke-d5b-admission-20261120-b01` independently resolves to **`3c2d0253bb9b4fa2fcffa34bb5ed8d33300fac97`**; it remains separate from the reviewed feature HEAD. The connector reports read/write permissions for all four canonical repos. No production source was modified during this independent review.

I reopened and compared the exact D5-A [review](D5A_INDEPENDENT_SOURCE_REVIEW_2026-11-20.md), [D5-B source review request](D5B_SOURCE_CUSTODY_INDEPENDENT_REVIEW_REQUEST_2026-11-20.md), [Primary report](D5B_SOURCE_CUSTODY_PRIMARY_REVIEW_2026-11-20.md), [producer/native-link plan](D5B_REAL_PLAYER_PRODUCER_AND_LINK_PLAN_2026-11-20.md), `README.md`, and `WEB_TO_LOCAL.md` with the four tested source files and raw evidence.

## 2. Actual CI verified independently

[**GitHub Actions run 44725519765**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44725519765), exact `hybridclr_demo@2843c545ef1597f866ebd329ff27d4f73d58ba90`, **attempt 1 `completed/success`, 2/2 jobs success**. I fetched both separate raw job logs, inspected `test_01` through `test_50` lines in each, the full test result summary, the source-only CLI preview, and the terminal no-Local receipt.

| Host | Job ID | Actual test results | Receipt |
| --- | --- | --- | --- |
| Ubuntu 24.04 | `136251811066` | **50/50 PASS**, `Ran 50 tests ... OK`, no unexpected errors | `PreparedSourceOnly_NoLocalExecution`; 18 `NoCoverage` |
| macOS 15 | `136251811428` | **50/50 PASS**, `Ran 50 tests ... OK`, no unexpected errors | `PreparedSourceOnly_NoLocalExecution`; 18 `NoCoverage` |
| **Aggregate** | | **100 passing Python source/synthetic tests** | **Two no-Local preview receipts** |

Tested categories: immutable source/proposal authority, incorrect approval flags, six mandatory historical root roles, actual synthetic directory nesting/alias/symlinks/consumed-root rejection, single exact remote-ref parser, missing/stale/wrong source pins, 12 native file-copy equality cases and malformed extra host allocator inclusion, and mocked four-remote readback with test-only patched approval blob.

Crucial distinctions:
- `test_49` and `test_50` monkeypatch both the **currently None** approval blob and the Git command function. They **did not** execute `git ls-remote` against real source remotes. The receipt accurately records `remoteSourceVerification=NotRun`.
- The 12 files in the copy test are **a synthetic test-directory copy**, not actual installed `libil2cpp`, Unity Bee compiled source, generated symbols or a Player. The receipt accurately reports `nativeUnityInstallation=NotRun`, `actualBeeCompilerInvoked=false`, `compiledTranslationUnits=0` and `actualPlayerLinked=false`.
- `UnityOrPlayerExecuted=false`, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION` in the CLI/CI. All **18 D5-Cxx Player cells remain `NoCoverage`**.

Earlier Actions run statuses independently confirmed and **not retroactively promoted**: `44724709973` **failure** (13-vs-12 source-copy input mismatch), `44725007578` **success** (43 cases), `44725311446` **success** (43 cases), `44725472952` **failure** (outdated 43-case CI threshold after adding seven tests), `44725519765` **final 50-case success**.

## 3. Independent source findings

### IR-D5B-C01 — PASS, bounded: mandatory historical-root custody fixes the D5-A empty-history flaw

In actual `d5b_custody_authority.py`, `check_proposed_custody(workspace,roots,historical_roots,evidence_parent,oneuse_name)` has **no optional default** for `historical_roots`; it requires **exactly six** role names: `originalS`, `b1EvidenceBase`, `b1Oneuse12`, `b1NativeHostRaw`, `b1B2HostRaw`, `b1Preflight`. Both source and historical input directories must be existing and physically canonical. Four source roots must be distinct children of the workspace, prior B1 roles must be children of the declared B1 base, and the output parent plus absent named output must be disjoint from **the entire workspace and all declared historical roots**.

This directly covers the D5-A finding where `historical=()` could omit the old evidence base: the new negative tests create a genuinely **new prospective path within an old B1 root** (and inside an original S root) and prove it is rejected, not merely rejected because the old output already existed. Alias/symlink, existing leaf, missing root roles, noncanonical path, duplicate source root and traversal cases also reject.

**Boundary:** the historical role-to-path mapping is still **caller-supplied in these synthetic tests**, not independently authenticated against a real macOS source/previous Local evidence catalog. An unrelated but physically valid set of six directories could satisfy the source-level shape checks. No exclusive first-create/reservation is implemented; a read-only absent-path test is susceptible to **time-of-check/time-of-use** changes if reused as a future execution gate. These are **mandatory before actual D5-B Local authority**, not defects in this deliberately read-only source-preparation checkpoint.

### IR-D5B-C02 — PASS, bounded: future remote source verification is hard-stopped without an approved immutable handoff

The production source sets `APPROVED_LOCAL_HANDOFF_BLOB = None`, and `read_independently_approved_handoff(raw)` immediately refuses when it remains None. Even a caller-provided JSON with `independentReview=Passed`, `userD5BExecutionApproval=ExplicitlyApproved`, and an exact-looking source pin is **not** sufficient. A future revised code pin would require byte-exact Git blob comparison before parsing the handoff, four pinned commit SHA strings and all six root-role bindings.

`verify_live_source_heads` then intends to check real physical local roots, exact checkout `HEAD`, canonical configured `origin`, clean working tree and **one** precise `git ls-remote --exit-code origin refs/heads/codex/assembly-shadow-r01b-h1` SHA equal to the reviewed immutable commit. The source of the current method does not allow an unconstrained CLI argument to become the review authority.

**Boundary:** currently the method cannot be successfully invoked under the production configuration. All positive remote checks use **mocked Git results and a test-only patched approval hash**, not actual network authority. Before Local execution, a new reviewed code revision must bind an actual approved handoff blob, authenticate its physical historical paths and current Git ref policy, ensure source file/blob admission is integrated, then perform a real readback against those remotes. The future handoff must distinguish immutable reviewed commits from a moving feature branch and fail closed if they diverge. A JSON flag is never independent proof of a human action by itself; the reviewed blob is the intended external authority boundary.

### IR-D5B-C03 — PASS/source only: 12 actual native Git source identities confirmed, not compiled installation

I independently read the D5-A manifest and fetched each **12 of 12** intended `libil2cpp` native source/header Git blobs at `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`. Every remote file blob matches the D5-A expected identity. This includes `AssemblyShadow.cpp`, `AssemblyShadowProcessSnapshotOwner.h`, `AssemblyShadowPublicationPhaseReceipt.h`, `Assembly.cpp`, `MetadataCache.cpp`, `Runtime.cpp` and their required headers. All four required production translation units are present.

The standalone `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` containing global allocator operators is **excluded** from the 12-file intent list. The tested `check_native_file_copy` requires all 12 expected Git blobs and exact byte equality for a synthetic copy, and rejects missing/corrupted/symlinked inputs and the forbidden file at the explicit `NativeHostTests` path.

**Boundary:** the helper does not walk a full native installation directory, scan all linked object/source files for rogue global allocation overrides, or provide a real Unity build-roster receipt. A copied allocator implementation at an unexpected path would require a complete input/symbol audit to detect. This remains the explicitly planned D5-B native installation and linker evidence task, not an accomplished build.

### IR-D5B-C04 — SOURCE-ONLY PASS: no Local execution or acceptance authority is exposed

The only supported CLI option is `--source-preview-only`, which reads the immutable proposal JSON and emits `PreparedSourceOnly_NoLocalExecution`. It neither creates an evidence root, invokes Unity or a build coordinator, nor claims to have checked real Local paths/remote refs. The old B1 source gate and oneuse-12 results remain unchanged, and the canonical `WEB_TO_LOCAL.md` is explicitly closed. The new future real-Player producer and native-link document is a plan, **not an installed fault producer**.

There is no newly implemented D5-B `run_d5_local.py` or linked P3/P4/P5/P6 real-Player test assembly in this reviewed source, and nothing in this source-only run verifies GC, VM epoch, 32-bit atomics, V1/B1/V2 first recovery, or actual Player behavior.

## 4. Mandatory next-stage work, NOT passed here

| ID | Severity for future Local | Required before Local authorization |
| --- | --- | --- |
| **IR-D5B-N01** | High | Independently bind the **actual** historical root paths to an approved handoff/source evidence catalog and call the custody guard in the future Local coordinator; never accept arbitrary six path roles as proven historical identity |
| **IR-D5B-N02** | High | Implement **atomic/exclusive fresh one-use output creation** only after source/root admission, rechecking disjointness and identity at the creation boundary; avoid a check→create path race |
| **IR-D5B-N03** | High | Create an independently reviewed byte-identical **approved Local handoff**, pin and review its source tuple in a new code revision, and perform actual `git ls-remote` checks against four canonical remotes. No JSON-only approval, unreviewed `HEAD` argument or self-signed local branch equality |
| **IR-D5B-N04** | High | Validate installed `libil2cpp`, full native compile-input/Bee DAG and **linked GameAssembly symbol** inventory including absence of any global allocator override from host tests. Synthetic 12-file copies cannot close this |
| **IR-D5B-N05** | Critical acceptance gap | Implement reviewed **test-only** P3/P4/P5/P6 fault-producer and P5→P6 concurrent method admission probes; observe them in **real** fresh Unity/IL2CPP Players. All 18 D5 Player cases currently `NoCoverage` |
| **IR-D5B-N06** | High acceptance gap | Real GC/shutdown, native/managed V1/B1/V2 readback, platform ABI/32-bit and additional requested targets remain NotRun; require separate execution evidence/coverage decisions |

**Independent decision rationale:** No source-custody defect that invalidates the **narrow, read-only preparation deliverable** was found after authenticating actual files and both CI logs. The previous D5-A historical-root and caller-supplied-commit issues now have **fail-closed preparation primitives**, while their **integration with a real reviewed Local handoff is deliberately absent**. The remaining high/critical gaps bar Local execution, but are not evidence to falsely reject a bounded no-Local source-only milestone.

**Final disposition: `D5BSourceCustodyIndependentReview=PassD5BCustodyForProducerPreparation`.** This does **not** imply `D5BLocalValidationPassed`. Next permitted activity is **a separately tasked Primary Implementation of real-Player producer/native-link preparation**, followed by independent source/test review and explicit user permission before any Local Unity/IL2CPP/Player. `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. No D6/H2/M08A/X02/SNAP-01/Human Review Gate.
