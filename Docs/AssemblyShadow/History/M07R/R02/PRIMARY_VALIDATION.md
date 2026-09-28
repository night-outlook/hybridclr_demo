# R02 Primary Validation — successor to batch F

Result: **Passed for the bounded Primary host/source scope. Awaiting real Local Validation.**

## Exact authority

- Input Local return: `6415fdf3cc384c0fb8fa7073d8b1ee3631702e0f`.
- Final executable/tool source anchor: `995dbf1003c306a69586f882ff02599db7a9780e`.
- CI-tested candidate authority: `a01ac8169ccdbaacc3eec8ce81009f38eb100d64`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@95b85617c92f8ce806f4652d88077936c76c3b8a`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- **Updated managed package, both roles:** `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`.

The control includes the common source anchor as Git ancestry and differs from that source tree only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate post-anchor changes are documentation and source pins only. The final handoff must use the latest verified transport HEAD, not the earlier source or CI commit. No source-policy allowlist is broadened.

## Returned problems and implemented disposition

Batch F reached current controlled builds and Player execution, but finished with 22 Passed, 8 Failed and 4 Blocked cells followed by failed complete sealing. Its 1,984-file preservation inventory is not a complete seal. Neither a complete `LOCAL_BATCH_RESULT.json` nor complete sealed archive was produced; those historical facts remain unchanged.

| Finding | Primary disposition | Actual Local verification still required |
| --- | --- | --- |
| Native `r02` extension rejected by managed parser | Strict optional 33-field extension; exact UInt64/token/schema/coverage handling, no generic unknown-field skip | Candidate ON sidecars and startup positives through actual Player APIs |
| Serialization/linking compatibility of the extension | Eighteen legacy public serialized fields retained; non-serialized parsed view; separate exact 33-field pre/post-link proof | Unity builds, stripping proof and all three new Editor tests |
| M07 launched without required early capsule | Prepare the existing mode-specific Control capsules and supply their root before launching | Actual native startup receipts, then M07 semantic/raw results |
| Nested count fixture sent to parameter auditor | Explicit family-to-existing-auditor dispatch | Fresh generation, both audits and 132-cell Player matrix |
| Diagnostic generation left linker input modified | Capture linker bytes in diagnostic/count transactions; allow only the observed exact expansion and restore originals | Actual generated linker set, build and restoration receipts |
| E raw forensic paths disappeared before sealing | Snapshot inputs before builds; exact Git/index/archive-bound recovery when live inputs are absent | Snapshot/archive acquisition in the user's retained evidence environment, complete new seal |

`F_INTEGRATION_REPAIR.md` supplies design, test mapping and limits. This is an implementation self-review, not a genuinely independent R02 stage review. M07's missing early arguments are a sufficient source-level cause of the observed refusal; the sparse old log does not prove that no additional cause exists. E archive recovery never repairs or relabels F's failed seal.

## Actual validation performed

All selected workflows tested `a01ac8169ccdbaacc3eec8ce81009f38eb100d64` and completed successfully:

| Check | Result and boundary |
| --- | --- |
| R02 workflow **36372371088**, Linux | Python **203/203**, zero failures/skips; source/native/managed checks Passed |
| Same workflow, macOS arm64 | **72/72** focused lifecycle, prerequisite, materialization, forensic-retention and batch-repair tests; repeated subset of the 203, not additional unique cases |
| Python in current Primary environment | **203/203 Passed**, zero failures/skips in the final selected run |
| Actual native-extension writer to actual package parser | **1,310 checks Passed**, twelve native extension fixtures and one legacy fixture; all diagnostics levels, saturation/truncation, field fidelity, malformed inputs and serialization round trips |
| Native production-header matrix | **70/70** process cases, **1,540** checks; not full IL2CPP VM integration |
| Native revision matrix | **70/70** process cases, **28,294** checks |
| Managed Baseline/P01/P03 | **102 / 111 / 111** assertions with clean process groups; not Unity execution |
| Scoped legacy-H1 workflow **36372371077** | **384/384** current reusable/rejection cases, **6/6** fixed-H1 positive cases; remaining R01/M07/R01B workflow steps Passed |
| Immutable M00 workflow **36372371129** | Exact frozen archive/member/compact-fixture provenance Passed; no new Player execution |
| Source artifact authentication | All **3,276** inventoried source/input files match size, SHA-256 and Git blob; all **19** changed executable paths across demo/package match tested bytes |
| Artifact authentication | Four ZIP sizes/digests/CRCs and member inventories passed; **137/137** unique nested exported bindings authenticated, no unavailable member |

The interoperability host compiles the production `AssemblyShadowR02Diagnostics.h` writer and links the production package parser plus the independent schema inventory. The outer legacy object is explicitly a synthetic fixture; the R02 extension is native-produced. Only the Unity Preserve attribute is stubbed. Real BCL JSON round trips verify the unchanged legacy shape. These checks do not replace real Unity serialization or linker execution.

Three new `R02TypeResolutionSchemaTests` were authored for real Editor/dnlib/Unity verification and are **NotRun in Primary**. They test every missing linked extension field, equally narrowed pre/post schemas, and Unity serialization of the transient view. Local must report all three plus the existing two `R02ProbeContractTests` as Passed before claiming Editor coverage.

Codec attribution also passed for both host compilers; its unchanged profile-2 allocation requests are not Unity RSS or new R02 memory. Earlier local test-development failures and preliminary successful CI runs are not substituted for the final selected evidence.

## Retained final artifacts

| Scope | Artifact ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Primary | 10949217962 | 13,192,862 | `8381e04ea33696758124664540d328c1dc36bd5f423be219418cf093c8e79388` |
| Darwin | 10949164749 | 2,136 | `f6372fc3fc8ac7f961ded0a97b0b8868fd0e492bbcf4e6ff0f0d1223e07f7f89` |
| Legacy | 10949871106 | 13,005,130 | `5ccfe7a05f0ac4bfafda88a2e867594ae9bd92b8bb1b1d26457d8247f6ddf9ee` |
| Origin | 10949497740 | 3,068 | `ec638883cd5d656150d368a7f35d97110639d40c1e8d6f6eb6ccb37f0f863549` |

Artifacts were downloaded through the Connector and authenticated locally. `F_PRIMARY_VALIDATION.json` records repository identities, exact changed blobs, selected raw member hashes, counts and scope. Nested bindings were resolved using the workflow's explicit checkout roots and pinned native-repository relative paths, not a basename search. The CI evidence records the CI authority commit; later documentation does not retroactively change that identity.

## Stop and next Local cycle

Run one fresh **34-cell R02LocalBatch-v1** from the final pushed candidate transport and the fixed control above. Both must use the new package and produce fresh source-bound builds. Preserve A/B/C/D/E/F, their retained inputs and H1 evidence. No old F graph becomes a new-package build merely through metadata updates.

Actual Unity compilation, serialization/linker tests, early startup, parser-enabled sidecars, controlled performance, count/diagnostic/capacity regressions and complete sealing remain Local work. No non-trivial implementation is assigned to Local. Commission the independent R02 stage reviewer only after eligible evidence. H1 remains PassedWithExplicitDeferredRisk; D1/D2 require measured disposition before H2; R02Accepted=false; mayEnterR03=false.
