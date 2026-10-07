using System;

// The host suite executes the production graph, model, identity and semantic
// hasher against real DLL bytes. It does not execute Unity's acquisition policy.
// Fail loudly if a test accidentally crosses one of those unlinked boundaries.
namespace HybridCLR.Editor.AssemblyShadow
{
    public sealed class ShadowReflectionBindingDeclaration { }
    public static class BootstrapIsolationRule
    {
        public static string CallSite(BootstrapEntrypointDeclaration entry)
        { throw new NotSupportedException("Bootstrap acquisition policy requires the real Editor suite."); }
    }
}
namespace HybridCLR.AssemblyShadow.CodeGen
{
    public static class ReflectionBindingConfiguration
    {
        public static string ProviderOf(string value)
        { throw new NotSupportedException("SerializeReference policy requires the real Editor suite."); }
    }
}
