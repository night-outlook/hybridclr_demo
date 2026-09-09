using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    [Preserve]
    public static class R01BLazyProbe
    {
        private const string FixtureName = "AssemblyShadow.R01BLazyFixture";
        private const string Prefix = "AssemblyShadow.R01B.";
        private static Result active;
        private static string output;

        public static IEnumerator RunAndWriteCoroutine(string baselineBuildId, string runtimeAbiHash, Action<int> completed)
        {
            completed(RunAndWrite(baselineBuildId, runtimeAbiHash));
            yield break;
        }

        private static int RunAndWrite(string baselineBuildId, string runtimeAbiHash)
        {
            output = Path.GetFullPath(Argument("-shadowR01BLazyResult", Path.Combine(
                Application.persistentDataPath, "AssemblyShadowTests/r01b-lazy.json")));
            active = new Result {
                schemaVersion = 1, kind = "R01BLazyPlayerResult", milestone = "R01B", result = "Failed",
                baselineBuildId = baselineBuildId, runtimeAbiHash = runtimeAbiHash,
                unityVersion = Application.unityVersion, platform = Application.platform.ToString(),
                buildGuid = Application.buildGUID, processId = Process.GetCurrentProcess().Id,
                resultPath = output, il2cpp = IsIl2CppPlayer(), checks = new List<CheckRecord>(),
                capacitySnapshots = new List<CapacitySnapshot>(), retryExceptions = new List<string>()
            };
            try
            {
                Check("il2cpp-player", active.il2cpp, "R01B lazy-path evidence requires an IL2CPP Player.");
                Check("result-path-unused", !File.Exists(output), "The result path must be immutable.");
                string fixturePath = Path.GetFullPath(Argument("-shadowR01BLazyDll", ""));
                Check("fixture-exists", File.Exists(fixturePath), "The R01B lazy fixture DLL is missing.");
                active.fixturePath = fixturePath;
                byte[] bytes = File.ReadAllBytes(fixturePath);
                active.fixtureBytes = bytes.LongLength;
                active.fixtureSha256 = Hash(bytes);
                Snapshot("before-load");

                Assembly assembly = Assembly.Load(bytes);
                active.assemblyFullName = assembly.FullName;
                active.assemblyName = assembly.GetName().Name;
                Check("assembly-identity", active.assemblyName == FixtureName && assembly.GetName().Version.ToString() == "1.0.0.1",
                    "Loaded fixture identity differs: " + assembly.FullName);
                Snapshot("after-load");
                Check("ordinary-image-accounted", ImageDelta(1), "Loading the fixture did not account for exactly one ordinary interpreter image.");

                Find(assembly, "LazyEntry");
                Type boxDefinition = Find(assembly, "LazyBox`1");
                Type boxInt = boxDefinition.MakeGenericType(typeof(int));
                Type boxString = boxDefinition.MakeGenericType(typeof(string));
                Type implementation = Find(assembly, "LazyImplementation");
                Type contractDefinition = Find(assembly, "ILazyContract`1");
                Type contractInt = contractDefinition.MakeGenericType(typeof(int));
                Type inherited = Find(assembly, "IInheritedLazyContract");

                Check("generic-int-method", InvokeInt(boxInt, "Echo", 41) == 41, "Closed generic int method returned the wrong value.");
                Check("generic-string-method", (string)Invoke(boxString, "Echo", "lazy") == "lazy", "Closed generic string method returned the wrong value.");
                Check("generic-type-reflection", InvokeInt(boxInt, "Echo", 42) == 42 && (string)Invoke(boxString, "Echo", "lazy") == "lazy",
                    "Reflection over constructed generic types did not reach the expected methods.");
                Snapshot("after-generics");

                Array values = (Array)Invoke(boxInt, "MakeArray", 9);
                Check("generic-array-method", values.GetType() == typeof(int[]) && (int)values.GetValue(0) == 9,
                    "Generic array construction or indexed read returned the wrong value.");
                Array created = Array.CreateInstance(boxInt, 2);
                created.SetValue(Activator.CreateInstance(boxInt), 0);
                Check("reflection-array", created.GetType().GetElementType() == boxInt && created.GetValue(0).GetType() == boxInt,
                    "Reflection-created constructed-generic array was not addressable.");
                Snapshot("after-arrays");

                Type[] interfaces = implementation.GetInterfaces();
                Check("inherited-interface-enumeration", interfaces.Contains(inherited) && interfaces.Contains(contractInt) && interfaces.Contains(typeof(IDisposable)),
                    "Inherited generic interface enumeration omitted an expected interface.");
                Check("inherited-interface-assignability", contractInt.IsAssignableFrom(implementation),
                    "Inherited generic interface assignability failed.");
                InterfaceMapping map = implementation.GetInterfaceMap(contractInt);
                MethodInfo interfaceEcho = contractInt.GetMethod("Echo");
                object implementationInstance = Activator.CreateInstance(implementation);
                Check("inherited-interface-map", map.InterfaceMethods.Length == 1 && map.TargetMethods.Length == 1 &&
                    map.TargetMethods[0].Name == "Echo" && (int)interfaceEcho.Invoke(implementationInstance, new object[] { 5 }) == 12,
                    "Inherited interface dispatch did not map to LazyImplementation.Echo.");
                InterfaceMapping aotMap = implementation.GetInterfaceMap(typeof(IDisposable));
                Check("inherited-aot-interface", typeof(IDisposable).IsAssignableFrom(implementation) &&
                    aotMap.InterfaceMethods.Length == 1 && aotMap.TargetMethods.Length == 1 &&
                    aotMap.TargetMethods[0].Name == "Dispose",
                    "Inherited native AOT IDisposable interface was not mapped by the interpreted implementation.");
                aotMap.InterfaceMethods[0].Invoke(implementationInstance, null);
                Check("inherited-aot-interface-invoke", true, "Inherited native AOT IDisposable invocation completed.");
                Snapshot("after-interfaces");

                Type carrier = Find(assembly, "LazyAttributeCarrier");
                IList<CustomAttributeData> markerData = carrier.GetCustomAttributesData();
                Check("attribute-data", markerData.Count == 1 && markerData[0].AttributeType.Name == "LazyMarkerAttribute" &&
                    markerData[0].ConstructorArguments.Count == 2 && (string)markerData[0].ConstructorArguments[0].Value == "lazy-marker" &&
                    markerData[0].ConstructorArguments[1].Value is Type,
                    "Valid custom-attribute metadata did not expose its constructor arguments.");
                object[] markerInstances = carrier.GetCustomAttributes(false);
                Check("attribute-conversion", markerInstances.Length == 1 && markerInstances[0].GetType().Name == "LazyMarkerAttribute" &&
                    (string)markerInstances[0].GetType().GetField("Name").GetValue(markerInstances[0]) == "lazy-marker" &&
                    (Type)markerInstances[0].GetType().GetField("PayloadType").GetValue(markerInstances[0]) == boxInt,
                    "Valid custom-attribute conversion did not preserve its constructed Type argument.");
                Snapshot("after-valid-attribute");

                Type retryCarrier = Find(assembly, "LazyRetryCarrier");
                IList<CustomAttributeData> retryData = retryCarrier.GetCustomAttributesData();
                Check("failed-attribute-data", retryData.Count == 1 && retryData[0].AttributeType.Name == "LazyRetryAttribute" &&
                    retryData[0].ConstructorArguments.Count == 1 && (int)retryData[0].ConstructorArguments[0].Value == 7,
                    "Retry attribute metadata was not readable before conversion.");
                for (int attempt = 1; attempt <= 2; ++attempt)
                {
                    Exception failure = null;
                    try { retryCarrier.GetCustomAttributes(false); }
                    catch (Exception error) { failure = error; active.retryExceptions.Add(error.GetType().FullName + ": " + error.Message); }
                    Check("failed-attribute-constructor-retry-" + attempt, failure != null,
                        "The throwing custom-attribute constructor did not fail on retry " + attempt + ".");
                    ++active.failedAttributeAttempts;
                    Snapshot("after-failed-attribute-" + attempt);
                }

                Type malformedCarrier = Find(assembly, "LazyMalformedCarrier");
                Type malformedAttribute = Find(assembly, "LazyMalformedAttribute");
                FieldInfo malformedCalls = malformedAttribute.GetField("ConstructorCalls", BindingFlags.Public | BindingFlags.Static);
                for (int attempt = 1; attempt <= 2; ++attempt)
                {
                    int callsBefore = (int)malformedCalls.GetValue(null);
                    Exception failure = null;
                    try { malformedCarrier.GetCustomAttributes(false); }
                    catch (Exception error) { failure = error; active.retryExceptions.Add("malformed-" + error.GetType().FullName + ": " + error.Message); }
                    int callsAfter = (int)malformedCalls.GetValue(null);
                    Check("malformed-attribute-conversion-retry-" + attempt, failure != null && callsBefore == 0 && callsAfter == 0,
                        "Malformed custom-attribute conversion did not fail before its constructor on retry " + attempt + ".");
                    ++active.malformedAttributeAttempts;
                    active.malformedConstructorCalls = callsAfter;
                    Snapshot("after-malformed-attribute-" + attempt);
                }

                Check("lazy-image-stable", LifetimeImageDelta(1),
                    "Lazy metadata operations unexpectedly created another interpreter image.");
                Check("capacity-pages-monotonic", PagesMonotonic(),
                    "Capacity page accounting moved backwards across lazy operations.");
                RunDenseAdjunctIfRequested();
                active.result = "Passed";
            }
            catch (Exception error)
            {
                active.error = error.ToString();
                UnityEngine.Debug.LogException(error);
            }
            Write(active);
            return active.result == "Passed" ? 0 : 1;
        }

        public static int CompleteCoroutineFailure(Exception error)
        {
            if (active == null) return 2;
            active.result = "Failed";
            active.error = error.ToString();
            try { Write(active); return 1; }
            catch { return 2; }
        }

        private static void RunDenseAdjunctIfRequested()
        {
            string manifestPath = Argument("-shadowR01BDenseManifest", "");
            if (string.IsNullOrWhiteSpace(manifestPath)) return;
            manifestPath = Path.GetFullPath(manifestPath);
            Check("dense-manifest-exists", File.Exists(manifestPath), "The optional dense adjunct manifest is missing.");
            DenseManifest manifest = JsonUtility.FromJson<DenseManifest>(File.ReadAllText(manifestPath));
            Check("dense-manifest-shape", manifest != null && manifest.fixtures != null && manifest.fixtures.Length == 2,
                "The optional dense adjunct manifest does not contain exactly two fixtures.");
            foreach (DenseFixture fixture in manifest.fixtures)
            {
                string path = Path.GetFullPath(fixture.path);
                byte[] bytes = File.ReadAllBytes(path);
                Check("dense-input-" + fixture.id, fixture.id > 0 && fixture.typeDefRows >= 4098 && fixture.methodDefRows >= 4097 &&
                    Hash(bytes) == fixture.sha256, "Dense adjunct hash or metadata envelope differs for fixture " + fixture.id + ".");
                Assembly assembly = Assembly.Load(bytes);
                string stem = "DenseType_" + fixture.id.ToString("D4") + "_";
                string suffix = "_MetadataBoundary_0123456789abcdef0123456789abcdef";
                foreach (int row in new[] { 4095, 4096 })
                {
                    Type type = assembly.GetType("AssemblyShadow.Workload." + stem + row.ToString("D4") + suffix, true);
                    Check("dense-row-" + fixture.id + "-" + row, InvokeInt(type, "ReturnId") == fixture.id,
                        "Dense metadata boundary method returned the wrong identity.");
                }
                ++active.denseFixtures;
                active.denseBoundaryChecks += 2;
            }
            Snapshot("after-dense-adjunct");
        }

        private static int InvokeInt(Type type, string method, params object[] arguments)
        {
            return (int)Invoke(type, method, arguments);
        }

        private static object Invoke(Type type, string method, params object[] arguments)
        {
            MethodInfo info = type.GetMethod(method, BindingFlags.Public | BindingFlags.Static);
            Check("method-present-" + type.FullName + "-" + method + "-" + active.checks.Count, info != null, "Missing fixture method " + type.FullName + "." + method);
            return info.Invoke(null, arguments);
        }

        private static Type Find(Assembly assembly, string name)
        {
            Type type = assembly.GetType(Prefix + name, true);
            Check("type-present-" + name, type != null, "Missing fixture type " + name + ".");
            return type;
        }

        private static void Check(string name, bool passed, string detail)
        {
            active.checks.Add(new CheckRecord { name = name, passed = passed, detail = detail });
            if (!passed) throw new InvalidOperationException(name + ": " + detail);
            ++active.passedChecks;
        }

        private static void Snapshot(string phase)
        {
            string json;
            AssemblyShadowErrorCode code = AssemblyShadowRuntime.GetMetadataCapacityJson(new long[0], out json);
            Check("capacity-query-" + phase, code == AssemblyShadowErrorCode.Success && !string.IsNullOrEmpty(json),
                "Metadata capacity query failed during " + phase + ": " + code);
            AssemblyShadowMetadataCapacityProfile2 value = AssemblyShadowMetadataCapacityProfile2.Parse(json);
            active.capacitySnapshots.Add(new CapacitySnapshot {
                phase = phase, reservedPages = value.reservedPages, mappedPages = value.mappedPages,
                lifetimeReservedImageCount = value.lifetimeReservedImageCount,
                remainingImageCount = value.remainingImageCount, ordinaryAllocatedCount = value.ordinaryAllocatedCount,
                shadowAllocatedCount = value.shadowAllocatedCount, reservedShadowImageCount = value.reservedShadowImageCount,
                aggregateInputDllBytes = value.aggregateInputDllBytes
            });
        }

        private static bool ImageDelta(ulong expected)
        {
            if (active.capacitySnapshots.Count < 2) return false;
            return active.capacitySnapshots[1].lifetimeReservedImageCount == active.capacitySnapshots[0].lifetimeReservedImageCount + expected;
        }

        private static bool LifetimeImageDelta(ulong expected)
        {
            if (!ImageDelta(expected)) return false;
            ulong baseline = active.capacitySnapshots[1].lifetimeReservedImageCount;
            return active.capacitySnapshots.Skip(1).All(item => item.lifetimeReservedImageCount == baseline);
        }

        private static bool PagesMonotonic()
        {
            for (int index = 1; index < active.capacitySnapshots.Count; ++index)
                if (active.capacitySnapshots[index].reservedPages < active.capacitySnapshots[index - 1].reservedPages) return false;
            return true;
        }

        private static void Write(Result result)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            using (var stream = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false)))
                writer.Write(JsonUtility.ToJson(result, true));
        }

        private static string Hash(byte[] bytes)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        private static string Argument(string name, string fallback)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int index = 0; index + 1 < args.Length; ++index)
                if (args[index] == name) return args[index + 1];
            return fallback;
        }

        private static bool IsIl2CppPlayer()
        {
#if ENABLE_IL2CPP && !UNITY_EDITOR
            return true;
#else
            return false;
#endif
        }

        [Serializable, Preserve]
        private sealed class Result
        {
            [Preserve] public int schemaVersion, processId, passedChecks, failedAttributeAttempts, malformedAttributeAttempts,
                malformedConstructorCalls, denseFixtures, denseBoundaryChecks;
            [Preserve] public long fixtureBytes;
            [Preserve] public string kind, milestone, result, error, baselineBuildId, runtimeAbiHash, unityVersion, platform,
                buildGuid, resultPath, fixturePath, fixtureSha256, assemblyName, assemblyFullName;
            [Preserve] public bool il2cpp;
            [Preserve] public List<CheckRecord> checks;
            [Preserve] public List<CapacitySnapshot> capacitySnapshots;
            [Preserve] public List<string> retryExceptions;
        }

        [Serializable, Preserve]
        private sealed class CheckRecord
        {
            [Preserve] public string name, detail;
            [Preserve] public bool passed;
        }

        [Serializable, Preserve]
        private sealed class CapacitySnapshot
        {
            [Preserve] public string phase;
            [Preserve] public ulong reservedPages, mappedPages, lifetimeReservedImageCount, remainingImageCount,
                ordinaryAllocatedCount, shadowAllocatedCount, reservedShadowImageCount, aggregateInputDllBytes;
        }

        [Serializable, Preserve]
        private sealed class DenseManifest
        {
            [Preserve] public DenseFixture[] fixtures;
        }

        [Serializable, Preserve]
        private sealed class DenseFixture
        {
            [Preserve] public int id, typeDefRows, methodDefRows;
            [Preserve] public string path, name, sha256;
        }
    }
}
