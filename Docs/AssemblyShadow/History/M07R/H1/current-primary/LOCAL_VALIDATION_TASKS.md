# Local Validation Tasks — Fresh Count Closure + M08

## Authority

Source anchor:

`0388479f7073289e3505b992956a7cbe78c302ce`

Latest Local return:

`482d9d5cfe703310e8ea6d980677c73817bad774`

Fresh count contract:

`Docs/AssemblyShadow/History/M07R/H1/current-primary/COUNT_MATRIX_CLOSURE_CONTRACT.md`

Protocol:

`H1CountMatrixClosureSource038-v1`

H1 remains `InProgress`. Do not begin R02.

## Goal

Replace only the BLOCKED historical count-chain suite with fresh source-038 Launch/Raw evidence, then rerun independent M08.

Do not rerun the five already accepted reused suites.

Do not rerun V04/V05/performance.

## C00 — source authority and environment

1. Pull exact final pushed handoff HEAD.
2. Require source pin demo revision = source 038.
3. Require source 038 → final HEAD zero non-metadata paths.
4. Require committed handoff preflight = `SourceTargetVerifiedNotBuildAccepted`.
5. Verify candidate four-repository heads.
6. Locate the registered protected reproduction worktree for branch `codex/assembly-shadow-h1-count-repro`.
7. Verify it and the split validation-tooling authority against `source-targets.json`.
8. Record absolute:
   - candidate checkout;
   - reproduction checkout;
   - Unity 2022.3.62f2 executable;
   - PowerShell executable;
   - Python executable/version.
9. Require no Unity process owns candidate or reproduction project.
10. Record disk availability before execution.

If source authority differs, stop.

## C01 — fresh fixtures

Choose a new canonical run root under candidate:

`_temp/AssemblyShadow/H1CountClosure038-20260925A`

If that name already exists, use the next unused suffix and record it. Never overwrite an old attempt.

Run exactly:

~~~text
python3 Tools/AssemblyShadow/create-h1-count-fixtures.py \
  --family parameters \
  --case-set all \
  --seed 20260925 \
  --output-root <run-root>/fixtures-parameters

python3 Tools/AssemblyShadow/audit-h1-count-fixtures.py \
  --manifest <run-root>/fixtures-parameters/h1-count-fixture-manifest.json \
  --output <run-root>/fixtures-parameters/h1-count-fixture-audit.json

python3 Tools/AssemblyShadow/create-h1-count-fixtures.py \
  --family nested \
  --case-set all \
  --seed 20260925 \
  --output-root <run-root>/fixtures-nested

python3 Tools/AssemblyShadow/audit-h1-nested-fixtures.py \
  --manifest <run-root>/fixtures-nested/h1-count-fixture-manifest.json \
  --output <run-root>/fixtures-nested/h1-count-fixture-audit.json
~~~

Require both audits Passed and generator inputs unchanged.

Retain all fixture DLLs/manifests/audits.

## C02 — fresh six-build provenance batch

Run the existing tooling-only split-authority batch:

~~~text
python3 Tools/AssemblyShadow/h1_count_build_batch_tooling.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction <verified-reproduction-checkout> \
  --unity <absolute-Unity-executable> \
  --pwsh <absolute-pwsh-executable> \
  --scope all \
  --output <run-root>/builds \
  --execute
~~~

Require `BuildsAndProvenanceVerifiedNotRuntimeAccepted`.

Require exactly six rows:

- candidate/on/Debug;
- candidate/on/Release;
- candidate/off/Debug;
- candidate/off/Release;
- reproduction/on/Debug;
- reproduction/on/Release.

Require all build GUIDs unique.

Require every row's native/managed provenance verification Passed.

Require post-build exact source/project restoration and source authority unchanged.

The two reproduction builds are retained but are **not** count acceptance inputs.

## C03 — select exactly four candidate build receipts

Read:

