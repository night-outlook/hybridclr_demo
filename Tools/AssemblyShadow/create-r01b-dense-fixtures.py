#!/usr/bin/env python3
"""Generate a new deterministic R01B dense-fixture contract and verify it independently."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from m04_metadata import read_identity
from m05_types import CliTables
from shadow_tools import require

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "r01b-dense-fixture.cs"
LAUNCHER = Path(__file__).resolve()
IDENTITY_READER = HERE / "m04_metadata.py"
TABLE_READER = HERE / "m05_types.py"
MONO_ROOT = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge")
MONO = MONO_ROOT / "bin/mono"
MCS = MONO_ROOT / "bin/mcs"
CECIL = MONO_ROOT / "lib/mono/net_4_x-macos/Mono.Cecil.dll"
TARGET_BYTES = 1024 * 1024
TYPEDEF_ROWS = 4098
METHODDEF_ROWS = 4097
HISTORICAL = {
    1: "14f1fb323db1f1c1ca34840de5ef14eb3434c31e9e1608813ff4c1e398fd1273",
    2: "e5c88e875c43575b2a3087e466c745b9f8f57366d1247fc469820d53ef295bcf",
}

def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def version(path: Path, *arguments: str) -> str:
    run = subprocess.run([str(path), *arguments], check=True, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return run.stdout.replace("\x00", "").strip()

def input_hashes() -> dict[str, str]:
    return {str(path): digest(path) for path in
            (SOURCE, LAUNCHER, IDENTITY_READER, TABLE_READER, MONO, MCS, CECIL)}

def inspect(path: Path, fixture_id: int) -> dict:
    data = path.read_bytes()
    identity = read_identity(path)
    tables = CliTables(data, path)
    expected_name = f"AssemblyShadow.Workload.I{fixture_id:04d}"
    require(path.stat().st_size == TARGET_BYTES, f"{path}: dense fixture is not exactly 1 MiB")
    require(identity["name"] == expected_name, f"{path}: dense assembly identity differs")
    require(tables.counts[2] == TYPEDEF_ROWS and tables.counts[6] == METHODDEF_ROWS,
            f"{path}: dense TypeDef/MethodDef counts differ")
    require(len(tables.streams["#Strings"]) > 65535, f"{path}: strings heap did not cross the 16-bit boundary")
    require(sum(tables.widths[2]) >= 18 and sum(tables.widths[6]) >= 16,
            f"{path}: dense table widths did not exercise 4-byte heap indexes")
    inventory = tables.type_inventory()
    require(len(inventory["types"]) == TYPEDEF_ROWS - 1, f"{path}: dense type inventory count differs")
    sample = (0, 4093, 4094, 4095, 4096)
    for index in sample:
        require(inventory["types"][index]["name"] ==
                f"DenseType_{fixture_id:04d}_{index:04d}_MetadataBoundary_0123456789abcdef0123456789abcdef",
                f"{path}: dense type sample differs at {index}")
    return {
        "id": fixture_id,
        "name": expected_name,
        "file": path.name,
        "path": str(path),
        "sha256": digest(path),
        "sizeBytes": path.stat().st_size,
        "mvid": identity["mvid"],
        "fullName": identity["fullName"],
        "typeDefRows": tables.counts[2],
        "methodDefRows": tables.counts[6],
        "stringsHeapBytes": len(tables.streams["#Strings"]),
        "typeDefRowBytes": sum(tables.widths[2]),
        "methodDefRowBytes": sum(tables.widths[6]),
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_root
    require(output.is_absolute() and output == output.resolve() and not output.exists() and
            output.parent.is_dir() and not output.is_symlink(),
            "output root must be a new canonical absolute path")
    require(SOURCE.is_file() and not SOURCE.is_symlink() and
            all(path.is_file() and not path.is_symlink() for path in (MONO, MCS, CECIL)),
            "pinned Unity Mono/Cecil toolchain is unavailable")

    output.mkdir()
    fixture_root = output / "fixtures"
    fixture_root.mkdir()
    hashes_before = input_hashes()
    compile_command = None
    generate_commands = []
    fixtures = []

    with tempfile.TemporaryDirectory(prefix="r01b-dense-v2-", dir=str(output)) as temporary:
        temp = Path(temporary)
        binary = temp / "r01b-dense-fixture-generator.exe"
        source_snapshot = temp / SOURCE.name
        cecil_snapshot = temp / CECIL.name
        source_snapshot.write_bytes(SOURCE.read_bytes())
        cecil_snapshot.write_bytes(CECIL.read_bytes())
        compile_command = [str(MCS), "-nologo", "-target:exe", "-out:" + str(binary),
                           "-r:" + str(cecil_snapshot), str(source_snapshot)]
        subprocess.run(compile_command, check=True)

        for fixture_id in (1, 2):
            runs = []
            for run_index in (1, 2):
                path = temp / f"I{fixture_id:04d}-run{run_index}.dll"
                command = [str(MONO), str(binary), str(fixture_id), str(path)]
                subprocess.run(command, check=True)
                generate_commands.append(command)
                runs.append(path)
            require(digest(runs[0]) == digest(runs[1]) and runs[0].read_bytes() == runs[1].read_bytes(),
                    f"dense fixture {fixture_id} is not byte-reproducible across two fresh runs")
            destination = fixture_root / f"AssemblyShadow.Workload.I{fixture_id:04d}.dll"
            shutil.copyfile(runs[0], destination)
            fixtures.append(inspect(destination, fixture_id))

    hashes_after = input_hashes()
    require(hashes_after == hashes_before, "dense generator inputs changed during execution")

    manifest = {
        "schemaVersion": 2,
        "kind": "R01BDenseAdjunctManifest",
        "status": "GeneratedDeterministicDenseV2",
        "evidenceIdentity": "replacement-fixtures-require-fresh-native-and-player-evidence",
        "historicalEvidenceReused": False,
        "fixtures": fixtures,
        "shapeContract": {
            "fixtureCount": 2,
            "sizeBytesEach": TARGET_BYTES,
            "typeDefRows": TYPEDEF_ROWS,
            "methodDefRows": METHODDEF_ROWS,
            "stringsHeapMinimumBytes": 65536,
            "purpose": "exercise RawImage 4-byte heap-index table widths around the 4095/4096 metadata boundary",
        },
        "historicalSealedV1": [
            {"id": fixture_id, "sha256": HISTORICAL[fixture_id], "status": "UnavailableDoNotRelabel"}
            for fixture_id in (1, 2)
        ],
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
            "generateCommands": generate_commands,
            "inputsUnchanged": True,
            "twoFreshRunsByteIdentical": True,
        },
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    manifest_path = output / "workload-v3-dense-adjunct-v2.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "Passed", "manifest": str(manifest_path),
                      "fixtures": [{"id": row["id"], "sha256": row["sha256"]} for row in fixtures]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
