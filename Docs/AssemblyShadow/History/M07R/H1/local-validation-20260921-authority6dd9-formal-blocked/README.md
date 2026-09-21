# H1 Local Validation checkpoint — authority `6dd964c0`

This is the authenticated pre-cleanup checkpoint for the 2026-09-21 retained-graph bridge and formal-admission batch.

- Candidate checkout: `1c6cdda260e2bf91e07e672aa261dcc38b3a5aa8`
- Candidate source/tool anchor: `6dd964c045034240ea53dd15ba7c0b33e9f2ad17`
- Candidate native/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Outcome: `AuthorityTestsReuseAndBridgePassed;StrictPilotSealFailedNestedPairingAuthority`

Fresh V00 passed candidate, reproduction-tooling, protected-reference, and installed-runtime authority. The candidate installed receipt was refreshed through the sanctioned Unity installation method after the source-pin advance.

Both independent source audits passed. The non-metadata delta from the previous Primary anchor and from retained graph anchor `69130bbb...` to `6dd964c0...` is exactly the reviewed 14-path set. The retained V04 checkpoint and Player-artifact manifests, the prior blocked checkpoint, the live protocol/schedule/map/pilot bindings, all eight selected launch receipts, and 33,784 unique bound files totaling 1,521,688,590 bytes all reauthenticated.

The real `H1GraphReuseBridge` passed and binds side B only, the exact 14-path transition, source-pin DTOs, frozen map, current verifier hashes, and refreshed installed-runtime receipt. Its SHA-256 is `088a338632a9d2a9970c0bc61aaa9b218b4ca93e080a1734539b68317fa1a89e`.

The one-time bridge-bound strict pilot seal failed after approximately 1104.2 seconds with `R00 baseline: source pins differ from baseline provenance`; no `H1PilotVerificationReceipt` was created. A focused read-only reproduction proved the bridge-aware outer R00 verification passes, while nested `r01_early_results._prepare()` fails identically because it calls the default current-pairing `verify_inputs` path rather than receiving the authenticated retained-graph authority. This is a Primary-side authority-propagation defect at early-capsule reconstruction, not bridge corruption or retained artifact drift.

Bounded Primary passed 348/348. Direct graph reuse, paired driver, formal batch, R01 early/failure/lazy, and both PowerShell recovery regressions passed; the first literal formal-batch test-file invocation failed before tests until the repository module path was supplied, and both states are retained. Complete Python discovery recorded 1,005 passed and 28 explicit environment skips with no failures/errors. Broad Unity EditMode passed 1,076/1,076.

`raw-evidence.tar.gz` contains the complete bounded `_temp` evidence root. `V00`, `V01`, `V02`, and `V04` expose the principal receipts and logs readably. `prior-v04` and `prior-blocked` retain the manifests authenticated during this batch. `MANIFEST.sha256` authenticates this checkpoint. No cleanup was performed.

Formal pairs, final analysis, V05, and independent M08 were not run. H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
