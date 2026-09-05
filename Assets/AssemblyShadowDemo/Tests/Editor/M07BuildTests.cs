using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07BuildTests
    {
        private const string BuildSource = "Assets/AssemblyShadowDemo/Editor/M07Build.cs";
        private const string AssetsSource = "Assets/AssemblyShadowDemo/Editor/M07SourceAssets.cs";
        private const string StructuralSource = "Assets/AssemblyShadowDemo/Editor/M07StructuralResources.cs";
        private const string ReplaySource = "Assets/AssemblyShadowDemo/Editor/M07EditorValidation.cs";
        private const string WorkflowSource = "Tools/AssemblyShadow/Invoke-M07Build.ps1";

        [Test]
        public void CanonicalBundleMapIsExactAndOutsideResources()
        {
            string[] expected = { "additive-scene.bundle", "business-scene.bundle", "mixed-assets.bundle", "nested-prefab.bundle",
                "scriptable-object.bundle", "serialize-reference.bundle", "versioned-prefab.bundle" };
            CollectionAssert.AreEqual(expected, M07Build.BundleNames);
            Type sourceAssets = typeof(M07Build).Assembly.GetType("AssemblyShadowDemo.Editor.M07SourceAssets", true);
            MethodInfo mapMethod = sourceAssets.GetMethod("Map", BindingFlags.Static | BindingFlags.NonPublic);
            var map = (ShadowResourceBuildMap)mapMethod.Invoke(null, new object[] { "Assets/AssemblyShadowDemo/M07Resources/Baseline" });
            AssetBundleBuild[] builds = ShadowResourceBaseline.ValidateMap(map);
            CollectionAssert.AreEqual(expected, builds.Select(build => build.assetBundleName).ToArray());
            Assert.AreEqual(8, builds.SelectMany(build => build.assetNames).Distinct(StringComparer.Ordinal).Count());
            Assert.IsTrue(builds.SelectMany(build => build.assetNames).All(path => path.StartsWith("Assets/AssemblyShadowDemo/M07Resources/Baseline/", StringComparison.Ordinal)));
            Assert.IsFalse(builds.SelectMany(build => build.assetNames).Any(path => ("/" + path + "/").IndexOf("/Resources/", StringComparison.OrdinalIgnoreCase) >= 0));
        }

        [Test]
        public void SourceGeneratorFreezesSerializationInsteadOfRepairingLoadedAssets()
        {
            string source = File.ReadAllText(AssetsSource);
            foreach (string field in new[] { "m07SerializedInt", "m07SerializedString", "m07InlineValue", "m07InlineValues", "m07ObjectReference",
                "m07NestedPayload", "relatedComponent", "serializedInterfaceObject", "persistentEvent", "managedReferenceValue" })
                StringAssert.Contains("\"" + field + "\"", source);
            StringAssert.Contains("PrefabUtility.SaveAsPrefabAsset", source);
            StringAssert.Contains("EditorSceneManager.SaveScene", source);
            StringAssert.Contains("UnityEventTools.AddPersistentListener", source);
            StringAssert.Contains("script.GetClass() == typeof(VersionedPrefabComponent)", source);
            StringAssert.Contains("ReadM07SerializedState() ==", source);
            StringAssert.Contains("graph.SumGraph() == 77", source);
            Assert.IsFalse(File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M07ResourceProbe.cs").Contains("SaveAsPrefabAsset"));
        }

        [Test]
        public void FixtureMatrixSeparatesCodeOnlyAndStructuralChanges()
        {
            string build = File.ReadAllText(BuildSource), structural = File.ReadAllText(StructuralSource);
            foreach (string id in new[] { "P01", "P02", "P03", "P04", "P05-DllOnly", "P14-ClassRename", "P15-SerializeReferenceRename" })
                StringAssert.Contains("\"" + id + "\"", build);
            StringAssert.Contains("fixture.patchId == \"P05\" && !structural.dllOnly", build);
            StringAssert.Contains("ResourceRebuildRequired", build);
            StringAssert.Contains("new[] { M07Build.P05Define }", structural);
            StringAssert.Contains("M02StructuralPatchCompilation.Prepare()", structural);
            StringAssert.Contains("M02StructuralPatchCompilation.Compile()", structural);
            StringAssert.Contains("M02StructuralPatchCompilation.Restore()", structural);
            StringAssert.Contains("ReadPreparedSnapshot", structural);
            StringAssert.Contains("replacementResourceReceiptSha256", structural);
            StringAssert.Contains("ResourceAbiDiffLevel.ResourceRebuildRequired", structural);
        }

        [Test]
        public void PlayerAndFixtureReceiptsCarryNativeAndResourceIdentity()
        {
            Type player = typeof(M07Build.M07PlayerBuildReceipt);
            foreach (string field in new[] { "inputSnapshotHash", "nativeLibraryPath", "nativeLibrarySha256", "nativeMetadataPath",
                "nativeMetadataSha256", "nativeMetadataVersion", "nativeAssemblyIdentities", "nativeGeneratedAssemblyNames",
                "placeholderManifestPath", "placeholderManifestSha256", "resourceBaselinePath", "resourceBuildReceiptPath",
                "resourceBuildReceiptSha256", "resourceAbiHash", "bundleNames" })
                Assert.IsNotNull(player.GetField(field), field);
            Type fixture = typeof(M07Build.M07Fixture);
            foreach (string field in new[] { "baselineResourceAbiHash", "resourceAbiHash", "resourceChangeLevel", "dllOnly",
                "resourceBundlesRequired", "replacementResourcePath", "replacementResourceReceiptPath", "replacementResourceReceiptSha256" })
                Assert.IsNotNull(fixture.GetField(field), field);
        }

        [Test]
        public void EditorAssemblyDeclaresItsBootstrapGenerationDependency()
        {
            string asmdef = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/AssemblyShadowDemo.Editor.asmdef");
            StringAssert.Contains("\"AssemblyShadowDemo.Bootstrap\"", asmdef);
            string bootstrap = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/AssemblyShadowDemo.Bootstrap.asmdef");
            foreach (string candidate in M07Build.Candidates) Assert.IsFalse(bootstrap.Contains("\"" + candidate + "\""), candidate);
        }

        [Test]
        public void BaselineAndPlayerOutputsAreUniqueAndBootstrapOnly()
        {
            string source = File.ReadAllText(BuildSource);
            StringAssert.Contains("!Directory.Exists(baselineRoot)", source);
            StringAssert.Contains("!Directory.Exists(output) && !File.Exists(output)", source);
            StringAssert.Contains("scenes = new[] { BootstrapScene }", source);
            StringAssert.Contains("new EditorBuildSettingsScene(BootstrapScene, true)", source);
            StringAssert.Contains("BuildOptions.CleanBuildCache", source);
            StringAssert.Contains("M02ReflectionBindingValidation.StageConfiguration()", source);
            StringAssert.Contains("BaselineBuild.SetNativeFeature(true)", source);
            StringAssert.Contains("PrebuildCommand.GenerateAll()", source);
        }

        [Test]
        public void StructuralFieldsHaveMutuallyExclusiveDeploymentPolicy()
        {
            string component = File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs");
            StringAssert.Contains("#if ASSEMBLY_SHADOW_M07_P04", component);
            StringAssert.Contains("[NonSerialized] private int m07RuntimeOnlyValue", component);
            StringAssert.Contains("#if ASSEMBLY_SHADOW_P05", component);
            StringAssert.Contains("[SerializeField] private int addedSerializedField", component);
            Assert.Less(component.IndexOf("[NonSerialized] private int m07RuntimeOnlyValue", StringComparison.Ordinal),
                component.IndexOf("[SerializeField] private int addedSerializedField", StringComparison.Ordinal));
        }

        [Test]
        public void IndependentReplayBindsOriginalAndBaselineCopiedResourceBytes()
        {
            string source = File.ReadAllText(ReplaySource);
            StringAssert.Contains("claimedResourceRoot = Path.GetFullPath(claimed.resourceBaselinePath)", source);
            StringAssert.Contains("claimed.resourceBuildReceiptSha256 == ShadowHash.File(baselineResourceReceiptPath)", source);
            StringAssert.Contains("item.name + \":\" + item.sha256", source);
            StringAssert.Contains("original and baseline-copied resource bytes differ", source);
            Assert.IsFalse(source.Contains("claimed.resourceBaselinePath == resourceRoot"));
        }

        [Test]
        public void WorkflowRestoresExactProjectSettingsBytesAcrossFreshEditors()
        {
            string source = File.ReadAllText(WorkflowSource);
            StringAssert.Contains("'M02Validation-' + [guid]::NewGuid().ToString('N')", source);
            foreach (string method in new[] { "M07Build.ValidateCompilerInputs", "M07Build.BuildBaselineResources", "M07Build.BuildPlayerBaseline",
                "M07Build.BuildFeatureDisabledPlayer", "M07StructuralResources.Prepare", "M07StructuralResources.Compile",
                "M07StructuralResources.Restore", "M07StructuralResources.FinalizeFixtures" })
                StringAssert.Contains(method, source);
            StringAssert.Contains("p05-project-settings.original", source);
            StringAssert.Contains("p05-settings-restored.json", source);
            StringAssert.Contains("[IO.FileMode]::CreateNew", source);
            StringAssert.Contains("Test-UnityProjectRunning", source);
            StringAssert.Contains("m07-build.lock", source);
        }
    }
}
