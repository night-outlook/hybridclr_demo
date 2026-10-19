# Primary Implementation → Local Validation — ONE 13-component P1 source/SDK preflight

**ONE NEW source-pinned, source/host/installed Unity2022.3.62f2 SDK SYNTAX-ONLY cycle is authorized after the exact repository/receipt gates below.** The Primary source and tooling are committed, pushed and read back through the GitHub Connector. This assignment does NOT authorize Unity Editor, Test Runner, Player, linked runtime execution, scheduler/engine experiments, another batch/retry, Human Review Gate, or a later milestone.

The last `20261018-5667` 12-component Local PASS is consumed. This is the new **13-component** command-failure plus original 12 source/SDK preflight, not a rerun of that old invocation. Local Validation owns factual execution and evidence only; all nontrivial implementation/architecture changes stay with Primary.

## Objective and single-cycle scope

Validate the published failure-aware P1 command receipts and batch stop semantics together with all retained source/host checks and the unchanged installed Unity2022.3.62f2 SDK syntax matrix in **one** source-pinned batch. The published code has 13 independently receipted components. This is not authorization for Editor, Test Runner, Player, linked runtime, a scheduler/engine experiment, a Human Review Gate, or another milestone.

## Required read order

1. `Docs/AssemblyShadow/README.md`, then `Plan/CURRENT_STATUS.md`.
2. Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, including the consumed `20261018-5667` report.
3. [Command-failure design](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/DESIGN.md), [Primary source review](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PRIMARY_REVIEW.md), [host evidence](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/EVIDENCE.json), and [publication reconciliation](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PUBLICATION.md).
4. The entire current `Handoff/WEB_TO_LOCAL.md` and exact four-repository source/transport checks before launching anything. Historical `PUBLICATION_BLOCKER.json` and `REMOTE_READBACK.json` are immutable **pre-publication snapshots**, not current blocker/HEAD evidence.

## Four exact repository/branch/source pins

All four canonical `night-outlook/<repo>` repositories use branch `codex/assembly-shadow-r01b-h1` and separate clean local checkouts. Verify canonical origin, local HEAD, remote HEAD and clean working tree in **every** repository; fast-forward clean ancestor trees only. The parent directory is not itself a Git repository.

| Canonical repository | Existing Local checkout path | Required exact source / remote HEAD |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | **Final handoff-containing, pushed and verified demo branch HEAD**, equal to `git log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md` and the exact 40-character SHA in the accompanying Primary handoff prompt. Source/host test anchor `d67846e9a28add70046198da9a4fba7e27f0764b`; all commits after this anchor must be Docs-only. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `e29a38f66331ccabe5822a9f83401cd4a2b20c5a` |

**Provenance:** The native Python failure-receipt change was published at `e29a38f66331ccabe5822a9f83401cd4a2b20c5a`, built on pre-existing native frozen-execution source commit `d8a1df3007e93aeb65dd9fe97ab96b4771de8f17`. That added inactive native feature is preserved but is **not separately qualified** by this tooling batch. The demo source/test/CI and historical evidence anchor is `d67846e9a28add70046198da9a4fba7e27f0764b`. GitHub Connector remote read-back for both source commits is documented in [PUBLICATION.md](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PUBLICATION.md). The final demo Docs-only handoff commit is authenticated independently by the accompanying exact-SHA Primary prompt and remote branch read-back. No smoke-test, local-only, older validation or unpublished SHA may substitute.

Do not edit historical `Tools/AssemblyShadow/R03/source-pins.json`: it belongs to earlier evidence. The candidate-native compiler switch passes `e29a38f66331ccabe5822a9f83401cd4a2b20c5a` explicitly. Confirm `git diff --exit-code d67846e9a28add70046198da9a4fba7e27f0764b HEAD -- . ':(exclude)Docs/**'` in the demo, and require handoff-file last-commit == HEAD. A later branch update invalidates this authorization until a fresh reviewed handoff.

Installed official Unity SDK anchor (read-only; **DO NOT launch Unity**): `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`.

## Implementation supplied by Primary

