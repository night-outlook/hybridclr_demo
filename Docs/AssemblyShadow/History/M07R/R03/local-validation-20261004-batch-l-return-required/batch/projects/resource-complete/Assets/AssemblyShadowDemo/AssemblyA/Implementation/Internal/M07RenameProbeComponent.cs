using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
#if ASSEMBLY_SHADOW_M07_P14
    public sealed class M07RenameProbeComponentRenamed : MonoBehaviour
#else
    public sealed class M07RenameProbeComponent : MonoBehaviour
#endif
    {
        [SerializeField] private int value = 714;
        public int ReadValue() { return value; }
    }
}
