#!/usr/bin/env python3
"""Focused source-anchored mutations for the inactive B2 topology boundary."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import verify_native_source_path_boundary as gate

ROOT = Path(os.environ.get('R03_B2_PINNED_NATIVE_ROOT',''))
NATIVE_AVAILABLE = bool(os.environ.get('R03_B2_PINNED_NATIVE_ROOT'))


def pinned_inputs():
    return {name:(ROOT/name).read_text(encoding='utf-8') for name in gate.PINNED_BLOBS}

class SourceBoundaryTests(unittest.TestCase):
    def test_comments_and_quoted_strings_do_not_prove_source(self):
        inp='// auto resolveOwner=[&]{ fake(); }\nconst char* x="case IL2CPP_TYPE_PTR:";\n' \
            '/* CheckFirstOwner(image) */ void call() { pass(); }'
        code=gate.code_only(inp)
        for forbidden in ('resolveOwner','CheckFirstOwner','IL2CPP_TYPE_PTR:'):
            self.assertNotIn(forbidden,code)
        self.assertIn('void call() { pass(); }',code)
        self.assertEqual(len(code),len(inp))

    def test_scope_recognizes_nested_braces_not_next_function(self):
        raw='struct Composer { void X(){if(z){hi();}} void Y(){next();} }; void A(){evil();}'
        body=gate.scope(gate.code_only(raw),r'struct\s+Composer\s*\{','Composer')
        self.assertIn('hi();',body)
        self.assertIn('next();',body)
        self.assertNotIn('evil();',body)

    def test_ambiguous_scope_rejected(self):
        with self.assertRaisesRegex(gate.SourceMismatch,'ambiguous'):
            gate.scope('auto f=[]{}; auto f=[]{};',r'auto\s+f=', 'f')

    def test_git_blob_digest(self):
        raw=b'abc\n'
        expected=hashlib.sha1(b'blob 4\0abc\n').hexdigest()
        self.assertEqual(gate.blob_sha(raw),expected)
        self.assertEqual(len(gate.PINNED_BLOBS),4)

    def test_status_output_flags_are_always_closed(self):
        # Both proof surfaces and model roots are asserted false by schema;
        # a source mutation must reject, not silently self-upgrade evidence.
        self.assertEqual(len(gate.PATHS),6)
        self.assertGreaterEqual(len(gate.REJECTIONS),7)
        self.assertEqual(gate.NATIVE_COMMIT,
                         'cecf4b859d50b128e5c0fc6c90cd89e3a452b96a')

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_real_source_and_cli_exact_pin(self):
        result=gate.verify_repository(ROOT)
        self.assertEqual(result['result'],'PinnedStaticBoundaryOnly')
        self.assertEqual(result['staticPathLabels'],[r[0] for r in gate.PATHS])
        self.assertEqual(result['nativeCombinedTypeDefLimit'],128)
        self.assertFalse(result['allRealTypeDefPathsDiscovered'])
        self.assertFalse(result['producerIntegrated'])
        self.assertFalse(result['R03Accepted'])
        script=Path(gate.__file__)
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'source-obligations.json'
            proc=subprocess.run([sys.executable,str(script),'--native-root',str(ROOT),
                                 '--output',str(output)],check=False,
                                capture_output=True,text=True,timeout=30)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(output.read_text())['handoffAuthority'],
                             'CLOSED_NO_LOCAL_EXECUTION')

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_missing_first_owner_check_rejected_independently_of_pin(self):
        inputs=pinned_inputs()
        source=inputs[gate.SOURCE]
        self.assertIn('original_join::CheckFirstOwner(',source)
        source=source.replace('original_join::CheckFirstOwner(',
                              'original_join::CheckAnyOwner(',1)
        with self.assertRaisesRegex(gate.SourceMismatch,'first-owner check'):
            gate.check_source(source,inputs[gate.OWNER],inputs[gate.LIFETIME],inputs[gate.LIMITS])

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_remove_primitive_owner_path_rejected(self):
        inputs=pinned_inputs()
        source=inputs[gate.SOURCE].replace(
            'makeDefinition(primitive->typeMetadataHandle',
            'makeDefinition(primitive->unrelatedHandle',1)
        with self.assertRaisesRegex(gate.SourceMismatch,'PrimitiveDefault'):
            gate.check_source(source,inputs[gate.OWNER],inputs[gate.LIFETIME],inputs[gate.LIMITS])

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_remove_pre_owner_rejection_rejected(self):
        inputs=pinned_inputs()
        source=inputs[gate.SOURCE].replace(
            'if(!array||!array->rank', 'if(array && array->rank',1)
        with self.assertRaisesRegex(gate.SourceMismatch,'InvalidArrayShape'):
            gate.check_source(source,inputs[gate.OWNER],inputs[gate.LIFETIME],inputs[gate.LIMITS])

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_reordered_owner_and_audit_rejected(self):
        inputs=pinned_inputs()
        source=inputs[gate.SOURCE]
        before='original_join::CheckFirstOwner('
        after='c.nonRootOwners->Note('
        self.assertEqual(source.count(before),3)
        self.assertEqual(source.count(after),1)
        # Move *the first owner check in resolveOwner* after the insertion site
        # by replacing its spelling with a sentinel and shifting the target.
        source=source.replace(before,'SourceOwnerCheckMoved(',1)
        source=source.replace(after,before,1)
        with self.assertRaisesRegex(gate.SourceMismatch,'128-cap audit insertion'):
            gate.check_source(source,inputs[gate.OWNER],inputs[gate.LIFETIME],inputs[gate.LIMITS])

    @unittest.skipUnless(NATIVE_AVAILABLE,'requires exact pinned native checkout')
    def test_changed_lookup_and_abi_bounds_rejected(self):
        inputs=pinned_inputs()
        altered=inputs[gate.LIMITS].replace(
            'kMaximumNonRootTypeDefOwnerPairs = 128',
            'kMaximumNonRootTypeDefOwnerPairs = 129',1)
        with self.assertRaisesRegex(gate.SourceMismatch,'combined native handle ceiling'):
            gate.check_source(inputs[gate.SOURCE],inputs[gate.OWNER],
                              inputs[gate.LIFETIME],altered)

if __name__ == '__main__':
    unittest.main()
