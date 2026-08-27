# M01: Unity 2022 serialized script resolution

Status: native investigation and real Player validation complete. Proposed Gate 1:
**CONDITIONAL-GO**, subject to independent acceptance recorded in
`../M01/M01-review.md`. This is a P01 feasibility result, not production approval.

## Scope and fixed inputs

Unity 2022.3.62f2, macOS ARM64, real IL2CPP Development Player. This substitutes
the available macOS target for the plan's suggested Windows x64 target. The
original demo checkout and its pre-existing Editor remain untouched; all demo
changes and generated files are in `hybridclr_demo_shadow`.

Only `AssemblyA.Implementation.Internal` is shadowed. Contracts, Extensibility,
and both external consumers stay AOT. Bootstrap has no compile-time reference
to any business assembly. The Player retains the original Internal AOT code.

P01 is the same-name Internal DLL, compiled with `ASSEMBLY_SHADOW_P01`; it changes
only `BASELINE-INTERNAL` string operands to `PATCH-P01-INTERNAL`. It does not
change types, inheritance, interfaces, fields, serialized assets, or bundles.

The first bundle bytes are frozen read-only under
`BaselineArtifacts/StandaloneOSX/M01-Baseline-v1`. An initial catalog-finalization
error was resumed by verifying the existing `.building` manifest and bundle
bytes, writing the missing catalog, and moving the completed directory. No
bundle was rebuilt during that recovery or later patch tests.

| First-build artifact | SHA-256 |
| --- | --- |
| business-scene.bundle | f4e0106dff4cc822a66a8b13557336023742b010182065a8da633cc5feac2486 |
| versioned-prefab.bundle | 985a762b8db78f128aea520571d79a553e0f7e37d9a7cd897e50366e70bcd98a |
| versioned-data.bundle | 7f93e66e3537d7b3634ff725e35c20dffaec172d2424cee789ff959ef0d72935 |
| baseline-manifest.json | e0125ed2b59177fb8577dab0498325a4a489404d3147b7bb857f442a9464928d |
| P01 Internal DLL | d8df67c0b817977987c33cb97d1911fca08da9fef02325b804985ac72186e291 |

Baseline compiler MVID: `d8de3f12-ebd6-442a-9631-0611025de8e9`.
P01 compiler MVID: `b1032359-f7de-4c8c-9995-20e9455266e0`.
The manifest also records all three business DLL/PDB snapshots and prefab,
MonoScript, data asset, and scene GUIDs.

## Observed name-only experiment

Native source: il2cpp_plus `5581012fda51e9aea5ee8a2800d32d1977c2e389`,
hybridclr `1bc69c3acc2434804e71560418df8c728a63360e`, package
`a1d2697dfa3b1c510d5bfe5cf5e513886a3af78a`.

The corrected harness build in `_temp/UnityExec_20260827_051519.log` succeeded.
Its GameAssembly SHA-256 is
`6bbb39b44896033f41bba14bf9bce94b0ee452929c9e664d2c50f3d4e4eb2eef`.
The no-patch run `m01-baseline-v2.json` passed reflection, prefab, ScriptableObject,
scene, scene unload/reload, serialized values, and AOT external consumer checks.

The `m01-p01-name-only.json` experiment failed the resource assertions while
reflection passed. This is a useful negative control, not a NO-GO verdict:

| Probe | Physical result |
| --- | --- |
| Stage | baseline assembly `0x11601a088`; interpreter assembly `0x125b2d450` |
| Assembly.Load / InternalEntry | interpreter; `PATCH-P01-INTERNAL` |
| Prefab component | baseline class `0x12583e420`; original method body |
| Scene first load and reload | same baseline class; original method body |
| ScriptableObject | baseline class `0x1257df7d0` |
| Serialized values | component 1234, inherited private field 7, data 5678 retained |
| GetComponent | name lookup succeeds; shadow Type lookup fails |

Object provenance is read directly from `Il2CppObject::klass` and that class's
physical image/assembly. It is not inferred from the managed assembly name or
from a redirected reflection wrapper.

## Actual native path, not a guessed engine implementation

