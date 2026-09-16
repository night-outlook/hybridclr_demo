import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
DEPENDENCIES = ROOT / 'ProjectSettings/AssemblyShadowDependencies.json'
BINDINGS = ROOT / 'ProjectSettings/AssemblyShadowReflectionBindings.json'
WORKFLOW = ROOT / 'Tools/AssemblyShadow/Invoke-M07Build.ps1'

CONSUMER = 'AssemblyShadowDemo.Bootstrap'
PROVIDER = 'AssemblyShadowBaseline.HotUpdate'
TYPE = 'AssemblyShadowBaseline.HotUpdate.Entry'
CALL_SITE = 'AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness'
METHOD_SIGNATURE = ('AssemblyShadowDemo.H1CountEarlyStartup/WitnessReceipt '
                    'AssemblyShadowDemo.H1CountEarlyStartup::LoadOrdinaryWitness()')
IMAGE_SHA = '9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27'
IMAGE_PATH = 'Assets/StreamingAssets/AssemblyShadow/M00/AssemblyShadowBaseline.HotUpdate.dll.bytes'
PROVIDER_IDENTITY = 'AssemblyShadowBaseline.HotUpdate, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def h1_binding(config):
    rows = [r for r in config['sites'] if r.get('id') == 'h1-count-ordinary-witness-image']
    if len(rows) != 1:
        raise AssertionError('Expected exactly one H1 fixed-byte binding')
    return rows[0]


def h1_bootstrap(config):
    rows = [r for r in config['bootstrapEntrypoints'] if r.get('method') == CALL_SITE]
    if len(rows) != 1:
        raise AssertionError('Expected exactly one H1 bootstrap declaration')
    return rows[0]


def approved(entry, reference, resolved_provider=None, resolved_type=None):
    # Mirrors BootstrapIsolationRule.IsApprovedReflection's exact value contract.
    call_site, sep, argument = reference.partition('|')
    if not sep or not call_site or not argument:
        return False
    if entry.get('consumer', '').lower() != CONSUMER.lower():
        return False
    if not entry.get('provider') or not entry.get('typeName') or not entry.get('method') or not entry.get('reason'):
        return False
    if entry['method'] != call_site:
        return False
    if resolved_provider and entry['provider'].lower() != resolved_provider.lower():
        return False
    if resolved_type and entry['typeName'] != resolved_type:
        return False
    target = entry.get('target')
    if target:
        return argument == target
    return argument in (entry['provider'], entry['typeName'], entry['typeName'] + ', ' + entry['provider'])


class H1M07FixedBytePolicyTests(unittest.TestCase):
    def test_fixed_byte_binding_and_bootstrap_contract_are_exactly_coupled(self):
        binding = h1_binding(load(BINDINGS))
        entry = h1_bootstrap(load(DEPENDENCIES))
        self.assertEqual('FixedAssemblyBytes', binding['kind'])
        self.assertEqual(CONSUMER, binding['assembly'])
        self.assertEqual('AssemblyShadowDemo.H1CountEarlyStartup', binding['typeName'])
        self.assertEqual(METHOD_SIGNATURE, binding['methodSignature'])
        self.assertRegex(binding['originalMethodHash'], r'^[0-9a-f]{64}$')
        self.assertIsInstance(binding['operationIndex'], int)
        self.assertGreaterEqual(binding['operationIndex'], 0)
        self.assertEqual(IMAGE_SHA, binding['imageSha256'])
        self.assertEqual(IMAGE_PATH, binding['imagePath'])
        self.assertEqual(PROVIDER_IDENTITY, binding['providerAssemblyIdentity'])
        self.assertTrue(binding['providerSemanticVariants'])

        self.assertEqual(CONSUMER, entry['consumer'])
        self.assertEqual(PROVIDER, entry['provider'])
        self.assertEqual(TYPE, entry['typeName'])
        self.assertEqual(CALL_SITE, entry['method'])
        self.assertEqual(binding['imageSha256'], entry['target'])
        self.assertTrue(entry['reason'])
        self.assertTrue(approved(entry, CALL_SITE + '|' + IMAGE_SHA))

    def test_bootstrap_contract_rejects_method_provider_and_image_drift(self):
        entry = h1_bootstrap(load(DEPENDENCIES))
        mutations = []
        wrong_method = copy.deepcopy(entry); wrong_method['method'] += 'Changed'; mutations.append(wrong_method)
        wrong_provider = copy.deepcopy(entry); wrong_provider['provider'] = 'Other.Provider'; mutations.append(wrong_provider)
        wrong_target = copy.deepcopy(entry); wrong_target['target'] = '0' * 64; mutations.append(wrong_target)
        for row in mutations:
            self.assertFalse(approved(row, CALL_SITE + '|' + IMAGE_SHA,
                                      resolved_provider=PROVIDER if row is wrong_provider else None))
        self.assertFalse(approved(entry, CALL_SITE + '|' + ('f' * 64)))
        self.assertFalse(approved(entry, 'AssemblyShadowDemo.Other::Load|' + IMAGE_SHA))

    def test_binding_contract_keeps_method_operation_provider_and_image_fail_closed(self):
        binding = h1_binding(load(BINDINGS))
        required = ('originalMethodHash', 'operationIndex', 'imageSha256', 'providerAssemblyIdentity',
                    'providerSemanticVariants', 'imagePath')
        for key in required:
            self.assertIn(key, binding)
            self.assertNotIn(binding[key], (None, '', []))
        self.assertEqual(IMAGE_SHA, binding['imageSha256'])
        self.assertEqual(PROVIDER_IDENTITY, binding['providerAssemblyIdentity'])

    def test_m07_workflow_has_outer_failure_restoration_for_scene_and_settings(self):
        text = WORKFLOW.read_text(encoding='utf-8-sig')
        self.assertIn('Save-M07WorkflowInputs', text)
        self.assertIn('Restore-M07WorkflowInputs', text)
        self.assertIn('Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity', text)
        self.assertIn('ProjectSettings/AssemblyShadowSettings.asset', text)
        dispose = text.rfind('$workflowLock.Dispose()')
        restore = text.rfind('Restore-M07WorkflowInputs')
        self.assertGreater(dispose, 0)
        self.assertGreater(restore, 0)
        self.assertLess(restore, dispose)
        self.assertIn('finally', text[restore - 500:dispose + 50])


if __name__ == '__main__':
    unittest.main()
