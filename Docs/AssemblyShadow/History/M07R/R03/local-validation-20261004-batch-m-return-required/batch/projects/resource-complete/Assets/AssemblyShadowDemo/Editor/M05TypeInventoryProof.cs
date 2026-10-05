using System;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    [Serializable] public sealed class M05TypeDefinition
    {
        public string fullName, namespaceName, name, kind;
        public string[] nestingPath;
        public int genericArity;
        public bool isExported;
    }

    [Serializable] public sealed class M05TypeInventory
    {
        public string assemblyName;
        public M05TypeDefinition[] types;
    }

    /// <summary>TypeDef order is evidence for raw GetTypes, never a logical type key.</summary>
    public static class M05TypeInventoryProof
    {
        public static M05TypeInventory[] ReadIdentities(M04AssemblyIdentity[] identities)
        {
            Require(identities != null && identities.Length > 0 && identities.All(item => item != null) &&
                identities.Select(item => item.name).Distinct(StringComparer.Ordinal).Count() == identities.Length,
                "M05TypeInventoryIdentity", "Expected unique byte-bound assembly identities.");
            return identities.OrderBy(item => item.name, StringComparer.Ordinal)
                .Select(item => ReadFile(item.path, item.sha256, item.name)).ToArray();
        }

        public static M05TypeInventory ReadFile(string path, string sha256, string expectedAssembly)
        {
            Require(Path.IsPathRooted(path), "M05TypeInventoryPath", "Type inventory DLL paths must be absolute.");
            byte[] bytes = File.ReadAllBytes(path);
            Require(!string.IsNullOrEmpty(sha256) && ShadowHash.Bytes(bytes) == sha256,
                "M05TypeInventoryBytes", "Type inventory DLL bytes changed: " + path);
            using (var module = ModuleDefMD.Load(bytes))
            {
                Require(module.Assembly != null && module.Assembly.Name == expectedAssembly,
                    "M05TypeInventoryIdentity", "Unexpected declared assembly name: " + path);
                return ReadModule(module);
            }
        }

        internal static M05TypeInventory ReadModule(ModuleDef module)
        {
            Require(module != null && module.Assembly != null, "M05TypeInventoryIdentity", "Type inventory requires an assembly.");
            var definitions = module.GetTypes().OrderBy(type => type.Rid).ToArray();
            Require(definitions.All(type => type.Rid > 0) && definitions.Select(type => type.Rid).Distinct().Count() == definitions.Length,
                "M05TypeInventoryOrder", "Type inventory requires actual unique TypeDef rows.");
            return new M05TypeInventory {
                assemblyName = module.Assembly.Name.String,
                types = definitions.Where(type => !type.IsGlobalModuleType).Select(type => {
                    var nesting = new System.Collections.Generic.List<string>();
                    TypeDef parent = type.DeclaringType;
                    bool exported = type.IsNested ? type.IsNestedPublic : type.IsPublic;
                    while (parent != null)
                    {
                        nesting.Insert(0, parent.Name.String);
                        exported &= parent.IsNested ? parent.IsNestedPublic : parent.IsPublic;
                        parent = parent.DeclaringType;
                    }
                    return new M05TypeDefinition {
                        fullName = type.ReflectionFullName, namespaceName = type.Namespace.String, name = type.Name.String,
                        nestingPath = nesting.ToArray(), genericArity = type.GenericParameters.Count,
                        kind = type.IsEnum ? "enum" : type.IsInterface ? "interface" : type.IsValueType ? "valuetype" : "class",
                        isExported = exported,
                    };
                }).ToArray(),
            };
        }

        public static void Verify(M05TypeInventory[] claimed, M05TypeInventory[] actual)
        {
            Require(claimed != null && actual != null && claimed.Length == actual.Length,
                "M05TypeInventoryMismatch", "Type inventory assembly count differs.");
            for (int assembly = 0; assembly < actual.Length; ++assembly)
            {
                var left = claimed[assembly]; var right = actual[assembly];
                Require(left != null && right != null && left.assemblyName == right.assemblyName && left.types != null &&
                    right.types != null && left.types.Length == right.types.Length, "M05TypeInventoryMismatch", "Type inventory assembly differs.");
                for (int index = 0; index < right.types.Length; ++index)
                {
                    var a = left.types[index]; var b = right.types[index];
                    Require(a != null && b != null && a.fullName == b.fullName && a.namespaceName == b.namespaceName && a.name == b.name &&
                        a.kind == b.kind && a.genericArity == b.genericArity && a.isExported == b.isExported &&
                        a.nestingPath != null && b.nestingPath != null && a.nestingPath.SequenceEqual(b.nestingPath),
                        "M05TypeInventoryMismatch", "TypeDef evidence differs at " + right.assemblyName + " row " + index);
                }
            }
        }

        private static void Require(bool value, string code, string message) { ShadowHash.Require(value, code, message); }
    }
}
