# Primary Implementation → Local Validation — ONE P1 registration witness source/SDK cycle

**Exactly ONE NEW source-pinned, source/host + installed Unity2022.3.62f2 SDK SYNTAX-ONLY cycle is authorized**, subject to all admission checks below. Objective: verify the new inactive registration-path source witness with the bounded opaque observed-class inventory and all retained P1 host/compiler contracts. It is NOT authority to launch Unity Editor, Test Runner, Player, linked native runtime, seven-root SNAP-01, an engine-owner scheduler experiment, Human Review Gate, H2/X02/M08A or a later milestone. Local may NOT change substantive implementation, tests, compiler procedures or design.

## Mandatory source/evidence read order

1. Docs/AssemblyShadow/README.md and Plan/CURRENT_STATUS.md at exact demo HEAD.
2. The Local-owned Handoff/LOCAL_VALIDATION.md **first**, then Handoff/RETURN_TO_WEB.md, including every historical result, failure and custody limitation.
3. [Registration witness design](../History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/DESIGN.md), [Primary source review](../History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/PRIMARY_REVIEW.md), [machine/source/CI evidence](../History/M07R/R03/IR_Remediation/P1_REGISTRATION_WITNESS_2026-10-20/EVIDENCE.json), then this WHOLE handoff and the unchanged P1/P2/E0/E1/P3 implementation plan.
4. Do not infer state or authority from chat history, source labels, CI widget statuses, or previous handoff revisions.

**Consumed Local factual result:** 20261020-f09e PASS / PassedSourceHostAndSDKOnly, 16/16 components, 75 unique command-failure tests, the exact original five managed positive products plus expected-negative compiler control and 90/90 Apple arm64 native SDK C++17 syntax. Its four execution commits, original raw batch, SDK scratch, independent audit and checkpoint are immutable. Every earlier P1 PASS/FAIL/Blocked is consumed. Original SNAP-01/N/M/K/I/E/R02 fingerprint FAIL, strict S custody Blocked and independent R03 full-stage FAIL/re-review NotRun remain factual. DO NOT rerun, reuse roots, alter or reclassify them.

## Four canonical repositories — one exact branch/tuple

All four nested paths are **independent Git working trees** on branch codex/assembly-shadow-r01b-h1, with canonical night-outlook origin, clean status, and identical local/live remote HEAD. The containing workspace directory is NOT a Git repository. A local branch may be safely fast-forwarded only when clean and the current ancestor is the specified source; never reset/clean, force-push, merge unrelated work, overwrite dirty files or invent a repo SHA.

