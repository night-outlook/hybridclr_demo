# Local Validation → Primary Implementation

## Current blocker: real Apple provenance inputs exceed the attempt retention budget

### Symptom

The repaired handoff preflight and V01 candidate validation pass. Both an authenticated retained-graph replay and a fresh candidate ON/Debug Player build then fail before provenance planning with:

```text
Capture input exceeds retention byte bound: .../UnityEngine.UIElementsModule__7.cpp
```

The rejected file is 1,498,382 bytes and below the 64 MiB per-file limit. The attempt had already retained 337 input observations and 267,613,743 unique bytes; adding the file would exceed the fixed 256 MiB aggregate limit.

The fresh Unity Player build reports success before `H1CompilerProvenance.CaptureAfterBuild` invokes `h1_native_capture.py`. The provenance attempt is `FailedNotAccepted`, planning/PCH replay/macro probes are all `NotRun`, no provenance/build receipt exists, and exact project restoration passes.

### Reproduction

From candidate handoff checkout `22eda8b9d27c2494cdf66749aefebcbbc8701371`, source anchor `b6db7c2fb2fce364d49458b7dfc78886fd430004`, after the pinned install and strict runtime verification:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /usr/local/bin/pwsh \
  --scope smoke \
  --output /ABS/NEW/candidate-on-debug-smoke \
  --execute
```

The batch exits 1 after the Player build. `failed.json` records `candidateAcceptance=false`; `restored.json` records `ExactRestorationVerified`.

The retained replay independently fails at the same boundary:

```sh
python3 Tools/AssemblyShadow/h1_pch_diagnose.py \
  --request /ABS/RETAINED/original-request.json \
  --graph /ABS/RETAINED/selected-bee-action-graph.json \
  --output /ABS/NEW/retained-apple-replay
```

### Evidence

Portable evidence is in [local-validation-20260915-22eda8b](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-22eda8b/README.md).

- `failure-manifest.json` binds source/build identities, aggregate limits, graph, managed-source begin capture, native Player identity, raw archives, and restoration.
- `v02/retained-apple-replay.tar.gz` is 39,242,521 bytes, SHA-256 `4fce745688f0f0aed77bb70ad39feb4ff6db45701f1909b90137790654136cab`.
- `v03/candidate-on-debug-failure-inputs.tar.gz` is 45,703,901 bytes, SHA-256 `af3bc51c75334576199d523b493cd026f8249655bd93064cfd1cd5f82539a7a3`.
- Fresh graph: 2,766,362 bytes, SHA-256 `a1a3eede51e061b4e9da2b9d5a5f4e119b9535434e896db3a55609a7c249ae37`.
- Fresh native output: 101,101,430 bytes, SHA-256 `f731d42f4ff9a91a240afa80310e126458232bacb5859fecb4efba02823155db`.
- Attempt input inventory SHA-256: `f01a19f6b49ee2df1ae1c94699903ea47bba6b0eabce79918acbc7660c2b85ac`.
- Build GUID: `9638639b2bfe41b793b8bb629f1801ff`; input snapshot: `fdcb5eb0bef2eb34567f242de74db10a3b132cfd0d7d9712bca4e1e12cc24d17`.

Unpacked raw roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-22eda8b/v02/retained-apple-replay` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-fa63d77e368c42d0b558979fecb5fc1b`.

### Root cause

`h1_capture_attempt.Attempt` caps aggregate retained input bytes at 256 MiB. Before domain planning, `retain_declared_inputs()` copies every declared `.c`, `.cpp`, header, PCH, response, and plist input from all selected compile/link nodes into the content-addressed attempt store. The real 446-action Unity Apple graph has more than 256 MiB of unique declared native input bytes, so a legitimate graph deterministically exhausts the budget before the reviewed domain/PCH logic can run.

The Primary 250-test suite validates the graph/domain design and synthetic retention failures, but it does not execute aggregate raw-byte retention over the actual generated Apple source set. The current design therefore allows bounded portable fixtures to pass while the real graph is structurally unable to reach planning.

### Impact

No fresh provenance-bound candidate ON/Debug receipt exists. The remaining candidate ON/OFF Debug/Release builds, reproduction Debug/Release builds, V04 runtime/count/startup/capacity/performance chain, successor package, and independent whole-chain M08 are blocked. The successful Player binary cannot be used for H1 acceptance.

The additional reproduction full Editor sweep has 12 nonpasses from absent reproduction baselines/fixtures; candidate full Editor validation is 351/351 and both required reproduction H1 fixtures pass 14/14. These failures are preserved separately and are not the reason the fresh build chain stops.

### Recommended direction

Primary should redesign or explicitly resize the declared-input retention contract using measured real-graph bounds. Preserve fail-closed graph/request/config/PCH/header/response evidence and a complete source inventory; do not silently skip generated sources or broaden source-domain allowlists. A durable design should separate content identity from raw-byte storage, retain required semantic inputs in full, and use an authenticated chunked/compressed or externally bound store for the larger generated-source set with explicit disk/count/size limits.

Add a regression that executes retention against a byte-volume fixture above 256 MiB while preserving the 446-action domain/linkage shape, plus a limit-exhaustion control that proves no receipt is published. Then issue a new reviewed source anchor and rerun fresh V00–V05.

### Uncertainty

This run proves the exact aggregate-byte failure twice and captures every reached stage. Because both real attempts stop during declared-input retention, it does not establish the current implementation's six Apple probe contexts, 444 linked objects, 430/2/14 domain result, or any later compiler/PCH semantic result on the fresh source anchor. Those remain `NotRun`, not failed probe evidence.

---

## Historical blocker: published c0d3070 handoff failed its own preflight

### Symptom

At final handoff HEAD `c0d3070e15682567bb1b2d693d7c7a4f9ea802fb`, the required candidate preflight exits `1` with:

```text
Blocked: Incomplete handoff sections
```

No preflight result JSON is created. The same command was executed twice with the same result.

### Reproduction

From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`:

