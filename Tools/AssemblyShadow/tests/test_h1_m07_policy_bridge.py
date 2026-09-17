import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
CALL = 'AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness'
SOURCE = 'image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4'
IMAGE = '9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27'
CODEGEN_ASMDEF = 'Unity.HybridCLR.AssemblyShadow.CodeGen'

class M07FixedBootstrapPolicyTests(unittest.TestCase):
    def test_dependency_bridge_is_exact_and_binding_owned(self):
        deps = json.loads((ROOT / 'ProjectSettings/AssemblyShadowDependencies.json').read_text())
        bindings = json.loads((ROOT / 'ProjectSettings/AssemblyShadowReflectionBindings.json').read_text())
        site = next(x for x in bindings['sites'] if x['id'] == 'h1-count-ordinary-witness-image')
        self.assertEqual('FixedAssemblyBytes', site['kind'])
        self.assertEqual(IMAGE, site['imageSha256'])
        self.assertEqual('fde200bf65fac1e9287bf38eebd22cef98ea72b0f348c1a93350d2ffc945cb5e', site['originalMethodHash'])
        self.assertEqual(25, site['operationIndex'])
        self.assertEqual([{'originalMethodHash':'4dba51434365b37d22bb2261e1cbea7530fb73a200954039296663c4c94b225e','operationIndex':25}], site['additionalMethodVariants'])
        self.assertEqual('AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null', site['providerAssemblyIdentity'])
        rows = [x for x in deps['bootstrapEntrypoints'] if (x.get('callSite') or x.get('method')) == CALL]
        self.assertEqual(2, len(rows))
        self.assertEqual({SOURCE, IMAGE}, {x.get('target') for x in rows})
        for row in rows:
            self.assertEqual('AssemblyShadowDemo.Bootstrap', row['consumer'])
            self.assertEqual('AssemblyShadowBaseline.HotUpdate', row['provider'])
            self.assertIn('h1-count-ordinary-witness-image', row['reason'])
            self.assertTrue(row['target'])

    def test_editor_test_asmdef_directly_references_codegen(self):
        asmdef = json.loads((ROOT / 'Assets/AssemblyShadowDemo/Tests/Editor/AssemblyShadowDemo.EditorTests.asmdef').read_text())
        references = asmdef['references']
        self.assertEqual(1, references.count(CODEGEN_ASMDEF))
        self.assertIn('HybridCLR.Editor', references)
        self.assertEqual(['Editor'], asmdef['includePlatforms'])
        self.assertFalse(asmdef['autoReferenced'])
        self.assertIn('UNITY_INCLUDE_TESTS', asmdef['defineConstraints'])

    def test_workflow_failure_wrapper_restores_real_scene_and_settings_inputs(self):
        wrapper = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1').read_text()
        core_path = ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.Core.ps1'
        self.assertTrue(core_path.is_file())
        core = core_path.read_text()
        self.assertIn("AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs", core)
        self.assertIn("AssemblyShadowDemo.Editor.M07Build.BuildBaselineResources", core)
        self.assertNotEqual('PLACEHOLDER', core.strip())
        for value in (
            'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity',
            'ProjectSettings/AssemblyShadowSettings.asset',
            'ProjectSettings/EditorBuildSettings.asset',
            'Save-M07WorkflowInputs',
            'Restore-M07WorkflowInputs',
            'workflow-inputs-restored.json'):
            self.assertIn(value, wrapper)
        self.assertIn("Invoke-M07Build.Core.ps1", wrapper)
        self.assertIn("if ($workflowFailure)", wrapper)
        self.assertIn("throw $workflowFailure", wrapper)
        self.assertNotIn('ProjectSettings/AssemblyShadow/AssemblyShadowSettings.asset', wrapper)

    def test_controlled_failure_occurs_only_after_real_validate_compiler_inputs(self):
        wrapper = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1').read_text()
        self.assertIn('[switch]$ControlledFailureAfterValidateCompilerInputs', wrapper)
        self.assertIn("method = 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs'", wrapper)
        self.assertIn('Assert-M07ControlledPinnedInputs -Project $shadowProject', wrapper)
        validate = wrapper.index('Invoke-M07ControlledValidateCompilerInputs -Project $shadowProject')
        controlled = wrapper.index("throw 'Controlled M07 failure after successful ValidateCompilerInputs")
        core = wrapper.index('& $core @invoke')
        self.assertLess(validate, controlled)
        self.assertLess(controlled, core)
        self.assertIn('Restore-M07WorkflowInputs -Project $shadowProject', wrapper[controlled:])

if __name__ == '__main__':
    unittest.main()
