#!/usr/bin/env python3
"""Prepare every captured D01 failure for replay; never select a 'latest' sample."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h1_local_batch as batch
import h1_pdb_constant_audit as pdb

MODES = ('unresolved', 'compiler-references', 'resolved-enums')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture_files(root):
    root = Path(root).resolve(strict=True)
    manifest = batch.read_json(root / 'capture.json')
    batch.need(manifest.get('schemaVersion') == 1 and manifest.get('kind') == 'ReflectionBindingFailureCapture', 'Unsupported failure capture')
    batch.need(manifest.get('missingReferences') == [], 'Failure capture has unavailable references')
    files = {}
    names = set()
    for row in manifest.get('files', []):
        name = row.get('path')
        batch.need(type(name) is str and name and '\\' not in name and ':' not in name and not Path(name).is_absolute() and
                   all(part not in ('', '.', '..') for part in name.split('/')) and name not in names, 'Unsafe/duplicate capture member')
        names.add(name)
        path = root / name
        batch.need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root), 'Capture member unavailable/outside root')
        batch.need(path.stat().st_size == row['sizeBytes'] and digest(path) == row['sha256'], 'Capture member bytes changed')
        files.setdefault(row['role'], []).append(path)
    batch.need(len(files.get('pe', [])) == 1 and len(files.get('pdb', [])) == 1 and len(files.get('configuration', [])) == 1,
               'D01 replay requires one original PE, PDB and configuration')
    return manifest, files


def make_plan(capture_root):
    root = Path(capture_root).resolve(strict=True)
    # The caller supplies one diagnostic run root. All captures in it are indexed.
    captures = sorted(root.rglob('capture.json'))
    batch.need(captures, 'No captured failures in this explicit run root')
    tasks = []
    selected = []
    for number, path in enumerate(captures, 1):
        capture_files(path.parent)
        name = 'replay-' + str(number).zfill(3)
        selected.append({'path': str(path), 'sha256': digest(path)})
        tasks.append({'id': name, 'kind': 'unity', 'cwd': '${candidate}', 'unityProject': '${candidate}', 'timeoutSec': 600,
                      'argv': ['${unity}', '-batchmode', '-nographics', '-quit', '-projectPath', '${candidate}',
                               '-executeMethod', 'HybridCLR.AssemblyShadow.CodeGen.ReflectionBindingFailureReplay.RunFromCommandLine',
                               '-shadowH1ReplayCapture', str(path.parent), '-shadowH1ReplayOutput', '${TASK_DIR}/replay',
                               '-logFile', '${TASK_DIR}/unity.log']})
        tasks.append({'id': name + '-audit', 'kind': 'python', 'cwd': '${candidate}', 'timeoutSec': 60, 'requires': [name],
                      'argv': ['${python}', '${candidate}/Tools/AssemblyShadow/h1_replay_batch.py', 'audit',
                               '--capture', str(path.parent), '--replay', '${RUN_DIR}/' + name + '/replay',
                               '--output', '${TASK_DIR}/pdb-audit.json']})
    return {'schemaVersion': 1, 'kind': 'H1LocalDiagnosticBatch', 'minimumFreeGiB': 1,
            'captureIndex': selected, 'tasks': tasks, 'humanGatePassed': False, 'mayEnterR02': False}


def audit_replay(capture, replay):
    capture, replay = Path(capture), Path(replay)
    _, inputs = capture_files(capture)
    original = pdb.parse(inputs['pdb'][0].read_bytes())
    rows = []
    for mode in MODES:
        result_path = replay / (mode + '.json')
        result = batch.read_json(result_path)
        batch.need(result.get('kind') == 'ReflectionBindingFailureReplay' and result.get('mode') == mode and
                   result.get('captureManifestSha256') == digest(capture / 'capture.json'), 'Replay mode/input binding differs')
        row = {'mode': mode, 'resultPath': str(result_path), 'resultSha256': digest(result_path)}
        if result.get('result') == 'Failed':
            batch.need(type(result.get('exception')) is str and result['exception'], 'Failed replay has no raw exception')
            row['status'] = 'EmissionFailed'
        else:
            batch.need(result.get('result') == 'EmittedAndVerified', 'Unknown replay result')
            for extension, key in (('dll', 'peSha256'), ('pdb', 'pdbSha256')):
                batch.need(digest(replay / (mode + '.' + extension)) == result.get(key), 'Emitted replay bytes differ')
            current = pdb.parse((replay / (mode + '.pdb')).read_bytes())
            row['status'] = 'ExactConstantScopeBytesEqual' if pdb.compare(original, current) else 'SymbolMismatch'
            row['constantCount'] = current['constantCount']
        rows.append(row)
    available = [row['mode'] for row in rows if row['mode'] != 'unresolved' and row['status'] == 'ExactConstantScopeBytesEqual']
    return {'kind': 'H1D01ReplayDiagnosticAudit', 'status': 'CandidateRouteAvailable' if available else 'InvestigationRequired',
            'routes': rows, 'availableRoutes': available, 'routeAutomaticallySelected': False,
            'wholeChainM08Pass': False, 'humanGatePassed': False, 'mayEnterR02': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'audit'))
    parser.add_argument('--capture-root', type=Path)
    parser.add_argument('--capture', type=Path)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.action == 'plan':
        batch.need(args.capture_root is not None, 'plan requires --capture-root')
        report = make_plan(args.capture_root)
    else:
        batch.need(args.capture is not None and args.replay is not None, 'audit requires capture and replay')
        report = audit_replay(args.capture, args.replay)
    batch.write_new(args.output, report)
    print(json.dumps({'output': str(args.output), 'status': report.get('status', 'PlanPrepared')}))
    return 1 if report.get('status') == 'InvestigationRequired' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as error:
        print('Blocked: ' + str(error), file=__import__('sys').stderr)
        raise SystemExit(1)
