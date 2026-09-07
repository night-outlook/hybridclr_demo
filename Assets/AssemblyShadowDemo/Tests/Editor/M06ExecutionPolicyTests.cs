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
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
            Type runner = ConfiguredRunner(policy);
            var inventory = ShadowExecutionPolicy.CaptureCurrentEditor(policy, runner);
            Assert.IsTrue(inventory.IsValid, string.Join("\n", inventory.Diagnostics));
            Assert.AreEqual(runner.Assembly.FullName, inventory.BootstrapAssemblyIdentity);
            Assert.AreEqual(runner.FullName, inventory.BootstrapTypeName);
            MonoScript script = MonoImporter.GetAllRuntimeMonoScripts().Single(item => item != null && item.GetClass() == runner);
            Assert.AreEqual(AssetDatabase.GetAssetPath(script), inventory.BootstrapScriptPath);
            Assert.AreEqual(MonoImporter.GetExecutionOrder(script), inventory.BootstrapExecutionOrder);
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
            Type runner = ConfiguredRunner(policy);
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

        [Test]
        public void M06RunnerRetainsItsPinnedEarliestExecutionOrder()
        {
            Type runner = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M06BootstrapRunner", true);
            MonoScript script = MonoImporter.GetAllRuntimeMonoScripts().Single(item => item != null && item.GetClass() == runner);
            Assert.AreEqual(-32000, MonoImporter.GetExecutionOrder(script));
        }

        private static Type ConfiguredRunner(ShadowPolicyConfiguration policy)
        {
            EditorBuildSettingsScene scene = EditorBuildSettings.scenes.Single(item => item.enabled);
            var bootstrap = policy.assemblies.Where(item => item != null && item.isBootstrap && !item.isShadowCapable)
                .Select(item => item.name).ToArray();
            Type[] runners = AssetDatabase.GetDependencies(scene.path, true)
                .Select(AssetDatabase.LoadAssetAtPath<MonoScript>).Where(script => script != null)
                .Select(script => script.GetClass()).Where(type => type != null && typeof(MonoBehaviour).IsAssignableFrom(type) &&
                    bootstrap.Contains(type.Assembly.GetName().Name, StringComparer.OrdinalIgnoreCase) &&
                    type.GetMethod("Awake", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic) != null)
                .Distinct().ToArray();
            Assert.AreEqual(1, runners.Length, "The configured startup scene must resolve one actual fixed-bootstrap Awake runner.");
            return runners[0];
        }
    }
}
