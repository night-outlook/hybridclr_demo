# R03 D5-B AP1 — independent proposal, exact-source, real-Git and raw-CI review

**Review date:** 2026-11-25 America/Los_Angeles. UTC execution timestamps are retained as recorded.  
**Role:** Independent source reviewer, separate from Primary Implementation and Local Validation.  
**Verdict:** **`D5BActivationPublicationAP1IndependentReview=ReturnRequired`**.  
**Exact reviewed and CI-tested source:** `night-outlook/hybridclr_demo@25551bca385c5af20c417110ad1ee27593a3eefc`.  
**Branch:** `codex/assembly-shadow-r01b-h1`.  
**Documentation HEAD examined before this publication:** `aa34e30eeec99579ad0eca38afb410ac3a57fdf9`.

[Companion independent machine evidence][Evidence] records the full test-name rosters, source identities, CI observations, and the additional reviewer fixture results.

## 1. Decision

**ReturnRequired** is assigned because the AP1 auditor can assert a sole-parent relationship that ordinary Git does not recognize. Its commit-header parser scans the whole header block for parent-named lines. A real stored commit with such a line after the committer header is accepted by the auditor as a child of H, while Git treats it as a root commit. AP1 nevertheless emits `ProposalPublicationStructureVerified_NoExecutionAuthority` and `runnerSoleParentIsSource=true`. This contradicts an express guarantee of the proposal auditor itself.

| Review area | Independent disposition |
|---|---|
| H/E/A/Q publication design | The proposed separation removes the stated ordinary publication dependency, with Q externally pinned and no new self-reference identified. |
| Actual local Git topology | **Blocked by D5B-AP1-IR-01.** The sole-parent assertion can be false. |
| Closed schema, exact writer/envelope binding, canonical refs and two-path delta | Substantive controls are present; existing tests meaningfully exercise the covered cases. The parent finding remains independently blocking. |
| Retained R5 source and tests | Five files are byte-identical to the reviewed R5 versions. **PassDryAdmissionSourceOnly is preserved.** |
| Focused CI provenance | Verified: exact tested SHA, **94 + 18 methods**, two OK footers, **1/1 job**, **9/9 returned steps** successful. |
| Local or activation authority | None. The proposal verdict does not open any execution gate. |

The passing CI remains a valid observation about the tests that ran. The additional parent-header case is outside those tests, so their success cannot settle that case. This report returns AP1's bounded proposal implementation for correction; it does not reopen R5's R4-IR-01/R4-IR-02 adjudications, retract the historical CI result, or require the explicitly deferred activation architecture to be implemented during this review.

The requested `PassActivationPublicationProposalOnly` is therefore **not granted**. Further work must begin with a focused Primary correction and a separately reviewed successor source revision. No implementation change is made by this publication.

## 2. Scope, method and evidence separation

The review started with [README][Readme], then the [closed WEB_TO_LOCAL handoff][Handoff], then the [AP1 independent review request][Request]. It examined the exact-source [design][Design], [auditor][Auditor], [18-method test suite][Tests], [workflow][Workflow], preserved R5 writer/plan/test/preflight/wrapper, [Primary report][Primary], Primary machine evidence, [retained R5 independent report][R5Review], remote run and attempt-specific job metadata, and the actual decoded raw job log.

GitHub content was retrieved through the **GitHub Connector**. Separate bounded reviewers examined protocol/source semantics, test coverage and CI/preservation evidence. Their conclusions were reconciled against the coordinating reviewer's own source reads and GitHub evidence.

This AP1 review **did not rerun the 94-method or 18-method project suites**. Their recorded execution was audited from the actual GitHub job and compared with source method inventories. The additional reviewer execution was one isolated Linux source-host Git fixture with two observations: an ordinary positive control and the parent-header counterexample. Only the exact AP1 auditor was imported. The candidate admission writer and synthetic runner remained inert Git bytes.

That fixture used a temporary repository, with no remote operation and no production ref. It did not inspect or run commands on the user's Mac or historical Local paths. The temporary repository was removed on exit. Its deliberately minimal source tree contained the reviewed writer; it was not a production source checkout or executable-closure attestation.

The fixture's recorded Git version is **2.47.3** on **Linux 6.18.57 x86_64 with glibc 2.41**. Its Python interpreter version was **not recorded**. The historical CI log reports Git **2.56.1** and Python **3.11.18**; this review does not represent the new counterexample as having run inside that historical CI job. Official Git source at `v2.51.0` provides separate static corroboration of the parent parsing rule.

