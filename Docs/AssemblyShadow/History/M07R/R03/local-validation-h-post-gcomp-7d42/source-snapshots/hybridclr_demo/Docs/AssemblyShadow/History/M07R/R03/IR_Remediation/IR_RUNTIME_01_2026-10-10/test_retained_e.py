"""Original-Git binding tests plus synthetic preservation negatives; not live E proof."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import verify_retained_e as audit

class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.old=self.root/'old-e';self.old.mkdir()
        self.file=self.old/'evidence';self.file.write_text('original')
        self.out=self.root/'new-f';self.out.mkdir()
        self.demo=self.root/'repo';self.demo.mkdir()

    def invoke(self,phase,before=None):
        args=['--demo',str(self.demo),'--phase',phase,'--receipt',str(self.out/(phase+'.json'))]
        if before:args += ['--before',str(before)]
        with patch.object(audit,'ROOTS',(self.old,)),patch.object(audit,'authenticate_published',return_value=1):
            return audit.main(args)

    def test_snapshot_is_read_only_and_stable(self):
        before=audit.snapshot((self.old,));self.assertEqual(before,audit.snapshot((self.old,)))
        self.assertEqual(self.file.read_text(),'original')

    def test_before_after_requires_exact_survival(self):
        self.assertEqual(self.invoke('before'),0)
        self.assertEqual(self.invoke('after',self.out/'before.json'),0)

    def test_changed_evidence_blocks(self):
        self.assertEqual(self.invoke('before'),0);self.file.write_text('changed')
        self.assertEqual(self.invoke('after',self.out/'before.json'),2)

    def test_additional_or_missing_file_blocks(self):
        self.assertEqual(self.invoke('before'),0);(self.old/'new').write_text('unexpected')
        self.assertEqual(self.invoke('after',self.out/'before.json'),2)

    def test_missing_retained_root_blocks(self):
        with self.assertRaises(RuntimeError):audit.snapshot((self.root/'missing',))

    def test_authenticated_symlink_is_rejected(self):
        alias=self.old/'link';alias.symlink_to(self.file)
        with self.assertRaises(RuntimeError):audit.regular(alias)

    def test_before_inventory_tampering_is_rejected(self):
        self.assertEqual(self.invoke('before'),0)
        (self.out/'before.inventory.json').write_text('{}')
        self.assertEqual(self.invoke('after',self.out/'before.json'),2)

    def test_no_receipt_overwrite(self):
        dest=self.out/'unique.json';audit.write_new(dest,{'old':1})
        with self.assertRaises(FileExistsError):audit.write_new(dest,{'changed':1})
        self.assertEqual(json.loads(dest.read_text()),{'old':1})

    def test_original_e_git_inventories_are_genuine(self):
        root=os.environ.get('IR_E_SOURCE_ROOT')
        if root is None:
            root=subprocess.check_output(['git','-C',str(Path(__file__).parent),'rev-parse','--show-toplevel'],text=True).strip()
        # Fail (never skip) if genuine E Git publication is unavailable.
        index=audit.original_json(Path(root),'batch/evidence-index.json')
        native=audit.original_json(Path(root),'RETAINED_LIVE_ROOTS.json')
        self.assertEqual(len(index['files']),999)
        self.assertEqual(len(native['nativeInventories']),3)
        for role in native['nativeInventories']:
            self.assertEqual(len(role['installedFileInventory']),972)
        self.assertEqual(native['batch'],str(audit.BATCH))

if __name__=='__main__':unittest.main()
