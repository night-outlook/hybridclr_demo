> **Independent review completed — `ReturnRequired` (2026-11-24 UTC).** [Read full design → source → 53-test → raw-CI report](D5B_LOCAL_DRY_ADMISSION_INDEPENDENT_REVIEW_2026-11-24.md). Three future one-use receipt-writer findings return to Primary Implementation. Current approval anchor remains None and Local remains CLOSED. The original source tuple and review request are preserved below for provenance.

---
# Independent review request — D5-B prospective physical dry-admission source/tooling

**Status at request publication: PENDING; now resolved `ReturnRequired` (see independent report).** Independent reviewer (separate from Primary and Local), please perform an evidence-based review of the **new physical D5-B dry-admission design → source → 53 tests → exact raw CI**. Do not merely endorse Primary's report. Do not invoke Local Unity/IL2CPP/Player, open `WEB_TO_LOCAL`, authorize execution, begin D5-C/D or later milestones, or approve a Human Review Gate.

## 1. Required read order and immutable source tuple

First read `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, and `Handoff/WEB_TO_LOCAL.md` on branch `codex/assembly-shadow-r01b-h1`; then [source review predecessor](D5B_RR5_R2_INDEPENDENT_REREVIEW_2026-11-24.md), [D5-B design and phases](D5B_LOCAL_DRY_ADMISSION_DESIGN_2026-11-24.md), and [Primary implementation/CI record](D5B_LOCAL_DRY_ADMISSION_PRIMARY_IMPLEMENTATION_2026-11-24.md). Older D5-A/B/B1 plans are historical comparators; do not replace the current reviewed C10 source tuple with stale native pins.

**Review actual implementation at immutable code commit** `hybridclr_demo@2d0039192d1264d5799411668acd7e911b28b830` (newer demo branch HEAD may have documentation commits), with unchanged `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, and `il2cpp_plus@1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` on the same branch. Verify canonical identities and source blob readbacks through GitHub Connector, not a mutable summary.

New five implementation files to inspect:

| Path | Expected Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `1a000360005647a2534bad15af9b32ab95887c22` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `b4c345bdb9a4f327b53ef9682a0e4a6c138715e6` |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `a98825583703766b0c601ad9182bd79e599f803a` |

## 2. Mandatory independent checks

1. **Exact review lineage / source:** inspect the proposed plan, prior R2 `PassSourcePreflightOnly` SHA+Git blob, 16 C10 native/demo link-source blobs, 14 C10 evidence-producer blobs, five historical comparator blobs and R2 independent review document blob. Check that `source.inspect` is really invoked and its result validated. Verify the separate **live Git `ls-remote`** source SHA for all four roles and the R2 demo code `merge-base --is-ancestor` rule; a caller-supplied demo SHA must not masquerade as authenticated live remote evidence.
2. **Physical source/output custody:** review `canonical_dir`, `check_custody`, `inspect_original_s`, `exact_remote_head` and `inspect`. The complete historical map has six mandatory physical paths and all four B1 children must be distinct descendants of the B1 base, with original-S clean fixed commit, symlink/`..` rejection, external disjoint and absent one-use output. Test output reuse, aliasing, missing roles, source/historical overlap, stale remote branch and wrong original-S. No writes or local process-spawning on a denied request.
3. **Mac environment:** verify source behavior of `inspect_machine`, `read_only_host_tool`, Xcode version, `xcrun` SDK physical target (including normal symlink), clang/license probes, actual Unity executable SHA-256, 20 GiB check, and **explicit `NotRun`** Unity-version/native IL2CPP evidence. The CI tests are on Ubuntu and mock macOS tools; they are **not** a real macOS admission or real SDK/Unity validation.
4. **Approval and one-use outputs:** verify `APPROVED_EXECUTION_ENVELOPE_BLOB=None` is the production hard gate in BOTH `--mode execute` and `seal_oneuse_dry_admission`, and that a caller-supplied forged JSON/env cannot grant approval. Inspect `approved_envelope` source schema checks, all six approved history paths, exact four commits/Unity hash, exclusive one-use `ADMISSION.json`/`CELLS.json`/`LOCAL_BATCH_RESULT.json`/`MANIFEST.json`, and 18/18 `NoCoverage`. The positive sealer test uses temporary paths plus a **mocked synthetic approval constant only** and must not be promoted to a real approved handoff.
5. **Scope non-escalation:** this is ONLY D5-B physical dry admission; there is no Unity `BuildPipeline`, IL2CPP Player process, C10 real `MethodInfo` or GC, completed P0-P6/fault producer, prior S actual archive audit or native source-to-Bee/Mach-O provenance. It cannot approve Local execution, D5-C/D, R03, H2 or Human Review Gate. Check `WEB_TO_LOCAL` remains CLOSED and no Local-owned evidence file was modified.
6. **Raw CI and prior attempts:** independently retrieve [final exact-source GitHub Actions 45357502504](https://github.com/night-outlook/hybridclr_demo/actions/runs/45357502504), attempt 1, raw job **`138318876333`**, verify exact demo code commit, **53/53 Python tests**, no unauthorized tool invocation, `run_d5_local.py --mode execute` exit 2 `NotAuthorized` and `outputCreated=false`. Also inspect first [source-only 45-test run 45356784265](https://github.com/night-outlook/hybridclr_demo/actions/runs/45356784265), prior 46/52/53-pass code runs as historical only, and the failed intermediate runs `45356977530`, `45356938323`, `45357154261`, `45357224002`, `45357282116` without reclassifying them as passes.

## 3. Independent verdict and authority

Issue **`PassDryAdmissionSourceOnly`** (bounded source/CI approval for future proposal/independent user decision) or **`ReturnRequired`** with exact code lines, path and a reproducible source/host counterexample. A `PassDryAdmissionSourceOnly` **must not** fill the empty user-approval envelope, open `WEB_TO_LOCAL`, run Local tools or claim D5-C/D approval. Nontrivial findings return to Primary Implementation; any actual Local run needs a new exact pushed four-commit handoff, separately verified user approval and a new independently pinned executable envelope.

**Current authority remains:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; all 18 real D5 Player cells `NoCoverage`; Unity/IL2CPP/native full VM/Bee/link/GC/PID/Player `NotRun`.