## 3. Immutable source and publication provenance

### 3.1 Four-repository identities

Fresh Connector reads resolved the canonical feature refs to the supplied heads.

| Repository | Exact AP1 source tuple | Observed feature HEAD before publication |
|---|---|---|
| `night-outlook/hybridclr_demo` | **`25551bca385c5af20c417110ad1ee27593a3eefc`** | **`aa34e30eeec99579ad0eca38afb410ac3a57fdf9`** |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | Same |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | Same |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | Same |

All four use `codex/assembly-shadow-r01b-h1`. Sibling ref verification establishes the unchanged source tuple; it is not a new full native-source audit.

The implementation commit's tree is `6ddaee379193bf586f19c2f6231134f205984945`, with sole parent `e63732d755c0ed283138e72d3e612609ea73a565`, the prior independent R5 publication. The [implementation comparison][ImplementationCompare] contains exactly four changed paths: AP1 auditor, AP1 tests, focused workflow, and AP1 design.

The [tested-source-to-documentation comparison][DocsCompare] contains one later commit and eight paths, all under `Docs/AssemblyShadow`: Primary report, review request, machine evidence, archived CI log, Primary host log, README, current status and closed handoff. The documentation commit has the tested source as its sole parent. No implementation, tests or workflow changed in that delivery.

**The CI-tested source is `25551bca…`; neither `aa34e30…` nor the commit publishing this independent review is the tested source.**

### 3.2 Source and evidence blobs

| Item | Verified Git blob |
|---|---|
| AP1 auditor | `e4508a201081dfb87fc77a0b097fd92ce143beb6` |
| AP1 test suite | `0b8cc3ad6a3c31e949be4296f2314777a6454e86` |
| Focused workflow | `426e80ceb3f157ddb9c909fbaa409cd8e1db7904` |
| AP1 design | `c972b5f5894edc0d289ca88b326991cea640ec42` |
| R5 writer | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| R5 94-method test file | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| R5 versioned plan | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| R5 public wrapper | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| R5 imported preflight | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| Existing custody-authority module | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| Archived decoded AP1 CI log | `8c14eb672e2576aee49eff37ebe3bfb8f91d770e` |
| WEB_TO_LOCAL at documentation HEAD | `69f38d094a50a245158e9a0bd300f9780551950b` |

The five preserved R5 files were independently fetched at both `eaca19c08f41245c46dfacbf605cd80480bc3a92` and the AP1 tested source. Contents and computed Git blobs match exactly. Equality of the complete test file establishes preservation of all **94 methods and their helpers**, beyond matching method names alone.

## 4. Design adjudication: H, E, A and Q

### 4.1 The original dependency follows from actual source checks

The retained writer requires a literal immutable envelope blob: `APPROVED_EXECUTION_ENVELOPE_BLOB` at [writer line 47][Writer], and the exact-byte check at [lines 454–482][EnvelopeParser]. The envelope names the four source commits. The imported preflight checks the clean checkout's exact HEAD at [preflight lines 245–258][Preflight]. The writer then checks each live feature ref against the same frozen tuple at [lines 363–388][SourceChecks]; `exact_remote_head` requires one exact canonical branch observation.

Under ordinary same-source-ref publication, inserting E's blob into the writer creates a new demo commit. If E still names the previous source commit, the exact source-ref check becomes stale. Regenerating E to name the new commit changes E's blob again. This is a publication dependency created by the existing identities; the review does not claim to prove a general mathematical impossibility of hash fixed points.

Test 02 supplies a meaningful ordinary control: it moves the synthetic source ref to A, observes that ref through a local-path Git remote query, and confirms that the retained exact-head helper rejects E's old H pin. That local-path query demonstrates the comparison logic; it is not evidence about a live GitHub remote.

### 4.2 The proposed separation is constructible

The design freezes the four-source tuple H first, then creates E(H), then a separate runner revision A containing the literal E blob, then publishes the independent review, user decision and handoff at Q on a separate approval/documentation ref. E excludes both A and Q. Q's own commit identity is resolved and communicated externally after publication.

Those relationships remove the stated same-revision dependency without requiring source H or runner A to advance for approval-document publication. The ordinary positive Git fixture demonstrates H and A on distinct refs, an exact E blob, and one literal writer substitution. There is no identified Q self-reference in the documented proposal.

This assessment is limited to constructibility. AP1 creates **closed proposal bytes**, not a production executable envelope, activation branch, approved runner or approved physical output location. A future authorization mechanism still needs to prove who approved which exact identities and how current custody is enforced.

