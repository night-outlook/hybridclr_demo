#!/usr/bin/env python3
"""Synthetic host-only schema tests, NEVER evidence of actual Player execution."""
import copy
import json
import unittest
from remaining_witness_contracts import WitnessRejected, verify_remaining, SENTINEL

SHA = 'a' * 64
PINS = ('requestSha256','fixtureSha256','buildReceiptSha256','sourceManifestSha256','nativeOverlaySha256')


def fixture(stimulus):
    authority = {p: SHA for p in PINS}
    authority['repositories'] = {name: '1'*40 for name in
        ('hybridclr_demo','hybridclr','hybridclr_unity','il2cpp_plus')}
    authority['fixtureMvid'] = '11111111-1111-1111-1111-111111111111'
    request = {'runId':'host-only-nonce-1234567890123456', 'caseId':'SYNTHETIC-'+stimulus,
               'stimulus':stimulus}
    raw = dict(authority, schemaVersion=1, kind='R03IRRemainingTerminalWitnessV1',
        reportTransport='NativePreopenedSnapshotV2', result='ObservedNotAccepted',
        runtimeAcceptance=False, R03Accepted=False, H2Passed=False,
        runId=request['runId'], caseId=request['caseId'], stimulus=stimulus,
        processId=4567, unityVersion='2022.3.62f2', platform='OSXPlayer',
        nativeObserverBoundBeforeFailure=True,
        nativeObserverReadAfterFailure=stimulus != 'initializer-control',
        preparedField=3, finalField=3, preDirectReturn=42, preDelegateReturn=42,
        preGenericReturn=42, commitReturn=0, initialState=6, finalState=9,
        postTerminalEntryAttempted=True, postTerminalEntrySucceeded=False,
        postTerminalException='ManagedExceptionCaught', preAotCanaryCount=1,
        finalAotCanaryCount=1, firstFailureStable=True,
        initializerAttempted=False, initializerCompleted=False)
    error = 15 if stimulus == 'captured-generic' else 19
    recovery = json.dumps({'published':True,'disposition':'RestartRequired',
                           'stateCode':9,'terminalFailureCode':error}, sort_keys=True)
    raw['firstRecovery'] = raw['finalRecovery'] = recovery
    if stimulus == 'captured-generic':
        raw.update(guardReason='CapturedBaselineType', capturedArgumentAssembly='Methods',
                   physicalGenericOwnerAssembly='Assembly-CandidateIndependent',
                   physicalBaselineArgumentVerified=True, closedGenericMethodInflated=True,
                   nativeMethodGuardEntered=True, physicalGenericOwnerImageIndex=3,
                   physicalCapturedArgumentImageIndex=7)
    else:
        raw.update(commitReturn=19, initialState=5, initializerAttempted=True,
                   initializerCompleted=False, initializerAttemptCount=1,
                   initializerSentinelObserved=True, initializerSentinel=SENTINEL,
                   afterPublication=True, firstFailureDetail='Methods: '+SENTINEL)
    if stimulus == 'initializer-control':
        raw.update(commitReturn=0, initialState=6, finalState=6,
                   initializerAttempted=True, initializerCompleted=True,
                   initializerSentinelObserved=False, postTerminalEntryAttempted=False,
                   firstRecovery=None, finalRecovery=None)
    return raw, request, {'pid':4567}, authority


