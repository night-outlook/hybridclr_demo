using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using dnlib.DotNet;
using AssemblyShadow.R03.Fixtures;

internal static class Program
{
    private static string Hash(byte[] b) => Convert.ToHexString(SHA256.HashData(b)).ToLowerInvariant();
    private static void Need(bool ok, string detail) { if (!ok) throw new InvalidDataException(detail); }
    private static byte[] Key(AssemblyRef r) => r.PublicKeyOrToken?.Data ?? Array.Empty<byte>();

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--player" || args[2] != "--output") return 2;
        string player = Path.GetFullPath(args[1]), output = Path.GetFullPath(args[3]);
        Need(Directory.Exists(player) && !Directory.Exists(output) && !File.Exists(output), "Existing player inputs and unused audit root required");
        Directory.CreateDirectory(output);
        string shared = Path.Combine(output, "shared");
        EvolutionFixtureCorpus.Write(shared);
        var playerFiles = Directory.GetFiles(player, "*.dll", SearchOption.AllDirectories).OrderBy(p => p, StringComparer.Ordinal).ToArray();
        var sharedFiles = Directory.GetFiles(shared, "*.dll", SearchOption.AllDirectories).OrderBy(p => p, StringComparer.Ordinal).ToArray();
        Need(playerFiles.Length == 15 && sharedFiles.Length == 18, "Exact original fixture inventory required");
        var cases = new List<object>();
        foreach (var group in new[] { (name: "player", root: player, files: playerFiles), (name: "shared", root: shared, files: sharedFiles) })
        foreach (string file in group.files)
        {
            byte[] bytes = File.ReadAllBytes(file);
            using var m = ModuleDefMD.Load(bytes);
            Need(!m.Assembly.HasPublicKey && (m.Assembly.PublicKey?.Data?.Length ?? 0) == 0, "Fixture definition must remain unsigned: " + file);
            var refs = m.GetAssemblyRefs().ToArray();
            foreach (var r in refs)
            {
                Need(!r.HasPublicKey, "Fixture AssemblyRef unexpectedly claims a full public key: " + file + " -> " + r.Name);
                Need(Key(r).Length == (r.Name == "mscorlib" ? 8 : 0), "Invalid token length: " + file + " -> " + r.Name);
                if (r.Name == "mscorlib") continue;
                Need(r.Name == "A" || r.Name == "B", "Unexpected provider: " + r.Name);
                Need(r.Version == new Version(1, 0, 0, 0) && UTF8String.IsNullOrEmpty(r.Culture), "Provider identity changed");
                string peer = Path.Combine(Path.GetDirectoryName(file), r.Name + ".dll");
                Need(File.Exists(peer), "Provider bytes missing: " + peer);
                using var provider = ModuleDefMD.Load(File.ReadAllBytes(peer));
                Need(provider.Assembly.Name == r.Name && provider.Assembly.Version == r.Version && !provider.Assembly.HasPublicKey, "Reference/definition mismatch");
            }
            var node = m.GetTypes().Single(t => t.FullName == "R03.Node");
            var witness = node.Fields.Where(f => f.Name == "provider").ToArray();
            if (group.name == "player") Need(witness.All(f => f.IsStatic), "Player graph witness changed instance layout");
            string relative = Path.GetRelativePath(group.root, file).Replace('\\', '/');
            // Expected graph direction is independently declared; a valid token must not drop edges.
            string expected = null;
            if (m.Assembly.Name == "A" && (relative.Contains("baseline/") || relative.StartsWith("baseline/") || relative.Contains("true-cycle/") || relative.Contains("cumulative/"))) expected = "B";
            if (m.Assembly.Name == "B" && (relative.Contains("true-cycle/") || relative.StartsWith("reversal/") && !relative.Contains("baseline/"))) expected = "A";
            var actual = refs.Where(r => r.Name != "mscorlib").Select(r => r.Name.String).ToArray();
            Need(actual.SequenceEqual(expected == null ? Array.Empty<string>() : new[] { expected }), "Graph edges changed: " + relative);
            string id = group.name + "-" + cases.Count.ToString("D2");
            string source = Path.Combine(output, id + ".cs");
            var keep = node.Methods.Single(method => method.Name == "Keep");
            string invocation = keep.IsStatic ? "Subject::R03.Node.Keep()" : "n.Keep()";
            File.WriteAllText(source, "extern alias Subject;\npublic static class Consumer { public static System.Type Type() => typeof(Subject::R03.Node); public static int Invoke(Subject::R03.Node n) => " + invocation + "; }\n");
            cases.Add(new { id, input = file, inputSha256 = Hash(bytes), source, sourceSha256 = Hash(File.ReadAllBytes(source)),
                references = refs.Select(r => new { name = r.Name.String, flags = (uint)r.Attributes, keyBytes = Key(r).Length }).ToArray(),
                peers = Directory.GetFiles(Path.GetDirectoryName(file), "*.dll").Where(p => p != file).OrderBy(p => p, StringComparer.Ordinal)
                    .Select(p => new { path = p, sha256 = Hash(File.ReadAllBytes(p)) }).ToArray() });
        }
        // Deliberate negative copy; never change the generated or sealed input corpus.
        string badDir = Path.Combine(output, "invalid-key"); Directory.CreateDirectory(badDir);
        string badPath = Path.Combine(badDir, "A.dll");
        using (var bad = ModuleDefMD.Load(File.ReadAllBytes(Path.Combine(player, "baseline/A.dll"))))
        {
            var reference = bad.GetAssemblyRefs().Single(r => r.Name == "B");
            reference.PublicKeyOrToken = new PublicKey(); reference.HasPublicKey = true;
            bad.Write(badPath);
        }
        using (var bad = ModuleDefMD.Load(File.ReadAllBytes(badPath)))
        {
            var reference = bad.GetAssemblyRefs().Single(r => r.Name == "B");
            Need(reference.HasPublicKey && Key(reference).Length == 0, "Negative control must reproduce the exact malformed reference");
        }
        var result = new { kind = "R03FixtureMetadataAudit", schemaVersion = 1, result = "Passed", cases,
            negative = new { input = badPath, inputSha256 = Hash(File.ReadAllBytes(badPath)), peer = Path.Combine(player, "baseline/B.dll"), expectedDiagnostic = "CS0009" },
            compilerConsumption = "NotRun", nativeExecution = false, runtimeAcceptance = false };
        File.WriteAllText(Path.Combine(output, "results.json"), JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        Console.WriteLine("33 fixture metadata contracts passed; compiler consumption remains separate.");
        return 0;
    }
}
