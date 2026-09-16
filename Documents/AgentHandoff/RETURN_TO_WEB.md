# Local Validation → Primary Implementation

## Current blocker: H1 fixed-byte witness is rejected by frozen M07 bootstrap policy

### Symptom

At candidate handoff `e96bc073e66c1ecdf1f461f9286422a7c9d26f82`, source anchor `3242b071540278510ea4ae287c70e37fc4c60340`, and reproduction-tooling revision `ba8fee33753a5ebc215b7a98739e343d8e05572e`, V00–V03 pass. Candidate count then passes 132/132 and all eight unfixed reproduction cells are freshly classified. The required fresh M07 baseline workflow fails in real Unity 2022.3.62f2 before it can produce baseline fixtures or Players:

```text
ShadowBuildException: PolicyValidation: BootstrapReflection: Bootstrap reflection reference is not an approved entrypoint: AssemblyShadowDemo.Bootstrap -> AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness|9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27
  at HybridCLR.Editor.AssemblyShadow.ShadowPolicyValidationResult.ThrowIfInvalid()
  at AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs()
```

### Reproduction

After V03 has installed/verified the pinned runtime and produced the six fresh Players, run:

```sh
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-M07Build.ps1 \
  -ProjectPath /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  -BaselineId M07-Baseline-H1-e96bc07-20260916 \
  -TimeoutSec 28800
```

`AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs` exits 1 on the policy exception.

### Evidence

Portable evidence is in [local-validation-20260916-e96bc07](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-e96bc07/README.md).

- `v04/m07-baseline/stdout.log`: complete PowerShell and Unity failure output.
- `v04/m07-baseline/exit-code.txt`: exit 1.
- `v04/m07-baseline/M07Bootstrap.postfailure.diff.gz` and `AssemblyShadowSettings.postfailure.diff.gz`: exact gzip-preserved workflow-created mutations before restoration.
- `v04/m07-baseline/restoration.txt`: working and HEAD blob equality after exact two-file restoration.
- `v04/control-and-fixture-metadata.tar.gz`: post-failure and post-restoration preflight attempts plus all V04 control records.
- `failure-analysis.json`: machine-readable cause/impact/recommendation.
- `results-summary.json`: prior passing stages and blocked downstream stages.

Post-restoration candidate preflight again returns `SourceTargetVerifiedNotBuildAccepted`; tooling preflight again returns `BehaviorAndToolingSourcesVerifiedNotBuildAccepted` with exact 9 replacements, 2 authenticated deletions, and `editorSourceCompatibility.status=Compatible`.

### Root cause

`H1CountEarlyStartup.LoadOrdinaryWitness` verifies the exact M00 image SHA-256 and calls `Assembly.Load(byte[])`. `ProjectSettings/AssemblyShadowReflectionBindings.json` declares the exact site as `FixedAssemblyBytes`, including method signature/hash, operation index, image SHA-256, provider identity, semantic variants, and image path.

The M07 compiled-policy scan also emits that acquisition as a bootstrap reflection reference whose target is the image hash. `ShadowAssemblyPolicyValidator.ValidateReflection` sends it through `BootstrapIsolationRule.IsApprovedReflection`, which accepts only a matching `bootstrapEntrypoints` declaration. `ProjectSettings/AssemblyShadowDependencies.json` has no matching H1 fixed-byte entry, so the valid fixed-image contract and the bootstrap-reflection policy model disagree.

The design allowed this because the H1 count build path injects an empty explicit dependency configuration and its focused tests do not run the global M07 `ValidateCompilerInputs` path after introducing the H1 fixed-byte witness. V00/V01 therefore prove source/tool compatibility and focused behavior without exercising this cross-policy integration.

### Impact

Fresh M07 baseline/fixtures/editor replay are unavailable. Startup11, 8192/8193, required lazy/dense/generic/array/reflection/FieldRVA/old-Player and M03–M07 coverage, and controlled Development performance are `Blocked / NotRun`. V05 successor packaging and independent whole-chain M08 are also `Blocked / NotRun`. Last independent M08 remains `FAIL`; Human Review Gate is not ready; R02 remains closed.

