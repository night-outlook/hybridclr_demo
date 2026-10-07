using System;
using System.IO;
using System.Security.Cryptography;
using UnityEngine;

namespace AssemblyShadowDemo
{
    public sealed class ShadowPatchFileProvider
    {
        [Serializable] public sealed class BundleFile { public string name; public string path; public string sha256; }
        [Serializable] public sealed class BaselineManifest
        {
            public int schemaVersion;
            public string baselineBuildId;
            public string unityVersion;
            public string target;
            public string architecture;
            public BundleFile[] bundles;
        }
        [Serializable] public sealed class PatchManifest
        {
            public string assemblyName;
            public string dllFile;
            public string pdbFile;
            public string patchDllSha256;
            public string baselineMvid;
            public string patchMvid;
            public bool abiCompatible;
        }

        public readonly string Root;
        public readonly BaselineManifest Baseline;
        public readonly string BaselineManifestHash;

        public ShadowPatchFileProvider()
        {
            Root = Path.GetFullPath(Argument("-shadowArtifactsPath",
                Path.Combine(Application.streamingAssetsPath, "AssemblyShadow/M01")));
            string manifest = SafePath(Root, "baseline-manifest.json");
            Baseline = JsonUtility.FromJson<BaselineManifest>(File.ReadAllText(manifest));
            BaselineManifestHash = Hash(File.ReadAllBytes(manifest));
            Require(Baseline != null && Baseline.schemaVersion == 1, "Invalid baseline manifest.");
            Require(Baseline.unityVersion == Application.unityVersion, "Baseline Unity version mismatch.");
            Require(Baseline.bundles != null && Baseline.bundles.Length == 3, "Expected three immutable baseline bundles.");
            VerifyBundles();
        }

        public void VerifyBundles()
        {
            foreach (var bundle in Baseline.bundles)
                Require(Hash(File.ReadAllBytes(SafePath(Root, bundle.path))) == bundle.sha256,
                    "Baseline bundle hash mismatch: " + bundle.name);
        }

        public string BundlePath(string name)
        {
            foreach (var bundle in Baseline.bundles)
                if (bundle.name == name) return SafePath(Root, bundle.path);
            throw new InvalidOperationException("Bundle absent from manifest: " + name);
        }

        public PatchManifest ReadPatch(out byte[] dll, out byte[] pdb)
        {
            string root = Path.GetFullPath(Argument("-shadowPatchPath", Path.Combine(Root, "P01")));
            var manifest = JsonUtility.FromJson<PatchManifest>(File.ReadAllText(SafePath(root, "patch-manifest.json")));
            Require(manifest != null && manifest.assemblyName == ShadowBootstrap.InternalAssembly, "Unexpected patch assembly.");
            Require(manifest.abiCompatible && manifest.baselineMvid != manifest.patchMvid, "Patch ABI/MVID evidence missing.");
            dll = File.ReadAllBytes(SafePath(root, manifest.dllFile));
            Require(Hash(dll) == manifest.patchDllSha256, "Patch DLL hash mismatch.");
            pdb = string.IsNullOrEmpty(manifest.pdbFile) ? null : File.ReadAllBytes(SafePath(root, manifest.pdbFile));
            return manifest;
        }

        public static string SafePath(string root, string relative)
        {
            Require(!string.IsNullOrEmpty(relative) && !Path.IsPathRooted(relative), "Expected a relative artifact path.");
            foreach (string segment in relative.Replace('\\', '/').Split('/'))
                Require(segment != ".." && segment != "." && segment.Length != 0, "Unsafe artifact path.");
            string path = Path.GetFullPath(Path.Combine(root, relative));
            Require(path.StartsWith(Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar,
                StringComparison.Ordinal), "Artifact path escapes root.");
            return path;
        }

        public static string Hash(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        public static string Argument(string name, string fallback)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == name) return args[i + 1];
            return fallback;
        }

        public static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }
    }
}