### 4.3 Explicitly deferred requirements remain deferred

Design §4 correctly reserves the fifth runner identity, clean canonical disjoint runner checkout, runner live-ref validation, complete executable/import/configuration closure, plan-version or adapter authority semantics, Q review/user-decision validation, external Q pin, drift/revocation handling, and fresh physical qualification for further Primary work.

The current R5 plan still declares closed, source-only authority. Replacing a writer literal cannot by itself change that plan's meaning. Similarly, a source H containing unchanged helper bytes is not proof that those helpers were independently authenticated. The AP1 delta check constrains H-to-A changes; it does not qualify every preexisting H dependency.

These disclosures are appropriate to the requested proposal-only phase. They do not excuse the parenthood defect, because actual local Git parentage is already an explicit AP1 guarantee.

## 5. Actual auditor review

The source implements a bounded object auditor, with no candidate-code import. Its fixed Git calls read configuration, repository metadata, refs and objects; the auditor does not issue checkout, fetch, push or update-ref commands.

| Contract | Source behavior and review |
|---|---|
| Exact proposal schema | `strict_json_object` rejects duplicate keys at every object depth, invalid UTF-8 and parser errors. `_exact_value` enforces exact keys, values and Python types, preventing bool/int equality from relaxing the schema. The full accepted schema contains no floating-point field. |
| Closed authority | The expected proposal and both report forms retain all eleven closed authority fields. Success explicitly leaves execution, live remotes, physical inputs and runner custody unverified. |
| Distinct kind | AP1 uses `R03D5BActivationPublicationProposalV1`. R5's executable-envelope parser requires a different kind and separate review/user-approval fields. Test 16 checks rejection even with an in-memory matching blob pin. |
| Writer binding | H's writer must be the exact R5 blob. A's writer must equal the exact bytes produced by replacing the single closed literal with the exact proposal blob. Additional writer edits reject. |
| Ref binding | The source ref must be the canonical feature ref, and the runner ref must be distinct. Both must be full direct local branch refs naming the supplied exact commits. Both are observed again before success. |
| Object integrity | The object reader checks actual type, batch length, raw-byte hash and requested identity. A blob/tree/tag does not become a commit by peeling or by accepting a revision expression. |
| Tree delta | The recursive comparison permits only the writer change and new proposal file, with touched directory ancestors preserved. Writer mode is preserved; the proposal is a new non-executable regular file. Other changes reject. |
| Parentage | **Incorrect for the demonstrated header placement.** The custom commit parser's extracted tuple is not always Git's parent tuple. |

The Git environment is narrowed, replacements are disabled, optional locks and lazy fetch are disabled, remote protocols are disallowed, and local include/extension/partial-clone settings are rejected. The 18 tests do not independently exercise every such defensive branch. Source presence is not reported here as exhaustive runtime qualification.

Ref checks are explicitly point-in-time local observations, not a lock or remote-state proof. The source says so at lines 367–369. That caveat remains material even after a future parser correction.

## 6. Blocking finding D5B-AP1-IR-01

**Priority:** P1, blocking within the AP1 local-Git proposal contract.  
**Status:** Open.  
**Title:** Commit-header parsing invents a sole-parent relationship that Git does not recognize.

### 6.1 Cause and effect

[`_Git.commit`, lines 261–276][CommitParser], reads the raw commit and scans every header line. Every line beginning with `parent ` contributes to its returned parent tuple, regardless of its position. The code then requires that tuple to equal `(source_commit,)` at [lines 383–386][ParentCheck], and emits `runnerSoleParentIsSource=true` at line 422.

Git's own parser treats the initial tree header and the immediately following contiguous parent-header sequence as the topology-bearing prefix. A later parent-named header is not added to the parent list. This rule is visible in [official Git `commit.c`][GitCommitSource], independently fetched at `v2.51.0`, blob `d1e1061214b9ab410f0619d3d4f92ccc6cb98b58`.

Consequently, checking that bytes hash to an object whose stored type is commit does not make AP1's interpretation of those bytes correct.

### 6.2 Additional reviewer observations

The reviewer fixture used the exact audited AP1 module and verified its blob before importing it. The R5 writer blob was likewise recomputed before being used as inert bytes. Both cases used the same runner tree, proposal-envelope bytes and exact writer substitution; only the placement of the parent-named header differed. The proposal remained closed.

