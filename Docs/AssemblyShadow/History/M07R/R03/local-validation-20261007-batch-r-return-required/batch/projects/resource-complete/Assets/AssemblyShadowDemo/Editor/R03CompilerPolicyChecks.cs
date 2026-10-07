using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using HybridCLR.AssemblyShadow.CodeGen;
using HybridCLR.Editor.AssemblyShadow;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace AssemblyShadowDemo.Editor
{
    // Shared with the pinned-Mono check. Actual CodeGen verifier and actual
    // BootstrapIsolationRule are used. No fabricated Unity compiler inventory.
    public static class R03CompilerPolicyChecks
    {
        public const string RawPath = "ProjectSettings/AssemblyShadowRawTypeAdmissions.json";
        public const string DependencyPath = "ProjectSettings/AssemblyShadowDependencies.json";
        public const string CallSite = "AssemblyShadowDemo.R03CompletionExecution::OnQuit";
        public const string Provider = "AssemblyA.Implementation.Internal";
        public const string TypeName = Provider + ".M06ExecutionWitness";
        public const string Target = TypeName + ", " + Provider;
        public const string RawSha = "0958d5c98ee7cdfa3662f9942687926343de95523398451c423ee5de38aa5a4c";
        [Serializable] public sealed class Input { public string path, sha256; }
        [Serializable] public sealed class Site
        {
            public string id, consumerAssemblyIdentity, consumerSha256, providerAssemblyIdentity, providerSha256;
            public string providerInventoryHash, methodSignature, methodHash, operationSignature;
            public int operationIndex;
        }
        [Serializable] public sealed class Control
        {
            public string id, operation, mode, omittedModule, configurationPath, configurationSha256;
            public string expected, actual, result;
        }
        [Serializable] public sealed class Observation
        {
            public string kind = "R03CompilerPolicyChecks", mode, rawSha256, dependencySha256, onQuitMethodHash;
            public string snapshotSha256;
            public Input[] moduleFiles;
            public Site[] sites;
            public List<Control> controls = new List<Control>();
            public bool linkedProofExecuted, runtimeAcceptance, expansionAuthorized;
        }
        public static Observation Run(string project, string snapshot, string controls, string mode)
        {
            Require(!Directory.Exists(controls), "Unused compiler-policy controls required.");
            Directory.CreateDirectory(controls);
            byte[] bytes = File.ReadAllBytes(Path.Combine(project, RawPath));
            Require(ShadowHash.Bytes(bytes) == RawSha, "Original operation-bound configuration changed.");
            string dependency = File.ReadAllText(Path.Combine(project, DependencyPath));
            var configuration = RawTypeAdmissionConfiguration.Parse(bytes);
            Require(configuration.schemaVersion == 2 && configuration.sites.Length == 25 && mode == "Development", "Exact compiler fixture domain.");
            var receiptPath = Path.Combine(snapshot, "assembly-snapshot.json");
            var receipt = JObject.Parse(File.ReadAllText(receiptPath));
            Require((string)receipt["kind"] == "CompilePlayerScripts", "Compiler snapshot only; no linked/runtime claim.");
            var modules = new Dictionary<string, ModuleDefMD>(StringComparer.OrdinalIgnoreCase);
            var files = new List<Input>();
            try
            {
                foreach (var row in ((JArray)receipt["assemblies"]).Concat((JArray)receipt["references"]))
                {
                    string path = ShadowHash.SafeChild(snapshot, (string)row["path"]), name = (string)row["name"];
                    byte[] data = File.ReadAllBytes(path);
                    Require(ShadowHash.Bytes(data) == (string)row["sha256"], "Snapshot input changed: " + name);
                    modules.Add(name, ModuleDefMD.Load(data));
                    files.Add(new Input { path = path, sha256 = ShadowHash.Bytes(data) });
                }
                var verified = RawTypeAdmissionVerifier.Verify(modules, configuration, mode);
                Require(verified.Length == 25, "Every raw operation must be verified.");
                var method = modules["AssemblyShadowDemo.Bootstrap"].GetTypes().SelectMany(t => t.Methods)
                    .Single(m => m.FullName == "System.Boolean " + CallSite + "()");
                Require(method.HasBody && method.Body.Instructions.Count(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == Target) == 1 &&
                    method.Body.Instructions.Count(i => i.Operand is IMethod && ((IMethod)i.Operand).FullName == "System.Type System.Type::GetType(System.String,System.Boolean)") == 1,
                    "The actual OnQuit acquisition is not the reviewed finite literal.");
                var result = new Observation { mode = mode, rawSha256 = ShadowHash.Bytes(bytes), dependencySha256 = ShadowHash.Bytes(System.Text.Encoding.UTF8.GetBytes(dependency)),
                    snapshotSha256 = ShadowHash.File(receiptPath), onQuitMethodHash = ReflectionBindingFingerprint.Compute(method), moduleFiles = files.ToArray(),
                    sites = verified.OrderBy(s => s.SiteId, StringComparer.Ordinal).Select(s => new Site { id = s.SiteId,
                        consumerAssemblyIdentity = s.ConsumerAssemblyIdentity, consumerSha256 = s.ConsumerSha256,
                        providerAssemblyIdentity = s.ProviderAssemblyIdentity, providerSha256 = s.ProviderSha256, providerInventoryHash = s.ProviderInventoryHash,
                        methodSignature = s.MethodSignature, methodHash = s.MethodHash, operationIndex = s.OperationIndex, operationSignature = s.OperationSignature }).ToArray() };
                for (int index = 1; index <= 8; index++)
                {
                    var raw = JObject.Parse(System.Text.Encoding.UTF8.GetString(bytes));
                    string controlMode = mode, omitted = null;
                    if (index == 3)
                    {
                        string methodName = (string)raw["sites"][0]["methodSignature"];
                        foreach (var site in raw["sites"].Where(s => (string)s["methodSignature"] == methodName))
                            foreach (var variant in site["compilerVariants"].Where(v => (string)v["compilerMode"] == mode)) variant["methodHash"] = new string('0', 64);
                    }
                    if (index == 4) raw["sites"][0]["compilerVariants"][0]["operationIndex"] = 100000;
                    if (index == 5) raw["sites"][0]["providerAssemblyIdentity"] = "AssemblyA.Contracts, Version=9.0.0.0, Culture=neutral, PublicKeyToken=null";
                    if (index == 6) controlMode = null;
                    if (index == 7) omitted = "AssemblyShadowDemo.Bootstrap";
                    if (index == 8) ((JArray)raw["sites"][0]["compilerVariants"]).RemoveAt(1);
                    string[] expected = { "Success", "MissingRawAdmissionEvidence", "RawAdmissionMethodHashMismatch", "RawAdmissionOperationMismatch",
                        "RawAdmissionProviderIdentityMismatch", "RawAdmissionCompilerModeMissing", "RawAdmissionConsumerMissing", "InvalidRawAdmissionMethodVariants" };
                    string path = Path.Combine(controls, "R" + index.ToString("D2") + ".json");
                    Write(path, index == 2 ? "null" : raw.ToString(Formatting.Indented));
                    var row = new Control { id = "R" + index.ToString("D2"), operation = "RawTypeAdmissionVerifier.Verify", mode = controlMode, omittedModule = omitted,
                        configurationPath = path, configurationSha256 = ShadowHash.File(path), expected = expected[index-1] };
                    try
                    {
                        var active = modules.Where(p => p.Key != omitted).ToDictionary(p => p.Key, p => p.Value, StringComparer.OrdinalIgnoreCase);
                        RawTypeAdmissionVerifier.Verify(active, index == 2 ? null : RawTypeAdmissionConfiguration.Parse(File.ReadAllBytes(path)), controlMode);
                        row.actual = "Success";
                    }
                    catch (ReflectionBindingException error) { row.actual = error.Code; }
                    row.result = row.actual == row.expected ? "Passed" : "Failed"; result.controls.Add(row);
                }
                MethodInfo approval = typeof(ShadowAssemblyPolicyValidator).Assembly.GetType("HybridCLR.Editor.AssemblyShadow.BootstrapIsolationRule", true)
                    .GetMethod("IsApprovedReflection", BindingFlags.Public | BindingFlags.Static);
                Require(approval != null, "Actual bootstrap isolation rule required.");
                for (int index = 1; index <= 8; index++)
                {
                    var document = JObject.Parse(dependency);
                    var entry = document["bootstrapEntrypoints"].Single(e => (string)e["method"] == CallSite);
                    if (index == 2) entry.Remove();
                    if (index == 3) entry["method"] = CallSite + "Wrong";
                    if (index == 4) entry["provider"] = "AssemblyA.Contracts";
                    if (index == 5) entry["typeName"] = TypeName + "Wrong";
                    if (index == 6) entry["target"] = Target + "Wrong";
                    if (index == 7) entry["consumer"] = "Other.Bootstrap";
                    if (index == 8) entry["reason"] = "";
                    string path = Path.Combine(controls, "B" + index.ToString("D2") + ".json"); Write(path, document.ToString(Formatting.Indented));
                    var policy = new ShadowPolicyConfiguration { dependencies = JsonConvert.DeserializeObject<ShadowDependencyConfiguration>(File.ReadAllText(path)) };
                    bool allowed = (bool)approval.Invoke(null, new object[] { new AssemblyPolicyDefinition { name = "AssemblyShadowDemo.Bootstrap", isBootstrap = true },
                        CallSite + "|" + Target, policy, new DateTime(2026,10,4,0,0,0,DateTimeKind.Utc), Provider, TypeName });
                    result.controls.Add(new Control { id = "B" + index.ToString("D2"), operation = "BootstrapIsolationRule.IsApprovedReflection",
                        configurationPath = path, configurationSha256 = ShadowHash.File(path), expected = index == 1 ? "Approved" : "Rejected",
                        actual = allowed ? "Approved" : "Rejected", result = allowed == (index == 1) ? "Passed" : "Failed" });
                }
                Write(Path.Combine(controls, "observation.json"), JsonConvert.SerializeObject(result, Formatting.Indented));
                Require(result.controls.Count == 16 && result.controls.All(c => c.result == "Passed"), "Compiler policy guard control failed; retain observation.");
                return result;
            }
            finally { foreach (var module in modules.Values) module.Dispose(); }
        }
        internal static void Write(string path, string text)
        {
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new System.Text.UTF8Encoding(false))) writer.Write(text);
        }
        internal static void Require(bool value, string message) { if (!value) throw new InvalidOperationException(message); }
    }
}
