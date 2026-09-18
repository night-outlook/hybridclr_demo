# Local Validation Tasks — V04 Repair + Protected Reference Batch

Candidate build-input source anchor:

`f15b339610c42f340c181bdfffef29bdc4a99ed3`

Latest Local checkpoint:

`f8e66d092b275173a415776f845182171c4dbc31`

The previous `af56b841...` results remain historical. Restart fresh V00; do not relabel prior build/Player receipts as current-anchor acceptance.

The goal is one maximal batch. Hard-stop only for source/provenance/shared-input corruption. Once foundations are valid, preserve isolated fresh-process functional failures and continue independent cells when the same authenticated common inputs remain valid.

## V00 — fresh authority

1. Pull the final pushed handoff HEAD.
2. Record checkout HEAD separately from source anchor `f15b339...`.
3. Require clean tracked state.
4. Run candidate `h1_handoff_preflight.py`.
5. Require `SourceTargetVerifiedNotBuildAccepted` and exact `codeCommit=f15b339...`.
6. Run reproduction-tooling preflight at `ba8fee33753a5ebc215b7a98739e343d8e05572e`.
7. Verify protected reproduction/runtime/package/IL2CPP/performance refs remain exact.

Stop on any V00 failure.

## V01 — source tests and Unity compilation

Run the complete H1 Python inventory and affected focused suites.

Primary CI reference at the source anchor:

- bounded Primary: 316/316;
- handoff: 11/11;
- early capsule: 7/7;
- early results: 19/19;
- failure pipeline: 17/17;
- lazy contract: 8/8.

Run real Unity 2022.3.62f2 compilation/tests required by the H1 matrix. In particular retain results for:

- failure fixture / failure probe compile path;
- `R01BLazyDiagnosticTests`;
- current M07 policy/authority tests.

## V02 / V03 — fresh candidate/reproduction provenance

Regenerate the required current-anchor candidate ON/OFF × Debug/Release and reproduction ON Debug/Release evidence.

Do not reuse `af56b841...` build receipts as current acceptance.

## V04.A — controlled + normal current M07

Run a fresh controlled M07 restoration case, then a separate normal M07 baseline.

Retain the complete current graph:

- `m07-build-workflow.json`;
- `m07-fixtures.json`;
- Native ON/OFF `m07-player-build.json`;
- `m07-editor-replay.json`;
- failure fixture / Q04 negative input;
- resource and restoration receipts.

Keep the graph live through all current-candidate V04 cells.

## V04.B — startup11 + M07 14/14

Generate build-bound control capsules from the fresh normal M07 graph.

Run startup11, then the complete M07 Player matrix with the matching capsule root.

Require the existing strict gates and preserve all launch/results/log evidence.

## V04.C — repaired failure/publication matrix

Run the three-mode failure/publication launcher and direct public verifier against the same current M07 graph.

The expected implementation behavior is:

1. earliest Baseline admission succeeds;
2. the late probe validates the patch through `ShadowPatchMetadataReservation.ValidateIfDeclared`;
3. validated profile version equals `M07Probe.RuntimeAbiVersion`;
4. late reservation uses that validated version;
5. Control reaches committed success;
6. Q04 reaches the intended metadata/reference failure oracle;
7. initializer mode reaches the intended post-publication initializer failure oracle;
8. strict verifier returns `Passed` for all three same-PID chains.

If the failure probe again reports unsupported metadata capability, retain the exact patch manifest/profile/report and return it to Primary.

## V04.D — current capacity/parser/index/retained coverage

Rerun the required current-anchor independent cells, including:

- 8192 / 8193 capacity boundary;
- 512 MiB mixed boundary;
- parser + FieldRVA + bounded reader + sanitizer;
- generic/array/reflection/index/cache/capability;
- retained M03-M07/R01 native/runtime coverage.

Historical `af56...` results remain comparison only.

## V04.E — deterministic dense-v2 + repaired lazy Player

Generate a **fresh** deterministic dense-v2 contract:

~~~text
python3 Tools/AssemblyShadow/create-r01b-dense-fixtures.py   --output-root <new-dense-v2-root>
~~~

Run the parser/native dense validation with that exact v2 manifest.

Generate a fresh standalone lazy fixture:

