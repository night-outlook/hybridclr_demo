# R03 P1 first-use class-metadata Local successor — Primary reconciliation

**Disposition: PASS / `PassedSourceHostAndSDKOnly` accepted solely within its actual host + official installed Unity SDK compilation scope.** Primary independently inspected published raw source and machine evidence at the returned four-repository tuple. This does **not** close P1, reclassify historical FAIL results, prove Unity native metadata ownership/shutdown or authorize Player/R03 acceptance.

**Finding:** the additive first-use class-name reader is now **VerifiedWithinFreshHostAndSdkSyntaxScope**, not `P1Complete` or `RuntimeAccepted`. No new substantive Local finding was returned. Both the `20261016-f598` successor and earlier `20261016-0620` and `20261016-0a0b` Local source/SDK cycles are **consumed**. Current owner: **Primary Implementation**. Local Validation: **PAUSED**.

## Authoritative source and provenance

All four canonical GitHub repositories are on `codex/assembly-shadow-r01b-h1`. Primary independently fetched each remote ref and permissions via the GitHub Connector at this reconciliation's start:

| Repository | Actual executed Local commit | Published Local checkpoint commit |
|---|---|---|
| `night-outlook/hybridclr_demo` | `c83707ac2d8b562a745ea2568cde77fc2cf030c4` | `1eb4fa5118734c5d533052c028e596ee0650dfa7` |
| `night-outlook/hybridclr` | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | same |
| `night-outlook/il2cpp_plus` | `1e1d152f0e05b8038427c76a9c8a9b4b60998a72` | same |

Native P1 first-use **implementation commit**: `f598f8da5749e7c09ad5816630ce7e40b3f4ebca`, on top of the metadata-epoch gate `f71691407bf9af5544d00dd54bff9e2e7eb77307`. Primary independently compared native f598→1e1d: **only `.github/workflows/r03-ir-terminal.yml` changed**, not the first-use production code. The full first-use production `AssemblyShadow.cpp` Git blob is `b7c99eeaefb77bd7739304214277484d8b2ab261`; bounded capture header blob is `b7ba5dffb2e3ecebe7406f598e97a1ab97251cdf`, unchanged across that range.

Primary compared **complete untruncated root Git tree entries** of the actual demo execution `c83707ac...` and returned `1eb4fa...`: every non-`Docs/` tree identity, including `Tools`, `.github`, `Assets`, `Packages`, and `ProjectSettings`, is identical. The Local report independently verified the handoff-containing execution commit and no non-Docs change relative to the prior demo source anchor `06209426b765a805da2cc2f810ba5da390787099`. Neither the returned documentation checkpoint nor this reconciliation is a fresh compiler execution identity.

