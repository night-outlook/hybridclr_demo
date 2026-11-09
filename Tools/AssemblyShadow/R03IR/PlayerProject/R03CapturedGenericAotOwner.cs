// R03 captured-baseline generic witness owner. Test-only AOT candidate.
// Do not resolve or materialize the physical Methods baseline type during
// startup/prepublication. Future Player code must acquire that type under an
// explicitly reviewed, source-bound guard and prove real method-inst context.
// The .NET host compiles this same source but is NOT a Unity/IL2CPP Player.
using System;
using System.Runtime.CompilerServices;
using System.Threading;

namespace AssemblyShadow.R03.IR
{
#if UNITY_2022_3_OR_NEWER
    [UnityEngine.Scripting.Preserve]
#endif
    public static class R03CapturedGenericAotOwner
    {
        private static int s_calls;

        public static int Calls { get { return Volatile.Read(ref s_calls); } }

        // No compile-time reference to any type defined in Methods.dll.
        // In a future real Player, the closed generic MethodInfo must be
        // owned by this physical AOT type while its T is the physical,
        // original (not interpreter) Methods.R03.Node.
#if UNITY_2022_3_OR_NEWER
        [UnityEngine.Scripting.Preserve]
#endif
        [MethodImpl(MethodImplOptions.NoInlining)]
        public static int Touch<T>() where T : class
        {
            // The reference-type constraint is verified when the method closes.
            // Avoid T's class metadata/RGCTX access before the native method
            // guard: inflation must not materialize physical Methods.R03.Node.
            Interlocked.Increment(ref s_calls);
            return 42;
        }

        // Warm a reference-type AOT instantiation without ever touching
        // Methods.R03.Node. WarmShared is a positive control, not permission
        // to run Touch<Methods.R03.Node> before Shadow publication.
#if UNITY_2022_3_OR_NEWER
        [UnityEngine.Scripting.Preserve]
#endif
        [MethodImpl(MethodImplOptions.NoInlining)]
        public static int WarmShared()
        {
            return Touch<object>();
        }
    }
}
