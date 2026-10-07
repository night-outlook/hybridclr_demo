using System;
using NUnit.Framework;
using AssemblyShadowDemo.Editor;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class H1PchEvidenceProcessTests
    {
        [TestCase(0)]
        [TestCase(999)]
        [TestCase(1800001)]
        public void InvalidTimeoutFailsBeforeStartingAnyProcess(int timeout)
        {
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                H1EvidenceProcess.RunPythonWithTimeout("unused", "unused", timeout));
        }

        [Test]
        public void CompilerReceiptPreservesPchSidecarFields()
        {
            var capture = new H1CompilerProvenance.Capture {
                schemaVersion = 1, projectRoot = "/fixture", pchProofPath = "/fixture/pch-proof.json",
                pchProofSha256 = new string('a', 64)
            };
            var roundTrip = UnityEngine.JsonUtility.FromJson<H1CompilerProvenance.Capture>(
                UnityEngine.JsonUtility.ToJson(capture));
            Assert.AreEqual(capture.projectRoot, roundTrip.projectRoot);
            Assert.AreEqual(capture.pchProofPath, roundTrip.pchProofPath);
            Assert.AreEqual(capture.pchProofSha256, roundTrip.pchProofSha256);
        }
    }
}
