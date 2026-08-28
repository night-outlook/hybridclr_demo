"""Focused native-key grammar tests; synthetic PE rows are not Player evidence."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from m05_types import MethodProof, TypeKeyReader, read_type_inventory_bytes
from shadow_tools import VerificationError
from test_m05_results import make_type_pe


INTERNAL = "AssemblyA.Implementation.Internal"
CONTRACTS = "AssemblyA.Contracts"
PAYLOAD = INTERNAL + ".M05InternalPayload"
DATA = INTERNAL + ".VersionedScriptableObject"
VALUE = CONTRACTS + ".DemoValue"


def part(value):
    return str(len(value.encode("utf-8"))) + ":" + value


def definition(assembly, name):
    return "type(" + part(assembly.casefold()) + "/" + part(assembly) + "/" + part(name) + "@0)"


class TypeKeyGrammarTests(unittest.TestCase):
    def setUp(self):
        self.inventories = {
            INTERNAL: read_type_inventory_bytes(make_type_pe([
                dict(name="M05InternalPayload", namespace=INTERNAL),
                dict(name="VersionedScriptableObject", namespace=INTERNAL),
                dict(name="Box`1", namespace=INTERNAL, arity=1),
            ], name=INTERNAL))["types"],
            CONTRACTS: read_type_inventory_bytes(make_type_pe([
                dict(name="DemoValue", namespace=CONTRACTS),
            ], name=CONTRACTS))["types"],
        }
        self.identities = {name: dict(fullName=name + ", Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")
                           for name in self.inventories}
        self.payload = definition(INTERNAL, "M05InternalPayload")
        self.data = definition(INTERNAL, "VersionedScriptableObject")
        self.value = definition(CONTRACTS, "DemoValue")

    def reader(self, key, annotations=()):
        return TypeKeyReader(key, self.inventories, self.identities, {INTERNAL}, "focused key", annotations)

    def array(self, rank=2, sizes="", bounds="", element=None):
        return "array(" + str(rank) + "," + part(element or self.payload) + ",sizes=" + sizes + "bounds=" + bounds + ")"

    def test_actual_v6_rank_two_key_and_original_empty_bounds(self):
        key = "array(2,103:type(33:assemblya.implementation.internal/33:AssemblyA.Implementation.Internal/18:M05InternalPayload@0),sizes=bounds=0,0,)"
        self.assertEqual(key, self.array(bounds="0,0,"))
        before = copy.deepcopy(self.inventories)
        for spelling in (key, self.array()):
            reader = self.reader(spelling)
            result = reader.read()
            self.assertEqual(result["fullName"], PAYLOAD + "[,]")
            self.assertEqual(result["elementShape"], "array-rank-2")
            self.assertTrue(result["containsShadowTypes"])
            self.assertEqual(reader.raw_key, spelling)
            self.assertEqual(reader.data, spelling.encode("utf-8"))
            self.assertEqual(reader.at, len(reader.data))
        self.assertEqual(self.inventories, before)

    def test_array_rank_one_stays_distinct_from_vector(self):
        for bounds in ("", "0,"):
            self.assertEqual(self.reader(self.array(1, bounds=bounds)).read()["fullName"], PAYLOAD + "[*]")
        self.assertEqual(self.reader("szarray(" + self.payload + ")").read()["fullName"], PAYLOAD + "[]")
        self.assertEqual(self.reader(self.array(32, bounds="0," * 32)).read()["fullName"], PAYLOAD + "[" + "," * 31 + "]")

    def test_array_sizes_nonzero_partial_and_overrank_bounds_rejected(self):
        keys = [self.array(sizes="0,"), self.array(sizes="2,"), self.array(sizes="2147483647,"),
                self.array(bounds="0,"), self.array(bounds="0,0,0,"), self.array(bounds="0,1,"),
                self.array(bounds="-1,0,"), self.array(bounds="-2147483648,0,"),
                self.array(bounds="2147483647,0,"), self.array(0), self.array(33)]
        for key in keys:
            with self.subTest(key=key), self.assertRaises(VerificationError): self.reader(key).read()

    def test_array_numbers_and_delimiters_are_canonical_and_bounded(self):
        for bounds in ("00,0,", "-0,0,", "+0,0,", "0, 0,", "0,0", "0,,0,", ",", "0,0,,",
                       "2147483648,0,", "-2147483649,0,", "999999999999,0,", "0;0,", "0.0,0,"):
            with self.subTest(bounds=bounds), self.assertRaises(VerificationError):
                self.reader(self.array(bounds=bounds)).read()
        for key in (self.array().replace("array(2,", "array(02,"), self.array() + "junk",
                    self.array().replace("sizes=bounds=", "bounds=sizes="), self.array(sizes="-1,")):
            with self.subTest(key=key), self.assertRaises(VerificationError): self.reader(key).read()

    def test_actual_v6_private_field_keys_need_exact_annotations(self):
        cases = [("qualified(1,0,0,0,type(33:assemblya.implementation.internal/33:AssemblyA.Implementation.Internal/25:VersionedScriptableObject@0))", INTERNAL, DATA),
                 ("qualified(1,0,0,0,type(19:assemblya.contracts/19:AssemblyA.Contracts/9:DemoValue@0))", CONTRACTS, VALUE)]
        for key, assembly, full_name in cases:
            with self.subTest(key=key):
                with self.assertRaisesRegex(VerificationError, "unbound field diagnostic attributes"):
                    self.reader(key).read()
                reader = self.reader(key, [(assembly, full_name, 1)])
                result = reader.read()
                self.assertEqual(result["fullName"], full_name)
                self.assertEqual(result["elementShape"], "")
                self.assertEqual(result["containsShadowTypes"], assembly == INTERNAL)
                self.assertEqual(reader.raw_key, key)
                self.assertEqual(reader.data, key.encode())

    def test_field_annotation_assembly_type_and_flag_must_all_match(self):
        key = "qualified(1,0,0,0," + self.data + ")"
        for annotation in ((CONTRACTS, DATA, 1), (INTERNAL.casefold(), DATA, 1), (INTERNAL, VALUE, 1),
                           (INTERNAL, DATA, 2), (INTERNAL, DATA, 0)):
            with self.subTest(annotation=annotation), self.assertRaises(VerificationError):
                self.reader(key, [annotation]).read()
        for unbound in (self.data.replace("VersionedScriptableObject", "UnknownScriptableObject"),
                        self.data.replace("@0)", "@1)")):
            with self.assertRaises(VerificationError):
                self.reader("qualified(1,0,0,0," + unbound + ")", [(INTERNAL, DATA, 1)]).read()

    def test_field_annotation_input_is_exact_tuple_with_uint16_not_bool(self):
        for flags in (True, False, -1, 65536, 1.0, "1", None):
            with self.subTest(flags=flags), self.assertRaises(VerificationError):
                self.reader(self.data, [(INTERNAL, DATA, flags)])
        for annotations in (None, "anything", [[INTERNAL, DATA, 1]], [(INTERNAL, DATA)],
                            [(INTERNAL, DATA, 1, "extra")], [("", DATA, 1)], [(INTERNAL, "", 1)]):
            with self.subTest(annotations=annotations), self.assertRaises(VerificationError):
                self.reader(self.data, annotations)
        # Numeric bounds are checked independently of the caller's provenance
        # obligation: exact byte-derived UInt16 flags, not a global attrs=1 list.
        self.reader(self.data, [(INTERNAL, DATA, 0)]).read()
        key = "qualified(65535,0,0,0," + self.data + ")"
        self.assertEqual(self.reader(key, [(INTERNAL, DATA, 65535)]).read()["fullName"], DATA)
        for attrs in ("65536", "4294967295", "01", "-1", "+1"):
            with self.subTest(attrs=attrs), self.assertRaises(VerificationError):
                self.reader("qualified(" + attrs + ",0,0,0," + self.data + ")", [(INTERNAL, DATA, 1)]).read()

    def test_field_annotations_never_authorize_composites_or_nested_wrappers(self):
        qualified = "qualified(1,0,0,0," + self.data + ")"
        cases = ["qualified(1,0,0,0,szarray(" + self.data + "))",
                 "qualified(1,0,0,0," + qualified + ")", "szarray(" + qualified + ")",
                 "ptr(" + qualified + ")", self.array(element=qualified),
                 "qualified(0,0,1,0," + qualified + ")"]
        for key in cases:
            with self.subTest(key=key), self.assertRaises(VerificationError):
                self.reader(key, [(INTERNAL, DATA, 1)]).read()

    def test_length_prefixed_generic_arguments_cannot_inherit_root_annotations(self):
        generic = definition(INTERNAL, "Box`1").replace("@0)", "@1)")
        valid = "generic(" + generic + "," + part(self.data) + ")"
        self.assertEqual(self.reader(valid).read()["genericArguments"], [DATA])
        for argument in ("qualified(1,0,0,0," + self.data + ")", "qualified(0,0,1,0," + self.data + ")"):
            key = "generic(" + generic + "," + part(argument) + ")"
            with self.assertRaises(VerificationError): self.reader(key, [(INTERNAL, DATA, 1)]).read()
        with self.assertRaises(VerificationError):
            self.reader("qualified(1,0,0,0," + valid + ")", [(INTERNAL, DATA, 1)]).read()

    def test_byref_is_preserved_but_modifiers_pinned_and_duplicate_qualifiers_fail(self):
        for element, expected in ((self.data, DATA + "&"), ("szarray(" + self.data + ")", DATA + "[]&"),
                                  (self.array(), PAYLOAD + "[,]&")):
            result = self.reader("qualified(0,0,1,0," + element + ")").read()
            self.assertEqual(result["fullName"], expected)
            self.assertEqual(result["elementShape"], "byref")
        prefixes = ["0,0,0,0", "0,0,1,1", "0,0,2,0", "0,0,1,2", "1,0,1,0", "1,0,0,1"]
        prefixes += ["0," + str(mods) + ",1,0" for mods in (1, 31, 32, 63)]
        prefixes += ["1," + str(mods) + ",0,0" for mods in (1, 31, 32, 63)]
        for prefix in prefixes:
            with self.subTest(prefix=prefix), self.assertRaises(VerificationError):
                self.reader("qualified(" + prefix + "," + self.data + ")", [(INTERNAL, DATA, 1)]).read()
        byref = "qualified(0,0,1,0," + self.data + ")"
        for key in ("qualified(0,0,1,0," + byref + ")", "szarray(" + byref + ")"):
            with self.assertRaises(VerificationError): self.reader(key).read()


class ReflectedFieldMetadataTests(unittest.TestCase):
    def test_actual_field_order_flags_reflection_spelling_and_full_owner_identity(self):
        data = make_type_pe([
            dict(name="Owner", fields=[dict(name="zLocal", flags=1, signature=b"\x06\x12\x0c"),
                                       dict(name="aExternal", flags=6, signature=b"\x06\x12\x11"),
                                       dict(name="number", flags=0x21, signature=b"\x06\x08")]),
            dict(name="Payload", namespace="Nested.Scope", flags=2, parent=2),
        ], extra_refs=[("Payload", "External.Scope")])
        proof = MethodProof(data, "actual field rows")
        old_fields = proof.fields("Example.Owner")
        self.assertEqual(proof.reflection_fields("Example.Owner"), [
            dict(name="zLocal", type="Example.Owner+Nested.Scope.Payload", assembly="Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null", flags=1),
            dict(name="aExternal", type="External.Scope.Payload", assembly="mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=null", flags=6),
            dict(name="number", type="System.Int32", assembly="mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=null", flags=0x21),
        ])
        self.assertEqual(proof.fields("Example.Owner"), old_fields)
        self.assertTrue(all(set(row) == {"name", "type", "flags"} for row in old_fields))
        self.assertEqual(proof.reflection_fields("Example.Owner+Nested.Scope.Payload"), [])
        with self.assertRaises(VerificationError): proof.reflection_fields("Example.Missing")

    def test_reflected_composite_fields_preserve_declared_full_assembly_scope(self):
        proof = MethodProof(make_type_pe([
            dict(name="Owner", fields=[dict(name="generic", signature=b"\x06\x15\x12\x0c\x01\x12\x11"),
                                       dict(name="array", signature=b"\x06\x1d\x12\x11")]),
            dict(name="Box`1", namespace="Nested.Scope", flags=2, parent=2, arity=1),
        ], extra_refs=[("Payload", "External.Scope")]), "composite fields")
        core = "mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=null"
        self.assertEqual(proof.reflection_fields("Example.Owner"), [
            dict(name="generic", type="Example.Owner+Nested.Scope.Box`1[[External.Scope.Payload, " + core + "]]",
                 assembly="Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null", flags=6),
            dict(name="array", type="External.Scope.Payload[]", assembly=core, flags=6),
        ])

    def test_reflected_field_signature_malformed_modified_or_trailing_bytes_fail(self):
        for signature in (b"\x05\x08", b"\x06", b"\x06\x08\x00", b"\x06\x1f\x05\x08", b"\x06\x45\x08"):
            with self.subTest(signature=signature):
                proof = MethodProof(make_type_pe([dict(name="Owner", fields=[dict(name="field", signature=signature)])]), "bad field")
                with self.assertRaises(VerificationError): proof.reflection_fields("Example.Owner")


if __name__ == "__main__":
    unittest.main()
