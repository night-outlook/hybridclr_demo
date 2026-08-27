using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M02ReflectionBindingValidationTests
    {
        [Test]
        public void FiniteDomainMatchesActualSerializedPrefab()
        {
            AssemblyShadowDemo.Editor.M02ReflectionBindingValidation.ValidateProjectAssets();
        }

        [Test]
        public void EditorDomainRemainsUnmodified()
        {
            AssemblyShadowDemo.Editor.M02ReflectionBindingValidation.ValidateEditorBehavior();
        }
    }
}
