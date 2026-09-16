# Static Review — Split Reproduction Validation Tooling

## Verdict

**Primary bounded review: PASS for Local Validation handoff.** This is not M08 or Human Review Gate acceptance.

## Reviewed invariants

- Protected reproduction branch/head remains `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`.
- Reproduction behavior/source pin remains `4e3d2035991ab5629265ac663e61bcb2ca62828b`.
- Reproduction native remains `99cdb1b67e4ed07b70732a2148cb69e079ca41cf`.
- Shared package/IL2CPP remain `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`.
- Performance reference remains `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`.
- Tooling successor is the separate branch `codex/assembly-shadow-h1-count-repro-tooling` at `0c9c2508d94a097dff50028212a01695c8e29c60`, not a rewritten reproduction head.
- Protected-head → tooling-revision non-metadata delta is exactly nine validation paths; no runtime/gameplay source is allowed.
- Complete eleven-file native+managed validation dependency set is independently bound to candidate Git blobs. `H1EvidenceProcess.cs` and `h1_compiler_actions.py` are already-identical dependencies and remain explicitly authenticated.
- Reproduction installed-runtime verification still uses protected pins; ordinary demo-source equality is replaced only after the stricter split-tree proof passes.
- Current managed provenance bridge/script is included so reproduction capture follows the reviewed schema-3 policy rather than the protected historical validation policy.
- Split identity is checked before and after every reproduction build/restoration.
- Candidate-owned strict compiler/managed verifiers remain the acceptance tools for both roles.
- `validation-tooling-binding.json` is emitted only after strict build verification and binds its exact receipt SHA.
- Diagnostic replay remains non-acceptance.
- Gate flags remain false.

## Candidate blast radius

Candidate implementation delta from Local-return head is validation infrastructure only:

- `Tools/AssemblyShadow/h1_reproduction_tooling.py`
- `Tools/AssemblyShadow/h1_count_build_batch_tooling.py`
- two focused split-tooling test modules
- bounded Primary test-runner registration

Candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669` passed workflow `35081136990`: **294/294**, zero nonpasses, artifact `10439663711`, SHA-256 `a7ad62cbd34200056448374b69f942c0cd7e9d3515bb7e499fe2d64c44d3dd7d`.

The reproduction-tooling branch changes only nine reviewed validation paths. All eleven required dependency blobs must exactly match candidate source anchor Git blobs.

## Failure modes retained

Fail closed on wrong tooling branch/revision, unexpected non-metadata delta, missing/extra override, wrong candidate blob, dirty/untracked build input, protected pin drift, behavior/published-head ancestry mismatch, install-receipt mismatch, stale managed/native validation dependency, strict provenance failure, restoration/source drift, missing frozen tooling identity, or receipt-binding failure.

## Residual risk

Primary CI cannot prove Unity 2022.3 on macOS compiles and executes the tooling successor inside the reproduction checkout. Local V00/V01 must validate the source split and Unity compilation; V03 must produce fresh reproduction build receipts plus tooling-binding sidecars. Any additional tooling dependency or required behavior/runtime modification returns to Primary.

Candidate V02/V03 evidence from `local-validation-20260916-9568ea3` remains preserved but is not current-source acceptance.
