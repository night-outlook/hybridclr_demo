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

    def test_controlled_failure_occurs_only_after_real_validate_and_split_authority(self):
        wrapper = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1').read_text()
        self.assertIn('[switch]$ControlledFailureAfterValidateCompilerInputs', wrapper)
        self.assertIn("method = 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs'", wrapper)
        self.assertIn('H1_M07_WORKFLOW_AUTHORITY_ROOT', wrapper)
        self.assertIn('H1_M07_WORKFLOW_BASELINE_ID', wrapper)
        env = wrapper.index('$env:H1_M07_WORKFLOW_AUTHORITY_ROOT = $recoveryRoot')
        validate = wrapper.index('Invoke-M07ControlledValidateCompilerInputs -Project $shadowProject')
        post = wrapper.index('Assert-M07ControlledPinnedInputs -Project $shadowProject', validate)
        controlled = wrapper.index("throw 'Controlled M07 failure after successful ValidateCompilerInputs")
        core = wrapper.index('& $core @invoke')
        self.assertLess(env, validate)
        self.assertLess(validate, post)
        self.assertLess(post, controlled)
        self.assertLess(controlled, core)
        self.assertIn('Restore-M07WorkflowInputs -Project $shadowProject', wrapper[controlled:])

    def test_normal_core_proceeds_under_scoped_m07_authority_without_removing_rechecks(self):
        wrapper = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1').read_text()
        core = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.Core.ps1').read_text()
        env = wrapper.index('$env:H1_M07_WORKFLOW_AUTHORITY_ROOT = $recoveryRoot')
        invoke = wrapper.index('& $core @invoke')
        restore_env = wrapper.index('Remove-Item Env:H1_M07_WORKFLOW_AUTHORITY_ROOT')
        self.assertLess(env, invoke)
        self.assertLess(invoke, restore_env)
        validate = core.index("Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs'")
        resources = core.index("Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildBaselineResources'")
        player_on = core.index("Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildPlayerBaseline'")
        player_off = core.index("Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.BuildFeatureDisabledPlayer'")
        self.assertLess(validate, resources)
        self.assertLess(resources, player_on)
        self.assertLess(player_on, player_off)
        self.assertGreaterEqual(core[validate:player_off].count('Assert-M07PinnedInputs $shadowProject'), 3)
        verifier = (ROOT / 'Tools/AssemblyShadow/verify-installed-runtime.py').read_text()
        self.assertIn('verify_m07_workflow', verifier)
        self.assertIn('--skip-demo-source', verifier)
        self.assertIn('if not required_changed', verifier)

if __name__ == '__main__':
    unittest.main()
