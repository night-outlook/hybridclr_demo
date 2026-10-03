using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AssemblyShadowDemo.Editor;
using dnlib.DotNet;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Scripting;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M04OrdinaryAssemblyTests
    {
        private const string ProbeName = "AssemblyShadowDemo.M04OrdinaryAssemblyProbe";
        private const string ConfigurationHash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        private const string Denial = "AssemblyShadow reflection denied; configuration=" + ConfigurationHash +
            "; site=m00-normal-hot-update-image";

        [Test]
        public void CurrentProjectPolicyKeepsOneEdgeAndExactOrdinaryEntrypoints()
        {
            var target = EditorUserBuildSettings.activeBuildTarget;
            var policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
            ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target).ThrowIfInvalid();

            // Runtime dependencies are graph edges, not per-call-site approvals.
            // Both milestones share one edge; Bootstrap approvals remain exact.
            const string consumer = "AssemblyShadowDemo.Bootstrap";
            const string provider = "AssemblyShadowBaseline.HotUpdate";
            Assert.AreEqual(1, policy.dependencies.runtimeDependencies.Count(edge =>
                edge.consumer == consumer && edge.provider == provider));
            foreach (string method in new[] {
                "AssemblyShadowDemo.M02ReflectionBindingProbe::ProbeFixedImage",
                ProbeName + "::Run",
                ProbeName + "::ProbeKnownNameCallback",
            })
            {
                var approval = policy.dependencies.bootstrapEntrypoints.Single(entry =>
                    entry.consumer == consumer && entry.provider == provider && entry.method == method);
                Assert.AreEqual(provider + ".Entry", approval.typeName);
                Assert.IsNotEmpty(approval.reason);
            }
        }

        [Test]
        public void OrdinaryResultPreservesExplicitFalseAndZeroJsonMembers()
        {
            Type type = Probe().GetNestedType("Result", BindingFlags.Public);
            Assert.IsNotNull(type);
            Assert.IsTrue(type.IsSerializable);
            Assert.IsNotNull(type.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault());
            object value = Activator.CreateInstance(type);
            string json = JsonUtility.ToJson(value);
            object roundtrip = JsonUtility.FromJson(json, type);
            foreach (FieldInfo field in type.GetFields(BindingFlags.Public | BindingFlags.Instance))
            {
                Assert.IsNotNull(field.GetCustomAttributes(typeof(PreserveAttribute), false).SingleOrDefault(), field.Name);
                StringAssert.Contains("\"" + field.Name + "\":", json, field.Name + " must be present even when default-valued.");
                if (field.FieldType == typeof(bool))
                {
                    StringAssert.Contains("\"" + field.Name + "\":false", json);
                    Assert.AreEqual(false, field.GetValue(roundtrip));
                }
                else if (field.FieldType == typeof(int))
                {
                    int expected = field.Name == "schemaVersion" ? 1 : 0;
                    StringAssert.Contains("\"" + field.Name + "\":" + expected, json);
                    Assert.AreEqual(expected, field.GetValue(roundtrip));
                }
                else Assert.AreEqual(typeof(string), field.FieldType, "Unexpected ordinary-result field kind.");
            }
            typeof(M04JsonEvidence).GetMethod("ValidateSchema").MakeGenericMethod(type).Invoke(null, new object[] { json });
        }

        [Test]
        public void FixedImageDenialRequiresTheExactTypeConfigurationAndSite()
        {
            MethodInfo check = Probe().GetMethod("IsGuardDenial", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(check);
            Assert.AreEqual(true, check.Invoke(null, new object[] { new InvalidOperationException(Denial), ConfigurationHash }));
            foreach (Exception error in new Exception[] {
                null,
                new Exception(Denial),
                new InvalidOperationException(Denial + " extra"),
                new InvalidOperationException(Denial.Replace("m00-normal-hot-update-image", "another-site")),
                new InvalidOperationException(Denial.Replace(ConfigurationHash, new string('f', 64))),
            }) Assert.AreEqual(false, check.Invoke(null, new object[] { error, ConfigurationHash }));
        }

        [Test]
        public void ReflectionFailureUnwrapsTheActualLoaderException()
        {
            var underlying = new InvalidOperationException("actual loader failure");
            MethodInfo capture = Probe().GetMethod("CaptureFailure", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(capture);
            Assert.AreSame(underlying, capture.Invoke(null, new object[] {
                (Action)(() => { throw new TargetInvocationException(underlying); }),
            }));
            Assert.AreSame(underlying, capture.Invoke(null, new object[] {
                (Action)(() => { throw underlying; }),
            }));
            Assert.IsNull(capture.Invoke(null, new object[] { (Action)(() => { }) }));
        }

        [Test]
        public void OrdinaryRegressionAddsNoRawImageOrFileLoader()
        {
            using (var module = ModuleDefMD.Load(File.ReadAllBytes(Probe().Assembly.Location)))
            {
                TypeDef[] types = module.GetTypes().Where(type => type.FullName == ProbeName ||
                    type.FullName.StartsWith(ProbeName + "/", StringComparison.Ordinal)).ToArray();
                Assert.Greater(types.Length, 0);
                foreach (MethodDef method in types.SelectMany(type => type.Methods).Where(method => method.HasBody))
                foreach (var instruction in method.Body.Instructions)
                {
                    var called = instruction.Operand as IMethod;
                    if (called == null || called.MethodSig == null || called.DeclaringType == null) continue;
                    string owner = called.DeclaringType.FullName;
                    if (owner != "System.Reflection.Assembly" && owner != "System.AppDomain") continue;
                    string name = called.Name.String;
                    Assert.AreNotEqual("get_ManifestModule", name,
                        "Pinned IL2CPP does not implement Assembly.ManifestModule; do not manufacture runtime MVID evidence.");
                    Assert.IsFalse(name == "LoadFile" || name == "LoadFrom" || name == "UnsafeLoadFrom" ||
                        name == "ReflectionOnlyLoadFrom", "An unbounded file acquisition was introduced: " + called.FullName);
                    if (name == "Load" || name == "ReflectionOnlyLoad")
                        Assert.IsFalse(called.MethodSig.Params.Any(parameter => parameter.FullName == "System.Byte[]"),
                            "The regression must use the existing verified M00 fixed-image guard: " + called.FullName);
                }
            }
        }

        private static Type Probe()
        {
            return Assembly.Load("AssemblyShadowDemo.Bootstrap").GetType(ProbeName, true);
        }
    }
}
