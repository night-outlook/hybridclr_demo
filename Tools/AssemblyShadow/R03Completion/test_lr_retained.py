"""Immutable R transaction witnesses; no historical mutation or Unity execution."""
import copy
from pathlib import Path
import shutil
import tempfile
import unittest
import retained_transaction as audit
from batch_contract import ContractError, sha


class RetainedRTests(unittest.TestCase):
    def setUp(self):
        self.manifest=audit.inputs()
        self.source=audit.HERE.parents[2]/self.manifest['checkpoint']
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()/'copy';self.root.mkdir()
        for row in self.manifest['files'].values():
            path=self.root/row['path'];path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(self.source/row['path'],path)

    def test_original_recorded_transaction_and_custody(self):
        before={r['path']:sha(self.source/r['path']) for r in self.manifest['files'].values()}
        result=audit.verify(self.source,self.manifest)
        self.assertEqual(result['filesVerified'],6);self.assertTrue(result['settingsRemainStaged'])
        self.assertFalse(result['restorationPerformed']);self.assertFalse(result['runtimeAcceptance'])
        self.assertEqual(before,{p:sha(self.source/p) for p in before})

    def test_staged_change_rejected_even_original_bytes(self):
        (self.root/self.manifest['files']['settings']['path']).write_bytes((self.root/self.manifest['files']['original']['path']).read_bytes())
        with self.assertRaisesRegex(ContractError,'differs'):audit.verify(self.root,self.manifest)

    def test_backup_change_rejected(self):
        p=self.root/self.manifest['files']['original']['path'];p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaisesRegex(ContractError,'differs'):audit.verify(self.root,self.manifest)

    def test_missing_state_rejected(self):
        (self.root/self.manifest['files']['state']['path']).unlink()
        with self.assertRaises(ContractError):audit.verify(self.root,self.manifest)

    def test_unexpected_restore_receipt_rejected(self):
        p=self.root/self.manifest['absent'][0];p.write_text('{}')
        with self.assertRaisesRegex(ContractError,'Unexpected historical'):audit.verify(self.root,self.manifest)

    def test_live_alias_is_not_admitted(self):
        alias=self.root.parent/'alias';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaisesRegex(ContractError,'Canonical'):audit.verify(alias,self.manifest)

    def test_path_escape_rejected(self):
        value=copy.deepcopy(self.manifest);value['files']['state']['path']='../foreign'
        with self.assertRaisesRegex(ContractError,'Relative'):audit.verify(self.root,value)


if __name__=='__main__':unittest.main()
