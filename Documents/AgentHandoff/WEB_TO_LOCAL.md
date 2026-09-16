# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the managed-cache response-scope repair.

Authoritative candidate demo source / implementation anchor:

`5f561abdfbe020d1d480594a2130c5ec846c0e6a`

Repository / branch:

`night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1`

Local Validation return commit `dc9116a46097739b634c791ac7213f431b54af22` proved the previous retention repair and fresh native provenance path, then failed closed in managed verification because schema 2 required every response file from every Csc action in the Bee DAG to remain unchanged. The committed Local census showed seven unrelated `StandaloneOSX_CodeGen/*.rsp` files changed during normal staging while both required cached managed actions retained unchanged recursive response closures, dependencies, outputs, reachability and exact fresh Player bindings.

Primary repaired that ownership boundary. New captures use managed provenance **schema 3**. Response stability now follows each selected required compiler action's exact recursive `@response` closure. Unrelated DAG response paths are audit-only. No other cache acceptance rule was relaxed.

Run fresh **V00–V05**. H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. **Do not begin R02.**

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Documents/AgentHandoff/source-targets.json`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-3695905/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/managed-response-scope-primary-20260915/`

Git is the handoff authority. Preserve all prior evidence and attempts. Do not apply chat ZIPs or unpublished patches.

## Source targets

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate demo source / implementation | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `5f561abdfbe020d1d480594a2130c5ec846c0e6a` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Reproduction demo published head — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction demo code anchor | same branch | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. `ProjectSettings/AssemblyShadowSourcePins.json` and `source-targets.json` both pin candidate source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a`. The fetched branch HEAD is expected to be a later metadata-only handoff successor; record both checkout HEAD and source anchor.

## Implementation

### Schema-3 action-local response ownership

The changed-graph proof remains preferred whenever exactly one changed managed action chain reaches a required fresh Player input. The cache route is considered only when no direct changed chain exists for that required assembly.

For a schema-3 cached candidate, begin capture still retains the exact Bee DAG, action hash/transcript, source set, compiler/tool/reference dependencies, Csc output and bounded downstream DLL closure. The difference is response ownership:

1. the graph is scanned under the existing bounded response parser;
2. `csc_arguments()` expands the selected compiler action recursively through `@response` and records its exact `responseSources`;
3. only those response bytes are retained as that compilation's `responseFiles`;
4. graph-wide discovered response paths may be recorded as `responseAuditSources`, but they are not stability requirements unless also owned by the selected action;
5. verification requires exact membership equality between that compilation's `responseSources` and `responseFiles`, independently reparses the action from retained response bytes, and requires every owned direct/nested response to remain unchanged.

Therefore a legitimate mutation of an unrelated CodeGen response does not invalidate either required cached chain, but any mutation of a direct or recursively nested response used by a required action still fails closed.

### Preserved fail-closed requirements

For each required assembly, cache acceptance still requires all of the following:

- retained Bee graph identity unchanged;
- exact Csc action SHA and independently reparsed transcript;
- exact required source set and Player defines; no `UNITY_EDITOR` output;
- exact compiler/tool/reference dependency closure, all unchanged;
- Csc output existed at begin, is retained, unchanged and at the same output path;
- bounded downstream DLL closure retained and unchanged;
- graph reachability from Csc output to the exact fresh Player input path;
- exact fresh Player input path, SHA-256 and size;
- at most one changed-action chain and exactly one accepted chain per required assembly;
- existing cache limits: 64 graphs, 128 MiB/graph, 4096 observations, 64 MiB/file, 512 MiB aggregate unique bytes, 128 reachable DLLs;
- `freshCompilerExecutionClaim=false` for a cache hit;
- no implicit fallback to legacy `--reuse-proof`.

Existing schema-1/2 historical evidence remains readable. Schema-2 evidence keeps its historical semantics; it is not retroactively reinterpreted as schema 3.

### Primary review and bounded validation

Primary source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` passed workflow run `35066118142` with **283/283** bounded tests and zero nonpasses.

Artifact ID: `10434108589`  
Artifact ZIP SHA-256: `94e4cfc61b62dd01c297a704f97085d1031e56e29986cc281eb6679ccafb1ded`.

The two new adversarial regressions prove the intended boundary:

- an unrelated Csc response in the same DAG changes after begin and both required cached chains remain valid;
- a nested response inside a required action's recursive closure changes after begin and verification rejects.

Existing negative coverage for stale output, ambiguous actions, changed source, changed required response, changed dependency, wrong fresh Player path and output created only after begin remains active.

This is bounded Primary/tool evidence only. It is not macOS Unity/Apple Player acceptance, V02/V03 completion, M08 PASS or human approval.

## Local validation

### V00 — authoritative preflight

