"""Completion entry-point and strict R02 schema tests; no Player is launched.

Only external launch/fixture work and the outer legacy entry are isolated.
The actual R02 bridge, duplicate-key parser and original M07 type verifier run.
"""
import contextlib
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import legacy_runtime as legacy
import m05_results
from evidence import EvidenceError
from shadow_tools import VerificationError

UINTS = '''definitionSearches definitionRowsScanned admissionCacheHits admissionCacheMisses
admissionProofAttempts admissionProofRejections admissionEntries admissionRetainedBytes admissionUnready
baselineStateChecks fieldWorkspaceBuilds interfaceWorkspaceBuilds layoutCheckCalls counterpartCacheHits
counterpartCacheMisses counterpartEntries absentCounterpartEntries cacheFixedBytes counterpartRetainedBytes
genericContextChecks observationLockContentions observationMemoHits observationMemoTlsBytesPerThread
counterStorageBytes counterThreadCapacity droppedCounterThreads'''.split()
PHASES = '''data-asset prefab-asset prefab-first unity-path-probe prefab-cached-after-unload-false
prefab-reloaded-after-gc serialize-reference-owner serialize-reference-concrete nested-internal nested-external
mixed-rename-guard monoscript-get-class mixed-reload-after-unload-true scene-single dont-destroy-component
scene-additive-delayed scene-scene-reload'''.split()


def rows(off=False):
    extension = {name: 0 for name in UINTS}
    extension.update(schemaVersion=1, diagnosticsLevel=2, counterThreadCapacity=128,
        counterSaturated=False, memoryAccountingAvailable=True, counterCoverage='BoundedComplete',
        classesCoverage='BoundedComplete', memoryAccountingScope='R02StructuresExcludingAllocatorOverhead')
    result = {'processId': 123, 'typeResolutions': []}
    for phase in PHASES:
        assembly = legacy.m07.EXTENSIBILITY_CONSUMER if phase == 'nested-external' else legacy.m07.INTERNAL
        shadow = not off and assembly == legacy.m07.INTERNAL
        value = dict(schemaVersion=1, logicalAssembly=assembly, executionModeCode=int(shadow),
            executionMode='InterpreterShadow' if shadow else 'AotBaseline', isActive=True,
            physicalImageKind='Interpreter' if shadow else 'Aot', typeKey='fixture-type',
            inputTypePointer='', activeTypePointer='', baselineTypePointer='', pointerDetailsAvailable=False,
            baselinePointerAvailable=False, containsShadowTypes=shadow, definitionCacheHits=0,
            definitionCacheMisses=0, compositeRebuilds=0, allocationRemaps=0, guardFailures=0, r02=dict(extension))
        result['typeResolutions'].append(dict(phase=phase, assemblyName=assembly,
            typeName='AssemblyA.Implementation.Internal.VersionedPrefabComponent',
            code='FeatureDisabled' if off else 'Success', executionMode=value['executionMode'],
            rawJson='' if off else json.dumps(value), sameType=True, active=True))
    return result