The 132 candidate cells, 8 reproduction observations, and V00–V03 evidence remain valid partial evidence only. They do not replace the missing fresh baseline/downstream chain.

### Recommended direction

Define and review how a `FixedAssemblyBytes` bootstrap acquisition participates in global bootstrap policy, then make the reflection-binding contract and `BootstrapIsolationRule` agree without a broad waiver. Add an integration regression that runs M07 `ValidateCompilerInputs` with the exact H1 site and rejects changed method hash, operation index, image hash, provider identity, or undeclared byte-load sites.

Also update `Invoke-M07Build.ps1` to restore its scene/settings mutations in a `finally` path when validation fails. Local captured and exactly restored the two files, but the workflow should guarantee this itself.

Publish a new reviewed source anchor and rerun fresh V00–V05. Do not ask Local Validation to broaden `bootstrapEntrypoints`, bypass the policy check, or reuse the partial V04 chain as whole-chain acceptance.

### Uncertainty

The exception occurs before fresh M07 resources, Players, and replay exist. This run makes no claim about downstream startup, capacity, retained coverage, or performance behavior after the policy models are reconciled.

---

## Historical blocker addressed by tooling handoff ba8fee3: tooling successor retained an incompatible historical Editor test

### Symptom

At candidate handoff `534b03eb49140eb7f9d9fbdb64217e113a317626`, candidate source anchor `1b1cc9fe192b88be2a20fad31ea030b1e30be669`, and reproduction-tooling revision `0c9c2508d94a097dff50028212a01695c8e29c60`, both V00 authority checks pass. Candidate V01 Python/Bee/Unity/focused NUnit checks pass. The exact reproduction-tooling checkout then fails its first Unity 2022.3.62f2 compilation:

```text
Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs(13,43): error CS0426: The type name 'Capture' does not exist in the type 'H1ManagedSourceProvenance'
```

No reproduction-tooling NUnit, Player build, provenance receipt, or `validation-tooling-binding.json` can be produced.

### Reproduction

Use the exact V00-verified tooling checkout and protected sibling pins, then invoke the repository compile helper:

```sh
cd /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro_tooling/hybridclr_demo
pwsh -NoProfile -File .agents/skills/unity-debug/scripts/Invoke-UnityCompile.ps1 \
  -AsJson -TimeoutSec 1800
```

The process exits 1 after Unity reports the CS0426 compiler error.

### Evidence

Portable evidence is in [local-validation-20260916-534b03e](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-534b03e/README.md).

- `v00/candidate-handoff.json`: candidate `SourceTargetVerifiedNotBuildAccepted`.
- `v00/reproduction-tooling.json`: exact split authority `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`.
- `v01/reproduction-tooling-unity-compile.json`: structured failed compile result.
- `v01/reproduction-tooling-unity-compile.unity.log`: complete Unity import/compiler log.
- `v01/reproduction-tooling-compile-blob-identity.txt`: exact test/bridge blob identities.
- `v01/reproduction-tooling-vs-candidate-test.diff`: the candidate source anchor has deleted the historical test path.
- `v01/reproduction-tooling-postcompile.json`: source/tool authority remains exact after failure.
- `failure-analysis.json`: direct issue, root cause, design gap, and disposition.

The tooling checkout and protected reproduction head share test blob `635847f71c72fa0f3b191ff53746d6cfe1efc7d1`. The tooling checkout correctly carries candidate bridge blob `2fdddcde4e9f1c62b93cd5f162aa922c67697628`. Candidate source anchor `1b1cc9fe...` has no `Assets/AssemblyShadowDemo/Tests/Editor/H1ManagedSourceProvenanceTests.cs` path.

### Root cause

The tooling successor overlays current schema-3 `H1ManagedSourceProvenance.cs` onto the protected historical project, but its exact nine-file override map leaves the tracked historical `H1ManagedSourceProvenanceTests.cs` in place. That test declares `H1ManagedSourceProvenance.Capture` and calls the old two-argument capture API. The current bridge no longer defines the nested type, so the resulting authenticated tree is not compile-compatible.

