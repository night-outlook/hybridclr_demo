# D5-B Runner Configuration AP4 Primary Report

Date: 2026-11-26 (America/Los_Angeles)

Status: Primary source-only implementation and qualification report. The host and GitHub Actions each completed 179 test methods successfully. Independent AP4 review remains `Pending`.

Accepted AP3 publication/review: `77fe1c174eb44c2d14a26cc9b057671541efe2a3`.

Accepted AP3 implementation source: `bcf3a9470a12758b210738476d18f80bf60d2eaf`.

AP4 source commit: `000e72941f74e52aa18bcd17553e8929acc69167`.

AP4 source tree: `4ddb8a5391d9d85c0d0a0609a8774dd117ecc569`.

Requested independent verdict: `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired`.

## 1. Implemented source contract

The source adds `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py` and its public API:

```python
observe_runner_configuration(
    raw: bytes,
    expected_closure_blob: str,
) -> ConfigurationObservation
```

The API accepts closure bytes and their exact external Git blob. It requires actual trusted-interpreter `-I -S -B` flags, checks immutable bounded bytes against the expected blob, authenticates the installed AP3 helper, obtains a fresh AP2 snapshot, and initializes the reviewed private module graph once. It accepts no caller-supplied context, modules, bundle, callback, execution mode, or prior report as a substitute for that fresh verification.

The implemented success result is `RunnerConfigurationConsumersObserved_NoExecutionAuthority`. The implemented rejection result is `RunnerConfigurationConsumersRejected_NoExecutionAuthority`. The qualification suites exercise successful bounded observations and closed rejection paths; their results do not constitute executable admission.

On the success path, `fixedConfigurationConsumerReadsBound=true` and `configurationConsumersValidated=true` describe only the designated plan/profile consumers in the current observation. The scope string is `read_plan_and_checked_profile_from_one_verified_snapshot`. Broader runtime, future runtime, executable, custody, source-data, machine, and authority claims remain false.

The public result is a frozen `ConfigurationObservation` containing canonical JSON bytes. Its `report` property returns fresh JSON data. It exposes no modules, functions, adapters, or private context.

## 2. Intentional AP3 private refactor and helper pin

The single deliberate baseline implementation change is in `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py`:

| Identity | Git blob |
| --- | --- |
| Accepted AP3 predecessor | `2bff794380f77b61dbbd84058fcba94d5ee4d9d2` |
| Refactored AP3 helper pinned by AP4 | `22ad93598131a59b2d5c46174a45187aede848a6` |

The helper introduces `_InitializedSnapshot(NamedTuple)` with `files`, `modules`, and `observation` fields. `_initialize_snapshot_context` contains the existing validated initializer and returns that context. `_initialize_snapshot` remains the compatibility wrapper returning `.observation` through its existing four-argument interface. The public `observe_runner_imports` API, import-only behavior, CLI contract, and retained AP3 test source remain preserved. The host static checks recorded preservation of the old initializer logic and other existing top-level AST, and the retained 20-method AP3 suite passed on both host and CI; see the `sourceHost` and `githubActions` sections of the [evidence JSON](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json).

AP4 authenticates the refactored helper's exact bytes before executing it. Its temporary trusted-helper registration supports the helper's initialization and is removed on the ordinary completed path. AP2 retains its existing helper identity, `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990`.

This private refactor keeps one implementation of snapshot validation, compilation order, import routing, and project-binding checks. A duplicate candidate loader would create another implementation to keep aligned solely to avoid an explicit helper identity change. The accepted predecessor identity is retained in AP4's source and success report so that the change is visible rather than presented as byte-identical AP3 code.

The prior independent `PassRunnerImportBootstrapSourceOnly` covers the accepted predecessor implementation and helper bytes. It does not independently approve helper blob `22ad93598131a59b2d5c46174a45187aede848a6`. The new private refactor and AP4 consumer integration are part of the requested independent AP4 review.

## 3. Twelve unchanged baseline files

The following twelve files preserve their exact accepted-baseline blobs from `77fe1c174eb44c2d14a26cc9b057671541efe2a3`. The evidence basis is Primary host blob checks followed by exact remote source readback and the baseline-to-source comparison. CI checked out the same source commit; no separate twelve-file hash audit is claimed from its job transcript. The preserved identities are recorded in the [evidence JSON](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json), including `sourceHost.preservation` and the `githubActions.preservationBasis` explanation.

