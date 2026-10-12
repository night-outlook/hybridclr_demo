# IR-LOCAL-CUSTODY-03 — H synthetic custody fixture alias correction

**Owner:** Primary Implementation. **Date:** 2026-10-12 UTC. **Disposition:** Source/host regression correction **Passed**; fresh Local I runtime preflight/execution **NotRun until independently admitted**. This is a bounded test-fixture repair, not runtime acceptance or original historical custody restoration.

## 1. Original H return is immutable

At exact execution demo `1e69bc11e6fbeab3fb1b4219101fb4186c578895`, H's mandatory C-scoped custody suite ran **15 tests: 12 Passed, 3 Failed, zero errors/skips**. Original C's five genuine immutable-receipt binding tests Passed. Seven synthetic tests Passed. Three synthetic tests failed before their intended status classification:

- `test_unchanged_historical_loss_is_scoped_only`: observed `Blocked` instead of `ScopedHistoricalLossStable`.
- `test_additional_missing_blocks`: observed `AdmissionError` instead of `NewMissing`.
- `test_restoring_originally_missing_requires_primary_review`: observed `AdmissionError` instead of `UnexpectedRestorationNeedsPrimaryReview`.

The actual macOS inherited `TMPDIR=/var/folders/.../T/` resolves to `/private/var/folders/.../T/`. The synthetic fixture set `self.root = Path(self.tmp.name)` without resolving the *owned* temporary directory. `verify_scoped_custody.audit_exact` correctly rejects that symlinked **parent** before it examines missing/stable/restored fixture files. [Original H diagnosis](../../local-validation-h-post-gcomp-7d42/preflight/C_CUSTODY_TEST_DIAGNOSIS.json), [failed stderr](../../local-validation-h-post-gcomp-7d42/preflight/commands/c-custody-tests/stderr.log), and [original result](../../local-validation-h-post-gcomp-7d42/preflight/LOCAL_H_RESULT.json) establish those facts. Local H publication `588cafb044e7d5e6da185368c5f69da709903bc4` and every historical H receipt are unchanged.

H's 20 scratch and 65 R03IR tests Passed; downstream retained-E/native/69-policy, **before** full custody and preservation, both storage sessions and all 14 cells / three native builds / four Players are **NotRun**. Zero Unity and Player launches. Its independent *after-only* live C custody audit found 339,367 survivors hash-verified, exactly 77,477 frozen missing identities out of 416,844 and zero problems; **after is not before admission**. It preserved original E and G/installed SDK bytes as bounded historical receipts. H cannot be resumed or retroactively promoted to Passed.

## 2. Minimal source correction

One existing file under Docs changed:
`Docs/AssemblyShadow/History/M07R/R03/IR_Remediation/IR_LOCAL_CUSTODY_01_2026-10-09/test_scoped_custody.py`.

In `ScopedCustodyUnitTests.setUp`, `Path(self.tmp.name).resolve(strict=True)` replaces the unresolved test-owned fixture root, *before* deriving test paths. Its source `new_fixture_directory()` factory defaults to the same standard `tempfile.TemporaryDirectory()`. A new subclass `AliasedTempScopedCustodyUnitTests` inherits every original synthetic test unchanged but deliberately constructs the directory under a verified symlink-backed parent; that subclass asserts the input was genuinely noncanonical before the shared fixture resolves it. No environment `TMPDIR` modification, skip, fake PASS, global tempfile override or platform exemption.

All **ten original synthetic test methods and expectations remain intact**, including cases requiring `NewMissing`, `UnexpectedRestorationNeedsPrimaryReview`, rejection of changed/restored/symlinked paths, and independent original C binding. The five genuine C tests are unchanged. The suite now has **25 tests**: ten original synthetic + ten inherited aliased-parent synthetic + five genuine C.

**Production `verify_scoped_custody.py` is byte-for-byte unchanged**, Git blob `ccc6af25d5d424b3bffe629ebd609ec5e5beed0a`, SHA-256 `fe4f3a21333f07bbf8f9e6120eb88a736b1faf4a92da01f2f98b0100e0dbb61d`. Original frozen C map (416,844 identities), all historical hash pins, missing-file exception and rejection guards are unchanged. No Player/native production code, fixtures, scripts, compiler profiles, storage thresholds or source pins changed. Test correction commit `06c4c483aa2ffad661a8c39d5ca5ee25f2c2fe4a`; repaired test blob `86f79849f2f4a5771e509815b3a005d3d9f3b0a6`, SHA-256 `5bda30a457d4ab90b646afcd1bce78521ca55b99cd30653a6cc38cef4c5b05e5`.

