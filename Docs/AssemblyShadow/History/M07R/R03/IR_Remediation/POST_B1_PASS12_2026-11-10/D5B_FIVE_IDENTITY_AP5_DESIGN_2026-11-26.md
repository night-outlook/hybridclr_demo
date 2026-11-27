# D5-B AP5 Five-Identity Observation Design

Date: 2026-11-26

Status: design proposal only. This document asserts no implementation pass, accepted review, live-ref observation, or execution authority.

## 1. Purpose and boundary

AP5 introduces a standalone, source-only observer of five externally pinned physical checkout identities and their exact live branch refs: the four source repositories and a separate demo runner checkout. Its implementation is `Tools/AssemblyShadow/R03IR/D5Local/d5b_five_identity.py`.

The observer supplies the physical-checkout and live-ref mechanism needed by the AP1 identity requirements. It does not compose AP1 publication validation, AP2 artifact closure, AP3 imports, AP4 configuration consumption, or semantic source admission into a new authority decision. Those stages keep their existing scope and accepted bytes.

The four source commit pins in the new proposal are dynamic exact identities. This permits observation of a separately reviewed tuple and meaningful tests using actual temporary Git objects. A successful observation establishes that the supplied tuple was observed; it does not establish that the tuple is the accepted AP1 source tuple. The external proposal blob pin establishes byte identity, not approval.

AP5 also authenticates the narrow topology fact that the runner commit has the demo source commit as its sole parent. It does not check AP1's two-path publication delta, proposal-envelope contents, writer substitution, or artifact catalog. The parent edge therefore does not establish the AP1 runner publication relation.

The observer never invokes candidate entry points, imports the candidate writer or preflight, creates admission or evidence output, fetches objects, updates refs, builds Unity/native code, or launches a Player.

## 2. Public interface and proposal

The public API is:

```python
observe_five_identities(raw, expected_proposal_blob) -> FiveIdentityObservation
```

`raw` must be immutable `bytes`, bounded by the existing 1 MiB input limit. `expected_proposal_blob` must be an exact lowercase 40-character Git SHA-1. The observer must compare the actual Git blob ID of `raw` with that external pin before using its contents.

The proposal is a strict UTF-8 JSON object. Reject duplicate keys at every depth, non-finite numbers, unexpected or missing fields, wrong JSON types, and unsupported nesting. A boolean is not an integer schema version. The observer accepts no injected module, context, policy object, callback, prior report, transport command, remote URL, or bypass mode.

The top-level schema is closed:

| Field | Required value or shape |
| --- | --- |
| `schemaVersion` | Exact integer `1` |
| `kind` | `R03D5BFiveIdentityProposalV1` |
| `sourcePins` | Exactly the four repository roles below, each mapped to an exact lowercase 40-character SHA-1 |
| `sourceRef` | `refs/heads/codex/assembly-shadow-r01b-h1` |
| `runner` | Exactly `repository`, `commit`, and `ref` |
| `locations` | Exactly the AP2-shaped location fields below |
| `scope` | `CheckoutAndLiveRefObservationOnly_NoExecutionAuthority` |
| `authorization` | The exact AP1 `CLOSED_AUTHORITY` object |

The fixed source roles are `hybridclr_demo`, `hybridclr`, `hybridclr_unity`, and `il2cpp_plus`. Their canonical repositories are respectively `night-outlook/` followed by the role name. AP5 derives these repository identities and remote endpoints; the proposal cannot substitute another owner, repository, URL, or protocol.

`runner.repository` must equal `night-outlook/hybridclr_demo`. `runner.commit` must differ from `sourcePins.hybridclr_demo`. `runner.ref` must be a valid full local branch ref under `refs/heads/codex/`, must differ from `sourceRef`, and must pass Git's exact ref-format validation. The proposal supplies one exact runner ref, not a prefix or search pattern.

The four source commits do not need to be mutually different strings: a source identity is its fixed repository role together with its exact commit. The runner and demo source are explicitly distinct identities in the same repository.