Local path authorities: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repo>`. Primary did not modify or execute commands in those checkouts. The historical `Tools/AssemblyShadow/R03/source-pins.json` remains bound to its older actually executed native commit `74dbdbea80d83923863303bd2b2c0a87f36541b1`; the source-bound candidate SDK validation explicitly supplied native `1e1d152f0e05b8038427c76a9c8a9b4b60998a72` without rewriting that historical pin.

## Independently inspected evidence

Read first, and do not overwrite:

- Local-owned [LOCAL_VALIDATION](../../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](../../../../../Handoff/RETURN_TO_WEB.md).
- [First-use factual checkpoint](../../local-validation-p1-firstuse-class-20261016-f598/README.md), [raw aggregate](../../local-validation-p1-firstuse-class-20261016-f598/batch/RESULT.json), [raw first-use method result](../../local-validation-p1-firstuse-class-20261016-f598/batch/bounded-first-use/RESULT.json), [first-use source verification](../../local-validation-p1-firstuse-class-20261016-f598/preflight/FIRST_USE_VERIFICATION.json), [native implementation equivalence](../../local-validation-p1-firstuse-class-20261016-f598/preflight/NATIVE_IMPLEMENTATION_EQUIVALENCE.json), [Local factual evidence audit](../../local-validation-p1-firstuse-class-20261016-f598/preflight/EVIDENCE_AUDIT.json), [one-shot command receipt](../../local-validation-p1-firstuse-class-20261016-f598/preflight/RECEIPT.json).
- [Managed outer](../../local-validation-p1-firstuse-class-20261016-f598/batch/commands/managed-sdk.json), [producer stdout binding](../../local-validation-p1-firstuse-class-20261016-f598/batch/commands/managed-sdk/stdout.bin), [managed inner](../../local-validation-p1-firstuse-class-20261016-f598/batch/managed-sdk/build-api/results.json), [native SDK result](../../local-validation-p1-firstuse-class-20261016-f598/batch/native-sdk/results.json).
- Earlier consumed source/SDK cycles [PASS 0620](../../local-validation-p1-managed-receipt-20261016-0620/README.md) and [FAIL 0a0b](../../local-validation-p1-metadata-source-20261016-0a0b/README.md).

Primary independently parsed the complete 10-command raw aggregate and checked **10 Passed, 0 Failed, 10 child exit 0, exact inner statuses**, pre/post four-source tuple equality, `sourcePreserved=true`, `postflightError=null`, `officialUnitySdkCompileAttempted=true`, `officialUnitySdkCompilePassed=true`, `realUnityEditorLaunched=false`, `UnityPlayerExecuted=false`, `R03Accepted=false`.

Primary independently recomputed SHA-256 over the **Connector-returned exact UTF-8 bytes** for:
- Raw aggregate `batch/RESULT.json`: `dabfae25587fcbbaae81d7d3bbe4c8d94928e29a7c1b85228e75a8a83a9943bc`, **matched** the Local audit (17,638 bytes).
- Managed producer stdout (211 bytes): `23fbdc2a9bc55160e80146c93cd4b57169e4f719cd1f5561c269daf6b9ad2e62`, **matched** the outer receipt.
- Actual nested managed result (119,136 bytes): `425577db1a66ab5b6d62ceca778ad6350d41ab767b7c3de7e61f1650e81427af`, **matched** producer binding and managed outer receipt.

The managed outer has `returnedBindingVerified=true`, `innerResult=Passed`, `status=Passed`, exit0 and the precise `managed-sdk/build-api/results.json` path; no obsolete root-level success fallback. The actual nested managed receipt carries `kind=R03CompleteBuildHelperCompile`, schema1, `unityVersion=2022.3.62f2`, `result=Passed`, and false runtime/native/Editor execution flags. It lists five positive compiler targets and separately expected-negative `OriginalUnsignedCounts` (expected exit1).

The exact first-use result has `result=PassedWithinHostScope`, method SHA256 `67fcd9f6660c67c8a60ed610cdc9b3c3cfc06adb01f9805a581e6dd97dd42be2`, two profiles `strict`/`sanitized`, **15 distinct, matching test groups per profile** and **four compile/run receipts with exit0**. Primary independently fetched the production body and `AssemblyShadowMetadataLifetime.h` from the final native commit, confirmed admission precedes the source lock, class naming uses `ResolvePhysicalClassCString` under `g_MetadataLock` without nesting `UsageLock`, then seals only after another usage-generation read. The source-side helper still fails closed on absent ownership/invalid inputs. This is a source inspection, **not a real class-pointer origin or global epoch proof**.

The nested native SDK result declares `Passed` with **70 actual translation-unit records, planned70, official candidate `1e1d152f...`**, and `unityEditorRun=false`, `runtimeAcceptance=false`. Local's independent raw compiler/source audit reports **14 distinct units × five profiles, 0 failed/0 NotRun**, and the same full source method/Unity2022.3.62f2 SDK. The prior native source CI [38876310270](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876310270) Passed 3/3 strict+sanitized host jobs. The later terminal-workflow source assertion update [38876957263](https://github.com/night-outlook/il2cpp_plus/actions/runs/38876957263) Passed 2/2; the older R02 whole-file historical pin check remains Failed.

## Local independently audited — not repeated by Primary

The separate Local audit reports **five managed products / 428 input hashes**, expected-negative exit1/exactly two CS0266/no DLL, and **70/70 native syntax-only configurations / 1,900 scratch input hashes**. It retained 68 managed / 742 native warning occurrences (including Baselib), all unsuppressed, with no unexpected errors. The SDK before/after audit reports **2,405 installed input files / 316,062,203 bytes unchanged**. The source/command/evidence audit reports **3,696 regular output entries** and **394 localized command-stream receipts**, plus four intentional negative symlinks validated against their nested manifests. The aggregate raw MANIFEST SHA-256 is `8852c93d82f008b7cde8498a3fb3a8d8597d0870f1e71e2fa4bcfdf44ceaf860`, from the Local audit.

Primary did **not** independently rehash the full 3,696-file external evidence tree, entire vendor SDK copy, all 1,900 scratch inputs, every compiler stream, or all 394 localized command receipts. These remain **Local-audited factual evidence**, not implied Primary runtime/compiler reproductions. Apple LeakSanitizer remains Unavailable.

## Immutable prior results

| Cycle | Original result | Custody |
| --- | --- | --- |
| `20261016-f598` | **PASS / PassedSourceHostAndSDKOnly (10/10)** | **Consumed**, this current exact tuple |
| `20261016-0620` | **PASS / PassedSourceHostAndSDKOnly (10/10)** | **Consumed**, earlier native `0a0b7015...` |
| `20261016-0a0b` | **FAIL / FailedOrIncomplete (9/10)** with `officialUnitySdkCompilePassed=false` | **Consumed**, preserved raw verdict |

Local checked preservation of old FAIL and earlier PASS raw/scratch roots. Earlier FAIL `RESULT.json` SHA256 `13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565` and its nested managed receipt `43f38be35063559bcb156c31968f6b80d8707982692aef55fd6ab05285ea916e` remain unchanged. Earlier PASS raw RESULT `d9fca3f1b223fd41907276ce321b7a58c4b1dd41526ad93e0b8bcfa7a499e901` remains distinct. Historical SNAP-01 remains **FAIL/ReturnRequired, 14/18**; original slot14 >262144 (only scanned prefix262145, full true byte length Unavailable); engine 51213 uncapped reports / 500ms, exit71. Other N/M/K/I/E failures, strict original S custody Blocked and historical independent R03 review FAIL/re-review NotRun are untouched.

## Remaining Primary-owned engineering gates and stop

**P1 still INCOMPLETE:** first-use class-bearing source is an **inactive** bounded input path, not the original live general/execution diagnostic capture nor a coherent R02/VM global epoch. The stored `Il2CppClass*` physical pointer's origin and first-session lifetime are not authenticated merely by admission and metadata locking. Original getters still allocate and read independently. No worst-case class iterator, type-key recursion, allocation/RSS/GC, lock/deadlock/shutdown safety or real Player behavior is proven.

**P2 NotIntegrated:** real authenticated native+C# V2 emission, transaction durability and original semantic verifier are not integrated. **E0 Blocked/Unavailable:** the verified Unity engine-owner safe point and native maintenance contract is missing; **E1 BlockedByE0** for scheduling/drain/restart. **P3 full integration Incomplete** despite successful host and SDK syntax tests. No human review gate or next milestone may be inferred.

`R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. Preserve all V1/V2 transport limits and original 500ms/1–64 native report predicates. **No new Local command, root or runtime assignment is authorized by this reconciliation.** `WEB_TO_LOCAL.md` must be PAUSED until a separately reviewed and committed exact-source assignment is ready. Current owner: **Primary Implementation**.
