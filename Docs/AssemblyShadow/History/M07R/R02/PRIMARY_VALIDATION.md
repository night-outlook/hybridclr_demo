# R02 Primary Validation — successor to batch H

Result: **Passed for bounded Primary source/host scope. Awaiting real Local Validation.**

## Exact authority

- Input Local return: `d33792957303488e03529c945ac01ce0eedd660b`.
- Common executable/tool source: `a81bb0d7b886fe941ba4b132296a30dcf4a319cc`.
- Selected CI authority: `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d`.
- Matched H1-runtime control: `codex/r02-h1-runtime-control@21c689732cd8087f8ee8fdce4e52a8f2a655f722`.
- HybridCLR, both roles: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
- Managed package, both roles: `b936a495ade1691ebb6f3bab8fdff3ef34f6f192`.
- **New candidate IL2CPP:** `a6e0b39c58c1c41bec1baa0a716c6bc6d77e3e4c`.
- Control IL2CPP remains `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Control includes the common source as explicit ancestry and differs only in `ProjectSettings/AssemblyShadowSourcePins.json`. Candidate post-source changes are permitted metadata only. No source-policy allowlist was broadened. Use the final verified candidate transport HEAD in Primary's prompt, not this earlier source or CI authority. The user Mac checkout was not accessed here.

## Findings and implemented disposition

H remains historically 25 Passed, 5 Failed and 4 Blocked with a complete seal. Its count132 and 1,119 Editor passes are genuine H results, not validation of the new native code. Warm P01/P03 rows had 10,000 proof attempts and unready outcomes. Their counters do not identify the responsible physical source/target class.

The native correction separates concrete AOT definition layout already copied from compiled registration from lazy `size_inited` field/static setup. It never initializes a protected baseline. Only fixed, concrete AOT definitions gain the alternative readiness test; active readiness, composite restrictions, all layout comparisons and cache-hit guards remain. The bounded sixteen-record cold readiness diagnostic enables the next run to report the exact class state. Cold logging overhead is not subtracted from performance measurements. `H_RUNTIME_REPAIR.md` records the source invariant and remaining uncertainty.

The current M07/startup wrapper validates the exact known R02 extension before delegating an in-memory legacy view to unchanged strict validators, preserving original raw bytes and hashes. Unknown, duplicate, missing and mistyped fields fail. It checks source authority before/after and requires all fourteen M07 and eleven startup modes. Startup uses the existing `r01_early_results.main`. Diagnostic output now honors the existing distinct `Builds/AssemblyShadow/R01B` artifact policy; no provenance check was waived.

This is a focused implementation self-review, not the independent R02 stage review. No real Unity Player, VM integration build, warm-path measurement or actual Editor test was executed in Primary.

## Actual selected validation

All four final workflows tested `c5278a1a6fe024f1b00f8807d4e162e8e6f17d4d` and completed successfully.

| Check | Result and boundary |
| --- | --- |
| R02 workflow **36431496003**, Linux | All nine Primary subcells Passed; Python **236/236**, zero failures/skips |
| Same workflow, macOS focused tests | **97/97** Passed; repeated subset of the 236 tests |
| Python in current Primary environment | **236/236** Passed, zero failures/skips in the final selected run |
| Actual macOS contract workflow **36431496157** | Native writer at levels 0/1/2, actual managed parser, and new Python extension validator; twelve native plus one legacy fixture and **1,310 checks Passed** |
| Actual Linux writer/parser contract | Same twelve native plus one legacy fixture and **1,310 checks Passed** |
| Dedicated macOS include regressions | **8/8** Passed; part of the 236-test inventory, not additional unique cases |
| Native production-header matrix | **70/70** process cases, **1,540** checks |
| Native revision matrix | **70/70** process cases, **168,616** checks, including the fixed-AOT/10,000-warm-allocation regression |
| Native deterministic source recipe | Passed against immutable H1 input blobs; protected guard body hashes unchanged |
| Managed Baseline/P01/P03 | **102 / 111 / 111** checks, clean process groups; not Unity execution |
| Scoped legacy workflow **36431495940** | **384/384** current cases; **6/6** fixed-H1 positives; remaining R01/M07/R01B workflow steps Passed |
| M00 origin workflow **36431495954** | Exact frozen archive/member/compact-fixture provenance Passed |
| Source authentication | **3,412** exported files match size/SHA-256/Git blob; all **13** changed executable paths across demo/native match tested bytes |
| Artifact and receipt authentication | Five ZIP sizes/digests/CRCs and unique member inventories verified; **226** unique nested source/output bindings authenticated with none unresolved |

The native matrices use the production proof/cache/readiness headers with synthetic physical-class descriptors. They do not compile the full IL2CPP VM. The native resolver source is authenticated by the deterministic recipe; actual VM compilation and the unchanged Player warm oracle remain Local requirements. All actual Unity/dnlib/linker/serialization tests remain required in Local.

Both native-writer/parser executions completed nineteen commands, including compiler-version capture, with zero exits and clean process groups; thirteen emitted fixtures were bound and checked. The known extension is native-produced; the outer legacy object is a labeled host fixture and Unity Preserve is stubbed. BCL serialization is not Unity serialization. The new Python bridge also validates those actual native extension fixtures.

The current environment has no .NET SDK; managed execution above is CI execution. Local native matrices and the 236 Python tests ran here. Initial development-test/validation-adapter failures are retained separately and were not relabeled; only final selected runs count. The verification adapter respects the native stdout/stderr receipt schema separately from outer process-group receipts.

Codec attribution remains four unchanged profile-2 allocation requests totaling 29,884,384 bytes plus a 120-byte object on the CI ABI; it is not Unity RSS, allocator overhead or new R02 memory.

## Retained final CI artifacts

| Scope | Artifact ID | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| primary | 10974042248 | 13,556,200 | `f56b45e9ac302244e065068df1370e58659351ab7a5d6aa6c98f37dc65cf8cb5` |
| macos-contract | 10973811620 | 206,482 | `ee1931a2c769668cfddc6e04162af8229cad3481dc17bd204811d7816fe4b4e1` |
| darwin | 10973816572 | 2,822 | `d3515d5e78d0a46d368c2c6691c91e3794389f6106e8a02e495f135991ae64b3` |
| legacy | 10973562806 | 13,018,355 | `1e1fcfb30a22bc7b42d95a61bc296ac03a12e4673d27d960af4620721fa2b08c` |
| origin | 10973961382 | 3,068 | `e49ec69555beb5b28b8beff1e7a2c43e8842d63e7bd5c2166360b0b9cb5b6f3f` |

All five artifacts were downloaded through the Connector and authenticated. `H_PRIMARY_VALIDATION.json` records exact source changes, selected raw members, repository identities, guarded-source hashes and results. Bindings use explicit CI checkout/output prefixes and pinned native relative paths, not basename search. The earlier source-only run 36430690352 also passed and was separately inspected; the authority runs above are the selected final evidence.

## Next Local cycle and stopping point

Run one fresh **34-cell R02LocalBatch-v1** from the final pushed transport and fixed control. Candidate native changed, so fresh source-bound installation/builds and affected regressions are mandatory. All eight sidecars, particularly unchanged P01/P03 warm certificate checks, must pass before four pilot plus forty formal A/B pairs. Require five exact Editor contracts, full M07/startup/failure/count132, diagnostic/lazy-dense/ordinary-mixed-capacity, final authority and full sealing.

Preserve A/B/C/D/E/F/G/H and H1 evidence. Return exact class-readiness logs and raw counter rows if the warm path still fails. Do not initialize baseline classes, relax warm assertions or replace original provenance to obtain a pass. D1/D2 still require measured disposition before H2. Independent R02 review is eligible only after complete Local evidence. H1 remains PassedWithExplicitDeferredRisk; R02Accepted=false; mayEnterR03=false.
