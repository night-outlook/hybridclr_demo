# Local Validation → Primary Implementation

## Resolved boundary repairs

Both previously reported controlled-workflow blockers are resolved and fresh Local-validated at candidate checkout `4424a920b7d25880eb78aa2e0d9b0cd9662dff84`, source anchor `69130bbb3a6df516916dddb5ad263799a7c6e5e3`.

- Protected profile-1 and current profile-2 each completed Native ON and Native OFF controlled Development IL2CPP builds.
- Every controlled stage restored both `Assets/HybridCLRGenerate/link.xml` and `ProjectSettings/ProjectSettings.asset` to exact original bytes before the next authority guard.
- Current Native ON/OFF provenance records `verificationEnvironmentScope=NativeOnlyWithoutOuterM07WorkflowAuthority`, verifier exit 0, and complete provenance.
- All post-Player outer M07 authority checks passed.
- Old-Player rejection, strict build-map freeze, preregistration, and all four pilot pairs passed.

Evidence is retained at `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/`.

## New blocker: formal driver repeats full pilot graph verification per pair

### Symptom

The first formal invocation remained CPU-active for 47 minutes 39 seconds before creating any formal pair output root or launching either Player. It was still inside `_successful_pilots`, which calls `_verify_prior_launch` and `r00_results.verify_suite` for all four successful pilot pairs on every formal invocation.

Each pilot side graph binds 16,876–16,889 files and about 0.696–0.697 GiB. One formal precondition therefore re-collects and re-hashes eight complete graphs before sampling. Repeating that path for forty formal pairs projects beyond a bounded Local batch and grows the total validation cost without adding a new pilot identity.

The outer verifier was terminated before formal launch. No formal output directory or Player process existed, and no child remained. Formal state is `Unavailable`, not Failed and not Passed.

### Evidence

- Formal blocker diagnostic: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/V04/performance/formal-01-prelaunch-operational-blocker.log`
- Cumulative four-pilot index: `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260921-authority6913-v04-boundary/V04/performance/pilot-sample-index.json`
- Bound protocol/schedule/map and archive: same checkpoint.

### Durable implementation direction

Add an authenticated pilot-verification receipt or content-addressed verification cache that is created only after all four pilot launch receipts pass strict reconstruction. Bind it to the protocol, schedule, build map, verifier implementation, every pilot launch receipt hash, and the complete immutable input inventory. Each formal invocation may then verify that compact receipt and current immutable bindings instead of re-running all eight full pilot graph scans. The optimization must fail closed on any changed path/hash/tool and must not relax whole-pair retry, ordering, or final analyzer requirements.

Add a process-level regression that proves forty formal driver admissions do not re-scan the unchanged pilot graph while still rejecting any mutated pilot receipt, bound artifact, build map, protocol, schedule, or verifier.

## Remaining validation

After the driver optimization, retain the current graph/map/preregistration only if the new source-scope audit proves the change is strictly orchestration/verifier caching and all bound artifact hashes remain unchanged. Otherwise restart fresh V00 and rebuild. Run all forty formal pairs, final analysis, and checkpoint authentication. Proceed to V05/M08 only if those mandatory results pass.

H1 remains `InProgress`; last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.
