# R03 B2 D5-B C10 — Independent RR5 design → source → raw-CI rereview

**Date:** 2026-11-24 UTC. **Independent verdict: PASS, strictly for RR5 C10 source/test-producer preparation.** Status token: **`D5BC10IndependentReview=PassSourceProducerOnly`**. This is **not** real-Player validation, admission of a Local run, D5 completion, R03 acceptance, or Human Review Gate approval. I performed direct immutable-source and raw-log review; Primary's summary and passing counts were not accepted as independent proof.

**Authority remains closed:** `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All **18 actual D5 Player cells = NoCoverage**. Only the three RR4 blockers and their directly related RR5 producer contracts are decided here; other D5/D6/H2/M08A/X02/SNAP-01 gates are not approved.

## 1. Reviewed immutable sources and independent provenance

All repositories use `codex/assembly-shadow-r01b-h1`. The CI-tested demo **code** SHA differs from the documentation-only branch HEAD.

| Repository | Immutable CI-reviewed source commit | Branch HEAD observed before this review |
|---|---|---|
| `night-outlook/hybridclr_demo` | `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328` | `0af13b563fda8f972f1cc97fc44e1afd5cee6376` (one later documentation-only commit) |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | same |

Independent Git compare: `il2cpp_plus@e9aee833...1268dd41` is **one commit changing only** `libil2cpp/vm/AssemblyShadow.cpp` (58 insertions/15 deletions) and `AssemblyShadowD5WindowProbe.h` (47 insertions/6 deletions). `hybridclr_demo@5f8334f8...a8f9cb31` is **two code commits affecting only** the C10 workflow plus 12 existing D5Probe paths. No other production fork was altered in this RR5 source tuple.

Read the complete [v3 source-pin manifest](https://github.com/night-outlook/hybridclr_demo/blob/a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328/Tools/AssemblyShadow/R03IR/D5Probe/d5c10_link_source_pinset_v1.json), Git blob `66b2e83f8cab4debb71af36d4bcd5eecd80b5629`. Through the GitHub Connector I fetched and checked **16/16 actual Git blob IDs**: all 13 listed native files at the pinned il2cpp_plus revision and all three isolated overlay/managed/build sources at the pinned demo revision. Key source blobs: native main `728acbc9e93857a5211b6f2ced12d21a42b16194`, probe header `d18aeb996ce4cf1b1abecf5377b6b6e3ff967ed0`, native overlay `e8643e242bdac6929c786d7ac994bbf0daa99469`, managed fixture `64371a90278849f05afbe39c196dbc7eea82f934`, parser `44094a2e6ddc5a16238d287c956eb483995dd847`. These are Git source identities, **not** hashes of installed Unity native inputs or any linked executable.

Read the [RR4 independent ReturnRequired](D5B_C10_RR4_INDEPENDENT_REREVIEW_2026-11-24.md), [RR5 Primary report](D5B_C10_RR5_PRIMARY_IMPLEMENTATION_2026-11-24.md), [RR5 review request](D5B_C10_RR5_INDEPENDENT_REREVIEW_REQUEST_2026-11-24.md), C10/D5 proposed Player matrix, native and managed sources, parser/tests, native host suites, and the four complete GitHub Actions job logs.

## 2. RR4-01 — terminal policy / denial origin: CLOSED at source-producer scope

- [The actual production terminal decision](https://github.com/night-outlook/il2cpp_plus/blob/1268dd417ffe9090fcd9ea2d49542c97ed3cccb3/libil2cpp/vm/AssemblyShadow.cpp#L327-L354) and test entry both use `ReadMethodTerminalPolicy()`: `s_state`, `s_typeFailure`, `s_unexpectedFailure`, `s_lateBaselineUse`, and `s_referenceViolation`. These are the same effective terminal *inputs*, rather than RR4's incomplete state+first-error pair.
- [Exact guard entry](https://github.com/night-outlook/il2cpp_plus/blob/1268dd417ffe9090fcd9ea2d49542c97ed3cccb3/libil2cpp/vm/AssemblyShadow.cpp#L2341-L2377) brackets two policy samples and two B1 first-error status reads before `TerminalMethodDenied`. [ClassifyGuardEntry](https://github.com/night-outlook/il2cpp_plus/blob/1268dd417ffe9090fcd9ea2d49542c97ed3cccb3/libil2cpp/vm/AssemblyShadowD5WindowProbe.h#L19-L38) returns `2` for a preexisting durable/terminal/first-error observation, `3` for mixed/unknown, and only `1` for observed nonterminal state 5 and first-error 0. The header explicitly does **not** claim an atomic whole-VM epoch.
- The terminal early return assigns denial kind `1` (terminal-policy, including raced denial). For a direct target guard rejection [lines 2484–2535](https://github.com/night-outlook/il2cpp_plus/blob/1268dd417ffe9090fcd9ea2d49542c97ed3cccb3/libil2cpp/vm/AssemblyShadow.cpp#L2484-L2535), denial kind `0` additionally requires a pre-failure nonterminal observation, the **successful native first-error freeze belonging to this guard** (`RecordFirstGuardFailure` return), still-Committing state and absence of competing durable latches; otherwise kind `2` is recorded. The existing first-writer CAS and immutable B1 error are preserved.
- Reproduced the RR4-01 publication-order counterexample at source/host-contract level: durable latch becomes true while state stays 5 and B1 first-error remains 0. The new `entry_durable_before_error` test classifies the entry as preexisting terminal, and `entry_policy_raced` as mixed, both never healthy candidates. The `terminal_policy_raced` synthetic writer produces `NoCoverage`. A post-entry terminal decision is kind `1`, never a direct kind `0` denial candidate.

**Bound:** no source/host test proves all atomics form a single coherent VM snapshot, or that real failure actors will be scheduled in a particular order. Current classification is properly limited to **observed** preconditions and first-failure ownership; a real Player/binary audit is still mandatory.

## 3. RR4-02 — exact worker release/acquire: CLOSED at source-producer scope

- [WindowProbe::ReleaseP5](https://github.com/night-outlook/il2cpp_plus/blob/1268dd417ffe9090fcd9ea2d49542c97ed3cccb3/libil2cpp/vm/AssemblyShadowD5WindowProbe.h#L118-L143) requires P5, the same TLS `ThreadAttempt.owner`, consumed `active==0` one-shot token, nonnull bound method, published target entry and terminal guard decision 1 or 2. A foreign or pre-result caller cannot perform the release CAS. `HasWorkerCompletedP5Acquire()` uses the actual release atomic, not the relaxed count.
- [The isolated managed source](https://github.com/night-outlook/hybridclr_demo/blob/a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328/Tools/AssemblyShadow/R03IR/D5Probe/R03D5P5WindowPlayer.cs#L102-L133) arms the exact Keep attempt immediately before `method.Invoke(instance, null)` and invokes the native release only in **that invocation's finally**. Constructor/binder failures preceding Invoke do not issue completion. This is a source-producer call-site contract, **not** proof that reflection and the physical native target worker actually run as designed in a Player.
- The [autonomous collector](https://github.com/night-outlook/hybridclr_demo/blob/a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328/Tools/AssemblyShadow/R03IR/D5Probe/R03D5WindowOverlay.cpp#L216-L253) acquires the native completion flag when deciding whether an allowed guard's non-atomic canary may be read. The worker's post-body release is the intended synchronization boundary. The host `foreign_release_during_body` case demonstrates foreign-thread release fails while the target body is held in progress; only the owning thread's later store and release allow canary observation. Wrong-method, unarmed, duplicate, earlier-than-guard and P6-raced scenarios are also exercised.

**Bound:** the source-host suites compile the exact header plus overlay with host-owned VM stubs, **not** the real Unity/IL2CPP `AssemblyShadow.cpp` translation unit and managed fixture together. Same native TLS across reflection/IL2CPP P/Invoke, actual GC-pinned field semantics and a real `MethodInfo*` join remain unverified.

## 4. RR4-03 — admitted guard survives unreadable canary: CLOSED at source-producer scope

- [v3 parser](https://github.com/night-outlook/hybridclr_demo/blob/a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328/Tools/AssemblyShadow/R03IR/D5Probe/d5_c10_native_receipt.py#L96-L189) separates `guard_joined` and `exact_guard` from `canary_joined`/`methodBodySideEffect`; slot 4 carries entry policy, slot 5 carries native result/denial origin, slot 6 native release observation, slot 9 canary, slot 10 native seal/validity.
- Coherent exact admitted guard plus externally supplied matching PID/exit 42, but **unreadable canary**, yields `AllowedGuardAtP5_CanaryUnknown` and `methodBodySideEffect=Unknown`, not `NoCoverage` and not fabricated `BodyExecuted`. The guard admission itself remains safety-significant source material; body execution is a distinct proposition.
- Direct denied candidate additionally requires kind 0, matching slot 5/7 counts, terminal state 9, frozen first error, unchanged readable canary, no timeout and externally supplied exit 20. Pre-poisoned, mixed, terminal-raced, unowned, missing slots and malformed observations fail closed or return `NoCoverage`.
- The fixed byte layout remains **4652 bytes** and protocol/receipt wire version is **3**. Regression tests reject versions 1 and 2, malformed/overlong files, wrong checksums, unsupported native release values, missing/contradictory slots, mismatched external PID or exit and false claims of Player authentication. The parser explicitly returns `externalProcessProvenanceIndependentlyVerified=false`, `actualLinkedBinaryAndPidAuthenticated=false`, `realPlayerC10Passed=false` and `R03Accepted=false`.

**Bound:** a consistent fabricated receipt and caller-supplied process numbers can produce a **SourceMaterial** classification. It is never a cryptographic/authenticated real Player claim. The real OS process monitor, argv, linked binary and actual B1 first-error provenance must be joined separately.

## 5. Independently fetched raw CI evidence

[GitHub Actions run 45337986472](https://github.com/night-outlook/hybridclr_demo/actions/runs/45337986472), attempt 1, fetched exact demo source `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328` and native source `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`. All **four** jobs independently verified `completed/success`; raw logs show both actual checkout SHAs and distinct Ubuntu/macOS C++11/17 compile targets.

| OS / C++ | Job ID | Python source+link+receipt | Native strict+sanitized | Manual native | Autonomous native | OFF | Synthetic parse |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ubuntu 24.04 / 11 | 138254511633 | 80+27+49 | 40 | 2 | 34 | 1 | 34 |
| Ubuntu 24.04 / 17 | 138254511895 | 80+27+49 | 40 | 2 | 34 | 1 | 34 |
| macOS 15 / 11 | 138254511927 | 80+27+49 | 40 | 2 | 34 | 1 | 34 |
| macOS 15 / 17 | 138254511930 | 80+27+49 | 40 | 2 | 34 | 1 | 34 |
| **Totals** | | **624 Python** | **160** | **8** | **136** | **4** | **136** |

**304 native host cases = 160+8+136.** The 136 synthetic parsing results are additional checks on the 136 autonomous-receipt materials, not 136 additional native compilations. Per-job raw logs contain 2 `foreign_release_during_body`, 2 `entry_durable_before_error`, 2 `entry_policy_raced`, 2 `AllowedGuardAtP5_CanaryUnknown` and expected `NoCoverage` outcomes for terminal-raced, preterminal and incomplete cases. No reported test failures or unexpected ASan/UBSan errors in the final four logs. CI itself says `actualIL2CPPCompiled=false`, `realUnityPlayerExecuted=false`.

**Prior failed run is not overwritten:** [45337866057](https://github.com/night-outlook/hybridclr_demo/actions/runs/45337866057), source commit `03b802ad8811009641f2b986a151bb2cd97fda60`, had 4/4 failed jobs at `test_63_guard_entry_acquire` (`AssertionError: SourceMismatch not raised`). That was a source mutation coverage failure. The successor `a8f9...` adds the second acquire-site mutation check and passes all four exact-source jobs.

## 6. Residual limitations and independent decision

**No new blocking source-producer defect was established in the requested RR4 remediation scope.** This `PASS` closes only RR5 RR4-01/02/03 **as designed and covered by source-host evidence**. It does not establish real-VM temporal coherence or actual method identity, native C++ full-TU compilation, reflection/IL2CPP call-site linkage, real GC/pinned object safety, Bee source→object→linked Mach-O/export roster/ABI, independently authenticated process PID/argv/exit/first-error, Player terminal behavior or absence of runtime data races. `R03D5Build.cs` and the source pinset describe intended build inputs, not completed compilation evidence. All 18 D5 Player matrix cases are `NoCoverage` and real full-VM/Unity/native-link/PID tests `NotRun`.

**Caution retained for future real validation:** the C10 observer distinguishes a native target guard admission from actual method-body execution; an allowed guard without after-canary visibility cannot prove body mutation, and phase/terminal observations are not a global atomic epoch. Exact worker same-TLS behavior and the native body's linked binary must be demonstrated with real execution. A source-only `exit=20/42` or synthetic receipt is never accepted as a Player result.

**Decision:** `D5BC10IndependentReview=PassSourceProducerOnly` (**Pass**, RR5 source-producer scope only). Report to Primary Implementation for the next separately scoped, documented gate/approval decision. Preserve `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, `APPROVED_LOCAL_HANDOFF_BLOB=None`, `D5BLocalExecution=NotAuthorized`, `D5LocalValidation=NotAuthorized`, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`. Do not start Local Validation, D6/H2/M08A/X02/SNAP-01, or Human Review Gate from this report alone.