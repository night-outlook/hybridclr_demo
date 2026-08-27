using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.UI;

namespace AssemblyShadowDemo
{
    // Executable evidence for the fixed AOT framework contract. There are no
    // business type tokens or dynamic Type.GetType calls in this bootstrap.
    public static class M02ReflectionBindingProbe
    {
        public const string Mode = "M02ReflectionBindings";
        public const string StagedConfiguration = "AssemblyShadow/M02/reflection-bindings.json";
        private const string GuardPrefix = "__AssemblyShadowReflectionBinding_";
        private const string Candidate = "AssemblyA.Implementation.Internal.VersionedPrefabComponent, AssemblyA.Implementation.Internal";

        [Serializable] private sealed class Configuration
        {
            public int schemaVersion;
            public int transformerVersion;
            public Site[] sites;
        }

        [Serializable] private sealed class Site
        {
            public string id;
            public string assembly;
            public string typeName;
            public string[] allowedTypes;
        }

        [Serializable] public sealed class AllowedResult
        {
            public string input;
            public string type;
            public string assembly;
        }

        [Serializable] public sealed class DeniedResult
        {
            public string name;
            public string input;
            public bool inputWasNull;
            public bool denied;
            public string exceptionType;
            public string message;
            public int assemblyResolveEvents;
        }

        [Serializable] public sealed class ProbeResult
        {
            public int schemaVersion = 1;
            public string milestone = "M02";
            public string mode = Mode;
            public string result = "Failed";
            public bool il2cpp;
            public string unityVersion;
            public string platform;
            public string buildGuid;
            public string playerDataPath;
            public string configurationSha256;
            public string configurationHash;
            public string canvasGuard;
            public string enumGuard;
            public AllowedResult[] allowed = new AllowedResult[0];
            public DeniedResult[] denied = new DeniedResult[0];
            public string error;
        }

        public static int RunAndWrite()
        {
            var result = new ProbeResult
            {
                unityVersion = Application.unityVersion,
                platform = Application.platform.ToString(),
                buildGuid = Application.buildGUID,
                playerDataPath = Application.dataPath,
#if ENABLE_IL2CPP && !UNITY_EDITOR
                il2cpp = true,
#endif
            };
            try { Run(result); result.result = "Passed"; }
            catch (Exception error) { result.error = error.ToString(); Debug.LogException(error); }
            try
            {
                string output = Path.GetFullPath(ShadowPatchFileProvider.Argument("-shadowBindingResult",
                    Path.Combine(Application.persistentDataPath, "AssemblyShadowTests/m02-reflection-bindings.json")));
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                File.WriteAllText(output, JsonUtility.ToJson(result, true));
                Debug.Log("[AssemblyShadow M02] Reflection bindings " + result.result + ": " + output);
            }
            catch (Exception error) { Debug.LogException(error); return 2; }
            return result.result == "Passed" ? 0 : 1;
        }

        private static void Run(ProbeResult result)
        {
            Require(result.il2cpp, "Reflection binding acceptance requires a real IL2CPP Player.");
            byte[] bytes = File.ReadAllBytes(Path.Combine(Application.streamingAssetsPath, StagedConfiguration));
            result.configurationSha256 = ShadowPatchFileProvider.Hash(bytes);
            var configuration = JsonUtility.FromJson<Configuration>(Encoding.UTF8.GetString(bytes));
            Require(configuration != null && configuration.schemaVersion == 1 && configuration.transformerVersion == 1 &&
                configuration.sites != null && configuration.sites.Length == 2, "Unexpected finite binding fixture.");
            Site canvasSite = configuration.sites.Single(site => site.id == "urp-debug-ui-prefab-types");
            Site enumSite = configuration.sites.Single(site => site.id == "urp-serializable-enum-player");
            Require(canvasSite.allowedTypes != null && canvasSite.allowedTypes.Length == 26 &&
                canvasSite.allowedTypes.Distinct(StringComparer.Ordinal).Count() == 26 &&
                enumSite.allowedTypes != null && enumSite.allowedTypes.Length == 0, "Unexpected finite domains.");
            MethodInfo canvasGuard = FindGuard(typeof(DebugUIHandlerCanvas), canvasSite);
            MethodInfo enumGuard = FindGuard(typeof(SerializableEnum), enumSite);
            result.canvasGuard = canvasGuard.Name;
            result.enumGuard = enumGuard.Name;
            result.configurationHash = canvasGuard.Name.Substring(GuardPrefix.Length, 64);
            Require(enumGuard.Name.Substring(GuardPrefix.Length, 64) == result.configurationHash, "Mixed guard configurations.");

            var allowed = new List<AllowedResult>();
            foreach (string input in canvasSite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal))
            {
                var type = (Type)canvasGuard.Invoke(null, new object[] { input });
                string[] identity = input.Split(',');
                Require(type != null && type.FullName == identity[0] && type.Assembly.GetName().Name == identity[1].Trim(),
                    "Allowed lookup changed behavior: " + input);
                allowed.Add(new AllowedResult { input = input, type = type.FullName, assembly = type.Assembly.GetName().Name });
            }
            result.allowed = allowed.ToArray();

