# R03 B2 D2 — Independent native-publication custody review

**Decision: PassD2ForD3.** Date: 2026-11-18 UTC. Reviewer: independent source/evidence reviewer acting separately from the Primary Implementation report. **Scope: D2 only** (native physical/CLI registry rollback, UsageLock custody, unexpected publication exit). This decision permits Primary Implementation to begin **D3 only**; it does not approve D3/D4, any Unity/IL2CPP/Player execution, R03 acceptance, H2, or the Human Review Gate.

## 1. Authority, provenance, and method

Working branch across all four repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Verified remote HEAD / source authority |
| --- | --- |
| night-outlook/hybridclr_demo | `245c808f5db16905dc427de7af0c23ab0d86c8b2` before publication of this review; tested D2 source `6362aa3469abd3baa15b97b8e5cb169f602c27d1` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `b86a97e1dcca18163df5ac2d5f268bf6de18bbdf` |

Read the [D2 independent review request](D2_NATIVE_CUSTODY_INTERIM_REVIEW_REQUEST_2026-11-18.md), [Approach A design](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md), [D2 Primary report](D2_NATIVE_PUBLICATION_CUSTODY_IMPLEMENTATION_REVIEW_2026-11-18.md), [real-CLI follow-up](D2_REAL_CLI_DYNAMIC_ARRAY_SOURCE_HOST_REVIEW_2026-11-18.md), and [D1 waiver](D1_INTERIM_REVIEW_USER_WAIVER_2026-11-18.md). I independently examined the actual native definitions and headers, native dynamic_array implementation, D1 receipt and first-error/terminal gates, extraction and mutation tests, C++ host, workflow, actual GitHub run/job metadata and four final job logs. This was a **read-only remote source/evidence review**; I did **not** execute a Unity Player or locally rebuild the host.

Native baseline-to-D2 compare: `il2cpp_plus@ff0b7f81f6e66ff47a51edb8b348c9d25d2237e3...b86a97e1dcca18163df5ac2d5f268bf6de18bbdf` is ahead by five commits and modifies exactly `Assembly.h/.cpp`, `MetadataCache.h/.cpp` and `AssemblyShadow.cpp` under `libil2cpp/vm`. All five independently fetched blob IDs matched the D2 report: `934de0826582339878dc7a70c53f966327c6ef69`, `e46ece727d5f03a914a4a6ba147cc69bc4e0a427`, `1f99a863e80a692053e57781648dba1bcc50f80c`, `f0f8124ee979d563fdd170fc13c8d90ea29bf702`, `a03111cd93e02ea9d89cd2a3dba8e764e922ba46`, respectively.

## 2. Independent conclusions against the seven reviewer questions

### Q1. Destructor order — PASS for the actual C++ scopes

`MetadataCache::PublishInterpreterAssembliesBatch` (MetadataCache.cpp ~1158–1172) obtains `g_MetadataLock`, reserves the CLI vector and constructs a synchronous stack context; `Assembly::PublishShadowBatch` (Assembly.cpp ~269–315) then obtains `s_assemblyLock`, reserves its pointer vector, and constructs `ScopedPhysicalRollback` **after** that lock. During the nested `PublishShadowRegistries` callback (MetadataCache.cpp ~1133–1156), `ScopedCliRollback` is created immediately before the CLI appends and the staged-publisher call.

For a failure after the CLI guard is constructed, normal return or C++ exception produces the following order:

1. CLI guard restores `s_cliAssemblies` to the recorded size;
2. physical guard calls the idempotent `onAbandon` wrapper, releasing the usage lease if held;
3. physical guard shrinks `s_Assemblies` to the previous size;
4. `s_assemblyLock` RAII unwinds;
5. `g_MetadataLock` RAII unwinds;
6. the outer CommitTransaction exceptional-exit guard freezes an error and seals terminal state **only on unwinding**, after the native callback scopes have exited.

No CLI rollback is required when execution refuses before entering the CLI callback; no registry entries have then been appended. On normal success, `PublishActive` releases the usage lease, both guards are disarmed and `s_assemblyVersion` is incremented once. No destructor-order violation was found within these paths.

### Q2. Callback ABI, real locks and allocation — PASS in source; platform integration unproved

