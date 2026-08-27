using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class M02ReflectionBindingValidation
    {
        private const string ConfigurationPath = "ProjectSettings/AssemblyShadowReflectionBindings.json";
        private const string CanvasPath = "Packages/com.unity.render-pipelines.core/Runtime/Debugging/Prefabs/Resources/DebugUICanvas.prefab";
        private const string CanvasType = "UnityEngine.Rendering.UI.DebugUIHandlerCanvas";
        private const string EnumType = "UnityEngine.Rendering.SerializableEnum";
        private const string GuardPrefix = "__AssemblyShadowReflectionBinding_";

        [Serializable] private sealed class Configuration { public Site[] sites; }
        [Serializable] private sealed class Site { public string id; public string[] allowedTypes; }

        public static void ValidateProjectAssets()
        {
            // The production parser validates identities, hashes and finite
            // target syntax. This additional check binds the domain to real
            // serialized strings, including Unity YAML whitespace folding.
            ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var configuration = JsonUtility.FromJson<Configuration>(Encoding.UTF8.GetString(File.ReadAllBytes(ConfigurationPath)));
            Require(configuration != null && configuration.sites != null && configuration.sites.Length == 2, "Expected two binding contracts.");
            var canvas = configuration.sites.Single(site => site.id == "urp-debug-ui-prefab-types");
            var enumSite = configuration.sites.Single(site => site.id == "urp-serializable-enum-player");
            Require(enumSite.allowedTypes != null && enumSite.allowedTypes.Length == 0, "SerializableEnum Player contract must be explicitly deny-all.");
            var component = CanvasComponent();
            var serialized = new SerializedObject(component);
            SerializedProperty prefabs = serialized.FindProperty("prefabs");
            Require(prefabs != null && prefabs.isArray && prefabs.arraySize == 26, "The pinned URP prefab domain changed.");
            var actual = Enumerable.Range(0, prefabs.arraySize).Select(index =>
                prefabs.GetArrayElementAtIndex(index).FindPropertyRelative("type").stringValue).OrderBy(value => value, StringComparer.Ordinal).ToArray();
            Require(canvas.allowedTypes != null && actual.SequenceEqual(canvas.allowedTypes.OrderBy(value => value, StringComparer.Ordinal), StringComparer.Ordinal),
                "The finite contract must exactly match every serialized URP prefab type name.");
            Debug.Log("[AssemblyShadow M02] All 26 serialized URP prefab type names match the finite Player contract.");
        }

        public static void ValidateEditorBehavior()
        {
            Type canvas = CanvasComponent().GetType();
            Type serializableEnum = canvas.Assembly.GetType(EnumType, true);
            foreach (Type type in new[] { canvas, serializableEnum })
                Require(!type.GetMethods(BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.DeclaredOnly)
                    .Any(method => method.Name.StartsWith(GuardPrefix, StringComparison.Ordinal)), "Player guards leaked into the Editor domain.");
            object value = Activator.CreateInstance(serializableEnum, new object[] { typeof(DayOfWeek) });
            var resolved = (Enum)serializableEnum.GetProperty("value").GetValue(value);
            Require(resolved != null && resolved.GetType() == typeof(DayOfWeek) && Convert.ToInt32(resolved) == 0,
                "Unmodified Editor SerializableEnum behavior changed.");
        }

        public static void StageConfiguration()
        {
            ValidateProjectAssets();
            ValidateEditorBehavior();
            byte[] bytes = File.ReadAllBytes(ConfigurationPath);
            string destination = Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M02/reflection-bindings.json");
            Directory.CreateDirectory(Path.GetDirectoryName(destination));
            File.WriteAllBytes(destination, bytes);
            Require(ShadowHash.File(destination) == ShadowHash.Bytes(bytes), "Staged binding bytes changed.");
            AssetDatabase.Refresh();
        }

        private static Component CanvasComponent()
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CanvasPath);
            Require(prefab != null, "The pinned URP debug canvas prefab is missing.");
            return prefab.GetComponents<Component>().Single(component => component != null && component.GetType().FullName == CanvasType);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
