# R03 P1 owned general V1 composer — Primary reconciliation of Local SDK PASS

## Decision and ownership

**Disposition: VerifiedWithinFreshSourceHostAndSdkSyntaxScope** for the exact Local `20261016-3dc9` source tuple. The factual Local verdict remains **PASS / `PassedSourceHostAndSDKOnly`, 11/11 outer components Passed**. This closes the single source/SDK-only validation assignment, **not P1 or R03**. No new substantive Local issue was reported. Both source and returned evidence were read directly through the GitHub Connector; Primary has not executed Unity, any SDK compiler, the tests again or a Player.

**Current owner: Primary Implementation. Local Validation: PAUSED.** The `20261016-3dc9` attempt and its evidence, copied-SDK scratch, Local preflight records and Git checkpoint are consumed. [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) contains no new executable authorization. Further P1 work belongs to Primary.

## Exact four-source identity — execution versus publication

All repositories use `codex/assembly-shadow-r01b-h1` and their canonical `night-outlook/<repo>` remote. GitHub Connector independently confirmed canonical repo identity, expected branch heads and write/read permission metadata.

| Canonical repository | **Actual Local execution SHA** | Returned factual publication |
| --- | --- | --- |
| night-outlook/hybridclr_demo | `bfb6056bead9dadf2f94d6aace8d3d600b8bdaad` | `9e862190e29f332114ad8b648cf3f7dca90a30c3` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | unchanged |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | unchanged |
| night-outlook/il2cpp_plus | `3dc9b848d1d6b7616b257c95dc4727db06fd05f7` | unchanged |

The demo's tested CLI/compiler source anchor is `85257e495a141e553b56bc1ef47369eb36f572a5`; the intervening authoritative handoff was Docs-only. Primary independently compared the **complete, nontruncated root Git trees** for the demo execution commit `bfb6056...` and returned publication `9e86219...`: every non-`Docs/` entry has identical Git object/mode/type (including Tools, .github, Assets, Packages, ProjectSettings). Thus the factual publication did not change executed tool or project sources. Local separately recorded [SOURCE_TRANSPORT_EQUIVALENCE](../../local-validation-p1-owned-general-20261016-3dc9/preflight/SOURCE_TRANSPORT_EQUIVALENCE.json), binding the handoff-containing execution HEAD and refusing non-Docs differences from the tested anchor. Do not substitute the later publication or this Primary report's future commit for the execution pin.

The existing historical `Tools/AssemblyShadow/R03/source-pins.json` continues to record earlier native `74dbdbea80d83923863303bd2b2c0a87f36541b1`; the executed candidate used native `3dc9b848d1d6b7616b257c95dc4727db06fd05f7` via a separate explicit SDK candidate pin without changing history. Local checkout authority remains `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`; Primary did not operate or mutate those worktrees.

## Raw evidence directly inspected by Primary

Read, without modification: Local-owned [LOCAL_VALIDATION](../../../../../Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../../../../../Handoff/RETURN_TO_WEB.md), [factual checkpoint](../../local-validation-p1-owned-general-20261016-3dc9/README.md), [aggregate RESULT](../../local-validation-p1-owned-general-20261016-3dc9/batch/RESULT.json), [owned general RESULT](../../local-validation-p1-owned-general-20261016-3dc9/batch/owned-general/RESULT.json), [composer verification](../../local-validation-p1-owned-general-20261016-3dc9/preflight/OWNED_GENERAL_VERIFICATION.json), [independent Local audit](../../local-validation-p1-owned-general-20261016-3dc9/preflight/EVIDENCE_AUDIT.json), [exact one-shot argv](../../local-validation-p1-owned-general-20261016-3dc9/preflight/RECEIPT.json), [managed outer receipt](../../local-validation-p1-owned-general-20261016-3dc9/batch/commands/managed-sdk.json), [producer stdout](../../local-validation-p1-owned-general-20261016-3dc9/batch/commands/managed-sdk/stdout.bin), [managed nested result](../../local-validation-p1-owned-general-20261016-3dc9/batch/managed-sdk/build-api/results.json), and [native SDK result](../../local-validation-p1-owned-general-20261016-3dc9/batch/native-sdk/results.json).

