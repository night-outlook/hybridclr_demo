# D5-B AP1 — Primary publication proposal implementation and exact CI

**Date:** 2026-11-25 America/Los_Angeles. Execution timestamps in evidence remain UTC.
**Status:** `D5BActivationPublicationAP1Primary=SourceOnlyCIComplete_PendingIndependentProtocolReview`.
**Exact tested implementation:** `hybridclr_demo@25551bca385c5af20c417110ad1ee27593a3eefc`.

[Design and historical input inventory](D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md) · [Independent protocol/source review request](D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_REQUEST_2026-11-25.md) · [Machine evidence](D5B_ACTIVATION_PUBLICATION_AP1_EVIDENCE_2026-11-25.json) · [Raw CI job log](D5B_ACTIVATION_PUBLICATION_AP1_CI_JOB_139654943143_2026-11-25.log) · [Primary source-host log](D5B_ACTIVATION_PUBLICATION_AP1_SOURCE_HOST_2026-11-25.log).

## 1. Outcome and boundary

The user requested continued Primary implementation after the independent R5 review completed. R5 remains `PassDryAdmissionSourceOnly` for `eaca19c08f41245c46dfacbf605cd80480bc3a92`; its [independent report](D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md) at the bootstrap publication `e63732d755c0ed283138e72d3e612609ea73a565` closes the earlier R4 findings within the reviewed scope. AP1 addresses the next, separate activation-publication problem. It does not reopen those findings or turn R5's source-only result into execution approval.

The previous same-revision activation sequence is circular: envelope E contains source commit H, the writer contains the Git blob of E, and that writer contributes to H. Publishing the pin on the source branch changes H and makes the old envelope pin stale. AP1 selects the **H → E → A → Q** proposal: freeze the four-source tuple H, construct E(H), freeze a separate runner A, then publish review and the canonical handoff at Q on a separate approval/documentation ref. Neither A nor Q is embedded in E. Q names the exact source tuple and runner A without advancing their refs.

This cycle implemented the **closed proposal auditor and real Git model**, not the future runner or authority mechanism. No production runner, activation ref, approved execution envelope, new physical output parent, or Local permission was created. The design's §4 lists the remaining Primary implementation after protocol review.

## 2. Published implementation

All four repositories use branch `codex/assembly-shadow-r01b-h1`. The following is the **CI-tested source tuple**, not a later documentation-delivery HEAD and not an authorized Local tuple:

| Repository | Exact implementation source commit |
|---|---|
| night-outlook/hybridclr_demo | `25551bca385c5af20c417110ad1ee27593a3eefc` |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

The implementation commit contains exactly four changed paths:

