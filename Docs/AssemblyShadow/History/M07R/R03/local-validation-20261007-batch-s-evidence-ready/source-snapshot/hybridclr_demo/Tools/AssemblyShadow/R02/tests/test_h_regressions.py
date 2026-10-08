"""Batch-H integration regressions. Synthetic data is never Player evidence."""
import contextlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import m05_results
import m07_results
import r01_early_results
import run_local
import type_resolution_schema as schema
import verify_regressions as gate
from evidence import EvidenceError, write

# Independent wire inventory, not read from the validator under test.
UINTS = '''definitionSearches definitionRowsScanned admissionCacheHits admissionCacheMisses
admissionProofAttempts admissionProofRejections admissionEntries admissionRetainedBytes admissionUnready
baselineStateChecks fieldWorkspaceBuilds interfaceWorkspaceBuilds layoutCheckCalls counterpartCacheHits
counterpartCacheMisses counterpartEntries absentCounterpartEntries cacheFixedBytes counterpartRetainedBytes
genericContextChecks observationLockContentions observationMemoHits observationMemoTlsBytesPerThread
counterStorageBytes counterThreadCapacity droppedCounterThreads'''.split()


def extension(level=2):
    value = {name: 0 for name in UINTS}
    value.update(schemaVersion=1, diagnosticsLevel=level, counterThreadCapacity=128,
                 counterSaturated=False, memoryAccountingAvailable=level > 0,
                 counterCoverage='Disabled' if level == 0 else 'BoundedComplete',
                 classesCoverage='Disabled' if level < 2 else 'BoundedComplete',
                 memoryAccountingScope='R02StructuresExcludingAllocatorOverhead')
    return value


def type_info(assembly='AssemblyA.Implementation.Internal', shadow=True):
    return dict(schemaVersion=1, logicalAssembly=assembly, executionModeCode=int(shadow),
                executionMode='InterpreterShadow' if shadow else 'AotBaseline', isActive=True,
                physicalImageKind='Interpreter' if shadow else 'Aot', typeKey='fixture-type',
                inputTypePointer='', activeTypePointer='', baselineTypePointer='',
                pointerDetailsAvailable=False, baselinePointerAvailable=False, containsShadowTypes=shadow,
                definitionCacheHits=0, definitionCacheMisses=0, compositeRebuilds=0, allocationRemaps=0, guardFailures=0)


def m07_rows(off=False):
    phases = '''data-asset prefab-asset prefab-first unity-path-probe prefab-cached-after-unload-false
prefab-reloaded-after-gc serialize-reference-owner serialize-reference-concrete nested-internal nested-external
mixed-rename-guard monoscript-get-class mixed-reload-after-unload-true scene-single dont-destroy-component
scene-additive-delayed scene-scene-reload'''.split()
    rows = []
    for phase in phases:
        assembly = m07_results.EXTENSIBILITY_CONSUMER if phase == 'nested-external' else m07_results.INTERNAL
        info = type_info(assembly, not off and assembly == m07_results.INTERNAL); info['r02'] = extension()
        rows.append(dict(phase=phase, assemblyName=assembly,
                         typeName='AssemblyA.Implementation.Internal.VersionedPrefabComponent',
                         code='FeatureDisabled' if off else 'Success', executionMode=info['executionMode'],
                         rawJson='' if off else json.dumps(info), sameType=True, active=True))
    return {'typeResolutions': rows}