Bounded in-process `backtrace`/`dladdr` records retain physical pointers, module
offsets, and symbols. The full trace is
`_temp/AssemblyShadow/m01-p01-name-only-native-diagnostics.json`.

Prefab/data loading reaches this observed stack (outer caller first):

```text
AssetBundle.LoadAsset
  -> PersistentManager::ReadAndActivateObjectThreaded
  -> PersistentManager::PostReadActivationQueue
  -> MonoScript::RebuildFromAwake
  -> MonoManager::GetScriptingClass
  -> il2cpp_class_from_name
  -> Class::FromName
  -> Image::ClassFromName
```

At event 31, `Image::ClassFromName` receives the **baseline** image
`0x116018c48`, despite active shadow image `0x125b2d4b0`. The engine's cached
image bypasses a fresh Assembly.Load name query. Image lookup returns the
baseline class before managed allocation.

Allocation then follows the independently observed stack:

```text
PersistentManager::ProduceObject
  -> SerializableManagedRef::RebuildMonoInstance
  -> scripting_unity_engine_object_new_and_invoke_default_constructor
  -> il2cpp_object_new
  -> Object::New
  -> Object::NewAllocSpecific
  -> Class::Init / allocation
```

Event 39 records the baseline prefab class at Object::New. Event 87 records
that class again during asynchronous scene reload. The second scene load can
reuse an already resolved class without another Image::ClassFromName call.

Some baseline classes are also looked up during `engine-before-bootstrap`.
That lookup alone does not prove an unchangeable binding: the old bundle's
MonoScript reconstruction demonstrably performs another image-local lookup.

Unity's engine source is unavailable. Engine function names above come from
the actual Player stack's exported symbols, not from invented source lines.
`UnityEditor.MonoScript.GetClass()` cannot be called in an IL2CPP Player. Its
requested runtime equivalent is documented by MonoScript reconstruction,
Image::ClassFromName's class output, Object::New's class input, and the final
physical object header. No claim is made that the Editor API itself ran there.

## Image mapping result and remaining string-lookup cache

Commit `d894d4483626055c4d2fa20c4fb8a1e37596f271` adds a 17-line native delta.
After activation, Image::ClassFromName maps only the exact staged baseline
image pointer to its paired interpreter image, before hash-table/class lookup.
It logs both physical images. All other images and inactive calls remain
unchanged. No global class-handle or Object::New redirection was added.

The native-ON build `_temp/UnityExec_20260827_052749.log` passed with semantic
equivalence of all three linked AOT inputs. GameAssembly SHA-256:
`2f91ac0f5f798a28911daf45a6f8bc4e064366b3ae89a9b2983e90d2ae3c3173`.

`m01-p01-image-map.json` proves that the original prefab, data asset, scene,
and scene reload now create physical interpreter objects. Component class
`0x125732f40` belongs to shadow assembly `0x12572d370`, not baseline class
`0x12543e340`. The prefab and both scene loads execute
`BASELINE-EXT|PATCH-P01-INTERNAL|1234`. Component 1234, inherited private value 7,
ScriptableObject 5678, and the object reference survive. Native Object::New
receives shadow classes; no allocation or object-header replacement is used.

The run is still Failed/UNDETERMINED because `GetComponent(string)` does not
return the expected component while `GetComponent(Type)` does. The original
probe records equality, not the returned object, so that result alone is not
proof that the returned value is null. The unpatched mode passes both overloads.

Read-only ARM64 disassembly exposes a second cache path:

```text
GameObject_CUSTOM_GetComponentByName                 UnityPlayer + 0x909a8
  -> GetScriptingWrapperOfComponentOfGameObjectWithCase          + 0xd7a658
  -> MonoScriptManager::FindRuntimeScript                       + 0xd9a35c
  -> MonoScript::GetClass                                      + 0xd95964
  -> scripting_object_get_class                               + 0xd72af4
  -> scripting_class_is_subclass_of                            + 0xd722ac
  -> il2cpp_class_is_subclass_of(actualClass, cachedClass, true)
```

