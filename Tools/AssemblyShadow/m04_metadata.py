"""Bounded, dependency-free ECMA-335 Assembly/AssemblyRef identity reader.

This is intentionally not an IL verifier or a replacement for the Editor's
semantic/Unity ABI proof. It independently binds identity claims to PE bytes.
Only ordinary CLI metadata tables (0..44) are accepted; no execution occurs.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import uuid

from shadow_tools import VerificationError, require


# ECMA-335 II.22. Heap: s/string, b/blob, g/guid; integer: u2/u4;
# integer table indices and named coded indices are sized from row counts.
CODED = {
    "TypeDefOrRef": (2, (2, 1, 27)), "HasConstant": (2, (4, 8, 23)),
    "HasCustomAttribute": (5, (6, 4, 1, 2, 8, 9, 10, 0, 14, 23, 20, 17, 26, 27, 32, 35, 38, 39, 40, 42, 44, 43)),
    "HasFieldMarshal": (1, (4, 8)), "HasDeclSecurity": (2, (2, 6, 32)),
    "MemberRefParent": (3, (2, 1, 26, 6, 27)), "HasSemantics": (1, (20, 23)),
    "MethodDefOrRef": (1, (6, 10)), "MemberForwarded": (1, (4, 6)),
    "Implementation": (2, (38, 35, 39)), "CustomAttributeType": (3, (6, 10)),
    "ResolutionScope": (2, (0, 26, 35, 1)), "TypeOrMethodDef": (1, (2, 6)),
}
TABLES = (
    ("u2", "s", "g", "g", "g"), ("ResolutionScope", "s", "s"),
    ("u4", "s", "s", "TypeDefOrRef", 4, 6), (4,), ("u2", "s", "b"), (6,),
    ("u4", "u2", "u2", "s", "b", 8), (8,), ("u2", "u2", "s"),
    (2, "TypeDefOrRef"), ("MemberRefParent", "s", "b"),
    ("u2", "HasConstant", "b"), ("HasCustomAttribute", "CustomAttributeType", "b"),
    ("HasFieldMarshal", "b"), ("u2", "HasDeclSecurity", "b"),
    ("u2", "u4", 2), ("u4", 4), ("b",), (2, 20), (20,),
    ("u2", "s", "TypeDefOrRef"), (2, 23), (23,), ("u2", "s", "b"),
    ("u2", 6, "HasSemantics"), (2, "MethodDefOrRef", "MethodDefOrRef"),
    ("s",), ("b",), ("u2", "MemberForwarded", "s", 26), ("u4", 4),
    ("u4", "u4"), ("u4",),
    ("u4", "u2", "u2", "u2", "u2", "u4", "b", "s", "s"),
    ("u4",), ("u4", "u4", "u4"),
    ("u2", "u2", "u2", "u2", "u4", "b", "s", "s", "b"),
    ("u4", 35), ("u4", "u4", "u4", 35), ("u4", "s", "b"),
    ("u4", "u4", "s", "s", "Implementation"),
    ("u4", "u4", "s", "Implementation"), (2, 2),
    ("u2", "u2", "TypeOrMethodDef", "s"), ("MethodDefOrRef", "b"),
    (42, "TypeDefOrRef"),
)


class Reader:
    def __init__(self, data, label):
        self.data, self.label = data, str(label)

    def fail(self, message):
        raise VerificationError(f"{self.label}: PE/CLI metadata: {message}")

    def block(self, offset, count):
        if offset < 0 or count < 0 or offset + count > len(self.data):
            self.fail("truncated/out-of-bounds data")
        return self.data[offset:offset + count]

    def number(self, offset, width):
        return int.from_bytes(self.block(offset, width), "little")


def _metadata(data, label):
    r = Reader(data, label)
    require(len(data) <= 512 * 1024 * 1024, f"{label}: oversized PE file")
    if r.block(0, 2) != b"MZ": r.fail("missing DOS header")
    pe = r.number(0x3c, 4)
    if r.block(pe, 4) != b"PE\0\0": r.fail("missing PE signature")
    sections, opt_size = r.number(pe + 6, 2), r.number(pe + 20, 2)
    if not 0 < sections <= 96: r.fail("invalid section count")
    opt, magic = pe + 24, r.number(pe + 24, 2)
    if magic not in (0x10b, 0x20b): r.fail("unsupported optional header")
    directory, numoff = (96, 92) if magic == 0x10b else (112, 108)
    if opt_size < directory + 15 * 8 or r.number(opt + numoff, 4) < 15:
        r.fail("missing CLI data directory")
    headers = r.number(opt + 60, 4)
    section_data = []
    for i in range(sections):
        p = opt + opt_size + i * 40
        r.block(p, 40)
        section_data.append((r.number(p + 12, 4), r.number(p + 16, 4), r.number(p + 20, 4)))

    def rva(value, size):
        matches = [ptr + value - start for start, count, ptr in section_data
                   if start <= value and value + size <= start + count]
        if value + size <= headers: matches.append(value)
        if len(matches) != 1: r.fail("unmapped or ambiguous RVA")
        r.block(matches[0], size)
        return matches[0]

    cli_rva, cli_size = r.number(opt + directory + 14 * 8, 4), r.number(opt + directory + 14 * 8 + 4, 4)
    if cli_size < 72: r.fail("short CLI header")
    cli = rva(cli_rva, 72)
    if r.number(cli, 4) < 72: r.fail("invalid CLI header size")
    md_size = r.number(cli + 12, 4)
    md = rva(r.number(cli + 8, 4), md_size)
    m = Reader(r.block(md, md_size), label)
    if m.block(0, 4) != b"BSJB": m.fail("invalid metadata root")
    version_size = m.number(12, 4)
    if version_size > 1024: m.fail("oversized metadata version")
    m.block(16, version_size)
    cursor = (16 + version_size + 3) & ~3
    stream_count = m.number(cursor + 2, 2)
    if not 1 <= stream_count <= 16: m.fail("invalid metadata stream count")
    cursor += 4
    streams, spans = {}, []
    for _ in range(stream_count):
        offset, size = m.number(cursor, 4), m.number(cursor + 4, 4)
        end = cursor + 8
        while m.number(end, 1) and end < cursor + 40: end += 1
        if end == cursor + 40: m.fail("unterminated stream name")
        try: name = m.block(cursor + 8, end - cursor - 8).decode("ascii")
        except UnicodeDecodeError: m.fail("non-ASCII stream name")
        if name in streams: m.fail("duplicate metadata stream")
        streams[name] = m.block(offset, size)
        spans.append((offset, offset + size))
        cursor = (end + 4) & ~3
    previous = cursor
    for start, end in sorted(spans):
        if start < previous: m.fail("overlapping metadata streams/headers")
        previous = end
    if ("#~" in streams) == ("#-" in streams): m.fail("ambiguous/missing table stream")
    if not all(name in streams for name in ("#Strings", "#GUID", "#Blob")):
        m.fail("missing identity heap")
    return streams


def read_identity_bytes(data: bytes, label="<bytes>") -> dict:
    streams = _metadata(data, label)
    t = Reader(streams.get("#~", streams.get("#-")), label)
    heap_sizes = t.number(6, 1)
    valid = t.number(8, 8)
    if valid >> len(TABLES): t.fail("unsupported metadata tables")
    rows, cursor = [0] * 45, 24
    for table in range(45):
        if valid & (1 << table):
            rows[table] = t.number(cursor, 4)
            cursor += 4
            if rows[table] > 10_000_000: t.fail("unreasonable metadata row count")
    if rows[0] != 1 or rows[32] != 1: t.fail("requires exactly one Module and Assembly row")

    def width(column):
        if isinstance(column, int): return 4 if rows[column] >= 65536 else 2
        if column in ("u2", "u4"): return int(column[1:])
        if column in "sbg": return 4 if heap_sizes & {"s": 1, "g": 2, "b": 4}[column] else 2
        bits, targets = CODED[column]
        return 4 if max(rows[target] for target in targets) >= 1 << (16 - bits) else 2

    offsets, widths = {}, {}
    for table, schema in enumerate(TABLES):
        offsets[table], widths[table] = cursor, [width(c) for c in schema]
        size = rows[table] * sum(widths[table])
        t.block(cursor, size)
        cursor += size

    def row(table, index=0):
        p = offsets[table] + index * sum(widths[table])
        values = []
        for n in widths[table]:
            values.append(t.number(p, n)); p += n
        return values

    def string(index):
        heap = streams["#Strings"]
        if index >= len(heap): t.fail("string heap index out of bounds")
        end = heap.find(b"\0", index)
        if end < 0: t.fail("unterminated string heap entry")
        try: return heap[index:end].decode("utf-8", errors="strict")
        except UnicodeDecodeError: t.fail("invalid UTF-8 identity")

    def blob(index):
        h = Reader(streams["#Blob"], label)
        first = h.number(index, 1)
        if first < 0x80: size, header = first, 1
        elif first < 0xc0:
            size, header = ((first & 0x3f) << 8) | h.number(index + 1, 1), 2
            if size < 0x80: t.fail("noncanonical blob length")
        elif first < 0xe0:
            size, header = ((first & 0x1f) << 24) | int.from_bytes(h.block(index + 1, 3), "big"), 4
            if size < 0x4000: t.fail("noncanonical blob length")
        else: t.fail("invalid blob length")
        return h.block(index + header, size)

    def identity(version, flags, key_index, name_index, culture_index):
        name, culture = string(name_index), string(culture_index)
        if not name or any(c in name for c in ',=\\/\r\n\0'): t.fail("unsupported assembly simple name")
        if any(c in culture for c in ',=\r\n\0'): t.fail("invalid assembly culture")
        key = blob(key_index)
        if flags & 1:
            token = hashlib.sha1(key).digest()[-8:][::-1].hex() if key else ""
        else:
            if len(key) not in (0, 8): t.fail("public key token must be absent or eight bytes")
            token = key.hex()
        version = ".".join(str(n) for n in version)
        full = f"{name}, Version={version}, Culture={culture or 'neutral'}, PublicKeyToken={token or 'null'}"
        if flags & 0x100: full += ", Retargetable=Yes"
        if flags & 0x200: full += ", ContentType=WindowsRuntime"
        return dict(name=name, fullName=full, version=version, culture=culture, publicKeyToken=token)

    assembly = row(32)
    result = identity(assembly[1:5], assembly[5], *assembly[6:9])
    guid_index = row(0)[2]
    if not guid_index: t.fail("missing Module MVID")
    result["mvid"] = str(uuid.UUID(bytes_le=Reader(streams["#GUID"], label).block((guid_index - 1) * 16, 16)))
    if result["mvid"] == str(uuid.UUID(int=0)): t.fail("empty Module MVID")
    result["referenceIdentities"] = []
    for index in range(rows[35]):
        ref = row(35, index)
        result["referenceIdentities"].append(dict(referenceIndex=index, **identity(ref[:4], ref[4], *ref[5:8])))
    return result


def read_identity(path: Path) -> dict:
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), f"{path}: missing or symlinked DLL")
    for parent in path.parents:
        require(not parent.is_symlink(), f"{path}: symlinked DLL parent")
    require(path.stat().st_size <= 512 * 1024 * 1024, f"{path}: oversized DLL")
    data = path.read_bytes()
    return dict(read_identity_bytes(data, path), path=str(path.absolute()), sha256=hashlib.sha256(data).hexdigest())
