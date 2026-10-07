"""Startup regression checks; synthetic receipts are not Player evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m07_results
TOOLS = Path(m07_results.__file__).resolve().parent
CANDIDATES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS/'tests'))
sys.path.insert(0, str(CANDIDATES))


def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,CANDIDATES/filename)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


import r01_early_results as early
lazy=load('r01b_lazy_candidate','run-r01b-lazy-player.py')
old=load('r01b_old_candidate','run-r01b-old-player-rejection.py')
from test_r01_early_results import make_capsule,emit_receipt
from shadow_tools import VerificationError
import r01_early_capsule as capsule


def as_profile2(receipt, data):
    """Independent wire projection of profile2 charges for the legacy scenarios."""
    value=copy.deepcopy(receipt); pages=mapped=0
    for snapshot in value['snapshots']:
        legacy=json.loads(snapshot['capacityJson']);phase=snapshot['phase'];sizes=snapshot['orderedSizes']
        o=legacy['ordinaryAllocatedCount'];s=legacy['shadowAllocatedCount'];r=legacy['reservedImageCount']
        if phase=='after-reserve':pages+=len(sizes)
        elif phase in ('after-ordinary-before-configure','after-ordinary-after-reserve'):pages+=3;mapped+=2
        elif phase=='after-stage':mapped+=len(sizes)
        elif phase=='after-validate' and data['mode'] not in early.GUARD_MODES:pages+=len(sizes)*3;mapped+=len(sizes)
        elif phase=='after-commit':mapped+=1
        oversized=data['mode']=='Oversize'
        capacity=dict(schemaVersion=2,enabled=True,profileVersion=2,maximumImageCount=8192,maximumDllBytes=33554432,
            usablePageCapacity=524287,chargedPageCeiling=393215,minimumFreePageMargin=131072,
            reservedPages=pages,mappedPages=mapped,lifetimeReservedImageCount=o+r,remainingImageCount=8192-o-r,
            requiredImages=len(sizes),acceptedImages=0 if oversized else len(sizes),
            firstFailingIndex=len(sizes)-1 if oversized else -1,firstFailingSize=sizes[-1] if oversized else 0,
            failureReason='DllTooLarge' if oversized else 'None',fitsPreliminary=not oversized,
            runtimeFinalizationRequired=True,aggregateInputDllBytes=sum(sizes),aggregateInputDllBytesInformational=True,
            ordinaryAllocatedCount=o,shadowAllocatedCount=s,reservedShadowImageCount=r)
        snapshot['capacityJson']=json.dumps(capacity)
        d=json.loads(snapshot['diagnosticsJson']);d.update(runtimeAbiVersion=2,metadataBudgetCapabilityVersion=2)
        snapshot['diagnosticsJson']=json.dumps(d)
    for observer in value['observerSamples']+[row['diagnostics'] for row in value['initializerEvents']]:
        d=json.loads(observer['rawJson']);d.update(runtimeAbiVersion=2,metadataBudgetCapabilityVersion=2);observer['rawJson']=json.dumps(d)
    return value


class Profile2TimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.cap=self.root/'startup.capsule';self.result=self.root/'early.json'
    def fixture(self,mode):
        data=make_capsule(self.root,mode);capsule.write_capsule(self.cap,data)
        return data,as_profile2(emit_receipt(data,self.cap,self.result),data)
    def verify(self,value,mode):
        self.result.write_text(json.dumps(value));return early.verify_early_receipt(self.result,self.cap,mode,1234,profile=2)
    def test_profile2_baseline_has_no_operations_or_allocations(self):
        data,value=self.fixture('Baseline');self.verify(value,'Baseline')
        self.assertEqual(value['operations'],[])
    def test_profile2_all_transaction_modes_keep_exact_state_and_lifetime_evidence(self):
        for mode in ('Control','OrdinaryFirst','OrdinaryAfterReserve','Mismatch','Type','Object','Cctor','NativeScript','MetadataFailure','InitializerFailure','Oversize'):
            self.cap.unlink(missing_ok=True)
            data,value=self.fixture(mode)
            with self.subTest(mode=mode):self.verify(value,mode)
    def test_profile2_rejects_hidden_reservation_or_rollback(self):
        _,value=self.fixture('Control')
        for phase,key,number in [('before-startup-ops','lifetimeReservedImageCount',1),('after-reserve','reservedShadowImageCount',4),
                                 ('after-stage','shadowAllocatedCount',4),('after-commit','lifetimeReservedImageCount',6)]:
            bad=copy.deepcopy(value);row=next(s for s in bad['snapshots'] if s['phase']==phase)
            c=json.loads(row['capacityJson']);c[key]=number;row['capacityJson']=json.dumps(c)
            with self.subTest(phase=phase,key=key),self.assertRaises(VerificationError):self.verify(bad,'Control')
    def test_profile2_rejects_credit_mapping_and_sealed_footprint_violations(self):
        _,value=self.fixture('Control')
        for phase,key,number in [('after-reserve','reservedPages',6),('after-reserve','mappedPages',1),
                                 ('after-stage','mappedPages',10),('after-validate','reservedPages',393216),
                                 ('after-commit','reservedPages',21)]:
            bad=copy.deepcopy(value);row=next(s for s in bad['snapshots'] if s['phase']==phase)
            c=json.loads(row['capacityJson']);c[key]=number;row['capacityJson']=json.dumps(c)
            with self.subTest(phase=phase,key=key),self.assertRaises(VerificationError):self.verify(bad,'Control')
    def test_profile2_abort_retains_both_image_and_page_ledger(self):
        _,value=self.fixture('Type');row=value['snapshots'][-1];c=json.loads(row['capacityJson']);c['reservedPages']=0;row['capacityJson']=json.dumps(c)
        with self.assertRaises(VerificationError):self.verify(value,'Type')
    def test_reserve_does_not_consume_shadow_images_and_mismatch_retains_reservation(self):
        data,value=self.fixture('Mismatch');self.verify(value,'Mismatch')
        for phase in ('after-reserve','after-mismatch','after-abort'):
            row=next(s for s in value['snapshots'] if s['phase']==phase);c=json.loads(row['capacityJson'])
            self.assertEqual(c['reservedShadowImageCount'],len(data['inputs']))
            self.assertEqual(c['shadowAllocatedCount'],0)
            bad=copy.deepcopy(value);target=next(s for s in bad['snapshots'] if s['phase']==phase)
            c['shadowAllocatedCount']=1;target['capacityJson']=json.dumps(c)
            with self.subTest(phase=phase),self.assertRaises(VerificationError):self.verify(bad,'Mismatch')
    def test_metadata_failure_consumes_full_staged_closure_and_never_rolls_back(self):
        data,value=self.fixture('MetadataFailure');self.verify(value,'MetadataFailure')
        reserve=json.loads(next(s for s in value['snapshots'] if s['phase']=='after-reserve')['capacityJson'])
        self.assertEqual(reserve['shadowAllocatedCount'],0)
        for phase in ('after-stage','after-validate','after-rejected-operations'):
            row=next(s for s in value['snapshots'] if s['phase']==phase);c=json.loads(row['capacityJson'])
            self.assertEqual(c['shadowAllocatedCount'],len(data['inputs']))
            self.assertEqual(c['reservedShadowImageCount'],len(data['inputs']))
            bad=copy.deepcopy(value);target=next(s for s in bad['snapshots'] if s['phase']==phase)
            c['shadowAllocatedCount']-=1;target['capacityJson']=json.dumps(c)
            with self.subTest(phase=phase),self.assertRaises(VerificationError):self.verify(bad,'MetadataFailure')
    def test_profile1_stays_strict_and_does_not_accept_profile2_fields(self):
        data,value=self.fixture('Baseline');self.result.write_text(json.dumps(value))
        with self.assertRaises(VerificationError):early.verify_early_receipt(self.result,self.cap,'Baseline',1234,profile=1)
        legacy=emit_receipt(data,self.cap,self.result);self.result.write_text(json.dumps(legacy))
        early.verify_early_receipt(self.result,self.cap,'Baseline',1234,profile=1)


class BaselineLauncherTests(unittest.TestCase):
    setUp = Profile2TimelineTests.setUp
    def test_lazy_and_old_capsules_bind_correct_context_and_profile(self):
        data=make_capsule(self.root,'Baseline');capsule.write_capsule(self.cap,data)
        for module,profile in ((lazy,2),(old,1)):
            emitted=emit_receipt(data,self.cap,self.result)
            if profile==2:emitted=as_profile2(emitted,data)
            self.result.write_text(json.dumps(emitted))
            context={'identity':'current' if profile==2 else 'historical'}
            with patch.object(module,'expected_baseline_capsule',return_value=data) as admitted:
                module.verify_baseline_startup(context,self.root/'fixtures.json',self.cap,self.result,1234,profile)
                admitted.assert_called_once_with(context,self.root/'fixtures.json',profile)
                with self.assertRaises(VerificationError):module.verify_baseline_startup(context,self.root/'fixtures.json',self.cap,self.result,9999,profile)
    def test_valid_capsule_hash_does_not_admit_wrong_fixture_or_control_mode(self):
        data=make_capsule(self.root,'Baseline');capsule.write_capsule(self.cap,data)
        emitted=as_profile2(emit_receipt(data,self.cap,self.result),data);self.result.write_text(json.dumps(emitted))
        for key,val in [('mode','Control'),('runtimeAbiHash','b'*64),('baselineBuildId','foreign')]:
            expected=copy.deepcopy(data);expected[key]=val
            with patch.object(lazy,'expected_baseline_capsule',return_value=expected),self.subTest(key=key),self.assertRaises(VerificationError):
                lazy.verify_baseline_startup({},self.root/'fixture.json',self.cap,self.result,1234,2)
    def test_startup_arguments_bind_capsule_and_result_paths(self):
        data=make_capsule(self.root,'Baseline');capsule.write_capsule(self.cap,data)
        for module in (lazy,old):
            self.assertEqual(module.baseline_startup_arguments(self.cap,self.result),['-shadowEarlyCapsule',str(self.cap),
                '-shadowEarlyCapsuleSha256',capsule.digest(self.cap),'-shadowEarlyResult',str(self.result)])
            expected={Path(row['path']) for row in data['prerequisiteFiles']}
            expected.update(Path(row[k]) for row in data['inputs'] for k in ('dllPath','pdbPath') if row[k])
            self.assertEqual(module.baseline_capsule_inputs(data),expected)


if __name__=='__main__':unittest.main()
