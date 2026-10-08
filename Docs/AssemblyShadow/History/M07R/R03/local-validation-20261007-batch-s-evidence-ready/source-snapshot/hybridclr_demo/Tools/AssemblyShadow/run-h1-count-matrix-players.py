#!/usr/bin/env python3
"""Run and independently verify every canonical H1 count Player cell."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from h1_count_matrix import required_cells


HERE = Path(__file__).resolve().parent


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical_file(value: str, label: str) -> Path:
    path = Path(value)
    require(path.is_absolute() and path == path.resolve() and path.is_file() and not path.is_symlink(),
            label + " must be an existing canonical file")
    return path


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(argv: list[str], cwd: Path, label: str) -> None:
    completed = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=False)
    if completed.returncode:
        raise RuntimeError(label + f" failed with exit code {completed.returncode}:\n" + completed.stdout)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--parameter-manifest", required=True)
    parser.add_argument("--parameter-audit", required=True)
    parser.add_argument("--nested-manifest", required=True)
    parser.add_argument("--nested-audit", required=True)
    parser.add_argument("--build-on-debug", required=True)
    parser.add_argument("--build-on-release", required=True)
    parser.add_argument("--build-off-debug", required=True)
    parser.add_argument("--build-off-release", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--resume", action="store_true",
                        help="reuse passed cell reports in an existing output root and retry only incomplete cells")
    args = parser.parse_args(argv)

    project = Path(args.project_root)
    require(project.is_absolute() and project == project.resolve() and project.is_dir() and
            not project.is_symlink(), "project root must be an existing canonical directory")
    output = Path(args.output_root)
    require(output.is_absolute() and output == output.resolve() and
            output.parent.is_dir() and output.parent == output.parent.resolve() and
            output.is_relative_to(project), "output root must be a new canonical directory inside the project")
    if args.resume:
        require(output.is_dir() and not output.is_symlink(),
                "resume output root must be an existing canonical directory")
    else:
        require(not output.exists(), "output root must be new unless --resume is used")
        output.mkdir()

    manifests = {
        "parameters": (canonical_file(args.parameter_manifest, "parameter manifest"),
                       canonical_file(args.parameter_audit, "parameter audit")),
        "nested": (canonical_file(args.nested_manifest, "nested manifest"),
                   canonical_file(args.nested_audit, "nested audit")),
    }
    builds = {
        (True, "Debug"): canonical_file(args.build_on_debug, "ON Debug build receipt"),
        (True, "Release"): canonical_file(args.build_on_release, "ON Release build receipt"),
        (False, "Debug"): canonical_file(args.build_off_debug, "OFF Debug build receipt"),
        (False, "Release"): canonical_file(args.build_off_release, "OFF Release build receipt"),
    }
    launcher = HERE / "run-h1-count-players.py"
    verifier = HERE / "verify-h1-count-results.py"
    cells = []
    for ordinal, (cell_id, cell) in enumerate(required_cells().items(), 1):
        family = cell["family"]
        path_name = cell["pathName"]
        cpp = cell["cppConfiguration"]
        flavor = "ordinary" if path_name.startswith("Ordinary") else "shadow"
        cell_output = output / (f"{ordinal:03d}-" + cell_id.replace("/", "-"))
        existing_report = cell_output / "verification.json"
        if args.resume and existing_report.is_file() and not existing_report.is_symlink():
            existing = json.loads(existing_report.read_text(encoding="utf-8"))
            requested = existing.get("requested") or {}
            require(existing.get("kind") == "H1CountResultVerification" and
                    existing.get("result") == "Passed" and requested.get("family") == family and
                    requested.get("caseId") == cell["caseId"] and requested.get("pathName") == path_name and
                    requested.get("cppConfiguration") == cpp,
                    "existing resumed report does not match " + cell_id)
            cells.append({"cellId": cell_id,
                          "report": {"path": str(existing_report), "sha256": digest(existing_report)}})
            print(f"[{ordinal:03d}/132] Reused {cell_id}", flush=True)
            continue
        if cell_output.exists():
            retry = 1
            while (output / ((f"{ordinal:03d}-" + cell_id.replace("/", "-")) +
                             f"-retry-{retry:02d}")).exists():
                retry += 1
            cell_output = output / ((f"{ordinal:03d}-" + cell_id.replace("/", "-")) +
                                    f"-retry-{retry:02d}")
        manifest, audit = manifests[family]
        build = builds[(cell["featureEnabled"], cpp)]
        run([sys.executable, str(launcher), "--project-root", str(project),
             "--build-receipt", str(build), "--fixture-manifest", str(manifest),
             "--fixture-audit", str(audit), "--family", family, "--path", flavor,
             "--case", cell["caseId"], "--output-root", str(cell_output),
             "--timeout", str(args.timeout)], project, "launcher for " + cell_id)
        report = cell_output / "verification.json"
        run([sys.executable, str(verifier), "--launch-receipt",
             str(cell_output / "h1-count-player-launch.json"), "--expected-case", cell["caseId"],
             "--expected-family", family, "--expected-path", path_name,
             "--expected-cpp", cpp, "--output", str(report)], project,
            "independent verifier for " + cell_id)
        cells.append({"cellId": cell_id, "report": {"path": str(report), "sha256": digest(report)}})
        print(f"[{ordinal:03d}/132] Passed {cell_id}", flush=True)

    index = output / "result-index.json"
    require(not index.exists(), "result index already exists; refusing to overwrite completed evidence")
    with index.open("x", encoding="utf-8") as stream:
        json.dump({"schemaVersion": 1, "kind": "H1CountResultIndex", "cells": cells},
                  stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(str(index), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
