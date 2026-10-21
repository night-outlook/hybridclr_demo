# Primary Implementation → Local Validation — ONE Git source-authority postflight receipt cycle

**ONE new R03 P1 24-component SOURCE/HOST + official installed Unity2022.3.62f2 SDK SYNTAX-ONLY Local Validation batch** is authorized, and **only after independent Local admission**. This increment fixes postflight **Git remote-authority evidence capture**, NOT HybridCLR product execution, Unity Player, codegen, V1/V2 API, canonical TypeKeys, physical pointer allocation provenance/lifetime, VM epoch/ABA, GC/RSS, Shutdown, or full R03 acceptance. **Keep unchanged 120-second Git timeout and original source-authority verification**, no retries, no alternate transport, and no relaxation of P1/Local requirements.

## 1. First reads, empirical FAIL, and immutable prior evidence

Read the following files from the final pushed **demo** source HEAD, in this exact order:

1. `Docs/AssemblyShadow/README.md`, `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md`.
2. **Local-owned** `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md` **FIRST**, then **`Handoff/RETURN_TO_WEB.md`**. Review the [latest consumed `20261021-82dd` checkpoint](../History/M07R/R03/local-validation-p1-vm-shape-json-20261021-82dd/README.md), [FINDING.json](../History/M07R/R03/local-validation-p1-vm-shape-json-20261021-82dd/FINDING.json), [independent evidence audit](../History/M07R/R03/local-validation-p1-vm-shape-json-20261021-82dd/preflight/EVIDENCE_AUDIT.json), [aggregate failure disposition](../History/M07R/R03/local-validation-p1-vm-shape-json-20261021-82dd/preflight/AGGREGATE_FAILURE_DISPOSITION.json), full raw/scratch/audit provenance, all prior P1 checkpoints, historical negative symlinks, original sources and installed Unity SDK.
3. [Current focused Design](../History/M07R/R03/IR_Remediation/P1_POSTFLIGHT_GIT_RECEIPTS_2026-10-21/DESIGN.md), [one-shot Plan](../History/M07R/R03/IR_Remediation/P1_POSTFLIGHT_GIT_RECEIPTS_2026-10-21/PLAN.md), [Primary Source Audit](../History/M07R/R03/IR_Remediation/P1_POSTFLIGHT_GIT_RECEIPTS_2026-10-21/PRIMARY_SOURCE_AUDIT.md), [machine CI/evidence](../History/M07R/R03/IR_Remediation/P1_POSTFLIGHT_GIT_RECEIPTS_2026-10-21/EVIDENCE.json), and existing P1/P2/E0/E1/full P3 outstanding scope.
4. **Before creating any root**, independently authenticate all four canonical clean Git repos/heads/branch/origin/submodules, native managed package, all consumed raw/scratch/audit/checkpoint/negative symlink evidence, installed official SDK and sufficient disk, and that all **four new roots below are absent, canonical and disjoint**. Failed admission ⇒ Blocked, STOP, no moved or renamed root.

