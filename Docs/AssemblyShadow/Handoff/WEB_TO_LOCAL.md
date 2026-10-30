# Primary Implementation → Local Validation — ACTIVE CONDITIONAL ONE-USE R03 oneuse-E (2026-10-30)

**Authority:** one NEW, clean, source-pinned R03 combined Local evidence cycle, oneuse-E, **only** after all current Git/CI/environment prerequisites and no-write admission pass. The previous oneuse-D is **consumed and Failed**, not a Player runtime failure: eight combined coordinator scoped Passed, one Failed, one Blocked; three actual Unity C++11 native builds Failed; five Players Blocked/NotRun; 126 old physical source pairs NotRun. All earlier A/B/C/D failures and original-S evidence are immutable. NEVER replay any used one-use output, old sparse projection, historical S Player, or failed build. No automatic H2, M08A, X02, SNAP-01, R03 acceptance, qualification, deployment, or Human Review Gate.

## 1. Exact source authority and checkouts

All four must own the branch `codex/assembly-shadow-r01b-h1`, be clean (tracked and untracked), carry the canonical `night-outlook` GitHub origin, match their live remote HEAD exactly, and have no unrelated changes. Local paths are prior *expected* paths; independently verify each Git root, branch, remote and full HEAD before use. Source/asset/SDK installers must also bind the same effective pins.

| GitHub repo | Required exact remote HEAD | Expected owning Mac checkout |
| --- | --- | --- |
| night-outlook/hybridclr_demo | **Final full pushed demo HEAD from the closing Primary-to-Local prompt** — never old D `b6076f8d` or its evidence publication `e171676a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| night-outlook/il2cpp_plus | `6510aed7cab67e9fc70b13ae22a115ad9819193b` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

**Critical different native identities:** historical R03 focused runner `74dbdbea80d83923863303bd2b2c0a87f36541b1`; original S executed native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`; failed oneuse-D current native `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`; **new repaired oneuse-E** native `6510aed7cab67e9fc70b13ae22a115ad9819193b`. Do not rewrite the original `Tools/AssemblyShadow/R03/source-pins.json` or reuse any old installed source/Player binary to represent E.

**New mandatory physical inventory:** the current corrected candidate differs from the 74db baseline at **43** `libil2cpp/vm` files (9 modified, 34 added), including `AssemblyShadowDiagnosticWriter.h`, which was absent from the old 42-file roster. The updated Git-blob-pinned manifest `Tools/AssemblyShadow/R03IR/current_native_vm_delta.json` and source tests admit all 43. Three real installed build roles must supply **129 source-to-installed-file pairs**; the old 42/126 is D-only historical and may not pass E.

## 2. Read order, project scope and preserved evidence

1. `Docs/AssemblyShadow/README.md`, **this** `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`.
2. Local-owned `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md`; the **complete** D checkpoint at `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261029-oneuse-d/`, especially `README.md`, `NATIVE_BUILD_FINDINGS.json`, `LOCAL_RESULT.json`, original C++11 compiler stderr and CI JSON artifact finding. Preserve D publication `e171676a...` and external `/Users/ah/GitHub/hybridclr/r03-local-validation/oneuse-D-PUBLICATION_RECEIPT.json`.
3. Primary design, plan and review under `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_D_CXX11_REPAIR_2026-10-30/`. Review `R03Build.cs`, `current_native_build_failure_contracts.py`, `current_native_source_gate.py`, `current_native_vm_delta_contracts.py`, `run_current_native_validation_cycle.py` and `current_native_install_audit.py` as needed.
4. Original Oct 8 independent R03 FAIL/erratum, current conservative NativeLayoutAdmissionV1 and owner D1=A/D2=A, original S `fc55` and source/provenance/RC1–RC6 obligations. Neither fresh host CI nor an updated manuscript closes them.

**Historical preservation:** original-S retained **sparse**, detached clean, singly registered Git worktree:
`/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`
at exactly `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, original checkpoint Git tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`, 16,978 protected files. Do not re-create, re-sparsify, move, delete, restore full projection, modify any historical Git objects, clean unrelated worktrees or relabel prior reports. The current coordinator may **read and reauthenticate** this original checkpoint under E's fresh external root.

