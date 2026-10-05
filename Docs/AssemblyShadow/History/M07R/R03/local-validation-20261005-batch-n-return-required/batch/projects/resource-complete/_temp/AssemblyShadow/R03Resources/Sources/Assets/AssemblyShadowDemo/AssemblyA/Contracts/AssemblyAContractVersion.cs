namespace AssemblyA.Contracts
{
    public static partial class AssemblyAContractVersion
    {
        public const string Value = "M01";
#if ASSEMBLY_SHADOW_P03
        // An additive Contracts API change. Every reverse consumer must ship
        // from this same compile snapshot even if its own source is unchanged.
        public static string GetProtocolRevision() { return "PATCH-P03-CONTRACTS"; }
#endif
    }
}
