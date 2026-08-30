using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using HybridCLR;
using AssemblyShadowDemo;
using NUnit.Framework;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06ExecutionProbeTests
    {
        private const string ProbeSource = "Assets/AssemblyShadowDemo/Bootstrap/M06ExecutionProbe.cs";
        private const string InputsSource = "Assets/AssemblyShadowDemo/Bootstrap/M06ExecutionInputs.cs";
        private const string RunnerSource = "Assets/AssemblyShadowDemo/Bootstrap/M06BootstrapRunner.cs";

        [Test]
        public void M06ModesAndCliLabelsAreExact()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string mode in new[] {
                "T06-01-New-P01", "T06-01-New-P02", "T06-01-New-P03", "T06-02-Statics-P01", "T06-02-Statics-P02", "T06-02-Statics-P03",
                "T06-03-P01", "T06-04-P02", "T06-05-P03", "T06-06-Delegates-P01", "T06-06-Delegates-P02", "T06-06-Delegates-P03",
                "T06-07-Generics-P01", "T06-07-Generics-P02", "T06-07-Generics-P03", "T06-08-Async-P01", "T06-08-Async-P02", "T06-08-Async-P03",
                "T06-09-InitializerFailure", "T06-09-BaselineRecovery", "T06-10-Warmup-P01", "T06-10-Warmup-P02", "T06-10-Warmup-P03",
                "T06-11-FeatureOff", "T06-12-NoWarmup-P01", "T06-12-NoWarmup-P02", "T06-12-NoWarmup-P03", "T06-13-ReleaseNoPdb" })
                StringAssert.Contains("\"" + mode + "\"", source);
            foreach (string argument in new[] { "-shadowM06Mode", "-shadowM06Fixtures", "-shadowM06PlayerReceipt", "-shadowM06Result", "-shadowM06FailedResult" })
                StringAssert.Contains("\"" + argument + "\"", source + File.ReadAllText(InputsSource) + File.ReadAllText(RunnerSource) + File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/M06ExecutionEvidence.cs"));
            var modes = (string[])typeof(M06ExecutionProbe).GetField("Modes", BindingFlags.NonPublic | BindingFlags.Static).GetValue(null);
            Assert.AreEqual(28, modes.Length);
            Assert.AreEqual(28, modes.Distinct(StringComparer.Ordinal).Count());
            foreach (string mode in modes) Assert.AreEqual(true, Invoke("IsKnownMode", mode));
            Assert.AreEqual(false, Invoke("IsKnownMode", "T06-Unknown"));
        }

        [Test]
        public void ResultAndInputDtosPreserveNumericCodesAndM06ProofBindings()
        {
            Type probe = typeof(M06ExecutionProbe);
            foreach (string name in new[] { "Result", "FixtureManifest", "Fixture", "PlayerBuildReceipt", "SupplementaryMetadataInput", "TypeProof", "ExecutionProof", "EnumValue", "SchemaType", "SchemaField", "ExecutionImage", "ExecutionMethod", "ExecutionSignatureType", "ExceptionHandler", "SequencePoint", "Check", "TransactionSnapshot", "ExecutionSnapshot", "ExecutionObservation", "MethodObservation", "ModuleObservation", "WarmupObservation", "TimingObservation", "SupplementaryMetadataObservation", "GenerationProof", "GenerationPlan", "GenerationPlanProof", "GenerationImage", "GenerationOutput", "AotInputProof", "CompilerModeProof", "LinkedPlayerReceipt", "ExecutionPolicyProof", "StartupFile", "StartupScript", "PreloadedAsset" })
            {
                Type nested = probe.GetNestedType(name, BindingFlags.Public);
                Assert.IsNotNull(nested, name);
                Assert.IsNotNull(nested.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name);
                foreach (FieldInfo field in nested.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), name + "." + field.Name);
            }
            Type result = probe.GetNestedType("Result", BindingFlags.Public);
            foreach (string field in new[] { "configureCode", "beginCode", "validateCode", "commitCode", "abortCode", "stateCode", "executionModeCode", "diagnosticsCode", "executionDiagnosticsCode", "typeResolutionCode" })
                Assert.AreEqual(typeof(int), result.GetField(field).FieldType, field);
            Type receipt = probe.GetNestedType("PlayerBuildReceipt", BindingFlags.Public);
            Assert.AreEqual(typeof(int), receipt.GetField("nativeMetadataVersion").FieldType);
            Assert.AreEqual(typeof(int), receipt.GetField("buildOptions").FieldType);
            Assert.AreEqual(typeof(bool), receipt.GetField("developmentBuild").FieldType);
            Assert.IsNotNull(receipt.GetField("supplementaryMetadataInputs"));
            Assert.IsNotNull(probe.GetNestedType("Fixture", BindingFlags.Public).GetField("requiredAotMetadataNames"));
        }

        [Test]
        public void InputAndRunnerKeepStrictPlayerAndCoroutineBoundaries()
        {
            string input = File.ReadAllText(InputsSource), probe = File.ReadAllText(ProbeSource), runner = File.ReadAllText(RunnerSource);
            StringAssert.Contains("nativeMetadataVersion == 31", input);
            StringAssert.Contains("FAB11BAF", input);
            StringAssert.Contains("global-metadata.dat", input);
            StringAssert.Contains("Directory.GetFiles(Application.dataPath", input);
            StringAssert.Contains("PatchManifestEnvelope", input);
            StringAssert.Contains("ConfinedPatchPath", input);
            StringAssert.Contains("GetExecutionDiagnosticsJson", probe);
            StringAssert.Contains("while (!task.IsCompleted) yield return null", probe);
            int begin = probe.IndexOf("BeginTransaction", StringComparison.Ordinal), supplementary = probe.IndexOf("RunSupplementaryMetadata(result, input, fixture)", begin, StringComparison.Ordinal), stage = probe.IndexOf("StageAssembly", begin, StringComparison.Ordinal);
            Assert.Greater(begin, 0);
            Assert.Less(supplementary, stage);
            StringAssert.Contains("shadowTransformationBefore", probe);
            StringAssert.Contains("RunAndWriteCoroutine", runner);
            StringAssert.Contains("DefaultExecutionOrder(-32000)", runner);
            Assert.IsFalse(probe.Contains("ModuleVersionId"));
            Assert.IsFalse(probe.Contains("Assembly.LoadFrom"));
            Assert.IsFalse(probe.Contains("Assembly.LoadFile"));
        }

        [Test]
        public void NativeCountersRemainUnsignedAndUncalledCodesRemainSentinel()
        {
            Type probe = typeof(M06ExecutionProbe);
            Type timing = probe.GetNestedType("TimingObservation", BindingFlags.Public);
            Type warmup = probe.GetNestedType("WarmupObservation", BindingFlags.Public);
            foreach (string field in new[] { "transformationsBefore", "transformationsAfter", "shadowTransformationsBefore", "shadowTransformationsAfter" })
                Assert.AreEqual(typeof(ulong), timing.GetField(field).FieldType, field);
            Assert.AreEqual(typeof(ulong), warmup.GetField("transformationBefore").FieldType);
            Assert.AreEqual(typeof(ulong), warmup.GetField("transformationAfter").FieldType);
            string source = File.ReadAllText(ProbeSource);
            StringAssert.Contains("configureCode = -1", source);
            StringAssert.Contains("typeResolutionCode = -1", source);
        }

        [Test]
        public void M06InputValidationPrecedesEveryShadowOperation()
        {
            string source = File.ReadAllText(ProbeSource);
            int read = source.IndexOf("ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash)", StringComparison.Ordinal);
            int configure = source.IndexOf("ConfigureCandidates", read, StringComparison.Ordinal);
            Assert.Greater(read, 0);
            Assert.Greater(configure, read);
            Assert.IsTrue(source.Substring(0, configure).Contains("BindResult(result, input)"));
        }

        [Test]
        public void WitnessDispatchUsesFiniteBaselineKnownTypes()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string name in new[] { "AssemblyA.Contracts.M06ExecutionWitness", "AssemblyA.Implementation.Extensibility.M06ExecutionWitness", "AssemblyA.Implementation.Internal.M06ExecutionWitness", "AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness", "AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness" })
                StringAssert.Contains(name, source);
            Assert.IsFalse(source.Contains("Type.GetType(typeName"));
            Assert.IsFalse(source.Contains("Assembly.Load(assemblyName"));
        }

        private const string CompilerJson = "{\"schemaVersion\":1,\"kind\":\"CompilePlayerScriptsMode\",\"developmentBuild\":false,\"compilerOptions\":0,\"unityVersion\":\"2022.3.62f2\",\"target\":\"StandaloneOSX\",\"architecture\":\"arm64\",\"snapshotHash\":\"hash\",\"snapshotReceiptSha256\":\"hash\",\"extraScriptingDefines\":[]}";

        [Test] public void StrictProofReaderRetainsExplicitFalseAndZero()
        { ValidateShape(CompilerJson, typeof(M06ExecutionProbe.CompilerModeProof)); }

        [TestCase("\"developmentBuild\":false,", "")]
        [TestCase("\"compilerOptions\":0,", "")]
        [TestCase("\"developmentBuild\":false", "\"developmentBuild\":0")]
        [TestCase("\"compilerOptions\":0", "\"compilerOptions\":false")]
        [TestCase("\"compilerOptions\":0", "\"compilerOptions\":0.0")]
        [TestCase("\"compilerOptions\":0", "\"compilerOptions\":2147483648")]
        [TestCase("\"compilerOptions\":0", "\"compilerOptions\":null")]
        [TestCase("\"compilerOptions\":0", "\"compilerOptions\":00")]
        [TestCase("\"schemaVersion\":1", "\"schemaVersion\":1,\"schemaVersion\":1")]
        [TestCase("\"schemaVersion\":1", "\"schemaVersion\":1,\"waiver\":true")]
        public void StrictProofReaderRejectsDefaultsCoercionsDuplicatesAndUnknownFields(string original, string replacement)
        { Assert.Throws<InvalidOperationException>(() => ValidateShape(CompilerJson.Replace(original, replacement), typeof(M06ExecutionProbe.CompilerModeProof))); }

        [Test] public void BeforeCommitChecksUseNativeEvidenceWithoutCallingWitnesses()
        {
            var execution = new AssemblyShadowExecutionDiagnostics();
            var assembly = new AssemblyShadowDiagnosticAssembly();
            var result = new M06ExecutionProbe.Result {
                executionSnapshots = new List<M06ExecutionProbe.ExecutionSnapshot> { new M06ExecutionProbe.ExecutionSnapshot { diagnostics = execution } },
                transactionSnapshots = new List<M06ExecutionProbe.TransactionSnapshot> { new M06ExecutionProbe.TransactionSnapshot { diagnostics = new AssemblyShadowDiagnostics { assemblies = new[] { assembly } } } }
            };
            Invoke("RequireNoEarlyInitializers", result);
            execution.shadowClassCctorStarted = 1;
            Assert.Throws<InvalidOperationException>(() => Invoke("RequireNoEarlyInitializers", result));
            execution.shadowClassCctorStarted = 0; assembly.moduleInitializerAttempted = true;
            Assert.Throws<InvalidOperationException>(() => Invoke("RequireNoEarlyInitializers", result));
            assembly.moduleInitializerAttempted = false; assembly.published = true;
            Assert.Throws<InvalidOperationException>(() => Invoke("RequireNoEarlyInitializers", result));
        }

        [Test] public void TimingRetainsDistinctActualTotalAndShadowCounters()
        {
            var result = new M06ExecutionProbe.Result { timings = new List<M06ExecutionProbe.TimingObservation>() };
            Invoke("AddTiming", result, "stage", 10L, 31L, 100UL, 119UL, 5UL, 7UL);
            var row = result.timings.Single();
            Assert.AreEqual(21L, row.elapsedTicks); Assert.AreEqual(100UL, row.transformationsBefore); Assert.AreEqual(119UL, row.transformationsAfter);
            Assert.AreEqual(5UL, row.shadowTransformationsBefore); Assert.AreEqual(7UL, row.shadowTransformationsAfter);
        }

        [TestCase("new")]
        [TestCase("dispatch")]
        [TestCase("delegates")]
        [TestCase("generics")]
        public void RuntimeAssertionsAcceptActualBaselineBodiesAndRejectChangedResults(string phase)
        {
            string[] names = (string[])typeof(M06ExecutionProbe).GetField("Candidates", BindingFlags.NonPublic | BindingFlags.Static).GetValue(null);
            foreach (string name in names)
            {
                Type witness = Assembly.Load(name).GetType((string)Invoke("WitnessName", name), true);
                MethodInfo run = witness.GetMethod("Run");
                string[] first = (string[])run.Invoke(null, new object[] { phase });
                Invoke("ValidateBusinessValues", name, "BASELINE", phase, first, 0, null);
                string[] second = (string[])run.Invoke(null, new object[] { phase });
                Invoke("ValidateBusinessValues", name, "BASELINE", phase, second, 1, first);
                string[] corrupt = (string[])second.Clone();
                string key = phase == "new" ? "ctor.count=" : phase == "dispatch" ? "virtual=" : phase == "delegates" ? "event.afterRemove=" : "generic.method=";
                int index = Array.FindIndex(corrupt, value => value.StartsWith(key, StringComparison.Ordinal));
                Assert.GreaterOrEqual(index, 0); corrupt[index] = key + "WRONG";
                Assert.Throws<InvalidOperationException>(() => Invoke("ValidateBusinessValues", name, "BASELINE", phase, corrupt, 1, first));
            }
        }

        [Test] public void IteratorDisposalExecutesSuspendedFinally()
        {
            bool disposed = false;
            IEnumerator iterator = Suspended(() => disposed = true);
            Assert.IsTrue(iterator.MoveNext()); Assert.IsFalse(disposed);
            Invoke("DisposeIterator", iterator); Assert.IsTrue(disposed);
        }

        [Test] public void ActualFailureCodesAreRetainedBeforeTheAssertionThrows()
        {
            var result = new M06ExecutionProbe.Result { checks = new List<M06ExecutionProbe.Check>() };
            Assert.Throws<InvalidOperationException>(() => Invoke("RecordCheck", result, "GetState", (int)AssemblyShadowErrorCode.InvalidState,
                AssemblyShadowErrorCode.Success, "Staging", "Committed"));
            Assert.AreEqual((int)AssemblyShadowErrorCode.InvalidState, result.checks.Single().actualCode);
            Assert.AreEqual("Staging", result.checks.Single().actual);
        }

        [Test] public void FeatureOffKeepsTheExistingDisabledTransactionSchema()
        {
            var value = new AssemblyShadowDiagnostics { schemaVersion = 1, enabled = false, runtimeAbiVersion = 1, state = "Disabled", stateCode = (int)AssemblyShadowState.Disabled,
                lastError = (int)AssemblyShadowErrorCode.FeatureDisabled, detail = "", baselineBuildId = "", patchId = "", closureLoadOrder = new string[0], stableAotNames = new string[0], commitOrder = new string[0],
                assemblies = new AssemblyShadowDiagnosticAssembly[0], events = new AssemblyShadowDiagnosticEvent[0], baselineUses = new AssemblyShadowBaselineUse[0],
                ordinaryAssemblies = new AssemblyShadowOrdinaryAssembly[0], ordinaryClasses = new AssemblyShadowOrdinaryClass[0] };
            Invoke("ValidateDisabledDiagnostics", value);
            value.enabled = true; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateDisabledDiagnostics", value));
            value.enabled = false; value.commitOrder = null; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateDisabledDiagnostics", value));
            value.commitOrder = new string[0]; value.staged = 1; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateDisabledDiagnostics", value));
        }

        [Test] public void StartupProofBindsArchivedBytesCompilerAndActualBootstrapRole()
        {
            string directory = Path.Combine(Path.GetTempPath(), "M06StartupTest-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(directory);
            string scene = Path.Combine(directory, "scene.unity"), script = Path.Combine(directory, "bootstrap.cs");
            try
            {
                File.WriteAllText(scene, "captured scene"); File.WriteAllText(script, "captured script");
                string sceneHash = (string)Invoke("HashFile", scene), scriptHash = (string)Invoke("HashFile", script);
                string assembly = typeof(M06BootstrapRunner).Assembly.FullName, type = typeof(M06BootstrapRunner).FullName;
                var proof = new M06ExecutionProbe.ExecutionPolicyProof { schemaVersion = 1, milestone = "M06", compileSnapshotHash = new string('a', 64),
                    bootstrapExecutionOrder = -32000, bootstrapAssemblyIdentity = assembly, bootstrapTypeName = type, diagnostics = new string[0],
                    startupScenePath = scene, startupSceneSourcePath = "original scene", startupSceneSha256 = sceneHash, bootstrapScriptPath = script, bootstrapScriptSourcePath = "original script", bootstrapScriptSha256 = scriptHash,
                    files = new[] { new M06ExecutionProbe.StartupFile { sourcePath = "original scene", path = scene, sha256 = sceneHash }, new M06ExecutionProbe.StartupFile { sourcePath = "original script", path = script, sha256 = scriptHash } },
                    preloadedAssets = new M06ExecutionProbe.PreloadedAsset[0], scripts = new[] { new M06ExecutionProbe.StartupScript {
                        phase = "StartupScene", assemblyIdentity = assembly, typeName = type, assetSourcePath = "original scene", assetPath = scene, assetSha256 = sceneHash,
                        scriptSourcePath = "original script", scriptPath = script, scriptSha256 = scriptHash, isBootstrapRunner = true, isCandidateDependent = true,
                        dependencyProved = true, callbacks = new[] { "Awake" }, dependencyEvidence = new[] { "captured dependency" }, executionOrder = -32000 } } };
                var plan = new M06ExecutionProbe.GenerationPlanProof { compileSnapshotHash = proof.compileSnapshotHash };
                Invoke("ValidateStartupProof", proof, plan);
                plan.compileSnapshotHash = new string('b', 64); Assert.Throws<InvalidOperationException>(() => Invoke("ValidateStartupProof", proof, plan)); plan.compileSnapshotHash = proof.compileSnapshotHash;
                proof.scripts[0].isBootstrapRunner = false; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateStartupProof", proof, plan)); proof.scripts[0].isBootstrapRunner = true;
                proof.scripts[0].isCandidate = true; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateStartupProof", proof, plan)); proof.scripts[0].isCandidate = false;
                File.WriteAllText(script, "changed script"); Assert.Throws<InvalidOperationException>(() => Invoke("ValidateStartupProof", proof, plan));
            }
            finally { Directory.Delete(directory, true); }
        }

        [Test] public void WarmupMethodSchemaRequiresExplicitGenericArityAndStaticFlag()
        {
            Type type = typeof(M06ExecutionProbe).GetNestedType("WarmupMethod", BindingFlags.NonPublic);
            string json = "{\"assembly\":\"literal\",\"declaringType\":\"Witness\",\"name\":\"Run\",\"isStatic\":true,\"genericArity\":0,\"genericArguments\":[],\"parameterTypes\":[],\"returnType\":{\"assembly\":\"core\",\"type\":\"System.String[]\"}}";
            ValidateShape(json, type);
            Assert.Throws<InvalidOperationException>(() => ValidateShape(json.Replace("\"genericArity\":0,", ""), type));
            Assert.Throws<InvalidOperationException>(() => ValidateShape(json.Replace("\"isStatic\":true,", ""), type));
        }

        [Test] public void WarmupPrimitiveResolutionAllowsOnlyTheActiveDeclaredOrResolvedProvider()
        {
            Assembly owner = typeof(M06ExecutionProbe).Assembly;
            string declared = owner.GetReferencedAssemblies().Single(reference => reference.Name == "netstandard").FullName;
            Type identity = typeof(M06ExecutionProbe).GetNestedType("WarmupTypeIdentity", BindingFlags.NonPublic);
            object value = Activator.CreateInstance(identity); identity.GetField("assembly").SetValue(value, declared); identity.GetField("type").SetValue(value, "System.Int32");
            Assert.AreEqual(typeof(int), Invoke("ResolveWarmupType", value, owner));
            identity.GetField("assembly").SetValue(value, typeof(int).Assembly.FullName); Assert.AreEqual(typeof(int), Invoke("ResolveWarmupType", value, owner));
            identity.GetField("assembly").SetValue(value, declared.Replace("Version=2.1.0.0", "Version=9.0.0.0"));
            Assert.Throws<InvalidOperationException>(() => Invoke("ResolveWarmupType", value, owner));
            identity.GetField("assembly").SetValue(value, declared); identity.GetField("type").SetValue(value, "System.DateTime");
            Assert.Throws<InvalidOperationException>(() => Invoke("ResolveWarmupType", value, owner));
        }

        [Test] public void ByteVerificationRejectsChangedFileAndEscapingPath()
        {
            string directory = Path.Combine(Path.GetTempPath(), "M06ProofTest-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(directory);
            string path = Path.Combine(directory, "proof.bin");
            try
            {
                File.WriteAllBytes(path, Encoding.UTF8.GetBytes("verified")); string hash = (string)Invoke("HashFile", path);
                Invoke("VerifyBytes", path, hash, "test"); File.WriteAllBytes(path, Encoding.UTF8.GetBytes("changed"));
                Assert.Throws<InvalidOperationException>(() => Invoke("VerifyBytes", path, hash, "test"));
                Assert.Throws<InvalidOperationException>(() => Invoke("ConfinedSnapshotPath", directory, "../outside.dll"));
            }
            finally { Directory.Delete(directory, true); }
        }

        [Test] public void ActualBootstrapIlHasNoCandidateReferencesOrModuleEnumerationWarmup()
        {
            using (var module = dnlib.DotNet.ModuleDefMD.Load(typeof(M06ExecutionProbe).Assembly.Location))
            {
                string[] candidates = (string[])typeof(M06ExecutionProbe).GetField("Candidates", BindingFlags.NonPublic | BindingFlags.Static).GetValue(null);
                Assert.IsFalse(module.GetAssemblyRefs().Any(reference => candidates.Contains(reference.Name.String)));
                var probe = module.Find("AssemblyShadowDemo.M06ExecutionProbe", false);
                var run = probe.Methods.Single(method => method.Name == "RunWarmup");
                Assert.IsFalse(run.Body.Instructions.Any(instruction => instruction.Operand is dnlib.DotNet.IMethod && ((dnlib.DotNet.IMethod)instruction.Operand).FullName.Contains("System.Reflection.Module::GetTypes")));
                Assert.IsTrue(run.Body.Instructions.Any(instruction => instruction.OpCode == dnlib.DotNet.Emit.OpCodes.Ldstr && (string)instruction.Operand == "warmup"));
                foreach (var selector in new[] { new[] { "InvokeRun", "Run" }, new[] { "InvokeAsyncCoroutine", "RunAsync" }, new[] { "InvokeCoroutine", "RunCoroutine" }, new[] { "InvokeModuleEvidence", "GetModuleEvidence" } })
                {
                    // Iterator method bodies live on their compiler-generated state machine; the finite string remains in this exact owning family.
                    Assert.IsTrue(module.GetTypes().Where(type => type == probe || type.DeclaringType == probe && type.Name.String.Contains(selector[0]))
                        .SelectMany(type => type.Methods).Where(method => method.HasBody && (method.DeclaringType != probe || method.Name == selector[0]))
                        .SelectMany(method => method.Body.Instructions).Any(instruction => instruction.OpCode == dnlib.DotNet.Emit.OpCodes.Ldstr && (string)instruction.Operand == selector[1]), selector[0]);
                }
            }
        }

        [Test] public void CoroutineIlValidatesAndPreparesTransactionBeforeFirstYield()
        {
            using (var module = dnlib.DotNet.ModuleDefMD.Load(typeof(M06ExecutionProbe).Assembly.Location))
                foreach (var pair in new[] { new[] { "RunAndWriteCoroutine", "ReadInputs" }, new[] { "RunTransactionCoroutine", "PrepareTransaction" } })
                {
                    var stateMachine = module.GetTypes().Single(type => type.DeclaringType != null && type.DeclaringType.FullName == typeof(M06ExecutionProbe).FullName && type.Name.String.Contains("<" + pair[0] + ">"));
                    var instructions = stateMachine.Methods.Single(method => method.Name == "MoveNext").Body.Instructions;
                    int prerequisite = instructions.ToList().FindIndex(instruction => instruction.Operand is dnlib.DotNet.IMethod && ((dnlib.DotNet.IMethod)instruction.Operand).Name == pair[1]);
                    int firstYield = instructions.ToList().FindIndex(instruction => instruction.OpCode == dnlib.DotNet.Emit.OpCodes.Stfld && instruction.Operand is dnlib.DotNet.IField &&
                        ((dnlib.DotNet.IField)instruction.Operand).Name.String.IndexOf("current", StringComparison.OrdinalIgnoreCase) >= 0);
                    Assert.GreaterOrEqual(prerequisite, 0, pair[0]); Assert.Greater(firstYield, prerequisite, pair[0] + " yielded before its startup prerequisite");
                }
        }

        [Test] public void SchemaFieldsRetainDeclaredAndResolvedAssemblyQualifiedNames()
        {
            int inspected = 0;
            foreach (Assembly assembly in new[] { typeof(M06ExecutionProbe).Assembly, typeof(AssemblyShadowExecutionDiagnostics).Assembly })
                using (var module = dnlib.DotNet.ModuleDefMD.Load(assembly.Location))
                    foreach (Type type in assembly.GetTypes().Where(type => type.IsSerializable &&
                        (type.DeclaringType == typeof(M06ExecutionProbe) && type.IsNestedPublic || type.Namespace == "HybridCLR" && type.Name.StartsWith("AssemblyShadow", StringComparison.Ordinal))))
                    {
                        var definition = module.Find(type.FullName.Replace('+', '/'), false);
                        var reflected = type.GetFields(BindingFlags.Public | BindingFlags.Instance).Where(field => !field.IsNotSerialized).ToArray();
                        var row = new M06ExecutionProbe.SchemaType { fields = definition.Fields.Where(field => field.IsPublic && !field.IsStatic && !field.IsNotSerialized)
                            .Select(field => new M06ExecutionProbe.SchemaField { name = field.Name.String, type = field.FieldType.AssemblyQualifiedName,
                                resolvedType = reflected.Single(actual => actual.Name == field.Name.String).FieldType.AssemblyQualifiedName,
                                attributes = (int)field.Attributes }).ToArray() };
                        Invoke("ValidateSchemaFields", row, type); ++inspected;
                        if (row.fields.Length > 0)
                        {
                            row.fields[0].resolvedType = row.fields[0].resolvedType.Replace("Version=", "Version=9");
                            Assert.Throws<InvalidOperationException>(() => Invoke("ValidateSchemaFields", row, type), type.FullName);
                        }
                    }
            Assert.Greater(inspected, 40);
        }

        [Test] public void CanonicalReceiptJoinRetainsExactMetadataIdentityAndRejectsCollisions()
        {
            const string name = "AssemblyA.Contracts", fullName = "AssemblyA.Contracts, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null";
            var identity = new M04ReferenceProbe.AssemblyIdentity { name = name, fullName = fullName };
            var native = new M04ReferenceProbe.NativeAssemblyIdentity { name = name, fullName = fullName, imageName = name + ".dll" };
            var player = new M06ExecutionProbe.PlayerBuildReceipt { assemblyIdentities = new[] { identity }, nativeAssemblyIdentities = new[] { native } };
            var file = new M06ExecutionProbe.LinkedPlayerFile { name = name.ToLowerInvariant() };
            Assert.AreSame(identity, Invoke("LinkedIdentity", player, file));
            Invoke("RequireCanonicalSet", new[] { name }, new[] { file.name }, "linked");
            Assert.Throws<InvalidOperationException>(() => Invoke("RequireCanonicalSet", new[] { name, file.name }, new[] { name }, "collision"));
            player.assemblyIdentities = new[] { identity, new M04ReferenceProbe.AssemblyIdentity { name = file.name, fullName = fullName } };
            Assert.Throws<InvalidOperationException>(() => Invoke("LinkedIdentity", player, file)); player.assemblyIdentities = new[] { identity };
            native.fullName = fullName.Replace("1.0.0.0", "2.0.0.0"); Assert.Throws<InvalidOperationException>(() => Invoke("LinkedIdentity", player, file)); native.fullName = fullName;
            native.imageName = file.name + ".dll"; Assert.Throws<InvalidOperationException>(() => Invoke("LinkedIdentity", player, file));
        }

        [Test] public void LinkerMayRewriteDeclaredScopeButMustPreserveVerifiedResolvedIdentity()
        {
            string declared = "System.Int32, netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51", resolved = typeof(int).AssemblyQualifiedName;
            var before = new M06ExecutionProbe.SchemaType { assemblyIdentity = "captured-owner", isSerializable = true,
                fields = new[] { new M06ExecutionProbe.SchemaField { name = "value", type = declared, resolvedType = resolved, attributes = 6 } } };
            var after = new M06ExecutionProbe.SchemaType { assemblyIdentity = before.assemblyIdentity, isSerializable = true,
                fields = new[] { new M06ExecutionProbe.SchemaField { name = "value", type = declared, resolvedType = resolved, attributes = 6 } } };
            Invoke("ValidateSchemaPair", before, after);
            // Actual accepted Unity input references netstandard; its linked field references mscorlib.
            after.fields[0].type = resolved; Invoke("ValidateSchemaPair", before, after);
            Assert.AreEqual(declared, before.fields[0].type); Assert.AreEqual(resolved, after.fields[0].type);
            after.fields[0].type = ""; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateSchemaPair", before, after)); after.fields[0].type = resolved;
            after.fields[0].resolvedType = declared; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateSchemaPair", before, after));
            Assert.Throws<InvalidOperationException>(() => ValidateShape("{\"name\":\"value\",\"type\":\"declared\",\"attributes\":6}", typeof(M06ExecutionProbe.SchemaField)));
        }

        [Test] public void ModuleObservationUsesActualSupportedModuleEnumeration()
        {
            string[] names = (string[])typeof(M06ExecutionProbe).GetField("Candidates", BindingFlags.NonPublic | BindingFlags.Static).GetValue(null);
            foreach (string name in names)
            {
                Assembly assembly = Assembly.Load(name);
                Assert.AreEqual(assembly.GetModules().Single().Name, Invoke("ObservedModuleName", assembly));
            }
            using (var module = dnlib.DotNet.ModuleDefMD.Load(typeof(M06ExecutionProbe).Assembly.Location))
            {
                var methods = module.Find(typeof(M06ExecutionProbe).FullName, false).Methods.Where(method => method.Name == "ObservedModuleName" || method.Name == "AddModuleObservation").ToArray();
                var calls = methods.SelectMany(method => method.Body.Instructions).Select(instruction => instruction.Operand).OfType<dnlib.DotNet.IMethod>().ToArray();
                Assert.IsFalse(calls.Any(call => call.Name == "get_ManifestModule")); Assert.IsTrue(calls.Any(call => call.Name == "GetModules"));
            }
        }

        [Test] public void RecoveryRequiresActualNativeInitializerErrorAndExactFailedImage()
        {
            const string name = "AssemblyA.Implementation.Internal", mvid = "f4850bf6-80ce-47c3-ae6c-890473b14f86";
            var fixture = new M06ExecutionProbe.Fixture { patchId = "InitializerFailure", closureLoadOrder = new[] { name } };
            Type patchType = typeof(M06ExecutionProbe).GetNestedType("PatchManifest", BindingFlags.NonPublic), imageType = typeof(M06ExecutionProbe).GetNestedType("PatchAssembly", BindingFlags.NonPublic);
            object patch = Activator.CreateInstance(patchType), image = Activator.CreateInstance(imageType);
            imageType.GetField("name").SetValue(image, name); imageType.GetField("mvid").SetValue(image, mvid);
            Array closure = Array.CreateInstance(imageType, 1); closure.SetValue(image, 0); patchType.GetField("closure").SetValue(patch, closure);
            typeof(M06ExecutionProbe.Fixture).GetField("patch", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(fixture, patch);
            var value = new AssemblyShadowDiagnostics { schemaVersion = 1, enabled = true, runtimeAbiVersion = 1, stateCode = (int)AssemblyShadowState.FailedAfterCommit,
                state = "FailedAfterCommit", lastError = (int)AssemblyShadowErrorCode.ModuleInitializerFailed, baselineBuildId = "baseline", patchId = fixture.patchId,
                generation = 1, expected = 1, staged = 1, closureLoadOrder = new[] { name }, assemblies = new[] { new AssemblyShadowDiagnosticAssembly { name = name, mvid = mvid,
                    skeletonBuilt = true, runtimeMetadataInitialized = true, published = true, moduleInitializerAttempted = true, moduleInitializerRan = false } } };
            Invoke("ValidateRetainedInitializerFailure", value, fixture, "baseline");
            value.lastError = 0; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateRetainedInitializerFailure", value, fixture, "baseline")); value.lastError = (int)AssemblyShadowErrorCode.ModuleInitializerFailed;
            value.assemblies[0].moduleInitializerRan = true; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateRetainedInitializerFailure", value, fixture, "baseline")); value.assemblies[0].moduleInitializerRan = false;
            value.assemblies[0].mvid = "other"; Assert.Throws<InvalidOperationException>(() => Invoke("ValidateRetainedInitializerFailure", value, fixture, "baseline"));
        }

        [Test] public void UnavailableStackFramesAreExplicitAndCannotSupplyMethodEvidence()
        {
            string[] unavailable = { "frame.0.methodAvailable=False", "frame.0.declaringType=absent", "frame.0.method=absent", "frame.0.token=0", "frame.0.file=actual.cs", "frame.0.line=12" };
            Assert.AreEqual(false, Invoke("FrameMethodAvailable", unavailable, "frame.0."));
            Assert.Throws<InvalidOperationException>(() => Invoke("FrameMethodAvailable", unavailable.Skip(1).ToArray(), "frame.0."));
            unavailable[3] = "frame.0.token=100663297"; Assert.Throws<InvalidOperationException>(() => Invoke("FrameMethodAvailable", unavailable, "frame.0."));
            string[] available = { "frame.0.methodAvailable=True", "frame.0.declaringType=Actual.Witness", "frame.0.method=ThrowNested", "frame.0.token=100663297" };
            Assert.AreEqual(true, Invoke("FrameMethodAvailable", available, "frame.0."));
        }

        private static IEnumerator Suspended(Action onDispose) { try { yield return null; } finally { onDispose(); } }
        private static void ValidateShape(string json, Type type)
        {
            Type readerType = typeof(M06ExecutionProbe).GetNestedType("ProofJsonReader", BindingFlags.NonPublic);
            object reader = Activator.CreateInstance(readerType, BindingFlags.NonPublic | BindingFlags.Instance, null, new object[] { json }, null);
            object value;
            try { value = readerType.GetMethod("Read", BindingFlags.NonPublic | BindingFlags.Instance).Invoke(reader, null); }
            catch (TargetInvocationException error) { throw error.InnerException; }
            Invoke("ValidateJsonShape", value, type, type.Name);
        }
        private static object Invoke(string name, params object[] arguments)
        {
            MethodInfo method = typeof(M06ExecutionProbe).GetMethod(name, BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(method, name);
            try { return method.Invoke(null, arguments); } catch (TargetInvocationException error) { throw error.InnerException; }
        }
    }
}
