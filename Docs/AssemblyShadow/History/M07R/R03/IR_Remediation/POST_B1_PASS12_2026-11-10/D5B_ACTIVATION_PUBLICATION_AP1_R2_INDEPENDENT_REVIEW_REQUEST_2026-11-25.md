# R03 D5-B AP1 R2 — independent source-only rereview request

**Client date:** 2026-11-25 America/Los_Angeles. Preserve historical UTC labels and actual execution timestamps.

## 1. Requested independent decision

Independently rereview the focused correction for **D5B-AP1-IR-01**, the AP1 commit parser's false sole-parent assertion. The [prior independent report][prior-review], blob `9065580fc26868b1c76b773348657564150c6741` at publication `6d0a5d1613c483119b41d774765ef9752adb7732`, assigned `D5BActivationPublicationAP1IndependentReview=ReturnRequired` against source `25551bca385c5af20c417110ad1ee27593a3eefc`.

That verdict remains applicable until this separate review adjudicates the successor. Primary requests a proposal/source-only decision; it does not assign `PassActivationPublicationProposalOnly`, approve activation, or reopen R5's retained `PassDryAdmissionSourceOnly` verdict. The previously accepted H/E/A/Q constructibility remains outside the focused return except where a new concrete interaction warrants attention.

## 2. Exact review target and evidence

| Repository | Exact R2 source tuple |
|---|---|
| `night-outlook/hybridclr_demo` | `2a0053bbe350bc52b189ca4201542b2c93b5eca7` |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

All source refs remain `codex/assembly-shadow-r01b-h1`. Later publication HEADs must be distinguished from the tested source. The Actions identifiers to verify are run **`45751527263`**, job **`139680200608`**. Read the [R2 design][design], [Primary report][primary], exact [auditor][auditor], [tests][tests] and [workflow][workflow], then the retained R5 files and actual raw evidence. Verify provenance rather than relying on Primary summaries.

The source inventory is **94 R5 methods plus 22 AP1 methods**, including four new AP1 methods 19–22. Primary records preservation of all prior **18 AP1 method bodies, 13 helpers and five exact R5 file blobs**. Confirm that preservation independently.

## 3. Focused review questions

1. **Does the shared parser agree with the supported Git topology?** Require the initial tree header and immediately contiguous parent prefix. Check rejection of late/resumed parent and duplicate/misordered tree headers for both source H and runner A. Preserve parent order/cardinality; A must have exactly `(H,)`.
2. **Does non-topological text remain non-topological?** Check supported metadata, leading-space continuations after metadata, opaque values and message contents. No tree/parent-looking continuation or message may manufacture an edge. The correction should not imply signature authentication or new author semantics.
3. **Does the bounded native check enforce actual local agreement?** The sanitized `rev-list --no-walk --parents <oid> --` result must contain exactly one row equal to the immutable-byte parser's result. Inspect the real shallow-view mismatch control. This check is not a live remote check, history walk, custody proof or namespace lock.
4. **Do the new regressions reach the finding?** Inspect ordinarily stored late-parent objects and their native parent observations, including the strict-check-positive case. Distinguish literal-only rejection fixtures from ordinary storage, and direct-parser checks from full-audit checks where Git permits refs. Confirm both source and runner roles are exercised using actual stored objects, with candidate code inert.
5. **Are existing boundaries preserved?** Recheck canonical/direct local refs, the exact closed proposal schema, reviewed writer/envelope substitution and two-path delta. The proposal kind must remain rejected by R5's executable parser, and the production plan and both approval gates must remain closed.

The old-auditor negative control is **transcript-only**: 17 failed subcase assertions across methods 19/21/22, 0 errors, and no retained raw log. It is not 17 tests, archived execution evidence or a new R2 failure/pass count. The reviewer should not treat it as a substitute for exact-source inspection and retained evidence.

## 4. Raw evidence and version separation

