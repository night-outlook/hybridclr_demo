# R03 D5-B — Primary physical dry-admission source implementation and raw-CI evidence

**Status:** `D5BDryAdmissionPrimary=SourceOnlyCIComplete_PendingIndependentReview`. **Not Local execution approval.** Date: 2026-11-24 UTC. Scope: the standalone D5-B **physical root / source / environment dry-admission** candidate and source-host tests, not D5-C native Unity builds or D5-D Player cases. See [design and phased plan](D5B_LOCAL_DRY_ADMISSION_DESIGN_2026-11-24.md) and predecessor independently [passed D5-B RR5 R2 Git source preflight](D5B_RR5_R2_INDEPENDENT_REREVIEW_2026-11-24.md).

## 1. Pushed immutable implementation source tuple

| Repository, branch `codex/assembly-shadow-r01b-h1` | Code/test source commit | Role |
|---|---|---|
| `night-outlook/hybridclr_demo` | **`2d0039192d1264d5799411668acd7e911b28b830`** | New D5Local admission/runner/tools and GitHub CI. Later demo commits are documentation only; check them separately |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Interpreter/Runtime pinned unchanged |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unity package pinned unchanged |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Actual C10 candidate pinned unchanged |

GitHub Connector readback verified exact new implementation Git blob IDs:

| File | Exact Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `1a000360005647a2534bad15af9b32ab95887c22` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `b4c345bdb9a4f327b53ef9682a0e4a6c138715e6` |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `a98825583703766b0c601ad9182bd79e599f803a` |

All changes are **additive to `hybridclr_demo`**; no native, HybridCLR fork, historical B1/D5-A/B runner or D5-C10 runtime test producer was modified. The proposal explicitly carries the predecessor source preflight code `54780df40bddfc9d050b87f64fcd259475d99ba4`, proposal blob `9956ea49656dc8337f9ab177c40faf29ea20c397`, independent review blob `5a1e3690de6f44494bc718284315b8d9d9ced12a` and C10 pinset `66b2e83f8cab4debb71af36d4bcd5eecd80b5629`.

## 2. Code implemented

**Independent physical source gate** — `inspect_source_and_remote` requires the existing reviewed 16 C10 link + 14 source-producer + five historical comparator Git blob checks, checks the R2 independent review document against its exact Git blob, then uses `git ls-remote --exit-code origin refs/heads/codex/assembly-shadow-r01b-h1` to match **each of the four** immutable review SHA identities. It additionally requires `git merge-base --is-ancestor` of the separately passed R2 source code to the frozen demo SHA. Local HEAD/clean state and canonical remotes are checked by the predecessor source preflight. A caller-supplied `--expected-demo-head` alone is *not* sufficient for this later live remote join.