MonoScript::GetClass reads the cached pointer at the script's `+0xa0` field;
it does not re-enter Image::ClassFromName. The comparison call's return PC is
UnityPlayer `+0xd7a7cc`. Two other branches could return null before comparison:
a found script with a null class, or a registry miss followed by a full-name
fallback. Operand-level tracing is required to distinguish them rather than
assuming that the baseline class is the decisive operand.

Commit `8f675aa4a78b62e3d8fca07d91c84c1ca2cde0b9` adds only comparison tracing.
It records actual/candidate classes and physical assemblies, result, interface
flag, phase, and stack. Pair/result-specific deduplication and dedicated
get-by-name phases prevent earlier reflection probes from consuming the trace
budget. The harness now separately records whether a name lookup returned an
object and, if so, its physical header. Compatibility rules remain unchanged
in this diagnostic experiment.

The diagnostic Player `m01-p01-class-comparison.json` resolves the ambiguity:
name lookup returns null. Native events 90, 108, and 125, in prefab, first scene,
and reloaded-scene get-by-name phases, compare actual interpreter class
`0x127d3cbe0` / assembly `0x127d37010` with baseline candidate class
`0x127a41ac0` / assembly `0x11841a088`. Every comparison returns false with
`checkInterfaces=true` and the expected UnityPlayer return PC `0xd7a7cc`.
This proves a stale class-bearing runtime-script cache, not either early-null
branch. UnityPlayer SHA-256 is
`417339d1c2d2b7bff00e30ac0f7cf0f25ed8918e1511c2340ca756090bb92c5f`.

Commit `03a450c73b5c5db2ed6f87dc4f194788fd204567` adds the next minimal mapping
at that observed `il2cpp_class_is_subclass_of` boundary. It remaps only a query
target from the exact paired baseline image, and only when the actual operand
already belongs to the physical shadow image. Generic and nested classes are
excluded. The target is looked up by namespace/name in the shadow image; actual
object classes are never remapped or rewritten. Both original and resolved
comparison operands/results remain in the trace. General VM cast/assignability
functions and reflection wrappers are not redirected.

This is an explicitly limited prototype compatibility rule, not a production
cache-coherence fix. Unity's pre-existing runtime-script cache itself still
stores baseline handles. Full type-handle, reflection, cast, and consumer safety
remain M03-M07 obligations. The final gate must retain that condition even if
all P01 fixture assertions pass.

## Metadata and debugging limitations

The first harness run called Assembly.ManifestModule and stopped with the
pinned IL2CPP RuntimeAssembly.GetManifestModuleInternal NotSupportedException.
RuntimeModule.GetGuidInternal also deliberately leaves module GUIDs unchanged.
The harness now reports this API as unsupported instead of fabricating a MVID.

The linker changes both MVID and SHA-256 of the three AOT inputs. Therefore
build evidence captures the actual post-strip DLLs immediately after BuildPlayer,
records their MVIDs/hashes separately, and checks their semantic equivalence to
the frozen compiler snapshots. Runtime identity uses actual physical pointers;
patch bytes are hash-checked before native staging.

The name-only GameAssembly and dSYM are retained under `_temp/AssemblyShadow/`.
Matching ARM64 UUID: `FBA17E40-0F47-4313-974C-A2541ABD8C7A`.
Offline LLDB resolved trace offset `0x9f6d8c` to Image::ClassFromName at
Image.cpp:247, and `0x68b020` to Object::New at Object.cpp:269. It also resolved
il2cpp_class_from_name and il2cpp_object_new to il2cpp-api.cpp:283 and :1069.
Live LLDB process launch remains blocked by host authorization; no machine
security setting was changed. Symbol-backed in-process stacks supply the
required native evidence without claiming successful live breakpoints.

## Final P01 result

The final native-ON build is `_temp/UnityExec_20260827_054717.log`, using native
commit `03a450c73b5c5db2ed6f87dc4f194788fd204567` and the runtime/package commits
listed above. Its GameAssembly SHA-256 is
`1d6e8e14de063594da475a7cf8c64f0fe1639b55506f4c95f40a6afab58e6ea7`.
The final demo build-source pin and strict installed-source check are recorded
in `../M01/M01-report.md`; pin-only closeout does not change compiled source.

