"""New original-resource project with exact source bytes; no historical app reuse."""
import hashlib
import os
from pathlib import Path
import shutil
import sys
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'R03'))
from batch_contract import loads, require, sha
from batch_evidence import write
from run_local import REPOS, git
from source_pin_contract import validate_document

POLICY = 'R03ResourceCompleteFixtureV1'
ROOTS = ('Assets/AssemblyShadowDemo', 'Assets/AssemblyShadowBaseline',
         'Assets/AssemblyShadowR01BDiagnostics', 'Assets/AssemblyShadowH1Baselines',
         'Assets/StreamingAssets/AssemblyShadow/M00')
SETTINGS = ('ProjectSettings/ProjectSettings.asset', 'ProjectSettings/ProjectVersion.txt',
            'ProjectSettings/HybridCLRSettings.asset', 'ProjectSettings/AssemblyShadowSettings.asset',
            'ProjectSettings/AssemblyShadowDependencies.json', 'ProjectSettings/AssemblyShadowExtensibilityWhitelist.json',
            'ProjectSettings/AssemblyShadowResourcesM07.json', 'ProjectSettings/AssemblyShadowResources.json',
            'ProjectSettings/AssemblyShadowReflectionBindings.json')
FROZEN = {
 'Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab': '935501089fc7a6a1c61d1ac2e676340b429d3062',
 'Assets/AssemblyShadowDemo/ResourcesSource/VersionedPrefab.prefab.meta': 'ac9a053cd5dcff06cfc511efba019f5a967dfa3b',
 'Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset': 'fad193a9e32ad4e6585a322812b6c11c9df03c04',
 'Assets/AssemblyShadowDemo/ResourcesSource/VersionedData.asset.meta': '16988ee07bf11c6a6fa618fbb65c5d2215c8e44f',
 'Assets/AssemblyShadowDemo/Scenes/Business.unity': 'b771cc6e0b401c50daeab877281f2f53d9ee43a0',
 'Assets/AssemblyShadowDemo/Scenes/Business.unity.meta': 'e3959ef1e1b84bbc1146e72fff3bb4ce2dd3839d',
}
# Production entry points write these in the new isolated project only. Their
# original/configured bytes and exact phase receipts remain external evidence.
MUTABLE = frozenset(('Assets/HybridCLRGenerate/link.xml', 'ProjectSettings/ProjectSettings.asset',
                    'ProjectSettings/HybridCLRSettings.asset', 'ProjectSettings/AssemblyShadowSettings.asset',
                    'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity',
                    'Assets/AssemblyShadowDemo/Scenes/M07Bootstrap.unity.meta'))


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def regular(path):
    path = Path(path)
    require(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)), 'Expected regular source file: ' + str(path))
    return path


def select(name):
    return name in SETTINGS or name in ('Assets/HybridCLRGenerate/link.xml', 'Assets/HybridCLRGenerate/link.xml.meta') or any(name == root + '.meta' or name.startswith(root + '/') for root in ROOTS)


