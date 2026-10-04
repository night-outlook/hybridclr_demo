using System;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R02TypeResolutionSchemaTests
    {
        private static ModuleDef RuntimeFixture()
        {
            // Only emulate native method metadata in memory; never execute ICALLs.
            var module = ModuleDefMD.Load(Assembly.Load("HybridCLR.Runtime").Location);
            foreach (var method in module.Find("HybridCLR.AssemblyShadowRuntime", false).Methods.Where(m => m.IsPublic && m.IsStatic))
            { method.Body = null; method.ImplAttributes = dnlib.DotNet.MethodImplAttributes.InternalCall; }
            return module;
        }
        private static void Verify(ModuleDef input, ModuleDef linked)
        {
            try { typeof(M05TypeSchemaVerifier).GetMethod("VerifyRuntime", BindingFlags.NonPublic | BindingFlags.Static).Invoke(null, new object[] { input, linked }); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }
        [Test] public void EveryR02LinkedFieldIsRequiredByActualRuntimeProof()
        {
            using (var input = RuntimeFixture())
            using (var linked = RuntimeFixture())
            {
                Verify(input, linked);
                var nested = linked.Find(R02TypeResolutionSchema.ExtensionType, false);
                var fields = nested.Fields.Where(f => f.IsPublic && !f.IsStatic).ToArray();
                Assert.AreEqual(33, fields.Length);
                foreach (var field in fields)
                {
                    int index = nested.Fields.IndexOf(field); nested.Fields.Remove(field);
                    Assert.AreEqual("M05TypeSchemaMismatch", Assert.Throws<ShadowBuildException>(() => Verify(input, linked)).Code);
                    nested.Fields.Insert(index, field);
                }
            }
        }
        [Test] public void MatchingButNarrowedInputsCannotRedefineTheR02WireSchema()
        {
            using (var input = RuntimeFixture())
            using (var linked = RuntimeFixture())
            {
                foreach (var module in new[] { input, linked })
                    module.Find(R02TypeResolutionSchema.ExtensionType, false).Fields.Single(f => f.Name == "admissionCacheHits")
                        .FieldSig = new FieldSig(module.CorLibTypes.Int64);
                Assert.AreEqual("M05TypeSchemaFields", Assert.Throws<ShadowBuildException>(() => Verify(input, linked)).Code);
            }
        }
        [Test] public void UnitySerializationDoesNotManufactureMissingOrZeroR02Coverage()
        {
            const string legacy = "{\"schemaVersion\":1,\"logicalAssembly\":\"Test\",\"executionModeCode\":0,\"executionMode\":\"AotBaseline\",\"isActive\":true,\"physicalImageKind\":\"Aot\",\"typeKey\":\"Test.Type\",\"inputTypePointer\":\"\",\"activeTypePointer\":\"\",\"baselineTypePointer\":\"\",\"pointerDetailsAvailable\":false,\"baselinePointerAvailable\":false,\"containsShadowTypes\":false,\"definitionCacheHits\":0,\"definitionCacheMisses\":0,\"compositeRebuilds\":0,\"allocationRemaps\":0,\"guardFailures\":0}";
            var value = HybridCLR.AssemblyShadowTypeResolutionInfo.Parse(legacy);
            Assert.IsNull(value.r02);
            // Deliberately present diagnostic view must also remain out of the
            // legacy serialized DTO; raw native JSON is the persisted authority.
            var backing = typeof(HybridCLR.AssemblyShadowTypeResolutionInfo).GetField("r02Value", BindingFlags.NonPublic | BindingFlags.Instance);
            Assert.IsTrue(backing.IsNotSerialized);
            backing.SetValue(value, new HybridCLR.AssemblyShadowTypeResolutionInfo.R02Diagnostics());
            string serialized = UnityEngine.JsonUtility.ToJson(value);
            Assert.IsFalse(serialized.Contains("r02"));
            Assert.IsNull(HybridCLR.AssemblyShadowTypeResolutionInfo.Parse(serialized).r02);
        }
    }
}
