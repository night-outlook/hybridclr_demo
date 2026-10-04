using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.AssemblyShadow.Tests;

internal static class Program
{
    private static readonly List<object> Results = new List<object>();
    private static int failures;
    private static void Require(bool condition, string message) { if (!condition) throw new Exception(message); }
    private static void Check(string id, Action action)
    {
        try { action(); Results.Add(new { id, result = "Passed" }); }
        catch (Exception ex) { failures++; Results.Add(new { id, result = "Failed", error = ex.ToString() }); }
    }
    private static Dictionary<string, AssemblyDescriptor> Descriptors() => new Dictionary<string, AssemblyDescriptor> {
        { "Consumer", new AssemblyDescriptor { name = "Consumer", classification = AssemblyClassification.EditorOnly,
            references = new [] { "mscorlib" } } } };
    private static Dictionary<string, ModuleDefMD> Modules() => new Dictionary<string, ModuleDefMD> {
        { "mscorlib", ModuleDefMD.Load(typeof(object).Assembly.Location) } };
    private static IResolver Resolver() => new Resolver(new AssemblyResolver());
    private static CompiledAssemblySet Make() => SyntheticCompiledAssemblySet.Create(Descriptors(), Modules(), Resolver(), Array.Empty<string>());
    private static void MustRejectNull(Action action, string param)
    { try { action(); throw new Exception("Null unexpectedly accepted"); } catch (ArgumentNullException ex) { Require(ex.ParamName == param, "Wrong null boundary"); } }
    public static int Main(string[] args)
    {
        if (args.Length != 2 || args[0] != "--output" || Directory.Exists(args[1])) throw new ArgumentException("Unused --output directory required");
        Directory.CreateDirectory(args[1]);
        Check("FC01-exact-constructor-signature", () => {
            var c = typeof(CompiledAssemblySet).GetConstructors(BindingFlags.Instance | BindingFlags.NonPublic);
            Require(c.Length == 1 && c[0].GetParameters().Length == 5 &&
                c[0].GetParameters()[4].ParameterType == typeof(IEnumerable<CompiledAssemblySource>), "Reviewed constructor changed"); });
        Check("FC02-reference-only-module-without-descriptor", () => {
            using (var set = Make()) Require(set.GetModule("mscorlib") != null && !set.Assemblies.ContainsKey("mscorlib") && set.Assemblies.ContainsKey("Consumer"), "Original PolicyTests construction invariant"); });
        Check("FC03-empty-synthetic-source-authority", () => { using (var set = Make()) Require(set.Sources.Count == 0, "Synthetic sources must stay empty"); });
        Check("FC04-synthetic-qualification-rejected", () => {
            using (var set = Make()) {
                try { PureInterpreterEligibility.Analyze(set, set, Array.Empty<string>(), new ShadowDependencyConfiguration(),
                    new ResourceAbiDescriptor { schemaVersion = 2 }); throw new Exception("Synthetic provenance accepted"); }
                catch (InvalidOperationException ex) { Require(ex.Message.Contains("no matching element", StringComparison.OrdinalIgnoreCase), "Expected missing loaded source evidence"); }
            } });
        Check("FC05-original-four-argument-negative", () => {
            var modules = Modules(); try {
                var c = typeof(CompiledAssemblySet).GetConstructors(BindingFlags.Instance | BindingFlags.NonPublic).Single();
                try { c.Invoke(new object[] { Descriptors(), modules, Resolver(), Array.Empty<string>() }); throw new Exception("Obsolete call accepted"); }
                catch (TargetParameterCountException) { }
            } finally { foreach (var m in modules.Values) m.Dispose(); } });
        Check("FC06-disposed-set-rejected", () => { var set = Make(); set.Dispose(); try { var x = set.GetModule("mscorlib"); throw new Exception("Disposed set allowed"); } catch (ObjectDisposedException) { } });
        Check("FC07-null-descriptors", () => MustRejectNull(() => SyntheticCompiledAssemblySet.Create(null, new Dictionary<string, ModuleDefMD>(), Resolver(), Array.Empty<string>()), "descriptors"));
        Check("FC08-null-modules", () => MustRejectNull(() => SyntheticCompiledAssemblySet.Create(Descriptors(), null, Resolver(), Array.Empty<string>()), "modules"));
        Check("FC09-null-resolver", () => MustRejectNull(() => SyntheticCompiledAssemblySet.Create(Descriptors(), new Dictionary<string, ModuleDefMD>(), null, Array.Empty<string>()), "resolver"));
        Check("FC10-null-deferred", () => MustRejectNull(() => SyntheticCompiledAssemblySet.Create(Descriptors(), new Dictionary<string, ModuleDefMD>(), Resolver(), null), "deferredFacadeReferences"));
        Check("FC11-mutable-policy-not-qualification", () => { using (var set = Make()) { set.Assemblies["Consumer"].isShadowCapable = true; Require(set.Sources.Count == 0, "Mutation invented loaded bytes"); } });
        Check("FC12-deferred-boundary-preserved", () => { using (var set = SyntheticCompiledAssemblySet.Create(Descriptors(), Modules(), Resolver(), new[] { "Image" })) Require(set.DeferredFacadeReferences.SequenceEqual(new[] { "Image" }), "Deferred policy input changed"); });
        File.WriteAllText(Path.Combine(args[1], "results.json"), JsonSerializer.Serialize(new {
            schemaVersion = 1, kind = "R03SyntheticFixtureConstructorContracts", result = failures == 0 ? "Passed" : "Failed",
            failures, cases = Results, originalFourArgumentException = "TargetParameterCountException",
            unityEditorRun = false, acquisitionPolicyAssertionsExecuted = false, qualificationAuthorized = false, expansionAuthorized = false
        }, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        return failures == 0 ? 0 : 1;
    }
}
