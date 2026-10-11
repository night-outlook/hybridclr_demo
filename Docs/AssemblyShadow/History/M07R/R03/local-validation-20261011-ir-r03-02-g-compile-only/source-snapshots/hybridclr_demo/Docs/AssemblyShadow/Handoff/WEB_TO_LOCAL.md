# Primary Implementation → Local Validation — G-COMP compilation ONLY

**Authorize one fresh G-COMP prerequisite/managed/native SDK compilation attempt. No Unity process, Test Runner, IL2CPP Player build, Player or runtime scheduler.** This supersedes the consumed F-COMP assignment. F-COMP remains PrerequisiteBlocked; E remains FAIL. Do not retry either or reuse their roots.

## Read first

1. `Docs/AssemblyShadow/README.md`, `Plan/CURRENT_STATUS.md`, this handoff.
2. Local-owned [LOCAL_VALIDATION.md](LOCAL_VALIDATION.md) and [RETURN_TO_WEB.md](RETURN_TO_WEB.md); [immutable F-COMP checkpoint](../History/M07R/R03/local-validation-20261010-ir-r03-02-f-compile-only/README.md).
3. [IR-LOCAL-COMPILE-01 correction](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/README.md), [source-bound CI and raw logs](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/CI_EVIDENCE.json), **[G-COMP full ordered procedure](../History/M07R/R03/IR_Remediation/IR_LOCAL_COMPILE_01_2026-10-11/G_COMPILE_ONLY_PROCEDURE.md)**.
4. Original C custody policy, E runtime return, R03 design/plans and HUMAN_REVIEW_GATES. The earlier F compile/runtime procedures are not execution authorization.

## Objective and source authority

Verify the repaired scratch test fixture and complete the outstanding official Unity 2022.3.62f2 managed/native SDK compilation against the current pinned sources. The repair is test-only: canonicalize the owned TemporaryDirectory root and run the same ten original controls under both default and guaranteed aliased parents. Production `checked_sdk_scratch`, compiler scripts, source-pins, C# Player, native sources, fixtures and custody/storage guards are unchanged.

All repositories use branch `codex/assembly-shadow-r01b-h1` and canonical `night-outlook/<repo>` HTTPS/SSH remotes. Check each owning checkout independently: actual top, branch, clean worktree, HEAD, origin, worktrees/submodules, ancestry and fresh remote HEAD. Any mismatch blocks; no reset/stash/clean, forced update or silent adoption of a new source tuple.

| Repository | Exact owning local path | Source binding |
| --- | --- | --- |
| night-outlook/hybridclr_demo | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo | Executable/test source `e36ab83b969f8ba8f9f4cc21fc8bb6c447d7fa2f`; final documentation-publication HEAD must equal the exact latest pushed SHA in the final Primary prompt and differ only under Docs/AssemblyShadow |
| night-outlook/hybridclr | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr | `4b2774b066cfc6afd77a8c8aded6bda7ea574f55` |
| night-outlook/hybridclr_unity | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity | `948c0e3b4f8891481301770115e8ba4945eea6de` |
| night-outlook/il2cpp_plus | /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus | `c386cdd1e8942561f1d1e1fada52d21ca524f174` |

The final prompt pins transport HEAD, while e36 is the tested source anchor; do not check out the older anchor in place of final docs. Demo source-pins.json must bind the exact three non-demo SHAs above. Test blob `5e58c14b5147ee591dda34d802f78b98d36cbaf7`, SHA-256 `dfbef375899856b3026584b81524228b53d458de7c0e85e7183f5a0249f05de2`; unchanged native_validation.py blob `15282b61dda3f61106913ce9e2973cc87d76c23d`, SHA-256 `bbe544b49d89325f40305045248295caf59ec01e98440ae184d4efbd08729428`.

## Confirmed results, not acceptance

