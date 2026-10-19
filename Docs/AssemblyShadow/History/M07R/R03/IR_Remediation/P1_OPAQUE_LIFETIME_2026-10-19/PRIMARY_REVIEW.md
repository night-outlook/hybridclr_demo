# Primary source review — opaque-inventory lifetime receipt parity

## Inputs independently inspected

- Local-owned 20261019-48ee PASS at demo 465c14e660b576836f544da2b410dcb8b9e6c05f / native 48ee6468065a6b559f53719dc310d901d8181ab8; later returned Local evidence commit 3853f965e3a9d191da470b515a45426802c9cc4a, without changing historical status. The four exact original source hashes and raw evidence remain Local-owned.
- Later native opaque source `5e2326a45bd6070aa25830ca8c0236e1915bde13`: `AssemblyShadowOpaqueExecutionInventory.h`, `AssemblyShadowOpaqueExecutionInventorySource.inl`, `run_opaque_execution_inventory.py`, fixture and CI; demo opaque source anchor 224f4db367c9bae557c32c2351b8dd36b64cb2fe; prior final docs-only handoff d4daea59682ffd14a8ff8b282c280733bcecb3d8.
- Current outer consumer before repair at demo d4daea: `read_component_result()` requires `commandLifetimeUnverified` only for `empty-live`; `execute_component()` catches completed parse failures as ordinary exceptions unless the component is `empty-live`. In contrast, native opaque runner explicitly writes the summary-level marker and its manifest unsealed state for unsafe command lifetime.

## Review conclusion

**Finding P1-OPAQUE-LIFETIME-01 (Primary source review, independently identified):** an absent/malformed opaque summary after a completed child can allow later independent subprocess activity although native compiler descendants are unverified. This is a fail-stop scheduling gap rather than a false overall PASS or a witnessed runtime survivor. No Local fault injection or historical reclassification has occurred.

**Correction:** demo source `d548799cc026b2ca78b40b7289fed404a3e8ec96` requires the typed marker on both native live components and stops after an invalid opaque receipt, preserving stream evidence and `NotRun` later scheduled cells. It adds five mock/controlled regression cases, increasing tested module count to 75 while retaining all earlier 70. Normal explicit false/nonzero does not trigger an unnecessary stop. No native runtime or SDK procedure is rewritten.

**Independent verifications:** the source-bound macOS/Linux [focused CI 39256679075](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679075), [integrated 75 CI 39256679128](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679128) and [managed/aggregate CI 39256679215](https://github.com/night-outlook/hybridclr_demo/actions/runs/39256679215) each PASSED all configured host jobs. Native opaque source [CI 39244090056](https://github.com/night-outlook/il2cpp_plus/actions/runs/39244090056) passed 3/3 Clang/GCC Mac/Linux jobs at source `5e2326a45bd6070aa25830ca8c0236e1915bde13`. These checks use host mocks, and **90 new official SDK syntax configurations remain NotRun** until Local's next exact one-shot cycle. Existing CI artifact receipts and source hashes are not Player/runtime acceptance.

**Opaque source limits reviewed:** it copies 2,048 native pointer values into fixed scratch under the existing short observation lock, validates counts and equality, then clears scratch before returning only numbers/booleans. It never dereferences/returns class addresses. O(n²) post-lock uniqueness testing, unchanged state ABA, pointer provenance/lifetime and real GC/RSS/Shutdown safety still require independent proof. A stable two-sample identity table is not a coherent VM epoch. The original allocating execution/general getters remain unchanged.

## Operational and publication evidence

The GitHub Connector write/read-back smoke for this task succeeded on disposable demo branch `codex/assembly-shadow-smoke-20261019-opaque-receipts` at commit d12c48bc1e4d8ff86f2c85b0de33dd02fd55406a. The connector currently offers no branch delete action; the disposable smoke branch remains isolated from the active feature branch. It is **not** source or acceptance evidence. No force push occurred.

A final Docs-only handoff commit must be created after source anchor `d548799cc026b2ca78b40b7289fed404a3e8ec96`, then read back along with the other three exact branch heads. The historical 20261019-48ee PASS and all prior FAIL/Blocked/NotRun statuses remain Local-owned and unchanged. Acceptance: P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, full P3 Incomplete, `R03Accepted=false`, `ReadyForHumanReviewGate=false`, PureInterpreter disabled.
