"""Real historical compiler bytes exercise the explicit negative transform."""
import base64
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import r01_negative_inputs as q
from shadow_tools import VerificationError

class NegativeInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((Path(__file__).parent/'data/r01-contracts-parser-fixture.json').read_text())
        cls.original=zlib.decompress(base64.b64decode(cls.fixture['data']))
        assert q.sha256(cls.original)==cls.fixture['sha256']
        assert len(cls.original)==cls.fixture['length']

    def test_real_compiler_transform_preserves_identity_and_records_shared_blob(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.dll';source.write_bytes(self.original)
            r=q.transform(source,root/'negative.dll',root/'receipt.json',self.fixture['provenance'])
            changed=[i for i,(a,b) in enumerate(zip(self.original,(root/'negative.dll').read_bytes())) if a!=b]
            self.assertEqual(changed,[r['mutation']['changedByteOffset']])
            self.assertEqual(r['mutation']['signatureOriginal'],'200001')
            self.assertEqual(len(r['mutation']['affectedMethodDefTokens']),22)
            self.assertEqual(r['sourceIdentity'],r['outputIdentity'])
            self.assertEqual(r['outputSha256'],'670684b63e60190f8736244f88a1816f7766e77e11572699a641049cf987b4dd')
            self.assertEqual(r['sourceLength'],r['outputLength'])

    def test_wrong_source_provenance_fails_before_any_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.dll';source.write_bytes(self.original)
            p=copy.deepcopy(self.fixture['provenance']);p['patchClosureRow']['sha256']='0'*64
            with self.assertRaises(VerificationError):q.transform(source,root/'negative.dll',root/'receipt.json',p)
            self.assertFalse((root/'negative.dll').exists());self.assertFalse((root/'receipt.json').exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.dll';source.write_bytes(self.original)
            (root/'negative.dll').write_bytes(b'existing')
            with self.assertRaises(VerificationError):q.transform(source,root/'negative.dll',root/'receipt.json')
            self.assertEqual((root/'negative.dll').read_bytes(),b'existing')
            self.assertFalse((root/'receipt.json').exists())

if __name__=='__main__':unittest.main()
