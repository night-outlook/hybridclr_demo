using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class M06Build
    {
        public const string BootstrapScene = "Assets/AssemblyShadowDemo/Scenes/M06Bootstrap.unity";
        public const string BootstrapRunnerScript = "Assets/AssemblyShadowDemo/Bootstrap/M06BootstrapRunner.cs";
        public const string StableAotHashDomain = "m06-stable-aot:1\n";
        public const string PlayerReceiptName = "m06-player-build.json", FixtureManifestName = "m06-fixtures.json", PlaceholderName = "m06-placeholder-AssemblyManifest.cpp";
        public static readonly string[] ProviderFirstOrder = M03Build.ProviderFirstOrder.ToArray();
        public static void Configure() { ConfigureMode(RequestedDevelopment()); }
        public static void PrepareGenerationInputs() { M06GenerationBuild.PrepareGenerationInputs(); }
        public static void BuildPlayerBaseline() { BuildPlayer(true, true); }
        public static void BuildReleasePlayerBaseline() { BuildPlayer(true, false); }
        public static void BuildFeatureDisabledPlayer() { BuildPlayer(false, RequestedDevelopment()); }
        public static void ResumePlayerBaselineCapture() { ResumePlayer(true, true); }
        public static void ResumeReleasePlayerBaselineCapture() { ResumePlayer(true, false); }
        public static void ResumeFeatureDisabledPlayerCapture() { ResumePlayer(false, RequestedDevelopment()); }
        public static void ValidateFixtureWarmups()
        {
            bool development = RequestedDevelopment(); ConfigureMode(development);
            string generationPath = GenerationArgument(); var generation = M06GenerationBuild.ReadAndVerify(generationPath, false);
            M06GenerationBuild.RequireCurrentSelection(generation);
            Require(generation.developmentBuild == development, "Warmup preflight and selected generator compilation modes differ.");
            PreflightFixtureWarmups(generation, AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget));
            Debug.Log("[AssemblyShadow M06] Fixture warmup metadata preflight passed: " + generationPath);
        }

        internal static bool RequestedDevelopment()
        {
            string mode = AssemblyShadowBuildCommands.Argument("-shadowM06BuildMode", "Development");
            Require(mode == "Development" || mode == "Release", "-shadowM06BuildMode must be Development or Release."); return mode == "Development";
        }
        internal static void ConfigureMode(bool development)
        {
            string previous = AssemblyShadowSettings.Instance.buildId;
            string fallback = development ? "M06-Baseline-v1" : "M06-Baseline-Release-v1";
            if (!string.IsNullOrEmpty(previous) && previous.StartsWith("M06-Baseline-", StringComparison.Ordinal) &&
                previous.Contains("-Release-") == !development) fallback = previous;
            string id = AssemblyShadowBuildCommands.Argument("-shadowBaselineId", fallback); RequireSafeId(id);
            M02Build.Configure(); EditorUserBuildSettings.development = development;
            PlayerSettings.SetIl2CppCompilerConfiguration(NamedBuildTarget.Standalone, NativeConfiguration(development));
            var settings = AssemblyShadowSettings.Instance; settings.buildId = id;
            settings.playerInputSnapshot = ""; settings.baselineManifestPath = ""; settings.resourceBaselinePath = ""; AssemblyShadowSettings.Save();
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, EditorUserBuildSettings.activeBuildTarget, settings.architecture);
            EnsureScene(id, pins.RuntimeAbiHash());
            RequireBootstrapExecutionOrder();
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(BootstrapScene, true) };
            AssemblyShadowSettings.Save(); AssetDatabase.SaveAssets();
        }
        private static void RequireBootstrapExecutionOrder()
        {
            var script = AssetDatabase.LoadAssetAtPath<MonoScript>(BootstrapRunnerScript);
            Require(script != null && script.GetClass() != null && script.GetClass().FullName == "AssemblyShadowDemo.M06BootstrapRunner",
                "M06 bootstrap runner script is not imported at its pinned path.");
            Require(MonoImporter.GetExecutionOrder(script) == -32000,
                "M06 bootstrap runner must have effective MonoImporter execution order -32000.");
        }
        public static void ValidateCompilerInputs()
        {
            bool development = RequestedDevelopment(); ConfigureMode(development);
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string snapshot = CompileSnapshot(Path.Combine(NewRoot("M06CompilerPreflight-"), "Compile"), new string[0], development, policy, pins);
            var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false); TargetFrameworkReferenceVerifier.Verify(snapshot, receipt);
            M06GenerationBuild.CaptureExecutionPolicy(snapshot, receipt, policy);
            Debug.Log("[AssemblyShadow M06] Compiler/startup preflight, not Player acceptance: " + snapshot);
        }
        internal static string CompileSnapshot(string root, string[] defines, bool development, ShadowPolicyConfiguration policy, ShadowSourcePins pins)
        {
            return AssemblySnapshot.CompileWithOptions(root, EditorUserBuildSettings.activeBuildTarget, AssemblyShadowSettings.Instance.architecture, pins, policy, defines, development);
        }

        private static void BuildPlayer(bool nativeEnabled, bool development)
        {
            ConfigureMode(development);
            string generationPath = GenerationArgument(); var generation = M06GenerationBuild.ReadAndVerify(generationPath, true);
            Require(generation.developmentBuild == development, "Player and selected generator compilation modes differ.");
            string generationHash = ShadowHash.File(generationPath);
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            if (nativeEnabled) Require(!Directory.Exists(Path.Combine(settings.baselineOutputRoot, target.ToString(), settings.buildId)), "Select a fresh M06 baseline ID; baseline artifacts are immutable.");
            string output = AssemblyShadowBuildCommands.Argument("-shadowBuildOutput", "Builds/AssemblyShadow/M06/" + settings.buildId + (nativeEnabled ? "" : "-NativeOff") + ".app");
            if (target == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal)) output = output.Substring(0, output.Length - 4) + ".exe";
            output = Path.GetFullPath(output); Require(!Directory.Exists(output) && !File.Exists(output), "Player output already exists.");
            string frozen = M01Paths.BaselineRoot(target); BuildBaselineBundles.VerifyExisting(frozen);
            M01BuildSupport.StageBaselineArtifacts(frozen, Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01"));
            M02ReflectionBindingValidation.StageConfiguration();
            string snapshot;
            try
            {
                BaselineBuild.SetNativeFeature(nativeEnabled); AssetDatabase.SaveAssets();
                snapshot = CapturePlayer(output, nativeEnabled, development, generationPath, generation);
                Require(ShadowHash.File(generationPath) == generationHash, "Generation proof changed during Player build.");
                M06GenerationBuild.VerifyInstalledFiles(generation, true);
            }
            finally { BaselineBuild.SetNativeFeature(true); AssetDatabase.SaveAssets(); }
            if (nativeEnabled) FinalizeBaseline(snapshot, generation, generationPath, generationHash, development, policy);
            Debug.Log("[AssemblyShadow M06] Actual Player receipt: " + Path.Combine(snapshot, PlayerReceiptName));
        }

        private static void ResumePlayer(bool nativeEnabled, bool development)
        {
            ConfigureMode(development);
            string generationPath = GenerationArgument(), generationHash = ShadowHash.File(generationPath);
            var generation = M04JsonEvidence.Read<M06GenerationProof>(File.ReadAllText(generationPath));
            Require(generation.schemaVersion == 1 && generation.milestone == "M06" && generation.baselineBuildId == AssemblyShadowSettings.Instance.buildId &&
                generation.developmentBuild == development, "Interrupted Player and selected generation differ.");
            M06GenerationBuild.RequireCurrentSelection(generation); M06GenerationBuild.VerifyInstalledFiles(generation, true);

            string snapshotArgument = AssemblyShadowBuildCommands.Argument("-shadowPlayerSnapshot", "");
            string outputArgument = AssemblyShadowBuildCommands.Argument("-shadowBuildOutput", "");
            string logArgument = AssemblyShadowBuildCommands.Argument("-shadowM06InterruptedBuildLog", "");
            Require(!string.IsNullOrWhiteSpace(snapshotArgument) && Path.IsPathRooted(snapshotArgument), "Pass the exact absolute interrupted -shadowPlayerSnapshot.");
            Require(!string.IsNullOrWhiteSpace(outputArgument) && Path.IsPathRooted(outputArgument), "Pass the exact absolute interrupted -shadowBuildOutput.");
            Require(!string.IsNullOrWhiteSpace(logArgument) && Path.IsPathRooted(logArgument), "Pass the exact absolute -shadowM06InterruptedBuildLog.");
            string snapshot = Path.GetFullPath(snapshotArgument), output = Path.GetFullPath(outputArgument), logPath = Path.GetFullPath(logArgument);
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            Require(captured.buildId == generation.baselineBuildId && captured.playerOutput == output &&
                (((BuildOptions)captured.playerBuildOptions & BuildOptions.Development) != 0) == development,
                "Interrupted Player snapshot/output/mode differs.");
            string logHash = VerifyInterruptedBuildLog(logPath, captured, nativeEnabled, development);

            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            if (nativeEnabled) Require(!Directory.Exists(Path.Combine(settings.baselineOutputRoot, target.ToString(), settings.buildId)), "Interrupted baseline output already exists.");
            var baselineCompile = AssemblySnapshot.ReadAndVerify(generation.baselineCompileSnapshot, false);
            var startup = M06GenerationBuild.CaptureExecutionPolicy(generation.baselineCompileSnapshot, baselineCompile, policy);
            var selectedStartup = M04JsonEvidence.Read<M06ExecutionPolicyProof>(File.ReadAllText(generation.plans.Single(row => row.planId == "Ordinary").executionPolicyPath));
            M06GenerationBuild.RequireSameStartup(selectedStartup, startup);
            var placeholders = M04PlaceholderManifestProof.CaptureBeforeBuild();
            try
            {
                BaselineBuild.SetNativeFeature(nativeEnabled); AssetDatabase.SaveAssets();
                snapshot = FinalizePlayerCapture(snapshot, nativeEnabled, development, generationPath, generation, placeholders, selectedStartup, true);
                VerifyHash(generationPath, generationHash); VerifyHash(logPath, logHash); M06GenerationBuild.VerifyInstalledFiles(generation, true);
            }
            finally { BaselineBuild.SetNativeFeature(true); AssetDatabase.SaveAssets(); }
            if (nativeEnabled) FinalizeBaseline(snapshot, generation, generationPath, generationHash, development, policy);
            Debug.Log("[AssemblyShadow M06] Resumed actual Player receipt: " + Path.Combine(snapshot, PlayerReceiptName));
        }

        private static string VerifyInterruptedBuildLog(string path, AssemblySnapshotReceipt captured, bool nativeEnabled, bool development)
        {
            Require(File.Exists(path), "Interrupted Unity build log is missing.");
            byte[] bytes = File.ReadAllBytes(path); string hash = ShadowHash.Bytes(bytes);
            string text = new UTF8Encoding(false, true).GetString(bytes);
            string flag = "--compiler-flags=-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (nativeEnabled ? "1" : "0");
            string entrypoint = nativeEnabled ? (development ? "BuildPlayerBaseline" : "BuildReleasePlayerBaseline") : "BuildFeatureDisabledPlayer";
            Require(text.Contains("Build Finished, Result: Success.") && text.Contains(flag) &&
                text.Contains("AssemblyShadowDemo.Editor.M06Build:" + entrypoint) &&
                text.Contains("[AssemblyShadow] Sealed Player input snapshot " + captured.snapshotHash + " for native " + captured.nativeLibrarySha256),
                "Interrupted Unity log does not prove this exact successful Player/native configuration/snapshot.");
            return hash;
        }

        private static void FinalizeBaseline(string snapshot, M06GenerationProof generation, string generationPath, string generationHash,
            bool development, ShadowPolicyConfiguration policy)
        {
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            string frozen = M01Paths.BaselineRoot(target); BuildBaselineBundles.VerifyExisting(frozen);
            string resources = M02FrozenResources.Import(frozen, snapshot, Path.Combine("HybridCLRData/AssemblyShadow/ResourceBaselines", target.ToString(), settings.buildId), target, settings.architecture, policy);
            // Real resource ABI validation permits new nonserialized M06
            // execution types; M01 DLL semantic equality is not asserted.
            var baseline = ShadowBaselineManifestBuilder.Build(new ShadowBaselineBuildRequest {
                playerInputSnapshot = snapshot, resourceBaselinePath = resources, outputDirectory = Path.Combine(settings.baselineOutputRoot, target.ToString(), settings.buildId),
                buildId = settings.buildId, target = target, architecture = settings.architecture, sourcePins = generation.sourcePins, policy = policy,
                resources = JsonUtility.FromJson<ShadowResourceBuildMap>(File.ReadAllText(settings.resourceBuildMapPath)) });
            string baselinePath = Path.GetFullPath(Path.Combine(settings.baselineOutputRoot, target.ToString(), settings.buildId, "baseline-manifest.json"));
            // A generation-specific immutable selection never reads or
            // replaces the historical M05 UserSettings build session.
            M04AssemblyIdentityProof.WriteNewJson(Path.Combine(Path.GetDirectoryName(generationPath), "m06-baseline-selection.json"), new M06BaselineSelection {
                playerInputSnapshot = snapshot, baselineBuildId = baseline.baselineBuildId, resourceBaselinePath = resources,
                baselineManifestPath = baselinePath, baselineManifestSha256 = ShadowHash.File(baselinePath), playerBuildReceiptSha256 = ShadowHash.File(Path.Combine(snapshot, PlayerReceiptName)),
                generationProofPath = generationPath, generationProofSha256 = generationHash, developmentBuild = development });
        }
        private static string CapturePlayer(string output, bool nativeEnabled, bool development, string generationPath, M06GenerationProof generation)
        {
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string arguments = NativeArguments(nativeEnabled); Require(PlayerSettings.GetAdditionalIl2CppArgs() == arguments, "Native feature compiler arguments differ.");
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/M06PlayerInputs-" + Guid.NewGuid().ToString("N"));
            var baselineCompile = AssemblySnapshot.ReadAndVerify(generation.baselineCompileSnapshot, false);
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var startup = M06GenerationBuild.CaptureExecutionPolicy(generation.baselineCompileSnapshot, baselineCompile, policy);
            var selectedStartup = M04JsonEvidence.Read<M06ExecutionPolicyProof>(File.ReadAllText(generation.plans.Single(row => row.planId == "Ordinary").executionPolicyPath));
            M06GenerationBuild.RequireSameStartup(selectedStartup, startup);
            string[] defines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            var placeholders = M04PlaceholderManifestProof.CaptureBeforeBuild();
            BuildOptions options = PlayerOptions(development);
            bool oldScriptsOnly = EditorUserBuildSettings.buildScriptsOnly;
            bool oldExportProject = PlayerExportProject(target);
            bool captureStarted = false;
            try
            {
                // Strip-only generation intentionally exports a native project.
                // A prior interrupted Editor must not leak that persistent route
                // into the evidence Player, which requires a built native binary.
                EditorUserBuildSettings.buildScriptsOnly = false;
                SetPlayerExportProject(target, false);
                Require(!EditorUserBuildSettings.buildScriptsOnly && !PlayerExportProject(target), "M06 Player must be a built application, not a scripts-only/exported native project.");
                M06GenerationBuild.VerifyInstalledFiles(generation, true);
                ShadowPlayerInputCapture.Begin(snapshot, settings.buildId, target, settings.architecture, pins, M02Build.Candidates, defines, development);
                captureStarted = true;
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { BootstrapScene }, locationPathName = output,
                    target = target, targetGroup = BuildTargetGroup.Standalone, options = options, extraScriptingDefines = defines });
                ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
            }
            finally
            {
                if (captureStarted) ShadowPlayerInputCapture.End();
                SetPlayerExportProject(target, oldExportProject);
                EditorUserBuildSettings.buildScriptsOnly = oldScriptsOnly;
            }
            return FinalizePlayerCapture(snapshot, nativeEnabled, development, generationPath, generation, placeholders, selectedStartup, false);
        }

        private static string FinalizePlayerCapture(string snapshot, bool nativeEnabled, bool development, string generationPath,
            M06GenerationProof generation, M04PlaceholderManifestProof.CapturedManifest placeholders,
            M06ExecutionPolicyProof selectedStartup, bool replayExistingProofs)
        {
            M06GenerationBuild.VerifyInstalledFiles(generation, true);
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string arguments = NativeArguments(nativeEnabled); Require(PlayerSettings.GetAdditionalIl2CppArgs() == arguments, "Native feature compiler arguments differ.");
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            Require((((BuildOptions)captured.playerBuildOptions & BuildOptions.Development) != 0) == development, "Actual Player development flag differs.");
            Require(captured.buildId == generation.baselineBuildId && captured.target == generation.target && captured.architecture == generation.architecture,
                "Actual Player identity differs from selected generation.");
            RequireBaselineCompilerMatches(generation, snapshot, captured);
            var linked = M04AssemblyIdentityProof.ReadLinked(snapshot, captured);
            string typePath = Path.Combine(snapshot, M06ExecutionSchemaVerifier.TypeProofName);
            string executionPath = Path.Combine(snapshot, M06ExecutionSchemaVerifier.ExecutionProofName);
            bool hasType = File.Exists(typePath), hasExecution = File.Exists(executionPath);
            Require(hasType == hasExecution && hasType == replayExistingProofs,
                replayExistingProofs ? "Interrupted capture requires both immutable proof companions." : "New capture proof companions already exist.");
            M06ExecutionProofPaths proofs;
            if (replayExistingProofs)
            {
                proofs = new M06ExecutionProofPaths { typeProofPath = typePath, typeProofSha256 = ShadowHash.File(typePath),
                    executionProofPath = executionPath, executionProofSha256 = ShadowHash.File(executionPath) };
                M06ExecutionSchemaVerifier.VerifyProofs(snapshot, captured, linked, generationPath, proofs.typeProofPath, proofs.typeProofSha256,
                    proofs.executionProofPath, proofs.executionProofSha256);
            }
            else proofs = M06ExecutionSchemaVerifier.WriteProofs(snapshot, captured, linked, generationPath);
            string placeholderPath = Path.Combine(snapshot, PlaceholderName);
            Require(!File.Exists(placeholderPath) && !File.Exists(Path.Combine(snapshot, "m06-execution-policy.json")) && !File.Exists(Path.Combine(snapshot, PlayerReceiptName)),
                "Player receipt companions are immutable and must not be partially finalized.");
            Require(ShadowHash.File(placeholders.sourcePath) == placeholders.sha256, "Placeholder manifest changed during Player build.");
            using (var file = new FileStream(placeholderPath, FileMode.CreateNew, FileAccess.Write, FileShare.None)) file.Write(placeholders.bytes, 0, placeholders.bytes.Length);
            M04AssemblyIdentityProof.WriteNewJson(Path.Combine(snapshot, "m06-execution-policy.json"), selectedStartup);
            var metadata = M04NativeMetadataProof.ReadPlayer(captured.playerOutput, linked);
            var receipt = new M06PlayerBuildReceipt { schemaVersion = 1, milestone = "M06", variant = nativeEnabled ? "NativeOn" : "NativeOff", developmentBuild = development,
                buildOptions = captured.playerBuildOptions, baselineBuildId = settings.buildId, runtimeAbiHash = pins.RuntimeAbiHash(), unityVersion = captured.unityVersion,
                target = captured.target, architecture = captured.architecture, buildGuid = captured.buildGuid, playerOutput = captured.playerOutput,
                inputSnapshot = snapshot, inputSnapshotHash = captured.snapshotHash, nativeLibraryPath = captured.nativeLibraryPath, nativeLibrarySha256 = captured.nativeLibrarySha256,
                nativeArguments = arguments, assemblyIdentities = linked, placeholderManifestPath = placeholderPath, placeholderManifestSha256 = placeholders.sha256, placeholderAssemblyNames = placeholders.names,
                nativeMetadataPath = metadata.path, nativeMetadataSha256 = metadata.sha256, nativeMetadataVersion = metadata.version, nativeAssemblyIdentities = metadata.assemblies, nativeGeneratedAssemblyNames = metadata.generatedAssemblyNames,
                generationProofPath = generationPath, generationProofSha256 = ShadowHash.File(generationPath), typeProofPath = proofs.typeProofPath, typeProofSha256 = proofs.typeProofSha256,
                executionProofPath = proofs.executionProofPath, executionProofSha256 = proofs.executionProofSha256, supplementaryMetadataInputs = MetadataInputs(generation, linked) };
            M04AssemblyIdentityProof.WriteNewJson(Path.Combine(snapshot, PlayerReceiptName), receipt); return snapshot;
        }
        internal static M06SupplementaryMetadataInput[] MetadataInputs(M06GenerationProof proof, M04AssemblyIdentity[] linked)
        {
            string[] required = proof.plans.SelectMany(row => row.requiredAotMetadataNames).Distinct(StringComparer.Ordinal).OrderBy(name => name, StringComparer.Ordinal).ToArray();
            return required.Select(name => {
                var matches = linked.Where(item => item.name == name).ToArray(); Require(matches.Length == 1, "Collector requires metadata absent from actual Player linked/stripped DLLs: " + name);
                var identity = M04AssemblyIdentityProof.ReadFile(matches[0].path, matches[0].sha256, name);
                return new M06SupplementaryMetadataInput { assemblyName = name, path = identity.path, sha256 = identity.sha256, identity = identity };
            }).ToArray();
        }

        public static void BuildFixtures()
        {
            ConfigureMode(RequestedDevelopment()); string generationPath = GenerationArgument(); var generation = M06GenerationBuild.ReadAndVerify(generationPath, false);
            M06GenerationBuild.RequireCurrentSelection(generation);
            var settings = AssemblyShadowSettings.Instance; var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            string selectionPath = Path.Combine(Path.GetDirectoryName(generationPath), "m06-baseline-selection.json");
            Require(File.Exists(selectionPath), "The selected generation has no actual M06 baseline selection.");
            var session = M04JsonEvidence.Read<M06BaselineSelection>(File.ReadAllText(selectionPath));
            Require(session.schemaVersion == 1 && session.milestone == "M06" && session.baselineBuildId == generation.baselineBuildId &&
                session.generationProofPath == generationPath && session.generationProofSha256 == ShadowHash.File(generationPath) && session.developmentBuild == generation.developmentBuild, "M06 baseline selection differs.");
            // The Player receipt replay is intentionally expensive. Resolve every
            // declared warmup target against the immutable compiler bytes first.
            PreflightFixtureWarmups(generation, policy);
            string baselinePath = Path.GetFullPath(AssemblyShadowBuildCommands.Argument("-shadowM06Baseline", session.baselineManifestPath ?? ""));
            Require(File.Exists(baselinePath), "Build this M06 Player baseline first.");
            Require(baselinePath == session.baselineManifestPath, "Explicit baseline differs from the selected actual generation baseline."); VerifyHash(baselinePath, session.baselineManifestSha256);
            var baseline = JsonUtility.FromJson<ShadowBaselineManifest>(File.ReadAllText(baselinePath));
            Require(baseline.baselineBuildId == generation.baselineBuildId, "No reuse of a different milestone/session baseline.");
            string snapshot = Path.GetFullPath(AssemblyShadowBuildCommands.Argument("-shadowPlayerSnapshot", session.playerInputSnapshot ?? ""));
            Require(snapshot == session.playerInputSnapshot, "Explicit Player snapshot differs from the selected actual generation baseline."); VerifyHash(Path.Combine(snapshot, PlayerReceiptName), session.playerBuildReceiptSha256);
            var player = M06EditorValidation.ValidatePlayerReceipt(Path.Combine(snapshot, PlayerReceiptName), snapshot, true);
            Require(player.generationProofPath == generationPath && player.generationProofSha256 == ShadowHash.File(generationPath) && player.developmentBuild == generation.developmentBuild, "Baseline/generation mode differs.");
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            var stable = ShadowFixtureProof.DeriveStableAotNames(snapshot, captured, policy, StableAotHashDomain);
            string root = NewRoot("M06Fixtures-");
            var all = new[] { "P01", "P02", "P03", "InitializerFailure" }.Select(id => BuildFixture(root, id, baselinePath, generation, policy, stable.names)).ToArray();
            var manifest = new M06FixtureManifest { schemaVersion = 1, milestone = "M06", unityVersion = captured.unityVersion, target = captured.target, architecture = captured.architecture,
                baselineBuildId = baseline.baselineBuildId, runtimeAbiHash = baseline.runtimeAbiHash, baselineManifestPath = baselinePath, baselineManifestSha256 = ShadowHash.File(baselinePath),
                baselineInputSnapshot = snapshot, baselineInputSnapshotHash = captured.snapshotHash, generationProofPath = generationPath, generationProofSha256 = ShadowHash.File(generationPath),
                developmentBuild = generation.developmentBuild, candidateNames = M02Build.Candidates.ToArray(), closureLoadOrder = ProviderFirstOrder.ToArray(), stableAotNames = stable.names,
                stableAotProvenance = stable.provenance, stableAotProvenanceHash = stable.provenanceHash, fixtures = all.Take(3).ToArray(), initializerFailureFixture = all[3] };
            string path = Path.Combine(root, FixtureManifestName); M04AssemblyIdentityProof.WriteNewJson(path, manifest);
            Debug.Log("[AssemblyShadow M06] Fixtures: " + path + "; replay: " + M06EditorValidation.ValidateAndWriteReceipt(path));
        }
        private static M06Fixture BuildFixture(string root, string id, string baselinePath, M06GenerationProof generation, ShadowPolicyConfiguration policy, string[] stable)
        {
            var row = generation.plans.Single(item => item.planId == id); var plan = M06GenerationBuild.ReadPlan(generation, id);
            string output = Path.Combine(root, id); ShadowWarmupPlan warmup;
            var captured = AssemblySnapshot.ReadAndVerify(row.compileSnapshot, false);
            using (var set = ShadowFixtureProof.Load(row.compileSnapshot, captured, policy)) warmup = Warmup(set, plan.LoadOrder);
            var patch = ShadowPatchManifestBuilder.BuildWithWarmup(PatchRequest(baselinePath, row, output, generation, policy), warmup);
            RequirePatchPlan(patch.patch, plan, output, generation.developmentBuild);
            var identities = M04AssemblyIdentityProof.ReadPatch(output, patch.patch);
            return new M06Fixture { patchId = id, compileSnapshot = row.compileSnapshot, compileSnapshotHash = row.compileSnapshotHash, patchDirectory = output,
                patchManifest = Path.Combine(output, "patch-manifest.json"), patchManifestSha256 = ShadowHash.File(Path.Combine(output, "patch-manifest.json")),
                variant = generation.developmentBuild ? "Development" : "ReleaseNoPdb", developmentBuild = generation.developmentBuild,
                generationPlanPath = row.planPath, generationPlanSha256 = row.planSha256, defines = row.defines.ToArray(), changedRoots = row.changedRoots.ToArray(),
                closureLoadOrder = patch.patch.loadOrder, stableAotNames = stable.ToArray(), requiredAotMetadataNames = row.requiredAotMetadataNames.ToArray(),
                assemblyIdentities = identities, typeInventories = M05TypeInventoryProof.ReadIdentities(identities) };
        }
        internal static void PreflightFixtureWarmups(M06GenerationProof generation, ShadowPolicyConfiguration policy)
        {
            Require(generation != null && policy != null, "M06 warmup preflight requires verified generation and policy inputs.");
            foreach (string id in new[] { "P01", "P02", "P03", "InitializerFailure" })
            {
                Debug.Log("[AssemblyShadow M06] Fixture warmup preflight begin: " + id);
                var row = generation.plans.Single(item => item.planId == id);
                var plan = M06GenerationBuild.ReadPlan(generation, id);
                var captured = AssemblySnapshot.ReadAndVerify(row.compileSnapshot, false);
                using (var set = ShadowFixtureProof.Load(row.compileSnapshot, captured, policy)) Warmup(set, plan.LoadOrder);
                Debug.Log("[AssemblyShadow M06] Fixture warmup preflight passed: " + id);
            }
        }
        internal static ShadowPatchBuildRequest PatchRequest(string baseline, M06GenerationPlanProof plan, string output, M06GenerationProof generation, ShadowPolicyConfiguration policy)
        { return new ShadowPatchBuildRequest { baselineManifestPath = baseline, currentCompileSnapshot = plan.compileSnapshot, outputDirectory = output, patchId = plan.planId,
            target = (BuildTarget)Enum.Parse(typeof(BuildTarget), generation.target), architecture = generation.architecture, sourcePins = generation.sourcePins, policy = policy,
            explicitChangedRoots = plan.changedRoots, dllOnly = true, includePdb = generation.developmentBuild }; }
        internal static ShadowWarmupPlan Warmup(CompiledAssemblySet inputs, IEnumerable<string> closure)
        {
            var types = new List<ShadowWarmupTypeEntry>(); var methods = new List<ShadowWarmupMethodEntry>();
            foreach (string assembly in closure)
            {
                string type = Witness(assembly); types.Add(new ShadowWarmupTypeEntry { assembly = assembly, type = type });
                var integer = CompilerCorlibIdentity(inputs, assembly, "System.Int32");
                var text = CompilerCorlibIdentity(inputs, assembly, "System.String");
                methods.Add(Method(assembly, type, "WarmupValue", 0, null, integer));
                methods.Add(Method(assembly, type, "WarmupEcho", 1, integer, integer));
                methods.Add(Method(assembly, type, "WarmupEcho", 1, text, text));
                methods.Add(new ShadowWarmupMethodEntry { assembly = assembly, declaringType = type, name = "Run", isStatic = true, genericArity = 0,
                    genericArguments = new ShadowWarmupTypeIdentity[0], returnType = Identity(text.assembly, "System.String[]"),
                    parameterTypes = new[] { Identity(text.assembly, text.type) } });
            }
            return ShadowWarmupValidator.ValidateAndClone(new ShadowWarmupPlan { types = types.ToArray(), methods = methods.ToArray() }, inputs, closure);
        }
        private static ShadowWarmupMethodEntry Method(string assembly, string type, string name, int arity,
            ShadowWarmupTypeIdentity generic, ShadowWarmupTypeIdentity signature)
        {
            return new ShadowWarmupMethodEntry { assembly = assembly, declaringType = type, name = name, isStatic = true, genericArity = arity,
                genericArguments = generic == null ? new ShadowWarmupTypeIdentity[0] : new[] { Identity(generic.assembly, generic.type) },
                returnType = Identity(signature.assembly, signature.type), parameterTypes = new[] { Identity(signature.assembly, signature.type) } };
        }
        private static ShadowWarmupTypeIdentity CompilerCorlibIdentity(CompiledAssemblySet inputs, string owner, string type)
        {
            var module = inputs.GetModule(owner);
            dnlib.DotNet.ITypeDefOrRef reference;
            if (type == "System.Int32") reference = module.CorLibTypes.Int32.TypeDefOrRef;
            else if (type == "System.String") reference = module.CorLibTypes.String.TypeDefOrRef;
            else throw new BuildFailedException("M06 warmup compiler type is outside the finite primitive set: " + type);
            var resolved = inputs.ResolveType(reference);
            Require(resolved != null && resolved.Module != null && resolved.Module.Assembly != null && resolved.ReflectionFullName == type,
                "M06 warmup compiler signature type did not resolve in the captured reference set: " + owner + " -> " + type);
            return Identity(resolved.Module.Assembly.FullName, resolved.ReflectionFullName);
        }
        private static ShadowWarmupTypeIdentity Identity(string assembly, string type)
        { return new ShadowWarmupTypeIdentity { assembly = assembly, type = type }; }
        internal static void RequireBaselineCompilerMatches(M06GenerationProof generation, string playerRoot, AssemblySnapshotReceipt player)
        {
            var compiled = AssemblySnapshot.ReadAndVerify(generation.baselineCompileSnapshot, false);
            ShadowCompilerModeEvidence.ReadAndVerify(generation.baselineCompileSnapshot, (((BuildOptions)player.playerBuildOptions & BuildOptions.Development) != 0));
            foreach (string name in M02Build.Candidates.Concat(new[] { "AssemblyShadowDemo.Bootstrap" }))
            {
                var before = compiled.assemblies.Single(item => item.name == name); var after = player.assemblies.Single(item => item.name == name);
                using (var original = dnlib.DotNet.ModuleDefMD.Load(ShadowHash.SafeChild(generation.baselineCompileSnapshot, before.path)))
                using (var actual = dnlib.DotNet.ModuleDefMD.Load(ShadowHash.SafeChild(playerRoot, after.path)))
                    Require(original.Assembly.FullName == actual.Assembly.FullName && AssemblySemanticHasher.Compute(original).semanticHash == AssemblySemanticHasher.Compute(actual).semanticHash,
                        "Actual M06 baseline candidate/Bootstrap differs from the pre-generation baseline compiler input: " + name);
            }
        }
        internal static void RequirePatchPlan(ShadowPatchManifest patch, VerifiedGenerationPlan plan, string output, bool development)
        {
            Require(patch.loadOrder.SequenceEqual(plan.LoadOrder), "Admitted patch load order differs from compile-only plan.");
            RequireSet(patch.closure.Select(item => item.name), plan.Closure, "Admitted patch closure");
            foreach (var item in patch.closure)
            {
                var image = plan.Receipt.images.Single(entry => entry.name == item.name);
                Require(item.sha256 == image.sha256 && item.mvid == image.mvid, "Patch DLL differs from selected plan bytes."); VerifyHash(ShadowHash.SafeChild(output, item.dll), image.sha256);
                Require(development ? item.pdbSha256 == image.pdbSha256 && string.IsNullOrEmpty(item.pdb) == string.IsNullOrEmpty(image.pdbPath) : string.IsNullOrEmpty(item.pdb) && string.IsNullOrEmpty(item.pdbSha256), "Patch PDB deployment differs from generation/development mode.");
                if (!string.IsNullOrEmpty(item.pdb)) VerifyHash(ShadowHash.SafeChild(output, item.pdb), image.pdbSha256);
            }
            if (!development) Require(Directory.GetFiles(output, "*.pdb", SearchOption.AllDirectories).Length == 0, "Release fixture contains a deployed PDB.");
        }
        internal static string Witness(string assembly)
        {
            switch (assembly)
            {
                case "AssemblyA.Contracts": case "AssemblyA.Implementation.Extensibility": case "AssemblyA.Implementation.Internal": return assembly + ".M06ExecutionWitness";
                case "AssemblyShadowDemo.ContractsConsumer": return "AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness";
                case "AssemblyShadowDemo.ExtensibilityConsumer": return "AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness";
                default: throw new BuildFailedException("No finite warmup witness for " + assembly);
            }
        }
        internal static string[] ExpectedDefines(string id)
        {
            Require(new[] { "P01", "P02", "P03", "InitializerFailure" }.Contains(id), "Unsupported M06 fixture.");
            var result = new List<string> { "ASSEMBLY_SHADOW_P01", "ASSEMBLY_SHADOW_M06" };
            if (id == "P02") result.AddRange(new[] { "ASSEMBLY_SHADOW_P02", "ASSEMBLY_SHADOW_M06_P02" });
            if (id == "P03") result.AddRange(new[] { "ASSEMBLY_SHADOW_P03", "ASSEMBLY_SHADOW_M06_P03" });
            if (id == "InitializerFailure") result.Add("ASSEMBLY_SHADOW_M06_INITIALIZER_THROW"); return result.ToArray();
        }
        internal static string[] ExpectedChangedRoots(string id)
        { ExpectedDefines(id); return id == "P03" ? ProviderFirstOrder.ToArray() : id == "P02" ? new[] { "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ExtensibilityConsumer" } : new[] { "AssemblyA.Implementation.Internal" }; }
        internal static BuildOptions PlayerOptions(bool development) { return BuildOptions.CleanBuildCache | BuildOptions.DetailedBuildReport | (development ? BuildOptions.Development : BuildOptions.None); }
        private static bool PlayerExportProject(BuildTarget target)
        {
#if UNITY_EDITOR_OSX
            if (target == BuildTarget.StandaloneOSX) return UnityEditor.OSXStandalone.UserBuildSettings.createXcodeProject;
#elif UNITY_EDITOR_WIN
            if (target == BuildTarget.StandaloneWindows64) return UnityEditor.WindowsStandalone.UserBuildSettings.createSolution;
#endif
            return false;
        }
        private static void SetPlayerExportProject(BuildTarget target, bool value)
        {
#if UNITY_EDITOR_OSX
            if (target == BuildTarget.StandaloneOSX) UnityEditor.OSXStandalone.UserBuildSettings.createXcodeProject = value;
#elif UNITY_EDITOR_WIN
            if (target == BuildTarget.StandaloneWindows64) UnityEditor.WindowsStandalone.UserBuildSettings.createSolution = value;
#endif
        }
        internal static string NativeArguments(bool enabled) { return "--compiler-flags=\"-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=" + (enabled ? "1" : "0") + "\""; }
        internal static Il2CppCompilerConfiguration NativeConfiguration(bool development) { return development ? Il2CppCompilerConfiguration.Debug : Il2CppCompilerConfiguration.Release; }
        internal static string GenerationArgument() { string path = AssemblyShadowBuildCommands.Argument("-shadowM06Generation", ""); Require(!string.IsNullOrWhiteSpace(path), "Pass the exact -shadowM06Generation proof path."); return Path.GetFullPath(path); }
        internal static string NewRoot(string prefix) { string path = Path.GetFullPath("_temp/AssemblyShadow/" + prefix + Guid.NewGuid().ToString("N")); Require(!Directory.Exists(path) && !File.Exists(path), "Immutable output exists."); Directory.CreateDirectory(path); return path; }
        internal static void RequireSafeId(string id) { Require(!string.IsNullOrEmpty(id) && id.StartsWith("M06-Baseline-", StringComparison.Ordinal) && Path.GetFileName(id) == id && id.IndexOfAny(Path.GetInvalidFileNameChars()) < 0 && id.IndexOfAny(new[] { '/', '\\', '\r', '\n' }) < 0, "Use a safe M06-Baseline-* identity."); }
        internal static void RequireSet(IEnumerable<string> actual, IEnumerable<string> expected, string description) { var a = actual.ToArray(); var b = expected.ToArray(); Require(a.Distinct(StringComparer.Ordinal).Count() == a.Length && b.Distinct(StringComparer.Ordinal).Count() == b.Length && new HashSet<string>(a, StringComparer.Ordinal).SetEquals(b), description + " differs."); }
        internal static void VerifyHash(string path, string hash) { Require(Path.IsPathRooted(path) && File.Exists(path) && !string.IsNullOrEmpty(hash) && ShadowHash.File(path) == hash, "Byte evidence differs: " + path); }
        internal static void Require(bool value, string message) { if (!value) throw new BuildFailedException(message); }
        private static void EnsureScene(string id, string abi)
        {
            Type type = M01BuildSupport.FindType("AssemblyShadowDemo.Bootstrap", "AssemblyShadowDemo.M06BootstrapRunner"); Require(type != null && typeof(MonoBehaviour).IsAssignableFrom(type), "Compile M06BootstrapRunner before Configure.");
            var scene = File.Exists(BootstrapScene) ? EditorSceneManager.OpenScene(BootstrapScene, OpenSceneMode.Single) : EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var found = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren(type, true)).ToArray(); Require(found.Length <= 1, "Duplicate M06 runner.");
            var component = found.Length == 1 ? found[0] : new GameObject("AssemblyShadow M06 Bootstrap").AddComponent(type);
            var serialized = new SerializedObject(component); serialized.FindProperty("expectedBaselineBuildId").stringValue = id; serialized.FindProperty("expectedRuntimeAbiHash").stringValue = abi;
            bool changed = serialized.ApplyModifiedPropertiesWithoutUndo(); if (changed || !File.Exists(BootstrapScene)) Require(EditorSceneManager.SaveScene(scene, BootstrapScene), "Could not save M06 Bootstrap scene.");
        }
    }
}
