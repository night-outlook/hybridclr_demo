# Static Review — Fresh Source-038 Count Closure

## Verdict

**PASS for Primary → Local execution handoff.**

The remaining blocker is evidentiary, not a known runtime implementation defect. Existing current-source count tooling already generates and verifies the missing Launch/Raw layers.

## Why historical reuse cannot close count

The selected 12cf archive contains 132 verifier reports and one index but not the 132 referenced launch receipts or 132 raw semantic results.

The reports preserve hashes, but a reviewer cannot independently reconstruct fresh-process identity, binary selection and raw oracle semantics from report assertions alone.

The missing bytes are not in the designated checkout/archive. They must not be synthesized.

## Why old 925e builds are not selected for new launch

Current `run-h1-count-players.py` correctly requires the build receipt's `sourcePinFile` to exist inside the selected project and hash exactly to the build's frozen source-pin bytes.

The current checkout carries source-038 source-pin authority. Historical 925e build receipts bind older source-pin bytes.

Temporarily swapping the current source-pin file would weaken the authority boundary, so it is not authorized.

## Fresh execution design

Existing source-038 tooling is sufficient:

- `create-h1-count-fixtures.py`
- `audit-h1-count-fixtures.py`
- `audit-h1-nested-fixtures.py`
- `h1_count_build_batch_tooling.py`
- `run-h1-count-matrix-players.py`
- `verify-h1-count-results.py`
- `verify-h1-count-matrix.py`

No source patch is required.

### Per-cell semantics already enforced

For every matrix cell, current tooling:

- validates fixture manifest/audit bytes;
- validates selected build receipt and explicit feature/compiler flags;
- validates Player executable/native library/metadata hashes;
- independently hashes the input snapshot;
- validates native and managed provenance;
- records immutable input hashes before/after;
- launches a new process;
- records the launch receipt;
- verifies early startup for Shadow cells;
- verifies raw diagnostic result or expected startup rejection;
- requires input bytes unchanged;
- independently reopens launch/raw/build/fixture evidence in the per-cell verifier.

### Aggregate semantics already enforced

`h1_count_matrix.py` independently requires:

- the exact canonical 132-cell set;
- unique report/launch/run identities;
- exactly four shared candidate feature/config build tuples;
- shared source/runtime identity;
- live build binary hashes;
- fixture audit bindings;
- per-cell raw semantics;
- per-cell evidence verifier PASS.

Therefore the previous failure is retention/packaging, not missing verification logic.

## Retention design

The new protocol corrects packaging by preserving:

- complete matrix tree;
- 132 launch receipts;
- 132 semantic raw outcomes;
- 132 verifier reports;
- fresh fixtures/audits;
- build batch evidence;
- all four selected candidate build roots including Player/input/provenance bytes.

No cleanup occurs before independent M08.

## Scope

No source/tool change occurs, so:

- source anchor remains 038;
- existing V04/V05 remain valid;
- five accepted reused suites remain valid;
- performance evidence remains unchanged.

Only count diagnostic Player execution is newly authorized.

## Residual empirical requirements

Local must perform the fresh build/matrix execution.

Any semantic count failure returns to Primary.

Only a complete fresh count closure may make whole-H1 closure eligible for independent M08.

M08 PASS still stops at `ReadyForHumanReviewGate`.

Do not begin R02.
