#!/usr/bin/env python3
"""Host-only tests of V1 stimulus scope; never launch Unity or import the runner.

AST-load only exact_int/verify_ir from the adjacent real source. All records
below are synthetic unit-test fixtures, not Player receipts. The full general
sidecar verifier is a declared test double: these tests cover classification
and rejection order, not diagnostic fidelity, process provenance or runtime.

Run in the repository:
    python3 -m unittest discover -s Tools/AssemblyShadow/R03IR \
        -p test_terminal_stimulus_scope.py -v
An optional R03_IR_VERIFIER_SOURCE path permits a pinned-before/after check.
"""
import ast
import copy
import json
import os
from pathlib import Path
import unittest

SOURCE = Path(os.environ.get('R03_IR_VERIFIER_SOURCE',
                            str(Path(__file__).with_name('run_terminal_local.py'))))


class ContractRejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractRejected(message)


def load_verifier(path):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'), filename=str(path))
    names = ('exact_int', 'verify_ir')
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if sorted(n.name for n in selected) != sorted(names):
        raise AssertionError('Expected exactly one definition of each tested function')
    sidecar_calls = []

    def host_sidecar(value, raw_path):
        sidecar_calls.append((value, raw_path))
        require(value == 'HostOnlyDiagnostic_TestDouble', 'Host fixture marker')
        return {'kind': 'HostOnlySidecarTestDouble', 'runtimeAcceptance': False}

    namespace = {'require': require, 'loads': json.loads,
                 'verify_complete_general': host_sidecar}
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace['verify_ir'], sidecar_calls


def fixture(stimulus='type-resolution'):
    """Inputs for unit tests only. They are never written as raw Player data."""
    request = {'runId': 'host-test-only', 'caseId': 'HOST-ONLY-'+stimulus,
               'stimulus': stimulus}
    recovery = {'published': True, 'stateCode': 9, 'disposition': 'RestartRequired',
                'terminalFailureCode': 21 if stimulus == 'baseline-owner' else 13}
    encoded = json.dumps(recovery, sort_keys=True)
    raw = {
        'reportTransport': 'NativePreopenedSnapshotV1', 'schemaVersion': 1,
        'kind': 'R03IRPostPoisonEntryV1', 'acceptance': False, 'result': 'Passed',
        'error': None, 'runId': request['runId'], 'caseId': request['caseId'],
        'stimulus': stimulus, 'processId': 123, 'unityVersion': '2022.3.62f2',
        'platform': 'OSXPlayer', 'reserveGcProbeMask': 31,
        'initialState': 6, 'poisonedState': 9, 'finalState': 9, 'prePositive': True,
        'preActiveReflection': 42, 'preActiveDelegate': 42,
        'preCanaryCount': 1, 'preShadowField': 2,
        'finalCanaryCount': 1, 'finalShadowField': 2, 'shadowFieldReadable': True,
        'recoveryStable': True, 'fixedDiagnosticsReadable': True,
        'firstRecovery': encoded, 'finalRecovery': encoded,
        'terminalReportingProbeMask': 15, 'nativeStimulusReturn': 1,
        'finalDiagnostics': 'HostOnlyDiagnostic_TestDouble',
        'nativeGuardJson': json.dumps({'available': True, 'activeGuard': 1,
            'baselineGuard': 0, 'caughtOldGuard': 1, 'stateCode': 9}),
    }
    for prefix in ('activeReflection', 'activeDelegate', 'aotReflection'):
        raw[prefix+'Attempted'] = True
        raw[prefix+'Succeeded'] = False
        raw[prefix+'Exception'] = 'HostOnlyCaughtMarker'
    if stimulus == 'off':
        raw.update(initialState=0, finalState=0, finalCanaryCount=2,
                   reserveGcProbeMask=0, terminalReportingProbeMask=0)
        for prefix in ('activeReflection', 'activeDelegate', 'aotReflection'):
            raw[prefix+'Attempted'] = False
    return raw, request, {'pid': 123}


