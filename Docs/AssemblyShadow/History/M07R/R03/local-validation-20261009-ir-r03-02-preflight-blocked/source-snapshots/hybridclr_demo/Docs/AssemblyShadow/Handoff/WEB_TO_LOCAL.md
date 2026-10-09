# Primary Implementation → Local Validation: R03 IR-R03-02 focused, conditional

**New focused Local Validation is authorized only after every preflight below passes.** This does **not** authorize rerunning S/R/Q/P/O/N, changing old evidence, repairing retained R, declaring R03/H2 approval, enabling PureInterpreter structural expansion, or starting M08A/X02. The earlier independent full-stage R03 verdict remains **FAIL**.

## Read order

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md` and this handoff.
2. [Focused validation procedure](../History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md) and [exact immutable-fixture policy](../History/M07R/R03/IR_Remediation/IR_R03_02_FIXTURE_PROVENANCE_2026-10-09.md).
3. [Native IR implementation design](../History/M07R/R03/IR_Remediation/IR_R03_02_NATIVE_DESIGN_2026-10-08.md), [original independent FAIL review](../History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) and its C04 citation erratum in the same directory.
4. Historical Local-owned `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and [original S correction](../History/M07R/R03/IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json).
5. Original R03 Design/Plan, HUMAN_REVIEW_GATES and recorded D1=A/D2=A scope. Do not infer additional authorization from chat history.

## Repository, branch and source authority

All four branch names: **`codex/assembly-shadow-r01b-h1`**; workspace `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`. **Use the exact latest four pushed SHAs in the final Primary handoff prompt**. Its `hybridclr_demo` HEAD must be a **Docs-only descendant** of source freeze `3eb309a1f82a9c7d4199a8499b95144a78cbdd24`, and the other three must equal this table:

| Repository | Local owning path | Exact source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Final handoff demo commit; executable source frozen at `3eb309a1f82a9c7d4199a8499b95144a78cbdd24` |
| night-outlook/hybridclr | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `9ce1c1bfec9a21b92ea300acda5f27a3815b2c37` |

The repository source manifest `Tools/AssemblyShadow/R03/source-pins.json` must bind the exact three non-demo commits above. Verify each real checkout separately: branch, clean worktree, HEAD, canonical origin, fresh `git ls-remote` matching HEAD. Refuse dirty, unpushed, switched, stale or unmatched sources. Do **not** reset, stash, clean, move, delete or repair the checkout for convenience.

**Historical S is not the runtime input pin.** S executed `hybridclr_demo@29bb3d4a39bf8a2f23be404f77535aaba3485bfc` with `il2cpp_plus@1cf87f8209790f9fb2ebec97487dc1990ccd56c5`, and its evidence was published at demo `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`. These immutable records remain separate from the new feature candidate.

## Completed Primary implementation and verified preconditions

