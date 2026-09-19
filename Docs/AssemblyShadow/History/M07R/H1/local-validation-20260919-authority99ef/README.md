# H1 Local Validation checkpoint — authority 99ef65db

This is the authenticated pre-cleanup checkpoint for the 2026-09-19 maximal Local batch.

- Candidate demo: `fe441e3e73f68bd1f237fe1264c93fb358004cbd`
- Candidate source: `99ef65db13341f54cf610e18453dddf197ee86e4`
- Native: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`
- Package: `0ea633a2c5b936b5af69d944593c55bd2783fca9`
- IL2CPP: `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Protected demo/source: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` / `f1c923cbaa814e1b63f3c5b9f8303c90616de726`
- Outcome: `ReturnRequiredAfterV04`

`results-summary.json` preserves evidence-state distinctions. `artifact-index.json` identifies important receipts and their hashes. `raw-evidence.tar.gz` retains the bounded logs, receipts, capsules, bindings, launch results, build evidence, and verification records. `MANIFEST.sha256` authenticates every checkpoint component.

The archive intentionally omits large reproducible compiler snapshots, copied assembly/reference trees, resource payloads, Player application bundles, and the 512 MiB corpora. Their exact identities remain bound by archived receipts and before/after maps. The live validation workspaces were not cleaned.
