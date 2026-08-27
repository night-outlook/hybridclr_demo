using AssemblyA.Contracts;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed class VersionedScriptableObject : ScriptableObject, IVersionTextProvider
    {
        [SerializeField] private DemoValue value;

        public string GetVersionText()
        {
            return "BASELINE-DATA";
        }

        public int ReadSerializedNumber()
        {
            return value == null ? 0 : value.number;
        }

        public string ReadSerializedText()
        {
            return value == null ? null : value.text;
        }
    }
}
