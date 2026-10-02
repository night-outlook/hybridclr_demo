# R03 G — allocation attribution and staged physical-layout readiness

Primary Implementation source review and handoff completion, 2026-10-02 UTC. This is not independent stage review, Local runtime acceptance, or a Human Review Gate.

## Received evidence and recovered source authority

Local publication `b97375d4b12357d0f987cf7738eaa422d4615081` records one batch E executed from demo `d51483dc1a11007fe1db2ee456a8b0444061389c`. Its result remains **ReturnRequired: 32 Passed / 4 Failed / 0 Blocked**, focused seal Passed. Four native build cells and 754 selected Editor cases passed. All nineteen fresh-process Players ran: fifteen Passed and four Failed. The excluded frozen-M01 resource test remains NoCoverage.

Read the unchanged `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and `History/M07R/R03/local-validation-20261001-batch-e-return-required/` under `Docs/AssemblyShadow`. The original 1,867 indexed files / 1,868 archive members and 3,081 prior custody bindings are Local's authenticated evidence, not a claim that Primary accessed the retained macOS live root.

E's result/index/archive SHA-256 values remain:
- `e57b15223de02b566c0e4157a6157487e0ed208b20700356e8378dab1d4bf95f`
- `7bce6d321265f0c4fa4c0d1b1946e25d523e3c5351d6e4ac0310cc5a57d041a4`
- `e8bb7e85a6b3e030de30c800c1f8b18dff5d0ac7a80332d6b00c1b612de94c36`

The continuation discovered already-pushed repair descendants instead of assuming the Local tuple was still remote HEAD. It compared and reviewed those commits rather than overwriting them. The recovered, tested source tuple is:

| Repository | Tested implementation revision |
| --- | --- |
| night-outlook/hybridclr_demo | `67e8c1df18f84dda4ec70edd45b1ed717bcea4e8` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` — unchanged |
| night-outlook/il2cpp_plus | `aae0ebb55b8761a7a905b410349d006d76fa748b` |

All use `codex/assembly-shadow-r01b-h1`. Demo was three source/tooling commits beyond the E publication; each native repository was one commit beyond E's executed native pin. This finalization adds documentation only after the tested demo anchor. Earlier source anchors do not authorize the next run.

## R03-LE-001: distinguish exact allocation work from observer work

E's C03/C04/C05 Release witnesses each gained one global admission miss/proof/entry and 80 retained bytes between two returned managed JSON observations, while completing 10,000 hits/baseline checks. Debug D02/D03 did not gain that extra proof. No repeated field/interface/layout work was observed. The existing counters include all classes and threads, and the native snapshot precedes construction of its returned managed string. The exact extra class, call site, thread and causal boundary **remain unproven by E**. This record does not label it a String allocation, marshalling defect, race or cache invalidation.

The implemented correction makes the measurement boundary explicit rather than accepting a fixed +1 or warming until a test passes. The isolated native diagnostic uses compile-time `HYBRIDCLR_R03_RUNTIME_PROBE=1`; the header defaults to 0 outside this test profile. The production allocation cache, one-time construction policy and per-allocation mutable baseline-state checks remain in place.

The bounded probe retains full admission keys (generation, physical class, context and domain), allocation sites, process-local native thread identities, cold counter events, and six ordered snapshots. Thread identities are probe identities, not asserted operating-system TIDs. Limits are 128 events, six snapshots, 32 layout rows and sixteen fields per layout row. Unknown identities, truncation, overflow, wrong owner, inconsistent boundaries, dropped counter threads and saturation fail the witness.

Boundary labels are `[0, 10, 1, 2, 11, 3]`: Begin; the first existing native GetInfo snapshot; immediately before the fixed 10,000-allocation loop; immediately after the loop; the second existing native GetInfo snapshot; and completion after its managed return. Cold-event logging and its counter increments share the snapshot lock during the active session. The existing broad snapshots remain in raw output and must agree with their corresponding native samples. No historical snapshot is rewritten.

The new explicit acceptance contract is:
1. Every consecutive native span must reconcile all six cold counter deltas exactly to retained full-key/site/thread events.
2. The exact allocation loop must have **zero** misses, proof attempts/rejections, new entries/retained bytes, unready proofs, layout checks and field/interface workspace builds; at least 10,000 certificate hits and baseline-state checks remain mandatory.
3. Cold events contributing to the original broad interval may occur only outside the exact loop and must identify a different physical class and a different logical assembly/namespace/type from the measured target. Their complete identities, sites, thread identities and broad counter deltas remain visible.