| Observation | Ordinary positive control | Additional parent-header case |
|---|---|---|
| Header sequence | Tree, parent, author, committer | Tree, author, committer, parent-named header |
| Synthetic H | `b013c319e5cdd4603e1e9cfb591cb5daa66d01ca` | Same |
| Synthetic A | `f4d3bdf4d4d30fca9ba36b12208234f7fb6d373d` | `115d5825b5bd79fab6ccce9afbcc13e055bed1c9` |
| Runner tree | `fd2cac0da8100c14bc664521c423c0912da38d95` | Same |
| Git-recognized parents | H | **None** |
| AP1 result | ProposalPublicationStructureVerified_NoExecutionAuthority | **Same success result** |
| AP1 sole-parent field | true | **true, incorrectly** |
| Ordinary object storage | Accepted | Accepted |
| Git strict object check | Exit 0 | Exit 0 |

The envelope blob is `178233b2dd7ac9780cf1d8becda1ee56cde8b7bd`; the synthetic pinned-writer blob is `8fab86c5876b845bde1eef0d3ab062f2de2b4db1`. These are **private synthetic fixture identities**, not production source or authorization pins.

Git's parent listing returned only the additional case's own object ID, with no parent. The independent evidence records that output and both complete auditor reports. The strict Git check reported only an unrelated dangling-control commit and exited successfully. Thus adding a generic object-integrity check alone would not establish the promised relationship. A separate ancestor command was not run; absence of H ancestry follows from the observed zero-parent commit.

### 6.3 Why this blocks the requested pass

The design explicitly promises that A has H as its sole parent. The auditor successfully verifies exact refs and the tree/envelope/writer details, but then makes a false topology assertion. This is a demonstrated result within today's implemented scope, independent of any future Local runner, Q validation or physical custody requirement.

The existing test fixture builds every commit through ordinary `commit-tree` at [test lines 106–112][FixtureCommit]. Test 15 varies valid parent lists—none, wrong, two and indirect—but does not vary raw header placement. Test 04 covers object kinds, and tests 07/08 cover writer/tree bytes; none reaches this distinction. The historical 18/18 result is therefore compatible with the defect.

## 7. Retained tests and all 18 new methods

The five exact R5 file identities preserve the prior independent source verdict and all 94 existing test bodies. The raw AP1 CI roster contains those same 94 source method names, all successful. Earlier R4-IR-01 and R4-IR-02 remain closed within R5's previously published scope. This review does not claim new Mac, APFS, hard-termination or namespace guarantees from rerunning them in CI.

The AP1 fixtures use actual Git objects, trees, commits and refs. They use the real writer/plan/wrapper/preflight bytes plus a synthetic source sentinel. Git is not mocked. The single approval mock in test 16 is confined to the pure envelope parser and restored afterwards.

| AP1 method | Test lines | Independently reviewed purpose |
|---|---:|---|
| 01 | 194–220 | Constructs separate refs; checks actual Git parenthood, exact E/writer bytes, closed result and unchanged refs. |
| 02 | 222–233 | Ordinary same-source-ref publication makes the old E source pin stale and is rejected. |
| 03 | 235–272 | Moved/missing refs, a noncanonical source alias and a symbolic canonical source ref reject. |
| 04 | 274–294 | Missing/blob/tree/tag objects reject, including direct commit-reader checks that reach the object-type guard. |
| 05 | 297–303 | A writer pin for different proposal bytes, even a newline difference, rejects. |
| 06 | 305–319 | Extra sentinel/helper/wrapper/plan changes, unrelated addition and deletion reject. |
| 07 | 321–331 | An altered source writer rejects even when the runner is consistently constructed from it. |
| 08 | 333–343 | Unchanged writer, extra comment and second approval assignment reject. |
| 09 | 345–371 | Relevant mode changes and symlink/tree/gitlink substitutions reject. |
| 10 | 373–383 | Proposal missing from A or already present in H rejects. |
| 11 | 386–400 | Equal-value duplicate keys reject at top level and both nested objects. |
| 12 | 402–448 | Malformed/invalid-UTF8/deep/oversized JSON and schema/type/root/key mutations reject. |
| 13 | 451–468 | Exact four source pins and exact repository-role set are required. |
| 14 | 470–491 | All eleven closed authority fields reject promotion. |
| 15 | 493–504 | Conventional root, wrong-parent, multiple-parent and indirect-parent commits reject; **raw header placement is uncovered**. |
| 16 | 506–517 | AP1 proposal rejects as a production execution envelope with both the real null pin and a temporarily matching test pin. |
| 17 | 531–537 | CLI positive result remains closed and preserves refs and the imported gate's approval constant. |
| 18 | 539–553 | Four execution/approval override argument forms reject with exit 2 and no stdout/ref/approval change. |

