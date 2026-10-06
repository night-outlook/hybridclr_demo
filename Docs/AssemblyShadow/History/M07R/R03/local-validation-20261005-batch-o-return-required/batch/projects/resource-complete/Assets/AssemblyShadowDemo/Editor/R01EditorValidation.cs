using System;
using System.IO;
using System.Linq;
using System.Reflection;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Player;
using UnityEditor.Compilation;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Runs the R01 Editor capacity gate against one fresh positive P03 snapshot
    /// and an isolated, semantically equivalent snapshot whose last ordered DLL
    /// is padded to the native oversize boundary.
    /// </summary>
    public static class R01EditorValidation
    {
        private const string PositivePatchId = "R01-P03-CapacityControl";
        private const string RejectedPatchId = "R01-P03-CapacityOversize";
        private const ulong OversizeBoundary = 64UL * 1024UL * 1024UL;

        public static void Validate()
        {
            string baselineArgument = AssemblyShadowBuildCommands.Argument("-shadowR01Baseline", "");
            Require(!string.IsNullOrWhiteSpace(baselineArgument), "Pass -shadowR01Baseline with an R01 baseline manifest or root.");
            string receiptArgument = AssemblyShadowBuildCommands.Argument("-shadowR01ValidationReceipt", "");
            string receiptPath = string.IsNullOrWhiteSpace(receiptArgument)
                ? Path.GetFullPath("_temp/AssemblyShadow/r01-editor-validation-" + Guid.NewGuid().ToString("N") + ".json")
                : Path.GetFullPath(receiptArgument);
            string receipt = ValidateAndWriteReceipt(baselineArgument, receiptPath);
            Debug.Log("[AssemblyShadow R01] Editor capacity validation passed: " + receipt);
        }

        public static string ValidateAndWriteReceipt(string baselineArgument, string receiptPath)
        {
            string baselineManifestPath = ResolveBaselineManifest(baselineArgument);
            receiptPath = Path.GetFullPath(receiptPath);
            Require(!File.Exists(receiptPath) && !Directory.Exists(receiptPath), "R01 validation receipt is immutable: " + receiptPath);

            BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
            AssemblyShadowSettings settings = AssemblyShadowSettings.Instance;
            string architecture = settings.architecture;
            ShadowSourcePins pins = ShadowSourcePins.Read(settings.sourcePinFile, target, architecture);
            string baselineHashPath = Path.Combine(Path.GetDirectoryName(baselineManifestPath), "manifest.sha256");
            Require(File.Exists(baselineHashPath) && File.ReadAllText(baselineHashPath).Trim() == ShadowHash.File(baselineManifestPath),
                "R01 baseline manifest hash differs from its sealed receipt.");
            ShadowBaselineManifest baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(baselineManifestPath));
            Require(baseline != null, "R01 baseline manifest is malformed.");
            Require(baseline.schemaVersion == 1 && baseline.semanticHashSchema == 1, "R01 baseline schema is unsupported.");
            ShadowSourcePins.RequireSameBuildSources(pins, baseline.sourcePins);
            MetadataEncodingProfile profile = baseline.metadataEncodingProfile;
            Require(profile != null && baseline.metadataCapacityReport != null, "R01 baseline has no capacity profile/report.");
            profile.ValidateOrThrow();
            Require(baseline.metadataCapacityReport.fits && baseline.metadataCapacityReport.runtimeReserveMetadataBudget,
                "R01 baseline capacity report is not a fitting mandatory reservation.");

            string baselineRoot = Path.GetDirectoryName(baselineManifestPath);
            string playerSnapshot = ShadowHash.SafeChild(baselineRoot, baseline.playerInputSnapshot);
            AssemblySnapshotReceipt playerReceipt = AssemblySnapshot.ReadAndVerify(playerSnapshot, true);
            Require(playerReceipt.snapshotHash == baseline.playerInputSnapshotHash, "R01 baseline Player snapshot hash differs from its manifest.");
            ShadowPolicyConfiguration policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            string scratch = Path.GetFullPath("_temp/AssemblyShadow/R01EditorValidation-" + Guid.NewGuid().ToString("N"));
            Require(!Directory.Exists(scratch) && !File.Exists(scratch), "R01 validation scratch must be new: " + scratch);
            Directory.CreateDirectory(scratch);

            string positiveSnapshot = AssemblySnapshot.CompileWithOptions(Path.Combine(scratch, "positive-compile"), target, architecture,
                pins, policy, new[] { M07Build.P01Define, M07Build.P03Define }, true);
            AssemblySnapshotReceipt positiveReceipt = AssemblySnapshot.ReadAndVerify(positiveSnapshot, false);
            ShadowReflectionBindingEvidence.RequirePolicy(policy, positiveSnapshot, positiveReceipt, false);
            ShadowPatchManifest positive = ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                baselineManifestPath = baselineManifestPath, currentCompileSnapshot = positiveSnapshot,
                outputDirectory = Path.Combine(scratch, "positive-patch"), patchId = PositivePatchId, target = target,
                architecture = architecture, sourcePins = pins, policy = policy, explicitChangedRoots = M07Build.Candidates,
                dllOnly = true, includePdb = true,
            });
            MetadataCapacityReport positiveReport = VerifyPositivePatch(positive, positiveSnapshot, positiveReceipt, profile, baseline);

            string paddedAssembly = positive.loadOrder[positive.loadOrder.Length - 1];
            string paddedSnapshot = CapturePaddedSnapshot(scratch, positiveSnapshot, positiveReceipt, paddedAssembly, target, architecture, pins, policy);
            AssemblySnapshotReceipt paddedReceipt = AssemblySnapshot.ReadAndVerify(paddedSnapshot, false);
            ShadowReflectionBindingEvidence.RequirePolicy(policy, paddedSnapshot, paddedReceipt, false);
            RequireSemanticParity(positiveSnapshot, paddedSnapshot, positiveReceipt);

            MetadataCapacityInput[] rejectedInputs = MetadataCapacityPlanner.ClosureInputs(paddedSnapshot, paddedReceipt, positive.loadOrder);
            MetadataCapacityReport rejectedReport = MetadataCapacityPlanner.Plan(profile, rejectedInputs, baseline.metadataCapacityReport.cursorsAfter);
            Require(!rejectedReport.fits && rejectedReport.firstFailingAssembly == paddedAssembly && rejectedReport.failureReason == "Oversize",
                "R01 padded closure did not produce the expected oversize planner report.");
            string rejectedOutput = Path.Combine(scratch, "rejected-patch");
            ShadowBuildException rejection = null;
            try
            {
                ShadowPatchManifestBuilder.Build(new ShadowPatchBuildRequest {
                    baselineManifestPath = baselineManifestPath, currentCompileSnapshot = paddedSnapshot,
                    outputDirectory = rejectedOutput, patchId = RejectedPatchId, target = target, architecture = architecture,
                    sourcePins = pins, policy = policy, explicitChangedRoots = M07Build.Candidates, dllOnly = true, includePdb = true,
                });
            }
            catch (ShadowBuildException error)
            {
                rejection = error;
            }
            Require(rejection != null && rejection.Code == "MetadataCapacityExceeded",
                "Padded R01 patch was not rejected by the production capacity gate: " + (rejection == null ? "<no error>" : rejection.Code));
            Require(!Directory.Exists(rejectedOutput) && !File.Exists(rejectedOutput),
                "Over-budget R01 patch created a publication directory: " + rejectedOutput);

            SnapshotFile paddedFile = AssemblySnapshot.AllFiles(paddedReceipt).Single(file =>
                AssemblyIdentityUtil.CanonicalName(file.name) == AssemblyIdentityUtil.CanonicalName(paddedAssembly));
            string validationReceipt = Path.GetFullPath(receiptPath);
            Directory.CreateDirectory(Path.GetDirectoryName(validationReceipt));
            var evidence = new R01ValidationReceipt {
                schemaVersion = 1, milestone = "M07R-R01", result = "Passed",
                baselineManifestPath = Path.GetFullPath(baselineManifestPath), baselineManifestSha256 = ShadowHash.File(baselineManifestPath),
                baselineInputSnapshotHash = baseline.playerInputSnapshotHash, baselineBuildId = baseline.baselineBuildId,
                profile = profile, positiveCompileSnapshot = positiveSnapshot, positiveCompileSnapshotHash = positiveReceipt.snapshotHash,
                positivePatchManifest = Path.Combine(scratch, "positive-patch", "patch-manifest.json"),
                positivePatchManifestSha256 = ShadowHash.File(Path.Combine(scratch, "positive-patch", "patch-manifest.json")),
                positiveLoadOrder = positive.loadOrder, positiveInputs = positiveReport.inputs, positiveReport = positiveReport,
                paddedCompileSnapshot = paddedSnapshot, paddedCompileSnapshotHash = paddedReceipt.snapshotHash,
                paddedAssembly = paddedAssembly, paddedAssemblyBytes = (ulong)new FileInfo(ShadowHash.SafeChild(paddedSnapshot, paddedFile.path)).Length,
                paddedAssemblySha256 = paddedFile.sha256, rejectedInputs = rejectedInputs, rejectedReport = rejectedReport,
                rejectedOutput = rejectedOutput, rejectedOutputAbsent = !Directory.Exists(rejectedOutput) && !File.Exists(rejectedOutput),
                rejectionCode = rejection.Code, rejectionMessage = rejection.Message,
            };
            M04AssemblyIdentityProof.WriteNewJson(validationReceipt, evidence);
            return validationReceipt;
        }

        private static MetadataCapacityReport VerifyPositivePatch(ShadowPatchManifest patch, string snapshotRoot,
            AssemblySnapshotReceipt receipt, MetadataEncodingProfile profile, ShadowBaselineManifest baseline)
        {
            Require(patch != null && patch.metadataEncodingProfile != null && patch.metadataCapacityReport != null, "R01 positive patch lacks capacity evidence.");
            patch.metadataEncodingProfile.ValidateOrThrow();
            Require(patch.metadataEncodingProfile.profileVersion == profile.profileVersion &&
                string.Equals(patch.metadataEncodingProfile.nativeSourceRevision, profile.nativeSourceRevision, StringComparison.OrdinalIgnoreCase) &&
                string.Equals(patch.metadataEncodingProfile.nativeHelperSha256, profile.nativeHelperSha256, StringComparison.OrdinalIgnoreCase),
                "R01 positive patch profile differs from baseline.");
            Require(patch.loadOrder != null && patch.loadOrder.Length == M07Build.Candidates.Length &&
                patch.closure != null && patch.closure.Length == patch.loadOrder.Length, "R01 positive patch does not contain the real five-assembly closure.");
            MetadataCapacityReport report = patch.metadataCapacityReport;
            Require(report.fits && report.requiredImages == patch.loadOrder.Length && report.runtimeReserveMetadataBudget,
                "R01 positive patch capacity report is not a fitting mandatory reservation.");
            Require(report.cursorsBefore.SequenceEqual(baseline.metadataCapacityReport.cursorsAfter), "R01 positive patch did not begin after ordinary consumption.");
            MetadataCapacityInput[] expected = MetadataCapacityPlanner.ClosureInputs(snapshotRoot, receipt, patch.loadOrder);
            Require(report.inputs.Length == expected.Length && report.allocations.Length == expected.Length, "R01 positive report input/allocation count differs from closure.");
            var closureByName = patch.closure.ToDictionary(item => AssemblyIdentityUtil.CanonicalName(item.name), StringComparer.OrdinalIgnoreCase);
            for (int index = 0; index < expected.Length; ++index)
            {
                Require(report.inputs[index].name == expected[index].name && report.inputs[index].bytes == expected[index].bytes &&
                    report.inputs[index].sha256 == expected[index].sha256, "R01 positive report input differs at index " + index + ".");
                Require(report.allocations[index].name == expected[index].name && report.allocations[index].bytes == expected[index].bytes &&
                    report.allocations[index].sha256 == expected[index].sha256, "R01 positive allocation order differs at index " + index + ".");
                ShadowPatchAssembly closureEntry;
                Require(closureByName.TryGetValue(AssemblyIdentityUtil.CanonicalName(patch.loadOrder[index]), out closureEntry) &&
                    closureEntry.dllSize == expected[index].dllSize && closureEntry.sha256 == expected[index].sha256,
                    "R01 positive closure size/hash differs at index " + index + ".");
            }
            return report;
        }

        private static string CapturePaddedSnapshot(string scratch, string sourceSnapshot, AssemblySnapshotReceipt sourceReceipt,
            string assemblyName, BuildTarget target, string architecture, ShadowSourcePins pins, ShadowPolicyConfiguration policy)
        {
            string inputRoot = Path.Combine(scratch, "padded-inputs");
            foreach (SnapshotFile file in AssemblySnapshot.AllFiles(sourceReceipt))
            {
                string source = ShadowHash.SafeChild(sourceSnapshot, file.path);
                string destination = ShadowHash.SafeChild(inputRoot, file.path);
                CopyFile(source, destination);
                if (!string.IsNullOrEmpty(file.pdbPath))
                    CopyFile(ShadowHash.SafeChild(sourceSnapshot, file.pdbPath), ShadowHash.SafeChild(inputRoot, file.pdbPath));
            }
            SnapshotFile selected = AssemblySnapshot.AllFiles(sourceReceipt).Single(file =>
                AssemblyIdentityUtil.CanonicalName(file.name) == AssemblyIdentityUtil.CanonicalName(assemblyName));
            string selectedPath = ShadowHash.SafeChild(inputRoot, selected.path);
            long originalLength = new FileInfo(selectedPath).Length;
            long targetLength = Math.Max((long)OversizeBoundary, originalLength);
            if (targetLength == originalLength) targetLength++;
            using (var stream = new FileStream(selectedPath, FileMode.Open, FileAccess.Write, FileShare.None))
                stream.SetLength(targetLength);

            string output = Path.Combine(scratch, "padded-snapshot");
            AssemblySnapshotReceipt captured = AssemblySnapshot.Capture(output,
                sourceReceipt.assemblies.Select(file => ShadowHash.SafeChild(inputRoot, file.path)),
                sourceReceipt.references.Select(file => ShadowHash.SafeChild(inputRoot, file.path)),
                sourceReceipt.kind, target, architecture, pins, sourceReceipt.extraScriptingDefines,
                sourceReceipt.filteredAssemblies.Select(file => ShadowHash.SafeChild(inputRoot, file.path)), true);
            CaptureCompilerModeEvidence(output, captured);
            AssemblySnapshotReceipt verified = AssemblySnapshot.ReadAndVerify(output, false);
            ShadowReflectionBindingEvidence.RequirePolicy(policy, output, verified, false);
            Require(verified.kind == sourceReceipt.kind && verified.target == sourceReceipt.target && verified.architecture == sourceReceipt.architecture &&
                verified.extraScriptingDefines.SequenceEqual(sourceReceipt.extraScriptingDefines), "Padded snapshot changed compiler identity.");
            return output;
        }

        private static void RequireSemanticParity(string originalRoot, string paddedRoot, AssemblySnapshotReceipt receipt)
        {
            foreach (SnapshotFile file in receipt.assemblies)
            {
                string original = ShadowHash.SafeChild(originalRoot, file.path);
                string padded = ShadowHash.SafeChild(paddedRoot, file.path);
                using (ModuleDefMD originalModule = ModuleDefMD.Load(original))
                using (ModuleDefMD paddedModule = ModuleDefMD.Load(padded))
                    Require(AssemblySemanticHasher.Compute(originalModule).semanticHash == AssemblySemanticHasher.Compute(paddedModule).semanticHash,
                        "Padded snapshot changed managed semantics: " + file.name);
            }
        }

        private static void CaptureCompilerModeEvidence(string root, AssemblySnapshotReceipt receipt)
        {
            Type evidenceType = typeof(AssemblySnapshot).Assembly.GetType("HybridCLR.Editor.AssemblyShadow.ShadowCompilerModeEvidence", true);
            MethodInfo capture = evidenceType.GetMethod("Capture", BindingFlags.Static | BindingFlags.NonPublic);
            Require(capture != null, "Production compiler-mode evidence API is unavailable.");
            try
            {
                capture.Invoke(null, new object[] { root, receipt, ScriptCompilationOptions.DevelopmentBuild, true });
            }
            catch (TargetInvocationException error)
            {
                throw error.InnerException ?? error;
            }
        }

        private static string ResolveBaselineManifest(string argument)
        {
            string candidate = Path.GetFullPath(argument);
            if (File.Exists(candidate)) return candidate;
            string manifest = Path.Combine(candidate, "baseline-manifest.json");
            Require(File.Exists(manifest), "R01 baseline manifest is missing: " + argument);
            return manifest;
        }

        private static void CopyFile(string source, string destination)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(destination));
            File.Copy(source, destination, false);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }

        [Serializable]
        private sealed class R01ValidationReceipt
        {
            public int schemaVersion;
            public string milestone;
            public string result;
            public string baselineManifestPath;
            public string baselineManifestSha256;
            public string baselineInputSnapshotHash;
            public string baselineBuildId;
            public MetadataEncodingProfile profile;
            public string positiveCompileSnapshot;
            public string positiveCompileSnapshotHash;
            public string positivePatchManifest;
            public string positivePatchManifestSha256;
            public string[] positiveLoadOrder;
            public MetadataCapacityInput[] positiveInputs;
            public MetadataCapacityReport positiveReport;
            public string paddedCompileSnapshot;
            public string paddedCompileSnapshotHash;
            public string paddedAssembly;
            public ulong paddedAssemblyBytes;
            public string paddedAssemblySha256;
            public MetadataCapacityInput[] rejectedInputs;
            public MetadataCapacityReport rejectedReport;
            public string rejectedOutput;
            public bool rejectedOutputAbsent;
            public string rejectionCode;
            public string rejectionMessage;
        }
    }
}
