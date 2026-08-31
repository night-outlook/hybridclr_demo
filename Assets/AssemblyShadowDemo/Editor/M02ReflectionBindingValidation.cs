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

        [Serializable] private sealed class Configuration { public int schemaVersion, transformerVersion; public Site[] sites; }
        [Serializable] private sealed class Site { public string id, kind, imagePath; public string[] allowedTypes; }

        public static void ValidateProjectAssets()
        {
            // The production parser validates identities, hashes and finite
            // target syntax. This additional check binds the domain to real
            // serialized strings, including Unity YAML whitespace folding.
            ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var configuration = JsonUtility.FromJson<Configuration>(Encoding.UTF8.GetString(File.ReadAllBytes(ConfigurationPath)));
            Require(configuration != null && configuration.schemaVersion == 3 && configuration.transformerVersion == 3 &&
                configuration.sites != null && configuration.sites.Length == 5, "Expected five version-3 binding contracts.");
            var canvas = configuration.sites.Single(site => site.id == "urp-debug-ui-prefab-types");
            var enumSite = configuration.sites.Single(site => site.id == "urp-serializable-enum-player");
            var assemblySite = configuration.sites.Single(site => site.id == "urp-volume-assembly-domain");
            var typesSite = configuration.sites.Single(site => site.id == "urp-volume-type-domain");
            var imageSite = configuration.sites.Single(site => site.id == "m00-normal-hot-update-image");
            Require(canvas.kind == "TypeGetType" && enumSite.kind == "TypeGetType", "Type lookup contract kinds changed.");
            Require(enumSite.allowedTypes != null && enumSite.allowedTypes.Length == 0, "SerializableEnum Player contract must be explicitly deny-all.");
            Require(assemblySite.kind == "FiniteAssemblyList" && typesSite.kind == "FiniteAssemblyTypes" &&
                assemblySite.allowedTypes != null && assemblySite.allowedTypes.Length == 17 &&
                assemblySite.allowedTypes.Distinct(StringComparer.Ordinal).Count() == 17 &&
                typesSite.allowedTypes != null && assemblySite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal)
                    .SequenceEqual(typesSite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal), StringComparer.Ordinal),
                "Both volume-discovery guards must declare the same 17 exact target types.");
            Require(assemblySite.allowedTypes.All(value => value.StartsWith("UnityEngine.Rendering.Universal.", StringComparison.Ordinal) &&
                value.EndsWith(", Unity.RenderPipelines.Universal.Runtime, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null", StringComparison.Ordinal)),
                "The pinned noncandidate volume-discovery provider changed.");
            Require(imageSite.kind == "FixedAssemblyBytes" && imageSite.allowedTypes != null && imageSite.allowedTypes.Length == 0 &&
                imageSite.imagePath == "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes",
                "The ordinary hot-update image must be the exact staged M00 input.");
            ShadowReflectionBindingEvidence.ValidateProjectImages();
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
            Type coreUtils = canvas.Assembly.GetType("UnityEngine.Rendering.CoreUtils", true);
            Type discoveryLambda = coreUtils.GetNestedType("<>c", BindingFlags.NonPublic);
            foreach (Type type in new[] { canvas, serializableEnum, coreUtils, discoveryLambda }.Where(value => value != null))
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
