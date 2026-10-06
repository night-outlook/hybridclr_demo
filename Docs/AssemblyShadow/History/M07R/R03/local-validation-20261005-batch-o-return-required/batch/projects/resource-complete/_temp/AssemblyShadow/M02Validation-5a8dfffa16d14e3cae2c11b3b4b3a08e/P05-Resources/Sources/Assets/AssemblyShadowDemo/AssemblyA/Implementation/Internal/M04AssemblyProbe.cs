#if ASSEMBLY_SHADOW_M04
using System.Reflection;

namespace AssemblyA.Implementation.Internal
{
    /// <summary>Patch-only executing-assembly witness for M04.</summary>
    public sealed partial class InternalEntry
    {
        public static object GetExecutingAssemblyObject()
        {
            return Assembly.GetExecutingAssembly();
        }
    }
}
#endif
