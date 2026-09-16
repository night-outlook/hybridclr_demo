# Static Review — M07 Fixed-Byte Bootstrap Repair

## Verdict

**Primary bounded review: PASS for Local Validation handoff.** This is not M08 or Human Review Gate acceptance.

## Reviewed invariants

- Protected reproduction demo remains `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` with unfixed behavior source `4e3d2035991ab5629265ac663e61bcb2ca62828b`.
- Reproduction tooling remains `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
- Candidate/reproduction native, package, IL2CPP and performance-reference pins do not move.
- Package `BootstrapIsolationRule` is unchanged.
- H1 receives no targetless bootstrap declaration and no wildcard/method-only exemption.
- Exactly two target-qualified declarations exist for `AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness`.
- The source/precompile and compiled target forms are separately exact.
- The Unity regression binds both declarations to the exact schema-4 `FixedAssemblyBytes` site, including method hash variants, operation index, provider identity and image hash/path.
- A wrong image target remains rejected by the global bootstrap validator.
- `Invoke-M07Build.ps1` snapshots both tracked mutation owners before the first Unity M07 method invocation.
- Outer recovery runs on both success and failure, preserves pre-restore bytes, restores exact original bytes, verifies SHA-256 and makes recovery failure fatal.
- Existing P05-specific restoration remains in place.
- Gate flags remain false.

## Source blast radius

Relative to Local return `d8349b3facaa5d420ec41a484854a9bba9e6c1a4`, source anchor `c8271753f489ba5a104875ee020f572b604c840e` changes only:

- `ProjectSettings/AssemblyShadowDependencies.json`
- `Tools/AssemblyShadow/Invoke-M07Build.ps1`
- `Tools/AssemblyShadow/h1_bee_primary_tests.py`
- `Tools/AssemblyShadow/tests/test_h1_m07_policy_bridge.py`
- `Assets/AssemblyShadowDemo/Tests/Editor/M07FixedByteBootstrapPolicyTests.cs`
- its `.meta`

The two temporary patch workflows used during Primary application/review were deleted before the source anchor was frozen.

## Primary checks

- generated patch `git diff --check`: PASS;
- PowerShell parser check for `Invoke-M07Build.ps1`: PASS before source publication;
- portable M07 bridge/restoration regression: PASS;
- normal authenticated Bee Primary workflow `35112630161`: **300/300 PASS**, zero nonpasses;
- artifact `10453272042`, SHA-256 `c7e01dccb9802d1ce87a0008c214b02301afb27db7c3612b73052014ff6075b5`.

## Residual risk

Primary cannot run Unity 2022.3/macOS M07 here. Local V01 must compile and execute `M07FixedByteBootstrapPolicyTests`; Local V04 must rerun the real M07 workflow. Local must also force a controlled pre-P05 M07 failure and empirically prove both tracked setting files return to their exact pre-run hashes with the recovery receipt present.

Any need to authorize another method/provider/image or add a targetless entry returns to Primary. Do not broaden locally.