The design gap is dependency closure: V00 authenticates the declared native/managed validation files and the exact protected-head delta, but does not include or reject protected tracked Editor tests that compile against the overlaid validation APIs. Primary's bounded Python suite did not compile the assembled tooling checkout in Unity.

### Impact

V01 reproduction-tooling Unity/NUnit is incomplete. V02–V05 are `Blocked / NotRun`; no fresh six-build set, reproduction tooling binding, runtime/count/startup/capacity/performance evidence, successor package, or independent M08 can be accepted. Last independent M08 remains `FAIL`; Human Review Gate is not ready; R02 remains closed.

The candidate-only V01 passes are partial regression evidence and do not substitute for reproduction compilation or current-source build acceptance. Historical candidate V02/V03 evidence remains unchanged and is not relabeled.

### Recommended direction

Publish a new tooling-only successor whose reviewed exact delta either deletes the obsolete test path, matching candidate source anchor behavior, or replaces it with a current schema-3 test that compiles against the overlaid bridge. Update `source-targets.json` tool/override authority and split-tooling regressions accordingly.

Add a bounded integration check that constructs the exact protected-head-plus-tooling tree and compiles all tracked Editor sources, or at minimum audits reverse source dependencies of every overlaid C# validation type. This must run before the final handoff bytes are published.

After publication, rerun fresh V00–V05. Do not reuse this failed checkout as acceptance evidence and do not broaden the allowlist in Local Validation.

### Uncertainty

The compile failure occurs before any reproduction Player build, so this run provides no new evidence about receipt binding or runtime behavior. Once the stale test dependency is corrected, fresh V01 compilation and the complete V03 reproduction pair remain necessary to validate the new tooling design.

---

## Historical blocker addressed by tooling handoff 534b03e: protected reproduction invoked obsolete project-local provenance policy

### Symptom

At handoff `9568ea386822b4e8e48ff73e793d4a2cd09092dc`, source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a`, V00–V02 pass and all four candidate V03 modes pass. The fresh protected reproduction ON/Debug Unity Player build reports success, seals input snapshot `7d1349c55854ce6f121eafef0312eb04da6698a7e245cc33b2ece52fa2654073`, and produces native SHA-256 `4ad497816822932021d89879e5f5d7c7f490a4b0ae5fda4994498281a278fae5`. Its mandatory post-build provenance step then fails:

```text
Failed: Translation units disagree on effective diagnostic macros (link flags are not compile evidence)
```

No `h1-compiler-provenance.json` or build receipt is published. The batch restores the diagnostic scene/settings exactly and exits 1. Reproduction ON/Release is not run.

### Reproduction

After the accepted V02 smoke, run the handoff-owned continuation exactly:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /usr/local/bin/pwsh \
  --scope all \
  --reuse-smoke /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-0e2d7991d39e47d3a508b13206945aa2/build-receipt.json \
  --output /ABS/NEW/v03/all \
  --execute
```

The first four candidate results pass. The fifth mode, reproduction ON/Debug, builds the Player and then fails in the reproduction checkout's `Tools/AssemblyShadow/h1_native_capture.py`.

### Evidence

Portable evidence is in [local-validation-20260916-9568ea3](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-9568ea3/README.md).

- `v03/build-runner-results.tar.gz` retains complete runner output and raw Unity logs for every reached mode.
- `v03/reproduction-on-debug-failure/original-request.json`: exact request, SHA-256 `d0264e40f116445884696ebbd56564622722c2b20ba78835b7e5a741439095e1`.
- `selected-bee-graph.json`: exact fresh graph, 2,796,905 bytes, SHA-256 `aaaedafc0c9d1a5e5410090d396d906ac1aced72b79965f3fe14d072ee22879d`.
- `macro-domain-census.json`: 446 compile actions, one unambiguous selected native output, zero graph errors.
- `failure-identity.json`: build GUID, input snapshot, native/config/request/graph hashes, and restoration status.
- `tool-identity.json`: candidate/reproduction validation-tool hashes and availability.
- `candidate-tool-diagnostic-result.json`: `DiagnosticReplayVerifiedNotBuildAccepted`, proof SHA-256 `a4425ebca605487b7c57fa851e6ac5f03f22d0e766da642934b4191b0cd5fc5d`.
- `candidate-tool-store-verification.json`: 451 retained objects, 317,525,404 logical bytes, 72,486,391 stored bytes, independently verified.

