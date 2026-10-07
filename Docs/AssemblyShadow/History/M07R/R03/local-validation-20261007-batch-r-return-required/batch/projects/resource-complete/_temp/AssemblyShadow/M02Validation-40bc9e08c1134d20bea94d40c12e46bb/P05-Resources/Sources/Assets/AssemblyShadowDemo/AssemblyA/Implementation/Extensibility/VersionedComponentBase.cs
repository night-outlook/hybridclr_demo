using UnityEngine;

namespace AssemblyA.Implementation.Extensibility
{
    public abstract partial class VersionedComponentBase : MonoBehaviour
    {
        [SerializeField] private int baseSerializedValue = 7;

        public virtual string GetBaseVersion()
        {
#if ASSEMBLY_SHADOW_P02
            return "PATCH-P02-EXT";
#else
            return "BASELINE-EXT";
#endif
        }

        public int ReadBaseSerializedValue()
        {
            return baseSerializedValue;
        }
    }
}
