import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
CALL = 'AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness'
SOURCE = 'image:d60cad840ff603dcfd5d0816196469ecce9576306e5bef2901427a13759d8de4'
IMAGE = '9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27'

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

    def test_workflow_restoration_covers_pre_p05_mutations(self):
        text = (ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1').read_text()
        for value in (
            'ProjectSettings/AssemblyShadow/AssemblyShadowSettings.asset',
            'ProjectSettings/EditorBuildSettings.asset',
            'workflow-settings-restored.json',
            'Save-M07WorkflowMutationState',
            'Restore-M07WorkflowMutationState'):
            self.assertIn(value, text)
        save = text.index('$workflowState = Save-M07WorkflowMutationState')
        first = text.index("Invoke-M07GuardedMethod 'AssemblyShadowDemo.Editor.M07Build.ValidateCompilerInputs'")
        self.assertLess(save, first)
        self.assertIn('catch { $workflowFailure = $_; throw }', text)
        self.assertIn('finally { $workflowLock.Dispose() }', text)

if __name__ == '__main__':
    unittest.main()
