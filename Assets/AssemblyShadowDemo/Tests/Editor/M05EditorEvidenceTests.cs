using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor.Build;
using FieldAttributes = dnlib.DotNet.FieldAttributes;
using MethodAttributes = dnlib.DotNet.MethodAttributes;
using TypeAttributes = dnlib.DotNet.TypeAttributes;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M05EditorEvidenceTests
    {
        [Test] public void InventoryUsesActualTypeDefOrderNestingArityKindAndExportVisibility()
        {
            using (var fixture = new TypeFixture())
            {
                var inventory = fixture.Read();
                using (var module = ModuleDefMD.Load(fixture.Path))
                    CollectionAssert.AreEqual(module.GetTypes().Where(type => !type.IsGlobalModuleType).OrderBy(type => type.Rid).Select(type => type.ReflectionFullName), inventory.types.Select(type => type.fullName));
                Assert.IsFalse(inventory.types.Any(type => type.name == "<Module>"));
                var nested = inventory.types.Single(type => type.name == "Inner`1");
                Assert.AreEqual("Fixture.Outer`1+Inner`1", nested.fullName);
                Assert.AreEqual("", nested.namespaceName, "Nested namespace is the declared TypeDef namespace, not an invented copy of the enclosing namespace.");
                CollectionAssert.AreEqual(new[] { "Outer`1" }, nested.nestingPath);
                Assert.AreEqual(2, nested.genericArity, "Actual GenericParam count includes the enclosing generic context.");
                Assert.IsTrue(nested.isExported);
                Assert.IsFalse(inventory.types.Single(type => type.name == "PublicChild").isExported);
                Assert.AreEqual("interface", inventory.types.Single(type => type.name == "IShape").kind);
                Assert.AreEqual("enum", inventory.types.Single(type => type.name == "Choice").kind);
                Assert.AreEqual("valuetype", inventory.types.Single(type => type.name == "Value").kind);
            }
        }

        [Test] public void EveryTypeInventoryFieldAndOrderIsRecomputed()
        {
            using (var fixture = new TypeFixture())
            {
                foreach (var field in typeof(M05TypeDefinition).GetFields())
                {
                    var claim = fixture.Read();
                    object value = field.FieldType == typeof(bool) ? (object)!claim.types[0].isExported : field.FieldType == typeof(int) ? (object)99 : field.FieldType == typeof(string[]) ? (object)new[] { "Fake" } : "tampered";
                    field.SetValue(claim.types[0], value);
                    AssertCode("M05TypeInventoryMismatch", () => M05TypeInventoryProof.Verify(new[] { claim }, new[] { fixture.Read() }));
                }
                foreach (string operation in new[] { "missing", "extra", "reordered", "owner" })
                {
                    var claim = fixture.Read();
                    if (operation == "missing") claim.types = claim.types.Skip(1).ToArray();
                    else if (operation == "extra") claim.types = claim.types.Concat(new[] { claim.types[0] }).ToArray();
                    else if (operation == "reordered") Array.Reverse(claim.types);
                    else claim.assemblyName = "Other";
                    AssertCode("M05TypeInventoryMismatch", () => M05TypeInventoryProof.Verify(new[] { claim }, new[] { fixture.Read() }));
                }
            }
        }

        [Test] public void TypeInventoryRejectsChangedBytesRelativePathsAndWrongAssembly()
        {
            using (var fixture = new TypeFixture())
            {
                AssertCode("M05TypeInventoryPath", () => M05TypeInventoryProof.ReadFile("fixture.dll", fixture.Hash, "Fixture"));
                AssertCode("M05TypeInventoryIdentity", () => M05TypeInventoryProof.ReadFile(fixture.Path, fixture.Hash, "Other"));
                byte[] bytes = File.ReadAllBytes(fixture.Path); bytes[bytes.Length - 1] ^= 1; File.WriteAllBytes(fixture.Path, bytes);
                AssertCode("M05TypeInventoryBytes", () => M05TypeInventoryProof.ReadFile(fixture.Path, fixture.Hash, "Fixture"));
            }
        }

        [Test] public void MissingZeroFalseAndUnknownTypeFieldsCannotDefaultThroughJson()
        {
            const string json = "{\"fullName\":\"X\",\"namespaceName\":\"\",\"name\":\"X\",\"kind\":\"class\",\"nestingPath\":[],\"genericArity\":0,\"isExported\":false}";
            Assert.DoesNotThrow(() => M04JsonEvidence.ValidateSchema<M05TypeDefinition>(json));
            foreach (string changed in new[] { json.Replace(",\"genericArity\":0", ""), json.Replace(",\"isExported\":false", ""), json.Replace("false", "0"), json.Replace("\"kind\"", "\"unknown\""), json.Replace("[]", "null") })
                AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<M05TypeDefinition>(changed));
        }

        [Test] public void ModuleWitnessesCaptureActualInstructionsAndEveryClaimedField()
        {
            using (var module = CoreFixture())
            {
                var actual = ModuleMethods(module);
                Assert.AreEqual(6, actual.Length);
                Assert.IsTrue(actual[0].instructions.Any(instruction => instruction.Contains(" method:System.Type System.Reflection.Assembly::InternalGetType")));
                Assert.AreEqual("0000:ldarg.0", actual[2].instructions[0]);
                Assert.IsFalse(actual[3].hasBody);
                Assert.IsEmpty(actual[3].instructions);
                foreach (var field in typeof(M05MethodWitness).GetFields())
                {
                    var claim = ModuleMethods(module);
                    field.SetValue(claim[0], field.FieldType == typeof(bool) ? (object)false : field.FieldType == typeof(int) ? (object)999 : field.FieldType == typeof(string[]) ? (object)new[] { "forged" } : "forged");
                    AssertCode("M05ModuleWitness", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifyWitnesses", claim, actual));
                }
            }
        }

        [Test] public void EveryRequiredLinkedModuleMethodMustSurviveAndRetainNativeShape()
        {
            for (int index = 0; index < 6; ++index)
            using (var module = CoreFixture())
            {
                var witness = ModuleMethods(module)[index];
                var type = module.Find(witness.declaringType, false);
                type.Methods.Remove(type.Methods.Single(method => method.FullName == witness.signature));
                AssertCode("M05ModuleMethods", () => ModuleMethods(module));
            }
            using (var module = CoreFixture())
            {
                module.Find("System.Reflection.RuntimeModule", false).Methods.Single(method => method.Name == "InternalGetTypes").ImplAttributes = 0;
                AssertCode("M05ModuleMethods", () => ModuleMethods(module));
            }
        }

        [Test] public void WrapperBodiesCannotOmitTheirNativeCallsOrAssemblyField()
        {
            foreach (string name in new[] { "GetType", "GetTypes", "get_Assembly" })
            using (var module = CoreFixture())
            {
                var method = module.Find("System.Reflection.RuntimeModule", false).Methods.Single(item => item.Name == name);
                method.Body.Instructions.Clear(); method.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
                AssertCode("M05ModuleMethods", () => ModuleMethods(module));
            }
        }

        [Test] public void RejectedFixtureMustFailTheRealResourceCodeAndCannotLeaveAnArtifact()
        {
            string root = Temp();
            try
            {
                string output = Path.Combine(root, "rejected");
                Action correct = () => { throw new ShadowBuildException("ResourceRebuildRequired", "actual serialized field difference"); };
                var result = (ShadowBuildException)Invoke(typeof(M05Build), "RequireLayoutRejection", correct, output);
                Assert.AreEqual("ResourceRebuildRequired: actual serialized field difference", result.Message);
                Assert.Throws<BuildFailedException>(() => Invoke(typeof(M05Build), "RequireLayoutRejection", (Action)(() => { }), output));
                AssertCode("PolicyRejected", () => Invoke(typeof(M05Build), "RequireLayoutRejection", (Action)(() => { throw new ShadowBuildException("PolicyRejected", "not ABI"); }), output));
                Assert.Throws<BuildFailedException>(() => Invoke(typeof(M05Build), "RequireLayoutRejection", (Action)(() => { Directory.CreateDirectory(output); correct(); }), output));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test] public void ReplayComparesTheEntireArtifactTreeWithoutNondeterminismWaivers()
        {
            string root = Temp();
            try
            {
                string left = Path.Combine(root, "recorded"), right = Path.Combine(root, "replayed");
                Directory.CreateDirectory(left); Directory.CreateDirectory(right);
                File.WriteAllText(Path.Combine(left, "patch-manifest.json"), "{}\n"); File.WriteAllText(Path.Combine(right, "patch-manifest.json"), "{}\n");
                Invoke(typeof(M05EditorValidation), "VerifyArtifactTree", left, right);
                File.WriteAllText(Path.Combine(right, "patch-manifest.json"), "{}");
                Assert.Throws<BuildFailedException>(() => Invoke(typeof(M05EditorValidation), "VerifyArtifactTree", left, right));
                File.WriteAllText(Path.Combine(right, "patch-manifest.json"), "{}\n"); File.WriteAllText(Path.Combine(left, "unlisted.dll"), "unknown");
                Assert.Throws<BuildFailedException>(() => Invoke(typeof(M05EditorValidation), "VerifyArtifactTree", left, right));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test] public void ReplayCannotOverwriteAnExistingReceipt()
        {
            string root = Temp();
            try
            {
                string path = Path.Combine(root, "m05-editor-replay.json"); File.WriteAllText(path, "preserve");
                Assert.Throws<BuildFailedException>(() => M05EditorValidation.ValidateAndWriteReceipt(Path.Combine(root, "absent.json"), path));
                Assert.AreEqual("preserve", File.ReadAllText(path));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test] public void MilestoneDomainsDefinesAndActualProofBoundariesRemainExplicit()
        {
            Assert.AreEqual("m05-stable-aot:1\n", M05Build.StableAotHashDomain);
            Assert.AreNotEqual(M04Build.StableAotHashDomain, M05Build.StableAotHashDomain);
            CollectionAssert.AreEqual(M04Build.ProviderFirstOrder, M05Build.ProviderFirstOrder);
            var p01 = (string[])Invoke(typeof(M05Build), "ExpectedDefines", "P01");
            CollectionAssert.AreEquivalent(new[] { "ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M04", "ASSEMBLY_SHADOW_M05" }, p01);
            var p03 = (string[])Invoke(typeof(M05Build), "ExpectedDefines", "P03");
            CollectionAssert.AreEquivalent(p01.Concat(new[] { "ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M04_P03", "ASSEMBLY_SHADOW_M05_P03" }), p03);
            string build = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M05Build.cs");
            StringAssert.Contains("CompilePatchDlls.VerifySemanticEquivalence", build);
            StringAssert.Contains("M05TypeSchemaVerifier.Capture", build);
            StringAssert.Contains("M04NativeMetadataProof.ReadPlayer", build);
            StringAssert.Contains("dllOnly = true", build);
            StringAssert.Contains("ResourceRebuildRequired", build);
            string replay = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M05EditorValidation.cs");
            StringAssert.Contains("ShadowPatchManifestBuilder.Build", replay);
            StringAssert.Contains("VerifyArtifactTree", replay);
            StringAssert.Contains("M05TypeInventoryProof.Verify", replay);
            StringAssert.Contains("M05TypeSchemaVerifier.Verify", replay);
        }

        [Test] public void ActualBootstrapTypeProofSchemaRetainsNestedListsAndUnsignedCounters()
        {
            using (var before = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var after = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var runtime = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location))
            using (var runtimeAfter = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location))
            {
                var inputs = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", runtime } };
                var linked = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", runtimeAfter } };
                Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, inputs, linked);
                var dto = runtimeAfter.Find("HybridCLR.AssemblyShadowTypeResolutionInfo", false);
                Assert.NotNull(dto);
                Assert.AreEqual(5, dto.Fields.Count(field => field.FieldType.FullName == "System.UInt64"));
                dto.Fields.Remove(dto.Fields.Single(field => field.Name == "definitionCacheHits"));
                AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, inputs, linked));
            }
        }

        [Test] public void EveryActualM05JsonInputHasAnExplicitLinkedSchemaRoot()
        {
            string[] roots = (string[])typeof(M05TypeSchemaVerifier).GetField("BootstrapRoots", BindingFlags.Static | BindingFlags.NonPublic).GetValue(null);
            using (var module = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            {
                var inputs = new HashSet<string>(StringComparer.Ordinal);
                foreach (string name in new[] { "AssemblyShadowDemo.M05TypeProbe", "AssemblyShadowDemo.M05ResourceProbe" })
                {
                    Assert.NotNull(module.Find(name, false), "Compile current M05 Bootstrap before checking its input graph.");
                    foreach (var type in module.GetTypes().Where(type => type.FullName == name || type.FullName.StartsWith(name + "/", StringComparison.Ordinal)))
                    foreach (var method in type.Methods.Where(item => item.HasBody))
                    foreach (var instruction in method.Body.Instructions)
                    {
                        var call = instruction.Operand as MethodSpec;
                        if (call != null && call.Name == "FromJson" && call.DeclaringType.FullName == "UnityEngine.JsonUtility") inputs.Add(call.GenericInstMethodSig.GenericArguments[0].FullName);
                    }
                }
                Assert.GreaterOrEqual(inputs.Count, 7);
                CollectionAssert.Contains(inputs, "AssemblyShadowDemo.M05ResourceProbe/FrozenManifest", "Iterator JSON input must be scanned.");
                CollectionAssert.Contains(inputs, "AssemblyShadowDemo.M05TypeProbe/BaselineManifest");
                CollectionAssert.Contains(inputs, "AssemblyShadowDemo.M05TypeProbe/SnapshotReceipt");
                foreach (string input in inputs) CollectionAssert.Contains(roots, input);
            }
        }

        [Test] public void PrivateBaselineSnapshotAndPatchFieldsHaveExactLinkedClosure()
        {
            using (var before = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var after = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var runtime = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location))
            {
                var external = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", runtime } };
                Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external);
                foreach (string name in new[] { "BaselineManifest", "BaselineAssembly", "SnapshotReceipt", "SnapshotFile", "PatchManifest", "PatchAssembly" })
                {
                    var type = after.Find("AssemblyShadowDemo.M05TypeProbe/" + name, false);
                    Assert.NotNull(type);
                    foreach (var field in type.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray())
                    {
                        int index = type.Fields.IndexOf(field); type.Fields.Remove(field);
                        AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                        type.Fields.Insert(index, field);
                    }
                    var unknown = new FieldDefUser("undeclaredLinkedField", new FieldSig(after.CorLibTypes.Boolean), FieldAttributes.Public);
                    type.Fields.Add(unknown);
                    AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                    type.Fields.Remove(unknown);
                    var parent = type.DeclaringType; int position = parent.NestedTypes.IndexOf(type); parent.NestedTypes.Remove(type);
                    AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                    parent.NestedTypes.Insert(position, type);
                }
            }
        }

        [Test] public void PrivateJsonInputDeclarationsRequireTrustedExplicitPreservation()
        {
            using (var before = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var after = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var runtime = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location))
            {
                var external = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", runtime } };
                foreach (string name in new[] { "BaselineManifest", "BaselineAssembly", "SnapshotReceipt", "SnapshotFile", "PatchManifest", "PatchAssembly" })
                {
                    var type = before.Find("AssemblyShadowDemo.M05TypeProbe/" + name, false);
                    var typePreserve = type.CustomAttributes.Single(attribute => attribute.AttributeType.FullName == "UnityEngine.Scripting.PreserveAttribute");
                    type.CustomAttributes.Remove(typePreserve);
                    AssertCode("M05InputPreservation", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                    type.CustomAttributes.Add(typePreserve);
                    foreach (var field in type.Fields.Where(field => field.IsPublic && !field.IsStatic))
                    {
                        var annotation = field.CustomAttributes.Single(attribute => attribute.AttributeType.FullName == "UnityEngine.Scripting.PreserveAttribute");
                        field.CustomAttributes.Remove(annotation);
                        AssertCode("M05InputPreservation", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                        var fake = new TypeRefUser(before, "UnityEngine.Scripting", "PreserveAttribute", new AssemblyRefUser(new AssemblyNameInfo("Untrusted")));
                        var forged = new CustomAttribute(new MemberRefUser(before, ".ctor", MethodSig.CreateInstance(before.CorLibTypes.Void), fake));
                        field.CustomAttributes.Add(forged);
                        AssertCode("M05InputPreservation", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                        field.CustomAttributes.Remove(forged); field.CustomAttributes.Add(annotation);
                    }
                }
            }
        }

        [Test] public void FrozenResourceFieldsAndIteratorJsonAdmissionRemainStrict()
        {
            using (var before = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var after = ModuleDefMD.Load(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location))
            using (var runtime = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location))
            {
                var external = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", runtime } };
                foreach (string name in new[] { "FrozenManifest", "FrozenBundle", "FrozenAssembly", "FrozenAsset" })
                {
                    var type = after.Find("AssemblyShadowDemo.M05ResourceProbe/" + name, false);
                    Assert.NotNull(type);
                    foreach (var field in type.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray())
                    {
                        int index = type.Fields.IndexOf(field); type.Fields.Remove(field);
                        AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
                        type.Fields.Insert(index, field);
                    }
                }
                var reads = before.GetTypes().Where(type => type.FullName.StartsWith("AssemblyShadowDemo.M05ResourceProbe/", StringComparison.Ordinal))
                    .SelectMany(type => type.Methods).Where(method => method.HasBody).SelectMany(method => method.Body.Instructions)
                    .Select(instruction => instruction.Operand as MethodSpec).Where(call => call != null && call.Name == "FromJson" && call.DeclaringType.FullName == "UnityEngine.JsonUtility").ToArray();
                Assert.AreEqual(1, reads.Length, "The resource manifest is deserialized in the generated iterator body.");
                reads[0].GenericInstMethodSig.GenericArguments[0] = before.CorLibTypes.Object;
                AssertCode("M05TypeSchemaRoot", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifySchemas", before, after, external, external));
            }
        }

        [Test] public void NativeTypeApiAndAllEighteenDiagnosticFieldsFailClosedOnDrift()
        {
            using (var before = RuntimeFixture())
            using (var after = RuntimeFixture())
            {
                Invoke(typeof(M05TypeSchemaVerifier), "VerifyRuntime", before, after);
                var type = after.Find("HybridCLR.AssemblyShadowTypeResolutionInfo", false);
                var fields = type.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray();
                Assert.AreEqual(18, fields.Length);
                foreach (var field in fields)
                {
                    int index = type.Fields.IndexOf(field); type.Fields.Remove(field);
                    AssertCode("M05TypeSchemaMismatch", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifyRuntime", before, after));
                    type.Fields.Insert(index, field);
                }
                var query = after.Find("HybridCLR.AssemblyShadowRuntime", false).Methods.Single(method => method.Name == "GetTypeResolutionInfo");
                query.ImplAttributes = 0;
                AssertCode("M05TypeApi", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifyRuntime", before, after));
                query.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall;
                query.ParamDefs.Single(parameter => parameter.Sequence == 2).Attributes = 0;
                AssertCode("M05TypeApi", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifyRuntime", before, after));
            }
            using (var before = RuntimeFixture())
            using (var after = RuntimeFixture())
            {
                foreach (var module in new[] { before, after }) module.Find("HybridCLR.AssemblyShadowTypeResolutionInfo", false)
                    .Fields.Single(field => field.Name == "guardFailures").FieldSig = new FieldSig(module.CorLibTypes.Int64);
                AssertCode("M05TypeSchemaFields", () => Invoke(typeof(M05TypeSchemaVerifier), "VerifyRuntime", before, after));
            }
        }

        private static ModuleDef RuntimeFixture()
        {
            // Represent the native build branch without executing native calls. The actual
            // Editor branch deliberately throws; this test changes only in-memory metadata.
            var module = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location);
            foreach (var method in module.Find("HybridCLR.AssemblyShadowRuntime", false).Methods.Where(method => method.IsPublic && method.IsStatic))
            {
                method.Body = null; method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall;
            }
            return module;
        }

        private static M05MethodWitness[] ModuleMethods(ModuleDef core) { return (M05MethodWitness[])Invoke(typeof(M05TypeSchemaVerifier), "ReadModuleMethods", core); }
        private static object Invoke(Type type, string name, params object[] args)
        {
            try { return type.GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, args); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }
        private static void AssertCode(string code, TestDelegate action) { Assert.AreEqual(code, Assert.Throws<ShadowBuildException>(action).Code); }
        private static string Temp() { string path = Path.Combine(Path.GetTempPath(), "M05EditorTest-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(path); return path; }

        private sealed class TypeFixture : IDisposable
        {
            private readonly string root = Temp();
            public readonly string Path, Hash;
            public TypeFixture()
            {
                Path = System.IO.Path.Combine(root, "Fixture.dll");
                using (var module = NewModule("Fixture"))
                {
                    var outer = AddType(module, "Outer`1"); outer.GenericParameters.Add(new GenericParamUser(0, 0, "T"));
                    var inner = new TypeDefUser("", "Inner`1", module.CorLibTypes.Object.TypeDefOrRef) { Attributes = TypeAttributes.NestedPublic };
                    outer.NestedTypes.Add(inner); inner.GenericParameters.Add(new GenericParamUser(0, 0, "T")); inner.GenericParameters.Add(new GenericParamUser(1, 0, "U"));
                    var hidden = AddType(module, "Hidden"); hidden.Attributes = TypeAttributes.NotPublic;
                    hidden.NestedTypes.Add(new TypeDefUser("", "PublicChild", module.CorLibTypes.Object.TypeDefOrRef) { Attributes = TypeAttributes.NestedPublic });
                    AddType(module, "IShape").Attributes = TypeAttributes.Public | TypeAttributes.Interface | TypeAttributes.Abstract;
                    AddType(module, "Choice").BaseType = new TypeRefUser(module, "System", "Enum", module.CorLibTypes.AssemblyRef);
                    AddType(module, "Value").BaseType = new TypeRefUser(module, "System", "ValueType", module.CorLibTypes.AssemblyRef);
                    module.Write(Path);
                }
                Hash = ShadowHash.File(Path);
            }
            public M05TypeInventory Read() { return M05TypeInventoryProof.ReadFile(Path, Hash, "Fixture"); }
            public void Dispose() { Directory.Delete(root, true); }
        }
        private static ModuleDefUser NewModule(string name)
        {
            var module = new ModuleDefUser(name + ".dll") { Kind = ModuleKind.Dll, Mvid = Guid.NewGuid() };
            new AssemblyDefUser(name, new Version(0, 0, 0, 0)).Modules.Add(module); return module;
        }
        private static TypeDef AddType(ModuleDef module, string name)
        {
            var type = new TypeDefUser("Fixture", name, module.CorLibTypes.Object.TypeDefOrRef) { Attributes = TypeAttributes.Public };
            module.Types.Add(type); return type;
        }
        private static ModuleDef CoreFixture()
        {
            var module = NewModule("mscorlib");
            var moduleType = AddType(module, "Module"); moduleType.Namespace = "System.Reflection";
            var runtimeModule = AddType(module, "RuntimeModule"); runtimeModule.Namespace = "System.Reflection";
            var runtimeAssembly = AddType(module, "RuntimeAssembly"); runtimeAssembly.Namespace = "System.Reflection";
            var assembly = AddType(module, "Assembly"); assembly.Namespace = "System.Reflection";
            TypeSig type = new ClassSig(new TypeRefUser(module, "System", "Type", module));
            var getType = Method(runtimeModule, "GetType", MethodSig.CreateInstance(type, module.CorLibTypes.String, module.CorLibTypes.Boolean, module.CorLibTypes.Boolean), false);
            var getTypes = Method(runtimeModule, "GetTypes", MethodSig.CreateInstance(new SZArraySig(type)), false);
            var getAssembly = Method(runtimeModule, "get_Assembly", MethodSig.CreateInstance(assembly.ToTypeSig()), false);
            Method(runtimeAssembly, "GetManifestModuleInternal", MethodSig.CreateInstance(moduleType.ToTypeSig()), true);
            var nativeType = Method(assembly, "InternalGetType", MethodSig.CreateInstance(type, moduleType.ToTypeSig(), module.CorLibTypes.String, module.CorLibTypes.Boolean, module.CorLibTypes.Boolean), true);
            var nativeTypes = Method(runtimeModule, "InternalGetTypes", MethodSig.CreateStatic(new SZArraySig(type), module.CorLibTypes.IntPtr), true);
            var field = new FieldDefUser("assembly", new FieldSig(assembly.ToTypeSig()), FieldAttributes.Private); runtimeModule.Fields.Add(field);
            getType.Body.Instructions.Add(Instruction.Create(OpCodes.Callvirt, nativeType)); getType.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
            getTypes.Body.Instructions.Add(Instruction.Create(OpCodes.Call, nativeTypes)); getTypes.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
            getAssembly.Body.Instructions.Add(Instruction.Create(OpCodes.Ldarg_0)); getAssembly.Body.Instructions.Add(Instruction.Create(OpCodes.Ldfld, field)); getAssembly.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
            return module;
        }
        private static MethodDef Method(TypeDef owner, string name, MethodSig signature, bool native)
        {
            var method = new MethodDefUser(name, signature) { Attributes = MethodAttributes.Public | (signature.HasThis ? MethodAttributes.Virtual : MethodAttributes.Static) };
            if (native) method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall;
            else method.Body = new CilBody();
            owner.Methods.Add(method); return method;
        }
    }
}
