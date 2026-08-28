using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using HybridCLR;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Scripting;
using Object = UnityEngine.Object;

namespace AssemblyShadowDemo
{
    /// <summary>Observes the frozen M01 assets only after the M05 transaction commits.</summary>
    [Preserve]
    public static class M05ResourceProbe
    {
        private const string Internal = "AssemblyA.Implementation.Internal";
        private const string Contracts = "AssemblyA.Contracts";
        private const string ComponentName = "AssemblyA.Implementation.Internal.VersionedPrefabComponent";
        private const string Marker = "BASELINE-EXT|PATCH-P01-INTERNAL|1234";
        private static readonly string[] BundleNames = { "business-scene.bundle", "versioned-prefab.bundle", "versioned-data.bundle" };

        public static IEnumerator Run(M05TypeProbe.Result result)
        {
            Require(result != null && (result.mode == "T05-08-P01" || result.mode == "T05-08-P03"), "Unexpected resource-probe mode.");
            AssemblyShadowState state;
            Require(AssemblyShadowRuntime.GetState(out state) == AssemblyShadowErrorCode.Success && state == AssemblyShadowState.Committed,
                "Frozen business resources must not load before commit.");
            var context = new Context();
            IEnumerator work = RunCore(result, context);
            try
            {
                // Yield only Unity operations, so the caller can capture every MoveNext failure.
                Exception failure = null;
                while (true)
                {
                    bool moved;
                    try { moved = work.MoveNext(); }
                    catch (Exception error) { failure = error; break; }
                    if (!moved) break;
                    yield return work.Current;
                }
                // An observation can fail after a scene loads. Finish its unload
                // before releasing its bundles, then propagate the original failure.
                if (!string.IsNullOrEmpty(context.ScenePath))
                {
                    Scene scene = SceneManager.GetSceneByPath(context.ScenePath);
                    if (scene.IsValid() && scene.isLoaded)
                    {
                        AsyncOperation unload = SceneManager.UnloadSceneAsync(scene);
                        Require(unload != null, "Could not unload the failed resource scene.");
                        yield return unload;
                        Require(!SceneManager.GetSceneByPath(context.ScenePath).isLoaded, "The failed resource scene remained loaded.");
                    }
                    context.ScenePath = null;
                }
                if (failure != null) throw new InvalidOperationException("Frozen resource observation failed.", failure);
            }
            finally
            {
                var disposable = work as IDisposable;
                if (disposable != null) disposable.Dispose();
                context.Dispose();
            }
        }

