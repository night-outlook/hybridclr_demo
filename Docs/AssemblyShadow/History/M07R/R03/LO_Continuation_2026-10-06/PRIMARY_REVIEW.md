# R03 LO continuation — Primary Implementation review

## Result

**Primary source repair complete; ready for one fresh Local Validation batch once this final documentation transport is published.** This is a bounded Primary review of the four batch-O returns and the additional live policy-domain guard. It is not the independent full-stage R03 review and does not approve H2 or PureInterpreter expansion.

Batch O remains authoritative: demo `7025f1026fd61f101a81fbafafb999095aa8604e`, 90 cells = 58 Passed / 30 Failed / 2 Blocked; six builds Passed; 18-method preflight and full 754/755 Editor rosters Passed; all 59 Players ran with 30 passing and 29 failing verifications; seal/final custody Passed.

## Source authority

All repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Published source pin |
| --- | --- |
| `night-outlook/hybridclr_demo` | `9c4b76a540e74c045cabaf9e700051512a75cead` executable source; `8db761455dfd73ef01eac7d48eb39c69ca253cf8` CI-only timeout commit; final Docs transport supplied by Primary prompt |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

The demo source sequence is `7025f102…` (Local O publication) → `ed615c913…` (LO-001–004 source repairs) → `7b148aa8…` (reported source graph versus emitted `AssemblyRef` correction) → `9c4b76a5…` (fresh integrated policy-domain guard) → `8db76145…` (CI-only timeout increase; no Unity/Player implementation change). `9c4b76a…` changes exactly four files from `7b148aa…`: `R03CompletionBuild.cs`, `resource_pipeline.py`, new `policy_domains.py`, and new `test_lo_policy_domains.py`.

## Repair review

### R03-LO-001 — compiler-policy domain reuse

The original failure reused the Player-derived filtered policy when returning to baseline source compilation. The published repair keeps the source/compiler policy immutable and derives a separate linked-Player policy. Restored `AssemblySnapshot.CompileWithOptions` receives the source policy.

`7b148aa…` corrected the regression model itself: the O diagnostic reported three source-graph edges that cannot be inferred from already-emitted DLL `AssemblyRef` metadata. The probe now authenticates those reported edges separately from physical compiler-DLL metadata and retains all negative controls.

`9c4b76a…` closes the remaining evidence gap inside the actual production-entry integration path. Immediately before restored-baseline compilation it:

1. executes `ValidateBeforeCompile` on the source policy against the live Unity project inventory;
2. separately executes it on the linked-Player policy as a negative control;
3. requires the source policy to pass;
4. requires the linked policy to fail with all three original `RuntimeReferencesFilteredAssembly` diagnostics;
5. proves neither policy object changed during validation;
6. writes and hashes the source/linked policy bytes and diagnostic report; and
7. binds that report into `integration.json` before the restored compile and zero-root/zero-closure comparison.

No guard is waived and emitted DLL references are not promoted into source-graph authority.

### R03-LO-002 — codec context loss

The published `ed615c…` repair forwards the authenticated native-codec source context through the shared diagnostic bridge. Relative codec pins still require explicit owner/project context. The next Local batch must re-run all 13 ON resource cases and four positive startup cases; host replays are not runtime acceptance.

### R03-LO-003 — case-sensitive linked-DLL lookup

The repair canonicalizes only the simple assembly-name lookup/comparison boundary. Original linked load order, full identity, duplicate/order checks, physical DLL bytes, hash/MVID and symbol evidence remain independent. The next Local batch must re-run all ON/OFF NoPatch measurement cells.

### R03-LO-004 — methods-list/image-record mismatch

The repair passes the complete image record, including methods and PDB availability, to the M06 measurement consumer. It does not synthesize a list-only substitute. The next Local batch must re-run all P01/P03 measurement cells and aggregate checks.

## Tests and diagnostics

Pre-publication exact-patch validation executed against authenticated source/O inputs:

- selected Python contracts: **102 Passed**, zero failures/errors/skips;
- Completion Python AST parse: **43 Passed**;
- a broader attempt retained 102 executed passes but one 8-test class was `NotRun` because the bounded source export did not contain N's `CURRENT_SIDECAR_AUDIT.json`; no skip/pass was fabricated;
- four downloaded CI/source/O archives and all provenance-indexed files were reauthenticated before publication.

Published `7b148aa…` source-matched workflows Passed:

- R03 remaining completion contracts: run `37457959880` — Passed on Linux/macOS;
- R03 resource-complete pinned API compilation: run `37457959968` — Passed, including the corrected 10-case policy-domain probe.

Published `9c4b76a…` source-matched CI:

- R03 remaining completion contracts at `9c4b76a…`: run `37470194294` — Passed on Linux/macOS.
- R02 Primary native/tooling validation at `9c4b76a…`: run `37470194292` — Passed.
- R03 pinned API attempt 1 at `9c4b76a…`: run `37470194390` — steps 6–12 Passed, including full resource compilation, fixed-image guards, raw/bootstrap guards, the 10-case policy-domain probe and layout forwarding; the job exhausted its 60-minute budget during unchanged N reference replay, so this attempt is **Cancelled**, not Passed.
- The same pinned API workflow previously Passed completely at `7b148aa…` in run `37457959968`, including the unchanged N reference replay. This is retained as reused-audited evidence, not promoted to source-matched acceptance.
- `8db76145…` changes only `timeout-minutes: 60` to `120` for the pinned API job and triggers a new source-equivalent API run. Final status: run `37484139882` was started from the CI-only timeout commit and was still InProgress at publication. It is not counted as acceptance; Local batch P remains the required fresh integrated validation.

The pinned API workflow compiles the full original resource project and dependencies against the extracted official Unity 2022.3.62f2 API/compiler profile; the host workflow runs package qualification and LO adapter regressions. These remain source/compiler evidence, not fresh Editor/Player acceptance.

## Connector transport verification

The mandatory GitHub Connector write/readback smoke test Passed for all four repositories using disposable branch `codex/connector-smoke-20261006-primary-r03`:

| Repository | Base | Smoke commit | Readback |
| --- | --- | --- | --- |
| `night-outlook/hybridclr_demo` | `7b148aa8cace4af4cb1d7a4219c4f79fe0182394` | `da729875baff41efbdfc64ecae946a41e0887e14` | Passed |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | `e0fd9b69f2b61f9716520232a45cfc733728c174` | Passed |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `22160fa6d0e461bb4c6b8e12e913e517e3ada089` | Passed |
| `night-outlook/il2cpp_plus` | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` | `8df927c8ba5ff4835be895dfa604cb202701dab0` | Passed |

The exposed Connector has no branch-delete operation. Cleanup therefore remains unavailable and the smoke branches are explicitly recorded as disposable non-product state. They must not be merged or used as handoff authority.

## Remaining Local Validation

Run exactly one fresh batch P from the final handoff transport. Retain the complete 90-cell scope, six builds, 59 Players, early 18-method preflight, and both 754/755 Editor rosters. In addition to all existing receipts, authenticate the new `compiler-policy-domains.json`, its policy-byte bindings, the live source-policy pass, the three linked-policy rejection guards, P01–P05 integration, restored-baseline compilation, and zero changed roots/closure.

All four original LO issues are to be verified in this single batch. Local must not perform a non-trivial source fix or retry a failed phase. Any new non-trivial failure returns to Primary.

A fully green batch is only `EvidenceReadyForPrimaryReview`. It still leaves `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, and PureInterpreter expansion disabled pending Primary reconciliation and the required independent full-stage design → plan → implementation → evidence review.
