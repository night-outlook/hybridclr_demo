"""Synthetic negative-observation contracts. Never relabel prior Player evidence."""
import copy
import json
from pathlib import Path
import unittest
from batch_contract import ContractError, loads
from runtime_contract import LAYOUT


def attach_rejection_observation(raw, request):
    from test_runtime_contract import layout
    p = layout()
    p.update(used=False, sealed=False, generation=0, ownerThread=0, samples=[], events=[],
             target=dict(physical='0x0', assembly='', namespace='', name='', typeKey=''))
    p['producerFence'].update(requested=False, acquired=False, released=False, drained=False,
                              ownerOsThread=0, elapsedMicros=0, leaseMs=0)
    d = loads(raw['diagnostics'])
    d.update(state='Failed', generation=0, expected=1, staged=1, retainedBytes=20, closureLoadOrder=['Methods'],
             stableAotNames=[], commitOrder=[], assemblies=[dict(published=False, moduleInitializerAttempted=False, moduleInitializerRan=False)],
             events=[], baselineUses=[])
    raw['diagnostics'] = json.dumps(d)
    raw['runtimeProbe'] = json.dumps(p)
    state = dict(stateCode=8, diagnosticsCode=0, diagnostics=raw['diagnostics'], recoveryCode=0, recovery=raw['recovery'])
    raw['rejectionProbe'] = dict(schemaVersion=1, policy='R03RejectedProbeNonMutationV1', smallCapacity=16, smallReturn=-2,
                                 firstReturn=len(raw['runtimeProbe'].encode()), secondReturn=len(raw['runtimeProbe'].encode()),
                                 repeatedProbe=raw['runtimeProbe'], **{k: copy.deepcopy(state) for k in ('before','afterSmall','afterFirst','afterSecond')})


def sample():
    from test_batch_contract import sample as make
    v = make('admission-reject'); v[1]['rejectionProbe'] = loads(v[1]['rejectionProbe']); return v


def check(v):
    from test_batch_contract import check as run
    v = copy.deepcopy(v)
    v[1]['rejectionProbe'] = json.dumps(v[1]['rejectionProbe'])
    return run(v)


def alter_probe(v, update, repeated=False):
    text = v[1]['rejectionProbe']['repeatedProbe'] if repeated else v[1]['runtimeProbe']
    p = loads(text); update(p); text = json.dumps(p)
    if repeated:
        v[1]['rejectionProbe']['repeatedProbe'] = text; v[1]['rejectionProbe']['secondReturn'] = len(text.encode())
    else:
        v[1]['runtimeProbe'] = text; v[1]['rejectionProbe']['firstReturn'] = len(text.encode())


