"""Synthetic verifier inputs only. Never used as native/Player evidence."""
import copy
import json
import unittest
from runtime_contract import COUNTERS, COLD, LAYOUT, verify_warm, verify_primitive_layout
from batch_contract import ContractError


def typename(pointer='0x1234', assembly='Methods', name='Node', namespace='R03'):
    return dict(physical=pointer, assembly=assembly, name=name, namespace=namespace, typeKey=assembly + '/' + namespace + '/' + name)


def fixture(cold=False):
    p = dict(schemaVersion=2, available=True, policy='R03ExactAllocationWindowV1', used=True,
             sealed=True, invalid=False, overflow=False, generation=1, ownerThread=1,
             target=typename(), eventCapacity=128, samples=[], events=[], layouts=[], runtimeAcceptance=False)
    p['producerFence'] = dict(policy='R03ArrayPoolFinalizerFenceV1', requested=True, acquired=True, released=True, expired=False, invalid=False, drained=True, admitted=0, completed=0, deferred=0, deferredCompleted=0, ownerOsThread=100, elapsedMicros=10, leaseMs=5000)
    c = {k: 0 for k in COUNTERS}
    if cold:
        for metric, amount in zip((COLD[0], COLD[1], COLD[3], COLD[4]), (1, 1, 1, 80)):
            p['events'].append(dict(index=len(p['events']), metric=metric, amount=amount, phase=1,
                                    thread=1, generation=1, domain=1, context='0x0', site='test:observer',
                                    type=typename('0x5678', 'mscorlib', 'String', 'System'),
                                    producer=dict(osThread=0, recognizedArrayPool=False, finalizerType=None, callback=None)))
    for label in (0, 10, 1, 2, 11, 3):
        if label == 1 and cold:
            for e in p['events']: c[e['metric']] += e['amount']
        if label == 2: c['admissionCacheHits'] = c['baselineStateChecks'] = 10000
        p['samples'].append(dict(label=label, eventEnd=len(p['events']) if label in (1, 2, 11, 3) else 0,
                                 thread=1, saturated=False, droppedThreads=0, counters=dict(c)))
    return p


def check(p):
    return verify_warm(json.dumps(p), p['samples'][1]['counters'], p['samples'][4]['counters'], 'Methods')


def layout():
    p = fixture(); r = {k: 0 for k in LAYOUT.split()}
    for k in ('fieldsChanged', 'baselineReady', 'targetReady', 'targetDefinitionReady', 'physicalProof'): r[k] = True
    for k in ('sourceSizeInited', 'targetSizeInited', 'sourcePending', 'targetPending', 'baselineInitialized',
              'baselineVtable', 'targetInitialized', 'targetVtable', 'truncated', 'baselineInitializedAtRead', 'baselineVtableAtRead'): r[k] = False
    r.update(baseline=typename('0x22', 'R03Contract'), target=typename('0x33', 'R03Contract'),
             sourceSize=24, targetSize=32, sourceNativeSize=-1, targetNativeSize=-1,
             sourceFieldCount=1, targetFieldCount=2, sourceOffsets=[16], targetOffsets=[16, 24],
             sourceAttrs=[1], targetAttrs=[1, 1], targetStorage=[4, 8])
    p['layouts'] = [r]; return p


