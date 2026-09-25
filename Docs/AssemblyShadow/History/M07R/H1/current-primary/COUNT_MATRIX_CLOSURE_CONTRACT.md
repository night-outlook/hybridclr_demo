# H1 Fresh Count-Matrix Closure Contract

## Status and purpose

Protocol ID:

`H1CountMatrixClosureSource038-v1`

Source anchor:

`0388479f7073289e3505b992956a7cbe78c302ce`

This protocol replaces only the BLOCKED historical count-chain suite with fresh source-038 execution evidence. It does not rerun or relabel the five already accepted `ReusedAudited` suites, source-27df performance evidence, V04, or V05.

The prior independent M08 finding is specific: the selected historical 132/132 verifier reports lack the underlying per-cell launch and raw-result bytes. This protocol therefore requires complete Launch + Raw retention for every new count cell.

## Frozen inputs

- Unity: `2022.3.62f2`
- Target: `StandaloneOSX`
- Architecture: `arm64`
- Candidate demo behavior/source: `0388479f7073289e3505b992956a7cbe78c302ce`
- Candidate HybridCLR: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- Candidate HybridCLR Unity package: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- Candidate IL2CPP Plus: `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Protected reproduction branch/head and split validation tooling: exactly as recorded in `Docs/AssemblyShadow/Handoff/source-targets.json`
- Fixture seed: **20260925**
- Fixture case set: `all`
- Matrix cell count: **132**
- Per-cell timeout: **120 seconds**
- Build path: existing `h1_count_build_batch_tooling.py --scope all --execute`
- Matrix path: existing `run-h1-count-matrix-players.py`
- Aggregate verifier: existing `verify-h1-count-matrix.py`

No source/tool modification is authorized by this protocol.

## C00 — source authority

Before fixture/build work:

1. require exact final pushed handoff HEAD;
2. require source pin demo revision = source 038;
3. require source 038 → final HEAD has zero non-metadata paths;
4. require committed handoff preflight `SourceTargetVerifiedNotBuildAccepted`;
5. require candidate four-repository heads exact;
6. require protected reproduction checkout and validation-tooling identity exactly match machine authority;
7. require no Unity process owns either project;
8. record Unity executable, PowerShell executable, Python version, host and free disk.

If any source/checkout mismatch exists, stop before fixture generation.

## C01 — fresh fixture generation and independent audit

Use a new root under the candidate project, for example:

`_temp/AssemblyShadow/H1CountClosure038-20260925A/`

The actual root must be recorded and must not pre-exist.

Generate parameter fixtures:

~~~text
python3 Tools/AssemblyShadow/create-h1-count-fixtures.py \
  --family parameters \
  --case-set all \
  --seed 20260925 \
  --output-root <run-root>/fixtures-parameters
~~~

Audit:

~~~text
python3 Tools/AssemblyShadow/audit-h1-count-fixtures.py \
  --manifest <run-root>/fixtures-parameters/h1-count-fixture-manifest.json \
  --output <run-root>/fixtures-parameters/h1-count-fixture-audit.json
~~~

Generate nested fixtures:

~~~text
python3 Tools/AssemblyShadow/create-h1-count-fixtures.py \
  --family nested \
  --case-set all \
  --seed 20260925 \
  --output-root <run-root>/fixtures-nested
~~~

Audit:

~~~text
python3 Tools/AssemblyShadow/audit-h1-nested-fixtures.py \
  --manifest <run-root>/fixtures-nested/h1-count-fixture-manifest.json \
  --output <run-root>/fixtures-nested/h1-count-fixture-audit.json
~~~

Require both audits `result=Passed`, complete canonical case sets and `inputsUnchanged=true` in both generator manifests.

Do not reuse historical fixture DLLs.

## C02 — fresh provenance-bound diagnostic Players

Use the existing split-identity build batch:

~~~text
python3 Tools/AssemblyShadow/h1_count_build_batch_tooling.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction <canonical-protected-reproduction-checkout> \
  --unity <absolute-Unity-2022.3.62f2-executable> \
  --pwsh <absolute-pwsh-executable> \
  --scope all \
  --output <run-root>/builds \
  --execute
~~~

The protected reproduction checkout must be discovered from the registered worktree/branch and verified against `source-targets.json`; do not guess or move it.

Require:

- `status=BuildsAndProvenanceVerifiedNotRuntimeAccepted`;
- six fresh build rows;
- candidate:
  - ON Debug;
  - ON Release;
  - OFF Debug;
  - OFF Release;
- reproduction:
  - ON Debug;
  - ON Release;
- six unique build GUIDs;
- every selected build has native strict provenance Passed;
- every selected build has managed source provenance Passed/SourceGraphBound;
- every build restores owned source/project inputs exactly;
- post-build source authority remains unchanged.

Only the **four candidate** build receipts are matrix acceptance inputs. Reproduction builds remain diagnostic provenance evidence and do not substitute for candidate count cells.

## C03 — fresh 132-cell matrix

Extract the four candidate build receipt paths from `<run-root>/builds/batch-result.json` by exact tuple:

- `candidate/on/Debug`
- `candidate/on/Release`
- `candidate/off/Debug`
- `candidate/off/Release`

Then run:

~~~text
python3 Tools/AssemblyShadow/run-h1-count-matrix-players.py \
  --project-root /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --output-root <run-root>/matrix \
  --parameter-manifest <run-root>/fixtures-parameters/h1-count-fixture-manifest.json \
  --parameter-audit <run-root>/fixtures-parameters/h1-count-fixture-audit.json \
  --nested-manifest <run-root>/fixtures-nested/h1-count-fixture-manifest.json \
  --nested-audit <run-root>/fixtures-nested/h1-count-fixture-audit.json \
  --build-on-debug <candidate-ON-Debug-build-receipt> \
  --build-on-release <candidate-ON-Release-build-receipt> \
  --build-off-debug <candidate-OFF-Debug-build-receipt> \
  --build-off-release <candidate-OFF-Release-build-receipt> \
  --timeout 120
~~~

Normal success requires one completed process per canonical cell. Do not delete failed attempts.

`--resume` is permitted only after an infrastructure interruption with no semantic failure in the interrupted cell. Preserve the interrupted attempt and reason before resume. A semantic verification failure returns to Primary.

## C04 — independent aggregate verification

Immediately after C03, while every referenced build/input/live path is still present, run:

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

- `kind=H1CountMatrixVerification`;
- `result=Passed`;
- `status=Passed`;
- `cellCount=132`;
- `expectedCellCount=132`;
- exactly four candidate build tuples in aggregate verification;
- 132 unique cell IDs;
- 132 unique run IDs;
- no missing/duplicate launch receipts;
- no missing semantic raw evidence;
- all per-cell evidence verifiers Passed.

This aggregate is mandatory. The per-cell `verification.json` reports alone are not count closure.

## C05 — complete Launch/Raw retention

This step fixes the historical defect.

Before any cleanup, inventory the complete `<run-root>/matrix` tree.

For each of the 132 canonical cells require:

1. one `verification.json`;
2. one `h1-count-player-launch.json`;
3. exactly one semantic raw outcome selected by the launch:
   - normal/accepted cell: `h1-count-diagnostic-result.json`;
   - expected startup rejection: authenticated early-startup result referenced by `earlyResultPath`;
4. launch SHA/path equals the per-cell verifier binding;
5. raw SHA/path equals the launch receipt binding;
6. process ID and build GUID agree across launch/raw/verifier;
7. `inputsUnchanged=true`;
8. selected build receipt/hash is one of the four frozen candidate builds.

Required totals:

- canonical cells: 132;
- verification reports: 132;
- launch receipts: 132;
- semantic raw outcomes: 132;
- unique run IDs: 132;
- missing launch/raw: 0;
- duplicate cell IDs: 0;
- unexpected build GUIDs: 0.

Create:

`H1FreshCountMatrixClosureReceipt`

with status:

`PassedFreshSource038CountMatrix`

The receipt must include:

- source/handoff authority;
- fixture seed and manifest/audit hashes;
- six-build batch hash;
- four selected candidate build receipt hashes/GUIDs;
- aggregate verification hash;
- per-cell launch/raw/verifier hashes;
- exact outcome counts;
- archive/seal information below;
- `humanGatePassed=false`;
- `mayEnterR02=false`.

## C06 — immutable evidence sealing

The previous 12cf closure failed because only verifier reports were retained. Do not repeat that packaging shape.

Preserve, at minimum:

1. complete parameter fixture root;
2. complete nested fixture root;
3. complete build-batch output root;
4. complete matrix output root, including all 132 launch/raw/verifier/log directories;
5. `matrix-verification.json`;
6. the four selected candidate build receipt roots, including:
   - Player app bytes;
   - input snapshot;
   - native provenance;
   - managed source provenance;
   - build receipt.

Create regular-file SHA-256 inventories before archives.

Use macOS archival with copyfile sidecars disabled, for example:

~~~text
COPYFILE_DISABLE=1 /usr/bin/tar -czf <archive> -C <parent> <root-name>
~~~

Reject any archive member whose basename starts with `._`.

At minimum create and SHA-bind:

- matrix archive;
- fixture archive;
- one archive for each of the four selected candidate build roots.

Archives may remain outside Git if large, but their canonical paths, byte sizes, SHA-256 values, member counts and per-file inventory hashes must be committed in the Local checkpoint. Do not clean the live roots before independent M08.

## C07 — whole-H1 closure update

Do not rewrite the previous corrected E04 receipt.

Create a new receipt:

`H1WholeChainSuiteClosureV2`

Required suite classifications:

- count-chain: `FreshCurrentSourceExecution`;
- startup11: `AcceptedReusedAudited`;
- failure-publication-recovery: `AcceptedReusedAudited`;
- ordinary-capacity: `AcceptedReusedAudited`;
- mixed-capacity: `AcceptedReusedAudited`;
- m07-and-native-regression: `AcceptedReusedAudited`.

The count suite must bind `H1FreshCountMatrixClosureReceipt` and `matrix-verification.json`.

The five reused suites must bind the previously authenticated corrected E04 evidence; do not rerun them.

Require:

- six required suites supported;
- zero Blocked/Rejected;
- source-038 current count execution explicitly Fresh;
- reused suites explicitly not Fresh;
- V05 source/performance classifications unchanged.

## C08 — independent M08

Only after C07 passes, rerun the established read-only reviewer:

`.codex/agents/code-gate-reviewer.toml`

Gate:

`MILESTONE`

The review input must include:

- previous BLOCKED independent review;
- fresh count closure receipt;
- matrix aggregate verification;
- complete count archive/index receipts;
- C07 whole-H1 closure;
- existing E01–E04 historical closure receipts;
- source-038 V05 evidence;
- full performance analysis.

The reviewer must explicitly decide whether the former count Launch/Raw blocker is closed.

Allowed verdicts:

- PASS;
- FAIL;
- BLOCKED.

PASS means only:

`ReadyForHumanReviewGate`

Human approval remains separate.

## Stop rules

Stop and return to Primary if:

- source authority changes;
- fixture audit fails;
- build provenance fails;
- a matrix cell has a semantic failure;
- aggregate verification fails;
- any launch/raw semantic file is missing;
- archive/inventory sealing is incomplete;
- C07 cannot support all six suites.

Do not rerun V04/V05/performance Players.

Do not begin R02.
