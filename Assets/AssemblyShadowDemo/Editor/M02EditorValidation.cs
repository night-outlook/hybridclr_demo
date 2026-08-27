using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Real target-compiler integration cases; NUnit supplies adversarial unit coverage separately.</summary>
    public static class M02EditorValidation
    {
        private const string Internal = "AssemblyA.Implementation.Internal";
        private const string Extensibility = "AssemblyA.Implementation.Extensibility";
        private const string Contracts = "AssemblyA.Contracts";

        public static void Validate()
        {
            var report = new ValidationReport { schemaVersion = 1, unityVersion = Application.unityVersion, target = EditorUserBuildSettings.activeBuildTarget.ToString() };
            var cases = new List<CaseResult>();
            string run = Path.GetFullPath("_temp/AssemblyShadow/M02Validation-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(run);
            report.runDirectory = run;
            try
            {
                var settings = AssemblyShadowSettings.Instance;
                var session = ShadowBuildSession.Load();
                var target = EditorUserBuildSettings.activeBuildTarget;
                var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
                var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
                string baselinePath = session.baselineManifestPath;
                Require(File.Exists(baselinePath), "Build the M02 Player baseline first.");
                report.baselineManifestPath = Path.GetFullPath(baselinePath);
                report.baselineManifestSha256 = ShadowHash.File(baselinePath);
                var snapshots = new Dictionary<string, string>();
                var patches = new Dictionary<string, ShadowPatchManifest>();
                var patchPaths = new List<Artifact>();
                foreach (string patch in new[] { "P01", "P02", "P03", "P05" })
                {
                    string snapshot = AssemblySnapshot.Compile(Path.Combine(run, patch + "-compile"), target, settings.architecture, pins, policy, new[] { "ASSEMBLY_SHADOW_" + patch });
                    snapshots.Add(patch, snapshot);
                }
                Func<string, bool, ShadowPolicyConfiguration, string, ShadowPatchManifest> build = (patch, dllOnly, configuration, suffix) =>
                {
                    string output = Path.Combine(run, patch + suffix);
                    var manifest = ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest
                    {
                        baselineManifestPath = baselinePath, currentCompileSnapshot = snapshots[patch], outputDirectory = output,
                        patchId = patch, target = target, architecture = settings.architecture, sourcePins = pins, policy = configuration,
                        dllOnly = dllOnly, includePdb = true,
                    });
                    string path = Path.Combine(output, "patch-manifest.json");
                    patchPaths.Add(new Artifact { id = patch + suffix, path = path, sha256 = ShadowHash.File(path) });
                    return manifest;
                };
                RunCase(cases, "T02-01", () =>
                {
                    var patch = build("P01", true, policy, ""); patches.Add("P01", patch);
                    EqualNames(new[] { Internal }, patch.changedRoots); EqualNames(new[] { Internal }, patch.loadOrder);
                });
                RunCase(cases, "T02-02", () =>
                {
                    var patch = build("P02", true, policy, ""); patches.Add("P02", patch);
                    EqualNames(new[] { Extensibility }, patch.changedRoots);
                    EqualNames(new[] { Extensibility, Internal, "AssemblyShadowDemo.ExtensibilityConsumer" }, patch.loadOrder);
                    Require(Array.IndexOf(patch.loadOrder, Extensibility) < Array.IndexOf(patch.loadOrder, Internal), "Dependency must precede consumer.");
                });
                RunCase(cases, "T02-03", () =>
                {
                    var patch = build("P03", true, policy, ""); patches.Add("P03", patch);
                    EqualNames(new[] { Contracts }, patch.changedRoots); EqualNames(M02Build.Candidates, patch.loadOrder);
                    Require(patch.loadOrder[0] == Contracts, "Contracts must load first.");
                });
                RunCase(cases, "T02-04", () =>
                {
                    var bad = JsonUtility.FromJson<ShadowPolicyConfiguration>(JsonUtility.ToJson(policy));
                    bad.assemblies.Single(a => a.name == "AssemblyShadowDemo.ContractsConsumer").isShadowCapable = false;
                    var error = ExpectFailure(() => build("P03", true, bad, "-missing-consumer"), "NonShadowConsumer");
                    Require(error.Message.Contains("AssemblyShadowDemo.ContractsConsumer") && error.Message.Contains(Contracts), "Missing full reverse dependency path.");
                });
                RunCase(cases, "T02-05", () => ValidateBadAsmdefBeforeCompile(Path.Combine(run, "illegal-asmdef"), target));
                RunCase(cases, "T02-06", () =>
                {
                    var error = ExpectFailure(() => build("P05", true, policy, "-rejected-dll-only"), "ResourceRebuildRequired");
                    Require(error.Message.Contains("versioned-prefab.bundle"), "Missing affected prefab bundle.");
                    var patch = build("P05", false, policy, "-requires-bundles"); patches.Add("P05", patch);
                    EqualNames(new[] { "business-scene.bundle", "versioned-prefab.bundle" }, patch.resourceBundlesRequired);
                    Require(!patch.dllOnly && patch.resourceChangeLevel == "ResourceRebuildRequired", "P05 must require resources.");
                });
                RunCase(cases, "T02-07", () =>
                {
                    Require(patches["P01"].dllOnly && patches["P01"].resourceBundlesRequired.Length == 0, "P01 must be DLL-only.");
                    Require(patches["P01"].resourceAbiHash == patches["P01"].baselineResourceAbiHash, "Method body must not change Resource ABI.");
                });
                RunCase(cases, "M02-Repeatability", () =>
                {
                    build("P01", true, policy, "-repeat");
                    Require(ShadowHash.File(Path.Combine(run, "P01/patch-manifest.json")) == ShadowHash.File(Path.Combine(run, "P01-repeat/patch-manifest.json")), "Same snapshot yielded different patch manifests.");
                    string repeated = Path.Combine(run, "baseline-repeat");
                    ShadowBaselineManifestBuilder.Build(new ShadowBaselineBuildRequest
                    {
                        buildId = session.baselineBuildId, playerInputSnapshot = session.playerInputSnapshot, outputDirectory = repeated,
                        resourceBaselinePath = session.resourceBaselinePath,
                        target = target, architecture = settings.architecture, sourcePins = pins, policy = policy,
                        resources = JsonUtility.FromJson<ShadowResourceBuildMap>(File.ReadAllText(settings.resourceBuildMapPath)),
                    });
                    Require(ShadowHash.File(Path.Combine(repeated, "baseline-manifest.json")) == ShadowHash.File(baselinePath), "Same Player snapshot yielded different baseline manifests.");
                });
                RunCase(cases, "M02-SnapshotTamper", () =>
                {
                    var receipt = AssemblySnapshot.ReadAndVerify(snapshots["P01"], false);
                    string dll = Path.Combine(snapshots["P01"], receipt.assemblies.First(a => a.name == Internal).path);
                    byte[] original = File.ReadAllBytes(dll);
                    try
                    {
                        byte[] modified = (byte[])original.Clone(); modified[modified.Length - 1] ^= 1; File.WriteAllBytes(dll, modified);
                        ExpectFailure(() => AssemblySnapshot.ReadAndVerify(snapshots["P01"], false), "SnapshotHashMismatch");
                    }
                    finally { File.WriteAllBytes(dll, original); }
                    AssemblySnapshot.ReadAndVerify(snapshots["P01"], false);
                });
                report.artifacts = patchPaths.ToArray();
                report.result = "Passed";
            }
            catch (Exception error)
            {
                report.result = "Failed"; report.error = error.ToString(); throw;
            }
            finally
            {
                report.cases = cases.ToArray();
                File.WriteAllText("_temp/AssemblyShadow/m02-editor-validation.json", JsonUtility.ToJson(report, true));
                Debug.Log("[AssemblyShadow M02] " + JsonUtility.ToJson(report));
            }
        }

        private static void ValidateBadAsmdefBeforeCompile(string root, BuildTarget target)
        {
            Directory.CreateDirectory(Path.Combine(root, "Assets/Provider"));
            Directory.CreateDirectory(Path.Combine(root, "Assets/Consumer"));
            File.WriteAllText(Path.Combine(root, "Assets/Provider/Provider.asmdef"), "{\"name\":\"AssemblyA.Implementation.Internal\",\"references\":[]}");
            File.WriteAllText(Path.Combine(root, "Assets/Consumer/Consumer.asmdef"), "{\"name\":\"Bad.External\",\"references\":[\"AssemblyA.Implementation.Internal\"]}");
            var policy = new ShadowPolicyConfiguration { assemblies = new[] {
                new AssemblyCapability { name = Internal, isShadowCapable = true }, new AssemblyCapability { name = "Bad.External" }
            } };
            var result = ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target, root);
            Require(!result.IsValid && result.Errors.Any(e => e.Contains("Internal") && e.Contains("Bad.External")), "Illegal external Internal reference was not rejected before invoking the compiler.");
        }

        private static ShadowBuildException ExpectFailure(Action action, string code)
        {
            try { action(); }
            catch (ShadowBuildException error) { Require(error.Code == code, "Expected " + code + ", got " + error); return error; }
            throw new BuildFailedException("Expected failure " + code + " did not occur.");
        }

        private static void RunCase(List<CaseResult> cases, string id, Action test)
        {
            var result = new CaseResult { id = id };
            cases.Add(result);
            try { test(); result.passed = true; }
            catch (Exception error) { result.error = error.ToString(); throw; }
        }
        private static void EqualNames(IEnumerable<string> expected, IEnumerable<string> actual) { Require(expected.OrderBy(v => v).SequenceEqual(actual.OrderBy(v => v)), "Unexpected set: " + string.Join(", ", actual.ToArray())); }
        private static void Require(bool condition, string message) { if (!condition) throw new BuildFailedException(message); }
        [Serializable] private sealed class CaseResult { public string id; public bool passed; public string error; }
        [Serializable] private sealed class Artifact { public string id; public string path; public string sha256; }
        [Serializable] private sealed class ValidationReport { public int schemaVersion; public string result; public string error; public string unityVersion; public string target; public string runDirectory; public string baselineManifestPath; public string baselineManifestSha256; public CaseResult[] cases; public Artifact[] artifacts; }
    }
}
