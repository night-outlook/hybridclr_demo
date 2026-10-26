# R03 one-use current-native + original S — Primary execution plan (2026-10-26)

Status before code publication: Primary implementation and source-only host CI preparation. Previous WEB_TO_LOCAL was CLOSED. This plan alone does not authorize Unity or Local execution; only the updated, pushed WEB_TO_LOCAL for this exact cycle does.

## P00 — Authority and hard boundaries (Primary)

- Use GitHub Connector on the four canonical night-outlook repositories, all branch codex/assembly-shadow-r01b-h1. Confirm read/push permission, current remote HEAD and disposable-branch write/read smoke test. Do not modify source, branch or uncommitted state except intended additive demo changes.
- Read Docs/AssemblyShadow/README.md, stage R03 plan, Human Review Gates, original independent October 8 FAIL/erratum, D1=A/D2=A, original S provenance correction, current source candidate design/plan and current closed/f51d handoff reports.
- Freeze external pin triple 4b2774 / 948c0e / e1e5; keep old native 74db source-pins and original S/f51d/b7e3/c42a evidence untouched.
- Separate original-S read-only worktree at fc55 from four live checkouts. One fresh external Local root, never a suffix/retry of earlier S/82dd/e1e5/6c72/b7e3/c42a/f51d.

## P01 — Coordinator and diagnostics (Primary)

Add Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py. Functional contracts:

- Admission must validate all source roots and exact remote identities plus ten candidate source blobs and 42 VM source files before output creation. Refuse symlink/alias/output inside any workspace checkout, missing or noncanonical Unity executable, non-macOS ARM64 host, insufficient disk and dirty original-S fc55 checkout.
- Explicit host regression suites must execute against exact current sources, maintain source-only labels and block Player launch on source/oracle failure; do not alter historical suites or test discovery.
- Reuse audit_s_provenance.py plus audit_s_process_joins.py on full original S evidence once; never run a historical S Player. If archive audit fails, process joins are Blocked, current real Player can independently proceed after source gates, but combined result is ReturnRequired.
- Reuse run_primary_host_preflight.py for additional bounded diagnostic-native/host scope. Do not equate a native C++ syntax compile with official Unity SDK installation/Player.
- Recheck source and original S identities before/after delegating exactly once to run_terminal_current.py; retain all three role builds and five real Player case results. Validate the actual child LOCAL_BATCH_RESULT.json and seal, not only exit 0; require 3/3 and 5/5, exact tuple and all non-acceptance flags.
- After a genuine successful five-Player result, run current_native_install_audit.py once: compare all 42 changed VM source blobs to three actual role-specific installed native trees, bind build-v2 before/after inventories and exact Release/Debug/OFF/config/source pins. Require 126 physical source/install byte pairs and explicitly mark generated C++ closure and binary linkage NotProven by that parity test.
- Preserve one-use invocation marker, stdout/stderr, PID, exit/timeout and timestamp/hash per component; finish with explicit per-component status and coordinator-only manifest. A failure never mutates prior outputs and never turns historical FAIL to PASS. No automatic batch retry, no silent cleanup, no unbounded subprocess waits.

## P02 — Source and adversarial host tests (Primary)

Add current_native_cycle_contracts.py, invoked explicitly (not test_ discovery). Cover at least:

- absent canonical external output vs existing, symlink alias, repo/workspace-contained, relative paths and original-S==live demo;
- exact pins/forty-digit demo source, stale source gate, omitted changed native VM file and source-only non-acceptance;
- subprocess receipt/hashes/retained failures and duplicate one-shot name refusal;
- fabricated or missing native batch role, case, seal, source tuple, terminal/fixture proof or acceptance flag;
- all component statuses necessary for final focused readiness, failure of even one to ReturnRequired;
- strict macOS ARM64 actual-run gate, no source-discovery collision or original-history cleanup.

CI: macos-15 and ubuntu-24.04 read-only workflow with exact native/interpreter/package source pins, run 20 coordinator contracts + 15 new installed-native parity contracts + existing 20 source gate + 27 synthetic real-verifier oracle + 12 changed VM files + original S host contracts. CI is not original S reconstruction, Unity compilation or actual Player.

Perform static source/diff review of code and workflow; if CI fails, make bounded Primary repairs and re-run. Do not change product/native C++, interpreter, package, historical R03IR Player source or evidence merely to make CI green.

## P03 — One fresh Local Validation cycle, not Primary execution

Local inputs:
- four repositories in an isolated, clean real macOS Apple Silicon workspace, branch codex/assembly-shadow-r01b-h1, exact final pushed commits from the handoff;
- a separate clean historical fc55 demo worktree and complete original S checkpoint;
- Unity 2022.3.62f2 executable path actually discovered and checked on the Local machine;
- one fresh, previously nonexistent output root outside all sources; at least 20 GiB available;
- historical local outputs remain immutable and are not execution inputs for the new Player (except original S committed fixture bytes checked by the existing runner).

Execution: one new coordinator invocation documented in WEB_TO_LOCAL, no retries or authorization of other stages. It produces source tests, original S historical audit/process crosswalk, native host diagnostic output, then at most one real three-build/five-Player witness using the current e1e5 native. Inspect and preserve generated/installed Unity SDK files, actual build receipts/compilation and linked Player identities, launch PID, raw and verification records, stdout/stderr, original first failure and method body-field/canary. Require native/VM physical installation source provenance beyond host-only Git blob checks.

Return:
- new exact output root and coordinator RESULT.json plus COORDINATOR_MANIFEST.json;
- all ten stage INVOCATION/RESULT/log receipts, original audit.json, process-joins.json, native host RESULT.json, installed-native-vm-parity.json (42 x 3 if Passed) and current-native LOCAL_BATCH_RESULT.json and seal;
- evidence manifest hash, representative raw receipts and failed/blocked logs, original S source/worktree after-clean status and four remote heads;
- Local-owned LOCAL_VALIDATION.md with Passed/Failed/Blocked/NotRun/Unavailable and RETURN_TO_WEB.md for any nontrivial finding. Commit and push factual checkpoints. Do not edit production code, re-run consumed roots, invoke independent R03 review or H2 automatically.

Success of all components can yield FocusedEvidenceReadyForIndependentReview only, not product acceptance. If a stage fails, preserve exact partial data and return to Primary; no local repair of design or source semantics.

## P04 — Independent R03 review (not part of new Local execution)

After Primary has reconciled returned empirical evidence, a separate human-initiated independent reviewer must examine design → plan → four-repo sources → exact generated/installed Player identities → old original S source/build/archive/process chain → current post-poison positive/negative cases, claim-by-claim RC1–RC6, missing generic/initializer/virtual/interface coverage, resources, M01 NoCoverage and D1/D2 historical risk. Return IR-R03-01 and IR-R03-02 separate Fixed/NotFixed/NeedsEvidence/ScopeDecision dispositions and an actual PASS/FAIL/BLOCKED full-stage verdict. Retain original October 8 FAIL verbatim.

Do not mark R03Accepted or ReadyForHumanReviewGate until independent exit conditions truly pass. H2 is not started by Primary or Local.
