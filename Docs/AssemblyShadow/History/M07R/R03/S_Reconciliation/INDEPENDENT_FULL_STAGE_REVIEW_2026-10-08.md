# Independent Full-Stage Review — HybridCLR Assembly Shadow R03

Date: 2026-10-08  
Role: independent reviewer, separate from Primary Implementation and Local Validation  
Overall verdict: **FAIL**  
Scope: **R03 only**. No H2 approval, R03 acceptance, X02 implementation, M08A work, or new Local Validation execution.

## 1. Executive decision

The reviewed implementation contains substantial conservative admission, identity, staging, graph, and diagnostic work. D1=A and D2=A are reasonable boundaries for evaluating this particular R03 submission: neither unrestricted PureInterpreter structural evolution nor a production performance SLA is required to pass this bounded review. Neither decision, however, waives terminal-failure enforcement or trustworthy evidence-to-source binding.

This review identifies two acceptance-blocking findings, presented in runtime-risk order below:

| ID | Severity | Finding | Basis |
| --- | --- | --- | --- |
| IR-R03-02 | High | Supported method-entry guards can admit an otherwise valid method after the transaction has already entered a terminal failure state. | Direct inspection of the native guard and interpreter entry chain; static counterexample, not a newly executed Player reproduction. |
| IR-R03-01 | High | The Primary S reconciliation names a different original archive, index and result digest set from the committed S checkpoint it claims to reconcile. | Direct comparison of pinned JSON records, plus inspection of the actual capture and reauthentication workflow logs. |

The first finding prevents RC3 closure. The second prevents RC6 evidence authentication and therefore prevents an independent full-stage PASS even without the runtime finding. Some verification work is additionally **BLOCKED/incomplete**, as documented in Section 9; that limitation is not disguised as a product defect or as a completed audit.

**The historical S result remains recorded as 90/90 Passed.** This review does not edit that result or assert that the recorded execution failed. It rejects the inference that those green cells establish all R03 requirements, and it does not authenticate the contradictory archive identities as interchangeable.

The following remain unchanged and unapproved:

```text
R03Accepted=false
H2Passed=false
qualificationApproved=false
ReadyForHumanReviewGate=false
PureInterpreter structural expansion disabled
```

No owner decision is needed to explain away either finding. Primary Implementation should remediate them and return for independent re-review. A later independent PASS would still not constitute the separately user-initiated Human Review Gate.

## 2. Immutable review inputs and access

All four repositories use `codex/assembly-shadow-r01b-h1`. Repository identity and branch existence were verified through the GitHub Connector before source review. Fresh `git/ref/heads/codex/assembly-shadow-r01b-h1` reads immediately before publication returned the same four HEADs.

