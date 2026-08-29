using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06StartupOrderTests
    {
        [Test]
        public void ActualImportedCallbackOrderRejectsEarlyCandidateDependencyAndAcceptsLaterOrder()
        {
            Type runner = Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType("AssemblyShadowDemo.M06BootstrapRunner", true);
            MonoScript runnerScript = MonoImporter.GetAllRuntimeMonoScripts().Single(script => script != null && script.GetClass() == runner);
            int runnerOrder = MonoImporter.GetExecutionOrder(runnerScript);
            Assert.AreEqual(-32000, runnerOrder);
            const string callbackPath = "Assets/AssemblyShadowDemo/Tests/Runtime/M06EarlyStartupProbe.cs";
            MonoScript callback = AssetDatabase.LoadAssetAtPath<MonoScript>(callbackPath);
            Assert.IsNotNull(callback);
            Type callbackType = callback.GetClass();
            Assert.IsNotNull(callbackType);
            Assert.AreEqual("AssemblyShadowDemo.M06EarlyStartupProbe", callbackType.FullName);
            Assert.IsTrue(callbackType.Assembly.GetReferencedAssemblies().Any(assembly => assembly.Name == "AssemblyA.Contracts"), "Use the actual imported runtime test assembly, not a fabricated dependency descriptor.");
            int originalOrder = MonoImporter.GetExecutionOrder(callback), injectedOrder = originalOrder;
            string metadata = Path.GetFullPath(callbackPath + ".meta"), sourceHash = ShadowHash.File(callbackPath);
            byte[] originalMetadata = File.ReadAllBytes(metadata);
            string injectedMetadataHash = ShadowHash.Bytes(originalMetadata);
            EditorBuildSettingsScene[] originalSettings = EditorBuildSettings.scenes;
            Scene originalScene = SceneManager.GetActiveScene(), temporary = default(Scene);
            string id = Guid.NewGuid().ToString("N");
            string asset = "Assets/AssemblyShadowDemo/Tests/Editor/M06StartupOrder-" + id + ".unity";
            string evidence = Path.GetFullPath("_temp/AssemblyShadow/M06StartupOrder-" + id);
            Assert.IsFalse(File.Exists(asset) || File.Exists(asset + ".meta") || Directory.Exists(evidence));
            Directory.CreateDirectory(evidence);
            File.Copy(callbackPath, Path.Combine(evidence, "callback.cs"));
            File.Copy(metadata, Path.Combine(evidence, "callback-original.cs.meta"));
            var injectedSettings = new[] { new EditorBuildSettingsScene(asset, true) };
            bool settingsChanged = false, orderChanged = false;
            string sceneHash = "", sceneMetaHash = "";
            try
            {
                Assert.IsTrue(AssetDatabase.CopyAsset(AssemblyShadowDemo.Editor.M06Build.BootstrapScene, asset),
                    "Could not create a test-owned copy of the configured M06 bootstrap scene.");
                AssetDatabase.ImportAsset(asset, ImportAssetOptions.ForceSynchronousImport);
                temporary = EditorSceneManager.OpenScene(asset, UnityEditor.SceneManagement.OpenSceneMode.Additive);
                Assert.IsTrue(SceneManager.SetActiveScene(temporary));
                Assert.IsNotNull(new GameObject("M06 actual candidate-dependent callback").AddComponent(callbackType));
                Assert.IsTrue(EditorSceneManager.SaveScene(temporary, asset));
                AssetDatabase.ImportAsset(asset, ImportAssetOptions.ForceSynchronousImport);
                sceneHash = ShadowHash.File(asset); sceneMetaHash = ShadowHash.File(asset + ".meta");
                File.Copy(asset, Path.Combine(evidence, "startup.unity"));
                File.Copy(asset + ".meta", Path.Combine(evidence, "startup.unity.meta"));
                EditorBuildSettings.scenes = injectedSettings; settingsChanged = true;
                var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
                foreach (int requested in new[] { runnerOrder - 1, runnerOrder, runnerOrder + 1 })
                {
                    orderChanged = true;
                    MonoImporter.SetExecutionOrder(callback, requested);
                    AssetDatabase.SaveAssets();
                    injectedOrder = MonoImporter.GetExecutionOrder(callback);
                    injectedMetadataHash = ShadowHash.File(metadata);
                    bool early = requested <= runnerOrder;
                    // The effective importer order, including any Editor clamping,
                    // is the evidence. Ties are unsafe because ordering is not fixed.
                    Assert.AreEqual(early, injectedOrder <= runnerOrder);
                    var inventory = ShadowExecutionPolicy.CaptureCurrentEditor(policy, runner);
                    var observed = inventory.Scripts.Single(script => script.TypeName == callbackType.FullName);
                    string phase = requested < runnerOrder ? "before" : early ? "tied" : "after";
                    WriteNew(Path.Combine(evidence, phase + ".json"), JsonUtility.ToJson(new OrderEvidence {
                        phase = phase, requestedOrder = requested, actualOrder = injectedOrder, bootstrapOrder = inventory.BootstrapExecutionOrder,
                        scenePath = asset, sceneSha256 = sceneHash, scriptPath = callbackPath, scriptSha256 = sourceHash, scriptMetaSha256 = injectedMetadataHash,
                        assemblyIdentity = observed.AssemblyIdentity, typeName = observed.TypeName, candidateDependent = observed.IsCandidateDependent,
                        dependencyProved = observed.DependencyProved, callbacks = observed.Callbacks, dependencyEvidence = observed.DependencyEvidence,
                        valid = inventory.IsValid, diagnostics = inventory.Diagnostics,
                    }, true));
                    File.Copy(metadata, Path.Combine(evidence, phase + ".cs.meta"));
                    Assert.AreEqual(injectedOrder, observed.ExecutionOrder);
                    Assert.AreEqual(callback.GetClass().Assembly.FullName, observed.AssemblyIdentity);
                    Assert.IsTrue(observed.IsCandidateDependent);
                    Assert.IsTrue(observed.Callbacks.Contains("Awake"));
                    Assert.IsTrue(observed.DependencyEvidence.Any(item => item.StartsWith("current-editor-reference:", StringComparison.Ordinal) && item.Contains("AssemblyA.Contracts")));
                    Assert.AreEqual(early, inventory.Diagnostics.Any(item => item.StartsWith("ScriptExecutionBeforeBootstrap:", StringComparison.Ordinal) && item.Contains(observed.TypeName)), string.Join("\n", inventory.Diagnostics));
                    if (!early) Assert.IsTrue(inventory.IsValid, string.Join("\n", inventory.Diagnostics));
                }
            }
            finally
            {
                var failures = new List<string>();
                bool settingsRestored = !settingsChanged;
                if (settingsChanged)
                {
                    if (SameSettings(EditorBuildSettings.scenes, injectedSettings))
                    { EditorBuildSettings.scenes = originalSettings; settingsRestored = SameSettings(EditorBuildSettings.scenes, originalSettings); }
                    if (!settingsRestored) failures.Add("Concurrent build-scene settings were preserved; the temporary scene was retained for inspection.");
                }
                bool orderRestored = !orderChanged;
                if (orderChanged)
                {
                    if (MonoImporter.GetExecutionOrder(callback) == injectedOrder && ShadowHash.File(metadata) == injectedMetadataHash && ShadowHash.File(callbackPath) == sourceHash)
                    {
                        // Restore only the exact test-owned importer change. Keep the
                        // original .meta bytes as well as its effective order.
                        File.WriteAllBytes(metadata, originalMetadata);
                        AssetDatabase.ImportAsset(callbackPath, ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                        orderRestored = MonoImporter.GetExecutionOrder(callback) == originalOrder && File.ReadAllBytes(metadata).SequenceEqual(originalMetadata);
                    }
                    if (!orderRestored) failures.Add("Concurrent script/importer state was preserved; restore requires inspection of the retained evidence.");
                }
                bool activeRestored = SceneManager.GetActiveScene() == originalScene;
                if (temporary.IsValid() && SceneManager.GetActiveScene() == temporary && originalScene.IsValid() && originalScene.isLoaded)
                    activeRestored = SceneManager.SetActiveScene(originalScene);
                if (!activeRestored) failures.Add("The active scene changed concurrently and was not overwritten.");
                bool removed = !File.Exists(asset);
                if (temporary.IsValid() && !temporary.isDirty && settingsRestored && activeRestored && File.Exists(asset) &&
                    ShadowHash.File(asset) == sceneHash && ShadowHash.File(asset + ".meta") == sceneMetaHash)
                {
                    if (EditorSceneManager.CloseScene(temporary, true)) removed = AssetDatabase.DeleteAsset(asset);
                }
                if (!removed) failures.Add("The test-created scene changed or could not be safely removed: " + asset);
                WriteNew(Path.Combine(evidence, "restore.json"), JsonUtility.ToJson(new RestoreEvidence {
                    settingsRestored = settingsRestored, orderRestored = orderRestored, activeSceneRestored = activeRestored,
                    temporarySceneRemoved = removed, originalOrder = originalOrder, actualOrder = MonoImporter.GetExecutionOrder(callback),
                    originalMetaSha256 = ShadowHash.Bytes(originalMetadata), actualMetaSha256 = ShadowHash.File(metadata), failures = failures.ToArray(),
                }, true));
                Debug.Log("[AssemblyShadow M06] Actual imported startup-order evidence: " + evidence);
                Assert.IsEmpty(failures, string.Join("\n", failures));
            }
        }

        private static bool SameSettings(EditorBuildSettingsScene[] left, EditorBuildSettingsScene[] right)
        { return left != null && right != null && left.Length == right.Length && left.Zip(right, (a, b) => a.path == b.path && a.enabled == b.enabled).All(equal => equal); }
        private static void WriteNew(string path, string text)
        { using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None)) using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(text); }

        [Serializable] private sealed class OrderEvidence
        {
            public int schemaVersion = 1, requestedOrder, actualOrder, bootstrapOrder;
            public string phase, scenePath, sceneSha256, scriptPath, scriptSha256, scriptMetaSha256, assemblyIdentity, typeName;
            public bool candidateDependent, dependencyProved, valid;
            public string[] callbacks, dependencyEvidence, diagnostics;
        }
        [Serializable] private sealed class RestoreEvidence
        {
            public int schemaVersion = 1, originalOrder, actualOrder;
            public bool settingsRestored, orderRestored, activeSceneRestored, temporarySceneRemoved;
            public string originalMetaSha256, actualMetaSha256;
            public string[] failures;
        }
    }
}
