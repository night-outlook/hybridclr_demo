"""Read one immutable historical archive; never execute or stage recovered bytes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

ARCHIVE = 'Docs/AssemblyShadow/History/M07R/H1/local-validation-20260919-authority925e/raw-evidence.tar.gz'
ARCHIVE_SHA = '2ecb3d04cdd093c469717d4c2959ec416ec8d0745c51c2a4ba37c82f9bc253e8'
IMAGE_SHA = '9108a2396fd1a292a1446a96b6e61ac19108fd930d8d2b70edb4c3af72780e27'


def export(project, output, verify_committed=False):
    if output.exists():
        raise ValueError('Unused output required')
    output.mkdir(parents=True)
    archive = project / ARCHIVE
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA:
        raise ValueError('Historical archive hash mismatch')
    result = dict(kind='R02M00FixtureSearch', archive=ARCHIVE, archiveSha256=digest,
                  frozenSha256=IMAGE_SHA, matches=[], ordinaryMembers=[], runtimeAcceptance=False)
    seen = set(); total = 0
    with tarfile.open(archive, 'r|gz') as stream:
        for member in stream:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or '\\' in member.name or member.name in seen:
                raise ValueError('Unsafe or duplicate member')
            if not (member.isfile() or member.isdir()):
                raise ValueError('Non-regular archive member')
            seen.add(member.name); total += member.size
            if len(seen) > 50000 or member.size < 0 or member.size > 256*1024*1024 or total > 2*1024**3:
                raise ValueError('Archive bounds exceeded')
            if not member.isfile():
                continue
            data = stream.extractfile(member).read()
            sha = hashlib.sha256(data).hexdigest()
            if 'AssemblyShadowBaseline.HotUpdate' in member.name:
                result['ordinaryMembers'].append(dict(member=member.name, sha256=sha, sizeBytes=len(data)))
            if sha == IMAGE_SHA:
                result['matches'].append(dict(member=member.name, sha256=sha, sizeBytes=len(data)))
                dest = output / 'frozen-m00.dll'
                if dest.exists() and dest.read_bytes() != data:
                    raise ValueError('Conflicting matching image')
                if not dest.exists():
                    dest.write_bytes(data)
    result.update(memberCount=len(seen), totalBytes=total,
                  result='FrozenFixtureRecovered' if result['matches'] else 'CompletedNoMatchingFixture')
    if verify_committed:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from ordinary_input import fixture, MEMBER
        fixed, encoded, origin, _ = fixture(project)
        if not any(row['member'] == MEMBER for row in result['matches']):
            raise ValueError('Pinned historical member was not recovered')
        if (output / 'frozen-m00.dll').read_bytes() != fixed:
            raise ValueError('Committed compact fixture differs from immutable archive')
        result.update(result='FrozenFixtureOriginVerified', compactFixture=encoded,
                      origin=origin, historicalPlayerExecutionReused=False)
    (output / 'search.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--verify-committed', action='store_true')
    args = parser.parse_args()
    export(args.project.resolve(strict=True), args.output.resolve(), args.verify_committed)
