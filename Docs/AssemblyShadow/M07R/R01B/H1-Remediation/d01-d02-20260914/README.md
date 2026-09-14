# D01/D02 continuation — 2026-09-14

**Prepared source changes, not a completed runtime acceptance. Publication from this session was blocked.** Use this document only with the corresponding source delivery. No previous status or evidence file is overwritten.

## Implemented scope

D01 adds compiler-list-only metadata resolution before PDB reading, retains complete exceptions and opt-in raw input packets, preserves local-constant names/types/values/scopes across emission, and provides three replay observations: unresolved control, compiler-reference route A, and explicit resolved-enum route B. No symbols are discarded and no arbitrary non-null class constant is changed to null. The existing three-argument transformer remains available for its prior callers and for a control reproduction.

D02 changes `m02_results.py` itself to accept either the exact historical five-site domain or the exact schema-4 H1 six-site domain. It preserves the original six-site bytes/hash in manifest projections, rejects duplicate JSON keys and unauthorized variants, checks actual H1 guard runtime results, and adds a configuration-only preflight to the normal CLI. The old `h1_m02_results.install()` becomes a compatibility no-op. No normal caller needs to install an extension.

The M02 runtime probe calls the existing H1 guard probe directly, checks both configuration identities, and emits null/tamper rejection, caller-byte and resolver-event fields. The ordinary witness acquisition method and its approved fingerprints are not changed.

## Execution boundary

This session ran 50 portable tests: raw-PDB audit 20; batch runner 16; replay planner/auditor 6; source-rendering mechanics 8. These include synthetic fixtures and child-process tests; they are not Player executions. The 15 new normal M02-owner tests and 19 NUnit tests are supplied for the full local repositories and are NotRun here. There is no new whole-chain M08 review or PASS.

[Local continuation](LOCAL_CONTINUE.md) · [Remaining local validation](LOCAL_VALIDATION_TASKS.md) · [Source basis and limits](SOURCE_BASIS.md) · [Bounded review](BOUNDED_REVIEW.md)

## Executed portable checks

53 tests passed in this delivery: 20 raw Portable-PDB audit, 16 diagnostic batch, 6 replay batch, and 11 patch-rendering checks. Exact IDs/logs are in `portable-validation/validation-report.json`. The 15 normal-owner tests and 19 NUnit tests are still NotRun. Earlier 50-test logs preceded three extra payload/output-isolation renderer tests.
