# M04 executable file and API inventory

This inventory binds the executable source pairing below, not a claim of M04
acceptance. The report and review record carry the later runtime/gate decision.
Evidence-only files added after these build pins do not change the executable
pairing. No file is deleted in these four ranges.

| Repository | Accepted M03 base | M04 build source | Added / modified |
| --- | --- | --- | --- |
| hybridclr | `0eca86aca3ca8e3b6f2b131ec0f2679f92deefe9` | `39eca7a2cc9c8e414f29701629da268e4e213e09` | 1 / 4 |
| il2cpp_plus | `0486098099e7e80176401267538499e611b181f2` | `229f9450c0ebe2293da2bffbfc35f160f18c69de` | 0 / 7 |
| hybridclr_unity | `0c9302ffa2f420b30774423d4da8305214a78784` | `deee300670730fbc4d864e82fa70e7b022581afe` | 2 / 1 |
| demo | `a8c15b754fe033cda9a791eb7e5cd6494b30ccfd` | `3118db3f406bdbeeacaf75737d26a89414029007` | 60 / 14 |

Demo pin-only commit `e1a0d48af6a2be136e6ff777e3628b91b1715d26` records the
last source commit above. The 74-file demo source range includes 22 new Unity
assets/scripts, their 22 metas, seven new tooling files, nine new documentation/
evidence files, and 14 modified files. Metadata and diagnostic history are not
miscounted as additional implementation.

## Runtime: five files

Added:

- `hybridclr/metadata/AssemblyShadowAssemblyReference.h`

Modified:

- `hybridclr/metadata/Image.cpp`
- `hybridclr/metadata/Image.h`
- `hybridclr/metadata/InterpreterImage.cpp`
- `hybridclr/metadata/InterpreterImage.h`

The retained `AssemblyReferenceIdentity` domain describes declared reference
name/version/culture/token, separately from physical provider identity.
Interpreter metadata exposes the declared reference name and token-presence
information needed by assembly-level reflection.

## Native: seven modified files

- `libil2cpp/icalls/mscorlib/System.Reflection/Assembly.cpp`
- `libil2cpp/vm/Assembly.cpp`
- `libil2cpp/vm/Assembly.h`
- `libil2cpp/vm/AssemblyShadow.cpp`
- `libil2cpp/vm/AssemblyShadow.h`
- `libil2cpp/vm/MetadataCache.cpp`
- `libil2cpp/vm/MetadataCache.h`

Resolver APIs include `CurrentResolveContext`, `ResolveByName` and
`ResolveReferencedAssembly`, with Normal, Staging and DiagnosticsPhysical
contexts. Physical lookup preferences are AotOnly, InterpreterOnly, AnyNewest
and AnyOldest. Original/physical metadata lookup and AssemblyRef access are
separated from semantic resolution, avoiding recursive semantic lookups.
Logical enumeration preserves baseline positions and filters placeholders;
explicit physical diagnostics retain their separate contract.

The existing `Assembly.GetReferencedAssemblies` icall is reused and reports
declared reference identities with exact token presence. Existing AppDomain and
executing-assembly paths consume the corrected native assembly resolution; no
new managed icall is introduced. Fixed AOT indexes and upstream metadata layouts
are not rewritten.

## Package: three files

Modified:

- `Editor/AssemblyShadow/Validation/ReflectionDependencyScanner.cs`

Added:

- `Tests/Editor/AssemblyShadow/M04NameAcquisitionTests.cs`
- `Tests/Editor/AssemblyShadow/M04NameAcquisitionTests.cs.meta`

The scanner proves an immediate literal, fresh trusted AssemblyName constructor
and exact Load overload; aliases, mutations and ambiguous control-flow entries
remain rejected. Contextual ASCII path/suffix normalization retains the original
literal for exact Bootstrap approval. Global AQN policy is not relaxed.

The nine public `AssemblyShadowRuntime` methods, managed state/error enums and
native diagnostic schema remain unchanged from M03.

## Demo: added Unity assets and exact meta pairs

Every path below is added together with the same path plus `.meta` (22 pairs).
Paths are relative to `Assets/AssemblyShadowDemo/`.

- `AssemblyA/Contracts/M04AssemblyProbe.cs`
- `AssemblyA/Implementation/Extensibility/M04AssemblyProbe.cs`
- `AssemblyA/Implementation/Internal/M04AssemblyProbe.cs`
- `Consumers/ContractsConsumer/M04AssemblyProbe.cs`
- `Consumers/ExtensibilityConsumer/M04AssemblyProbe.cs`
- `Bootstrap/M04BootstrapRunner.cs`
- `Bootstrap/M04OrdinaryAssemblyProbe.cs`
- `Bootstrap/M04ReferenceProbe.cs`
- `Editor/M04AssemblyIdentityProof.cs`
- `Editor/M04Build.cs`
- `Editor/M04DiagnosticSchemaVerifier.cs`
- `Editor/M04EditorValidation.cs`
- `Editor/M04JsonEvidence.cs`
- `Editor/M04NativeMetadataProof.cs`
- `Editor/M04PlaceholderManifestProof.cs`
- `Editor/ShadowDiagnosticSchemaProof.cs`
- `Editor/ShadowFixtureProof.cs`
- `Scenes/M04Bootstrap.unity`
- `Tests/Editor/M04EditorEvidenceTests.cs`
- `Tests/Editor/M04NativeMetadataTests.cs`
- `Tests/Editor/M04OrdinaryAssemblyTests.cs`
- `Tests/Editor/M04ReferenceProbeTests.cs`

