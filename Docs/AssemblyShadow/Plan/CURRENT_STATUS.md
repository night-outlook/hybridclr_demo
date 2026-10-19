# R03/P1 current status — failure-aware command receipts published; one Local source/SDK preflight

**Owner: Primary Implementation.** The prior `20261018-5667` Local return is **PASS / PassedSourceHostAndSDKOnly within 12-component source/host/installed-SDK syntax scope** and is consumed. No new product-runtime acceptance follows. Primary has now published the failure-aware Python tooling, regression coverage, and one source-pinned 13-component Local cycle. Read [WEB_TO_LOCAL.md](../Handoff/WEB_TO_LOCAL.md) for execution authorization and stop boundary.

## Source commits and owner paths

All four repositories use `codex/assembly-shadow-r01b-h1`. Exact feature source pins are:

| Repository | Existing Local checkout | Required source / HEAD |
| --- | --- | --- |
| `night-outlook/hybridclr_demo` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | Tested source commit `d67846e9a28add70046198da9a4fba7e27f0764b`; final Docs-only remote HEAD must equal the accompanying Primary handoff prompt and latest `WEB_TO_LOCAL.md` commit. |
| `night-outlook/hybridclr` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| `night-outlook/hybridclr_unity` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `e29a38f66331ccabe5822a9f83401cd4a2b20c5a` |

Native HEAD retains predecessor `d8a1df3007e93aeb65dd9fe97ab96b4771de8f17` containing a separate inactive owned execution/R02 feature; that feature is NOT claimed covered by the new command-failure contracts. Historical `Tools/AssemblyShadow/R03/source-pins.json` is not changed; native candidate syntax mode uses explicit `e29a38f66331ccabe5822a9f83401cd4a2b20c5a`.

## Completed Primary increment

- Reproduced original timeout output disappearance and outer continuation under an unverified execution lifetime.
- Native Python host-runner failure receipts now record stream availability/completeness, exact captured bytes/hashes and failed RESULT even on missing compiler/postflight source change. Compiled-source claims require actual successful compiler commands.
- Outer 13-component preflight stops immediately on timeout/interruption/unknown lifetime/child-reported unsafe lifetime, writes explicit `NotRun` cells, refrains from later subprocesses/postflight remote verification, preserves a nonaccepted observation inventory. Strict component-result JSON parsing rejects duplicates, nonfinite values and symlink targets.
- Source-bound host harness passed **53/53 unique tests**, with three additional admission refusal checks, all original 12 components kept and native SDK matrix **75 syntax configurations** unchanged. The five positive managed products and the expected OriginalUnsignedCounts negative are unchanged.

This is **Python tooling only**; no native C++ or managed runtime production code was altered for this increment. The focused demo/native command-failure GitHub CI workflows both passed ([demo 39208716350](https://github.com/night-outlook/hybridclr_demo/actions/runs/39208716350), [native 39208403729](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403729)). A separate inherited owned-execution/R02 workflow has one [macOS Clang failure](https://github.com/night-outlook/il2cpp_plus/actions/runs/39208403669), which is a Primary-owned distinct issue and not qualified in this focused batch. Fresh installed-SDK execution remains separate evidence; host mocks do not establish actual Unity execution or native runtime acceptance. [Primary review](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PRIMARY_REVIEW.md) · [publication](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/PUBLICATION.md) · [original evidence](../History/M07R/R03/IR_Remediation/P1_COMMAND_FAILURES_2026-10-19/EVIDENCE.json).

## Next Local assignment and limits

Exactly **one unused source/host + installed Unity2022.3.62f2 official SDK syntax-only cycle**, 13 independently receipted children (new command-failure harness + 12 retained), with 75 actual arm64 C++17 native syntax configurations, five managed products and original expected-negative control. All four checked-out repos must match current remote pins, be clean, preserve consumed evidence and SDK bytes, use one fresh set of external roots, run once and stop. No Editor, Player, Test Runner, linked runtime, new terminal experiment, automatic retry or Human Review Gate is authorized. Local only records observations in `LOCAL_VALIDATION.md`, `RETURN_TO_WEB.md`, and designated additive checkpoint; substantive work remains Primary-owned.

## Immutable historical evidence and remaining production work

`20261018-5667` remains PASS 12/12; `20261016-3dc9`, `20261016-f598`, `20261016-0620` remain source/SDK PASS, `20261016-0a0b` remains source/SDK FAIL 9/10. SNAP-01/N/M/K/I/E FAIL, historic R02 source-fingerprint FAIL, strict original S custody Blocked, R03 independent full-stage FAIL/rereview NotRun all unchanged. Original V1 slot14 >262144 and native engine 51,213 reports in 500ms remain unresolved. Native logger/GC/recovery/canary and V1/V2 budgets remain unchanged.

P1 coherent all-VM epoch/ABA, pointer ownership, complete R02/execution live capture/getters, type-key/class memory bounds, GC/RSS and real Shutdown/lock proof still Incomplete. P2 authenticated native/C# V2 file transaction and semantics NotIntegrated. E0 actual StandaloneOSX engine-owner safe point Blocked/Unavailable; E1 BlockedByE0; full P3 linked Player/runtime acceptance incomplete. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No automatic milestone advance.
