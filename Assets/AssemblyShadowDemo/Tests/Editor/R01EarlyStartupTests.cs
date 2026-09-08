using System;
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