        private static IEnumerator RunCore(M05TypeProbe.Result result, Context context)
        {
            string root = Path.GetFullPath(Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01"));
            string manifestPath = Path.Combine(root, "baseline-manifest.json");
            Require(File.Exists(manifestPath), "The Player is missing its frozen M01 manifest.");
            FrozenManifest manifest = JsonUtility.FromJson<FrozenManifest>(File.ReadAllText(manifestPath));
            ValidateManifest(manifest, Application.unityVersion);
            AddCheck(result, "resource-baseline", manifest.baselineBuildId, "M01-Baseline-v1");

            context.DataBundle = LoadBundle(result, root, manifest, "versioned-data.bundle");
            context.Data = context.DataBundle.LoadAsset<ScriptableObject>(AssetName(context.DataBundle, manifest, "scriptableObject"));
            Require(context.Data != null, "The old ScriptableObject did not load.");
            context.PrefabBundle = LoadBundle(result, root, manifest, "versioned-prefab.bundle");
            GameObject prefab = context.PrefabBundle.LoadAsset<GameObject>(AssetName(context.PrefabBundle, manifest, "prefab"));
            Require(prefab != null, "The old Prefab did not load.");
            Component assetComponent = FindComponent(new[] { prefab });
            ObserveType(result, "resource:prefab-asset:component", assetComponent.GetType(), ExpectedComponentType(), Internal, true);
            context.Instance = Object.Instantiate(prefab);
            Require(context.Instance != null, "The old Prefab did not instantiate.");
            ObserveComponent(result, context, manifest, root, "prefab", "versioned-prefab.bundle", "", FindComponent(new[] { context.Instance }));
            Object.Destroy(context.Instance);
            context.Instance = null;
            yield return null;

            context.SceneBundle = LoadBundle(result, root, manifest, "business-scene.bundle");
            string[] scenePaths = context.SceneBundle.GetAllScenePaths();
            Require(scenePaths.Length == 1, "The frozen scene bundle must contain one scene.");
            context.ScenePath = scenePaths[0];
            Require(string.Equals(context.ScenePath, manifest.assets.Single(item => item.kind == "scene").path, StringComparison.OrdinalIgnoreCase),
                "The bundle scene differs from the frozen manifest.");
            Scene existing = SceneManager.GetSceneByPath(context.ScenePath);
            Require(!existing.IsValid() || !existing.isLoaded, "The business scene was already loaded before the resource probe.");

            AsyncOperation load = SceneManager.LoadSceneAsync(context.ScenePath, LoadSceneMode.Additive);
            Require(load != null, "The old business scene did not start loading.");
            yield return load;
            Scene firstScene = RequireLoadedScene(context.ScenePath);
            Component firstComponent = FindComponent(firstScene.GetRootGameObjects());
            int firstId = firstComponent.GetInstanceID();
            ObserveComponent(result, context, manifest, root, "scene-first", "business-scene.bundle", context.ScenePath, firstComponent);
            AsyncOperation unload = SceneManager.UnloadSceneAsync(firstScene);
            Require(unload != null, "The first business scene did not start unloading.");
            yield return unload;
            Require(!SceneManager.GetSceneByPath(context.ScenePath).isLoaded, "The first business scene remained loaded.");

            load = SceneManager.LoadSceneAsync(context.ScenePath, LoadSceneMode.Additive);
            Require(load != null, "The old business scene did not start reloading.");
            yield return load;
            Scene reloadedScene = RequireLoadedScene(context.ScenePath);
            Component reloadedComponent = FindComponent(reloadedScene.GetRootGameObjects());
            int reloadedId = reloadedComponent.GetInstanceID();
            bool sameObject = System.Object.ReferenceEquals(firstComponent, reloadedComponent);
            result.identityObservations.Add(new M05TypeProbe.IdentityObservation {
                operation = "resource:scene-reload:new-component", left = ComponentName + "#" + firstId,
                right = ComponentName + "#" + reloadedId, sameObject = sameObject,
            });
            Require(!sameObject && firstId != 0 && reloadedId != 0 && firstId != reloadedId, "Scene reload did not create a distinct component instance.");
            ObserveComponent(result, context, manifest, root, "scene-reload", "business-scene.bundle", context.ScenePath, reloadedComponent);
            unload = SceneManager.UnloadSceneAsync(reloadedScene);
            Require(unload != null, "The reloaded business scene did not start unloading.");
            yield return unload;
            Require(!SceneManager.GetSceneByPath(context.ScenePath).isLoaded, "The reloaded business scene remained loaded.");
            context.ScenePath = null;
            result.businessMarker = Marker;
        }

        private static void ObserveComponent(M05TypeProbe.Result result, Context context, FrozenManifest manifest, string root,
            string phase, string bundleName, string scenePath, Component component)
        {
            FrozenBundle bundle = manifest.bundles.Single(item => item.name == bundleName);
            var row = new M05TypeProbe.SceneObservation {
                phase = phase, bundleName = bundleName, bundlePath = BundlePath(root, bundle), bundleSha256 = bundle.sha256,
                scenePath = scenePath, componentAssemblyName = "", componentType = "", businessMarker = "", error = "", loaded = component != null,
            };
            result.sceneObservations.Add(row);
            try
            {
                Require(component != null, "The old asset is missing its business component.");
                Type componentType = component.GetType();
                row.componentAssemblyName = componentType.Assembly.GetName().Name;
                row.componentType = componentType.FullName;
                bool componentActive = ObserveType(result, "resource:" + phase + ":component", componentType, ExpectedComponentType(), Internal, true);
                object data = ReadField(component, "dataReference");
                object value = ReadField(component, "value");
                Require(data != null && value != null, "The old serialized object references are missing.");
                row.referenceIdentity = System.Object.ReferenceEquals(data, context.Data);
                bool dataActive = ObserveType(result, "resource:" + phase + ":data", data.GetType(), ExpectedDataType(), Internal, true);
                bool valueActive = ObserveType(result, "resource:" + phase + ":value", value.GetType(), ExpectedValueType(), Contracts, result.patchId == "P03");
                row.serializedValue = (int)Invoke(component, "ReadSerializedNumber");
                row.baseSerializedValue = (int)Invoke(component, "ReadBaseSerializedValue");
                row.dataSerializedValue = (int)Invoke(data, "ReadSerializedNumber");
                row.businessMarker = (string)Invoke(component, "GetCombinedText");
                row.activeType = componentActive && dataActive && valueActive;
                Require(row.componentAssemblyName == Internal && row.componentType == ComponentName && row.activeType && row.referenceIdentity &&
                    row.serializedValue == 1234 && row.baseSerializedValue == 7 && row.dataSerializedValue == 5678 && row.businessMarker == Marker,
                    "The old asset did not preserve its values, reference identity and active type world: " + phase);
            }
            catch (Exception error)
            {
                row.error = error.ToString();
                throw;
            }
        }

        private static bool ObserveType(M05TypeProbe.Result result, string operation, Type actual, Type expected, string assemblyName, bool shadow)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetTypeResolutionInfo(actual, out json);
            Require(code == AssemblyShadowErrorCode.Success, "Resource type diagnostics failed: " + operation + ":" + code);
            AssemblyShadowTypeResolutionInfo info = AssemblyShadowTypeResolutionInfo.Parse(json);
            bool sameType = System.Object.ReferenceEquals(actual, expected);
            result.typeResolutionObservations.Add(new M05TypeProbe.TypeResolutionObservation {
                operation = operation, requested = actual.FullName, rawJson = json, info = info, sameType = sameType,
            });
            Require(sameType && info.isActive && info.logicalAssembly == assemblyName && info.executionModeCode == (shadow ? 1 : 0) &&
                info.physicalImageKind == (shadow ? "Interpreter" : "Aot") && info.containsShadowTypes == shadow,
                "Resource object has a non-active or unexpected physical type: " + operation);
            return sameType && info.isActive;
        }

