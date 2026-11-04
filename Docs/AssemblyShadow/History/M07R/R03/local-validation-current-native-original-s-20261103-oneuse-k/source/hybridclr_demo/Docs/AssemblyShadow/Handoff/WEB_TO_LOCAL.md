# Primary Implementation → Local Validation — CONDITIONAL R03 oneuse-K (2026-11-03 UTC)

**Authority / stop:** A brand-new, single-use **K** R03 focused Local cycle is authorized **only after** all exact-final-demo-SHA two-OS CI, source/branch/remotes, original-S/A–J custody, read-only Mac/SDK admission, actual host CLI read-only preflight, two fresh disk-capacity samples and absent K root checks below pass. J is **consumed FAIL / ReturnRequired**; NEVER rerun J or rewrite its evidence. The exact final demo commit is the **40-digit pushed HEAD in Primary's closing prompt**, and all nine CI `head_sha` values must match that same commit. No source-equivalent ancestor substitution.

Design and reviews: [K design](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/DESIGN.md), [K execution plan](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/PLAN.md), [Primary source review](../History/M07R/R03/IR_Remediation/IR_R03_ONEUSE_J_PATH_CLI_2026-11-03/PRIMARY_SOURCE_REVIEW.md).

## 1. Read order and historical J result (do not reclassify)

Read `Docs/AssemblyShadow/README.md`, **this** `Handoff/WEB_TO_LOCAL.md`, Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` in that order; then actual J `History/M07R/R03/local-validation-current-native-original-s-20261103-oneuse-j/{README.md,LOCAL_RESULT.json,RUNTIME_FINDINGS.json}` and retained `batch/steps/native-host-diagnostics/{INVOCATION.json,stderr.log,RESULT.json}`. Read K design/plan/source review.

Exactly one J ran at demo execution `07c96a3739d746b0fe70a9b7acc861d5261a0752` / native `41764ae1eeefb33b05966e7f7676e52aae39c340`; J Local documentation publication HEAD `8db47f02f51d9b97061eb9b3f5199c6a43fc8069`. J was **FAIL / ReturnRequired / exit1**: nine exact source CI workflow/18 OS jobs Passed, fresh Mac admission and two >=28GiB J-specific samples Passed, seven source/archive stages Passed and after-preservation Passed. The actual host wrapper rejected valid canonical `PosixPath` in `inputs():180` via `type(workspace) is Path`. Therefore **all ten internal native host components NotRun, no new Unity/IL2CPP builds, Players0, no new child/sidecar, official135 native audit Blocked**. This is a validation startup issue, not evidence of a new native/runtime failure. Its stopped coordinator correctly preserved NotRun statuses. Never promote J, rerun its output, substitute earlier I Player, or modify its archived failure.

Prior I had three real builds/five Players/18 cells and official135 pairs Passed in scoped child evidence, but its historical **outer** result remained ReturnRequired; I's bounded native engine success is not a new K Player. G/H/E FAIL and F Blocked, A–D checkpoints and original-S historical-only audit keep their own verdicts. Preserve exact detached original S at `/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`, HEAD `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, protected tree `2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79`, **16978 protected files**, all A–J original live raw/archives/manifests/SDK, original 59 historical process joins. No re-sparsify, git clean/reset/gc/prune, archive copy-reseal or protected root cleanup.

## 2. Exact canonical sources (all 4 must be clean remote-verified)

All repos use **branch** `codex/assembly-shadow-r01b-h1`. For each verify absolute canonical Git root, `origin` `night-outlook`, `HEAD` exactly as below and **current live remote branch HEAD** identical. No source/SDK changes by Local before tests.

| Repository | Local checkout | Required pushed source SHA |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **the 40-digit final pushed demo SHA in closing Primary prompt** (identical nine CI `head_sha` values) |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Current candidate source gate checks eleven pinned source files; current native delta pins 45 changed VM files versus immutable original historical `74db...` and requires **135 physical source pairs across three successful Unity build roles**. Native current I/J/K constituent `41764...` is unchanged; neither G/H nor archived I demo execution are source authority for K. Historical `Tools/AssemblyShadow/R03/source-pins.json` is immutable. Do not overwrite old Player outputs.

## 3. Primary K correction and new Local host evidence

Changes are confined to **`hybridclr_demo` R03IR validation source**, not Unity runtime or the other three repositories.

