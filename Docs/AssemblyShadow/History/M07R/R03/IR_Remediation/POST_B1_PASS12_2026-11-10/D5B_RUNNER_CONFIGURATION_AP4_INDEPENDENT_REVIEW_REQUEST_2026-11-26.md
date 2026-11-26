# D5-B Runner Configuration AP4 Independent Review Request

Date: 2026-11-26 (America/Los_Angeles)

Status: Source and qualification evidence assembled for independent review. The host and GitHub Actions each completed 179 test methods successfully. Independent AP4 remains `Pending`; no independent pass verdict is asserted.

Requested verdict: `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired`.

Review target: commit `000e72941f74e52aa18bcd17553e8929acc69167`, tree `4ddb8a5391d9d85c0d0a0609a8774dd117ecc569`.

Accepted AP3 publication/review: `77fe1c174eb44c2d14a26cc9b057671541efe2a3`; accepted AP3 implementation source: `bcf3a9470a12758b210738476d18f80bf60d2eaf`.

## 1. Decision requested

Review the bounded source implementation that makes the existing `read_plan` and `checked_profile` consumers use bytes from one fresh AP2-verified snapshot and the same AP3-initialized private context. Assess whether `fixedConfigurationConsumerReadsBound` accurately describes that fixed observation and whether the implementation preserves every broader closed boundary.

The requested source-only verdict does not cover admission, Local execution, a complete runtime closure, continuous custody, native compilation, Unity, Player, Q, or a human-review gate transition. If implementation, evidence, identity, reporting, or scope is inadequate, return `ReturnRequired` with concrete findings. Do not infer an independent approval from the Primary report or from the presence of success-result labels in source.

## 2. Implementation to inspect

The new source is `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py`. Its public contract is:

```python
observe_runner_configuration(
    raw: bytes,
    expected_closure_blob: str,
) -> ConfigurationObservation
```

It accepts no bundle, module, context, import callback, execution mode, or prior-verification shortcut. It checks actual `-I -S -B` flags and the immutable bounded closure bytes against an external exact blob, authenticates the installed AP3 helper, obtains a fresh AP2 snapshot, and initializes the private candidate graph once. Public outcomes contain frozen canonical JSON bytes and fresh presentation copies, not callables or contexts.

The intentional baseline change is the AP3 private refactor:

| Item | Identity or contract |
| --- | --- |
| File | `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py` |
| Accepted predecessor blob | `2bff794380f77b61dbbd84058fcba94d5ee4d9d2` |
| Refactored helper pin in AP4 | `22ad93598131a59b2d5c46174a45187aede848a6` |
| Private context | `_InitializedSnapshot(NamedTuple)` with `files`, `modules`, `observation` |
| Shared initializer | `_initialize_snapshot_context` |
| Compatibility seam | `_initialize_snapshot(closure, records, artifact_report, progress)` still returns the dictionary held in the new context's `.observation` |

Review that the original four-argument `_initialize_snapshot` still returns a dictionary, the public AP3 observer invokes no candidate function, and the public AP3/CLI/result contracts remain preserved. The refactor is selected to retain one source loader and one validation/import mechanism rather than duplicate them. The changed helper identity is intentional and matches the source identities recorded in the companion evidence. The retained AP3 suite completed 20 methods successfully on both host and CI, and the host static receipt records preservation of the initializer logic and other existing top-level AST.

The prior independent `PassRunnerImportBootstrapSourceOnly` covers the accepted predecessor implementation and helper blob `2bff794380f77b61dbbd84058fcba94d5ee4d9d2`. It does not independently approve helper blob `22ad93598131a59b2d5c46174a45187aede848a6`. Review this private refactor together with the new AP4 observer and its bounded consumer integration.

## 3. Twelve-file preservation roster

The following exact blobs remain unchanged from accepted baseline `77fe1c174eb44c2d14a26cc9b057671541efe2a3`. The preservation basis is Primary host checks plus exact remote source readback and the baseline-to-source comparison. CI checked out the same source commit; its transcript is not claimed to contain a separate twelve-file hash audit. See the [evidence JSON](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json), including `sourceHost.preservation` and `githubActions.preservationBasis`, and review this evidence distinction explicitly.

