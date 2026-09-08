using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07R00PerformanceProbeTests
    {
        [Test]
        public void ReadinessPreservesOriginalProbeInvocationAndOrdersItsTimestamps()
        {
            MethodInfo capture = typeof(M07R00PerformanceProbe).GetMethod("CaptureReadiness", BindingFlags.Static | BindingFlags.NonPublic);
            long invokedUtc = DateTime.UtcNow.AddSeconds(-1).Ticks;
            var first = (M07R00PerformanceProbe.ReadinessObservation)capture.Invoke(null, new object[] { 123L, invokedUtc, false });
            var ready = (M07R00PerformanceProbe.ReadinessObservation)capture.Invoke(null, new object[] { 123L, invokedUtc, true });
            Assert.AreEqual(invokedUtc, first.probeInvocationUtcTicks);
            Assert.AreEqual(invokedUtc, ready.probeInvocationUtcTicks);
            Assert.AreEqual(0, first.businessReadyUtcTicks);
            Assert.Greater(ready.businessReadyUtcTicks, ready.probeInvocationUtcTicks);
            Assert.AreEqual(first.invocationTimestamp, ready.invocationTimestamp);
        }

        private const string ProbeSource = "Assets/AssemblyShadowDemo/Bootstrap/M07R00PerformanceProbe.cs";
        private const string WitnessSource = "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/R00PerformanceWitness.cs";
        private const string M07Source = "Assets/AssemblyShadowDemo/Bootstrap/M07Probe.cs";

        [Test]
        public void M07ProbeIsOnlyMadePartialForTheR00Companion()
        {
            string source = File.ReadAllText(M07Source);
            StringAssert.Contains("public static partial class M07Probe", source);
            Assert.AreEqual(1, source.Split(new[] { "public static partial class M07Probe" }, StringSplitOptions.None).Length - 1);
        }

        [Test]
        public void R00HasFourExplicitWorldsAndUsesM07InputAndTransactionBoundaries()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string mode in new[] { "R00-ON-NoPatch", "R00-ON-P01", "R00-ON-P03", "R00-OFF-NoPatch" })
                StringAssert.Contains("\"" + mode + "\"", source);
            StringAssert.Contains("M07Probe.R00ReadInputs", source);
            StringAssert.Contains("M07Probe.R00RunTransaction", source);
            StringAssert.Contains("ReadInputs(baseline, runtimeAbi, mode)", source);
            StringAssert.Contains("RunTransaction(result, input)", source);
            StringAssert.Contains("M07Probe.HashFile", source);
            StringAssert.Contains("-shadowR00Mode", source);
            StringAssert.Contains("-shadowR00Result", source);
            Assert.IsFalse(source.Contains("M07ResourceProbe.Run"), "R00 must not silently claim the M07 resource matrix.");
        }

        [Test]
        public void R00ResultIsDistinctAndFailsClosedOnExistingOutputOrRealErrors()
        {
            string source = File.ReadAllText(ProbeSource);
            StringAssert.Contains("milestone = \"M07R-R00\"", source);
            StringAssert.Contains("FileMode.CreateNew", source);
            StringAssert.Contains("result.result = \"Failed\"", source);
            StringAssert.Contains("CompleteCoroutineFailure", source);
            Assert.IsFalse(source.Contains("FileMode.Create, "), "R00 output must refuse replacement writes.");
            Assert.IsFalse(source.Contains("GetAllocatedBytesForCurrentThread"));
            Assert.IsFalse(source.Contains("GC.GetTotalMemory"));
        }

        [Test]
        public void DiagnosticsDeclareUnavailableNativePerformanceCounters()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string field in new[] { "proofBuildCount", "typeRowsScanned", "nativeAllocationCount" })
                StringAssert.Contains(field + " = \"unavailable\"", source);
            StringAssert.Contains("diagnosticsOnly = true", source);
            StringAssert.Contains("diagnosticsBefore", source);
            StringAssert.Contains("diagnosticsAfter", source);
        }

        [Test]
        public void WitnessIsPureManagedAndHasConditionalMarkersFreshPayloadsAndMeasuredOperations()
        {
            string source = File.ReadAllText(WitnessSource);
            StringAssert.Contains("#if ASSEMBLY_SHADOW_P03", source);
            StringAssert.Contains("#elif ASSEMBLY_SHADOW_P01", source);
            StringAssert.Contains("new R00PerformancePayload", source);
            StringAssert.Contains("ConstructorCount", source);
            StringAssert.Contains("RunAllocationBatch", source);
            StringAssert.Contains("InvokeStep", source);
            StringAssert.Contains("ClosedGeneric<T>", source);
            Assert.IsFalse(source.Contains("GameObject"));
            Assert.IsFalse(source.Contains("UnityEngine.Object"));
        }

        [Test]
        public void R00MeasuresActualCountsAndChecksumsAtRequiredBoundaries()
        {
            string source = File.ReadAllText(ProbeSource);
            foreach (string token in new[] { "requestedIterations", "actualNewCount", "actualInvocationCount", "checksum", "expectedChecksum", "stopwatchFrequency" })
                StringAssert.Contains(token, source);
            foreach (string phase in new[] { "\"first\"", "\"warmup\"", "\"repeat10\"", "\"repeat10000\"" })
                StringAssert.Contains(phase, source);
            foreach (string operation in new[] { "\"allocation\"", "\"reflectionInvoke\"", "\"closedGeneric\"" })
                StringAssert.Contains(operation, source);
            StringAssert.Contains("actual == count", source);
            StringAssert.Contains("checksum == expected", source);
        }
    }
}