~~~text
python3 Tools/AssemblyShadow/create-r01b-lazy-fixture.py   --output-root <new-lazy-fixture-root>
~~~

Build a fresh current diagnostic Player through:

`AssemblyShadowDemo.Editor.R01BDiagnosticBuild.BuildDiagnosticPlayer`

using the current normal-M07 fixture manifest and current Native-ON receipt. Preserve the new diagnostic build receipt.

Run:

~~~text
python3 Tools/AssemblyShadow/run-r01b-lazy-player.py   --project-root <candidate>   --diagnostic-build-receipt <fresh-diagnostic-build-receipt>   --fixture-receipt <new-lazy-fixture-root>/r01b-lazy-fixture-receipt.json   --dense-manifest <new-dense-v2-root>/workload-v3-dense-adjunct-v2.json   --output-root <new-lazy-output>
~~~

Require:

- Python v2 admission succeeds;
- v2 manifest remains `historicalEvidenceReused=false`;
- both dense fixture IDs are exactly 1 and 2;
- diagnostic Player launches;
- two dense assemblies load and rows 4095/4096 execute;
- lazy operations do not create unintended extra image reservations;
- strict lazy result verification passes.

Do not reconstruct or relabel sealed-v1.

## V04.F — create/authenticate isolated protected profile-1 reference family

Use a new sibling worktree family, not the candidate working copies.

Exact protected identities:

- demo: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`;
- HybridCLR: `b22fa3d92223645c32663e4a2157eaadf8ea495e`;
- HybridCLR Unity: `b649c499385ea68490a0f652a98b732e060aeb89`;
- IL2CPP: `7967b8c7043904fcae130b294defd5ce7aa897c4`.

Preserve the layout expected by the protected source pins:

~~~text
<reference-root>/hybridclr_demo
<reference-root>/hybridclr
<reference-root>/hybridclr_unity
<reference-root>/il2cpp_plus
~~~

Use detached worktrees or equivalent isolated read-only-source checkouts. Do not move protected branches.

Before installation/build, run from the current candidate tools:

~~~text
python3 Tools/AssemblyShadow/verify-h1-protected-reference.py   --reference-demo <reference-root>/hybridclr_demo   --reference-hybridclr <reference-root>/hybridclr   --reference-hybridclr-unity <reference-root>/hybridclr_unity   --reference-il2cpp-plus <reference-root>/il2cpp_plus   --candidate-demo <candidate>   --output <new-reference-verification.json>
~~~

Require `ProtectedReferenceInputsVerifiedNotBuilt`.

Install the profile-1 runtime into the reference project using the same project-local HybridCLR installation flow already used for H1 runtime swaps. Do not install it into the candidate project.

Then require the reference project's own:

~~~text
python3 <reference-demo>/Tools/AssemblyShadow/verify-installed-runtime.py   --project <reference-demo> --expect-shadow on --json
~~~

Retain the installation receipt/inventory and re-run the protected-reference verifier after any setup that could touch tracked files.

## V04.G — fresh profile-1 M07 graph + old-Player rejection

In the authenticated reference project, run its own protected `Invoke-M07Build.ps1` with a new reference baseline ID.

Require a fresh profile-1:

- fixture manifest;
- Native-ON receipt/Player;
- Native-OFF receipt/Player;
- Editor replay receipt.

Verify the reference graph remains profile 1.

Then use the **current candidate** runner:

~~~text
python3 Tools/AssemblyShadow/run-r01b-old-player-rejection.py   --project-root <candidate>   --fixture-manifest <current-m07-fixtures>   --on-build <current-on>   --off-build <current-off>   --replay-receipt <current-replay>   --old-fixture-manifest <reference-m07-fixtures>   --old-on-build <reference-on>   --old-off-build <reference-off>   --old-replay-receipt <reference-replay>   --output-root <new-old-player-output>
~~~

Require the old Player to pass its Baseline early admission and then refuse the profile-2 current input **before Configure/Stage** for the expected embedded baseline/runtime ABI identity mismatch.

No historical old-Player receipt may substitute for this fresh graph.

## V04.H — fresh protected-reference and candidate controlled Development builds

For both side A = protected profile-1 reference and side B = current candidate:

1. start from the corresponding freshly verified normal M07 baseline/fixture/replay graph;
2. invoke that project's own `AssemblyShadowDemo.Editor.R00ControlledBuild.BuildPlayer` twice:
   - `-shadowR00Feature on`;
   - `-shadowR00Feature off`;
3. use fresh Development Player output paths;
4. use fresh `-shadowR00BuildEvidence` JSON paths;
5. preserve the generated M07 receipts and controlled build evidence.

Each controlled build must independently report:

- `result=Passed`;
- `provenanceComplete=true`;
- source pins unchanged;
- measurement sources unchanged;
- Development=true;
- IL2CPP;
- C++ Release;
- Low stripping;
- OptimizeSpeed;
- no debugging/profiler/deep profiling;
- exact Player executable/native library/native metadata/input snapshot bindings.

Do not reuse normal-M07 production Players as controlled performance Players.

## V04.I — freeze authenticated A/B build map and run preregistered performance

Use the new Primary tool:

~~~text
python3 Tools/AssemblyShadow/freeze-h1-performance-build-map.py   --side-a-project <reference-demo>   --side-a-fixture-manifest <reference-fixtures>   --side-a-replay-receipt <reference-replay>   --side-a-on-receipt <reference-controlled-on-receipt>   --side-a-on-evidence <reference-controlled-on-evidence>   --side-a-off-receipt <reference-controlled-off-receipt>   --side-a-off-evidence <reference-controlled-off-evidence>   --side-b-project <candidate>   --side-b-fixture-manifest <current-fixtures>   --side-b-replay-receipt <current-replay>   --side-b-on-receipt <candidate-controlled-on-receipt>   --side-b-on-evidence <candidate-controlled-on-evidence>   --side-b-off-receipt <candidate-controlled-off-receipt>   --side-b-off-evidence <candidate-controlled-off-evidence>   --output <new-frozen-build-map.json>
~~~

Require the freeze receipt `result=Passed` and strict `ComparabilityPassed`.

The freezer derives comparability from the authenticated evidence. Do not edit its comparability section manually.

Before sampling, bind the immutable preregistration into a fresh evidence root:

~~~text
python3 Tools/AssemblyShadow/bind-h1-performance-preregistration.py \
  --output-root <new-performance-preregistration-root>
~~~

Require the binding receipt to report:

- `result=Passed`;
- protocol bytes unchanged;
- schedule semantic fields unchanged;
- exactly 44 preregistered pairs.

This operation changes only the schedule's transport fields `protocolPath` and `protocolSha256`; pair IDs, phases and A/B order are unchanged.

Use the bound files:

- `<new-performance-preregistration-root>/performance-protocol.preregistered.json`;
- `<new-performance-preregistration-root>/performance-schedule.bound.json`.

Run `run-h1-paired-performance.py` for the required pilot pairs first. Proceed to formal pairs only under the existing pilot/source-freeze rules. Retain **all** attempts.

Analyze the final sample index using `analyze-h1-paired-performance.py`.

No latency-based deletion or selective retry is allowed.

## Retention checkpoint — mandatory before cleanup

Before deleting/consolidating any candidate or reference artifacts, authenticate a new Local checkpoint.

In addition to the normal current-candidate evidence, retain/hash-bind:

- repaired failure/publication binding/capsule/early/late results;
- fresh dense-v2 manifest + generator/tool hashes;
- lazy fixture receipt + diagnostic build receipt + lazy launch/result;
- protected-reference verifier result;
- exact four reference Git heads/source-pin bytes;
- reference installed-runtime receipt/inventory;
- reference M07 workflow/fixture/ON/OFF/replay;
- old-Player rejection evidence;
- both sides' controlled ON/OFF receipts/evidence;
- frozen performance build map + freeze receipt;
- protocol/schedule hashes;
- every paired performance attempt;
- final performance analysis.

A failed or unavailable cell retains that status. Do not reconstruct acceptance.

## V05 — successor + independent whole-chain M08

Proceed only if mandatory V04 prerequisites are complete.

Build/authenticate successor evidence and commission a genuinely independent design → source → builds → raw-evidence whole-chain M08 review.

Only genuine independent whole-chain **M08 PASS** may make H1 Ready for Human Review Gate.

Then stop for explicit human approval.

Do not begin R02.
