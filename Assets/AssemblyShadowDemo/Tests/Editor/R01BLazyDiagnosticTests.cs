using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class R01BLazyDiagnosticTests
    {
        private const string DiagnosticsAssembly = "AssemblyShadow.R01BDiagnostics";

        [Test]
        public void LifetimeImageDeltaAcceptsOneLoadThenStableMetadata()
        {
            Type probe = ProbeType();
            FieldInfo active = PrivateField(probe, "active");
            object result = NewResult(probe);
            AddSnapshot(probe, result, 10);
            AddSnapshot(probe, result, 11);
            AddSnapshot(probe, result, 11);
            WithActive(active, result, delegate {
                Assert.IsTrue(CallBool(probe, "ImageDelta", (ulong)1));
                Assert.IsTrue(CallBool(probe, "LifetimeImageDelta", (ulong)1));
            });
        }

        [Test]
        public void LifetimeImageDeltaRejectsAnExtraLazyImage()
        {
            Type probe = ProbeType();
            FieldInfo active = PrivateField(probe, "active");
            object result = NewResult(probe);
            AddSnapshot(probe, result, 10);
            AddSnapshot(probe, result, 11);
            AddSnapshot(probe, result, 12);
            WithActive(active, result, delegate {
                Assert.IsFalse(CallBool(probe, "LifetimeImageDelta", (ulong)1));
            });
        }

        [Test]
        public void ImageDeltaRejectsTheWrongInitialReservationDelta()
        {
            Type probe = ProbeType();
            FieldInfo active = PrivateField(probe, "active");
            object result = NewResult(probe);
            AddSnapshot(probe, result, 10);
            AddSnapshot(probe, result, 12);
            WithActive(active, result, delegate {
                Assert.IsFalse(CallBool(probe, "ImageDelta", (ulong)1));
                Assert.IsTrue(CallBool(probe, "ImageDelta", (ulong)2));
                Assert.IsFalse(CallBool(probe, "LifetimeImageDelta", (ulong)1));
            });
        }

        [Test]
        public void DenseManifestAcceptsHistoricalV1AndDeterministicV2Only()
        {
            Type probe = ProbeType();
            Type manifestType = probe.GetNestedType("DenseManifest", BindingFlags.NonPublic);
            Type fixtureType = probe.GetNestedType("DenseFixture", BindingFlags.NonPublic);
            MethodInfo accepted = PrivateMethod(probe, "IsAcceptedDenseManifestContract", manifestType);

            object v1 = DenseManifest(manifestType, fixtureType, 1,
                "R01BWorkloadV3DenseMetadataAdjunct", "VerifiedSealedV1FixturesOutsideV2Envelope", false);
            Assert.IsTrue((bool)accepted.Invoke(null, new[] { v1 }));

            object v2 = DenseManifest(manifestType, fixtureType, 2,
                "R01BDenseAdjunctManifest", "GeneratedDeterministicDenseV2", false);
            Assert.IsTrue((bool)accepted.Invoke(null, new[] { v2 }));

            object relabelled = DenseManifest(manifestType, fixtureType, 2,
                "R01BDenseAdjunctManifest", "GeneratedDeterministicDenseV2", true);
            Assert.IsFalse((bool)accepted.Invoke(null, new[] { relabelled }));

            object wrongKind = DenseManifest(manifestType, fixtureType, 2,
                "R01BWorkloadV3DenseMetadataAdjunct", "GeneratedDeterministicDenseV2", false);
            Assert.IsFalse((bool)accepted.Invoke(null, new[] { wrongKind }));
        }

        [Test]
        public void DenseV2FixtureRequiresExactGeneratedBoundaryEnvelope()
        {
            Type probe = ProbeType();
            Type manifestType = probe.GetNestedType("DenseManifest", BindingFlags.NonPublic);
            Type fixtureType = probe.GetNestedType("DenseFixture", BindingFlags.NonPublic);
            object manifest = DenseManifest(manifestType, fixtureType, 2,
                "R01BDenseAdjunctManifest", "GeneratedDeterministicDenseV2", false);
            object fixture = DenseFixture(fixtureType, 1, 4098, 4097, 70000, 1024L * 1024L);
            MethodInfo accepted = PrivateMethod(probe, "IsAcceptedDenseFixtureContract",
                manifestType, fixtureType, typeof(long));

            Assert.IsTrue((bool)accepted.Invoke(null, new[] { manifest, fixture, (object)(1024L * 1024L) }));

            fixtureType.GetField("stringsHeapBytes", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .SetValue(fixture, 65535);
            Assert.IsFalse((bool)accepted.Invoke(null, new[] { manifest, fixture, (object)(1024L * 1024L) }));

            fixture = DenseFixture(fixtureType, 1, 4098, 4097, 70000, 1024L * 1024L);
            Assert.IsFalse((bool)accepted.Invoke(null, new[] { manifest, fixture, (object)(1024L * 1024L - 1) }));
        }

        [Test]
        public void DenseBoundaryIdentityMatchesGeneratorContract()
        {
            Type probe = ProbeType();
            MethodInfo typeName = PrivateMethod(probe, "DenseTypeName", typeof(int), typeof(int));
            MethodInfo returnId = PrivateMethod(probe, "DenseReturnId", typeof(int), typeof(int));

            Assert.AreEqual(
                "AssemblyShadow.Dense.DenseType_0001_4095_MetadataBoundary_0123456789abcdef0123456789abcdef",
                typeName.Invoke(null, new object[] { 1, 4095 }));
            Assert.AreEqual(14095, returnId.Invoke(null, new object[] { 1, 4095 }));
            Assert.AreEqual(
                "AssemblyShadow.Dense.DenseType_0002_4096_MetadataBoundary_0123456789abcdef0123456789abcdef",
                typeName.Invoke(null, new object[] { 2, 4096 }));
            Assert.AreEqual(24096, returnId.Invoke(null, new object[] { 2, 4096 }));
        }

        [Test]
        public void RepeatedFixtureInvokeChecksUseUniqueNames()
        {
            Type probe = ProbeType();
            FieldInfo active = PrivateField(probe, "active");
            object result = NewResult(probe);
            Type box = typeof(EchoFixture<int>);
            MethodInfo invoke = PrivateMethod(probe, "Invoke", typeof(Type), typeof(string), typeof(object[]));
            WithActive(active, result, delegate {
                Assert.AreEqual(13, invoke.Invoke(null, new object[] { box, "Echo", new object[] { 13 } }));
                Assert.AreEqual(17, invoke.Invoke(null, new object[] { box, "Echo", new object[] { 17 } }));
                Assert.AreEqual(19, invoke.Invoke(null, new object[] { box, "Echo", new object[] { 19 } }));
                IList checks = (IList)PrivateField(probe, "active").GetValue(null).GetType().GetField("checks", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).GetValue(result);
                Assert.AreEqual(3, checks.Count);
                var names = checks.Cast<object>().Select(item => (string)item.GetType().GetField("name", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).GetValue(item)).ToArray();
                Assert.AreEqual(names.Length, names.Distinct(StringComparer.Ordinal).Count());
                StringAssert.Contains("EchoFixture`1", names[0]);
            });
        }

        private static Type ProbeType()
        {
            Assembly assembly = AppDomain.CurrentDomain.GetAssemblies().SingleOrDefault(item => item.GetName().Name == DiagnosticsAssembly);
            Assert.IsNotNull(assembly, "The diagnostics assembly must be loaded in the Editor test domain.");
            Type type = assembly.GetType("AssemblyShadowDemo.R01BLazyProbe", true);
            Assert.IsNotNull(type);
            return type;
        }

        public static class EchoFixture<T>
        {
            public static T Echo(T value) { return value; }
        }

        private static object DenseManifest(Type manifestType, Type fixtureType, int schemaVersion,
            string kind, string status, bool historicalEvidenceReused)
        {
            object manifest = Activator.CreateInstance(manifestType, true);
            SetField(manifest, "schemaVersion", schemaVersion);
            SetField(manifest, "kind", kind);
            SetField(manifest, "status", status);
            SetField(manifest, "historicalEvidenceReused", historicalEvidenceReused);
            Array fixtures = Array.CreateInstance(fixtureType, 2);
            fixtures.SetValue(DenseFixture(fixtureType, 1, 4098, 4097, 70000, 1024L * 1024L), 0);
            fixtures.SetValue(DenseFixture(fixtureType, 2, 4098, 4097, 70000, 1024L * 1024L), 1);
            SetField(manifest, "fixtures", fixtures);
            return manifest;
        }

        private static object DenseFixture(Type fixtureType, int id, int typeDefs, int methodDefs,
            int stringsHeapBytes, long sizeBytes)
        {
            object fixture = Activator.CreateInstance(fixtureType, true);
            SetField(fixture, "id", id);
            SetField(fixture, "typeDefRows", typeDefs);
            SetField(fixture, "methodDefRows", methodDefs);
            SetField(fixture, "stringsHeapBytes", stringsHeapBytes);
            SetField(fixture, "sizeBytes", sizeBytes);
            SetField(fixture, "name", "AssemblyShadow.Workload.I" + id.ToString("D4"));
            SetField(fixture, "path", "/fixture/AssemblyShadow.Workload.I" + id.ToString("D4") + ".dll");
            SetField(fixture, "sha256", new string('a', 64));
            return fixture;
        }

        private static void SetField(object value, string name, object fieldValue)
        {
            FieldInfo field = value.GetType().GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            Assert.IsNotNull(field, value.GetType().FullName + "." + name);
            field.SetValue(value, fieldValue);
        }

        private static object NewResult(Type probe)
        {
            Type resultType = probe.GetNestedType("Result", BindingFlags.NonPublic);
            Assert.IsNotNull(resultType);
            object result = Activator.CreateInstance(resultType, true);
            FieldInfo checks = resultType.GetField("checks", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            checks.SetValue(result, Activator.CreateInstance(typeof(List<>).MakeGenericType(probe.GetNestedType("CheckRecord", BindingFlags.NonPublic))));
            FieldInfo snapshots = resultType.GetField("capacitySnapshots", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            snapshots.SetValue(result, Activator.CreateInstance(typeof(List<>).MakeGenericType(probe.GetNestedType("CapacitySnapshot", BindingFlags.NonPublic))));
            return result;
        }

        private static void AddSnapshot(Type probe, object result, ulong imageCount)
        {
            Type resultType = result.GetType();
            IList snapshots = (IList)resultType.GetField("capacitySnapshots", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).GetValue(result);
            Type snapshotType = probe.GetNestedType("CapacitySnapshot", BindingFlags.NonPublic);
            object snapshot = Activator.CreateInstance(snapshotType, true);
            snapshotType.GetField("lifetimeReservedImageCount", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic).SetValue(snapshot, imageCount);
            snapshots.Add(snapshot);
        }

        private static void WithActive(FieldInfo active, object value, Action body)
        {
            object previous = active.GetValue(null);
            try { active.SetValue(null, value); body(); }
            finally { active.SetValue(null, previous); }
        }

        private static bool CallBool(Type probe, string name, ulong argument)
        {
            return (bool)PrivateMethod(probe, name, typeof(ulong)).Invoke(null, new object[] { argument });
        }

        private static FieldInfo PrivateField(Type type, string name)
        {
            FieldInfo field = type.GetField(name, BindingFlags.Static | BindingFlags.Instance | BindingFlags.NonPublic);
            Assert.IsNotNull(field, type.FullName + "." + name);
            return field;
        }

        private static MethodInfo PrivateMethod(Type type, string name, params Type[] parameters)
        {
            MethodInfo method = type.GetMethod(name, BindingFlags.Static | BindingFlags.NonPublic, null, parameters, null);
            Assert.IsNotNull(method, type.FullName + "." + name);
            return method;
        }
    }
}
