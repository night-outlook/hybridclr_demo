// Compile surface only; never claims a Unity compiler execution.
using System;
namespace UnityEditor
{
    public enum BuildTarget { StandaloneOSX }
    public enum ImportAssetOptions { ForceSynchronousImport }
    public static class EditorUserBuildSettings { public static BuildTarget activeBuildTarget; }
    public static class AssetDatabase
    { public static void Refresh(ImportAssetOptions options) { throw new NotSupportedException("Compile stub"); } }
}
namespace UnityEditor.Build
{ public class BuildFailedException : Exception { public BuildFailedException(string message) : base(message) { } } }
namespace HybridCLR.Editor.Commands
{
    public static class CompileDllCommand
    { public static void CompileDll(string output, UnityEditor.BuildTarget target, bool development)
        { throw new NotSupportedException("Compile stub, not the Unity compiler"); } }
}
namespace AssemblyShadowBaseline.Editor
{
    public static class BaselineBuild
    { public static string Argument(string key, string fallback) { throw new NotSupportedException("Compile stub"); } }
}
