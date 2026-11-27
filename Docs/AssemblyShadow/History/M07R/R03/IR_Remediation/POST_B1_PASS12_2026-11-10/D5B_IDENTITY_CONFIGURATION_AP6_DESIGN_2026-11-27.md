# D5-B AP6 Identity and Configuration Composition Design

Date: 2026-11-27

Status: design proposal only. This document asserts no implementation pass, independent review verdict, production live-ref observation, source admission, or execution authority.

## 1. Purpose and bounded increment

AP6 adds a source-only composition observer at `Tools/AssemblyShadow/R03IR/D5Local/d5b_identity_configuration.py`. It relates an externally pinned AP2 closure proposal C and an externally pinned AP5 identity proposal I, runs the accepted AP5 and AP4 public observers in that order, and compares the common runner and location observations at their existing boundaries.

The useful new claim is deliberately narrow: the two exact proposals describe the same source tuple, runner, source ref, and locations; the tuple uses the fixed AP1 sibling pins; AP5 completed its five-checkout/ref observations; AP4 subsequently completed its captured configuration consumers; and AP5's final runner/location observations match the corresponding AP2 observations captured before AP4 initialized candidate modules.

This is sequential composition. It does not establish a simultaneous five-identity snapshot, custody throughout the gap between stages, state after the consumers, frozen remote refs, source semantic admission, executable admission, or a handoff to Local execution. There is one AP5 call and one AP4 call. AP6 does not add a second AP5 pass after AP4.

AP4 remains responsible for its own fresh AP2 snapshot, private AP3 module initialization, captured configuration adapters, and the two actual configuration consumer calls. AP6 does not change those implementations, expose their contexts, or substitute a previously observed bundle.

## 2. Public interface and exact proposal relation

The public API is:

```python
observe_identity_configuration(
    closure_raw,
    expected_closure_blob,
    identity_raw,
    expected_identity_blob,
)
```

Both raw inputs must be immutable `bytes` within the existing 1 MiB proposal bound. Each external pin must be an exact lowercase 40-character Git SHA-1. Compare the actual Git blob ID of each byte string with its supplied external pin before interpreting the proposal contents.

The external pins establish byte identity, not approval. The API accepts no caller-supplied observation, report, bundle, module context, transport, remote endpoint, callback, helper pin, alternate source policy, or execution mode.

Parse both inputs as strict UTF-8 JSON objects. Reject duplicate keys at every depth, non-finite values, malformed or unsupported nesting, missing or unexpected fields, and incorrect JSON types. Equality must preserve JSON types: `true` is not schema version `1`, and `false` is not integer zero.

The relation gate must complete before invoking either public observation stage. It must establish the following exact common projection:

| Field | Required relation |
| --- | --- |
| `sourcePins` | Exactly `hybridclr_demo`, `hybridclr`, `hybridclr_unity`, and `il2cpp_plus`; each value is an exact SHA-1 and matches the corresponding value in the other proposal. |
| `sourceRef` | Both equal `refs/heads/codex/assembly-shadow-r01b-h1`. |
| `runner` | Exactly `repository`, `commit`, and `ref`, with matching values and types in C and I. |
| `runner.repository` | Exactly `night-outlook/hybridclr_demo`. |
| `runner.commit` | Distinct from `sourcePins.hybridclr_demo`. |
| `runner.ref` | The same full supported `refs/heads/codex/...` branch in both proposals, distinct from the fixed source ref. |
| `locations.runnerRoot` | The same normalized absolute path string. |
| `locations.workspace` | The same normalized absolute path string; the four source roots remain its fixed role-named children. |
| `locations.historicalRoots` | Exactly the six accepted roles, with identical normalized absolute path strings. |
| `locations.evidenceParent` | The same normalized absolute path string. |
| `authorization` | The exact accepted closed authority object and JSON types in each proposal. |

The six historical roles are `originalS`, `b1EvidenceBase`, `b1Oneuse12`, `b1NativeHostRaw`, `b1B2HostRaw`, and `b1Preflight`. Comparing only runnerRoot or workspace is insufficient. The relation binds the complete location declaration, including the protected historical roots and evidence parent.

C retains the accepted `R03D5BRunnerClosureProposalV1` structure and `ArtifactSnapshotOnly_NoCandidateImports` scope. I retains the accepted `R03D5BFiveIdentityProposalV1` structure and `CheckoutAndLiveRefObservationOnly_NoExecutionAuthority` scope. AP6 does not add fields or authority to either proposal.

