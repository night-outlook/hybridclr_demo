using AssemblyA.Contracts;
using AssemblyA.Implementation.Extensibility;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed class VersionedPrefabComponent : VersionedComponentBase, IVersionTextProvider
    {
        [SerializeField] private DemoValue value;
        [SerializeField] private VersionedScriptableObject dataReference;
#if ASSEMBLY_SHADOW_P05
        [SerializeField] private int addedSerializedField = 42;
#endif

        public string GetVersionText()
        {
#if ASSEMBLY_SHADOW_P01
            return "PATCH-P01-INTERNAL";
#else
            return "BASELINE-INTERNAL";
#endif
        }

        public static string GetVersionMarker()
        {
            return GetVersionTextStatic();
        }

        private static string GetVersionTextStatic()
        {
#if ASSEMBLY_SHADOW_P01
            return "PATCH-P01-INTERNAL";
#else
            return "BASELINE-INTERNAL";
#endif
        }

        public string GetCombinedText()
        {
            return string.Format("{0}|{1}|{2}", GetBaseVersion(), GetVersionText(), value == null ? 0 : value.number);
        }

        public int ReadSerializedNumber()
        {
            return value == null ? 0 : value.number;
        }

        public string ReadSerializedText()
        {
            return value == null ? null : value.text;
        }

        public string ReadDataReferenceName()
        {
            return dataReference == null ? null : dataReference.name;
        }
    }
}