The one original Local attempt was **2026-10-16T10:35:20.028775Z → 10:37:54.060784Z, exit0**. The complete aggregate records all **11/11 commands Passed and child exit0**:

- legacy-host: `PassedHostOnly`
- metadata-gate, bounded-class, bounded-physical, bounded-first-use, bounded-status, bounded-inventory: `PassedWithinHostScope`
- owned-general: `PassedWithinOwnedHostScope`
- frozen-v2: `PassedWithinInactiveHostScope`
- managed-sdk and native-sdk: `Passed`

The raw aggregate also records `sourcePreserved=true`, `postflightError=null`, `expectedNativeSyntaxUnits=75`, `officialUnitySdkCompileAttempted=true`, `officialUnitySdkCompilePassed=true`, `realUnityEditorLaunched=false`, `UnityPlayerExecuted=false`, `R03Accepted=false`, `ReadyForHumanReviewGate=false` and `historicalEvidenceReclassified=false`. The before/after four-repository source tuples are exactly equal.

**Primary independently recomputed SHA-256 over the exact UTF-8 file bytes returned by GitHub**, matched to the recorded sources:

| Authenticated published record | Actual bytes | Independent SHA-256 |
| --- | ---: | --- |
| `batch/RESULT.json` | 19,725 | `706a7a8e981c036a31bccfbe4ab267dcb3108465d19d46c45351e81a16426b8c` |
| `batch/owned-general/RESULT.json` | 9,109 | `a8bf2d7036008890231a03d9d659a06be087b46bbc9899055ac7e8f63f52803a` |
| `batch/commands/managed-sdk/stdout.bin` | 210 | `cd693266b987c5a78d9825906d48f3429888dc751fb1eb0065a2ddc37a5add26` |
| `batch/managed-sdk/build-api/results.json` | 119,119 | `5638ebd6f1a587ce672a22ca9d92727f578b50d337d30c447a3999c2f04c8d3a` |

The managed outer receipt independently matches the producer stdout's returned exact nested path and SHA-256, `innerResult=Passed`, `returnedBindingVerified=true`, outer status Passed and child exit0. The actual managed nested record has `kind=R03CompleteBuildHelperCompile`, schema1, Unity2022.3.62f2, no Editor/runtime acceptance, **five positive targets** and separate `OriginalUnsignedCounts` expected-negative control (exit1, exactly two CS0266, no DLL per independent Local audit). The obsolete root-level managed success path was absent and not fabricated.

The new owned-general child independently records **strict and sanitized** runs, each with **11 distinct actual test groups**, four successful compile/run receipts, watched allocator count **0 after prewarm**, exact old V1 JSON bytes from actual production bounded source headers and original serializer, and correct negative handling of incomplete input, mixed physical/class generations, bad startup references, 3,932,160-byte general output limit, malformed UTF-8 and reused/partial output. Its source contract explicitly records `globalVmEpochProven=false`, `realClassPointerProven=false`, `originalLiveGettersReplaced=false`, `runtimeAcceptance=false`. Primary also read the actual native `AssemblyShadowBoundedGeneralComposer.h`, frozen capture header and source-bound runner at the executed native SHA and confirmed their Git blobs (`bf3c19fab543c24134712ea08dc2cb78190f7f3a`, `08856d4a610ed3fa519cee67bad8a307dd82a34b`, `59fd0b4360a4e3b1768c64c1a4d19de765fb1469`).

The native SDK child declares `Passed`, exactly **75 actual translation-unit records**, 15 units in each of five `candidate/debug/probe-off/diagnostics-off/feature-off` profiles; candidate `3dc9...`, including **AssemblyShadowGeneralComposeSyntax.cpp**, Runtime.cpp, AssemblyShadow.cpp, Assembly.cpp, AssemblyShadowVisibility.cpp and the original serializer. This is `-fsyntax-only`, **not linking, installed Player execution or runtime teardown**.

## Local independent audit, preserved without overstating Primary coverage