| Canonical GitHub repo | Absolute existing Local checkout | Required pushed head |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | **Final pushed Docs-only handoff-containing HEAD**. Must equal the 40-char demo commit in the accompanying Primary Local prompt, the live remote branch SHA, the checked-out local HEAD and the last commit modifying Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md. The implementation/test source anchor is d7cbcc9deeb3d8f384887826bb8d65cec8324641. Every later commit MUST modify Docs/** only. |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | f0cb6f9f7a80c0601b5bc95c1a1cdda78a116e16 |

Historical Tools/AssemblyShadow/R03/source-pins.json remains untouched: it records previous actual source evidence, not the new candidate. The outer --candidate-native-sha selects the current native source without rebasing any historical FAIL/pin. Any new push AFTER final Primary handoff HEAD, even Docs-only, invalidates this authority until a new reviewed handoff.

## Primary completed source change and controls

- New native AssemblyShadowExecutionRegistrationWitness.h stores 2,048 fixed write-once source witnesses (opaque identity + Candidate or ActiveShadow). Each successful new ObserveExecutionClass insertion records its matching witness first, under the ORIGINAL ExecutionObservationLock and before pointer/count/revision publication. Missing registration drops the observation without publishing an unwitnessed class; no new class metadata dereference or lock.
- The inactive TryCaptureOpaqueExecutionInventory now checks every sample slot against its witness under the same existing short lock and an initial-session metadata-lifetime ticket, including empty-slot/phantom refusal. Candidate and active witnessed counts are compared across two original full 2,048-slot snapshots and the existing registry revision. It refuses missing, mismatched and phantom witnesses. Witness table bounded <=40,960 bytes, capture Scratch <=33,000 bytes; no raw class pointer is returned/dereferenced or serialized as JSON.
- **Registration-path admission is not safe physical pointer provenance**. It does NOT establish source lifetime across metadata teardown, true VM epoch or general ABA freedom, real class type keys/cctor/static fields, complete execution JSON, original getter replacement, GC/RSS/Shutdown safety or Player acceptance. Every existing physicalClassPointerOriginProven, coherentVmEpochProven, executionJsonComplete and runtimeAcceptance flag remains FALSE.
- Native source runner run_opaque_execution_inventory.py compiles EXACT production opaque header/inl and new witness header against controlled VM mocks; its byte-source audit authenticates original AssemblyShadow.cpp getter/guard code after removing only enumerated narrow additions. Host **25 distinct groups each strict and ASan/UBSan**, including retained 21 cases plus missing witness, mismatched pointer, phantom empty slot and active-shadow witness. **Five direct compiler-version/compile/run successful receipts** are required.
- Existing demo source/SDK orchestrator retains **16 independent components** and **75 unique source-bound Python command-failure tests (5+14+34+10+12)**. It now includes the new native witness header in before/after source hashes, fake-source tests and the SDK type probe.
- Official native SDK candidate syntax remains exactly **90 real arm64 C++17 syntax commands = 18 unique translation units × five unchanged candidate/debug/probe-off/diagnostics-off/feature-off profiles**, including actual full AssemblyShadow.cpp with new code plus AssemblyShadowOpaqueInventorySyntax.cpp witness-type checks. Five original positive managed compiler products and OriginalUnsignedCounts expected-negative (exit1, exactly two CS0266, no DLL) are unchanged.
- [Corrected native host CI 39366349420](https://github.com/night-outlook/il2cpp_plus/actions/runs/39366349420) passed 3/3 Mac Clang/Linux Clang/GCC, 25 strict/25 sanitized groups per job; the earlier failed source-audit comment CI 39366207558 remains historically FAIL, not reclassified. [Integrated demo CI 39366390774](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390774), [command-failure CI 39366390772](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390772), [managed/aggregate CI 39366390737](https://github.com/night-outlook/hybridclr_demo/actions/runs/39366390737) passed. These are host/mocked checks, NOT new installed Unity SDK syntax/Player tests at this four-source tuple.

## ONE new unused evidence root set

All four paths below must be **absent**, canonical and pairwise disjoint, outside the four checkouts, installed Unity Editor/SDK and ALL consumed P1 raw/scratch/audit/checkpoint roots. Independently verify exact four source and remote pins, original prior evidence/root inventories, all deliberate historical negative symlinks and enough approved external disk space BEFORE creating any output. Local's independent audit/checkpoint is separately owned; the Primary outer script must not precreate those roots.

- Raw: /Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-REGISTRATION-WITNESS-20261020-f0cb
- SDK scratch: /Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-REGISTRATION-WITNESS-20261020-f0cb
- Independent Local authority/audit: /Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-REGISTRATION-WITNESS-20261020-f0cb
- Additive checkpoint in demo: Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-registration-witness-20261020-f0cb/

Installed read-only Unity2022.3.62f2 native SDK anchor (DO NOT EXECUTE Unity):
/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity

Keep the inherited TMPDIR and original native/managed SDK compiler/private-temp policies; do not commit vendor SDK files, binaries or full test fixtures. Old roots may NEVER be reused or renamed to rerun.

## EXACTLY ONE source/SDK-only invocation after independent preflight

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=d7cbcc9deeb3d8f384887826bb8d65cec8324641
NATIVE=f0cb6f9f7a80c0601b5bc95c1a1cdda78a116e16
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-REGISTRATION-WITNESS-20261020-f0cb" \
  --sdk-scratch "$B/Scratch-R03-P1-REGISTRATION-WITNESS-20261020-f0cb"
```

ONE invocation consumes the roots upon PASS, FAIL, interruption, timeout or Blocked. NO retry, resume, root suffix change, standalone child re-execution, compiler threshold/SDK patch or manufactured PASS. An unverified command/descendant lifetime stops all subsequent subprocesses, records later planned cells as NotRun without component roots and forbids source/Git postflight while descendants may survive. Preserve all partial streams and the factual unsealed evidence. A known completed nonzero is Failed but does not imply unknown descendant lifetime.

## Required Local verification and factual return

Inspect each of **16 distinct** outer cases, not only aggregate: command-failures, legacy-host, metadata-gate, bounded-class, bounded-physical, bounded-first-use, owned-general, live-general, owned-execution, empty-live, opaque-inventory, bounded-status, bounded-inventory, frozen-v2, managed-sdk and native-sdk.

A new PASS / PassedSourceHostAndSDKOnly requires all 16 exact Passed, sourcePreserved=true, postflightError=null, stoppedAfter=null, truthful attempted/passed SDK flags, four clean canonical source/remote pins, source and SDK preservation and no historical reclassification. Inspect all actual child status/verdict/path/stream/manifest hashes.

- Opaque inventory: **25 distinct groups per strict/sanitized profile**, five native compiler-version/compile/run successes with actual raw stdout/stderr and source SHA binds. Source-authenticated fixture assertions must reject missing, wrong-identity or phantom registration witnesses; accept an explicit valid ActiveShadow witness; preserve all prior slot/revision/stability/refusal cases. The positive source-host runtime assert registrationWitnessesObserved=true is from the fixture, NOT an independently emitted per-case numeric JSON sample. The actual host RESULT must retain physicalClassPointerOriginProven=false, coherentVmEpochProven=false, completeExecutionSource=false, UnityPlayerExecuted=false, officialUnitySdkCompiled=false, runtimeAcceptance=false.
- All 75 source/host command-failure contracts (5+14+34+10+12) and prior native suites must remain intact: live-general 13/profile, owned-general 11/profile, first-use 15/profile, owned-execution 6×35, empty-live 2×20 plus all exact V1, invalid-input, fail-stop/NotRun and frozen-V2 controls.
- Official native SDK must freshly execute **90/90 actual** C++17 Apple arm64 syntax configurations: 18 units × five unchanged modes, including full exact current AssemblyShadow.cpp and the new registration witness header through the existing opaque syntax probe. Verify scratch SDK input sources, compiler receipts, warnings, source-to-command SHA and unchanged installed SDK. Managed SDK must freshly compile exactly five original positive products and the distinct original negative exit1/exact two CS0266/no DLL with independently joined nested producer receipt path+SHA.
- Verify ALL consumed source/SDK/history original raw/batch/manifests, independent audits, SDK scratches and original negative symlink controls preserved byte-for-byte. Historical 0a0b failure, d16d finding, source fingerprint FAIL, strict S custody Blocked and R03 independent full-stage FAIL/re-review NotRun remain unchanged; do not invent or import a Player result.

Local may modify ONLY the factual Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md, RETURN_TO_WEB.md and the single new additive checkpoint, plus separately owned bounded environment-only audit data. No native/demo substantive fixes. Commit/push evidence and return the exact four-source tuple, independent raw/audit receipts and factual PASS/FAIL/Blocked.

## Stop and acceptance policy

**STOP after ONE bounded source/host/SDK cycle**. Do not begin Player, E0/E1, next milestone, Human Review Gate or another Local attempt. P1 remains Incomplete for actual class origin/lifetime, type-key/complete nonempty execution JSON, all-VM coherent epoch/ABA, real allocation/GC/RSS/locks/Shutdown and original getters. P2 NotIntegrated; E0 Blocked/Unavailable; E1 BlockedByE0; full P3 Incomplete. Keep original V1/V2 budgets, 500ms/1–64 uncapped report, logger/GC/canary/recovery predicates fixed. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; fullLegacyRegressionAcceptance=false; PureInterpreter disabled.
