# LR-002 Primary review — Git diagnostics and recovery ownership

## Scope and reconciliation

This is the bounded Primary review of LR-002, source repair, host tests and handoff. It is not an independent full-stage design/plan/implementation/evidence review or a Human Review Gate approval.

Local publication `1fb504b2732c72dd1c403060396276af69d6251a` preserves R executed at `ba57a3391da9627e694ee33f8bfe3cb993e6c56a`. Original R remains ReturnRequired, 47 Passed / 1 Failed / 42 Blocked. Its six builds, 18/754 Editor cases and 23 focused Players are separate completed evidence; 755 resource cases and 36 other Players are NotRun. Storage and seal Passed. The restore command never launched because `ls-remote` failed first. Original stderr, numeric exit, complete argv and failing repository are Unavailable; no particular transport cause, remote change, runtime defect or storage exhaustion is inferred.

## Published delta

Source/CI commit: `9f27feb647bbf2d2bc82483700fe4f78e5ea60be`, branch `codex/assembly-shadow-r01b-h1`, parent the exact Local publication. Final transport is a Docs-only descendant supplied in Primary's final prompt and verified against remote HEAD.

Changes are limited to Git diagnostics and its two entry scopes, the cleanup/normal authority split, the P05 restore ordering/report, two diagnostic CLIs and a pinned retained-state manifest, three test files and the new source-bound LR CI workflow. `run_completion.py` and its90-cell dependencies are unchanged. There are no C#, native, package, IL2CPP, fixture, schema-bridge, source-pin, agent-profile, gate, build-profile, timeout, warm-up, lease or storage-threshold edits. The three other pins remain HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, IL2CPP+ `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

The twelve-file atomic Connector tree was constructed on the read-back base tree; uploaded Git blob IDs match tested local bytes. No uncommitted local checkout is handoff authority. One end-of-file newline difference in run_local.py is retained in the exact tested/published byte manifest and has no executable effect.

## Reviewed correctness boundaries

**Diagnostics:** the wrapper distinguishes process errors, preserves status/actual exit and bounded stream evidence, and never retries. Recording a successful remote subprocess is not approval of its response; the caller still requires the exact SHA/ref tuple. Evidence-write failure denies acceptance. Redaction is performed before clipping, with full original byte hashes/lengths and no raw stream or environment dump. Scoped context is restored on error and source-less host test fixtures retain their original scheduler behavior.

**Cleanup:** a fresh network check cannot run before the P05 restoration path. Local-only authentication retains the same roots, commits, branches, cleanliness, origins, catalog/blob, marker, pins and executable-input checks. State and backup ownership are checked before the unchanged production restore. The original C# guards still limit the allowed defines/settings mutation and verify quiescence; the Python exact-byte restorer still requires that producer receipt. No arbitrary backup copy or relaxed source mode was introduced.

**Acceptance:** normal authentication runs after exact restoration. An outage or wrong tip at that point preserves cleanup evidence but fails the original cell and blocks its dependents. The existing final authority and all other normal phase checks remain. No state means no mutation, not required P05 coverage. An exclusive recovery evidence directory prevents a second invocation; malformed local state, unsafe paths or failed producer writes remain explicit failures.

**Historical preservation:** the old staged R root is intentionally not recovered or reopened. Its six input witnesses and five missing outputs are audited read-only using committed hashes. The new isolated S project exercises recovery. A Passed retained-state audit explicitly says original cell Failed, settings remain staged and restoration was not performed. This avoids altering the sealed/live evidence to manufacture a historical success.

**Storage integration:** the existing essential-cleanup dispatch remains; metadata sampling, capacity formula/floors and in-flight command lifetime are unchanged. The wrapper binds the added helper/authority/recovery files into source authority. Pre-constructor errors include bounded requested-source diagnostics even before a sidecar exists.

## Executed host checks

