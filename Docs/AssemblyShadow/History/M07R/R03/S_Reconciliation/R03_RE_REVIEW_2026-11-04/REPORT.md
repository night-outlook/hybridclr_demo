# R03 re-review — design, plan, implementation and K evidence

Date: 2026-11-04. Scope: R03 only.

**Technical stage-acceptance verdict: FAIL — required closure evidence remains incomplete.** This is not a new failure of K's five Players, nor a claim that the original terminal predicate defect remains unchanged. K retains **PASS / FocusedEvidenceReadyForIndependentReview** within its recorded scope. The source correction and the exact tests it passed receive credit below; missing proof is not represented as an observed runtime failure.

## 1. Review authority, continuity and immutable inputs

The user explicitly requested this re-review in the current session after Primary reconciliation. This assessment uses fresh source/evidence reads and a newly executed host check rather than treating Primary's conclusions as approval. **Continuity disclosure:** the same assistant/session previously prepared the Primary reconciliation. This is a reviewer-role technical reassessment, not a claim that a second isolated agent or an organizationally independent person performed it. It must not be used to manufacture independent-person approval or Human Review Gate approval.

All repositories use branch `codex/assembly-shadow-r01b-h1`.

| Repository | Frozen review input |
| --- | --- |
| night-outlook/hybridclr_demo | `6e4790a32103c76148c751a0d6f12fbf30fefe23` |
| night-outlook/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `41764ae1eeefb33b05966e7f7676e52aae39c340` |

Execution identities are deliberately separate:

