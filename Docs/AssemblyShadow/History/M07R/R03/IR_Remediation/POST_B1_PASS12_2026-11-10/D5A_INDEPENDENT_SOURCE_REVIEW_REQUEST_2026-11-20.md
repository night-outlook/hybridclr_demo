# R03 B2 D5-A — independent source/CI review request

**Decision status: `D5AIndependentReview=Pending`.** This is a **request**, not an independent acceptance report or Primary self-approval. D5-A was explicitly approved by the user for source-only preparation. The review scope is only new D5-A source admissions, test-fixture provenance, old B1 isolation, and exact CI evidence. It must not authorize D5-B, real Unity/IL2CPP Player execution, R03 acceptance, H2 or Human Review Gate.

## 1. Exact read-first evidence

- [Primary D5-A implementation review](D5A_SOURCE_ADMISSION_PRIMARY_IMPLEMENTATION_REVIEW_2026-11-20.md).
- [User D5-A authorization](D5A_PRIMARY_IMPLEMENTATION_USER_APPROVAL_2026-11-20.md).
- [Independent D4 `PassD4ForNextGate`](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md).
- [D5 preapproval design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md) and [42-cell matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md).
- [D5-A staged Local procedure — **draft only**](D5A_STAGED_LOCAL_PROCEDURE_DRAFT_2026-11-20.md).
- [D5-A CI 44701514587](https://github.com/night-outlook/hybridclr_demo/actions/runs/44701514587), final source-test demo commit `6b3990e9bd6c0e7008f987ad93308b7d92d736a8`.

Branch for all: `codex/assembly-shadow-r01b-h1`. Production source tuple is `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`, with **no D5-A production edits**. Demo tested HEAD is fixed above; later docs-only commits must be compared explicitly to it, not silently promoted to CI-tested code.

Review these exact source files in `hybridclr_demo`:
- `Tools/AssemblyShadow/R03IR/D5Admission/d5a_candidate_v1.json` — Git blob `e15bdbff02de2dbb7adef42c39f363fe2d1f3b37`;
- `Tools/AssemblyShadow/R03IR/D5Admission/d5a_fixture_registry_v1.json` — blob `dbdfd51b85b1a8dfc9caedd9916842e1b0d042fc`;
- `Tools/AssemblyShadow/R03IR/D5Admission/d5a_source_gate.py` — blob `8e1fa91c8fe3158c7095dab2116f95af80fd1e00`;
- `Tools/AssemblyShadow/R03IR/D5Admission/test_d5a_source_gate.py` — blob `5fae18301dd96fda27cac9657968659cfd735a12`;
- `.github/workflows/r03-b2-d5a-source-admission.yml` — blob `f9f3da46eb37e2179adbe609800fe88e1f9aa8f0`.

## 2. Required independent verification

1. **Source authority and no-silent-profile-retarget:** authenticate each exact production HEAD/Git blob, dynamic full 40-hex demo HEAD supplied via CI, Git remote identity, clean status, real file bytes (not LFS pointers), and four sibling source roots. Prove a forged/cancelled/stale B1 candidate cannot be accepted by simply changing JSON or a command argument. Assess both source-scan and Git/file validation assumptions.
2. **Source isolation:** compare demo `a728c869481dd82f12526545749ecda4cfceaf3a` to the current feature HEAD; verify only new D5-A files/docs/workflow, with **zero changes** in `current_native_candidate.json`, `current_native_source_gate.py`, `run_current_native_validation_cycle.py`, `run_captured_generic_local.py`, original-S manifests, oneuse-12 receipts, or the three production repositories. The prior 14/46 admission must not be converted into a D4 proof.
3. **D2–D4 actual source and roster:** verify the 33-blob inventory and 12-`libil2cpp` source-install **intent** against real native files, including source/header `AssemblyShadow.h` and `dynamic_array.h`. Inspect P3/P4 Runtime observer sites, D3 terminal-before-UsageUnlock, D4 owner move before `s_active`, P5/P6/Complete and native D2 physical/CLI rollback. **Do not** treat source scans as actual native linking.
4. **Host allocator protection:** inspect `NativeHostTests/AssemblyShadowFirstFailureV2Host.cpp` containing global `operator new/delete`, confirm it is outside `libil2cpp` and excluded from proposed install source list. A real Unity Bee/build roster check remains `NotRun`.
5. **Fixture truthfulness:** independent audit all **18 D5-Cxx cases**, their phase tags and `NoCoverage`. In particular, C07/C08/C09/C10/C13/C17 have no real linked D5 Player fault producer. A historical B1/R03 test or D4 host result must not be accepted as a fresh D5 Player receipt. No Local commands are hidden in D5-A scripts.
6. **Actual CI logs:** independently read run `44701514587` (Ubuntu 24.04 job `136170773950`, macOS 15 job `136170774310`), verify each **47/47 Python tests**, 33 source blobs, 18 `NoCoverage` Player cells, expected-failing bad-demo-SHA control, no unexpected errors and explicit `UnityOrPlayerExecuted=false`. Earlier source runs `44701007296`, `44701183171`, `44701193894`, `44701484271` failed; `44701302399` passed at an obsolete 10-path native roster. Preserve historical statuses; do not call them all passing.
7. **No Local authority:** confirm D5-B remains unapproved, `WEB_TO_LOCAL` is *CLOSED*, and no `LOCAL_VALIDATION.md` or `RETURN_TO_WEB.md` file was edited. Source-only GitHub Actions is not a Unity/IL2CPP Player. A new D5-B source/actual test producer and independently approved Local handoff are still required.

## 3. Review decision requested

Choose **`PassD5AForD5BPreparation`**, **`ReturnRequired`**, or **`Blocked`**, with precise findings and source evidence. Even `PassD5AForD5BPreparation` would authorize only planning and implementation of a *separately scoped D5-B harness/producer candidate* after task assignment; it **must not** authorize a Local build, Player launch, source-migration to historical B1 pins, H2, R03 acceptance or Human Review Gate.

**Current gate at request:** `D5A_Primary=CompleteSourceCI`; `D5AIndependentReview=Pending`; `D5B=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`.