| Path | Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `e4508a201081dfb87fc77a0b097fd92ce143beb6` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `0b8cc3ad6a3c31e949be4296f2314777a6454e86` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `426e80ceb3f157ddb9c909fbaa409cd8e1db7904` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md` | `c972b5f5894edc0d289ca88b326991cea640ec42` |

The auditor reads actual local commit/tree/blob bytes, verifies their object IDs, binds the canonical source branch and a distinct direct runner ref to exact commits, checks A's sole parent H, and permits exactly the proposal file addition plus one literal writer-pin substitution. It rejects extra tree changes, mode/type substitutions, wrong pins, ambiguous or malformed JSON, and any promotion of the closed authority fields. It rechecks the observed local refs before returning.

Its proposal kind is `R03D5BActivationPublicationProposalV1`; success is only `ProposalPublicationStructureVerified_NoExecutionAuthority`. It does not import the candidate writer, mutate the repository, fetch, push, inspect the Mac, or validate live remotes. The report explicitly leaves runtime runner custody, execution authority, live-ref verification and current physical inputs unverified. The existing R5 parser rejects this proposal kind even when an isolated test supplies its matching blob pin.

During Primary peer review, an alias-ref ambiguity was found and corrected before publication: a supplied source alias could have remained at H while the envelope-named branch moved. The auditor now requires `refs/heads/codex/assembly-shadow-r01b-h1`; test 03 rejects alias substitution and symbolic refs. Raw-JSON parser errors, including recursion and integer conversion limits observed on the tested Python versions, are reported as proposal rejection. Peer review is not independent project approval.

## 3. Preserved reviewed state

The following files retain their exact R5 bytes:

| Preserved R5 file | Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |

The complete retained suite remains 94 methods; no old test body was edited. Legacy B1 comparators, native sources, producer inventories, source-preflight pins, and the three sibling repositories were not changed. The GitHub comparison from bootstrap to implementation contains only the four paths above.

## 4. Validation and raw evidence

[GitHub Actions **45743817742**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45743817742), attempt **1**, push at exact source `25551bca385c5af20c417110ad1ee27593a3eefc`, completed **success**. Raw job **139654943143** has **1/1 focused job and 9/9 returned steps successful**. The raw log identifies Ubuntu **24.04.5**, Python **3.11.18**, and Git **2.56.1**.

| Validation | Primary Linux host, Python 3.12.14 | Exact-source GitHub CI, Python 3.11.18 |
|---|---|---|
| Retained R5 suite | 94/94; 0.155 seconds | 94/94; 0.189 seconds |
| New AP1 Git publication suite | 18/18; 7.826 seconds | 18/18; 2.899 seconds |
| Public execution without approval | Exit 2, NotAuthorized, outputCreated=false | Exit 2, NotAuthorized, outputCreated=false |

These are **112 unittest methods across two suites**, with mutation subtests excluded from the count. The AP1 suite creates temporary Git objects and commits; it demonstrates a constructible separate-runner chain and the stale source-pin result from ordinary same-ref publication. Its checks include canonical/direct refs, actual object kinds, parentage, exact tree changes, source/writer identity, JSON schema and types, closed authority, production rejection of the proposal, and a CLI with no execution override. These are source-host tests, not 18 real Player executions.

The workflow checks the actual 94- and 18-test footers and two OK results before emitting matching counts. The [decoded CI log](D5B_ACTIVATION_PUBLICATION_AP1_CI_JOB_139654943143_2026-11-25.log) retains its UTF-8 BOM: **38,408 bytes**, SHA-256 `86890d4b25c7f3825c0efc29ae6e456656239f2e05f18a65349d9f4f231fb6d2`. The [Primary host log](D5B_ACTIVATION_PUBLICATION_AP1_SOURCE_HOST_2026-11-25.log) is **18,037 bytes**, SHA-256 `e3ecbca7b4a39ea564c658023494ef07c9c4bf8d6cdc2d1e23fc53cdd3647797`. Source hashes were stable throughout the integrated host run and matched committed readback. Python AST parsing, workflow YAML parsing and changed-file whitespace checks passed.

Five other workflows automatically started at the source commit. Native B1 run **45743817704** reported success as metadata only; runs **45743817757**, **45743817718**, **45743817869** and **45743817759** reported cancelled. They are not AP1-reviewed evidence and are not counted as additional passing validation.

An early fixture setup attempt referenced an optional profile absent from the partial source snapshot. That unnecessary dependency was removed before the final tests; the fixture retains the actual writer, plan, preflight and wrapper. No failed exploratory/setup run is promoted to passing evidence.

## 5. Provenance and integration

Fresh Connector reads confirmed all four canonical repository identities, the working branch and read/write permissions. The prior same-session Git-data smoke writes were freshly read back on `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0`; their exact bases and commits are recorded in the machine evidence. The branches remain because no Connector deletion capability is available. They are operational transport evidence, not source or acceptance pins.

AP1 was committed using the same Connector tree/commit/ref path with an expected-head lease, then each changed file was read back byte-for-byte at `25551bca385c5af20c417110ad1ee27593a3eefc`. No local clone or unpushed artifact supplies handoff authority. The evidence publication changes documentation only. `README.md`, `Plan/CURRENT_STATUS.md` and Primary-owned `Handoff/WEB_TO_LOCAL.md` are updated; Local-owned `LOCAL_VALIDATION.md` and `RETURN_TO_WEB.md` remain untouched.

The historical Mac workspace is `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r`, with each repository as its named child. These are published historical candidates, **not currently verified checkouts**. Original S, six historical roles, and the historical Unity path/hash are itemized with immutable provenance in the design. No historical observation proves today's filesystem or toolchain. No new runner path, evidence parent or one-use name is approved.

## 6. Next review and remaining work

Next is a separate independent review of AP1's proposal design, exact source, tests and raw CI. The requested bounded verdict is `PassActivationPublicationProposalOnly` or `ReturnRequired`; current independent status is **Pending**. Primary does not assign that verdict.

After protocol review, Primary still owns the fifth runner identity and executable/import closure, explicit plan-version/adapter authorization semantics, Q authority/custody and drift handling, and exact-source qualification of that implementation. The retained R5 namespace limitation requires controlled evidence-parent custody before future Local authorization. The final source tuple and concrete physical inputs must be frozen and explicitly approved before a new executable handoff can open. No missing architecture is delegated to Local.

`APPROVED_EXECUTION_ENVELOPE_BLOB=None`; `APPROVED_LOCAL_HANDOFF_BLOB=None`; **`WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`**; `D5BLocalExecution=NotAuthorized`; `D5LocalValidation=NotAuthorized`; `R03Accepted=false`; `H2Passed=false`; `ReadyForHumanReviewGate=false`. All **18 real D5 Player cases remain NoCoverage**. Candidate macOS admission, Unity/IL2CPP/Bee/full VM/Mach-O/GC/PID/Player validation remain **NotRun**. This is ready for source/protocol review and is **not Local-handoff-ready**.
