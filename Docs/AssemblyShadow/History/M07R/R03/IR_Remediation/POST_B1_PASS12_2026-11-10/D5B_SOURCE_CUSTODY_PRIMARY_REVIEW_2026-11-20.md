# R03 B2 D5-B — Primary review: historical-root and remote-source custody (source-only)

**Primary disposition:** `D5BSourceCustody=ImplementedSourceCI`; `D5BIndependentReview=Pending`; `D5BLocalExecution=NotAuthorized`. Date: 2026-11-20 UTC. This document records a **bounded D5-B preparation slice**, not a completed D5-B Local Validation runner, independent review, actual Unity/IL2CPP build or Player result. It follows [independent D5-A `PassD5AForD5BPreparation`](D5A_INDEPENDENT_SOURCE_REVIEW_2026-11-20.md) and addresses the two specific pre-Local admission findings in that report.

## 1. Scope and exact four-repository source authority

All repositories use `codex/assembly-shadow-r01b-h1`. Source/CI test `hybridclr_demo@2843c545ef1597f866ebd329ff27d4f73d58ba90` (later documentation-only HEAD separately verified). Production pins unchanged:
- `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`
- `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`
- `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`

**Affected repository:** `night-outlook/hybridclr_demo` only. Source-only files added beneath `Tools/AssemblyShadow/R03IR/D5Admission`, one GitHub Actions workflow and documentation under `Docs/AssemblyShadow`. Historical B1 14/46 source gate and runner, D5-A implementation, original-S, oneuse-12 evidence, V1/B1/R02 and three runtime repositories were not intentionally modified. Verify with actual Git compare before accepting this report.

A fresh GitHub Connector disposable-branch write/readback test used `codex/smoke-d5b-admission-20261120-b01`, based on demo feature commit `b9776f7dc87170ba08bfed9021c0ee8546bceccf`, and created smoke commit `3c2d0253bb9b4fa2fcffa34bb5ed8d33300fac97`; the remote branch HEAD and file content matched. The connector lacks a branch-delete action; **disposable smoke branch remains** and is not a product or handoff commit.

## 2. Implemented source code and independent-review targets

| File | Exact source Git blob | Purpose |
| --- | --- | --- |
| `D5Admission/d5b_preparation_v1.json` | `202c7847e4ae741902162391a4e4bd7a66e33c2c` | Immutable proposal-only record: current reviewed baseline, fixed 3 runtime SHA pins, six mandatory historical root roles, 12 required native source inputs and four translation units, 18 `NoCoverage` Player cells, explicitly **no D5-B Local authority** |
| `D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` | No-write source preview, strict proposed history/output custody, immutable reviewed-handoff identity API, real `git ls-remote` source-ref verification **hard-stopped without a separate approval blob**, and synthetic native file-copy check |
| `D5Admission/test_d5b_custody_authority.py` | `d89da965d336ddc50e906036deecc5d8a18f5e46` | 50 Python positive/negative tests including nested/alias historical outputs, full reviewed source-ref parser, missing/fake approval, mutations to native source copy, and synthetic mocked remote listings |
| `.github/workflows/r03-b2-d5b-custody-preparation.yml` | `5c988dbd880797b2b6841874b3ac2767fb4a164a` | Two-OS GitHub Actions source-only checkouts (demo triggering SHA, exact `il2cpp_plus`, `hybridclr`, `hybridclr_unity` commits), 50 tests/job, CLI preview with explicit `NotRun` flags; **never launches Unity or Player** |

**IR-D5A historical-root follow-up:** `check_proposed_custody` now **requires** all six roles `originalS`, `b1EvidenceBase`, `b1Oneuse12`, `b1NativeHostRaw`, `b1B2HostRaw`, `b1Preflight` (no default empty list), four distinct sibling Git roots and an absent, physically canonical `R03-B2-D5-...` name. It rejects an output inside the complete source workspace, any historical root or child, an original S child, existing/consumed path, symlinked parent or output, path traversal, malformed custody relationship and incomplete historical inventory. The standalone function remains **a read-only synthetic/test contract**; **no actual macOS historical paths were verified in this Primary environment**, and it is not called by an authorized Local runner.

