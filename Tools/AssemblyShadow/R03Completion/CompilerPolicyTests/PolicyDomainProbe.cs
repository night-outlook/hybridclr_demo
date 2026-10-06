using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using Newtonsoft.Json;

// Runs the real package implementation against immutable O receipts and DLLs.
// The source-policy fixture is reconstructed from captured original role stamps;
// this is not a new Unity compiler run or permission to accept historical O.
internal static class PolicyDomainProbe
{
    private static readonly string[] Providers = {
        "Unity.Burst.Unsafe", "Unity.RenderPipelines.Universal.2D.Internal", "Unity.RenderPipelines.Universal.Config.Runtime" };
    private static readonly string[] Consumers = { "Unity.Burst", "Unity.RenderPipelines.Universal.Runtime" };
    private static T Clone<T>(T value) { return JsonConvert.DeserializeObject<T>(JsonConvert.SerializeObject(value)); }
    private static void Check(bool value, string message) { if (!value) throw new InvalidOperationException(message); }
    private static void Reject(Action action, string code)
    {
        try { action(); }
        catch (ShadowBuildException error) { Check(error.Code == code, "Expected " + code + ", got " + error); return; }
        throw new InvalidOperationException("Expected rejection: " + code);
    }
    private static AssemblyCapability Find(ShadowPolicyConfiguration policy, string name)
    { return policy.assemblies.Single(row => string.Equals(row.name, name, StringComparison.OrdinalIgnoreCase)); }
    private static ShadowPolicyConfiguration Derive(ShadowPolicyConfiguration source, AssemblySnapshotReceipt player)
    { return ShadowFilteredInputPolicy.ApplyPatch(source, player, source.assemblies.Where(a => a.isShadowCapable).Select(a => a.name), source.assemblies.Where(a => a.isBootstrap).Select(a => a.name)); }

