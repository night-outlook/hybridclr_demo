# Static Review — Split Reproduction Validation Tooling

## Verdict

**Primary bounded review: PASS for Local Validation handoff.** This is not M08 or Human Review Gate acceptance.

## Reviewed invariants

- Protected reproduction branch/head remains `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`.
- Reproduction behavior/source pin remains `4e3d2035991ab5629265ac663e61bcb2ca62828b`.
- Reproduction native remains `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`.
- Shared package/IL2CPP remain `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Performance reference remains `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.
- Tooling successor is a separate branch/revision, not a rewritten reproduction head.
- Protected-head → tooling-revision non-metadata delta is exact and allowlisted; no runtime/gameplay source may appear in the override set.
- Complete required tool dependency set is independently bound to candidate Git blobs, including already-identical `h1_compiler_actions.py`.
- Reproduction installed-runtime verification still uses protected pins; only ordinary demo-source equality is replaced by the stricter split-tree proof.
- Split identity is checked before and after every reproduction build/restoration.
- Candidate-owned strict compiler/managed verifiers remain the acceptance tools for both roles.
- `validation-tooling-binding.json` is emitted only after strict build verification and binds its exact receipt SHA.
- Diagnostic replay remains non-acceptance.
- Gate flags remain false.

## Blast radius

Candidate implementation delta from Local-return head is validation infrastructure only:

- `Tools/AssemblyShadow/h1_reproduction_tooling.py`
- `Tools/AssemblyShadow/h1_count_build_batch_tooling.py`
- two focused test modules
- bounded Primary test-runner registration

The separate reproduction-tooling branch changes only six validation paths from the protected head; its seventh required tool dependency was already byte-identical.

## Failure modes retained

The flow fails closed on wrong tooling branch/revision, unexpected non-metadata diff, missing/extra override, wrong candidate blob, dirty/untracked build input, protected pin drift, behavior/published-head ancestry mismatch, install-receipt mismatch, strict provenance failure, restoration/source drift, missing frozen tooling identity, or receipt-binding failure.

## Residual risk

The candidate CI cannot prove that Unity 2022.3 on macOS compiles and executes the tooling successor correctly inside the protected reproduction checkout. Local V00/V01 must validate that source split, and V03 must produce fresh reproduction build receipts plus tooling-binding sidecars. Any need to alter behavior/runtime source or expand the tooling allowlist returns to Primary.

Candidate V02/V03 evidence from the previous Local checkpoint remains preserved but is not current-source acceptance.
