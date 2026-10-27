# R03 IR original-S retained worktree sparse-projection capacity remediation — design (2026-10-26)

**Role:** Primary Implementation. **Scope:** bounded environment/layout remediation for IR-LOCAL-CURRENT-NATIVE-ORIGINAL-S-CAPACITY-01; no native source or product acceptance changes. The original independent R03 full-stage verdict from October 8 remains FAIL. Neither oneuse-A nor oneuse-B launched the combined coordinator. This design authorizes a narrowly scoped Git checkout-projection change, not arbitrary cleanup.

## 1. Authoritative Local findings

oneuse-A initial original-S worktree checkout consumed approximately 32 GiB of observed shared APFS capacity; immediately after creating the clean detached fc55 worktree, only 19.63 GiB remained, below the unchanged 20 GiB coordinator floor. The later 20.29 GiB observation was passive and never admission.

oneuse-B independently reauthenticated the retained fc55 worktree and the unchanged source/remote bindings, but available output capacity was 21,322,317,824 bytes (19.858 GiB) before readmission and 21,303,300,096 bytes (19.840 GiB) afterward, both below 21,474,836,480 bytes. The read-only admission exited2; no ten-stage coordinator invocation, Unity, build, Player, SDK compiler, original-S archive audit or 126 source/install pairs ran. Proposed /Volumes/Data is an APFS volume sharing container disk3 with /System/Volumes/Data and therefore did not provide additional independent capacity.

The previously absent dotnet CLI was resolved without installation: Local discovered a trusted Unity6000.5.3f1 embedded DotNetSdk at SDK8.0.318, Microsoft.NETCore.App8.0.21, osx-arm64 and enabled only its directory in a process-scoped PATH. Actual Unity product execution remains Unity2022.3.62f2. The shipped toolchain check itself was NotReached after capacity admission refused; Local independently recorded real CLI outputs. No new SDK installation or source modification is needed.

Retained historical original-S worktree: /Users/ah/GitHub/hybridclr/r03-local-validation/OriginalS-20261026-fc55-oneuse, clean/detached at fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b, registered to the canonical demo source repository. Do not recreate this worktree.

## 2. Exact Git evidence and choice

GitHub Connector independently inspected the tree of the actual original-S checkpoint:

- Git commit fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b.
- Required subtree Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready.
- Tree SHA 2acdcc0ec3c0f15dea11f99bc9c5d6d0f431de79.
- Exactly **16,978 regular Git blobs** (16,958 mode100644 and 20 mode100755).
- Aggregate committed logical file size **3,882,340,952 bytes (3.62 GiB)**.
- The existing original-S read-only audit_s_provenance.py and audit_s_process_joins.py consume this committed checkpoint subtree and external new audit output; they do not require a full historical non-checkpoint working-tree projection.

Therefore a narrowed sparse checkout of this *same retained* fc55 worktree may avoid keeping many unrelated historical tracked files materialized and recover substantial capacity. The observed old full checkout loss minus 3.62 GiB is a **hypothesis, not a free-space guarantee**: APFS cloning, snapshots, compression, purgeable records and current disk activity can change physical reclamation. Measure before and after; never infer acceptance from projected logical bytes.

**Selected:** retain the same worktree identity and Git object history but change only its materialized checkout projection through Git sparse-checkout cone mode to include the entire exact protected checkpoint subtree. This deliberately de-materializes otherwise-clean tracked files outside the protected subtree from that *auxiliary* fc55 worktree; the corresponding objects remain in Git and no historical committed bytes, source project commit or separate Local evidence directory is deleted or rewritten. The operation is not a claim that the physical full checkout remains unchanged. Reconstruction of the former full projection requires sufficient disk space and separate authorization.

## 3. Guarded Primary implementation

New Tools/AssemblyShadow/R03IR/original_s_sparse_projection.py supports:

1. Read-only --inspect: authenticate exact same retained canonical physical path; exact registered detached clean fc55, canonical origin, absence of submodule checkout and dirty/untracked files; four live repo HEAD/remote + ten candidate and 42 VM blobs; commit-anchored subtree tree SHA, exactly 16,978 regular blobs and aggregate 3,882,340,952 logical bytes. Report current free space and whether checkout is already sparse. Do not modify any source, root or metadata during inspection.
2. --apply: re-authenticate and SHA1 Git-blob-hash **all 16,978 materialized checkpoint files** against the exact pinned original Git tree before changing projection. Refuse aliases/symlinks/missing/size/byte mismatch, dirty/untracked files, submodules, wrong repo or SHA, already-sparse source, existing evidence root, altered current sources or wrong path.
3. Create one new external environment-remediation evidence root and write an INTENT.json receipt **before** the Git command. Invoke exactly one bounded Git sparse-checkout set --cone --no-sparse-index to include only the complete pinned checkpoint subtree. No automatic retries, cache cleanup, prune, worktree remove, reset or deletion of Git objects.
4. After execution, require original worktree still singly registered at fc55, clean, sparse path exactly the one checkpoint; confirm checkpoint Git tree unchanged and independently hash **all 16,978 physical protected files again**. Retain exact Git command/stdout/stderr/exit, before/after free bytes and outcome in RESULT.json. If command fails or times out, record failure and stop; do not repeat or auto-disable sparse mode.
5. A success means only PassedBoundedSourceProjection_RequiresFreshCapacityAdmission. It does not assert sustained future Unity build capacity, that a threshold is met, that historical S archive semantics passed or that any coordinator launched.

Original P1 and R03 production/interpreter/package/native implementations, original S archive, source-pins.json, all historic FAIL/Blocked/Passed states and previous oneuse-A/B checkpoints are unchanged.

## 4. Capacity and execution boundary

No arbitrary deletion, Time Machine snapshot thinning, macOS cache purge, Git gc/prune, repository cleanup, unrelated historical output relocation, fresh fc55 worktree, CLI installer or minimum-threshold change is authorized. Sparse projection is the sole authorized mutating environment remediation. If it fails, remains ambiguous, does not improve actual available bytes or damages protected checkout integrity, **stop with preserved evidence** and return to Primary. Do not retry the projection or run the coordinator.

After successful sparse projection, run the existing read-only current_native_environment_admission.py on the newly designated, never-used **oneuse-C** output root. Require the existing 20-GiB hard floor at its actual output parent and actual PATH-visible SDK8/runtime8, plus clean source/worktree/Unity checks. Because 3 full native Unity roles and 5 fresh Players may consume much more than 20 GiB, **40 GiB post-projection advisory headroom** is preferred; this is not a demonstrated lower bound nor a replacement for the 20-GiB hard stop. If only a small margin passes the minimum, Local must report capacity uncertainty, seek explicit Primary decision before expensive Player dispatch and not claim guaranteed success.

Only once source/capacity/toolchain conditions are independently satisfied may Local run the existing, unchanged combined 10-stage coordinator exactly once in the fresh oneuse-C root. Preflight itself is read-only and may be rerun solely after bounded environment repair, never to reuse oneuse-B. The coordinator still requires original S nine-part full byte/90-cell/59-process audit, current-native 3 builds, 5 real Players, 42×3 physical installed VM source identity and complete final receipts. A green coordinator's ceiling remains FocusedEvidenceReadyForIndependentReview, not R03 acceptance.

## 5. Host tests, failure and review gates

New explicit source-only original_s_sparse_contracts.py runs 31 tests against tiny isolated Git repos covering actual sparse behavior, identity preservation, checkpoint byte matching, alias/malformed/missing/dirty rejection, tracked-object retrieval after sparse de-materialization, one-use intent and no-retry command failures, hidden Git assume-unchanged/skip-worktree flags and actual linked-worktree isolation. It uses no original-S worktree and does not compile Unity. CI source-only has 31 new plus 149 retained tests per Mac/Linux host = 180 tests per host.

No new Local toolchain or product evidence has been run in the web environment. October 8 independent R03 FAIL with High IR-R03-01/02 remains; D1=A conservative NativeLayoutAdmissionV1/X02 deferral, D2=A observational-only performance and contaminated certificates, original S bounded 90/90, b7e3/c42a overall FAIL and f51d historical-only PASS are preserved. P1/P2/E0/E1/full P3 open; R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, runtimeAcceptance=false, PureInterpreter disabled. No H2, M08A, X02, protected SNAP-01 or Human Review Gate in this cycle.
