#if ASSEMBLY_SHADOW_M03_INITIALIZERS && ASSEMBLY_SHADOW_M03_P03
using System;
using AssemblyA.Implementation.Extensibility.M03Fixtures;

namespace AssemblyA.Implementation.Internal.M03Fixtures
{
    // Field layout resolves cross-image generic metadata during private staging.
    // In particular Nullable's class image is corlib but its argument is private.
    internal struct M03VisibilityConsumer
    {
        public M03Holder value;
        public Nullable<M03Holder> optional;
        public M03Holder[] array;
        public M03Pair<M03Holder[]> compound;
    }
}
#endif
