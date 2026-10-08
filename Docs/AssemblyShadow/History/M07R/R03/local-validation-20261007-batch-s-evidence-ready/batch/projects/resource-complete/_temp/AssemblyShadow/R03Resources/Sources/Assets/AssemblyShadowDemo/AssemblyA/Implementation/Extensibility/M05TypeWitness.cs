#if ASSEMBLY_SHADOW_M05_P03
using System;

namespace AssemblyA.Implementation.Extensibility
{
    public class M05ExtensibilityPayload
    {
        public string Text { get { return "M05-EXT"; } }
        public M05ExtensibilityPayload Field;
        public M05ExtensibilityPayload Property { get; set; }
        public event Action<M05ExtensibilityPayload> Changed;
        public M05ExtensibilityPayload Echo(M05ExtensibilityPayload value) { if (Changed != null) Changed(value); return value; }
        public virtual string GetDispatchText() { return "M05-EXT-BASE"; }
    }
    public sealed class M05ExtensibilityGeneric<T> { public T Value; }
    public sealed class M05ExtensibilityOuter { public sealed class Inner { } }

    public abstract partial class VersionedComponentBase
    {
        public static Type[] GetM05Types()
        {
            return new[] { typeof(M05ExtensibilityPayload), typeof(M05ExtensibilityGeneric<>), typeof(M05ExtensibilityOuter), typeof(M05ExtensibilityOuter.Inner) };
        }

        public static object GetM05Payload()
        {
            return new M05ExtensibilityPayload();
        }

        public static Type[] GetM05TypeNameForms()
        {
            return new[] {
                Type.GetType("AssemblyA.Implementation.Extensibility.M05ExtensibilityPayload, AssemblyA.Implementation.Extensibility", true),
                Type.GetType("AssemblyA.Implementation.Extensibility.M05ExtensibilityOuter+Inner, AssemblyA.Implementation.Extensibility", true),
                Type.GetType("AssemblyA.Implementation.Extensibility.M05ExtensibilityGeneric`1[[System.Int32, mscorlib]], AssemblyA.Implementation.Extensibility", true),
            };
        }
    }
}
#endif
