using System;
using System.IO;
using System.Linq;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.AssemblyShadow;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class M02Build
    {
        public static readonly string[] Candidates = {
            "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
            "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"
        };

        public static void Configure()
        {
            BaselineBuild.Configure();
            BaselineBuild.SetNativeFeature(true);
            EditorUserBuildSettings.development = true;
            EditorUserBuildSettings.buildScriptsOnly = false;
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(M01Paths.BootstrapScene, true) };
            var settings = AssemblyShadowSettings.Instance;
            settings.enableAssemblyShadow = true;
            settings.shadowAssemblyNames = Candidates;
            settings.bootstrapAssemblyNames = new[] { "AssemblyShadowDemo.Bootstrap" };
            settings.allowedInternalEditorAssemblies = new[] { "AssemblyShadowDemo.Editor", "AssemblyShadowDemo.EditorTests" };
            settings.precompiledAssemblyCapabilities = new[] {
                new AssemblyCapability { name = "Newtonsoft.Json", isShadowCapable = false },
                new AssemblyCapability { name = "Unity.Burst.Unsafe", isShadowCapable = false },
                new AssemblyCapability { name = "Unity.Collections.LowLevel.ILSupport", isShadowCapable = false },
                // This is a real compiler dependency of UnityEngine.TestRunner.
                // Actual Player filter evidence, not its name, excludes it from AOT.
                new AssemblyCapability { name = "nunit.framework", isShadowCapable = false },
                new AssemblyCapability { name = "Unity.VisualScripting.Antlr3.Runtime", isShadowCapable = false },
            };
            settings.architecture = BaselineBuild.TargetArchitecture();
            settings.buildId = "M02-Baseline";
            settings.resourceBuildMapPath = "ProjectSettings/AssemblyShadowResources.json";
            settings.enforceResourceAbi = true;
            settings.rejectUnknownReflectionDependencies = true;
            AssemblyShadowSettings.Save();
            AssemblyShadowSettingsUtil.ValidateSettingsOrThrow();
            AssetDatabase.SaveAssets();
            Debug.Log("[AssemblyShadow M02] Configured independent candidates; ordinary hot-update filtering is unchanged.");
        }

        public static void ValidateConfiguration()
        {
            Configure();
            var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            Directory.CreateDirectory("_temp/AssemblyShadow");
            File.WriteAllText("_temp/AssemblyShadow/m02-policy-inventory.json", JsonUtility.ToJson(policy, true));
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            Debug.Log("[AssemblyShadow M02] Actual target compiler inventory and source policy validated.");
        }

        public static void BuildPlayerBaseline()
        {
            Configure();
            var target = EditorUserBuildSettings.activeBuildTarget;
            var settings = AssemblyShadowSettings.Instance;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();
            string frozen = M01Paths.BaselineRoot(target);
            BuildBaselineBundles.VerifyExisting(frozen);
            M01BuildSupport.StageBaselineArtifacts(frozen, Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01"));
            M02ReflectionBindingValidation.StageConfiguration();
            PrebuildCommand.GenerateAll();
            string snapshot = Path.GetFullPath("_temp/AssemblyShadow/M02PlayerInputs-" + Guid.NewGuid().ToString("N"));
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string buildId = AssemblyShadowBuildCommands.Argument("-shadowBaselineId", settings.buildId + "-" + ShadowHash.Text(pins.RuntimeAbiHash() + ":" + pins.demo.revision).Substring(0, 16));
            string[] compilationDefines = ShadowReflectionBindingEvidence.CompilationDefines(new string[0]);
            ShadowPlayerInputCapture.Begin(snapshot, buildId, target, settings.architecture, pins, Candidates, compilationDefines);
            try
            {
                string output = AssemblyShadowBuildCommands.Argument("-shadowBuildOutput", "Builds/AssemblyShadow/M02/Baseline.app");
                if (target == BuildTarget.StandaloneWindows64 && output.EndsWith(".app", StringComparison.Ordinal))
                    output = output.Substring(0, output.Length - 4) + ".exe";
                Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)));
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { M01Paths.BootstrapScene }, locationPathName = output,
                    target = target, targetGroup = BuildTargetGroup.Standalone,
                    options = BuildOptions.Development | BuildOptions.DetailedBuildReport,
                    extraScriptingDefines = compilationDefines,
                });
                ShadowPlayerInputCapture.CompleteSuccessfulBuild(report);
            }
            finally { ShadowPlayerInputCapture.End(); }
            var captured = AssemblySnapshot.ReadAndVerify(snapshot, true);
            foreach (string name in new[] { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal" })
            {
                var input = captured.assemblies.Single(a => a.name == name);
                CompilePatchDlls.VerifySemanticEquivalence(Path.Combine(frozen, "AssemblySnapshot/" + name + ".dll"), Path.Combine(snapshot, input.path));
            }
            var session = ShadowBuildSession.Load();
            session.playerInputSnapshot = snapshot;
            session.resourceBaselinePath = M02FrozenResources.Import(frozen, snapshot,
                Path.Combine("HybridCLRData/AssemblyShadow/ResourceBaselines", target.ToString(), buildId), target, settings.architecture, policy);
            session.Save();
            AssemblyShadowBuildCommands.BuildBaselineManifest();
            Debug.Log("[AssemblyShadow M02] Baseline established from actual Player inputs; frozen M01 bundles reused unchanged.");
        }

        public static void ValidateCompilerInputs()
        {
            ValidateConfiguration();
            var settings = AssemblyShadowSettings.Instance;
            var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, target, settings.architecture);
            string snapshot = AssemblySnapshot.Compile(Path.GetFullPath("_temp/AssemblyShadow/M02CompilerPreflight-" + Guid.NewGuid().ToString("N")),
                target, settings.architecture, pins, policy, new string[0]);
            Debug.Log("[AssemblyShadow M02] Compiler preflight snapshot: " + snapshot);
            var receipt = AssemblySnapshot.ReadAndVerify(snapshot, false);
            var framework = TargetFrameworkReferenceVerifier.Verify(snapshot, receipt);
            using (var set = DnlibAssemblyLoader.Load(Path.Combine(snapshot, "Assemblies"), new[] { Path.Combine(snapshot, "References") }, policy.assemblies,
                targetFrameworkReferences: framework))
            {
                foreach (string reference in set.DeferredFacadeReferences)
                    Debug.LogWarning("[AssemblyShadow M02] Unused optional framework forwarder (not resolved): " + reference);
                ShadowReflectionBindingEvidence.ValidateCompiled(set, policy, snapshot, receipt, false).ThrowIfInvalid();
            }
            Debug.Log("[AssemblyShadow M02] Fresh target compiler metadata and compiled policy validated (not a Player baseline).");
        }
    }
}
