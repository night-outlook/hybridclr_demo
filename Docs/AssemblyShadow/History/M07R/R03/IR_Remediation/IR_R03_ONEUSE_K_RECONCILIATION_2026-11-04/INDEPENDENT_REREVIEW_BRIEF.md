# R03 independent full-stage re-review brief — K evidence (NOT INVOKED)

This is a **prepared review input**, not an independent review result or approval. A human must explicitly initiate a new independent R03 review; Primary Implementation and Local Validation cannot self-certify their work. R03 independent result remains **FAIL** pending a separately executed and published review.

## Review boundaries and source pins

Scope: R03 only. Do not start H2, M08A, X02, SNAP-01, another Local cycle or other milestones. Read-only review. Preserve historical evidence and every previous FAIL/Blocked/PassedWithinScope verdict.

**Current K executed source tuple:**
- night-outlook/hybridclr_demo, codex/assembly-shadow-r01b-h1, **c20da0b261172cbdd188378e24dbe9343a14c6b2**
- night-outlook/hybridclr, same branch, **4b2774b066cfc6afd77a8c8aded6bda7ea574f55**
- night-outlook/hybridclr_unity, same branch, **948c0e3b4f8891481301770115e8ba4945eea6de**
- night-outlook/il2cpp_plus, same branch, **41764ae1eeefb33b05966e7f7676e52aae39c340**

**K Local evidence publication:** hybridclr_demo **14f97f15af6c06afa65957a9b880ccf841069452** (a descendant of executed c20...; do not treat that publication commit as a second Player run). The new Primary reconciliation resides in a subsequent documentation commit. At reviewer invocation freeze and report the actual then-current branch HEAD separately; never merge evidence/source roles into a single guessed SHA.

**Historical original S:** execution demo 29bb3d4a39bf8a2f23be404f77535aaba3485bfc, immutable checkpoint demo fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b, native 1cf87f8209790f9fb2ebec97487dc1990ccd56c5, original historical 90-cell ledger. The October 8 independent review used demo aee7975874a5ddf236ab9d00d5d682b470010f8f and reported **FAIL**.

## Mandatory first reads

1. Docs/AssemblyShadow/README.md, Plan/CURRENT_STATUS.md, Plan/DESIGN.md, Plan/EVIDENCE_CONTRACT.md, Plan/HUMAN_REVIEW_GATES.md, Plan/stages/R03-evolution-semantics.md, Plan/stages/R03-remaining-completion.md.
2. History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md and its INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md; owner D1=A/D2=A and historical closure matrix.
3. This directory's PRIMARY_RECONCILIATION.md and EVIDENCE_INDEX.json; historical original-S provenance correction/capture-omission and RC1–RC6 ledger.
4. History/M07R/R03/local-validation-current-native-original-s-20261103-oneuse-k/{README.md,LOCAL_RESULT.json,EVIDENCE_SCOPE.json,RUNTIME_FINDINGS.json,batch/RESULT.json,batch/current-native/LOCAL_BATCH_RESULT.json,batch/installed-native-vm-parity.json,batch/native-host-diagnostics/RESULT.json,local-evidence/oneuse-K-FINAL_INDEPENDENT_AUDIT.json}, and retained live/raw/seal as needed. Handoff/RETURN_TO_WEB.md and Local Validation records distinguish source-only/host-only/real Players.

## Required independent finding decisions

**IR-R03-02 (High).** Reinspect exact pinned native AssemblyShadow.cpp terminal predicates (AssertMethodIsActive, RequireActiveMethod, RequireUserCodeAllowed), Runtime::Invoke/InvokeWithThrow, interpreter frames/nested/delegate/virtual/interface and physical AOT/managed bridge paths. Compare to the original source-derived counterexample and the corrected C04 citation erratum. Independently authenticate K's *actual* pre-positive 42, post-poison attempts true, reflection/delegate/AOT failure, canary 1→1, field 2→2 and OFF 1→2; check first failure 13/21 and persistent terminal state. Distinguish tested baseline/type from captured-generic and post-publication initializer (both K NotRun), and classify whether additional real Player coverage is necessary. Review the test-only native application-quit decision against the original shutdown contract; do not infer Unity-managed shutdown from NativeAtexit.

**IR-R03-01 (High).** Reconcile the authoritative original nine-part 23aedcaf.../15,713-member S archive, original transport/index/seal/process/source/build/Player graph and old 90/90 cells independently. Explicitly reject the withdrawn five-part f4c2a120... record as original-S authority absent a proven crosswalk. Verify material original generated Il2CppGenericMethodPointerTable.c and Il2CppInvokerTable.cpp semantics/installation/linked role and the complete historical capture omissions index; K's 135 **current** source pairs do not prove original S binary provenance. Distinguish independent byte verification from trusting Primary/Local logs.

**RC1–RC6.** Provide a requirement-by-requirement review covering conservative D1=A V1/X02 deferral, resource/Unity ABI/old serialized assets, generic/method/old handles/entry, cumulative baseline safety graph versus target load order and ordinary roles, D2=A observational performance and four Failed warm certificates, provenance and independent acceptance. Explicitly list P1/P2/E0/E1/P3 and whole-VM epoch, managed shutdown, GC/RSS, fullNativeIncludeClosure and generatedCppBinaryLinkage where still unsupported.

## Required output and stop

Produce a separate evidence-backed **PASS / FAIL / BLOCKED** independent R03 full-stage verdict, four frozen source SHA pins plus K evidence publication SHA, direct code/raw case references, each High finding's **Fixed / NotFixed / NeedsEvidence / ScopeDecision** with severity and justification, a bounded RC1–RC6 status matrix and exact remaining proof requirements. Identify uncertainty or unavailable external binary data rather than converting it to Passed.

If a new executable witness is needed, specify the *minimum* source-matched scenarios and proof contract for future Primary design and human authorization; **do not create a new runnable Local handoff or invoke Unity** under this request. The historical October 8 review and prior Local verdicts are immutable.

Until a separate independent stage PASS and all applicable closure obligations: R03Accepted=false, H2Passed=false, ReadyForHumanReviewGate=false, qualificationApproved=false, runtimeAcceptance=false, fullLegacyRegressionAcceptance=false; PureInterpreter disabled. Even a new independent PASS would not automatically start H2.
