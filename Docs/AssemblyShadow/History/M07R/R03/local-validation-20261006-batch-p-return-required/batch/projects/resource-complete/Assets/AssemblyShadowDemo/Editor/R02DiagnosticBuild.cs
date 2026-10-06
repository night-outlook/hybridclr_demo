using System;
using System.IO;
using HybridCLR.Editor.AssemblyShadow;
using UnityEngine;

namespace AssemblyShadowDemo.Editor
{
    /// <summary>Bind the diagnostic builder to the new R02 graph, not restored H1 settings.</summary>
    public static class R02DiagnosticBuild
    {
        [Serializable] private sealed class Fixture { public int schemaVersion; public string milestone, baselineBuildId, runtimeAbiHash; }
        public static void Build()
        {
            string[] args = Environment.GetCommandLineArgs();
            int index = Array.IndexOf(args, "-shadowM07Fixtures");
            if (index < 0 || index + 1 >= args.Length || !Path.IsPathRooted(args[index + 1]))
                throw new ArgumentException("An absolute new M07 fixture manifest is required.");
            byte[] original = File.ReadAllBytes(args[index + 1]);
            var fixture = JsonUtility.FromJson<Fixture>(System.Text.Encoding.UTF8.GetString(original));
            if (fixture == null || fixture.schemaVersion != 1 || fixture.milestone != "M07" ||
                string.IsNullOrWhiteSpace(fixture.baselineBuildId) || !fixture.baselineBuildId.StartsWith("M07-Baseline-R02-", StringComparison.Ordinal))
                throw new InvalidOperationException("Only the current R02 controlled graph may select a diagnostic baseline.");
            var settings = AssemblyShadowSettings.Instance;
            var pins = ShadowSourcePins.Read(settings.sourcePinFile, UnityEditor.EditorUserBuildSettings.activeBuildTarget, settings.architecture);
            if (pins.RuntimeAbiHash() != fixture.runtimeAbiHash)
                throw new InvalidOperationException("Diagnostic graph and current runtime pins differ.");
            string before = settings.buildId;
            try
            {
                settings.buildId = fixture.baselineBuildId;
                R01BDiagnosticBuild.BuildDiagnosticPlayer();
            }
            finally { settings.buildId = before; }
            if (Convert.ToBase64String(File.ReadAllBytes(args[index + 1])) != Convert.ToBase64String(original))
                throw new InvalidOperationException("Diagnostic fixture changed during build.");
        }
    }
}
