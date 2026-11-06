# Primary Implementation -> Local Validation — CONDITIONAL initializer oneuse-03 (2026-11-06 UTC)

**New, single-use authority; NOT a replay.** Consume this document only
with the latest pushed 40-character demo HEAD from the Primary final
handoff prompt. Source preparation is complete, but a real Unity/Player
execution **has not been run** for oneuse-03. Never reuse, reseal or
rewrite the prior oneuse-01 (BLOCKED) or oneuse-02 (FAIL, two Players
exit2 and original product seal Failed), or any historical S/K/I/J
evidence. Preserve all source/custody files unchanged.

Current objective: diagnose both
`IR-LOCAL-R03-INITIALIZER-02-PLAYER-01` and
`IR-LOCAL-R03-INITIALIZER-02-SEAL-02` in **one** new 15-cell batch.
Read the complete [design](../History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/DESIGN.md),
[plan](../History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/PLAN.md)
and [Primary review](../History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/PRIMARY_SOURCE_REVIEW.md)
before any Local execution.

## Frozen source authority

| Repository | Feature branch | Exact source commit |
| --- | --- | --- |
| night-outlook/hybridclr_demo | codex/assembly-shadow-r01b-h1 | **Latest final pushed full SHA from this conversation's Primary handoff prompt**. Resolve it against actual clean checkout and live remote, not the earlier test source SHAs. |
| night-outlook/hybridclr | codex/assembly-shadow-r01b-h1 | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | codex/assembly-shadow-r01b-h1 | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | codex/assembly-shadow-r01b-h1 | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

All four repository root paths:
`/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/{hybridclr_demo,hybridclr,hybridclr_unity,il2cpp_plus}`.
Each has its own .git root; never infer a parent Git repository.
Do not use prior execution demo
`7da27a486b529cdebf73100b5ce4c332a1bb7e86` or its
evidence publication `61bf436d65e5909767206d385ecba865e4c7a5ac`
as current executable source authority.