## 3. Actual original C corpus regression: 25 Passed on each OS

Isolated CI verification branch `codex/r03-h-custody-fixture-ci-20261011-4b8e` was created **at** fixed active source commit `06c4c483aa2ffad661a8c39d5ca5ee25f2c2fe4a`. It adds only its CI workflow `.github/workflows/r03-h-custody-fixture-sourcecheck.yml` on that disposable branch. Do not use that branch or its HEAD `f37419e6c2c1d0879964169ef3adbd954801ca58` as a Local runtime source.

[Run 38197141796](https://github.com/night-outlook/hybridclr_demo/actions/runs/38197141796), macOS job 114642218248 and Ubuntu job 114642218442: **both Passed, 25/25**, no errors/failures/skips. The tests executed the *actual frozen C* five SHA-256 + original Git-blob receipt checks and parsed all four C map parts (127,296,143 total bytes and 416,844 entries), while the synthetic tests used only disposable fixtures. No protected live Mac S file was opened by these CI checks. The CI manifest binds the repaired test blob and unchanged verifier blob.

Both original GitHub artifact ZIPs were downloaded and independently authenticated: macOS artifact 11724215407 SHA-256 `e3dd6ffaa1b4d56657218727c1511ee857e62ff227b7568bfdba39d0c096d60e`; Ubuntu artifact 11723751907 SHA-256 `615aa0262bd1acb4cede76b34d657f5553a5ed9af2a2b73c31d4b95cbbad6237`. Their **complete byte-identical original test logs** are retained as [macOS](ci/macos-14-custody-tests.log) and [Ubuntu](ci/ubuntu-24.04-custody-tests.log). The retained Git blob IDs, SHA-256 digests and CI job/source identities appear in [EVIDENCE.json](EVIDENCE.json). The CI ZIPs expire per GitHub retention; repository logs persist. These are host/corpus tests, not a fresh Local live inventory or Unity test.

## 4. Narrow successor boundary: I, not resumed H

The linked [I runtime procedure](I_RUNTIME_PROCEDURE.md) and final Primary four-SHA `Handoff/WEB_TO_LOCAL.md` conditionally authorize **one new I preflight**. All four candidate external roots with suffix `I-post-H-custody-7f36` must be absent/canonical/nonsymlinked/nonaliasing; no reuse of H or other historical roots. Final demo must be a docs-only descendant of G-compiled source `d7f46bfd090313b41b38175ce1196f14484a3d1e` and retain the exact other three pin commits.

Fresh Local must run **25 C custody tests** (10 original + 10 aliased + five real) along with the 20 scratch, 65 R03IR, nine retained-E, native reporting/observer/Object.h and 69 policy tests; verify immutable original C/E/F/G/H/S/R/Q evidence and **all 15 original S fixture DLLs**. Complete both full original-C custody admission and separate E/H/G/F/installed-SDK preservation *before* any storage/Unity. Strict original S custody stays **Blocked** with four original installed native roots Missing. Any new missing/restored/changed file or unreadable manifest blocks I.

Only after complete source and historical data checks and an independently **Admitted** diagnostic-only storage wrapper may **one** distinct executing storage wrapper attempt run the unmodified 14-cell / three-build / four-Player matrix. The wrapper re-admits storage under original threshold `max(64 GiB, 2×retained Q + 20 GiB)` and 20 GiB floor. Execute at most once; preserve full raw logs/receipts/first failure and independent after audits even on failure where possible. No fifth Player, modified native guard, change of TMPDIR, old app/SDK reuse, retry, historical rewrite or early H2/X02/M08A advancement. I is only an attempt letter, **not a Human Review Gate**.

E remains **FAIL** (three ON SIGSEGV, first cause Unavailable), F-COMP remains **PrerequisiteBlocked**, G is **Passed compile-only**, H stays **PrerequisiteBlocked**, original strict S custody stays **Blocked** and independent R03 full-stage review stays **FAIL** (re-review NotRun). Genuine engine-originated reporting after an uncaught exception, captured-generic/initializer, IR-R03-01 and broader acceptance are **not** proved by the four-Player I run, even if focused I passes. `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled.