class RejectedObservationContracts(unittest.TestCase):
    def test_safe_observation(self):
        self.assertTrue(check(sample())['rejectionObservation']['terminalUnchanged'])
    def test_requires_original_pre_probe_error(self):
        v=sample();d=loads(v[1]['rejectionProbe']['before']['diagnostics']);d['lastError']=15
        v[1]['rejectionProbe']['before']['diagnostics']=json.dumps(d)
        with self.assertRaises(ContractError):check(v)
    def test_rejects_error_mutation_at_every_boundary(self):
        for where in ('afterSmall','afterFirst','afterSecond'):
            v=sample();d=loads(v[1]['rejectionProbe'][where]['diagnostics']);d['lastError']=15
            v[1]['rejectionProbe'][where]['diagnostics']=json.dumps(d)
            with self.subTest(where=where),self.assertRaises(ContractError):check(v)
    def test_recovery_mutation(self):
        v=sample();r=loads(v[1]['rejectionProbe']['afterFirst']['recovery']);r['terminalFailureCode']=15
        v[1]['rejectionProbe']['afterFirst']['recovery']=json.dumps(r)
        with self.assertRaises(ContractError):check(v)
    def test_detail_mutation_with_same_error_is_rejected(self):
        v=sample();d=loads(v[1]['rejectionProbe']['afterFirst']['diagnostics']);d['detail']+='changed'
        v[1]['rejectionProbe']['afterFirst']['diagnostics']=json.dumps(d)
        with self.assertRaisesRegex(ContractError,'mutated'):check(v)
    def test_transaction_events_must_not_change(self):
        v=sample();d=loads(v[1]['rejectionProbe']['afterFirst']['diagnostics']);d['events']=[{'unexpected':True}]
        v[1]['rejectionProbe']['afterFirst']['diagnostics']=json.dumps(d)
        with self.assertRaisesRegex(ContractError,'mutated'):check(v)
    def test_final_diagnostics_are_bound(self):
        v=sample();d=loads(v[1]['diagnostics']);d['detail']+='late change';v[1]['diagnostics']=json.dumps(d)
        with self.assertRaisesRegex(ContractError,'mutated'):check(v)
    def test_capacity_control_is_not_probe_failure(self):
        for value in (-3,-1,0,16,False):
            v=sample();v[1]['rejectionProbe']['smallReturn']=value
            with self.subTest(value=value),self.assertRaises(ContractError):check(v)
    def test_full_return_codes_are_byte_bound(self):
        for key in ('firstReturn','secondReturn'):
            for value in (-3,0,1,131072,True):
                v=sample();v[1]['rejectionProbe'][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ContractError):check(v)
    def test_missing_or_extra_fields(self):
        for field in sample()[1]['rejectionProbe']:
            v=sample();del v[1]['rejectionProbe'][field]
            with self.subTest(field=field),self.assertRaises(ContractError):check(v)
    def test_cannot_omit_retained_rows(self):
        v=sample();alter_probe(v,lambda p:p.update(layouts=[]))
        with self.assertRaisesRegex(ContractError,'omitted'):check(v)
    def test_incomplete_or_truncated_identity(self):
        for field in ('baselineIdentityStatus','targetIdentityStatus'):
            for state in ('NotCaptured','TooLong','MissingInput','CaptureFailed'):
                v=sample();alter_probe(v,lambda p:p['layouts'][0].update({field:state}))
                with self.subTest(field=field,state=state),self.assertRaises(ContractError):check(v)
    def test_repeated_identity_must_not_change(self):
        v=sample();alter_probe(v,lambda p:p['layouts'][0]['target'].update(typeKey='other'),True)
        with self.assertRaisesRegex(ContractError,'Immutable'):check(v)
    def test_probe_overflow_or_activity_rejected(self):
        for field,value in (('overflow',True),('invalid',True),('available',False),('used',True),('generation',1)):
            v=sample();alter_probe(v,lambda p:p.update({field:value}))
            with self.subTest(field=field),self.assertRaises(ContractError):check(v)
    def test_rejected_probe_cannot_publish_or_run_initializer(self):
        for field in ('published','moduleInitializerAttempted','moduleInitializerRan'):
            v=sample();d=loads(v[1]['rejectionProbe']['before']['diagnostics']);d['assemblies'][0][field]=True
            v[1]['rejectionProbe']['before']['diagnostics']=json.dumps(d)
            with self.subTest(field=field),self.assertRaises(ContractError):check(v)
    def test_no_terminal_restore_waiver(self):
        v=sample();v[1]['exception']='RuntimeProbeFailure: -3, but restored 16'
        with self.assertRaises(ContractError):check(v)
    def test_old_raw_schema_is_not_reused(self):
        v=sample();v[1]['schemaVersion']=2
        with self.assertRaises(ContractError):check(v)
    def test_old_probe_schema_is_not_upgraded(self):
        v=sample();alter_probe(v,lambda p:p.update(schemaVersion=2))
        with self.assertRaises(ContractError):check(v)
    def test_diagnostic_enumeration_is_retained_not_misclassified(self):
        v=sample();d=loads(v[1]['rejectionProbe']['afterFirst']['diagnostics']);d['ordinaryClasses']=[{'harness':'new'}]
        v[1]['rejectionProbe']['afterFirst']['diagnostics']=json.dumps(d)
        self.assertTrue(check(v)['rejectionObservation']['terminalUnchanged'])
    def test_layout_renderer_does_not_format_private_handles(self):
        s=(Path(__file__).parent/'PlayerProject/AssemblyShadowR03Probe.cpp').read_text()
        block=s[s.index('for (size_t i = 0; i < r.layouts;'):s.index('producerFence',s.index('for (size_t i = 0; i < r.layouts;'))]
        self.assertNotIn('ProbeType(',block)
        self.assertNotIn('AssemblyShadowTypeKey',block)
        self.assertIn('l.baselineIdentity.WriteJson(out)',block)
        self.assertIn('l.targetIdentity.WriteJson(out)',block)

if __name__ == '__main__': unittest.main()
