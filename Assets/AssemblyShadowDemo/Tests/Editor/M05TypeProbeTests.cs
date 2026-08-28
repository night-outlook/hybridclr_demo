using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    /// <summary>Static/editor contract checks for the M05 runtime probe.</summary>
    public sealed class M05TypeProbeTests
    {
        private const string ProbeSource = "Assets/AssemblyShadowDemo/Bootstrap/M05TypeProbe.cs";

        [Test]
        public void PublicDtoSchemaIsPreservedAndComplete()
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M05TypeProbe", true);
            foreach (string name in new[] { "Result", "FixtureManifest", "PlayerBuildReceipt", "Fixture", "TypeInventory", "TypeDefinition", "NegativeRejectedFixture", "TypeProof", "MethodWitness" })
            {
                Type nested = probe.GetNestedType(name, BindingFlags.Public);
                Assert.IsNotNull(nested, name);
                Assert.IsNotNull(nested.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + " must be preserved.");
                foreach (FieldInfo field in nested.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + "." + field.Name + " must be preserved.");
            }
            AssertFields(probe, "TypeDefinition", new[] { "fullName", "namespaceName", "name", "nestingPath", "genericArity", "kind", "isExported" });
            AssertFields(probe, "TypeProof", new[] { "schemaVersion", "milestone", "policy", "compileSnapshotHash", "linkedPlayerReceiptHash", "nativeLibrarySha256", "buildGuid", "developmentBuild", "assemblies", "moduleMethods" });
            AssertFields(probe, "MethodWitness", new[] { "declaringType", "name", "signature", "hasBody", "implementationFlags", "instructions" });
            AssertFields(probe, "PlayerBuildReceipt", new[] { "typeProofPath", "typeProofSha256", "nativeMetadataPath", "nativeMetadataSha256", "nativeMetadataVersion", "nativeAssemblyIdentities", "nativeGeneratedAssemblyNames" });
            Assert.AreEqual(typeof(int), probe.GetNestedType("TypeDefinition", BindingFlags.Public).GetField("genericArity").FieldType);
        }

        [Test]
        public void ModesAndCliLabelsAreExactAndFeatureOffIsSeparate()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string mode in new[] {
                "T05-01-P01", "T05-01-P03", "T05-02-P01", "T05-02-P03", "T05-03-P01", "T05-03-P03",
                "T05-04-EarlyType", "T05-05-P01", "T05-05-P03", "T05-06-P01", "T05-07-P03", "T05-08-P01",
                "T05-08-P03", "T05-09-LayoutMismatch", "T05-10-P01", "T05-10-P03", "T05-11-FeatureOff",
                "T05-12-BenchmarkOn", "T05-13-BenchmarkOff" })
                StringAssert.Contains("\"" + mode + "\"", source);
            foreach (string label in new[] { "-shadowM05Mode", "-shadowM05Fixtures", "-shadowM05PlayerReceipt", "-shadowM05Result" })
                StringAssert.Contains("\"" + label + "\"", source);
            StringAssert.Contains("GetTypeResolutionInfo", source);
            StringAssert.Contains("nativeMetadataVersion == 31", source);
            StringAssert.Contains("active-type-world:1", source);
            Assert.IsFalse(source.Contains("ModuleVersionId"));
            Assert.IsFalse(source.Contains("Assembly.LoadFrom"));
            Assert.IsFalse(source.Contains("Assembly.LoadFile"));
        }

        [Test]
        public void PrivateJsonRootsArePreservedAndFixtureBindsPatchManifest()
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M05TypeProbe", true);
            foreach (string name in new[] { "PatchManifest", "PatchAssembly", "BaselineManifest", "BaselineAssembly", "SnapshotReceipt", "SnapshotFile" })
            {
                Type nested = probe.GetNestedType(name, BindingFlags.NonPublic);
                Assert.IsNotNull(nested, name);
                Assert.IsNotNull(nested.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault());
                foreach (FieldInfo field in nested.GetFields(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic))
                    if (!field.IsNotSerialized) Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + "." + field.Name);
            }
            Type fixture = probe.GetNestedType("Fixture", BindingFlags.Public);
            Assert.IsNotNull(fixture.GetField("patch", BindingFlags.NonPublic | BindingFlags.Instance));
            StringAssert.Contains("FromJson<PatchManifest>", File.ReadAllText(ProbeSource));
        }

        [Test]
        public void BaselineWriterResourceHashRoundTripsThroughRuntimeGuard()
        {
            // Use the production writer DTO and hasher: file hashes and resource
            // semantic hashes deliberately have different transport formats.
            ShadowBaselineManifest baseline = BaselineForRuntimeGuard();
            object actual = ReadRuntimeBaseline(baseline, RuntimeFixture(baseline));
            Assert.AreEqual(baseline.resourceAbiHash, actual.GetType().GetField("resourceAbiHash").GetValue(actual));
            Assert.IsTrue((bool)InvokePrivate("IsHash", baseline.bootstrapAbiHash));
            Assert.IsFalse((bool)InvokePrivate("IsHash", baseline.resourceAbiHash), "Raw byte hashes must not start accepting tagged semantic hashes.");
        }

        [Test]
        public void BaselineRuntimeGuardRejectsHashDomainAndIdentityMutations()
        {
            ShadowBaselineManifest good = BaselineForRuntimeGuard();
            object fixture = RuntimeFixture(good);
            string digest = good.resourceAbiHash.Substring("sha256:".Length);
            foreach (string invalid in new[] { null, "", digest, "SHA256:" + digest, "sha256:" + digest.ToUpperInvariant(),
                "sha512:" + digest, "sha256:" + digest.Substring(1), "sha256:" + digest + "0", "sha256:" + new string('g', 64), " sha256:" + digest })
            {
                ShadowBaselineManifest changed = BaselineForRuntimeGuard();
                changed.resourceAbiHash = invalid;
                AssertRuntimeBaselineRejected(changed, fixture);
            }
            foreach (string fieldName in new[] { "schemaVersion", "semanticHashSchema", "baselineBuildId", "runtimeAbiHash", "unityVersion", "target", "architecture", "playerInputSnapshotHash", "bootstrapAbiHash" })
            {
                ShadowBaselineManifest changed = BaselineForRuntimeGuard();
                FieldInfo field = typeof(ShadowBaselineManifest).GetField(fieldName);
                field.SetValue(changed, field.FieldType == typeof(int) ? (object)99 : "tampered");
                AssertRuntimeBaselineRejected(changed, fixture);
            }
            ShadowBaselineManifest taggedBootstrap = BaselineForRuntimeGuard();
            taggedBootstrap.bootstrapAbiHash = taggedBootstrap.resourceAbiHash;
            AssertRuntimeBaselineRejected(taggedBootstrap, fixture);
            foreach (string[] candidates in new[] { null, good.shadowCandidates.Reverse().ToArray(), good.shadowCandidates.Skip(1).ToArray(), good.shadowCandidates.Concat(new[] { good.shadowCandidates[0] }).ToArray() })
            {
                ShadowBaselineManifest changed = BaselineForRuntimeGuard();
                changed.shadowCandidates = candidates;
                AssertRuntimeBaselineRejected(changed, fixture);
            }
        }

        [Test]
        public void BenchmarkUsesFixedLiteralTypeGetTypeWithoutWitnessInvocationInMeasuredLoop()
        {
            string source = File.ReadAllText(ProbeSource);
            StringAssert.Contains("const int warmups = 1000, iterations = 100000", source);
            StringAssert.Contains("AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal", source);
            StringAssert.Contains("for (int i = 0; i < iterations; ++i)", source);
            int begin = source.IndexOf("private static void RunBenchmark", StringComparison.Ordinal);
            int end = source.IndexOf("private static Type[] InvokeWitnessTypes", begin, StringComparison.Ordinal);
            Assert.Greater(begin, 0);
            Assert.Greater(end, begin);
            string benchmark = source.Substring(begin, end - begin);
            Assert.IsFalse(benchmark.Contains("InvokeWitnessTypes"));
            Assert.IsFalse(benchmark.Contains("AssemblyShadowRuntime."));
            StringAssert.Contains("ReferenceEquals(first, last)", benchmark);
        }

        [Test]
        public void WitnessesRemainGuardedAndPrefabLayoutChangeIsTheOnlyExistingSourceEdit()
        {
            string[] witnesses = {
                "Assets/AssemblyShadowDemo/AssemblyA/Contracts/M05TypeWitness.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M05TypeWitness.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M05TypeWitness.cs",
                "Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M05TypeWitness.cs",
                "Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M05TypeWitness.cs",
            };
            foreach (string path in witnesses)
            {
                string source = File.ReadAllText(path);
                StringAssert.Contains("Type.GetType", source);
                Assert.IsFalse(source.Contains("AssemblyVersion"));
                Assert.IsFalse(source.Contains("M05TypeProbe"));
            }
            StringAssert.Contains("#if ASSEMBLY_SHADOW_M05", File.ReadAllText(witnesses[2]));
            for (int i = 0; i < witnesses.Length; ++i)
                if (i != 2) StringAssert.Contains("ASSEMBLY_SHADOW_M05_P03", File.ReadAllText(witnesses[i]));
            StringAssert.Contains("partial", File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs"));
        }

        [Test]
        public void ArtifactPathsRejectEscapesAndPrefixSiblings()
        {
            string root = Path.Combine(Path.GetTempPath(), "m05-path-root");
            Assert.AreEqual(Path.Combine(root, "Assemblies", "Internal.dll"), InvokePrivate("ConfinedChild", root, "Assemblies/Internal.dll"));
            AssertRejected("ConfinedChild", root, "../Internal.dll");
            AssertRejected("ConfinedChild", root, root + "-sibling/Internal.dll");
            AssertRejected("ConfinedChild", root, "");
        }

        [Test]
        public void ActualByteAndMetadataHeaderChecksRejectTampering()
        {
            string root = Path.Combine(Path.GetTempPath(), "m05-runtime-integrity-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            try
            {
                string path = Path.Combine(root, "global-metadata.dat");
                byte[] good = { 0xaf, 0x1b, 0xb1, 0xfa, 31, 0, 0, 0 };
                File.WriteAllBytes(path, good);
                string hash = (string)InvokePrivate("Hash", good);
                InvokePrivate("ValidateByteFile", path, hash);
                InvokePrivate("ValidateMetadataHeader", path);
                File.WriteAllBytes(path, new byte[] { 0xaf, 0x1b, 0xb1, 0xfa, 30, 0, 0, 0 });
                AssertRejected("ValidateByteFile", path, hash);
                AssertRejected("ValidateMetadataHeader", path);
                File.WriteAllBytes(path, new byte[] { 0xaf, 0x1b });
                AssertRejected("ValidateMetadataHeader", path);
                AssertRejected("ValidateByteFile", path, new string('A', 64));
                AssertRejected("ValidateByteFile", Path.Combine(root, "missing.pdb"), hash);
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void UserAndGeneratedCompilerDefinesAreBoundSeparately()
        {
            string hash = new string('a', 64), control = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_" + hash;
            string[] requested = { "Z_FIXTURE", "A_FIXTURE" };
            InvokePrivate("ValidateDefines", new[] { "A_FIXTURE", control, "Z_FIXTURE" }.OrderBy(value => value, StringComparer.Ordinal).ToArray(), requested, hash);
            AssertRejected("ValidateDefines", new[] { "A_FIXTURE", "Z_FIXTURE" }, requested, hash);
            AssertRejected("ValidateDefines", new[] { "A_FIXTURE", control, "EXTRA", "Z_FIXTURE" }, requested, hash);
            AssertRejected("ValidateDefines", new[] { "A_FIXTURE", control, "Z_FIXTURE" }, requested, new string('b', 64));
            AssertRejected("ValidateDefines", new[] { control }, new[] { control }, hash);
        }

        [Test]
        public void RawTypeAdmissionControlRequiresActualCapturedBytesAndUniqueHash()
        {
            const string prefix = "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_";
            string root = Path.Combine(Path.GetTempPath(), "m05-raw-admission-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path.Combine(root, "RawTypeAdmissions"));
            try
            {
                string path = Path.Combine(root, "RawTypeAdmissions/configuration.json");
                byte[] bytes = System.Text.Encoding.UTF8.GetBytes("{\"schemaVersion\":1}");
                File.WriteAllBytes(path, bytes);
                string hash = (string)InvokePrivate("Hash", bytes), control = prefix + hash;
                Assert.AreEqual(hash, InvokePrivate("ValidateRawAdmission", root, new[] { control }));
                AssertRejected("ValidateRawAdmission", root, new[] { control, control });
                AssertRejected("ValidateRawAdmission", root, new[] { prefix + new string('A', 64) });
                File.WriteAllText(path, "tampered");
                AssertRejected("ValidateRawAdmission", root, new[] { control });
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void RuntimeProofUsesActualMembersArraysCastsAndAllocationOutcome()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string token in new[] { "type-resolution-valid-null-json", "type-resolution-state-unchanged", "allocation-no-object", "appdomain-identity-", "contracts-consumer-interface-dispatch",
                "GetMethod(\"Echo\"", "GetField(\"Field\"", "GetProperty(\"Property\"", "GetEvent(\"Changed\"", "GetParameters()", "GetM05CompositeArrays", "Type.GetTypeFromHandle", "allocated == null" })
                StringAssert.Contains(token, source);
            foreach (string method in new[] { "GetTypes", "GetDefinedTypes", "GetExportedTypes", "GetModuleTypes", "GetModuleType" })
                StringAssert.Contains("M05BoundTypeQueries." + method + "(name)", source);
        }

        private static ShadowBaselineManifest BaselineForRuntimeGuard()
        {
            return new ShadowBaselineManifest {
                baselineBuildId = "M05-Baseline-GuardRegression", runtimeAbiHash = new string('a', 64),
                unityVersion = "2022.3.62f2", target = "StandaloneOSX", architecture = "arm64",
                playerInputSnapshotHash = new string('b', 64), bootstrapAbiHash = new string('c', 64),
                resourceAbiHash = ResourceAbiHasher.Compute(new ResourceAbiDescriptor()),
                shadowCandidates = M05Build.ProviderFirstOrder.OrderBy(name => name, StringComparer.Ordinal).ToArray(),
            };
        }

        private static object RuntimeFixture(ShadowBaselineManifest baseline)
        {
            var fixture = new M05Build.M05FixtureManifest {
                baselineBuildId = baseline.baselineBuildId, runtimeAbiHash = baseline.runtimeAbiHash,
                unityVersion = baseline.unityVersion, target = baseline.target, architecture = baseline.architecture,
                baselineInputSnapshotHash = baseline.playerInputSnapshotHash,
            };
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M05TypeProbe", true);
            return JsonUtility.FromJson(JsonUtility.ToJson(fixture), probe.GetNestedType("FixtureManifest", BindingFlags.Public));
        }

        private static object ReadRuntimeBaseline(ShadowBaselineManifest baseline, object fixture)
        {
            return InvokePrivate("ReadBaselineManifest", JsonUtility.ToJson(baseline), fixture, "M05-Baseline-GuardRegression", new string('a', 64));
        }

        private static void AssertRuntimeBaselineRejected(ShadowBaselineManifest baseline, object fixture)
        {
            TargetInvocationException error = Assert.Throws<TargetInvocationException>(() => ReadRuntimeBaseline(baseline, fixture));
            Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
        }

        private static object InvokePrivate(string name, params object[] arguments)
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M05TypeProbe", true);
            MethodInfo method = probe.GetMethod(name, BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(method, name);
            return method.Invoke(null, arguments);
        }

        private static void AssertRejected(string name, params object[] arguments)
        {
            TargetInvocationException error = Assert.Throws<TargetInvocationException>(() => InvokePrivate(name, arguments));
            Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
        }

        private static void AssertFields(Type probe, string typeName, string[] names)
        {
            Type type = probe.GetNestedType(typeName, BindingFlags.Public);
            foreach (string name in names)
            {
                FieldInfo field = type.GetField(name, BindingFlags.Public | BindingFlags.Instance);
                Assert.IsNotNull(field, typeName + "." + name);
                Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), typeName + "." + name);
            }
        }
    }
}
