# R02 Primary publication — batch-E successor

Status: **Published source/control authority; Primary CI passed. Final documentation transport commit follows this record.** No Local implementation is requested.

## Fixed identities

- Local return/base: `1d7dc134003206ada8a92b50763ca2da7dc9530d`.
- Read-only archive investigation: `74e41cdc0173379b424014de151ae5413fd1c9a3`.
- Executable/tool source: `d4cfbe5da29482a3b307fbec3333821615288129`.
- Matched control: `codex/r02-h1-runtime-control@5a931fe86795e8cc192d3df262cdee824b105963`.
- Candidate authority: `69f75b78a0696be8b7da69c1725f07c6e1708c48`.
- Candidate HybridCLR/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `3981da12f2cd3ee878a04dda6f573d0ad3faeda5`.
- Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`.

## Performed publication

1. Read Local return and exact remote tuple through the Connector; demo write/read-back smoke test passed on a disposable branch.
2. Inspected the already tracked historical archive in read-only CI; recovered and hash-authenticated the exact protected M00 image and provenance.
3. Implemented materialization, safe compact decoding, source/origin checks, independent PE diagnostics, tests and integration; removed the invalid new-compilation-equals-fixed-image helper. Original fixed hash, provider semantics, source allowlist and runtime code remain unchanged.
4. Published executable source, then advanced the existing matched control with common source as additional parent and its tree plus only H1-runtime source pins. No force-push or history rewrite.
5. Published candidate pins, source-targets, WEB_TO_LOCAL and 34-cell task sheet. All later deliverables are metadata-only.
6. Verified successful final R02, macOS, legacy and origin CI at candidate authority. Downloaded four selected artifacts and authenticated digests, CRCs, source inventory, changed source paths and nested receipt bindings. Exact identities appear in E_PRIMARY_VALIDATION.json.
7. Update canonical status/validation docs, publish this metadata-only commit, re-read all remote heads and compare the final candidate/control trees against the frozen source. Supply the actual returned final transport SHA in the Local prompt.

Candidate paths: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repository>`.
Control paths: `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/<repository>`.
Both demo checkouts use their specified branches; control siblings may be detached at exact source-target commits. No generated output crosses workspaces.

## Stop boundary

All code changes belong to Primary. Local executes the supplied batch, collects evidence and returns non-trivial issues; it does not rewrite pins/fixtures/verifiers. E forensic results remain pending on retained Local raw bytes, without blocking otherwise valid fresh build cells. Original A/B/C/D/E attempts remain immutable. No host/source CI establishes R02 runtime or D1/D2 acceptance. R02Accepted=false; mayEnterR03=false.
