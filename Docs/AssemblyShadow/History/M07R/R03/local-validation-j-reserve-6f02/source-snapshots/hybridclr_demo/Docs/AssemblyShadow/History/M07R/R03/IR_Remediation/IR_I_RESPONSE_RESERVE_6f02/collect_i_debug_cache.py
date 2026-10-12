#!/usr/bin/env python3
"""Read-only collection of retained I Debug Bee diagnostics; never execute them.

Copies only selected diagnostic extensions into a new external directory.
Current-only Bee files are NOT retroactively authenticated build provenance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

PUBLICATION = '3a3d8f384bd6f02e7a685f2e3aae5758e850d72a'
CHECKPOINT = 'Docs/AssemblyShadow/History/M07R/R03/local-validation-i-post-h-custody-7f36'
WORKSPACE = Path('/Users/ah/GitHub/hybridclr/assembly_shadow_h1r')
BASE = Path('/Users/ah/GitHub/hybridclr/r03-local-validation')
I_ROOT = BASE / 'R03IRLocal-I-post-H-custody-7f36'
BEE = I_ROOT / 'projects/candidate-debug/Library/Bee'
OUTPUT = BASE / 'DebugBee-R03J-reserve-6f02'
ANCHORS = {
    'batch/builds/candidate-debug/Editor.log': 'ff88312ae6a01a3b9fd402f8f290c1b68bc028da',
    'batch/builds/candidate-debug/build-receipt.json': 'fdcd91d2f3e2ef350bfd78e4f7ffa84ebd505d07',
    'batch/commands/0004/command.json': 'ef97e7b08d6a29e200d8223d9fc725103961671f',
}
EXTENSIONS = {'.binlog', '.json', '.dag', '.log', '.traceevents', '.rsp'}
MAX_FILE = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_FILES = 2048
NEEDLE = b'failed to allocate space to load shared cache file'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(path):
    require(path.is_absolute() and path == path.resolve(strict=False), 'Noncanonical path: ' + str(path))
    for p in (path, *path.parents):
        require(not p.is_symlink(), 'Symlink path: ' + str(p))
    return path


def stable_bytes(path):
    canonical(path)
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), 'Nonregular diagnostic: ' + str(path))
    require(before.st_size <= MAX_FILE, 'Per-file bound exceeded: ' + str(path))
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as f:
        opened = os.fstat(f.fileno())
        require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino), 'File replaced before read')
        data = f.read(MAX_FILE + 1)
        after = os.fstat(f.fileno())
    require((opened.st_size, opened.st_mtime_ns, opened.st_ino) ==
            (after.st_size, after.st_mtime_ns, after.st_ino), 'File changed during read')
    current = path.stat()
    require((current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) ==
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns), 'File changed after read')
    require(len(data) == before.st_size, 'Incomplete diagnostic read')
    return data


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    canonical(root)
    require(root.is_dir(), 'Retained Bee directory Unavailable')
    rows, exclusions, total = [], [], 0
    def walk_error(error):
        raise error
    for parent, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        for name in list(dirs):
            p = Path(parent) / name
            if p.is_symlink():
                exclusions.append({'path':str(p.relative_to(root)), 'kind':'SymlinkDirectoryNotFollowed'})
                dirs.remove(name)
        for name in sorted(files):
            p = Path(parent) / name
            if p.suffix.lower() not in EXTENSIONS:
                continue
            data = stable_bytes(p)
            total += len(data)
            require(len(rows) < MAX_FILES and total <= MAX_TOTAL, 'Diagnostic collection bound exceeded')
            rows.append({'path':str(p.relative_to(root)), 'bytes':len(data), 'sha256':sha(data)})
    return sorted(rows, key=lambda r:r['path']), sorted(exclusions, key=lambda r:r['path'])


def authenticate_original(demo):
    records = []
    for rel, expected_blob in ANCHORS.items():
        data = subprocess.check_output(['git','-C',str(demo),'show',PUBLICATION+':'+CHECKPOINT+'/'+rel])
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == expected_blob,
                'Original I Git anchor mismatch: ' + rel)
        path = I_ROOT / rel.removeprefix('batch/')
        require(stable_bytes(path) == data, 'Retained I anchor differs: ' + str(path))
        records.append({'path':str(path),'gitBlob':expected_blob,'bytes':len(data),'sha256':sha(data)})
    return records


def collect(root, output, protected=()):
    canonical(root); canonical(output)
    require(not output.exists() and output.parent.is_dir(), 'Fresh output with existing parent required')
    for p in (root, *protected):
        canonical(p)
        require(output != p and p not in output.parents and output not in p.parents,
                'Output overlaps protected input')
    rows, exclusions = inventory(root)
    require(rows, 'No selected Bee diagnostics available; no build retry permitted')
    output.mkdir()
    findings = []
    for row in rows:
        data = stable_bytes(root / row['path'])
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Diagnostic changed before copy')
        dest = output / 'files' / row['path']
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as f:
            f.write(data)
        require(sha(dest.read_bytes()) == row['sha256'], 'Copied diagnostic mismatch')
        cursor = 0
        while len(findings) < 100:
            at = data.find(NEEDLE, cursor)
            if at < 0:
                break
            findings.append({'path':row['path'],'offset':at,'sha256':row['sha256'],
                'context':data[max(0,at-256):at+512].decode('utf-8',errors='replace')})
            cursor = at + len(NEEDLE)
    after, excluded_after = inventory(root)
    require(after == rows and exclusions == excluded_after, 'Bee diagnostic inventory changed during collection')
    record = {'kind':'IReadOnlyDebugBeeCollection','result':'CollectedForPrimaryAnalysis',
        'root':str(root),'files':rows,'excluded':exclusions,'diagnosticOccurrences':findings,
        'classification':'Current read-only preserved diagnostic bytes; not original build provenance',
        'originalIResult':'FAIL','buildsRun':0,'unityLaunches':0,'runtimeAcceptance':False}
    with (output/'collection.json').open('x',encoding='utf-8') as f:
        json.dump(record,f,indent=2);f.write('\n')
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--demo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(canonical(a.demo) == WORKSPACE/'hybridclr_demo', 'Use exact owning demo checkout')
    require(canonical(a.output) == OUTPUT, 'Only new J DebugBee destination is authorized')
    anchors = authenticate_original(a.demo)
    record = collect(BEE, a.output, (WORKSPACE,I_ROOT,BASE/'Preflight-R03IRLocal-I-post-H-custody-7f36'))
    require(authenticate_original(a.demo) == anchors, 'Original I anchors changed during collection')
    with (a.output/'original-anchor-bindings.json').open('x',encoding='utf-8') as f:
        json.dump({'publication':PUBLICATION,'anchors':anchors},f,indent=2);f.write('\n')
    print(json.dumps({'result':record['result'],'files':len(record['files']),
                      'occurrences':len(record['diagnosticOccurrences']),'runtimeAcceptance':False}))


if __name__ == '__main__':
    main()
