#!/usr/bin/env python3
"""Read-only R03 diagnostics host batch. Does not run Unity or Player."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BRANCH = "codex/assembly-shadow-r01b-h1"
NAMES = ("hybridclr_demo", "hybridclr", "hybridclr_unity", "il2cpp_plus")
PINS = (None, "4b2774b066cfc6afd77a8c8aded6bda7ea574f55",
        "948c0e3b4f8891481301770115e8ba4945eea6de", None)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(argv: list[str], cwd: Path | None = None, timeout: int = 1800):
    start = time.time()
    p = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout, check=False)
    receipt = {"argv": argv, "cwd": str(cwd) if cwd else None, "startedUnix": start,
               "finishedUnix": time.time(), "exit": p.returncode,
               "stdoutSha256": sha(p.stdout), "stderrSha256": sha(p.stderr)}
    return p, receipt


def git(repo: Path, *args: str) -> str:
    p, _ = command(["git", "-C", str(repo), *args], timeout=45)
    if p.returncode:
        raise ValueError(f"git failed for {repo} / {args}: {p.stderr[:300]!r}")
    return p.stdout.decode("utf-8").strip()


def verify_repo(workspace: Path, name: str, expected: str) -> dict:
    path = workspace / name
    if not path.is_dir() or path.is_symlink() or path.resolve() != path:
        raise ValueError("Invalid repo path: " + str(path))
    identity = "night-outlook/" + name
    origin = git(path, "remote", "get-url", "origin")
    valid = {f"https://github.com/{identity}", f"https://github.com/{identity}.git",
             f"git@github.com:{identity}", f"git@github.com:{identity}.git",
             f"ssh://git@github.com/{identity}.git"}
    if origin not in valid:
        raise ValueError("Unexpected canonical GitHub remote for " + identity)
    branch = git(path, "branch", "--show-current")
    head = git(path, "rev-parse", "HEAD")
    dirty = git(path, "status", "--porcelain")
    remote_line = git(path, "ls-remote", "origin", "refs/heads/" + BRANCH).split()
    remote = remote_line[0] if len(remote_line) == 2 and remote_line[1] == "refs/heads/" + BRANCH else None
    if branch != BRANCH or head != expected or remote != expected or dirty:
        raise ValueError(f"Checkout mismatch: {identity}, branch={branch}, HEAD={head}, "
                         f"remote={remote}, dirty={bool(dirty)}")
    return {"repository": identity, "path": str(path), "origin": origin,
            "branch": branch, "head": head, "remoteHead": remote, "clean": True}


def source_hashes(demo: Path, native: Path) -> dict:
    paths = [native / "libil2cpp/vm/AssemblyShadow.cpp",
             native / "libil2cpp/vm/AssemblyShadowExecutionSerializer.h",
             native / "libil2cpp/vm/AssemblyShadowDiagnosticWriter.h",
             native / "tools/r03/diagnostic_stream/execution_serializer_tests.cpp",
             demo / "Tools/AssemblyShadow/R03IR/bounded_v2/BoundedDiagnosticsV2.h",
             demo / "Tools/AssemblyShadow/R03IR/bounded_v2/PosixDiagnosticTransaction.h",
             demo / "Tools/AssemblyShadow/R03IR/bounded_v2/transaction_reader.py",
             demo / "Tools/AssemblyShadow/R03IR/PlayerProject/R03TerminalPlayer.cs"]
    return {str(p): {"bytes": p.stat().st_size, "sha256": sha(p.read_bytes())} for p in paths}


def run_case(name: str, argv: list[str], output: Path, timeout: int = 1800) -> dict:
    folder = output / name
    folder.mkdir(mode=0o700)
    record = {"name": name, "status": "Failed", "resultRoot": str(folder)}
    try:
        p, receipt = command(argv, timeout=timeout)
        (folder / "stdout.bin").write_bytes(p.stdout)
        (folder / "stderr.bin").write_bytes(p.stderr)
        record.update(receipt)
        record["status"] = "Passed" if p.returncode == 0 else "Failed"
    except Exception as error:
        record["exception"] = repr(error)
    (folder / "command.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def inventory(root: Path) -> list[dict]:
    result = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            result.append({"path": str(p.relative_to(root)), "kind": "Symlink",
                           "target": os.readlink(p)})
        elif p.is_file():
            data = p.read_bytes()
            result.append({"path": str(p.relative_to(root)), "size": len(data),
                           "sha256": sha(data)})
    return result


def main():
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--workspace", required=True, type=Path)
    arg.add_argument("--expected-demo", required=True)
    arg.add_argument("--expected-native", required=True)
    arg.add_argument("--output", required=True, type=Path)
    args = arg.parse_args()
    if not __debug__:
        raise ValueError("Python -O is prohibited")
    for value in (args.expected_demo, args.expected_native):
        if not re.fullmatch(r"[0-9a-f]{40}", value):
            raise ValueError("Exact source commit SHA required")
    base = args.workspace.resolve(strict=True)
    if base != args.workspace or base.is_symlink() or not base.is_dir():
        raise ValueError("Canonical workspace parent required")
    paths = [base / n for n in NAMES]
    dest = args.output
    if not dest.is_absolute() or dest.exists() or dest.is_symlink() or dest != dest.resolve(strict=False) or not dest.parent.is_dir():
        raise ValueError("Fresh canonical external output root required")
    if any(p == dest or p in dest.parents or dest in p.parents for p in paths):
        raise ValueError("Output must remain outside all four sources")
    pins = (args.expected_demo, PINS[1], PINS[2], args.expected_native)
    repositories = [verify_repo(base, n, pin) for n, pin in zip(NAMES, pins)]
    demo, native = paths[0], paths[-1]
    before = source_hashes(demo, native)
    # No evidence directory is opened before branch/source/clean/remote checks.
    dest.mkdir(mode=0o700)
    results = []
    python = sys.executable
    try:
        tests = (
            ("native-general-stream", [python, "-B", str(native / "tools/r03/diagnostic_stream/run_tests.py"),
                "--native", str(native), "--demo", str(demo),
                "--output", str(dest / "native-general-stream" / "evidence")]),
            ("native-v2-codec", [python, "-B", str(demo / "Tools/AssemblyShadow/R03IR/bounded_v2/run_tests.py"),
                "--repository", str(demo), "--output", str(dest / "native-v2-codec" / "evidence")]),
            ("native-v2-file-transaction", [python, "-B", str(demo / "Tools/AssemblyShadow/R03IR/bounded_v2/run_transaction_tests.py"),
                "--repository", str(demo), "--output", str(dest / "native-v2-file-transaction" / "evidence")]),
            ("native-v2-legacy-sink", [python, "-B", str(demo / "Tools/AssemblyShadow/R03IR/NativeDiagnostics/test_native_v2.py"),
                "--output", str(dest / "native-v2-legacy-sink" / "evidence")]),
        )
        # Independent host suites continue after a single component failure.
        for name, argv in tests:
            results.append(run_case(name, argv, dest))
        compiler = shutil.which(os.environ.get("CXX", "clang++"))
        if compiler:
            source = native / "tools/r03/diagnostic_stream/execution_serializer_tests.cpp"
            for profile in ("strict", "sanitized"):
                name = "execution-serializer-" + profile
                binary = dest / name / "test"
                flags = ["-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                         "-I" + str(native / "libil2cpp/vm")]
                flags += ["-O2"] if profile == "strict" else [
                    "-O1", "-g", "-fno-omit-frame-pointer", "-fsanitize=address,undefined"]
                receipt = run_case(name, [compiler, *flags, str(source), "-o", str(binary)], dest, timeout=120)
                results.append(receipt)
                if receipt["status"] == "Passed":
                    results.append(run_case(name + "-run", [str(binary)], dest, timeout=120))
        else:
            results.append({"name": "execution-serializer", "status": "Unavailable", "reason": "CXX missing"})
    finally:
        after = source_hashes(demo, native)
        preserved = before == after
        report = {"schemaVersion": 1, "kind": "R03PrimaryHostOnlyPreflight",
                  "result": "PassedHostOnly" if preserved and all(r["status"] == "Passed" for r in results)
                  else "FailedOrIncomplete",
                  "repositories": repositories, "platform": platform.platform(),
                  "python": sys.version, "commands": results, "sourceBefore": before,
                  "sourceAfter": after, "sourcePreserved": preserved,
                  "actualUnityOrPlayerRun": False, "officialUnitySdkCompile": False,
                  "runtimeAcceptance": False, "historicalEvidenceUpgraded": False}
        (dest / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
        (dest / "MANIFEST.json").write_text(json.dumps({"files": inventory(dest)}, indent=2) + "\n")
    print(json.dumps({"result": report["result"], "cases": [(r["name"], r["status"]) for r in results],
                      "output": str(dest)}, indent=2))
    if report["result"] != "PassedHostOnly":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
