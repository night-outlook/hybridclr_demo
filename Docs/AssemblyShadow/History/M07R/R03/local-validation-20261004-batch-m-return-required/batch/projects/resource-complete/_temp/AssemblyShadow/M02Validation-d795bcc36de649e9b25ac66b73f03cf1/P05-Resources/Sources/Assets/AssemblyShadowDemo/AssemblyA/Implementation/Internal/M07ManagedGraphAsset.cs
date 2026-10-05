using AssemblyA.Contracts;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed class M07ManagedGraphAsset : ScriptableObject
    {
        [SerializeReference] private IM07ManagedNode node;

        public string DescribeGraph() { return node == null ? "null" : node.Describe(); }
        public int SumGraph() { return node == null ? 0 : node.Sum(); }
        public string ConcreteTypeName() { return node == null ? "null" : node.GetType().AssemblyQualifiedName; }
        public IM07ManagedNode GetNode() { return node; }
    }
}
