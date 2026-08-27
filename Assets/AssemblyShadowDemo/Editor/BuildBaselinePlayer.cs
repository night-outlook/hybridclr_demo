using System;
using System.IO;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.Commands;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Player;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    public static class BuildBaselinePlayer
    {
        public static void Build()
        {
            BuildBaselineBundles.Build();
            BaselineBuild.Configure();
            M01BuildSupport.EnsureDemoAssets();
            M01BuildSupport.EnsureBootstrapScene();
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(M01Paths.BootstrapScene, true) };
            AssetDatabase.SaveAssets();
            PrebuildCommand.GenerateAll();

            string root = M01Paths.BaselineRoot(EditorUserBuildSettings.activeBuildTarget);
            BuildBaselineBundles.VerifyExisting(root);
            string staged = Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01");
            M01BuildSupport.StageBaselineArtifacts(root, staged);

            // BaselineBuild.Configure intentionally resets this OFF; M01 enables the native PoC only after it
            // and deliberately leaves it ON for this source configuration.
            BaselineBuild.SetNativeFeature(true);
            BaselineBuild.BuildPlayer("M01", M01Paths.BootstrapScene,
                "Builds/AssemblyShadow/M01/Prototype.app");
            M01PlayerBuildEvidence.Capture(EditorUserBuildSettings.activeBuildTarget,
                "Builds/AssemblyShadow/M01/Prototype.app");
        }
    }
}
