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
        private const string M00ImageSha256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string M00ProviderIdentity = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        private const string M00ImagePath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        private const string H1WitnessMethodSignature = "AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()";
        private const string H1WitnessPrimaryMethodHash = "fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e";
        private const string H1WitnessAdditionalMethodHash = "4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e";

        [Serializable] private sealed class Configuration { public int schemaVersion, transformerVersion; public Site[] sites; }
        [Serializable] private sealed class Site
        {
            public string id, assembly, typeName, methodSignature, originalMethodHash, kind;
            public int operationIndex;
            public string imageSha256, providerAssemblyIdentity, imagePath, reason;
            public string[] allowedTypes;
            public MethodVariant[] additionalMethodVariants;
            public SemanticVariant[] providerSemanticVariants;
        }
        [Serializable] private sealed class MethodVariant { public string originalMethodHash; public int operationIndex; }
        [Serializable] private sealed class SemanticVariant { public string compilerMode, semanticHash; }

        public static void ValidateProjectAssets()
        {
            // The production parser validates identities, hashes and finite
            // target syntax. This additional check binds the domain to real
            // serialized strings, including Unity YAML whitespace folding.
            ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var configuration = JsonUtility.FromJson<Configuration>(Encoding.UTF8.GetString(File.ReadAllBytes(ConfigurationPath)));
            Require(configuration != null && configuration.schemaVersion == 4 && configuration.transformerVersion == 4 &&
                configuration.sites != null && configuration.sites.Length == 6, "Expected the exact six version-4 binding contracts.");
            var expectedIds = new[] { "urp-debug-ui-prefab-types", "urp-serializable-enum-player", "urp-volume-assembly-domain",
                "urp-volume-type-domain", "m00-normal-hot-update-image", "h1-count-ordinary-witness-image" };
            Require(configuration.sites.All(site => site != null && expectedIds.Contains(site.id, StringComparer.Ordinal)) &&
                expectedIds.All(id => configuration.sites.Count(site => site.id == id) == 1),
                "Reflection binding sites must contain exactly the six declared IDs.");
            var canvas = configuration.sites.Single(site => site.id == "urp-debug-ui-prefab-types");
            var enumSite = configuration.sites.Single(site => site.id == "urp-serializable-enum-player");
            var assemblySite = configuration.sites.Single(site => site.id == "urp-volume-assembly-domain");
            var typesSite = configuration.sites.Single(site => site.id == "urp-volume-type-domain");
            var imageSite = configuration.sites.Single(site => site.id == "m00-normal-hot-update-image");
            var h1WitnessSite = configuration.sites.Single(site => site.id == "h1-count-ordinary-witness-image");
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
            Require(imageSite.assembly == "AssemblyShadowBaseline.Aot" && imageSite.typeName == "AssemblyShadowBaseline.BaselineBootstrap" &&
                imageSite.methodSignature == "System.Void AssemblyShadowBaseline.BaselineBootstrap::Start()" &&
                imageSite.originalMethodHash == "5f6005b4130594f1c951bd8aba50f784b27976027977e8108ff6662170b87c22" &&
                imageSite.operationIndex == 28 && imageSite.kind == "FixedAssemblyBytes" && imageSite.allowedTypes != null && imageSite.allowedTypes.Length == 0 &&
                imageSite.imageSha256 == M00ImageSha256 && imageSite.providerAssemblyIdentity == M00ProviderIdentity && imageSite.imagePath == M00ImagePath &&
                imageSite.additionalMethodVariants != null && imageSite.additionalMethodVariants.Length == 1 &&
                imageSite.additionalMethodVariants[0].originalMethodHash == "27b4708dcf832f298f02c6939e548a06d0e34de908bf76743eebb0e80e22ed75" &&
                imageSite.additionalMethodVariants[0].operationIndex == 23 &&
                HasSemanticVariants(imageSite.providerSemanticVariants, "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369",
                    "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022"),
                "The ordinary hot-update image must retain its exact M00 identity, operation and semantics.");
            Require(h1WitnessSite.assembly == "AssemblyShadowDemo.Bootstrap" && h1WitnessSite.typeName == "AssemblyShadowDemo.H1CountEarlyStartup" &&
                h1WitnessSite.methodSignature == H1WitnessMethodSignature && h1WitnessSite.originalMethodHash == H1WitnessPrimaryMethodHash &&
                h1WitnessSite.operationIndex == 25 && h1WitnessSite.kind == "FixedAssemblyBytes" && h1WitnessSite.allowedTypes != null && h1WitnessSite.allowedTypes.Length == 0 &&
                h1WitnessSite.imageSha256 == M00ImageSha256 && h1WitnessSite.providerAssemblyIdentity == M00ProviderIdentity && h1WitnessSite.imagePath == M00ImagePath &&
                h1WitnessSite.additionalMethodVariants != null && h1WitnessSite.additionalMethodVariants.Length == 1 &&
                h1WitnessSite.additionalMethodVariants[0].originalMethodHash == H1WitnessAdditionalMethodHash &&
                h1WitnessSite.additionalMethodVariants[0].operationIndex == 25 &&
                HasSemanticVariants(h1WitnessSite.providerSemanticVariants, "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369",
                    "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022"),
                "The H1 ordinary witness must bind only its exact direct byte-load variants and pinned M00 provider.");
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

        private static bool HasSemanticVariants(SemanticVariant[] variants, string development, string release)
        {
            return variants != null && variants.Length == 2 &&
                variants.Count(value => value != null && value.compilerMode == "Development" && value.semanticHash == development) == 1 &&
                variants.Count(value => value != null && value.compilerMode == "Release" && value.semanticHash == release) == 1;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
