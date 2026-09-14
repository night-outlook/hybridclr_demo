using System;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class H1CountNativeDiagnosticsTests
    {
        private const string DiagnosticsAssembly = "AssemblyShadow.R01BDiagnostics";
        private const string ValidJson = "{\"schemaVersion\":1,\"kind\":\"H1CountNativeDiagnostics\",\"diagnosticOnly\":true,\"featureEnabled\":false,\"featureMode\":\"AssemblyShadowOff\",\"reservedPages\":0,\"mappedPages\":0,\"reservationCount\":0,\"nextImageId\":1,\"nextPageSlot\":0,\"ordinaryAllocatedCount\":0,\"shadowAllocatedCount\":0,\"reservedImageCount\":0,\"logicalAssemblies\":[],\"physicalAssemblies\":[],\"publishedInterpreterImages\":[]}";

        [Test]
        public void MissingRootCountersAreRejectedEvenWhenNestedUnknownFieldsQuoteTheirNames()
        {
            string missingRoot = ValidJson.Replace(",\"reservedPages\":0,\"mappedPages\":0", ",\"extension\":{\"reservedPages\":0,\"mappedPages\":0}");
            AssertRejected(missingRoot);
        }

        [Test]
        public void DuplicateRootCounterIsRejected()
        {
            AssertRejected(ValidJson.Substring(0, ValidJson.Length - 1) + ",\"reservedPages\":0}");
        }

        [Test]
        public void CounterWrongPrimitiveTypeIsRejected()
        {
            AssertRejected(ValidJson.Replace("\"reservedPages\":0", "\"reservedPages\":\"0\""));
            AssertRejected(ValidJson.Replace("\"diagnosticOnly\":true", "\"diagnosticOnly\":1"));
        }

        [Test]
        public void BothFeatureModesMaterializeEveryNonzeroFieldExactly()
        {
            AssertSnapshot(Parse("{\"schemaVersion\":1,\"kind\":\"H1CountNativeDiagnostics\",\"diagnosticOnly\":true,\"featureEnabled\":false,\"featureMode\":\"AssemblyShadowOff\",\"reservedPages\":100,\"mappedPages\":40,\"reservationCount\":7,\"nextImageId\":9,\"nextPageSlot\":88,\"ordinaryAllocatedCount\":3,\"shadowAllocatedCount\":2,\"reservedImageCount\":6,\"logicalAssemblies\":[],\"physicalAssemblies\":[],\"publishedInterpreterImages\":[]}"),
                false, "AssemblyShadowOff", 100UL, 40UL, 7UL, 9UL, 88UL, 3UL, 2UL, 6UL);
            AssertSnapshot(Parse("{\"schemaVersion\":1,\"kind\":\"H1CountNativeDiagnostics\",\"diagnosticOnly\":true,\"featureEnabled\":true,\"featureMode\":\"AssemblyShadowOn\",\"reservedPages\":200,\"mappedPages\":150,\"reservationCount\":11,\"nextImageId\":17,\"nextPageSlot\":166,\"ordinaryAllocatedCount\":8,\"shadowAllocatedCount\":5,\"reservedImageCount\":13,\"logicalAssemblies\":[],\"physicalAssemblies\":[],\"publishedInterpreterImages\":[]}"),
                true, "AssemblyShadowOn", 200UL, 150UL, 11UL, 17UL, 166UL, 8UL, 5UL, 13UL);
        }

        [Test]
        public void CountRunnerUsesNativeIdentityBridgeInsteadOfUnsupportedManagedModuleProbe()
        {
            string source = File.ReadAllText("Assets/AssemblyShadowR01BDiagnostics/Runtime/H1CountDiagnosticRunner.cs");
            string startup = File.ReadAllText("Assets/AssemblyShadowDemo/Bootstrap/H1CountEarlyStartup.cs");
            Assert.IsFalse(source.Contains("ManifestModule"));
            Assert.IsFalse(source.Contains("ModuleVersionId"));
            Assert.IsFalse(startup.Contains("ManifestModule"));
            Assert.IsFalse(startup.Contains("Type.GetType"));
            Assert.IsFalse(startup.Contains("GetMethod(\"Run\""));
            Assert.IsFalse(startup.Contains("method.Invoke"));
            StringAssert.Contains("NativeAssemblyIdentity", startup);
            StringAssert.Contains("CapturePublicationInventory", source);
            StringAssert.Contains("physicalAssembliesBefore", source);
            StringAssert.Contains("publishedInterpreterImagesBefore", source);
        }

        [Test]
        public void NativeIdentityInventoryMaterializesExactFields()
        {
            string identity = "{\"nativeAssemblyId\":\"0xa\",\"nativeImageId\":\"0xb\",\"name\":\"Fixture\",\"fullName\":\"Fixture, Version=1.2.3.4, Culture=neutral, PublicKeyToken=null\",\"versionMajor\":1,\"versionMinor\":2,\"versionBuild\":3,\"versionRevision\":4,\"culture\":\"neutral\",\"flags\":0,\"publicKeyToken\":\"null\",\"mvidAvailable\":true,\"mvid\":\"00112233-4455-6677-8899-aabbccddeeff\",\"imageKind\":\"Interpreter\",\"imageId\":7,\"published\":true,\"identityKey\":\"Fixture|00112233-4455-6677-8899-aabbccddeeff|Fixture, Version=1.2.3.4, Culture=neutral, PublicKeyToken=null|0xa|0xb|Interpreter|7\"}";
            string json = ValidJson.Substring(0, ValidJson.Length - 1).Replace(
                "\"logicalAssemblies\":[]", "\"logicalAssemblies\":[" + identity + "]") + "}";
            object snapshot = Parse(json);
            Type type = snapshot.GetType();
            Array rows = (Array)type.GetField("logicalAssemblies").GetValue(snapshot);
            Assert.AreEqual(1, rows.Length);
            object row = rows.GetValue(0);
            Assert.AreEqual("Fixture", row.GetType().GetField("name").GetValue(row));
            Assert.AreEqual(7U, row.GetType().GetField("imageId").GetValue(row));
            Assert.AreEqual(true, row.GetType().GetField("mvidAvailable").GetValue(row));
        }

        private static void AssertRejected(string json)
        {
            MethodInfo parse = DiagnosticsType().GetMethod("Parse", BindingFlags.Public | BindingFlags.Static);
            Assert.IsNotNull(parse);
            TargetInvocationException error = Assert.Throws<TargetInvocationException>(() => parse.Invoke(null, new object[] { json }));
            Assert.IsInstanceOf<FormatException>(error.InnerException);
        }

        private static object Parse(string json)
        {
            MethodInfo parse = DiagnosticsType().GetMethod("Parse", BindingFlags.Public | BindingFlags.Static);
            Assert.IsNotNull(parse);
            return parse.Invoke(null, new object[] { json });
        }

        private static void AssertSnapshot(object snapshot, bool featureEnabled, string featureMode,
            ulong reservedPages, ulong mappedPages, ulong reservationCount, ulong nextImageId,
            ulong nextPageSlot, ulong ordinaryAllocatedCount, ulong shadowAllocatedCount,
            ulong reservedImageCount)
        {
            Type type = snapshot.GetType();
            Assert.AreEqual(1, type.GetField("schemaVersion").GetValue(snapshot));
            Assert.AreEqual("H1CountNativeDiagnostics", type.GetField("kind").GetValue(snapshot));
            Assert.AreEqual(true, type.GetField("diagnosticOnly").GetValue(snapshot));
            Assert.AreEqual(featureEnabled, type.GetField("featureEnabled").GetValue(snapshot));
            Assert.AreEqual(featureMode, type.GetField("featureMode").GetValue(snapshot));
            Assert.AreEqual(reservedPages, type.GetField("reservedPages").GetValue(snapshot));
            Assert.AreEqual(mappedPages, type.GetField("mappedPages").GetValue(snapshot));
            Assert.AreEqual(reservationCount, type.GetField("reservationCount").GetValue(snapshot));
            Assert.AreEqual(nextImageId, type.GetField("nextImageId").GetValue(snapshot));
            Assert.AreEqual(nextPageSlot, type.GetField("nextPageSlot").GetValue(snapshot));
            Assert.AreEqual(ordinaryAllocatedCount, type.GetField("ordinaryAllocatedCount").GetValue(snapshot));
            Assert.AreEqual(shadowAllocatedCount, type.GetField("shadowAllocatedCount").GetValue(snapshot));
            Assert.AreEqual(reservedImageCount, type.GetField("reservedImageCount").GetValue(snapshot));
        }

        private static Type DiagnosticsType()
        {
            Assembly assembly = AppDomain.CurrentDomain.GetAssemblies().SingleOrDefault(item => item.GetName().Name == DiagnosticsAssembly);
            Assert.IsNotNull(assembly, "The diagnostics assembly must be loaded in the Editor test domain.");
            Type type = assembly.GetType("AssemblyShadowDemo.H1CountNativeDiagnostics", true);
            Assert.IsNotNull(type);
            return type;
        }
    }
}
