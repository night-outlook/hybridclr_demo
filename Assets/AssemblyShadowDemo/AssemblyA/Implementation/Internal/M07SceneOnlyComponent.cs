using UnityEngine;
using UnityEngine.Events;

namespace AssemblyA.Implementation.Internal
{
    public sealed class M07SceneOnlyComponent : MonoBehaviour, ISerializationCallbackReceiver
    {
        [SerializeField] private int sceneValue = 707;
        [SerializeField] private VersionedScriptableObject dataReference;
        [SerializeField] private M07ManagedGraphAsset graphReference;
        [SerializeField] private UnityEngine.Object serializedInterfaceObject;
        [SerializeField] private UnityEvent persistentEvent = new UnityEvent();
        [SerializeField] private int beforeSerializeCount;
        [SerializeField] private int afterDeserializeCount;

        private static int s_beforeSerializeCount;
        private static int s_afterDeserializeCount;
        private static int s_awakeCount;
        private static int s_enableCount;
        private static int s_startCount;
        private static int s_updateCount;
        private static int s_disableCount;
        private static int s_destroyCount;
        private static int s_eventCount;
        private static int s_sendMessageCount;
        private static int s_invokeCount;
        private static int s_pauseCount;
        private static string s_lastMarker;

        public void OnBeforeSerialize() { ++beforeSerializeCount; }
        public void OnAfterDeserialize() { ++afterDeserializeCount; }
        public void PublishCallbackCounters()
        {
            s_beforeSerializeCount = beforeSerializeCount;
            s_afterDeserializeCount = afterDeserializeCount;
        }
        private void Awake() { ++s_awakeCount; s_lastMarker = Marker(); }
        private void OnEnable() { ++s_enableCount; s_lastMarker = Marker(); }
        private void Start() { ++s_startCount; s_lastMarker = Marker(); }
        private void Update() { ++s_updateCount; }
        private void OnDisable() { ++s_disableCount; s_lastMarker = Marker(); }
        private void OnDestroy() { ++s_destroyCount; s_lastMarker = Marker(); }
        private void M07ReceiveMessage(string value) { if (value == "M07-SEND") { ++s_sendMessageCount; s_lastMarker = Marker(); } }
        private void M07Invoked() { ++s_invokeCount; s_lastMarker = Marker(); }
        private void OnApplicationPause(bool paused) { s_pauseCount += paused ? 1 : 10; s_lastMarker = Marker(); }

        public void OnM07UnityEvent() { ++s_eventCount; s_lastMarker = Marker(); }
        public void InvokePersistentEvent() { persistentEvent.Invoke(); }
        public void InvokeStringPaths()
        {
            SendMessage("M07ReceiveMessage", "M07-SEND", SendMessageOptions.RequireReceiver);
            Invoke("M07Invoked", 0f);
        }

        public string ReadSerializedState()
        {
            return sceneValue + "|" + (dataReference == null ? "null" : dataReference.name) + "|" +
                (graphReference == null ? "null" : graphReference.name) + "|" +
                (serializedInterfaceObject == null ? "null" : serializedInterfaceObject.GetType().FullName);
        }

        public static string ReadCounters()
        {
            return string.Join("|", new object[] { s_beforeSerializeCount, s_afterDeserializeCount, s_awakeCount, s_enableCount, s_startCount,
                s_updateCount, s_disableCount, s_destroyCount, s_eventCount, s_sendMessageCount, s_invokeCount, s_pauseCount }) + "|" + (s_lastMarker ?? "");
        }

        public static string Marker()
        {
#if ASSEMBLY_SHADOW_P05
            return "M07-P05-SCENE";
#elif ASSEMBLY_SHADOW_M07_P04
            return "M07-P04-SCENE";
#elif ASSEMBLY_SHADOW_P03
            return "M07-P03-SCENE";
#elif ASSEMBLY_SHADOW_P01
            return "M07-P01-SCENE";
#else
            return "M07-BASELINE-SCENE";
#endif
        }
    }
}
