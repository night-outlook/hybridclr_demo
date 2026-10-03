using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M01EditorValidationTests
    {
        [Test]
        public void M01EditorValidationPasses()
        {
            AssemblyShadowDemo.Editor.M01EditorValidation.Validate();
        }
    }
}