**Physical and historical custody** — six mandatory disjoint historical roots, canonical non-symlink four-repo sibling checkouts, immutable clean original-S demo commit `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, four distinct B1 historical evidence subroles under the original B1 base, complete workspace/historical disjointness, absent one-use output root and an external parent. No evidence file or directory is created by `--mode preview`.

**macOS environment checks** — platform `darwin`/arm64, executable real Unity file+SHA-256, >=20 GiB disk, installed Xcode and `xcrun`, read-only `xcodebuild -version`, actual macOS SDK path (normal `MacOSX.sdk` symlink resolved), clang executable, `xcodebuild -license check`. The CLI **does not launch Unity, IL2CPP, a C++ compilation or Player**. Unity 2022.3.62f2 version/IL2CPP module and actual Bee/source-to-binary parity must be verified in a future authorized BuildPipeline; they remain `NotRun` here.

**Hard authority / one-use output** — `APPROVED_EXECUTION_ENVELOPE_BLOB=None` in production source; both public `run_d5_local.py --mode execute` and the inner `seal_oneuse_dry_admission()` reject absent immutable approval before output creation. A hypothetical future reviewed `R03D5BApprovedDryAdmissionEnvelopeV1` must bind all four SHAs, the full six historical physical roots, external destination, Unity executable SHA-256, source-review/user approvals and exact dry-only scope. Only in a future newly reviewed authorized revision could the sealer write `ADMISSION.json`, `CELLS.json`, `LOCAL_BATCH_RESULT.json` and `MANIFEST.json` to a fresh exclusive root, with **18/18 cells `NoCoverage`**. Unit tests that exercise this path use temporary filesystem and a **mocked test-only approval anchor**. No genuine authorization exists in this commit.

**No D5-C/D5-D execution** — `run_d5_local.py` is an explicit *dry-admission-only* front-end, not a full build-orchestration harness. The already existing `R03D5Build.cs` and C10 candidate inputs have not been built/linked; no fake assertion that all 18 Player fault producers exist. Future concrete D5-C source installation/generation, ON/OFF Unity build, Mach-O binary provenance, and actual D5-D fresh Player cases require their own new stage and independent review.

## 3. Source-host validation, exact CI and failed history

**Final exact-code CI:** [GitHub Actions run 45357502504](https://github.com/night-outlook/hybridclr_demo/actions/runs/45357502504), attempt 1, **1/1 PASS**, head `hybridclr_demo@2d0039192d1264d5799411668acd7e911b28b830`, raw job `138318876333`. The raw log was independently fetched via GitHub Connector: **253 lines / 25,058 bytes**, `Ran 53 tests in 0.043s`, then `OK`, no unexpected Python test failures. It also invokes the public `run_d5_local.py --mode execute --approved-envelope <unapproved nonexistent file>` and asserts **exit 2** with `result=NotAuthorized`, `outputCreated=false`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `D5BLocalExecution=NotAuthorized`, `R03Accepted=false`. The unapproved file was never created and no Unity or Player was launched. This is **SourceOnlyDeniedLocalExecution**, not a Local batch result.

Tests cover: plan Git blob and immutable prior R2 gate; all 18 no-coverage slots; required six physical roots and B1 subtree; symlink, overlap, output reuse, original S identity; one-line live branch SHA/ref parsing; remote drift; four-reference joins (simulated, not live GitHub); macOS/Xcode version, SDK symlink/clang/license and disk (synthetic/mocked on Ubuntu); source preflight predecessor requirement; frozen future envelope SHA, review/user flags and exact source/historical paths; one-use receipt exclusivity in a **temporary directory**; direct sealer and CLI hard-stop without approval. These tests were **not** executed against a real macOS Unity installation.

Some intermediate pushed source revisions had failed CI runs due to sequential source/expected-test updates; do not reuse or reclassify these as pass: `45356977530`, `45356938323`, `45357154261`, `45357224002`, `45357282116`. Earlier scoped source-host runs `45356784265`, `45357004974`, `45357178189`, `45357307884`, `45357475211` succeeded at their own **earlier** commits, not the final wrapper/CI revision. Only **45357502504** is attached to this exact final D5Local source tuple. No historical C10 or B1 Player evidence has been promoted.

## 4. Residual risks and next required independent gate

**Next action is a separate independent source/design/raw-CI review of this newly prepared D5-B dry-admission tool**, not a Local run. The reviewer should examine (a) the exact live Git-ref and original-S proof, (b) all six physical historical roots and output path canonicality, (c) Xcode SDK alias/host prerequisite behavior, (d) source plan Git blob anchors, (e) explicit approval-envelope and hard-block semantics, (f) direct `seal` helper and exclusive file writer, (g) 53 source-only test bodies, (h) raw final CI and failure history. Result may be `PassDryAdmissionSourceOnly` or `ReturnRequired`; **not** Local execution authority. An independent pass would permit later planning of a separately pinned user-approved Local dry run, not self-approve it.

**Unverified:** actual physical Local roots/Unity version/IL2CPP module on macOS; real Xcode/SDK/clang/license/disk on Local; full native `AssemblyShadow.cpp` compilation and Bee DAG; linked nine exports/allocator exclusion; B1 original-S physical archive custody; real P0–P6 method-guard/GC first-error/PID/argv/exit and all 18 D5 Player cells. These remain `NotRun`, `Unavailable` or `NoCoverage` until future real execution is explicitly approved and observed. The source-host suite does not satisfy any real Player acceptance gate.

**Authority unchanged:** `APPROVED_EXECUTION_ENVELOPE_BLOB=None`, `APPROVED_LOCAL_HANDOFF_BLOB=None`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `D5BLocalExecution=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. No Local commands, D5-C/D, D6/H2/M08A/X02/SNAP-01 or Human Review Gate are authorized by this delivery.