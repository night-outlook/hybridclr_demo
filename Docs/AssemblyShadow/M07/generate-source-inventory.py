#!/usr/bin/env python3
"""Generate the exact committed M06-to-M07 executable source inventory."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


REPOSITORIES = (
    (
        "hybridclr",
        Path("/Users/ah/GitHub/hybridclr/hybridclr"),
        "a19db144751f4f016769b90e61a80b8c27578678",
        "a19db144751f4f016769b90e61a80b8c27578678",
    ),
    (
        "il2cpp_plus",
        Path("/Users/ah/GitHub/hybridclr/il2cpp_plus"),
        "5b12ee96e574999d0eb82a6200d95a5b63c7fcfc",
        "666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8",
    ),
    (
        "hybridclr_unity",
        Path("/Users/ah/GitHub/hybridclr/hybridclr_unity"),
        "8d2e811fb37f4427ea15321369c883a61975a57d",
        "2180b99daf39095cd76301da2bdf34ac945ee8b4",
    ),
    (
        "demo",
        Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow_m07"),
        "577baf6d4ad295774e5a2397a4f73040d4f6f846",
        "3aab779a3304dd9785ab14fb5fcdc73a107066f7",
    ),
)
DEMO_PIN_REVISION = "671737c082effa5094bed16b087f6da5c3c666c9"


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def run(repository: Path, *arguments: str) -> bytes:
    return subprocess.check_output(
        ["git", *arguments], cwd=repository, env={**os.environ, "LC_ALL": "C"}
    )


def commit(repository: Path, revision: str) -> str:
    return run(repository, "rev-parse", "--verify", revision + "^{commit}").decode().strip()


def delta(repository: Path, base: str, target: str) -> tuple[list[dict], dict]:
    base = commit(repository, base)
    target = commit(repository, target)
    require(
        run(repository, "merge-base", "--is-ancestor", base, target) == b"",
        f"{base} is not an ancestor of {target} in {repository}",
    )
    fields = run(
        repository, "diff", "--name-status", "--no-renames", "-z", base + ".." + target
    ).split(b"\0")
    require(fields[-1] == b"", "Non-NUL-terminated name/status output")
    values = fields[:-1]
    require(len(values) % 2 == 0, "Malformed name/status output")
    files = []
    for index in range(0, len(values), 2):
        status = values[index].decode()
        path = values[index + 1].decode()
        require(status in {"A", "M", "D"} and path, "Unsupported source delta row")
        numstat = run(
            repository,
            "diff",
            "--numstat",
            "--no-renames",
            base + ".." + target,
            "--",
            path,
        ).decode().splitlines()
        require(len(numstat) == 1, "Missing/ambiguous numstat for " + path)
        added, removed, reported = numstat[0].split("\t", 2)
        require(
            reported == path and added.isdigit() and removed.isdigit(),
            "Binary or mismatched source delta: " + path,
        )
        files.append(
            {"path": path, "status": status, "added": int(added), "removed": int(removed)}
        )
    files.sort(key=lambda row: row["path"])
    counts = {
        "files": len(files),
        "addedFiles": sum(row["status"] == "A" for row in files),
        "modifiedFiles": sum(row["status"] == "M" for row in files),
        "deletedFiles": sum(row["status"] == "D" for row in files),
        "linesAdded": sum(row["added"] for row in files),
        "linesRemoved": sum(row["removed"] for row in files),
    }
    return files, counts


def main(project: Path) -> None:
    project = project.resolve(strict=True)
    require(project == REPOSITORIES[-1][1], "Inventory is bound to the isolated M07 checkout")
    destination = project / "Docs/AssemblyShadow/M07/M07-source-inventory.json"
    require(not destination.exists() and not destination.is_symlink(), "Inventory output already exists")
    repositories = []
    for name, path, base, target in REPOSITORIES:
        require(path.resolve(strict=True) == path and path.is_dir(), "Missing repository: " + str(path))
        files, counts = delta(path, base, target)
        repositories.append(
            {
                "name": name,
                "path": str(path),
                "base": commit(path, base),
                "target": commit(path, target),
                "files": files,
                "counts": counts,
            }
        )
    pin_files, pin_counts = delta(project, REPOSITORIES[-1][3], DEMO_PIN_REVISION)
    require(
        len(pin_files) == 1
        and pin_files[0]["path"] == "ProjectSettings/AssemblyShadowSourcePins.json"
        and pin_files[0]["status"] == "M",
        "Demo pin commit changed more than source identity metadata",
    )
    value = {
        "schemaVersion": 1,
        "milestone": "M07",
        "scope": "Immutable M07 executable pairing plus separately identified demo source-pin metadata; evidence and closeout commits are not executable inputs",
        "runtimeAcceptance": False,
        "repositories": repositories,
        "demoPinMetadata": {
            "base": REPOSITORIES[-1][3],
            "target": commit(project, DEMO_PIN_REVISION),
            "scope": "Source identity metadata only; all M07 Players and fixtures use the preceding immutable executable source revision",
            "files": pin_files,
            "counts": pin_counts,
        },
    }
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                "success": True,
                "output": str(destination),
                "repositories": {row["name"]: row["counts"] for row in repositories},
                "demoPinMetadata": pin_counts,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    arguments = parser.parse_args()
    main(arguments.project_root)
