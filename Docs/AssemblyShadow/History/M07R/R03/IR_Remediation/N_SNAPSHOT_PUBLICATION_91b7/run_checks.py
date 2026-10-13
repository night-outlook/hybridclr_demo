#!/usr/bin/env python3
"""Source-bound host-only snapshot diagnostics; no Unity launch or repository edits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASELINE = {
    'R03/PlayerProject/AssemblyShadowR03Probe.cpp': '2de5e4ef90eaa79daed65c3df0a8faa58ebd5837',
    'R03IR/PlayerProject/R03TerminalPlayer.cs': 'a7420cbc71c13f2951c1b5330b61307d2c4da5e5',
}
CANDIDATE = {
    'R03/PlayerProject/AssemblyShadowR03Probe.cpp': '2f13925190a1576738457d8d43f3646a4c7c095f',
    'R03IR/PlayerProject/R03TerminalPlayer.cs': '598feeec3231707091699d99fbf4428d50b52024',
}
SCRIPTS = ('test_transport_contract.py', 'test_snapshot_integration.py',
           'test_diagnostic_size.py', 'test_producer_to_snapshot.py',
           'classify_snapshot_failure.py')


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    require(__debug__, 'Python optimization would disable regression assertions')
    here = Path(__file__).resolve().parent
    repo = args.repository.resolve(strict=True)
    output = args.output
    require(output.is_absolute() and output == output.resolve(strict=False), 'Canonical absolute output required')
    require(output.parent.is_dir() and not output.exists() and not output.is_symlink(), 'Unused output with existing parent required')
    require(repo != output and repo not in output.parents and output not in repo.parents, 'Output must be outside source')
    sources = []
    for rel, expected in CANDIDATE.items():
        data = (repo / 'Tools/AssemblyShadow' / rel).read_bytes()
        require(blob(data) == expected, 'Unexpected current candidate: ' + rel)
        original = (here / 'checks/original' / rel).read_bytes()
        require(blob(original) == BASELINE[rel], 'Unexpected original N source: ' + rel)
        sources.append({'path': 'Tools/AssemblyShadow/' + rel, 'gitBlob': expected,
                        'sha256': digest(data), 'bytes': len(data)})
    output.mkdir()
    work = output / 'work'
    work.mkdir()
    for name in SCRIPTS:
        shutil.copyfile(here / 'checks' / name, work / name)
    shutil.copytree(here / 'checks/source-extracts', work / 'source-extracts')
    for rel in CANDIDATE:
        old = work / 'source/hybridclr_demo/Tools/AssemblyShadow' / rel
        new = work / 'candidate/hybridclr_demo/Tools/AssemblyShadow' / rel
        old.parent.mkdir(parents=True, exist_ok=True)
        new.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(here / 'checks/original' / rel, old)
        shutil.copyfile(repo / 'Tools/AssemblyShadow' / rel, new)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    steps = [
        ('contracts', [sys.executable, '-B', '-m', 'unittest', 'test_transport_contract', '-v']),
        ('integration', [sys.executable, '-B', 'test_snapshot_integration.py', '--output', str(output/'integration')]),
        ('size', [sys.executable, '-B', 'test_diagnostic_size.py', '--output', str(output/'size')]),
        ('coupled', [sys.executable, '-B', 'test_producer_to_snapshot.py', '--producer-json', str(output/'size/strict.json'), '--output', str(output/'coupled')]),
    ]
    results = []
    verified = False
    try:
        for name, argv in steps:
            result = subprocess.run(argv, cwd=work, env=env, capture_output=True, timeout=180)
            (output/(name+'.stdout')).write_bytes(result.stdout)
            (output/(name+'.stderr')).write_bytes(result.stderr)
            results.append({'name': name, 'argv': argv, 'cwd': str(work), 'exitCode': result.returncode,
                            'stdoutSha256': digest(result.stdout), 'stderrSha256': digest(result.stderr)})
            require(result.returncode == 0, name + ' failed; preserve original logs')
        text = (output/'contracts.stderr').read_text()
        require('Ran 18 tests' in text and '\nOK\n' in text and 'skipped=' not in text, 'All contract tests must run')
        integration = json.loads((output/'integration/results.json').read_text())
        require(integration['scenarioCountPerProfile'] == 26 and integration['compilerProcessRecords'] == 54, 'Complete integration matrix required')
        coupled = json.loads((output/'coupled/result.json').read_text())
        require(coupled['compilerProcessRecords'] == 4 and coupled['NRootCauseProven'] is False, 'Coupled scope mismatch')
        verified = True
    finally:
        after = [{'path': x['path'], 'sha256': digest((repo/x['path']).read_bytes())} for x in sources]
        unchanged = all(a['sha256'] == b['sha256'] for a,b in zip(sources,after))
        result = {'kind': 'SnapshotDiagnosticPublicationHostAudit', 'source': sources, 'steps': results,
                  'result': 'PassedWithinHostScope' if verified and unchanged else 'FailedOrIncomplete',
                  'allCommandsPassed': len(results) == 4 and all(x['exitCode'] == 0 for x in results),
                  'allResultContractsVerified': verified, 'sourceUnchanged': unchanged,
                  'runtimeAcceptance': False, 'unityLaunched': False,
                  'NRootCauseProven': False, 'sizeRepresentationFixed': False, 'engineDispositionFixed': False}
        (output/'HOST_RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
        files = [{'path': str(p.relative_to(output)), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
                 for p in sorted(output.rglob('*')) if p.is_file()]
        (output/'MANIFEST.json').write_text(json.dumps({'files': files}, indent=2)+'\n')
    require(verified and unchanged, 'Full checks and input preservation required')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
