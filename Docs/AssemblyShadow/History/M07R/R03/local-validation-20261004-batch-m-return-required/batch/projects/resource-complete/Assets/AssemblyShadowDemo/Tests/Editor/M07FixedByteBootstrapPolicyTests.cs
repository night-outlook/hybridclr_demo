using System;
using System.IO;
using System.Linq;
using System.Reflection;
using HybridCLR.AssemblyShadow.CodeGen;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEditor;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M07FixedByteBootstrapPolicyTests
    {
        private const string SiteId = "h1-count-ordinary-witness-image";
        private const string Consumer = "AssemblyShadowDemo.Bootstrap";
        private const string Provider = "AssemblyShadowBaseline.HotUpdate";
        private const string ProviderIdentity = "AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null";
        private const string ConsumerType = "AssemblyShadowDemo.H1CountEarlyStartup";
        private const string CallSite = ConsumerType + "::LoadOrdinaryWitness";
        private const string MethodSignature = "AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()";
        private const string MethodHash = "fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e";
        private const string VariantHash = "4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e";
        private const string ImageSha = "9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27";
        private const string ImagePath = "Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes";
        private const string SourceEvidenceTarget = "image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4";

        [Test]
        public void RealM07PolicyBindsFixedBytesToExactlyTwoBootstrapEvidenceTargets()
        {
  BuildTarget target = EditorUserBuildSettings.activeBuildTarget;
  ShadowPolicyConfiguration policy = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(target);
  ReflectionBindingConfiguration bindings = ReflectionBindingConfiguration.Parse(File.ReadAllBytes(ReflectionBindingConfiguration.ProjectRelativePath));
  ReflectionBindingSite site = bindings.sites.Single(value => value.id == SiteId);
  Assert.AreEqual(4, bindings.schemaVersion);
  Assert.AreEqual("FixedAssemblyBytes", site.kind);
  Assert.AreEqual(Consumer, site.assembly);
  Assert.AreEqual(ConsumerType, site.typeName);
  Assert.AreEqual(MethodSignature, site.methodSignature);
  Assert.AreEqual(MethodHash, site.originalMethodHash);
  Assert.AreEqual(25, site.operationIndex);
  Assert.AreEqual(ImageSha, site.imageSha256);
  Assert.AreEqual(ImagePath, site.imagePath);
  Assert.AreEqual(ProviderIdentity, site.providerAssemblyIdentity);
  Assert.AreEqual(1, site.additionalMethodVariants.Length);
  Assert.AreEqual(VariantHash, site.additionalMethodVariants[0].originalMethodHash);
  Assert.AreEqual(25, site.additionalMethodVariants[0].operationIndex);
  Assert.AreEqual(bindings.ComputeHash(), policy.reflectionBindingConfigurationHash);

  BootstrapEntrypointDeclaration[] entries = policy.dependencies.bootstrapEntrypoints.Where(value => value != null &&
      string.Equals(string.IsNullOrWhiteSpace(value.callSite) ? value.method : value.callSite, CallSite, StringComparison.Ordinal)).ToArray();
  Assert.AreEqual(2, entries.Length);
  CollectionAssert.AreEquivalent(new[] { SourceEvidenceTarget, ImageSha }, entries.Select(value => value.target).ToArray());
  foreach (BootstrapEntrypointDeclaration entry in entries)
  {
      Assert.AreEqual(Consumer, entry.consumer);
      Assert.AreEqual(Provider, entry.provider);
      Assert.AreEqual("AssemblyShadowBaseline.HotUpdate.Entry", entry.typeName);
      Assert.IsFalse(string.IsNullOrWhiteSpace(entry.target));
      StringAssert.Contains(SiteId, entry.reason);
  }

  ShadowPolicyValidationResult real = ShadowAssemblyPolicyValidator.ValidateBeforeCompile(policy, target);
  Assert.IsTrue(real.IsValid, real.ToString());
        }

        [Test]
        public void BootstrapAdmissionRemainsTargetExactAndRejectsAnotherImage()
        {
  ShadowPolicyConfiguration source = AssemblyShadowSettingsUtil.CreatePolicyConfiguration(EditorUserBuildSettings.activeBuildTarget);
  BootstrapEntrypointDeclaration[] entries = source.dependencies.bootstrapEntrypoints.Where(value => value != null &&
      string.Equals(string.IsNullOrWhiteSpace(value.callSite) ? value.method : value.callSite, CallSite, StringComparison.Ordinal)).ToArray();
  var policy = new ShadowPolicyConfiguration {
      dependencies = new ShadowDependencyConfiguration { schemaVersion = 2, bootstrapEntrypoints = entries },
      rejectUnknownReflectionDependencies = true,
  };
  var bootstrap = new AssemblyPolicyDefinition { name = Consumer, classification = AssemblyClassification.Runtime,
      entersPlayer = true, isBootstrap = true, reflectionReferences = new[] { CallSite + "|" + SourceEvidenceTarget, CallSite + "|" + ImageSha } };
  var provider = new AssemblyPolicyDefinition { name = Provider, classification = AssemblyClassification.NormalHotUpdate, entersPlayer = true };
  Assert.IsTrue(ShadowAssemblyPolicyValidator.ValidateDefinitions(new[] { bootstrap, provider }, policy, DateTime.UtcNow).IsValid);
  bootstrap.reflectionReferences = new[] { CallSite + "|image:" + new string('0', 64) };
  ShadowPolicyValidationResult rejected = ShadowAssemblyPolicyValidator.ValidateDefinitions(new[] { bootstrap, provider }, policy, DateTime.UtcNow);
  Assert.IsFalse(rejected.IsValid);
  Assert.IsTrue(rejected.Errors.Any(value => value.Contains("BootstrapReflection")), rejected.ToString());
        }
    }
}
