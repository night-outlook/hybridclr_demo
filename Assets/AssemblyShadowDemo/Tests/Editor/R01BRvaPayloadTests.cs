using System;
using System.IO;
using System.Linq;
using System.Reflection;
using dnlib.DotNet;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01BRvaPayloadTests
    {
        [TestCase(0)]
        [TestCase(29)]
        [TestCase(250)]
        public void ReadsRvaPayloadThroughRuntimeInitialization(int value)
        {
            string name = "R01BRvaFixture" + Guid.NewGuid().ToString("N");
            using (var module = new ModuleDefUser(name + ".dll") { Kind = ModuleKind.Dll })
            {
                new AssemblyDefUser(name, new Version(1, 0, 0, 0)).Modules.Add(module);
                var type = new TypeDefUser("Fixture", "Payload", module.CorLibTypes.Object.TypeDefOrRef) {
                    Attributes = dnlib.DotNet.TypeAttributes.Public | dnlib.DotNet.TypeAttributes.Abstract | dnlib.DotNet.TypeAttributes.Sealed };
                module.Types.Add(type);
                var field = new FieldDefUser("Data", new FieldSig(module.CorLibTypes.Byte),
                    dnlib.DotNet.FieldAttributes.Public | dnlib.DotNet.FieldAttributes.Static | dnlib.DotNet.FieldAttributes.HasFieldRVA) {
                    InitialValue = new byte[] { (byte)value } };
                type.Fields.Add(field);
                using (var stream = new MemoryStream())
                {
                    module.Write(stream);
                    FieldInfo loaded = Assembly.Load(stream.ToArray()).GetType("Fixture.Payload", true).GetField("Data");
                    Assert.AreEqual((byte)value, Read(loaded));
                }
            }
        }

        [Test]
        public void RejectsStaticStorageWithoutRvaPayload()
        {
            FieldInfo field = typeof(NoRva).GetField("Value");
            TargetInvocationException error = Assert.Throws<TargetInvocationException>(() => Read(field));
            Assert.IsInstanceOf<InvalidOperationException>(error.InnerException);
        }

        private static byte Read(FieldInfo field)
        {
            Type probe = AppDomain.CurrentDomain.GetAssemblies().Single(a => a.GetName().Name == "AssemblyShadow.R01BDiagnostics")
                .GetType("AssemblyShadowDemo.R01BCapacityProbe", true);
            return (byte)probe.GetMethod("ReadRvaByte", BindingFlags.NonPublic | BindingFlags.Static).Invoke(null, new object[] { field });
        }
        private static class NoRva { public static byte Value; }
    }
}
