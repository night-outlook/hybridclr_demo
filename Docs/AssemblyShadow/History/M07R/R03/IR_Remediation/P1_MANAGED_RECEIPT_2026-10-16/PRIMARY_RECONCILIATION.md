# P1 managed receipt consumer — Primary reconciliation and correction

## Disposition and authority

**IR-LOCAL-P1-MANAGED-RECEIPT-01: corrected in source; host regression Passed; fresh Local successor NotRun.** The consumed `20261016-0a0b` aggregate remains **FAIL / FailedOrIncomplete, 9 Passed / 1 Failed**. No historical result, Local-owned report, source-pins.json, native code or compiler procedure has been rewritten.

Returned publication: `hybridclr_demo@1abf5df96c61e8f5bd870d6b03a93e33f44182f5`. Correction/source-test/CI commit: **`06209426b765a805da2cc2f810ba5da390787099`**, branch `codex/assembly-shadow-r01b-h1`. Later documentation-only commits are transport publications, not additional compiler execution. Native source remains `il2cpp_plus@0a0b70156e75d450d75d0bcfd9132843b8abbbb0`; HybridCLR and package remain `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` and `948c0e3b4f8891481301770115e8ba4945eea6de`.

Read the unchanged [Local report](../../../../../Handoff/LOCAL_VALIDATION.md), [return](../../../../../Handoff/RETURN_TO_WEB.md), and [original checkpoint](../../local-validation-p1-metadata-source-20261016-0a0b/README.md). The checkpoint link is relative to R03 through IR_Remediation; the canonical checkpoint is `Docs/AssemblyShadow/History/M07R/R03/local-validation-p1-metadata-source-20261016-0a0b/`.

## Confirmed defect

Primary's wrapper requested `managed-sdk/results.json`, but the unchanged managed producer creates `managed-sdk/build-api/results.json` and prints a JSON binding with that absolute path and SHA-256. Primary read the actual returned stdout, Failed outer command, producer source, managed receipt excerpt and Local evidence audit. The child exited 0; the receipt lookup, not compilation, made the outer cell fail.

The original aggregate SHA-256 remains `13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565`. The actual managed receipt is `43f38be35063559bcb156c31968f6b80d8707982692aef55fd6ab05285ea916e`. Local independently verified five managed products, one expected-negative control, and all **70 native syntax configurations**. Its reported 68 managed and 742 native warning occurrences remain unsuppressed. Primary did not repeat Local's complete external SDK/raw inventory audit or execute Unity.

## Implemented contract

Only three source/CI paths changed:

- `Tools/AssemblyShadow/R03IR/run_p1_metadata_local_preflight.py`: new `read_managed_result`, connected to the actual `managed-sdk` cell. It accepts only the exact nested path returned by `build_api.py`, validates the returned SHA-256 against the same bytes it parses, requires the managed receipt kind/schema/Unity version and non-runtime scope, then returns the actual inner verdict. Outer success still requires child exit 0 **and** inner Passed. It records `innerResultPath`, `innerResultSha256`, and `returnedBindingVerified`.
- `Tools/AssemblyShadow/R03IR/test_p1_managed_receipt.py`: 13 regression methods, including full ten-component orchestration under explicit Git/SDK/child-process mocks. The managed root assignment, initial record, final write and returned binding execute from the **actual producer AST**, not a separately invented path convention. This does not execute the full compiler function.
- `.github/workflows/r03-p1-metadata-preflight-contract.yml`: runs the five existing CLI tests and thirteen new tests on macOS/Linux, retaining command streams, source hashes, results and manifests.

Missing files, wrong/relative/out-of-component paths, obsolete root-level decoys, changed bytes, malformed/duplicate-key/non-finite JSON, wrong kind/schema/scope, file/parent symlinks, nonregular files, Failed inner results and nonzero child exits fail closed. There is no search-for-Passed fallback, synthesized root receipt, warning suppression, partial success or historical promotion. The diagnostic command directory is now created before child execution so a launch exception can retain its Failed command record and the independent native component can still run.

This reader assumes the existing one-owner, completed-child, canonical external output contract. It is not a new adversarial filesystem transaction protocol, an SDK provenance reimplementation, or a substitute for the producer's five-product/expected-negative checks and Local's independent evidence joins. The native V2 transaction, native SDK matrix and original semantic predicates are untouched.

## Fresh verification

Primary first reproduced the defect with the new aggregate success test against the exact original wrapper blob `67447d2476f247e9912eeb6a7f4c090fabb83273`: it failed as expected. The corrected wrapper passed all thirteen methods in this environment. The test source, corrected runner and unchanged producer bytes were matched to their Git blobs.

[CI run 38859685370](https://github.com/night-outlook/hybridclr_demo/actions/runs/38859685370) then passed **2/2 jobs, 18 methods per operating system**: the original five plus the new thirteen. Both original artifact ZIP hashes and all **10 manifest-declared files** were independently checked after downloading through the Connector. These are host/mock tests, not new SDK or Player evidence.

[Machine evidence and exact commands](EVIDENCE.json) and [retained raw test stderr](HOST_TEST_LOGS.txt) preserve the original-source failing regression, corrected-source results, CI streams and scope. CI artifacts also contain full RESULT/MANIFEST files; their original artifact identifiers and hashes are recorded in EVIDENCE.json.

## Next Local cycle and remaining work

The old batch and SDK scratch roots are consumed. Only the separately published [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) authorizes one new source/SDK successor with unused roots. Its ten components and 14-unit/five-profile native syntax matrix are unchanged. Local must verify the returned managed path/hash/verdict and raw compiler receipts, preserve all source/SDK/prior evidence, then stop and return factual results. No nontrivial correction belongs to Local.

**P1 remains Incomplete:** coherent bounded live general/execution VM capture, allocation/RSS/GC limits, original getter integration and shutdown/lock safety remain Primary-owned. P2 native/C# V2 semantic integration remains NotIntegrated; E0/E1 engine-owner lifecycle remains unresolved. A passing syntax matrix does not prove linking, metadata teardown, scheduler ownership or Player behavior.

Historical SNAP-01/N/M/K/I/E failures, strict S custody Blocked and independent R03 review FAIL/re-review NotRun are unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No Human Review Gate or H2/X02/M08A advancement.
