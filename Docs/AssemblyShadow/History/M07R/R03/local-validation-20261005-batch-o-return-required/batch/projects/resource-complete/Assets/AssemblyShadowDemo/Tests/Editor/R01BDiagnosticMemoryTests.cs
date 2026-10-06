using System;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01BDiagnosticMemoryTests
    {
#if UNITY_EDITOR_OSX
        [Test]
        public void MachCaptureUsesNativeLayoutAndReportsResidentAndPeakBytes()
        {
            Assembly assembly = AppDomain.CurrentDomain.GetAssemblies().Single(item => item.GetName().Name == "AssemblyShadow.R01BDiagnostics");
            Type provider = assembly.GetType("AssemblyShadowDemo.R01BProcessMemory", true);
            Type native = provider.GetNestedType("MachTaskBasicInfo", BindingFlags.NonPublic);
            Assert.AreEqual(48, Marshal.SizeOf(native));
            MethodInfo capture = provider.GetMethod("Capture", BindingFlags.Public | BindingFlags.Static);
            object first = capture.Invoke(null, null);
            object second = capture.Invoke(null, null);
            Type sample = first.GetType();
            long firstResident = (long)sample.GetField("ResidentBytes").GetValue(first);
            long firstPeak = (long)sample.GetField("PeakResidentBytes").GetValue(first);
            long secondResident = (long)sample.GetField("ResidentBytes").GetValue(second);
            long secondPeak = (long)sample.GetField("PeakResidentBytes").GetValue(second);
            Assert.Greater(firstResident, 0);
            Assert.Greater(secondResident, 0);
            Assert.GreaterOrEqual(firstPeak, firstResident);
            Assert.GreaterOrEqual(secondPeak, secondResident);
            Assert.GreaterOrEqual(secondPeak, firstPeak);
        }
#endif
    }
}
