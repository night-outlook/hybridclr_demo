# H1 Local Validation checkpoint — authority `24a0d3af`

This is the authenticated blocked checkpoint for the 2026-09-21 formal subprocess repair validation.

- Candidate checkout: `0733534d8112a7a0b1e05bb5d904e945b6ed24cc`
- Candidate source/tool anchor: `24a0d3af7d5b5b664d063a75d85deb4f11aa2915`
- Native/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Outcome: `AuthorityTestsAuditsEvidenceAndBridgePassed;RetainedPilotSealAdmissionBlocked`

Fresh V00/V01 passed, including 359/359 bounded Primary tests and a full Python inventory of 1,016 Passed plus 28 explicit environment skips with no failures/errors. Exact 11-path and 20-path source audits passed. The prior Unity 1,076/1,076 result and prior retained-ON 3/3 result are retained only as `ReusedAuditedFromD18`.

The retained V04/Player manifests and latest a964 blocked checkpoint authenticated. Eight selected pilot launch receipts and 33,792 bound files totaling 1,606,993,133 bytes rehashed with zero mismatches.

The new side-B-only `H1GraphReuseBridge` passed with SHA-256 `3962cdd9fbd2d81de2d1f2918bc802c9e6e10151f8ae41ec01d40d388ae76004`. The production strict seal then failed before deep verification with `Prior A diagnostic runner binding mismatch`. The retained pilot correctly records the graph-era runner hash `afc0b649...`; current runner hash is `a8de4dc1...`. The loader compares historical pilot provenance to the current runner before authenticating the bridge.

No seal or formal series was created. Neither historical a964 formal index was used. Final analysis, V05, and independent M08 remain ineligible.

`raw-evidence.tar.gz` contains the complete bounded Local evidence root. `MANIFEST.sha256` authenticates this checkpoint. No retained graph or pilot cleanup was performed.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.