The two headers and definitions agree on the added `onAbandon` callback. The physical guard supplies `AbandonShadowPublication`, which forwards to native `ReleasePublicationUsage`, whose function definition is explicitly `noexcept`. The assembly vector is `std::vector<const Il2CppAssembly*>`; its destructor-time `resize(previousSize)` shrinks a pre-reserved pointer vector, with no element construction/allocation on the exercised path. The real `libil2cpp/utils/dynamic_array.h` blob `0e6653e6e7efe93f023f63893c1a3b94f347a1d0` has `resize_uninitialized` returning when the new size is within capacity; the CLI vector is reserved before publication. Thus the intended cleanup operations are non-growing for valid prior sizes. This is a **source argument for the scoped data structures**, not proof of every native allocator, OOM, ABI, Unity lock implementation or shutdown behavior.

### Q3. Double unlock, lock order, destructor throws — no D2 blocker found

`TryBeginPublication` takes UsageLock and sets `publication.usageHeld=true` immediately; all normal success/refusal and physical rollback paths call the same function. `ReleasePublicationUsage` returns without unlocking if `usageHeld=false`, then sets it false **before** `UnlockUsage`. The callbacks operate under the nested registry locks and one transaction context, so a second cleanup in this path does not clear another owner's already released lease. `UsedClosureMember` reads the existing closure/first-use fields while UsageLock is held, without metadata-lock acquisition. The reviewed path acquires locks in the documented order transaction → metadata → assembly → usage and does not acquire them in reverse. This does not establish a transitive, whole-VM lock graph or native atomic ABI guarantee.

Both new rollback destructors and the abandonment callback are `noexcept`; pointer-vector shrink and capacity-preserving CLI shrink are non-growing. A throwing or otherwise malformed callback outside this fixed implementation would violate the contract; none is present at the pinned callsite.

### Q4. First-error and terminal semantics — PASS at source/host scope

In `CommitTransaction` (AssemblyShadow.cpp ~1261–1284), `ScopedUnexpectedPublicationExit` is armed across the actual nested publisher call. Its noexcept destructor attempts `FirstErrorV2::TryFreeze(InternalError,UnexpectedFailure,...)`, sets `s_unexpectedFailure=true`, and stores `Failed` with null `s_active` or `FailedAfterCommit` with non-null `s_active`. The actual `AssemblyShadowFirstFailureV2.h` uses a one-time compare/exchange from Empty, so a previous Frozen/Invalid first event is not overwritten. `TerminalMethodDenied` (AssemblyShadow.cpp ~314–328) treats `s_unexpectedFailure` as durable and rejects business method execution even without an active snapshot; the terminal helper also denies `Failed` directly.

The D2 host directly tests prior-first-error preservation with a **mock** FirstError implementation and tests the extracted native exceptional guard. The actual first-error class and terminal predicate were inspected as source, **not** linked into this D2 host, so full native reporting/visibility remains for later validation. This does not authorize retry after Codec publication.

### Q5. D3 critical gap — explicitly OPEN, not counted as D2 rollback

`PublishActive` (~727–741) calls `InterpreterAssembly::PublishStagedImagesBatch` without a real D1 phase receipt. The `CommitTransaction` normal `!published` branch (~1286–1294) still restores `Validated`, including when `runtimePublicationFailed` is true. D2 registry truncation cannot undo an attempted or completed HybridCLR `Codec::PublishBatch` / runtime group. D3 must record **CodecAttempted before the real call** and classify unknown/post-attempt outcomes as terminal/restart-required, unless genuine precodec non-attempt and complete cleanup are independently proven. **Critical carry-forward; D3 must close this before product/Local acceptance.**

### Q6. D4 snapshot ownership — explicitly OPEN

`PublishActive` publishes `s_active` using `publication.snapshot` (~738), while `CommitTransaction` still holds the corresponding `std::unique_ptr<ActiveSnapshot>` until `snapshot.release()` (~1296). This is not a general proven process-lifetime handoff across asynchronous faults, unwinding or shutdown. D4 must settle lifetime before public store, prove its post-store path and terminal behavior, and test actual relevant phases. **Critical carry-forward; not solved by D2.**

### Q7. Real-environment validation — required later, not performed

Real production native translation-unit compilation and linkage with Unity/IL2CPP, FastAutoLock/baselib native semantics, real allocator and GC/VM epoch, actual Runtime/Codec exception/boolean outcomes, active snapshot lifetime, concurrent registry readers, no-exceptions behavior in a real Player, platform/32-bit ABI, shutdown/finalizer behavior, native V2 first-error transport and first recovery are NotRun. Future D5/Local authorization must be explicit and source-pinned; no previous oneuse B1 batch is consumed or reused as a fresh D2 product run.