`m01-p01-final.json` passed, exited zero, and records **CONDITIONAL-GO**.
The complete 141-event trace is archived with it under `../M01/Evidence/`.
The physical baseline assembly is `0x117c1a088` / image `0x117c18c48`; the
interpreter assembly is `0x127537010` / image `0x127537070`.

| Final probe | Physical proof and result |
| --- | --- |
| Reflection before business bundles | InternalEntry class `0x1275372c0`, shadow assembly, `PATCH-P01-INTERNAL`, Type.Assembly identity true |
| Old prefab | object `0x1204664c0`, class `0x12753cbe0`, shadow assembly, both GetComponent overloads return that component |
| Old scene, first asynchronous load | object `0x120466700`, same shadow class, both GetComponent overloads pass |
| Old scene, after unload/reload | new object `0x1204a5e40`, same shadow class, no cached AOT fallback |
| Old ScriptableObject | object `0x12045cf30`, class `0x12778e8d0`, shadow assembly, value 5678; its unchanged body returns BASELINE-DATA |
| External derived consumer | remains AOT and returns BASELINE-EXT |

All three component probes return `BASELINE-EXT|PATCH-P01-INTERNAL|1234`, retain
the inherited private value 7 and the data reference, and report no Missing
Script. No InvalidCast or native crash occurred. No component was removed,
re-added, retyped, or replaced as a workaround.

Native events 57-60 show the old prefab MonoScript reconstruction entering with
the baseline image and leaving with shadow class `0x12753cbe0`. Object::New
receives that class before allocation (prefab event 82, scene event 100, reload
event 121). The string query still presents cached baseline class `0x127241ac0`
at events 90/112/133; the bounded query-target rule resolves it to the actual
shadow class and returns true at events 93/115/136. All six comparisons retain
UnityPlayer return PC `0xd7a7cc`. This establishes both the successful resource
path and the remaining engine-cache limitation.

The original `m01-p01-target-map.json` experiment emitted an overly broad `GO`
label while its fixture assertions passed. That label was corrected before the
final build and six-mode matrix. Only `m01-p01-final.json` supplies the accepted
candidate gate; the earlier label is not unconditional approval.

Final GameAssembly and dSYM ARM64 UUID:
`37AA5842-07E5-4517-BE9C-1C42C5A065FE`. Offline LLDB resolves the final trace's
`0x68b020` to Object.cpp:269, `0xa0a4a8` to il2cpp-api.cpp:278, and the target-map
helper to AssemblyShadowPrototype.cpp:206. `il2cpp_class_from_name` and
`il2cpp_object_new` resolve to il2cpp-api.cpp:296 and :1082. The dSYM is retained
at `_temp/AssemblyShadow/M01-final-GameAssembly.dylib.dSYM`.

## Timing-negative matrix and required guard points

These are separate processes using the same final binary and first-build
bundles. P01 ran last; its persistent result and archived result are identical
(SHA-256 `79881992707a885029ccd8d5043e13e35719039fba307518c79bdd98b97be66e`).

| Mode | Exit / result | Observation | Future guard boundary |
| --- | --- | --- | --- |
| Baseline | 0 / Passed | All objects and method bodies remain AOT | No activation |
| PreUseType | 0 / Passed | AOT Type query recorded before activation; subsequent shadow probes pass, but two physical identities exist | Type resolution before commit |
| PreUseReflection | 0 / Passed | AOT Assembly.Load/GetType recorded before activation; subsequent probes pass | Reflection/assembly exposure before commit |
| PreUsePrefab | 1 / Failed, complete negative observation | Old prefab object remains AOT and runs its original body after activation | Resource load and managed object creation before commit |
| PreUseScene | 1 / Failed, complete negative observation | Old scene object remains AOT; later resource assertions expose cached baseline state | Scene/preloaded-object materialization before commit |
| P01 | 0 / Passed, CONDITIONAL-GO | No business pre-use; all positive fixture checks pass | Activate before business use |