`<run-root>/builds/batch-result.json`

Select by exact tuple, not array position:

- role=candidate, feature=on, cpp=Debug;
- role=candidate, feature=on, cpp=Release;
- role=candidate, feature=off, cpp=Debug;
- role=candidate, feature=off, cpp=Release.

Before the matrix, independently rehash all four receipt files and require they equal the batch `receiptSha256`.

Record the four paths, hashes and GUIDs in:

`C03/selected-candidate-builds.json`

## C04 — fresh 132-cell matrix

Run:

~~~text
python3 Tools/AssemblyShadow/run-h1-count-matrix-players.py \
  --project-root /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --output-root <run-root>/matrix \
  --parameter-manifest <run-root>/fixtures-parameters/h1-count-fixture-manifest.json \
  --parameter-audit <run-root>/fixtures-parameters/h1-count-fixture-audit.json \
  --nested-manifest <run-root>/fixtures-nested/h1-count-fixture-manifest.json \
  --nested-audit <run-root>/fixtures-nested/h1-count-fixture-audit.json \
  --build-on-debug <candidate-on-debug-receipt> \
  --build-on-release <candidate-on-release-receipt> \
  --build-off-debug <candidate-off-debug-receipt> \
  --build-off-release <candidate-off-release-receipt> \
  --timeout 120
~~~

Expected stdout reaches:

`[132/132] Passed ...`

and emits:

`<run-root>/matrix/result-index.json`

Do not delete any cell attempt directory.

A semantic verification failure is a real count closure failure and returns to Primary.

`--resume` is allowed only after a documented infrastructure interruption with no semantic count failure. Preserve the incomplete attempt before resume.

## C05 — strict aggregate

Run immediately while all live build/input bytes are intact:

~~~text
python3 Tools/AssemblyShadow/verify-h1-count-matrix.py \
  --result-index <run-root>/matrix/result-index.json \
  --output <run-root>/matrix-verification.json \
  --parameter-manifest <run-root>/fixtures-parameters/h1-count-fixture-manifest.json \
  --parameter-audit <run-root>/fixtures-parameters/h1-count-fixture-audit.json \
  --nested-manifest <run-root>/fixtures-nested/h1-count-fixture-manifest.json \
  --nested-audit <run-root>/fixtures-nested/h1-count-fixture-audit.json
~~~

Require:

- kind `H1CountMatrixVerification`;
- result/status `Passed`;
- cellCount=132;
- expectedCellCount=132;
- four exact candidate build tuples;
- every per-cell verifier Passed.

## C06 — explicit Launch/Raw audit

Walk all 132 canonical cells from `result-index.json`.

For each cell:

1. open its `verification.json`;
2. resolve its bound launch receipt;
3. require launch exists and SHA matches;
4. require `kind=H1CountPlayerLaunchReceipt`;
5. require `launchSucceeded=true`;
6. require `inputsUnchanged=true`;
7. require unique nonzero process ID and unique runId;
8. require build GUID is one of the four C03 builds;
9. for normal/accepted cells:
   - raw diagnostic result exists;
   - launch result SHA matches bytes;
10. for expected Shadow startup rejection:
   - authenticated early-startup result exists;
   - launch early-result SHA matches bytes;
   - no scene diagnostic result exists;
11. require verifier/raw/launch case, family, configuration and build identity agree.

Produce:

`C06/count-launch-raw-audit.json`

Required totals:

- cells=132;
- verifications=132;
- launches=132;
- semanticRawOutcomes=132;
- uniqueRunIds=132;
- missingLaunch=0;
- missingRaw=0;
- duplicateCellIds=0;
- unexpectedBuildGuids=0;
- allPassed=true.

This receipt is mandatory even though C05 already semantically verifies the same chain; it exists specifically to make the previous M08 blocker reviewable.

## C07 — evidence sealing

Before cleanup, produce regular-file SHA-256 inventories for:

