// Execute the package's actual Editor negotiation tests without starting Unity.
// Only unused Unity JSON/attribute types and the UnityEditor namespace are adapted.
using System;
using System.IO;
using System.Reflection;
using HybridCLR;

namespace UnityEngine
{
    public static class JsonUtility
    {
        public static T FromJson<T>(string value) { throw new InvalidOperationException("Unity JSON must not run during capability negotiation"); }
    }
}
namespace UnityEngine.Scripting
{
    [AttributeUsage(AttributeTargets.All)] public sealed class PreserveAttribute : Attribute { }
}
namespace UnityEditor { internal sealed class CapabilityStandaloneNamespaceAnchor { } }

internal static class R01BLiveCapabilityStandalone
{
    public static int Main(string[] args)
    {
        try
        {
            var fixture = new HybridCLR.Editor.AssemblyShadow.Tests.R01EarlyCapabilityNegotiationTests();
            int tests = 0;
            foreach (MethodInfo method in fixture.GetType().GetMethods())
            {
                if (!Attribute.IsDefined(method, typeof(NUnit.Framework.TestAttribute))) continue;
                try { method.Invoke(fixture, null); }
                catch (TargetInvocationException failure) { throw new Exception("Package test failed: " + method.Name, failure.InnerException); }
                ++tests;
            }
            string large = File.ReadAllText(args[0]);
            AssemblyShadowCapabilityReader.Snapshot ignored;
            if (AssemblyShadowCapabilityReader.TryRead(large, out ignored))
                throw new Exception("Strict full diagnostics parser accepted a native snapshot above its node limit");
            Type parserType = typeof(AssemblyShadowCapabilityReader).GetNestedType("Parser", BindingFlags.NonPublic);
            object parser = Activator.CreateInstance(parserType, BindingFlags.Instance | BindingFlags.NonPublic,
                null, new object[] { large }, null);
            bool nodeBound = false;
            try
            {
                parserType.GetMethod("ReadDocument", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(parser,
                    new object[] { new AssemblyShadowCapabilityReader.Snapshot() });
            }
            catch (TargetInvocationException failure)
            {
                nodeBound = failure.InnerException is FormatException &&
                    failure.InnerException.Message == "JSON resource bound exceeded.";
            }
            if (!nodeBound) throw new Exception("Native large-snapshot reproduction did not isolate the parser node bound");
            int fallbackCalls = 0;
            var result = AssemblyShadowRuntimeCapabilityNegotiation.NegotiateLive(option =>
                option == RuntimeOptionId.AssemblyShadowMetadataBudgetCapabilityVersion ? 2 : 1,
                (out string json) => { ++fallbackCalls; json = large; return AssemblyShadowErrorCode.Success; }, false, 2);
            if (result != AssemblyShadowErrorCode.Success || fallbackCalls != 0)
                throw new Exception("Live negotiation depended on oversized actual native diagnostics");
            // The actual Player-only wrapper is compiled in this executable.
            // Do not invoke it under Mono: its JIT resolves missing IL2CPP
            // internal calls eagerly, which cannot prove Player dispatch.
            Console.WriteLine("r01b_live_capability_managed_tests=" + tests + " native_snapshot_rejected=1 node_bound_reproduced=1 compact_independent=1 runtime_wrappers_compiled=1 PASS");
            return 0;
        }
        catch (Exception error) { Console.Error.WriteLine(error); return 1; }
    }
}
