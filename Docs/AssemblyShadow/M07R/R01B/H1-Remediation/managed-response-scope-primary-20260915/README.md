# Managed cache response-scope Primary repair

## Status

Primary Implementation source/implementation anchor: `5f561abdfbe020d1d480594a2130c5ec846c0e6a`.

Returned Local Validation checkpoint: `dc9116a46097739b634c791ac7213f431b54af22`, with raw checkpoint under `local-validation-20260915-3695905`.

H1 remains **InProgress**. Last independent whole-chain M08 remains **FAIL**. `humanGatePassed=false`; `mayEnterR02=false`. This repair does not authorize R02.

## Local finding

The fresh ON/Debug Player reused the two required managed compilation chains from Bee cache. Their own recursive response closures, dependencies, Csc outputs, downstream PlayerScriptAssemblies outputs and exact fresh Player bindings were unchanged. Schema 2 nevertheless failed because it attached every response discovered from every Csc action in `200b0aPDevDbg.dag.json` to the cache graph. Seven unrelated `StandaloneOSX_CodeGen/*.rsp` files changed during normal staging and invalidated the whole graph.

The retained Local census proves that this was a response-ownership error, not evidence that the required cache chains changed.

## Repair

Fresh captures use managed provenance schema 3.

For each matched required Csc action, `csc_arguments()` obtains `responseSources` from the existing bounded recursive `@response` expansion. `capture_cache_graphs()` retains exactly those response bytes on that compilation as `responseFiles`. Shared required response files are content-retained once but remain explicitly referenced by each owning action.

Graph-wide response discovery is retained only as `responseAuditSources`; it is not an acceptance dependency unless a path also belongs to the selected action's recursive response closure.

At verification, schema-3 response membership must exactly equal the compilation's recorded `responseSources`; every owned response byte must be retained and unchanged. Nested required responses therefore remain fail-closed. Unrelated responses may change without invalidating a required cache chain.

## Preserved acceptance boundaries

This change does **not** broaden any other cache acceptance rule. The verifier still requires:

- unchanged retained Bee graph identity;
- exact selected Csc action hash and independently re-parsed transcript;
- exact required source set and required Player defines;
- exact compiler/tool/reference dependency closure, with every retained dependency unchanged;
- Csc output present before build, retained, unchanged and at the recorded output path;
- retained downstream DLL closure and unchanged outputs;
- graph reachability from Csc output to the exact fresh Player input path;
- exact fresh Player input SHA-256 and size;
- at most one changed-action chain and exactly one accepted chain per required assembly;
- all existing graph/file/byte/reachability bounds;
- `freshCompilerExecutionClaim=false` for cache-hit proof;
- explicit legacy `--reuse-proof` remains separate and is not automatic fallback.

Schema-2 retained evidence remains independently verifiable with its original graph-wide response semantics. New captures do not silently reinterpret old evidence as schema 3.

## Primary validation

Workflow run `35066118142` at anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` passed **283/283** bounded Primary tests with zero nonpasses.

Artifact ID: `10434108589`  
Artifact ZIP SHA-256: `94e4cfc61b62dd01c297a704f97085d1031e56e29986cc281eb6679ccafb1ded`.

New regressions prove both sides of the intended boundary:

1. an unrelated Csc response in the same DAG can mutate while two required cached chains remain accepted and bound to fresh Player inputs;
2. a nested response inside a required action's recursive closure remains stability-critical and mutation is rejected.

Existing stale output, ambiguous action, source change, required response change, dependency change, wrong fresh Player path, and output-not-present-at-begin rejection tests remain in the same suite.

This CI is portable/bounded Primary evidence. It is **not** Unity/Apple Player acceptance, V02/V03 completion, M08 PASS, or human H1 approval.
