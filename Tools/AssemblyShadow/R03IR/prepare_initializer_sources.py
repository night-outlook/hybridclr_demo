#!/usr/bin/env python3
"""Add initializer test sources to a NEW already-isolated R03 project copy.

No Unity build, Player launch, historic fixture modification or Local authority.
The current runner must separately authenticate the four Git pins and the
resulting BuildReport/executable before using these sources.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANAGED = HERE / 'PlayerProject/R03InitializerObservationPlayer.cs'
ADDITIONS = (HERE / 'PlayerProject/R03InitializerPreparedProbe.cpp',
             HERE / 'PlayerProject/R03InitializerObservationWriter.cpp')
EXISTING = ('R03TerminalPlayer.cs', 'R03EngineFrameDispatcher.cs')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    def unique(items):
        out = {}
        for name, value in items:
            need(name not in out, 'Duplicate JSON key: ' + name)
            out[name] = value
        return out
    data = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)
    need(type(data) is dict, 'JSON object required')
    return data


def new_bytes(path, data):
    with Path(path).open('xb') as out:
        out.write(data)


def prepare(project, config_path, dest):
    project, config_path, dest = map(Path, (project, config_path, dest))
    need(all(p.is_absolute() for p in (project, config_path, dest)),
         'Absolute isolated paths required')
    need(project.is_dir() and not project.is_symlink() and
         (project / '.r03-isolated-project').is_file(), 'Fresh isolated project required')
    need(config_path.is_file() and not config_path.is_symlink() and
         not dest.exists() and not dest.is_relative_to(project) and
         not project.is_relative_to(dest), 'Unused external output required')
    manifest_path = project / 'source-inputs.json'
    record, config = read_json(manifest_path), read_json(config_path)
    need(config.get('schemaVersion') == 1 and config.get('projectPath') == str(project) and
         config.get('sourceManifestSha256') == sha(manifest_path.read_bytes()),
         'Coherent existing project/config')
    files = record.get('files')
    need(record.get('schemaVersion') == 1 and type(files) is list, 'Typed source manifest')
    mapped = {x['path']: x for x in files}
    need(len(mapped) == len(files) and
         all('Assets/' + n in mapped and
             (project / ('Assets/' + n)).is_file() and
             mapped['Assets/' + n]['sha256'] == sha(
                 (project / ('Assets/' + n)).read_bytes()) for n in EXISTING),
         'Two intact existing IR Player source inputs')
    old_overlay = Path(config.get('overlayPath', ''))
    need(old_overlay.is_absolute() and old_overlay.is_file() and
         not old_overlay.is_symlink() and
         old_overlay.name == 'AssemblyShadowR03Probe.cpp' and
         config.get('overlaySha256') == sha(old_overlay.read_bytes()),
         'Pinned preexisting native diagnostic overlay')
    name = 'Assets/R03InitializerObservationPlayer.cs'
    target = project / name
    need(name not in mapped and not target.exists() and
         MANAGED.is_file() and all(p.is_file() for p in ADDITIONS),
         'No previous initializer source or missing new inputs')
    original = old_overlay.read_bytes()
    concat = original + b''.join(
        b'\n// Source-bound separate initializer part: ' + p.name.encode() + b'\n' +
        p.read_bytes() for p in ADDITIONS)
    need(concat.startswith(original) and len(concat) > len(original),
         'Composite overlay must preserve original as exact prefix')
    dest.mkdir(parents=True)
    combined_path = dest / 'R03InitializerCompositeOverlay.cpp'
    new_bytes(combined_path, concat)
    managed_bytes = MANAGED.read_bytes()
    new_bytes(target, managed_bytes)
    files.append({'path': name, 'sha256': sha(managed_bytes),
        'origin': {'kind': 'R03InitializerPrimarySource',
                   'source': str(MANAGED), 'runtimeAcceptance': False}})
    new_manifest = (json.dumps(record, indent=2, sort_keys=True) + '\n').encode()
    manifest_path.write_bytes(new_manifest)
    config['overlayPath'] = str(combined_path)
    config['overlaySha256'] = sha(concat)
    config['sourceManifestSha256'] = sha(new_manifest)
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + '\n',
                           encoding='utf-8')
    receipt = {'schemaVersion': 1, 'kind': 'R03InitializerSourcePreparationV1',
        'result': 'PreparedSourcesOnly_NoUnityOrPlayer',
        'project': str(project), 'configuration': str(config_path),
        'managedSourceSha256': sha(managed_bytes),
        'originalOverlaySha256': sha(original),
        'compositeOverlaySha256': sha(concat),
        'nativePartsSha256': {p.name: sha(p.read_bytes()) for p in ADDITIONS},
        'manifestSha256': sha(new_manifest), 'unityBuildExecuted': False,
        'playerExecuted': False, 'runtimeAcceptance': False,
        'R03Accepted': False, 'H2Passed': False}
    new_bytes(dest / 'SOURCE_PREPARATION.json',
              (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('project', 'config', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.project, args.config, args.output), sort_keys=True))


if __name__ == '__main__':
    main()
