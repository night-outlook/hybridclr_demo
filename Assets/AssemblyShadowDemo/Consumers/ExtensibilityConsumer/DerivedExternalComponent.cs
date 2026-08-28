using AssemblyA.Implementation.Extensibility;
using UnityEngine;

namespace AssemblyShadowDemo.Consumers
{
    public sealed partial class DerivedExternalComponent : VersionedComponentBase
    {
        public string GetDerivedText()
        {
            return GetBaseVersion() + "|DERIVED-EXTERNAL";
        }
    }
}
