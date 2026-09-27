# R02 continuation implementation review

## Disposition

**Prepared repair and diagnostics are tested within the available host scope. Publication is blocked; this is not a completed or handoff-ready Primary cycle.**

The current continuation did not modify any remote repository. It recovered source and evidence from the published R02 CI artifact, continued the already-implemented R02 work, and prepared executable repairs, tests, metadata tooling and documentation. No H1 work was restarted. No Local-owned report or historical evidence was overwritten.

This is a Primary self-review and source/evidence audit, not a newly commissioned independent MILESTONE review.

## Source and evidence basis

| Repository | Published input |
| --- | --- |
| hybridclr_demo | 44a115cdeb4b5ba4d75552ec7864d20d5d5ddb25 |
| hybridclr | 1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad |
| hybridclr_unity | 0ea633a2c5b936b5af69d944593c55bd2783fca9 |
| il2cpp_plus | 3981da12f2cd3ee878a04dda6f573d0ad3faeda5 |

Branch: `codex/assembly-shadow-r01b-h1` in each repository. Identity and remote refs were read through the GitHub connection. Source snapshot artifact: run `36286602193`, job `108528440448`, artifact `10920384270`, ZIP SHA-256 `9cb5a5f9c1ea442f00b278d3c19486b076a975fd90a341b0de8480e895f3c38a`.

All 3070 original exported source files were checked against their inventory size, SHA-256 and Git blob identities. The local snapshots are not Git checkouts. All native/package source bytes remain unchanged by this continuation. The artifact and its failed-run evidence remain intact.

## Findings and changes

| Finding | Observed issue | Prepared correction | Verification / remaining boundary |
| --- | --- | --- | --- |
| R02-C01 | All three `dotnet run` commands exited zero and printed successful assertion records but had `processGroupClean=false` | Separate build and `dotnet exec`; disable compiler/build-server reuse per invocation; bind exact host marker and assertion count; retain strict cleanup failure | New orchestration/negative tests pass. A real .NET rerun of the repair is still required. The old receipt did not record survivor executables, so build-server identity is a diagnosis to confirm, not an authenticated historical observation |
| R02-C02 | A failed later build could leave source dirty while downstream cells still depended only on an earlier successful graph | Exact source/remote preflight before every workspace-dependent cell; invalid state blocks consumers without suppressing independent valid cells | New preflight tests cover both clean execution and dirty-source blocking |
| R02-C03 | A recovery exception could obscure a build failure, and restoration lacked a complete before/after disposition | Separate build/recovery records; capture whole bounded change set; refuse unknown/concurrent changes; retain original bytes and exact restoration results | Positive, negative, missing-file, linked-file, concurrent-change and dual-error tests pass |
| R02-C04 | Cleanup failure lacked survivor diagnostics | Record only owned process-group PID/state/executable names before cleanup; omit other processes and command arguments | Real POSIX child-survivor test fails the command despite parent exit zero and Passed output; census-unavailable path never relaxes cleanup |
| R02-C05 | D2 attribution could conflate new cache storage with the retained profile-2 codec arrays | Compile a standalone production-header constructor-allocation probe on both host compilers | Both host measurements pass. This is bounded native allocation-request attribution, not Unity RSS or complete historical-cause proof |
| R02-C06 | Published demo pins and live handoff still identify H1, despite R02 source changes | Define and implement two-phase candidate/control metadata generation, exact source/ref verification and post-publication prompt generation | Metadata/negative tests pass. Actual source/control commits and final CI require unavailable publication transport |

No production correctness guard, case expectation, provenance check, process cleanup requirement or historical verdict was relaxed. No native cache implementation changes were made in this continuation.

## Source review

The reviewed native implementation retains complete physical-type/generation keys, immutable acquire/release publication, single slow construction under the metadata lock, dependency propagation, rejection of incomplete reusable proofs, mutable baseline/failure checks outside reusable permission, and distinct absent-baseline cache entries. The observation cache only memoizes registered physical classes; detailed inventory truncation remains visible. Counter coverage is explicitly bounded and level zero is unavailable, not a zero-cost success.

The Local runner keeps the R02 functional sidecar outside unchanged formal R00 timing. It binds source/build/launch/raw identity, uses a frozen balanced paired schedule, separates candidate/control source graphs and native runtimes, retains failed attempts, and seals actual input and launch/raw bytes. The repaired cell preflights and recovery records close orchestration gaps without treating an earlier PASS as authority for changed workspaces.

This inspection and host testing do not prove actual Unity type materialization, IL2CPP compilation, platform memory behavior, all possible races or production input coverage. Those remain explicit Local/independent-review work, not hidden source changes for Local to invent.

## Tests actually completed in this continuation

- R02 Python unit tests: **115 Passed**, no failures/errors/skips in the final recorded run. Includes real process exit/timeout/surviving-child cases, file binding/archive integrity and mocked build/metadata orchestration.
- Focused native production-header run: **20/20 process cases**, Clang C++17, diagnostic levels 0/1/2 and ASan/UBSan configuration.
- Native revision matrix: **70/70 process cases**, GCC and Clang, C++11/C++17, diagnostic levels 0/1/2 plus sanitizer configurations.
- Codec storage probe: two successful host compiler builds/runs, each observing four allocation requests totaling **29,884,384 bytes** (about **28.50 MiB**) plus a 120-byte codec object on this 64-bit host ABI. Allocator overhead and Unity RSS are excluded. This unchanged component is shared by H1-runtime control and R02 candidate.
- Original source artifact: **3070/3070** file size/SHA-256/Git-blob checks.
- Final R02 Python syntax and prepared-file whitespace checks are recorded with the delivery evidence.

A broader initial native attempt was interrupted by the tool's wall-clock limit. Its completed command receipts are retained, but no aggregate PASS is invented. The subsequent complete focused and revision runs above are separate evidence.

## Historical CI versus current checks

The original failed CI run passed its 70/70 native and 70/70 revision process cases and original R02 Python tests. Baseline/P01/P03 managed programs printed 102/111/111 successful host assertions, but the strict command outcomes were Failed because of cleanup. These historical results are not reclassified as a successful repaired build.

The current environment has no .NET SDK, Unity or IL2CPP platform toolchain. A real new managed build/exec run, complete current-source Primary CI, Unity/Player builds, the controlled 88-process series and affected Player matrices were **NotRun here**. The original .NET output does not close validation of the command repair.

## Remaining operational blocker

The available GitHub operation set has reads/artifact downloads but no commit/file-update/branch-write action. Plugin discovery found the existing installed GitHub connection, not another usable write capability. Direct Git transport also failed to resolve `github.com`. Although repository metadata reports push permission, no usable write transport is available in this session.

Consequently there is no new pushed source anchor, matched control HEAD, final source-target JSON or remotely verified final handoff for this repair. `PUBLICATION_PLAN.md` and `prepare_metadata.py` define the complete mechanical sequence, owned by Primary. This is not delegated production implementation for Local.

## Exit boundary

H1 remains closed with its explicit deferred risks. R02 remains unaccepted and R03 is not authorized. Finish Primary publication and a passing current CI run before issuing the generated pinned Local Validation prompt. Then Local executes the prepared batch, returns factual evidence, and obtains a genuinely independent R02 stage review. D1/D2 measured disposition must remain visible before H2.
