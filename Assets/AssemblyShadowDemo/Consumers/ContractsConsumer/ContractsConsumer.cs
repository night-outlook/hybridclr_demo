using AssemblyA.Contracts;

namespace AssemblyShadowDemo.Consumers
{
    public static partial class ContractsConsumer
    {
        public static string ReadContractVersion()
        {
            return AssemblyAContractVersion.Value;
        }

        public static string ReadValueText(DemoValue value)
        {
            return value == null ? null : value.text;
        }
    }
}
