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
            def verify(base,name,sha):
                checks.append(name)
                if mode=='postflight-error' and len(checks)>4:raise RuntimeError('mock remote failure')
                return {'repository':'night-outlook/'+name,'head':sha,'clean':True}
            def child(argv,timeout=120):
                args=list(map(str,argv));out=Path(args[args.index('--output')+1]);name=out.name
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
                if name in ('empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json') and name==target:
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
                if not (name in ('empty-live','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json') and name==target and mode=='missing-result'):
                    file.write_text(json.dumps(data))
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
            self.assertEqual(len(report['commands']),19)
            self.assertEqual(report['componentCount'],19)
            self.assertEqual(report['attemptedComponentCount'],len(launched))
            self.assertEqual(report['expectedNativeSyntaxUnits'],100)
            self.assertEqual(report['expectedOwnedBindingCaseGroupsPerProfile'],28)
            self.assertEqual(report['expectedOwnedPhysicalJsonCaseGroupsPerProfile'],21)
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
        code,report,manifest,launched,checks=self.exercise()
        self.assertEqual(code,0);self.assertEqual(len(launched),19);self.assertEqual(len(checks),8)
        self.assertTrue(report['sourcePreserved']);self.assertIsNone(report['stoppedAfter'])
        self.assertTrue(report['officialUnitySdkCompileAttempted']);self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertEqual(manifest['inventoryScope'],'CompletedBatchFiles')

    def assert_stopped(self,mode,target='live-general',code=1):
        actual,report,manifest,launched,checks=self.exercise(mode,target)
        self.assertEqual(actual,code);self.assertEqual(launched[-1],target)
        self.assertLess(len(launched),19);self.assertEqual(len(checks),4)
        self.assertFalse(report['sourcePreserved']);self.assertTrue(report['commandLifetimeUnverified'])
        self.assertEqual(report['result'],'FailedOrIncomplete')
        self.assertFalse(report['officialUnitySdkCompileAttempted'])
        self.assertEqual(manifest['inventoryScope'],'UnsealedObservedFiles')
        self.assertIn(target,report['stoppedAfter'])
        self.assertGreater(sum(c['status']=='NotRun' for c in report['commands']),0)

    def test_outer_timeout_stops_remaining_commands(self):self.assert_stopped('timeout')
    def test_nested_timeout_stops_even_with_passed_child_verdict(self):self.assert_stopped('nested-timeout')
    def test_unknown_outcome_stops_without_fabricating_postflight(self):self.assert_stopped('unknown')
    def test_keyboard_interrupt_preserves_summary_and_exit130(self):self.assert_stopped('interrupted',code=130)
    def test_first_component_timeout_leaves_seventeen_notrun(self):self.assert_stopped('timeout','command-failures')

    def test_completed_nonzero_keeps_other_independent_checks(self):
        for target in ('owned-execution','opaque-inventory','physical-membership','owned-physical-names','owned-physical-json'):
            with self.subTest(target=target):
                code,report,manifest,launched,checks=self.exercise('nonzero',target)
                self.assertEqual(code,1);self.assertEqual(len(launched),19);self.assertEqual(len(checks),8)
                self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),18)
                self.assertEqual(next(c for c in report['commands'] if c['name']==target)['status'],'Failed')
                self.assertTrue(report['officialUnitySdkCompilePassed']);self.assertTrue(report['sourcePreserved'])
                self.assertIsNone(report['stoppedAfter'])

    def test_known_launch_failure_is_retained_without_faking_an_exit(self):
        code,report,manifest,launched,checks=self.exercise('spawn-failed')
        self.assertEqual(code,1);self.assertEqual(len(launched),19)
        record=next(c for c in report['commands'] if c['name']=='live-general')
        self.assertIsNone(record['exit']);self.assertIn('FileNotFoundError',record['exception'])

    def test_last_sdk_timeout_is_attempted_but_not_passed(self):
        code,report,manifest,launched,checks=self.exercise('timeout','native-sdk')
        self.assertEqual(code,1);self.assertEqual(len(launched),19)
        self.assertTrue(report['officialUnitySdkCompileAttempted'])
        self.assertFalse(report['officialUnitySdkCompilePassed']);self.assertFalse(report['sourcePreserved'])
        self.assertTrue(report['commandLifetimeUnverified'])

    def test_postflight_failure_cannot_turn_green(self):
        code,report,manifest,launched,checks=self.exercise('postflight-error')
        self.assertEqual(code,1);self.assertFalse(report['sourcePreserved'])
        self.assertIn('mock remote failure',report['postflightError'])

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
        self.assertEqual(len(launched),19)
        self.assertEqual(len(checks),8)
        self.assertIsNone(report['stoppedAfter'])
        self.assertFalse(report['commandLifetimeUnverified'])
        self.assertTrue(report['sourcePreserved'])
        self.assertTrue(report['officialUnitySdkCompilePassed'])
        self.assertEqual(sum(c['status']=='Passed' for c in report['commands']),18)
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

if __name__=='__main__':unittest.main(verbosity=2)
