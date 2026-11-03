# Primary source review — H engine termination return and oneuse-I candidate

Date: 2026-11-03 UTC. **Primary Implementation source review, NOT an independent R03 full-stage review.**

## Immutable evidence checked

- H Local exact execution: demo `3e838edf8995e40058f3bc6c42f071446a0be821`, native `cdd3f7bc671880052e4f55ae4c1cd75b99a603e1`; independent published return demo `d49ad3e113b67b300381e6af904ed1d343005e7e`.
- H three real C++11 builds all Passed; four semantic Players Passed; one engine Player Failed, 55,656 unbounded reports/514ms, no atexit, watchdog exit71. Original terminal failure13/recovery and frame phase75 authentic.
- H actual Player.log line56 denied `UnityEngine.Application.Internal_ApplicationWantsToQuit` after one native quit request/return; its actual Unity native caller's behavior remains closed-source.
- UnityCsReference `2022.3.62f2` `Application.cs` (read-only official fork blob `5df54a6f3cba20670a68d740d6f1dcddf42e4c1b`) establishes exact private static signatures, AOT namespace, wants true→continue and void quit notification; official 2022.3 API documentation confirms quit can be cancelled by false wantsToQuit.
- Earlier G/E/F/H results remain unchanged. H's independent 135 diagnostic source pairs do not confer an official installed audit PASS; historical G OFF compiler FAIL remains, while H empirically verified its correction.

## Implementation and risk review

| Finding / contract | Primary disposition | Independent empirical requirement |
| --- | --- | --- |
| H native Quit called but Unity continues | Exact two native owner-only lifecycle responses in `AssemblyShadowTerminalReporting.h`, gated by test-only macro, original sentinel/owner request/immutable recovery and FailedAfterCommit | Unity I must show actual wants decision true, optional typed quit notification observed as required by focused oracle, and real `NativeAtexit` rather than watchdog |
| Ordinary post-terminal callback denial | No change to ordinary `AssemblyShadow::RequireActiveMethod/Class`; exact physical nongeneric UnityEngine.CoreModule/class/signature filter; preallocated pinned Boolean or void; no managed body | ON post-poison canary/field/entry/recovery cases and engine callback proof remain valid, no unrelated method body permitted |
| Potential name-only bypass | Host C++11 classifier compiled from real native header with positive and wrong name, class, assembly, generic, static, params, return, active-state and unarmed negative tests | Real installed SDK C++11 ON/Debug/OFF builds; source/host mocks cannot stand in |
| H failed engine count/timer | Actual real counter unchanged, bound64/max500ms unchanged, terminal reporter/native watchdog unchanged; two distinct uncapped native decision counters added to V2 raw | I must preserve actual counts/timing/first failure even if >64 or timeout, and fail correctly |
| H official installed parity blocked | Repaired independent read-only parity admission: sealed exact-source batch, three genuinely successful build receipts, exact full repo metadata; can report 135 source pairs even if a Player is Failed, without upgrading Player | I official audit must authenticate all3 installed build roles and report original sibling Player verdict verbatim |
| Latent reduced repository-tuple mismatch | `current_native_install_audit.py` now checks complete source tuple including schema, phase, branch, runtimeAcceptance instead of omitting these fields | Real Local audit source identity must match actual batch and all receipt/source file bytes |
| Historical primary host workflow unintended drift | The old `run_primary_host_preflight.py` was restored byte-for-byte to prior blob `2d51be157b94a47ac19d1061d0066c1f98dbc177`, preserving historical purpose; new owner source host tests execute in the **current-native combined CI** | Preserve original-S/historical workflow source authority; no reuse of old CI failure as current source acceptance |

## Host evidence and restrictions

At native `il2cpp_plus@41764ae1eeefb33b05966e7f7676e52aae39c340`, the initial current-native demo source `6d7c308cdbade5c2caaf28436bcd7e32a829dd7a` had all seven triggered CI workflows `completed/success`, including actual C++11 native-owner method matcher and ON/OFF probe TU host tests. Current-native demo `24bda74d61552bc8d8ad640f875ec44241a72a70` passed its combined host workflow after independent build-parity changes. Supplemental `r03-primary-host-preflight.yml` at this intermediate SHA failed because that *historical* workflow expected old native `74db` while its source checkout used the active I branch; the incidental modification of the historical helper was reverted to its exact prior Git blob, not used to justify any acceptance. These are scoped source/host results only. The final I handoff must independently verify **nine** mandatory workflows at one **final** demo commit across both OS jobs; no ancestor substitution.

The native owner callback's bool `true` permits Unity's quit decision without invoking managed events, while `Internal_ApplicationQuit` void response skips managed token-cancellation. Thus even a future scoped `NativeAtexit` PASS cannot prove all engine-managed shutdown, cancellation-token callbacks, finalizer completion, GC/RSS or whole-VM coherent epoch. Original terminal failure and reporting safety are not relaxed. Unexpected callbacks remain fully guarded. The Unity native caller may still need other lifecycle handling; no assumptions or implicit success.

A source-only forward plan and test-harness review cannot themselves close independent High IR-R03-01/02, H2 or full R03. No I Player or actual Unity SDK build has been executed by Primary; retain exact failed H evidence and all historical archive/process limitations.

## Primary disposition

Conditional oneuse-I source candidate for new single-batch Local Validation, subject to exact final dual-OS CI and fresh Mac admission/storage GO. Accept outcomes Passed/Failed/Blocked/NotRun separately. Never automatically advance H2/M08A/X02/SNAP-01, do not mark Human Review Gate approved, do not enable PureInterpreter. `R03Accepted=false`, `H2Passed=false`, `ReadyForHumanReviewGate=false`, `qualificationApproved=false`, `runtimeAcceptance=false`.
