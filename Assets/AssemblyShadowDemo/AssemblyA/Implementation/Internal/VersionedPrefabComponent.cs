using System;
using System.Collections.Generic;
using AssemblyA.Contracts;
using AssemblyA.Implementation.Extensibility;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed partial class VersionedPrefabComponent : VersionedComponentBase, IVersionTextProvider
    {
        [SerializeField] private DemoValue value;
        [SerializeField] private VersionedScriptableObject dataReference;
        [SerializeField] private int m07SerializedInt = 701;
        [SerializeField] private string m07SerializedString = "M07-BASELINE-TEXT";
        [SerializeField] private M07InlineValue m07InlineValue;
        [SerializeField] private List<M07InlineValue> m07InlineValues = new List<M07InlineValue>();
        [SerializeField] private UnityEngine.Object m07ObjectReference;
        [SerializeField] private M07NestedPayload m07NestedPayload;
#if ASSEMBLY_SHADOW_M07_P04
        [NonSerialized] private int m07RuntimeOnlyValue;
#endif
#if ASSEMBLY_SHADOW_P05
        [SerializeField] private int addedSerializedField = 42;
#endif

        private static int s_awakeCount;
        private static int s_enableCount;
        private static int s_startCount;
        private static int s_updateCount;
        private static int s_disableCount;
        private static int s_destroyCount;
        private static int s_sendMessageCount;
        private static int s_invokeCount;

        private void Awake() { ++s_awakeCount; }
        private void OnEnable() { ++s_enableCount; }
        private void Start() { ++s_startCount; }
        private void Update() { ++s_updateCount; }
        private void OnDisable() { ++s_disableCount; }
        private void OnDestroy() { ++s_destroyCount; }
        private void M07ReceiveMessage(string value) { if (value == "M07-SEND") ++s_sendMessageCount; }
        private void M07Invoked() { ++s_invokeCount; }

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

        public string ReadM07SerializedState()
        {
            string list = m07InlineValues == null ? "null" : string.Join(",", m07InlineValues.ConvertAll(item => item == null ? "null" : item.number + ":" + item.text).ToArray());
            return m07SerializedInt + "|" + m07SerializedString + "|" +
                (m07InlineValue == null ? "null" : m07InlineValue.number + ":" + m07InlineValue.text) + "|" + list + "|" +
                (m07ObjectReference == null ? "null" : m07ObjectReference.name) + "|" +
                (m07NestedPayload == null ? "null" : m07NestedPayload.number + ":" + m07NestedPayload.text);
        }

        public string RunM07MessagePaths()
        {
            SendMessage("M07ReceiveMessage", "M07-SEND", SendMessageOptions.RequireReceiver);
            Invoke("M07Invoked", 0f);
            return M07PatchMarker();
        }

        public int ReadM07AddedSerializedField()
        {
#if ASSEMBLY_SHADOW_P05
            return addedSerializedField;
#else
            return -1;
#endif
        }

        public int WriteAndReadM07RuntimeOnlyField(int value)
        {
#if ASSEMBLY_SHADOW_M07_P04
            m07RuntimeOnlyValue = value;
            return m07RuntimeOnlyValue;
#else
            return -1;
#endif
        }

        public static string M07PatchMarker()
        {
#if ASSEMBLY_SHADOW_P05
            return "M07-P05";
#elif ASSEMBLY_SHADOW_M07_P04
            return "M07-P04";
#elif ASSEMBLY_SHADOW_P03
            return "M07-P03";
#elif ASSEMBLY_SHADOW_P01
            return "M07-P01";
#else
            return "M07-BASELINE";
#endif
        }

        public static int[] ReadM07LifecycleCounts()
        {
            return new[] { s_awakeCount, s_enableCount, s_startCount, s_updateCount, s_disableCount, s_destroyCount, s_sendMessageCount, s_invokeCount };
        }
    }
}
