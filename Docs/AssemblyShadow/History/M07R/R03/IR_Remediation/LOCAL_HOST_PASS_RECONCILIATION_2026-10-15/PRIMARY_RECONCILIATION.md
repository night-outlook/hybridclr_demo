# Primary reconciliation — Local host-only successor PASS (R03)

**Owner:** Primary Implementation. **Source-bound date:** 2026-10-15 UTC. **Disposition:** Host validation evidence accepted **within its explicitly limited host-only scope**. **Next owner:** Primary Implementation. **New Local assignment:** none; runtime remains PAUSED.

## 1. Authority and provenance

The published [Local factual report](../../../../../Handoff/LOCAL_VALIDATION.md), [Local return](../../../../../Handoff/RETURN_TO_WEB.md), [immutable checkpoint](../../local-validation-host-only-20261015-74dbdbea-a1/README.md), [raw result](../../local-validation-host-only-20261015-74dbdbea-a1/host/RESULT.json), [independent Local evidence audit](../../local-validation-host-only-20261015-74dbdbea-a1/preflight/EVIDENCE_AUDIT.json) and [finding revalidation](../../local-validation-host-only-20261015-74dbdbea-a1/PRIOR_FINDING_REVALIDATION.json) are the factual inputs. Local exit was 0, with run interval 2026-10-15T06:18:10.405717Z through 06:19:11.121169Z. No Unity, Player or integrated official SDK compilation occurred.

The **exact tested code tuple** on branch codex/assembly-shadow-r01b-h1:

| Repository | Execution commit |
| --- | --- |
| night-outlook/hybridclr_demo | 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | 74dbdbea80d83923863303bd2b2c0a87f36541b1 |

**Publication is not execution.** Local's final documentation commit is demo 8ac3cec286173e5e2110ee7853f648ddf50eda4e. GitHub comparison from execution demo 7b9d1d4e37d1731f9f00042eb04892a8afaf7e80 to that publication shows one additive historical/checkpoint publication commit, with only Docs/AssemblyShadow changes; no product, runner, native, package or test source changed. This new Primary reconciliation publication itself is Docs-only; its latest pushed commit must be obtained from remote HEAD, not inferred as a rerun.

## 2. Accepted scoped evidence

Local recorded **PassedHostOnly**, 8/8 outer commands Passed and 0 Failed. The native-general-stream component ran the original 25 tests per strict and sanitized profile, each with zero failures/errors/skips; its oldExecutionProducer and currentExecutionProducer both Passed, with firstFailure=null and sourceUnchanged=true.

Under the same pinned historical synthetic VM fixtures, the **actual old and current complete execution function bodies** produced 6/6 full JSON byte-equal pairs across 3 fixtures and 2 profiles. Primary separately fetched all twelve published frozen/current JSON files through the GitHub Connector and compared every full pair: 331078-byte 1024-class, 327-byte empty, and 342307-byte DEBUG/class-state/storage variants. Each pair matched exactly, and both profiles agreed on byte length and content. In the DEBUG specimen, the first class retained staticStoragePointer=0x1234, executionModeCode=1 and isActive=false. This confirms complete **mock-based byte parity**, not real VM acquisition or actual SNAP-01 diagnostic sizes. The parity producer also had 24 compiler/process receipts.

Other host suites: bounded V2 native codec 20 tests/profile, POSIX V2 transaction 27 tests/profile, earlier native sink 32 total tests, and execution serializer strict/sanitized compile+run all Passed. The Local independent audit reports 567 nested command streams verified, 3164 inventory entries including 4 intentional test symlinks, full source preservation and clean four-repository remote authority. Recorded hashes: batch RESULT ea5dd8a85d1c6d4851ac123771c5e6c2d4f6827e7bcecce7f112017e21c62f4f; batch MANIFEST 88d90ae88f27f43110dc3c313b520c100f93621fb58fde60d01e98d17504c87f.

The Local preservation check verified the **previous 2549-entry FAIL root** and **1183-file checkpoint** unchanged. The old host attempt remains FAIL/FailedOrIncomplete, with its two general profiles **NotRun**. The new PASS does not retroactively change the old result.

Primary separately verified GitHub repository identities/branch HEADs, confirmed source-versus-publication separation, inspected the Local results/audit/checkpoint and fetched/compared all twelve full original/current JSON files. **Primary did not rerun the host command or independently scan the complete external Local filesystem root**; 567 stream-hash and 3164-inventory verification are attributed to Local's recorded independent audit, not claimed as newly repeated checks here.

