using System;
using System.Linq;
using System.Reflection;
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

        [Test]
        public void RuntimeProbeRejectsSiteSetAndH1WitnessMutations()
        {
            Type probe = typeof(AssemblyShadowDemo.M02ReflectionBindingProbe);
            MethodInfo membership = probe.GetMethod("ValidateExactSiteMembership", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.That(membership, Is.Not.Null);
            var siteIds = new[]
            {
                "urp-debug-ui-prefab-types",
                "urp-serializable-enum-player",
                "urp-volume-assembly-domain",
                "urp-volume-type-domain",
                "m00-normal-hot-update-image",
                "h1-count-ordinary-witness-image",
            };
            Assert.DoesNotThrow(() => membership.Invoke(null, new object[] { siteIds }));
            AssertValidatorRejects(membership, (object)siteIds.Take(5).ToArray());
            AssertValidatorRejects(membership, (object)siteIds.Concat(new[] { siteIds[0] }).ToArray());

            MethodInfo witness = probe.GetMethod("ValidateH1WitnessContract", BindingFlags.NonPublic | BindingFlags.Static);
            Assert.That(witness, Is.Not.Null);
            object[] valid =
            {
                "AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()",
                "fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e",
                25,
                "4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e",
                25,
                "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27",
                "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null",
            };
            Assert.DoesNotThrow(() => witness.Invoke(null, valid));
            foreach (int index in new[] { 0, 1, 2, 3, 4, 5, 6 })
            {
                object[] mutated = (object[])valid.Clone();
                if (index == 0) mutated[index] = "AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt AssemblyShadowDemo.H1CountEarlyStartup::Other()";
                if (index == 1) mutated[index] = "wrong-method-hash";
                if (index == 2 || index == 4) mutated[index] = 24;
                if (index == 3) mutated[index] = "wrong-variant-hash";
                if (index == 5) mutated[index] = "wrong-image-hash";
                if (index == 6) mutated[index] = "wrong-provider";
                AssertValidatorRejects(witness, mutated);
            }
        }

        private static void AssertValidatorRejects(MethodInfo validator, params object[] arguments)
        {
            var error = Assert.Throws<TargetInvocationException>(() => validator.Invoke(null, arguments));
            Assert.That(error.InnerException, Is.TypeOf<InvalidOperationException>());
        }
    }
}
