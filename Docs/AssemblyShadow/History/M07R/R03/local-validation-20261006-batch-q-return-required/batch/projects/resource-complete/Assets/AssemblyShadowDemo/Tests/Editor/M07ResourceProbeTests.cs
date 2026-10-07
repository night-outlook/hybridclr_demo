using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo;
using dnlib.DotNet;
using dnlib.DotNet.Emit;
using NUnit.Framework;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07ResourceProbeTests
    {
        private const string ProbeSource = "Assets/AssemblyShadowDemo/Bootstrap/M07Probe.cs";
        private const string ResourceSource = "Assets/AssemblyShadowDemo/Bootstrap/M07ResourceProbe.cs";
        private const string RunnerSource = "Assets/AssemblyShadowDemo/Bootstrap/M07BootstrapRunner.cs";

        [Test]
        public void ModesAreTheExactM07AcceptanceInventory()
        {
            string[] expected = {
                "T07-01-Prefab-P01", "T07-02-Nested-P02", "T07-03-FullClosure-P03", "T07-04-UnityApis-P01",
                "T07-05-Scriptable-P03", "T07-06-SceneSingle-P01", "T07-07-SceneAdditive-P03",
                "T07-08-SerializeReference-P03", "T07-09-Messages-P01", "T07-10-Cache-P03",
                "T07-11-DelayedCatalog-P03", "T07-12-P04-NonSerialized", "T07-13-P05-Rebuilt", "T07-14-FeatureOff"
            };
            var field = typeof(M07Probe).GetField("Modes", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(field);
            CollectionAssert.AreEqual(expected, (string[])field.GetValue(null));
            Assert.AreEqual(expected.Length, expected.Distinct(StringComparer.Ordinal).Count());
            string source = File.ReadAllText(ProbeSource);
            foreach (string mode in expected) StringAssert.Contains("\"" + mode + "\"", source);
            foreach (string argument in new[] { "-shadowM07Mode", "-shadowM07Fixtures", "-shadowM07PlayerReceipt", "-shadowM07Result" })
                StringAssert.Contains("\"" + argument + "\"", source);
        }

        [Test]
        public void PublicEvidenceDtosAreSerializableAndExplicitlyPreserved()
        {
            foreach (string name in new[] { "Result", "Check", "StageResult", "Snapshot", "BundleObservation", "AssetObservation",
                "SceneObservation", "TypeResolutionObservation", "CacheObservation", "AssemblyModeObservation" })
            {
                Type nested = typeof(M07Probe).GetNestedType(name, BindingFlags.Public);
                Assert.IsNotNull(nested, name);
                Assert.IsTrue(nested.IsDefined(typeof(SerializableAttribute), false), name);
                Assert.IsTrue(nested.IsDefined(typeof(PreserveAttribute), false), name);
                foreach (FieldInfo field in nested.GetFields(BindingFlags.Public | BindingFlags.Instance))
                    Assert.IsTrue(field.IsDefined(typeof(PreserveAttribute), false), name + "." + field.Name);
            }
            Type result = typeof(M07Probe).GetNestedType("Result", BindingFlags.Public);
            CollectionAssert.IsSubsetOf(new[] { "baselineUseCount", "nativeEventCount", "transactionGeneration", "assemblyModes",
                "commitCompletedBeforeResourceLoad", "resourcePrecheckPassed" }, result.GetFields().Select(field => field.Name).ToArray());
            Assert.IsNotNull(typeof(M07Probe).GetNestedType("SceneObservation", BindingFlags.Public).GetField("serializedState"));
        }

        [Test]
        public void FixedAotBootstrapHasNoBusinessAssemblyReference()
        {
            string[] forbidden = { "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
                "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer" };
            Assert.IsFalse(typeof(M07Probe).Assembly.GetReferencedAssemblies().Any(reference => forbidden.Contains(reference.Name, StringComparer.Ordinal)));
            using (var module = ModuleDefMD.Load(typeof(M07Probe).Assembly.Location))
            {
                Assert.IsFalse(module.GetAssemblyRefs().Any(reference => forbidden.Contains(reference.Name.String, StringComparer.Ordinal)));
                TypeDef probe = module.Find(typeof(M07Probe).FullName, false);
                Assert.IsNotNull(probe);
                Assert.IsFalse(probe.Methods.Where(method => method.HasBody).SelectMany(method => method.Body.Instructions)
                    .Select(instruction => instruction.Operand).OfType<ITypeDefOrRef>()
                    .Any(type => forbidden.Contains(type.DefinitionAssembly == null ? "" : type.DefinitionAssembly.Name.String, StringComparer.Ordinal)));
            }
        }

        [Test]
        public void ResourceLoadCannotBeginBeforeCommitAndPrecheck()
        {
            string probe = File.ReadAllText(ProbeSource), resource = File.ReadAllText(ResourceSource);
            int inputs = probe.IndexOf("ReadInputs(expectedBaselineBuildId, expectedRuntimeAbiHash, mode)", StringComparison.Ordinal);
            int precheck = probe.IndexOf("resourcePrecheckPassed = true", inputs, StringComparison.Ordinal);
            int transaction = probe.IndexOf("RunTransaction(result, input)", precheck, StringComparison.Ordinal);
            int coroutine = probe.IndexOf("M07ResourceProbe.Run(result, input)", transaction, StringComparison.Ordinal);
            Assert.Greater(inputs, 0); Assert.Greater(precheck, inputs); Assert.Greater(transaction, precheck); Assert.Greater(coroutine, transaction);
            int commit = probe.IndexOf("CommitTransaction()", StringComparison.Ordinal);
            int commitFlag = probe.IndexOf("commitCompletedBeforeResourceLoad = !result.businessResourceLoadStarted", commit, StringComparison.Ordinal);
            Assert.Greater(commit, 0); Assert.Greater(commitFlag, commit);
            int entryCheck = resource.IndexOf("resource-load-not-started-at-entry", StringComparison.Ordinal);
            int loadFlag = resource.IndexOf("businessResourceLoadStarted = true", entryCheck, StringComparison.Ordinal);
            int firstLoad = resource.IndexOf("Load(result, input, context", loadFlag, StringComparison.Ordinal);
            Assert.Greater(entryCheck, 0); Assert.Greater(loadFlag, entryCheck); Assert.Greater(firstLoad, loadFlag);
        }

        [Test]
        public void RuntimeExercisesEveryRequiredUnityAndCachePath()
        {
            string source = File.ReadAllText(ResourceSource) + File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M07UnityPathProbe.cs");
            foreach (string token in new[] { "AddComponent<VersionedPrefabComponent>", "AddComponent(resolvedType)",
                "GetComponentInChildren<VersionedPrefabComponent>", "GetComponentInChildren(resolvedType", "TryGetComponent<VersionedPrefabComponent>",
                "GetComponentsInChildren<VersionedPrefabComponent>", "GetComponentInParent<VersionedPrefabComponent>", "GetComponent<IVersionTextProvider>",
                "GetComponent<VersionedComponentBase>", "CreateInstance<VersionedScriptableObject>", "CreateInstance(typeof(VersionedScriptableObject))",
                "CreateInstance(\"AssemblyA.Implementation.Internal.VersionedScriptableObject\")", "Object.Instantiate(existingAsset)",
                "Unload(false)", "Unload(true)", "Resources.UnloadUnusedAssets", "GC.WaitForPendingFinalizers", "allowSceneActivation = false",
                "LoadSceneMode.Single", "LoadSceneMode.Additive", "DontDestroyOnLoad", "InvokePersistentEvent", "InvokeStringPaths",
                "OnBeforeSerialize", "OnApplicationPause", "MonoScript.GetClass" })
                StringAssert.Contains(token, source, token);
            StringAssert.Contains("mixed-reload-after-unload-true", source);
            StringAssert.Contains("prefab-reloaded-after-gc", source);
            StringAssert.Contains("serialize-reference-graph", source);
        }

        [Test]
        public void UnityObjectsCannotBindToABooleanReflectionHelperOverload()
        {
            string source = File.ReadAllText(ResourceSource);
            StringAssert.Contains("InvokeString(external, \"RunM07GenericComponentApis\", external.gameObject)", source);
            StringAssert.Contains("InvokeStaticString(component.GetType(), \"M07PatchMarker\")", source);
            Assert.IsFalse(source.Contains("InvokeString(object owner, string method, bool staticCall)"));
        }

        [Test]
        public void BaselineUseGateRejectsOnlyTheSelectedShadowClosure()
        {
            string source = File.ReadAllText(ProbeSource);
            StringAssert.Contains("final.baselineUses.Count(use =>", source);
            StringAssert.Contains("result.stageOrder.Contains(use.name, StringComparer.Ordinal)", source);
            Assert.IsFalse(source.Contains("baselineUseCount = final.baselineUses.Length"));
        }

        [Test]
        public void MonoScriptEvidenceUsesOnlyThePlanPermittedPlayerFallback()
        {
            string source = File.ReadAllText(ResourceSource);
            StringAssert.Contains("ResolveMonoScriptType(carrier, mixedPrefab", source);
            StringAssert.Contains("monoscript-evidence-policy", source);
            StringAssert.Contains("direct-or-plan-permitted-runtime-component-helper", source);
            foreach (string evidence in new[] { "direct-monoscript-get-class", "runtime-component-fallback-script-unavailable",
                "runtime-component-fallback-getclass-unavailable", "runtime-component-fallback-getclass-not-supported" })
                StringAssert.Contains("\"" + evidence + "\"", source);
            StringAssert.Contains("FindComponent(mixedPrefab, InternalComponent).GetType()", source);
            Assert.IsFalse(source.Contains("carrier != null && carrier.Script != null"));
            StringAssert.Contains("if (!(error.InnerException is NotSupportedException) && !(error.InnerException is MissingMethodException)) throw;", source);
        }

        [Test]
        public void FixedBootstrapTypeAcquisitionIsFiniteAndLiteral()
        {
            string source = File.ReadAllText(ResourceSource);
            foreach (string type in new[] { "VersionedPrefabComponent", "VersionedScriptableObject", "M07ManagedGraphAsset", "M07NodeA",
                "M07SceneOnlyComponent", "M07RenameProbeComponent", "M07UnityPathProbe", "DerivedExternalComponent" })
                StringAssert.Contains("." + type + ", ", source);
            StringAssert.Contains("ResolveRepeatedType(actual)", source);
            StringAssert.Contains("outside the finite contract", source);
            Assert.IsFalse(source.Contains("Type.GetType(actual.FullName"));
            Assert.IsFalse(source.Contains("Type.GetType(InternalComponent +"));
        }

        [Test]
        public void CoroutineFailureRetainsEvidenceAndUsesOwnedProbeCleanup()
        {
            string runner = File.ReadAllText(RunnerSource);
            StringAssert.Contains("CompleteCoroutineFailure(error)", runner);
            StringAssert.Contains("work = null", runner);
            // M07BootstrapLifetimeTests executes the detach/dispose ownership
            // contract, including repeated cleanup and a throwing disposer.
            StringAssert.Contains("ReleaseProbe(ref work)", runner);
            StringAssert.Contains("FileMode.CreateNew", File.ReadAllText(ProbeSource));
        }
    }
}
