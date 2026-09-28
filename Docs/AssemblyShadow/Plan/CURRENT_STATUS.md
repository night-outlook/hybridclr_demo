# Current Status — batch-G host include repair; awaiting Local Validation

- Input Local return: `4c4f50adfd3a44073d14b107227f399c53ea605c`.
- H1: `PassedWithExplicitDeferredRisk`; D1=A/D2=A remain development-stage deferrals.
- Source/tool anchor: `af9ba49127a7e852fed504a55c733c5f6ec5e54e`.
- Selected CI authority: `5c7b9babca7257edb61976f50e3b8a51fc18abd6`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Matched control: `codex/r02-h1-runtime-control@2e8ae9f5e5fa30325a4b6225b34a602477d7aa0e`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate/control IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- R02Accepted=false; mayEnterR03=false.

## Completed Primary work

G's native host compile failed because `-I` exposed the project's `vm/string.h` to standard library includes. The compiler command now uses quote-only project search via `-iquote`; no additional native-root include path or Local workaround is needed. All native/parser semantics and strict assertions remain unchanged. Compiler/platform/version and fixture diagnostics are recorded.

Eight new tests cover the real collision and negative control, quoted sibling resolution, path spaces, all diagnostics levels and failure propagation. The full Python suite passes 218/218 locally and in Linux CI. The new dedicated macOS workflow executes the actual writer/parser at levels 0/1/2, passing 1,310 checks and all nineteen commands with clean completion. The existing macOS lifecycle subset passes 79/79; the new eight tests are repeated there only in the dedicated contract workflow, not additional unique cases beyond 218.

Final authority workflows Passed: 36393519340 (R02), 36393519338 (actual macOS contract), 36393519418 (legacy), 36393519352 (origin). Native matrices remain 70/70 each; managed host assertions 102/111/111; scoped legacy 384/384 and 6/6. All 3,336 source/input files and the three changed executable blobs match the downloaded tested artifact. Details and digests are in `History/M07R/R02/PRIMARY_VALIDATION.md` and `G_PRIMARY_VALIDATION.json`.

Control contains the new source as ancestry and differs only in source pins. Candidate post-anchor changes are metadata-only. All three runtime/package repositories remain unchanged. The final prompt must use the latest verified transport HEAD, not the earlier source or CI commit.

## Next action and gates

Run one new unused 34-cell R02LocalBatch-v1. Local host contract validation remains mandatory before fresh Unity graphs. Complete all eight sidecars, four pilot plus forty formal A/B pairs, five Editor contracts, native/generated/M07/startup/count/diagnostic/capacity regressions, final source checks and full sealing. Commission independent R02 review only when complete evidence is eligible.

G remains ReturnRequired: 9 Passed, 1 Failed, 24 Blocked, with a complete audited seal and no new Unity graph. Preserve A/B/C/D/E/F/G and H1 history. No Primary Unity/Player execution or runtime acceptance is claimed. D1/D2 still need measured disposition before H2. Stop before R03.
