#!/usr/bin/env python3
"""Inventory and seal all fresh count evidence before M08."""

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tarfile
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def save_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def inventory(parent, members, output):
    rows = []
    for member in members:
        root = parent / member
        assert root.exists() and root == root.resolve() and not root.is_symlink(), root
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            mode = path.lstat().st_mode
            if stat.S_ISDIR(mode):
                continue
            assert stat.S_ISREG(mode), f"nonregular evidence member: {path}"
            rows.append({"path": path.relative_to(parent).as_posix(),
                         "sizeBytes": path.stat().st_size, "sha256": digest(path)})
    assert len({row["path"] for row in rows}) == len(rows)
    save_new(output, {"kind": "H1CountEvidenceRegularFileInventory",
                      "parent": str(parent), "members": members,
                      "regularFileCount": len(rows), "files": rows})
    return {row["path"]: row for row in rows}


def seal(label, parent, members, output, archive_dir):
    inv_path = output / "inventories" / (label + ".json")
    rows = inventory(parent, members, inv_path)
    archive = archive_dir / (label + ".tar.gz")
    assert not archive.exists(), archive
    command = ["/usr/bin/tar", "-czf", str(archive), "-C", str(parent), *members]
    env = dict(os.environ, COPYFILE_DISABLE="1")
    subprocess.run(command, env=env, check=True)
    seen = {}
    names = []
    with tarfile.open(archive, "r:gz") as stream:
        for member in stream:
            name = member.name.rstrip("/")
            names.append(name)
            assert not Path(name).name.startswith("._"), f"AppleDouble member: {name}"
            assert not name.startswith("/") and ".." not in Path(name).parts
            if member.isdir():
                continue
            assert member.isfile(), f"nonregular archive member: {name}"
            assert name in rows and name not in seen, f"unexpected/duplicate archive file: {name}"
            value = hashlib.sha256()
            source = stream.extractfile(member)
            assert source is not None
            for block in iter(lambda: source.read(1024 * 1024), b""):
                value.update(block)
            assert value.hexdigest() == rows[name]["sha256"] and member.size == rows[name]["sizeBytes"], name
            seen[name] = True
    assert set(seen) == set(rows), f"missing archive files in {label}"
    return {"label": label, "originalParent": str(parent), "originalMembers": members,
            "archivePath": str(archive), "archiveSha256": digest(archive),
            "archiveSizeBytes": archive.stat().st_size,
            "archiveMemberCount": len(names),
            "archiveMemberNamesSha256": hashlib.sha256("\n".join(names).encode()).hexdigest(),
            "regularFileCount": len(rows), "inventoryPath": str(inv_path),
            "inventorySha256": digest(inv_path), "appleDoubleMembers": 0,
            "archiveContentsMatchInventory": True, "command": command,
            "copyfileDisable": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--selected-builds", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run = args.run_root.resolve(strict=True)
    out = args.output.resolve(strict=True)
    archives = run / "archives"
    archives.mkdir(exist_ok=False)
    (out / "inventories").mkdir(exist_ok=False)
    selected = json.loads(args.selected_builds.read_text())["builds"]
    plans = [
        ("fixtures", run, ["fixtures-parameters", "fixtures-nested"]),
        ("matrix", run, ["matrix", "matrix-verification.json"]),
        ("build-batch", run, ["builds"]),
    ]
    for key in ("on-Debug", "on-Release", "off-Debug", "off-Release"):
        build_root = Path(selected[key]["buildRoot"]).resolve(strict=True)
        plans.append(("candidate-" + key.lower(), build_root.parent, [build_root.name]))
    records = []
    for label, parent, members in plans:
        row = seal(label, parent, members, out, archives)
        records.append(row)
        print(label, row["regularFileCount"], row["archiveSizeBytes"], flush=True)
    save_new(out / "seal-index.json",
             {"kind": "H1FreshCountEvidenceSealIndex", "status": "Passed",
              "runRoot": str(run), "requiredArchiveCount": 6,
              "actualArchiveCount": len(records), "archives": records,
              "allArchiveContentsMatchInventories": True,
              "allAppleDoubleMemberCountsZero": True,
              "liveRootsPreserved": True})


if __name__ == "__main__":
    main()