## 3. Host/CI prerequisite — require real evidence before E root

Require exact-source or demonstrably identical source-bound **Passed** jobs (record run IDs, commit SHA, job conclusions, logs and source hashes) for:

- Native `il2cpp_plus@6510aed7cab67e9fc70b13ae22a115ad9819193b`: `.github/workflows/r03-cxx11-unity-compat-host.yml`, macOS Clang, Ubuntu Clang and Ubuntu GCC, actual production header compilation at **C++11** (both feature values) and C++17 host controls. Relevant success run: [41043686073](https://github.com/night-outlook/il2cpp_plus/actions/runs/41043686073). This is HOST/source-only, not an SDK Player build.
- Final pinned demo commit: `.github/workflows/r03-ir-current-native-local-cycle-host.yml` (strict 43-file source/CLI/real fresh Python startup/installed parity synthetic contracts, and 8 negative BuildReport source-order tests), `r03-ir-current-native-source-only.yml`, and `r03-ir-current-native-vm-delta-source-only.yml`.
- Final pinned demo commit: `.github/workflows/r03-ir-fixture.yml` macOS and Ubuntu **actual net8 generator compilation**, pinned IR SHA/MVID, independent repeated target output, 15 generated comparison DLLs checked structurally against immutable original S inventory, and `historical-differences.json` written with a *real LF* then parsed from the saved artifact. New regenerated DLL bytes and MVIDs are **not** original-S historical authority.

If any required fresh job fails, is pending, cancelled or unverified at dispatch, STOP before any Local E output/root creation. Return to Primary with exact job/run and raw log. Never silently reuse an old CI success for a changed source blob, modify Local product code to unblock CI, or infer real Unity success from host CI.

## 4. Read-only Mac admission, no new root / no Unity invocation

Verify the actual Mac toolchain, not its printed history: Unity `2022.3.62f2` native ARM64 executable and Info.plist:
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`
and the existing real `.NET SDK 8.0.318 / Microsoft.NETCore.App 8.0.21` osx-arm64 from
`/Applications/Unity/Hub/Editor/6000.5.3f1/Unity.app/Contents/Resources/Scripting/DotNetSdk/dotnet`.
Only that SDK's existing directory may be prepended to this terminal/session's PATH; Unity 6000 is NEVER a Player here. Require actual `dotnet --info`, SDK/runtime lists, compiler (`clang++`), `lipo`, Python3, Git and exact source/installed package identity. Do not install/modify SDKs or globally change PATH, TMPDIR, compiler args or assets. Check there are no conflicting Unity/IL2CPP processes or incomplete concurrent build roots.

**Space:** read-only admission maintains fixed **20 GiB hard minimum** and **40 GiB advisory** for three native builds/five Players. Below 20 GiB STOP. At least 20 but below 40 is an admitted but high-risk observation: stop and return to Primary for explicit go/no-go; do not consume the oneuse-E root or assume an APFS sibling volume offers more capacity. Fresh capacity measurement, not the old oneuse-C/D measurements, is authoritative.

Select and independently check the following **absent, physically canonical, disjoint** root (only if unused):
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261030-oneuse-E`.
Do not pre-create it. If it exists or aliases any existing A/B/C/D, stop and request new source-pinned Primary authority; do not silently choose another suffix. New admission receipts may be stored outside both the reserved E root and protected older evidence, with exact raw stderr/stdout hashes.

For an authenticated existing workspace, execute this **no-write** script; `DEMO_COMMIT` is the full **closing handoff prompt** demo SHA and never an earlier source/evidence SHA:

```bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261030-oneuse-E
# DEMO_COMMIT=FULL_40_CHAR_PUSHED_DEMO_SHA_FROM_CLOSING_HANDOFF
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

Require exit 0, `PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun`, `standaloneCurrentNativeCli.result=PassedFreshPythonProcessHelp_NoUnityOrRuntime`, 43 exact VM Git source blobs, verified fresh Python process from external cwd **without** PYTHONPATH/PYTHONHOME, four live remote heads, clean sparse original S, real dotnet/Unity and capacity. The admission cannot compile Unity or create E root. On any failure, preserve raw evidence and report **PrerequisiteBlocked**, coordinator invocations 0 and ten E stages NotRun; never assist import via PYTHONPATH or modify Local sources.

## 5. Exactly ONE unmodified ten-stage R03 coordinator batch

Only when all preceding CI, Git, toolchain, one-use-destination and capacity gates are green, execute once:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

The existing coordinator separately authenticates source/remote/sparse original-S again before E creates its root. Ten original stages remain: current source contracts, oracle synthetic negative contracts, 43 VM delta source contracts, original-S host contracts, installed parity host synthetic contracts, original nine-part/15,713-member/90-cell S archive auditor, 59 original process joins, native C++ host diagnostics, real current-native builder/Player runner, and actual 3-role×43-file installed parity audit. Record exact source, independent paths, SHA and timestamps for each stage even if a later stage fails. Nothing from D's 3 failed builds or old S Players may satisfy E.

Real Player stage requires three fresh Unity2022.3.62f2 arm64 IL2CPP build roles: ON Release, ON Debug, OFF Release. Five fresh actual Players: release baseline-owner post-terminal, debug baseline-owner, release type-resolution, release OFF control, release engine-unhandled native sentinel. Require pre-poison positive call, real post-poison reflection/delegate/AOT attempts, zero body/canary side-effects, stable terminal reason/recovery, GC/reserve probe, exact PID/request/nonce and source-identified linked build/Player raw logs. Real build results must report `buildPipelineResult=Succeeded` and `playerInventoryStatus=PresentAndInventoried`; if a BuildPipeline fails, preserve `buildPipelineResult/errors/warnings`, explicit absent-app inventory status, **first original Editor C++11 compiler errors**, Bee report and failed receipt instead of inventing Player content.

All three successful build roles must then physically prove **129** equal-source installed VM pairs, including corrected DiagnosticWriter. Source inclusion in installed trees is not itself proof all files reached linked Player; preserve that limitation and other scope flags. CI synthetic PASS cannot replace real Unity/Player. Do not run a second coordinator, do not retry partially failed E root, no old runner/stimulus replay or extra arbitrary Unity build beyond this source-pinned cycle. On errors, retain the FIRST concrete failure and all remaining later stages separately Failed/Blocked/NotRun.

## 6. Required factual Local publication and stop

Preserve immutable A/B/C/D, D's raw CI malformed JSON bytes, all prior S/b7e3/c42a/f51d historical results, and the retained sparse fc55. For E, retain no-write admission, E `ADMISSION.json`, `RESULT.json`, `COORDINATOR_MANIFEST.json`, all ten step INVOCATION/RESULT/exit/stdout/stderr/PGID and cleanup records, full S archive/index/90 cells and 59 joins, generator/host C++ logs, each real Unity Editor/Bee/IL2CPP build receipt and installed source manifest, five Player request/PID/raw/log/canary/verifier receipts, `installed-native-vm-parity.json` if reached, and before/after source/worktree/S protected integrity. Distinguish genuine `Passed`, `Failed`, `Blocked`, `NotRun`, `Unavailable`, synthetic/adversarial `PassedHostOnly` and historical audit-only evidence.

Publish a **new additive oneuse-E checkpoint** under `Docs/AssemblyShadow/History/M07R/R03/` and update Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` with exact source/source-build-output provenance, complete stage table, FIRST failure, evidence path and remaining reviewer obligations. Commit/push and independently verify all four remote heads; preserve any prior unrelated changes. Nontrivial architecture/source corrections go back to Primary Implementation. STOP after this single E cycle.

## 7. Immutable gate and review limits

The Oct 8 independent R03 full-stage review **FAIL** with High IR-R03-01/02 is not changed. D1=A conservative NativeLayoutAdmissionV1/X02 deferral, D2=A observational performance/four contaminated Failed certificates and original S bounded historical 90/90 remain unchanged. The best possible new Local outcome is `FocusedEvidenceReadyForIndependentReview` requiring a fresh independent reviewer; never `R03Accepted` or Human Review Gate approval. Existing P1/P2/E0/E1/P3 limitations and PureInterpreter disabled remain, with no H2/M08A/X02/SNAP-01 progression.
