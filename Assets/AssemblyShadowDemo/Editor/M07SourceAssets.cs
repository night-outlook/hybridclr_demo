using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyA.Contracts;
using AssemblyA.Implementation.Internal;
using AssemblyShadowDemo.Consumers;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor;
using UnityEditor.Events;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Creates and verifies the authored inputs for all seven M07 bundles.</summary>
    internal static class M07SourceAssets
    {
        internal const string BaselineRoot = "Assets/AssemblyShadowDemo/M07Resources/Baseline";
        internal const string P05Root = "Assets/AssemblyShadowDemo/M07Resources/P05";

        internal static ShadowResourceBuildMap Ensure(bool structural)
        {
            string root = structural ? P05Root : BaselineRoot;
            bool hasStructuralField = typeof(VersionedPrefabComponent).GetField("addedSerializedField", BindingFlags.Instance | BindingFlags.NonPublic) != null;
            Require(hasStructuralField == structural, "The active Editor domain does not match the requested M07 resource layout.");
            EnsureFolder(root);

            VersionedScriptableObject data = EnsureData(root + "/VersionedData.asset");
            M07ManagedGraphAsset graph = EnsureGraph(root + "/ManagedGraph.asset");
            GameObject versioned = EnsureVersionedPrefab(root + "/VersionedPrefab.prefab", data, structural, "VersionedPrefab");
            EnsureNestedPrefab(root + "/NestedPrefab.prefab", data, structural);
            EnsureMixedPrefab(root + "/MixedAssets.prefab", data, structural);
            EnsureScene(root + "/BusinessScene.unity", versioned, data, graph, false);
            EnsureScene(root + "/AdditiveScene.unity", versioned, data, graph, true);
            EnsureMonoScriptCarrier(root + "/MonoScriptCarrier.asset");
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            return ValidateExisting(structural);
        }

        /// <summary>
        /// Validates the already-authored source inputs without changing the AssetDatabase or
        /// opening a scene. Build/replay entry points must use this method when they consume the
        /// pinned fixture; <see cref="Ensure"/> remains the explicit authoring path.
        /// </summary>
        internal static ShadowResourceBuildMap ValidateExisting(bool structural)
        {
            string root = structural ? P05Root : BaselineRoot;
            bool hasStructuralField = typeof(VersionedPrefabComponent).GetField("addedSerializedField", BindingFlags.Instance | BindingFlags.NonPublic) != null;
            Require(hasStructuralField == structural, "The active Editor domain does not match the requested M07 resource layout.");
            ShadowResourceBuildMap map = Map(root);
            Validate(root, structural, map);
            return map;
        }

        internal static ShadowResourceBuildMap Map(string root)
        {
            return new ShadowResourceBuildMap {
                schemaVersion = 1,
                bundleDirectory = "Bundles",
                bundles = new[] {
                    Bundle("versioned-prefab.bundle", root + "/VersionedPrefab.prefab"),
                    Bundle("nested-prefab.bundle", root + "/NestedPrefab.prefab"),
                    Bundle("business-scene.bundle", root + "/BusinessScene.unity"),
                    Bundle("additive-scene.bundle", root + "/AdditiveScene.unity"),
                    Bundle("scriptable-object.bundle", root + "/VersionedData.asset"),
                    Bundle("serialize-reference.bundle", root + "/ManagedGraph.asset"),
                    Bundle("mixed-assets.bundle", root + "/MixedAssets.prefab", root + "/MonoScriptCarrier.asset"),
                }
            };
        }

        private static VersionedScriptableObject EnsureData(string path)
        {
            var asset = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(path);
            if (asset == null)
            {
                asset = ScriptableObject.CreateInstance<VersionedScriptableObject>();
                AssetDatabase.CreateAsset(asset, path);
            }
            asset.name = "M07 Versioned Data";
            var serialized = new SerializedObject(asset);
            SetDemoValue(serialized.FindProperty("value"), 5678, "M07-DATA");
            SetInlineValue(serialized.FindProperty("m07InlineValue"), 81, "M07-INLINE-DATA");
            SetInlineArray(serialized.FindProperty("m07InlineValues"), new[] { 82, 83 }, "M07-DATA-LIST-");
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(asset);
            return asset;
        }

        private static M07ManagedGraphAsset EnsureGraph(string path)
        {
            var asset = AssetDatabase.LoadAssetAtPath<M07ManagedGraphAsset>(path);
            if (asset == null)
            {
                asset = ScriptableObject.CreateInstance<M07ManagedGraphAsset>();
                AssetDatabase.CreateAsset(asset, path);
            }
            asset.name = "M07 Managed Graph";
            var first = new M07NodeA();
            first.SetNext(new M07NodeB());
            var serialized = new SerializedObject(asset);
            serialized.FindProperty("node").managedReferenceValue = first;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(asset);
            return asset;
        }

        private static GameObject EnsureVersionedPrefab(string path, VersionedScriptableObject data, bool structural, string name)
        {
            var root = new GameObject(name);
            try
            {
                var component = root.AddComponent<VersionedPrefabComponent>();
                ConfigureVersioned(component, data, null, structural);
                GameObject saved = PrefabUtility.SaveAsPrefabAsset(root, path);
                Require(saved != null, "Could not save M07 versioned prefab: " + path);
                return saved;
            }
            finally { Object.DestroyImmediate(root); }
        }

        private static void EnsureNestedPrefab(string path, VersionedScriptableObject data, bool structural)
        {
            var root = new GameObject("M07 Nested Prefab");
            try
            {
                var internalComponent = root.AddComponent<VersionedPrefabComponent>();
                var child = new GameObject("M07 Nested Child");
                child.transform.SetParent(root.transform, false);
                var external = child.AddComponent<DerivedExternalComponent>();
                ConfigureVersioned(internalComponent, data, external, structural);
                var serialized = new SerializedObject(external);
                serialized.FindProperty("relatedComponent").objectReferenceValue = internalComponent;
                serialized.FindProperty("m07SerializedLabel").stringValue = "M07-NESTED-EXTERNAL";
                serialized.ApplyModifiedPropertiesWithoutUndo();
                Require(PrefabUtility.SaveAsPrefabAsset(root, path) != null, "Could not save M07 nested prefab.");
            }
            finally { Object.DestroyImmediate(root); }
        }

        private static void EnsureMixedPrefab(string path, VersionedScriptableObject data, bool structural)
        {
            var root = new GameObject("M07 Mixed Assets");
            try
            {
                ConfigureVersioned(root.AddComponent<VersionedPrefabComponent>(), data, null, structural);
                root.AddComponent<M07RenameProbeComponent>();
                Require(PrefabUtility.SaveAsPrefabAsset(root, path) != null, "Could not save M07 mixed prefab.");
            }
            finally { Object.DestroyImmediate(root); }
        }

        private static void EnsureScene(string path, GameObject prefab, VersionedScriptableObject data, M07ManagedGraphAsset graph, bool additive)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject instance = PrefabUtility.InstantiatePrefab(prefab, scene) as GameObject;
            Require(instance != null, "Could not instantiate the M07 scene prefab.");
            instance.name = additive ? "M07 Additive Prefab Instance" : "M07 Business Prefab Instance";
            var sceneRoot = new GameObject(additive ? "M07 Additive Scene Root" : "M07 Business Scene Root");
            SceneManager.MoveGameObjectToScene(sceneRoot, scene);
            var sceneOnly = sceneRoot.AddComponent<M07SceneOnlyComponent>();
            var serialized = new SerializedObject(sceneOnly);
            serialized.FindProperty("sceneValue").intValue = additive ? 708 : 707;
            serialized.FindProperty("dataReference").objectReferenceValue = data;
            serialized.FindProperty("graphReference").objectReferenceValue = graph;
            serialized.FindProperty("serializedInterfaceObject").objectReferenceValue = instance.GetComponent<VersionedPrefabComponent>();
            serialized.ApplyModifiedPropertiesWithoutUndo();
            FieldInfo eventField = typeof(M07SceneOnlyComponent).GetField("persistentEvent", BindingFlags.Instance | BindingFlags.NonPublic);
            var persistent = eventField == null ? null : eventField.GetValue(sceneOnly) as UnityEvent;
            Require(persistent != null, "M07 scene UnityEvent field is unavailable.");
            UnityEventTools.AddPersistentListener(persistent, sceneOnly.OnM07UnityEvent);
            EditorUtility.SetDirty(sceneOnly);
            Require(EditorSceneManager.SaveScene(scene, path), "Could not save M07 scene: " + path);
        }

        private static void EnsureMonoScriptCarrier(string path)
        {
            var carrier = AssetDatabase.LoadAssetAtPath<M07MonoScriptCarrier>(path);
            if (carrier == null)
            {
                carrier = ScriptableObject.CreateInstance<M07MonoScriptCarrier>();
                AssetDatabase.CreateAsset(carrier, path);
            }
            carrier.name = "M07 MonoScript Carrier";
            MonoScript script = AssetDatabase.LoadAssetAtPath<MonoScript>("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs");
            Require(script != null && script.GetClass() == typeof(VersionedPrefabComponent), "M07 MonoScript carrier target is not the exact component script.");
            var serialized = new SerializedObject(carrier);
            serialized.FindProperty("script").objectReferenceValue = script;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(carrier);
        }

        private static void ConfigureVersioned(VersionedPrefabComponent component, VersionedScriptableObject data, Object objectReference, bool structural)
        {
            var serialized = new SerializedObject(component);
            SetDemoValue(serialized.FindProperty("value"), 1234, "M07-PREFAB");
            serialized.FindProperty("dataReference").objectReferenceValue = data;
            serialized.FindProperty("m07SerializedInt").intValue = 701;
            serialized.FindProperty("m07SerializedString").stringValue = "M07-BASELINE-TEXT";
            SetInlineValue(serialized.FindProperty("m07InlineValue"), 71, "M07-INLINE");
            SetInlineArray(serialized.FindProperty("m07InlineValues"), new[] { 72, 73 }, "M07-LIST-");
            serialized.FindProperty("m07ObjectReference").objectReferenceValue = objectReference == null ? data : objectReference;
            SerializedProperty nested = serialized.FindProperty("m07NestedPayload");
            nested.FindPropertyRelative("number").intValue = 74;
            nested.FindPropertyRelative("text").stringValue = "M07-NESTED";
            SerializedProperty added = serialized.FindProperty("addedSerializedField");
            Require(structural ? added != null : added == null, "M07 P05 serialized field visibility differs from the Editor domain.");
            if (added != null) added.intValue = 705;
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetDemoValue(SerializedProperty property, int number, string text)
        {
            Require(property != null, "Missing DemoValue property.");
            property.FindPropertyRelative("number").intValue = number;
            property.FindPropertyRelative("text").stringValue = text;
        }

        private static void SetInlineValue(SerializedProperty property, int number, string text)
        {
            Require(property != null, "Missing M07InlineValue property.");
            property.FindPropertyRelative("number").intValue = number;
            property.FindPropertyRelative("text").stringValue = text;
        }

        private static void SetInlineArray(SerializedProperty property, int[] numbers, string prefix)
        {
            Require(property != null && property.isArray, "Missing M07 inline-value list.");
            property.arraySize = numbers.Length;
            for (int index = 0; index < numbers.Length; ++index)
                SetInlineValue(property.GetArrayElementAtIndex(index), numbers[index], prefix + numbers[index]);
        }

        private static void Validate(string root, bool structural, ShadowResourceBuildMap map)
        {
            Require(map.bundles.Length == 7 && map.bundles.Select(item => item.name).Distinct(StringComparer.Ordinal).Count() == 7,
                "M07 requires exactly seven uniquely named bundles.");
            foreach (string path in map.bundles.SelectMany(item => item.assets))
                Require(File.Exists(path) && File.Exists(path + ".meta") && !string.IsNullOrEmpty(AssetDatabase.AssetPathToGUID(path)), "M07 source asset is not imported: " + path);

            string dataPath = root + "/VersionedData.asset";
            string graphPath = root + "/ManagedGraph.asset";
            string nestedPath = root + "/NestedPrefab.prefab";
            string mixedPath = root + "/MixedAssets.prefab";
            string monoScriptPath = root + "/MonoScriptCarrier.asset";

            var data = AssetDatabase.LoadAssetAtPath<VersionedScriptableObject>(dataPath);
            string dataMarker = structural ? "M07-P05-DATA" : "M07-BASELINE-DATA";
            Require(data != null && data.name == "M07 Versioned Data" && data.ReadSerializedNumber() == 5678 && data.ReadSerializedText() == "M07-DATA" &&
                data.ReadM07State() == "81:M07-INLINE-DATA|82:M07-DATA-LIST-82,83:M07-DATA-LIST-83|" + dataMarker,
                "M07 versioned data did not retain its exact serialized values.");

            var graph = AssetDatabase.LoadAssetAtPath<M07ManagedGraphAsset>(graphPath);
            string graphDescription = structural ? "NODE-A|M07-P05-NODE|NODE-B|M07-P05" : "NODE-A|M07-BASELINE-NODE|NODE-B|M07-BASELINE";
            Require(graph != null && graph.name == "M07 Managed Graph" && graph.SumGraph() == 77 && graph.DescribeGraph() == graphDescription &&
                graph.ConcreteTypeName().StartsWith("AssemblyA.Implementation.Internal.M07NodeA, AssemblyA.Implementation.Internal", StringComparison.Ordinal),
                "M07 SerializeReference graph did not retain the baseline concrete type or values.");

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(root + "/VersionedPrefab.prefab");
            var component = prefab == null ? null : prefab.GetComponent<VersionedPrefabComponent>();
            Require(prefab != null && prefab.name == "VersionedPrefab" && component != null && component.ReadSerializedNumber() == 1234 && component.ReadSerializedText() == "M07-PREFAB" && component.ReadDataReferenceName() == "M07 Versioned Data" && component.ReadM07SerializedState() ==
                "701|M07-BASELINE-TEXT|71:M07-INLINE|72:M07-LIST-72,73:M07-LIST-73|M07 Versioned Data|74:M07-NESTED" &&
                component.ReadM07AddedSerializedField() == (structural ? 705 : -1), "M07 versioned prefab did not freeze its exact serialized values.");

            var nested = AssetDatabase.LoadAssetAtPath<GameObject>(nestedPath);
            var nestedComponent = nested == null ? null : nested.GetComponent<VersionedPrefabComponent>();
            var external = nested == null ? null : nested.GetComponentInChildren<DerivedExternalComponent>(true);
            Require(nested != null && nested.name == "NestedPrefab" && nestedComponent != null && nestedComponent.ReadM07SerializedState() ==
                "701|M07-BASELINE-TEXT|71:M07-INLINE|72:M07-LIST-72,73:M07-LIST-73|M07 Nested Child|74:M07-NESTED" &&
                external != null && external.ReadM07NestedState() == "M07-NESTED-EXTERNAL|AssemblyA.Implementation.Internal.VersionedPrefabComponent|M07-BASELINE-CONSUMER",
                "M07 nested prefab did not retain its cross-component references and values.");

            var mixed = AssetDatabase.LoadAssetAtPath<GameObject>(mixedPath);
            var mixedComponent = mixed == null ? null : mixed.GetComponent<VersionedPrefabComponent>();
            var renameProbe = mixed == null ? null : mixed.GetComponent<M07RenameProbeComponent>();
            Require(mixed != null && mixed.name == "MixedAssets" && mixedComponent != null && mixedComponent.ReadM07SerializedState() ==
                "701|M07-BASELINE-TEXT|71:M07-INLINE|72:M07-LIST-72,73:M07-LIST-73|M07 Versioned Data|74:M07-NESTED" &&
                renameProbe != null && renameProbe.ReadValue() == 714,
                "M07 mixed prefab did not retain its component domain shape and values.");

            var carrier = AssetDatabase.LoadAssetAtPath<M07MonoScriptCarrier>(monoScriptPath);
            MonoScript script = AssetDatabase.LoadAssetAtPath<MonoScript>("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/VersionedPrefabComponent.cs");
            Require(carrier != null && carrier.name == "M07 MonoScript Carrier" && script != null && script.GetClass() == typeof(VersionedPrefabComponent) && carrier.Script == script,
                "M07 MonoScript carrier does not retain the exact component script object.");

            ValidateScene(root + "/BusinessScene.unity", 707, dataPath, graphPath);
            ValidateScene(root + "/AdditiveScene.unity", 708, dataPath, graphPath);
        }

        private static void ValidateScene(string path, int expectedValue, string dataPath, string graphPath)
        {
            Require(AssetDatabase.LoadAssetAtPath<SceneAsset>(path) != null, "M07 scene is not imported: " + path);
            string yaml = File.ReadAllText(path);
            string dataGuid = AssetDatabase.AssetPathToGUID(dataPath);
            string graphGuid = AssetDatabase.AssetPathToGUID(graphPath);
            string sceneScriptGuid = AssetDatabase.AssetPathToGUID("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M07SceneOnlyComponent.cs");
            Require(ValidateSceneContent(yaml, expectedValue, dataGuid, graphGuid, sceneScriptGuid),
                "M07 scene did not retain its exact serialized values and persistent event shape: " + path);
        }

        /// <summary>Validates scene YAML without opening or importing the scene.</summary>
        internal static bool ValidateSceneContent(string yaml, int expectedValue, string dataGuid, string graphGuid, string sceneScriptGuid)
        {
            if (yaml == null || dataGuid == null || graphGuid == null || sceneScriptGuid == null)
                return false;
            string expected = expectedValue.ToString(CultureInfo.InvariantCulture);
            return HasExactScalar(yaml, "sceneValue", expected) &&
                yaml.Contains("dataReference: {fileID: 11400000, guid: " + dataGuid + ", type: 2}") &&
                yaml.Contains("graphReference: {fileID: 11400000, guid: " + graphGuid + ", type: 2}") &&
                HasReferencedSceneRecord(yaml, "serializedInterfaceObject") &&
                yaml.Contains("m_Script: {fileID: 11500000, guid: " + sceneScriptGuid + ", type: 3}") &&
                HasReferencedSceneRecord(yaml, "m_Target") &&
                yaml.Contains("m_TargetAssemblyTypeName: AssemblyA.Implementation.Internal.M07SceneOnlyComponent,") &&
                yaml.Contains("m_MethodName: OnM07UnityEvent");
        }

        private static bool HasExactScalar(string yaml, string field, string expected)
        {
            string prefix = field + ":";
            foreach (string line in yaml.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = line.Trim();
                if (trimmed.StartsWith(prefix, StringComparison.Ordinal))
                    return trimmed.Substring(prefix.Length).Trim() == expected;
            }
            return false;
        }

        private static bool HasReferencedSceneRecord(string yaml, string field)
        {
            string prefix = field + ": {fileID: ";
            foreach (string line in yaml.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = line.Trim();
                if (trimmed.StartsWith("- ", StringComparison.Ordinal))
                    trimmed = trimmed.Substring(2).TrimStart();
                if (!trimmed.StartsWith(prefix, StringComparison.Ordinal))
                    continue;
                int end = trimmed.IndexOf('}', prefix.Length);
                if (end <= prefix.Length)
                    return false;
                string fileId = trimmed.Substring(prefix.Length, end - prefix.Length).Trim();
                if (fileId == "0" || !IsDecimal(fileId))
                    return false;
                return HasSceneRecord(yaml, fileId);
            }
            return false;
        }

        private static bool HasSceneRecord(string yaml, string fileId)
        {
            string marker = "&" + fileId;
            foreach (string line in yaml.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = line.Trim();
                if (!trimmed.StartsWith("--- !u!", StringComparison.Ordinal))
                    continue;
                string[] tokens = trimmed.Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                if (tokens.Contains(marker, StringComparer.Ordinal))
                    return true;
            }
            return false;
        }

        private static bool IsDecimal(string value)
        {
            if (value.Length == 0)
                return false;
            for (int index = 0; index < value.Length; ++index)
                if (value[index] < '0' || value[index] > '9')
                    return false;
            return true;
        }

        private static ShadowBundleDefinition Bundle(string name, params string[] assets)
        {
            return new ShadowBundleDefinition { name = name, assets = assets };
        }

        private static void EnsureFolder(string path)
        {
            string current = "Assets";
            foreach (string segment in path.Split('/').Skip(1))
            {
                string child = current + "/" + segment;
                if (!AssetDatabase.IsValidFolder(child)) Require(!string.IsNullOrEmpty(AssetDatabase.CreateFolder(current, segment)), "Could not create asset folder: " + child);
                current = child;
            }
        }

        private static void Require(bool value, string message)
        {
            if (!value) throw new InvalidOperationException(message);
        }
    }
}
