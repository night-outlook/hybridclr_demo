# D5-B AP5 Independent Review Request

Date: 2026-11-26 America/Los_Angeles

**Independent AP5 review is Pending.** Review the four-path source increment at `0dff80b0fffb37d8c13ff08ad955454a60dde5d6`, tree `d43a6ca553ad009b656b7691df89cf34f0508280`, against accepted baseline `911d8f96f44430124c487698dde53183d7a75dd2` on `codex/assembly-shadow-r01b-h1`. The containing Primary publication adds documentation and evidence only. Identify its exact current pushed SHA separately; do not substitute it for the CI-tested source.

## 1. Exact review references

- [Design](D5B_FIVE_IDENTITY_AP5_DESIGN_2026-11-26.md); [Primary report](D5B_FIVE_IDENTITY_AP5_PRIMARY_2026-11-26.md); [machine evidence](D5B_FIVE_IDENTITY_AP5_EVIDENCE_2026-11-26.json).
- [Host transcript](D5B_FIVE_IDENTITY_AP5_SOURCE_HOST_2026-11-26.log); [CI transcript](D5B_FIVE_IDENTITY_AP5_CI_45929766326_JOB_140279429052.log).
- [Actions 45929766326 / job 140279429052](https://github.com/night-outlook/hybridclr_demo/actions/runs/45929766326/job/140279429052), attempt 1: 210/210 methods, one successful job and 13 successful returned steps.
- All 15 accepted Python/configuration blobs are preserved; the exact source delta contains only the new observer, focused tests, design and workflow change.

AP4 is accepted as `PassRunnerConfigurationBindingSourceOnly` for exact source `000e72941f74e52aa18bcd17553e8929acc69167`, including the changed AP3 helper `22ad93598131a59b2d5c46174a45187aede848a6`, with independent publication `911d8f96f44430124c487698dde53183d7a75dd2`. AP3 `PassRunnerImportBootstrapSourceOnly`, AP2 `PassRunnerArtifactClosureSourceOnly`, AP1 R2 `PassActivationPublicationProposalOnly`, `D5B-AP1-IR-01=ClosedInCorrectedSource`, and R5 `PassDryAdmissionSourceOnly` remain preserved in their accepted scopes. Retained earlier AP4-pending labels are historical and do not override the independent AP4 decision.

Review `Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py`, `test_d5b_five_identity.py`, the direct unchanged AP2/AP1 helper calls and the workflow. Use the report's exact four-repository tuple and source hashes. Historical Mac paths remain physically Unverified. These tests exercise temporary fixtures; actual production HTTPS reachability and real production five-checkout state remain unqualified.

## 2. Contract to review

`observe_five_identities(raw, expected_proposal_blob)` requires trusted POSIX Python `-I -S -B` and a strict externally blob-pinned `R03D5BFiveIdentityProposalV1`. The proposal selects four dynamic exact source commits under the fixed source feature ref plus a distinct demo runner commit and restricted full codex branch ref. It uses AP2-shaped canonical locations, fixed repository roles, derived endpoints, exact AP1 `CLOSED_AUTHORITY`, and scope `CheckoutAndLiveRefObservationOnly_NoExecutionAuthority`.

Check that the five checkout roots are physically separate and all 15 observed `.git`, `objects`, and `refs` directory-root identities are pairwise distinct, each checkout is canonical/ordinary/clean at its exact attached branch and commit, logical index entries equal the authenticated tree, and AP2's no-follow complete worktree scan compares the actual entries and bytes. The runner's sole parent must equal the demo source commit. That single edge must not be reported as the AP1 two-path publication relation.

Verify this exact order and equality checks: locations before; five local observations before; five remote observations before; five remote observations after; five local observations after; locations after. Check rejection paths and truthful partial progress as well as successful fixtures. `runnerSoleParentObserved` can be true after completed local passes without making a later rejected overall observation successful.

## 3. Required review evidence

- Confirm unchanged bytes for all 15 accepted Python/configuration files. AP5 must reuse the pinned AP2 helper `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` and AP1 helper `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` without repinning or importing candidate modules.
- Review strict proposal/helper rejection, canonical aliases and overlap, unsupported Git layouts/configuration, wrong origins/HEAD/branches, logical index and complete worktree differences, sole-parent failures, and local/ref/location recheck drift.
- Inspect actual temporary checkout/bare-repository positive fixtures. Only private test transport may reroute remote calls; a fabricated expected report is not a real checkout/ref positive. Require separate evidence that production endpoint/argument/environment selection is unchanged and isolated from local URL rewrites and inherited configuration sentinels.
- Review exact remote parsing and error paths: one exact requested ref row, expected SHA, no missing/extra/duplicate/wrong rows, command failure, timeout, and oversized output rejection without fallback.
- Check that stored report bytes are immutable through returned dictionaries, helper registration is cleaned up, candidate import state is unchanged, and rejected reports retain accurate attempted/completed phases and conservative possible-network flags.

Production transport uses derived canonical HTTPS URLs, an explicit null Git directory with `cwd=/`, a constructed environment, HTTPS-only protocol selection, TLS verification, disabled redirects/prompts, and cleared credential helpers, proxy configuration and inherited configuration. It creates no observer scratch. Each query has a 30-second timeout and a 65,536-byte stdout/stderr validation limit after capture. Actual production HTTPS reachability and live production refs remain unqualified by the private local fixture tests.

## 4. Scope and authority checks

Dynamic exact proposal pins are not AP1 approval. `sourcePinsMatchAcceptedAP1SiblingPins` is metadata only. Require these fields to remain false even on an AP5 success: `acceptedAP1SourceTupleVerified`, `runnerPublicationRelationVerified`, `AP2ArtifactCompatibilityVerified`, `AP4ConfigurationCompatibilityVerified`, `AP4CompositionVerified`, `sourceSemanticPreflightVerified`, and `sourceDataInputsVerified`.

Also retain the stated limits: sequential observations provide neither atomic state nor frozen refs, continuous/exclusive custody, future-read binding, runtime isolation, raw Git index-byte verification, or complete administrative custody. The AP2 limits are 1 MiB proposal/helper reads, 256 MiB per tracked file, 4 GiB and 100,000 entries per checkout scan, and depth 64; ten scans can hash up to 40 GiB. Captured Git output and object caches mean there is no hard process-memory or network-byte bound, and blocking filesystem reads have no claimed global wall-clock bound.

No candidate writer/preflight import, admission/configuration-consumer invocation, evidence output, Unity/Player operation, or Q execution is authorized. Require the null approved envelope, closed WEB-to-Local state, `NotAuthorized` Local execution/validation, false R03/H2/human-review-gate flags, `NotRun` build, zero Player passes, and 18 cells without coverage to remain unchanged.

## 5. Requested verdict

Return exactly one of:

- **`PassFiveIdentityObservationSourceOnly`** — the exact reviewed candidate and supplied evidence satisfy the narrow physical-checkout/exact-ref contract and preservation requirements, with the limitations and authority closure intact.
- **`ReturnRequired`** — identify the concrete implementation, evidence, preservation, or reporting defects and required corrections.

The runtime result `FiveIdentitiesObserved_NoExecutionAuthority` is not an independent review verdict. Any independent pass remains source-only and cannot qualify production HTTPS reachability, admit source data, authorize Local execution, promote evidence, accept R03/H2, or open the human-review gate.

## 6. Review protocol and stop point

Verify the authoritative branch, source-to-publication ancestry, four-file source delta, 15 preserved blobs, Local-owned record identities, source-host/CI log hashes, exact CI checkout and AP5 method identities. Read ordinary-failure progress and the real null-Git-directory transport test. The all-15 administrative-root guard and `plannedReadOrder` clarification are included in the submitted source and must be reviewed; neither claims recursive storage custody or a completed sequence on early rejection.

Any source-host rerun must use a downloaded exact-source copy and the commands recorded in the evidence; record tool versions, commands, actual methods/footers and before/after file identities. Such a rerun qualifies those downloaded bytes, not a physical Mac checkout or historical host. No Local/Mac/Unity/Player operations, production ref mutations, approval changes or candidate integration are requested.

Publish the independent report/evidence under `Docs/AssemblyShadow`, update the canonical review status without changing implementation or Primary-owned handoff content unless explicitly required, preserve Local-owned records, and stop after the exact source-only verdict and remote readback. A request for correction returns to Primary. Production `APPROVED_EXECUTION_ENVELOPE_BLOB=None` and `APPROVED_LOCAL_HANDOFF_BLOB=None` remain unchanged. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`; `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false. Q, explicit user Local approval, native/Player permission and production activation remain unauthorized. Current real Unity/native/Player work remains `NotRun`; all 18 real Player cells remain `NoCoverage`, with zero passed. Historical Mac paths are physically `Unverified`. The candidate proposal literal is not an approval and is not assumed null.
