using System;
using System.IO;
using System.Reflection;
using System.Text;
using NUnit.Framework;

namespace AssemblyShadowDemo.EditorTests
{
    public sealed class M02StructuralPatchCompilationTests
    {
        [TestCase("", "ASSEMBLY_SHADOW_P05")]
        [TestCase("USER_FIRST;USER_SECOND", "USER_FIRST;USER_SECOND;ASSEMBLY_SHADOW_P05")]
        public void StagingPreservesOriginalDefineOrder(string original, string expected)
        { Assert.AreEqual(expected, Invoke("StagedDefines", original)); }

        [TestCase("ASSEMBLY_SHADOW_P01")]
        [TestCase("USER;ASSEMBLY_SHADOW_P05")]
        [TestCase("ASSEMBLY_SHADOW_P99")]
        public void PreexistingPatchSymbolsRequireExplicitUserResolution(string original)
        { Assert.That(() => Invoke("StagedDefines", original), Throws.Exception.With.Message.Contains("StructuralPatchDefinePresent")); }

        [TestCase("USER;USER")]
        [TestCase("USER; OTHER")]
        [TestCase("USER;")]
        public void StagingNeverSilentlyNormalizesUserDefines(string original)
        { Assert.That(() => Invoke("StagedDefines", original), Throws.Exception.With.Message.Contains("StructuralDefinesInvalid")); }

        [Test] public void RecoveryHandlesFailureBeforeAndAfterSettingsMutation()
        {
            Assert.AreEqual(false, Invoke("RestorationRequired", "USER", "USER", "USER;ASSEMBLY_SHADOW_P05"));
            Assert.AreEqual(true, Invoke("RestorationRequired", "USER;ASSEMBLY_SHADOW_P05", "USER", "USER;ASSEMBLY_SHADOW_P05"));
            Assert.That(() => Invoke("RestorationRequired", "USER;CONCURRENT", "USER", "USER;ASSEMBLY_SHADOW_P05"),
                Throws.Exception.With.Message.Contains("StructuralDefineConflict"));
            Assert.That(() => Invoke("RestorationRequired", "USER;ASSEMBLY_SHADOW_P05;CONCURRENT", "USER", "USER;ASSEMBLY_SHADOW_P05"),
                Throws.Exception.With.Message.Contains("StructuralDefineConflict"));
            Assert.That(() => Invoke("RestorationRequired", "USER", "USER", "WRONG"), Throws.Exception.With.Message.Contains("StructuralStateInvalid"));
        }

