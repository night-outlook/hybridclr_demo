using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Loader;
using System.Text.Json;
using AssemblyShadow.R03.Fixtures;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;

internal static class Program
{
    private static readonly List<object> Results = new List<object>();
    private static int failures;

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--phase" || args[2] != "--output" ||
            (args[1] != "baseline" && args[1] != "candidate"))
        {
            Console.Error.WriteLine("Usage: --phase baseline|candidate --output <unused-directory>");
            return 2;
        }
        bool baseline = args[1] == "baseline";
        string output = Path.GetFullPath(args[3]);
        if (Directory.Exists(output) || File.Exists(output)) throw new IOException("Output already exists: " + output);
        Directory.CreateDirectory(output);
        string fixtures = Path.Combine(output, "fixtures");
        EvolutionFixtureCorpus.Write(fixtures);
        var observations = new Dictionary<string, object>();

        Check("R03-F01-private-reference-real-bytes", () =>
        {
            using (var before = Open(fixtures, "private-reference/baseline/Layout.dll"))
            using (var after = Open(fixtures, "private-reference/target/Layout.dll"))
            {
                var a = before.GetTypes().Single(t => t.FullName == "R03.Node");
                var b = after.GetTypes().Single(t => t.FullName == "R03.Node");
                Require(a.Fields.Count == 1 && b.Fields.Count == 2, "Actual field table shape");
                Require(b.Fields[1].IsPrivate && b.Fields[1].FieldType.ElementType == ElementType.Object, "Private reference field");
                observations["privateReference"] = new { beforeFields = a.Fields.Select(f => f.FullName).ToArray(),
                    afterFields = b.Fields.Select(f => f.FullName).ToArray(), nativeAllocation = "NotRun" };
            }
            Require(Invoke(fixtures, "private-reference/baseline/Layout.dll") == 41, "Baseline real IL invocation");
            Require(Invoke(fixtures, "private-reference/target/Layout.dll") == 42, "Target real IL invocation");
        });

        Check("R03-F02-virtual-insertion-real-bytes", () =>
        {
            using (var before = Open(fixtures, "virtual-slot/baseline/Methods.dll"))
            using (var after = Open(fixtures, "virtual-slot/target/Methods.dll"))
            {
                var a = before.GetTypes().Single(t => t.FullName == "R03.Node");
                var b = after.GetTypes().Single(t => t.FullName == "R03.Node");
                Require(a.Methods.Where(m => m.IsVirtual).Select(m => m.Name.String).SequenceEqual(new[] { "Keep" }), "Baseline virtual order");
                Require(b.Methods.Where(m => m.IsVirtual).Select(m => m.Name.String).SequenceEqual(new[] { "Before", "Keep" }), "Target virtual order");
                var am = a.Methods.Single(m => m.Name == "Keep"); var bm = b.Methods.Single(m => m.Name == "Keep");
                Require(am.MDToken.Raw != bm.MDToken.Raw && am.MethodSig.ToString() == bm.MethodSig.ToString(), "Retained signature with changed physical row");
                observations["virtualInsertion"] = new { baselineToken = am.MDToken.Raw, targetToken = bm.MDToken.Raw,
                    targetDeclaredVirtualOrder = new[] { "Before", "Keep" }, nativeSlots = "NotRun", nativeMethodInfoMapping = "NotRun" };
            }
            Require(Invoke(fixtures, "virtual-slot/baseline/Methods.dll") == 41, "Baseline real IL invocation");
            Require(Invoke(fixtures, "virtual-slot/target/Methods.dll") == 42, "Target real IL invocation");
        });

        Check("R03-G01-direction-reversal", () =>
        {
            var before = Set(fixtures, "reversal/baseline"); var after = Set(fixtures, "reversal/target");
            Require(before.Single(x => x.name == "A").references.Contains("B"), "Actual baseline A->B AssemblyRef");
            Require(after.Single(x => x.name == "B").references.Contains("A"), "Actual target B->A AssemblyRef");
            var roots = AssemblyReferenceGraph.DetectChangedRoots(before, after);
            var graph = new AssemblyReferenceGraph(after, null, new AssemblyReferenceGraph(before).Edges);
            if (baseline)
            {
                ExpectCode("DependencyCycle", () => graph.ReverseClosure(roots));
                observations["directionReversal"] = new { observed = "DependencyCycle", sourcePhase = "baseline" };
            }
            else
            {
                var closure = graph.ReverseClosure(roots);
                Require(SameSet(closure, "A", "B"), "Safety closure retained both versions");
                Require(graph.LoadOrder(closure).SequenceEqual(new[] { "A", "B" }), "Target provider-before-consumer order");
                Require(new AssemblyReferenceGraph(after).LoadOrder(closure).SequenceEqual(graph.LoadOrder(closure)), "Generation/patch target algorithm equality");
                observations["directionReversal"] = new { observed = "Accepted", closure, order = graph.LoadOrder(closure) };
            }
        });

        Check("R03-G02-real-target-cycle", () =>
        {
            var graph = new AssemblyReferenceGraph(Set(fixtures, "true-cycle/target"));
            ExpectCode("DependencyCycle", () => graph.LoadOrder(graph.ReverseClosure(new[] { "A" })));
        });

        Check("R03-G03-cumulative-installation-baseline", () =>
        {
            var before = Set(fixtures, "cumulative/baseline");
            var v1 = Set(fixtures, "cumulative/v1"); var v2 = Set(fixtures, "cumulative/v2");
            var rollback = Set(fixtures, "cumulative/rollback");
            Require(SameSet(AssemblyReferenceGraph.DetectChangedRoots(before, v1), "A"), "v1 root A");
            var roots = AssemblyReferenceGraph.DetectChangedRoots(before, v2);
            Require(SameSet(roots, "A", "B"), "v2 keeps A relative to installed baseline");
            Require(SameSet(AssemblyReferenceGraph.DetectChangedRoots(v1, v2), "B"), "Network delta alone is insufficient");
            var graph = new AssemblyReferenceGraph(v2, null, new AssemblyReferenceGraph(before).Edges);
            Require(SameSet(graph.ReverseClosure(roots), "A", "B"), "v2 complete runtime closure");
            Require(AssemblyReferenceGraph.DetectChangedRoots(before, rollback).Length == 0, "Source rollback to installation baseline");
        });

        Check("R03-G04-deleted-historical-edge", () =>
        {
            var before = Set(fixtures, "cumulative/baseline");
            var target = new[] { Describe(EvolutionFixtureCorpus.Build("A")), Describe(EvolutionFixtureCorpus.Build("B", 42)) };
            var graph = new AssemblyReferenceGraph(target, null, new AssemblyReferenceGraph(before).Edges);
            var closure = graph.ReverseClosure(new[] { "B" });
            Require(SameSet(closure, "A", "B"), "Historical consumer is retained");
            if (!baseline) Require(graph.LoadOrder(closure).SequenceEqual(new[] { "A", "B" }), "Deleted edge does not order target");
        });

        Check("R03-G05-ordinary-role-false", () => OrdinaryRole(fixtures, false, baseline));
        Check("R03-G06-ordinary-role-true", () => OrdinaryRole(fixtures, true, baseline));

        Check("R03-G07-declared-impact-not-initializer-order", () =>
        {
            var modules = new[] { Describe(EvolutionFixtureCorpus.Build("A")), Describe(EvolutionFixtureCorpus.Build("B")) };
            var config = new ShadowDependencyConfiguration { runtimeDependencies = new[] {
                new DeclaredRuntimeDependency { consumer = "A", provider = "B", kind = "ReflectionString", evidence = "Finite impact declaration" } } };
            var graph = new AssemblyReferenceGraph(modules, config);
            var closure = graph.ReverseClosure(new[] { "B" });
            Require(SameSet(closure, "A", "B"), "Declared reverse impact retained");
            if (!baseline) Require(graph.LoadOrder(closure).SequenceEqual(new[] { "A", "B" }), "Impact declaration does not impose initializer order");
        });

        var inventory = Directory.GetFiles(fixtures, "*.dll", SearchOption.AllDirectories)
            .OrderBy(p => p, StringComparer.Ordinal).Select(p => new { path = Path.GetRelativePath(output, p).Replace('\\', '/'),
                bytes = new FileInfo(p).Length, sha256 = ShadowHash.File(p) }).ToArray();
        Require(inventory.Length == 18, "Exact fixture inventory");
        var report = new { kind = "R03HostEvolutionEvidence", schemaVersion = 1, phase = args[1],
            result = failures == 0 ? "Passed" : "Failed", failures, cases = Results, observations, fixtures = inventory,
            unityEditorRun = false, il2cppPlayerRun = false, nativeCounterexamples = "NotRun", runtimeAcceptance = false };
        string json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(Path.Combine(output, "results.json"), json + "\n");
        Console.WriteLine(json);
        return failures == 0 ? 0 : 1;
    }

    private static void OrdinaryRole(string fixtures, bool flag, bool baseline)
    {
        var modules = Set(fixtures, "cumulative/baseline");
        modules.Single(d => d.name == "A").classification = AssemblyClassification.NormalHotUpdate;
        modules.Single(d => d.name == "A").isShadowCapable = flag;
        var graph = new AssemblyReferenceGraph(modules);
        if (baseline && flag) Require(SameSet(graph.ReverseClosure(new[] { "B" }), "A", "B"), "Record existing role-promotion gap");
        else ExpectCode("NonShadowConsumer", () => graph.ReverseClosure(new[] { "B" }));
    }

    private static int Invoke(string root, string relative)
    {
        var context = new AssemblyLoadContext("R03-" + Guid.NewGuid(), true);
        try
        {
            var assembly = context.LoadFromAssemblyPath(Path.Combine(root, relative));
            var type = assembly.GetType("R03.Node", true);
            return (int)type.GetMethod("Keep", BindingFlags.Instance | BindingFlags.Public).Invoke(Activator.CreateInstance(type), null);
        }
        finally { context.Unload(); }
    }
    private static ModuleDefMD Open(string root, string path) { return ModuleDefMD.Load(File.ReadAllBytes(Path.Combine(root, path))); }
    private static AssemblyDescriptor[] Set(string root, string path)
    { return Directory.GetFiles(Path.Combine(root, path), "*.dll").OrderBy(p => p, StringComparer.Ordinal).Select(p => Describe(File.ReadAllBytes(p))).ToArray(); }
    private static AssemblyDescriptor Describe(byte[] bytes)
    {
        using (var module = ModuleDefMD.Load(bytes))
            return new AssemblyDescriptor { name = module.Assembly.Name, mvid = module.Mvid.ToString(),
                sha256 = ShadowHash.Bytes(bytes), semanticHash = AssemblySemanticHasher.Compute(module).semanticHash,
                references = module.GetAssemblyRefs().Select(r => r.Name.String).ToArray(), classification = AssemblyClassification.Runtime,
                isShadowCapable = true, capabilityDeclared = true };
    }
    private static bool SameSet(string[] values, params string[] expected)
    { return values.OrderBy(v => v, StringComparer.Ordinal).SequenceEqual(expected.OrderBy(v => v, StringComparer.Ordinal)); }
    private static void ExpectCode(string expected, Action action)
    {
        try { action(); }
        catch (ShadowBuildException e) { Require(e.Code == expected, "Expected " + expected + ", got " + e.Code); return; }
        throw new Exception("Expected rejection " + expected);
    }
    private static void Require(bool condition, string message) { if (!condition) throw new Exception(message); }
    private static void Check(string id, Action test)
    {
        try { test(); Results.Add(new { id, result = "Passed" }); }
        catch (Exception e) { ++failures; Results.Add(new { id, result = "Failed", error = e.ToString() }); }
    }
}
