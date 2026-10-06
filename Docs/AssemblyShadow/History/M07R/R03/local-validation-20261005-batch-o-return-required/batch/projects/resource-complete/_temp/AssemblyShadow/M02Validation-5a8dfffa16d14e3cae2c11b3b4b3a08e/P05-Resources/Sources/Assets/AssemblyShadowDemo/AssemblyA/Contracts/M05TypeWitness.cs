#if ASSEMBLY_SHADOW_M05_P03
using System;

namespace AssemblyA.Contracts
{
    public interface IM05ContractPayload { int Value { get; } }

    public sealed class M05ContractPayload : IM05ContractPayload
    {
        public int Value { get { return 501; } }
        public M05ContractPayload Field;
        public M05ContractPayload Property { get; set; }
        public event Action<M05ContractPayload> Changed;
        public M05ContractPayload Echo(M05ContractPayload value) { if (Changed != null) Changed(value); return value; }
    }

    public sealed class M05ContractGeneric<T> { public T Value; }

    public sealed class M05ContractOuter
    {
        public sealed class Inner { }
    }

    public static partial class AssemblyAContractVersion
    {
        public static Type[] GetM05Types()
        {
            return new[] { typeof(M05ContractPayload), typeof(M05ContractGeneric<>), typeof(M05ContractOuter), typeof(M05ContractOuter.Inner) };
        }

        public static object GetM05Payload()
        {
            return new M05ContractPayload();
        }

        public static object GetM05InterfacePayload()
        {
            IM05ContractPayload payload = new M05ContractPayload();
            return payload;
        }

        public static object GetM05InterfaceCastResult()
        {
            object payload = new M05ContractPayload();
            IM05ContractPayload cast = payload as IM05ContractPayload;
            return cast == null ? "FAIL" : cast.Value.ToString();
        }

        public static Type[] GetM05TypeNameForms()
        {
            return new[] {
                Type.GetType("AssemblyA.Contracts.M05ContractPayload, AssemblyA.Contracts", true),
                Type.GetType("AssemblyA.Contracts.M05ContractOuter+Inner, AssemblyA.Contracts", true),
                Type.GetType("AssemblyA.Contracts.M05ContractGeneric`1[[System.Int32, mscorlib]], AssemblyA.Contracts", true),
            };
        }
    }
}
#endif
