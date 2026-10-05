"""Exact copied-fixture authority. Does NOT weaken shadow_tools.verify's Git-root rule.

The original M07 byte/ABI/Player verifiers remain authoritative for artifacts.
This separate policy authenticates a source-catalog copy of the owning demo,
explicit generated settings, actual pinned installation and current Git tuple.
It cannot authenticate arbitrary projects or historical retained Player reuse.
"""
import hashlib
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'R03'))
import m07_results as m07
from native_codec_source import CodecSourceContext, read_codec
import r01_failure_results as failure_contract
import r01_early_results as early
import shadow_tools as original
from batch_contract import loads, require, sha
from batch_evidence import write
from fixture_project import POLICY, REPOS, source_catalog, source_pins, verify_sources
from run_local import git

PIN_NAMES = ('demo', 'hybridclr', 'hybridclrUnity', 'il2cppPlus')
DIR_NAMES = ('hybridclr_demo', 'hybridclr', 'hybridclr_unity', 'il2cpp_plus')


def authenticate_copy(batch, config):
    project = Path(config['projectPath'])
    require(project == batch.root / 'projects/resource-complete' and project == project.resolve(strict=True), 'Exact batch-owned resource project')
    require(config['kind'] == POLICY and config['schemaVersion'] == 1 and config['owningDemoCommit'] == batch.pins['hybridclr_demo'], 'Copy authority source revision')
    require(all(config.get(k) is False for k in ('expansionAuthorized', 'R03Accepted', 'H2Passed')), 'No authority flag promotion')
    require(loads((project / '.r03-completion-project').read_text()) == config, 'Original marker changed')
    require(config['files'] == source_catalog(batch.workspace / 'hybridclr_demo', batch.pins['hybridclr_demo']), 'Copied inventory differs from actual committed source selection')
    pin_path = project / original.PINS
    pins = loads(pin_path.read_text())
    require(pins == source_pins(batch, project), 'Exact four-project pins and relative owners required')
    for name in DIR_NAMES:
        root = batch.workspace / name
        require(Path(git(root, 'rev-parse', '--show-toplevel')).resolve() == root, 'Canonical owning Git root')
        require(git(root, 'rev-parse', 'HEAD') == batch.pins[name] and git(root, 'branch', '--show-current') == batch.pins['branch'], 'Owning HEAD/branch changed')
        require(not git(root, 'status', '--porcelain=v1', '--untracked-files=all'), 'Owning repository is dirty')
        remote = git(root, 'config', '--get', 'remote.origin.url')
        full = 'night-outlook/' + name
        require(remote in ('git@github.com:' + full + '.git', 'https://github.com/' + full, 'https://github.com/' + full + '.git'), 'Canonical origin required')
        require(git(root, 'ls-remote', 'origin', 'refs/heads/' + batch.pins['branch']).split()[0] == batch.pins[name], 'Owning remote authority changed')
    verify_sources(project, config, configured=True)
    # Ignored compiled-source injection must not evade Git status or copying.
    allowed = {r['path'] for r in config['files']}
    generated = {'Assets/HybridCLRGenerate/AOTGenericReferences.cs'}
    for folder in ('Assets',):
        for path in (project / folder).rglob('*'):
            require(not path.is_symlink(), 'Symlink in fixture source tree')
            if path.is_file() and path.suffix in ('.cs', '.asmdef', '.asmref', '.dll'):
                relative = path.relative_to(project).as_posix()
                require(relative in allowed or relative in generated, 'Unbound source in fixture: ' + relative)
    return project, pins


def verify_native_inventory(installed, pins, paths):
    """Uses original source_inventory and identical four-file generation policy."""
    installed = Path(installed)
    for parent in (installed, *installed.parents):
        require(not parent.is_symlink(), 'Symlinked installed root')
    expected = original.source_inventory(pins, paths)
    receipt_path = installed / original.RECEIPT
    receipt = loads(receipt_path.read_text())
    require(receipt.get('schemaVersion') == 1 and receipt.get('installMode') == 'PinnedLocal', 'Pinned installation receipt')
    require(receipt.get('unityVersion') == pins['unityVersion'] == '2022.3.62f2' and
            receipt.get('target') == pins['target'] == 'StandaloneOSX', 'Pinned installation platform')
    for name in PIN_NAMES:
        require(all(receipt.get('repositories', {}).get(name, {}).get(k) == pins[name][k] for k in ('url', 'revision', 'localPath')), 'Installation tuple differs: ' + name)
    package = loads((paths['hybridclrUnity'] / 'package.json').read_text())
    require(package['name'] == original.PACKAGE and receipt['packageRevision'] == pins['hybridclrUnity']['revision'] and
            receipt['packageVersion'] == package['version'], 'Package identity/version')
    exclusions = receipt.get('generatedFileExclusions')
    require(type(exclusions) is list and len(exclusions) == len(original.GENERATED) and set(exclusions) == original.GENERATED, 'Exact generated native exclusions')
    observed = {}
    for row in receipt['sourceFileHashes']:
        original.safe_file(installed, row['path'])
        require(row['path'] not in observed, 'Duplicate native source record')
        observed[row['path']] = {'source': row['source'], 'sha256': row['sha256']}
    require(observed == expected, 'Exact pinned native source inventory')
    actual = original.files_under(installed)
    require(actual == set(expected) | original.GENERATED | {original.RECEIPT}, 'Unexpected installed native files')
    for relative, entry in expected.items():
        if relative not in original.GENERATED:
            require(sha(installed / relative) == entry['sha256'], 'Installed native source changed: ' + relative)
    header = (installed / 'AssemblyShadowConfig.h').read_text()
    require(receipt.get('defaultShadowMacro') == 0 and receipt.get('defaultShadowMacroSource') == 'AssemblyShadowConfig.h' and
            re.search(r'(?m)^\s*#define\s+HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\s+0\s*$', header) and
            re.search(r'(?m)^\s*#ifndef\s+HYBRIDCLR_ENABLE_ASSEMBLY_SHADOW\s*$', header) and
            '#include "AssemblyShadowConfig.h"' in (installed / 'il2cpp-config.h').read_text(), 'Default OFF retained')
    return {'kind': 'R03ResourceInstalledSourceBinding', 'policy': POLICY, 'installedNativeRoot': str(installed),
            'receiptSha256': sha(receipt_path), 'sourceFiles': len(expected), 'installedFiles': len(actual),
            'generatedHashes': {p: sha(installed / p) for p in sorted(original.GENERATED)},
            'sourcePins': pins, 'probeEnabled': False, 'expansionAuthorized': False}


