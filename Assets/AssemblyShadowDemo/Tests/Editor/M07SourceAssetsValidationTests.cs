using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07SourceAssetsValidationTests
    {
        private const string SourcePath = "Assets/AssemblyShadowDemo/Editor/M07SourceAssets.cs";
        private const string BaselineRoot = "Assets/AssemblyShadowDemo/M07Resources/Baseline";

        [Test]
        public void ValidateExistingIsExplicitAndReadOnly()
        {
            string source = File.ReadAllText(SourcePath);
            int start = source.IndexOf("internal static ShadowResourceBuildMap ValidateExisting(bool structural)", StringComparison.Ordinal);
            int end = source.IndexOf("internal static ShadowResourceBuildMap Map", start, StringComparison.Ordinal);
            Assert.GreaterOrEqual(start, 0, "The source asset consumer must expose ValidateExisting(bool).");
            Assert.Greater(end, start, "Could not isolate the read-only source validation implementation.");
            string validation = source.Substring(start, end - start);
            int helperStart = source.IndexOf("private static void Validate(", StringComparison.Ordinal);
            int helperEnd = source.IndexOf("private static ShadowBundleDefinition Bundle", helperStart, StringComparison.Ordinal);
            Assert.GreaterOrEqual(helperStart, 0, "The canonical validator helper is missing.");
            Assert.Greater(helperEnd, helperStart, "Could not isolate the canonical validator helper.");
            validation += source.Substring(helperStart, helperEnd - helperStart);
            foreach (string mutator in new[] { "SaveAssets(", "Refresh(", "CreateInstance<", "CreateAsset(", "SaveAsPrefabAsset(",
                "SaveScene(", "NewScene(", "InstantiatePrefab(", "DestroyImmediate(", "SetDirty(", "ApplyModifiedProperties" })
                Assert.Less(validation.IndexOf(mutator, StringComparison.Ordinal), 0, mutator);
            StringAssert.Contains("Validate(root, structural, map)", validation);
            StringAssert.Contains("return map;", validation);
            StringAssert.Contains("File.ReadAllText(path)", validation);
        }

        [Test]
        public void ValidateExistingPreservesBaselineInputBytes()
        {
            string[] paths = new[] {
                "VersionedPrefab.prefab", "NestedPrefab.prefab", "BusinessScene.unity", "AdditiveScene.unity",
                "VersionedData.asset", "ManagedGraph.asset", "MixedAssets.prefab", "MonoScriptCarrier.asset"
            }.SelectMany(name => new[] { BaselineRoot + "/" + name, BaselineRoot + "/" + name + ".meta" }).ToArray();
            var before = paths.ToDictionary(path => path, ReadBytes);

            Type sourceAssets = typeof(M07Build).Assembly.GetType("AssemblyShadowDemo.Editor.M07SourceAssets", true);
            MethodInfo validate = sourceAssets.GetMethod("ValidateExisting", BindingFlags.Static | BindingFlags.NonPublic);
            Assert.IsNotNull(validate);
            var map = (ShadowResourceBuildMap)validate.Invoke(null, new object[] { false });
            Assert.IsNotNull(map);
            Assert.AreEqual(7, map.bundles.Length);
            validate.Invoke(null, new object[] { false });
            AssetDatabase.SaveAssets();

            foreach (KeyValuePair<string, byte[]> entry in before)
                CollectionAssert.AreEqual(entry.Value, ReadBytes(entry.Key), entry.Key);
        }

        [Test]
        public void SceneContentValidationRejectsScalarPrefixesAndMissingLocalReferences()
        {
            string path = BaselineRoot + "/BusinessScene.unity";
            string yaml = File.ReadAllText(path);
            string dataGuid = AssetDatabase.AssetPathToGUID(BaselineRoot + "/VersionedData.asset");
            string graphGuid = AssetDatabase.AssetPathToGUID(BaselineRoot + "/ManagedGraph.asset");
            string sceneScriptGuid = AssetDatabase.AssetPathToGUID("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M07SceneOnlyComponent.cs");
            Type sourceAssets = typeof(M07Build).Assembly.GetType("AssemblyShadowDemo.Editor.M07SourceAssets", true);
            MethodInfo validate = sourceAssets.GetMethod("ValidateSceneContent", BindingFlags.Static | BindingFlags.NonPublic);
            Assert.IsNotNull(validate);
            Assert.IsTrue((bool)validate.Invoke(null, new object[] { yaml, 707, dataGuid, graphGuid, sceneScriptGuid }));

            string prefixedScalar = yaml.Replace("sceneValue: 707", "sceneValue: 7070");
            Assert.IsFalse((bool)validate.Invoke(null, new object[] { prefixedScalar, 707, dataGuid, graphGuid, sceneScriptGuid }));

            const string interfacePrefix = "serializedInterfaceObject: {fileID: ";
            int interfaceStart = yaml.IndexOf(interfacePrefix, StringComparison.Ordinal);
            int interfaceEnd = yaml.IndexOf('}', interfaceStart + interfacePrefix.Length);
            Assert.GreaterOrEqual(interfaceStart, 0);
            Assert.Greater(interfaceEnd, interfaceStart);
            string missingReference = yaml.Substring(0, interfaceStart) + interfacePrefix + "999999999999" + yaml.Substring(interfaceEnd);
            Assert.IsFalse((bool)validate.Invoke(null, new object[] { missingReference, 707, dataGuid, graphGuid, sceneScriptGuid }));
        }

        private static byte[] ReadBytes(string path)
        {
            Assert.IsTrue(File.Exists(path), "Missing pinned M07 input: " + path);
            return File.ReadAllBytes(path);
        }
    }
}
