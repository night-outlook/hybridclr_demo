using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class R01FailureFixtures
    {
        public const string InitializerPatchId = "R01-P03-InitializerThrow";

        public static void Build()
        {
            string baselinePath = RequiredPath("-shadowR01FailureBaseline");
            string m07Path = RequiredPath("-shadowM07Fixtures");
            string output = RequiredPath("-shadowR01FailureOutput");
            Require(File.Exists(baselinePath) && File.Exists(m07Path), "Pass existing baseline and M07 manifest files.");
            Require(!File.Exists(output) && !Directory.Exists(output), "Failure fixture output must be new.");
            var settings = AssemblyShadowSettings.Instance;
            var target = EditorUserBuildSettings.activeBuildTarget;
            ShadowSourcePins pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(baselinePath));
            var m07 = JsonUtility.FromJson<M07Build.M07FixtureManifest>(File.ReadAllText(m07Path));
            Require(baseline != null && m07 != null && baseline.schemaVersion == 1 && m07.schemaVersion == 1, "Invalid input manifest schema.");
            Require(Path.GetFullPath(m07.baselineManifestPath) == baselinePath && m07.baselineManifestSha256 == ShadowHash.File(baselinePath) &&
                m07.baselineBuildId == baseline.baselineBuildId && m07.runtimeAbiHash == baseline.runtimeAbiHash, "M07 baseline binding differs.");
            Require(File.ReadAllText(Path.Combine(Path.GetDirectoryName(baselinePath), "manifest.sha256")).Trim() == ShadowHash.File(baselinePath), "Unsealed baseline.");
            ShadowSourcePins.RequireSameBuildSources(pins, baseline.sourcePins);
            Require(baseline.metadataEncodingProfile != null && baseline.metadataCapacityReport != null && baseline.metadataCapacityReport.fits,
                "Failure fixtures require the R01 capacity baseline.");
            baseline.metadataEncodingProfile.ValidateOrThrow();
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            string[] defines = { M07Build.P01Define, M07Build.P03Define, M03Build.InitializerDefine,
                M03Build.P03InitializerDefine, M03Build.InitializerThrowDefine };
            Directory.CreateDirectory(output);
            M07Build.M07Fixture initializer = M07Build.BuildFixture(output, InitializerPatchId, defines, M07Build.Candidates,
                true, target, settings.architecture, pins, policy, baselinePath);
            var snapshot = AssemblySnapshot.ReadAndVerify(initializer.compileSnapshot, false);
            ShadowSourcePins.RequireSameBuildSources(pins, snapshot.sourcePins);
            ShadowReflectionBindingEvidence.RequirePolicy(policy, initializer.compileSnapshot, snapshot, false);
            M07Build.M07Fixture replay = M07Build.BuildFixtureFromSnapshot(Path.Combine(output, "Replay"), InitializerPatchId,
                defines, M07Build.Candidates, true, target, settings.architecture, pins, policy, baselinePath, initializer.compileSnapshot);
            M05EditorValidation.VerifyArtifactTree(initializer.patchDirectory, replay.patchDirectory);
            Require(initializer.patchManifestSha256 == replay.patchManifestSha256, "Initializer replay bytes differ.");
            var patch = JsonUtility.FromJson<ShadowPatchManifest>(File.ReadAllText(initializer.patchManifest));
            Require(patch.nativeBudgetCapabilityVersion == 1 && patch.metadataCapacityReport != null && patch.metadataCapacityReport.fits &&
                patch.metadataCapacityReport.runtimeReserveMetadataBudget && patch.loadOrder.SequenceEqual(M07Build.Candidates),
                "Initializer patch lacks the complete budgeted closure.");
            string path = Path.Combine(output, "failure-fixtures.json");
            var evidence = new Receipt {
                schemaVersion = 1, kind = "R01FailureFixtures", result = "Passed", sourcePins = pins,
                baselineManifestPath = baselinePath, baselineManifestSha256 = ShadowHash.File(baselinePath),
                baselineBuildId = baseline.baselineBuildId, runtimeAbiHash = baseline.runtimeAbiHash,
                fixtureManifestPath = m07Path, fixtureManifestSha256 = ShadowHash.File(m07Path),
                initializer = initializer, replayPatchManifest = replay.patchManifest, replayPatchManifestSha256 = replay.patchManifestSha256,
                replayBytesEqual = true,
                files = Directory.GetFiles(output, "*", SearchOption.AllDirectories).OrderBy(value => value, StringComparer.Ordinal)
                    .Select(value => new FileRow { path = Path.GetFullPath(value), sha256 = ShadowHash.File(value), length = new FileInfo(value).Length }).ToArray()
            };
            M04AssemblyIdentityProof.WriteNewJson(path, evidence);
            Debug.Log("[AssemblyShadow R01] Failure fixtures and production replay: " + path);
        }

        private static string RequiredPath(string name)
        {
            string value = AssemblyShadowBuildCommands.Argument(name, "");
            Require(!string.IsNullOrEmpty(value), "Missing " + name);
            return Path.GetFullPath(value);
        }
        private static void Require(bool condition, string detail) { if (!condition) throw new BuildFailedException(detail); }
        [Serializable] private sealed class FileRow { public string path, sha256; public long length; }
        [Serializable] private sealed class Receipt
        {
            public int schemaVersion; public string kind, result, baselineBuildId, runtimeAbiHash;
            public string baselineManifestPath, baselineManifestSha256, fixtureManifestPath, fixtureManifestSha256;
            public ShadowSourcePins sourcePins; public M07Build.M07Fixture initializer;
            public string replayPatchManifest, replayPatchManifestSha256; public bool replayBytesEqual; public FileRow[] files;
        }
    }
}
