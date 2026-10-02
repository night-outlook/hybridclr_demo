"""Synthetic verifier tests only: these dictionaries are NOT Player evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from batch_contract import ContractError, RAW_FIELDS, RECOVERY_FIELDS, METHOD_FIELDS, loads, sha, verify_raw
from batch_evidence import excluded, finalize, selected_files
from run_local import Batch


def sample(outcome='success', method=False, guard=False):
    request = {'runId': 'synthetic-run', 'caseId': 'synthetic-case', 'baselineId': 'synthetic-baseline',
               'dlls': [{'name': 'Methods'}], 'invokeAssembly': 'Methods', 'observeMethod': method, 'oldExecutionGuard': guard, 'producerControl': False}
    expected = {'outcome': outcome, 'value': 42}
    raw = {key: '' for key in RAW_FIELDS.split()}
    raw.update(schemaVersion=3, kind='R03PlayerObservation', runId=request['runId'], caseId=request['caseId'],
               requestSha256='a' * 64, pid=1234, unityVersion='2022.3.62f2', platform='OSXPlayer',
               il2cpp=True, published=True, phase='Completed', acceptance=False, finalState=6,
               diagnosticsCode=0, recoveryCode=0, invocationResult=42, delegateResult=42, warmAllocationCount=10000)
    phases = ['Configure', 'Begin', 'Reserve', 'Stage:Methods', 'Validate', 'Commit']
    raw['steps'] = [{'phase': p, 'code': 0, 'state': 6 if p == 'Commit' else 3} for p in phases]
    diagnostics = {'schemaVersion': 1, 'stateCode': 6, 'baselineBuildId': request['baselineId'],
                   'patchId': 'R03-' + request['runId'], 'lastError': 0, 'detail': ''}
    recovery = {key: '' for key in RECOVERY_FIELDS.split()}
    recovery.update(schemaVersion=1, enabled=True, capabilityVersion=1, stateCode=6, state='Committed', published=True,
                    abortAllowed=False, dispositionCode=4, disposition='ActiveShadow', terminalFailureCode=0,
                    reason='', retainedBytes=20, baselineEligibilityRequiresStartupValidation=False)
    if outcome == 'baseline':
        raw.update(steps=[], published=False, invocationResult=41, delegateResult=41)
    if outcome in ('admission-reject', 'target-cycle'):
        code, state = (16, 8) if outcome == 'admission-reject' else (13, 3)
        raw.update(steps=raw['steps'][:-1], published=False, phase='Validate', finalState=state,
                   invocationResult=0, delegateResult=0, warmAllocationCount=0)
        raw['steps'][-1].update(code=code, state=state)
        diagnostics.update(lastError=code, stateCode=state, detail='NativeLayoutAdmissionV1: synthetic negative')
        recovery.update(published=False, stateCode=state, disposition='RestartRequired' if state == 8 else 'CorrectInputOrAbort', terminalFailureCode=code)
    if outcome == 'legacy-late-layout':
        raw.update(phase='ActiveInvoke', exception='Synthetic exception, not empirical evidence', finalState=9,
                   invocationResult=0, delegateResult=0, warmAllocationCount=0)
        diagnostics.update(lastError=16, stateCode=9)
        recovery.update(stateCode=9, disposition='RestartRequired', terminalFailureCode=16)
    if method:
        value = {key: 0 for key in METHOD_FIELDS.split()}
        value.update(schemaVersion=1, available=True, mappingCode=0, mappingDetail='', baselineToken=100, activeToken=101,
                     baselineSlot=0, activeSlot=1, differentPhysicalMethods=True, activeOwner=True, cacheIdentityStable=True,
                     activeGuard=-1, baselineGuard=-1, stateCode=6, activeGeneration=1)
        if outcome == 'legacy-slot':
            value.update(mappingCode=13, mappingDetail='ShadowMethodNotFound synthetic test', activeOwner=False)
        if guard:
            value.update(activeGuard=1, baselineGuard=0, stateCode=9)
            raw['finalState'] = 9
            diagnostics.update(stateCode=9, lastError=21)
            recovery.update(stateCode=9, disposition='RestartRequired', terminalFailureCode=21)
        raw['nativeMethod'] = json.dumps(value)
    raw['diagnostics'] = json.dumps(diagnostics)
    raw['recovery'] = json.dumps(recovery)
    if outcome == 'admission-reject':
        from test_rejection_contract import attach_rejection_observation
        attach_rejection_observation(raw, request)
        raw['rejectionProbe'] = json.dumps(raw['rejectionProbe'])
    return request, raw, expected


def check(value):
    return verify_raw(value[0], value[1], value[2], 'a' * 64, 1234)


class ObservationContracts(unittest.TestCase):
    def test_valid_shapes_are_only_verifier_inputs(self):
        for outcome, method, guard in [('baseline', False, False), ('success', False, False), ('success', True, False),
            ('success', True, True), ('admission-reject', False, False), ('target-cycle', False, False),
            ('legacy-late-layout', False, False), ('legacy-slot', True, False)]:
            with self.subTest(outcome=outcome, method=method, guard=guard):
                self.assertEqual(check(sample(outcome, method, guard))['outcome'], outcome)

    def test_missing_raw_members(self):
        for key in RAW_FIELDS.split():
            value = sample()
            del value[1][key]
            with self.subTest(key=key), self.assertRaises(ContractError): check(value)

    def test_unknown_raw_member(self):
        value = sample(); value[1]['claim'] = 'Passed'
        with self.assertRaises(ContractError): check(value)

    def test_request_binding(self):
        for key, replacement in [('runId', 'other'), ('caseId', 'other'), ('requestSha256', 'b' * 64), ('pid', 5678)]:
            value = sample(); value[1][key] = replacement
            with self.subTest(key=key), self.assertRaises(ContractError): check(value)

    def test_wrong_runtime_or_platform(self):
        for key, replacement in [('il2cpp', False), ('platform', 'OSXEditor'), ('unityVersion', 'other'), ('acceptance', True)]:
            value = sample(); value[1][key] = replacement
            with self.subTest(key=key), self.assertRaises(ContractError): check(value)

    def test_api_order_and_membership(self):
        for operation in ('missing', 'duplicate', 'reverse'):
            value = sample()
            if operation == 'missing': value[1]['steps'].pop(2)
            elif operation == 'duplicate': value[1]['steps'].append(copy.deepcopy(value[1]['steps'][-1]))
            else: value[1]['steps'].reverse()
            with self.subTest(operation=operation), self.assertRaises(ContractError): check(value)

    def test_api_boolean_is_not_integer_error(self):
        value = sample(); value[1]['steps'][0]['code'] = False
        with self.assertRaises(ContractError): check(value)

    def test_wrong_rejection_phase(self):
        value = sample('admission-reject'); value[1]['steps'][2]['code'] = 16
        with self.assertRaises(ContractError): check(value)

    def test_unrelated_error_16_is_not_layout_proof(self):
        value = sample('admission-reject')
        diagnostic = loads(value[1]['diagnostics']); diagnostic['detail'] = 'Unrelated resource error'
        value[1]['diagnostics'] = json.dumps(diagnostic)
        with self.assertRaises(ContractError): check(value)

    def test_failed_admission_cannot_publish(self):
        value = sample('admission-reject'); value[1]['published'] = True
        with self.assertRaises(ContractError): check(value)

    def test_runtime_and_recovery_disagree(self):
        value = sample(); recovery = loads(value[1]['recovery']); recovery['published'] = False
        value[1]['recovery'] = json.dumps(recovery)
        with self.assertRaises(ContractError): check(value)

    def test_legacy_layout_requires_guard_code(self):
        value = sample('legacy-late-layout'); recovery = loads(value[1]['recovery']); recovery['terminalFailureCode'] = 13
        value[1]['recovery'] = json.dumps(recovery)
        with self.assertRaises(ContractError): check(value)

    def test_wrong_method_slot_or_owner(self):
        for key, replacement in [('activeSlot', 0), ('activeOwner', False), ('differentPhysicalMethods', False), ('cacheIdentityStable', False)]:
            value = sample('success', True); method = loads(value[1]['nativeMethod']); method[key] = replacement
            value[1]['nativeMethod'] = json.dumps(method)
            with self.subTest(key=key), self.assertRaises(ContractError): check(value)

    def test_baseline_initializer_must_not_run(self):
        value = sample('success', True); method = loads(value[1]['nativeMethod']); method['baselineCctorAfter'] = 1
        value[1]['nativeMethod'] = json.dumps(method)
        with self.assertRaises(ContractError): check(value)

    def test_old_method_cannot_be_approved(self):
        value = sample('success', True, True); method = loads(value[1]['nativeMethod']); method['baselineGuard'] = 1
        value[1]['nativeMethod'] = json.dumps(method)
        with self.assertRaises(ContractError): check(value)

    def test_legacy_slot_does_not_count_arbitrary_failure(self):
        value = sample('legacy-slot', True); method = loads(value[1]['nativeMethod']); method['mappingDetail'] = 'Other error'
        value[1]['nativeMethod'] = json.dumps(method)
        with self.assertRaises(ContractError): check(value)

    def test_no_counter_data_is_not_warm_proof(self):
        value = sample(); value[2]['warmCertificate'] = True
        with self.assertRaises((ContractError, ValueError)): check(value)

    def test_actual_invocation_values_required(self):
        for key, replacement in [('invocationResult', 0), ('delegateResult', 0), ('warmAllocationCount', 9999)]:
            value = sample(); value[1][key] = replacement
            with self.subTest(key=key), self.assertRaises(ContractError): check(value)

    def test_duplicate_json_rejected(self):
        with self.assertRaises(ContractError): loads('{"a":1,"a":2}')

    def test_nonfinite_json_rejected(self):
        for text in ('NaN', 'Infinity', '-Infinity'):
            with self.subTest(text=text), self.assertRaises(ContractError): loads('{"a":' + text + '}')


class EvidenceContracts(unittest.TestCase):
    def test_cache_pruning_contract(self):
        self.assertTrue(excluded(('projects', 'candidate', 'Library', 'data')))
        self.assertTrue(excluded(('reference-worktrees', 'hybridclr', '.git')))
        self.assertFalse(excluded(('projects', 'candidate', 'Assets', 'source.cs')))
        self.assertFalse(excluded(('builds', 'candidate', 'R03.app', 'Contents')))

    def test_actual_file_seal_and_final_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'raw.txt').write_text('synthetic verifier input\n')
            result = finalize(root, {'result': 'EvidenceReadyForPrimaryReview', 'cells': []})
            self.assertEqual(result['sealStatus'], 'Passed')
            self.assertFalse(result['R03Accepted']); self.assertFalse(result['H2Passed'])
            self.assertEqual(result['executionLedgerSha256'], sha(root / 'BATCH_EXECUTION.json'))
            self.assertEqual(result['seal']['archiveSha256'], sha(root / 'evidence.tar.gz'))

    def test_seal_failure_cannot_leave_ready_status(self):
        with tempfile.TemporaryDirectory() as temporary, patch('batch_evidence.seal', side_effect=OSError('synthetic write failure')):
            root = Path(temporary)
            result = finalize(root, {'result': 'EvidenceReadyForPrimaryReview', 'cells': []})
            self.assertEqual(result['result'], 'ReturnRequired')
            self.assertEqual(loads((root / 'LOCAL_BATCH_RESULT.json').read_text())['sealStatus'], 'Failed')
            self.assertTrue((root / 'SEAL_FAILED.json').is_file())

    def test_existing_results_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'BATCH_EXECUTION.json').write_text('preserved')
            with self.assertRaises(FileExistsError): finalize(root, {'result': 'ReturnRequired'})
            self.assertEqual((root / 'BATCH_EXECUTION.json').read_text(), 'preserved')

    def test_included_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'actual').write_text('x'); (root / 'alias').symlink_to('actual')
            with self.assertRaises(ContractError): selected_files(root)

    def test_complete_file_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); file = root / 'source'; file.write_text('original')
            entries = [{'path': 'source', 'size': file.stat().st_size, 'sha256': sha(file)}]
            Batch.verify_inventory(root, entries)
            file.write_text('modified')
            with self.assertRaises(ContractError): Batch.verify_inventory(root, entries)

    def test_inventory_addition_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); file = root / 'source'; file.write_text('x')
            entries = [{'path': 'source', 'size': 1, 'sha256': sha(file)}]
            (root / 'unexpected').write_text('y')
            with self.assertRaises(ContractError): Batch.verify_inventory(root, entries)

    def test_inventory_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); file = root / 'source'; file.write_text('x')
            entry = {'path': 'source', 'size': 1, 'sha256': sha(file)}
            with self.assertRaises(ContractError): Batch.verify_inventory(root, [entry, entry])

    def test_inventory_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ContractError):
                Batch.verify_inventory(temporary, [{'path': '../outside', 'size': 0, 'sha256': '0' * 64}])


if __name__ == '__main__':
    import sys
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    if suite.countTestCases() != 29:
        raise SystemExit('Incomplete verifier contract discovery')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