Verify the run attempt, exact run/job/checkout SHA, individual 94/22 method rosters, both unittest footers and `OK` results, job/step outcomes, and retained log bytes. Verify the separate production null-approval refusal, including exit-code evidence and absence of its unapproved-envelope path.

The decoded CI log identity to reconcile is **`40426` bytes / `689a9416b5e9839973b400c86aa5e3a77e9146a164654dc1b481f6b053c9ce9d`**. The Primary host log identity is **`19186` bytes / `27544339c8929e3b460538eaa398c0ca2d35cf396b06e02f6a1e96b5a2b04eb1`**. The CI archive preserves the UTF-8 encoding of the Connector-returned decoded log, including its BOM. Both archive links and the corresponding machine record are supplied below.

Record **fixture Git** (`git version 2.56.1`) and the **sanitized auditor Git** (`git version 2.56.1`) separately, with their executable paths and CI Python (`3.11.18`). Check host selections separately. The two Git selectors can resolve to different versions; no result should silently inherit an earlier run's interpreter or Git version.

Retained evidence: [machine record](D5B_ACTIVATION_PUBLICATION_AP1_R2_EVIDENCE_2026-11-25.json), [host raw log](D5B_ACTIVATION_PUBLICATION_AP1_R2_SOURCE_HOST_2026-11-25.log), [decoded CI job log](D5B_ACTIVATION_PUBLICATION_AP1_R2_CI_JOB_139680200608_2026-11-25.log), [Actions run](https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263) and [job](https://github.com/night-outlook/hybridclr_demo/actions/runs/45751527263/job/139680200608). Attempt **1**, event **push**, exact source **`2a0053bbe350bc52b189ca4201542b2c93b5eca7`**, **1/1 job and 9/9 returned steps successful**. Host Python **3.12.14**, fixture Git **git version 2.56.1** at **`/usr/local/bin/git`**, auditor Git **git version 2.47.3** at **`/bin/git`**. CI fixture path **`/usr/bin/git`**, auditor path **`/bin/git`**. These are distinct observed environment selections.

Independent publication is limited to a new R2 report and companion evidence in this same directory and current verdict links in README/CURRENT_STATUS. Preserve implementation, tests, workflow, approval constants, WEB_TO_LOCAL, Local-owned validation/return records and sibling repositories; return non-trivial findings to Primary. Record the independent decision and exact reviewed source without promoting it to Local authority.

## 5. Authority and stopping point

This review concerns the AP1 R2 source-only return. It neither requests nor permits implementation/execution of the future runner, Q authority, plan adapter, physical admission or Local validation. Those disclosed future Primary requirements remain deferred, including the R5 namespace/custody limitation.

```text
D5BActivationPublicationAP1IndependentReview=ReturnRequired
D5BActivationPublicationAP1R2IndependentReview=Pending
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

All 18 real D5 Player cases remain `NoCoverage`; candidate Local/macOS, Unity, IL2CPP, Bee, native VM, Mach-O, GC, PID and Player work remain `NotRun`. Any independent result must state its proposal-only scope. No Local command, activation, approved envelope, Human Review Gate or later milestone follows from this request. Stop after the separately authorized independent report and its permitted publication/readback.

[prior-review]: https://github.com/night-outlook/hybridclr_demo/blob/6d0a5d1613c483119b41d774765ef9752adb7732/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_INDEPENDENT_REVIEW_2026-11-25.md
[design]: D5B_ACTIVATION_PUBLICATION_AP1_R2_DESIGN_2026-11-25.md
[primary]: D5B_ACTIVATION_PUBLICATION_AP1_R2_PRIMARY_2026-11-25.md
[auditor]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py
[tests]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py
[workflow]: https://github.com/night-outlook/hybridclr_demo/blob/2a0053bbe350bc52b189ca4201542b2c93b5eca7/.github/workflows/r03-b2-d5b-local-admission-source-host.yml
