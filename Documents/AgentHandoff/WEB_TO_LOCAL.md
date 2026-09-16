# Primary Implementation → Local Validation

## Objective

Resume HybridCLR Assembly Shadow R01B H1 validation from the managed Bee cache provenance repair. The new candidate demo source/implementation anchor is `0387feb4344bbe95fd7db524d6e0bae759adc203` on `night-outlook/hybridclr_demo` branch `codex/assembly-shadow-r01b-h1`.

Local Validation commit `7f98084518054bd43e10abb603fe193612cfb321` established that the previous retention repair succeeds on the real Apple replay and fresh native provenance path, but the managed verifier rejects a legitimate unchanged Bee cache hit because it required a changed managed Bee graph. The fresh Player used the required managed DLLs, while the matching Player Csc/ILPP graph and outputs were already present before the build and remained byte-identical.

This successor adds a fail-closed current-build cache proof. It does **not** broaden managed source membership, source-domain allowlists, native provenance, ILPP acceptance, witness rules, runtime behavior, or historical evidence. Run fresh V00–V05. H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Do not begin R02.

Read first:

- `Documents/AgentHandoff/LOCAL_VALIDATION.md`
- `Documents/AgentHandoff/RETURN_TO_WEB.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-8f5bcaa/README.md`
- `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/managed-cache-primary-20260915/`

Git is the sole handoff authority. Preserve all previous evidence and attempts. Do not apply chat ZIPs or unpublished patches.

## Source targets

Machine-readable authority: `Documents/AgentHandoff/source-targets.json`.

| Role | Repository / branch | Exact identity |
| --- | --- | --- |
| Candidate demo source / implementation anchor | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-r01b-h1` | `0387feb4344bbe95fd7db524d6e0bae759adc203` |
| Candidate native | `night-outlook/hybridclr` / `codex/assembly-shadow-r01b-h1` | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` |
| Shared package | `night-outlook/hybridclr_unity` / `codex/assembly-shadow-r01b-h1` | `0ea633a2c5b936b5af69d944593c55bd2783fca9` |
| Shared IL2CPP | `night-outlook/il2cpp_plus` / `codex/assembly-shadow-r01b-h1` | `6be7f38bec2fa4677d24efc1a4a1294240789933` |
| Reproduction demo published head — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-count-repro` | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` |
| Reproduction demo code anchor | same branch | `4e3d2035991ab5629265ac663e61bcb2ca62828b` |
| Unfixed reproduction native | `night-outlook/hybridclr` / `codex/assembly-shadow-h1-count-repro` | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` |
| Performance reference — preserve | `night-outlook/hybridclr_demo` / `codex/assembly-shadow-h1-performance-reference` | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` |

