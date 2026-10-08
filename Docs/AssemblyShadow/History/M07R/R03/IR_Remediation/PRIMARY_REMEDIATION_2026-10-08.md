# R03 Primary remediation — original S provenance and remaining execution fix

Date basis: 2026-10-08 UTC. Owner: **Primary Implementation**.

**This is a partial remediation checkpoint, not a Local Validation handoff or stage approval.** The existing independent full-stage verdict remains **FAIL**. IR-R03-01 now has a successful original-byte audit and an explicit withdrawal of mismatched claims, but is not independently closed. IR-R03-02 remains open: this continuation did not modify the native runtime or implement/run its new Player regression.

## 1. Authority and read order

Read the [independent report](../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md) together with its [C04 citation erratum](../S_Reconciliation/INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md), then the [corrective machine-readable index](ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json). The original report was published at `0320495a6262f634fe0f69b628b143d5d1c1581b`; the erratum at `034db0973fe5b69dbb56644f05cb345b9e52cbb7`. Neither is replaced by this Primary assessment.

All feature branches remain `codex/assembly-shadow-r01b-h1`. The original S evidence publication is `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`; its actual executable tuple is:

| Repository | S execution source |
| --- | --- |
| night-outlook/hybridclr_demo | `29bb3d4a39bf8a2f23be404f77535aaba3485bfc` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` |

The new auditor/tests/workflow executed from demo `38575b165d798defe545f2501f1fc307ccac44a3`, not from the S runtime source. Later documentation-only descendants are publication transports, not new executable validation. The final publication response supplies their exact remote HEAD.

The Local-owned [LOCAL_VALIDATION](../../../../Handoff/LOCAL_VALIDATION.md) and [RETURN_TO_WEB](../../../../Handoff/RETURN_TO_WEB.md), all original checkpoint bytes, and original historical verdicts remain unchanged.

## 2. Explicit correction of Primary's previous provenance claims

The historical `S_Reconciliation/EVIDENCE.json` (blob `45cdc9192461330a09779f55e4391facfc994f61`) attributed a five-part, 283,728,477-byte archive with 18,159 indexed files / 18,160 members to the original S checkpoint. **That attribution is withdrawn.** Its `f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7` archive and associated result/ledger/index/seal digest family are not authority for original S.

The new audit reconstructs the nine committed original parts and authenticates this exact archive:

```text
Original archive bytes: 587907380
SHA-256: 23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6
Indexed files: 15712
Archive members: 15713
```

The corrective JSON supplies all five complete original digests, byte lengths, input commits, output identities and separate assurance boundaries. It also withdraws the earlier index's unjoined PID/time/custody/storage/P05-detail and capture-completeness claims. They must not be retained merely because some aggregate counts resemble original S. Original Local records remain the source for factual historical runtime observations; this correction does not silently substitute new values for unverified old claims.

The provenance of the withdrawn digest family remains **unresolved**. No byte-authenticated transformation between that family, the earlier review capture, and original S has been demonstrated. The earlier outer capture ZIP is a separate transport artifact; verifying its outer digest cannot establish the inner original-S identity. No inference about intent is made. The old records are preserved, not rewritten to conceal the discrepancy.

## 3. Implementation delivered in this continuation

The concurrent comparator repair at `843ada13041d719b896912bb60bac59af3da397d` was inspected and retained. Its successful run `37796007687` is historical evidence of that revision; the preceding failed comparator run remains Failed.

This continuation published:

| Commit | Change |
| --- | --- |
| `66e1c4e204b4ae8735e28c6e3e4e2ad965a7dc6c` | Strengthened `Tools/AssemblyShadow/R03IR/audit_s_provenance.py` |
| `f479cd3779d20cb390fce0b900fdd27f9c03f03d` | Added `test_audit_s_provenance.py`, 30 synthetic host tests |
| `38575b165d798defe545f2501f1fc307ccac44a3` | Ran tests and exposed bounded audit/source/output provenance in `.github/workflows/r03-ir-provenance.yml` |

The auditor now requires literal false acceptance flags in both original ledger and final result, compares JSON without conflating booleans and numbers, rejects malformed evidence paths/duplicate keys/non-finite constants, and authenticates selected checkpoint JSON against archived bytes before interpreting it. C04 fields are measured as NotRecorded rather than hardcoded as false. Every cell's archival equality is separated from a complete role-specific build/process semantic join.

A further reporting defect was corrected: the previous script set Passed before exporting output files and checking the final input checkout. A later exception could leave `audit.json` with `result=Passed` plus an error even though the command failed. Passed is now assigned only after exports and the clean-tree check; the exception path explicitly revokes Passed and does not report unchanged inputs when their final status is unavailable.

The tests cover valid producer behavior, no input mutation, missing/invalid flags, changed seals/digests/nested cells, numeric-versus-boolean substitution, duplicate/non-finite JSON, path/symlink escape, archive-to-JSON binding, absent/null/false distinction, exclusive output writes and early/late failure reporting. These are host tests of evidence tooling, not runtime tests of Assembly Shadow.

## 4. Actual validation performed and read back

[Workflow run 37845000985](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985), job `113543552737`, executed from `38575b165d798defe545f2501f1fc307ccac44a3` and completed successfully. Primary read the actual job log, including the test roster, audit JSON and output-provenance JSON. The Connector's artifact metadata was also read and agrees with the upload log.

| Check | Observed result |
| --- | --- |
| Synthetic host regressions | 30 tests, 0 failures, 0 errors, 0 skips, 0 unexpected successes |
| Checkpoint Git-blob/manifest authentication | 16,978 tracked blobs, 16,977 manifest rows; exact membership and bytes |
| Ordered transport reconstruction | Original sizes and full digests match committed transport records |
| Original archive | All 15,713 members authenticated; exactly 15,712 indexed files plus the index |
| Finalizer and cell equality | Original result/ledger relationship and all 90 cells match; dependencies retain recorded Passed states |
| Selected archival receipt joins | P05 recovery, integration, C04 raw/verification match archived bytes |
| Final source checks | Original fc55 checkout and exact tools checkout both clean |
| Unity / IL2CPP / Player execution | **NotRun in this continuation** |
| Independent reviewer / stage acceptance | **Not performed by this workflow** |

P05's archived receipt records ExactOriginalBytesRestored, fresh remote authority Passed, stage Complete and matching original/after settings digests. The separately authenticated integration receipt records empty restored-baseline roots and closure. Neither observation is a new execution of P05.

C04's raw and verification JSON have neither `newMethodInvocationAttempted` nor `newMethodInvocationSucceeded` at the top level. Their absence is **NotRecorded**, not an observed false value. This matches the preserved reviewer erratum and does not establish a post-poison valid-call test.

Output artifact: [11579112494](https://github.com/night-outlook/hybridclr_demo/actions/runs/37845000985/artifacts/11579112494), 584,964,754 bytes, ZIP SHA-256 `59fd67ab70958178bd979912572781ecc76c1045fad4ba607ff6ce95f818e6e6`, expires `2026-11-07T21:12:48Z`. This outer digest is reported by the Actions upload and Connector metadata; Primary did not download/recompute it in the unavailable chat container. The exact original archive inside the output is separately identified by `23aedcaf...` in the full-digest corrective JSON. Do not conflate these hashes.

The output contains the checkpoint/blob crosswalk, original archive member map, ninety-cell crosswalk, C04 field observations, host results/log, exact source bindings and original archive. The original committed transport parts remain the durable reproduction input after artifact expiration. Reproduction must use the pinned auditor and an exact clean fc55 checkout, writing to a new external directory; never reseal or overwrite original S.

## 5. Remaining assurance limits and finding status

**IR-R03-01: partially remediated, not independently closed.** Original checkpoint reconstruction/byte authentication and withdrawal of wrong original-family claims are complete for this bounded audit. A complete role-specific source/build/process semantic audit is not: the tool explicitly reports `fullSourceBuildProcessSemanticAudit=false`. Absent top-level fields are not accepted as successful joins. The earlier capture's omitted material source files and the withdrawn family's origin remain unresolved. A separate reviewer must inspect the correction and remaining coverage rather than accepting a green workflow as stage closure.

**IR-R03-02: open.** Native `AssemblyShadow.cpp` is still blob `08fd924a91fbd9701b50ac45ea7846f0bedd9a8c` at `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`. Its existing method guard distinguishes valid physical identity from obsolete identity but does not enforce an already terminal transaction on the success path. No native fix or new post-poison Player regression was committed in this continuation.

**Next Primary implementation objective:** add a shared terminal-execution predicate at supported business entry boundaries while preserving the original first failure and explicitly permitted fixed diagnostics. The no-throw/no-allocation boolean boundary, staging/private metadata restrictions, exception-construction reentrancy, pre-publication failure, and ordinary/OFF behavior require explicit treatment. Do not clear poison, globally exempt all calls during error handling, or grant arbitrary callbacks diagnostic privilege. A single state check without resolving these paths is not a complete correction.

Required fresh-process regression design remains:

1. Prove a prewarmed allocation-free active void method with an observable counter is callable before failure.
2. Trigger and catch, in separate cases, baseline-owner, captured-generic, type-resolution and post-publication initializer failures.
3. Actually attempt the valid target through supported interpreter, reflection and applicable delegate/interface entries after failure. Assert no body side effect and unchanged first failure/state/world; explicitly allowed fixed diagnostics must still work.
4. Include Debug ON, release ON and ordinary/OFF controls. Bind the real source/native/package/build/process tuple to raw outcomes. Do not relabel old C04 fields or historical S as this missing test.

Before any Local Validation handoff, Primary must implement/review the native changes and executable fixtures/verifier, publish exact pins and proportional commands, preserve historical roots, and perform the prescribed pre-handoff checks. Native scope cannot be delegated to Local as an unimplemented design task. No new Local runtime batch is authorized by this document.

## 6. Transport/bootstrap and execution limitations

GitHub Connector write capability was restored and proved in all four repositories. The uniquely named disposable branch `codex/connector-smoke-r03-ir-20261008-resume-843ada13` did not exist before creation in any repository. Each harmless commit was created through the Connector and its branch HEAD read back exactly:

| Repository | Base | Created/read-back smoke commit |
| --- | --- | --- |
| hybridclr_demo | `843ada13041d719b896912bb60bac59af3da397d` | `3950a92a590511c749609b5de97f4ea174f29ac7` |
| hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | `f79ead75065a1e4e6164d4b9728e1569e38e831d` |
| hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` | `61b17a1a10fc806578f159a65014e21d69aae34e` |
| il2cpp_plus | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` | `5807e22405487c7ff165f142742d8642f5a89aa4` |

All smoke branches remain because no branch-deletion action was exposed. Do not merge them; they are transport checks, not product or acceptance evidence. Only the demo feature branch changed in this continuation.

The chat container and Python execution each returned ClientError. Host tests and the read-only audit therefore ran in the source-pinned Actions job, with contents:read permission and persisted credentials disabled. No credentials, repository permission settings, automatic reviewer settings, platform pins or historical source files were altered to obtain execution.

## 7. Stop and ownership boundary

Owner D1=A/D2=A remains recorded; NativeLayoutAdmissionV1 bounds R03, X02 expansion remains deferred/disabled, and performance observations do not approve a production SLA or deferred CPU/RSS risks. Preserve S/R/Q/P/O/N and prerequisite records; retained R stays staged; four contaminated unisolated warm certificates stay Failed.

`R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. **Current owner remains Primary Implementation.** The immediate unfinished implementation is IR-R03-02, alongside the remaining IR-R03-01 semantic/capture coverage. No independent re-review PASS, H2, X02, M08A or Local runtime assignment is issued here.
