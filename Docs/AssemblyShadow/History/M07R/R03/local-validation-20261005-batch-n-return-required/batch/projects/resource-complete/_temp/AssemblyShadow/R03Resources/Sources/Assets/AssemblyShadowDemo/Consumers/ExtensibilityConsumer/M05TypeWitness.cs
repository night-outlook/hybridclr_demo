#if ASSEMBLY_SHADOW_M05_P03
using System;
using AssemblyA.Contracts;
using AssemblyA.Implementation.Extensibility;

namespace AssemblyShadowDemo.Consumers
{
    public sealed class M05ExtensibilityConsumerPayload : M05ExtensibilityPayload, IVersionTextProvider
    {
        public new string Text { get { return "M05-EXT-CONSUMER"; } }
        public new M05ExtensibilityConsumerPayload Field;
        public new M05ExtensibilityConsumerPayload Property { get; set; }
        public new event Action<M05ExtensibilityConsumerPayload> Changed;
        public M05ExtensibilityConsumerPayload Echo(M05ExtensibilityConsumerPayload value) { if (Changed != null) Changed(value); return value; }
        public override string GetDispatchText() { return "M05-EXT-CONSUMER"; }
        public string GetVersionText() { return "M05-SHADOW-CONTRACTS"; }
    }
    public sealed class M05ExtensibilityConsumerGeneric<T> { public T Value; }
    public sealed class M05ExtensibilityConsumerOuter { public sealed class Inner { } }

#pragma warning disable 0108
    public sealed partial class DerivedExternalComponent
    {
        public static object GetM05ConsumerDispatch(object value)
        {
            M05ExtensibilityPayload parent = (M05ExtensibilityPayload)value;
            IVersionTextProvider contract = (IVersionTextProvider)value;
            return parent.GetDispatchText() + "|" + contract.GetVersionText();
        }

        public static Type[] GetM05Types()
        {
            return new[] { typeof(M05ExtensibilityConsumerPayload), typeof(M05ExtensibilityConsumerGeneric<>), typeof(M05ExtensibilityConsumerOuter), typeof(M05ExtensibilityConsumerOuter.Inner) };
        }

        public static object GetM05Payload()
        {
            return new M05ExtensibilityConsumerPayload();
        }

        public static Type[] GetM05TypeNameForms()
        {
            return new[] {
                Type.GetType("AssemblyShadowDemo.Consumers.M05ExtensibilityConsumerPayload, AssemblyShadowDemo.ExtensibilityConsumer", true),
                Type.GetType("AssemblyShadowDemo.Consumers.M05ExtensibilityConsumerOuter+Inner, AssemblyShadowDemo.ExtensibilityConsumer", true),
                Type.GetType("AssemblyShadowDemo.Consumers.M05ExtensibilityConsumerGeneric`1[[System.Int32, mscorlib]], AssemblyShadowDemo.ExtensibilityConsumer", true),
            };
        }
    }
#pragma warning restore 0108
}
#endif
