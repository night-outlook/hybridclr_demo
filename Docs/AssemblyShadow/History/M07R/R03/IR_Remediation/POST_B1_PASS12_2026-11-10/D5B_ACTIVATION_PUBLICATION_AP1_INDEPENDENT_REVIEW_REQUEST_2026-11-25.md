# D5-B AP1 — independent publication protocol/source review request

**Requested on:** 2026-11-25 America/Los_Angeles. **Independent status: Pending.**
**Scope:** source-only activation-publication proposal and closed local Git auditor.
**No Local execution or activation permission is requested or granted by this document.**

## Read order and exact source

Read `Docs/AssemblyShadow/README.md`, the current CLOSED `Handoff/WEB_TO_LOCAL.md`, [AP1 design](D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md), [Primary implementation/evidence](D5B_ACTIVATION_PUBLICATION_AP1_PRIMARY_2026-11-25.md), [machine evidence](D5B_ACTIVATION_PUBLICATION_AP1_EVIDENCE_2026-11-25.json), and the retained [R5 independent report](D5B_LOCAL_DRY_ADMISSION_R5_INDEPENDENT_REREVIEW_2026-11-25.md).

Review implementation **`hybridclr_demo@25551bca385c5af20c417110ad1ee27593a3eefc`**, whose parent is `e63732d755c0ed283138e72d3e612609ea73a565`. A later metadata-only delivery commit is not the CI-tested source. All repositories remain on `codex/assembly-shadow-r01b-h1`:

| Repository | Exact implementation source commit |
|---|---|
| night-outlook/hybridclr_demo | `25551bca385c5af20c417110ad1ee27593a3eefc` |
| night-outlook/hybridclr | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| night-outlook/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

| Path | Git blob |
|---|---|
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `e4508a201081dfb87fc77a0b097fd92ce143beb6` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `0b8cc3ad6a3c31e949be4296f2314777a6454e86` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `426e80ceb3f157ddb9c909fbaa409cd8e1db7904` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_ACTIVATION_PUBLICATION_AP1_DESIGN_2026-11-25.md` | `c972b5f5894edc0d289ca88b326991cea640ec42` |

## Independent questions

1. Does the documented same-revision hash dependency follow from the existing envelope, writer pin, exact checkout and live source-ref contracts? Does the selected H/E/A/Q proposal remove that dependency without silently weakening those source checks or moving the problem into Q self-reference?
2. Does AP1 accurately limit its result to non-executable local Git proposals? Verify strict closed schema/types, production rejection of the distinct proposal kind, canonical source-ref binding, direct exact refs and rechecks, actual object hashes/types, sole parentage and the exact two-path tree delta.
3. Are the real Git fixtures meaningful? Inspect the ordinary same-ref stale-pin control, alias and symbolic-ref cases, actual noncommit object probes, writer/helper/plan changes, parent and mode/type mutations, malformed JSON, authority promotions and CLI controls. Mutation subtests must not inflate the **18-method** count.
4. Confirm the five R5 files retain their published Git blobs and the old **94 methods** are unchanged. Preserve R5's independent `PassDryAdmissionSourceOnly` scope; AP1 is a different proposal phase.
5. Verify the actual raw CI source SHA, two test footers and OK results. [Run **45743817742**](https://github.com/night-outlook/hybridclr_demo/actions/runs/45743817742), attempt 1, job **139654943143**, reports 1/1 focused job and 9/9 returned steps successful. Actual tests: **94 + 18**, with public execution still denied. Check [raw log](D5B_ACTIVATION_PUBLICATION_AP1_CI_JOB_139654943143_2026-11-25.log) and its evidence SHA-256; other automatic runs are outside the claim.
6. Check that the remaining runner identity/import closure, plan authority semantics, Q review/user-decision validation, live refs, physical inputs and retained namespace limitation are explicit further Primary work. A proposal pass must not imply that these are implemented or that a real envelope can be executed now.

The Primary peer review corrected a local-ref alias ambiguity before publication. It is implementation evidence, not an independent project verdict.

## Requested output and stop

Publish a separate independent report with a bounded **`PassActivationPublicationProposalOnly`** or **`ReturnRequired`** result, exact reviewed identities, findings, evidence and retained limits. Update README/current status to link that report. Do not self-convert a source/protocol pass into user approval, real Local results or a Human Review Gate.

The current production approval constants remain **None**, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, both Local execution statuses `NotAuthorized`, and R03/H2/Human Review readiness false. All 18 real Player cases remain **NoCoverage**. No Local command, new production activation ref, runner execution, Unity/IL2CPP/Player or later milestone is authorized. Stop after the independent report is committed and pushed.
