#if ASSEMBLY_SHADOW_M04_P03
#pragma warning disable 0108
using System.Reflection;

namespace AssemblyShadowDemo.Consumers
{
    /// <summary>Patch-only executing-assembly witness for M04.</summary>
    public sealed partial class DerivedExternalComponent
    {
        public static object GetExecutingAssemblyObject()
        {
            return Assembly.GetExecutingAssembly();
        }
    }
}
#pragma warning restore 0108
#endif
