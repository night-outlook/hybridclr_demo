using System;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01MetadataProfile2MigrationTests
    {
        private const string Profile2Empty = "{\"schemaVersion\":2,\"enabled\":true,\"profileVersion\":2,\"maximumImageCount\":8192,\"maximumDllBytes\":33554432,\"usablePageCapacity\":524287,\"chargedPageCeiling\":393215,\"minimumFreePageMargin\":131072,\"reservedPages\":0,\"mappedPages\":0,\"lifetimeReservedImageCount\":0,\"remainingImageCount\":8192,\"requiredImages\":0,\"acceptedImages\":0,\"firstFailingIndex\":-1,\"firstFailingSize\":0,\"failureReason\":\"None\",\"fitsPreliminary\":true,\"runtimeFinalizationRequired\":true,\"aggregateInputDllBytes\":0,\"aggregateInputDllBytesInformational\":true,\"ordinaryAllocatedCount\":0,\"shadowAllocatedCount\":0,\"reservedShadowImageCount\":0}";

        [Test]
        public void ManagedR01ParserAcceptsActualProfile2WireShape()
        {
            object value = Parse(Profile2Empty);
            Assert.AreEqual(2, Get<int>(value, "profileVersion"));
            Assert.IsTrue(Get<bool>(value, "fits"));
            Assert.AreEqual((ulong)0, Get<ulong>(value, "acceptedImages"));
            Assert.AreEqual((ulong)8192, Get<ulong>(value, "remainingImageCount"));
        }

        [Test]
        public void Profile2ObservationUsesDeliberateEmptyLegacyArraysInUnityJson()
        {
            var observation = new M07R01Probe.CapacityObservation {
                profileVersion = 2, fits = true, fitsPreliminary = true,
                cursors = new uint[0], finalCursors = new uint[0], remainingSlots = new uint[0],
                reservedImageCount = 0, requiredImages = 1, acceptedImages = 1,
                reservedPages = 1, mappedPages = 0, lifetimeReservedImageCount = 1,
                remainingImageCount = 8191, reservedShadowImageCount = 1
            };
            string json = JsonUtility.ToJson(observation);
            M07R01Probe.CapacityObservation roundTrip = JsonUtility.FromJson<M07R01Probe.CapacityObservation>(json);
            Assert.NotNull(roundTrip.cursors);
            Assert.NotNull(roundTrip.finalCursors);
            Assert.NotNull(roundTrip.remainingSlots);
            Assert.AreEqual(0, roundTrip.cursors.Length);
            Assert.AreEqual(0, roundTrip.finalCursors.Length);
            Assert.AreEqual(0, roundTrip.remainingSlots.Length);
            StringAssert.Contains("\"fitsPreliminary\":true", json);
            StringAssert.Contains("\"reservedPages\":1", json);
        }

        [Test]
        public void Profile2OversizeUsesAtomicZeroAcceptedImages()
        {
            string rejected = Profile2Empty
                .Replace("\"requiredImages\":0", "\"requiredImages\":2")
                .Replace("\"firstFailingIndex\":-1", "\"firstFailingIndex\":1")
                .Replace("\"firstFailingSize\":0", "\"firstFailingSize\":33554433")
                .Replace("\"failureReason\":\"None\"", "\"failureReason\":\"DllTooLarge\"")
                .Replace("\"fitsPreliminary\":true", "\"fitsPreliminary\":false");
            object value = Parse(rejected);
            Assert.IsTrue((bool)Invoke(value, "IsOversizeFailure", 1, (ulong)33554433));
            Assert.AreEqual((ulong)0, Get<ulong>(value, "acceptedImages"));
        }

        [Test]
        public void FailedProfile2ReserveDetectsEveryChangedSharedLedgerField()
        {
            object before = Parse(Profile2Empty);
            object after = Parse(Profile2Empty);
            Assert.IsTrue((bool)Invoke(before, "SameAtomicState", after));
            foreach (string field in new[] { "reservedPages", "mappedPages", "lifetimeReservedImageCount", "remainingImageCount", "reservedShadowImageCount", "ordinaryAllocatedCount", "shadowAllocatedCount" })
            {
                after = Parse(Profile2Empty);
                Set(after, field, (ulong)1);
                Assert.IsFalse((bool)Invoke(before, "SameAtomicState", after), field + " mutation was not detected.");
            }
        }

        [Test]
        public void UnknownOrMalformedProfile2DoesNotFallBackToProfile1()
        {
            Assert.Throws<FormatException>(() => Parse(Profile2Empty.Replace("\"maximumImageCount\":8192,", "\"unknownCapacityField\":1,")));
            Assert.Throws<FormatException>(() => Parse(Profile2Empty.Replace("\"remainingImageCount\":8192", "\"remainingImageCount\":8191")));
        }

        private static Type SnapshotType
        {
            get { return typeof(R01EarlyStartup).Assembly.GetType("AssemblyShadowDemo.R01MetadataCapacitySnapshot", true); }
        }

        private static object Parse(string json)
        {
            try
            {
                return SnapshotType.GetMethod("Parse", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic).Invoke(null, new object[] { json, 2 });
            }
            catch (TargetInvocationException error)
            {
                throw error.InnerException ?? error;
            }
        }

        private static object Invoke(object instance, string name, params object[] args)
        {
            return SnapshotType.GetMethod(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).Invoke(instance, args);
        }

        private static T Get<T>(object instance, string name)
        {
            return (T)SnapshotType.GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).GetValue(instance);
        }

        private static void Set<T>(object instance, string name, T value)
        {
            SnapshotType.GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).SetValue(instance, value);
        }
    }
}