| Baseline file | Preserved Git blob |
| --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `519e6a4a8a11e3c821adb02fe1bf9e9d5b685b39` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `99746fe64976da313cbd0e1625f0fcc5a67bca62` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py` | `06aaf4f3ef4df3cc7306fe8d83d56f35ce1e0e0c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission_plan_v1.json` | `5c0ab7a6d788ebd5adf57f1fddc567ba700632e9` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | `81e7c3a2eaccb77bff2515c91b173558e4eeba2f` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight_v1.json` | `9956ea49656dc8337f9ab177c40faf29ea20c397` |
| `Tools/AssemblyShadow/R03IR/D5Admission/d5b_custody_authority.py` | `185c1bd6603a8c43e4222d30ed8bb057ab94824a` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_activation_publication.py` | `ecf36a7a51f1750c6e8425ee79e9ac8938102b54` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py` | `ef0b562951afd5deb49528e5b8acf013a015eadb` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py` | `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py` | `ed503a5d5eeeeff07a2e5c11be38bf7aba6b5976` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py` | `86840e72285b99ea885469390b66c42d1f3d681f` |

## 4. One context, shared import graph, and actual consumers

The reused AP3 initializer compiles the captured preflight, writer, and wrapper source bytes and initializes them in that order. One private `sys` facade is shared by the candidate preflight and writer modules. Its private `path` list is distinct from the process's real `sys.path`; the writer's existing insertion changes that private list. The direct import forms total 23 requests: eight from preflight, fourteen from the writer, and one from the wrapper. Candidate dependencies select the private snapshot modules; standard-library dependencies select the trusted preloaded modules. There is no candidate finder, ambient candidate `sys.modules` selection, or source/bytecode fallback.

AP4 uses the records and module instances from this same initialized context. It checks `writer.source is preflight`, the two consumer functions' `__globals__`, and the plan/profile constants against the captured records. It records original runtime paths as metadata and then deliberately adapts only `writer.PLAN` and `preflight.PROFILE`.

The actual call sequence is:

```python
plan = writer.read_plan(verify_blob=True)
profile_raw = preflight.PROFILE.read_bytes()
profile = preflight.checked_profile(profile_raw, check_blob=True)
```

The profile read occurs before `checked_profile` is recorded as attempted, so a read failure cannot claim that the profile validator was entered. No replacement parser substitutes for these existing consumer functions. `read_plan` does not itself call `checked_profile`.

The frozen `_CapturedFile` objects return the captured immutable bytes and record this exact four-operation sequence:

| Order | Bound artifact | Adapter operation |
| --- | --- | --- |
| 1 | Plan | `is_file()` returns true for the captured artifact |
| 2 | Plan | `is_symlink()` returns false for the captured artifact |
| 3 | Plan | `read_bytes()` returns its captured bytes |
| 4 | Profile | `read_bytes()` returns its captured bytes |

The implementation checks that sequence and that the two globals still name the installed views. Metadata scope is `CapturedArtifactMetadata_NotCurrentPathState`; binding scope is `PrivateModuleGlobalsOnly`. The objects have no filesystem or path-protocol fallback. AP4 does not rewrite candidate source, replace candidate functions, alter the candidate approval constant, or patch global filesystem/standard-library operations. Frozen view fields do not make the private operation journal or module dictionaries an adversarial sandbox.

The candidate Python call scope is the two root consumers and their reviewed pure helper paths: writer `need`, `git_blob`, and `parse_json`; preflight `require`, `git_blob`, `read_object`, and `strict_pairs`, plus the plan's existing cell-name comprehension. The parser uses the existing duplicate-key and object checks. No `inspect`, candidate `main`, wrapper `main`, admission preview, source inspection, envelope admission, or receipt producer is called by this path.

## 5. Earlier-stage reports and current AP4 facts

Before adapting the globals or calling the consumers, AP4 serializes and reparses the earlier AP3 observation to freeze it. Its scope is `AP3BeforeConfigurationBindingAndConsumerCallsOnly`. The nested AP2 artifact observation retains `AP2BeforeCandidateModuleInitializationOnly`.

The earlier AP3 record correctly states `candidateFunctionsInvoked=false` and `planProfileFunctionsInvoked=false`. The outer AP4 record derives those fields from its own consumer-attempt list. A completed AP4 observation therefore reports that candidate functions did run while its earlier AP3 snapshot continues to describe the preceding import-only stage. Neither stage is relabeled as an admission or runtime-closure result.

AP4 retains separate `configurationConsumerCallsAttempted` and `configurationConsumerCallsCompleted` lists, `configurationOperations`, binding-installation progress, artifact identities, and parsed configuration values. An ordinary exception after the first consumer retains that partial progress and leaves the overall binding/validation success flags false. Real `sys.path` and the candidate module-name slots are checked against their captured process state. Temporary trusted-helper registration is reported separately; there is no claim that every `sys.modules` entry was globally unchanged.

