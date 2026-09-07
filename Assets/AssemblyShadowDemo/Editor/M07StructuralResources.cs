using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Extends the crash-safe M02 P05 define workflow with a matching resource
    /// build. Every public method is intended for a separate Editor process.
    /// </summary>
    public static class M07StructuralResources
    {
        private const string ReceiptName = "m07-p05-structural.json";

        public static void Prepare()
        {
            M02StructuralPatchCompilation.Prepare();
        }

        public static void Compile()
        {
            M02StructuralPatchCompilation.Compile();
            string run = M02StructuralPatchCompilation.GetValidationRunDirectory();
            string snapshot = M02StructuralPatchCompilation.ReadCompiledSnapshotInStagedDomain(run);
            var settings = AssemblyShadowSettings.Instance;
            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var session = ShadowBuildSession.Load();
            Require(File.Exists(session.baselineManifestPath), "M07 P05 requires the successful M07 baseline manifest.");
            ShadowBaselineManifest baseline = M07Build.ReadBaseline(session.baselineManifestPath);
            Require(baseline.baselineBuildId == settings.buildId && baseline.runtimeAbiHash == pins.RuntimeAbiHash(),
                "M07 P05 baseline/source identity differs from the prepared structural context.");
            ShadowResourceBuildMap map = M07SourceAssets.Ensure(true);
            string resources = Path.Combine(run, "P05-Resources");
            string frozen = ShadowResourceBaseline.Build(new ShadowResourceBuildRequest {
                outputDirectory = resources, target = target, architecture = settings.architecture, sourcePins = pins,
                policy = policy, resources = map, extraScriptingDefines = new[] { M07Build.P05Define },
                captureCompilerMode = true, developmentBuild = true,
            });
            string p05DllOnlySnapshot = AssemblySnapshot.CompileWithOptions(Path.Combine(run, "P05-DllOnly-compile"),
                target, settings.architecture, pins, policy, new[] { M07Build.P01Define, M07Build.P05Define }, true);
            M07Build.M07Fixture fixture = M07Build.BuildFixtureFromSnapshot(run, "P05", new[] { M07Build.P05Define },
                new[] { "AssemblyA.Implementation.Internal" }, false, target, settings.architecture, pins, policy, session.baselineManifestPath, snapshot);
            VerifiedShadowResourceBaseline replacement = ShadowResourceBaseline.ReadAndVerify(frozen, target, settings.architecture);
            Require(fixture.resourceChangeLevel == ResourceAbiDiffLevel.ResourceRebuildRequired.ToString() &&
                fixture.baselineResourceAbiHash == baseline.resourceAbiHash && fixture.resourceAbiHash == replacement.Receipt.resourceAbiHash &&
                fixture.resourceBundlesRequired != null && fixture.resourceBundlesRequired.Length > 0 &&
                replacement.Receipt.bundles.Select(item => item.name).SequenceEqual(M07Build.BundleNames),
                "M07 P05 patch/resource ABI or bundle inventory is not an atomic structural replacement.");
            fixture.replacementResourcePath = Path.GetFullPath(frozen);
            fixture.replacementResourceReceiptPath = Path.Combine(fixture.replacementResourcePath, ShadowResourceBaseline.ReceiptName);
            fixture.replacementResourceReceiptSha256 = ShadowHash.File(fixture.replacementResourceReceiptPath);
            fixture.replacementBundleNames = replacement.Receipt.bundles.Select(item => item.name).ToArray();
            M04AssemblyIdentityProof.WriteNewJson(Path.Combine(run, ReceiptName), new StructuralReceipt {
                schemaVersion = 1, milestone = "M07", baselineBuildId = baseline.baselineBuildId,
                baselineManifestPath = Path.GetFullPath(session.baselineManifestPath),
                baselineManifestSha256 = ShadowHash.File(session.baselineManifestPath), fixture = fixture,
                p05DllOnlyCompileSnapshot = Path.GetFullPath(p05DllOnlySnapshot),
            });
            Debug.Log("[AssemblyShadow M07] P05 DLL/resource pair compiled in one guarded Editor domain: " + run);
        }

        public static void Restore()
        {
            M02StructuralPatchCompilation.Restore();
        }

        public static void FinalizeFixtures()
        {
            string run = M02StructuralPatchCompilation.GetValidationRunDirectory();
            M02StructuralPatchCompilation.ReadPreparedSnapshot(run); // Includes restoration and context proof.
            string receiptPath = Path.Combine(run, ReceiptName);
            Require(File.Exists(receiptPath), "M07 P05 structural receipt is missing.");
            StructuralReceipt receipt = JsonUtility.FromJson<StructuralReceipt>(File.ReadAllText(receiptPath));
            var session = ShadowBuildSession.Load();
            Require(receipt != null && receipt.schemaVersion == 1 && receipt.milestone == "M07" && receipt.fixture != null &&
                receipt.baselineBuildId == AssemblyShadowSettings.Instance.buildId && receipt.baselineManifestPath == Path.GetFullPath(session.baselineManifestPath) &&
                receipt.baselineManifestSha256 == ShadowHash.File(session.baselineManifestPath), "M07 P05 receipt does not belong to this restored baseline.");
            Require(receipt.fixture.patchManifestSha256 == ShadowHash.File(receipt.fixture.patchManifest) &&
                receipt.fixture.replacementResourceReceiptSha256 == ShadowHash.File(receipt.fixture.replacementResourceReceiptPath),
                "M07 P05 patch or resource receipt changed before publication.");
            M07Build.M07FixtureManifest manifest = M07Build.BuildFixtureManifest(run, receipt.fixture, receipt.p05DllOnlyCompileSnapshot);
            string path = M07Build.WriteFixtureManifest(run, manifest);
            string replay = M07EditorValidation.ValidateAndWriteReceipt(path);
            Debug.Log("[AssemblyShadow M07] Complete fixture manifest and independent replay: " + path + " | " + replay);
        }

        [Serializable]
        private sealed class StructuralReceipt
        {
            public int schemaVersion;
            public string milestone, baselineBuildId, baselineManifestPath, baselineManifestSha256;
            public string p05DllOnlyCompileSnapshot;
            public M07Build.M07Fixture fixture;
        }

        private static void Require(bool value, string message)
        {
            if (!value) throw new ShadowBuildException("M07StructuralResource", message);
        }
    }
}