### 2.1 Locations

`locations` contains exactly:

- `runnerRoot`: the separate runner checkout directory.
- `workspace`: the parent of the four source checkout directories.
- `historicalRoots`: exactly `originalS`, `b1EvidenceBase`, `b1Oneuse12`, `b1NativeHostRaw`, `b1B2HostRaw`, and `b1Preflight`.
- `evidenceParent`: the existing external evidence-parent directory.

All values must be normalized absolute path strings. Source roots are derived as `workspace / role`; there is no separate caller-supplied source-root mapping. All declared directories must exist, have canonical spellings, and resolve without a symlink or path alias.

Retain AP2's runner/protected-location and evidence-parent separation observations. Add pairwise physical separation of all five checkout roots, using both paths and directory identities, including ancestor identities. The four sources must be siblings under the declared workspace. Each checkout must have its own ordinary Git administrative directory, with its observed absolute Git directory and common directory equal to its own canonical `.git` directory. Require the 15 observed `.git`, `objects`, and `refs` directory identities to be pairwise distinct across all five checkouts. This checks those directory roots; it does not recursively establish exclusive ownership of their descendants, files, or underlying storage.

The six historical locations are protected path observations, not six authenticated historical datasets. AP5 does not import the writer's historical-custody or admission contract. It does not create an output root or validate the contents of the evidence parent.

### 2.2 Closed authorization

The proposal must contain exactly the existing AP1 values:

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

These values remain closed in successful and rejected reports. AP5 provides no operation that transforms this proposal into an executable envelope or approval.

## 3. Trusted helper reuse

Invoke AP5 in a trusted Python process with `-I -S -B`. Enforce these flags in the public API as well as the CLI. This is a trusted-process requirement, not a Python sandbox or standard-library identity proof.

Authenticate installed helper bytes before compiling or executing them. The reviewed helper pins are:

| Helper | Exact Git blob |
| --- | --- |
| `d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |

Use AP1's strict JSON, exact-type, SHA, and isolated local Git helpers. Use AP2's canonical-path, directory-identity, separation, fingerprint, no-follow read, raw-tree inventory, and complete worktree-observation primitives. These are reviewed verifier helpers; their loading must not select modules from candidate paths or ambient candidate module names. If private temporary module registration is required by dataclasses, remove that registration on every completion path without altering pre-existing module entries or `sys.path`.

Implement a new role-aware checkout front end in AP5. AP2's existing `_checkout_observation` has a demo-only origin allowlist and runner-specific assumptions, so it must not be silently repurposed for the other source repositories. Reuse its leaf mechanisms without changing the accepted AP2 file or its helper pins.

Do not use the RR5 `checked_checkout`, writer `inspect_source_and_remote`, or writer `inspect` as the AP5 identity boundary. They have different environmental, cleanliness, semantic-preflight, historical, and machine-input scope. AP5 does not call the AP2 closure proposal verifier or AP4 consumer observer and claim compatibility by association.

## 4. Local observation contract

Each of the five checkout observations must establish all of the following:

1. The root is the declared canonical directory, not a discovered parent repository or alias, and its identity remains the same across the scan.
2. The checkout is non-bare and has canonical ordinary `.git`, `objects`, and `refs` directories. The 15 observed administrative-directory root identities are pairwise distinct. Linked-worktree administrative files, shared common directories, shallow state, grafts, alternate-object stores, partial clones, and unsupported Git extensions are rejected. Recursive administrative-storage custody remains unverified.
3. Git runs through the isolated AP1 local reader, with inherited command/configuration overrides removed, optional locks disabled, replacement objects disabled, and lazy fetching/network protocols disabled.
4. Local configuration contains no includes, URL rewrites, filters, sparse configuration, hidden-status configuration, or other forms excluded by the reused checks. Exactly one origin must name the canonical repository for the checkout role using an accepted exact canonical spelling.
5. `HEAD`, the checked-out branch, and the exact local branch ref equal the supplied identity. The four source branches equal `sourceRef`; the runner branch equals `runner.ref`. Detached checkouts are outside this V1 contract.
6. The supplied commit and raw tree objects authenticate to their SHA-1 identities. For the runner, the parsed and Git-observed parent tuple is exactly the one-element tuple containing the demo source commit.
7. All index entries are supported stage-zero tracked entries, without assumed, skipped, unmerged, or submodule state, and the index exactly equals the committed tree.
8. Verifier-owned no-follow reads compare the entire worktree with that tree. Missing, untracked, and ignored entries fail. Regular-file type, mode, single-link status, sizes, bytes, directory entries, and read-time identities must satisfy the reused AP2 contract.

Tracked symlinks supported by AP2 are checked as literal link text and are never followed. This does not permit a symlinked checkout root, administrative directory, or traversed directory ancestor. A source semantic preflight does not follow from whole-checkout identity equality; AP5 reports only the identity fact it actually observed.

Use fresh local Git reader instances for the second pass so first-pass object and tree caches do not stand in for reobservation. Compare stable observed values, including root and administrative identities, HEAD/ref values, configuration and index digests, and complete worktree inventory digests and counts.

## 5. Exact live-ref transport

Live-ref observation is an explicitly permitted read-only network operation of AP5. It performs no fetch, push, local ref update, or object-store write.

Derive fixed HTTPS URLs of the form `https://github.com/night-outlook/` followed by the fixed repository name and `.git`. Query the exact source ref for each of the four source repositories and the exact distinct runner ref in the demo repository. The runner's remote target must equal `runner.commit`; it must not be inferred from the demo source ref or from a local tracking ref.

