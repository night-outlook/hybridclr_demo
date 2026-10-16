# P1 managed receipt successor PASS — Primary reconciliation

## Decision

**IR-LOCAL-P1-MANAGED-RECEIPT-01: VerifiedCorrectedInFreshSourceSDKOnlySuccessor.** Primary accepts the fresh `20261016-0620` result as **PASS / PassedSourceHostAndSDKOnly**, with all ten outer components Passed. This closes the receipt-consumer finding only for the exact executed source tuple and tested scope. It does not complete P1 or approve R03.

The earlier `20261016-0a0b` aggregate remains **FAIL / FailedOrIncomplete, 9 Passed / 1 Failed**, including its original `officialUnitySdkCompilePassed=false`. No historical result is recalculated or reclassified. Both one-shot cycles are consumed. **Current owner: Primary Implementation. Local Validation is PAUSED; no new execution is authorized.**

## Exact source and publication authority

All four repositories use `codex/assembly-shadow-r01b-h1` and their canonical `night-outlook/<repository>` remotes. Primary fetched each current remote ref through the GitHub Connector and confirmed the returned identities and read/write permission metadata.

| Repository | Actual Local execution commit | Returned publication checked by Primary |
| --- | --- | --- |
| night-outlook/hybridclr_demo | 9427336ebce4fa4e633e9408fbbef4841ea9ff45 | af22a2391a6e15127593f0d3a77fe965ad08f71a |
| night-outlook/hybridclr | 4b2774b066cfc6afd77a8c8aded6bda7ea574f55 | same |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | same |
| night-outlook/il2cpp_plus | 0a0b70156e75d450d75d0bcfd9132843b8abbbb0 | same |

The earlier demo source/CI anchor is `06209426b765a805da2cc2f810ba5da390787099`; the actual executed demo HEAD is `9427336ebce4fa4e633e9408fbbef4841ea9ff45`. The returned `af22a239...` adds Local reports/evidence, not a new compilation. Primary compared both complete, non-truncated root Git tree inventories for the executed and returned demo commits: every non-Docs entry has identical path, mode, type and object ID. In particular, Tools is `962caa2d79284834322e3280a141c7c483584385`, Assets is `743ebd69149d8a9df2dd3fa02f831bf3816c1acc`, and .github is `8e3a709b9a17ca916db2465691fc196cb02f78d4` at both commits.

This reconciliation changes documentation only. Its later publication HEAD must not replace the actual historical execution SHA. The Local paths remain `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repository>`; Primary did not operate those local checkouts. Historical `Tools/AssemblyShadow/R03/source-pins.json` remains unchanged at the earlier native execution pin `74dbdbea80d83923863303bd2b2c0a87f36541b1`; the completed SDK batch explicitly admitted native candidate `0a0b70156e75d450d75d0bcfd9132843b8abbbb0`.

## Evidence read and independently reconciled

Read the unchanged [LOCAL_VALIDATION](../../../../../Handoff/LOCAL_VALIDATION.md), [RETURN_TO_WEB](../../../../../Handoff/RETURN_TO_WEB.md), [fresh checkpoint](../../local-validation-p1-managed-receipt-20261016-0620/README.md), [raw aggregate](../../local-validation-p1-managed-receipt-20261016-0620/batch/RESULT.json), [managed outer cell](../../local-validation-p1-managed-receipt-20261016-0620/batch/commands/managed-sdk.json), [producer stdout](../../local-validation-p1-managed-receipt-20261016-0620/batch/commands/managed-sdk/stdout.bin), [nested managed result](../../local-validation-p1-managed-receipt-20261016-0620/batch/managed-sdk/build-api/results.json), [binding revalidation](../../local-validation-p1-managed-receipt-20261016-0620/MANAGED_BINDING_REVALIDATION.json), [Local evidence audit](../../local-validation-p1-managed-receipt-20261016-0620/preflight/EVIDENCE_AUDIT.json), and [consumed evidence preservation](../../local-validation-p1-managed-receipt-20261016-0620/preflight/CONSUMED_AFTER.json).

Primary checked the complete raw aggregate in two consecutive ranges, including all ten command records, exact before/after repository tuples, `sourcePreserved=true`, `postflightError=null`, and both SDK attempted/passed flags true. The managed cell records child exit0, `innerResult=Passed`, `status=Passed`, `returnedBindingVerified=true` and the exact nested `innerResultPath`.

The producer stdout and outer receipt agree on:

