# IR-R03-02 — terminal method entry remediation

**Primary Implementation design / implementation checkpoint. Not a full-stage PASS, not an independent re-review.** All four repositories remain on `codex/assembly-shadow-r01b-h1`. Original S/R/Q/P/O/N and independent FAIL review records are immutable.

## Defect and exact correction

Before this change, `AssemblyShadow::AssertMethodIsActive` could return true for an otherwise valid method after the transaction had already entered Failed or FailedAfterCommit. The method-identity proof did not also enforce the terminal *business execution* predicate.

The native correction is in `night-outlook/il2cpp_plus/libil2cpp/vm/AssemblyShadow.cpp` with lock-free policy `AssemblyShadowTerminalExecution.h`. `AssertMethodIsActive` now denies terminal calls before any class-use observation or metadata lookup, and checks again on its original success path to catch a racing terminal publication. The same decision feeds `RequireActiveMethod`; the latter never turns a prior failure into a new root cause. Actual interpreter, nested, virtual/delegate and reflection entry call sites continue to use the existing common method guards. No stage, image resolution, layout admission, ownership or source-roster feature is relaxed.

`TerminalForBusiness` treats Failed/FailedAfterCommit as terminal and also catches durable failures that race the state store; Disabled/OFF without a transaction is not blocked. Original first-failure source fields remain unchanged; a terminal-state rejection when `s_typeFailure` is absent does **not** synthesize a new `InternalError` to overwrite an initializer failure in recovery diagnostics.

### Fixed diagnostic exception construction

The original managed error constructor uses `Runtime::ObjectInit` and `Runtime::Invoke`, so naively blocking *all* methods at terminal state could recursively block creation of the very exception being raised. A thread-local scoped construction allowance permits **only zero-parameter, nongeneric, instance `.ctor` methods of exact physical corlib `System.Object`, `System.Exception`, `System.SystemException`, and `System.InvalidOperationException`**, not arbitrary callbacks, user methods or interpreter IL. It is active only around the native diagnostic error creation, not around a public business call. A nested diagnostic-construction attempt fails natively rather than recursively creating another managed error. The ordinary private/staging restriction in `RequireUserCodeAllowed` remains intact.

Do not widen this method allowlist without direct compiled native/Player evidence. A method-identity guard does not claim that every direct AOT-to-AOT call (outside common dispatch boundaries) is retroactively instrumented. The supported guarantee under review is the stated common business-entry paths.

## Verification inventory

- `il2cpp_plus/tools/r03/terminal_execution_tests.cpp`: pure native policy tests, positive call before poison, post-poison side-effect denial, the fixed diagnostic constructor condition, ordinary Disabled/OFF, and a cross-thread poison observation. The host test makes **no** claim to execute actual AssemblyShadow.cpp or managed IL.
- Native workflow `.github/workflows/r03-ir-terminal.yml`: Linux/macOS standalone C++ compilation and exact source-integration contract checks.
- New **parallel** IR-only Unity Player file `hybridclr_demo/Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs`; the original R03Player and its 90-cell S evidence remain unchanged. The fixed original R03 native overlay has opt-in bit 2 for a caught baseline-owner guard and a test-only type-resolution stimulus. Original bit 0/1 output schemas are unchanged.
- New one-shot isolated `run_terminal_local.py`: exact-pinned host fixtures, three native builds (release ON, debug ON, OFF) and four **fresh-process** Players: release/debug caught baseline owner, release synthetic type-resolution boundary, and OFF ordinary control. It binds Player argv/PID/request/DLL/build/source/raw receipts and refuses reused outputs. The verifier requires an *actual attempted* post-poison active reflection/delegate method, an AOT reflective canary whose counter must not increment, pre-poison positive calls, unchanged first recovery diagnostics, and fixed diagnostic availability.
- `test_terminal_contract.py`: host-only negative mutations prevent false PASS from missing attempt markers, numeric/boolean substitution, missing process/bindings, stale recovery or extra AOT effects. `R03IR/test_audit_s_provenance.py` separately covers the original archive correction.
- `r03-build-api.yml` is requested to compile the IR C# witness against the exact pinned package and official Unity 2022 SDK and attempt production native translation-unit compilation. This does not execute a new Player.

**Explicit not-covered cases:** a genuinely captured-generic failure and real post-publication failing module initializer each need their own exact-source Player witness. The type-resolution stimulus invokes the real production `FailTypeResolution` with test-only error input; it is not misrepresented as an organically malformed metadata graph. Old S C04 does not record post-poison attempts and is not promoted into this new evidence.

## Acceptance sequencing

1. Verify exact latest pushed heads and all source pins; require clean owning Local checkouts, real Unity/IL2CPP source build and fresh disk/transport admission before any Player.
2. Run the new `run_terminal_local.py` **once** in a fresh external diagnostic root only after the source-bound CI/native code and script contracts are verified. Capture raw failures, no phase retry or history cleanup. This is **four focused Players**, not a rerun of S's 90 cells.
3. Primary reconciles every terminal path and addresses any functional defect; add the still-missing genuine generic/initializer cases and any broader impacted runtime regression that evidence shows necessary.
4. Separate independent reviewer inspects both IR-R03-02 code/evidence and IR-R03-01 provenance correction. Only after findings close can Human Review Gate H2 be separately considered.

**Current flags remain false:** `R03Accepted`, `H2Passed`, `ReadyForHumanReviewGate`, `qualificationApproved`, `fullLegacyRegressionAcceptance`, PureInterpreter expansion. Owner D1=A/D2=A remain recorded. X02/M08A never begin automatically.
