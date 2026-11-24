# D5-B RR5 — Primary source-admission preparation (NOT Local Validation)

**Status:** `D5BRR5Preflight=SourceCommitted_PendingExactCIAndIndependentReview`. Date: 2026-11-24 UTC. This is a **new, additive, read-only** D5-B preparation step after [bounded C10 RR5 independent source-producer PASS](D5B_C10_RR5_INDEPENDENT_REREVIEW_2026-11-24.md). It neither reauthorizes D5-B execution nor modifies the previous D5-A / D5-B / B1 admission contracts.

## 1. Purpose and exact baseline

Reconcile the former D5-B **source-only custody proposal** (still pinned to D4 native `3e3d2ab9...`) with the subsequently reviewed C10 RR5 native `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`. Prevent any agent from misusing the former `D5Admission/d5b_custody_authority.py`, the historical `R03IR/current_native_source_gate.py` or the old B1 runner to claim a current C10 native build/Player. Provide a fresh reviewable Git source-input check, **not** an executable `WEB_TO_LOCAL` or a substitute for full D5 producer coverage.

Working branch for all repos: `codex/assembly-shadow-r01b-h1`. The exact reviewed C10 source baseline remains demo code `a8f9cb31cd51aed97a65d84e555ec7f4d3f2e328`, native `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3`, HybridCLR `c3c232023724cbad565b85e9b2c3beea8ce2789a`, and package `948c0e3b4f8891481301770115e8ba4945eea6de`. The **current** demo branch HEAD includes subsequent documentation/new source-only test tooling and must be passed as an exact independently checked SHA; do not mislabel the reviewed demo code commit as the latest branch HEAD.

## 2. Primary implementation / files

| File | Scope |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json` | Proposed immutable source authority; RR5 tuple, 13 native + 3 demo Git file identities via the reviewed C10 pinset, 5 intended native TUs, 9 C exports, six historical custody roles, mandatory zero real-Player coverage and closed authority |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | New read-only Python 3.11 source check: exact proposal/blob, C10 manifest/blob, four distinct clean canonical Git checkouts/commits/branch policy, 16 actual Git blob IDs at HEAD, 5 historical admission/B1 file blobs, exact legacy B1 tuple, and no fake Local/Player evidence |
| `Tools/AssemblyShadow/R03IR/D5Admission/test_d5b_rr5_source_preflight.py` | 27 adversarial unit tests, including wrong native/HybridCLR/package, changed native/exports, historic 14/46 drift, missing custody role, fabricated runtime/Local authority, wrong origin, checkout mismatch/dirty tree, malformed JSON and incorrect source blobs |
| `.github/workflows/r03-b2-d5b-rr5-source-preflight.yml` | Four GitHub repo checkouts at fixed native/HybridCLR/package commits and current demo SHA; run 27 Python tests and read-only source check on Ubuntu/Python 3.11; no Unity/IL2CPP/Player commands |

**Fixed proposal Git blob:** `35ac430e32623e796ccd8bdf0af0052e3dc7fd18`, verified by GitHub Connector readback. **Predecessor reviewed C10 pinset Git blob:** `66b2e83f8cab4debb71af36d4bcd5eecd80b5629`, unchanged. The C10 pinset remains the source of the 13 native inputs, 3 isolated demo inputs, 5 TUs and 9 exports; no parallel altered source-count contract or forced legacy 14/46 rewrite.

## 3. Validation and explicit evidence classes

**Already established before this step:** independent C10 RR5 source-host run [45337986472](https://github.com/night-outlook/hybridclr_demo/actions/runs/45337986472), 4/4 successful **at the old C10 tested source commit only**, not at these newly added preflight files. Do not reattribute that 4/4 result to the new admission code.

**New CI requirement:** source-only workflow `r03-b2-d5b-rr5-source-preflight.yml` must complete successfully **for the exact new source commit** and expose raw log proof of 27 Python tests plus `RR5PinnedGitSourceVerified_NoLocalExecution`. Until the exact run ID/job logs have been independently checked, record `D5BRR5PreflightCI=NotVerified`, not PASS. GitHub Connector readbacks establish that the four new source files are **pushed** and the proposal's Git blob matches its hard-coded reviewer anchor; they do not establish that the script executed successfully. Independently review any CI failures before another push. No B1 or earlier D5-A/D5-B results may substitute.

Additional proof **still missing**: external remote HEAD pinning at a future Local batch, actual complete Unity 2022.3.62f2 C# compilation, IL2CPP/Bee native full translation units, installed source-to-object provenance, GameAssembly/Mach-O symbol and UUID checks, exact fixture method identity, native GC/pinned canary, authoritative PID/argv/exit, P0–P6 failure producers, native B1 first recovery receipt and all 18 D5 real Player cells. `GitSourceVerified` is only a source class, not an installed or executed binary.

## 4. Gates and stopping rule

1. Run and independently inspect the **new** GitHub Actions source-preflight matrix at its own commit. If FAIL, return to Primary for a single focused correction; preserve failed attempts.
2. Request a **separate independent D5-B RR5 source-admission review** of this proposal, Python code, negative regressions and raw CI, particularly its non-escalation property and its actual relationship to the immutable C10 pinset.
3. Only after that review may Primary plan the **next separately authorized** D5 admission/runner stage. The D5-B executable Local handoff still needs independent source/Unity runner review, all historical custody roots, fresh user execution authorization and a new exact-pushed-commit `WEB_TO_LOCAL.md`. This source-only step cannot open it.

**Authority:** `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. Actual Unity/IL2CPP/VM/Bee/GC/PID/Player `NotRun`; all 18 D5 Player cases `NoCoverage`. Do not run Unity, begin D6/H2/M08A/X02/SNAP-01, or claim Human Review Gate approval.