These are **18 methods**, not one test per mutation subcase. Together with R5 they are **112 methods across two suites**.

Additional static coverage observations are retained without inflating the blocking finding:

- Normal Git object constructors do not exercise malformed raw tree encodings, duplicate raw names, hash/length mismatches or all raw commit-header layouts.
- The suite does not directly cover symbolic runner refs, mid-audit ref movement, all sanitized-environment/configuration branches, alternate proposal paths, or invalid-topology CLI JSON rejection. Test 18 exercises argument parsing.
- The shared success assertion checks the main closed fields but not every report field. Ref snapshots alone are narrower than proof that no other repository bytes changed; fixed read-only command sites provide the complementary source evidence.
- The JSON helper's broad nonfinite-number docstring is stronger than its helper-level parsing: exponent overflow may produce a float without invoking the named-constant rejection hook. The complete exact schema accepts no float-valued leaf, so this does **not** establish an accepted AP1 proposal or a second blocking finding.

## 8. Raw GitHub Actions adjudication

The reviewer independently retrieved [run metadata][RunAPI], [attempt-1 job metadata][JobsAPI], the decoded job log and artifact listing. The actual log was compared with the [committed archive][RawLog].

| Observation | Verified value |
|---|---|
| Run / attempt / job | **45743817742 / 1 / 139654943143** |
| Event / branch | push / codex/assembly-shadow-r01b-h1 |
| Source in run, job and raw checkout | **25551bca385c5af20c417110ad1ee27593a3eefc** |
| Run / job conclusion | completed, success |
| Focused jobs / returned successful steps | **1/1 / 9/9** |
| Run created / updated | 2026-11-26T02:38:58Z / 2026-11-26T02:39:16Z |
| Raw platform/interpreter/Git | Ubuntu **24.04.5**, CPython **3.11.18**, Git **2.56.1** |
| Retained suite footer | **Ran 94 tests in 0.189s**, followed by **OK** |
| AP1 suite footer | **Ran 18 tests in 2.899s**, followed by **OK** |
| Method rosters | 94 and 18 unique names; exact source-name match; all terminal statuses ok |
| Artifacts | **0**; evidence is actual decoded log and metadata |

Retained tests 36/37 emit expected CLI JSON before a following standalone `ok`; the roster audit accounts for that interleaving. Summary echo fields are corroborated by actual test output.

The workflow uses `set -euo pipefail`, checks the actual 94/18 footers and both OK results, and separately requires the public null-approval command to exit 2. Its observed response is `NotAuthorized`, `outputCreated=false`, `retryAllowed=false`, and `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`. The workflow also asserts that the supplied unapproved-envelope path does not exist. The exit code is supported by the successful shell assertion; a separate numeric exit value is not printed in the raw response.

Fresh decoded log and committed archive are byte-identical:

| Identity | Value |
|---|---|
| UTF-8 bytes, BOM retained | **38,408** |
| Characters | **38,406** |
| SHA-256 | `86890d4b25c7f3825c0efc29ae6e456656239f2e05f18a65349d9f4f231fb6d2` |
| Git blob | `8c14eb672e2576aee49eff37ebe3bfb8f91d770e` |

No provenance mismatch was found in the audited CI claims. The Primary host execution was not independently rerun, and other automatically triggered workflows are excluded from this AP1 validation count. The new reviewer counterexample is recorded separately from the historical CI.

## 9. Retained limits and authority

The disclosed limitations remain material:

