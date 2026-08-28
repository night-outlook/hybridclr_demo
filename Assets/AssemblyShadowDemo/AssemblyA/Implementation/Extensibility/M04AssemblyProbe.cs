#if ASSEMBLY_SHADOW_M04_P03
using System.Reflection;

namespace AssemblyA.Implementation.Extensibility
{
    /// <summary>Patch-only executing-assembly witness for M04.</summary>
    public abstract partial class VersionedComponentBase
    {
        public static object GetExecutingAssemblyObject()
        {
            return Assembly.GetExecutingAssembly();
        }
    }
}
#endif