- `run_current_native_host_preflight.py::inputs` now accepts a real `isinstance(workspace, Path)` (argparse creates concrete `PosixPath`) while still requiring absolute directory, exact strict canonical resolution, no final/parent symlink alias/`..`, actual four clean remotes/current heads, eleven source Git blobs, correct native SHA, unchanged historical eight-suite helper (blob `2d51be157b94a47ac19d1061d0066c1f98dbc177`) and two real owner scripts **before any native host output creation**.
- New `--read-only-admission` performs that **same real input and output path check** and returns `PassedReadOnlyNativeHostInputs_NoComponentsOrUnity`, with `nativeHostComponentsExecuted=0`, `outputRootCreated=false`, `runtimeAcceptance=false`. It must create no host output and does not prove any ten-suite execution or Unity.
- Current normal wrapper still runs the original eight historical native-host commands **plus two fresh Local C++11 owner suites**: `native-owner-method-classifier` (2 real unit tests) and `native-owner-full-tu` (3 real unit tests). Independent per-subcommand argv/PID/exit/timeout/stderr SHA and exact unittest counts required; all ten unique Passed and `R03IRCurrentNativeTenHostComponents` receipt validated before any Unity. Missing/failing/duplicated/faked/NotRun host → fail-stop Unity0. No historical eight-suite or CI host evidence can stand in for fresh Local 8+2.
- `current_native_host_contracts.py` adds actual concrete Path positives, literal string/relative/path alias/symlink/wrong SHA negatives, foreign-cwd fresh-process CLI `--help` and negative argv startup. Combined GitHub Actions **actually checks out four independent real repos in Local workspace shape**, runs real read-only source/remote/path CLI positive and negatives, then executes the **complete normal 8+2 native-host CLI** in both macOS and Ubuntu CI. This was not present in J's CI.
- Existing complete 18-cell strict producer-record consumer, typed repository metadata (schema/phase/branch/four sources/nonacceptance), I byte-exact test fixture and independent 135-pair source audit remain unchanged. They require a **new K child result**, never copied I evidence, for a new K scoped PASS.

The original uncapped native reporter count and **64 real reports/500ms** bound, first terminal failure13/RestartRequired, native wants/quit once-only transport, no managed post-terminal body, strict complete sidecar and original Player oracle remain unchanged. No new production behavior has been introduced. A clean CI test is host-only, not a real Unity build/Player.

## 4. Exactly nine mandatory same-final-commit GitHub CI workflows

Before Local creates a K root or launches Unity, inspect **real** GitHub `push` workflow runs and **both** macOS+Ubuntu job results for the **exact final demo SHA from closing Primary prompt**. Every job must be `completed/success`; record run IDs, job IDs, source/checkout SHA, trigger and logs. The nine required workflow files are:

- `r03-ir-current-native-local-cycle-host.yml`
- `r03-ir-current-native-source-only.yml`
- `r03-ir-current-native-vm-delta-source-only.yml`
- `r03-ir-current-native-oracle-source-only.yml`
- `r03-ir-fixture.yml`
- `r03-ir-host.yml`
- `r03-k-host-contracts.yml`
- `r03-k-sourcecheck.yml`
- `r03-l-contracts.yml`

All nine `push.paths` include this canonical `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`, so the **final handoff publication** must trigger nine actual runs at the same full commit. Combined current-native host must include the **genuine additional four-repo read-only CLI** and **genuine 8+2 full host CLI on both OS**, not only mock/unit code or unchanged historical helper. The native double checkout in combined CI must have two exact 40-character equal `il2cpp_plus` ref pins, and other two native CI workflows one exact pin each. A missing/pending/failing/cancelled/wrong-SHA job => **NO-GO, K coordinator0/Unity0, K root absent**, return actual blocker. Do not substitute pre-doc source-equivalent or an earlier failed CI attempt.

## 5. New K Mac admission and *K-only* capacity GO/NO-GO

Actual Unity must be installed **2022.3.62f2 arm64** at `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`, previously recorded hash `35721b35221875b2d170160f7fdd661afff7458b3386f029124f30e1ba2b862c`. Actual .NET SDK8.0.318/runtime8.0.21 and Git/Python/Apple clang++/lipo and **2405 original installed SDK source inputs** remain pinned. No duplicate Unity/IL2CPP owners, installer, compiler/SDK switch, TMPDIR/CXX workaround, or cache cleanup. Child-process-only use of existing .NET SDK path previously authenticated is allowed.

J had 31,837,822,976 bytes immediate pre-coordinator and 30,872,297,472 bytes at independent final audit (about28.754GiB), a historic **~0.899GiB** drop without Unity. I's earlier real full cycle consumed ~2.832GiB, but neither is a guarantee. Hard **20GiB** and advisory **40GiB** unchanged. Primary grants a **new, nontransferable K-only conditional advisory exception** if **both** fresh read-only admission and independent immediately-pre-coordinator capacity samples show **>=25.0GiB free on the actual K parent volume** and all CI/source/custody/SDK/root gates Passed. At >=40GiB ordinary GO; at25..under40GiB record explicit K-only exceptional GO, exact bytes/GiB/timestamps/device/volume. **Below25.0GiB NO-GO**, even if hard20 passes. No cleanup, APFS sibling-volume trick or reuse of J waiver.

