#!/usr/bin/env python3
"""Synthetic schema-only negatives for the separate initializer diagnostic."""
import copy
import json
import unittest
from verify_initializer_observation import Rejected, strict_load, verify


def fixture(mode='initializer-failure'):
    sha = 'a' * 64
    request = {'runId': 'HostInitializerEvidenceRun000001',
               'caseId': 'HOST-INIT', 'stimulus': mode, 'dllSha256': sha}
    raw = {'schemaVersion': 1,
           'kind': 'R03IRInitializerCommitObservationV1',
           'reportTransport': 'NativePreopenedInitializerObservationV1',
           'result': 'ObservedNotAccepted',
           'runId': request['runId'], 'caseId': request['caseId'],
           'stimulus': mode, 'fixtureSha256': sha, 'processId': 987,
           'commitReturn': 0 if mode == 'initializer-control' else 19,
           'finalState': 6 if mode == 'initializer-control' else 9,
           'nativeObserverBoundBeforeFailure': True,
           'preparedField': 3, 'finalField': 3, 'positiveMask': 15,
           'initializerCallbackCalls': 1,
           'postAotAttempted': mode != 'initializer-control',
           'postAotSucceeded': False, 'firstRecoveryAuthenticated': False,
           'completeDiagnosticsAuthenticated': False,
           'nativeV2TransportImplemented': False,
           'runtimeAcceptance': False, 'R03Accepted': False,
           'H2Passed': False}
    return raw, request, {'pid':987}, sha


class InitializerDiagnosticHostTests(unittest.TestCase):
    def test_two_separate_schemas(self):
        for mode in ('initializer-control','initializer-failure'):
            with self.subTest(mode=mode):
                data = fixture(mode)
                before = copy.deepcopy(data)
                result = verify(*data)
                self.assertEqual(result['result'], 'SchemaConsistentNotRuntimeAuthenticated')
                self.assertIs(result['runtimeAcceptance'],False)
                self.assertIs(result['nativeV2TransportImplemented'],False)
                self.assertEqual(before,data)

    def test_fail_closed_mutations(self):
        common = {
            'schemaVersion': True,
            'kind': 'R03IRRemainingTerminalWitnessV1',
            'reportTransport': 'NativePreopenedSnapshotV2',
            'result': 'Passed',
            'runId': 'wrong-run',
            'caseId': 'other',
            'fixtureSha256': 'b'*64,
            'processId': 0,
            'nativeObserverBoundBeforeFailure': False,
            'preparedField': 2,
            'finalField': 4,
            'positiveMask': 7,
            'initializerCallbackCalls': 2,
            'postAotSucceeded': True,
            'firstRecoveryAuthenticated': True,
            'completeDiagnosticsAuthenticated': True,
            'nativeV2TransportImplemented': True,
            'runtimeAcceptance': True, 'R03Accepted': True, 'H2Passed': True,
        }
        for mode in ('initializer-control','initializer-failure'):
            changes = dict(common,
                           commitReturn=19 if mode=='initializer-control' else 0,
                           finalState=9 if mode=='initializer-control' else 6,
                           postAotAttempted=mode=='initializer-control')
            for name, altered in changes.items():
                with self.subTest(mode=mode,key=name):
                    data=list(fixture(mode))
                    data[0][name]=altered
                    with self.assertRaises(Rejected):
                        verify(*data)

    def test_missing_and_extra_attributes_rejected(self):
        data=list(fixture())
        del data[0]['positiveMask']
        with self.assertRaises(Rejected): verify(*data)
        data=list(fixture())
        data[0]['claimedPlayerPassed']=True
        with self.assertRaises(Rejected): verify(*data)

    def test_request_and_launch_are_independent(self):
        data=list(fixture())
        data[1]['runId']='bad'
        with self.assertRaises(Rejected): verify(*data)
        data=list(fixture())
        data[2]['pid']=988
        with self.assertRaises(Rejected): verify(*data)
        data=list(fixture())
        data[3]='b'*64
        with self.assertRaises(Rejected): verify(*data)

    def test_json_duplicate_nonfinite_and_oversize_rejected(self):
        for raw in (b'{"kind":"A","kind":"B"}', b'{"x":NaN}',
                    b'{"x":Infinity}',b'x'*2049,b''):
            with self.subTest(raw=raw[:30]),self.assertRaises((Rejected, ValueError)):
                strict_load(raw)

    def test_actual_native_json_shape_round_trip(self):
        data=fixture()
        encoded=(json.dumps(data[0],separators=(',',':'))+'\n').encode()
        parsed=strict_load(encoded)
        self.assertEqual(verify(parsed,*data[1:])['result'],
                         'SchemaConsistentNotRuntimeAuthenticated')

    def test_original_k_relabel_rejected(self):
        data=list(fixture())
        data[0]['kind']='R03IRPostPoisonEntryV1'
        data[0]['reportTransport']='NativePreopenedSnapshotV1'
        with self.assertRaises(Rejected): verify(*data)

    def test_no_unstated_player_acceptance(self):
        data=fixture()
        result=verify(*data)
        for key in ('R03Accepted','H2Passed','runtimeAcceptance','firstRecoveryAuthenticated'):
            self.assertIs(result[key],False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
