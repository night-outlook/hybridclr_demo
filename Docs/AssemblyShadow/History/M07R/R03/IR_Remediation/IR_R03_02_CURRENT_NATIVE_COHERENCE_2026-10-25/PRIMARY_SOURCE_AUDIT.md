# Primary source review — IR-R03-02 coherent current-native candidate

**Method:** direct GitHub Connector reads of the exact four repo branches and fixed current source Git blobs; inspection of the actual original `R03IR/run_terminal_local.py` + `R03/run_local.py` dispatch/build/remote authority, current native terminal guards and original R03TerminalPlayer request/result contracts. New Mac/Linux source-only CI authenticates actual checkouts. **Not** an independent R03 full-stage review, actual Unity/IL2CPP compile, Player execution or Human Review Gate.

## 1. Exact actual source and branch pairing

- `hybridclr_demo@<current transport SHA>` on `codex/assembly-shadow-r01b-h1`: original `R03/source-pins.json` blob `9d72a237fb6ecd3efe3267ca89625aa49c61775d`; original `R03/run_local.py` `9aef8093f98fb7f9b5dd395ba4e5c2ed0220276e`; original `R03IR/run_terminal_local.py` `70b1a27f2dbbcad93f67e8caddcf7282ff3afd73`; `R03IR/PlayerProject/R03TerminalPlayer.cs` `598feeec3231707091699d99fbf4428d50b52024`; Unity Editor build source `R03/PlayerProject/R03Build.cs` `90eeccfa30e904955708d11530b99f179584de8c`; native test probe `R03/PlayerProject/AssemblyShadowR03Probe.cpp` `2f13925190a1576738457d8d43f3646a4c7c095f`.
- `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`: `hybridclr/interpreter/Interpreter_Execute.cpp` `2dbdb7527afee7f2546e45f20e6ef93e1bca237a`.
- `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`: fixed package identity at `Batch.authority`; package source/build credentials/Unity installation not exercised in source-only CI.
- `il2cpp_plus@e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb`: `libil2cpp/vm/AssemblyShadow.cpp` `57cf47f964a83973df8296955ccf856b105c595f`, `AssemblyShadowTerminalExecution.h` `33258986c31b2e6ae3af17b8553030482a83aef7`, `Runtime.cpp` `96b914fbeb31c69d649e4076a802de0b6418daa8`. Older historical runner native `74dbdbea80d83923863303bd2b2c0a87f36541b1` differs by 147 commits/125 changed paths in GitHub comparison; it cannot silently certify this current native runtime.

The new manifest `Tools/AssemblyShadow/R03IR/current_native_candidate.json` binds **all 10** relevant existing source bytes to the above exact Git blob SHA-1 values. Its own acceptance flags remain false; no source file may be omitted by editing the manifest because `current_native_source_gate.py` also maintains a hard-coded exact ten-entry allowlist.

## 2. Actual path through the original R03IR runner

The original focused runner accepts an injected `batch_type` and invokes `batch.authority()` **before** fixture generation, three isolated candidate native builds and five new Player cases. Original `Batch.authority` enforces each owning repo checkout, expected SHA, clean worktree, exact origin, branch and remote HEAD. `prepare_project` writes actual per-role `AssemblyShadowSourcePins.json` and `source-inputs.json`; the native build/install verifier requires actual installed source inventory, build receipts, compiler policy, managed baseline fixture hashes and exact final Player architecture.

The parallel `run_terminal_current.py` verifies ten Git source blobs + external HEADs before calling the original `Batch.__init__`, which creates an output root. It then invokes `candidate_pins()` in memory, requiring original `source-pins.json` to remain bound to old `74db...` and replacing only the new batch effective `il2cpp_plus` pin with exact `e1e5...`. It delegates to original `run_terminal_local.execute(..., batch_type=CurrentNativeBatch)`. Its `authority()` still calls original remote/source/clean validation, not a mock or alternative admission. No current-native result is accepted merely because source pins are coherent.

This is a **source-level composition** proof. Actual installed IL2CPP internals, Player linking, compiler warning envelope, post-terminal side effects, process isolation, metadata and failure cleanup remain **NotRun** at the new effective pin tuple.

## 3. Host CI, test interference and resolution

[Source-only CI 40264569824](https://github.com/night-outlook/hybridclr_demo/actions/runs/40264569824) completed **SUCCESS** on `ubuntu-24.04` (job `121384007429`) and `macos-15` (job `121384007834`), both **20/20** positive/adversarial source tests, source-only report `PassedCoherentSourceOnly_NoPlayerOrRuntimeValidation`, and exact ten source blobs. CI checked out actual current `e1e5` native / `4b27` interpreter / `948c` package and source-bound demo fixture; it did not run Unity/SDK compilers or the focused Player.

The initial test filename `test_current_native_source_gate.py` was accidentally discovered by unrelated historic `R03IR unittest discover` workflows, and those runs genuinely failed because custom candidate source-root arguments were missing. To resolve it without changing historic suites or inventing skips, Primary copied the 20 tests **byte-identically** to `current_native_source_contracts.py`, deleted the discovery-colliding old file, and changed the candidate-only workflow to invoke the explicit filename. [Current final source-only CI 40264569824](https://github.com/night-outlook/hybridclr_demo/actions/runs/40264569824) PASS is recorded separately from earlier red attempts. Existing broad historic CI is rerun to ensure no old R03 suite was weakened by the additional code. Do not erase earlier failed CI or claim it was a product/native failure.

The 20 tests cover old/native pin separation, exact source blob checks, git source HEADs, symlinked/aliased parent and leaf, missing/changed source, malformed/duplicated config, false runtime acceptance flags, five original focused cases, original batch-type injection and negative source tampering. All tests run source-only; not one launches a Unity Player.

## 4. What this does and does not establish

**Supported Primary fact:** A coherent **candidate** source tuple has been assembled without changing historical original pins. Actual branch/source bytes are fixed for source-only review, the R03IR original runner has an injection seam for a parallel candidate, and Mac/Linux tests do not observe a source-level mismatch in the ten checked files.

**Not yet established:** native generated-code/install/transitive input completeness across the 147 native commits, new actual Unity2022.3.62f2 macOS arm64 compilation, all three native build configurations, five fresh Player cases, catch-and-later-valid-invocation safety, generic captured/initializer failure paths, independent IR-R03-02 closure, original S IR-R03-01 semantic and generated-source omissions, full RC1–RC6 stage acceptance or H2.

The existing independent R03 **FAIL** remains, as do original source/SDK/Player historical outcomes. Owner D1=A/D2=A scope remains binding. `f51d` is **only** a historical source/host/SDK receipt audit PASS, not real current-native Player proof. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`, PureInterpreter disabled.

## 5. Primary disposition and next review gate

Result: `CandidateSourcesBound_SourceOnlyPreflightPassed_NoLocalRunAuthorized`. This specific old-vs-new native pin blocker is resolved **for source selection**, not for runtime behavior. Additional independent source/process reviewer scrutiny of the 147-commit native drift and a new explicitly authorized, source-pinned Local Player witness are needed before IR-R03-02 could be closed. Original IR-R03-01 remains partially remediated and independently unclosed. The current `WEB_TO_LOCAL.md` stays **CLOSED / NO ACTIVE EXECUTION AUTHORITY**. No H2, M08A, X02, new Player or Local cycle is initiated here.