Choose only an **absent, disjoint, canonical** output root (do not pre-create, auto-suffix, reuse J or old I/H, or touch F absent root):
`/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261103-oneuse-K`.

Define:
```bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-CurrentNativeOriginalS-20261103-oneuse-K
DEMO_COMMIT=<the exact full final pushed demo SHA from closing Primary handoff>
```

**Both** independent read-only preflights must pass from a foreign cwd without PYTHONPATH or PYTHONHOME, before K root creation, with receipts stored **outside all consumed roots**:

1. Original Mac/source/SDK/environment admission; must return `PassedReadOnlyPrerequisites_NoCoordinatorOrUnityRun`:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```
2. Additional actual native-host wrapper **read-only** input-path/remote CLI check; `HOST_CHECK_ROOT` must be another absent path whose parent already exists, for example:
```bash
HOST_CHECK_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-K-native-host-admission-NEVERCREATE
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_host_preflight.py" --workspace "$WORKSPACE" --expected-demo "$DEMO_COMMIT" --expected-native 41764ae1eeefb33b05966e7f7676e52aae39c340 --output "$HOST_CHECK_ROOT" --read-only-admission
```
Require `PassedReadOnlyNativeHostInputs_NoComponentsOrUnity`, `HOST_CHECK_ROOT` absent, zero host commands, no runtime/Unity. If any preflight or capacity fails: publish `PrerequisiteBlocked` factual evidence, coordinator0, Unity0, K root absent, STOP. The two read-only results do not replace the actual ten-host stage.

## 6. Exactly ONE K full coordinator after all gates pass

Only after sections4/5 complete and a second independent immediate K-parent free-space sample meets the K-specific threshold, invoke the existing source-pinned ten-stage coordinator **once**, no retries or old apps:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py" --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
```

Mandatory resulting evidence:
- Exact current source/host/oracle/VM/installed-source contracts and archival original-S nine-part/15713-member/90 *historical* cells, 59 historic request/raw/PID process joins, all scoped correctly.
- A **new K native-host-diagnostics** output containing original eight real historical subcommands **plus both fresh Local owner C++11 suites**, real compiler invocation/logs,10 unique Passed components, exact stdout/stderr SHA, intact source before/after and completed source/remote metadata. If this stage fails, Unity/builds/Players must **not run**.
- **Three new** actual Unity2022.3 arm64 IL2CPP C++11 builds: ON release, ON debug, OFF release; each real BuildReport Succeeded/no masked errors and physical pre/post installed source inventory.
- **Five new** real Player processes: ON release/debug baseline, ON type-resolution, OFF healthy and ON frame-originated unhandled engine. Original per-case request SHA/run nonce/PID/argv/build/executable/Editor/Player.log/raw/strict complete general sidecars and semantic verifiers. OFF canary1→2; ON denies post-terminal reflection/delegate/AOT with unchanged canary/field/recovery; engine authentic sentinel/type failure13, one owner quit, native wants/quit counts1 each, **real uncapped** 1..64 completed reports <=500ms and durable `NativeAtexit`/exit0, not watchdog or fabricated success. Keep first actual error/counter/time if Failed.
- **Independent official 135** native VM source pairs (45 VM files×3 successful builds), with actual source-to-installed SHA and original sibling Player verdict retained even if Player semantic test failed. No full binary linkage/managed shutdown proof from source parity alone.
- Actual fresh complete 18-cell child result consumed by the repaired shared typed record checker and true outer coordinator receipt. Original I/J child or historical source-only CI does not stand in for fresh K.
- Seal/preservation audit of full original-S protected projection and **all A–J prior evidence**, 2405 SDK inputs, four remote HEADs, no owned survivors.

Any source/host/Unity failure yields factual Failed/Blocked/NotRun; do not override from earlier I success or a mock. One K, no rerun.

## 7. Local publication, review gate and STOP

Publish a new **additive** `Docs/AssemblyShadow/History/M07R/R03/local-validation-current-native-original-s-20261103-oneuse-k/` checkpoint and update Local-owned `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`. Include exact governing four source SHAs/final nine run IDs, both independent read-only preflights and actual K capacity, native eight+two command/negative evidence, 3 builds/5 Players/135 pairs and original semantic aggregate, source/SDK/custody/seal identities. Commit/push via Git, verify four live remote HEADs and return to Primary Implementation. Local may fix only bounded immediately verifiable unblockers, no architecture/native/SDK refactor; no K retry, H2/M08A/X02/SNAP-01 or Human Review Gate automatically.

**All independent acceptance gates remain closed**, even on a focused K success: Oct8 independent R03 FAIL/High IR-R03-01/02, P1/P2/E0/E1/P3, full Unity-managed Shutdown, coherent whole-VM epoch, GC/RSS and legacy completeness are unproven. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled.