## Demo: 14 modified paths

- `Assets/AssemblyShadowDemo/AssemblyA/Contracts/AssemblyAContractVersion.cs`
- `Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/VersionedComponentBase.cs`
- `Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/InternalEntry.cs`
- `Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/ContractsConsumer.cs`
- `Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/DerivedExternalComponent.cs`
- `Assets/AssemblyShadowDemo/Bootstrap/link.xml`
- `Assets/AssemblyShadowDemo/Editor/M03Build.cs`
- `Assets/AssemblyShadowDemo/Editor/M03DiagnosticSchemaVerifier.cs`
- `Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs`
- `ProjectSettings/AssemblyShadowDependencies.json`
- `ProjectSettings/AssemblyShadowSettings.asset`
- `ProjectSettings/AssemblyShadowSourcePins.json`
- `ProjectSettings/EditorBuildSettings.asset`
- `Tools/AssemblyShadow/README.md`

The five existing business classes gain only `partial`; witnesses are patch-only
methods on those existing baseline-known types. The M03 edits narrowly extract
shared fixture/diagnostic proof helpers while keeping M03 output roots, schemas
and validation domains separate. Frozen M00/M01 artifact bytes are not replaced.

## Demo: seven added tooling files

- `Tools/AssemblyShadow/m04_metadata.py`
- `Tools/AssemblyShadow/m04_results.py`
- `Tools/AssemblyShadow/verify-m04-results.py`
- `Tools/AssemblyShadow/run-m04-native-tests.py`
- `Tools/AssemblyShadow/native-tests/m04_reference_identity.cpp`
- `Tools/AssemblyShadow/native-tests/m04_resolution.cpp`
- `Tools/AssemblyShadow/tests/test_m04_results.py`

## Demo: nine documentation/evidence files in the build-source range

- `Docs/AssemblyShadow/M04/M04-assembly-contract.md`
- `Docs/AssemblyShadow/M04/M04-report.md`
- `Docs/AssemblyShadow/M04/Evidence/capture-m04-linked-managed-wrappers.ps1`
- `Docs/AssemblyShadow/M04/Evidence/m04-linked-managed-wrappers.json`
- `Docs/AssemblyShadow/M04/Evidence/m04-native-regression.json`
- `Docs/AssemblyShadow/M04/Evidence/m04-preserved-m03-native-regression.json`
- `Docs/AssemblyShadow/M04/Evidence/m04-preserved-m03-visibility.json`
- `Docs/AssemblyShadow/M04/Evidence/player-results-v1-9ff427c.index.json`
- `Docs/AssemblyShadow/M04/Evidence/player-results-v1-9ff427c.tar.gz`

## Editor and probe contracts

Unity executeMethod entrypoints in `AssemblyShadowDemo.Editor`:

- `M04Build.Configure`
- `M04Build.ValidateCompilerInputs`
- `M04Build.BuildPlayerBaseline`
- `M04Build.BuildFixtures`
- `M04Build.BuildFeatureDisabledPlayer`
- `M04EditorValidation.Validate`

The helper proof APIs support strict compiler/linked/patch identity, generated
placeholder input, native metadata format 31, JSON schema and independent Editor
replay. They are Editor tooling, not a new deployment runtime API.

`AssemblyShadowDemo.M04BootstrapRunner` invokes `M04ReferenceProbe.RunAndWrite`.
The probe has explicit T04-01 through T04-08, T04-09-BenchmarkOn and
T04-10-BenchmarkOff modes. The final mode does not call Shadow APIs.
`M04OrdinaryAssemblyProbe` uses the existing finite M00 loader guard.

The corrected Player receipt adds nativeMetadataPath, nativeMetadataSha256,
nativeMetadataVersion, nativeAssemblyIdentities and nativeGeneratedAssemblyNames.
A native identity has exactly nine fields: assemblyIndex, imageIndex, token
(UInt32), imageName, name, fullName, version, culture and publicKeyToken.
It has no MVID. C# and Python derive generated names from actual native-minus-
linked inventories and bind the unique metadata file to the Player.
Runtime observations explicitly mark module MVID unavailable; DLL/patch MVID
proof remains separate and byte-backed.

## Remaining milestone boundaries

M04 establishes assembly-level resolution and observes reflection Assembly
equality. It does not establish complete Type/Member reflection-cache correctness,
all execution dispatch paths, or Unity asset/type integration. Those remain
M05-M07 work; platform acceptance here is limited to the pinned macOS ARM64
Unity 2022.3.62f2 IL2CPP configuration.
