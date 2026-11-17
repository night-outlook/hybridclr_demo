# R03 B2 — Actual standalone codec batch-publication test: source/implementation review

**Date:** 2026-11-17 UTC. **Scope:** one additive, host-only test of the *actual* pinned `hybridclr/metadata/InterpreterMetadataIndexCodec.h`; no Unity, no native Runtime adapter, no admission of Local Validation, no R03 acceptance. Branch: `codex/assembly-shadow-r01b-h1` in all four repos.

**Tested code commit:** `night-outlook/hybridclr_demo@c923181db93719da7181cd80a23aa16b2ff2de40`. **Exact upstream header:** `night-outlook/hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr/metadata/InterpreterMetadataIndexCodec.h` Git blob `2020d4e2da6dea8601525203e7ab307d21c40a73`. Other unchanged pins: `night-outlook/il2cpp_plus@cecf4b859d50b128e5c0fc6c90cd89e3a452b96a`, `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`.

## Evidence target and implementation

The prior [publication point-of-no-return review](B2_PUBLICATION_FAILURE_BOUNDARY_REVIEW_2026-11-17.md) established the **lexical** order of codec validation, `Lifecycle::Published` release stores, Runtime publication-group activation and native active-snapshot release store. The current checkpoint advances only the **codec** part from a source-shaped synthetic model to a compiled/ran real standalone implementation.

`Tools/AssemblyShadow/R03IR/TypeDefCensus/ActualCodecPublishBatchHost.cpp` includes the **actual pinned** `InterpreterMetadataIndexCodec.h` rather than reproducing its implementation. It allocates a real codec, reserves four image IDs, encodes tokens under their private owners, finalizes the first two, then checks ten ordered scenarios: invalid arguments; unfinalized later member; mismatched later owner; duplicate reservation; aborted later member; valid two-image publication; failure to abort published images; failure to publish twice; mixture of published and private images; constructor-allocation failure. Negative batch results are checked against `Decode(token, caller=0)` to ensure an earlier valid entry **remained private**. After successful publication, unrestricted `Decode` succeeds; `Abort` and repeated `PublishBatch` reject the already published records. Caller identity, reservation counters and mapped-page counts are observed without a VM.

`.github/workflows/r03-b2-actual-codec-batch-host.yml` checks out a detached sparse **exact** `hybridclr` commit, verifies both `git rev-parse HEAD:...` and `git hash-object` against the reviewed blob, and compiles/runs C++11/C++17 strict (`-Wall -Wextra -Werror -pedantic`) and ASan/UBSan source-host profiles on macOS-15/Ubuntu-24.04. Each run emits bounded JSON with **all runtime/Unity/exception/rollback/acceptance flags false**. No actual native or Unity binaries are changed.

## Test results and evidence custody

- Initial code/CI run [44116674550](https://github.com/night-outlook/hybridclr_demo/actions/runs/44116674550) **failed in the CI assertion** for two Ubuntu jobs because it required `checks >= 48` while the actual standalone executable reports **43 checks**. It had already compiled and completed the host process; this was a **test threshold mistake**, not an observed codec defect. Never classify that initial run as passing.
- Corrected test-only workflow `hybridclr_demo@c923181db93719da7181cd80a23aa16b2ff2de40`, [GitHub Actions run 44116950061](https://github.com/night-outlook/hybridclr_demo/actions/runs/44116950061): **Ubuntu C++11 and C++17 each completed successfully**, strict and sanitized tests, **10 actual-codec scenarios / 43 assertions per execution**. Raw JSON was captured in each job log. **macOS C++11/C++17 were queued at the time of this publication**. Do not claim complete 4/4 evidence without independently reading all four job conclusions.
- This exact-code host evidence is **not** Local Validation, which remains `CLOSED_NO_LOCAL_EXECUTION`.

## Review findings and next boundary

**CODEC-01 — PASS in actual standalone codec / normal-return scope.** `PublishBatch` rejects invalid later members before publishing an earlier valid image. Positive publication and subsequent `Abort` / duplicate-publish rejection are exercised by the pinned implementation and native `Codec::Decode` semantics.

**CODEC-02 — OPEN / HIGH.** `InterpreterMetadataIndexRuntime::PublishBatch` owns separate `reservationMutex`, publication-group records and public-group activation. Its calls and state are **not exercised by this standalone header test**. A lifecycle-published codec image does **not** itself prove public runtime group visibility, active `AssemblyShadow` mapping, atomic class/GC epoch or a coherent closure during concurrent readers.

**CODEC-03 — OPEN / HIGH.** The test observes only defined normal returns. No exception is injected into the real codec after its first lifecycle store, and the test does not establish exception freedom of mutex acquisition, transitive callbacks, or the native manual `UsageLock` held across callbacks. A real unknown outcome after codec attempt must remain terminal/restart-required absent independently proven rollback, per the prior [policy review](B2_PUBLICATION_FAILURE_BOUNDARY_REVIEW_2026-11-17.md). An RAII lease by itself does not restore transaction integrity.

**CODEC-04 — OPEN.** No Unity 2022.3 native TU, Player, 32-bit ABI, real metadata/GC/class provenance, lock hold-time, memory profiling, V1 terminal fields 14/15, native V2 receipt/readback/first recovery or product acceptance was run. There is no capacity or storage-candidate decision. The inactive B2 native **combined 128 TypeDefs, 64-byte declaration fields and 65,536 owner lookups** are unchanged. The exact 64-native/eight-demo source manifest, V1/B1/R02 and active resolver remain untouched.

**Disposition:** `PassedActualStandaloneCodecNormalReturnsOnly` for successful exact-code Ubuntu host jobs, **cross-platform CI pending**. This is not native Runtime/Player acceptance. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or self-approved Human Review Gate.
