using System;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    /// <summary>Editor-only contract tests; runtime acceptance remains IL2CPP Player evidence.</summary>
    public sealed class M04ReferenceProbeTests
    {
        [Test]
        public void RuntimeDtoNamesAndRequiredFieldsArePublicAndPreserved()
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M04ReferenceProbe", true);
            foreach (string name in new[] { "Result", "FixtureManifest", "PlayerBuildReceipt", "Fixture", "AssemblyIdentity", "ReferenceIdentity", "NativeAssemblyIdentity" })
            {
                Type nested = probe.GetNestedType(name, BindingFlags.Public);
                Assert.IsNotNull(nested, name);
                Assert.IsNotNull(nested.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + " must be preserved.");
                foreach (FieldInfo field in nested.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + "." + field.Name + " must be preserved.");
            }
            AssertFields(probe, "AssemblyIdentity", new[] { "name", "fullName", "version", "culture", "publicKeyToken", "mvid", "path", "sha256", "referenceIdentities" });
            AssertFields(probe, "ReferenceIdentity", new[] { "referenceIndex", "name", "fullName", "version", "culture", "publicKeyToken" });
            AssertFields(probe, "PlayerBuildReceipt", new[] { "schemaVersion", "milestone", "baselineBuildId", "runtimeAbiHash", "buildGuid", "assemblyIdentities", "nativeMetadataPath", "nativeMetadataSha256", "nativeMetadataVersion", "nativeAssemblyIdentities", "nativeGeneratedAssemblyNames" });
            AssertFields(probe, "NativeAssemblyIdentity", new[] { "assemblyIndex", "imageIndex", "token", "imageName", "name", "fullName", "version", "culture", "publicKeyToken" });
            AssertFields(probe, "FixtureManifest", new[] { "schemaVersion", "milestone", "baselineBuildId", "runtimeAbiHash", "candidateNames", "fixtures" });
            Assert.AreEqual(typeof(int), probe.GetNestedType("ReferenceIdentity", BindingFlags.Public).GetField("referenceIndex").FieldType);
            Assert.AreEqual(typeof(uint), probe.GetNestedType("NativeAssemblyIdentity", BindingFlags.Public).GetField("token").FieldType);
        }

        [Test]
        public void RequiredModesAreExplicitAndDoNotAliasM03()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M04ReferenceProbe.cs");
            foreach (string mode in new[] { "T04-01", "T04-02", "T04-03", "T04-04", "T04-05", "T04-06", "T04-07", "T04-08", "T04-09-BenchmarkOn", "T04-10-BenchmarkOff" })
                StringAssert.Contains("\"" + mode + "\"", source);
            StringAssert.Contains("AssemblyShadowRuntime.ConfigureCandidates", source);
            StringAssert.Contains("AssemblyShadowRuntime.BeginTransaction", source);
            StringAssert.Contains("AssemblyShadowRuntime.StageAssembly", source);
            StringAssert.Contains("AssemblyShadowRuntime.ValidateTransaction", source);
            StringAssert.Contains("AssemblyShadowRuntime.CommitTransaction", source);
            StringAssert.Contains("AssemblyShadowRuntime.AbortTransaction", source);
            StringAssert.Contains("AssemblyShadowRuntime.GetState", source);
            StringAssert.Contains("AssemblyShadowRuntime.GetAssemblyExecutionMode", source);
            StringAssert.Contains("AssemblyShadowRuntime.GetDiagnosticsJson", source);
            Assert.IsFalse(source.Contains("M03TransactionProbe.RunAndWrite"));
        }

        [Test]
        public void CandidateBusinessWitnessesArePatchOnlyAndDoNotChangeBaselineSources()
        {
            string[] paths = {
                "Assets/AssemblyShadowDemo/AssemblyA/Contracts/M04AssemblyProbe.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M04AssemblyProbe.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M04AssemblyProbe.cs",
                "Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M04AssemblyProbe.cs",
                "Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M04AssemblyProbe.cs",
            };
            foreach (string path in paths)
            {
                string source = File.ReadAllText(path);
                StringAssert.Contains("GetExecutingAssemblyObject", source);
                StringAssert.Contains("Assembly.GetExecutingAssembly()", source);
                Assert.IsFalse(source.Contains("AssemblyVersion"));
                Assert.IsFalse(source.Contains("M04ReferenceProbe"));
            }
            StringAssert.Contains("ASSEMBLY_SHADOW_M04_P03", File.ReadAllText(paths[0]));
            StringAssert.Contains("ASSEMBLY_SHADOW_M04", File.ReadAllText(paths[2]));
            foreach (string path in new[] {
                "Assets/AssemblyShadowDemo/AssemblyA/Contracts/AssemblyAContractVersion.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/VersionedComponentBase.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/InternalEntry.cs",
                "Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/ContractsConsumer.cs",
                "Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/DerivedExternalComponent.cs",
            }) StringAssert.Contains("partial", File.ReadAllText(path));
        }

        [Test]
        public void StartupDoesNotAcquireCandidateHandlesBeforeCommit()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M04ReferenceProbe.cs");
            int commit = source.IndexOf("AssemblyShadowRuntime.CommitTransaction", StringComparison.Ordinal);
            Assert.Greater(commit, 0);
            int firstLoad = source.IndexOf("Assembly.Load", StringComparison.Ordinal);
            Assert.Greater(firstLoad, commit, "Successful startup must not acquire candidate handles before commit.");
            Assert.IsFalse(source.Contains("static readonly Assembly"));
        }

        [Test]
        public void NativeMetadataReceiptIsByteAndPlayerPathBound()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M04ReferenceProbe.cs");
            StringAssert.Contains("ValidateNativeMetadataReceipt", source);
            StringAssert.Contains("nativeMetadataVersion == 31", source);
            StringAssert.Contains("HashFile(metadataPath)", source);
            StringAssert.Contains("Directory.GetFiles(Application.dataPath", source);
            StringAssert.Contains("SearchOption.AllDirectories", source);
            StringAssert.Contains("nativeAssemblyIdentities.Length > 0", source);
            StringAssert.Contains("nativeGeneratedAssemblyNames.Length > 0", source);
            Assert.IsFalse(source.Contains("ModuleVersionId"));
            Assert.IsFalse(source.Contains("Resources/Data/il2cpp_data/Metadata"));
        }

        private static void AssertFields(Type probe, string typeName, string[] required)
        {
            Type type = probe.GetNestedType(typeName, BindingFlags.Public);
            foreach (string field in required)
            {
                FieldInfo info = type.GetField(field, BindingFlags.Public | BindingFlags.Instance);
                Assert.IsNotNull(info, typeName + "." + field);
                Assert.IsNotNull(info.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), typeName + "." + field + " must be preserved.");
            }
        }
    }
}