- parameter fixture root;
- nested fixture root;
- build batch output root;
- complete matrix root;
- each of the four candidate build receipt roots.

Create archives with macOS copyfile metadata disabled:

~~~text
COPYFILE_DISABLE=1 /usr/bin/tar -czf <archive> -C <parent> <root-name>
~~~

Reject archive listings containing any basename beginning `._`.

Required sealed archives:

- fresh parameter/nested fixture evidence;
- complete matrix evidence;
- candidate ON Debug build root;
- candidate ON Release build root;
- candidate OFF Debug build root;
- candidate OFF Release build root.

Do not need to select the two reproduction build roots for count acceptance; retain their batch/provenance evidence separately.

For every archive record:

- canonical path;
- original root;
- SHA-256;
- size bytes;
- regular-file count;
- member count;
- inventory SHA.

Do not clean live roots before M08.

## C08 — fresh count closure receipt

Create:

`C08/fresh-count-matrix-closure.json`

Required:

- kind `H1FreshCountMatrixClosureReceipt`;
- status `PassedFreshSource038CountMatrix`;
- protocol `H1CountMatrixClosureSource038-v1`;
- source anchor 038;
- seed 20260925;
- fixture/audit bindings;
- six fresh build/provenance bindings;
- exact four selected candidate build bindings;
- C05 aggregate SHA;
- C06 Launch/Raw audit SHA;
- six archive/seal bindings;
- 132/132 cells;
- 132 launches;
- 132 semantic raws;
- all inputs unchanged;
- no missing evidence;
- `humanGatePassed=false`;
- `mayEnterR02=false`.

## C09 — whole-H1 suite closure V2

Create:

`C09/whole-h1-suite-closure-v2.json`

Required kind:

`H1WholeChainSuiteClosureV2`

Required classifications:

- count-chain = `FreshCurrentSourceExecution`;
- startup11 = `AcceptedReusedAudited`;
- failure-publication-recovery = `AcceptedReusedAudited`;
- ordinary-capacity = `AcceptedReusedAudited`;
- mixed-capacity = `AcceptedReusedAudited`;
- m07-and-native-regression = `AcceptedReusedAudited`.

Bind the five reused suites to the corrected E04 receipt from:

`local-validation-20260925-authority038-m08-re-review/`

Bind count to C08 and C05/C06.

Require zero Blocked/Rejected.

Do not rewrite the old corrected E04 receipt.

## C10 — independent M08

Only after C09 passes.

Use the established read-only reviewer:

`.codex/agents/code-gate-reviewer.toml`

Gate:

`MILESTONE`

Input must include:

- latest BLOCKED M08 review;
- C08 fresh count closure;
- C05 aggregate;
- C06 Launch/Raw audit;
- C07 archive/seal receipts;
- C09 whole-H1 closure V2;
- previous E01–E04 evidence closure;
- source-038 V05 package;
- full performance analysis.

The reviewer must explicitly revisit the count Launch/Raw finding.

Allowed verdicts:

- PASS;
- FAIL;
- BLOCKED.

PASS means only:

`ReadyForHumanReviewGate`

Keep:

- `humanGatePassed=false`;
- `mayEnterR02=false`.

Stop for explicit human H1 approval.

## Final checkpoint

Create a new immutable Local checkpoint containing C00–C10 receipts, command logs, exact stdout/stderr, archive indexes, independent review, handoff snapshots and `MANIFEST.sha256`.

Large build/matrix archives may remain outside Git, but their paths/hashes/sizes/inventories must be committed in the checkpoint and remain available through independent M08.

## Local correction boundary

Local may execute the pre-registered commands, select the exact build tuples, create hashes/inventories/archives/receipts, and rerun independent M08.

Local must not modify source, source pins, count tools, fixtures after generation, historical evidence, V05, performance evidence, or reviewer verdict.

**Do not rerun unrelated suites. Do not begin R02.**
