#!/usr/bin/env python3
"""Generate the bounded H1R/M02 parameter and nested fixture families.

The Cecil writer receives an ordinary and a Shadow assembly name for every
case. The launcher records the bytes and identities it actually produced;
shape proof is deliberately left to the independent auditor.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "h1-count-fixture-writer.cs"
LAUNCHER = Path(__file__).resolve()
IDENTITY_READER = HERE / "m04_metadata.py"
MONO_ROOT = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge")
MONO = MONO_ROOT / "bin/mono"
MCS = MONO_ROOT / "bin/mcs"
CECIL = MONO_ROOT / "lib/mono/net_4_x-macos/Mono.Cecil.dll"
TARGET_TYPE = "AssemblyShadow.H1Count.Target"
TARGET_METHOD = "Probe"
NESTED_TARGET_TYPE = "AssemblyShadow.H1Nested.Target"
MAX_DLL_BYTES = 32 * 1024 * 1024


def _case(case_id: str, count: int, variant: str, expected: str) -> dict[str, object]:
    return {"caseId": case_id, "family": "parameters", "count": count,
            "variant": variant, "expected": expected}


CASE_SPECS = (
    _case("H1R-P01-a", 0, "base-0", "Accepted"),
    _case("H1R-P01-b", 1, "base-1", "Accepted"),
    _case("H1R-P01-c", 254, "base-254", "Accepted"),
    _case("H1R-P01-d", 255, "base-255", "Accepted"),
    _case("H1R-P02-a", 256, "base-256", "ControlledRejected"),
    _case("H1R-P02-b", 65535, "base-65535", "ControlledRejected"),
    _case("H1R-P03-a", 65536, "base-65536", "ControlledRejected"),
    _case("H1R-P03-b", 65537, "base-65537", "ControlledRejected"),
    _case("H1R-P04-return255", 255, "return255", "Accepted"),
    _case("H1R-P04-partial-names", 255, "partial-names", "Accepted"),
    _case("H1R-P04-instance", 255, "instance", "Accepted"),
    _case("H1R-P04-mixed-kinds", 255, "mixed-kinds", "Accepted"),
)


def _nested_case(case_id: str, variant: str, group_counts: tuple[int, ...],
                 expected: str, *, interleaved: bool = False) -> dict[str, object]:
    if not group_counts or any(count < 0 or count > 65537 for count in group_counts):
        raise ValueError("nested group counts must be in 0..65537")
    return {
        "caseId": case_id,
        "family": "nested",
        "count": sum(group_counts),
        "variant": variant,
        "expected": expected,
        "groupCounts": list(group_counts),
        "declaringTypes": ["Target", "SiblingB"][:len(group_counts)],
        "interleaved": interleaved,
    }


NESTED_CASE_SPECS = (
    _nested_case("H1R-N01-a", "nested-single", (0,), "Accepted"),
    _nested_case("H1R-N01-b", "nested-single", (1,), "Accepted"),
    _nested_case("H1R-N01-c", "nested-single", (65534,), "Accepted"),
    _nested_case("H1R-N01-d", "nested-single", (65535,), "Accepted"),
    _nested_case("H1R-N02-a", "nested-single", (65536,), "ControlledRejected"),
    _nested_case("H1R-N02-b", "nested-single", (65537,), "ControlledRejected"),
    _nested_case("H1R-N03-interleaved", "nested-interleaved", (2, 2), "Accepted",
                 interleaved=True),
    _nested_case("H1R-N04-adjacent-valid", "nested-adjacent-valid", (1, 65535),
                 "Accepted"),
    _nested_case("H1R-N04-adjacent-overflow", "nested-adjacent-overflow", (1, 65536),
                 "ControlledRejected"),
    _nested_case("H1R-N05-final-repeat", "nested-final-repeat", (65535,), "Accepted"),
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def version(path: Path, *arguments: str) -> str:
    run = subprocess.run([str(path), *arguments], check=True, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return run.stdout.replace("\x00", "").strip()


def canonical_new_root(path: Path) -> Path:
    path = Path(path)
    if not path.is_absolute() or path != path.resolve() or path.exists() or path.is_symlink():
        raise ValueError("output root must be a new canonical absolute path")
    if not path.parent.is_dir() or path.parent.is_symlink() or path.parent != path.parent.resolve():
        raise ValueError("output root parent must be an existing canonical directory")
    return path


def _metadata_table_location(data: bytes) -> tuple[int, int, int, int, int, int]:
    """Return #~ absolute offset, heap flags, valid mask, row counts, and table offset.

    This is a bounded locator used only to reorder the NESTEDCLASS rows emitted by
    Cecil for the interleaved recipe.  It does not parse or load assembly code.
    """
    def u(offset: int, size: int) -> int:
        if offset < 0 or offset + size > len(data):
            raise ValueError("truncated PE/CLI metadata")
        return int.from_bytes(data[offset:offset + size], "little")

    pe = u(0x3c, 4)
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")
    section_count, optional_size = u(pe + 6, 2), u(pe + 20, 2)
    optional = pe + 24
    magic = u(optional, 2)
    directory, number_of_directories = ((96, 92) if magic == 0x10b else
                                        (112, 108) if magic == 0x20b else (0, 0))
    if optional_size < directory + 15 * 8 or u(optional + number_of_directories, 4) < 15:
        raise ValueError("missing CLI data directory")
    sections = []
    for index in range(section_count):
        section = optional + optional_size + index * 40
        sections.append((u(section + 12, 4), u(section + 16, 4), u(section + 20, 4)))

    def rva(value: int, size: int) -> int:
        matches = [pointer + value - start for start, length, pointer in sections
                   if start <= value and value + size <= start + length]
        if len(matches) != 1:
            raise ValueError("unmapped or ambiguous PE RVA")
        return matches[0]

    cli_directory = optional + directory + 14 * 8
    cli = rva(u(cli_directory, 4), u(cli_directory + 4, 4))
    metadata = rva(u(cli + 8, 4), u(cli + 12, 4))
    if data[metadata:metadata + 4] != b"BSJB":
        raise ValueError("invalid metadata root")
    version_size = u(metadata + 12, 4)
    cursor = (metadata + 16 + version_size + 3) & ~3
    stream_count = u(cursor + 2, 2)
    cursor += 4
    tables = None
    for _ in range(stream_count):
        relative, size = u(cursor, 4), u(cursor + 4, 4)
        name_end = cursor + 8
        while name_end < cursor + 40 and data[name_end]:
            name_end += 1
        if name_end == cursor + 40:
            raise ValueError("unterminated metadata stream name")
        name = data[cursor + 8:name_end].decode("ascii")
        if name == "#~":
            tables = (metadata + relative, size)
        cursor = (name_end + 4) & ~3
    if tables is None:
        raise ValueError("missing #~ metadata stream")
    table_offset, table_size = tables
    if table_offset + table_size > len(data):
        raise ValueError("truncated #~ metadata stream")
    heap_flags = u(table_offset + 6, 1)
    valid = u(table_offset + 8, 8)
    row_counts = [0] * 45
    cursor = table_offset + 24
    for table in range(45):
        if valid & (1 << table):
            row_counts[table] = u(cursor, 4)
            cursor += 4
    return table_offset, table_size, heap_flags, valid, cursor, row_counts


def _table_layout(data: bytes) -> tuple[object, int, list[int], dict[int, int], dict[int, int], int]:
    """Return pinned table schema details and absolute offsets for each table."""
    table_offset, _, heap_flags, valid, cursor, row_counts = _metadata_table_location(data)
    reader = load_identity_reader()

    def width(column: object) -> int:
        if isinstance(column, int):
            return 4 if row_counts[column] >= 65536 else 2
        if column in ("u2", "u4"):
            return int(column[1:])
        if column in ("s", "b", "g"):
            return 4 if heap_flags & {"s": 1, "g": 2, "b": 4}[column] else 2
        bits, targets = reader.CODED[column]
        return 4 if max(row_counts[target] for target in targets) >= 1 << (16 - bits) else 2

    offsets: dict[int, int] = {}
    widths: dict[int, int] = {}
    for table, schema in enumerate(reader.TABLES):
        row_width = sum(width(column) for column in schema)
        offsets[table], widths[table] = cursor, row_width
        cursor += row_counts[table] * row_width
    sorted_mask = int.from_bytes(data[table_offset + 16:table_offset + 24], "little")
    return reader, table_offset, row_counts, offsets, widths, sorted_mask


def interleave_nested_rows(groups: list[list[bytes]]) -> list[bytes]:
    """Return rows in round-robin order while preserving each group order."""
    result = []
    position = 0
    while any(position < len(group) for group in groups):
        for group in groups:
            if position < len(group):
                result.append(group[position])
        position += 1
    return result


def reorder_interleaved_nested_rows(path: Path, declaring_types: tuple[str, ...]) -> None:
    """Interleave declaring groups while retaining child-RID table sorting."""
    data = bytearray(path.read_bytes())
    reader, table_offset, counts, offsets, widths, sorted_mask = _table_layout(bytes(data))
    nested_offset, row_width = offsets[41], widths[41]
    type_offset, type_row_width = offsets[2], widths[2]
    if row_width not in (4, 8):
        raise ValueError("unexpected NESTEDCLASS row width")

    # The generated nested table has two TypeDef indices per row.  Cecil emits
    # each declaring type as a contiguous group; retain each group's row order.
    groups: dict[int, list[bytes]] = {}
    for index in range(counts[41]):
        row = bytes(data[nested_offset + index * row_width:nested_offset + (index + 1) * row_width])
        child = int.from_bytes(row[:row_width // 2], "little")
        parent = int.from_bytes(row[row_width // 2:], "little")
        groups.setdefault(parent, []).append(row)
    if len(groups) != len(declaring_types):
        raise ValueError("generated nested groups differ from recipe")

    # Group IDs are supplied in emitted parent order.  The writer creates them
    # in the same order, so this avoids making names or heap parsing part of the
    # byte-level reorder operation.
    ordered_groups = list(groups.values())
    if len(ordered_groups) != len(declaring_types):
        raise ValueError("nested group order is ambiguous")
    old_children = [int.from_bytes(row[:row_width // 2], "little")
                    for row in interleave_nested_rows(ordered_groups)]
    child_set = {int.from_bytes(row[:row_width // 2], "little")
                 for row in sum(ordered_groups, [])}
    top_level = [rid for rid in range(1, counts[2] + 1) if rid not in child_set]
    old_order = top_level + old_children
    if len(old_order) != counts[2] or len(set(old_order)) != counts[2]:
        raise ValueError("nested TypeDef rows are incomplete or duplicated")
    old_to_new = {old: new for new, old in enumerate(old_order, 1)}
    type_rows = [bytes(data[type_offset + (rid - 1) * type_row_width:
                        type_offset + rid * type_row_width]) for rid in old_order]
    for rid, row in enumerate(type_rows):
        start = type_offset + rid * type_row_width
        data[start:start + type_row_width] = row

    remapped_rows = []
    for group in ordered_groups:
        for row in group:
            old_child = int.from_bytes(row[:row_width // 2], "little")
            old_parent = int.from_bytes(row[row_width // 2:], "little")
            remapped_rows.append((old_to_new[old_child], old_to_new[old_parent]))
    remapped_rows.sort(key=lambda pair: pair[0])
    index_width = row_width // 2
    for index, (child, parent) in enumerate(remapped_rows):
        row = child.to_bytes(index_width, "little") + parent.to_bytes(index_width, "little")
        start = nested_offset + index * row_width
        data[start:start + row_width] = row
    # The reordered rows remain sorted by child RID, so preserve the emitted
    # NestedClass sorted declaration instead of masking an invalid permutation.
    if remapped_rows and not (sorted_mask & (1 << 41)):
        sorted_mask |= 1 << 41
        data[table_offset + 16:table_offset + 24] = sorted_mask.to_bytes(8, "little")
    path.write_bytes(data)


def input_paths() -> tuple[Path, ...]:
    return (SOURCE, LAUNCHER, IDENTITY_READER, MONO, MCS, CECIL)


def input_hashes() -> dict[str, str]:
    return {str(path): digest(path) for path in input_paths()}


def load_identity_reader():
    spec = importlib.util.spec_from_file_location("h1_m04_metadata", IDENTITY_READER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned identity reader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity_record(path: Path) -> dict[str, object]:
    reader = load_identity_reader()
    identity = reader.read_identity(path)
    return {
        "path": str(path),
        "sha256": identity["sha256"],
        "sizeBytes": path.stat().st_size,
        "name": identity["name"],
        "version": identity["version"],
        "fullName": identity["fullName"],
        "mvid": identity["mvid"],
    }


def require_identity(path: Path, expected_name: str) -> dict[str, object]:
    record = identity_record(path)
    if record["name"] != expected_name:
        raise RuntimeError(f"{path}: generated identity {record['name']!r} differs from {expected_name!r}")
    return record


def assembly_name(case_id: str, shadow: bool, family: str = "parameters") -> str:
    if shadow:
        return TARGET_TYPE if family == "parameters" else NESTED_TARGET_TYPE
    prefix = "AssemblyShadow.H1Count" if family == "parameters" else "AssemblyShadow.H1Nested"
    return prefix + ".Ordinary." + case_id


def target_type(case_id: str, shadow: bool, family: str = "parameters") -> str:
    if family == "nested":
        return NESTED_TARGET_TYPE
    if shadow:
        return TARGET_TYPE if family == "parameters" else NESTED_TARGET_TYPE
    prefix = "AssemblyShadow.H1Count" if family == "parameters" else "AssemblyShadow.H1Nested"
    return prefix + ".Ordinary_" + "".join(
        character if character.isalnum() else "_" for character in case_id)


def generation_command(binary: Path, output: Path, case_id: str, count: int,
                       variant: str, seed: int, shadow: bool, family: str) -> list[str]:
    command = [str(MONO), str(binary), str(output), assembly_name(case_id, shadow, family),
               case_id, str(count), variant, str(seed)]
    if family == "nested":
        command.append("nested")
    return command


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=("parameters", "nested"), required=True)
    parser.add_argument("--case-set", choices=("all",), required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    if args.seed < 0 or args.seed > 0x7fffffff:
        parser.error("--seed must be in 0..2147483647")
    output = canonical_new_root(args.output_root)
    if any(not path.is_file() or path.is_symlink() for path in input_paths()):
        raise RuntimeError("pinned writer, launcher, metadata reader, or Unity tool is unavailable")

    output.mkdir()
    (output / "ordinary").mkdir()
    (output / "shadow").mkdir()
    before = input_hashes()
    source_bytes = SOURCE.read_bytes()
    cecil_bytes = CECIL.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != before[str(SOURCE)] or hashlib.sha256(cecil_bytes).hexdigest() != before[str(CECIL)]:
        raise RuntimeError("generator inputs changed while being captured")

    compile_command: list[str]
    generate_commands: list[list[str]] = []
    records: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="h1-count-fixtures-", dir=str(output)) as temporary:
        temporary_root = Path(temporary)
        binary = temporary_root / "h1-count-fixture-writer.exe"
        source_snapshot = temporary_root / SOURCE.name
        cecil_snapshot = temporary_root / CECIL.name
        source_snapshot.write_bytes(source_bytes)
        cecil_snapshot.write_bytes(cecil_bytes)
        compile_command = [str(MCS), "-nologo", "-target:exe", "-out:" + str(binary),
                           "-r:" + str(cecil_snapshot), str(source_snapshot)]
        subprocess.run(compile_command, check=True)

        specifications = CASE_SPECS if args.family == "parameters" else NESTED_CASE_SPECS
        for specification in specifications:
            case_id = str(specification["caseId"])
            count = int(specification["count"])
            variant = str(specification["variant"])
            record: dict[str, object] = dict(specification)
            for flavor, shadow in (("ordinary", False), ("shadow", True)):
                path = output / flavor / (case_id + ".dll")
                command = generation_command(binary, path, case_id, count, variant,
                                             args.seed, shadow, args.family)
                subprocess.run(command, check=True)
                generate_commands.append(command)
                if path.stat().st_size > MAX_DLL_BYTES:
                    raise RuntimeError(str(path) + ": generated DLL exceeds 32 MiB")
                if args.family == "nested" and bool(specification["interleaved"]):
                    reorder_interleaved_nested_rows(
                        path, tuple(str(name) for name in specification["declaringTypes"]))
                    if path.stat().st_size > MAX_DLL_BYTES:
                        raise RuntimeError(str(path) + ": generated DLL exceeds 32 MiB")
                record[flavor] = require_identity(path, assembly_name(case_id, shadow,
                                                                       args.family))
                record[flavor]["targetType"] = target_type(case_id, shadow, args.family)
                record[flavor]["targetMethod"] = TARGET_METHOD if args.family == "parameters" else None
            records.append(record)

    after = input_hashes()
    if after != before:
        failure = {
            "schemaVersion": 1,
            "kind": "H1CountFixtureFailureReceipt",
            "family": args.family,
            "result": "FailedInputDrift",
            "inputHashesBefore": before,
            "inputHashesAfter": after,
            "inputsUnchanged": False,
        }
        with (output / "h1-count-fixture-failure.json").open("x", encoding="utf-8") as stream:
            json.dump(failure, stream, indent=2, sort_keys=True)
            stream.write("\n")
        raise RuntimeError("generator inputs changed during execution")

    receipt = {
        "schemaVersion": 1,
        "kind": "H1CountFixtureManifest",
        "family": args.family,
        "caseSet": args.case_set,
        "seed": args.seed,
        "targetType": TARGET_TYPE if args.family == "parameters" else NESTED_TARGET_TYPE,
        "targetMethod": TARGET_METHOD,
        "recipe": {
            "family": args.family,
            "caseSet": args.case_set,
            "seed": args.seed,
            "cases": [dict(case) for case in specifications],
            "flavors": ["ordinary", "shadow"],
        },
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "generator": {
            "sourcePath": str(SOURCE),
            "sourceSha256": before[str(SOURCE)],
            "launcherPath": str(LAUNCHER),
            "launcherSha256": before[str(LAUNCHER)],
            "identityReaderPath": str(IDENTITY_READER),
            "identityReaderSha256": before[str(IDENTITY_READER)],
            "monoPath": str(MONO),
            "monoSha256": before[str(MONO)],
            "monoVersion": version(MONO, "--version").splitlines()[0],
            "compilerPath": str(MCS),
            "compilerSha256": before[str(MCS)],
            "compilerVersion": version(MCS, "--version"),
            "cecilPath": str(CECIL),
            "cecilSha256": before[str(CECIL)],
            "compileCommand": compile_command,
            "generateCommands": generate_commands,
            "inputHashesBefore": before,
            "inputHashesAfter": after,
            "inputsUnchanged": True,
            "shapeAudit": "pending-independent-h1_count_fixture_audit",
        },
        "cases": records,
    }
    manifest = output / "h1-count-fixture-manifest.json"
    with manifest.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"result": "Generated", "manifest": str(manifest), "caseCount": len(records)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
