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