**IR-D5A remote-authority follow-up:** `read_independently_approved_handoff` refuses any record unless its **actual bytes equal a separately pinned Git blob** and the record contains exact four source pins, six historical roots, an independent review status and explicit user Local approval. The current production constant is deliberately **`APPROVED_LOCAL_HANDOFF_BLOB = None`**, so the real `verify_live_source_heads` can never return an approval under the current source. The *future* reviewed Local implementation, requiring a new code-review/pin update, will use `git ls-remote --exit-code origin refs/heads/codex/assembly-shadow-r01b-h1`, compare the actual single remote SHA against the reviewed handoff SHA, and separately check physical local Git HEAD, remote URL, canonical checkout and dirty state. The tests use **synthetic mocked ref output**, not an actual Local GitHub remote readback. An arbitrary caller-supplied SHA or a self-claimed JSON approval cannot authorize D5-B today.

**Native source-copy provenance:** `check_native_file_copy` compares all **12** D5-A pinned `libil2cpp` inputs from the D4 native checkout to synthetic copied files by exact bytes and Git blob. Missing/mutated/symlinked headers and inclusion of standalone `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` are rejected. The returned receipt expressly says `SyntheticNativeFileCopyOnly_NotUnityInstalled`, `actualBeeCompilerInvoked=false`, `compiledTranslationUnits=0` and `actualPlayerLinked=false`. It is **not** a Bee/compiler/linker/real-source-install manifest.

## 3. Exact source-only GitHub CI and error history

[**Final CI 44725519765**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44725519765) at demo `2843c545ef1597f866ebd329ff27d4f73d58ba90`, **completed/success, 2/2 jobs**, Ubuntu 24.04 (job `136251811066`) and macOS 15 (job `136251811428`). Both raw logs were read back directly, and each contains `test_01` through `test_50 ... ok`, **`Ran 50 tests ... OK`**, preview `PreparedSourceOnly_NoLocalExecution` and terminal `SourceTestsOnly` with `UnityOrPlayerExecuted=false`. Total **100 passing source/synthetic tests**, including positive exact-12-native-copy data and negative missing file, corrupted file, host allocator, wrong-handoff SHA, stale remote-ref and nested-historical-output cases. No unexpected test failure in the final logs.

**Historical CI results preserve their actual statuses:**
- `44724709973`: **failure**, initial synthetic-copy test mistakenly passed the 13-item D5-A source inventory to a 12-input installation check. Fixed by selecting exactly the 12 production input paths; the 13th remains the intentionally excluded standalone allocator host file.
- `44725007578`: **success**, 43 test cases before separate immutable-approval blob tests.
- `44725311446`: **success**, earlier 43-case guard implementation.
- `44725472952`: **failure** because new 50-case tests no longer matched the old 43-case workflow threshold; no suite failures claimed from that threshold.
- `44725519765`: **current final-source success**, 50 cases × 2 OS.

These results are source-only and use synthetic temp directories, fake remote-ref data and synthetic native copies. They do not prove an actual Local checkout, authentic macOS file roots, installed Unity sources, native C++ compilation/link or real Player fault behavior.

## 4. Primary findings and next boundary

| Finding | Current status | Follow-up |
| --- | --- | --- |
| D5B-P0-01 — six mandatory history roots, reject nested prior evidence | **PASS in source/synthetic tests** | Validate the actual reviewed macOS paths, all prior roots and absent oneuse directory in a separately authorized Local batch |
| D5B-P0-02 — remote branch must match immutable reviewed four-repo handoff | **Implemented but deliberately DISABLED** until approval Git blob exists | After independent D5-B review and separate user Local approval, pin approved handoff byte identity in a new reviewed code commit and perform actual `git ls-remote` readback |
| D5B-P0-03 — 12 native source installation *intent* files exclude host allocator | **PASS in synthetic copy tests** | Actual Unity install/Bee/compiler/linker source-to-binary proof **NotRun** |
| D5B-P0-04 — D5 native test fixture P3–P6 faults and concurrent method entry | **NotImplemented / NoCoverage** | Separate focused Primary producer implementation and independent review; see [producer/link plan](D5B_REAL_PLAYER_PRODUCER_AND_LINK_PLAN_2026-11-20.md) |
| D5B-P0-05 — native 32-bit, GC/VM shutdown, V2 transport, real Unity Player | **NotRun** | Remain blocked until separately approved Local Validation |

**Primary conclusion:** This is a **source-only D5-B admission hardening slice** and is ready for **independent D5-B source-custody review**, *not* for executable D5-B Local handoff, D5 completion or R03 acceptance. Even a positive independent review would authorize next scoped **Primary test-producer/native-link preparation only**; the user must separately authorize actual Local execution. Until then, `D5BIndependentReview=Pending`, `D5BLocalExecution=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
