#!/usr/bin/env python3
"""Independent Portable-PDB local-constant byte/scope audit; no assembly execution.

The comparison is intentionally strict: metadata-token/signature differences
must be reviewed rather than interpreted as harmless symbol loss.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct


class PdbAuditError(ValueError):
    pass


def need(value, message):
    if not value:
        raise PdbAuditError(message)


def uint(data: bytes, position: int, size: int) -> int:
    need(0 <= position <= len(data) - size, "Truncated metadata field")
    return int.from_bytes(data[position:position + size], "little")


def compressed(data: bytes, position: int) -> tuple[int, int]:
    first = uint(data, position, 1)
    if first < 0x80:
        return first, position + 1
    if first < 0xC0:
        need(position + 2 <= len(data), "Truncated two-byte compressed integer")
        return ((first & 0x3F) << 8) | data[position + 1], position + 2
    need(first < 0xE0 and position + 4 <= len(data), "Invalid/truncated compressed integer")
    return ((first & 0x1F) << 24) | int.from_bytes(data[position + 1:position + 4], "big"), position + 4


def streams(data: bytes) -> dict[str, bytes]:
    need(data[:4] == b"BSJB", "Expected an uncompressed standalone Portable PDB (BSJB)")
    version_length = uint(data, 12, 4)
    position = (16 + version_length + 3) & ~3
    count = uint(data, position + 2, 2)
    need(0 < count <= 64, "Invalid metadata stream count")
    position += 4
    entries = []
    for _ in range(count):
        offset, size = uint(data, position, 4), uint(data, position + 4, 4)
        position += 8
        end = data.find(b"\0", position, min(position + 32, len(data)))
        need(end >= position, "Unterminated metadata stream name")
        try:
            name = data[position:end].decode("ascii")
        except UnicodeDecodeError as error:
            raise PdbAuditError("Non-ASCII metadata stream name") from error
        need(name and name not in {row[0] for row in entries}, "Duplicate/empty metadata stream")
        position = (end + 1 + 3) & ~3
        need(offset <= len(data) and size <= len(data) - offset, "Metadata stream outside file")
        entries.append((name, offset, size))
    ranges = sorted((offset, offset + size) for _, offset, size in entries if size)
    need(all(start >= position for start, _ in ranges), "Metadata stream overlaps header")
    need(all(left[1] <= right[0] for left, right in zip(ranges, ranges[1:])), "Overlapping metadata streams")
    return {name: data[offset:offset + size] for name, offset, size in entries}


def parse(data: bytes) -> dict:
    parts = streams(data)
    need(all(name in parts for name in ("#Pdb", "#~", "#Strings", "#Blob")), "Missing Portable PDB streams")
    pdb = parts["#Pdb"]
    mask = uint(pdb, 24, 8)
    external = {}
    position = 32
    for table in range(64):
        if mask & (1 << table):
            external[table] = uint(pdb, position, 4)
            position += 4
    need(position == len(pdb), "Invalid #Pdb external-row inventory")
    table_data = parts["#~"]
    heap_flags = uint(table_data, 6, 1)
    valid = uint(table_data, 8, 8)
    need(valid & ~sum(1 << table for table in range(48, 56)) == 0,
         "Unexpected type-system tables in standalone Portable PDB")
    counts = {}
    position = 24
    for table in range(64):
        if valid & (1 << table):
            counts[table] = uint(table_data, position, 4)
            position += 4
    rows = dict(external)
    rows.update(counts)
    index = lambda table: 4 if rows.get(table, 0) >= 65536 else 2
    string_size = 4 if heap_flags & 1 else 2
    guid_size = 4 if heap_flags & 2 else 2
    blob_size = 4 if heap_flags & 4 else 2
    custom_parents = (6, 4, 1, 2, 8, 9, 10, 0, 14, 23, 20, 17, 26, 27, 32, 35, 38, 39, 40, 42, 44, 43, 48, 50, 51, 52, 53)
    custom_size = 4 if max((rows.get(table, 0) for table in custom_parents), default=0) >= 2048 else 2
    layouts = {
        48: (blob_size, guid_size, blob_size, guid_size),
        49: (index(48), blob_size),
        50: (index(6), index(53), index(51), index(52), 4, 4),
        51: (2, 2, string_size),
        52: (string_size, blob_size),
        53: (index(53), blob_size),
        54: (index(6), index(6)),
        55: (custom_size, guid_size, blob_size),
    }
    parsed = {}
    for table in sorted(counts):
        layout = layouts[table]
        size = sum(layout)
        need(counts[table] <= (len(table_data) - position) // size, "Truncated Portable PDB table rows")
        values = []
        for _ in range(counts[table]):
            row = []
            for width in layout:
                row.append(uint(table_data, position, width))
                position += width
            values.append(row)
        parsed[table] = values
    need(all(byte == 0 for byte in table_data[position:]), "Unexpected trailing table bytes")

    def name_at(offset):
        heap = parts["#Strings"]
        need(0 <= offset < len(heap), "Constant name outside string heap")
        end = heap.find(b"\0", offset)
        need(end >= offset, "Unterminated constant name")
        try:
            return heap[offset:end].decode("utf-8")
        except UnicodeDecodeError as error:
            raise PdbAuditError("Invalid constant-name UTF-8") from error

    def signature_at(offset):
        heap = parts["#Blob"]
        need(offset > 0, "Empty local-constant signature")
        size, start = compressed(heap, offset)
        need(size > 0 and start + size <= len(heap), "Local-constant signature outside blob heap")
        return heap[start:start + size].hex()

    constants = [(name_at(name), signature_at(signature)) for name, signature in parsed.get(52, [])]
    scopes = parsed.get(50, [])
    records = []
    used = []
    for number, row in enumerate(scopes):
        method, _, _, first, start, length = row
        last = scopes[number + 1][3] if number + 1 < len(scopes) else len(constants) + 1
        need(0 < method <= external.get(6, 0), "Local scope references an invalid method")
        need(1 <= first <= last <= len(constants) + 1, "Invalid local-constant list range")
        for rid in range(first, last):
            name, signature = constants[rid - 1]
            records.append({"methodRid": method, "startOffset": start, "length": length,
                            "name": name, "signatureHex": signature})
            used.append(rid)
    need(used == list(range(1, len(constants) + 1)), "Unscoped or multiply-owned constants")
    return {"schemaVersion": 1, "kind": "H1PortablePdbConstantInventory",
            "sha256": hashlib.sha256(data).hexdigest(), "constantCount": len(constants),
            "scopeCount": len(scopes), "constants": records,
            "runtimeAcceptance": False, "humanGatePassed": False, "mayEnterR02": False}


def compare(before: dict, after: dict) -> bool:
    key = lambda row: (row["methodRid"], row["startOffset"], row["length"], row["name"], row["signatureHex"])
    return Counter(map(key, before["constants"])) == Counter(map(key, after["constants"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--emitted", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    before = parse(args.input.read_bytes())
    report = {"kind": "H1PortablePdbConstantAudit", "input": before,
              "status": "Parsed", "humanGatePassed": False, "mayEnterR02": False}
    if args.emitted:
        after = parse(args.emitted.read_bytes())
        equal = compare(before, after)
        report.update(emitted=after, status="ExactConstantScopeBytesEqual" if equal else "Mismatch")
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "output": str(args.output)}))
    return 1 if report["status"] == "Mismatch" else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print("Failed: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(1)
