using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using HybridCLR.Editor;
using HybridCLR.Editor.Installer;
using HybridCLR.Editor.Settings;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace AssemblyShadowBaseline.Editor
{
    /// <summary>Editor/tooling checks only. Player results remain the runtime authority.</summary>
    public static class BaselineValidation
    {
        public static void Run()
        {
            var cases = new List<TestCase>();
            Check(cases, "process_large_stdout_is_drained", () =>
            {
                var pins = JsonUtility.FromJson<Pins>(File.ReadAllText("ProjectSettings/AssemblyShadowSourcePins.json"));
                var repo = Path.GetFullPath(Path.Combine(SettingsUtil.ProjectDir, pins.il2cppPlus.localPath));
                var result = BashUtil.RunCommand2(repo, "git", new[] { "ls-tree", "-r", "-z", "HEAD", "--", "libil2cpp" }, false);
                Require(result.ExitCode == 0, result.StdErr);
                Require(result.StdOut.Length > 65536, "Fixture must exceed an OS pipe buffer.");
                var receipt = JsonUtility.FromJson<Receipt>(File.ReadAllText(Path.Combine(SettingsUtil.LocalIl2CppDir,
                    "libil2cpp/assembly-shadow-install.json")));
                Require(result.StdOut.Count(character => character == '\0') ==
                    receipt.sourceFileHashes.Count(file => file.source == "il2cppPlus"), "Git output was truncated.");
            });
            Check(cases, "process_argument_quotes_and_backslashes_round_trip", () =>
            {
                string value = "spaces \"quotes\" backslash\\ and trailing\\";
                var result = BashUtil.RunCommand2(SettingsUtil.ProjectDir, "git",
                    new[] { "-c", "assemblyshadow.test=" + value, "config", "--get", "assemblyshadow.test" }, false);
                Require(result.ExitCode == 0, result.StdErr);
                Require(result.StdOut.TrimEnd('\r', '\n') == value, "Process arguments changed in transit.");
            });
            Check(cases, "native_feature_modes_are_independent_of_managed_defines", () =>
            {
                string original = PlayerSettings.GetAdditionalIl2CppArgs();
                try
                {
                    BaselineBuild.SetNativeFeature(true);
                    Require(PlayerSettings.GetAdditionalIl2CppArgs().Contains("-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=1"), "ON missing.");
                    BaselineBuild.SetNativeFeature(false);
                    Require(PlayerSettings.GetAdditionalIl2CppArgs().Contains("-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=0"), "OFF missing.");
                }
                finally { PlayerSettings.SetAdditionalIl2CppArgs(original); }
            });
            Check(cases, "editor_baseline_monoscript_and_prefab_metadata", () =>
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(
                    "Assets/AssemblyShadowBaseline/Resources/AssemblyShadowBaseline/BaselinePrefab.prefab");
                Require(prefab != null, "Prefab missing.");
                var component = prefab.GetComponent<BaselineProbe>();
                Require(component != null && component.number == 1234, "Serialized component mismatch.");
                Require(MonoScript.FromMonoBehaviour(component).GetClass() == typeof(BaselineProbe), "MonoScript baseline mismatch.");
            });
            Check(cases, "ordinary_hotupdate_is_not_an_aot_reference", () =>
            {
                Require(HybridCLRSettings.Instance.hotUpdateAssemblies.SequenceEqual(new[] { "AssemblyShadowBaseline.HotUpdate" }),
                    "Unexpected ordinary hot-update list.");
                var definition = JsonUtility.FromJson<Definition>(File.ReadAllText(
                    "Assets/AssemblyShadowBaseline/Aot/AssemblyShadowBaseline.Aot.asmdef"));
                Require(!definition.references.Contains("AssemblyShadowBaseline.HotUpdate"), "AOT bootstrap references hot-update assembly.");
            });

            Directory.CreateDirectory("_temp/AssemblyShadow");
            var evidence = new Evidence { passed = cases.All(test => test.passed), tests = cases.ToArray() };
            File.WriteAllText("_temp/AssemblyShadow/m00-editor-tests.json", JsonUtility.ToJson(evidence, true));
            Debug.Log("[AssemblyShadow M00] Editor checks: " + JsonUtility.ToJson(evidence));
            if (!evidence.passed) throw new BuildFailedException("M00 Editor/tooling validation failed.");
        }

        private static void Check(List<TestCase> cases, string name, Action action)
        {
            var test = new TestCase { name = name };
            try { action(); test.passed = true; }
            catch (Exception exception) { test.error = exception.ToString(); }
            cases.Add(test);
        }

        private static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        [Serializable] private sealed class TestCase { public string name; public bool passed; public string error; }
        [Serializable] private sealed class Evidence { public bool runtimeEvidence = false; public bool passed; public TestCase[] tests; }
        [Serializable] private sealed class Pins { public Pin il2cppPlus; }
        [Serializable] private sealed class Pin { public string localPath; }
        [Serializable] private sealed class Receipt { public FileHash[] sourceFileHashes; }
        [Serializable] private sealed class FileHash { public string source; }
        [Serializable] private sealed class Definition { public string[] references; }
    }
}
