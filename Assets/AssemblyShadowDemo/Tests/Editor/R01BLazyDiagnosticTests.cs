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
