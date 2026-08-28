#if ASSEMBLY_SHADOW_M03_INITIALIZERS && ASSEMBLY_SHADOW_M03_P03
using System;

namespace AssemblyShadowDemo.Consumers
{
    internal static class M03ModuleInitializer
    {
        [System.Runtime.CompilerServices.ModuleInitializer]
        internal static void Initialize()
        {
            Console.WriteLine("M03-INIT:AssemblyShadowDemo.ContractsConsumer");
        }
    }
}

namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute { }
}
#endif
