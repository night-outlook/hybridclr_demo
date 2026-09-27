import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
import evidence as e

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name).resolve()
    def tearDown(self): self.temp.cleanup()
    def file(self, name="a", data=b"abc"):
        p = self.root/name; p.write_bytes(data); return p
    def test_large_integers_preserved(self):
        self.assertEqual(e.loads('{"v":9007199254740993}')["v"], 9007199254740993)
    def test_duplicate_keys_rejected(self):
        with self.assertRaises(e.EvidenceError): e.loads('{"a":1,"a":2}')
    def test_nonfinite_and_overflow_rejected(self):
        for text in ('NaN','Infinity','-Infinity','1e9999','-1e9999'):
            with self.subTest(text=text), self.assertRaises(e.EvidenceError): e.loads(text)
    def test_boolean_is_not_integer(self):
        with self.assertRaises(e.EvidenceError): e.integer(True,"field")
    def test_binding_and_changed_content(self):
        p=self.file(); row=e.binding(p); self.assertEqual(e.check_binding(row),p)
        p.write_bytes(b"abd")
        with self.assertRaises(e.EvidenceError): e.check_binding(row)
    def test_symlink_rejected(self):
        p=self.file(); link=self.root/'link'; link.symlink_to(p)
        with self.assertRaises(e.EvidenceError): e.binding(link)
    def test_linked_parent_rejected(self):
        folder=self.root/'folder'; folder.mkdir(); (folder/'x').write_text('x')
        link=self.root/'link'; link.symlink_to(folder,target_is_directory=True)
        with self.assertRaises(e.EvidenceError): e.binding(link/'x')
        with self.assertRaises(e.EvidenceError): e.write(link/'new',{})
    def test_write_is_exclusive(self):
        p=self.root/'r.json'; e.write(p,{'result':'Failed'})
        with self.assertRaises(FileExistsError): e.write(p,{'result':'Passed'})
    def test_archive_roundtrip_deduplicates_bytes_not_locators(self):
        a=self.file(); b=self.file('b'); receipt=e.seal([a,b,a],self.root/'sealed')
        self.assertEqual(len(receipt['files']),2);self.assertEqual(receipt['uniqueMemberCount'],1)
        e.audit_archive(receipt)
    def test_archive_duplicate_or_extra_member_rejected(self):
        for name in ('../escape','blobs/'+'f'*64):
            with self.subTest(name=name):
                p=self.file('in'+str(len(name)));receipt=e.seal([p],self.root/('out'+str(len(name))))
                archive=Path(receipt['archive']['path'])
                with tarfile.open(archive,'w:gz') as t:
                    m=tarfile.TarInfo(name);m.size=1;t.addfile(m,io.BytesIO(b'x'))
                receipt['archive']=e.binding(archive)
                with self.assertRaises(e.EvidenceError):e.audit_archive(receipt)
    def test_archive_missing_member_rejected(self):
        receipt=e.seal([self.file()],self.root/'out');p=Path(receipt['archive']['path'])
        with tarfile.open(p,'w:gz'): pass
        receipt['archive']=e.binding(p)
        with self.assertRaises(e.EvidenceError):e.audit_archive(receipt)
    def test_command_exit_and_log_binding(self):
        row=e.run([sys.executable,'-c','print("ok")'],self.root,self.root/'run',10)
        self.assertEqual(row['result'],'Passed');self.assertTrue(row['processGroupClean'])
        for entry in row['logs']:e.check_binding(entry)
    def test_failed_command_is_retained(self):
        row=e.run([sys.executable,'-c','import sys;sys.exit(3)'],self.root,self.root/'run',10)
        self.assertEqual(row['result'],'Failed');self.assertEqual(row['exitCode'],3)
        self.assertTrue((self.root/'run/command.json').is_file())
    def test_timeout_is_failure(self):
        row=e.run([sys.executable,'-c','import time;time.sleep(10)'],self.root,self.root/'run',1)
        self.assertTrue(row['timedOut']);self.assertEqual(row['result'],'Failed')
    def test_spawn_failure_is_retained(self):
        row=e.run([str(self.root/'absent')],self.root,self.root/'run',2)
        self.assertEqual(row['result'],'Failed');self.assertIn('error',row)
