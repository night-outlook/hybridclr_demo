# Primary Implementation → Local Validation — ONE P1 owned physical-name source/SDK cycle

**Exactly ONE new source-pinned 18-component SOURCE/HOST + installed Unity2022.3.62f2 SDK SYNTAX-ONLY batch is authorized**, after the independent preflight below. Objective: validate the newly inactive owned physical display-name capture and retained source/SDK controls. This is **not** permission to launch Unity Editor, Test Runner, Player, run linked native binaries, seven-root SNAP-01, the engine-owner scheduler, a Human Review Gate, H2/X02/M08A or another milestone. Local does not own substantive code or compiler modifications.

## First reads and previous factual authority

1. `Docs/AssemblyShadow/README.md`, then `Plan/CURRENT_STATUS.md` at exact final demo HEAD.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` **first**, then `Handoff/RETURN_TO_WEB.md`, including the full consumed `20261020-699d` checkpoint and historical failure/custody limitations.
3. [New bounded design](../History/M07R/R03/IR_Remediation/P1_OWNED_PHYSICAL_NAMES_2026-10-20/DESIGN.md), [Primary review](../History/M07R/R03/IR_Remediation/P1_OWNED_PHYSICAL_NAMES_2026-10-20/PRIMARY_REVIEW.md), [machine evidence](../History/M07R/R03/IR_Remediation/P1_OWNED_PHYSICAL_NAMES_2026-10-20/EVIDENCE.json), and the earlier physical-membership design; then read this entire handoff and the original remaining P1/P2/E0/E1/P3 implementation plan.

**Consumed Local evidence:** `20261020-699d` **PASS / PassedSourceHostAndSDKOnly**: 16/16 independent outer components, 75 command-failure tests, five real official managed positive products plus exact expected-negative, 90/90 native Apple SDK C++17 arm64 syntax, immutable old source/installed SDK/history. It was not Unity Editor/Player or full runtime. All earlier P1 PASS/FAIL, original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked, and independent full-stage R03 FAIL/re-review NotRun remain unchanged. DO NOT rerun or reclassify any old evidence.

**Superseded intermediate handoff:** The original physical-membership source/SDK assignment at demo `d0bde05d2eb55da52c4ab35f4504d00897f951c5` was superseded by new source changes. No completed Local return for that intermediate tuple is recorded in the Local-owned report. Preserve any observed old root state and do not fabricate a PASS, FAIL or reusable root.

## Exact canonical repositories and branch

All four are independent clean canonical Git working trees on `codex/assembly-shadow-r01b-h1`. Their parent `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r` is NOT itself a Git repository. Verify canonical `night-outlook/<repo>` HTTPS/SSH origin, branch, worktree and submodule identity, exact local HEAD and live remote HEAD, no dirty paths. Fast-forward clean ancestors only; never `git reset --hard`, `git clean`, force-push, merge unrelated work or overwrite an uncommitted file.

| Repository | Existing Local checkout | Required final source |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final pushed handoff-containing Docs-only branch HEAD**, equal to the full 40-hex SHA in Primary's accompanying final Local prompt, exact live branch HEAD, local HEAD and `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. Tested demo source anchor is `6e3d84d649b5f0ff2d19df48f355c173ef2d0be9`; all commits after the anchor MUST change only `Docs/**`. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5` |

Historical `Tools/AssemblyShadow/R03/source-pins.json` records earlier executions and must NOT be updated or rebaselined. The current candidate native SHA is passed explicitly by `--candidate-native-sha` in the preserved SDK orchestration. Any later push after the final Primary handoff HEAD, including Docs-only, invalidates this authorization until Primary reviews and reissues it.

## Source changes completed by Primary — Local validates only

- `AssemblyShadowOwnedPhysicalNames.h` owns a fixed one-shot class-name table: **1,024 maximum matched observed classes**, **256 KiB raw owned name text**, **4,096-byte field bound**, capture object **<=512 KiB**. Each row stores exact copied `physicalAssemblyName`, `nameSpace`, `simpleName` spans with no retained physical pointer; it is **NOT a canonical execution TypeKey** and is not serialized as full execution JSON.
- `AssemblyShadowPhysicalMembership.h` exposes FirstMatch/DuplicateMatch/Ignored/Invalid results of the original bounded registry hash match, while preserving the old `void ObserveEnumerated` API. Only `FirstMatch` is permitted to borrow physical class names. Unrelated or duplicate physical iterator pointers are not dereferenced. All new owned buffers must be prepared outside metadata/registry lock scopes.
- New INACTIVE `AssemblyShadow::TryCaptureOwnedObservedPhysicalNames` is defined once by an additive `.inl` in real `AssemblyShadow.cpp` and declared under the existing feature switch. One initial-session metadata Reader surrounds bounded observed table capture, synchronous `il2cpp_class_for_each` under `g_MetadataLock`, subsequent witness/slot/revision/state verification under the short existing registry lock and source data revocation on failure. **Never nest the registry and metadata locks**. Missing type/image/assembly names, unknown iterator pointer, oversized names/text, source changes, count disagreement or name-sink reuse fail closed. No original getter, C# API or Player calls the new method.
- Native [source-host CI 39393569677](https://github.com/night-outlook/il2cpp_plus/actions/runs/39393569677) passed **3/3** Mac Clang/Linux Clang/GCC jobs, each **20 distinct strict and 20 ASan+UBSan groups**, five actual direct version/compile/run receipts, source SHA/bindings and old CPP/API header fingerprint equivalence. First native owned-name CI 39393330975 was a precompile fixture-label mismatch and remains historical FAIL; correction was label-only.
- Demo CI source/test anchor `6e3d84d649b5f0ff2d19df48f355c173ef2d0be9` adds the **18th** independent `owned-physical-names` host child with expected result `PassedWithinInactiveOwnedPhysicalNamesHostScope`, source-before/after hash coverage, typed lifetime result, fail-stop/NotRun safeguards and an official SDK syntax-only probe.
- Existing controlled command-failure inventory increases to **85 = 5+14+44+10+12** without removing any prior test. New five tests cover reported unknown lifetime, absent/string/null lifetime marker and missing child RESULT; unknown lifetime stops later subprocesses, no component roots for `NotRun` and no unsafe Git/source postflight. A completed safe child exit!=0 remains Failed without a fabricated process survivor.
- Official installed native SDK matrix expands to **100 actual Apple C++17 arm64 `-fsyntax-only` commands = 20 distinct native translation units × five unchanged candidate/debug/probe-off/diagnostics-off/feature-off profiles**; actual full `AssemblyShadow.cpp` with the .inl plus the new `AssemblyShadowOwnedPhysicalNamesSyntax.cpp` must compile in each. Original official managed SDK must freshly produce **five actual positives and one distinct `OriginalUnsignedCounts` expected-negative (exit1, exactly two CS0266, no DLL)**.
- Demo host [integrated CI 39394007824](https://github.com/night-outlook/hybridclr_demo/actions/runs/39394007824), [focused command failure CI 39394007860](https://github.com/night-outlook/hybridclr_demo/actions/runs/39394007860), [managed/aggregate CI 39394007845](https://github.com/night-outlook/hybridclr_demo/actions/runs/39394007845) passed on Mac/Linux. These are host/mock results, **NOT** the new official installed SDK or Player evidence.

## ONE unused raw/SDK/audit/checkpoint set — do not precreate/reuse

All FOUR roots MUST be **absent before Local preflight**, canonical, pairwise disjoint and outside every Git checkout, Unity installation, prior raw/scratch/audit/checkpoint or protected negative-control symlink. Local independently verifies every old P1 consumed manifest, source, installed SDK hashes, available external space and exact remote heads BEFORE creating any new root. The Local audit/checkpoint is created only AFTER admission and never by Primary. No Unity SDK/vendor/product binaries in Git.

- Raw: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3`
- SDK scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3`
- Independent Local authority/audit: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3`
- Additive checked-in checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-physical-names-20261020-e6a3/`

Read-only official Unity2022.3.62f2 SDK anchor (**do not execute Unity**):
`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Preserve inherited TMPDIR and unchanged compiler/private-temp lifetime policy.

