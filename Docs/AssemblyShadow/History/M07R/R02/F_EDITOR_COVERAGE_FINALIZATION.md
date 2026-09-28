# R02 batch-F finalization: require the complete Editor contract set

## Scope and authority

Continuation input: published batch-F repair `d43663e9ff96a9249d5e7bbf1e02bbd7e40f552b`, following Local return `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.

The resumed Primary audit authenticated the selected CI artifact at `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`: all 3,276 exported source files matched size, SHA-256 and Git blob, and the 203-test Python suite passed again on that export. These checks establish the recovered implementation identity, not new Unity execution.

One acceptance gap remained: the handoff required three new schema/serialization Editor tests and the two existing R02 probe tests, but `Batch.editor_tests` enforced only the original two. Missing or skipped new tests could therefore coexist with an accepted Editor cell.

## Correction

The runner requires a Passed NUnit test-run and exactly one Passed record for each of these five full names:

- `AssemblyShadowDemo.Tests.R02ProbeContractTests.FormulaMatchesIndependentLoop`
- `AssemblyShadowDemo.Tests.R02ProbeContractTests.JsonPreservesNestedRawDiagnosticsAndLargeIntegers`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.EveryR02LinkedFieldIsRequiredByActualRuntimeProof`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.MatchingButNarrowedInputsCannotRedefineTheR02WireSchema`
- `AssemblyShadowDemo.EditorTests.R02TypeResolutionSchemaTests.UnitySerializationDoesNotManufactureMissingOrZeroR02Coverage`

Absent, duplicate, renamed, foreign-namespace or non-Passed required cases fail the existing Editor cell. The successful `editor-tests.json` includes all five in `requiredCases` and binds the original XML. Unrelated skips remain individually reported rather than silently promoted to passes. Any Failed/Inconclusive test, or a failed overall run, still rejects the cell.

No test body, runtime source, managed parser, native writer, fixture, timeout, performance schedule or restoration policy changes. The batch remains 34 cells. The new source must nevertheless be frozen and paired with control because runner behavior is executable input; no source-policy allowlist is broadened.

## Regression coverage

Seven additional host tests execute the real `Batch.editor_tests` method with synthetic NUnit XML and mocked Unity command execution. They cover complete success/receipt fidelity, each missing case, each non-Passed required result, duplicate cases, foreign namespaces, failed run/unrelated failure, and truthful reporting of unrelated skips.

The resulting Python suite has 210 tests; its selected local run passed with no failures or skips. These seven tests are included in the existing macOS workflow through `test_f_batch_repairs`. They validate acceptance logic, not execution of the five real Editor tests. Actual Unity/dnlib/linker/serialization behavior remains required in the next Local batch.

The original batch-F integration review and evidence remain in `F_INTEGRATION_REPAIR.md`, `F_PRIMARY_VALIDATION.json` and Git history. The final metadata records the new source/control tuple and selected CI results. Prior Local F remains unsealed and unaccepted.

## Transport and boundary

Demo-only disposable Connector smoke branch `codex/connector-smoke-r02-f-coverage-8d72` passed write/read-back at `7664740f26680d9b89223962413cc93a2eab0aaa`, based on `d43663e9ff96a9249d5e7bbf1e02bbd7e40f552b`. It is not a handoff or acceptance commit and must not be merged. It remains because no branch-deletion action is exposed.

This finalization is a focused implementation self-review, not the independent R02 stage review. Keep both roles on managed package `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`, refresh only the demo source/control authority, and run the supplied batch once in a new root. Do not reuse an old graph as a new-source build. H1 remains PassedWithExplicitDeferredRisk; D1/D2 require measured disposition before H2; R02Accepted=false; mayEnterR03=false.
