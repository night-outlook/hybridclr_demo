using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using dnlib.DotNet;
using dnlib.DotNet.Emit;

namespace AssemblyShadow.R03.Fixtures
{
    /// <summary>Real, independently writable baseline/target ECMA-335 DLLs.</summary>
    public static class EvolutionFixtureCorpus
    {
        public static byte[] Build(string assembly, int value = 41, string provider = null,
            bool appendReference = false, bool insertVirtual = false)
        {
            using (var module = new ModuleDefUser(assembly + ".dll"))
            {
                module.Kind = ModuleKind.Dll;
                module.RuntimeVersion = "v4.0.30319";
                using (var hash = SHA256.Create())
                    module.Mvid = new Guid(hash.ComputeHash(Encoding.UTF8.GetBytes(
                        assembly + ":" + value + ":" + provider + ":" + appendReference + ":" + insertVirtual)).Take(16).ToArray());
                new AssemblyDefUser(assembly, new Version(1, 0, 0, 0)).Modules.Add(module);
                var type = new TypeDefUser("R03", "Node", module.CorLibTypes.Object.TypeDefOrRef)
                { Attributes = TypeAttributes.Public | TypeAttributes.AutoLayout | TypeAttributes.AnsiClass | TypeAttributes.BeforeFieldInit };
                module.Types.Add(type);
                type.Fields.Add(new FieldDefUser("stable", new FieldSig(module.CorLibTypes.Int32), FieldAttributes.Private));
                if (appendReference)
                    type.Fields.Add(new FieldDefUser("added", new FieldSig(module.CorLibTypes.Object), FieldAttributes.Private));
                if (provider != null)
                {
                    var reference = new AssemblyRefUser(provider, new Version(1, 0, 0, 0));
                    var target = new TypeRefUser(module, "R03", "Node", reference);
                    type.Fields.Add(new FieldDefUser("provider", new FieldSig(new ClassSig(target)), FieldAttributes.Private));
                }
                var ctor = new MethodDefUser(".ctor", MethodSig.CreateInstance(module.CorLibTypes.Void),
                    MethodImplAttributes.IL | MethodImplAttributes.Managed,
                    MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName | MethodAttributes.RTSpecialName);
                ctor.Body = new CilBody();
                ctor.Body.Instructions.Add(Instruction.Create(OpCodes.Ldarg_0));
                ctor.Body.Instructions.Add(Instruction.Create(OpCodes.Call, new MemberRefUser(module, ".ctor",
                    MethodSig.CreateInstance(module.CorLibTypes.Void), module.CorLibTypes.Object.TypeDefOrRef)));
                ctor.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
                type.Methods.Add(ctor);
                if (insertVirtual) AddVirtual(module, type, "Before", 9);
                AddVirtual(module, type, "Keep", value);
                using (var bytes = new MemoryStream())
                { module.Write(bytes); return bytes.ToArray(); }
            }
        }

        private static void AddVirtual(ModuleDef module, TypeDef type, string name, int value)
        {
            var method = new MethodDefUser(name, MethodSig.CreateInstance(module.CorLibTypes.Int32),
                MethodImplAttributes.IL | MethodImplAttributes.Managed,
                MethodAttributes.Public | MethodAttributes.Virtual | MethodAttributes.NewSlot | MethodAttributes.HideBySig);
            method.Body = new CilBody();
            method.Body.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4, value));
            method.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
            type.Methods.Add(method);
        }

        public static void Write(string root)
        {
            if (Directory.Exists(root) || File.Exists(root)) throw new IOException("Fixture destination must be unused: " + root);
            Directory.CreateDirectory(root);
            Put(root, "private-reference/baseline/Layout.dll", Build("Layout"));
            Put(root, "private-reference/target/Layout.dll", Build("Layout", 42, appendReference: true));
            Put(root, "virtual-slot/baseline/Methods.dll", Build("Methods"));
            Put(root, "virtual-slot/target/Methods.dll", Build("Methods", 42, insertVirtual: true));
            Put(root, "reversal/baseline/A.dll", Build("A", provider: "B"));
            Put(root, "reversal/baseline/B.dll", Build("B"));
            Put(root, "reversal/target/A.dll", Build("A"));
            Put(root, "reversal/target/B.dll", Build("B", provider: "A"));
            Put(root, "true-cycle/target/A.dll", Build("A", provider: "B"));
            Put(root, "true-cycle/target/B.dll", Build("B", provider: "A"));
            Put(root, "cumulative/baseline/A.dll", Build("A", provider: "B"));
            Put(root, "cumulative/baseline/B.dll", Build("B"));
            Put(root, "cumulative/v1/A.dll", Build("A", 42, "B"));
            Put(root, "cumulative/v1/B.dll", Build("B"));
            Put(root, "cumulative/v2/A.dll", Build("A", 42, "B"));
            Put(root, "cumulative/v2/B.dll", Build("B", 42));
            Put(root, "cumulative/rollback/A.dll", Build("A", provider: "B"));
            Put(root, "cumulative/rollback/B.dll", Build("B"));
        }

        private static void Put(string root, string relative, byte[] bytes)
        {
            string path = Path.Combine(root, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllBytes(path, bytes);
        }
    }
}
