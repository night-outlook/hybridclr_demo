# R03 B2 D3 — Actual Runtime/Codec phase bridge, fail-closed native classification

**Primary Implementation source and evidence review — complete within D3; independent D3 review PENDING.** Date: 2026-11-19 UTC. Branch: `codex/assembly-shadow-r01b-h1`. This record does NOT approve D4, real Unity/IL2CPP/Player acceptance, Local Validation, R03 or any Human Review Gate.

## 1. Prior decision and exact production pins

The independent [D2 review](D2_INDEPENDENT_REVIEW_2026-11-18.md) issued **PassD2ForD3**. D1 interim independent review was separately `WaivedByUser`, not Passed. The previously selected Approach A requires a real pre-Codec attempt boundary, a real Runtime-group publication boundary, conservative classification of false-return outcomes, and no rollback claim after Codec mutation.

All four repositories use the feature branch `codex/assembly-shadow-r01b-h1`:

| Repository | D3 reviewed source commit | Role |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `430a9f9f81d504ae1bc37c62963e49a6d056ea6b` | Exact-source D3 workflow/tests; later metadata-only docs HEAD separately checked |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Production Runtime observer and forwarding |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | Unchanged |
| night-outlook/il2cpp_plus | `e31d73968e1895e46c0d790132f1b10b23f78842` | Production D1 receipt wiring and fail-closed native decision |

Changes relative to independent-D2 source:
- hybridclr: six files — `InterpreterMetadataIndexRuntime.h/.cpp`, `InterpreterImage.h/.cpp`, `Assembly.h`, `StagedAssembly.cpp`.
- il2cpp_plus: two files — `libil2cpp/vm/AssemblyShadow.cpp`, new `AssemblyShadowPublicationD3Decision.h`.
- hybridclr_demo: five test-only files — `extract_d3_runtime_bridge.py`, `test_extract_d3_runtime_bridge.py`, `D3RuntimeBridgeHost.cpp`, `D3FailureDecisionHost.cpp`, `.github/workflows/r03-b2-d3-runtime-bridge-host.yml`.
- No Unity package, source/registration roster, feature flag, B2 cap, V1/B1/R02 source or HybridCLR Unity repository modification. Inactive B2 remains at 128 combined TypeDefs, 64-byte names and 65,536 indexed owner lookups. PureInterpreter remains disabled.

## 2. D3 behavior / exact call chain

`AssemblyShadow::CommitTransaction` constructs a **fresh stack-owned D1 `PublicationPhaseReceipt` for this attempt**, before publication. A synchronous borrowed `PublicationObserver` propagates through:

`AssemblyShadow::PublishActive` → `hybridclr::metadata::Assembly::PublishStagedImagesBatch` → `InterpreterImage::RegisterImagesBatch` → `InterpreterMetadataIndexRuntime::PublishBatch` → **real `Codec::PublishBatch`**.

The observer is a three-field POD (two `bool(*)(void*)` callbacks and context) with no allocation or ownership transfer. Ordinary `Publish` / `PublishBatch` calls that do not supply an observer preserve their previous signatures through default null arguments. The two supplied native callbacks are `noexcept`, use only the existing atomic D1 receipt, and do not take a VM/transaction/metadata lock or invoke managed code.

Observed transitions:
1. **P0 Prepared** — new per-attempt receipt, no shared mutation.
2. **P1 UsageAdmitted** — after `TryBeginPublication` acquires the lease and verifies the closure was not used; denial before this point leaves P0.
3. **P2 RegistriesAppended** — `PublishActive` is reached synchronously only after D2 physical and CLI append loops complete under their locks; receipt advances before the staged publisher.
4. **P3 CodecAttempted** — `Runtime::PublishBatch` calls `observer->beforeCodec` **after Runtime input prechecks and immediately before the actual `codec.PublishBatch`**. This is deliberately an *attempt*, not a claim that any Codec lifecycle has transitioned.
5. **P4 RuntimeGroupPublished** — after real Runtime stores every group membership, release-stores `groups[group].active=1` and increments its group counter, it invokes `observer->afterRuntimeGroup`. Any false result is returned as a failed Runtime publication even though the actual Codec/group may now be published. The native caller MUST seal terminal state.

D3 does **not** mark P5/P6, complete the receipt, persist a success receipt or change ActiveSnapshot ownership. D4 still owns the snapshot lifetime and the post-active phases.

## 3. Normal failure policy, actual native code

The new pure C++11 `ClassifyFailedNativeBatch` helper is included by the real `CommitTransaction` and directly compiled in the D3 native decision host. A failed publication may return to `Validated` **only** if:
- the native `UsedClosureMember` denied the closure *before either registry append*;
- the receipt is still P0/Prepared + InProgress;
- the UsageLock lease has been released and `runtimePublicationFailed` is false;
- `RejectBeforeCodec` accepts the complete source-derivable no-mutation proof.

All other normal false returns become **TerminalRestartRequired**, even when Runtime rejects before the actual Codec call. This is an intentional conservative semantic choice: it avoids inferring cleanup proof from a boolean alone. If P3 or later was reached, reason is `CodecOutcomeUnknown`; otherwise `MissingCleanupProof`. The native caller freezes the existing FirstErrorV2 (without overwriting an earlier event), sets the durable `s_unexpectedFailure`, changes state to Failed/FailedAfterCommit depending on actual active snapshot visibility, and returns InternalError through existing Result logic. There is **no Codec rollback** or second attempt within the current process.

