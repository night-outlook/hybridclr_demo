using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class H1CompilerProvenanceTests
    {
        [Test]
        public void RetainedBeeGraphShapeContainsNativeCompilerAndLinkActions()
        {
            string root = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string[] graphs = Directory.Exists(Path.Combine(root, "Library", "Bee"))
                ? Directory.GetFiles(Path.Combine(root, "Library", "Bee"), "Player*.dag.json", SearchOption.TopDirectoryOnly)
                : new string[0];
            Assume.That(graphs.Length, Is.GreaterThan(0), "A Unity Player Bee graph is required for this evidence-shape test.");
            string json = File.ReadAllText(graphs.OrderBy(path => path, System.StringComparer.Ordinal).Last());
            Assert.That(json, Does.Contain("\"Action\""));
            Assert.That(json, Does.Contain("C_Mac_arm64"));
            Assert.That(json, Does.Contain("Link_Mac_arm64"));
            Assert.That(json, Does.Contain("clang++"));
            Assert.That(json, Does.Contain("-isysroot"));
        }
    }
}
