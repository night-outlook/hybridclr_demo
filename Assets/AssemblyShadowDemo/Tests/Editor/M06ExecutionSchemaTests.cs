using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization.Json;
using System.Text;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using dnlib.DotNet.Pdb;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06ExecutionSchemaTests
    {
        private const string Root = "HybridCLR.AssemblyShadowExecutionDiagnostics";
        private const string Row = "HybridCLR.AssemblyShadowExecutionClassInfo";
        private const string M05Root = "HybridCLR.AssemblyShadowDiagnostics";
        private const string M05Row = "HybridCLR.AssemblyShadowDiagnosticAssembly";
        private const string Capacity = "HybridCLR.AssemblyShadowMetadataCapacity";
        private const string Allocation = "HybridCLR.AssemblyShadowMetadataAllocation";
        private const string Recovery = "HybridCLR.AssemblyShadowRecoveryInfo";

        [Test] public void ActualExecutionDtosAndExactNativeSignaturesSurviveDifferentMvids()
        {
            using (var fixture = new RuntimeFixture())
            {
                fixture.Linked.Mvid = Guid.NewGuid();
                Assert.DoesNotThrow(fixture.Verify);
            }
        }

        [Test] public void EveryExecutionDiagnosticFieldMustSurviveLinking()
        {
            using (var names = new RuntimeFixture())
                foreach (string typeName in new[] { Root, Row })
                    foreach (string fieldName in names.Input.Find(typeName, false).Fields.Where(field => field.IsPublic && !field.IsStatic).Select(field => field.Name.String))
                        using (var fixture = new RuntimeFixture())
                        {
                            TypeDef type = fixture.Linked.Find(typeName, false);
                            type.Fields.Remove(type.Fields.Single(field => field.Name == fieldName));
                            AssertCode("M06ExecutionSchemaMismatch", fixture.Verify);
                        }
        }

        [Test] public void MatchingButUndeclaredExpansionAndSignedCountersAreRejected()
        {
            foreach (string mutation in new[] { "extra", "signed", "row-extra", "row-flag" })
                using (var fixture = new RuntimeFixture())
                {
                    foreach (ModuleDef module in new[] { fixture.Input, fixture.Linked })
                    {
                        TypeDef type = module.Find(mutation.StartsWith("row", StringComparison.Ordinal) ? Row : Root, false);
                        if (mutation.EndsWith("extra", StringComparison.Ordinal))
                            type.Fields.Add(new FieldDefUser("undeclared", new FieldSig(module.CorLibTypes.Int32), dnlib.DotNet.FieldAttributes.Public));
                        else if (mutation == "signed") type.Fields.Single(field => field.Name == "methodChecks").FieldSig = new FieldSig(module.CorLibTypes.Int64);
                        else type.Fields.Single(field => field.Name == "isActive").FieldSig = new FieldSig(module.CorLibTypes.Int32);
                    }
                    AssertCode("M06ExecutionFields", fixture.Verify);
                }
        }

        [Test] public void NativeApiInventoryRejectsMissingExtraManagedAndNonOutOperations()
        {
            foreach (string mutation in new[] { "missing", "extra", "managed", "non-out", "wrong-return" })
                using (var fixture = new RuntimeFixture())
                {
                    var type = fixture.Linked.Find("HybridCLR.AssemblyShadowRuntime", false);
                    var method = type.Methods.Single(candidate => candidate.Name == "GetExecutionDiagnosticsJson");
                    if (mutation == "missing") type.Methods.Remove(method);
                    else if (mutation == "extra") type.Methods.Add(new MethodDefUser("Unexpected",
                        MethodSig.CreateStatic(fixture.Linked.CorLibTypes.Void), dnlib.DotNet.MethodAttributes.Public | dnlib.DotNet.MethodAttributes.Static));
                    else if (mutation == "managed") { method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.IL; method.Body = new CilBody(); method.Body.Instructions.Add(OpCodes.Ret.ToInstruction()); }
                    else if (mutation == "non-out") method.ParamDefs.Single(parameter => parameter.Sequence == 1).IsOut = false;
                    else method.MethodSig.RetType = fixture.Linked.CorLibTypes.Int32;
                    AssertCode("M06ExecutionApi", fixture.Verify);
                }
        }

        [Test] public void NegotiatedApiInventoryRejectsMissingMalformedAndExtraNativeEntries()
        {
            foreach (string mutation in new[] { "missing-public", "missing-private", "private-managed", "private-extra", "wrapper-native", "capacity-non-out" })
                using (var fixture = new RuntimeFixture())
                {
                    var type = fixture.Linked.Find("HybridCLR.AssemblyShadowRuntime", false);
                    var wrapper = type.Methods.Single(candidate => candidate.Name == "GetMetadataCapacityJson");
                    if (mutation == "missing-public") type.Methods.Remove(wrapper);
                    else if (mutation == "missing-private") type.Methods.Remove(type.Methods.Single(candidate => candidate.Name == "GetMetadataCapacityJsonInternal"));
                    else if (mutation == "private-managed")
                    {
                        var method = type.Methods.Single(candidate => candidate.Name == "GetMetadataCapacityJsonInternal");
                        method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.IL; method.Body = new CilBody(); method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
                    }
                    else if (mutation == "private-extra") type.Methods.Add(new MethodDefUser("UnexpectedInternal", wrapper.MethodSig,
                        dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static) { ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall });
                    else if (mutation == "wrapper-native") { wrapper.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall; wrapper.Body = null; }
                    else wrapper.ParamDefs.Single(parameter => parameter.Sequence == 2).IsOut = false;
                    AssertCode("M06ExecutionApi", fixture.Verify);
                }
        }

        [Test] public void EveryStableExecutionErrorCodeRejectsRenumbering()
        {
            for (int value = 0; value < 22; ++value)
                using (var fixture = new RuntimeFixture())
                {
                    var field = fixture.Linked.Find("HybridCLR.AssemblyShadowErrorCode", false).Fields.Single(candidate => candidate.IsLiteral && (int)candidate.Constant.Value == value);
                    field.Constant = new ConstantUser(value + 100);
                    AssertCode("M06ExecutionErrorCodes", fixture.Verify);
                }
        }

        [Test] public void R01ErrorCodesAreAdditiveAfterTheLegacyRange()
        {
            using (var fixture = new RuntimeFixture())
            {
                var code = fixture.Linked.Find("HybridCLR.AssemblyShadowErrorCode", false);
                foreach (int value in new[] { 22, 23, 24 })
                {
                    var field = code.Fields.Single(candidate => candidate.IsLiteral && (int)candidate.Constant.Value == value);
                    field.Constant = new ConstantUser(value + 100);
                    AssertCode("M06ExecutionErrorCodes", fixture.Verify);
                    field.Constant = new ConstantUser(value);
                }
            }
        }

        [Test] public void NewSourceDtosRequireTrustedTypeAndFieldPreservation()
        {
            foreach (string typeName in new[] { Root, Row, Capacity, Allocation, Recovery })
                foreach (bool removeType in new[] { false, true })
                    using (var fixture = new RuntimeFixture())
                    {
                        var type = fixture.Input.Find(typeName, false);
                        if (removeType) type.CustomAttributes.Clear();
                        else type.Fields.First(field => field.IsPublic && !field.IsStatic).CustomAttributes.Clear();
                        AssertCode("M06ExecutionPreserve", fixture.Verify);
                    }
        }

        [Test] public void LinkerMayConsumePreserveAttributesButNotActualFields()
        {
            using (var fixture = new RuntimeFixture())
            {
                foreach (string name in new[] { Root, Row, Capacity, Allocation, Recovery })
                {
                    TypeDef type = fixture.Linked.Find(name, false);
                    type.CustomAttributes.Clear();
                    foreach (var field in type.Fields) field.CustomAttributes.Clear();
                }
                Assert.DoesNotThrow(fixture.Verify);
            }
        }

        [Test] public void NegotiatedDtosRejectMissingExtraAndWrongTypedFields()
        {
            foreach (string mutation in new[] { "capacity-missing", "capacity-extra", "capacity-wrong", "allocation-missing", "recovery-missing", "recovery-wrong" })
                using (var fixture = new RuntimeFixture())
                {
                    TypeDef type = fixture.Linked.Find(mutation.StartsWith("capacity", StringComparison.Ordinal) ? Capacity :
                        mutation.StartsWith("allocation", StringComparison.Ordinal) ? Allocation : Recovery, false);
                    if (mutation == "capacity-missing" || mutation == "allocation-missing" || mutation == "recovery-missing")
                        type.Fields.Remove(type.Fields.First(field => field.IsPublic && !field.IsStatic));
                    else if (mutation == "capacity-extra") type.Fields.Add(new FieldDefUser("undeclared", new FieldSig(fixture.Linked.CorLibTypes.Int32), dnlib.DotNet.FieldAttributes.Public));
                    else if (mutation == "capacity-wrong") type.Fields.Single(field => field.Name == "ordinaryAllocatedCount").FieldSig = new FieldSig(fixture.Linked.CorLibTypes.Int64);
                    else if (mutation == "recovery-wrong") type.Fields.Single(field => field.Name == "retainedBytes").FieldSig = new FieldSig(fixture.Linked.CorLibTypes.Int64);
                    AssertCode("M06ExecutionSchemaMismatch", fixture.Verify);
                }
        }

        [Test] public void WrongRuntimeAssemblyIdentityIsRejected()
        {
            using (var fixture = new RuntimeFixture())
            {
                fixture.Linked.Assembly.Name = "Impostor.Runtime";
                AssertCode("M06ExecutionRuntimeIdentity", fixture.Verify);
            }
        }

        [Test] public void AcceptedM05BytesResolveTheActualLinkedFrameworkIdentity()
        {
            using (var fixture = new M05LinkedSchemaFixture())
            {
                FieldDef input = fixture.Source.Find(M05Root, false).Fields.Single(field => field.Name == "schemaVersion");
                FieldDef linked = fixture.LinkedRuntime.Find(M05Root, false).Fields.Single(field => field.Name == "schemaVersion");
                StringAssert.Contains(", netstandard,", input.FieldType.AssemblyQualifiedName);
                StringAssert.Contains(", mscorlib,", linked.FieldType.AssemblyQualifiedName);
                Assert.IsNotNull(fixture.CompilerNetstandard.Find("System.Int32", false));

                string inputResolved = (string)Invoke("ResolvedSchemaFieldType", input, fixture.Modules);
                string linkedResolved = (string)Invoke("ResolvedSchemaFieldType", linked, fixture.Modules);
                Assert.AreEqual(linked.FieldType.AssemblyQualifiedName, inputResolved);
                Assert.AreEqual(linkedResolved, inputResolved);
                StringAssert.Contains(", mscorlib,", inputResolved);

                FieldDef inputAssemblies = fixture.Source.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                FieldDef linkedAssemblies = fixture.LinkedRuntime.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                Assert.AreEqual(linkedAssemblies.FieldType.AssemblyQualifiedName,
                    (string)Invoke("ResolvedSchemaFieldType", inputAssemblies, fixture.Modules));
            }
        }

        [Test] public void LinkedSchemaResolutionRecursesThroughListAndArrayDefinitions()
        {
            using (var fixture = new M05LinkedSchemaFixture())
            {
                FieldDef input = fixture.Source.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                FieldDef linked = fixture.LinkedRuntime.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                TypeDef inputRow = fixture.Source.Find(M05Row, false), linkedRow = fixture.LinkedRuntime.Find(M05Row, false);
                var inputList = new TypeRefUser(fixture.Source, "System.Collections.Generic", "List`1", fixture.Source.CorLibTypes.AssemblyRef);
                var linkedList = new TypeRefUser(fixture.LinkedRuntime, "System.Collections.Generic", "List`1", fixture.LinkedRuntime.CorLibTypes.AssemblyRef);
                input.FieldSig = new FieldSig(new GenericInstSig(new ClassSig(inputList), new SZArraySig(new ClassSig(inputRow))));
                linked.FieldSig = new FieldSig(new GenericInstSig(new ClassSig(linkedList), new SZArraySig(new ClassSig(linkedRow))));

                string resolved = (string)Invoke("ResolvedSchemaFieldType", input, fixture.Modules);
                Assert.AreEqual((string)Invoke("ResolvedSchemaFieldType", linked, fixture.Modules), resolved);
                StringAssert.Contains("System.Collections.Generic.List`1", resolved);
                StringAssert.Contains("HybridCLR.AssemblyShadowDiagnosticAssembly[]", resolved);
                StringAssert.Contains(", mscorlib,", resolved);
                StringAssert.DoesNotContain(", netstandard,", resolved);
            }
        }

        [Test] public void LinkedSchemaResolutionHasNoAmbientOrNameOnlyFallback()
        {
            foreach (string mutation in new[] { "missing-owner", "duplicate-owner", "wrong-owner-version", "wrong-owner-culture", "wrong-owner-key",
                "missing-type", "duplicate-type", "missing-field", "duplicate-field", "field-flags", "field-shape", "class-value-shape",
                "missing-framework", "wrong-framework-version", "wrong-framework-culture", "wrong-framework-key", "missing-definition", "unsupported-signature" })
                using (var fixture = new M05LinkedSchemaFixture())
                {
                    FieldDef source = fixture.Source.Find(M05Root, false).Fields.Single(field => field.Name == "schemaVersion");
                    FieldDef linked = fixture.LinkedRuntime.Find(M05Root, false).Fields.Single(field => field.Name == "schemaVersion");
                    if (mutation == "missing-owner") fixture.Modules.Remove("HybridCLR.Runtime");
                    else if (mutation == "duplicate-owner") fixture.Modules.Add("duplicate-runtime-key", fixture.LinkedRuntime);
                    else if (mutation == "wrong-owner-version") fixture.LinkedRuntime.Assembly.Version = new Version(9, 0, 0, 0);
                    else if (mutation == "wrong-owner-culture") fixture.LinkedRuntime.Assembly.Culture = "fixture";
                    else if (mutation == "wrong-owner-key") fixture.LinkedRuntime.Assembly.PublicKey = new PublicKey(new byte[] { 1, 2, 3, 4 });
                    else if (mutation == "missing-type") fixture.LinkedRuntime.Types.Remove(linked.DeclaringType);
                    else if (mutation == "duplicate-type") fixture.LinkedRuntime.Types.Add(new TypeDefUser("HybridCLR", "AssemblyShadowDiagnostics"));
                    else if (mutation == "missing-field") linked.DeclaringType.Fields.Remove(linked);
                    else if (mutation == "duplicate-field") linked.DeclaringType.Fields.Add(new FieldDefUser(linked.Name, new FieldSig(linked.FieldType), linked.Attributes));
                    else if (mutation == "field-flags") linked.Attributes ^= dnlib.DotNet.FieldAttributes.InitOnly;
                    else if (mutation == "field-shape") linked.FieldSig = new FieldSig(fixture.LinkedRuntime.CorLibTypes.String);
                    else if (mutation == "class-value-shape") linked.FieldSig = new FieldSig(new ClassSig(new TypeRefUser(fixture.LinkedRuntime,
                        "System", "Int32", fixture.LinkedRuntime.CorLibTypes.AssemblyRef)));
                    else if (mutation == "missing-framework") fixture.Modules.Remove("mscorlib");
                    else if (mutation == "wrong-framework-version") fixture.LinkedMscorlib.Assembly.Version = new Version(9, 0, 0, 0);
                    else if (mutation == "wrong-framework-culture") fixture.LinkedMscorlib.Assembly.Culture = "fixture";
                    else if (mutation == "wrong-framework-key") fixture.LinkedMscorlib.Assembly.PublicKey = new PublicKey(new byte[] { 1, 2, 3, 4 });
                    else if (mutation == "missing-definition") fixture.LinkedMscorlib.Types.Remove(fixture.LinkedMscorlib.Find("System.Int32", false));
                    else
                    {
                        source.FieldSig = new FieldSig(new PtrSig(fixture.Source.CorLibTypes.Int32));
                        linked.FieldSig = new FieldSig(new PtrSig(fixture.LinkedRuntime.CorLibTypes.Int32));
                    }
                    AssertCode("M06ExecutionSchemaResolution", () => Invoke("ResolvedSchemaFieldType", source, fixture.Modules));
                }
        }

        [Test] public void LinkedSchemaShapeRejectsSameNamedTypesFromAnUnrelatedAssembly()
        {
            using (var fixture = new M05LinkedSchemaFixture())
            using (var fake = new ModuleDefUser("M06.Schema.Fake.dll", Guid.NewGuid(), new AssemblyRefUser(fixture.LinkedMscorlib.Assembly)) { Kind = ModuleKind.Dll })
            {
                new AssemblyDefUser("M06.Schema.Fake", new Version(1, 0, 0, 0)).Modules.Add(fake);
                var impostor = new TypeDefUser("HybridCLR", "AssemblyShadowDiagnosticAssembly", fake.CorLibTypes.Object.TypeDefOrRef) {
                    Attributes = dnlib.DotNet.TypeAttributes.Public,
                };
                fake.Types.Add(impostor); fixture.Modules.Add("M06.Schema.Fake", fake);
                FieldDef source = fixture.Source.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                FieldDef linked = fixture.LinkedRuntime.Find(M05Root, false).Fields.Single(field => field.Name == "assemblies");
                linked.FieldSig = new FieldSig(new SZArraySig(new ClassSig(impostor)));
                Assert.AreEqual(source.FieldType.FullName, linked.FieldType.FullName);
                AssertCode("M06ExecutionSchemaResolution", () => Invoke("ResolvedSchemaFieldType", source, fixture.Modules));
            }
        }

        [Test] public void LinkedSchemaResolutionUsesOnlyExactBoundedForwarders()
        {
            using (var fixture = new ForwarderFixture())
            {
                string resolved = (string)Invoke("ResolvedSchemaFieldType", fixture.SourceField, fixture.Modules);
                StringAssert.Contains("Fixture.Forwarded, M06.Schema.Target, Version=1.0.0.0", resolved);
            }
            foreach (string mutation in new[] { "missing-target", "duplicate-target", "wrong-target-version", "wrong-target-culture", "wrong-target-key",
                "not-forwarder", "duplicate-export", "definition-and-export", "cycle" })
                using (var fixture = new ForwarderFixture())
                {
                    if (mutation == "missing-target") fixture.Modules.Remove("M06.Schema.Target");
                    else if (mutation == "duplicate-target") fixture.Modules.Add("duplicate-target-key", fixture.Target);
                    else if (mutation == "wrong-target-version") fixture.Target.Assembly.Version = new Version(9, 0, 0, 0);
                    else if (mutation == "wrong-target-culture") fixture.Target.Assembly.Culture = "fixture";
                    else if (mutation == "wrong-target-key") fixture.Target.Assembly.PublicKey = new PublicKey(new byte[] { 1, 2, 3, 4 });
                    else if (mutation == "not-forwarder") fixture.Forwarder.Attributes &= ~dnlib.DotNet.TypeAttributes.Forwarder;
                    else if (mutation == "duplicate-export") fixture.Facade.ExportedTypes.Add(fixture.NewForwarder(fixture.Facade, fixture.Target));
                    else if (mutation == "definition-and-export") fixture.Target.ExportedTypes.Add(fixture.NewForwarder(fixture.Target, fixture.Facade));
                    else
                    {
                        fixture.Target.Types.Remove(fixture.Definition);
                        fixture.Target.ExportedTypes.Add(fixture.NewForwarder(fixture.Target, fixture.Facade));
                    }
                    AssertCode("M06ExecutionSchemaResolution", () => Invoke("ResolvedSchemaFieldType", fixture.SourceField, fixture.Modules));
                }
        }

        [Test] public void AcceptedM05LinkedSetResolvesTopLevelAndNestedForwarders()
        {
            using (var fixture = new M05LinkedSchemaFixture())
            {
                var systemCore = new AssemblyRefUser(fixture.LinkedSystemCore.Assembly);
                var action = new TypeRefUser(fixture.LinkedRuntime, "System", "Action", systemCore);
                TypeDef actionDefinition = (TypeDef)Invoke("ResolveLinkedSchemaDefinition", action, fixture.Modules);
                Assert.AreEqual("System.Action", actionDefinition.FullName);
                Assert.AreSame(fixture.LinkedMscorlib, actionDefinition.Module);

                var timeZone = new TypeRefUser(fixture.LinkedRuntime, "System", "TimeZoneInfo", systemCore);
                var adjustment = new TypeRefUser(fixture.LinkedRuntime, "", "AdjustmentRule", timeZone);
                TypeDef nestedDefinition = (TypeDef)Invoke("ResolveLinkedSchemaDefinition", adjustment, fixture.Modules);
                Assert.AreEqual("System.TimeZoneInfo/AdjustmentRule", nestedDefinition.FullName);
                Assert.AreSame(fixture.LinkedMscorlib, nestedDefinition.Module);
            }
        }

        [Test] public void MethodEvidenceUsesRealMetadataTokenGenericsLocalsAndExceptionBoundaries()
        {
            using (var fixture = new MethodFixture())
            {
                M06ExecutionMethod actual = fixture.Read();
                Assert.AreEqual(unchecked((int)fixture.Method.MDToken.Raw), actual.metadataToken);
                Assert.AreEqual(1, actual.genericArity);
                Assert.IsTrue(actual.hasBody && actual.isStatic);
                CollectionAssert.AreEqual(new[] { "T" }, actual.genericParameterNames);
                Assert.AreEqual(2, actual.parameterTypes.Length);
                Assert.AreEqual("System.Int32&", actual.parameterTypes[1].type);
                Assert.AreEqual(fixture.Method.MethodSig.RetType.ReflectionFullName, actual.returnType.type);
                Assert.AreEqual(fixture.Method.Body.Variables.Count, actual.locals.Length);
                Assert.IsTrue(actual.exceptionHandlers.Any(handler => handler.handlerType == "Finally"));
                Assert.IsTrue(actual.instructions.Any(instruction => instruction.Contains(" branch:")));
                foreach (var handler in actual.exceptionHandlers)
                {
                    Assert.GreaterOrEqual(handler.tryStart, 0); Assert.Greater(handler.tryEnd, handler.tryStart);
                    Assert.GreaterOrEqual(handler.handlerStart, 0); Assert.Greater(handler.handlerEnd, handler.handlerStart);
                    Assert.AreEqual(-1, handler.filterStart);
                }
            }
        }

        [Test] public void BranchNormalizationDoesNotDependOnByteOffsets()
        {
            using (var fixture = new MethodFixture())
            {
                var before = fixture.Read();
                foreach (var instruction in fixture.Method.Body.Instructions) instruction.Offset += 4096;
                var after = fixture.Read();
                CollectionAssert.AreEqual(before.instructions, after.instructions);
                Assert.AreEqual(Serialize(before.exceptionHandlers), Serialize(after.exceptionHandlers));
            }
        }

        [Test] public void ForeignBranchAndExceptionTargetsFailClosed()
        {
            foreach (bool exceptionBoundary in new[] { false, true })
                using (var fixture = new MethodFixture())
                {
                    var foreign = OpCodes.Nop.ToInstruction();
                    if (exceptionBoundary) fixture.Method.Body.ExceptionHandlers[0].TryStart = foreign;
                    else fixture.Method.Body.Instructions.First(instruction => instruction.Operand is Instruction).Operand = foreign;
                    AssertCode("M06ExecutionIlBoundary", () => fixture.Read());
                }
        }

        [Test] public void SourceSequencePointsKeepActualDocumentChecksumAndLineData()
        {
            using (var fixture = new MethodFixture())
            {
                var point = new SequencePoint {
                    Document = new PdbDocument { Url = "/captured/M06Witness.cs", CheckSumAlgorithmId = new Guid("8829d00f-11b8-4213-878b-770e8597ac16"), CheckSum = new byte[] { 1, 17, 255 } },
                    StartLine = 27, EndLine = 29, StartColumn = 8, EndColumn = 13,
                };
                fixture.Method.Body.Instructions[0].SequencePoint = point;
                var actual = fixture.Read().sequencePoints.Single();
                Assert.AreEqual("/captured/M06Witness.cs", actual.document);
                Assert.AreEqual("0111ff", actual.checksum);
                Assert.AreEqual(point.Document.CheckSumAlgorithmId.ToString(), actual.checksumAlgorithm);
                Assert.AreEqual(0, actual.instructionIndex); Assert.AreEqual(27, actual.startLine); Assert.AreEqual(29, actual.endLine);
                Assert.AreEqual(8, actual.startColumn); Assert.AreEqual(13, actual.endColumn);
            }
        }

        [Test] public void EveryMethodFieldIncludingZeroFalseAndNestedTypesIsRequiredInJson()
        {
            string[] fields = {
                "\"declaringType\":\"Fixture\"", "\"name\":\"Method\"", "\"signature\":\"signature\"",
                "\"metadataToken\":0", "\"genericArity\":0", "\"methodFlags\":0", "\"implementationFlags\":0", "\"maxStack\":0",
                "\"isStatic\":false", "\"hasBody\":false", "\"initLocals\":false",
                "\"returnType\":{\"assembly\":\"\",\"type\":\"System.Void\"}", "\"parameterTypes\":[]",
                "\"genericParameterNames\":[]", "\"locals\":[]", "\"instructions\":[]", "\"exceptionHandlers\":[]", "\"sequencePoints\":[]",
            };
            Assert.AreEqual(typeof(M06ExecutionMethod).GetFields().Length, fields.Length);
            string json = "{" + string.Join(",", fields) + "}";
            Assert.DoesNotThrow(() => M04JsonEvidence.ValidateSchema<M06ExecutionMethod>(json));
            for (int index = 0; index < fields.Length; ++index)
            {
                string changed = "{" + string.Join(",", fields.Where((field, ordinal) => ordinal != index)) + "}";
                AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<M06ExecutionMethod>(changed));
            }
            AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<M06ExecutionMethod>(json.Replace("\"isStatic\":false", "\"isStatic\":1")));
            AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<M06ExecutionMethod>(json.Replace("\"assembly\":\"\",", "")));
        }

        [Test] public void ProductionProofsAreByteBoundWriteOnceAndReplayBothModes()
        {
            string text = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M06ExecutionSchemaVerifier.cs");
            StringAssert.Contains("AssemblySnapshot.ReadAndVerify(snapshot, true)", text);
            StringAssert.Contains("M06GenerationBuild.ReadAndVerify(generationProofPath)", text);
            StringAssert.Contains("generation.developmentBuild == development", text);
            StringAssert.Contains("ShadowSourcePins.RequireSameBuildSources", text);
            StringAssert.Contains("TryToLoadPdbFromDisk = false", text);
            StringAssert.Contains("options.PdbFileOrData = pdb", text);
            StringAssert.Contains("plan.VerifyUnchanged()", text);
            StringAssert.Contains("!File.Exists(typePath) && !File.Exists(executionPath)", text);
            StringAssert.DoesNotContain("VerifySemanticEquivalence", text);
            StringAssert.DoesNotContain("Assembly.LoadFile", text);
            StringAssert.DoesNotContain("new AssemblyResolver", text);
        }

        [Test] public void FinitePrivateJsonHelperAcceptsActualClosedCallsitesBeforeAndAfterMetadataRoundTrip()
        {
            using (var fixture = new JsonFixture())
            {
                Assert.DoesNotThrow(fixture.Verify);
                using (var bytes = new MemoryStream())
                {
                    fixture.Module.Write(bytes);
                    using (var captured = ModuleDefMD.Load(bytes.ToArray()))
                        Assert.DoesNotThrow(() => Invoke("VerifyJsonInputCalls", captured, new[] { fixture.Root.FullName }));
                }
            }
        }

        [Test] public void JsonHelperRejectsOpenUnknownAndEscapedSelectors()
        {
            foreach (string mutation in new[] { "open", "unknown", "delegate", "token", "public", "extra", "unused", "wrong-return", "wrong-input", "duplicate-deserializer" })
                using (var fixture = new JsonFixture())
                {
                    if (mutation == "open") fixture.Call.GenericInstMethodSig.GenericArguments[0] = new GenericMVar(0);
                    else if (mutation == "unknown") fixture.Call.GenericInstMethodSig.GenericArguments[0] = new ClassSig(fixture.Unknown);
                    else if (mutation == "delegate") fixture.Caller.Body.Instructions[1].OpCode = OpCodes.Ldftn;
                    else if (mutation == "token") fixture.Caller.Body.Instructions[1].OpCode = OpCodes.Ldtoken;
                    else if (mutation == "public") fixture.Helper.Attributes = (fixture.Helper.Attributes & ~dnlib.DotNet.MethodAttributes.MemberAccessMask) | dnlib.DotNet.MethodAttributes.Public;
                    else if (mutation == "extra") fixture.Probe.Methods.Add(new MethodDefUser("ReadJson", MethodSig.CreateStatic(fixture.Module.CorLibTypes.Void)));
                    else if (mutation == "unused") fixture.Probe.Methods.Remove(fixture.Caller);
                    else if (mutation == "wrong-return") fixture.Helper.MethodSig.RetType = fixture.Module.CorLibTypes.Object;
                    else if (mutation == "wrong-input") fixture.Deserialize.GenericInstMethodSig.GenericArguments[0] = new ClassSig(fixture.Root);
                    else fixture.Helper.Body.Instructions.Insert(0, OpCodes.Call.ToInstruction(fixture.Deserialize));
                    AssertCode("M06ExecutionJsonRoot", fixture.Verify);
                }
        }

        [Test] public void DirectJsonAndNestedCoroutineInputsRequireExplicitCapturedRoots()
        {
            foreach (bool declared in new[] { false, true })
                using (var fixture = new JsonFixture())
                {
                    var nested = new TypeDefUser("", "Coroutine", fixture.Module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.NestedPrivate };
                    fixture.Probe.NestedTypes.Add(nested);
                    TypeDef root = declared ? fixture.Root : fixture.Unknown;
                    var method = new MethodDefUser("MoveNext", MethodSig.CreateStatic(new ClassSig(root), fixture.Module.CorLibTypes.String), dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static) { Body = new CilBody() };
                    nested.Methods.Add(method);
                    method.Body.Instructions.Add(OpCodes.Ldarg_0.ToInstruction());
                    method.Body.Instructions.Add(OpCodes.Call.ToInstruction(new MethodSpecUser(fixture.Deserialize.Method, new GenericInstMethodSig(new ClassSig(root)))));
                    method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
                    if (declared) Assert.DoesNotThrow(fixture.Verify);
                    else AssertCode("M06ExecutionJsonRoot", fixture.Verify);
                }
        }

        [Test] public void ActualConsumerWitnessesUseTheirExactModuleInitializerNames()
        {
            foreach (string consumer in new[] { "Contracts", "Extensibility" })
                using (var module = ModuleDefMD.Load(File.ReadAllBytes(Assembly.Load("AssemblyShadowDemo." + consumer + "Consumer").Location)))
                {
                    Assert.DoesNotThrow(() => Invoke("VerifyWitnessBoundary", module, false));
                    var initializer = new TypeDefUser("AssemblyShadowDemo.Consumers", consumer + "ConsumerM06ModuleInitializer", module.CorLibTypes.Object.TypeDefOrRef);
                    module.Types.Add(initializer);
                    var initialize = new MethodDefUser("Initialize", MethodSig.CreateStatic(module.CorLibTypes.Void), dnlib.DotNet.MethodAttributes.Assembly | dnlib.DotNet.MethodAttributes.Static) { Body = new CilBody() };
                    initialize.Body.Instructions.Add(OpCodes.Ret.ToInstruction()); initializer.Methods.Add(initialize);
                    var cctor = new MethodDefUser(".cctor", MethodSig.CreateStatic(module.CorLibTypes.Void), dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static | dnlib.DotNet.MethodAttributes.SpecialName | dnlib.DotNet.MethodAttributes.RTSpecialName) { Body = new CilBody() };
                    cctor.Body.Instructions.Add(OpCodes.Call.ToInstruction(initialize)); cctor.Body.Instructions.Add(OpCodes.Ret.ToInstruction()); module.GlobalType.Methods.Add(cctor);
                    Assert.DoesNotThrow(() => Invoke("VerifyWitnessBoundary", module, true));
                    cctor.Body.Instructions.Insert(0, OpCodes.Call.ToInstruction(initialize));
                    AssertCode("M06ExecutionInitializer", () => Invoke("VerifyWitnessBoundary", module, true));
                    cctor.Body.Instructions.RemoveAt(0);
                    initializer.Name = "M06ModuleInitializer";
                    AssertCode("M06ExecutionInitializer", () => Invoke("VerifyWitnessBoundary", module, true));
                }
        }

        [Test] public void ActualWitnessBoundaryRejectsChangedReturnParametersAndGenericArity()
        {
            foreach (string name in new[] { "Run", "GetModuleEvidence", "RunAsync", "RunCoroutine", "WarmupValue", "WarmupEcho", "ThrowForEvidence" })
                foreach (bool parameter in new[] { false, true })
                    using (var module = ModuleDefMD.Load(File.ReadAllBytes(Assembly.Load("AssemblyA.Contracts").Location)))
                    {
                        var method = module.Find("AssemblyA.Contracts.M06ExecutionWitness", false).Methods.Single(item => item.Name == name);
                        if (parameter) method.MethodSig.Params.Add(module.CorLibTypes.Object);
                        else method.MethodSig.RetType = module.CorLibTypes.Object;
                        AssertCode("M06ExecutionWitness", () => Invoke("VerifyWitnessBoundary", module, false));
                    }
        }

        private static object Invoke(string method, params object[] values)
        {
            try { return typeof(M06ExecutionSchemaVerifier).GetMethod(method, BindingFlags.NonPublic | BindingFlags.Static).Invoke(null, values); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }
        private static void AssertCode(string code, TestDelegate action)
        { Assert.AreEqual(code, Assert.Throws<ShadowBuildException>(action).Code); }
        private static string Serialize(object value)
        {
            using (var stream = new MemoryStream())
            {
                new DataContractJsonSerializer(value.GetType()).WriteObject(stream, value);
                return Encoding.UTF8.GetString(stream.ToArray());
            }
        }

        private sealed class JsonFixture : IDisposable
        {
            internal readonly ModuleDefUser Module;
            internal readonly TypeDef Probe, Root, Unknown;
            internal readonly MethodDef Helper, Caller;
            internal readonly MethodSpecUser Call, Deserialize;
            internal JsonFixture()
            {
                Module = new ModuleDefUser("AssemblyShadowDemo.Bootstrap.dll", Guid.NewGuid(), new AssemblyRefUser(new AssemblyNameInfo(typeof(object).Assembly.FullName))) { Kind = ModuleKind.Dll };
                new AssemblyDefUser("AssemblyShadowDemo.Bootstrap", new Version(1, 0, 0, 0)).Modules.Add(Module);
                Probe = new TypeDefUser("AssemblyShadowDemo", "M06ExecutionProbe", Module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.Public }; Module.Types.Add(Probe);
                Root = new TypeDefUser("", "Result", Module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.NestedPublic }; Probe.NestedTypes.Add(Root);
                Unknown = new TypeDefUser("", "Unknown", Module.CorLibTypes.Object.TypeDefOrRef) { Attributes = dnlib.DotNet.TypeAttributes.NestedPublic }; Probe.NestedTypes.Add(Unknown);
                Helper = new MethodDefUser("ReadJson", MethodSig.CreateStaticGeneric(1, new GenericMVar(0), Module.CorLibTypes.String), dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static) { Body = new CilBody() };
                Helper.GenericParameters.Add(new GenericParamUser(0, GenericParamAttributes.NonVariant, "T")); Probe.Methods.Add(Helper);
                var json = new TypeRefUser(Module, "UnityEngine", "JsonUtility", new AssemblyRefUser("UnityEngine.JSONSerializeModule", new Version(0, 0, 0, 0)));
                var from = new MemberRefUser(Module, "FromJson", MethodSig.CreateStaticGeneric(1, new GenericMVar(0), Module.CorLibTypes.String), json);
                Deserialize = new MethodSpecUser(from, new GenericInstMethodSig(new GenericMVar(0)));
                Helper.Body.Instructions.Add(OpCodes.Ldarg_0.ToInstruction()); Helper.Body.Instructions.Add(OpCodes.Call.ToInstruction(Deserialize)); Helper.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
                Caller = new MethodDefUser("ReadInputs", MethodSig.CreateStatic(new ClassSig(Root), Module.CorLibTypes.String), dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static) { Body = new CilBody() }; Probe.Methods.Add(Caller);
                Call = new MethodSpecUser(Helper, new GenericInstMethodSig(new ClassSig(Root)));
                Caller.Body.Instructions.Add(OpCodes.Ldarg_0.ToInstruction()); Caller.Body.Instructions.Add(OpCodes.Call.ToInstruction(Call)); Caller.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
            }
            internal void Verify() { Invoke("VerifyJsonInputCalls", Module, new[] { Root.FullName }); }
            public void Dispose() { Module.Dispose(); }
        }

        private sealed class RuntimeFixture : IDisposable
        {
            internal readonly ModuleDefMD Input, Linked;
            internal RuntimeFixture()
            {
                byte[] bytes = File.ReadAllBytes(Assembly.Load("HybridCLR.Runtime").Location);
                Input = ModuleDefMD.Load(bytes); Linked = ModuleDefMD.Load(bytes);
                // This is a metadata mutation test seam, not a Player build claim.
                // Editor/Mono implementations throw. Model the real IL2CPP declarations
                // without executing the business/native API or resolving another DLL.
                foreach (ModuleDef module in new[] { Input, Linked })
                {
                    TypeDef api = module.Find("HybridCLR.AssemblyShadowRuntime", false);
                    foreach (MethodDef method in api.Methods.Where(method => method.IsPublic && !method.IsConstructor && LegacyNames.Contains(method.Name.String)))
                    { method.Body = null; method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall; }
                    AddNegotiatedNativeEntries(api);
                }
            }
            internal void Verify() { Invoke("VerifyRuntimeModules", Input, Linked); }
            public void Dispose() { Input.Dispose(); Linked.Dispose(); }

            private static readonly HashSet<string> LegacyNames = new HashSet<string>(new[] {
                "ConfigureCandidates", "BeginTransaction", "StageAssembly", "ValidateTransaction", "CommitTransaction", "AbortTransaction",
                "GetState", "GetAssemblyExecutionMode", "GetDiagnosticsJson", "GetTypeResolutionInfo", "GetExecutionDiagnosticsJson",
            }, StringComparer.Ordinal);

            private static void AddNegotiatedNativeEntries(TypeDef api)
            {
                foreach (string name in new[] { "GetMetadataCapacityJsonInternal", "ReserveMetadataBudgetInternal", "GetRecoveryInfoJsonInternal" })
                {
                    MethodDef wrapper = api.Methods.Single(method => method.Name == name.Substring(0, name.Length - "Internal".Length));
                    var native = new MethodDefUser(name, wrapper.MethodSig,
                        dnlib.DotNet.MethodAttributes.Private | dnlib.DotNet.MethodAttributes.Static) {
                        ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall,
                    };
                    api.Methods.Add(native);
                }
            }
        }

        private sealed class M05LinkedSchemaFixture : IDisposable
        {
            private const string RootPath = "HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M05-Baseline-v6/PlayerInputs";
            internal readonly ModuleDefMD Source, LinkedRuntime, LinkedMscorlib, LinkedSystemCore, CompilerNetstandard;
            internal readonly Dictionary<string, ModuleDef> Modules;

            internal M05LinkedSchemaFixture()
            {
                string root = Path.GetFullPath(RootPath);
                string sourcePath = Path.Combine(root, "Assemblies/HybridCLR.Runtime.dll");
                string runtimePath = Path.Combine(root, "LinkedPlayer/Assemblies/hybridclr.runtime.dll");
                string mscorlibPath = Path.Combine(root, "LinkedPlayer/Assemblies/mscorlib.dll");
                string systemCorePath = Path.Combine(root, "LinkedPlayer/Assemblies/system.core.dll");
                string netstandardPath = Path.Combine(root, "References/netstandard.dll");
                foreach (string path in new[] { sourcePath, runtimePath, mscorlibPath, systemCorePath, netstandardPath })
                    Assert.IsTrue(File.Exists(path), "Accepted M05 compiler/linker input is missing: " + path);
                Source = ModuleDefMD.Load(File.ReadAllBytes(sourcePath));
                LinkedRuntime = ModuleDefMD.Load(File.ReadAllBytes(runtimePath));
                LinkedMscorlib = ModuleDefMD.Load(File.ReadAllBytes(mscorlibPath));
                LinkedSystemCore = ModuleDefMD.Load(File.ReadAllBytes(systemCorePath));
                CompilerNetstandard = ModuleDefMD.Load(File.ReadAllBytes(netstandardPath));
                Modules = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase) {
                    { "HybridCLR.Runtime", LinkedRuntime }, { "mscorlib", LinkedMscorlib }, { "System.Core", LinkedSystemCore },
                };
            }

            public void Dispose()
            {
                Source.Dispose(); LinkedRuntime.Dispose(); LinkedMscorlib.Dispose(); LinkedSystemCore.Dispose(); CompilerNetstandard.Dispose();
            }
        }

        private sealed class ForwarderFixture : IDisposable
        {
            internal readonly ModuleDefUser Source, LinkedOwner, Facade, Target;
            internal readonly TypeDef Definition;
            internal readonly FieldDef SourceField;
            internal readonly ExportedType Forwarder;
            internal readonly Dictionary<string, ModuleDef> Modules;

            internal ForwarderFixture()
            {
                Source = NewModule("M06.Schema.Owner"); LinkedOwner = NewModule("M06.Schema.Owner");
                Facade = NewModule("M06.Schema.Facade"); Target = NewModule("M06.Schema.Target");
                Definition = new TypeDefUser("Fixture", "Forwarded", Target.CorLibTypes.Object.TypeDefOrRef) {
                    Attributes = dnlib.DotNet.TypeAttributes.Public,
                };
                Target.Types.Add(Definition);
                Forwarder = NewForwarder(Facade, Target); Facade.ExportedTypes.Add(Forwarder);

                var sourceContainer = new TypeDefUser("Fixture", "Container", Source.CorLibTypes.Object.TypeDefOrRef) {
                    Attributes = dnlib.DotNet.TypeAttributes.Public,
                };
                var linkedContainer = new TypeDefUser("Fixture", "Container", LinkedOwner.CorLibTypes.Object.TypeDefOrRef) {
                    Attributes = dnlib.DotNet.TypeAttributes.Public,
                };
                Source.Types.Add(sourceContainer); LinkedOwner.Types.Add(linkedContainer);
                SourceField = new FieldDefUser("value", new FieldSig(new ClassSig(new TypeRefUser(Source, "Fixture", "Forwarded", new AssemblyRefUser(Facade.Assembly)))),
                    dnlib.DotNet.FieldAttributes.Public);
                sourceContainer.Fields.Add(SourceField);
                linkedContainer.Fields.Add(new FieldDefUser("value", new FieldSig(new ClassSig(new TypeRefUser(LinkedOwner, "Fixture", "Forwarded", new AssemblyRefUser(Facade.Assembly)))),
                    dnlib.DotNet.FieldAttributes.Public));
                Modules = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase) {
                    { "M06.Schema.Owner", LinkedOwner }, { "M06.Schema.Facade", Facade }, { "M06.Schema.Target", Target },
                };
            }

            internal ExportedType NewForwarder(ModuleDef module, ModuleDef target)
            {
                return new ExportedTypeUser(module, 0, "Fixture", "Forwarded",
                    dnlib.DotNet.TypeAttributes.Public | dnlib.DotNet.TypeAttributes.Forwarder, new AssemblyRefUser(target.Assembly));
            }

            private static ModuleDefUser NewModule(string name)
            {
                var module = new ModuleDefUser(name + ".dll", Guid.NewGuid(), AssemblyRefUser.CreateMscorlibReferenceCLR40()) { Kind = ModuleKind.Dll };
                new AssemblyDefUser(name, new Version(1, 0, 0, 0)).Modules.Add(module);
                return module;
            }

            public void Dispose()
            {
                Source.Dispose(); LinkedOwner.Dispose(); Facade.Dispose(); Target.Dispose();
            }
        }

        private sealed class MethodFixture : IDisposable
        {
            internal readonly ModuleDefMD Module;
            internal readonly MethodDef Method;
            internal MethodFixture()
            {
                Module = ModuleDefMD.Load(File.ReadAllBytes(typeof(M06ExecutionSchemaTests).Assembly.Location), new ModuleCreationOptions { TryToLoadPdbFromDisk = false });
                Method = Module.Find(typeof(M06ExecutionSchemaTests).FullName, false).Methods.Single(method => method.Name == "CapturedGeneric");
            }
            internal M06ExecutionMethod Read() { return (M06ExecutionMethod)Invoke("ReadMethod", Method); }
            public void Dispose() { Module.Dispose(); }
        }

        private static T CapturedGeneric<T>(T value, ref int count)
        {
            int original = count;
            try { if (count < 3) count = original + 7; else count = original + 9; return value; }
            finally { ++count; }
        }
    }
}
