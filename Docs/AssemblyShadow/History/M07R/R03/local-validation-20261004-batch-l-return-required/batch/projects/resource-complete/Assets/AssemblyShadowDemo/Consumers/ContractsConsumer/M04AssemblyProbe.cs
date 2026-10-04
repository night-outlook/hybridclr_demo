#if ASSEMBLY_SHADOW_M04_P03
using System.Reflection;

namespace AssemblyShadowDemo.Consumers
{
    /// <summary>Patch-only executing-assembly witness for M04.</summary>
    public static partial class ContractsConsumer
    {
        public static object GetExecutingAssemblyObject()
        {
            return Assembly.GetExecutingAssembly();
        }
    }
}
#endif