The reproduction project-local `h1_native_capture.py` SHA-256 is `ec09eb58b4b9cf632d8ec68d570c7a0a70a3faf56fc69bb42cf9217ff9c7081a`; the candidate source anchor's current file is `17022d2e55421730a1e280fc43ffc3eb2f4ad6d16458c5d47a61483726e6c1b7`.

### Root cause

`h1_count_build_batch.py` selects the project root per role, and Unity's `H1CompilerProvenance.CaptureAfterBuild` invokes `Tools/AssemblyShadow/h1_native_capture.py` from that target project. The protected reproduction demo is intentionally frozen at published head `352d7474dd7c2ffd9b9501d8fa42334a3b236e05` to preserve unfixed count behavior, so it also retains the old capture implementation that applies one global diagnostic-macro equality predicate before domain-aware PCH probes.

The candidate source anchor contains the reviewed Apple macro-domain and retention implementation. Running that current diagnostic-only tool against the exact failed reproduction request and graph passes all probe/store checks. The reproduction graph is therefore supported by the current policy, but the strict build does not execute that policy because tool selection is coupled to the protected behavior checkout.

The design permits this because build-under-test source selection and acceptance-tool selection share one project root. Freezing the reproduction behavior unintentionally freezes obsolete validation policy as well.

### Impact

The reproduction Player has no valid compiler provenance or build receipt and cannot enter V04. Reproduction ON/Release, the 132 candidate count cells, 8 reproduction cells, startup11, capacity boundaries, replay, performance pairs, successor package, and independent whole-chain M08 are `Blocked / NotRun`. Human Review Gate is not ready and R02 remains closed.

The four candidate builds are valid partial evidence only. They do not substitute for the required reproduction pair or whole-chain M08.

### Recommended direction

Primary should decouple the reviewed validation-tool bundle from the protected behavior source. A durable successor can pin and authenticate one candidate-owned tool bundle for both roles while keeping each role's project, native source, source-pin bytes, Player inputs, and build outputs distinct. The receipt must record tool-bundle identity and target-role identity, and the preflight/batch regressions must reject tool drift or cross-role source substitution.

An alternative is a reviewed reproduction-demo successor that changes only validation tooling while cryptographically preserving the unfixed behavior/native pins and reproduction code anchor. That conflicts with the current `publishedHead` preservation contract unless `source-targets.json` and the handoff are explicitly revised, so Local Validation did not attempt it.

Add an integration fixture that runs the strict all-mode batch with a frozen reproduction behavior checkout whose local tools predate the candidate policy. The fixture should prove the selected current tool bundle is exact, role-specific source bindings remain unchanged, and no diagnostic replay is promoted to a build receipt.

### Uncertainty

The candidate-tool replay proves the exact graph is compatible with current macro/PCH/store diagnostics. It does not prove that a future decoupled invocation is correctly bound into Unity's build receipt or managed provenance chain. That binding requires Primary design and a fresh V03 rerun. The unfixed runtime count behavior remains `NotRun` because the failed Player is unreceipted.

---


## Historical blocker addressed by handoff 9568ea3: published schema-3 handoff failed its authoritative preflight

### Symptom

At published handoff `2ca4720508dc114e9c55756fcb2a068678dff90c`, source/implementation anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a`, the required V00 command exits `1` with:

```text
Blocked: Incomplete handoff sections
```

No preflight result JSON is created. Candidate and protected repository identities independently match the handoff, but the executable authority check stops before source-target verification.

### Reproduction

From `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo`:

```sh
git pull --ff-only origin codex/assembly-shadow-r01b-h1
python3 Tools/AssemblyShadow/h1_handoff_preflight.py \
  --project /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --role candidate \
  --output /ABS/NEW/v00/candidate-handoff.json
