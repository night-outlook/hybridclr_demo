# Local Validation checkpoint — handoff 3695905

## Exit

**Local Validation → Primary Implementation**

Fresh V00 and V01 pass. The prioritized fresh candidate ON/Debug Player build also completes, and its native compiler/PCH/store verification passes. Managed verification then fails closed before it can emit either required acceptance row:

```text
Blocked: Cached managed response changed or was unavailable: .../Library/Bee/artifacts/StandaloneOSX_CodeGen/Unity.Burst.CodeGen.rsp
```

The normal Bee cache was preserved and `--reuse-proof` was not used. Both required managed compilations are present in the one retained Player DAG. For each assembly, its direct response closure, all 201 dependencies, compiler output, reachable downstream DLLs, and exact fresh Player input binding remain unchanged. However, the cache row attaches all 92 response files from the entire DAG, and seven unrelated `StandaloneOSX_CodeGen` response files legitimately gain the two diagnostic defines staged for this Player build. The verifier requires all 92 graph-wide responses to remain unchanged before filtering to either required assembly, so it rejects the real cache structure.

Changing response-file scope or acceptance semantics is outside Local Validation. The remaining five builds and V04–V05 are `Blocked / NotRun`; independent whole-chain M08 was not commissioned. `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Source identity

| Role | Exact identity | Final state |
| --- | --- | --- |
| Candidate handoff checkout | `3695905b1981a5cecbd444e27114c34cbc3bf255` | explicitly pulled requested branch |
| Candidate source/implementation anchor | `0387feb4344bbe95fd7db524d6e0bae759adc203` | source target and source pin match |
| Candidate native | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | clean |
| Candidate package | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | clean |
| Candidate IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` | clean |
| Reproduction demo | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | unchanged and clean |
| Reproduction native | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | unchanged and clean |
| Performance reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | unchanged and clean |

Pre-existing untracked historical `v7`–`v11` evidence was preserved and excluded.

## Results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; expected checkout, source anchor, pins, and false gate flags. |
| V01 Bee Primary | `Pass` | 281/281. |
| V01 H1 Python | `Pass` | 459/459. An additional broad inventory completed 955 passed / 1 skipped; the skip is the known platform-path export-boundary fixture and is not promoted to H1 acceptance. |
| V01 strict provenance / normal M02 owner / cache controls | `Pass` | 4/4, 15/15, and 8/8. |
| V01 candidate Unity | `Pass` | Compile passed; focused NUnit 4/4 and 10/10; full demo Editor suite 351/351; package Editor suite 720/720. |
| V01 reproduction Unity | `CompletedWithNonPass` | Compile and focused 14/14 passed. Additional full demo sweep completed 330/342 with the same 12 historical missing-fixture/baseline failures. |
| V02 real unchanged Bee cache proof | `Fail` | Required assembly-local material is unchanged and bound, but seven unrelated graph-wide CodeGen responses changed. No `BeeCacheHitBoundToFreshPlayerInput` row was emitted. |
| V03 pinned install / runtime verification | `Pass` | Install and exact source/runtime verification passed: 955 source files, 957 installed files, demo source verified, mode `on`. |
| V03 Player/native provenance | `Pass` before managed verification | Player build, strict native verification, compiler/PCH/domain capture, independent store verification, and exact restoration pass. |
| V03 managed provenance | `Fail` | Independent verifier rejects `Unity.Burst.CodeGen.rsp` before evaluating either required assembly's unique unchanged chain. |
| V03 remaining builds | `Blocked / NotRun` | A valid candidate ON/Debug smoke receipt is mandatory. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | The six-build provenance set does not exist. |
| V05 successor/M08 | `Blocked / NotRun` | Acceptance inputs are incomplete. |

## Real Bee cache census