Use a separate fixed remote subprocess path, independent of the checkout-oriented AP1 `_Git` object. Its production invocation must have:

- A fixed system Git executable and argument list, without a shell.
- An explicit null Git directory, `--git-dir=/dev/null`, and `cwd=/`, with no candidate `-C` location.
- A constructed environment, with no inherited Git directory, namespace, config parameters, executable-path override, askpass, SSH, proxy, or TLS override variables.
- System/global configuration disabled, credential helpers cleared, terminal prompts disabled, HTTPS as the only permitted transport, TLS verification enabled, and redirects disabled.
- A fixed finite subprocess timeout and finite stdout/stderr size validation, neither adjustable by the proposal.

The explicit null Git directory and neutral current directory must be covered by focused tests of the selected system Git behavior. Do not create an empty temporary directory in production for transport isolation. AP5 creates no observer scratch or candidate output.

Require a single exact response row for each requested ref: the expected lowercase SHA-1, a tab, and the exact full requested ref name. Reject a missing ref, extra or duplicate rows, a wrong ref name, a different object ID, malformed bytes, command failure, timeout, or oversized captured output. Do not retry through a different protocol, arbitrary URL, tracking ref, saved report, or caller-supplied response.

Timeout and post-capture output-size validation do not establish hard subprocess-memory or network-byte bounds. The report and review must retain that limitation. Record network attempts and completed queries truthfully, including when a rejection occurs after a network attempt.

## 6. Observation sequence and equality

After proposal and helper authentication, execute this exact sequence:

1. Observe all declared locations.
2. Observe all five local checkouts, in the fixed role order with the runner last.
3. Observe all five exact remote refs in the same fixed order.
4. Reobserve all five exact remote refs.
5. Reobserve all five local checkouts using fresh local Git readers.
6. Reobserve all declared locations.

Require exact equality between the corresponding first and second observations and require every observed identity to equal its proposal pin. Git administrative identities are recorded and compared within the local checkout passes. Observation timestamps, if recorded, are explanatory metadata and must not be substituted for identity equality or included in an equality comparison that necessarily changes with time.

