"""Independent CLI-byte shape inspection for H1 count fixtures (never loads DLLs)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from m04_metadata import read_identity_bytes
from m05_types import CliTables, Signature, reflection_escape
from shadow_tools import require


PRIMITIVES = {1: "System.Void", 2: "System.Boolean", 3: "System.Char",
              4: "System.SByte", 5: "System.Byte", 6: "System.Int16",
              7: "System.UInt16", 8: "System.Int32", 9: "System.UInt32",
              10: "System.Int64", 11: "System.UInt64", 12: "System.Single",
              13: "System.Double", 14: "System.String", 24: "System.IntPtr",
              25: "System.UIntPtr", 28: "System.Object"}
MAX_DLL_BYTES = 32 * 1024 * 1024


def signature_type(reader: Signature, *, allow_void=False, depth=0):
    require(depth < 16, "H1 fixture signature nesting exceeds audit contract")
    tag = reader.byte()
    if tag in PRIMITIVES:
        require(tag != 1 or allow_void, "Void parameter is invalid")
        return PRIMITIVES[tag]
    if tag == 16:
        nested = signature_type(reader, depth=depth + 1)
        require(not nested.endswith("&"), "ByRef-of-ByRef parameter type is invalid")
        return nested + "&"
    if tag == 29:
        nested = signature_type(reader, depth=depth + 1)
        require(not nested.endswith("&"), "Array-of-ByRef parameter type is invalid")
        return nested + "[]"
    raise ValueError("Unsupported H1 fixture signature element: " + hex(tag))


def decode_method_signature(blob: bytes):
    reader = Signature(blob, "H1 method signature")
    flags = reader.byte()
    require(flags & 0x0f == 0 and not flags & 0xd0,
            "H1 requires non-generic default method signatures without EXPLICITTHIS")
    count = reader.compressed()
    result = signature_type(reader, allow_void=True)
    parameters = [signature_type(reader) for _ in range(count)]
    require(reader.position == len(blob), "Trailing bytes after declared method parameters")
    return {"count": count, "instance": bool(flags & 32), "returnType": result,
            "parameterTypes": parameters,
            "parameterTypesSha256": hashlib.sha256("\n".join(parameters).encode()).hexdigest()}


def inspect_bytes(data: bytes, label="<H1 DLL>"):
    require(0 < len(data) <= MAX_DLL_BYTES, "H1 DLL outside 32 MiB limit")
    tables = CliTables(data, label)
    identity = read_identity_bytes(data, label)
    types = {rid: tables.row(2, rid) for rid in range(1, tables.counts[2] + 1)}
    require(tables.string(types[1][1]) == "<Module>", "First TypeDef must be the module")
    names = {}
    namespaces = {}
    for rid, row in types.items():
        name, namespace = tables.string(row[1]), tables.string(row[2])
        require(name and "\r" not in name and "\n" not in name,
                "Invalid TypeDef name")
        require("\r" not in namespace and "\n" not in namespace,
                "Invalid TypeDef namespace")
        names[rid], namespaces[rid] = name, namespace

    parents, groups, nested_rows = {}, {}, []
    previous_child = 0
    sorted_mask = tables.reader.number(16, 8)
    for rid in range(1, tables.counts[41] + 1):
        child, parent = tables.row(41, rid)
        require(child in types and parent in types and child != parent and child != 1 and parent != 1,
                "Invalid NestedClass row")
        require(child not in parents, "Duplicate nested child ownership")
        if sorted_mask & (1 << 41):
            require(child > previous_child, "NestedClass sort declaration disagrees with child RID order")
        previous_child = child
        require(types[child][0] & 7 in range(2, 8), "Nested child lacks nested visibility")
        parents[child] = parent
        groups.setdefault(parent, []).append(child)
        nested_rows.append([child, parent])

    for rid, row in types.items():
        require((rid in parents) == ((row[0] & 7) >= 2),
                "NestedClass visibility/ownership differs")

    def type_name(rid):
        chain, seen = [], set()
        while True:
            require(rid not in seen, "NestedClass cycle")
            seen.add(rid)
            chain.append(rid)
            if rid not in parents:
                chain.reverse()
                return "+".join((reflection_escape(namespaces[names_rid]) + "." if namespaces[names_rid] else "") +
                                 reflection_escape(names[names_rid]) for names_rid in chain)
            rid = parents[rid]

    type_identities = [{"rid": rid, "name": names[rid], "namespace": namespaces[rid],
                        "fullName": type_name(rid),
                        "parentRid": parents[rid] if rid in parents else None}
                       for rid in types]

    method_owners = {}
    method_rows = {}
    for owner, row in types.items():
        start = row[5]
        end = types[owner + 1][5] if owner < tables.counts[2] else tables.counts[6] + 1
        require(1 <= start <= end <= tables.counts[6] + 1, "Invalid TypeDef method extent")
        for rid in range(start, end):
            require(rid not in method_owners, "Duplicate MethodDef ownership")
            method_owners[rid], method_rows[rid] = owner, tables.row(6, rid)
    require(set(method_owners) == set(range(1, tables.counts[6] + 1)),
            "Method ownership is incomplete")

    methods = []
    param_owners = {}
    previous_first = 1
    for rid in range(1, tables.counts[6] + 1):
        owner, method = method_owners[rid], method_rows[rid]
        first = method[5]
        last = tables.row(6, rid + 1)[5] if rid < tables.counts[6] else tables.counts[8] + 1
        require(1 <= first <= last <= tables.counts[8] + 1, "Invalid MethodDef Param extent")
        require(first >= previous_first, "MethodDef Param lists are out of order")
        previous_first = first
        sig = decode_method_signature(tables.blob(method[4]))
        require(sig["instance"] == (not bool(method[2] & 16)), "Method static flag disagrees with signature")
        metadata, seen_sequences = [], set()
        for param_rid in range(first, last):
            require(param_rid not in param_owners, "Duplicate Param ownership")
            param_owners[param_rid] = rid
            flags, sequence, name = tables.row(8, param_rid)
            require(sequence <= sig["count"] and sequence not in seen_sequences,
                    "Invalid or duplicate Param sequence")
            seen_sequences.add(sequence)
            metadata.append({"rid": param_rid, "flags": flags, "sequence": sequence,
                             "name": tables.string(name)})
        methods.append({"rid": rid, "declaringType": type_name(owner),
                        "name": tables.string(method[3]), "signature": sig,
                        "paramListStart": first, "paramListEnd": last,
                        "paramRows": metadata, "rva": method[0]})
    require(set(param_owners) == set(range(1, tables.counts[8] + 1)),
            "Param ownership is incomplete")
    nesting = [{"declaringType": type_name(parent), "parentRid": parent,
                "count": len(children), "first": type_name(children[0]),
                "last": type_name(children[-1]),
                "childrenSha256": hashlib.sha256("\n".join(type_name(c) for c in children).encode()).hexdigest()}
               for parent, children in groups.items()]
    return {"kind": "H1CountDllByteShape", "identity": identity,
            "sizeBytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "typeDefCount": tables.counts[2], "methodDefCount": tables.counts[6],
            "paramTableCount": tables.counts[8], "nestedClassTableCount": tables.counts[41],
            "nestedClassSortedDeclared": bool(sorted_mask & (1 << 41)),
            "nestedRowsSha256": hashlib.sha256(str(nested_rows).encode()).hexdigest(),
            "types": type_identities, "methods": methods, "nestedGroups": nesting}


def inspect_file(path: Path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "H1 audit input must be a regular DLL")
    size = path.stat().st_size
    require(0 < size <= MAX_DLL_BYTES, "H1 DLL outside 32 MiB limit")
    with path.open("rb") as stream:
        data = stream.read(MAX_DLL_BYTES + 1)
    require(len(data) == size, "H1 DLL changed while being read")
    return inspect_bytes(data, str(path))