The source-matched finding IR-LOCAL-HOST-EXECUTION-BINDING-01 is therefore **VerifiedCorrectedWithinFreshHostScope** and may be closed for this scoped host regression only. The corrected component no longer fails on the old textual source-equality requirement.

## 3. What this PASS does not prove

- General/execution native VM capture is **not** coherent, lifetime-reviewed, allocation-bounded or safe for post-terminal serialization. Synthetic 331078-byte/342307-byte fixtures are not the three actual failing ON Player payload lengths; the real full length remains **Unavailable**.
- The inactive V2 codec/descriptor-bound file transaction is **not integrated** with the current native/C# Player emitter, authentic source/run/PID/build receipts, both complete actual diagnostic fields or every unchanged original semantic verifier predicate.
- The Unity2022.3.62f2 StandaloneOSX engine scheduler-owner safe point, callback draining, GC/finalizer/services and restart disposition are **unproven**. A modeled coordinator is not an engine adapter.
- The official new managed/55-native SDK build, actual Unity Player runtime, full historical C/S custody, hardware power-loss durability and broader regression are **NotRun/NoCoverage** in this Local host cycle. macOS LeakSanitizer is Unavailable; Linux Clang/GCC were CI, not Local.
- Real historical SNAP-01 remains **FAIL/ReturnRequired**: 18 cells (14 Passed/4 Failed), three ON output files zero bytes / exit2 because original V1 finalDiagnostics slot14 exceeded 262144 (first scanned prefix262145, exact producer size unavailable); engine produced **51213 uncapped reports / 500ms, exit71**. Strict original S custody remains **Blocked** (416844 expected,339367 verified survivors,77477 missing and four original native roots absent). N/M/K/I/E remain FAIL; independent full-stage R03 review remains FAIL / re-review NotRun.

Transport limits and acceptance predicates are unchanged: V1 per-text slot262144 bytes; V2 frame65536, artifact3932160, envelope262144 and combined encoded4194304; authentic full output required, no truncation; uncapped native engine 1–64 reports over the original 500ms with logger1→1 and all original guard/GC/recovery predicates. No report cap, coalescing, sleep, benign dispatch default, finalizer suppression, arbitrary managed allowlist or early exit may simulate success.

## 4. Primary-owned remaining work and sequencing

| Gate | Current status | Required next Primary evidence |
| --- | --- | --- |
| P1 coherent bounded general + execution capture | **Incomplete** | Review VM/transaction/metadata lock order and object lifetime, preprepare bounded native storage, capture complete slot14+15 without terminal managed string marshalling, compare original JSON bytes and measure capture/GC/RSS envelopes on source-bound tests |
| P2 V2 Player and semantic integration | **NotIntegrated** | Actual native/C# producer, descriptor-pinned complete artifact+envelope, independently authenticated identity and V2 readback into **all unchanged original semantic predicates**, preserving V1 historical verification and fail-closed negative cases |
| E0 engine-owner capability | **Blocked/Unavailable** | Vendor or pinned engine-source-supported Unity2022.3.62f2 StandaloneOSX owner thread/safe-point, drain, GC/finalizer/service and restart contract; public PlayerLoop/native-plugin callbacks do not prove ownership |
| E1 real native adapter/supervisor | **BlockedByE0** | Implement only against proven safe-point/maintenance contract, preserve original uncapped 500ms/1–64 witness and full teardown/restart receipts |
| P3 integration and next Local runtime preparation | **NotRun** | Source-bound official managed and 55-native compiler matrix, terminal path independent review, fresh exact four-commit pins, unused roots and explicit new runtime authorization |

**Earliest actionable Primary task:** P1 source/lifetime and allocation census, followed by a source-bound frozen-capture design and focused implementation/tests. P2 may proceed only when P1 contracts are resolved. E0 is an independent external engine-capability dependency and must not be assumed satisfied. No nontrivial development is delegated to Local until a separately authorized, fully prepared handoff.

## 5. Stop and acceptance

This host cycle is **consumed** and CLOSED within host scope. Current owner is **Primary Implementation**; the previous WEB_TO_LOCAL host-only command must no longer be treated as a pending Local task. Do not launch another Local batch on this evidence. Keep WEB_TO_LOCAL **PAUSED / no active Local assignment**, and do not designate new Player roots.

R03Accepted=false, H2Passed=false, qualificationApproved=false, ReadyForHumanReviewGate=false, fullLegacyRegressionAcceptance=false. PureInterpreter expansion remains disabled. No H2/X02/M08A, no automatic Human Review Gate and no full legacy regression acceptance.
