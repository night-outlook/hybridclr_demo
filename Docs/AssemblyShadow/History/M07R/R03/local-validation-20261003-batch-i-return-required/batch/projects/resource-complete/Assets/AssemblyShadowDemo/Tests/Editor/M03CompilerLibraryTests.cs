using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M03CompilerLibraryTests
    {
        [Test]
        public void InstalledCompilerBytesAndIdentityProduceBoundEvidence()
        {
            using (var fixture = new Fixture())
            {
                var proof = fixture.Proof();
                Assert.AreEqual(1, proof.Providers.Count);
                StringAssert.StartsWith(AssemblyName.GetAssemblyName(fixture.CatalogPath).FullName + " | sha256=", proof.Providers[0]);
                StringAssert.EndsWith(ShadowHash.File(fixture.CapturedPath), proof.Providers[0]);
                var receipt = fixture.Receipt(); receipt.references[0].sourcePath = "/untrusted/forged/source/UnityEngine.dll";
                Assert.AreEqual(proof.ProvenanceHash, fixture.Proof(receipt).ProvenanceHash,
                    "sourcePath is descriptive, never compiler-library authority.");
                Assert.AreNotEqual(proof.ProvenanceHash, fixture.Proof(frameworkHash: new string('2', 64)).ProvenanceHash);
            }
        }

        [Test]
        public void CapturedInputRoleCanMatchButFilteredRoleCannot()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                var receipt = fixture.Receipt();
                Directory.CreateDirectory(Path.Combine(fixture.Snapshot, "Assemblies"));
                var file = receipt.references[0];
                file.path = "Assemblies/" + file.name + ".dll";
                File.Copy(fixture.CapturedPath, Path.Combine(fixture.Snapshot, file.path));
                receipt.references = new SnapshotFile[0]; receipt.assemblies = new[] { file };
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt);
                Assert.AreEqual(1, fixture.Proof(receipt).Providers.Count);
                file.path = "Assemblies/Filtered/" + file.name + ".dll";
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt);
                AssertCode("M03CompilerReferenceRoleMismatch", () => fixture.Proof(receipt));
            }
        }

        [Test]
        public void ChangedCapturedBytesFailEvenAfterSelfRehashing()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                var receipt = fixture.Receipt();
                AppendOverlay(fixture.CapturedPath);
                AssertCode("M03CompilerReferenceHashMismatch", () => fixture.Proof(receipt));
                AssertCode("M03CompilerReferenceMismatch", () => fixture.Proof());
            }
        }

        [Test]
        public void ChangedInstalledBytesFailEvenWithSameAssemblyIdentity()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                AppendOverlay(fixture.CatalogPath);
                AssertCode("M03CompilerReferenceMismatch", () => fixture.Proof());
            }
        }

        [Test]
        public void ConflictingCompilerLocationsAreRejected()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                string other = Path.Combine(fixture.Contents, "Other", Path.GetFileName(fixture.CatalogPath));
                Directory.CreateDirectory(Path.GetDirectoryName(other)); File.Copy(fixture.CatalogPath, other);
                Assert.AreEqual(1, fixture.Proof(compilerReferences: new[] { fixture.CatalogPath, other }).Providers.Count);
                AppendOverlay(other);
                AssertCode("M03CompilerCatalogAmbiguous", () => fixture.Proof(compilerReferences: new[] { fixture.CatalogPath, other }));
            }
        }

        [Test]
        public void InstalledFileNeedsActualCompilerMembershipAndExternalNamesGrantNothing()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                string anchor = Path.Combine(fixture.Contents, "Target", "mscorlib.dll");
                File.Copy(typeof(object).Assembly.Location, anchor);
                // The CoreModule remains installed, but is not in this supplied
                // compiler catalog. A project copy with the same name cannot
                // substitute for compiler membership, even with sourcePath set.
                var receipt = fixture.Receipt(); receipt.references[0].sourcePath = fixture.CatalogPath;
                Assert.IsEmpty(fixture.Proof(receipt, new[] { anchor, fixture.CapturedPath }).Providers);
                AssertCode("M03CompilerCatalogUnavailable", () => fixture.Proof(compilerReferences: new[] { fixture.CapturedPath }));
                AssertCode("M03CompilerCatalogUnavailable", () => fixture.Proof(compilerReferences: new string[0]));
            }
        }

        [Test]
        public void SnapshotHashRoleAndIdentityAreChecked()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                var receipt = fixture.Receipt(); receipt.snapshotHash = new string('0', 64);
                AssertCode("M03CompilerSnapshotMismatch", () => fixture.Proof(receipt));
                receipt = fixture.Receipt(); receipt.references[0].path = "Assemblies/" + fixture.Name + ".dll";
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt);
                AssertCode("M03CompilerReferenceRoleMismatch", () => fixture.Proof(receipt));
                receipt = fixture.Receipt(); receipt.references = new[] { receipt.references[0], receipt.references[0] };
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt);
                AssertCode("M03CompilerReferenceRoleMismatch", () => fixture.Proof(receipt));
                receipt = fixture.Receipt(); receipt.references[0].name = "UnityEngine.Forged";
                receipt.references[0].path = "References/UnityEngine.Forged.dll";
                File.Copy(fixture.CapturedPath, Path.Combine(fixture.Snapshot, receipt.references[0].path));
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt);
                AssertCode("M03CompilerReferenceIdentityMismatch", () => fixture.Proof(receipt));
            }
        }

        [Test]
        public void ProductionEntryRequiresVerifiedTargetFrameworkBinding()
        {
            using (var fixture = new Fixture())
            {
                Assert.AreEqual(1, fixture.Proof().Providers.Count);
                AssertCode("M03CompilerTargetMismatch", () => M03CompilerLibraryVerifier.Verify(fixture.Snapshot, fixture.Receipt(), null));
            }
        }

        private static void AppendOverlay(string path)
        {
            // A PE overlay changes bytes without changing managed identity.
            using (var stream = new FileStream(path, FileMode.Append, FileAccess.Write)) stream.WriteByte(0x41);
        }

        private static void AssertCode(string expected, TestDelegate action)
        {
            Assert.AreEqual(expected, Assert.Throws<ShadowBuildException>(action).Code);
        }

        private sealed class Fixture : IDisposable
        {
            public readonly string Root, Contents, Snapshot, Name, CatalogPath, CapturedPath;
            public Fixture()
            {
                Root = Path.Combine(Path.GetTempPath(), "M03CompilerLibrary-" + Guid.NewGuid().ToString("N"));
                Contents = Path.Combine(Root, "Editor.app/Contents"); Snapshot = Path.Combine(Root, "Snapshot");
                string source = typeof(UnityEngine.Object).Assembly.Location;
                Name = AssemblyName.GetAssemblyName(source).Name;
                CatalogPath = Path.Combine(Contents, "Target/" + Name + ".dll");
                CapturedPath = Path.Combine(Snapshot, "References/" + Name + ".dll");
                Directory.CreateDirectory(Path.GetDirectoryName(CatalogPath)); Directory.CreateDirectory(Path.GetDirectoryName(CapturedPath));
                File.Copy(source, CatalogPath); File.Copy(source, CapturedPath);
            }

            public AssemblySnapshotReceipt Receipt()
            {
                var pin = new ShadowRepositoryPin { revision = new string('1', 40) };
                var receipt = new AssemblySnapshotReceipt {
                    kind = "CompilePlayerScripts", unityVersion = "fixture", target = "StandaloneOSX", architecture = "arm64",
                    sourcePins = new ShadowSourcePins { unityVersion = "fixture", target = "StandaloneOSX", architecture = "arm64",
                        hybridclr = pin, hybridclrUnity = pin, il2cppPlus = pin, demo = pin },
                    assemblies = new SnapshotFile[0],
                    references = new[] { new SnapshotFile { name = Name, path = "References/" + Name + ".dll",
                        sha256 = ShadowHash.File(CapturedPath), sourcePath = "untrusted" } },
                };
                receipt.snapshotHash = AssemblySnapshot.ComputeHash(receipt); return receipt;
            }

            public M03CompilerLibraryEvidence Proof(AssemblySnapshotReceipt receipt = null, string[] compilerReferences = null, string frameworkHash = null)
            {
                var method = typeof(M03CompilerLibraryVerifier).GetMethod("VerifyAgainstCatalog", BindingFlags.NonPublic | BindingFlags.Static);
                try { return (M03CompilerLibraryEvidence)method.Invoke(null, new object[] { Snapshot, receipt ?? Receipt(), Contents,
                    compilerReferences ?? new[] { CatalogPath }, frameworkHash ?? new string('1', 64) }); }
                catch (TargetInvocationException error) { throw error.InnerException; }
            }

            public void Dispose() { Directory.Delete(Root, true); }
        }
    }
}
