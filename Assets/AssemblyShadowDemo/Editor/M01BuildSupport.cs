using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Globalization;
using System.Security.Cryptography;
using AssemblyA.Implementation.Internal;
using AssemblyShadowDemo.Consumers;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Player;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    internal static class M01Paths
    {
        public const string Root = "Assets/AssemblyShadowDemo";
        public const string BootstrapScene = Root + "/Scenes/Bootstrap.unity";
        public const string BusinessScene = Root + "/Scenes/Business.unity";
        public const string Prefab = Root + "/ResourcesSource/VersionedPrefab.prefab";
        public const string Data = Root + "/ResourcesSource/VersionedData.asset";
        public const string BaselineBuildId = "M01-Baseline-v1";
        public const string BootstrapAssemblyName = "AssemblyShadowDemo.Bootstrap";
        public const string InternalAssemblyName = "AssemblyA.Implementation.Internal";
        public const string PatchDirectory = "PatchArtifacts/P01";

        public static string BaselineRoot(BuildTarget target)
        {
            string platform = target == BuildTarget.StandaloneOSX ? "StandaloneOSX" : target.ToString();
            return Path.Combine("BaselineArtifacts", platform, BaselineBuildId);
        }
    }

    internal static class M01BuildSupport
    {
        public static void EnsureDemoAssets()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(M01Paths.Prefab));
            Directory.CreateDirectory(Path.GetDirectoryName(M01Paths.BusinessScene));
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);

            var data = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(M01Paths.Data);
            if (data == null)
            {
                data = ScriptableObject.CreateInstance<VersionedScriptableObject>();
                AssetDatabase.CreateAsset(data, M01Paths.Data);
            }
            SetDemoValue(data, "value", 5678, "M01-DATA");

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(M01Paths.Prefab);
            if (prefab == null)
            {
                var source = new GameObject("VersionedPrefab");
                var component = source.AddComponent<VersionedPrefabComponent>();
                SetDemoValue(component, "value", 1234, "M01-PREFAB");
                SetSerializedInt(component, "baseSerializedValue", 7);
                SetObjectReference(component, "dataReference", data);
                PrefabUtility.SaveAsPrefabAsset(source, M01Paths.Prefab);
                UnityEngine.Object.DestroyImmediate(source);
            }
            else
            {
                var component = prefab.GetComponent<VersionedPrefabComponent>();
                if (component == null)
                    throw new BuildFailedException("VersionedPrefab.prefab does not contain VersionedPrefabComponent.");
                SetDemoValue(component, "value", 1234, "M01-PREFAB");
                SetSerializedInt(component, "baseSerializedValue", 7);
                SetObjectReference(component, "dataReference", data);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            data = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(M01Paths.Data);
            prefab = AssetDatabase.LoadAssetAtPath<GameObject>(M01Paths.Prefab);
            EnsureBusinessScene(data, prefab);
        }

        public static void EnsureBootstrapScene()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(M01Paths.BootstrapScene));
            if (File.Exists(M01Paths.BootstrapScene))
                return;

            Type bootstrapType = FindType(M01Paths.BootstrapAssemblyName, "AssemblyShadowDemo.ShadowBootstrap");
            if (bootstrapType == null || !typeof(MonoBehaviour).IsAssignableFrom(bootstrapType))
                throw new BuildFailedException("ShadowBootstrap is not available; compile Bootstrap before creating Bootstrap.unity.");

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("AssemblyShadow Bootstrap");
            root.AddComponent(bootstrapType);
            EditorSceneManager.SaveScene(scene, M01Paths.BootstrapScene);
            AssetDatabase.SaveAssets();
        }

        public static Type FindType(string assemblyName, string fullName)
        {
            var assembly = AppDomain.CurrentDomain.GetAssemblies()
                .FirstOrDefault(item => string.Equals(item.GetName().Name, assemblyName, StringComparison.Ordinal));
            return assembly == null ? null : assembly.GetType(fullName, false);
        }

        public static void SetDemoValue(UnityEngine.Object owner, string propertyName, int number, string text)
        {
            var serialized = new SerializedObject(owner);
            var value = serialized.FindProperty(propertyName);
            if (value == null)
                throw new BuildFailedException("Missing serialized field " + propertyName + " on " + owner.GetType().FullName + ".");
            value.FindPropertyRelative("number").intValue = number;
            value.FindPropertyRelative("text").stringValue = text;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(owner);
        }

        public static void SetSerializedInt(UnityEngine.Object owner, string propertyName, int value)
        {
            var serialized = new SerializedObject(owner);
            var property = serialized.FindProperty(propertyName);
            if (property == null)
                throw new BuildFailedException("Missing serialized field " + propertyName + " on " + owner.GetType().FullName + ".");
            property.intValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(owner);
        }

        public static void SetObjectReference(UnityEngine.Object owner, string propertyName, UnityEngine.Object value)
        {
            var serialized = new SerializedObject(owner);
            var property = serialized.FindProperty(propertyName);
            if (property == null)
                throw new BuildFailedException("Missing serialized field " + propertyName + " on " + owner.GetType().FullName + ".");
            property.objectReferenceValue = value;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(owner);
        }

        private static void EnsureBusinessScene(VersionedScriptableObject data, GameObject prefab)
        {
            if (File.Exists(M01Paths.BusinessScene))
                return;

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var business = new GameObject("Business Versioned Component");
            var component = business.AddComponent<VersionedPrefabComponent>();
            SetDemoValue(component, "value", 1234, "M01-SCENE");
            SetSerializedInt(component, "baseSerializedValue", 7);
            var serialized = new SerializedObject(component);
            serialized.FindProperty("dataReference").objectReferenceValue = data;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(business);

            var external = new GameObject("External Derived Component");
            external.AddComponent<DerivedExternalComponent>();
            EditorUtility.SetDirty(external);
            EditorSceneManager.SaveScene(scene, M01Paths.BusinessScene);
            AssetDatabase.SaveAssets();
        }

        public static string Sha256(string path)
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", string.Empty).ToLowerInvariant();
        }

        public static string Relative(string path)
        {
            return path.Replace('\\', '/');
        }

        public static string AssetGuid(string path)
        {
            string guid = AssetDatabase.AssetPathToGUID(path);
            if (string.IsNullOrEmpty(guid))
                throw new BuildFailedException("Asset has no GUID: " + path);
            return guid;
        }

        public static string ScriptGuid(UnityEngine.Object component)
        {
            string scriptPath = AssetDatabase.GetAssetPath(MonoScript.FromMonoBehaviour(component as MonoBehaviour));
            return AssetGuid(scriptPath);
        }

        public static string FindAssembly(string simpleName)
        {
            string root = Path.GetFullPath("Library/PlayerScriptAssemblies");
            if (!Directory.Exists(root))
                throw new BuildFailedException("PlayerScriptAssemblies is missing; compile the player scripts first.");
            string expected = simpleName + ".dll";
            string path = Directory.GetFiles(root, expected, SearchOption.AllDirectories).FirstOrDefault();
            if (path == null)
                throw new BuildFailedException("Compiled assembly is missing: " + expected);
            return path;
        }

        public static string CompileBaselineScripts(BuildTarget target)
        {
            string output = Path.GetFullPath("_temp/AssemblyShadow/M01BaselineScripts-" + DateTime.UtcNow.Ticks.ToString(CultureInfo.InvariantCulture));
            Directory.CreateDirectory(output);
            var settings = new ScriptCompilationSettings
            {
                group = BuildPipeline.GetBuildTargetGroup(target),
                target = target,
                options = EditorUserBuildSettings.development ? ScriptCompilationOptions.DevelopmentBuild : ScriptCompilationOptions.None,
                extraScriptingDefines = Array.Empty<string>(),
            };
            PlayerBuildInterface.CompilePlayerScripts(settings, output);
#if UNITY_2022
            EditorUtility.ClearProgressBar();
#endif
            return output;
        }

        public static string FindCompiledAssembly(string root, string simpleName)
        {
            string expected = simpleName + ".dll";
            string path = Directory.GetFiles(root, expected, SearchOption.AllDirectories).FirstOrDefault();
            if (path == null)
                throw new BuildFailedException("Fresh player compilation is missing " + expected + " in " + root);
            return path;
        }

        public static string ReadMvid(string assemblyPath)
        {
            using (var module = dnlib.DotNet.ModuleDefMD.Load(assemblyPath))
                return module.Mvid.ToString();
        }

        public static void CopyFile(string source, string destination)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(destination));
            File.Copy(source, destination, true);
        }

        public static void CopyTree(string source, string destination)
        {
            foreach (string directory in Directory.GetDirectories(source, "*", SearchOption.AllDirectories))
                Directory.CreateDirectory(Path.Combine(destination, directory.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)));
            foreach (string file in Directory.GetFiles(source, "*", SearchOption.AllDirectories))
                CopyFile(file, Path.Combine(destination, file.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)));
        }

        public static void SetReadonly(string root)
        {
            foreach (string file in Directory.GetFiles(root, "*", SearchOption.AllDirectories))
                File.SetAttributes(file, File.GetAttributes(file) | FileAttributes.ReadOnly);
        }

        public static void StageBaselineArtifacts(string source, string destination)
        {
            // Baseline staging and P01 patch staging share M01. Preserve the sibling P01 directory and
            // never put source/DLL snapshots under Assets/StreamingAssets where Unity would import them.
            Directory.CreateDirectory(destination);
            CopyBaselinePath(source, destination, "baseline-manifest.json");
            CopyBaselineDirectory(source, destination, "Bundles");
            CopyBaselineDirectory(source, destination, "Catalog");
        }

        private static void CopyBaselineDirectory(string source, string destination, string name)
        {
            string sourceDirectory = Path.Combine(source, name);
            if (!Directory.Exists(sourceDirectory)) return;
            foreach (string file in Directory.GetFiles(sourceDirectory, "*", SearchOption.AllDirectories))
            {
                string relative = file.Substring(sourceDirectory.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar, '/');
                CopyBaselinePath(source, destination, name + "/" + relative);
            }
        }

        private static void CopyBaselinePath(string source, string destination, string relative)
        {
            string from = Path.Combine(source, relative.Replace('/', Path.DirectorySeparatorChar));
            string to = Path.Combine(destination, relative.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(to))
            {
                if (Sha256(from) != Sha256(to))
                    throw new BuildFailedException("Staged baseline artifact differs: " + to);
                return;
            }
            CopyFile(from, to);
        }
    }
}
