"""Factory capture receipt negatives. Synthetic data, never a Unity PASS."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'R03'))
from batch_contract import ContractError
from bee_observation import verify_observation


class FactoryReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = 'a' * 64
        self.raw = {
            'schemaVersion': 1, 'kind': 'R03BeeResultObservationV1',
            'runtimeAcceptance': False, 'sourceManifestSha256': self.manifest,
            'result': 'CapturedForAnalysis', 'sameProcessor': True,
            'driverInitiallyAbsent': True, 'limitsExceeded': False,
            'acquisition': 'ScopedOriginalFactoryForwarderV1',
            'factoryRestored': True, 'factoryCalls': 2,
            'capturedProcessors': 1, 'selectedFactorySequence': 2,
            'moduleType': 'Original.Module', 'processorType': 'Original.Bee',
            'moduleAssemblySha256': 'b' * 64, 'processorAssemblySha256': 'c' * 64,
            'buildErrors': 2, 'error': None,
            'nodes': [{'exitCode': 0, 'outputFile': 'test.o', 'output': 'error: diagnostic'}],
            'messages': [{'text': 'test.o: diagnostic'}],
        }

    def check(self, raw=None):
        return verify_observation(self.raw if raw is None else raw, self.manifest)

    def test_complete_capture_is_not_build_acceptance(self):
        before = copy.deepcopy(self.raw)
        result = self.check()
        self.assertFalse(result['buildAcceptanceChanged'])
        self.assertFalse(result['runtimeAcceptance'])
        self.assertEqual(result['buildErrors'], 2)
        self.assertTrue(result['sharedCacheLogs'][0]['matchesNodeOutput'])
        self.assertEqual(self.raw, before)

    def test_missing_instance_type_identities_rejected(self):
        for key in ('moduleType', 'processorType'):
            for value in (None, '', ' ', ' padded', 1):
                with self.subTest(key=key, value=value):
                    raw = copy.deepcopy(self.raw); raw[key] = value
                    with self.assertRaises(ContractError): self.check(raw)

    def test_missing_or_malformed_assembly_hash_rejected(self):
        for key in ('moduleAssemblySha256', 'processorAssemblySha256'):
            for value in (None, '', 'a' * 63, 'G' * 64, True):
                with self.subTest(key=key, value=value):
                    raw = copy.deepcopy(self.raw); raw[key] = value
                    with self.assertRaises(ContractError): self.check(raw)

    def test_absent_captured_count_rejected(self):
        del self.raw['capturedProcessors']
        with self.assertRaises(ContractError): self.check()

    def test_impossible_captured_count_rejected(self):
        for value in (True, 0, -1, 3, '1'):
            with self.subTest(value=value):
                self.raw['capturedProcessors'] = value
                with self.assertRaises(ContractError): self.check()

    def test_factory_call_counts_remain_exact(self):
        for value in (True, 0, 65, '2'):
            with self.subTest(value=value):
                self.raw['factoryCalls'] = value
                with self.assertRaises(ContractError): self.check()

    def test_selected_sequence_must_be_a_real_call(self):
        for value in (True, 0, 3, '2'):
            with self.subTest(value=value):
                self.raw['selectedFactorySequence'] = value
                with self.assertRaises(ContractError): self.check()

    def test_unrestored_factory_and_different_owner_rejected(self):
        for key in ('factoryRestored', 'sameProcessor', 'driverInitiallyAbsent'):
            raw = copy.deepcopy(self.raw); raw[key] = False
            with self.subTest(key=key), self.assertRaises(ContractError): self.check(raw)

    def test_acquisition_error_cannot_be_marked_captured(self):
        self.raw['error'] = 'FactoryCapture:System.InvalidOperationException'
        with self.assertRaises(ContractError): self.check()

    def test_manifest_must_be_exact_full_hash(self):
        for expected in ('a', None, True, 'A' * 64):
            with self.subTest(expected=expected), self.assertRaises(ContractError):
                verify_observation(self.raw, expected)
        self.raw['sourceManifestSha256'] = 'd' * 64
        with self.assertRaises(ContractError): self.check()

    def test_boolean_schema_version_rejected(self):
        self.raw['schemaVersion'] = True
        with self.assertRaises(ContractError): self.check()

    def test_unavailable_truncated_or_authorizing_capture_rejected(self):
        for key, value in (('result', 'Unavailable'), ('limitsExceeded', True),
                           ('runtimeAcceptance', True)):
            raw = copy.deepcopy(self.raw); raw[key] = value
            with self.subTest(key=key), self.assertRaises(ContractError): self.check(raw)


if __name__ == '__main__':
    unittest.main()
