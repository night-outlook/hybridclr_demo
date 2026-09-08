using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07R01OrdinarySnapshotBindingTests
    {
        private const string ImageName = "AssemblyShadowBaseline.HotUpdate";

        [Test]
        public void RepresentativeWireFixtureReturnsVerifiedBytesAndPath()
        {
            using (Fixture fixture = Fixture.Create())
            {
                Assert.AreNotEqual(fixture.SnapshotHash, fixture.RawReceiptSha256);
                M07R01OrdinarySnapshotBinding.VerifiedImage image = fixture.Load();
                Assert.AreEqual(fixture.ImagePath, image.path);
                CollectionAssert.AreEqual(fixture.ImageBytes, image.bytes);
            }
        }

        [TestCase("")]
        [TestCase("0000000000000000000000000000000000000000000000000000000000000000")]
        public void MissingOrWrongRawReceiptDigestIsRejected(string rawDigest)
        {
            using (Fixture fixture = Fixture.Create())
                Assert.Throws<InvalidOperationException>(() => fixture.Load(rawReceiptSha256: rawDigest));
        }

        [Test]
        public void WrongSemanticHashIsRejectedEvenWhenRawReceiptMatches()
        {
            using (Fixture fixture = Fixture.Create())
                Assert.Throws<InvalidOperationException>(() => fixture.Load(snapshotHash: new string('0', 64)));
        }

        [Test]
        public void WrongPlayerIdentityIsRejected()
        {
            using (Fixture fixture = Fixture.Create())
                Assert.Throws<InvalidOperationException>(() => fixture.Load(buildGuid: "wrong-build-guid"));
        }

        [Test]
        public void MissingFilteredImageIsRejected()
        {
            using (Fixture fixture = Fixture.Create())
                Assert.Throws<InvalidOperationException>(() => fixture.Load(imageName: "Missing.Image"));
        }

        [Test]
        public void DuplicateFilteredImageIsRejected()
        {
            using (Fixture fixture = Fixture.Create(duplicateImage: true))
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
        }

        [Test]
        public void MutatedFilteredDllIsRejected()
        {
            using (Fixture fixture = Fixture.Create())
            {
                File.WriteAllBytes(fixture.ImagePath, fixture.ImageBytes.Concat(new byte[] { 0xFF }).ToArray());
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
        }

        private static string Digest(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        private sealed class Fixture : IDisposable
        {
            internal readonly string Root;
            internal readonly string ImagePath;
            internal readonly byte[] ImageBytes;
            internal readonly string SnapshotHash;
            internal readonly string RawReceiptSha256;
            private readonly SnapshotDto snapshot;

            private Fixture(bool duplicateImage)
            {
                Root = Path.Combine(Path.GetTempPath(), "assembly-shadow-r01-binding-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(Path.Combine(Root, "Assemblies", "Filtered"));
                ImagePath = Path.Combine(Root, "Assemblies", "Filtered", "AssemblyShadowBaseline.HotUpdate.dll");
                ImageBytes = new byte[] { 0x41, 0x53, 0x2D, 0x52, 0x30, 0x31 };
                File.WriteAllBytes(ImagePath, ImageBytes);
                SnapshotHash = new string('a', 64);
                snapshot = new SnapshotDto {
                    schemaVersion = 1, kind = "PlayerBuildInputs", snapshotHash = SnapshotHash,
                    buildGuid = "fixture-build-guid", playerOutput = "/fixture/player.app",
                    nativeLibraryPath = "/fixture/player.app/Contents/Frameworks/GameAssembly.dylib",
                    nativeLibrarySha256 = new string('b', 64), playerBuildSucceeded = true,
                    playerBuildFilterCaptured = true,
                    filteredAssemblies = new[] {
                        new SnapshotFileDto { name = ImageName, path = "Assemblies/Filtered/AssemblyShadowBaseline.HotUpdate.dll", sha256 = Digest(ImageBytes) }
                    }
                };
                if (duplicateImage)
                    snapshot.filteredAssemblies = snapshot.filteredAssemblies.Concat(new[] {
                        new SnapshotFileDto { name = ImageName, path = snapshot.filteredAssemblies[0].path, sha256 = snapshot.filteredAssemblies[0].sha256 }
                    }).ToArray();
                string receiptPath = Path.Combine(Root, "assembly-snapshot.json");
                File.WriteAllText(receiptPath, JsonUtility.ToJson(snapshot, true));
                RawReceiptSha256 = Digest(File.ReadAllBytes(receiptPath));
            }

            internal static Fixture Create(bool duplicateImage = false) { return new Fixture(duplicateImage); }

            internal M07R01OrdinarySnapshotBinding.VerifiedImage Load(string snapshotHash = null,
                string buildGuid = null, string rawReceiptSha256 = null, string imageName = ImageName)
            {
                return M07R01OrdinarySnapshotBinding.LoadVerifiedImage(Root,
                    snapshotHash ?? snapshot.snapshotHash, buildGuid ?? snapshot.buildGuid,
                    snapshot.playerOutput, snapshot.nativeLibraryPath, snapshot.nativeLibrarySha256,
                    rawReceiptSha256 ?? RawReceiptSha256, imageName);
            }

            public void Dispose()
            {
                try { Directory.Delete(Root, true); } catch { }
            }
        }

        [Serializable]
        private sealed class SnapshotDto
        {
            public int schemaVersion;
            public string kind, snapshotHash, buildGuid, playerOutput, nativeLibraryPath, nativeLibrarySha256;
            public bool playerBuildSucceeded, playerBuildFilterCaptured;
            public SnapshotFileDto[] filteredAssemblies;
        }

        [Serializable]
        private sealed class SnapshotFileDto
        {
            public string name, path, sha256;
        }
    }
}
