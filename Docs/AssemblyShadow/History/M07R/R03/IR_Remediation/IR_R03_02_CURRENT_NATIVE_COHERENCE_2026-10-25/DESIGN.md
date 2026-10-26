# R03 IR-R03-02 — current-native coherent candidate (Primary design)

**Status: Primary source-only candidate, NOT a Local/Player run, independent re-review, or H2.** The original 2026-10-08 independent full-stage verdict remains **FAIL**. The two high findings were `IR-R03-02` (terminal failure did not block a later otherwise-valid business method) and `IR-R03-01` (incorrect original S archive identity and incomplete source/build/process binding). The original S 90/90 are retained; a later f51d historical audit-only PASS authenticates previously recorded b7e3 host/SDK receipts, not current-source Player execution or the full original S identity.

## 1. Canonical authority and previous separate evidence

Four feature repositories/branch `codex/assembly-shadow-r01b-h1`:

| Repo | Native/source bound revision |
|---|---|
| `night-outlook/hybridclr_demo` | exact current HEAD supplied at read/publish; demo R03IR executable fixture code is unchanged and fixed to Git blobs below |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `e1e5be67641f18c4a5b1d5fb35429a6d15aa2edb` |

**Historical R03 focused runner source pin** is `74dbdbea80d83923863303bd2b2c0a87f36541b1`, in unchanged `Tools/AssemblyShadow/R03/source-pins.json` blob `9d72a237fb6ecd3efe3267ca89625aa49c61775d`. The new native candidate is 147 commits ahead (125 changed paths returned by GitHub comparison), including relevant `AssemblyShadow.cpp` and `Runtime.cpp`. A direct one-line overwrite of the historical R03 source-pins.json would destroy source identity distinctions and is forbidden. The resulting new candidate **must** compile/install/link and run a newly built Player before claiming current source matched runtime safety. A source-only preflight cannot prove binary-installation coverage.

Other original source bases remain distinct: S execution `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`; b7e3 original source `49c6b62d38d7668be10004ac1e5a030d74894f09`; c42a audit source `26a4ea22aa0a11f1e86c8d2ac2aa4bd55a308a05`; f51d audit-only source `ea530e59eef38175738e517110c698ebd31bb07f`. None of those historic receipts can be relabeled as current native candidate Player evidence.

## 2. Additive, non-destructive implementation

New files in `Tools/AssemblyShadow/R03IR`:

- `current_native_candidate.json`: exact schema/kind, original native `74db...`, candidate native `e1e5...`, interpreter/package pins, ten exact Git source blob identities, three native build roles and five focused Player witnesses; all acceptance flags false.
- `current_native_source_gate.py`: source-only static/byte check of all ten required original Player/runner/narrow terminal source inputs, original historical pin still `74db...`, and candidate pins. An optional checkout-HEAD mode checks the three external source Git revisions. No SDK compiler, Unity/Player build, extra source files or historical artifact updates.
- `run_terminal_current.py`: **parallel candidate runner**. Before constructing any batch output, it authenticates the ten source blobs and fixed checked-out external source HEADs. It derives an in-memory native candidate from the intact historical `source-pins.json` and then delegates to the unchanged original `run_terminal_local.execute(..., batch_type=CurrentNativeBatch)`. The original BaseBatch `authority()` must still enforce all four exact clean current local branch/origin/remote HEADs before use, and build/install receipts bind native/source packages to their effective tuple. No separate product runtime implementation or weaker bypass path is created.
- `current_native_source_contracts.py`: 20 focused host-only negative and positive assertions, deliberately **NOT prefixed `test_`**. This prevents the many existing `Tools/AssemblyShadow/R03IR/test_*.py` wildcard-discovery suites from running the candidate with missing custom source paths. The candidate-specific CI calls the file explicitly.

**Critical test-compatibility resolution:** An initial file named `test_current_native_source_gate.py` was inadvertently discovered by historical R03/K/R03IR host workflows and failed because its four repository paths were not supplied. Primary retained that CI as a real test-only failure, renamed the candidate to `current_native_source_contracts.py` and deleted the discovery-colliding file, then explicitly invoked the candidate tests in a dedicated source-only CI workflow. Original host test suites are not allowed to gain skips or change their rosters to accommodate the new candidate.

No native runtime, Unity project, production H1/R03 code, original 85-test consumer, S evidence, historical b7e3/c42a/f51d Local records, or original `run_terminal_local.py` was changed. The current test-specific overlay affects **only a future newly created isolated candidate source tuple**.

## 3. Proposed future Player witness — NOT YET AUTHORIZED

The existing `run_terminal_local.py` has exactly **three isolated candidate builds** (feature-ON release, feature-ON debug and OFF), with **five** source-bound fresh process cases:

| Case | Purpose |
|---|---|
| `IR-R03-02-release-baseline` | Catch baseline-owner terminal poison and attempt valid active reflection, delegate and old AOT canary; verify body/field unchanged |
| `IR-R03-02-debug-baseline` | Same in debug native configuration |
| `IR-R03-02-release-type` | A separate type-resolution terminal failure and later valid method attempt |
| `IR-R03-02-off` | Confirm feature-OFF ordinary method paths remain unaffected |
| `IR-R03-02-release-engine` | Controlled actual Unity engine-originated unhandled callback diagnostic/reporting, distinct from direct diagnostics |

The test fixture `R03TerminalPlayer.cs` measures actual pre-terminal method/reflection/delegate/field/canary behavior; after terminal failure it attempts supported valid target entry and asserts no side effects, unchanged first recovery error/world and fixed diagnostic availability. The original S fixture bytes are copied from immutable evidence rather than regenerated. A candidate **PASS** would support only these five concrete cases on Unity 2022.3.62f2 macOS arm64 at exact paired sources/build receipts, never universal interpreter/CLR path safety.

The harness **does not** cover every captured generic, post-publication module-initializer terminal failure, virtual/interface bridge, alternate platforms or full execution-V1 type safety. Those remain explicitly outstanding independent re-review/Primary obligations. The source-only preflight does not test Unity Editor, IL2CPP generated C++, production Player or memory/GC/RSS.

## 4. Boundaries and remaining IR findings

`IR-R03-02`: current native source appears corrected at `e1e5...`: terminal failure predicate before and after method-identity verification, `RequireActiveMethod`, guarded Runtime::Invoke and interpreter nested/entry/delegate/virtual calls; source-only header CI (69 native policy checks) and existing review-readiness CI (20 tests) are supporting **source proof**, not a fresh Player result. Current-source Player still **NotRun**.

`IR-R03-01`: original S authoritative archive is nine-part `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6` (587907380 bytes), distinct from the withdrawn five-part `f4c2a1...` family. Source/build/process semantic re-review and two oversized generated-source omissions remain independently unclosed; none is resolved by the current Player source candidate.

Owner D1=A confines R03 to conservative NativeLayoutAdmissionV1 and defers structural expansion to X02. D2=A retains development performance observations only, no SLA or deferred CPU/RSS acceptance. IR-R03-01, IR-R03-02 and RC1–RC6 require a **new separate independent reviewer** and, where warranted, source-matched Player evidence. A separate user-initiated Human Review Gate follows only **after** actual R03 closure.

**No new Local Validation authority is issued by this design.** `WEB_TO_LOCAL.md` remains CLOSED. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`, PureInterpreter disabled; no H2/M08A/X02/SDK/Player execution starts from this document.
