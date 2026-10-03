using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07R01OrdinarySnapshotBindingTests
    {
        private const string ImageName = "AssemblyShadowBaseline.HotUpdate";
        private const string ReflectionPrefix = "ASSEMBLY_SHADOW_REFLECTION_BINDINGS_";
        private const string FixedImageSha256 = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string FixedImageSiteId = "m00-normal-hot-update-image";
        private const string FixedImageProvider = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        private const string FixedImageContractPath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        private const string FixedImageMethodHash = "5f6005b4130594f1c951bd8aba50f784b27976027977e8108ff6662170b87c22";
        private const string DevelopmentSemanticHash = "7af4cf568c2c6bccebd58e780846f22826472629ca972e5abfcd02a8ba636369";
        private const string ReleaseSemanticHash = "e34d8fe97ff909d878e91a081565fd7afaee5d1672da091eb58aadbb0289d022";

        [Test]
        public void RepresentativeWireFixtureReturnsVerifiedBytesAndPath()
        {
            using (Fixture fixture = Fixture.Create())
            {
                Assert.AreNotEqual(fixture.SnapshotHash, fixture.RawReceiptSha256);
                M07R01OrdinarySnapshotBinding.VerifiedImage image = fixture.Load();
                Assert.AreEqual(fixture.FixedImagePath, image.path);
                CollectionAssert.AreEqual(fixture.FixedImageBytes, image.bytes);
                CollectionAssert.AreNotEqual(fixture.FilteredImageBytes, image.bytes);
            }
        }

        [Test]
        public void FixedImageSelectionRejectsMissingDuplicateAndMalformedControlDefine()
        {
            using (Fixture fixture = Fixture.Create())
            {
                fixture.SetReflectionDefines();
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
                fixture.SetReflectionDefines(ReflectionPrefix + fixture.ConfigurationHash,
                    ReflectionPrefix + fixture.ConfigurationHash);
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
                fixture.SetReflectionDefines(ReflectionPrefix + "bad");
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
        }

        [Test]
        public void FixedImageSelectionRejectsConfigurationAndSiteIdentityTampering()
        {
            foreach (Action<BindingSiteDto> mutation in new[] {
                new Action<BindingSiteDto>(site => site.kind = "TypeGetType"),
                new Action<BindingSiteDto>(site => site.assembly = "Wrong.Consumer"),
                new Action<BindingSiteDto>(site => site.providerAssemblyIdentity = "Wrong.Provider, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null")
            })
            {
                using (Fixture fixture = Fixture.Create())
                {
                    fixture.MutateSite(mutation);
                    Assert.Throws<InvalidOperationException>(() => fixture.Load());
                }
            }
            using (Fixture fixture = Fixture.Create())
            {
                fixture.MutateConfiguration(config => config.sites = new BindingSiteDto[0]);
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
            using (Fixture fixture = Fixture.Create())
            {
                fixture.MutateConfiguration(config => config.sites = config.sites.Concat(new[] { config.sites[0] }).ToArray());
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
        }

        [Test]
        public void FixedImageSelectionRejectsConfigurationHashAndBlobTampering()
        {
            using (Fixture fixture = Fixture.Create())
            {
                fixture.MutateConfigurationWithoutUpdatingDefine(config => config.sites[0].reason = "mutated");
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
            using (Fixture fixture = Fixture.Create())
            {
                File.Delete(fixture.FixedImagePath);
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
            }
            using (Fixture fixture = Fixture.Create())
            {
                File.WriteAllBytes(fixture.FixedImagePath, fixture.FixedImageBytes.Concat(new byte[] { 0xFF }).ToArray());
                Assert.Throws<InvalidOperationException>(() => fixture.Load());
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
                File.WriteAllBytes(fixture.FilteredImagePath, fixture.FilteredImageBytes.Concat(new byte[] { 0xFF }).ToArray());
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
            internal readonly string FilteredImagePath;
            internal readonly string FixedImagePath;
            internal readonly byte[] FilteredImageBytes;
            internal readonly byte[] FixedImageBytes;
            internal readonly string SnapshotHash;
            internal string RawReceiptSha256;
            internal string ConfigurationHash { get; private set; }
            private readonly SnapshotDto snapshot;
            private readonly string configurationPath;
            private BindingConfigurationDto configuration;

            private Fixture(bool duplicateImage)
            {
                Root = Path.Combine(Path.GetTempPath(), "assembly-shadow-r01-binding-" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(Path.Combine(Root, "Assemblies", "Filtered"));
                Directory.CreateDirectory(Path.Combine(Root, "ReflectionBindings", "Images"));
                FilteredImagePath = Path.Combine(Root, "Assemblies", "Filtered", "AssemblyShadowBaseline.HotUpdate.dll");
                FixedImagePath = Path.Combine(Root, "ReflectionBindings", "Images", FixedImageSha256 + ".dll.bytes");
                FilteredImageBytes = new byte[] { 0x46, 0x49, 0x4C, 0x54, 0x45, 0x52, 0x45, 0x44 };
                FixedImageBytes = ReadApprovedFixedImage();
                File.WriteAllBytes(FilteredImagePath, FilteredImageBytes);
                File.WriteAllBytes(FixedImagePath, FixedImageBytes);
                SnapshotHash = new string('a', 64);
                configurationPath = Path.Combine(Root, "ReflectionBindings", "configuration.json");
                configuration = CreateConfiguration();
                WriteConfiguration(false);
                snapshot = new SnapshotDto {
                    schemaVersion = 1, kind = "PlayerBuildInputs", snapshotHash = SnapshotHash,
                    buildGuid = "fixture-build-guid", playerOutput = "/fixture/player.app",
                    nativeLibraryPath = "/fixture/player.app/Contents/Frameworks/GameAssembly.dylib",
                    nativeLibrarySha256 = new string('b', 64), playerBuildSucceeded = true,
                    playerBuildFilterCaptured = true,
                    extraScriptingDefines = new[] {
                        "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_" + new string('c', 64),
                        ReflectionPrefix + ConfigurationHash
                    },
                    linkedPlayerReceipt = new LinkedPlayerReceiptDto {
                        schemaVersion = 2, buildGuid = "fixture-build-guid",
                        nativeLibrarySha256 = new string('b', 64), reflectionBindingEvidenceHash = new string('d', 64)
                    },
                    linkedPlayerReceiptHash = new string('e', 64),
                    filteredAssemblies = new[] {
                        new SnapshotFileDto { name = ImageName, path = "Assemblies/Filtered/AssemblyShadowBaseline.HotUpdate.dll", sha256 = Digest(FilteredImageBytes) }
                    }
                };
                if (duplicateImage)
                    snapshot.filteredAssemblies = snapshot.filteredAssemblies.Concat(new[] {
                        new SnapshotFileDto { name = ImageName, path = snapshot.filteredAssemblies[0].path, sha256 = snapshot.filteredAssemblies[0].sha256 }
                    }).ToArray();
                WriteReceipt();
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

            internal void SetReflectionDefines(params string[] defines)
            {
                snapshot.extraScriptingDefines = defines;
                WriteReceipt();
            }

            internal void MutateSite(Action<BindingSiteDto> mutation)
            {
                mutation(configuration.sites[0]);
                WriteConfiguration(true);
            }

            internal void MutateConfiguration(Action<BindingConfigurationDto> mutation)
            {
                mutation(configuration);
                WriteConfiguration(true);
            }

            internal void MutateConfigurationWithoutUpdatingDefine(Action<BindingConfigurationDto> mutation)
            {
                mutation(configuration);
                WriteConfiguration(false);
            }

            private void WriteConfiguration(bool updateDefine)
            {
                File.WriteAllText(configurationPath, JsonUtility.ToJson(configuration, true));
                ConfigurationHash = Digest(File.ReadAllBytes(configurationPath));
                if (updateDefine)
                {
                    snapshot.extraScriptingDefines = new[] {
                        "ASSEMBLY_SHADOW_RAW_TYPE_ADMISSION_" + new string('c', 64), ReflectionPrefix + ConfigurationHash
                    };
                    WriteReceipt();
                }
            }

            private void WriteReceipt()
            {
                string receiptPath = Path.Combine(Root, "assembly-snapshot.json");
                File.WriteAllText(receiptPath, JsonUtility.ToJson(snapshot, true));
                RawReceiptSha256 = Digest(File.ReadAllBytes(receiptPath));
            }

            private static BindingConfigurationDto CreateConfiguration()
            {
                return new BindingConfigurationDto {
                    schemaVersion = 4, transformerVersion = 4,
                    sites = new[] { new BindingSiteDto {
                        id = FixedImageSiteId, assembly = "AssemblyShadowBaseline.Aot",
                        typeName = "AssemblyShadowBaseline.BaselineBootstrap",
                        methodSignature = "System.Void AssemblyShadowBaseline.BaselineBootstrap::Start()",
                        originalMethodHash = FixedImageMethodHash, operationIndex = 28,
                        additionalMethodVariants = new[] { new BindingMethodVariantDto {
                            originalMethodHash = "27b4708dcf832f298f02c6939e548a06d0e34de908bf76743eebb0e80e22ed75", operationIndex = 23
                        }},
                        allowedTypes = new string[0], reason = "test",
                        kind = "FixedAssemblyBytes", imageSha256 = FixedImageSha256,
                        providerAssemblyIdentity = FixedImageProvider, imagePath = FixedImageContractPath,
                        providerSemanticVariants = new[] {
                            new BindingSemanticVariantDto { compilerMode = "Development", semanticHash = DevelopmentSemanticHash },
                            new BindingSemanticVariantDto { compilerMode = "Release", semanticHash = ReleaseSemanticHash }
                        }
                    }}
                };
            }

            private static byte[] ReadApprovedFixedImage()
            {
                const string compressed =
                    "H4sIAAAAAAAC/+0XW2wcV/Xc2YfXdmq8sRsSCO0mbooTt7uzL++uGop3d2Zjl7h2vXYaIgtnZudmPdXszDIza2ehqUpRQHwUgdTy" +
                    "kS8E/UEEqVVTqUKEDySkSk0kRIXajxaFCIl8FPGFBAhizr0zu+O4FhZIfKBy1/fcex73vO5jjufPfQdCABDGvrUF8CZ4bQb2bs9jH3nwpyNwbfDmkTfJ6ZtHltd1J9G2raattBINxTQtN6HShN0xE7qZkBbqiZal0eR99w095OtYlAFOkxDEjr//y57eW3A0MUxEgCFEoh7tt5MIEn3HRvlc8PwGCEbulOBNQzBzmYmyv2DsD7x9C/Uu+AHHQrsEeR5gHw4XPwuwDP9GQ/9i29AY4rPb8KRLL7o4nh304xoK/N6m4nzSduwG+L7N+IHuu1cOyTNJmxpWw2ed93WNfkSustPN65PeOMuXROAtNPoq5pzAf9bGxDB8Efj6OOyHu/dHUO9+eLD04jASj/2KbdnkAIZ7CQMKI2PKZ5A+I8wZn7wU9ccIHw9cQmY4OjwFAyeOCpMxlrETn7JxWfsE2qvUn6gQ32uWg41cUkxmxWy6xCgRMFg60PjEcwDP4lhE8xN119bNpsMkrqEVdiYnVurwXsRL3cSplTkJxzuIv8XwimGpfpyogjz9kpAYZHn+G8nCAS9nI9gH/M62LObPBS8n/ZH4fIAlwfM6Cn8lrwtROCQweIN8X/gEvCMw+hVOv0xOIrzF4RvkBYQDoU2E5wiDBYHBv/C1hzn9FNKZ3h9z7V5uRvkBOMaxr5FRSIU0wrAQd+iazwvDMPIeQcpx5IRhDGdfBobFfOzbfSxL3oEcQgJF9PQBchLhOId/FGYQ3ubwaKgKi+yUk+/CSKiGNt5gGHzj4BX0lMDPOfY9eE74AmKDcAVzEgfGO4RwCG2xeQnhKJQRHgAF9ocmYI7TkzCMdzgJY3AW4adhE6owgQ9BFabgMsIs+vt1TiFIYRklUOL7chjuTLLQDx5nOxN+fudp1gijB3dhCh4j3nkSUEsYNfB3pyrni7JYSpdquVpBzpVLcj4zXcjly+ni9HRFluVCKZ1JF9Pl6WwxnZsuV2tSPltNl4rTxayUKaRhxdTdbt3q2A16iprUVlyqlR2HtlSjO2+ZVr1h6213udumztpGGtbW6q7i6o2ybSvdOVzLOHX9K/Rzuey/YOYLcHLe0joGfRxOLtr6BpqZa7UN2qImW2KZEnUV3XAeB/S1Klcy+bwol9JluZzJZNLVYrYql6YztXwply+g22JGLOVztayYKxTy" +
                    "uYKcTmfKtXxOEqUacF8lxVWgpht0UXHXPSyIhqMmdR1XMTXF1mCpY7p6i9Z0amizSDMonFGMDmWqoJeN+rqiWZsVxaGGbtLkrOWutDWMA2RNdy27YlubjqIalOWAQtVqtdG8HSTVxSuvdpDVJ1XxixSQJap2mk2mIaDtUB0wPPU8c0vUUC7ymRPw/YiYGLJU3cBdDriVLoJ613FpK8lELBO3AfeHGntGm9QMw1/KjARaNCpZnjYWNiQb6HiPK+lK07QcPBpOj+Q72F9Qp/aG3qCOnwZ8HJk/DixbrmKwjfSnfHd74c1So01tBxbUZ2jDxcS6wI6drhh46PgphDnHy+GCaXRBNl27y6/TkXkQ8fcofn0W8Ou6Aosg4f1eBhlpC8Degquv/fkPr3yYm3nxFf326o/uPgbhBCGxUAJIBCfxOIeHIgmBjIxEB4T4eHx8AASyPx8vxW58dWzr5qMfPBWKxg9iPxyKfiYiRGNCVMBbGx/HR28kRvyv9APsSVwWDjxtK+0nLVO+2KBttpvL62zbCcoN8JsfZjDW+9IUCKT53U0G59o/WJa9jTZnXrD69K3ea3Jo/PrvgMwvCvztA7iBNcaNweD1YTbGsCMZVHyn1KF7X6cdn3dYqkv1H7z8w3cj574kvfzrbx7/+8+snzAdqRUH9yelrKdO6e5sR02td1Vb1xqGHczWNNqy1hx+3lKnddVW7G6qQmlKsV39gtJwnVRGFFVRXJTohqQ2k5rSTO15TNuaCvXZciY/Db5jL/3Gd4wF/8I/7v/Fh78XN4Wnbk+9NhkE8nav2NulXZ/cjq1VLVsyjHlFN6HlNCybenfDb1vHUE0/TQ/v5e+zwdH0059eZWtcZ3X3pav9pat8abLhwP9yIzxZB70q+h46S4a4C71XO57F4vLqtvr1qpBDeAbqsIZQhiWczeGdfhLxOYQ1r+qG6+E/3d2t2vz8trp+R1kMErd8BmsAG/XoWNtR1GnCBbA4/yG+ahm5+IEBB/kKuChnIea1V8P7WAGHPrkopSO9uYumO4TJiP1fDlSWA3iE1wQ9eQm7Aw2up32PnQTPWWyb7BnsNkoHMiJWLEEHeIZXYMwHl8ua6LuB+VKghTjg6+jgjyKmIr2LEawjT0N9m1jbKZxn8IgoapxFuovvahslFK4xiTMDvAsyyeM4jdQmt1JF6TbqZJE0Ua/rx2BznxZ8uu771IvJ/K/4luN5W0SbFlI7mF/3I9nbmbsiX7PTi8Se6z7WLeH9v3SrCP9vH8P2T30AJ0oAEgAA";
                using (var input = new MemoryStream(Convert.FromBase64String(compressed)))
                using (var gzip = new GZipStream(input, CompressionMode.Decompress))
                using (var output = new MemoryStream()) { gzip.CopyTo(output); return output.ToArray(); }
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
            public string[] extraScriptingDefines;
            public LinkedPlayerReceiptDto linkedPlayerReceipt;
            public string linkedPlayerReceiptHash;
            public SnapshotFileDto[] filteredAssemblies;
        }

        [Serializable]
        private sealed class SnapshotFileDto
        {
            public string name, path, sha256;
        }

        [Serializable]
        private sealed class LinkedPlayerReceiptDto
        {
            public int schemaVersion;
            public string buildGuid, nativeLibrarySha256, reflectionBindingEvidenceHash;
        }

        [Serializable]
        private sealed class BindingConfigurationDto
        {
            public int schemaVersion, transformerVersion;
            public BindingSiteDto[] sites;
        }

        [Serializable]
        private sealed class BindingSiteDto
        {
            public string id, assembly, typeName, methodSignature, originalMethodHash, kind;
            public string imageSha256, providerAssemblyIdentity, imagePath;
            public int operationIndex;
            public BindingMethodVariantDto[] additionalMethodVariants;
            public string[] allowedTypes;
            public string reason;
            public BindingSemanticVariantDto[] providerSemanticVariants;
        }

        [Serializable]
        private sealed class BindingMethodVariantDto
        {
            public string originalMethodHash;
            public int operationIndex;
        }

        [Serializable]
        private sealed class BindingSemanticVariantDto
        {
            public string compilerMode, semanticHash;
        }
    }
}
