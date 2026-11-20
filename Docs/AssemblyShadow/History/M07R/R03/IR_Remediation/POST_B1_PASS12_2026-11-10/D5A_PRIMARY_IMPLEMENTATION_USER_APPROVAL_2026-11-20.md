# R03 B2 D5-A — explicit user approval of Primary-only implementation

**Decision:** `D5A=ApprovedByUser`. **Scope:** new versioned D5-A source-only candidate/admission tooling, negative mutation tests, fault-producer inventory/contract, source and build-roster assertions, CI, and versioned Local procedure draft, on `codex/assembly-shadow-r01b-h1`. The user explicitly requested: **“approve D5-A Primary Implementation”**. Do not reinterpret this as approval of any Local Unity/IL2CPP/Player execution, D5-B, real hardware/SDK tests, D6 or the Human Review Gate.

**Source authority at approval bootstrap:** `hybridclr_demo@a728c869481dd82f12526545749ecda4cfceaf3a`, `hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `il2cpp_plus@3e3d2ab9c0f7cd68f0a98c6f6677a4ab0e64a699`, all on branch `codex/assembly-shadow-r01b-h1`.

Predecessor gate: [independent D4 `PassD4ForNextGate`](D4_ACTIVE_SNAPSHOT_OWNERSHIP_INDEPENDENT_REVIEW_2026-11-20.md), source-host scope only. D5 requirements: [design](D5_LOCAL_VALIDATION_PREAPPROVAL_DESIGN_2026-11-20.md), [42-cell matrix](D5_LOCAL_VALIDATION_MATRIX_2026-11-20.md), [approval decisions](D5_LOCAL_VALIDATION_APPROVAL_REQUEST_2026-11-20.md).

## Operational GitHub Connector smoke test

Only the affected `hybridclr_demo` repository requires writable D5-A commits. A disposable branch `codex/smoke-d5a-20261120-gpt6-a01` was created from `a728c869481dd82f12526545749ecda4cfceaf3a`. The harmless text file `Docs/AssemblyShadow/.connector-smoke/D5A_WRITE_READBACK_2026-11-20.txt` was committed as `b27b03e9a2f339f90a300cc1fcae5c7249a88b3a`. The branch remote HEAD and file content were independently fetched and matched exactly. The current connector has no branch-delete action; **the disposable branch remains**, explicitly outside the feature branch. It is not a product/source pin, Local handoff or validation result.

## Boundaries and stopping point

- **Approved**: source-only Primary preparation and automated source-host CI on GitHub; docs and independent-review request.
- **Not approved**: `D5B=NotAuthorized`, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, no local dry-run admission that would start real tools, no Unity/IL2CPP build, Player, D5-A self-review pass, D6, H2/M08A/X02/SNAP-01 or Human Review Gate.
- Historical B1 `current_native_source_gate.py`, `current_native_candidate.json`, 14-file/46-VM-count tests, oneuse-12 runner and saved results remain immutable.
- When D5-A implementation and CI are complete, stop for an **independent D5-A review**. Only afterward can a **separate user D5-B Local execution decision** authorize a new exact-source handoff.

**Status at authorization:** `D5A=ApprovedByUser_InProgress`, `D5B=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`.
