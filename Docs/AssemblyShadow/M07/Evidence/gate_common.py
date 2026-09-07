"""Shared fail-closed checks for the two M07 evidence-commit gates."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path


DEMO_EXECUTABLE = "3aab779a3304dd9785ab14fb5fcdc73a107066f7"
RUNTIME = "a19db144751f4f016769b90e61a80b8c27578678"
NATIVE = "666f5f4bfa3aa408e6ba4c3552fc4758dcc6bcc8"
PACKAGE = "2180b99daf39095cd76301da2bdf34ac945ee8b4"
LIVE = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow_m07")
COMPILER_ROOT = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow/_temp/AssemblyShadow/M05RawAdmissionCompiler-955e889bd4c1442eaf694f53ff6a0ff3/Assemblies")
WORKFLOW_ROOT = LIVE / "_temp/AssemblyShadow/M02Validation-00d060a2714443d2ba21203d5f1e9c8e"
RESULT_ROOT = LIVE / "_temp/AssemblyShadow/M07Results-v6-20260906T2207"
ON_BUILD = LIVE / "_temp/AssemblyShadow/M07PlayerInputs-30c933f9043545cc887466494ecef5d4/m07-player-build.json"
OFF_BUILD = LIVE / "_temp/AssemblyShadow/M07PlayerInputs-b90e7402282a44108f738b5a3f718e74/m07-player-build.json"


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular gate input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def write_json_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def command_output(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(
        command, cwd=cwd, text=True, env={**os.environ, "LC_ALL": "C", **(env or {})}
    )


def git(root: Path, *arguments: str) -> str:
    return command_output(["git", *arguments], root).strip()


def run(command: list[str], cwd: Path, log: Path, timeout: int, env: dict[str, str] | None = None) -> dict:
    started = dt.datetime.now(dt.timezone.utc)
    with log.open("xb") as stream:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env={**os.environ, "LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1", **(env or {})},
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    require(completed.returncode == 0, f"Command failed with exit {completed.returncode}: {command!r}; log={log}")
    return {
        "command": command,
        "startedUtc": started.isoformat(),
        "completedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "exitCode": completed.returncode,
        "logPath": str(log),
        "logSha256": sha256(log),
    }


def verify_git_tree(project: Path, evidence_commit: str, detached: bool) -> dict:
    require(re.fullmatch(r"[0-9a-f]{40}", evidence_commit) is not None, "Full evidence commit required")
    require(git(project, "rev-parse", "HEAD") == evidence_commit, "Checkout is not the evidence commit")
    require(not git(project, "status", "--short"), "Evidence checkout is dirty")
    branch = git(project, "rev-parse", "--abbrev-ref", "HEAD")
    require((branch == "HEAD") is detached, "Detached/current checkout mode differs")
    evidence = project / "Docs/AssemblyShadow/M07/Evidence"
    files = sorted(path for path in evidence.rglob("*") if path.is_file())
    require(files, "Committed evidence tree is empty")
    for path in files:
        relative = path.relative_to(project).as_posix()
        require(git(project, "rev-parse", evidence_commit + ":" + relative) == git(project, "hash-object", relative), "Evidence bytes differ from Git: " + relative)
    return {"commit": evidence_commit, "files": len(files), "detached": detached, "clean": True}


def verify_source_inventory(project: Path, evidence_commit: str) -> dict:
    inventory = read_json(project / "Docs/AssemblyShadow/M07/M07-source-inventory.json")
    require(inventory.get("milestone") == "M07" and inventory.get("runtimeAcceptance") is False, "Wrong source inventory")
    total = 0
    demo_root = None
    for row in inventory["repositories"]:
        repository = Path(row["path"])
        require(git(repository, "rev-parse", row["base"]) == row["base"], "Missing inventory base")
        require(git(repository, "rev-parse", row["target"]) == row["target"], "Missing inventory target")
        actual = git(repository, "diff", "--name-status", "--no-renames", row["base"] + ".." + row["target"]).splitlines()
        expected = [item["status"] + "\t" + item["path"] for item in row["files"]]
        require(actual == expected and len(expected) == row["counts"]["files"], "Source inventory differs: " + row["name"])
        total += len(expected)
        if row["name"] == "demo":
            demo_root = repository
        else:
            require(git(repository, "rev-parse", "HEAD") == row["target"] and not git(repository, "status", "--short"), "Paired repository drift: " + row["name"])
    require(demo_root == LIVE and git(LIVE, "rev-parse", "HEAD") == evidence_commit and not git(LIVE, "status", "--short"), "Live demo differs from evidence commit")
    delta = git(LIVE, "diff", "--name-only", DEMO_EXECUTABLE + ".." + evidence_commit).splitlines()
    require(delta and all(path == "ProjectSettings/AssemblyShadowSourcePins.json" or path.startswith("Docs/AssemblyShadow/M07/") for path in delta), "Post-executable commit contains build-input changes")
    return {"repositories": len(inventory["repositories"]), "files": total, "postExecutableMetadataFiles": len(delta)}


def verify_retention(evidence: Path) -> tuple[dict, dict]:
    index_path = evidence / "artifact-index-v6.json"
    index = read_json(index_path)
    require(index.get("milestone") == "M07" and index.get("allCopiedBytesMatch") is True, "Evidence index is not sealed")
    archive_members = 0
    for summary in index["archives"]:
        archive_path = evidence / summary["name"]
        archive_index_path = evidence / Path(summary["indexPath"]).name
        require(sha256(archive_path) == summary["sha256"] and archive_path.stat().st_size == summary["size"], "Archive hash/size differs")
        require(sha256(archive_index_path) == summary["indexSha256"], "Archive index hash differs")
        details = read_json(archive_index_path)
        expected = {row["name"]: row for row in details["files"]}
        require(len(expected) == details["fileCount"] == summary["fileCount"], "Archive member count differs")
        seen = set()
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive:
                require(member.isfile() and member.name in expected and member.name not in seen, "Unexpected archive member")
                row = expected[member.name]
                require(member.size == row["size"] and member.mtime == member.uid == member.gid == 0, "Archive metadata differs")
                extracted = archive.extractfile(member)
                require(extracted is not None, "Unreadable archive member")
                digest = hashlib.sha256()
                for block in iter(lambda: extracted.read(1024 * 1024), b""):
                    digest.update(block)
                require(digest.hexdigest() == row["sha256"], "Archive payload differs: " + member.name)
                require(sha256(Path(row["originalPath"])) == row["sha256"], "Original archive input changed")
                seen.add(member.name)
        require(seen == set(expected), "Archive is incomplete")
        archive_members += len(seen)
    names = set()
    for row in index["copiedArtifacts"]:
        require(row["name"] not in names, "Duplicate copied artifact")
        names.add(row["name"])
        copied = evidence / row["name"]
        original = Path(row["originalPath"])
        require(copied.stat().st_size == original.stat().st_size == row["size"], "Copied artifact size differs")
        require(sha256(copied) == sha256(original) == row["sha256"], "Copied artifact hash differs")
    return index, {"archives": len(index["archives"]), "archiveMembers": archive_members, "copiedArtifacts": len(names)}


def validate_recorded(evidence: Path) -> dict:
    closeout = read_json(evidence / "verification/m07-closeout-v6.json")
    strict = read_json(evidence / "verification/m07-strict-gate-3b-v6.json")
    native = read_json(evidence / "verification/native-tests-v6.json")
    installed = read_json(evidence / "verification/installed-source-v6.json")
    require(closeout.get("result") == "Passed" and closeout.get("baselineBuildId") == "M07-Baseline-v6", "Recorded closeout failed")
    require(strict.get("resultPassed") is True and strict.get("diagnosticOnly") is False and len(strict.get("modes", [])) == 14, "Recorded strict gate failed")
    require(native.get("success") is True and native.get("checks") == 824 and native.get("syntaxChecks") == 20, "Recorded native suite failed")
    require(installed.get("demoSourceVerified") is True and installed.get("installedFiles") == 942 and installed.get("configuredShadowMode") == "on", "Recorded installed-source gate failed")
    python_text = (evidence / "verification/python-tests-v6.log").read_text(encoding="utf-8", errors="replace")
    require(re.search(r"Ran 356 tests? in", python_text) and re.search(r"(?m)^OK$", python_text) and "skipped=" not in python_text, "Recorded Python suite failed/skipped")
    return {"playerCases": 14, "pythonTests": 356, "editorTests": 912, "nativeChecks": 824, "nativeSyntaxChecks": 20}


def run_python_and_strict(source_root: Path, output_root: Path) -> tuple[dict, dict]:
    require(COMPILER_ROOT.is_dir() and len(list(COMPILER_ROOT.glob("*.dll"))) == 36, "Preserved M05 compiler boundary is missing")
    python = run(
        ["python3", "-m", "unittest", "discover", "-s", "Tools/AssemblyShadow/tests", "-q"],
        source_root,
        output_root / "python-tests.log",
        3600,
        {"M05_REAL_COMPILER_ROOT": str(COMPILER_ROOT), "M05_RAW_CONFIGURATION": str(source_root / "ProjectSettings/AssemblyShadowRawTypeAdmissions.json")},
    )
    python_text = Path(python["logPath"]).read_text(encoding="utf-8", errors="replace")
    require(re.search(r"Ran 356 tests? in", python_text) and re.search(r"(?m)^OK$", python_text) and "skipped=" not in python_text, "Fresh Python suite failed/skipped")
    python["testCount"] = 356
    strict_output = output_root / "m07-strict.json"
    strict = run(
        [
            "python3",
            str(source_root / "Tools/AssemblyShadow/verify-m07-results.py"),
            "--fixture-manifest",
            str(WORKFLOW_ROOT / "m07-fixtures.json"),
            "--result-dir",
            str(RESULT_ROOT / "Results"),
            "--on-build",
            str(ON_BUILD),
            "--off-build",
            str(OFF_BUILD),
            "--replay-receipt",
            str(WORKFLOW_ROOT / "m07-editor-replay.json"),
            "--output",
            str(strict_output),
        ],
        source_root,
        output_root / "m07-strict.log",
        3600,
    )
    value = read_json(strict_output)
    require(value.get("resultPassed") is True and value.get("diagnosticOnly") is False and value.get("gate") == "Gate 3B" and len(value.get("modes", [])) == 14, "Fresh strict Gate 3B failed")
    strict.update(receiptPath=str(strict_output), receiptSha256=sha256(strict_output), caseCount=14)
    return python, strict


def run_installed(source_root: Path, output_root: Path) -> dict:
    installed = run(
        ["python3", str(source_root / "Tools/AssemblyShadow/verify-installed-runtime.py"), "--project", str(LIVE), "--expect-shadow", "on", "--json"],
        source_root,
        output_root / "installed-source.log",
        1200,
    )
    value = read_json(Path(installed["logPath"]))
    require(value.get("demoSourceVerified") is True and value.get("installedFiles") == 942 and value.get("configuredShadowMode") == "on", "Fresh installed-source verification failed")
    installed["summary"] = value
    return installed