1. `git pull --ff-only origin codex/assembly-shadow-r01b-h1`.
2. Record origin, branch, checkout HEAD and dirty/untracked state without reset/clean/stash-away of evidence.
3. Confirm pins/targets resolve to source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` and all protected identities above.
4. Run the committed candidate handoff preflight into a new absolute evidence path.

Expected source status remains `SourceTargetVerifiedNotBuildAccepted`; gate flags remain false. If V00 fails, stop before V01–V05.

### V01 — affected source/tool/Unity regression

Run the full H1 Python inventory and exact Bee Primary suite, with explicit coverage of `test_h1_managed_provenance`, `test_h1_managed_cache_provenance`, compiler/native provenance, retention/store verification, PCH provenance, handoff, selection, successor and affected M02-owner tests.

Compile candidate and reproduction in Unity and run focused affected Editor tests. Preserve exact IDs, logs, XML, failures and skips. Primary 283/283 is supporting evidence only.

### V02 — real normal-cache action-local proof

This is the key repair validation.

- Preserve the normal Bee cache. **Do not clear it merely to force Csc/ILPP recompilation.**
- Execute a fresh candidate ON/Debug smoke through the managed provenance wrapper.
- Require fresh managed begin/capture/proof schema 3.
- For both `AssemblyShadowDemo.Bootstrap` and `AssemblyShadow.R01BDiagnostics`, inspect the selected compilation's `responseSources` and retained `responseFiles`; membership must be exact and recursively complete.
- Confirm the previously observed unrelated `StandaloneOSX_CodeGen/*.rsp` class of staging changes can occur without becoming acceptance inputs unless a changed path is actually in the selected required action's recursive closure.
- Confirm every response that *is* in either required action's direct/nested closure is `Unchanged`; any mutation remains a hard failure.
- Require all preserved graph/action/dependency/output/reachability/uniqueness controls and exact fresh Player input path + SHA-256 + size binding.
- A legitimate unchanged reuse must emit `evidenceMode=BeeCacheHitBoundToFreshPlayerInput` with `freshCompilerExecutionClaim=false`.
- If Bee genuinely recompiles an assembly and produces one valid changed graph, `ChangedBeeGraphBoundToFreshPlayerInput` remains valid for that assembly; record the route, do not force cache/recompile behavior.
- **Do not use `--reuse-proof`** to satisfy this current-build cache requirement.

If the real Bee action has an unsupported response/dependency/ILPP structure, retain the full graph/action/response census and return to Primary. Do not broaden acceptance locally.

### V03 — fresh provenance-bound build set

After V02 passes, execute fresh candidate ON/OFF × Debug/Release and reproduction ON Debug/Release in new immutable roots through the established strict flow.

Each accepted build still requires native compiler/PCH/store provenance, managed provenance, exact fresh Player input binding, build/input receipt consistency and exact restoration. Record the managed evidence mode for both required assemblies in every build. Preserve all failures.

### V04 — runtime/count/startup/capacity/performance chain

Run the established current R01B chain, including 132 candidate count cells, 8 unfixed reproduction cells, fresh baseline/fixtures/replay, 11 startup modes, 8192/8193 lifetime-capacity boundary, lazy/dense/generic/array/reflection/FieldRVA/old-Player coverage and affected M03–M07 checks.

Run controlled Development performance only against the preserved performance reference on common supported workloads. Do not infer unsupported Release/P99/device-RAM conclusions.

### V05 — successor package and independent whole-chain M08

Build the successor archive/index only from explicit fresh evidence locations. Include raw managed begin/end/cache graph/action/action-local response/dependency/output observations and final managed verification, plus required native/PCH/store/runtime evidence.

Authenticate archive/index bytes and membership, run strict semantic verifiers, then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review.

A tooling, CI, V02 or V03 PASS is **not** M08 PASS. Only a genuine independent whole-chain M08 PASS may make the package Ready for Human Review Gate. Then stop for explicit human H1 approval.

Commit new Local checkpoints/raw evidence under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`. Update/push Local-owned `LOCAL_VALIDATION.md`; return nontrivial issues through `RETURN_TO_WEB.md`.

## Failure evidence

On any managed-cache failure retain the exact checkout/source anchor/pins, build GUID/input snapshot, begin/end managed captures, exact fresh Player inputs, retained Bee DAG bytes/hash, selected Csc action/transcript, per-action recursive response closure, dependency/tool bytes/hashes, Csc output, downstream DLLs, end observations and verifier error/output. Distinguish unrelated audit-only responses from selected action-owned responses.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Preserve all earlier Local checkpoints and historical v6–v11 evidence unchanged.

## Alternatives

Do not bypass V00, clear Bee cache merely to force recompilation, use legacy `--reuse-proof` as a substitute for the current-build cache proof, broaden response/source/dependency allowlists, or relax any native/PCH/managed provenance requirement. If the real Bee graph exposes a legitimate structure outside the reviewed schema-3 contract, preserve the full evidence and return it to Primary for a reviewed successor.

## Risks

The schema-3 implementation has not yet received fresh macOS Unity/Player validation under this handoff because the preceding Local cycle stopped at V00 on the literal-heading contract. Primary's 283/283 result remains bounded tooling evidence only. Fresh V00–V05 must therefore establish the real action-local response behavior, full build/runtime evidence, and independent whole-chain M08 without promoting historical results to the new handoff.

## Local correction boundary

Local may correct machine-specific paths, executable permissions, invocation syntax, fresh output-directory choices, isolated test harness setup and already-documented exact generated-file restoration after preserving before/after bytes.

Local must not change response ownership rules, source selection, dependency/reachability semantics, cache limits, reuse semantics, retention/native/PCH provenance, witness rules, count behavior, ABI/architecture or performance methodology. Return such issues to Primary regardless of diff size.

Do not rewrite this `WEB_TO_LOCAL.md` during Local Validation.

## Human review gate

H1 is still **InProgress / BlockedPendingFreshV00ToV05**. Last independent M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`.

**Do not begin R02.**