- **K execution:** demo `c20da0b261172cbdd188378e24dbe9343a14c6b2`, with the three other pins above.
- **K evidence publication:** demo `14f97f15af6c06afa65957a9b880ccf841069452`.
- **Current review/documentation input:** demo `6e4790a32103c76148c751a0d6f12fbf30fefe23`; not a second K execution.
- **Original S execution:** demo `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`, native `1cf87f8209790f9fb2ebec97487dc1990ccd56c5`.
- **Original S checkpoint:** demo `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
- **October 8 independent review:** demo `aee7975874a5ddf236ab9d00d5d682b470010f8f`, original S native. Its historical FAIL is not overwritten.

The Mac execution workspace remains `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/{hybridclr_demo,hybridclr,hybridclr_unity,il2cpp_plus}`. This reviewer did not operate those directories or execute Unity there.

GitHub Connector reads verified the four remote references. Direct, nonrecursive root-tree comparisons of K execution and the current demo input found identical entries outside `Docs`: Assets `743ebd69149d8a9df2dd3fa02f831bf3816c1acc`, Tools `c645e4f9ecdd754efe46535099ef84f4eef30f8e`, Packages `44fc563e446d7a3625e4881d1e7f0165ef4f45db`, ProjectSettings `ec04fc470897dcb919b8603d2e84069d1d8d4912`, and the remaining non-Docs root entries. This avoids incorrectly treating a 300-file-capped comparison response as a complete diff. It establishes non-Docs tree equality, not fresh execution or universal equivalence of every evidence input.

Publication is additive documentation only. The existing Connector create-file smoke commit `8baa9827ca61b238b0864545b63fd317527b6ab6` was freshly read back from `codex/assembly-shadow-smoke-20261103-role-bootstrap-6fca`; repository push permission and the active branch head were checked. No smoke branch is merged, no historical evidence is edited, and no active Local execution authority is created.

## 2. Governing requirements and review method

The governing basis is `Docs/AssemblyShadow/Plan/{DESIGN.md,EVIDENCE_CONTRACT.md,HUMAN_REVIEW_GATES.md}`, the R03 evolution and remaining-completion plans, the owner D1=A/D2=A disposition, and the original review plus its evidence erratum. Primary's November 4 reconciliation and review brief are inputs to challenge, not the verdict.

The review distinguishes four levels: source semantics inspected; existing Local/CI execution corroborated by committed records; new host checks actually executed here; and remaining unavailable or unreviewed proof. Reading an archived audit's Passed field is not the same as independently reconstructing its archive or witnessing the Mac filesystem.

D1=A permits conservative NativeLayoutAdmissionV1 and explicitly defers unsupported structural expansion to X02. Such deferred cases are not newly invented R03 defects. D2=A permits observational performance reporting; it does not rehabilitate the four contaminated warm certificates or accept production CPU/RSS risks. Conversely, neither decision waives persistent poison at supported business entry or source/build/evidence authentication.

No Unity, IL2CPP Player build, new Local cycle, K retry, or original-S replay was performed. The only newly compiled code is the small, source-bound standalone terminal-policy check described in section 6. No product code was modified.

## 3. Findings and dispositions

| Existing finding | What is corrected or supported | Remaining acceptance disposition |
| --- | --- | --- |
| **IR-R03-02 — High** | The original valid-method-after-poison predicate hole is corrected in the inspected common guard. K supplies affirmative pre-positive and post-poison attempt/side-effect evidence for its selected baseline/type cases. | **NeedsEvidence / not fully closed.** Required captured-generic and post-publication initializer failure regressions are still absent; supported entry-path and production-configuration coverage must be reconciled. |
| **IR-R03-01 — High** | The contradictory five-part archive claim has been explicitly withdrawn as original-S authority, and the canonical nine-part identity is documented and audited. | **NeedsEvidence / not fully closed.** Complete independent authentication of the material original source/generated-code/build/Player graph and capture omissions is not established by this review. |

These are remaining closure obligations, not two newly reproduced product failures. A finding may have a corrected root defect while still failing its agreed acceptance contract.

### 3.1 IR-R03-02: corrected common predicate, incomplete required runtime matrix

**Source inspected.** At native `41764ae1...`, `libil2cpp/vm/AssemblyShadow.cpp::AssertMethodIsActive` rejects `TerminalMethodDenied(method)` before ownership/generic processing. Its otherwise-successful path rechecks the terminal predicate before returning true. `RequireActiveMethod` routes terminal rejection through the reserved rejection transport rather than creating a new first failure. The inspected source blob is `57cf47f964a83973df8296955ccf856b105c595f`.

The source-bound policy header `AssemblyShadowTerminalExecution.h`, blob `33258986c31b2e6ae3af17b8553030482a83aef7`, treats states 8/9 as terminal and recognizes durable failure for enabled transactions. Disabled/OFF is not poisoned merely by a durable flag. An exception-construction allowance requires both the construction scope and a separately verified fixed physical constructor; the scope alone cannot admit arbitrary business calls.

`AssemblyShadowTerminalRejection.h` prepares a physical pinned exception while healthy, preserves native recovery as the original-cause authority, and rethrows without ordinary exception stack/constructor preparation. Its fail-stop path when the reserve is unavailable is not an ordinary managed recovery. These observations reduce the earlier recursive-diagnostic risk; they do not prove every shutdown/concurrency case.

The current `Runtime.cpp` Invoke/InvokeWithThrow guards and HybridCLR interpreter entry/nested/delegate call sites were examined. The helper is an entry guard, not proof that all already-running native/AOT instructions cease instantaneously. A count of guard call sites is not an exhaustive proof of every virtual/interface/generated bridge endpoint.

**K is a meaningful regression, not a vacuous caught-exception test.** `R03TerminalPlayer.cs` resolves and executes the same active instance method and delegate before poison, reads its private primitive counter, and binds an exact native field observer before the failing operation. It then records attempted reflection, delegate and AOT reflective calls. The native field observer checks the actual primitive state after poison, so an exception thrown only after an incorrectly executed method body would not automatically pass.

The directly inspected release-baseline raw record has PID3851, run nonce `4ef7696a0aee47c180f56989e32edfbe`, pre-reflection/delegate values42, `prePositive=true`, all three attempt flags true, all three success flags false, canary1→1 and instance field2→2. State remains9 and first/final recovery retains failure21/RestartRequired. Its raw SHA-256 is `11a6b3c79c862d688f8ce348d84be73f17be36cffffa4635122cbab66ab18e02`. This is affirmative evidence missing from historical S C04.

The original October8 citation erratum is essential: C04's post-poison attempt flags were **absent**, not explicitly false. This review does not repeat the erroneous assertion or recast S's historical test as an observed failure.

**Why the High finding is not closed.** The original finding explicitly required fresh baseline-owner, captured-generic, type-resolution and post-publication initializer failures followed by valid prewarmed business-entry attempts and unchanged first-failure/side-effect evidence. K's child receipt explicitly records `capturedGenericFailure=NotRun`, `initializerFailure=NotRun`, and scope `generic/initializer not covered`. The current C# fixture accepts only baseline-owner, type-resolution and its engine case as ON stimuli. This is a concrete coverage omission relative to the agreed review exit, not a speculative new runtime defect.

The initializer path is particularly nonredundant: the first terminal cause may reside in the transaction recovery record instead of a normal method/type-failure record. Captured generic rejection also follows a different first-failure path. A correct standalone terminal boolean does not prove those producers, their recovery records, and the real call bridges integrate correctly.

**Required closure:** add genuinely source-bound generic and initializer terminal witnesses, preserve pre-positive controls, attempt the applicable supported method/delegate/interface/reflection paths, inspect actual primitive side effects, and preserve the original failure, state and diagnostics. Classify direct interpreter, nested, virtual/interface and ordinary/AOT paths by source evidence and explicit coverage; do not claim a single Func delegate covers every generated bridge. Use Debug/release and ordinary/OFF controls proportionate to the changed path. Reused historical tests require an explicit source/behavioral reuse rationale. This is a test requirement, not authorization to rerun K or create a new output root.

### 3.2 IR-R03-01: documentary contradiction repaired, semantic provenance closure incomplete

The corrected original-S authority is the nine-part, 587,907,380-byte archive SHA-256 `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6`, with15,713 archive members and index SHA-256 `0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70`.

The older five-part, 283,728,477-byte `f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7` family is expressly withdrawn as original-S authority. This satisfies the documentary choice allowed by the original finding: an authenticated transformation was not mandatory if the mismatched claims were explicitly withdrawn. Its unresolved origin alone is not evidence of falsification and is not a reason to demand another Unity batch.

The original provenance correction and K's archive/process audit materially strengthen the original record. K reports90 historical cells,59 historical process joins and preservation of16,978 original-S files. These remain historical source/evidence, not current-native K Players or independent proof that all material generated outputs were linked into their claimed binaries.

**New artifact work in this review.** The generated-source crosswalk artifact11594386600 was downloaded through the Connector, opened locally and SHA-256 checked against `65db909cc7f39b1296f6f11be6bb4d3a3cd44ac1ce3a4f7c5065f311ea89f22e`. Its `results.json` describes four occurrences of two unique generated sources and explicitly has `semanticInspectionCompleted=false`. It is an identity crosswalk, not the complete generated source archive.

The two material identities are `Il2CppGenericMethodPointerTable.c` (Git blob `bf86c8ee7dffe81a23c0b21ccbdc37e7374d414c`,11,350,766bytes) and `Il2CppInvokerTable.cpp` (Git blob `c5a9c6bb34b7a48c000e7c2f16f1b5d4844a4f86`,8,465,159bytes), each in NativeOn/NativeOff backup output. The Connector returned actual invoker source text; limited generated invoker/template structure could be inspected. That must not be overstated as checking every registration row, logical method mapping or compiled/link input. This review did not independently rehash both complete generated sources or close every omission in the original capture index.

The full original-S audit artifact11579112494 could not be downloaded through the exposed action: it returned a response-too-large error. The full original archive was therefore not independently reassembled and rehashed here. This is a verification limitation, not a finding that Local's checksum is wrong. The committed audit results and source identities remain usable evidence, with their actual scope retained.

**Required closure:** finish a read-only, independently checked material-source-to-build-to-executable crosswalk for the original S profile, including the generated tables' relevant mappings, compiler/link receipts and the original capture omissions. Distinguish original archive, capture artifact, generated files and Player identities. Preserve the corrected nine-part authority and withdrawn five-part family. Reuse the already captured raw evidence where intact; only a demonstrated missing or mismatched executable input would justify a proportionate new Local runtime run. Do not impose an unbounded line-by-line review of every generated wrapper as a substitute for material dependency analysis.

### 3.3 Additional scope observation: probe-enabled engine exit is not production shutdown proof

K's engine raw record is authentic scoped evidence of its recorded route: PID3859, nonce `28e2c7de622e417fad6554e36eb90722`,11 completed reports,103ms,one native quit request,one wants-to-quit response,one quit notification,NativeAtexit and exit0. The raw record itself says `ObservedNotAccepted` and `runtimeAcceptance=false`.

The inspected `AssemblyShadowTerminalReporting.h` places the native owner-decision support behind `HYBRIDCLR_R03_RUNTIME_PROBE`. The recorded native decisions deliberately do not execute managed quit bodies/subscribers. The nonengine fixture also exits through its native test reporting path rather than validating ordinary Unity shutdown.

Therefore this result must not be promoted to probe-disabled production lifecycle coverage, full Unity-managed Shutdown, or GC/RSS acceptance. **No new production shutdown failure is established here.** Before any broader claim, document the actual production terminal-owner contract and test that configuration, or retain the explicitly narrower claim. This is a scope/coverage observation attached to RC3/RC5, not an invented additional High runtime defect.

## 4. RC1–RC6 assessment

| Requirement | Assessment in this re-review | Remaining boundary |
| --- | --- | --- |
| RC1: bounded admission/layout | Inspected package metadata screen compares actual DLLs, rejects removed/reordered/changed instance fields and unsupported structural growth, and returns NeedsNativeProof rather than a physical allocation certificate. PureInterpreter expansion remains false. | Native per-platform proof and original bounded cases remain separate. D1-deferred expansion is not silently required or approved. |
| RC2: old resources and Unity ABI | Historical production/resource receipts retain concrete bindings and settings-restoration evidence. K is not a fresh old-resource regression suite. | Material original source/resource/consumer authentication and a reuse/impact analysis for changed common native guards are needed; original M01 NoCoverage is not upgraded. |
| RC3: identity, generic/method entry and poison | Corrected early/late terminal guard; meaningful K pre-positive/attempt/side-effect cases; new standalone policy checks passed. | IR-R03-02's generic/initializer and supported-path coverage remains incomplete. Test-only lifecycle evidence is not universal runtime behavior. |
| RC4: graphs, cumulative patches and roles | Direct `AssemblyReferenceGraph.cs` inspection confirms safety union/reverse closure is separate from target AssemblyRef load ordering. Ordinary hot-update cannot be promoted into a shadow closure. Target cycles use a separate DFS rejection. Historical production cell records five patches and baseline-return roots0. | Not every cumulative fixture or production caller has been newly executed or independently byte-authenticated. Preserve historical scope; do not substitute K's five terminal Players. |
| RC5: characterization and regression | D2 observational scope is respected. K is not a production performance certificate. | Four contaminated warm certificates remain Failed; R02 CPU/H1 RSS risk acceptance and full managed shutdown/global-epoch/GC claims are not supplied by these results. |
| RC6: provenance and stage review | Source/evidence commits separated; non-Docs source trees compared; raw K records and corrected original-S identities inspected. | IR-R03-01 material provenance review and IR-R03-02 closure evidence remain incomplete. No stage acceptance or Human Review Gate approval. |

The package graph source was read directly at blob `63154db05507677dd94b30827a3760f20c4cd52a`; the layout validator at `921756c0ee6282f84c6914599ca1c60ba3d20bad`. The original production-integration cell at fc55 has blob `0a4f22b2824245c983d112d510326c49b9308c0e`, identifies the historical integration SHA `ace3d35b5030eebab2a520f605ba8c2f301f2e1e7cd16b3119fb93b876f29c73`, and records frozen historical ordinary input materialization rather than pretending it was freshly compiled. These are positive observations with bounded scope, not blanket RC acceptance.

## 5. K evidence accounting and prohibited promotions

The published K coordinator/Local records report ten host components,three real builds,five Players,18 child cells,135 source-install pairs,seal/preservation PASS, and the nine exact-demo CI workflows with18 successful OS jobs. These counts are retained. They are not new executions performed by this reviewer. Earlier direct CI API reads in this session occurred during Primary reconciliation; this review does not relabel them as a second set of independent CI runs.

The direct baseline and engine raw records were compared with the current witness source and the published result identities. The current-source manifest pins11 files and the three external source revisions; the standalone header used for the fresh host check matched its actual Git blob. The coordinator's complete-child receipt repair and the ten-host dispatch repair have credible focused K evidence; previous I/J FAIL outcomes remain immutable.

The official135-pair receipt explicitly records `fullNativeIncludeClosure=NotProven`, `generatedCppBinaryLinkage=NotProven` and `PassedInstalledSourceParityOnly`. A matching copied source file is not by itself proof that a specific binary compiled and linked that file. K's complete general sidecar validation likewise records `coherentVmEpochProven=false`. Neither absence is automatically a new product defect, but neither may be represented as a proved stage property.

Whole-VM epoch, P1/P2/E0/E1/P3 completion, complete legacy regression and full managed shutdown are tracked separately. This report does not invent new scope by equating every future diagnostic work item with a newly demonstrated R03 bug. It preserves unproved status and requires an explicit requirement/deferral mapping before stage approval.

## 6. New checks actually executed in this review

A standalone C++11 truth-table harness was written in `/mnt/data/r03_rereview_20261104`, using an exact copy of the fetched `AssemblyShadowTerminalExecution.h`. Before compiling, the Git object SHA-1 was recomputed as SHA1(`blob <byte-count>\\0` + bytes) and required to equal `33258986c31b2e6ae3af17b8553030482a83aef7`. Header SHA-256: `3ff7e1f149090c9869844de9059cc6829bdbf104d93bba5f13dcd09e4f4a08ce`.

The requirement-derived checks enumerate states0–9, durable failure off/on, diagnostic-construction scope off/on and verified fixed-constructor off/on:20 terminal decisions plus80 method decisions. Both GCC14.2.0 and Clang17.0.0 compiled with `-std=c++11 -Wall -Wextra -Werror -pedantic` and returned `checks=100 failures=0`, exit0. The result is **200 checks across two compilers**, not200 distinct runtime scenarios.

Five deliberate local-only mutations each compiled and were detected by the unchanged harness:

| Mutation | Failing checks /100 |
| --- | ---: |
| Omit FailedAfterCommit state | 4 |
| Ignore durable failure | 28 |
| Poison Disabled when durable flag is set | 4 |
| Change constructor scope AND identity to OR | 22 |
| Admit scoped but unverified method | 11 |

These mutant failures are expected negative controls, not failures of repository source. No mutant was committed to production or tested in Unity. The test establishes the pure decision table only: it does not execute `AssertMethodIsActive`, prove placement at every call site, exercise real constructor identity, validate GC roots or reproduce concurrent VM behavior. See adjacent `HOST_CHECK_RESULT.json` and `terminal_policy_review.cpp` for the actual commands and reusable harness.

## 7. Minimum next Primary work, without execution authority

1. **Complete the explicit terminal-failure matrix.** Prepare source-bound captured-generic and post-publication initializer cases, with pre-positive and attempted valid entry, primitive side effects, stable original cause/state and fixed diagnostics. Map the applicable entry families and test configuration, including the distinction between probe-enabled instrumentation and production behavior. Select regression by changed call graph; do not blindly rerun all historical stages.
2. **Finish material provenance reconciliation read-only first.** Independently verify the original S archive/capture/source/build/Player links and material generated tables/omissions. Existing raw evidence should be reused and audited before requesting any further Unity run. Keep current K135 source-install pairs separate from original S executable provenance.
3. **Return for finding-specific review.** Submit exact new evidence and source deltas, not merely an all-green aggregate. Only then can the High findings and applicable RC rows be closed. A separate Human Review Gate remains separately initiated and approved.

This report does not allocate a new Local cycle name, lower a capacity threshold, create an execution root, authorize a retry, or change the closed `WEB_TO_LOCAL.md`.

## 8. Evidence map and final state

All paths below are repository-relative in `hybridclr_demo` unless another repository is named. Review-document links are relative to this report.

- Original review and corrected citation: [October8 report](../INDEPENDENT_FULL_STAGE_REVIEW_2026-10-08.md), [erratum](../INDEPENDENT_FULL_STAGE_REVIEW_EVIDENCE_ERRATUM_2026-10-08.md).
- Governing scope: `Docs/AssemblyShadow/Plan/DESIGN.md`, `Plan/stages/R03-remaining-completion.md`, `Plan/HUMAN_REVIEW_GATES.md`, `S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md`.
- Original-S correction: [provenance](../../IR_Remediation/ORIGINAL_S_PROVENANCE_CORRECTION_2026-10-08.json), [omissions](../../IR_Remediation/ORIGINAL_S_CAPTURE_OMISSIONS_2026-10-08.md).
- K checkpoint: [README](../../local-validation-current-native-original-s-20261103-oneuse-k/README.md), [Local result](../../local-validation-current-native-original-s-20261103-oneuse-k/LOCAL_RESULT.json), [child result](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/current-native/LOCAL_BATCH_RESULT.json), [native parity](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/installed-native-vm-parity.json).
- Direct raw examples: [baseline](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/current-native/players/IR-R03-02-release-baseline/raw.json), [engine](../../local-validation-current-native-original-s-20261103-oneuse-k/batch/current-native/players/IR-R03-02-release-engine/raw.json).
- Witness source at executed c20: `Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs`, blob `e2f650ad95b290620aa52949b43a1866272ac6bf`; `current_native_candidate.json`, blob `45ff575f24567e043a50cca642e030ac0e838786`.
- Native sources at41764: `libil2cpp/vm/{AssemblyShadow.cpp,AssemblyShadowTerminalExecution.h,AssemblyShadowTerminalRejection.h,AssemblyShadowTerminalReporting.h,Runtime.cpp}`; HybridCLR interpreter entry source at4b277; package graph/layout source at948c.

**Final state: return to Primary Implementation for the concrete evidence-closure work above.** K remains focused PASS. This R03 stage-acceptance re-review is FAIL/NeedsEvidence; the historical review remains intact. No new runtime defect beyond the identified incomplete obligations is claimed to have been reproduced.

`R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`; `qualificationApproved=false`; `runtimeAcceptance=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2, M08A, X02, SNAP-01 or other milestone has been started.
