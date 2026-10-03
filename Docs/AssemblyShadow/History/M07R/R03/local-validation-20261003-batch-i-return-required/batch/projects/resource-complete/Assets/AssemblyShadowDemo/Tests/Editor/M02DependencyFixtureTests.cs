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
        public void ActualAssemblyReferenceRetainsCompleteP03Closure()
        {
            var definitions = FixtureDescriptors();
            var graph = new AssemblyReferenceGraph(definitions);
            CollectionAssert.AreEquivalent(new[] { Internal }, graph.ReverseClosure(new[] { Internal }));
            CollectionAssert.AreEquivalent(new[] { Extensibility, Internal, "AssemblyShadowDemo.ExtensibilityConsumer" }, graph.ReverseClosure(new[] { Extensibility }));
            CollectionAssert.AreEquivalent(AssemblyShadowDemo.Editor.M02Build.Candidates, graph.ReverseClosure(new[] { Contracts }));
            Assert.AreEqual(Contracts, graph.LoadOrder(AssemblyShadowDemo.Editor.M02Build.Candidates)[0]);

            var frozenEdges = new AssemblyReferenceGraph(definitions, requiredBaselineEdges: graph.Edges);
            CollectionAssert.AreEquivalent(AssemblyShadowDemo.Editor.M02Build.Candidates, frozenEdges.ReverseClosure(new[] { Contracts }));
        }

        [Test]
        public void ModuleContractUsesAssemblyReferenceWithoutDuplicateDeclaration()
        {
            var definition = JsonUtility.FromJson<Definition>(File.ReadAllText(DefinitionPath));
            CollectionAssert.Contains(definition.references, Contracts);
            Assert.IsTrue(FixtureDescriptors().Single(item => item.name == Extensibility).references.Contains(Contracts),
                "The compiled Extensibility witness must retain its real Contracts AssemblyRef.");
            var configuration = JsonUtility.FromJson<ShadowDependencyConfiguration>(File.ReadAllText("ProjectSettings/AssemblyShadowDependencies.json"));
            Assert.IsFalse(configuration.runtimeDependencies.Any(edge => edge.consumer == Extensibility && edge.provider == Contracts),
                "A real AssemblyRef and an explicit runtime dependency would describe the same edge twice.");
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
