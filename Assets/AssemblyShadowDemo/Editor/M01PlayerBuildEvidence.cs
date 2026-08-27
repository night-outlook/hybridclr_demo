using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using HybridCLR.Editor;
using AssemblyShadowBaseline.Editor;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Captures the physical managed inputs and native library from the completed Player.
    /// This is build evidence only; runtime assembly introspection is intentionally separate.
    /// </summary>
    internal static class M01PlayerBuildEvidence
    {
        private static readonly string[] RequiredAssemblies =
        {
            "AssemblyA.Contracts",
            "AssemblyA.Implementation.Extensibility",
            "AssemblyA.Implementation.Internal",
        };

        public static void CaptureExisting()
        {
            Capture(EditorUserBuildSettings.activeBuildTarget, "Builds/AssemblyShadow/M01/Prototype.app");
        }

        internal static void Capture(BuildTarget target, string defaultOutput)
        {
            string strippedDirectory = Path.GetFullPath(SettingsUtil.GetAssembliesPostIl2CppStripDir(target));
            if (!Directory.Exists(strippedDirectory))
                throw new BuildFailedException("Post-IL2CPP-strip assembly directory is missing: " + strippedDirectory);

            string baselineRoot = M01Paths.BaselineRoot(target);
            BuildBaselineBundles.VerifyExisting(baselineRoot);
            var baseline = BuildBaselineBundles.ReadManifest(baselineRoot);
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/M01PlayerAssemblyEvidence-" +
                DateTime.UtcNow.Ticks.ToString(CultureInfo.InvariantCulture));
            Directory.CreateDirectory(snapshot);
            var assemblies = new List<AssemblyEvidence>();
            foreach (string name in RequiredAssemblies)
            {
                string source = FindExactAssembly(strippedDirectory, name);
                string copied = Path.Combine(snapshot, name + ".dll");
                M01BuildSupport.CopyFile(source, copied);
                var expected = baseline.assemblies.FirstOrDefault(item => item.name == name);
                if (expected == null)
                    throw new BuildFailedException("Frozen baseline manifest lacks assembly " + name + ".");
                string baselineAssembly = Path.Combine(baselineRoot, expected.path);
                CompilePatchDlls.VerifySemanticEquivalence(baselineAssembly, copied);
                assemblies.Add(new AssemblyEvidence
                {
                    name = name,
                    path = copied,
                    sourcePath = source,
                    sha256 = M01BuildSupport.Sha256(copied),
                    mvid = M01BuildSupport.ReadMvid(copied),
                    baselineMvid = expected.mvid,
                    baselineSha256 = expected.sha256,
                    matchesBaselineMvid = M01BuildSupport.ReadMvid(copied) == expected.mvid,
                    matchesBaselineSha256 = M01BuildSupport.Sha256(copied) == expected.sha256,
                    matchesBaselineSemantics = true,
                    comparisonPolicy = CompilePatchDlls.SemanticComparisonPolicy,
                });
            }

            string outputPath = ResolveOutputPath(target, defaultOutput);
            string gameAssembly = FindGameAssembly(outputPath);
            string manifestPath = Path.Combine(baselineRoot, "baseline-manifest.json");
            var receipt = new PlayerEvidence
            {
                schemaVersion = 1,
                milestone = "M01",
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                architecture = BaselineBuild.TargetArchitecture(),
                strippedAssemblyDirectory = strippedDirectory,
                snapshotDirectory = snapshot,
                outputPath = outputPath,
                baselineManifestPath = Path.GetFullPath(manifestPath),
                baselineManifestSha256 = M01BuildSupport.Sha256(manifestPath),
                gameAssemblyPath = gameAssembly,
                gameAssemblySha256 = M01BuildSupport.Sha256(gameAssembly),
                comparisonPolicy = CompilePatchDlls.SemanticComparisonPolicy,
                assemblies = assemblies.ToArray(),
            };
            Directory.CreateDirectory("_temp/AssemblyShadow");
            File.WriteAllText("_temp/AssemblyShadow/m01-player-assemblies.json",
                JsonUtility.ToJson(receipt, true));
            Debug.Log("[AssemblyShadow M01] Player assembly evidence: " + JsonUtility.ToJson(receipt));
        }

        private static string FindExactAssembly(string directory, string name)
        {
            string expected = name + ".dll";
            string[] matches = Directory.GetFiles(directory, expected, SearchOption.TopDirectoryOnly);
            if (matches.Length != 1)
                throw new BuildFailedException("Expected exactly one stripped AOT input " + expected + " in " + directory + ". Found " + matches.Length + ".");
            return matches[0];
        }

        private static string FindGameAssembly(string outputPath)
        {
            if (!Directory.Exists(outputPath))
                throw new BuildFailedException("Built Player output directory is missing: " + outputPath);
            string[] matches = Directory.GetFiles(outputPath, "GameAssembly.dylib", SearchOption.AllDirectories);
            if (matches.Length != 1)
                throw new BuildFailedException("Expected exactly one GameAssembly.dylib below " + outputPath + ". Found " + matches.Length + ".");
            return matches[0];
        }

        private static string ResolveOutputPath(BuildTarget target, string defaultOutput)
        {
            string output = BaselineBuild.Argument("-shadowBuildOutput", defaultOutput);
            if (target == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal))
                output = output.Substring(0, output.Length - 4) + ".exe";
            return Path.GetFullPath(output);
        }

        [Serializable]
        private sealed class PlayerEvidence
        {
            public int schemaVersion;
            public string milestone;
            public string unityVersion;
            public string target;
            public string architecture;
            public string strippedAssemblyDirectory;
            public string snapshotDirectory;
            public string outputPath;
            public string baselineManifestPath;
            public string baselineManifestSha256;
            public string gameAssemblyPath;
            public string gameAssemblySha256;
            public string comparisonPolicy;
            public AssemblyEvidence[] assemblies;
        }

        [Serializable]
        private sealed class AssemblyEvidence
        {
            public string name;
            public string path;
            public string sourcePath;
            public string sha256;
            public string mvid;
            public string baselineMvid;
            public string baselineSha256;
            public bool matchesBaselineMvid;
            public bool matchesBaselineSha256;
            public bool matchesBaselineSemantics;
            public string comparisonPolicy;
        }
    }
}
