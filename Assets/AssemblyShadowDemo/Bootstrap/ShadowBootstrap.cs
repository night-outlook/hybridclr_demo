using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HybridCLR;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace AssemblyShadowDemo
{
    // This fixed AOT bootstrap never has a compile-time reference to a business type.
    public sealed class ShadowBootstrap : MonoBehaviour
    {
        public const string InternalAssembly = "AssemblyA.Implementation.Internal";
        private const string ComponentName = "AssemblyA.Implementation.Internal.VersionedPrefabComponent";
        private const string EntryName = "AssemblyA.Implementation.Internal.InternalEntry";
        private ShadowDemoResult result;
        private ShadowPatchFileProvider files;
        private AssetBundle dataBundle;
        private AssetBundle prefabBundle;
        private AssetBundle sceneBundle;
        private GameObject prefab;
        private ScriptableObject data;
        private Component earlyObject;
        private BaselineUse earlyUse;
        private bool patch;

        private IEnumerator Start()
        {
            result = new ShadowDemoResult
            {
                mode = ShadowPatchFileProvider.Argument("-shadowMode", "P01"),
                unityVersion = Application.unityVersion,
                platform = Application.platform.ToString(),
#if ENABLE_IL2CPP && !UNITY_EDITOR
                il2cpp = true,
#endif
            };
            var test = Run();
            while (true)
            {
                bool more;
                object current = null;
                try { more = test.MoveNext(); if (more) current = test.Current; }
                catch (Exception error) { result.error = error.ToString(); Debug.LogException(error); break; }
                if (!more) break;
                yield return current;
            }
            string diagnostics = "{}";
            try
            {
                diagnostics = RuntimeApi.GetAssemblyShadowPrototypeDiagnostics();
                var native = JsonUtility.FromJson<NativeDiagnostics>(diagnostics);
                result.nativeFeatureEnabled = native.enabled;
                result.assemblyResolution.resourceNativeTraceObserved = native.events != null && native.events.Any(item =>
                    (item.phase == "prefab" || item.phase == "scene-first" || item.phase == "scene-reload") &&
                    item.type == ComponentName && item.site != "InspectObject.physical-header");
                result.assemblyResolution.objectNew = native.events != null && native.events.Any(item =>
                    item.type == ComponentName && item.site == "Object::New.input" && item.isInterpreter)
                    ? "shadow" : "no shadow Object::New observed";
                if (result.result == "Passed")
                {
                    if (result.mode == "Baseline") result.gate = "BASELINE-PASS";
                    else if (result.mode != "P01") result.gate = "NEGATIVE-TIMING-OBSERVED";
                    else
                    {
                        result.gate = result.assemblyResolution.resourceNativeTraceObserved ? "CONDITIONAL-GO" : "UNDETERMINED";
                        result.gateNotes = "P01 fixture only: activate before business use; cached Unity query targets are mapped, " +
                            "but general type/cast/reflection cache coherence and Usage Guard remain M03-M07 work.";
                    }
                }
            }
            catch (Exception error) { result.result = "Failed"; result.error += "\nDiagnostics: " + error; }
            try { ShadowDemoResultWriter.Write(result, diagnostics); }
            catch (Exception error) { Debug.LogException(error); Application.Quit(2); yield break; }
            Application.Quit(result.result == "Passed" ? 0 : 1);
        }

        private IEnumerator Run()
        {
            Require(result.il2cpp, "M01 acceptance requires a real IL2CPP Player.");
            Require(new[] { "Baseline", "P01", "PreUseType", "PreUseReflection", "PreUsePrefab", "PreUseScene" }
                .Contains(result.mode), "Unknown M01 mode.");
            patch = result.mode != "Baseline";
            Require(JsonUtility.FromJson<NativeDiagnostics>(RuntimeApi.GetAssemblyShadowPrototypeDiagnostics()).enabled,
                "M01 native feature is disabled; use M00 for OFF regression.");
            files = new ShadowPatchFileProvider();
            result.baselineBuildId = files.Baseline.baselineBuildId;
            result.baselineManifestSha256 = files.BaselineManifestHash;
            result.baselineBundleSha256 = files.Baseline.bundles;
            Phase("bootstrap-before-use");

            if (result.mode == "PreUseType" || result.mode == "PreUseReflection")
            {
                Phase("negative-pre-use-type");
                Type type = result.mode == "PreUseType" ? Type.GetType(EntryName + ", " + InternalAssembly, true)
                    : Assembly.Load(InternalAssembly).GetType(EntryName, true);
                earlyUse = new BaselineUse { kind = result.mode, type = type.FullName, assemblyBefore = Inspect(type.Assembly) };
                result.baselineUsesBeforeActivate = new[] { earlyUse };
            }
            if (result.mode == "PreUsePrefab" || result.mode == "PreUseScene")
            {
                Phase("negative-pre-use-resources");
                LoadDataAndPrefab();
                var instance = Instantiate(prefab);
                earlyObject = FindComponent(instance);
                earlyUse = new BaselineUse { kind = result.mode, type = ComponentName, objectBefore = Inspect(earlyObject) };
                result.baselineUsesBeforeActivate = new[] { earlyUse };
                if (result.mode == "PreUseScene")
                {
                    LoadSceneBundle();
                    yield return SceneManager.LoadSceneAsync(ScenePath(), LoadSceneMode.Additive);
                    // Record a real scene object as the pre-activation witness too.
                    earlyObject = FindSceneComponent();
                    earlyUse.objectBefore = Inspect(earlyObject);
                }
            }

            if (patch)
            {
                Phase("stage");
                var manifest = files.ReadPatch(out byte[] dll, out byte[] pdb);
                result.patchDllSha256 = manifest.patchDllSha256;
                result.baselineMvid = manifest.baselineMvid;
                result.patchMvid = manifest.patchMvid;
                Assembly staged = RuntimeApi.LoadAssemblyShadowPrototype(dll, pdb);
                var stagedInfo = Inspect(staged);
                Require(stagedInfo.isInterpreter && stagedInfo.matchesShadow, "Stage did not create a physical interpreter assembly.");
                Phase("activate");
                Require(RuntimeApi.ActivateAssemblyShadowPrototype(InternalAssembly), "Shadow activation failed.");
                if (earlyObject != null)
                {
                    earlyUse.objectAfterActivate = Inspect(earlyObject);
                    earlyUse.resultAfterActivate = InvokeString(earlyObject, "GetCombinedText");
                }
                if (result.mode == "PreUseScene")
                    yield return SceneManager.UnloadSceneAsync(SceneManager.GetSceneByPath(ScenePath()));
            }

            Phase("reflection-before-bundles");
            result.reflection = ProbeReflection();
            result.assemblyResolution.assemblyLoad = result.reflection.assembly.matchesShadow ? "shadow" : "baseline";
            result.assemblyResolution.assemblyGetType = result.reflection.instance.physicalAssembly.matchesShadow ? "shadow" : "baseline";

            Phase("prefab");
            LoadDataAndPrefab();
            result.scriptableObject = ProbeData();
            var prefabInstance = Instantiate(prefab);
            result.prefab = ProbeComponent(prefabInstance, "prefab");
            Destroy(prefabInstance);
            yield return null;

            LoadSceneBundle();
            Phase("scene-first");
            yield return SceneManager.LoadSceneAsync(ScenePath(), LoadSceneMode.Additive);
            result.scene.firstLoad = ProbeComponent(FindSceneComponent().gameObject, "scene-first");
            ProbeDerivedConsumer();
            yield return SceneManager.UnloadSceneAsync(SceneManager.GetSceneByPath(ScenePath()));
            Phase("scene-reload");
            yield return SceneManager.LoadSceneAsync(ScenePath(), LoadSceneMode.Additive);
            result.scene.reload = ProbeComponent(FindSceneComponent().gameObject, "scene-reload");
            yield return SceneManager.UnloadSceneAsync(SceneManager.GetSceneByPath(ScenePath()));
            result.scene.passed = result.scene.firstLoad.passed && result.scene.reload.passed && result.scene.derivedConsumerAot;
            files.VerifyBundles();
            result.originalBundlesUnchanged = true;
            result.result = result.reflection.passed && result.prefab.passed && result.scriptableObject.passed &&
                result.scene.passed ? "Passed" : "Failed";
            // A failing probe is not automatically a NO-GO. The gate needs native
            // investigation and independent review before claiming an engine limit.
            if (result.result != "Passed") result.error = "One or more executable probes failed; inspect physical pointers and native traces.";
            Phase("finished");
            dataBundle.Unload(true);
            prefabBundle.Unload(true);
            sceneBundle.Unload(true);
        }

        private ReflectionProbe ProbeReflection()
        {
            Assembly assembly = Assembly.Load(InternalAssembly);
            Type type = assembly.GetType(EntryName, true);
            object instance = Activator.CreateInstance(type);
            var probe = new ReflectionProbe
            {
                fullName = assembly.FullName,
                // The pinned IL2CPP RuntimeAssembly.GetManifestModuleInternal throws.
                // Read PE MVIDs from the build/patch snapshots, not this unsupported API.
                moduleMvid = string.Empty,
                moduleMvidSupported = false,
                moduleMvidNote = "IL2CPP does not support Assembly.ManifestModule; use the build-time DLL evidence.",
                isDynamic = assembly.IsDynamic,
                typeAssemblyIdentity = type.Assembly == assembly,
                sameNameAssemblyCount = AppDomain.CurrentDomain.GetAssemblies().Count(item => item.GetName().Name == InternalAssembly),
                result = InvokeString(instance, "GetMarker"),
                assembly = Inspect(assembly),
                instance = Inspect(instance),
            };
            probe.passed = probe.result == Marker && probe.typeAssemblyIdentity && PhysicalMatches(probe.instance)
                && probe.assembly.isInterpreter == patch && probe.assembly.matchesShadow == patch;
            return probe;
        }

        private void LoadDataAndPrefab()
        {
            if (dataBundle == null) dataBundle = LoadBundle("versioned-data.bundle");
            if (data == null) data = dataBundle.LoadAsset<ScriptableObject>(dataBundle.GetAllAssetNames().Single());
            Require(data != null, "Old ScriptableObject asset failed to load.");
            if (prefabBundle == null) prefabBundle = LoadBundle("versioned-prefab.bundle");
            if (prefab == null) prefab = prefabBundle.LoadAsset<GameObject>(prefabBundle.GetAllAssetNames().Single());
            Require(prefab != null, "Old Prefab failed to load.");
        }

        private DataProbe ProbeData()
        {
            var probe = new DataProbe { serializedValue = (int)Invoke(data, "ReadSerializedNumber"), result = InvokeString(data, "GetVersionText"), nativeObject = Inspect(data) };
            probe.passed = probe.serializedValue == 5678 && probe.result == "BASELINE-DATA" && PhysicalMatches(probe.nativeObject);
            return probe;
        }

        private ComponentProbe ProbeComponent(GameObject owner, string phase)
        {
            var probe = new ComponentProbe { phase = phase };
            try
            {
                probe.missingScript = owner.GetComponents<Component>().Any(item => item == null);
                Component component = FindComponent(owner);
                Require(component != null, "VersionedPrefabComponent is missing.");
                Type expected = Assembly.Load(InternalAssembly).GetType(ComponentName, true);
                probe.componentAssembly = component.GetType().Assembly.GetName().Name;
                Phase(phase + "-get-by-name");
                Component byName = owner.GetComponent("VersionedPrefabComponent");
                probe.getComponentByNameFound = byName != null;
                if (byName != null) probe.byNameNativeObject = Inspect(byName);
                probe.getComponentByName = byName == component;
                Phase(phase);
                probe.getComponentByType = owner.GetComponent(expected) == component;
                probe.serializedValue = (int)Invoke(component, "ReadSerializedNumber");
                probe.baseSerializedValue = (int)Invoke(component, "ReadBaseSerializedValue");
                probe.result = InvokeString(component, "GetCombinedText");
                probe.nativeObject = Inspect(component);
                probe.dataReference = component.GetType().GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
                    .Any(field => typeof(ScriptableObject).IsAssignableFrom(field.FieldType) && field.GetValue(component) != null);
                probe.passed = !probe.missingScript && probe.getComponentByName && probe.getComponentByType &&
                    probe.serializedValue == 1234 && probe.baseSerializedValue == 7 &&
                    probe.result == "BASELINE-EXT|" + Marker + "|1234" && PhysicalMatches(probe.nativeObject) && probe.dataReference;
            }
            catch (Exception error) { probe.error = error.ToString(); }
            return probe;
        }

        private void LoadSceneBundle() { if (sceneBundle == null) sceneBundle = LoadBundle("business-scene.bundle"); }
        private string ScenePath() => sceneBundle.GetAllScenePaths().Single();
        private Component FindSceneComponent()
        {
            foreach (var root in SceneManager.GetSceneByPath(ScenePath()).GetRootGameObjects())
            {
                var component = FindComponent(root);
                if (component != null) return component;
            }
            throw new InvalidOperationException("Business scene component is missing.");
        }
        private static Component FindComponent(GameObject owner) => owner.GetComponentsInChildren<Component>(true)
            .FirstOrDefault(component => component != null && component.GetType().FullName == ComponentName);

        private void ProbeDerivedConsumer()
        {
            var components = SceneManager.GetSceneByPath(ScenePath()).GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Component>(true));
            Component derived = components.FirstOrDefault(component => component != null && component.GetType().Name == "DerivedExternalComponent");
            Require(derived != null, "Extensibility consumer missing from scene.");
            result.scene.derivedConsumerResult = InvokeString(derived, "GetBaseVersion");
            result.scene.derivedConsumerAot = !Inspect(derived).physicalAssembly.isInterpreter && result.scene.derivedConsumerResult == "BASELINE-EXT";
        }

        private AssetBundle LoadBundle(string name)
        {
            var bundle = AssetBundle.LoadFromFile(files.BundlePath(name));
            Require(bundle != null, "Unable to load immutable bundle: " + name);
            return bundle;
        }
        private string Marker => patch ? "PATCH-P01-INTERNAL" : "BASELINE-INTERNAL";
        private bool PhysicalMatches(NativeObjectInfo info) => info != null && info.physicalAssembly != null &&
            info.physicalAssembly.name == InternalAssembly && info.physicalAssembly.isInterpreter == patch && info.physicalAssembly.matchesShadow == patch;
        private static void Phase(string phase) { RuntimeApi.SetAssemblyShadowPrototypePhase(phase); Debug.Log("[AssemblyShadow M01] Phase=" + phase); }
        private static NativeObjectInfo Inspect(object instance) => JsonUtility.FromJson<NativeObjectInfo>(RuntimeApi.InspectAssemblyShadowPrototypeObject(instance));
        private static NativeAssemblyInfo Inspect(Assembly assembly) => JsonUtility.FromJson<NativeAssemblyInfo>(RuntimeApi.InspectAssemblyShadowPrototypeAssembly(assembly));
        private static object Invoke(object instance, string method) => instance.GetType().GetMethod(method, BindingFlags.Public | BindingFlags.Instance).Invoke(instance, null);
        private static string InvokeString(object instance, string method) => (string)Invoke(instance, method);
        private static void Require(bool condition, string message) => ShadowPatchFileProvider.Require(condition, message);
    }
}
