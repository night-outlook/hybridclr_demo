#if (ASSEMBLY_SHADOW_M06 || ASSEMBLY_SHADOW_M06_P02 || ASSEMBLY_SHADOW_M06_P03) && !ASSEMBLY_SHADOW_M03_INITIALIZERS
using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;

namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Method, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute { }
}

namespace AssemblyA.Implementation.Internal
{
    internal static class M06ModuleInitializer
    {
        [ModuleInitializer]
        internal static void Initialize()
        {
            M06ExecutionWitness.BeginModuleInitialization(Stopwatch.GetTimestamp());
            try
            {
                string[] provider = AssemblyA.Implementation.Extensibility.M06ExecutionWitness.GetModuleEvidence();
                M06ExecutionWitness.RecordModuleProvider(ReadValue(provider, "assembly="), ReadValue(provider, "marker="), ReadCount(provider));
#if ASSEMBLY_SHADOW_M06_INITIALIZER_THROW
                throw new InvalidOperationException("M06 initializer failure");
#endif
            }
            finally { M06ExecutionWitness.EndModuleInitialization(); }
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
