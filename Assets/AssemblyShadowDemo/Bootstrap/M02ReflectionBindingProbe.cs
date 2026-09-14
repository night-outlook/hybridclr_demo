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
        private const string M00ImagePath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        private const string M00ImageSha256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string M00ProviderAssemblyIdentity = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        private const string H1WitnessAssembly = "AssemblyShadowDemo.Bootstrap";
        private const string H1WitnessType = "AssemblyShadowDemo.H1CountEarlyStartup";
        private const string H1WitnessMethod = "AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()";
        private const string H1WitnessPrimaryHash = "fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e";
        private const string H1WitnessVariantHash = "4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e";
        private const int H1WitnessOperationIndex = 25;
        private const string H1WitnessProviderSemanticDevelopment = "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369";
        private const string H1WitnessProviderSemanticRelease = "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022";
        private static readonly string[] ExpectedSiteIds =
        {
            "urp-debug-ui-prefab-types",
            "urp-serializable-enum-player",
            "urp-volume-assembly-domain",
            "urp-volume-type-domain",
            "m00-normal-hot-update-image",
            "h1-count-ordinary-witness-image",
        };

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
            public string methodSignature;
            public string originalMethodHash;
            public int operationIndex;
            public MethodVariant[] additionalMethodVariants;
            public string[] allowedTypes;
            public string kind;
            public string imageSha256;
            public string providerAssemblyIdentity;
            public SemanticVariant[] providerSemanticVariants;
            public string imagePath;
        }

        [Serializable] private sealed class MethodVariant
        {
            public string originalMethodHash;
            public int operationIndex;
        }

        [Serializable] private sealed class SemanticVariant
        {
            public string compilerMode;
            public string semanticHash;
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
            public int schemaVersion = 2;
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
            public string finiteAssemblyGuard;
            public string finiteTypesGuard;
            public string fixedImageGuard;
            public string[] discoveryAllowedTypes;
            public string[] discoveryAssemblyNames;
            public bool discoveryDeniedBeforeEnumeration;
            public bool volumeManagerMatchesContract;
            public string fixedImageSha256;
            public string fixedImageLoadedAssembly;
            public string fixedImageLoadedMarker;
            public bool fixedImageTamperRejected;
            public bool fixedImageNullRejected;
            public bool fixedImageCallerBytesUnchanged;
            public bool h1WitnessContractValidated;
            public string h1WitnessMethod;
            public string h1WitnessPrimaryHash;
            public int h1WitnessOperationIndex;
            public string h1WitnessImageSha256;
            public string h1WitnessProviderAssembly;
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
            Require(configuration != null && configuration.schemaVersion == 4 && configuration.transformerVersion == 4 &&
                configuration.sites != null, "Unexpected finite binding fixture.");
            ValidateExactSiteMembership(configuration.sites.Select(site => site == null ? null : site.id));
            Site canvasSite = configuration.sites.Single(site => site.id == "urp-debug-ui-prefab-types");
            Site enumSite = configuration.sites.Single(site => site.id == "urp-serializable-enum-player");
            Require(canvasSite.allowedTypes != null && canvasSite.allowedTypes.Length == 26 &&
                canvasSite.allowedTypes.Distinct(StringComparer.Ordinal).Count() == 26 &&
                enumSite.allowedTypes != null && enumSite.allowedTypes.Length == 0, "Unexpected finite domains.");
            MethodInfo canvasGuard = FindGuard(typeof(DebugUIHandlerCanvas), canvasSite, typeof(Type), typeof(string));
            MethodInfo enumGuard = FindGuard(typeof(SerializableEnum), enumSite, typeof(Type), typeof(string));
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
            ProbeDiscovery(result, configuration);
            ProbeFixedImage(result, configuration);
            ProbeH1Witness(result, configuration);
        }

        private static void ProbeDiscovery(ProbeResult result, Configuration configuration)
        {
            Site assembliesSite = configuration.sites.Single(site => site.id == "urp-volume-assembly-domain");
            Site typesSite = configuration.sites.Single(site => site.id == "urp-volume-type-domain");
            Require(assembliesSite.kind == "FiniteAssemblyList" && typesSite.kind == "FiniteAssemblyTypes" &&
                assembliesSite.allowedTypes.Length == 17 && assembliesSite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal)
                    .SequenceEqual(typesSite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal)), "Unexpected volume discovery contract.");
            MethodInfo assemblyGuard = FindGuard(typeof(CoreUtils), assembliesSite, typeof(Assembly[]), typeof(AppDomain));
            Type lambda = typeof(CoreUtils).GetNestedType("<>c", BindingFlags.NonPublic);
            Require(lambda != null, "The pinned CoreUtils discovery lambda was stripped.");
            MethodInfo typesGuard = FindGuard(lambda, typesSite, typeof(Type[]), typeof(Assembly));
            Require(assemblyGuard.Name.Substring(GuardPrefix.Length, 64) == result.configurationHash &&
                typesGuard.Name.Substring(GuardPrefix.Length, 64) == result.configurationHash, "Mixed discovery configurations.");
            result.finiteAssemblyGuard = assemblyGuard.Name;
            result.finiteTypesGuard = typesGuard.Name;
            var assemblies = (Assembly[])assemblyGuard.Invoke(null, new object[] { AppDomain.CurrentDomain });
            result.discoveryAssemblyNames = assemblies.Select(value => value.GetName().Name).OrderBy(value => value, StringComparer.Ordinal).ToArray();
            Require(result.discoveryAssemblyNames.SequenceEqual(new[] { "Unity.RenderPipelines.Universal.Runtime" }), "Discovery enumerated an undeclared assembly.");
            var direct = (Type[])typesGuard.Invoke(null, new object[] { assemblies[0] });
            string[] expected = typesSite.allowedTypes.OrderBy(value => value, StringComparer.Ordinal).ToArray();
            Require(direct.Select(type => type.AssemblyQualifiedName).OrderBy(value => value, StringComparer.Ordinal).SequenceEqual(expected),
                "Finite type guard changed its approved types.");
            var witness = new EnumerationWitness();
            RequireDenied(() => typesGuard.Invoke(null, new object[] { witness }), typesSite.id, result.configurationHash);
            RequireDenied(() => typesGuard.Invoke(null, new object[] { null }), typesSite.id, result.configurationHash);
            result.discoveryDeniedBeforeEnumeration = witness.enumerationCalls == 0;
            Require(result.discoveryDeniedBeforeEnumeration, "A rejected receiver was enumerated before rejection.");
            // Exercise the original caller and VolumeManager as well as the guards.
            // A post-GetTypes filter is not sufficient to pass this contract.
            result.discoveryAllowedTypes = CoreUtils.GetAllAssemblyTypes().Select(type => type.AssemblyQualifiedName)
                .OrderBy(value => value, StringComparer.Ordinal).ToArray();
            Require(result.discoveryAllowedTypes.SequenceEqual(expected), "Actual CoreUtils discovery differs from its finite contract.");
            result.volumeManagerMatchesContract = VolumeManager.instance.baseComponentTypeArray.Select(type => type.AssemblyQualifiedName)
                .OrderBy(value => value, StringComparer.Ordinal).SequenceEqual(expected);
            Require(result.volumeManagerMatchesContract, "VolumeManager lost an approved component type.");
        }

        private static void ProbeFixedImage(ProbeResult result, Configuration configuration)
        {
            Site site = configuration.sites.Single(value => value.id == "m00-normal-hot-update-image");
            RequireFixedImageSite(site, "m00-normal-hot-update-image", "AssemblyShadowBaseline.Aot",
                "AssemblyShadowBaseline.BaselineBootstrap", "System.Void AssemblyShadowBaseline.BaselineBootstrap::Start()",
                "5f6005b4130594f1c951bd8aba50f784b27976027977e8108ff6662170b87c22", 28,
                "27b4708dcf832f298f02c6939e548a06d0e34de908bf76743eebb0e80e22ed75", 23,
                M00ImagePath, M00ImageSha256, M00ProviderAssemblyIdentity);
            MethodInfo guard = FindGuard(typeof(AssemblyShadowBaseline.BaselineBootstrap), site, typeof(Assembly), typeof(byte[]));
            result.fixedImageGuard = guard.Name;
            Require(guard.Name.Substring(GuardPrefix.Length, 64) == result.configurationHash, "Mixed fixed-image configuration.");
            byte[] image = File.ReadAllBytes(Path.Combine(Application.streamingAssetsPath,
                M00ImagePath.Substring("Assets/StreamingAssets/".Length)));
            result.fixedImageSha256 = ShadowPatchFileProvider.Hash(image);
            Require(result.fixedImageSha256 == site.imageSha256, "Staged normal hot-update bytes differ from the fixed contract.");
            byte[] altered = (byte[])image.Clone();
            altered[altered.Length / 2] ^= 1;
            RequireDenied(() => guard.Invoke(null, new object[] { altered }), site.id, result.configurationHash);
            result.fixedImageTamperRejected = true;
            RequireDenied(() => guard.Invoke(null, new object[] { null }), site.id, result.configurationHash);
            result.fixedImageNullRejected = true;
            var loaded = (Assembly)guard.Invoke(null, new object[] { image });
            result.fixedImageLoadedAssembly = loaded.FullName;
            Require(loaded.FullName == site.providerAssemblyIdentity, "Fixed image loaded the wrong physical assembly.");
            // A literal ordinary-hot-update entry is declared in the dependency
            // policy. No Shadow candidate type or token is introduced here.
            Type entry = Type.GetType("AssemblyShadowBaseline.HotUpdate.Entry, AssemblyShadowBaseline.HotUpdate", true);
            Require(entry.Assembly == loaded, "Normal hot-update entry resolved to a different assembly.");
            result.fixedImageLoadedMarker = (string)entry.GetMethod("Run", BindingFlags.Public | BindingFlags.Static).Invoke(null, null);
            Require(result.fixedImageLoadedMarker == "M00-HOTUPDATE-OK", "The fixed normal hot-update method did not execute.");
            result.fixedImageCallerBytesUnchanged = ShadowPatchFileProvider.Hash(image) == result.fixedImageSha256;
            Require(result.fixedImageCallerBytesUnchanged, "The guard modified caller-owned image bytes.");
        }

        private static void ProbeH1Witness(ProbeResult result, Configuration configuration)
        {
            Site site = configuration.sites.Single(value => value.id == "h1-count-ordinary-witness-image");
            RequireFixedImageSite(site, "h1-count-ordinary-witness-image", H1WitnessAssembly, H1WitnessType, H1WitnessMethod,
                H1WitnessPrimaryHash, H1WitnessOperationIndex, H1WitnessVariantHash, H1WitnessOperationIndex,
                M00ImagePath, M00ImageSha256, M00ProviderAssemblyIdentity);
            Require(site.providerSemanticVariants != null && site.providerSemanticVariants.Length == 2,
                "Unexpected H1 witness semantic variants.");
            Require(site.providerSemanticVariants.Any(value => value != null && value.compilerMode == "Development" &&
                value.semanticHash == H1WitnessProviderSemanticDevelopment) &&
                site.providerSemanticVariants.Any(value => value != null && value.compilerMode == "Release" &&
                value.semanticHash == H1WitnessProviderSemanticRelease),
                "Unexpected H1 witness provider semantics.");
            ValidateH1WitnessContract(site.methodSignature, site.originalMethodHash, site.operationIndex,
                site.additionalMethodVariants[0].originalMethodHash, site.additionalMethodVariants[0].operationIndex,
                site.imageSha256, site.providerAssemblyIdentity);
            result.h1WitnessContractValidated = true;
            result.h1WitnessMethod = site.methodSignature;
            result.h1WitnessPrimaryHash = site.originalMethodHash;
            result.h1WitnessOperationIndex = site.operationIndex;
            result.h1WitnessImageSha256 = site.imageSha256;
            result.h1WitnessProviderAssembly = site.providerAssemblyIdentity;
        }

        private static void RequireFixedImageSite(Site site, string expectedId, string expectedAssembly, string expectedType,
            string expectedMethod, string expectedHash, int expectedOperationIndex, string expectedVariantHash,
            int expectedVariantOperationIndex, string expectedImagePath, string expectedImageSha256,
            string expectedProviderAssemblyIdentity)
        {
            Require(site != null && site.id == expectedId && site.assembly == expectedAssembly &&
                site.typeName == expectedType && site.methodSignature == expectedMethod &&
                site.originalMethodHash == expectedHash && site.operationIndex == expectedOperationIndex &&
                site.kind == "FixedAssemblyBytes" && site.allowedTypes != null && site.allowedTypes.Length == 0 &&
                site.imagePath == expectedImagePath && site.imageSha256 == expectedImageSha256 &&
                site.providerAssemblyIdentity == expectedProviderAssemblyIdentity,
                "Unexpected fixed-image contract: " + expectedId);
            Require(site.additionalMethodVariants != null && site.additionalMethodVariants.Length == 1 &&
                site.additionalMethodVariants[0] != null &&
                site.additionalMethodVariants[0].originalMethodHash == expectedVariantHash &&
                site.additionalMethodVariants[0].operationIndex == expectedVariantOperationIndex,
                "Unexpected fixed-image method variants: " + expectedId);
        }

        private static void ValidateExactSiteMembership(IEnumerable<string> siteIds)
        {
            string[] observed = siteIds == null ? null : siteIds.ToArray();
            Require(observed != null && observed.Length == ExpectedSiteIds.Length &&
                observed.All(id => ExpectedSiteIds.Contains(id, StringComparer.Ordinal)) &&
                ExpectedSiteIds.All(id => observed.Count(value => value == id) == 1),
                "Unexpected finite binding site membership.");
        }

        private static void ValidateH1WitnessContract(string methodSignature, string originalMethodHash, int operationIndex,
            string variantHash, int variantOperationIndex, string imageSha256, string providerAssemblyIdentity)
        {
            Require(methodSignature == H1WitnessMethod && originalMethodHash == H1WitnessPrimaryHash &&
                operationIndex == H1WitnessOperationIndex && variantHash == H1WitnessVariantHash &&
                variantOperationIndex == H1WitnessOperationIndex && imageSha256 == M00ImageSha256 &&
                providerAssemblyIdentity == M00ProviderAssemblyIdentity,
                "Unexpected H1 witness acquisition contract.");
        }

        [UnityEngine.Scripting.Preserve]
        private sealed class EnumerationWitness : Assembly
        {
            public int enumerationCalls;
            public override Type[] GetTypes() { ++enumerationCalls; return new Type[0]; }
        }

        private static void RequireDenied(Action action, string site, string configurationHash)
        {
            Exception failure = null;
            try { action(); }
            catch (TargetInvocationException error) { failure = error.InnerException; }
            catch (Exception error) { failure = error; }
            Require(failure is InvalidOperationException && failure.Message ==
                "AssemblyShadow reflection denied; configuration=" + configurationHash + "; site=" + site,
                "An undeclared acquisition escaped its guard: " + site);
        }

        private static MethodInfo FindGuard(Type owner, Site site, Type returnType, Type parameterType)
        {
            Require(owner.FullName == site.typeName.Replace('/', '+') && owner.Assembly.GetName().Name == site.assembly, "Wrong guard consumer.");
            var guards = owner.GetMethods(BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Where(method => method.Name.StartsWith(GuardPrefix, StringComparison.Ordinal)).ToArray();
            Require(guards.Length == 1, "Expected exactly one emitted guard on " + owner.FullName);
            var guard = guards[0];
            string suffix = "_" + ShadowPatchFileProvider.Hash(Encoding.UTF8.GetBytes(site.id));
            Require(guard.IsPrivate && guard.ReturnType == returnType && guard.GetParameters().Length == 1 &&
                guard.GetParameters()[0].ParameterType == parameterType && guard.Name.Length == GuardPrefix.Length + 129 &&
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
