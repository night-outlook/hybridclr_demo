using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AssemblyA.Implementation.Internal;
using AssemblyShadowBaseline.Editor;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class BuildBaselineBundles
    {
        public static void Build()
        {
            BaselineBuild.Configure();
            M01BuildSupport.EnsureDemoAssets();
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            string root = M01Paths.BaselineRoot(target);
            if (Directory.Exists(root))
            {
                VerifyExisting(root);
                Debug.Log("[AssemblyShadow M01] Reused immutable baseline artifacts: " + Path.GetFullPath(root));
                return;
            }

            string parent = Path.GetDirectoryName(root);
            Directory.CreateDirectory(parent);
            string temporary = root + ".building";
            if (Directory.Exists(temporary))
            {
                // An interruption after the full manifest was written must not rebuild
                // the first bundles. Verify that complete snapshot and finish metadata only.
                FinalizeStaging(temporary, root);
                Debug.Log("[AssemblyShadow M01] Finalized existing first-build bytes without rebuilding bundles: " + root);
                return;
            }
            Directory.CreateDirectory(temporary);
            try
            {
                string bundles = Path.Combine(temporary, "Bundles");
                Directory.CreateDirectory(bundles);
                var builds = new[]
                {
                    new AssetBundleBuild { assetBundleName = "business-scene.bundle", assetNames = new[] { M01Paths.BusinessScene } },
                    new AssetBundleBuild { assetBundleName = "versioned-prefab.bundle", assetNames = new[] { M01Paths.Prefab } },
                    new AssetBundleBuild { assetBundleName = "versioned-data.bundle", assetNames = new[] { M01Paths.Data } },
                };
                var result = BuildPipeline.BuildAssetBundles(bundles, builds,
                    BuildAssetBundleOptions.ChunkBasedCompression | BuildAssetBundleOptions.StrictMode, target);
                if (result == null)
                    throw new BuildFailedException("BuildAssetBundles returned no manifest.");
                string baselineScripts = M01BuildSupport.CompileBaselineScripts(target);
                var manifest = CreateManifest(temporary, target, builds, baselineScripts);
                File.WriteAllText(Path.Combine(temporary, "baseline-manifest.json"), JsonUtility.ToJson(manifest, true));
                FinalizeStaging(temporary, root);
            }
            catch
            {
                // Keep a failed staging directory for diagnosis; immutable roots are never removed or overwritten.
                throw;
            }
            VerifyExisting(root);
            Debug.Log("[AssemblyShadow M01] Wrote immutable baseline artifacts: " + Path.GetFullPath(root));
        }

        private static void FinalizeStaging(string temporary, string root)
        {
            VerifyExisting(temporary);
            var manifest = ReadManifest(temporary);
            Directory.CreateDirectory(Path.Combine(temporary, "Catalog"));
            string catalogPath = Path.Combine(temporary, "Catalog/catalog.json");
            string catalog = JsonUtility.ToJson(new BundleCatalog { bundles = manifest.bundles }, true);
            if (!File.Exists(catalogPath)) File.WriteAllText(catalogPath, catalog);
            else if (File.ReadAllText(catalogPath) != catalog)
                throw new BuildFailedException("Existing staging catalog differs from the recorded first build.");
            // Unity names its aggregate manifest after the output folder, not the target.
            string unityManifest = Path.Combine(temporary, "Bundles/Bundles.manifest");
            string catalogManifest = Path.Combine(temporary, "Catalog/UnityAssetBundleManifest.txt");
            if (File.Exists(unityManifest) && !File.Exists(catalogManifest))
                M01BuildSupport.CopyFile(unityManifest, catalogManifest);
            M01BuildSupport.SetReadonly(temporary);
            Directory.Move(temporary, root);
            VerifyExisting(root);
        }

        internal static BaselineManifest ReadManifest(string root)
        {
            string path = Path.Combine(root, "baseline-manifest.json");
            if (!File.Exists(path))
                throw new BuildFailedException("Immutable baseline root has no baseline-manifest.json: " + root);
            try { return JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(path)); }
            catch (Exception exception) { throw new BuildFailedException("Invalid baseline manifest: " + exception.Message); }
        }

        internal static void VerifyExisting(string root)
        {
            BaselineManifest manifest = ReadManifest(root);
            if (manifest.schemaVersion != 1 || manifest.baselineBuildId != M01Paths.BaselineBuildId)
                throw new BuildFailedException("Baseline manifest schema/build id mismatch.");
            if (manifest.unityVersion != Application.unityVersion ||
                manifest.target != EditorUserBuildSettings.activeBuildTarget.ToString() ||
                manifest.architecture != BaselineBuild.TargetArchitecture())
                throw new BuildFailedException("Baseline Unity/target/architecture does not match this build.");
            string[] required = { "business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle" };
            foreach (string name in required)
            {
                BundleEntry entry = manifest.bundles == null ? null : manifest.bundles.FirstOrDefault(item => item.name == name);
                if (entry == null)
                    throw new BuildFailedException("Baseline manifest is missing " + name + ".");
                string path = Path.Combine(root, entry.path.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(path) || M01BuildSupport.Sha256(path) != entry.sha256)
                    throw new BuildFailedException("Immutable baseline bundle hash mismatch: " + path);
            }
            if (manifest.assemblies == null || manifest.assemblies.Length < 3)
                throw new BuildFailedException("Baseline assembly snapshot is incomplete.");
            foreach (AssemblyEntry assembly in manifest.assemblies)
            {
                string path = Path.Combine(root, assembly.path.Replace('/', Path.DirectorySeparatorChar));
                if (!File.Exists(path) || M01BuildSupport.Sha256(path) != assembly.sha256)
                    throw new BuildFailedException("Immutable baseline assembly hash mismatch: " + path);
                if (!string.IsNullOrEmpty(assembly.pdbPath))
                {
                    string pdbPath = Path.Combine(root, assembly.pdbPath.Replace('/', Path.DirectorySeparatorChar));
                    if (!File.Exists(pdbPath) || M01BuildSupport.Sha256(pdbPath) != assembly.pdbSha256)
                        throw new BuildFailedException("Immutable baseline PDB hash mismatch: " + pdbPath);
                }
            }
        }

        private static BaselineManifest CreateManifest(string temporary, BuildTarget target, AssetBundleBuild[] builds, string baselineScripts)
        {
            string snapshotRoot = Path.Combine(temporary, "AssemblySnapshot");
            Directory.CreateDirectory(snapshotRoot);
            string sourceRoot = Path.Combine(snapshotRoot, "Source");
            Directory.CreateDirectory(sourceRoot);
            foreach (string file in Directory.GetFiles(M01Paths.Root, "*", SearchOption.AllDirectories)
                .Where(file => file.EndsWith(".cs", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith(".asmdef", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith(".meta", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith(".unity", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith(".asset", StringComparison.OrdinalIgnoreCase) ||
                               file.EndsWith("link.xml", StringComparison.OrdinalIgnoreCase)))
            {
                string relative = file.Substring(M01Paths.Root.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar, '/');
                M01BuildSupport.CopyFile(file, Path.Combine(sourceRoot, "Assets/AssemblyShadowDemo", relative));
            }

            var assemblies = new List<AssemblyEntry>();
            foreach (string name in new[] { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", M01Paths.InternalAssemblyName })
            {
                string source = M01BuildSupport.FindCompiledAssembly(baselineScripts, name);
                string relative = "AssemblySnapshot/" + name + ".dll";
                M01BuildSupport.CopyFile(source, Path.Combine(temporary, relative));
                var assembly = new AssemblyEntry { name = name, path = relative, sha256 = M01BuildSupport.Sha256(Path.Combine(temporary, relative)), mvid = M01BuildSupport.ReadMvid(source) };
                string pdb = Path.ChangeExtension(source, ".pdb");
                if (File.Exists(pdb))
                {
                    M01BuildSupport.CopyFile(pdb, Path.Combine(temporary, "AssemblySnapshot/" + name + ".pdb"));
                    assembly.pdbPath = "AssemblySnapshot/" + name + ".pdb";
                    assembly.pdbSha256 = M01BuildSupport.Sha256(Path.Combine(temporary, assembly.pdbPath));
                }
                assemblies.Add(assembly);
            }

            var bundles = new List<BundleEntry>();
            foreach (AssetBundleBuild build in builds)
            {
                string path = Path.Combine(temporary, "Bundles", build.assetBundleName);
                bundles.Add(new BundleEntry { name = build.assetBundleName, path = "Bundles/" + build.assetBundleName, sha256 = M01BuildSupport.Sha256(path) });
            }
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(M01Paths.Prefab);
            var prefabComponent = prefab.GetComponent<VersionedPrefabComponent>();
            var data = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(M01Paths.Data);
            if (prefabComponent == null || prefabComponent.ReadSerializedNumber() != 1234 ||
                prefabComponent.ReadBaseSerializedValue() != 7 || string.IsNullOrEmpty(prefabComponent.ReadDataReferenceName()))
                throw new BuildFailedException("Prefab serialized baseline values/reference are not ready to freeze.");
            if (data == null || data.ReadSerializedNumber() != 5678)
                throw new BuildFailedException("ScriptableObject serialized baseline value is not ready to freeze.");
            return new BaselineManifest
            {
                schemaVersion = 1,
                baselineBuildId = M01Paths.BaselineBuildId,
                unityVersion = Application.unityVersion,
                target = target.ToString(),
                architecture = BaselineBuild.TargetArchitecture(),
                sourceSnapshotPath = "AssemblySnapshot/Source",
                bundles = bundles.ToArray(),
                assemblies = assemblies.ToArray(),
                assets = new[]
                {
                    new AssetEntry { kind = "scene", path = M01Paths.BusinessScene, assetGuid = M01BuildSupport.AssetGuid(M01Paths.BusinessScene) },
                    new AssetEntry { kind = "prefab", path = M01Paths.Prefab, assetGuid = M01BuildSupport.AssetGuid(M01Paths.Prefab), scriptGuid = M01BuildSupport.ScriptGuid(prefabComponent), serializedNumber = 1234 },
                    new AssetEntry { kind = "scriptableObject", path = M01Paths.Data, assetGuid = M01BuildSupport.AssetGuid(M01Paths.Data), scriptGuid = M01BuildSupport.AssetGuid(AssetDatabase.GetAssetPath(MonoScript.FromScriptableObject(AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(M01Paths.Data)))), serializedNumber = 5678 },
                }
            };
        }

        [Serializable] internal sealed class BaselineManifest { public int schemaVersion; public string baselineBuildId; public string unityVersion; public string target; public string architecture; public string sourceSnapshotPath; public BundleEntry[] bundles; public AssemblyEntry[] assemblies; public AssetEntry[] assets; }
        [Serializable] internal sealed class BundleEntry { public string name; public string path; public string sha256; }
        [Serializable] internal sealed class BundleCatalog { public BundleEntry[] bundles; }
        [Serializable] internal sealed class AssemblyEntry { public string name; public string path; public string sha256; public string mvid; public string pdbPath; public string pdbSha256; }
        [Serializable] internal sealed class AssetEntry { public string kind; public string path; public string assetGuid; public string scriptGuid; public int serializedNumber; }
    }
}