```

The checkout is exactly `2ca4720508dc114e9c55756fcb2a068678dff90c` and contains source anchor `5f561abdfbe020d1d480594a2130c5ec846c0e6a` in its history.

### Evidence

Portable evidence is in [local-validation-20260916-2ca4720](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260916-2ca4720/README.md).

- `v00/preflight.stderr.log`: exact error.
- `v00/preflight.exit-code.txt`: exit `1`.
- `v00/handoff-section-census.json`: required/present/missing heading census.
- `source-state.json`: candidate, protected pins, preservation boundaries, and authority hashes.
- `WEB_TO_LOCAL.md` SHA-256: `33f23574233ddcfba36438bc6c393557ac34df879ed8210f33cb44efdbf8230c`.
- preflight script SHA-256: `994e6e48c05aa15b2c66207a256ca76dcebdc8075bb9c1350d35e1d6f55263b1`.

The committed preflight requires these exact literal substrings:

```text
## Objective
## Source targets
## Implementation
## Local validation
## Failure evidence
## Alternatives
## Risks
## Local correction boundary
## Human review gate
```

The published handoff headings are:

```text
## Objective
## Exact source targets
## Repair contract
## Primary review and bounded validation
## Local Validation
## Failure evidence
## Local correction boundary
## Gate
```

Only three required literals are present. The six missing literals are `## Source targets`, `## Implementation`, `## Local validation`, `## Alternatives`, `## Risks`, and `## Human review gate`.

### Root cause

`WEB_TO_LOCAL.md` was reorganized with semantically meaningful headings, but the unchanged preflight uses a case-sensitive substring contract. `## Exact source targets` does not contain the literal `## Source targets`, `## Local Validation` differs by case, and four other required headings were renamed or omitted. The handoff document and its committed validator are incompatible.

The design allows this recurrence because heading compatibility is not validated in Primary's 283-test publication workflow. The same class previously blocked handoff `c0d3070`; the current Primary repair updated the handoff again without an executable preflight result bound to the final published bytes.

### Impact

The handoff explicitly says: “If V00 fails, stop before V01–V05.” Therefore schema-3 Unity/Bee validation, fresh builds, runtime/count/startup/capacity/performance, successor packaging, and independent whole-chain M08 are all `Blocked / NotRun`. Human Review Gate is not ready and R02 remains closed.

### Recommended direction

Preferred: publish a metadata-only successor that preserves all current content while restoring the six exact required heading literals, then run the unchanged preflight against the final committed handoff before returning it to Local Validation.

If the literal-heading contract is intentionally obsolete, update `h1_handoff_preflight.py` and its regression tests as a reviewed executable-input change, publish a new source anchor, and issue a matching handoff. Do not ask Local Validation to bypass or rewrite the authority document.

Add a publication check that executes `h1_handoff_preflight.py` against the final branch HEAD after the last handoff edit. This prevents semantically equivalent heading changes from publishing an unusable Local handoff.

### Uncertainty

The failure occurs before source-target and schema-3 checks. Independently observed heads and pins match, but this run provides no schema-3 Unity/Player evidence and must not be interpreted as a finding about the response-scope implementation itself.

---

## Historical blocker addressed by source anchor 5f561ab

### Graph-wide response stability rejects valid assembly-local cache chains

### Symptom

At handoff `3695905b1981a5cecbd444e27114c34cbc3bf255`, source/implementation anchor `0387feb4344bbe95fd7db524d6e0bae759adc203`, V00/V01 pass and the fresh candidate ON/Debug Player plus native provenance pass. Managed verification fails with:

```text
Blocked: Cached managed response changed or was unavailable: /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/Library/Bee/artifacts/StandaloneOSX_CodeGen/Unity.Burst.CodeGen.rsp
```

The normal Bee cache was preserved; no clean/recompile was forced and `--reuse-proof` was not used. The one retained Player DAG contains exactly one cached compiler action for each required assembly. Both actions have unchanged direct response files, all 201 dependencies, compiler output, reachable downstream DLLs, and exact fresh Player input path/hash/size bindings. The verifier nevertheless emits no `BeeCacheHitBoundToFreshPlayerInput` row.

### Reproduction

