# IR-R03-02 — Full changed native VM source-identity audit (2026-10-26)

**Primary source-only audit. No Unity, IL2CPP compiler, generated native build, Player execution, or independent full-stage R03 PASS.** Supplements [current-native design](DESIGN.md), [source review](PRIMARY_SOURCE_AUDIT.md), [oracle review](ORACLE_SOURCE_AUDIT_2026-10-26.md), and [independent re-review addendum](INDEPENDENT_REREVIEW_ADDENDUM.md).

## 1. Why ten pinned entry files alone were insufficient for review inventory

The focused historical R03 runner pins native `74dbdbea80d83923863303bd2b2c0a87f36541b1`; the source-only current-native candidate pins `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. The GitHub Connector compared those immutable native commits and returned **147 commits ahead**, **0 behind**, and **125 changed paths**:

| Changed-path surface | Paths |
| --- | ---: |
| `libil2cpp/vm/` native sources/headers/inlines | **42** |
| `tools/` diagnostic fixtures and runners | **59** |
| `.github/workflows/` | **24** |
| **Total** | **125** |

Within the 42 native VM paths, **8 are modified** and **34 are added**. The modified paths are `Assembly.cpp`, `Assembly.h`, `AssemblyShadow.cpp`, `AssemblyShadow.h`, `AssemblyShadowR02Diagnostics.h`, `AssemblyShadowVisibility.cpp`, `AssemblyShadowVisibility.h` and `Runtime.cpp`. The added sources include lifetime/admitted diagnostics/registration/physical binding/shape/owned output and first-use capture components. Although source-fixed native checkout HEAD constrains these files, the earlier ten-file reviewer manifest listed only three key native implementation paths plus the terminal header. This additional inventory makes the complete changed VM surface explicit.

## 2. New source-bound machine evidence and tests

| File | Git blob | Purpose |
| --- | --- | --- |
| `Tools/AssemblyShadow/R03IR/current_native_vm_delta.json` | `83c1ed0ae5470b2267703f2aa529cefc2706425f` | Ordered exact 42-file path/status/source-Git-blob manifest from native GitHub comparison and current directory metadata |
| `Tools/AssemblyShadow/R03IR/current_native_vm_delta_contracts.py` | `64cced754b0391a6efb36095081e5313f1b1a267` | 12 host-only contracts: actual current-native source Git blobs, exact ordered roster, exact source pin, rejects dropped/duplicate/forged/aliased/invalid entries and source/acceptance promotion |
| `.github/workflows/r03-ir-current-native-vm-delta-source-only.yml` | Source blob read back at final publication | Fixed native `e1e5...` sparse checkout; Mac/Linux read-only source/hash tests, no compiler |

The CI checks each file's actual checked-out **Git blob** against the committed 42-entry manifest. It validates the exact current `git rev-parse HEAD`, old/current commit distinction, complete ordered roster and fail-closed negative mutations. It does **not** simply check that filenames exist. The test suite is explicitly invoked; its filename does not begin with `test_` to avoid perturbing historical unittest discovery.

## 3. Actual host-only Mac/Linux CI result

[GitHub Actions run 40287146227](https://github.com/night-outlook/hybridclr_demo/actions/runs/40287146227), source/CI commit `3a7e9a13f6668a132b3db54679f6a342d20e803c`, completed **success** on **macos-15** (job `121453386586`, `12/12` OK) and **ubuntu-24.04** (job `121453386960`, `12/12` OK). The official native source pin used by CI is exactly `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. Both raw job logs were independently examined. An earlier [current-native source gate run 40264569824](https://github.com/night-outlook/hybridclr_demo/actions/runs/40264569824) independently passed 20 source tests per host, and [Player-oracle run 40285861973](https://github.com/night-outlook/hybridclr_demo/actions/runs/40285861973) independently passed 27 adversarial oracle tests per host.

## 4. Nonclaims and independent-review requirements

**A 42-file byte inventory is not an include-dependency closure, a full semantic review, a source-installation trace, nor proof of the particular generated/linked Player binary.** The future independent reviewer must inspect actual production call chains and the native code delta beyond hash equality. For a future separately authorized Local Player witness, require the installed current-native source file hashes/headers, compiler source tree, generated C++ and linked binary/build receipt to match the coherent 4-repo tuple, not merely three manually pinned entry methods.

Current native terminal method-guard code is present, but **no real Player at `e1e5...` has attempted the specific valid method after caught terminal poison**. The original C04 receipts did not record affirmative fields, and the current 27-test verifier suite uses synthetic host receipts. The original independent full-stage R03 **FAIL** remains. High IR-R03-02 is still open pending real Player and independent review; High IR-R03-01 original-S archive byte provenance is corrected but full independent source/build/Player/semantic review is still outstanding. Owner D1=A/D2=A and all historical PASS/FAIL distinctions remain intact.

**No Local Validation handoff is authorized** by this source delta. `WEB_TO_LOCAL.md` remains CLOSED. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, `qualificationApproved=false`, PureInterpreter disabled. No H2, X02, M08A, protected SNAP-01.
