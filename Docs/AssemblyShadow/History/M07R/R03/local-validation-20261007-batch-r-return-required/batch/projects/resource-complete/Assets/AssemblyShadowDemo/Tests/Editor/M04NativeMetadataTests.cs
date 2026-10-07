using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using AssemblyShadowDemo.Editor;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M04NativeMetadataTests
    {
        [Test]
        public void NativeInventoryRetainsTableIndicesAndDerivesGeneratedNames()
        {
            var fixture = new Fixture();
            var rows = M04NativeMetadataProof.Parse(fixture.Bytes);
            CollectionAssert.AreEqual(new[] { "ConverterOnly", "Linked" }, rows.Select(row => row.name));
            Assert.AreEqual(1, rows[0].assemblyIndex);
            Assert.AreEqual(1, rows[0].imageIndex);
            Assert.AreEqual(0x20000000u, rows[0].token);
            Assert.AreEqual("Linked.dll", rows[1].imageName);
            Assert.AreEqual("1.2.3.4", rows[1].version);
            Assert.AreEqual("Linked, Version=1.2.3.4, Culture=neutral, PublicKeyToken=null", rows[1].fullName);
            CollectionAssert.AreEqual(new[] { "ConverterOnly" }, M04NativeMetadataProof.VerifyLinkedIdentities(rows, fixture.Linked()));
            Assert.IsNull(typeof(M04NativeAssemblyIdentity).GetField("mvid"), "Native metadata does not supply an MVID.");
            Assert.DoesNotThrow(() => M04NativeMetadataProof.VerifyIdentities(rows, M04NativeMetadataProof.Parse(fixture.Bytes)));
        }

        [Test]
        public void NativeNameFormattingUsesPinnedTokenSentinelAndRetargetableFlag()
        {
            var fixture = new Fixture();
            fixture.Write(fixture.Assemblies + 36, 0x100);
            fixture.Bytes[fixture.Assemblies + 56] = 0;
            fixture.Bytes[fixture.Assemblies + 57] = 0xab;
            var identity = M04NativeMetadataProof.Parse(fixture.Bytes).Single(row => row.name == "Linked");
            Assert.AreEqual("", identity.publicKeyToken, "Native code uses the first token byte, unlike declared DLL AssemblyRef evidence.");
            StringAssert.EndsWith("PublicKeyToken=null, Retargetable=Yes", identity.fullName);
            fixture.Bytes[fixture.Assemblies + 56] = 0x01;
            identity = M04NativeMetadataProof.Parse(fixture.Bytes).Single(row => row.name == "Linked");
            Assert.AreEqual("01ab000000000000", identity.publicKeyToken);
            StringAssert.EndsWith("PublicKeyToken=01ab000000000000, Retargetable=Yes", identity.fullName);
            fixture = new Fixture("WindowsRuntimeMetadata");
            StringAssert.EndsWith(", ContentType=WindowsRuntime", M04NativeMetadataProof.Parse(fixture.Bytes).Single(row => row.assemblyIndex == 0).fullName);
        }

        [Test]
        public void MalformedHeadersRegionsAndStridesAreRejected()
        {
            AssertCode("M04NativeMetadataHeader", () => M04NativeMetadataProof.Parse(new byte[255]));
            foreach (string mutation in new[] { "magic", "version29", "version32", "negative-offset", "negative-size", "overflow", "header-overlap", "table-overlap", "image-stride", "assembly-stride", "reference-stride" })
            {
                var fixture = new Fixture();
                string expected = "M04NativeMetadataBounds";
                if (mutation == "magic") { fixture.Write(0, 0); expected = "M04NativeMetadataVersion"; }
                else if (mutation == "version29") { fixture.Write(4, 29); expected = "M04NativeMetadataVersion"; }
                else if (mutation == "version32") { fixture.Write(4, 32); expected = "M04NativeMetadataVersion"; }
                else if (mutation == "negative-offset") fixture.Write(24, -1);
                else if (mutation == "negative-size") fixture.Write(28, -1);
                else if (mutation == "overflow") { fixture.Write(24, int.MaxValue); fixture.Write(28, int.MaxValue); }
                else if (mutation == "header-overlap") fixture.Write(24, 255);
                else if (mutation == "table-overlap") { fixture.Write(168, 256); expected = "M04NativeMetadataOverlap"; }
                else if (mutation == "image-stride") { fixture.Write(172, 79); expected = "M04NativeMetadataStride"; }
                else if (mutation == "assembly-stride") { fixture.Write(180, 127); expected = "M04NativeMetadataStride"; }
                else { fixture.Write(196, 3); expected = "M04NativeMetadataStride"; }
                AssertCode(expected, () => M04NativeMetadataProof.Parse(fixture.Bytes));
            }
        }

        [Test]
        public void InvalidIndicesReverseBindingDuplicateNamesAndReferenceRangesAreRejected()
        {
            foreach (string mutation in new[] { "image-index", "reverse-index", "duplicate-image", "duplicate-name", "reference-index", "reference-start", "reference-count", "negative-count" })
            {
                var fixture = new Fixture();
                string expected = "M04NativeMetadataImageBinding";
                if (mutation == "image-index") fixture.Write(fixture.Assemblies, 2);
                else if (mutation == "reverse-index") fixture.Write(fixture.Images + 4, 1);
                else if (mutation == "duplicate-image") fixture.Write(fixture.Assemblies + 64, 0);
                else if (mutation == "duplicate-name") { fixture.Write(fixture.Assemblies + 64 + 16, fixture.NameIndex); expected = "M04NativeMetadataIdentity"; }
                else if (mutation == "reference-index") { fixture.Write(fixture.References, 2); expected = "M04NativeMetadataReferences"; }
                else if (mutation == "reference-start") { fixture.Write(fixture.Assemblies + 64 + 8, -1); expected = "M04NativeMetadataReferences"; }
                else if (mutation == "reference-count") { fixture.Write(fixture.Assemblies + 64 + 12, 2); expected = "M04NativeMetadataReferences"; }
                else { fixture.Write(fixture.Assemblies + 12, -1); expected = "M04NativeMetadataReferences"; }
                AssertCode(expected, () => M04NativeMetadataProof.Parse(fixture.Bytes));
            }
        }

        [Test]
        public void InvalidStringsVersionAndAssemblyTokenAreRejected()
        {
            foreach (string mutation in new[] { "name-index", "culture-index", "public-key-index", "unterminated", "utf8", "empty-name", "negative-version", "large-version", "token" })
            {
                var fixture = new Fixture();
                string expected = "M04NativeMetadataString";
                if (mutation == "name-index") fixture.Write(fixture.Assemblies + 16, -1);
                else if (mutation == "culture-index") fixture.Write(fixture.Assemblies + 20, int.MaxValue);
                else if (mutation == "public-key-index") fixture.Write(fixture.Assemblies + 24, int.MaxValue);
                else if (mutation == "unterminated") { fixture.Write(fixture.Assemblies + 16, fixture.StringSize - 1); fixture.Bytes[256 + fixture.StringSize - 1] = (byte)'x'; }
                else if (mutation == "utf8") fixture.Bytes[256 + fixture.NameIndex] = 0xff;
                else if (mutation == "empty-name") { fixture.Write(fixture.Assemblies + 16, 0); expected = "M04NativeMetadataIdentity"; }
                else if (mutation == "negative-version") { fixture.Write(fixture.Assemblies + 40, -1); expected = "M04NativeMetadataIdentity"; }
                else if (mutation == "large-version") { fixture.Write(fixture.Assemblies + 40, 65536); expected = "M04NativeMetadataIdentity"; }
                else { fixture.Write(fixture.Assemblies + 4, 0x01000001); expected = "M04NativeMetadataIdentity"; }
                AssertCode(expected, () => M04NativeMetadataProof.Parse(fixture.Bytes));
            }
        }

        [Test]
        public void EveryClaimedNativeFieldAndMissingLinkedIdentityAreRejected()
        {
            var fixture = new Fixture();
            foreach (FieldInfo field in typeof(M04NativeAssemblyIdentity).GetFields())
            {
                var claimed = M04NativeMetadataProof.Parse(fixture.Bytes);
                field.SetValue(claimed[0], field.FieldType == typeof(uint) ? (object)0u : field.FieldType == typeof(int) ? (object)(-1) : "tampered");
                AssertCode("M04NativeIdentityEvidence", () => M04NativeMetadataProof.VerifyIdentities(claimed, M04NativeMetadataProof.Parse(fixture.Bytes)));
            }
            var rows = M04NativeMetadataProof.Parse(fixture.Bytes);
            AssertCode("M04NativeLinkedIdentity", () => M04NativeMetadataProof.VerifyLinkedIdentities(rows.Where(row => row.name != "Linked").ToArray(), fixture.Linked()));
            foreach (string field in new[] { "name", "fullName", "version", "culture", "publicKeyToken" })
            {
                var linked = fixture.Linked(); typeof(M04AssemblyIdentity).GetField(field).SetValue(linked[0], "tampered");
                AssertCode("M04NativeLinkedIdentity", () => M04NativeMetadataProof.VerifyLinkedIdentities(rows, linked));
            }
            AssertCode("M04NativeLinkedIdentity", () => M04NativeMetadataProof.VerifyLinkedIdentities(rows, fixture.Linked().Concat(fixture.Linked()).ToArray()));
            var nameless = fixture.Linked(); nameless[0].name = null;
            AssertCode("M04NativeLinkedIdentity", () => M04NativeMetadataProof.VerifyLinkedIdentities(rows, nameless));
            AssertCode("M04NativeIdentityEvidence", () => M04NativeMetadataProof.VerifyIdentities(rows.Reverse().ToArray(), rows));
        }

        [Test]
        public void ReceiptBindingUsesActualUniquePlayerMetadataAndRejectsTampering()
        {
            string root = Path.Combine(Path.GetTempPath(), "M04MetadataTest-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(root);
            try
            {
                var fixture = new Fixture();
                string path = Path.Combine(root, "global-metadata.dat");
                File.WriteAllBytes(path, fixture.Bytes);
                var capture = M04NativeMetadataProof.ReadPlayer(root, fixture.Linked());
                Assert.AreEqual(path, capture.path);
                var receipt = new M04Build.M04PlayerBuildReceipt {
                    playerOutput = root, nativeMetadataPath = path, nativeMetadataSha256 = capture.sha256,
                    nativeMetadataVersion = capture.version, nativeAssemblyIdentities = capture.assemblies,
                    nativeGeneratedAssemblyNames = capture.generatedAssemblyNames,
                };
                Assert.DoesNotThrow(() => M04NativeMetadataProof.Verify(receipt, fixture.Linked()));
                receipt.nativeMetadataPath = "global-metadata.dat";
                AssertCode("M04NativeMetadataBinding", () => M04NativeMetadataProof.Verify(receipt, fixture.Linked()));
                receipt.nativeMetadataPath = path; receipt.nativeGeneratedAssemblyNames = new[] { "Invented" };
                AssertCode("M04NativeGeneratedInventory", () => M04NativeMetadataProof.Verify(receipt, fixture.Linked()));
                receipt.nativeGeneratedAssemblyNames = capture.generatedAssemblyNames;
                fixture.Bytes[fixture.Assemblies + 64 + 40] = 2;
                File.WriteAllBytes(path, fixture.Bytes);
                AssertCode("M04NativeMetadataBinding", () => M04NativeMetadataProof.Verify(receipt, fixture.Linked()));
                Directory.CreateDirectory(Path.Combine(root, "duplicate"));
                File.WriteAllBytes(Path.Combine(root, "duplicate/global-metadata.dat"), fixture.Bytes);
                AssertCode("M04NativeMetadataPath", () => M04NativeMetadataProof.FindMetadataPath(root));
            }
            finally { Directory.Delete(root, true); }
        }

        [Test]
        public void NativeTokenJsonIsAnExplicitBoundedUnsignedInteger()
        {
            foreach (string valid in new[] { "0", "536870913", "4294967295" })
                Assert.DoesNotThrow(() => M04JsonEvidence.ValidateSchema<TokenEvidence>("{\"token\":" + valid + "}"));
            foreach (string invalid in new[] { "-1", "4294967296", "0.0", "false", "null", "\"1\"" })
                AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<TokenEvidence>("{\"token\":" + invalid + "}"));
            AssertCode("M04EvidenceJsonSchema", () => M04JsonEvidence.ValidateSchema<TokenEvidence>("{}"));
        }

        [Serializable] private sealed class TokenEvidence { public uint token; }
        private static void AssertCode(string code, TestDelegate action) { Assert.AreEqual(code, Assert.Throws<ShadowBuildException>(action).Code); }

        private sealed class Fixture
        {
            public readonly byte[] Bytes;
            public readonly int Images, Assemblies, References, StringSize, NameIndex = 1;
            public Fixture(string linkedName = "Linked")
            {
                byte[] strings = Encoding.UTF8.GetBytes("\0" + linkedName + "\0" + linkedName + ".dll\0ConverterOnly\0ConverterOnly.dll\0");
                StringSize = strings.Length;
                Images = (256 + strings.Length + 3) & ~3;
                Assemblies = Images + 80; References = Assemblies + 128;
                Bytes = new byte[References + 4];
                Buffer.BlockCopy(strings, 0, Bytes, 256, strings.Length);
                Write(0, unchecked((int)0xfab11baf)); Write(4, 31);
                Write(24, 256); Write(28, strings.Length);
                Write(168, Images); Write(172, 80);
                Write(176, Assemblies); Write(180, 128);
                Write(192, References); Write(196, 4);
                int linkedImage = 2 + linkedName.Length;
                int generatedName = linkedImage + linkedName.Length + 5;
                int generatedImage = generatedName + "ConverterOnly".Length + 1;
                for (int index = 0; index < 2; ++index)
                {
                    int image = Images + index * 40, assembly = Assemblies + index * 64;
                    Write(image, index == 0 ? linkedImage : generatedImage); Write(image + 4, index);
                    Write(image + 24, -1); Write(image + 28, index == 0 ? 1 : 0);
                    Write(assembly, index); Write(assembly + 4, index == 0 ? 0x20000001 : 0x20000000);
                    Write(assembly + 8, index == 0 ? -1 : 0); Write(assembly + 12, index);
                    Write(assembly + 16, index == 0 ? NameIndex : generatedName);
                }
                for (int part = 0; part < 4; ++part) Write(Assemblies + 40 + part * 4, part + 1);
                Write(References, 0);
            }
            public void Write(int offset, int value)
            {
                for (int part = 0; part < 4; ++part) Bytes[offset + part] = (byte)((uint)value >> (part * 8));
            }
            public M04AssemblyIdentity[] Linked()
            {
                var row = M04NativeMetadataProof.Parse(Bytes).Single(item => item.assemblyIndex == 0);
                return new[] { new M04AssemblyIdentity { name = row.name, fullName = row.fullName, version = row.version, culture = row.culture, publicKeyToken = row.publicKeyToken } };
            }
        }
    }
}
