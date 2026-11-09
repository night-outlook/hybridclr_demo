# Primary reconciliation — R03 captured-generic A2 oneuse-09 focused PASS

Date: 2026-11-09 UTC. Owner: Primary Implementation. **Scope: R03 IR-R03-02 A2 only.** This is not an independent full-stage R03 review, production admission, Human Review Gate approval, or new Local validation.

## Source and evidence authority

- Exact executed demo source: **bb5fce9c15450e68c6341d88270fbc30dd7b9738**.
- Exact Local evidence publication demo: **97cd47e06a837569ff62c4ac7744117d22966126**.
- Other unchanged execution pins: hybridclr **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**; hybridclr_unity **948c0e3b4f8891481301770115e8ba4945eea6de**; il2cpp_plus **41764ae1eeefb33b05966e7f7676e52aae39c340**.
- Local-owned Handoff/LOCAL_VALIDATION.md is **empty at the Git-published HEAD**. Read the full factual Local Handoff/RETURN_TO_WEB.md and immutable checkpoint instead of inventing that file's text.
- Original Git-published record: Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-09/, particularly LOCAL_RESULT.json, local-evidence/RUNTIME_FINDINGS.json, RUNTIME_REVIEW.md, FINAL_INDEPENDENT_AUDIT.json, CI_VALIDATOR.json, the three Player request/raw/verification records and original command receipts, build-receipt.json, manifest, custody and seal.

## What the original Local run supports

- Exactly **one authorized runner invocation**: 19 distinct cells Passed; exactly **one** Unity 2022.3.62f2 macOS ARM64 IL2CPP ON/diagnostics2/Release BuildPipeline succeeded (zero errors, one BuildReport warning). Published BuildReceipt SHA-256: **671644a8b110684389fe07c00e6052559b5151d2ed876364824d1bb66ac3b345**.
- The real generated Cdecl int32() Bi4 source before/after BuildPipeline was **c6bbea6e179964b7296bff02ee4f434b188e8578a4e7086da1c283e79b82f3da**. Linked GameAssembly SHA-256 **1a7b6a25125c79478b6019a859498fbed6d412cd8d05bc03aed4d081e77882c4**; executable SHA-256 **e8eacb584cb71d6f54d7a73d72ff11a1bc9c8790526228d444ef49b25268656c**.
- Initializer-control PID **52095**, exit0, genuine linked Bi4 phase103=1 before Commit, callback299/300 once, field3/mask15, Commit0/state6 and empty recovery reason.
- Initializer-failure PID **52113**, exit0, same callback/field/mask, Commit19/state9 after callback and native first recovery ending **R03IR.InitializerFailure.AfterPublication.V1**. A postterminal AOT attempt did not change the canary.
- Captured-generic PID **52122**, exit0: physical Methods.R03.Node TypeDef used as the method_inst argument in an independently owned, inflated Assembly-CSharp R03CapturedGenericAotOwner.Touch<T> MethodInfo. VM state remained6 **after inflation**. The genuine native AssemblyShadow::AssertMethodIsActive denied entry; first failure **15**, state9, Context=method_inst, TypePath=/arg[0], Reason=CapturedBaselineType. Subsequent actual Runtime::Invoke reported an exception and the AOT counter was unchanged **1→1**.
- Captured fixture SHA-256 **c7e4ddd3da14207ad680e9c0f60458f967661202a9cbf6a383ba06289ec11aab**, MVID **d8f7bafb-421a-2979-4e5a-1b290117a32a**, 2,560 bytes; two distinct same-Mac generator runs matched exactly.
- Seven mandatory exact-source dual-OS GitHub Actions workflows/14 jobs passed the strict job-level source preflight; four direct job web pages supplied independent status during API rate limiting, crossjoined with attempt/check-run records. Original capacity samples were each >45 GiB; original source/SDK/custody and 3,198 regular native host files/4 literal symlinks passed. Product archive seal Passed with **509** indexed members within its declared bounded scope.
- The single-use **oneuse-08** remains historical **PrerequisiteBlocked/NotRun**: no runner, Unity build or Player and no reused root. oneuse-07 remains the earlier focused initializer PASS. Neither is rerun or overwritten.

