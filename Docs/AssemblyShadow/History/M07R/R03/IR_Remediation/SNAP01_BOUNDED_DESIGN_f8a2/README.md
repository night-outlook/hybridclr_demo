# SNAP-01 reconciliation: bounded lossless diagnostics and native terminal ownership

**Current owner: Primary Implementation. Delivery: design plus executable reference contracts. Production integration is pending; no new Local runtime execution is authorized.** SNAP-01 remains FAIL, collectionResult=EvidenceCollected and semanticBatchResult=ReturnRequired.

## Read order

1. [Lossless diagnostic design](LOSSLESS_DIAGNOSTICS_DESIGN.md): exact bytes, explicit V2 transport, 65536-byte frames, unchanged262144-byte physical text limit, 4194304-byte pooled encoded allowance, complete hashes and strict semantic integration requirements.
2. [Native engine terminal/restart design](ENGINE_TERMINAL_DESIGN.md): real scheduler ownership, safe-point acknowledgement, maintained native services, complete500ms uncapped report observation and separately authenticated restart. The concrete StandaloneOSX adapter remains unestablished.
3. [Primary implementation plan](IMPLEMENTATION_PLAN.md): native shared producer/capture/sink, safe durable file transaction and unchanged semantic predicates; supported engine-owner integration; full source/SDK review before a separately authorized Local cycle.
4. [Evidence audit](EVIDENCE.json) and the [reference check runner](reference/run_checks.py).
5. Original Local-owned [LOCAL_VALIDATION](../../../../../Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../../../../../Handoff/RETURN_TO_WEB.md) and the [SNAP-01 checkpoint](../../local-validation-snap01-82bd/README.md), which are not modified by this delivery.

## Actual finding reconciled

SNAP-01's three ON processes recorded first writer rejection at **slot14 finalDiagnostics**, reason9, original limit262144, scanned prefix262145, errno0. Exact full lengths and full ON semantic data remain Unavailable. The previous synthetic331078-byte slot15 example is neither SNAP-01's payload nor its first failure. Engine recorded **51213 actual uncapped reports in500ms**, exit71, with no dominant-method frequency proven by sampling. The original18 cells remain14 Passed/4 Failed, despite three builds, OFF, all Bee observations, preservation and bounded seal passing within their scopes.

## Work completed

Five new reference sources are isolated under this documentation directory: a versioned exact-byte codec/strict decoder, its36 Python tests, a native terminal-owner coordinator contract, its21 scenarios and a source-preserving test runner. None is included in production Player compilation, the original snapshot emitter, Runtime::Invoke, the scheduler or the existing semantic verifier.

The transport reference authenticates all ordered chunks and complete fields, EOF/footer, run/PID/request/build/source identity and envelope hash before returning a tagged V2 semantic view. It rejects missing/corrupt/reordered/trailing data and aggregate overflow; it never substitutes a hash for missing content or turns Failed into Passed. It is a host model, not proof of bounded native heap usage or safe runtime filesystem operations.

The coordinator models one immutable first cause, verified native owner/generation/epoch, zero in-flight managed work, continued maintenance, no late dispatch, durable evidence and the full500ms window. It preserves actual counters:65 and51213 fail. It does not control Unity, disable finalizers, suppress reporting, sleep callbacks, fabricate benign returns, terminate a process or perform a restart.

## Executed tests and audited CI

[CI38435030795](https://github.com/night-outlook/hybridclr_demo/actions/runs/38435030795), source commit **1ae589ce5bc38441ff1c90eb8f632304343f7a3f**, passed on macOS14 and Ubuntu24.04. Each platform ran36 Python tests and21 native scenarios in each strict C++17 and ASan/UBSan profile; five compiler/process records per platform. Both original ZIP digests, exact15-file inventories, all13 declared manifest members, five command stdout/stderr hashes and all five source hashes were independently authenticated. Current-container execution passed the same reference checks with unchanged sources. Complete artifact identities and limitations are recorded in EVIDENCE.json. ZIPs are retention-limited; retained audit data is not a claim that original binary/log archives are permanently stored in Git.

No new official product SDK compilation, native producer integration, real scheduler adapter, GC/finalizer lifecycle, restart or Local live-custody/Player execution was performed. The original production files and source pins remain unchanged.

## Remaining gates and pause

The native complete serializer/capture/sink, secure preopened file transaction, versioned semantic dispatch and concrete supported Unity2022.3.62f2 StandaloneOSX scheduler/lifecycle adapter must be implemented and reviewed by Primary. Model acknowledgements are not engine evidence. A valid full diagnostic stream may still exceed the finite pooled allowance; that must fail rather than change limits. No repeated known-failing runtime experiment is assigned to Local while these are unresolved.

The canonical [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) is paused after consumed SNAP-01. Future Local admission requires a new separately published full four-SHA tuple, fresh roots, original host/compiler/custody/storage/SDK/fixture gates and unchanged ON/OFF/report predicates. No SNAP-01/N retry, new acceptance, H2/X02/M08A or PureInterpreter expansion. All acceptance flags remain false; strict historical S custody remains Blocked; independent full-stage R03 review FAIL/re-review NotRun.