class RemainingWitnessContracts(unittest.TestCase):
    def check(self, data):
        return verify_remaining(*data)

    def test_three_positive_schema_controls(self):
        for kind in ('captured-generic','initializer-failure','initializer-control'):
            with self.subTest(kind=kind):
                data=fixture(kind); before=copy.deepcopy(data)
                result=self.check(data)
                self.assertEqual(result['result'],'SchemaSemanticsOnly')
                self.assertIs(result['runtimeAcceptance'],False)
                self.assertEqual(data,before)

    def test_adversarial_mutations(self):
        mutants = [
            ('captured-generic', 'guardReason', 'Other'),
            ('captured-generic', 'physicalBaselineArgumentVerified', False),
            ('captured-generic', 'nativeMethodGuardEntered', False),
            ('captured-generic', 'physicalGenericOwnerAssembly', 'Methods'),
            ('captured-generic', 'closedGenericMethodInflated', False),
            ('captured-generic', 'initializerAttempted', True),
            ('captured-generic', 'physicalGenericOwnerImageIndex', 7),
            ('captured-generic', 'physicalCapturedArgumentImageIndex', True),
            ('initializer-failure', 'commitReturn', 0),
            ('initializer-failure', 'commitReturn', 13),
            ('initializer-failure', 'afterPublication', False),
            ('initializer-failure', 'initializerSentinelObserved', False),
            ('initializer-failure', 'initializerAttemptCount', 0),
            ('initializer-failure', 'initializerSentinel', 'Wrong'),
            ('initializer-failure', 'firstFailureDetail', 'Lost module failure'),
            ('initializer-control', 'finalState', 9),
            ('initializer-control', 'initializerCompleted', False),
            ('initializer-control', 'firstRecovery', '{}'),
            ('initializer-control', 'postTerminalEntryAttempted', True),
        ]
        common = [
            ('schemaVersion',True), ('reportTransport','NativePreopenedSnapshotV1'),
            ('runtimeAcceptance',True), ('R03Accepted',True),
            ('nativeObserverBoundBeforeFailure',False), ('preparedField',2),
            ('preGenericReturn',43), ('processId', True), ('fixtureSha256','b'*64),
            ('sourceManifestSha256',None), ('requestSha256','a'*63),
            ('fixtureMvid','BAD'), ('repositories',{'hybridclr_demo':'1'*40}),
        ]
        terminal = [
            ('finalField',4), ('nativeObserverReadAfterFailure',False),
            ('postTerminalEntrySucceeded',True), ('preAotCanaryCount',2),
            ('finalAotCanaryCount',2), ('firstFailureStable',False),
            ('finalRecovery','{}'),
        ]
        count=0
        for stimulus in ('captured-generic','initializer-failure','initializer-control'):
            for field,value in (common + ([] if stimulus=='initializer-control' else terminal) +
                    [(k,v) for s,k,v in mutants if s==stimulus]):
                with self.subTest(stimulus=stimulus, field=field):
                    data=list(fixture(stimulus)); data[0][field]=value
                    with self.assertRaises(WitnessRejected): self.check(data)
                    count+=1
        self.assertGreaterEqual(count,55)

    def test_terminal_codes_do_not_alias(self):
        for stimulus,other in [('captured-generic',21),('captured-generic',13),
                               ('initializer-failure',13),('initializer-failure',15)]:
            data=list(fixture(stimulus))
            recovery=json.loads(data[0]['firstRecovery'])
            recovery['terminalFailureCode']=other
            data[0]['firstRecovery']=data[0]['finalRecovery']=json.dumps(recovery)
            with self.subTest(stimulus=stimulus, error=other):
                with self.assertRaises(WitnessRejected): self.check(data)

    def test_relabel_k_type_failure_to_new_stimulus(self):
        for new in ('captured-generic','initializer-failure'):
            data=list(fixture('captured-generic'))
            data[0]['stimulus']=data[1]['stimulus']=new
            data[0]['kind']='R03IRPostPoisonEntryV1'
            with self.assertRaises(WitnessRejected): self.check(data)

    def test_unsupported_stimuli(self):
        for unsupported in ('off','type-resolution','engine-unhandled',None,False,1,[]):
            data=list(fixture('captured-generic'))
            data[0]['stimulus']=data[1]['stimulus']=unsupported
            with self.assertRaises(WitnessRejected): self.check(data)

    def test_authority_cannot_come_from_forged_raw(self):
        data=list(fixture('captured-generic'))
        data[0]['fixtureSha256']=data[1]['fixtureSha256']='b'*64
        with self.assertRaises(WitnessRejected): self.check(data)

    def test_zero_based_image_index_is_valid(self):
        data=list(fixture('captured-generic'))
        data[0]['physicalGenericOwnerImageIndex']=0
        self.assertEqual(self.check(data)['result'],'SchemaSemanticsOnly')

    def test_wrong_pid(self):
        data=list(fixture('initializer-control'))
        data[2]['pid']=9876
        with self.assertRaises(WitnessRejected): self.check(data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
