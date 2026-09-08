#!/usr/bin/env python3
"""Create and verify the bounded Q04 invalid-method-signature fixture.

This helper consumes the verified P03 Contracts DLL from m07-fixtures.json. It
changes exactly one byte in a zero-parameter void MethodDef signature blob:
ELEMENT_TYPE_VOID (0x01) -> invalid element type (0xff). The blob length,
PE layout, Assembly/Module identity, MVID, and AssemblyRef rows remain intact.
It deliberately writes a negative-input sidecar instead of any production
patch or fixture manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from m04_metadata import CODED, TABLES, _metadata, read_identity_bytes  # noqa: E402
from shadow_tools import VerificationError, require  # noqa: E402

TARGET_ASSEMBLY = "AssemblyA.Contracts"
TRANSFORM_ID = "Q04-MethodDefVoidReturn-0x01-to-0xff-v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(data: bytes, offset: int) -> int:
    require(0 <= offset <= len(data) - 2, "truncated uint16")
    return int.from_bytes(data[offset:offset + 2], "little")


def u32(data: bytes, offset: int) -> int:
    require(0 <= offset <= len(data) - 4, "truncated uint32")
    return int.from_bytes(data[offset:offset + 4], "little")


def rva_offset(data: bytes, rva: int, size: int = 1) -> int:
    pe = u32(data, 0x3c)
    require(data[pe:pe + 4] == b"PE\0\0", "missing PE signature")
    section_count = u16(data, pe + 6)
    optional_size = u16(data, pe + 20)
    optional = pe + 24
    section_start = optional + optional_size
    candidates = []
    for index in range(section_count):
        section = section_start + index * 40
        virtual_size = u32(data, section + 8)
        virtual_address = u32(data, section + 12)
        raw_size = u32(data, section + 16)
        raw_pointer = u32(data, section + 20)
        span = max(virtual_size, raw_size)
        if virtual_address <= rva and rva + size <= virtual_address + span:
            offset = raw_pointer + (rva - virtual_address)
            require(offset + size <= len(data), "RVA maps outside file")
            candidates.append(offset)
    require(len(candidates) == 1, "RVA has no unique section mapping")
    return candidates[0]


def metadata_file_offset(data: bytes) -> int:
    pe = u32(data, 0x3c)
    optional = pe + 24
    magic = u16(data, optional)
    directory_offset = 96 if magic == 0x10b else 112 if magic == 0x20b else -1
    require(directory_offset >= 0, "unsupported PE optional header")
    cli_rva = u32(data, optional + directory_offset + 14 * 8)
    cli = rva_offset(data, cli_rva, 72)
    return rva_offset(data, u32(data, cli + 8), u32(data, cli + 12))


def stream_file_offsets(data: bytes) -> dict[str, tuple[int, int]]:
    root = metadata_file_offset(data)
    require(data[root:root + 4] == b"BSJB", "invalid metadata root")
    version_size = u32(data, root + 12)
    cursor = (root + 16 + version_size + 3) & ~3
    stream_count = u16(data, cursor + 2)
    cursor += 4
    result = {}
    for _ in range(stream_count):
        relative, size = u32(data, cursor), u32(data, cursor + 4)
        end = cursor + 8
        while end < cursor + 40 and data[end] != 0:
            end += 1
        require(end < cursor + 40, "unterminated metadata stream name")
        name = data[cursor + 8:end].decode("ascii")
        require(name not in result, "duplicate metadata stream")
        result[name] = (root + relative, size)
        cursor = (end + 4) & ~3
    return result


def index_width(rows: list[int], table: int) -> int:
    return 2 if rows[table] < 65536 else 4


def coded_width(rows: list[int], name: str) -> int:
    bits, targets = CODED[name]
    return 2 if max(rows[target] for target in targets) < (1 << (16 - bits)) else 4


def column_width(rows: list[int], heap_sizes: int, column) -> int:
    if isinstance(column, int):
        return index_width(rows, column)
    if column in ("u2", "u4"):
        return int(column[1:])
    if column in "sbg":
        bit = {"s": 1, "g": 2, "b": 4}[column]
        return 4 if heap_sizes & bit else 2
    return coded_width(rows, column)


def tables_view(data: bytes, label: str) -> tuple[bytes, dict[str, tuple[int, int]], list[int], dict[int, int], dict[int, list[int]]]:
    streams = _metadata(data, label)
    table_stream = streams.get("#~", streams.get("#-"))
    require(table_stream is not None, "missing metadata table stream")
    table_bytes = table_stream
    heap_sizes = table_bytes[6]
    valid = int.from_bytes(table_bytes[8:16], "little")
    rows = [0] * len(TABLES)
    cursor = 24
    for table in range(len(TABLES)):
        if valid & (1 << table):
            rows[table] = int.from_bytes(table_bytes[cursor:cursor + 4], "little")
            cursor += 4
    offsets, widths, schemas = {}, {}, {}
    for table, schema in enumerate(TABLES):
        widths[table] = [column_width(rows, heap_sizes, column) for column in schema]
        offsets[table] = cursor
        cursor += rows[table] * sum(widths[table])
        require(cursor <= len(table_bytes), f"{label}: metadata table stream truncated")
        schemas[table] = list(schema)
    return table_bytes, streams, rows, offsets, schemas


def table_row(table_bytes: bytes, rows: list[int], offsets: dict[int, int], schemas: dict[int, list], table: int, rid: int) -> list[int]:
    require(1 <= rid <= rows[table], f"MethodDef RID out of range: {rid}")
    schema = schemas[table]
    widths = [column_width(rows, table_bytes[6], column) for column in schema]
    row_size = sum(widths)
    cursor = offsets[table] + (rid - 1) * row_size
    result = []
    for width in widths:
        result.append(int.from_bytes(table_bytes[cursor:cursor + width], "little"))
        cursor += width
    return result


def compressed_uint(blob: bytes, offset: int) -> tuple[int, int]:
    require(offset < len(blob), "signature ended before compressed integer")
    first = blob[offset]
    if first < 0x80:
        return first, 1
    if first < 0xc0:
        require(offset + 2 <= len(blob), "truncated two-byte compressed integer")
        return ((first & 0x3f) << 8) | blob[offset + 1], 2
    if first < 0xe0:
        require(offset + 4 <= len(blob), "truncated four-byte compressed integer")
        return ((first & 0x1f) << 24) | (blob[offset + 1] << 16) | (blob[offset + 2] << 8) | blob[offset + 3], 4
    raise VerificationError("invalid compressed integer in method signature")


def blob_entry(blob_heap: bytes, index: int) -> tuple[int, bytes]:
    require(index > 0 and index < len(blob_heap), "invalid MethodDef blob index")
    length, prefix = compressed_uint(blob_heap, index)
    start = index + prefix
    require(start + length <= len(blob_heap), "MethodDef blob exceeds #Blob heap")
    return prefix, blob_heap[start:start + length]


def find_mutation(data: bytes, label: str) -> dict:
    table_bytes, streams, rows, offsets, schemas = tables_view(data, label)
    require(rows[6] > 0, f"{label}: MethodDef table is empty")
    blob_heap = streams["#Blob"]
    candidates = []
    for rid in range(1, rows[6] + 1):
        method = table_row(table_bytes, rows, offsets, schemas, 6, rid)
        blob_index = method[4]
        _, signature = blob_entry(blob_heap, blob_index)
        if not signature:
            continue
        callconv, callconv_size = signature[0], 1
        if callconv & 0x10:
            _, generic_size = compressed_uint(signature, callconv_size)
            callconv_size += generic_size
        param_count, param_size = compressed_uint(signature, callconv_size)
        return_offset = callconv_size + param_size
        if param_count == 0 and return_offset + 1 == len(signature) and signature[return_offset] == 0x01:
            candidates.append((rid, blob_index, signature, return_offset))
    require(candidates, f"{label}: no deterministic zero-parameter void MethodDef signature found")
    rid, blob_index, signature, return_offset = candidates[0]
    token = 0x06000000 | rid
    all_rows = []
    for method_rid in range(1, rows[6] + 1):
        method = table_row(table_bytes, rows, offsets, schemas, 6, method_rid)
        if method[4] == blob_index:
            all_rows.append(0x06000000 | method_rid)
    blob_start_rel = blob_index + compressed_uint(blob_heap, blob_index)[1]
    streams_on_disk = stream_file_offsets(data)
    blob_file_start, _ = streams_on_disk["#Blob"]
    changed_offset = blob_file_start + blob_start_rel + return_offset
    require(data[changed_offset] == 0x01, "computed mutation byte is not ELEMENT_TYPE_VOID")
    return dict(methodDefRid=rid, methodDefToken=f"0x{token:08x}", affectedMethodDefTokens=[f"0x{x:08x}" for x in all_rows],
                blobHeapIndex=blob_index, signatureBlobOffsetInHeap=blob_start_rel,
                changedByteOffset=changed_offset, signatureOriginal=signature.hex(), signatureOffset=return_offset,
                blobFileOffset=blob_file_start + blob_start_rel, signatureLength=len(signature))


def identity_projection(identity: dict) -> dict:
    return {key: identity[key] for key in ("name", "fullName", "version", "culture", "publicKeyToken", "mvid", "referenceIdentities")}


def transform(source: Path, output: Path, receipt: Path, provenance: dict | None = None) -> dict:
    original = source.read_bytes()
    before = identity_projection(read_identity_bytes(original, source))
    mutation = find_mutation(original, str(source))
    mutated = bytearray(original)
    changed = mutation["changedByteOffset"]
    mutated[changed] = 0xFF
    require(len(mutated) == len(original), "mutation changed file length")
    require(sum(a != b for a, b in zip(original, mutated)) == 1, "mutation changed more than one byte")
    after = identity_projection(read_identity_bytes(bytes(mutated), output))
    require(before == after, "Assembly/Module identity or AssemblyRef rows changed")
    if provenance:
        row = provenance["patchClosureRow"]
        require(row.get("name") == before["name"], "P03 patch row identity name differs")
        require(row.get("sha256") == sha256(original), "P03 patch row does not bind source bytes")
        require(row.get("dllSize") == len(original), "P03 patch row length differs from source bytes")
        require(row.get("mvid") == before["mvid"], "P03 patch row does not bind source MVID")
        require(row.get("references", []) == [item["name"] for item in before["referenceIdentities"]],
                "P03 patch row AssemblyRefs differ from parsed source bytes")
    result = {
        "schemaVersion": 1,
        "kind": "Q04-NegativeMetadataTransform",
        "transformId": TRANSFORM_ID,
        "sourceFixture": "P03",
        "sourceAssembly": TARGET_ASSEMBLY,
        "sourceProvenance": provenance or {},
        "sourcePath": str(source.absolute()),
        "outputPath": str(output.absolute()),
        "sourceSha256": sha256(original),
        "outputSha256": sha256(mutated),
        "sourceLength": len(original),
        "outputLength": len(mutated),
        "lengthPreserved": len(original) == len(mutated),
        "changedByteCount": 1,
        "identityUnchanged": before == after,
        "sourcePatchRowMatches": provenance is not None,
        "sourceIdentity": before,
        "outputIdentity": after,
        "mutation": mutation,
        "mutatedByte": "ff",
        "originalByte": "01",
        "assemblyReferencesUnchanged": before["referenceIdentities"] == after["referenceIdentities"],
    }
    require(not output.exists() and not output.is_symlink() and not receipt.exists() and not receipt.is_symlink(),
            "negative input outputs must be new immutable files")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(mutated)
    with receipt.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def provenance_for(fixtures: Path) -> dict:
    document = json.loads(fixtures.read_text())
    for fixture in document.get("fixtures", []):
        if fixture.get("patchId") != "P03":
            continue
        patch_path = Path(fixture["patchManifest"])
        require(patch_path.is_file(), f"P03 patch manifest is missing: {patch_path}")
        patch_bytes = patch_path.read_bytes()
        declared_patch_hash = fixture.get("patchManifestSha256", "")
        if declared_patch_hash:
            require(sha256(patch_bytes) == declared_patch_hash, "P03 patch manifest hash mismatch")
        patch = json.loads(patch_bytes.decode("utf-8"))
        row = next((item for item in patch.get("closure", []) if item.get("name") == TARGET_ASSEMBLY), None)
        require(row is not None, "P03 patch manifest has no Contracts closure row")
        return {
            "fixtureManifestPath": str(fixtures.absolute()),
            "fixtureManifestSha256": sha256(fixtures.read_bytes()),
            "patchManifestPath": str(patch_path.absolute()),
            "patchManifestSha256": sha256(patch_bytes),
            "patchId": patch.get("patchId"),
            "patchClosureRow": row,
        }
    raise VerificationError("m07-fixtures.json has no P03 fixture")


def fixture_path(fixtures: Path) -> Path:
    document = json.loads(fixtures.read_text())
    for fixture in document.get("fixtures", []):
        if fixture.get("patchId") == "P03":
            for identity in fixture.get("assemblyIdentities", []):
                if identity.get("name") == TARGET_ASSEMBLY:
                    candidate = Path(identity["path"])
                    require(candidate.is_file(), f"P03 source DLL is missing: {candidate}")
                    return candidate
    raise VerificationError("m07-fixtures.json has no P03 Contracts identity")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = fixture_path(args.fixtures)
    output = args.output_dir / (source.stem + ".Q04MetadataInvalid.dll")
    receipt = args.output_dir / "q04-metadata-transform.json"
    result = transform(source, output, receipt, provenance_for(args.fixtures))
    print(json.dumps({key: result[key] for key in ("outputPath", "outputSha256", "outputLength", "identityUnchanged", "changedByteCount", "mutation")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, ValueError) as error:
        print(f"Q04 transform failed: {error}", file=sys.stderr)
        raise SystemExit(1)
