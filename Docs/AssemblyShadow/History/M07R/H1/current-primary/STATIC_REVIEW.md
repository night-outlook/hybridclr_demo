# Static Review — Formal Pilot Verification Seal

## Verdict

**PASS for Primary → Local Validation handoff**, subject to Local execution of one strict pilot seal and all formal pairs.

Reviewed build-input/tool source anchor: `01cdd033665400eba9fa0533fe17c12f9da92746`.

## Returned issue

The prior formal driver used `_successful_pilots` during every formal admission. That function called `_verify_prior_launch` for A/B across all four successful pilots, which invokes `r00_results.verify_suite`. The same immutable graph was therefore fully re-collected and re-hashed before every formal pair.

The observed 47:39 pre-launch run confirms this is not a theoretical cost.

## Review of repair

The repair preserves the strict-verification boundary rather than removing it.

- Deep verification still occurs once for all eight pilot sides.
- The seal is created only after the latest retained attempt for every pilot mode is Passed.
- The immutable file set comes from launch receipts whose complete input inventory is itself checked by deep verification.
- Pre/post filesystem identity stability closes the race between deep verification and sealing without a second full content-hash pass.
- Formal reuse is content-bound to protocol/schedule/map/launch receipts/verifier code and identity-bound to every sealed immutable file.
- A guard mismatch is a hard failure requiring reseal; it is not an automatic cache miss.
- The cache cannot change across cumulative formal indexes.
- Final paired analysis is untouched and still performs full strict evidence reconstruction.

Using device/inode/ctime in addition to size/mtime is deliberate: an in-place rewrite or file replacement that attempts to preserve common timestamp/size fields still invalidates the seal on the target Local filesystem.

## Regression review

The bounded regression models the exact operational requirement: one seal causes eight deep validations; forty later admissions cause zero deep validations. Six mutation classes independently fail closed.

## Reuse boundary

The new source changes only performance admission orchestration, sealing, tests, CI enrollment, and documentation. It does not change the already-built Player graphs or the preregistered measurement contract.

Local must independently verify that scope and all retained hashes before reusing the existing graph/map/preregistration/pilot evidence.

## Residual empirical requirements

- run the strict sealer against retained real pilot evidence;
- measure seal completion and cached admission cost;
- run 40 formal pairs;
- retain retries/failures unchanged;
- run the unchanged final analyzer;
- rerun/close complete Python and EditMode inventories after required generated prerequisites are present;
- authenticate a new checkpoint;
- V05 and independent M08 only after V04 closure.

H1 remains `InProgress`. Do not begin R02.
