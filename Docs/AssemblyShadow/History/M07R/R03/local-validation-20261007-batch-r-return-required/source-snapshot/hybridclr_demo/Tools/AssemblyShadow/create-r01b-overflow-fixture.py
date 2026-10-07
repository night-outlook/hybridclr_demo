#!/usr/bin/env python3
"""Create and independently verify the distinct R01B 8,193rd DLL fixture."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from m04_metadata import read_identity
from m05_types import CliTables
from shadow_tools import require


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "r01b-overflow-fixture.cs"
LAUNCHER = Path(__file__).resolve()
IDENTITY_READER = HERE / "m04_metadata.py"
TYPE_READER = HERE / "m05_types.py"
MONO_ROOT = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge")
MONO = MONO_ROOT / "bin/mono"
MCS = MONO_ROOT / "bin/mcs"
CECIL = MONO_ROOT / "lib/mono/net_4_x-macos/Mono.Cecil.dll"
NAME = "AssemblyShadow.WorkloadV2.I8192"
SIZE_BYTES = 61440


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def version(path: Path, *arguments: str) -> str:
    run = subprocess.run([str(path), *arguments], check=True, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return run.stdout.replace("\x00", "").strip()


def input_hashes() -> dict[str, str]:
    return {str(path): digest(path) for path in (SOURCE, LAUNCHER, IDENTITY_READER, TYPE_READER, MONO, MCS, CECIL)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and not output.is_symlink(),
            "output root must be a new canonical absolute path")
    require(output.parent.is_dir() and not output.parent.is_symlink(),
            "output root parent must be an existing canonical directory")
    require(SOURCE.is_file() and not SOURCE.is_symlink() and
            all(path.is_file() and not path.is_symlink() for path in (MONO, MCS, CECIL)),
            "pinned Unity Mono/Cecil toolchain is unavailable")
    output.mkdir()

    dll = output / (NAME + ".dll")
    receipt_path = output / "r01b-overflow-fixture-receipt.json"
    hashes_before = input_hashes()
    source_bytes = SOURCE.read_bytes()
    cecil_bytes = CECIL.read_bytes()
    require(hashlib.sha256(source_bytes).hexdigest() == hashes_before[str(SOURCE)] and
            hashlib.sha256(cecil_bytes).hexdigest() == hashes_before[str(CECIL)],
            "generator inputs changed while being captured")
    with tempfile.TemporaryDirectory(prefix="r01b-overflow-") as temporary:
        binary = Path(temporary) / "r01b-overflow-fixture.exe"
        source_snapshot = Path(temporary) / SOURCE.name
        cecil_snapshot = Path(temporary) / CECIL.name
        source_snapshot.write_bytes(source_bytes)
        cecil_snapshot.write_bytes(cecil_bytes)
        compile_command = [str(MCS), "-nologo", "-target:exe", "-out:" + str(binary),
                           "-r:" + str(cecil_snapshot), str(source_snapshot)]
        subprocess.run(compile_command, check=True)
        generate_command = [str(MONO), str(binary), str(dll)]
        subprocess.run(generate_command, check=True)

    hashes_after = input_hashes()
    if hashes_after != hashes_before:
        failure = {
            "schemaVersion": 1,
            "kind": "R01BOverflowFixtureFailureReceipt",
            "milestone": "R01B",
            "result": "FailedInputDrift",
            "inputHashesBefore": hashes_before,
            "inputHashesAfter": hashes_after,
            "inputsUnchanged": False,
        }
        with (output / "r01b-overflow-fixture-failure.json").open("x", encoding="utf-8") as stream:
            json.dump(failure, stream, indent=2)
            stream.write("\n")
        raise RuntimeError("generator or verification inputs changed during execution")

    identity = read_identity(dll)
    data = dll.read_bytes()
    tables = CliTables(data, dll)
    inventory = tables.type_inventory()
    require(identity["name"] == NAME and identity["version"] == "1.0.0.8192",
            "generated overflow assembly has the wrong identity")
    require(len(data) == SIZE_BYTES and inventory["assemblyName"] == NAME,
            "generated overflow assembly has the wrong size or table identity")
    require(tables.counts[2] == 98 and tables.counts[6] == 98 and len(tables.streams["#Strings"]) > 4096,
            "overflow fixture does not preserve the dense metadata shape")
    receipt = {
        "schemaVersion": 1,
        "kind": "R01BOverflowFixtureReceipt",
        "milestone": "R01B",
        "result": "Passed",
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "assembly": {
            "id": 8192,
            "name": NAME,
            "path": str(dll),
            "sha256": digest(dll),
            "sizeBytes": len(data),
            "mvid": identity["mvid"],
            "fullName": identity["fullName"],
            "typeDefRows": tables.counts[2],
            "methodDefRows": tables.counts[6],
            "stringsHeapBytes": len(tables.streams["#Strings"]),
        },
        "generator": {
            "sourcePath": str(SOURCE),
            "sourceSha256": hashes_before[str(SOURCE)],
            "launcherPath": str(LAUNCHER),
            "launcherSha256": hashes_before[str(LAUNCHER)],
            "monoPath": str(MONO),
            "monoSha256": hashes_before[str(MONO)],
            "monoVersion": version(MONO, "--version").splitlines()[0],
            "compilerPath": str(MCS),
            "compilerSha256": hashes_before[str(MCS)],
            "compilerVersion": version(MCS, "--version"),
            "cecilPath": str(CECIL),
            "cecilSha256": hashes_before[str(CECIL)],
            "compileCommand": compile_command,
            "generateCommand": generate_command,
            "inputHashesBefore": hashes_before,
            "inputHashesAfter": hashes_after,
            "inputsUnchanged": True,
        },
        "verification": {
            "identityReader": str(IDENTITY_READER),
            "identityReaderSha256": hashes_before[str(IDENTITY_READER)],
            "typeTableReader": str(TYPE_READER),
            "typeTableReaderSha256": hashes_before[str(TYPE_READER)],
            "distinctFromSupportedCorpus": True,
            "note": "This fixture is outside the 8,192-item/512-MiB supported corpus and is used only to prove exact limit rejection.",
        },
    }
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"result": "Passed", "dll": str(dll), "sha256": receipt["assembly"]["sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