The existing D2 `ScopedUnexpectedPublicationExit` continues to handle C++ exceptional unwind separately; the D2 physical/CLI guard/UsageLock custody order is unchanged. Terminal business method rejection uses the existing durable failure gate. No new enum value or managed-visible ABI was introduced. D3 does not assert no-throw execution for arbitrary native allocations or real target mutexes.

## 4. Actual tests, raw CI evidence, and limitations

[**Final enhanced D3 GitHub Actions 44487046888**](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487046888) at exact demo test commit `430a9f9f81d504ae1bc37c62963e49a6d056ea6b`: **4/4 completed success**, macOS 15/Ubuntu 24.04 × C++11/C++17. All four job logs read back and their JSON host receipts independently counted.

Per job:
- **15/15 Python source/mutation tests** against exact pinned Git commits and 11 native/HybriCLR function bodies extracted with body-hash receipts; no skipped/error tests.
- **14 host executions / 220 assertions**: strict + ASan/UBSan across seven scenarios. This links the *actual* HybridCLR `InterpreterMetadataIndexRuntime.cpp` and *actual* `InterpreterMetadataIndexCodec.h`, exact extracted native UsageLock/phase callback bodies and the two *actual* intermediate staged/image forwarding definitions. Scenarios include P0 used-denial, Runtime precheck rejection, real Codec validation error, successful Runtime group, group already published when a synthetic callback rejects, attempted Codec disguised as used-denial, and malformed observer. Runtime group visibility remains mediated by a **test-owned mock VM bridge**.
- **18 host executions / 63 assertions**: the actual native `AssemblyShadowPublicationD3Decision.h` plus D1 receipt compiled and run under strict, ASan/UBSan and `-fno-exceptions -fno-rtti` (six cases per profile).
- Thus **32 host receipts / 283 checks per job**, **128 host receipts / 1,132 checks across 4 jobs**, plus 60 source mutation tests. No native-host assertion or sanitizer failure found. The full Runtime.cpp was **not** compiled with no-exceptions; that profile only covers the no-throw classifier/receipt header.

Earlier runs remain recorded with their historical outcomes:
- [44486080330](https://github.com/night-outlook/hybridclr_demo/actions/runs/44486080330), [44486331190](https://github.com/night-outlook/hybridclr_demo/actions/runs/44486331190), [44486337701](https://github.com/night-outlook/hybridclr_demo/actions/runs/44486337701): FAIL in initial source-mutation verifier/target selection, before a native host acceptance claim.
- [44486466404](https://github.com/night-outlook/hybridclr_demo/actions/runs/44486466404): PASS 4/4 in earlier narrower test that source-verified but did not compile the two actual intermediary wrappers.
- [44486952917](https://github.com/night-outlook/hybridclr_demo/actions/runs/44486952917), [44487004192](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487004192), [44487040320](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487040320): FAIL in intermediate enhanced-test versions before the corrected final run.
- [44487046888](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487046888): final PASS; earlier failures are not reclassified as passes.

Host limitations: test-owned VM/StagedAssembly classes, fake real-VM-public-visibility predicate, no real native Unity/baselib mutex, no full native TUs/Player, no real allocator/GC/class epoch, platform 32-bit ABI or shutdown. The post-group observer failure is an intentionally synthesized callback failure **after an actual real Runtime/Codec group store**. It proves the source-host failure semantics only. Physical/CLI RAII guards are independently covered by D2 source-host evidence, not recompiled end-to-end with this Runtime host. The real FirstErrorV2 class and full managed V2 reporting were source-checked, not re-linked into this new host.

## 5. Primary review findings / next gate

| ID | Disposition | Scope |
| --- | --- | --- |
| PI-D3-01 | PASS / source+host | Actual CodecAttempted occurs before the actual Codec call; actual RuntimeGroupPublished occurs after its group release-store |
| PI-D3-02 | PASS / source+host | Observer passes through the two exact intermediate wrappers to native publication |
| PI-D3-03 | PASS / source+host | Used-denial P0 permits Validated; unknown post-P3 failures and incomplete precodec proof are terminal |
| PI-D3-04 | PASS / source+host | A returned error after a real group store does **not** prove rollback, and the classifier never grants retry |
| PI-D3-05 | OPEN / CRITICAL D4 | ActiveSnapshot raw pointer is release-stored before `unique_ptr` relinquishes ownership; lifetime and P5/P6 receipts remain unfinished |
| PI-D3-06 | OPEN / HIGH | Complete Unity/IL2CPP Player/32-bit ABI, real exception/native mutex, GC/metadata epochs and V1 fields 14/15 plus V2/first-recovery remain NotRun |
| PI-D3-07 | REVIEW REQUIRED | Independent D3 review must evaluate the intended conservative policy (all non-used-denial false returns terminal), callback contract and source-host proof limits |

**Primary disposition:** D3 implementation and reviewed host evidence are complete within this environment, but **D3IndependentReview=Pending**. **Stop here** for an independent D3 review; do not automatically start D4. The independent reviewer may return PassD3ForD4, ReturnRequired or Blocked. No Local execution authority: `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. D1 was waived by user, D2 independent Passed, D4 NotStarted.
