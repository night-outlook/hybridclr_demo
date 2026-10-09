using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Security.Cryptography;
using System.Text;
using dnlib.DotNet.Emit;
using dnlib.DotNet;
using AssemblyShadow.R03.Fixtures;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.AssemblyShadow.Tests;

internal static class Program
{
    private static string root;
    private static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--ir-target") return WriteIrTarget(args[1]);
        if (args.Length != 2 || args[0] != "--output") return 2;
        root = Path.GetFullPath(args[1]);
        if (File.Exists(root) || Directory.Exists(root)) throw new IOException("Fixture output must be unused.");
        Directory.CreateDirectory(root);
        Put("baseline/Layout.dll", EvolutionFixtureCorpus.Build("Layout"));
        Put("baseline/Methods.dll", EvolutionFixtureCorpus.Build("Methods"));
        Put("baseline/A.dll", StaticReference("A", "B"));
        Put("baseline/B.dll", StaticReference("B", null));
        Put("private-reference/Layout.dll", EvolutionFixtureCorpus.Build("Layout", 42, appendReference: true));
        Put("virtual-slot/Methods.dll", EvolutionFixtureCorpus.Build("Methods", 42, insertVirtual: true));
        Put("reversal/A.dll", StaticReference("A", null));
        Put("reversal/B.dll", StaticReference("B", "A"));
        Put("true-cycle/A.dll", StaticReference("A", "B"));
        Put("true-cycle/B.dll", StaticReference("B", "A"));
        var cases = new Dictionary<string, string>
        {
            { "L03-private-primitive-append-needs-native", "primitive" },
            { "L12-interface-addition", "interface" },
            { "L05-value-type-growth", "value" },
            { "L07-instance-field-removal", "removal" },
        };
        foreach (var pair in cases)
        {
            R03EvolutionContractCases.Run(pair.Key, (name, bytes) =>
            {
                // L05 has a value-type baseline. Its target is used against the
                // ordinary reference-type baseline as a distinct TypeKind test,
                // not mislabeled as the original value-type-growth counterexample.
                if (name == "baseline.dll" && pair.Value == "primitive") Put("baseline/R03Contract.dll", bytes);
                if (name == "target.dll") Put(pair.Value + "/R03Contract.dll", bytes);
            });
        }
        var files = Directory.GetFiles(root, "*.dll", SearchOption.AllDirectories).OrderBy(p => p, StringComparer.Ordinal).Select(p =>
        {
            byte[] bytes = File.ReadAllBytes(p);
            using (var module = ModuleDefMD.Load(bytes))
                return new { path = Path.GetRelativePath(root, p).Replace('\\', '/'), assembly = module.Assembly.Name.String,
                    mvid = module.Mvid.ToString(), size = bytes.Length, sha256 = ShadowHash.Bytes(bytes),
                    references = module.GetAssemblyRefs().Select(r => r.Name.String).OrderBy(n => n, StringComparer.Ordinal).ToArray() };
        }).ToArray();
        if (files.Length != 15) throw new InvalidOperationException("Expected exactly 15 native input DLLs.");
        // Verify graph-only pairs have identical instance layouts. A field-based
        // AssemblyRef witness would otherwise confound reversal with V1 rejection.
        foreach (string name in new[] { "A", "B" })
        {
            var report = NativeLayoutAdmissionValidator.Analyze(File.ReadAllBytes(Path.Combine(root, "baseline", name + ".dll")),
                File.ReadAllBytes(Path.Combine(root, "reversal", name + ".dll")));
            report.RequireEditorAdmission();
            if (report.types.Any(t => t.metadataChanged)) throw new InvalidOperationException("Graph-only witness changed instance metadata.");
        }
        var result = new { kind = "R03PlayerFixtureInventory", schemaVersion = 1, files,
            note = "Reversal uses static reference fields; original host counterexamples are retained separately. Native execution is NotRun.",
            nativeExecution = false, runtimeAcceptance = false };
        string json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(Path.Combine(root, "inventory.json"), json + "\n"); Console.WriteLine(json);
        return 0;
    }
    // Extra IR-only fixture. Never changes the fifteen established --output
    // DLLs, their MVIDs, or the immutable S evidence. The exact new target
    // has the same instance field layout but a side-effecting Keep body.
    private static int WriteIrTarget(string folder)
    {
        root = Path.GetFullPath(folder);
        if (File.Exists(root) || Directory.Exists(root))
            throw new IOException("IR target output must be unused.");
        Directory.CreateDirectory(root);
        byte[] target;
        using (var module = ModuleDefMD.Load(EvolutionFixtureCorpus.Build("Methods", 42, insertVirtual: true)))
        {
            var node = module.GetTypes().Single(t => t.FullName == "R03.Node");
            var field = node.Fields.Single(f => f.Name == "stable");
            if (field.IsStatic || field.FieldSig.Type.ElementType != ElementType.I4)
                throw new InvalidOperationException("Expected existing int instance field.");
            var keep = node.Methods.Single(m => m.Name == "Keep");
            if (!keep.HasBody || keep.MethodSig.Params.Count != 0 || !keep.MethodSig.HasThis)
                throw new InvalidOperationException("Unexpected original virtual Keep method.");
            var il = new CilBody();
            // side effect: this.stable += 1; return 42;
            il.Instructions.Add(Instruction.Create(OpCodes.Ldarg_0));
            il.Instructions.Add(Instruction.Create(OpCodes.Dup));
            il.Instructions.Add(Instruction.Create(OpCodes.Ldfld, field));
            il.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_1));
            il.Instructions.Add(Instruction.Create(OpCodes.Add));
            il.Instructions.Add(Instruction.Create(OpCodes.Stfld, field));
            il.Instructions.Add(Instruction.Create(OpCodes.Ldc_I4_S, (sbyte)42));
            il.Instructions.Add(Instruction.Create(OpCodes.Ret));
            keep.Body = il;
            // The IR binary is distinct from the historical target; avoid
            // inheriting its otherwise identical deterministic MVID.
            using (var hash = SHA256.Create())
                module.Mvid = new Guid(hash.ComputeHash(Encoding.UTF8.GetBytes("R03IR/Methods/side-effect-v1"))
                    .Take(16).ToArray());
            using (var stream = new MemoryStream())
            {
                module.Write(stream);
                target = stream.ToArray();
            }
        }
        Put("Methods.dll", target);
        using (var parsed = ModuleDefMD.Load(target))
        {
            if (parsed.Assembly.Name.String != "Methods" || parsed.GetTypes().Count(t => t.FullName == "R03.Node") != 1)
                throw new InvalidOperationException("IR target assembly identity mismatch.");
            var report = new
            {
                schemaVersion = 1, kind = "R03IRSideEffectFixture",
                result = "GeneratedNotRuntimeValidated", assembly = "Methods",
                mvid = parsed.Mvid.ToString(), size = target.Length,
                sha256 = ShadowHash.Bytes(target), instanceField = "R03.Node.stable",
                method = "R03.Node.Keep", expectedReturn = 42,
                expectedIncrementPerCall = 1, sourceMode = "SupplementaryIR",
                originalSFixtureUnchanged = true, runtimeAcceptance = false
            };
            string json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(Path.Combine(root, "ir-target.json"), json + "\n");
            Console.WriteLine(json);
        }
        return 0;
    }

    private static byte[] StaticReference(string name, string provider)
    {
        byte[] original = EvolutionFixtureCorpus.Build(name, provider: provider);
        using (var module = ModuleDefMD.Load(original))
        {
            var type = module.GetTypes().Single(t => t.FullName == "R03.Node");
            foreach (var field in type.Fields.Where(f => f.Name == "provider")) field.Attributes |= FieldAttributes.Static;
            using (var stream = new MemoryStream()) { module.Write(stream); return stream.ToArray(); }
        }
    }
    private static void Put(string path, byte[] bytes)
    {
        path = Path.Combine(root, path); Directory.CreateDirectory(Path.GetDirectoryName(path));
        using (var stream = new FileStream(path, FileMode.CreateNew)) stream.Write(bytes, 0, bytes.Length);
    }
}
