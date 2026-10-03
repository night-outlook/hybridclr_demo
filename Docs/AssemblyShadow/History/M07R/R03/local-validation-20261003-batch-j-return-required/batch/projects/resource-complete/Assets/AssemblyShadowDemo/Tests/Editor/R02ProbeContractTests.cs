using NUnit.Framework;
using UnityEngine;
namespace AssemblyShadowDemo.Tests
{
    public class R02ProbeContractTests
    {
        [Test] public void FormulaMatchesIndependentLoop()
        {
            foreach (int n in new[] { 1, 10, 100, 1000, 10000 })
                foreach (int marker in new[] { 3000, 3001, 3003 })
                { long sum = 0; for (int i = 0; i < n; ++i) sum += (3017 + i) * 17L + marker;
                  Assert.AreEqual(sum, R02PlayerProbe.Expected(n, 3017, marker)); }
        }
        [Test] public void JsonPreservesNestedRawDiagnosticsAndLargeIntegers()
        {
            var row = new R02PlayerProbe.Row { checksum = 9007199254740993L, before = new R02PlayerProbe.Snapshot {
                executionJson = "{\"r02\":{\"admissionCacheHits\":10000}}", currentRssBytes = 244596736, utcTicks = 639000000000000000L } };
            var restored = JsonUtility.FromJson<R02PlayerProbe.Row>(JsonUtility.ToJson(row));
            Assert.AreEqual(row.checksum, restored.checksum); Assert.AreEqual(row.before.executionJson, restored.before.executionJson);
            Assert.AreEqual(row.before.utcTicks, restored.before.utcTicks); Assert.AreEqual(row.before.currentRssBytes, restored.before.currentRssBytes);
        }
    }
}
