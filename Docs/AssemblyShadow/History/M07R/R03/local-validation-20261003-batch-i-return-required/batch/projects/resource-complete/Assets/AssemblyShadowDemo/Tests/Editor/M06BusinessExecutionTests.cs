using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M06BusinessExecutionTests
    {
        private static readonly Type[] Witnesses = {
            typeof(AssemblyA.Contracts.M06ExecutionWitness),
            typeof(AssemblyA.Implementation.Extensibility.M06ExecutionWitness),
            typeof(AssemblyA.Implementation.Internal.M06ExecutionWitness),
            typeof(AssemblyShadowDemo.Consumers.ContractsM06ExecutionWitness),
            typeof(AssemblyShadowDemo.Consumers.ExtensibilityM06ExecutionWitness),
        };

        [Test]
        public void EveryWitnessHasTheFixedBootstrapBoundary()
        {
            foreach (Type witness in Witnesses)
            {
                MethodInfo run = witness.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
                MethodInfo evidence = witness.GetMethod("GetModuleEvidence", BindingFlags.Public | BindingFlags.Static);
                MethodInfo async = witness.GetMethod("RunAsync", BindingFlags.Public | BindingFlags.Static);
                MethodInfo coroutine = witness.GetMethod("RunCoroutine", BindingFlags.Public | BindingFlags.Static);
                MethodInfo warmup = witness.GetMethod("WarmupValue", BindingFlags.Public | BindingFlags.Static);
                MethodInfo echo = witness.GetMethod("WarmupEcho", BindingFlags.Public | BindingFlags.Static);
                Assert.IsNotNull(run, witness.FullName);
                Assert.AreEqual(typeof(string[]), run.ReturnType);
                Assert.AreEqual(typeof(string[]), evidence.ReturnType);
                Assert.AreEqual(typeof(System.Threading.Tasks.Task<string[]>), async.ReturnType);
                Assert.AreEqual(typeof(System.Collections.IEnumerator), coroutine.ReturnType);
                Assert.AreEqual(typeof(int), warmup.ReturnType);
                Assert.IsTrue(echo.IsGenericMethodDefinition);
                Assert.AreEqual(1, echo.GetGenericArguments().Length);
                Assert.IsTrue(run.GetParameters().Single().ParameterType == typeof(string));
                Assert.AreEqual(1, coroutine.GetParameters().Length);
            }
        }

        [Test]
        public void BaselineWitnessesProduceComputedDistinctOperations()
        {
            foreach (Type witness in Witnesses)
            {
                MethodInfo run = witness.GetMethod("Run", BindingFlags.Public | BindingFlags.Static);
                string[] values = (string[])run.Invoke(null, new object[] { "new" });
                Assert.IsTrue(values.Length >= 4, witness.FullName);
                Assert.IsTrue(values.Any(value => value.StartsWith("marker=M06-BASELINE", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(values.Any(value => value.Contains("ctor=")), witness.FullName);
                Assert.IsTrue(values.Any(value => value.Contains("interface=")), witness.FullName);
                int warmup = (int)witness.GetMethod("WarmupValue").Invoke(null, new object[] { 7 });
                Assert.AreEqual(1007, warmup, witness.FullName);
                string echo = (string)witness.GetMethod("WarmupEcho").MakeGenericMethod(typeof(string)).Invoke(null, new object[] { "echo" });
                Assert.AreEqual("echo", echo, witness.FullName);
            }
        }

        [Test]
        public void EachFinitePhaseRunsAndCoroutineRecordsContinuation()
        {
            string[] phases = { "statics", "dispatch", "delegates", "generics", "exceptions", "warmup" };
            foreach (Type witness in Witnesses)
            {
                MethodInfo run = witness.GetMethod("Run");
                foreach (string phase in phases)
                {
                    string[] values = (string[])run.Invoke(null, new object[] { phase });
                    Assert.IsTrue(values.Any(value => value == "phase=" + phase || value.StartsWith("warmup=", StringComparison.Ordinal)), witness.FullName + ":" + phase);
                }
                var observations = new List<string>();
                var coroutine = (System.Collections.IEnumerator)witness.GetMethod("RunCoroutine").Invoke(null, new object[] { observations });
                try
                {
                    Assert.IsTrue(coroutine.MoveNext());
                    Assert.IsNull(coroutine.Current);
                    Assert.AreEqual(1, observations.Count, "Continuation must follow the yielded frame.");
                    Assert.IsTrue(observations[0].StartsWith("coroutine.begin=", StringComparison.Ordinal));
                    Assert.IsFalse(coroutine.MoveNext());
                    Assert.IsTrue(observations[1].StartsWith("coroutine.continuation=", StringComparison.Ordinal));
                }
                finally { (coroutine as IDisposable)?.Dispose(); }
                CollectionAssert.AllItemsAreNotNull(observations);
                Assert.AreEqual(2, observations.Count);
            }
        }

        [Test]
        public void ModuleEvidenceAndHardCasesExposeActualBoundaries()
        {
            foreach (Type witness in Witnesses)
            {
                string[] evidence = (string[])witness.GetMethod("GetModuleEvidence").Invoke(null, null);
                StringAssert.Contains("module.count=", string.Join("|", evidence));
                StringAssert.Contains("module.startTicks=", string.Join("|", evidence));
                StringAssert.Contains("module.frequency=", string.Join("|", evidence));
                StringAssert.Contains("provider.assembly=", string.Join("|", evidence));
                StringAssert.Contains("provider.marker=", string.Join("|", evidence));
                StringAssert.Contains("provider.count=", string.Join("|", evidence));
                string[] generic = (string[])witness.GetMethod("Run").Invoke(null, new object[] { "generics" });
                Assert.IsTrue(generic.Any(value => value.StartsWith("generic.method=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(generic.Any(value => value.StartsWith("ref=", StringComparison.Ordinal)), witness.FullName);
                string[] exceptions = (string[])witness.GetMethod("Run").Invoke(null, new object[] { "exceptions" });
                Assert.IsTrue(exceptions.Any(value => value == "wrapped=InvalidOperationException"), witness.FullName);
                Assert.IsTrue(exceptions.Any(value => value.StartsWith("method.token=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(exceptions.Any(value => value.StartsWith("stack.text=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(exceptions.Any(value => value.StartsWith("frame.0.declaringType=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(exceptions.Any(value => value.StartsWith("frame.0.file=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(exceptions.Any(value => value.StartsWith("source.status=", StringComparison.Ordinal)), witness.FullName);
                string[] delegates = (string[])witness.GetMethod("Run").Invoke(null, new object[] { "delegates" });
                string before = delegates.Single(value => value.StartsWith("event.beforeRemove=", StringComparison.Ordinal));
                string after = delegates.Single(value => value.StartsWith("event.afterRemove=", StringComparison.Ordinal));
                Assert.AreEqual(before.Substring(before.IndexOf('=') + 1), after.Substring(after.IndexOf('=') + 1), witness.FullName);
                Assert.IsTrue(delegates.Any(value => value == "event.removed=True"), witness.FullName);
            }
        }

        [Test]
        public void StaticFixturesExposeExplicitAndBeforeFieldInitMetadata()
        {
            foreach (Type witness in Witnesses)
            {
                Type beforeDefinition = witness.GetNestedType("BeforeFieldInitState`1", BindingFlags.NonPublic);
                Type explicitType = witness.GetNestedType("ExplicitStaticState", BindingFlags.NonPublic);
                Assert.IsNotNull(beforeDefinition, witness.FullName);
                Assert.IsNotNull(explicitType, witness.FullName);
                Type beforeType = beforeDefinition.MakeGenericType(typeof(int));
                Assert.IsTrue((beforeType.Attributes & TypeAttributes.BeforeFieldInit) != 0, witness.FullName);
                Assert.IsFalse((explicitType.Attributes & TypeAttributes.BeforeFieldInit) != 0, witness.FullName);
                string[] values = (string[])witness.GetMethod("Run").Invoke(null, new object[] { "statics" });
                Assert.IsTrue(values.Any(value => value.StartsWith("beforefieldinit.count=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(values.Any(value => value.StartsWith("beforefieldinit.int.repeat=", StringComparison.Ordinal)), witness.FullName);
                Assert.IsTrue(values.Any(value => value.StartsWith("beforefieldinit.string.repeat=", StringComparison.Ordinal)), witness.FullName);
            }
        }

        [Test]
        public void ExtensibilityBaseIsARealCrossAssemblyBoundary()
        {
            Type baseType = typeof(AssemblyA.Implementation.Extensibility.M06ExecutionBase);
            Assert.IsTrue(baseType.IsAbstract);
            Assert.IsTrue(typeof(AssemblyA.Contracts.IVersionTextProvider).IsAssignableFrom(baseType));
            Assert.IsTrue(typeof(AssemblyA.Implementation.Extensibility.M06ExecutionBase).IsAssignableFrom(typeof(AssemblyA.Implementation.Internal.M06ExecutionWitness.M06InternalNode)));
            string[] dispatch = (string[])typeof(AssemblyA.Implementation.Internal.M06ExecutionWitness).GetMethod("Run").Invoke(null, new object[] { "dispatch" });
            Assert.IsTrue(dispatch.Any(value => value.StartsWith("base=", StringComparison.Ordinal)));
        }

        [Test]
        public void PatchGuardsKeepBaselineAndClosureMarkersSeparate()
        {
            string contracts = File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Contracts/M06ExecutionWitness.cs");
            string extensibility = File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/M06ExecutionWitness.cs");
            string internalWitness = File.ReadAllText("Assets/AssemblyShadowDemo/AssemblyA/Implementation/Internal/M06ExecutionWitness.cs");
            string contractsConsumer = File.ReadAllText("Assets/AssemblyShadowDemo/Consumers/ContractsConsumer/M06ExecutionWitness.cs");
            string extensibilityConsumer = File.ReadAllText("Assets/AssemblyShadowDemo/Consumers/ExtensibilityConsumer/M06ExecutionWitness.cs");
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P03", contracts);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P02", extensibility);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P03", extensibility);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06", internalWitness);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P03", contractsConsumer);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P02", extensibilityConsumer);
            StringAssert.Contains("ASSEMBLY_SHADOW_M06_P03", extensibilityConsumer);
            Assert.IsFalse(contracts.Contains("VersionedPrefabComponent"));
            Assert.IsFalse(contractsConsumer.Contains("VersionedPrefabComponent"));
        }
    }
}
