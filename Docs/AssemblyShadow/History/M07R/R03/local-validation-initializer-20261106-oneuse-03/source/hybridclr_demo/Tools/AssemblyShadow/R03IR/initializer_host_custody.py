#!/usr/bin/env python3
"""One-use initializer host custody: lossless regular bytes + link identities.

The real ten-component host runner intentionally retains adversarial directory
symlinks. Its raw output is a separate sibling tree. This module records every
regular file's byte digest and every symlink's *literal* target without
traversing any link, creates a regular-member-only digest-verified archive,
and binds that archive into the ordinary strict product seal.

Never change R03/batch_evidence.py: its symlink refusal is intentional.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tarfile

KIND = "R03InitializerNativeHostCustodyV1"
MAX_ENTRIES = 30000
MAX_CONTENT_BYTES = 4 * 1024**3


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest_stream(stream):
    hashed = hashlib.sha256()
    while True:
        b = stream.read(1024 * 1024)
        if not b:
            break
        hashed.update(b)
    return hashed.hexdigest()


def file_digest(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        st = os.fstat(fd)
        require(stat.S_ISREG(st.st_mode), "Regular nofollow file required")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return digest_stream(stream), st.st_size
    finally:
        os.close(fd)


def safe_name(relative):
    parts = PurePosixPath(relative).parts
    require(parts and not any(p in ("", ".", "..") for p in parts)
            and relative == "/".join(parts) and not relative.startswith("/"),
            "Invalid host evidence path")
    return relative


def inventory(root):
    root = Path(root)
    require(root.is_absolute() and root.is_dir() and not root.is_symlink() and
            root.resolve(strict=True) == root,
            "Canonical exact real host output root required")
    rows = []
    total = 0
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        here = Path(current)
        preserved = []
        for name in sorted(dirs):
            path = here / name
            rel = safe_name(path.relative_to(root).as_posix())
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                rows.append({"path": rel, "kind": "symlink", "target": os.readlink(path)})
            else:
                require(stat.S_ISDIR(mode), "Unexpected non-directory node: " + rel)
                rows.append({"path": rel, "kind": "directory"})
                preserved.append(name)
        dirs[:] = preserved
        for name in sorted(files):
            path = here / name
            rel = safe_name(path.relative_to(root).as_posix())
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                rows.append({"path": rel, "kind": "symlink", "target": os.readlink(path)})
            else:
                require(stat.S_ISREG(mode), "Unexpected non-regular host node: " + rel)
                hexdigest, size = file_digest(path)
                rows.append({"path": rel, "kind": "file", "sha256": hexdigest, "size": size})
                total += size
            require(len(rows) <= MAX_ENTRIES and total <= MAX_CONTENT_BYTES,
                    "Bounded host custody inventory limit")
    rows.sort(key=lambda x: x["path"])
    require(len(rows) == len({r["path"] for r in rows}),
            "Duplicate host custody paths")
    links = [r for r in rows if r["kind"] == "symlink"]
    files = [r for r in rows if r["kind"] == "file"]
    require(files and links, "Actual host regular files and adversarial links required")
    return {"schemaVersion": 1, "kind": KIND,
            "rawHostPath": str(root),
            "entries": rows,
            "fileCount": len(files),
            "symlinkCount": len(links),
            "directoryCount": sum(r["kind"] == "directory" for r in rows),
            "regularBytes": total,
            "symlinksFollowed": False,
            "runtimeAcceptance": False,
            "R03Accepted": False, "H2Passed": False}


def write_exclusive(path, content):
    with Path(path).open("xb") as stream:
        stream.write(content)


def verify_archive(archive, rows, manifest_data):
    expected = {r["path"]: r for r in rows if r["kind"] == "file"}
    expected["HOST_MANIFEST.json"] = {
        "size": len(manifest_data),
        "sha256": hashlib.sha256(manifest_data).hexdigest()}
    with tarfile.open(archive, "r:gz") as data:
        members = data.getmembers()
        require(len(members) == len(expected) and
                {m.name for m in members} == set(expected),
                "Exact host archive member identity")
        for member in members:
            entry = expected[member.name]
            require(member.isfile() and member.size == entry["size"],
                    "Host archive must contain only correctly sized regular members")
            fp = data.extractfile(member)
            require(fp is not None and digest_stream(fp) == entry["sha256"],
                    "Full host archive payload integrity")
    return len(expected)


def capture(root, target):
    root, target = Path(root), Path(target)
    require(target.is_absolute() and not target.exists() and
            target.parent.is_dir() and not target.parent.is_symlink() and
            not target.is_relative_to(root) and not root.is_relative_to(target),
            "Fresh external-to-host, internal-to-batch custody directory required")
    record = inventory(root)
    target.mkdir(mode=0o700)
    manifest_data = (json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True)
                     + "\n").encode("utf-8")
    manifest = target / "HOST_MANIFEST.json"
    archive = target / "HOST_REGULAR_BYTES.tar.gz"
    write_exclusive(manifest, manifest_data)
    with tarfile.open(archive, "x:gz") as out:
        for entry in record["entries"]:
            if entry["kind"] != "file":
                continue
            path = root / entry["path"]
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                st = os.fstat(fd)
                require(stat.S_ISREG(st.st_mode) and st.st_size == entry["size"],
                        "Host file mutated during capture")
                info = tarfile.TarInfo(entry["path"])
                info.size, info.mode, info.mtime = st.st_size, 0o600, 0
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    out.addfile(info, stream)
                require(file_digest(path) == (entry["sha256"], entry["size"]),
                        "Host file changed while archived")
            finally:
                os.close(fd)
        blob = tarfile.TarInfo("HOST_MANIFEST.json")
        blob.size, blob.mode, blob.mtime = len(manifest_data), 0o600, 0
        out.addfile(blob, io.BytesIO(manifest_data))
    verified = verify_archive(archive, record["entries"], manifest_data)
    require(inventory(root) == record, "Raw host source changed during archive")
    report = {
        "schemaVersion": 1, "kind": "R03InitializerNativeHostCustodyReceiptV1",
        "result": "PassedFullRegularBytesAndLiteralSymlinkTargets",
        "rawHostPath": str(root),
        "manifestSha256": hashlib.sha256(manifest_data).hexdigest(),
        "archiveSha256": file_digest(archive)[0],
        "archivedRegularMembersIncludingManifest": verified,
        "fileCount": record["fileCount"],
        "directoryCount": record["directoryCount"],
        "symlinkCount": record["symlinkCount"],
        "regularBytes": record["regularBytes"],
        "rawHostPreservedOutsideProductSeal": True,
        "symlinksFollowed": False,
        "runtimeAcceptance": False, "R03Accepted": False, "H2Passed": False,
    }
    write_exclusive(target / "HOST_CUSTODY_RESULT.json",
                    (json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    return report


def verify_live(root, target):
    root, target = Path(root), Path(target)
    manifest = target / "HOST_MANIFEST.json"
    archive = target / "HOST_REGULAR_BYTES.tar.gz"
    receipt = target / "HOST_CUSTODY_RESULT.json"
    for path in (manifest, archive, receipt):
        require(path.is_file() and not path.is_symlink(), "Host custody artifacts missing")
    expected = json.loads(manifest.read_bytes())
    current = inventory(root)
    require(current == expected, "Retained host raw bytes or link identities drifted")
    observed = json.loads(receipt.read_bytes())
    require(observed["kind"] == "R03InitializerNativeHostCustodyReceiptV1" and
            observed["result"] == "PassedFullRegularBytesAndLiteralSymlinkTargets" and
            observed["manifestSha256"] == file_digest(manifest)[0] and
            observed["archiveSha256"] == file_digest(archive)[0] and
            observed["symlinkCount"] == current["symlinkCount"] and
            observed["fileCount"] == current["fileCount"] and
            observed["rawHostPath"] == str(root) and
            observed["runtimeAcceptance"] is False,
            "Immutable source-bound raw host custody receipt required")
    verify_archive(archive, current["entries"], manifest.read_bytes())
    return {"result": "PassedFullRawHostAndArchiveBinding_NoRuntimeAcceptance",
            "hostReceiptSha256": file_digest(receipt)[0],
            "symlinkCount": current["symlinkCount"],
            "regularFiles": current["fileCount"],
            "runtimeAcceptance": False, "R03Accepted": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw-host", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(capture(args.raw_host, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
