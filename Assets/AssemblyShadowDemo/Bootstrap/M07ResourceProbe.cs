using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HybridCLR;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Scripting;
using Object = UnityEngine.Object;

namespace AssemblyShadowDemo
{
    /// <summary>Exercises every M07 Unity resource/API path after the transaction boundary.</summary>
    [Preserve]
    internal static class M07ResourceProbe
    {
        private const string InternalAssembly = "AssemblyA.Implementation.Internal";
        private const string InternalComponent = "AssemblyA.Implementation.Internal.VersionedPrefabComponent";
        private const string DataType = "AssemblyA.Implementation.Internal.VersionedScriptableObject";
        private const string GraphType = "AssemblyA.Implementation.Internal.M07ManagedGraphAsset";
        private const string NodeType = "AssemblyA.Implementation.Internal.M07NodeA";
        private const string SceneType = "AssemblyA.Implementation.Internal.M07SceneOnlyComponent";
        private const string ExternalType = "AssemblyShadowDemo.Consumers.DerivedExternalComponent";
        private const string RenameType = "AssemblyA.Implementation.Internal.M07RenameProbeComponent";
        private const string UnityPathType = "AssemblyA.Implementation.Internal.M07UnityPathProbe";

        internal static IEnumerator Run(M07Probe.Result result, M07Probe.Input input)
        {
            bool featureOff = result.mode == "T07-14-FeatureOff";
            string expectedMarker = Marker(input.fixture == null ? "Baseline" : input.fixture.patchId);
            string expectedNodeMarker = NodeMarker(input.fixture == null ? "Baseline" : input.fixture.patchId);
            var context = new Context();
            IEnumerator work = RunCore(result, input, context, featureOff, expectedMarker, expectedNodeMarker);
            Exception failure = null;
            try
            {
                while (true)
                {
                    bool moved;
                    try { moved = work.MoveNext(); }
                    catch (Exception error) { failure = error; break; }
                    if (!moved) break;
                    yield return work.Current;
                }
                if (failure != null) throw new InvalidOperationException("M07 Unity resource observation failed.", failure);
            }
            finally
            {
                var disposable = work as IDisposable;
                if (disposable != null) disposable.Dispose();
                context.Dispose();
            }
        }

