# Static Review — Managed Bee Cache Proof

## Verdict

**Ready for Local Validation, not H1 acceptance.**

Reviewed source/implementation anchor: `0387feb4344bbe95fd7db524d6e0bae759adc203`.

## Invariants preserved

1. Required managed membership remains exactly `AssemblyShadowDemo.Bootstrap` and `AssemblyShadow.R01BDiagnostics`.
2. A cached Csc candidate is selected only when its parsed source set exactly equals the planned source set for one required assembly.
3. Required Player defines must be present; `UNITY_EDITOR` rejects the candidate.
4. Begin captures the cache graph/action and all accepted evidence **before** the Player build can mutate it.
5. Direct changed-graph proof remains preferred when exactly one current changed chain exists.
6. Cache proof is evaluated only when there is no direct chain for that assembly.
7. End records observations for every retained graph/response/dependency/Csc-output/reachable-output row.
8. Independent verification re-reads retained bytes and re-parses the Csc action rather than trusting capture summaries.
9. Response closure and compiler dependency closure must exactly match the re-parsed action.
10. Every accepted cache evidence component must still be `Unchanged` at end.
11. The selected downstream cached DLL must match the fresh Player input path, SHA-256 and size, and remain reachable from the Csc output in the retained DAG.
12. Exactly one matching cache chain is required. Ambiguity fails closed.
13. A required output absent at begin cannot be created during the build and retroactively treated as cache proof.
14. Cache evidence explicitly sets `freshCompilerExecutionClaim=false`.
15. Existing explicit prior-proof reuse is separate and is not automatic fallback.

## Bounds

The pre-build cache proof has independent hard bounds: 64 graphs, 128 MiB/graph, 4096 retained observations, 64 MiB/file, 512 MiB aggregate retained unique bytes, and 128 reachable DLLs. Bounds are not user-selected by the current graph and Local Validation must not raise them.

## Regressions

Primary suite now covers the prior managed-provenance tests plus:

- accepted unchanged Bee cache bound to fresh Player input;
- stale cached output rejection;
- duplicate/ambiguous cached action rejection;
- source mutation rejection;
- response mutation rejection;
- compiler dependency mutation rejection;
- wrong fresh Player path rejection even when bytes are identical;
- output-created-after-begin rejection.

Workflow run `35061641985`: **281/281 PASS**, zero nonpasses. Artifact `10432043605`, SHA-256 `5492b3051f6e35dfbf1a970932383308788fb6907bb63b5aa1183e133309d536`.

## Limitations requiring Local Validation

The proof does not assert that Bee executed Csc on a cache hit; it proves a byte-stable pre-build action/input/output chain is exactly what this fresh Player consumed. Real Unity/Bee may contain legitimate response/dependency/ILPP/copy structures not represented by the synthetic fixtures. The actual cached `200b0aPDevDbg.dag.json` path and both required assemblies therefore must be validated on macOS/Unity.

Any unsupported real graph structure, ambiguity, changed byte, or limit exhaustion is a Primary issue. Do not broaden acceptance locally.

No M08 review was performed by this bounded review. `humanGatePassed=false`; `mayEnterR02=false`.
