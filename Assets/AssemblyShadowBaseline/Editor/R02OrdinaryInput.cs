using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowBaseline.Editor
{
    // Prepare only the immutable ordinary witness. Do not call M00 Configure:
    // it changes the feature flag, scenes, product identity and build settings.
    public static class R02OrdinaryInput
    {
        private const string Name = "AssemblyShadowBaseline.HotUpdate";
        private const string Expected = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string Source = "Assets/AssemblyShadowBaseline/HotUpdate";
        private const string Destination = "Assets/StreamingAssets/AssemblyShadow/M00/" + Name + ".dll.bytes";

        [Serializable] public sealed class FileRecord { public string path, sha256; public long sizeBytes; }
        [Serializable] public sealed class Receipt
        {
            public int schemaVersion = 1;
            public string kind = "R02OrdinaryInputPreparation", result = "Failed", error = "";
            public string projectRoot, outputRoot, unityVersion, target, sourcePinsSha256;
            public string expectedSha256 = Expected, classification = "CurrentWorkspaceCompilerOutput";
            public bool development = true, freshCscExecutionClaimed = false, runtimeAcceptance = false;
            public FileRecord[] sources; public FileRecord compiled, staged;
        }

        private static string Hash(string path)
        {
            using (var algorithm = SHA256.Create())
                return BitConverter.ToString(algorithm.ComputeHash(File.ReadAllBytes(path))).Replace("-", "").ToLowerInvariant();
        }
        private static FileRecord Record(string path)
        {
            path = Path.GetFullPath(path);
            return new FileRecord { path = path, sha256 = Hash(path), sizeBytes = new FileInfo(path).Length };
        }
        private static void Require(bool value, string message)
        {
            if (!value) throw new BuildFailedException(message);
        }

        public static void Prepare()
        {
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string root = Path.GetFullPath(BaselineBuild.Argument("-shadowR02OrdinaryRoot", ""));
            string parent = Path.Combine(project, "_temp/AssemblyShadow") + Path.DirectorySeparatorChar;
            Require(root.StartsWith(parent, StringComparison.Ordinal) && !Directory.Exists(root) && !File.Exists(root),
                "An unused in-project -shadowR02OrdinaryRoot is required.");
            Directory.CreateDirectory(root);
            var receipt = new Receipt { projectRoot = project, outputRoot = root,
                unityVersion = Application.unityVersion, target = EditorUserBuildSettings.activeBuildTarget.ToString() };
            try
            {
                Require(Application.unityVersion == "2022.3.62f2" && EditorUserBuildSettings.activeBuildTarget == BuildTarget.StandaloneOSX,
                    "R02 ordinary input requires Unity 2022.3.62f2 StandaloneOSX.");
                string pins = Path.Combine(project, "ProjectSettings/AssemblyShadowSourcePins.json");
                receipt.sourcePinsSha256 = Hash(pins);
                receipt.sources = Directory.GetFiles(Path.Combine(project, Source), "*", SearchOption.AllDirectories)
                    .Where(path => path.EndsWith(".cs", StringComparison.Ordinal) || path.EndsWith(".asmdef", StringComparison.Ordinal))
                    .OrderBy(path => path, StringComparer.Ordinal).Select(Record).ToArray();
                Require(receipt.sources.Length > 0, "Ordinary witness source is missing.");
                // Use the existing canonical HybridCLR compiler entry, with a
                // new output directory. No candidate files, cached DLL copies,
                // pin rewrite, or special Player validation override is used.
                string compiledRoot = Path.Combine(root, "compiled");
                CompileDllCommand.CompileDll(compiledRoot, EditorUserBuildSettings.activeBuildTarget, true);
                receipt.compiled = Record(Path.Combine(compiledRoot, Name + ".dll"));
                Require(receipt.sources.All(file => Hash(file.path) == file.sha256) && Hash(pins) == receipt.sourcePinsSha256,
                    "Source/pins changed while producing ordinary input.");
                Require(AssemblyName.GetAssemblyName(receipt.compiled.path).FullName ==
                    Name + ", Version=0.0.0.0, Culture=neutral, PublicKeyToken=null", "Wrong ordinary provider identity.");
                Require(receipt.compiled.sha256 == Expected,
                    "Ordinary compiler output differs from the frozen M00 contract; retain output and return to Primary. Expected " + Expected + " actual " + receipt.compiled.sha256);
                string destination = Path.Combine(project, Destination);
                Directory.CreateDirectory(Path.GetDirectoryName(destination));
                if (File.Exists(destination))
                    Require(Hash(destination) == Expected, "Existing M00 input differs; it must not be overwritten.");
                else
                    using (var stream = new FileStream(destination, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                    { byte[] bytes = File.ReadAllBytes(receipt.compiled.path); stream.Write(bytes, 0, bytes.Length); stream.Flush(true); }
                receipt.staged = Record(destination);
                Require(receipt.staged.sha256 == Expected, "Staged M00 bytes changed.");
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                Require(Hash(destination) == Expected, "Imported M00 bytes changed.");
                receipt.result = "Passed";
            }
            catch (Exception error) { receipt.error = error.ToString(); throw; }
            finally
            {
                using (var stream = new StreamWriter(new FileStream(Path.Combine(root, "preparation.json"), FileMode.CreateNew)))
                    stream.Write(JsonUtility.ToJson(receipt, true));
            }
        }
    }
}
