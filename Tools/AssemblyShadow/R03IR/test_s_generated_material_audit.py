#!/usr/bin/env python3
"""Host-only tests for lexical/audit boundary; no S checkout or Unity executed."""
import tempfile
import unittest

from audit_s_generated_material import (FILES, ORIGINAL, git_blob, scan,
    no_duplicates, audit, sha256, table_structure)


class OriginalSGeneratedMaterialTests(unittest.TestCase):

    def test_generic_table_scalar_entries(self):
        raw = (b"IL2CPP_EXTERN_C const Il2CppMethodPointer g_Il2CppGenericMethodPointers[];\n"
               b"const Il2CppMethodPointer g_Il2CppGenericMethodPointers[48232] =\n{\n" +
               b" (Il2CppMethodPointer)&Foo_gshared,\n" * 48231 +
               b" (Il2CppMethodPointer)&Last_gshared,\n};\n")
        result = table_structure(raw, "Il2CppGenericMethodPointerTable.c")
        self.assertEqual(result["declaredRows"], 48232)
        self.assertEqual(result["initializerRows"], 48232)
        self.assertEqual(result["distinctInitializerLines"], 2)
        self.assertEqual(result["linkageToCompiledObject"], "NotProven")

    def test_invoker_table_scalar_entries(self):
        raw = (b"IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];\n"
               b"const InvokerMethod g_Il2CppInvokerPointers[10198] =\n{\n" +
               b" RuntimeInvoker_One,\n" * 10197 +
               b" RuntimeInvoker_Last\n};\n")
        result = table_structure(raw, "Il2CppInvokerTable.cpp")
        self.assertEqual(result["initializerRows"], 10198)
        self.assertFalse(result["fullSemanticCxxInspection"])

    def test_table_rejects_missing_row_and_wrong_size(self):
        head = b"const InvokerMethod g_Il2CppInvokerPointers[10198] =\n{\n"
        valid_rows = b" ExampleInvoker,\n" * 10198
        for data in (head + valid_rows[:-len(b" ExampleInvoker,\n")] + b"};\n",
                     b"const InvokerMethod g_Il2CppInvokerPointers[10197] =\n{\n" +
                     valid_rows + b"};\n"):
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                table_structure(data, "Il2CppInvokerTable.cpp")

    def test_table_rejects_duplicate_declaration_and_comment_rows(self):
        raw = b"const InvokerMethod g_Il2CppInvokerPointers[10198] =\n{\n" + \
            b" x,\n" * 10198 + b"};\n"
        with self.assertRaises(ValueError):
            table_structure(raw + raw, "Il2CppInvokerTable.cpp")
        broken = raw.replace(b" x,\n", b" // not an initializer,\n", 1)
        with self.assertRaises(ValueError):
            table_structure(broken, "Il2CppInvokerTable.cpp")


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
