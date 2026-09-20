# H1 Local Validation checkpoint — authority `316894a8`

This is the authenticated pre-cleanup checkpoint for the 2026-09-20 Local batch.

- Candidate checkout: `9b4eccd0159b41b5172f7b192130eb4d4c380445`
- Candidate source: `316894a83873c46ffd3eefa57222311ae03da214`
- Candidate native/package/IL2CPP: `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` / `6be7f38bec2fa4677d24efc1a4a1294240789933`
- Protected demo/source: `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` / `f1c923cbaa814e1b63f3c5b9f8303c90616de726`
- Outcome: `ReturnRequiredAfterV04`

Fresh V00/V01 passed, including the four-label PowerShell binder, 324/324 bounded tests, and 1,076/1,076 EditMode tests. The source-scope audit matched the exact expected narrow delta, so unaffected `925e84d7...` runtime evidence is cataloged only as `ReusedAuditedFrom925e`.

The repaired label entered real Unity on both sides. Protected profile-1 built and sealed Native ON, then failed the next pinned-source guard because controlled settings restoration changed the serialized representation of `ProjectSettings/ProjectSettings.asset`. Current profile-2 failed earlier in Native ON because its provenance preprocessor inherited the outer M07 authority environment while invoking the native-only verifier with `--skip-demo-source`. Both failed attempts, exact `link.xml` and outer restoration receipts, the protected successful Native ON receipt/evidence, mutated bytes, diffs, logs, and final runtime re-verification are retained.

No Native OFF controlled Player, complete workflow graph, old-Player result, frozen map, preregistration, performance sample, V05, or M08 result exists for this cycle. No cleanup was performed.

`raw-evidence.tar.gz` retains the bounded evidence set; `artifact-index.json` records individual artifact hashes and `MANIFEST.sha256` authenticates the complete checkpoint.