Unity/target remains **2022.3.62f2 / StandaloneOSX / arm64**. `ProjectSettings/AssemblyShadowSourcePins.json` must pin candidate demo revision `0387feb4344bbe95fd7db524d6e0bae759adc203`. The fetched branch HEAD is a later metadata-only successor; record both checkout HEAD and source anchor. New auxiliary validation checkpoints/raw evidence belong under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`, not under a new `Documents/AgentHandoff/local-validation-*` directory.

## Implementation

### Managed cached-action proof

The existing direct changed-graph proof remains preferred whenever exactly one changed managed action chain reaches a required fresh Player input. The new cache route is considered only when no direct chain was found for that required assembly.

At **begin**, schema 2 now snapshots only bounded pre-existing Bee Player Csc chains whose source set exactly equals one of the two required assemblies and whose Player defines contain the requested extra defines while excluding `UNITY_EDITOR`. For each candidate it retains:

- exact Bee DAG bytes and SHA-256;
- exact Csc action hash and parsed source/dependency/output/define/response transcript;
- complete recursive response-file closure;
- compiler/tool/reference dependency bytes;
- the pre-existing Csc output DLL;
- bounded reachable downstream DLL outputs under `Library/Bee` that can connect that Csc output to the eventual Player input.

At **end**, the tool observes the same graph, responses, dependencies, Csc output and reachable DLLs. A cache candidate is eligible only if every retained component is still byte-identical and available. The fresh `actualInputs` captured by the existing Unity adapter remain the current-build consumption boundary.

At independent **verify**, the retained graph is reparsed. The verifier requires the Csc action SHA to match, re-derives source/dependency/output/defines/responses, requires every source to have been in the pre-build source ledger, verifies retained dependency/output bytes, and requires exactly one graph path from the retained Csc output to the **exact fresh Player input path, SHA-256 and size**. The accepted row is explicitly labeled `BeeCacheHitBoundToFreshPlayerInput`.

The cache route does **not** claim fresh Csc execution: `freshCompilerExecutionClaim=false`. A cache hit proves a byte-stable pre-build compiler/ILPP action chain whose output is exactly the managed DLL consumed by this fresh Player build. Native build execution, ILPP/witness verification, installed-source proof and Player execution remain separate evidence.

### Fail-closed boundaries

The new cache proof is bounded independently:

| Bound | Value |
| --- | ---: |
| Candidate Bee DAGs | 64 |
| One retained Bee DAG | 128 MiB |
| Retained cache observations | 4096 |
| One retained cache file | 64 MiB |
| Aggregate retained unique bytes | 512 MiB |
| Reachable retained DLLs | 128 |

Any changed/missing response, compiler dependency/tool, Csc output, downstream DLL, source/configuration input, changed DAG/action, wrong fresh Player path, output that did not exist at begin, or multiple matching cache chains fails closed. Unknown/implicit compiler input search is still unsupported. Cache proof does not auto-fall back to legacy prior-proof reuse.

Existing `verify_exact_reuse(... --reuse-proof ...)` remains an explicitly selected legacy route only; **do not use it to satisfy the current fresh smoke**. The requested repair must be demonstrated by the direct current-build cache proof.

### Primary review and bounded tests

Primary CI workflow run **35061641985** at anchor `0387feb4344bbe95fd7db524d6e0bae759adc203` authenticated the established Apple Bee fixture and passed **281/281** tests, zero nonpasses. The suite now includes legacy managed-provenance tests and eight cache-specific controls: legitimate unchanged cache hit, stale output rejection, ambiguous action rejection, changed source, changed response, changed dependency, wrong fresh Player binding even with identical bytes, and output absent at begin.

CI artifact ID `10432043605`, ZIP SHA-256 `5492b3051f6e35dfbf1a970932383308788fb6907bb63b5aa1183e133309d536`. This is bounded Primary/tool evidence, not current macOS Unity/Player, runtime, M08, or human acceptance.

The previous retention-store repair remains part of this source anchor. Do not regress or bypass its reversible declared-input store, independent store verifier, Apple macro-domain proof, PCH replay, or fail-closed limits.

## Local validation

Run fresh **V00–V05**. Prior successful facts remain historical evidence but do not replace affected validation of this source anchor.

### V00 — authoritative preflight

1. Explicitly `git pull --ff-only origin codex/assembly-shadow-r01b-h1` in candidate.
2. Record branch/origin/checkout HEAD and dirty/untracked state without reset/clean/stash-away of unrelated evidence.
3. Confirm source targets and source pins identify `0387feb4344bbe95fd7db524d6e0bae759adc203` and protected identities match the table.
4. Run into a new absolute output path:

```sh
python3 Tools/AssemblyShadow/h1_handoff_preflight.py \
  --project /ABS/CANDIDATE/hybridclr_demo \
  --role candidate \
  --output /ABS/NEW/v00/candidate-handoff.json
