using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.AssemblyShadow.Tests;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length != 2 || args[0] != "--output") { Console.Error.WriteLine("Usage: --output <unused-directory>"); return 2; }
        string root = Path.GetFullPath(args[1]);
        if (Directory.Exists(root) || File.Exists(root)) throw new IOException("Output must be unused: " + root);
        Directory.CreateDirectory(root);
        string[] ids = R03EvolutionContractCases.CaseIds;
        if (ids.Length != 35 || ids.Distinct(StringComparer.Ordinal).Count() != 35) throw new InvalidOperationException("The complete 35-case identity set is required.");
        var results = new List<object>();
        int failures = 0;
        foreach (string id in ids)
        {
            try
            {
                R03EvolutionContractCases.Run(id, (name, bytes) =>
                {
                    string directory = Path.Combine(root, "inputs", id); Directory.CreateDirectory(directory);
                    File.WriteAllBytes(Path.Combine(directory, name), bytes);
                });
                results.Add(new { id, result = "Passed" });
            }
            catch (Exception e) { ++failures; results.Add(new { id, result = "Failed", error = e.ToString() }); }
        }
        var files = Directory.GetFiles(root, "*.dll", SearchOption.AllDirectories).OrderBy(p => p, StringComparer.Ordinal)
            .Select(p => new { path = Path.GetRelativePath(root, p).Replace('\\', '/'), size = new FileInfo(p).Length, sha256 = ShadowHash.File(p) }).ToArray();
        if (files.Length != 70) { ++failures; results.Add(new { id = "fixture-completeness", result = "Failed", expected = 70, observed = files.Length }); }
        var report = new { kind = "R03AdmissionHostEvidence", schemaVersion = 1, result = failures == 0 ? "Passed" : "Failed", failures,
            cases = results, files, unityEditorRun = false, nativeMethodInfoMapping = "NotRun", nativeLayoutProof = "NotRun", runtimeAcceptance = false };
        string json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(Path.Combine(root, "results.json"), json + "\n"); Console.WriteLine(json);
        return failures == 0 ? 0 : 1;
    }
}
