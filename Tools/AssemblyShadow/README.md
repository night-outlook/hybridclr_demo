# Assembly Shadow milestone tools

Requirements: Python 3.9+, Git, PowerShell 7, and the pinned Unity Editor with
IL2CPP support. Run from the demo root. Do not run a second Editor for an open
project. The original demo may stay open while the separate shadow worktree is
built through the shared Unity debugging scripts.

## M00 reproduction

1. Check out the milestone pairing in all four repositories. Keep their sibling
   paths, or update the manifest's relative localPath values deliberately.
2. Inspect exact versions with print-source-pins.sh or print-source-pins.ps1.
3. Run the Unity static method AssemblyShadowBaseline.Editor.BaselineBuild.Configure.
4. Run AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability. This
   verifies two installations and saves identical source receipts.
5. Run python3 Tools/AssemblyShadow/verify-installed-runtime.py.
6. Run AssemblyShadowBaseline.Editor.BaselineValidation.Run and
   python3 -m unittest discover -s Tools/AssemblyShadow/tests -v.
7. Run AssemblyShadowBaseline.Editor.BaselineBuild.Build through
   .agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1 with a suitable timeout.
8. Launch the resulting IL2CPP Player with -batchmode -nographics,
   -shadowResultPath <absolute-result.json> and -logFile <absolute-player.log>.
   Both process exit zero and result=Passed are required.

The build defaults to native Shadow OFF. BaselineBuild.SetNativeFeature(bool)
sets the native compiler definition, not a C# define. M01's build uses this
shared switch for ON. The verifier defaults to the M00 OFF expectation;
--expect-shadow on selects the M01 build configuration expectation. Neither
header inspection nor an Editor check is a substitute for Player evidence.

The demo pin identifies a build-source commit. Later metadata-only commits may
update the pin file and Docs/AssemblyShadow. The default verifier checks the
complete pinned demo source, including ignored stray C# and asmdef files.
--skip-demo-source is for intermediate development inspection only and cannot
establish milestone acceptance.

## M01 reproduction

Use the exact M01 pairing and the isolated project, then run these static methods
through `.agents/skills/unity-debug/scripts/Invoke-UnityMethod.ps1`:

1. `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability`
2. `AssemblyShadowDemo.Editor.BuildBaselineBundles.Build`
3. `AssemblyShadowDemo.Editor.CompilePatchDlls.Build`
4. `AssemblyShadowDemo.Editor.BuildBaselinePlayer.Build`
5. `AssemblyShadowDemo.Editor.M01EditorValidation.Validate`

Use a 2400-second timeout for Player builds. The first bundle build freezes
`BaselineArtifacts/<target>/M01-Baseline-v1`. Subsequent invocations verify/reuse
that directory; they must not rebuild or replace its bundles. P01 is compiled
separately into `PatchArtifacts/P01`. Runtime staging contains only the baseline
manifest, bundles, catalog, and P01 bytes, not source or AOT DLL snapshots.

Run `Builds/AssemblyShadow/M01/Prototype.app/Contents/MacOS/AssemblyShadowBaseline`
on macOS ARM64 with `-batchmode -nographics`. Use `-shadowMode` to select, in
order, `Baseline`, `PreUseType`, `PreUseReflection`, `PreUsePrefab`, `PreUseScene`,
and finally `P01`. Give every run a distinct absolute `-shadowResultPath` and
`-logFile` path. The writer also updates
`PersistentDataPath/AssemblyShadowTests/m01-result.json`; P01 last leaves the
positive gate result there. Do not run these processes concurrently against
the same persistent result path.

Baseline and P01 must exit zero and pass every assertion. Timing-negative runs
may exit one when retained baseline resources fail the intentionally shadow-only
assertions; they must still finish and record genuine AOT pre-use, activation,
and post-activation observations. A failed harness or missing output is not a
successful negative test.

Verify the recorded runs against real artifacts:

```sh
python3 Tools/AssemblyShadow/verify-m01-results.py \
  --baseline-root BaselineArtifacts/StandaloneOSX/M01-Baseline-v1 \
  --baseline-result <baseline-result.json> --patch-result <p01-result.json> \
  --patch-dll PatchArtifacts/P01/AssemblyA.Implementation.Internal.dll \
  --player-assemblies _temp/AssemblyShadow/m01-player-assemblies.json \
  --negative-result <preuse-type.json> --negative-result <preuse-reflection.json> \
  --negative-result <preuse-prefab.json> --negative-result <preuse-scene.json> \
  --output <verification.json>
python3 Tools/AssemblyShadow/verify-installed-runtime.py --expect-shadow on
```

The build receipt captures the actual post-strip AOT DLLs and native library
hash. Linker MVID changes are recorded, while dnlib checks preserved semantics.
The pinned IL2CPP does not support Assembly.ManifestModule; runtime MVIDs are
not fabricated. Physical native object/assembly pointers and resource-allocation
stacks, not managed assembly names alone, establish shadow provenance.

Gate approval additionally requires the native-path investigation, a real
macro-OFF ordinary Player regression, and independent review. The prototype is
not the M03-M07 production transaction, usage guard, or cache system.

## M02 reproduction (integration in progress)

M02 acceptance is not yet recorded. Use the source pairing and detailed evidence
in `Docs/AssemblyShadow/M02/M02-report.md`; do not treat a checkpoint as a milestone.

1. Run `AssemblyShadowDemo.Editor.M02Build.Configure` through the shared Unity
   method helper.
2. Run `Invoke-ShadowEditorTests.ps1 -TestFilter 'HybridCLR.Editor.AssemblyShadow.Tests;AssemblyShadowDemo.EditorTests'`.
3. Verify the pinned installation with `BaselineBuild.InstallRepeatability` and
   `verify-installed-runtime.py --expect-shadow on`.
4. Run `AssemblyShadowDemo.Editor.M02Build.BuildPlayerBaseline`. It stages the
   finite reflection configuration and reuses the immutable M01 bundles; it never
   replaces them. The resulting Player input snapshot includes actual linked DLLs
   and a separately verified type-forwarding/guard proof.
5. Run that Player with `-shadowMode M02ReflectionBindings`, a unique absolute
   `-shadowBindingResult` path, and `-batchmode -nographics -logFile <absolute.log>`.
6. Run `AssemblyShadowDemo.Editor.M02EditorValidation.Validate` for the real
   P01/P02/P03/P05 compiler, closure, ABI and repeatability cases.
7. Run `verify-m02-results.py` with the Editor, NUnit and `--reflection-result`
   evidence. Independent review and a milestone tag remain required.

The `SerializableEnum` Player contract is intentionally deny-all for nonempty
serialized type names. Editor usage remains unchanged. The canvas contract admits
only its 26 pinned widget names; changing this fixed AOT contract requires a new
Player baseline. These bounded guards do not establish the later native gates.

## Recoverable native-cache rebuild

clean-il2cpp-cache.sh is a dry-run unless --apply is passed; PowerShell uses
-Apply. Only Library/Bee and Library/Il2cppBuildCache are eligible. The shared
exact-project Unity process/lock guard must succeed before every move.

Caches are moved, not deleted, into a unique
_temp/AssemblyShadow/CacheBackups/<id> directory. manifest.json records the
source and backup paths. Restore only with the project closed and only when the
original target path is absent; never overlay a newly generated cache.

## Evidence and limits

The source verifier checks committed Git blobs, installed SHA-256 hashes and
the entire native file inventory. It permits exactly four generated files to
change. Pin JSON, receipt JSON, Unity version, package path/version, target and
native compiler mode must agree. Symlinks and path traversal fail closed.

M00 Player, build, install and Editor results go under _temp/AssemblyShadow.
Accepted results and review records are archived under Docs/AssemblyShadow.
Builds, caches, patch DLLs and dSYM files are reproducible local artifacts, not
checked-in source. Windows/Android results must never be inferred from macOS.
