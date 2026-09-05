#!/usr/bin/env python3
"""M06 Gate A: current-checkout source, artifact and recorded-suite audit."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path


EXPECTED_DEMO_DIRTY = {
    " M Assets/AssemblyShadowDemo/Scenes/M06Bootstrap.unity",
    " M Assets/HybridCLRGenerate/AOTGenericReferences.cs",
    " M Assets/HybridCLRGenerate/link.xml",
    " M ProjectSettings/AssemblyShadowSettings.asset",
    " M ProjectSettings/ProjectSettings.asset",
}
EXPECTED_ORIGINAL_DIRTY = {
    " M Assets/Settings/Renderer2D.asset",
    "?? .DS_Store",
    "?? Assets/Editor.meta",
    "?? Documents/HybridCLR_AssemblyShadow_Design_and_Plans/.DS_Store",
}
PAIRED_HEADS = {
    Path("/Users/ah/GitHub/hybridclr/hybridclr"): "a19db144751f4f016769b90e61a80b8c27578678",
    Path("/Users/ah/GitHub/hybridclr/il2cpp_plus"): "6613a02feaf7774b14fb1b57d20a72812bde0434",
    Path("/Users/ah/GitHub/hybridclr/hybridclr_unity"): "8d2e811fb37f4427ea15321369c883a61975a57d",
}
DEMO_EXECUTABLE = "88b4f9145430f9993eb49c1e6854e377ce7ea345"


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular gate input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected object: " + str(path))
    return value


def output(command: list[str], cwd: Path) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True, env={**os.environ, "LC_ALL": "C"})


def git(root: Path, *arguments: str) -> str:
    return output(["git", *arguments], root)


def status(root: Path) -> set[str]:
    return set(git(root, "status", "--short").splitlines())


def no_shadow_unity(project: Path) -> bool:
    for line in output(["ps", "ax", "-o", "pid=", "-o", "command="], project).splitlines():
        pieces = line.strip().split(None, 1)
        if len(pieces) == 2 and pieces[1].startswith("/Applications/Unity/") and "-projectPath " + str(project) in pieces[1]:
            return False
    return True


def run(command: list[str], cwd: Path, log: Path, timeout: int) -> dict:
    started = dt.datetime.now(dt.timezone.utc)
    with log.open("xb") as stream:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env={**os.environ, "LC_ALL": "C"},
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


def write_json_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def named_copy(index: dict, name: str) -> dict:
    rows = [row for row in index["copiedArtifacts"] if row["name"] == name]
    require(len(rows) == 1, "Missing/ambiguous retained artifact: " + name)
    return rows[0]


def verify_archives(evidence: Path, index: dict) -> dict:
    total_members = 0
    total_bytes = 0
    for row in index["archives"]:
        archive_path = Path(row["path"])
        archive_index_path = Path(row["indexPath"])
        require(archive_path.parent == evidence and archive_index_path.parent == evidence, "Archive escaped evidence root")
        require(sha256(archive_path) == row["sha256"] and archive_path.stat().st_size == row["size"], "Archive hash/size changed")
        require(sha256(archive_index_path) == row["indexSha256"], "Archive index changed")
        archive_index = read_json(archive_index_path)
        require(archive_index.get("allArchivedBytesMatch") is True and archive_index.get("normalizedTarMetadata") is True, "Archive was not sealed")
        require(archive_index.get("archiveSha256") == row["sha256"] and archive_index.get("fileCount") == row["fileCount"], "Archive summary differs")
        expected = {item["name"]: item for item in archive_index["files"]}
        require(len(expected) == row["fileCount"], "Duplicate archive index members")
        seen = set()
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive:
                require(member.isfile() and member.name in expected and member.name not in seen, "Unexpected archive member")
                item = expected[member.name]
                require(member.size == item["size"] and member.mtime == 0 and member.uid == 0 and member.gid == 0, "Archive metadata drift")
                stream = archive.extractfile(member)
                require(stream is not None, "Unreadable archive member")
                digest = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
                require(digest.hexdigest() == item["sha256"], "Archive payload mismatch: " + member.name)
                seen.add(member.name)
        require(seen == set(expected), "Incomplete archive")
        for item in expected.values():
            require(sha256(Path(item["originalPath"])) == item["sha256"], "Original archive input changed")
        total_members += len(seen)
        total_bytes += archive_path.stat().st_size
    return {"archiveCount": len(index["archives"]), "memberCount": total_members, "compressedBytes": total_bytes}


def verify_copies(evidence: Path, index: dict) -> dict:
    names = set()
    total = 0
    for row in index["copiedArtifacts"]:
        require(row["name"] not in names, "Duplicate retained copy")
        names.add(row["name"])
        copy = Path(row["path"])
        original = Path(row["originalPath"])
        require(copy == evidence / row["name"] and copy.is_relative_to(evidence), "Copy escaped evidence root")
        require(copy.stat().st_size == original.stat().st_size == row["size"], "Copied size changed")
        require(sha256(copy) == sha256(original) == row["sha256"], "Copied/original bytes differ")
        total += row["size"]
    return {"copyCount": len(names), "copyBytes": total}


def verify_git_evidence(project: Path, evidence: Path, evidence_commit: str) -> dict:
    require(git(project, "rev-parse", "HEAD").strip() == evidence_commit, "Gate A must run at the evidence commit")
    paths = sorted(path for path in evidence.rglob("*") if path.is_file())
    for path in paths:
        relative = path.relative_to(project).as_posix()
        require(git(project, "ls-files", "--error-unmatch", relative).strip() == relative, "Untracked evidence file: " + relative)
        committed_blob = git(project, "rev-parse", evidence_commit + ":" + relative).strip()
        working_blob = git(project, "hash-object", relative).strip()
        require(committed_blob == working_blob, "Evidence working bytes differ from Git: " + relative)
    return {"files": len(paths), "commit": evidence_commit}


def verify_source_inventory(project: Path) -> dict:
    inventory = read_json(project / "Docs/AssemblyShadow/M06/M06-source-inventory.json")
    require(inventory.get("milestone") == "M06" and inventory.get("runtimeAcceptance") is False, "Wrong source inventory")
    expected = {str(path): revision for path, revision in PAIRED_HEADS.items()}
    expected[str(project)] = DEMO_EXECUTABLE
    for row in inventory["repositories"]:
        require(row["target"] == expected[row["path"]], "Source inventory target mismatch")
        repo = Path(row["path"])
        require(git(repo, "rev-parse", row["target"]).strip() == row["target"], "Missing inventory target")
        actual = git(repo, "diff", "--name-status", "--no-renames", row["base"] + ".." + row["target"]).splitlines()
        recorded = [item["status"] + "\t" + item["path"] for item in row["files"]]
        require(actual == recorded, "Source inventory path/status drift: " + row["name"])
        require(row["counts"]["files"] == len(recorded), "Source inventory count drift")
    demo_delta = git(project, "diff", "--name-only", DEMO_EXECUTABLE + "..HEAD").splitlines()
    require(
        all(path == "ProjectSettings/AssemblyShadowSourcePins.json" or path.startswith("Docs/AssemblyShadow/M06/") for path in demo_delta),
        "Executable demo input changed after frozen source",
    )
    return {"repositories": len(inventory["repositories"]), "postExecutableMetadataFiles": len(demo_delta)}


def main(project: Path, output_root: Path, evidence_commit: str) -> None:
    project = project.resolve(strict=True)
    require(project == Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow"), "Wrong isolated project")
    require(re.fullmatch(r"[0-9a-f]{40}", evidence_commit) is not None, "Full evidence commit required")
    require(output_root.is_absolute() and output_root.resolve() == output_root and not output_root.exists(), "New canonical output root required")
    require(output_root.is_relative_to(project / "_temp/AssemblyShadow"), "Gate output must remain task-local")
    require(no_shadow_unity(project), "Shadow-project Unity is still running")
    output_root.mkdir()
    evidence = project / "Docs/AssemblyShadow/M06/Evidence"
    index_path = evidence / "artifact-index-v7.json"
    index = read_json(index_path)
    require(index.get("milestone") == "M06" and index.get("allCopiedBytesMatch") is True and index.get("runtimeAcceptance") is False, "Wrong/unsealed evidence index")
    archives = verify_archives(evidence, index)
    copies = verify_copies(evidence, index)
    git_evidence = verify_git_evidence(project, evidence, evidence_commit)
    source = verify_source_inventory(project)

    closeout_row = named_copy(index, "verification/closeout-validation-v7.json")
    closeout = read_json(Path(closeout_row["originalPath"]))
    require(closeout.get("result") == "Passed", "Recorded closeout suite failed")
    python_log = Path(closeout["python"]["logPath"])
    python_text = python_log.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Ran (\d+) tests? in", python_text)
    require(match is not None and int(match.group(1)) == closeout["python"]["testCount"] and re.search(r"(?m)^OK$", python_text) and "skipped=" not in python_text, "Recorded Python suite is not an unskipped pass")
    editor = closeout["editor"]
    require(editor["result"] == "Passed" and int(editor["total"]) == int(editor["passed"]) and all(int(editor[key]) == 0 for key in ("failed", "skipped", "inconclusive")), "Recorded Editor suite is not a full pass")
    for row in closeout["nativeReceipts"]:
        require(read_json(Path(row["path"])).get("success") is True and sha256(Path(row["path"])) == row["sha256"], "Recorded native suite failed/changed")

    continuation = read_json(Path(named_copy(index, "verification/release-continuation-v7.json")["originalPath"]))
    release_fixture = Path(continuation["releaseFixtureManifest"])
    strict_output = output_root / "strict-replay.json"
    strict = run(
        [
            "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
            str(project / "Tools/AssemblyShadow/verify-m06-results.py"),
            "--fixture-manifest",
            str(project / "_temp/AssemblyShadow/M06Fixtures-88145bf85f4a4de887232554027d108a/m06-fixtures.json"),
            "--on-build",
            str(project / "_temp/AssemblyShadow/M06PlayerInputs-d0443d0087b846a18b4cbf525887e6c9/m06-player-build.json"),
            "--off-build",
            str(project / "_temp/AssemblyShadow/M06PlayerInputs-b0ac61d48df24880a94434c49f71c985/m06-player-build.json"),
            "--release-fixture-manifest",
            str(release_fixture),
            "--release-build",
            str(project / "_temp/AssemblyShadow/M06PlayerInputs-4c2ea626ceba4ee2866a2d0bb9748ecf/m06-player-build.json"),
            "--results",
            str(project / "_temp/AssemblyShadow/M06Results-final-20260904-2006/Results"),
            "--m01-baseline-root",
            str(project / "BaselineArtifacts/StandaloneOSX/M01-Baseline-v1"),
            "--output",
            str(strict_output),
        ],
        project,
        output_root / "strict-replay.log",
        4 * 60 * 60,
    )
    strict_value = read_json(strict_output)
    require(strict_value.get("result") == "Passed" and strict_value.get("caseCount") == 28, "Gate A strict replay failed")

    install = run(
        [
            "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
            str(project / "Tools/AssemblyShadow/verify-installed-runtime.py"),
            "verify",
            "--project",
            str(project),
            "--verify-demo-source",
            "--expect-shadow",
            "on",
            "--json",
        ],
        project,
        output_root / "installed-source-verification.log",
        1200,
    )

    require(status(project) == EXPECTED_DEMO_DIRTY, "Demo working status changed")
    for repo, revision in PAIRED_HEADS.items():
        require(git(repo, "rev-parse", "HEAD").strip() == revision and not status(repo), "Paired repository drift: " + str(repo))
    original = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo")
    require(status(original) == EXPECTED_ORIGINAL_DIRTY, "Original checkout status changed")
    original_editor = " ".join(output(["ps", "-p", "13313", "-o", "pid=,lstart=,command="], project).split())
    require(original_editor.startswith("13313 Thu Aug 27 01:46:54 2026 ") and "/Contents/MacOS/Unity" in original_editor, "Original Editor identity changed")

    receipt = {
        "schemaVersion": 1,
        "milestone": "M06",
        "gate": "A-current-source-artifacts-and-recorded-suites",
        "result": "PASS",
        "reviewMode": "deterministic-current-checkout-process",
        "checkedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidenceCommit": evidence_commit,
        "artifactIndexPath": str(index_path),
        "artifactIndexSha256": sha256(index_path),
        "archives": archives,
        "copies": copies,
        "gitEvidence": git_evidence,
        "sourceInventory": source,
        "recordedSuites": {
            "pythonTests": int(match.group(1)),
            "editorTests": int(editor["total"]),
            "nativeSuites": len(closeout["nativeReceipts"]),
        },
        "strictReplay": {**strict, "receiptPath": str(strict_output), "receiptSha256": sha256(strict_output)},
        "installedSourceVerification": install,
        "originalStatus": sorted(status(original)),
        "originalEditor": original_editor,
        "demoStatus": sorted(status(project)),
        "limitation": "Independent deterministic process gate, not an independent human or LLM review. Recorded Unity/native suites are passively revalidated; the strict M06 verifier and installed-source verifier are rerun.",
    }
    receipt_path = output_root / "gate-a.json"
    write_json_new(receipt_path, receipt)
    print(json.dumps({"result": "PASS", "receipt": str(receipt_path), "sha256": sha256(receipt_path)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    arguments = parser.parse_args()
    main(arguments.project_root, arguments.output_root, arguments.evidence_commit)