class WarmContracts(unittest.TestCase):
    def test_zero_native_work(self): self.assertEqual(check(fixture())['exactLoopProofDelta'], 0)
    def test_attributed_broad_observer_work(self): self.assertEqual(len(check(fixture(True))['broadColdEvents']), 4)
    def test_unattributed_extra_miss(self):
        p=fixture();p['samples'][-1]['counters'][COLD[0]]=1
        with self.assertRaisesRegex(ContractError, 'Unattributed'): check(p)
    def test_exact_loop_cold_work_rejected(self):
        p=fixture(True);p['samples'][2]['counters'] = dict(p['samples'][1]['counters']);p['samples'][2]['eventEnd']=0
        for e in p['events']: e['phase']=2
        with self.assertRaisesRegex(ContractError, 'exact-loop'): check(p)
    def test_no_target_warmup_by_observer(self):
        p=fixture(True)
        for e in p['events']: e['type']=copy.deepcopy(p['target'])
        with self.assertRaisesRegex(ContractError, 'Target proof'): check(p)
    def test_baseline_logical_target_is_also_forbidden(self):
        p=fixture(True)
        for e in p['events']: e['type']=typename('0x9999')
        with self.assertRaisesRegex(ContractError, 'Target proof'): check(p)
    def test_marshal_snapshots_are_bound(self):
        p=fixture(True);after=dict(p['samples'][4]['counters']);after[COLD[0]]+=1
        with self.assertRaisesRegex(ContractError, 'snapshot binding'): verify_warm(json.dumps(p),p['samples'][1]['counters'],after,'Methods')
    def test_trace_completeness_flags(self):
        for k,v in [('sealed',False),('invalid',True),('overflow',True),('available',False),('used',False),('runtimeAcceptance',True)]:
            with self.subTest(k=k):
                p=fixture();p[k]=v
                with self.assertRaises(ContractError):check(p)
    def test_boundaries_must_be_exact(self):
        for k in ('label','eventEnd','thread','saturated','droppedThreads'):
            p=fixture(True);p['samples'][1][k]={'label':3,'eventEnd':2,'thread':2,'saturated':True,'droppedThreads':1}[k]
            with self.subTest(k=k),self.assertRaises(ContractError): check(p)
    def test_key_site_and_phase_completeness(self):
        for k,v in [('metric','mystery'),('amount',0),('phase',2),('thread',0),('generation',2),('domain',2),('context','0x55'),('site',''),('index',4)]:
            p=fixture(True);p['events'][0][k]=v
            with self.subTest(k=k),self.assertRaises(ContractError):check(p)
    def test_counter_reset_and_missing_are_rejected(self):
        p=fixture();p['samples'][-1]['counters']['admissionCacheHits']=9999
        with self.assertRaises(ContractError):check(p)
        del p['samples'][-1]['counters']['admissionCacheHits']
        with self.assertRaises(ContractError):check(p)
    def test_retained_per_allocation_baseline_guard(self):
        p=fixture()
        for s in p['samples'][3:]:s['counters']['baselineStateChecks']=9999
        with self.assertRaises(ContractError):check(p)
    def test_layout_workspace_inside_loop_rejected(self):
        for k in ('fieldWorkspaceBuilds','interfaceWorkspaceBuilds','layoutCheckCalls'):
            p=fixture()
            for s in p['samples'][3:]:s['counters'][k]=1
            with self.subTest(k=k),self.assertRaises(ContractError):check(p)
    def test_wrong_measured_class(self):
        p=fixture();p['target']['assembly']='NotMethods'
        with self.assertRaises(ContractError):check(p)
    def test_other_thread_outside_loop_remains_visible(self):
        p=fixture(True)
        for e in p['events']:e['thread']=2
        self.assertTrue(all(e['thread']==2 for e in check(p)['broadColdEvents']))
    def test_numeric_booleans_rejected(self):
        for where,k in [('root','schemaVersion'),('root','eventCapacity'),('event','generation'),('event','domain'),('event','amount'),('sample','droppedThreads')]:
            p=fixture(True);o=p if where=='root' else p['events'][0] if where=='event' else p['samples'][0];o[k]=True
            with self.subTest(where=where,k=k),self.assertRaises(ContractError):check(p)
    def test_no_missing_event_fields(self):
        for k in fixture(True)['events'][0]:
            p=fixture(True);del p['events'][0][k]
            with self.subTest(k=k),self.assertRaises(ContractError):check(p)
    def test_capacity_exhaustion_cannot_pass(self):
        p=fixture(True);p['eventCapacity']=129
        with self.assertRaises(ContractError):check(p)
    def test_historical_raw_without_new_probe_cannot_pass(self):
        with self.assertRaises(ContractError):verify_warm('{}',{}, {}, 'Methods')


class PrimitiveContracts(unittest.TestCase):
    def test_positive_metadata_only_private_tail(self): self.assertTrue(verify_primitive_layout(json.dumps(layout()))['physicalProof'])
    def test_no_initializers_or_partial_metadata(self):
        for k in ('sourcePending','targetPending','baselineInitialized','baselineVtable','targetInitialized','targetVtable','baselineInitializedAtRead','baselineVtableAtRead','truncated'):
            p=layout();p['layouts'][0][k]=True
            with self.subTest(k=k),self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_no_cctor_or_error(self):
        for k in ('baselineCctor','targetCctor','baselineCctorAtRead','error'):
            p=layout();p['layouts'][0][k]=1
            with self.subTest(k=k),self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_readiness_and_proof_are_mandatory(self):
        for k in ('fieldsChanged','baselineReady','targetReady','targetDefinitionReady','physicalProof'):
            p=layout();p['layouts'][0][k]=False
            with self.subTest(k=k),self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_no_invented_or_removed_field(self):
        for k,v in [('sourceFieldCount',0),('targetFieldCount',3),('targetStorage',[4,0]),('targetAttrs',[1,6]),('targetOffsets',[16,16]),('targetSize',24)]:
            p=layout();p['layouts'][0][k]=v
            with self.subTest(k=k),self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_duplicate_physical_witness(self):
        p=layout();p['layouts']*=2
        with self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_existing_field_may_not_move(self):
        p=layout();p['layouts'][0]['targetOffsets'][0]=20
        with self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_distinct_physical_classes(self):
        p=layout();p['layouts'][0]['target']=copy.deepcopy(p['layouts'][0]['baseline'])
        with self.assertRaises(ContractError):verify_primitive_layout(json.dumps(p))
    def test_missing_field_rejected(self):
        for k in layout()['layouts'][0]:
            p=layout();del p['layouts'][0][k]
            with self.subTest(k=k),self.assertRaises((ContractError,KeyError)):verify_primitive_layout(json.dumps(p))

if __name__=='__main__':unittest.main()
