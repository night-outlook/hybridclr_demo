# IR-LOCAL-INVENTORY-01 — L test-owned inventory root correction

**Owner:** Primary Implementation. **Date:** 2026-10-13 UTC. **Status:** Source/host correction **Passed**; one fresh **M** Local Validation attempt is conditional. **L was consumed and is permanently `PrerequisiteBlocked`**, not an executed runtime failure. M's runtime has not run.

## Original L return and causality

Local L executed demo `fe783e101f53b2799c278ad5a1cc5a73cc9e1ad9` with pinned HybridCLR `4b2774b066cfc6afd77a8c8aded6bda7ea574f55`, package `948c0e3b4f8891481301770115e8ba4945eea6de`, native `c1a6876a3801a8343123977a0e230558904fd94d`; report publication `329040279d18aa053e3af23b962e608b34c6b01f`. At the first prescribed R03 host suite, `test_batch_contract.EvidenceContracts.test_complete_file_inventory` failed before its positive exact-inventory/hash assertions. **203 tests: 202 Passed, zero Failed, one Error, zero skipped**. On the Local Mac, `Path(temporary)` under `/var/folders/...` was noncanonical: `/var` is a symlink to `private/var`. Production `build_provenance.canonical_path` correctly rejected that ancestor. This is a synthetic fixture premise error, **not** reason to relax production symlink guards.

All dependent host suites, **full before** original C custody, both official compiler gates, storage and all **18 runtime cells/three builds/five Players** were **NotRun**. No Unity/Player launched, no batch/seal produced. Independent after-only original C custody still verified **339,367 surviving original SHA-matched files and 77,477 unchanged missing identities of 416,844**, zero problems, `ScopedHistoricalLossStable`. **After-only does not substitute for L's missing before-admission scan**. Historical strict S custody remains `Blocked`, with four old installed native roots missing. Original L checkpoint and Local-owned `LOCAL_VALIDATION.md` / `RETURN_TO_WEB.md` are untouched.

Read [original L checkpoint](../../local-validation-l-after-k-52d9/README.md), [raw diagnosis](../../local-validation-l-after-k-52d9/preflight/FAILURE_DIAGNOSIS.json), [actual L result](../../local-validation-l-after-k-52d9/preflight/LOCAL_L_RESULT.json) and its immutable stderr/command receipts for factual attribution.

## Minimal test-only correction

Exactly one owned test source file changed: `Tools/AssemblyShadow/R03/test_batch_contract.py`:

- Positive inventory fixture canonicalizes its **own** temporary directory using `Path(temporary).resolve(strict=True)`, then constructs inventory files beneath it. Real bytes and hashes are checked, including the negative edited-content case.
- It explicitly creates an inventory **symlink-root** and requires `Linked path refused`. Production keeps rejecting aliases.
- The addition, duplicate and parent-escape negatives also canonicalize only their owned roots, first prove the positive inventory is admitted, and then assert the intended **`Exact file membership`**, **`Duplicate inventory path`**, or **`Noncanonical inventory path`** rejection instead of accepting an unrelated failure.
- All **29 original test methods** remain. Whole R03 suite still has **203 tests**. No change to `run_host_lifetime.py` expected count, `TMPDIR`, global settings, original protected path definitions, actual Player/build scripts, acceptance predicates or product runtime source.

Original test Git blob `594eb5e1598c946ccf2e1a6f8e8bfa66349141ef`; repaired blob `dc58b0ab95e1f3f5b595abfbbd04e100a41047e1`, SHA-256 `542322a4b0beb95ec8527a934920e237384ca4939122113ad5157370d933f954`. Correction source commit `bd29db408ba7a046695aea940a4e918602a76958`.

**Production inventory source is byte-identical**: `Tools/AssemblyShadow/R03/build_provenance.py`, Git blob `4a9ba7240ded6ad81bcc29ada489ed26cbc2ae50`, SHA-256 `65e1208508b232bd5ccedc0004e5c6f853055b1a2401a71ae17a56dfe04f9ed9`. No native guard, source-pin, Player, compiler, fixture DLL, custody-map or storage code was modified.

## Original cross-platform verification

[Isolated CI 38332375404](https://github.com/night-outlook/hybridclr_demo/actions/runs/38332375404) ran exact repaired test bytes at test source `be452a70e94cb69eac749db40f1b0f8d63068c03` plus a CI-only workflow. **29/29 inventory tests and 203/203 complete R03 host tests Passed on macOS14 and Ubuntu24.04**, no failures/errors/skips. I downloaded both actual Actions artifact ZIPs and authenticated their ZIP SHA-256, member sizes/content hashes, original source/test/guard Git blob bindings and logs. Exact artifact identities and all four original test-log hashes appear in [EVIDENCE.json](EVIDENCE.json). These artifacts are retention-limited and do **not** contain any protected live historical S data or Player runtime evidence.

An active-branch [CI 38332604506](https://github.com/night-outlook/hybridclr_demo/actions/runs/38332604506) independently passed 29/203 on both macOS and Ubuntu at source commit `a633a69860043a0de56d52d722290997ca6c2ee0`. Its new `.github/workflows/r03-m-inventory-contract.yml` keeps the original production-guard Git blob pinned and will detect inventory fixture regressions.

The regression verifies synthetic fixture behavior. It does **not** rehash the live 339,367 Mac surviving files, authenticate today's storage, compile changed executable sources in the official SDK, link a Player, or prove terminal exception/engine/Bee behavior.

## Fresh M scope and absolute stopping rules

Read the [M procedure](M_BATCH_PROCEDURE.md) and current [WEB_TO_LOCAL](../../../../../Handoff/WEB_TO_LOCAL.md) for **one new M preflight**, exact final four-SHA remote tuple and seven unused external roots. All current executable, native, ABI, resource and business-guard bytes remain identical to the L source anchor `fe783e101f53b2799c278ad5a1cc5a73cc9e1ad9` except the one **test fixture** and documentation/CI. Check actual Git blobs and source-pins, not ancestry alone. The historical K/I/E runtime issues are not automatically resolved by this test fix.

Fresh Local must authenticate all sources/15 original S DLLs/historical S seal, run **203 R03 +91 R03IR +25 C custody +9 retained-E +14 collector** plus prescribed native reporter/Object.h/observer/terminal-policy checks, require full C-before exact-loss audit and E/F/G/H/I/J/K/L/SDK before preservation. Only if all pass: **one** fresh official managed compilation and **one** 55-configuration native syntax matrix, then diagnostic-only storage admission, then at most one independently admitted **18-cell, three-build, five-Player** invocation. Distinct after-audits and truthful raw result classification mandatory. No resume L, source/TMPDIR workaround, cleanup, retry, sixth Player, reduced admission floor or business guard relaxation. Publish factual additive M checkpoint, stop and return.

Historic E/I/K runtime remain **FAIL**; F/H/L `PrerequisiteBlocked`; G/J historical compile-only `Passed`. Original full-stage independent R03 review **FAIL** / independent re-review `NotRun`. Real captured-generic/initializer, IR-R03-01 and full original native provenance remain open. `R03Accepted=false`; `H2Passed=false`; `qualificationApproved=false`; `ReadyForHumanReviewGate=false`; `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2, X02, M08A or Human Review Gate advancement.
