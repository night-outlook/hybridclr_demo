# R02 Primary publication sequence

Status: blocked by transport availability in the current session. Code and metadata-generation logic are supplied; no Local implementation is requested.

## Fixed bases

Candidate demo remote base: `44a115cdeb4b5ba4d75552ec7864d20d5d5ddb25` on `codex/assembly-shadow-r01b-h1`.
Candidate IL2CPP: `3981da12f2cd3ee878a04dda6f573d0ad3faeda5` on that branch.
HybridCLR: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`.
Unity package: `0ea633a2c5b936b5af69d944593c55bd2783fca9`.
Control IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933` on existing `codex/assembly-shadow-r01b`.

All identity/ref reads and source artifact downloads used the connected GitHub interface. Earlier write smoke tests in this conversation are historical operational evidence, not proof that the currently read-only operation set can write.

## Sequence — performed by Primary, not Local Validation

1. Recheck all four current refs and the exact changed-file base blobs in the delivery manifest. If any ref has moved, inspect and integrate intentionally; do not reset, force-push or overwrite concurrent work.
2. Apply the supplied code/document changes to the candidate demo branch and commit/push. Denote the resulting actual executable-source commit by C. Do not claim that the pre-existing H1 source pin proves this new code. Verify all intended file bytes against the delivery manifest. No change to the other three repositories is required by this continuation.
3. Prepare a matched control branch `codex/r02-h1-runtime-control` from exact C. This new branch is required only for the bounded controlled comparison; it is not a product feature branch. Confirm it is unused before creation. Run `prepare_metadata.py control` using C and a new absolute staging output. Commit/push **only** its generated `ProjectSettings/AssemblyShadowSourcePins.json` on that control branch. Record the actual returned control HEAD. The generated `PREPARATION.json` is a staging receipt, not a repository file to commit.
4. Run `prepare_metadata.py candidate` using C, the actual pushed control HEAD, and a new staging output. Commit its generated candidate source pins, R02 source-targets JSON and final WEB_TO_LOCAL.md. Do not commit the staging receipt. Keep the original H1 handoff source-target file and immutable historical records unchanged; R02 has its explicitly named authority file.
5. Update README/CURRENT_STATUS to `AwaitingLocalValidation` only after the publication and Primary checks succeed. These are metadata-only changes; no executable files may change after C without choosing a new source anchor and repeating source pairing.
6. Verify a **new** Primary workflow run at the final pushed candidate state. It must pass exact-source verification, all native/revision matrices, R02 Python tests, codec-owned-storage measurements, and separate .NET build/exec checks for Baseline/P01/P03. Preserve the initial failed run and the new run/artifact IDs and hashes separately.
7. Verify control/candidate common managed source graphs, source-pin consistency and all exact remote refs. Do not treat a working tree or a local-only commit as handoff authority.
8. Generate the short handoff with `prepare_metadata.py prompt` only after actual candidate/control checkouts at the final verified heads are available. Alternatively Primary may render the same format from independently verified Connector source/ref receipts. Never issue a prompt with C substituted for a later final transport HEAD or with a hypothetical commit.

## Scope of prepared metadata

The generator only writes a new staging directory; it does not perform Git writes, install runtime code, run Players or mark publication successful. Both roles use the same demo source C. Only their IL2CPP runtime pins differ. The unchanged native/package repositories have exact pins, not latest/upstream aliases.

Candidate local paths are `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/<repository>`.
Control local paths are `/Users/ah/GitHub/hybridclr/assembly_shadow_r02_control/<repository>`.
All three control runtime/package checkouts can be detached worktrees at their exact published commits; this avoids attaching one local branch to two worktrees. Candidate owning branches remain `codex/assembly-shadow-r01b-h1`.

No revision C or control HEAD is invented in this document. Their actual values must be obtained from successful publication. This is an operational dependency, not delegated design or production-code work.
