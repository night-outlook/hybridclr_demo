"""No-Unity, no-write tests of external SDK copy-root admission for native_validation."""
import tempfile
import unittest
from pathlib import Path

from native_validation import checked_sdk_scratch
from batch_contract import ContractError


class SdkScratchBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'assembly_shadow_h1r'
        self.workspace.mkdir()
        self.output = self.root / 'preflight' / 'native'
        self.output.mkdir(parents=True)
        self.contents = self.root / 'UnityEditor' / 'Unity.app' / 'Contents'
        self.contents.mkdir(parents=True)
        self.scratch = self.root / 'external-sdk-copy'

    def valid(self, path):
        return checked_sdk_scratch(path, self.workspace, self.output, self.contents)

    def test_fresh_external_root_is_read_only_admitted(self):
        self.assertEqual(self.valid(self.scratch), self.scratch)
        self.assertFalse(self.scratch.exists())

    def test_no_scratch_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'sdk-scratch'):
            self.valid(None)

    def test_relative_root_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'Canonical absolute'):
            self.valid(Path('relative-scratch'))

    def test_consumed_scratch_is_rejected_without_touching_bytes(self):
        self.scratch.mkdir()
        sentinel = self.scratch / 'preserve.txt'
        sentinel.write_text('original')
        with self.assertRaisesRegex(ContractError, 'Fresh absent'):
            self.valid(self.scratch)
        self.assertEqual(sentinel.read_text(), 'original')

    def test_source_nested_root_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'outside source'):
            self.valid(self.workspace / 'fresh-sdk')

    def test_evidence_nested_root_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'outside source'):
            self.valid(self.output / 'fresh-sdk')

    def test_installed_editor_nested_root_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'outside source'):
            self.valid(self.root / 'UnityEditor' / 'new-sdk')

    def test_symlink_parent_is_rejected(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ContractError, 'Canonical absolute'):
            self.valid(alias / 'fresh-sdk')

    def test_missing_parent_is_rejected(self):
        with self.assertRaisesRegex(ContractError, 'Fresh absent'):
            self.valid(self.root / 'missing-parent' / 'fresh-sdk')

    def test_validation_does_not_change_inputs(self):
        files = []
        for directory in (self.workspace, self.output, self.contents):
            marker = directory / 'owned.txt'
            marker.write_text('keep')
            files.append(marker)
        self.valid(self.scratch)
        self.assertTrue(all(p.read_text() == 'keep' for p in files))
        self.assertFalse(self.scratch.exists())


if __name__ == '__main__':
    unittest.main()
