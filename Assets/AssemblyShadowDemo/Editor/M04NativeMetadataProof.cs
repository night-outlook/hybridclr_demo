using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    [Serializable] public sealed class M04NativeAssemblyIdentity
    {
        public int assemblyIndex, imageIndex;
        public uint token;
        public string imageName, name, fullName, version, culture, publicKeyToken;
    }

    /// <summary>Native inventory comes from the actual Player metadata, including converter-generated assemblies.</summary>
    public static class M04NativeMetadataProof
    {
        public const int MetadataVersion = 31;
        private const int HeaderSize = 256, ImageStride = 40, AssemblyStride = 64;
        private const uint Magic = 0xfab11baf;
        private static readonly UTF8Encoding StrictUtf8 = new UTF8Encoding(false, true);

        public sealed class Capture
        {
            public string path, sha256;
            public int version;
            public M04NativeAssemblyIdentity[] assemblies;
            public string[] generatedAssemblyNames;
        }

        public static Capture ReadPlayer(string playerOutput, M04AssemblyIdentity[] linkedAssemblies)
        {
            string path = FindMetadataPath(playerOutput);
            byte[] bytes = File.ReadAllBytes(path);
            var assemblies = Parse(bytes);
            return new Capture {
                path = path, sha256 = ShadowHash.Bytes(bytes), version = MetadataVersion, assemblies = assemblies,
                generatedAssemblyNames = VerifyLinkedIdentities(assemblies, linkedAssemblies),
            };
        }

        public static void Verify(M04Build.M04PlayerBuildReceipt receipt, M04AssemblyIdentity[] verifiedLinkedAssemblies)
        {
            var actual = ReadPlayer(receipt.playerOutput, verifiedLinkedAssemblies);
            Require(receipt.nativeMetadataPath == actual.path && receipt.nativeMetadataSha256 == actual.sha256 &&
                receipt.nativeMetadataVersion == actual.version, "M04NativeMetadataBinding", "Native metadata path/hash/version differs from the actual Player.");
            VerifyIdentities(receipt.nativeAssemblyIdentities, actual.assemblies);
            Require(receipt.nativeGeneratedAssemblyNames != null && receipt.nativeGeneratedAssemblyNames.SequenceEqual(actual.generatedAssemblyNames),
                "M04NativeGeneratedInventory", "Generated names must equal the native metadata inventory minus verified linked DLLs.");
        }

        public static string FindMetadataPath(string playerOutput)
        {
            string root = Path.GetFullPath(playerOutput).TrimEnd(Path.DirectorySeparatorChar);
            Require(Directory.Exists(root), "M04NativeMetadataPath", "M04 metadata evidence requires an existing Player output directory.");
            var pending = new Stack<string>();
            var matches = new List<string>();
            pending.Push(root);
            while (pending.Count != 0)
            {
                string directory = pending.Pop();
                Require((File.GetAttributes(directory) & FileAttributes.ReparsePoint) == 0, "M04NativeMetadataPath", "Player metadata discovery refuses symbolic-link directories.");
                foreach (string file in Directory.GetFiles(directory, "global-metadata.dat", SearchOption.TopDirectoryOnly))
                {
                    Require((File.GetAttributes(file) & FileAttributes.ReparsePoint) == 0, "M04NativeMetadataPath", "Player metadata cannot be a symbolic link.");
                    matches.Add(Path.GetFullPath(file));
                }
                foreach (string child in Directory.GetDirectories(directory)) pending.Push(child);
            }
            Require(matches.Count == 1 && matches[0].StartsWith(root + Path.DirectorySeparatorChar, StringComparison.Ordinal),
                "M04NativeMetadataPath", "Exactly one actual global-metadata.dat inside the Player is required.");
            return matches[0];
        }

        public static M04NativeAssemblyIdentity[] Parse(byte[] bytes)
        {
            Require(bytes != null && bytes.Length >= HeaderSize, "M04NativeMetadataHeader", "Truncated IL2CPP metadata header.");
            Require(UInt32(bytes, 0) == Magic && Int32(bytes, 4) == MetadataVersion,
                "M04NativeMetadataVersion", "Only the pinned IL2CPP metadata magic and version 31 are supported.");
            // The pinned GlobalMetadataFileInternals.h has 31 offset/size pairs.
            // Validate all nonempty regions, so an identity table cannot alias another metadata table.
            var regions = new Dictionary<int, Region>();
            for (int slot = 8; slot < HeaderSize; slot += 8)
            {
                int offset = Int32(bytes, slot), size = Int32(bytes, slot + 4);
                Require(offset >= 0 && size >= 0 && (long)offset + size <= bytes.Length && (size == 0 || offset >= HeaderSize),
                    "M04NativeMetadataBounds", "Out-of-bounds metadata region at header byte " + slot);
                regions.Add(slot, new Region { Offset = offset, Size = size });
            }
            Region[] occupied = regions.Values.Where(region => region.Size != 0).OrderBy(region => region.Offset).ToArray();
            for (int index = 1; index < occupied.Length; ++index)
                Require((long)occupied[index - 1].Offset + occupied[index - 1].Size <= occupied[index].Offset,
                    "M04NativeMetadataOverlap", "Metadata regions overlap.");
            Region strings = regions[24], images = regions[168], assemblies = regions[176], references = regions[192];
            Require(strings.Size > 0 && images.Size > 0 && assemblies.Size > 0 && images.Size % ImageStride == 0 &&
                assemblies.Size % AssemblyStride == 0 && references.Size % 4 == 0,
                "M04NativeMetadataStride", "Metadata image/assembly/reference tables have invalid strides.");
            int imageCount = images.Size / ImageStride, assemblyCount = assemblies.Size / AssemblyStride, referenceCount = references.Size / 4;
            Require(imageCount == assemblyCount, "M04NativeMetadataImageBinding", "Each native assembly must have exactly one image.");
            for (int index = 0; index < referenceCount; ++index)
                Require(InRange(Int32(bytes, references.Offset + index * 4), assemblyCount),
                    "M04NativeMetadataReferences", "Referenced-assembly table contains an invalid assembly index.");
            var rows = new List<M04NativeAssemblyIdentity>(assemblyCount);
            var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var boundImages = new HashSet<int>();
            for (int index = 0; index < assemblyCount; ++index)
            {
                int offset = assemblies.Offset + index * AssemblyStride;
                int imageIndex = Int32(bytes, offset), referenceStart = Int32(bytes, offset + 8), referenceLength = Int32(bytes, offset + 12);
                Require(InRange(imageIndex, imageCount) && boundImages.Add(imageIndex), "M04NativeMetadataImageBinding", "Assembly image index is invalid or reused.");
                int imageOffset = images.Offset + imageIndex * ImageStride;
                Require(Int32(bytes, imageOffset + 4) == index, "M04NativeMetadataImageBinding", "Image-to-assembly reverse binding differs.");
                Require(referenceLength >= 0 && referenceStart >= -1 &&
                    (referenceLength == 0 ? referenceStart <= referenceCount : referenceStart >= 0 && (long)referenceStart + referenceLength <= referenceCount),
                    "M04NativeMetadataReferences", "Assembly reference range is invalid.");
                string name = String(bytes, strings, Int32(bytes, offset + 16));
                string culture = String(bytes, strings, Int32(bytes, offset + 20));
                // Native code treats the public key as a byte pointer, not UTF-8 text.
                StringEnd(bytes, strings, Int32(bytes, offset + 24));
                string imageName = String(bytes, strings, Int32(bytes, imageOffset));
                Require(!string.IsNullOrWhiteSpace(name) && names.Add(name) && !string.IsNullOrWhiteSpace(imageName),
                    "M04NativeMetadataIdentity", "Native assembly names must be nonempty and unique.");
                Require(imageName == name || imageName == name + ".dll" || imageName == name + ".exe",
                    "M04NativeMetadataImageBinding", "Native image name does not identify its assembly.");
                var components = new int[4];
                for (int part = 0; part < components.Length; ++part)
                {
                    components[part] = Int32(bytes, offset + 40 + part * 4);
                    Require(components[part] >= 0 && components[part] <= ushort.MaxValue, "M04NativeMetadataIdentity", "Invalid native assembly version component.");
                }
                string version = string.Join(".", components.Select(part => part.ToString(CultureInfo.InvariantCulture)));
                // AssemblyName::AssemblyNameToString uses the FIRST byte as the absence sentinel.
                // This differs intentionally from declared AssemblyRef token preservation in DLL evidence.
                string token = bytes[offset + 56] == 0 ? "" : BitConverter.ToString(bytes, offset + 56, 8).Replace("-", "").ToLowerInvariant();
                uint flags = UInt32(bytes, offset + 36), assemblyToken = UInt32(bytes, offset + 4);
                Require((assemblyToken & 0xff000000u) == 0x20000000u, "M04NativeMetadataIdentity", "Invalid native Assembly table token.");
                string fullName = name + ", Version=" + version + ", Culture=" + (culture.Length == 0 ? "neutral" : culture) +
                    ", PublicKeyToken=" + (token.Length == 0 ? "null" : token) + ((flags & 0x100u) != 0 ? ", Retargetable=Yes" : "") +
                    (name == "WindowsRuntimeMetadata" ? ", ContentType=WindowsRuntime" : "");
                rows.Add(new M04NativeAssemblyIdentity {
                    assemblyIndex = index, imageIndex = imageIndex, token = assemblyToken, imageName = imageName,
                    name = name, fullName = fullName, version = version, culture = culture, publicKeyToken = token,
                });
            }
            return rows.OrderBy(row => row.name, StringComparer.Ordinal).ToArray();
        }

        public static string[] VerifyLinkedIdentities(M04NativeAssemblyIdentity[] native, M04AssemblyIdentity[] linked)
        {
            Require(native != null && linked != null && native.Length > 0 && linked.Length > 0 &&
                native.All(row => row != null && !string.IsNullOrWhiteSpace(row.name)) &&
                linked.All(row => row != null && !string.IsNullOrWhiteSpace(row.name)) &&
                native.Select(row => row.name).Distinct(StringComparer.OrdinalIgnoreCase).Count() == native.Length &&
                linked.Select(row => row.name).Distinct(StringComparer.OrdinalIgnoreCase).Count() == linked.Length,
                "M04NativeLinkedIdentity", "Native and linked identity inventories must be nonempty and unique.");
            var actual = native.ToDictionary(row => row.name, StringComparer.Ordinal);
            foreach (var assembly in linked)
            {
                M04NativeAssemblyIdentity row;
                Require(actual.TryGetValue(assembly.name, out row) && row.fullName == assembly.fullName && row.version == assembly.version &&
                    row.culture == assembly.culture && row.publicKeyToken == assembly.publicKeyToken,
                    "M04NativeLinkedIdentity", "Linked DLL identity differs from native metadata: " + assembly.name);
            }
            var linkedNames = new HashSet<string>(linked.Select(row => row.name), StringComparer.Ordinal);
            return native.Where(row => !linkedNames.Contains(row.name)).Select(row => row.name).OrderBy(name => name, StringComparer.Ordinal).ToArray();
        }

        public static void VerifyIdentities(M04NativeAssemblyIdentity[] claimed, M04NativeAssemblyIdentity[] actual)
        {
            Require(claimed != null && actual != null && claimed.Length == actual.Length, "M04NativeIdentityEvidence", "Native identity inventory length differs.");
            for (int index = 0; index < actual.Length; ++index)
            {
                var a = claimed[index]; var b = actual[index];
                Require(a != null && b != null && a.assemblyIndex == b.assemblyIndex && a.imageIndex == b.imageIndex && a.token == b.token &&
                    a.imageName == b.imageName && a.name == b.name && a.fullName == b.fullName && a.version == b.version &&
                    a.culture == b.culture && a.publicKeyToken == b.publicKeyToken, "M04NativeIdentityEvidence", "Native identity fields differ from metadata at row " + index);
            }
        }

        private sealed class Region { public int Offset, Size; }
        private static bool InRange(int value, int count) { return value >= 0 && value < count; }
        private static uint UInt32(byte[] bytes, int offset)
        {
            return (uint)(bytes[offset] | bytes[offset + 1] << 8 | bytes[offset + 2] << 16 | bytes[offset + 3] << 24);
        }
        private static int Int32(byte[] bytes, int offset) { return unchecked((int)UInt32(bytes, offset)); }
        private static int StringEnd(byte[] bytes, Region strings, int index)
        {
            Require(InRange(index, strings.Size), "M04NativeMetadataString", "Native metadata string index is out of bounds.");
            int start = strings.Offset + index;
            int end = Array.IndexOf(bytes, (byte)0, start, strings.Size - index);
            Require(end >= start, "M04NativeMetadataString", "Native metadata string lacks a bounded terminator.");
            return end;
        }
        private static string String(byte[] bytes, Region strings, int index)
        {
            int end = StringEnd(bytes, strings, index);
            try { return StrictUtf8.GetString(bytes, strings.Offset + index, end - strings.Offset - index); }
            catch (DecoderFallbackException) { throw new ShadowBuildException("M04NativeMetadataString", "Native metadata identity string is not valid UTF-8."); }
        }
        private static void Require(bool condition, string code, string message) { ShadowHash.Require(condition, code, message); }
    }
}