        // All three are existing baseline types; new patch-only names are not admitted here.
        private static Type ExpectedComponentType() { return Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true); }
        private static Type ExpectedDataType() { return Type.GetType("AssemblyA.Implementation.Internal.VersionedScriptableObject, AssemblyA.Implementation.Internal", true); }
        private static Type ExpectedValueType() { return Type.GetType("AssemblyA.Contracts.DemoValue, AssemblyA.Contracts", true); }

        private static Component FindComponent(IEnumerable<GameObject> roots)
        {
            Component[] components = roots.SelectMany(root => root.GetComponentsInChildren<Component>(true)).ToArray();
            Require(components.All(component => component != null), "The old resource contains a missing script.");
            Component[] found = components.Where(component => component.GetType().FullName == ComponentName).ToArray();
            Require(found.Length == 1, "The old resource must contain exactly one business component.");
            return found[0];
        }

        private static Scene RequireLoadedScene(string path)
        {
            Scene scene = SceneManager.GetSceneByPath(path);
            Require(scene.IsValid() && scene.isLoaded, "The old business scene is not loaded.");
            return scene;
        }

        private static object ReadField(object owner, string name)
        {
            FieldInfo field = owner.GetType().GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            Require(field != null, "Missing frozen serialized field: " + name);
            return field.GetValue(owner);
        }

        private static object Invoke(object owner, string name)
        {
            MethodInfo method = owner.GetType().GetMethod(name, BindingFlags.Public | BindingFlags.Instance);
            Require(method != null && method.GetParameters().Length == 0, "Missing frozen resource method: " + name);
            return method.Invoke(owner, null);
        }

        private static AssetBundle LoadBundle(M05TypeProbe.Result result, string root, FrozenManifest manifest, string name)
        {
            FrozenBundle declared = manifest.bundles.Single(item => item.name == name);
            byte[] bytes = File.ReadAllBytes(BundlePath(root, declared));
            string actual = Hash(bytes);
            AddCheck(result, "resource-bundle:" + name, actual, declared.sha256);
            // Load precisely the bytes that were hashed, not a second file read.
            AssetBundle bundle = AssetBundle.LoadFromMemory(bytes);
            Require(bundle != null, "Could not load the frozen bundle: " + name);
            return bundle;
        }

        private static string AssetName(AssetBundle bundle, FrozenManifest manifest, string kind)
        {
            string[] names = bundle.GetAllAssetNames();
            string expected = manifest.assets.Single(item => item.kind == kind).path;
            Require(names.Length == 1 && string.Equals(names[0], expected, StringComparison.OrdinalIgnoreCase), "The frozen bundle asset inventory differs: " + kind);
            return names[0];
        }

