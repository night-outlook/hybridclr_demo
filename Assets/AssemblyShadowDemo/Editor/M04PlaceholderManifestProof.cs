using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using HybridCLR.Editor;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    public static class M04PlaceholderManifestProof
    {
        internal const string SnapshotName = "m04-placeholder-AssemblyManifest.cpp";

        internal sealed class CapturedManifest
        {
            internal string sourcePath, sha256;
            internal byte[] bytes;
            internal string[] names;
        }

        internal static CapturedManifest CaptureBeforeBuild()
        {
            string path = Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp/hybridclr/generated/AssemblyManifest.cpp"));
            byte[] bytes = File.ReadAllBytes(path);
            return new CapturedManifest { sourcePath = path, bytes = bytes, sha256 = ShadowHash.Bytes(bytes), names = Parse(bytes) };
        }

        internal static string WriteSnapshot(string root, CapturedManifest captured)
        {
            ShadowHash.Require(ShadowHash.File(captured.sourcePath) == captured.sha256, "M04PlaceholderManifestChanged",
                "Installed generated placeholder manifest changed during Player compilation.");
            string path = Path.GetFullPath(Path.Combine(root, SnapshotName));
            using (var output = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                output.Write(captured.bytes, 0, captured.bytes.Length);
            return path;
        }

        public static string[] Parse(byte[] bytes)
        {
            string source = new UTF8Encoding(false, true).GetString(bytes);
            const string begin = "//!!!{{PLACE_HOLDER", end = "//!!!}}PLACE_HOLDER";
            int start = source.IndexOf(begin, StringComparison.Ordinal), finish = source.IndexOf(end, StringComparison.Ordinal);
            ShadowHash.Require(start >= 0 && finish > start && source.IndexOf(begin, start + begin.Length, StringComparison.Ordinal) < 0 &&
                source.IndexOf(end, finish + end.Length, StringComparison.Ordinal) < 0,
                "M04PlaceholderManifestSchema", "Expected exactly one ordered generated placeholder region.");
            string region = source.Substring(start + begin.Length, finish - start - begin.Length);
            string[] lines = region.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries).Where(line => !string.IsNullOrWhiteSpace(line)).ToArray();
            string[] names = lines.Select(line => {
                Match match = Regex.Match(line, "^\\s*\"([^\"\\\\\\r\\n]+)\"\\s*,\\s*$");
                ShadowHash.Require(match.Success, "M04PlaceholderManifestSchema", "Unexpected generated placeholder declaration: " + line);
                string name = match.Groups[1].Value;
                ShadowHash.Require(!string.IsNullOrWhiteSpace(name) && name == name.Trim() && Path.GetFileName(name) == name &&
                    !name.Contains("/") && !name.Contains("\\"), "M04PlaceholderManifestSchema", "Invalid placeholder simple name.");
                return name;
            }).ToArray();
            ShadowHash.Require(names.Length > 0 && names.Distinct(StringComparer.OrdinalIgnoreCase).Count() == names.Length,
                "M04PlaceholderManifestSchema", "Placeholder manifest must have nonempty, unambiguous assembly names.");
            return names;
        }

        public static void Verify(string snapshotRoot, M04Build.M04PlayerBuildReceipt receipt)
        {
            string expected = Path.GetFullPath(Path.Combine(snapshotRoot, SnapshotName));
            ShadowHash.Require(receipt.placeholderManifestPath == expected && File.Exists(expected), "M04PlaceholderManifestMismatch",
                "Placeholder manifest must be the immutable snapshot copy.");
            byte[] bytes = File.ReadAllBytes(expected);
            ShadowHash.Require(ShadowHash.Bytes(bytes) == receipt.placeholderManifestSha256 && receipt.placeholderAssemblyNames != null &&
                Parse(bytes).SequenceEqual(receipt.placeholderAssemblyNames), "M04PlaceholderManifestMismatch",
                "Placeholder declarations do not replay from captured generated native input bytes.");
        }
    }
}
