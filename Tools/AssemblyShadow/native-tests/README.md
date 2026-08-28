# M03 focused native regression

Run on macOS with Python 3.9+ and clang++, from the demo repository:

```sh
python3 Tools/AssemblyShadow/run-m03-native-tests.py --output /tmp/m03-native-receipt.json
```

The receipt path must not already exist. The runner resolves native repositories
from `ProjectSettings/AssemblyShadowSourcePins.json`; override them with
`--demo-root`, `--native-root` (HybridCLR), and `--runtime-root` (il2cpp_plus).
`--installed-root` identifies the pinned installed `il2cpp/libil2cpp` directory,
used read-only for external headers and generated Unity-version definitions.
No Unity launch, installation, source mutation, or build-cache cleanup occurs.
Only the runner's unique temporary build directory is removed automatically.

Default fixtures are the existing Contracts, Internal, and Extensibility DLLs
under `HybridCLRData/HotUpdateDlls/StandaloneOSX`. Use repeated `--dll` arguments
to select other real fixtures. Missing fixtures fail; this runner does not build
or replace them. The original three fixtures produce 23,027 parser checks;
the exact count depends on their physical metadata sizes. Thirty additional
name checks compare `NameIndex` normalization/Unicode folding against the real
`VmStringUtils` implementation and character tables.

The parser checks cover real DLL identity/MVID/references, successive truncated
prefixes, invalid PE signatures/offsets, 6,000 deterministic byte mutations,
and a synthetic portable PDB with invalid/truncated variants. AddressSanitizer
is enabled with fail-fast options overriding inherited `ASAN_OPTIONS`.
The receipt records all commands and exits, check counts, source
pins/current Git heads, compiler identity, installed-header provenance, and
SHA-256 hashes of actual transitive compilation inputs (including SDK headers).
Inputs are hashed before compilation and checked again after tests to detect
concurrent changes. A source-pin/head match does not imply clean working bytes;
the recorded file hashes identify the tested worktree state.

This is not M03 runtime acceptance: it does not initialize Unity/IL2CPP, test
transaction state/publication/concurrency/initializers, validate a real PDB/DLL
debug identity pair, or perform full IL semantic verification. The harness
includes the real private parser implementation; its only VM adapter is
`Memory::Free`. Unused VM paths are dead-stripped and linked with macOS
`dynamic_lookup`; accidentally reaching an unresolved VM symbol fails the test.
Installed-header provenance is recorded, not claimed as a full installed-runtime
verification. Use the separate installed-runtime verifier for that boundary.

## Private metadata visibility predicates

Run the independent visibility harness with a new receipt path:

```sh
python3 -B Tools/AssemblyShadow/run-m03-visibility-tests.py \
  --output /tmp/m03-visibility-receipt.json
```

This compiles the actual `AssemblyShadowVisibility.cpp` and `MetadataUtil.cpp`
from the paired source repositories under ASan. Synthetic native metadata covers
all four encoded image-index formats, unmaterialized private type handles,
public-image `Nullable<private>`, nested class/method generic contexts, generic
parameters, arrays, pointers, both byref representations, element/declaring
identities, and cycle-safe traversal. Separate abort and commit processes verify
pre-publication invisibility, retained invisibility without publication, old
generation-zero visibility after publication, active membership, ordinary-class
preservation, and retained staged provenance after activation.

The current scenarios run 18,674 assertions, including repeated retained-state
and captured-generation checks. Only `ActiveGeneration` and `IsActiveShadow` are
substituted by a simulated immutable active snapshot. This is predicate proof,
not proof of actual `CommitTransaction`, Abort, concurrent VM publication,
global-cache construction, `il2cpp_class_for_each`, or managed memory snapshots.
Those paths still require the real T03 Player tests.

The runner additionally preprocesses the actual ON `MemoryInformation.cpp` and
`GlobalMetadata.cpp` and checks the cached-only ordinary-definition callback
policy: initialized existing AOT/interpreter slots, metadata-lock protection,
physical interpreter lookup without private TLS, no direct materializing calls,
and retention of all four compound-cache walkers. These five structural checks
prevent accidental reintroduction of the known diagnostic materialization path;
they are not executable proof of VM cache reads or baseline-use behavior.
Full managed memory snapshots still perform field/type resolution and are not
claimed to be no-use observations.

The runner reuses read-only provenance helpers from `run-m03-native-tests.py`
without creating Python caches. It defaults to external/generated headers under
`HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP`;
override with `--generated-root`. The matching generated installation receipt and
Unity version are checked. Repository heads/pins, compiler identity, exact commands,
all transitive input hashes, and before/after input stability are recorded.
Existing receipt files are refused. Only a unique temporary build directory is
created and removed; no Unity, installation, or build-cache mutation occurs.