For PreUsePrefab, object `0x1127e77c0` and class `0x127681ac0` are identical
before/after activation. For PreUseScene, object `0x110f27600` and class
`0x125641ac0` are identical. Both return
`BASELINE-EXT|BASELINE-INTERNAL|1234` after activation; their headers still point
to the physical baseline assembly. Reflection after activation sees the shadow
in both runs. Activation cannot retroactively make these objects safe.

The two exit-one runs are not accepted as positive tests. The independent
verifier requires complete observations, actual AOT pre-use, successful staging
and activation, unchanged old-object pointers/headers, and unchanged bundle
hashes. An exception, crash, missing output, or partial harness run would fail
that evidence check.

## Native-OFF regression

The final native commit was also built with
`HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0`, using the ordinary M00 harness and a separate
`Builds/AssemblyShadow/M01/NativeOffRegression.app` output. The accepted M00 app
was not overwritten. `_temp/UnityExec_20260827_054452.log` and
`m01-native-off-build.json` record a successful ARM64 IL2CPP build. GameAssembly
SHA-256: `8cb44b007c8fb86c7a3f50999caea41a1bb70ef90c007f113d3ecfb54b557c08`.

The real Player exited zero and passed ordinary hot-update loading, AOT assembly
identity, prefab result `M00-AOT-OK|1234`, ScriptableObject 5678, and scene/no
Missing Script checks. Native symbol inspection finds no AssemblyShadowPrototype
VM implementation in the OFF binary. Read-only source review confirms that all
changes to pre-existing resolution behavior are macro-guarded; the newly added
experimental APIs retain deterministic disabled stubs. Those new stubs were
source-reviewed, not separately invoked by the ordinary M00 Player harness.

## Gate constraints and M03-M07 backlog

CONDITIONAL-GO is justified because physical shadow objects are created from
the unchanged bundles through modifiable libil2cpp boundaries, before layout
allocation. The closed Unity engine does cache baseline handles, but this
fixture's decisive boundaries can be intercepted without modifying UnityPlayer.
The stronger unconditional GO claim, that all early caches are coherent, is
not established.

- **M03 transaction and usage safety:** separate Stage from registration and
  commit. This PoC immediately registers interpreter metadata, supports one
  Internal patch per process, has no rollback/unload or failure cleanup, and
  intentionally retains diagnostic state for process lifetime. Module
  initializer execution is disabled. Add a Usage Guard before business type,
  reflection, resource, and object use; do not migrate existing AOT objects.
- **M04 assembly consistency:** remove active-world ambiguity from AssemblyRef
  and AppDomain queries. The PoC records two same-name assemblies; IsDynamic is
  false and is not evidence of AOT versus interpreter execution. The one-name
  resolver is hard-coded and is not a general dependency-closure resolver.
- **M05 type/reflection consistency:** replace the narrow image/query-target
  rule with a reviewed class/type/reflection/cache policy. Unity's runtime-script
  cache still holds baseline classes. General Class::IsSubclassOf,
  IsAssignableFrom, casts, reflection wrappers, arrays, nested/generic types,
  and previously cached handles are not globally redirected by this PoC.
- **M06 execution semantics:** validate statics, virtual/interface calls,
  delegates, generics, initialization, thread publication and prewarming beyond
  this flat marker-only fixture. No production performance or memory claim is
  made; bounded stack tracing is diagnostic overhead, not release behavior.
- **M07 Unity coverage:** cover AddComponent, remaining GetComponent variants,
  ScriptableObject creation, Resources, first scene and preloaded assets, plus
  engine cache lifetimes. Supported ordering here is Bootstrap activation
  followed by business AssetBundles. First-scene/Resources/preloaded business
  objects are not approved for Shadow. Broader platforms remain unvalidated.

The fixture ABI comparison and post-strip semantic comparison are bounded
evidence tools, not the full M02 manifest/resource-ABI/security toolchain. Windows
x64 and Android ARM64 are not validated; helper native artifact capture currently
targets macOS GameAssembly.dylib. Headless NullGfx shader messages and the M00
allocator-shutdown diagnostic remain visible in logs, so this is not visual or
whole-engine clean-shutdown certification. Live debugger authorization remains
unchanged. M02-M12 implementation has not begun.
