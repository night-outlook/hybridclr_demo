#if ASSEMBLY_SHADOW_M05
using System;
using System.Collections.Generic;
using AssemblyA.Contracts;
using UnityEngine;

namespace AssemblyA.Implementation.Internal
{
    public sealed class M05InternalPayload
    {
        public int Value { get { return 505; } }
        public M05InternalPayload Field;
        public M05InternalPayload Property { get; set; }
        public event Action<M05InternalPayload> Changed;
        public M05InternalPayload Echo(M05InternalPayload value) { if (Changed != null) Changed(value); return value; }
    }
    public sealed class M05InternalGeneric<T> { public T Value; }
    public sealed class M05InternalOuter { public sealed class Inner { } }
    public sealed class M05InternalGenericOuter<T> { public sealed class Inner<U> { } }
    public sealed class M05InternalInterfacePayload : IVersionTextProvider
    {
        public int Value { get { return 506; } }
        public string GetVersionText() { return "M05-INTERNAL"; }
    }

    public sealed partial class InternalEntry
    {
        public static Type[] GetM05Types()
        {
            return new[] { typeof(M05InternalPayload), typeof(M05InternalGeneric<>), typeof(M05InternalOuter), typeof(M05InternalOuter.Inner), typeof(M05InternalInterfacePayload) };
        }

        public static Type[] GetM05CompositeTypes()
        {
            return new[] {
                typeof(List<M05InternalPayload>), typeof(Dictionary<string, M05InternalPayload>),
                typeof(M05InternalGeneric<int>), typeof(M05InternalGeneric<M05InternalPayload>),
                typeof(M05InternalGenericOuter<int>.Inner<M05InternalPayload>),
                typeof(M05InternalPayload[]), typeof(M05InternalPayload[,]),
                typeof(M05InternalPayload).MakeByRefType(), typeof(M05InternalPayload).MakePointerType()
            };
        }

        public static object GetM05CompositeArrays()
        {
            return new Array[] { new M05InternalPayload[2], new M05InternalPayload[1, 2] };
        }

        public static object GetM05Payload()
        {
            return new M05InternalPayload();
        }

        public static object GetM05InterfacePayload()
        {
            IVersionTextProvider provider = new M05InternalInterfacePayload();
            return provider;
        }

        public static object GetM05InterfaceCastResult()
        {
            object payload = new M05InternalInterfacePayload();
            IVersionTextProvider cast = payload as IVersionTextProvider;
            return cast == null ? "FAIL" : cast.GetVersionText();
        }

        public static string GetM05PayloadText()
        {
            return ((M05InternalPayload)GetM05Payload()).Value.ToString();
        }

        public static Type[] GetM05TypeNameForms()
        {
            return new[] {
                Type.GetType("AssemblyA.Implementation.Internal.M05InternalPayload, AssemblyA.Implementation.Internal", true),
                Type.GetType("AssemblyA.Implementation.Internal.M05InternalOuter+Inner, AssemblyA.Implementation.Internal", true),
                Type.GetType("AssemblyA.Implementation.Internal.M05InternalGeneric`1[[System.Int32, mscorlib]], AssemblyA.Implementation.Internal", true),
            };
        }
    }
}
#endif

#if ASSEMBLY_SHADOW_M05 && ASSEMBLY_SHADOW_M05_LAYOUT_MISMATCH
namespace AssemblyA.Implementation.Internal
{
    public sealed partial class VersionedPrefabComponent : ISerializationCallbackReceiver
    {
        // Keep Unity's Editor/Player serialized schema identical so the public
        // compiler can emit this test-only DLL. The native instance layout still
        // changes, and callback access to unproven nonserialized state must be
        // rejected by the normal DLL-only resource policy before deployment.
        [NonSerialized] private int m05BadLayoutField = 99;

        public void OnBeforeSerialize() { ++m05BadLayoutField; }
        public void OnAfterDeserialize() { m05BadLayoutField = 99; }
    }
}
#endif
