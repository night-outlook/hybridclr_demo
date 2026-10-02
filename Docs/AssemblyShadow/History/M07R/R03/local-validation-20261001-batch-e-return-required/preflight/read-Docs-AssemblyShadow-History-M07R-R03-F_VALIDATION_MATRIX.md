# R03 F — explicit native provenance and isolated Editor validation

This matrix governs the next focused batch E. It supplements, but does not reduce, the full R03 exit conditions. Historical A–D results are immutable. H2 remains closed.

## Authority and preserved scope

The final exact source tuple, tested anchor, environment and unused root are in `Handoff/WEB_TO_LOCAL.md` under `Docs/AssemblyShadow`. The three external implementation pins and reference-core/package pins remain unchanged.

The top-level runner retains **36 cells**: entry/final authority, verifier contracts, reference worktrees, two graph suites, admission suite, Player fixture/prerequisite checks, four prepare/build pairs, one actual Editor run, and nineteen fresh-process Players. Independent cells continue; failed prerequisites block dependents. There is no semantic retry or relabeling of failed evidence.

## Required repair observations

| Requirement | New evidence | Rejection conditions |
| --- | --- | --- |
| Producer identifies actual installed native root | Each fresh build receipt is schema 2, with `installedNativeRoot` captured from `SettingsUtil.LocalIl2CppDir` | Missing field, schema 1, copied receipt used as a substitute |
| Installed SDK belongs to the exact batch and role | `nativeBinding` in each build cell binds root, project, install hash, source pins and file count | Different role/batch, unsupported profile, relative/traversing/symlinked path |
| Legitimate generation copies are harmless, not authoritative | Build and pre-Player verification inspect only the producer-bound SDK root | Recursive search, selecting first hash match, deleting a copy to make verification pass |
| Physical native provenance remains strict | Exact installedAfter membership, size/hash, unchanged install receipt, four-source tuple, additive probe and non-generated preservation | Any stale/tampered/missing/extra source or wrong pin |
| Actual app provenance remains strict | Original Player inventory and ARM64 checks; repeated pre-launch build verification | Wrong architecture, mutated app/source/overlay or failed build receipt |
| Explicit Editor scope retains every executable package case | `editor-scope.json` enumerates 754 exact names, 35 required R03 IDs and true-cycle test | Changed package/catalog, wrong or duplicate IDs, undeclared scope change |
| Actual selected Editor run has no skips | `editor-results.xml` and `editor-verification.json`, all 754 names Passed, aggregate Passed | Missing/extra case, any skip/failure/inconclusive/ignored label or inconsistent counts |
| Absent M01 resource contract remains visible | Exactly one excluded identity recorded as `NoCoverage` | Treating it as Passed or claiming full legacy/resource acceptance |

The one excluded identity is:

`HybridCLR.Editor.AssemblyShadow.Tests.ResourceAbiTests.FrozenDemoResourcesUseActualScriptGuidsAndOnlyAffectedBundles`

The isolated project does not provide `VersionedPrefab.prefab`, `Business.unity` and `VersionedData.asset` at their frozen `Assets/AssemblyShadowDemo/` paths. This cycle does not fabricate those assets or substitute new GUIDs. Actual M01 resource coverage remains a separate full-stage prerequisite. Newly present frozen assets require a scope review, not automatic adaptation.

The 754-name catalog is taken from D's hash-pinned XML solely to identify tests. Its historical results are not new execution evidence. The unfiltered ignored D XML remains rejected by the new verifier. The current run must independently produce the complete filtered result and command receipt.

## Retained prerequisites and Player cases

Retain the 116 Python tests (67 previous plus 49 provenance/scope tests), both 9-case graph suites, all 35 admission/method cases, 15 Player inputs, 33 fixture metadata audits and actual compiler consumers, exact invalid-key control, valid/invalid Editor lifecycle probes, and complete-helper/package compilation with the preserved C-source negative control.

The nineteen Player cases are unchanged in `Tools/AssemblyShadow/R03/player-cases.json`: C01–C10, R01–R05, D01–D03 and O01. All require new run IDs, direct launch PIDs, request/raw/verifier bindings and fresh build authority. Candidate Release, reference Release, candidate Debug and feature-OFF roles remain mandatory. Debug labels D01–D03 are case names, not permission to reuse failed batch D.

## Completion and return

A focused batch is `EvidenceReadyForPrimaryReview` only when all 36 cells pass and the focused evidence seal passes. `R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false` and `fullLegacyRegressionAcceptance=false` remain mandatory. The excluded M01 test stays `NoCoverage`, even on a successful focused run.

Preserve all existing result/ledger/index/archive/seal, commands, fixtures, compiler responses, lifecycle completions, build receipts/apps, Editor XML and Player evidence. Additionally preserve `editor-scope.json`, `editor-verification.json`, and each build cell's `nativeBinding`. Missing outputs stay NotRun/Unavailable; never manufacture them.

If evidence exceeds the single-file transport limit, preserve the original live archive and publish exact ordered byte parts with a new transport manifest and reconstruction audit, using the existing D transport convention. Do not re-compress, replace or mutate the original sealed archive. Transport metadata is separate from the runner's seal.

Local owns only its factual report, return and new immutable checkpoint. Any non-trivial implementation, change to provenance/scope/expectations, or runtime failure returns to Primary. No retry of A/B/C/D/E or execution of blocked cases outside the batch is authorized.
