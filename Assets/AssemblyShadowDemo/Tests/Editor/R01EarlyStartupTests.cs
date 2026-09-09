using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01EarlyStartupTests
    {
        [Test]
        public void CapsuleCodecReadsVersionedPayloadAndPrerequisites()
        {
            byte[] payload = Encode("Control", ordinary: false);
            R01EarlyStartup.Capsule capsule = R01EarlyStartup.CapsuleCodec.Parse(payload);
            Assert.AreEqual("Control", capsule.mode);
            CollectionAssert.AreEqual(new[] { "AssemblyZ.Contracts", "AssemblyA.Contracts" }, capsule.candidateNames);
            CollectionAssert.AreEqual(new[] { "AssemblyZ.Contracts", "AssemblyA.Contracts" }, capsule.closureLoadOrder);
            Assert.AreEqual(2, capsule.inputs.Length);
            Assert.AreEqual(1, capsule.prerequisites.Length);
            Assert.AreEqual(17L, capsule.prerequisites[0].length);
        }

        [Test]
        public void CapsuleCodecAcceptsBudgetAndNativeScriptModes()
        {
            foreach (string mode in new[] { "Oversize", "Mismatch", "NativeScript" })
            {
                R01EarlyStartup.Capsule capsule = R01EarlyStartup.CapsuleCodec.Parse(Encode(mode, ordinary: false));
                Assert.AreEqual(mode, capsule.mode);
                CollectionAssert.AreEqual(new[] { "AssemblyZ.Contracts", "AssemblyA.Contracts" }, capsule.closureLoadOrder);
            }
        }

        [Test]
        public void CapsuleCodecRejectsTrailingBytesAndMalformedUtf8()
        {
            byte[] payload = Encode("Control", ordinary: false).Concat(new byte[] { 0x7f }).ToArray();
            Assert.Throws<InvalidDataException>(() => R01EarlyStartup.CapsuleCodec.Parse(payload));

            byte[] invalid = Encode("Control", ordinary: false);
            // The first string length begins after magic, version, and mode's
            // four-byte length plus its bytes. Replace the first byte of the
            // baselineBuildId UTF-8 sequence with an invalid continuation.
            int baselineByte = 8 + 4 + 4 + Encoding.UTF8.GetByteCount("Control") + 4;
            invalid[baselineByte] = 0xff;
            Assert.Throws<InvalidDataException>(() => R01EarlyStartup.CapsuleCodec.Parse(invalid));
        }

        [Test]
        public void ReceiptCodecEscapesOpaqueNativePayloadWithoutUnityJsonUtility()
        {
            var receipt = new R01EarlyStartup.Receipt { mode = "Control", result = "Passed", callbackReturnCode = 0 };
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "validate", code = "Success", intCode = 0 });
            receipt.snapshots.Add(new R01EarlyStartup.SnapshotReceipt {
                phase = "after-validate", diagnosticsCode = "Success", diagnosticsJson = "{\"detail\":\"quote\\slash\"}",
                recoveryCode = "Success", recoveryJson = "{\"state\":\"Validated\"}", capacityCode = "Success", capacityJson = "{\"fits\":true}", orderedSizes = new long[] { 1, 2 }
            });
            string json = R01EarlyStartup.ReceiptCodec.Serialize(receipt);
            StringAssert.Contains("\\\"detail\\\":\\\"quote\\\\slash\\\"", json);
            StringAssert.Contains("\"orderedSizes\":[1,2]", json);
            StringAssert.DoesNotContain("UnityEngine.JsonUtility", json);
        }

        [Test]
        public void ReceiptCodecEmitsRequiredStableFieldsAndByteInputs()
        {
            var receipt = new R01EarlyStartup.Receipt {
                baselineBuildId = "baseline", runtimeAbiHash = new string('a', 64), patchId = "patch", inputReadCount = 2
            };
            receipt.byteInputs.Add(new R01EarlyStartup.ByteInputReceipt { name = "AssemblyA.Contracts", path = "/tmp/a.dll", length = 3, sha256 = new string('b', 64), kind = "dll" });
            receipt.byteInputs.Add(new R01EarlyStartup.ByteInputReceipt { path = "/tmp/resource.bundle", length = 4, sha256 = new string('c', 64), kind = "prerequisite" });
            string json = R01EarlyStartup.ReceiptCodec.Serialize(receipt);
            foreach (string field in new[] { "schemaVersion", "kind", "mode", "processId", "managedThreadId", "capsulePath", "capsuleSha256", "baselineBuildId", "runtimeAbiHash", "patchId", "result", "error", "callbackReturnCode", "operations", "snapshots", "byteInputs", "inputReadCount" })
                StringAssert.Contains("\"" + field + "\"", json);
            StringAssert.Contains("\"kind\":\"prerequisite\"", json);
        }

        [Test]
        public void Profile2PatchReservationValidatesDistinctManifestFields()
        {
            var profile = Profile2();
            var report = Report2(profile, 1);
            var closure = new[] { new ShadowPatchMetadataAssembly { name = "AssemblyA.Contracts", dllSize = 3 } };
            int version;
            Dictionary<string, long> sizes;
            Assert.IsTrue(ShadowPatchMetadataReservation.ValidateIfDeclared(2, null, null, profile, report,
                new[] { "AssemblyA.Contracts" }, closure, _ => new byte[] { 1, 2, 3 }, out version, out sizes));
            Assert.AreEqual(2, version);
            Assert.AreEqual(3, sizes["AssemblyA.Contracts"]);

            Assert.Throws<InvalidOperationException>(() => ShadowPatchMetadataReservation.ValidateIfDeclared(2,
                new ShadowPatchMetadataEncodingProfile { profileVersion = 1, nativeBudgetCapabilityVersion = 1 }, null,
                profile, report, new[] { "AssemblyA.Contracts" }, closure, _ => new byte[] { 1, 2, 3 }, out version, out sizes));
            report.acceptedImages = 0;
            Assert.Throws<InvalidOperationException>(() => ShadowPatchMetadataReservation.ValidateIfDeclared(2, null, null,
                profile, report, new[] { "AssemblyA.Contracts" }, closure, _ => new byte[] { 1, 2, 3 }, out version, out sizes));
        }

        [Serializable]
        private sealed class LegacyWire
        {
            public ShadowPatchMetadataEncodingProfile metadataEncodingProfile;
            public ShadowPatchMetadataCapacityReport metadataCapacityReport;
        }

        [Test]
        public void Profile2ReservationAcceptsOnlyExactDormantLegacyJsonUtilityFields()
        {
            string json = UnityEngine.JsonUtility.ToJson(new HybridCLR.Editor.AssemblyShadow.ShadowPatchManifest {
                nativeBudgetCapabilityVersion = 2
            });
            LegacyWire wire = UnityEngine.JsonUtility.FromJson<LegacyWire>(json);
            Assert.NotNull(wire.metadataEncodingProfile);
            Assert.NotNull(wire.metadataCapacityReport);
            var profile = Profile2();
            var report = Report2(profile, 1);
            var closure = new[] { new ShadowPatchMetadataAssembly { name = "AssemblyA.Contracts", dllSize = 3 } };
            int version;
            Dictionary<string, long> sizes;
            Assert.IsTrue(ShadowPatchMetadataReservation.ValidateIfDeclared(2, wire.metadataEncodingProfile,
                wire.metadataCapacityReport, profile, report, new[] { "AssemblyA.Contracts" }, closure,
                _ => new byte[] { 1, 2, 3 }, out version, out sizes));
            wire.metadataEncodingProfile.extraShiftBits[0] = 7;
            Assert.Throws<InvalidOperationException>(() => ShadowPatchMetadataReservation.ValidateIfDeclared(2,
                wire.metadataEncodingProfile, wire.metadataCapacityReport, profile, report,
                new[] { "AssemblyA.Contracts" }, closure, _ => new byte[] { 1, 2, 3 }, out version, out sizes));
            wire = UnityEngine.JsonUtility.FromJson<LegacyWire>(json);
            wire.metadataCapacityReport.nativeSourceRevision = "active-legacy-profile";
            Assert.Throws<InvalidOperationException>(() => ShadowPatchMetadataReservation.ValidateIfDeclared(2,
                wire.metadataEncodingProfile, wire.metadataCapacityReport, profile, report,
                new[] { "AssemblyA.Contracts" }, closure, _ => new byte[] { 1, 2, 3 }, out version, out sizes));
        }

        private static ShadowPatchMetadataEncodingProfile2 Profile2()
        {
            return new ShadowPatchMetadataEncodingProfile2 {
                schemaVersion = 2, profileVersion = 2, nativeBudgetCapabilityVersion = 2,
                codecId = "SparseSignedInt32", codecBits = 32, invalidIndexSentinel = -1,
                aotMaxIndex = int.MaxValue, minImageId = 1, maximumImageCount = 8192,
                pageValues = 4096, usablePageCapacity = 524287, chargedPageCeiling = 393215,
                minimumFreePageMargin = 131072, maximumDllBytes = 33554432UL,
                aggregateDllEnvelopeBytes = 536870912UL, nativeSourceRevision = "revision",
                nativeCodecHeaderSha256 = new string('a', 64)
            };
        }

        private static ShadowPatchMetadataCapacityReport2 Report2(ShadowPatchMetadataEncodingProfile2 profile, int count)
        {
            return new ShadowPatchMetadataCapacityReport2 {
                schemaVersion = 2, profileVersion = 2, nativeBudgetCapabilityVersion = 2,
                nativeSourceRevision = profile.nativeSourceRevision, nativeCodecHeaderSha256 = profile.nativeCodecHeaderSha256,
                codecId = profile.codecId, codecBits = profile.codecBits, invalidIndexSentinel = profile.invalidIndexSentinel,
                aotMaxIndex = profile.aotMaxIndex, minImageId = profile.minImageId, maximumImageCount = profile.maximumImageCount,
                maximumDllBytes = profile.maximumDllBytes, usablePageCapacity = profile.usablePageCapacity,
                chargedPageCeiling = profile.chargedPageCeiling, minimumFreePageMargin = profile.minimumFreePageMargin,
                requiredImages = count, acceptedImages = count, admissionAccepted = true, fitsPreliminary = true,
                finalPageFitKnown = false, runtimeFinalizationRequired = true, aggregateInputDllBytesInformational = true,
                firstFailingIndex = -1, failureReason = "None"
            };
        }

        private static byte[] Encode(string mode, bool ordinary)
        {
            using (var stream = new MemoryStream())
            using (var writer = new BinaryWriter(stream, new UTF8Encoding(false), true))
            {
                writer.Write(Encoding.ASCII.GetBytes("R01EARLY")); writer.Write(1);
                String(writer, mode); String(writer, "baseline"); String(writer, new string('a', 64)); String(writer, "patch");
                Strings(writer, new[] { "AssemblyZ.Contracts", "AssemblyA.Contracts" }); Strings(writer, new[] { "mscorlib" });
                writer.Write(2); String(writer, "AssemblyZ.Contracts"); String(writer, "/tmp/z.dll"); writer.Write(3L); String(writer, new string('b', 64));
                String(writer, ""); writer.Write(0L); String(writer, "");
                String(writer, "AssemblyA.Contracts"); String(writer, "/tmp/a.dll"); writer.Write(3L); String(writer, new string('d', 64));
                String(writer, ""); writer.Write(0L); String(writer, "");
                if (ordinary) { String(writer, "/tmp/ordinary.dll.bytes"); String(writer, R01EarlyStartup.FixedOrdinarySha256); }
                else { String(writer, ""); String(writer, ""); }
                writer.Write(1); String(writer, "/tmp/resource.bundle"); writer.Write(17L); String(writer, new string('c', 64));
                writer.Flush(); return stream.ToArray();
            }
        }

        private static void Strings(BinaryWriter writer, string[] values)
        {
            writer.Write(values.Length); foreach (string value in values) String(writer, value);
        }

        private static void String(BinaryWriter writer, string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value); writer.Write(bytes.Length); writer.Write(bytes);
        }
    }
}
