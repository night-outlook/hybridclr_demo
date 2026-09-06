#!/usr/bin/env python3
"""M06 Gate B: clean detached-commit tests, strict replay and archive audit."""

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
    "?? .agents/.DS_Store",
    "?? .codex/.DS_Store",
    "?? Assets/Editor.meta",
    "?? Documents/HybridCLR_AssemblyShadow_Design_and_Plans/.DS_Store",
}
PAIRED_HEADS = {
    Path("/Users/ah/GitHub/hybridclr/hybridclr"): "a19db144751f4f016769b90e61a80b8c27578678",
    Path("/Users/ah/GitHub/hybridclr/il2cpp_plus"): "5b12ee96e574999d0eb82a6200d95a5b63c7fcfc",
    Path("/Users/ah/GitHub/hybridclr/hybridclr_unity"): "8d2e811fb37f4427ea15321369c883a61975a57d",
}
DEMO_EXECUTABLE = "e1ab1ca512dfd12642c333094d884808ff757fc9"
POST_EXECUTION_VERIFIER_FILES = {
    "Tools/AssemblyShadow/m06_results.py",
    "Tools/AssemblyShadow/tests/test_m06_results.py",
}


def require(value: object, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "Missing/nonregular Gate B input: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(type(value) is dict, "Expected JSON object: " + str(path))
    return value


def command_output(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(command, cwd=cwd, text=True, env={**os.environ, "LC_ALL": "C", **(env or {})})


def optional_process(pid: int, cwd: Path) -> str:
    result = subprocess.run(["ps", "-p", str(pid), "-o", "pid=,lstart=,command="], cwd=cwd,
                            text=True, capture_output=True, env={**os.environ, "LC_ALL": "C"})
    require(result.returncode in (0, 1), "Unable to inspect process identity: " + result.stderr.strip())
    return " ".join(result.stdout.split())


def git(root: Path, *arguments: str) -> str:
    return command_output(["git", *arguments], root)


def status(root: Path) -> set[str]:
    return set(git(root, "status", "--short").splitlines())


def run(command: list[str], cwd: Path, log: Path, timeout: int, env: dict[str, str] | None = None) -> dict:
    started = dt.datetime.now(dt.timezone.utc)
    with log.open("xb") as stream:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env={**os.environ, "LC_ALL": "C", **(env or {})},
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


def validate_git_tree(review: Path, evidence: Path, evidence_commit: str) -> dict:
    require(git(review, "rev-parse", "HEAD").strip() == evidence_commit, "Detached worktree is not the evidence commit")
    require(not status(review), "Detached worktree is dirty")
    require(git(review, "rev-parse", "--abbrev-ref", "HEAD").strip() == "HEAD", "Review worktree is not detached")
    files = sorted(path for path in evidence.rglob("*") if path.is_file())
    require(files, "Detached evidence tree is empty")
    for path in files:
        relative = path.relative_to(review).as_posix()
        committed = git(review, "rev-parse", evidence_commit + ":" + relative).strip()
        actual = git(review, "hash-object", relative).strip()
        require(committed == actual, "Detached evidence bytes differ from Git: " + relative)
    return {"commit": evidence_commit, "evidenceFiles": len(files), "detached": True, "clean": True}


def verify_retention(review_evidence: Path, index: dict) -> dict:
    archive_members = 0
    copied = 0
    original_hashes = set()
    for summary in index["archives"]:
        archive = review_evidence / summary["name"]
        archive_index = review_evidence / Path(summary["indexPath"]).name
        require(sha256(archive) == summary["sha256"] and sha256(archive_index) == summary["indexSha256"], "Detached archive/index hash differs")
        details = read_json(archive_index)
        expected = {row["name"]: row for row in details["files"]}
        require(len(expected) == details["fileCount"] == summary["fileCount"], "Detached archive count differs")
        seen = set()
        with tarfile.open(archive, "r:gz") as stream:
            for member in stream:
                require(member.isfile() and member.name in expected and member.name not in seen, "Unexpected detached archive member")
                row = expected[member.name]
                require(member.size == row["size"] and member.mtime == member.uid == member.gid == 0, "Detached archive metadata differs")
                extracted = stream.extractfile(member)
                require(extracted is not None, "Unreadable detached archive member")
                value = hashlib.sha256()
                for block in iter(lambda: extracted.read(1024 * 1024), b""):
                    value.update(block)
                require(value.hexdigest() == row["sha256"], "Detached archive member hash differs")
                original = Path(row["originalPath"])
                require(sha256(original) == row["sha256"], "Immutable original changed")
                original_hashes.add((str(original), row["sha256"]))
                seen.add(member.name)
        require(seen == set(expected), "Detached archive incomplete")
        archive_members += len(seen)
    names = set()
    for row in index["copiedArtifacts"]:
        require(row["name"] not in names, "Duplicate detached copy name")
        names.add(row["name"])
        copy = review_evidence / row["name"]
        original = Path(row["originalPath"])
        require(copy.stat().st_size == original.stat().st_size == row["size"], "Detached copy size differs")
        require(sha256(copy) == sha256(original) == row["sha256"], "Detached copy/original hash differs")
        original_hashes.add((str(original), row["sha256"]))
        copied += 1
    return {
        "archives": len(index["archives"]),
        "archiveMembers": archive_members,
        "copiedArtifacts": copied,
        "uniqueOriginalHashes": len(original_hashes),
    }


def named_copy(index: dict, name: str) -> dict:
    rows = [row for row in index["copiedArtifacts"] if row["name"] == name]
    require(len(rows) == 1, "Missing/ambiguous retained artifact: " + name)
    return rows[0]


def verify_source_inventory(review: Path) -> dict:
    inventory = read_json(review / "Docs/AssemblyShadow/M06/M06-source-inventory.json")
    require(inventory.get("milestone") == "M06" and inventory.get("runtimeAcceptance") is False, "Wrong detached source inventory")
    for row in inventory["repositories"]:
        repository = Path(row["path"])
        require(git(repository, "rev-parse", row["base"]).strip() == row["base"], "Missing source base")
        require(git(repository, "rev-parse", row["target"]).strip() == row["target"], "Missing source target")
        actual = git(repository, "diff", "--name-status", "--no-renames", row["base"] + ".." + row["target"]).splitlines()
        expected = [item["status"] + "\t" + item["path"] for item in row["files"]]
        require(actual == expected and len(expected) == row["counts"]["files"], "Detached source inventory differs: " + row["name"])
    demo_delta = git(review, "diff", "--name-only", DEMO_EXECUTABLE + "..HEAD").splitlines()
    require(POST_EXECUTION_VERIFIER_FILES <= set(demo_delta) and all(
        path == "ProjectSettings/AssemblyShadowSourcePins.json" or
        path.startswith("Docs/AssemblyShadow/M06/") or path in POST_EXECUTION_VERIFIER_FILES
        for path in demo_delta
    ), "Detached evidence commit contains unapproved post-execution demo changes")
    return {"repositories": len(inventory["repositories"]),
            "files": sum(row["counts"]["files"] for row in inventory["repositories"]),
            "postExecutionVerifierFiles": sorted(POST_EXECUTION_VERIFIER_FILES)}


def no_shadow_unity(live: Path) -> bool:
    for line in command_output(["ps", "ax", "-o", "pid=", "-o", "command="], live).splitlines():
        pieces = line.strip().split(None, 1)
        if len(pieces) == 2 and pieces[1].startswith("/Applications/Unity/") and "-projectPath " + str(live) in pieces[1]:
            return False
    return True


def main(review: Path, live: Path, output_root: Path, evidence_commit: str) -> None:
    review = review.resolve(strict=True)
    live = live.resolve(strict=True)
    require(live == Path("/Users/ah/GitHub/hybridclr/hybridclr_demo_shadow"), "Wrong live project")
    require(review != live and review.parent == live.parent, "Review must use a separate sibling worktree")
    require(re.fullmatch(r"[0-9a-f]{40}", evidence_commit) is not None, "Full evidence commit required")
    require(output_root.is_absolute() and output_root.resolve() == output_root and not output_root.exists(), "New canonical output root required")
    require(output_root.is_relative_to(live / "_temp/AssemblyShadow"), "Gate B output must remain task-local")
    require(no_shadow_unity(live), "Shadow-project Unity is still running")
    output_root.mkdir()

    evidence = review / "Docs/AssemblyShadow/M06/Evidence"
    git_tree = validate_git_tree(review, evidence, evidence_commit)
    index_path = evidence / "artifact-index-v8.json"
    index = read_json(index_path)
    require(index.get("milestone") == "M06" and index.get("allCopiedBytesMatch") is True, "Detached evidence index is not sealed")
    retention = verify_retention(evidence, index)
    source = verify_source_inventory(review)

    closeout = read_json(Path(named_copy(index, "verification/closeout-validation-v8.json")["originalPath"]))
    require(closeout.get("result") == "Passed", "Recorded closeout suite failed")
    closeout_python = Path(closeout["python"]["logPath"]).read_text(encoding="utf-8", errors="replace")
    closeout_match = re.search(r"Ran (\d+) tests? in", closeout_python)
    require(closeout_match is not None and re.search(r"(?m)^OK$", closeout_python) and "skipped=" not in closeout_python, "Recorded Python suite is not an unskipped pass")
    editor = closeout["editor"]
    require(editor["result"] == "Passed" and int(editor["total"]) == int(editor["passed"]) and all(int(editor[key]) == 0 for key in ("failed", "skipped", "inconclusive")), "Recorded Editor suite is not a complete pass")
    for row in closeout["nativeReceipts"]:
        require(sha256(Path(row["path"])) == row["sha256"] and read_json(Path(row["path"])).get("success") is True, "Recorded native suite failed/changed")

    compiler_root = live / "_temp/AssemblyShadow/M05RawAdmissionCompiler-955e889bd4c1442eaf694f53ff6a0ff3/Assemblies"
    require(len(list(compiler_root.glob("*.dll"))) == 36, "Detached Python gate lacks the preserved real compiler")
    python = run(
        [
            "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "Tools/AssemblyShadow/tests",
            "-q",
        ],
        review,
        output_root / "python-tests.log",
        3600,
        {
            "M05_REAL_COMPILER_ROOT": str(compiler_root),
            "M05_RAW_CONFIGURATION": str(review / "ProjectSettings/AssemblyShadowRawTypeAdmissions.json"),
        },
    )
    python_text = Path(python["logPath"]).read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Ran (\d+) tests? in", python_text)
    require(match is not None and re.search(r"(?m)^OK$", python_text) and "skipped=" not in python_text, "Detached full Python suite was not an unskipped pass")
    python["testCount"] = int(match.group(1))

    continuation = read_json(Path(named_copy(index, "verification/release-continuation-v8.json")["originalPath"]))
    development_fixture = Path(named_copy(index, "fixtures/development-fixtures-v8.json")["originalPath"])
    development_on = Path(named_copy(index, "players/development-native-on-build-v8.json")["originalPath"])
    development_off = Path(named_copy(index, "players/development-native-off-build-v8.json")["originalPath"])
    release_player = Path(named_copy(index, "players/release-native-on-build-v8.json")["originalPath"])
    strict_output = output_root / "strict-replay.json"
    strict = run(
        [
            "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
            str(review / "Tools/AssemblyShadow/verify-m06-results.py"),
            "--fixture-manifest",
            str(development_fixture),
            "--on-build",
            str(development_on),
            "--off-build",
            str(development_off),
            "--release-fixture-manifest",
            continuation["releaseFixtureManifest"],
            "--release-build",
            str(release_player),
            "--results",
            str(Path(continuation["resultRoot"]) / "Results"),
            "--m01-baseline-root",
            str(live / "BaselineArtifacts/StandaloneOSX/M01-Baseline-v1"),
            "--output",
            str(strict_output),
        ],
        review,
        output_root / "strict-replay.log",
        4 * 60 * 60,
    )
    strict_value = read_json(strict_output)
    require(strict_value.get("result") == "Passed" and strict_value.get("caseCount") == 28, "Detached strict replay failed")

    installed = run(
        [
            "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3",
            str(review / "Tools/AssemblyShadow/verify-installed-runtime.py"),
            "--project",
            str(live),
            "--skip-demo-source",
            "--expect-shadow",
            "on",
            "--json",
        ],
        review,
        output_root / "installed-source-verification.log",
        1200,
    )

    require(not status(review), "Detached worktree changed during Gate B")
    require(status(live) == EXPECTED_DEMO_DIRTY, "Live demo status changed")
    for repository, revision in PAIRED_HEADS.items():
        require(git(repository, "rev-parse", "HEAD").strip() == revision and not status(repository), "Paired repository changed")
    original = Path("/Users/ah/GitHub/hybridclr/hybridclr_demo")
    require(status(original) == EXPECTED_ORIGINAL_DIRTY, "Original checkout status changed")
    original_editor = optional_process(13313, live)
    require(not original_editor or
            (original_editor.startswith("13313 Thu Aug 27 01:46:54 2026 ") and "/Contents/MacOS/Unity" in original_editor),
            "Original Editor identity changed or was replaced")

    receipt = {
        "schemaVersion": 1,
        "milestone": "M06",
        "gate": "B-detached-commit-tests-strict-and-retention",
        "result": "PASS",
        "reviewMode": "independent-deterministic-clean-detached-worktree-process",
        "checkedUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "evidenceCommit": evidence_commit,
        "reviewRoot": str(review),
        "liveArtifactRoot": str(live),
        "gitTree": git_tree,
        "artifactIndexPath": str(index_path),
        "artifactIndexSha256": sha256(index_path),
        "retention": retention,
        "sourceInventory": source,
        "recordedSuites": {
            "pythonTests": int(closeout_match.group(1)),
            "editorTests": int(editor["total"]),
            "nativeSuites": len(closeout["nativeReceipts"]),
        },
        "python": python,
        "strictReplay": {**strict, "receiptPath": str(strict_output), "receiptSha256": sha256(strict_output)},
        "installedSourceVerification": installed,
        "reviewStatus": sorted(status(review)),
        "liveStatus": sorted(status(live)),
        "originalStatus": sorted(status(original)),
        "originalEditor": original_editor,
        "originalEditorState": "PresentUntouched" if original_editor else "AbsentAtGate",
        "limitation": "Independent deterministic detached-worktree process gate, not an independent human or LLM review. It executes the full Python and strict runtime verifiers; Unity/native suites remain byte-bound recorded inputs checked through the retained closeout receipt and archives.",
    }
    receipt_path = output_root / "gate-b.json"
    write_json_new(receipt_path, receipt)
    print(json.dumps({"result": "PASS", "receipt": str(receipt_path), "sha256": sha256(receipt_path)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-root", type=Path, required=True)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    arguments = parser.parse_args()
    main(arguments.review_root, arguments.live_project, arguments.output_root, arguments.evidence_commit)
