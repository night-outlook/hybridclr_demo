# R02 Primary Validation — successor to batch G

Result: **Passed for the bounded Primary host/source scope. Awaiting real Local Validation.**

## Exact authority

- Input Local return: `4c4f50adfd3a44073d14b107227f399c53ea605c`.
- Executable/tool source anchor: `af9ba49127a7e852fed504a55c733c5f6ec5e54e`.
- Selected CI authority: `5c7b9babca7257edb61976f50e3b8a51fc18abd6`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Managed package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Control contains the common source as explicit ancestry and differs from its tree only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate transport after the source anchor is metadata-only under the unchanged policy. Use the final remotely verified candidate transport HEAD in Primary's prompt, not the earlier source/CI commit. No runtime/package branch changed in this cycle.

## Returned failure and correction

G correctly returned 9 Passed, 1 Failed and 24 Blocked with a complete audited seal. Its host contract compiler exposed project `vm/string.h` through `-I`, so macOS libc++ selected it instead of the system string header. No producer/parser assertion or Unity build ran after that failure. G's results and raw evidence remain unchanged.

The corrected shared compiler-command builder uses `-iquote` for quoted project headers, not `-I` or an expanded native-root search. Compiler/platform/version and all emitted fixtures are recorded. Eight new tests include an actual negative control that reproduces header shadowing with `-I`, then compiles/runs with `-iquote`, including quoted siblings and paths with spaces. Mocked orchestration cases remain synthetic; they do not establish parser semantics.

The added macOS workflow runs the **actual** native writer and **actual** package parser at levels 0/1/2. This closes the CI coverage gap: the existing macOS lifecycle subset alone did not execute that compiler path. The native writer, parser, 33-field schema, UInt64 and coverage checks, fixture counts, serialization tests, runtime code, timeouts and all five required Editor tests are unchanged.

`G_INCLUDE_REPAIR.md` records the design, compiler references, regression mapping and rollback boundary. The review here is a focused implementation self-review, not the independent R02 stage review.

## Selected execution evidence

All final workflows below tested authority `5c7b9babca7257edb61976f50e3b8a51fc18abd6` and passed.

| Check | Actual result and limit |
| --- | --- |
| R02 workflow 36393519340, Linux | All nine Primary subcells Passed; Python 218/218, zero failures/skips |
| R02 workflow, existing macOS lifecycle subset | 79/79 Passed; repeated subset, not additional unique cases |
| Actual macOS contract workflow 36393519338 | macOS 14.8.9 arm64, Apple clang 15.0.0; levels 0/1/2 compiled and emitted twelve native extensions plus one legacy fixture; actual managed parser passed 1,310 checks |
| Same dedicated macOS workflow | Eight new include/orchestration regressions Passed; these are part of the 218-test inventory |
| Actual Linux writer/parser contract | Same twelve native plus one legacy fixture and 1,310 checks Passed |
| Both contract executions | All nineteen command receipts, their stdout/stderr bindings and thirteen fixture bindings authenticated; all commands exited zero with clean process groups |
| Python in current Primary environment | 218/218 Passed, zero failures/skips; real collision test exercised available GCC and Clang drivers |
| Native production-header matrix | 70/70 process cases, 1,540 checks; synthetic classes, not full IL2CPP VM integration |
| Native revision matrix | 70/70 process cases, 28,294 checks |
| Managed Baseline/P01/P03 | 102 / 111 / 111 assertions, clean process groups; not Unity execution |
| Scoped legacy workflow 36393519418 | 384/384 current reusable/rejection cases, 6/6 fixed-H1 positives; remaining workflow regressions Passed |
| Immutable M00 workflow 36393519352 | Exact historical archive/member/compact-fixture provenance Passed |
| Source and artifact authentication | 3,336 exported files match size/SHA-256/Git blob; all three changed executable blobs match tested bytes; five ZIP sizes/digests/CRCs and unique member lists verified |

The contract still uses a labeled synthetic outer legacy object and stubbed Unity Preserve attribute, with the actual native extension, actual parser and independent schema inventory. BCL serialization tests are not Unity serialization. Actual Unity/dnlib/linker tests remain Local requirements.

Codec attribution remains four unchanged profile-2 allocation requests totaling 29,884,384 bytes plus a 120-byte object on the CI ABI; it is not Unity RSS or new R02 memory. Local Python compilation, YAML, embedded Python and shell syntax checks also passed. The current chat environment has no .NET SDK; actual managed execution reported above is CI execution, not a claimed local SDK run.

## Retained final artifacts

| Scope | Artifact ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Primary | 10957845251 | 13,286,139 | `e5d16be0e60ea0e9ee323c948adf0613eec34a7ad63b880aa4587baf60ebad80` |
| Actual macOS contract | 10957481858 | 206,493 | `5620f7538f52c2c9a4e4b255b5f382141c30a2cf86376cef0c00bf6f84ba43c2` |
| Darwin lifecycle | 10956813919 | 2,313 | `418b90ba83f5134e9e109d47e2e108ed07f05de4b07dca4b78bc1c7db14ab3c9` |
| Legacy | 10957551024 | 13,009,355 | `ea3bee0e4f6e4bb054b8cfa549ace0e2e4934ad163df0342a88163867c605233` |
| Origin | 10957047950 | 3,068 | `aad045ac004f9610c8f9435050d6af157d41b34d819b1b1c2b7a014663c6505f` |

All five were downloaded through the Connector and verified. `G_PRIMARY_VALIDATION.json` binds selected raw members, repository identities, source blobs, result counts and artifact digests. The earlier source-only macOS run 36393199569 passed too; it is not substituted for the final-authority evidence. Earlier F validation records and G Local results retain their original scope in Git history.

## Stop and next Local cycle

Run one fresh 34-cell R02LocalBatch-v1 using the final published candidate transport and fixed control above. Host contract execution remains mandatory locally; CI does not exempt it. Then execute fresh controlled builds, eight sidecars, four pilot plus forty formal A/B pairs, five Editor contracts, all affected regressions, final authorities and complete sealing.

Primary did not run the user's Unity/Player environment or rerun G. Preserve A/B/C/D/E/F/G and H1 history. Commission independent R02 stage review only after eligible complete evidence. H1 remains PassedWithExplicitDeferredRisk; D1/D2 require measured disposition before H2; R02Accepted=false; mayEnterR03=false.
