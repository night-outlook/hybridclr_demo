using System;

// Compile-only stand-ins for Unity's environment. No HybridCLR API is stubbed:
// every transaction signature and DTO is compiled from the pinned package.
// This project must never be executed or used as native behavior evidence.
namespace UnityEngine
{
    public enum RuntimeInitializeLoadType { BeforeSceneLoad }
    [AttributeUsage(AttributeTargets.Method)]
    public sealed class RuntimeInitializeOnLoadMethodAttribute : Attribute
    { public RuntimeInitializeOnLoadMethodAttribute(RuntimeInitializeLoadType value) { } }
    public enum RuntimePlatform { OSXPlayer }
    public class Object { }
    public enum LogType { Error, Assert, Warning, Log, Exception }
    public interface ILogHandler
    {
        void LogException(Exception exception, Object context);
        void LogFormat(LogType type, Object context, string format, params object[] args);
    }
    public interface ILogger : ILogHandler
    {
        ILogHandler logHandler { get; set; }
    }
    public static class Application
    {
        public static string unityVersion { get { throw new NotSupportedException(); } }
        public static RuntimePlatform platform { get { throw new NotSupportedException(); } }
        public static void Quit(int code) { throw new NotSupportedException(); }
    }
    public static class Debug
    {
        public static ILogger unityLogger { get { throw new NotSupportedException(); } }
        public static void LogException(Exception error) { throw new NotSupportedException(); }
    }
    public static class JsonUtility
    {
        public static T FromJson<T>(string json) { throw new NotSupportedException(); }
        public static string ToJson(object value, bool pretty = false) { throw new NotSupportedException(); }
    }
}
namespace UnityEngine.Scripting
{
    [AttributeUsage(AttributeTargets.All)]
    public sealed class PreserveAttribute : Attribute { }
}