        [Test] public void RunArgumentRequiresOneExistingImmediateGuidChild()
        {
            string project = Path.Combine(Path.GetTempPath(), "M02StructuralRunTests-" + Guid.NewGuid().ToString("N"));
            string run = Path.Combine(project, "_temp", "AssemblyShadow", "M02Validation-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(run);
            try
            {
                Assert.AreEqual(run, Invoke("ParseRunDirectory", new[] { "Unity", "-shadowValidationRoot", run }, project));
                foreach (var arguments in new[] {
                    new string[0], new[] { "-shadowValidationRoot" }, new[] { "-shadowValidationRoot", "relative" },
                    new[] { "-shadowValidationRoot", run, "-shadowValidationRoot", run },
                    new[] { "-shadowValidationRoot", project }, new[] { "-shadowValidationRoot", run + "-other" },
                }) Assert.That(() => Invoke("ParseRunDirectory", arguments, project), Throws.Exception.With.Message.Contains("StructuralRunArgument"));
            }
            finally { Directory.Delete(project, true); }
        }

        [TestCase("  scriptingDefineSymbols: {}\n", "  scriptingDefineSymbols:\n    Standalone: \n", "", "")]
        [TestCase("  scriptingDefineSymbols: {}\n", "  scriptingDefineSymbols:\n    Standalone: ASSEMBLY_SHADOW_P05\n", "", "ASSEMBLY_SHADOW_P05")]
        [TestCase("  scriptingDefineSymbols:\n    Android: MOBILE;USER\n", "  scriptingDefineSymbols:\n    Android: MOBILE;USER\n    Standalone: \n", "", "")]
        [TestCase("  scriptingDefineSymbols:\n    Standalone: USER_FIRST;USER_SECOND\n    Android: MOBILE\n", "  scriptingDefineSymbols:\n    Standalone: USER_FIRST;USER_SECOND;ASSEMBLY_SHADOW_P05\n    Android: MOBILE\n", "USER_FIRST;USER_SECOND", "USER_FIRST;USER_SECOND;ASSEMBLY_SHADOW_P05")]
        [TestCase("  scriptingDefineSymbols:\n    Standalone: USER\n", "  scriptingDefineSymbols:\n    Standalone: USER\n", "USER", "USER")]
        public void ByteRestoreAllowsOnlyRecordedTargetSerialization(string originalMap, string currentMap, string originalDefines, string currentDefines)
        {
            Invoke("RequireSettingsOnlyTargetChange", Settings(originalMap), Settings(currentMap), "Standalone", originalDefines, currentDefines);
        }

        [Test] public void ByteRestorePreservesBomAndWindowsNewlines()
        {
            byte[] original = Encoding.UTF8.GetBytes("\uFEFF" + Encoding.UTF8.GetString(Settings("  scriptingDefineSymbols: {}\n")).Replace("\n", "\r\n"));
            byte[] current = Encoding.UTF8.GetBytes("\uFEFF" + Encoding.UTF8.GetString(Settings("  scriptingDefineSymbols:\n    Standalone: \n")).Replace("\n", "\r\n"));
            Invoke("RequireSettingsOnlyTargetChange", original, current, "Standalone", "", "");
            Assert.That(() => Invoke("RequireSettingsOnlyTargetChange", original, Settings("  scriptingDefineSymbols:\n    Standalone: \n"), "Standalone", "", ""),
                Throws.Exception.With.Message.Contains("StructuralSettingsChanged"));
        }

        [Test] public void ByteRestoreRejectsConcurrentUnrelatedSettingsChanges()
        {
            byte[] original = Settings("  scriptingDefineSymbols: {}\n");
            byte[] changed = Encoding.UTF8.GetBytes(Encoding.UTF8.GetString(Settings("  scriptingDefineSymbols:\n    Standalone: \n")).Replace("productName: Keep", "productName: Concurrent"));
            Assert.That(() => Invoke("RequireSettingsOnlyTargetChange", original, changed, "Standalone", "", ""),
                Throws.Exception.With.Message.Contains("StructuralSettingsChanged"));
            Assert.That(() => Invoke("RequireSettingsOnlyTargetChange", Settings("  scriptingDefineSymbols:\n    Android: MOBILE\n"),
                Settings("  scriptingDefineSymbols:\n    Android: CHANGED\n    Standalone: \n"), "Standalone", "", ""),
                Throws.Exception.With.Message.Contains("StructuralSettingsChanged"));
        }

        [TestCase("  scriptingDefineSymbols:\n    Standalone: CONCURRENT\n", "StructuralSettingsDefines")]
        [TestCase("  scriptingDefineSymbols:\n    Standalone: \n    Standalone: \n", "StructuralSettingsShape")]
        [TestCase("  scriptingDefineSymbols: {}\n  scriptingDefineSymbols: {}\n", "StructuralSettingsShape")]
        [TestCase("  scriptingDefineSymbols:\n    Standalone:\n      - USER\n", "StructuralSettingsShape")]
        public void ByteRestoreRejectsUnexpectedDefineValueOrYamlShape(string map, string error)
        {
            Assert.That(() => Invoke("RequireSettingsOnlyTargetChange", Settings("  scriptingDefineSymbols: {}\n"), Settings(map), "Standalone", "", ""),
                Throws.Exception.With.Message.Contains(error));
        }

        [Test] public void ByteRestoreCannotDeleteOriginalNonemptyTargetEntry()
        {
            Assert.That(() => Invoke("RequireSettingsOnlyTargetChange", Settings("  scriptingDefineSymbols:\n    Standalone: USER\n"),
                Settings("  scriptingDefineSymbols: {}\n"), "Standalone", "USER", "USER"), Throws.Exception.With.Message.Contains("StructuralSettingsDefines"));
        }

        private static byte[] Settings(string map)
        { return Encoding.UTF8.GetBytes("%YAML 1.1\nPlayerSettings:\n  productName: Keep\n" + map + "  otherSetting: unchanged\n"); }

        private static object Invoke(string name, params object[] values)
        {
            var method = typeof(AssemblyShadowDemo.Editor.M02StructuralPatchCompilation).GetMethod(name, BindingFlags.NonPublic | BindingFlags.Static);
            Assert.IsNotNull(method);
            try { return method.Invoke(null, values); }
            catch (TargetInvocationException error) { throw error.InnerException; }
        }
    }
}