- Implemented native terminal business-entry denial in `il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowTerminalExecution.h`, retaining first-failure facts and narrow physical corelib exception-constructor allowance; host-policy [run 37872834945](https://github.com/night-outlook/il2cpp_plus/actions/runs/37872834945) **Passed Linux and macOS**. No API/ABI layout expansion was authorized.
- Prepared `Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs`, opt-in native test stimuli in `R03/PlayerProject/AssemblyShadowR03Probe.cpp`, one-shot `run_terminal_local.py`, strict verifier tests, and conservative `run_terminal_storage_checked.py`.
- **Original S inputs**: not regenerated. `ir_original_fixtures.py` authenticates/copies the original **15 committed S DLL Git blobs** from publication `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`, inventory Git blob `0688bd2dad054bd59fcdd1564a050a398cfa14e7`, into a fresh isolated IR build source. Any content/commit mismatch prevents Player execution.
- **New IR-only Methods target** (distinct from S) SHA-256 `8d0b28cbca4d889801883ad436c51c215b913f1645055590980f902f1e80fffd`, MVID `597eb18e-e0e7-6f8b-7e4a-6cdaabf9d1ff`, 2,048 bytes, zero PE timestamp. Exact deterministic inputs/source-copy [run 37894308627](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894308627) **Passed on Linux/macOS** with eight host negative tests per platform. The earlier S *regeneration* comparison and same-source non-repeatability experiments remain **Failed/NotIdentical**, not retconned as passing or as evidence that S changed.
- [Official Unity 2022.3 pinned API and native source compile run 37893353097](https://github.com/night-outlook/hybridclr_demo/actions/runs/37893353097) **Passed** with the same new native source and deterministic IR generator. [C# supplementary Player API run 37874183375](https://github.com/night-outlook/hybridclr_demo/actions/runs/37874183375) Passed with 0 errors, 13 warnings.
- [IR host contract run 37894749414](https://github.com/night-outlook/hybridclr_demo/actions/runs/37894749414) **Passed 64 tests each** on Linux and macOS, including terminal receipt mutation, exact Git input and 64GiB/20GiB conservative storage gates. No Unity Player was launched in any of these host checks.

**Limits:** Four new fresh Players are a focused source-bound test, **not complete IR-R03-02 or IR-R03-01 independent closure**. Genuine captured-generic and post-publication initializer-failure post-poison paths and broader legacy/production SLA are still unproved. A green host/SDK compile result cannot be called fresh Player execution.

## Preflight, fresh directories, and execution

Local uses Unity 2022.3.62f2 (`/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`), macOS arm64; net8-capable dotnet, Python 3.14. Do not launch Unity 6000. Perform all read-only source, Q/S custody, host-test and full capacity checks from the [focused procedure](../History/M07R/R03/IR_Remediation/IR_R03_02_FOCUSED_LOCAL_PROCEDURE_2026-10-09.md). Native `c++` policy tests and Python host suites must pass in the actual Local environment.

Use exactly these **currently expected unused** external paths; if any already exists or aliases/symlinks a historical source, **CapacityBlocked/NotRun** and return to Primary for a distinct authorized root:

- IR batch root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03IRLocal-20261009A-terminal`.
- Diagnostic-only sidecar `/Users/ah/GitHub/hybridclr/r03-local-validation/StorageCheck-R03IRLocal-20261009A-terminal`.
- Separate executing sidecar `/Users/ah/GitHub/hybridclr/r03-local-validation/Storage-R03IRLocal-20261009A-terminal`.
- **Read-only** retained Q root `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261006Q-lp-repair`.

Use the new `Tools/AssemblyShadow/R03IR/run_terminal_storage_checked.py` **without** `--execute` first, setting `EXPECTED_DEMO_COMMIT` to the **exact** SHA in the final Primary prompt, and read its fresh `admission.json`, capacity samples and source authority. The wrapper enforces the existing `R03StorageAdmissionV1` Q failure-cell check, full Q size and `max(64GiB, 2*Q+20GiB)` headroom, fsync/readback probes and 20GiB sampled running floor. No thresholds, temp paths, quota policies, retry/cleanup or source pins are weakened. **Diagnostics-only runs must never launch Unity.**

Only with Passed fresh diagnostic, clean exact pins, source/blob/native tests and all prerequisites, run **one executing invocation** of the same wrapper with fresh *different* storage sidecar and `--execute`. It remeasures/probes from scratch and starts exactly **14** scheduler cells: 3 build roles (ON Release, ON Debug, OFF Release) and 4 fresh Player processes. It writes separate storage telemetry/session/dispatch receipts and the original focused sealed result. There is no attempted continuation, phase retry, or resume of a failed execution.

Preflight/failures must preserve the original error/output and return without launching/retrying other Players. If capacity is Blocked, do not treat the diagnostic no-launch result as a runtime Fail or a qualification verdict.

## Exact expected Player assertions and returned evidence

The ON Players must show the **same valid active `Methods.R03.Node.Keep` reflection/delegate** returning 42 and incrementing its own real instance `stable` counter to 2 **before** failure, followed by a caught original baseline-owner or synthetic type-resolution terminal failure. Afterwards actually attempt those same reflection and delegate calls and a retained ordinary AOT canary. None may succeed or change the active counter or AOT canary. Read the active field **after** failure; a failed/unrecorded read is not a passing proof. First recovery reason, terminal state/generation and fixed diagnostics must remain stable. The OFF control must invoke its ordinary AOT canary twice with no Shadow transaction.

Preserve signed/pinned source inventory, exact original S 15-blob source receipt, distinct IR target MVID/SHA, 3 real native build receipts, 4 raw Player JSONs/logs, invocation PID/nonce/request/argv/build bindings, all 14 cell receipts, JSON ledger/index/archive/seal, capacity admission/samples/dispatch and original Q/S/R custody. Any missing source/authenticity, build, Player or receipt is a **Failed/Blocked/NotRun** fact, not inferred success.

Return factual results in Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md`, publish an additive immutable checkpoint under `Docs/AssemblyShadow/History/M07R/R03/`, read back remote SHAs and return to **Primary Implementation**. Minor local syntax/path fixes may be made only when bounded and fully evidenced; return nontrivial native/design or validation-contract findings to Primary without changing the old artifacts. Do not use Local work as independent R03 review.

## Approval boundary

Original independent R03 full-stage review stays **FAIL**; separate independent re-review is not yet run. Owner D1=A/D2=A remains approved for scope only, and no full R03/H2 gate has been passed. Retained R remains staged; S retains 90/90 Passed but no R03 acceptance, Q/P/O/N remain unchanged, four contaminated unisolated warm certificates remain Failed, and deferred R02 CPU/H1 RSS risk is unaccepted.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`, PureInterpreter expansion disabled. H2 is separately human-initiated and unavailable until findings close. No X02/M08A/release or performance SLA approval.

**Work stops after the single focused Local result; next state is Primary Implementation.**
