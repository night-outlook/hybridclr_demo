# Local Validation → Primary Implementation

## Native-provenance macro scope rejects the actual Apple Bee graph

### Symptom

Both the exact old ON/Debug diagnostic replay and a fresh candidate ON/Debug Player build fail with:

```text
Translation units disagree on effective diagnostic macros (link flags are not compile evidence)
```

The fresh Unity Player build itself reports success. `H1CompilerProvenance.CaptureAfterBuild` then invokes `h1_native_capture.py`, which fails before creating the provenance output or build receipt. This is an executed acceptance failure, not missing evidence.

### Minimal reproduction

From candidate checkout `bec2bd1936171313663a425d63bd3b0249b171c5` / code anchor `54259ef467e3937fe1879161aa552e42eb7e5854`, after the exact pinned installer and strict runtime verification pass:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity --pwsh /usr/local/bin/pwsh --scope smoke --output /Users/ah/GitHub/hybridclr/h1-local-validation-20260914-bec2bd1/v03/smoke-execute-2 --execute
```

The runner exits 1 after 188.05 seconds in the build process. `failed.json` records `candidateAcceptance=false`; `restored.json` records exact restoration.

The independent old-attempt replay is:

```sh
python3 Tools/AssemblyShadow/h1_pch_diagnose.py --request /ABS/EXACT_OLD_REQUEST.json --graph /ABS/EXACT_OLD_DAG.json --output /Users/ah/GitHub/hybridclr/h1-local-validation-20260914-bec2bd1/v02/pch-diagnostic
```

It exits 1 with the same error. The exact old DAG SHA-256 observed at execution is `e29cd922a598644ae5a46e44b579418598c789f094202a7f41b8ff63e90eabac`; both old PCH hashes match the fresh attempt. The original request is committed with SHA-256 `fb0c229f6ea8ad0e147cfbe96645ce2730a2c127d3599ed80fca37a928d3c979`. The old DAG itself is `Unavailable` after the fresh build replaced the mutable Bee graph; use the complete fresh V03 graph below for the actionable reproducer.

### Evidence and observed boundary

The portable failure input is [fresh-smoke-failure-inputs.tar.gz](local-validation-20260914-bec2bd1/fresh-smoke-failure-inputs.tar.gz), SHA-256 `e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8`. Its `failure-input-manifest.json` binds:

- build GUID `4ca877a4f3bf4c708d43089f6016f9fb`;
- input snapshot `3cbdc85d75bf7b185936b9dff450dfdd43f60a91d46875ed8be112069b3b8418`;
- fresh DAG `dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181`;
- native output `d26b47e1f83781ff0bf14baa178e8ace3184ff52552177e53109e21abff981c6`;
- C PCH `dfeb9887f49fcb7698e15959a17a8edb5d87c400f270970e176b82315b7d2197`;
- C++ PCH `512070807ba6df6f592a96f2cbd99bd3535e33c2f7544986a38f4bad3defc6a5`;
- selected Apple clang binary identity `f30550eab15fdf5ab8c0dc54c52679711241e5d4b636b027e18c09fef531775d` and SDK settings `e5c7c40b8c5dc1a9f99f8b9fa51870f8fe180421225b8201d0c4c826aad11bdc`.

All 446 compile actions parse. Two macro-intent groups are present:

| Native action scope | Count | IL2CPP_DEBUG | NDEBUG defined | IL2CPP_DEVELOPMENT | PCH producers |
| --- | ---: | ---: | ---: | ---: | ---: |
| Platform/helper C actions, nodes 151–167 excluding 153 | 16 | 0 | 0 | 0 | 0 |
| GameAssembly/IL2CPP actions, nodes 236–666 excluding 359 | 430 | 1 | 0 | 0 | 2 |

Every action has the requested Shadow and count-diagnostic defines. There are no response files and no libtool action in the selected DAG. Raw module-file-info succeeds for both PCHs and identifies 85 C inputs and 827 C++ inputs; 833 unique referenced header/config byte blobs are retained.

The failure occurs in `h1_pch_provenance.plan()`: it strips PCH syntax, passes every `C_Mac_arm64` action to `derive_graph_evidence()`, and requires one global `IL2CPP_DEBUG/NDEBUG/IL2CPP_DEVELOPMENT` state before PCH replay groups are created. Because planning fails first, replayed PCH, probe source/argv, compiler macro output, and the tool's own diagnostic output directory are `UnavailableBeforeReplay` / `UnavailableBeforeProbe`, not failed probe evidence. The committed bundle records these states explicitly.

### Most likely root cause

The provenance design treats all native compile actions reaching the selected Player as one diagnostic macro domain. The actual Unity 2022.3.62f2 Apple Bee graph contains a small platform/helper C domain that uses the pinned header defaults while the GameAssembly/PCH domain has `-DIL2CPP_DEBUG=1`. The global-equality predicate runs before the intended per-context PCH probes, so it rejects the real graph without determining whether either domain is inconsistent internally.

The same stage-order issue prevents `h1_pch_diagnose.py` and fresh capture from retaining their own partial failure directory: both call `plan()` before creating output. Local packaging recovered the immutable input set, but the product diagnostic does not satisfy its promised failure-retention behavior for plan-stage errors.

### Impact

No fresh provenance-bound candidate ON/Debug receipt exists. The remaining candidate modes, unfixed reproduction builds, runtime count/startup/reproduction chain, performance pairs, successor archive, and independent M08 are blocked. The successfully built Player cannot be used for H1 acceptance because native provenance capture did not complete.

### Recommended direction

Primary implementation should define and review the intended macro-domain selection before changing the predicate. A likely direction is to separate compiler/link identity and requested Shadow/count define checks across all selected actions from assertion/debug-profile checks for the GameAssembly/PCH domain, then prove every included/excluded action's relation to the selected native output. Per-domain consistency must remain fail-closed; do not simply ignore the 16 actions or union their defines.

Also move creation of a bounded diagnostic root and raw graph/request/input inventory ahead of plan-stage validation so unsupported graphs retain actionable tool-owned failure evidence. Add fixtures for the observed 16/430 Apple graph split and for malicious mixed macros inside each permitted domain, then rerun V01–V05 from a new reviewed code anchor.

### Uncertainty

The local run establishes the two domains and the failing stage, but it does not establish the design-authoritative boundary for the 16 actions. Their exact annotations, sources, flags, graph edges, and outputs are in `compile-actions-macro-intent.json` and the selected DAG. Primary review must decide whether they are platform support, generated user C, or another category that should remain inside a particular assertion/debug contract.
