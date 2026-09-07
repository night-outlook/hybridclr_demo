using AssemblyA.Implementation.Extensibility;
using UnityEngine;

namespace AssemblyShadowDemo.Consumers
{
    public sealed partial class DerivedExternalComponent : VersionedComponentBase
    {
        [SerializeField] private Component relatedComponent;
        [SerializeField] private string m07SerializedLabel = "M07-EXTERNAL";

        public string GetDerivedText()
        {
            return GetBaseVersion() + "|DERIVED-EXTERNAL";
        }

        public string ReadM07NestedState()
        {
            return m07SerializedLabel + "|" + (relatedComponent == null ? "null" : relatedComponent.GetType().FullName) + "|" + M07Marker();
        }

        public string RunM07GenericComponentApis(GameObject root)
        {
            DerivedExternalComponent direct = root.GetComponent<DerivedExternalComponent>();
            DerivedExternalComponent child = root.GetComponentInChildren<DerivedExternalComponent>(true);
            DerivedExternalComponent parent = transform.parent == null ? null : transform.parent.GetComponentInChildren<DerivedExternalComponent>(true);
            return (direct == this) + "|" + (child != null) + "|" + (parent != null) + "|" + M07Marker();
        }

        public static string M07Marker()
        {
#if ASSEMBLY_SHADOW_P03
            return "M07-P03-CONSUMER";
#else
            return "M07-BASELINE-CONSUMER";
#endif
        }
    }
}
