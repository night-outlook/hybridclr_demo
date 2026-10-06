using System;
using NUnit.Framework;
using UnityEngine;

namespace AssemblyShadowDemo.EditorTests
{
    // Portable C# logic/DTO checks. They are not Player or compiler provenance.
    public sealed class H1EvidenceProcessTests
    {
        [TestCase("", "\"\"")]
        [TestCase("/tmp/build path/test.py", "\"/tmp/build path/test.py\"")]
        [TestCase("a\"b", "\"a\\\"b\"")]
        [TestCase("a\\b", "\"a\\\\b\"")]
        public void ExplicitArgumentsAreQuoted(string input, string expected)
        { Assert.That(global::AssemblyShadowDemo.Editor.H1EvidenceProcess.Quote(input), Is.EqualTo(expected)); }

        [TestCase(null)]
        [TestCase("a\nb")]
        [TestCase("a\rb")]
        [TestCase("a\0b")]
        public void InvalidArgumentsAreRejected(string input)
        { Assert.Throws<ArgumentException>(() => global::AssemblyShadowDemo.Editor.H1EvidenceProcess.Quote(input)); }

        [Test]
        public void CompilerCaptureRetainsResponseAndMacroFields()
        {
            var value = new global::AssemblyShadowDemo.Editor.H1CompilerProvenance.Capture {
                schemaVersion = 1, buildId = "H1Count-On-Debug", buildGuid = "test-only",
                il2cppDebug = "1", ndebug = "0", il2cppDevelopment = "0",
                responseFiles = new[] { new global::AssemblyShadowDemo.Editor.H1CompilerProvenance.ResponseFile {
                    sourcePath = "/source/compile.rsp", retainedPath = "/retained/compile.rsp",
                    sha256 = new string('a', 64), bytes = 123 } }
            };
            string json = JsonUtility.ToJson(value);
            var copy = JsonUtility.FromJson<global::AssemblyShadowDemo.Editor.H1CompilerProvenance.Capture>(json);
            Assert.That(copy.ndebug, Is.EqualTo("0"));
            Assert.That(copy.responseFiles.Length, Is.EqualTo(1));
            Assert.That(copy.responseFiles[0].bytes, Is.EqualTo(123));
            Assert.That(copy.responseFiles[0].retainedPath, Is.EqualTo("/retained/compile.rsp"));
        }

        [Test]
        public void EmptyCaptureDoesNotCreateProvenance()
        {
            var value = JsonUtility.FromJson<global::AssemblyShadowDemo.Editor.H1CompilerProvenance.Capture>("{}");
            Assert.That(value.schemaVersion, Is.EqualTo(0));
            Assert.That(value.buildGuid, Is.Null.Or.Empty);
            Assert.That(value.responseFiles, Is.Null);
        }
    }
}
