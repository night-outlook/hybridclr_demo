"""Authenticate the retained 33543 failure fixture for read-only CI diagnosis.

No native compilation, archive path extraction, acceptance, or Git writes.
The complete source graph and header/PCH inputs remain available for Primary
review; the text census is only a navigation aid, never a domain policy.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

ARCHIVE = 'Docs/AssemblyShadow/Evidence/fixtures/fresh-smoke-failure-inputs.tar.gz'
EXPECTED = 'e3549743a39b44e865a6015f1f16ed151cb47c038d0542d351d3622d8a5e54d8'
GRAPH = 'dbf1deae4c537fed4c9da57b942d14fb9c1823f5e40dc077a66914648a3be181'


def export(root: Path, output: Path) -> None:
    raw = (root / ARCHIVE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED:
        raise ValueError('Failure archive identity changed')
    output.mkdir(parents=True, exist_ok=False)
    members, seen, total, graphs = [], set(), 0, []
    with tarfile.open(root / ARCHIVE, 'r|gz') as archive:
        for item in archive:
            path = PurePosixPath(item.name)
            if (path.is_absolute() or '..' in path.parts or '\\' in item.name
                    or item.name in seen or not (item.isfile() or item.isdir())):
                raise ValueError('Unsafe or duplicate member')
            seen.add(item.name)
            total += item.size
            if len(seen) > 10000 or item.size < 0 or item.size > 64*1024*1024 or total > 512*1024*1024:
                raise ValueError('Archive bounds exceeded')
            if item.isdir():
                continue
            with archive.extractfile(item) as stream:
                data = stream.read(64*1024*1024+1)
            if len(data) != item.size:
                raise ValueError('Truncated member')
            digest = hashlib.sha256(data).hexdigest()
            members.append({'member': item.name, 'sha256': digest, 'bytes': len(data)})
            target = output / 'members' / digest
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
            elif target.read_bytes() != data:
                raise ValueError('Digest collision')
            if digest == GRAPH:
                graphs.append(item.name)
                (output / 'bee-action-graph.json').write_bytes(data)
    if not graphs:
        raise ValueError('Pinned raw graph is absent')
    index = {'archiveSha256': EXPECTED, 'graphSha256': GRAPH, 'matchingMembers': graphs,
             'files': members, 'macroPolicyApproved': False, 'humanGatePassed': False, 'mayEnterR02': False}
    (output / 'fixture-index.json').write_text(json.dumps(index, indent=2)+'\n')
    graph = json.loads((output / 'bee-action-graph.json').read_text())
    nodes = graph['Nodes']
    print('AUTHENTICATED', json.dumps({'members': len(members), 'graphNodes': len(nodes), 'sha256': GRAPH}))
    for i, node in enumerate(nodes):
        annotation = str(node.get('Annotation', ''))
        if annotation.startswith('C_Mac_arm64'):
            action = node.get('Action', '')
            if '-DIL2CPP_DEBUG=1' not in action or annotation.startswith('C_Mac_arm64Pch'):
                print('ACTION', i, json.dumps(node, separators=(',', ':')))
        elif annotation.startswith('Link_Mac_arm64'):
            print('LINK', i, json.dumps(node, separators=(',', ':')))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(args.project, args.output)
