using System;
using System.Linq;
using System.Threading;
using HybridCLR.Editor.AssemblyShadow;

namespace AssemblyShadowDemo.Editor
{
    // Reviewed fixture scope, never an inventory-dependent missing-plugin waiver.
    // Only the authenticated completion adapter enters this synchronous scope.
    internal static class R03ResourceCapabilityProfile
    {
        internal const string Id = "R03ResourceCapabilitiesV1";
        internal static string[] Included => new[] { "Newtonsoft.Json", "Unity.Burst.Unsafe", "nunit.framework" };
        internal static string[] Excluded => new[] { "Unity.Collections.LowLevel.ILSupport", "Unity.VisualScripting.Antlr3.Runtime" };
        private static int owner;
        internal static IDisposable Enter()
        {
            int thread = Thread.CurrentThread.ManagedThreadId;
            if (Interlocked.CompareExchange(ref owner, thread, 0) != 0)
                throw new InvalidOperationException("Resource capability scope cannot nest or overlap.");
            return new Scope(thread);
        }
        private sealed class Scope : IDisposable
        {
            private readonly int thread;
            private bool disposed;
            internal Scope(int thread) { this.thread = thread; }
            public void Dispose()
            {
                if (disposed) return;
                if (Thread.CurrentThread.ManagedThreadId != thread || Volatile.Read(ref owner) != thread)
                    throw new InvalidOperationException("Only the creating thread may release capability scope.");
                Volatile.Write(ref owner, 0); disposed = true;
            }
        }
        internal static AssemblyCapability[] Apply(AssemblyCapability[] inherited)
        {
            int current = Volatile.Read(ref owner);
            if (current == 0) return inherited; // Original M02/M07 behavior outside the adapter.
            if (current != Thread.CurrentThread.ManagedThreadId)
                throw new InvalidOperationException("Capability scope is owned by another thread.");
            return Select(inherited);
        }
        internal static AssemblyCapability[] Select(AssemblyCapability[] inherited)
        {
            string[] expected = Included.Concat(Excluded).OrderBy(n => n, StringComparer.Ordinal).ToArray();
            if (inherited == null || inherited.Length != expected.Length || inherited.Any(c => c == null) ||
                !inherited.Select(c => c.name).OrderBy(n => n, StringComparer.Ordinal).SequenceEqual(expected) ||
                inherited.Any(c => c.classification != AssemblyClassification.Runtime || c.isShadowCapable ||
                    c.isBootstrap || c.isPrecompiled || c.capabilityDeclared))
                throw new InvalidOperationException("Complete inherited five-declaration contract changed; review the resource profile.");
            // Do not consult CompilationPipeline here. Required plugins must be
            // present later, and excluded plugins must be absent, or validation fails.
            return Included.Select(n => new AssemblyCapability { name = n, isShadowCapable = false }).ToArray();
        }
    }
}
