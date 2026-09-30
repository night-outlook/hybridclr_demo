"""Source-independent filesystem evidence helpers, shared with host tests."""
import hashlib
import json
import os
from pathlib import Path
import tarfile

from batch_contract import require, sha

EXCLUDED = ['reference-worktrees/**', 'bin/**', 'obj/**',
            'projects/*/{Library,Temp,Logs,HybridCLRData,obj}/**']


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def excluded(parts):
    return (bool(parts) and parts[0] in ('reference-worktrees', 'bin', 'obj')) or (
        len(parts) >= 3 and parts[0] == 'projects' and parts[2] in ('Library', 'Temp', 'Logs', 'HybridCLRData', 'obj'))


def selected_files(root):
    root = Path(root).resolve()
    result = []
    # Prune caches before traversing them; a Unity Library may contain millions
    # of files. Symlinks in the included scope are never followed or hidden.
    for directory, directories, files in os.walk(root, followlinks=False):
        base = Path(directory)
        kept = []
        for name in sorted(directories):
            path = base / name
            if excluded(path.relative_to(root).parts):
                continue
            require(not path.is_symlink(), 'Unexpected directory symlink: ' + str(path.relative_to(root)))
            kept.append(name)
        directories[:] = kept
        for name in sorted(files):
            path = base / name
            relative = path.relative_to(root)
            if excluded(relative.parts):
                continue
            require(path.is_file() and not path.is_symlink(), 'Expected regular evidence file: ' + str(relative))
            result.append(path)
    return sorted(result)


def seal(root):
    root = Path(root).resolve()
    require(not (root / 'LOCAL_BATCH_RESULT.json').exists(), 'Final result must be written after sealing')
    files = [{'path': str(p.relative_to(root)), 'size': p.stat().st_size, 'sha256': sha(p)} for p in selected_files(root)]
    require(files, 'Empty evidence cannot be sealed')
    index = {'schemaVersion': 1, 'kind': 'R03FocusedEvidenceIndex', 'files': files,
             'excludedLiveRoots': EXCLUDED, 'fullR02Seal': False, 'runtimeAcceptance': False}
    write(root / 'evidence-index.json', index)
    archive = root / 'evidence.tar.gz'
    with tarfile.open(archive, 'x:gz') as output:
        for item in files:
            output.add(root / item['path'], arcname=item['path'], recursive=False)
        output.add(root / 'evidence-index.json', arcname='evidence-index.json', recursive=False)
    with tarfile.open(archive, 'r:gz') as source:
        all_members = source.getmembers()
        members = {m.name: m for m in all_members}
        require(len(members) == len(all_members), 'Duplicate archive members')
        require(set(members) == {f['path'] for f in files} | {'evidence-index.json'}, 'Exact archive membership')
        expected = files + [{'path': 'evidence-index.json', 'size': (root / 'evidence-index.json').stat().st_size,
                             'sha256': sha(root / 'evidence-index.json')}]
        for item in expected:
            require(members[item['path']].isfile(), 'Non-regular archive entry')
            stream = source.extractfile(members[item['path']])
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
            require(digest.hexdigest() == item['sha256'] and members[item['path']].size == item['size'], 'Archive byte authentication')
    receipt = {'archiveSha256': sha(archive), 'indexSha256': sha(root / 'evidence-index.json'),
               'members': len(files) + 1, 'boundedEvidenceOnly': True, 'runtimeAcceptance': False}
    write(root / 'seal-receipt.json', receipt)
    return receipt


def finalize(root, summary):
    root = Path(root)
    # The immutable execution ledger is an input to the seal. The final result
    # binds that ledger and the completed seal, avoiding a circular self-hash.
    write(root / 'BATCH_EXECUTION.json', summary)
    result = dict(summary)
    try:
        result['seal'] = seal(root)
        result['sealStatus'] = 'Passed'
    except Exception as error:
        result['sealStatus'] = 'Failed'
        result['result'] = 'ReturnRequired'
        result['sealError'] = str(error)
        write(root / 'SEAL_FAILED.json', {'error': str(error), 'result': 'ReturnRequired'})
    result['executionLedgerSha256'] = sha(root / 'BATCH_EXECUTION.json')
    result['R03Accepted'] = False
    result['H2Passed'] = False
    write(root / 'LOCAL_BATCH_RESULT.json', result)
    return result
