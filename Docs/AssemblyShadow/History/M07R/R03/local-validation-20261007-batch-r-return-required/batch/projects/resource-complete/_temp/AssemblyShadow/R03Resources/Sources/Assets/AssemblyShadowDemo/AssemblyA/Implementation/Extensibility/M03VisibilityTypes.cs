#if ASSEMBLY_SHADOW_M03_INITIALIZERS && ASSEMBLY_SHADOW_M03_P03
namespace AssemblyA.Implementation.Extensibility.M03Fixtures
{
    // Conditional types leave the frozen baseline ABI and bytes untouched.
    public struct M03Pair<T>
    {
        public T value;
    }

    public struct M03Holder
    {
        public M03Pair<int> value;
        public System.Nullable<M03PrivateValue> optional;
    }

    public struct M03PrivateValue
    {
        public int value;
    }
}
#endif
