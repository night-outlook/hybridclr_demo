using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using HybridCLR;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// Exercises ordinary loading without introducing another raw-byte loader.
    /// The existing generated M00 guard remains the sole byte acquisition path.
    /// Call only in a fresh OFF process or after successful shadow publication.
    /// </summary>
    public static class M04OrdinaryAssemblyProbe
    {
        private const string OrdinaryName = "AssemblyShadowBaseline.HotUpdate";
        private const string FixedSite = "m00-normal-hot-update-image";
        private const string GuardPrefix = "__AssemblyShadowReflectionBinding_";

        [Serializable, Preserve]
        public sealed class Result
        {
            [Preserve] public int schemaVersion = 1;
            [Preserve] public string moduleMvidObservationPolicy;
            [Preserve] public string aotFullName, aotMvid;
            [Preserve] public bool aotLoadMatchesType, aotMvidAvailable;
            [Preserve] public string placeholderName;
            [Preserve] public bool placeholderFoundBefore, placeholderHiddenBefore, placeholderSameAfterLoad;
            [Preserve] public int assemblyCountBefore, assemblyCountAfter;
            [Preserve] public int ordinaryCountBefore, ordinaryCountAfter, ordinaryCountAfterDuplicate;
            [Preserve] public string configurationPath, configurationSha256, configurationHash, fixedImageGuard;
            [Preserve] public string fixedImagePath, fixedImageSha256, fixedImageFullName, fixedImageMvid, fixedImageMarker;
            [Preserve] public bool fixedImageMvidAvailable;
            [Preserve] public bool fixedImageTamperRejected, fixedImageNullRejected, fixedImageCallerBytesUnchanged;
            [Preserve] public bool loadedNameSame, enumeratedSame;
            [Preserve] public bool duplicateRejected;
            [Preserve] public string duplicateExceptionType, duplicateMessage;
            [Preserve] public string knownNameResolveInput, knownNameResolveFullName;
            [Preserve] public int knownNameResolveEvents;
            [Preserve] public bool knownNameResolveSame;
            [Preserve] public string supplementaryInputPath, supplementaryInputSha256;
            [Preserve] public string supplementaryInputFullName, supplementaryInputMvid;
            [Preserve] public int supplementaryFirstCode, supplementaryRepeatCode, supplementaryInvalidModeCode;
            [Preserve] public bool supplementaryCallerBytesUnchanged;
        }

        [Serializable, Preserve]
        private sealed class Configuration
        {
            [Preserve] public int schemaVersion;
            [Preserve] public int transformerVersion;
            [Preserve] public Site[] sites;
        }

        [Serializable, Preserve]
        private sealed class Site
        {
            [Preserve] public string id, assembly, typeName, kind, imageSha256, providerAssemblyIdentity;
            [Preserve] public string[] allowedTypes;
        }

        public static Result Run(string linkedMscorlibPath, string linkedMscorlibSha256,
            string linkedMscorlibFullName, string linkedMscorlibMvid)
        {
            var result = new Result {
                moduleMvidObservationPolicy = "unavailable-pinned-il2cpp-use-byte-bound-build-and-native-diagnostics",
                aotMvid = "", aotMvidAvailable = false,
                fixedImageMvid = "", fixedImageMvidAvailable = false,
            };
            Require(!string.IsNullOrEmpty(linkedMscorlibPath) && Path.IsPathRooted(linkedMscorlibPath),
                "Supplementary metadata must come from an absolute captured linked-Player path.");
            byte[] supplementary = File.ReadAllBytes(linkedMscorlibPath);
            result.supplementaryInputPath = Path.GetFullPath(linkedMscorlibPath);
            result.supplementaryInputSha256 = ShadowPatchFileProvider.Hash(supplementary);
            result.supplementaryInputFullName = linkedMscorlibFullName;
            result.supplementaryInputMvid = linkedMscorlibMvid;
            Require(result.supplementaryInputSha256 == linkedMscorlibSha256,
                "Supplementary metadata bytes differ from this Player's linked receipt.");

            Assembly aot = Assembly.Load("mscorlib");
            result.aotFullName = aot.FullName;
            result.aotLoadMatchesType = ReferenceEquals(aot, typeof(object).Assembly);
            // The pinned RuntimeAssembly.GetManifestModuleInternal throws, and
            // RuntimeModule.GetGuidInternal is a no-op. Do not relabel the
            // build-time input MVID as an observed runtime value.
            Require(result.aotLoadMatchesType && result.aotFullName == linkedMscorlibFullName,
                "The runtime AOT mscorlib identity differs from this Player's linked receipt.");

            Assembly[] before = AppDomain.CurrentDomain.GetAssemblies();
            result.assemblyCountBefore = before.Length;
            result.ordinaryCountBefore = before.Count(value => value.GetName().Name == OrdinaryName);
            result.placeholderHiddenBefore = result.ordinaryCountBefore == 0;
            // Normal Prebuild generates this token-zero placeholder from the
            // configured ordinary hot-update list. Never inspect its MVID or
            // types before the real image fills it.
            Assembly placeholder = Assembly.Load("AssemblyShadowBaseline.HotUpdate");
            result.placeholderName = placeholder == null ? "" : placeholder.GetName().Name;
            result.placeholderFoundBefore = result.placeholderName == OrdinaryName;
            Require(result.placeholderFoundBefore && result.placeholderHiddenBefore,
                "Expected the configured ordinary placeholder to be loadable but absent from AppDomain enumeration.");

            result.configurationPath = Path.GetFullPath(Path.Combine(Application.streamingAssetsPath,
                M02ReflectionBindingProbe.StagedConfiguration));
            byte[] configurationBytes = File.ReadAllBytes(result.configurationPath);
            result.configurationSha256 = ShadowPatchFileProvider.Hash(configurationBytes);
            var configuration = JsonUtility.FromJson<Configuration>(Encoding.UTF8.GetString(configurationBytes));
            Require(configuration != null && configuration.schemaVersion == 4 && configuration.transformerVersion == 4 &&
                configuration.sites != null, "The captured finite reflection configuration is missing.");
            Site[] matching = configuration.sites.Where(value => value != null && value.id == FixedSite).ToArray();
            Require(matching.Length == 1, "The fixed ordinary-image contract is missing or ambiguous.");
            Site site = matching[0];
            Require(site.kind == "FixedAssemblyBytes" && site.allowedTypes != null && site.allowedTypes.Length == 0 &&
                !string.IsNullOrEmpty(site.imageSha256) && !string.IsNullOrEmpty(site.providerAssemblyIdentity),
                "The ordinary loader requires the exact generated fixed-byte contract.");
            MethodInfo guard = FindFixedGuard(site);
            result.fixedImageGuard = guard.Name;
            result.configurationHash = guard.Name.Substring(GuardPrefix.Length, 64);
            result.fixedImagePath = Path.GetFullPath(Path.Combine(Application.streamingAssetsPath,
                "AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes"));
            byte[] image = File.ReadAllBytes(result.fixedImagePath);
            result.fixedImageSha256 = ShadowPatchFileProvider.Hash(image);
            Require(result.fixedImageSha256 == site.imageSha256, "Fixed ordinary-image bytes drifted.");

            byte[] tampered = (byte[])image.Clone();
            Require(tampered.Length > 0, "The fixed ordinary image is empty.");
            tampered[tampered.Length / 2] ^= 1;
            result.fixedImageTamperRejected = IsGuardDenial(CaptureFailure(() => guard.Invoke(null, new object[] { tampered })),
                result.configurationHash);
            result.fixedImageNullRejected = IsGuardDenial(CaptureFailure(() => guard.Invoke(null, new object[] { null })),
                result.configurationHash);
            Require(result.fixedImageTamperRejected && result.fixedImageNullRejected,
                "The existing ordinary-image guard did not reject null/tampered bytes.");

            Assembly loaded = (Assembly)guard.Invoke(null, new object[] { image });
            result.fixedImageFullName = loaded.FullName;
            result.placeholderSameAfterLoad = ReferenceEquals(placeholder, loaded);
            result.loadedNameSame = ReferenceEquals(Assembly.Load("AssemblyShadowBaseline.HotUpdate"), loaded);
            Require(result.placeholderSameAfterLoad && result.loadedNameSame && loaded.FullName == site.providerAssemblyIdentity,
                "Ordinary bytes did not fill the existing placeholder identity.");

            // Literal ordinary entry, separately declared in Bootstrap policy.
            Type entry = Type.GetType("AssemblyShadowBaseline.HotUpdate.Entry, AssemblyShadowBaseline.HotUpdate", true);
            Require(ReferenceEquals(entry.Assembly, loaded), "Ordinary entry resolves to another physical image.");
            MethodInfo run = entry.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
            Require(run != null, "The fixed ordinary entry method is absent.");
            result.fixedImageMarker = (string)run.Invoke(null, null);
            Require(result.fixedImageMarker == "M00-HOTUPDATE-OK", "Ordinary interpreter execution failed.");

            Assembly[] after = AppDomain.CurrentDomain.GetAssemblies();
            result.assemblyCountAfter = after.Length;
            Assembly[] ordinary = after.Where(value => value.GetName().Name == OrdinaryName).ToArray();
            result.ordinaryCountAfter = ordinary.Length;
            result.enumeratedSame = ordinary.Length == 1 && ReferenceEquals(ordinary[0], loaded);
            Require(result.enumeratedSame && result.assemblyCountAfter == result.assemblyCountBefore + 1,
                "Ordinary placeholder publication did not invalidate the logical Assembly list once.");

            Exception duplicate = CaptureFailure(() => guard.Invoke(null, new object[] { image }));
            result.duplicateExceptionType = duplicate == null ? "" : duplicate.GetType().FullName;
            result.duplicateMessage = duplicate == null ? "" : duplicate.Message;
            result.duplicateRejected = duplicate != null && result.duplicateMessage.IndexOf(
                "reloading placeholder assembly is not supported!", StringComparison.Ordinal) >= 0;
            result.ordinaryCountAfterDuplicate = AppDomain.CurrentDomain.GetAssemblies()
                .Count(value => value.GetName().Name == OrdinaryName);
            Require(result.duplicateRejected && result.ordinaryCountAfterDuplicate == 1,
                "Reloading an already-filled ordinary placeholder changed its upstream failure contract.");
            result.fixedImageCallerBytesUnchanged = ShadowPatchFileProvider.Hash(image) == result.fixedImageSha256;
            Require(result.fixedImageCallerBytesUnchanged, "Ordinary load modified caller-owned bytes.");

            ProbeKnownNameCallback(result, loaded);

            result.supplementaryInvalidModeCode = (int)RuntimeApi.LoadMetadataForAOTAssembly(supplementary, (HomologousImageMode)(-1));
            result.supplementaryFirstCode = (int)RuntimeApi.LoadMetadataForAOTAssembly(supplementary, HomologousImageMode.Consistent);
            result.supplementaryRepeatCode = (int)RuntimeApi.LoadMetadataForAOTAssembly(supplementary, HomologousImageMode.Consistent);
            Require(result.supplementaryInvalidModeCode == (int)LoadImageErrorCode.INVALID_HOMOLOGOUS_MODE &&
                result.supplementaryFirstCode == (int)LoadImageErrorCode.OK &&
                result.supplementaryRepeatCode == (int)LoadImageErrorCode.HOMOLOGOUS_ASSEMBLY_HAS_LOADED,
                "Ordinary supplementary metadata success/repeat/invalid-mode results changed.");
            result.supplementaryCallerBytesUnchanged = ShadowPatchFileProvider.Hash(supplementary) == linkedMscorlibSha256;
            Require(result.supplementaryCallerBytesUnchanged, "Supplementary loading modified captured metadata bytes.");
            return result;
        }

        private static void ProbeKnownNameCallback(Result result, Assembly loaded)
        {
            int events = 0;
            ResolveEventHandler handler = (sender, args) => { ++events; return loaded; };
            AppDomain.CurrentDomain.AssemblyResolve += handler;
            try
            {
                result.knownNameResolveInput = OrdinaryName;
                Assembly resolved = Assembly.Load("AssemblyShadowBaseline.HotUpdate");
                result.knownNameResolveFullName = resolved.FullName;
                result.knownNameResolveSame = ReferenceEquals(resolved, loaded);
                result.knownNameResolveEvents = events;
                Require(result.knownNameResolveSame && events == 0,
                    "A loaded ordinary name incorrectly invoked the AssemblyResolve callback.");
            }
            finally { AppDomain.CurrentDomain.AssemblyResolve -= handler; }
        }

        private static MethodInfo FindFixedGuard(Site site)
        {
            Type owner = typeof(AssemblyShadowBaseline.BaselineBootstrap);
            Require(owner.FullName == site.typeName && owner.Assembly.GetName().Name == site.assembly,
                "The fixed-image guard consumer differs from configuration.");
            MethodInfo[] guards = owner.GetMethods(BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly)
                .Where(method => method.Name.StartsWith(GuardPrefix, StringComparison.Ordinal)).ToArray();
            Require(guards.Length == 1, "Expected exactly one generated fixed-image guard.");
            MethodInfo guard = guards[0];
            string suffix = "_" + ShadowPatchFileProvider.Hash(Encoding.UTF8.GetBytes(FixedSite));
            Require(guard.IsPrivate && guard.ReturnType == typeof(Assembly) && guard.GetParameters().Length == 1 &&
                guard.GetParameters()[0].ParameterType == typeof(byte[]) && guard.Name.Length == GuardPrefix.Length + 129 &&
                guard.Name.EndsWith(suffix, StringComparison.Ordinal), "The fixed-image guard identity/signature differs.");
            return guard;
        }

        private static Exception CaptureFailure(Action operation)
        {
            try { operation(); return null; }
            catch (TargetInvocationException error) { return error.InnerException ?? error; }
            catch (Exception error) { return error; }
        }

        private static bool IsGuardDenial(Exception error, string configurationHash)
        {
            return error is InvalidOperationException && error.Message ==
                "AssemblyShadow reflection denied; configuration=" + configurationHash + "; site=" + FixedSite;
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
