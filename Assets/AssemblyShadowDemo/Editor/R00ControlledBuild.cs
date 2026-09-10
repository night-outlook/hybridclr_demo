using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>
    /// Runs the existing M07 Player build with the controlled R00 performance
    /// configuration and immutable native-input provenance.
    /// </summary>
    public static class R00ControlledBuild
    {
        private const string EvidenceArgument = "-shadowR00BuildEvidence";
        private const string FeatureArgument = "-shadowR00Feature";
        private const string OutputArgument = "-shadowBuildOutput";
        private const string NativeOnArguments = "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1\"";
        private const string NativeOffArguments = "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0\"";
        private static readonly string[] MeasurementSourcePaths = {
            "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs",
            "Assets/AssemblyShadowDemo/Bootstrap/R00ProcessMemory.cs",
            "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/R00PerformanceWitness.cs",
        };

        private static bool active;
        private static bool preprocessorApplied;
        private static bool selectedFeatureEnabled;
        private static bool provenanceCaptureAttempted;
        private static bool provenanceSealed;
        private static H1BuildInputProvenance.Capture nativeProvenance;
        private static string provenanceProjectRoot;
        private static string provenanceSourcePinFile;
        private static string requestedFinalOutput;
        private static EffectiveConfiguration effective;

        /// <summary>Builds the selected NativeOn or NativeOff M07 Player.</summary>
        public static void BuildPlayer()
        {
            bool featureEnabled = ParseFeature(AssemblyShadowBuildCommands.Argument(FeatureArgument, ""));
            string evidenceArgument = AssemblyShadowBuildCommands.Argument(EvidenceArgument, "");
            Require(!string.IsNullOrWhiteSpace(evidenceArgument), EvidenceArgument + " requires a new JSON path.");
            string evidencePath = Path.GetFullPath(evidenceArgument);
            Require(!File.Exists(evidencePath) && !Directory.Exists(evidencePath),
                "R00 controlled-build evidence must be new: " + evidencePath);
            string evidenceDirectory = Path.GetDirectoryName(evidencePath);
            Require(!string.IsNullOrEmpty(evidenceDirectory) && Directory.Exists(evidenceDirectory),
                "R00 controlled-build evidence parent must already exist: " + evidenceDirectory);

            PreviousSettings previous = CaptureSettings();
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string sourcePinFile = AssemblyShadowSettings.Instance.sourcePinFile;
            string sourcePinsPath = Path.GetFullPath(AssemblyShadowSettings.Instance.sourcePinFile);
            string sourcePinsHash = ShadowHash.File(sourcePinsPath);
            ShadowSourcePins sourcePins = ShadowSourcePins.Read(
                sourcePinsPath, EditorUserBuildSettings.activeBuildTarget,
                AssemblyShadowSettings.Instance.architecture);
            string requestedOutput = AssemblyShadowBuildCommands.Argument(OutputArgument, "");
            BuildSourceEvidence[] measurementSources = CaptureMeasurementSources(projectRoot, evidencePath,
                out string measurementSourceSnapshotRoot);
            var evidence = new BuildEvidence {
                schemaVersion = 1,
                kind = "R00ControlledBuildEvidence",
                result = "Failed",
                feature = featureEnabled ? "on" : "off",
                selectedBuildMethod = featureEnabled ? nameof(M07Build.BuildPlayerBaseline) : nameof(M07Build.BuildFeatureDisabledPlayer),
                requestedBuildOutput = string.IsNullOrWhiteSpace(requestedOutput) ? "" : Path.GetFullPath(requestedOutput),
                passedThroughArguments = new[] {
                    "-shadowBaselineId=" + AssemblyShadowBuildCommands.Argument("-shadowBaselineId", ""),
                    "-shadowBuildOutput=" + requestedOutput,
                },
                evidencePath = evidencePath,
                provenanceComplete = false,
                provenanceStatus = "PendingFinalPlayerProvenanceCapture",
                acceptanceBlocked = true,
                fullSourceFreezeRequired = true,
                provenanceMissing = new[] {
                    "Separate full source and executable freeze remains a coordinator build-map gate."
                },
                sourcePinsPath = sourcePinsPath,
                sourcePinsSha256Before = sourcePinsHash,
                measurementSourceSnapshotRoot = measurementSourceSnapshotRoot,
                measurementSources = measurementSources,
                requestedConfiguration = RequestedConfiguration(featureEnabled),
                assertionConditions = new[] {
                    "Development=true",
                    "ScriptingBackend=IL2CPP",
                    "Il2CppCompilerConfiguration=Release",
                    "ManagedStrippingLevel=Low",
                    "Il2CppCodeGeneration=OptimizeSpeed",
                    "AllowDebugging=false",
                    "ConnectProfiler=false",
                    "DeepProfiling=false",
                    "BuildScriptsOnly=false",
                    "Native feature mode is selected by the existing M07 build path."
                }
            };

            HashSet<string> receiptsBefore = ExistingM07Receipts();
            Exception buildError = null;
            Exception restoreError = null;
            Exception pinError = null;
            Exception measurementSourceError = null;
            Exception writeError = null;
            active = true;
            selectedFeatureEnabled = featureEnabled;
            provenanceCaptureAttempted = false;
            provenanceSealed = false;
            nativeProvenance = null;
            provenanceProjectRoot = projectRoot;
            provenanceSourcePinFile = sourcePinFile;
            requestedFinalOutput = requestedOutput;
            preprocessorApplied = false;
            effective = null;
            bool buildSucceeded = false;
            try
            {
                // M07Build.Configure() also configures these settings.  The
                // pre-build callback below reapplies them after that call and
                // immediately before BuildPipeline starts the actual build.
                ApplyControlledConfiguration();
                if (featureEnabled) M07Build.BuildPlayerBaseline();
                else M07Build.BuildFeatureDisabledPlayer();

                evidence.nativeProvenance = nativeProvenance;
                Require(provenanceCaptureAttempted && nativeProvenance != null,
                    "Controlled build did not capture final Player native provenance exactly once.");
                H1BuildInputProvenance.RequireUnchanged(nativeProvenance);
                RequireMeasurementSourcesUnchanged(measurementSources);
                provenanceSealed = true;
                evidence.provenanceStatus = "CapturedAfterGenerateAndSealed;FullSourceFreezeRequired";
                Require(preprocessorApplied, "Controlled build preprocessor did not apply the required configuration.");
                evidence.effectiveConfiguration = effective;
                M07Build.M07PlayerBuildReceipt receipt = FindReceipt(
                    featureEnabled, requestedOutput, receiptsBefore);
                BindActualReceipt(evidence, receipt, sourcePins, sourcePinsPath, sourcePinsHash, featureEnabled);
                buildSucceeded = true;
            }
            catch (Exception error)
            {
                buildError = error;
                evidence.error = error.ToString();
            }
            finally
            {
                active = false;
                try
                {
                    RestoreSettings(previous);
                }
                catch (Exception error)
                {
                    restoreError = error;
                    evidence.error = string.IsNullOrEmpty(evidence.error)
                        ? "Restore failed: " + error
                        : evidence.error + "\nRestore failed: " + error;
                }

                try
                {
                    evidence.nativeProvenance = nativeProvenance;
                    evidence.sourcePinsSha256After = ShadowHash.File(sourcePinsPath);
                    evidence.sourcePinsUnchanged = evidence.sourcePinsSha256After == sourcePinsHash;
                    if (!evidence.sourcePinsUnchanged)
                    {
                        pinError = new BuildFailedException("Source pins changed during the controlled build.");
                        evidence.error = string.IsNullOrEmpty(evidence.error)
                            ? pinError.Message
                            : evidence.error + "\n" + pinError.Message;
                    }
                }
                catch (Exception error)
                {
                    pinError = error;
                    evidence.error = string.IsNullOrEmpty(evidence.error)
                        ? "Source pin integrity check failed: " + error
                        : evidence.error + "\nSource pin integrity check failed: " + error;
                }

                try
                {
                    RequireMeasurementSourcesUnchanged(measurementSources);
                    evidence.measurementSourcesUnchanged = true;
                }
                catch (Exception error)
                {
                    measurementSourceError = error;
                    evidence.measurementSourcesUnchanged = false;
                    evidence.error = string.IsNullOrEmpty(evidence.error)
                        ? "Measurement source integrity check failed: " + error
                        : evidence.error + "\nMeasurement source integrity check failed: " + error;
                }

                evidence.provenanceComplete = provenanceSealed && evidence.sourcePinsUnchanged &&
                    evidence.measurementSourcesUnchanged;
                if (!evidence.provenanceComplete && provenanceCaptureAttempted)
                    evidence.provenanceStatus = "ProvenanceIntegrityFailed;FullSourceFreezeRequired";
                evidence.result = buildSucceeded && restoreError == null && pinError == null &&
                    measurementSourceError == null && evidence.sourcePinsUnchanged &&
                    evidence.measurementSourcesUnchanged ? "Passed" : "Failed";
                try { WriteNewEvidence(evidencePath, evidence); }
                catch (Exception error) { writeError = error; }
            }

            if (buildError != null) throw buildError;
            if (restoreError != null) throw restoreError;
            if (pinError != null) throw pinError;
            if (measurementSourceError != null) throw measurementSourceError;
            if (writeError != null) throw writeError;
        }

        /// <summary>Reapplies the controlled settings immediately before Player compilation.</summary>
        public sealed class ControlledBuildPreprocessor : IPreprocessBuildWithReport
        {
            public int callbackOrder { get { return -100000; } }

            public void OnPreprocessBuild(BuildReport report)
            {
                if (!active) return;
                if (!IsFinalPlayerBuild(report)) return;
                ApplyControlledConfiguration();
                string expectedNative = selectedFeatureEnabled
                    ? NativeOnArguments : NativeOffArguments;
                Require(PlayerSettings.GetAdditionalIl2CppArgs() == expectedNative,
                    "Existing M07 build selected unexpected native feature arguments.");
                Require(!provenanceCaptureAttempted,
                    "Controlled build final Player provenance capture occurred more than once.");
                provenanceCaptureAttempted = true;
                nativeProvenance = H1BuildInputProvenance.CaptureAfterGenerate(
                    provenanceProjectRoot, provenanceSourcePinFile, selectedFeatureEnabled);
                Require(nativeProvenance != null,
                    "Controlled build final Player provenance capture returned no capture.");
                preprocessorApplied = true;
                effective = ReadEffectiveConfiguration(report);
                Require(effective.development && effective.developmentOption,
                    "Controlled build is not an actual Development Player.");
                Require(effective.scriptingBackend == ScriptingImplementation.IL2CPP.ToString() &&
                    effective.il2CppCompilerConfiguration == Il2CppCompilerConfiguration.Release.ToString() &&
                    effective.managedStrippingLevel == ManagedStrippingLevel.Low.ToString() &&
                    effective.il2CppCodeGeneration == Il2CppCodeGeneration.OptimizeSpeed.ToString() &&
                    !effective.allowDebugging && !effective.connectProfiler && !effective.deepProfiling,
                    "Controlled build effective settings differ from the requested performance configuration.");
            }
        }

        private static bool IsFinalPlayerBuild(BuildReport report)
        {
            if ((report.summary.options & BuildOptions.BuildScriptsOnly) != 0) return false;
            string output = report.summary.outputPath;
            if (string.IsNullOrWhiteSpace(output)) return false;
            string fullOutput = Path.GetFullPath(output);
            if (!string.IsNullOrWhiteSpace(requestedFinalOutput))
                return string.Equals(fullOutput, Path.GetFullPath(requestedFinalOutput), StringComparison.Ordinal);
            string m07Root = Path.GetFullPath(Path.Combine("Builds", "AssemblyShadow", "M07")) + Path.DirectorySeparatorChar;
            return fullOutput.StartsWith(m07Root, StringComparison.Ordinal) &&
                (fullOutput.EndsWith(".app", StringComparison.OrdinalIgnoreCase) ||
                 fullOutput.EndsWith(".exe", StringComparison.OrdinalIgnoreCase));
        }

        private static EffectiveConfiguration RequestedConfiguration(bool featureEnabled)
        {
            return new EffectiveConfiguration {
                development = true,
                developmentOption = true,
                scriptingBackend = ScriptingImplementation.IL2CPP.ToString(),
                il2CppCompilerConfiguration = Il2CppCompilerConfiguration.Release.ToString(),
                managedStrippingLevel = ManagedStrippingLevel.Low.ToString(),
                il2CppCodeGeneration = Il2CppCodeGeneration.OptimizeSpeed.ToString(),
                allowDebugging = false,
                connectProfiler = false,
                deepProfiling = false,
                buildScriptsOnly = false,
                nativeArguments = featureEnabled ? NativeOnArguments : NativeOffArguments,
                buildOptions = BuildOptions.Development.ToString(),
            };
        }

        private static EffectiveConfiguration ReadEffectiveConfiguration(BuildReport report)
        {
            return new EffectiveConfiguration {
                development = EditorUserBuildSettings.development,
                developmentOption = (report.summary.options & BuildOptions.Development) != 0,
                scriptingBackend = PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone).ToString(),
                il2CppCompilerConfiguration = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone).ToString(),
                managedStrippingLevel = PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.Standalone).ToString(),
                il2CppCodeGeneration = PlayerSettings.GetIl2CppCodeGeneration(NamedBuildTarget.Standalone).ToString(),
                allowDebugging = EditorUserBuildSettings.allowDebugging,
                connectProfiler = EditorUserBuildSettings.connectProfiler,
                deepProfiling = EditorUserBuildSettings.buildWithDeepProfilingSupport,
                buildScriptsOnly = EditorUserBuildSettings.buildScriptsOnly,
                nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs(),
                buildOptions = report.summary.options.ToString(),
            };
        }

        private static void ApplyControlledConfiguration()
        {
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.IL2CPP);
            PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, Il2CppCompilerConfiguration.Release);
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone, ManagedStrippingLevel.Low);
            PlayerSettings.SetIl2CppCodeGeneration(NamedBuildTarget.Standalone, Il2CppCodeGeneration.OptimizeSpeed);
            EditorUserBuildSettings.development = true;
            EditorUserBuildSettings.allowDebugging = false;
            EditorUserBuildSettings.connectProfiler = false;
            EditorUserBuildSettings.buildWithDeepProfilingSupport = false;
            EditorUserBuildSettings.buildScriptsOnly = false;
        }

        private static PreviousSettings CaptureSettings()
        {
            return new PreviousSettings {
                assemblyShadowSettingsJson = JsonUtility.ToJson(AssemblyShadowSettings.Instance),
                hybridClrSettingsJson = JsonUtility.ToJson(HybridCLRSettings.Instance),
                scenes = EditorBuildSettings.scenes,
                scriptingBackend = PlayerSettings.GetScriptingBackend(NamedBuildTarget.Standalone),
                il2CppCompilerConfiguration = PlayerSettings.GetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone),
                managedStrippingLevel = PlayerSettings.GetManagedStrippingLevel(NamedBuildTarget.Standalone),
                il2CppCodeGeneration = PlayerSettings.GetIl2CppCodeGeneration(NamedBuildTarget.Standalone),
                apiCompatibilityLevel = PlayerSettings.GetApiCompatibilityLevel(NamedBuildTarget.Standalone),
                architecture = PlayerSettings.GetArchitecture(NamedBuildTarget.Standalone),
                companyName = PlayerSettings.companyName,
                productName = PlayerSettings.productName,
                runInBackground = PlayerSettings.runInBackground,
                development = EditorUserBuildSettings.development,
                allowDebugging = EditorUserBuildSettings.allowDebugging,
                connectProfiler = EditorUserBuildSettings.connectProfiler,
                deepProfiling = EditorUserBuildSettings.buildWithDeepProfilingSupport,
                buildScriptsOnly = EditorUserBuildSettings.buildScriptsOnly,
                nativeArguments = PlayerSettings.GetAdditionalIl2CppArgs(),
#if UNITY_EDITOR_OSX
                osxArchitecture = UnityEditor.OSXStandalone.UserBuildSettings.architecture,
#endif
            };
        }

        private static void RestoreSettings(PreviousSettings previous)
        {
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, previous.scriptingBackend);
            PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, previous.il2CppCompilerConfiguration);
            PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Standalone, previous.managedStrippingLevel);
            PlayerSettings.SetIl2CppCodeGeneration(NamedBuildTarget.Standalone, previous.il2CppCodeGeneration);
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Standalone, previous.apiCompatibilityLevel);
            PlayerSettings.SetArchitecture(NamedBuildTarget.Standalone, previous.architecture);
