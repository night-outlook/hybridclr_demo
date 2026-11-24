# D5-B RR5 — Primary source-admission preparation (NOT Local Validation)

**Status:** `D5BRR5Preflight=ExactSourceCIPass_PendingIndependentReview`; `D5BRR5PreflightCI=PassedExactSourceHostOnly`. Date: 2026-11-24 UTC. This is a **new, additive, read-only** D5-B preparation step after [bounded C10 RR5 independent source-producer PASS](D5B_C10_RR5_INDEPENDENT_REREVIEW_2026-11-24.md). It neither reauthorizes D5-B execution nor modifies the previous D5-A / D5-B / B1 admission contracts.

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

**Independently verified new CI:** [GitHub Actions run 45342478424](https://github.com/night-outlook/hybridclr_demo/actions/runs/45342478424), attempt 1, `completed/success` at the **exact new source-code commit** `9962d7463e2200a81856bfb8cb3bbde4dbb7216d`. I retrieved [raw job 138269154590](https://github.com/night-outlook/hybridclr_demo/actions/runs/45342478424/job/138269154590) through the GitHub Connector, not just the workflow badge. The 1/1 successful Ubuntu 24.04/Python 3.11 job shows `Ran 27 tests in 0.005s` followed by `OK`; four checkout records match demo `9962d746...`, native `1268dd417...`, HybridCLR `c3c2320...`, and package `948c0e3...`. The actual preflight JSON returned `RR5PinnedGitSourceVerified_NoLocalExecution` with `checkedNativeAndOverlayFiles=16`, `checkedHistoricalComparators=5`, `compiledTranslationUnits=0`, `actualUnityBuild=NotRun`, `actualIl2CppNativeLink=NotRun`, `realPlayerCellsPassed=0`, `realPlayerCellsNoCoverage=18`, and `remoteBranchAtReview=NotAuthenticatedBySourceOnlyCLI`. `APPROVED_LOCAL_HANDOFF_BLOB=null` and Local/WEB_TO_LOCAL remain closed. **This is a source-preflight CI PASS, not a Local-run or actual Unity/IL2CPP validation.** Do not substitute prior C10 run `45337986472` or historic B1/D5-A results.

Additional proof **still missing**: external remote HEAD pinning at a future Local batch, actual complete Unity 2022.3.62f2 C# compilation, IL2CPP/Bee native full translation units, installed source-to-object provenance, GameAssembly/Mach-O symbol and UUID checks, exact fixture method identity, native GC/pinned canary, authoritative PID/argv/exit, P0–P6 failure producers, native B1 first recovery receipt and all 18 D5 real Player cells. `GitSourceVerified` is only a source class, not an installed or executed binary.

## 4. Gates and stopping rule

1. **Complete:** exact source-preflight CI [45342478424](https://github.com/night-outlook/hybridclr_demo/actions/runs/45342478424) and raw job `138269154590` independently verified (27/27 Python tests, 16 C10 blobs + 5 historical comparators; no Unity). Future revisions require their **own** exact-code source CI; do not reuse this run.
2. **Pending:** execute a separate independent D5-B RR5 source-admission review of this proposal, Python code, negative regressions and raw CI, particularly its non-escalation property and its actual relationship to the immutable C10 pinset.
3. Only after that review may Primary plan the **next separately authorized** D5 admission/runner stage. The D5-B executable Local handoff still needs independent source/Unity runner review, all historical custody roots, fresh user execution authorization and a new exact-pushed-commit `WEB_TO_LOCAL.md`. This source-only step cannot open it.

**Authority:** `APPROVED_LOCAL_HANDOFF_BLOB=None`; `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. Actual Unity/IL2CPP/VM/Bee/GC/PID/Player `NotRun`; all 18 D5 Player cases `NoCoverage`. Do not run Unity, begin D6/H2/M08A/X02/SNAP-01, or claim Human Review Gate approval.