class StrictSchema(unittest.TestCase):
    def test_inventory_is_exactly_33_and_all_native_profiles_are_supported(self):
        for level in range(3):
            self.assertEqual(len(extension(level)), 33)
            self.assertEqual(schema.validate_extension(extension(level)), extension(level))
        self.assertEqual(set(UINTS), set(schema.COUNTERS))

    def test_every_field_is_mandatory_and_unknown_fields_fail(self):
        for name in extension():
            value = extension(); del value[name]
            with self.subTest(name=name), self.assertRaises(EvidenceError): schema.validate_extension(value)
        value = extension(); value['extra'] = 0
        with self.assertRaises(EvidenceError): schema.validate_extension(value)
        for value in (None, [], False, '{}'):
            with self.assertRaises(EvidenceError): schema.validate_extension(value)

    def test_unsigned_fields_preserve_precision_and_reject_coercion(self):
        for name in UINTS:
            if name != 'counterThreadCapacity':
                value = extension(); value[name] = (1 << 64) - 1
                self.assertEqual(schema.validate_extension(value)[name], (1 << 64) - 1)
            for invalid in (-1, 1 << 64, True, 1.0, '1', None):
                value = extension(); value[name] = invalid
                with self.subTest(name=name, value=invalid), self.assertRaises(EvidenceError): schema.validate_extension(value)

    def test_profile_version_boolean_and_coverage_are_typed(self):
        changes = [('schemaVersion', True), ('schemaVersion', 2), ('diagnosticsLevel', True),
                   ('diagnosticsLevel', -1), ('diagnosticsLevel', 3), ('counterThreadCapacity', 129),
                   ('counterCoverage', 'Unknown'), ('classesCoverage', None), ('counterSaturated', 0),
                   ('memoryAccountingAvailable', 1), ('memoryAccountingScope', 'Other')]
        for key, item in changes:
            value = extension(); value[key] = item
            with self.subTest(key=key), self.assertRaises(EvidenceError): schema.validate_extension(value)
        for level, key, item in ((0,'memoryAccountingAvailable',True), (0,'counterCoverage','BoundedComplete'),
                                 (1,'classesCoverage','BoundedComplete'), (2,'classesCoverage','Disabled')):
            value=extension(level);value[key]=item
            with self.assertRaises(EvidenceError): schema.validate_extension(value)

    def test_live_counter_relations_are_not_invented(self):
        value = extension(); value.update(admissionCacheHits=99999, admissionEntries=0,
            counterSaturated=True, counterCoverage='BoundedComplete', memoryAccountingAvailable=True)
        # Different native loads can straddle a transition; schema is not a global snapshot.
        schema.validate_extension(value)

    def test_legacy_checker_is_unchanged_and_scope_restores_on_failure(self):
        original = m07_results.verify_type_resolutions
        value = type_info(); value['r02'] = extension()
        with self.assertRaises(Exception): m05_results.verify_type_info(value, 'raw')
        with self.assertRaisesRegex(RuntimeError, 'intentional'):
            with schema.current_m07_schema(): raise RuntimeError('intentional')
        self.assertIs(m07_results.verify_type_resolutions, original)
        with self.assertRaises(Exception): m05_results.verify_type_info(value, 'raw')

    def test_bridge_preserves_every_original_raw_string(self):
        raw=m07_rows();saved=copy.deepcopy(raw)
        with schema.current_m07_schema() as receipt:
            m07_results.verify_type_resolutions(raw, 'raw', {m07_results.INTERNAL}, False)
            self.assertEqual(receipt['verifiedTypeInfoObjects'], 17)
            self.assertFalse(receipt['rawEvidenceModified'])
        self.assertEqual(raw,saved)

    def test_bridge_requires_known_extension_and_keeps_legacy_semantics(self):
        for mutation in ('missing','unknown','duplicate','legacy-mode','profile'):
            raw=m07_rows();value=json.loads(raw['typeResolutions'][0]['rawJson'])
            if mutation=='missing': del value['r02']
            elif mutation=='unknown': value['extra']=0
            elif mutation=='legacy-mode': value['executionModeCode']=0
            elif mutation=='profile': value['r02']=extension(1)
            text=json.dumps(value)
            if mutation=='duplicate': text=text[:-1]+',"r02":'+json.dumps(extension())+'}'
            raw['typeResolutions'][0]['rawJson']=text
            with self.subTest(mutation=mutation), schema.current_m07_schema(), self.assertRaises(Exception):
                m07_results.verify_type_resolutions(raw,'raw',{m07_results.INTERNAL},False)

    def test_off_still_uses_unchanged_disabled_contract(self):
        with schema.current_m07_schema() as receipt:
            m07_results.verify_type_resolutions(m07_rows(True),'off',set(),True)
            self.assertEqual(receipt['verifiedTypeInfoObjects'],0)


