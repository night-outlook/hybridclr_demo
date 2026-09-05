using System.Collections.Generic;
using AssemblyA.Contracts;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed class VersionedScriptableObject : ScriptableObject, IVersionTextProvider
    {
        [SerializeField] private DemoValue value;
        [SerializeField] private M07InlineValue m07InlineValue;
        [SerializeField] private List<M07InlineValue> m07InlineValues = new List<M07InlineValue>();
        private static int s_enableCount;

        private void OnEnable() { ++s_enableCount; }

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

        public string ReadM07State()
        {
            return (m07InlineValue == null ? "null" : m07InlineValue.number + ":" + m07InlineValue.text) + "|" +
                (m07InlineValues == null ? "null" : string.Join(",", m07InlineValues.ConvertAll(item => item == null ? "null" : item.number + ":" + item.text).ToArray())) + "|" + M07Marker();
        }

        public static int ReadM07EnableCount() { return s_enableCount; }

        public static string M07Marker()
        {
#if ASSEMBLY_SHADOW_P05
            return "M07-P05-DATA";
#elif ASSEMBLY_SHADOW_M07_P04
            return "M07-P04-DATA";
#elif ASSEMBLY_SHADOW_P03
            return "M07-P03-DATA";
#elif ASSEMBLY_SHADOW_P01
            return "M07-P01-DATA";
#else
            return "M07-BASELINE-DATA";
#endif
        }
    }
}