The two remote passes occur between the two complete local passes. Neither the sequence nor equal results establish an atomic snapshot across repositories, a frozen ref, uninterrupted custody, or proof that a value did not change and return between observations. A remote can change immediately after its final query, and a checkout can change immediately after its final read.

Reject the whole observation if any required phase fails or changes. Retain truthful partial progress, but do not turn a partial scan, one successful ref query, or the sole-parent fact into overall success.

## 7. Result and non-authority reporting

`FiveIdentityObservation` stores canonical immutable report bytes and returns decoded copies for presentation. Caller changes to a returned dictionary must not change the stored observation.

Ordinary `Exception` failures in observation become structured rejected reports. CLI argument-parser failures retain argparse's exit-2 stderr behavior. `BaseException`, termination, resource exhaustion, report-serialization failure, and unavailable output delivery are not covered by an unconditional JSON-delivery guarantee.

A completed report binds the exact proposal blob, the supplied five identities, the helper blob pins, the two rounds of local and remote observations, the compared location identities, the sole-parent topology result, and the finite observation scope. It records real operations and results without carrying an executable context or admission handle.

The following fields remain false even when all AP5 identity observations succeed:

```text
acceptedAP1SourceTupleVerified
runnerPublicationRelationVerified
AP2ArtifactCompatibilityVerified
AP4ConfigurationCompatibilityVerified
sourceSemanticPreflightVerified
executionAuthorityVerified
exclusiveCustodyVerified
continuousCustodyVerified
runtimeImportIsolationVerified
runnerExecutableClosureVerified
currentMacInputsVerified
```

Add `sourcePinsMatchAcceptedAP1SiblingPins` as factual metadata. It is true exactly when all three non-demo source pins equal AP1's existing `SOURCE_PINS`; it is false otherwise. This comparison does not turn `acceptedAP1SourceTupleVerified` true, authorize the tuple, validate an AP1 publication, or prove compatibility with captured AP2/AP4 inputs.

Report the narrow runner topology fact separately as `runnerSoleParentObserved`. On a completed observation it is true, while `runnerPublicationRelationVerified` remains false. `plannedReadOrder` describes the complete intended sequence even on early rejection; the attempted/completed arrays and observation maps record actual progress.

Preserve the exact AP1 closed authority values. Also report that candidate code was not imported or executed, admission and configuration-consumer functions were not invoked, output and observer scratch were not created, and Unity/Player operations were not performed. Real build state remains `NotRun`, passed Player cells remain zero, and the 18 cells retain no coverage. No report is an approval, executable envelope, receipt, or evidence promotion.

## 8. Resource and observational limits

Retain the existing AP2 traversal and file-read bounds:

| Resource | Existing bound |
| --- | --- |
| Proposal or installed helper bytes | 1 MiB |
| One tracked regular file | 256 MiB |
| Tracked bytes in one checkout scan | 4 GiB |
| Entries in one checkout scan | 100,000 |
| Tree depth | 64 |

Ten complete checkout scans can hash up to 40 GiB of tracked bytes under these per-checkout limits. The design deliberately makes this cost visible. It does not describe repeated full scans as a lightweight metadata check.

AP1's local Git subprocess reader captures output and caches whole objects before AP2's traversal limits apply. Remote subprocess timeout and output-size validation likewise do not establish a hard process-memory bound. AP5 must not claim such a bound, nor a global wall-clock bound for potentially blocking filesystem reads. Unsupported sizes, entries, topology, configuration, or filesystem features fail closed under the actual implemented checks.

The observer relies on a trusted Python process, system Git, standard library, and operating system. It provides neither a malicious-process sandbox nor continuous protection of the namespace it reads.

## 9. Focused verification plan

Use actual temporary working checkouts and actual temporary bare repositories for synthetic positive and negative fixtures. Generate genuine Git commits, trees, index state, and branch refs. Use the private test transport to route only the network invocation to those real temporary bare refs. Do not expose a production transport callback, alternate URL, file-protocol option, or synthetic-success mode.

