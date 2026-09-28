# R02 Primary Validation — successor to batch E

Result: **Passed for the bounded Primary host/source scope. Awaiting real Local Validation.**

## Exact authority

- Input Local return: `1d7dc134003206ada8a92b50763ca2da7dc9530d`.
- New executable/tool source anchor: `d4cfbe5da29482a3b307fbec3333821615288129`.
- CI-tested candidate authority: `69f75b78a0696be8b7da69c1725f07c6e1708c48`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@5a931fe86795e8cc192d3df262cdee824b105963`.
- Candidate HybridCLR/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`; the other runtime/package pins match the candidate.

Control includes the common source as explicit ancestry and its tree differs only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate post-source commits change documentation and source pins only. No source-policy allowlist is broadened. The final Local prompt uses the final pushed documentation transport HEAD, not the earlier source or CI commit.

## Finding disposition and limits

The original batch E remains ReturnRequired: 9 Passed, 2 Failed, 22 Blocked. It confirmed Roslyn v2 cleanup on the two installers and failed compiler commands, but produced no accepted controlled graphs, functional Players or D1/D2 series.

The defect was a contract mismatch in R02 preparation: the helper required a newly compiled ordinary provider to reproduce an immutable `FixedAssemblyBytes` witness. The unchanged witness contract separately specifies compiler provider semantic variants. The fixed ReflectionBindings image and a compiled provider already differ inside the authenticated historical H1 archive.

Primary recovered the exact frozen 4,608-byte DLL from that archive, preserved SHA-256 `9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27`, and supplied an independently materialized, origin-bound compact fixture for each checkout. Wrong existing bytes, links, races, changed origin/pins and old compiler receipts still fail. Correct existing staged bytes are not rewritten. The obsolete compiler-and-stage helper/stub is removed. Fresh M07 compiler, semantic provider, source and fixed-byte checks remain unchanged.

New schema-2 receipts explicitly say `FrozenHistoricalInputMaterialization`, not fresh compilation or reused Player execution. Neither role reads the other role's generated output. The materialized image is historical input to new executions, not historical execution evidence promoted to R02.

The frozen DLL's CodeView PDB path and MVID were inspected directly. The raw E candidate/control DLLs are not available in Primary. Their exact differing fields and complete compiler cause therefore remain unproven here. The implemented read-only `m00-batch-e-forensics` cell authenticates the original Git receipts and retained raw files, compares all three pairs, records byte spans/MVID/PDB paths and conservative provenance-only comparisons, and never authorizes normalized bytes.

See `E_M00_REPAIR.md` for design, official compiler references, boundaries and test mapping. This is a focused Primary self-review, not the independent R02 stage review.

## Actual validation

All selected workflows tested `69f75b78a0696be8b7da69c1725f07c6e1708c48` and completed successfully:

| Check | Result and boundary |
| --- | --- |
| R02 workflow 36330847917 — Linux | Source/native/managed checks Passed; Python **191/191**, zero failures/skips |
| R02 workflow 36330847917 — macOS arm64 | **60/60** process identity, completion, native prerequisite, materialization and PE-forensic tests. Repeated subset of the 191 tests, not additional unique cases. |
| Python in current Primary environment | **191/191** Passed, zero failures/skips |
| Native production-header matrix | **70/70** process cases, **1,540** checks; synthetic physical classes, not IL2CPP VM integration |
| Native revision matrix | **70/70** process cases, **28,294** checks |
| Managed host Baseline/P01/P03 | **102 / 111 / 111** assertions with clean process groups; not Unity execution |
| Scoped legacy-H1 workflow 36330847766 | **384/384** current reusable/rejection cases; **6/6** fixed-H1 positives; remaining R01/M07/R01B workflow steps Passed |
| Immutable M00 origin workflow 36330847788 | Exact archive digest/member and compact fixture authenticated byte-for-byte; no staging or runtime execution |
| Source artifact authentication | **3,146** inventoried files match size/SHA-256/Git blob; all **16** changed source paths match tested content or expected deletion |
| Artifact authentication | Four ZIPs match declared size/digest and CRC; **48** unique nested exported bindings authenticated; selected raw logs and result hashes recorded |

Codec storage checks also passed for GCC and Clang: four unchanged profile-2 allocation requests totaling 29,884,384 bytes plus a 120-byte object on the CI ABI. This is not Unity RSS, allocator overhead or new R02 bytes. Initial local test-development failures remain in retained logs; only the final passing suite is selected here. Earlier D and initial R02 CI remain historical in Git and are not claimed to validate this source.

## Retained final CI artifacts

| Scope | Artifact ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Primary | 10935253012 | 10,682,540 | `d78395863b4d0ab82a2e11902f6d6450b3b182bf5f1ae24f05becb1f0b915a79` |
| Darwin | 10935178272 | 1,759 | `47444e9c3100d858a90273695948cfc179b8c4adabe188b27e6e6c8f66e89c91` |
| Legacy | 10935802048 | 12,993,014 | `03cdbf643f126519a84a1e2c93b69ab625d0b80872feb770f6d8e51d002f47e6` |
| Origin | 10934524826 | 3,068 | `5e5594525b29daf6e3b56b437c7c5e3f6fb0a724a741512704fd52ae715aa427` |

`E_PRIMARY_VALIDATION.json` records selected raw member bindings, source changes and actual results. The origin artifact contains the exact recovered DLL and its authenticated search receipt. The archive extraction inspected 1,902 members, including three exact fixed-image aliases; only the explicitly recorded CompileSnapshot member establishes the selected origin.

## Next Local cycle and stop

Run the **34-cell** successor once in a new unused root. Preserve A/B/C/D/E, their external raw inputs, seals, all H1 evidence and the historical R01 comparison. The original 33-cell scope remains; E forensics is one independent addition. A diagnostic failure retains exact evidence and does not block otherwise valid fresh builds, but full evidence readiness requires all required cells.

Actual Unity import/build/semantic checks for the materialized fixture, long M07 completion, generated-native transaction execution, functional/paired performance and affected regressions remain Local work. No non-trivial implementation is left to Local. Return exact failures and measured D1/D2 disposition; commission independent R02 stage review only when eligible. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false.
