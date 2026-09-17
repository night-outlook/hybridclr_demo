# R01B H1 — M07 Post-ValidateCompilerInputs Authority Repair

## Status

Primary Implementation completed for the Local Validation return at:

`e053b1803b2dd94fa818714c4b79e53220f246b8`

Reviewed candidate source / implementation anchor:

`21d3d5763ce027185d2e7f777f71545d354d44ec`

Local had already established that V00–V03 and candidate count 132/132 pass. The new blocker was narrower: real `M07Build.ValidateCompilerInputs` legitimately mutates the M07 bootstrap scene and AssemblyShadow settings, then the next full installed-runtime source check rejected those intentional workflow bytes against the immutable source-anchor blobs. The same conflict blocked both the controlled-recovery path and the normal M07 workflow.

## Reconciled authority model

The generic source/runtime verifier is not weakened.

Outside the M07 outer-wrapper context, `verify-installed-runtime.py` behaves exactly as before and requires full demo-source identity.

`Invoke-M07Build.ps1` now scopes two process environment values to its own workflow lifetime:

- `H1_M07_WORKFLOW_AUTHORITY_ROOT` — the newly created outer recovery root containing exact pre-workflow snapshots;
- `H1_M07_WORKFLOW_BASELINE_ID` — the exact requested fresh `M07-Baseline-*` identity.

Before any required M07 mutation, repeated `Assert-M07PinnedInputs` checks still use the original full verifier.

After a required workflow-owned file changes, every existing recheck becomes a conjunction:

1. generic installed-runtime/native/package/source-receipt verification with only demo working-tree comparison skipped;
2. `h1_m07_workflow_authority.py`, which authenticates the demo working tree under the exact M07 mutable-state contract.

The core workflow and its repeated guard locations are unchanged.

## Exact mutable contract

Only these three paths participate:

1. `Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity`
2. `ProjectSettings/AssemblyShadowSettings.asset`
3. `ProjectSettings/EditorBuildSettings.asset`

The verifier requires their recovery-root originals to match the exact source-anchor Git blobs. It byte-verifies every other non-metadata demo build input against the source anchor and still rejects untracked/unpinned Unity code.

The first two paths are baseline-bound and must both:

- differ from their authenticated originals after `ValidateCompilerInputs`;
- contain the exact requested baseline ID.

`EditorBuildSettings.asset` may or may not differ, but it remains inside the exact three-file recovery contract.

There is no wildcard path, directory-level mutation allowance, policy bypass, or general `--skip-demo-source` acceptance. A caller attempting `--skip-demo-source` while the M07 authority context is active is rejected.

## Controlled and normal paths

### Controlled

The expected sequence is:

1. full pre-mutation source/runtime verification;
2. real Unity `M07Build.ValidateCompilerInputs`;
3. post-mutation installed-runtime + exact M07 demo authority verification;
4. explicit failure:
   `Controlled M07 failure after successful ValidateCompilerInputs for exact-byte restoration verification.`
5. outer exact-byte restoration of all three files;
6. fresh full post-recovery source authority verification by Local Validation.

### Normal

The normal no-switch path runs `Invoke-M07Build.Core.ps1` unchanged. Its existing post-validation and later `Assert-M07PinnedInputs` calls remain active under the same scoped M07 authority context, so the workflow may proceed through baseline resources, Native-ON/OFF Players, structural fixtures and replay without treating the known workflow-owned bytes as arbitrary source drift.

Any other tracked build-input mutation remains a hard failure.

## Primary bounded validation

Workflow `35195186054` at source anchor `21d3d5763ce027185d2e7f777f71545d354d44ec`:

- **311/311 Passed**
- zero nonpasses
- authenticated Apple Bee graph SHA-256: `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`
- artifact ID: `10485926242`
- artifact ZIP SHA-256: `d2486ad13ab52d41b5fcd19ce7902863c2ef8b242b1747ec9f9b1284402be9a5`

New regressions cover exact mutable backups, baseline binding, immutable-source tamper, backup tamper, partial mutation, wrong baseline, untracked code, pre/post mutation verifier dispatch, caller demo-skip rejection, controlled explicit-failure ordering, and normal core progression with repeated guards retained.

This bounded result is not real Unity M07 acceptance, runtime/performance acceptance, independent M08 PASS, or Human Review Gate approval.

## Preserved evidence and pins

The Local checkpoint `local-validation-20260917-12cf9b2` remains unchanged and retains the valid V00–V03, six-build provenance, 132/132 count, reproduction observations, actual mutation evidence and exact restoration evidence under the previous source identity.

All protected reproduction/runtime/tooling/performance pins remain unchanged. Fresh Local V00–V05 is required under the new source anchor.
