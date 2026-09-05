# M07 Unity resource and API acceptance contract

Status: implementation and offline validation in progress; Gate 3B is not yet
accepted.

## Boundary and source identity

M07 starts only from the accepted M06 four-repository pairing. It changes the
native class-layout admission rule, HybridCLR Unity resource tooling and the
isolated demo. The HybridCLR runtime public API remains the accepted M06 API.
All Player, fixture, resource and result evidence is bound to one exact source
pin file, Unity 2022.3.62f2, StandaloneOSX arm64 and a fresh `M07-Baseline-*`
identity. Local commits and tags are allowed; push and PR creation are not.

The original demo checkout and any pre-existing Unity Editor remain outside the
workflow. Unity may run only against the dedicated isolated checkout, with no
second Editor for that exact project.

## Frozen resource graph

The baseline contains exactly these seven bundles in canonical name order:

1. `additive-scene.bundle`
2. `business-scene.bundle`
3. `mixed-assets.bundle`
4. `nested-prefab.bundle`
5. `scriptable-object.bundle`
6. `serialize-reference.bundle`
7. `versioned-prefab.bundle`

The resource receipt binds the exact source assets and `.meta` GUIDs, compiler
snapshot, effective compiler/editor defines, candidate metadata DLLs, dependency
graph, resource ABI/index, bundle bytes and reconstruction proof. Source assets
are outside every `Resources` directory. The first Player scene contains only
the fixed AOT M07 bootstrap.

The native-ON Player receipt refers to the original verified resource-build
root. The immutable baseline copies those same bytes under `ResourceInputs`.
These paths are intentionally different. Identity is the resource-receipt hash,
resource ABI/index and ordered bundle name/SHA inventory, checked independently
in the Editor replay, runtime bootstrap and Python verifier.

## Patch and structural policy

The accepted positive fixtures are:

| Patch | Closure root | Deployment |
| --- | --- | --- |
| P01 | Internal | DLL-only, original bundles |
| P02 | Extensibility reverse closure | DLL-only, original bundles |
| P03 | Contracts full closure | DLL-only, original bundles |
| P04 | Internal private nonserialized field | DLL-only, original bundles |
| P05 | Internal appended serialized field | DLL plus all required rebuilt bundles |

`P05-DllOnly`, `P14-ClassRename` and `P15-SerializeReferenceRename` must each
produce the real `ResourceRebuildRequired` policy failure and no patch output.
P05 compilation and resource construction occur in the same guarded structural
Editor domain. A separate prepare/compile/restore/finalize workflow records the
original scripting defines, restores them in `finally`, replaces the complete
original ProjectSettings bytes only after Unity proves the change was confined
to that define entry, and validates the fixture in a fresh baseline domain.

The native metadata gate distinguishes two questions. Existing managed fields,
base/interface sets and layout are exact. A candidate cannot shrink or change
an existing field. Appended private primitive storage may be admitted physically;
Unity serialization remains conservative and requires the Editor resource ABI
gate and matching rebuilt resources before startup.

## Runtime ordering and cases

Every positive case follows:

```text
read and hash all manifests/resources
  -> resource ABI precheck
  -> Configure / Begin / Stage / Validate / Commit
  -> verify committed assembly modes
  -> load any business bundle or scene
  -> exercise Unity APIs and serialization
  -> capture final native diagnostics
  -> create a new result file
```

The exact 14-process inventory is T07-01-Prefab-P01,
T07-02-Nested-P02, T07-03-FullClosure-P03, T07-04-UnityApis-P01,
T07-05-Scriptable-P03, T07-06-SceneSingle-P01,
T07-07-SceneAdditive-P03, T07-08-SerializeReference-P03,
T07-09-Messages-P01, T07-10-Cache-P03,
T07-11-DelayedCatalog-P03, T07-12-P04-NonSerialized,
T07-13-P05-Rebuilt and T07-14-FeatureOff. Each uses a distinct actual operating
system process and unique result/log path. Only T07-14 uses the native-OFF
Player.

The launcher hashes the complete native-ON and native-OFF Player app trees,
not only their executable/native metadata subset, before the first process and
after the last. This binds the serialized bootstrap data and every other Player
file against cross-case mutation.

The runtime proof covers immutable prefab deserialization/reload, nested
cross-assembly references, ScriptableObject asset/create/clone paths,
SerializeReference concrete types, `MonoScript.GetClass`, generic and `Type`
Add/GetComponent APIs, Single/Additive/delayed/repeated scene loading,
DontDestroyOnLoad, UnityEvent/string messages, serialization callbacks,
lifecycle counters, unload(false), unload(true), UnloadUnusedAssets and GC.
There must be no unexplained baseline resolver use after Commit.

Because `MonoScript` is Editor-facing and may not be exposed in the Player,
that row accepts only four explicit evidence labels: direct `GetClass`, missing
script object, missing `GetClass`, or its documented not-supported exception.
The three fallback labels resolve the exact component embedded beside the
Editor-generated carrier; its active logical identity and unload/reload
stability remain mandatory. Other reflection failures and a callable
`GetClass` returning null are not fallback cases.

## Acceptance

Gate 3B requires all of the following from one frozen pairing:

- package and demo Editor tests, the complete Python suite and focused native
  layout tests pass without relevant skips;
- native-ON and native-OFF Players are genuine distinct builds with hash-bound
  linked assemblies, native metadata and resource inputs;
- five positive fixtures, three real rejected fixtures and the independent
  Editor reconstruction replay pass;
- all 14 fresh Player processes exit zero with `result=Passed`, distinct PIDs
  and unchanged immutable input hashes;
- `verify-m07-results.py` emits a new strict `result=Passed`, `caseCount=14`
  receipt without `--allow-incomplete`;
- evidence is retained losslessly, committed, rechecked from the current
  checkout and a clean detached evidence commit, and independently reviewed;
- matching local annotated `assembly-shadow-m07-unity-assets` tags exist in all
  four repositories and the post-tag audit passes.

Editor compilation, synthetic schemas, resource build success or source review
alone are not Player acceptance. This milestone does not claim M08 production
build integration, M09 download/security/rollback, other platforms, arbitrary
Addressables installations or cross-version Unity serialization compatibility.
