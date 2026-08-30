using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Build;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06BuildTests
    {
        [Test] public void FixtureDefinesAreM06OnlyAndRootsAreTruthful()
        {
            CollectionAssert.AreEqual(new[] { "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M06" }, (string[])Call(typeof(M06Build), "ExpectedDefines", "P01"));
            foreach (string id in new[] { "P01", "P02", "P03", "InitializerFailure" })
            {
                var defines = (string[])Call(typeof(M06Build), "ExpectedDefines", id);
                Assert.IsFalse(defines.Any(value => value.Contains("M03") || value.Contains("M04") || value.Contains("M05")));
                Assert.AreEqual(defines.Length, defines.Distinct().Count());
            }
            CollectionAssert.AreEqual(new[] { "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ExtensibilityConsumer" }, (string[])Call(typeof(M06Build), "ExpectedChangedRoots", "P02"));
            CollectionAssert.AreEqual(M06Build.ProviderFirstOrder, (string[])Call(typeof(M06Build), "ExpectedChangedRoots", "P03"));
            CollectionAssert.AreEqual(new[] { "AssemblyA.Implementation.Internal" }, (string[])Call(typeof(M06Build), "ExpectedChangedRoots", "InitializerFailure"));
            Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "ExpectedDefines", "M05"));
        }
        [Test] public void ReleaseBuildOptionsAreGenuinelyDifferent()
        {
            var development = (BuildOptions)Call(typeof(M06Build), "PlayerOptions", true);
            var release = (BuildOptions)Call(typeof(M06Build), "PlayerOptions", false);
            Assert.IsTrue((development & BuildOptions.Development) != 0); Assert.IsFalse((release & BuildOptions.Development) != 0);
            Assert.AreEqual(development & ~BuildOptions.Development, release);
            Assert.AreEqual(BuildOptions.CleanBuildCache | BuildOptions.DetailedBuildReport, release);
        }
        [Test] public void ReleaseNativeConfigurationOverridesInheritedDebugAfterM02Setup()
        {
            Assert.AreEqual(Il2CppCompilerConfiguration.Debug, (Il2CppCompilerConfiguration)Call(typeof(M06Build), "NativeConfiguration", true));
            Assert.AreEqual(Il2CppCompilerConfiguration.Release, (Il2CppCompilerConfiguration)Call(typeof(M06Build), "NativeConfiguration", false));
            using (var module = ModuleDefMD.Load(typeof(M06Build).Assembly.Location))
            {
                var method = module.Find(typeof(M06Build).FullName, false).Methods.Single(value => value.Name == "ConfigureMode");
                var instructions = method.Body.Instructions.Where(instruction => instruction.OpCode.Code != Code.Nop).ToArray();
                int inherited = Array.FindIndex(instructions, instruction => {
                    var called = instruction.Operand as IMethod;
                    return called != null && called.DeclaringType.FullName == typeof(M02Build).FullName && called.Name == "Configure";
                });
                int selected = Array.FindIndex(instructions, instruction => {
                    var called = instruction.Operand as IMethod;
                    return called != null && called.DeclaringType.FullName == typeof(M06Build).FullName && called.Name == "NativeConfiguration";
                });
                Assert.GreaterOrEqual(inherited, 0); Assert.Greater(selected, inherited);
                Assert.AreEqual(Code.Ldarg_0, instructions[selected - 1].OpCode.Code, "The native mode must use the requested development mode.");
                var setter = instructions[selected + 1].Operand as IMethod;
                Assert.IsNotNull(setter); Assert.AreEqual(typeof(PlayerSettings).FullName, setter.DeclaringType.FullName);
                Assert.AreEqual("SetIl2CppCompilerConfiguration", setter.Name.String);
                var target = instructions[selected - 2].Operand as IField;
                Assert.IsNotNull(target); Assert.AreEqual(typeof(NamedBuildTarget).FullName, target.DeclaringType.FullName);
                Assert.AreEqual("Standalone", target.Name.String);
                Assert.AreEqual(1, instructions.Count(instruction => {
                    var called = instruction.Operand as IMethod;
                    return called != null && called.DeclaringType.FullName == typeof(PlayerSettings).FullName && called.Name == "SetIl2CppCompilerConfiguration";
                }), "No later setter may silently restore inherited Debug.");
            }
        }
        [Test] public void M06BaselineIdentityRejectsOlderMilestonesAndEscapedPaths()
        {
            Call(typeof(M06Build), "RequireSafeId", "M06-Baseline-v1"); Call(typeof(M06Build), "RequireSafeId", "M06-Baseline-Release-v1");
            foreach (string id in new[] { "M05-Baseline-v1", "../M06-Baseline-v1", "M06-Baseline-../other", "M06-Baseline-\\outside", "M06-Baseline-v1\n", "" })
                Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "RequireSafeId", id));
        }
        [Test] public void MetadataRequirementsComeFromCollectorAndExcludeOnlyCurrentClosure()
        {
            var receipt = new ShadowGenerationOutputReceipt { stage = "AotGenericReference", emittedAssemblyNames = new[] { "mscorlib.dll", "AssemblyA.Contracts.dll", "AssemblyA.Implementation.Internal.dll" } };
            CollectionAssert.AreEqual(new[] { "AssemblyA.Contracts", "mscorlib" }, (string[])Call(typeof(M06GenerationBuild), "RequiredMetadataNames", receipt, new[] { "AssemblyA.Implementation.Internal" }));
            receipt.emittedAssemblyNames = new[] { "mscorlib.dll", "mscorlib" };
            Assert.Throws<BuildFailedException>(() => Call(typeof(M06GenerationBuild), "RequiredMetadataNames", receipt, new string[0]));
            receipt.emittedAssemblyNames = new[] { "../mscorlib.dll" };
            Assert.Throws<BuildFailedException>(() => Call(typeof(M06GenerationBuild), "RequiredMetadataNames", receipt, new string[0]));
        }
        [Test] public void MissingActualPlayerMetadataHasNoAmbientFallback()
        {
            var generation = new M06GenerationProof { plans = new[] { new M06GenerationPlanProof { planId = "P01", requiredAotMetadataNames = new[] { "Required.Core" } } } };
            Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "MetadataInputs", generation, new M04AssemblyIdentity[0]));
        }
        [Test] public void FiniteWitnessNamesNeverAcceptArbitraryAssemblies()
        {
            foreach (string name in M06Build.ProviderFirstOrder) Assert.IsTrue(((string)Call(typeof(M06Build), "Witness", name)).EndsWith("M06ExecutionWitness", StringComparison.Ordinal));
            Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "Witness", "Other"));
        }
        [Test] public void WarmupDeclaresExactRunAndClosedGenericMethodsForEveryCapturedWitness()
        {
            using (var fixture = new WarmupFixture())
            foreach (string id in new[] { "P01", "P02", "P03", "InitializerFailure" })
            {
                var closure = (string[])Call(typeof(M06Build), "ExpectedChangedRoots", id);
                var plan = (ShadowWarmupPlan)Call(typeof(M06Build), "Warmup", fixture.Inputs, closure);
                CollectionAssert.AreEqual(closure, plan.types.Select(entry => entry.assembly).ToArray());
                Assert.AreEqual(closure.Length * 4, plan.methods.Length);
                foreach (string assembly in closure)
                {
                    var methods = plan.methods.Where(entry => entry.assembly == assembly).ToArray();
                    CollectionAssert.AreEqual(new[] { "WarmupValue", "WarmupEcho", "WarmupEcho", "Run" }, methods.Select(entry => entry.name).ToArray());
                    Assert.IsTrue(methods.All(entry => entry.isStatic && entry.declaringType == (string)Call(typeof(M06Build), "Witness", assembly)));
                    CollectionAssert.AreEqual(new[] { "System.Int32", "System.String" }, methods.Where(entry => entry.name == "WarmupEcho").Select(entry => entry.genericArguments.Single().type).ToArray());
                    var run = methods.Single(entry => entry.name == "Run");
                    Assert.AreEqual(0, run.genericArity); Assert.IsEmpty(run.genericArguments);
                    Assert.AreEqual("System.String[]", run.returnType.type);
                    Assert.AreEqual("System.String", run.parameterTypes.Single().type);
                    Assert.AreEqual(fixture.CoreIdentity, run.returnType.assembly);
                    Assert.AreEqual(fixture.CoreIdentity, run.parameterTypes.Single().assembly);
                    Assert.IsTrue(methods.SelectMany(entry => entry.genericArguments.Concat(entry.parameterTypes).Concat(new[] { entry.returnType }))
                        .All(identity => identity.assembly == fixture.CoreIdentity));
                }
            }
        }
        [Test] public void WarmupRejectsMissingBodyOrWrongRunSignatureFromActualDllBytes()
        {
            foreach (string mutation in new[] { "missing", "wrong-return", "bodyless", "duplicate" })
            using (var fixture = new WarmupFixture(mutation))
                Assert.Throws<ShadowBuildException>(() => Call(typeof(M06Build), "Warmup", fixture.Inputs, M06Build.ProviderFirstOrder), mutation);
        }
        [Test] public void WarmupRetainsTheCapturedCompilerProviderInsteadOfAssumingRuntimeMscorlib()
        {
            using (var fixture = new WarmupFixture(null, true))
            {
                var plan = (ShadowWarmupPlan)Call(typeof(M06Build), "Warmup", fixture.Inputs, new[] { M06Build.ProviderFirstOrder[0] });
                Assert.AreNotEqual(fixture.CoreIdentity, fixture.CompilerCoreIdentity);
                Assert.IsTrue(plan.methods.SelectMany(entry => entry.genericArguments.Concat(entry.parameterTypes).Concat(new[] { entry.returnType }))
                    .All(identity => identity.assembly == fixture.CompilerCoreIdentity));
            }
        }
        [Test] public void FixtureWarmupsFailFastBeforeTheExpensivePlayerReceiptReplay()
        {
            using (var module = ModuleDefMD.Load(typeof(M06Build).Assembly.Location))
            {
                var method = module.Find(typeof(M06Build).FullName, false).Methods.Single(value => value.Name == "BuildFixtures");
                var calls = method.Body.Instructions.Select(instruction => instruction.Operand).OfType<IMethod>().ToArray();
                int preflight = Array.FindIndex(calls, call => call.DeclaringType.FullName == typeof(M06Build).FullName && call.Name == "PreflightFixtureWarmups");
                int playerReplay = Array.FindIndex(calls, call => call.DeclaringType.FullName == typeof(M06EditorValidation).FullName && call.Name == "ValidatePlayerReceipt");
                Assert.GreaterOrEqual(preflight, 0); Assert.Greater(playerReplay, preflight);
            }
        }
        [Test] public void CompiledStartupCaptureRequiresByteBoundCompilerPolicyBeforeImportedAssetCapture()
        {
            using (var module = ModuleDefMD.Load(typeof(M06GenerationBuild).Assembly.Location))
            {
                var method = module.Find(typeof(M06GenerationBuild).FullName, false).Methods.Single(value => value.Name == "CaptureExecutionPolicy");
                var instructions = method.Body.Instructions.Where(instruction => instruction.OpCode.Code != Code.Nop).ToArray();
                int gate = Array.FindIndex(instructions, instruction => {
                    var called = instruction.Operand as IMethod;
                    return called != null && called.DeclaringType.FullName == typeof(ShadowReflectionBindingEvidence).FullName && called.Name == "ValidateCompilerSnapshot";
                });
                Assert.GreaterOrEqual(gate, 0, "The byte-bound compiler reflection/raw/policy gate must be called.");
                Assert.AreEqual("ThrowIfInvalid", ((IMethod)instructions[gate + 1].Operand).Name.String);
                int imported = Array.FindIndex(instructions, instruction => {
                    var called = instruction.Operand as IMethod;
                    return called != null && called.DeclaringType.FullName == typeof(ShadowExecutionPolicy).FullName && called.Name == "CaptureCurrentEditor";
                });
                Assert.Greater(imported, gate + 1, "Imported startup assets cannot be captured before policy rejection.");
            }
        }
        [Test] public void PatchPlanComparisonRejectsByteOrderAndReleasePdbDrift()
        {
            string root = Path.Combine(Path.GetTempPath(), "M06PatchPlan-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(root);
            try
            {
                string dll = Path.Combine(root, "A.dll"), pdb = Path.Combine(root, "A.pdb");
                File.WriteAllBytes(dll, new byte[] { 1, 2, 3 }); File.WriteAllBytes(pdb, new byte[] { 4, 5, 6 });
                var receipt = new ShadowGenerationPlanReceipt { closure = new[] { "A" }, loadOrder = new[] { "A" }, images = new[] {
                    new GenerationImage { name = "A", sha256 = ShadowHash.File(dll), mvid = "unit-test-identity", pdbPath = "A.pdb", pdbSha256 = ShadowHash.File(pdb) } } };
                var constructor = typeof(VerifiedGenerationPlan).GetConstructor(BindingFlags.Instance | BindingFlags.NonPublic, null, new[] { typeof(string), typeof(ShadowGenerationPlanReceipt) }, null);
                var plan = (VerifiedGenerationPlan)constructor.Invoke(new object[] { root, receipt });
                var patch = new ShadowPatchManifest { loadOrder = new[] { "A" }, closure = new[] { new ShadowPatchAssembly { name = "A", dll = "A.dll", sha256 = ShadowHash.File(dll),
                    mvid = "unit-test-identity", pdb = "A.pdb", pdbSha256 = ShadowHash.File(pdb) } } };
                Call(typeof(M06Build), "RequirePatchPlan", patch, plan, root, true);
                Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "RequirePatchPlan", patch, plan, root, false));
                patch.loadOrder = new[] { "Other" }; Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "RequirePatchPlan", patch, plan, root, true));
                patch.loadOrder = new[] { "A" }; File.AppendAllText(dll, "changed");
                Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "RequirePatchPlan", patch, plan, root, true));
            }
            finally { Directory.Delete(root, true); }
        }
        [Test] public void RuntimeMirrorsKeepModeAndGenerationBindingsExplicit()
        {
            Assert.AreEqual(typeof(int), typeof(M06PlayerBuildReceipt).GetField("buildOptions").FieldType);
            Assert.AreEqual(typeof(bool), typeof(M06FixtureManifest).GetField("developmentBuild").FieldType);
            Assert.IsNotNull(typeof(M06Fixture).GetField("generationPlanSha256")); Assert.IsNull(typeof(M06Fixture).GetField("warmup"));
            Assert.IsNotNull(typeof(M06GenerationPlanProof).GetField("compilerModeSha256"));
            Assert.AreEqual(typeof(M06GenerationProof), typeof(M06GenerationBuild).GetMethod("ReadAndVerify", new[] { typeof(string) }).ReturnType);
        }
        [Test] public void MissingModeZeroAndCompilerProvenanceFieldsNeverBecomeDefaults()
        {
            string player = JsonDefaults(typeof(M06PlayerBuildReceipt));
            M04JsonEvidence.ValidateSchema<M06PlayerBuildReceipt>(player);
            foreach (string name in new[] { "developmentBuild", "buildOptions", "generationProofSha256" })
            {
                string value = name == "developmentBuild" ? "false" : name == "buildOptions" ? "0" : "\"\"";
                string changed = player.Replace("\"" + name + "\":" + value + ",", ""); Assert.AreNotEqual(player, changed);
                Assert.Throws<ShadowBuildException>(() => M04JsonEvidence.ValidateSchema<M06PlayerBuildReceipt>(changed));
            }
            player = player.Replace("\"buildOptions\":0", "\"buildOptions\":false");
            Assert.Throws<ShadowBuildException>(() => M04JsonEvidence.ValidateSchema<M06PlayerBuildReceipt>(player));
            string plan = JsonDefaults(typeof(M06GenerationPlanProof));
            M04JsonEvidence.ValidateSchema<M06GenerationPlanProof>(plan); plan = plan.Replace("\"compilerModeSha256\":\"\",", "");
            Assert.Throws<ShadowBuildException>(() => M04JsonEvidence.ValidateSchema<M06GenerationPlanProof>(plan));
        }
        [Test] public void InterruptedPlayerResumeIsBoundToExistingProofsAndNeverRebuilds()
        {
            foreach (string name in new[] { "ResumePlayerBaselineCapture", "ResumeReleasePlayerBaselineCapture", "ResumeFeatureDisabledPlayerCapture" })
                Assert.IsNotNull(typeof(M06Build).GetMethod(name, BindingFlags.Public | BindingFlags.Static));
            using (var module = ModuleDefMD.Load(typeof(M06Build).Assembly.Location))
            {
                var type = module.Find(typeof(M06Build).FullName, false);
                var resume = type.Methods.Single(method => method.Name == "ResumePlayer");
                var finalize = type.Methods.Single(method => method.Name == "FinalizePlayerCapture");
                Func<MethodDef, IMethod[]> calls = method => method.Body.Instructions.Select(instruction => instruction.Operand as IMethod).Where(methodCall => methodCall != null).ToArray();
                Assert.IsFalse(calls(resume).Any(method => method.DeclaringType.FullName == typeof(BuildPipeline).FullName && method.Name == "BuildPlayer"));
                Assert.IsTrue(calls(resume).Any(method => method.DeclaringType.FullName == typeof(M06Build).FullName && method.Name == "VerifyInterruptedBuildLog"));
                Assert.IsTrue(calls(resume).Any(method => method.DeclaringType.FullName == typeof(M06Build).FullName && method.Name == "FinalizePlayerCapture"));
                Assert.IsTrue(calls(finalize).Any(method => method.DeclaringType.FullName == typeof(M06ExecutionSchemaVerifier).FullName && method.Name == "VerifyProofs"));
                Assert.IsTrue(calls(finalize).Any(method => method.DeclaringType.FullName == typeof(M06ExecutionSchemaVerifier).FullName && method.Name == "WriteProofs"));
            }
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M06Build.cs");
            foreach (string argument in new[] { "-shadowPlayerSnapshot", "-shadowBuildOutput", "-shadowM06InterruptedBuildLog" }) StringAssert.Contains(argument, source);
        }
        [Test] public void InterruptedBuildLogMustBindConfigurationSnapshotAndNativeHash()
        {
            string path = Path.Combine(Path.GetTempPath(), "M06InterruptedBuild-" + Guid.NewGuid().ToString("N") + ".log");
            var captured = new AssemblySnapshotReceipt { snapshotHash = new string('a', 64), nativeLibrarySha256 = new string('b', 64) };
            string valid = "Build Finished, Result: Success.\n--compiler-flags=-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\n" +
                "AssemblyShadowDemo.Editor.M06Build:BuildPlayerBaseline\n[AssemblyShadow] Sealed Player input snapshot " + captured.snapshotHash + " for native " + captured.nativeLibrarySha256;
            try
            {
                File.WriteAllText(path, valid); Assert.AreEqual(ShadowHash.File(path), Call(typeof(M06Build), "VerifyInterruptedBuildLog", path, captured, true, true));
                File.WriteAllText(path, valid.Replace("ASSEMBLY_SHADOW=1", "ASSEMBLY_SHADOW=0"));
                Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "VerifyInterruptedBuildLog", path, captured, true, true));
                File.WriteAllText(path, valid.Replace(captured.nativeLibrarySha256, new string('c', 64)));
                Assert.Throws<BuildFailedException>(() => Call(typeof(M06Build), "VerifyInterruptedBuildLog", path, captured, true, true));
            }
            finally { if (File.Exists(path)) File.Delete(path); }
        }
        [Test] public void BuilderSourceDoesNotInvokeLegacyGenerationOrM01WholeDllEquality()
        {
            string build = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M06Build.cs");
            string generation = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M06GenerationBuild.cs");
            Assert.IsFalse(build.Contains("PrebuildCommand.GenerateAll")); Assert.IsFalse(generation.Contains("PrebuildCommand.GenerateAll"));
            Assert.IsFalse(build.Contains("VerifySemanticEquivalence")); Assert.IsFalse(generation.Contains("GenerateStripedAOTDlls("));
            Assert.IsFalse(build.Contains("ShadowBuildSession"), "M06 must not reuse or overwrite the M05 session.");
            Assert.IsTrue(build.Contains("BuildWithWarmup")); Assert.IsTrue(build.Contains("CompileWithOptions"));
            Assert.IsTrue(build.Contains("SetPlayerExportProject(target, false)"), "Actual Players must override stale native-project export state.");
            Assert.IsTrue(build.Contains("EditorUserBuildSettings.buildScriptsOnly = false"), "Actual Players must override stale scripts-only state.");
        }
        private static object Call(Type type, string name, params object[] arguments)
        {
            try { return type.GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, arguments); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }
        private sealed class WarmupFixture : IDisposable
        {
            private readonly string root = Path.Combine(Path.GetTempPath(), "M06BuilderWarmup-" + Guid.NewGuid().ToString("N"));
            internal readonly CompiledAssemblySet Inputs;
            internal string CoreIdentity { get { return Inputs.GetModule("mscorlib").Assembly.FullName; } }
            internal string CompilerCoreIdentity { get { return Inputs.GetModule(compilerFacade ? "netstandard" : "mscorlib").Assembly.FullName; } }
            private readonly bool compilerFacade;
            internal WarmupFixture(string mutation = null, bool compilerFacade = false)
            {
                this.compilerFacade = compilerFacade;
                string source = Path.Combine(root, "Inputs"), references = Path.Combine(root, "References");
                Directory.CreateDirectory(source); Directory.CreateDirectory(references);
                File.Copy(typeof(object).Assembly.Location, Path.Combine(references, "mscorlib.dll"));
                string compilerCore = typeof(object).Assembly.FullName;
                if (compilerFacade)
                {
                    using (var facade = new ModuleDefUser("netstandard.dll", Guid.NewGuid(), new AssemblyRefUser(new AssemblyNameInfo(typeof(object).Assembly.FullName))) { Kind = ModuleKind.Dll })
                    {
                        new AssemblyDefUser("netstandard", new Version(2, 1, 0, 0)).Modules.Add(facade);
                        foreach (string name in new[] { "Object", "Int32", "String" })
                            facade.Types.Add(new TypeDefUser("System", name, null) { Attributes = dnlib.DotNet.TypeAttributes.Public });
                        facade.Write(Path.Combine(references, "netstandard.dll")); compilerCore = facade.Assembly.FullName;
                    }
                }
                foreach (string assembly in M06Build.ProviderFirstOrder)
                using (var module = new ModuleDefUser(assembly + ".dll", Guid.NewGuid(), new AssemblyRefUser(new AssemblyNameInfo(compilerCore))) { Kind = ModuleKind.Dll })
                {
                    new AssemblyDefUser(assembly, new Version(1, 0, 0, 0)).Modules.Add(module);
                    string witness = (string)Call(typeof(M06Build), "Witness", assembly); int split = witness.LastIndexOf('.');
                    var type = new TypeDefUser(witness.Substring(0, split), witness.Substring(split + 1), module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.Public };
                    module.Types.Add(type);
                    type.Methods.Add(Body("WarmupValue", MethodSig.CreateStatic(module.CorLibTypes.Int32, module.CorLibTypes.Int32), OpCodes.Ldarg_0));
                    var echo = Body("WarmupEcho", MethodSig.CreateStaticGeneric(1, new GenericMVar(0), new GenericMVar(0)), OpCodes.Ldarg_0);
                    echo.GenericParameters.Add(new GenericParamUser(0, GenericParamAttributes.NonVariant, "T")); type.Methods.Add(echo);
                    if (mutation != "missing")
                    {
                        TypeSig returned = mutation == "wrong-return" ? (TypeSig)module.CorLibTypes.String : new SZArraySig(module.CorLibTypes.String);
                        var run = Body("Run", MethodSig.CreateStatic(returned, module.CorLibTypes.String), OpCodes.Ldnull);
                        if (mutation == "bodyless") { run.Body = null; run.ImplAttributes = dnlib.DotNet.MethodImplAttributes.Runtime; }
                        type.Methods.Add(run);
                        if (mutation == "duplicate") type.Methods.Add(Body("Run", MethodSig.CreateStatic(returned, module.CorLibTypes.String), OpCodes.Ldnull));
                    }
                    module.Write(Path.Combine(source, assembly + ".dll"));
                }
                Inputs = DnlibAssemblyLoader.Load(source, new[] { references }, M06Build.ProviderFirstOrder.Select(name =>
                    new AssemblyCapability { name = name, isShadowCapable = true, capabilityDeclared = true }).ToArray());
            }
            private static MethodDef Body(string name, MethodSig signature, OpCode instruction)
            {
                var method = new MethodDefUser(name, signature, dnlib.DotNet.MethodImplAttributes.IL | dnlib.DotNet.MethodImplAttributes.Managed,
                    dnlib.DotNet.MethodAttributes.Public | dnlib.DotNet.MethodAttributes.Static) { Body = new CilBody() };
                method.Body.Instructions.Add(Instruction.Create(instruction)); method.Body.Instructions.Add(Instruction.Create(OpCodes.Ret)); return method;
            }
            public void Dispose() { Inputs.Dispose(); Directory.Delete(root, true); }
        }
        private static string JsonDefaults(Type type)
        {
            if (type == typeof(string)) return "\"\"";
            if (type.IsArray) return "[]";
            if (type == typeof(bool)) return "false";
            if (type.IsValueType) return "0";
            return "{" + string.Join(",", type.GetFields(BindingFlags.Instance | BindingFlags.Public).Select(field => "\"" + field.Name + "\":" + JsonDefaults(field.FieldType)).ToArray()) + "}";
        }
    }
}
