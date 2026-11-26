# D5-B AP4 Independent Source Review

Date: 2026-11-26 (America/Los_Angeles)

**Verdict: PassRunnerConfigurationBindingSourceOnly**

**Reviewed implementation: hybridclr_demo@000e72941f74e52aa18bcd17553e8929acc69167.**  
**Reviewed Primary documentation/evidence packet: hybridclr_demo@e76d8a6ea83ce71b83b4a4263f6054b037088fbb.**  
**Role: independent source reviewer, separate from Primary Implementation and Local Validation.**

Companion: [complete machine evidence, method inventories and raw independent fixture logs](D5B_RUNNER_CONFIGURATION_AP4_INDEPENDENT_EVIDENCE_2026-11-26.json).

## 1. Decision and exact scope

AP4 satisfies the bounded proposal: the existing plan and profile consumers read immutable bytes from **one freshly verified AP2 snapshot and the same AP3-initialized private context**, with their original blob checks enabled. The deliberate AP3 private-context refactor is accepted as part of this AP4 review. It was compared directly with the accepted predecessor; the earlier AP3 verdict was not treated as approval of changed helper bytes.

No material in-scope source, identity, reporting, regression or evidence defect was established. **Blocking findings: none. ReturnRequired is not assigned.** This decision accepts fixed configuration-consumer binding in the reviewed source. It does not establish broader runtime configuration binding, executable admission, complete executable closure, continuous or exclusive custody, current Mac state, Local authorization, native/Unity/Player qualification, Q, or a Human Review Gate transition.

The successful observation can truthfully set **fixedConfigurationConsumerReadsBound=true** and **configurationConsumersValidated=true** for its designated two consumers. The broader runtimeConfigurationReadsBound and futureRuntimeConfigurationReadsBound fields correctly remain false. Candidate module initialization and the two consumers/their selected pure helpers execute Python; describing this phase as “no candidate code executes” would be incorrect.

R5 **PassDryAdmissionSourceOnly**, AP1 R2 **PassActivationPublicationProposalOnly**, D5B-AP1-IR-01 **ClosedInCorrectedSource**, AP2 **PassRunnerArtifactClosureSourceOnly**, and the predecessor AP3 **PassRunnerImportBootstrapSourceOnly** remain preserved within their original scopes. This report adds no execution authority to any of them. See the [accepted AP3 independent report](D5B_RUNNER_IMPORTS_AP3_INDEPENDENT_REVIEW_2026-11-26.md) and the unchanged earlier records linked from the project status.

## 2. Review basis, identity and publication distinction

The review began with the committed README and WEB_TO_LOCAL checkpoint. It then examined the [AP4 request](D5B_RUNNER_CONFIGURATION_AP4_INDEPENDENT_REVIEW_REQUEST_2026-11-26.md), [design](D5B_RUNNER_CONFIGURATION_AP4_DESIGN_2026-11-26.md), [Primary report](D5B_RUNNER_CONFIGURATION_AP4_PRIMARY_2026-11-26.md), [Primary machine evidence](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json), exact implementation/test/workflow content, the accepted AP3 implementation, and fresh GitHub Actions metadata and decoded raw logs. Repository access and publication use the GitHub Connector. No historical Mac path was inspected.

| Role | Commit | Git tree | Sole parent |
| --- | --- | --- | --- |
| Accepted AP3 review/publication baseline | 77fe1c174eb44c2d14a26cc9b057671541efe2a3 | 760b4d4324840ad1f0c2fb83ee51d221c1dfb296 | 246aedcd9e3aa9d09dd1bad2aba1a00864c94416 |
| Exact AP4 CI-tested source | 000e72941f74e52aa18bcd17553e8929acc69167 | 4ddb8a5391d9d85c0d0a0609a8774dd117ecc569 | 77fe1c174eb44c2d14a26cc9b057671541efe2a3 |
| Subsequent Primary documentation/evidence packet | e76d8a6ea83ce71b83b4a4263f6054b037088fbb | 41f046d683041c065627b8f20d52fa779e92ca10 | 000e72941f74e52aa18bcd17553e8929acc69167 |
| This independent publication | Git commit containing this report and its companion evidence | Its enclosing Git tree | e76d8a6ea83ce71b83b4a4263f6054b037088fbb |

