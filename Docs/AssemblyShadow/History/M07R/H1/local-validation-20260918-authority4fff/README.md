# H1 Local Validation checkpoint — authority 4fff4df2

This is the authenticated pre-cleanup checkpoint for the 2026-09-18 maximal Local batch.

- Candidate demo: `f480d3a6cccbbc4d3728dc0cf46ad8723f99fb53`
- Candidate source: `4fff4df26681ab3595bb241bbc972207d032831e`
- Native: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- Package: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Outcome: `ReturnRequiredAfterV04`

`results-summary.json` preserves evidence-state distinctions. `artifact-index.json` identifies the important receipts and their hashes. `raw-evidence.tar.gz` contains 5,060 retained receipt/log/input entries, including V00–V03. `MANIFEST.sha256` authenticates all checkpoint components.

The archive intentionally omits large reproducible compiler snapshots, copied assembly/reference trees, resource payloads, Player bundles, and the 512 MiB mixed corpus. Their exact identities remain bound by the archived build receipts, file inventories, and before/after maps. The live workspaces were not cleaned.
