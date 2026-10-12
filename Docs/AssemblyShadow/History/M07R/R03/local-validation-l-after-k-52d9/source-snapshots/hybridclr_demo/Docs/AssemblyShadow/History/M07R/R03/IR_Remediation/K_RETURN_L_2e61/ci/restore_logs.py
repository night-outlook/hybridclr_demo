#!/usr/bin/env python3
"""Verify and optionally restore the two original CI logs; never overwrite files."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional fresh external directory')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    spec = json.loads((root / 'LOG_STORAGE.json').read_text())
    base = spec['base']; mac = spec['macos']
    compressed = (root / base['path']).read_bytes()
    digest = lambda data: hashlib.sha256(data).hexdigest()
    require(len(compressed) == base['compressedBytes'] and digest(compressed) == base['compressedSha256'], 'Compressed log identity')
    ubuntu = gzip.decompress(compressed)
    require(len(ubuntu) == base['originalBytes'] and digest(ubuntu) == base['originalSha256'], 'Original Ubuntu log identity')
    old = mac['oldUtf8'].encode('utf-8'); new = mac['newUtf8'].encode('utf-8')
    require(ubuntu.count(old) == mac['expectedOccurrences'] == 1, 'Unique original elapsed-time line')
    macos = ubuntu.replace(old, new, 1)
    require(len(macos) == mac['originalBytes'] and digest(macos) == mac['originalSha256'], 'Original macOS log identity')
    if args.output is not None:
        output = args.output
        require(output.is_absolute() and output == output.resolve(strict=False), 'Canonical absolute output')
        require(not output.exists() and not output.is_symlink() and output.parent.is_dir(), 'Fresh output with existing parent')
        require(root != output and root not in output.parents and output not in root.parents, 'Output outside stored evidence')
        output.mkdir()
        for name, data in (('ubuntu-host.log', ubuntu), ('macos-host.log', macos)):
            with (output / name).open('xb') as stream:
                stream.write(data)
    print(json.dumps({'result':'OriginalBytesVerified','bytesEach':len(ubuntu),'ubuntuSha256':digest(ubuntu),'macosSha256':digest(macos),'runtimeAcceptance':False}))


if __name__ == '__main__':
    main()
