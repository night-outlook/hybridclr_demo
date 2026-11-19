# R03 B2 D3 — request for independent review (NOT YET COMPLETED)

**Requested decision:** `PassD3ForD4`, `ReturnRequired` or `Blocked`. **Do not issue an independent decision from the Primary self-review.** Scope is D3: actual HybridCLR Runtime/Codec publication-phase witness, native false-return terminal policy, and proof limits. Do not begin D4, D5, H2, M08A, X02, SNAP-01, Local Validation or a Human Review Gate.

## Exact source and review entry points

Branch `codex/assembly-shadow-r01b-h1` across the four repositories:

- `night-outlook/hybridclr_demo@430a9f9f81d504ae1bc37c62963e49a6d056ea6b` — D3 test/workflow code; docs-only HEAD to be verified separately
- `night-outlook/hybridclr@c3c232023724cbad565b85e9b2c3beea8ce2789a` — real publication Runtime observer and forwarding signatures
- `night-outlook/hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de` — unchanged
- `night-outlook/il2cpp_plus@e31d73968e1895e46c0d790132f1b10b23f78842` — native observer callbacks, D1 receipt, normal-false classifier

Start with [D3 Primary implementation/source/evidence review](D3_RUNTIME_PHASE_BRIDGE_IMPLEMENTATION_PRIMARY_REVIEW_2026-11-19.md), the [D2 independent pass](D2_INDEPENDENT_REVIEW_2026-11-18.md), and [Approach A](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md). Independently inspect these **actual source files**, not solely summaries:

- hybridclr: `hybridclr/metadata/InterpreterMetadataIndexRuntime.h/.cpp`, `InterpreterMetadataIndexCodec.h`, `InterpreterImage.h/.cpp`, `Assembly.h`, `StagedAssembly.cpp`.
- il2cpp_plus: `libil2cpp/vm/AssemblyShadow.cpp`, `AssemblyShadowPublicationPhaseReceipt.h`, `AssemblyShadowPublicationD3Decision.h`; use the D2 native Assembly.cpp/MetadataCache.cpp for physical/CLI rollback context.
- hybridclr_demo: `Tools/AssemblyShadow/R03IR/TypeDefCensus/extract_d3_runtime_bridge.py`, `test_extract_d3_runtime_bridge.py`, `D3RuntimeBridgeHost.cpp`, `D3FailureDecisionHost.cpp`, and `.github/workflows/r03-b2-d3-runtime-bridge-host.yml`.

[**Exact tested CI 44487046888**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487046888) = verified **4/4 completed success**, macOS 15/Ubuntu 24.04 × C++11/17, 15 Python mutation tests/job, 14 actual Runtime/Codec + exact-native callback host scenarios/job (220 checks), and 18 native decision-header host scenarios/job (63 checks). Total: **128 passing host receipts / 1,132 checks**; actual two intermediate publisher method bodies are compiled in the host. Explicitly distinguish test VM/staging mocks, no-exceptions *decision-only* compilation, and the real native Player not executed. Failed prior CI runs retain their failure disposition.

## Reviewer questions

1. **Real timing and phase integrity.** Is P3/CodecAttempted recorded immediately before the actual irreversible `codec.PublishBatch` call? Is P4/RuntimeGroupPublished emitted *only after* the real `groups[group].active` release-store? Does the callback survive all four forwarding layers without bypass?
2. **No rollback fiction.** Does any normal false-return after P3, including a real Codec validation error or a callback refusal after a published group, incorrectly reset `Validated`, permit Abort/retry, hide terminal state, or claim Codec rollback? Check the public VM read gates.
3. **Precodec refusal proof.** Is the sole retryable UsedClosureMember denial genuinely before **any** registry appends or Codec entry, with UsageLock returned by the D2 scoped guard? Can a stale `publication.used`, forged proof or failed phase transition escape terminal?
4. **Exceptional and concurrency edges.** Review D2 RAII compatibility, callback exception/noexcept contract, Runtime mutex/Codec mutex order, lifetime of the stack receipt and observer, C++11 vs 17, and target-dependent atomic lock-free assumptions. Identify any new lock inversion, allocation in a sensitive path or unguarded bypass.
5. **Terminal and first-error fidelity.** Does a normal false preserve previous FirstErrorV2 and set `s_unexpectedFailure` to gate business execution even when `s_active=null`? Is managed/native public ABI preserved? Note source/host vs Player/V2 reporting gaps.
6. **D3/D4 boundary.** Confirm that D3's success receipt currently reaches P4 but D4 must finish process-owned ActiveSnapshot, P5/P6 and postactive fault cleanup; no D3 claim should approve lifetime, full-VM epoch, real Unity Player, native V2 first recovery or release.
7. **Test independence.** Authenticate actual two-repository pins, extracted definitions, mutation tests, real Codec/Runtime compilation, synthetic exception/observer rejection injection and separate decision-host -fno-exceptions coverage. Do not promote CI pass to native product acceptance.

**Policy choice requiring explicit reviewer attention:** D3 intentionally treats *every normal false result except a proven P0 used-closure denial as terminal*, even if Runtime validation rejected before Codec. This is conservative and safe, but can change recovery ergonomics; assess correctness and compatibility before giving PassD3ForD4.

**Current authority:** `D3Implementation=PrimaryComplete`; `D3IndependentReview=Pending`; `D4=NotStarted`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. D1 interim waived, D2 independent PassD2ForD3. No local Unity/IL2CPP build/test authorized by this packet.
