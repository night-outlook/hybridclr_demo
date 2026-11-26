# D5-B AP3 runner import bootstrap design

Date: 2026-11-26, America/Los_Angeles. Actual UTC execution timestamps retain their own meaning.

Stage: Primary source-only design and implementation increment.

Base: `20ca45419ca797ed2bcd330a7be0698fab59819f`.

Precondition: AP2 runner artifact and checkout observation passed the [accepted independent review dated 2026-11-26](D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md), report Git blob `c9ee646dc77b2775d336b5afcee517a7e0932255`.

Requested independent verdict: `PassRunnerImportBootstrapSourceOnly` or `ReturnRequired`

## 1. Decision and bounded claim

AP3 adds a trusted import bootstrap for the exact three reviewed candidate Python modules already captured by fresh AP2 verification. It initializes those modules from immutable in-memory source bytes, resolves their direct imports through private exact allowlists, checks their resulting bindings, and returns an observation. It does not call any candidate function.

The successful observation means that the fixed reviewed module initialization used the selected verified bytes and the specified import providers. It grants no permission to call a runner, perform admission, run preview, create a one-use receipt, build native code, launch Unity or a Player, or advance Q or any acceptance gate.

This is not a Python sandbox, an attestation that the interpreter or standard library is pristine, runtime configuration closure, continuous filesystem custody, or complete executable closure. Importing a module executes its top-level Python statements. A successful AP3 report must say that candidate initialization occurred; it must not describe the candidate modules as remaining inert bytes.

The implementation is a new `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_imports.py`. The eleven baseline implementation, test, and configuration files remain unchanged. Within the existing implementation/test/configuration/workflow surface, only the workflow is eligible for integration changes; new AP3 implementation, tests, and documentation are separate additions. An AP3 design or source-only pass does not authorize changing the established candidate source, plan, profile, publication envelope, or earlier verifier contracts.

## 2. Public API and process boundary

The public API is:

```python
observe_runner_imports(raw: bytes, expected_closure_blob: str) -> ImportObservation
```

`raw` is the externally pinned closure proposal supplied to AP2. `expected_closure_blob` is its exact external Git blob identity. Neither value is approval.

The API accepts no caller-constructed bundle, module objects, import resolver, import callback, additional import paths, replacement standard-library map, execution option, or candidate arguments. It has no preview or execute mode. A caller cannot promote a fabricated `VerifiedBundle` into a trusted observation merely by constructing the same Python type.

`ImportObservation` stores immutable JSON bytes. Its `report` accessor returns a fresh decoded value on each access, so changes made to a returned dictionary do not change the recorded observation. The result exposes no candidate module, callable, code object, import hook, or execution handle. This immutable representation protects the observation from ordinary presentation changes; it is not a security boundary against arbitrary hostile code in the same process.

The public boundary requires the actual trusted-process flags associated with `Python -I -S -B`: isolated mode, no site initialization, and disabled bytecode writes. This check belongs in the API as well as any CLI wrapper. Calling AP2's Python API alone does not establish these flags, because the existing AP2 flag check is in its CLI entry point.

A fresh trusted interpreter and its trusted standard library are explicit prerequisites. The flags and the bootstrap do not authenticate the interpreter binary, prove the provenance of every preexisting standard-library object, or cleanse a process in which arbitrary code has already run.

## 3. Trusted AP2 acquisition and fresh verification

AP3 authenticates the adjacent `d5b_runner_closure.py` against this exact Git blob before compiling it:

```text
2535bc14c31f1ff2d73fdb8c7be1d7dab605d990
```

The helper is read into bytes, checked against the embedded exact pin, and compiled from those same checked bytes. AP3 must not acquire it through ordinary lookup of the module name, an ambient module cache entry, or a second pathname read after authentication. The read is bounded and must reject unsupported or changed file conditions under the implementation's explicit trusted-helper read policy.

AP2 uses dataclasses. If execution of the authenticated helper requires a `sys.modules` registration for that standard-library mechanism, AP3 may install one temporary, uniquely named trusted-helper entry. It must not overwrite an existing entry, and must remove its own entry on both success and failure. This allowance applies only to the authenticated trusted helper. Canonical candidate names are never installed in real `sys.modules`.

The loaded helper performs a fresh `verify_runner_closure(raw, expected_closure_blob)` call. AP3 consumes the resulting immutable `BundleFile.raw` bytes directly. It does not replace fresh verification with a report supplied by the caller, a cached success flag, or an externally constructed bundle.

AP2's physical checkout, artifact, and location observations occur before candidate initialization. AP3 introduces no new post-import checkout or custody observation and must not report one. AP2's existing limits on snapshot observation and continuous custody remain in force.

## 4. Candidate graph and exact direct imports

The candidate graph is closed and has three modules:

| Private candidate name | Verified relative source path | Project import |
| --- | --- | --- |
| `d5b_rr5_source_preflight` | `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py` | None |
| `d5b_local_admission` | `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py` | `import d5b_rr5_source_preflight as source` |
| `run_d5_local` | `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py` | `from d5b_local_admission import main` |

The direct standard-library allowlists are per module:

