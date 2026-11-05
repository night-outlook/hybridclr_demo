#!/usr/bin/env python3
"""Host-only original-S source registration contract tests. No archived Player run."""
import copy
from pathlib import Path
import tempfile
import unittest

from audit_s_binary_linkage import (
    ORIGINAL, TABLES, ROLES, MACHO_BLOBS, SOURCES, registration_symbols,
    git_blob_file, audit, unique, bounded_nm, classify_nm_symbols,
)


def registration():
    text = """#include "pch-cpp.hpp"
IL2CPP_EXTERN_C const Il2CppMethodPointer g_Il2CppGenericMethodPointers[];
IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];
IL2CPP_EXTERN_C const Il2CppCodeRegistration g_CodeRegistration;
const Il2CppCodeRegistration g_CodeRegistration = {
 2, g_ReversePInvokeWrapperPointers,
 48232, g_Il2CppGenericMethodPointers,
 g_Il2CppGenericAdjustorThunks,
 10198, g_Il2CppInvokerPointers,
 1795, g_UnresolvedVirtualMethodPointers, g_UnresolvedInstanceMethodPointers,
 g_UnresolvedStaticMethodPointers, 456, g_Il2CppInteropData,
 0, NULL, 57, g_CodeGenModules,
};
void s_Il2CppCodegenRegistration()
{
 il2cpp_codegen_register (&g_CodeRegistration, &g_MetadataRegistration, &s_Il2CppCodeGenOptions);
}
"""
    return text.encode("utf-8")


class SBinaryLinkageContracts(unittest.TestCase):
    def test_concrete_source_registration(self):
        row = registration_symbols(registration())
        self.assertEqual(row["genericCount"], 48232)
        self.assertEqual(row["invokerCount"], 10198)
        self.assertEqual(row["referencedSymbols"], sorted(TABLES))

    def test_mutated_method_count_fails(self):
        src = registration().replace(b"48232,", b"48231,")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_mutated_invoker_count_fails(self):
        src = registration().replace(b"10198,", b"10199,")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_missing_registration_reference_fails(self):
        src = registration().replace(b"g_Il2CppInvokerPointers,\n", b"g_OtherInvokers,\n")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_missing_external_declaration_fails(self):
        src = registration().replace(b"IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];\n", b"")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_missing_registration_call_fails(self):
        src = registration().replace(b"il2cpp_codegen_register", b"not_code_registration")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_duplicate_external_declaration_fails(self):
        src = registration().replace(b"IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];",
            b"IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];\n"
            b"IL2CPP_EXTERN_C const InvokerMethod g_Il2CppInvokerPointers[];")
        with self.assertRaises(ValueError):
            registration_symbols(src)

    def test_original_roles_and_blob_ids(self):
        self.assertEqual(ORIGINAL, "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b")
        self.assertEqual(set(ROLES), {"NativeOn", "NativeOff"})
        self.assertEqual(len(SOURCES), 2)
        self.assertEqual({v[1] for v in MACHO_BLOBS.values()}, {98041110, 96480726})

    def test_real_macho_symbol_format_is_defined(self):
        entries = [
            "0000000002b9dee8 (__DATA_CONST,__const) non-external (was a private external) _g_Il2CppGenericMethodPointers",
            "0000000002b4c328 (__DATA_CONST,__const) non-external (was a private external) _g_Il2CppInvokerPointers",
        ]
        answer = classify_nm_symbols(entries)
        self.assertIs(answer["allRequiredSymbolsDefined"], True)
        self.assertEqual(len(answer["definedSymbols"]["g_Il2CppGenericMethodPointers"]), 1)

    def test_undefined_and_lookalike_symbols_cannot_pass(self):
        bad = [
            "                 (undefined) external _g_Il2CppGenericMethodPointers",
            "0000000002b4c328 (__DATA_CONST,__const) non-external _g_Il2CppInvokerPointers",
            "0000000002b9dee8 (__DATA_CONST,__const) non-external _g_Il2CppGenericMethodPointersSuffix",
        ]
        self.assertIs(classify_nm_symbols(bad)["allRequiredSymbolsDefined"], False)

    def test_duplicate_definition_rejected(self):
        defined = [
            "0000000002b9dee8 (__DATA_CONST,__const) non-external _g_Il2CppGenericMethodPointers",
            "0000000002b4c328 (__DATA_CONST,__const) non-external _g_Il2CppInvokerPointers",
        ]
        self.assertIs(classify_nm_symbols(defined + defined)["allRequiredSymbolsDefined"], False)

    def test_no_invented_original_binary_fixture(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaises(ValueError):
                audit(Path(p))

    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):
            unique([("a", 1), ("a", 2)])

    def test_symbol_observation_is_not_linkage_proof(self):
        with tempfile.TemporaryDirectory() as p:
            fake = Path(p) / "fake.dylib"
            fake.write_bytes(b"not a Mach-O")
            result = bounded_nm(fake)
            self.assertIs(result["exactSourceBytesInBinaryProven"], False)
            self.assertIs(result["objectFileIdentityProven"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
