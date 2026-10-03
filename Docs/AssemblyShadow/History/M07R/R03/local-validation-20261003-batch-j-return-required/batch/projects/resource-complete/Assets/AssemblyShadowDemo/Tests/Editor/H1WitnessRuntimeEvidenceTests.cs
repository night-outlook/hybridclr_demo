using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class H1WitnessRuntimeEvidenceTests
    {
        [Test]
        public void DedicatedWitnessNegativeEvidenceSurvivesSerialization()
        {
            var value = new H1WitnessGuardRuntimeProbe.Result {
                result = "Passed", configurationSha256 = new string('a', 64), configurationHash = new string('b', 64),
                guardName = "test-only", imageSha256 = new string('c', 64),
                tamperRejected = true, nullRejected = true, callerBytesUnchanged = true, assemblyResolveEvents = 0
            };
            var copy = JsonUtility.FromJson<H1WitnessGuardRuntimeProbe.Result>(JsonUtility.ToJson(value));
            Assert.That(copy.tamperRejected && copy.nullRejected, Is.True);
            Assert.That(copy.callerBytesUnchanged, Is.True);
            Assert.That(copy.guardName, Is.EqualTo("test-only"));
            Assert.That(copy.assemblyResolveEvents, Is.EqualTo(0));
            Assert.That(copy.humanGatePassed || copy.mayEnterR02, Is.False);
        }

        [Test]
        public void HistoricalOrIncompleteResultDoesNotDefaultToWitnessPass()
        {
            var copy = JsonUtility.FromJson<H1WitnessGuardRuntimeProbe.Result>("{\"result\":\"Passed\"}");
            Assert.That(copy.tamperRejected, Is.False);
            Assert.That(copy.nullRejected, Is.False);
            Assert.That(copy.callerBytesUnchanged, Is.False);
            Assert.That(copy.guardName, Is.Null.Or.Empty);
        }
    }
}