| Candidate | Allowed standard-library requests |
| --- | --- |
| Preflight | `from __future__ import annotations`; `argparse`; `hashlib`; `json`; `from pathlib import Path`; `re`; `subprocess`; `sys` |
| Writer | `from __future__ import annotations`; `argparse`; `hashlib`; `json`; `os`; `from pathlib import Path`; `platform`; `re`; `shutil`; `stat`; `subprocess`; `sys`; `from typing import Mapping` |
| Wrapper | None |

These requests are resolved from a fixed map of already loaded trusted standard-library references, with the special private `sys` facade described below. The map is not supplied by the caller. Exact project names, standard-library names, relative-import level, and approved `from` requests are checked by the per-module importer. Unknown requests fail closed. No fallback to the process's normal project import machinery is allowed.

The reviewed sources contain no additional function-local import statements. That fact bounds this source-only increment to the reviewed initialization. It is not a general guarantee for other code or later revisions.

## 5. Module initialization mechanism

AP3 creates fresh module objects in a private candidate table and initializes them in dependency order: preflight, writer, wrapper. Each receives its own builtins dictionary with a private `__import__` function. Changing that dictionary does not replace process-wide builtins.

For each candidate, compilation consumes the verified bundle's immutable `bytes`. The module's `__file__` and the compiler's filename derive from the verified runner root and fixed relative path. Source loaders, ordinary module-name imports, reopening candidate code paths, `.pyc` caches, and candidate entries in real `sys.modules` are not used.

Each module has a non-`__main__` name. Its existing main guard therefore remains inactive. The original source bytes are not rewritten. AP3 does not strip an import, replace a function, alter an approval constant, or patch the plan/profile bindings.

The candidate importer returns the private preflight object to the writer and the private writer object to the wrapper. Ambient `sys.modules` entries bearing the same canonical candidate names neither satisfy these requests nor receive the newly created modules.

### Private `sys` path

The reviewed writer contains this top-level behavior:

```python
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "D5Admission"))
```

AP3 supplies a private path-only `sys` facade whose `path` is a private list. The writer's literal insertion affects only that list. The facade does not delegate unknown attributes to real `sys`, and the bootstrap neither modifies real `sys.path` nor temporarily modifies and restores it.

This deliberately supports the reviewed import initialization only. Later candidate functions refer to additional `sys` attributes; AP3 does not call those functions or claim that this import context is an approved runtime environment for them.

### Import-time side effects

Both the writer and preflight call `Path(__file__).resolve()` at top level. These operations may perform filesystem metadata reads. They are acknowledged rather than hidden by a claim that module import performs no filesystem operations.

The remaining reviewed top-level behavior binds imports, constructs constants and collections, compiles regular expressions, and defines classes and functions. Plan/profile content reads and candidate entry-point operations occur only in functions that AP3 does not call.

The verified root/path labels establish where the compiled source was observed. They do not establish that a pathname still denotes its AP2-observed inode after AP2 returns. In particular, `resolve()` can observe later filesystem state. AP3 does not convert those labels or derived `Path` values into a fresh custody claim.

## 6. Observations and reporting

The successful result is:

```text
kind: R03D5BRunnerImportObservationV1
result: RunnerImportBindingsObserved_NoExecutionAuthority
```

The observation records the external closure pin, authenticated AP2 helper pin, verified source identities, import requests and their selected providers, and the module initialization stages. It may include only the bounded binding and provenance facts needed to assess import selection, including:

- The three initialized candidates came from their corresponding immutable AP2 bundle bytes.
- `writer.source` is the privately initialized preflight module.
- `wrapper.main` is the writer's `main` function, established by identity comparison without calling it.
- Canonical candidate names were not installed in real `sys.modules` or selected from its ambient entries.
- Candidate initialization did not change real `sys.path`.
- The temporary trusted AP2 helper registration, if needed, was removed.

The report must distinguish candidate import from candidate function invocation. If it retains AP2's combined `candidateWriterExecutedOrImported` field, that field is true after successful writer initialization. A separate entry-point-invocation field remains false. Describing a successful import as "candidate code did not run" would be incorrect.

Attempted and completed module initialization are tracked separately. The attempted state is armed before entering the initialization operation; completion is recorded only after execution returns. A failure after preflight or partial writer initialization retains those observations. Rejection cannot erase earlier progress or claim that no candidate initialization occurred merely because the overall bootstrap did not succeed.

No error path falls back to another import provider, starts a candidate entry point, retries under broader permissions, or changes a gate. Rejection reports remain closed and preserve the stage reached.

## 7. Runtime configuration remains outside AP3

The plan, profile, and closed publication proposal remain data in the verified bundle. AP3 does not compile them, invoke candidate validators on them, or redirect candidate runtime reads to them.

