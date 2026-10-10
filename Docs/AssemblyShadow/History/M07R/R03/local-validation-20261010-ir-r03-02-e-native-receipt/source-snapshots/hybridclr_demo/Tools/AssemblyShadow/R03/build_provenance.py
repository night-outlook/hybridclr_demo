"""R03 build receipt v2: explicit installed SDK identity, never recursive discovery.

Generated projects may contain byte-identical receipt copies. Their existence is
not an ambiguity in the producer-selected installed root. This module verifies
that root, its exact contents and source tuple; it never deletes copied evidence.
"""
import os
from pathlib import Path, PurePosixPath
import re

from batch_contract import loads, require, sha

RECEIPT_VERSION = 2
POLICY = 'R03InstalledNativeRootV1'
# Independently checked against the pinned package's SettingsUtil.cs. This is
# the supported OSXEditor profile, not a guessed directory-search preference.
NATIVE_RELATIVE = 'HybridCLRData/LocalIl2CppData-OSXEditor/il2cpp/libil2cpp'
INSTALL_FILE = 'assembly-shadow-install.json'
OVERLAY = 'vm/AssemblyShadowR03Probe.cpp'
GENERATED = frozenset(('hybridclr/generated/AssemblyManifest.cpp', 'hybridclr/generated/MethodBridge.cpp',
                       'hybridclr/generated/UnityVersion.h', 'hybridclr/generated/libil2cpp-version.txt'))
SOURCE_KEYS = {'hybridclr': 'hybridclr', 'hybridclrUnity': 'hybridclr_unity',
               'il2cppPlus': 'il2cpp_plus', 'demo': 'hybridclr_demo'}
ROLES = frozenset(('candidate-release', 'reference-release', 'candidate-debug', 'candidate-off'))


def canonical_path(value, *, directory):
    require(isinstance(value, (str, Path)) and bool(str(value)), 'Explicit path required')
    path = Path(value)
    require(path.is_absolute() and str(path) == str(value) and '..' not in path.parts,
            'Absolute canonical path required: ' + str(value))
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'Linked path refused: ' + str(path))
    require(path.is_dir() if directory else path.is_file(), 'Missing path: ' + str(path))
    require(path.resolve(strict=True) == path, 'Noncanonical path refused: ' + str(path))
    return path


def inventory_entries(entries):
    require(type(entries) is list and entries, 'A nonempty exact inventory is required')
    result = {}
    for entry in entries:
        require(type(entry) is dict and set(entry) == {'path', 'sha256', 'size'}, 'Invalid inventory entry')
        name = entry['path']
        require(type(name) is str and name and '\\' not in name and '\0' not in name,
                'Unsafe inventory path')
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and str(path) == name and name != '.',
                'Noncanonical inventory path: ' + name)
        require(name not in result, 'Duplicate inventory path: ' + name)
        require(type(entry['size']) is int and entry['size'] >= 0, 'Invalid file size')
        require(type(entry['sha256']) is str and re.fullmatch('[0-9a-f]{64}', entry['sha256']), 'Invalid file hash')
        result[name] = entry
    return result


def verify_inventory(root, entries):
    root = canonical_path(root, directory=True)
    expected = inventory_entries(entries)
    actual = {}
    def error(exc):
        raise exc  # os.walk must not silently omit an unreadable directory.
    for directory, directories, files in os.walk(root, followlinks=False, onerror=error):
        base = Path(directory)
        for name in directories:
            require(not (base / name).is_symlink(), 'Linked inventory directory refused: ' + str(base / name))
        for name in files:
            path = canonical_path(base / name, directory=False)
            actual[path.relative_to(root).as_posix()] = path
    require(set(actual) == set(expected), 'Exact file membership: ' + str(root))
    for name, path in actual.items():
        require(path.stat().st_size == expected[name]['size'] and sha(path) == expected[name]['sha256'],
                'File changed: ' + name)
    return len(actual)


def verify_installation(receipt, project, batch_root, repositories):
    """Return an authenticated binding; old v1 receipts are never auto-upgraded."""
    require(type(receipt.get('schemaVersion')) is int and receipt['schemaVersion'] == RECEIPT_VERSION and
            receipt.get('kind') == 'R03IsolatedPlayerBuild', 'Explicit build receipt v2 required')
    batch_root = canonical_path(batch_root, directory=True)
    project = canonical_path(project, directory=True)
    require(project.parent == batch_root / 'projects' and project.name in ROLES,
            'Installed SDK must belong to this batch and role')
    require(receipt['projectPath'] == str(project), 'Producer/project binding mismatch')
    canonical_path(project / '.r03-isolated-project', directory=False)
    native = canonical_path(receipt.get('installedNativeRoot'), directory=True)
    require(native == project / NATIVE_RELATIVE, 'Installed SDK root/profile mismatch')
    install_path = canonical_path(native / INSTALL_FILE, directory=False)
    require(sha(install_path) == receipt['installReceiptSha256'], 'Installation receipt hash mismatch')
    installed = loads(install_path.read_text())
    pins_path = canonical_path(project / 'ProjectSettings/AssemblyShadowSourcePins.json', directory=False)
    pins = loads(pins_path.read_text())
    require(installed.get('schemaVersion') == 1 and installed.get('installMode') == 'PinnedLocal',
            'PinnedLocal installation receipt required')
    require(pins.get('schemaVersion') == 1, 'Source pin schema mismatch')
    for field, value in (('unityVersion', '2022.3.62f2'), ('target', 'StandaloneOSX')):
        require(installed.get(field) == pins.get(field) == receipt.get(field) == value,
                'Installation target mismatch: ' + field)
    require(set(installed.get('repositories', {})) == set(SOURCE_KEYS) and
            set(repositories) == set(SOURCE_KEYS.values()), 'Complete four-source tuple required')
    for key, name in SOURCE_KEYS.items():
        require(installed['repositories'][key] == pins.get(key), 'Installed/source pin mismatch: ' + name)
        item = installed['repositories'][key]
        require(item.get('url') == 'https://github.com/night-outlook/' + name + '.git' and
                item.get('revision') == repositories[name] and re.fullmatch('[0-9a-f]{40}', repositories[name]),
                'Installation repository identity mismatch: ' + name)
    require(installed.get('packageRevision') == repositories['hybridclr_unity'], 'Installed package revision mismatch')
    before, after = inventory_entries(receipt['installedBefore']), inventory_entries(receipt['installedAfter'])
    require(INSTALL_FILE in before and INSTALL_FILE in after and
            before[INSTALL_FILE]['sha256'] == after[INSTALL_FILE]['sha256'] == receipt['installReceiptSha256'],
            'Installation receipt must be preserved in both exact inventories')
    count = verify_inventory(native, receipt['installedAfter'])
    require(OVERLAY not in before and OVERLAY in after and
            after[OVERLAY]['sha256'] == receipt['testOverlaySha256'], 'Exact additive native probe required')
    for name, entry in before.items():
        if name not in GENERATED:
            require(after.get(name) == entry, 'Changed non-generated installed source: ' + name)
    require(set(after) - set(before) <= GENERATED | {OVERLAY}, 'Unexplained native source addition')
    return {'kind': POLICY, 'schemaVersion': 1, 'installedNativeRoot': str(native),
            'projectPath': str(project), 'installationReceipt': str(install_path),
            'installReceiptSha256': receipt['installReceiptSha256'], 'verifiedNativeFiles': count,
            'sourcePinsSha256': sha(pins_path), 'repositories': repositories, 'runtimeAcceptance': False}