After V00/V01 and pinned candidate install/runtime verification, run from the candidate checkout:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /usr/local/bin/pwsh \
  --scope smoke \
  --output /ABS/NEW/smoke \
  --execute
```

The batch exits 1 at `verify-managed.log`. Player/native build and verification complete first, `failed.json` records `candidateAcceptance=false`, and `restored.json` records exact restoration.

### Evidence

Portable evidence is in [local-validation-20260915-3695905](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-3695905/README.md).

- Cached Player DAG: `Library/Bee/200b0aPDevDbg.dag.json`, 9,281,264 bytes, SHA-256 `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af`.
- End census: 302 observations, 295 unchanged and 7 changed.
- Bootstrap action: node 273, SHA-256 `147ff4fdd7fb75e65bf9ac1e541096a0a7a72b82bfe1e32ddafab91101cef6a7`; 33 sources; 201 dependencies; 5 reachable outputs; fresh Player input 567,296 bytes, SHA-256 `863743cc1aba2835c5491e01277d9a054e9cf590923059627a4c42667aaa8c39`.
- Diagnostics action: node 327, SHA-256 `67df1baf137e19ff95e6d36cf579e4065b5c57281ec80b1ed2ee17734ca560cc`; 7 sources; 201 dependencies; 3 reachable outputs; fresh Player input 111,616 bytes, SHA-256 `d8c6a81f7c0f489d8de76c60454e8ebd06c5448d60c9ee67e7940c60cc10dd04`.
- The seven changed responses are unrelated `StandaloneOSX_CodeGen` inputs: `Unity.Burst.CodeGen.rsp`, `Unity.Burst.rsp`, `Unity.HybridCLR.AssemblyShadow.CodeGen.rsp`, `UnityEditor.TestRunner.rsp`, `UnityEditor.UI.rsp`, `UnityEngine.TestRunner.rsp`, and `UnityEngine.UI.rsp`.
- Every before/after diff adds only `ASSEMBLY_SHADOW_H1_COUNT_DIAGNOSTICS` and `ASSEMBLY_SHADOW_R01B_DIAGNOSTICS`.
- `v02/managed-cache-census.json` records all observations and per-assembly chain material.
- `v02/managed-source-provenance.tar.gz` retains the complete 36 MiB unpacked managed ledger and blobs, SHA-256 `3dc8967fc79389a83e2e9fca453fe44644f23344d4b2482795cb8fa56f069cc4`.
- `v03/fresh-native-provenance.tar.gz` retains complete compiler/PCH/domain/store evidence, SHA-256 `c52e39bc207e7736145522830c45ab6deb5ed044be97982409c5565e6f1ab3a9`.
- `v03/smoke-runner.tar.gz` retains the raw batch failure, native verification, and restoration, SHA-256 `b3839f62d9a595b331e384734265ca9eb9a50aeac61dab724022a7e75f90e059`.

Build GUID is `f6aa5298e2284385a9d458bb58f08e68`; input snapshot SHA-256 is `ea5f83c1c1de80ce83bc9d121e4138843de8fb6234681e11a38c090d1ed55713`; native library SHA-256 is `117e733567a7b6d52742c93281a3842773af2820301dee602264887fdf4b2e85`.

### Root cause

`collect_cache_graphs()` resolves all response files while parsing the full DAG and, when either required compilation is found, attaches every resolved response as `graph_row.responseFiles`. On this real graph that is 92 response files, including unrelated `StandaloneOSX_CodeGen` actions.

`_cache_matches()` validates every graph-level response with `_require_unchanged()` before filtering `graph_row.compilations` by the requested assembly. Staging the two diagnostic defines legitimately rewrites seven CodeGen responses. The first changed row aborts verification, even though neither required compilation references it and both required assembly-local chains are otherwise complete and unchanged.

The bounded eight-test cache suite does not model this real graph shape. Its valid-hit and rejection fixtures prove the intended checks for a small compilation-scoped response set, but do not exercise an unrelated changed response elsewhere in the same DAG.

### Impact

No accepted candidate ON/Debug smoke exists. The remaining five builds, 132 candidate count cells, 8 reproduction cells, startup11, capacity/boundary/performance chain, successor package, and independent whole-chain M08 remain blocked. Human Review Gate is not ready and R02 must remain closed.

The additional broad Python inventory has one platform-path skip, and the reproduction full Editor sweep has the same 12 historical missing-fixture/baseline nonpasses. Required H1 Python, candidate Unity, candidate/package NUnit, reproduction compile, and focused reproduction H1 fixtures pass; those results do not override this Player provenance failure.

### Recommended direction

Primary should make cached response retention and end-observation requirements follow the recursively resolved response closure of each candidate compiler action. Keep the DAG identity, action transcript, source set, compiler/tool/dependency closure, Csc output, reachable downstream DLLs, fresh Player input binding, and uniqueness checks fail closed. Unrelated response files in the same DAG may remain in an audit census, but their mutation should not invalidate a compilation that cannot reach or reference them.

Add a regression fixture with two required unchanged cached compiler chains plus one unrelated response/action in the same DAG that legitimately changes. Require both cache-hit rows to pass while existing changed-response controls still fail when the changed response is in a required action's recursive closure. Also retain controls for ambiguous actions, changed dependencies, stale outputs, output creation after begin, and wrong fresh Player binding.

Do not solve this by allowing any changed response, ignoring response bytes, forcing cache deletion, using `--reuse-proof`, or selecting a candidate by recency/order. Publish a reviewed source anchor and rerun fresh V00–V05.

### Uncertainty

The retained DAG establishes that the seven files are outside both required actions' direct response source lists, and the full per-assembly dependency/output chains are unchanged. Primary should confirm whether Bee has any implicit response inclusion rule beyond the parsed recursive `@response` closure before narrowing the acceptance scope.

---

## Historical blocker addressed by source anchor 0387feb

### Fresh Player reuses managed Bee actions that capture excludes

### Symptom

At handoff `8f5bcaa687e33e8666eacc942b5e414a83b737fc`, source anchor `91ebef56eaa7034ed49a80bced422ea4c067d2fe`, the real retention repair works as designed. Both the retained Apple replay and fresh candidate ON/Debug capture cross the former 267,613,743-byte boundary and independently authenticate 318,212,421 logical bytes stored in 72,612,459 bytes. The fresh Player builds; native compiler provenance, Apple domain/PCH probes, strict native verification, independent store verification, and exact restoration pass.

The subsequent managed-source verifier fails:

```text
Blocked: Missing or ambiguous managed action chain for AssemblyShadow.R01BDiagnostics
```

`ManagedSourceProvenance/h1-managed-source-capture.json` contains one newly changed native Bee graph and zero managed compilation rows. The exact `AssemblyShadowDemo.Bootstrap` and `AssemblyShadow.R01BDiagnostics` Player compiler actions are present only in pre-existing `Library/Bee/200b0aPDevDbg.dag.json`; that DAG's SHA-256 is unchanged since the begin capture, and both compiler outputs existed before the build.

### Reproduction

After V00/V01 and the pinned candidate install/runtime verification, run from the candidate checkout:

```sh
python3 Tools/AssemblyShadow/h1_count_build_batch.py \
  --candidate /Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo \
  --reproduction /Users/ah/GitHub/hybridclr/assembly_shadow_h1r_repro/hybridclr_demo \
  --unity /Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity \
  --pwsh /usr/local/bin/pwsh \
  --scope smoke \
  --output /ABS/NEW/smoke \
  --execute
