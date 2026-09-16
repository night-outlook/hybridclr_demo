import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import h1_count_build_batch_tooling as w


class ToolingBindingTests(unittest.TestCase):
    def tearDown(self):
        w._FROZEN_BY_PROJECT.clear()
    def test_verified_receipt_gets_role_and_tooling_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();out=root/'out';out.mkdir();receipt=root/'receipt.json';receipt.write_text('{"buildGuid":"fixture"}\n')
            target_sha='a'*64
            w._FROZEN_BY_PROJECT[str(root)]={'role':'reproduction','head':'1'*40,'sourcePinSha256':'2'*64,
                'behaviorSourceCommit':'3'*40,'validationToolingCommit':'4'*40,
                'handoff':{'sourceTargetSha256':target_sha,'toolFiles':{'Tools/AssemblyShadow/tool.py':'5'*40}}}
            with patch.object(w,'_ORIGINAL_VERIFY',return_value={'receiptPath':str(receipt)}):
                result=w.verify_build(root,receipt,out,'2'*64)
            binding=Path(result['validationToolingBindingPath']);value=json.loads(binding.read_text())
            self.assertEqual('reproduction',value['role']);self.assertEqual('3'*40,value['behaviorSourceCommit'])
            self.assertEqual('4'*40,value['validationToolingCommit']);self.assertEqual(target_sha,value['authoritySourceTargetSha256'])
            self.assertEqual(w.digest(receipt.read_bytes()),value['buildReceiptSha256'])
            self.assertFalse(value['humanGatePassed']);self.assertFalse(value['mayEnterR02'])
    def test_missing_frozen_identity_fails_after_underlying_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();out=root/'out';out.mkdir();receipt=root/'receipt.json';receipt.write_text('{}')
            with patch.object(w,'_ORIGINAL_VERIFY',return_value={}):
                with self.assertRaisesRegex(RuntimeError,'not frozen'):
                    w.verify_build(root,receipt,out,'2'*64)


if __name__=='__main__':unittest.main()