## Exactly ONE command after independent admission

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=6e3d84d649b5f0ff2d19df48f355c173ef2d0be9
NATIVE=e6a350eb684a388b0c7a598f7ad0d1bae9b4f4e5
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3" \
  --sdk-scratch "$B/Scratch-R03-P1-OWNED-PHYSICAL-NAMES-20261020-e6a3"
```

This one-shot attempt consumes the fresh roots on PASS/FAIL/timeout/interruption/Blocked. **No retries, child resumes, changed suffix names, threshold relaxations or Local native/compiler fixes.** An unknown command/descendant lifetime stops later subprocesses, makes planned children `NotRun` without creating roots, and prohibits source/Git postflight until quiescence is independently established. Preserve complete/partial stream availability, null unknown exits, error codes and unsealed inventory, not fabricated positive SDK flags.

## Independent Local checks and return

Verify all **18** separate child receipts and their expected inner scope: `command-failures`, `legacy-host`, `metadata-gate`, `bounded-class`, `bounded-physical`, `bounded-first-use`, `owned-general`, `live-general`, `owned-execution`, `empty-live`, `opaque-inventory`, `physical-membership`, **`owned-physical-names`**, `bounded-status`, `bounded-inventory`, `frozen-v2`, `managed-sdk`, `native-sdk`.

To report `PASS / PassedSourceHostAndSDKOnly`, require 18/18 Passed, matching authenticated inner verdicts, `sourcePreserved=true`, `postflightError=null`, `stoppedAfter=null`, `commandLifetimeUnverified=false`, actual official SDK attempted/passed flags, exact four current clean local/remote source pins, no historical status reclassification and unchanged source/installed SDK/old consumed evidence before/after.

**New `owned-physical-names`:** inner `PassedWithinInactiveOwnedPhysicalNamesHostScope`; strict and ASan/UBSan each exactly **20 independently labeled case groups**, five direct compiler-version/compile/run commands exit0, complete stdout/stderr hashes and source hash preservation. Verify matched raw physical name bytes are copied and remain immutable after source string mutation, not class/assembly/image pointers or owned generic TypeKeys; missing/oversized names, incomplete matches, changed state/revision, invalid callbacks, reused scratch/capture all fail. Its actual production .h/.inl and callback classification must compile once. Assert `physicalClassPointerOriginProven=false`, `metadataPointerLifetimeProven=false`, `completeExecutionTypeKeys=false`, `coherentVmEpochProven=false`, `runtimeAcceptance=false`, `UnityPlayerExecuted=false`. A host PASS does not establish runtime memory or pointer ownership.

**Retained checks:** all 85 unique command-failure tests (5+14+44+10+12), 75 prior cases unchanged; physical-membership 21 groups/profile, opaque publisher 34/profile, empty-live 20/profile, owned-execution 6×35, live-general 13/profile, owned-general 11/profile, first-use 15/profile and complete legacy/frozen V1 byte parity/negative cases. Five *real* managed positives plus exact expected-negative must bind canonical producer stdout/nested receipt hashes. All **100 native official SDK arm64 C++17 syntax configs** (20 unique translation units × five modes) must be freshly compiled, with real `AssemblyShadow.cpp` and `AssemblyShadowOwnedPhysicalNamesSyntax.cpp`; warnings are observations, not to be hidden or copied as predicted values.

Preserve installed SDK, all earlier source/ABI pins and current actual checkout/remote integrity, historical SNAP-01/N/M/K/I/E/R02 FAIL, original strict S custody Blocked, R03 independent full-stage FAIL/re-review NotRun, all prior P1 raw/scratch/audit manifests/files, original negative symlinks, and complete source/SDK returned receipts. Keep `descendantQuiescenceProven=false` until independently proven.

Local may edit **only** factual `Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, and the single new additive checkpoint, plus bounded environment-only diagnosis. Commit/push factual evidence and return all four latest exact remote HEADs to Primary Implementation. **STOP after this one cycle** regardless of outcome.

## Remaining acceptance

P1 physical allocation/pointer lifetime, generic-aware execution TypeKeys, full owned nonempty execution JSON, VM-global coherent epoch/ABA, original getter integration, allocation/GC/RSS and Shutdown/lock proof remain **Incomplete**. P2 authenticated native/C# V2 transaction **NotIntegrated**. E0 supported StandaloneOSX engine-owner safe point **Blocked/Unavailable**, E1 drain/restart **BlockedByE0**, full P3 linked Player **Incomplete**. Original 500ms/1..64 uncapped semantic reporting/logger/GC/recovery/canary and V1/V2 budgets are fixed. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. No automatic Human Review Gate or next milestone.