Fresh comparisons establish one commit and **five changed paths** from the accepted baseline to the tested source, followed by one commit and **eight documentation/evidence paths** from source to the Primary packet. The five increment files have identical bytes at source and packet. The later documentation HEAD is not relabeled as the CI checkout. The independent publication is also a documentation change, distinct from both.

| AP4 increment file | Exact Git blob at source and packet |
| --- | --- |
| [d5b_runner_imports.py](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py) | 22ad93598131a59b2d5c46174a45187aede848a6 |
| [d5b_runner_configuration.py](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py) | 5263742017950a28bd9750eeeaefe50df4f4fa49 |
| [test_d5b_runner_configuration.py](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py) | 595ba10093825d4d1c3940587ede8aa66bc6ac83 |
| [r03-b2-d5b-local-admission-source-host.yml](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/.github/workflows/r03-b2-d5b-local-admission-source-host.yml) | 5af2c86af0a6567d80d3c79e0cb7e87483329891 |
| [D5B_RUNNER_CONFIGURATION_AP4_DESIGN_2026-11-26.md](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CONFIGURATION_AP4_DESIGN_2026-11-26.md) | 48a3aca3ba787464e0bd9833b221b3b26a74a09b |

The machine evidence includes byte counts, SHA-256 hashes, complete method inventories, commit parents, comparison paths and Connector identities. The independent reviewer recomputed source blob identities before using downloaded files. Review used static source/AST analysis, separate source-focused subreviews, and an additional run of the existing AP3/AP4 synthetic source-host fixtures. No implementation or test was edited.

## 3. Helper identities and AP3 refactor

AP4 authenticates its adjacent AP3 helper bytes against **22ad93598131a59b2d5c46174a45187aede848a6** before compiling those same bytes. The accepted AP3 predecessor is **2bff794380f77b61dbbd84058fcba94d5ee4d9d2**. AP3 retains AP2 verifier identity **2535bc14c31f1ff2d73fdb8c7be1d7dab605d990**; AP2 retains AP1 identity **ecf36a7a51f1750c6e8425ee79e9ac8938102b54**. The input closure is exact immutable bounded bytes checked against an external full blob identity, and actual isolated/no-site/no-bytecode interpreter flags are required before helper use. This remains dependent on the reviewed companion source and a trusted process; the pin is not an authorization envelope. [AP4 authentication and helper lifetime](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L35-L132).

The complete AP3 diff is a private return-shape refactor. It adds _InitializedSnapshot(files, modules, observation), moves the existing initializer body to _initialize_snapshot_context, and returns that private context after constructing the original observation. The four-argument _initialize_snapshot remains and returns the context's observation dictionary. Inert AST comparison reconstructed precisely this transformation from the predecessor and matched the changed initializer. Every other original top-level AP3 AST is unchanged. The complete textual diff and comparison facts are embedded in the machine evidence. [Refactored initializer and compatibility wrapper](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L226-L296).

The public AP3 observer continues to use its compatibility wrapper, returns serialized observation data and invokes no candidate consumer or entry point. The unchanged twenty-method AP3 suite passed on the Primary host, focused CI and the independent source-host rerun. The new helper bytes are accepted here for the specified refactor and AP4 integration; the earlier predecessor review is neither rewritten nor extended to an unrestricted new runtime.