Structured rejection covers ordinary `Exception` failures. It does not guarantee JSON after `BaseException`, including `KeyboardInterrupt` or `SystemExit`, abrupt termination, resource exhaustion, serialization failure, or failed output. Unsupported or missing CLI arguments retain argparse's exit-2 diagnostic on stderr and empty stdout. The inherited AP3 compilation-progress list describes completion of the whole compile batch; the refactor does not create a per-compilation journal. The isolated interpreter flags are preconditions, not attestation of arbitrary process history or standard-library identity.

## 6. Authority and remaining boundaries

AP3's initialized candidate writer is checked against the closure's candidate proposal-envelope literal. The fact that the production writer source contains `APPROVED_EXECUTION_ENVELOPE_BLOB=None` is not an assertion that this value remains null inside that candidate snapshot. AP4 preserves the existing candidate-literal check without changing the constant or treating it as approval.

The public `approvedEnvelopeGitBlob` remains null and `executionAuthorityVerified=false`. `independentlyReviewedConfigurationBinding` and `independentlyReviewedExecutableAdmission` remain `Pending`. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; `D5BLocalExecution`, `D5LocalValidation`, and explicit user Local approval remain `NotAuthorized`. Native and Player permission flags remain false. Unity/build/Player work remains unperformed, with zero real Player cells passed and eighteen cells without coverage. `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false. Q authority remains closed and no Q execution, completion, or acceptance is claimed.

`runtimeConfigurationReadsBound`, `futureRuntimeConfigurationReadsBound`, `runtimeImportIsolationVerified`, `runnerExecutableClosureVerified`, `standardLibraryIdentityVerified`, continuous/exclusive custody, live-remote verification, other source-data inputs, and current Mac inputs remain unverified. Captured-byte consumption can continue after a pathname changes; it does not attest the current pathname. Future admission, `inspect`/`main` integration, other configuration/input consumers, runtime imports, and any native/Unity/Player work remain deferred.

## 7. Exact source identities and qualification evidence

The source is one commit beyond accepted baseline `77fe1c174eb44c2d14a26cc9b057671541efe2a3`, with five changed files. Host qualification ran before publication in the Connector-derived source directory recorded in the host log. The five byte identities below were then read back exactly from published source commit `000e72941f74e52aa18bcd17553e8929acc69167`; this readback establishes the association between the prepublication host run and the published source bytes. GitHub Actions' actual checkout log names that same commit; the Actions receipt records tree `4ddb8a5391d9d85c0d0a0609a8774dd117ecc569`.

| Source file | Git blob | SHA-256 |
| --- | --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py` | `22ad93598131a59b2d5c46174a45187aede848a6` | `34022e6cd17af28420c165e7be80f94c56acd7846d1b782a4cf4b9acb59f981c` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py` | `5263742017950a28bd9750eeeaefe50df4f4fa49` | `96aaa7e172d94613e3a974e17187529091498e008959b1c75a318bfc10e86682` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py` | `595ba10093825d4d1c3940587ede8aa66bc6ac83` | `d38fc9d0f2e1cf0d5da52a041d9f1e552f7abd3628cf0fa17e21b64fad200798` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `5af2c86af0a6567d80d3c79e0cb7e87483329891` | `db7149caa96c6e21b2f1b5b2e66613018981dcab63b94ec0e12c3aa7ae044c7f` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CONFIGURATION_AP4_DESIGN_2026-11-26.md` | `48a3aca3ba787464e0bd9833b221b3b26a74a09b` | `9dfe4fed8dd5e5bb45eb9fe6e4f775477435e573ff5e23243d9947bf63204291` |

The [evidence JSON](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json) contains the host receipt in `sourceHost` and the Actions receipt in `githubActions`. Their actual suite footers give the following results; durations are the per-suite unittest footer durations, not workflow wall times.

| Suite | Methods per environment | Host seconds | CI seconds | Host / CI |
| --- | ---: | ---: | ---: | --- |
| R5 writer | 94 | 0.153 | 0.186 | `OK` / `OK` |
| AP1-R2 activation/publication | 22 | 10.100 | 4.107 | `OK` / `OK` |
| AP2 artifact closure | 25 | 14.532 | 6.656 | `OK` / `OK` |
| AP3 private import observation | 20 | 8.752 | 4.202 | `OK` / `OK` |
| AP4 configuration binding | 18 | 8.725 | 4.140 | `OK` / `OK` |
| Total | 179 | — | — | Five successful suites in each environment |

The host interval was `2026-11-26T10:34:00.186076+00:00` through `2026-11-26T10:34:43.600855+00:00`. All five suite processes exited 0, the source bytes remained unchanged after tests, and the static receipt records three Python AST parses, parsed workflow YAML, six checked Bash run blocks, no trailing whitespace, the AP3 helper pin match, and the intended AP3 AST preservation.

| Environment fact | Source host | GitHub Actions |
| --- | --- | --- |
| Python | `3.12.14` | `3.11.18` |
| Python executable / configured runner | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3` | Workflow runner `ubuntu-24.04` |
| Host platform observation | `Linux-6.18.57-x86_64-with-glibc2.41` | The workflow configuration supplies the runner label; no equivalent host-platform string is asserted here |
| Fixture Git | `/usr/local/bin/git`, `2.56.1` | `/usr/bin/git`, `2.56.1` |
| Auditor Git | `/bin/git`, `2.47.3` | `/bin/git`, `2.56.1` |

