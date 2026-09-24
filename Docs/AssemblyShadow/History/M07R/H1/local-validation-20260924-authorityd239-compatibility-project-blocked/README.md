# Local v2 historical-analysis validation return checkpoint

This checkpoint records fresh Local Validation on the pushed demo handoff
`aedf3c58c3e3f8ab612552563a29c8906b82bea1`, source anchor
`d239d9d00784ea2df22133cb8c938ec25035f5a0`, and pinned native/package
commits. It references the immutable source-27df historical execution checkpoint;
no Player, Unity, native, or IL2CPP build was run or relabeled as current.

- `V00/`: exact four-repository source authority, seven-path v2 analysis delta,
  25-path retained-graph delta, committed handoff preflight, command receipt.
- `V01/`: fresh bounded Primary 377/377 and complete 1,061-leaf Python inventory,
  1,033 Passed and 28 explicit environment Skipped, zero failures/errors,
  including the corrected positive analyzer leaf; command receipts and raw logs.
  The Python inventory tool exited 2 because its status is
  `CompletedWithNonPass` for the explicit skips; the handoff requirement is
  zero Failed/Error and explicit skips.
- `V02/`: 92/92 source-27df checkpoint manifest, four fixed live SHA-256
  bindings, 33,792 sealed files and stable-stat guards, plus direct-binding
  audits. The first generic sweep reports five mismatches because it compares
  historical Git-pinned source/tool identities to later live checkout files.
  The semantic follow-up verifies all five against their pinned Git blobs,
  leaving zero unresolved mismatches. Preserve both audit attempts.
- `V04/`: exact original live-path v2 compatibility preflight command,
  fail-closed output, and checkout-selection diagnosis. The preflight failed
  before historical analysis and before V05/M08 eligibility.

`MANIFEST.sha256` authenticates all files in this checkpoint except itself.
Verification: from this directory, run `shasum -a 256 -c MANIFEST.sha256`.
The source-27df live evidence remains at its original historical paths and
must not be replaced by checkpoint copies.
