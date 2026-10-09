"""Host-only strict IR-R03-02 Player receipt checks; not Player execution."""
import copy
import json
import unittest

from run_terminal_local import verify_ir
from batch_contract import ContractError


class TerminalReceiptContractTests(unittest.TestCase):
    def setUp(self):
        self.request = {'runId': 'a' * 32, 'caseId': 'IR-R03-02-release-baseline', 'stimulus': 'baseline-owner'}
        self.launch = {'pid': 12034}
        self.build_sha = 'b' * 64
        self.recovery = json.dumps({'published': True, 'stateCode': 9,
                                    'disposition': 'RestartRequired', 'terminalFailureCode': 21})
        self.raw = {'schemaVersion': 1, 'kind': 'R03IRPostPoisonEntryV1',
            'acceptance': False, 'result': 'Passed', 'error': None,
            'runId': self.request['runId'], 'caseId': self.request['caseId'],
            'stimulus': self.request['stimulus'], 'processId': self.launch['pid'],
            'unityVersion': '2022.3.62f2', 'platform': 'OSXPlayer',
            'initialState': 6, 'poisonedState': 9, 'finalState': 9,
            'prePositive': True, 'preActiveReflection': 42, 'preActiveDelegate': 42,
            'preCanaryCount': 1, 'finalCanaryCount': 1,
            'preShadowField': 2, 'finalShadowField': 2, 'shadowFieldReadable': True,
            'activeReflectionAttempted': True, 'activeReflectionSucceeded': False,
            'activeReflectionException': 'System.Reflection.TargetInvocationException',
            'activeDelegateAttempted': True, 'activeDelegateSucceeded': False,
            'activeDelegateException': 'System.InvalidOperationException',
            'aotReflectionAttempted': True, 'aotReflectionSucceeded': False,
            'aotReflectionException': 'System.Reflection.TargetInvocationException',
            'firstRecovery': self.recovery, 'finalRecovery': self.recovery,
            'recoveryStable': True, 'fixedDiagnosticsReadable': True,
            'nativeStimulusReturn': 1,
            'nativeGuardJson': json.dumps({'available':True, 'activeGuard':1,'baselineGuard':0,
                                           'caughtOldGuard':1,'stateCode':9})}

    def verify(self):
        return verify_ir(self.raw, self.request, self.launch, self.build_sha)

    def test_positive_baseline_owner_receipt(self):
        self.assertEqual(self.verify()['result'], 'Passed')

    def test_original_tuple_binding(self):
        for field in ('runId', 'caseId', 'stimulus'):
            with self.subTest(field=field):
                self.setUp()
                self.raw[field] = 'changed'
                with self.assertRaises(ContractError): self.verify()

    def test_unowned_process_rejected(self):
        self.raw['processId'] = 42
        with self.assertRaises(ContractError): self.verify()

    def test_boolean_cannot_masquerade_as_native_integer(self):
        for name in ('initialState','poisonedState','finalState','preActiveReflection',
                     'preActiveDelegate','preCanaryCount','finalCanaryCount','nativeStimulusReturn'):
            with self.subTest(field=name):
                self.setUp()
                self.raw[name] = True if name in ('poisonedState','finalState') else False
                with self.assertRaises(ContractError): self.verify()

    def test_nested_recovery_boolean_cannot_masquerade_as_integer(self):
        self.raw['firstRecovery'] = self.raw['finalRecovery'] = json.dumps(
            {'published':True,'stateCode':True,'disposition':'RestartRequired','terminalFailureCode':21})
        with self.assertRaises(ContractError): self.verify()

    def test_no_fabricated_acceptance(self):
        self.raw['acceptance'] = True
        with self.assertRaises(ContractError): self.verify()

    def test_pre_poison_must_actually_execute(self):
        for field in ('prePositive','preActiveReflection','preActiveDelegate','preCanaryCount'):
            with self.subTest(field=field):
                self.setUp()
                self.raw[field] = 0
                with self.assertRaises(ContractError): self.verify()

    def test_no_reflection_delegate_or_aot_body_after_poison(self):
        for prefix in ('activeReflection', 'activeDelegate', 'aotReflection'):
            for suffix in ('Attempted', 'Succeeded', 'Exception'):
                with self.subTest(prefix=prefix,suffix=suffix):
                    self.setUp()
                    self.raw[prefix+suffix] = False if suffix == 'Attempted' else (
                        True if suffix == 'Succeeded' else '')
                    with self.assertRaises(ContractError): self.verify()

    def test_shadow_body_side_effect_cannot_change(self):
        for field, value in [('preShadowField', 0), ('finalShadowField', 3), ('shadowFieldReadable', False)]:
            with self.subTest(field=field):
                self.setUp()
                self.raw[field] = value
                with self.assertRaises(ContractError): self.verify()

    def test_aot_side_effect_cannot_change(self):
        self.raw['finalCanaryCount'] = 2
        with self.assertRaises(ContractError): self.verify()

    def test_fixed_diagnostics_and_recovery_must_stay_intact(self):
        for field in ('finalState', 'fixedDiagnosticsReadable', 'recoveryStable', 'finalRecovery'):
            with self.subTest(field=field):
                self.setUp()
                self.raw[field] = None
                with self.assertRaises(ContractError): self.verify()

    def test_old_baseline_guard_must_be_caught(self):
        self.raw['nativeGuardJson'] = json.dumps({'available':True,'activeGuard':1,
            'baselineGuard':0,'caughtOldGuard':0,'stateCode':9})
        with self.assertRaises(ContractError): self.verify()

    def test_real_type_resolution_stimulus_contract(self):
        self.request['stimulus'] = self.raw['stimulus'] = 'type-resolution'
        self.request['caseId'] = self.raw['caseId'] = 'IR-R03-02-release-type'
        self.raw['firstRecovery'] = self.raw['finalRecovery'] = json.dumps({'published':True,
            'stateCode':9,'disposition':'RestartRequired','terminalFailureCode':13})
        self.assertEqual(self.verify()['result'], 'Passed')
        self.raw['nativeStimulusReturn'] = 0
        with self.assertRaises(ContractError): self.verify()

    def test_feature_off_does_not_require_shadow_transaction(self):
        self.request['stimulus'] = self.raw['stimulus'] = 'off'
        self.request['caseId'] = self.raw['caseId'] = 'IR-R03-02-off'
        self.raw.update(initialState=0,finalState=0,prePositive=True,
            preCanaryCount=1,finalCanaryCount=2,activeReflectionAttempted=False,
            activeDelegateAttempted=False,aotReflectionAttempted=False)
        self.assertEqual(self.verify()['result'],'Passed')
        self.raw['finalCanaryCount']=1
        with self.assertRaises(ContractError): self.verify()


if __name__=='__main__':
    unittest.main()
