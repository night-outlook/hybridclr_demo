# Primary Implementation → Local Validation — CLOSED (oneuse-09 consumed)

Date: 2026-11-09 UTC. **No further Local Unity build, Player, runner, repair, cleanup, or reuse of any previous output root is authorized.** This is a closed handoff, not an unconsumed execution ticket.

## Latest authoritative Local result and ownership

- Original oneuse-09 executed source: hybridclr_demo `bb5fce9c15450e68c6341d88270fbc30dd7b9738` on `codex/assembly-shadow-r01b-h1`.
- Local evidence publication source: hybridclr_demo `97cd47e06a837569ff62c4ac7744117d22966126`.
- Other execution source SHAs: hybridclr `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`; hybridclr_unity `948c0e3b4f8891481301770115e8ba4945eea6de`; il2cpp_plus `41764ae1eeefb33b05966e7f7676e52aae39c340`.
- Local result: **Focused captured-generic A2 PASS** — one authorized 19-cell run, one Unity2022.3.62f2 macOS ARM64 IL2CPP build (0 errors/1 warning), three distinct Players exit0. Initializer control Commit0/state6, initializer failure Commit19/state9 after actual Bi4 callback, captured-generic real physical Methods.R03.Node in stable AOT `method_inst` with state6 after inflation, native first error15/state9, postterminal Runtime::Invoke threw and unchanged counter1→1.
- Original evidence: `Docs/AssemblyShadow/History/M07R/R03/local-validation-captured-generic-20261109-oneuse-09/` with LOCAL_RESULT.json, Local evidence/native raw, source-specific commands, complete custody and 509-member product seal. Local-owned `Handoff/RETURN_TO_WEB.md` is the full handoff; `Handoff/LOCAL_VALIDATION.md` is empty in Git at publication and its contents must not be invented.
- Previous **oneuse-08** is permanently historical `PrerequisiteBlocked/NotRun` with 0 builds/Players and original two absent roots. Previous oneuse-07 remains a distinct focused initializer PASS. All original source/evidence/retirement verdicts are immutable.

## What Primary has completed since receipt

- Added source-bound `Tools/AssemblyShadow/R03IR/captured09_publication_audit.py`, negative `test_captured09_publication.py` and dual-OS `.github/workflows/r03-ir-captured09-publication.yml`. The source-only crosscheck revalidates selected Git-published raw, 19/19 cells, build, original source/CI identities, native phase/recovery, and actual captured error15 **without** rerunning Unity or claiming full binary custody.
- Added the **inactive host-only** `NativeDiagnostics/FirstFailureFreezeV2.h` and `first_failure_freeze_driver.cpp`, with dual-OS C++11/17 host regression workflow `.github/workflows/r03-ir-first-failure-freeze-host.yml`. This does NOT observe an actual native VM first error or integrate native diagnostic V2.
- Read the [Primary captured09 reconciliation](../History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/PRIMARY_RECONCILIATION.md) and [staged native V2 design/plan](../History/M07R/R03/IR_Remediation/POST_CAPTURED09_2026-11-09/B_NATIVE_V2_FIRST_ERROR_DESIGN_AND_PLAN.md).

## Exact current responsibility

**Primary Implementation**, not Local Validation, owns the next work: source-level B1 integration of the actual VM first-error origin with bounded freeze semantics, B2 exclusive descriptor-relative V2 transport, B3 global epoch/source-lifecycle analysis, then new reviewed source/host CI and eventually a **new** one-use Local handoff. Original S provenance and remaining RC/P/E obligations stay open.

No new Local cycle exists. No oneuse-09 replay, historical root reconstruction, unverified SDK substitution, H2/M08A/X02/SNAP-01 or self-approval of Human Review Gate.

## Source and acceptance boundary

Current Git branch: `codex/assembly-shadow-r01b-h1`. The exact **current** demo remote HEAD must be independently checked when resuming Primary work; it is *not* the historical oneuse-09 execution SHA. The other three remote heads remain at the pinned revisions above unless independently changed in a future scoped project handoff.

Original first V1 captured error15 proof does not establish complete NativePreopenedSnapshotV2, native-origin first-error freeze, whole VM epoch, exception type, managed shutdown, GC/RSS, original S complete compiler/object/link/Player provenance, universal direct AOT denial or whole R03 acceptance. The 17 owner-retired roots/40 duplicate paths remain `Unavailable/PermanentlyDeleted`, with historical strict custody `Blocked`.

`R03Accepted=false; H2Passed=false; ReadyForHumanReviewGate=false; runtimeAcceptance=false; qualificationApproved=false; fullLegacyRegressionAcceptance=false`; PureInterpreter disabled. Independent full-stage R03 verdict remains FAIL, High IR-R03-01/02 open.
