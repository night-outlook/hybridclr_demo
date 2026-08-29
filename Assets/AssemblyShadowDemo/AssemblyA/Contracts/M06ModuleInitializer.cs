#if ASSEMBLY_SHADOW_M06_P03 && !ASSEMBLY_SHADOW_M03_INITIALIZERS
using System;
using System.Diagnostics;
using System.Runtime.CompilerServices;

namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Method, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute { }
}

namespace AssemblyA.Contracts
{
    internal static class M06ModuleInitializer
    {
        [ModuleInitializer]
        internal static void Initialize()
        {
            M06ExecutionWitness.BeginModuleInitialization(Stopwatch.GetTimestamp());
            try { M06ExecutionWitness.RecordModuleProvider("none", "none", 0); }
            finally { M06ExecutionWitness.EndModuleInitialization(); }
        }
    }
}
#endif