- **Only the R5 writer is independently hard-pinned inside the AP1 model.** Unchanged H helpers/imports are not authenticated executable closure. Future runner A still needs its own complete identity and custody contract.
- **Local ref rechecks are observations.** They do not establish live remote state, a cross-process lock, or absence of a transient away-and-back change.
- **Q remains unimplemented authority work.** No committed review or claimed user-approval string is authenticated by this auditor.
- **R5's namespace limit is unchanged.** Its no-adoption guarantee concerns unresolved creation. Recorded mkdir followed by initial pathname-based open retains the previously disclosed replacement gap, and moves after the last observation remain possible. Controlled evidence-parent custody is still required.
- **Historical physical inputs remain Unverified.** The Mac workspace and repositories under `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, historical roots, Unity path/hash, runner location and prospective output custody received no fresh physical qualification in this review.

The current constants were checked directly: `APPROVED_EXECUTION_ENVELOPE_BLOB=None` at writer line 47; `APPROVED_LOCAL_HANDOFF_BLOB=None` at [custody-authority line 25][Custody]. The AP1 auditor's synthetic substitution does not modify either production constant.

```text
D5BActivationPublicationAP1IndependentReview=ReturnRequired
D5BDryAdmissionR5IndependentReview=PassDryAdmissionSourceOnly
APPROVED_EXECUTION_ENVELOPE_BLOB=None
APPROVED_LOCAL_HANDOFF_BLOB=None
WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION
D5BLocalExecution=NotAuthorized
D5LocalValidation=NotAuthorized
R03Accepted=false
H2Passed=false
ReadyForHumanReviewGate=false
```

All **18 real D5 Player cases remain NoCoverage**, with zero passed. Candidate macOS admission, Unity, IL2CPP, Bee, full native VM, Mach-O, GC, PID and Player validation remain **NotRun**.

## 10. Required return and publication boundary

The focused return is to make commit-header interpretation agree with Git's actual topology, or reject a stricter unambiguous subset. It must not derive a parent edge from a late header that Git treats as non-topological data. The same shared parser serves source and runner commits, so correction and regressions should address both.

A successor should retain the existing 94 and 18 methods, add real stored-object coverage for relevant header-order cases, and compare the accepted parent relationship against Git's own parent view. General object-integrity success alone is insufficient, as demonstrated by the strict-check result. Fresh exact-source CI and a separate independent rereview must qualify the correction before a proposal-only pass can be assigned. This report does not implement that correction or begin the later activation work.

Publication is limited to this independent report, its companion machine evidence, and links/current verdict in README and CURRENT_STATUS. Existing implementation, tests, workflow, approval constants, WEB_TO_LOCAL, Local-owned validation/return records, and sibling repositories are outside the publication delta. The handoff remains closed; its earlier pending-review text is a historical Primary checkpoint superseded for review status by this report.

**Stop after independent review publication and readback. No Local handoff, Human Review Gate or later milestone is authorized.**

[Evidence]: D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_EVIDENCE_2026-11-25.json
[Readme]: https://github.com/night-outlook/hybridclr_demo/blob/aa34e30eeec99579ad0eca38afb410ac3a57fdf9/Docs/AssemblyShadow/README.md
[Handoff]: https://github.com/night-outlook/hybridclr_demo/blob/aa34e30eeec99579ad0eca38afb410ac3a57fdf9/Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md
[Request]: https://github.com/night-outlook/hybridclr_demo/blob/aa34e30eeec99579ad0eca38afb410ac3a57fdf9/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md
[Design]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md
[Auditor]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[Tests]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py
[Workflow]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
[Primary]: https://github.com/night-outlook/hybridclr_demo/blob/aa34e30eeec99579ad0eca38afb410ac3a57fdf9/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_PRIMARY_2026-11-25.md
[R5Review]: https://github.com/night-outlook/hybridclr_demo/blob/e63732d755c0ed283138e72d3e612609ea73a565/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md
[ImplementationCompare]: https://github.com/night-outlook/hybridclr_demo/compare/e63732d755c0ed283138e72d3e612609ea73a565...25551bca385c5af20c417110ad1ee27593a3eefc
[DocsCompare]: https://github.com/night-outlook/hybridclr_demo/compare/25551bca385c5af20c417110ad1ee27593a3eefc...aa34e30eeec99579ad0eca38afb410ac3a57fdf9
[Writer]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L47
[EnvelopeParser]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L454-L482
[Preflight]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py#L245-L258
[SourceChecks]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L363-L388
[CommitParser]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L261-L276
[ParentCheck]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py#L383-L386
[GitCommitSource]: https://github.com/git/git/blob/v2.51.0/commit.c#L464-L527
[FixtureCommit]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py#L106-L112
[Run]: https://github.com/night-outlook/hybridclr_demo/actions/runs/45743817742
[RunAPI]: https://api.github.com/repos/night-outlook/hybridclr_demo/actions/runs/45743817742
[JobsAPI]: https://api.github.com/repos/night-outlook/hybridclr_demo/actions/runs/45743817742/attempts/1/jobs?per_page=100
[RawLog]: https://github.com/night-outlook/hybridclr_demo/blob/aa34e30eeec99579ad0eca38afb410ac3a57fdf9/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_CI_JOB_139654943143_2026-11-25.log
[Custody]: https://github.com/night-outlook/hybridclr_demo/blob/25551bca385c5af20c417110ad1ee27593a3eefc/Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py#L19-L25