| Repository | Immutable review commit | Remote HEAD before publication |
| --- | --- | --- |
| [night-outlook/hybridclr_demo](https://github.com/night-outlook/hybridclr_demo) | `aee7975874a5ddf236ab9d00d5d682b470010f8f` | Identical |
| [night-outlook/hybridclr](https://github.com/night-outlook/hybridclr) | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` | Identical |
| [night-outlook/hybridclr_unity](https://github.com/night-outlook/hybridclr_unity) | `948c0e3b4f8891481301770115e8ba4945eea6de` | Identical |
| [night-outlook/il2cpp_plus](https://github.com/night-outlook/il2cpp_plus) | `1cf87f8209790f9fb2ebec97487dc1990ccd56c5` | Identical |

The relevant demo revisions are distinct, not alternative names for one build:

- S execution: `29bb3d4a39bf8a2f23be404f77535aaba3485bfc`.
- S evidence publication: `fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b`.
- Current governing documentation and owner disposition: `aee7975874a5ddf236ab9d00d5d682b470010f8f`.

The Connector comparison of `fc55d8b8...` to `aee79758...` returned `ahead`, 19 commits, zero commits behind, and merge base `fc55d8b8...`. Its 18 changed paths are under `Docs/AssemblyShadow`; no product source or S checkpoint path is in that comparison. This rules out a subsequent change to those checkpoint records as an explanation for IR-R03-01 in the inspected descendant range. It is not a substitute for authenticating the earlier execution/build binding.

### Reviewer environment and independence

Reads used the connected GitHub repository/ref, commit comparison, tree, pinned file, and GitHub Actions log/artifact APIs. Product source was read directly at the immutable commits, not inferred solely from Primary's capture or prose. Source excerpts were requested with explicit source line ranges. JSON field paths below disambiguate evidence locations where a whole receipt is the relevant unit.

No Unity installation, Player, IL2CPP build, local compiler test, or new validation batch was run. Container execution was unavailable (`ClientError`, including a trivial executable probe). An Actions capture artifact was retrieved through the Connector, but this environment did **not** successfully unpack and independently hash its complete bytes. Accordingly, no claim is made that this reviewer recomputed the archive digest, verified every indexed member, or semantically checked all 90 cells.

Reading a workflow log establishes what that workflow recorded, not that this reviewer independently reproduced its calculations. Reading a Local receipt establishes the committed record, not direct observation of the original Mac filesystem. These distinctions materially affect the verdict.

### Connector write smoke test

A disposable branch was created from `aee7975874a5ddf236ab9d00d5d682b470010f8f`:

```text
Repository: night-outlook/hybridclr_demo
Branch: codex/review-smoke-r03-20261008-8ac7d921
Commit: 191b2a5d3a97cb4ddff093775069e18cbfd27b2e
File: Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/SMOKE_REVIEW_2026-10-08_8ac7d921.md
```

The harmless documentation commit was written through the Connector, its contents were read back, and its exact branch HEAD was verified remotely, including a fresh verification before formal publication. **Smoke test: Passed.** The exposed Connector supports file deletion but not branch deletion; the disposable branch remains. It must not be merged into the feature branch. It is not runtime or acceptance evidence.

This formal publication adds only this new review document. The documentation publication commit is distinct from all four review inputs and from the smoke commit; the resulting remote commit and changed-path readback are reported with the publication response.

## 3. Governing design and plan assessment

The required first-read order was followed: `README.md`, `Plan/CURRENT_STATUS.md`, `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and `Handoff/WEB_TO_LOCAL.md`. The governing design, both R03 stage plans, ADR-0002, Human Review Gates, owner disposition, bounded exit matrix, independent review request/addendum, Primary reconciliation/full-stage review, and evidence index were then read. Additional implementation and raw evidence references were followed independently.

### 3.1 Supported, rejected and deferred scope

The current design and ADR distinguish a conservative `NativeLayoutAdmissionV1` envelope from an eventual PureInterpreter expansion. The code inspection supports that distinction: the static eligibility report is non-authorizing, while native staged validation and physical-layout checks remain required. A report classifying something as potentially PureInterpreter is not a license to expose arbitrary changed physical layouts.

D1=A is reflected in the current governing disposition and bounded exit matrix. Outside-V1 private-reference addition/removal remains deferred to separately gated X02. The negative C02 result must not be converted into a structural-expansion qualification. Similarly, C07's private-primitive append evidence concerns the specific admitted physical-layout case, not unrestricted field addition.

D2=A is reflected as an observational-only measurement boundary. Current development-profile timing and memory observations do not approve a production threshold, resolve the deferred R02 CPU/H1 RSS risks, or rehabilitate the four contaminated unisolated-warm certificates. The older Primary evidence snapshot still contains then-pending owner decisions; it must be interpreted chronologically alongside the newer owner disposition, not silently rewritten as a current decision record.

### 3.2 Core requirements that still apply

The design requires one active logical world, private staged metadata until publication, preservation of physical ownership, a baseline-use barrier, complete method identity rather than token/slot coincidence, conservative native allocation admission, and fail-closed execution after terminal failure. Installed-baseline change roots and the safety closure must remain distinct from the target's actual load graph. Resource reuse requires actual old asset/schema compatibility, not merely a successful new asset build.

The plans express these concerns in RC1–RC6. Their dependency structure is sound at a high level: an eligibility report cannot override layout validation; a graph report cannot substitute for production integration; measurement completion cannot substitute for source provenance; and Primary's review cannot close the independent-review gate.

The substantive design-to-implementation mismatch is the persistence of poison at supported business entry, described in IR-R03-02. D1 and D2 do not narrow that requirement away.

### 3.3 Stage closure

The bounded exit matrix is an appropriate claim boundary, but not evidence that every row has independently passed. RC6 is not closed merely by adding this document: its verdict is FAIL and its evidence authentication has unresolved limitations. No stage flag should be advanced from the fact that a review document now exists.

## 4. RC1–RC6 traceability matrix

Source paths in this table are expanded in Section 10. `S checkpoint` means the immutable committed directory defined in Section 6. Results here are the independent assessment, not replacements for Local's recorded statuses.

| Requirement | Implementation inspected | Evidence inspected and its limit | Independent assessment |
| --- | --- | --- | --- |
| **RC1 — bounded eligibility/admission** | Package `PureInterpreterEligibility`, `NativeLayoutAdmissionValidator`; native `ValidateStagedImage` and `CheckStagedPair`; HybridCLR staged metadata finalization. Static reports do not grant runtime authority. | C02 private-reference rejection and C07 private-primitive append verification; owner D1; ADR-0002 and bounded exit matrix. No new qualifying structural-expansion run. | Conservative design/code alignment in inspected paths. C02 is a **tested rejection**; C07 is a bounded positive case. Outside-V1 expansion **deferred**, not Passed. Full qualification remains false. |
| **RC2 — original resources and Unity ABI** | Logical/public identity is separated from physical allocation in the native resolver; old-field prefix/offset and physical compatibility checks; package manifest construction. | Committed `resource-contracts.json`, integrated build bindings and resource summaries were read. The original assets and every runtime schema consumption path were not independently rehashed/exhaustively traced here. | Bounded compatibility is plausible and recorded tests are positive, but not a blanket independent old-resource/ABI approval. Full closure remains **unproved** pending the custody/coverage work in Section 9. |
| **RC3 — type/method identity and runtime safety** | Full native type resolver, core native transaction/guard implementation, `Runtime::Invoke` path, HybridCLR interpreter entry/frame guard, staged loader and bridge. | C04 old-AOT guard and transaction-recovery raw verification; C02/C07 diagnostics. C04 explicitly does not attempt the new method after the old-method failure. | **FAIL: IR-R03-02.** First rejection and restart/reload refusal do not prove that later valid business entry is rejected in a poisoned transaction. |
| **RC4 — installed-baseline graphs, roles, P01–P05** | `AssemblyReferenceGraph`, generation plan and production manifest builder. Reverse safety closure and actual forward target graph are separate operations; installed-baseline inputs are used in construction. | Production integration cell plus underlying `integration.json`; exact-settings restoration and empty return roots/closure are recorded. Not every integration caller/fixture and cumulative-change case was exhaustively re-executed or independently byte-authenticated. | Positive structural inspection and direct receipt corroboration. **No new graph defect established**. Independent end-to-end closure remains bounded by IR-R03-01 and coverage limitations. |
| **RC5 — timing/memory characterization** | D2 governing scope; receipt/audit organization and integrated-detail audit script. No claim of a new performance implementation or benchmark. | Recorded six builds, twelve measurement Players, strict-warm summaries and four retained Failed contaminated certificates; workflow logs inspected. Not all raw sample series independently recomputed. | **Observational-only**. No production SLA, noise threshold, CPU-risk acceptance or RSS-risk acceptance. Failed contaminated certificates remain Failed. |
| **RC6 — source freeze, provenance and independent review** | Fixed tuple, fresh remote ref authority, documentation-only descendant comparison, direct source access and independent review process. | Original transport/seal/postrun records contradict Primary's archive identity; capture and reauthentication workflow logs were inspected; full local artifact reauthentication could not be completed. | **FAIL: IR-R03-01**, with archive/omission sub-audits **BLOCKED/incomplete**. No independent approval or Human Review Gate readiness. |

## 5. Runtime and integration technical assessment

### 5.1 Active-world, logical and physical identity

The native resolver does not simply rename an AOT type and assume physical compatibility. It resolves logical definitions, generic instantiations, arrays/by-reference forms and methods while separately validating allocation/exposure against physical classes. Method matching includes signature/declaring identity and generic context rather than assuming metadata tokens or virtual slots are stable across builds. Ambiguous or unsupported resolution is rejected rather than guessed.

The old instance-field prefix, offsets, reference/value distinctions, parent/interface restrictions and V1 append constraints are meaningful safeguards. A cached layout proof is not a permanent exemption: allocation admission also rechecks generation, baseline use, private metadata scope and terminal state. This is a positive distinction from the method-entry defect: **IR-R03-02 is not a claim that every allocation path ignores poison**.

The logical/public image path and Unity-facing identity require careful separation from the class/image that owns actual native metadata. The inspected resolver/bridge/API paths preserve that separation in their intended use. This review does not infer that all uninspected Unity native API consumers inherit the same guarantee automatically.

### 5.2 Reflection, generics, interfaces and delegates

The inspected reflection resolver maps methods using logical identity, and the native invocation path checks method/class ownership before invoking. Generic guarding inspects actual captured class and method contexts, not just the assembly that declares a generic method. That is necessary for an unchanged generic owner capturing an obsolete baseline type.

The implementation's rejection of stale captured arguments must not be advertised as universal transparent remapping of every generic/interface/delegate path. The resolver and interpreter entry checks support the intended bounded design, but this review did not independently enumerate every virtual/interface thunk, generated delegate bridge, reflection overload or reverse invocation endpoint. Their complete profile-specific coverage remains an explicit re-review obligation, particularly after changing the common entry guard.

The most important counterexample is not ambiguous method matching. It is an already resolved, otherwise valid method being invoked after a prior caught failure: identity can be valid while the transaction is terminal. These are separate predicates.

### 5.3 Staging, publication, retention and recovery

HybridCLR's staged loader validates the borrowed PE/CLI envelope before retaining owned metadata, builds private staged identities, binds staged references without an accidental public-baseline fallback, and invokes the native V1 validation before publication. The metadata bridge has an explicit handled/private resolution boundary; a handled failure is not equivalent to permission to fall through to a public lookup.

Native candidate registration, baseline-use observation and publication share the intended ordering barriers. The active snapshot is published as a unit rather than exposing arbitrary partially loaded candidates. Module initializers are post-publication execution and can therefore produce `FailedAfterCommit`; retaining metadata and requiring restart is distinct from rolling back the published world.

The staged-loader and native recovery implementations retain monotonic metadata/index consequences rather than pretending failed stages are free to unload and retry indefinitely. The recovery receipts support refusal/restart behavior for staging, abort and initializer failure cases. They do not establish refusal of all later business calls after poison; that is precisely the missing predicate in IR-R03-02.

### 5.4 Graphs and P01–P05

The inspected package code distinguishes the union used for reverse safety reachability from the target's actual forward dependency graph used for load ordering and cycle detection. A cycle in a real target graph cannot be dismissed because the safety closure is a set; conversely, a union of historical and current edges must not invent a load cycle that no target has. Assembly roles and ordinary inputs are not interchangeable with shadow candidates.

The production integration receipt records changed roots `Target`, safety closure `Observer, Target`, and target load order `Target, Observer`. It records preservation of the ordinary role and retained bootstrap exception. The P05 return state records no roots and no closure, rather than comparing only to the immediately preceding patch and inventing a cumulative change.

Both the production-cell receipt and underlying integration receipt were read. They are concrete positive evidence for the asserted restoration/return behavior, not just a Primary prose statement. They still do not prove every cumulative-change or cycle fixture was correctly constructed, nor resolve the independent archive binding discrepancy.

## 6. Evidence authentication and historical limitations

For this section, the **S checkpoint** is:

[`Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready`](https://github.com/night-outlook/hybridclr_demo/tree/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready).

All receipt links below use the fixed demo review commit. A mutable local cache, an uncommitted Mac file, or a matching short hash prefix is not substituted for it.

### 6.1 What was directly authenticated as a committed record

The following were retrieved directly, rather than only read through Primary's review:

| Record | Direct observation | What it does not establish |
| --- | --- | --- |
| `FILE_TRANSPORT.json` | Original sizes, full SHA-256 values and ordered part records are present. The original archive is described as nine parts totaling 587,907,380 bytes. | This reviewer did not concatenate/hash all part bytes. |
| `batch/seal-receipt.json` | Archive hash agrees with the transport record; index hash and 15,713 member count are explicit. | A seal label alone is not independent byte verification. |
| `preflight/POSTRUN_AUTHENTICATION.json` | The inspected portion records Passed, 90 Passed cells, 15,712 indexed files/15,713 members and raw command receipts. | The entire 80 KB record and every associated command output were not semantically checked here. |
| `CHECKPOINT_VERIFICATION.json` | Local copy/checkpoint verification is committed and records exact-copy/transport checks. | No direct access to the live excluded Mac roots was obtained. |
| `preflight/INTEGRATED_DETAILS.json` and `integrated-details.py` | Build/source bindings and the audit assertions were inspected, including the intentional reference-control tuple distinction. | Running or reading an audit script is not independent runtime approval; this reviewer did not rerun it. |
| `batch/cells/production-entry-integration.json` and underlying `integration.json` | P05 exact-restoration claims, return roots `[]`, closure `[]`, and no-op return are explicit. | The original settings bytes were not independently hashed by this reviewer. |
| C02, C04 and C07 Player verification receipts | Specific negative and bounded-positive outcomes can be examined separately from the 90-cell total. | These few receipts do not authenticate all 59 fresh process histories or prove unrelated requirements. |
| `batch/transaction-recovery/verification.json` | Thirteen recovery cases record bounded failure/restart/ordinary-control behavior. | Reload refusal is not a post-poison business-entry test. |
| `batch/resource-contracts.json` and producer-control excerpts | Resource/producer checks are committed and inspectable. | Not every serialized asset, binary library, raw measurement row or strict schema consumer was independently audited. |

The 6-build, 59-fresh-Player, 18/754/755-Editor accounting is present in the Local/Primary summaries and captured audit output. This review preserves that accounting as recorded, without promoting it to a newly recomputed independent result.

The candidate/reference build comparison intentionally includes different native source commits for the reference control. A control tuple is not automatically a provenance defect merely because it differs from the candidate tuple. Candidate/reference identity must be checked per build and process; it cannot be collapsed into one global source label.

### 6.2 Original versus capture archives

The Actions ZIP is not the original S tar archive. Capture run [37735479304](https://github.com/night-outlook/hybridclr_demo/actions/runs/37735479304), job `113173910187`, checked out the stated source pins and executed a transport/seal audit. Its inspected log includes the audit script, pinned checkout outputs and artifact upload receipt:

```text
Capture artifact ID: 11531491593
ZIP size: 405960931
ZIP SHA-256 recorded by Actions:
a323402ec537537c0c1ce71519ffd210167260db42f1ee977597c94a195af35f
```

Reauthentication run [37740248886](https://github.com/night-outlook/hybridclr_demo/actions/runs/37740248886), job `113189051409`, actually ran and recorded a successful audit. Its log was read. It reports the 18,159/18,160, five-part, `f4c2a120...` archive family used by Primary. Therefore this review does **not** claim the automated audit never ran. The problem is that those recorded identities do not agree with the frozen checkpoint's own original transport/seal records, as detailed below.

A correct hash of a capture ZIP does not resolve an inconsistent claim about the original S archive inside its provenance chain. The raw checkpoint, captured input, audit script, audit output and current summary must be joined by a full-digest crosswalk. Similar prefixes, a green Actions conclusion, or the phrase “independently verified” do not provide that join.

### 6.3 Historical states

R, earlier failed/blocked evidence, and contaminated warm certificates remain historical records. None was restored, edited, rerun, deleted, or relabeled by this review. The four contaminated unisolated-warm certificates remain **Failed**; they are not converted to Passed by the existence of isolated diagnostic measurements. Deferred R02 CPU and H1 RSS risks remain deferred/unaccepted here.

The Local historical-custody receipts are relevant evidence but are not a fresh independent scan of every retained/cache path on the original workstation. No claim is made that this reviewer inspected all 228,702 live paths described by Primary's summary.

## 7. Concrete findings, ordered by runtime severity

### IR-R03-02 — High — Existing terminal poison is not enforced at supported method entry

**Violated requirement:** `Plan/DESIGN.md`, terminal-failure behavior table: when a business caller catches a guard exception, state must not recover and supported business entry must continue to recognize poison; fixed diagnostics may remain available. RC3 also requires poisoned-transaction safety. D1/D2 do not waive it.

**Exact primary location:** [il2cpp_plus `libil2cpp/vm/AssemblyShadow.cpp`, lines 1572–1746](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/AssemblyShadow.cpp#L1572-L1746), functions `AssertMethodIsActive`, `RequireActiveMethod`, `RequireUserCodeAllowed`, and `FailTypeResolution`. Git blob: `08fd924a91fbd9701b50ac45ea7846f0bedd9a8c`.

**Affected direct call chain:** [HybridCLR `Interpreter_Execute.cpp`, inspected entry range 1590–1750](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/Interpreter_Execute.cpp#L1590-L1750), `Interpreter::Execute` → `REQUIRE_ACTIVE_METHOD` → native `RequireActiveMethod`; [HybridCLR `Engine.cpp`](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/Engine.cpp), `InterpFrameGroup::EnterFrameFromInterpreter` → `RequireActiveMethod`. The managed/reflection invocation chain was also inspected in [native `Runtime.cpp`, lines 540–760](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/Runtime.cpp#L540-L760) and HybridCLR `InterpreterModule.cpp`.

**Reasoning:**

1. `AssertMethodIsActive` checks physical ownership, obsolete baseline method identity and actual captured generic arguments. It returns `true` immediately when the current method produces `Success`.
2. That success path does not inspect an already stored terminal transaction state or an existing first/type failure.
3. `RequireActiveMethod` consults `s_typeFailure` only after `AssertMethodIsActive` returns false. An otherwise valid active method therefore does not reach that failure branch merely because an earlier call poisoned the transaction.
4. `RequireUserCodeAllowed` checks staging/private type-metadata resolution. It does not check `Failed` or `FailedAfterCommit`.
5. The inspected interpreter entry and frame-entry path uses these same guards. With an already prepared, otherwise valid method and no new allocation/layout exposure, there is no demonstrated terminal-state predicate before entering its bytecode.

This separates two conditions the implementation currently conflates: “this method's identity is valid in the published world” and “business execution is still permitted in this transaction.” The former can remain true after the latter becomes false.

**Static counterexample to validate:** publish a valid bounded shadow world; retain an already resolved/prewarmed, allocation-free active static method with an observable side effect; trigger and catch a supported baseline/captured-argument guard failure so state becomes `FailedAfterCommit`; invoke that valid method through the supported interpreter/invocation entry. The inspected guards admit its valid identity without rejecting the existing poison. Use a void/nonallocating body to avoid accidentally testing only the separately guarded allocation path.

This is a **source-derived defect**, not a claim that a new reproduction was executed in this review. Entry paths that independently reject terminal state, such as the guarded allocation path, do not invalidate this counterexample at a different entry.

**Existing evidence gap:** [C04 old-AOT guard verification](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/players/C04-old-AOT-guard/verification.json) records the old method throwing and terminal state, but explicitly records `newMethodInvocationAttempted=false` and `newMethodInvocationSucceeded=false`. Those values are not a negative test of attempting a valid post-poison call. The recovery receipt's restart/reload refusals likewise do not exercise this counterexample.

**Required correction:** Primary Implementation should introduce a common, explicit terminal-execution predicate at supported business entries while preserving an explicit fixed-diagnostic allowance, metadata private-scope restrictions and the original first failure. Do not clear poison to permit diagnostics. Do not broadly block ordinary/OFF execution without regard to the protocol. Review reentrancy, exception construction and no-allocation guard paths to avoid recursive failure handling.

**Required regression:** fresh process cases for caught baseline-owner failure, captured-generic failure, type-resolution failure and post-publication initializer failure; then attempt a valid prewarmed allocation-free active method through interpreter, reflection and applicable delegate/interface entry. Assert no side effect, unchanged first diagnostic/state/world identity, and continued allowed fixed diagnostics. Include Debug ON, release ON and OFF/ordinary controls. Add a pre-poison positive call so the test cannot pass merely because its target was never callable.

### IR-R03-01 — High — The reconciled S archive identity contradicts the committed original checkpoint

**Violated requirement:** RC6 source/build/test binding, raw archive custody, and a reproducible review evidence index. A review summary cannot substitute a different artifact family for the fixed committed S checkpoint without an explicit, verified transformation/crosswalk.

**Exact locations:**

- [S_Reconciliation/EVIDENCE.json, lines 19–52](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/EVIDENCE.json#L19-L52): `localBatch.checkpoint`, `originalArtifacts`, `archiveVerification`. Blob `45cdc9192461330a09779f55e4391facfc994f61`.
- [S checkpoint FILE_TRANSPORT.json](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/FILE_TRANSPORT.json): `files[]` rows selected by `originalPath`, especially `batch/evidence.tar.gz`, and their `originalSize`, `originalSha256`, `parts`. Blob `42a97f1a58f38e3b1b27885691f5086b5eb09c24`.
- [S checkpoint batch/seal-receipt.json, lines 1–7](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/seal-receipt.json#L1-L7): `archiveSha256`, `indexSha256`, `members`. Blob `0f28f7f5445385d815f0740ecde8e9dfa29c78ad`.

**Observed contradiction:**

| Artifact property | Primary reconciliation | Committed S checkpoint |
| --- | --- | --- |
| Original archive SHA-256 | `f4c2a120e3fdbb1fbc5a984e920ba0dbf34a3e1502c3ecea955769d70179054a7` | `23aedcaf54e67a07a93853dcca299ddbc69cc0c1a91b7149e21fd254ea6ae9f6` |
| Original archive bytes | 283,728,477 | 587,907,380 |
| Original archive transport parts | 5 | 9 |
| Index SHA-256 | `f1d13ab3c4c3c49d8608454f0421580e9e4783e52a7b89a3a9e22f2c695bfafb` | `0685d23a40b581cc7d22abc543c7d9067e808a0f25fa0b3f2aea32966b22bd70` |
| Archive members | 18,160 | 15,713 |
| Indexed files | 18,159 | 15,712 in postrun authentication |
| LOCAL_BATCH_RESULT.json SHA-256 | `2e09a5bfc0b4ad72b4fac9376fb2e73070a518082763356a3503842fe9cf8c46` | `2e09d46c800d7721eb14a6d7a31ba1d89327d1126ff7f7be35dd889bdbdf3096` |
| BATCH_EXECUTION.json SHA-256 | `7b5fa01ebf6d068841c9d2fab03caedbc7f1c14e3c58f67763d3f8a15dcfb068` | `241144d39b1cfa47be3dcd4f67a3e40f7608ab58d605117c81fcccea8c68a427` |

The raw transport and raw seal agree with each other on the archive hash; the raw postrun record agrees with the seal's member/index cardinality. The Primary index points to that same checkpoint directory but reports different full digests and cardinalities. The `fc55d8b8...` → `aee79758...` comparison contains no edit to these checkpoint paths.

The reauthentication workflow log genuinely reports a Passed audit of the Primary-described family. That is additional evidence of an unresolved binding problem, not permission to prefer its summary over contradictory pinned raw records. The discrepancy cannot be resolved by counting 90 green cells in both places or by confirming only the outer Actions ZIP hash.

**Impact:** an independent reviewer cannot currently tell from this reconciliation whether the purported original archive, all 90 cell records, source bindings and detailed claims refer to the frozen checkpoint bytes or to another capture/transformation. This blocks RC6. It does not prove that Local's runtime execution failed, nor establish motive or deliberate alteration.

**Required correction:** append a new corrective reconciliation, preserving all historical files. It must identify the exact provenance of both digest families and either provide a byte-authenticated transformation/crosswalk or explicitly withdraw the mismatched claims. Reconstruct the committed original parts read-only; verify full sizes/digests, index membership/uniqueness and raw result/ledger equality; bind every cell to its process/build/source tuple. Record audit script commit, exact input commit, original archive digest, capture digest and output artifact identity as separate fields. Reconcile full P05 and source/build receipt identities, not hash prefixes. Do not retroactively alter Local-owned receipts or rewrite an old Failed/Passed result to make the index agree.

**Required regression/re-review:** a read-only provenance audit, not necessarily another Unity batch, is sufficient for this documentation/custody correction if the original raw evidence is intact and binds to unchanged executable inputs. An independent reviewer must inspect the corrected original-to-capture join and material omitted sources. If the join exposes missing evidence or changed executable inputs, additional proportionate Local Validation is then required. A successful automated digest script alone is not the independent approval.

## 8. Claim classification and residual risks

| Classification | Claims that belong here |
| --- | --- |
| **Supported within the inspected design/code envelope** | V1 admission only; logical identity distinct from physical layout; complete logical method matching rather than token coincidence; private staged reference resolution; separation of reverse safety closure and actual target load graph. This category is not a full runtime acceptance verdict. |
| **Tested rejection** | C02 outside-V1 private-reference staging rejection; C04 obsolete-baseline guard rejection; bounded restart/reload rejection after retained failed metadata. A rejection test does not prove the rejected operation is supported. |
| **Bounded positive evidence** | C07's particular private-primitive append case and native physical proof; P05 exact-settings restoration and empty restored-baseline roots/closure as recorded. Neither generalizes to all structural changes or all fixtures. |
| **Deferred** | Outside-V1 PureInterpreter structural expansion, including the owner-deferred private-reference field addition/removal, and separately gated X02 qualification. X02 is not Passed and was not begun. |
| **Unproved / not independently closed** | Business entry after caught terminal failure; the contradictory original-to-capture archive join; complete recovery of capture omissions; all 90 cells' source/process/build joins; exhaustive original-resource and strict runtime-schema consumer coverage; every platform/generated generic-interface-delegate endpoint. |
| **Observational-only** | Current development-profile timing/memory data, storage samples and diagnostic counters. No approved production performance SLA, release threshold, CPU-risk disposition or RSS-risk disposition follows. |

C02's diagnostic receipt itself says the failing row/logical type was not identified and that target validation did not complete. That is a diagnostic limitation, not evidence that a valid outside-V1 target was incorrectly rejected. Improved row-level diagnostics would help future X02 work, but this review does not elevate that limitation into a new R03 expansion requirement.

The recovery design also carries deliberate costs: retained failed metadata, quotas, restart requirements and a first-failure diagnostic policy. Passing selected recovery cases does not establish unbounded retry safety or memory reclamation. No such claim is approved here.

## 9. Incomplete verification and access blockers

These limitations are part of the review result, not hidden assumptions:

1. **Full original/capture byte authentication was not completed independently.** Connector artifact retrieval worked; container execution/unpacking did not. Raw committed receipts and workflow logs were inspected, but their computations were not rerun by this reviewer. IR-R03-01 would block acceptance even in an otherwise fully functioning review environment.
2. **Capture omission recovery is not closed.** Primary reports two oversized source omissions. The capture workflow log shows its bounded export policy and an omissions inventory, but this reviewer did not successfully unpack that complete inventory and retrieve every omitted material file. Core native guards, resolver, staged loader, interpreter entry and package policy code were fetched directly, independently of the capture. That does not establish that every omitted source was recovered. The corrected evidence index must name the omissions with repository/commit/blob/path/size and record direct review of all material ones.
3. **Not all 90 cells were independently joined and semantically audited.** This report examined the critical receipts described above and traced counterexamples; it does not claim exhaustive raw stdout/XML/process authentication for six builds, 59 Players and all Editor cases. The counts remain Local-reported/corroborated counts.
4. **Full resource and generated-call-path coverage remains bounded.** The review covered central identity/admission mechanisms and selected resource evidence, not every original asset's bytes, every strict schema consumer, or every generated interface/delegate bridge. These are acceptance gaps to close, not invented defects in uninspected code.
5. **Historical live filesystem custody was not independently observed.** GitHub-committed authority was used throughout. No retained R restoration, local cache mutation, workstation scan or new Local Validation was performed.

Consequently, this report provides a cross-repository, full-stage assessment with concrete blocking findings and a declared inspection boundary. It does not claim a completed exhaustive certification. The appropriate overall verdict is **FAIL**, not PASS; the incomplete provenance/coverage sub-audits remain BLOCKED/unproved until corrected and independently inspected.

## 10. Source and evidence inspection index

All native/package links below use the immutable tuple. Ranges identify material portions inspected; a range is not a claim that every other line in that file was reviewed.

| Repository / source | Inspected implementation concern |
| --- | --- |
| [il2cpp_plus — AssemblyShadow.cpp](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/AssemblyShadow.cpp) | Core implementation read across candidate setup, transaction staging/validation/publication, baseline-use observation, terminal state, diagnostics, method/class guards and wrappers; especially 1490–1880 for IR-R03-02. |
| [il2cpp_plus — AssemblyShadowTypeResolver.cpp](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/AssemblyShadowTypeResolver.cpp) | Logical definition/type/method resolution, physical V1 admission, old field compatibility, staged-pair checks, reflection and allocation cache/terminal rechecks. |
| [il2cpp_plus — Runtime.cpp](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/vm/Runtime.cpp#L540-L760) | Reflection/invocation ownership checks and interpreter dispatch. |
| [il2cpp_plus — il2cpp-api.cpp](https://github.com/night-outlook/il2cpp_plus/blob/1cf87f8209790f9fb2ebec97487dc1990ccd56c5/libil2cpp/il2cpp-api.cpp#L170-L355) | Selected public class/image/type API identity boundary; not a complete API-surface audit. |
| [hybridclr — AssemblyShadowBridge.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/metadata/AssemblyShadowBridge.cpp) and header | Private staged resolution, handled failure and public physical identity boundary. |
| [hybridclr — Assembly.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/metadata/Assembly.cpp) | Ordinary image ownership/retention, publication and initializer ordering; selected loading ranges. |
| [hybridclr — StagedAssembly.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/metadata/StagedAssembly.cpp) | Borrowed-byte envelope checks, private metadata ownership/reference binding, finalized layouts, native V1 validation and post-publication initializer handling. |
| [hybridclr — InterpreterModule.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/InterpreterModule.cpp#L1-L430) | Managed/reflection-to-interpreter entry and guard placement. |
| [hybridclr — Interpreter_Execute.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/Interpreter_Execute.cpp#L1590-L1750) and [Engine.cpp](https://github.com/night-outlook/hybridclr/blob/4b2774b066cfc6afd77a8c8aded6bda7ea574f55/hybridclr/interpreter/Engine.cpp) | Actual interpreter entry, cached method/frame entry and guard macro/caller; not every opcode. |
| [hybridclr_unity — AssemblyShadowRuntime.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Runtime/AssemblyShadow/AssemblyShadowRuntime.cs) | Managed native API boundary and diagnostics/mode semantics. |
| [hybridclr_unity — NativeLayoutAdmissionValidator.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Metadata/NativeLayoutAdmissionValidator.cs) | Conservative managed admission and changed-layout rejection. |
| [hybridclr_unity — LogicalMethodIdentity.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Metadata/LogicalMethodIdentity.cs) | Complete logical method identity, overload/generic distinctions. |
| [hybridclr_unity — PureInterpreterEligibility.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Metadata/PureInterpreterEligibility.cs) | Qualification remains false; bounded source-domain reopening and static non-authority. |
| [hybridclr_unity — AssemblyReferenceGraph.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Metadata/AssemblyReferenceGraph.cs#L1-L250) | Safety union/reverse closure versus target graph/load cycle semantics. |
| [hybridclr_unity — ShadowGenerationPlan.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Generation/ShadowGenerationPlan.cs#L1-L245) | Compile-only/nondeployable plan, captured inputs and strict canonical plan representation. |
| [hybridclr_unity — ShadowPatchManifestBuilder.cs](https://github.com/night-outlook/hybridclr_unity/blob/948c0e3b4f8891481301770115e8ba4945eea6de/Editor/AssemblyShadow/Build/ShadowPatchManifestBuilder.cs#L1-L270) | Installed-baseline change computation, graph/role inputs, resource/admission integration; selected production construction range. |
| hybridclr_demo — required governing documents and S checkpoint records listed in Sections 3/6/7 | Owner boundaries, RC dependencies, test intent and direct raw receipt comparison. Primary prose was treated as a claim to verify, not independent approval. |

Useful immutable evidence entry points: [Primary evidence index](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/EVIDENCE.json), [owner disposition](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/OWNER_DISPOSITION_2026-10-08.md), [bounded exit matrix](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/S_Reconciliation/BOUNDED_R03_EXIT_MATRIX.md), [production integration receipt](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/cells/production-entry-integration.json), [C02](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/players/C02-private-reference/verification.json), [C07](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/players/C07-private-primitive-append/verification.json), [transaction recovery](https://github.com/night-outlook/hybridclr_demo/blob/aee7975874a5ddf236ab9d00d5d682b470010f8f/Docs/AssemblyShadow/History/M07R/R03/local-validation-20261007-batch-s-evidence-ready/batch/transaction-recovery/verification.json).

## 11. Primary Implementation remediation and re-review contract

### Step A — Correct and rebind the evidence, without rewriting history

Append a provenance correction addressing IR-R03-01. Preserve both old digest families and all original statuses. Establish the exact authoritative original S archive and execution tuple, show the original-parts/index/result/ledger/capture joins, and inventory all omitted material source. Reconcile P05 restoration, build profiles, reference controls and raw process receipts with full identities. Do not authorize a new Unity batch merely to conceal a documentation or transport mismatch.

Exit: another reviewer can retrieve the exact source and raw evidence and reproduce the join. An automated byte audit is a prerequisite, not the independent verdict.

### Step B — Fix terminal entry enforcement under Primary ownership

Make the common business-entry poison predicate explicit and preserve fixed diagnostics/first-failure semantics. Review all callers affected by the shared predicate, including no-allocation and exception paths, staging/private metadata resolution, ordinary/OFF controls, reflection, interpreter and generated delegate/interface entry. Do not enable PureInterpreter expansion or introduce unrelated milestone work.

Exit: focused source tests and static review demonstrate both valid entry before poison and refusal after poison, without a diagnostic recursion or ordinary-load regression.

### Step C — Proportionate Local Validation on the changed tuple

Because Step B changes runtime behavior, old S binaries cannot validate that fix. Primary should supply a new exact four-repository tuple and a bounded Local Validation request. Require the specific counterexamples and controls in IR-R03-02, plus regression of staging/publication/initializer failure, generic captured arguments, guarded allocation and retained-metadata recovery. Recheck affected resource and production integration cases according to the changed call graph. Any reused historical case must be labeled reused evidence with justification, not claimed as fresh execution.

A full rerun is not automatically required for a documentation-only correction. Conversely, a tiny code diff is not adequate justification for omitting regression of a widely shared guard. Select the batch by the actual behavioral blast radius.

### Step D — Independent re-review, then stop

The independent reviewer must inspect the corrected guard implementation and actual fresh failure-path receipts, authenticate the corrected S/new evidence joins, close the material-source omissions and remaining RC2/RC4/RC6 coverage gaps, and issue a new explicit verdict. Preserve this FAIL report as history. Do not overwrite it with a later PASS.

**Remaining owner decisions:** none are necessary for the two corrections; D1=A and D2=A remain the governing choices. Any later change to expansion scope or a production performance SLA is a separate owner/gate decision, outside this R03 review. No H2 approval is implied or requested by this report.

## 12. Final disposition

**FAIL.** RC3 terminal-failure enforcement has a source-derived counterexample, and RC6's evidence identity is internally inconsistent across the pinned Primary reconciliation and original S checkpoint. The declared incomplete authentication/coverage work independently precludes an unqualified PASS.

This review adds documentation only. It does not change product source, tests, source pins, project configuration, Local-owned handoffs, prior reports, historical results or acceptance flags. No fixes, new Local Validation, retained-R restoration, PureInterpreter expansion, H2 or M08A work was performed. Stop after remote publication verification and reporting this verdict.