The fixed private initialization still compiles captured preflight, writer and wrapper bytes and initializes them in that order. Its 23 direct import requests consist of 19 trusted preloaded standard-library references, two requests to one shared private sys facade, and two private project bindings. The preflight and writer share that facade and its private path list; candidate names do not select ambient candidate cache entries. This is fixed import selection, not standard-library attestation or arbitrary Python isolation. [Initializer and routing](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py#L163-L296).

## 4. One fresh context and original consumers

The public observer has one fresh _verified_snapshot call, one _initialize_snapshot_context call and one _consume_configuration call using that returned context. It does not call the public AP3 observer and then build a second graph. Callers supply only raw closure bytes and the expected closure blob; no prior result, context, module bundle, import callback or execution mode can substitute for fresh verification. [Public control flow](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L310-L360).

Within that context, AP4 checks writer.source identity, both consumer functions' globals, captured artifact path/type/bounds/blob consistency, and the original PLAN_BLOB/PROFILE_BLOB constants. The exact production writer, preflight, plan and profile source bytes remain preserved. AP1's permitted candidate writer alteration is the checked proposal-envelope literal; it does not replace either consumer body.

Only two private globals are deliberately adapted: writer.PLAN and preflight.PROFILE. AP4 calls the original **writer.read_plan(verify_blob=True)**, obtains profile bytes from the captured view, and calls the original **preflight.checked_profile(profile_raw, check_blob=True)**. read_plan does not itself call checked_profile. No alternate parser is substituted, no candidate function is replaced, and AP4 changes no candidate approval constant. [Bindings and actual calls](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L162-L214).

The original plan consumer checks the exact plan hash and the existing closed schema, pins, target, custody, producer-coverage and authorization policy. The original profile consumer checks its exact hash and existing source-manifest, history, target, evidence and closed-authority policy. Their selected Python helper paths are writer need/git_blob/parse_json and preflight require/git_blob/read_object/strict_pairs, plus the plan cell-name comprehension. None of these paths invokes admission, preview, source inspection, a candidate main, wrapper main, a build or a receipt producer. [Original plan consumer](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py#L120-L184); [original profile consumer](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py#L103-L197).

The operation journal must match these actual adapter calls:

| Order | Artifact | Actual operation | Meaning |
| --- | --- | --- | --- |
| 1 | Captured plan | is_file() | True for the verified captured artifact |
| 2 | Captured plan | is_symlink() | False for the verified captured artifact |
| 3 | Captured plan | read_bytes() | The captured immutable plan bytes |
| 4 | Captured profile | read_bytes() | The captured immutable profile bytes |

The adapter exposes no file opening, path resolution, __fspath__, writable-file protocol or dynamic fallback. The metadata scope is **CapturedArtifactMetadata_NotCurrentPathState**. AP4 verifies the operation sequence and continued identity of the two bound globals after consumption. Its private frozen record does not make the operation list, module dictionaries or Python internals a hostile-process sandbox. [Captured views](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L135-L170).

## 5. Truthful stages, partial failure and public results

Before binding the configuration globals or calling the consumers, AP4 canonicalizes and reparses the earlier import observation. The outer AP4 report labels the frozen record **AP3BeforeConfigurationBindingAndConsumerCallsOnly**. Within that frozen AP3 record, **AP2BeforeCandidateModuleInitializationOnly** identifies the scope of the nested AP2 observation. AP3's earlier false candidate-function fields therefore remain statements about the earlier phase. The outer AP4 fields derive candidate-function invocation from its current attempt list. Success does not retroactively turn AP2's pre-initialization checkout observation into a post-consumption custody claim. [Stage freeze and later consumption](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L327-L353).

Attempts and completions are recorded separately. Plan completion and parsed values survive a later ordinary failure. The profile argument is read **before** adding checked_profile to the attempted list: a read interruption cannot falsely claim entry into the validator. Both success booleans remain false on rejection even when some useful work completed. The following interpretations were checked against source and regression assertions:

| Interruption point | Attempted consumers | Completed consumers | Retained meaning |
| --- | --- | --- | --- |
| Invalid public input or helper drift | None | None | No candidate consumer progress |
| Before consumption after initialization | None | None | Earlier import observation can exist; no consumer invocation claimed |
| Plan hash validation failure | Plan | None | Three plan operations can be recorded; no parsed plan success |
| Profile-byte acquisition failure | Plan | Plan | Plan values retained; profile body not entered |
| Profile hash validation failure | Plan and profile | Plan | Four reads/metadata operations recorded; profile validation failed |

Temporary trusted-helper registration is separate from candidate module installation. Owned helper entries are removed through finally on covered ordinary paths, with identity checked before removal. Real sys.path object identity and contents, and the three canonical candidate cache slots, are compared with their earlier state. A mismatch causes rejection and is reported; these checks do not promise restoration of arbitrary external mutations or global sys.modules immutability.

Successful public results contain frozen canonical JSON bytes, and report access returns a fresh decoded copy. Rejections likewise retain serialized report bytes and return copied presentations. No module, function, adapter or reusable context is deliberately returned in the report payload. This is a narrow API/data property, not a claim that private Python state or exception tracebacks are inaccessible to arbitrary code in the trusted process.

Structured rejection covers ordinary **Exception**. It does not promise reliable JSON after BaseException, abrupt termination, resource exhaustion, serialization failure or output failure. Missing/unsupported CLI arguments retain argparse's exit-2 stderr diagnostics and empty stdout. AP3's compilation list remains a whole-batch completion record, not an incremental per-compilation journal. These are documented contract limits rather than omitted success guarantees. [Reports, exception path and CLI](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py#L246-L382).

## 6. Exact AP4 test inventory and evidential reach

The exact test source declares **18 direct AP4 methods**. Module-qualified fixture reuse contributes setup/helpers, not inherited AP2/AP3 methods that would inflate the count. The full 94 R5, 22 AP1 R2, 25 AP2, 20 AP3 and 18 AP4 class.method inventories were compared with both raw qualification transcripts; every one of the 179 entries matched in order and completed successfully.

| AP4 method | Exact method in reviewed source | What it establishes and relevant limit |
| --- | --- | --- |
| 01 | [test_01_actual_consumers_keep_private_function_identity_and_enabled_checks](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L149) | Profiles the actual original consumers and their globals; checks both enabled hash-check arguments and the exact captured bytes entering the hash helpers. Only PLAN and PROFILE change in the private modules. |
| 02 | [test_02_each_public_call_uses_one_fresh_snapshot_and_initialization](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L221) | Observes one fresh snapshot, one initialization and one consumption per public call; repeated calls use distinct fresh helpers, modules and captured byte objects. No public-AP3-observe-then-reinitialize shortcut. |
| 03 | [test_03_report_matches_four_actual_captured_file_operations](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L277) | Wraps actual adapter methods and compares the four calls, ordering, returned values and byte identities with the report. |
| 04 | [test_04_actual_candidate_call_graph_and_consumption_use_no_io](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L319) | Profiles the two roots and reviewed pure-helper call graph; guards content, metadata, path-protocol and process I/O during consumption. It does not guard the entire AP2 verification/import phase. |
| 05 | [test_05_configuration_pathname_changes_after_capture_use_captured_bytes](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L428) | Actually replaces both configuration pathnames after capture, then checks that the original captured bytes are consumed. It does not enumerate every deletion, link or race variation. |
| 06 | [test_06_invalid_public_inputs_reject_before_helper_code](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L457) | Rejects malformed pins, wrong/mutable/subclass bytes, changed bytes and oversized inputs before helper/candidate progress. |
| 07 | [test_07_pinned_helper_drift_rejects_before_compilation](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L479) | Returns an inert changed helper through the read seam and proves rejection before compilation. This is a read-seam check, not a physical helper-file replacement fixture. |
| 08 | [test_08_private_captured_records_require_consistent_immutable_bytes](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L501) | Checks private record consistency for both artifacts, including exact bytes, path, bounds and blob. It does not independently confer AP2 provenance on caller-made records. |
| 09 | [test_09_private_adapters_are_narrow_frozen_snapshot_views](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L529) | Checks narrow frozen adapters, exact bytes, absent file/path fallback and ordinary assignment rejection. Python-private objects are not an adversarial sandbox. |
| 10 | [test_10_private_binding_and_blob_mismatches_reject_before_consumer_calls](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L557) | Rejects wrong project/function bindings and artifact constants before consumer attempts, including self-consistent changed record bytes that disagree with the original constant. |
| 11 | [test_11_real_consumers_reject_changed_read_bytes_with_truthful_progress](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L587) | Benign appended newlines reach the real consumer hash checks; plan/profile failures retain distinct attempted/completed lists and partial values. This is not exhaustive schema rejection coverage. |
| 12 | [test_12_profile_read_interruption_does_not_claim_profile_invocation](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L618) | Interrupts profile-byte acquisition and profiles actual calls: plan completion survives and checked_profile is neither entered nor reported attempted. |
| 13 | [test_13_earlier_reports_remain_frozen_preconsumer_observations](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L653) | Mutates later private observation/progress data and verifies the previously serialized AP3/AP2 reports remain unchanged with their earlier-stage scopes. |
| 14 | [test_14_private_helper_registrations_are_removed_for_all_outcomes](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L686) | Covers four enumerated ordinary outcomes: success, AP3 compile interruption, AP2 rejection and consumer-boundary interruption. It does not prove cleanup for every possible failure. |
| 15 | [test_15_public_observations_are_immutable_json_with_a_narrow_signature](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L741) | Checks the two-argument API, frozen canonical success bytes, copied success/rejection presentations and rejection of context/module/bundle/mode keywords. |
| 16 | [test_16_real_isolated_cli_preserves_checkout_and_creates_no_output](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L778) | Runs the real isolated CLI in a temporary Git fixture with inert ambient import files; checks refs, index, tracked bytes, clean status, protected outputs and no ambient bytecode. |
| 17 | [test_17_cli_requires_all_three_real_interpreter_flags](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L803) | Removes each required real interpreter flag separately and checks rejection before candidate progress. |
| 18 | [test_18_cli_requires_both_arguments_and_rejects_execution_options](https://github.com/night-outlook/hybridclr_demo/blob/000e72941f74e52aa18bcd17553e8929acc69167/Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py#L815) | Checks wrong pin, missing required arguments and unsupported execution options; distinguishes structured rejection from argparse diagnostics. |

The independent review also considered the adjacent counterexamples without creating new implementation or adversarial fixtures. A later pathname replacement does not invalidate use of already captured bytes, but it prevents a current-path/custody interpretation. A self-consistent caller-made private record is not independent provenance; the public flow still requires the authenticated fresh snapshot. A caller-created serialized observation is not approval or a verification shortcut. A changed ambient or standard-library object outside the fixed trusted-process assumptions is not covered by the isolation flags. A late ordinary failure must reject overall while retaining completed stages; it cannot be reported as full validation.

These considerations did not expose a contradiction in the bounded claim. The tests support the named operations and covered cases; their titles and passing counts are not treated as exhaustive proof of all races, exceptions, schemas or runtime integrations.

## 7. Raw host/CI evidence and independent rerun

Fresh Connector reads of [Actions run 45803071282](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282), **attempt 1**, and [job 139851042426](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282/job/139851042426) establish completed/success at **000e72941f74e52aa18bcd17553e8929acc69167**. The attempt jobs response contains **one job**; all **twelve returned steps** succeeded. Step numbers include post-action numbering gaps and are not mistaken for twelve contiguous integers. The actual checkout log prints the same source SHA.

The ordinary run endpoint reports created_at 2026-11-26T10:37:33Z and updated_at **10:38:09Z**, matching the Primary packet. The attempt-specific endpoint returns updated_at **10:38:10Z**. These endpoint-specific values are recorded separately; the difference is not a Primary error. Both identify the same successful source, run and attempt.

| Suite | Exact methods | Primary host footer | Focused CI footer | Independent reviewer fixture run |
| --- | ---: | --- | --- | --- |
| R5 | 94 | OK; 0.153s | OK; 0.186s | Raw evidence/source inventory reviewed; not rerun |
| AP1 R2 | 22 | OK; 10.100s | OK; 4.107s | Raw evidence/source inventory reviewed; not rerun |
| AP2 | 25 | OK; 14.532s | OK; 6.656s | Raw evidence/source inventory reviewed; not rerun |
| AP3 | 20 | OK; 8.752s | OK; 4.202s | OK; 8.821s; exit 0 |
| AP4 | 18 | OK; 8.725s | OK; 4.140s | OK; 9.620s; exit 0 |
| Total | 179 | Five successful suites | Five successful suites | 38 methods across two successful suites |

These are unittest footer durations, not job wall times. The Primary host archive records five successful suite exits, then the separate expected exit-2 denial control. The recorded host interval is 2026-11-26T10:34:00.186076+00:00 through 10:34:43.600855+00:00. Its Python is 3.12.14, fixture Git /usr/local/bin/git 2.56.1 and auditor Git /bin/git 2.47.3 on Linux 6.18.57 x86_64/glibc2.41. CI requests ubuntu-24.04/Python 3.11 and actually records Python 3.11.18, fixture Git /usr/bin/git 2.56.1 and auditor Git /bin/git 2.56.1. The actual-consumer call-graph assertions cover the Python 3.11 comprehension frame and Python 3.12 inlined behavior in those runs.

The Primary host transcript and recorded source identities are internally consistent with the committed source. That establishes a documentary association; it does not independently attest the original host process, original worktree or historical physical machine. The fresh CI checkout record provides the separate exact-commit CI association.

| Raw record | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| [Primary host archive](D5B_RUNNER_CONFIGURATION_AP4_SOURCE_HOST_2026-11-26.log) | 31,323 | a39479730cd312f9aa7195a8d0aad8b2c15c59facd1452ea9b688ac79cf56331 | 0ffcfaecf225e7e4598036771c9007328af64719 |
| [CI archive and freshly fetched decoded text](D5B_RUNNER_CONFIGURATION_AP4_CI_45803071282_JOB_139851042426.log) | 60,972 | 28865ccb94d9da06d16d9c6400e46694eb9e3da60d93f7209cfb81f2ceb028cd | 5c54ed3f15e5745d7dcac26669da81438c7d2073 |
| Independent AP3 fixture log, embedded in companion evidence | 3,619 | ef650bb6dabe78b52c2ab5a8e03f3978b3a79021cd951eebae0260231bc644ae | 8f4cf6ee76c7e7ebb28c08268f4b84529b538a06 |
| Independent AP4 fixture log, embedded in companion evidence | 3,365 | cf305dad744fcafc9475250dbfb72ba10e8549cf853c98203cb5a7034260d268 | 2ad52b27fb978360a082057794c5fc97e26f3f5d |

The fresh decoded CI text, encoded as UTF-8, equals its committed archive byte for byte, including the leading BOM. This is not an attestation of the original download ZIP/archive representation. The first artifact page is empty; no artifact archive is used as evidence. The workflow contains six Bash run blocks and no upload-artifact action.

The historical host and CI closed-wrapper controls report **NotAuthorized**, **WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION**, **outputCreated=false** and **retryAllowed=false**. Host exit 2 and absent envelope are explicit recorded observations. CI exit 2 and absence are supported by the successful step's explicit shell assertions, alongside the actual denial JSON. These are negative controls; they are not successful Local admission.

The independent rerun used a separate Connector-derived scratch source copy, with exact Git blob verification for all **16** selected source/test/configuration/workflow files before and after. Only the existing AP3 and AP4 synthetic fixture suites ran, under actual **-I -S -B**. They use temporary Git objects and synthetic locations; the reviewer did not invoke Local admission or the separate production wrapper gate. Start/end were 2026-11-26T12:11:52.059966+00:00 and 12:12:10.841531+00:00. All sixteen source files remained exact. The companion evidence embeds complete raw logs, commands, method identities, environment and before/after hashes. The independent environment used Python 3.12.14, fixture Git 2.56.1 and auditor Git 2.47.3.

## 8. Twelve-file preservation and protected records

Fresh remote identities at the accepted baseline, tested source and Primary packet agree for each protected file below. Full retrieved source bytes independently reconstruct to the expected blobs and SHA-256 values. The changed AP3 **helper** is deliberately outside this preservation roster; the retained AP3 **test** is inside it. CI's exact checkout is evidence of source identity, not a separate twelve-file hash audit in its transcript.

Paths in this table are relative to Tools/AssemblyShadow/R03IR/.

| Protected file | Preserved Git blob |
| --- | --- |
| D5Local/run_d5_local.py | 519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39 |
| D5Local/d5b_local_admission.py | 99746fe64976da313cbd0e1625f0fcc5a67bca62 |
| D5Local/test_d5b_local_admission.py | 06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c |
| D5Local/d5b_local_admission_plan_v1.json | 5c0ab7a6d788ebd5adf57f1fddc567ba700632e9 |
| D5Admission/d5b_rr5_source_preflight.py | 81e7c3a2eaccb77bff2515c91b173558e4eeba2f |
| D5Admission/d5b_rr5_source_preflight_v1.json | 9956ea49656dc8337f9ab177c40faf29ea20c397 |
| D5Admission/d5b_custody_authority.py | 185c1bd6603a8c43e4222d30ed8bb057ab94824a |
| D5Local/d5b_activation_publication.py | ecf36a7a51f1750c6e8425ee79e9ac8938102b54 |
| D5Local/test_d5b_activation_publication.py | ef0b562951afd5deb49528e5b8acf013a015eadb |
| D5Local/d5b_runner_closure.py | 2535bc14c31f1ff2d73fdb8c7be1d7dab605d990 |
| D5Local/test_d5b_runner_closure.py | ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976 |
| D5Local/test_d5b_runner_imports.py | 86840e72285b99ea885469390b66c42d1f3d681f |

Local-owned records remain unchanged across the same three commits:

| Record | Git blob | Full source bytes |
| --- | --- | ---: |
| Docs/AssemblyShadow/Handoff/LOCAL_VALIDATION.md | cbc4141a1f79c16c920d1723a81c5507b87b7e5f | 1,265,383 |
| Docs/AssemblyShadow/Handoff/RETURN_TO_WEB.md | 411948c65d0ab04a36ed0f43a8944b6c8291ed30 | 696,171 |

For the large LOCAL_VALIDATION file, the contents response did not supply usable full content. A Git-blob read supplied the full text and its recomputed identity matched; an empty response was not hashed as the file. These preserved historical records are not evidence of current physical Mac state.

Primary-owned **WEB_TO_LOCAL.md**, blob **38c841e24f88491ed6d17cd8fbba339cf130b57d**, is preserved by this independent publication. Its closed checkpoint is authoritative for the execution boundary. AP4-pending labels in the older Primary packet, unchanged checkpoint and implementation report are historical or deliberately non-self-approving source fields; they do not override this separate external source verdict or open executable admission.

## 9. Four-repository observations and closed authority

Fresh feature-ref reads at **2026-11-26 12:14:33 UTC** returned the following input heads. Branch for every row: codex/assembly-shadow-r01b-h1. The demonstration repository alone receives this separate documentation publication; final publication identity and remote readback are reported with delivery.

| Repository | Observed input HEAD | Historical candidate path | Current physical state |
| --- | --- | --- | --- |
| night-outlook/hybridclr_demo | e76d8a6ea83ce71b83b4a4263f6054b037088fbb | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Unverified |
| night-outlook/hybridclr | c3c232023724cbad565b85e9b2c3beea8ce2789a | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | Unverified |
| night-outlook/hybridclr_unity | 948c0e3b4f8891481301770115e8ba4945eea6de | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | Unverified |
| night-outlook/il2cpp_plus | 1268dd417ffe9090fcd9ea2d49542c97ed3cccb3 | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | Unverified |

These Connector observations serve review identity and publication bookkeeping. They do not change AP4's runtime liveRemoteRefsVerified=false, verify source/live-ref admission, or establish current filesystem state at any historical path.

| Boundary | Preserved state |
| --- | --- |
| Production APPROVED_EXECUTION_ENVELOPE_BLOB | None |
| Production APPROVED_LOCAL_HANDOFF_BLOB | None |
| Candidate proposal-envelope literal | Checked against its proposal; unchanged by AP4; not approval and not assumed None |
| Public approvedEnvelopeGitBlob / executionAuthorityVerified | null / false |
| WEB_TO_LOCAL | CLOSED_NO_LOCAL_EXECUTION |
| D5BLocalExecution / D5LocalValidation / explicit user Local approval | NotAuthorized |
| R03Accepted / H2Passed / ReadyForHumanReviewGate | false / false / false |
| allowNativeBuild / allowPlayerLaunch | false / false |
| Current real Unity/native/Player work | NotRun |
| Real Player coverage | 18 NoCoverage; 0 passed |
| Q, production activation and approval repinning | Not authorized |
| Runtime/future configuration, executable closure, standard-library identity, custody and current Mac inputs | Not established |

The production approval constants were checked in the preserved source, not inferred from the runtime candidate. The candidate's proposal literal is a different concept and can be non-null without granting authority.

## 10. Publication disposition and stop

This decision is **PassRunnerConfigurationBindingSourceOnly** for exact source **000e72941f74e52aa18bcd17553e8929acc69167**, including its AP3 private-context refactor and the two designated original consumers. The reviewed evidence is sufficient for that claim; it does not justify a broader acceptance label.

Publication is limited to this report, its independent machine evidence, and new current-verdict sections in README and Plan/CURRENT_STATUS. Existing status history is retained byte for byte beneath those sections. Implementation, tests, workflow, Primary reports/logs/request, WEB_TO_LOCAL, Local-owned records and sibling repositories are preserved. No approval constant, approval ref, execution handoff or later milestone is changed.

The publication uses the observed documentation HEAD as its parent and an expected-head non-forced ref update. Required completion is remote readback of the publication and preserved identities, followed by stopping. No Local integration, admission, Unity/native build, Player work, Q work, production activation, Human Review Gate approval or later milestone follows from this review.
