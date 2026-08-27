using UnityEngine;

namespace AssemblyA.Implementation.Extensibility
{
    public abstract class VersionedComponentBase : MonoBehaviour
    {
        [SerializeField] private int baseSerializedValue = 7;

        public virtual string GetBaseVersion()
        {
            return "BASELINE-EXT";
        }

        public int ReadBaseSerializedValue()
        {
            return baseSerializedValue;
        }
    }
}
