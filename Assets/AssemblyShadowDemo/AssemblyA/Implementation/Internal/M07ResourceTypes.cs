using System;
using AssemblyA.Contracts;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    [Serializable]
    public sealed class M07NestedPayload
    {
        public int number;
        public string text;
    }

#if ASSEMBLY_SHADOW_M07_P15
    [Serializable]
    public sealed class M07NodeARenamed : IM07ManagedNode
#else
    [Serializable]
    public sealed class M07NodeA : IM07ManagedNode
#endif
    {
        [SerializeField] private int value = 70;
        [SerializeField] private string label = "NODE-A";
        [SerializeReference] private IM07ManagedNode next;

        public string Describe() { return label + "|" + M07Marker() + "|" + (next == null ? "END" : next.Describe()); }
        public int Sum() { return value + (next == null ? 0 : next.Sum()); }
        public void SetNext(IM07ManagedNode valueToSet) { next = valueToSet; }

        private static string M07Marker()
        {
#if ASSEMBLY_SHADOW_P05
            return "M07-P05-NODE";
#elif ASSEMBLY_SHADOW_M07_P04
            return "M07-P04-NODE";
#elif ASSEMBLY_SHADOW_P03
            return "M07-P03-NODE";
#elif ASSEMBLY_SHADOW_P01
            return "M07-P01-NODE";
#else
            return "M07-BASELINE-NODE";
#endif
        }
    }

    [Serializable]
    public sealed class M07NodeB : IM07ManagedNode
    {
        [SerializeField] private int value = 7;
        [SerializeField] private string label = "NODE-B";

        public string Describe() { return label + "|" + VersionedPrefabComponent.M07PatchMarker(); }
        public int Sum() { return value; }
    }
}
