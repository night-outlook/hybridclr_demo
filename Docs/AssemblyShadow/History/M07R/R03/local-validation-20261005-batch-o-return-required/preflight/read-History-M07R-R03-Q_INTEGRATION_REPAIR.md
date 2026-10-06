# R03 Q — N integration closure candidate

Primary Implementation, 2026-10-05. **LN-001–LN-004 source repairs and batch-O preparation. Fresh integrated closure, R03 acceptance and H2 remain pending.**

## Preserved Local result

N remains ReturnRequired: **90 cells, 48 Passed / 4 Failed / 38 Blocked; seal Passed**. P05 compile/restoration/finalization Passed; full Editor rosters were NotRun and 36 downstream Players were Blocked. Preserve every N and earlier state unchanged.

## Repairs

### LN-001 — exact Editor source scope

The reviewed package delta now contains the actual 13 files from base `120bb01be680cec0375002a0823552d66d34b84c` to current package `948c0e3b4f8891481301770115e8ba4945eea6de`. The source-scope preflight executes the real Git diff and binds the unchanged 754/755 name catalogs. Extra or missing package changes still fail.

### LN-002 — equivalent closed metadata revalidation

`CompiledAssemblySet` retains the verified target-framework policy used by the production loader. Reference revalidation constructs a separate complete verification domain from the exact captured source bindings and the same verified framework policy; it does not reuse mutable loaded modules. Disk hashes, source membership, descriptors and semantic sections remain checked.

The exact N UnityEngine.AnimationModule bytes reproduce the old isolated-vs-closed semantic mismatch in the types/attributes sections. The repaired closed-domain comparison passes. Fifteen fresh supervised controls cover six unchanged worlds plus type, method, attribute, primary/descriptor, assembly-identity, disposed-domain, disk mutation and disappearance cases. Historical N qualification remains Failed; this replay authorizes nothing.

### LN-003 — explicit native-codec source authority

The Python verifier no longer interprets a project-relative native pin against ambient process cwd. Completion captures an explicit codec authority context and validates repository top-level, exact commit and codec blob/hash before use. Context is threaded through production integration and early-success verification. Missing/foreign/wrong-commit/hash contexts fail; no fallback checkout is selected.

### LN-004 — canonical sidecar lookup only

Sidecar verification retains the producer's original targetLoadOrder strings but derives canonical simple-name keys consistently for report/file lookup. Canonical duplicates, order changes, foreign hashes and missing records remain failures. The five exact N sidecars now verify read-only with mapped declaration counts 18/18/19/18/18.

## Verification

Executable/CI anchor: demo `fefe846b1209d18a96c432ed0ca2222f16cda976`; package `948c0e3b4f8891481301770115e8ba4945eea6de`.

- Host workflow `37404395804`: Linux and macOS Passed.
- Pinned Unity workflow `37404395811`: Passed.
- Completion Python suite: 281/281 per host.
- Retained R03 Python: 183/183 per host.
- Reference binding: 15/15 fresh supervised cases per host and under pinned Unity Mono.
- Editor source scope: Passed against actual 13-file package delta; expected counts 754 and 755.
- Constructor contracts: 12/12 Passed.
- Captured sidecar replay: all five N reports Passed read-only.
- Qualification: 32/32; baseline/candidate graph 9/9 each; admission 35/35.
- Exact artifacts: Linux SHA-256 e1a2e43054ba98005d975384c32d0704f71dbac081ca53d6b1d9761a323a070c (1130 indexed/1131 ZIP); macOS 08e485622d94f624c59078025e29acf389d75ca4e348efac8acc460ecb8e03e0 (1130/1131); API 88b340a2c0519d2166ca52de684b77510d5e0687c88d25afef5c84c7c5b68324 (763/764). Every indexed size/hash authenticated.

No Unity Editor or Player was launched by these CI checks. Historical-input replay is not N reclassification or runtime acceptance.

## Handoff

Batch O uses an unused root and retains all 90 cells, six builds, 59 fresh Players, early 18 and both 754/755 zero-skip Editor rosters. Require fresh qualification, codec authority, all five sidecars, P01–P05 production integration, measurements and early startup. Any non-trivial failure returns to Primary.

Connector write smoke passed on all four repositories using disposable branch `codex/connector-smoke-r03-ln-20261005-2030`; delete-ref is unavailable, so those branches remain non-authoritative.
