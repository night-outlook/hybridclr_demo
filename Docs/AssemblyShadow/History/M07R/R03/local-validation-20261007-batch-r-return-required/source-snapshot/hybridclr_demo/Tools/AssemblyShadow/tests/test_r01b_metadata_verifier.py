"""Profile 2 wire/provenance and adversarial offline admission regressions."""
import copy
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch as mock_patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import m07_results as gate
import m04_results as diagnostics
from shadow_tools import VerificationError
from test_m04_results import diagnostic
from test_r01_metadata_pipeline import patch_fixture

NATIVE = Path(__file__).resolve().parents[4] / 'hybridclr'
MANAGED = Path(__file__).resolve().parents[4] / 'hybridclr_unity'


def profile2_metadata(rows, before=0):
    revision = subprocess.check_output(['git', '-C', str(NATIVE), 'rev-parse', 'HEAD'], text=True).strip()
    header = subprocess.check_output(['git', '-C', str(NATIVE), 'show', revision + ':hybridclr/metadata/InterpreterMetadataIndexCodec.h'])
    profile = dict(gate.R01B_PROFILE_CONSTANTS, nativeSourceRevision=revision,
                   nativeCodecHeaderSha256=hashlib.sha256(header).hexdigest())
    inputs = [{key: row[key] for key in ('name', 'dllSize', 'sha256')} for row in rows]
    total = sum(row['dllSize'] for row in inputs)
    report = dict(gate.R01B_REPORT_CONSTANTS, nativeSourceRevision=revision,
                  nativeCodecHeaderSha256=profile['nativeCodecHeaderSha256'], inputs=inputs,
                  allocations=[dict(row, imageId=before+i+1) for i,row in enumerate(inputs)],
                  currentReservedImageCount=before, reservedImageCountBefore=before,
                  reservedImageCountAfter=before+len(rows), requestedImageCount=len(rows),
                  requiredImages=len(rows), aggregateDllBytes=total, aggregateInputDllBytes=total,
                  lifetimeReservedImageCount=before+len(rows), remainingImageCount=8192-before-len(rows),
                  acceptedImages=len(rows), aggregateDllEnvelopeFits=total<=536870912,
                  aggregateDllEnvelopeExceeded=total>536870912)
    return dict(nativeBudgetCapabilityVersion=2, metadataEncodingProfile2=profile, metadataCapacityReport2=report)


def promote(fixture, manifest, baseline, patch):
    for value in (baseline, patch):
        value.pop('metadataEncodingProfile'); value.pop('metadataCapacityReport')
        value.update(profile2_metadata(patch['closure'] if value is patch else []))
        value['sourcePins']['hybridclr'].update(localPath=str(NATIVE), revision=value['metadataEncodingProfile2']['nativeSourceRevision'])
    manifest['runtimeAbiHash'] = gate.prior._runtime_abi_hash(baseline['sourcePins'], 'test')
    patch['runtimeAbiHash'] = manifest['runtimeAbiHash']


