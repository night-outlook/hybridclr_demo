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
    public sealed class M03DiagnosticSchemaTests
    {
        [Test]
        public void ActualDiagnosticMetadataSurvivesWithDifferentMvid()
        {
            using (var fixture = new Fixture())
            {
                fixture.Linked.Mvid = Guid.NewGuid();
                Assert.DoesNotThrow(fixture.Verify);
            }
        }

        [Test]
        public void EveryRemovedSchemaFieldIsRejected()
        {
            using (var reference = new Fixture())
            foreach (string typeName in DiagnosticTypeNames())
            {
                TypeDef type = reference.Input.Find(typeName, false);
                foreach (FieldDef field in type.Fields.Where(field => field.IsPublic && !field.IsStatic))
                using (var fixture = new Fixture())
                {
                    TypeDef linked = fixture.Linked.Find(type.FullName, false);
                    linked.Fields.Remove(linked.Fields.Single(candidate => candidate.Name == field.Name));
                    AssertCode("M03DiagnosticSchemaMismatch", fixture.Verify);
                }
            }
        }

        [Test]
        public void MissingNestedTypeIsRejected()
        {
            using (var fixture = new Fixture())
            {
                fixture.Linked.Types.Remove(fixture.Linked.Find("HybridCLR.AssemblyShadowDiagnosticEvent", false));
                AssertCode("M03DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void ChangedTypeFlagsAndExtraFieldsAreRejected()
        {
            foreach (string mutation in new[] { "type", "static", "nonserialized", "extra" })
            using (var fixture = new Fixture())
            {
                TypeDef type = fixture.Linked.Find("HybridCLR.AssemblyShadowDiagnosticEvent", false);
                FieldDef field = type.Fields.Single(candidate => candidate.Name == "generation");
                if (mutation == "type") field.FieldSig = new FieldSig(fixture.Linked.CorLibTypes.String);
                else if (mutation == "static") field.IsStatic = true;
                else if (mutation == "nonserialized") field.IsNotSerialized = true;
                else type.Fields.Add(new FieldDefUser("unexpected", new FieldSig(fixture.Linked.CorLibTypes.Int32), dnlib.DotNet.FieldAttributes.Public));
                AssertCode("M03DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void NewReachableDtoIsComparedWithoutUpdatingAnAllowlist()
        {
            using (var fixture = new Fixture())
            {
                foreach (ModuleDef module in new[] { fixture.Input, fixture.Linked })
                {
                    var nested = new TypeDefUser("HybridCLR", "FutureDiagnosticPayload", module.CorLibTypes.Object.TypeDefOrRef) {
                        Attributes = dnlib.DotNet.TypeAttributes.Public | dnlib.DotNet.TypeAttributes.Serializable,
                    };
                    nested.Fields.Add(new FieldDefUser("value", new FieldSig(module.CorLibTypes.Int32), dnlib.DotNet.FieldAttributes.Public));
                    module.Types.Add(nested);
                    module.Find("HybridCLR.AssemblyShadowDiagnostics", false).Fields.Add(new FieldDefUser("future",
                        new FieldSig(new SZArraySig(nested.ToTypeSig())), dnlib.DotNet.FieldAttributes.Public));
                }
                Assert.DoesNotThrow(fixture.Verify);
                fixture.Linked.Find("HybridCLR.FutureDiagnosticPayload", false).Fields.Clear();
                AssertCode("M03DiagnosticSchemaMismatch", fixture.Verify);
            }
        }

        [Test]
        public void WrongRuntimeAndClaimlessSnapshotAreRejected()
        {
            using (var fixture = new Fixture())
            {
                fixture.Linked.Assembly.Name = "Other.Runtime";
                AssertCode("M03DiagnosticRuntimeIdentity", fixture.Verify);
            }
            AssertCode("M03DiagnosticSnapshotMismatch", () => M03DiagnosticSchemaVerifier.Verify("unused", null));
        }

        [Test]
        public void BothBuildAndReplayCheckTheLinkedSchema()
        {
            StringAssert.Contains("M03DiagnosticSchemaVerifier.Verify(snapshot, captured)",
                File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M03Build.cs"));
            StringAssert.Contains("M03DiagnosticSchemaVerifier.Verify(manifest.baselineInputSnapshot, player)",
                File.ReadAllText("Assets/AssemblyShadowDemo/Editor/M03EditorValidation.cs"));
        }

        private static IEnumerable<string> DiagnosticTypeNames()
        {
            Assembly runtime = Assembly.Load("HybridCLR.Runtime");
            var pending = new Queue<Type>();
            var visited = new HashSet<Type>();
            pending.Enqueue(runtime.GetType("HybridCLR.AssemblyShadowDiagnostics", true));
            while (pending.Count != 0)
            {
                Type type = pending.Dequeue();
                while (type.IsArray) type = type.GetElementType();
                if (type.IsPrimitive || type == typeof(string) || !visited.Add(type)) continue;
                Assert.AreEqual(runtime, type.Assembly);
                yield return type.FullName;
                foreach (FieldInfo field in type.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    pending.Enqueue(field.FieldType);
            }
        }

        private static void AssertCode(string code, TestDelegate action)
        {
            Assert.AreEqual(code, Assert.Throws<ShadowBuildException>(action).Code);
        }

        private sealed class Fixture : IDisposable
        {
            public readonly ModuleDefMD Input, Linked;
            public Fixture()
            {
                byte[] bytes = File.ReadAllBytes(Assembly.Load("HybridCLR.Runtime").Location);
                Input = ModuleDefMD.Load(bytes); Linked = ModuleDefMD.Load(bytes);
            }

            public void Verify()
            {
                var method = typeof(M03DiagnosticSchemaVerifier).GetMethod("VerifyModules", BindingFlags.NonPublic | BindingFlags.Static);
                try { method.Invoke(null, new object[] { Input, Linked }); }
                catch (TargetInvocationException error) { throw error.InnerException; }
            }

            public void Dispose() { Input.Dispose(); Linked.Dispose(); }
        }
    }
}