```sh
git pull --ff-only origin codex/assembly-shadow-r01b-h1
python3 Tools/AssemblyShadow/h1_handoff_preflight.py --project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo --role candidate --output /ABS/NEW/candidate-handoff.json
```

The checkout is exactly `c0d3070e15682567bb1b2d693d7c7a4f9ea802fb`; the code anchor is `463ec3fab5d5e3bdbd09fe1970c21bf90f26ada9`.

### Evidence

Portable evidence is in [local-validation-20260915-c0d3070](local-validation-20260915-c0d3070/README.md):

- `preflight-attempt1.*` and `preflight-attempt2.*`: raw stdout/stderr and the captured exit code;
- `handoff-section-census.json`: exact required, present, and missing headings;
- `source-state.json`: observed repository heads, worktree state, and authoritative-file hashes.

The handoff SHA-256 is `b89c4c156ae9687adaf81cc03f156cc601e58d89f8eb1ecd442ba03f8626cc68`; the preflight script SHA-256 is `994e6e48c05aa15b2c66207a256ca76dcebdc8075bb9c1350d35e1d6f55263b1`.

### Root cause

`Tools/AssemblyShadow/h1_handoff_preflight.py` requires nine literal section substrings. The new `WEB_TO_LOCAL.md` reorganized the handoff but did not preserve four required names:

- `## Implementation`
- `## Alternatives`
- `## Risks`
- `## Human review gate`

The check runs before source-target, branch, pin, or demo-source verification. The candidate pin and repository identities were manually observed as correct, but those observations cannot be promoted to a successful authoritative preflight.

### Impact

The handoff explicitly makes preflight a prerequisite for fresh V01–V05. Continuing would produce evidence against a source state that the committed authority tool refused to accept. V01–V05 are therefore `Blocked / NotRun`; no new Unity, Player, runtime, performance, successor, or M08 result exists for anchor `463ec3f`.

### Recommended direction

Preferred: publish a metadata-only handoff successor that restores the four required headings and places the current content beneath them, then run the unchanged preflight before returning to Local Validation.

If the heading contract is intentionally obsolete, update `h1_handoff_preflight.py` and its tests as a reviewed executable-input change, publish a new code anchor, and issue a matching handoff. Do not ask Local Validation to weaken or bypass the committed check.

### Uncertainty

The failure occurs before the remaining preflight stages, so this run does not establish that the tool would accept code-anchor identity after the section issue is fixed. The independently observed pins and heads match the handoff, but a repaired published handoff must still be run through the full tool.

---

## Historical blocker addressed by code anchor 463ec3f

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
