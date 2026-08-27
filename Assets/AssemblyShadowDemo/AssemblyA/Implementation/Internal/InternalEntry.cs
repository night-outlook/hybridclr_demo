namespace AssemblyA.Implementation.Internal
{
    public sealed class InternalEntry
    {
        public string GetMarker()
        {
            return VersionedPrefabComponent.GetVersionMarker();
        }

        public static string GetBaselineTypeAssemblyName()
        {
            return typeof(VersionedPrefabComponent).Assembly.GetName().Name;
        }

    }
}
