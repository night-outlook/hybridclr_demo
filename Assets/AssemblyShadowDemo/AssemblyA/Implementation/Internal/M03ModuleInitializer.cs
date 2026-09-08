#if ASSEMBLY_SHADOW_M03_INITIALIZERS && !ASSEMBLY_SHADOW_R01_INITIALIZER_THROW
using System;

namespace AssemblyA.Implementation.Internal
{
    internal static class M03ModuleInitializer
    {
        [System.Runtime.CompilerServices.ModuleInitializer]
        internal static void Initialize()
        {
            Console.WriteLine("M03-INIT:AssemblyA.Implementation.Internal");
#if ASSEMBLY_SHADOW_M03_INITIALIZER_THROW
            throw new InvalidOperationException("M03-INIT-THROW:AssemblyA.Implementation.Internal");
#endif
        }
    }
}

namespace System.Runtime.CompilerServices
{
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false, Inherited = false)]
    internal sealed class ModuleInitializerAttribute : Attribute { }
}
#endif
