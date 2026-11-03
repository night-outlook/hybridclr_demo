# Primary source review — oneuse-G remediation, before new H Local evidence

Date: 2026-11-03 UTC. **This is a Primary source review, not an independent R03 full-stage reviewer verdict.**

| Finding | Prior evidence | Candidate disposition | Remaining real validation |
| --- | --- | --- | --- |
| G-OFF-COMPILE-01 | G OFF C++11 Il2CppException/Il2CppString incomplete on probe=1, feature=0 | Explicit `il2cpp-object-internals.h` and ON-only writer. Host compiler contract compiles complete source in both modes, intentionally fails when include deleted. | Installed Unity2022.3 C++11 OFF compile + actual OFF Player and official 135 installed VM pairs |
| G-ENGINE-02 | 51,865 real reports in500ms after native quit icall called once; watchdog exited71 | Move sentinel to actual `Update` frame, keep exact native failure and once-only quit, add real `atexit` vs failure-only watchdog evidence and V2 fail-closed verifier. | Genuine engine Player: normal termination, original recovery and <=64 real reports/500ms; full Unity owner shutdown still unproved |
| G complete-general sidecars | Three ON Players passed with ~540k full native JSON sidecars, stable post-poison fields | Preserve existing source contracts and 3,932,160-byte full sidecar upper bound, no truncation/global-epoch inference | Fresh three ON Player cases and original semantic verification |
| G installed parity | 135 independent diagnostic pairs, 45 OFF from failed build; official audit Blocked | Keep exact 45 changed VM source roster and official audit dependency on 3 successful builds | Fresh successful3-role audit of all 135 physical source pairs |
| F exact-source CI blocker | Eight of nine workflows missing at F SHA; G all9/18 jobs passed | Retain nine-workflow exact-final-demo SHA requirement and handoff-only trigger paths | H *final* demo SHA: nine actual push runs and both jobs each success |

**Scope and boundaries:** no changes to production terminal guard, counted callbacks, 64/500ms bound, original durable recovery, feature-OFF semantics, original-S archive, old G raw, historical R03 pins or Human Review Gate policy. Native probes remain test-only. A normal `atexit` is strictly a C process-exit signal; it is not a substitute for full Unity Shutdown, coherent whole-VM epoch or GC/RSS qualification.

**Static review observations:** the feature-OFF reporter includes complete object internals while feature-ON-dependent writer is compiled only with feature-ON; the new native test separately compiles the entire translator and rejects dropped include. Source gate requires 11 exact files, including a real frame fixture, and 45 changed VM files (not product-link coverage). Synthetic host oracle rejects old V1, a watchdog-forced false PASS, missing frame phase75, missing atexit marker, >64 counts and invalid first failure. The native collector never emits a synthetic success from the watchdog. The original three ON cases and OFF control remain in the one-use coordinator.

**Execution status at authoring:** source review only, not actual local SDK/Unity execution. CI must be inspected at the exact final pushed demo commit. Any CI failure or missing required macOS/Ubuntu job blocks H dispatch; do not label source review alone as an empirical PASS.

**Risks requiring Local:** `Application.Quit` may still defer/no-op after terminal native reporting, and even a running Update callback may not yield a normal engine exit in500ms; report actual raw as failed, never relax guard/threshold. `std::atexit` does not confirm full Unity lifecycle. Runtime source compiler may expose SDK-specific headers/ABI not reproduced by the narrow mock, especially feature-OFF; actual Unity compiler remains mandatory. The new H-only disk advisory exception is readmission-bound and cannot carry to later runs.

**Disposition:** design/source candidate prepared for focused CI and conditional H one-use Local validation. Original Oct 8 independent R03 FAIL and High IR-R03-01/02 remain open; `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `runtimeAcceptance=false`.