This is a deliberate observation-contract refinement, not proof that E's extra event has already been attributed. A new Local result is needed to establish the actual attribution or report another failure. A missing trace, unmatched counter delta or target proof in the protected interval cannot become a pass. The fixed preparation count and allocation count are unchanged; no retry, increasing warm-up or cache mutation was added.

## R03-LE-002: finalized staged metadata is not lazy class initialization

E's C07 ended at Validate code 16/state 8 before physical comparison, with ChangedLayoutUnavailableBeforePublication. It demonstrated a readiness failure, not incompatible offsets. C07 remains a **positive private-Int64-append case**, not a newly expected rejection.

`InterpreterImage::InitRuntimeMetadatasForStaging` clears a staging-only readiness marker, invokes the complete existing metadata initialization sequence, and marks definition layouts ready only after successful return. Partial or throwing initialization cannot publish the marker. Ordinary hot-update initialization is unchanged. `TryGetReadyDefinitionLayout` authenticates the exact image, TYPEDEF row and metadata handle; excludes generic, array and pending layouts; and checks instance/native/static/thread-static sizes against finalized type-detail tables.

The native staged screen accepts target physical readiness from either the existing completed class flag or this authenticated finalized-definition capability, with no size-initialization pending. It retains the existing baseline readiness predicate. It does not call Class::Init, allocate a baseline business object, run a business initializer, force SetupFields or set lazy class flags to manufacture proof.

When field shape or physical representation changes, the screen still runs the existing physical CheckLayout: baseline-use guard, actual instance size and offsets, unchanged retained fields, strictly appended private primitive tail storage, value-type/native representation, parent/interface and layout-kind checks. The readiness capability does not bypass that comparison and does not issue a reusable allocation certificate. The post-publication allocation proof remains separate.

Bounded prepublication rows expose both sides' readiness, pending and initialization flags, physical class identities, sizes, retained/new offsets, attributes/storage widths and proof outcome. C07 now additionally requires exactly one successful physical witness for R03Contract/R03.Node, the original one-to-two field shape, private eight-byte tail storage, and no baseline business initialization before proof or at report time. Unready or incompatible input retains the code-16 fail-closed behavior. If the intended positive case still cannot prove readiness or geometry, its next cell remains Failed; Local must not reinterpret it as an accepted rejection.

## Changed implementation and test surface

HybridCLR: `hybridclr/metadata/InterpreterImage.h` and `StagedAssembly.cpp`. The header also makes the existing GetEventInfo metadata pointer const-correct; no event behavior changes.

IL2CPP: `libil2cpp/vm/AssemblyShadowAllocationProof.h`, new `AssemblyShadowRuntimeProbe.h`, `AssemblyShadowTypeResolver.cpp`, and new `tools/r03/runtime_probe_tests.cpp` / `runtime_probe_other.cpp`.

Demo: `PlayerProject/AssemblyShadowR03Probe.cpp`, `R03Build.cs`, `R03Player.cs`; `batch_contract.py`, `runtime_contract.py`, `test_runtime_contract.py`, `test_batch_contract.py`; `native_validation.py`, `run_local.py`, `run_host_lifetime.py`, `player-cases.json`, `source-pins.json`; and the r03-primary, r03-build-api and r03-native workflows. Unqualified tooling paths are under `Tools/AssemblyShadow/R03/`.

Raw Player output advances to schema 2 with runtimeProbe evidence. Fresh requests and case identities retain their prior contract. Semantic verifier failures now produce an explicit Failed `players/<case>/verification.json` retaining raw/request/build/launch bindings; this does not alter historical absence of successful-verdict files in E. Native reference controls retain their old-core behavior; the adapter does not invent unavailable reference probe coverage.

The source review checked the real staged initializer, physical comparison, allocation-cache validation, observer placement, bounded native report, managed call sequence and strict verifier. This is Primary self-review, not independent full-stage review. No frozen M01 assets, broader runtime features or unrelated refactors were added.

## Completed validation and authenticated evidence

Source anchor `67e8c1df18f84dda4ec70edd45b1ed717bcea4e8` passed host workflow **36973943178** on Linux x86_64 and macOS 15.7.9 arm64, both using SDK 8.0.318. Each passed **144 Python contracts** (28 additional runtime-witness contracts), both 9-case graph suites, 35 admission/method contracts, fifteen fixture DLLs, 33 audits/consumers, actual managed Runtime API compilation, prior provenance/scope checks and shared-compiler success/failure supervision.