## New additive source-based verification (not a new Player)

- Tools/AssemblyShadow/R03IR/captured09_publication_audit.py reopens selected **Git-published** original files, rehashes the actual published BuildReceipt, raw Player records, published index and request bytes, and independently re-parses the captured generic strict V1 record, original initializer phase/recovery journals and 7-workflow/14-job snapshot. It enforces unique PIDs/nonces, original source/build/fixture/overlay identities and false stage flags.
- Tools/AssemblyShadow/R03IR/test_captured09_publication.py exercises the original successful checkpoint plus **22 test methods** with adversarial mutations: source drift, extra/missing cells, replay, false acceptance/V2, damaged product/host scope, Bi4, callback order, first recovery, captured error13/21, swapped context, silent AOT invocation, PID/nonce/source mismatch, duplicate JSON keys and no-write checks.
- .github/workflows/r03-ir-captured09-publication.yml ran this **read-only** source suite on macOS 15 and Ubuntu 24.04. First diagnostic attempt at d53906ff09d23912a0d655831cce721be104d16e failed because original RUNTIME_FINDINGS.json has only runtimeAcceptance (no fabricated R03/H2 fields). The authoritative coordinator repository record also contains branch/phase/schema keys, not just a four-key pin map. Those schema assumptions were fixed without changing original evidence; successful both-OS source run: [42570848609](https://github.com/night-outlook/hybridclr_demo/actions/runs/42570848609).
- The verifier **does not independently rehash** the original physical macOS GameAssembly/executable, independently extract/reassemble all 509 sealed product members, rerun Unity, authenticate the original native V2 producer, or give a full independent R03 acceptance verdict. It returns **PassedPublishedBoundedRawCrossCheck_NotUnityV2OrR03Acceptance**.

## Next Primary work: B1 first-failure freeze source candidate

- New test-only Tools/AssemblyShadow/R03IR/NativeDiagnostics/FirstFailureFreezeV2.h provides a preallocated one-shot native error code/reason copy; concurrent writer CAS, release/acquire publication, bounded UTF-8, no truncation or fallback to later errors, no heap allocation/VM metadata/locks/IO in the capture path. This is **not** part of any Unity/IL2CPP Player.
- The companion native C++11 driver and dual-OS workflow ran real host code for genuine one-writer publication, immutable source-buffer copy, invalid-first sticky failure, malformed UTF-8, a full 4096-byte reason, 4097-byte rejection, 12 racing writers and a no-allocation sampling interval. Successful source run: [42571591288](https://github.com/night-outlook/hybridclr_demo/actions/runs/42571591288). Earlier malformed CI heredoc and signed-compare compile failures are historical failures, not relabeled.
- This header currently receives **caller-supplied** error facts. It does not read or freeze AssemblyShadow::s_typeFailure, Transaction::recoveryTerminalError, unexpected/reference/late-use cases, actual physical VM epoch, postpoison scheduler/GC, or a V2 filesystem sink. The native GetRecoveryInfoJson currently constructs std::string and std::ostringstream output. The next Primary source design must reconcile that real owner/lifetime boundary before integrating the test-only latch.

## Unclosed scope and stop

The independent full-stage October R03 verdict remains **FAIL**, High IR-R03-01 and IR-R03-02 remain open; the A2 witness alone does not authorize full terminal-entry coverage, complete native V2 first-recovery, single coherent VM epoch, managed shutdown, GC/RSS, original S full source/compiler/object/link/Player chain or RC/P/E qualification. **The type of the postterminal Runtime::Invoke exception is not identified by the original receipt**; do not infer it.

The 17 owner-retired roots and 40 duplicate paths remain Unavailable/PermanentlyDeleted. Historical strict custody remains Blocked. R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false. PureInterpreter disabled. No H2/M08A/X02/SNAP-01 or automatic Human Review Gate.

The A2 oneuse-09 WEB_TO_LOCAL authorization is **consumed/CLOSED**. Further Local Validation requires a new separately committed one-use exact-source contract. Current responsibility stays with **Primary Implementation** for native B integration and original-S evidence reconciliation.
