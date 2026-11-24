# R03 B2 D5-B C10 — RR5 Primary Implementation (2026-11-24 UTC)

**Primary status: SourceHostComplete_PendingIndependentRereview.** This is focused Primary remediation of [the independent RR4 ReturnRequired findings](D5B_C10_RR4_INDEPENDENT_REREVIEW_2026-11-24.md), not independent acceptance or a real Player result.

## 1. Exact source and scope

All four repositories are on `codex/assembly-shadow-r01b-h1`. The tested demo code commit is not the later documentation commit.

| Repository | Exact source commit |
|---|---|
| hybridclr_demo | `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328` |
| hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| il2cpp_plus | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

Native changes since RR4 `e9aee83345aa9df90085de50162a7aa9172e8263`: only `libil2cpp/vm/AssemblyShadow.cpp` and `AssemblyShadowD5WindowProbe.h`. Demo changes since RR4 review head `5f8334f8f229012f898a5bf865bb1ad377522e15`: the existing C10 workflow and 12 D5Probe files only. Initial demo implementation `03b802ad8811009641f2b986a151bb2cd97fda60`; successor source-contract test correction `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328`. HybridCLR and package commits unchanged. The existing five intended TU and nine C-export roster is unchanged. All **16/16 actual source blob identities** in [the v3 source pinset](https://github.com/night-outlook/hybridclr_demo/blob/a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328/Tools/AssemblyShadow/R03IR/D5Probe/d5c10_link_source_pinset_v1.json) (pinset blob `66b2e83f8cab4debb71af36d4bcd5eecd80b5629`) were read back through the Connector: 13 native inputs plus three isolated demo sources. No Local-owned documents, D5 admission authority, B1 oneuse evidence or unrelated milestone code changed.

## 2. RR4-01 — effective terminal predicate and denial origin

The native method-entry probe now observes the same `ReadMethodTerminalPolicy()` inputs as the production `TerminalMethodDenied`: state and all four durable failure latches (`s_typeFailure`, `s_unexpectedFailure`, `s_lateBaselineUse`, `s_referenceViolation`). It brackets first-error reads with two terminal-policy observations. Header `ClassifyGuardEntry` uses the existing `TerminalForBusiness` predicate: changed state/first-error/durable observations are mixed/raced, existing terminal/first error is preexisting, and only matching observed nonterminal Committing/Empty is code 1. This is an observed precondition, NOT an atomic whole-VM snapshot.

Wire v3 slot 4 = (1, entryPolicy, state, firstError), where entryPolicy 1=observed nonterminal, 2=preexisting terminal or first error, 3=mixed/raced/unknown. The exact same TLS method/worker binding still applies. Slot 5.d separately records decision origin: 0=direct target decision, 1=terminal-policy denial (including races after entry), 2=unowned/raced failure. The helper `RecordFirstGuardFailure` returns the existing first-error freeze result; underlying winning CAS, first-error immutability, failure publication and production rejection behavior are retained. Only a direct guard-owned denial with the matching first-error publication, pre-failure nonterminal observation and no competing durable failures can be a healthy-denial candidate. The actual native policy is not changed to globally deny Committing calls.

Header host tests simulate the exact split publication: durable latch published while state remains 5 and first-error 0, then later state/error completion. New mixed entry and independently racing terminal denial scenarios produce NoCoverage, never a healthy-denial candidate. Source mutation checks pin all four terminal inputs, both observation samples, first-error source, denial kind, and entry publication. The full native VM is not built, so this is source/host evidence, not empirical whole-VM ordering or proof that the actual fixture will be admitted/denied.

## 3. RR4-02 — exact-worker completion and canary ordering

`WindowProbe::ReleaseP5` rejects foreign, unarmed, unobserved and pre-guard-completion callers using the original one-shot TLS token owner, method pointer, consumed-token state, published guard-entry and completed decision. The release CAS publishes the calling worker's ordinary writes; its acquire is recorded once by the collector and that same value governs any admitted-body raw read. The managed release invocation moved to the finally of the exact `MethodInfo.Invoke(instance, null)` attempt; earlier binding/constructor errors no longer publish completion. No managed Join or managed-success flag is fabricated. The bounded native timer remains.

The new `foreign_release_during_body` case holds the target writer in an in-progress body, calls the exported release on another thread, verifies that neither foreign release nor early completion occurs, then permits the writer's ordinary canary store and checks the real release/acquire. Source-host tests cover both release and receipt-reader acquire sites separately. The release check enforces native thread/guard identity; the isolated managed fixture supplies the post-Invoke call-site contract. The same-thread call-site and actual Methods fixture/linkage must still be independently verified in a real binary, not inferred from host-only tests.

## 4. RR4-03 — guard admission is independent of body-side-effect read

The autonomous collector waits for the actual target entry and outcome records before normal completion; deadline paths remain bounded. Slot 9 and slot 10.b describe canary readability; slot 10 still requires native file publication and a matching externally supplied process outcome. The parser independently joins exact entry, result, counts, phase, receipt seal and PID/exit material. A coherent admitted guard with exit 42 and unreadable/unknown after-canary now returns `AllowedGuardAtP5_CanaryUnknown`, not generic NoCoverage, with `methodBodySideEffect=Unknown`. A denial candidate still requires the direct denial, terminal/frozen first-error and readable unchanged canary. An allowed guard without authenticated native worker release cannot establish body-side-effect evidence.

The fixed 4,652-byte layout is preserved, but receipt wire and native/managed protocol are **v3**; v1/v2 receipts are rejected. Historical evidence is not reinterpreted. The real Player flags in the parser remain false; externally supplied PID/exit values are NOT independent binary/process authentication.

## 5. Exact source-host CI and raw logs

Initial [run 45337866057](https://github.com/night-outlook/hybridclr_demo/actions/runs/45337866057), demo `03b802ad8811009641f2b986a151bb2cd97fda60`, **failed all four jobs** at `test_63_guard_entry_acquire`: two occurrences of the acquire anchor meant the first mutation escaped the old presence check. No C++/receipt stage was run in those jobs. The successor source-contract correction checks both acquire locations separately and adds test 80; no native/overlay source changed after that initial implementation. Preserve the first run as failed.

Final [run 45337986472](https://github.com/night-outlook/hybridclr_demo/actions/runs/45337986472), attempt 1, exact demo `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328`, native `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`, completed success. Primary fetched all four actual raw job logs and counted result markers:

| Runner / C++ | Raw job ID | Source Python | Link Python | Receipt Python | Native witness strict+sanitized | Manual writer | Auto writer | OFF | Synthetic receipt checks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Ubuntu 24.04 / 11 | 138254511633 | 80 | 27 | 49 | 40 | 2 | 34 | 1 | 34 |
| Ubuntu 24.04 / 17 | 138254511895 | 80 | 27 | 49 | 40 | 2 | 34 | 1 | 34 |
| macOS 15 / 11 | 138254511927 | 80 | 27 | 49 | 40 | 2 | 34 | 1 | 34 |
| macOS 15 / 17 | 138254511930 | 80 | 27 | 49 | 40 | 2 | 34 | 1 | 34 |
| **Total** | | **320** | **108** | **196** | **160** | **8** | **136** | **4** | **136** |

**624 Python tests, 304 C++ strict/sanitized host cases, four feature-OFF controls, 136 synthetic auto-receipt checks.** Every raw job includes two foreign-release witness passes, six synthetic NoCoverage markers across durable-before-error / mixed-entry / terminal-raced-denial, and two `AllowedGuardAtP5_CanaryUnknown` markers (strict/sanitized). No unexpected sanitizer/test errors observed in the four logs. The workflow's final marker explicitly says `actualIL2CPPCompiled=false` and `realUnityPlayerExecuted=false`. Ancillary auto-triggered B1 host qualification succeeded; four unrelated auto-triggered historical contract runs were cancelled, not promoted or used as acceptance. Their historical scopes are unchanged.

## 6. Limits and next permitted checkpoint

Actual full `AssemblyShadow.cpp` VM TU, Unity C# compiler, real VM/GC/MethodInfo, complete native linked Mach-O/Bee source-to-object custody, platform ABI, authentic process PID/argv/exit/first-error and all **18 D5 real Player cases remain NotRun/NoCoverage**. Historical custody roots remain unbound for new D5 execution. Source-host evidence cannot prove real method identity, live scheduling, genuine field mutation, production correctness, or acceptance.

`D5BC10IndependentReview=ReturnRequired` pending a separate RR5 rereview; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`.

Next only a new independently initiated C10 RR5 design/source/raw-CI review of the exact tuple. See [review request](D5B_C10_RR5_INDEPENDENT_REREVIEW_REQUEST_2026-11-24.md). No Local execution or later milestone; no Human Review Gate self-approval.
