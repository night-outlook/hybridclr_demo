# R03 LP repairs — Primary Implementation review

## Scope and verdict

The two batch-P orchestration/consumer defects have source repairs. This is the bounded Primary review of those repairs, their tests and their evidence boundaries, not an independent full-stage R03 review or Human Review Gate approval. The published handoff assigns one new complete batch Q; only fresh Local evidence can establish its runtime result.

Authoritative input: Local publication `d9ef449e8e8aef885539e4b981243a868f8d0ba6`, executed demo `d8884646659f7b6ae0f6ceda746fd271c96c8d61`. P remains ReturnRequired, 90 cells = 71 Passed / 18 Failed / 1 Blocked. Its six builds, 18+754+755 Editor cases and seal Passed. All 59 Players executed with 42 passing and 17 failing verifications. Passing live-policy and restored-baseline subproofs do not promote the failed integration cell.

## Source authority and ownership

All branches: `codex/assembly-shadow-r01b-h1`. Product repair commit: `b42cbe1134a56e675b8a98e275a45ae5a012e17d`. Complete CI/source anchor: `0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5`. The two commits after the product repair change only the standalone CI workspace and canonical temporary path. Final handoff transport is a Docs-only descendant recorded in the final prompt and verified against remote HEAD.

The other three source pins are unchanged: HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; package `948c0e3b4f8891481301770115e8ba4945eea6de`; IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. Both R03 pin manifests agree. No C#, native, package, IL2CPP, build profile, Player fixture, Editor catalog or acceptance flag changed. Local checkouts remain the four exact `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>` paths in WEB_TO_LOCAL.md. Primary used Connector-fetched source artifacts, not those Mac checkouts.

Production Python changes are confined to `Tools/AssemblyShadow/R03Completion/run_completion.py` and `legacy_runtime.py`. The additional files are `test_lp_orchestration.py`, `test_lp_runtime.py`, `test_lp_replay.py`, `lp_replay.py`, `lp-inputs.json`, and the read-only CI workflows `r03-lp-inputs.yml` / `r03-lp-contracts.yml` under `.github/workflows`.

## LP-001: authenticated context before integration

### Diagnosis

The actual Completion constructor does not create `resource_context`; successful resource graph binding does. The old execute order called integration first. The C# producer had already emitted valid live-domain and restored-baseline proofs, but the Python consumer then accessed a field not yet initialized. A passing producer cannot justify a passing orchestration cell.

### Design and implementation

Move the existing `resource-input-binding` cell before `production-entry-integration` in both the plan and execution, and make it integration's explicit prerequisite. Retain the real graph factory and layout checks. Do not synthesize an early context, copy an unverified baseline hash from an arbitrary receipt, or duplicate the graph inside integration.

The graph factory can assign a context before its later layout check fails. Therefore scheduling tests require a Passed binding cell, not merely an existing object. Both graph failure and post-assignment layout failure block integration. P05 cleanup retains its independent path. An integration failure does not suppress unrelated Player cells that have their own passing prerequisites. All 90 IDs, six build roles, 59 Player selections and Editor rosters remain unchanged; only the two cell positions and dependency are corrected.

Review of `layout_evidence.verify_graph` and the resource graph confirms they consume the P05-finalized fixture/snapshot inputs, not the later integration output. The unchanged C# integration producer writes its own fresh output tree. There is no introduced dependency cycle. The existing policy-domain consumer continues to compare the live report with the authenticated ON snapshot.

### Coverage

Five tests instantiate the real Completion constructor and use the real cell scheduler and execute method, isolating only external expensive actions. No test pre-populates context. Tests cover success order, graph failure, partial context after layout failure, independent Players after integration failure and P05 cleanup/finalize failure. The original source fails three of these controls; the repaired source passes all five.

## LP-002: strict existing current-R02 bridge at every M07 boundary

### Diagnosis

Current native type-info includes the known `r02` object. The original legacy checker intentionally admits only its legacy fields. Completion invoked that checker directly without the already-implemented R02 bridge. Earlier codec errors masked this next boundary. Local reproduced the same unknown-field failure in 13 ON resource and four positive-startup witnesses.

### Design and implementation

Reuse `R02/type_resolution_schema.current_m07_schema` around (1) per-resource `m07.verify_case`, (2) aggregate `m07.verify_suite`, and (3) positive-startup `m07.verify_case`. Do not relax the legacy field set, delete fields from evidence, or create a second permissive verifier. The bridge and default legacy checkers are unchanged.

The bridge validates the exact 33-field extension, typed unsigned 64-bit values, schema/profile and coverage contract, then creates an in-memory projection for unchanged legacy semantic validation. Callback restoration is guaranteed by its existing context manager. Completion executes these scopes synchronously and sequentially; parallel Python verifier execution would require a separate design, not reuse of the global callback scope concurrently.

The explicit codec source context still passes through each entry point. Successful receipts record the bridge's actual count and raw-evidence-unchanged flag. ON/positive/aggregate checks cannot pass with zero verified type-info objects. OFF retains the original disabled contract and zero bridged objects. Negative startup never enters business resource verification and records a null bridge. Resource, business, early receipt, log, PID and inventory checks remain in place outside the bridge.

### Coverage

