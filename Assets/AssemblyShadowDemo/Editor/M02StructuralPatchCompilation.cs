using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Stages P05 in a matching Editor domain; the public Player compiler still performs every layout check.</summary>
    public static class M02StructuralPatchCompilation
    {
        private const string PatchDefine = "ASSEMBLY_SHADOW_P05";
        private const string StateName = "p05-define-state.json";
        private const string CompileName = "p05-compile-receipt.json";
        private const string RestoreName = "p05-restored.json";
        private const string OriginalSettingsName = "p05-project-settings.original";
        private const string ByteRestoreName = "p05-settings-restored.json";
        private const string SnapshotPath = "P05-compile/Snapshot";

        [Serializable] private sealed class DefineState
        {
            public int schemaVersion = 2;
            public string runDirectory, projectDirectory, unityVersion, target, architecture;
            public string sourcePinsPath, sourcePinsSha256, baselinePath, baselineSha256;
            public ShadowSourcePins sourcePins;
            public string originalDefines, stagedDefines, stateHash;
            public string defineTarget, originalSettingsSha256;
        }

        [Serializable] private sealed class CompileReceipt
        {
            public int schemaVersion = 1;
            public string stateSha256, snapshotPath, snapshotHash;
        }

        [Serializable] private sealed class RestoreReceipt
        {
            public int schemaVersion = 2;
            public string stateSha256, originalDefines, originalSettingsSha256, restoredSettingsSha256;
        }

        [Serializable] private sealed class ByteRestoreReceipt
        {
            public int schemaVersion = 1;
            public string stateSha256, originalSettingsSha256, restoredSettingsSha256;
        }

        public static string GetValidationRunDirectory()
        {
            return ParseRunDirectory(Environment.GetCommandLineArgs(), ProjectDirectory());
        }

        public static void Prepare()
        {
            string run = GetValidationRunDirectory();
            RequireQuiescentEditor(); RequireEditorLayout(false);
            Require(!File.Exists(Path.Combine(run, StateName)) && !File.Exists(Path.Combine(run, CompileName)) && !File.Exists(Path.Combine(run, RestoreName)),
                "StructuralRunAlreadyPrepared", "Never overwrite a prior structural compilation state.");
            DefineState state = CurrentContext(run);
            state.originalDefines = CurrentDefines();
            state.stagedDefines = StagedDefines(state.originalDefines);
            state.defineTarget = NamedTarget().TargetName;
            byte[] originalSettings = ReadRegularFile(Path.Combine(run, OriginalSettingsName));
            state.originalSettingsSha256 = ShadowHash.Bytes(originalSettings);
            Require(ShadowHash.File(SettingsPath()) == state.originalSettingsSha256, "StructuralSettingsChanged", "Settings changed after the wrapper captured their original bytes.");
            RequireSettingsOnlyTargetChange(originalSettings, originalSettings, state.defineTarget, state.originalDefines, state.originalDefines);
            state.stateHash = StateHash(state);
            // This immutable, flushed record precedes the first settings mutation.
            WriteNewJson(Path.Combine(run, StateName), state);
            Require(CurrentDefines() == state.originalDefines, "StructuralDefineConflict", "Defines changed before staging; no settings were replaced.");
            Require(ShadowHash.File(SettingsPath()) == state.originalSettingsSha256, "StructuralSettingsChanged", "Settings changed before staging; no settings were replaced.");
            SetDefines(state.stagedDefines);
            Debug.Log("[AssemblyShadow M02] P05 defines staged. A fresh Editor process must compile the structural patch: " + run);
        }

        public static void Compile()
        {
            string run = GetValidationRunDirectory(), stateSha;
            DefineState state = ReadState(run, out stateSha);
            RequireCurrentContext(state); RequireQuiescentEditor();
            Require(!File.Exists(Path.Combine(run, RestoreName)) && !File.Exists(Path.Combine(run, CompileName)),
                "StructuralCompileAlreadyFinished", "The staged compilation is single-use.");
            Require(CurrentDefines() == state.stagedDefines, "StructuralDefineConflict", "P05 requires the exact recorded staged defines.");
            RequireEditorLayout(true);
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            string snapshot = AssemblySnapshot.Compile(Path.Combine(run, "P05-compile"), target, settings.architecture,
                state.sourcePins, policy, new[] { PatchDefine });
            Require(Path.GetFullPath(snapshot) == Path.GetFullPath(Path.Combine(run, SnapshotPath)), "StructuralSnapshotPath", snapshot);
            var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            RequireSnapshot(state, receipt);
            RequireCurrentContext(state);
            Require(CurrentDefines() == state.stagedDefines, "StructuralDefineConflict", "Defines changed during P05 compilation.");
            WriteNewJson(Path.Combine(run, CompileName), new CompileReceipt { stateSha256 = stateSha, snapshotPath = SnapshotPath, snapshotHash = receipt.snapshotHash });
            Debug.Log("[AssemblyShadow M02] P05 captured through successful public CompilePlayerScripts: " + receipt.snapshotHash);
        }

        public static void Restore()
        {
            string run = GetValidationRunDirectory();
            if (!File.Exists(Path.Combine(run, StateName)))
            {
                // Prepare writes the state before mutation. A failure before that
                // point gives us no authority to change any user-owned defines.
                Debug.Log("[AssemblyShadow M02] No recorded P05 define mutation; recovery leaves settings untouched: " + run);
                return;
            }
            string stateSha;
            DefineState state = ReadState(run, out stateSha);
            RequireCurrentContext(state); RequireQuiescentEditor();
            string currentDefines = CurrentDefines();
            bool write = RestorationRequired(currentDefines, state.originalDefines, state.stagedDefines);
            byte[] originalSettings = ReadOriginalSettings(state);
            RequireSettingsOnlyTargetChange(originalSettings, ReadRegularFile(SettingsPath()), state.defineTarget, state.originalDefines, currentDefines);
            if (write) SetDefines(state.originalDefines);
            Require(CurrentDefines() == state.originalDefines, "StructuralRestoreFailed", "Exact original scripting defines were not restored.");
            byte[] restoredSettings = ReadRegularFile(SettingsPath());
            RequireSettingsOnlyTargetChange(originalSettings, restoredSettings, state.defineTarget, state.originalDefines, state.originalDefines);
            string restoredSettingsSha = ShadowHash.Bytes(restoredSettings);
            string path = Path.Combine(run, RestoreName);
            if (File.Exists(path)) Require(RequireRestoreReceipt(path, state, stateSha).restoredSettingsSha256 == restoredSettingsSha,
                "StructuralSettingsChanged", "The settings serialization changed after Restore recorded its result.");
            else WriteNewJson(path, new RestoreReceipt { stateSha256 = stateSha, originalDefines = state.originalDefines,
                originalSettingsSha256 = state.originalSettingsSha256, restoredSettingsSha256 = restoredSettingsSha });
            // The current domain may still contain P05 types. The fourth fresh
            // process verifies baseline Editor layout before consuming the snapshot.
            Debug.Log("[AssemblyShadow M02] Exact original defines restored; restart before validation: " + run);
        }

        public static string ReadPreparedSnapshot(string runDirectory)
        {
            string run = GetValidationRunDirectory();
            Require(Path.GetFullPath(runDirectory) == run, "StructuralRunMismatch", "The requested snapshot belongs to another validation run.");
            string stateSha;
            DefineState state = ReadState(run, out stateSha);
            RequireCurrentContext(state); RequireQuiescentEditor();
            Require(CurrentDefines() == state.originalDefines, "StructuralDefineConflict", "Baseline scripting defines must be restored before validation.");
            RequireEditorLayout(false);
            RestoreReceipt restored = RequireRestoreReceipt(Path.Combine(run, RestoreName), state, stateSha);
            string byteRestorePath = Path.Combine(run, ByteRestoreName);
            Require(File.Exists(byteRestorePath), "StructuralByteRestoreMissing", "The wrapper must restore exact settings bytes after the Restore Editor exits.");
            var byteRestored = JsonUtility.FromJson<ByteRestoreReceipt>(File.ReadAllText(byteRestorePath));
            Require(byteRestored != null && byteRestored.schemaVersion == 1 && byteRestored.stateSha256 == stateSha &&
                byteRestored.originalSettingsSha256 == state.originalSettingsSha256 && byteRestored.restoredSettingsSha256 == restored.restoredSettingsSha256 &&
                ShadowHash.File(SettingsPath()) == state.originalSettingsSha256,
                "StructuralByteRestoreMismatch", "Original settings bytes were not restored or changed before validation.");
            ReadOriginalSettings(state);
            string path = Path.Combine(run, CompileName);
            Require(File.Exists(path), "StructuralCompileMissing", "P05 has no successful captured compilation.");
            var prepared = JsonUtility.FromJson<CompileReceipt>(File.ReadAllText(path));
            Require(prepared != null && prepared.schemaVersion == 1 && prepared.stateSha256 == stateSha && prepared.snapshotPath == SnapshotPath,
                "StructuralCompileMismatch", "P05 compilation receipt does not belong to this define state.");
            string snapshot = Path.Combine(run, SnapshotPath);
            var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            RequireSnapshot(state, receipt);
            Require(receipt.snapshotHash == prepared.snapshotHash, "StructuralSnapshotChanged", "P05 snapshot changed after successful capture.");
            return snapshot;
        }

        private static string ParseRunDirectory(string[] arguments, string project)
        {
            int[] positions = arguments.Select((argument, index) => new { argument, index }).Where(p => p.argument == "-shadowValidationRoot").Select(p => p.index).ToArray();
            Require(positions.Length == 1 && positions[0] + 1 < arguments.Length, "StructuralRunArgument", "Exactly one -shadowValidationRoot is required.");
            string value = arguments[positions[0] + 1];
            Require(!string.IsNullOrWhiteSpace(value) && Path.IsPathRooted(value), "StructuralRunArgument", "The validation run must be absolute.");
            string run = Path.GetFullPath(value).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string parent = Path.Combine(Path.GetFullPath(project), "_temp", "AssemblyShadow");
            Require(Path.GetDirectoryName(run) == parent && Regex.IsMatch(Path.GetFileName(run), "^M02Validation-[0-9a-f]{32}$") && Directory.Exists(run),
                "StructuralRunArgument", "The run must be an existing unique _temp/AssemblyShadow/M02Validation-<guid> directory.");
            Require((File.GetAttributes(run) & FileAttributes.ReparsePoint) == 0 && (File.GetAttributes(parent) & FileAttributes.ReparsePoint) == 0 &&
                (File.GetAttributes(Path.GetDirectoryName(parent)) & FileAttributes.ReparsePoint) == 0,
                "StructuralRunArgument", "The validation path cannot traverse a filesystem link.");
            return run;
        }

        private static string StagedDefines(string original)
        {
            Require(original != null, "StructuralDefinesInvalid", "Unity returned no scripting define string.");
            string[] values = original.Length == 0 ? new string[0] : original.Split(';');
            Require(values.All(v => Regex.IsMatch(v, "^[A-Za-z_][A-Za-z_0-9]*$")) && values.Distinct(StringComparer.Ordinal).Count() == values.Length,
                "StructuralDefinesInvalid", "Existing defines must be canonical; do not normalize user settings during staging.");
            Require(!values.Any(v => v.StartsWith("ASSEMBLY_SHADOW_P", StringComparison.Ordinal)), "StructuralPatchDefinePresent", "Remove preexisting patch symbols explicitly before structural validation.");
            return original.Length == 0 ? PatchDefine : original + ";" + PatchDefine;
        }

        private static bool RestorationRequired(string current, string original, string staged)
        {
            Require(StagedDefines(original) == staged, "StructuralStateInvalid", "Recorded staged defines do not extend the exact original defines.");
            Require(current == original || current == staged, "StructuralDefineConflict", "Scripting defines changed concurrently; refusing to overwrite them. Restore the recorded original manually after inspection.");
            return current == staged;
        }

        private static DefineState CurrentContext(string run)
        {
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            Require(settings.architecture == BaselineBuild.TargetArchitecture(), "StructuralArchitectureMismatch", "Configured and active target architectures differ.");
            string sourcePath = Path.GetFullPath(settings.sourcePinFile);
            var pins = ShadowSourcePins.Read(sourcePath, target, settings.architecture);
            string baseline = ShadowBuildSession.Load().baselineManifestPath;
            Require(!string.IsNullOrWhiteSpace(baseline) && File.Exists(baseline), "StructuralBaselineMissing", "Build the M02 baseline before structural validation.");
            baseline = Path.GetFullPath(baseline);
            string baselineHash = ShadowHash.File(baseline), hashPath = Path.Combine(Path.GetDirectoryName(baseline), "manifest.sha256");
            Require(File.Exists(hashPath) && File.ReadAllText(hashPath).Trim() == baselineHash, "StructuralBaselineChanged", "Baseline manifest hash does not verify.");
            var manifest = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(baseline));
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.unityVersion == Application.unityVersion && manifest.target == target.ToString() && manifest.architecture == settings.architecture,
                "StructuralBaselineMismatch", "Baseline Unity/target/architecture does not match the current Editor.");
            ShadowSourcePins.RequireCompatible(manifest.sourcePins, pins);
            return new DefineState { runDirectory = run, projectDirectory = ProjectDirectory(), unityVersion = Application.unityVersion,
                target = target.ToString(), architecture = settings.architecture, sourcePinsPath = sourcePath, sourcePinsSha256 = ShadowHash.File(sourcePath),
                sourcePins = pins, baselinePath = baseline, baselineSha256 = baselineHash };
        }

        private static void RequireCurrentContext(DefineState state)
        {
            DefineState current = CurrentContext(state.runDirectory);
            Require(state.projectDirectory == current.projectDirectory && state.unityVersion == current.unityVersion && state.target == current.target && state.architecture == current.architecture &&
                state.sourcePinsPath == current.sourcePinsPath && state.sourcePinsSha256 == current.sourcePinsSha256 &&
                state.baselinePath == current.baselinePath && state.baselineSha256 == current.baselineSha256,
                "StructuralContextChanged", "Run target, architecture, source pins or baseline changed between Editor processes.");
            ShadowSourcePins.RequireSameBuildSources(state.sourcePins, current.sourcePins);
        }

        private static DefineState ReadState(string run, out string fileHash)
        {
            string path = Path.Combine(run, StateName);
            Require(File.Exists(path), "StructuralStateMissing", "Prepare must record define recovery state before compilation.");
            byte[] bytes = File.ReadAllBytes(path); fileHash = ShadowHash.Bytes(bytes);
            var state = JsonUtility.FromJson<DefineState>(Encoding.UTF8.GetString(bytes));
            Require(state != null && state.schemaVersion == 2 && state.runDirectory == run && state.projectDirectory == ProjectDirectory() &&
                state.defineTarget == NamedTarget().TargetName && Regex.IsMatch(state.originalSettingsSha256 ?? "", "^[0-9a-f]{64}$") &&
                state.sourcePins != null && state.stateHash == StateHash(state) && StagedDefines(state.originalDefines) == state.stagedDefines,
                "StructuralStateInvalid", "Structural define state is incomplete or changed.");
            return state;
        }

        private static string StateHash(DefineState state)
        {
            return ShadowHash.Text("m02-structural-define-state:2\n" + state.runDirectory + "\n" + state.projectDirectory + "\n" + state.unityVersion + "\n" + state.target + "\n" + state.architecture + "\n" +
                state.sourcePinsPath + "\n" + state.sourcePinsSha256 + "\n" + JsonUtility.ToJson(state.sourcePins) + "\n" + state.baselinePath + "\n" + state.baselineSha256 + "\n" +
                state.originalDefines + "\n" + state.stagedDefines + "\n" + state.defineTarget + "\n" + state.originalSettingsSha256);
        }

        private static void RequireSnapshot(DefineState state, AssemblySnapshotReceipt receipt)
        {
            Require(receipt.unityVersion == state.unityVersion && receipt.target == state.target && receipt.architecture == state.architecture &&
                ShadowReflectionBindingEvidence.UserDefines(receipt.extraScriptingDefines).SequenceEqual(new[] { PatchDefine }),
                "StructuralSnapshotMismatch", "P05 must be one successful target compiler snapshot with exactly the expected patch define.");
            ShadowSourcePins.RequireSameBuildSources(state.sourcePins, receipt.sourcePins);
        }

        private static RestoreReceipt RequireRestoreReceipt(string path, DefineState state, string stateSha)
        {
            Require(File.Exists(path), "StructuralRestoreMissing", "Restore must complete before validation.");
            var restored = JsonUtility.FromJson<RestoreReceipt>(File.ReadAllText(path));
            Require(restored != null && restored.schemaVersion == 2 && restored.stateSha256 == stateSha && restored.originalDefines == state.originalDefines &&
                restored.originalSettingsSha256 == state.originalSettingsSha256 && Regex.IsMatch(restored.restoredSettingsSha256 ?? "", "^[0-9a-f]{64}$"),
                "StructuralRestoreMismatch", "Restore receipt belongs to another define state.");
            return restored;
        }

        private static byte[] ReadOriginalSettings(DefineState state)
        {
            byte[] bytes = ReadRegularFile(Path.Combine(state.runDirectory, OriginalSettingsName));
            Require(ShadowHash.Bytes(bytes) == state.originalSettingsSha256, "StructuralSettingsBackupChanged", "Original settings backup changed.");
            return bytes;
        }

        private static byte[] ReadRegularFile(string path)
        {
            Require(File.Exists(path) && (File.GetAttributes(path) & FileAttributes.ReparsePoint) == 0,
                "StructuralSettingsFile", "Settings evidence must be an existing regular file: " + path);
            return File.ReadAllBytes(path);
        }

        private static void RequireSettingsOnlyTargetChange(byte[] original, byte[] current, string target, string originalDefines, string currentDefines)
        {
            // Decode strictly and retain every character (including BOM/newlines).
            // Only Unity's single-line target entry and empty-map spelling may differ.
            var utf8 = new UTF8Encoding(false, true);
            Require(SettingsWithoutTarget(utf8.GetString(original), target, originalDefines) == SettingsWithoutTarget(utf8.GetString(current), target, currentDefines),
                "StructuralSettingsChanged", "Unrelated project settings changed; refusing to overwrite them with the original file.");
        }

        private static string SettingsWithoutTarget(string text, string target, string expectedDefines)
        {
            Require(Regex.IsMatch(target ?? "", "^[A-Za-z_][A-Za-z_0-9]*$"), "StructuralSettingsShape", "Unsupported define target key.");
            MatchCollection headers = Regex.Matches(text, @"(?m)^  scriptingDefineSymbols:(?<empty> \{\})?(?<newline>\r?\n)");
            Require(headers.Count == 1, "StructuralSettingsShape", "Expected one canonical scriptingDefineSymbols map.");
            Match header = headers[0];
            int start = header.Index + header.Length;
            Match next = Regex.Match(text.Substring(start), @"(?m)^ {0,2}\S");
            int end = next.Success ? start + next.Index : text.Length;
            string body = text.Substring(start, end - start);
            Require(!header.Groups["empty"].Success || body.Length == 0, "StructuralSettingsShape", "An inline empty map cannot contain entries.");
            var remaining = new StringBuilder();
            var keys = new System.Collections.Generic.HashSet<string>(StringComparer.Ordinal);
            string actualDefines = "";
            int offset = 0;
            while (offset < body.Length)
            {
                Match entry = Regex.Match(body.Substring(offset), @"\A    (?<key>[A-Za-z_][A-Za-z_0-9]*): (?<value>[^\r\n]*)(?:\r?\n)");
                Require(entry.Success && keys.Add(entry.Groups["key"].Value), "StructuralSettingsShape", "Unsupported or duplicate define map entry.");
                if (entry.Groups["key"].Value == target) actualDefines = entry.Groups["value"].Value;
                else remaining.Append(entry.Value);
                offset += entry.Length;
            }
            Require(actualDefines == expectedDefines, "StructuralSettingsDefines", "Serialized target defines do not match the recorded Unity define string.");
            string canonicalHeader = "  scriptingDefineSymbols:" + (remaining.Length == 0 ? " {}" : "") + header.Groups["newline"].Value;
            return text.Substring(0, header.Index) + canonicalHeader + remaining + text.Substring(end);
        }

        private static string SettingsPath() { return Path.Combine(ProjectDirectory(), "ProjectSettings", "ProjectSettings.asset"); }

        private static void RequireEditorLayout(bool structural)
        {
            var field = typeof(AssemblyA.Implementation.Internal.VersionedPrefabComponent).GetField("addedSerializedField", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.DeclaredOnly);
            Require(structural ? field != null && field.FieldType == typeof(int) && field.IsDefined(typeof(SerializeField), false) : field == null,
                "StructuralEditorDomainMismatch", "Start a fresh Editor process after changing defines; the loaded serialized layout is not the expected " + (structural ? "P05" : "baseline") + " layout.");
        }

        private static string ProjectDirectory() { return Path.GetFullPath(Directory.GetParent(Application.dataPath).FullName); }
        private static NamedBuildTarget NamedTarget() { return NamedBuildTarget.FromBuildTargetGroup(BuildPipeline.GetBuildTargetGroup(EditorUserBuildSettings.activeBuildTarget)); }
        private static string CurrentDefines() { return PlayerSettings.GetScriptingDefineSymbols(NamedTarget()); }
        private static void SetDefines(string defines)
        {
            PlayerSettings.SetScriptingDefineSymbols(NamedTarget(), defines);
            AssetDatabase.SaveAssets();
            Require(CurrentDefines() == defines, "StructuralDefineWriteFailed", "Unity did not retain the exact requested define string.");
        }
        private static void RequireQuiescentEditor()
        { Require(!EditorApplication.isCompiling && !EditorApplication.isUpdating, "StructuralEditorBusy", "Compilation/import must finish before structural validation."); }
        private static void WriteNewJson(string path, object value)
        {
            byte[] bytes = new UTF8Encoding(false).GetBytes(JsonUtility.ToJson(value, true));
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            { stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
        }
        private static void Require(bool condition, string code, string message) { if (!condition) throw new ShadowBuildException(code, message); }
    }
}