Native runner: exact captured stdout/stderr and receipts survive timeout/interruption/start failure; unknown exit/completeness/lifetime remain explicit. Missing compiler and postflight source loss retain failed summaries, and successful-compilation flags require actual successful compile commands.

Demo runner: strict nonmanaged receipt parsing/hashing, explicit stop on unknown command lifetime, NotRun records for all later planned cells, accurate SDK-attempt and aggregate fields, and no postflight Git subprocesses after an unsafe stop. The managed producer-binding consumer, all compiler helpers, production code, source-pin history and acceptance predicates remain unchanged.

The new `run_p1_command_failure_tests.py` invokes all 53 source-bound Python contracts as the first `command-failures` component. It includes controlled actual Python subprocess behavior, plus explicitly mocked Git/SDK/VM orchestration. No original source/SDK test component was removed. The additive focused GitHub CI workflows **PASSED** on both affected repos: [demo run 39208716350](https://github.com/night-outlook/hybridclr_demo/actions/runs/39208716350) and [native run 39208403729](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403729). The pre-existing separate inactive native owned-execution/R02 suite has a [macOS Clang CI failure at run 39208403669](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403669) (Linux Clang/GCC passed). **That distinct feature is not included or accepted in this assignment; it remains a Primary-owned issue.** No CI result substitutes for official installed SDK syntax or runtime evidence.

## Authorized 13-component single-batch matrix

| Component | Required result/evidence |
| --- | --- |
| command-failures | PassedWithinHostScope; 53 unique tests, 0 failures/errors/skips, source hashes unchanged; full unittest.log and RESULT/MANIFEST |
| legacy-host | Original PassedHostOnly host matrix, including source-bound byte comparisons and original negative controls |
| metadata-gate / bounded-class / bounded-physical | Three separate PassedWithinHostScope results with original source/admission/ownership limits |
| bounded-first-use | PassedWithinHostScope; original 15 groups per strict/sanitized profile |
| owned-general | PassedWithinOwnedHostScope; original 11 groups/profile, original byte parity and allocation assertions |
| live-general | PassedWithinInactiveSourceHostScope; original 13 groups/profile and four successful native compile/run receipts; exact actual method and original non-acceptance flags |
| bounded-status / bounded-inventory | Two separate PassedWithinHostScope results with original field/source controls |
| frozen-v2 | Original PassedWithinInactiveHostScope, full original transport negative controls, not Player integration |
| managed-sdk | Actual exact nested producer-bound receipt; five positive managed products and OriginalUnsignedCounts exit1/exactly two CS0266/no DLL |
| native-sdk | 75 actual C++17 macOS arm64 syntax commands, 15 units × candidate/debug/probe-off/diagnostics-off/feature-off; not linking |

The executable outer CLI is `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py`. After the source, remote, input, consumed-evidence and storage-admission checks below, execute exactly **one** command using the final verified handoff-containing demo HEAD:

```bash
set -euo pipefail
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
D="$W/hybridclr_demo"
B=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
SOURCE=d67846e9a28add70046198da9a4fba7e27f0764b
NATIVE=e29a38f66331ccabe5822a9f83401cd4a2b20c5a
DEMO_SHA="$(git -C "$D" rev-parse HEAD)"
test "$(git -C "$D" branch --show-current)" = codex/assembly-shadow-r01b-h1
test "$DEMO_SHA" = "$(git -C "$D" log -1 --format=%H -- Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md)"
test "$DEMO_SHA" = "$(git -C "$D" ls-remote origin refs/heads/codex/assembly-shadow-r01b-h1 | awk '{print $1}')"
git -C "$D" diff --exit-code "$SOURCE" "$DEMO_SHA" -- . ':(exclude)Docs/**'
python3 -B "$D/Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py" \
  --workspace "$W" --unity "$UNITY" \
  --expected-demo "$DEMO_SHA" --expected-native "$NATIVE" \
  --output "$B/R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a" \
  --sdk-scratch "$B/Scratch-R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a"
```

This invocation is consumed regardless of PASS/FAIL/Blocked. Do not retry, resume a child, or invent another root on failure. A terminal/unknown-lifetime result halts the batch; preserve its factual evidence.

## Evidence storage and execution admission

All prior roots ending `R03-P1-LIVE-GENERAL-20261018-5667` (raw, Scratch, Preflight) and the matching versioned checkpoint are consumed. Preserve their files, digests and verdicts. Do not resume, retry, rename a failed root, or reuse its compiled products as fresh evidence.

**This cycle exclusively authorizes the following ONE unused set**; all must be confirmed absent/canonical/mutually disjoint/from source & SDK and prior roots before execution, with sufficient approved external space:

- Raw batch: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a`
- SDK-copy scratch: `/Users/ah/GitHub/hybridclr/r03-local-validation/Scratch-R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a`
- Independent Local audit/authority: `/Users/ah/GitHub/hybridclr/r03-local-validation/Preflight-R03-P1-COMMAND-FAILURES-20261019-cmdfail-e29a`
- Additive checked-in evidence checkpoint: `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-command-failures-20261019-cmdfail-e29a/`

The independent audit root/checkpoint are Local-owned evidence and must not be precreated by the Primary batch script. Verify absence, space, clean branch/origin/HEAD/remote identity, source bindings, SDK before hashes and consumed historical original results/manifests/raw/scratch inputs before the one invocation. Preserve their bytes afterward. No vendor SDK binaries may be committed to Git.

## Results and failure handling

A full source/SDK PASS requires all **13/13** cells Passed, both SDK attempted/passed flags true, no stop marker, sourcePreserved=true, postflightError=null, exact source bindings, and unchanged historical evidence. Verify each inner receipt and compiler command; an aggregate label alone is insufficient.

Timeout/interruption/unknown lifetime must remain FailedOrIncomplete. Retained timeout bytes are captured prefixes, not complete output; missing streams remain Unavailable. Unknown exit is null. Subsequent cells are NotRun and must have no executed command/component-root evidence. `commandInvoked` is an invocation attempt, not spawn confirmation. `descendantQuiescenceProven=false` is intentional on every outer/native command even when no lifetime failure was witnessed.

After such a stop, do not manually launch the unrun children, rerun the batch, mutate compiler/source files, globally kill compilers or reset unrelated worktrees. Preserve the feasible observation inventory as UnsealedObservedFiles and return the unknown-lifetime condition to Primary. Local may collect bounded read-only process/environment diagnosis; it must not design a new process supervisor. Ordinary completed test/receipt failures may coexist with later independently completed cells, but cannot become overall PASS.

Keep warnings unsuppressed; counts are observations, not historical fixed targets. Preserve exact command/stream hashes, attempted/NotRun distinctions, input hashes and before/after evidence. Do not publish Unity vendor binaries or reinterpret historical FAIL as a fresh PASS.

## Local ownership and stopping point

Local may make factual updates only to `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and the separately designated additive checkpoint. No nontrivial product/test/tool/compiler changes, implementation from design prose, patch application, policy relaxation, unreviewed source pins, or new runtime work is delegated. On any substantive issue, retain evidence and return it to Primary.

P1 coherent VM-wide epoch/ABA protection, class-pointer provenance, complete execution/R02 capture, original live getter integration, worst-case allocation/GC/RSS, and true lock/Shutdown safety remain incomplete. P2 authenticated native/C# V2 transport/semantic integration remains NotIntegrated. E0 supported Unity2022.3.62f2 StandaloneOSX engine-owner safe point remains Blocked/Unavailable; E1 is BlockedByE0. Full P3 linked Player/runtime acceptance remains incomplete. These are Primary-owned work, not a Local implementation assignment.

The latest `20261018-5667` Local source/host/SDK PASS is consumed. The `20261016-3dc9`, `20261016-f598`, and `20261016-0620` source/SDK PASS cycles and `20261016-0a0b` FAIL remain unchanged. SNAP-01/N/M/K/I/E FAIL, historical R02 source-fingerprint FAIL, original strict S custody Blocked, and independent full-stage R03 FAIL/re-review NotRun are not reclassified.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion remains disabled.

**STOP after exactly one 13-component host/installed-SDK syntax-only invocation, independent raw evidence audit, and factual publication to LOCAL_VALIDATION.md / RETURN_TO_WEB.md / the single additive checkpoint. Return control to Primary. No further batch, runtime or Human Review Gate is authorized.**
