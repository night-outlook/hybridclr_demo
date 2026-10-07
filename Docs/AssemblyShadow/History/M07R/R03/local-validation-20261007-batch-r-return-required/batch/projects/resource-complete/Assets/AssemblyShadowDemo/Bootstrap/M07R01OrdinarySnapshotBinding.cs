using System;
using System.IO;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo
{
    /// <summary>
    /// Hash-bound ordinary image selection for the R01 Player probe. The
    /// semantic snapshot hash identifies the captured input set; the raw
    /// receipt hash is supplied by the launcher after preflight and binds the
    /// exact JSON consumed by this boundary.
    /// </summary>
    [Preserve]
    public static class M07R01OrdinarySnapshotBinding
    {
        public const string RawReceiptSha256Argument = "-shadowR01SnapshotReceiptSha256";
        private const string ReflectionDefinePrefix = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_";
        private const string ReflectionConfigurationRelativePath = "ReflectionBindings/configuration.json";
        private const string FixedImageSiteId = "m00-normal-hot-update-image";
        private const string FixedImageConsumer = "AssemblyShadowBaseline.Aot";
        private const string FixedImageDeclaringType = "AssemblyShadowBaseline.BaselineBootstrap";
        private const string FixedImageMethod = "System.Void AssemblyShadowBaseline.BaselineBootstrap::Start()";
        private const string FixedImageKind = "FixedAssemblyBytes";
        private const string FixedImageSha256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string FixedImagePath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        private const string FixedImageProvider = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        private const string FixedImageMethodHash = "5f6005b4130594f1c951bd8aba50f784b27976027977e8108ff6662170b87c22";
        private const string FixedImageDevelopmentSemanticHash = "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369";
        private const string FixedImageReleaseSemanticHash = "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022";

        [Preserve]
        public sealed class VerifiedImage
        {
            public readonly byte[] bytes;
            public readonly string path;

            internal VerifiedImage(byte[] bytes, string path)
            {
                this.bytes = bytes;
                this.path = path;
            }
        }

        public static VerifiedImage LoadVerifiedImage(string snapshotRoot, string expectedSnapshotHash,
            string expectedBuildGuid, string expectedPlayerOutput, string expectedNativeLibraryPath,
            string expectedNativeLibrarySha256, string expectedRawReceiptSha256, string imageName)
        {
            string root = Path.GetFullPath(snapshotRoot ?? "");
            string receiptPath = M07Probe.Confined(root, "assembly-snapshot.json");
            M07Probe.Require(Directory.Exists(root) && File.Exists(receiptPath),
                "R01 ordinary image snapshot receipt is missing.");

            // The semantic snapshot hash is not the byte hash of this JSON.
            // The launcher-provided raw digest prevents a modified receipt
            // from replacing its filtered image while retaining snapshotHash.
            byte[] receiptBytes = File.ReadAllBytes(receiptPath);
            M07Probe.Require(M07Probe.IsHash(expectedRawReceiptSha256) &&
                M07Probe.Hash(receiptBytes) == expectedRawReceiptSha256,
                "R01 ordinary image snapshot receipt raw hash differs from launcher preflight.");

            InputSnapshotReceipt snapshot;
            try
            {
                string receiptJson = Encoding.UTF8.GetString(receiptBytes).TrimStart('\uFEFF');
                snapshot = JsonUtility.FromJson<InputSnapshotReceipt>(receiptJson);
            }
            catch (Exception error)
            {
                throw new InvalidOperationException("R01 ordinary image snapshot receipt JSON is malformed.", error);
            }
            M07Probe.Require(snapshot != null && snapshot.schemaVersion == 1 && snapshot.kind == "PlayerBuildInputs" &&
                M07Probe.IsHash(expectedSnapshotHash) && snapshot.snapshotHash == expectedSnapshotHash &&
                snapshot.playerBuildSucceeded && snapshot.playerBuildFilterCaptured &&
                !string.IsNullOrEmpty(expectedBuildGuid) && !string.IsNullOrEmpty(snapshot.buildGuid) &&
                snapshot.buildGuid == expectedBuildGuid &&
                !string.IsNullOrEmpty(expectedPlayerOutput) && !string.IsNullOrEmpty(snapshot.playerOutput) &&
                Path.GetFullPath(snapshot.playerOutput) == Path.GetFullPath(expectedPlayerOutput) &&
                !string.IsNullOrEmpty(expectedNativeLibraryPath) && !string.IsNullOrEmpty(snapshot.nativeLibraryPath) &&
                Path.GetFullPath(snapshot.nativeLibraryPath) == Path.GetFullPath(expectedNativeLibraryPath) &&
                M07Probe.IsHash(expectedNativeLibrarySha256) &&
                M07Probe.IsHash(snapshot.nativeLibrarySha256) &&
                snapshot.nativeLibrarySha256 == expectedNativeLibrarySha256 &&
                snapshot.linkedPlayerReceipt != null && snapshot.linkedPlayerReceipt.schemaVersion == 2 &&
                snapshot.linkedPlayerReceipt.buildGuid == snapshot.buildGuid &&
                snapshot.linkedPlayerReceipt.nativeLibrarySha256 == snapshot.nativeLibrarySha256 &&
                M07Probe.IsHash(snapshot.linkedPlayerReceiptHash) &&
                M07Probe.IsHash(snapshot.linkedPlayerReceipt.reflectionBindingEvidenceHash) &&
                snapshot.filteredAssemblies != null,
                "R01 ordinary image snapshot identity is incomplete or differs from the executed Player.");

            InputSnapshotFile[] matches = snapshot.filteredAssemblies.Where(file => file != null &&
                (file.name == imageName || file.name == imageName + ".dll")).ToArray();
            M07Probe.Require(matches.Length == 1,
                "R01 ordinary image is missing or ambiguous in the filtered Player catalog.");
            InputSnapshotFile filteredFile = matches[0];
            string filteredPath = M07Probe.Confined(root, filteredFile.path);

            // Keep the filtered compiler image as provider identity provenance.
            // It is deliberately not the byte source for the M00 fixed-image
            // guard: the filtered compiler DLL and approved fixed image are
            // different artifacts with different hashes.
            M07Probe.Require(File.Exists(filteredPath), "R01 ordinary filtered provider file is missing: " + filteredPath);
            byte[] filteredBytes = File.ReadAllBytes(filteredPath);
            M07Probe.Require(M07Probe.IsHash(filteredFile.sha256) && M07Probe.Hash(filteredBytes) == filteredFile.sha256,
                "R01 ordinary image bytes differ from the filtered snapshot entry.");

            string controlHash = SelectReflectionControlHash(snapshot.extraScriptingDefines);
            string configurationPath = M07Probe.Confined(root, ReflectionConfigurationRelativePath);
            M07Probe.Require(File.Exists(configurationPath),
                "R01 reflection binding configuration is missing.");
            // Read and hash this file exactly once. The same immutable bytes
            // are parsed below, closing a configuration read/hash race.
            byte[] configurationBytes = File.ReadAllBytes(configurationPath);
            M07Probe.Require(M07Probe.Hash(configurationBytes) == controlHash,
                "R01 reflection binding configuration SHA differs from its control define.");
            ReflectionBindingConfiguration configuration;
            try
            {
                string configurationJson = Encoding.UTF8.GetString(configurationBytes).TrimStart('\uFEFF');
                configuration = JsonUtility.FromJson<ReflectionBindingConfiguration>(configurationJson);
            }
            catch (Exception error)
            {
                throw new InvalidOperationException("R01 reflection binding configuration JSON is malformed.", error);
            }
            ReflectionBindingSite site = SelectFixedImageSite(configuration);
            string fixedImagePath = M07Probe.Confined(root,
                "ReflectionBindings/Images/" + site.imageSha256 + ".dll.bytes");
            M07Probe.Require(File.Exists(fixedImagePath),
                "R01 fixed ordinary image blob is missing: " + fixedImagePath);
            byte[] fixedImageBytes = File.ReadAllBytes(fixedImagePath);
            M07Probe.Require(M07Probe.Hash(fixedImageBytes) == site.imageSha256,
                "R01 fixed ordinary image bytes differ from its configuration SHA.");
            return new VerifiedImage(fixedImageBytes, fixedImagePath);
        }

        private static string SelectReflectionControlHash(string[] defines)
        {
            M07Probe.Require(defines != null, "R01 snapshot compiler defines are missing.");
            string selected = null;
            foreach (string define in defines)
            {
                M07Probe.Require(define != null, "R01 snapshot compiler defines contain a null entry.");
                if (!define.StartsWith(ReflectionDefinePrefix, StringComparison.Ordinal)) continue;
                string hash = define.Substring(ReflectionDefinePrefix.Length);
                M07Probe.Require(M07Probe.IsHash(hash),
                    "R01 reflection binding control define is malformed.");
                M07Probe.Require(selected == null,
                    "R01 snapshot contains duplicate reflection binding control defines.");
                selected = hash;
            }
            M07Probe.Require(selected != null,
                "R01 snapshot reflection binding control define is missing.");
            return selected;
        }

        private static ReflectionBindingSite SelectFixedImageSite(ReflectionBindingConfiguration configuration)
        {
            M07Probe.Require(configuration != null && configuration.schemaVersion == 4 && configuration.transformerVersion == 4 &&
                configuration.sites != null && configuration.sites.Length > 0,
                "R01 reflection binding configuration schema is missing or unsupported.");
            ReflectionBindingSite[] matches = configuration.sites.Where(site => site != null && site.id == FixedImageSiteId).ToArray();
            M07Probe.Require(matches.Length == 1,
                "R01 M00 fixed-image reflection binding site is missing or ambiguous.");
            ReflectionBindingSite site = matches[0];
            M07Probe.Require(site.assembly == FixedImageConsumer && site.typeName == FixedImageDeclaringType &&
                site.methodSignature == FixedImageMethod && site.kind == FixedImageKind &&
                site.allowedTypes != null && site.allowedTypes.Length == 0 &&
                site.imageSha256 == FixedImageSha256 && site.imagePath == FixedImagePath &&
                site.providerAssemblyIdentity == FixedImageProvider && site.originalMethodHash == FixedImageMethodHash &&
                site.providerSemanticVariants != null && site.providerSemanticVariants.Length == 2,
                "R01 M00 fixed-image reflection binding site identity differs from the pinned contract.");
            ReflectionBindingSemanticVariant development = site.providerSemanticVariants.SingleOrDefault(item => item != null && item.compilerMode == "Development");
            ReflectionBindingSemanticVariant release = site.providerSemanticVariants.SingleOrDefault(item => item != null && item.compilerMode == "Release");
            M07Probe.Require(development != null && release != null &&
                M07Probe.IsHash(development.semanticHash) && development.semanticHash == FixedImageDevelopmentSemanticHash &&
                M07Probe.IsHash(release.semanticHash) && release.semanticHash == FixedImageReleaseSemanticHash,
                "R01 M00 fixed-image provider semantic variants differ from the pinned contract.");
            return site;
        }

        [Serializable, Preserve]
        private sealed class InputSnapshotReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind, snapshotHash, buildGuid, playerOutput, nativeLibraryPath, nativeLibrarySha256;
            [Preserve] public bool playerBuildSucceeded, playerBuildFilterCaptured;
            [Preserve] public string[] extraScriptingDefines;
            [Preserve] public InputSnapshotFile[] assemblies;
            [Preserve] public LinkedPlayerReceipt linkedPlayerReceipt;
            [Preserve] public string linkedPlayerReceiptHash;
            [Preserve] public InputSnapshotFile[] filteredAssemblies;
        }

        [Serializable, Preserve]
        private sealed class InputSnapshotFile
        {
            [Preserve] public string name, path, sha256;
        }

        [Serializable, Preserve]
        private sealed class ReflectionBindingConfiguration
        {
            [Preserve] public int schemaVersion, transformerVersion;
            [Preserve] public ReflectionBindingSite[] sites;
        }

        [Serializable, Preserve]
        private sealed class ReflectionBindingSite
        {
            [Preserve] public string id, assembly, typeName, methodSignature, originalMethodHash, kind;
            [Preserve] public string imageSha256, providerAssemblyIdentity, imagePath;
            [Preserve] public string[] allowedTypes;
            [Preserve] public ReflectionBindingSemanticVariant[] providerSemanticVariants;
        }

        [Serializable, Preserve]
        private sealed class ReflectionBindingSemanticVariant
        {
            [Preserve] public string compilerMode, semanticHash;
        }

        [Serializable, Preserve]
        private sealed class LinkedPlayerReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string buildGuid, nativeLibrarySha256, reflectionBindingEvidenceHash;
        }
    }
}