Local's factual audit independently authenticated **five managed products / 428 input hashes**, expected-negative exit1/two CS0266/no DLL, **75 native syntax commands / 1,901 scratch input hashes**, and retained **68 managed plus 742 native warning occurrences** (including Baselib; no suppressed warnings or unexpected compiler errors). It confirmed **2,405 installed SDK files / 316,062,203 bytes unchanged**, source Git states before/after, 3,734 regular evidence entries, **403 localized command-stream pairs** and four intentional negative-control symlinks against nested legacy manifests. The fresh Local manifest SHA-256 is `71045ef14e868faeb1f3eb22d30a8f6ba1279a0de4d74de861553dfcfa6a18f1`.

Primary did **not** rehash the full external 3,734-entry evidence directory, the 2,405-file Unity installation, all 1,901 copied SDK inputs, or all 403 command streams. These claims are **Local-audited, not independently rerun or reauthenticated by Primary**. Apple LeakSanitizer remains Unavailable in this Local environment; host ASan/UBSan and SDK syntax do not establish native GC/RSS, metadata lifetime or deadlock freedom.

## Immutable consumed outcomes and acceptance

| Historical cycle / gate | Original result | Treatment |
| --- | --- | --- |
| `20261016-3dc9` | **PASS / PassedSourceHostAndSDKOnly 11/11, 75 syntax** | **Consumed**, current verification |
| `20261016-f598` | **PASS / PassedSourceHostAndSDKOnly 10/10, 70 syntax** | Consumed, unchanged |
| `20261016-0620` | **PASS / PassedSourceHostAndSDKOnly 10/10, 70 syntax** | Consumed, unchanged |
| `20261016-0a0b` | **FAIL / FailedOrIncomplete 9/10**; aggregate SDK flag false | Consumed, **not repaired/reclassified** |
| SNAP-01 | **FAIL / ReturnRequired, 14/18** | Unchanged |
| N/M/K/I/E, historical R02 whole-file fingerprint | **FAIL** | Unchanged |
| Original S custody | **Blocked** | Unchanged |
| Independent full-stage R03 review / fresh rereview | **FAIL / NotRun** | Unchanged |

Primary opened the three older exact raw aggregate receipts (f598, 0620, 0a0b) at the stated returned publication: each retains its historical result and SDK aggregate boolean. The older 0a0b raw result digest remains `13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565` with `officialUnitySdkCompilePassed=false`. The new PASS does not alter the original SNAP-01 slot14 oversized V1 witness (>262144 byte observed prefix 262145, full exact length Unavailable) or the native engine 51213 uncapped reports / 500ms / exit71.

## Remaining engineering scope — do not infer a Human Review Gate

**Earliest unfinished work remains P1 coherent bounded LIVE general/execution/R02 VM capture.** The new composer reads already completed independently acquired owned snapshots, not a single atomic VM source epoch. Equal physical/class active generations are at most a local consistency check; they do not authenticate stored `Il2CppClass*` pointer origin/epoch or prove absence of ABA and concurrent native metadata mutation. Original GetDiagnosticsJson and GetExecutionDiagnosticsJson still allocate and are not replaced; the real type-key recursion, class iterator allocations/peak GC/RSS, VM lock ordering and Shutdown reader drain remain unqualified.

**P2 NotIntegrated:** no real authenticated native/C# V2 sidecar/file transaction/unchanged original semantic verifier integration. **E0 Blocked/Unavailable:** no source/vendor-supported Unity2022.3.62f2 StandaloneOSX engine owner safe point. **E1 BlockedByE0:** no genuine callback/GC/finalizer maintenance/drain/restart. **Full P3 Incomplete:** 75 source/SDK syntax checks do not demonstrate linked Player/runtime behavior.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2/X02/M08A, engine scheduler, Unity/Player run or Human Review Gate authorized.

**No new Local commands or output roots follow from this reconciliation.** The Primary-owned `WEB_TO_LOCAL.md` is PAUSED; the next Local assignment would require a separately reviewed, committed, exact-four-source publication. Preserve all factual Local-owned reports, evidence and historical source pins.
