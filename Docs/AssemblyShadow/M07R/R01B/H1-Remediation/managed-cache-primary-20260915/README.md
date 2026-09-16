# Managed Bee Cache Primary Repair — 2026-09-15

## Scope

Primary Implementation response to Local Validation commit `7f98084518054bd43e10abb603fe193612cfb321`.

Local established that source anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe` passed the real Apple declared-input retention/native provenance path, but managed verification failed because the exact required Player Csc/ILPP graph and DLLs were legitimate unchanged Bee cache outputs rather than a changed graph.

## Repair

New candidate source/implementation anchor: `0387feb4344bbe95fd7db524d6e0bae759adc203`.

`h1_managed_provenance.py` now records bounded reusable Player Csc chains at begin and, when no unique changed-graph chain exists, can prove a current-build Bee cache hit only when:

- the retained Csc source set exactly matches one required assembly;
- required Player defines are present and `UNITY_EDITOR` is absent;
- graph, response closure, compiler dependencies/tools, Csc output and reachable downstream DLLs remain byte-identical through end;
- independent verification re-parses the retained action/transcript;
- exactly one chain reaches the exact path/SHA-256/size of the DLL captured as a fresh Player input.

Accepted cache rows use `evidenceMode=BeeCacheHitBoundToFreshPlayerInput` and `freshCompilerExecutionClaim=false`.

The unique changed-graph route remains preferred. Existing explicit prior-proof reuse remains separate and is not automatic fallback.

## Fail-closed bounds

- cache Bee graphs: 64
- one graph: 128 MiB
- retained observations: 4096
- one retained file: 64 MiB
- retained unique bytes: 512 MiB
- reachable DLLs: 128

Stale/missing evidence, ambiguity, implicit compiler search, changed action/input/output bytes, wrong Player binding or output absent at begin rejects the cache proof.

## Primary validation

GitHub workflow run `35061641985` at `0387feb4344bbe95fd7db524d6e0bae759adc203` passed **281/281** bounded Primary tests with zero nonpasses.

Artifact ID `10432043605`; ZIP SHA-256 `5492b3051f6e35dfbf1a970932383308788fb6907bb63b5aa1183e133309d536`.

This validates the bounded implementation and synthetic cache controls. It is **not** current macOS Unity/Player acceptance, M08 PASS, or Human Review Gate approval.

## Next

Follow `Documents/AgentHandoff/WEB_TO_LOCAL.md` and `LOCAL_VALIDATION_TASKS.md`. Local must validate the normal real unchanged Bee-cache route; deleting Bee cache or supplying `--reuse-proof` does not satisfy this repair.

H1 remains `InProgress`; `humanGatePassed=false`; `mayEnterR02=false`.
