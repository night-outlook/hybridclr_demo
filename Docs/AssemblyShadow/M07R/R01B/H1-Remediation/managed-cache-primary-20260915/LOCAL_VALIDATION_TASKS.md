# Local Validation Tasks — Managed Bee Cache Repair

Execute in order. `WEB_TO_LOCAL.md` is authoritative when details differ.

- **V00 — authority:** pull `codex/assembly-shadow-r01b-h1`; require source pin/target `0387feb4344bbe95fd7db524d6e0bae759adc203`; run authoritative preflight; preserve protected reproduction/performance refs.
- **V01 — regressions:** rerun H1 Python/Primary suites, managed provenance/cache tests, strict native/PCH/retention tests, normal M02 owner, Unity compile and affected Editor tests.
- **V02 — real cache mode:** without deleting Bee cache, validate both required managed assemblies against the actual unchanged Player DAG. Require begin schema 2, exact retained Csc/action/response/dependency/output closure, all accepted end observations `Unchanged`, exact fresh Player path/hash/size binding, unique chain, and `BeeCacheHitBoundToFreshPlayerInput` where cache is reused. Do not use `--reuse-proof` to close this requirement.
- **V02 negative controls:** stale output, ambiguous action, changed source/response/dependency, wrong fresh Player path and output-absent-at-begin must reject.
- **V03 — fresh builds:** reinstall/pin, verify installed runtime, run fresh candidate ON/Debug smoke first; require native provenance/store + managed proof + final receipt + strict verifier + restoration. Then complete other candidate modes and unfixed reproduction modes. Record managed evidence mode per required assembly/build.
- **V04 — project chain:** complete required count/reproduction/startup/capacity/regression and controlled Development performance evidence against the separate reference.
- **V05 — successor/M08:** package raw managed cache evidence plus native/runtime evidence, authenticate successor, run strict verifiers, then genuine independent whole-chain M08.

If real Bee uses an unsupported action/response/dependency/ILPP structure, cache proof is ambiguous/stale, or any proof bound is reached, preserve complete evidence and return to Primary. Do not change the parser, source membership, cache limits, cache-clearing acceptance strategy, prior-proof reuse semantics, native/witness rules, or performance methodology locally.

After M08 PASS, stop for explicit human H1 approval. Do not begin R02.
