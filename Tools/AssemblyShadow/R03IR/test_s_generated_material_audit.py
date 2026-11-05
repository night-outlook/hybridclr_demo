#!/usr/bin/env python3
"""Host-only tests for lexical/audit boundary; no S checkout or Unity executed."""
import tempfile
import unittest

from audit_s_generated_material import (FILES, ORIGINAL, git_blob, scan,
    no_duplicates, audit, sha256)


class OriginalSGeneratedMaterialTests(unittest.TestCase):
    def test_git_blob_known(self):
        self.assertEqual(git_blob(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_pinned_unique_files(self):
        self.assertEqual(len(FILES), 2)
        self.assertEqual({v[2] for v in FILES.values()}, {11350766, 8465159})
        self.assertEqual({v[3] for v in FILES.values()}, {96487, 91940})
        self.assertEqual(ORIGINAL, "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b")

    def test_distinct_lexical_marker_classes(self):
        s = scan((b"#include <stdint.h>\n"
                  b"IL2CPP_EXTERN_C int SomeInvoker(InvokerMethod* arg) {}\n"
                  b"Il2CppMethodPointer p; /* GenericMethod */\n"))
        self.assertEqual(s["lines"], 3)
        for key in ("include", "externC", "invoker", "methodPointer", "generic"):
            self.assertEqual(s["counts"][key], 1)
        self.assertFalse(s["semanticCxxAstReviewed"])
        self.assertFalse(s["linkedPlayerBound"])
        self.assertFalse(s["compiledObjectBound"])

    def test_changed_marker_line_changes_hash(self):
        first = scan(b"Il2CppMethodPointer x = 0;\n")
        second = scan(b"Il2CppMethodPointer x = 1;\n")
        self.assertEqual(first["counts"]["methodPointer"], 1)
        self.assertNotEqual(first["lineFingerprints"]["methodPointer"],
                            second["lineFingerprints"]["methodPointer"])

    def test_absent_markers_are_not_synthetic_successes(self):
        result = scan(b"none\n")
        self.assertEqual(sum(result["counts"].values()), 0)
        self.assertFalse(result["semanticCxxAstReviewed"])

    def test_no_text_or_null_bytes(self):
        for value in (b"", b"\0abc", b"ab\0cd", b"\xff\xfe"):
            with self.subTest(value=value):
                with self.assertRaises((ValueError, UnicodeError)):
                    scan(value)

    def test_samples_are_bounded(self):
        result = scan(b"Il2CppMethodPointer entry;\n" * 60)
        self.assertEqual(result["counts"]["methodPointer"], 60)
        self.assertEqual(len(result["samples"]["methodPointer"]), 8)

    def test_scan_is_deterministic(self):
        code = b"InvokerMethod one;\nInvokerMethod two;\n"
        self.assertEqual(scan(code), scan(code))

    def test_empty_duplicate_json_fails(self):
        with self.assertRaises(ValueError):
            no_duplicates([("path", "one"), ("path", "two")])

    def test_readonly_auditor_rejects_non_repository(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):
                audit(path)

    def test_pinned_blob_hash_is_input_bound(self):
        self.assertNotEqual(git_blob(b"abc\n"), git_blob(b"abcd\n"))
        self.assertNotEqual(sha256(b"abc\n"), sha256(b"abcd\n"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
