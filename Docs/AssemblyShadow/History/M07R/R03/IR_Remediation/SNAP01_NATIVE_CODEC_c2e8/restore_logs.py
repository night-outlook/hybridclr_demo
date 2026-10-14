#!/usr/bin/env python3
"""Restore six exact original CI text logs into a fresh caller-owned directory."""
import argparse
import hashlib
import json
from pathlib import Path

NAMES = {f'{host}/{profile}.log' for host in ('macos', 'linux-clang', 'linux-gcc')
         for profile in ('strict', 'sanitized')}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path,
                        default=Path(__file__).with_name('RETAINED_LOGS.json'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    require(args.manifest.stat().st_size <= 65536, 'manifest byte limit')
    doc = json.loads(args.manifest.read_bytes())
    require(doc['kind'] == 'ExactOriginalNativeCodecCILogs' and
            doc['sourceCommit'] == '8120ca91c0c762b8b29f703f087ab1bfdaf0f532' and
            doc['runId'] == 38529319047 and doc['encoding'] == 'common-prefix-utf8', 'source identity')
    require(type(doc['files']) is list and len(doc['files']) == 6, 'complete inventory')
    seen, decoded = set(), []
    for row in doc['files']:
        name = row['path']
        require(name in NAMES and name not in seen, 'invalid/duplicate log path')
        seen.add(name)
        require(type(row['bytes']) is int and 0 < row['bytes'] <= 16384, 'log length')
        require(isinstance(doc['prefix'], str) and isinstance(row['suffix'], str), 'log text')
        data = (doc['prefix'] + row['suffix']).encode('utf-8')
        require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],
                'original log size/hash mismatch')
        require('Ran 20 tests' in data.decode('utf-8') and data.endswith(b'\nOK\n'),
                'unexpected original test log')
        decoded.append((name, data))
    require(seen == NAMES, 'missing log')
    out = args.output
    require(out.is_absolute() and out == out.resolve(strict=False) and
            out.parent.is_dir() and not out.exists() and not out.is_symlink(),
            'fresh canonical directory required')
    out.mkdir()
    for name, data in decoded:
        target = out / name
        target.parent.mkdir(exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
    print('Verified/restored six original logs; no Unity or runtime validation performed.')

if __name__ == '__main__':
    main()
