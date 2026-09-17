# Static Review — M07 Post-Validation Authority Repair

## Verdict

**PASS for Primary → Local Validation handoff.**

This is a bounded source/tool review only. It does not establish current-source Unity M07/runtime/performance acceptance, independent M08 PASS, or Human Review Gate readiness.

## Reviewed invariants

### Global source/runtime verification is not broadened

Without `H1_M07_WORKFLOW_AUTHORITY_ROOT` and `H1_M07_WORKFLOW_BASELINE_ID`, `verify-installed-runtime.py` preserves its original full verification path.

Within the scoped M07 context:

- before required mutation, the original full verifier still runs;
- after mutation, generic installed-runtime verification still checks native/package/IL2CPP repositories, install receipt/inventory/hashes, package identity, Unity/target pins and requested Shadow mode;
- demo-source skipping is only an internal half of a conjunction with `h1_m07_workflow_authority.py`;
- a caller-supplied `--skip-demo-source` is rejected.

### Mutable set is exactly three paths

No wildcard or directory allowlist exists. The only mutable paths are the three already owned by outer exact-byte recovery:

- `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`
- `ProjectSettings/AssemblyShadowSettings.asset`
- `ProjectSettings/EditorBuildSettings.asset`

Each saved original must authenticate to the corresponding source-anchor Git blob.

### Immutable demo build inputs remain exact

Every other non-metadata demo build input is byte-verified against the source anchor. Untracked build inputs and unpinned `.cs`/`.asmdef` files still fail.

`ProjectSettings/AssemblyShadowSourcePins.json` is also verified against the final committed HEAD bytes during the M07 context.

### Mutation state is not accepted merely because a path is named mutable

Both baseline-bound paths — scene and AssemblyShadow settings — must differ from their authenticated originals and contain the exact requested `M07-Baseline-*` value. Partial mutation and wrong-baseline state fail closed.

### Core workflow guards remain

`Invoke-M07Build.Core.ps1` was not modified by this repair. Its repeated `Assert-M07PinnedInputs` checks remain between real `ValidateCompilerInputs`, baseline resources, Native-ON Player, Native-OFF Player, structural work and fixture finalization.

The wrapper only scopes the M07 authority context around controlled or normal execution and restores the prior process environment afterward.

### Three-file exact restoration remains unchanged

The outer recovery still snapshots/restores the same three exact files and writes `workflow-inputs-restored.json`. No reset, clean, wildcard overwrite or extra recovery path was introduced.

## Regression coverage

The new bounded regressions prove:

- exact backups + exact baseline-bound mutation pass;
- immutable demo source tampering fails;
- backup tampering fails;
- only one required path changing fails;
- wrong baseline binding fails;
- untracked Unity code fails;
- pre-mutation M07 context still uses the full generic verifier;
- post-mutation recheck invokes runtime/native proof plus exact M07 demo authority;
- caller-provided demo-source skip is rejected;
- controlled path orders post-validation authority before its explicit controlled failure;
- normal core executes inside the scoped authority and retains repeated pin checks.

Final bounded CI at `21d3d5763ce027185d2e7f777f71545d354d44ec` is **311/311 Passed**, workflow `35195186054`, artifact `10485926242`, artifact SHA-256 `d2486ad13ab52d41b5fcd19ce7902863c2ef8b242b1747ec9f9b1284402be9a5`.

## Residual empirical requirements

Local Validation must still prove on real Unity/macOS that:

1. the controlled path reaches the explicit controlled-failure text after the post-validation authority recheck;
2. exact restoration then returns all three files to originals and full candidate preflight passes;
3. a separate normal M07 run proceeds beyond the former guard into baseline resources and completes the required Player/fixture/replay chain;
4. no additional tracked demo input needs to mutate. If one does, return to Primary rather than widening the mutable set locally.

## Gate disposition

H1 remains `InProgress / BlockedPendingFreshV00ToV05`.

Last independent whole-chain M08 remains `FAIL`.

`humanGatePassed=false`; `mayEnterR02=false`.
