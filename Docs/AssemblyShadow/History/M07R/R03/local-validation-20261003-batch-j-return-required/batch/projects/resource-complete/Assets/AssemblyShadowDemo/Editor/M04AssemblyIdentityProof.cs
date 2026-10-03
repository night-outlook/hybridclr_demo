using System;
using System.IO;
using System.Linq;
using System.Text;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    [Serializable] public sealed class M04AssemblyReferenceIdentity
    {
        public int referenceIndex;
        public string name, fullName, version, culture, publicKeyToken;
    }

    [Serializable] public sealed class M04AssemblyIdentity
    {
        public string name, fullName, version, culture, publicKeyToken, mvid, path, sha256;
        public M04AssemblyReferenceIdentity[] referenceIdentities;
    }

    /// <summary>Declared metadata identities. Never resolves a facade to a provider identity.</summary>
    public static class M04AssemblyIdentityProof
    {
        public static M04AssemblyIdentity[] ReadLinked(string root, AssemblySnapshotReceipt receipt)
        {
            ShadowLinkedPlayerEvidence.ReadAndVerify(root, receipt);
            return receipt.linkedPlayerReceipt.assemblies
                .Select(file => ReadFile(ShadowHash.SafeChild(root, ShadowLinkedPlayerEvidence.DirectoryName + "/" + file.path), file.sha256, file.name))
                .OrderBy(identity => identity.name, StringComparer.Ordinal).ToArray();
        }

        public static M04AssemblyIdentity[] ReadPatch(string root, ShadowPatchManifest patch)
        {
            ShadowHash.Require(patch != null && patch.closure != null && patch.closure.Length > 0,
                "M04IdentityPatchMissing", "Patch closure identities require actual artifact DLLs.");
            return patch.closure.Select(file => ReadFile(ShadowHash.SafeChild(root, file.dll), file.sha256, file.name))
                .OrderBy(identity => identity.name, StringComparer.Ordinal).ToArray();
        }

        public static M04AssemblyIdentity ReadFile(string path, string expectedSha256, string expectedName)
        {
            path = Path.GetFullPath(path);
            byte[] bytes = File.ReadAllBytes(path);
            ShadowHash.Require(!string.IsNullOrEmpty(expectedSha256) && ShadowHash.Bytes(bytes) == expectedSha256,
                "M04IdentityBytesChanged", "Assembly identity must bind the captured DLL bytes: " + path);
            using (var module = ModuleDefMD.Load(bytes))
            {
                ShadowHash.Require(module.Assembly != null && AssemblyIdentityUtil.CanonicalName(module.Assembly.Name) ==
                    AssemblyIdentityUtil.CanonicalName(expectedName) && module.Mvid.HasValue,
                    "M04IdentityAssemblyMismatch", "Unexpected assembly identity in DLL: " + path);
                var name = new System.Reflection.AssemblyName(module.Assembly.FullName);
                return new M04AssemblyIdentity {
                    name = name.Name, fullName = module.Assembly.FullName, version = name.Version.ToString(),
                    culture = name.CultureName ?? "", publicKeyToken = Token(name), mvid = module.Mvid.Value.ToString(),
                    path = path, sha256 = expectedSha256,
                    referenceIdentities = module.GetAssemblyRefs().Select((reference, index) => {
                        // GetAssemblyRefs walks the actual table, retaining absent facade refs and row order.
                        ShadowHash.Require(reference.Rid == (uint)index + 1, "M04ReferenceIndexMismatch", "AssemblyRef metadata row ordering changed.");
                        var declared = new System.Reflection.AssemblyName(reference.FullName);
                        return new M04AssemblyReferenceIdentity {
                            referenceIndex = index, name = declared.Name, fullName = reference.FullName,
                            version = declared.Version.ToString(), culture = declared.CultureName ?? "", publicKeyToken = Token(declared),
                        };
                    }).ToArray(),
                };
            }
        }

        public static void Verify(M04AssemblyIdentity[] claimed, M04AssemblyIdentity[] actual)
        {
            ShadowHash.Require(claimed != null && actual != null && claimed.Length == actual.Length,
                "M04IdentityEvidenceMismatch", "Assembly identity inventory differs from actual DLLs.");
            for (int index = 0; index < actual.Length; ++index)
            {
                var left = claimed[index]; var right = actual[index];
                ShadowHash.Require(left != null && right != null && left.name == right.name && left.fullName == right.fullName &&
                    left.version == right.version && left.culture == right.culture && left.publicKeyToken == right.publicKeyToken &&
                    left.mvid == right.mvid && left.path == right.path && left.sha256 == right.sha256 &&
                    left.referenceIdentities != null && left.referenceIdentities.Length == right.referenceIdentities.Length,
                    "M04IdentityEvidenceMismatch", "Assembly identity evidence differs from actual DLL bytes at index " + index);
                for (int referenceIndex = 0; referenceIndex < right.referenceIdentities.Length; ++referenceIndex)
                {
                    var reference = left.referenceIdentities[referenceIndex]; var expected = right.referenceIdentities[referenceIndex];
                    ShadowHash.Require(reference != null && reference.referenceIndex == expected.referenceIndex &&
                        reference.name == expected.name && reference.fullName == expected.fullName && reference.version == expected.version &&
                        reference.culture == expected.culture && reference.publicKeyToken == expected.publicKeyToken,
                        "M04ReferenceIdentityMismatch", "Declared AssemblyRef identity changed: " + right.name + " row " + referenceIndex);
                }
            }
        }

        internal static void WriteNewJson(string path, object value)
        {
            string json = JsonUtility.ToJson(value, true);
            using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            using (var writer = new StreamWriter(stream, new UTF8Encoding(false))) writer.Write(json);
        }

        private static string Token(System.Reflection.AssemblyName name)
        {
            // Empty means absent. A real eight-byte all-zero token is not absence.
            return BitConverter.ToString(name.GetPublicKeyToken() ?? new byte[0]).Replace("-", "").ToLowerInvariant();
        }
    }
}
