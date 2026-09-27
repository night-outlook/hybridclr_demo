// Compile surface only. These stubs are not a Unity/IL2CPP or native acceptance model.
using System;
using System.Collections;
namespace UnityEngine.Scripting { public class PreserveAttribute : Attribute { } }
namespace UnityEngine
{
    public class SerializeField : Attribute { }
    public class MonoBehaviour { protected object gameObject; protected void DontDestroyOnLoad(object value) { } }
    public enum RuntimePlatform { OSXPlayer }
    public static class Application
    {
        public static string dataPath = "not-unity";
        public static string buildGUID = "host-only";
        public static string unityVersion = "not-unity";
        public static RuntimePlatform platform;
        public static void Quit(int value) { }
    }
    public static class Debug { public static void Log(string value) { } public static void LogException(Exception error) { } }
    public static class JsonUtility
    {
        public static string ToJson(object value, bool pretty) { return System.Text.Json.JsonSerializer.Serialize(value, new System.Text.Json.JsonSerializerOptions { IncludeFields = true }); }
    }
}
namespace HybridCLR
{
    public enum AssemblyShadowErrorCode { Success, FeatureDisabled }
    public static class AssemblyShadowRuntime
    {
        public static AssemblyShadowErrorCode GetExecutionDiagnosticsJson(out string json) { throw new NotSupportedException("Compile stub"); }
        public static AssemblyShadowErrorCode GetTypeResolutionInfo(Type type, out string json) { throw new NotSupportedException("Compile stub"); }
    }
}
namespace AssemblyShadowDemo
{
    public static class M07Probe
    {
        public static string Argument(string key, string fallback) { return fallback; }
        public static bool R00IsIl2CppPlayer() { return false; }
        public static IEnumerator RunAndWriteCoroutine(string a, string b, Action<int> c) { throw new NotSupportedException(); }
        public static int CompleteCoroutineFailure(Exception e) { return 1; }
    }
    public static class R01FailureProbe
    {
        public static IEnumerator RunAndWriteCoroutine(string a, string b, Action<int> c) { throw new NotSupportedException(); }
        public static int CompleteCoroutineFailure(Exception e) { return 1; }
    }
    public static class M07R01Probe
    {
        public static IEnumerator RunAndWriteCoroutine(string a, string b, Action<int> c) { throw new NotSupportedException(); }
        public static int CompleteCoroutineFailure(Exception e) { return 1; }
    }
    public static class M07R00PerformanceProbe
    {
        public static IEnumerator RunAndWriteCoroutine(string a, string b, Action<int> c) { throw new NotSupportedException(); }
        public static int CompleteCoroutineFailure(Exception e) { return 1; }
    }
    public static class R00ProcessMemory
    {
        public const string Measurement = "HostStub", MeasurementSemantics = "not-runtime";
        public struct Sample { public long CurrentRssBytes, ManagedBytes, LifetimePeakRssBytes; }
        public static Sample Capture() { throw new NotSupportedException("Compile stub"); }
    }
}
