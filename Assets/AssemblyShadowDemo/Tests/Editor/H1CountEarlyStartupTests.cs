using System;
using System.IO;
using System.Linq;
using System.Text;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class H1CountEarlyStartupTests
    {
        [Test]
        public void OrdinaryGatewayReturnsWithoutNativeCallsOrReceipt()
        {
            Assert.AreEqual(0, H1CountEarlyStartup.RunArguments(new[] { "player", "-shadowH1Path", "ordinary" }));
            Assert.IsNull(H1CountEarlyStartup.LastReceiptJson);
            Assert.IsNull(H1CountEarlyStartup.LastReceipt);
        }

        [Test]
        public void MissingOrDuplicatePathFailsClosed()
        {
            Assert.AreEqual(2, H1CountEarlyStartup.RunArguments(new[] { "player" }));
            Assert.AreEqual(2, H1CountEarlyStartup.RunArguments(new[] { "-shadowH1Path", "ordinary", "-shadowH1Path", "ordinary" }));
        }

        [Test]
        public void ArgumentsValidateOutcomeCountHashAndDuplicates()
        {
            string[] args = Arguments();
            var parsed = H1CountEarlyStartup.Arguments.Read(args);
            Assert.AreEqual(65536, parsed.expectedCount);
            Assert.AreEqual("ControlledRejected", parsed.expectedOutcome);
            Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.Arguments.Read(Replace(args, "65536", "65538")));
            Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.Arguments.Read(Replace(args, "ControlledRejected", "Passed")));
            Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.Arguments.Read(Replace(args, new string('a', 64), "bad")));
            Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.Arguments.Read(args.Concat(new[] { "-shadowH1Case", "H1R-P03-a" }).ToArray()));
        }

        [Test]
        public void ReceiptCodecEscapesNativeJsonAndAuthenticatesAllFields()
        {
            var receipt = new H1CountEarlyStartup.Receipt { caseId = "H1R-P03-a", expectedCount = 65536 };
            receipt.snapshots.Add(new H1CountEarlyStartup.SnapshotReceipt {
                phase = "after-validate", nativeCode = "Success", nativeJson = "{\"quoted\":\"slash\\line\n\"}",
                diagnosticsCode = "Success", diagnosticsJson = "{\"detail\":\"BaselineAlreadyUsed\"}"
            });
            string canonical = H1CountEarlyStartup.ReceiptCodec.Serialize(receipt);
            string authenticated = H1CountEarlyStartup.ReceiptCodec.Authenticate(receipt);
            Assert.AreEqual(H1CountEarlyStartup.Sha256(Encoding.UTF8.GetBytes(canonical)), receipt.receiptSha256);
            Assert.IsTrue(H1CountEarlyStartup.ReceiptCodec.VerifySerialized(authenticated, receipt.receiptSha256));
            Assert.IsFalse(H1CountEarlyStartup.ReceiptCodec.VerifySerialized(authenticated + "\n", receipt.receiptSha256));
            Assert.IsFalse(H1CountEarlyStartup.ReceiptCodec.VerifySerialized(
                authenticated.Replace("65536", "65537"), receipt.receiptSha256));
            StringAssert.Contains("\\\"quoted\\\"", authenticated);
            StringAssert.Contains("\\\\line\\n", authenticated);
            StringAssert.Contains("\"expectedCount\":65536", authenticated);
            string digest = receipt.receiptSha256;
            receipt.expectedCount++;
            H1CountEarlyStartup.ReceiptCodec.Authenticate(receipt);
            Assert.AreNotEqual(digest, receipt.receiptSha256);
        }

        [Test]
        public void EmptyAndOversizedFilesAreRejectedBeforeAllocation()
        {
            string path = Path.GetTempFileName();
            try
            {
                Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.ReadFixture(path));
                using (var stream = new FileStream(path, FileMode.Open, FileAccess.Write)) stream.SetLength(H1CountEarlyStartup.MaxFixtureBytes + 1);
                Assert.Throws<InvalidDataException>(() => H1CountEarlyStartup.ReadFixture(path));
            }
            finally { File.Delete(path); }
        }

        [Test]
        public void StartupSourceAndBuildKeepThePreCatalogContract()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/H1CountEarlyStartup.cs");
            foreach (string forbidden in new[] { "JsonUtility", "Application.", "Debug.Log", "ManifestModule",
                "GetManifestModuleInternal", "Type.GetType", "GetMethod(\"Run\")", "method.Invoke", "AbortTransaction(" })
                StringAssert.DoesNotContain(forbidden, source);
            StringAssert.Contains("Assembly.Load(bytes)", source);
            StringAssert.Contains("BaselineAlreadyUsed", source);
            StringAssert.Contains("ReserveMetadataBudget(new[] { bytes.LongLength }, 2)", source);
            string build = File.ReadAllText("Assets/AssemblyShadowDemo/Editor/H1CountDiagnosticBuild.cs");
            StringAssert.Contains("settings.startupBootstrapAssembly = \"AssemblyShadowDemo.Bootstrap\"", build);
            StringAssert.Contains("settings.startupBootstrapType = \"H1CountEarlyStartup\"", build);
            StringAssert.Contains("settings.startupBootstrapMethod = \"Run\"", build);
        }

        private static string[] Replace(string[] args, string from, string to) { return args.Select(s => s == from ? to : s).ToArray(); }
        private static string[] Arguments()
        {
            return new[] { "-shadowH1Path", "shadow", "-shadowH1EarlyResult", "/tmp/new-h1-early.json",
                "-shadowH1Family", "parameters", "-shadowH1Case", "H1R-P03-a", "-shadowH1Fixture", "/tmp/fixture.dll",
                "-shadowH1FixtureSha256", new string('a', 64), "-shadowH1BaselineBuildId", "H1Count-On-Release",
                "-shadowH1RuntimeAbiHash", new string('b', 64), "-shadowH1ExpectedOutcome", "ControlledRejected",
                "-shadowH1ExpectedCount", "65536" };
        }
    }
}