The relation gate is a prerequisite, not a replacement for each observer's full validation. AP5 must still validate I, its physical checkouts, topology, and refs. AP4 must still validate C through its existing AP2 chain before initializing candidate modules. Matching proposal metadata does not establish the artifact catalog, publication delta, physical directories, or live refs.

### 2.1 Fixed AP1 sibling pins

The relation gate must also require the accepted AP1 sibling pins:

| Source role | Exact commit |
| --- | --- |
| `hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` |
| `hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| `il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` |

The demo source commit remains the exact externally proposed commit, subject to AP1/AP2's publication and reviewed-artifact requirements. AP6 does not introduce an alternate sibling-pin policy.

AP5 intentionally permits arbitrary exact proposed source commits and reports whether its sibling metadata matches AP1. AP2 constructs its expected closure with AP1's fixed `SOURCE_PINS`. Consequently, matching C and I is not enough if both have the same unsupported siblings. AP6 must reject that pair before AP5 transport attempts or AP4 candidate initialization.

The accepted AP5 report retains its original meaning and fields. AP6 must not rewrite AP5's `acceptedAP1SourceTupleVerified`, publication, or AP2/AP4 compatibility fields to make a composed result appear to have been established by AP5 alone.

## 3. Trusted process and accepted helpers

Require a trusted POSIX Python process invoked with `-I -S -B`, enforced in the API and CLI. This is an isolation requirement for the reviewed observer. It is not a Python sandbox, standard-library identity proof, or protection against a malicious trusted process or operating system.

Authenticate installed helper bytes before compiling or executing them. The two directly reused public observers have these exact Git blobs:

| Direct helper | Exact Git blob |
| --- | --- |
| `d5b_runner_configuration.py` (AP4) | `5263742017950a28bd9750eeeaefe50df4f4fa49` |
| `d5b_five_identity.py` (AP5) | `ab4e9cbf796d4ab91602a14a9294d3773e75879c` |

Their accepted helper chain remains unchanged:

| Existing helper | Exact Git blob |
| --- | --- |
| `d5b_runner_imports.py` used by AP4 | `22ad93598131a59b2d5c46174a45187aede848a6` |
| `d5b_runner_closure.py` used by AP3/AP5 | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `d5b_activation_publication.py` used by AP2 | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |

Any additional accepted parsing/helper code loaded by the relation gate must be authenticated before execution as well. Module-name lookup, a pre-existing ambient module, or caller-supplied objects cannot replace the pinned implementation. Helper drift rejects; no repinning or fallback occurs at runtime.

Follow the existing bounded no-follow input/helper read approach. If temporary private module registrations are needed, preserve pre-existing slots, remove the observer's registrations on every completion path, and verify that the real `sys.path` and ambient candidate module cache remain unchanged. The candidate module names remain `d5b_rr5_source_preflight`, `d5b_local_admission`, and `run_d5_local`.

## 4. Fixed stage sequence

The successful call sequence is:

1. Enforce process isolation, validate immutable inputs and both external byte pins, authenticate the required trusted helpers, parse the proposals, and complete the exact relation and fixed-sibling checks.
2. Call `observe_five_identities(identity_raw, expected_identity_blob)` exactly once. Retain its frozen report. A rejected AP5 stage stops the sequence before AP4.
3. Call `observe_runner_configuration(closure_raw, expected_closure_blob)` exactly once. Retain its frozen report. AP4 obtains its own fresh AP2 snapshot, initializes its private modules, and calls only its accepted captured configuration consumers.
4. Compare the common runner and location observations described in section 5. Complete the composition only if both comparisons succeed.
5. Produce the immutable composition report with explicit stage order, actual partial progress, both proposal pins, the matched proposal projection, the scoped comparison result, the nested stage reports, and closed authority.

AP6 does not call AP2 separately and then claim that AP4 consumed that earlier snapshot. AP4's existing `observe_runner_configuration` owns the snapshot it consumes. The direct AP2 API `verify_runner_closure` and proposal constructor `make_closure_proposal` remain unchanged; the latter can support fixture construction without becoming an observation or execution mode.

AP4 performs the actual `read_plan(verify_blob=True)` and `checked_profile(..., check_blob=True)` calls through its accepted private adapters. Preserve both enabled blob checks, the actual function identities, and the accepted fixed operation shape. AP6 introduces no pathname fallback, candidate source rewriting, consumer replacement, runtime-path adapter, or approval-constant change.

### 4.1 Failure timing

The relation gate parses C as strict JSON and validates its shared fields against the complete I schema. Full closure-specific schema and artifact validation remains with the later unchanged AP4/AP2 call. A closure-specific defect can therefore reject after AP5 has performed its identity and remote-ref observations; the report must retain those completed observations and possible network activity.

The comparison in section 5 occurs after the AP4 public call returns. At that point its candidate module initialization and both configuration consumer calls may already have completed. A cross-stage mismatch must reject the composition while truthfully retaining that progress.

AP6 must not claim that the final comparison guarded entry into those consumers. Preventing entry on that comparison would require a different API boundary or refactor of the accepted AP4 code, outside this increment.

## 5. Exact cross-stage comparison

The comparison scope is:

> AP5 final observations versus AP2 observations before AP4 candidate module initialization.

The report must state this scope explicitly. It must not describe the comparison as a check after configuration consumption or an observation of the current checkout at report time.

### 5.1 Common runner checkout fields

Take the runner object from:

```text
AP5.report.checkoutObservations.after.runner
```

Project exactly these 12 common AP2 fields:

| Common field | Meaning within the existing observation |
| --- | --- |
| `head` | Observed exact checkout HEAD. |
| `branch` | Observed attached branch ref. |
| `origin` | Observed exact canonical origin spelling. |
| `gitDir` | Observed ordinary absolute Git directory. |
| `commonDir` | Observed common Git directory. |
| `configSha256` | Digest of the observed local configuration representation. |
| `indexFlagsSha256` | Digest of the observed index flags representation. |
| `indexStagesSha256` | Digest of the observed staged index representation. |
| `worktreeInventorySha256` | AP2 raw worktree inventory digest, including its recorded metadata. |
| `worktreeFiles` | Observed worktree file count. |
| `worktreeEntries` | Observed worktree entry count. |
| `worktreeBytes` | Observed worktree byte total. |

Compare that projection, including exact value types, with:

```text
AP4.report.importObservation.artifactObservation.observedCheckout
```

Require the expected key roster and reject missing, malformed, or unexpected comparison structure. Do not silently compute the intersection of two available dictionaries or omit a field whose value differs.

AP5's additional fields, such as its role, repository, selected root, commit, ref, tree, parents, Git executable, and administrative-directory identities, remain in its nested report. AP2 does not emit all those fields in `observedCheckout`; the composition must not present their absence as a new AP2 comparison or claim broader administrative custody.

### 5.2 Complete location observations

Compare, with exact value types:

```text
AP5.report.locationObservations.after
```

against:

```text
AP4.report.importObservation.artifactObservation.observedLocations
```

This is equality of the complete accepted location-observation map, including each recorded path, device, and inode for the runner, workspace, evidence parent, six historical roles, and four derived source roots. It supplements the earlier exact proposal-location relation with a comparison of the observations emitted by the two accepted stages.

It does not revalidate historical data, establish exclusive storage ownership, or inspect source semantics. Matching directory identities are observations at the stated stage boundaries.

### 5.3 Limits of equality across stages

The two existing observers make repeated sequential reads. Equality of their reported fields does not establish uninterrupted custody, prevent a change and restoration in the intervening interval, or bind a remote ref to the instant of AP4 consumption.

AP4 freezes its nested AP2 and AP3 observations before consumer calls. Reading those frozen observations after AP4 returns does not make them current observations. A configuration pathname can change after AP2 capture while the accepted AP4 adapters continue consuming their captured bytes; AP6 must preserve that distinction.

## 6. Report contract and closed authority

Return an immutable observation whose stored representation is JSON bytes and whose public report access yields a fresh JSON value. Rejections must also retain frozen, truthful partial progress. The report accepts no externally supplied successful stage result as proof.

Distinguish at least these facts:

- Both external proposal byte pins were checked.
- The exact proposal relation and fixed AP1 sibling policy passed.
- AP5 was attempted and completed, with its own partial or completed report.
- AP4 was attempted and completed, with its own partial or completed report.
- The AP5-after/AP2-before-initialization runner comparison was attempted and matched.
- The corresponding complete location comparison was attempted and matched.
- The composition completed within the stated sequential scope.

Do not flatten stage reports into a shared dictionary. AP5 correctly says it did not import candidate code; AP4 may have initialized candidate modules and invoked configuration consumers. AP4 correctly reports no network use; the composition may have attempted AP5 remote processes. Overall fields must reflect the actual stage progress, while each nested report retains its original scope and values.

Record attempted operations before entry and completed operations only after return. If AP4 rejects after partial initialization or one consumer, preserve that report and its actual progress. If a final comparison rejects after AP4 succeeds, preserve the completed AP4 report rather than resetting candidate activity to false.

The successful and rejected composition reports retain the exact closed authority values:

```json
{
  "approvedEnvelopeGitBlob": null,
  "independentlyReviewedExecutableAdmission": "Pending",
  "explicitUserLocalApproval": "NotAuthorized",
  "WEB_TO_LOCAL": "CLOSED_NO_LOCAL_EXECUTION",
  "D5BLocalExecution": "NotAuthorized",
  "D5LocalValidation": "NotAuthorized",
  "R03Accepted": false,
  "H2Passed": false,
  "ReadyForHumanReviewGate": false,
  "allowNativeBuild": false,
  "allowPlayerLaunch": false
}
```

The composition continues to report no executable authority, Q authorization, simultaneous snapshot, exclusive custody, continuous custody, frozen refs, source semantic preflight, source-data admission, current Mac-input verification, general runtime import isolation, general or future runtime configuration binding, executable closure, or Python sandbox.

Candidate entry points, admission preview, source-inspection entry points, Unity/native build operations, and Player launch remain uninvoked. Observation creates no evidence output, receipt, admission result, or observer scratch. Its machine-readable report may be emitted to stdout. Network activity is confined to the accepted AP5 remote-observation stage and must be reported conservatively when attempted.

Real build state remains `NotRun`; passed real Player cells remain zero; all 18 real Player cells retain no coverage. Existing nested independent-review fields are not rewritten by AP6. A composition report is an observation, not an approval or evidence promotion.

## 7. Verification strategy and honest coverage labels

### 7.1 Host source-only tests

The host suite must distinguish relation tests, orchestration tests, and component behavior. A host orchestration positive that doubles AP5 is not a full five-identity integration positive.

Use test-only private seams for stage doubles without exposing those seams through the production public API. Keep production source pins, helper pins, argument selection, input validation, and accepted files unchanged.

Focused host coverage must include:

1. Exact external byte pins, immutable input types, size limits, strict JSON, closed schema and authority, and exact JSON types.
2. A mismatch in every common identity field and every declared location role, including sourceRef, runner repository/commit/ref, the four source pins, all six historical paths, and evidenceParent.
3. Identically unsupported sibling pins in both proposals, rejected before AP5 or AP4 is invoked.
4. Helper drift and missing interpreter isolation, rejected before affected helper execution, network attempts, or candidate initialization.
5. Exactly one AP5 call followed by exactly one AP4 call with the original exact bytes and pins; AP5 rejection prevents AP4.
6. Separate failures of every common runner comparison field, location-observation drift, and Boolean/integer aliases, with no silent key intersection or type coercion.
7. AP4 partial failure and final-comparison failure after real or test-declared consumer progress, retaining truthful attempted/completed state.
8. Report immutability, nested stage-scope preservation, private helper cleanup, unchanged ambient import state, and closed authority on every outcome.
9. CLI argument rejection and actual `-I -S -B` enforcement, without a caller-facing transport, callback, or bypass option.

Retain real AP4 positive coverage from a genuine AP1/AP2-compatible synthetic demo/runner fixture and actual captured consumers. Its runner ref must use the supported `refs/heads/codex/...` spelling.

The earlier AP2/AP4 fixture binds the real sibling pins in proposal metadata but leaves the sibling workspace directories empty. The earlier AP5 fixture creates real synthetic sibling checkouts with different commit IDs and deliberately reports a nonmatching AP1 sibling tuple. Neither fixture alone is a complete AP6 positive. Do not relabel either as one or weaken the production pin policy to combine them.

### 7.2 Required full CI positive

CI must provide the actual three pinned sibling repositories at the exact commits in section 2.1. Check them out with `fetch-depth: 0` and `persist-credentials: false`. A shallow repository, a substitute commit, or an unavailable required repository is not acceptable positive coverage.

The integration fixture must clone the pinned objects into temporary ordinary checkouts and temporary bare file remotes. These fixture clones must have separate ordinary administrative directories, complete required objects, no alternate-object stores or shallow state, and no fixture-induced shared checkout roots. Use the canonical repository origins and attach each fixture source HEAD to the exact fixed source ref. Set the fixed ref in each temporary bare repository to its pinned commit.

Construct the demo source and separate runner from the actual reviewed AP1/AP2 candidate artifact bytes. The runner must be the demo source's sole child under the accepted AP1 publication relation: the exact allowed writer substitution and new closed proposal envelope, with the accepted closure catalog. Use the same demo source commit in the separate source checkout and the runner's local source ref. Put both source and runner refs in the temporary demo bare remote.

Create the complete declared location set outside the observed checkouts as required. Construct C through the accepted AP2 proposal rules and construct I with the same exact identity/location projection and fixed sibling pins. Record each exact proposal byte pin.

The required full positive must invoke the real AP6 public API, the real accepted AP5 observer, and the real accepted AP4 observer. It must execute genuine local checkout scans, actual exact-ref queries against temporary bare refs, real AP2 closure validation, real AP3 initialization, and the actual captured configuration consumers. It may not double observations, reports, checkout readers, publication verification, snapshots, initializers, consumers, or the cross-stage comparison.

The sole allowed integration adaptation is test-private routing of AP5's remote subprocess transport to the corresponding real temporary file remote. Validate the original production command, fixed HTTPS endpoint, exact ref, and isolated environment before routing. Retain the original parsing, subprocess handling, repeated passes, and equality checks. No production file transport, endpoint override, or fixture mode is added.

The fixture result establishes integration against actual pinned sibling trees and real local refs. It does not qualify production HTTPS reachability or claim observation of the real GitHub refs. Keep that limitation explicit in CI evidence.

The required CI integration must fail or otherwise block the review gate if its pinned inputs are missing or the test cannot run. A skipped required positive is not a successful full-positive result. CI evidence must identify the checked-out repository commits and distinguish the full integration from host orchestration tests.

### 7.3 Scope-specific drift coverage

Verify the comparison boundary using benign fixture mutations between AP5 completion and AP4's AP2 observation: runner metadata/inventory or location identity differences must reject at the appropriate stage or final comparison.

Separately verify that AP6 does not reinterpret a frozen pre-initialization observation as a post-consumer check. A test that changes a configuration pathname after AP2 capture must preserve the accepted AP4 captured-byte semantics and label the scope honestly. No positive test may claim continuous custody merely because the same recorded state is seen at separated observations.

The observer call itself remains read-only with respect to fixture checkouts, refs, protected locations, and evidence parent. Fixture construction and deliberate negative mutations belong to the test harness outside the observation boundary.

## 8. Preservation

All 17 accepted Python/configuration files remain byte-for-byte unchanged. AP6 adds its own observer, focused tests, required integration/CI support, and design/review material without refactoring or repinning accepted implementations or weakening their policies.

The 14 preserved files under `Tools/AssemblyShadow/R03IR/D5Local/` are:

- `d5b_activation_publication.py`
- `d5b_local_admission.py`
- `d5b_local_admission_plan_v1.json`
- `d5b_runner_closure.py`
- `d5b_runner_configuration.py`
- `d5b_runner_imports.py`
- `d5b_five_identity.py`
- `run_d5_local.py`
- `test_d5b_activation_publication.py`
- `test_d5b_local_admission.py`
- `test_d5b_runner_closure.py`
- `test_d5b_runner_configuration.py`
- `test_d5b_runner_imports.py`
- `test_d5b_five_identity.py`

The three preserved files under `Tools/AssemblyShadow/R03IR/D5Admission/` are:

- `d5b_custody_authority.py`
- `d5b_rr5_source_preflight.py`
- `d5b_rr5_source_preflight_v1.json`

Preservation verification must compare these exact file bytes with the accepted baseline. Updating a pin to accommodate an unintended accepted-file change is not preservation.

## 9. Review gate

Independent review of the completed implementation and its evidence must return one of these exact verdicts:

- `PassIdentityConfigurationCompositionSourceOnly`: the implemented and verified change satisfies the exact proposal relation, fixed AP1 pin policy, unchanged accepted-helper reuse, AP5-to-AP4 sequence, scoped runner/location comparison, required full CI integration, preservation, truthful reporting, and closed authority requirements.
- `ReturnRequired`: the implementation, tests, required integration evidence, scope, preservation, or reporting does not satisfy the contract; the review identifies the concrete corrections required.

This design document grants neither verdict. No implementation or verification result is asserted here. A later source-only composition pass would still not authorize Local execution, establish custody after configuration consumption, admit source data, promote evidence, accept R03/H2, or open the human-review gate.