## 3. Independently checked CI evidence

- [Final actual-CLI run 44278898831](https://github.com/night-outlook/hybridclr_demo/actions/runs/44278898831) is **completed/success, 4/4 jobs**; run head `6362aa3469abd3baa15b97b8e5cb169f602c27d1`, push event. Independently fetched **all four job logs**; parsed exactly 36 D2 JSON scenario receipts/job = 19 mock-CLI (287 checks) + 17 real CLI template (281 checks), or **144 passing receipts, 2,272 checks** in total. Four jobs: macOS 15 C++11/C++17, Ubuntu 24.04 C++11/C++17. Each has 18 source mutation tests, and normal/exception host scenarios under strict, ASan/UBSan and no-exceptions builds. No D2 native C++ compile error, sanitizer violation, or failing host assertion found. GitHub action Node/punycode deprecation notices are unrelated tooling warnings, not native compilation failures.
- [Original final mock-CLI run 44255064703](https://github.com/night-outlook/hybridclr_demo/actions/runs/44255064703) independently confirmed **completed/success, 4/4 jobs**, run head `150f4a685dda170880089dbe1a930028f562056a`.
- [Initial actual-CLI run 44278777181](https://github.com/night-outlook/hybridclr_demo/actions/runs/44278777181) confirmed **completed/failure, 4/4 jobs failed**. Historical failures remain failures; correcting the assertion-count threshold does not retroactively convert that run into a pass.
- `extract_d2_native_custody.py` verifies the exact five native blob IDs, checks branch-specified native commit HEAD, extracts fourteen source definitions and tests source mutations. The `D2NativeCustodyHost.cpp` assembles exact extracted expressions with **mocked** VM, allocator and locks. The real CLI profile compiles the exact pinned dynamic_array template with a test-owned `Memory.h` shim. This is not the complete native `CommitTransaction` translation unit; the local exception guard is extracted as a standalone struct.

## 4. Findings and disposition

| ID | Severity | Conclusion | Required follow-up |
| --- | --- | --- | --- |
| IR-D2-01 | Pass / D2 | Scope ownership, destructor order, CLI and physical rollback consistent on normal false and C++ unwinding | Preserve guards, no D2 corrective source change |
| IR-D2-02 | Pass / D2 bounded | Idempotent usage release, no duplicate unlock in single-context callback chain | Validate real locks and platform behavior in D5 |
| IR-D2-03 | Pass / D2 bounded | Unexpected C++ exit latches terminal first-error state, including null-active; host and source agree | Real FirstErrorV2 reporting and Player gate still NotRun |
| IR-D2-04 | Critical / D3 | Normal false-return may still restore Validated after unknown Codec attempt | **Mandatory D3 fix; no post-Codec retry claim** |
| IR-D2-05 | Critical / D4 | Process-lifetime snapshot ownership not proven at public active store | **Mandatory D4 fix; avoid dangling public pointer** |
| IR-D2-06 | High / validation | Mock locks/VM/allocator and extracted bodies are not a complete native Unity build | Require exact-source real Unity/IL2CPP/Player/ABI testing only at authorized Local stage |
| IR-D2-07 | Coverage limitation | D2 host's hypothetical post-group throw is synthetic; real Runtime/Codec not executed in this host | D3 actual Runtime/Codec phase-linked fault test |

**Decision rationale:** D2's authorized exit criterion is bounded ownership of native physical/CLI registry cleanup and UsageLock on false/exceptional callback exits; the actual pinned implementation and authenticated cross-platform source-host evidence satisfy that narrow checkpoint. D3/D4 issues are genuine and **critical**, but they are explicitly designated separate slices, not proof of a defect in D2's scoped cleanup. No independent evidence supports extending this pass into D3/D4 or real Player acceptance.

**Final state:** `D2IndependentReview=PassD2ForD3`; `D1IndependentReview=WaivedByUser` (not passed); `D3=NotStarted`; `D4=NotStarted`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. B2 inactive with 128 combined TypeDefs, 64-byte names and 65,536 owner-lookups; original V1/B1/R02/source-roster/PureInterpreter constraints unchanged. **Do not begin D3 as part of this independent review.**