Separately verify the unmodified production argument/environment selection. Local fixture results do not qualify actual production HTTPS reachability or observe the real GitHub refs.

The focused test set must cover:

1. Complete positive observation of five real checkouts and five real refs, including a distinct demo runner commit with the demo source as sole parent and every authority field still closed.
2. Exact proposal and type rejection: external blob mismatch, duplicate keys, invalid schema types, unknown/missing roles or fields, malformed SHA, arbitrary endpoint fields, and source/runner commit or ref collisions.
3. Topology distinction: reject zero-parent, wrong-parent, and merge-parent runners; accept only the selected one-parent fact without claiming AP1's two-path publication relation.
4. Canonical location and Git-layout rejection: aliases, nesting, shared physical roots or administrative directories, gitfiles, linked worktrees, bare/shallow/grafted/alternate/partial-clone state, wrong origins, and unsupported configuration.
5. Complete cleanliness: staged or unstaged bytes, missing/untracked/ignored entries, wrong mode, hard links, assumed/skipped/unmerged entries, and submodules. Confirm that supported tracked symlink text is observed without following its target.
6. Exact remote responses: missing, duplicate, extra, wrong-name, wrong-SHA, malformed, non-ASCII, oversized, timed-out, and failed observations, without fallback.
7. Recheck drift: changed local root, administrative identity, config, index, worktree bytes, HEAD/local ref, or remote ref between corresponding observations.
8. Transport isolation: a benign local URL-rewrite configuration and inherited Git/config/askpass sentinels cannot alter the fixed production endpoint or invoke a helper; null-Git-directory behavior and the selected fixed arguments/environment are verified.
9. Boundary and progress truthfulness: bad helper pins and missing interpreter isolation reject before network; rejection preserves actual partial progress; candidate imports, admission calls, output creation, scratch writes, and Unity/Player operations remain absent.
10. Report scope: sibling-pin metadata is correct for both matching and nonmatching synthetic tuples; the accepted-tuple, publication, AP2/AP4 compatibility, semantic-admission, custody, and execution-authority fields remain false on success.

Tests must distinguish fixture routing from the production transport. They must not manufacture live-ref success by merely returning an expected dictionary, patch the public input policy to accept arbitrary endpoints, or treat a source-code inspection assertion as a real checkout/ref positive test.

The administrative-root uniqueness guard may be tested by injecting duplicate identity tuples after real checkout scans. Such negative coverage verifies the comparison rule; it must not be described as an actual mounted-alias integration fixture.

## 10. Preservation and review gate

All 15 already accepted Python/configuration files remain byte-for-byte unchanged. AP5 adds its own observer, focused tests, and design/review material without refactoring or repinning those accepted files.

The preserved `D5Local` files are:

- `d5b_activation_publication.py`
- `d5b_local_admission.py`
- `d5b_local_admission_plan_v1.json`
- `d5b_runner_closure.py`
- `d5b_runner_configuration.py`
- `d5b_runner_imports.py`
- `run_d5_local.py`
- `test_d5b_activation_publication.py`
- `test_d5b_local_admission.py`
- `test_d5b_runner_closure.py`
- `test_d5b_runner_configuration.py`
- `test_d5b_runner_imports.py`

The preserved `D5Admission` files are:

- `d5b_custody_authority.py`
- `d5b_rr5_source_preflight.py`
- `d5b_rr5_source_preflight_v1.json`

Independent review of the completed implementation must return one of these exact verdicts:

- `PassFiveIdentityObservationSourceOnly`: the implemented and verified change satisfies this physical/ref observation contract, preserves the accepted files, and retains every stated limitation and closed authority field.
- `ReturnRequired`: the implementation, evidence, scope, preservation, or reporting does not satisfy the contract; the review identifies the concrete corrections required.

This design document grants neither verdict. A later pass remains limited to five-identity source-only observation. It does not admit source data, qualify actual production HTTPS reachability, authorize local execution, promote evidence, accept R03/H2, or open the human-review gate.