    private static int Main(string[] args)
    {
        if (args.Length != 4) throw new ArgumentException("captured-policy player-receipt compiler-snapshot unused-result");
        Check(!File.Exists(args[3]), "Unused result required");
        var captured = JsonConvert.DeserializeObject<ShadowPolicyConfiguration>(File.ReadAllText(args[0]));
        var player = JsonConvert.DeserializeObject<AssemblySnapshotReceipt>(File.ReadAllText(args[1]));
        var compiler = JsonConvert.DeserializeObject<AssemblySnapshotReceipt>(File.ReadAllText(Path.Combine(args[2], "assembly-snapshot.json")));
        var source = Clone(captured);
        var stamps = player.filteredAssemblyCapabilities.Concat(player.linkerExcludedAssemblyCapabilities).ToArray();
        foreach (var original in stamps)
        {
            int index = Array.FindIndex(source.assemblies, row => string.Equals(row.name, original.name, StringComparison.OrdinalIgnoreCase));
            Check(index >= 0, "Captured source role missing"); source.assemblies[index] = Clone(original);
        }
        Check(source.assemblies.All(row => row.classification != AssemblyClassification.BuildFiltered), "No derived source role");
        Check(AssemblySnapshot.ComputeHash(player) == player.snapshotHash && AssemblySnapshot.ComputeHash(compiler) == compiler.snapshotHash,
            "Immutable O source receipt hashes");
        var names = new HashSet<string>(Consumers.Concat(Providers), StringComparer.OrdinalIgnoreCase);
        var refs = new Dictionary<string, string[]>(StringComparer.OrdinalIgnoreCase);
        var dllBindings = new List<object>();
        foreach (string name in Consumers.Concat(Providers))
        {
            var file = compiler.assemblies.Concat(compiler.references).Single(row => string.Equals(row.name, name, StringComparison.OrdinalIgnoreCase));
            string path = ShadowHash.SafeChild(args[2], file.path);
            Check(ShadowHash.File(path) == file.sha256, "Actual O compiler DLL bytes: " + name);
            using (var module = ModuleDefMD.Load(path))
            {
                Check(module.Assembly.Name.String == name, "Physical compiler assembly identity");
                refs[name] = module.GetAssemblyRefs().Select(row => row.Name.String).Where(names.Contains).ToArray();
                dllBindings.Add(new { name, file.sha256, identity = module.Assembly.FullName, references = refs[name] });
            }
        }
        Check(refs[Consumers[0]].SequenceEqual(new[] { Providers[0] }), "Original Burst compiler edge");
        Check(Providers.Skip(1).All(name => refs[Consumers[1]].Contains(name, StringComparer.OrdinalIgnoreCase)), "Original two URP compiler edges");
        var cases = new List<object>(); int failures = 0;
        Action<string, Action> test = (id, action) => {
            string error = null; try { action(); } catch (Exception e) { error = e.ToString(); failures++; }
            cases.Add(new { id, result = error == null ? "Passed" : "Failed", error });
        };
        Func<ShadowPolicyConfiguration, ShadowPolicyValidationResult> validate = policy => {
            var view = new ShadowPolicyConfiguration { assemblies = policy.assemblies.Where(row => names.Contains(row.name)).Select(Clone).ToArray() };
            var definitions = view.assemblies.Select(row => new AssemblyPolicyDefinition {
                name = row.name, classification = row.classification, entersPlayer = row.classification == AssemblyClassification.Runtime,
                isPrecompiled = row.isPrecompiled, capabilityDeclared = row.capabilityDeclared, references = refs[row.name]
            }).ToArray();
            return ShadowAssemblyPolicyValidator.ValidateDefinitions(definitions, view, new DateTime(2026, 10, 6, 0, 0, 0, DateTimeKind.Utc));
        };
        test("LO001-01-original-source-graph", () => validate(source).ThrowIfInvalid());
        test("LO001-02-exact-derived-provider-roles", () => {
            var derived = Derive(source, player);
            foreach (string name in Providers) Check(Find(source, name).classification == AssemblyClassification.Runtime && Find(derived, name).classification == AssemblyClassification.BuildFiltered, name);
        });
        test("LO001-03-old-domain-reuse-rejected", () => {
            var result = validate(Derive(source, player));
            Check(!result.IsValid, "Player policy cannot validate the source graph");
            foreach (string name in Providers)
                Check(result.Diagnostics.Any(d => d.code == "RuntimeReferencesFilteredAssembly" && d.message.EndsWith(name + ".", StringComparison.Ordinal)), "Guard remains for " + name);
        });
        test("LO001-04-no-source-alias", () => {
            string before = JsonConvert.SerializeObject(source); var derived = Derive(source, player);
            Find(derived, Consumers[0]).isShadowCapable = true;
            derived.dependencies.runtimeDependencies = new[] { new DeclaredRuntimeDependency { consumer = "synthetic-copy-only" } };
            if (derived.allowedInternalEditorAssemblies.Length > 0) derived.allowedInternalEditorAssemblies[0] = "synthetic-copy-only";
            Check(JsonConvert.SerializeObject(source) == before, "Derived analysis mutated the source policy");
        });
        test("LO001-05-derived-policy-cannot-be-source", () => Reject(() => Derive(Derive(source, player), player), "FilteredRoleChanged"));
        test("LO001-06-filter-receipt-hash", () => { var changed = Clone(player); changed.snapshotHash = new string('f', 64); Reject(() => Derive(source, changed), "FilterEvidenceHashMismatch"); });
        test("LO001-07-filtered-candidate-promotion", () => { var changed = Clone(source); Find(changed, Providers[0]).isShadowCapable = true; Reject(() => Derive(changed, player), "FilteredCandidatePromotion"); });
        test("LO001-08-filtered-bootstrap-promotion", () => { var changed = Clone(source); Find(changed, Providers[0]).isBootstrap = true; Reject(() => Derive(changed, player), "FilteredCandidatePromotion"); });
        test("LO001-09-original-role-mutation", () => { var changed = Clone(source); Find(changed, Providers[0]).isPrecompiled = !Find(changed, Providers[0]).isPrecompiled; Reject(() => Derive(changed, player), "FilteredRoleChanged"); });
        test("LO001-10-source-still-valid-after-analysis", () => { Derive(source, player); validate(source).ThrowIfInvalid(); });
        using (var file = new FileStream(args[3], FileMode.CreateNew))
        using (var writer = new StreamWriter(file, new System.Text.UTF8Encoding(false)))
            writer.Write(JsonConvert.SerializeObject(new {
                kind = "R03LOPolicyDomainRegression", result = failures == 0 ? "Passed" : "Failed", failures, cases, dllBindings,
                basis = "CapturedOriginalRolesAndCompilerAssemblyRefs", graphScope = "TwoConsumersThreeProviders",
                unityEditorRun = false, playerRun = false, freshCompilerSnapshot = false, runtimeAcceptance = false,
                historicalOResult = "Failed", historicalEvidenceModified = false, R03Accepted = false, H2Passed = false
            }, Formatting.Indented));
        Console.WriteLine("LO_POLICY_DOMAIN_CASES=" + cases.Count + " FAILURES=" + failures);
        return failures == 0 ? 0 : 1;
    }
}
