"""Synthetic filesystem/receipt contracts, not native build or Player evidence."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from batch_contract import ContractError, sha
from build_provenance import (INSTALL_FILE, NATIVE_RELATIVE, OVERLAY, SOURCE_KEYS, verify_installation,
                              verify_inventory, inventory_entries)
from run_local import Batch


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) if isinstance(value, dict) else value)


def inventory(root):
    return [{'path': p.relative_to(root).as_posix(), 'sha256': sha(p), 'size': p.stat().st_size}
            for p in sorted(root.rglob('*')) if p.is_file()]


class BuildProvenanceContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'batch with spaces'
        self.project = self.root / 'projects/candidate-release'
        self.native = self.project / NATIVE_RELATIVE
        self.native.mkdir(parents=True)
        put(self.project / '.r03-isolated-project', 'synthetic isolated project')
        self.repositories = {n: str(i) * 40 for i, n in enumerate(SOURCE_KEYS.values(), 1)}
        sources = {k: {'url': 'https://github.com/night-outlook/' + n + '.git',
                       'revision': self.repositories[n], 'localPath': '../source/' + n}
                   for k, n in SOURCE_KEYS.items()}
        self.pins = dict(schemaVersion=1, unityVersion='2022.3.62f2', target='StandaloneOSX', **sources)
        self.install = dict(schemaVersion=1, installMode='PinnedLocal', unityVersion='2022.3.62f2',
                            target='StandaloneOSX', packageRevision=self.repositories['hybridclr_unity'], repositories=sources)
        put(self.project / 'ProjectSettings/AssemblyShadowSourcePins.json', self.pins)
        put(self.native / INSTALL_FILE, self.install)
        put(self.native / 'vm/Core.cpp', 'unchanged native source')
        put(self.native / 'hybridclr/generated/MethodBridge.cpp', 'before generation')
        before = inventory(self.native)
        put(self.native / 'hybridclr/generated/MethodBridge.cpp', 'after generation')
        put(self.native / OVERLAY, 'synthetic diagnostic probe')
        self.receipt = dict(schemaVersion=2, kind='R03IsolatedPlayerBuild', projectPath=str(self.project),
                            unityVersion='2022.3.62f2', target='StandaloneOSX', installedNativeRoot=str(self.native),
                            installReceiptSha256=sha(self.native / INSTALL_FILE), testOverlaySha256=sha(self.native / OVERLAY),
                            installedBefore=before, installedAfter=inventory(self.native))

    def verify(self):
        return verify_installation(self.receipt, self.project, self.root, self.repositories)

    def duplicate(self, changed=True):
        target = self.project / 'HybridCLRData/StrippedAOTDllsTempProj/StandaloneOSX/Il2CppOutputProject/IL2CPP/libil2cpp'
        shutil.copytree(self.native, target)
        if changed:
            put(target / 'hybridclr/generated/MethodBridge.cpp', 'different legitimate generated snapshot')
        return target

    def test_explicit_root_accepts_duplicate_receipt_and_distinct_generated_snapshot(self):
        duplicate = self.duplicate()
        self.assertEqual(sha(duplicate / INSTALL_FILE), self.receipt['installReceiptSha256'])
        self.assertEqual(len(list((self.project / 'HybridCLRData').rglob(INSTALL_FILE))), 2)
        result = self.verify()
        self.assertEqual(result['installedNativeRoot'], str(self.native))
        self.assertEqual(result['verifiedNativeFiles'], 4)
        self.assertTrue(duplicate.is_dir())

    def test_generated_copy_not_selected_even_when_inventory_is_identical(self):
        self.receipt['installedNativeRoot'] = str(self.duplicate(changed=False))
        with self.assertRaises(ContractError): self.verify()

    def test_no_explicit_root_cannot_fall_back_to_unique_hash(self):
        self.receipt.pop('installedNativeRoot')
        with self.assertRaises(ContractError): self.verify()

    def test_legacy_schema_not_upgraded(self):
        self.receipt['schemaVersion'] = 1
        with self.assertRaises(ContractError): self.verify()

    def test_other_role_root_rejected(self):
        other = self.root / 'projects/candidate-debug' / NATIVE_RELATIVE
        shutil.copytree(self.native, other)
        self.receipt['installedNativeRoot'] = str(other)
        with self.assertRaises(ContractError): self.verify()

    def test_other_batch_rejected(self):
        with self.assertRaises(ContractError):
            verify_installation(self.receipt, self.project, self.root.parent, self.repositories)

    def test_relative_root_rejected(self):
        self.receipt['installedNativeRoot'] = NATIVE_RELATIVE
        with self.assertRaises(ContractError): self.verify()

    def test_dotdot_root_rejected(self):
        self.receipt['installedNativeRoot'] += '/../libil2cpp'
        with self.assertRaises(ContractError): self.verify()

    def test_symlinked_root_rejected(self):
        real = self.native.with_name('original'); self.native.rename(real); self.native.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ContractError): self.verify()

    def test_symlinked_parent_rejected(self):
        parent = self.native.parent; real = parent.with_name('real-il2cpp'); parent.rename(real); parent.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ContractError): self.verify()

    def test_linked_inventory_file_rejected(self):
        core = self.native / 'vm/Core.cpp'; core.unlink(); core.symlink_to(self.native / OVERLAY)
        with self.assertRaises(ContractError): self.verify()

    def test_linked_empty_inventory_directory_rejected(self):
        target = self.root / 'external'; target.mkdir(); (self.native / 'alias').symlink_to(target, target_is_directory=True)
        with self.assertRaises(ContractError): self.verify()

    def test_mutated_install_receipt_rejected(self):
        put(self.native / INSTALL_FILE, self.install | {'installMode': 'Other'})
        with self.assertRaises(ContractError): self.verify()

    def test_wrong_source_tuple_rejected(self):
        self.repositories['hybridclr'] = 'f' * 40
        with self.assertRaises(ContractError): self.verify()

    def test_wrong_local_pin_rejected(self):
        self.pins['demo'] = self.pins['demo'] | {'localPath': '../other'}
        put(self.project / 'ProjectSettings/AssemblyShadowSourcePins.json', self.pins)
        with self.assertRaises(ContractError): self.verify()

    def test_missing_install_inventory_entry_rejected(self):
        self.receipt['installedBefore'] = [r for r in self.receipt['installedBefore'] if r['path'] != INSTALL_FILE]
        with self.assertRaises(ContractError): self.verify()

    def test_duplicate_inventory_entry_rejected(self):
        self.receipt['installedBefore'].append(copy.deepcopy(self.receipt['installedBefore'][0]))
        with self.assertRaises(ContractError): self.verify()

    def test_changed_generated_file_without_new_receipt_rejected(self):
        put(self.native / 'hybridclr/generated/MethodBridge.cpp', 'changed after build')
        with self.assertRaises(ContractError): self.verify()

    def test_missing_native_file_rejected(self):
        (self.native / 'vm/Core.cpp').unlink()
        with self.assertRaises(ContractError): self.verify()

    def test_unexplained_native_addition_rejected_even_when_inventoried(self):
        put(self.native / 'extra.cpp', 'new'); self.receipt['installedAfter'] = inventory(self.native)
        with self.assertRaises(ContractError): self.verify()

    def test_changed_nongenerated_source_rejected_even_when_inventoried(self):
        put(self.native / 'vm/Core.cpp', 'mutated'); self.receipt['installedAfter'] = inventory(self.native)
        with self.assertRaises(ContractError): self.verify()

    def test_wrong_overlay_hash_rejected(self):
        self.receipt['testOverlaySha256'] = '0' * 64
        with self.assertRaises(ContractError): self.verify()

    def test_unsafe_inventory_paths_rejected(self):
        for name in ('../escape', '/absolute', './relative', 'a//b', 'a\\b', '.', ''):
            with self.subTest(name=name), self.assertRaises(ContractError):
                inventory_entries([dict(path=name, sha256='0' * 64, size=1)])

    def test_invalid_inventory_size_hash_rejected(self):
        for size, digest in ((-1, '0' * 64), (True, '0' * 64), (0, 'invalid')):
            with self.subTest(size=size), self.assertRaises(ContractError):
                inventory_entries([dict(path='core.cpp', sha256=digest, size=size)])

    def integrated(self, architecture='arm64'):
        # Deliberately synthetic files: lipo alone is mocked, never run a Player.
        root = self.root / 'builds/candidate-release'; root.mkdir(parents=True)
        app = root / 'R03Isolated.app'; put(app / 'Contents/MacOS/R03Isolated', 'not an executable')
        source_root = self.root / 'tool-source'; put(source_root / 'PlayerProject/AssemblyShadowR03Probe.cpp', 'synthetic diagnostic probe')
        manifest = {'repositories': self.repositories, 'files': []}
        put(self.project / 'source-inputs.json', manifest)
        config = dict(projectPath=str(self.project), outputPath=str(app), sourceManifestSha256=sha(self.project / 'source-inputs.json'),
                      featureEnabled=True, diagnosticsLevel=2, cppConfiguration='Release')
        self.receipt.update(config, result='Passed', nonGeneratedCorePreserved=True, errors=0, warnings=0,
                            architecture='arm64', playerFiles=inventory(app))
        put(root / 'build-receipt.json', self.receipt)
        batch = object.__new__(Batch); batch.root = self.root
        batch.builds = {'candidate-release': dict(root=root, project=self.project, config=config)}
        with patch('run_local.ROOT', source_root), patch('run_local.subprocess.run', return_value=SimpleNamespace(returncode=0, stdout=architecture)):
            value = Batch.verify_build(batch, 'candidate-release')
        return value, batch

    def test_actual_batch_verifier_uses_explicit_root_with_duplicate(self):
        self.duplicate()
        result, batch = self.integrated()
        self.assertEqual(result['schemaVersion'], 2)
        self.assertEqual(batch.builds['candidate-release']['nativeBinding']['installedNativeRoot'], str(self.native))

    def test_actual_batch_verifier_retains_architecture_guard(self):
        with self.assertRaises(ContractError): self.integrated('x86_64')

    def test_producer_writes_v2_and_actual_settings_root(self):
        source = (Path(__file__).parent / 'PlayerProject/R03Build.cs').read_text()
        self.assertIn('public int schemaVersion = 2;', source)
        self.assertIn('receipt.installedNativeRoot = native;', source)
        self.assertIn('Path.GetFullPath(Path.Combine(SettingsUtil.LocalIl2CppDir, "libil2cpp"))', source)
        self.assertIn('report.summary.totalErrors != 0', source)


if __name__ == '__main__': unittest.main()
