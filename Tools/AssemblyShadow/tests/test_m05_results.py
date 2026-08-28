"""Adversarial M05 byte/schema tests; synthetic DLLs are not Player evidence."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch as mock_patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from m05_types import CliTables, MethodProof, TypeKeyReader, read_type_inventory_bytes, read_type_inventory
from m04_metadata import read_identity
from shadow_tools import VerificationError
from test_m04_results import make_pe, SyntheticRuntimeSuite
import m05_results as v


def make_type_pe(types, name="Types", reference_assembly="mscorlib", nested=None, generic_rows=None, extra_refs=(), type_specs=()):
    strings, blobs = bytearray(b"\0"), bytearray(b"\0")
    def string(value):
        p = len(strings); strings.extend(value.encode() + b"\0"); return p
    def blob(value):
        p = len(blobs); blobs.append(len(value)); blobs.extend(value); return p
    rows = {0: [struct.pack("<HHHHH", 0, string(name + ".dll"), 1, 0, 0)],
            1: [struct.pack("<HHH", 6, string(t), string(ns)) for t, ns in [(t,"System") for t in ("Object", "ValueType", "Enum")] + list(extra_refs)],
            2: [struct.pack("<IHHHHH", 0, string("<Module>"), 0, 0, 1, 1)], 4: [], 6: [], 9: [], 18: [], 20: [], 21: [], 23: [],
            27: [struct.pack("<H", blob(signature)) for signature in type_specs], 41: [], 42: [],
            32: [struct.pack("<IHHHHIHHH", 0x8004, 1, 0, 0, 0, 0, 0, string(name), 0)],
            35: [struct.pack("<HHHHIHHHH", 4, 0, 0, 0, 0, 0, string(reference_assembly), 0, 0)]}
    bodies = bytearray()
    for index, t in enumerate(types, 2):
        rows[2].append(struct.pack("<IHHHHH", t.get("flags", 1), string(t["name"]), string(t.get("namespace", "Example")),
                                   t.get("extends", 5), len(rows[4]) + 1, len(rows[6]) + 1))
        if "parent" in t: rows[41].append(struct.pack("<HH", index, t["parent"]))
        for interface in t.get("interfaces",[]):rows[9].append(struct.pack("<HH",index,interface))
        for n in range(t.get("arity", 0)):
            rows[42].append(struct.pack("<HHHH", n, 0, index * 2, string("T" + str(n))))
        for f in t.get("fields", []): rows[4].append(struct.pack("<HHH", 6, string(f["name"]), blob(f.get("signature", b"\x06\x08"))))
        for m in t.get("methods", []):
            body = m.get("body")
            rva = 0 if body is None else 0x2100 + len(bodies)
            if body is not None:
                assert len(body) < 64
                bodies.append(len(body) * 4 + 2); bodies.extend(body)
            rows[6].append(struct.pack("<IHHHHH", rva, m.get("impl", 0), m.get("flags", 6), string(m["name"]), blob(m.get("signature", b"\x20\x00\x01")), 1))
        if t.get("properties"):
            rows[21].append(struct.pack("<HH", index, len(rows[23]) + 1))
            for p in t["properties"]: rows[23].append(struct.pack("<HHH", 0, string(p["name"]), blob(p["signature"])))
        if t.get("events"):
            rows[18].append(struct.pack("<HH", index, len(rows[20]) + 1))
            for event in t["events"]: rows[20].append(struct.pack("<HHH", 0, string(event["name"]), event["type"]))
    if nested is not None: rows[41] = [struct.pack("<HH", *row) for row in nested]
    if generic_rows is not None: rows[42] = [struct.pack("<HHHH", number, 0, owner, string("T")) for number, owner in generic_rows]
    rows = {table: items for table, items in rows.items() if items}
    valid = sum(1 << table for table in rows)
    tables = struct.pack("<IBBBBQQ", 0, 2, 0, 0, 1, valid, 0)
    tables += b"".join(struct.pack("<I", len(rows[table])) for table in sorted(rows))
    tables += b"".join(b"".join(rows[table]) for table in sorted(rows))
    streams = [("#~", tables), ("#Strings", bytes(strings)), ("#Blob", bytes(blobs)), ("#GUID", bytes(range(16)))]
    root = struct.pack("<IHHII", 0x424a5342, 1, 1, 0, 12) + b"v4.0.30319\0\0" + struct.pack("<HH", 0, len(streams))
    offset = len(root) + sum(8 + ((len(n) + 4) & ~3) for n, _ in streams)
    headers, content = b"", b""
    for n, data in streams:
        raw = n.encode() + b"\0"
        headers += struct.pack("<II", offset, len(data)) + raw + bytes(-len(raw) % 4)
        content += data; offset += len(data)
    metadata = root + headers + content
    pe = bytearray(make_pe()[:1024]) + metadata
    struct.pack_into("<I", pe, 512 + 12, len(metadata))
    section = 0x98 + 224
    struct.pack_into("<I", pe, section + 8, len(pe) - 512)
    struct.pack_into("<I", pe, section + 16, len(pe) - 512)
    # Keep the fixture loadable by the independent pinned dnlib reader too:
    # its RVA translation requires real PE alignment/image-size fields.
    struct.pack_into("<III", pe, 0x98 + 28, 0x400000, 0x2000, 0x200)
    struct.pack_into("<I", pe, 0x98 + 56, (0x2000 + len(pe) - 512 + 0x1fff) & ~0x1fff)
    struct.pack_into("<I", pe, 512 + 16, 1)  # COMIMAGE_FLAGS_ILONLY
    assert len(bodies) < 256
    pe[768:768 + len(bodies)] = bodies
    return bytes(pe)


def make_module_pe():
    return make_type_pe([
        dict(name="RuntimeModule", namespace="System.Reflection", fields=[dict(name="assembly", signature=b"\x06\x12\x10")], methods=[
            dict(name="GetType", flags=0x46, signature=b"\x20\x03\x12\x11\x0e\x02\x02", body=b"\x02\x03\x04\x05\x28\x06\0\0\x06\x2a"),
            dict(name="GetTypes", flags=0x46, signature=b"\x20\x00\x1d\x12\x11", body=b"\x16\x28\x04\0\0\x06\x2a"),
            dict(name="get_Assembly", flags=0x46, signature=b"\x20\x00\x12\x10", body=b"\x02\x7b\x01\0\0\x04\x2a"),
            dict(name="InternalGetTypes", impl=4096, flags=0x16, signature=b"\x00\x01\x1d\x12\x11\x18"),
        ]),
        dict(name="RuntimeAssembly", namespace="System.Reflection", methods=[dict(name="GetManifestModuleInternal", impl=4096, signature=b"\x20\x00\x12\x15")]),
        dict(name="Assembly", namespace="System.Reflection", methods=[dict(name="InternalGetType", impl=4096, signature=b"\x20\x04\x12\x11\x12\x15\x0e\x02\x02")]),
    ], name="mscorlib", extra_refs=[("Type", "System"), ("Module", "System.Reflection")])


class TypeMetadataTests(unittest.TestCase):
    def test_actual_typedef_order_nesting_arity_kind_and_visibility(self):
        data = make_type_pe([
            dict(name="ZOuter`1", arity=1),
            dict(name="Inner`1", namespace="", flags=2, parent=2, arity=2),
            dict(name="HiddenOuter", flags=0),
            dict(name="VisibleInner", namespace="", flags=2, parent=4),
            dict(name="Interface", flags=0x21), dict(name="Struct", extends=9), dict(name="Enum", extends=13),
        ])
        inventory = read_type_inventory_bytes(data)
        rows = inventory["types"]
        self.assertEqual(inventory["assemblyName"], "Types")
        self.assertEqual([r["name"] for r in rows], ["ZOuter`1", "Inner`1", "HiddenOuter", "VisibleInner", "Interface", "Struct", "Enum"])
        self.assertEqual(rows[1], dict(fullName="Example.ZOuter`1+Inner`1", namespaceName="", name="Inner`1", nestingPath=["ZOuter`1"], genericArity=2, kind="class", isExported=True))
        self.assertFalse(rows[3]["isExported"])
        self.assertEqual([r["kind"] for r in rows[-3:]], ["interface", "valuetype", "enum"])

    def test_each_nested_typedef_namespace_matches_pinned_dnlib_reflection_name(self):
        # These are actual PE/NestedClass rows, not compiler-shaped assumptions:
        # generated nested TypeDefs can retain a nonempty Namespace heap entry.
        data = make_type_pe([
            dict(name="Outer`1", arity=1),
            dict(name="Inner`1", namespace="Inner.Scope", flags=2, parent=2, arity=2),
            dict(name="PlainLeaf", namespace="", flags=2, parent=3, arity=2),
            dict(name="DeepLeaf", namespace="Leaf.Scope", flags=2, parent=4, arity=2),
        ])
        rows = read_type_inventory_bytes(data)["types"]
        self.assertEqual([row["fullName"] for row in rows], [
            "Example.Outer`1", "Example.Outer`1+Inner.Scope.Inner`1",
            "Example.Outer`1+Inner.Scope.Inner`1+PlainLeaf",
            "Example.Outer`1+Inner.Scope.Inner`1+PlainLeaf+Leaf.Scope.DeepLeaf",
        ])
        self.assertEqual([row["namespaceName"] for row in rows], ["Example", "Inner.Scope", "", "Leaf.Scope"])
        self.assertEqual([row["name"] for row in rows], ["Outer`1", "Inner`1", "PlainLeaf", "DeepLeaf"])
        self.assertEqual([row["nestingPath"] for row in rows], [[], ["Outer`1"], ["Outer`1", "Inner`1"], ["Outer`1", "Inner`1", "PlainLeaf"]])
        self.assertEqual([row["genericArity"] for row in rows], [1, 2, 2, 2])
        self.assertTrue(all(row["kind"] == "class" and row["isExported"] for row in rows))

    def test_nested_namespace_and_name_escaping_matches_pinned_dnlib(self):
        rows = read_type_inventory_bytes(make_type_pe([
            dict(name="Outer+Name", namespace="Out+Space"),
            dict(name="Inner+Name", namespace="In+Space", flags=2, parent=2),
            dict(name="Leaf[Name]", namespace="Leaf,Space", flags=2, parent=3),
        ]))["types"]
        # Cross-checked against the repository's pinned dnlib ReflectionFullName.
        self.assertEqual(rows[-1]["fullName"], r"Out\+Space.Outer\+Name+In\+Space.Inner\+Name+Leaf\,Space.Leaf\[Name\]")
        self.assertEqual(rows[-1]["namespaceName"], "Leaf,Space")
        self.assertEqual(rows[-1]["name"], "Leaf[Name]")
        self.assertEqual(rows[-1]["nestingPath"], ["Outer+Name", "Inner+Name"])

    def test_nested_siblings_are_distinct_by_actual_namespace_without_sorting(self):
        types = [dict(name="Outer"), dict(name="Same", namespace="Z.Scope", flags=2, parent=2),
                 dict(name="Same", namespace="A.Scope", flags=2, parent=2)]
        rows = read_type_inventory_bytes(make_type_pe(types))["types"]
        self.assertEqual([row["fullName"] for row in rows], ["Example.Outer", "Example.Outer+Z.Scope.Same", "Example.Outer+A.Scope.Same"])
        types[-1]["namespace"] = "Z.Scope"
        with self.assertRaisesRegex(VerificationError, "duplicate logical type definition"):
            read_type_inventory_bytes(make_type_pe(types))

    def test_arity_is_metadata_not_name_suffix_and_fake_corlib_base_is_class(self):
        self.assertEqual(read_type_inventory_bytes(make_type_pe([dict(name="Name`7", arity=2)]))["types"][0]["genericArity"], 2)
        fake = read_type_inventory_bytes(make_type_pe([dict(name="PretendEnum", extends=13)], reference_assembly="UserAssembly"))
        self.assertEqual(fake["types"][0]["kind"], "class")
        core = read_type_inventory_bytes(make_type_pe([dict(name="Enum", namespace="System", extends=9)], name="mscorlib"))
        self.assertEqual(core["types"][0]["kind"], "class")

    def test_nested_cycles_duplicates_visibility_and_generic_owner_fail(self):
        types = [dict(name="A", flags=2), dict(name="B", flags=2)]
        fixtures = [make_type_pe(types, nested=[(2, 3), (3, 2)]), make_type_pe(types, nested=[(2, 3), (2, 3)]),
                    make_type_pe([dict(name="A")], nested=[(2, 9)]), make_type_pe([dict(name="A", flags=2)]),
                    make_type_pe([dict(name="A"), dict(name="A")]),
                    make_type_pe([dict(name="A")], generic_rows=[(0, 4), (0, 4)]),
                    make_type_pe([dict(name="A")], generic_rows=[(1, 4)]),
                    make_type_pe([dict(name="A")], generic_rows=[(0, 99)])]
        for data in fixtures:
            with self.subTest(size=len(data)):
                with self.assertRaises(VerificationError): read_type_inventory_bytes(data)

    def test_type_metadata_range_string_and_extends_tampering_fail(self):
        valid = make_type_pe([dict(name="A")])
        tables = CliTables(valid)
        table_offset = valid.index(tables.reader.data)
        typedef = table_offset + tables.offsets[2] + sum(tables.widths[2])
        for offset, value in ((typedef + 4, 65535), (typedef + 6, 65535), (typedef + 8, 65535), (typedef + 10, 0), (typedef + 12, 2)):
            data = bytearray(valid); struct.pack_into("<H", data, offset, value)
            with self.assertRaises(VerificationError): read_type_inventory_bytes(data)
        data = bytearray(valid); position = valid.index(b"Example\0"); data[position] = 0xff
        with self.assertRaises(VerificationError): read_type_inventory_bytes(data)

    def test_type_inventory_hash_and_path_are_actual(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); path = root / "Types.dll"; path.write_bytes(make_type_pe([dict(name="A")]))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(read_type_inventory(path, digest, "Types")["types"][0]["name"], "A")
            for sha, name in (("0" * 64, "Types"), (digest, "Other")):
                with self.assertRaises(VerificationError): read_type_inventory(path, sha, name)
            link = root / "alias.dll"; link.symlink_to(path)
            with self.assertRaises(VerificationError): read_type_inventory(link)


class MethodByteProofTests(unittest.TestCase):
    def test_exact_six_module_witnesses_and_actual_icall_flags(self):
        data = make_module_pe(); proof = MethodProof(data, "module fixture")
        rows = proof.witnesses()
        self.assertEqual([r["name"] for r in rows], ["GetType", "GetTypes", "get_Assembly", "GetManifestModuleInternal", "InternalGetType", "InternalGetTypes"])
        self.assertEqual([r["hasBody"] for r in rows], [True, True, True, False, False, False])
        self.assertTrue(rows[2]["instructions"][1].startswith("0001:ldfld field:System.Reflection.Assembly System.Reflection.RuntimeModule::assembly | mscorlib,"))
        table_start = data.index(proof.tables.reader.data)
        method_start = table_start + proof.tables.offsets[6]
        for offset in (method_start + 4, method_start + 6, method_start + 3 * sum(proof.tables.widths[6]) + 4):
            changed = bytearray(data); struct.pack_into("<H", changed, offset, 4096 if offset == method_start + 4 else 0)
            with self.assertRaises(VerificationError): MethodProof(bytes(changed), "bad flags").witnesses()

    def test_method_flags_signature_and_instructions_come_from_bytes(self):
        proof = MethodProof(make_type_pe([dict(name="Owner", methods=[dict(name="Test", body=b"\x02\x2a", signature=b"\x20\x00\x1c")])]), "fixture")
        self.assertEqual(proof.member(6, 1)["fullName"], "System.Object Example.Owner::Test()")
        self.assertEqual(proof.instructions(1), ["0000:ldarg.0", "0001:ret"])
        with self.assertRaisesRegex(VerificationError, "missing/ambiguous linked module method"): proof.witnesses()

    def test_branch_labels_are_instruction_indices_and_bad_targets_fail(self):
        proof = MethodProof(make_type_pe([dict(name="Owner", methods=[dict(name="Test", body=b"\x2b\x01\x00\x2a")])]), "fixture")
        self.assertEqual(proof.instructions(1), ["0000:br.s ->2", "0001:nop", "0002:ret"])
        for body in (b"\x2b\xff\x2a", b"\xff", b"\x28\x01"):
            proof = MethodProof(make_type_pe([dict(name="Owner", methods=[dict(name="Test", body=body)])]), "fixture")
            with self.assertRaises(VerificationError): proof.instructions(1)


class TypeInventoryEvidenceTests(unittest.TestCase):
    def test_nested_namespace_claims_and_rehashed_namespace_byte_changes_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "Types.dll"
            types = [dict(name="Outer"), dict(name="Inner", namespace="Nested.Scope", flags=2, parent=2)]
            path.write_bytes(make_type_pe(types))
            identity = read_identity(path)
            claimed = read_type_inventory(path)
            self.assertEqual(claimed["types"][1]["fullName"], "Example.Outer+Nested.Scope.Inner")
            v.verify_type_inventories([claimed], [identity], "nested namespace fixture")
            for fields in (dict(fullName="Example.Outer+Inner"), dict(namespaceName="")):
                changed = copy.deepcopy(claimed); changed["types"][1].update(fields)
                with self.assertRaisesRegex(VerificationError, "type inventory differs"):
                    v.verify_type_inventories([changed], [identity], "dropped nested namespace")
            types[-1]["namespace"] = "Changed.Scope"
            path.write_bytes(make_type_pe(types))
            # Even rebinding the identity/hash cannot preserve a stale type claim.
            with self.assertRaisesRegex(VerificationError, "type inventory differs"):
                v.verify_type_inventories([claimed], [read_identity(path)], "rehashed namespace mutation")

    def test_type_inventory_exact_schema_and_rehashed_claims_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "Types.dll"; path.write_bytes(make_type_pe([dict(name="Outer", arity=1), dict(name="Inner", namespace="", flags=2, parent=2)]))
            identity = read_identity(path); actual = read_type_inventory(path)
            v.verify_type_inventories([actual], [identity], "fixture")
            mutations = [lambda a: a["types"].reverse(), lambda a: a["types"][0].update(genericArity=True),
                         lambda a: a["types"][0].update(genericArity=65537), lambda a: a["types"][0].update(isExported=1),
                         lambda a: a["types"][1].update(nestingPath=[]), lambda a: a["types"][0].update(kind="enum"),
                         lambda a: a["types"][0].pop("name"), lambda a: a["types"][0].update(metadataToken=0x2000002),
                         lambda a: a["types"].append(copy.deepcopy(a["types"][0])), lambda a: a.update(assemblyName="Other")]
            for mutation in mutations:
                bad = copy.deepcopy(actual); mutation(bad)
                with self.assertRaises(VerificationError): v.verify_type_inventories([bad], [identity], "rehashed receipt")

    def test_rejected_output_is_never_admitted_or_partially_emitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp).resolve(); v._no_rejected_output(parent, "absent")
            output = parent / "LayoutMismatch-must-not-be-admitted"; output.mkdir()
            with self.assertRaises(VerificationError): v._no_rejected_output(parent, "admitted")
            output.rmdir(); output.with_name(output.name + ".building-123").mkdir()
            with self.assertRaises(VerificationError): v._no_rejected_output(parent, "partial")


class TypeProofBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        core = self.root / "mscorlib.dll"; core.write_bytes(make_module_pe())
        fields = []
        for name in v.TYPE_INFO_FIELDS.split():
            code = 8 if name in v.TYPE_INFO_INTS else 2 if name in v.TYPE_INFO_BOOLS else 11 if name in v.TYPE_INFO_COUNTERS else 14
            fields.append(dict(name=name, signature=bytes([6, code])))
        runtime = self.root / "HybridCLR.Runtime.dll"
        runtime.write_bytes(make_type_pe([dict(name="AssemblyShadowTypeResolutionInfo", namespace="HybridCLR", fields=fields)], name="HybridCLR.Runtime"))
        self.player = dict(inputSnapshot=str(self.root), typeProofPath=str(self.root / "m05-type-proof.json"),
                           nativeLibrarySha256="1" * 64, buildGuid="a" * 32,
                           assemblyIdentities=sorted([read_identity(core), read_identity(runtime)], key=lambda row: row["name"]))
        self.snapshot = dict(snapshotHash="2" * 64, linkedPlayerReceiptHash="3" * 64, playerBuildOptions=1)
        self.proof = dict(schemaVersion=1, milestone="M05", policy="active-type-world:1", compileSnapshotHash="2" * 64,
                          linkedPlayerReceiptHash="3" * 64, nativeLibrarySha256="1" * 64, buildGuid="a" * 32, developmentBuild=True,
                          assemblies=[read_type_inventory(a["path"]) for a in self.player["assemblyIdentities"]],
                          moduleMethods=MethodProof(core.read_bytes(), core).witnesses())
        self.write()

    def write(self):
        path = Path(self.player["typeProofPath"]); path.write_text(json.dumps(self.proof))
        self.player["typeProofSha256"] = v.digest(path)

    def test_complete_byte_bound_type_proof(self):
        self.assertEqual(v.verify_type_proof(self.player, self.snapshot, "Player"), self.proof)

    def test_rehashed_schema_crossbuild_or_wrapper_claims_fail(self):
        mutations = [lambda p: p.update(schemaVersion=True), lambda p: p.update(milestone="M04"),
                     lambda p: p.update(policy="other"), lambda p: p.update(compileSnapshotHash="4" * 64),
                     lambda p: p.update(linkedPlayerReceiptHash="4" * 64), lambda p: p.update(buildGuid="b" * 32),
                     lambda p: p.update(nativeLibrarySha256="4" * 64), lambda p: p.update(developmentBuild=1),
                     lambda p: p.pop("assemblies"), lambda p: p.update(extra=False),
                     lambda p: p["moduleMethods"].reverse(), lambda p: p["moduleMethods"][0].update(hasBody=False),
                     lambda p: p["moduleMethods"][0].update(implementationFlags=True),
                     lambda p: p["moduleMethods"][0]["instructions"].append("0010:ret"),
                     lambda p: p["moduleMethods"][0].update(signature="fake")]
        original = copy.deepcopy(self.proof)
        for mutation in mutations:
            self.proof = copy.deepcopy(original); mutation(self.proof); self.write()
            with self.assertRaises(VerificationError): v.verify_type_proof(self.player, self.snapshot, "rehashed proof")

    def test_actual_linked_type_bytes_cannot_be_replaced(self):
        path = Path(self.player["assemblyIdentities"][0]["path"])
        path.write_bytes(make_type_pe([dict(name="Changed")], name="HybridCLR.Runtime"))
        with self.assertRaises(VerificationError): v.verify_type_proof(self.player, self.snapshot, "changed DLL")


def key_part(value): return str(len(value.encode("utf-8"))) + ":" + value


def type_key(assembly, declarations):
    return "type(" + key_part(assembly.casefold()) + "".join("/" + key_part(ns) + "/" + key_part(name) + "@" + str(arity) for ns, name, arity in declarations) + ")"


def type_info(assembly="Types", key=None, shadow=True):
    value = dict(schemaVersion=1, logicalAssembly=assembly, executionModeCode=int(shadow), executionMode="InterpreterShadow" if shadow else "AotBaseline",
                 isActive=True, physicalImageKind="Interpreter" if shadow else "Aot", typeKey=key or type_key("Types", [("Example", "A", 0)]),
                 inputTypePointer="", activeTypePointer="", baselineTypePointer="", pointerDetailsAvailable=False, baselinePointerAvailable=False,
                 containsShadowTypes=shadow)
    value.update({key: 0 for key in v.TYPE_INFO_COUNTERS})
    return value


class NativeTypeInfoTests(unittest.TestCase):
    def test_exact_eighteen_fields_uint64_and_pointer_flags(self):
        value = type_info(); value["definitionCacheHits"] = (1 << 64) - 1
        self.assertEqual(v.verify_type_info(value, "native"), value)
        for key in value:
            bad = copy.deepcopy(value); bad.pop(key)
            with self.assertRaises(VerificationError): v.verify_type_info(bad, "omitted field")
        for mutation in (dict(schemaVersion=True), dict(executionModeCode=True), dict(isActive=1), dict(definitionCacheHits=-1),
                         dict(definitionCacheHits=1 << 64), dict(definitionCacheHits=float(1 << 63)), dict(definitionCacheHits=True),
                         dict(inputTypePointer="0x123"), dict(pointerDetailsAvailable=True), dict(extra=0),
                         dict(baselinePointerAvailable=True, baselineTypePointer="0x123")):
            with self.assertRaises(VerificationError): v.verify_type_info(dict(value, **mutation), "bad field")
        good = dict(value, pointerDetailsAvailable=True, inputTypePointer="0x100", activeTypePointer="0x100")
        v.verify_type_info(good, "optional real pointer details")

    def test_raw_typed_and_byte_bound_key_must_agree(self):
        inventory = read_type_inventory_bytes(make_type_pe([dict(name="A")]))
        inventories = {"Types": inventory["types"]}
        identities = {"Types": dict(fullName="Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")}
        info = type_info(); row = dict(operation="name-form", requested="Example.A", rawJson=json.dumps(info), info=info, sameType=True)
        self.assertEqual(v.verify_type_resolution(row, inventories, identities, {"Types"}, "observation")["fullName"], "Example.A")
        for mutation in (lambda r: r.update(rawJson=r["rawJson"].replace('"isActive": true', '"isActive": false')),
                         lambda r: r.update(rawJson='{"schemaVersion":1,' + r["rawJson"][1:]),
                         lambda r: r.update(sameType=False), lambda r: r.update(requested="Example.Other")):
            bad = copy.deepcopy(row); mutation(bad)
            with self.assertRaises(VerificationError): v.verify_type_resolution(bad, inventories, identities, {"Types"}, "bad raw observation")
        for key in (type_key("Unbound", [("Example","A",0)]), type_key("Types", [("Example","B",0)]), type_key("Types", [("Example","A",1)])):
            bad = copy.deepcopy(row); bad["info"]["typeKey"] = key; bad["rawJson"] = json.dumps(bad["info"])
            with self.assertRaises(VerificationError): v.verify_type_resolution(bad, inventories, identities, {"Types"}, "rehashed fake native key")

    def test_composite_key_arity_components_utf8_and_qualifiers(self):
        inventory = read_type_inventory_bytes(make_type_pe([dict(name="Box`1", arity=1), dict(name="é")]))
        inventories = {"Types": inventory["types"]}; identities = {"Types": dict(fullName="Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null")}
        element = type_key("Types", [("Example","é",0)]); definition = type_key("Types", [("Example","Box`1",1)])
        cases = [("szarray(" + element + ")", "Example.é[]"), ("ptr(" + element + ")", "Example.é*"),
                 ("qualified(0,0,1,0," + element + ")", "Example.é&"),
                 ("array(2," + key_part(element) + ",sizes=bounds=)", "Example.é[,]"),
                 ("generic(" + definition + "," + key_part(element) + ")", "Example.Box`1[[Example.é, " + identities["Types"]["fullName"] + "]]")]
        for key, expected in cases:
            result = TypeKeyReader(key, inventories, identities, {"Types"}).read()
            self.assertEqual(result["fullName"], expected); self.assertTrue(result["containsShadowTypes"])
        for key in (element.replace("2:é", "1:é"), "generic(" + definition + ")", "qualified(1,0,1,0," + element + ")", element + "junk"):
            with self.assertRaises(VerificationError): TypeKeyReader(key, inventories, identities, {"Types"}).read()


class ResourceAndBenchmarkTests(unittest.TestCase):
    def test_resources_require_original_bytes_three_phases_values_and_real_reload_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); original = root / "Original"; output = root / "Player.app"
            staged = output / "Contents/Data/StreamingAssets/AssemblyShadow/M01"
            bundles = []
            for name in ("versioned-data.bundle", "versioned-prefab.bundle", "business-scene.bundle"):
                data = ("synthetic " + name).encode(); sha = hashlib.sha256(data).hexdigest()
                bundles.append(dict(name=name, path="Bundles/" + name, sha256=sha))
                for directory in (original, staged):
                    (directory / "Bundles").mkdir(parents=True, exist_ok=True)
                    (directory / "Bundles" / name).write_bytes(data)
            frozen = dict(baselineBuildId="M01-Baseline-v1", bundles=bundles, assets=[dict(kind="scene", path="Assets/AssemblyShadowDemo/Scenes/Business.unity")])
            for directory in (original, staged): (directory / "baseline-manifest.json").write_text(json.dumps(frozen))
            result = dict(sceneObservations=[], typeResolutionObservations=[dict(operation="resource:prefab-asset:component", requested=v.RESOURCE_COMPONENT)],
                          identityObservations=[dict(operation="resource:scene-reload:new-component", left=v.RESOURCE_COMPONENT + "#-12", right=v.RESOURCE_COMPONENT + "#-34", sameObject=False)],
                          businessMarker=v.RESOURCE_MARKER)
            for phase in ("prefab", "scene-first", "scene-reload"):
                bundle = bundles[1 if phase == "prefab" else 2]
                result["sceneObservations"].append(dict(phase=phase, bundleName=bundle["name"], bundlePath=str(staged / bundle["path"]), bundleSha256=bundle["sha256"],
                    scenePath="" if phase == "prefab" else frozen["assets"][0]["path"].lower(), componentAssemblyName=v.INTERNAL, componentType=v.RESOURCE_COMPONENT,
                    businessMarker=v.RESOURCE_MARKER, error="", serializedValue=1234, baseSerializedValue=7, dataSerializedValue=5678, loaded=True, activeType=True, referenceIdentity=True))
                result["typeResolutionObservations"] += [dict(operation="resource:" + phase + ":" + label, requested=full_name) for label, full_name in
                                                          (("component",v.RESOURCE_COMPONENT),("data",v.RESOURCE_DATA),("value",v.RESOURCE_VALUE))]
            manifest, player = dict(_m01Root=str(original)), dict(playerOutput=str(output))
            self.assertEqual(len(v.verify_resources(result, manifest, player, "resource result")), 4)
            mutations = [lambda r:r["sceneObservations"].reverse(), lambda r:r["sceneObservations"][0].update(serializedValue=True),
                         lambda r:r["sceneObservations"][1].update(dataSerializedValue=1234), lambda r:r["sceneObservations"][0].update(referenceIdentity=False),
                         lambda r:r["sceneObservations"][0].update(bundleSha256="0"*64), lambda r:r["typeResolutionObservations"].pop(),
                         lambda r:r["identityObservations"][0].update(sameObject=True), lambda r:r["identityObservations"][0].update(right=r["identityObservations"][0]["left"])]
            for mutation in mutations:
                bad=copy.deepcopy(result);mutation(bad)
                with self.assertRaises(VerificationError):v.verify_resources(bad,manifest,player,"bad resource result")
            (staged / "Bundles/versioned-data.bundle").write_bytes(b"changed data input")
            with self.assertRaises(VerificationError):v.verify_resources(result,manifest,player,"changed actual data bytes")

    def test_benchmark_exact_workload_raw_timing_and_final_identity(self):
        benchmark = dict(enabled=True, finalSameType=True, warmupCount=1000, lookupCount=100000, elapsedTicks=123, stopwatchFrequency=1000000,
                         checksum=100000, requestedName="AssemblyA.Implementation.Internal.InternalEntry, AssemblyA.Implementation.Internal",
                         finalTypeName="AssemblyA.Implementation.Internal.InternalEntry", finalAssemblyName=v.INTERNAL)
        v.verify_benchmark(benchmark,True,"benchmark")
        for update in (dict(lookupCount=1000000),dict(elapsedTicks=0),dict(stopwatchFrequency=True),dict(finalSameType=False),dict(enabled=False),dict(finalTypeName="Other"),dict(checksum=float(100000))):
            with self.assertRaises(VerificationError):v.verify_benchmark(dict(benchmark,**update),True,"bad benchmark")


class EnumerationAndMemberTests(unittest.TestCase):
    def test_assignability_relations_are_actual_metadata_not_boolean_claims(self):
        proof=MethodProof(make_type_pe([dict(name="Contract",flags=0x21,extends=0),dict(name="Base"),
              dict(name="Derived",extends=12,interfaces=[8])]),"relations")
        relations=proof.type_relations("Example.Derived")
        full="Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null"
        self.assertEqual(relations,dict(base=("Example.Base",full),interfaces=[("Example.Contract",full)]))
        for interfaces in ([8,8],[65535]):
            with self.assertRaises(VerificationError):
                MethodProof(make_type_pe([dict(name="Contract",flags=0x21,extends=0),dict(name="Derived",interfaces=interfaces)]),"bad relations").type_relations("Example.Derived")

    def test_actual_generic_event_and_complete_member_signatures(self):
        data=make_type_pe([dict(name="Owner",fields=[dict(name="Field",signature=b"\x06\x12\x08")],
            methods=[dict(name="Echo",signature=b"\x20\x01\x12\x08\x12\x08",body=b"\x03\x2a")],
            properties=[dict(name="Property",signature=b"\x28\x00\x12\x08")],events=[dict(name="Changed",type=6)])],
            extra_refs=[("Action`1","System")],type_specs=[b"\x15\x12\x11\x01\x12\x08"])
        proof=MethodProof(data,"member signatures")
        rows=proof.reflection_members("Example.Owner")
        self.assertEqual([r["memberKind"] for r in rows],["method","field","property","event"])
        self.assertEqual(rows[0]["parameterTypes"],["Example.Owner"])
        self.assertEqual(rows[1]["fieldType"],"Example.Owner")
        self.assertEqual(rows[2]["returnType"],"Example.Owner")
        self.assertEqual(rows[3]["fieldType"],"System.Action`1[[Example.Owner, Types, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null]]")
        table_start=data.index(proof.tables.reader.data)
        for table in (18,21):
            bad=bytearray(data);struct.pack_into("<H",bad,table_start+proof.tables.offsets[table]+2,65535)
            with self.assertRaises(VerificationError):MethodProof(bytes(bad),"bad map").reflection_members("Example.Owner")

    def test_raw_enumeration_order_duplicates_and_ancestor_exported(self):
        base = read_type_inventory_bytes(make_type_pe([dict(name="Existing")]))
        patch = read_type_inventory_bytes(make_type_pe([dict(name="Existing"), dict(name="Hidden", flags=0), dict(name="Child", namespace="", flags=2, parent=3)]))
        fixture = dict(closureLoadOrder=["Types"], typeInventories=[patch])
        expected = [dict(operation=operation, assemblyName="Types", typeNames=[row["fullName"] for row in patch["types"] if operation != "Assembly.ExportedTypes" or row["isExported"]])
                    for operation in ("Assembly.GetTypes", "Assembly.DefinedTypes", "Assembly.ExportedTypes", "Module.GetTypes")]
        v.verify_enumerations(expected, fixture, {"Types": base["types"]}, "enumeration")
        for mutate in (lambda rows: rows.reverse(), lambda rows: rows[0]["typeNames"].reverse(),
                       lambda rows: rows[0]["typeNames"].append(rows[0]["typeNames"][0]),
                       lambda rows: rows[2]["typeNames"].append("Example.Hidden+Child")):
            bad=copy.deepcopy(expected); mutate(bad)
            with self.assertRaises(VerificationError): v.verify_enumerations(bad, fixture, {"Types": base["types"]}, "bad enumeration")

    def test_member_signatures_bind_actual_owner_and_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "Types.dll"
            path.write_bytes(make_type_pe([dict(name="Owner", fields=[dict(name="Value")], methods=[dict(name="Echo", signature=b"\x20\x01\x08\x08", body=b"\x03\x2a")])]))
            identity = read_identity(path); inventories={"Types":read_type_inventory(path)["types"]}
            row=dict(declaringType="Example.Owner", reflectedType="Example.Owner", memberName="Echo", memberKind="method", returnType="System.Int32",fieldType="",parameterTypes=["System.Int32"],sameMember=True,activeOwner=True)
            v.verify_members([row],{"Types":identity},inventories,{"Types"},"member")
            for mutation in (dict(returnType="System.String"),dict(parameterTypes=[]),dict(reflectedType="Example.Other"),dict(activeOwner=False),dict(sameMember=1),dict(memberName="Value")):
                with self.assertRaises(VerificationError):v.verify_members([dict(row,**mutation)],{"Types":identity},inventories,{"Types"},"bad member")


class NativePhaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.suite = SyntheticRuntimeSuite(self.root)

    def result(self, kind="positive"):
        early = kind == "early"
        result = self.suite.result("T04-03" if early else "T04-01", 123)
        result["mode"] = "T05-04-EarlyType" if early else "T05-09-LayoutMismatch" if kind == "layout" else "T05-01-P01"
        fixture = self.suite.fixtures["P03" if early else "P01"][0]
        if early:
            final = result["snapshots"][-1]
            final["phase"] = "aborted"
            final["diagnostics"]["baselineUses"] = [dict(name=v.INTERNAL,kind="TypeReflection",type=v.RESOURCE_COMPONENT,
                detail="Type.GetType FirstUseSequence=1",thread=(1<<64)-1,timestamp=(1<<64)-1)]
        if kind == "layout":
            result["patchId"] = "LayoutMismatch"; result["state"] = "FailedAfterCommit"
            for row in result["snapshots"][1:]:row["diagnostics"]["patchId"] = "LayoutMismatch"
            final = result["snapshots"][-1]; final["phase"] = "allocation-failure"
            final["diagnostics"].update(state="FailedAfterCommit",stateCode=v.prior.STATE_CODES["FailedAfterCommit"],lastError=16,
                detail="ShadowLayoutMismatch " + type_key(v.INTERNAL,[("AssemblyA.Implementation.Internal","VersionedPrefabComponent",0)]) + " Site=Object::NewAllocSpecific BaselineSize=32 ActiveSize=40")
        return result, fixture

    def check(self, result, fixture):
        path = self.root / ("m05-" + result["mode"] + ".json")
        raw = path.with_name(path.stem + "-native-diagnostics.json")
        raw.write_text(json.dumps(result["snapshots"][-1]["diagnostics"]))
        result.update(nativeDiagnosticsJson=raw.read_text(),rawDiagnosticsPath=str(raw),rawDiagnosticsSha256=v.digest(raw))
        v.verify_phases(result,self.suite.manifest,self.suite.players["on"],fixture["closureLoadOrder"],
                        {row["name"]:row for row in fixture["assemblyIdentities"]},path)

    def test_positive_private_metadata_publication_and_physical_order(self):
        result, fixture = self.result(); self.check(result,fixture)
        mutations=[lambda r:r["snapshots"].pop(1), lambda r:r["snapshots"][1].update(diagnostics=copy.deepcopy(r["snapshots"][-1]["diagnostics"])),
                   lambda r:r["snapshots"][2]["diagnostics"]["assemblies"][0].update(moduleInitializerRan=True),
                   lambda r:r["snapshots"][-1]["diagnostics"]["assemblies"][0].update(mvid="f"*36),
                   lambda r:r["snapshots"][-1]["diagnostics"]["ordinaryAssemblies"].reverse(),
                   lambda r:r["snapshots"][-1]["diagnostics"].update(generation=True),
                   lambda r:r["snapshots"][-1]["diagnostics"]["events"][0].update(sequence=0)]
        for mutate in mutations:
            bad=copy.deepcopy(result);mutate(bad)
            with self.assertRaises(VerificationError):self.check(bad,fixture)

    def test_early_type_use_only_after_actual_validation(self):
        result,fixture=self.result("early");self.check(result,fixture)
        for mutate in (lambda r:r["snapshots"][-1]["diagnostics"].update(baselineUses=[]),
                       lambda r:r["snapshots"][-1]["diagnostics"]["baselineUses"][0].update(kind="AssemblyReflection"),
                       lambda r:r["snapshots"][-1]["diagnostics"]["baselineUses"][0].update(type=""),
                       lambda r:r["snapshots"][-1]["diagnostics"]["baselineUses"][0].update(detail="unbound sequence"),
                       lambda r:r["snapshots"][2]["diagnostics"].update(baselineUses=copy.deepcopy(r["snapshots"][-1]["diagnostics"]["baselineUses"]))):
            bad=copy.deepcopy(result);mutate(bad)
            with self.assertRaises(VerificationError):self.check(bad,fixture)

    def test_layout_rejection_is_allocation_after_successful_commit(self):
        result,fixture=self.result("layout");self.check(result,fixture)
        for mutate in (lambda r:r["snapshots"][2]["diagnostics"].update(lastError=16),
                       lambda r:r["snapshots"][-1]["diagnostics"].update(state="Aborted",stateCode=v.prior.STATE_CODES["Aborted"]),
                       lambda r:r["snapshots"][-1]["diagnostics"].update(lastError=15),
                       lambda r:r["snapshots"][-1]["diagnostics"].update(detail="some error"),
                       lambda r:r["snapshots"][-1]["diagnostics"]["assemblies"][0].update(published=False)):
            bad=copy.deepcopy(result);mutate(bad)
            with self.assertRaises(VerificationError):self.check(bad,fixture)

    def test_field_guard_passes_full_allocation_failure_phase(self):
        result,fixture=self.result("layout")
        key = type_key(v.INTERNAL, [("AssemblyA.Implementation.Internal", "VersionedPrefabComponent", 0)])
        result["snapshots"][-1]["diagnostics"]["detail"] = "ShadowFieldLayoutMismatch " + key + " Site=Object::NewAllocSpecific"
        self.check(result,fixture)
        for mutate in (
            lambda r:r["snapshots"][-1]["diagnostics"].update(lastError=15),
            lambda r:r["snapshots"][-1]["diagnostics"].update(detail="ShadowFieldLayoutMismatch " + key + " Site=Object::Other"),
            lambda r:r["snapshots"][-1]["diagnostics"].update(detail="ShadowFieldLayoutMismatch " + key.replace("VersionedPrefabComponent", "OtherComponent") + " Site=Object::NewAllocSpecific"),
            lambda r:r["snapshots"][-1]["diagnostics"].update(detail="ShadowFieldLayoutMismatch " + key + " Site=Object::NewAllocSpecific\n"),
        ):
            bad=copy.deepcopy(result);mutate(bad)
            with self.assertRaises(VerificationError):self.check(bad,fixture)

    def test_layout_field_guard_matches_actual_detail_and_rejects_near_misses(self):
        key = type_key(v.INTERNAL, [("AssemblyA.Implementation.Internal", "VersionedPrefabComponent", 0)])
        field = "ShadowFieldLayoutMismatch " + key + " Site=Object::NewAllocSpecific"
        self.assertTrue(v._precise_allocation_guard(field))
        self.assertTrue(v._precise_allocation_guard(
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=32 ActiveSize=40"))
        for detail in (
            "ShadowFieldLayoutMismatch " + key + " Site=Object::Other",
            field + " BaselineSize=32 ActiveSize=40",
            "ShadowFieldLayoutMismatch " + key.replace("VersionedPrefabComponent", "OtherComponent") + " Site=Object::NewAllocSpecific",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=32 ActiveSize=32",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=032 ActiveSize=32",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=032 ActiveSize=40",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=0 ActiveSize=40",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=4294967296 ActiveSize=40",
            "ShadowLayoutMismatch " + key + " Site=Object::NewAllocSpecific BaselineSize=10000000000 ActiveSize=40",
            "ResourceAbiMismatch " + key + " Site=Object::NewAllocSpecific",
        ):
            self.assertFalse(v._precise_allocation_guard(detail), detail)

    def test_ordered_check_values_are_not_self_authorizing(self):
        rows=[dict(name="commit",actual="BaselineAlreadyUsed",expected="BaselineAlreadyUsed",actualCode=15,expectedCode=15)]
        v.verify_checks(rows,[("commit","BaselineAlreadyUsed",15)],"check")
        for update in (dict(actualCode=True),dict(expectedCode=0),dict(actual="Success",expected="Success",actualCode=0,expectedCode=0),dict(unknown=0)):
            with self.assertRaises(VerificationError):v.verify_checks([dict(rows[0],**update)],[("commit","BaselineAlreadyUsed",15)],"bad check")


class ProcessSuiteAndHeaderTests(unittest.TestCase):
    def test_all_nineteen_unique_processes_and_raw_companions_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            manifest=dict(baselineBuildId="M05-Baseline-test",runtimeAbiHash="a"*64)
            paths=[]
            for index,mode in enumerate(sorted(v.REQUIRED_MODES),1):
                path=root/("m05-"+mode+".json");path.write_text(json.dumps(dict(mode=mode,processId=index,passed=True)));paths.append(path)
                if mode!="T05-13-BenchmarkOff":path.with_name(path.stem+"-native-diagnostics.json").write_text("{}")
            def unit_case(path,*args):return json.loads(path.read_text())
            # Isolates suite inventory; individual result/byte gates have their
            # own tests. These mock rows are not real process acceptance.
            with mock_patch.object(v,"verify_case",side_effect=unit_case):
                result=v.verify_results(root,manifest,{}, {},{}, {},root/"on",root/"off")
                self.assertTrue(result["resultPassed"]);self.assertEqual(len(result["modes"]),19)
                paths[-1].write_text(json.dumps(dict(mode="T05-13-BenchmarkOff",processId=1,passed=True)))
                with self.assertRaisesRegex(VerificationError,"fresh unique"):v.verify_results(root,manifest,{}, {},{}, {},root/"on",root/"off")
                paths[-1].unlink()
                with self.assertRaisesRegex(VerificationError,"incomplete"):v.verify_results(root,manifest,{}, {},{}, {},root/"on",root/"off")
                partial=v.verify_results(root,manifest,{}, {},{}, {},root/"on",root/"off",True)
                self.assertFalse(partial["resultPassed"]);self.assertTrue(partial["diagnosticOnly"])
                self.assertEqual(partial["missingModes"],["T05-13-BenchmarkOff"])
                (root/"m05-T05-13-BenchmarkOff-native-diagnostics.json").write_text("{}")
                with self.assertRaisesRegex(VerificationError,"raw native"):v.verify_results(root,manifest,{}, {},{}, {},root/"on",root/"off",True)

    def test_result_header_exact_types_cross_build_and_duplicate_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();fixture=root/"fixture.json";build=root/"build.json"
            fixture.write_text("{}");build.write_text("{}")
            manifest=dict(_path=str(fixture))
            player=dict(baselineBuildId="M05-Baseline-test",runtimeAbiHash="a"*64,unityVersion="2022.3.62f2",buildGuid="1"*32,
                        typeProofPath=str(root/"proof.json"),typeProofSha256="b"*64,playerOutput=str(root/"Player.app"),variant="NativeOn")
            result={key:"" for key in v.RESULT_FIELDS.split()}
            result.update({key:[] for key in v.RESULT_ARRAYS.split()})
            result.update({key:player[key] for key in ("baselineBuildId","runtimeAbiHash","unityVersion","buildGuid","typeProofPath","typeProofSha256")})
            result.update(schemaVersion=1,processId=1,milestone="M05",mode="T05-01-P01",result="Passed",il2cpp=True,platform="OSXPlayer",
                          moduleMvidObservationPolicy=v.MVID_POLICY,playerDataPath=player["playerOutput"]+"/Contents",fixtureManifestPath=str(fixture),
                          fixtureManifestSha256=v.digest(fixture),playerBuildReceiptPath=str(build),playerBuildReceiptSha256=v.digest(build),ordinary=None,benchmark=None)
            path=root/("m05-"+result["mode"]+".json")
            path.write_text(json.dumps(result));v.verify_result_header(path,manifest,player,build)
            for mutate in (lambda r:r.update(processId=True),lambda r:r.update(schemaVersion=True),lambda r:r.update(processId=1<<31),
                           lambda r:r.update(buildGuid="2"*32),lambda r:r.update(playerDataPath="/outside"),lambda r:r.update(typeProofSha256="f"*64),
                           lambda r:r.pop("allocationException"),lambda r:r.update(fabricated=True),lambda r:r.update(typeObservations=None)):
                bad=copy.deepcopy(result);mutate(bad);path.write_text(json.dumps(bad))
                with self.assertRaises(VerificationError):v.verify_result_header(path,manifest,player,build)
            path.write_text(json.dumps(result)[:-1]+',"schemaVersion":1}')
            with self.assertRaises(VerificationError):v.verify_result_header(path,manifest,player,build)

    def test_inactive_benchmark_never_claims_work_or_identity(self):
        value=dict(enabled=False,finalSameType=False,warmupCount=0,lookupCount=0,elapsedTicks=0,stopwatchFrequency=0,checksum=0,requestedName="",finalTypeName="",finalAssemblyName="")
        v.inactive_benchmark(value,"empty")
        for update in (dict(finalSameType=True),dict(checksum=True),dict(lookupCount=100000),dict(finalTypeName="Example.Owner"),dict(unknown=0)):
            with self.assertRaises(VerificationError):v.inactive_benchmark(dict(value,**update),"bad inactive benchmark")


class ModeCoverageTests(unittest.TestCase):
    def test_every_closure_member_requires_four_real_member_kinds_and_type_witnesses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();identities={};inventories={};result={key:[] for key in v.RESULT_ARRAYS.split()}
            result["mode"]="T05-03-P03"
            for assembly in v.PROVIDER_ORDER:
                prefix=v.PAYLOAD_PREFIXES[assembly];namespace,leaf=prefix.rsplit(".",1);payload=prefix+"Payload"
                path=root/(assembly+".dll")
                path.write_bytes(make_type_pe([dict(name=leaf+"Payload",namespace=namespace,
                    fields=[dict(name="Field",signature=b"\x06\x12\x08")],
                    methods=[dict(name="Echo",signature=b"\x20\x01\x12\x08\x12\x08",body=b"\x03\x2a")],
                    properties=[dict(name="Property",signature=b"\x28\x00\x12\x08")],events=[dict(name="Changed",type=6)])],
                    name=assembly,extra_refs=[("Action`1","System")],type_specs=[b"\x15\x12\x11\x01\x12\x08"]))
                identity=read_identity(path);identities[assembly]=identity;inventories[assembly]=read_type_inventory(path)["types"]
                full=identity["fullName"]
                for operation,value in (("Assembly.Load",full),("ManifestModule",full),("Type/Module.GetType",v.prior.TYPE_NAMES[assembly]),("PatchType/Assembly",full),
                                        ("PatchType witness repeat",payload),("ManifestModule.Assembly",full)):
                    result["identityObservations"].append(dict(operation=operation,left=value,right=value,sameObject=True))
                result["typeResolutionObservations"].append(dict(operation="GetTypeResolutionInfo",requested=v.prior.TYPE_NAMES[assembly]))
                for kind,name in (("method","Echo"),("field","Field"),("property","Property"),("event","Changed")):
                    event="System.Action`1[["+payload+", "+full+"]]"
                    return_type=payload if kind in ("method","property") else ""
                    field_type=payload if kind=="field" else event if kind=="event" else ""
                    for operation,value in (("declaring",payload),("reflected",payload),("return" if return_type else "type",return_type or field_type)):
                        result["typeResolutionObservations"].append(dict(operation="member-"+kind+"-"+operation,requested=value))
                    if kind=="method":result["typeResolutionObservations"].append(dict(operation="member-method-parameter-0",requested=payload))
                    result["memberObservations"].append(dict(declaringType=payload,reflectedType=payload,memberName=name,memberKind=kind,
                        returnType=return_type,fieldType=field_type,parameterTypes=[payload] if kind=="method" else [],sameMember=True,activeOwner=True))
            fixture=dict(closureLoadOrder=list(v.PROVIDER_ORDER))
            check=lambda r:v.verify_mode_observations(r,{}, {},fixture,{},inventories,identities,[],"cache coverage")
            self.assertEqual(len(check(result)),30)
            for mutate in (lambda r:r["memberObservations"].pop(),lambda r:r["memberObservations"].reverse(),
                           lambda r:r["memberObservations"][0].update(parameterTypes=[]),lambda r:r["memberObservations"][3].update(fieldType="System.Action"),
                           lambda r:r["typeResolutionObservations"].pop(),lambda r:r["typeResolutionObservations"][2].update(requested="Baseline.Owner"),
                           lambda r:r["identityObservations"][0].update(sameObject=1)):
                bad=copy.deepcopy(result);mutate(bad)
                with self.assertRaises(VerificationError):check(bad)
            identities[v.INTERNAL]["sha256"]="0"*64
            with self.assertRaises(VerificationError):check(result)


if __name__ == "__main__":
    unittest.main()
