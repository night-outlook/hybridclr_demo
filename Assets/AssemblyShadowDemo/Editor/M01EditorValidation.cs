using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AssemblyA.Implementation.Extensibility;
using AssemblyA.Implementation.Internal;
using AssemblyShadowBaseline.Editor;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Static editor gate for artifact/configuration checks; it does not claim Player runtime evidence.</summary>
    public static class M01EditorValidation
    {
        public static void Validate()
        {
            var cases = new List<Case>();
            Check(cases, "bootstrap_has_no_business_references", CheckBootstrapAssembly);
            Check(cases, "baseline_aot_configuration", CheckAotConfiguration);
            Check(cases, "asset_guids_and_serialized_values", CheckAssets);
            Check(cases, "immutable_manifest_and_bundle_hashes", CheckManifest);
            Check(cases, "patch_abi_when_present", CheckPatchAbi);
            var evidence = new Evidence { runtimeEvidence = false, passed = cases.All(item => item.passed), tests = cases.ToArray() };
            Directory.CreateDirectory("_temp/AssemblyShadow");
            File.WriteAllText("_temp/AssemblyShadow/m01-editor-validation.json", JsonUtility.ToJson(evidence, true));
            Debug.Log("[AssemblyShadow M01] Editor validation: " + JsonUtility.ToJson(evidence));
            if (!evidence.passed)
                throw new BuildFailedException("M01 editor validation failed.");
        }

        private static void CheckBootstrapAssembly()
        {
            const string path = "Assets/AssemblyShadowDemo/Bootstrap/AssemblyShadowDemo.Bootstrap.asmdef";
            if (!File.Exists(path))
                throw new InvalidOperationException("Bootstrap asmdef is missing: " + path);
            Definition definition = JsonUtility.FromJson<Definition>(File.ReadAllText(path));
            string[] business = { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal", "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer" };
            if (definition.references != null && definition.references.Any(reference => business.Contains(reference)))
                throw new InvalidOperationException("Bootstrap has a business assembly reference.");
        }

        private static void CheckAotConfiguration()
        {
            string[] hot = HybridCLRSettings.Instance.hotUpdateAssemblies ?? Array.Empty<string>();
            if (!hot.SequenceEqual(new[] { "AssemblyShadowBaseline.HotUpdate" }))
                throw new InvalidOperationException("M00 ordinary hot-update list was changed.");
            if (hot.Any(item => item.StartsWith("AssemblyA.", StringComparison.Ordinal) || item.StartsWith("AssemblyShadowDemo.", StringComparison.Ordinal)))
                throw new InvalidOperationException("M01 business assembly is configured as ordinary HotUpdate.");
        }

        private static void CheckAssets()
        {
            var data = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(M01Paths.Data);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(M01Paths.Prefab);
            if (data == null || prefab == null)
                throw new InvalidOperationException("M01 resources are missing.");
            var component = prefab.GetComponent<VersionedPrefabComponent>();
            if (component == null || component.ReadSerializedNumber() != 1234 || component.ReadBaseSerializedValue() != 7)
                throw new InvalidOperationException("Prefab serialized values are not stable.");
            if (data.ReadSerializedNumber() != 5678)
                throw new InvalidOperationException("ScriptableObject serialized values are not stable.");
            if (string.IsNullOrEmpty(M01BuildSupport.AssetGuid(M01Paths.Prefab)) || string.IsNullOrEmpty(M01BuildSupport.ScriptGuid(component)))
                throw new InvalidOperationException("Prefab GUID metadata is missing.");
            if (string.IsNullOrEmpty(M01BuildSupport.AssetGuid(M01Paths.Data)))
                throw new InvalidOperationException("ScriptableObject GUID metadata is missing.");
        }

        private static void CheckManifest()
        {
            string root = M01Paths.BaselineRoot(EditorUserBuildSettings.activeBuildTarget);
            BuildBaselineBundles.VerifyExisting(root);
            var manifest = BuildBaselineBundles.ReadManifest(root);
            var prefab = manifest.assets.FirstOrDefault(item => item.kind == "prefab");
            var data = manifest.assets.FirstOrDefault(item => item.kind == "scriptableObject");
            if (prefab == null || prefab.assetGuid != M01BuildSupport.AssetGuid(M01Paths.Prefab) || prefab.serializedNumber != 1234)
                throw new InvalidOperationException("Prefab manifest metadata mismatch.");
            if (data == null || data.assetGuid != M01BuildSupport.AssetGuid(M01Paths.Data) || data.serializedNumber != 5678)
                throw new InvalidOperationException("Data manifest metadata mismatch.");
        }

        private static void CheckPatchAbi()
        {
            string patch = Path.Combine(M01Paths.PatchDirectory, M01Paths.InternalAssemblyName + ".dll");
            if (!File.Exists(patch)) return;
            string baseline = Path.Combine(M01Paths.BaselineRoot(EditorUserBuildSettings.activeBuildTarget), "AssemblySnapshot/" + M01Paths.InternalAssemblyName + ".dll");
            CompilePatchDlls.VerifyAbi(baseline, patch);
            if (M01BuildSupport.ReadMvid(baseline) == M01BuildSupport.ReadMvid(patch))
                throw new InvalidOperationException("Patch MVID equals baseline MVID.");
        }

        private static void Check(List<Case> cases, string name, Action action)
        {
            var item = new Case { name = name };
            try { action(); item.passed = true; }
            catch (Exception exception) { item.error = exception.ToString(); }
            cases.Add(item);
        }

        [Serializable] private sealed class Definition { public string[] references; }
        [Serializable] private sealed class Case { public string name; public bool passed; public string error; }
        [Serializable] private sealed class Evidence { public bool runtimeEvidence; public bool passed; public Case[] tests; }
    }
}
