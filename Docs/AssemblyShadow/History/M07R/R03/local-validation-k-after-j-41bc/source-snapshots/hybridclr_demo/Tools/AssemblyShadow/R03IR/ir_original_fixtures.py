"""R03 IR immutable S fixture authentication, independent of regenerated PE bytes.

The historical S inventory + all 15 DLLs are stored as real Git blobs. This
module copies those *exact* published bytes to a fresh IR-only output root.
No executable, generator, archive, S input or historical result is modified.
"""
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess

S_PUBLICATION = "fc55d8b8ce1738fda465c06cd97dc2a8f95ce34b"
S_RELATIVE_ROOT = ("Docs/AssemblyShadow/History/M07R/R03/"
    "local-validation-20261007-batch-s-evidence-ready/batch/host/player-fixtures")
S_INVENTORY_BLOB = "0688bd2dad054bd59fcdd1564a050a398cfa14e7"
EXPECTED_COUNT = 15


def assert_fact(ok, message):
    if not ok:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args],
                                   stderr=subprocess.PIPE, text=True).strip()


def check_path(name):
    assert_fact(isinstance(name, str) and
                re.fullmatch(r"(?:baseline|private-reference|virtual-slot|reversal|true-cycle|primitive|interface|value|removal)/[A-Za-z][A-Za-z0-9]*\.dll", name) is not None and
                str(PurePosixPath(name)) == name, "Noncanonical S fixture file name")
    return name


def validate_inventory(value):
    assert_fact(isinstance(value, dict) and
                value.get("kind") == "R03PlayerFixtureInventory" and
                type(value.get("schemaVersion")) is int and value["schemaVersion"] == 1 and
                value.get("nativeExecution") is False and
                value.get("runtimeAcceptance") is False,
                "Original S fixture inventory schema")
    rows = value.get("files")
    assert_fact(type(rows) is list and len(rows) == EXPECTED_COUNT,
                "Exactly fifteen S fixture identities required")
    by_name = {}
    for row in rows:
        assert_fact(type(row) is dict and
                    {"path", "assembly", "mvid", "size", "sha256", "references"} == set(row),
                    "Complete S inventory row")
        name = check_path(row["path"])
        assert_fact(name not in by_name and type(row["size"]) is int and row["size"] > 0 and
                    isinstance(row["assembly"], str) and
                    isinstance(row["mvid"], str) and
                    re.fullmatch("[0-9a-f]{64}", row["sha256"]) is not None and
                    type(row["references"]) is list and
                    all(isinstance(v, str) for v in row["references"]),
                    "Invalid/duplicate S fixture inventory entry")
        by_name[name] = row
    assert_fact("baseline/Methods.dll" in by_name and
                "virtual-slot/Methods.dll" in by_name,
                "Expected original Methods baseline and target")
    return by_name


def stage_immutable_original_s(demo, output, file_sha256):
    """Verify exact 2026 S Git blob identity and copy to new external output."""
    demo, output = Path(demo).resolve(), Path(output).resolve()
    assert_fact(demo.is_dir() and demo.name == "hybridclr_demo" and
                output != demo and not output.is_relative_to(demo) and
                not output.exists(), "Unused external fixture output required")
    assert_fact(git(demo, "rev-parse", "--show-toplevel") == str(demo),
                "Owning demo checkout identity")
    assert_fact(git(demo, "merge-base", "--is-ancestor", S_PUBLICATION,
                    "HEAD") == "", "Original S must be an ancestor")
    source_root = demo / S_RELATIVE_ROOT
    rel_inventory = S_RELATIVE_ROOT + "/inventory.json"
    original_blob = git(demo, "rev-parse", S_PUBLICATION + ":" + rel_inventory)
    current_blob = git(demo, "rev-parse", "HEAD:" + rel_inventory)
    assert_fact(original_blob == current_blob == S_INVENTORY_BLOB,
                "Original S inventory Git blob changed")
    inventory_path = source_root / "inventory.json"
    assert_fact(inventory_path.is_file() and not inventory_path.is_symlink() and
                git(demo, "hash-object", str(inventory_path)) == original_blob,
                "Working original S inventory changed")
    from batch_contract import loads  # existing strict duplicate/NaN JSON parser
    inventory = loads(inventory_path.read_text(encoding="utf-8"))
    entries = validate_inventory(inventory)
    observed = []
    for name, row in sorted(entries.items()):
        relative = S_RELATIVE_ROOT + "/" + name
        before = git(demo, "rev-parse", S_PUBLICATION + ":" + relative)
        now = git(demo, "rev-parse", "HEAD:" + relative)
        f = source_root / name
        assert_fact(before == now and f.is_file() and not f.is_symlink() and
                    git(demo, "hash-object", str(f)) == before and
                    f.stat().st_size == row["size"] and
                    file_sha256(f) == row["sha256"],
                    "Original S tracked fixture byte mismatch: " + name)
        observed.append({"path": name, "gitBlob": before, "sha256": row["sha256"],
                         "mvid": row["mvid"], "size": row["size"],
                         "assembly": row["assembly"], "references": row["references"]})
    # Only create output after the entire source has been authenticated. No
    # history cleanup, in-place reserialization or re-generation is permitted.
    output.mkdir(parents=True)
    shutil.copyfile(inventory_path, output / "inventory.json")
    assert_fact(file_sha256(output / "inventory.json") == file_sha256(inventory_path),
                "Original S fixture inventory copy")
    for row in observed:
        dest = output / row["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / row["path"], dest)
        assert_fact(file_sha256(dest) == row["sha256"] and
                    dest.stat().st_size == row["size"],
                    "Copied S fixture hash mismatch: " + row["path"])
    authority = {"kind": "R03IRImmutableSFixtureAuthority", "schemaVersion": 1,
                 "result": "AuthenticatedCopied", "originalCommit": S_PUBLICATION,
                 "originalInventoryGitBlob": S_INVENTORY_BLOB,
                 "sourceDemoCommit": git(demo, "rev-parse", "HEAD"),
                 "files": observed, "originalFixtureCount": EXPECTED_COUNT,
                 "fixtureBytesRegenerated": False, "historicalInputsModified": False,
                 "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False}
    receipt = output.parent / "ir-original-s-fixture-authority.json"
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(authority, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return entries, receipt
