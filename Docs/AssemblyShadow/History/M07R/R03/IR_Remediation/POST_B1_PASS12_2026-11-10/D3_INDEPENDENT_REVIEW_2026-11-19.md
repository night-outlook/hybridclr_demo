# R03 B2 D3 — Independent source-and-evidence review

**Decision: ReturnRequired — D3 NOT accepted; D4 NOT authorized.**
**Review date:** 2026-11-19 UTC. **Scope:** D3 phase observer, real Codec/Runtime publication boundaries, normal-false terminal disposition, concurrency/first-error behavior, and exact-code host evidence. This is an independent, read-only production-source review and CI-log audit, not a Primary self-review, local Unity validation, or Human Review Gate.

## 1. Exact authority and methods

Feature branch: \`codex/assembly-shadow-r01b-h1\` in all four repositories. Independently verified remote heads *before publication of this review*:

| Repository | Verified branch HEAD | Reviewed source |
| --- | --- | --- |
| night-outlook/hybridclr_demo | \`dbfc778b6162c820d9ee369e2897eebe977e6993\` | D3 tested code at \`430a9f9f81d504ae1bc37c62963e49a6d056ea6b\`, later docs-only HEAD |
| night-outlook/hybridclr | \`c3c232023724cbad565b85e9b2c3beea8ce2789a\` | Six modified production files |
| night-outlook/hybridclr_unity | \`948c0e3b4f8891481301770115e8ba4945eea6de\` | Unchanged |
| night-outlook/il2cpp_plus | \`e31d73968e1895e46c0d790132f1b10b23f78842\` | AssemblyShadow.cpp and D3 decision header |

Diff to the approved D2 pins: \`hybridclr\` = six production file modifications (six commits); \`il2cpp_plus\` = two production paths (three commits); \`hybridclr_demo\` = five D3 test/workflow paths (twelve commits to the tested code). No unexpected production file or \`hybridclr_unity\` change appeared in the reviewed compare. All D3 source blob hashes were directly re-read and matched the pinned test extractor.

Documents consulted: [D3 request](D3_INTERIM_INDEPENDENT_REVIEW_REQUEST_2026-11-19.md), [D3 Primary evidence](D3_RUNTIME_PHASE_BRIDGE_IMPLEMENTATION_PRIMARY_REVIEW_2026-11-19.md), [D2 independent review](D2_INDEPENDENT_REVIEW_2026-11-18.md), [Approach A](B2_NATIVE_PUBLICATION_REMEDIATION_PREAPPROVAL_DESIGN_2026-11-18.md), and canonical README/handoff. Unlike the Primary report, the conclusions below were reached by independently inspecting the exact production definitions, reader/guard logic, actual Codec, D2 native rollback scopes, harnesses, workflow and four raw CI job logs.

**Evidence standard:** A source-derived permitted interleaving is a code-level finding, not a claim of observed Player execution. Successful host tests remain valid within their exact stated mock/source scope.

## 2. Critical finding — IR-D3-01: post-Codec failure unlocks UsageLock before terminal business denial

**Severity:** CRITICAL. **Result:** ReturnRequired. **Affected guarantee:** No baseline/business execution can slip through after an uncertain or irreversible Codec publication failure before the process becomes terminal.

**Exact causal source chain (all references to pinned production):**

1. \`hybridclr/metadata/InterpreterMetadataIndexRuntime.cpp:252–263\` calls \`beforeCodec\` then the **actual** \`codec.PublishBatch\`. The latter can produce a normal failure after entering Codec (e.g. validation error) or complete a real publication group. The phase receipt advances to P3/CodecAttempted at the correct site.
2. \`il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp:753–779\` calls the staged publisher. On a **normal false return**, \`PublishActive\` sets \`runtimePublicationFailed=true\` then calls \`ReleasePublicationUsage(context)\` **before** any D3 durable terminal flag is stored. \`ReleasePublicationUsage\` (~729–735) sets \`usageHeld=false\` and clears the process UsageLock.
3. The call then passes through \`MetadataCache.cpp:1133–1156\` CLI rollback and \`Assembly.cpp:269–315\` physical rollback/lock unwinding. The D2 physical rollback's second abandonment callback is idempotent, but it does not reinstate the usage lease or seal terminal state.
4. Only after the entire nested publisher returns to \`AssemblyShadow::CommitTransaction\` does \`ClassifyFailedNativeBatch\` execute (~1335–1343). The first durable flag is written in the normal \`!published\` branch at \`AssemblyShadow.cpp:1350\` (\`s_unexpectedFailure.store(true, release)\`); \`s_state\` is changed from **Committing** to Failed/FailedAfterCommit afterward (~1351–1353).
5. \`AssemblyShadowTypes.h:40–52\` assigns \`Committing=5\`, \`Failed=8\`, \`FailedAfterCommit=9\`. \`AssemblyShadowTerminalExecution.h:12–27\` explicitly treats **Committing + durableFailure=false** as **not terminal**. \`AssemblyShadow.cpp:316–328\` implements the corresponding \`TerminalMethodDenied\` test.
6. On another thread, \`AssertMethodIsActive\` (\`AssemblyShadow.cpp:2114–2196\`) can pass the initial terminal check, acquire the newly released UsageLock for a candidate baseline method, observe \`s_active==nullptr\`, record baseline first use and pass the final \`TerminalMethodDenied\` recheck **before the failure producer publishes the flag**. \`RequireUserCodeAllowed\` (~2286–2292) tests staging/metadata resolution, not Committing as terminal. This method path does not need the outer \`s_assemblyLock\` or \`g_MetadataLock\` in its simple nongeneric case.

**Permitted two-thread schedule (source-derived counterexample; NOT observed in a Player):**

| Step | Publication thread T1 | Method-entry thread T2 |
| --- | --- | --- |
| A | P3 reached; Codec called; Runtime returns error, or post-group observer refuses | — |
| B | \`PublishActive\` sets \`runtimePublicationFailed\`, calls \`ReleasePublicationUsage\` | — |
| C | T1 has **not yet** run the outer D3 classification; \`s_state=Committing\`, \`s_unexpectedFailure=false\`, \`s_active=nullptr\` | \`TerminalMethodDenied\` returns false; acquires UsageLock |
| D | T1 still unwinding registry scopes, or paused before D3 terminal store | T2 sees no active shadow, records candidate baseline use, final terminal check also returns false, and can enter a baseline method |
| E | T1 eventually sets \`s_unexpectedFailure\` and \`Failed\` | Business execution may already have begun |

This is a **check-then-publish gap** between releasing the exclusive publication/use serialization and publishing the durable fail-closed decision. Its width need not be large to make a valid interleaving. It is particularly relevant when a real publication group was already written but the native callback returns a failure, the precise failure family D3 was introduced to protect. No unconditional background/implicit state transition closes this gap in the inspected paths.

**Required D3 remediation:**

- Make the terminal intent/failure gate observable **before releasing UsageLock** on every D3 normal false return for which the attempt cannot be proven precodec and retryable. The first-error freeze may occur separately if necessary, but no business entry may see the usage lease released and a still-healthy terminal predicate after a postcodec failure.
- Cover exceptional unwind where Codec has been attempted but the outer \`ScopedUnexpectedPublicationExit\` guard currently seals state only after the D2 inner onAbandon callback releases UsageLock. Preserve D2 destructor/lock order and the already reviewed first-error/noalloc constraints. Do **not** poison the proven P0 used-closure refusal.
- Use a single monotonic, source-owned failure/transition mechanism that does not require new reverse lock acquisition or managed calls from native scope destructors. Do not set/clear a global terminal flag transiently on ordinary successful publication without proving reader semantics.
- Add a **deterministic two-thread interleaving test** (barrier/scheduler-controlled) that forces T2 method admission immediately after T1 releases the usage lease but before the old outer terminal-store site. Assert denial for P3 failure and postgroup failure, while proving P0 used-denial still supports the documented cleanup. Test both normal false and C++ exceptional exits; the real source-host may use a mock reader/entry gate provided the exact native callbacks, publication observation and terminal latch placement are authenticated.
- Retain D1 phase/first-error monotonicity and D2 physical/CLI cleanup. Do not claim that truncating native registries reversed a committed Codec lifecycle or that process restart happens automatically.

**Gate impact:** This is a correctness defect in D3's own fail-closed classification/visibility contract, not merely D4's already-open ActiveSnapshot ownership transfer. Independent D3 cannot pass solely because the sequential failure disposition is correct.

## 3. Other independent conclusions

### IR-D3-02 — PASS / source: actual P3/P4 placement and callback forwarding

\`InterpreterMetadataIndexRuntime.cpp:252–254\`: \`beforeCodec\` immediately precedes \`current->codec.PublishBatch\`, after Runtime's validation loop. \`Runtime.cpp:258–263\`: real group membership stores and \`groups[group].active.store(1, release)\` precede \`afterRuntimeGroup\`. The Codec body (\`InterpreterMetadataIndexCodec.h:549–582\`) validates every reservation before the first \`Lifecycle::Published\` store and does **not** implement a reverse transition after publication. \`StagedAssembly.cpp:538–543\` and \`InterpreterImage.cpp:188–193\` forward the same observer pointer synchronously without taking ownership. Native \`ObserveCodecAttempt\` and \`ObserveRuntimeGroupPublished\` advance the original D1 receipt. No misplaced callback or missing ordinary call-site was found in this inspected chain.

### IR-D3-03 — PASS / sequential source and host: P0 used-closure vs terminal normal-false decision

\`TryBeginPublication\` records a used closure while holding UsageLock, releases the lease and returns false before either registry append. P0 remains Prepared. The actual D3 \`ClassifyFailedNativeBatch\` requires a used-closure identity, P0/InProgress, usage released and no runtime publication failure before granting a P0 \`RejectedBeforeCodec\` disposition. All other failed callback returns produce terminal disposition, including P3 real Codec validation rejection and P4 postgroup rejection. The applied conservative policy is correct **as a sequential disposition**, though it may make provably harmless Runtime prevalidation failures restart-required. Its semantics are documented and no retry after P3 is granted by this helper. **This result does not override IR-D3-01's race.**

### IR-D3-04 — PASS / source with visibility caveat: first-error, ABI and success path

After a normal false, \`CommitTransaction\` invokes \`FirstErrorV2::TryFreeze(TransactionTerminal)\` before setting the durable unexpected-failure flag. \`FirstErrorV2\` freezes via Empty→Writing CAS and will not replace an earlier Frozen/Invalid event. After the terminal store, the method gate rejects even when \`s_active\` remains null. The existing \`AssemblyShadowState\` enum and managed-visible signatures are not modified; the added publication-observer parameter has a default-null argument on the C++ runtime API, not a new managed API entry. The success path leaves D3's phase receipt at **P4/InProgress**, retains the existing publication/version path and does not claim D4/P5/P6 completion.

### IR-D3-05 — HIGH / evidence limit: concurrency and full native call-chain proof absent

The [D3 test host](https://github.com/night-outlook/hybridclr_demo/blob/430a9f9f81d504ae1bc37c62963e49a6d056a/Tools/AssemblyShadow/R03IR/TypeDefCensus/D3RuntimeBridgeHost.cpp) links the *actual* \`InterpreterMetadataIndexRuntime.cpp\` and \`Codec.h\`, eleven authenticated extracted function bodies, and the two literal staged/image wrappers. However, \`Fixture::Publish\` calls \`PublishActive\` **directly**, bypassing production \`MetadataCache::PublishInterpreterAssembliesBatch\`, D2 CLI/physical rollback scopes, and the real \`CommitTransaction\` terminal latch. It does not run concurrent method-entry admission, freeze the real FirstErrorV2, or verify \`UsageLock\`-to-terminal publication ordering. The postgroup negative case changes the host callback behavior artificially; that is a valid source-host simulation but not evidence of an actual Unity postgroup producer. Accordingly, neither the test's \`exactForwardingBodiesCompiled=true\` field nor its 4/4 success closes the D3 race.

A bounded source-host regression integrated with the real D2 scopes and actual D3 classifier is recommended before re-review, followed by full real native/Player validation only at an authorized later Local Validation stage.

### IR-D3-06 — deferred / D4 and later integration (not a second D3 failure)

\`PublishActive\` still writes the raw \`s_active\` pointer before \`CommitTransaction\` relinquishes its local \`unique_ptr\`; D4's critical process-lifetime ownership and P5/P6 status are unchanged. Native full Unity/IL2CPP compilation, real mutex/VM/GC epoch, V1 fields14/15, V2 first-error transport/recovery, 32-bit ABI, shutdown, complete Runtime no-exceptions build and real Players are **NotRun**. These remain separate mandatory checkpoints; no historical B1 evidence is promoted.

## 4. Independent CI audit — PASS only within the host's claims

[Final D3 CI 44487046888](https://github.com/night-outlook/hybridclr_demo/actions/runs/44487046888) is **completed/success, 4/4 jobs**, at *tested* demo SHA \`430a9f9f81d504ae1bc37c62963e49a6d056ea6b\`, on macOS 15 and Ubuntu 24.04 × C++11/C++17. All four raw logs were independently fetched and parsed:

- Each job: **15/15 Python source/extraction mutation tests** reported \`OK\`, no skipped/error tests.
- Each job: **14 actual Runtime/Codec host executions, 220 checks** across strict/ASan+UBSan profiles (seven scenario names per profile); exact two forwarding method definitions present in compiled host.
- Each job: **18 native C++11 decision-header executions, 63 checks** across strict/ASan+UBSan/\`-fno-exceptions\` profiles (six scenario names per profile).
- Combined: **128 passing host receipts / 1,132 assertions**, plus **60 Python source tests**. No assertion or sanitizer failure appeared in these completed job logs. The no-exceptions build tests only the decision header, not the full Runtime/Codec native translation unit.

Historical GitHub conclusions were independently read: 44486080330 FAIL; 44486331190 FAIL; 44486337701 FAIL; 44486466404 PASS (narrower); 44486952917 FAIL; 44487004192 FAIL; 44487040320 FAIL; final 44487046888 PASS. Previous failures are not reclassified as successes.

This successful evidence demonstrates correct single-threaded phase ordering and selected failure outcomes under host stand-ins. It **does not** cover IR-D3-01 or authorize R03/H2/Human Review acceptance.

## 5. Reviewer decision and next checkpoint

| Finding | Severity | Disposition |
| --- | --- | --- |
| **IR-D3-01** — failure lease released before durable terminal gate | **Critical** | **ReturnRequired: correct and add deterministic concurrency regression** |
| IR-D3-02 — actual Codec/Runtime observer placement | Pass | Preserve |
| IR-D3-03 — P0 used-denial / P3+ sequential classifier | Pass bounded | Preserve; cover concurrent transition |
| IR-D3-04 — first-error monotonicity / ABI unchanged | Pass source-only | Retain exact input/first-error tests |
| IR-D3-05 — host bypasses real failure unwinding and business gate | High evidence gap | Extend focused source-host regression |
| IR-D3-06 — active snapshot/Player/whole-VM | Critical D4 and Local-deferred | Not D3 acceptance |

**Decision: \`D3IndependentReview=ReturnRequired\`**, not \`PassD3ForD4\` and not \`Blocked\` by missing access. The source-derived concurrency flaw warrants a focused Primary Implementation correction and a subsequent **new independent D3 re-review**. The Phase/Codec instrumentation itself and the sequential host tests may be reused with exact provenance. Do **not** begin D4 under the existing pass record.

Handoff authority remains \`WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION\`; \`D1IndependentReview=WaivedByUser\` (not Passed); \`D2IndependentReview=PassD2ForD3\`; \`D4=NotStarted\`; \`R03Accepted=false\`; \`H2Passed=false\`; \`ReadyForHumanReviewGate=false\`. No Local Validation, H2/M08A/X02/SNAP-01 or Human Review Gate authorized by this report.