[GitHub Actions run 45803071282](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282), attempt 1, completed with `success` for job [139851042426](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282/job/139851042426), `future-admission-source-host`. All twelve returned steps were completed successfully. The run record was created at `2026-11-26T10:37:33Z` and updated at `2026-11-26T10:38:09Z`. Five actual `OK` footers and the AP4 method inventory match the host receipt. Other workflow metadata is not AP4 qualification evidence.

The separate closed-gate control in both environments returned `NotAuthorized` with exit 2, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, and `outputCreated=false`; the unapproved envelope pathname remained absent. That negative control is separate from the AP4 consumer path and grants no execution authority.

The 18 AP4 methods exercise actual consumer identity and enabled checks, one fresh context per public call, the four adapter operations, the bounded call graph and absence of consumption I/O, benign post-capture pathname changes, invalid public input, helper drift, malformed private records, narrow adapters, binding/blob mismatch, truthful partial progress, profile-read interruption, frozen earlier reports, ordinary-path helper cleanup, immutable JSON results, real isolated CLI behavior, required flags, and rejection of execution options. The scope remains the reviewed source and synthetic fixtures.

### Raw evidence files

| Evidence file | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| [D5B_RUNNER_CONFIGURATION_AP4_SOURCE_HOST_2026-11-26.log](D5B_RUNNER_CONFIGURATION_AP4_SOURCE_HOST_2026-11-26.log) | 31323 | `a39479730cd312f9aa7195a8d0aad8b2c15c59facd1452ea9b688ac79cf56331` | `0ffcfaecf225e7e4598036771c9007328af64719` |
| [D5B_RUNNER_CONFIGURATION_AP4_CI_45803071282_JOB_139851042426.log](D5B_RUNNER_CONFIGURATION_AP4_CI_45803071282_JOB_139851042426.log) | 60972 | `28865ccb94d9da06d16d9c6400e46694eb9e3da60d93f7209cfb81f2ceb028cd` | `5c54ed3f15e5745d7dcac26669da81438c7d2073` |

The CI log is the exact UTF-8 encoding of the Connector-decoded job-log text, including its leading BOM. It is not an attestation of original ZIP/archive bytes. The Connector's first artifact page returned zero uploaded artifacts; the qualification evidence comes from the recorded job transcript and receipts rather than an uploaded-artifact claim.

## 8. Practical source review commands

In a repository containing the source commit, these read-only identity commands select the reviewed source and its baseline comparison:

```bash
git show --no-patch --format=fuller 000e72941f74e52aa18bcd17553e8929acc69167
git rev-parse '000e72941f74e52aa18bcd17553e8929acc69167^{tree}'
git diff --stat 77fe1c174eb44c2d14a26cc9b057671541efe2a3 000e72941f74e52aa18bcd17553e8929acc69167
```

From the root of a trusted source copy whose contents match that commit, the recorded suite entry points are:

```bash
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py -v
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py -v
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py -v
python3 -I -S -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py -v
python3 -I -S -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py -v
```

The environment and command records above distinguish the two qualified runs. These commands describe source-only fixture qualification and do not authorize admission or Local/native/Unity/Player/Q execution.

## 9. Independent review disposition

Independent AP4 remains `Pending`. The companion request asks for `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired` against source `000e72941f74e52aa18bcd17553e8929acc69167` and the linked evidence. Primary's internal peer review found no source blocker; the ordinary-Exception/argparse clarification was incorporated before qualification. That internal review is not independent approval, and the prior AP3 verdict covers the predecessor only.

This Primary report issues neither independent verdict and cannot authorize Local/native/Unity/Player/Q work. A later source-only verdict would still leave future executable integration and authority closed.

## 10. Four-repository state and exact paths