```

Expected: exit 0, `SourceTargetVerifiedNotBuildAccepted`, code commit `0387feb4344bbe95fd7db524d6e0bae759adc203`, gate flags false. If V00 fails, stop before V01–V05 and return evidence.

### V01 — affected source/tool/Unity regression

Run the full H1 Python inventory and the exact Bee Primary suite, with special attention to `test_h1_managed_provenance` and `test_h1_managed_cache_provenance`, plus strict compiler/native provenance, retention, PCH, handoff, normal M02-owner, collector/successor tests. Compile candidate and reproduction in Unity and rerun focused H1 Editor tests and affected Assembly Shadow regressions. Preserve exact IDs/logs/XML/skips.

Expected: affected regressions pass. The Linux Primary 281/281 result does not replace macOS/Unity execution.

### V02 — real unchanged Bee cache proof

Validate the repair on the real normal cache state, not only synthetic fixtures. The previous checkpoint identified the unchanged Player DAG `Library/Bee/200b0aPDevDbg.dag.json`; use the current actual Player graph identity rather than assuming its hash/path if Unity legitimately regenerates it.

For both required assemblies (`AssemblyShadowDemo.Bootstrap` and `AssemblyShadow.R01BDiagnostics`) require:

1. begin ledger schema 2 and a retained cache candidate whose source set exactly matches the assembly plan;
2. retained graph/action, recursive response closure, compiler dependencies/tools, Csc output, and reachable downstream DLL identities;
3. end observations for every retained cache element are `Unchanged` for an accepted cache hit;
4. fresh Player `actualInputs` are captured normally after this build;
5. independent managed verification returns exactly one row per assembly and, wherever Bee legitimately reused the chain, `evidenceMode=BeeCacheHitBoundToFreshPlayerInput`;
6. that row binds the cached downstream DLL to the exact fresh Player input **path + SHA-256 + size** and preserves DAG reachability from the Csc output;
7. `freshCompilerExecutionClaim=false` for cache proof;
8. no `reusedFrom`/`--reuse-proof` is used to close this requirement.

If an assembly actually recompiles and has one valid changed graph, `ChangedBeeGraphBoundToFreshPlayerInput` remains acceptable for that assembly. Record which route each assembly used; do not force either result.

Run the new stale/ambiguous/source/response/dependency/wrong-Player/output-created-after-begin controls. Any ambiguity or stale component must reject rather than pick a candidate by order/recency.

**Do not delete/clean Bee cache merely to force managed recompilation as the acceptance route.** A clean-build diagnostic may be additional evidence, but this handoff specifically requires validation that legitimate unchanged cache reuse can be proved fail-closed.

### V03 — fresh provenance-bound Player builds

Reinstall candidate from the new source pins and run normal installed-runtime verification with demo-source checking enabled. Execute a fresh candidate ON/Debug smoke first.

Acceptance requires all existing evidence plus managed verification through either the unique changed-action route or the new current-build cache route:

- Player build success;
- complete native compiler provenance and independently verified declared-input store;
- Apple domain / compiler / PCH evidence;
- managed source begin/end capture;
- exactly one managed chain for each required assembly;
- cache-hit rows, if present, bound to the exact fresh Player input as specified above;
- no legacy `--reuse-proof` substitution for the current smoke;
- final build receipt and strict single-build verifier PASS;
- exact project/generated restoration.

After a valid smoke, run remaining candidate ON/OFF × Debug/Release and unfixed reproduction ON Debug/Release in fresh immutable roots. Record per-build managed evidence mode for both required assemblies. Preserve all failures.

If real Bee graph structure uses a legitimate action/response/dependency/ILPP path not expressible by the reviewed cache proof, return full evidence to Primary. Do not broaden parser/allowlists or erase cache locally.

### V04 — runtime/count/startup/capacity/performance chain

After six provenance-bound builds exist, execute the current R01B chain: 132 candidate count cells, 8 unfixed reproduction cells, fresh baseline/fixtures/replay and 11 startup modes, ordinary/mixed 8192 lifetime capacity and 8193 rejection, retained failures, >=25% usable encoded-page free capacity, 32 MiB maximum DLL and 512 MiB valid input boundary, lazy/dense/generic/array/reflection/FieldRVA/old-Player and affected M03–M07 regressions.

Run controlled Development performance pairs only against the separate performance-reference checkout on common supported workloads. Do not infer Release/P99/device-RAM acceptance.

### V05 — successor package and independent whole-chain M08

Construct the successor evidence archive/index from explicit source/build/raw locations. Include managed source begin/end, cache graph/action/input/output observations, final managed graph verification, native compiler/PCH/store proof and required runtime evidence. Summary PASS artifacts are insufficient.

Authenticate archive/index bytes, membership and references, run strict semantic verifiers, then commission a genuine independent design → source → builds → raw evidence whole-chain M08 review. A cache/tooling PASS is not M08 PASS.

Only genuine independent whole-chain M08 PASS may make the package **Ready for Human Review Gate**. Then stop for explicit human H1 approval.

Commit new checkpoint/raw evidence under `Docs/AssemblyShadow/M07R/R01B/H1-Remediation/...`. Update and push Local-owned `LOCAL_VALIDATION.md`; return any nontrivial issue through `RETURN_TO_WEB.md`.

## Failure evidence

For a managed-cache failure retain exact checkout/source pins, build GUID/input snapshot, before/after managed capture, exact fresh Player inputs, retained Bee DAG bytes/hash, Csc action/transcript, recursive responses, dependency/tool bytes/hashes, Csc output, reachable downstream DLLs, end observations, managed verifier output/error, and evidence mode. Preserve native compiler/PCH/store evidence and Unity/batch logs as usual.

For stale or ambiguous cache rejection, identify which precise element changed/duplicated and whether the failure happened at begin, end observation, transcript re-derivation, DAG reachability, fresh Player binding, or uniqueness enforcement.

Keep `Passed`, `Failed`, `InvalidEvidence`, `Unavailable`, `NotRun` and `NoCoverage` distinct. Preserve `local-validation-20260915-8f5bcaa`, `local-validation-20260915-22eda8b`, c0d3070, and historical v6–v11 evidence unchanged.

## Alternatives

The selected route is a **fresh-build-bound cached-action proof**. It proves unchanged pre-build action/input/output bytes are exactly the managed DLL consumed by the current fresh Player; it deliberately does not claim fresh compiler execution.

The existing explicit prior-proof `--reuse-proof` route remains a separate legacy equivalence mechanism and must not be used as a substitute for validating this new path. Clearing Bee cache to force Csc/ILPP execution also does not validate the requested cache-hit repair.

Do not broaden source membership, accept path/hash-only evidence without the retained action/dependency chain, weaken ILPP/witness/native checks, increase cache-proof bounds locally, or change runtime/performance methodology. Such alternatives return to Primary first.

## Risks

Real Unity/Bee graphs may contain additional legitimate response-file, compiler dependency, or ILPP/copy stages not represented in the bounded synthetic cache fixtures. The implementation fails closed on implicit compiler search, excessive graph/file/byte/reachable-DLL volume, ambiguity, changed bytes, and unsupported transcript grammar. A real rejection therefore requires evidence and Primary review rather than a local allowlist expansion.

`freshCompilerExecutionClaim=false` is intentional for cache hits. Acceptance depends on fresh Player consumption of an unchanged, source-bound cached chain plus the rest of the independent build/native/runtime evidence; it must not be described as a fresh Csc execution.

This source-anchor change invalidates affected old build receipts unless an existing explicit equivalence contract independently permits reuse. Historical results remain historical.

## Local correction boundary

Local Validation may correct machine paths, executable permissions, invocation syntax, output-directory choices, isolated test setup, and already-documented exact generated-file restoration after preserving before/after bytes.

Local Validation must not change cached-action source selection, cache-proof limits, action/dependency/reachability semantics, managed verification acceptance, prior-proof reuse semantics, retention/native/PCH provenance, witness rules, source identity, count behavior, ABI/architecture, or performance methodology. Those are Primary changes regardless of diff size.

Do not rewrite `WEB_TO_LOCAL.md`. Preserve and append empirical facts only in Local-owned reports.

## Human review gate

Current project gate remains H1. State is `InProgress`, technically blocked pending fresh V00–V05; last independent whole-chain M08 is `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Only after implementation and actual Local Validation satisfy the current project gate definition **and** a genuine independent whole-chain M08 returns PASS may the package become **Ready for Human Review Gate**. Then stop for explicit human approval. Neither agent may grant H1. Do not begin R02 before that approval is recorded.
