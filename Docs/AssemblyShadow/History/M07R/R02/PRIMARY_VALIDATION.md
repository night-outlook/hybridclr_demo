# R02 Primary Validation — final batch-F coverage handoff

Result: **Passed for the bounded Primary host/source scope. Awaiting real Local Validation.**

## Exact authority

- Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.
- Recovered published batch-F repair: `d43663e9ff96a9249d5e7bbf1e02bbd7e40f552b`.
- Final executable/tool source: `1642392278a97bc9348195e35ec5d1b7fb6fa530`.
- CI-tested candidate authority: `4a6a8d604e27aa5e3175149c4df0170b8ec09b05`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@028ad68fa25a531be07f11f1fdcc417842f98ab4`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Managed package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.

The control includes the final source as Git ancestry and differs only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate post-source commits are permitted metadata only. The final prompt must identify the final pushed transport HEAD, not substitute the source or CI commit. No source-policy allowlist was broadened.

## Repair and finalization review

The batch-F integration repair remains fully included: strict known 33-field R02 extension parsing with exact unsigned values; unchanged eighteen-field legacy serialization and separate linked-extension proof; M07 mode-specific early capsules; correct parameter/nested auditor dispatch; bounded diagnostic/count linker restoration; stable E raw snapshots and exact Git/index/archive-bound recovery. `F_INTEGRATION_REPAIR.md` retains the original design and its source identity.

On resumption, the selected original CI artifact was reauthenticated (3,276 files) and its 203-test Python suite rerun successfully. One further acceptance gap was found: the batch checked only the two old probe tests, although the handoff also required three new schema/serialization tests. The final runner now requires each of the five exact full names exactly once and Passed, checks overall NUnit success, and includes all five in the XML-bound `requiredCases` receipt. Missing, skipped, duplicate and foreign-namespace cases fail. Unrelated skips remain reported, not promoted.

`F_EDITOR_COVERAGE_FINALIZATION.md` records this focused correction and seven added host tests. Only `run_local.py` and `tests/test_f_batch_repairs.py` changed executable bytes after the recovered publication. No runtime/package, Editor test body, native writer, fixture, timeout, restoration or formal timing change was introduced by this finalization.

This is a focused implementation self-review, not the independent R02 stage review. F's sparse M07 log cannot exclude additional causes beyond the diagnosed missing early arguments. Its historical failed complete seal is not repaired or relabeled by the new snapshot implementation.

## Actual selected validation

All workflows below tested `4a6a8d604e27aa5e3175149c4df0170b8ec09b05` and completed successfully.

| Check | Result and boundary |
| --- | --- |
| R02 workflow 36387357718 — Linux | Source/native/managed checks Passed; Python **210/210**, zero failures/skips |
| Same workflow — macOS arm64 | **79/79** focused lifecycle, prerequisite, materialization, retention and batch-acceptance tests; repeated subset of the 210, not additional unique cases |
| Python in the current Primary environment | **210/210 Passed**, zero failures/skips; seven Editor-coverage tests use synthetic XML and mocked Unity invocation |
| Actual native extension writer to actual package parser | **1,310 checks Passed**, twelve native extension fixtures plus one legacy fixture, numeric/schema/coverage/malformed inputs and BCL serialization round trips |
| Native production-header matrix | **70/70** process cases; **1,540** checks; synthetic classes, not full IL2CPP VM integration |
| Native revision matrix | **70/70** process cases; **28,294** checks |
| Managed Baseline/P01/P03 | **102 / 111 / 111** assertions, clean process groups; not Unity execution |
| Scoped legacy workflow 36387357712 | **384/384** current reusable/rejection cases; **6/6** fixed-H1 positives; other R01/M07/R01B workflow steps Passed |
| Fixed-origin workflow 36387357717 | Immutable M00 archive/member/compact-fixture provenance Passed; protected DLL hash unchanged |
| Source authentication | **3,278** exported files match size, SHA-256 and Git blob; both final changed executable blobs match tested bytes |
| Artifact authentication | Four ZIP sizes/digests/CRCs and unique member inventories verified; **137/137** nested exported bindings verified |

Native/revision raw stdout/stderr hashes and exit codes were checked under their native receipt schema. Outer host/build/exec command receipts passed their process-group cleanup checks. Codec attribution remains four unchanged profile-2 allocation requests totaling 29,884,384 bytes plus a 120-byte object on the CI ABI, not Unity RSS or new R02 memory.

The cross-language host uses the actual native header and package parser; the outer legacy object is synthetic and Unity Preserve is stubbed. BCL serialization is not Unity serialization. All five actual Editor tests and Unity/dnlib/linker execution remain NotRun in Primary and mandatory in Local.

## Final artifacts

| Scope | Artifact ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Primary | 10955057360 | 13,205,038 | `b7f0152ebc7840060027e0679afe0ace7bc8976598e55ce7a3daf54aa33b6d28` |
| Darwin | 10954434941 | 2,314 | `26685a35b74c99f17687399f34bfd21457654eac2945beb8e4400eb4681815fe` |
| Legacy | 10954383544 | 13,006,535 | `853d5a10b4ac92fd3808e9f0564ebf0fab6213f5a68e449f0918026341707d4e` |
| Origin | 10954897908 | 3,068 | `c443b43da6359214e9d99b8e57b9caa8ee366f454e47eccfbe034f60fcbc0a82` |

`F_COVERAGE_VALIDATION.json` binds selected raw members, exact source changes, repository identities and test results. Bindings use explicit CI output and checkout prefixes, not basename search. `F_PRIMARY_VALIDATION.json` and earlier CI remain unchanged evidence for the previous repair authority. The local verification adapter was corrected for differing native receipt schemas and combined stdout/stderr logs; those adapter errors did not modify any CI result or production verifier.

## Stop and next Local cycle

Run one fresh **34-cell R02LocalBatch-v1** using the final pushed candidate transport, control above and new package in both workspaces. Require fresh controlled builds, eight functional sidecars, four pilot plus forty formal A/B pairs, all five machine-enforced Editor contracts, native/generated-transaction/M07/startup/failure/count/diagnostic/lazy-dense/capacity regressions and complete sealing.

Preserve A/B/C/D/E/F, their retained inputs and H1 evidence. F remains 22 Passed, 8 Failed, 4 Blocked followed by failed sealing; its partial inventory is not a complete archive. No Primary work accessed the user's Mac, reran F, ran a Unity Player or granted runtime acceptance. No non-trivial implementation is assigned to Local. Commission the independent R02 stage reviewer only after eligible evidence. H1 remains PassedWithExplicitDeferredRisk; D1/D2 require measured disposition before H2; R02Accepted=false; mayEnterR03=false.
