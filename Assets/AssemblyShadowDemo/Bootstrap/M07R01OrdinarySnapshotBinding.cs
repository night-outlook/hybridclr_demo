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
                snapshot.filteredAssemblies != null,
                "R01 ordinary image snapshot identity is incomplete or differs from the executed Player.");

            InputSnapshotFile[] matches = snapshot.filteredAssemblies.Where(file => file != null &&
                (file.name == imageName || file.name == imageName + ".dll")).ToArray();
            M07Probe.Require(matches.Length == 1,
                "R01 ordinary image is missing or ambiguous in the filtered Player catalog.");
            InputSnapshotFile file = matches[0];
            string path = M07Probe.Confined(root, file.path);

            // Read once, then hash and return the same bytes. This closes the
            // hash/read TOCTOU gap between validation and the M00 guard.
            M07Probe.Require(File.Exists(path), "R01 ordinary image file is missing: " + path);
            byte[] imageBytes = File.ReadAllBytes(path);
            M07Probe.Require(M07Probe.IsHash(file.sha256) && M07Probe.Hash(imageBytes) == file.sha256,
                "R01 ordinary image bytes differ from the filtered snapshot entry.");
            return new VerifiedImage(imageBytes, path);
        }

        [Serializable, Preserve]
        private sealed class InputSnapshotReceipt
        {
            [Preserve] public int schemaVersion;
            [Preserve] public string kind, snapshotHash, buildGuid, playerOutput, nativeLibraryPath, nativeLibrarySha256;
            [Preserve] public bool playerBuildSucceeded, playerBuildFilterCaptured;
            [Preserve] public InputSnapshotFile[] filteredAssemblies;
        }

        [Serializable, Preserve]
        private sealed class InputSnapshotFile
        {
            [Preserve] public string name, path, sha256;
        }
    }
}
