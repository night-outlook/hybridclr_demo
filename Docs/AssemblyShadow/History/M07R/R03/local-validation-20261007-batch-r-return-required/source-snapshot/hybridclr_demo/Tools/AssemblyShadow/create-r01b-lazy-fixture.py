#!/usr/bin/env python3
"""Generate and independently verify the bounded R01B lazy-path fixture."""
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
from shadow_tools import require


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "r01b-lazy-fixture.cs"
LAUNCHER = Path(__file__).resolve()
IDENTITY_READER = HERE / "m04_metadata.py"
MONO_ROOT = Path("/Applications/Unity/Hub/Editor/2022.3.62f2/Unity.app/Contents/MonoBleedingEdge")
MONO = MONO_ROOT / "bin/mono"
MCS = MONO_ROOT / "bin/mcs"
CECIL = MONO_ROOT / "lib/mono/net_4_x-macos/Mono.Cecil.dll"
NAME = "AssemblyShadow.R01BLazyFixture"
VERSION = "1.0.0.1"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def version(path: Path, *arguments: str) -> str:
    run = subprocess.run([str(path), *arguments], check=True, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return run.stdout.replace("\x00", "").strip()


def input_hashes() -> dict[str, str]:
    return {str(path): digest(path) for path in
            (SOURCE, LAUNCHER, IDENTITY_READER, MONO, MCS, CECIL)}


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
    hashes_before = input_hashes()
    source_bytes = SOURCE.read_bytes()
    cecil_bytes = CECIL.read_bytes()
    require(hashlib.sha256(source_bytes).hexdigest() == hashes_before[str(SOURCE)] and
            hashlib.sha256(cecil_bytes).hexdigest() == hashes_before[str(CECIL)],
            "generator inputs changed while being captured")

    compile_command = None
    generate_commands = []
    with tempfile.TemporaryDirectory(prefix="r01b-lazy-fixture-", dir=str(output)) as temporary:
        temporary_root = Path(temporary)
        binary = temporary_root / "r01b-lazy-fixture-generator.exe"
        source_snapshot = temporary_root / SOURCE.name
        cecil_snapshot = temporary_root / CECIL.name
        source_snapshot.write_bytes(source_bytes)
        cecil_snapshot.write_bytes(cecil_bytes)
        compile_command = [str(MCS), "-nologo", "-target:exe", "-out:" + str(binary),
                           "-r:" + str(cecil_snapshot), str(source_snapshot)]
        subprocess.run(compile_command, check=True)

        generated = []
        for index in (1, 2):
            path = temporary_root / ("lazy-" + str(index) + ".dll")
            command = [str(MONO), str(binary), str(path)]
            subprocess.run(command, check=True)
            generated.append(path)
            generate_commands.append(command)

        first_hash, second_hash = digest(generated[0]), digest(generated[1])
        first_identity = read_identity(generated[0])
        second_identity = read_identity(generated[1])
        first_pe_identity = {key: value for key, value in first_identity.items() if key not in ("path", "sha256")}
        second_pe_identity = {key: value for key, value in second_identity.items() if key not in ("path", "sha256")}
        require(first_hash == second_hash and first_pe_identity == second_pe_identity,
                "two fresh generator runs did not produce identical bytes and PE identity")
        require(first_identity["name"] == NAME and first_identity["version"] == VERSION,
                "generated lazy fixture has the wrong PE identity")

        final_dll = output / (NAME + ".dll")
        shutil.copyfile(generated[0], final_dll)

    hashes_after = input_hashes()
    final_identity = read_identity(final_dll)
    final_hash = digest(final_dll)
    final_pe_identity = {key: value for key, value in final_identity.items() if key not in ("path", "sha256")}
    require(final_hash == first_hash and final_pe_identity == first_pe_identity,
            "published fixture differs from the independently verified generation")
    if hashes_after != hashes_before:
        failure = {
            "schemaVersion": 1,
            "kind": "R01BLazyFixtureFailureReceipt",
            "milestone": "R01B",
            "result": "FailedInputDrift",
            "inputHashesBefore": hashes_before,
            "inputHashesAfter": hashes_after,
            "inputsUnchanged": False,
        }
        with (output / "r01b-lazy-fixture-failure.json").open("x", encoding="utf-8") as stream:
            json.dump(failure, stream, indent=2)
            stream.write("\n")
        raise RuntimeError("generator inputs changed during execution")

    receipt = {
        "schemaVersion": 1,
        "kind": "R01BLazyFixtureReceipt",
        "milestone": "R01B",
        "result": "Passed",
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "assembly": {
            "name": final_identity["name"],
            "version": final_identity["version"],
            "path": str(final_dll),
            "sha256": final_hash,
            "mvid": final_identity["mvid"],
            "fullName": final_identity["fullName"],
            "sizeBytes": final_dll.stat().st_size,
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
            "generateCommands": generate_commands,
            "inputHashesBefore": hashes_before,
            "inputHashesAfter": hashes_after,
            "inputsUnchanged": True,
            "reproducibleTwoRunSha256": True,
        },
        "verification": {
            "identityReader": str(IDENTITY_READER),
            "identityReaderSha256": hashes_before[str(IDENTITY_READER)],
            "independentPeIdentity": True,
            "note": "This standalone fixture is loaded after publication by the R01B lazy Player probe; it is outside the 8,192-DLL envelope.",
        },
    }
    receipt_path = output / "r01b-lazy-fixture-receipt.json"
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"result": "Passed", "dll": str(final_dll), "sha256": final_hash,
                      "mvid": final_identity["mvid"], "sizeBytes": final_dll.stat().st_size}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
