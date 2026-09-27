"""R02 receipts and regular-file retention. No branch, source, or pin writes."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tarfile
import time
from typing import Iterable


class EvidenceError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise EvidenceError(message)


def _pairs(rows):
    result = {}
    for key, value in rows:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def loads(text: str):
    def invalid(value):
        raise EvidenceError("Non-finite JSON number: " + value)
    def floating(value):
        parsed = float(value)
        require(math.isfinite(parsed), "Non-finite JSON number: " + value)
        return parsed
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid, parse_float=floating)


def read(path: Path):
    regular(path)
    return loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    require(path.is_absolute(), "Absolute output required")
    require(not path.is_symlink(), "Linked output refused")
    for parent in path.parents:
        require(not parent.is_symlink(), "Linked output parent refused")
    path.parent.mkdir(parents=True, exist_ok=True)
    require(path.parent == path.parent.resolve(strict=True), "Canonical output parent required")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def regular(path: Path) -> Path:
    require(path.is_absolute(), "Absolute file required")
    require(path.is_file(), "Missing regular file: " + str(path))
    require(not path.is_symlink(), "File must not be a link: " + str(path))
    for parent in path.parents:
        require(not parent.is_symlink(), "Linked parent: " + str(parent))
    require(path == path.resolve(strict=True), "Canonical file required")
    return path


def sha256(path: Path) -> str:
    regular(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: Path) -> dict:
    path = regular(path)
    before = path.stat()
    value = {"path": str(path), "sha256": sha256(path), "sizeBytes": before.st_size}
    require(stable(before) == stable(path.stat()), "File changed while hashing: " + str(path))
    return value


def stable(stat) -> tuple:
    # No st_dev: remounting is not a change of file content or stable identity.
    return stat.st_ino, stat.st_mode, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def check_binding(row: dict) -> Path:
    require(isinstance(row, dict), "Expected file binding")
    path = regular(Path(row["path"]))
    require(type(row.get("sizeBytes")) is int and row["sizeBytes"] >= 0, "Invalid bound size")
    require(binding(path) == {"path": row["path"], "sha256": row["sha256"], "sizeBytes": row["sizeBytes"]}, "File binding mismatch: " + str(path))
    return path


def integer(value, label: str, minimum: int = 0, maximum: int = (1 << 64) - 1) -> int:
    require(type(value) is int and minimum <= value <= maximum, "Invalid integer: " + label)
    return value


def number(value, label: str) -> float:
    require(type(value) in (float, int) and math.isfinite(value), "Invalid finite number: " + label)
    return float(value)


def owned_group_members(group: int) -> dict:
    """Diagnostic-only census of the owned group; never store other processes.

    A missing census does not relax the separate killpg ownership/cleanup check.
    Executable names are enough; command arguments and environments are omitted.
    """
    try:
        observed = subprocess.run(["ps", "-eo", "pid=,pgid=,stat=,comm="], capture_output=True, text=True, timeout=3)
        if observed.returncode:
            return {"status": "Unavailable", "reason": "ps exited nonzero"}
        members = []
        for line in observed.stdout.splitlines():
            parts = line.strip().split(None, 3)
            if len(parts) != 4:
                continue
            try:
                pid, pgid = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            if pgid == group:
                members.append({"pid": pid, "processGroup": pgid, "state": parts[2], "executable": parts[3][:1024]})
        return {"status": "Observed", "members": members}
    except (OSError, subprocess.SubprocessError) as error:
        return {"status": "Unavailable", "reason": type(error).__name__}


def run(argv: list[str], cwd: Path, output: Path, timeout: int, env: dict | None = None) -> dict:
    """An owned process group; log files and failed/partial attempts are retained."""
    require(argv and all(isinstance(a, str) and "\0" not in a for a in argv), "Invalid argv")
    require(1 <= timeout <= 86400, "Invalid timeout")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"kind": "R02Command", "argv": argv, "cwd": str(cwd), "startedAtUnix": time.time(),
               "result": "Failed", "exitCode": None, "timedOut": False, "processGroupClean": False}
    process = None
    try:
        with (output / "stdout.log").open("xb") as stdout, (output / "stderr.log").open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=(os.name == "posix"))
            receipt["pid"] = process.pid
            try:
                receipt["exitCode"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                receipt["timedOut"] = True
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    receipt["exitCode"] = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    if os.name == "posix": os.killpg(process.pid, signal.SIGKILL)
                    else: process.kill()
                    receipt["exitCode"] = process.wait(timeout=10)
            receipt["processGroupClean"] = True
            if os.name == "posix":
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    # Even a zero-exit parent with surviving children fails.
                    receipt["processGroupClean"] = False
                    receipt["survivorsBeforeCleanup"] = owned_group_members(process.pid)
                    os.killpg(process.pid, signal.SIGKILL)
            receipt["result"] = "Passed" if receipt["exitCode"] == 0 and not receipt["timedOut"] and receipt["processGroupClean"] else "Failed"
    except (OSError, subprocess.SubprocessError) as error:
        receipt["error"] = str(error)
        if process is not None and process.poll() is None:
            if os.name == "posix": os.killpg(process.pid, signal.SIGKILL)
            else: process.kill()
            process.wait(timeout=10)
    receipt["endedAtUnix"] = time.time()
    receipt["logs"] = [binding(p) for p in (output / "stdout.log", output / "stderr.log") if p.is_file()]
    write(output / "command.json", receipt)
    return receipt


def files_under(root: Path) -> list[Path]:
    require(root.is_absolute() and root.is_dir() and not root.is_symlink(), "Canonical directory required")
    paths = []
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "Unexpected linked artifact: " + str(path))
        if path.is_file():
            paths.append(regular(path))
        else:
            require(path.is_dir(), "Unexpected non-regular artifact")
    return paths


def seal(paths: Iterable[Path], output: Path) -> dict:
    """Content-addressed regular members, with a separate non-circular index.

    Original absolute paths remain locators; no basename guessing or extraction
    of archive paths is required. The inventory records each unique locator.
    """
    output.mkdir(parents=True, exist_ok=False)
    rows = [binding(p) for p in sorted(set(paths))]
    require(rows, "Empty evidence archive")
    unique = {}
    for row in rows:
        require(not Path(row["path"]).is_relative_to(output), "Archive cannot include itself")
        row["member"] = "blobs/" + row["sha256"]
        previous = unique.setdefault(row["member"], row)
        require(previous["sizeBytes"] == row["sizeBytes"], "Digest/size conflict")
    archive_path = output / "evidence.tar.gz"
    with archive_path.open("xb") as file, tarfile.open(fileobj=file, mode="w:gz") as archive:
        for name, row in unique.items():
            path = check_binding({k: row[k] for k in ("path", "sha256", "sizeBytes")})
            before = stable(path.stat())
            info = tarfile.TarInfo(name); info.size = row["sizeBytes"]; info.mode = 0o644; info.mtime = 0
            with path.open("rb") as stream:
                archive.addfile(info, stream)
            require(before == stable(path.stat()) and sha256(path) == row["sha256"], "Input changed while sealing")
    receipt = {"kind": "R02EvidenceSeal", "result": "Passed", "files": rows,
               "uniqueMemberCount": len(unique), "archive": binding(archive_path), "runtimeAcceptance": False}
    audit_archive(receipt)
    write(output / "seal-index.json", receipt)
    return receipt


def audit_archive(receipt: dict) -> None:
    archive_path = check_binding(receipt["archive"])
    require(receipt.get("kind") == "R02EvidenceSeal", "Wrong seal kind")
    expected = {}
    locators = set()
    for row in receipt["files"]:
        require(row["path"] not in locators, "Duplicate retained locator")
        locators.add(row["path"])
        require(row["member"] == "blobs/" + row["sha256"] and len(row["sha256"]) == 64 and
                all(c in "0123456789abcdef" for c in row["sha256"]), "Invalid archive member identity")
        pair = (integer(row["sizeBytes"], "member size"), row["sha256"])
        require(row["member"] not in expected or expected[row["member"]] == pair, "Conflicting member identity")
        expected[row["member"]] = pair
    require(expected and len(expected) == receipt["uniqueMemberCount"], "Wrong archive member count")
    seen = set()
    with tarfile.open(archive_path, "r|gz") as archive:
        for member in archive:
            require(member.isfile() and member.name in expected and member.name not in seen, "Extra, linked, duplicate, or invalid archive member")
            require(member.size == expected[member.name][0], "Archive member size mismatch")
            stream = archive.extractfile(member)
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
            require(digest.hexdigest() == expected[member.name][1], "Archive member hash mismatch")
            seen.add(member.name)
    require(seen == set(expected), "Missing archive members")
