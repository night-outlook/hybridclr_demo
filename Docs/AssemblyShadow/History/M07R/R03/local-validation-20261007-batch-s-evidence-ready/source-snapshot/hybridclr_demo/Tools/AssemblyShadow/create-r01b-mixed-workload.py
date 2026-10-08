#!/usr/bin/env python3
"""Materialize the hash-bound mixed R01B ordinary/Shadow 512 MiB envelope."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from m04_metadata import read_identity
from m05_types import CliTables
from r00_player_inputs import verify_inputs
from r01b_capacity_inputs import (HERE, IMAGE_COUNT, MAXIMUM_DLL_BYTES, MEAN_DLL_BYTES, TOTAL_DLL_BYTES,
                                  canonical_directory, canonical_file, digest, validate_mixed_workload,
                                  validate_workload)
from shadow_tools import require


FAILED_INPUT = bytes((0x42, 0x41, 0x44, 0x00))
RETAINED_FAILURE_COUNT = 3
PADDING_BYTE = 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--fixture-manifest", required=True, type=Path)
    parser.add_argument("--on-build", required=True, type=Path)
    parser.add_argument("--off-build", required=True, type=Path)
    parser.add_argument("--replay-receipt", required=True, type=Path)
    parser.add_argument("--ordinary-manifest", required=True, type=Path)
    parser.add_argument("--ordinary-corpus", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    project = canonical_directory(args.project_root, "project root")
    fixture_path = canonical_file(args.fixture_manifest, "M07 fixture manifest")
    on_build = canonical_file(args.on_build, "NativeOn build receipt")
    off_build = canonical_file(args.off_build, "NativeOff build receipt")
    replay = canonical_file(args.replay_receipt, "M07 replay receipt")
    ordinary_manifest = canonical_file(args.ordinary_manifest, "R01B ordinary workload manifest")
    ordinary_root = canonical_directory(args.ordinary_corpus, "R01B ordinary corpus root")
    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and not output.is_symlink() and
            output.parent.is_dir() and not output.parent.is_symlink(),
            "output root must be a new canonical absolute path with an existing parent")
    require(output != ordinary_root and not output.is_relative_to(ordinary_root) and
            not ordinary_root.is_relative_to(output), "mixed output must be separate from the ordinary corpus")

    # This verifies the current M07 fixture, patch closure, ON/OFF receipts and
    # replay before any bytes are copied. It is the freshness/provenance gate.
    context = verify_inputs(project, fixture_path, on_build, off_build, replay)
    ordinary, ordinary_paths = validate_workload(ordinary_manifest, ordinary_root, deep=True)
    p03 = context["fixtures"]["P03"]
    fixture = p03["fixture"]
    patch = p03["patch"]
    patch_root = canonical_directory(p03["root"], "M07 P03 patch root")
    require(fixture["patchId"] == patch["patchId"] == "P03" and
            fixture["closureLoadOrder"] == patch["loadOrder"] and len(fixture["closureLoadOrder"]) == 5,
            "Fresh M07 P03 closure is not the expected five-image order")

    shadow_rows = []
    shadow_bytes = 0
    for name in fixture["closureLoadOrder"]:
        source = next(row for row in patch["closure"] if row["name"] == name)
        path = canonical_file(patch_root / source["dll"], "M07 P03 closure DLL")
        data = path.read_bytes()
        identity = read_identity(path)
        tables = CliTables(data, path)
        require(digest(path) == source["sha256"] and identity["mvid"] == source["mvid"] and
                identity["name"] == name and tables.type_inventory()["assemblyName"] == name,
                "M07 P03 closure identity/hash drifted: " + name)
        shadow_rows.append({
            "name": name, "path": str(path), "sha256": digest(path), "sizeBytes": len(data),
            "mvid": identity["mvid"], "fullName": identity["fullName"],
            "typeDefRows": tables.counts[2], "methodDefRows": tables.counts[6],
            "stringsHeapBytes": len(tables.streams["#Strings"]),
        })
        shadow_bytes += len(data)

    selected = ordinary_paths[:IMAGE_COUNT - len(shadow_rows) - RETAINED_FAILURE_COUNT]
    selected_rows = ordinary["assemblies"][:len(selected)]
    source_total = sum(row["sizeBytes"] for row in selected_rows)
    ordinary_target = TOTAL_DLL_BYTES - shadow_bytes
    padding = ordinary_target - source_total
    require(padding > 0 and ordinary_target <= TOTAL_DLL_BYTES and
            selected_rows[-1]["id"] == len(selected_rows) - 1,
            "R01B mixed ordinary split cannot reach the exact valid DLL envelope")
    pad_id = selected_rows[-1]["id"]
    mixed_rows = []
    output_corpus = output / "corpus"
    output_corpus.mkdir(parents=True)
    for row, source_path in zip(selected_rows, selected):
        source_data = source_path.read_bytes()
        pad_bytes = padding if row["id"] == pad_id else 0
        data = source_data + bytes((PADDING_BYTE,)) * pad_bytes
        destination = output_corpus / source_path.name
        with destination.open("xb") as stream:
            stream.write(data)
        identity = read_identity(destination)
        tables = CliTables(data, destination)
        require(identity["name"] == row["name"] and identity["mvid"] == read_identity(source_path)["mvid"] and
                tables.type_inventory()["assemblyName"] == row["name"] and tables.counts[2] == row["typeDefRowsActual"] and
                tables.counts[6] == row["methodDefRowsActual"] and len(tables.streams["#Strings"]) == row["stringsHeapBytesActual"],
                "Mixed padded DLL did not preserve independent PE/CLI identity: " + row["name"])
        mixed_rows.append({
            "id": row["id"], "name": row["name"], "file": destination.name, "sha256": digest(destination),
            "sizeBytes": len(data), "sourcePath": str(source_path), "sourceSha256": row["sha256"],
            "bodyPrefixSha256": row["sha256"],
            "sourceSizeBytes": len(source_data), "paddingBytes": pad_bytes, "mvid": identity["mvid"],
            "sourceMvid": read_identity(source_path)["mvid"], "fullName": identity["fullName"],
            "typeDefRows": tables.counts[2], "methodDefRows": tables.counts[6],
            "stringsHeapBytes": len(tables.streams["#Strings"]), "sourceTypeDefRows": row["typeDefRowsActual"],
            "sourceMethodDefRows": row["methodDefRowsActual"], "sourceStringsHeapBytes": row["stringsHeapBytesActual"],
        })
    valid_ordinary = source_total + padding
    require(valid_ordinary + shadow_bytes == TOTAL_DLL_BYTES and max(row["sizeBytes"] for row in mixed_rows) == MAXIMUM_DLL_BYTES,
            "Mixed materialization did not satisfy the exact 512 MiB/32 MiB envelope")
    generator = HERE / "create-r01b-mixed-workload.py"
    source = {
        "ordinaryManifestPath": str(ordinary_manifest), "ordinaryManifestSha256": digest(ordinary_manifest),
        "ordinaryCorpusRoot": str(ordinary_root), "fixtureManifestPath": str(fixture_path),
        "fixtureManifestSha256": digest(fixture_path), "patchManifestPath": str(p03["path"]),
        "patchManifestSha256": digest(p03["path"]), "patchId": "P03", "onBuildPath": str(on_build),
        "onBuildSha256": digest(on_build), "offBuildPath": str(off_build), "offBuildSha256": digest(off_build),
        "replayReceiptPath": str(replay), "replayReceiptSha256": digest(replay), "generatorPath": str(generator),
        "generatorSha256": digest(generator),
    }
    manifest = {
        "schemaVersion": 1, "kind": "R01BMixedWorkloadManifest",
        "status": "DerivedFromVerifiedM07P03AndOrdinaryCorpus", "requiredImages": IMAGE_COUNT,
        "retainedFailureCount": RETAINED_FAILURE_COUNT, "failedInputBytes": len(FAILED_INPUT) * RETAINED_FAILURE_COUNT,
        "retainedFailureInputs": [{"attempt": index, "hex": bytes((0x42, 0x41, 0x44, index)).hex(),
                                   "sha256": hashlib.sha256(bytes((0x42, 0x41, 0x44, index))).hexdigest(),
                                   "sizeBytes": len(FAILED_INPUT)} for index in range(RETAINED_FAILURE_COUNT)],
        "paddingEvidence": {"method": "DeterministicZeroTrailer", "addressabilityEstablished": False,
                             "note": "Zero trailer padding preserves the original PE/CLI body and identity proof; it cannot establish metadata addressability for the added bytes."},
        "source": source, "shadow": {"imageCount": len(shadow_rows), "validDllBytes": shadow_bytes, "assemblies": shadow_rows},
        "ordinary": {"selectedCount": len(mixed_rows), "sourceStartIndex": 0,
                      "sourceEndIndex": mixed_rows[-1]["id"], "sourceBytes": source_total,
                      "paddingBytes": padding, "validDllBytes": valid_ordinary, "paddingAssemblyId": pad_id},
        "totals": {"assemblyCount": IMAGE_COUNT, "shadowImageCount": len(shadow_rows),
                   "retainedFailureCount": RETAINED_FAILURE_COUNT, "ordinarySourceBytes": source_total,
                   "ordinaryValidDllBytes": valid_ordinary, "shadowValidDllBytes": shadow_bytes,
                   "paddingBytes": padding, "validDllBytes": TOTAL_DLL_BYTES,
                   "failedInputBytes": len(FAILED_INPUT) * RETAINED_FAILURE_COUNT,
                   "maxBytes": MAXIMUM_DLL_BYTES, "meanBytes": MEAN_DLL_BYTES},
        "assemblies": mixed_rows,
    }
    manifest_path = output / "r01b-mixed-workload-manifest.json"
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    # Re-read the artifact through the strict verifier, including the body and
    # metadata proof, before declaring generation complete.
    validate_mixed_workload(manifest_path, output_corpus, deep=True)
    print(json.dumps({"result": "Passed", "manifest": str(manifest_path), "corpus": str(output_corpus),
                      "ordinaryValidDllBytes": valid_ordinary, "shadowValidDllBytes": shadow_bytes,
                      "validDllBytes": TOTAL_DLL_BYTES, "paddingBytes": padding}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