def source_catalog(demo, expected_commit=None):
    if expected_commit:
        require(git(demo, 'rev-parse', 'HEAD') == expected_commit, 'Copied-source commit changed')
    rows = []
    for line in git(demo, 'ls-tree', '-r', '--full-tree', 'HEAD').splitlines():
        mode, kind, rest = line.split(' ', 2); oid, name = rest.split('\t', 1)
        if not select(name):
            continue
        require(mode == '100644' and kind == 'blob', 'Unsupported resource source entry: ' + name)
        data = regular(Path(demo) / name).read_bytes()
        require(blob(data) == oid, 'Source differs from exact commit: ' + name)
        rows.append({'path': name, 'blob': oid, 'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)})
    require(set(SETTINGS) <= {r['path'] for r in rows}, 'Required original project configuration missing')
    for path, expected in FROZEN.items():
        require(any(r['path'] == path and r['blob'] == expected for r in rows), 'Original M01 asset changed: ' + path)
    require(any(r['path'].endswith('/R03CompletionBuild.cs') for r in rows), 'Complete Primary build adapter is required')
    return sorted(rows, key=lambda row: row['path'])


def dependencies(demo, package):
    manifest = loads(regular(Path(demo) / 'Packages/manifest.json').read_text())
    require(manifest['dependencies']['com.unity.render-pipelines.universal'] == '14.0.12', 'Original URP version changed')
    result = {k: v for k, v in manifest['dependencies'].items()
              if k.startswith('com.unity.modules.') or k in ('com.unity.ugui', 'com.unity.test-framework', 'com.unity.render-pipelines.universal')}
    locked = loads(regular(Path(demo) / 'Packages/packages-lock.json').read_text())['dependencies']
    require(locked['com.unity.nuget.newtonsoft-json']['version'] == '3.2.1', 'Original JSON parser dependency changed')
    result['com.unity.nuget.newtonsoft-json'] = '3.2.1'
    result['com.code-philosophy.hybridclr'] = 'file:' + str(package)
    return {'dependencies': result, 'testables': ['com.code-philosophy.hybridclr']}


def source_pins(batch, project):
    names = {'hybridclr': 'hybridclr', 'hybridclr_unity': 'hybridclrUnity', 'il2cpp_plus': 'il2cppPlus', 'hybridclr_demo': 'demo'}
    pins = {'schemaVersion': 1, 'unityVersion': '2022.3.62f2', 'target': 'StandaloneOSX', 'architecture': 'arm64'}
    for name in REPOS:
        pins[names[name]] = {'url': 'https://github.com/night-outlook/' + name + '.git',
                            'revision': batch.pins[name], 'localPath': os.path.relpath(batch.workspace / name, project)}
    return pins


def provision(batch):
    project = batch.root / 'projects/resource-complete'
    require(not project.exists() and project.parent == batch.root / 'projects', 'New isolated project required')
    rows = source_catalog(batch.workspace / 'hybridclr_demo', batch.pins['hybridclr_demo'])
    project.mkdir(parents=True)
    for row in rows:
        dest = project / row['path']; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(batch.workspace / 'hybridclr_demo' / row['path'], dest)
        require(sha(dest) == row['sha256'], 'Copy mismatch: ' + row['path'])
    write(project / 'Packages/manifest.json', dependencies(batch.workspace / 'hybridclr_demo', batch.workspace / 'hybridclr_unity'))
    write(project / 'ProjectSettings/AssemblyShadowSourcePins.json', validate_document(source_pins(batch, project), batch, project))
    config = {'schemaVersion': 1, 'kind': POLICY, 'projectPath': str(project), 'owningDemoCommit': batch.pins['hybridclr_demo'],
              'baselineId': 'M07-Baseline-R03Completion-' + batch.pins['hybridclr_demo'][:12],
              'runPath': str(project / ('_temp/AssemblyShadow/M02Validation-' + uuid.uuid4().hex)),
              'receiptRoot': str(project / '_temp/AssemblyShadow/R03CompletionArtifacts'),
              'repositories': {n: batch.pins[n] for n in REPOS}, 'files': rows,
              'resourceMapSha256': sha(project / 'ProjectSettings/AssemblyShadowResourcesM07.json'),
              'sourcePinsSha256': sha(project / 'ProjectSettings/AssemblyShadowSourcePins.json'),
              'packagesManifestSha256': sha(project / 'Packages/manifest.json'),
              'R03Accepted': False, 'H2Passed': False, 'expansionAuthorized': False}
    write(project / '.r03-completion-project', config)
    (project / '.r03-isolated-project').write_text(POLICY + '\n')
    return project, config


def verify_sources(project, config, *, configured=False):
    require(Path(config['projectPath']) == project and config['kind'] == POLICY, 'Project ownership')
    changes = []
    for row in config['files']:
        observed = sha(regular(project / row['path']))
        if observed != row['sha256']:
            require(configured and row['path'] in MUTABLE, 'Unexpected original fixture source mutation: ' + row['path'])
            changes.append({'path': row['path'], 'originalSha256': row['sha256'], 'configuredSha256': observed})
    for path, oid in FROZEN.items():
        require(blob(regular(project / path).read_bytes()) == oid, 'Frozen M01 bytes/GUID changed')
    require(sha(project / 'Packages/manifest.json') == config['packagesManifestSha256'] and
            sha(project / 'ProjectSettings/AssemblyShadowSourcePins.json') == config['sourcePinsSha256'], 'Immutable project pins')
    return {'kind': POLICY, 'filesVerified': len(config['files']), 'allowedConfigurationChanges': changes,
            'frozenM01Files': len(FROZEN), 'newResourceBundlesRequired': True, 'runtimeAcceptance': False}
