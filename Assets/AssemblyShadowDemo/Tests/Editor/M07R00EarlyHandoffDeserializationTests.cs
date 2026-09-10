using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07R00EarlyHandoffDeserializationTests
    {
        private static readonly string[] P01Closure = { "AssemblyA.Implementation.Internal" };
        private static readonly string[] P03Closure = {
            "AssemblyA.Contracts", "AssemblyA.Implementation.Extensibility", "AssemblyA.Implementation.Internal",
            "AssemblyShadowDemo.ContractsConsumer", "AssemblyShadowDemo.ExtensibilityConsumer"
        };

        [Test]
        public void ActualReceiptCodecOutputUsesTheR00UnityParserForBaselineP01AndP03()
        {
            AssertBaseline(Receipt("Baseline", "P03", new string[0]));
            AssertControl(Receipt("Control", "P01", P01Closure), P01Closure);
            AssertControl(Receipt("Control", "P03", P03Closure), P03Closure);
        }

        [Test]
        public void R00ValidatorsRejectNullMissingReorderedWrongIdentityAndNonSuccessRows()
        {
            object nullReceipt = null;
            Assert.IsFalse(Invoke("HasExpectedReceiptIdentity", nullReceipt, IdentityArguments("Baseline")));
            Assert.IsFalse(Invoke("HasExactBaselineReceipt", nullReceipt));

            object missingOperations = Parse(Receipt("Control", "P01", P01Closure));
            SetField(missingOperations, "operations", null);
            Assert.IsFalse(HasExactOperations(missingOperations, P01Closure));

            object missingSnapshots = Parse(Receipt("Baseline", "P03", new string[0]));
            SetField(missingSnapshots, "snapshots", null);
            Assert.IsFalse(Invoke("HasExactBaselineReceipt", missingSnapshots));

            object missingRow = Parse(Receipt("Control", "P03", P03Closure));
            Array rows = (Array)GetField(missingRow, "operations");
            Array fewer = Array.CreateInstance(rows.GetType().GetElementType(), rows.Length - 1);
            Array.Copy(rows, fewer, fewer.Length);
            SetField(missingRow, "operations", fewer);
            Assert.IsFalse(HasExactOperations(missingRow, P03Closure));

            object reordered = Parse(Receipt("Control", "P03", P03Closure));
            rows = (Array)GetField(reordered, "operations");
            object firstStage = rows.GetValue(3);
            rows.SetValue(rows.GetValue(4), 3);
            rows.SetValue(firstStage, 4);
            Assert.IsFalse(HasExactOperations(reordered, P03Closure));

            object nonSuccess = Parse(Receipt("Control", "P01", P01Closure));
            object reserve = ((Array)GetField(nonSuccess, "operations")).GetValue(2);
            SetField(reserve, "code", "MetadataCapacityExceeded");
            SetField(reserve, "intCode", 3);
            Assert.IsFalse(HasExactOperations(nonSuccess, P01Closure));

            object wrongPid = Parse(Receipt("Control", "P01", P01Closure));
            SetField(wrongPid, "processId", 42);
            Assert.IsFalse(HasExpectedIdentity(wrongPid, "Control"));
        }

        [Test]
        public void ProbeUsesPrivateSerializableProjectionInsteadOfFrameworkReceiptType()
        {
            const string path = "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs";
            string source = File.ReadAllText(path);
            StringAssert.Contains("JsonUtility.FromJson<EarlyReceipt>", source);
            StringAssert.DoesNotContain("JsonUtility.FromJson<R01EarlyStartup.Receipt>", source);
            StringAssert.Contains("[Serializable, Preserve] private sealed class EarlyReceipt", source);
            StringAssert.Contains("[Serializable, Preserve] private sealed class EarlyOperation", source);
            StringAssert.Contains("[Serializable, Preserve] private sealed class EarlySnapshot", source);
        }

        private static void AssertBaseline(R01EarlyStartup.Receipt receipt)
        {
            object parsed = Parse(receipt);
            Assert.AreEqual("Baseline", GetField(parsed, "mode"));
            Assert.IsTrue(HasExpectedIdentity(parsed, "Baseline"));
            Assert.IsTrue((bool)Invoke("HasExactBaselineReceipt", parsed));
            Assert.AreEqual(0, ((Array)GetField(parsed, "operations")).Length);
        }

        private static void AssertControl(R01EarlyStartup.Receipt receipt, string[] closure)
        {
            object parsed = Parse(receipt);
            Assert.AreEqual("Control", GetField(parsed, "mode"));
            Assert.IsTrue(HasExpectedIdentity(parsed, "Control"));
            Assert.IsTrue(HasExactOperations(parsed, closure));
        }

        private static object Parse(R01EarlyStartup.Receipt receipt)
        {
            string raw = R01EarlyStartup.ReceiptCodec.Serialize(receipt);
            MethodInfo parser = typeof(M07R00PerformanceProbe).GetMethod("ParseEarlyReceipt", BindingFlags.Static | BindingFlags.NonPublic);
            Assert.NotNull(parser);
            return parser.Invoke(null, new object[] { raw });
        }

        private static bool HasExpectedIdentity(object receipt, string mode)
        {
            return Invoke("HasExpectedReceiptIdentity", receipt, IdentityArguments(mode));
        }

        private static object[] IdentityArguments(string mode)
        {
            return new object[] { mode, "/tmp/r00.capsule", new string('a', 64), "/tmp/r00.json", "baseline", new string('b', 64), 41, 7 };
        }

        private static bool HasExactOperations(object receipt, string[] closure)
        {
            MethodInfo validator = typeof(M07R00PerformanceProbe).GetMethod("HasExactSuccessfulOperations", BindingFlags.Static | BindingFlags.NonPublic);
            Assert.NotNull(validator);
            return (bool)validator.Invoke(null, new[] { GetField(receipt, "operations"), closure });
        }

        private static bool Invoke(string name, object receipt, params object[] arguments)
        {
            MethodInfo method = typeof(M07R00PerformanceProbe).GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic);
            Assert.NotNull(method);
            object[] values = new object[arguments.Length + 1];
            values[0] = receipt;
            Array.Copy(arguments, 0, values, 1, arguments.Length);
            return (bool)method.Invoke(null, values);
        }

        private static object GetField(object target, string name)
        {
            return target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.Public).GetValue(target);
        }

        private static void SetField(object target, string name, object value)
        {
            target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.Public).SetValue(target, value);
        }

        private static R01EarlyStartup.Receipt Receipt(string mode, string patchId, string[] closure)
        {
            var receipt = new R01EarlyStartup.Receipt {
                mode = mode, patchId = patchId, result = "Passed", error = "", callbackReturnCode = 0,
                processId = 41, managedThreadId = 7, capsulePath = "/tmp/r00.capsule", capsuleSha256 = new string('a', 64),
                resultPath = "/tmp/r00.json", baselineBuildId = "baseline", runtimeAbiHash = new string('b', 64),
                operations = new System.Collections.Generic.List<R01EarlyStartup.OperationReceipt>(),
                snapshots = new System.Collections.Generic.List<R01EarlyStartup.SnapshotReceipt>()
            };
            if (mode == "Baseline")
            {
                receipt.snapshots.Add(new R01EarlyStartup.SnapshotReceipt { phase = "before-startup-ops" });
                return receipt;
            }
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "configure", code = "Success", intCode = 0 });
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "begin", code = "Success", intCode = 0 });
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "reserve", code = "Success", intCode = 0 });
            foreach (string name in closure)
                receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "stage:" + name, code = "Success", intCode = 0 });
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "validate", code = "Success", intCode = 0 });
            receipt.operations.Add(new R01EarlyStartup.OperationReceipt { phase = "commit", code = "Success", intCode = 0 });
            return receipt;
        }
    }
}
