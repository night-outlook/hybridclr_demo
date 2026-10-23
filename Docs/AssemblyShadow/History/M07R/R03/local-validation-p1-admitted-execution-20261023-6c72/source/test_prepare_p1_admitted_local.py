#!/usr/bin/env python3
"""Pure host-only regression tests. Does not contact GitHub or run Unity."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from prepare_p1_admitted_local import (
    API_NEW, API_OLD, CPP_NEW, CPP_OLD, admitted_addition,
    archive_integrity, digest, literal_map, pristine_root, transform_helper,
)


class LocalCollectorRepairTests(unittest.TestCase):
    def fixture(self):
        return ("def verify():\n"
                "  cpp_without_live=cpp.replace(literals['integrated_json_header'],'');api=api.replace(literals['integrated_json_forward'],'')\n"
                "  # restoredcpp=actualcpp.replace(ol['admitted_include'],'')\n"
                "  # restoredapi=actualapi.replace(ol['admitted_decl'],'')\n"
                "  # '53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2'\n"
                "  # '32956c2c4084951131b497c1201712a0d4fe11b3'\n").encode()

    def test_only_two_admission_literals_are_added(self):
        original = self.fixture()
        fixed = transform_helper(original)
        self.assertEqual(fixed, original.replace(CPP_OLD.encode(), CPP_NEW.encode())
                                       .replace(API_OLD.encode(), API_NEW.encode()))
        self.assertIn("literals['admitted_include']", fixed.decode())
        self.assertIn("literals['admitted_decl']", fixed.decode())

    def test_missing_cpp_anchor_refused(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture().replace(CPP_OLD.encode(), b'cpp_without_live=unknown'))

    def test_duplicate_cpp_anchor_refused(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture() + b'\n# ' + CPP_OLD.encode())

    def test_missing_api_anchor_refused(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture().replace(API_OLD.encode(), b';api=unknown'))

    def test_duplicate_api_anchor_refused(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture() + b'\n# ' + API_OLD.encode())

    def test_double_repair_refused(self):
        with self.assertRaises(ValueError):
            transform_helper(transform_helper(self.fixture()))

    def test_original_frozen_tokens_unchanged(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture().replace(b'53aecc2d113b20b6ff825d0aa4ca0f4372a7cce2', b'changed'))

    def test_previous_owned_name_reconstruction_unchanged(self):
        with self.assertRaises(ValueError):
            transform_helper(self.fixture().replace(b'restoredapi=actualapi.replace(ol', b'restoredapi=bad.replace(ol'))

    def test_bytes_require_one_exact_addition(self):
        prior = b'a\nb\nc\n'
        added = b'// admitted\n#include "x.inl"\n'
        admitted_addition(prior[:2] + added + prior[2:], prior, added)
        for invalid in (prior, prior + added + added, prior + added + b'extra', prior + b'not the same'):
            with self.assertRaises(ValueError):
                admitted_addition(invalid, prior, added)
        with self.assertRaises(ValueError):
            admitted_addition(prior + added, prior, b'changed')

    def test_literal_source_parser(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'verify.py'
            path.write_text('def verify():\n  admitted_include="include\\n"\n  admitted_decl="declaration\\n"\n')
            self.assertEqual(literal_map(path)['admitted_decl'], 'declaration\n')
            path.write_text('def verify():\n  admitted_include="include\\n"\n')
            with self.assertRaises(ValueError):
                literal_map(path)

    def test_archived_manifest_and_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d)
            entries = []
            for i in range(31):
                rel = ('FINDING.json' if i == 0 else
                       'preflight/run-once.py' if i == 1 else f'preflight/evidence-{i}.json')
                p = archive / rel
                p.parent.mkdir(exist_ok=True)
                p.write_bytes(f'content-{i}'.encode())
                entries.append(f'{digest(p.read_bytes())}  {rel}')
            (archive / 'MANIFEST.sha256').write_text('\n'.join(entries) + '\n')
            self.assertEqual(archive_integrity(archive)['filesVerified'], 31)
            (archive / 'FINDING.json').write_text('changed')
            with self.assertRaises(ValueError):
                archive_integrity(archive)

    def test_archive_path_traversal_refused(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d)
            (archive / 'MANIFEST.sha256').write_text('0' * 64 + '  ../outside.txt\n')
            with self.assertRaises(ValueError):
                archive_integrity(archive)

    def test_pristine_root_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            pristine_root(parent / 'absent')
            with self.assertRaises(ValueError):
                pristine_root(parent)
            (parent / 'symlink').symlink_to(parent / 'absent')
            with self.assertRaises(ValueError):
                pristine_root(parent / 'symlink')
            with self.assertRaises(ValueError):
                pristine_root(Path('relative-root'))


if __name__ == '__main__':
    unittest.main()