- Path: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03-P1-MANAGED-RECEIPT-20261016-0620/managed-sdk/build-api/results.json`.
- Nested result SHA-256: `3e2dc122b1d317bda78e9354d191a15d035269fc8ae9700d2eaf19d93ca04130`.
- Stdout SHA-256: `eb63e65efcebb3514c1dcc7959f4bd1a93675f208ba1f3f995e30f1c2e3a6bd9`.

Primary independently recomputed the stdout SHA-256 and Git blob ID from the Connector-returned UTF-8 bytes, matching the outer receipt and published stdout blob `5a844c987c934e683882ad55909c1dcba3046dfd`. The fetched nested result's final fields confirm `result=Passed`, schema1, Unity2022.3.62f2 and false runtime/Editor/Player execution flags; its Git blob is `d48d26b87bf0180bfdc2bf3244d05ec1ed67f0b1`. Local's separate revalidation records that the full nested bytes match the returned SHA-256 and that no obsolete root-level receipt exists. Primary did not independently rehash the entire nested receipt, all SDK inputs, or the complete external raw tree in this reconciliation.

## Empirical results retained with their scope

| Evidence | Reconciled result and boundary |
| --- | --- |
| Fresh aggregate | PassedSourceHostAndSDKOnly; ten Passed outer components; consumed after this execution |
| Managed receipt consumer | Verified corrected in this fresh source/SDK-only successor; exact path/hash/verdict joins recorded |
| Official managed compilation | Local-audited five products and one expected-negative control; 428 input hashes; negative exit1, exactly two CS0266 errors and no negative DLL |
| Official native syntax | Local-audited 70/70 Passed: 14 translation units x five profiles; 0 Failed/0 NotRun; 1900 scratch inputs checked |
| Host components | Passed within their existing host/mock scopes, including legacy parity, metadata admission, bounded readers and frozen execution/V2 |
| Warnings | Local recorded 68 managed and 742 native warning occurrences; retained unsuppressed, not new failures or warnings eliminated |
| Preservation | Local audited 2405 installed inputs / 316062203 bytes unchanged; 3658 fresh regular output entries and 382 localized command-stream pairs verified; four intentional negative symlinks checked separately |
| Consumed FAIL | Local audited its 3658 regular entries and 1900 scratch inputs preserved; no reuse or reclassification |
| New execution in Primary | None: no Unity, SDK compiler, Player, host regression rerun or full custody campaign was invoked by this reconciliation |

Primary's checks above corroborate the published joins and source authority. The extensive SDK, compiler-output and external preservation counts remain **Local-audited evidence**, not a claim that Primary repeated those full audits. [EVIDENCE_DISPOSITION.json](EVIDENCE_DISPOSITION.json) records that distinction explicitly.

Fresh raw RESULT SHA-256: `d9fca3f1b223fd41907276ce321b7a58c4b1dd41526ad93e0b8bcfa7a499e901`. Fresh MANIFEST SHA-256: `d4027bcd866c83d5adc6e432ffb311fedb580e7ae300fd95d371f8ab6ac17f61`. These identities are reported in the Local audit; Primary did not regenerate these manifests.

Consumed FAIL identities remain RESULT `13e256649c9c6355b4ed7eb4c5190a0f62acacaf42ad0195a27a21718d3ba565`, MANIFEST `b0f6c0597a7311ce2ec8647d807da8dcfbef34ee41140a104ef79dc84a10a13f`, managed result `43f38be35063559bcb156c31968f6b80d8707982692aef55fd6ab05285ea916e`.

## Remaining Primary engineering gates

**Earliest unfinished stage: P1 coherent bounded live general/execution VM capture.** Original getter integration, metadata/type-key ownership, global snapshot coherence, source mutation handling, lock/shutdown safety and allocation/GC/RSS limits are still open. Passing the 70-unit syntax matrix does not prove a linked Player, deadlock freedom, real metadata teardown or a complete bounded capture.

P2 authenticated native/C# V2 semantic integration remains NotIntegrated. E0 Unity2022.3.62f2 StandaloneOSX supported engine-owner capability remains Blocked/Unavailable; E1 real scheduling, maintenance, callback draining and restart remains BlockedByE0. Full P3 integrated/runtime preparation remains incomplete despite its scoped compiler evidence. All nontrivial work remains Primary-owned; none is delegated to Local in this reconciliation.

The consumed source/SDK assignment is closed in [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md). Required new Local commands, roots and evidence: **none**. Any successor needs a separate reviewed, committed, exact-source handoff. No retry of either consumed cycle, runtime seven-root batch, new Player or Human Review Gate follows from this PASS.

Historical SNAP-01/N/M/K/I/E FAIL, strict S custody Blocked and independent R03 full-stage FAIL/re-review NotRun remain unchanged. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion remains disabled. No H2/X02/M08A advancement.
