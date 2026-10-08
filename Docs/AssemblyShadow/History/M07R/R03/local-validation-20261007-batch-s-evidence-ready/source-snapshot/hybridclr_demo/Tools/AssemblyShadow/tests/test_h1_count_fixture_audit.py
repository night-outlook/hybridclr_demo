"""Byte-level regressions for the independent H1 count-fixture auditor."""
from __future__ import annotations

from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shadow_tools import VerificationError
from test_m04_results import make_pe
from test_m05_results import make_type_pe
import h1_count_fixture_audit as audit


def _param_pe(methods=(), leading_params=()):
    """Build a small PE whose CLI rows are controlled directly by this test."""
    strings, blobs = bytearray(b"\0"), bytearray(b"\0")

    def string(value):
        index = len(strings)
        strings.extend(value.encode("utf-8") + b"\0")
        return index

    def blob(value):
        index = len(blobs)
        if len(value) < 128:
            blobs.append(len(value))
        else:
            raise AssertionError("test signature blob is unexpectedly large")
        blobs.extend(value)
        return index

    rows = {
        0: [struct.pack("<HHHHH", 0, string("Shape.dll"), 1, 0, 0)],
        2: [struct.pack("<IHHHHH", 0, string("<Module>"), 0, 0, 1, 1)],
        6: [],
        8: [],
        32: [struct.pack("<IHHHHIHHH", 0x8004, 1, 0, 0, 0, 0, 0,
                         string("Shape"), 0)],
    }

    for flags, sequence, name in leading_params:
        rows[8].append(struct.pack("<HHH", flags, sequence, string(name)))
    for method in methods:
        start = method.get("paramList", len(rows[8]) + 1)
        for flags, sequence, name in method.get("params", ()):
            rows[8].append(struct.pack("<HHH", flags, sequence, string(name)))
        rows[6].append(struct.pack(
            "<IHHHHH", 0, method.get("impl", 0), method.get("flags", 0x16),
            string(method.get("name", "Probe")), blob(method["signature"]), start))

    valid = sum(1 << table for table, values in rows.items() if values)
    table_data = struct.pack("<IBBBBQQ", 0, 2, 0, 0, 1, valid, 0)
    table_data += b"".join(struct.pack("<I", len(rows[table]))
                             for table in sorted(rows) if rows[table])
    table_data += b"".join(b"".join(rows[table])
                            for table in sorted(rows) if rows[table])

    streams = [("#~", table_data), ("#Strings", bytes(strings)),
               ("#Blob", bytes(blobs)), ("#GUID", bytes(range(16)))]
    root = (struct.pack("<IHHII", 0x424A5342, 1, 1, 0, 12) +
            b"v4.0.30319\0\0" + struct.pack("<HH", 0, len(streams)))
    offset = len(root) + sum(8 + ((len(name) + 4) & ~3)
                             for name, _ in streams)
    headers, content = b"", b""
    for name, data in streams:
        encoded = name.encode("ascii") + b"\0"
        headers += (struct.pack("<II", offset, len(data)) + encoded +
                    bytes(-len(encoded) % 4))
        content += data
        offset += len(data)
    metadata = root + headers + content

    pe = bytearray(make_pe()[:1024])
    pe.extend(metadata)
    struct.pack_into("<I", pe, 512 + 12, len(metadata))
    section = 0x98 + 224
    struct.pack_into("<I", pe, section + 8, len(pe) - 512)
    struct.pack_into("<I", pe, section + 16, len(pe) - 512)
    return bytes(pe)


class H1CountFixtureAuditTests(unittest.TestCase):
    def assert_rejected(self, data):
        with self.assertRaises(VerificationError):
            audit.inspect_bytes(data, "h1-test")

    def test_zero_child_target_is_observable_and_nested_names_are_escaped(self):
        data = make_type_pe([
            {"name": "Outer,Name", "namespace": r"Ns\One"},
            {"name": "Inner+Name", "namespace": "Ns.Two", "flags": 2},
        ], nested=[(3, 2)])
        result = audit.inspect_bytes(data, "nested-name")

        self.assertEqual(result["nestedGroups"][0]["count"], 1)
        self.assertEqual([item["rid"] for item in result["types"]], [1, 2, 3])
        self.assertEqual(result["types"][1]["fullName"], r"Ns\\One.Outer\,Name")
        self.assertEqual(result["types"][2]["fullName"],
                         r"Ns\\One.Outer\,Name+Ns.Two.Inner\+Name")

        zero_child = audit.inspect_bytes(make_type_pe([
            {"name": "Target", "namespace": "AssemblyShadow.H1Count"},
        ], nested=[]), "zero-child")
        self.assertEqual(zero_child["nestedGroups"], [])
        self.assertEqual(zero_child["types"][-1]["fullName"],
                         "AssemblyShadow.H1Count.Target")

    def test_nested_visibility_requires_complete_nestedclass_ownership(self):
        self.assert_rejected(make_type_pe([
            {"name": "TopLevelButNestedVisibility", "flags": 2},
        ], nested=[]))
        self.assert_rejected(make_type_pe([
            {"name": "Outer"},
            {"name": "ChildButTopLevelVisibility", "flags": 1},
        ], nested=[(3, 2)]))

    def test_param_rows_require_full_ownership_and_preserve_sequence_zero_names(self):
        result = audit.inspect_bytes(_param_pe(methods=[{
            "signature": b"\x00\x02\x08\x08\x08",
            "params": [(0, 0, ""), (0, 1, "first"), (0, 2, "")],
        }]), "params")
        rows = result["methods"][0]["paramRows"]
        self.assertEqual([row["sequence"] for row in rows], [0, 1, 2])
        self.assertEqual([row["name"] for row in rows], ["", "first", ""])

        self.assert_rejected(_param_pe(
            methods=[{"signature": b"\x00\x00\x08", "params": []}],
            leading_params=[(0, 1, "orphan")]))
        self.assert_rejected(_param_pe(leading_params=[(0, 1, "no-method")]))

    def test_signature_rejects_explicitthis_and_nested_byref_shapes(self):
        for signature in (
                b"\x00\x01\x08\x10\x10\x08",  # byref<byref<int32>>
                b"\x00\x01\x08\x1d\x10\x08",  # array<byref<int32>>
                b"\x40\x00\x08"):              # EXPLICITTHIS
            self.assert_rejected(_param_pe(methods=[{"signature": signature}]))

        result = audit.inspect_bytes(_param_pe(methods=[
            {"name": "StaticMixed", "flags": 0x16,
             "signature": b"\x00\x02\x08\x10\x08\x1d\x0e"},
            {"name": "InstanceArray", "flags": 0x06,
             "signature": b"\x20\x01\x08\x1d\x08"},
        ]), "valid-signatures")
        self.assertEqual([method["signature"]["instance"]
                          for method in result["methods"]], [False, True])
        self.assertEqual(result["methods"][0]["signature"]["parameterTypes"],
                         ["System.Int32&", "System.String[]"])

    def test_oversized_file_is_rejected_before_reading_contents(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "oversized.dll"
            with path.open("wb") as stream:
                stream.truncate(audit.MAX_DLL_BYTES + 1)
            with self.assertRaises(VerificationError):
                audit.inspect_file(path)


if __name__ == "__main__":
    unittest.main()