| Repository | Branch | Source review commit | Historical candidate path — physical state Unverified |
|---|---|---|---|
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `000e72941f74e52aa18bcd17553e8929acc69167` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

The table is the source-review tuple. The demonstration repository initially resolved to accepted AP3 publication `77fe1c174eb44c2d14a26cc9b057671541efe2a3`; the other three initial heads equal their listed source-review commits. All four identities and feature refs resolved through the GitHub Connector, and its repository metadata reported pull/push permission. Only `night-outlook/hybridclr_demo` changed in this cycle. No physical Mac checkout was inspected. Primary's source snapshot is `/workspace/scratch/a6fad0908883/ap4_source`, populated from exact Connector file reads.

Source/package/overlay/native/build pins remain preserved reviewed or historical inputs; no package regeneration, native output or Unity build is qualified here. The latest Local-owned records still describe historical Native B1 oneuse-12 focused results, not current D5/AP4 qualification. `Handoff/LOCAL_VALIDATION.md` retains blob `cbc4141a1f79c16c920d1723a81c5507b87b7e5f`; `Handoff/RETURN_TO_WEB.md` retains blob `411948c65d0ab04a36ed0f43a8944b6c8291ed30`. Their ownership remains Local, and neither file is modified.

## 11. Connector transport proof

The existing same-conversation disposable branch `codex/assembly-shadow-smoke-20261125-primary-r5-a6fad0` is retained in all four repositories. Fresh read-only requests verified each exact branch target and its commit object. No new smoke commit was needed for this already-proven transport.

| Repository | Original smoke base | Smoke commit | Current readback result |
|---|---|---|---|
| `night-outlook/hybridclr_demo` | `83ceb2ba9868d96bd35628908919978e16cc5d2f` | `a0c30160de9697d42223310bece86cd96c796d93` | Exact ref and commit object read back |
| `night-outlook/hybridclr` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `c4197a1c19353ef4c6bf9f670bbb234dc8afc086` | Exact ref and commit object read back |
| `night-outlook/hybridclr_unity` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `9a7da758fcad50f81708202d0a5ad30aa2f64ee1` | Exact ref and commit object read back |
| `night-outlook/il2cpp_plus` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `ecf7c731b3bd2f20719b9363cf897ed6cf7304d8` | Exact ref and commit object read back |

Eight readbacks matched: four refs and four commit objects. The Connector exposes no delete-ref operation in this session, so these disposable refs remain recorded explicitly. No credential or authentication details are included. This proves the operational Connector write/readback path and supplies no product acceptance or Local execution authority.

## 12. Publication identity and next-agent checkpoint

The source publication used GitHub Connector `create_tree → create_commit → update_ref`, with expected old head `77fe1c174eb44c2d14a26cc9b057671541efe2a3` and `force=false`. The resulting source is `000e72941f74e52aa18bcd17553e8929acc69167`, tree `4ddb8a5391d9d85c0d0a0609a8774dd117ecc569`. Exact contents of all five changed files and all twelve preserved blobs were read back; the baseline comparison is one commit with five changed paths.

The commit containing this report is the documentation/evidence-only child of that source. It contains the three canonical checkpoint prefixes, this report, the independent review request, machine evidence and two raw logs. Its actual latest pushed commit must be resolved from the feature ref and reported separately in the final handoff. This avoids embedding an impossible self-referential commit identity or attributing the source workflow to a later documentation commit. The final publication gate is exact readback of the eight documentation/evidence files, a documentation-only comparison, unchanged source and Local-owned records, and fresh four-repository remote refs.

Canonical checkpoint locations are `Docs/AssemblyShadow/README.md`, `Docs/AssemblyShadow/Plan/CURRENT_STATUS.md` and Primary-owned `Docs/AssemblyShadow/Handoff/WEB_TO_LOCAL.md`. The new prefixes preserve the previous contents as historical suffixes. The accepted AP3 record supersedes older AP3-pending labels; AP4 independent review remains Pending.

Read next: README, the current WEB_TO_LOCAL checkpoint, accepted AP3 independent report, AP4 design, this Primary report and exact machine/raw evidence, AP4 independent request, then the pinned source. Record the tested source, containing publication, four remote refs, source/log identities, factual checks and either `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired` in a separate independent report/evidence beside this file. Stop after that publication/readback. A material finding returns to Primary; no Local integration, approval change or real-environment execution follows automatically.

The sole candidate is the AP4 companion observer. If a concrete finding requires removal, use a separately reviewed forward revert preserving all accepted predecessor evidence. There is no authorized Local fix, reset/clean, candidate execution output directory, native/Unity/Player action or later milestone in this checkpoint.
