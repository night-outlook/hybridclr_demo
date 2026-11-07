#!/usr/bin/env python3
"""R03 initializer-specific bridge source boundary contracts, not Unity tests."""
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
DEMO = HERE.parents[2]
BRIDGE = HERE / "PlayerProject/R03InitializerBridge.cs"
BUILDER = DEMO / "Tools/AssemblyShadow/R03/PlayerProject/R03Build.cs"
MANAGED = HERE / "PlayerProject/R03InitializerObservationPlayer.cs"
NATIVE = HERE / "PlayerProject/R03InitializerPreparedProbe.cpp"
PREPARE = HERE / "prepare_initializer_sources.py"
RUNNER = HERE / "run_initializer_local.py"


class InitializerBridgeScopeTests(unittest.TestCase):
    def test_01_actual_new_editor_bridge_is_isolated_after_default_generation(self):
        builder = BUILDER.read_text()
        self.assertIn("PrebuildCommand.GenerateAll();", builder)
        self.assertIn("GenerateInitializerBridgeIfRequested(config, native)", builder)
        self.assertLess(builder.index("PrebuildCommand.GenerateAll();"),
                        builder.index("GenerateInitializerBridgeIfRequested(config, native)"))
        self.assertIn('settings.hotUpdateAssemblies = Array.Empty<string>();', builder)
        self.assertIn('settings.hotUpdateAssemblyDefinitions = Array.Empty<UnityEditorInternal.AssemblyDefinitionAsset>();', builder)
        self.assertIn('if (string.IsNullOrEmpty(config.initializerBridgeContract))', builder)
        self.assertIn('AssemblyShadow.R03.Editor.R03InitializerBridge', builder)
        self.assertIn('initializerBridgePostBuildSha256', builder)
        self.assertNotIn('settings.hotUpdateAssemblies = new[]', builder)

    def test_02_real_methods_dll_metadata_controls_bridge(self):
        code = BRIDGE.read_text()
        for required in (
            'ModuleDefMD.Load(File.ReadAllBytes(path))',
            'ShadowHash.File(path) == sha',
            'module.Mvid.ToString()',
            'callback.ImplMap.Module.Name.String == ImportModule',
            'callback.ImplMap.Name.String == NativeEntry',
            'callback.MethodSig.Params.Count == 0',
            'callback.MethodSig.RetType.ElementType == ElementType.I4',
            'PInvokeAttributes.CallConvCdecl',
            'PInvokeAttributes.NoMangle',
            'ImportModule = "__InternalDynamic"',
            'NativeSignature = "Bi4"',
            'Exactly one null-only generated native bridge table',
        ):
            with self.subTest(marker=required):
                self.assertIn(required, code)

    def test_03_narrow_generated_table_and_real_linked_probe(self):
        source = BRIDGE.read_text()
        native = NATIVE.read_text()
        managed = MANAGED.read_text()
        runner = RUNNER.read_text()
        self.assertIn('typedef int32_t (CDECL *NativeMethod)();', source)
        self.assertIn('"    *(int32_t*)ret = ((NativeMethod)(methodPointer))();', source)
        self.assertIn('g_managed2NativeFunctionPointerCallStub', source)
        self.assertIn('R03_IRW_BridgeStatus()', native)
        self.assertIn('entries[i].methodPointer == nullptr', native)
        self.assertIn('std::strcmp(entries[i].methodSig, "Bi4")', native)
        self.assertIn('R03_IRW_BridgeStatus()', managed)
        self.assertIn('R03_IRW_Trace(103, linkedBi4, 0, 0, 0);', managed)
        self.assertIn('Need(linkedBi4 == 1, "Genuine linked Bi4 bridge table entry")', managed)
        self.assertIn('R03InitializerLinkedBi4StaticEvidenceV1', runner)
        self.assertIn('receipt.get("initializerBridgeGeneratedSha256")', runner)
        self.assertIn('exports.stdout.count("_R03_IRW_BridgeStatus")', runner)
        self.assertIn('R03InitializerBridge.cs', PREPARE.read_text())

    def test_04_no_global_resolver_vm_or_legacy_runner_edits_in_bridge_scope(self):
        source = BRIDGE.read_text()
        self.assertNotIn('ConfigureCandidates', source)
        self.assertNotIn('StageAssembly', source)
        code_lines = [line for line in source.splitlines()
                      if not line.lstrip().startswith("//")]
        self.assertFalse(any("PrebuildCommand.GenerateAll(" in line
                             for line in code_lines))
        self.assertNotIn('hotUpdateAssemblies =', source)
        self.assertNotIn('GetManaged2NativeFunctionPointerMethodPointer', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
