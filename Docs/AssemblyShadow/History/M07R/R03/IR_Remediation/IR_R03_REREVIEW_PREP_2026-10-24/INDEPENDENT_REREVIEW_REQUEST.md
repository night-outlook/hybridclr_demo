# Request template — independent R03 finding re-review (NOT invoked)

This is an **unexecuted request template**, not the independent reviewer result and not an H2 initiation. A person must explicitly start an independent design → plan → implementation → actual raw evidence assessment; no agent may self-certify Primary's work as a separate reviewer.

**Role:** Independent Full-Stage R03 Reviewer, separate from Primary Implementation and Local Validation. Use the GitHub Connector against an exact fixed four-repo tuple. Review only R03, including owner D1=A/D2=A. Do NOT edit/rewrite historical evidence, commit product code, run Unity/Player without separate authorization, begin H2/M08A/X02 or change acceptance flags.

## Read order

1. `hybridclr_demo/Docs/AssemblyShadow/README.md`, current `Plan/CURRENT_STATUS.md`, historical Local-owned `Handoff/LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md` and CLOSED `WEB_TO_LOCAL.md`.
2. Canonical `Plan/DESIGN.md`, `Plan/stages/R03-evolution-semantics.md`, `Plan/stages/R03-remaining-completion.md`, `Plan/EVIDENCE_CONTRACT.md`, `Plan/HUMAN_REVIEW_GATES.md`, S owner `OWNER_DISPOSITION_2026-10-08.md`.
3. Historical **FAIL** `History/M07R/R03/S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md` and its evidence citation erratum, bounded RC1–RC6 exit matrix, original S provenance correction, original S source/build/Player checkpoint and original host/SDK/Local results.
4. Current `IR_R03_REREVIEW_PREP_2026-10-24/{DESIGN.md,PLAN.md,PRIMARY_REVIEW.md,EVIDENCE.json,review_readiness.py,test_review_readiness.py}` and actual independent results from GitHub Actions 40086902503; treat machine source CI only as supporting source proof.

## Fixed reviewed source refs (verify new refs before beginning actual re-review)

- hybridclr_demo audited product/source is the historical S demo `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`, historical independent reviewed demo `aee7975874a5ddf236ab9d00d5d682b470010f8f`, and current branch Docs/CI descendant whose final SHA must be pinned when review starts; do not combine source execution identities.
- hybridclr: `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`.
- hybridclr_unity: `948c0e3b4f8891481301770115e8ba4945eea6de`.
- il2cpp_plus current native: `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`; older independent baseline `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.

## Required finding decisions

**IR-R03-02:** Independently inspect actual native `AssemblyShadow.cpp` terminal predicate, early and late `AssertMethodIsActive` state checks, safe diagnostic ctor scope, `RequireActiveMethod`, `Runtime::Invoke`/`InvokeWithThrow`, HybridCLR interpreter initial/nested/delegate/virtual methods and real AOT bridging. Re-evaluate the original source-derived counterexample; determine what is now code-corrected and which common business entry paths remain unproved. Require genuine source-matched post-poison *attempted* valid business call and actual body/field/canary result for Player closure; old S C04 lacks such affirmative receipt fields. Current focused runner uses stale native `74dbdbea...` vs actual `e1e5be...`, so no current-source Player PASS is implied from the pre-review CI.

**IR-R03-01:** Independently identify committed original-S nine-part archive SHA `23aed...` (587907380 bytes), seal/index/membership/ledger and actual source/build/Player/transitive inputs; explicitly reject old contradictory `f4c2...` five-part source as original S (withdrawn and provenance unjoined). Evaluate additive original-S provenance workflow 37845000985 and source capture of oversized generated IL2CPP outputs. Distinguish digest equality, actual semantic/full source-capture review, live external binaries, historical S original 90/90 and current acceptance.

**All remaining RC1–RC6:** Enumerate supported/observed, tested rejection, explicitly deferred by owner, unproved outside deferrals and failed/incomplete. Preserve D1 conservative V1/X02 deferral and D2 observational performance; assess RC2 original resources/Unity ABI, RC3 generics/old handles, RC4 cumulative baseline graph/roles, RC5 fixed risk budgets and RC6 source/evidence custody. No missing coverage may be relabeled Passed.

## Output obligations

Provide one independent design → plan → implementation → raw evidence report with exact four-repo Git SHAs, native/package/Player pairing, original test/evidence IDs, issue-by-issue `Fixed / NotFixed / NotReproduced / ScopeDecision / NeedsEvidence` disposition and severity, concrete safe remediation actions, missing source/Player proof, and a re-review decision. If an obligation requires a new Local runtime run, propose it for Primary/human authorization; do not create an executable handoff or launch the run.

**Required default until proven otherwise:** R03 full-stage independent **FAIL** remains, `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled. After a genuinely independent stage PASS and complete applicable exit matrix, the user may separately initiate Human Review Gate H2; automatic advancement is forbidden.