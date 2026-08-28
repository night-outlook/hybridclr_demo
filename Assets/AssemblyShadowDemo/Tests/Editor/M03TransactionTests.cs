using System;
using System.IO;
using System.Linq;
using System.Reflection;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M03TransactionTests
    {
        [Test]
        public void CandidateOrderMatchesM02AndProviderFirstClosure()
        {
            CollectionAssert.AreEqual(AssemblyShadowDemo.Editor.M02Build.Candidates,
                AssemblyShadowDemo.Editor.M03Build.ProviderFirstOrder);
            CollectionAssert.AreEqual(new[] {
                "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
                "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"
            }, AssemblyShadowDemo.Editor.M03Build.ProviderFirstOrder);
        }

        [Test]
        public void InitializerFixturesAreExcludedUnlessExplicitlyDefined()
        {
            string[] roots = {
                "Assets/AssemblyShadowDemo/AssemblyA/Contracts/M03ModuleInitializer.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M03ModuleInitializer.cs",
                "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M03ModuleInitializer.cs",
                "Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M03ModuleInitializer.cs",
                "Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M03ModuleInitializer.cs",
            };
            foreach (string path in roots)
            {
                string source = File.ReadAllText(path);
                StringAssert.Contains("ASSEMBLY_SHADOW_M03_INITIALIZERS", source);
                StringAssert.Contains("M03-INIT:", source);
                StringAssert.Contains("ModuleInitializerAttribute", source);
            }
            StringAssert.Contains("ASSEMBLY_SHADOW_M03_INITIALIZER_THROW", File.ReadAllText(roots[2]));
            StringAssert.Contains("ASSEMBLY_SHADOW_M03_P03", File.ReadAllText(roots[0]));
        }

        [Test]
        public void BootstrapUsesStringBoundaryAndNoCandidateTypeTokens()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M03TransactionProbe.cs");
            Assert.IsFalse(source.Contains("using AssemblyA."), "Bootstrap must not reference candidate namespaces.");
            Assert.IsFalse(source.Contains("typeof(AssemblyA."), "Bootstrap must not carry candidate Type tokens.");
            StringAssert.Contains("Assembly.Load", source);
            StringAssert.Contains("GetType(\"AssemblyA.Implementation.Internal.InternalEntry\"", source);
        }

        [Test]
        public void FixtureBuildDefinesOnlyOptIntoInitializers()
        {
            Assert.AreEqual("ASSEMBLY_SHADOW_M03_INITIALIZERS", AssemblyShadowDemo.Editor.M03Build.InitializerDefine);
            Assert.AreEqual("ASSEMBLY_SHADOW_M03_P03", AssemblyShadowDemo.Editor.M03Build.P03InitializerDefine);
            Assert.AreEqual("ASSEMBLY_SHADOW_M03_INITIALIZER_THROW", AssemblyShadowDemo.Editor.M03Build.InitializerThrowDefine);
            Assert.AreEqual("ASSEMBLY_SHADOW_P03", AssemblyShadowDemo.Editor.M03Build.P03Define);
        }

        [Test]
        public void InitializerOutputNamesAreUniqueAndDeterministic()
        {
            string[] paths = Directory.GetFiles("Assets/AssemblyShadowDemo", "M03ModuleInitializer.cs", SearchOption.AllDirectories);
            Assert.AreEqual(5, paths.Length);
            var names = paths.Select(path => File.ReadAllText(path).Split(new[] { "M03-INIT:" }, StringSplitOptions.None)[1].Split('"')[0]).ToArray();
            Assert.AreEqual(5, names.Distinct(StringComparer.Ordinal).Count());
        }

        [Test]
        public void RuntimeEnumsKeepTheNativeAbiIntegers()
        {
            Type errorCode = RuntimeType("AssemblyShadowErrorCode"), state = RuntimeType("AssemblyShadowState"), executionMode = RuntimeType("AssemblyExecutionMode");
            CollectionAssert.AreEqual(new[] {
                "Success", "FeatureDisabled", "InvalidState", "InvalidArgument", "CandidateNotRegistered", "DuplicateAssemblyName",
                "BaselineAssemblyNotFound", "BaselineBuildMismatch", "AssemblyNameMismatch", "BadImage", "UnsupportedAssembly",
                "ClosureMemberMissing", "UnexpectedClosureMember", "ReferenceResolutionFailed", "ReferenceEscapesClosure",
                "BaselineAlreadyUsed", "ResourceAbiMismatch", "RuntimeAbiMismatch", "AlreadyCommitted", "ModuleInitializerFailed", "InternalError"
            }, Enum.GetNames(errorCode));
            CollectionAssert.AreEqual(Enumerable.Range(0, 21).ToArray(), Enum.GetValues(errorCode).Cast<object>().Select(Convert.ToInt32).ToArray());
            CollectionAssert.AreEqual(new[] { "Disabled", "CandidatesRegistered", "Staging", "Staged", "Validated", "Committing", "Committed", "Aborted", "Failed", "FailedAfterCommit" }, Enum.GetNames(state));
            CollectionAssert.AreEqual(Enumerable.Range(0, 10).ToArray(), Enum.GetValues(state).Cast<object>().Select(Convert.ToInt32).ToArray());
            Assert.AreEqual(0, Convert.ToInt32(Enum.Parse(executionMode, "AotBaseline")));
            Assert.AreEqual(1, Convert.ToInt32(Enum.Parse(executionMode, "InterpreterShadow")));
        }

        [Test]
        public void AllNineOperationsReturnErrorCodesAndEditorNeverSimulatesSuccess()
        {
            Type api = RuntimeType("AssemblyShadowRuntime");
            MethodInfo[] methods = api.GetMethods(BindingFlags.Public | BindingFlags.Static);
            Assert.AreEqual(9, methods.Length);
            foreach (MethodInfo method in methods)
            {
                Assert.AreEqual(RuntimeType("AssemblyShadowErrorCode"), method.ReturnType, method.Name);
                object[] args = method.GetParameters().Select(p => p.ParameterType == typeof(int) ? (object)1 : null).ToArray();
                var error = Assert.Throws<TargetInvocationException>(() => method.Invoke(null, args));
                Assert.IsInstanceOf<NotSupportedException>(error.InnerException, method.Name);
            }
            Assert.IsTrue(api.GetMethod("GetState").GetParameters()[0].IsOut);
            Assert.IsTrue(api.GetMethod("GetDiagnosticsJson").GetParameters()[0].IsOut);
            Assert.IsTrue(api.GetMethod("GetAssemblyExecutionMode").GetParameters()[1].IsOut);
        }

        [Test]
        public void ProbeCannotAliasThePrototypeOrTurnAnUnprovenFailureGreen()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M03TransactionProbe.cs");
            Assert.IsFalse(source.Contains("using AssemblyShadowRuntime ="));
            Assert.IsFalse(source.Contains("new AssemblyName("), "Bootstrap acquisitions must remain finite string loads.");
            Assert.AreEqual(2, source.Split(new[] { "Assembly.Load(Internal)" }, StringSplitOptions.None).Length - 1);
            StringAssert.Contains("Assembly.Load(\"mscorlib\")", source);
            StringAssert.Contains("stable.Contains(\"mscorlib\", StringComparer.OrdinalIgnoreCase)", source);
            StringAssert.Contains("Intersect(Candidates, StringComparer.OrdinalIgnoreCase)", source);
            Assert.IsFalse(source.Contains("if (result.result == \"Failed\")"));
            StringAssert.Contains("RunAndWrite(string expectedBaselineBuildId, string expectedRuntimeAbiHash)", source);
            StringAssert.Contains("method.Invoke(Activator.CreateInstance(entry), null)", source);
            StringAssert.Contains("result.stressJoined = stress.StopAndJoin()", source);
            StringAssert.Contains("processId = System.Diagnostics.Process.GetCurrentProcess().Id", source);
            StringAssert.Contains("marker.processId != result.processId", source);
            StringAssert.Contains("ModuleInitializerFailed", source);
            StringAssert.Contains("FailedAfterCommit", source);
            // Exactly one managed enumeration call, explicitly scoped to the rejection mode.
            Assert.AreEqual(1, source.Split(new[] { "AppDomain.CurrentDomain.GetAssemblies()" }, StringSplitOptions.None).Length - 1);
            int mode = source.IndexOf("if (mode == \"T03-11\")", StringComparison.Ordinal);
            int enumeration = source.IndexOf("AppDomain.CurrentDomain.GetAssemblies()", StringComparison.Ordinal);
            Assert.That(enumeration, Is.GreaterThan(mode));
            Assert.That(enumeration - mode, Is.LessThan(400));
        }

        [Test]
        public void RuntimeArtifactDtosRemainCompatibleWithAuthoritativeEditorFields()
        {
            // No reference from the runtime Bootstrap to an Editor assembly is needed.
            var probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M03TransactionProbe", true);
            Assert.IsNotNull(probe);
            VerifyFields(probe.GetNestedType("PatchManifest", BindingFlags.NonPublic), typeof(ShadowPatchManifest));
            VerifyFields(probe.GetNestedType("PatchAssembly", BindingFlags.NonPublic), typeof(ShadowPatchAssembly));
            VerifyFields(probe.GetNestedType("BaselineManifest", BindingFlags.NonPublic), typeof(ShadowBaselineManifest));
            VerifyFields(probe.GetNestedType("FixtureManifest", BindingFlags.NonPublic), typeof(AssemblyShadowDemo.Editor.M03Build.M03FixtureManifest));
            VerifyFields(probe.GetNestedType("Fixture", BindingFlags.NonPublic), typeof(AssemblyShadowDemo.Editor.M03Build.M03Fixture));
        }

        [Test]
        public void EditorValidationReplaysCompilationAndLinkedProof()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs");
            StringAssert.Contains("VerifiedLinkedRuntimeReferences.Verify", source);
            StringAssert.Contains("ShadowReflectionBindingEvidence.ValidateCompiled", source);
            StringAssert.Contains("TargetFrameworkReferenceVerifier.Verify", source);
            StringAssert.Contains("AssemblyReferenceGraph.DetectChangedRoots", source);
            StringAssert.Contains("graph.ReverseClosure(roots)", source);
            StringAssert.Contains("assembly.sha256 == file.sha256", source);
            StringAssert.Contains("assembly.pdbSha256 == file.pdbSha256", source);
            StringAssert.Contains("ValidateFixtures(manifestPath)", source);
            StringAssert.Contains("FileMode.CreateNew", source);
            StringAssert.Contains("M03EditorValidation.ValidateAndWriteReceipt(path)",
                File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M03Build.cs"));
        }

        [Test]
        public void EditorReplayNeverOverwritesExistingEvidence()
        {
            string root = Path.Combine(Path.GetTempPath(), "M03ReplayTest-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            string receipt = Path.Combine(root, "m03-editor-replay.json");
            try
            {
                File.WriteAllText(receipt, "retained-evidence");
                var error = Assert.Catch(() => AssemblyShadowDemo.Editor.M03EditorValidation.ValidateAndWriteReceipt(
                    Path.Combine(root, "missing-fixtures.json"), receipt));
                StringAssert.Contains("receipt already exists", error.Message);
                Assert.AreEqual("retained-evidence", File.ReadAllText(receipt));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void FailedEditorReplayDoesNotCreatePassingReceipt()
        {
            string root = Path.Combine(Path.GetTempPath(), "M03ReplayTest-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            string receipt = Path.Combine(root, "m03-editor-replay.json");
            try
            {
                var error = Assert.Catch(() => AssemblyShadowDemo.Editor.M03EditorValidation.ValidateAndWriteReceipt(
                    Path.Combine(root, "missing-fixtures.json"), receipt));
                StringAssert.Contains("fixture manifest is missing", error.Message);
                Assert.IsFalse(File.Exists(receipt));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void RuntimeExactSetValidationRejectsMissingExtraAndDuplicateMembers()
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M03TransactionProbe", true);
            MethodInfo validate = probe.GetMethod("RequireSet", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(validate);
            string[] expected = { "A", "B" };
            Assert.DoesNotThrow(() => validate.Invoke(null, new object[] { new[] { "B", "A" }, expected, "test" }));
            foreach (string[] invalid in new[] { null, new string[0], new[] { "A" }, new[] { "A", "A" }, new[] { "A", "B", "C" } })
            {
                var error = Assert.Throws<TargetInvocationException>(() => validate.Invoke(null, new object[] { invalid, expected, "test" }));
                Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
            }
        }

        [Test]
        public void ConcurrentLoadRequiresVerifiedMscorlibAndAcceptsIdentityCase()
        {
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M03TransactionProbe", true);
            Type stress = probe.GetNestedType("ThreadStress", BindingFlags.NonPublic);
            Assert.IsNotNull(stress);
            Assert.DoesNotThrow(() => Activator.CreateInstance(stress, new object[] { new[] { "MSCORLIB" }, new[] { "AssemblyA.Implementation.Internal" } }));
            var error = Assert.Throws<TargetInvocationException>(() => Activator.CreateInstance(stress, new object[] { new[] { "Other.Framework" }, new[] { "AssemblyA.Implementation.Internal" } }));
            Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
        }

        [Test]
        public void RuntimeSourcePinsRecomputeTheSameAbiAsTheEditor()
        {
            var pins = new ShadowSourcePins {
                unityVersion = "2022.3.62f2", target = "StandaloneOSX", architecture = "arm64",
                hybridclr = new ShadowRepositoryPin { url = "https://example.invalid/hybridclr", revision = new string('a', 40) },
                il2cppPlus = new ShadowRepositoryPin { url = "https://example.invalid/il2cpp", revision = new string('b', 40) },
                hybridclrUnity = new ShadowRepositoryPin { url = "https://example.invalid/unity", revision = new string('c', 40) },
                demo = new ShadowRepositoryPin { url = "https://example.invalid/demo", revision = new string('d', 40) },
            };
            Type probe = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M03TransactionProbe", true);
            Type mirror = probe.GetNestedType("SourcePins", BindingFlags.NonPublic);
            object runtimePins = UnityEngine.JsonUtility.FromJson(UnityEngine.JsonUtility.ToJson(pins), mirror);
            MethodInfo verify = probe.GetMethod("VerifyPins", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.DoesNotThrow(() => verify.Invoke(null, new[] { runtimePins, pins.RuntimeAbiHash(), pins.unityVersion, pins.target, pins.architecture }));
            var error = Assert.Throws<TargetInvocationException>(() => verify.Invoke(null, new[] { runtimePins, new string('0', 64), pins.unityVersion, pins.target, pins.architecture }));
            Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
        }

        private static void VerifyFields(Type mirror, Type authoritative)
        {
            Assert.IsNotNull(mirror);
            foreach (FieldInfo field in mirror.GetFields(BindingFlags.Public | BindingFlags.Instance))
            {
                FieldInfo expected = authoritative.GetField(field.Name);
                Assert.IsNotNull(expected, authoritative.Name + "." + field.Name);
                if (field.FieldType.IsPrimitive || field.FieldType == typeof(string) || field.FieldType == typeof(string[]))
                    Assert.AreEqual(expected.FieldType, field.FieldType, field.Name);
                else Assert.AreEqual(expected.FieldType.IsArray, field.FieldType.IsArray, field.Name);
            }
        }

        private static Type RuntimeType(string name) { return Assembly.Load("HybridCLR.Runtime").GetType("HybridCLR." + name, true); }
    }
}
