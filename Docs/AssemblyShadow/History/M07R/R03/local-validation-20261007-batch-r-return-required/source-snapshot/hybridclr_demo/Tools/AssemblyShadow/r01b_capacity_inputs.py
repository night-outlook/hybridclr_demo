"""Strict shared input readers for the R01B capacity Player and verifier."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import plistlib
import re
from typing import Any

from m04_metadata import read_identity
from m05_types import CliTables
from shadow_tools import read_json, require


HERE = Path(__file__).resolve().parent
IMAGE_COUNT = 8192
MAXIMUM_DLL_BYTES = 32 * 1024 * 1024
TOTAL_DLL_BYTES = 512 * 1024 * 1024
MEAN_DLL_BYTES = 64 * 1024
USABLE_PAGES = 524287
CHARGED_PAGE_CEILING = 393215
MINIMUM_FREE_PAGES = 131072
WORKLOAD_FIELDS = frozenset(("assemblies", "correction", "errataSha256", "kind", "schemaVersion",
                             "sealedOriginalManifestSha256", "sealedOriginalReceiptSha256", "status", "totals"))
ROW_FIELDS = frozenset(("file", "id", "methodDefRowsActual", "methodDefRowsExpected", "name", "sha256",
                        "sizeBytes", "stringsHeapBytesActual", "typeDefRowsActual"))
MIXED_FIELDS = frozenset(("schemaVersion", "kind", "status", "requiredImages", "retainedFailureCount",
                          "failedInputBytes", "retainedFailureInputs", "paddingEvidence", "source", "shadow", "ordinary", "totals", "assemblies"))
MIXED_FAILURE_FIELDS = frozenset(("attempt", "hex", "sha256", "sizeBytes"))
MIXED_PADDING_FIELDS = frozenset(("method", "addressabilityEstablished", "note"))
MIXED_SOURCE_FIELDS = frozenset(("ordinaryManifestPath", "ordinaryManifestSha256", "ordinaryCorpusRoot",
                                "fixtureManifestPath", "fixtureManifestSha256", "patchManifestPath",
                                "patchManifestSha256", "patchId", "onBuildPath", "onBuildSha256", "offBuildPath",
                                "offBuildSha256", "replayReceiptPath", "replayReceiptSha256", "generatorPath",
                                "generatorSha256"))
MIXED_SHADOW_FIELDS = frozenset(("imageCount", "validDllBytes", "assemblies"))
MIXED_SHADOW_ROW_FIELDS = frozenset(("name", "path", "sha256", "sizeBytes", "mvid", "fullName", "typeDefRows",
                                    "methodDefRows", "stringsHeapBytes"))
MIXED_ORDINARY_FIELDS = frozenset(("selectedCount", "sourceStartIndex", "sourceEndIndex", "sourceBytes", "paddingBytes",
                                  "validDllBytes", "paddingAssemblyId"))
MIXED_TOTAL_FIELDS = frozenset(("assemblyCount", "shadowImageCount", "retainedFailureCount", "ordinarySourceBytes",
                               "ordinaryValidDllBytes", "shadowValidDllBytes", "paddingBytes", "validDllBytes",
                               "failedInputBytes", "maxBytes", "meanBytes"))
MIXED_ROW_FIELDS = frozenset(("id", "name", "file", "sha256", "sizeBytes", "sourcePath", "sourceSha256", "bodyPrefixSha256",
                             "sourceSizeBytes", "paddingBytes", "mvid", "sourceMvid", "fullName", "typeDefRows",
                             "methodDefRows", "stringsHeapBytes", "sourceTypeDefRows", "sourceMethodDefRows",
                             "sourceStringsHeapBytes"))
HASH = re.compile(r"[0-9a-f]{64}")
MVID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")
OVERFLOW_FIELDS = frozenset(("schemaVersion", "kind", "milestone", "result", "createdAtUtc",
                             "assembly", "generator", "verification"))
OVERFLOW_ASSEMBLY_FIELDS = frozenset(("id", "name", "path", "sha256", "sizeBytes", "mvid", "fullName",
                                      "typeDefRows", "methodDefRows", "stringsHeapBytes"))
OVERFLOW_GENERATOR_FIELDS = frozenset(("sourcePath", "sourceSha256", "launcherPath", "launcherSha256", "monoPath",
                                      "monoSha256", "monoVersion", "compilerPath", "compilerSha256", "compilerVersion",
                                      "cecilPath", "cecilSha256", "compileCommand", "generateCommand",
                                      "inputHashesBefore", "inputHashesAfter", "inputsUnchanged"))
OVERFLOW_VERIFICATION_FIELDS = frozenset(("identityReader", "identityReaderSha256", "typeTableReader",
                                          "typeTableReaderSha256", "distinctFromSupportedCorpus", "note"))


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing or symlinked input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_file(value: str | Path, label: str) -> Path:
    require(isinstance(value, (str, Path)), label + " must be a canonical absolute regular file")
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_file() and not path.is_symlink(),
            label + " must be a canonical absolute regular file")
    return path


def canonical_directory(value: str | Path, label: str) -> Path:
    require(isinstance(value, (str, Path)), label + " must be a canonical absolute directory")
    path = Path(value)
    require(path.is_absolute() and path == path.resolve(strict=True) and path.is_dir() and not path.is_symlink(),
            label + " must be a canonical absolute directory")
    return path


def executable_for(app: Path) -> Path:
    app = canonical_directory(app, "Player app")
    require(app.suffix == ".app", "Player output is not a macOS app")
    with (app / "Contents/Info.plist").open("rb") as stream:
        name = plistlib.load(stream)["CFBundleExecutable"]
    require(type(name) is str and Path(name).name == name, "Invalid Player executable name")
    return canonical_file(app / "Contents/MacOS" / name, "Player executable")


def validate_workload(manifest_path: Path, corpus_root: Path, deep: bool) -> tuple[dict, list[Path]]:
    manifest_path = canonical_file(manifest_path, "R01B workload manifest")
    corpus_root = canonical_directory(corpus_root, "R01B corpus root")
    value = read_json(manifest_path)
    require(type(value) is dict and set(value) == WORKLOAD_FIELDS and type(value["schemaVersion"]) is int and
            value["schemaVersion"] == 1 and type(value["kind"]) is str and
            value["kind"] == "R01BWorkloadV2VerifiedManifest" and type(value["status"]) is str and
            value["status"] == "CorrectedMetadataOnlySealedCorpus", "Wrong R01B workload manifest schema")
    require(all(type(value[field]) is str and HASH.fullmatch(value[field])
                for field in ("errataSha256", "sealedOriginalManifestSha256", "sealedOriginalReceiptSha256")),
            "Invalid sealed workload provenance hash")
    totals = value["totals"]
    require(type(totals) is dict and set(totals) == {"assemblyCount", "maxBytes", "meanBytes", "totalBytes"} and
            all(type(totals[field]) is int for field in ("assemblyCount", "maxBytes", "meanBytes", "totalBytes")) and
            totals == {"assemblyCount": IMAGE_COUNT, "maxBytes": MAXIMUM_DLL_BYTES,
                       "meanBytes": MEAN_DLL_BYTES, "totalBytes": TOTAL_DLL_BYTES},
            "R01B workload envelope differs")
    rows = value["assemblies"]
    require(type(rows) is list and len(rows) == IMAGE_COUNT, "R01B workload must contain exactly 8,192 rows")
    paths: list[Path] = []
    names: set[str] = set()
    hashes: set[str] = set()
    total = 0
    maximum = 0
    for index, row in enumerate(rows):
        label = f"workload.assemblies[{index}]"
        name = f"AssemblyShadow.WorkloadV2.I{index:04d}"
        file_name = name + ".dll"
        require(type(row) is dict and set(row) == ROW_FIELDS and type(row["id"]) is int and
                row["id"] == index and type(row["name"]) is str and row["name"] == name and
                type(row["file"]) is str and row["file"] == file_name and
                type(row["methodDefRowsActual"]) is int and row["methodDefRowsActual"] == 98 and
                type(row["methodDefRowsExpected"]) is int and row["methodDefRowsExpected"] == 98 and
                type(row["typeDefRowsActual"]) is int and row["typeDefRowsActual"] == 98 and
                type(row["stringsHeapBytesActual"]) is int and
                row["stringsHeapBytesActual"] > 4096 and type(row["sizeBytes"]) is int and
                0 < row["sizeBytes"] <= MAXIMUM_DLL_BYTES and type(row["sha256"]) is str and
                HASH.fullmatch(row["sha256"]), label + ": invalid value")
        require(name.casefold() not in names and row["sha256"] not in hashes, label + ": duplicate identity or bytes")
        names.add(name.casefold())
        hashes.add(row["sha256"])
        path = canonical_file(corpus_root / file_name, label + ".file")
        require(path.parent == corpus_root and path.stat().st_size == row["sizeBytes"] and digest(path) == row["sha256"],
                label + ": DLL size/hash mismatch")
        if deep:
            identity = read_identity(path)
            tables = CliTables(path.read_bytes(), path)
            require(identity["name"] == name and tables.type_inventory()["assemblyName"] == name and
                    tables.counts[2] == 98 and tables.counts[6] == 98 and
                    len(tables.streams["#Strings"]) == row["stringsHeapBytesActual"],
                    label + ": independent PE/CLI metadata mismatch")
        total += row["sizeBytes"]
        maximum = max(maximum, row["sizeBytes"])
        paths.append(path)
    require(total == TOTAL_DLL_BYTES and maximum == MAXIMUM_DLL_BYTES,
            "R01B workload rows do not satisfy the declared byte envelope")
    require({path.name for path in corpus_root.glob("*.dll")} == {path.name for path in paths},
            "R01B corpus DLL inventory differs from the manifest")
    return value, paths


def validate_mixed_workload(manifest_path: Path, corpus_root: Path, deep: bool) -> tuple[dict, list[Path]]:
    """Validate the separately materialized mixed ordinary/Shadow input envelope."""
    manifest_path = canonical_file(manifest_path, "R01B mixed workload manifest")
    corpus_root = canonical_directory(corpus_root, "R01B mixed corpus root")
    value = read_json(manifest_path)
    require(type(value) is dict and set(value) == MIXED_FIELDS and type(value["schemaVersion"]) is int and
            value["schemaVersion"] == 1 and value["kind"] == "R01BMixedWorkloadManifest" and
            value["status"] == "DerivedFromVerifiedM07P03AndOrdinaryCorpus" and
            type(value["requiredImages"]) is int and value["requiredImages"] == IMAGE_COUNT and
            type(value["retainedFailureCount"]) is int and value["retainedFailureCount"] == 3 and
            type(value["failedInputBytes"]) is int and value["failedInputBytes"] == 12,
            "Wrong R01B mixed workload manifest schema")
    failures = value["retainedFailureInputs"]
    require(type(failures) is list and len(failures) == value["retainedFailureCount"],
            "Wrong R01B mixed retained failure inputs")
    for index, failure in enumerate(failures):
        expected = bytes((0x42, 0x41, 0x44, index))
        require(type(failure) is dict and set(failure) == MIXED_FAILURE_FIELDS and type(failure["attempt"]) is int and
                failure["attempt"] == index and type(failure["hex"]) is str and failure["hex"] == expected.hex() and
                type(failure["sizeBytes"]) is int and failure["sizeBytes"] == len(expected) and
                type(failure["sha256"]) is str and failure["sha256"] == hashlib.sha256(expected).hexdigest(),
                f"mixed.retainedFailureInputs[{index}]: invalid value")
    padding_evidence = value["paddingEvidence"]
    require(type(padding_evidence) is dict and set(padding_evidence) == MIXED_PADDING_FIELDS and
            padding_evidence["method"] == "DeterministicZeroTrailer" and
            padding_evidence["addressabilityEstablished"] is False and
            padding_evidence["note"] == "Zero trailer padding preserves the original PE/CLI body and identity proof; it cannot establish metadata addressability for the added bytes.",
            "R01B mixed padding evidence is incomplete")
    source = value["source"]
    require(type(source) is dict and set(source) == MIXED_SOURCE_FIELDS and
            all(type(source[field]) is str for field in MIXED_SOURCE_FIELDS) and
            all(HASH.fullmatch(source[field]) for field in ("ordinaryManifestSha256", "fixtureManifestSha256",
                                                             "patchManifestSha256", "onBuildSha256", "offBuildSha256",
                                                             "replayReceiptSha256", "generatorSha256")) and
            source["patchId"] == "P03" and source["generatorPath"] == str(HERE / "create-r01b-mixed-workload.py"),
            "Wrong R01B mixed workload provenance")
    ordinary_manifest = canonical_file(source["ordinaryManifestPath"], "R01B mixed ordinary manifest")
    ordinary_root = canonical_directory(source["ordinaryCorpusRoot"], "R01B mixed ordinary corpus")
    fixture_manifest = canonical_file(source["fixtureManifestPath"], "R01B mixed fixture manifest")
    patch_manifest = canonical_file(source["patchManifestPath"], "R01B mixed patch manifest")
    for path, expected, label in ((ordinary_manifest, source["ordinaryManifestSha256"], "ordinary manifest"),
                                  (fixture_manifest, source["fixtureManifestSha256"], "fixture manifest"),
                                  (patch_manifest, source["patchManifestSha256"], "patch manifest"),
                                  (canonical_file(source["onBuildPath"], "R01B mixed ON build"), source["onBuildSha256"], "ON build"),
                                  (canonical_file(source["offBuildPath"], "R01B mixed OFF build"), source["offBuildSha256"], "OFF build"),
                                  (canonical_file(source["replayReceiptPath"], "R01B mixed replay"), source["replayReceiptSha256"], "replay receipt"),
                                  (canonical_file(source["generatorPath"], "R01B mixed generator"), source["generatorSha256"], "generator")):
        require(digest(path) == expected, "R01B mixed " + label + " hash drifted")
    shadow = value["shadow"]
    require(type(shadow) is dict and set(shadow) == MIXED_SHADOW_FIELDS and type(shadow["imageCount"]) is int and
            shadow["imageCount"] == 5 and type(shadow["validDllBytes"]) is int and shadow["validDllBytes"] > 0 and
            type(shadow["assemblies"]) is list and len(shadow["assemblies"]) == shadow["imageCount"],
            "Wrong R01B mixed Shadow closure")
    shadow_paths: list[Path] = []
    shadow_names: list[str] = []
    shadow_total = 0
    for index, row in enumerate(shadow["assemblies"]):
        require(type(row) is dict and set(row) == MIXED_SHADOW_ROW_FIELDS and type(row["name"]) is str and
                type(row["path"]) is str and type(row["sha256"]) is str and HASH.fullmatch(row["sha256"]) and
                type(row["sizeBytes"]) is int and 0 < row["sizeBytes"] <= MAXIMUM_DLL_BYTES and
                type(row["mvid"]) is str and MVID.fullmatch(row["mvid"]) and type(row["fullName"]) is str and
                type(row["typeDefRows"]) is int and type(row["methodDefRows"]) is int and
                type(row["stringsHeapBytes"]) is int and row["stringsHeapBytes"] > 4096,
                f"mixed.shadow.assemblies[{index}]: invalid value")
        path = canonical_file(row["path"], f"mixed.shadow.assemblies[{index}].path")
        require(digest(path) == row["sha256"] and path.stat().st_size == row["sizeBytes"] and
                row["name"].casefold() not in {item.casefold() for item in shadow_names},
                f"mixed.shadow.assemblies[{index}]: hash or identity mismatch")
        if deep:
            identity = read_identity(path)
            tables = CliTables(path.read_bytes(), path)
            require(identity["name"] == row["name"] and identity["mvid"] == row["mvid"] and
                    identity["fullName"] == row["fullName"] and tables.type_inventory()["assemblyName"] == row["name"] and
                    tables.counts[2] == row["typeDefRows"] and tables.counts[6] == row["methodDefRows"] and
                    len(tables.streams["#Strings"]) == row["stringsHeapBytes"],
                    f"mixed.shadow.assemblies[{index}]: independent PE/CLI verification differs")
        shadow_paths.append(path)
        shadow_names.append(row["name"])
        shadow_total += row["sizeBytes"]
    require(shadow_total == shadow["validDllBytes"], "R01B mixed Shadow byte total differs")
    ordinary = value["ordinary"]
    require(type(ordinary) is dict and set(ordinary) == MIXED_ORDINARY_FIELDS and
            ordinary == {"selectedCount": IMAGE_COUNT - shadow["imageCount"] - value["retainedFailureCount"],
                         "sourceStartIndex": 0, "sourceEndIndex": IMAGE_COUNT - shadow["imageCount"] - value["retainedFailureCount"] - 1,
                         "sourceBytes": ordinary["sourceBytes"], "paddingBytes": ordinary["paddingBytes"],
                         "validDllBytes": ordinary["validDllBytes"], "paddingAssemblyId": ordinary["paddingAssemblyId"]} and
            all(type(ordinary[field]) is int for field in MIXED_ORDINARY_FIELDS) and ordinary["selectedCount"] > 0,
            "Wrong R01B mixed ordinary selection")
    totals = value["totals"]
    require(type(totals) is dict and set(totals) == MIXED_TOTAL_FIELDS and
            all(type(totals[field]) is int for field in MIXED_TOTAL_FIELDS) and
            totals["assemblyCount"] == IMAGE_COUNT and totals["shadowImageCount"] == shadow["imageCount"] and
            totals["retainedFailureCount"] == value["retainedFailureCount"] and totals["failedInputBytes"] == value["failedInputBytes"] and
            totals["validDllBytes"] == TOTAL_DLL_BYTES and totals["maxBytes"] == MAXIMUM_DLL_BYTES and
            totals["meanBytes"] == MEAN_DLL_BYTES and totals["shadowValidDllBytes"] == shadow["validDllBytes"] and
            totals["ordinaryValidDllBytes"] == ordinary["validDllBytes"] and totals["paddingBytes"] == ordinary["paddingBytes"] and
            totals["ordinarySourceBytes"] == ordinary["sourceBytes"] and
            totals["ordinaryValidDllBytes"] + totals["shadowValidDllBytes"] == totals["validDllBytes"] and
            totals["ordinarySourceBytes"] + totals["paddingBytes"] == totals["ordinaryValidDllBytes"],
            "R01B mixed totals do not satisfy the exact valid DLL envelope")
    rows = value["assemblies"]
    require(type(rows) is list and len(rows) == ordinary["selectedCount"], "R01B mixed ordinary row count differs")
    paths: list[Path] = []
    total_source = total_valid = total_padding = 0
    names: set[str] = set()
    for index, row in enumerate(rows):
        label = f"mixed.assemblies[{index}]"
        require(type(row) is dict and set(row) == MIXED_ROW_FIELDS and type(row["id"]) is int and
                row["id"] == index and type(row["name"]) is str and type(row["file"]) is str and
                type(row["sha256"]) is str and HASH.fullmatch(row["sha256"]) and type(row["sizeBytes"]) is int and
                0 < row["sizeBytes"] <= MAXIMUM_DLL_BYTES and all(type(row[field]) is int for field in
                ("sourceSizeBytes", "paddingBytes", "typeDefRows", "methodDefRows", "stringsHeapBytes",
                 "sourceTypeDefRows", "sourceMethodDefRows", "sourceStringsHeapBytes")) and
                all(type(row[field]) is str for field in ("sourcePath", "sourceSha256", "bodyPrefixSha256", "mvid", "sourceMvid", "fullName")) and
                HASH.fullmatch(row["sourceSha256"]) and row["bodyPrefixSha256"] == row["sourceSha256"] and
                MVID.fullmatch(row["mvid"]) and MVID.fullmatch(row["sourceMvid"]) and
                row["name"] == f"AssemblyShadow.WorkloadV2.I{index:04d}" and row["file"] == row["name"] + ".dll" and
                row["name"].casefold() not in names,
                label + ": invalid value")
        source_path = canonical_file(ordinary_root / row["file"], label + ".sourcePath")
        path = canonical_file(corpus_root / row["file"], label + ".file")
        source_bytes = source_path.read_bytes()
        data = path.read_bytes()
        require(source_path == canonical_file(row["sourcePath"], label + ".sourcePath.provenance") and
                digest(source_path) == row["sourceSha256"] == row["bodyPrefixSha256"] and len(source_bytes) == row["sourceSizeBytes"] and
                len(data) == row["sizeBytes"] and data[:len(source_bytes)] == source_bytes and
                data[len(source_bytes):] == bytes(row["paddingBytes"]) and row["sizeBytes"] == row["sourceSizeBytes"] + row["paddingBytes"] and
                digest(path) == row["sha256"], label + ": body/padding/hash mismatch")
        if deep:
            source_identity = read_identity(source_path)
            identity = read_identity(path)
            source_tables = CliTables(source_bytes, source_path)
            tables = CliTables(data, path)
            require(identity["name"] == row["name"] and identity["mvid"] == row["mvid"] == source_identity["mvid"] and
                    identity["fullName"] == row["fullName"] == source_identity["fullName"] and
                    tables.type_inventory()["assemblyName"] == row["name"] and source_tables.type_inventory()["assemblyName"] == row["name"] and
                    tables.counts[2] == row["typeDefRows"] == row["sourceTypeDefRows"] == source_tables.counts[2] and
                    tables.counts[6] == row["methodDefRows"] == row["sourceMethodDefRows"] == source_tables.counts[6] and
                    len(tables.streams["#Strings"]) == row["stringsHeapBytes"] == row["sourceStringsHeapBytes"] == len(source_tables.streams["#Strings"]),
                    label + ": independent PE/CLI identity or metadata proof differs")
        names.add(row["name"].casefold())
        paths.append(path)
        total_source += row["sourceSizeBytes"]
        total_valid += row["sizeBytes"]
        total_padding += row["paddingBytes"]
    require(total_source == ordinary["sourceBytes"] and total_valid == ordinary["validDllBytes"] and
            total_padding == ordinary["paddingBytes"] and ordinary["paddingAssemblyId"] == rows[-1]["id"],
            "R01B mixed ordinary totals differ from rows")
    require({path.name for path in corpus_root.glob("*.dll")} == {path.name for path in paths},
            "R01B mixed corpus DLL inventory differs from the manifest")
    return value, paths


def validate_overflow(receipt_path: Path, deep: bool) -> tuple[dict, Path]:
    receipt_path = canonical_file(receipt_path, "R01B overflow receipt")
    value = read_json(receipt_path)
    require(type(value) is dict and set(value) == OVERFLOW_FIELDS and type(value["schemaVersion"]) is int and
            value["schemaVersion"] == 1 and type(value["kind"]) is str and
            value["kind"] == "R01BOverflowFixtureReceipt" and type(value["milestone"]) is str and
            value["milestone"] == "R01B" and type(value["result"]) is str and value["result"] == "Passed",
            "Wrong R01B overflow receipt")
    require(type(value["createdAtUtc"]) is str and value["createdAtUtc"].endswith("Z"),
            "Invalid R01B overflow receipt timestamp")
    try:
        created = datetime.fromisoformat(value["createdAtUtc"].replace("Z", "+00:00"))
    except ValueError:
        require(False, "Invalid R01B overflow receipt timestamp")
    require(created.tzinfo is not None and created.utcoffset() == timezone.utc.utcoffset(created),
            "R01B overflow receipt timestamp must be UTC")
    row = value["assembly"]
    require(type(row) is dict and set(row) == OVERFLOW_ASSEMBLY_FIELDS and type(row["id"]) is int and
            type(row["name"]) is str and type(row["sha256"]) is str and type(row["sizeBytes"]) is int and
            type(row["mvid"]) is str and type(row["fullName"]) is str and type(row["typeDefRows"]) is int and
            type(row["methodDefRows"]) is int and type(row["stringsHeapBytes"]) is int and
            MVID.fullmatch(row["mvid"]) is not None,
            "Wrong R01B overflow assembly schema")
    path = canonical_file(row["path"], "R01B overflow DLL")
    require(path.parent == receipt_path.parent and row["id"] == IMAGE_COUNT and
            row["name"] == "AssemblyShadow.WorkloadV2.I8192" and row["sizeBytes"] == 61440 and
            row["typeDefRows"] == 98 and row["methodDefRows"] == 98 and row["stringsHeapBytes"] > 4096 and
            HASH.fullmatch(row["sha256"]) and
            path.stat().st_size == row["sizeBytes"] and digest(path) == row["sha256"],
            "Invalid R01B overflow assembly")
    generator = value["generator"]
    require(type(generator) is dict and set(generator) == OVERFLOW_GENERATOR_FIELDS and
            all(type(generator[field]) is str for field in
                ("sourcePath", "sourceSha256", "launcherPath", "launcherSha256", "monoPath", "monoSha256",
                 "monoVersion", "compilerPath", "compilerSha256", "compilerVersion", "cecilPath", "cecilSha256")) and
            all(HASH.fullmatch(generator[field]) for field in
                ("sourceSha256", "launcherSha256", "monoSha256", "compilerSha256", "cecilSha256")) and
            type(generator["compileCommand"]) is list and type(generator["generateCommand"]) is list and
            len(generator["compileCommand"]) >= 5 and len(generator["generateCommand"]) == 3 and
            all(type(item) is str for item in generator["compileCommand"] + generator["generateCommand"]) and
            type(generator["inputHashesBefore"]) is dict and type(generator["inputHashesAfter"]) is dict and
            type(generator["inputsUnchanged"]) is bool and generator["inputsUnchanged"] is True,
            "Wrong R01B overflow generator schema")
    source = canonical_file(generator["sourcePath"], "R01B overflow generator source")
    launcher = canonical_file(generator["launcherPath"], "R01B overflow generator launcher")
    mono = canonical_file(generator["monoPath"], "R01B fixture Mono")
    compiler = canonical_file(generator["compilerPath"], "R01B fixture compiler")
    cecil = canonical_file(generator["cecilPath"], "R01B fixture Cecil")
    verification = value["verification"]
    require(type(verification) is dict and set(verification) == OVERFLOW_VERIFICATION_FIELDS and
            type(verification["identityReader"]) is str and type(verification["identityReaderSha256"]) is str and
            type(verification["typeTableReader"]) is str and type(verification["typeTableReaderSha256"]) is str and
            type(verification["distinctFromSupportedCorpus"]) is bool and
            type(verification["note"]) is str and verification["note"],
            "Wrong R01B overflow verification schema")
    identity_reader = canonical_file(verification["identityReader"], "R01B identity reader")
    type_reader = canonical_file(verification["typeTableReader"], "R01B type-table reader")
    require(generator["compileCommand"][0] == str(compiler) and
            generator["compileCommand"][1:3] == ["-nologo", "-target:exe"] and
            Path(generator["compileCommand"][-1]).is_absolute() and
            Path(generator["compileCommand"][-1]).name == source.name and
            sum(item.startswith("-out:") for item in generator["compileCommand"]) == 1 and
            Path(next(item[5:] for item in generator["compileCommand"] if item.startswith("-out:"))).is_absolute() and
            sum(item.startswith("-r:") for item in generator["compileCommand"]) == 1 and
            Path(next(item[3:] for item in generator["compileCommand"] if item.startswith("-r:"))).is_absolute() and
            Path(next(item[3:] for item in generator["compileCommand"] if item.startswith("-r:"))).name == cecil.name and
            generator["generateCommand"][0] == str(mono) and
            Path(generator["generateCommand"][1]).is_absolute() and
            generator["generateCommand"][-1] == str(path),
            "R01B overflow generator commands are not bound to their inputs")
    current_inputs = {str(item): digest(item) for item in
                      (source, launcher, identity_reader, type_reader, mono, compiler, cecil)}
    require(source == HERE / "r01b-overflow-fixture.cs" and launcher == HERE / "create-r01b-overflow-fixture.py" and
            identity_reader == HERE / "m04_metadata.py" and type_reader == HERE / "m05_types.py" and
            generator["sourceSha256"] == current_inputs[str(source)] and
            generator["launcherSha256"] == current_inputs[str(launcher)] and
            generator["monoSha256"] == current_inputs[str(mono)] and
            generator["compilerSha256"] == current_inputs[str(compiler)] and
            generator["cecilSha256"] == current_inputs[str(cecil)] and
            value["verification"]["identityReaderSha256"] == current_inputs[str(identity_reader)] and
            value["verification"]["typeTableReaderSha256"] == current_inputs[str(type_reader)] and
            generator["inputHashesBefore"] == current_inputs and generator["inputHashesAfter"] == current_inputs and
            generator["inputsUnchanged"] is True,
            "R01B overflow generator/reader inputs are not bound to stable current bytes")
    require(verification["distinctFromSupportedCorpus"] is True and
            verification["identityReaderSha256"] == current_inputs[str(identity_reader)] and
            verification["typeTableReaderSha256"] == current_inputs[str(type_reader)],
            "Overflow receipt does not assert its evidence boundary")
    if deep:
        identity = read_identity(path)
        tables = CliTables(path.read_bytes(), path)
        require(identity["name"] == row["name"] and identity["mvid"] == row["mvid"] and
                identity["fullName"] == row["fullName"] and tables.type_inventory()["assemblyName"] == row["name"] and
                tables.counts[2] == row["typeDefRows"] and tables.counts[6] == row["methodDefRows"] and
                len(tables.streams["#Strings"]) == row["stringsHeapBytes"],
                "R01B overflow independent PE/CLI verification differs")
    return value, path


def collect_direct_inputs(workload_manifest: Path, workload_files: list[Path], overflow_receipt: Path,
                          overflow_dll: Path, fixture_manifest: Path, on_build: Path, off_build: Path,
                          replay_receipt: Path, player_app: Path) -> set[Path]:
    files = {workload_manifest, overflow_receipt, overflow_dll, fixture_manifest, on_build, off_build, replay_receipt}
    files.update(workload_files)
    for path in player_app.rglob("*"):
        require(not path.is_symlink(), "Symlink in Player input tree: " + str(path))
        if path.is_file():
            files.add(path.resolve(strict=True))
    return files
