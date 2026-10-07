"""Read-only P resource-observation replay, not a new Player or full build audit.

Authenticate exact P inputs and process receipts. The only I/O relocation maps
one original resource-receipt path to a byte-identical preserved copy. No raw
file/string, semantic checker, codec authority, or historical verdict is changed.
"""
import argparse
import copy
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
import legacy_runtime as legacy
from batch_contract import loads, require, sha
from batch_evidence import write
from compiler_policy_inputs import regular
from unity_command import clean_outer
from shadow_tools import VerificationError

PUBLICATION = 'd9ef449e8e8aef885539e4b981243a868f8d0ba6'
EXECUTED = 'd8884646659f7b6ae0f6ceda746fd271c96c8d61'
CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-20261006-batch-p-return-required'


def replay(project):
    project = Path(project).resolve()
    manifest_path = HERE / 'lp-inputs.json'
    manifest_hash = sha(manifest_path)
    spec = loads(manifest_path.read_text())
    require(spec['kind'] == 'R03LPImmutableConsumerInputs' and spec['schemaVersion'] == 1 and
            spec['publicationCommit'] == PUBLICATION and spec['executedDemoCommit'] == EXECUTED and
            spec['checkpoint'] == CHECKPOINT and spec['historicalPResult'] == 'ReturnRequired' and
            spec['runtimeAcceptance'] is False, 'Exact P input authority and evidence limits')
    checkpoint = project / CHECKPOINT
    files = {}
    for row in spec['files']:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts and row['path'] not in files,
                'Unique bounded P input path')
        file = regular(checkpoint / relative)
        require(file.stat().st_size == row['size'] and sha(file) == row['sha256'], 'Immutable P input: ' + row['path'])
        files[row['path']] = file
    require(len(files) == 40 and len(spec['cases']) == 18, 'Exact bounded P replay inventory')
    def read(name):
        require(name in files, 'Unbound P input')
        return loads(files[name].read_text())
    original_root = Path(spec['originalBatchRoot'])
    fixture = read(spec['fixtureManifest'])
    failures = read(spec['originalFailureReport'])
    require(failures['kind'] == 'ReadOnlyPFailedContractReproduction', 'Original P failure report')
    old = {row['rawPath']: row for row in failures['cases']}
    expected = {'batch/m07-results/m07-' + mode + '.json' for mode in legacy.m07.MODES}
    for case, mode, patch_id in legacy.EARLY_CASES:
        if mode in legacy.early.POSITIVE_MODES:
            m07_mode = 'T07-01-Prefab-P01' if patch_id == 'P01' else legacy.early.DEFAULT_M07_MODE
            expected.add('batch/early/' + case + '/m07-' + m07_mode + '.json')
    require({c['raw'] for c in spec['cases']} == expected, 'All 14 resource and four positive-startup witnesses')
    results = []; callback = legacy.m07.verify_type_resolutions
    for case in spec['cases']:
        file = files[case['raw']]; raw = read(case['raw']); saved = copy.deepcopy(raw)
        original_path = str(original_root / Path(case['raw']).relative_to('batch'))
        command = read(case['command']); clean_outer(command, 0)
        require(raw['processId'] == command['pid'] and raw['result'] == 'Passed' and raw['error'] == '',
                'Original P raw/command process binding')
        argv = command['command']
        require(argv.count('-shadowM07Result') == 1 and argv[argv.index('-shadowM07Result') + 1] == original_path,
                'Exact original raw-output argv')
        require(raw['fixtureManifestSha256'] == sha(files[spec['fixtureManifest']]), 'P fixture bytes')
        require(raw['fixtureManifestPath'] == str(original_root / Path(spec['fixtureManifest']).relative_to('batch')), 'P fixture identity')
        patch_id = legacy.m07.MODE_PATCH[raw['mode']]; off = patch_id is None
        require(case['originalState'] == ('Passed' if off else 'Failed'), 'Preserve P original state')
        if not off:
            original = old[original_path]
            require(original['originalState'] == 'Failed' and original['rawSha256'] == sha(file) and
                    original['commandReceiptSha256'] == sha(files[case['command']]), 'Original failure custody')
        item = None if off else next(x for x in fixture['fixtures'] if x['patchId'] == patch_id)
        closure = [] if off else item['closureLoadOrder']
        resource_root = Path(item['replacementResourcePath']) if patch_id == 'P05' else Path(fixture['baselineManifestPath']).parent / 'ResourceInputs'
        receipt_path = resource_root / 'resource-build-receipt.json'
        require(raw['resourceReceiptPath'] == str(receipt_path), 'Fixture-derived resource identity')
        copies = [files[n] for n in spec['resourceReceipts'] if sha(files[n]) == raw['resourceReceiptSha256']]
        require(len(copies) == 1, 'One exact preserved resource receipt')
        receipt = loads(copies[0].read_text())
        selected = {'path': receipt_path, 'root': resource_root, 'receipt': receipt, 'bundles': receipt['bundles']}
        def relocated_digest(path):
            require(Path(path) == receipt_path, 'Unmapped historical receipt read')
            return sha(copies[0])
        old_error = None
        with patch.object(legacy.m07, 'digest', side_effect=relocated_digest):
            try: legacy.m07.verify_resource_observations(raw, original_path, selected, patch_id, closure, off)
            except VerificationError as error: old_error = str(error)
            require(old_error is None if off else old_error is not None and "unknown=['r02']" in old_error,
                    'Reproduce the precise original schema boundary before bridging')
            with legacy.current_m07_schema() as bridge:
                legacy.m07.verify_resource_observations(raw, original_path, selected, patch_id, closure, off)
        require(legacy.m07.verify_type_resolutions is callback and raw == saved, 'Legacy callback and raw object custody')
        require(bridge['verifiedTypeInfoObjects'] == (0 if off else 17) and bridge['rawEvidenceModified'] is False, 'Exact current type-info observations')
        results.append({'path': case['raw'], 'rawSha256': sha(file), 'processId': command['pid'],
            'originalState': case['originalState'], 'originalSchemaError': old_error,
            'resourceObservationReplay': 'Passed', 'typeInfoBridge': bridge})
    require(len({r['processId'] for r in results}) == 18, 'Distinct original processes, not new executions')
    require(sha(manifest_path) == manifest_hash and all(sha(files[r['path']]) == r['sha256'] for r in spec['files']), 'Post-replay byte custody')
    return {'kind': 'R03LPBoundedHistoricalResourceReplay', 'result': 'Passed', 'publicationCommit': PUBLICATION,
        'executedDemoCommit': EXECUTED, 'inputManifestSha256': manifest_hash, 'verifiedInputFiles': len(files),
        'cases': results, 'typeInfoObjects': sum(r['typeInfoBridge']['verifiedTypeInfoObjects'] for r in results),
        'scope': 'Complete original resource-observation branch only; not whole M07/build/codec/Player acceptance',
        'receiptPathRelocation': 'One byte-identical resource receipt per case; reject all unmapped reads',
        'historicalPResult': 'ReturnRequired', 'historicalEvidenceModified': False,
        'unityRun': False, 'playerRun': False, 'runtimeAcceptance': False, 'R03Accepted': False, 'H2Passed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Unused replay output')
    write(args.output, replay(args.project))
