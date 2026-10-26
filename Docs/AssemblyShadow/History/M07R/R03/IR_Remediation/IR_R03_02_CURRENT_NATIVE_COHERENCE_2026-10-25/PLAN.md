# R03 IR-R03-02 current-native candidate — staged Primary/Local plan

**This document implements Primary source-only preparation and defines a potential future focused Local cycle; it does not authorize that cycle.** Current `WEB_TO_LOCAL.md` is CLOSED and no new Local root is allocated.

## Primary work in the present environment

1. Read canonical Assembly Shadow README / current closed handoff / latest f51d Local result and reconciliation, canonical R03 plan/owner D1=A and D2=A, the actual October 8 independent R03 FAIL and its erratum, plus the current October 24 IR re-review-preparation package. Verify exact remote HEADs of all four repositories, canonical branch and GitHub Connector write capability.
2. Verify the actual historical `Tools/AssemblyShadow/R03/source-pins.json` binds older native `74dbdbea80d83923863303bd2b2c0a87f36541b1`, while the current R03 native source in `il2cpp_plus` is `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`. GitHub compare shows 147 native commits / 125 changed paths; do not edit/relabel the old original pin or historical run. Current terminal code source hashes appear in `current_native_candidate.json`.
3. Implement additive, versioned and explicit `current_native_candidate.json` + `current_native_source_gate.py` (no build) with exactly ten actual Git blob identities, strict old+new native distinction, interpreter/package version pins, failure-on-mutation, four separate source roots, zero runtime acceptance.
4. Implement additive `run_terminal_current.py` that runs the source gate **before** `Batch.__init__` creates any output, derives a one-use in-memory native candidate pin, then delegates to unchanged `run_terminal_local.execute(..., batch_type=CurrentNativeBatch)`. Preserve original `Batch.authority` remote/branch/clean checks, original three native builds/five Player witnesses, original S fixtures and all original negative checks. Do not change R03IR Player/corpus/SDK/native production or modify the old native source-pins.json.
5. Add 20 source-only hostile/positive regression tests in `current_native_source_contracts.py`, covering actual ten source blobs and external Git revisions, stale-original-pin refusal, symlinks/aliases, source drift, missing/duplicate manifest rows, no runtime-acceptance promotion, and original five cases/actual batch-type injection. Explicit filename (no `test_` prefix) avoids broad historical `unittest discover`.
6. Add Mac/Linux read-only source CI `.github/workflows/r03-ir-current-native-source-only.yml`, checking out exactly the three external repositories at pinned revisions. Run candidate checks and write reports only under GitHub runner temp. Verify complete job conclusions **and** existing historic R03IR/K workflows after test-discovery collision repair. Preserve prior failed CI runs as real test-only failures; do not rewrite them into green.
7. Publish this design, plan, source review and machine evidence, with complete observed CI IDs/claims. Verify only intended `Tools/AssemblyShadow/R03IR/current_native_*`, `run_terminal_current.py`, `Docs/AssemblyShadow` and one CI workflow are changed. Commit/push and verify exact remote HEAD for all four repositories.

## Explicit separate decision gate — CURRENTLY NOT AUTHORIZED

Before any future Real Local Unity Player operation, Primary must:

- Re-review the 147-commit native drift's transitive generated/installed-source effects, the actual independent IR-R03-02 source findings and the strict three-build/five-Player fixture coverage.
- Complete all possible source/code/tests/scripts diagnostic work, reject source mismatches early and freeze exact current four-repo source HEADs.
- Establish a fresh, isolated, unused Local destination; quantify disk/Unity/SDK capacity and toolchain. No reuse of S, b7e3, c42a or f51d roots.
- Explicitly confirm approval for the **new** real Unity2022.3.62f2 macOS arm64 run (not obtained in this document), then update `WEB_TO_LOCAL.md` with a new, one-time source-bound scope and exit/failure evidence requirements, and push.
- Require at least three builds (feature-ON release/debug and OFF) and five fresh real Player cases, with before/after raw hashes, actual installed source/binary/toolchain SHA, child process PID/start/end/exit, original S fixture byte custody, warning/diagnostic modes, and exact negative/canary/field/first failure oracle. Rejected old type use cannot be inferred from a lack of raw method-invocation records; actually attempt valid methods after terminal poison.
- A fresh success would be **`FocusedEvidenceReadyForPrimaryReview` at most**, not R03/P1 acceptance. Additional generic/initializer/new method-entry paths and IR-R03-01 source/build/process semantic re-review remain. Existing full-stage independent FAIL is not reclassified.

## Review/rollback/stop rules

All source hashes belong to their actual repo paths and immutable commits. A Python host/CI pass certifies ten source bytes and the candidate-overlay structure, **not** native Player safety or all 147 changed native commits. Any CI failure returns to Primary; do not delegate nontrivial repairs to Local. If an independent reviewer cannot cover the 147-commit source-input drift, do not run a Player based solely on a green source gate.

Rollback for this Primary cycle means removing the new *parallel* candidate manifest/tool/test/CI/doc files in a new commit, without rewriting original historical `source-pins.json` or any preexisting R03 source/evidence. On a future failed/restart-required actual Player, terminate/discard only the new isolated experiment process/root after evidence preservation; never in-process reset native global state.

Current state: `IR-R03-02=CurrentNativeGuardSourcePresent_CurrentSourceMatchedPlayerNotRun`; `IR-R03-01=OriginalSProvenanceCorrected_AwaitingIndependentRereview`. Original independent R03 overall FAIL, owner D1=A/D2=A, original S 90/90, b7e3/c42a original FAIL, f51d historical audit-only PASS are unchanged. P1/P2/E0/E1/full P3 open; `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, PureInterpreter disabled. No H2, M08A, X02, Human Review Gate or Local task is initiated.