**Authoritative latest Local `20261021-82dd` = aggregate `FAIL / FailedOrIncomplete`**. Source tuple executed: demo `bf4ebab005d008e7d936e4c9b17f62d06afcd37c`, native `82ddcef9417e3d662fdd39916a92124b5c835094`, hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`. **24/24 components actually Passed**, 85 original tests, seven independently verified source case inventories, five real managed positive products plus distinct `OriginalUnsignedCounts` exact compiler negative, **100/100 actual official Apple C++17 arm64 SDK syntax**. HOWEVER final `hybridclr git ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1` exceeded 120 seconds; original raw **`sourcePreserved=false`, `fourRepositoriesAfter=[]`, `postflightError=TimeoutExpired(...)`, exit 1** cannot be promoted by later independent `PassedFactualEvidenceAudit` or successful Git checks. Source/SDK/history independently preserved, but authority finalization failed. **No core retry**, no Unity Editor/Test Runner/Player, product-native link, runtime GC/RSS or Shutdown. All used `82dd` roots consumed and immutable; prior `20261021-c776` 23/23 PASS belongs to its **separate older tuple only**.

## 2. Exact working source tuple and repository custody

Four **separate** canonical GitHub repositories, each branch `codex/assembly-shadow-r01b-h1`. Parent `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` is **NOT** a Git repo. Resolve origin SSH to the matching canonical HTTPS identity, verify exact live remote HEAD/local HEAD/clean `git status --porcelain`/worktrees/submodules/packages before running. Fast-forward only from a clean ancestor; no reset-hard, clean, force, unrelated merge, uncommitted overwrite or source-pins rebaseline.

| Repository / HTTPS origin | Existing checkout | Required pushed HEAD |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` / `https://github.com/night-outlook/hybridclr_demo.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final Docs-only handoff HEAD**, supplied as an exact full 40-hex SHA in Primary's accompanying Local prompt; must equal local HEAD, live remote HEAD and `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. Reviewed/demo code anchor: `7c2c41e192f7afe7350d47632b8e452dcc1a8aad`; every commit after it must modify **Docs/** only. |
| `night-outlook/hybridclr` / `https://github.com/night-outlook/hybridclr.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` / `https://github.com/night-outlook/hybridclr_unity.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` / `https://github.com/night-outlook/il2cpp_plus.git` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `82ddcef9417e3d662fdd39916a92124b5c835094` (unchanged native source) |

Historical `Tools/AssemblyShadow/R03/source-pins.json` must remain **BYTE-IDENTICAL** (old native `74dbdbea80d83923863303bd2b2c0a87f36541b1`); new candidate stays explicitly passed as `--expected-native` / internal `--candidate-native-sha`. Original managed package `file:../../hybridclr_unity` resolves to sibling checkout. Any advance after this final handoff requires a new Primary pinned handoff.

## 3. Focused Primary correction — Local validates only

Exact Primary changed source files since latest Local report:

- `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py`
- `Tools/AssemblyShadow/R03IR/test_p1_command_failures.py`
- `Tools/AssemblyShadow/R03IR/test_p1_managed_receipt.py`
- `Tools/AssemblyShadow/R03IR/test_p1_metadata_preflight.py`

**No native, HybridCLR, Unity SDK/compiler, generated Player code or normal product source was changed.** Original P1 source/host/sanitized/SDK code, original V1/V2, VM shape/JSON/pointer-free proof and native Git blob source fingerprints are unchanged.

`GitPostflightProbe` wraps only the **final** Git authority checks after component runs, not initial local admission. Per each repo, it records the identical five original operations in the identical order: `remote get-url origin`, `branch --show-current`, `rev-parse HEAD`, `status --porcelain`, and `ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1`, with original **120-second timeout**, inherited environment/SSH configuration and no repeat/alternate transport. For each *actually invoked* command:
- `<raw>/postflight-git/<repo>/<ordinal>-<operation>/START.json`: repository, ordinal, exact argv, start Unix timestamp, fixed 120-second timeout, `descendantQuiescenceProven=false`.
- `RESULT.json`: actual started/completed Unix, monotonic elapsed, known/nonzero/nullable exit, Completed/CompletedNonzero/TimedOut/LaunchFailed/Interrupted/UnknownExecutionError, typed exception, stream availability/completeness and unknown child lifetime.
- `stdout.bin` and `stderr.bin`: up to **65,536 captured direct-child bytes EACH**, with true total captured lengths, full-captured SHA256 when available, stored-prefix SHA256, truncation flags. Do not invent full data for timeout prefixes or interpret direct process completion as independent SSH descendant quiescence.

`postflightGitDiagnostics` reports direct command count, limit, completed-repository names/count and timeout/nonzero/lifetime. Fully verified repos are appended individually to `fourRepositoriesAfter`. **Any missing one of the final four, timeout, nonzero, unverified descendant status or source-hash mismatch means aggregate `FailedOrIncomplete`, `sourcePreserved=false`**; partial completed repos are NOT accepted as source transport. A timeout preserves partial direct streams, `commandLifetimeUnverified=true` and unsealed manifest; later independent read-only checks do not rewrite it. If a prior component already has unknown lifetime, **no final Git source subprocess is launched**, and new postflight evidence is not fabricated.

Focused CI source-host (NOT official installed SDK): corrected [integrated 85 tests 39630866119](https://github.com/night-outlook/hybridclr_demo/actions/runs/39630866119) **PASS 2/2** Mac/Linux, corrected [command failure 39630866124](https://github.com/night-outlook/hybridclr_demo/actions/runs/39630866124) **PASS 2/2** Mac/Linux, earlier same core runner [managed receipt 39630599185](https://github.com/night-outlook/hybridclr_demo/actions/runs/39630599185) **PASS 2/2**. Initial Mac-only `39630599200` and `39630599234` **FAIL** from new test canonical TempDirectory path `/var` vs `/private/var` was fixed only in the synthetic test using `Path(td).resolve()`, preserving original strict real checkout guard. All original 85 test IDs unchanged.

## 4. Exactly one fresh set of four absent/disjoint roots

Local independently verifies ALL four are **ABSENT**, canonical, pairwise disjoint, outside four repos/submodules/worktrees, original installed Unity SDK, prior P1 raw/scratch/audit/checkpoints and deliberate historical negative symlinks. All previously consumed roots, including **`82dd` raw FAIL and its associated independent audit**, remain read-only. No root precreation, reuse, changed suffix or retry.

- **New raw:** `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-GIT-POSTFLIGHT-20261021-7c2c`
- **New SDK scratch:** `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-GIT-POSTFLIGHT-20261021-7c2c`
- **New independent preflight/audit:** `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-GIT-POSTFLIGHT-20261021-7c2c`
- **New additive checked-in checkpoint:** `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-git-postflight-20261021-7c2c/`

Original installed Unity2022.3.62f2 SDK binary (READ-ONLY; **DO NOT LAUNCH**):
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Preserve source/vendor/compiler private-temp policies and original native/managed candidate compiler inputs. No platform/timeout override.

## 5. ONE exact batch command after completely successful independent admission

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=7c2c41e192f7afe7350d47632b8e452dcc1a8aad
NATIVE=82ddcef9417e3d662fdd39916a92124b5c835094
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-GIT-POSTFLIGHT-20261021-7c2c" \
  --sdk-scratch "$B/Scratch-R03-P1-GIT-POSTFLIGHT-20261021-7c2c"
```

This is the **only** authorized core attempt. Consumes all four new names on PASS/FAIL/Blocked/timeout/interrupt. No repeat/run of individual children as substituted acceptance, no fresh suffix, no changing SSH transport, timeout, Git, compiler, SDK or source, no Unity Editor/Test Runner/Player/native product link. Report exact PID/time/argv/exit/streams and true partial or unavailable data. Known complete nonzero remains Failed; unknown command/descendant lifetime stops later subprocesses, records children NotRun without their directories and skips unsafe source postflight.

## 6. All 24 components and mandatory final Git evidence

Components retain original sequence, source gates and expected inner results:
- `command-failures` (original **85** unique test IDs/modules 5+14+44+10+12), `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, `empty-live`, `opaque-inventory`, `physical-membership` (21/profile).
- `owned-physical-names` (28+28), `owned-physical-json` (21+21), `live-owned-physical-json` (12+12 plus old 28/profile), `observed-type-shape` (15+15 plus old 28/profile), `live-type-shape-census` (16+16 plus old 28+15), `observed-type-shape-json` (16+16 plus old 28+15+16), `vm-shape-json` (16+16 genuine integration plus prior 28+15+16+16 =91/profile); all **seven** outer source-inventory flags `ownedBindingCaseInventoryVerified`, `ownedPhysicalJsonCaseInventoryVerified`, `liveOwnedPhysicalJsonCaseInventoryVerified`, `observedTypeShapeCaseInventoryVerified`, `liveTypeShapeCensusCaseInventoryVerified`, `observedTypeShapeJsonCaseInventoryVerified` and `vmShapeJsonSourceCaseInventoryVerified` must be **true**.
- `bounded-status`, `bounded-inventory`, `frozen-v2` with all old 34 opaque publisher cases/profile, owned execution 6×35, six immutable original current/frozen V1 byte parity and negative tests.
- `managed-sdk`: five **actual official** managed positive products from 428 pinned source inputs and **distinct** original `OriginalUnsignedCounts` expected-negative exit1, exactly **two CS0266, NO DLL**, canonical nested `managed-sdk/build-api/results.json` producer/stdout SHA/outer receipt joins.
- `native-sdk`: **100 actual** official Apple arm64 C++17 `-fsyntax-only` compiler commands, 20 unchanged distinct translation units×five candidate/debug/diagnostics-off/feature-off/probe-off modes. Complete original native `AssemblyShadow.cpp` with genuine source, original owned-names signature TU and all native SDK inputs, no link/Player.
- **Mandatory source-authority postflight after all 24 children:** **exactly 20** genuine Git direct commands (five per four repos) recorded under `postflight-git/`; each a valid `START/RESULT/stdout/stderr` bound by source/manifest hashes with total/stored bytes and durations. All 20 operations must have known exit0 and no timeout/unknown-lifetime; four exact final repo results verified, each clean and matching before/expected pinned HEAD; all source/script/SDK/historical evidence unchanged. `postflightGitDiagnostics.actualDirectCommandCount=20`, `completedRepositoryCount=4`, `timedOutCommands=0`, `commandLifetimeUnverified=false`, `noRetry=true`. `descendantQuiescenceProven=false` is a literal nonclaim, not a PASS requirement to flip.

**Aggregate PASS / PassedSourceHostAndSDKOnly** only if 24/24 actual child Passed with all 85 test IDs, seven source inventories, five real managed positive products + exact negative, 100/100 native SDK syntax, **complete real Git authority postflight**, `sourcePreserved=true`, `fourRepositoriesAfter` complete/exact, `postflightError=null`, `stoppedAfter=null`, `commandLifetimeUnverified=false`, full before/after source and installed SDK/history hashes verified. Independent Local audit must join all source/SDK/command Git stdout/stderr hashes, PID/times/argv, raw inventory, deliberate negative symlinks and old `82dd` immutable failure evidence.

If a postflight SSH Git timeout occurs again, preserve **raw FAIL**, new partial repo list/streams/null exit/lifetime uncertainty and unsealed manifest; later read-only independent Git success cannot repair that raw aggregate. Never mark this as P1, R03, native runtime or Player acceptance.

## 7. Local-only authorized modifications and STOP

Local may modify/push **ONLY** factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md` and the single additive `local-validation-p1-git-postflight-20261021-7c2c/` checkpoint. Bounded independent environment-only diagnosis is allowed but not source/compiler/SDK/network/auth policy modification or repeating the core batch. Commit/push actual evidence, verify all four current remote HEADs and **STOP after this one run**, whether PASS/FAIL/Blocked.

**Outstanding product acceptance unchanged:** P1 Incomplete (generic-aware canonical TypeKeys, pointer origin/lifetime, coherent VM epoch/ABA, complete execution V1, original getter, GC/RSS/latency/Shutdown); P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete linked Player. Original strict S custody Blocked, SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, independent full-stage R03 FAIL/re-review NotRun, uncapped 500ms/1..64 reporting/GC/logger/recovery/canary obligations remain. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No Human Review Gate/H2/X02/M08A permission.