| File required unchanged | Baseline Git blob |
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

## 4. Same-context consumption and import boundary

The AP3 graph contains the captured preflight, writer, and wrapper modules, initialized in that order. Its preflight and writer use one shared private `sys` facade with a private `path` list. The fixed direct requests total 23: eight preflight, fourteen writer, and one wrapper. Review that imports still select the intended private project modules or trusted preloaded standard-library modules, with no ambient candidate lookup or bytecode fallback. The runtime report does not claim standard-library identity or sandboxing.

Within the same context, AP4 checks the project binding and both consumer functions' globals. It deliberately replaces only `writer.PLAN` and `preflight.PROFILE` with private captured-file views after AP3's original path and constant checks. The source then performs:

```python
plan = writer.read_plan(verify_blob=True)
profile_raw = preflight.PROFILE.read_bytes()
profile = preflight.checked_profile(profile_raw, check_blob=True)
```

The exact adapter operation sequence is plan `is_file`, plan `is_symlink`, plan `read_bytes`, and profile `read_bytes`. `is_file` and `is_symlink` describe the captured artifact, not current pathname state. Both reads return the verified immutable bytes, and the implementation checks the four-operation shape and continued identity of the bound globals. No filesystem or `__fspath__` fallback is provided.

Review the actual existing consumer execution rather than treating separate parsing or report text as equivalent evidence. `read_plan` does not invoke `checked_profile`. The candidate pure-helper scope is writer `need`, `git_blob`, and `parse_json`; preflight `require`, `git_blob`, `read_object`, and `strict_pairs`; plus the plan's existing cell-name comprehension. No `inspect`, candidate or wrapper `main`, admission preview, source inspection, envelope admission, or receipt production is included. Candidate source/functions and the candidate approval constant are not rewritten by AP4.

## 5. Reporting and failure questions

Verify that AP4 freezes its earlier AP3 observation before adaptation and consumer calls. That record retains `AP3BeforeConfigurationBindingAndConsumerCallsOnly`; its nested AP2 record retains `AP2BeforeCandidateModuleInitializationOnly`. The earlier AP3 record's false candidate-function fields describe that earlier stage, while the current AP4 record truthfully derives candidate-function invocation from its consumer-attempt list.

Review attempted and completed consumer lists, binding-installation progress, artifact identities, four-operation evidence, and ordinary-exception rejection records. The profile bytes are obtained before the attempt entry for `checked_profile`; a profile-read failure must not claim entry into its body. Partial plan completion must survive later ordinary failures, while the overall success flags remain false.

Structured rejection is limited to ordinary `Exception`. It does not promise JSON after `BaseException`, including `KeyboardInterrupt` or `SystemExit`, abrupt termination, resource exhaustion, serialization failure, or output failure. Argparse still handles missing or unsupported arguments with exit 2, stderr diagnostics, and empty stdout. AP3's compile-progress list records whole-batch completion, not each successful compilation. Interpreter isolation flags remain required preconditions rather than proof of arbitrary prior process history.

Temporary helper registration is distinct from candidate module installation. Verify reported cleanup on the covered ordinary paths and preservation of the real `sys.path` object/contents and candidate-name slots. Do not reinterpret those checks as a global immutability claim for all process state or as continuous custody.

## 6. Source identities and completed qualification evidence

The qualification evidence is in the `sourceHost` and `githubActions` sections of [D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json](D5B_RUNNER_CONFIGURATION_AP4_EVIDENCE_2026-11-26.json). The host ran before publication in the Connector-derived source directory recorded in its log. Exact remote readback of all five changed-file identities subsequently matched those host bytes to source commit `000e72941f74e52aa18bcd17553e8929acc69167`. CI's actual checkout log names that same source commit; its recorded tree is `4ddb8a5391d9d85c0d0a0609a8774dd117ecc569`.

