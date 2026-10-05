using System;
// Unused model dependencies only. Image guards, JSON parsing and hashing are
// actual package sources; no Unity or acquisition-policy execution is claimed.
namespace HybridCLR.Editor.AssemblyShadow
{
    public sealed class ShadowReflectionBindingDeclaration { }
    public static class BootstrapIsolationRule
    {
        public static string CallSite(BootstrapEntrypointDeclaration entry)
        { throw new NotSupportedException("Bootstrap policy is outside fixed-image host checks."); }
    }
}