class CompletionSchemaDispatchTests(unittest.TestCase):
    def call_entry(self, entry='resource', *, off=False, case='Control-P03', raw=None,
                   no_type_check=False, fail_after_check=False):
        original_callback = legacy.m07.verify_type_resolutions
        with tempfile.TemporaryDirectory() as temp, contextlib.ExitStack() as stack:
            root = Path(temp).resolve(); token = object(); raw = rows(off) if raw is None else raw
            before = copy.deepcopy(raw)
            mode = 'T07-14-FeatureOff' if off else 'T07-01-Prefab-P01'
            build = {'output': root / 'app', 'path': root / 'receipt.json'}
            context = {'manifest': {}, 'baseline': {}, 'fixtures': {}, 'on': build, 'off': build}
            batch = SimpleNamespace(root=root, resource_manifest=root/'fixtures.json', resource_on=root/'on.json',
                resource_off=root/'off.json', resource_replay=root/'replay.json', resource_context={
                    'context': context, 'baselineResources': {}, 'codecContext': token, 'profile': 2,
                    'runner': SimpleNamespace(executable_for=lambda p: root/'app')})
            cap = root / 'capsule'; cap.write_bytes(b'unit-test-only')
            raw_path = root / 'm07-results' / ('m07-' + mode + '.json')
            positive = True
            selected = None
            if entry == 'early':
                selected = next(row for row in legacy.EARLY_CASES if row[0] == case)
                _, early_mode, patch = selected
                positive = early_mode in legacy.early.POSITIVE_MODES
                mode = 'T07-01-Prefab-P01' if patch == 'P01' else legacy.early.DEFAULT_M07_MODE
                raw_path = root / 'early' / case / ('m07-' + mode + '.json')
                # early_case owns its leaf directory.
                raw_path.parent.parent.mkdir(parents=True, exist_ok=True)
            else:
                raw_path.parent.mkdir(parents=True)
                raw_path.write_text(json.dumps(raw))
            disk_before = json.dumps(raw)

            def launch(value, args, folder, expected_exit=0):
                (folder / 'early.json').write_text('{}')
                if entry == 'early' and positive: raw_path.write_text(disk_before)
                return {'pid': 123}, {'console': str(root/'console.log')}

            def verify_case(*args, **kwargs):
                self.assertIs(kwargs['source_context'], token)
                if not no_type_check:
                    legacy.m07.verify_type_resolutions(raw, 'unit-raw', {legacy.m07.INTERNAL}, off)
                if fail_after_check: raise ValueError('failure after strict type-info')
                return {'mode': mode, 'passed': True}

            def verify_suite(*args, **kwargs):
                self.assertIs(kwargs['source_context'], token)
                self.assertIs(kwargs['allow_incomplete'], False)
                for name in sorted(legacy.m07.MODES):
                    is_off = legacy.m07.MODE_PATCH[name] is None
                    legacy.m07.verify_type_resolutions(rows(is_off), 'unit-suite', {legacy.m07.INTERNAL}, is_off)
                return {'resultPassed': True, 'modes': sorted(legacy.m07.MODES)}

            stack.enter_context(mock.patch.object(legacy, 'inventory', return_value={'unit-input': 'unchanged'}))
            stack.enter_context(mock.patch.object(legacy, 'capsule', return_value=cap))
            stack.enter_context(mock.patch.object(legacy, 'launch', side_effect=launch))
            stack.enter_context(mock.patch.object(legacy.early, 'command_for', return_value=[]))
            stack.enter_context(mock.patch.object(legacy.early, 'verify_early_receipt', return_value={'diagnosticProfileComplete': True}))
            for name in ('verify_imported_snapshots', 'verify_startup_logs'):
                stack.enter_context(mock.patch.object(legacy.early, name))
            call = stack.enter_context(mock.patch.object(legacy.m07, 'verify_case', side_effect=verify_case))
            stack.enter_context(mock.patch.object(legacy.m07, 'verify_suite', side_effect=verify_suite))
            try:
                if entry == 'resource': verdict = legacy.m07_case(batch, mode)
                elif entry == 'early': verdict = legacy.early_case(batch, *selected)
                else:
                    legacy.m07_summary(batch)
                    verdict = json.loads((root / 'resource-contracts.json').read_text())
                if entry == 'early' and not positive:
                    self.assertEqual(call.call_count, 0)
                    self.assertIsNone(verdict['typeInfoBridge'])
                else:
                    count = 0 if off else 221 if entry == 'summary' else 17
                    self.assertEqual(verdict['typeInfoBridge']['verifiedTypeInfoObjects'], count)
                    self.assertIs(verdict['typeInfoBridge']['rawEvidenceModified'], False)
                return verdict
            finally:
                self.assertIs(legacy.m07.verify_type_resolutions, original_callback)
                self.assertEqual(raw, before)
                if raw_path.is_file(): self.assertEqual(raw_path.read_text(), disk_before)

    def test_resource_entry_uses_strict_bridge_and_retains_codec_context(self): self.call_entry()
    def test_off_entry_uses_original_disabled_contract(self): self.call_entry(off=True)
    def test_aggregate_rechecks_all_fourteen_modes_under_bridge(self): self.call_entry('summary')

    def test_all_four_positive_startup_paths_use_bridge(self):
        for case in ('Control-P03', 'Control-P01', 'OrdinaryFirst', 'OrdinaryAfterReserve'):
            with self.subTest(case=case): self.call_entry('early', case=case)

    def test_all_six_rejected_startups_do_not_acquire_business_type_evidence(self):
        for case, mode, _ in legacy.EARLY_CASES:
            if mode not in legacy.early.POSITIVE_MODES:
                with self.subTest(case=case): self.call_entry('early', case=case)

    def test_no_type_info_cannot_create_a_passing_on_receipt(self):
        with self.assertRaisesRegex(Exception, 'type-info'): self.call_entry(no_type_check=True)

    def test_outer_failure_restores_legacy_callback_and_raw(self):
        with self.assertRaisesRegex(ValueError, 'failure after strict'): self.call_entry(fail_after_check=True)

    def test_legacy_default_still_rejects_r02_before_and_after_scope(self):
        value = json.loads(rows()['typeResolutions'][0]['rawJson'])
        with self.assertRaises(Exception): m05_results.verify_type_info(value, 'legacy-before')
        self.call_entry()
        with self.assertRaises(Exception): m05_results.verify_type_info(value, 'legacy-after')

    def bad(self, mutate=None, text_mutate=None, entry='resource'):
        raw = rows(); value = json.loads(raw['typeResolutions'][0]['rawJson'])
        if mutate: mutate(value)
        text = json.dumps(value)
        raw['typeResolutions'][0]['rawJson'] = text_mutate(text) if text_mutate else text
        with self.assertRaises((EvidenceError, VerificationError)): self.call_entry(entry, raw=raw)

    def test_each_missing_extension_field_rejected_through_completion(self):
        for key in json.loads(rows()['typeResolutions'][0]['rawJson'])['r02']:
            with self.subTest(key=key): self.bad(lambda v: v['r02'].pop(key))

    def test_unknown_missing_duplicate_and_mistyped_objects_rejected(self):
        self.bad(lambda v: v.pop('r02'))
        self.bad(lambda v: v.update(future=0))
        self.bad(lambda v: v['r02'].update(future=0))
        self.bad(lambda v: v.update(r02=[]))
        self.bad(text_mutate=lambda text: text[:-1] + ',"r02":{}}')
        self.bad(text_mutate=lambda text: text.replace('"diagnosticsLevel": 2', '"diagnosticsLevel": 2,"diagnosticsLevel": 2'))
        self.bad(text_mutate=lambda text: text.replace('"schemaVersion": 1', '"schemaVersion": 1,"schemaVersion": 1', 1))

    def test_each_counter_rejects_coercion_negative_and_overflow(self):
        for key in UINTS:
            for bad in (-1, 1 << 64, True, 1.0, '1', None):
                with self.subTest(key=key, value=bad): self.bad(lambda v: v['r02'].update({key: bad}))

    def test_uint64_max_is_lossless_through_completion(self):
        raw = rows()
        for row in raw['typeResolutions']:
            value = json.loads(row['rawJson'])
            value['r02'].update({key: (1 << 64) - 1 for key in UINTS if key != 'counterThreadCapacity'})
            row['rawJson'] = json.dumps(value)
        self.call_entry(raw=raw)

    def test_profiles_coverage_and_legacy_semantics_remain_strict(self):
        for key, value in (('schemaVersion', 2), ('schemaVersion', True), ('diagnosticsLevel', 1),
                ('diagnosticsLevel', 0), ('diagnosticsLevel', True), ('counterCoverage', 'Unknown'),
                ('classesCoverage', 'Disabled'), ('memoryAccountingScope', 'other'),
                ('counterSaturated', 0), ('memoryAccountingAvailable', 1)):
            with self.subTest(key=key, value=value): self.bad(lambda v: v['r02'].update({key: value}))
        self.bad(lambda v: v.update(executionModeCode=0))
        self.bad(lambda v: v.pop('logicalAssembly'))
        self.bad(lambda v: v['r02'].update(diagnosticsLevel=1, classesCoverage='Disabled'), entry='early')


if __name__ == '__main__': unittest.main()