class StimulusScopeTests(unittest.TestCase):
    def setUp(self):
        self.verify, self.sidecar_calls = load_verifier(SOURCE)

    def call(self, raw, request, launch):
        return self.verify(raw, request, launch, 'host-only-build-digest',
                           raw_path=Path('host-only-not-a-player/raw.json'))

    def test_allowed_baseline_owner(self):
        self.assert_allowed('baseline-owner')

    def test_allowed_type_resolution(self):
        self.assert_allowed('type-resolution')

    def test_allowed_off_control(self):
        self.assert_allowed('off')

    def assert_allowed(self, stimulus):
        data = fixture(stimulus)
        before = copy.deepcopy(data)
        result = self.call(*data)
        self.assertEqual(result['result'], 'Passed')
        self.assertEqual(result['stimulus'], stimulus)
        for flag in ('runtimeAcceptance', 'R03Accepted', 'H2Passed'):
            self.assertIs(result[flag], False)
        self.assertEqual(len(self.sidecar_calls), 0 if stimulus == 'off' else 1)
        self.assertEqual(data, before, 'Verification must not rewrite input records')

    def test_missing_stimulus(self):
        raw, request, launch = fixture()
        request.pop('stimulus')
        with self.assertRaisesRegex(ContractRejected, 'Unsupported'):
            self.call(raw, request, launch)
        self.assertEqual(self.sidecar_calls, [])

    def test_baseline_requires_baseline_reason(self):
        raw, request, launch = fixture('baseline-owner')
        for key in ('firstRecovery', 'finalRecovery'):
            record = json.loads(raw[key]); record['terminalFailureCode'] = 13
            raw[key] = json.dumps(record)
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_type_requires_type_reason(self):
        raw, request, launch = fixture()
        for key in ('firstRecovery', 'finalRecovery'):
            record = json.loads(raw[key]); record['terminalFailureCode'] = 21
            raw[key] = json.dumps(record)
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_real_initializer_error_cannot_be_counted_as_type(self):
        raw, request, launch = fixture()
        for key in ('firstRecovery', 'finalRecovery'):
            record = json.loads(raw[key]); record['terminalFailureCode'] = 19
            raw[key] = json.dumps(record)
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_captured_generic_error_cannot_be_counted_as_type(self):
        # AssemblyShadowTypes.h at native 41764ae1...: BaselineAlreadyUsed=15.
        raw, request, launch = fixture()
        for key in ('firstRecovery', 'finalRecovery'):
            record = json.loads(raw[key]); record['terminalFailureCode'] = 15
            raw[key] = json.dumps(record)
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_runtime_abi_mismatch_is_not_initializer_failure(self):
        # RuntimeAbiMismatch=17; ModuleInitializerFailed=19. Never renumber ABI.
        raw, request, launch = fixture()
        for key in ('firstRecovery', 'finalRecovery'):
            record = json.loads(raw[key]); record['terminalFailureCode'] = 17
            raw[key] = json.dumps(record)
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_recovery_change_is_rejected(self):
        raw, request, launch = fixture()
        raw['finalRecovery'] = raw['firstRecovery'] + ' '
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)

    def test_nonterminal_off_counter_growth_is_required(self):
        raw, request, launch = fixture('off')
        raw['finalCanaryCount'] = 1
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)


def unsupported_case(stimulus):
    def test(self):
        raw, request, launch = fixture()
        # Identical type-failure content, only relabelled in BOTH input records.
        # This reproduces the previous classifier hole without a real Player.
        raw['stimulus'] = request['stimulus'] = stimulus
        with self.assertRaisesRegex(ContractRejected, 'Unsupported'):
            self.call(raw, request, launch)
        self.assertEqual(self.sidecar_calls, [], 'Reject before sidecar processing')
    return test


for name, value in {
    'captured_generic': 'captured-generic',
    'captured_generic_failure': 'captured-generic-failure',
    'initializer_failure': 'initializer-failure',
    'module_initializer': 'module-initializer',
    'engine_goes_to_other_verifier': 'engine-unhandled',
    'unknown': 'future-path', 'empty': '', 'whitespace': 'type-resolution ',
    'capitalized': 'Type-Resolution', 'none': None, 'boolean': True,
    'integer': 1, 'list': ['type-resolution'], 'mapping': {'type-resolution': 1},
}.items():
    setattr(StimulusScopeTests, 'test_reject_stimulus_'+name, unsupported_case(value))


def invalid_raw_case(field, value):
    def test(self):
        raw, request, launch = fixture()
        raw[field] = value
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)
    return test


for name, field, value in [
    ('schema_bool', 'schemaVersion', True), ('schema_float', 'schemaVersion', 1.0),
    ('schema_new', 'schemaVersion', 2), ('schema_string', 'schemaVersion', '1'),
    ('acceptance_true', 'acceptance', True), ('result', 'result', 'NotRun'),
    ('pre_positive_false', 'prePositive', False), ('pre_field', 'preShadowField', 0),
    ('post_field_changed', 'finalShadowField', 3), ('post_field_unreadable', 'shadowFieldReadable', False),
    ('post_canary_changed', 'finalCanaryCount', 2), ('state_healthy', 'finalState', 6),
    ('boolean_counter', 'preCanaryCount', True), ('wrong_pid', 'processId', 124),
    ('wrong_case', 'caseId', 'OTHER-HOST-CASE'), ('wrong_run', 'runId', 'other'),
    ('no_native_stimulus', 'nativeStimulusReturn', 0), ('wrong_transport', 'reportTransport', 'Other'),
]:
    setattr(StimulusScopeTests, 'test_reject_'+name, invalid_raw_case(field, value))

for prefix in ('activeReflection', 'activeDelegate', 'aotReflection'):
    for suffix, value in [('Attempted', False), ('Succeeded', True), ('Exception', '')]:
        setattr(StimulusScopeTests, 'test_reject_'+prefix+'_'+suffix,
                invalid_raw_case(prefix+suffix, value))


def non_object_case(which, value):
    def test(self):
        raw, request, launch = fixture()
        if which == 'raw': raw = value
        else: request = value
        with self.assertRaises(ContractRejected):
            self.call(raw, request, launch)
        self.assertEqual(self.sidecar_calls, [])
    return test

for which in ('raw', 'request'):
    for name, value in [('none', None), ('list', []), ('string', 'host-only')]:
        setattr(StimulusScopeTests, 'test_non_object_'+which+'_'+name,
                non_object_case(which, value))


if __name__ == '__main__':
    unittest.main(verbosity=2)
