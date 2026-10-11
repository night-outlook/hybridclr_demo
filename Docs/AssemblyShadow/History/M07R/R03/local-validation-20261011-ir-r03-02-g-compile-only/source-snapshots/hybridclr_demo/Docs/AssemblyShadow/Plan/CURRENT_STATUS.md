# Current Status — IR-LOCAL-COMPILE-01 repaired; G-COMP next

## Owner and earliest unfinished gate

**Next owner: Local Validation for one fresh G-COMP compile-only attempt.** The immediate fixture defect is repaired and verified on macOS/Ubuntu. The earliest unfinished Local gate remains official Unity 2022.3.62f2 managed/native SDK compilation, after all fresh prerequisites. No Unity launch, Player build, Player, runtime scheduler or Human Review Gate advancement is authorized.

Read [G-COMP handoff](../Handoff/WEB_TO_LOCAL.md), [correction](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/README.md), [source-bound CI evidence](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/CI_EVIDENCE.json) and [exact G procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/G_COMPILE_ONLY_PROCEDURE.md).

## Evidence states — keep distinct

| Evidence | State |
| --- | --- |
| F-COMP source at c5662700; Local publication a9483a6e | PrerequisiteBlocked; scratch tests 3 Passed / 5 failures / 2 errors of 10 |
| F-COMP subsequent native host checks and 69 policy checks | NotRun |
| F-COMP official managed and 55 native configurations | NotRun; no compiler-script invocation or SDK scratch creation |
| F-COMP before admission custody scan | NotRun |
| F-COMP independent after custody | ScopedHistoricalLossStable: 339,367 survivors, 77,477 unchanged missing identities, zero problems from 416,844 entries |
| F-COMP installed SDK after verification | Passed; 2,113 files unchanged; Unity/Player launches zero |
| Primary corrected fixture CI | Run 38123748124, source e36ab83b: 20 Passed on macos-14 and 20 Passed on ubuntu-24.04; no failures/errors/skips |
| G-COMP Local prerequisites and compilers | NotRun until this new assignment is executed |
| Historical strict S custody | Blocked; four original installed native roots Missing |
| E runtime | FAIL: 11 Passed / 3 Failed cells, three ON SIGSEGV, OFF Passed; required ON semantic proofs and originating error Unavailable |
| Independent R03 full-stage / re-review | FAIL / NotRun |
| Acceptance and later-stage gates | All false; PureInterpreter expansion disabled |

The independent F after audit does not grant an unrun before admission. The new scratch CI is not a compiler or runtime test and does not reclassify F-COMP or E.

## Change and exact pins

Only executable change since Local publication `a9483a6e2212701cfedcf93faeb0e71ce82b73ca`: `Tools/AssemblyShadow/R03/test_native_validation_scratch.py`. Its owned fixture root now uses `.resolve(strict=True)`; a second inherited cohort runs the same ten controls under an explicit symlink-backed temporary parent. All original test bodies/expectations stay intact. No TMPDIR/global-temp change, platform skip or guard relaxation.

Validated test source commit `e36ab83b969f8ba8f9f4cc21fc8bb6c447d7fa2f`; test Git blob `5e58c14b5147ee591dda34d802f78b98d36cbaf7`. Production native_validation.py remains blob `15282b61dda3f61106913ce9e2973cc87d76c23d`. Source pins, managed compiler/Player, native code and historical evidence are unchanged. Final publication is a Docs-only descendant of e36; obtain latest exact demo HEAD from the final Primary prompt and verify it remotely.

All owning checkouts are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>` on `codex/assembly-shadow-r01b-h1`. Non-demo pins remain `hybridclr@4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, `hybridclr_unity@948c0e3b4f8891481301770115e8ba4945eea6de`, `il2cpp_plus@c386cdd1e8942561f1d1e1fada52d21ca524f174`.

## Next bounded action

Use only the new `20261011G-canonical-temp` preflight/ManagedAPI/NativeSDK/Scratch roots after proving all absent and nonaliasing. Freshly pass 20 scratch tests, prescribed native host checks and 69 policy checks; authenticate official installed SDK/compiler inputs and original C/E/F checkpoints; complete before-custody admission. Run one managed script, then one 55-configuration native syntax script only if all earlier stages pass. Reverify installed SDK and independent after custody, publish the G checkpoint and return to Primary. Stop on failure, retain partial evidence, no F/E retry, source edits, TMPDIR workaround or root substitution.

Compiler results may reveal remaining source defects; neither scratch CI nor G compilation success grants runtime execution. Any future runtime assignment requires a separate Primary review/handoff. IR-LOCAL-RUNTIME-01, IR-R03-01, captured-generic/initializer and true engine-originated reporting coverage remain unclosed.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`. Preserve S/R/Q/P/O/N/A/B/C/D/E/F exactly; no H2/X02/M08A or PureInterpreter expansion.
