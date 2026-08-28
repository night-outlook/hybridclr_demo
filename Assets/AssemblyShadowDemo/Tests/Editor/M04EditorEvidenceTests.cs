using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M04EditorEvidenceTests
    {
        private const string ReferenceJson = "{\"referenceIndex\":0,\"name\":\"netstandard\",\"fullName\":\"netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51\",\"version\":\"2.1.0.0\",\"culture\":\"\",\"publicKeyToken\":\"cc7b13ffcd2ddd51\"}";

        [Test]
        public void DeclaredReferencesPreserveAbsentFacadeVersionsTokensAndRowOrder()
        {
            using (var fixture = new IdentityFixture())
            {
                var actual = fixture.Read();
                Assert.AreEqual("Identity.Fixture", actual.name);
                Assert.AreEqual("9.8.7.6", actual.version);
                Assert.AreEqual("", actual.culture);
                Assert.AreEqual("", actual.publicKeyToken);
                Assert.AreEqual(fixture.Path, actual.path);
                Assert.AreEqual(ShadowHash.File(fixture.Path), actual.sha256);
                Assert.IsFalse(File.Exists(System.IO.Path.Combine(fixture.Root, "netstandard.dll")));
                var facade = actual.referenceIdentities.Single(reference => reference.name == "netstandard");
                Assert.AreEqual("2.1.0.0", facade.version);
                Assert.AreEqual("cc7b13ffcd2ddd51", facade.publicKeyToken);
                Assert.AreEqual("", facade.culture);
                var zeros = actual.referenceIdentities.Single(reference => reference.name == "Zero.Token");
                Assert.AreEqual("0000000000000000", zeros.publicKeyToken, "A declared eight-byte zero token is not absence.");
                Assert.AreEqual("fr-FR", zeros.culture);
                using (var module = ModuleDefMD.Load(fixture.Path))
                {
                    Assert.AreEqual(module.Mvid.ToString(), actual.mvid);
                    Assert.AreEqual(module.GetAssemblyRefs().Select(reference => reference.FullName).ToArray(), actual.referenceIdentities.Select(reference => reference.fullName).ToArray());
                    Assert.AreEqual(Enumerable.Range(0, actual.referenceIdentities.Length).ToArray(), actual.referenceIdentities.Select(reference => reference.referenceIndex).ToArray());
                }
                Assert.DoesNotThrow(() => M04AssemblyIdentityProof.Verify(new[] { actual }, new[] { fixture.Read() }));
            }
        }

        [Test]
        public void EveryAssemblyAndReferenceIdentityFieldIsRecomputed()
        {
            using (var fixture = new IdentityFixture())
            {
                foreach (FieldInfo field in typeof(M04AssemblyIdentity).GetFields().Where(field => field.FieldType == typeof(string)))
                {
                    var claimed = fixture.Read();
                    field.SetValue(claimed, "tampered");
                    AssertCode("M04IdentityEvidenceMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                }
                foreach (FieldInfo field in typeof(M04AssemblyReferenceIdentity).GetFields())
                {
                    var claimed = fixture.Read();
                    field.SetValue(claimed.referenceIdentities[0], field.FieldType == typeof(int) ? (object)99 : "tampered");
                    AssertCode("M04ReferenceIdentityMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                }
            }
        }

        [Test]
        public void ProviderSubstitutionMissingRowsReorderingAndRelativePathsAreRejected()
        {
            using (var fixture = new IdentityFixture())
            {
                var claimed = fixture.Read();
                var facade = claimed.referenceIdentities.Single(reference => reference.name == "netstandard");
                facade.name = "mscorlib";
                AssertCode("M04ReferenceIdentityMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                claimed = fixture.Read(); claimed.referenceIdentities = claimed.referenceIdentities.Skip(1).ToArray();
                AssertCode("M04IdentityEvidenceMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                claimed = fixture.Read(); Array.Reverse(claimed.referenceIdentities);
                AssertCode("M04ReferenceIdentityMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                claimed = fixture.Read(); claimed.path = "Identity.Fixture.dll";
                AssertCode("M04IdentityEvidenceMismatch", () => M04AssemblyIdentityProof.Verify(new[] { claimed }, new[] { fixture.Read() }));
                AssertCode("M04IdentityBytesChanged", () => M04AssemblyIdentityProof.ReadFile(fixture.Path, new string('0', 64), "Identity.Fixture"));
                AssertCode("M04IdentityAssemblyMismatch", () => M04AssemblyIdentityProof.ReadFile(fixture.Path, ShadowHash.File(fixture.Path), "Wrong.Assembly"));
            }
        }

        [Test]
        public void CanonicalLinkedFilenameStillReportsDeclaredAssemblyCasing()
        {
            using (var fixture = new IdentityFixture())
                Assert.AreEqual("Identity.Fixture", M04AssemblyIdentityProof.ReadFile(fixture.Path, ShadowHash.File(fixture.Path), "identity.fixture").name);
        }

        [Test]
        public void MissingZeroIndexAndOtherRawIdentityMembersAreRejected()
        {
            Assert.DoesNotThrow(() => M04JsonEvidence.ValidateSchema<M04AssemblyReferenceIdentity>(ReferenceJson));
            foreach (string missing in new[] {
                ReferenceJson.Replace("\"referenceIndex\":0,", ""),
                ReferenceJson.Replace("\"culture\":\"\",", ""),
                ReferenceJson.Replace(",\"publicKeyToken\":\"cc7b13ffcd2ddd51\"", ""),
                ReferenceJson.Replace("\"referenceIndex\":0", "\"referenceIndex\":false"),
                ReferenceJson.Replace("\"referenceIndex\":0", "\"referenceIndex\":0.0"),
                ReferenceJson.Replace("\"referenceIndex\":0", "\"referenceIndex\":2147483648"),
                ReferenceJson.Replace("\"referenceIndex\":0", "\"referenceIndex\":0,\"referenceIndex\":0"),
                ReferenceJson.Replace("\"culture\":\"\"", "\"culture\":null"),
                ReferenceJson.Replace("\"culture\":\"\"", "\"culture\":\"\",\"extra\":true"),
                ReferenceJson + "{}", "[]", "null", "{" })
                AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<M04AssemblyReferenceIdentity>(missing));
        }

        [Test]
        public void TypedFalseDoesNotStandInForAMissingRawBoolean()
        {
            Assert.DoesNotThrow(() => M04JsonEvidence.ValidateSchema<BooleanEvidence>("{\"observed\":false}"));
            AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<BooleanEvidence>("{}"));
        }

        [Test]
        public void PlaceholderNamesComeOnlyFromOneUnambiguousGeneratedRegion()
        {
            string valid = "//!!!{{PLACE_HOLDER\n\t\t\"AssemblyShadowBaseline.HotUpdate\",\n//!!!}}PLACE_HOLDER\n";
            Assert.AreEqual(new[] { "AssemblyShadowBaseline.HotUpdate" }, M04PlaceholderManifestProof.Parse(System.Text.Encoding.UTF8.GetBytes(valid)));
            foreach (string invalid in new[] { "", valid + valid, valid.Replace("//!!!}}PLACE_HOLDER", ""),
                valid.Replace("\"AssemblyShadowBaseline.HotUpdate\",", "nullptr,"),
                valid.Replace("\"AssemblyShadowBaseline.HotUpdate\",", "\"path/AssemblyShadowBaseline.HotUpdate\","),
                valid.Replace("\"AssemblyShadowBaseline.HotUpdate\",", "\"A\",\n\"a\","),
                "//!!!{{PLACE_HOLDER\n//!!!}}PLACE_HOLDER" })
                AssertCode("M04PlaceholderManifestSchema", () => M04PlaceholderManifestProof.Parse(System.Text.Encoding.UTF8.GetBytes(invalid)));
        }

        [Test]
        public void SchemaPreservesEveryNestedFieldRegardlessOfItsDefaultValue()
        {
            using (var fixture = new SchemaFixture())
            {
                fixture.Linked.Mvid = Guid.NewGuid();
                Assert.DoesNotThrow(fixture.Verify);
            }
            using (var reference = new SchemaFixture())
            foreach (TypeDef type in reference.Input.GetTypes().Where(type => type.IsSerializable))
            foreach (FieldDef field in type.Fields.Where(field => field.IsPublic && !field.IsStatic))
            using (var fixture = new SchemaFixture())
            {
                TypeDef linked = fixture.Linked.Find(type.FullName, false);
                linked.Fields.Remove(linked.Fields.Single(candidate => candidate.Name == field.Name));
                AssertCode("M04DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void ChangedSchemaFlagsTypesExtraFieldsAndMissingRootsAreRejected()
        {
            foreach (string mutation in new[] { "bool-type", "static", "nonserialized", "extra", "missing-root" })
            using (var fixture = new SchemaFixture())
            {
                TypeDef type = fixture.Linked.Find("AssemblyShadowDemo.M04ReferenceProbe/Result", false);
                FieldDef field = type.Fields.Single(candidate => candidate.Name == "observed");
                if (mutation == "bool-type") field.FieldSig = new FieldSig(fixture.Linked.CorLibTypes.Int32);
                else if (mutation == "static") field.IsStatic = true;
                else if (mutation == "nonserialized") field.IsNotSerialized = true;
                else if (mutation == "extra") type.Fields.Add(new FieldDefUser("unexpected", new FieldSig(fixture.Linked.CorLibTypes.Boolean), dnlib.DotNet.FieldAttributes.Public));
                else type.DeclaringType.NestedTypes.Remove(type);
                AssertCode("M04DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void ListsTraverseNestedDtoFieldsAndRejectLostNestedEvidence()
        {
            foreach (string mutation in new[] { "field", "type", "list-field" })
            using (var fixture = new SchemaFixture())
            {
                SchemaFixture.AddList(fixture.Input); SchemaFixture.AddList(fixture.Linked);
                Assert.DoesNotThrow(fixture.Verify);
                TypeDef child = fixture.Linked.Find("AssemblyShadowDemo.M04ReferenceProbe/ListPayload", false);
                if (mutation == "field") child.Fields.Clear();
                else if (mutation == "type") child.DeclaringType.NestedTypes.Remove(child);
                else
                {
                    TypeDef root = fixture.Linked.Find("AssemblyShadowDemo.M04ReferenceProbe/Result", false);
                    root.Fields.Remove(root.Fields.Single(field => field.Name == "listPayload"));
                }
                AssertCode("M04DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void OnlyClosedSingleArgumentCoreLibraryListsAreSupported()
        {
            foreach (string mutation in new[] { "generic-name", "argument-count", "open-argument", "foreign-owner", "spoofed-core-owner" })
            using (var fixture = new SchemaFixture())
            {
                foreach (ModuleDef module in new[] { fixture.Input, fixture.Linked })
                {
                    GenericInstSig list = SchemaFixture.AddList(module);
                    var type = (TypeRef)list.GenericType.TypeDefOrRef;
                    if (mutation == "generic-name") type.Name = "HashSet`1";
                    else if (mutation == "argument-count") list.GenericArguments.Add(module.CorLibTypes.String);
                    else if (mutation == "open-argument") list.GenericArguments[0] = new GenericVar(0);
                    else
                    {
                        var scope = new AssemblyRefUser(new AssemblyNameInfo(module.CorLibTypes.AssemblyRef.FullName));
                        if (mutation == "foreign-owner") scope.Name = "Foreign.CoreLibrary";
                        else scope.PublicKeyOrToken = new PublicKeyToken("0011223344556677");
                        type.ResolutionScope = scope;
                    }
                }
                AssertCode("M04DiagnosticSchemaUnsupported", fixture.Verify);
            }
        }

        [Test]
        public void LinkedListOwnerCannotHideBehindCoreLibrarySignatureEquivalence()
        {
            using (var fixture = new SchemaFixture())
            {
                SchemaFixture.AddList(fixture.Input);
                GenericInstSig list = SchemaFixture.AddList(fixture.Linked);
                var scope = new AssemblyRefUser(new AssemblyNameInfo(fixture.Linked.CorLibTypes.AssemblyRef.FullName));
                scope.Version = new Version(99, 0, 0, 0);
                ((TypeRef)list.GenericType.TypeDefOrRef).ResolutionScope = scope;
                AssertCode("M04DiagnosticSchemaUnsupported", fixture.Verify);
            }
        }

        [Test]
        public void ArraysAndListsCanWrapCapturedDtosWithoutSkippingTheDto()
        {
            using (var fixture = new SchemaFixture())
            {
                foreach (ModuleDef module in new[] { fixture.Input, fixture.Linked })
                {
                    GenericInstSig list = SchemaFixture.AddList(module);
                    list.GenericArguments[0] = new SZArraySig(list.GenericArguments[0]);
                    FieldDef field = module.Find("AssemblyShadowDemo.M04ReferenceProbe/Result", false).Fields.Single(candidate => candidate.Name == "listPayload");
                    field.FieldSig = new FieldSig(new SZArraySig(list));
                }
                Assert.DoesNotThrow(fixture.Verify);
                fixture.Linked.Find("AssemblyShadowDemo.M04ReferenceProbe/ListPayload", false).Fields.Clear();
                AssertCode("M04DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void M03DoesNotAcquireM04ListAdmission()
        {
            byte[] bytes = File.ReadAllBytes(Assembly.Load("HybridCLR.Runtime").Location);
            using (var input = ModuleDefMD.Load(bytes))
            using (var linked = ModuleDefMD.Load(bytes))
            {
                foreach (ModuleDef module in new[] { input, linked })
                {
                    var list = new GenericInstSig(new ClassSig(new TypeRefUser(module, "System.Collections.Generic", "List`1", module.CorLibTypes.AssemblyRef)), module.CorLibTypes.String);
                    module.Find("HybridCLR.AssemblyShadowDiagnostics", false).Fields.Add(new FieldDefUser("futureList", new FieldSig(list), dnlib.DotNet.FieldAttributes.Public));
                }
                var method = typeof(M03DiagnosticSchemaVerifier).GetMethod("VerifyModules", BindingFlags.Static | BindingFlags.NonPublic);
                var error = Assert.Throws<TargetInvocationException>(() => method.Invoke(null, new object[] { input, linked }));
                Assert.AreEqual("M03DiagnosticSchemaUnsupported", ((ShadowBuildException)error.InnerException).Code);
            }
        }

        [Test]
        public void CapturedExternalNativeDtoIsComparedAndUncapturedProviderIsRejected()
        {
            using (var fixture = new SchemaFixture())
            using (var nativeInput = SchemaFixture.NativeModule())
            using (var nativeLinked = SchemaFixture.NativeModule())
            {
                foreach (ModuleDef module in new[] { fixture.Input, fixture.Linked })
                {
                    var reference = new AssemblyRefUser(nativeInput.Assembly);
                    var type = new TypeRefUser(module, "HybridCLR", "NativeEvidence", reference);
                    module.Find("AssemblyShadowDemo.M04ReferenceProbe/Result", false).Fields.Add(
                        new FieldDefUser("native", new FieldSig(new ClassSig(type)), dnlib.DotNet.FieldAttributes.Public));
                }
                AssertCode("M04DiagnosticSchemaUnsupported", fixture.Verify);
                var inputs = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", nativeInput } };
                var linked = new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", nativeLinked } };
                Assert.DoesNotThrow(() => fixture.VerifyExternal(inputs, linked));
                nativeLinked.Find("HybridCLR.NativeEvidence", false).Fields.Clear();
                AssertCode("M04DiagnosticSchemaMismatch", () => fixture.VerifyExternal(inputs, linked));
            }
        }

        [Test]
        public void ReplayRefusesToOverwriteExistingEvidence()
        {
            string root = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "M04ReplayTest-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            string receipt = System.IO.Path.Combine(root, "m04-editor-replay.json");
            try
            {
                File.WriteAllText(receipt, "retained-evidence");
                var error = Assert.Catch(() => M04EditorValidation.ValidateAndWriteReceipt(System.IO.Path.Combine(root, "missing.json"), receipt));
                StringAssert.Contains("M04 replay receipt already exists", error.Message);
                Assert.AreEqual("retained-evidence", File.ReadAllText(receipt));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void BuildAndReplayKeepMilestoneBoundariesAndActualProofCalls()
        {
            string build = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M04Build.cs");
            string replay = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M04EditorValidation.cs");
            StringAssert.Contains("M04DiagnosticSchemaVerifier.Verify(snapshot, captured)", build);
            StringAssert.Contains("M04AssemblyIdentityProof.ReadLinked(snapshot, captured)", build);
            StringAssert.Contains("M04AssemblyIdentityProof.ReadPatch(artifact, patch)", build);
            StringAssert.Contains("M04EditorValidation.ValidateAndWriteReceipt(path)", build);
            StringAssert.Contains("VerifiedLinkedRuntimeReferences.Verify", replay);
            StringAssert.Contains("ShadowReflectionBindingEvidence.ValidateCompiled", replay);
            StringAssert.Contains("AssemblyReferenceGraph.DetectChangedRoots", replay);
            StringAssert.Contains("graph.ReverseClosure(roots)", replay);
            StringAssert.Contains("CompilePatchDlls.VerifySemanticEquivalence", replay);
            StringAssert.Contains("ShadowResourceBaseline.ReadAndVerify", replay);
            StringAssert.Contains("M04AssemblyIdentityProof.Verify(fixture.assemblyIdentities", replay);
            StringAssert.Contains("FileMode.CreateNew", replay);
            StringAssert.Contains("FileMode.CreateNew", File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M04AssemblyIdentityProof.cs"));
            StringAssert.Contains("manifest.milestone == \"M03\"", File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs"));
            Assert.AreEqual("m04-stable-aot:1\n", M04Build.StableAotHashDomain);
            CollectionAssert.AreEqual(M03Build.ProviderFirstOrder, M04Build.ProviderFirstOrder);
            CollectionAssert.AreEquivalent(new[] { "ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M04" }, Defines("P01"));
            CollectionAssert.AreEquivalent(new[] { "ASSEMBLY_SHADOW_M03_INITIALIZERS", "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M04",
                "ASSEMBLY_SHADOW_M03_P03", "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M04_P03" }, Defines("P03"));
        }

        [Test]
        public void ActualBootstrapDtoSchemaSurvivesAnUnstrippedMetadataRoundtrip()
        {
            byte[] bytes = File.ReadAllBytes(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location);
            byte[] native = File.ReadAllBytes(Assembly.Load("HybridCLR.Runtime").Location);
            using (var before = ModuleDefMD.Load(bytes))
            using (var after = ModuleDefMD.Load(bytes))
            using (var nativeBefore = ModuleDefMD.Load(native))
            using (var nativeAfter = ModuleDefMD.Load(native))
            {
                after.Mvid = Guid.NewGuid();
                InvokeSchema(before, after, new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", nativeBefore } },
                    new Dictionary<string, ModuleDef> { { "HybridCLR.Runtime", nativeAfter } });
            }
        }

        [Test]
        public void EveryM04JsonInputHasAnExplicitCapturedSchemaRoot()
        {
            var roots = (string[])typeof(M04DiagnosticSchemaVerifier).GetField("BootstrapRoots", BindingFlags.Static | BindingFlags.NonPublic).GetValue(null);
            using (var module = ModuleDefMD.Load(File.ReadAllBytes(Assembly.Load("AssemblyShadowDemo.Bootstrap").Location)))
            {
                var inputs = new HashSet<string>(StringComparer.Ordinal);
                foreach (string probe in new[] { "AssemblyShadowDemo.M04ReferenceProbe", "AssemblyShadowDemo.M04OrdinaryAssemblyProbe" })
                {
                    TypeDef type = module.Find(probe, false);
                    Assert.NotNull(type, "Compile the actual M04 Bootstrap before validating its JSON entrypoints.");
                    foreach (MethodDef method in type.Methods.Where(method => method.HasBody))
                    foreach (var instruction in method.Body.Instructions)
                    {
                        var call = instruction.Operand as MethodSpec;
                        if (call == null || call.Name != "FromJson" || call.DeclaringType.FullName != "UnityEngine.JsonUtility") continue;
                        Assert.AreEqual(1, call.GenericInstMethodSig.GenericArguments.Count);
                        inputs.Add(call.GenericInstMethodSig.GenericArguments[0].FullName);
                    }
                }
                Assert.GreaterOrEqual(inputs.Count, 5, "Both M04 probes must have their expected JSON input entrypoints.");
                foreach (string input in inputs) CollectionAssert.Contains(roots, input, "New JsonUtility input DTO needs an explicit linked-schema root.");
            }
        }

        private static string[] Defines(string patchId)
        {
            return (string[])typeof(M04Build).GetMethod("ExpectedDefines", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, new object[] { patchId });
        }

        private static void AssertCode(string code, TestDelegate action)
        {
            Assert.AreEqual(code, Assert.Throws<ShadowBuildException>(action).Code);
        }

        private static void InvokeSchema(ModuleDef input, ModuleDef linked, IDictionary<string, ModuleDef> inputs, IDictionary<string, ModuleDef> linkedModules)
        {
            try { typeof(M04DiagnosticSchemaVerifier).GetMethod("VerifyModules", BindingFlags.Static | BindingFlags.NonPublic).Invoke(null, new object[] { input, linked, inputs, linkedModules }); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }

        [Serializable] private sealed class BooleanEvidence { public bool observed; }

        private sealed class IdentityFixture : IDisposable
        {
            public readonly string Root = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "M04IdentityTest-" + Guid.NewGuid().ToString("N"));
            public string Path { get { return System.IO.Path.Combine(Root, "Identity.Fixture.dll"); } }
            public IdentityFixture()
            {
                Directory.CreateDirectory(Root);
                using (var module = new ModuleDefUser("Identity.Fixture.dll") { Kind = ModuleKind.Dll, Mvid = Guid.NewGuid() })
                {
                    new AssemblyDefUser("Identity.Fixture", new Version(9, 8, 7, 6)).Modules.Add(module);
                    var type = new TypeDefUser("Fixture", "Consumer", module.CorLibTypes.Object.TypeDefOrRef);
                    module.Types.Add(type);
                    foreach (string identity in new[] { "netstandard, Version=2.1.0.0, Culture=neutral, PublicKeyToken=cc7b13ffcd2ddd51", "Zero.Token, Version=3.2.1.0, Culture=fr-FR, PublicKeyToken=0000000000000000" })
                    {
                        var reference = new AssemblyRefUser(new AssemblyNameInfo(identity));
                        type.Fields.Add(new FieldDefUser(reference.Name, new FieldSig(new ClassSig(new TypeRefUser(module, "Fixture", "Dependency", reference))), dnlib.DotNet.FieldAttributes.Public));
                    }
                    module.Write(Path);
                }
            }
            public M04AssemblyIdentity Read() { return M04AssemblyIdentityProof.ReadFile(Path, ShadowHash.File(Path), "Identity.Fixture"); }
            public void Dispose() { Directory.Delete(Root, true); }
        }

        private sealed class SchemaFixture : IDisposable
        {
            public readonly ModuleDef Input = Create(), Linked = Create();
            public void Verify() { InvokeSchema(Input, Linked, null, null); }
            public void VerifyExternal(IDictionary<string, ModuleDef> input, IDictionary<string, ModuleDef> linked) { InvokeSchema(Input, Linked, input, linked); }
            public void Dispose() { Input.Dispose(); Linked.Dispose(); }

            public static GenericInstSig AddList(ModuleDef module)
            {
                TypeDef parent = module.Find("AssemblyShadowDemo.M04ReferenceProbe", false);
                TypeDef payload = Nested(module, parent, "ListPayload");
                payload.Fields.Add(new FieldDefUser("observed", new FieldSig(module.CorLibTypes.Boolean), dnlib.DotNet.FieldAttributes.Public));
                var scope = new AssemblyRefUser(new AssemblyNameInfo(module.CorLibTypes.AssemblyRef.FullName));
                var list = new GenericInstSig(new ClassSig(new TypeRefUser(module, "System.Collections.Generic", "List`1", scope)), payload.ToTypeSig());
                module.Find("AssemblyShadowDemo.M04ReferenceProbe/Result", false).Fields.Add(new FieldDefUser("listPayload", new FieldSig(list), dnlib.DotNet.FieldAttributes.Public));
                return list;
            }

            private static ModuleDef Create()
            {
                var module = NewModule("AssemblyShadowDemo.Bootstrap");
                var probe = new TypeDefUser("AssemblyShadowDemo", "M04ReferenceProbe", module.CorLibTypes.Object.TypeDefOrRef);
                var ordinary = new TypeDefUser("AssemblyShadowDemo", "M04OrdinaryAssemblyProbe", module.CorLibTypes.Object.TypeDefOrRef);
                module.Types.Add(probe); module.Types.Add(ordinary);
                var reference = Nested(module, probe, "ReferenceIdentity");
                reference.Fields.Add(new FieldDefUser("referenceIndex", new FieldSig(module.CorLibTypes.Int32), dnlib.DotNet.FieldAttributes.Public));
                reference.Fields.Add(new FieldDefUser("publicKeyToken", new FieldSig(module.CorLibTypes.String), dnlib.DotNet.FieldAttributes.Public));
                foreach (var parent in new[] { probe, ordinary })
                foreach (string name in parent == probe ? new[] { "Result", "FixtureManifest", "PlayerBuildReceipt", "PatchManifest", "BaselineManifest" } : new[] { "Result", "Configuration", "Site" })
                {
                    var root = Nested(module, parent, name);
                    root.Fields.Add(new FieldDefUser("observed", new FieldSig(module.CorLibTypes.Boolean), dnlib.DotNet.FieldAttributes.Public));
                    root.Fields.Add(new FieldDefUser("references", new FieldSig(new SZArraySig(reference.ToTypeSig())), dnlib.DotNet.FieldAttributes.Public));
                }
                return module;
            }

            public static ModuleDef NativeModule()
            {
                var module = NewModule("HybridCLR.Runtime");
                var dto = new TypeDefUser("HybridCLR", "NativeEvidence", module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.Public | dnlib.DotNet.TypeAttributes.Serializable };
                dto.Fields.Add(new FieldDefUser("enabled", new FieldSig(module.CorLibTypes.Boolean), dnlib.DotNet.FieldAttributes.Public));
                module.Types.Add(dto); return module;
            }

            private static ModuleDef NewModule(string name)
            {
                var module = new ModuleDefUser(name + ".dll") { Kind = ModuleKind.Dll, Mvid = Guid.NewGuid() };
                new AssemblyDefUser(name, new Version(0, 0, 0, 0)).Modules.Add(module); return module;
            }

            private static TypeDef Nested(ModuleDef module, TypeDef parent, string name)
            {
                var type = new TypeDefUser("", name, module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.NestedPublic | dnlib.DotNet.TypeAttributes.Serializable };
                parent.NestedTypes.Add(type); return type;
            }
        }
    }
}