- Retained Player DAG: `Library/Bee/200b0aPDevDbg.dag.json`, 9,281,264 bytes, SHA-256 `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af`.
- End observations: 302 total, 295 `Unchanged`, 7 `Changed`.
- Required compilations: exactly one cached action for `AssemblyShadowDemo.Bootstrap` and one for `AssemblyShadow.R01BDiagnostics`.
- Bootstrap: node 273, action SHA-256 `147ff4fdd7fb75e65bf9ac1e541096a0a7a72b82bfe1e32ddafab91101cef6a7`, 33 sources, 201 dependencies, 5 reachable DLL outputs.
- Diagnostics: node 327, action SHA-256 `67df1baf137e19ff95e6d36cf579e4065b5c57281ec80b1ed2ee17734ca560cc`, 7 sources, 201 dependencies, 3 reachable DLL outputs.
- Fresh Bootstrap Player input: 567,296 bytes, SHA-256 `863743cc1aba2835c5491e01277d9a054e9cf590923059627a4c42667aaa8c39`.
- Fresh Diagnostics Player input: 111,616 bytes, SHA-256 `d8c6a81f7c0f489d8de76c60454e8ebd06c5448d60c9ee67e7940c60cc10dd04`.
- The seven changed files are `Unity.Burst.CodeGen.rsp`, `Unity.Burst.rsp`, `Unity.HybridCLR.AssemblyShadow.CodeGen.rsp`, `UnityEditor.TestRunner.rsp`, `UnityEditor.UI.rsp`, `UnityEngine.TestRunner.rsp`, and `UnityEngine.UI.rsp` under `StandaloneOSX_CodeGen`.
- Every captured diff adds only `ASSEMBLY_SHADOW_H1_COUNT_DIAGNOSTICS` and `ASSEMBLY_SHADOW_R01B_DIAGNOSTICS`.
- `v02/managed-cache-census.json` contains the exact paths, hashes, sizes, observation status, actions, dependencies, outputs, and fresh bindings.

## Fresh build identity

- Build ID: `H1Count-On-Debug`
- Build GUID: `f6aa5298e2284385a9d458bb58f08e68`
- Input snapshot SHA-256: `ea5f83c1c1de80ce83bc9d121e4138843de8fb6234681e11a38c090d1ed55713`
- Native Bee graph SHA-256: `d0e34c181592adc10abedf1139104b951ac75bf2e356f352e04888edc297cf57`
- `GameAssembly.dylib` SHA-256: `117e733567a7b6d52742c93281a3842773af2820301dee602264887fdf4b2e85`
- Native build receipt SHA-256: `ab2cf18d908b302e9de775c35b06bbd824df260dc5d3725fb6d6336e887cd0ae`
- Compiler provenance SHA-256: `47bed29c77133de6f001b984a65c45371bac75ffc5ab5484bb9dbf72339a2b18`
- Managed capture SHA-256: `a081924a5a08a6d13666e26df43144074db240d9c3940fd5446978faa3d4502e`
- Source-pin SHA-256: `5b5ed1bc189b90a0f1f9eaa25e52dc90ffc245d2d1a553ae348c07e717a855a3`
- Restoration: `ExactRestorationVerified`

## Native store integrity

`h1_verify_capture_store.py` exits 0 with `StoreVerifiedNotAcceptance`: 451 observations/content objects/blobs, 318,212,421 logical unique bytes, and 72,612,459 stored bytes. Inventory SHA-256 is `a66bc38bdf402c5130b95b42ab6b535716236dabbceb9b369da0d9cbf28956c7`. This is storage integrity evidence, not managed or Player acceptance.

## Preserved raw evidence

- `v02/managed-source-provenance.tar.gz`: full begin/end managed cache ledger, retained DAG/responses/dependencies/outputs, and actual Player inputs; SHA-256 `3dc8967fc79389a83e2e9fca453fe44644f23344d4b2482795cb8fa56f069cc4`.
- `v03/fresh-native-provenance.tar.gz`: full compiler/PCH/domain/store evidence and native receipt; SHA-256 `c52e39bc207e7736145522830c45ab6deb5ed044be97982409c5565e6f1ab3a9`.
- `v03/smoke-runner.tar.gz`: raw batch logs, verifier error, native verification, and restoration evidence; SHA-256 `b3839f62d9a595b331e384734265ca9eb9a50aeac61dab724022a7e75f90e059`.
- Full unpacked roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-3695905/v03/smoke` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-27d8ff137d4b40258d6b42dbd83dd99a`.

All long raw failures are retained. No production source, cache, limit, allowlist, provenance rule, or acceptance policy was changed locally.
