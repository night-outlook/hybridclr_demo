# Local Validation checkpoint — handoff 9568ea3

## Exit

**Local Validation → Primary Implementation**

V00, V01, V02, and all four candidate V03 modes pass. The fresh reproduction ON/Debug Player also builds successfully, but its mandatory provenance step invokes the protected reproduction checkout's older project-local `h1_native_capture.py` and fails with:

```text
Translation units disagree on effective diagnostic macros (link flags are not compile evidence)
```

The serial V03 batch therefore exits 1 before reproduction ON/Release. The candidate source anchor's diagnostic-only tool accepts the exact failed reproduction request and 446-action graph, runs all Apple macro/PCH probes, and independently verifies the retained store. That replay is explicitly `DiagnosticReplayVerifiedNotBuildAccepted`; it cannot create or repair a build receipt. This isolates a tooling-chain mismatch while preserving the protected reproduction code and native behavior.

V04 and V05 are `Blocked / NotRun`. Independent whole-chain M08 was not commissioned. `humanGatePassed=false`, `mayEnterR02=false`, and R02 was not started.

## Source identity

| Role | Exact identity | Final state |
| --- | --- | --- |
| Candidate handoff checkout | `9568ea386822b4e8e48ff73e793d4a2cd09092dc` | explicitly pulled requested branch |
| Candidate source anchor | `5f561abdfbe020d1d480594a2130c5ec846c0e6a` | source target and pin match |
| Candidate native | `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | clean |
| Shared package | `0ea633a2c5b936b5af69d944593c55bd2783fca9` | clean |
| Shared IL2CPP | `6be7f38bec2fa4677d24efc1a4a1294240789933` | clean |
| Reproduction demo | `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` | unchanged and clean |
| Reproduction native | `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` | unchanged and clean |
| Performance reference | `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` | unchanged and clean |

The candidate retained pre-existing untracked historical `v7`–`v11` evidence. No reset, clean, stash, branch movement, or protected-pin modification was performed.

## Results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00 authoritative preflight | `Pass` | Exit 0; `SourceTargetVerifiedNotBuildAccepted`; requested checkout/source/pins and false gate flags. |
| V01 Bee Primary | `Pass` | Corrected fresh invocation 283/283. The initial pre-created-output invocation failed and is retained. |
| V01 H1 Python | `Pass` | 461/461. Managed cache 10/10, managed provenance 17/17, strict compiler provenance 4/4, normal M02 owner 15/15. |
| V01 candidate Unity | `Pass` | Compile; focused NUnit 4/4 and 10/10; full demo 351/351; package 720/720. |
| V01 reproduction Unity | `Pass` for required scope | Compile and focused NUnit 4/4 and 10/10. |
| V02 candidate ON/Debug | `Pass` | Fresh Player, strict native provenance, schema-3 managed proof, exact restoration. Both assemblies use `BeeCacheHitBoundToFreshPlayerInput`; `freshCompilerExecutionClaim=false`. |
| V02 action-local response proof | `Pass` | Each required action owns exactly two recursive responses; membership is exact and all owned responses are unchanged. This run observed no audit-only response mutation. |
| V02 native retention store | `Pass` for store integrity | `StoreVerifiedNotAcceptance`; 451 objects, 318,212,421 logical bytes, 72,612,459 stored bytes. |
| V03 candidate four-mode set | `Pass` | ON/OFF × Debug/Release all pass strict native and schema-3 managed provenance with exact restoration. |
| V03 reproduction ON/Debug | `Fail` | Player succeeds; old project-local capture rejects the real Apple macro split before publishing compiler provenance or a receipt. Exact restoration passes. |
| V03 candidate-tool diagnostic | `Pass` for diagnosis only | Exact failed request/graph returns `DiagnosticReplayVerifiedNotBuildAccepted`; 446 actions and store verification pass. No receipt or acceptance claim. |
| V03 reproduction ON/Release | `Blocked / NotRun` | Serial strict batch stops on reproduction ON/Debug. |
| V04 runtime/count/startup/performance | `Blocked / NotRun` | Required six-build provenance set is incomplete. |
| V05 successor/M08 | `Blocked / NotRun` | Acceptance inputs are incomplete; last independent M08 remains `FAIL`. |

The two mistaken runtime-verifier invocations used a duplicate operation argument. One raw failure is retained; the first was overwritten before this checkpoint and is recorded as `Unavailable`. The corrected exact verifier passed with 955 source files, 957 installed files, `demoSourceVerified=true`, mode `on`, and install receipt SHA-256 `8b6d04c1e54c57174bae04476814166ff78d52ab5d1af1d048695c4462087f68`.

## V02 schema-3 evidence

- Build GUID: `1d8b8152db7348839de41dbe0206aa2f`.
- Input snapshot: `498a47bdffd70f650b51bfd1057a51e6bb2be0e914ba8196dad67ed1c576c2f1`.
- `GameAssembly.dylib`: `c5fcf8c9e78632a5d9a1df8319ce7a5cc346526c745823ab72df8ded27d901c0`.
- Managed capture: `04676747c894c68f5f9727221ef9a7e405cfc33c1ba04946e85d3b7eac3893b3`.
- Cached Player DAG: 9,281,264 bytes, SHA-256 `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af`.
- Diagnostics action: `67df1baf137e19ff95e6d36cf579e4065b5c57281ec80b1ed2ee17734ca560cc`; response closure `[90c6e799…, e3b0c442…]`; exact fresh DLL `d8c6a81f…`, 111,616 bytes.
- Bootstrap action: `147ff4fdd7fb75e65bf9ac1e541096a0a7a72b82bfe1e32ddafab91101cef6a7`; response closure `[18ded2b1…, e3b0c442…]`; exact fresh DLL `863743cc…`, 567,296 bytes.
- The normal Bee cache was preserved. Neither cache cleaning nor `--reuse-proof` was used.

## V03 candidate identities

| Mode | Build GUID | Input snapshot | Native SHA-256 | Managed evidence |
| --- | --- | --- | --- | --- |
| ON/Debug | `1d8b8152db7348839de41dbe0206aa2f` | `498a47bdffd70f650b51bfd1057a51e6bb2be0e914ba8196dad67ed1c576c2f1` | `c5fcf8c9e78632a5d9a1df8319ce7a5cc346526c745823ab72df8ded27d901c0` | two schema-3 cache-hit rows |
| ON/Release | `44bff9cb00204110ad0e8387592677a9` | `e16515dff4d03a59ea3a51b9fe3df8f6a63f996a0c738bd1e0d2c13d0d8f4c26` | `15f8fff440ea0fa4ac42bdde359e5c964cd4b53311b892ed4caf81201510c441` | two schema-3 cache-hit rows |
| OFF/Debug | `54e8baf465ab44268c6549a20b464b3c` | `bd4f3a8e49c361446151f533e64cb0b7551b7f70292f9d80ae9f90f7038cac4e` | `533436c06b84349c86168d6edf22a7ea7ffa77da0f584227cbbd3f7b0bc6aab8` | two schema-3 cache-hit rows |
| OFF/Release | `76d52132084f49f1b359b4dbbff019d1` | `570d6089a00e5e540f64a5f7bc73e5724da53ed396bdb94fced2670cb38efc63` | `4c3a9700c41c59190233c39d3ea7d41ceb2b0294ad8c738f3b5657226001f9d2` | two schema-3 cache-hit rows |

## Reproduction failure identity

- Build GUID: `44882bc8dac74f538be9e951991d790e`.
- Input snapshot: `7d1349c55854ce6f121eafef0312eb04da6698a7e245cc33b2ece52fa2654073`.
- Fresh Player native SHA-256: `4ad497816822932021d89879e5f5d7c7f490a4b0ae5fda4994498281a278fae5`.
- Exact request SHA-256: `d0264e40f116445884696ebbd56564622722c2b20ba78835b7e5a741439095e1`.
- Selected fresh Bee graph: 2,796,905 bytes, SHA-256 `aaaedafc0c9d1a5e5410090d396d906ac1aced72b79965f3fe14d072ee22879d`.
- Project-local reproduction `h1_native_capture.py`: `ec09eb58b4b9cf632d8ec68d570c7a0a70a3faf56fc69bb42cf9217ff9c7081a`.
- Candidate `h1_native_capture.py`: `17022d2e55421730a1e280fc43ffc3eb2f4ad6d16458c5d47a61483726e6c1b7`.
- Candidate diagnostic replay proof: `a4425ebca605487b7c57fa851e6ac5f03f22d0e766da642934b4191b0cd5fc5d`.
- Diagnostic store: 451 observations/content blobs, 317,525,404 logical bytes, 72,486,391 stored bytes.
- Restoration: `ExactRestorationVerified`.

The failure is not a runtime count result. The mandatory build receipt does not exist, so the successful Player is invalid for V04 acceptance.

## Evidence

- `v02/managed-source-provenance.tar.gz`: full schema-3 begin/capture/cache/action-local response/dependency/output/actual-input evidence and receipt.
- `v02/managed-cache-census.json`: compact exact action-local ownership and observation census.
- `v02/capture-store-verification.json`: independent native store verification.
- `v03/build-runner-results.tar.gz`: complete V03 runner outputs, including all Unity build logs and the raw reproduction failure.
- `v03/candidate-*`: accepted candidate native/managed verifier outputs and restoration records.
- `v03/reproduction-on-debug-failure`: exact request, graph, config, failure identity, tool identities, raw restoration result, graph census, and diagnostic-only replay results.
- Full unpacked runner root: `/Users/ah/GitHub/hybridclr/h1-local-validation-20260916-9568ea3/v03/all`.
- V02 immutable root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-0e2d7991d39e47d3a508b13206945aa2`.
- Failed reproduction root: `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-113d3fcd452546179ee4a6b0aecf3397`.
- Diagnostic-only replay root: `/Users/ah/GitHub/hybridclr/h1-local-validation-20260916-9568ea3/v03/reproduction-candidate-tool-diagnostic`.

No product code, allowlist, cache limit, response ownership rule, provenance policy, reproduction pin, or performance reference was changed locally.
