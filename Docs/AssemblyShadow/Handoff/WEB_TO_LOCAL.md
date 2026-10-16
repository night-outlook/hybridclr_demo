# Primary Implementation → Local Validation — one new owned general V1 source/SDK preflight

**ONE NEW eleven-component, source-bound host and official Unity SDK SYNTAX-ONLY cycle is authorized.** The goal is to validate the already published P1 owned general JSON composer against its actual production headers and current Unity2022.3.62f2 macOS arm64 SDK, together with the retained ten components. There is NO authorization to launch Unity Editor, Test Runner, Player, run a linked runtime, repeat SNAP-01, reuse any historical evidence root, start an engine-owner adapter, proceed to a new milestone, or enter a Human Review Gate.

**Ownership:** Local Validation executes and publishes only factual results. All nontrivial source/architecture/test/procedure changes belong to Primary Implementation. On failure retain the first raw error and return without in-place repair/retry.

## Read first

1. Docs/AssemblyShadow/README.md, then Plan/CURRENT_STATUS.md.
2. Factual Local-owned Handoff/LOCAL_VALIDATION.md and Handoff/RETURN_TO_WEB.md.
3. [Primary owned-general review](../History/M07R/R03/IR_Remediation/P1_OWNED_GENERAL_COMPOSER_2026-10-16/PRIMARY_RECONCILIATION.md) and [machine evidence](../History/M07R/R03/IR_Remediation/P1_OWNED_GENERAL_COMPOSER_2026-10-16/EVIDENCE.json).
4. [Previously consumed first-use source/SDK PASS](../History/M07R/R03/local-validation-p1-firstuse-class-20261016-f598/README.md), [receipt PASS](../History/M07R/R03/local-validation-p1-managed-receipt-20261016-0620/README.md), and [earlier FAIL](../History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/README.md).
5. This complete handoff, all constraints and acceptance boundaries.

## Source identity, branch, exact checkout paths

All four canonical GitHub repositories must be clean, on branch codex/assembly-shadow-r01b-h1, with origins resolving to night-outlook/<repo>. Local checkouts (not touched by Primary):

| Canonical repository | Exact Local checkout | Required pushed source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Latest remote SHA matching this handoff and the final Primary handoff message; verify that all changes since tested demo source anchor 85257e495a141e553b56bc1ef47369eb36f572a5 are Docs-only |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | 3dc9b848d1d6b7616b257c95dc4727db06fd05f7 |

