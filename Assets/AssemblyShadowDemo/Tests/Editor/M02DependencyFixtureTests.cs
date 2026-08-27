using System;
using System.IO;
using System.Linq;
using HybridCLR.Editor.AssemblyShadow;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M02DependencyFixtureTests
    {
        private const string Contracts = "AssemblyA.Contracts";
        private const string Extensibility = "AssemblyA.Implementation.Extensibility";
        private const string Internal = "AssemblyA.Implementation.Internal";
        private const string DefinitionPath = "Assets/AssemblyShadowDemo/AssemblyA/Implementation/Extensibility/AssemblyA.Implementation.Extensibility.asmdef";

        [Test]
        public void DeclaredModuleContractRetainsCompleteP03Closure()
        {
            var configuration = ReadModuleContract();
            var definitions = FixtureDescriptors();
            var graph = new AssemblyReferenceGraph(definitions, configuration);
            CollectionAssert.AreEquivalent(new[] { Internal }, graph.ReverseClosure(new[] { Internal }));
            CollectionAssert.AreEquivalent(new[] { Extensibility, Internal, "AssemblyShadowDemo.ExtensibilityConsumer" }, graph.ReverseClosure(new[] { Extensibility }));
            CollectionAssert.AreEquivalent(AssemblyShadowDemo.Editor.M02Build.Candidates, graph.ReverseClosure(new[] { Contracts }));
            Assert.AreEqual(Contracts, graph.LoadOrder(AssemblyShadowDemo.Editor.M02Build.Candidates)[0]);

            var withoutDeclaration = new AssemblyReferenceGraph(definitions);
            CollectionAssert.AreEquivalent(new[] { Contracts, Internal, "AssemblyShadowDemo.ContractsConsumer" }, withoutDeclaration.ReverseClosure(new[] { Contracts }));
            var frozenEdges = new AssemblyReferenceGraph(definitions, requiredBaselineEdges: graph.Edges);
            CollectionAssert.AreEquivalent(AssemblyShadowDemo.Editor.M02Build.Candidates, frozenEdges.ReverseClosure(new[] { Contracts }));
        }

        [Test]
        public void ModuleContractIsDeclaredRatherThanInventedAsAnAssemblyReference()
        {
            var definition = JsonUtility.FromJson<Definition>(File.ReadAllText(DefinitionPath));
            CollectionAssert.Contains(definition.references, Contracts);
            var declaration = ReadModuleContract().runtimeDependencies.Single();
            Assert.AreEqual("ModuleContract", declaration.kind);
            StringAssert.Contains(DefinitionPath, declaration.evidence);
            Assert.IsFalse(FixtureDescriptors().Single(item => item.name == Extensibility).references.Contains(Contracts),
                "If the fixture starts emitting a real AssemblyRef, replace the now-duplicate explicit dependency deliberately.");
        }

        private static ShadowDependencyConfiguration ReadModuleContract()
        {
            var configuration = JsonUtility.FromJson<ShadowDependencyConfiguration>(File.ReadAllText("ProjectSettings/AssemblyShadowDependencies.json"));
            var declarations = configuration.runtimeDependencies.Where(edge => edge.consumer == Extensibility && edge.provider == Contracts).ToArray();
            Assert.AreEqual(1, declarations.Length, "The demo's no-token module dependency must be explicit and unique.");
            return new ShadowDependencyConfiguration { runtimeDependencies = declarations };
        }

        private static AssemblyDescriptor[] FixtureDescriptors()
        {
            // This is an Editor fixture regression only. T02 compiles and verifies
            // actual target DLLs; production never substitutes Editor-domain DLLs.
            var loaded = AppDomain.CurrentDomain.GetAssemblies();
            return AssemblyShadowDemo.Editor.M02Build.Candidates.Select(name =>
            {
                var assembly = loaded.Single(item => item.GetName().Name == name);
                return new AssemblyDescriptor { name = name, classification = AssemblyClassification.Runtime,
                    isShadowCapable = true, references = assembly.GetReferencedAssemblies().Select(item => item.Name).ToArray() };
            }).ToArray();
        }

        [Serializable] private sealed class Definition { public string[] references; }
    }
}
