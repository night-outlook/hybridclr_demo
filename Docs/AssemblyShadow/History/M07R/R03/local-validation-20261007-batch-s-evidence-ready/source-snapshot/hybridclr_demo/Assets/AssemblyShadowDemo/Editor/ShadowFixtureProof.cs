using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using UnityEditor.Build;
using ReflectionAssemblyName = System.Reflection.AssemblyName;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Shared byte-backed proof primitives, not milestone schema admission.</summary>
    internal static class ShadowFixtureProof
    {
        internal static M03Build.StableAotProvenance DeriveStableAotNames(string snapshotRoot, AssemblySnapshotReceipt receipt, ShadowPolicyConfiguration policy, string hashDomain)
        {
            var framework = TargetFrameworkReferenceVerifier.Verify(snapshotRoot, receipt);
            var libraries = M03CompilerLibraryVerifier.Verify(snapshotRoot, receipt, framework);
            var candidateSet = new HashSet<string>(M02Build.Candidates.Select(AssemblyIdentityUtil.CanonicalName), StringComparer.OrdinalIgnoreCase);
            // Only linked bytes prove physical AOT membership. Compiler-only
            // facade references and arbitrary Bootstrap dependencies are not an
            // authorization to escape the transaction closure.
            ShadowLinkedPlayerEvidence.ReadAndVerify(snapshotRoot, receipt);
            var physicalByCanonical = receipt.linkedPlayerReceipt.assemblies
                .ToDictionary(item => AssemblyIdentityUtil.CanonicalName(item.name), item => item.name, StringComparer.OrdinalIgnoreCase);
            var compilerNames = new HashSet<string>(framework.Providers.Concat(libraries.Providers).Select(ProviderName), StringComparer.OrdinalIgnoreCase);
            var bootstrapNames = new HashSet<string>((policy.assemblies ?? new AssemblyCapability[0]).Where(item => item != null && item.isBootstrap)
                .Select(item => AssemblyIdentityUtil.CanonicalName(item.name)), StringComparer.OrdinalIgnoreCase);
            Require(bootstrapNames.Count > 0, "M03 policy has no fixed Bootstrap assembly.");

            var required = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string name in compilerNames)
            {
                string physicalName;
                if (physicalByCanonical.TryGetValue(name, out physicalName) && !candidateSet.Contains(name)) required.Add(physicalName);
            }

            foreach (string bootstrap in bootstrapNames)
            {
                string physicalName;
                Require(physicalByCanonical.TryGetValue(bootstrap, out physicalName) && !candidateSet.Contains(bootstrap),
                    "Fixed Bootstrap is absent from linked physical AOT: " + bootstrap);
                required.Add(physicalName);
            }

            string[] names = required.OrderBy(item => item, StringComparer.Ordinal).ToArray();
            Require(names.Length > 0, "Verified Bootstrap has no physical stable AOT dependencies.");
            string provenance = "framework=" + framework.ProvenanceHash + "\ncompiler-libraries=" + libraries.ProvenanceHash +
                "\nlinked-player=" + receipt.linkedPlayerReceiptHash + "\nbootstrap-policy=" +
                string.Join(",", bootstrapNames.OrderBy(item => item, StringComparer.Ordinal).ToArray()) + "\nphysical=" +
                string.Join(",", names);
            return new M03Build.StableAotProvenance {
                names = names,
                provenance = provenance,
                provenanceHash = ShadowHash.Text(hashDomain + provenance),
            };
        }


        private static string ProviderName(string value)
        {
            int separator = value.IndexOf(" | ", StringComparison.Ordinal);
            string identity = separator < 0 ? value : value.Substring(0, separator);
            return AssemblyIdentityUtil.CanonicalName(new ReflectionAssemblyName(identity).Name);
        }


        internal static CompiledAssemblySet Load(string root, AssemblySnapshotReceipt receipt, ShadowPolicyConfiguration policy)
        {
            ShadowReflectionBindingEvidence.RequirePolicy(policy, root, receipt, receipt.kind == "PlayerBuildInputs");
            var framework = TargetFrameworkReferenceVerifier.Verify(root, receipt);
            return DnlibAssemblyLoader.Load(Path.Combine(root, "Assemblies"), new[] { Path.Combine(root, "References") }, policy.assemblies, targetFrameworkReferences: framework);
        }


        internal static string BootstrapHash(IEnumerable<AssemblyDescriptor> descriptors)
        {
            return ShadowHash.Text("bootstrap-abi:1\n" + string.Join("\n", descriptors.Where(a => a.isBootstrap).OrderBy(a => a.name, StringComparer.Ordinal).Select(a => AssemblyIdentityUtil.CanonicalName(a.name) + ":" + a.semanticHash)));
        }


        private static void Require(bool condition, string message)
        {
            if (!condition) throw new BuildFailedException(message);
        }
    }
}