Each host also passed 24 new native header-test processes across language/diagnostic/probe profiles, including sanitizer coverage, plus the existing R02 and R02-revision suites with 60 passed processes each. These are production-header and synthetic-policy regressions, not execution of Unity's staged metadata pipeline. Each artifact has 87 fully owned command receipts (85 exit 0, two named expected-negative exit 1) with clean completion. A separate 148 legacy receipts per host were authenticated for retained streams; their schemas do not provide equivalent process-lifetime evidence.

Pinned-Unity workflow **36973943228** passed actual full-helper/package compilation and **25 native translation-unit/profile syntax compilations** using the extracted Unity 2022.3.62f2 ARM64 SDK. Profiles include candidate, Debug, probe-off, diagnostics-off and feature-off. The complete updated helper has no compiler diagnostics; 61 existing CS0649 package warnings are retained. The unchanged full C helper still yields exactly its two expected CS0266 errors. The final standalone native profile explicitly binds `BASELIB_INLINE_NAMESPACE=il2cpp_baselib`; earlier incomplete standalone-profile attempts are not final evidence.

The critical CoreModule hash remains `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`. Updated helper source SHA-256 is `84f97d772616c4d7d8203c4680bd1ee7d2826155b624a9b6eb40d45750bc4524`; emitted helper is `a8a16d5d5cb3aff57eafca0e18fcc899455cc191aeab7e7e2169e804a111f117`, 13,824 bytes. Syntax checks are not linking or Player execution.

| Evidence | Workflow / artifact | ZIP SHA-256 | Exact membership |
| --- | --- | --- | --- |
| Linux host | 36973943178 / 11213325661 | `a84560b85a5e4acb18d1f86cd95d36fb4e92e54aa74945aee9fd15669ad43094` | 1,221 indexed / 1,222 files |
| macOS host | 36973943178 / 11212379301 | `4ae84907587761f8d80f8fa5813997d6fcaac7320e00c1d04153342d9e16865d` | 1,320 indexed / 1,321 files |
| Pinned Unity API/native syntax | 36973943228 / 11213520118 | `594d63d933bb6c582d457513c9e86e4f585c6a40338587eb9bb36d766a9993db` | 109 indexed / 110 files |

Primary downloaded all three archives and checked exact safe/nonduplicate membership, every indexed size/hash, source identities, results and command streams. `G_HOST_EVIDENCE.json` records that audit. Artifacts expire 2026-10-16 in GitHub. The current container separately reran all 144 Python contracts successfully; actual .NET/Unity compiler and SDK compilation occurred in CI, not this container. No new Unity Editor or IL2CPP Player execution is claimed by Primary.

## Disposition, transport and next cycle

LE-001: bounded attribution and explicit observer/loop contract implemented and host-validated; actual class/site/thread attribution and integrated witness remain pending. LE-002: finalized staging-layout capability and positive physical witness implemented and compiler-validated; actual primitive-append publication/allocation remains pending. Neither issue is empirically closed by syntax or synthetic tests.

The four live refs were read through the GitHub Connector. This continuation writes demo documentation only, on top of the already-pushed repair tuple. A fresh disposable demo tree/commit/ref smoke passed on `codex/connector-smoke-r03-runtime-handoff-20261002-0746`, exact read-back commit `c644e89d66b14d10080f8e3b54f1e68ac907c344`. Earlier four-repository smoke records remain historical; no new native writes are claimed here. Delete-ref is unavailable in the exposed actions, so the disposable branch remains non-authoritative.

Next unused root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261002F-runtime`. The live WEB_TO_LOCAL.md and final prompt bind its exact pushed demo transport. Local runs one prepared 36-cell batch: four fresh native builds, all 754 selected Editor cases with zero skips, and all nineteen fresh-process Players, including six warm witnesses and C07's positive physical proof. No non-trivial implementation is delegated.

Rollback requires a new coherent Primary-controlled source tuple/handoff, never mixed native versions, old app reuse or rewritten E evidence. Full legacy/resource/P01–P05, broader generic/interface/delegate/stack-trace work, startup/capacity/performance/memory, gated PureInterpreter qualification and independent stage review remain open. R03Accepted=false; H2Passed=false; PureInterpreter expansion disabled; fullLegacyRegressionAcceptance=false. R02 deferred CPU and original H1 RSS risks remain visible.
