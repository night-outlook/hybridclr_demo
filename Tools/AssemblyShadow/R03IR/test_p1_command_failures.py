#!/usr/bin/env python3
"""P1 failure handling: real Python children; Git/SDK/VM children explicitly mocked."""
from __future__ import annotations
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).with_name('run_p1_metadata_local_preflight.py')

def load():
    spec=importlib.util.spec_from_file_location('p1_preflight_failure_under_test',SOURCE)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

class ComponentFailureReceipts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.mod=load()

    def execute(self,effect=None,completed=None):
        with patch.object(self.mod,'run',side_effect=effect,return_value=completed):
            result=self.mod.execute_component(self.root,'test',['mock-command'],'Passed')
        self.assertEqual(result,json.loads((self.root/'commands/test.json').read_bytes()))
        for stream in ('stdout','stderr'):
            raw=(self.root/'commands/test'/(stream+'.bin')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),result[stream+'.binSha256'])
        return result

    def write_result(self,raw=b'{"result":"Passed"}'):
        component=self.root/'test';component.mkdir()
        (component/'RESULT.json').write_bytes(raw)
        return component

    def test_real_outer_timeout_keeps_exact_prefix(self):
        cmd=[sys.executable,'-B','-c',"import os,time;os.write(1,b'outer-out');os.write(2,b'outer-err');time.sleep(30)"]
        record=self.mod.execute_component(self.root,'test',cmd,'Passed',timeout=0.8)
        self.assertEqual(record['status'],'Failed')
        self.assertEqual(record['stopBatchReason'],'OuterCommandTimeout')
        self.assertTrue(record['commandLifetimeUnverified'])
        self.assertIsNone(record['exit'])
        self.assertEqual(record['outputCompleteness'],'CapturedPrefix')
        self.assertEqual((self.root/'commands/test/stdout.bin').read_bytes(),b'outer-out')
        self.assertEqual((self.root/'commands/test/stderr.bin').read_bytes(),b'outer-err')

    def test_timeout_missing_capture_remains_unavailable(self):
        record=self.execute(effect=subprocess.TimeoutExpired(['mock'],1))
        self.assertFalse(record['stdoutAvailable']);self.assertFalse(record['stderrAvailable'])
        self.assertEqual(record['outputCompleteness'],'CapturedPrefix')
        self.assertEqual(record['status'],'Failed')

    def test_interruption_is_retained_for_batch_stop(self):
        record=self.execute(effect=KeyboardInterrupt)
        self.assertTrue(record['interrupted'])
        self.assertEqual(record['stopBatchReason'],'OuterCommandInterrupted')
        self.assertEqual(record['outputCompleteness'],'Unavailable')

    def test_real_missing_command_keeps_failed_receipt(self):
        record=self.mod.execute_component(self.root,'test',[str(self.root/'missing')],'Passed')
        self.assertEqual(record['status'],'Failed');self.assertIsNone(record['exit'])
        self.assertIn('FileNotFoundError',record['exception'])
        self.assertFalse(record['stdoutAvailable'])

    def test_unknown_command_exception_stops(self):
        record=self.execute(effect=RuntimeError('unknown execution state'))
        self.assertEqual(record['stopBatchReason'],'UnknownCommandExecutionOutcome')

    def test_normal_nonzero_is_not_promoted_or_mislabeled_timeout(self):
        self.write_result()
        record=self.execute(completed=subprocess.CompletedProcess(['mock'],9,b'out',b'err'))
        self.assertEqual(record['status'],'Failed');self.assertEqual(record['exit'],9)
        self.assertFalse(record['timedOut']);self.assertIsNone(record['stopBatchReason'])
        self.assertEqual(record['outputCompleteness'],'CompleteDirectChildStreams')

    def test_child_lifetime_marker_overrides_passed_verdict(self):
        self.write_result(b'{"result":"Passed","commandLifetimeUnverified":true}')
        record=self.execute(completed=subprocess.CompletedProcess(['mock'],0,b'out',b''))
        self.assertEqual(record['status'],'Failed')
        self.assertEqual(record['stopBatchReason'],'ChildReportedUnverifiedCommandLifetime')

    def test_invalid_json_cannot_become_pass(self):
        self.write_result(b'{"result":"Passed",')
        record=self.execute(completed=subprocess.CompletedProcess(['mock'],0,b'out',b'err'))
        self.assertEqual(record['status'],'Failed');self.assertIn('exception',record)
        self.assertIsNone(record['stopBatchReason'])

    def test_duplicate_keys_rejected(self):
        component=self.write_result(b'{"result":"Failed","result":"Passed"}')
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            self.mod.read_component_result(component,'RESULT.json')

    def test_nonfinite_and_nonobject_records_rejected(self):
        component=self.write_result()
        for raw in (b'[]',b'null',b'{"result":NaN}',b'{"result":"Passed","commandLifetimeUnverified":1}'):
            with self.subTest(raw=raw):
                (component/'RESULT.json').write_bytes(raw)
                with self.assertRaises(ValueError):self.mod.read_component_result(component,'RESULT.json')

    def test_result_file_symlink_is_rejected(self):
        component=self.write_result();file=component/'RESULT.json';target=self.root/'outside.json'
        file.replace(target);file.symlink_to(target)
        with self.assertRaises(ValueError):self.mod.read_component_result(component,'RESULT.json')

    def test_parent_symlink_is_rejected(self):
        component=self.write_result();target=self.root/'elsewhere';component.rename(target)
        component.symlink_to(target,target_is_directory=True)
        with self.assertRaises(ValueError):self.mod.read_component_result(component,'RESULT.json')

    def test_receipt_hash_matches_exact_parsed_bytes(self):
        raw=b' {"result": "Passed"}\n';component=self.write_result(raw)
        result=self.mod.read_component_result(component,'RESULT.json')
        self.assertEqual(result['innerResultSha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['innerResult'],'Passed')

    def test_managed_binding_remains_nested_and_hash_authenticated(self):
        component=self.root/'managed-sdk';nested=component/'build-api';nested.mkdir(parents=True)
        source=nested/'results.json'
        record={'kind':'R03CompleteBuildHelperCompile','schemaVersion':1,
                'unityVersion':'2022.3.62f2','result':'Passed','unityEditorRun':False,
                'nativeExecution':False,'runtimeAcceptance':False}
        source.write_text(json.dumps(record))
        stdout=json.dumps({'result':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}).encode()
        consumed=self.mod.read_managed_result(component,stdout)
        self.assertTrue(consumed['returnedBindingVerified'])
        source.write_bytes(source.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'SHA-256'):self.mod.read_managed_result(component,stdout)

class OwnedBindingInventoryContract(unittest.TestCase):
    def verify_exact_host_binding_inventory_and_fail_closed_mutations(self):
        mod=load();expected=mod.EXPECTED_OWNED_BINDING_GROUPS
        self.assertEqual(len(expected),28)
        self.assertEqual(len(set(expected)),28)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();result=out/'RESULT.json'
            baseline=dict(kind='R03P1InactiveOwnedObservedPhysicalNamesSourceHost',
                schemaVersion=1,result='PassedWithinInactiveOwnedPhysicalNamesHostScope',
                commandLifetimeUnverified=False,actualSourceCompiled=True,
                sourcePreserved=True,ownedPhysicalNamesOnly=True,
                completeExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                metadataPointerLifetimeProven=False,coherentVmEpochProven=False,
                officialUnitySdkCompiled=False,UnityPlayerExecuted=False,
                runtimeAcceptance=False,
                profiles={profile:{'result':'PassedWithinExplicitVmMocks',
                      'caseGroups':list(expected)} for profile in ('strict','sanitized')})
            def check(data):
                result.write_text(json.dumps(data))
                return mod.read_component_result(out,'RESULT.json',True,expected)
            self.assertTrue(check(baseline)['ownedBindingCaseInventoryVerified'])
            for mutate in ('missing-case','duplicate-case','wrong-result','false-runtime-scope',
                           'missing-source-compile','missing-sanitized','wrong-kind','bool-schema'):
                with self.subTest(mutate=mutate):
                    variant=json.loads(json.dumps(baseline))
                    if mutate=='missing-case':variant['profiles']['strict']['caseGroups'].pop()
                    elif mutate=='duplicate-case':variant['profiles']['strict']['caseGroups'][-1]=variant['profiles']['strict']['caseGroups'][0]
                    elif mutate=='wrong-result':variant['profiles']['sanitized']['result']='Failed'
                    elif mutate=='false-runtime-scope':variant['runtimeAcceptance']=True
                    elif mutate=='missing-source-compile':variant.pop('actualSourceCompiled')
                    elif mutate=='missing-sanitized':variant['profiles'].pop('sanitized')
                    elif mutate=='wrong-kind':variant['kind']='Unrelated'
                    elif mutate=='bool-schema':variant['schemaVersion']=True
                    with self.assertRaisesRegex(ValueError,'Owned binding'):check(variant)
            unverified=json.loads(json.dumps(baseline))
            unverified['commandLifetimeUnverified']=True
            self.assertFalse(check(unverified)['ownedBindingCaseInventoryVerified'])


    def verify_noncanonical_json_receipt_and_fail_closed_mutations(self):
        mod=load();expected=mod.EXPECTED_OWNED_JSON_GROUPS
        self.assertEqual(len(expected),21)
        self.assertEqual(len(set(expected)),21)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();result=out/'RESULT.json'
            baseline=dict(kind='R03P1OwnedPhysicalNamesJsonActualSourceHost',
                schemaVersion=1,result='PassedWithinOwnedPhysicalNamesJsonHostScope',
                commandLifetimeUnverified=False,actualSourceCompiled=True,
                sourcePreserved=True,ownedJsonSchema='R03P1ObservedPhysicalDisplayNames',
                rowScope='OwnedSnapshotLocalDisplayNamesOnly',
                canonicalExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                coherentVmEpochProven=False,officialUnitySdkCompiled=False,
                UnityPlayerExecuted=False,runtimeAcceptance=False,
                sourceContract=dict(actualFixtureCaseIds=list(expected),
                                    noVmMetadataOrFileOperations=True,
                                    nonCanonicalScopeOnly=True),
                profiles={label:{'result':'PassedWithinOwnedNonCanonicalJsonHostScope',
                       'caseGroups':list(expected)} for label in ('strict','sanitized')})
            def check(value):
                result.write_text(json.dumps(value))
                return mod.read_component_result(out,'RESULT.json',True,
                                                 expected_owned_json_groups=expected)
            self.assertTrue(check(baseline)['ownedPhysicalJsonCaseInventoryVerified'])
            for mutate in ('missing-case','duplicate-case','wrong-result',
                           'source-compiled-false','bool-schema','missing-sanitized',
                           'fake-VM-epoch','wrong-source-schema','incomplete-contract'):
                with self.subTest(mutate=mutate):
                    variant=json.loads(json.dumps(baseline))
                    if mutate=='missing-case':variant['profiles']['strict']['caseGroups'].pop()
                    elif mutate=='duplicate-case':variant['profiles']['strict']['caseGroups'][-1]=variant['profiles']['strict']['caseGroups'][0]
                    elif mutate=='wrong-result':variant['profiles']['sanitized']['result']='Failed'
                    elif mutate=='source-compiled-false':variant['actualSourceCompiled']=False
                    elif mutate=='bool-schema':variant['schemaVersion']=True
                    elif mutate=='missing-sanitized':variant['profiles'].pop('sanitized')
                    elif mutate=='fake-VM-epoch':variant['coherentVmEpochProven']=True
                    elif mutate=='wrong-source-schema':variant['ownedJsonSchema']='Other'
                    elif mutate=='incomplete-contract':variant['sourceContract']['actualFixtureCaseIds']=[]
                    with self.assertRaisesRegex(ValueError,'Owned physical JSON'):check(variant)
            unverified=json.loads(json.dumps(baseline))
            unverified['commandLifetimeUnverified']=True
            self.assertFalse(check(unverified)['ownedPhysicalJsonCaseInventoryVerified'])


    def verify_live_owned_json_receipt_and_fail_closed_mutations(self):
        mod=load(); expected=mod.EXPECTED_LIVE_OWNED_JSON_GROUPS
        self.assertEqual(len(expected),12)
        self.assertEqual(len(set(expected)),12)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve(); path=out/'RESULT.json'
            baseline=dict(kind='R03P1InactiveLiveOwnedPhysicalJsonSourceHost',
                schemaVersion=1,result='PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope',
                actualSourceCompiled=True,sourcePreserved=True,
                commandLifetimeUnverified=False,sourceToJsonIntegrationTestedWithMocks=True,
                canonicalExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                metadataPointerLifetimeProven=False,coherentVmEpochProven=False,
                officialUnitySdkCompiled=False,UnityPlayerExecuted=False,runtimeAcceptance=False,
                sourceContract=dict(originalNativeCppAndApiFingerprintPreserved=True,
                    productionSourceMethodsCompiled=2,
                    bridgeDoesNotReadAdditionalVmPointers=True,
                    sourcePassBeforePureOwnedSerialization=True,
                    caseGroups=list(expected),canonicalExecutionTypeKeys=False,
                    runtimeAcceptance=False),
                profiles={mode:{'result':'PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope',
                    'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                    'liveIntegrationGroups':list(expected)}
                    for mode in ('strict','sanitized')})
            def check(record):
                path.write_text(json.dumps(record))
                return mod.read_component_result(out,'RESULT.json',True,
                    expected_live_owned_json_groups=expected)
            self.assertTrue(check(baseline)['liveOwnedPhysicalJsonCaseInventoryVerified'])
            for mutate in ('missing-case','duplicate-case','wrong-profile',
                           'wrong-compiled','wrong-contract','forgot-original-names',
                           'false-pointer-claim','bool-schema','wrong-kind',
                           'missing-sanitized'):
                with self.subTest(mutate=mutate):
                    data=json.loads(json.dumps(baseline))
                    if mutate=='missing-case':data['profiles']['strict']['liveIntegrationGroups'].pop()
                    elif mutate=='duplicate-case':data['profiles']['strict']['liveIntegrationGroups'][-1]=data['profiles']['strict']['liveIntegrationGroups'][0]
                    elif mutate=='wrong-profile':data['profiles']['sanitized']['result']='Failed'
                    elif mutate=='wrong-compiled':data['actualSourceCompiled']=False
                    elif mutate=='wrong-contract':data['sourceContract']['sourcePassBeforePureOwnedSerialization']=False
                    elif mutate=='forgot-original-names':data['profiles']['strict']['originalNameGroups']=[]
                    elif mutate=='false-pointer-claim':data['physicalClassPointerOriginProven']=True
                    elif mutate=='bool-schema':data['schemaVersion']=True
                    elif mutate=='wrong-kind':data['kind']='Unrelated'
                    elif mutate=='missing-sanitized':data['profiles'].pop('sanitized')
                    with self.assertRaisesRegex(ValueError,'Inactive live physical JSON'):
                        check(data)
            data=json.loads(json.dumps(baseline))
            data['commandLifetimeUnverified']=True
            self.assertFalse(check(data)['liveOwnedPhysicalJsonCaseInventoryVerified'])


    def verify_observed_type_shape_receipt_and_failure_mutations(self):
        mod=load();expected=mod.EXPECTED_TYPE_SHAPE_GROUPS
        self.assertEqual(len(expected),15)
        self.assertEqual(len(set(expected)),15)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();file=out/'RESULT.json'
            baseline=dict(kind='R03P1ObservedTypeShapeActualVmSourceHost',
                schemaVersion=1,result='PassedWithinObservedTypeShapeSourceHostScope',
                commandLifetimeUnverified=False,actualSourceCompiled=True,
                sourcePreserved=True,typeShapeCategoriesOnly=True,
                completeExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                coherentVmEpochProven=False,officialUnitySdkCompiled=False,
                UnityPlayerExecuted=False,runtimeAcceptance=False,
                sourceContract=dict(typedFieldsCopiedOnlyFromMatchedCallback=True,
                     exactPinnedIl2CppClassAbiSourceInspected=True,
                     originalCppApiFingerprintVerified=True,
                     noMetadataPointersRetained=True,
                     candidateRowsAreOnlySimpleShapeHints=True,
                     canonicalExecutionTypeKeys=False,physicalPointerOriginProven=False,
                     globalVmEpochProven=False,playerExecution=False,
                     runtimeAcceptance=False,
                     originalNameGroups=list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                     shapeGroups=list(expected)),
                profiles={label:{'result':'PassedWithinObservedTypeShapeSourceHostScope',
                     'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                     'shapeGroups':list(expected)}
                     for label in ('strict','sanitized')})
            def check(record):
                file.write_text(json.dumps(record))
                return mod.read_component_result(out,'RESULT.json',True,
                       expected_type_shape_groups=expected)
            self.assertTrue(check(baseline)['observedTypeShapeCaseInventoryVerified'])
            for mutation in ('missing-case','duplicate-case','wrong-result',
                             'wrong-source-kind','boolean-schema','claim-typekeys',
                             'incorrect-ABI-contract','missing-match-proof',
                             'wrong-original-roster','missing-sanitized',
                             'source-not-compiled'):
                with self.subTest(mutation=mutation):
                    data=json.loads(json.dumps(baseline))
                    if mutation=='missing-case':data['profiles']['strict']['shapeGroups'].pop()
                    elif mutation=='duplicate-case':data['profiles']['strict']['shapeGroups'][-1]=data['profiles']['strict']['shapeGroups'][0]
                    elif mutation=='wrong-result':data['profiles']['sanitized']['result']='Failed'
                    elif mutation=='wrong-source-kind':data['kind']='Other'
                    elif mutation=='boolean-schema':data['schemaVersion']=True
                    elif mutation=='claim-typekeys':data['completeExecutionTypeKeys']=True
                    elif mutation=='incorrect-ABI-contract':data['sourceContract']['exactPinnedIl2CppClassAbiSourceInspected']=False
                    elif mutation=='missing-match-proof':data['sourceContract']['typedFieldsCopiedOnlyFromMatchedCallback']=False
                    elif mutation=='wrong-original-roster':data['sourceContract']['originalNameGroups']=[]
                    elif mutation=='missing-sanitized':data['profiles'].pop('sanitized')
                    elif mutation=='source-not-compiled':data['actualSourceCompiled']=False
                    with self.assertRaisesRegex(ValueError,'Observed type-shape'):check(data)
            uncertain=json.loads(json.dumps(baseline))
            uncertain['commandLifetimeUnverified']=True
            self.assertFalse(check(uncertain)['observedTypeShapeCaseInventoryVerified'])


    def verify_live_type_shape_census_receipt_and_fail_closed_mutations(self):
        mod=load();expected=mod.EXPECTED_LIVE_TYPE_SHAPE_GROUPS
        self.assertEqual(len(expected),16)
        self.assertEqual(len(set(expected)),16)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();receipt=out/'RESULT.json'
            original=dict(typedFieldsCopiedOnlyFromMatchedCallback=True,
                originalCppApiFingerprintVerified=True,
                noMetadataPointersRetained=True,
                originalNameGroups=list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                shapeGroups=list(mod.EXPECTED_TYPE_SHAPE_GROUPS))
            baseline=dict(kind='R03P1InactiveLiveObservedTypeShapeCensusHost',
                schemaVersion=1,result='PassedWithinInactiveLiveTypeShapeCensusHostScope',
                actualSourceCompiled=True,sourcePreserved=True,
                commandLifetimeUnverified=False,
                canonicalExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                coherentVmEpochProven=False,officialUnitySdkCompiled=False,
                UnityPlayerExecuted=False,runtimeAcceptance=False,
                sourceContract=dict(previousMatchedShapeSourceContractVerified=original,
                    originalNativeCppAndApiFingerprintPreserved=True,
                    actualNativeSourceMethodsCompiled=2,
                    sourceLocksReleasedBeforePureCensus=True,
                    oneShotCensusPreflightBeforeIterator=True,
                    candidateShapeOnlyNotCanonicalIdentity=True,
                    originalNameGroups=list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                    originalShapeGroups=list(mod.EXPECTED_TYPE_SHAPE_GROUPS),
                    liveIntegrationGroups=list(expected),
                    physicalClassPointerOriginProven=False,
                    canonicalExecutionTypeKeys=False,coherentVmEpochProven=False,
                    runtimeAcceptance=False),
                profiles={mode:{'result':'PassedWithinInactiveLiveTypeShapeCensusHostScope',
                    'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                    'originalShapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS),
                    'liveIntegrationGroups':list(expected)}
                    for mode in ('strict','sanitized')})
            def check(data):
                receipt.write_text(json.dumps(data))
                return mod.read_component_result(out,'RESULT.json',True,
                    expected_live_type_shape_groups=expected)
            self.assertTrue(check(baseline)['liveTypeShapeCensusCaseInventoryVerified'])
            for mutate in ('no-new-case','duplicate-case','wrong-profile',
                           'wrong-kind','boolean-schema','fake-canonical',
                           'missing-original-source','wrong-fingerprint',
                           'wrong-preflight','wrong-original-group',
                           'wrong-shape-roster','missing-sanitized',
                           'compiler-not-run'):
                with self.subTest(mutate=mutate):
                    value=json.loads(json.dumps(baseline))
                    if mutate=='no-new-case':value['profiles']['strict']['liveIntegrationGroups'].pop()
                    elif mutate=='duplicate-case':value['profiles']['strict']['liveIntegrationGroups'][-1]=value['profiles']['strict']['liveIntegrationGroups'][0]
                    elif mutate=='wrong-profile':value['profiles']['sanitized']['result']='Failed'
                    elif mutate=='wrong-kind':value['kind']='Other'
                    elif mutate=='boolean-schema':value['schemaVersion']=True
                    elif mutate=='fake-canonical':value['canonicalExecutionTypeKeys']=True
                    elif mutate=='missing-original-source':value['sourceContract']['previousMatchedShapeSourceContractVerified']={}
                    elif mutate=='wrong-fingerprint':value['sourceContract']['originalNativeCppAndApiFingerprintPreserved']=False
                    elif mutate=='wrong-preflight':value['sourceContract']['oneShotCensusPreflightBeforeIterator']=False
                    elif mutate=='wrong-original-group':value['profiles']['strict']['originalNameGroups']=[]
                    elif mutate=='wrong-shape-roster':value['sourceContract']['originalShapeGroups']=[]
                    elif mutate=='missing-sanitized':value['profiles'].pop('sanitized')
                    elif mutate=='compiler-not-run':value['actualSourceCompiled']=False
                    with self.assertRaisesRegex(ValueError,'Inactive live type-shape'):
                        check(value)
            unknown=json.loads(json.dumps(baseline))
            unknown['commandLifetimeUnverified']=True
            self.assertFalse(check(unknown)['liveTypeShapeCensusCaseInventoryVerified'])


    def verify_noncanonical_shape_json_receipts_and_mutations(self):
        mod=load();expected=mod.EXPECTED_SHAPE_JSON_GROUPS
        self.assertEqual(len(expected),16)
        self.assertEqual(len(set(expected)),16)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();path=out/'RESULT.json'
            def check(value):
                path.write_text(json.dumps(value))
                return mod.read_component_result(out,'RESULT.json',True,
                    expected_shape_json_groups=expected)
            baseline=make_shape_json_positive(mod)
            self.assertTrue(check(baseline)['observedTypeShapeJsonCaseInventoryVerified'])
            for name in ('missing-case','duplicate-case','wrong-profile',
                         'false-compiled','false-source-preserved','bogus-kind',
                         'bool-schema','wrong-json-scope','wrong-limit',
                         'fake-typekey','fake-epoch','wrong-predecessor',
                         'missing-original-name-group','missing-sanitized',
                         'missing-pure-proof','missing-old-live-group'):
                with self.subTest(mutation=name):
                    data=json.loads(json.dumps(baseline))
                    if name=='missing-case':data['profiles']['strict']['shapeJsonGroups'].pop()
                    elif name=='duplicate-case':
                        data['profiles']['strict']['shapeJsonGroups'][-1]=expected[0]
                    elif name=='wrong-profile':
                        data['profiles']['sanitized']['result']='Failed'
                    elif name=='false-compiled':data['actualSourceCompiled']=False
                    elif name=='false-source-preserved':data['sourcePreserved']=False
                    elif name=='bogus-kind':data['kind']='Other'
                    elif name=='bool-schema':data['schemaVersion']=True
                    elif name=='wrong-json-scope':
                        data['sourceContract']['rowScope']='ExecutionV1'
                    elif name=='wrong-limit':
                        data['sourceContract']['fixedOwnedMaximumBytes']=True
                    elif name=='fake-typekey':
                        data['completeExecutionTypeKeys']=True
                    elif name=='fake-epoch':
                        data['sourceContract']['coherentVmEpochProven']=True
                    elif name=='wrong-predecessor':
                        data['sourceContract']['predecessor']={}
                    elif name=='missing-original-name-group':
                        data['profiles']['strict']['originalNameGroups']=[]
                    elif name=='missing-sanitized':
                        data['profiles'].pop('sanitized')
                    elif name=='missing-pure-proof':
                        data['sourceContract']['purePointerFreeNoVmCalls']=False
                    elif name=='missing-old-live-group':
                        data['sourceContract']['previousLiveCensusGroups']=[]
                    with self.assertRaisesRegex(ValueError,'Observed type-shape JSON'):
                        check(data)
            pending=json.loads(json.dumps(baseline))
            pending['commandLifetimeUnverified']=True
            self.assertFalse(check(pending)['observedTypeShapeJsonCaseInventoryVerified'])

    def verify_real_vm_shape_json_receipt_and_fail_closed_mutations(self):
        mod=load();expected=mod.EXPECTED_VM_SHAPE_JSON_GROUPS
        self.assertEqual(len(expected),16)
        self.assertEqual(len(set(expected)),16)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td).resolve();path=out/'RESULT.json'
            def check(data):
                path.write_text(json.dumps(data))
                return mod.read_component_result(out,'RESULT.json',True,
                    expected_vm_shape_json_groups=expected)
            baseline=make_vm_shape_json_positive(mod)
            baseline['commandLifetimeUnverified']=False
            self.assertTrue(check(baseline)['vmShapeJsonSourceCaseInventoryVerified'])
            for name in ('missing-case','duplicate-case','wrong-kind',
                'nonint-schema','missing-source-compiler','wrong-vm-source',
                'wrong-preflight','wrong-lock-order','fake-typekey',
                'fake-epoch','previous-shape-json-scope','previous-json-budget',
                'previous-source-proof','missing-original-name-group',
                'missing-json-group','missing-sanitized','wrong-profile'):
                with self.subTest(mutation=name):
                    item=json.loads(json.dumps(baseline))
                    if name=='missing-case':
                        item['profiles']['strict']['newBridgeGroups'].pop()
                    elif name=='duplicate-case':
                        item['profiles']['strict']['newBridgeGroups'][-1]=expected[0]
                    elif name=='wrong-kind':item['kind']='Old'
                    elif name=='nonint-schema':item['schemaVersion']=True
                    elif name=='missing-source-compiler':item['actualSourceCompiled']=False
                    elif name=='wrong-vm-source':
                        item['sourceContract']['threeActualVmSourceMethodsCompiled']=False
                    elif name=='wrong-preflight':
                        item['sourceContract']['preflightBeforeIterator']=False
                    elif name=='wrong-lock-order':
                        item['sourceContract']['sourceLocksReleasedBeforePureJson']=False
                    elif name=='fake-typekey':item['canonicalExecutionTypeKeys']=True
                    elif name=='fake-epoch':
                        item['sourceContract']['coherentVmEpochProven']=True
                    elif name=='previous-shape-json-scope':
                        item['sourceContract']['precedingActualVmAndPureJsonSourceVerified']['rowScope']='execution-v1'
                    elif name=='previous-json-budget':
                        item['sourceContract']['precedingActualVmAndPureJsonSourceVerified']['fixedOwnedMaximumBytes']=True
                    elif name=='previous-source-proof':
                        item['sourceContract']['precedingActualVmAndPureJsonSourceVerified']['predecessor']={}
                    elif name=='missing-original-name-group':
                        item['profiles']['strict']['oldNameGroups']=[]
                    elif name=='missing-json-group':
                        item['sourceContract']['oldShapeJsonGroups']=[]
                    elif name=='missing-sanitized':item['profiles'].pop('sanitized')
                    elif name=='wrong-profile':
                        item['profiles']['sanitized']['result']='Failed'
                    with self.assertRaisesRegex(ValueError,'Inactive genuine VM shape JSON'):
                        check(item)
            uncertain=json.loads(json.dumps(baseline))
            uncertain['commandLifetimeUnverified']=True
            self.assertFalse(check(uncertain)['vmShapeJsonSourceCaseInventoryVerified'])


def make_shape_json_positive(mod):
    names=list(mod.EXPECTED_OWNED_BINDING_GROUPS)
    shapes=list(mod.EXPECTED_TYPE_SHAPE_GROUPS)
    live=list(mod.EXPECTED_LIVE_TYPE_SHAPE_GROUPS)
    json_cases=list(mod.EXPECTED_SHAPE_JSON_GROUPS)
    previous={'originalNativeCppAndApiFingerprintPreserved':True,
        'sourceLocksReleasedBeforePureCensus':True,
        'originalNameGroups':names,'originalShapeGroups':shapes,
        'liveIntegrationGroups':live}
    proof={'sourceKind':'R03P1ObservedTypeShapeCounts',
        'rowScope':'ObservedRegistrySubsetShapeCountsOnly',
        'fixedOwnedMaximumBytes':4096,
        'predecessorActualVmSourcesAndFingerprintVerified':True,
        'purePointerFreeNoVmCalls':True,'nonCanonicalOnly':True,
        'previousNameGroups':names,'previousShapeGroups':shapes,
        'previousLiveCensusGroups':live,'newJsonGroups':json_cases,
        'fullExecutionV1':False,'canonicalExecutionTypeKeys':False,
        'physicalClassPointerOriginProven':False,
        'coherentVmEpochProven':False,'runtimeAcceptance':False,
        'predecessor':previous}
    return {'kind':'R03P1ObservedTypeShapeJsonActualVmSourceHost',
        'schemaVersion':1,'result':'PassedWithinOwnedTypeShapeJsonSourceHostScope',
        'sourcePreserved':True,'actualSourceCompiled':True,
        'commandLifetimeUnverified':False,'noncanonicalShapeCountsOnly':True,
        'completeExecutionTypeKeys':False,'fullExecutionV1':False,
        'physicalClassPointerOriginProven':False,'coherentVmEpochProven':False,
        'officialUnitySdkCompiled':False,'UnityPlayerExecuted':False,
        'runtimeAcceptance':False,'sourceContract':proof,
        'profiles':{k:{'result':'PassedWithinOwnedTypeShapeJsonSourceHostScope',
            'originalNameGroups':names,'originalShapeGroups':shapes,
            'liveIntegrationGroups':live,'shapeJsonGroups':json_cases}
            for k in ('strict','sanitized')}}

def make_vm_shape_json_positive(mod):
    old=make_shape_json_positive(mod)["sourceContract"]
    names=list(mod.EXPECTED_OWNED_BINDING_GROUPS)
    shapes=list(mod.EXPECTED_TYPE_SHAPE_GROUPS)
    live=list(mod.EXPECTED_LIVE_TYPE_SHAPE_GROUPS)
    json=list(mod.EXPECTED_SHAPE_JSON_GROUPS)
    new=list(mod.EXPECTED_VM_SHAPE_JSON_GROUPS)
    return {
        'kind':'R03P1InactiveLiveObservedTypeShapeJsonSourceHost',
        'schemaVersion':1,'result':'PassedWithinInactiveVmShapeJsonHostScope',
        'actualSourceCompiled':True,'sourcePreserved':True,
        'canonicalExecutionTypeKeys':False,'fullExecutionV1':False,
        'physicalClassPointerOriginProven':False,'coherentVmEpochProven':False,
        'officialUnitySdkCompiled':False,'UnityPlayerExecuted':False,
        'runtimeAcceptance':False,
        'sourceContract':{
            'precedingActualVmAndPureJsonSourceVerified':old,
            'originalNativeCppAndApiFingerprintPreserved':True,
            'threeActualVmSourceMethodsCompiled':True,
            'preflightBeforeIterator':True,
            'sourceLocksReleasedBeforePureJson':True,
            'ownedPointerFreeJsonOnly':True,
            'oldNameGroups':names,'oldShapeGroups':shapes,
            'oldLiveCensusGroups':live,'oldShapeJsonGroups':json,
            'newBridgeGroups':new,
            'canonicalExecutionTypeKeys':False,
            'coherentVmEpochProven':False,
            'physicalClassPointerOriginProven':False,
            'fullExecutionV1':False,'runtimeAcceptance':False},
        'profiles':{mode:{
            'result':'PassedWithinInactiveVmShapeJsonHostScope',
            'oldNameGroups':names,'oldShapeGroups':shapes,
            'oldLiveCensusGroups':live,'oldShapeJsonGroups':json,
            'newBridgeGroups':new}
            for mode in ('strict','sanitized')}
    }

class BatchFailureScheduling(unittest.TestCase):
    def exercise(self,mode='passed',target='live-general'):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve();ws=root/'workspace';ws.mkdir()
            demo=ws/'hybridclr_demo';native=ws/'il2cpp_plus'
            # Execute the actual input-path expression; only file CONTENTS,
            # Git answers, SDK anchor and child execution are mocks.
            tree=ast.parse(SOURCE.read_text())
            main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
            node=next(n for n in main.body if isinstance(n,ast.Assign) and
                      isinstance(n.targets[0],ast.Name) and n.targets[0].id=='inputs')
            paths=eval(compile(ast.Expression(node.value),str(SOURCE),'eval'),{'demo':demo,'native':native})
            for path in paths:path.parent.mkdir(parents=True,exist_ok=True);path.write_text('MOCK SOURCE\n')
            unity=root/'Editor/2022.3.62f2/Unity.app/Contents/MacOS/Unity'
            unity.parent.mkdir(parents=True);unity.write_text('MOCK SDK ANCHOR; NOT EXECUTED')
            dest=root/'batch';mod=load();launched=[];checks=[]
            def verify(base,name,sha,git_probe=None):
                checks.append(name)
                if mode=='postflight-error' and len(checks)>5:
                    raise RuntimeError('mock remote failure')
                if mode=='postflight-git-timeout' and len(checks)>5:
                    # The only instrumented command is a deliberately timed-out
                    # fake ls-remote. Never execute Git/SSH in host tests.
                    assert git_probe is not None
                    git_probe.command(name,["git","-C",base/name,"ls-remote",
                                           "origin","refs/heads/"+mod.BRANCH])
                return {'repository':'night-outlook/'+name,'head':sha,'clean':True}
            def child(argv,timeout=120):
                args=list(map(str,argv))
                if args[0]=='git':
                    raise subprocess.TimeoutExpired(args,timeout,
                        output=b'partial-git-authority-stdout',
                        stderr=b'partial-ssh-transport-stderr')
                out=Path(args[args.index('--output')+1]);name=out.name
                launched.append(name);out.mkdir()
                if name==target:
                    if mode=='timeout':raise subprocess.TimeoutExpired(args,timeout,output=b'partial-out',stderr=b'partial-err')
                    if mode=='interrupted':raise KeyboardInterrupt
                    if mode=='unknown':raise RuntimeError('mock unknown outcome')
                    if mode=='spawn-failed':raise FileNotFoundError('mock launch failure')
                expected=('Passed' if name in ('managed-sdk','native-sdk') else
                          'PassedHostOnly' if name=='legacy-host' else
                          'PassedWithinOwnedHostScope' if name=='owned-general' else
                          'PassedWithinInactiveSourceHostScope' if name=='live-general' else
                          'PassedWithinOwnedExecutionHostScope' if name=='owned-execution' else
                          'PassedWithinInactiveZeroClassHostScope' if name=='empty-live' else
                          'PassedWithinInactiveOpaqueHostScope' if name=='opaque-inventory' else
                          'PassedWithinInactivePhysicalEnumerationHostScope' if name=='physical-membership' else
                          'PassedWithinInactiveOwnedPhysicalNamesHostScope' if name=='owned-physical-names' else
                          'PassedWithinOwnedPhysicalNamesJsonHostScope' if name=='owned-physical-json' else
                          'PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope' if name=='live-owned-physical-json' else
                          'PassedWithinObservedTypeShapeSourceHostScope' if name=='observed-type-shape' else
                          'PassedWithinInactiveLiveTypeShapeCensusHostScope' if name=='live-type-shape-census' else
                          'PassedWithinOwnedTypeShapeJsonSourceHostScope' if name=='observed-type-shape-json' else
                          'PassedWithinInactiveVmShapeJsonHostScope' if name=='vm-shape-json' else
                          'PassedWithinInactiveHostScope' if name=='frozen-v2' else 'PassedWithinHostScope')
                data={'result':expected,'commandLifetimeUnverified':name==target and mode=='nested-timeout'}
                if name=='owned-physical-names':
                    data.update(kind='R03P1InactiveOwnedObservedPhysicalNamesSourceHost',
                                schemaVersion=1,actualSourceCompiled=True,
                                sourcePreserved=True,ownedPhysicalNamesOnly=True,
                                completeExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                                metadataPointerLifetimeProven=False,coherentVmEpochProven=False,
                                officialUnitySdkCompiled=False,UnityPlayerExecuted=False,
                                runtimeAcceptance=False,
                                profiles={mode_name:{'result':'PassedWithinExplicitVmMocks',
                                      'caseGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS)}
                                      for mode_name in ('strict','sanitized')})
                if name=='owned-physical-json':
                    data.update(kind='R03P1OwnedPhysicalNamesJsonActualSourceHost',
                                schemaVersion=1,actualSourceCompiled=True,
                                sourcePreserved=True,
                                ownedJsonSchema='R03P1ObservedPhysicalDisplayNames',
                                rowScope='OwnedSnapshotLocalDisplayNamesOnly',
                                canonicalExecutionTypeKeys=False,
                                physicalClassPointerOriginProven=False,
                                coherentVmEpochProven=False,
                                officialUnitySdkCompiled=False,
                                UnityPlayerExecuted=False,runtimeAcceptance=False,
                                sourceContract={'actualFixtureCaseIds':list(mod.EXPECTED_OWNED_JSON_GROUPS),
                                    'noVmMetadataOrFileOperations':True,'nonCanonicalScopeOnly':True},
                                profiles={mode_name:{'result':'PassedWithinOwnedNonCanonicalJsonHostScope',
                                      'caseGroups':list(mod.EXPECTED_OWNED_JSON_GROUPS)}
                                      for mode_name in ('strict','sanitized')})
                if name=='live-owned-physical-json':
                    data.update(kind='R03P1InactiveLiveOwnedPhysicalJsonSourceHost',
                         schemaVersion=1,actualSourceCompiled=True,sourcePreserved=True,
                         sourceToJsonIntegrationTestedWithMocks=True,
                         physicalClassPointerOriginProven=False,metadataPointerLifetimeProven=False,
                         canonicalExecutionTypeKeys=False,coherentVmEpochProven=False,
                         officialUnitySdkCompiled=False,UnityPlayerExecuted=False,
                         runtimeAcceptance=False,
                         sourceContract={'originalNativeCppAndApiFingerprintPreserved':True,
                             'productionSourceMethodsCompiled':2,
                             'bridgeDoesNotReadAdditionalVmPointers':True,
                             'sourcePassBeforePureOwnedSerialization':True,
                             'caseGroups':list(mod.EXPECTED_LIVE_OWNED_JSON_GROUPS),
                             'canonicalExecutionTypeKeys':False,'runtimeAcceptance':False},
                         profiles={k:{'result':'PassedWithinInactiveLiveOwnedPhysicalJsonVmMockScope',
                             'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                             'liveIntegrationGroups':list(mod.EXPECTED_LIVE_OWNED_JSON_GROUPS)}
                             for k in ('strict','sanitized')})
                if name=='observed-type-shape':
                    data.update(kind='R03P1ObservedTypeShapeActualVmSourceHost',
                        schemaVersion=1,actualSourceCompiled=True,sourcePreserved=True,
                        typeShapeCategoriesOnly=True,completeExecutionTypeKeys=False,
                        physicalClassPointerOriginProven=False,coherentVmEpochProven=False,
                        officialUnitySdkCompiled=False,UnityPlayerExecuted=False,
                        runtimeAcceptance=False,
                        sourceContract={'typedFieldsCopiedOnlyFromMatchedCallback':True,
                            'exactPinnedIl2CppClassAbiSourceInspected':True,
                            'originalCppApiFingerprintVerified':True,
                            'noMetadataPointersRetained':True,
                            'candidateRowsAreOnlySimpleShapeHints':True,
                            'canonicalExecutionTypeKeys':False,
                            'physicalPointerOriginProven':False,
                            'globalVmEpochProven':False,'playerExecution':False,
                            'runtimeAcceptance':False,
                            'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                            'shapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS)},
                        profiles={k:{'result':'PassedWithinObservedTypeShapeSourceHostScope',
                            'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                            'shapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS)}
                            for k in ('strict','sanitized')})
                if name=='live-type-shape-census':
                    data.update(kind='R03P1InactiveLiveObservedTypeShapeCensusHost',
                        schemaVersion=1,actualSourceCompiled=True,sourcePreserved=True,
                        canonicalExecutionTypeKeys=False,physicalClassPointerOriginProven=False,
                        coherentVmEpochProven=False,officialUnitySdkCompiled=False,
                        UnityPlayerExecuted=False,runtimeAcceptance=False,
                        sourceContract={'previousMatchedShapeSourceContractVerified':{
                            'typedFieldsCopiedOnlyFromMatchedCallback':True,
                            'originalCppApiFingerprintVerified':True,
                            'noMetadataPointersRetained':True,
                            'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                            'shapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS)},
                            'originalNativeCppAndApiFingerprintPreserved':True,
                            'actualNativeSourceMethodsCompiled':2,
                            'sourceLocksReleasedBeforePureCensus':True,
                            'oneShotCensusPreflightBeforeIterator':True,
                            'candidateShapeOnlyNotCanonicalIdentity':True,
                            'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                            'originalShapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS),
                            'liveIntegrationGroups':list(mod.EXPECTED_LIVE_TYPE_SHAPE_GROUPS),
                            'physicalClassPointerOriginProven':False,
                            'canonicalExecutionTypeKeys':False,
                            'coherentVmEpochProven':False,'runtimeAcceptance':False},
                        profiles={p:{'result':'PassedWithinInactiveLiveTypeShapeCensusHostScope',
                            'originalNameGroups':list(mod.EXPECTED_OWNED_BINDING_GROUPS),
                            'originalShapeGroups':list(mod.EXPECTED_TYPE_SHAPE_GROUPS),
                            'liveIntegrationGroups':list(mod.EXPECTED_LIVE_TYPE_SHAPE_GROUPS)}
                            for p in ('strict','sanitized')})
                if name=='vm-shape-json':
                    # Preserve separately injected timeout/lifetime evidence.
                    data.update(make_vm_shape_json_positive(mod))
                if name=='observed-type-shape-json':
                    positive=make_shape_json_positive(mod)
                    # Keep the independently injected timeout/lifetime state;
                    # a source-host positive mock must never erase this fault.
                    positive.pop('commandLifetimeUnverified')
                    data.update(positive)
                if name in ('empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json','live-owned-physical-json','observed-type-shape','live-type-shape-census','observed-type-shape-json','vm-shape-json') and name==target:
                    if mode=='missing-lifetime-marker':
                        data.pop('commandLifetimeUnverified')
                    if mode=='malformed-lifetime-marker':
                        data['commandLifetimeUnverified']='false'
                    if mode=='null-lifetime-marker':
                        data['commandLifetimeUnverified']=None
                if name=='managed-sdk':
                    data.update(kind='R03CompleteBuildHelperCompile',schemaVersion=1,unityVersion='2022.3.62f2',
                                unityEditorRun=False,nativeExecution=False,runtimeAcceptance=False)
                    (out/'build-api').mkdir();file=out/'build-api/results.json'
                else:file=out/('results.json' if name=='native-sdk' else 'RESULT.json')
                if not (name in ('empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json','live-owned-physical-json','observed-type-shape','live-type-shape-census','observed-type-shape-json','vm-shape-json') and name==target and mode=='missing-result'):
                    file.write_text(json.dumps(data))
                if mode=='missing-result' and name==target:
                    # Ensure this failure injection remains an actual absent
                    # producer result (not a cached positive response).
                    file.unlink(missing_ok=True)
                    if file.exists():
                        raise AssertionError("Missing-result fixture retained positive bytes")
                stdout=(json.dumps({'result':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}).encode()
                        if name=='managed-sdk' else b'mock child\n')
                return subprocess.CompletedProcess(args,7 if mode=='nonzero' and name==target else 0,stdout,b'mock stderr\n')
            argv=['runner','--workspace',str(ws),'--unity',str(unity),'--output',str(dest),
                  '--sdk-scratch',str(root/'scratch'),'--expected-demo','a'*40,'--expected-native','b'*40]
            code=0
            with patch.object(sys,'argv',argv),patch.object(mod,'verify_repo',side_effect=verify), \
                 patch.object(mod,'run',side_effect=child),contextlib.redirect_stdout(io.StringIO()):
                try:mod.main()
                except SystemExit as error:code=error.code
            report=json.loads((dest/'RESULT.json').read_bytes())
            manifest=json.loads((dest/'MANIFEST.json').read_bytes())
            self.assertEqual(len(report['commands']),24)
            self.assertEqual(report['componentCount'],24)
            self.assertEqual(report['attemptedComponentCount'],len(launched))
            self.assertEqual(report['expectedNativeSyntaxUnits'],100)
            self.assertEqual(report['expectedOwnedBindingCaseGroupsPerProfile'],28)
            self.assertEqual(report['expectedOwnedPhysicalJsonCaseGroupsPerProfile'],21)
            self.assertEqual(report['expectedLiveOwnedPhysicalJsonCaseGroupsPerProfile'],12)
            self.assertEqual(report['expectedObservedTypeShapeCaseGroupsPerProfile'],15)
            self.assertEqual(report['expectedLiveTypeShapeCensusCaseGroupsPerProfile'],16)
            self.assertEqual(report['expectedObservedTypeShapeJsonCaseGroupsPerProfile'],16)
            self.assertEqual(report['expectedVmShapeJsonCaseGroupsPerProfile'],16)
            self.assertFalse(report['R03Accepted']);self.assertFalse(report['UnityPlayerExecuted'])
            self.assertFalse(report['historicalEvidenceReclassified'])
            for row in report['commands']:
                self.assertEqual(row,json.loads((dest/'commands'/(row['name']+'.json')).read_bytes()))
                if row['status']=='NotRun':self.assertFalse((dest/row['name']).exists())
            for row in manifest['files']:
                raw=(dest/row['path']).read_bytes()
                self.assertEqual(row['sha256'],hashlib.sha256(raw).hexdigest());self.assertEqual(row['size'],len(raw))
            return code,report,manifest,launched,checks

    def test_all_eighteen_components_have_independent_success(self):
        # Preserve the frozen 85-test public inventory while adding the
        # source-bound registration binding negative assertions to this leaf.
        OwnedBindingInventoryContract().verify_exact_host_binding_inventory_and_fail_closed_mutations()
        OwnedBindingInventoryContract().verify_noncanonical_json_receipt_and_fail_closed_mutations()
        OwnedBindingInventoryContract().verify_live_owned_json_receipt_and_fail_closed_mutations()
        OwnedBindingInventoryContract().verify_observed_type_shape_receipt_and_failure_mutations()
        OwnedBindingInventoryContract().verify_live_type_shape_census_receipt_and_fail_closed_mutations()
        OwnedBindingInventoryContract().verify_noncanonical_shape_json_receipts_and_mutations()
        OwnedBindingInventoryContract().verify_real_vm_shape_json_receipt_and_fail_closed_mutations()
        self.verify_bounded_git_postflight_direct_command_receipts()
        code,report,manifest,launched,checks=self.exercise()
        self.assertEqual(code,0);self.assertEqual(len(launched),24);self.assertEqual(len(checks),8)
        self.assertTrue(report['sourcePreserved']);self.assertIsNone(report['stoppedAfter'])
        # Git identity commands are intentionally mocked here; do not claim
        # host test values are real SSH/remote stream evidence.
        self.assertEqual(report['postflightGitDiagnostics']['actualDirectCommandCount'],0)
        self.assertFalse(report['postflightGitDiagnostics']['receiptsRecorded'])
        self.assertEqual(report['postflightGitDiagnostics']['completedRepositoryCount'],4)
        self.assertTrue(report['officialUnitySdkCompileAttempted']);self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertEqual(manifest['inventoryScope'],'CompletedBatchFiles')
        self.assertFalse(report['commandLifetimeUnverified'])
        self.assertFalse(manifest['commandLifetimeUnverified'])
        self.assertEqual(manifest['commandLifetimeUnverified'],
                         report['commandLifetimeUnverified'])

    def verify_bounded_git_postflight_direct_command_receipts(self):
        mod=load()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            workspace=root/"workspace";workspace.mkdir()
            identity="hybridclr_demo";source=workspace/identity;source.mkdir()
            expected="a"*40
            commands=[]
            def fake_git(argv,timeout=120):
                arguments=list(map(str,argv))
                commands.append((arguments,timeout))
                op=arguments[3]
                results={
                    "remote":b"https://github.com/night-outlook/hybridclr_demo.git\n",
                    "branch":(mod.BRANCH+"\n").encode(),
                    "rev-parse":(expected+"\n").encode(),
                    "status":b"",
                    "ls-remote":(expected+"\trefs/heads/"+mod.BRANCH+"\n").encode(),
                }
                return subprocess.CompletedProcess(arguments,0,results[op],b"")
            probe=mod.GitPostflightProbe(root/"postflight-git")
            with patch.object(mod,"run",side_effect=fake_git):
                identityRow=mod.verify_repo(workspace,identity,expected,git_probe=probe)
            self.assertEqual(identityRow["head"],expected)
            self.assertEqual(len(commands),5)
            self.assertTrue(all(t==120 for _,t in commands))
            self.assertEqual([record["status"] for record in probe.records],["Completed"]*5)
            self.assertFalse(probe.unknown_lifetime)
            completed=probe.summary([identityRow])
            self.assertEqual(completed["completedRepositoryCount"],1)
            self.assertEqual(completed["actualDirectCommandCount"],5)
            self.assertFalse(completed["descendantQuiescenceProven"])
            full=root/"postflight-git"/identity/"05-ls-remote"
            actual=(expected+"\trefs/heads/"+mod.BRANCH+"\n").encode()
            self.assertEqual((full/"stdout.bin").read_bytes(),actual)
            receipt=json.loads((full/"RESULT.json").read_bytes())
            self.assertEqual(receipt["stdoutCapturedSha256"],hashlib.sha256(actual).hexdigest())
            self.assertEqual(receipt["timeoutSeconds"],120)
            self.assertFalse(receipt["timedOut"])
            self.assertEqual(receipt["exit"],0)
            # Simulate the exact previously missing postflight authority
            # evidence. No retry and no executable SSH work takes place.
            failed=mod.GitPostflightProbe(root/"postflight-failed")
            timed=["git","-C",workspace/"hybridclr","ls-remote","origin",
                   "refs/heads/"+mod.BRANCH]
            with patch.object(mod,"run",side_effect=subprocess.TimeoutExpired(
                    timed,120,output=b'partial-remote-head',
                    stderr=b'partial-ssh-handshake')) as cmd:
                with self.assertRaises(subprocess.TimeoutExpired):
                    failed.command("hybridclr",timed)
                self.assertEqual(cmd.call_count,1)
            line=failed.records[0]
            self.assertEqual(line["status"],"TimedOut")
            self.assertEqual(line["exit"],None)
            self.assertTrue(line["commandLifetimeUnverified"])
            self.assertEqual(line["timeoutSeconds"],120)
            self.assertFalse(line["descendantQuiescenceProven"])
            self.assertEqual((root/"postflight-failed/hybridclr/01-ls-remote/stdout.bin").read_bytes(),
                             b'partial-remote-head')
            self.assertEqual((root/"postflight-failed/hybridclr/01-ls-remote/stderr.bin").read_bytes(),
                             b'partial-ssh-handshake')
            self.assertTrue(failed.summary([])["commandLifetimeUnverified"])
            # Known completed nonzero remains distinct from unknown lifetime.
            nonzero=mod.GitPostflightProbe(root/"postflight-nonzero")
            argv=["git","-C",workspace/"hybridclr","ls-remote","origin",
                  "refs/heads/"+mod.BRANCH]
            with patch.object(mod,"run",return_value=subprocess.CompletedProcess(
                    argv,128,b'',b'unknown host')):
                response=nonzero.command("hybridclr",argv)
            self.assertEqual(response.returncode,128)
            self.assertEqual(nonzero.records[0]["status"],"CompletedNonzero")
            self.assertFalse(nonzero.unknown_lifetime)

    def assert_stopped(self,mode,target='live-general',code=1):
        actual,report,manifest,launched,checks=self.exercise(mode,target)
        self.assertEqual(actual,code);self.assertEqual(launched[-1],target)
        self.assertLess(len(launched),24);self.assertEqual(len(checks),4)
        self.assertFalse(report['sourcePreserved']);self.assertTrue(report['commandLifetimeUnverified'])
        self.assertEqual(report['result'],'FailedOrIncomplete')
        self.assertFalse(report['officialUnitySdkCompileAttempted'])
        self.assertEqual(manifest['inventoryScope'],'UnsealedObservedFiles')
        self.assertTrue(manifest['commandLifetimeUnverified'])
        self.assertEqual(manifest['commandLifetimeUnverified'],
                         report['commandLifetimeUnverified'])
        self.assertIn(target,report['stoppedAfter'])
        self.assertGreater(sum(c['status']=='NotRun' for c in report['commands']),0)

    def test_outer_timeout_stops_remaining_commands(self):self.assert_stopped('timeout')
    def test_nested_timeout_stops_even_with_passed_child_verdict(self):self.assert_stopped('nested-timeout')
    def test_unknown_outcome_stops_without_fabricating_postflight(self):self.assert_stopped('unknown')
    def test_keyboard_interrupt_preserves_summary_and_exit130(self):self.assert_stopped('interrupted',code=130)
    def test_first_component_timeout_leaves_seventeen_notrun(self):self.assert_stopped('timeout','command-failures')

    def test_completed_nonzero_keeps_other_independent_checks(self):
        for target in ('owned-execution','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json','live-owned-physical-json','observed-type-shape','live-type-shape-census','observed-type-shape-json','vm-shape-json'):
            with self.subTest(target=target):
                code,report,manifest,launched,checks=self.exercise('nonzero',target)
                self.assertEqual(code,1);self.assertEqual(len(launched),24);self.assertEqual(len(checks),8)
                self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),23)
                self.assertEqual(next(c for c in report['commands'] if c['name']==target)['status'],'Failed')
                self.assertTrue(report['officialUnitySdkCompilePassed']);self.assertTrue(report['sourcePreserved'])
                self.assertIsNone(report['stoppedAfter'])

    def test_known_launch_failure_is_retained_without_faking_an_exit(self):
        code,report,manifest,launched,checks=self.exercise('spawn-failed')
        self.assertEqual(code,1);self.assertEqual(len(launched),24)
        record=next(c for c in report['commands'] if c['name']=='live-general')
        self.assertIsNone(record['exit']);self.assertIn('FileNotFoundError',record['exception'])

    def test_last_sdk_timeout_is_attempted_but_not_passed(self):
        code,report,manifest,launched,checks=self.exercise('timeout','native-sdk')
        self.assertEqual(code,1);self.assertEqual(len(launched),24)
        self.assertTrue(report['officialUnitySdkCompileAttempted'])
        self.assertFalse(report['officialUnitySdkCompilePassed']);self.assertFalse(report['sourcePreserved'])
        self.assertTrue(report['commandLifetimeUnverified'])

    def test_postflight_failure_cannot_turn_green(self):
        code,report,manifest,launched,checks=self.exercise('postflight-error')
        self.assertEqual(code,1);self.assertFalse(report['sourcePreserved'])
        self.assertIn('mock remote failure',report['postflightError'])
        self.assertEqual(len(report['fourRepositoriesAfter']),1)
        self.assertEqual(report['postflightGitDiagnostics']['completedRepositoryCount'],1)
        self.assertEqual(report['postflightGitDiagnostics']['actualDirectCommandCount'],0)
        self.assertFalse(report['postflightGitDiagnostics']['receiptsRecorded'])
        self.assertEqual(report['result'],'FailedOrIncomplete')
        # Reproduce the c776 successor's exact aggregate failure mode
        # using one fake partial-output timeout, never a live SSH probe.
        code,report,manifest,launched,checks=self.exercise('postflight-git-timeout')
        self.assertEqual(code,1)
        self.assertEqual(len(launched),24)
        self.assertEqual(len(report['fourRepositoriesAfter']),1)
        self.assertEqual(report['componentCount'],24)
        self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),24)
        self.assertFalse(report['sourcePreserved'])
        self.assertTrue(report['commandLifetimeUnverified'])
        self.assertEqual(report['result'],'FailedOrIncomplete')
        self.assertIsNone(report['stoppedAfter'])
        self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertEqual(manifest['inventoryScope'],'UnsealedObservedFiles')
        # Synthetic END-TO-END Git-only timeout: all 24 child mocks pass and
        # only the second final repository's real GitPostflightProbe times out.
        # Compare separately serialized RESULT.json and MANIFEST.json, not
        # just a local boolean/AST fragment. This assertion was missing and
        # exposes IR-LOCAL-P1-GIT-MANIFEST-LIFETIME-01.
        self.assertTrue(manifest['commandLifetimeUnverified'])
        self.assertEqual(manifest['commandLifetimeUnverified'],
                         report['commandLifetimeUnverified'])
        self.assertTrue(report['postflightGitDiagnostics']['commandLifetimeUnverified'])
        self.assertIn('TimeoutExpired',report['postflightError'])
        self.assertEqual(report['postflightGitDiagnostics']['timedOutCommands'],1)
        self.assertEqual(report['postflightGitDiagnostics']['completedRepositoryCount'],1)
        self.assertFalse(report['postflightGitDiagnostics']['descendantQuiescenceProven'])
        # Per-command bytes are preserved and hashed under new raw root.
        # The helper returns after its TemporaryDirectory ends, so inspect
        # the serialized aggregate rather than guessing a separate path.

    def test_native_empty_live_nested_timeout_stops_outer_children(self):
        self.assert_stopped('nested-timeout','empty-live')

    def test_missing_native_empty_live_marker_stops_outer_children(self):
        self.assert_stopped('missing-lifetime-marker','empty-live')

    def test_malformed_native_empty_live_marker_stops_outer_children(self):
        self.assert_stopped('malformed-lifetime-marker','empty-live')

    def test_missing_native_empty_live_result_stops_outer_children(self):
        self.assert_stopped('missing-result','empty-live')

    def test_known_nonzero_empty_live_continues_without_claiming_pass(self):
        code,report,manifest,launched,checks=self.exercise('nonzero','empty-live')
        self.assertEqual(code,1)
        self.assertEqual(len(launched),24)
        self.assertEqual(len(checks),8)
        self.assertIsNone(report['stoppedAfter'])
        self.assertFalse(report['commandLifetimeUnverified'])
        self.assertTrue(report['sourcePreserved'])
        self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),23)
        self.assertEqual(next(c for c in report['commands']
                              if c['name']=='empty-live')['status'],'Failed')

    def test_opaque_reported_lifetime_uncertainty_stops_batch(self):
        self.assert_stopped('nested-timeout','opaque-inventory')

    def test_missing_opaque_lifetime_marker_stops_batch(self):
        self.assert_stopped('missing-lifetime-marker','opaque-inventory')

    def test_malformed_opaque_lifetime_marker_stops_batch(self):
        self.assert_stopped('malformed-lifetime-marker','opaque-inventory')

    def test_null_opaque_lifetime_marker_stops_batch(self):
        self.assert_stopped('null-lifetime-marker','opaque-inventory')

    def test_missing_opaque_result_stops_batch(self):
        self.assert_stopped('missing-result','opaque-inventory')

    def test_physical_membership_reported_uncertainty_stops_batch(self):
        self.assert_stopped('nested-timeout','physical-membership')

    def test_physical_membership_missing_lifetime_marker_stops_batch(self):
        self.assert_stopped('missing-lifetime-marker','physical-membership')

    def test_physical_membership_string_lifetime_marker_stops_batch(self):
        self.assert_stopped('malformed-lifetime-marker','physical-membership')

    def test_physical_membership_null_lifetime_marker_stops_batch(self):
        self.assert_stopped('null-lifetime-marker','physical-membership')

    def test_physical_membership_missing_result_stops_batch(self):
        self.assert_stopped('missing-result','physical-membership')

    def test_owned_names_reported_lifetime_stops(self):
        self.assert_stopped('nested-timeout','owned-physical-names')

    def test_owned_names_missing_lifetime_marker_stops(self):
        self.assert_stopped('missing-lifetime-marker','owned-physical-names')

    def test_owned_names_malformed_lifetime_marker_stops(self):
        self.assert_stopped('malformed-lifetime-marker','owned-physical-names')

    def test_owned_names_null_lifetime_marker_stops(self):
        self.assert_stopped('null-lifetime-marker','owned-physical-names')

    def test_owned_names_missing_result_stops(self):
        self.assert_stopped('missing-result','owned-physical-names')
        self.assert_stopped('nested-timeout','owned-physical-json')
        self.assert_stopped('missing-lifetime-marker','owned-physical-json')
        self.assert_stopped('malformed-lifetime-marker','owned-physical-json')
        self.assert_stopped('null-lifetime-marker','owned-physical-json')
        self.assert_stopped('missing-result','owned-physical-json')
        self.assert_stopped('nested-timeout','live-owned-physical-json')
        self.assert_stopped('missing-lifetime-marker','live-owned-physical-json')
        self.assert_stopped('malformed-lifetime-marker','live-owned-physical-json')
        self.assert_stopped('null-lifetime-marker','live-owned-physical-json')
        self.assert_stopped('missing-result','live-owned-physical-json')
        self.assert_stopped('nested-timeout','observed-type-shape')
        self.assert_stopped('missing-lifetime-marker','observed-type-shape')
        self.assert_stopped('malformed-lifetime-marker','observed-type-shape')
        self.assert_stopped('null-lifetime-marker','observed-type-shape')
        self.assert_stopped('missing-result','observed-type-shape')
        self.assert_stopped('nested-timeout','live-type-shape-census')
        self.assert_stopped('missing-lifetime-marker','live-type-shape-census')
        self.assert_stopped('malformed-lifetime-marker','live-type-shape-census')
        self.assert_stopped('null-lifetime-marker','live-type-shape-census')
        self.assert_stopped('missing-result','live-type-shape-census')
        self.assert_stopped('nested-timeout','observed-type-shape-json')
        self.assert_stopped('missing-lifetime-marker','observed-type-shape-json')
        self.assert_stopped('malformed-lifetime-marker','observed-type-shape-json')
        self.assert_stopped('null-lifetime-marker','observed-type-shape-json')
        self.assert_stopped('missing-result','observed-type-shape-json')
        self.assert_stopped('nested-timeout','vm-shape-json')
        self.assert_stopped('missing-lifetime-marker','vm-shape-json')
        self.assert_stopped('malformed-lifetime-marker','vm-shape-json')
        self.assert_stopped('null-lifetime-marker','vm-shape-json')
        self.assert_stopped('missing-result','vm-shape-json')

if __name__=='__main__':unittest.main(verbosity=2)