        private static void ValidateManifest(FrozenManifest manifest, string unityVersion)
        {
            Require(manifest != null && manifest.schemaVersion == 1 && manifest.baselineBuildId == "M01-Baseline-v1" &&
                manifest.unityVersion == unityVersion && manifest.target == "StandaloneOSX" && manifest.architecture == "arm64", "Frozen M01 manifest identity mismatch.");
            Require(manifest.bundles != null && manifest.bundles.Length == 3 && manifest.bundles.All(item => item != null) &&
                manifest.bundles.Select(item => item.name).Distinct(StringComparer.Ordinal).Count() == 3 &&
                BundleNames.All(name => manifest.bundles.Any(item => item.name == name)), "Frozen M01 bundle inventory mismatch.");
            foreach (FrozenBundle bundle in manifest.bundles)
                Require(bundle.path == "Bundles/" + bundle.name && IsHash(bundle.sha256), "Unsafe or unbound frozen bundle path: " + bundle.name);
            Require(manifest.assets != null && manifest.assets.Length == 3 && manifest.assets.All(item => item != null) &&
                manifest.assets.Select(item => item.kind).Distinct(StringComparer.Ordinal).Count() == 3 &&
                new[] { "scene", "prefab", "scriptableObject" }.All(kind => manifest.assets.Any(item => item.kind == kind)), "Frozen M01 asset inventory mismatch.");
            foreach (FrozenAsset asset in manifest.assets)
                Require(!string.IsNullOrEmpty(asset.path) && asset.path.StartsWith("Assets/AssemblyShadowDemo/", StringComparison.Ordinal) &&
                    asset.path.IndexOf("..", StringComparison.Ordinal) < 0 && asset.path.IndexOf('\\') < 0, "Unsafe frozen asset path.");
            Require(manifest.assets.Single(item => item.kind == "prefab").serializedNumber == 1234 &&
                manifest.assets.Single(item => item.kind == "scriptableObject").serializedNumber == 5678, "Frozen serialized value declarations differ.");
        }

        private static string BundlePath(string root, FrozenBundle bundle)
        {
            Require(bundle != null && BundleNames.Contains(bundle.name, StringComparer.Ordinal) && bundle.path == "Bundles/" + bundle.name, "Unsafe frozen bundle path.");
            return Path.GetFullPath(Path.Combine(root, bundle.path));
        }

        private static void AddCheck(M05TypeProbe.Result result, string name, string actual, string expected)
        {
            bool equal = string.Equals(actual, expected, StringComparison.Ordinal);
            result.checks.Add(new M05TypeProbe.Check { name = name, actual = actual, expected = expected, actualCode = equal ? 0 : 1, expectedCode = 0 });
            Require(equal, name + " differs from the frozen declaration.");
        }

        private static bool IsHash(string value) { return value != null && value.Length == 64 && value.All(c => c >= '0' && c <= '9' || c >= 'a' && c <= 'f'); }
        private static string Hash(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        private static void Require(bool value, string message) { if (!value) throw new InvalidOperationException(message); }

        private sealed class Context : IDisposable
        {
            public AssetBundle DataBundle, PrefabBundle, SceneBundle;
            public ScriptableObject Data;
            public GameObject Instance;
            public string ScenePath;

            public void Dispose()
            {
                if (Instance != null) Object.Destroy(Instance);
                if (!string.IsNullOrEmpty(ScenePath))
                {
                    Scene scene = SceneManager.GetSceneByPath(ScenePath);
                    // A cancelled coroutine cannot wait here. Leave loaded-scene
                    // resources alive for Player teardown rather than invalidating them.
                    if (scene.IsValid() && scene.isLoaded) return;
                }
                if (SceneBundle != null) SceneBundle.Unload(true);
                if (PrefabBundle != null) PrefabBundle.Unload(true);
                if (DataBundle != null) DataBundle.Unload(true);
            }
        }

        [Serializable, Preserve] public sealed class FrozenManifest
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string baselineBuildId, unityVersion, target, architecture, sourceSnapshotPath;
            [Preserve] public FrozenBundle[] bundles;
            [Preserve] public FrozenAssembly[] assemblies;
            [Preserve] public FrozenAsset[] assets;
        }
        [Serializable, Preserve] public sealed class FrozenBundle { [Preserve] public string name, path, sha256; }
        [Serializable, Preserve] public sealed class FrozenAssembly { [Preserve] public string name, path, sha256, mvid, pdbPath, pdbSha256; }
        [Serializable, Preserve] public sealed class FrozenAsset { [Preserve] public string kind, path, assetGuid, scriptGuid; [Preserve] public int serializedNumber; }
    }
}