class Profile2Tests(unittest.TestCase):
    def test_explicit_schemas_match_managed_serializable_fields(self):
        source = (MANAGED / 'Editor/AssemblyShadow/Build/MetadataCapacityPlannerProfile2.cs').read_text()
        for cls, expected in [('MetadataEncodingProfile2', gate.R01B_PROFILE_FIELDS),
                              ('MetadataCapacityProfile2PreliminaryReport', gate.R01B_REPORT_FIELDS)]:
            section = source.split('public sealed class ' + cls)[1].split('public bool IsValid')[0].split('\n    }')[0]
            fields = re.findall(r'^        public (?:int|ulong|bool|string|MetadataCapacityProfile2Input\[\]|MetadataCapacityProfile2Allocation\[\]) (\w+)\s*[;=]', section, re.M)
            self.assertEqual(set(fields), set(expected.split()))

    def test_public_patch_verifier_recomputes_profile2_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            fixture, manifest, baseline, path, patch, compiled, snapshot, write = patch_fixture(Path(temp), True)
            promote(fixture, manifest, baseline, patch); write()
            with mock_patch.object(gate, 'verify_compile_snapshot', return_value=(compiled, snapshot)), mock_patch.object(gate.prior, '_reflection_snapshot', return_value=None):
                self.assertTrue(gate.verify_patch(fixture, manifest, baseline, path)['r01Capability'])
                for key, value in [('finalPageFitKnown', True), ('runtimeFinalizationRequired', False),
                                   ('reservedPages', 1), ('mappedPages', 1), ('remainingImageCount', 8192),
                                   ('aggregateInputDllBytes', 1), ('fitsPreliminary', False),
                                   ('admissionKind', 'Final'), ('firstFailingAssembly', None),
                                   ('budgetCapabilityVersion', 1), ('maxImages', 8191)]:
                    original = copy.deepcopy(patch['metadataCapacityReport2'])
                    patch['metadataCapacityReport2'][key] = value; write()
                    with self.subTest(key=key), self.assertRaises(VerificationError): gate.verify_patch(fixture, manifest, baseline, path)
                    patch['metadataCapacityReport2'] = original
                patch['metadataCapacityReport2']['allocations'][0]['imageId'] += 1; write()
                with self.assertRaises(VerificationError): gate.verify_patch(fixture, manifest, baseline, path)

    def test_codec_hash_source_revision_and_baseline_reservation_binding(self):
        value = profile2_metadata([])
        value['sourcePins'] = {'hybridclr': dict(revision=value['metadataEncodingProfile2']['nativeSourceRevision'], localPath=str(NATIVE))}
        self.assertEqual(gate.diagnostic_abi(value, 'test'), 2)
        for target, key, replacement in [('metadataEncodingProfile2', 'nativeCodecHeaderSha256', '0'*64),
                                         ('metadataEncodingProfile2', 'nativeSourceRevision', '0'*40),
                                         ('metadataEncodingProfile2', 'codecBits', 31),
                                         ('metadataCapacityReport2', 'reservedImageCountAfter', 1)]:
            bad = copy.deepcopy(value); bad[target][key] = replacement
            with self.subTest(key=key), self.assertRaises(VerificationError): gate.verify_budget_binding(value, bad, 'test')

    def test_mixed_partial_and_unknown_profile_fields_fail_closed(self):
        value = dict.fromkeys(gate.R01B_PATCH_FIELDS.split())
        value.update(profile2_metadata([]))
        gate.patch_schema(value, 'test')
        for extra in [dict(metadataEncodingProfile=None), dict(metadataEncodingProfile={}, metadataCapacityReport={}),
                      dict(metadataIndexBits=22), dict(metadataEncodingProfile2=dict(value['metadataEncodingProfile2'], metadataIndexBits=22))]:
            bad = dict(value, **extra)
            with self.subTest(extra=extra), self.assertRaises(VerificationError):
                gate.patch_schema(bad, 'test')
                bad['sourcePins'] = {'hybridclr': {'revision': value['metadataEncodingProfile2']['nativeSourceRevision'], 'localPath': str(NATIVE)}}
                gate.verify_profile2(bad, 'test')
        value.update(metadataEncodingProfile=None, metadataCapacityReport=None)
        gate.patch_schema(value, 'test')

    def test_baseline_ordinary_inputs_are_bound_to_snapshot_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); dll = root / 'Ordinary.dll'; dll.write_bytes(b'ordinary-input')
            row = dict(name='Ordinary', dllSize=dll.stat().st_size, sha256=gate.digest(dll))
            baseline = profile2_metadata([row])
            baseline['sourcePins'] = {'hybridclr': dict(revision=baseline['metadataEncodingProfile2']['nativeSourceRevision'], localPath=str(NATIVE))}
            snapshot = dict(assemblies=[dict(name='Ordinary', path=dll.name)], filteredAssemblies=[],
                            references=[], normalHotUpdateAssemblies=['Ordinary'])
            gate.verify_baseline_metadata(baseline, snapshot, root, 'test')
            dll.write_bytes(b'tampered-input')
            with self.assertRaises(VerificationError): gate.verify_baseline_metadata(baseline, snapshot, root, 'test')

    def test_dormant_profile1_constructor_defaults_are_exact(self):
        import json
        sample = json.loads((Path(__file__).parent / 'data/r01-metadata-serialization.json').read_text())
        profile = sample['profile']; profile.update(nativeSourceRevision='', nativeHelperSha256='')
        gate._dormant_profile1(profile, False, 'test')
        profile['nativeSourceRevision'] = '0'*40
        with self.assertRaises(VerificationError): gate._dormant_profile1(profile, False, 'test')
        report = dict(schemaVersion=1, profileVersion=1, metadataIndexBits=22, metadataKindBits=2,
            nativeSourceRevision='', nativeHelperSha256='', nativeBudgetCapabilityVersion=1,
            inputs=[], allocations=[], cursorsBefore=[0]*4, cursorsAfter=[0]*4,
            remainingSlotsBefore=[0]*4, remainingSlotsAfter=[0]*4, requiredImages=0, acceptedImages=0,
            availableImages=0, availableImagesAtFailure=0, fits=False, firstFailingIndex=-1,
            firstFailingAssembly='', firstFailingBytes=0, firstFailingSize=0, failureReason='None',
            firstFailingReason='None', ordinaryAssemblyCount=0, aotCandidateAssemblyCount=0,
            actualRemainingRuntime='NotKnown', runtimeCursorSource='BaselineOrdinaryPlan',
            ordinaryConsumptionIsEstimate=True, runtimeReserveMetadataBudget=False)
        gate._dormant_profile1(report, True, 'test')
        report['fits'] = True
        with self.assertRaises(VerificationError): gate._dormant_profile1(report, True, 'test')

    def test_diagnostic_abi_is_explicit_and_capability_is_bound(self):
        value = diagnostic()
        value.update(runtimeAbiVersion=2, startupCandidateSchemaVersion=1, startupCandidateNames=[],
                     startupObservationMode='ConfigureOnly', metadataBudgetCapabilityVersion=2, recoveryCapabilityVersion=1)
        diagnostics._diagnostic(value, 'test', 2)
        with self.assertRaises(VerificationError): diagnostics._diagnostic(value, 'test')
        for key, val in [('runtimeAbiVersion', 1), ('metadataBudgetCapabilityVersion', 1), ('recoveryCapabilityVersion', 2)]:
            with self.subTest(key=key), self.assertRaises(VerificationError): diagnostics._diagnostic(dict(value, **{key: val}), 'test', 2)
        with self.assertRaises(VerificationError): diagnostics._diagnostic(dict(diagnostic(), runtimeAbiVersion=2), 'test', 2)


if __name__ == '__main__': unittest.main()
