# Primary Implementation source review — initializer oneuse-02 admission

Date: 2026-11-05 UTC. Review owner: Primary Implementation.
This is NOT the independent full-stage R03 review and not product/runtime acceptance.

## Factual incoming evidence

Oneuse-01 remained **BLOCKED** at its mandatory Mac read-only admission;
the exact source pin was demo
`bf1e8283061fe3a94c56ea2ac9ab6445905cf738`,
evidence publication demo
`fda6c84b8cf1af336c6eedb16343e7ddc0362831`.
The recorded admission exited 2 with:
`Current R03 net8.0 fixture project source identity changed`.
The original 01 root was never created, no local runner invoked, 15
cells NotRun, Unity builds 0, Players 0 and fresh seal unavailable.
Both >=25 GiB samples and independent source/SDK/preservation checks
are only historical prerequisite facts. The original Local finding and
stdout/command SHA remain unmodified.

## Exact code correction

Review source paths at
`Tools/AssemblyShadow/R03IR/current_native_environment_admission.py`:
the previous `REQUIRED_CSPROJ_BLOB` incorrectly targeted the old
`249c47c1b453fc0cd3520173122599ca03cbe78c`.
Current reviewed project is
`1c5c8628ead41d67d94bb1846dd5bf9764620c68`; its only intentional
change adds `InitializerNativeTargetFixtures.cs` to compilation.
The correction pins that complete project plus the actual native
initializer fixture source
`da4bf2ece4999d2765ca51d4bdeecf2bc0617fd2`
and Program entry
`c8de453c03321a5b91635da7c6ed795664bcb975`.
The parser also validates unique explicit compile entries,
default-item disabling, exact net8.0, and dispatcher presence. It
does not accept arbitrary Git HEAD, relaxed glob matching, historical
old source or developer-local modifications.

The pre-existing 29 readmission contracts were retained and extended.
New `initializer_admission_contracts.py` covers exact committed
positive source, tampered/old/missing/multiplied/symlink negatives,
fresh foreign-cwd process startup of the actual initializer CLI,
and a controlled `inspect` integration where only external Mac/Git/
SDK/capacity is mocked. Actual execution of those external requirements
is still reserved for Local Validation.

## Verified source and host results

Corrected-source commit: demo
`b24e51ec074c7b3f9c7f7d86584c873f38dc2387`.
GitHub Actions finished SUCCESS on both OSes:
- [Initializer host contracts, run 42012373589](https://github.com/night-outlook/hybridclr_demo/actions/runs/42012373589):
  Ubuntu 24.04 and macOS 14 jobs Passed. Source, new admission
  regression, fresh CLI, initializer observer/writer C++11 host tests.
- [Shared current-native Local host contracts, run 42012373659](https://github.com/night-outlook/hybridclr_demo/actions/runs/42012373659):
  Ubuntu 24.04 and macOS 15 jobs Passed, including actual-source
  readmission contracts, CLI contracts, existing source/VM/host oracles.

Both workflows must still succeed at the FINAL handoff's exact pushed
documentation SHA, not solely at b24e. CI is host/source only; the
Mac's real readmission has not yet been rerun and Unity/Players are NotRun.

## Nonchanges and next action

No changes to product `hybridclr`, `hybridclr_unity`, `il2cpp_plus`, the
15-cell initializer runner, generated target fixture bytes,
the protected original S worktree, historical S/K/oneuse-01 evidence,
or stage decisions. Primary approves only a **conditional oneuse-02**
with a new absent root, two fresh >=25 GiB capacity samples, exact four
remote heads, updated strict readmission PASS, source/SDK/custody checks,
and two dual-OS exact final SHA CI successes. Failures return to Primary
without Local non-trivial implementation.

Open independent High IR-R03-01/02; captured-generic error 15,
native V2 complete diagnostics, managed shutdown, whole-VM epoch,
GC/RSS, original S full compiler/source/object/link/Player join and
RC/P/E obligations remain unproven. `R03Accepted=false`,
`H2Passed=false`, `ReadyForHumanReviewGate=false`,
`runtimeAcceptance=false`, PureInterpreter disabled.
