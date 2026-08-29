#if ASSEMBLY_SHADOW_M06_P03 && !ASSEMBLY_SHADOW_M03_INITIALIZERS
using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;

namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Method, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute { }
}

namespace AssemblyShadowDemo.Consumers
{
    internal static class ContractsConsumerM06ModuleInitializer
    {
        [ModuleInitializer]
        internal static void Initialize()
        {
            ContractsM06ExecutionWitness.BeginModuleInitialization(Stopwatch.GetTimestamp());
            try
            {
                string[] provider = AssemblyA.Contracts.M06ExecutionWitness.GetModuleEvidence();
                ContractsM06ExecutionWitness.RecordModuleProvider(ReadValue(provider, "assembly="), ReadValue(provider, "marker="), ReadCount(provider));
            }
            finally { ContractsM06ExecutionWitness.EndModuleInitialization(); }
        }

        private static int ReadCount(string[] evidence)
        {
            for (int i = 0; i < evidence.Length; ++i)
                if (evidence[i].StartsWith("module.count=", StringComparison.Ordinal))
                    return int.Parse(evidence[i].Substring("module.count=".Length));
            return 0;
        }

        private static string ReadValue(string[] evidence, string prefix)
        {
            for (int i = 0; i < evidence.Length; ++i)
                if (evidence[i].StartsWith(prefix, StringComparison.Ordinal)) return evidence[i].Substring(prefix.Length);
            return "none";
        }
    }
}
#endif
