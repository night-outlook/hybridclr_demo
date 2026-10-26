# R03 current-native and original-S one-use Local cycle — design (2026-10-26)

**Primary owner; R03 only.** This cycle addresses independent R03 findings IR-R03-01 and IR-R03-02. It does not start H2, M08A, X02, protected SNAP-01, deployment qualification, or another milestone. The October 8 independent R03 full-stage FAIL remains authoritative until a separate independent review reaches a new verdict.

## Problem and objective

Original S passed 90/90 historically, but the nine-part 587,907,380-byte archive and related process/build/Player relationships still need independent semantic review (IR-R03-01). The current native terminal guards are source-present at il2cpp_plus e1e5, but actual source-matched macOS arm64 Unity 2022.3.62f2 Players have not run (IR-R03-02). Historical focused R03 source-pins still bind older native 74db and must not be rewritten.

Prepare a **new, one-use** Local cycle combining new read-only analysis of historical S evidence and a freshly built current-native three-build/five-Player witness. Evidence is collected in distinct subroots and cannot be used to retroactively relabel failed or consumed runs.

## Immutable sources

Four working repositories on branch codex/assembly-shadow-r01b-h1:

| Repository | Fixed source pin |
| --- | --- |
| night-outlook/hybridclr_demo | latest pushed demo handoff HEAD, remotely verified and supplied in final Local prompt; do not confuse with code-only commit anchor |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de |
| night-outlook/il2cpp_plus | e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb |

Separate immutable original S Git worktree: hybridclr_demo at fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b. Historical S executed at demo 29bb3d4a39bf8a2f23be404f77535aaba3485bfc with original native 1cf87f8209790f9fb2ebec97487dc1990ccd56c5. Do not build a current Player from original S native.

Owner scope D1=A: conservative NativeLayoutAdmissionV1 only; structural expansion deferred to X02. D2=A: performance results observational; four contaminated certificates stay Failed. Forty-two verified native VM Git blobs do not establish binary inclusion or runtime safety.

## One-use stages and evidence

1. **Zero-write admission.** Check real canonical workspace, four exact clean owning Git checkouts, branch, live remote HEAD, ten actual source blobs, 42 changed native VM bytes, original S worktree at exact fc55 and clean, arm64 macOS Unity executable, at least 20 GiB available, fresh disjoint external output root. A failure creates no new batch root or Player.
2. **Source/host regressions.** Explicit existing 20 source/pin tests, 27 actual-verifier synthetic oracle tests, 12 full native VM source tests and original-S host contracts. All are test-only; any failure prevents new Unity Player execution.
3. **Original S archived proof.** Existing audit_s_provenance.py authenticates the original nine-part archive, full index and 90 ledger cells. Existing audit_s_process_joins.py authenticates 59 archived Player/process joins. This is new read-only analysis of older evidence, not a new S runtime run or an independent full semantic reviewer verdict. The withdrawn five-part archive is never used.
4. **Native source-host diagnostics.** Existing run_primary_host_preflight.py executes native diagnostic stream, codec, transaction, legacy sink, strict and sanitized host compilation where available. Retain separately even if the real Player still runs.
5. **Actual current-native Unity Player.** Recheck exact source and remote authority immediately before calling unchanged run_terminal_current.py exactly once, inside a fresh subroot. Its existing build/install/arm64 checks and five-case oracle must verify three new builds (release/debug/OFF) and five fresh Players (release/debug baseline poison, type poison, OFF, engine-unhandled). Positive precondition, actual post-poison reflection/delegate/AOT canary attempts, absence of side effect, original failure retention, logs and owned process identities are mandatory. Coordinator separately validates the actual sealed Local batch receipt, 3/3 and 5/5, not just child exit code.
6. **Postbuild installed VM parity.** New read-only current_native_install_audit.py checks all 42 current changed native VM source files against the physical installed Unity native tree for each of release/debug/OFF, verifying the build-v2 before/after file inventories and exact source roles (126 source-installed pairs). It refuses missing, mutated or symlinked files. This is physical installed byte parity; it expressly does NOT assert that each header/source was transitively compiled, linked or executed. Fifteen synthetic host tests independently exercise tampering and scope limits.
7. **Custody and stop.** New per-step invocation, argv, timestamp, PID, exit, timeout, stdout/stderr hashes, independent audit/Player child roots, postflight clean Git/remote check and coordinator-only manifest. No retries, no historical file rewrites or shared child output. If any required step fails, final outcome is ReturnRequired; partial evidence remains.

Additive Primary files: Tools/AssemblyShadow/R03IR/run_current_native_validation_cycle.py, current_native_cycle_contracts.py, current_native_install_audit.py, current_native_install_contracts.py, one Mac/Linux source-only CI workflow and Docs/AssemblyShadow design/plan/handoff. Both Python files avoid test_ discovery prefix; actual Local execution requires explicit current WEB_TO_LOCAL authorization.

## Important nonclaims and independent review

IR-R03-02: source-matched Player evidence must prove *actual* entry attempts after caught poison, source-to-installed-native/build/binary pairing, stable terminal reason and absent body execution. Five fixed cases do not cover captured generic, module initializer, every AOT crossing or interface/virtual entry. Do not promote five-case evidence into universal RC3 proof.

IR-R03-01: full archive/90-cell/59-process checksum and typed crosswalk do not by themselves prove original source/build/Unity Player runtime semantic relationships. A separate independent reviewer must inspect original generated C++ method-pointer and invoker omissions, old source-build-process path, resource ABI, M01 NoCoverage, remaining RC1–RC6 claim-by-claim scope and D1/D2 deferrals.

Historical b7e3 and c42a overall Local FAILs stay FAIL, f51d remains historical audit-only scoped PASS. No P1/P2/E0/E1/full P3 stage is closed.

Failure/rollback policy: no --skip or force correction, no Local non-trivial source edits, no retries of old/consumed roots, no auto-recovery of poisoned processes. Return defects with raw receipts to Primary. Revisions and retries require another explicitly pinned and authorized one-use batch. Rollback the additive coordinator/CI/docs using new Primary commits only; preserve history.

**Maximum combined result:** FocusedEvidenceReadyForIndependentReview. Never R03Accepted, H2Passed, ReadyForHumanReviewGate, qualificationApproved, runtimeAcceptance, or PureInterpreter enabled. A genuinely separate independent full-stage R03 PASS and user-started Human Review Gate remain prerequisites to H2 and subsequent milestones.