| Input | Existing later read | AP3 limitation |
| --- | --- | --- |
| Runner plan | Writer `read_plan()` checks the plan pathname and reads `PLAN.read_bytes()`; blob verification is enabled by default. | AP3 does not call it. A later pathname read is not automatically bound to the immutable bundle snapshot. The optional `verify_blob=False` path is not used by AP3. |
| Runner profile | Preflight `inspect()` reads `PROFILE.read_bytes()` and passes the result to `checked_profile()`. | AP3 does not call it. Import selection does not establish descriptor-based no-follow runtime configuration access. |
| Profile in active demo source | Preflight `inspect()` separately verifies the profile under the active source checkout. | The source-checkout profile and runner-adjacent profile are distinct reads and locations. AP3 does not merge their custody claims. |
| C10 pinset, source files, historical B1 data | Preflight `inspect()` reads and checks these runtime inputs. | Source-data admission and their runtime read custody remain unverified by AP3. |
| Preview request, later envelope, repositories, live refs, Mac tools | Writer entry points and inspection functions obtain these inputs and observations. | None is invoked or admitted by this bootstrap. |

The existing plan/profile hash checks authenticate the bytes a later caller actually reads when those checks are enabled. They do not establish continuous pathname custody or prove that the caller consumed the AP2-captured snapshot. Binding runtime reads to immutable reviewed data requires a separate reviewed increment.

The import-only bootstrap must not call `read_plan`, `checked_profile`, `inspect`, either candidate `main`, `inspect_source_and_remote`, `inspect_machine`, `approved_envelope`, `seal_oneuse_dry_admission`, or any other candidate function. In particular, the writer's preview mode performs substantive admission-related reads and probes and is outside AP3.

## 8. Closed authority and non-claims

Success and rejection preserve closed authority. In particular:

- Admission, preview, and one-use writer invocation are false.
- No evidence output is created by a candidate operation.
- `approvedEnvelopeGitBlob` remains null as an authority field. A candidate literal or publication blob may be recorded only as artifact identity.
- `WEB_TO_LOCAL` remains `CLOSED_NO_LOCAL_EXECUTION`.
- `D5BLocalExecution` and `D5LocalValidation` remain `NotAuthorized`.
- Independently reviewed executable admission remains pending; explicit user Local approval remains unauthorized.
- Native build, Unity execution, IL2CPP linking, and Player execution remain unperformed; build and launch permissions remain false.
- All 18 real Player cells remain without coverage and the real Player pass count remains zero.
- Q is neither established nor approved. `R03Accepted`, `H2Passed`, and `ReadyForHumanReviewGate` remain false.
- Runtime configuration-read closure, source-data admission, live remote refs, current Mac inputs, exclusive or continuous custody, execution authority, and complete executable closure remain unverified.

Any positive import-isolation field must be explicitly scoped to selection of imports during these fixed reviewed initializations. It must not imply full runtime import isolation or a general capability sandbox. Standard-library objects such as `os` and `subprocess` remain capable objects; AP3's basis is exact reviewed initialization with no candidate function calls.

## 9. Independent review boundary

The AP2 independent Pass recorded in the accepted 2026-11-26 report remains the prerequisite for this increment, not its verdict. AP3 requests a separate review with exactly one of these outcomes:

- `PassRunnerImportBootstrapSourceOnly`: the reviewed bootstrap establishes its bounded import-binding observation, maintains the baseline files and closed gates, and makes no broader execution or custody claim.
- `ReturnRequired`: a defect, missing evidence, changed baseline, or excessive claim prevents that conclusion.

Review should assess source provenance before compilation, fresh AP2 verification, exact private imports, absence of ambient candidate selection, confinement of the writer's path insertion, truthful partial-initialization reporting, non-exposure of execution handles, and the explicit runtime-read and custody limits above.

Neither verdict changes Local authorization. A source-only Pass authorizes no admission, preview, native build, Unity/Player execution, receipt creation, Q, or acceptance transition.

## 10. Source references

- `Tools/AssemblyShadow/R03IR/D5Local/run_d5_local.py`: the wrapper import and guarded `main()` call.
- `Tools/AssemblyShadow/R03IR/D5Local/d5b_local_admission.py`: direct imports; top-level `HERE` resolution and path insertion; runner-relative `PLAN`; later plan, inspection, preview, and writer operations.
- `Tools/AssemblyShadow/R03IR/D5Admission/d5b_rr5_source_preflight.py`: direct imports; top-level `ROOT` resolution and `PROFILE`; later profile and source-data reads.
- `Tools/AssemblyShadow/R03IR/D5Local/d5b_runner_closure.py`, pinned at `2535bc14c31f1ff2d73fdb8c7be1d7dab605d990`: AP2's immutable bundle, fresh closure verification, snapshot observation, and closed report contract.
- [Accepted AP2 independent review dated 2026-11-26](https://github.com/night-outlook/hybridclr_demo/blob/20ca45419ca797ed2bcd330a7be0698fab59819f/Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/POST_B1_PASS12_2026-11-10/D5B_RUNNER_CLOSURE_AP2_INDEPENDENT_REVIEW_2026-11-26.md), report Git blob `c9ee646dc77b2775d336b5afcee517a7e0932255`: AP2 independent Pass at base `20ca45419ca797ed2bcd330a7be0698fab59819f`, supplied as the controlling prerequisite for this AP3 design.

This document records the AP3 design. It does not record an AP3 independent review result or execution authorization.
