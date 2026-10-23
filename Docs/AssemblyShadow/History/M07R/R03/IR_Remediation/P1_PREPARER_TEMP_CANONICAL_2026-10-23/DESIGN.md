# R03 P1: Canonical temporary-directory fixture remediation

## Authority and latest empirical result

Latest Local-owned cycle `20261023-6c72` is **BLOCKED / PrerequisiteBlocked**. Its initial four-source clean/remote, historical evidence, installed Unity SDK and unused-root admission Passed. It executed one published `test_prepare_p1_admitted_local.py` prerequisite suite: **13 discovered tests, 12 Passed, 1 ERROR**, exit 1. The failed test was `LocalCollectorRepairTests.test_pristine_root_fail_closed` in the Primary-authored test at blob `58e6e0b9ff870d1ada20021ab36a82882d60b837`; root finding `IR-LOCAL-P1-PREPARER-TEMP-01` is immutable. The actual preparation was NotRun and 0/25 core components were invoked. The 6c72 evidence report, source and installed SDK bytes were preserved by independent Local after-checks. This is **not** a native code or SDK failure.

The test created a `tempfile.TemporaryDirectory()` and passed `Path(d) / 'absent'` to `pristine_root`. Native macOS inherits `TMPDIR=/var/folders/...`, whose `/var` path resolves to `/private/var`. The existing and correct production guard rejects noncanonical roots: `path.resolve() != path`. The expected-valid fixture input was accidentally noncanonical. No adjustment to the guard, environment or Local evidence is justified.

## Narrow, chosen correction

Modify **only** `Docs/AssemblyShadow/Handoff/Tools/test_prepare_p1_admitted_local.py`:

1. In the preexisting failing leaf, use `parent = Path(d).resolve(strict=True)` for the fixture-owned parent, then preserve the original expected-valid absent child, existing parent rejection, symlink rejection, and relative-path rejection.
2. Add `test_inherited_tempdir_alias_is_rejected_before_canonicalization`: independently compare inherited `Path(d)` with its resolved canonical path, always verify canonical absent child succeeds, and on actual alias hosts verify raw inherited path fails.
3. Add `test_aliased_parent_refused_even_with_absent_child`: create a **test-owned** symlinked directory parent on any host; require canonical absent child acceptance and both aliased child and aliased parent rejection.

The **real preparer** `prepare_p1_admitted_local.py` is byte-identical to historical blob `cf2fdf39fe17df076d50dcc33ed72c757eaa3b26`. Do not change `pristine_root`, aliases in the user's real workspace, Git checks, source identity and frozen baseline reconstruction, SDK flags, old test IDs or product code. No `TMPDIR` override is authorized in actual Local Validation.

## Evidence, scope and stop

Primary repeated the complete **15/15** suite on a canonical Linux Python 3.13.5 host and also **15/15** under a test-owned in-process simulated `/var -> /private/var` inherited temp alias. Exact executed source Git blobs match the pushed test source and unchanged preparer; Python syntax parsed. The macOS native prerequisite suite is **NotRun for this correction** until Local. The Linux simulation is not a factual native macOS result.

One fresh independent Local cycle may run only after new four-root independent admission, exactly one updated 15-leaf prerequisite suite, one source-bound preparer, one 25-component source/host/official installed Unity2022.3.62f2 SDK syntax-only batch, original 85 tests, eight inventories, nine strict and nine sanitized admitted cases, five managed positive products plus original compiler-negative, 100 C++17 syntax commands and 20 Git postflight checks. Independent factual audit and old checkpoint/SDK preservation are required. Failure consumes the new root identifiers; no repair/retry or alternate suffix in Local.

No Unity Editor/Player, product-native linking, actual runtime GC/RSS/Shutdown, canonical TypeKeys, original V1 getter activation or milestone progression. P1 Incomplete, P2 NotIntegrated, E0 Blocked/Unavailable, E1 BlockedByE0, P3 Incomplete; original R03/H2/Human Review flags remain false; PureInterpreter disabled.