        private static IEnumerator RunCore(M07Probe.Result result, M07Probe.Input input, Context context, bool featureOff,
            string expectedMarker, string expectedNodeMarker)
        {
            M07Probe.Verify(result, "resource-load-not-started-at-entry", !result.businessResourceLoadStarted,
                result.businessResourceLoadStarted.ToString(), false.ToString());
            if (result.mode == "T07-11-DelayedCatalog-P03")
            {
                yield return null;
                yield return null;
                M07Probe.Verify(result, "delayed-catalog-after-commit", result.commitCompletedBeforeResourceLoad && !result.businessResourceLoadStarted,
                    "commit=" + result.commitCompletedBeforeResourceLoad + ",load=" + result.businessResourceLoadStarted, "commit=True,load=False");
            }
            result.businessResourceLoadStarted = true;

            LoadedBundle dataBundle = Load(result, input, context, "scriptable-object.bundle");
            LoadedBundle versionedBundle = Load(result, input, context, "versioned-prefab.bundle");
            ScriptableObject data = LoadAssetByType<ScriptableObject>(dataBundle.bundle, DataType);
            GameObject prefab = LoadAssetByType<GameObject>(versionedBundle.bundle, "UnityEngine.GameObject");
            Require(data != null && prefab != null, "M07 data or versioned prefab did not load.");
            ObserveType(result, data.GetType(), "data-asset", featureOff);
            Component prefabComponent = FindComponent(prefab, InternalComponent);
            ObserveType(result, prefabComponent.GetType(), "prefab-asset", featureOff);
            result.serializedState = InvokeString(prefabComponent, "ReadM07SerializedState");
            M07Probe.Verify(result, "prefab-serialized-state", result.serializedState ==
                "701|M07-BASELINE-TEXT|71:M07-INLINE|72:M07-LIST-72,73:M07-LIST-73|M07 Versioned Data|74:M07-NESTED",
                result.serializedState, "canonical M07 serialized state");

            result.lifecycleBefore = InvokeStaticString(prefabComponent.GetType(), "ReadM07LifecycleCounts");
            GameObject first = Object.Instantiate(prefab);
            int firstInstanceId = first.GetInstanceID();
            context.instances.Add(first);
            Component firstComponent = FindComponent(first, InternalComponent);
            ObserveComponent(result, "prefab-first", "versioned-prefab.bundle", firstComponent, expectedMarker, featureOff);
            RunShadowUnityApis(result, first, data, expectedMarker, featureOff);
            yield return null;
            result.lifecycleAfter = InvokeStaticString(firstComponent.GetType(), "ReadM07LifecycleCounts");
            RequireLifecycleProgress(result.lifecycleBefore, result.lifecycleAfter, "prefab lifecycle");
            Object.Destroy(first);
            context.instances.Remove(first);
            yield return null;

            // Unload(false) retains the already loaded object. Use it, release it,
            // collect, then reload the same immutable bytes and require active types.
            versionedBundle.bundle.Unload(false);
            versionedBundle.observation.unloaded = true;
            versionedBundle.bundle = null;
            GameObject cachedInstance = Object.Instantiate(prefab);
            context.instances.Add(cachedInstance);
            Component cachedComponent = FindComponent(cachedInstance, InternalComponent);
            ObserveComponent(result, "prefab-cached-after-unload-false", "versioned-prefab.bundle", cachedComponent, expectedMarker, featureOff);
            result.cacheEvents.Add(new M07Probe.CacheObservation { operation = "unload-false-retained-asset", typeName = cachedComponent.GetType().FullName,
                marker = expectedMarker, active = true, distinctInstance = cachedInstance.GetInstanceID() != firstInstanceId });
            int cachedInstanceId = cachedInstance.GetInstanceID();
            Object.Destroy(cachedInstance);
            context.instances.Remove(cachedInstance);
            prefabComponent = null;
            firstComponent = null;
            cachedComponent = null;
            cachedInstance = null;
            prefab = null;
            yield return null;
            AsyncOperation unused = Resources.UnloadUnusedAssets();
            yield return unused;
            GC.Collect();
            GC.WaitForPendingFinalizers();
            versionedBundle = Reload(result, input, context, versionedBundle);
            prefab = LoadAssetByType<GameObject>(versionedBundle.bundle, "UnityEngine.GameObject");
            GameObject reloaded = Object.Instantiate(prefab);
            context.instances.Add(reloaded);
            Component reloadedComponent = FindComponent(reloaded, InternalComponent);
            ObserveComponent(result, "prefab-reloaded-after-gc", "versioned-prefab.bundle", reloadedComponent, expectedMarker, featureOff);
            result.cacheEvents.Add(new M07Probe.CacheObservation { operation = "reload-after-unload-unused-and-gc", typeName = reloadedComponent.GetType().FullName,
                marker = expectedMarker, active = true, distinctInstance = reloaded.GetInstanceID() != cachedInstanceId });

            LoadedBundle graphBundle = Load(result, input, context, "serialize-reference.bundle");
            ScriptableObject graph = LoadAssetByType<ScriptableObject>(graphBundle.bundle, GraphType);
            Require(graph != null, "M07 SerializeReference graph did not load.");
            ObserveType(result, graph.GetType(), "serialize-reference-owner", featureOff);
            result.graphDescription = InvokeString(graph, "DescribeGraph");
            result.graphSum = (int)Invoke(graph, "SumGraph");
            object node = Invoke(graph, "GetNode");
            result.graphType = node == null ? "" : node.GetType().AssemblyQualifiedName;
            ObserveType(result, node.GetType(), "serialize-reference-concrete", featureOff);
            M07Probe.Verify(result, "serialize-reference-graph", result.graphSum == 77 && result.graphDescription ==
                "NODE-A|" + expectedNodeMarker + "|NODE-B|" + expectedMarker && result.graphType.StartsWith("AssemblyA.Implementation.Internal.M07NodeA, " + InternalAssembly, StringComparison.Ordinal),
                result.graphDescription + ":" + result.graphSum + ":" + result.graphType, "active NodeA->NodeB graph");

            LoadedBundle nestedBundle = Load(result, input, context, "nested-prefab.bundle");
            GameObject nestedPrefab = LoadAssetByType<GameObject>(nestedBundle.bundle, "UnityEngine.GameObject");
            GameObject nested = Object.Instantiate(nestedPrefab);
            context.instances.Add(nested);
            Component nestedInternal = FindComponent(nested, InternalComponent);
            Component external = FindComponent(nested, ExternalType);
            ObserveType(result, nestedInternal.GetType(), "nested-internal", featureOff);
            ObserveType(result, external.GetType(), "nested-external", featureOff);
            string nestedState = InvokeString(external, "ReadM07NestedState");
            string genericExternal = InvokeString(external, "RunM07GenericComponentApis", external.gameObject);
            M07Probe.Verify(result, "nested-cross-reference", nestedState.Contains("|" + InternalComponent + "|") && genericExternal.StartsWith("True|True|True|", StringComparison.Ordinal),
                nestedState + ":" + genericExternal, "serialized cross-reference and consumer generic APIs");

            LoadedBundle mixedBundle = Load(result, input, context, "mixed-assets.bundle");
            GameObject mixedPrefab = mixedBundle.bundle.GetAllAssetNames().Select(name => mixedBundle.bundle.LoadAsset<GameObject>(name)).FirstOrDefault(value => value != null);
            M07MonoScriptCarrier carrier = mixedBundle.bundle.GetAllAssetNames().Select(name => mixedBundle.bundle.LoadAsset<M07MonoScriptCarrier>(name)).FirstOrDefault(value => value != null);
            Require(mixedPrefab != null && carrier != null, "M07 mixed assets or MonoScript carrier did not load.");
            Component rename = FindComponent(mixedPrefab, RenameType);
            ObserveType(result, rename.GetType(), "mixed-rename-guard", featureOff);
            string monoScriptEvidence;
            Type scriptClass = ResolveMonoScriptType(carrier, mixedPrefab, out monoScriptEvidence);
            M07Probe.Verify(result, "monoscript-evidence-policy", IsMonoScriptEvidenceAllowed(monoScriptEvidence), monoScriptEvidence,
                "direct-or-plan-permitted-runtime-component-helper");
            ObserveType(result, scriptClass, "monoscript-get-class", featureOff);
            result.monoScriptClass = scriptClass.FullName;
            result.monoScriptAssembly = scriptClass.Assembly.GetName().Name;
            M07Probe.Verify(result, "monoscript-logical-identity", result.monoScriptClass == InternalComponent && result.monoScriptAssembly == InternalAssembly,
                result.monoScriptAssembly + ":" + result.monoScriptClass, InternalAssembly + ":" + InternalComponent);

            int firstMixedBundleId = mixedBundle.instanceId;
            mixedBundle.bundle.Unload(true);
            mixedBundle.observation.unloaded = true;
            mixedBundle.bundle = null;
            mixedPrefab = null;
            carrier = null;
            rename = null;
            scriptClass = null;
            yield return null;
            mixedBundle = Reload(result, input, context, mixedBundle);
            mixedPrefab = mixedBundle.bundle.GetAllAssetNames().Select(name => mixedBundle.bundle.LoadAsset<GameObject>(name)).FirstOrDefault(value => value != null);
            carrier = mixedBundle.bundle.GetAllAssetNames().Select(name => mixedBundle.bundle.LoadAsset<M07MonoScriptCarrier>(name)).FirstOrDefault(value => value != null);
            Require(mixedPrefab != null && carrier != null && mixedBundle.instanceId != firstMixedBundleId,
                "M07 mixed bundle did not reload after Unload(true).");
            rename = FindComponent(mixedPrefab, RenameType);
            ObserveType(result, rename.GetType(), "mixed-reload-after-unload-true", featureOff);
            string reloadedMonoScriptEvidence;
            scriptClass = ResolveMonoScriptType(carrier, mixedPrefab, out reloadedMonoScriptEvidence);
            M07Probe.Verify(result, "monoscript-active-after-unload-true", reloadedMonoScriptEvidence == monoScriptEvidence &&
                scriptClass != null && scriptClass.FullName == InternalComponent &&
                scriptClass.Assembly.GetName().Name == InternalAssembly, scriptClass == null ? "null" : scriptClass.AssemblyQualifiedName,
                InternalComponent + ", " + InternalAssembly);

            // ScriptableObject asset, generic/Type/string creation, and clone paths
            // are all exercised inside the shadow-owned M07UnityPathProbe above.
            string dataState = InvokeString(data, "ReadM07State");
            M07Probe.Verify(result, "scriptable-object-state", dataState == "81:M07-INLINE-DATA|82:M07-DATA-LIST-82,83:M07-DATA-LIST-83|" + DataMarker(input.fixture == null ? "Baseline" : input.fixture.patchId),
                dataState, "active ScriptableObject serialized state");

            LoadedBundle businessBundle = Load(result, input, context, "business-scene.bundle");
            LoadedBundle additiveBundle = Load(result, input, context, "additive-scene.bundle");
            string businessPath = SingleScenePath(businessBundle.bundle);
            string additivePath = SingleScenePath(additiveBundle.bundle);
            AsyncOperation single = SceneManager.LoadSceneAsync(businessPath, LoadSceneMode.Single);
            Require(single != null, "M07 business Single scene load did not start.");
            yield return single;
            Scene business = RequireScene(businessPath);
            context.scenePaths.Add(businessPath);
            Component businessSceneComponent = FindSceneComponent(business, SceneType);
            ObserveScene(result, "single", "business-scene.bundle", business, businessSceneComponent, expectedMarker, false, false, featureOff);
            Invoke(businessSceneComponent, "OnBeforeSerialize");
            Invoke(businessSceneComponent, "InvokePersistentEvent");
            Invoke(businessSceneComponent, "InvokeStringPaths");
            businessSceneComponent.SendMessage("OnApplicationPause", true, SendMessageOptions.RequireReceiver);
            businessSceneComponent.SendMessage("OnApplicationPause", false, SendMessageOptions.RequireReceiver);
            yield return null;
            result.sceneLifecycleAfter = InvokeStaticString(businessSceneComponent.GetType(), "ReadCounters");
            RequireSceneCounters(result.sceneLifecycleAfter, expectedMarker);

            var persistent = new GameObject("M07 DontDestroyOnLoad Probe");
            context.instances.Add(persistent);
            Component persistentComponent = persistent.AddComponent(Type.GetType(
                "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true));
            Object.DontDestroyOnLoad(persistent);
            ObserveType(result, persistentComponent.GetType(), "dont-destroy-component", featureOff);

            AsyncOperation delayed = SceneManager.LoadSceneAsync(additivePath, LoadSceneMode.Additive);
            Require(delayed != null, "M07 additive delayed scene load did not start.");
            delayed.allowSceneActivation = false;
            int frames = 0;
            while (delayed.progress < 0.9f && frames++ < 1800) yield return null;
            Require(delayed.progress >= 0.9f && !delayed.isDone, "M07 additive scene did not remain pending before activation.");
            delayed.allowSceneActivation = true;
            yield return delayed;
            Scene additive = RequireScene(additivePath);
            context.scenePaths.Add(additivePath);
            Component additiveComponent = FindSceneComponent(additive, SceneType);
            ObserveScene(result, "additive-delayed", "additive-scene.bundle", additive, additiveComponent, expectedMarker, true, true, featureOff);

            Scene host = SceneManager.CreateScene("M07 Final Host " + Guid.NewGuid().ToString("N"));
            SceneManager.SetActiveScene(host);
            AsyncOperation unloadBusiness = SceneManager.UnloadSceneAsync(business);
            Require(unloadBusiness != null, "M07 business scene unload did not start.");
            yield return unloadBusiness;
            context.scenePaths.Remove(businessPath);
            M07Probe.Verify(result, "dont-destroy-survives-scene-switch", persistent != null && persistentComponent != null,
                (persistent != null && persistentComponent != null).ToString(), true.ToString());

            AsyncOperation repeatLoad = SceneManager.LoadSceneAsync(businessPath, LoadSceneMode.Additive);
            Require(repeatLoad != null, "M07 business scene reload did not start.");
            yield return repeatLoad;
            Scene repeatedScene = RequireScene(businessPath);
            context.scenePaths.Add(businessPath);
            Component repeatedComponent = FindSceneComponent(repeatedScene, SceneType);
            ObserveScene(result, "scene-reload", "business-scene.bundle", repeatedScene, repeatedComponent, expectedMarker, true, false, featureOff);
            AsyncOperation repeatUnload = SceneManager.UnloadSceneAsync(repeatedScene);
            Require(repeatUnload != null, "M07 repeated business scene unload did not start.");
            yield return repeatUnload;
            context.scenePaths.Remove(businessPath);
            AsyncOperation unloadAdditive = SceneManager.UnloadSceneAsync(additive);
            Require(unloadAdditive != null, "M07 additive scene unload did not start.");
            yield return unloadAdditive;
            context.scenePaths.Remove(additivePath);
            Object.Destroy(persistent);
            context.instances.Remove(persistent);
            yield return null;
            string finalSceneCounters = InvokeStaticString(businessSceneComponent.GetType(), "ReadCounters");
            RequireSceneDestroyed(finalSceneCounters, expectedMarker);
            result.scenes.ForEach(item => item.unloaded = item.phase == "single" || item.phase == "additive-delayed" || item.phase == "scene-reload");

            result.p04RuntimeValue = ReadPathInt(result.unityPathJson, "p04RuntimeValue");
            result.p05SerializedValue = ReadPathInt(result.unityPathJson, "p05SerializedValue");
            int expectedP04 = input.fixture != null && input.fixture.patchId == "P04" ? 704 : -1;
            int expectedP05 = input.fixture != null && input.fixture.patchId == "P05" ? 705 : -1;
            M07Probe.Verify(result, "p04-runtime-storage", result.p04RuntimeValue == expectedP04, result.p04RuntimeValue.ToString(), expectedP04.ToString());
            M07Probe.Verify(result, "p05-serialized-storage", result.p05SerializedValue == expectedP05, result.p05SerializedValue.ToString(), expectedP05.ToString());
        }

        private static LoadedBundle Load(M07Probe.Result result, M07Probe.Input input, Context context, string name)
        {
            M07Probe.ResourceBundle claim = input.resources.bundles.Single(item => item.name == name);
            string path = M07Probe.Confined(input.resourceRoot, input.resources.bundleDirectory + "/" + name);
            byte[] bytes = System.IO.File.ReadAllBytes(path);
            Require(M07Probe.Hash(bytes) == claim.sha256, "M07 bundle bytes changed: " + name);
            AssetBundle bundle = AssetBundle.LoadFromMemory(bytes);
            Require(bundle != null, "M07 bundle did not load: " + name);
            var observation = new M07Probe.BundleObservation { name = name, path = path, sha256 = claim.sha256, loaded = true,
                assetCount = bundle.GetAllAssetNames().Length, sceneCount = bundle.GetAllScenePaths().Length };
            result.bundles.Add(observation);
            var loaded = new LoadedBundle { name = name, bundle = bundle, observation = observation };
            loaded.instanceId = bundle.GetInstanceID();
            context.bundles.Add(loaded);
            return loaded;
        }

        private static LoadedBundle Reload(M07Probe.Result result, M07Probe.Input input, Context context, LoadedBundle old)
        {
            LoadedBundle replacement = Load(result, input, context, old.name);
            result.cacheEvents.Add(new M07Probe.CacheObservation { operation = "bundle-reloaded", typeName = old.name, marker = replacement.observation.sha256,
                active = replacement.bundle != null, distinctInstance = old.instanceId != replacement.instanceId });
            return replacement;
        }

        private static T LoadAssetByType<T>(AssetBundle bundle, string typeName) where T : Object
        {
            T[] values = bundle.GetAllAssetNames().Select(bundle.LoadAsset<T>).Where(value => value != null &&
                (typeName == "UnityEngine.GameObject" || value.GetType().FullName == typeName)).ToArray();
            Require(values.Length == 1, "M07 bundle asset type inventory differs: " + typeName + " count=" + values.Length);
            return values[0];
        }

        private static void RunShadowUnityApis(M07Probe.Result result, GameObject root, ScriptableObject data, string expectedMarker, bool featureOff)
        {
            Type probe = Type.GetType(
                "AssemblyA.Implementation.Internal.M07UnityPathProbe, AssemblyA.Implementation.Internal", true);
            ObserveType(result, probe, "unity-path-probe", featureOff);
            MethodInfo run = probe.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
            Require(run != null, "M07 shadow UnityPathProbe.Run is unavailable.");
            string json = run.Invoke(null, new object[] { root, data }) as string;
            PathResult path = JsonUtility.FromJson<PathResult>(json);
            Require(path != null && path.marker == expectedMarker && path.componentType == InternalComponent && path.componentAssembly == InternalAssembly &&
                path.getComponentGeneric.EndsWith(":" + InternalComponent, StringComparison.Ordinal) && path.getComponentType.EndsWith(":" + InternalComponent, StringComparison.Ordinal) &&
                path.tryGetComponent.StartsWith("True:", StringComparison.Ordinal) && path.addComponentGeneric.EndsWith(":" + InternalComponent, StringComparison.Ordinal) &&
                path.addComponentType.EndsWith(":" + InternalComponent, StringComparison.Ordinal) && path.createInstanceGeneric.EndsWith(":" + DataType, StringComparison.Ordinal) &&
                path.createInstanceType.EndsWith(":" + DataType, StringComparison.Ordinal) && path.createInstanceString.EndsWith(":" + DataType, StringComparison.Ordinal) &&
                path.instantiateExisting.EndsWith(":" + DataType, StringComparison.Ordinal) && path.getComponents.StartsWith("1:", StringComparison.Ordinal) &&
                path.getComponentInChildren.EndsWith(":" + InternalComponent, StringComparison.Ordinal) &&
                path.getComponentInParent.EndsWith(":" + InternalComponent, StringComparison.Ordinal) &&
                path.interfaceComponent.EndsWith(":" + InternalComponent, StringComparison.Ordinal) &&
                path.baseComponent.EndsWith(":" + InternalComponent, StringComparison.Ordinal) && path.serializedState == result.serializedState &&
                path.messageMarker == expectedMarker, "M07 generic/Type Unity API result differs.");
            result.unityPathJson = json;
            result.assets.Add(new M07Probe.AssetObservation { phase = "unity-api", bundle = "versioned-prefab.bundle", assetName = root.name,
                typeName = path.componentType, assemblyName = path.componentAssembly, marker = path.marker, serializedState = path.serializedState, active = true, instantiated = true });
        }

        private static void ObserveComponent(M07Probe.Result result, string phase, string bundle, Component component, string expectedMarker, bool featureOff)
        {
            Require(component != null, "M07 component observation is null: " + phase);
            ObserveType(result, component.GetType(), phase, featureOff);
            string marker = InvokeString(component, "M07PatchMarker", true);
            string combined = InvokeString(component, "GetCombinedText");
            string expectedCombined = ExpectedCombined(result.patchId);
            Require(marker == expectedMarker && combined == expectedCombined, "M07 component method dispatch differs: " + phase + ":" + marker + ":" + combined);
            result.assets.Add(new M07Probe.AssetObservation { phase = phase, bundle = bundle, assetName = component.gameObject.name,
                typeName = component.GetType().FullName, assemblyName = component.GetType().Assembly.GetName().Name, marker = marker,
                serializedState = InvokeString(component, "ReadM07SerializedState"), active = true, instantiated = true });
        }

        private static void ObserveScene(M07Probe.Result result, string phase, string bundle, Scene scene, Component component,
            string expectedMarker, bool additive, bool delayed, bool featureOff)
        {
            ObserveType(result, component.GetType(), "scene-" + phase, featureOff);
            string marker = InvokeStaticString(component.GetType(), "Marker");
            Require(marker == SceneMarker(expectedMarker), "M07 scene component marker differs: " + phase + ":" + marker);
            string serialized = InvokeString(component, "ReadSerializedState");
            string expectedSerialized = (bundle == "additive-scene.bundle" ? "708" : "707") +
                "|M07 Versioned Data|M07 Managed Graph|" + InternalComponent;
            Require(serialized == expectedSerialized, "M07 scene serialized state differs: " + phase + ":" + serialized);
            result.scenes.Add(new M07Probe.SceneObservation { phase = phase, bundle = bundle, scenePath = scene.path,
                componentType = component.GetType().FullName, marker = marker, serializedState = serialized,
                lifecycle = InvokeStaticString(component.GetType(), "ReadCounters"),
                loaded = scene.IsValid() && scene.isLoaded, additive = additive, activationDelayed = delayed });
        }

        private static void ObserveType(M07Probe.Result result, Type actual, string phase, bool featureOff)
        {
            Require(actual != null, "M07 type observation is null: " + phase);
            Type repeated = ResolveRepeatedType(actual);
            bool same = object.ReferenceEquals(actual, repeated);
            if (featureOff)
            {
                Require(same, "M07 native-OFF Type identity differs: " + phase);
                result.typeResolutions.Add(new M07Probe.TypeResolutionObservation { phase = phase, typeName = actual.FullName,
                    assemblyName = actual.Assembly.GetName().Name, code = "FeatureDisabled", executionMode = "AotBaseline", sameType = same, active = true, rawJson = "" });
                return;
            }
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetTypeResolutionInfo(actual, out json);
            Require(code == AssemblyShadowErrorCode.Success, "M07 type diagnostics failed: " + phase + ":" + code);
            AssemblyShadowTypeResolutionInfo info = AssemblyShadowTypeResolutionInfo.Parse(json);
            bool expectedShadow = result.stageOrder != null && result.stageOrder.Contains(actual.Assembly.GetName().Name, StringComparer.Ordinal);
            Require(same && info.isActive && info.logicalAssembly == actual.Assembly.GetName().Name &&
                info.executionMode == (expectedShadow ? "InterpreterShadow" : "AotBaseline"),
                "M07 resource type is not the active shadow type: " + phase);
            result.typeResolutions.Add(new M07Probe.TypeResolutionObservation { phase = phase, typeName = actual.FullName,
                assemblyName = actual.Assembly.GetName().Name, code = code.ToString(), executionMode = info.executionMode,
                sameType = same, active = info.isActive, rawJson = json });
        }

        private static Type ResolveRepeatedType(Type actual)
        {
            string name = actual.FullName;
            string assembly = actual.Assembly.GetName().Name;
            if (assembly == InternalAssembly && name == InternalComponent)
                return Type.GetType("AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == DataType)
                return Type.GetType("AssemblyA.Implementation.Internal.VersionedScriptableObject, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == GraphType)
                return Type.GetType("AssemblyA.Implementation.Internal.M07ManagedGraphAsset, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == NodeType)
                return Type.GetType("AssemblyA.Implementation.Internal.M07NodeA, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == SceneType)
                return Type.GetType("AssemblyA.Implementation.Internal.M07SceneOnlyComponent, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == RenameType)
                return Type.GetType("AssemblyA.Implementation.Internal.M07RenameProbeComponent, AssemblyA.Implementation.Internal", true);
            if (assembly == InternalAssembly && name == UnityPathType)
                return Type.GetType("AssemblyA.Implementation.Internal.M07UnityPathProbe, AssemblyA.Implementation.Internal", true);
            if (assembly == "AssemblyShadowDemo.ExtensibilityConsumer" && name == ExternalType)
                return Type.GetType("AssemblyShadowDemo.Consumers.DerivedExternalComponent, AssemblyShadowDemo.ExtensibilityConsumer", true);
            throw new InvalidOperationException("M07 repeated type acquisition is outside the finite contract: " + assembly + ":" + name);
        }

        private static Component FindComponent(GameObject root, string fullName)
        {
            Component[] found = root.GetComponentsInChildren<Component>(true).Where(item => item != null && item.GetType().FullName == fullName).ToArray();
            Require(found.Length == 1, "M07 expected exactly one component: " + fullName + ", found " + found.Length);
            return found[0];
        }

        private static Type ResolveMonoScriptType(M07MonoScriptCarrier carrier, GameObject mixedPrefab, out string evidence)
        {
            // MonoScript.GetClass is Editor-centric. The M07 plan permits the
            // Editor-generated carrier plus its runtime component as Player
            // corroboration when MonoScript or GetClass is not exposed there.
            if (carrier.Script == null)
            {
                evidence = "runtime-component-fallback-script-unavailable";
                return FindComponent(mixedPrefab, InternalComponent).GetType();
            }
            MethodInfo getClass = carrier.Script.GetType().GetMethod("GetClass", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (getClass == null)
            {
                evidence = "runtime-component-fallback-getclass-unavailable";
                return FindComponent(mixedPrefab, InternalComponent).GetType();
            }
            try
            {
                Type resolved = getClass.Invoke(carrier.Script, null) as Type;
                Require(resolved != null, "M07 MonoScript.GetClass returned no type despite being callable.");
                evidence = "direct-monoscript-get-class";
                return resolved;
            }
            catch (TargetInvocationException error)
            {
                if (!(error.InnerException is NotSupportedException) && !(error.InnerException is MissingMethodException)) throw;
                evidence = "runtime-component-fallback-getclass-not-supported";
                return FindComponent(mixedPrefab, InternalComponent).GetType();
            }
            catch (NotSupportedException)
            {
                evidence = "runtime-component-fallback-getclass-not-supported";
                return FindComponent(mixedPrefab, InternalComponent).GetType();
            }
            catch (MissingMethodException)
            {
                evidence = "runtime-component-fallback-getclass-not-supported";
                return FindComponent(mixedPrefab, InternalComponent).GetType();
            }
        }

        private static bool IsMonoScriptEvidenceAllowed(string evidence)
        {
            return evidence == "direct-monoscript-get-class" ||
                evidence == "runtime-component-fallback-script-unavailable" ||
                evidence == "runtime-component-fallback-getclass-unavailable" ||
                evidence == "runtime-component-fallback-getclass-not-supported";
        }

        private static Component FindSceneComponent(Scene scene, string fullName)
        {
            Component[] found = scene.GetRootGameObjects().SelectMany(root => root.GetComponentsInChildren<Component>(true))
                .Where(item => item != null && item.GetType().FullName == fullName).ToArray();
            Require(found.Length == 1, "M07 scene expected exactly one component: " + fullName + ", found " + found.Length);
            return found[0];
        }

        private static string SingleScenePath(AssetBundle bundle)
        {
            string[] paths = bundle.GetAllScenePaths();
            Require(paths.Length == 1, "M07 scene bundle must contain exactly one scene.");
            return paths[0];
        }

        private static Scene RequireScene(string path)
        {
            Scene scene = SceneManager.GetSceneByPath(path);
            Require(scene.IsValid() && scene.isLoaded, "M07 scene is not loaded: " + path);
            return scene;
        }

        private static object Invoke(object owner, string method, params object[] arguments)
        {
            Require(owner != null, "M07 reflection owner is null: " + method);
            Type type = owner as Type ?? owner.GetType();
            BindingFlags flags = BindingFlags.Public | BindingFlags.NonPublic | (owner is Type ? BindingFlags.Static : BindingFlags.Instance);
            MethodInfo[] matches = type.GetMethods(flags).Where(item => item.Name == method && item.GetParameters().Length == arguments.Length).ToArray();
            Require(matches.Length == 1, "M07 reflection method is absent or ambiguous: " + type.FullName + "." + method);
            return matches[0].Invoke(owner is Type ? null : owner, arguments);
        }

        private static string InvokeString(object owner, string method, params object[] arguments)
        {
            object value = Invoke(owner, method, arguments);
            return value == null ? "" : value.ToString();
        }

        private static string InvokeString(object owner, string method, bool staticCall)
        {
            return staticCall ? InvokeStaticString(owner.GetType(), method) : InvokeString(owner, method, new object[0]);
        }

        private static string InvokeStaticString(Type type, string method)
        {
            object value = Invoke(type, method);
            if (value is int[]) return string.Join("|", ((int[])value).Select(item => item.ToString()).ToArray());
            return value == null ? "" : value.ToString();
        }

        private static void RequireLifecycleProgress(string before, string after, string label)
        {
            int[] b = ParseCounters(before, 8);
            int[] a = ParseCounters(after, 8);
            Require(a[0] > b[0] && a[1] > b[1] && a[2] > b[2] && a[3] > b[3] && a[4] > b[4] && a[5] > b[5] &&
                a[6] > b[6] && a[7] > b[7], label + " did not execute every active lifecycle/message path.");
        }

        private static void RequireSceneCounters(string counters, string expectedMarker)
        {
            string[] values = counters.Split('|');
            Require(values.Length == 13 && int.Parse(values[0]) > 0 && int.Parse(values[1]) > 0 && int.Parse(values[2]) > 0 && int.Parse(values[3]) > 0 &&
                int.Parse(values[4]) > 0 && int.Parse(values[5]) > 0 && int.Parse(values[8]) > 0 && int.Parse(values[9]) > 0 &&
                int.Parse(values[10]) > 0 && int.Parse(values[11]) >= 11 && values[12] == SceneMarker(expectedMarker),
                "M07 scene serialization/messages/update/pause counters differ: " + counters);
        }

        private static void RequireSceneDestroyed(string counters, string expectedMarker)
        {
            string[] values = counters.Split('|');
            Require(values.Length == 13 && int.Parse(values[6]) > 0 && int.Parse(values[7]) > 0 && values[12] == SceneMarker(expectedMarker),
                "M07 scene OnDisable/OnDestroy counters differ: " + counters);
        }

        private static int[] ParseCounters(string value, int count)
        {
            string[] parts = value.Split('|');
            Require(parts.Length == count, "M07 lifecycle counter shape differs: " + value);
            return parts.Select(int.Parse).ToArray();
        }

        private static int ReadPathInt(string json, string field)
        {
            PathResult path = JsonUtility.FromJson<PathResult>(json);
            Require(path != null, "M07 Unity path JSON is malformed.");
            return field == "p04RuntimeValue" ? path.p04RuntimeValue : path.p05SerializedValue;
        }

        private static string Marker(string patchId)
        {
            if (patchId == "P05") return "M07-P05";
            if (patchId == "P04") return "M07-P04";
            if (patchId == "P03") return "M07-P03";
            if (patchId == "P01") return "M07-P01";
            return "M07-BASELINE";
        }

        private static string NodeMarker(string patchId)
        {
            string marker = Marker(patchId);
            return marker == "M07-BASELINE" ? "M07-BASELINE-NODE" : marker + "-NODE";
        }

        private static string DataMarker(string patchId)
        {
            string marker = Marker(patchId);
            return marker == "M07-BASELINE" ? "M07-BASELINE-DATA" : marker + "-DATA";
        }

        private static string SceneMarker(string marker)
        {
            return marker == "M07-BASELINE" ? "M07-BASELINE-SCENE" : marker + "-SCENE";
        }

        private static string ExpectedCombined(string patchId)
        {
            if (patchId == "P02") return "PATCH-P02-EXT|BASELINE-INTERNAL|1234";
            if (patchId == "P01" || patchId == "P03" || patchId == "P04") return "BASELINE-EXT|PATCH-P01-INTERNAL|1234";
            return "BASELINE-EXT|BASELINE-INTERNAL|1234";
        }

        private static void Require(bool value, string message) { M07Probe.Require(value, message); }

        private sealed class LoadedBundle
        {
            public string name;
            public AssetBundle bundle;
            public int instanceId;
            public M07Probe.BundleObservation observation;
        }

        private sealed class Context : IDisposable
        {
            public readonly List<LoadedBundle> bundles = new List<LoadedBundle>();
            public readonly List<GameObject> instances = new List<GameObject>();
            public readonly List<string> scenePaths = new List<string>();

            public void Dispose()
            {
                foreach (GameObject value in instances) if (value != null) Object.Destroy(value);
                // A failed coroutine cannot safely block on scene unload. Keep
                // scene-owned bundle objects alive for process teardown.
                if (scenePaths.Any(path => { Scene scene = SceneManager.GetSceneByPath(path); return scene.IsValid() && scene.isLoaded; })) return;
                foreach (LoadedBundle value in bundles.AsEnumerable().Reverse())
                    if (value.bundle != null) { value.bundle.Unload(true); value.observation.unloaded = true; }
            }
        }

        [Serializable, Preserve]
        private sealed class PathResult
        {
            public string marker, componentType, componentAssembly, baseType, baseAssembly, interfaceType, interfaceAssembly;
            public string getComponentGeneric, getComponentType, tryGetComponent, getComponents, getComponentInChildren, getComponentInParent;
            public string interfaceComponent, baseComponent, addComponentGeneric, addComponentType;
            public string createInstanceGeneric, createInstanceType, createInstanceString, instantiateExisting, serializedState, messageMarker;
            public int p04RuntimeValue, p05SerializedValue;
        }
    }
}