class DispatchAndOutput(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();(self.root/'_temp/AssemblyShadow').mkdir(parents=True)
        self.batch=object.__new__(run_local.Batch)
        self.batch.roots={'candidate':self.root};self.batch.heads={'candidate':'a'*40};self.batch.targets={}
        self.batch.generated_roots=set();self.batch.prefix='R02-'+'1'*32;self.batch.out=self.root/'batch'
        self.batch.graphs={'candidate':dict(fixtureManifest='fixtures',nativeOnReceipt='on',nativeOffReceipt='off',editorReplayReceipt='replay')}
        self.batch.values={'negative-fixtures':dict(failure='failure',negative='negative')}

    def test_startup_dispatches_existing_strict_module_via_source_bound_bridge(self):
        with patch.object(self.batch,'tool') as call: self.batch.regression('startup11')
        self.assertEqual([c.args[0] for c in call.call_args_list], ['run-r01-early-players.py','R02/verify_regressions.py'])
        args=call.call_args_list[-1].args[1]
        self.assertIn('--candidate-head',args);self.assertIn('startup11',args)
        self.assertTrue((run_local.TOOLS/call.call_args_list[-1].args[0]).is_file())
        self.assertTrue(callable(r01_early_results.main))

    def test_m07_and_failure_keep_distinct_strict_verifiers(self):
        with patch.object(self.batch,'tool') as call: self.batch.regression('m07')
        self.assertEqual(call.call_args_list[-1].args[0],'R02/verify_regressions.py')
        self.assertIn('m07',call.call_args_list[-1].args[1])
        with patch.object(self.batch,'tool') as call: self.batch.regression('failure')
        self.assertEqual(call.call_args_list[-1].args[0],'verify-r01-failure-results.py')

    def diagnostic(self, wrong=False):
        for name,text in (('Assets/AssemblyShadowR01BDiagnostics/Scenes/R01BDiagnostic.unity','  expectedBaselineBuildId: old\n  expectedRuntimeAbiHash: old\n'),
                          ('Assets/HybridCLRGenerate/link.xml','<linker/>')):
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        def unity(role, method, args):
            self.assertEqual(method,'AssemblyShadowDemo.Editor.R02DiagnosticBuild.Build')
            output=Path(args[args.index('-shadowR01BDiagnosticOutput')+1]);output.mkdir()
            self.assertTrue(output.is_relative_to(self.root/'Builds/AssemblyShadow/R01B'))
            receipt=Path(args[args.index('-shadowR01BDiagnosticBuildReceipt')+1])
            snapshot=self.root/'_temp/AssemblyShadow/R01B/snapshot';snapshot.mkdir(parents=True)
            write(receipt,dict(playerOutput=str(self.root/'wrong') if wrong else str(output),inputSnapshot=str(snapshot)))
        with patch.object(self.batch,'unity',side_effect=unity) as call, patch.object(self.batch,'stopped'), \
             patch.object(run_local.authority,'inspect'), patch('r01b_diagnostic_inputs.verify_diagnostic_inputs'):
            result=self.batch.diagnostic()
        return result, call

    def test_diagnostic_uses_fresh_required_root_and_retains_it(self):
        result,call=self.diagnostic();value=json.loads(result.read_text());output=Path(value['playerOutput'])
        self.assertIn(output.parent,self.batch.generated_roots)
        self.assertEqual(json.loads((result.parent/'output-plan.json').read_text())['playerOutput'],str(output))
        self.assertEqual(call.call_count,1)

    def test_diagnostic_rejects_preexisting_root_before_unity(self):
        path=self.root/'Builds/AssemblyShadow/R01B'/(self.batch.prefix+'-diagnostic');path.mkdir(parents=True)
        with self.assertRaises(EvidenceError): self.diagnostic()

    def test_diagnostic_rejects_linked_parent(self):
        external=self.root/'external';external.mkdir();(self.root/'Builds').symlink_to(external,target_is_directory=True)
        with self.assertRaises(EvidenceError): self.diagnostic()
        self.assertEqual(list(external.iterdir()),[])

    def test_wrong_diagnostic_output_cannot_pass_after_recovery(self):
        with self.assertRaisesRegex(EvidenceError,'receipt output differs'): self.diagnostic(wrong=True)


class StrictEntry(unittest.TestCase):
    def run_gate(self, kind, *, incomplete=False, fail_authority=False):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();output=root/'strict.json'
            write(root/gate.authority.TARGETS,{})
            result=({'resultPassed':not incomplete,'diagnosticOnly':False,'missingModes':[],
                     'modes':[{} for _ in m07_results.MODES]} if kind=='m07' else
                    {'result':'PassedBoundedProfile','requestedModes':list(r01_early_results.DEFAULT_MODES),
                     'modes':[{'diagnosticProfileComplete':True} for _ in range(10 if incomplete else 11)]})
            def delegate(args): write(output,result);return 0
            @contextlib.contextmanager
            def bridge(): yield {'verifiedTypeInfoObjects':17}
            module=gate.m07_results if kind=='m07' else gate.r01_early_results
            with patch.object(module,'main',side_effect=delegate) as call, \
                 patch.object(gate,'current_m07_schema',side_effect=bridge), \
                 patch.object(gate.authority,'inspect',return_value={'result':'fixture'},side_effect=EvidenceError('source mismatch') if fail_authority else None):
                try: code=gate.main(['--kind',kind,'--project-root',str(root),'--candidate-head','a'*40,'--output',str(output)])
                except EvidenceError: code=1
            return code,json.loads(output.with_name('strict.json.r02-schema.json').read_text()),call.call_count

    def test_source_checked_entry_invokes_the_existing_strict_startup_main(self):
        code,report,count=self.run_gate('startup11');self.assertEqual((code,count),(0,1));self.assertEqual(report['result'],'Passed')

    def test_partial_startup_and_m07_are_not_promoted(self):
        for kind in ('startup11','m07'):
            code,report,count=self.run_gate(kind,incomplete=True)
            self.assertEqual((code,count),(1,1));self.assertEqual(report['result'],'Failed')

    def test_source_mismatch_prevents_verifier_execution(self):
        code,report,count=self.run_gate('m07',fail_authority=True)
        self.assertEqual((code,count),(1,0));self.assertIn('source mismatch',report['error'])