The demo source/CLI CI anchor 85257e495a141e553b56bc1ef47369eb36f572a5 precedes Docs-only publication. Native source CI [38885246083](https://github.com/night-outlook/il2cpp_plus/actions/runs/38885246083) at exact current native head Passed 3/3 jobs. Demo regression CI [38885611665](https://github.com/night-outlook/hybridclr_demo/actions/runs/38885611665) at exact demo tooling anchor Passed 2/2 jobs. Each CI artifact's GitHub ZIP digest and all 61 combined manifest entries were independently verified by Primary. These host/mock checks do NOT count as the new official installed SDK results.

Historical Tools/AssemblyShadow/R03/source-pins.json is intentionally retained at the older actual Local execution source; do not change it. The new wrapper passes the explicit native candidate SHA 3dc9b848d1d6b7616b257c95dc4727db06fd05f7 to the candidate native syntax compiler. Preserve the previous R02 whole-file historical fingerprint FAIL as a separate identity contract; do not retrofit its expected hashes to make it green.

**Preflight requirement:** verify exact GitHub repository identities, clean ancestor-only fast-forward, branch and remote HEAD for each. If any checkout is dirty, divergent, unexpected, remote-inaccessible or source-changing after preflight, record Blocked/Failed and STOP. Never reset, clean, force-push, or modify unrelated worktrees.

## Implementation already completed by Primary

Native (il2cpp_plus):
- New libil2cpp/vm/AssemblyShadowBoundedGeneralComposer.h: pure synchronous composition of completed owned inventory, first-use, physical and class captures into the original V1 field sequence. Matching physical/class generation required; does not prove global VM coherence.
- Extended libil2cpp/vm/AssemblyShadowFrozenGeneralCapture.h with one fail-closed invalid-source method.
- Actual production header/original-serializer parity fixture, strict/sanitized C++ runner and CI workflow under tools/r03/diagnostic_stream and .github/workflows.

Demo:
- Existing Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py now includes eleventh owned-general component with same source-preservation, per-child logging and fail-closed contracts.
- Candidate native_validation.py adds an actual standalone SDK parser translation unit Tools/AssemblyShadow/R03IR/PlayerProject/AssemblyShadowGeneralComposeSyntax.cpp. The candidate matrix is now **15 actual C++ units x five profiles = 75 configurations**. Noncandidate historical 12x5=60 behavior is unchanged.
- Updated CLI/managed-receipt regression tests; the existing managed compiler still builds five real positive product targets and preserves the exact expected-negative OriginalUnsignedCounts exit1/two CS0266/no DLL.
- No source or interpreter policy, original general/execution getter, managed Player, native V2 transport or engine lifecycle has been modified by this increment.

## One fresh batch — unused storage roots only

Use these new names ONLY if all paths are absent, canonical and disjoint from other evidence/SDK/install/source trees, with approved volume/capacity/custody:

- Evidence: /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-OWNED-GENERAL-20261016-3dc9
- External copied SDK scratch: /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-OWNED-GENERAL-20261016-3dc9
- Independent Local preflight/authority: /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-OWNED-GENERAL-20261016-3dc9
- Additive Git evidence: Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-owned-general-20261016-3dc9/

Installed official SDK anchor (read only; DO NOT execute binary): /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity.

After validating absence, external separation, complete before-source/installed-SDK/older-evidence hashes and safe storage conditions, run exactly ONCE:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
DEMO_SOURCE=85257e495a141e553b56bc1ef47369eb36f572a5
NATIVE=3dc9b848d1d6b7616b257c95dc4727db06fd05f7
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
git -C "$D" diff --exit-code "$DEMO_SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-OWNED-GENERAL-20261016-3dc9" \
  --sdk-scratch "$B/Scratch-R03-P1-OWNED-GENERAL-20261016-3dc9"
```

## Expected results and evidence to retain

**Exactly 11 outer components:** original retained host suite, metadata admission gate, bounded ordinary class reader, bounded physical assembly reader, bounded first-use class capture, NEW owned-general byte composer, bounded transaction status, bounded transaction inventory, frozen V2 execution, official managed SDK, and official native SDK.

Require owned-general child result **PassedWithinOwnedHostScope** with strict and sanitized profiles, **11 distinct groups/profile, four compile/run exits 0, real production headers/original V1 serializer compiled, zero allocations after locale prewarm**, source hashes and manifest preserved. It must demonstrate whole original general JSON byte equality under independently populated owned fixtures, in-memory source ownership, generation-mismatch refusal, inactive/partial-output refusal, 3,932,160-byte frozen general capacity and invalid UTF-8, and receipt fields explicitly stating globalVmEpochProven=false and runtimeAcceptance=false.

Require five official managed positive products plus original expected-negative control, the corrected returned binding for managed-sdk/build-api/results.json with SHA256/inner Passed/outer Passed and returnedBindingVerified=true. Require all **75** official native C++17 arm64 syntax configurations (15 source units x five candidate/debug/probe-off/diagnostics-off/feature-off profiles), including full Runtime.cpp, AssemblyShadow.cpp, Assembly.cpp, AssemblyShadowVisibility.cpp, original general serializer and the NEW composer-probe C++ unit. Bind every compiler profile, argv, stdout/stderr and source/input hash; preserve all warnings and expected negative controls.

Aggregate success only if **11/11 Passed**, result PassedSourceHostAndSDKOnly, sourcePreserved=true, postflightError=null, both SDK attempted/passed flags true, expectedNativeSyntaxUnits=75, strict source identities, no Unity Editor/Player, and no historical result reclassification. Read all individual command receipts and nested results, not only the aggregate flag. Preserve all original actual source, official installed SDK inputs, scratch, before/after and consumed PASS/FAIL evidence; separately authenticate any deliberate negative-control symlinks via nested manifests. Do not compress away warning/error streams.

**Any observed failure is Failed/Blocked/Unavailable/NotRun as factually supported, never promoted from host mocks.** Retain the one attempt's raw logs, output records and independent audit. Do not rerun or invent a new root to hide a failed attempt. Local may make only bounded environment diagnoses, never design/refactor native, compiler, test harness, SDK source, scheduler or transport logic.

Publish one additive new factual checkpoint and update ONLY Local-owned Handoff/LOCAL_VALIDATION.md and Handoff/RETURN_TO_WEB.md as needed; commit/push factual reports/evidence via canonical GitHub. Never commit Unity vendor binaries; preserve external binaries by exact path/hash and publication receipts. Return exact source/branch/commit tuples and any first substantive issue to Primary.

## Open engineering gates and stop

**P1 Incomplete:** the composer is only an inactive owned-source stage, not a coherent admitted VM/live general+execution capture, an authenticated class-pointer-origin/ABA proof, a real bound on type-key/metadata lock/GC/RSS/teardown, or a replacement for original allocating getters. P2 native/C# authenticated V2 artifact/envelope and unchanged original semantic verifier remain NotIntegrated. E0 Unity2022.3.62f2 StandaloneOSX source/vendor-supported engine-owner capability remains Blocked/Unavailable; E1 native maintenance/drain/restart BlockedByE0. Full P3 is not certified by SDK syntax. The earlier engine witness is still Failed with 51213 uncapped reports/500ms/exit71.

Previous 20261016-f598 PASS, 20261016-0620 PASS, and 20261016-0a0b FAIL are consumed; SNAP-01/N/M/K/I/E FAIL, strict S custody Blocked and historical independent R03 review FAIL/rereview NotRun are preserved. All V1/V2 capacities, original 500ms report count and original recovery/logger/GC/canary semantics are unchanged.

R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled.

**STOP after exactly this ONE host/SDK-only cycle.** Return to Primary Implementation. No subsequent Unity/Player batch, additional source work, E0/E1 implementation, Human Review Gate or H2/X02/M08A is authorized by this document.
