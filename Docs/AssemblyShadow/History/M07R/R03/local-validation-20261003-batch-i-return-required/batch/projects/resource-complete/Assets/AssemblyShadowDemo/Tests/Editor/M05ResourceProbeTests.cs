using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    /// <summary>Pure input/schema checks; real binding remains a Player acceptance gate.</summary>
    public sealed class M05ResourceProbeTests
    {
        private const string UnityVersion = "2022.3.62f2";
        private static Type Probe { get { return Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M05ResourceProbe", true); } }

        [Test]
        public void FrozenInputGraphPreservesEveryDeclaredField()
        {
            AssertShape("FrozenManifest", "schemaVersion,baselineBuildId,unityVersion,target,architecture,sourceSnapshotPath,bundles,assemblies,assets");
            AssertShape("FrozenBundle", "name,path,sha256");
            AssertShape("FrozenAssembly", "name,path,sha256,mvid,pdbPath,pdbSha256");
            AssertShape("FrozenAsset", "kind,path,assetGuid,scriptGuid,serializedNumber");
            Assert.AreEqual(typeof(IEnumerator), Probe.GetMethod("Run", BindingFlags.Public | BindingFlags.Static).ReturnType);
        }

        [Test]
        public void FrozenManifestAcceptsTheExactBundleAndAssetShape()
        {
            object manifest = Read(ValidJson());
            Validate(manifest);
            string json = JsonUtility.ToJson(manifest);
            Validate(Read(json));
        }

        [TestCase("\"schemaVersion\":1", "\"schemaVersion\":2")]
        [TestCase("M01-Baseline-v1", "M05-Baseline-v1")]
        [TestCase("2022.3.62f2", "2022.3.61f1")]
        [TestCase("StandaloneOSX", "StandaloneWindows64")]
        [TestCase("arm64", "x64")]
        [TestCase("Bundles/versioned-data.bundle", "../versioned-data.bundle")]
        [TestCase("Bundles/versioned-data.bundle", "/tmp/versioned-data.bundle")]
        [TestCase("Bundles/versioned-data.bundle", "Bundles/other.bundle")]
        [TestCase("\"serializedNumber\":1234", "\"serializedNumber\":1235")]
        [TestCase("\"serializedNumber\":5678", "\"serializedNumber\":5679")]
        [TestCase("Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset", "Assets/AssemblyShadowDemo/../VersionedData.asset")]
        public void FrozenManifestRejectsIdentityPathAndValueDrift(string oldValue, string newValue)
        {
            var exception = Assert.Throws<TargetInvocationException>(() => Validate(Read(ValidJson().Replace(oldValue, newValue))));
            Assert.IsInstanceOf<InvalidOperationException>(exception.InnerException);
        }

        [Test]
        public void FrozenManifestRejectsDuplicateMissingAndUnboundBundleEntries()
        {
            foreach (string malformed in new[] {
                ValidJson().Replace("business-scene.bundle", "versioned-prefab.bundle"),
                ValidJson().Replace("\"kind\":\"scene\"", "\"kind\":\"prefab\""),
                ValidJson().Replace(new string('0', 64), "missing-hash"),
                ValidJson().Replace("\"bundles\":[", "\"bundles\":[null,"),
                ValidJson().Replace("\"assets\":[", "\"assets\":[null,") })
            {
                var exception = Assert.Throws<TargetInvocationException>(() => Validate(Read(malformed)));
                Assert.IsInstanceOf<InvalidOperationException>(exception.InnerException);
            }
        }

        [Test]
        public void BundlePathRejectsTraversalEvenOutsideManifestValidation()
        {
            Type bundleType = Probe.GetNestedType("FrozenBundle", BindingFlags.Public);
            object bundle = JsonUtility.FromJson("{\"name\":\"versioned-data.bundle\",\"path\":\"Bundles/versioned-data.bundle\"}", bundleType);
            MethodInfo resolve = Probe.GetMethod("BundlePath", BindingFlags.NonPublic | BindingFlags.Static);
            string root = Path.GetFullPath("_temp/M05ResourcePathTest");
            Assert.AreEqual(Path.Combine(root, "Bundles/versioned-data.bundle"), resolve.Invoke(null, new[] { (object)root, bundle }));
            bundleType.GetField("path").SetValue(bundle, "../versioned-data.bundle");
            var exception = Assert.Throws<TargetInvocationException>(() => resolve.Invoke(null, new[] { (object)root, bundle }));
            Assert.IsInstanceOf<InvalidOperationException>(exception.InnerException);
        }

        [Test]
        public void ResourceSourceLoadsHashedBytesAndRecordsRealReloadAndReferenceIdentity()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M05ResourceProbe.cs");
            StringAssert.Contains("AssetBundle.LoadFromMemory(bytes)", source);
            StringAssert.Contains("string actual = Hash(bytes)", source);
            Assert.IsFalse(source.Contains("AssetBundle.LoadFromFile"));
            StringAssert.Contains("System.Object.ReferenceEquals(data, context.Data)", source);
            StringAssert.Contains("System.Object.ReferenceEquals(firstComponent, reloadedComponent)", source);
            StringAssert.Contains("SceneManager.UnloadSceneAsync(firstScene)", source);
            StringAssert.Contains("SceneManager.UnloadSceneAsync(reloadedScene)", source);
            StringAssert.Contains("AssemblyShadowRuntime.GetTypeResolutionInfo(actual, out json)", source);
            foreach (string phase in new[] { "prefab", "scene-first", "scene-reload" }) StringAssert.Contains("\"" + phase + "\"", source);
            Assert.IsFalse(source.Contains("MonoScript"));
            Assert.IsFalse(source.Contains("ModuleVersionId"));
            Assert.IsFalse(source.Contains("InspectAssemblyShadowPrototype"));
        }

        private static void AssertShape(string name, string expected)
        {
            Type type = Probe.GetNestedType(name, BindingFlags.Public);
            Assert.IsNotNull(type); Assert.IsTrue(type.IsSerializable); Assert.IsTrue(type.IsDefined(typeof(PreserveAttribute), false));
            FieldInfo[] fields = type.GetFields(BindingFlags.Instance | BindingFlags.Public);
            CollectionAssert.AreEquivalent(expected.Split(','), fields.Select(field => field.Name));
            foreach (FieldInfo field in fields) Assert.IsTrue(field.IsDefined(typeof(PreserveAttribute), false), name + "." + field.Name);
        }
        private static object Read(string json) { return JsonUtility.FromJson(json, Probe.GetNestedType("FrozenManifest", BindingFlags.Public)); }
        private static void Validate(object manifest) { Probe.GetMethod("ValidateManifest", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, new[] { manifest, UnityVersion }); }

        private static string ValidJson()
        {
            string hash = new string('0', 64);
            string bundles = string.Join(",", new[] { "business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle" }
                .Select(name => "{\"name\":\"" + name + "\",\"path\":\"Bundles/" + name + "\",\"sha256\":\"" + hash + "\"}"));
            return "{\"schemaVersion\":1,\"baselineBuildId\":\"M01-Baseline-v1\",\"unityVersion\":\"" + UnityVersion +
                "\",\"target\":\"StandaloneOSX\",\"architecture\":\"arm64\",\"sourceSnapshotPath\":\"AssemblySnapshot/Source\",\"bundles\":[" + bundles +
                "],\"assemblies\":[],\"assets\":[{\"kind\":\"scene\",\"path\":\"Assets/AssemblyShadowDemo/Scenes/Business.unity\",\"serializedNumber\":0}," +
                "{\"kind\":\"prefab\",\"path\":\"Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab\",\"serializedNumber\":1234}," +
                "{\"kind\":\"scriptableObject\",\"path\":\"Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset\",\"serializedNumber\":5678}]}";
        }
    }
}