Thirteen entry-point tests run the real bridge/parser/original type checker with isolated launch/fixture/outer dispatch. They cover all three entries, four positive and six negative startup variants, OFF, success and exception restoration, unchanged raw objects/files and mandatory nonzero consumption. Negative controls cover each extension field missing, duplicate object/member keys, unknown fields, mistyped fields, every UInt64 counter with negative/overflow/coercion inputs, UINT64_MAX preservation, profile/coverage/version errors and existing legacy semantics. Nine unchanged R02 StrictSchema tests were separately executed and Passed.

## Evidence and limits

At complete source/CI anchor `0a0974c95ad4eab2cfdaf9b9ff7e0609be67abf5`, run **37518987943 Passed on Linux and macOS**. Each platform executed all **360 Completion tests with zero failures, errors or skips**, including the eight retained N-sidecar tests absent from the local export, and separately passed the bounded P replay (18 witnesses / 289 type-info objects). Both ZIP digests, all three indexed output files and 417 source hashes per artifact were authenticated. Exact artifact IDs, hashes and intermediate limitations are in EVIDENCE.json. These results establish the Python repair contracts, not new Unity/Player acceptance.

The new LP unit/replay selection has 21 Passed tests, zero failures/errors/skips, on the exact product bytes published. All 47 Completion Python modules parsed successfully. The handoff shell block passed `bash -n` after correction of its explanatory parameter-error text. This is syntax validation, not execution against the user's Mac checkouts.

A broader source-slice attempt had 352 executed passes and one setUpClass error: eight retained N-sidecar cases could not run because that bounded export lacked `CURRENT_SIDECAR_AUDIT.json` and its inputs. It is retained as an incomplete/failed-setup run, never full-suite success. The complete-checkout CI independently supplies those inputs. Initial standalone CI omitted the sibling package needed by existing source-contract tests; `f58ef378...` adds its exact pinned checkout and records its SHA/cleanliness. No test or coverage was removed to fix CI. The macOS run at `f58ef378...` then executed 360 tests with 356 passes and four errors caused by its symlinked `/var` temp parent. `0a0974c9...` selects and records the canonical existing temporary directory before creating test inputs; path-rejection guards remain unchanged. A controlled same-source reproduction failed the same four tests through an alias and passed all four through the real path. CI outcomes and authenticated artifacts are recorded in EVIDENCE.json.

The immutable P capture originated at `d9ef449e...` through run 37514312847, artifact 11436133078. The downloaded ZIP SHA-256 is `2bb7c167b25fc231a8d6b7b601f477c81454e292e3e6a81ee061279710fe3726`; 2,819 indexed files were authenticated by size/SHA-256/Git blob. Four large historical aggregates were explicitly omitted from this bounded export; no complete-custody re-audit is claimed.

`lp-inputs.json` independently binds 40 preserved P files: 18 raw observations and their exact original command receipts, fixture/resource receipts and original failure record. Read-only replay reproduces all 17 original schema errors and then passes the complete original resource-observation branch under the strict bridge; the OFF witness passes unchanged. It validates 289 ON type-info objects. The single permitted historical I/O relocation maps the original resource receipt path to a SHA-identical preserved copy and rejects all other reads. Original raw strings/dictionaries/files and hashes remain unchanged. This does **not** re-execute a Player, certify the entire M07/build/codec chain, or reclassify P; it is bounded consumer regression evidence.

P's original C#/Editor/native proofs are retained empirical evidence for unchanged source, not fresh Q results. Any automatically triggered broad API/host run is recorded separately from the focused Python repair evidence; pending or failed workflows are never silently counted Passed.

## Connector and publication controls

All four feature heads and identities were read through the Connector. The previously published four-repository smoke remains the retained initial transport proof. This cycle additionally tested the same Git-data tree/commit/ref path used for product publication on demo-only disposable branch `codex/connector-smoke-20261006-lp-a21f`, base `d9ef449e8e8aef885539e4b981243a868f8d0ba6`, created/read-back commit `64d2860e84e3827476f6b1ac1084b7d9f91c1708`. It Passed. The three unchanged repositories need no product writes in this cycle; their read access/pins were reverified, not represented as fresh write tests.

The Connector exposes no branch-delete operation. The new demo smoke and prior four-repository smoke branches remain explicitly disposable; never merge or execute from them. Product refs use fast-forward writes with expected-HEAD checks. Historical P/O/N files and Local-owned handoff reports are outside this change set. Final publication must read back all four feature heads and the Docs-only delta.

## Next validation and rollback boundary

The next assignment is exactly one unused source-bound batch Q in WEB_TO_LOCAL.md. Required order is authenticated graph/layout binding → integration, with unchanged independent Player prerequisites. Collect all prior evidence plus actual bridge receipts for each relevant case and the aggregate. Retain the 90-cell matrix, six fresh builds, 59 Players, 18-method preflight and 754/755 Editor rosters, including zero skips/inconclusive. All cells and seal must Pass before evidence is ready for Primary review.

No non-trivial Local source fix, guard/schema relaxation, pin substitution, historical result rebinding or phase retry is allowed. A new issue returns to Primary with the failed cell/traceback and independent subproofs. Rollback, if required, is a new Primary-owned forward commit reverting the two orchestration/consumer changes and updating its validation assignment; do not reset branches, remove evidence or silently reuse a batch root.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`; PureInterpreter expansion remains disabled. Independent full-stage design → plan → implementation → evidence review and human approval remain separate, pending stages. R02 CPU, H1 RSS and failed unisolated warm-certificate risks remain visible.