            int resolverEvents = 0;
            ResolveEventHandler observeResolve = (sender, args) => { ++resolverEvents; return null; };
            AppDomain.CurrentDomain.AssemblyResolve += observeResolve;
            var denied = new List<DeniedResult>();
            GameObject mutationObject = null;
            try
            {
                var inputs = new[]
                {
                    new KeyValuePair<string, string>("candidate", Candidate),
                    new KeyValuePair<string, string>("generic-provider-escape", "System.Collections.Generic.List`1[[" + Candidate + "]], mscorlib"),
                    new KeyValuePair<string, string>("null", null),
                    new KeyValuePair<string, string>("unqualified", "UnityEngine.Rendering.DebugUI+Value"),
                    new KeyValuePair<string, string>("unknown", "AssemblyShadowUnknown.Type, AssemblyShadowUnknown"),
                    new KeyValuePair<string, string>("mutated-string", canvasSite.allowedTypes[0] + " "),
                };
                foreach (var input in inputs)
                    ExpectDenied(denied, input.Key, input.Value, canvasSite.id, result.configurationHash,
                        () => canvasGuard.Invoke(null, new object[] { input.Value }), () => resolverEvents);

                // Mutate the real public prefab field and invoke the real caller,
                // not just the generated guard. Rebuild must fail at its lookup.
                mutationObject = new GameObject("M02 reflection mutation probe");
                var canvas = mutationObject.AddComponent<DebugUIHandlerCanvas>();
                canvas.enabled = false;
                var bundle = new DebugUIPrefabBundle { type = canvasSite.allowedTypes[0] };
                canvas.prefabs = new List<DebugUIPrefabBundle> { bundle };
                bundle.type = Candidate;
                MethodInfo rebuild = typeof(DebugUIHandlerCanvas).GetMethod("Rebuild", BindingFlags.Instance | BindingFlags.NonPublic);
                Require(rebuild != null, "The actual canvas caller was stripped.");
                ExpectDenied(denied, "runtime-prefab-mutation", bundle.type, canvasSite.id, result.configurationHash,
                    () => rebuild.Invoke(canvas, null), () => resolverEvents);

                var serializedEnum = new SerializableEnum(typeof(DayOfWeek));
                ExpectDenied(denied, "serializable-enum-deny-all", typeof(DayOfWeek).AssemblyQualifiedName, enumSite.id,
                    result.configurationHash, () => { Enum ignored = serializedEnum.value; }, () => resolverEvents);
            }
            finally
            {
                result.denied = denied.ToArray();
                AppDomain.CurrentDomain.AssemblyResolve -= observeResolve;
                if (mutationObject != null) UnityEngine.Object.Destroy(mutationObject);
            }
        }

        private static MethodInfo FindGuard(Type owner, Site site)
        {
            Require(owner.FullName == site.typeName && owner.Assembly.GetName().Name == site.assembly, "Wrong guard consumer.");
            var guards = owner.GetMethods(BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Where(method => method.Name.StartsWith(GuardPrefix, StringComparison.Ordinal)).ToArray();
            Require(guards.Length == 1, "Expected exactly one emitted guard on " + owner.FullName);
            var guard = guards[0];
            string suffix = "_" + ShadowPatchFileProvider.Hash(Encoding.UTF8.GetBytes(site.id));
            Require(guard.IsPrivate && guard.ReturnType == typeof(Type) && guard.GetParameters().Length == 1 &&
                guard.GetParameters()[0].ParameterType == typeof(string) && guard.Name.Length == GuardPrefix.Length + 129 &&
                guard.Name.EndsWith(suffix, StringComparison.Ordinal), "Unexpected guard identity or signature.");
            return guard;
        }

        private static void ExpectDenied(List<DeniedResult> results, string name, string input, string site, string configurationHash,
            Action action, Func<int> resolverEvents)
        {
            int before = resolverEvents();
            Exception failure = null;
            try { action(); }
            catch (TargetInvocationException error) { failure = error.InnerException; }
            catch (Exception error) { failure = error; }
            string expected = "AssemblyShadow reflection denied; configuration=" + configurationHash + "; site=" + site;
            var result = new DeniedResult
            {
                name = name, input = input, inputWasNull = input == null,
                denied = failure is InvalidOperationException && failure.Message == expected,
                exceptionType = failure == null ? "" : failure.GetType().FullName,
                message = failure == null ? "" : failure.Message,
                assemblyResolveEvents = resolverEvents() - before,
            };
            results.Add(result);
            Require(result.denied && result.assemblyResolveEvents == 0, "Undeclared reflection escaped its guard: " + name);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
