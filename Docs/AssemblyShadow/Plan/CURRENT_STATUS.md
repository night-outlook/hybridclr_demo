# Current Status — batch-H repair awaiting Local Validation

- Input Local return: `d33792957303488e03529c945ac01ce0eedd660b`.
- H1: PassedWithExplicitDeferredRisk; D1=A/D2=A remain development-stage deferrals.
- Common source: `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`.
- CI authority: `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d`.
- Candidate branch: `codex/assembly-shadow-r01b-h1`.
- Matched control: `codex/r02-h1-runtime-control@21c689732cd8087f8ee8fdce4e52a8f2a655f722`.
- HybridCLR/package, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- Candidate/control IL2CPP: `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- R02Accepted=false; mayEnterR03=false.

## Implemented work

Concrete AOT compiled layout can now complete an allocation proof without initializing the protected baseline; all physical comparisons, active-target readiness, composite restrictions and per-hit correctness guards remain. A capped cold-readiness diagnostic and a 10,000-warm-allocation native-header regression are included. H's exact failing class remains unproven from its counters alone.

Current M07/startup validation has a source-bound strict R02 schema bridge; legacy verifiers and raw evidence are unchanged. Startup invokes its existing verifier module. The diagnostic Player now uses a new distinct canonical R01B build root, retaining full receipts and restoration. Earlier F/G repairs and all five machine-enforced Editor tests remain.

## Selected evidence

At `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d`, R02 CI 36431496003, actual macOS writer/parser CI 36431496157, legacy CI 36431495940 and origin CI 36431495954 passed. Python: 236/236 local and Linux; macOS repeated subset 97/97; actual writer/parser 1,310 checks per platform; native matrices 70/70 each, 1,540/168,616 checks; managed Baseline/P01/P03 102/111/111; legacy 384/384 and 6/6. All 3,412 source entries, thirteen changed executable blobs and 226 nested bindings authenticated.

`PRIMARY_VALIDATION.md` and `H_PRIMARY_VALIDATION.json` retain exact results, artifacts and limits. No Primary Unity/Player execution or performance acceptance is claimed. H remains 25 Passed, 5 Failed, 4 Blocked with its original complete seal.

## Required next action

Local runs one unused 34-cell batch from the latest verified candidate transport and the fixed control above, with fresh candidate native installation/builds. It verifies warm admission, eight sidecars, four pilot plus forty formal A/B pairs, five Editor tests, M07/startup/failure/count132, diagnostic/lazy/dense/capacity, final authority and complete sealing. Prior count and Editor passes cannot authenticate the new native runtime. D1/D2 require measured disposition before H2; independent review only after complete eligible evidence. Preserve all history and stop before R03.