#if UNITY_EDITOR_OSX
            UnityEditor.OSXStandalone.UserBuildSettings.architecture = previous.osxArchitecture;
#endif
            PlayerSettings.companyName = previous.companyName;
            PlayerSettings.productName = previous.productName;
            PlayerSettings.runInBackground = previous.runInBackground;
            EditorUserBuildSettings.development = previous.development;
            EditorUserBuildSettings.allowDebugging = previous.allowDebugging;
            EditorUserBuildSettings.connectProfiler = previous.connectProfiler;
            EditorUserBuildSettings.buildWithDeepProfilingSupport = previous.deepProfiling;
            EditorUserBuildSettings.buildScriptsOnly = previous.buildScriptsOnly;
            PlayerSettings.SetAdditionalIl2CppArgs(previous.nativeArguments);
            EditorBuildSettings.scenes = previous.scenes;
            JsonUtility.FromJsonOverwrite(previous.assemblyShadowSettingsJson, AssemblyShadowSettings.Instance);
            AssemblyShadowSettings.Save();
            JsonUtility.FromJsonOverwrite(previous.hybridClrSettingsJson, HybridCLRSettings.Instance);
            HybridCLRSettings.Save();
            AssetDatabase.SaveAssets();
        }

        private static HashSet<string> ExistingM07Receipts()
        {
            string root = Path.GetFullPath("_temp/AssemblyShadow");
            if (!Directory.Exists(root)) return new HashSet<string>(StringComparer.Ordinal);
            return new HashSet<string>(Directory.GetDirectories(root, "M07PlayerInputs-*", SearchOption.TopDirectoryOnly)
                .Select(path => Path.Combine(path, "m07-player-build.json")), StringComparer.Ordinal);
        }

        private static M07Build.M07PlayerBuildReceipt FindReceipt(bool featureEnabled, string requestedOutput,
            HashSet<string> receiptsBefore)
        {
            string root = Path.GetFullPath("_temp/AssemblyShadow");
            Require(Directory.Exists(root), "M07 build input root is missing after the build.");
            string expectedVariant = featureEnabled ? "NativeOn" : "NativeOff";
            var matches = new List<Tuple<string, M07Build.M07PlayerBuildReceipt>>();
            foreach (string directory in Directory.GetDirectories(root, "M07PlayerInputs-*", SearchOption.TopDirectoryOnly))
            {
                string path = Path.Combine(directory, "m07-player-build.json");
                if (receiptsBefore.Contains(path) || !File.Exists(path)) continue;
                M07Build.M07PlayerBuildReceipt receipt = JsonUtility.FromJson<M07Build.M07PlayerBuildReceipt>(File.ReadAllText(path));
                if (receipt == null || receipt.variant != expectedVariant) continue;
                if (!string.IsNullOrWhiteSpace(requestedOutput) &&
                    Path.GetFullPath(receipt.playerOutput) != Path.GetFullPath(requestedOutput)) continue;
                matches.Add(Tuple.Create(path, receipt));
            }
            Require(matches.Count == 1, "Expected exactly one new M07 Player receipt for the controlled build; found " + matches.Count + ".");
            return matches[0].Item2;
        }

        private static void BindActualReceipt(BuildEvidence evidence, M07Build.M07PlayerBuildReceipt receipt,
            ShadowSourcePins expectedPins, string sourcePinsPath, string sourcePinsHash, bool featureEnabled)
        {
            Require(receipt.schemaVersion == 1 && receipt.variant == (featureEnabled ? "NativeOn" : "NativeOff"),
                "Actual M07 Player receipt header differs from the selected feature mode.");
            Require(Directory.Exists(receipt.inputSnapshot),
                "Actual M07 input snapshot directory is missing.");
            AssemblySnapshotReceipt snapshot = AssemblySnapshot.ReadAndVerify(receipt.inputSnapshot, true);
            Require(snapshot.snapshotHash == receipt.inputSnapshotHash,
                "Actual M07 input snapshot hash differs from its Player receipt.");
            Require(snapshot.sourcePins != null, "Actual M07 input snapshot has no source pin record.");
            ShadowSourcePins.RequireSameBuildSources(expectedPins, snapshot.sourcePins);
            Require(receipt.runtimeAbiHash == snapshot.sourcePins.RuntimeAbiHash(),
                "Actual M07 receipt ABI hash differs from its input snapshot.");
            string expectedNative = featureEnabled ? NativeOnArguments : NativeOffArguments;
            Require(receipt.nativeArguments == expectedNative,
                "Actual M07 receipt native arguments differ from the selected feature mode.");
            Require(File.Exists(receipt.nativeLibraryPath) && receipt.nativeLibrarySha256 == ShadowHash.File(receipt.nativeLibraryPath),
                "Actual M07 native library is missing or stale.");
            Require(File.Exists(receipt.nativeMetadataPath) && receipt.nativeMetadataSha256 == ShadowHash.File(receipt.nativeMetadataPath),
                "Actual M07 native metadata is missing or stale.");
            string executable = PlayerExecutable(receipt.playerOutput);
            evidence.actualReceiptPath = FindReceiptPath(receipt);
            evidence.actualReceiptSha256 = ShadowHash.File(evidence.actualReceiptPath);
            evidence.actualReceiptVariant = receipt.variant;
            evidence.buildGuid = receipt.buildGuid;
            evidence.baselineBuildId = receipt.baselineBuildId;
            evidence.runtimeAbiHash = receipt.runtimeAbiHash;
            evidence.playerOutput = Path.GetFullPath(receipt.playerOutput);
            evidence.playerExecutable = executable;
            evidence.playerExecutableSha256 = ShadowHash.File(executable);
            evidence.nativeLibraryPath = Path.GetFullPath(receipt.nativeLibraryPath);
            evidence.nativeLibrarySha256 = receipt.nativeLibrarySha256;
            evidence.nativeMetadataPath = Path.GetFullPath(receipt.nativeMetadataPath);
            evidence.nativeMetadataSha256 = receipt.nativeMetadataSha256;
            evidence.inputSnapshotPath = Path.GetFullPath(receipt.inputSnapshot);
            evidence.inputSnapshotSha256 = snapshot.snapshotHash;
            evidence.measurementSourcesBuildGuid = receipt.buildGuid;
            Require(nativeProvenance != null && nativeProvenance.sourcePinSha256 == sourcePinsHash,
                "Controlled build immutable source pin differs from the selected source.");
            evidence.sourcePinsPath = nativeProvenance.sourcePinFile;
            evidence.sourcePinsSha256Before = sourcePinsHash;
            evidence.nativeArguments = receipt.nativeArguments;
        }

        private static BuildSourceEvidence[] CaptureMeasurementSources(string projectRoot, string evidencePath,
            out string snapshotRoot)
        {
            string parent = Path.GetDirectoryName(evidencePath);
            string name = Path.GetFileNameWithoutExtension(evidencePath) + "-measurement-sources-" +
                Guid.NewGuid().ToString("N");
            snapshotRoot = Path.GetFullPath(Path.Combine(parent, name));
            Require(!File.Exists(snapshotRoot) && !Directory.Exists(snapshotRoot),
                "Measurement source snapshot root must be new: " + snapshotRoot);
            Directory.CreateDirectory(snapshotRoot);
            var result = new List<BuildSourceEvidence>();
            foreach (string relativePath in MeasurementSourcePaths)
            {
                string original = Path.GetFullPath(Path.Combine(projectRoot,
                    relativePath.Replace('/', Path.DirectorySeparatorChar)));
                Require(File.Exists(original) && !IsSymlink(original),
                    "Measurement source is missing or symlinked: " + original);
                string sha256 = ShadowHash.File(original);
                string snapshot = Path.GetFullPath(Path.Combine(snapshotRoot,
                    relativePath.Replace('/', Path.DirectorySeparatorChar)));
                Directory.CreateDirectory(Path.GetDirectoryName(snapshot));
                File.Copy(original, snapshot, false);
                Require(File.Exists(snapshot) && !IsSymlink(snapshot) && ShadowHash.File(snapshot) == sha256,
                    "Measurement source snapshot differs from the pre-build source: " + relativePath);
                result.Add(new BuildSourceEvidence {
                    relativePath = relativePath,
                    originalSourcePath = original,
                    snapshotPath = snapshot,
                    sha256 = sha256,
                });
            }
            return result.ToArray();
        }

        private static void RequireMeasurementSourcesUnchanged(BuildSourceEvidence[] expected)
        {
            Require(expected != null && expected.Length == MeasurementSourcePaths.Length,
                "Measurement source evidence is incomplete.");
            foreach (string relativePath in MeasurementSourcePaths)
            {
                BuildSourceEvidence item = expected.SingleOrDefault(row => row != null && row.relativePath == relativePath);
                Require(item != null && File.Exists(item.originalSourcePath) && !IsSymlink(item.originalSourcePath) &&
                        File.Exists(item.snapshotPath) && !IsSymlink(item.snapshotPath) &&
                        ShadowHash.File(item.originalSourcePath) == item.sha256 &&
                        ShadowHash.File(item.snapshotPath) == item.sha256,
                    "Measurement source changed after its pre-build snapshot: " + relativePath);
            }
        }

        private static bool IsSymlink(string path)
        {
            try { return (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0; }
            catch (FileNotFoundException) { return false; }
        }

        private static string FindReceiptPath(M07Build.M07PlayerBuildReceipt receipt)
        {
            string root = Path.GetFullPath("_temp/AssemblyShadow");
            var matches = Directory.GetDirectories(root, "M07PlayerInputs-*", SearchOption.TopDirectoryOnly)
                .Select(path => Path.Combine(path, "m07-player-build.json"))
                .Where(File.Exists)
                .Where(path => {
                    try {
                        M07Build.M07PlayerBuildReceipt item = JsonUtility.FromJson<M07Build.M07PlayerBuildReceipt>(File.ReadAllText(path));
                        return item != null && item.buildGuid == receipt.buildGuid;
                    }
                    catch { return false; }
                }).ToArray();
            Require(matches.Length == 1, "Actual M07 receipt GUID is not unique.");
            return matches[0];
        }

        private static string PlayerExecutable(string output)
        {
            string macos = Path.Combine(output, "Contents/MacOS");
            Require(Directory.Exists(macos), "Player executable directory is missing: " + macos);
            string[] files = Directory.GetFiles(macos, "*", SearchOption.TopDirectoryOnly)
                .Where(path => !path.EndsWith(".dSYM", StringComparison.OrdinalIgnoreCase)).ToArray();
            Require(files.Length == 1, "Controlled OSX Player must contain exactly one executable.");
            return Path.GetFullPath(files[0]);
        }

        private static void WriteNewEvidence(string path, BuildEvidence evidence)
        {
            byte[] bytes = System.Text.Encoding.UTF8.GetBytes(JsonUtility.ToJson(evidence, true));
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                stream.Write(bytes, 0, bytes.Length);
        }

        private static bool ParseFeature(string value)
        {
            if (string.Equals(value, "on", StringComparison.OrdinalIgnoreCase)) return true;
            if (string.Equals(value, "off", StringComparison.OrdinalIgnoreCase)) return false;
            throw new BuildFailedException(FeatureArgument + " must be on or off.");
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }

        [Serializable]
        private sealed class PreviousSettings
        {
            public string assemblyShadowSettingsJson, hybridClrSettingsJson, nativeArguments, companyName, productName;
            public EditorBuildSettingsScene[] scenes;
            public ScriptingImplementation scriptingBackend;
            public Il2CppCompilerConfiguration il2CppCompilerConfiguration;
            public ManagedStrippingLevel managedStrippingLevel;
            public Il2CppCodeGeneration il2CppCodeGeneration;
            public ApiCompatibilityLevel apiCompatibilityLevel;
            public int architecture;
            public bool runInBackground, development, allowDebugging, connectProfiler, deepProfiling, buildScriptsOnly;
#if UNITY_EDITOR_OSX
            public OSArchitecture osxArchitecture;
#endif
        }

        [Serializable]
        public sealed class EffectiveConfiguration
        {
            public bool development, developmentOption, allowDebugging, connectProfiler, deepProfiling, buildScriptsOnly;
            public string scriptingBackend, il2CppCompilerConfiguration, managedStrippingLevel, il2CppCodeGeneration;
            public string nativeArguments, buildOptions;
        }

        [Serializable]
        public sealed class BuildSourceEvidence
        {
            public string relativePath, originalSourcePath, snapshotPath, sha256;
        }

        [Serializable]
        public sealed class BuildEvidence
        {
            public int schemaVersion;
            public string kind, result, feature, selectedBuildMethod, requestedBuildOutput, evidencePath;
            public string[] passedThroughArguments;
            public bool provenanceComplete, acceptanceBlocked, sourcePinsUnchanged, measurementSourcesUnchanged;
            public bool fullSourceFreezeRequired;
            public string provenanceStatus, error;
            public string[] provenanceMissing, assertionConditions;
            public EffectiveConfiguration requestedConfiguration, effectiveConfiguration;
            public H1BuildInputProvenance.Capture nativeProvenance;
            public string actualReceiptPath, actualReceiptSha256, actualReceiptVariant;
            public string buildGuid, baselineBuildId, runtimeAbiHash;
            public string playerOutput, playerExecutable, playerExecutableSha256;
            public string nativeLibraryPath, nativeLibrarySha256, nativeMetadataPath, nativeMetadataSha256, nativeArguments;
            public string inputSnapshotPath, inputSnapshotSha256;
            public string sourcePinsPath, sourcePinsSha256Before, sourcePinsSha256After;
            public string measurementSourceSnapshotRoot, measurementSourcesBuildGuid;
            public BuildSourceEvidence[] measurementSources;
        }
    }
}
