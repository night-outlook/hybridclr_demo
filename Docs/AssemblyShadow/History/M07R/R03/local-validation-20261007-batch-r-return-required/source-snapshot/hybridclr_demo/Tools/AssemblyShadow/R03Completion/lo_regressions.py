#!/usr/bin/env python3
"""Bounded, read-only O adapter regressions; never reclassify the original run.

Only filesystem transport paths in transient contexts are relocated. The stored
receipts, raw observations, source pins, codec profile and bytes are not rewritten.
This does not replay the complete resource verifier or launch Editor/Players.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent / 'R03')]
import execution_contract
import m07_results as m07
from native_codec_source import CodecSourceContext
from batch_contract import loads, require, sha
from batch_evidence import write
from compiler_policy_inputs import regular

RUN = 'projects/resource-complete/_temp/AssemblyShadow/M02Validation-5a8dfffa16d14e3cae2c11b3b4b3a08e'
PLAYER_INPUTS = {
    'on': 'M07PlayerInputs-662516a0fb0f4979a093c0bac5afeb0e',
    'off': 'M07PlayerInputs-13ffef51f0d14c2aa186c622282189cb',
}
ORIGINAL_ROOT = '/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261005O-ln-closure'


def checkpoint(project, override=None):
    index = loads((HERE / 'lo-inputs.json').read_text())
    root = Path(override) if override else Path(project) / index['checkpoint']
    root = root.resolve(strict=True)
    for row in index['files']:
        relative = Path(row['path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'LO regression input path')
        path = regular(root / relative)
        require(path.stat().st_size == row['size'] and sha(path) == row['sha256'], 'Immutable O input differs: ' + row['path'])
    return root, index


def measurement_context(root):
    batch = Path(root) / 'batch'
    context = {'fixtures': {}}
    for name in ('P01', 'P03'):
        path = batch / RUN / (name + '-patch') / 'patch-manifest.json'
        context['fixtures'][name] = {'root': path.parent, 'patch': loads(path.read_text())}
    for role, folder in PLAYER_INPUTS.items():
        path = batch / 'projects/resource-complete/_temp/AssemblyShadow' / folder
        snapshot = loads((path / 'assembly-snapshot.json').read_text())
        player = loads((path / 'm07-player-build.json').read_text())
        require(snapshot['buildGuid'] == player['buildGuid'], 'Original Player/snapshot identity')
        context[role] = {'root': path, 'snapshot': snapshot, 'player': player}
    return context


def measurement_cases(root):
    batch = Path(root) / 'batch'
    for mode in ('R00-ON-NoPatch', 'R00-ON-P01', 'R00-ON-P03', 'R00-OFF-NoPatch'):
        for repetition in range(3):
            folder = batch / 'measurements' / mode / str(repetition)
            request, raw, extra = folder / 'request.json', folder / (mode + '.json'), folder / 'execution.json'
            yield mode, repetition, request, raw, extra


def verify_measurement(context, request, raw, extra):
    request, raw, extra = map(Path, (request, raw, extra))
    observation = loads(extra.read_text())
    return execution_contract.verify(loads(request.read_text()), observation, loads(raw.read_text()),
        sha(request), sha(raw), observation['processId'], context)


def transaction_cases(root):
    batch = Path(root) / 'batch'
    manifest = loads((batch / RUN / 'm07-fixtures.json').read_text())
    paths = [batch / 'm07-results' / ('m07-' + mode + '.json') for mode in sorted(m07.MODE_PATCH) if m07.MODE_PATCH[mode]]
    for role in ('Control-P01', 'Control-P03', 'OrdinaryFirst', 'OrdinaryAfterReserve'):
        mode = 'T07-01-Prefab-P01' if role == 'Control-P01' else 'T07-03-FullClosure-P03'
        paths.append(batch / 'early' / role / ('m07-' + mode + '.json'))
    require(len(paths) == 17, 'Exactly the original 13 ON resources and four positive early cases')
    for path in paths:
        result = loads(path.read_text())
        patch_id = m07.MODE_PATCH[result['mode']]
        fixture = next(row for row in manifest['fixtures'] if row['patchId'] == patch_id)
        patch = loads((batch / RUN / (patch_id + '-patch') / 'patch-manifest.json').read_text())
        # The raw JSON bytes are unchanged; only an in-memory file-transport field
        # is relocated so the original sibling/hash/inline equality checks run.
        old_raw = Path(result['rawDiagnosticsPath'])
        require(old_raw.is_relative_to(Path(ORIGINAL_ROOT)), 'Original raw path provenance')
        actual_raw = batch / old_raw.relative_to(Path(ORIGINAL_ROOT))
        require(actual_raw == path.with_name(path.stem + '-diagnostics.json'), 'Original raw sibling identity')
        require(sha(regular(actual_raw)) == result['rawDiagnosticsSha256'], 'Original raw diagnostic bytes')
        relocated = dict(result, rawDiagnosticsPath=str(actual_raw))
        yield path, relocated, manifest, {'fixture': fixture, 'patch': patch}


def replay(project, native_owner, output, override=None):
    project, owner, out = Path(project).resolve(), Path(native_owner).resolve(strict=True), Path(output).resolve()
    require(not out.exists(), 'Unused LO regression output'); out.mkdir(parents=True)
    root, index = checkpoint(project, override)
    result = {'schemaVersion': 1, 'kind': 'R03LOAdapterRegressionReplay', 'result': 'Failed',
        'basis': 'ReusedAuditedLocalOInputs', 'historicalSourceCommit': index['sourceCommit'],
        'historicalBatchResult': 'Failed', 'historicalEvidenceModified': False,
        'unityEditorRun': False, 'playerRun': False, 'runtimeAcceptance': False,
        'fullResourceVerifierReplayed': False, 'fullR00GateReplayed': False,
        'R03Accepted': False, 'H2Passed': False, 'measurements': [], 'transactions': []}
    try:
        context = measurement_context(root)
        for mode, rep, request, raw, extra in measurement_cases(root):
            verdict = verify_measurement(context, request, raw, extra)
            result['measurements'].append({'mode': mode, 'repetition': rep, 'verdict': verdict,
                'requestSha256': sha(request), 'rawSha256': sha(raw), 'supplementSha256': sha(extra)})
        require(owner.name == 'hybridclr' and owner.parent.name == 'assembly_shadow_h1r', 'Explicit historical codec owner layout')
        # Match the original relative pin without changing it or using cwd. This
        # empty project context is outside every owning Git checkout; it supplies
        # only a base directory, not replacement source, evidence or validation.
        with tempfile.TemporaryDirectory(prefix='r03-lo-codec-', dir=owner.parent.parent) as temp:
            project_context = Path(temp) / 'run/projects/resource-complete'; project_context.mkdir(parents=True)
            for path, raw, manifest, patch in transaction_cases(root):
                pin = patch['patch']['sourcePins']['hybridclr']
                require((project_context / pin['localPath']).resolve() == owner, 'Original codec pin has one exact owner')
                authority = CodecSourceContext(project_context, owner, pin['revision'])
                final = m07.verify_transaction(raw, path, manifest, patch, source_context=authority)
                result['transactions'].append({'case': str(path.relative_to(root / 'batch')), 'result': 'Passed',
                    'rawSha256': sha(path), 'rawDiagnosticSha256': raw['rawDiagnosticsSha256'],
                    'generation': final['generation'], 'nativeEventCount': len(final['events']),
                    'relocatedTransportFields': ['rawDiagnosticsPath'], 'sourcePinsRewritten': False})
        checkpoint(project, root)  # Independent after-read custody check.
        result['result'] = 'Passed'
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        write(out / 'results.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('project', 'native-owner', 'output'): parser.add_argument('--' + name, required=True)
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    replay(args.project, args.native_owner, args.output, args.checkpoint)
