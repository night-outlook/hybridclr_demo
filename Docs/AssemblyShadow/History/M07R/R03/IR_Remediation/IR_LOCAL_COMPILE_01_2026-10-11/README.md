# IR-LOCAL-COMPILE-01 — canonical temporary fixture correction

Owner: Primary Implementation. Date: 2026-10-11. Scope: SDK scratch test fixture and fresh compile-only handoff; no production guard or runtime correction in this cycle.

## Original observation remains immutable

At Local prerequisite source `c5662700452ebc4769b376303e1b812cb42ccc72`, the F-COMP scratch suite ran once: **10 tests, 3 Passed, 5 failures, 2 errors**. F-COMP result is **PrerequisiteBlocked**. Subsequent reporting/access/observer host checks, native policy, managed compilation and all 55 native configurations were **NotRun**. Before-custody admission scan was **NotRun**. The independent after-custody scan verified 339,367 survivors and 77,477 unchanged missing identities from 416,844 entries, zero problems; strict historical custody remained **Blocked**. Installed SDK preservation verified 2,113 files unchanged. Zero Unity/Player launches.

Authority: [Local F-COMP checkpoint](../../local-validation-20261010-ir-r03-02-f-compile-only/README.md), [raw scratch diagnosis](../../local-validation-20261010-ir-r03-02-f-compile-only/preflight/SCRATCH_TEST_DIAGNOSIS.json), [original stderr](../../local-validation-20261010-ir-r03-02-f-compile-only/preflight/commands/sdk-scratch-tests/stderr.log), and Local-owned reports at publication `a9483a6e2212701cfedcf93faeb0e71ce82b73ca`. These files are not edited by this correction. F-COMP cannot be retried or relabeled Passed.

## Cause and implementation

`test_native_validation_scratch.py` kept `Path(self.temp.name)` unresolved. On the Local Mac its `/var/folders/...` parent resolves through `/private/var/folders/...`. The production predicate `raw.is_absolute() and raw == raw.resolve(strict=False)` correctly rejected that input, so most tests never reached their intended occupied-root, missing-parent or overlap checks.

The corrected fixture resolves **only its owned existing root** using `Path(self.temp.name).resolve(strict=True)` before deriving test workspace/evidence/Editor/scratch paths. A test-only directory factory permits a second inherited cohort to create the fixture under an explicit symlink parent. It asserts that the supplied parent really is a symlink and that the resulting raw fixture differs from its resolved path. No environment `TMPDIR`, global tempfile setting, validator input normalizer, skip, or platform exemption is introduced.

All ten original test bodies and expectations remain unchanged. The inherited cohort executes the SAME ten tests with the guaranteed alias: **20 tests total**. Deliberate relative/symlink, occupied, missing-parent, source/evidence/Editor overlap and no-write controls remain mandatory. Cleanup affects only owned synthetic fixtures, never local SDK/historical data.

Only executable file changed: `Tools/AssemblyShadow/R03/test_native_validation_scratch.py` at source commit **`e36ab83b969f8ba8f9f4cc21fc8bb6c447d7fa2f`**, Git blob `5e58c14b5147ee591dda34d802f78b98d36cbaf7`, SHA-256 `dfbef375899856b3026584b81524228b53d458de7c0e85e7183f5a0249f05de2`.

**Unchanged production validator:** `Tools/AssemblyShadow/R03/native_validation.py`, Git blob `15282b61dda3f61106913ce9e2973cc87d76c23d`, SHA-256 `bbe544b49d89325f40305045248295caf59ec01e98440ae184d4efbd08729428`. `build_api.py`, source-pins.json, C# Player, all native sources, fixtures, storage/custody guards and previous procedures are unchanged. No native/package repository receives a commit in this cycle.

## Verification and limits

[GitHub Actions run 38123748124](https://github.com/night-outlook/hybridclr_demo/actions/runs/38123748124) at exact source e36ab83b completed successfully on **macos-14 and ubuntu-24.04**. Both jobs ran **20 Passed / 0 failures / 0 errors / 0 skipped**, including all ten aliased-parent cases. AST checks and clean-source checks passed. Both original ZIP artifacts were downloaded through the Connector and independently authenticated by archive SHA-256, member sizes/hashes, test names/results and source receipts.

[CI_EVIDENCE.json](CI_EVIDENCE.json) contains exact run/job/artifact/source identities and digests. Complete byte-preserved test logs: [macOS](ci/macos-14-scratch-tests.log) and [Ubuntu](ci/ubuntu-24.04-scratch-tests.log). Artifact IDs 11696566789 / 11696157405 are retention-limited; the copied logs and source bindings persist here. Earlier provisional inline ZIP encodings were replaced before handoff; only this final receipt and these digest-bound log files are authoritative.

This is a host fixture/admission regression pass, **not** official managed/native compilation, fresh Local live custody, SDK copying, Unity execution or runtime acceptance. G-COMP must rerun its prerequisites and perform its actual compiler work. Source review checked that the ten method bodies, production validator and non-demo pins were not relaxed. No independent full-stage review is claimed.

Connector bootstrap verified all four requested remote heads and read/push metadata. Demo-only disposable write test branch `codex/connector-smoke-20261011-compile01-92d7`, commit `34c96ec8c3f14c2a18141ddb98e373eda59c44e0`, passed exact remote readback. It remains because the Connector does not expose branch deletion. This is transport evidence only.

## Successor and unchanged acceptance

[G-COMP compile-only procedure](G_COMPILE_ONLY_PROCEDURE.md) defines new `20261011G-canonical-temp` roots and an additive G checkpoint. Use the final exact pushed four-SHA prompt and current `Handoff/WEB_TO_LOCAL.md`. Do not reuse F-COMP outputs, even its uncreated compiler roots; do not select alternative paths. Stop on any failed prerequisite and publish actual Failed/Blocked/NotRun states. Complete original-C before/after custody and installed-SDK preservation; no rebaseline or protected cleanup.

One managed compiler-script invocation and one native compiler-script invocation are conditionally permitted; no Unity process, Test Runner, IL2CPP Player build, Player or runtime scheduler. Compilation success must return to Primary before any runtime assignment. E remains **FAIL**, its originating runtime failure/ON proofs Unavailable. Strict custody Blocked; four historical S native roots Missing. Independent R03 full-stage FAIL/re-review NotRun; all acceptance flags false and PureInterpreter expansion disabled. No H2/X02/M08A or Human Review Gate advancement.