Final Primary host selections Passed:45 new LR tests, 48 storage tests, 5 retained LP scheduler tests, 9 retained strict R02 schema tests, and 183 retained R03 core tests, with zero failures/errors/skips in those selections. The five scheduler cases are also part of the complete Completion suite; do not double-count them as unique coverage. Ten changed/new Python files parsed; all three handoff shell blocks passed bash -n. The retained checkpoint CLI passed its six-file read-only audit and explicitly left staged state unchanged.

At the exact source/CI commit, run **37653557539 Passed on Linux and macOS**. Each platform passed **405 Completion tests, 48 storage tests and 9 strict-schema tests:462 tests, zero failures/errors/skips**. Both artifact ZIP digests, all four indexed outputs and 427 source-file hashes per artifact were authenticated. The45 new tests and five retained scheduler tests are included in405, not additional counts. Full commands, output identities and source tuple are retained in the committed workflow and exact artifacts indexed in EVIDENCE.json. CI did not launch Unity or Players or inspect the user's Mac. Other automatically triggered broad workflows are not counted as full-run passes or runtime acceptance here.

The broader bounded-export attempt recorded394 passing methods, 3 errored methods and a setUpClass error preventing8 N-sidecar tests from running (397 methods executed, 4 errors total). Its missing inputs were a package source file, two workflow files and the retained N-sidecar corpus, not waived assertions. A prior incomplete timed-out export run and a schema test invocation with a missing import path were also not counted as passing. Complete-checkout CI is separate evidence for inputs absent from that export; all limitations remain in EVIDENCE.json.

## Capture and transport proof

Read-only capture run 37648395523 checked out exact Local publication 1fb504b2, not the workflow's smoke commit. Artifact 11496041439 has ZIP SHA-256 `0a9af29782e2122788d16e13dc755382604c5d9a8f5873c329a286ae944f5a0c`; 3957 indexed source/evidence files were checked by size, SHA-256 and Git blob. The export is bounded and not a full fresh historical custody audit or a real Mac checkout.

The prior four-repository initial Connector smoke remains retained. This cycle additionally proved the exact demo Git-data tree/commit/expected-head-ref path on disposable `codex/connector-smoke-lr-1fb504b2`, base 1fb504b2, final read-back smoke commit `ada350bc2da723aab71a5b9858a786f1a99c370c`. That branch also carries the immutable capture workflow; it is never a product source or merge target. Branch deletion is unavailable; the retained branch is recorded explicitly. The three unchanged repositories were re-read, not falsely represented as receiving fresh writes.

## Limits, remaining validation and rollback

The original transport cause is still Unavailable. No Unity/Player ran in Primary; no actual Local network or current disk capacity has been proved. Tests isolate external commands while exercising actual Python authority/byte-restoration/scheduler code; they do not establish fresh Unity semantics. Existing byte-copy and subprocess-lifetime behavior is preserved rather than claimed to be newly crash-atomic or process-group hardened. An OS failure, source change, unsafe transaction, concurrent edit or unwritable evidence can still prevent cleanup and must remain visible. Redacted excerpts cannot recover every raw detail and are not universal secret detection.

Retained R stays quarantined and staged by design. S requires read-only retained-state audit, point-in-time exact transport readiness, fresh capacity admission, then one complete90-cell batch. No source/protocol/credential repair, threshold reduction, old-root reopening or phase retry is delegated. Any new failure returns to Primary with separate cleanup/authority states and available evidence. A fully green S only becomes EvidenceReadyForPrimaryReview; its full-stage independent review and human approval remain pending.

Rollback is a new reviewed forward commit and updated assignment, never a reset or historical result rewrite. R03Accepted=false; H2Passed=false; qualificationApproved=false; ReadyForHumanReviewGate=false; PureInterpreter expansion disabled. Contaminated unisolated warm certificates remain Failed; R02 CPU/H1 RSS, ancillary effective-model identity and production-performance decisions remain unresolved where previously recorded.
