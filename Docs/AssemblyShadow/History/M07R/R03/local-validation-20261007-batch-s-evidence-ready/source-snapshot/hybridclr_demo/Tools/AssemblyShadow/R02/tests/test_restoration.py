import json
from pathlib import Path
import tempfile
import unittest
from evidence import EvidenceError
from restoration import diagnostic_scene_allowed, restore_files, with_recovery

class Restoration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();self.project=self.root/'project';self.project.mkdir()
        self.file=self.project/'scene';self.file.write_bytes(b'generated')
    def test_allowed_changes_restore_exact_original_bytes(self):
        value=restore_files(self.project,{'scene':b'original'},lambda *a:True,self.root/'capture')
        self.assertEqual(value['result'],'Passed');self.assertEqual(self.file.read_bytes(),b'original')
        self.assertEqual((self.root/'capture/000.after').read_bytes(),b'generated')
    def test_unexpected_change_is_retained_and_not_overwritten(self):
        with self.assertRaises(EvidenceError):restore_files(self.project,{'scene':b'original'},lambda *a:False,self.root/'capture')
        self.assertEqual(self.file.read_bytes(),b'generated')
        self.assertEqual(json.loads((self.root/'capture/restoration.json').read_text())['result'],'Failed')
    def test_all_files_checked_before_any_write(self):
        (self.project/'second').write_bytes(b'unrelated')
        with self.assertRaises(EvidenceError):
            restore_files(self.project,{'scene':b'original','second':b'old'},lambda p,*a:p=='scene',self.root/'capture')
        self.assertEqual(self.file.read_bytes(),b'generated')
        self.assertEqual((self.project/'second').read_bytes(),b'unrelated')
    def test_concurrent_change_refused(self):
        def allowed(*a):self.file.write_bytes(b'concurrent');return True
        with self.assertRaises(EvidenceError):restore_files(self.project,{'scene':b'original'},allowed,self.root/'capture')
        self.assertEqual(self.file.read_bytes(),b'concurrent')
    def test_missing_file_retains_original_and_failure_record(self):
        self.file.unlink()
        with self.assertRaises(EvidenceError):restore_files(self.project,{'scene':b'original'},lambda *a:True,self.root/'capture')
        self.assertEqual((self.root/'capture/000.before').read_bytes(),b'original')
        self.assertTrue((self.root/'capture/restoration.json').is_file())
    def test_symlink_target_not_overwritten(self):
        target=self.root/'outside';target.write_bytes(b'outside');self.file.unlink();self.file.symlink_to(target)
        with self.assertRaises(EvidenceError):restore_files(self.project,{'scene':b'original'},lambda *a:True,self.root/'capture')
        self.assertEqual(target.read_bytes(),b'outside')
    def test_diagnostic_scene_only_allows_two_identity_values(self):
        a=b'x\n  expectedBaselineBuildId: old\n  expectedRuntimeAbiHash: oldhash\ny\n'
        b=a.replace(b'old',b'new')
        self.assertTrue(diagnostic_scene_allowed(a,b))
        self.assertFalse(diagnostic_scene_allowed(a,b.replace(b'x\n',b'other\n')))
        with self.assertRaises(EvidenceError):diagnostic_scene_allowed(a,b+b'  expectedRuntimeAbiHash: duplicate\n')
    def test_two_failures_both_retained(self):
        def action():raise RuntimeError('build-cause')
        def recovery():raise RuntimeError('recovery-cause')
        with self.assertRaises(EvidenceError):with_recovery(action,recovery,self.root/'record.json')
        record=json.loads((self.root/'record.json').read_text())
        self.assertIn('build-cause',record['actionError']);self.assertIn('recovery-cause',record['recoveryError'])
    def test_successful_recovery_does_not_promote_failed_build(self):
        def action():raise RuntimeError('build-cause')
        with self.assertRaises(EvidenceError):with_recovery(action,lambda:None,self.root/'record.json')
        record=json.loads((self.root/'record.json').read_text())
        self.assertEqual(record['recoveryResult'],'Passed');self.assertEqual(record['result'],'Failed')
    def test_success_returns_action_value(self):
        self.assertEqual(with_recovery(lambda:42,lambda:None,self.root/'record.json'),42)
