"""Synthetic contract regressions, not evidence from a Player or the GC."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from batch_contract import ContractError
from runtime_contract import verify_fence, verify_warm, verify_producer_control
from test_runtime_contract import fixture, typename
from run_local import Batch


def natural(cold=True):
    p = fixture(cold)
    f = p['producerFence']
    for key in ('requested', 'acquired', 'released', 'drained'): f[key] = False
    for key in ('ownerOsThread', 'elapsedMicros', 'leaseMs'): f[key] = 0
    if cold:
        p['samples'][2]['counters'] = dict(p['samples'][1]['counters'])
        p['samples'][2]['eventEnd'] = 0
        for e in p['events']:
            e.update(phase=2, thread=2, site='Object::NewAllocSpecific')
            e['type'] = typename('0x5678', 'mscorlib', 'Enumerator', '')
            e['type']['typeKey'] = 'type(mscorlib/System.Runtime.CompilerServices/ConditionalWeakTable`2/Enumerator<System.Byte[][],System.Object>)'
            e['producer'] = dict(osThread=987, recognizedArrayPool=True,
                finalizerType=typename('0x111', 'mscorlib', 'Gen2GcCallback', 'System'),
                callback=dict(name='Gen2GcCallbackFunc', token=123,
                    declaringType=typename('0x222', 'mscorlib', 'TlsOverPerCoreLockedStacksArrayPool`1', 'System.Buffers')))
    return p


def control(p):
    return verify_producer_control(json.dumps(p),p['samples'][1]['counters'],p['samples'][4]['counters'],'Methods')


class ProducerControlContracts(unittest.TestCase):
    def test_unisolated_failure_is_retained(self):
        result = control(natural())
        self.assertEqual(result['unisolatedWarmCertificate'], 'Failed')
        self.assertEqual(result['identifiedLoopAdmissions'], 1)
        self.assertFalse(result['runtimeAcceptance'])
    def test_no_event_is_not_claimed_as_attribution(self):
        result = control(natural(False))
        self.assertEqual(result['observation'], 'NoContaminationObserved')
        self.assertEqual(result['identifiedLoopAdmissions'], 0)
    def test_all_thread_requirement_is_unchanged(self):
        p = natural(); p['producerFence'] = fixture()['producerFence']
        with self.assertRaisesRegex(ContractError, 'Repeated exact-loop'):
            verify_warm(json.dumps(p),p['samples'][1]['counters'],p['samples'][4]['counters'],'Methods')
    def test_control_cannot_fence_away_the_actor(self):
        p=natural();p['producerFence']=fixture()['producerFence']
        with self.assertRaises(ContractError):control(p)
    def test_unknown_finalizer_cannot_establish_the_producer(self):
        p=natural();p['events'][0]['producer']['finalizerType']['name']='Unknown'
        with self.assertRaises(ContractError):control(p)
    def test_unknown_callback_cannot_establish_the_producer(self):
        p=natural();p['events'][0]['producer']['callback']['name']='Other'
        with self.assertRaises(ContractError):control(p)
    def test_nested_owner_is_not_guessed_from_simple_enumerator(self):
        p=natural();p['events'][0]['type']['typeKey']='Enumerator'
        with self.assertRaises(ContractError):control(p)
    def test_os_thread_mapping_required(self):
        p=natural();p['events'][0]['producer']['osThread']=0
        with self.assertRaises(ContractError):control(p)
    def test_owner_proof_work_is_never_allowed(self):
        p=natural();p['events'][0]['thread']=1
        with self.assertRaises(ContractError):control(p)
    def test_incomplete_callback_identity_rejected(self):
        for key in ('callback','finalizerType'):
            p=natural();p['events'][0]['producer'][key]=None
            with self.subTest(key=key), self.assertRaises(ContractError):control(p)
    def test_expired_and_invalid_leases_rejected(self):
        for key in ('expired','invalid'):
            p=fixture();p['producerFence'][key]=True
            with self.subTest(key=key),self.assertRaises(ContractError):verify_fence(p,True)
    def test_unreleased_unacquired_or_undrained_lease_rejected(self):
        for key in ('requested','acquired','released','drained'):
            p=fixture();p['producerFence'][key]=False
            with self.subTest(key=key),self.assertRaises(ContractError):verify_fence(p,True)
    def test_lost_deferred_work_is_rejected(self):
        p=fixture();p['producerFence']['deferred']=1
        with self.assertRaises(ContractError):verify_fence(p,True)
    def test_lease_bound_and_identity_are_fixed(self):
        for key,value in [('ownerOsThread',0),('leaseMs',6000),('elapsedMicros',5000000)]:
            p=fixture();p['producerFence'][key]=value
            with self.subTest(key=key),self.assertRaises(ContractError):verify_fence(p,True)
    def test_scalar_and_field_set_are_strict(self):
        p=fixture();p['producerFence']['leaseMs']=True
        with self.assertRaises(ContractError):verify_fence(p,True)
        p=fixture();p['producerFence']['extra']=True
        with self.assertRaises(ContractError):verify_fence(p,True)
    def test_native_mode_uses_no_warmup_or_counter_waiver(self):
        s=Path(__file__).with_name('PlayerProject').joinpath('R03Player.cs').read_text()
        self.assertIn('preparation < 8',s);self.assertIn('i < 10000',s)
        self.assertNotIn('GC.Collect',s);self.assertNotIn('WaitForPendingFinalizers',s)
        self.assertIn('producerControl ? 0 : 1',s)
    def test_four_controls_continue_after_independent_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Batch.__new__(Batch);b.root=Path(tmp);seen=[]
            ids=('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append')
            b.matrix={'cases':[dict(id=k) for k in ids]}
            def player(c):
                seen.append(c['id'])
                if len(seen)==1:raise ContractError('synthetic failure')
                return {'warmWindow':{'identifiedLoopAdmissions':1}}
            b.player=player
            with self.assertRaises(ContractError):b.producer_controls()
            self.assertEqual(len(seen),4)
            self.assertTrue((b.root/'producer-controls.json').is_file())
    def test_no_attribution_all_four_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Batch.__new__(Batch);b.root=Path(tmp)
            b.matrix={'cases':[dict(id=k) for k in ('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append')]}
            b.player=lambda c:{'warmWindow':{'identifiedLoopAdmissions':0}}
            with self.assertRaisesRegex(ContractError,'NoCoverage'):b.producer_controls()
    def test_at_least_one_identified_control_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Batch.__new__(Batch);b.root=Path(tmp)
            b.matrix={'cases':[dict(id=k) for k in ('C03-moved-slot','C04-old-AOT-guard','C05-direction-reversal','C07-private-primitive-append')]}
            b.player=lambda c:{'warmWindow':{'identifiedLoopAdmissions':int(c['id'].startswith('PC-C03'))}}
            self.assertEqual(b.producer_controls()['identifiedLoopAdmissions'],1)