Historical original S:
`/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse`
must stay clean and detached at
`fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
Production VM, interpreter, package, original S and K runners remain
byte-unchanged in this source cycle.

## Mandatory first reads and exact CI

1. `Docs/AssemblyShadow/README.md`; THIS canonical live handoff.
2. `History/M07R/R03/IR_Remediation/INITIALIZER03_PLAYER_SEAL_REPAIR_2026-11-06/{DESIGN.md,PLAN.md,PRIMARY_SOURCE_REVIEW.md}`.
3. `Tools/AssemblyShadow/R03IR/run_initializer_local.py`,
   `initializer_host_custody.py`, `verify_initializer_trace.py`,
   `PlayerProject/R03InitializerObservation{Writer.cpp,Player.cs}`,
   `PlayerProject/R03InitializerPreparedProbe.cpp` and their new host tests.
4. `Handoff/RETURN_TO_WEB.md`, oneuse-02 actual raw/finding,
   oneuse-01 blocked checkpoint, original S/K source and prior custody
   history. `Handoff/LOCAL_VALIDATION.md` is Local-owned.

Two **mandatory exact-FINAL-demo-SHA GitHub Actions workflows**
must each have completed/success on macOS 15 **and** Ubuntu 24.04.
The initializer workflow's earlier macOS-14 jobs were cancelled without
a verified success; those cancelled jobs are not admissible evidence:
- `.github/workflows/r03-ir-initializer-local-contracts.yml`:
  real C++11 native observer/writer hosts, standalone Player
  orchestrator, strict diagnostic parser, source preparation, source
  admission and symlink-free seal/custody synthetic negatives.
- `.github/workflows/r03-ir-current-native-local-cycle-host.yml`:
  complete **real** ten-component native-host CLI using actual
  pinned source checkouts, four symlink identities, regular-byte
  custody and the existing generic product seal on both OSes.

Also independently verify the source-bound managed Player API compile
CI completed successfully for this **unchanged Player C# source blob**
(at final SHA if that workflow runs, otherwise the last exactly matching
source commit). On any missing, cancelled, skipped, failed, wrong-SHA,
or wrong-OS required CI outcome: **NO-GO, do not create new roots**.
Historical CI success is not current Player evidence.

## Strict read-only Local GO/NO-GO

Exact new canonical paths:
~~~bash
WORKSPACE=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
ORIGINAL_S=/Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse
UNITY_EXE=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
RUN_ROOT=/Users/ah/GitHub/hybridclr/r03-local-validation/R03IR-Initializer-20261106-oneuse-03
HOST_RAW="$RUN_ROOT-native-host-raw"
# DEMO_COMMIT is the 40-character final Primary pushed SHA, never K/01/02.
~~~

Both RUN_ROOT and HOST_RAW must be **absent** and canonical, distinct
from all repository/historical/evidence paths and each other.
Require four clean Git roots (canonical origin, branch and exact live
remote commit), retained original S authority, pinned macOS arm64 Unity
2022.3.62f2/IL2CPP/SDK and no conflicting Unity/Bee/Players.
Preserve every previous checkpoint (including consumed 02 failed
raw/product seal) before/after. Take **two fresh separate timestamped
free-space samples** on the exact shared output parent; BOTH >=25.0GiB.
The hard 20GiB/advisory 40GiB constraints remain unchanged; the 25GiB
conditional exception applies ONLY to oneuse-03. Historical 01/02
capacity receipts cannot serve as admission, and no unapproved
cleanup, volume redirection, root alias or retry is permitted.

Before any write, execute the unchanged admission:
~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/current_native_environment_admission.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~
Check the genuinely uncreated HOST_RAW sibling separately. Any failure:
BLOCKED/STOP, no runner invocation, no new root.

## ONE authorized batch after GO

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$WORKSPACE/hybridclr_demo/Tools/AssemblyShadow/R03IR/run_initializer_local.py" \
  --workspace "$WORKSPACE" --original-s "$ORIGINAL_S" \
  --unity "$UNITY_EXE" --demo-commit "$DEMO_COMMIT" --output "$RUN_ROOT"
~~~

Fixed 15-cell scope:
- Genuine ten-host native C++11 tests plus all new additive
  initializer host/synthetic negative tests.
- Original read-only S nine-part archive/90 cells/59 process
  joins/generated C++ lexical/Mach-O symbol identity audits.
- Deterministic separate Methods.dll target fixtures, isolated
  initializer composite overlay and exact one ON/Release macOS
  ARM64 Unity 2022.3.62f2 IL2CPP BuildReport.
- Two separate actual Players:
  `initializer-control`, Commit0/state6, and
  `initializer-failure`, Commit19/state9 with true postterminal
  attempted and denied AOT canary. Strict prepared field3,
  pre-positive mask15, callback exactly once, canary1→1.
- New preopened native diagnostic journal has exact request/PID/
  fixture and typed phase/reason even when strict `raw.json` is empty.
  **Never relabel a diagnostic as accepted V1, V2 or Player PASS.**

Actual complete host raw tree with FOUR intentional symlinks is
preserved under HOST_RAW. The in-batch
`host-custody/{HOST_MANIFEST.json,HOST_REGULAR_BYTES.tar.gz,HOST_CUSTODY_RESULT.json}`
binds every regular byte and literal symlink identity to the strict
product seal. Do not follow or remove any raw host symlinks.
`R03/batch_evidence.py` is unchanged and must remain strict.

## Results, failure evidence and publication

For EACH Player retain request, OS-PID command/exit/argv/stderr,
Player.log, original raw.json byte size/digest, exact new
`raw.json.native-trace.jsonl` bytes/digest when present,
`verification.json/nativeDiagnostic`, compiled binary and BuildReport
provenance. On nonzero exit the semantic verifier remains
`NotRun_CommandFailed`; report any stage300 native callback code,
phase900 last managed stage and native Seal phase610 reason separately.
If no journal is available, classify it Unavailable instead of
inventing a diagnostic.

Verify full host custody + external raw HOST_RAW symlink count/targets,
regular bytes and postflight match; ensure the actual product archive
has exactly its indexed regular members, hashes, and full content.
Preserve `BATCH_EXECUTION.json` and `LOCAL_BATCH_RESULT.json`,
`evidence-index.json`, `evidence.tar.gz`,
`seal-receipt.json` or original `SEAL_FAILED.json`. A PASS of the
seal alone cannot upgrade a Failed Player or full R03 acceptance.
Final absolute evidence and source tuples must be independently
inspected and checked.

Publish one **new additive** checkpoint:
`Docs/AssemblyShadow/History/M07R/R03/local-validation-initializer-20261106-oneuse-03/`
with original raw preserved externally (both RUN_ROOT and HOST_RAW),
a complete SHA/path/symlink manifest, exact execution demo SHA vs
later evidence publication SHA, source/build/Player/host verdicts,
and separate failures/NotRun/NoCoverage. Update Local-owned
`Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`,
commit/push and verify live remote heads. Local may do only a bounded
immediately verifiable unblocker; **all non-trivial source fixes return
to Primary**. Do not repeat a consumed cycle, self-review/approve
Human Review Gate, or continue to H2/M08A/X02/SNAP-01.

## Immutable acceptance boundary

Independent High `IR-R03-01/02` remain open. Captured-generic
error15, full V2/first-failure/general diagnostics, original S
source/object/link/Player closure, managed Unity shutdown, GC/RSS,
whole-VM epoch, P1/P2/E0/E1/P3, RC1–RC6, performance and full
legacy regression remain NotProven/NotRun.
`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false;
runtimeAcceptance=false; qualificationApproved=false;
fullLegacyRegressionAcceptance=false`. PureInterpreter disabled.
