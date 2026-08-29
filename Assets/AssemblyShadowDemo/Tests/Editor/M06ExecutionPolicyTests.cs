using System;
using System.Linq;
using System.Reflection;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06ExecutionPolicyTests
    {
        [Test]
        public void ActualStartupInventoryBindsConfiguredRunnerSceneAndEffectiveImporterOrder()
        {
            Type runner = Runner();
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
            var inventory = ShadowExecutionPolicy.CaptureCurrentEditor(policy, runner);
            Assert.IsTrue(inventory.IsValid, string.Join("\n", inventory.Diagnostics));
            Assert.AreEqual(runner.Assembly.FullName, inventory.BootstrapAssemblyIdentity);
            Assert.AreEqual(runner.FullName, inventory.BootstrapTypeName);
            MonoScript script = MonoImporter.GetAllRuntimeMonoScripts().Single(item => item != null && item.GetClass() == runner);
            Assert.AreEqual(AssetDatabase.GetAssetPath(script), inventory.BootstrapScriptPath);
            Assert.AreEqual(MonoImporter.GetExecutionOrder(script), inventory.BootstrapExecutionOrder);
            Assert.AreEqual(-32000, inventory.BootstrapExecutionOrder);
            Assert.AreEqual(EditorBuildSettings.scenes.Single(item => item.enabled).path, inventory.StartupScenePath);
            Assert.IsTrue(inventory.Scripts.Any(item => item.IsBootstrapRunner && item.Callbacks.Contains("Awake") && item.AssetPath == inventory.StartupScenePath));
            // Returned arrays cannot be used to rewrite the captured inventory.
            var copy = inventory.Scripts; copy[0] = null;
            Assert.IsNotNull(inventory.Scripts[0]);
        }

        [Test]
        public void ActualCandidatePreloadedAssetIsRejectedAndOriginalPlayerSettingsAreRestored()
        {
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
            Type runner = Runner();
            ScriptableObject candidate = AssetDatabase.FindAssets("t:VersionedScriptableObject").Select(AssetDatabase.GUIDToAssetPath)
                .Select(AssetDatabase.LoadAssetAtPath<ScriptableObject>).FirstOrDefault(asset => asset != null && asset.GetType().Assembly.GetName().Name == "AssemblyA.Implementation.Internal");
            Assert.IsNotNull(candidate, "The actual imported candidate ScriptableObject fixture must exist.");
            UnityEngine.Object[] original = PlayerSettings.GetPreloadedAssets();
            Assert.IsNotNull(original);
            Assert.IsFalse(original.Contains(candidate), "The normal startup configuration already preloads the business fixture.");
            UnityEngine.Object[] injected = original.Concat(new UnityEngine.Object[] { candidate }).ToArray();
            bool restored = false;
            try
            {
                PlayerSettings.SetPreloadedAssets(injected);
                var inventory = ShadowExecutionPolicy.CaptureCurrentEditor(policy, runner);
                Assert.IsFalse(inventory.IsValid);
                Assert.IsTrue(inventory.Diagnostics.Any(item => item.StartsWith("PreloadedCandidateAsset:", StringComparison.Ordinal)), string.Join("\n", inventory.Diagnostics));
                Assert.IsTrue(inventory.PreloadedAssets.Any(item => item.IsCandidate && item.AssetPath == AssetDatabase.GetAssetPath(candidate) && item.AssemblyIdentity == candidate.GetType().Assembly.FullName));
            }
            finally
            {
                UnityEngine.Object[] current = PlayerSettings.GetPreloadedAssets();
                if (current != null && current.SequenceEqual(injected))
                {
                    PlayerSettings.SetPreloadedAssets(original);
                    restored = PlayerSettings.GetPreloadedAssets().SequenceEqual(original);
                }
                else
                    Debug.LogError("M06 preload regression observed concurrent PlayerSettings changes; refusing to overwrite them. Review the current preloaded list before continuing.");
                Assert.IsTrue(restored, "Original preloaded assets were not restored exactly; concurrent state was left untouched for investigation.");
            }
        }

        private static Type Runner()
        {
            return Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M06BootstrapRunner", true);
        }
    }
}