```

The batch exits 1 at `verify-managed.log` after producing and strictly verifying the native receipt. `failed.json` records `candidateAcceptance=false`; `restored.json` records `ExactRestorationVerified`.

### Evidence

Portable evidence is in [local-validation-20260915-8f5bcaa](../../Docs/AssemblyShadow/M07R/R01B/H1-Remediation/local-validation-20260915-8f5bcaa/README.md).

- Build GUID: `540065befa904f7f880ab13416c0f852`; input snapshot: `7ddd2f21c4718469ec06998ce3f19e2ff0100cc28eda2c4b5a2431a6eab753d5`.
- Native library SHA-256: `9acf78528cda4587f0cf97b4a2e565767e57962c863da19f30479276f91c4ba0`.
- Build receipt SHA-256: `3043f69397cb8cc0dc4a798cbfe851f02f65031a6d8a23f2b31f09dec1ce1a92`.
- Compiler provenance SHA-256: `13a2fe9f1ce20a8db3d120b38e18e93040117edf94ea8fb8127cd4acbd998109`.
- Retention inventory SHA-256: `089060a3ca2ea4e9eb162c4f9bf9b90a77819b455bed7faa8119ed6ab45629dc`.
- Player managed DAG SHA-256: `46997e81b065cdd57c5d93913e076192fdc79e809d6757e9045e1bafef5080af`; it existed before and did not change during the build.
- `v03/managed-action-census.json` records all four matching Editor/Player actions, their node indices, source/dependency/response counts, pre-existence, graph freshness, and Player reachability.
- `v03/candidate-on-debug-managed-provenance-failure.tar.gz` is 81,310,527 bytes, SHA-256 `a82275037f61c3e42e7d298a0f10b5446b1b7fd7cea3cadef80fdef584f76658`.
- `v02/retained-apple-replay.tar.gz` is 79,418,186 bytes, SHA-256 `a36c324c635911a4c68f814a5d17cc7819f32d57ea76f5b8c7c398aee08632d6`.

Full unpacked roots remain at `/Users/ah/GitHub/hybridclr/h1-local-validation-20260915-8f5bcaa` and `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo/_temp/AssemblyShadow/H1CountBuild-e347902b06224cbc8af39ec58902fafa`.

### Root cause

`h1_managed_provenance.end()` selects Bee DAGs that are new or whose byte hash differs from `beeGraphsBefore`. Unity legitimately reused cached Player C# outputs for this build, so the authoritative managed compilation DAG and DLLs remained byte-identical. The new native DAG is captured, but it has no C# compiler actions; managed verification therefore has no direct action chain for the two required assemblies.

The existing exact-reuse route does not close this run. It requires a prior direct managed proof for the same source-pin SHA, while the current source anchor changed that SHA. The batch's `--reuse-smoke` path revalidates an entire previously accepted source chain and cannot promote this failed managed capture.

The design allowed this because managed provenance equates “freshly used in this build” with “new or byte-changed during this build.” Bee's valid incremental reuse breaks that implication: an unchanged cached action/output can still be the actual input used by the fresh Player.

### Impact

There is no accepted candidate ON/Debug smoke result even though the Player and native receipt are valid. The other five builds, 132 candidate count cells, 8 reproduction cells, startup11, capacity/boundary/performance chain, successor package, and independent whole-chain M08 remain blocked. Human Review Gate is not ready and R02 must remain closed.

The reproduction optional full Editor sweep again completed 330/342 with the same 12 historical missing-fixture/baseline failures; focused required H1 fixtures passed 14/14. Those preserved nonpasses are separate from this blocker.

### Recommended direction

Primary should define and implement a reviewed fail-closed proof for cached managed Bee action reuse. The proof should bind the exact unchanged DAG action, response files, source/config/dependency bytes, output DLL hash/MVID, Player input binding, build/source pin, and evidence that the selected cached output is the one consumed by the fresh Player. It must distinguish legitimate unchanged reuse from stale or unrelated cached artifacts.

An alternative is to force a scoped managed recompile before the build and capture the resulting changed action/output, provided that the operation and before/after state are deterministic, restored, and provenance-bound. Do not accept all pre-existing DAGs by name or path, and do not waive freshness because matching actions happen to exist.

Add a regression in which native inputs rebuild while the two managed assemblies are valid cache hits, plus stale-output, ambiguous-action, changed-source, changed-response, and wrong-Player-binding rejection controls. Publish a new reviewed source anchor and rerun fresh V00–V05.

### Uncertainty

This run establishes that the matching cached actions reach the Player input and that their files existed unchanged before the build. It does not independently prove why Unity selected those cached outputs or whether a hidden freshness token exists elsewhere in Bee state. Primary review must choose the design-authoritative proof rather than treating the local census as acceptance.

---

## Historical blocker addressed by source anchor 91ebef56

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