| Changed source file | Exact Git blob |
| --- | --- |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py` | `22ad93598131a59b2d5c46174a45187aede848a6` |
| `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_configuration.py` | `5263742017950a28bd9750eeeaefe50df4f4fa49` |
| `Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py` | `595ba10093825d4d1c3940587ede8aa66bc6ac83` |
| `.github/workflows/r03-b2-d5b-local-admission-source-host.yml` | `5af2c86af0a6567d80d3c79e0cb7e87483329891` |
| `Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CONFIGURATION_AP4_DESIGN_2026-11-26.md` | `48a3aca3ba787464e0bd9833b221b3b26a74a09b` |

The companion evidence and Primary report also retain the SHA-256 identities. The source comparison is one commit and five changed files from the accepted baseline.

| Suite | Methods per environment | Host footer seconds | CI footer seconds | Host / CI result |
| --- | ---: | ---: | ---: | --- |
| R5 writer | 94 | 0.153 | 0.186 | `OK` / `OK` |
| AP1-R2 | 22 | 10.100 | 4.107 | `OK` / `OK` |
| AP2 | 25 | 14.532 | 6.656 | `OK` / `OK` |
| AP3 | 20 | 8.752 | 4.202 | `OK` / `OK` |
| AP4 | 18 | 8.725 | 4.140 | `OK` / `OK` |
| Total | 179 | — | — | Five successful suites in each environment |

The host ran from `2026-11-26T10:34:00.186076+00:00` through `2026-11-26T10:34:43.600855+00:00`; its five suite processes exited 0. It used Python `3.12.14`, platform `Linux-6.18.57-x86_64-with-glibc2.41`, fixture Git `/usr/local/bin/git` version `2.56.1`, and auditor Git `/bin/git` version `2.47.3`. Its static checks record three parsed Python AST files, parsed workflow YAML, six Bash run blocks, no trailing whitespace, matching refactored AP3 pin, unchanged source bytes after tests, preserved initializer logic, and unchanged other existing AP3 top-level AST.

[Run 45803071282](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282), attempt 1, and [job 139851042426](https://github.com/night-outlook/hybridclr_demo/actions/runs/45803071282/job/139851042426), `future-admission-source-host`, completed with `success`. All twelve returned steps succeeded. The run record was created at `2026-11-26T10:37:33Z` and updated at `2026-11-26T10:38:09Z`. The workflow specifies `ubuntu-24.04`; the actual tool-version record reports Python `3.11.18`, fixture Git `/usr/bin/git` version `2.56.1`, and auditor Git `/bin/git` version `2.56.1`. Five actual `OK` footers and the AP4 method inventory match the host receipt. The per-suite durations above are unittest footers, not workflow wall times.

The separate host and CI closed-gate controls returned `NotAuthorized`, exit 2, `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`, and `outputCreated=false`; the unapproved envelope pathname remained absent. These negative controls do not authorize admission.

Raw records to inspect:

- [D5B_RUNNER_CONFIGURATION_AP4_SOURCE_HOST_2026-11-26.log](D5B_RUNNER_CONFIGURATION_AP4_SOURCE_HOST_2026-11-26.log): 31323 bytes; SHA-256 `a39479730cd312f9aa7195a8d0aad8b2c15c59facd1452ea9b688ac79cf56331`; Git blob `0ffcfaecf225e7e4598036771c9007328af64719`.
- [D5B_RUNNER_CONFIGURATION_AP4_CI_45803071282_JOB_139851042426.log](D5B_RUNNER_CONFIGURATION_AP4_CI_45803071282_JOB_139851042426.log): 60972 bytes; SHA-256 `28865ccb94d9da06d16d9c6400e46694eb9e3da60d93f7209cfb81f2ceb028cd`; Git blob `5c54ed3f15e5745d7dcac26669da81438c7d2073`.

The CI file preserves the exact UTF-8 encoding of the Connector-decoded log text and its leading BOM; it does not attest original ZIP/archive bytes. The first Connector artifact page returned zero uploaded artifacts. Other workflow states are observations only and are not AP4 qualification evidence.

The AP4 methods directly exercise captured bytes after benign post-snapshot pathname changes, actual consumers and helper scope, enabled blob checks, one fresh snapshot/context, no content/process I/O during bounded consumption, malformed-record consistency rejection, ordinary failures and truthful partial progress, profile-read failure without a false invocation claim, frozen earlier reports, narrow immutable public results, helper cleanup on covered ordinary paths, and real CLI/flag controls. The retained AP3 suite supplies regression evidence. Independently assess whether these tests substantiate the bounded claim rather than extrapolating to future runtime integration.

Primary's internal peer review found no source blocker, and its ordinary-Exception/argparse clarification was incorporated before qualification. This is internal Primary evidence, not an independent verdict.

## 7. Practical review commands

With the target commit available in a repository, inspect its identity and baseline change scope:

```bash
git show --no-patch --format=fuller 000e72941f74e52aa18bcd17553e8929acc69167
git rev-parse '000e72941f74e52aa18bcd17553e8929acc69167^{tree}'
git diff --stat 77fe1c174eb44c2d14a26cc9b057671541efe2a3 000e72941f74e52aa18bcd17553e8929acc69167
```

From a trusted source copy matching that commit, the source-host workflow uses these suite entry points:

```bash
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_local_admission.py -v
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_activation_publication.py -v
python3 -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_closure.py -v
python3 -I -S -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_imports.py -v
python3 -I -S -B Tools/AssemblyShadow/R03IR/D5Local/test_d5b_runner_configuration.py -v
```

These are source-only fixture checks. No native, Unity, Player, admission, or Q execution is requested for review.

## 8. Authority caveat and verdict limits

The candidate writer's approval constant is checked against the closure's candidate proposal-envelope literal by the existing initializer. It cannot be assumed to remain null merely because the production source uses `None`. Candidate literal identity is not an approved envelope and AP4 does not change it.

The public approved-envelope field remains null; `executionAuthorityVerified=false`. Independent configuration binding and executable admission remain `Pending`. `WEB_TO_LOCAL=CLOSED_NO_LOCAL_EXECUTION`; Local execution/validation and explicit user Local approval remain `NotAuthorized`. Native/Player permission flags remain false. Unity/build/Player work remains unperformed, with zero real Player cells passed and eighteen without coverage. R03 acceptance, H2, the human-review gate, and Q authority remain closed.

Broad runtime/future-runtime configuration closure, import isolation, executable closure, standard-library identity, live remote state, continuous/exclusive custody, other source inputs, and current Mac inputs are not established. Future `inspect`/`main`/admission integration and native/Unity/Player/Q work remain deferred.

Independent AP4 is `Pending` until a separate reviewer issues `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired` against the final exact source and evidence. A source-only pass would not open any execution authority or extend the claim beyond these fixed consumers.

## 9. Repository tuple, publication and required review record

| Repository | Branch | Source review commit | Historical candidate path — physical state Unverified |
|---|---|---|---|
| `night-outlook/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` | `000e72941f74e52aa18bcd17553e8929acc69167` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` |
| `night-outlook/hybridclr` | `codex/assembly-shadow-r01b-h1` | `c3c232023724cbad565b85e9b2c3beea8ce2789a` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` |
| `night-outlook/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` | `948c0e3b4f8891481301770115e8ba4945eea6de` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` |
| `night-outlook/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` | `1268dd417ffe9090fcd9ea2d49542c97ed3cccb3` | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` |

The table identifies source scope. The commit containing this request and evidence is a documentation-only child of `000e72941f74e52aa18bcd17553e8929acc69167`. Resolve the actual latest pushed feature HEAD for the demonstration repository and record it separately from the tested source; fresh-read the three sibling refs as well. Historical Mac paths are physical-state Unverified and are not instructions to run Local tools. The Primary report's transport section records the reused four-repository Connector smoke proof and its retained refs.

Read README and the current WEB_TO_LOCAL checkpoint first, then the accepted AP3 independent report, AP4 design, Primary report, machine/raw evidence and exact source. This review should identify the source and publication commits, four refs, five changed-file blobs, twelve preserved baseline blobs, unchanged Local-owned records, raw-log digests, actual AP4 method inventory and all execution/acceptance limits.

Publish a separate independent AP4 report and machine evidence under this history directory, with factual findings and `PassRunnerConfigurationBindingSourceOnly` or `ReturnRequired`. Preserve Primary-owned WEB_TO_LOCAL and Local-owned LOCAL_VALIDATION/RETURN_TO_WEB. Stop after independent publication and remote readback. No native/Unity/Player/Local execution, approval repinning, production activation or next milestone is part of this request.
