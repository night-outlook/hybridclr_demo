#if ASSEMBLY_SHADOW_M05_P03
using System;
using AssemblyA.Contracts;

namespace AssemblyShadowDemo.Consumers
{
    public sealed class M05ContractsConsumerPayload
    {
        public string Text { get { return "M05-CONTRACTS-CONSUMER"; } }
        public M05ContractsConsumerPayload Field;
        public M05ContractsConsumerPayload Property { get; set; }
        public event Action<M05ContractsConsumerPayload> Changed;
        public M05ContractsConsumerPayload Echo(M05ContractsConsumerPayload value) { if (Changed != null) Changed(value); return value; }
    }
    public sealed class M05ContractsConsumerGeneric<T> { public T Value; }
    public sealed class M05ContractsConsumerOuter { public sealed class Inner { } }

    public static partial class ContractsConsumer
    {
        public static object GetM05ConsumerDispatch(object value)
        {
            return ((IVersionTextProvider)value).GetVersionText() + "|CONTRACTS-CONSUMER";
        }

        public static Type[] GetM05Types()
        {
            return new[] { typeof(M05ContractsConsumerPayload), typeof(M05ContractsConsumerGeneric<>), typeof(M05ContractsConsumerOuter), typeof(M05ContractsConsumerOuter.Inner) };
        }

        public static object GetM05Payload()
        {
            return new M05ContractsConsumerPayload();
        }

        public static Type[] GetM05TypeNameForms()
        {
            return new[] {
                Type.GetType("AssemblyShadowDemo.Consumers.M05ContractsConsumerPayload, AssemblyShadowDemo.ContractsConsumer", true),
                Type.GetType("AssemblyShadowDemo.Consumers.M05ContractsConsumerOuter+Inner, AssemblyShadowDemo.ContractsConsumer", true),
                Type.GetType("AssemblyShadowDemo.Consumers.M05ContractsConsumerGeneric`1[[System.Int32, mscorlib]], AssemblyShadowDemo.ContractsConsumer", true),
            };
        }
    }
}
#endif
