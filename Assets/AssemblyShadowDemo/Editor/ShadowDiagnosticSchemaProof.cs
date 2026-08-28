using System;
using System.Collections.Generic;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Compares captured DTO graphs without an ambient Editor assembly resolver.</summary>
    internal static class ShadowDiagnosticSchemaProof
    {
        internal static void Verify(ModuleDef input, ModuleDef linked, string[] roots, string codePrefix,
            IDictionary<string, ModuleDef> externalInput = null, IDictionary<string, ModuleDef> externalLinked = null,
            bool allowCoreLibraryLists = false)
        {
            var pending = new Queue<TypeDef>();
            var visited = new HashSet<string>(StringComparer.Ordinal);
            var beforeModules = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            var afterModules = new Dictionary<string, ModuleDef>(StringComparer.OrdinalIgnoreCase);
            if (externalInput != null) foreach (var pair in externalInput) beforeModules.Add(pair.Key, pair.Value);
            if (externalLinked != null) foreach (var pair in externalLinked) afterModules.Add(pair.Key, pair.Value);
            beforeModules[input.Assembly.Name.String] = input;
            afterModules[linked.Assembly.Name.String] = linked;
            foreach (string root in roots)
            {
                TypeDef type = input.Find(root, false);
                ShadowHash.Require(type != null, codePrefix + "SchemaMismatch", "Missing diagnostic root: " + root);
                pending.Enqueue(type);
            }
            while (pending.Count != 0)
            {
                TypeDef before = pending.Dequeue();
                string assembly = before.Module.Assembly.Name.String;
                if (!visited.Add(assembly + "|" + before.FullName)) continue;
                ModuleDef counterpart;
                ShadowHash.Require(afterModules.TryGetValue(assembly, out counterpart) &&
                    before.Module.Assembly.FullName == counterpart.Assembly.FullName,
                    codePrefix + "SchemaMismatch", "Diagnostic assembly identity mismatch: " + assembly);
                TypeDef after = counterpart.Find(before.FullName, false);
                ShadowHash.Require(after != null && before.IsSerializable && after.IsSerializable,
                    codePrefix + "SchemaMismatch", "Missing or non-serializable diagnostic type: " + before.FullName);
                FieldDef[] fields = before.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray();
                FieldDef[] actual = after.Fields.Where(field => field.IsPublic && !field.IsStatic).ToArray();
                ShadowHash.Require(fields.Length > 0 && fields.Length == actual.Length,
                    codePrefix + "SchemaMismatch", "Diagnostic field count changed after linking: " + before.FullName);
                foreach (FieldDef field in fields)
                {
                    FieldDef[] matches = actual.Where(candidate => candidate.Name == field.Name).ToArray();
                    ShadowHash.Require(matches.Length == 1 && matches[0].Attributes == field.Attributes &&
                        new SigComparer().Equals(field.FieldType, matches[0].FieldType), codePrefix + "SchemaMismatch",
                        "Diagnostic field missing or changed after linking: " + before.FullName + "." + field.Name);
                    TypeSig element = Element(field.FieldType, before.Module, allowCoreLibraryLists, codePrefix);
                    // SigComparer intentionally treats compiler CoreLib facades and their linked
                    // CoreLib replacement as equivalent. Independently verify the exact declared
                    // List owner on BOTH sides so that equivalence cannot admit a spoofed scope.
                    if (allowCoreLibraryLists) Element(matches[0].FieldType, after.Module, true, codePrefix);
                    if (element.IsPrimitive || element.ElementType == ElementType.String) continue;
                    ModuleDef owner = before.Module;
                    if (element.DefinitionAssembly != null && element.DefinitionAssembly.Name != owner.Assembly.Name)
                    {
                        ShadowHash.Require(beforeModules.TryGetValue(element.DefinitionAssembly.Name.String, out owner),
                            codePrefix + "SchemaUnsupported", "Uncaptured external diagnostic DTO: " + field.FullName);
                    }
                    TypeDef child = owner.Find(element.FullName, false);
                    ShadowHash.Require(child != null, codePrefix + "SchemaUnsupported",
                        "Diagnostic fields must be primitive, string, or captured serializable DTOs: " + field.FullName);
                    pending.Enqueue(child);
                }
            }
        }

        private static TypeSig Element(TypeSig type, ModuleDef owner, bool allowCoreLibraryLists, string codePrefix)
        {
            for (int depth = 0; depth < 64; ++depth)
            {
                if (type is SZArraySig) { type = type.Next; continue; }
                var list = type as GenericInstSig;
                if (!allowCoreLibraryLists || list == null) return type;
                IAssembly scope = list.GenericType == null ? null : list.GenericType.DefinitionAssembly;
                IAssembly core = owner.CorLibTypes.AssemblyRef;
                ShadowHash.Require(list.GenericType is ClassSig && list.GenericType.FullName == "System.Collections.Generic.List`1" &&
                    list.GenericArguments.Count == 1 && !list.ContainsGenericParameter && scope != null && core != null &&
                    scope.FullName == core.FullName,
                    codePrefix + "SchemaUnsupported", "Only closed single-argument List<T> from the captured module CoreLib is supported: " + type.FullName);
                type = list.GenericArguments[0];
            }
            ShadowHash.Require(false, codePrefix + "SchemaUnsupported", "Diagnostic collection nesting is excessive.");
            return null;
        }
    }
}
