// Host-only compilation surface. This is NOT the Unity engine/HybridCLR runtime.
using System;
using System.Text.Json;

namespace UnityEngine
{
    public enum RuntimePlatform { OSXPlayer }
    public enum RuntimeInitializeLoadType { BeforeSceneLoad }
    [AttributeUsage(AttributeTargets.Method)]
    public sealed class RuntimeInitializeOnLoadMethodAttribute : Attribute
    {
        public RuntimeInitializeOnLoadMethodAttribute(RuntimeInitializeLoadType value) {}
    }
    public static class Application
    {
        public static string unityVersion { get { return "2022.3.62f2"; } }
        public static RuntimePlatform platform { get { return RuntimePlatform.OSXPlayer; } }
    }
    public static class JsonUtility
    {
        public static T FromJson<T>(string value)
        {
            return JsonSerializer.Deserialize<T>(value, new JsonSerializerOptions { IncludeFields = true });
        }
    }
}
namespace UnityEngine.Scripting
{
    [AttributeUsage(AttributeTargets.All)]
    public sealed class PreserveAttribute : Attribute {}
}
namespace HybridCLR
{
    public enum AssemblyShadowErrorCode { Success = 0 }
    public enum AssemblyShadowState { Disabled = 0, Committed = 6, FailedAfterCommit = 9 }
    public static class AssemblyShadowRuntime
    {
        public static AssemblyShadowErrorCode ConfigureCandidates(
            string baseline, string[] candidates, string[] stable)
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode BeginTransaction(
            string patch, string baseline, string[] closure, int level)
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode ReserveMetadataBudget(long[] sizes, int level)
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode StageAssembly(byte[] bytes, object data)
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode ValidateTransaction()
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode CommitTransaction()
        { return AssemblyShadowErrorCode.Success; }
        public static AssemblyShadowErrorCode GetState(out AssemblyShadowState state)
        { state = AssemblyShadowState.Committed; return AssemblyShadowErrorCode.Success; }
    }
}