def verify_installation(batch, config):
    project, pins = authenticate_copy(batch, config)
    paths = {key: batch.workspace / name for key, name in zip(PIN_NAMES, DIR_NAMES)}
    installed = project / 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp'
    result = verify_native_inventory(installed, pins, paths)
    dependencies = loads((project / 'Packages/manifest.json').read_text())['dependencies']
    require(Path(dependencies[original.PACKAGE][5:]).resolve() == paths['hybridclrUnity'], 'UPM package source mismatch')
    require(dependencies['com.unity.render-pipelines.universal'] == '14.0.12', 'Original URP version')
    arguments = re.search(r'(?m)^  additionalIl2CppArgs:([^\n]*)$', (project / 'ProjectSettings/ProjectSettings.asset').read_text())
    require(arguments and 'HYBRIDCLR_R03_RUNTIME_PROBE' not in arguments[1] and 'R03_RUNTIME_PROBE' not in arguments[1], 'Resource/measurement profile must not use finalizer isolation')
    overrides = [value.rstrip("\"'") for value in re.findall(r'-DHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW=(\S+)', arguments[1])]
    require(overrides == ['1'] and '-UHYBRIDCLR_ENABLE_ASSEMBLY_SHADOW' not in arguments[1], 'Resource source project restored to ON')
    # Input graph/receipt hashes bind all flags used for EACH actual ON/OFF build;
    # current settings alone are not proof of historical compilation arguments.
    result['projectAuthoritySha256'] = sha(project / '.r03-completion-project')
    return result


def verify_graph(batch, config, fixture_path, on_path, off_path, replay_path):
    installed = verify_installation(batch, config)
    project = Path(config['projectPath']); pins = loads((project / original.PINS).read_text())
    codec_context = CodecSourceContext(project, batch.workspace / 'hybridclr', batch.pins['hybridclr'])
    graph = loads(Path(fixture_path).read_text())
    baseline_path = Path(graph['baselineManifestPath'])
    require(baseline_path.is_relative_to(project) and sha(baseline_path) == graph['baselineManifestSha256'], 'Current baseline codec authority')
    baseline_value = loads(baseline_path.read_text())
    profile = baseline_value['metadataEncodingProfile2']
    _, codec_receipt = read_codec(baseline_value['sourcePins']['hybridclr'], profile['nativeSourceRevision'],
                                 profile['nativeCodecHeaderSha256'], codec_context)
    write(batch.root / 'native-codec-source-verification.json', codec_receipt)
    manifest, baseline, fixtures, rejected, resources = m07.verify_inputs(fixture_path, source_context=codec_context)
    m07.exact(baseline['sourcePins'], pins, 'R03 resource baseline current tuple')
    m07.prepare_fixture_resources(manifest, baseline, fixtures, resources)
    on = m07.verify_player(on_path, manifest, baseline, resources, 'NativeOn')
    off = m07.verify_player(off_path, manifest, baseline, resources, 'NativeOff')
    for mode, build in (('NativeOn', on), ('NativeOff', off)):
        m07.exact(build['snapshot']['sourcePins'], pins, mode + ' exact tuple')
        require(build['output'].is_relative_to(project / 'Builds/AssemblyShadow/M07'), 'App escapes fresh resource project')
        require('R03_RUNTIME_PROBE' not in build['player']['nativeArguments'], 'No lease profile in M07/R00')
    for key in ('inputSnapshotHash', 'nativeLibrarySha256', 'buildGuid'):
        require(on['player'][key] != off['player'][key], 'Fresh distinct ON/OFF: ' + key)
    m07.exact(m07.managed_player_inputs(on['snapshot'], on['path']), m07.managed_player_inputs(off['snapshot'], off['path']), 'Exact paired managed ON/OFF inputs')
    m07.exact(on['path'], Path(manifest['playerBuildReceiptPath']), 'Manifest ON receipt')
    m07.exact(sha(on['path']), manifest['playerBuildReceiptSha256'], 'Manifest ON receipt hash')
    m07.verify_replay(replay_path, manifest, baseline, fixtures, rejected, on, resources)
    m07.exact(loads(Path(replay_path).read_text())['validatorSourcePins'], pins, 'Editor replay source tuple')
    context = {'manifest': manifest, 'baseline': baseline, 'fixtures': fixtures, 'on': on, 'off': off,
               'sourcePins': pins, 'currentSourcePins': pins, 'installed': installed}
    profile = failure_contract.metadata_profile(context, 'R03 source-bound early startup')
    require(profile == 2, 'Current profile-2 baseline; do not fallback to historical late startup')
    runner = early._load_runner()
    inventory = runner.collect_inputs(fixture_path, replay_path, (on_path, off_path))
    inventory.update({project / '.r03-completion-project', project / original.PINS})
    return {'codecContext': codec_context, 'context': context, 'profile': profile, 'runner': runner, 'inventory': inventory,
            'failures': None, 'baselineResources': resources, 'rejected': rejected}