[Scratch CI 38123748124](https://github.com/night-outlook/hybridclr_demo/actions/runs/38123748124) at e36 passed **20/20 on macos-14 and 20/20 on ubuntu-24.04**, no failures/errors/skips. Both ZIPs and source/log digests were authenticated and full raw logs retained in the correction directory. All original ten controls are unchanged; the alias cohort explicitly verifies it received a noncanonical temp parent before the fixture resolves its owned root. No environment TMPDIR/global tempfile changes or platform skips.

F-COMP's original ten-test result remains **3 Passed / 5 failures / 2 errors**. Subsequent native host/policy, official managed compile and all 55 native configurations are **NotRun**. Before admission census NotRun; independent after census stable (339,367 survivors/77,477 missing/zero problems). Installed SDK preservation Passed (2,113 files). No SDK copy, Unity or Player launch occurred. Original reports at `a9483a6e2212701cfedcf93faeb0e71ce82b73ca` must remain unchanged.

The new CI closes a fixture defect, not native/managed compilation or runtime correctness. Prior native host CI is reused-attributed evidence, not a substitute for G's required fresh host checks. Earlier official compiler and download failures retain their recorded outcomes. G is not authorized to change expectations or source to force success.

## New single-use roots and installed SDK

Under `/Users/ah/GitHub/hybridclr/r03-local-validation`, prove all four paths are absent, canonical, nonsymlinked and nonaliasing with source, installed SDK, peers and every protected/consumed history before creating only preflight:

- `Preflight-R03IRCompile-20261011G-canonical-temp`
- `ManagedAPI-R03IRCompile-20261011G-canonical-temp`
- `NativeSDK-R03IRCompile-20261011G-canonical-temp`
- `Scratch-R03IRCompile-20261011G-canonical-temp`

Do not reuse F-COMP's unused compiler destinations or any F runtime root. An occupied/aliased candidate blocks; no alternate name or TMPDIR workaround.

Installed official Unity path, **reference only, never execute**: `/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity`. Python 3.14 and existing official compiler/Apple clang arm64 profile. Capture SDK/compiler version, full before inventory and read-only after preservation. No Unity 6000 substitution, installation changes or copying beside installed Unity. Vendor SDK copy goes only into the explicit external `--sdk-scratch`; keep it out of Git evidence.

## Required ordered validation

Follow the full G procedure. Stop at any failed prerequisite, preserve partial state and classify later steps NotRun. Do not retry tests, compiler invocations or partial roots.

1. Exact source/remote/SDK/unused-root checks and immutable C/E/F authentication.
2. Fresh **20** scratch tests, zero failures/errors/skips, with unchanged inherited environment. Then native reporting normal/sanitized, real Object.h access, native observer normal/sanitized, and **69** standalone policy checks. Record every command and raw output separately.
3. Complete original-C before-custody audit to a new receipt: require exit0, completeScan, ScopedHistoricalLossStable, originalExpectedFiles=416844, presentVerified=339367, historicalStillMissing=77477 and zero problems. Strict custody remains Blocked. No new loss, changed bytes, symlinks or unexpected restorations; never rebaseline.
4. One official managed compiler-script invocation, preserving current Player/package/helper/reference hashes, actual results and the expected historical unsigned-count negative control. Unexpected failure blocks native compilation.
5. One native compiler-script invocation with new NativeSDK and external Scratch. Verify **11 units × 5 profiles = 55** actual syntax-only compilations if the script completes; include engine observer and R03 native overlay. Preserve actual first error, completed and NotRun configurations. No disabled guards/access-check workaround.
6. Independent full after-custody and installed SDK/compiler preservation audit, including after an earlier failure where feasible. A successful after audit cannot replace an unrun before admission.
7. Publish Local-owned reports plus additive `Docs/AssemblyShadow/History/M07R/R03/local-validation-20261011-ir-r03-02-g-compile-only/`, commit/push/read back all four HEADs, and STOP/return to Primary.

The compiler commands, executed separately and conditionally after gates 1–3, are:

~~~bash
PY=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
W=/Users/ah/GitHub/hybridclr/assembly_shadow_h1r
BASE=/Users/ah/GitHub/hybridclr/r03-local-validation
UNITY=/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/build_api.py" \
 --workspace "$W" --unity "$UNITY" --output "$BASE/ManagedAPI-R03IRCompile-20261011G-canonical-temp"
"$PY" -B "$W/hybridclr_demo/Tools/AssemblyShadow/R03/native_validation.py" \
 --workspace "$W" --unity "$UNITY" --output "$BASE/NativeSDK-R03IRCompile-20261011G-canonical-temp" \
 --sdk-scratch "$BASE/Scratch-R03IRCompile-20261011G-canonical-temp"
~~~

Expected evidence: exact source/pin/SDK inventories, root checks, 20-test log, each native host result, actual managed/native compiler argv/cwd/clocks/exits/logs/output hashes, complete per-target states, custody-before/after and installed-SDK preservation, additive manifest and publication receipt. Upload only permitted metadata/logs/receipts, not vendor SDK/compiler binaries or unrelated user data.

## Stop conditions and preserved history

Compile success returns to Primary; it grants no runtime permission. Never edit the test/production guard, change TMPDIR, regenerate historical inputs, clean protected roots, or resume F/E. Record unrun stages honestly; no fabricated compiler errors, warning counts, ledger or runtime seal.

Historical strict custody stays Blocked and four original S native roots Missing. E stays FAIL (three ON SIGSEGV, OFF Passed); original first error and ON semantic proofs Unavailable. Preserve S/R/Q/P/O/N/A/B/C/D/E/F. Independent R03 review FAIL/re-review NotRun; `R03Accepted=false`, `H2Passed=false`, `qualificationApproved=false`, `ReadyForHumanReviewGate=false`, `fullLegacyRegressionAcceptance=false`; PureInterpreter expansion disabled. No H2/X02/M08A, runtime batch or Human Review Gate approval.
