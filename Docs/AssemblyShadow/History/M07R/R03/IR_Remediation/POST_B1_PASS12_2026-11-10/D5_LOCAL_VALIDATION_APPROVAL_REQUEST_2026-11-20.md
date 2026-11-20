# R03 B2 D5 — Approval request and stop point

**Decision status: `PendingUserApproval`.** Date: 2026-11-20 UTC. This is an approval request from Primary Implementation, **not** permission granted by this document or by an AI reviewer. No D5 local run/handoff, Unity/IL2CPP build, Player, H2, R03 release or Human Review Gate is authorized.

## 1. Decision basis

1. [Independent D4 review](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md) = `PassD4ForNextGate`, **source-host scope only**. The actual Unity/IL2CPP Player, whole VM/GC/shutdown, 32-bit atomic ABI, V1/B1/R02/V2 recovery, and P5/P6 cross-thread method execution were not run.
2. [D5 preapproval design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md) proposes a **new immutable source-admission profile** rather than reusing the B1 candidate.
3. [D5 validation matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md) specifies preflight, real native build/link, fault/phase/terminal/GC tests, ABI, compatibility and evidence custody. Some fault-injection producers have **not** been implemented or demonstrated on a real Player.
4. Verified legacy runner **is not compatible with D4 native/HybridCLR pins**: `current_native_source_gate.CURRENT` still identifies B1 source `il2cpp_plus@8aa8d093...` and `hybridclr@4b2774b0...`; old composed admission demands 14 source files and 46 VM files. It must remain immutable as a historical comparator, not be patched to accept D4.

## 2. Requested decisions (do not infer permission)

| Decision | Recommended choice | Effect if explicitly approved |
| --- | --- | --- |
| **D5-A: Primary preparation** | **Approve** | Authorizes Primary to implement and test **source-only** D5 candidate manifest/admission/fixture/CI tooling and to prepare a fresh four-repo `WEB_TO_LOCAL` draft. Does **not** authorize Local execution or Player builds |
| **D5-B: Local Validation execution** | **Defer until D5-A passes new independent/source provenance review** | After future exact handoff approval, authorizes **one** new source-pinned macOS arm64 Unity 2022.3.62f2 IL2CPP feature-ON/Release + feature-OFF control Local batch with fresh separate Player processes and a sealed one-use output |
| **D5-C: Additional platform/ABI coverage** | **Defer / separate decision** | Specifies Windows, Android armv7/arm64, iOS and any 32-bit ABI targets only when tooling/devices are known; unavailable coverage stays `NotRun`, never waived silently |

**Requested immediate choice: `Approve D5-A only`**. This follows the role boundary (Primary builds source/test infrastructure; Local runs real Unity/IL2CPP only after separately authorized handoff) and prevents code/provenance mismatch.

## 3. Exact tuple for preparing D5-A (not a Local handoff)

All repos: `codex/assembly-shadow-r01b-h1`.

| Repo | Source SHA in independent D4 review |
| --- | --- |
| `night-outlook/hybridclr_demo` | D4 CI-tested `c3307abacaaaec9db2a0f866b726e2ae5df1108b`; current D5 proposal branch HEAD must be freshly read at each new task and fixed to latest pushed commit before any formal Local handoff |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699` |

The branch HEAD recorded in any proposal or history file is informational at the time of writing; **the final Local handoff must use the newly verified, latest pushed 40-character commit for each repository and must pass a write/readback smoke test**. Do not supply a handoff prompt while D5-B remains unapproved.

## 4. Approval entry and expected work products

**D5-A acceptance:** Primary publishes a new D5 source pin manifest, source-only admission script/negative tests, exact native roster/installed-source checks, source-host fault-producer provenance, and a full-fidelity staged Local procedure. New tests must reject old candidate pins, wrong source inventory, old B1 output roots, missing real C++ source, unlinked test probe and wrong platform/Unity. Each new preflight/fixture output must explicitly state `UnityOrPlayerExecuted=false`. Commit and push to the exact D5 branch and independently audit source/CI. Keep `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION` until the user separately approves D5-B.

**D5-B authorization entry:** D5-A source/CI passes and is independently reviewed, exact `WEB_TO_LOCAL` includes all four latest commits and roots, official Unity/IL2CPP build toolchain/environment is confirmed, new one-use output root is absent, scope/budget are explicit, and the user grants a **separate** Local Validation approval. Any `Blocked`, `NoCoverage` or missing probe from new D5 source-admission must be resolved/declared before running a native Player.

## 5. Explicit status

`D4IndependentReview=PassD4ForNextGate`; `D5Proposal=CompletePendingUserDecision`; `D5A=NotAuthorized`; `D5B=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. No user decision has been made in this approval document.
